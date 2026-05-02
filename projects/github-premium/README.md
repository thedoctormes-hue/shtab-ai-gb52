# 🚀 GitHub Premium

Проект по созданию стильного корпоративного GitHub для LabDoctorM.

## 🌟 Что уже готово

| Компонент | Статус | Описание |
|-----------|--------|----------|
| 📋 STYLE_GUIDE.md | ✅ | Гайд по оформлению репозиториев |
| 🤖 Шаблоны README | ✅ | Telegram-боты, FastAPI, React, Landing |
| ⚙️ GitHub Actions | ✅ | CI/CD workflows для Python/React |
| 🐛 Issue Template | ✅ | Шаблон для баг-репортов |
| 📥 PR Template | ✅ | Шаблон для пулреквестов |
| 🛡️ Security Audit | ✅ | Отчёт по аудиту безопасности |

## 📂 Структура
```
github-premium/
├── README.md           # Этот файл
├── STYLE_GUIDE.md      # Гайд по оформлению
├── workflows/          # Готовые GitHub Actions
│   ├── python-app.yml
│   ├── node-app.yml
│   └── pages-deploy.yml
├── templates/          # Шаблоны README
│   ├── template-telegram-bot.md
│   ├── template-fastapi-app.md
│   ├── template-react-app.md
│   ├── template-landing.md
│   └── template-infrastructure.md
└── security-audit-report.md
```

## 🚀 Быстрый старт

```bash
# Скопировать шаблоны в новый репозиторий
cp -r templates/* /path/to/new/repo/
cp workflows/* /path/to/new/repo/.github/workflows/
```

## 🔧 GitHub Actions Workflows

### Python (FastAPI, боты)
```yaml
name: Python CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt ruff pytest
      - run: ruff check .
      - run: pytest
```

### React/Node.js
```yaml
name: Node.js CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20.x'
      - run: npm ci
      - run: npm run build
      - run: npm test
```

## 📋 Стандарты коммитов (Conventional Commits)
```
feat: новый функционал
fix: исправление бага
docs: изменения документации
chore: обслуживание
test: тесты
```

## 🤝 Contributing

1. Форкнуть репозиторий
2. Создать ветку `feature/имя-фичи`
3. Внести изменения
4. Создать Pull Request

---

> **LabDoctorM — ЗавЛаб Безумный Доктор** ⚡
> 
> Premium GitHub setup for infrastructure that prints money.