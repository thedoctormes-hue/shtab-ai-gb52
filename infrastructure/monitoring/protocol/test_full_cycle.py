#!/usr/bin/env python3
"""Быстрая проверка цикла: регистрация -> JWT -> фрагмент -> поиск"""
import asyncio
import aiohttp
import sys
from pathlib import Path
sys.path.insert(0, '/root/LabDoctorM/protocol')

# Загружаем .env вручную
env_path = Path('/root/LabDoctorM/protocol/.env')
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, _, value = line.partition('=')
                import os
                os.environ.setdefault(key.strip(), value.strip())

from app.jwt_utils import create_access_token

API = "http://localhost:8000/api/v1"
TG_ID = "999888777"

async def main():
    async with aiohttp.ClientSession() as s:
        # 1. Регистрация
        async with s.post(f"{API}/users/register", json={"tg_id": TG_ID}) as r:
            data = await r.json()
            user_id = data["user_id"]
            print(f"✅ User registered: {user_id}")

        # 2. Генерация JWT (внутренняя логика)
        token = create_access_token(tg_id=TG_ID, user_id=user_id)
        headers = {"Authorization": f"Bearer {token}"}
        print(f"✅ JWT created: {token[:20]}...")

        # 3. Создание фрагмента
        payload = {"text": "Тестовый фрагмент для проверки вайба!", "source": "text"}
        async with s.post(f"{API}/fragments", json=payload, headers=headers) as r:
            frag = await r.json()
            frag_id = frag["id"]
            print(f"✅ Fragment created: {frag_id}")

        # 4. Поиск
        async with s.get(f"{API}/fragments/search?q=вайб", headers=headers) as r:
            search_res = await r.json()
            # API может вернуть список или объект с 'results'
            count = len(search_res) if isinstance(search_res, list) else len(search_res.get('results', []))
            print(f"✅ Search result: {count} items")

        print("\n🚀 Protocol is fully operational!")

asyncio.run(main())
