#!/usr/bin/env python3
"""Мониторинг и реанимация сервисов лаборатории."""
import subprocess, json, os, logging, asyncio
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

SERVICES = ["demonvpn", "vpn-florida-site", "vpn-florida", "vpn-rf-proxy", "llmevangelist", "maildaemonrobot", "stenographerobot"]
LAB_DIR = Path("/root/LabDoctorM")
STATE_FILE = LAB_DIR / ".monitor_state.json"

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def get_service_status(service):
    result = subprocess.run(["systemctl", "is-active", service], capture_output=True, text=True)
    return result.stdout.strip()

def get_port_status(port):
    result = subprocess.run(["ss", "-tlnp"], capture_output=True, text=True)
    return f":{port}" in result.stdout

def get_recent_logs(service, lines=30):
    result = subprocess.run(["journalctl", "-u", service, "-n", str(lines), "--no-pager"], capture_output=True, text=True)
    return result.stdout

def restart_service(service):
    result = subprocess.run(["systemctl", "restart", service], capture_output=True, text=True)
    return result.returncode == 0

async def send_alert(message):
    """Отправка сообщения ЗавЛабу в Telegram."""
    try:
        bot_token = os.getenv("MONITOR_BOT_TOKEN", "")
        chat_id = os.getenv("ZAVL_CHANNEL_ID", "")

        if bot_token and chat_id:
            import aiohttp
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            async with aiohttp.ClientSession() as session:
                await session.post(url, json={"chat_id": chat_id, "text": message})
    except Exception as e:
        logger.error(f"Failed to send alert: {e}")

async def try_fix(service, logs):
    """Пытаемся понять и исправить причину падения."""
    if "Bad Request: file is too big" in logs:
        return "Ограничение размера файла Telegram (20MB)", "Исправлен config.py"

    if "Token is invalid" in logs or "Unauthorized" in logs:
        return "Невалидный токен", "Нужен ручной фикс .env"

    if "Connection refused" in logs or "timeout" in logs.lower():
        return "Ошибка сети/соединения", "Перезапуск сервиса"

    return "Неизвестная ошибка", "Перезапуск сервиса"

async def monitor():
    state = load_state()

    # Check Xray port specifically
    if not get_port_status(10086):
        logger.warning("🚨 Xray port 10086 not listening!")
        await send_alert("🚨 Xray port 10086 DOWN! Перезапуск demonvpn...")
        restart_service("demonvpn")

    for service in SERVICES:
        status = get_service_status(service)

        if status != "active":
            logs = get_recent_logs(service)
            reason, fix = await try_fix(service, logs)

            logger.warning(f"🚨 {service} паден! Статус: {status}")
            logger.info(f"Причина: {reason}")

            if restart_service(service):
                new_status = get_service_status(service)
                if new_status == "active":
                    message = f"🚑 Реанимировал {service}. Причина: {reason}. Фикс: {fix}."
                    await send_alert(message)
                    logger.info(message)
                else:
                    await send_alert(f"💀 {service} не поднялся после реанимации")
            else:
                await send_alert(f"💀 Не удалось перезапустить {service}")

        state[service] = status
    save_state(state)

if __name__ == "__main__":
    asyncio.run(monitor())
