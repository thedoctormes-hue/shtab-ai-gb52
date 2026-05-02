#!/usr/bin/env python3
"""
Management API for RF Proxy (89.169.4.51)
Provides endpoints for managing the Xray whitelist proxy via SSH
Uses SSH key-based authentication (no passwords in memory)
"""

import os, json, subprocess, shlex
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

# Load .env
BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / '.env')

app = FastAPI(title="RF Proxy Management API", version="1.0")

# RF Proxy config - using SSH config aliases
RF_HOST = os.getenv('RF_PROXY_HOST', 'rf-proxy')
RF_IP = os.getenv('RF_PROXY_1_IP', '89.169.4.51')
RF_USER = os.getenv('RF_PROXY_1_SSH_USER', 'root')
RF_SSH_KEY = os.getenv('RF_PROXY_1_SSH_KEY', '/root/.ssh/rf_proxy_ed25519')
RF_CONFIG = os.getenv('RF_PROXY_1_XRAY_CONFIG', '/usr/local/etc/xray/config.json')

def ssh_exec(cmd, host=RF_HOST):
    """Execute command on RF proxy via SSH using key-based auth"""
    # Use ssh config host alias for isolation
    ssh_cmd = ["ssh", "-i", RF_SSH_KEY, "-o", "StrictHostKeyChecking=no", 
               "-o", "UserKnownHostsFile=/dev/null", f"{RF_USER}@{host}", cmd]
    try:
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=30)
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return None, str(e), -1

@app.get("/health")
async def health_check():
    """Check RF proxy health"""
    stdout, stderr, code = ssh_exec("systemctl is-active xray")
    is_active = stdout.strip() == "active"
    return {"status": "healthy" if is_active else "unhealthy", "xray_active": is_active}

@app.get("/config")
async def get_config():
    """Get Xray config from RF proxy"""
    stdout, stderr, code = ssh_exec(f"cat {RF_CONFIG}")
    if code != 0:
        raise HTTPException(status_code=500, detail=f"Failed to read config: {stderr}")
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON config")

@app.post("/reload")
async def reload_xray():
    """Reload Xray on RF proxy"""
    stdout, stderr, code = ssh_exec("systemctl reload-or-restart xray")
    if code != 0:
        raise HTTPException(status_code=500, detail=f"Failed to reload Xray: {stderr}")
    return {"status": "reloaded"}

@app.get("/stats")
async def get_stats():
    """Get Xray stats from RF proxy"""
    stdout, stderr, code = ssh_exec("/usr/local/bin/xray run -config /dev/null -test || true")
    return {"stats": stdout}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9001)
