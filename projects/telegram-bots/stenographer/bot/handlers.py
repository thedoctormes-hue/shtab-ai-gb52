import os, tempfile, logging, datetime, aiohttp
from aiogram import Router, F, types
from core import config, api
from utils import files

logger = logging.getLogger(__name__)
router = Router()

def get_filename():
    return datetime.datetime.now().strftime("%d-%m-%Y_%H:%M") + ".txt"

async def download_file_custom(bot, file_path, dest_path, timeout=300):
    """Скачать файл с увеличенным таймаутом."""
    url = f"https://api.telegram.org/file/bot{bot.token}/{file_path}"
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
        async with session.get(url) as resp:
            resp.raise_for_status()
            with open(dest_path, "wb") as f:
                while True:
                    chunk = await resp.content.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
    return True

@router.message(F.command("start"))
async def cmd_start(message: types.Message):
    await message.answer("🎙️ Готов. Жду голосовое или файл (до 50 МБ).")

@router.message(F.voice | F.document | F.audio)
async def handle_audio(message: types.Message):
    # 1. Определяем файл и расширение
    if message.voice:
        file, ext = message.voice, ".ogg"
    elif message.audio:
        file = message.audio
        ext = os.path.splitext(getattr(file, "file_name", ""))[1].lower()
        if not ext: ext = ".m4a"
    elif message.document:
        file = message.document
        name = file.file_name or ""
        ext = os.path.splitext(name)[1].lower()
        if not ext or ext == ".bin": ext = ".m4a"
    else:
        return

    # 2. Проверка расширения
    allowed = {".ogg",".mp3",".wav",".m4a",".flac",".aac",".opus",".mp4"}
    if ext.lower() not in allowed:
        await message.answer(f"❌ '{ext}' не поддерживается."); return

    # 3. Скачивание и обработка
    file_info = await message.bot.get_file(file.file_id)
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp_path = tmp.name

        await message.answer("🔄 Скачиваю файл...")
        await download_file_custom(message.bot, file_info.file_path, tmp_path)
        logger.info(f"✅ Файл скачан: {tmp_path}")

        valid, error = files.check_file_size(tmp_path, config.MAX_FILE_SIZE)
        if not valid:
            await message.answer(f"❌ {error}"); return

        status = await message.answer("🔄 Обрабатываю...")

        # Step 1: Raw STT
        raw_transcript = await api.transcribe_audio(
            tmp_path, config.load_prompt("transcribe.txt"), audio_format=ext.lstrip(".")
        )
        if not raw_transcript:
            await status.edit_text("⚠️ Ошибка транскрибации."); return

        # Step 2: Clean text
        clean = await api.process_text(
            text=raw_transcript, prompt=config.load_prompt("clean.txt"), model_list=config.ROLE_CLEAN_MODELS
        )
        if not clean:
            await status.edit_text("⚠️ Ошибка очистки текста."); return

        # Step 3: Magic — протокол + задачи + рефлексия СРАЗУ
        summary = await api.process_text(
            text=clean, prompt=config.load_prompt("protocol.txt"), model_list=config.ROLE_PROTOCOL_MODELS
        )
        if not summary:
            await status.edit_text("⚠️ Ошибка генерации выводов."); return

        await status.delete()

        # Отправляем 2 файла магически
        clean_name = "Чистый текст " + get_filename()
        clean_path = f"/tmp/{clean_name}"
        with open(clean_path, "w", encoding="utf-8") as f:
            f.write(clean)

        summary_name = "Выводы " + get_filename()
        summary_path = f"/tmp/{summary_name}"
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary)

        await message.answer_document(types.FSInputFile(clean_path, filename=clean_name))
        await message.answer_document(types.FSInputFile(summary_path, filename=summary_name))

        os.unlink(clean_path)
        os.unlink(summary_path)

    except Exception as e:
        logger.error(f"❌ {e}", exc_info=True)
        await message.answer(f"⚠️ Ошибка обработки: {e}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)