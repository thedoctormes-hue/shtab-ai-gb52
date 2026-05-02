#!/usr/bin/env python3
"""OS Lab Dashboard API - порт 8002"""
import os
import subprocess

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Загружаем переменные окружения из .env
load_dotenv()

app = FastAPI(title="OS Lab Dashboard API", version="1.0.0")

# CORS origins из .env или по умолчанию
cors_origins_env = os.getenv('CORS_ORIGINS', 'http://185.138.90.150,http://localhost:5173')
cors_origins = [origin.strip() for origin in cors_origins_env.split(',')]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_methods=["*"], allow_headers=["*"]
)


def ping_server(host):
    """Пингует сервер и возвращает статус"""
    try:
        subprocess.run(['ping', '-c', '1', '-W', '2', host],
                      capture_output=True, check=True)
        return True
    except Exception:
        return False


def get_server_config():
    """Возвращает конфигурацию серверов из .env"""
    return {
        'warsaw': {
            'host': os.getenv('WARSAW_HOST', '127.0.0.1'),
            'syncthing': os.getenv('WARSAW_SYNCTHING', 'http://127.0.0.1:8384')
        },
        'florida': {
            'host': os.getenv('FLORIDA_HOST', '45.135.192.10'),
            'syncthing': os.getenv('FLORIDA_SYNCTHING', 'http://104.253.1.210:8384')
        },
        'rf-proxy': {
            'host': os.getenv('RF_PROXY_HOST', '89.169.4.51'),
            'syncthing': os.getenv('RF_PROXY_SYNCTHING', 'http://89.169.4.51:8384')
        }
    }


@app.get("/api/monitoring/servers")
async def get_servers():
    """Возвращает статус серверов"""
    servers = get_server_config()
    result = {}
    for name, cfg in servers.items():
        up = ping_server(cfg['host'])
        result[name] = {
            "cpu": 0,
            "ram": 0,
            "disk": 0,
            "ping": "OK" if up else "FAIL",
            "uptime": 0
        }
    return result


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8002)
