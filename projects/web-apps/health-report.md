# 🏥 Health Report — /projects/web-apps/

**Дата**: 2026-05-02
**Автор**: КотОлизатОр

---

## 📊 Сводка

| Проект | Тип | Тесты | Линтеры | Доки | .gitignore | Статус |
|--------|-----|--------|---------|------|------------|---------|
| os-lab-api | Python API | ❌ | ❌ | ❌ | ❌ | 🔴 Критично |
| shtab-ai-gb52 | Static Site | ❌ | ❌ | ❌ | ❌ | 🟡 Минимум |
| syncthing-dashboard | React SPA | ❌ | ⚠️ (только скрипт) | ✅ | ❌ | 🟡 Есть issues |

---

## 1️⃣ os-lab-api

**Путь**: `/root/LabDoctorM/projects/web-apps/os-lab-api/`
**Тип**: FastAPI (Python)

### ✅ Что есть
- Рабочий FastAPI сервер (порт 8002)
- CORS настроен
- requirements.txt с зависимостями

### ❌ Чего нет
- **Тесты**: нет вообще
- **Линтеры**: нет (ruff, flake8, pytest)
- **README.md**: нет описания
- **.gitignore**: нет (venv/, __pycache__/ могут попасть в гит)
- **Обработка ошибок**: ping_server просто молчит при ошибках
- **Конфиги**: серверы захардкожены в коде (warsaw, florida, rf-proxy)

### 🔧 Рекомендации
1. Добавить тесты (pytest)
2. Настроить ruff линтер
3. Создать README.md
4. Добавить .gitignore
5. Вынести конфиги серверов в .env

---

## 2️⃣ shtab-ai-gb52

**Путь**: `/root/LabDoctorM/projects/web-apps/shtab-ai-gb52/`
**Тип**: Статический сайт (сборка)

### ✅ Что есть
- Собранный HTML + ассеты (JS/CSS)
- Сайт работает по адресу: `https://shtab-ai.ru`

### ❌ Чего нет
- **Исходники**: только билд (нет исходного кода React/Vue/etc.)
- **Тесты**: нет
- **Линтеры**: нет
- **README.md**: нет
- **.gitignore**: нет

### 🔧 Рекомендации
1. Найти исходники (возможно в другом месте)
2. Если это только билд — создать отдельный репозиторий для исходников
3. Добавить README с описанием структуры

---

## 3️⃣ syncthing-dashboard

**Путь**: `/root/LabDoctorM/projects/web-apps/syncthing-dashboard/`
**Тип**: React + TypeScript + Vite

### ✅ Что есть
- Полноценный React проект (TypeScript)
- README.md с описанием ✅
- Скрипт линтера в package.json
- Tailwind CSS настроен
- Vite сборщик

### ❌ Чего нет
- **Тесты**: нет (jest, vitest не найдены)
- **ESLint конфиг**: есть скрипт `npm run lint`, но нет `.eslintrc` или `eslint.config.js`
- **.gitignore**: нет — **node_modules/** и **dist/** не игнорируются!

### 🚨 Критические проблемы

#### 1. Секрет в коде!
В `vite.config.ts` захардкожен API ключ:
```typescript
headers: {
  'X-API-Key': 'kFLqDXU49vvssvfmSWDnktCdYLrzuKZD'
}
```
**Решение**: вынести в .env и использовать `process.env`

#### 2. Нет .gitignore
- `node_modules/` — 1000+ пакетов
- `dist/` — билд артефакты
- `tsconfig.tsbuildinfo` — временные файлы TypeScript

### 🔧 Рекомендации
1. **СРОЧНО**: вынести API ключ в .env
2. Добавить .gitignore
3. Создать `eslint.config.js`
4. Добавить тесты (vitest + react-testing-library)
5. Добавить GitHub Actions для CI/CD

---

## 🎯 Общие проблемы всех проектов

1. **Нет ни одного теста** во всех трёх проектах
2. **Нет .gitignore** нигде
3. **Нет линтеров** (кроме упоминания скрипта в syncthing-dashboard)
4. **Документация** только в одном проекте из трёх

---

## 📋 План исправления (приоритетный)

### Высокий приоритет (🔥 Сейчас)
- [ ] Вынести API ключ из `syncthing-dashboard/vite.config.ts` в .env
- [ ] Добавить .gitignore во все проекты
- [ ] Настроить ESLint для syncthing-dashboard

### Средний приоритет
- [ ] Добавить тесты в os-lab-api (pytest)
- [ ] Добавить тесты в syncthing-dashboard (vitest)
- [ ] Создать README для os-lab-api и shtab-ai-gb52

### Низкий приоритет
- [ ] Настроить CI/CD (GitHub Actions)
- [ ] Добавить линтеры (ruff для Python, eslint для React)

---

**Итог**: 
- 🔴 **1 проект** в критическом состоянии (os-lab-api)
- 🟡 **2 проекта** требуют доработки (shtab-ai-gb52, syncthing-dashboard)
- 🚨 **1 критическая уязвимость** (секрет в коде)
