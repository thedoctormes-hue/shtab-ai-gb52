import base64, asyncio, httpx, os, subprocess, logging, json
from typing import Optional, List
from . import config

logger = logging.getLogger(__name__)

async def _call_openrouter(
    model: str,
    messages: List[dict],
    timeout: float = 120.0
) -> Optional[str]:
    """Вспомогательная: один вызов к OpenRouter с обработкой ошибок."""
    headers = {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/LabDoctorM/stenographerobot",
        "X-Title": "Stenographerobot"
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 4000
    }
    logger.info(f"🌐 {model}: запрос...")
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(
                f"{config.OPENROUTER_BASE_URL}/chat/completions",
                headers=headers, json=payload
            )
            r.raise_for_status()
            data = r.json()
            result = data["choices"][0]["message"]["content"].strip()
            logger.info(f"✅ {model}: успех")
            return result
    except Exception as e:
        logger.error(f"❌ {model}: {e}")
        return None

async def transcribe_audio(
    file_path: str,
    system_prompt: str,
    audio_format: str = "ogg"
) -> Optional[str]:
    wav_path = file_path + ".conv.wav"
    final_path, final_format = file_path, audio_format.lower()

    try:
        logger.info(f"🔄 ffmpeg: {file_path} → {wav_path} (wav, 16kHz mono)")
        subprocess.run(
            ["ffmpeg", "-i", file_path, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", "-y", wav_path],
            check=True, capture_output=True
        )
        final_path, final_format = wav_path, "wav"
        logger.info("✅ ffmpeg OK")
    except Exception as e:
        logger.warning(f"⚠️ ffmpeg failed: {e}, пробую исходный формат")

    with open(final_path, "rb") as f:
        audio_data = base64.b64encode(f.read()).decode("utf-8")
    logger.info(f"📡 Base64: {len(audio_data)} символов, format={final_format}")

    messages = [
        {"role": "user", "content": [
            {"type": "input_audio", "input_audio": {"data": audio_data, "format": final_format}},
            {"type": "text", "text": system_prompt}
        ]}
    ]

    for model in config.ROLE_STT_MODELS:
        result = await _call_openrouter(model, messages)
        if result:
            if os.path.exists(wav_path):
                os.unlink(wav_path)
            return result

    if os.path.exists(wav_path):
        os.unlink(wav_path)
    return None

async def process_text(
    text: str,
    prompt: str,
    model_list: List[str] = None
) -> Optional[str]:
    if model_list is None:
        model_list = config.ROLE_CLEAN_MODELS

    messages = [
        {"role": "system", "content": "Отвечай строго по инструкции. Без маркдауна."},
        {"role": "user", "content": f"{prompt}\n\nТекст:\n---\n{text}"}
    ]

    for model in model_list:
        result = await _call_openrouter(model, messages)
        if result:
            return result
    return None
