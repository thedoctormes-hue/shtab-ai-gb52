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