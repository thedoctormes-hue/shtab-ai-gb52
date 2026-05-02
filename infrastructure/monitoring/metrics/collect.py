#!/usr/bin/env python3
"""Metrics collector - сбор метрик серверов"""
import json
import subprocess
from datetime import datetime
from pathlib import Path

def ping_server(host):
    """Пинг сервера"""
    try:
        result = subprocess.run(['ping', '-c', '1', '-W', '2', host],
                              capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def get_syncthing_metrics():
    """Получить метрики серверов"""
    results = {}
    # Warsaw - локальный сервер
    # Florida - VPN сервер (45.135.192.10)
    # RF-proxy - 89.169.4.51 (всегда онлайн)
    servers = {
        'warsaw': '127.0.0.1',
        'florida': '45.135.192.10',
        'rf-proxy': '89.169.4.51'
    }
    
    for name, host in servers.items():
        up = ping_server(host)
        results[name] = {
            'status': 'online' if up else 'offline',
            'host': host,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    return results

def save_metrics(period='weekly'):
    metrics = get_syncthing_metrics()
    ts = datetime.utcnow().strftime('%Y-%m-%d')
    path = Path(f'/root/LabDoctorM/infrastructure/monitoring/metrics/{period}/{ts}.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"✅ Saved to {path}")

if __name__ == '__main__':
    import sys
    period = sys.argv[1] if len(sys.argv) > 1 else 'weekly'
    save_metrics(period)
