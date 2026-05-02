#!/usr/bin/env python3
# VPN Failover Healthcheck с таймаутом 60s

import subprocess
import time
import json
import os
from datetime import datetime

WARSAW = ("185.138.90.150", 443)
FLORIDA = ("104.253.1.210", 10086)
CHECK_INTERVAL = 30  # сек
MAX_FAILURES = 2     # 2 провала = 60s максимум

state = {"warsaw_down": False, "failures": 0}

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    with open('/var/log/vpn-failover.log', 'a') as f:
        f.write(line + '\n')

def check_tcp(ip, port, timeout=5):
    try:
        result = subprocess.run(
            ['timeout', str(timeout), 'nc', '-z', ip, str(port)],
            capture_output=True, timeout=timeout+1
        )
        return result.returncode == 0
    except:
        return False

def reload_xray():
    subprocess.run(['systemctl', 'reload', 'xray-failover'], capture_output=True)

def main():
    log("Failover healthcheck запущен (interval=30s, timeout=60s)")
    
    while True:
        warsaw_ok = check_tcp(*WARSAW)
        
        if warsaw_ok:
            if state["warsaw_down"]:
                log("OK: Warsaw восстановлен")
                state["warsaw_down"] = False
                state["failures"] = 0
                reload_xray()
        else:
            state["failures"] += 1
            log(f"FAIL: Warsaw недоступен (попытка {state['failures']})")
            
            if state["failures"] >= MAX_FAILURES and not state["warsaw_down"]:
                log("SWITCH: Переключаю трафик на Florida")
                state["warsaw_down"] = True
                reload_xray()
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()