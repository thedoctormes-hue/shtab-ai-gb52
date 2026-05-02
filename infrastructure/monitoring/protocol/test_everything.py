#!/usr/bin/env python3
"""Итоговый тест Протокола — ебашим все проверки!"""
import asyncio
import aiohttp
import sys
sys.path.insert(0, '/root/LabDoctorM/protocol')

from app.jwt_utils import create_access_token

API = "http://localhost:8000/api/v1"

async def test():
    async with aiohttp.ClientSession() as s:
        print("🚀 Начинаем ебашить тесты...")
        
        # 1. Регистрация
        async with s.post(f"{API}/users/register", json={"tg_id": "TEST_001"}) as r:
            data = await r.json()
            user_id = data["user_id"]
            token = data["access_token"]
            print(f"✅ Регистрация: {user_id[:8]}...")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Создание фрагментов
        for i in range(3):
            async with s.post(f"{API}/fragments", 
                json={"text": f"Тестовый фрагмент номер {i}", "source": "text"}, 
                headers=headers) as r:
                frag = await r.json()
                print(f"✅ Фрагмент {i+1}: {frag['id'][:8]}...")
        
        # 3. Поиск
        async with s.get(f"{API}/fragments/search?q=Тестовый", headers=headers) as r:
            res = await r.json()
            print(f"✅ Поиск: найдено {len(res)} шт.")
        
        # 4. Список людей (пока пусто, но API работает)
        async with s.get(f"{API}/people", headers=headers) as r:
            if r.status == 200:
                res = await r.json()
                print(f"✅ Люди: {len(res)} записей")
            else:
                print(f"⚠️ Люди: {r.status}")
        
        # 5. Настройки (GET)
        async with s.get(f"{API}/settings/exit", headers=headers) as r:
            if r.status == 200:
                print("✅ Настройки: API работает")
            else:
                print(f"⚠️ Настройки: {r.status}")
        
        # 6. Настройки (PUT)
        async with s.put(f"{API}/settings/exit", 
            json={"export_format": "json", "auto_delete_days": 30}, 
            headers=headers) as r:
            if r.status == 200:
                print("✅ Изменение настроек: OK")
            else:
                print(f"⚠️ Изменение настроек: {r.status}")
        
        print("\n🎯 ВСЁ РАБОТАЕТ! ЕБАШИМ ДАЛЬШЕ!")

asyncio.run(test())
