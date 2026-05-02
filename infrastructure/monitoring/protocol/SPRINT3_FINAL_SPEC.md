# 🚀 Protocol: Итоговый Спек Спринта 3 (Финальная редакция)

**Версия:** 2.0 (После ультра-аудита)
**Дата:** 2026-04-28
**Статус:** ✅ Готов к реализации
**Автор:** ЗавЛаб Безумный Доктор + КотОлизатОр

---

## 1. Архитектура решения (Tех. стек)

### Бэкенд (существует, вычищен)
- **FastAPI** (0.115.0) + **Uvicorn** (внутри venv: `/root/LabDoctorM/venv/`)
- **БД:** SQLite 3 + FTS5 (полнотекстовый поиск)
- **LLM:** OpenRouter (Gemini 2.5 Flash / Llama 3.3 70B)
- **Бот:** aiogram 3.17.0

### Фронтенд (Твой скелет, ЗавЛаб!)
- **База:** `/root/LabDoctorM/protocol/frontend/`
- **Стек:** React 18, Axios, React Router v6
- **Auth:** JWT (HS256), токен хранится в `localStorage`

---

## 2. Что сделано в ходе аудита (P0 Fixes)

### Критические фиксы (погнали в прод):
1. **Миграция путей:** Проект перенесен в `/root/LabDoctorM/protocol/`. Все хардкоды (`/root/protocol`) вычищены.
2. **Systemd:** Сервисы (`protocol.service`, `protocol-bot.service`, `protocol-analyst.service`) перенастроены на использование Python из venv.
3. **Баг поиска в боте:** Исправлена передача `tg_id` вместо `user_id` (UUID) в функцию `search_fragments`.
4. **CORS:** В `main.py` добавлены порты для React-фронта (3000).
5. **Real paths:** `backup_db.sh` и `/etc/logrotate.d/protocol` обновлены.

---

## 3. ТЗ на Фронтенд (Для ЗавЛаба)

### 3.1 Структура (скелет)
```
frontend/
├── public/index.html
├── src/
│   ├── api/
│   │   ├── client.js       # Axios instance + interceptors
│   │   ├── fragments.js
│   │   ├── auth.js
│   │   ├── people.js      # NEW: API для people_edges
│   │   └── settings.js
│   ├── components/
│   │   ├── Layout.jsx
│   │   ├── FragmentCard.jsx
│   │   ├── PatternCard.jsx
│   │   └── PeopleCard.jsx
│   ├── pages/
│   │   ├── Login.jsx      # Вход (Telegram ID -> JWT)
│   │   ├── Home.jsx       # Главная (мысли + ввод)
│   │   ├── Search.jsx     # FTS5 поиск (с дебаунсом!)
│   │   ├── People.jsx     # Люди и связи (NEW)
│   │   └── Settings.jsx   # Настройки профиля
│   ├── context/AuthContext.js
│   ├── App.jsx
│   └── index.js
├── package.json
└── Dockerfile
```

### 3.2 API Контракт (что ждет фронт)
Бэкенд ждет токен в заголовке: `Authorization: Bearer <JWT>`.

**Фрагменты:**
- `GET /api/v1/fragments?limit=20&offset=0&privacy=private`
- `POST /api/v1/fragments` (body: `{text, source, privacy}`)
- `DELETE /api/v1/fragments/{id}`

**Поиск (FTS5):**
- `GET /api/v1/fragments/search?q=query`

**Люди (NEW):**
- `GET /api/v1/people` — список людей
- `GET /api/v1/people/{id}` — детали + связанные фрагменты

**Настройки:**
- `GET /api/v1/settings/exit`
- `PUT /api/v1/settings/exit` (body: `{export_format, auto_delete_days}`)

### 3.3 Важные нюансы для фронта:
- **Обработка векторов:** `semantic_vector` приходит строкой JSON, нужно парсить.
- **Даты:** `created_at` в формате ISO, использовать `new Date().toLocaleString()`.
- **Privacy:** При создании фрагмента обязательно предусмотреть select (private/trusted/public).

---

## 4. Бэкенд: Что осталось допилить (P1/P2)

### P1 (Важно, но не блокирует фронт):
1. **FTS5 Экранирование:** В `app/database.py::search_fragments()` спецсимволы FTS5 (`"`, `'`, `*`, `AND`) не экранируются. Нужно добавить санитайзер.
2. **Транзакции:** В `upsert_pattern()` нет транзакции — возможна гонка данных.
3. **Async FFmpeg:** `transcribe_audio()` использует синхронный `subprocess.run`. При нагрузке вешает event loop. Заменить на `asyncio.create_subprocess_exec`.

### P2 (Рефакторинг):
1. **Разделить `handle_callbacks`:** Огромная функция в `bot/main.py` (600+ строк). Вынести логику в отдельные хендлеры.
2. **Объединить JWT:** Убрать дублирование `make_jwt` (в боте) и `create_access_token` (в app).
3. **People Edges:** В спеке Спринта 3 был `app/routers/people.py`. Его еще нет, нужно создать (или ты создашь вместе с фронтом?).

---

## 5. Докеризация (Sprint 3 Goal)

### 5.1 `frontend/Dockerfile`
Используй многоступенчатую сборку (Node -> Nginx):
```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
# COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 5.2 `docker-compose.yml` (обновленный)
```yaml
version: '3.8'
services:
  api:
    build: /root/LabDoctorM/protocol
    command: uvicorn main:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    env_file:
      - /root/LabDoctorM/protocol/.env
    volumes:
      - /root/LabDoctorM/protocol/data:/app/data
    restart: unless-stopped

  frontend:
    build: /root/LabDoctorM/protocol/frontend
    ports:
      - "3000:80"
    environment:
      - REACT_APP_API_URL=http://localhost:8000/api/v1
    depends_on:
      - api
    restart: unless-stopped

  bot:
    build: /root/LabDoctorM/protocol
    command: python -m bot.main
    env_file:
      - /root/LabDoctorM/protocol/.env
    depends_on:
      - api
    restart: unless-stopped
```

---

## 6. Чеклист готовности к Спринту 3

- [x] Проект в `/root/LabDoctorM/protocol/`
- [x] Systemd сервисы на venv
- [x] Баг поиска в боте пофикшен
- [x] `requirements.txt` полный (aiogram, slowapi и т.д.)
- [ ] **Фронтенд скелет готов** (ЗавЛаб, твой ход!)
- [ ] `app/routers/people.py` создан
- [ ] FTS5 спецсимволы экранируются
- [ ] Тесты интеграционные пройдены (`pytest tests/ -v`)

---

## 7. Команды для ЗавЛаба (после создания скелета)

### Запуск фронта (dev):
```bash
cd /root/LabDoctorM/protocol/frontend
npm install
REACT_APP_API_URL=http://localhost:8000/api/v1 npm start
```

### Сборка и докер:
```bash
cd /root/LabDoctorM/protocol
docker-compose up --build -d
```

---

**ЗавЛаб, жду твой скелет! Как закинешь фронт в папку — погнали рестартить сервисы и тестить! 🚀**
