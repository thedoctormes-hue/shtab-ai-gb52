"""
Ночной аналитик.
Запускается по cron в 09:00 MSK (06:00 UTC).
Анализирует фрагменты за сутки через Gemini, ищет паттерны и шлёт сводку.
"""
import asyncio
import json
import logging
import os
from datetime import datetime, timedelta

import httpx

from app.database import get_all_user_ids, get_recent_fragments, upsert_pattern, get_user_by_id, get_last_fragment_date
from app.schemas_llm import PatternAnalysis

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
BOT_TOKEN = os.getenv("BOT_TOKEN")


async def call_gemini(fragments_text: str) -> list[dict]:
    """Вызов Gemini через OpenRouter для анализа паттернов."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    system_prompt = "Ты ночной аналитик личного дневника. Отвечай строго JSON."
    
    user_prompt = f"""Вот мысли пользователя за сутки:

{fragments_text}

Найди 1-3 повторяющихся темы или слепых пятна.
Не задачи. Не события. Именно паттерны мышления.

Ответь строго JSON без markdown:
[{{"description": "...", "is_new": true}}]
"""
    
    payload = {
        "model": "google/gemini-2.0-flash-001",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 500
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        
        data = response.json()
        content = data["choices"][0]["message"]["content"]

        # Убираем markdown обёртку если есть
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        raw_list = json.loads(content.strip())
        # Валидация каждого паттерна через Pydantic
        return [PatternAnalysis(**item).model_dump() for item in raw_list]


async def analyze_user(user_id: str) -> None:
    """Анализ паттернов для одного пользователя + уведомление."""
    from app.database import get_today_fragments, get_user_by_id

    # Получаем tg_id пользователя
    user = await get_user_by_id(user_id)
    if not user:
        logger.warning(f"User {user_id} not found")
        return

    tg_id = user.get("tg_id")
    if not tg_id:
        logger.warning(f"No tg_id for user {user_id}")
        return

    fragments = await get_recent_fragments(user_id)

    # Сводка по фрагментам
    today_count = len(fragments) if fragments else 0

    # Проверяем, не пропустил ли пользователь 3+ дней
    from app.database import get_last_fragment_date
    last_date = await get_last_fragment_date(user_id)

    message_lines = ["🌙 Ночной анализ Протокола\n"]

    if last_date:
        days_ago = (datetime.utcnow() - datetime.fromisoformat(last_date)).days
        if days_ago >= 3:
            message_lines.append(f"⚠️ Ты пропустил {days_ago} дн.\n")
            if fragments:
                message_lines.append(f"Последний: {fragments[0].get('summary', '')[:100]}...\n")

    if today_count == 0:
        message_lines.append("За сегодня записей нет. Жду твоих мыслей! 🧠")
    else:
        message_lines.append(f"За сутки: {today_count} фрагментов\n")

    # Анализируем паттерны
    if fragments:
        fragments_text = "\n---\n".join(
            f.get("summary") or f.get("text", "") for f in fragments
        )

        if fragments_text.strip():
            logger.info(f"Анализируем {len(fragments)} фрагментов для user {user_id}")

            try:
                patterns = await call_gemini(fragments_text)

                new_patterns = []
                for pattern in patterns:
                    desc = pattern.get("description", "")
                    is_new = pattern.get("is_new", True)
                    if desc:
                        await upsert_pattern(user_id, desc)
                        if is_new:
                            new_patterns.append(pattern)
                        logger.info(f"Сохранён паттерн: {desc[:50]}...")

                if new_patterns:
                    message_lines.append("\n🆕 Новые паттерны:")
                    for i, p in enumerate(new_patterns[:3], 1):
                        message_lines.append(f"{i}. {p.get('description', '')[:80]}")

            except Exception as e:
                logger.error(f"Ошибка при анализе для user {user_id}: {e}")

    # Отправляем сводку через бота
    final_message = "\n".join(message_lines)

    if BOT_TOKEN:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": tg_id,
                        "text": final_message,
                        "parse_mode": "HTML"
                    }
                )
                logger.info(f"Сводка отправлена user {user_id} (tg_id={tg_id})")
        except Exception as e:
            logger.error(f"Ошибка отправки сводки user {user_id}: {e}")
    else:
        logger.warning("BOT_TOKEN not set, cannot send notifications")


async def main() -> None:
    """Главная функция."""
    logger.info("Запуск ночного аналитика")
    
    user_ids = await get_all_user_ids()
    logger.info(f"Найдено {len(user_ids)} пользователей")
    
    for user_id in user_ids:
        await analyze_user(user_id)
    
    logger.info("Ночной аналитик завершён")


if __name__ == "__main__":
    asyncio.run(main())