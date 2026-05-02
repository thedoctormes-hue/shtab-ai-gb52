# 📊 Dashboard React — Инструкция пользователя

## Доступ к дашборду

| Окружение | URL |
|-----------|-----|
| Локальный | http://localhost/dashboard-react/ |
| Продакшен | http://dashboard.shtab-ai.ru/dashboard-react/ |

## Быстрый старт

1. Откройте один из URL выше в браузере
2. Дашборд автоматически загрузит данные из API backlog
3. Используйте интерактивные элементы для навигации

## API backlog

```
GET http://localhost/api/backlog/evolution_backlog.json
```

### Структура данных

`evolution_backlog.json` содержит массив задач в формате:
```json
[
  {
    "id": "TASK-001",
    "title": "Название задачи",
    "status": "todo|in-progress|done",
    "priority": "low|medium|high|critical",
    "assignee": "username"
  }
]
```

## Стек технологий

| Компонент | Технология |
|-----------|------------|
| Frontend | React + Vite |
| Стилизация | Tailwind CSS |
| Сервер | nginx |
| Данные | JSON (REST API) |

## Разработка

### Установка зависимостей
```bash
npm install
```

### Локальная разработка
```bash
npm run dev
# Откройте http://localhost:5173
```

### Сборка
```bash
npm run build
# Артефакты попадут в /dist
```

### Деплой
```bash
npm run build && rsync -av dist/ /var/www/dashboard-react/
```

## Структура проекта

```
dashboard-react/
├── src/
│   ├── components/    # UI компоненты
│   ├── pages/         # Страницы
│   └── api/           # API клиент
├── public/            # Статические файлы
└── dist/              # Готовая сборка
```

## FAQ

**Q: Дашборд не загружает данные?**  
A: Проверьте доступность API: `curl http://localhost/api/backlog/evolution_backlog.json`

**Q: Как добавить новый виджет?**  
A: Создайте компонент в `src/components/` и подключите в `src/App.jsx`

**Q: Ошибки при сборке?**  
A: Удалите `node_modules` и `package-lock.json`, затем выполните `npm install`