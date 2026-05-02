#!/usr/bin/env python3
"""
🗂️ Migration Script v1.0
Анализ, миграция, валидация файловой системы
"""
import os
import json
import shutil
import argparse
from pathlib import Path

BASE_DIR = "/root/LabDoctorM"

PROJECTS_MAP = {
    # Telegram боты → projects/telegram-bots/
    'bot_keywords': ['bot', 'robot'],
    'telegram_bots_dir': '/root/LabDoctorM/projects/telegram-bots',
    
    # Web apps → projects/web-apps/
    'web_keywords': ['landing', 'dashboard', 'web', 'app'],
    'web_apps_dir': '/root/LabDoctorM/projects/web-apps',
    
    # Инфраструктура → infrastructure/
    'infra_keywords': ['vpn', 'monitor', 'proxy'],
    'infra_dir': '/root/LabDoctorM/infrastructure',
}

EXCLUDE = ['archive', 'venv', 'node_modules', '.git', '.lab', 'projects', '__pycache__']
MD_FILES = ['.md', '.MD']

def scan_current():
    """Сканирует текущую структуру"""
    chaos = []
    for item in Path(BASE_DIR).iterdir():
        if item.is_dir() and item.name not in EXCLUDE:
            chaos.append({
                'name': item.name,
                'path': str(item),
                'type': classify_project(str(item))
            })
    return chaos

def classify_project(path):
    """Классифицирует проект"""
    name_lower = Path(path).name.lower()
    
    for kw in PROJECTS_MAP['bot_keywords']:
        if kw in name_lower:
            return 'telegram-bot'
    
    for kw in PROJECTS_MAP['web_keywords']:
        if kw in name_lower:
            return 'web-app'
            
    for kw in PROJECTS_MAP['infra_keywords']:
        if kw in name_lower:
            return 'infrastructure'
    
    return 'unknown'

def move_to_standard(chaos):
    """Перемещает в стандартную структуру"""
    moves = []
    
    for item in chaos:
        old_path = Path(item['path'])
        if item['type'] == 'telegram-bot':
            new_path = Path(PROJECTS_MAP['telegram_bots_dir']) / old_path.name
        elif item['type'] == 'web-app':
            new_path = Path(PROJECTS_MAP['web_apps_dir']) / old_path.name
        elif item['type'] == 'infrastructure':
            new_path = Path(PROJECTS_MAP['infra_dir']) / old_path.name
        else:
            continue
        
        # Создаём целевую директорию
        new_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Перемещаем
        if not new_path.exists():
            shutil.move(str(old_path), str(new_path))
            moves.append(f"{old_path} → {new_path}")
    
    return moves

def validate():
    """Проверяет соответствие стандарту"""
    errors = []
    
    # Проверяем .md файлы в корне
    for item in Path(BASE_DIR).glob("*.md"):
        if item.name not in ['QWEN.md', 'README.md']:
            errors.append(f"MD файл в корне: {item}")
    
    return errors

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--scan', action='store_true', help='Scan current chaos')
    parser.add_argument('--move', action='store_true', help='Move to standard')
    parser.add_argument('--validate', action='store_true', help='Validate')
    
    args = parser.parse_args()
    
    if args.scan:
        chaos = scan_current()
        print("🔍 Найденный бардак:")
        for item in chaos:
            print(f"  {item['name']} → {item['type']}")
    
    if args.move:
        chaos = scan_current()
        moves = move_to_standard(chaos)
        print("✅ Перемещения:")
        for m in moves:
            print(f"  {m}")
    
    if args.validate:
        errors = validate()
        if errors:
            print("❌ Ошибки:")
            for e in errors:
                print(f"  {e}")
        else:
            print("✅ Стандарт соблюдён!")
