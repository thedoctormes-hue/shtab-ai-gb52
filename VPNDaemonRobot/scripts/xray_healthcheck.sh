#!/bin/bash
# Xray Health Check + Auto-Failover

CONFIG_FILE="/usr/local/etc/xray/config.json"
PID_FILE="/var/run/xray.pid"
LOG_FILE="/root/LabDoctorM/VPNDaemonRobot/logs/xray-health.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Check if xray is running
if ! systemctl is-active --quiet demonvpn; then
    log "FAIL: demonvpn service not active"
    systemctl restart demonvpn
    exit 1
fi

# Check if port 10086 is listening
if ! ss -tlnp | grep -q ":10086"; then
    log "FAIL: Port 10086 not listening"
    systemctl restart demonvpn
    exit 1
fi

log "OK: Xray healthy"
exit 0
