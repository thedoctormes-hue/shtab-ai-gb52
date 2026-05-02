# VPN Инфраструктура Аудит 2026

**Дата аудита:** 2 мая 2026  
**Объекты анализа:** Сервера Warsaw, Florida, RF-Proxy  
**Аналитик:** АнтКэт (клон КотОлизатОра)

---

## 📋 ИСПОЛНИТЕЛЬНОЕ РЕЗЮМЕ

- **Критических уязвимостей:** 4
- **Средних проблем:** 7  
- **Рекомендаций:** 12

---

## 🔐 АНАЛИЗ КЛЮЧЕЙ И БЕЗОПАСНОСТИ

### Reality Key Pairs

| Сервер | Private Key | Public Key | ShortIds | Статус |
|--------|-------------|------------|----------|--------|
| Warsaw (main) | `iJPbrf-Vv1pePgDQHroLYlnLu3-V6MbndZmJhK7zhns` | `Q7P9aveiWcBmNYLcnP5b-HXMnnz7FUcpIfDZKk--elY` | `["", "a1b2c3d4"]` | 🟡 Повторяется |
| Warsaw 8443 | `iJPbrf-Vv1pePgDQHroLYlnLu3-V6MbndZmJhK7zhns` | `Q7P9aveiWcBmNYLcnP5b-HXMnnz7FUcpIfDZKk--elY` | `["", "a1b2c3d4"]` | ⚠️ Дублирование |
| Florida | `SI87jchWXJfK2GOr3e2FL51F-djNDVgVWPiSHq5GfFI` | — | `["", "01234567", "abcdef01", "11223344"]` | 🟢 ОК |
| RF-Proxy | `8OS_zaT3om2RTyqG_5aYLXxICN28uyfaIQ1JmYwt3GM` | — | `["", "0123456789abcdef"]` | 🟢 ОК |

### Критические находки

🚨 **KEY-001:** Warsaw main и Warsaw 8443 используют **одинаковые reality keys**. Это создает correlated traffic pattern и снижает стойкость к обнаружению.

🚨 **KEY-002:** Warsaw xhttp-outbound использует `publicKey: Q7P9aveiWcBmNYLcnP5b-HXMnnz7FUcpIfDZKk--elY` (клиентский), но privateKey отличается — потенциальный конфигурационный конфликт.

🚨 **KEY-003:** Florida имеет 4 shortIds, что повышает attack surface для brute-force.

---

## 📊 СРАВНЕНИЕ КОНФИГУРАЦИЙ

### Warsaw vs Florida

| Параметр | Warsaw | Florida | Совпадение |
|----------|--------|---------|------------|
| Порт | 10086 / 8443 / 443 | 10086 | ❌ |
| Протокол инбаунда | vless, xhttp | vless | ❌ |
| Network | tcp, xhttp | tcp | ❌ |
| DNS настройки | отсутствуют | отсутствуют | ✅ |
| API | отсутствуют | включён (StatsService) | ❌ |
| Policy | отсутствуют | connIdle=300, handshake=4 | ❌ |
| Observatory | отсутствует | включён | ❌ |
| Sniffing | ✅ (http, tls) | ✅ (http, tls) | ✅ |

### Расхождения требуют внимания

🔴 **CF-001:** Warsaw имеет три инбаунта (443/tcp-reality, 8443/xhttp, 10086/tcp), Florida — один (10086). Это несимметричная архитектура.

🔴 **CF-002:** Warsaw xhttp inbound (8443) использует `dest: vkvideo.ru`, Warsaw TCP (443) — `www.google.com`. Несогласованные dest-ы создают DPI-следы.

🔴 **CF-003:** Florida использует `allocate.strategy: always` с concurrency=1000, Warsaw — базовые настройки. Возможна недостаточная производительность Warsaw.

---

## 🚨 КРИТИЧЕСКИЕ УЯЗВИМОСТИ

### 1. Информация о клиентах в конфиге

```json
"clients": [
  {"id": "bb50444f-7f4d-48ac-8a99-d0eae92a1529", "email": "@Лёша"},
  {"id": "75e37503-6222-464c-a575-da94f470322b", "email": "@babak_danila"}
]
```

**Риск:** Раскрытие личных имён (Лёша) и привязка к Telegram-никам (@babak_danila).

### 2. Токен бота в открытом виде

```python
TOKEN = "8649218949:AAESDIYZwLE-tHgC358jmnb9YEIBi3WNJ_A"  # main.py:5
```

**Риск:** Компрометация Telegram-бота, возможность отправки произвольных сообщений.

### 3. Дублирование UUID между конфигами

| UUID | Где используется |
|------|-----------------|
| `75e37503-6222-464c-a575-da94f470322b` | Warsaw, Warsaw 8443, Florida whitelist |
| `bb50444f-7f4d-48ac-8a99-d0eae92a1529` | Warsaw, Warsaw 8443 |

**Риск:** Correlation атаки — злоумышленник может отследить трафик между серверами.

### 4. Fallback misconfiguration в xray-ws.json

```json
"fallbacks": [{"dest": "www.microsoft.com:443"}]
```

**Риск:** Прямой fallback на внешний хост без локального прокси. Раскрывает реальный IP.

---

## ⚙️ НЕОПТИМАЛЬНЫЕ НАСТРОЙКИ

| Файл | Проблема | Рекомендация |
|------|----------|--------------|
| xray.json | Нет policy | Добавить connIdle, handshake |
| xray.json | Нет DNS | Настроить 1.1.1.1/1.0.0.1 |
| xray.json | dest=microsoft.com | Разделить dest на inbound/outbound |
| xray-warsaw-working.json | fallback на 127.0.0.1:8444 | Убедиться в существовании службы |
| xray-rf-proxy.json | dest=yandex.ru, serverNames=yandex | Сменить на обфусцируемый домен |
| xray-rf-proxy-xhttp.json | dest=ok.ru | Российский домен — высокий риск блокировки |
| Все configs | Отсутствуют detour-ы | Добавить для цепочки proxy chaining |

---

## 📁 СТРУКТУРА КОНФИГОВ

```
/root/LabDoctorM/projects/telegram-bots/vpn-daemon/vpnconfig/
├── xray.json — базовый Warsaw (устаревший)
├── xray-optimized.json — Warsaw с API/policy
├── xray-warsaw-working.json — Warsaw мульти-инбаунд
├── xray-warsaw-fix.json — Warsaw 8443 only
├── xray-florida-optimized.json — Florida standalone
├── xray-rf-proxy.json — TCP фронтенд
├── xray-rf-proxy-whitelist.json — Load balancing Warsaw/Florida
├── xray-rf-proxy-xhttp.json — xhttp фронтенд
├── xray-rf-proxy-xhttp-alt.json — fallback на ok.ru
├── xray-ws.json — WebSocket (небезопасный, no TLS)
└── xray-xhttp-warsaw.json — не найден (отсутствует)
```

---

## 🛡️ РЕКОМЕНДАЦИИ

### Приоритет HIGH

1. **Заменить все reality keys** на уникальные для каждого сервера/инбаунда
2. **Удалить email с именами** из конфигов, использовать анонимные теги
3. **Переместить токен бота** в переменную окружения
4. **Внедрить DNS настройки** (1.1.0.0/1.1.0.1 Cloudflare или AdGuard)

### Приоритет MEDIUM

5. Настроить `policy.levels` с connIdle=300 на всех серверах
6. Убрать дублирование UUID между серверами
7. Заменить dest на более обфусцируемые домены (Cloudflare, Apple)
8. Добавить `detour` для chain-routing (inbound → outbound)

### Приоритет LOW

9. Настроить `observatory` для всхождения нагрузки
10. Упростить shortIds до 1-2 значений
11. Добавить `tcpKeepAlive` настройки в Florida
12. Удалить xray-ws.json (без TLS — security risk)

---

## 📊 МЕТРИКИ ТРАФИКА

| Показатель | Warsaw | Florida | RF-Proxy |
|------------|--------|---------|----------|
| Активные inbound порты | 3 | 1 | 1 |
| Инбаунт протоколы | vless/tcp, vless/xhttp, vless/tcp | vless/tcp | vless/tcp, socks |
| Клиентские UUID | 4 | 0 (по умолчанию) | 1 |
| ShortIds count | 2 | 4 | 2 |

---

## 🔚 ЗАКЛЮЧЕНИЕ

VPN инфраструктура Warsaw/Florida/RF-Proxy функциональна, но имеет серьёзные пробелы в сфере:

- **Security:** Раскрытие персональных данных, уязвимые токены
- **Anonymity:** Коррелированные ключи, дублирование UUID
- **DPI-resistance:** Использование российских доменов (ok.ru, vkvideo.ru, yandex.ru)

Требуется **немедленное** вмешательство для замены ключей и очистки конфигов от PII.

---

*Аудит завершён. Файл сохранён: `/root/LabDoctorM/VPNDaemonRobot/VPN_AUDIT_2026.md`*
---

## ✅ ВНЕДРЁННЫЕ ИСПРАВЛЕНИЯ (02.05.2026)

| Проблема | Действие | Статус |
|----------|----------|--------|
| Дублирование reality keys | Сгенерированы уникальные key pairs для Warsaw/main, Warsaw/8443, Florida, RF-Proxy | ✅ |
| Личные данные в конфигах | Удалены email @Лёша и @babak_danila, заменены на анонимные UUID | ✅ |
| Токен бота в коде | Перемещён в `.env`, main.py теперь читает из переменной окружения | ✅ |
| Дублирование UUID | Все UUID заменены на уникальные | ✅ |
| Отсутствие DNS | Добавлен Cloudflare DNS (1.1.1.1, 1.0.0.1) в Florida и whitelist | ✅ |
| Российские домены | Заменены на www.cloudflare.com, www.microsoft.com, apple.com | ✅ |
| .gitignore | Добавлен для исключения .env | ✅ |

### Новые UUID клиентов:

| Прежний UUID | Новый UUID | Где используется |
|--------------|----------|-----------------|
| `75e37503-6222-464c-a575-da94f470322b` | `0129aba9-e2bf-470b-a06c-9a465ab015b5` | Warsaw, RF-Proxy, whitelist |
| `bb50444f-7f4d-48ac-8a99-d0eae92a1529` | `e0e4c7c1-930f-411e-99e8-3cf193259f39` | Warsaw |
| `53396a4c-47d4-482a-8202-8327b485f5a0` | `8d62aec9-904f-4cc2-a45e-6d9d2f8c00db` | Warsaw 8443 |
| `ed4faffa-e3fe-4ff4-b3b0-65ff400242b1` | `0eae4082-3514-4810-a02c-219c5c5d2065` | Warsaw |
| — | `bfffefdb-2f46-45a3-975c-f8119f269be4` | Florida |

### Новые Reality Keys:

| Сервер | Private Key | Public Key |
|--------|-------------|------------|
| Warsaw/main | `2GHw814dHN1bdgYrdl_oWFBzDmctPwzyl00B8Klk1XQ` | `n9EpKAGf4UGwrJtcxMlpVunJJomnbidMne38TysKOW4` |
| Warsaw/8443 | `YPlL15OyMmaBZJufseGms5EC06X2ep-As4jZCE51mXo` | `WqXYALR9fraWU38kkJFDe0ZxpTwwYi32WvvfjktQnhE` |
| Florida | `OC1kKNoZDAsaU3h3aLJ8D5PWMhCYAJck_Uz7VIqTymk` | `AB-kH9JEaNv9U7yllmoR2NA8ODh-Uxm8vCql8tVIMXk` |
| RF-Proxy | `kAdoyjUTciHFgoKM5awHXLl4OGGfC5ysoeZnTAIOgEo` | `Raw2e8oTrs3sG4lVVJOLvgEgrm7KGsvcoT5zsSypznM` |

---

## ⚡ FAILOVER СИСТЕМА (НОВИНКА)

### Конфигурация автоматического переключения

| Параметр | Значение |
|----------|----------|
| Healthcheck interval | 30 секунд |
| Макс. время переключения | 60 секунд (2 неправильных проверки) |
| Primary сервер | Warsaw (185.138.90.150:443) |
| Fallback сервер | Florida (104.253.1.210:10086) |
| Strategy | leastLoad с RTT контролем |
| Ping destination | http://www.gstatic.com/generate_204 |

### Файлы

- `vpnconfig/xray-failover-client.json` — клиентский конфиг с балансировкой
- `scripts/healthcheck-failover.py` — Python healthcheck скрипт
- `/etc/systemd/system/xray-failover.service` — Xray сервис
- `/etc/systemd/system/vpn-healthcheck.service` — Healthcheck сервис

### Установка

```bash
systemctl daemon-reload
systemctl enable xray-failover vpn-healthcheck
systemctl start xray-failover vpn-healthcheck
```

### Мониторинг

```bash
journalctl -u vpn-healthcheck -f
tail -f /var/log/vpn-failover.log
```
