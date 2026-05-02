# AUDIT_2026.md — Полный аудит кодовой базы /root/LabDoctorM

**Дата аудита:** 2026-05-02  
**Аудитор:** КотОлизатОр (hr)

---

## 1. Дублирующийся код между проектами

### 1.1. Core-модули Protocol (database.py)

**Файлы с ~85% дублированием:**

| Файл | Строк | Различия |
|------|-------|----------|
| `/root/LabDoctorM/projects/telegram-bots/protocol/app/database.py` | ~350 | Базовые функции, `upsert_pattern` использует LIKE |
| `/root/LabDoctorM/infrastructure/monitoring/protocol/app/database.py` | ~400 | Доп. `get_user_by_id`, `get_last_fragment_date`, точное совпадение в `upsert_pattern` |

**Ключевые отличия:**
- FTS схема: projects версия включает `fragment_id` в индекс, infrastructure — нет
- `upsert_pattern`: projects ищет по `LIKE "%description%"`, infrastructure — точное совпадение
- Infrastructure версия использует `UNIQUE(user_id, description)` в схеме

**Рекомендация:** Создать shared package `/root/LabDoctorM/shared/protocol_db/`

### 1.2. Config файлы (50-70% дублирования)

```
/projects/telegram-bots/protocol/app/config.py
/infrastructure/monitoring/protocol/app/config.py
```

Infrastructure версия содержит дополнительные поля: `frontend_origins`, `api_base_url`, `debug`.

### 1.3. Telegram Bot конфигурации

VPN Daemon:
- `config_bot.py` — дублирует main.py логику

Mail Daemon:
- `config.py` — похож на структуру protocol config

---

## 2. Устаревшие зависимости в requirements.txt

### 2.1. Версии по проектам

| Проект | FastAPI | Uvicorn | Pydantic | aiosqlite | AIogram |
|--------|---------|---------|----------|-----------|---------|
| protocol | 0.115.0 | 0.30.0 | 2.7.0 | 0.20.0 | — |
| vpn-florida-site | >=0.104.0 ❌ | >=0.24.0 ❌ | >=2.5.0 | — | — |
| vpn-daemon | — | — | — | — | >=3.0.0 |
| mail-daemon | — | — | — | 0.19.0 | 3.4.1 |
| stenographer | — | — | — | — | >=3.0.0 |
| llm-evangelist | — | — | — | — | aiohttp (нет aiogram) |

**Критичные устаревшие:**
- `vpn-florida-site`: FastAPI >=0.104.0 (от 2024-05) — нужно 0.115.0+
- `os-lab-api`: FastAPI >=0.110.0 — нужен pin конкретных версий

---

## 3. Захардкоженные значения (КРИТИЧНО)

### 3.1. Telegram Bot токены

**💀 Файл: `/root/LabDoctorM/VPNDaemonRobot/config_bot.py`**
- Строка 6: `TOKEN = "7593603158:AAHXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"` — реальный токен в коде!

- Строки 11-12: VPN конфиги с реальными IP и ключами REALITY:
```python
"vless": "vless://...@185.138.90.150:10086?...?pbk=Q7P9aveiWcBmNYLcnP5b-HXMnnz7FUcpIfDZKk--elY..."
```

**💀 Файл: `/root/LabDoctorM/VPNDaemonRobot/main.py`**
- Строка 10: `TOKEN = "8649218949:AAESDIYZwLE-tHgC358jmnb9YEIBi3WNJ_A"` — второй токен!

- Строка 26: IP сервера `104.253.1.210` в ping

### 3.2. VPN конфигурации

**📄 Файл: `/root/LabDoctorM/vpn-florida-site/server/main.py`**
- IP: `185.138.90.150` (строки 53, 21, 30)
- IP: `104.253.1.210` (строки 15, 481)
- REALITY public key: `pbk=Q7P9aveiWcBmNYLcnP5b-HXMnnz7FUcpIfDZKk--elY`

### 3.3. Секреты по умолчанию

**📄 Файл: `/root/LabDoctorM/projects/telegram-bots/protocol/app/config.py`**
- Строка 8: `secret_key: str = "change-me-in-prod"` — значение по умолчанию

---

## 4. Неиспользуемые файлы

### 4.1. Archive (полностью неактивны)

**📁 `/root/LabDoctorM/archive/AiderDMrobot/`** — дублирует функционал
- `bot.py` — не импортируется
- `config.py` — не используется
- `utils.py` — не импортируется
- `requirements.txt` — старые версии

**📁 `/root/LabDoctorM/archive/vpn-florida-site/`** — дубль
- `server/main.py` — дублирует `/root/LabDoctorM/vpn-florida-site/server/main.py`

**📁 `/root/LabDoctorM/archive/eva_forewa_bot/`**
- `evaV3.py` — не используется

### 4.2. Одноразовые скрипты

**📄 `/root/LabDoctorM/migrate_filesystem.py`**
- Скорее всего, использовался один раз для миграции

---

## 5. Дополнительные замечания

### 5.1. CORS уязвимости

**📄 `/root/LabDoctorM/vpn-florida-site/server/main.py`**
```python
allow_origins=["*"]  # ❌ Открытый CORS — уязвимость
```

**📄 `/root/LabDoctorM/projects/telegram-bots/protocol/main.py`**
```python
allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"]  # Ограничено
```

### 5.2. Дублирование node_modules

Есть три копии `node_modules` с одинаковыми зависимостями:
- `/root/LabDoctorM/vpn-florida-site/node_modules/`
- `/root/LabDoctorM/archive/landing-page/node_modules/`
- `/root/LabDoctorM/archive/vpn-florida-site/node_modules/`

---

## 6. Рекомендации (приоритеты)

### 🔴 HIGH (безопасность)
1. **Немедленно** вынести токены из `VPNDaemonRobot/*.py` в `.env`
2. Вынести VPN IP адреса и ключи REALITY в `.env`
3. Изменить `secret_key` с дефолтного значения

### 🟡 MEDIUM (техдолг)
1. Создать shared package для database.py
2. Обновить устаревшие версии FastAPI/uvicorn
3. Добавить корневой `requirements.txt` с общими версиями
4. Очистить archive — удалить или добавить в .gitignore

### 🟢 LOW (улучшения)
1. Настроить CORS правильно в vpn-florida-site
2. Удалить дублирующиеся node_modules или вынести в workspace
3. Стандартизировать версии зависимостей между проектами

---

## 7. Файлы для рассмотрения к удалению

```
/root/LabDoctorM/archive/AiderDMrobot/              # Полный дубль
/root/LabDoctorM/archive/vpn-florida-site/         # Дубль vpn-florida-site
/root/LabDoctorM/archive/eva_forewa_bot/evaV3.py   # Не используется
/root/LabDoctorM/migrate_filesystem.py            # Одноразовый скрипт
```

---

**END OF AUDIT**