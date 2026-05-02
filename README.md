# 🏥 LabDoctorM
### *Клинико-диагностическая лаборатория | Автоматизация будущего*

<div align="center">

```
╔══════════════════════════════════════════════════════════════════╗
║  🧬 LAB DOCTOR M • МЕДЛАБОРАТОРИЯ БУДУЩЕГО • FUTURE LAB        ║
╚══════════════════════════════════════════════════════════════════╝
```

[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![aiogram](https://img.shields.io/badge/aiogram-3.0%2B-2CA5E0?logo=telegram&logoColor=white)](https://docs.aiogram.dev/)
[![React](https://img.shields.io/badge/React-18%2B-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![CI/CD](https://img.shields.io/badge/GitHub_Actions-AutoDeploy-2088FF?logo=githubactions&logoColor=white)](https://github.com/features/actions)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[![GitHub last commit](https://img.shields.io/github/last-commit/thedoctormes-hue/shtab-ai-gb52?style=flat&color=blue&logo=github)](https://github.com/thedoctormes-hue/shtab-ai-gb52)
[![GitHub repo size](https://img.shields.io/github/repo-size/thedoctormes-hue/shtab-ai-gb52?style=flat&color=green&logo=github)](https://github.com/thedoctormes-hue/shtab-ai-gb52)
[![GitHub stars](https://img.shields.io/github/stars/thedoctormes-hue/shtab-ai-gb52?style=flat&color=yellow&logo=github)](https://github.com/thedoctormes-hue/shtab-ai-gb52/stargazers)

</div>

---

## 🚀 TL;DR — Что это?

> **LabDoctorM** — экосистема автоматизации лабораторных процессов и инфраструктуры. Мы строим роботов, которые работают за людей, экономя сотни человеко-часов еженедельно.

```
💡 Автоматизация → 📈 Экономия времени → 💰 Экономия денег
```

---

## 🎯 Фокус проекта

| 📊 | 60K клиентов | VPN-инфраструктура |
|:---:|:---:|:---:|
| 🏥 | Клинико-диагностическая лаборатория | Автоматизация бизнес-процессов |
| 🤖 | 7 Telegram-ботов в продакшене | Интеграция с LLM (GPT, Claude, Gemini) |
| 🌐 | 3 дата-центра (Warsaw, Florida, RF) | Мониторинг в реальном времени |

---

## 🛠️ Экосистема проектов

### 🤖 Telegram Боты (7 активных)

| Бот | Описание | Статус |
|:---|:---|:---:|
| [📡 **vpn-daemon**](https://github.com/LabDoctorM/vpn-daemon) | Управление VPN для 60k клиентов | ✅ В проде |
| [📧 **mail-daemon**](https://github.com/LabDoctorM/mail-daemon) | Почтовые уведомления и обработка | ✅ В проде |
| [👨‍💼 **stenographer**](https://github.com/LabDoctorM/stenographer) | Стенография встреч | ✅ В проде |
| [🤖 **llm-evangelist**](https://github.com/LabDoctorM/llm-evangelist) | Авто-ревью LLM моделей | ✅ В проде |
| [📊 **syncthing-dashboard**](https://dashboard.shtab-ai.ru) | Мониторинг синхронизации | ✅ В проде |
| [🔌 **os-lab-api**](https://github.com/LabDoctorM/os-lab-api) | API мониторинга серверов | ✅ В проде |
| [📖 **protocol-bot**](https://t.me/Protocolstandbot) | Личная память и протоколы | ✅ В проде |

### 🌐 Веб-Приложения

| Приложение | Технологии | Статус |
|:---|:---|:---:|
| [**shtab-ai.ru**](https://shtab-ai.ru) | Landing page | ✅ Онлайн |
| [**dashboard.shtab-ai.ru**](https://dashboard.shtab-ai.ru) | React + FastAPI | ✅ Онлайн |
| **os-lab-api** | FastAPI + SQLite | ✅ На 8002 порту |

---

## ⚡ Быстрый старт

### 🔧 Требования

```bash
python3.10+   # Backend сервисы
nodejs + npm  # Frontend приложения
systemd       # Управление сервисами
```

### 🚀 Установка

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

### 🏃‍♂️ Запуск сервисов

```bash
# Backend — через systemd
systemctl restart <service-name>

# Frontend — через nginx
npm run build && rsync -av dist/ /var/www/<project>/
```

---

## 🔄 CI/CD

- **Автоматический деплой** при push в `main` ветку
- **GitHub Actions** проверяют код на каждый PR
- **Docker-ready** для масштабирования

---

## 📡 Мониторинг

| 📍 Локация | 🖥️ Серверы | 🎯 Статус |
|:---|:---|:---:|
| Warsaw | Основной центр | ✅ Онлайн |
| Florida | Резервный центр | ✅ Онлайн |
| RF Proxy | Обход DPI | ✅ Онлайн |

---

## 🤝 Contributing

1. Форкнуть репозиторий
2. Создать ветку `feature/имя-фичи`
3. Внести изменения (соблюдая [Conventional Commits](https://www.conventionalcommits.org/))
4. Создать Pull Request

---

## 📞 Контакты

| 📱 Канал | 🔗 Ссылка |
|:---|:---:|
| 🌐 Сайт | [shtab-ai.ru](https://shtab-ai.ru) |
| 💬 Telegram | [@LabDoctorM](https://t.me/LabDoctorM) |
| 🐙 GitHub | [@thedoctormes-hue](https://github.com/thedoctormes-hue) |

---

<div align="center">

**💎 Invest 2 minutes in setup — save hours every week**  
*Made with ❤️ in LabDoctorM Laboratory*

</div>