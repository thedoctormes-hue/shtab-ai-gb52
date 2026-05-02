"""Telegram bot for OpenClawBox."""

import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import (
    create_user, get_user, get_usage_stats, increment_usage,
    init_db
)

logging.basicConfig(level=logging.INFO)

TOKEN = "YOUR_TG_BOT_TOKEN"  # Set via env
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Provider status (mock, should be imported from app.router)
PROVIDERS = {
    "groq": {"limit": 300, "remaining": 250},
    "mistral": {"limit": 500000, "remaining": 450000},
    "google": {"limit": 15, "remaining": 8},
    "together": {"limit": 1000000, "remaining": 900000},
    "cohere": {"limit": 1000000, "remaining": 850000},
    "openrouter": {"limit": 500, "remaining": 300}
}


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user = get_user(message.from_user.id)
    if not user:
        api_key = create_user(message.from_user.id)
        await message.answer(
            f"👋 Добро пожаловать в OpenClawBox!\n\n"
            f"✅ Ваш API ключ: `{api_key}`\n\n"
            f"Отправляйте запросы на `/v1/chat/completions`\n"
            f"Лимит: 5000 токенов/сутки (freemium)",
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            f"👋 С возвращением!\n\n"
            f"Ваш API ключ: `{user.api_key}`\n"
            f"Тариф: {user.tier}\n\n"
            f"/key — показать ключ\n"
            f"/usage — расход\n"
            f"/providers — статус\n"
            f"/tier — тариф",
            parse_mode="Markdown"
        )


@dp.message(Command("key"))
async def cmd_key(message: types.Message):
    user = get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала /start")
        return
    
    await message.answer(
        f"🔑 Ваш API ключ:\n`{user.api_key}`",
        parse_mode="Markdown"
    )


@dp.message(Command("usage"))
async def cmd_usage(message: types.Message):
    user = get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала /start")
        return
    
    stats = get_usage_stats(message.from_user.id)
    
    # Warning threshold
    warning = ""
    if stats["percentage"] > 90:
        warning = "\n⚠️ ВНИМАНИЕ: приближаетесь к лимиту!"
    elif stats["percentage"] > 75:
        warning = "\n🔸 Осталось мало токенов"
    
    await message.answer(
        f"📊 Использование (сегодня):\n\n"
        f"Использовано: {stats['used_today']} токенов\n"
        f"Лимит: {stats['daily_limit']} токенов\n"
        f"Осталось: {stats['remaining']}\n"
        f"Процент: {stats['percentage']}%{warning}",
        parse_mode="Markdown"
    )


@dp.message(Command("providers"))
async def cmd_providers(message: types.Message):
    status_lines = ["🤖 Статус провайдеров:\n"]
    for name, data in PROVIDERS.items():
        remaining = data["remaining"]
        limit = data["limit"]
        pct = (remaining / limit) * 100 if limit > 0 else 0
        
        if pct > 50:
            emoji = "🟢"
        elif pct > 20:
            emoji = "🟡"
        else:
            emoji = "🔴"
        
        status_lines.append(f"{emoji} {name}: {remaining}/{limit}")
    
    await message.answer("\n".join(status_lines))


@dp.message(Command("tier"))
async def cmd_tier(message: types.Message):
    user = get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала /start")
        return
    
    tiers = {
        "freemium": "🆓 Freemium — ~5000 токенов/сутки",
        "premium": "💎 Premium — неограниченно ($9.99/мес)"
    }
    
    await message.answer(
        f"💎 Ваш тариф: {tiers.get(user.tier, user.tier)}\n\n"
        f"Используйте /upgrade для повышения"
    )


@dp.message(F.text.startswith("/"))
async def unknown_command(message: types.Message):
    await message.answer("❓ Неизвестная команда. Доступно: /start /key /usage /providers /tier")


async def check_thresholds():
    """Background task to check user limits."""
    while True:
        await asyncio.sleep(3600)  # Check every hour


async def main():
    # Create tables
    init_db()
    
    # Start polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())