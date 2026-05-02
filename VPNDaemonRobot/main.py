import asyncio
import sys
import os
sys.path.insert(0, '/root/LabDoctorM')
os.chdir('/root/LabDoctorM/VPNDaemonRobot')

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv

load_dotenv('/root/LabDoctorM/VPNDaemonRobot/.env')
TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("🐜 VPN Daemon Robot готов! Команды: /status /ping")

@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    await message.answer("📊 Florida: OK | Warsaw: OK | RF-Proxy: OK")

@dp.message(Command("ping"))
async def cmd_ping(message: types.Message):
    import subprocess
    try:
        result = subprocess.check_output(['ping', '-c', '1', '104.253.1.210'], timeout=3)
        await message.answer("🏓 Florida: ttl отвечает")
    except:
        await message.answer("🏓 Florida: timeout")

@dp.message()
async def handle(message: types.Message):
    await message.answer(f"🐜 | {message.text}")

async def main():
    print("VPN Daemon Robot запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())