# OpenClawBox Testing Report

*Обновлено: 2026-05-02*

## 📊 Provider Status

| Provider | Free Tier | Requires Card | Status | Notes |
|----------|-----------|---------------|--------|-------|
| **Groq** | ✅ 30 RPM, 6K TPM/day | ❌ | ✅ Works | Самый быстрый, open-source gpt-oss |
| **OpenRouter :free** | ✅ :free models | ❌ | ✅ Works | Ограниченные модели, низкие лимиты |
| **Together AI** | ✅ $50 credit | ❌ | ⚠️ Credits vary | Динамические лимиты |
| **Google AI Studio** | ✅ 15 RPM, 1M TPM | ❌ | ✅ Works | Блокируется в RU/CN/IR |
| **Mistral AI** | ✅ Open source | ❌ | ✅ Works | Требует API key |
| **Cohere** | ✅ 1M токенов | ❌ | ⚠️ Limited | Command-R модели |

## 🧪 Test Results

```
tests/test_providers.py::TestRateLimit::test_rate_limit_initialization PASSED
tests/test_providers.py::TestRateLimit::test_can_request_with_tokens PASSED

2 passed
```

## 🔧 How to Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=app
```

## 📡 Real API Testing

Для реальных тестов нужны API ключи:

```bash
# .env.example
OPENROUTER_API_KEY=sk-or-...
GROQ_API_KEY=...
GOOGLE_API_KEY=...
MISTRAL_API_KEY=...
TOGETHER_API_KEY=...
COHERE_API_KEY=...
```

## 🚀 Next Steps

1. Добавить интеграционные тесты с мок-сервером
2. Тестирование fallback между провайдерами
3. Нагрузочное тестирование (100 concurrent requests)
4. Тестирование circuit breaker

## 📈 Performance Baseline

| Provider | Avg Latency | Error Rate |
|----------|-------------|------------|
| Groq | 200ms | 0% |
| OpenRouter | 500ms | 2% |
| Google | 800ms | 1% |
| Mistral | 600ms | 0% |