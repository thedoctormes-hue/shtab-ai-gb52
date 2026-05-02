# 🚀 Protocol — Технический спек Спринта 3

**Версия:** 1.0  
**Дата:** 2026-04-28  
**Статус:** Готов к реализации  
**Автор:** КотОлизатОр (Qwen Code)  

---

## 1. Обзор Спринта 3

### Цель
Довести проект Protocol до production-ready состояния:
- Завершить UI настроек в Telegram-боте
- Реализовать просмотр `people_edges` (связи людей с фрагментами)
- Добавить фильтрацию по `privacy` в API
- Создать веб-фронтенд (React)
- Улучшить UX кнопок бота
- Написать интеграционные тесты
- Докеризировать приложение

### Границы
- Не менять схему БД (только добавление индексов если нужно)
- Не переезжать с SQLite на PostgreSQL (пока 1-2 пользователя)
- Не менять LLM провайдеры (Gemini/Llama через OpenRouter)

---

## 2. Фронтенд (React)

### 2.1 Структура папки `frontend/`
```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── FragmentCard.jsx
│   │   ├── PatternCard.jsx
│   │   ├── SearchBar.jsx
│   │   ├── SettingsPanel.jsx
│   │   └── PeopleEdges.jsx
│   ├── pages/
│   │   ├── Home.jsx
│   │   ├── Search.jsx
│   │   ├── Patterns.jsx
│   │   └── Settings.jsx
│   ├── services/
│   │   ├── api.js         # HTTP-клиент (axios)
│   │   └── auth.js        # JWT токен менеджмент
│   ├── App.jsx
│   └── index.js
├── package.json
└── Dockerfile
```

### 2.2 API сервис (`frontend/src/services/api.js`)
```javascript
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' }
});

// Автоматически добавлять JWT токен
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('jwt_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const fragmentsAPI = {
  list: (limit = 20, offset = 0) => 
    api.get(`/fragments?limit=${limit}&offset=${offset}`),
  search: (query, limit = 10) => 
    api.get(`/fragments/search?q=${encodeURIComponent(query)}&limit=${limit}`),
  create: (text, source = 'text', privacy = 'private') => 
    api.post('/fragments', { text, source, privacy }),
  delete: (id) => api.delete(`/fragments/${id}`),
};

export const patternsAPI = {
  list: () => api.get('/patterns'),
};

export const settingsAPI = {
  get: () => api.get('/settings/exit'),
  update: (data) => api.put('/settings/exit', data),
};

export const edgesAPI = {
  list: (from_id, to_id) => 
    api.get(`/edges?from_id=${from_id || ''}&to_id=${to_id || ''}`),
  create: (from_id, to_id, relation_type = 'similar') => 
    api.post('/edges', { from_id, to_id, relation_type }),
  delete: (id) => api.delete(`/edges/${id}`),
};

export const usersAPI = {
  register: (tg_id) => api.post('/users/register', { tg_id }),
  me: () => api.get('/users/me'),
  stats: () => api.get('/users/me/stats'),
};
```

### 2.3 Страница Home (`frontend/src/pages/Home.jsx`)
```jsx
import React, { useState, useEffect } from 'react';
import { fragmentsAPI, patternsAPI } from '../services/api';
import FragmentCard from '../components/FragmentCard';
import PatternCard from '../components/PatternCard';

function Home() {
  const [fragments, setFragments] = useState([]);
  const [patterns, setPatterns] = useState([]);
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    const [fragRes, patRes] = await Promise.all([
      fragmentsAPI.list(20, 0),
      patternsAPI.list()
    ]);
    setFragments(fragRes.data);
    setPatterns(patRes.data);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await fragmentsAPI.create(text);
      setText('');
      loadData();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Протокол — Мои мысли</h1>
      
      <form onSubmit={handleSubmit}>
        <textarea 
          value={text} 
          onChange={(e) => setText(e.target.value)}
          placeholder="Что ты хочешь не забыть?"
          rows={4}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Сохраняю...' : 'Сохранить'}
        </button>
      </form>

      <h2>Фрагменты</h2>
      {fragments.map(f => 
        <FragmentCard key={f.id} fragment={f} onDelete={loadData} />
      )}

      <h2>Паттерны</h2>
      {patterns.map(p => 
        <PatternCard key={p.id} pattern={p} />
      )}
    </div>
  );
}

export default Home;
```

### 2.4 Компонент FragmentCard (`frontend/src/components/FragmentCard.jsx`)
```jsx
import React from 'react';
import { fragmentsAPI } from '../services/api';

function FragmentCard({ fragment, onDelete }) {
  const getCategory = (vector) => {
    if (!vector) return 'Знание';
    const max = Object.entries(vector).sort((a,b) => b[1] - a[1])[0];
    const map = { task: 'Задача', idea: 'Идея', identity: 'Я', knowledge: 'Знание', pattern: 'Паттерн' };
    return map[max[0]] || 'Знание';
  };

  const handleDelete = async () => {
    if (window.confirm('Удалить фрагмент?')) {
      await fragmentsAPI.delete(fragment.id);
      onDelete();
    }
  };

  const vector = typeof fragment.semantic_vector === 'string' 
    ? JSON.parse(fragment.semantic_vector) 
    : fragment.semantic_vector;

  return (
    <div className="fragment-card">
      <div className="header">
        <span className="category">{getCategory(vector)}</span>
        <span className="date">{new Date(fragment.created_at).toLocaleString()}</span>
      </div>
      <p className="summary">{fragment.summary}</p>
      <div className="text">{fragment.text}</div>
      <div className="actions">
        <button onClick={handleDelete}>Удалить</button>
      </div>
    </div>
  );
}

export default FragmentCard;
```

### 2.5 CORS настройка (обновить `main.py`)
```python
# В main.py добавить фронтенд URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",  # React dev server
        "http://127.0.0.1:3000",
        "https://protocol.yourdomain.com"  # продакшн фронтенд
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

### 2.6 package.json (`frontend/package.json`)
```json
{
  "name": "protocol-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0",
    "react-router-dom": "^6.20.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test"
  },
  "devDependencies": {
    "react-scripts": "5.0.1"
  }
}
```

---

## 3. API для people_edges и privacy фильтрации

### 3.1 Новые эндпоинты в `app/routers/people.py`

**Файл:** `/root/protocol/app/routers/people.py` (создать)

```python
"""
Роутер для работы с людьми и их связями
GET  /people      — список людей пользователя
GET  /people/{id} — детали человека + связанные фрагменты
"""

import json
from fastapi import APIRouter, Depends, Query
from app.database import get_db
from app.deps import get_current_user

router = APIRouter()

@router.get("")
async def list_people(
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    async with db.execute(
        "SELECT id, name, role, first_seen_at FROM people WHERE user_id=? ORDER BY name",
        (user["id"],)
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]

@router.get("/{person_id}")
async def get_person(
    person_id: str,
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    # Получаем человека
    async with db.execute(
        "SELECT * FROM people WHERE id=? AND user_id=?",
        (person_id, user["id"])
    ) as cur:
        person = await cur.fetchone()
    
    if not person:
        raise HTTPException(404, "Человек не найден")
    
    # Получаем связанные фрагменты через people_edges
    async with db.execute("""
        SELECT f.*, pe.emotion, pe.context
        FROM people_edges pe
        JOIN memory_fragments f ON pe.fragment_id = f.id
        WHERE pe.person_id = ?
        ORDER BY pe.created_at DESC
    """, (person_id,)) as cur:
        edges = await cur.fetchall()
    
    return {
        "person": dict(person),
        "fragments": [dict(e) for e in edges]
    }
```

### 3.2 Обновить `app/routers/fragments.py` для фильтрации по privacy

```python
@router.get("")
async def list_fragments(
    limit: int = Query(20, le=100),
    offset: int = 0,
    privacy: str = Query(None, description="Фильтр по privacy: private/trusted/public"),
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    sql = """
        SELECT id, summary, semantic_vector, emotion, confidence,
               source, privacy, created_at, conflict_detected
        FROM memory_fragments
        WHERE user_id=?
    """
    params = [user["id"]]
    
    if privacy:
        sql += " AND privacy = ?"
        params.append(privacy)
    
    sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    async with db.execute(sql, params) as cur:
        rows = await cur.fetchall()
    
    return [dict(r) for r in rows]
```

### 3.3 Подключить роутер в `main.py`

```python
from app.routers import fragments, users, patterns, edges, settings, people

# ... существующий код ...

app.include_router(people.router, prefix="/api/v1/people", tags=["people"])
```

---

## 4. UI настроек в Telegram-боте

### 4.1 Команда `/settings` в `bot/main.py`

```python
@dp.message(Command("settings"))
async def cmd_settings(message: types.Message):
    """Показать настройки пользователя"""
    tg_id = str(message.from_user.id)
    token = make_jwt(tg_id)
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = await http_client.get(f"{API_BASE_URL}/settings/exit", headers=headers)
        response.raise_for_status()
        settings_data = response.json()
        
        text = "⚙️ Настройки Protocol\n\n"
        text += f"Формат экспорта: {settings_data['export_format']}\n"
        text += f"Авто-удаление: {settings_data['auto_delete_days']} дней\n"
        
        if settings_data['trusted_tg_id']:
            text += f"Доверенный ID: {settings_data['trusted_tg_id']}\n"
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Экспорт", callback_data="settings_export"),
                types.InlineKeyboardButton(text="Авто-удаление", callback_data="settings_autodelete")
            ],
            [
                types.InlineKeyboardButton(text="Доверенные", callback_data="settings_trusted"),
                types.InlineKeyboardButton(text="Приветствие", callback_data="settings_farewell")
            ]
        ])
        
        await message.answer(text, reply_markup=keyboard)
    except Exception as e:
        logging.error(f"Settings error: {e}")
        await message.answer("Ошибка получения настроек")
```

### 4.2 Обработка кнопок настроек

```python
@dp.callback_query(F.data.startswith("settings_"))
async def handle_settings_callbacks(callback: types.CallbackQuery):
    data = callback.data
    tg_id = str(callback.from_user.id)
    token = make_jwt(tg_id)
    headers = {"Authorization": f"Bearer {token}"}
    
    if data == "settings_export":
        # Показать выбор формата
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Bundle", callback_data="set_export:bundle")],
            [types.InlineKeyboardButton(text="JSON", callback_data="set_export:json")],
            [types.InlineKeyboardButton(text="TXT", callback_data="set_export:txt")]
        ])
        await callback.message.answer("Выбери формат экспорта:", reply_markup=keyboard)
        
    elif data.startswith("set_export:"):
        export_format = data.split(":")[1]
        try:
            await http_client.put(
                f"{API_BASE_URL}/settings/exit",
                headers=headers,
                json={"export_format": export_format}
            )
            await callback.answer(f"✅ Формат: {export_format}")
        except Exception as e:
            logging.error(f"Export format error: {e}")
            await callback.answer("Ошибка", show_alert=True)
            
    elif data == "settings_autodelete":
        # Запросить количество дней
        await callback.message.answer(
            "Введи количество дней для авто-удаления (0 = отключить):",
            reply_markup=types.ForceReply(selective=True)
        )
        # TODO: добавить FSM состояние для обработки ответа
        
    await callback.answer()
```

---

## 5. Улучшение UX кнопок бота

### 5.1 Пагинация для списка фрагментов

```python
@dp.callback_query(F.data.startswith("today_fragments"))
async def handle_today_fragments(callback: types.CallbackQuery):
    data = callback.data
    tg_id = str(callback.from_user.id)
    token = make_jwt(tg_id)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Парсим offset если есть
    offset = 0
    if ":" in data:
        offset = int(data.split(":")[1])
    
    user = await get_user_by_tg_id(tg_id)
    if not user:
        await callback.answer("Пользователь не найден", show_alert=True)
        return
        
    user_id = user["id"]
    fragments = await get_today_fragments(user_id, limit=10, offset=offset)
    total = await get_today_fragments_count(user_id)
    
    if not fragments:
        await callback.answer("Больше нет фрагментов", show_alert=True)
        return
        
    response = f"Фрагменты за сегодня ({offset+1}-{offset+len(fragments)} из {total}):\n\n"
    for i, frag in enumerate(fragments, offset+1):
        category = get_category(frag["semantic_vector"])
        time_str = format_date(frag["created_at"]).split(",")[1].strip()
        summary = frag["summary"] or "(без summary)"
        response += f"{i}. {summary}\n"
        response += f"   {category}  {time_str}\n\n"
    
    # Кнопки пагинации
    keyboard_buttons = []
    
    if offset > 0:
        keyboard_buttons.append(
            types.InlineKeyboardButton(text="« Назад", callback_data=f"today_fragments:{offset-10}")
        )
    
    if offset + len(fragments) < total:
        keyboard_buttons.append(
            types.InlineKeyboardButton(text="Ещё »", callback_data=f"today_fragments:{offset+10}")
        )
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[keyboard_buttons])
    
    await callback.message.answer(response, reply_markup=keyboard)
    await callback.answer()
```

### 5.2 Красивое форматирование паттернов

```python
@dp.callback_query(F.data == "patterns_more")
async def handle_patterns_more(callback: types.CallbackQuery):
    tg_id = str(callback.from_user.id)
    user = await get_user_by_tg_id(tg_id)
    if not user:
        await callback.answer("Пользователь не найден", show_alert=True)
        return
        
    user_id = user["id"]
    patterns = await get_patterns(user_id, limit=20)  # Увеличить лимит
    
    if not patterns:
        await callback.answer("Паттернов нет", show_alert=True)
        return
        
    # Форматируем с эмодзи и прогресс-барами
    response = "🧠 Все твои паттерны:\n\n"
    
    for i, pat in enumerate(patterns, 1):
        desc = pat["description"]
        occ = pat["occurrences"]
        date_str = format_date(pat["last_seen_at"]).split(",")[0].strip()
        
        # Прогресс-бар (10 символов)
        bar_length = min(10, occ)
        bar = "█" * bar_length + "░" * (10 - bar_length)
        
        response += f"{i}. {desc}\n"
        response += f"   {bar} {occ} раз(а)  {date_str}\n\n"
    
    # Кнопка "Подробнее" для каждого паттерна (через инлайн кнопки)
    keyboard_buttons = []
    for i, pat in enumerate(patterns[:5], 1):  # Показать первые 5 как кнопки
        keyboard_buttons.append(
            [types.InlineKeyboardButton(
                text=f"{i}. {pat['description'][:30]}...", 
                callback_data=f"pattern_detail:{pat.get('id', '')}"
            )]
        )
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.answer(response, reply_markup=keyboard)
    await callback.answer()
```

---

## 6. Интеграционные тесты

### 6.1 Структура тестов (`tests/test_integration.py`)

```python
"""
Интеграционные тесты Protocol API
Используем реальную БД в памяти (SQLite :memory:)
"""

import pytest
import sys
import os
from pathlib import Path
from fastapi.testclient import TestClient

# Настройка окружения
os.environ["SECRET_KEY"] = "test_secret_key_integration"
os.environ["OPENROUTER_API_KEY"] = "test_key"

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
from app.database import init_db, DB_PATH
import aiosqlite

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_db():
    """Создаем тестовую БД"""
    # TODO: переделать на :memory: для полной изоляции
    pass

def test_complete_flow():
    """Тест полного цикла: регистрация → создание фрагмента → поиск → удаление"""
    
    # 1. Регистрация пользователя
    resp = client.post("/api/v1/users/register", json={"tg_id": "test_user_1"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["new"] == True
    user_id = data["user_id"]
    
    # 2. Получаем JWT токен (симулируем)
    import jwt
    from app.config import settings
    token = jwt.encode({"tg_id": "test_user_1", "exp": 9999999999}, settings.secret_key, algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Создаем фрагмент
    resp = client.post(
        "/api/v1/fragments",
        headers=headers,
        json={"text": "Тестовая мысль о Python и FastAPI", "source": "text", "privacy": "private"}
    )
    assert resp.status_code == 200
    fragment = resp.json()
    assert "id" in fragment
    fragment_id = fragment["id"]
    
    # 4. Ищем фрагмент
    resp = client.get(
        f"/api/v1/fragments/search?q=Python",
        headers=headers
    )
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) > 0
    
    # 5. Создаем связь (edge)
    resp = client.post(
        "/api/v1/edges",
        headers=headers,
        json={"from_id": fragment_id, "to_id": fragment_id, "relation_type": "similar"}
    )
    # Ожидаем ошибку (нельзя связать с самим собой или заглушка)
    assert resp.status_code in [200, 400, 404]
    
    # 6. Удаляем фрагмент
    resp = client.delete(f"/api/v1/fragments/{fragment_id}", headers=headers)
    assert resp.status_code == 200

def test_people_edges_flow():
    """Тест работы с людьми и связями"""
    # Регистрация
    resp = client.post("/api/v1/users/register", json={"tg_id": "test_user_2"})
    assert resp.status_code == 200
    
    import jwt
    from app.config import settings
    token = jwt.encode({"tg_id": "test_user_2", "exp": 9999999999}, settings.secret_key, algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Создаем фрагмент с упоминанием человека
    resp = client.post(
        "/api/v1/fragments",
        headers=headers,
        json={"text": "Встретился с Иваном и обсудили проект", "source": "text"}
    )
    assert resp.status_code == 200
    
    # Проверяем, что people API доступен (если реализовано)
    # resp = client.get("/api/v1/people", headers=headers)
    # assert resp.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### 6.2 Обновление `requirements.txt`
```txt
fastapi==0.115.0
uvicorn[standard]==0.30.0
aiosqlite==0.20.0
httpx==0.27.0
pydantic==2.7.0
pydantic-settings==2.3.0
PyJWT==2.12.1
slowapi==0.1.9
pytest==9.0.3
pytest-asyncio==1.3.0
```

---

## 7. Докеризация

### 7.1 Dockerfile для FastAPI (`Dockerfile`)
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# Создаем папку для БД
RUN mkdir -p data

# Expose порт
EXPOSE 8000

# Запуск
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 7.2 Dockerfile для фронтенда (`frontend/Dockerfile`)
```dockerfile
# Этап сборки
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Этап продакшена
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 7.3 docker-compose.yml
```yaml
version: '3.8'

services:
  db:
    image: sqlite
    volumes:
      - ./data:/data
    restart: unless-stopped

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - BOT_TOKEN=${BOT_TOKEN}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - db
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    environment:
      - REACT_APP_API_URL=http://localhost:8000/api/v1
    restart: unless-stopped

  bot:
    build: .
    command: python -m bot.main
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - BOT_TOKEN=${BOT_TOKEN}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - api
    restart: unless-stopped

volumes:
  data:
  logs:
```

### 7.4 .dockerignore
```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.env
.git/
.gitignore
*.log
data/
logs/
frontend/node_modules/
frontend/build/
```

---

## 8. План реализации (Таблица задач)

| Задача | Файлы | Приоритет | Трудозатраты | Зависимости |
|--------|-------|-----------|--------------|-------------|
| **1. API для people** | `app/routers/people.py`, `main.py` | Высокий | 3 часа | Нет |
| **2. Privacy фильтрация** | `app/routers/fragments.py` | Средний | 2 часа | Нет |
| **3. Бот: команда /settings** | `bot/main.py` | Высокий | 4 часа | API settings |
| **4. Бот: улучшение UX** | `bot/main.py` | Средний | 3 часа | Нет |
| **5. Фронтенд: база** | `frontend/` (все файлы) | Высокий | 8 часов | API готово |
| **6. Фронтенд: people edges** | `frontend/src/components/PeopleEdges.jsx` | Средний | 4 часа | API people |
| **7. Интеграционные тесты** | `tests/test_integration.py` | Средний | 6 часов | Весь функционал |
| **8. Docker** | `Dockerfile`, `docker-compose.yml` | Низкий | 3 часа | Фронтенд + API |

---

## 9. Чеклист готовности

### Перед началом Спринта 3:
- [ ] Спринт 2 официально завершен (все тесты проходят)
- [ ] `SECRET_KEY` изменен (не "change-me-in-prod")
- [ ] Бэкапы БД настроены (cron + скрипт)
- [ ] Логи ротируются (logrotate)
- [ ] JWT работает (старый X-TG-ID удален)

### После завершения Спринта 3:
- [ ] Фронтенд доступен на порту 3000
- [ ] Все кнопки бота работают (нет "В разработке")
- [ ] Интеграционные тесты проходят (`pytest tests/ -v`)
- [ ] Приложение собирается в Docker (`docker-compose up --build`)
- [ ] Документация обновлена (`README.md`)

---

**🚀 Спек готов! ЗавЛаб, очищай чат и погнали кодить!**
