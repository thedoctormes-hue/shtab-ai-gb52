# LabDoctorM — Лаборатория ЗавЛаб Безуми́й Доктор

## Стек и среда
- **Основной**: Python (aiogram, FastAPI), React
- **venv**: `/root/LabDoctorM/venv/` или локальные `.venv/`
- **Зависимости**: `/root/LabDoctorM/venv/bin/pip install -r requirements.txt`
- **Сервисы**: файлы в `/etc/systemd/system/`, управление через `systemctl`
- **Логи**: `journalctl -u <service-name> -f`

// @see projects.json для списка проектов

## Глобальные правила
1. Читай QWEN.md в корне и в папке проекта перед работой
2. Мелкие задачи — сразу делай. Сложные — `/plan`
3. Ошибки — сразу фиксим
4. Деплой — инструкции в `## Deploy` в QWEN.md проекта
5. Тесты: `pytest` для Python, `npm test` для React

## Инциденты
- `// @see /root/LabDoctorM/INCIDENTS.md`