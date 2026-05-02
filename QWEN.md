# LabDoctorM — Лаборатория ЗавЛаб Безуми́й Доктор

## Стек и среда
- **Основной**: Python (aiogram, FastAPI), React
- **venv**: `/root/LabDoctorM/venv/` или локальные `.venv/`
- **Зависимости**: `/root/LabDoctorM/venv/bin/pip install -r requirements.txt`
- **Сервисы**: файлы в `/etc/systemd/system/`, управление через `systemctl`
- **Логи**: `journalctl -u <service-name> -f`

// @see projects.json для списка проектов

## Deploy
- **Python**: `cd /root/LabDoctorM/<project> && systemctl restart <service>`
- **React**: `npm run build && rsync -av dist/ /var/www/<project>/`
- **.env**: не трогать без подтверждения

## Инциденты
- `// @see /root/LabDoctorM/INCIDENTS.md`

## Автоматический старт сессии (ЕБШ)
🔥 Каждая сессия начинается с чтения:
1. `/root/.qwen/evolution_backlog.json` — задачи
2. `/root/.qwen/agents/EMPLOYEES.md` — сотрудники
3. `/root/.qwen/rules.md` — протокол (ниже)

`/root/.qwen/session_startup.sh` — быстрый запуск