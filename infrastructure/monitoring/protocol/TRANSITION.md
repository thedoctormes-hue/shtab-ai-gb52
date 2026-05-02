# Протокол — Переходная документация

**Дата передачи:** 2026-04-27 (обновлено: Спринт 2 завершён)
**Статус:** Спринт 2 ЗАВЕРШЁН ✅, готовы к Спринту 3
**Кто делал:** КотОлизатОр (Qwen Code) для ЗавЛаб Безумный Доктор

---

## Что сделано в этой сессии

### 1. Полное изучение проекта
- Прочитан и проанализирован **весь код** проекта `/root/protocol`
- Составлен подробный отчёт структуры, стека, компонентов
- Наняты сотрудники: `context-session-specialist`, `docs-writer`, `skill-architect`, `protocol-analyst`

### 2. Создана документация
- ✅ `/root/protocol/QWEN.md` — описание проекта, стек, деплой
- ✅ `/root/protocol/TECHNICAL_AUDIT.md` — полный технический аудит (6 разделов)
- ✅ `/root/LabDoctorM/QWEN.md` — добавлен раздел **Protocol**
- ✅ `/root/.qwen/projects/-root-LabDoctorM/memory/protocol_project.md` — сохранён контекст проекта
- ✅ `/root/.qwen/projects/-root-LabDoctorM/memory/MEMORY.md` — добавлена ссылка на Protocol

### 3. Спринт 1: «Безопасность и надёжность» — ЗАВЕРШЁН ✅

| Задача | Статус | Детали |
|--------|--------|--------|
| Сменить SECRET_KEY | ✅ | Сгенерирован ключ `39908bf5e4001ea815b6fa84c2d2d4bb...` в `.env` |
| Ограничить CORS | ✅ | `allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"]` |
| Бэкап БД | ✅ | Скрипт `/root/protocol/backup_db.sh`, cron `0 3 * * *` |
| Logrotate | ✅ | Конфиг `/etc/logrotate.d/protocol` (7 дней, сжатие) |
| JWT-авторизация | ✅ | Заменён X-TG-ID на JWT (HS256, 30 дней) |
| Rate limiting | ✅ | slowapi: 100/мин глобально, 30/мин на создание фрагментов |

### 4. Спринт 2: «Активация фич» — ЗАВЕРШЁН ✅

| Задача | Статус | Что сделано |
|--------|--------|------------|
| API для `memory_edges` | ✅ | Создан `app/routers/edges.py` (CRUD) |
| API для `exit_settings` | ✅ | Создан `app/routers/settings.py` |
| Подключение роутеров | ✅ | Обновлён `main.py` |
| Кнопки «Все фрагменты» | ✅ | Работает, показывает фрагменты за сегодня |
| Кнопки «Паттерны» | ✅ | Работает, показывает паттерн дня |
| Кнопка «Подробнее» | ✅ | Показывает все паттерны пользователя |
| Кнопка «История» | ✅ | Показывает историю паттернов |
| Кнопка «Связать» | ✅ | Создаёт связи через `edges` API |
| Кнопка «Удалить» | ✅ | Удаляет фрагменты через API |
| Чтение `people_edges` | ✅ | Добавлено в `database.py` |
| Тесты (pytest) | ✅ | 7 тестов в `tests/test_new_features.py` |

---

## Текущее состояние проекта

### Работающие сервисы
```bash
systemctl status protocol.service        # FastAPI на порту 8000
systemctl status protocol-bot.service    # Telegram-бот @Protocolstandbot
systemctl status protocol-analyst.timer # Ночной аналитик (00:00 UTC)
```

### Ключевые файлы и что они делают

| Файл | Назначение |
|-------|------------|
| `/root/protocol/main.py` | Точка входа FastAPI, CORS, rate limiter, подключены все роутеры |
| `/root/protocol/bot/main.py` | Telegram-бот, JWT-авторизация, ВСЕ кнопки активны ✅ |
| `/root/protocol/app/database.py` | Схема БД (SQLite FTS5), функции для работы с данными |
| `/root/protocol/app/classifier.py` | Классификация через OpenRouter (Gemini/Llama) |
| `/root/protocol/app/night_analyst.py` | Ночной анализ паттернов |
| `/root/protocol/app/deps.py` | JWT-авторизация (Authorization: Bearer) |
| `/root/protocol/app/jwt_utils.py` | Создание и декодирование JWT-токенов |
| `/root/protocol/app/limiter.py` | Настройка slowapi rate limiter |
| `/root/protocol/app/people.py` | Извлечение и сохранение людей (NER) |
| `/root/protocol/app/routers/edges.py` | ✅ NEW: CRUD для memory_edges |
| `/root/protocol/app/routers/settings.py` | ✅ NEW: API для exit_settings |
| `/root/protocol/app/routers/fragments.py` | Роутер фрагментов |
| `/root/protocol/app/routers/users.py` | Роутер пользователей |
| `/root/protocol/app/routers/patterns.py` | Роутер паттернов |
| `/root/protocol/tests/test_new_features.py` | ✅ NEW: Тесты для Спринта 2 |
| `/root/protocol/.env` | Переменные окружения (НОВЫЙ SECRET_KEY!) |
| `/root/protocol/backup_db.sh` | Скрипт ежедневного бэкапа БД |
| `/etc/logrotate.d/protocol` | Ротация логов |

### Установленные пакеты (добавлены в Спринтах 1-2)
```bash
PyJWT==2.12.1      # JWT-токены
slowapi==0.1.9      # Rate limiting
pytest==9.0.3       # Тесты
pytest-asyncio==1.3.0  # Асинхронные тесты
httpx==0.27.0       # HTTP клиент (для тестов и бота)
```

### Fixes in dependencies
```bash
starlette==0.38.6    # Downgraded for compatibility with FastAPI 0.115.0
```

---

## Что НЕ сделано (в планах Спринта 3)

### Неактивные поля схемы
- `users.encryption_key` — не используется
- `users.meta` — не используется
- `memory_fragments.privacy` — сохраняется, но не фильтруется
- `memory_fragments.meta` — не используется
- `exit_settings.*` — API есть, но нет UI в боте для настройки

### Частично активные фичи
- `people_edges` — данные сохраняются, чтение есть в `database.py`, но нет отображения в боте или API для просмотра
- Кнопка «Связать» — работает базово, но нужен более удобный UI выбора фрагментов

---

## План Спринта 3: «Полировка и фронтенд»

**Цель:** Довести проект до production-ready состояния.

| Задача | Где | Приоритет | Что делать |
|--------|-----|------|------------|
| UI настроек в боте | `bot/main.py` | Высокий | Команды /settings, настройка export_format, auto_delete |
| Просмотр people_edges | `bot/main.py`, API | Средний | Показывать связанных людей с фрагментами |
| Фильтрация по privacy | `app/routers/fragments.py` | Средний | Использовать поле privacy в поиске и списке |
| Фронтенд (React) | Новая папка `frontend/` | Высокий | Веб-интерфейс для просмотра фрагментов и паттернов |
| Улучшение UX кнопок | `bot/main.py` | Низкий | Красивое форматирование, пагинация, inline-кнопки |
| Интеграционные тесты | `tests/` | Средний | Тесты с реальной БД (sqlite в памяти) |
| Докеризация | `Dockerfile`, `docker-compose.yml` | Низкий | Контейнеризация для деплоя |

---

## Важные примечания для следующей сессии

### 1. Авторизация
- **Метод:** `Authorization: Bearer <JWT-token>`
- JWT токен создаётся в `app/jwt_utils.py` (функция `create_access_token`)
- Бот генерирует токен через `make_jwt(tg_id)` в `bot/main.py`
- **Важно:** Старый метод `X-TG-ID` полностью удалён!

### 2. Rate limiting
- Глобально: 100 запросов/минуту на IP
- Создание фрагментов: 30/минуту на IP
- При превышении: `429 Too Many Requests`

### 3. Бэкапы
- Место: `/root/protocol/backup/protocol.db.YYYY-MM-DD_HH-MM-SS`
- Хранятся 30 последних копий
- Логи: `/root/protocol/logs/backup.log`
- Проверка: `ls -la /root/protocol/backup/`

### 4. CORS
- Разрешены только: `http://localhost:8000`, `http://127.0.0.1:8000`
- Если нужен другой фронтенд — добавь в `main.py` в `allow_origins`

### 5. Бот @Protocolstandbot
- Токен в `.env`: `BOT_TOKEN=8671317159:AAEwWvWd0zmfAbqy1kAEoGXBlM8NMM0CUTo`
- Команды: `/start`, `/today`, `/search`, `/patterns`
- Обрабатывает: текст, голосовые/аудио (через ffmpeg + Gemini Flash Lite)
- **Все кнопки активны! ✅**

### 6. Тесты
- Запуск: `cd /root/protocol && /root/LabDoctorM/venv/bin/pytest tests/ -v`
- 7 тестов проходят успешно
- Покрытие: проверка структуры API, схем, health check

### 7. Каскад LLM моделей (Протокол)
- **Primary**: `google/gemini-2.5-flash` (через OpenRouter)
- **Fallback**: `meta-llama/llama-3.3-70b-instruct:free`
- **Транскрипция**: `google/gemini-2.0-flash-lite-001`
- Схема: текст → Gemini 2.5 Flash → если ошибка → Llama 3.3 70B → заглушка

---

## Как продолжить работу

### Быстрый старт в новой сессии
```bash
# 1. Проверить статус сервисов
systemctl status protocol.service protocol-bot.service

# 2. Проверить логи
journalctl -u protocol-bot.service -n 50

# 3. Проверить наличие бэкапов
ls -la /root/protocol/backup/

# 4. Прочитать технический аудит
cat /root/protocol/TECHNICAL_AUDIT.md

# 5. Запустить тесты
cd /root/protocol && /root/LabDoctorM/venv/bin/pytest tests/ -v

# 6. Список задач Спринта 3 (см. выше в этом файле)
```

### Что читать в первую очередь
1. `/root/protocol/TRANSITION.md` (этот файл) — что сделано, что планируется
2. `/root/protocol/TECHNICAL_AUDIT.md` — разделы 4 (Карта активации) и 6 (Следующие 3 спринта)
3. `/root/protocol/QWEN.md` — текущее состояние проекта

---

## Контекст для Qwen Code (следующая сессия)

При старте новой сессии, чтобы восстановить контекст, выполните (внутри Qwen Code):
```
/context-session-specialist restore protocol project
```

Или просто попросите:
```
Прочитай /root/protocol/TRANSITION.md и продолжи Спринт 3
```

### Kratkaya pamiatka dlya novoy sessii:
1. **JWT работает** — не используй старый X-TG-ID!
2. **Спринт 2 завершён** — memory_edges, exit_settings, кнопки бота активны
3. **Тесты проходят** — 7 тестов ✅
4. **Спринт 3 ждёт** — фронтенд, UI настроек, полировка

---

**Готово! Спринт 2 закрыт, Спринт 3 ждёт. Удачи, ЗавЛаб! 🚀**

---

## Приложение: Сотрудники лаборатории

### Наняты через HR-специалиста:
- `commercial-agent.md` — коммерческий агент
- `context-session-specialist.md` — контекстный спец
- `deploy-bot.md` — бот деплоя
- `docs-writer.md` — техпис
- `skill-architect.md` — архитектор скилов

### Скиллы лаборатории (`/root/LabDoctorM/skills/`):
- `manage-bot-commands/SKILL.md` — управление командами бота
- `vpn-setup/SKILL.md` — настройка VPN

### MCP сервера (доступны Qwen Code):
- **filesystem** — файловая система (чтение/запись/поиск)
- **memory** — граф памяти (knowledge graph для контекста)
- **time** — время и таймзоны
- **zavlab-vibecoding** — спецы лабы (QWEN.md, деплой, память)
- **mermaid** — генерация диаграмм

### LLM модели (Qwen Code + Протокол):
- **Qwen Code (я):** Qwen (через канал Qwen Code / OpenRouter)
- **Классификатор Протокола:** Gemini 2.5 Flash → Llama 3.3 70B (fallback)
- **Транскрипция:** Gemini 2.0 Flash Lite
