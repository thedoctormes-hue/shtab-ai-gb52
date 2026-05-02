#!/bin/bash
# VPN Failover Healthcheck - Warsaw/Florida
# Проверка каждые 30s, переключение за 60s

WARSAW_IP="185.138.90.150"
FLORIDA_IP="104.253.1.210"
XRAY_PID_FILE="/var/run/xray.pid"
CONFIG_DIR="/root/LabDoctorM/projects/telegram-bots/vpn-daemon/vpnconfig"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> /var/log/vpn-failover.log; }

check_server() {
    local ip=$1
    local port=$2
    timeout 5 bash -c "echo > /dev/tcp/$ip/$port" 2>/dev/null
    return $?
}

get_active_config() {
    ps aux | grep -v grep | grep xray | grep -oP 'config\.json|\w+\.json' | head -1
}

switch_to_fallback() {
    log "FAIL: Warsaw недоступен, переключаю на Florida"
    systemctl reload xray-failover 2>/dev/null || true
    log "OK: Переключение завершено"
}

switch_to_primary() {
    log "OK: Warsaw восстановлен, возвращаю основной"
    systemctl reload xray-failover 2>/dev/null || true
}

# Основной цикл
COUNTER=0
while true; do
    COUNTER=$((COUNTER + 1))
    
    # Проверяем Warsaw
    if check_server $WARSAW_IP 443; then
        if [ $COUNTER -gt 3 ]; then
            switch_to_primary
            COUNTER=0
        fi
    else
        log "WARN: Warsaw timeout (attempt $COUNTER)"
        if [ $COUNTER -ge 2 ]; then
            switch_to_fallback
        fi
    fi
    
    sleep 30
done