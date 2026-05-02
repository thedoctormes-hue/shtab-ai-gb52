# 🔧 СПЕК: Устранение всех несоответствий (Pre-Sprint 3)

**Цель:** Привести код в идеальное состояние перед Спринтом 3.
**Дата:** 2026-04-28
**Статус:** 🚀 Готов к исполнению

---

## 1. Критические (P0) — СДЕЛАТЬ НЕМЕДЛЕННО

### 1.1 Блокирующий `subprocess.run` в `transcribe_audio`
**Файл:** `app/classifier.py`
**Суть:** Синхронный вызов `ffmpeg` вешает event loop бота.
**Решение:** Заменить на `asyncio.create_subprocess_exec`.

```python
# БЫЛО (classifier.py ~строка 89):
subprocess.run([
    "ffmpeg", "-i", ogg_path, "-ar", "16000", "-ac", "1", "-y", wav_path
], check=True, capture_output=True, text=True)

# СТАЛО:
proc = await asyncio.create_subprocess_exec(
    "ffmpeg", "-i", ogg_path, "-ar", "16000", "-ac", "1", "-y", wav_path,
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE
)
await proc.communicate()
if proc.returncode != 0:
    raise RuntimeError("FFmpeg conversion failed")
```

### 1.2 BOT_TOKEN в `QWEN.md`
**Файл:** `QWEN.md` (корень проекта)
**Суть:** Реальный токен бота `8671317159:AAEwWvWd0zmfAbqy1kAEoGXBlM8NMM0CUTo` записан в документацию.
**Решение:**
1. Отозвать токен через `@BotFather` в Telegram.
2. Сгенерировать новый.
3. Обновить `.env` и `QWEN.md` (заменить на заглушку).

```diff
# QWEN.md
- BOT_TOKEN=8671317159:AAEwWvWd0zmfAbqy1kAEoGXBlM8NMM0CUTo
+ BOT_TOKEN=<your-token>
```

---

## 2. Важные (P1) — Сделать до Спринта 3

### 2.1 Баг FTS5 (`fragment_id` и экранирование)
**Файл:** `app/database.py`
**Суть:** В `memory_fts` прописана колонка `fragment_id`, которой нет в `memory_fragments`. Плюс поисковый запрос не экранирует спецсимволы FTS5.
**Решение:**
1. Убрать `fragment_id` из определения FTS5 (используем external content mode корректно).
2. Добавить функцию экранирования для FTS5.

```python
# database.py - функция search_fragments
import re

def _escape_fts5(query: str) -> str:
    # Экранируем спецсимволы: ", ', (, ), *, AND, OR, NOT
    # Простой вариант: оборачиваем в кавычки если есть пробелы, иначе просто чистим
    if any(c in query for c in ['"', "'", '(', ')', '*', 'AND', 'OR', 'NOT']):
        return f'"{query.replace('"', '""')}"'
    return query

async def search_fragments(user_id: str, query: str, offset: int = 0):
    fts_query = _escape_fts5(query)
    # ... остальной код
```

### 2.2 Race Condition в `upsert_pattern`
**Файл:** `app/database.py`
**Суть:** Между SELECT и UPDATE/INSERT может вклиниться другой запрос.
**Решение:** Использовать SQLite `INSERT ... ON CONFLICT`.

```sql
-- Вместо поиска и апдейта, сразу:
INSERT INTO patterns (id, user_id, description, occurrences, ...)
VALUES (?, ?, ?, 1, ...)
ON CONFLICT(user_id, description) DO UPDATE SET occurrences = occurrences + 1, last_seen_at = excluded.last_seen_at;
```
*Нужно добавить UNIQUE constraint: `CREATE UNIQUE INDEX IF NOT EXISTS idx_patterns_user_desc ON patterns(user_id, description);`*

### 2.3 Дублирование JWT логики
**Файлы:** `bot/main.py` и `app/jwt_utils.py`
**Суть:** `make_jwt` в боте и `create_access_token` в app делают одно и то же, но могут разойтись.
**Решение:** Использовать `jwt_utils.create_access_token` везде.

```python
# bot/main.py
# Удалить:
# def make_jwt(tg_id: str) -> str: ...

# Импортировать:
from app.jwt_utils import create_access_token

# Использовать:
token = create_access_token(tg_id=str(message.from_user.id))
```

### 2.4 Нет Rate Limit на `/register`
**Файл:** `app/routers/users.py`
**Суть:** Можно флудить регистрацией.
**Решение:** Добавить декоратор лимитера.

```python
# users.py
from app.limiter import limiter

@router.post("/register")
@limiter.limit("10/minute")  # или меньше
async def register(...):
    ...
```

### 2.5 Валидация ответа LLM
**Файлы:** `app/classifier.py`, `app/night_analyst.py`
**Суть:** `json.loads` падает при кривом ответе.
**Решение:** Обернуть в try/except с fallback.

```python
try:
    data = json.loads(clean)
    # Проверка полей
    if "category" not in data: raise ValueError("No category")
except Exception as e:
    logging.error(f"LLM parse error: {e}")
    data = _fallback_result()
```

---

## 3. Рефакторинг (P2) — После Спринта 3

### 3.1 Разделить `handle_callbacks` в `bot/main.py`
**Задача:** Вынести логику из огромной функции (600+ строк) в отдельные хендлеры с фильтрами aiogram 3.x.

### 3.2 Убрать WIP артефакты
**Задача:** Найти и удалить все `:WIP` суффиксы в `callback_data` и мертвый код.

### 3.3 Централизовать `get_db`
**Задача:** Оставить одну функцию `get_db` в `app/deps.py` и использовать её везде (включая бота, передавая сессию или используя зависимости FastAPI).

---

## 4. Чеклист перед Спринтом 3 (Final Check)

- [ ] **P0.1** `asyncio.create_subprocess_exec` в `classifier.py` (тест: голосовое сообщение)
- [ ] **P0.2** Токен в `QWEN.md` заменен, новый в `.env`
- [ ] **P1.1** FTS5 поиск экранирует спецсимволы (тест: поиск с кавычками)
- [ ] **P1.2** `upsert_pattern` работает атомарно (тест: две параллельных вставки)
- [ ] **P1.3** JWT централизован через `jwt_utils`
- [ ] **P1.4** Регистрация лимитирована (`/register` 429 после 10 попыток)
- [ ] **P1.5** LLM ответы валидируются (тест: сломанный JSON)
- [ ] **Build** `pytest tests/ -v` проходит ✅
- [ ] **Deploy** `systemctl status protocol-bot` active ✅

---

**ЗавЛаб, как будешь готов — очищаем чат и погнали кодить Спринт 3!** 🚀
