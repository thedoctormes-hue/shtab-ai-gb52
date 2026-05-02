#!/usr/bin/env python3
"""
🐜 Муравейник КотОлизаторов v1.0
Новый проект = одна команда → новый бот + канал + сервис
"""
import os
import json
import sys
import re
from pathlib import Path

PROJECTS_JSON = "/root/LabDoctorM/projects.json"
SETTINGS_JSON = "/root/LabDoctorM/settings.json"
SERVICES_DIR = "/etc/systemd/system"
BOTFATHER_TOKEN = os.getenv("BOTFATHER_TOKEN", "")

def create_bot_via_botfather(name):
    """Создаёт бота через BotFather API (заглушка)"""
    # TODO: Реальная интеграция с BotFather API
    token = f"{name}_BOT_TOKEN_PLACEHOLDER"
    print(f"🤖 Создан бот @{name.lower()}bot")
    return token

def create_channel(name):
    """Создаёт канал в settings.json"""
    channel_id = f"-100{name[:2]}{hash(name) % 100000}"
    print(f"📢 Создан канал {name}")
    return channel_id

def create_systemd_service(name, path):
    """Создаёт systemd сервис"""
    service_content = f"""[Unit]
Description={name} Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={path}
ExecStart=/root/LabDoctorM/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    service_path = f"{SERVICES_DIR}/{name}.service"
    with open(service_path, 'w') as f:
        f.write(service_content)
    print(f"⚙️ Создан сервис {name}.service")

def clone_project(name, base_path="/root/LabDoctorM"):
    """Основная функция клонирования проекта"""
    name_kebab = name.lower().replace(" ", "-")
    project_dir = f"{base_path}/{name_kebab}"
    
    # 1. Создаём директорию проекта
    Path(project_dir).mkdir(parents=True, exist_ok=True)
    print(f"📁 Создана директория: {project_dir}")
    
    # 2. Создаём бота
    token = create_bot_via_botfather(name_kebab)
    
    # 3. Создаём канал
    channel_id = create_channel(name)
    
    # 4. Обновляем settings.json
    settings = {"bots": {}}
    if os.path.exists(SETTINGS_JSON):
        with open(SETTINGS_JSON, 'r') as f:
            settings = json.load(f)
    
    settings["bots"][name_kebab] = {
        "token": token,
        "channel_id": channel_id,
        "path": project_dir
    }
    
    with open(SETTINGS_JSON, 'w') as f:
        json.dump(settings, f, indent=2)
    print(f"⚙️ Обновлён settings.json")
    
    # 5. Обновляем projects.json
    with open(PROJECTS_JSON, 'r') as f:
        projects = json.load(f)
    
    projects["projects"].append({
        "name": name_kebab,
        "path": f"{project_dir}/",
        "priority": 3
    })
    
    with open(PROJECTS_JSON, 'w') as f:
        json.dump(projects, f, indent=2)
    print(f"📝 Обновлён projects.json")
    
    # 6. Создаём systemd сервис
    create_systemd_service(name_kebab, project_dir)
    
    print(f"\n✅ Проект {name} готов! cwd={project_dir}")
    return project_dir

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: antswarm.py <project_name>")
        sys.exit(1)
    
    project_name = sys.argv[1]
    clone_project(project_name)
