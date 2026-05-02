---
name: manage-bot-commands
description: "Вызывать при: 'обнови меню бота', 'добавь команду', 'зарегистрируй команды'"
requiredTools: [read_file, write_file, run_shell_command]
---

# manage-bot-commands

Управление меню команд Telegram бота Qwen Code (регистрация, обновление, добавление команд).

## Triggers

- "обнови меню бота"
- "добавь команду в бота"
- "зарегистрируй команды"
- "сделай красивое меню"

## Steps

1. Прочитать токен бота из `/root/.qwen/.env` (переменная `TELEGRAM_TOKEN`)
2. Узнать `chat_id` из `/root/.qwen/channels/sessions.json` (поле `target.chatId`)
3. Обновить `/root/.qwen/commands.json` с эмодзи (♻️, 📦, 🤖, ❓, 📋, 👨‍💼, 🛡, 📊, 🔄, 🧠, 🔍)
4. Выполнить 3 запроса к Telegram API (`setMyCommands`) для scope:
   - `default`
   - `all_private_chats`
   - `chat` (с конкретным `chat_id`)
5. Проверить результат через `getMyCommands`

## Examples

**Добавить команду /test в меню бота**
Обновляет `commands.json` и делает `setMyCommands` для всех scope.

**Сделать красивое меню**
Добавляет эмодзи к описаниям команд.

## Tools

- `read_file` — чтение конфигов
- `write_file` — обновление `commands.json`
- `run_shell_command` — запросы к Telegram API
