---
name: openclaw_architecture
description: OpenClawBox freemium tier — агрегатор официальных бесплатных LLM API
type: project
---

# 🦀 OpenClawBox Freemium Architecture

*Агрегатор официальных бесплатных LLM API с автоматическим переключением*

---

## 🎯 Концепция

OpenClawBox — **прозрачный агрегатор** бесплатных LLM провайдеров:
- ✅ Агрегирует только официальные бесплатные тиры
- ✅ Автоматическое переключение при исчерпании лимитов
- ✅ Монетизация через платный tier
- ❌ Без перехвата чужих токенов (ToS compliant)

---

## 📊 Free Tier Providers & Limits

### 1. Google AI Studio (Gemini)
| Model | RPM | TPM (in) | TPM (out) | RPD | Notes |
|-------|-----|----------|-----------|-----|-------|
| Gemini 2.0 Flash | 15 | 1M | 2M | 1500 | 🔥 Лучший баланс |
| Gemini 2.5 Flash | 10 | 400K | 1M | 1000 | Новая модель |
| Gemini 1.5 Flash | 15 | 400K | 2M | 1500 | Стабильная |

**Free tier**: Active project, без карты  
**Upgrade**: Tier 1 ($250 cap)

### 2. Groq
| Model | RPM | TPM | RPD | Notes |
|-------|-----|-----|-----|-------|
| llama-3.1-8b-instant | 30 | 6K | 14.4K | 🦙 Самый быстрый |
| llama-3.3-70b-versatile | 30 | 12K | 1K | 🦙 70B качество |
| qwen/qwen3-32b | 60 | 6K | 1K | 🔥 Qwen3 |
| openai/gpt-oss-120b | 30 | 8K | 1K | 🆕 Open Source |

### 3. OpenRouter :free Models
| Model | Approx RPM | Notes |
|-------|------------|-------|
| meta-llama/llama-3.2-3b:free | 5-10 | Быстрая, мало токенов |
| google/gemini-flash-1.5:free | 5-10 | Качество Google |
| mistralai/mistral-7b:free | 5-10 | Хорош для кода |

### 4. Together AI
| Limit | Value |
|-------|-------|
| Free credits | $50-100 (промо) |
| Rate limits | Dynamic (рост при использовании) |

### 5. Mistral AI (Open Source)
| Model | License | Notes |
|-------|---------|-------|
| Mistral 7B | Apache 2.0 | Бесплатно |
| Mathstral 7B | Apache 2.0 | Математика |
| Codestral Mamba 7B | Apache 2.0 | Код |

---

## ⚠️ 6 Слабых Мест Архитектуры

1. **Региональные блокировки** — Google недоступен в RU, CN, IR
   - **Решение**: Детекция IP + fallback на Groq/OpenRouter

2. **Непредсказуемые лимиты** — Together AI динамические
   - **Решение**: Жесткие буферы + backoff экспоненциальный

3. **Отсутствие circuit breaker** — постоянные попытки недоступных
   - **Решение**: 3 ошибки подряд → cooldown 5 минут

4. **Нет кэширования** — дублирующие запросы льют лимиты
   - **Решение**: Redis кэш + semantic dedup (sentence-transformers)

5. **Один аккаунт = один лимит** — нет load balancing
   - **Решение**: Pool токенов с ротацией при исчерпании

6. **Не учитывается размер ответа** — TPM важнее RPM
   - **Решение**: Трекинг TPM отдельно + резерв 20%

---

## 🏗️ Архитектура с Защитой От Слабых Мест

```
┌─────────────────────────────────────────────────────┐
│              OpenClawBox Core                       │
└─────────────────────────────────────────────────────┘
           │    │    │    │    │    │    │    │
           ▼    ▼    ▼    ▼    ▼    ▼    ▼    ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
    │Pool Tier1 │ │Pool Tier2 │ │Pool Tier3 │ │...      │
    │(Google)   │ │(Groq)     │ │(OpenRout)│ │         │
    └──────────┘ └──────────┘ └──────────┘ └──────────┘
           │    │    │    │    │    │    │    │
           ▼    ▼    ▼    ▼    ▼    ▼    ▼    ▼
    ┌─────────────────────────────────────────────────┐
    │         Load Balancer + Circuit Breaker         │
    │  - Region check                                    │
    │  - Token pool rotation                             │
    │  - Exponential backoff                             │
    │  - Semantic cache                                    │
    └─────────────────────────────────────────────────┘
```

---

## 🛠️ Rate Limit Tracker (улучшенный)

```python
class RateLimitTracker:
    def __init__(self):
        self.state = {
            'google': {'rpm': 15, 'tpm': 1_000_000, 'rpd': 1500, 'cooldown': 0},
            'groq': {'rpm': 30, 'tpm': 6_000, 'rpd': 14400, 'cooldown': 0},
            'openrouter': {'rpm': 5, 'tpm': 1000, 'rpd': 100, 'cooldown': 0},
        }
        self.counters = defaultdict(lambda: {'rpm': 0, 'tpm': 0, 'rpd': 0, 'errors': 0})
        self.region_blocked = set()  # RU, CN, IR если Google недоступен
    
    def select_provider(self, tokens_needed):
        now = time.time()
        
        # Фильтруем cooldown и регион
        available = [p for p in self.state 
                     if self.state[p]['cooldown'] < now 
                     and p not in self.region_blocked]
        
        # Сортируем по доступности TPM
        available.sort(key=lambda p: self.state[p]['tpm'] - self.counters[p]['tpm'], reverse=True)
        
        for provider in available:
            # Резерв 20% + проверка
            if (self.counters[provider]['tpm'] + tokens_needed * 1.2 
                <= self.state[provider]['tpm']):
                return provider
        
        return 'openrouter'  # Last resort
```

---

## 💰 Монетизация (Paid Tier)

| Tier | Price | Requests/Day | Tokens | Features |
|------|-------|--------------|--------|----------|
| Free | $0 | 2K | 2M | 5 провайдеров |
| Pro | $9.99 | 10K | 15M | Priority, нет cooldown |
| Team | $29.99 | 100K | 150M | Dedicated, SLA 99.9% |

---

## 📁 Структура Проекта

```
openclawbox/
├── core/
│   ├── router.py          # Алгоритм выбора провайдера
│   ├── tracker.py         # Трекер лимитов + cooldown
│   ├── circuit.py         # Circuit breaker
│   └── cache.py           # Semantic cache
├── providers/
│   ├── google.py          # Gemini API
│   ├── groq.py            # Groq API
│   ├── openrouter.py      # :free models
│   └── together.py        # Dynamic limits
├── tokens/
│   └── pool.json          # Пул токенов с ротацией
└── tiers/
    ├── free.py            # Freemium
    └── paid.py            # Premium
```

---

## 🔗 Источники

- [Google Gemini Rate Limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- [Groq Rate Limits](https://console.groq.com/docs/rate-limits)
- [OpenRouter :free Models](https://openrouter.ai/docs/guides/routing/model-variants/free)
- [Together AI Rate Limits](https://docs.together.ai/docs/rate-limits)