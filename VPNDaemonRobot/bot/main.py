#!/usr/bin/env python3
import asyncio, json, logging, os, sys, uuid, subprocess, base64, re
from pathlib import Path
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, BufferedInputFile
from dotenv import load_dotenv
import qrcode
from io import BytesIO
import aiohttp
from aiohttp import web
import shlex

# Load .env from project root
BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / '.env')

# Load config from environment
TOKEN = os.getenv('TELEGRAM_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID') or 0)
if not TOKEN or not ADMIN_ID: logging.error(" TOKEN/ADMIN_ID missing"); sys.exit(1)

# Paths from .env (with fallback to BASE_DIR)
XRAY_CONFIG = Path(os.getenv('XRAY_CONFIG', BASE_DIR / 'vpnconfig' / 'xray.json'))
CLIENTS_DB = Path(os.getenv('CLIENTS_DB', BASE_DIR / 'vpnconfig' / 'clients.json'))
USERS_DB = Path(os.getenv('USERS_DB', BASE_DIR / 'vpnconfig' / 'users.json'))
KEYS_FILE = Path(os.getenv('KEYS_FILE', BASE_DIR / 'vpnconfig' / 'keys' / 'reality_keys.json'))
LOG_FILE = Path(os.getenv('LOG_FILE', BASE_DIR / 'logs' / 'bot.log'))
LOG_DIR = LOG_FILE.parent
LOG_DIR.mkdir(parents=True, exist_ok=True)

# VPN settings
SERVER_IP = os.getenv('SERVER_IP', '185.138.90.150')
VPN_PORT = int(os.getenv('VPN_PORT', 443))
REALITY_SNI = os.getenv('REALITY_SNI', 'www.microsoft.com')
REALITY_FP = os.getenv('REALITY_FP', 'chrome')
SERVERS_FILE = Path(BASE_DIR / 'vpnconfig' / 'servers.json')

logging.basicConfig(level=logging.INFO, format='%(asctime)s|%(message)s',
                    handlers=[logging.FileHandler(LOG_FILE, encoding='utf-8'), logging.StreamHandler()])
log = logging.getLogger(__name__)
bot = Bot(token=TOKEN)
dp = Dispatcher()

def load_json(p):
    with open(p, 'r', encoding='utf-8') as f: return json.load(f)
def save_json(p, d):
    tmp = p.with_suffix('.tmp')
    with open(tmp, 'w', encoding='utf-8') as f: json.dump(d, f, indent=2, ensure_ascii=False)
    tmp.replace(p)
def fmt_limit(b):
    if not b: return '∞'
    return f"{b/(1024**3):.1f} GB" if b>=1024**3 else f"{b/1024**2:.0f} MB"
def fmt_traffic(b):
    if b < 1024: return f"{b} B"
    if b < 1024**2: return f"{b/1024:.1f} KB"
    if b < 1024**3: return f"{b/(1024**2):.1f} MB"
    return f"{b/(1024**3):.2f} GB"
def reload_xray():
    subprocess.run(['systemctl', 'reload-or-restart', 'demonvpn'], timeout=10, capture_output=True)

def load_servers():
    """Load servers from servers.json"""
    try:
        return load_json(SERVERS_FILE).get('servers', [])
    except Exception as e:
        log.error(f"load_servers error: {e}")
        return []

def get_server_by_name(name):
    """Get server config by name"""
    servers = load_servers()
    for s in servers:
        if s['name'] == name:
            return s
    return None

def ssh_exec(server_name, cmd):
    """Execute command on remote server via SSH"""
    s = get_server_by_name(server_name)
    if not s: return None, 'Server not found'
    ip = s['ip']
    # Get server-specific SSH credentials from .env
    # Format: <SERVER_NAME>_SSH_USER, <SERVER_NAME>_SSH_PASS
    name_upper = s['name'].replace('-', '_').upper()
    user = os.getenv(f'{name_upper}_SSH_USER', os.getenv('FLORIDA_SSH_USER', 'root'))
    passwd = os.getenv(f'{name_upper}_SSH_PASS', os.getenv('FLORIDA_SSH_PASS', ''))
    ssh_cmd = f"sshpass -p {shlex.quote(passwd)} ssh -o StrictHostKeyChecking=no {user}@{ip} {shlex.quote(cmd)}"
    try:
        result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout, result.stderr
    except Exception as e:
        return None, str(e)

def add_client_to_server(server_name, uuid, email):
    """Add client to remote server's Xray config"""
    s = get_server_by_name(server_name)
    if not s: return False, 'Server not found'
    
    # For local server (Warsaw) - use local Xray config
    if s['ip'] == SERVER_IP:
        cfg = load_json(XRAY_CONFIG)
        cfg['inbounds'][0]['settings']['clients'].append({'id': uuid, 'email': email, 'flow': ''})
        save_json(XRAY_CONFIG, cfg)
        reload_xray()
        return True, 'OK'
    
    # For remote server (Florida) - SSH and modify config
    cfg_path = os.getenv('FLORIDA_XRAY_CONFIG', '/usr/local/etc/xray/config.json')
    # Get remote config
    stdout, stderr = ssh_exec(server_name, f"cat {cfg_path}")
    if not stdout: return False, f'Failed to read remote config: {stderr}'
    try:
        cfg = json.loads(stdout)
        # Find the Reality inbound (port 10086 for Florida)
        target_port = s.get('port', 10086)
        inbound = None
        for ib in cfg.get('inbounds', []):
            if ib.get('port') == target_port:
                inbound = ib
                break
        if not inbound:
            return False, f'Inbound with port {target_port} not found on {server_name}'
        inbound['settings']['clients'].append({'id': uuid, 'email': email, 'flow': 'xtls-rprx-vision'})
        # Write updated config back
        new_cfg_str = json.dumps(cfg, indent=2)
        # Use a temp file and scp, or echo with escaping
        esc = shlex.quote(new_cfg_str)
        stdout, stderr = ssh_exec(server_name, f"cat > {cfg_path} << 'XRAYEOF'\n{new_cfg_str}\nXRAYEOF")
        # Reload remote Xray
        ssh_exec(server_name, 'systemctl reload-or-restart xray')
        return True, 'OK'
    except Exception as e:
        return False, str(e)
def get_xray_log_path():
    try:
        cfg = load_json(XRAY_CONFIG)
        return Path(cfg['log']['access'])
    except Exception as e:
        log.error(f"get_xray_log_path error: {e}")
        return LOG_DIR / 'xray-access.log'
def get_active():
    try:
        log_path = get_xray_log_path()
        if not log_path.exists(): return 0
        lines = log_path.read_text(errors='ignore').split('\n')[-500:]
        emails = {l.split('email: ')[1].strip().split()[0] for l in lines if 'accepted' in l and 'email:' in l}
        return len(emails)
    except Exception as e:
        log.error(f"get_active error: {e}")
        return 0
def get_last_activity(email):
    try:
        log_path = get_xray_log_path()
        if not log_path.exists(): return None
        lines = log_path.read_text(errors='ignore').split('\n')
        for line in reversed(lines):
            if 'email:' in line and email in line and 'accepted' in line:
                # Extract timestamp from log line
                parts = line.split('|')
                if parts:
                    return parts[0].strip()
        return None
    except Exception as e:
        log.error(f"get_last_activity error: {e}")
        return None

def get_recent_activity(limit=5):
    """Get recent client activity from logs"""
    try:
        log_path = get_xray_log_path()
        if not log_path.exists(): return []

        lines = log_path.read_text(errors='ignore').split('\n')
        seen = set()
        recent = []

        for line in reversed(lines):
            if 'accepted' in line and 'email:' in line:
                try:
                    # Extract email
                    email = line.split('email: ')[1].strip().split()[0]
                    if email in seen: continue
                    seen.add(email)

                    # Try to parse timestamp and calculate time ago
                    time_ago = "unknown"
                    try:
                        if '|' in line:
                            time_str = line.split('|')[0].strip()
                            parts = time_str.split()
                            if len(parts) >= 2:
                                time_part = parts[0] + ' ' + parts[1]
                                log_time = datetime.strptime(time_part, "%Y/%m/%d %H:%M:%S")
                                delta = datetime.now() - log_time
                                if delta.days > 0:
                                    time_ago = f"{delta.days}d ago"
                                elif delta.seconds > 3600:
                                    time_ago = f"{delta.seconds//3600}h ago"
                                elif delta.seconds > 60:
                                    time_ago = f"{delta.seconds//60}m ago"
                                else:
                                    time_ago = "just now"
                    except Exception as e:
                        pass

                    recent.append({
                        'email': email,
                        'time': time_ago,
                        'emoji': '🟢'
                    })

                    if len(recent) >= limit:
                        break
                except Exception as e:
                    log.debug(f"get_recent_activity parse error: {e}")
                    continue

        return recent
    except Exception as e:
        log.error(f"get_recent_activity error: {e}")
        return []

def is_client_online(email, minutes=5):
    """Check if client was active in last X minutes"""
    try:
        log_path = get_xray_log_path()
        if not log_path.exists(): return False

        lines = log_path.read_text(errors='ignore').split('\n')
        cutoff = datetime.now() - timedelta(minutes=minutes)

        for line in reversed(lines):
            if 'accepted' in line and 'email:' in line and email in line:
                try:
                    if '|' in line:
                        time_str = line.split('|')[0].strip()
                        parts = time_str.split()
                        if len(parts) >= 2:
                            time_part = parts[0] + ' ' + parts[1]
                            log_time = datetime.strptime(time_part, "%Y/%m/%d %H:%M:%S")
                            return log_time > cutoff
                except Exception as e:
                    log.debug(f"is_client_online parse error: {e}")
                    continue
        return False
    except Exception as e:
        log.error(f"is_client_online error: {e}")
        return False

def gen_link(u, email, server_name=None):
    """Generate VLESS link, optionally for specific server"""
    if server_name:
        s = get_server_by_name(server_name)
        if s:
            ip = s['ip']
            port = s.get('port', 443)
            sni = s.get('reality_sni', REALITY_SNI)
            fp = s.get('reality_fp', REALITY_FP)
            pk = s.get('public_key', '')
            sid = 'a1b2c3d4'
            return f"vless://{u}@{ip}:{port}?type=tcp&security=reality&sni={sni}&pbk={pk}&sid={sid}&fp={fp}#{email}"
    # Fallback to default (Warsaw)
    k = load_json(KEYS_FILE); pk = k['public_key']; sid = k['short_id']
    return f"vless://{u}@{SERVER_IP}:{VPN_PORT}?type=tcp&security=reality&sni={REALITY_SNI}&pbk={pk}&sid={sid}&fp={REALITY_FP}#{email}"

async def get_traffic_stats(email=None):
    """Get traffic stats from Xray API"""
    try:
        api_socket = os.getenv("XRAY_API_SOCKET", str(BASE_DIR / "runtime" / "api.sock"))
        cmd = ['xray', 'api', 'stats', f'--server=unix://{api_socket}']
        if email:
            cmd.extend(['-name', f'user>>>{email}>>>traffic>>>downvalue', '-reset'])
        else:
            cmd.extend(['-name', 'inbound>>>traffic>>>downvalue', '-reset'])

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            log.error(f"Xray API error: {stderr.decode()}")
            return {}

        output = stdout.decode()
        stats = {}
        for line in output.strip().split('\n'):
            if 'value:' in line:
                parts = line.split()
                name_idx = parts.index('name:') if 'name:' in parts else -1
                value_idx = parts.index('value:') if 'value:' in parts else -1
                if name_idx >= 0 and value_idx >= 0:
                    name = parts[name_idx + 1].strip('"')
                    value = int(parts[value_idx + 1])
                    stats[name] = value
        return stats
    except Exception as e:
        log.error(f"get_traffic_stats error: {e}")
        return {}

def generate_qr(data):
    """Generate QR code image"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    bio = BytesIO()
    img.save(bio, 'PNG')
    bio.seek(0)
    return bio

def get_subscription_link():
    """Generate subscription URL for importing all clients"""
    # This will be served by our simple HTTP server
    return f"http://{SERVER_IP}:8081/sub/{TOKEN}"

def generate_subscription_content():
    """Generate base64-encoded subscription content with all active clients"""
    db = load_json(CLIENTS_DB)
    links = []
    for client in db['clients']:
        if client.get('active', True):
            links.append(gen_link(client['uuid'], client['email']))
    content = '\n'.join(links)
    return base64.b64encode(content.encode()).decode()

# Subscription web server
async def subscription_handler(request):
    """Handle subscription requests"""
    token = request.match_info.get('token', '')
    if token != TOKEN:
        return web.Response(status=403, text='Forbidden')

    content = generate_subscription_content()
    return web.Response(text=content, content_type='text/plain')

async def start_subscription_server():
    """Start the subscription HTTP server"""
    app = web.Application()
    app.router.add_get('/sub/{token}', subscription_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8081)
    await site.start()
    log.info("Subscription server started on port 8081")
    return runner

async def cleanup_inactive_clients(days=30, dry_run=False):
    """Cleanup clients that haven't been active for specified days"""
    log_path = get_xray_log_path()
    if not log_path.exists():
        return 0, []

    cutoff = datetime.now() - timedelta(days=days)
    db = load_json(CLIENTS_DB)
    active_clients = db.get('clients', [])

    # Get last activity for each client from logs
    lines = log_path.read_text(errors='ignore').split('\n')
    client_last_seen = {}

    for line in reversed(lines):
        if 'email:' in line and 'accepted' in line:
            try:
                email = line.split('email: ')[1].strip().split()[0]
                if email not in client_last_seen:
                    client_last_seen[email] = True
            except Exception as e:
                log.debug(f"cleanup log parse error: {e}")

    to_remove = []
    for client in active_clients:
        email = client['email']
        should_remove = False

        # Check if client was created more than 'days' ago and is not active
        try:
            created = datetime.fromisoformat(client.get('created', datetime.now().isoformat()))
            if created < cutoff and not client.get('active', True):
                should_remove = True
        except Exception as e:
            log.debug(f"cleanup date parse error for {email}: {e}")

        if should_remove:
            to_remove.append(client)

    removed = []
    if not dry_run and to_remove:
        for client in to_remove:
            # Remove from xray config
            cfg = load_json(XRAY_CONFIG)
            cfg['inbounds'][0]['settings']['clients'] = [
                x for x in cfg['inbounds'][0]['settings']['clients'] if x.get('email') != client.get('email')
            ]
            save_json(XRAY_CONFIG, cfg)
            removed.append(client['email'])
            log.info(f" Auto-removed inactive client: {client['email']}")

        db['clients'] = [x for x in active_clients if x not in to_remove]
        save_json(CLIENTS_DB, db)

        if removed:
            reload_xray()

    return len(to_remove), [c['email'] for c in to_remove] if to_remove else []

def main_kb():
    sub_link = get_subscription_link()
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=' Клиенты', callback_data='clients_list'),
         InlineKeyboardButton(text=' Статус', callback_data='status')],
        [InlineKeyboardButton(text=' Подписка', url=sub_link),
         InlineKeyboardButton(text=' Настройки', callback_data='settings')]
    ])
def back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=' Назад', callback_data='back_main')]])

user_state = {}

@dp.message(CommandStart())
async def cmd_start(m: types.Message):
    if m.from_user.id != ADMIN_ID: return
    await show_dashboard(m)

@dp.callback_query(F.data == 'back_main')
async def cb_back(c: CallbackQuery):
    if c.from_user.id != ADMIN_ID: return await c.answer('', show_alert=True)
    await show_dashboard(c.message, edit=True)
    await c.answer()

async def show_dashboard(target, edit=False):
    """Show main dashboard with stats"""
    # Get client stats
    cl = load_json(CLIENTS_DB)['clients']
    total = len(cl)
    active = len([x for x in cl if x.get('active', True)])
    inactive = total - active
    online = get_active()

    # Get system status
    xray_status = '🟢' if os.system('systemctl is-active --quiet demonvpn') == 0 else '🔴'
    bot_status = '🟢' if os.system('systemctl is-active --quiet demonvpn-bot') == 0 else '🔴'

    # Get system uptime
    uptime = "?"
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            uptime_days = int(uptime_seconds // 86400)
            uptime_hours = int((uptime_seconds % 86400) // 3600)
            if uptime_days > 0:
                uptime = f"{uptime_days}d {uptime_hours}h"
            else:
                uptime = f"{uptime_hours}h"
    except Exception as e:
        log.debug(f"show_dashboard uptime error: {e}")

    # Get recent activity
    recent = get_recent_activity(limit=3)

    # Build dashboard
    txt = "🔐 <b>VPNDaemon Dashboard</b>\n"
    txt += "━━━━━━━━━━━━━━━━━\n"
    txt += f"👥 <b>Clients:</b> {total} total\n"
    txt += f"  ✅ Active: {active}\n"
    txt += f"  ❌ Inactive: {inactive}\n\n"
    txt += f"🌐 <b>Online now:</b> {online}\n"

    if recent:
        txt += f"\n🕐 <b>Recent activity:</b>\n"
        for r in recent:
            txt += f"  {r['emoji']} {r['email']} - {r['time']}\n"

    txt += f"\n━━━━━━━━━━━━━━━━━\n"
    txt += f"{xray_status} Xray: {'running' if xray_status == '🟢' else 'STOPPED'}\n"
    txt += f"{bot_status} Bot: {'running' if bot_status == '🟢' else 'STOPPED'}\n"
    txt += f"⏱ Uptime: {uptime}\n"
    txt += f"🗺 {SERVER_IP}:{VPN_PORT}\n"

    # System resources
    try:
        with open('/proc/loadavg', 'r') as f:
            cpu_load = f.read().split()[0]
            txt += f"💻 CPU: {cpu_load}\n"
    except Exception as e:
        log.debug(f"show_dashboard cpu error: {e}")

    try:
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
            mem_total = int([l for l in lines if 'MemTotal' in l][0].split()[1])
            mem_free = int([l for l in lines if 'MemFree' in l][0].split()[1])
            mem_used_pct = int((mem_total - mem_free) / mem_total * 100)
            # Progress bar
            filled = '█' * (mem_used_pct // 10)
            empty = '░' * (10 - mem_used_pct // 10)
            txt += f"🧠 RAM: {mem_used_pct}% {filled}{empty}\n"
    except Exception as e:
        log.debug(f"show_dashboard ram error: {e}")

    try:
        import shutil
        usage = shutil.disk_usage('/root')
        disk_pct = int(usage.used / usage.total * 100)
        filled = '█' * (disk_pct // 10)
        empty = '░' * (10 - disk_pct // 10)
        txt += f"💾 Disk: {disk_pct}% {filled}{empty}\n"
    except Exception as e:
        log.debug(f"show_dashboard disk error: {e}")

    # Log size
    try:
        log_path = get_xray_log_path()
        if log_path.exists():
            txt += f"📄 Log: {fmt_traffic(log_path.stat().st_size)}\n"
    except Exception as e:
        log.debug(f"show_dashboard log size error: {e}")

    # Alerts
    try:
        if mem_used_pct > 90:
            txt += "⚠️ RAM usage critical!\n"
    except Exception as e:
        log.debug(f"show_dashboard alert error: {e}")

    try:
        if disk_pct > 90:
            txt += "⚠️ Disk usage critical!\n"
    except Exception as e:
        log.debug(f"show_dashboard disk alert error: {e}")

    # Build keyboard: first Add button, then client list
    kb_buttons = []
    # Add client button
    kb_buttons.append([InlineKeyboardButton(text='➕ Добавить', callback_data='add_client')])
    # Load clients
    cl = load_json(CLIENTS_DB)['clients']
    # Sort clients by email
    for client in sorted(cl, key=lambda x: x['email']):
        email = client['email']
        online = is_client_online(email)
        emoji = '🟢' if online else '⚫'
        btn_text = f"{emoji} {email}"
        kb_buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f'client_{email}')])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_buttons)

    if edit:
        await target.edit_text(txt, reply_markup=kb, parse_mode='HTML')
    else:
        await target.answer(txt, reply_markup=kb, parse_mode='HTML')

@dp.callback_query(F.data == 'status')
async def cb_status(c: CallbackQuery):
    if c.from_user.id != ADMIN_ID: return await c.answer('', show_alert=True)

    # Xray status
    xray_running = os.system('systemctl is-active --quiet demonvpn') == 0
    xray_status = '🟢 running' if xray_running else '🔴 STOPPED'

    # Bot status
    bot_running = os.system('systemctl is-active --quiet demonvpn-bot') == 0
    bot_status = '🟢 running' if bot_running else '🔴 STOPPED'

    # Online count
    online = get_active()

    # System resources
    cpu_load = "?.??"
    try:
        with open('/proc/loadavg', 'r') as f:
            cpu_load = f.read().split()[0]
    except Exception as e:
        log.debug(f"cb_status cpu error: {e}")

    mem_pct = "?"
    try:
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
            mem_total = int([l for l in lines if 'MemTotal' in l][0].split()[1])
            mem_free = int([l for l in lines if 'MemFree' in l][0].split()[1])
            mem_used_pct = int((mem_total - mem_free) / mem_total * 100)
            filled = '█' * (mem_used_pct // 10)
            empty = '░' * (10 - mem_used_pct // 10)
            mem_pct = f"{mem_used_pct}% {filled}{empty}"
    except Exception as e:
        log.debug(f"cb_status ram error: {e}")

    # Disk usage
    disk_pct = "?"
    try:
        import shutil
        usage = shutil.disk_usage('/root')
        disk_pct_val = int(usage.used / usage.total * 100)
        filled = '█' * (disk_pct_val // 10)
        empty = '░' * (10 - disk_pct_val // 10)
        disk_pct = f"{disk_pct_val}% {filled}{empty}"
    except Exception as e:
        log.debug(f"cb_status disk error: {e}")

    # Uptime
    uptime = "?"
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            uptime_days = int(uptime_seconds // 86400)
            uptime_hours = int((uptime_seconds % 86400) // 3600)
            if uptime_days > 0:
                uptime = f"{uptime_days}d {uptime_hours}h"
            else:
                uptime = f"{uptime_hours}h"
    except Exception as e:
        log.debug(f"cb_status uptime error: {e}")

    # Log size
    log_size = "0"
    try:
        log_path = get_xray_log_path()
        if log_path.exists():
            log_size = fmt_traffic(log_path.stat().st_size)
    except Exception as e:
        log.debug(f"cb_status log error: {e}")

    # Xray version
    xray_version = "?"
    try:
        import subprocess
        result = subprocess.run(['/usr/local/bin/xray', 'version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            xray_version = result.stdout.strip().split('\n')[0]
    except Exception as e:
        log.debug(f"cb_status xray version error: {e}")

    txt = f"📊 <b>Статус системы</b>\n"
    txt += "━━━━━━━━━━━━━━━━\n"
    txt += f"🟢 Xray: {xray_status}\n"
    txt += f"   {xray_version}\n"
    txt += f"🟢 Bot: {bot_status}\n"
    txt += f"🌐 Online: {online}\n\n"
    txt += f"⏱ Uptime: {uptime}\n"
    txt += f"💻 CPU: {cpu_load}\n"
    txt += f"🧠 RAM: {mem_pct}%\n"
    txt += f"💾 Disk: {disk_pct}%\n"
    txt += f"📄 Log: {log_size}\n"
    txt += f"\n🗺 {SERVER_IP}:{VPN_PORT}"

    await c.message.edit_text(txt, reply_markup=back_kb(), parse_mode='HTML')
    await c.answer()

@dp.callback_query(F.data == 'reload_xray')
async def cb_reload(c: CallbackQuery):
    if c.from_user.id != ADMIN_ID: return await c.answer('', show_alert=True)
    try:
        reload_xray()
        await c.message.edit_text(" X-ray перезапущен", reply_markup=back_kb())
    except Exception as e:
        await c.message.edit_text(f" {e}", reply_markup=back_kb())
    await c.answer()

@dp.callback_query(F.data == 'settings')
async def cb_settings(c: CallbackQuery):
    if c.from_user.id != ADMIN_ID: return await c.answer('', show_alert=True)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=' Очистка старых (30 дн)', callback_data='cleanup_30')],
        [InlineKeyboardButton(text=' Очистка старых (60 дн)', callback_data='cleanup_60')],
        [InlineKeyboardButton(text=' Проверить (без удаления)', callback_data='cleanup_dry')],
        [InlineKeyboardButton(text=' Назад', callback_data='back_main')]
    ])
    await c.message.edit_text(" <b>Настройки</b>\nВыбери действие:", reply_markup=kb, parse_mode='HTML')
    await c.answer()

@dp.callback_query(F.data.startswith('cleanup_'))
async def cb_cleanup(c: CallbackQuery):
    if c.from_user.id != ADMIN_ID: return await c.answer('', show_alert=True)

    action = c.data.split('_')[1]

    if action == 'dry':
        count, clients = await cleanup_inactive_clients(days=30, dry_run=True)
        txt = f" <b>Проверка (dry run)</b>\n"
        txt += f"Найдено неактивных: {count}\n\n"
        if clients:
            txt += "Клиенты:\n"
            for em in clients[:10]:
                txt += f"• {em}\n"
            if len(clients) > 10:
                txt += f"... и еще {len(clients) - 10}\n"
        else:
            txt += "Нет клиентов для удаления"
    else:
        days = int(action)
        count, clients = await cleanup_inactive_clients(days=days, dry_run=False)
        txt = f" <b>Очистка завершена</b>\n"
        txt += f"Удалено клиентов: {count}\n"
        if clients:
            txt += "\nУдалены:\n"
            for em in clients:
                txt += f"• {em}\n"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=' Настройки', callback_data='settings')],
        [InlineKeyboardButton(text=' К списку', callback_data='clients_list')]
    ])
    await c.message.edit_text(txt, reply_markup=kb, parse_mode='HTML')
    await c.answer()

@dp.callback_query(F.data == 'clients_list')
async def cb_clients(c: CallbackQuery):
    if c.from_user.id != ADMIN_ID: return await c.answer('', show_alert=True)
    cl = load_json(CLIENTS_DB)['clients']
    if not cl:
        await c.message.edit_text(" Пусто", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=' Добавить', callback_data='add_client')],
            [InlineKeyboardButton(text=' Назад', callback_data='back_main')]
        ]), parse_mode='HTML')
        return await c.answer()
    txt = " <b>Клиенты</b>\n"
    for item in cl: txt += f"{'' if item.get('active', True) else ''} <code>{item['email']}</code>  {fmt_limit(item.get('limit'))}\n"
    kb = [[InlineKeyboardButton(text=' Добавить', callback_data='add_client')]]
    row = []
    for item in cl:
        row.append(InlineKeyboardButton(text=item['email'], callback_data=f"client_{item['email']}"))
        if len(row) == 2: kb.append(row); row = []
    if row: kb.append(row)
    kb.append([InlineKeyboardButton(text=' Назад', callback_data='back_main')])
    await c.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode='HTML')
    await c.answer()

@dp.callback_query(F.data.startswith('client_'))
async def cb_client(c: CallbackQuery):
    if c.from_user.id != ADMIN_ID: return await c.answer('', show_alert=True)
    em = c.data.split('_', 1)[1]; cl = load_json(CLIENTS_DB)['clients']
    client = next((x for x in cl if x['email'] == em), None)
    if not client: return await c.answer('', show_alert=True)

    # Check if client is online
    online = is_client_online(em)
    online_emoji = '🟢' if online else '⚫'

    # Get last activity
    last_active = get_last_activity(em)
    if last_active is None:
        last_active = "нет данных"

    # Status
    active = client.get('active', True)
    status_emoji = '✅' if active else '❌'
    status_text = 'Активен' if active else 'Отключен'

    txt = f"👤 <b>{em}</b>\n"
    txt += f"━━━━━━━━━━━━━━━━━\n"
    txt += f"{online_emoji} <b>Онлайн:</b> {'ДА' if online else 'НЕТ'}\n"
    txt += f"{status_emoji} <b>Статус:</b> {status_text}\n"
    txt += f"🕐 <b>Последний раз:</b> {last_active}\n"
    txt += f"📅 <b>Создан:</b> {client.get('created', 'нет данных')}\n"
    txt += f"🔑 <b>UUID:</b> <code>{client['uuid'][:8]}...</code>\n"

    kb = [
        [InlineKeyboardButton(text='🔗 Ссылка', callback_data=f'link_{em}'),
         InlineKeyboardButton(text='📱 QR-код', callback_data=f'qr_{em}')],
        [InlineKeyboardButton(text='🗑 Удалить', callback_data=f'delete_{em}')],
        [InlineKeyboardButton(text='⛔ Отозвать' if active else '✅ Активировать',
                              callback_data=f'revoke_{em}' if active else f'activate_{em}')]
    ]
    await c.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode='HTML')
    await c.answer()

@dp.callback_query(F.data.startswith('link_'))
async def cb_link(c: CallbackQuery):
    if c.from_user.id != ADMIN_ID: return await c.answer('', show_alert=True)
    em = c.data.split('_', 1)[1]; cl = load_json(CLIENTS_DB)['clients']
    client = next((x for x in cl if x['email'] == em), None)
    if not client or not client.get('active', True): return await c.answer(' Неактивен', show_alert=True)
    await bot.send_message(c.message.chat.id, f" <b>{em}</b>:\n<pre>{gen_link(client['uuid'], em)}</pre>\n<i>Копируй  вставляй в клиент</i>",
                           parse_mode='HTML', reply_markup=back_kb())
    await c.answer()

@dp.callback_query(F.data.startswith('qr_'))
async def cb_qr(c: CallbackQuery):
    if c.from_user.id != ADMIN_ID: return await c.answer('', show_alert=True)
    em = c.data.split('_', 1)[1]; cl = load_json(CLIENTS_DB)['clients']
    client = next((x for x in cl if x['email'] == em), None)
    if not client or not client.get('active', True): return await c.answer(' Неактивен', show_alert=True)

    link = gen_link(client['uuid'], em)
    qr_img = generate_qr(link)
    # Используем getvalue() вместо read() чтобы избежать проблемы с BytesIO в BufferedInputFile
    qr_data = qr_img.getvalue()
    qr_file = BufferedInputFile(qr_data, filename=f"{em.replace('@', '')}_qr.png")

    await bot.send_photo(c.message.chat.id, photo=qr_file, caption=f" <b>{em}</b>\nQR-код для подключения",
                         parse_mode='HTML')
    await c.answer()

@dp.callback_query(F.data.startswith('delete_'))
async def cb_delete(c: CallbackQuery):
    if c.from_user.id != ADMIN_ID: return await c.answer('', show_alert=True)
    em = c.data.split('_', 1)[1]

    # Confirm deletion
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=' ДА, удалить', callback_data=f'confirm_delete_{em}')],
        [InlineKeyboardButton(text=' Нет, отмена', callback_data=f'client_{em}')]
    ])
    await c.message.edit_text(f" <b>Удаление {em}</b>\nВы уверены? Это действие нельзя отменить!",
                              reply_markup=kb, parse_mode='HTML')
    await c.answer()

@dp.callback_query(F.data.startswith('confirm_delete_'))
async def cb_confirm_delete(c: CallbackQuery):
    if c.from_user.id != ADMIN_ID: return await c.answer('', show_alert=True)
    em = c.data.split('_', 2)[2]

    # Remove from CLIENTS_DB
    db = load_json(CLIENTS_DB)
    db['clients'] = [x for x in db['clients'] if x['email'] != em]
    save_json(CLIENTS_DB, db)

    # Remove from xray.json
    cfg = load_json(XRAY_CONFIG)
    cfg['inbounds'][0]['settings']['clients'] = [
        x for x in cfg['inbounds'][0]['settings']['clients'] if x['email'] != em
    ]
    save_json(XRAY_CONFIG, cfg)

    reload_xray()
    log.info(f" Deleted: {em}")

    await c.message.edit_text(f" {em} удален", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=' К списку', callback_data='clients_list')]]))
    await c.answer()

@dp.callback_query(F.data.startswith('revoke_'))
async def cb_revoke(c: CallbackQuery):
    if c.from_user.id != ADMIN_ID: return await c.answer('', show_alert=True)
    em = c.data.split('_', 1)[1]
    db = load_json(CLIENTS_DB)
    for item in db['clients']:
        if item['email'] == em: item['active'] = False; break
    save_json(CLIENTS_DB, db); reload_xray(); log.info(f" Revoked: {em}")
    await c.message.edit_text(f" {em} отозван", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=' К списку', callback_data='clients_list')]]))
    await c.answer()

@dp.callback_query(F.data.startswith('activate_'))
async def cb_activate(c: CallbackQuery):
    if c.from_user.id != ADMIN_ID: return await c.answer('', show_alert=True)
    em = c.data.split('_', 1)[1]
    db = load_json(CLIENTS_DB)
    for item in db['clients']:
        if item['email'] == em: item['active'] = True; break
    save_json(CLIENTS_DB, db); log.info(f" Activated: {em}")
    await cb_client(c)
    await c.answer()

@dp.callback_query(F.data == 'add_client')
async def cb_add_start(c: CallbackQuery):
    if c.from_user.id != ADMIN_ID: return await c.answer('', show_alert=True)
    # Show server selection
    servers = load_servers()
    kb = []
    for s in servers:
        if s.get('active', True):
            kb.append([InlineKeyboardButton(text=f" {s['name']} ({s['city']})", callback_data=f"add_srv_{s['name']}")])
    kb.append([InlineKeyboardButton(text=' Назад', callback_data='back_add')])
    await c.message.edit_text(" <b>Выбери сервер:</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode='HTML')
    await c.answer()

@dp.callback_query(F.data.startswith('add_srv_'))
async def cb_add_server(c: CallbackQuery):
    if c.from_user.id != ADMIN_ID: return await c.answer('', show_alert=True)
    server_name = c.data.replace('add_srv_', '')
    user_state[c.from_user.id] = {'action': 'add', 'email': None, 'server': server_name}
    await c.message.edit_text(f" <b>Новый клиент на {server_name}</b>\nВведи @username:", reply_markup=back_kb(), parse_mode='HTML')
    await c.answer()

@dp.callback_query(F.data == 'back_add')
async def cb_back_add(c: CallbackQuery):
    uid = c.from_user.id
    if uid in user_state: del user_state[uid]
    await cb_clients(c)
    await c.answer()

@dp.message(F.text)
async def handle_text(m: types.Message):
    uid = m.from_user.id
    if uid not in user_state: return
    st = user_state[uid]
    if st['action'] == 'add' and st['email'] is None:
        txt = m.text.strip()
        if not txt.startswith('@'): return await m.answer(" Введи @username")
        em = txt
        db = load_json(CLIENTS_DB)
        if any(item['email'] == em for item in db['clients']):
            await m.answer(f" {em} уже есть", reply_markup=back_kb())
            del user_state[uid]
            return
        nu = str(uuid.uuid4())
        db['clients'].append({'email': em, 'uuid': nu, 'limit': None, 'active': True, 'created': datetime.now().isoformat()})
        save_json(CLIENTS_DB, db)
        
        # Add to selected server
        server_name = st.get('server', 'WARSAW')
        ok, msg = add_client_to_server(server_name, nu, em)
        if ok:
            log.info(f" Created: {em} on {server_name}, unlimited")
            await m.answer(f" <b>{em} создан на {server_name}</b>\n```{gen_link(nu, em, server_name)}```\n<i>Отправь ссылку</i>",
                          parse_mode='HTML', reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                              [InlineKeyboardButton(text=' К списку', callback_data='clients_list')]]))
        else:
            await m.answer(f" Ошибка создания на {server_name}: {msg}", reply_markup=back_kb())
        del user_state[uid]
    else:
        await m.answer(" Нажми /start", reply_markup=main_kb())

async def main():
    log.info(" VPNDaemon Bot 2.0 started")

    # Start subscription server
    sub_runner = await start_subscription_server()

    # Start bot
    try:
        await dp.start_polling(bot)
    finally:
        await sub_runner.cleanup()

if __name__ == '__main__': asyncio.run(main())
