# 🏛️ ФАЙЛОВАЯ СИСТЕМА ЛАБОРАТОРИИ ЗАВЛАБ

## 📐 СТАНДАРТ ИЕРАРХИИ

```
/root/LabDoctorM/
├── .lab/                      # Системные файлы лаборатории
│   ├── standards/            # Стандарты кода и документация
│   ├── scripts/              # Системные скрипты
│   └── hooks/                # Git hooks и автоматизация
│
├── projects/                  # ВСЕ ПРОЕКТЫ ЗДЕСЬ!
│   ├── telegram-bots/        # Telegram боты
│   │   ├── botname/          # = название бота
│   │   │   ├── bot.py        # Главный файл
│   │   │   ├── config/       # Конфиги
│   │   │   ├── handlers/     # Хэндлеры
│   │   │   ├── services/     # Сервисы
│   │   │   └── tests/        # Тесты
│   │   └── ...
│   │
│   ├── web-apps/             # Веб-приложения
│   │   ├── app-name/
│   │   │   ├── src/
│   │   │   ├── public/
│   │   │   ├── api/
│   │   │   └── tests/
│   │   └── ...
│   │
│   └── libraries/            # Библиотеки и утилиты
│
├── infrastructure/            # Инфраструктурные сервисы
│   ├── vpn/
│   ├── monitoring/
│   └── proxy/
│
├── docs/                      # Документация (устарело, используй .lab/standards/)
│
├── archive/                   # Архивные проекты
│
├── sandbox/                   # Временные эксперименты
│
├── venv/                      # Виртуальное окружение (только для dev)
│
├── system/                    # Системные сервисы и конфиги
│
└── projects.json              # Реестр всех проектов
```

## 📛 ЗАКОНЫ ИМЕНОВАНИЯ

### 1. Проекты
- **Telegram боты**: `kebab-case-bot` (botfather friendly)
- **Web приложения**: `PascalCase` (Next.js style)
- **Библиотеки**: `snake_case` (Python lib style)

### 2. Файлы
- `.py` → `snake_case.py`
- `.js/.ts` → `camelCase.ext`
- `.md` → `UPPER_CASE.md` (документация)
- `.sh` → `kebab-case.sh`

### 3. Директории
- Все в `kebab-case`
- Главная папка проекта = название проекта

## 🔗 ЦЕПЬ ЗАВИСИМОСТЕЙ

```
projects.json → settings.json → systemd services
     ↓               ↓                ↓
  Реестр      ←→   Токены      ←→   Авто-деплой
```

## ⚡ КОМАНДЫ МУВАЦИИ

```bash
# Анализ текущего бардака
python3 /root/LabDoctorM/migrate_filesystem.py --scan

# Миграция проектов в правильное место
python3 /root/LabDoctorM/migrate_filesystem.py --move

# Валидация стандарта
python3 /root/LabDoctorM/migrate_filesystem.py --validate
```
