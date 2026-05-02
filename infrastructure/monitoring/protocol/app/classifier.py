"""
Классификатор фрагментов памяти
Модель: Gemini 2.5 Flash через OpenRouter
Резерв: llama-3.3-70b:free
"""

import json
import os
import httpx
from app.config import settings
from app.schemas_llm import FragmentClassification

CLASSIFY_PROMPT = """Ты — классификатор фрагментов памяти для системы "Протокол".

Твоя задача: принять текстовый фрагмент и вернуть ТОЛЬКО валидный JSON без markdown, без пояснений, без преамбул.

Схема ответа:
{
  "semantic_vector": {
    "task": 0.0,
    "idea": 0.0,
    "identity": 0.0,
    "knowledge": 0.0,
    "pattern": 0.0
  },
  "emotion": {
    "positive": 0.0,
    "negative": 0.0,
    "neutral": 0.0
  },
  "three_interpretations": [
    "через призму роста: ...",
    "через призму защиты: ...",
    "через призму связи: ..."
  ],
  "conflict_detected": false,
  "unknown_type": false,
  "people": [],
  "tags": [],
  "summary": "одно предложение — суть фрагмента",
  "confidence": 0.0,
  "meta": {}
}

Правила:
- Все числа от 0.0 до 1.0
- Сумма semantic_vector не обязана быть 1.0 — независимые веса
- Сумма emotion должна быть 1.0
- people — имена людей упомянутых в тексте (массив строк)
- tags — 2-5 смысловых тегов на русском
- confidence — уверенность в классификации
- conflict_detected: true если есть противоречие или внутренний конфликт
- unknown_type: true если не понимаешь что это
- three_interpretations — на русском, 1-2 предложения каждая
- summary — строго одно предложение на русском
- ТОЛЬКО JSON. Никакого текста до или после."""


async def classify_fragment(text: str) -> dict:
    """
    Классифицирует фрагмент.
    Пробует primary модель, при ошибке — fallback.
    """
    for model in [settings.llm_primary, settings.llm_fallback]:
        try:
            result = await _call_openrouter(text, model)
            return result
        except Exception as e:
            print(f"[classifier] {model} failed: {e}, trying next...")

    # Если оба упали — возвращаем заглушку с unknown_type
    return _fallback_result(text)


async def _call_openrouter(text: str, model: str) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": CLASSIFY_PROMPT},
                    {"role": "user", "content": text},
                ],
                "temperature": 0.3,
                "max_tokens": 800,
            },
        )
        response.raise_for_status()
        raw = response.json()["choices"][0]["message"]["content"]
        clean = raw.strip().removeprefix("```json").removesuffix("```").strip()
        data = json.loads(clean)
        # Валидация через Pydantic
        return FragmentClassification(**data).model_dump()


def _fallback_result(text: str) -> dict:
    return {
        "semantic_vector": {"task": 0, "idea": 0, "identity": 0, "knowledge": 0, "pattern": 0},
        "emotion": {"positive": 0, "negative": 0, "neutral": 1.0},
        "three_interpretations": ["—", "—", "—"],
        "conflict_detected": False,
        "unknown_type": True,
        "people": [],
        "tags": [],
        "summary": "Классификация недоступна",
        "confidence": 0.0,
        "meta": {"error": "all_models_failed"},
    }


TRANSCRIBE_PROMPT = "Транскрибируй речь точно, без правок"


async def transcribe_audio(file_path: str, openrouter_api_key: str) -> str:
    """
    Транскрибирует аудиофайл через OpenRouter (google/gemini-2.0-flash-lite-001).
    """
    import base64
    import subprocess
    import logging
    import os

    logger = logging.getLogger(__name__)

    wav_path = os.path.splitext(file_path)[0] + "_converted.wav"
    try:
        # Конвертируем в wav 16kHz mono через ffmpeg (асинхронно)
        logger.info(f"[transcribe] converting {file_path} -> {wav_path}")
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg", "-i", file_path, "-ar", "16000", "-ac", "1", "-y", wav_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            logger.error(f"[transcribe] ffmpeg failed: {stderr.decode()}")
            raise RuntimeError("FFmpeg conversion failed")

        # Читаем и кодируем в base64
        with open(wav_path, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode()

        logger.info(f"[transcribe] audio encoded, size={len(audio_b64)}")

        # Отправляем на OpenRouter
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openrouter_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "google/gemini-2.0-flash-lite-001",
                    "messages": [
                        {"role": "system", "content": TRANSCRIBE_PROMPT},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Транскрибируй это аудио:"},
                                {
                                    "type": "input_audio",
                                    "input_audio": {
                                        "data": audio_b64,
                                        "format": "wav",
                                    },
                                },
                            ],
                        },
                    ],
                },
            )
            logger.info(f"[transcribe] openrouter response status={response.status_code}")
            response.raise_for_status()
            text = response.json()["choices"][0]["message"]["content"]
            logger.info(f"[transcribe] result: {text[:100]}...")
            return text.strip()
    except Exception as e:
        logger.error(f"[transcribe] error: {e}")
        raise
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)
