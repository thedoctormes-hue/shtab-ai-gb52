import asyncio
import logging
import os
import tempfile
from datetime import datetime, timedelta
import jwt

import httpx
from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.classifier import transcribe_audio
from app.config import settings
from app.database import search_fragments, get_today_fragments, get_today_pattern, get_user_by_tg_id, get_patterns


# JWT helpers
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    logging.error("SECRET_KEY environment variable not set.")
    exit(1)


def make_jwt(tg_id: str) -> str:
    payload = {
        "tg_id": str(tg_id),
        "exp": datetime.utcnow() + timedelta(days=30),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# Configure logging
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()],
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger("app.classifier").setLevel(logging.INFO)

# Bot token from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_BASE_URL = "http://localhost:8000/api/v1"

if not BOT_TOKEN:
    logging.error("BOT_TOKEN environment variable not set.")
    exit(1)

# Initialize bot and dispatcher
bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
http_client = httpx.AsyncClient()


# FSM States for search
class SearchStates(StatesGroup):
    waiting_for_query = State()


async def on_shutdown():
    await http_client.aclose()


dp.shutdown.register(on_shutdown)


# Категории из semantic_vector
CATEGORY_MAP = {
    "task": "Задача",
    "idea": "Идея",
    "identity": "Я",
    "knowledge": "Знание",
    "pattern": "Паттерн"
}


def get_category(semantic_vector: str) -> str:
    """Извлечь категорию из semantic_vector JSON."""
    import json
    try:
        vector = json.loads(semantic_vector) if isinstance(semantic_vector, str) else semantic_vector
        if not vector:
            return "Знание"
        # Найти ключ с максимальным значением
        max_key = max(vector, key=vector.get)
        return CATEGORY_MAP.get(max_key, "Знание")
    except Exception:
        return "Знание"


def format_date(created_at: str) -> str:
    """Формат даты ДД мм, ЧЧ:ММ."""
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        return dt.strftime("%d %m, %H:%M")
    except Exception:
        return created_at


@dp.message(Command("search"))
async def cmd_search(message: types.Message, state: FSMContext):
    await state.set_state(SearchStates.waiting_for_query)
    await message.answer("Что ищем?")


@dp.message(Command("today"))
async def cmd_today(message: types.Message):
    tg_id = str(message.from_user.id)
    
    # Получаем user_id по tg_id
    user = await get_user_by_tg_id(tg_id)
    if not user:
        await message.answer("Сегодня пусто. Самое время надиктовать первую мысль.")
        return
    
    user_id = user["id"]
    fragments = await get_today_fragments(user_id)
    pattern = await get_today_pattern(user_id)
    
    if not fragments:
        await message.answer("Сегодня пусто. Самое время надиктовать первую мысль.")
        return
    
    # Дата сегодня
    from datetime import datetime
    today_str = datetime.utcnow().strftime("%d %B")
    
    # Группировка по категориям
    category_counts = {}
    for frag in fragments:
        cat = get_category(frag["semantic_vector"])
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    # Топ-3 по weight * confidence
    sorted_fragments = sorted(
        fragments,
        key=lambda x: (x["weight"] or 1.0) * (x["confidence"] or 0.0),
        reverse=True
    )
    top3 = sorted_fragments[:3]
    
    # Формируем ответ
    response = f"Сегодня, {today_str}\n\n"
    response += "Темы дня:\n"
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        response += f"{cat} ({count})\n"
    
    response += "\nГлавное:\n"
    for i, frag in enumerate(top3, 1):
        summary = frag["summary"] or "(без summary)"
        time_str = format_date(frag["created_at"]).split(",")[1].strip()
        response += f"{i}. {summary}  {time_str}\n"
    
    if pattern:
        response += f"\nПаттерн дня: {pattern['description']}"
    
    # Кнопки
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="Все фрагменты", callback_data="today_fragments"),
            types.InlineKeyboardButton(text="Паттерны", callback_data="today_patterns")
        ]
    ])
    
    await message.answer(response, reply_markup=keyboard)


@dp.message(Command("patterns"))
async def cmd_patterns(message: types.Message):
    tg_id = str(message.from_user.id)
    
    user = await get_user_by_tg_id(tg_id)
    if not user:
        await message.answer(
            "Паттерны ещё не найдены.\n"
            "Ночной аналитик начнёт работу после первых записей."
        )
        return
    
    user_id = user["id"]
    patterns = await get_patterns(user_id)
    
    if not patterns:
        await message.answer(
            "Паттерны ещё не найдены.\n"
            "Ночной аналитик начнёт работу после первых записей."
        )
        return
    
    response = "Твои паттерны:\n\n"
    
    for i, pat in enumerate(patterns, 1):
        desc = pat["description"]
        occ = pat["occurrences"]
        date_str = format_date(pat["last_seen_at"]).split(",")[0].strip()
        
        response += f"{i}. {desc}\n"
        response += f"   Замечен {occ} раз  {date_str}\n\n"
    
    response += "Следующий анализ: сегодня ночью"

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="Подробнее", callback_data="patterns_more"),
            types.InlineKeyboardButton(text="История", callback_data="patterns_history")
        ]
    ])

    await message.answer(response, reply_markup=keyboard)


@dp.message(SearchStates.waiting_for_query)
async def handle_search_query(message: types.Message, state: FSMContext):
    tg_id = str(message.from_user.id)
    query = message.text.strip()

    await state.clear()

    # Получаем user_id по tg_id
    user = await get_user_by_tg_id(tg_id)
    if not user:
        await message.answer("Пользователь не найден.")
        return
    user_id = user["id"]

    # Поиск фрагментов
    results = await search_fragments(user_id, query, offset=0)
    
    if not results:
        await message.answer(f"По запросу {query} ничего не найдено.")
        return
    
    # Форматирование результатов
    response_text = f"По запросу {query}:\n\n"
    
    for i, item in enumerate(results, 1):
        category = get_category(item["semantic_vector"])
        date_str = format_date(item["created_at"])
        summary = item["summary"] or "(без summary)"
        
        response_text += f"{i}. {summary}\n"
        response_text += f"   {category}  {date_str}\n\n"
    
    # Кнопки
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="Ещё", callback_data=f"search_more:{query}:3"),
            types.InlineKeyboardButton(text="Связать", callback_data="search_link:WIP"),
            types.InlineKeyboardButton(text="Удалить", callback_data="search_delete:WIP")
        ]
    ])
    
    await message.answer(response_text, reply_markup=keyboard)


@dp.callback_query()
async def handle_callbacks(callback: types.CallbackQuery):
    data = callback.data
    tg_id = str(callback.from_user.id)
    token = make_jwt(tg_id)
    headers = {"Authorization": f"Bearer {token}"}

    if data.startswith("search_more:"):
        # Формат: search_more:query:offset
        parts = data.split(":", 2)
        if len(parts) == 3:
            query = parts[1]
            offset = int(parts[2])

            results = await search_fragments(tg_id, query, offset)

            if not results:
                await callback.answer("Больше ничего не найдено", show_alert=True)
                return

            response_text = f"По запросу «{query}» (продолжение):\n\n"
            for i, item in enumerate(results, offset + 1):
                category = get_category(item["semantic_vector"])
                date_str = format_date(item["created_at"])
                summary = item["summary"] or "(без summary)"

                response_text += f"{i}. {summary}\n"
                response_text += f"   {category}  {date_str}\n\n"

            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [
                    types.InlineKeyboardButton(text="Ещё", callback_data=f"search_more:{query}:{offset + 3}"),
                    types.InlineKeyboardButton(text="Связать", callback_data=f"search_link:{results[0]['id']}"),
                    types.InlineKeyboardButton(text="Удалить", callback_data=f"search_delete:{results[0]['id']}")
                ]
            ])

            await callback.message.answer(response_text, reply_markup=keyboard)
            await callback.answer()

    elif data.startswith("search_link:"):
        # Формат: search_link:fragment_id
        fragment_id = data.split(":", 1)[1] if ":" in data else None
        if not fragment_id or fragment_id == "WIP":
            await callback.answer("Выбери фрагмент для связи", show_alert=True)
            return

        # Сохраняем в FSM состояние для выбора второго фрагмента
        await callback.message.answer(
            f"Фрагмент {fragment_id[:8]}... выбран.\n"
            "Теперь отправь ID второго фрагмента или нажми кнопку ниже для поиска.",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="Поиск фрагментов", callback_data=f"link_search:{fragment_id}")]
            ])
        )
        await callback.answer()

    elif data.startswith("link_search:"):
        # Показываем последние фрагменты для связи
        from app.database import get_recent_fragments
        user = await get_user_by_tg_id(tg_id)
        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return

        recent = await get_recent_fragments(user["id"])
        base_fragment_id = data.split(":", 1)[1]

        if not recent:
            await callback.answer("Нет недавних фрагментов", show_alert=True)
            return

        response = "Выбери фрагмент для связи:\n\n"
        keyboard_buttons = []

        for i, frag in enumerate(recent[:5], 1):
            summary = frag.get("summary", frag.get("text", ""))[:50]
            response += f"{i}. {summary}...\n"
            keyboard_buttons.append(
                [types.InlineKeyboardButton(
                    text=f"Связать с {i}",
                    callback_data=f"do_link:{base_fragment_id}:{frag.get('id', '')}"
                )]
            )

        await callback.message.answer(response, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons))
        await callback.answer()

    elif data.startswith("do_link:"):
        # Формат: do_link:from_id:to_id
        parts = data.split(":", 2)
        if len(parts) == 3:
            from_id, to_id = parts[1], parts[2]

            try:
                resp = await http_client.post(
                    f"{API_BASE_URL}/edges",
                    headers=headers,
                    json={"from_id": from_id, "to_id": to_id, "relation_type": "similar"},
                )
                resp.raise_for_status()
                await callback.answer("✅ Связь создана!", show_alert=True)
            except Exception as e:
                logging.error(f"Link error: {e}")
                await callback.answer("Ошибка создания связи", show_alert=True)
        else:
            await callback.answer("Ошибка", show_alert=True)

    elif data.startswith("search_delete:"):
        # Формат: search_delete:fragment_id
        fragment_id = data.split(":", 1)[1] if ":" in data else None
        if not fragment_id or fragment_id == "WIP":
            await callback.answer("Выбери фрагмент для удаления", show_alert=True)
            return

        try:
            response = await http_client.delete(
                f"{API_BASE_URL}/fragments/{fragment_id}",
                headers=headers
            )
            response.raise_for_status()
            await callback.answer("🗑 Фрагмент удалён", show_alert=True)
        except Exception as e:
            logging.error(f"Delete error: {e}")
            await callback.answer("Ошибка удаления", show_alert=True)

    elif data == "today_fragments:WIP" or data == "today_fragments":
        # Показать все фрагменты за сегодня
        user = await get_user_by_tg_id(tg_id)
        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return

        user_id = user["id"]
        fragments = await get_today_fragments(user_id)

        if not fragments:
            await callback.answer("Сегодня пусто", show_alert=True)
            return

        response = f"Сегодня записано {len(fragments)} фрагментов:\n\n"
        for i, frag in enumerate(fragments, 1):
            category = get_category(frag["semantic_vector"])
            time_str = format_date(frag["created_at"]).split(",")[1].strip()
            summary = frag["summary"] or "(без summary)"
            response += f"{i}. {summary}\n"
            response += f"   {category}  {time_str}\n\n"

        await callback.message.answer(response)
        await callback.answer()

    elif data == "today_patterns:WIP" or data == "today_patterns":
        # Показать паттерны за сегодня
        user = await get_user_by_tg_id(tg_id)
        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return

        user_id = user["id"]
        pattern = await get_today_pattern(user_id)

        if not pattern:
            await callback.answer("Паттернов за сегодня нет", show_alert=True)
            return

        response = f"Паттерн дня:\n\n{pattern['description']}\n\n"
        response += f"Замечен {pattern['occurrences']} раз(а)"

        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Подробнее", callback_data="patterns_more")]
        ])

        await callback.message.answer(response, reply_markup=keyboard)
        await callback.answer()

    elif data == "patterns_more" or data.startswith("patterns_more:"):
        # Показать все паттерны пользователя
        user = await get_user_by_tg_id(tg_id)
        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return

        user_id = user["id"]
        patterns = await get_patterns(user_id)

        if not patterns:
            await callback.answer("Паттернов нет", show_alert=True)
            return

        response = "Все твои паттерны:\n\n"
        for i, pat in enumerate(patterns, 1):
            desc = pat["description"]
            occ = pat["occurrences"]
            date_str = format_date(pat["last_seen_at"]).split(",")[0].strip()
            response += f"{i}. {desc}\n"
            response += f"   Замечен {occ} раз(а)  {date_str}\n\n"

        await callback.message.answer(response)
        await callback.answer()

    elif data == "patterns_history:WIP" or data == "patterns_history":
        # История паттернов (пока заглушка с общим списком)
        user = await get_user_by_tg_id(tg_id)
        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return

        user_id = user["id"]
        patterns = await get_patterns(user_id)

        if not patterns:
            await callback.answer("История пуста", show_alert=True)
            return

        response = "История паттернов:\n\n"
        for i, pat in enumerate(patterns, 1):
            desc = pat["description"]
            first = await get_pattern_first_seen(user_id, desc)
            response += f"{i}. {desc}\n"
            response += f"   Первый раз: {first}\n\n"

        await callback.message.answer(response)
        await callback.answer()

    else:
        await callback.answer("Неизвестная команда", show_alert=True)


@dp.message(Command("start"))
async def handle_start(message: types.Message):
    await message.answer("Что ты хочешь не забыть?")


@dp.message(F.text, ~Command("start"), ~Command("today"), ~Command("search"), ~Command("patterns"))
async def handle_text_messages(message: types.Message):
    user_id = message.from_user.id
    text = message.text

    try:
        token = make_jwt(str(user_id))
        headers = {"Authorization": f"Bearer {token}"}
        json_data = {"text": text}

        response = await http_client.post(f"{API_BASE_URL}/fragments", headers=headers, json=json_data)

        if response.status_code == 401:
            # User not registered, attempt to register
            await http_client.post(f"{API_BASE_URL}/users/register", json={"tg_id": str(user_id)})
            # Retry fragment creation after registration
            token = make_jwt(str(user_id))
            headers = {"Authorization": f"Bearer {token}"}
            response = await http_client.post(f"{API_BASE_URL}/fragments", headers=headers, json=json_data)

        response.raise_for_status()

        data = response.json()
        if data.get("magic_trigger"):
            await message.answer("Я заметил кое-что интересное. Хочешь узнать?")

    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error for user {user_id}: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        logging.error(f"Request error for user {user_id}: {e!r}")
    except Exception as e:
        logging.error(f"An unexpected error occurred for user {user_id}: {e}")


@dp.message(F.voice | F.audio)
async def handle_voice_messages(message: types.Message):
    user_id = message.from_user.id

    # Определяем тип файла (voice или audio)
    if message.voice:
        file = message.voice
    elif message.audio:
        file = message.audio
    else:
        return

    ogg_path = None
    wav_path = None

    try:
        # Скачиваем голосовое/аудио сообщение
        tg_file = await bot.get_file(file.file_id)

        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp_ogg:
            ogg_path = tmp_ogg.name
            await bot.download_file(tg_file.file_path, destination=tmp_ogg)

        # Транскрибируем
        text = await transcribe_audio(ogg_path, settings.openrouter_api_key)

        if not text:
            await message.answer("Не удалось распознать речь.")
            return

        # Отправляем на сохранение (аналогично текстовому сообщению)
        token = make_jwt(str(user_id))
        headers = {"Authorization": f"Bearer {token}"}
        json_data = {"text": text, "source": "voice"}

        logging.info(f"[voice] user={user_id}, text={text[:50]}...")

        response = await http_client.post(f"{API_BASE_URL}/fragments", headers=headers, json=json_data)

        if response.status_code == 401:
            logging.info(f"[voice] user={user_id} not registered, registering...")
            await http_client.post(f"{API_BASE_URL}/users/register", json={"tg_id": str(user_id)})
            token = make_jwt(str(user_id))
            headers = {"Authorization": f"Bearer {token}"}
            response = await http_client.post(f"{API_BASE_URL}/fragments", headers=headers, json=json_data)

        logging.info(f"[voice] response status={response.status_code}")
        response.raise_for_status()

        data = response.json()
        logging.info(f"[voice] fragment saved, id={data.get('id')}")
        if data.get("magic_trigger"):
            await message.answer("Я заметил кое-что интересное. Хочешь узнать?")
        else:
            await message.answer("Записано")

    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error for user {user_id}: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        logging.error(f"Request error for user {user_id}: {e!r}")
    except Exception as e:
        logging.error(f"An unexpected error occurred for user {user_id}: {e}")
    finally:
        # Удаляем временные файлы
        if ogg_path and os.path.exists(ogg_path):
            os.remove(ogg_path)
        if wav_path and os.path.exists(wav_path):
            os.remove(wav_path)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped by user.")
    except Exception as e:
        logging.error(f"Unhandled exception in main: {e}")