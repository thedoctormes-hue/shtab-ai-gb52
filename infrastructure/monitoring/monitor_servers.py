#!/usr/bin/env python3
import requests
import json

# Syncthing API на всех серверах
SERVICES = {
    'warsaw': {'url': 'http://127.0.0.1:8384', 'key': 'kFLqDXU49vvssvfmSWDnktCdYLrzuKZD'},
    'florida': {'url': 'http://104.253.1.210:8384', 'key': 'kFLqDXU49vvssvfmSWDnktCdYLrzuKZD'},
    'rf-proxy': {'url': 'http://89.169.4.51:8384', 'key': 'kFLqDXU49vvssvfmSWDnktCdYLrzuKZD'}
}

def get_metrics():
    results = {}
    for name, cfg in SERVICES.items():
        try:
            r = requests.get(f"{cfg['url']}/rest/system/status", 
                           headers={'X-API-Key': cfg['key']}, timeout=2)
            results[name] = r.json() if r.ok else {'error': str(r.status_code)}
        except Exception as e:
            results[name] = {'error': str(e)}
    return results

if __name__ == '__main__':
    print(json.dumps(get_metrics(), indent=2))