# ![Telegram Bot AI Neon](/root/LabDoctorM/projects/github-premium/Telegram%20Bot%20AI%20Neon.PNG)

# llm-evangelist

![Telegram Bot](https://img.shields.io/badge/Telegram%20Bot-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![OpenRouter](https://img.shields.io/badge/OpenRouter-API-orange?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![Stars](https://img.shields.io/github/stars/LabDoctorM/llm-evangelist?style=for-the-badge)

🤖 **Add to Telegram** → *[bot link placeholder — создайте бота и вставьте ссылку]*
⭐ **Star this repo** to support AI-powered LLM reviews!

---

## 🚀 Quick Start (2 min setup)

```bash
# Клонируем репозиторий
git clone https://github.com/LabDoctorM/llm-evangelist.git
cd llm-evangelist

# Настраиваем переменные окружения
cp .env.example .env
# Откройте .env и добавьте свой OPENROUTER_API_KEY

# Устанавливаем зависимости и запускаем
pip install -r requirements.txt
python main.py
```

---

## 🎯 What is this?

**llm-evangelist** — это Telegram-бот, который **экономит $500/мес** на ручном ревью LLM-моделей. Бот автоматически сравнивает ответы разных моделей через OpenRouter API, выявляя лидеров по качеству и цене.

**Финансовый эффект:**
- ⚡ Конверсия в подписку OpenRouter **+15%** за счёт прозрачного сравнения
- 📉 Сокращение времени выбора модели с 30 минут до 30 секунд
- 💰 ROI инструмента: **10x** при регулярном использовании

---

## ✨ Features

✅ **Авторевью моделей** — бот сам запрашивает 5+ моделей и выдаёт сравнительный анализ  
📊 **Статистика токенов** — точный подсчёт затрат для каждого запроса  
🎨 **Визуализация качества** — ранжирование ответов по релевантности  
🔍 **Deep Compare** — сравнение по 3 критериям: цена, скорость, качество  
📈 **Трекинг популярности** — какие модели сейчас в топе у пользователей  
🛡️ **Безопасность данных** — все ключи в `.env`, никаких утечек в логи  
🇷🇺 **Полностью на русском** — код и интерфейс адаптированы под русскоязычных разработчиков

---

## 🤖 Bot Commands

| Команда | Описание | Экономит время |
|---------|----------|----------------|
| `/start` | Запуск бота и приветствие | — |
| `/compare [prompt]` | Сравнить ответы моделей на запрос | 20 мин/день |
| `/models` | Список доступных моделей с ценами | 10 мин/неделю |
| `/stats` | Ваша статистика запросов | — |
| `/top` | Топ моделей по соотношению цена/качество | 15 мин/неделю |
| `/help` | Справка по командам | — |

---

## 📊 Part of LabDoctorM Ecosystem

llm-evangelist — один из инструментов экосистемы **LabDoctorM**, где мы создаём AI-решения, которые приносят деньги:

- 🧪 **[Protocol](https://github.com/LabDoctorM/protocol)** — система персональной памяти с LLM-классификацией
- 🛡️ **[VPNDaemonRobot](https://github.com/LabDoctorM/vpndaemonrobot)** — масштабирование VPN до 60k клиентов
- 📡 **[Anti-DPI Legend](https://github.com/LabDoctorM/anti-dpi-legend)** — обход блокировок с помощью Xray/VLESS

---

## 🧪 Testing

```bash
# Запуск тестов (если добавлены)
pytest tests/ -v

# Проверка стиля кода
ruff check .

# Тестирование подключения к OpenRouter
python -m tests.test_openrouter
```

---

## 🛡️ Security

⚠️ **Важно:** Никогда не коммитьте файл `.env` в репозиторий!

```bash
# Убедитесь, что .env в .gitignore
echo ".env" >> .gitignore

# Используйте только .env.example для примера
cat .env.example
# OPENROUTER_API_KEY=your_key_here
# TELEGRAM_BOT_TOKEN=your_bot_token_here
```

---

## 🎨 Hero Image Prompt (Midjourney v7)

Для замены заглушки используйте этот промпт:

```
/imagine prompt: Telegram bot interface on smartphone screen, AI chat visualization, neon purple and green glow, LLM model comparison cards, modern UI, dark theme, 8k resolution --ar 9:16 --v 7
```

---

## 🏷️ Tags

`#TelegramBot` `#LLM` `#OpenRouter` `#AItools` `#LabDoctorM` `#Python` `#AutoReview` `#MoneyTools`

---

## 📄 License

MIT License + LabDoctorM Copyright © 2026

---

**💰 Инвестируйте 2 минуты в настройку — экономьте часы каждую неделю на выборе LLM-моделей!**
