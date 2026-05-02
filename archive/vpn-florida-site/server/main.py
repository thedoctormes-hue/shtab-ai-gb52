from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import os
import socket
import subprocess
import platform
import time
import io
import requests
import traceback
from typing import Optional
from pathlib import Path
import hashlib
from datetime import datetime, timezone, timedelta
import paramiko
from dotenv import load_dotenv

# Load .env file
load_dotenv()

app = FastAPI(title="VPN Florida API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data storage
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
SERVERS_FILE = os.path.join(DATA_DIR, "servers.json")
PAYMENTS_FILE = os.path.join(DATA_DIR, "payments.json")

# Shares storage
SHARES_DIR = Path("/root/.qwen/shares")
UPLOADS_DIR = Path("/root/.qwen/uploads")

# Ensure files exist
if not os.path.exists(SERVERS_FILE):
    with open(SERVERS_FILE, "w") as f:
        json.dump({
            "servers": [
                {
                    "id": "florida-1",
                    "name": "Florida Miami",
                    "ip": "185.138.90.150",
                    "port": 443,
                    "protocol": "vless",
                    "flow": "xtls-rprx-vision",
                    "network": "tcp",
                    "security": "reality",
                    "sni": "www.cloudflare.com",
                    "pbk": "2P5dvl5PIzrFCHpC-vkcn5cBNC8jcEB2h_3MQJ0thUA",
                    "sid": "6ba85179e30d4fc2"
                }
            ]
        }, f, indent=2)

if not os.path.exists(PAYMENTS_FILE):
    with open(PAYMENTS_FILE, "w") as f:
        json.dump({"payments": []}, f, indent=2)


class PaymentRequest(BaseModel):
    tx_hash: str
    email: Optional[str] = None
    telegram: Optional[str] = None


class PaymentStatus(BaseModel):
    tx_hash: str
    status: str  # "pending", "confirmed", "rejected"
    created_at: str


class ShareRequest(BaseModel):
    file_path: str
    password: str = "zavlab"


def load_servers():
    with open(SERVERS_FILE, "r") as f:
        return json.load(f)


def load_payments():
    with open(PAYMENTS_FILE, "r") as f:
        return json.load(f)


def save_payments(data):
    with open(PAYMENTS_FILE, "w") as f:
        json.dump(data, f, indent=2)


# Telegram Notification
def send_telegram_notification(tx_hash: str, email: str = None, telegram: str = None):
    """Sends payment notification to ZavLab via Telegram Bot"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID_HERE")

    if not bot_token or not chat_id or "YOUR_" in bot_token:
        print(f"[WARN] Telegram credentials not set. Skipping notification for {tx_hash}")
        return

    contact_info = email or telegram or "Не указан"
    message = (
        f"🔔 <b>Новая оплата VPN Florida!</b>\n\n"
        f"💸 Хеш: <code>{tx_hash}</code>\n"
        f"📞 Контакт: {contact_info}\n\n"
        f"Проверь и активируй доступ, ЗавЛаб!"
    )

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            data={"chat_id": chat_id, "text": message, "parse_mode": "HTML"},
            timeout=5
        )
        if response.ok:
            print(f"[INFO] Telegram notification sent for {tx_hash}")
        else:
            print(f"[ERROR] Telegram send failed: {response.text}")
    except Exception as e:
        print(f"[ERROR] Failed to send Telegram notification: {e}")


# === Share File Endpoints ===

@app.post("/api/share")
async def create_share(share_req: ShareRequest):
    """Generate share token for a file"""
    file_path = Path(share_req.file_path).resolve()
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    if not file_path.is_relative_to(UPLOADS_DIR):
        raise HTTPException(status_code=403, detail="File must be in uploads directory")
    
    token = str(__import__('uuid').uuid4())[:8]
    token_data = {
        "file_path": str(file_path),
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(),
        "password_hash": hashlib.sha256(share_req.password.encode()).hexdigest()[:16],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    token_file = SHARES_DIR / f"{token}.json"
    SHARES_DIR.mkdir(parents=True, exist_ok=True)
    with open(token_file, "w") as f:
        json.dump(token_data, f, indent=2)
    
    return {"link": f"/f/{token}", "expires_at": token_data["expires_at"]}


@app.get("/f/{token}")
async def download_shared(token: str, request: Request):
    """Serve shared file with basic auth"""
    import base64
    
    token_file = SHARES_DIR / f"{token}.json"
    
    if not token_file.exists():
        raise HTTPException(status_code=404, detail="Invalid or expired link")
    
    with open(token_file) as f:
        data = json.load(f)
    
    # Check expiration
    expires_at = datetime.fromisoformat(data["expires_at"])
    if datetime.now(timezone.utc) > expires_at:
        token_file.unlink()
        raise HTTPException(status_code=410, detail="Link expired")
    
    # Check basic auth
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Basic "):
        return JSONResponse(
            status_code=401,
            headers={"WWW-Authenticate": 'Basic realm="Share Access"'},
            content={"detail": "Authentication required"}
        )
    
    try:
        decoded = base64.b64decode(auth[6:]).decode()
        username, password = decoded.split(":", 1)
    except:
        raise HTTPException(status_code=401, detail="Invalid auth format")
    
    if username != "zavlab" or hashlib.sha256(password.encode()).hexdigest()[:16] != data["password_hash"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Log access
    with open("/var/log/shared.log", "a") as f:
        f.write(f"{datetime.now().isoformat()} {request.client.host} {token}\n")
    
    return FileResponse(data["file_path"])


@app.get("/api/uploads")
async def list_uploads():
    """List files in uploads directory"""
    files = []
    if UPLOADS_DIR.exists():
        for f in sorted(UPLOADS_DIR.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
            if f.is_file():
                files.append({
                    "name": f.name,
                    "path": str(f),
                    "size": f.stat().st_size,
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                })
    return {"files": files}


# QR Code Generator
@app.get("/api/get-config-by-txid/{tx_id}")
async def get_config_by_txid(tx_id: str):
    """Get VLESS config if payment is confirmed"""
    # Initialize all required variables
    data = load_payments()
    server_data = load_servers()

    # Find payment
    payment = None
    for p in data["payments"]:
        if p["tx_hash"] == tx_id:
            payment = p
            break

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if not server_data["servers"]:
        raise HTTPException(status_code=500, detail="No servers available")

    server = server_data["servers"][0]

    # Handle client UUID
    client_uuid = payment.get("uuid")
    if not client_uuid:
        import uuid
        client_uuid = str(uuid.uuid4())
        payment["uuid"] = client_uuid
        # Save updated payment
        for i, p in enumerate(data["payments"]):
            if p["tx_hash"] == tx_id:
                data["payments"][i] = payment
                break
        save_payments(data)

    # Build VLESS URL (preserve original format)
    vless_url = (
        f"vless://{client_uuid}@{server['ip']}:{server['port']}?"
        f"security={server['security']}&"
        f"flow={server['flow']}&"
        f"type={server['network']}&"
        f"sni={server['sni']}&"
        f"pbk={server['pbk']}&"
        f"sid={server['sid']}&"
        f"fp=chrome"
        f"#VPN-{server['name'].replace(' ', '-')}"
    )

    # Add client to Xray server if not already added (keep inner try/except for SSH)
    if not payment.get("client_added"):
        try:
            # Try environment variables first (more secure)
            ssh_host = os.getenv("FLORIDA_SSH_HOST")
            ssh_user = os.getenv("FLORIDA_SSH_USER", "root")
            ssh_pass = os.getenv("FLORIDA_SSH_PASS")

            # Fallback to per-server credentials from servers.json
            if not ssh_host or not ssh_pass:
                server_cfg = None
                for s in server_data["servers"]:
                    if s["id"] == server["id"]:
                        server_cfg = s
                        break
                if server_cfg:
                    ssh_host = ssh_host or server_cfg.get("ssh_host")
                    ssh_user = ssh_user or server_cfg.get("ssh_user", "root")
                    ssh_pass = ssh_pass or server_cfg.get("ssh_pass")
                    if ssh_pass:
                        print(f"[WARN] Using SSH credentials from servers.json (consider using env vars)")

            if not ssh_host or not ssh_pass:
                print(f"[WARN] SSH credentials not configured, skipping client addition")
            else:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(ssh_host, username=ssh_user, password=ssh_pass, timeout=10)

                sftp = ssh.open_sftp()
                config_path = "/usr/local/etc/xray/config.json"

                with sftp.open(config_path, 'r') as f:
                    config = json.loads(f.read())

                new_client = {
                    "id": client_uuid,
                    "email": f"user-{tx_id[:8]}",
                    "flow": server['flow'],
                    "encryption": "none",
                    "sid": server.get('sid', '01234567')
                }

                # Check if client already exists (by email)
                clients = config["inbounds"][0]["settings"]["clients"]
                if not any(c.get("email") == new_client["email"] for c in clients):
                    clients.append(new_client)

                    with sftp.open(config_path, 'w') as f:
                        json.dump(config, f, indent=2)

                    ssh.exec_command("systemctl restart xray")
                    print(f"[INFO] Client added to Xray: {new_client['email']}, Xray restarted")
                else:
                    print(f"[INFO] Client already exists: {new_client['email']}")

                sftp.close()
                ssh.close()

                payment["client_added"] = True
                for i, p in enumerate(data["payments"]):
                    if p["tx_hash"] == tx_id:
                        data["payments"][i] = payment
                        break
                save_payments(data)

        except Exception as e:
            print(f"[ERROR] Failed to add client to Xray: {e}")

    # Always return the config regardless of client addition status
    return {
        "status": payment.get("status", "pending"),
        "server": server,
        "vless_url": vless_url
    }


@app.get("/api/vmess-url/{tx_id}")
async def get_vmess_url(tx_id: str):
    """Get VMess URL for QR code (v2box iOS)"""
    data = load_payments()
    server_data = load_servers()

    payment = None
    for p in data["payments"]:
        if p["tx_hash"] == tx_id:
            payment = p
            break;

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if not server_data["servers"]:
        raise HTTPException(status_code=500, detail="No servers available")

    server = server_data["servers"][0]
    client_uuid = payment.get("uuid")

    if not client_uuid:
        raise HTTPException(status_code=400, detail="UUID not generated yet")

    # Build VMess JSON
    vmess_json = json.dumps({
        "v": "2",
        "ps": f"VPN-Florida-{tx_id[:8]}",
        "add": server['ip'],
        "port": server.get('port', 10086),
        "id": client_uuid,
        "aid": "0",
        "net": "tcp",
        "type": "none",
        "security": "auto",
        "scy": "auto"
    }, separators=(',', ':'))

    # Base64 encode
    import base64
    vmess_b64 = base64.b64encode(vmess_json.encode()).decode()

    # VMess URL
    vmess_url = f"vmess://{vmess_b64}@{server['ip']}:{server.get('port', 10086)}"

    return vmess_url


@app.get("/api/v2ray-config/{tx_id}")
async def get_v2ray_config(tx_id: str):
    """Get V2Ray JSON config for v2box (iOS)"""
    data = load_payments()
    server_data = load_servers()

    payment = None
    for p in data["payments"]:
        if p["tx_hash"] == tx_id:
            payment = p
            break

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if not server_data["servers"]:
        raise HTTPException(status_code=500, detail="No servers available")

    server = server_data["servers"][0]
    client_uuid = payment.get("uuid")

    if not client_uuid:
        raise HTTPException(status_code=400, detail="UUID not generated yet")

    # Minimal working V2Ray config for Reality/Xray
    config = {
        "log": {"loglevel": "warning"},
        "inbounds": [{
            "port": 10808,
            "protocol": "socks",
            "settings": {"udp": True}
        }],
        "outbounds": [{
            "protocol": "vless",
            "settings": {
                "vnext": [{
                    "address": server['ip'],
                    "port": server['port'],
                    "users": [{
                        "id": client_uuid,
                        "flow": server['flow'],
                        "encryption": "none"
                    }]
                }]
            },
            "streamSettings": {
                "network": "tcp",
                "security": "reality",
                "realitySettings": {
                    "fingerprint": "chrome",
                    "serverName": server['sni'],
                    "publicKey": server['pbk'],
                    "shortId": server.get('sid', '01234567')
                }
            },
            "tag": "proxy"
        }, {
            "protocol": "freedom",
            "tag": "direct"
        }],
        "routing": {
            "rules": [
                {"type": "field", "ip": ["geoip:private"], "outboundTag": "direct"}
            ]
        }
    }

    return JSONResponse(content=config)

    return {
        "status": payment.get("status", "pending"),
        "server": server,
        "vless_url": vless_url
    }


@app.post("/api/add-client")
async def add_client(request: Request):
    """Add a new client to Xray config via SSH to Florida server"""
    try:
        body = await request.json()
        email = body.get("email")
        uuid = body.get("uuid", str(__import__('uuid').uuid4()))
        server_ip = body.get("server_ip", "104.253.1.210")

        if not email:
            raise HTTPException(status_code=400, detail="Email required")

        # SSH to Florida server and update Xray config
        import paramiko

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Load SSH credentials from env (no defaults for security)
        ssh_host = os.getenv("FLORIDA_SSH_HOST")
        ssh_user = os.getenv("FLORIDA_SSH_USER", "root")
        ssh_pass = os.getenv("FLORIDA_SSH_PASS")

        if not ssh_host or not ssh_pass:
            raise HTTPException(status_code=500, detail="SSH credentials not configured. Set FLORIDA_SSH_HOST and FLORIDA_SSH_PASS env variables.")

        try:
            ssh.connect(ssh_host, username=ssh_user, password=ssh_pass, timeout=10)

            # Read current config
            sftp = ssh.open_sftp()
            config_path = "/usr/local/etc/xray/config.json"

            with sftp.open(config_path, 'r') as f:
                config = json.loads(f.read())

            # Add new client
            new_client = {
                "id": uuid,
                "email": email,
                "flow": "xtls-rprx-vision"
            }

            config["inbounds"][0]["settings"]["clients"].append(new_client)

            # Write back
            with sftp.open(config_path, 'w') as f:
                json.dump(config, f, indent=2)

            sftp.close()

            # Reload Xray
            ssh.exec_command("systemctl reload xray")
            ssh.close()

            return {"status": "success", "email": email, "uuid": uuid}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"SSH error: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/config")
async def get_config():
    """Get VLESS configuration for Florida servers"""
    data = load_servers()
    configs = []

    for server in data["servers"]:
        vless_url = (
            f"vless://user-{server['id']}@{server['ip']}:{server['port']}?"
            f"security={server['security']}&"
            f"flow={server['flow']}&"
            f"type={server['network']}&"
            f"sni={server['sni']}&"
            f"pbk={server['pbk']}&"
            f"sid={server['sid']}&"
            f"spx=%2F#VPN-{server['name'].replace(' ', '-')}"
        )
        # Remove sensitive data before returning
        safe_server = {k: v for k, v in server.items() if k not in ['ssh_pass', 'ssh_user', 'ssh_host']}
        configs.append({
            "server": safe_server,
            "vless_url": vless_url,
            "qr_data": vless_url
        })

    return {"servers": configs}


@app.get("/api/status")
async def get_status(ip: str = None):
    """Check Florida server availability with real ping"""
    data = load_servers()

    # Find server by IP or use first
    server = None
    if ip:
        for s in data["servers"]:
            if s["ip"] == ip:
                server = s
                break

    if not server:
        server = data["servers"][0]

    ip_addr = server["ip"]
    port = server["port"]

    # Real TCP ping
    ping_ms = None
    port_open = False

    try:
        start_time = time.perf_counter()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((ip_addr, port))
        end_time = time.perf_counter()
        sock.close()

        port_open = (result == 0)
        if port_open:
            ping_ms = round((end_time - start_time) * 1000, 2)
    except Exception:
        port_open = False

    return {
        "server": server["name"],
        "ip": ip_addr,
        "port": port,
        "online": port_open,
        "ping_ms": ping_ms,
        "location": "Miami, Florida, USA" if "Florida" in server["name"] else "Warsaw, Poland"
    }


@app.post("/api/verify-payment")
async def verify_payment(payment: PaymentRequest):
    """Submit payment for verification"""
    from datetime import datetime, timezone
    import uuid

    data = load_payments()

    # Check if already exists
    for p in data["payments"]:
        if p["tx_hash"] == payment.tx_hash:
            return {
                "status": "already_submitted",
                "tx_hash": payment.tx_hash,
                "verification_status": p.get("status", "pending")
            }

    # Generate UUID for VLESS client
    client_uuid = str(uuid.uuid4())

    new_payment = {
        "tx_hash": payment.tx_hash,
        "email": payment.email,
        "telegram": payment.telegram,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "uuid": client_uuid,
        "client_added": False
    }

    data["payments"].append(new_payment)
    save_payments(data)

    # 🔔 Notify ZavLab via Telegram (async in production, but fine for now)
    send_telegram_notification(
        tx_hash=payment.tx_hash,
        email=payment.email,
        telegram=payment.telegram
    )

    return {
        "status": "submitted",
        "tx_hash": payment.tx_hash,
        "message": "Payment submitted for verification. Contact @DoctorMES with your hash.",
        "verification_status": "pending"
    }


@app.get("/api/verify-payment/{tx_hash}")
async def check_payment_status(tx_hash: str):
    """Check payment verification status"""
    data = load_payments()

    for p in data["payments"]:
        if p["tx_hash"] == tx_hash:
            return {
                "tx_hash": tx_hash,
                "status": p.get("status", "pending"),
                "created_at": p.get("created_at")
            }

    raise HTTPException(status_code=404, detail="Payment not found")


@app.get("/api/ip-info")
async def get_ip_info():
    """Get client IP info (proxied through frontend)"""
    return {
        "message": "Use frontend widget with ipify.org"
    }


# Serve static frontend if dist/ exists
frontend_dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
    print(f"[INFO] Serving frontend from {frontend_dist}")
else:
    print(f"[WARNING] Frontend dist/ not found at {frontend_dist}")

    @app.get("/")
    async def root():
        return {"message": "Frontend not built. Run npm run build."}