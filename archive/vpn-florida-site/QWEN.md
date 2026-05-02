# vpn-florida-site — Лендинг + Личный кабинет VPN Florida (Майами)

## Обзор
Лендинг и личный кабинет для VPN-сервиса Florida (Майами). Проект включает фронтенд на React 19 + TypeScript и бэкенд на FastAPI для управления конфигами, оплатой и клиентами через SSH.

## Стек
- **Фронтенд**: React 19 + TypeScript + Vite 7 + Tailwind CSS 3 + shadcn/ui (40+ компонентов)
- **Бэкенд**: Python FastAPI (сервер на `:8000`)
- **Прокси**: в dev-режиме `/api` → `localhost:8000` (настроено в `vite.config.ts`)
- **Стилизация**: неоновый розовый `#FF00FF`, циан `#00FFFF`, glass-панели
- **Инструменты**: vitest (тесты фронта), pytest (тесты бэкенда), paramiko (SSH-доступ к серверу Xray)

## Структура проекта
```
vpn-florida-site/
├── src/                # Фронтенд
│   ├── sections/       # Секции лендинга
│   ├── hooks/          # Кастомные хуки
│   ├── types/          # Типы (в т.ч. API в types/server.ts)
│   ├── components/     # UI-компоненты
│   ├── App.tsx         # Корневой компонент
│   └── main.tsx        # Точка входа
├── server/             # Бэкенд FastAPI
│   ├── main.py         # Основной файл сервера
│   ├── servers.json    # Данные серверов
│   ├── payments.json   # История платежей
│   └── requirements.txt # Зависимости Python
├── ssl/                # SSL-сертификаты
├── public/             # Статика (wallet-qr.png и др.)
└── dist/               # Сборка фронтенда (после npm run build)
```

## API (эндпоинты)
| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/api/config` | Выдача VLESS-конфигов |
| GET | `/api/status` | Проверка доступности сервера (пинг) |
| POST | `/api/verify-payment` | Прием оплаты (хеш транзакции) |
| GET | `/api/get-config-by-txid/{tx_id}` | Выдача конфига после оплаты |
| POST | `/api/add-client` | Добавление клиента через SSH (paramiko) |

## Environment Variables (бэкенд)
Задаются в `.env` или системном окружении (НЕ хардкодить в коде):
- `FLORIDA_SSH_HOST` — IP сервера Florida
- `FLORIDA_SSH_USER` — пользователь SSH (default: `root`)
- `FLORIDA_SSH_PASS` — пароль SSH
- `TELEGRAM_BOT_TOKEN` — токен бота для уведомлений
- `TELEGRAM_CHAT_ID` — ID чата для уведомлений

## Deploy
1. **Фронтенд**:
   ```bash
   npm install
   npm run build  # Сборка в /dist
   ```

2. **Бэкенд**:
   ```bash
   /root/LabDoctorM/venv/bin/pip install -r server/requirements.txt
   /root/LabDoctorM/venv/bin/uvicorn server.main:app --host 0.0.0.0 --port 8000
   ```

3. **Systemd-сервис**:
   Создать файл `/etc/systemd/system/vpn-florida.service`:
   ```ini
   [Unit]
   Description=VPN Florida FastAPI Service
   After=network.target

   [Service]
   User=root
   WorkingDirectory=/root/LabDoctorM/vpn-florida-site
   ExecStart=/root/LabDoctorM/venv/bin/uvicorn server.main:app --host 0.0.0.0 --port 8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
   Затем:
   ```bash
   systemctl daemon-reload
   systemctl enable vpn-florida
   systemctl start vpn-florida
   ```

4. **Nginx/Caddy**:
   Настроить проксирование, SSL из `/ssl/`. Пример для Nginx:
   ```nginx
   server {
       listen 443 ssl;
       server_name your-domain.com;

       ssl_certificate /root/LabDoctorM/vpn-florida-site/ssl/cert.pem;
       ssl_certificate_key /root/LabDoctorM/vpn-florida-site/ssl/key.pem;

       location / {
           root /root/LabDoctorM/vpn-florida-site/dist;
           try_files $uri $uri/ /index.html;
       }

       location /api/ {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## Как работать
1. Мелкие правки — сразу делай
2. Сложные задачи — `/plan`, план тезисно
3. Деплой — по разделу `## Deploy` этого файла
4. Тесты: `vitest` (фронт), `pytest` (бэкенд); перед коммитом обязательно
5. Соблюдай правила лаборатории из `/root/LabDoctorM/QWEN.md`

## Особенности
- В коде НЕ хардкодить пароли/credentials — только через env
- Типы API вынесены в `/src/types/server.ts`
- `server/main.py` использует `paramiko` для SSH-доступа к серверу Xray
- Цвета бренда: неоновый розовый `#FF00FF`, циан `#00FFFF`, glass-панели
