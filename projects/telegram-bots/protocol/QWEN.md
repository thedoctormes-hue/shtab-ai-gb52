# Protocol — Система личной памяти

## Обзор
База: /root/protocol/
Тип: Система личной памяти с ИИ-классификацией и Telegram-интерфейсом. Позволяет сохранять мысли (текст/голос), классифицировать через LLM, искать по FTS5, выявлять повторяющиеся паттерны мышления.

**Статус:** Спринт 2 ЗАВЕРШЁН ✅, готовы к Спринту 3

## Стек
- Backend: FastAPI 0.115.0 + Uvicorn
- Bot: aiogram 3.x
- DB: SQLite 3 + FTS5
- LLM: OpenRouter (Gemini 2.5 Flash / Llama 3.3 70B)
- Транскрибация: Gemini 2.0 Flash Lite + ffmpeg
- Auth: JWT (HS256, 30 дней)

## Файлы
### Основные
- `main.py` — точка входа FastAPI, CORS, rate limiter
- `bot/main.py` — Telegram-бот (@Protocolstandbot), **ВСЕ кнопки активны ✅**
- `app/database.py` — работа с SQLite (FTS5, схема БД), включая `get_people_edges`
- `app/classifier.py` — классификация фрагментов и транскрибация аудио
- `app/night_analyst.py` — ночной анализ паттернов (cron 00:00 UTC)
- `app/people.py` — извлечение и сохранение упомянутых людей

### Новые файлы (Спринт 2 ✅)
- `app/routers/edges.py` — **NEW:** CRUD для memory_edges
- `app/routers/settings.py` — **NEW:** API для exit_settings
- `tests/test_new_features.py` — **NEW:** 7 тестов (pytest)

### Конфигурация
- `requirements.txt` — Python-зависимости
- `.env` — переменные окружения (НОВЫЙ SECRET_KEY!)
- `backup_db.sh` — скрипт ежедневного бэкапа БД
- `/etc/logrotate.d/protocol` — ротация логов

## Деплой
Сервисы systemd в `/etc/systemd/system/`:
1. `protocol.service` — FastAPI (порт 8000)
2. `protocol-bot.service` — Telegram-бот (зависит от protocol.service)
3. `protocol-analyst.service` + `protocol-analyst.timer` — ночной анализ (запуск 00:00 UTC)

Команды управления:
- `systemctl restart protocol-bot` — перезапуск бота
- `journalctl -u protocol-bot -f` — логи бота
- `systemctl list-timers` — проверка таймера аналитика

## Тестирование
```bash
cd /root/protocol
/root/LabDoctorM/venv/bin/pytest tests/ -v
```
- ✅ 7 тестов в `tests/test_new_features.py` проходят успешно
- Покрытие: структура API, схемы, health check
- Зависимости для тестов: `pytest`, `pytest-asyncio`, `httpx`

## Спринт 2 ЗАВЕРШЁН ✅
### Что сделано:
1. **API для memory_edges** — `app/routers/edges.py` (CRUD)
2. **API для exit_settings** — `app/routers/settings.py`
3. **Все кнопки бота активны:**
   - «Все фрагменты» — показывает фрагменты за сегодня
   - «Паттерны» — паттерн дня
   - «Подробнее» — все паттерны
   - «История» — история паттернов
   - «Связать» — создание связей между фрагментами
   - «Удалить» — удаление фрагментов
4. **Чтение people_edges** добавлено в `database.py`
5. **Тесты** — 7 тестов (pytest + pytest-asyncio)

## План Спринта 3: «Полировка и фронтенд»
**Цель:** Довести проект до production-ready состояния.

| Задача | Где | Приоритет |
|--------|-----|------|
| UI настроек в боте | `bot/main.py` | Высокий |
| Просмотр people_edges | `bot/main.py`, API | Средний |
| Фильтрация по privacy | `app/routers/fragments.py` | Средний |
| Фронтенд (React) | Новая папка `frontend/` | Высокий |
| Улучшение UX кнопок | `bot/main.py` | Низкий |
| Интеграционные тесты | `tests/` | Средний |
| Докеризация | `Dockerfile`, `docker-compose.yml` | Низкий |

## Особенности
- Магический триггер №47: при сохранении 47-го фрагмента бот сообщает о «находке»
- Семантическая классификация: веса категорий (task/idea/identity/knowledge/pattern), эмоции, 3 интерпретации
- Автоматическое распознавание людей (NER через LLM) и сохранение связей с фрагментами
- Полнотекстовый поиск (FTS5) по фрагментам
- Обработка голосовых сообщений: конвертация в WAV 16kHz → транскрибация через Gemini
- **JWT-авторизация** (HS256, 30 дней) — старый X-TG-ID удалён!
- **Rate limiting** — 100/мин глобально, 30/мин на создание фрагментов

## Как работать
1. Перед правками читай QWEN.md в корне лаборатории и этот файл
2. Зависимости: `cd /root/protocol && /root/LabDoctorM/venv/bin/pip install -r requirements.txt`
3. Деплой через systemctl (сервисы уже настроены)
4. Тесты: `pytest` (запускать перед коммитом!)
5. Не трогай `.env` без подтверждения ЗавЛаба
6. Бэкапы: `ls -la /root/protocol/backup/` (хранятся 30 копий)

## Важные примечания
### Авторизация
- **Метод:** `Authorization: Bearer <JWT-token>`
- JWT токен создаётся в `app/jwt_utils.py` (функция `create_access_token`)
- Бот генерирует токен через `make_jwt(tg_id)` в `bot/main.py`

### Rate limiting
- Глобально: 100 запросов/минуту на IP
- Создание фрагментов: 30/минуту на IP
- При превышении: `429 Too Many Requests`

### Бэкапы
- Место: `/root/protocol/backup/protocol.db.YYYY-MM-DD_HH-MM-SS`
- Хранятся 30 последних копий
- Логи: `/root/protocol/logs/backup.log`

### CORS
- Разрешены только: `http://localhost:8000`, `http://127.0.0.1:8000`
- Если нужен другой фронтенд — добавь в `main.py` в `allow_origins`

### Бот @Protocolstandbot
- Токен в `.env`: `BOT_TOKEN=8671317159:AAEwWvWd0zmfAbqy1kAEoGXBlM8NMM0CUTo`
- Команды: `/start`, `/today`, `/search`, `/patterns`
- Обрабатывает: текст, голосовые/аудио (через ffmpeg + Gemini Flash Lite)
- **Все кнопки активны! ✅**
