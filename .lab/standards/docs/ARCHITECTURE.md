# Архитектурная справка LabDoctorM

## Боты проекта

### 1. @MSKgastroDigestbot — Дайджест новостей
- **Путь:** `/root/LabDoctorM/@MSKgastroDigestbot/`
- **Стек:** Python 3, aiogram, httpx, beautifulsoup4
- **LLM:** OpenRouter (mistralai/mistral-small-creative, mistralai/mistral-nemo, x-ai/grok-3-mini, anthropic/claude-3-haiku)
- **БД:** JSON файлы (`channels.json`, `processed.json`)
- **Функция:** Парсит каналы, создает дайджест для @moscovskiiest

### 2. AiderDMrobot — AI-ассистент для кода
- **Путь:** `/root/LabDoctorM/AiderDMrobot/`
- **Стек:** Python 3, python-telegram-bot, aiohttp
- **LLM:** OpenRouter (deepseek/deepseek-chat, mistralai/mistral-nemo)
- **БД:** Нет (управляет другими ботами)
- **Функция:** Интерфейс для Qwen Code через Telegram, управление армией ботов

### 3. VPNDaemonRobot — VPN Management
- **Путь:** `/root/LabDoctorM/VPNDaemonRobot/`
- **Стек:** Python 3, aiogram 3.x, Xray-core
- **LLM:** Нет (VPN-бот)
- **БД:** JSON (`clients.json`, `servers.json`)
- **Функция:** Управление VLESS+REALITY серверами (Warsaw, Florida)

### 4. Protocol — Система личной памяти
- **Путь:** `/root/LabDoctorM/protocol/`
- **Стек:** FastAPI, aiogram 3.x, React + Vite, SQLite FTS5
- **LLM:** OpenRouter (Gemini 2.5 Flash, Llama 3.3 70B)
- **БД:** SQLite + FTS5
- **Функция:** Сохранение мыслей, классификация, поиск, паттерн-анализ

### 5. LLMevangelist — Анонсер моделей
- **Путь:** `/root/LabDoctorM/LLMevangelist/`
- **Стек:** Python 3, aiohttp, python-telegram-bot
- **LLM:** OpenRouter (mistralai/mistral-small-creative, mistralai/mistral-nemo, x-ai/grok-3-beta, deepseek/deepseek-v3)
- **БД:** JSON (`posted_models.json`)
- **Функция:** Публикация обзоров новых LLM-моделей в Telegram-канал

### 6. MailDaemonRobot — Email-бот
- **Путь:** `/root/LabDoctorM/MailDaemonRobot/`
- **Стек:** Python 3, imaplib, aiogram
- **LLM:** OpenRouter (из .env: `OPENROUTER_API_KEY`)
- **БД:** JSON
- **Функция:** Чтение email и генерация ответов через AI

### 7. eva_forewa_bot — EVA персональный бот
- **Путь:** `/root/LabDoctorM/eva_forewa_bot/`
- **Стек:** Python 3, aiogram
- **LLM:** OpenRouter (google/gemini-2.0-flash-001)
- **БД:** Нет
- **Функция:** Персональный помощник EVA

## Сводная таблица

| Бот | Язык | Фреймворк | LLM | БД | Приоритет |
|-----|------|-----------|-----|-----|----------|
| @MSKgastroDigestbot | Python | aiogram | OpenRouter | JSON | 1 |
| AiderDMrobot | Python | python-telegram-bot | OpenRouter | — | 2 |
| VPNDaemonRobot | Python | aiogram | — | JSON | 1 |
| Protocol | Python/React | FastAPI/React | OpenRouter | SQLite FTS5 | 1 |
| LLMevangelist | Python | aiohttp | OpenRouter | JSON | 3 |
| MailDaemonRobot | Python | aiogram | OpenRouter | JSON | 3 |
| eva_forewa_bot | Python | aiogram | OpenRouter | — | 2 |

## Инфраструктура

### Виртуальное окружение
- **Путь:** `/root/LabDoctorM/venv/` или проектные `.venv/`
- **Установка:** `/root/LabDoctorM/venv/bin/pip install -r requirements.txt`

### Сервисы systemd
- `mskgastrodigestbot.service`
- `aiderdm.service`
- `demonvpn.service` (Xray)
- `demonvpn-bot.service`
- `vpn-florida.service` (FastAPI для Florida)
- `protocol.service`
- `protocol-bot.service`
- `protocol-analyst.service`

### Мониторинг
- `journalctl -u <service-name> -f`
- Логи в `<project>/logs/`

## Конвенции
- Команды деплоя: `systemctl restart <service>`
- React-приложения: `npm run build && rsync -av dist/ /var/www/<project>/`
- **Не трогать .env без подтверждения**