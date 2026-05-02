# VLESS Reality DPI Обход (Warsaw + Florida)

## Title
VLESS Reality DPI Обход

## Description
Руководство по обходу DPI РКН через VLESS+Reality для серверов Warsaw и Florida. Содержит готовые конфиги, команды диагностики и best practices.

## Author
ЗавЛаб Безумный Доктор

## Version
1.0 (2026-04-30)

---

## Triggers

Активируй этот навык при:
- Не работает VLESS+Reality соединение
- DPI РКН блокирует сервер Warsaw/Florida
- Нужно проверить конфиг Xray на корректность
- Требуется быстрая диагностика порта

---

## Steps

1. Проверь порт: `ss -tlnp | grep 10086`
2. Проверь сервис: `systemctl status demonvpn`
3. Проверь логи: `journalctl -u demonvpn -f`
4. Тестируй соединение: `timeout 3 bash -c 'cat < /dev/tcp/IP/PORT'`
5. При ошибке - проверь xray.json на пустые shortIds и отсутствие flow
6. При необходимости - `systemctl restart demonvpn`

---

## Examples

### Проверка Warsaw TCP
```bash
ss -tlnp | grep 10086
# Вывод: LISTEN 0 128 0.0.0.0:10086
```

### Исправление пустого shortIds
```json
// Было (ошибка)
"shortIds": ["", "a1b2c3d4"]

// Стало (правильно)
"shortIds": ["a1b2c3d4"]
```

### Диагностика клиента
```bash
# На клиенте
curl -x http://127.0.0.1:10808 https://www.google.com
# Если 503 - проблема на сервере
```

---

## Quick Start

### Warsaw (TCP) - Рабочий
```bash
# Тест порта
ss -tlnp | grep 10086

# Готовая ссылка
vless://75e37503-6222-464c-a575-da94f470322b@185.138.90.150:10086?type=tcp&security=reality&sni=www.microsoft.com&pbk=Q7P9aveiWcBmNYLcnP5b-HXMnnz7FUcpIfDZKk--elY&sid=a1b2c3d4&flow=xtls-rprx-vision&fp=chrome#Warsaw
```

### Florida (TCP)
```bash
vless://7bc5a931-e8dc-4675-9085-d0e9ea70eca6@104.253.1.210:10086?security=reality&flow=xtls-rprx-vision&type=tcp&sni=www.google.com&pbk=czO92eWUw0tNqjZKzTd9YqSSy42LQZdSEvardnpqtio&sid=01234567&fp=chrome#Florida
```

### Warsaw (XHTTP) - Альтернатива
```bash
vless://79eb240c-889d-410d-8773-5bc7d7f57893@185.138.90.150:8443?type=xhttp&security=reality&sni=ok.ru&pbk=Q7P9aveiWcBmNYLcnP5b-HXMnnz7FUcpIfDZKk--elY&sid=0123456789abcdef&fp=chrome&path=/api/v1/users/auth#Warsaw_xhttp
```

---

## Configuration Reference

### Warsaw Server (185.138.90.150)

| Параметр | TCP (10086) | XHTTP (8443) |
|----------|-------------|--------------|
| Protocol | vless | vless |
| Network | tcp | xhttp |
| Security | reality | reality |
| Flow | xtls-rprx-vision | xtls-rprx-vision |
| SNI | www.microsoft.com | ok.ru |
| Public Key | Q7P9aveiWcBmNYLcnP5b-HXMnnz7FUcpIfDZKk--elY | Q7P9aveiWcBmNYLcnP5b-HXMnnz7FUcpIfDZKk--elY |
| Short ID | a1b2c3d4 | 0123456789abcdef |
| Path | - | /api/v1/users/auth |

### Florida Server (104.253.1.210)

| Параметр | Значение |
|----------|----------|
| Port | 10086 |
| Protocol | vless |
| Network | tcp |
| Security | reality |
| Flow | xtls-rprx-vision |
| SNI | www.google.com |
| Public Key | czO92eWUw0tNqjZKzTd9YqSSy42LQZdSEvardnpqtio |
| Short ID | 01234567 |

---

## DPI Bypass Formula

**Все 6 элементов обязательны:**

```
vless + xtls-rprx-vision + reality + tcp + chrome + реальный_SNI + точный_shortId
```

### Критические параметры

1. **flow: xtls-rprx-vision** - без него REALITY не шифрует трафик
2. **network: tcp** - xhttp видим для DPI на Layer 7
3. **shortIds: без пустых элементов** - пустой shortId ломает handshake

---

## Troubleshooting

### Чеклист диагностики

| Шаг | Команда | Ожидаемый результат |
|-----|---------|---------------------|
| 1. Порт слушается | `ss -tlnp \| grep 10086` | LISTEN |
| 2. Сервис активен | `systemctl status demonvpn` | active (running) |
| 3. Логи ошибок | `journalctl -u demonvpn -f` | нет ошибок |
| 4. Тест соединения | `timeout 3 bash -c 'cat < /dev/tcp/IP/PORT'` | OK |

### Типичные ошибки

| Ошибка | Признак | Решение |
|--------|---------|---------|
| Пустой shortIds | `""` в массиве | Удалить пустой элемент |
| Нет flow | `flow: ""` | Добавить `xtls-rprx-vision` |
| xhttp виден DPI | RKN блок | Перейти на TCP |
| Неверный SNI | Соединение падает | Проверить доступность SNI |

---

## Best Practices

### Как не дать себя поймать

1. **Используй реальные SNI** - microsoft.com, google.com, yandex.ru (работающие сайты)
2. **Не используй xhttp в проде** - только для тестов, DPI видит HTTP-фреймы
3. **Проверяй shortIds** - пустые значения ломают REALITY handshake
4. **Регулярно меняй порты** - каждые 2-3 недели на новые
5. **Объединяй сервера** - схема "Белый список": Клиент → РФ-прокладка → VPN

### Схема White List Tunneling

```
Клиент (РФ) → Прокладка (РФ, 443/tcp) → VPN-сервер (загранина)
```

- РФ-прокладка фильтрует по whitelist
- Только разрешённые домены идут дальше
- Снижает объём подозрительного трафика

---

## Tools

### Диагностика
- `ss -tlnp` - проверка портов
- `systemctl status demonvpn` - статус сервиса Xray
- `journalctl -u demonvpn -f` - логи в реальном времени
- `timeout 3 bash -c 'cat < /dev/tcp/IP/PORT'` - тест соединения

### Управление
- `systemctl restart demonvpn` - рестарт Xray
- `systemctl restart demonvpn-bot` - рестарт Telegram-бота
- `/root/LabDoctorM/VPNDaemonRobot/vpnconfig/xray.json` - основной конфиг