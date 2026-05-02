import asyncio
import logging
import os
import tempfile
from datetime import datetime, timedelta

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
from app.jwt_utils import create_access_token

# Configure logging
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()],
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger("app.classifier").setLevel(logging.INFO)

# Bot token from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", settings.api_base_url) # Читаем из .env, дефолт из settings

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
    
    # Кнопки (используем ID первого фрагмента из результатов)
    first_frag_id = results[0]['id'] if results else None
    keyboard_buttons = [
        types.InlineKeyboardButton(text="Ещё", callback_data=f"search_more:{query}:3")
    ]
    if first_frag_id:
        keyboard_buttons.append(types.InlineKeyboardButton(text="Связать", callback_data=f"search_link:{first_frag_id}"))
        keyboard_buttons.append(types.InlineKeyboardButton(text="Удалить", callback_data=f"search_delete:{first_frag_id}"))

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[keyboard_buttons])
    
    await message.answer(response_text, reply_markup=keyboard)


# ── Callback handlers (refactored) ──────────────────────────

def _get_auth(callback: types.CallbackQuery):
    """Вспомогательная: получить tg_id, token и headers."""
    tg_id = str(callback.from_user.id)
    token = create_access_token(tg_id)
    headers = {"Authorization": f"Bearer {token}"}
    return tg_id, token, headers


@dp.callback_query(F.data.startswith("search_more:"))
async def cb_search_more(callback: types.CallbackQuery):
    tg_id, _, headers = _get_auth(callback)
    parts = callback.data.split(":", 2)
    if len(parts) != 3:
        await callback.answer("Неверный формат", show_alert=True)
        return

    query, offset = parts[1], int(parts[2])
    user = await get_user_by_tg_id(tg_id)
    if not user:
        await callback.answer("Пользователь не найден", show_alert=True)
        return

    results = await search_fragments(user["id"], query, offset)
    if not results:
        await callback.answer("Больше ничего не найдено", show_alert=True)
        return

    response_text = f"По запросу «{query}» (продолжение):\n\n"
    for i, item in enumerate(results, offset + 1):
        category = get_category(item["semantic_vector"])
        date_str = format_date(item["created_at"])
        summary = item["summary"] or "(без summary)"
        response_text += f"{i}. {summary}\n   {category}  {date_str}\n\n"

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="Ещё", callback_data=f"search_more:{query}:{offset + 3}"),
            types.InlineKeyboardButton(text="Связать", callback_data=f"search_link:{results[0]['id']}"),
            types.InlineKeyboardButton(text="Удалить", callback_data=f"search_delete:{results[0]['id']}")
        ]
    ])
    await callback.message.answer(response_text, reply_markup=keyboard)
    await callback.answer()


@dp.callback_query(F.data.startswith("search_link:"))
async def cb_search_link(callback: types.CallbackQuery):
    tg_id, _, _ = _get_auth(callback)
    fragment_id = callback.data.split(":", 1)[1] if ":" in callback.data else None
    if not fragment_id:
        await callback.answer("Выбери фрагмент для связи", show_alert=True)
        return

    await callback.message.answer(
        f"Фрагмент {fragment_id[:8]}... выбран.\nТеперь нажми кнопку для поиска.",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Поиск фрагментов", callback_data=f"link_search:{fragment_id}")]
        ])
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("link_search:"))
async def cb_link_search(callback: types.CallbackQuery):
    tg_id, _, _ = _get_auth(callback)
    from app.database import get_recent_fragments
    user = await get_user_by_tg_id(tg_id)
    if not user:
        await callback.answer("Пользователь не найден", show_alert=True)
        return

    base_fragment_id = callback.data.split(":", 1)[1]
    recent = await get_recent_fragments(user["id"])
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


@dp.callback_query(F.data.startswith("do_link:"))
async def cb_do_link(callback: types.CallbackQuery):
    tg_id, _, headers = _get_auth(callback)
    parts = callback.data.split(":", 2)
    if len(parts) != 3:
        await callback.answer("Ошибка", show_alert=True)
        return

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


@dp.callback_query(F.data.startswith("search_delete:"))
async def cb_search_delete(callback: types.CallbackQuery):
    tg_id, _, headers = _get_auth(callback)
    fragment_id = callback.data.split(":", 1)[1] if ":" in callback.data else None
    if not fragment_id:
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


@dp.callback_query(F.data == "today_fragments")
async def cb_today_fragments(callback: types.CallbackQuery):
    tg_id, _, _ = _get_auth(callback)
    user = await get_user_by_tg_id(tg_id)
    if not user:
        await callback.answer("Пользователь не найден", show_alert=True)
        return

    fragments = await get_today_fragments(user["id"])
    if not fragments:
        await callback.answer("Сегодня пусто", show_alert=True)
        return

    response = f"Сегодня записано {len(fragments)} фрагментов:\n\n"
    for i, frag in enumerate(fragments, 1):
        category = get_category(frag["semantic_vector"])
        time_str = format_date(frag["created_at"]).split(",")[1].strip()
        summary = frag["summary"] or "(без summary)"
        response += f"{i}. {summary}\n   {category}  {time_str}\n\n"

    await callback.message.answer(response)
    await callback.answer()


@dp.callback_query(F.data == "today_patterns")
async def cb_today_patterns(callback: types.CallbackQuery):
    tg_id, _, _ = _get_auth(callback)
    user = await get_user_by_tg_id(tg_id)
    if not user:
        await callback.answer("Пользователь не найден", show_alert=True)
        return

    pattern = await get_today_pattern(user["id"])
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


@dp.callback_query(F.data == "patterns_more")
async def cb_patterns_more(callback: types.CallbackQuery):
    tg_id, _, _ = _get_auth(callback)
    user = await get_user_by_tg_id(tg_id)
    if not user:
        await callback.answer("Пользователь не найден", show_alert=True)
        return

    patterns = await get_patterns(user["id"])
    if not patterns:
        await callback.answer("Паттернов нет", show_alert=True)
        return

    response = "Все твои паттерны:\n\n"
    for i, pat in enumerate(patterns, 1):
        desc = pat["description"]
        occ = pat["occurrences"]
        date_str = format_date(pat["last_seen_at"]).split(",")[0].strip()
        response += f"{i}. {desc}\n   Замечен {occ} раз(а)  {date_str}\n\n"

    await callback.message.answer(response)
    await callback.answer()


@dp.callback_query(F.data == "patterns_history")
async def cb_patterns_history(callback: types.CallbackQuery):
    tg_id, _, _ = _get_auth(callback)
    user = await get_user_by_tg_id(tg_id)
    if not user:
        await callback.answer("Пользователь не найден", show_alert=True)
        return

    patterns = await get_patterns(user["id"])
    if not patterns:
        await callback.answer("История пуста", show_alert=True)
        return

    response = "История паттернов:\n\n"
    for i, pat in enumerate(patterns, 1):
        desc = pat["description"]
        first = await get_pattern_first_seen(user["id"], desc)
        response += f"{i}. {desc}\n   Первый раз: {first}\n\n"

    await callback.message.answer(response)
    await callback.answer()


@dp.callback_query(F.data == "go_patterns")
async def cb_go_patterns(callback: types.CallbackQuery):
    """Переход к паттернам после онбординга."""
    await callback.message.answer(
        "Твои паттерны мышления: /patterns\n\n"
        "Паттерны — это повторяющиеся темы и слепые пятна."
    )
    await callback.answer()


@dp.message(Command("start"))
async def handle_start(message: types.Message):
    tg_id = str(message.from_user.id)
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="/today"), types.KeyboardButton(text="/patterns")],
            [types.KeyboardButton(text="/search"), types.KeyboardButton(text="/settings")],
        ],
        resize_keyboard=True
    )

    # Проверяем, есть ли юзер
    user = await get_user_by_tg_id(tg_id)

    if not user:
        # Онбординг: Шаг 1
        await message.answer(
            "Привет! Я Протокол — твоя вторая память. 🧠\n\n"
            "Я запомню твою первую мысль.\n"
            "Просто напиши её сейчас или надиктуй голосом:",
            reply_markup=keyboard
        )
    else:
        await message.answer(
            "С возвращением! Я Протокол — твоя вторая память.\n\n"
            "Команды:\n"
            "/today — фрагменты за сегодня\n"
            "/patterns — паттерны мышления\n"
            "/search — поиск мыслей\n"
            "/settings — настройки",
            reply_markup=keyboard
        )


@dp.message(F.text, ~Command("start"), ~Command("today"), ~Command("search"), ~Command("patterns"))
async def handle_text_messages(message: types.Message):
    user_id = message.from_user.id
    text = message.text

    try:
        token = create_access_token(str(user_id))
        headers = {"Authorization": f"Bearer {token}"}
        json_data = {"text": text}

        response = await http_client.post(f"{API_BASE_URL}/fragments", headers=headers, json=json_data)

        if response.status_code == 401:
            # User not registered, attempt to register
            await http_client.post(f"{API_BASE_URL}/users/register", json={"tg_id": str(user_id)})
            # Retry fragment creation after registration
            token = create_access_token(str(user_id))
            headers = {"Authorization": f"Bearer {token}"}
            response = await http_client.post(f"{API_BASE_URL}/fragments", headers=headers, json=json_data)

        response.raise_for_status()

        data = response.json()

        # Онбординг: проверяем количество фрагментов
        try:
            count_resp = await http_client.get(f"{API_BASE_URL}/fragments?limit=1&count_only=true", headers=headers)
            total = count_resp.json().get("total", 0) if count_resp.status_code == 200 else 0
        except Exception:
            total = 0

        # Шаг 2: После 1-го фрагмента
        if total == 1:
            await message.answer(
                "✅ Круто! Первая мысль сохранена.\n\n"
                "Теперь запиши голосом (нажми на микрофон в Telegram)\n"
                "— я умею распознавать аудио!"
            )
        # Шаг 3: После 3-х фрагментов
        elif total == 3:
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="Смотреть паттерны", callback_data="go_patterns")]
            ])
            await message.answer(
                "🔥 Ты в деле! Уже 3 фрагмента.\n\n"
                "Смотри свои паттерны мышления:",
                reply_markup=keyboard
            )

        if data.get("magic_trigger"):
            await message.answer("Я заметил кое-что интересное. Хочешь узнать?")

    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error for user {user_id}: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        logging.error(f"Request error for user {user_id}: {e!r}")
    except Exception as e:
        logging.error(f"An unexpected error occurred for user {user_id}: {e}")


@dp.message(Command("settings"))
async def cmd_settings(message: types.Message):
    tg_id = str(message.from_user.id)
    token = create_access_token(tg_id)
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{API_BASE_URL}/settings/exit", headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                text = "Твои настройки:\n"
                text += f"Формат экспорта: {data.get('export_format', 'bundle')}\n"
                text += f"Авто-удаление (дней): {data.get('auto_delete_days', 90)}\n"
                text += f"Доверенный ID: {data.get('trusted_tg_id', 'не задан')}\n"
                # Inline keyboard for editing
                keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                    [types.InlineKeyboardButton(text="Сменить формат", callback_data="settings_format")],
                    [types.InlineKeyboardButton(text="Авто-удаление", callback_data="settings_autodelete")],
                ])
                await message.answer(text, reply_markup=keyboard)
            else:
                await message.answer("Ошибка получения настроек")
    except Exception as e:
        logging.error(f"Settings error: {e}")
        await message.answer("Ошибка настроек")

@dp.callback_query(F.data.startswith("settings_"))
async def cb_settings(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]
    tg_id = str(callback.from_user.id)
    token = create_access_token(tg_id)
    headers = {"Authorization": f"Bearer {token}"}
    
    if action == "format":
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Bundle", callback_data="set_format:bundle")],
            [types.InlineKeyboardButton(text="JSON", callback_data="set_format:json")],
            [types.InlineKeyboardButton(text="TXT", callback_data="set_format:txt")],
        ])
        await callback.message.answer("Выбери формат экспорта:", reply_markup=keyboard)
    elif action == "autodelete":
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Никогда", callback_data="set_autodelete:never")],
            [types.InlineKeyboardButton(text="30 дней", callback_data="set_autodelete:30d")],
            [types.InlineKeyboardButton(text="90 дней", callback_data="set_autodelete:90d")],
            [types.InlineKeyboardButton(text="1 год", callback_data="set_autodelete:1y")],
        ])
        await callback.message.answer("Выбери срок авто-удаления:", reply_markup=keyboard)
    else:
        await callback.answer("Неизвестное действие")
    await callback.answer()

@dp.callback_query(F.data.startswith("set_format:"))
async def cb_set_format(callback: types.CallbackQuery):
    tg_id = str(callback.from_user.id)
    token = create_access_token(tg_id)
    headers = {"Authorization": f"Bearer {token}"}
    fmt = callback.data.split(":")[1]
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.put(f"{API_BASE_URL}/settings/exit", 
                                 headers=headers, 
                                 json={"export_format": fmt})
            if resp.status_code == 200:
                await callback.answer(f"Формат изменён на {fmt}")
            else:
                await callback.answer("Ошибка сохранения")
    except Exception as e:
        logging.error(f"Set format error: {e}")
        await callback.answer("Ошибка")
    await callback.answer()

@dp.callback_query(F.data.startswith("set_autodelete:"))
async def cb_set_autodelete(callback: types.CallbackQuery):
    tg_id = str(callback.from_user.id)
    token = create_access_token(tg_id)
    headers = {"Authorization": f"Bearer {token}"}
    value = callback.data.split(":")[1]
    # Convert to days
    days_map = {"never": 0, "30d": 30, "90d": 90, "1y": 365}
    days = days_map.get(value, 90)
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.put(f"{API_BASE_URL}/settings/exit", 
                                 headers=headers, 
                                 json={"auto_delete_days": days})
            if resp.status_code == 200:
                await callback.answer(f"Авто-удаление изменено")
            else:
                await callback.answer("Ошибка сохранения")
    except Exception as e:
        logging.error(f"Set autodelete error: {e}")
        await callback.answer("Ошибка")
    await callback.answer()

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
        token = create_access_token(str(user_id))
        headers = {"Authorization": f"Bearer {token}"}
        json_data = {"text": text, "source": "voice"}

        logging.info(f"[voice] user={user_id}, text={text[:50]}...")

        response = await http_client.post(f"{API_BASE_URL}/fragments", headers=headers, json=json_data)

        if response.status_code == 401:
            logging.info(f"[voice] user={user_id} not registered, registering...")
            await http_client.post(f"{API_BASE_URL}/users/register", json={"tg_id": str(user_id)})
            token = create_access_token(str(user_id))
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