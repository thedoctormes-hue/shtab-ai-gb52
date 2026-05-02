# 🏥 LabDoctorM

**Клинико-диагностическая лаборатория | Laboratory Doctor**

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![aiogram](https://img.shields.io/badge/aiogram-3.0%2B-blue?logo=telegram)](https://docs.aiogram.dev/)
[![React](https://img.shields.io/badge/React-18%2B-61DAFB?logo=react)](https://react.dev/)
[![GitHub last commit](https://img.shields.io/github/last-commit/thedoctormes-hue/shtab-ai-gb52?style=flat&color=blue)](https://github.com/thedoctormes-hue/shtab-ai-gb52)
[![GitHub repo size](https://img.shields.io/github/repo-size/thedoctormes-hue/shtab-ai-gb52?style=flat&color=green)](https://github.com/thedoctormes-hue/shtab-ai-gb52)

---

## 📋 О проекте

**LabDoctorM** — экосистема для автоматизации лабораторных процессов и инфраструктуры. Инструменты, которые приносят деньги.

**КДЛ (Клинико-диагностическая лаборатория)** — [shtab-ai.ru](https://shtab-ai.ru)

### 💡 Экосистема проектов

| Проект | Тип | Описание | Статус |
|--------|-----|----------|--------|
| [🌐 shtab-ai-gb52](https://shtab-ai.ru) | landing | КДЛ сайт | ✅ |
| [📡 vpn-daemon](https://github.com/LabDoctorM/vpn-daemon) | telegram-bot | VPN управление (60k клиентов) | ✅ |
| [📧 mail-daemon](https://github.com/LabDoctorM/mail-daemon) | telegram-bot | Почтовые уведомления | ✅ |
| [👨‍💼 stenographer](https://github.com/LabDoctorM/stenographer) | telegram-bot | Стенография встреч | ✅ |
| [🤖 llm-evangelist](https://github.com/LabDoctorM/llm-evangelist) | telegram-bot | Авто-ревью LLM моделей | ✅ |
| [📊 syncthing-dashboard](https://dashboard.shtab-ai.ru) | dashboard | Мониторинг синхронизации | ✅ |
| [🔌 os-lab-api](https://github.com/LabDoctorM/os-lab-api) | api | Мониторинг серверов | ✅ |

---

## 🚀 Быстрый старт

### Требования
```bash
python3.10+
pip
nodejs + npm
```

### Установка
```bash
# Клонирование
git clone https://github.com/thedoctormes-hue/shtab-ai-gb52.git
cd shtab-ai-gb52

# Python зависимости
pip install -r requirements.txt

# Frontend (для веб-приложений)
cd projects/web-apps/syncthing-dashboard
npm install
npm run build
```

### Запуск сервисов
```bash
# Python сервисы
systemctl restart <service-name>

# Web приложения
npm run dev  # разработка
npm run build && rsync -av dist/ /var/www/<project>/  # прод
```

---

## 🛠️ Деплой

### Автоматический (CI/CD)
GitHub Actions развертывает изменения автоматически при push в `main`.

### Ручной деплой
```bash
# Backend
cd /root/LabDoctorM/<project>
systemctl restart <service>

# Frontend
npm run build
rsync -av dist/ /var/www/<project>/
```

---

## 📊 Мониторинг

- **Серверы**: Warsaw, Florida, RF Proxy
- **Dashboard**: [dashboard.shtab-ai.ru](https://dashboard.shtab-ai.ru)
- **API**: os-lab-api (порт 8002)

---

## 🤝 Contributing

1. Форкнуть репозиторий
2. Создать ветку `feature/имя-фичи`
3. Внести изменения (соблюдая [Conventional Commits](https://www.conventionalcommits.org/))
4. Создать Pull Request

---

## 📞 Контакты

- Сайт: [shtab-ai.ru](https://shtab-ai.ru)
- GitHub: [@thedoctormes-hue](https://github.com/thedoctormes-hue)
- Telegram: [@LabDoctorM](https://t.me/LabDoctorM)

---

<p align="center">
  <b>💰 Инвестируйте 2 минуты в настройку — экономьте часы каждую неделю</b>
</p>