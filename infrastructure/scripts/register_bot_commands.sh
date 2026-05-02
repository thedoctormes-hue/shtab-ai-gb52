#!/bin/bash

# 🛠 Регистрация команд для КотОлизатОр (ЗавЛаб Безумний Доктор)
# Использование: 
# 1. Вставь токен бота в BOT_TOKEN ниже
# 2. Запусти: bash register_bot_commands.sh

BOT_TOKEN="<TELEGRAM_BOT_TOKEN>"

if [ "$BOT_TOKEN" = "<TELEGRAM_BOT_TOKEN>" ]; then
    echo "❌ Вставь токен бота в переменную BOT_TOKEN!"
    exit 1
fi

echo "🚀 Регистрирую команды для бота..."
curl -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setMyCommands" \
-H "Content-Type: application/json" \
-d '{
  "commands": [
    {"command": "clear", "description": "♻️ Сбросить контекст сессии"},
    {"command": "agent", "description": "👨‍💼 Вызвать сотрудника: /agent <имя> <запрос>"},
    {"command": "skills", "description": "🛠 Запустить навык: /skills <имя> <запрос>"},
    {"command": "plan", "description": "📋 Разбить задачу на шаги"},
    {"command": "status", "description": "📊 Показать статус системы"},
    {"command": "reload", "description": "🔄 Перезагрузить список сотрудников"},
    {"command": "help", "description": "❓ Показать шпаргалку по командам"}
  ],
  "language_code": "ru"
}'

echo -e "\n✅ Готово! Проверь команды в Telegram."