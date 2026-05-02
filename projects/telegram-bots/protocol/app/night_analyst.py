"""
Ночной аналитик.
Запускается по cron в 03:00 MSK (00:00 UTC).
Анализирует фрагменты за сутки через Gemini и ищет паттерны.
"""
import asyncio
import json
import logging
import os

import httpx

from app.database import get_all_user_ids, get_recent_fragments, upsert_pattern

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


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
        
        return json.loads(content.strip())


async def analyze_user(user_id: str) -> None:
    """Анализ паттернов для одного пользователя."""
    fragments = await get_recent_fragments(user_id)
    
    if not fragments:
        logger.info(f"Нет фрагментов для user {user_id}")
        return
    
    # Собираем текст
    fragments_text = "\n---\n".join(
        f.get("summary") or f.get("text", "") for f in fragments
    )
    
    if not fragments_text.strip():
        logger.info(f"Нет текста для анализа для user {user_id}")
        return
    
    logger.info(f"Анализируем {len(fragments)} фрагментов для user {user_id}")
    
    try:
        patterns = await call_gemini(fragments_text)
        
        for pattern in patterns:
            desc = pattern.get("description", "")
            if desc:
                await upsert_pattern(user_id, desc)
                logger.info(f"Сохранён паттерн: {desc[:50]}...")
                
    except Exception as e:
        logger.error(f"Ошибка при анализе для user {user_id}: {e}")


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