# @MSKgastroDigestbot — МСК ГАСТРО ДАЙДЖЕСТ

## Назначение
Telegram-бот для создания дайджестов новостей и ресторанов Москвы. Публикует в канал @moscovskiiest.

## Стек
- **Python 3**, **aiogram** (Telegram Bot API)
- **Библиотеки**: httpx, beautifulsoup4, python-dotenv
- **AI**: OpenRouter (модели: mistralai/mistral-small-creative, mistralai/mistral-nemo, x-ai/grok-3-mini, anthropic/claude-3-haiku)

## Файлы проекта
- `main.py` — основной код бота (v6.1)
- `requirements.txt` — зависимости
- `channels.json` — список каналов для дайджеста
- `processed.json` — прогресс обработки
- `.env` — токены (путь: `/root/LabDoctorM/@MSKgastroDigestbot/.env`)
- `logs/digest.log` — логи

## Переменные окружения (.env)
- `TELEGRAM_BOT_TOKEN` — токен бота
- `AUTHOR_TELEGRAM_ID` — ID автора
- `OPENROUTER_API_KEY` — ключ OpenRouter
- `CHANNEL_ID` — `@moscovskiiest` (боевой канал)

## Зависимости
```bash
/root/LabDoctorM/venv/bin/pip install -r requirements.txt
```

## Деплой (## Deploy)
```bash
systemctl restart mskgastrodigestbot
```
Сервис: `/etc/systemd/system/mskgastrodigestbot.service`

## Логи
```bash
journalctl -u mskgastrodigestbot -f
# Или файл:
tail -f /root/LabDoctorM/@MSKgastroDigestbot/logs/digest.log
```

## Особенности
- Работает с несколькими каналами (defaults: raidedrests, restaurantmoscow, vkusonomika, sysoevfm, thesaltmagazine, michelinwontgive)
- Вердикты: случайный выбор из списка (Хочу посетить, Стоит проверить, Есть сомнения, Лучше пропустить)
- Дисклеймер: дайджест сформирован при помощи AI
- Voice DNA: главный редактор @moscovskiiest, честно, с лёгкой иронией

## Как работать
- При изменении `requirements.txt` — переустановка зависимостей
- При правке `main.py` — `systemctl restart mskgastrodigestbot`
- Перед коммитом — тесты (если есть)
