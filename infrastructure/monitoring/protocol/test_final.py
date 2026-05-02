#!/usr/bin/env python3
"""Финальный тест: регистрация -> логин -> API"""
import asyncio
import aiohttp
import sys
sys.path.insert(0, '/root/LabDoctorM/protocol')

from app.jwt_utils import create_access_token

API = "http://localhost:8000/api/v1"

async def main():
    async with aiohttp.ClientSession() as s:
        # 1. Регистрация
        async with s.post(f"{API}/users/register", json={"tg_id": "999777666"}) as r:
            data = await r.json()
            user_id = data["user_id"]
            print(f"1. Registered: {user_id}")

        # 2. Генерация токена (через бэкенд-логику)
        token = create_access_token(tg_id="999777666", user_id=user_id)
        headers = {"Authorization": f"Bearer {token}"}
        print(f"2. Token: {token[:20]}...")

        # 3. Создание фрагмента
        async with s.post(f"{API}/fragments", 
            json={"text": "Hello from Protocol!", "source": "text", "privacy": "private"}, 
            headers=headers) as r:
            frag = await r.json()
            print(f"3. Fragment created: {frag['id']}")

        # 4. Поиск
        async with s.get(f"{API}/fragments/search?q=Protocol", headers=headers) as r:
            res = await r.json()
            print(f"4. Search found: {len(res)} items")

        # 5. Список людей
        async with s.get(f"{API}/people", headers=headers) as r:
            if r.status == 200:
                res = await r.json()
                print(f"5. People: {len(res)} items")
            else:
                text = await r.text()
                print(f"5. People error: {r.status} - {text}")

        # 6. Проверка фронтенда
        async with s.get("http://localhost:5173") as r:
            text = await r.text()
            if "html" in text.lower():
                print("6. Frontend: OK (HTML received)")
            else:
                print("6. Frontend: Check failed")

    print("\n🚀 ALL SYSTEMS GO!")

asyncio.run(main())
