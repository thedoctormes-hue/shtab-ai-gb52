import asyncio
import aiohttp
import json
import time
import socket
from datetime import datetime

CONFIGS_FILE = "/root/LabDoctorM/VPNDaemonRobot/honeynet_configs.json"

async def check_handshake(config):
    """Проверка работы VLESS+REALITY конфига"""
    if config.get('reality'):
        # REALITY handshake проверка через TCP соединение
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((config['server'], config['port']))
            # Если TCP соединение удалось - сервер жив
            sock.close()
            return True
        except:
            return False
    else:
        # Обычная HTTP проверка
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                url = f"https://{config['server']}:{config['port']}"
                async with session.get(url, ssl=False) as resp:
                    return True
        except:
            return False

async def monitor_configs():
    """Основной цикл мониторинга"""
    while True:
        try:
            with open(CONFIGS_FILE, 'r') as f:
                configs = json.load(f)

            for cfg in configs:
                alive = await check_handshake(cfg)
                cfg['last_check'] = time.time()
                cfg['alive'] = alive

                if alive:
                    cfg['success_count'] = cfg.get('success_count', 0) + 1
                else:
                    cfg['success_count'] = 0

                # Активный = 3+ успешных подряд
                cfg['active'] = cfg.get('success_count', 0) >= 3

            with open(CONFIGS_FILE, 'w') as f:
                json.dump(configs, f, indent=2)

            await asyncio.sleep(300)  # 5 минут
        except Exception as e:
            print(f"Monitor error: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(monitor_configs())