# Team Dashboard Center (TDC)
## DoctorM&Ai Laboratory

**Статус:** 💻 В разработке (приоритет проекта)
**Текущий этап:** Активная разработка
**Дата начала:** 2026-05-01

---

## 📋 ОПИСАНИЕ ПРОЕКТА

Team Dashboard Center (TDC) — это централизованный мониторинг и управление всей инфраструктурой лаборатории DoctorM&Ai.

### Ключевые функции:
- Многосерверный мониторинг (Warsaw, Florida, RF Proxy)
- Управление Syncthing (папки, резан, статус)
- File Browser для просмотра файлов ~/.qwen
- Upload файлов в синхронизируемую папку
- Share ссылки на файлы

---

## 🏗 ТЕХНИЧЕСКАЯ АРХИТЕКТУРА

### Фронтенд
- **Технологии:** React + TypeScript + Vite
- **Стиль:** Tailwind CSS (glass-morphism)
- **Иконки:** Lucide React
- **Расположение:** `/root/LabDoctorM/syncthing-dashboard/`

### Бекенд
- **File Browser API:** Python HTTPServer (порт 8001)
- **Syncthing API:** REST API через nginx reverse proxy
- **Серверы:** systemd сервисы на всех 3 серверах

### Деплой
- **URL:** http://185.138.90.150/dashboard-react/
- **Папка:** /var/www/html/dashboard-react/dist/
- **Обновление:** `npm run build && rsync`

---

## 🎯 ТЕКУЩИЕ ЗАДАЧИ

| Задача | Статус | Приоритет |
|--------|--------|-----------|
| File Browser с Upload | ✅ Готово | Высокий |
| Share ссылки на файлы | ✅ Готово | Высокий |
| Copy Link функция | ✅ Готово | Средний |
| Multi-server мониторинг | ✅ Готово | Высокий |
| Telegram интеграция | ⏳ Требуется | Низкий |
| Мобильная адаптация | ✅ Готово | Средний |

---

## 🔌 API ЭНДПОИНТЫ

### Файлы
```
GET  /api/files           - Список файлов из ~/.qwen
GET  /api/file/{path}     - Чтение файла
POST /api/upload          - Загрузка файла в /var/syncthing/Sync
```

### Syncthing
```
GET  /api/syncthing/system/status    - Статус системы
GET  /api/syncthing/folder           - Список папок
GET  /api/syncthing/connections      - Подключения к устройствам
```

---

## 📱 МОБИЛЬНАЯ ВЕРСИЯ

**Адаптации:**
- Карточки вместо таблиц
- Кнопки View/Download/Share на каждой карточке
- Preview с Download/Copy Link
- Upload через input[type=file]

---

## 🚀 ДЕПЛОЙ

```bash
# Сборка
npm run build

# Деплой
rm -rf /var/www/html/dashboard-react/dist/*
cp -r dist/* /var/www/html/dashboard-react/dist/

# Перезагрузка сервисов
systemctl restart filebrowser
nginx -s reload
```

---

## 🧠 КОНТЕКСТ ДЛЯ НОВЫХ СЕССИЙ

**Точки входа:**
1. App.tsx — главный компонент с табами
2. FileBrowser.tsx — файловый браузер
3. ServerStatus.tsx — статус серверов
4. useSyncthingData.ts — хук данных

**Ключевые файлы:**
- `/root/LabDoctorM/syncthing-dashboard/src/App.tsx`
- `/root/LabDoctorM/syncthing-dashboard/src/components/FileBrowser.tsx`
- `/root/LabDoctorM/file_browser_api.py`

---

## 🔄 ИНТЕГРАЦИИ

- **Syncthing** — синхронизация файлов между серверами
- **nginx** — reverse proxy + BasicAuth
- **Telegram Bot (kotolizator)** — через /f/ эндпоинт
- **Система памяти** — ~/.qwen/memory/

---

*Документ поддерживается автоматически. Последнее обновление: 2026-05-01*