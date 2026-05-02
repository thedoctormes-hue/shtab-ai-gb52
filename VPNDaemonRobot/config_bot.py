import asyncio
import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = "7593603158:AAHXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"  # Замени на реальный токен
bot = Bot(token=TOKEN)
dp = Dispatcher()

CONFIGS = {
    "vless": "vless://b831381d-6324-4d53-ad4f-8cda48b30811@185.138.90.150:10086?type=tcp&security=reality&sni=www.microsoft.com&fp=chrome&pbk=Q7P9aveiWcBmNYLcnP5b-HXMnnz7FUcpIfDZKk--elY&sid=a1b2c3d4&flow=xtls-rprx-vision#Warsaw-VLESS",
    "wg": "[Interface]\nPrivateKey = \nAddress = 10.0.0.2/32\nDNS = 1.1.1.1\n\n[Peer]\nPublicKey = \nEndpoint = 185.138.90.150:51820\nAllowedIPs = 0.0.0.0/0"
}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    text = """🤖 **Warsaw VPN Bot**

**Команды:**
/get_vless — VLESS+REALITY конфиг
/get_wg — WireGuard конфиг
/status — статус серверов

**Два способа обхода — один сервер:**
1. VLESS (XTLS-Vision)
2. WireGuard"""
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("get_vless"))
async def cmd_vless(message: types.Message):
    await message.answer(f"```\n{CONFIGS['vless']}\n```", parse_mode="Markdown")

@dp.message(Command("get_wg"))
async def cmd_wg(message: types.Message):
    await message.answer(f"```\n{CONFIGS['wg']}\n```", parse_mode="Markdown")

@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    await message.answer("📊 Warsaw: VLESS ✅ | WG ⏳ | 2 способа обхода")

async def main():
    print("VPN Config Bot started!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())