# Protocol — Система личной памяти

## Обзор
База: /root/LabDoctorM/protocol/
Тип: Система личной памяти с ИИ-классификацией и Telegram-интерфейсом. Позволяет сохранять мысли (текст/голос), классифицировать через LLM, искать по FTS5, выявлять повторяющиеся паттерны мышления.

**Статус:** Спринт 3 ЗАВЕРШЁН ✅, готовы к Спринту 4.

## Стек
- Backend: FastAPI 0.115.0 + Uvicorn
- Bot: aiogram 3.x
- DB: SQLite 3 + FTS5
- LLM: OpenRouter (Gemini 2.5 Flash / Llama 3.3 70B)
- Транскрибация: Gemini 2.0 Flash Lite + ffmpeg
- Auth: JWT (HS256, 30 дней)
- Frontend: React + Vite (порт 5173)

## Файлы
### Основные
- `main.py` — точка входа FastAPI, CORS, rate limiter
- `bot/main.py` — Telegram-бот (@Protocolstandbot), **ВСЕ кнопки активны ✅**
- `app/database.py` — работа с SQLite (FTS5, схема БД), включая `get_people_edges`
- `app/classifier.py` — классификация фрагментов и транскрибация аудио
- `app/night_analyst.py` — ночной анализ паттернов (cron 00:00 UTC)
- `app/people.py` — извлечение и сохранение упомянутых людей

### Новые файлы (Спринт 3 ✅)
- `app/routers/edges.py` — **NEW:** CRUD для memory_edges
- `app/routers/settings.py` — **NEW:** API для exit_settings (исправлен 500 error)
- `app/routers/people.py` — **NEW:** API для people (исправлены SQL-запросы)
- `frontend/app/` — **NEW:** React фронтенд (Home, Search, People, Settings)
- `Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml` — **NEW:** Докеризация
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
cd /root/LabDoctorM/protocol
/root/LabDoctorM/venv/bin/pytest tests/ -v
```
- ✅ 7 тестов в `tests/test_new_features.py` проходят успешно
- Покрытие: структура API, схемы, health check
- Зависимости для тестов: `pytest`, `pytest-asyncio`, `httpx`
- Custom tests: `test_full_cycle.py`, `test_everything.py`

## Спринт 3 ЗАВЕРШЁН ✅ (Обновлено 2026-04-28)

### Что сделано:
1. **Фронтенд (React + Vite)** — Скелет распакован, настроен `vite.config.ts`, установлены зависимости, CORS настроен.
2. **Интеграция Frontend-Backend** — CORS в `config.py` обновлен, JWT-авторизация через `/users/register` работает.
3. **API Людей (People)** — Создан `app/routers/people.py`, подключен в `main.py`. Исправлены SQL-запросы.
4. **API Настроек (Settings)** — Пофикшен `app/routers/settings.py`. Устранена 500-я ошибка: добавлен Upsert (UPDATE/INSERT), логирование ошибок.
5. **Бот @Protocolstandbot** — Добавлена кнопка `/settings` в `/start`. Реализованы инлайн-хендлеры `settings_*`, `set_format:`, `set_autodelete:`.
6. **Docker** — Созданы `Dockerfile` (бэкенд), `frontend/Dockerfile` (фронтенд), `docker-compose.yml`.
7. **Тесты** — Написаны скрипты `test_full_cycle.py`, `test_final.py`, `test_everything.py`.

### Исправленные баги:
- ✅ **Settings API 500** → Исправлено в `app/routers/settings.py`.
- ✅ **People API пустой** → Исправлены SQL-запросы в `app/routers/people.py`.
- ✅ **FragmentCard не рендерит текст** → Исправлено в `frontend/app/src/components/FragmentCard.tsx`.
- ✅ **AuthContext не сохранял user_id** → Исправлено в `frontend/app/src/context/AuthContext.tsx`.

## План Спринта 4: «Коммерческая готовность»
**Цель:** Превратить рабочий прототип в продукт, приносящий деньги. Устранить 3 «смертных греха» из аудита.

**Бюджет времени:** 30 дней.
**Ожидаемый рост:** +$2600/мес (LTV).

| Задача | Где | Приоритет | Ожидаемый $ Impact | Статус |
|--------|-----|------|------|--------|
| Онбординг (3 шага) | `bot/main.py` | Высокий | +$800/мес | ⚠️ В процессе |
| Воронка и CRM (нотификации) | `app/night_analyst.py`, `bot/main.py` | Высокий | +$800/мес | ⚠️ В процессе |
| Социальный граф (People UX) | `frontend/app/src/pages/People.tsx` | Средний | +$600/мес | ⚠️ В процессе |
| Полировка фронтенда | Все страницы React | Средний | +$200/мес | ⚠️ В процессе |
| Докеризация (Compose) | `docker-compose.yml` | Низкий | +$100/мес | ✅ Готово |
| Интеграционные тесты | `tests/` | Средний | +$300/мес | ⚠️ В процессе |

### Детализация задач Спринта 4 (см. `SPRINT4_SPEC.md`):
1. **Онбординг:** 3-шаговый визард после `/start`. Первый фрагмент, первый голос, предложение `/patterns`.
2. **Настройки экспорта:** UI в боте (редактирование auto_delete_days).
3. **Социальный граф:** Отображение реальных данных из API People, граф связей.
4. **Воронка:** Cron + Ночной анализ должен слать сводку в 09:00 по Москве. Magic Trigger 47: предлагать экспорт истории.
5. **Фронтенд:** Страница `People.tsx` должна строить граф (или список связей). `Settings.tsx` — форма редактирования.

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
- Бот генерирует токен через `create_access_token(tg_id)` в `bot/main.py`

### Rate limiting
- Глобально: 100 запросов/минуту на IP
- Создание фрагментов: 30/минуту на IP
- При превышении: `429 Too Many Requests`

### Бэкапы
- Место: `/root/protocol/backup/protocol.db.YYYY-MM-DD_HH-MM-SS`
- Хранятся 30 последних копий
- Логи: `/root/protocol/logs/backup.log`

### CORS
- Разрешены: `http://localhost:8000`, `http://127.0.0.1:8000`, `http://localhost:5173`, `http://127.0.0.1:5173`
- Если нужен другой фронтенд — добавь в `app/config.py` в `frontend_origins`

### Бот @Protocolstandbot
- Токен в `.env`: `BOT_TOKEN=<your-token>` (get via @BotFather)
- Команды: `/start`, `/today`, `/search`, `/patterns`, `/settings`
- Обрабатывает: текст, голосовые/аудио (через ffmpeg + Gemini Flash Lite)
- **Все кнопки активны! ✅**

## Статус проекта (на 2026-04-28)
- Backend: `http://localhost:8000` (дока: `/docs`) — ✅ Живой
- Frontend: `http://localhost:5173` — ✅ Живой
- Bot: `@Protocolstandbot` — ✅ Active (running)
- Docker: ✅ Готово к деплою
- Docs: ✅ QWEN.md, SPRINT4_SPEC.md обновлены

## Инцидент 2026-04-28
**Утечка памяти и рестарт-петля:**
- Корень: порт 8000 занят зомби-процессом → protocol.service падал → protocol-bot рестартился
- Фикс: убит PID 198547, пофикшен run_bot.sh, очищен journald (2.4GB → 72MB)
- Статус: ✅ Стабилизировано в 11:30 MSK
- Подробности: `/root/LabDoctorM/INCIDENTS.md`
