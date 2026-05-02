# vpn-setup

Автоматическое разворачивание VPN серверов (Xray/V2Ray) с настройкой VLess + Reality. Интеграция с FastAPI бэкендом.

## Triggers

Вызывать при:
- `настрой vpn`, `разверни xray`, `подними сервер vpn`
- `создай конфиг vless reality`, `сгенерируй ключи x25519`
- `добавь клиента в xray`, `выдай vless url`
- `настрой nginx для vpn`, `сделай api для конфигов`
- `vpn-setup`, `vpn-скилл`

## Steps

### 1. Подготовка и аудит сервера
- Проверить доступность сервера по SSH
- Считать переменные из `.env` (хост, порт, пользователь, пароль/ключ)
- **Никогда не хранить пароли в коде** — только в `.env`

### 2. Установка Xray
- Скачать официальный инсталлятор: `bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install`
- Проверить версию: `xray version`
- Создать systemd-юнит `/etc/systemd/system/xray.service` (стандартный)

### 3. Генерация ключей Reality
- Сгенерировать x25519 пару:
  ```bash
  xray x25519
  ```
- Сохранить `private_key` и `public_key`
- Выбрать SNI (fake domain) — реальный сайт, например `www.google.com`

### 4. Создание конфига Xray
- Путь: `/usr/local/etc/xray/config.json`
- Структура для VLess + Reality:

```json
{
  "log": { "loglevel": "warning" },
  "inbounds": [{
    "port": 443,
    "protocol": "vless",
    "settings": {
      "clients": [{
        "id": "<UUID>",
        "flow": "xtls-rprx-vision"
      }],
      "decryption": "none"
    },
    "streamSettings": {
      "network": "tcp",
      "security": "reality",
      "realitySettings": {
        "show": false,
        "dest": "www.google.com:443",
        "xver": 0,
        "serverNames": ["www.google.com"],
        "privateKey": "<x25519_private_key>",
        "shortIds": ["", "0123456789abcdef"]
      }
    }
  }],
  "outbounds": [{ "protocol": "freedom" }]
}
```

**Критические правила:**
- В `clients` **НЕТ** поля `encryption` (иначе ошибка "encryption should not be in inbound settings")
- У клиента **ОБЯЗАТЕЛЬНО** `flow: "xtls-rprx-vision"` (иначе ошибка "account is not able to use the flow")
- JSON должен быть валидным — следить за кавычками при записи через SSH

### 5. Настройка клиентов
- Генерировать UUID: `xray uuid`
- Формировать VLess URL:
  ```
  vless://<UUID>@<SERVER_IP>:443?encryption=none&flow=xtls-rprx-vision&security=reality&sni=www.google.com&fp=chrome&pbk=<public_key>&sid=&type=tcp#Reality-VPN
  ```
- Генерировать QR-код: `qrencode -t UTF8 "vless://..."` или base64 PNG

### 6. Интеграция с FastAPI бэкендом
- Создать FastAPI приложение (Python, порт 8000)
- Эндпоинты:
  - `POST /api/client` — добавить клиента (генерирует UUID, обновляет config.json через SSH, рестарт Xray)
  - `GET /api/config?client=<UUID>` — выдать VLess URL и QR-код
  - `DELETE /api/client/<UUID>` — удалить клиента
- Бэкенд хранит маппинг UUID -> конфиги в SQLite/JSON
- При изменении конфига: записать через SSH, выполнить `systemctl restart xray`

### 7. Настройка Nginx
- Проксирование API: слушать 80/443, проксировать `/api/*` на FastAPI
- SSL: использовать certbot или self-signed (при необходимости)
- Конфиг: `/etc/nginx/sites-available/vpn-api`

### 8. Systemd юниты
- Xray: `/etc/systemd/system/xray.service`
- FastAPI: `/etc/systemd/system/vpn-api.service` (через `uvicorn`)
- Включить автозапуск: `systemctl enable xray vpn-api`

### 9. Деплой и проверка
- `systemctl daemon-reload`
- `systemctl restart xray vpn-api`
- `journalctl -u xray -f` — проверить ошибки
- Тест коннекта: попытка подключения клиента

## Examples

**Пример 1: Базовый деплой**
```
User: настрой VPN на сервере 123.45.67.89
Assistant: Принято. Читаю .env, ставлю Xray, генерирую ключи Reality, создаю конфиг VLess+Reality, настраиваю API и Nginx. Готово за 5 минут.
```

**Пример 2: Добавление клиента**
```
User: добавь клиента в VPN
Assistant: Создал UUID: 550e8400-e29b-41d4-a716-446655440000. Обновил конфиг, рестарт Xray. Вот твой VLess URL и QR-код.
```

**Пример 3: Получение конфига**
```
User: дай конфиг для UUID 550e8400-e29b-41d4-a716-446655440000
Assistant: GET /api/config?client=550e8400-e29b-41d4-a716-446655440000 → возвращает URL и QR-код
```

## Tools

- **SSH (paramiko/fabric)**: подключение к серверу, выполнение команд, запись файлов
- **Xray CLI**: `xray x25519` (генерация ключей), `xray uuid` (генерация UUID), `xray version`
- **qrencode**: генерация QR-кодов для VLess URL
- **systemctl**: управление сервисами xray и vpn-api
- **nginx**: проксирование API бэкенда
- **FastAPI + uvicorn**: бэкенд для управления клиентами
- **certbot**: получение SSL сертификатов (опционально)
- **.env (python-dotenv)**: хранение SSH credentials и конфигурации

## Warnings

⚠️ **Валидация JSON**: При записи config.json через SSH используй `cat > /path << 'EOF'` или `jq`, чтобы избежать сломанных кавычек.

⚠️ **Безопасность**: Пароли SSH только в `.env`. Публичные ключи Reality — это нормально, приватные — никогда не светить в логах.

⚠️ **Reality SNI**: Используй реальные, популярные домены (Google, Cloudflare, etc.) в `serverNames` и `dest`.

⚠️ **Права доступа**: Конфиги Xray должны быть доступны пользователю, от которого запущен сервис.
