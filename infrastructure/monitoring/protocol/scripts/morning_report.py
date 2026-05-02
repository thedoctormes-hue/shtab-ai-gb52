#!/usr/bin/env python3
"""
🌅 Утренний отчёт для Протокола
— данные из SQLite (офлайн), красивый вывод, отправка в Telegram
"""
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import (
    get_all_user_ids,
    get_today_fragments,
    get_patterns,
    get_today_pattern,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
TG_ID = os.getenv("TG_ID")


def get_category(semantic_vector: str) -> str:
    """Извлечь категорию из semantic_vector JSON."""
    try:
        vector = json.loads(semantic_vector) if isinstance(semantic_vector, str) else semantic_vector
        if not vector:
            return "Знание"
        max_key = max(vector, key=vector.get)
        cat_map = {"task": "Задача", "idea": "Идея", "identity": "Я", "knowledge": "Знание", "pattern": "Паттерн"}
        return cat_map.get(max_key, "Знание")
    except Exception:
        return "Знание"


def format_date(created_at: str) -> str:
    """Формат даты ДД мм, ЧЧ:ММ."""
    try:
        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        return dt.strftime("%d %m, %H:%M")
    except Exception:
        return created_at


async def generate_morning_report(user_id: str) -> str:
    """Сформировать утренний отчёт."""
    today_str = datetime.utcnow().strftime("%d %B %Y")

    fragments = await get_today_fragments(user_id)
    patterns = await get_patterns(user_id)
    today_pattern = await get_today_pattern(user_id)

    category_counts = {}
    for frag in fragments:
        cat = get_category(frag["semantic_vector"])
        category_counts[cat] = category_counts.get(cat, 0) + 1

    sorted_fragments = sorted(
        fragments,
        key=lambda x: (x["weight"] or 1.0) * (x["confidence"] or 0.0),
        reverse=True
    )
    top3 = sorted_fragments[:3]

    report = []
    report.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    report.append("🌅 УТРЕННИЙ ОТЧЁТ | Протокол")
    report.append(f"📅 {today_str}")
    report.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    report.append("")
    report.append("📊 СТАТИСТИКА:")
    report.append(f"   Фрагментов за сутки: <b>{len(fragments)}</b>")
    report.append(f"   Паттернов всего: <b>{len(patterns)}</b>")
    report.append("")

    if category_counts:
        report.append("📌 КАТЕГОРИИ:")
        for cat, cnt in sorted(category_counts.items(), key=lambda x: -x[1]):
            report.append(f"   {cat} — {cnt}")
        report.append("")

    if top3:
        report.append("🎯 ГЛАВНОЕ СЕГОДНЯ:")
        for i, frag in enumerate(top3, 1):
            summary = frag["summary"] or frag["text"][:50] + "..."
            time_str = format_date(frag["created_at"]).split(",")[1].strip()
            report.append(f"   {i}. {summary} <i>({time_str})</i>")
        report.append("")

    if today_pattern:
        report.append("🔮 ПАТТЕРН ДНЯ:")
        report.append(f"   «{today_pattern['description']}»")
        report.append(f"   Встречается: {today_pattern['occurrences']} раз")
        report.append("")

    if len(fragments) > 5:
        report.append("📈 ТРЕНД: Активный день! Продолжай в том же духе.")
    elif fragments:
        report.append("📈 ТРЕНД: Норма. Можно больше думать.")
    else:
        report.append("📈 ТРЕНД: Пусто. Самое время начать.")

    report.append("")
    report.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    report.append("💡 /today — детали | /patterns — все паттерны")

    return "\n".join(report)


async def send_report():
    """Отправить отчёт в Telegram."""
    if not BOT_TOKEN or not TG_ID:
        print("❌ Установи BOT_TOKEN и TG_ID")
        return

    from aiogram import Bot
    from aiogram.enums import ParseMode

    bot = Bot(BOT_TOKEN, default=Bot.default(ParseMode.HTML))
    users = await get_all_user_ids()

    for user_id in users:
        try:
            report = await generate_morning_report(user_id)
            await bot.send_message(TG_ID, report, parse_mode=ParseMode.HTML)
            print(f"✅ Отчёт отправлен для {user_id}")
        except Exception as e:
            print(f"❌ Ошибка для {user_id}: {e}")

    await bot.session.close()


if __name__ == "__main__":
    asyncio.run(send_report())