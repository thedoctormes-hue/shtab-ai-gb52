# OpenClawBox — LLM Агрегатор

## Стек
- **Python 3.10+** (aiogram 3.x, FastAPI)
- **PostgreSQL** для users/usage
- **Redis** для rate-limit state

## Deploy
```bash
pip install -r requirements.txt
cp .env.example .env
python bot/main.py
```

## Система провайдеров
- `app/providers/groq.py`
- `app/providers/mistral.py`
- `app/providers/google.py`
- `app/providers/together.py`
- `app/providers/cohere.py`
- `app/providers/openrouter.py`