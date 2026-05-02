# ДАШБОРД — Отладка и решение проблем

> **Кодовое имя проекта:** ДАШБОРД  
> **Домен:** dashboard.shtab-ai.ru  
> **Исходники:** `/root/LabDoctorM/syncthing-dashboard/`  
> **Продакшен:** `/var/www/html/dashboard-react/`  
> **API сервер:** `os-lab-dashboard-api.service` (порт 8002)  
> **Nginx конфиг:** `/etc/nginx/sites-enabled/default`

---

## 🔥 Ошибки и решения

### 1. Nginx лежал (не запущен)

**Симптом:** Дашборд не открывается, порты 80/443 не слушаются.

**Причина:** `nginx.service` был в состоянии `inactive (dead)` с 13:08.

**Решение:**
```bash
systemctl start nginx
systemctl reload nginx
```

**Как избежать:** Проверять статус сервисов перед дебагом фронта.

---

### 2. Бэкапы конфигов в `sites-enabled/`

**Симптом:** Nginx ругается `duplicate default server for 0.0.0.0:80`.

**Причина:** В `/etc/nginx/sites-enabled/` лежали файлы `default.bak`, `default.bak2`. Nginx читает **все** файлы в папке, а не только симлинки.

**Решение:**
```bash
rm -f /etc/nginx/sites-enabled/*.bak*
```

**Как избежать:** Никогда не оставлять бэкапы в `sites-enabled/`. Хранить в `/etc/nginx/sites-available/` или `/tmp/`.

---

### 3. Отсутствие SSL (порт 443 не слушался)

**Симптом:** По HTTPS дашборд не открывается.

**Причина:** В nginx конфиге не было блока `server { listen 443 ssl ... }`.

**Решение:** Добавить SSL-блок:
```nginx
server {
    listen 443 ssl http2 default_server;
    listen [::]:443 ssl http2 default_server;
    server_name dashboard.shtab-ai.ru localhost;

    ssl_certificate /etc/letsencrypt/live/shtab-ai.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/shtab-ai.ru/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    root /var/www/html/dashboard-react;
    index index.html;
    # ... locations
}
```

---

### 4. Неверный `base` в Vite и пути в `index.html`

**Симптом:** Чёрный экран, JS файлы не грузятся (404 или неверные пути).

**Причина:** 
- В `vite.config.ts`: `base: '/dashboard-react/'`
- В `index.html` после сборки: `<base href="/">`
- В `index.html`: `src="/dashboard-react/assets/..."` (двойные пути)

**Решение:**
```typescript
// vite.config.ts
export default defineConfig({
  base: '/',  // Вместо '/dashboard-react/'
  // ...
});
```

---

### 5. Неверный `API_BASE` в `useApi.ts`

**Симптом:** Чёрный экран, данные не приходят, API возвращает 404.

**Причина:** 
```typescript
// БЫЛО (НЕВЕРНО):
const API_BASE = '/dashboard-react/api';

// Компоненты шлют запросы вида '/api/monitoring/servers'
// Итого: '/dashboard-react/api/api/monitoring/servers' — дублирование!
```

**Решение:**
```typescript
// СТАЛО (ВЕРНО):
const API_BASE = '';
```

---

### 6. Nginx проксировал `/api/` не на тот порт

**Симптом:** API отдаёт 404, данные не приходят.

**Причина:** 
```nginx
# БЫЛО (НЕВЕРНО):
location /api/ {
    proxy_pass http://127.0.0.1:8000;  # ОШИБКА! API на 8002
}
```

**Решение:**
```nginx
# СТАЛО (ВЕРНО):
location /api/ {
    proxy_pass http://127.0.0.1:8002;  # os-lab-dashboard-api.service
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

**Порты API:**
- `8000` — основной бэкенд (для `/f/`, файловые операции)
- `8001` — `file_browser_api` (для `/api/files`, `/api/file/`, `/api/upload`)
- `8002` — `os-lab-dashboard-api` (для `/api/monitoring/`, `/api/or/`, `/api/domains/` и т.д.)

---

### 7. Неверный путь в `Monitoring.tsx` (прямой fetch)

**Симптом:** Кнопка рестарта сервиса не работает.

**Причина:**
```typescript
// БЫЛО (НЕВЕРНО):
await fetch(`/dashboard-react/api/monitoring/services/${service}/restart`, ...);
```

**Решение:**
```typescript
// СТАЛО (ВЕРНО):
await fetch(`/api/monitoring/services/${service}/restart`, ...);
```

---

### 8. Старая папка `dist/` в продакшене

**Симптом:** Nginx отдаёт старый `index.html` с неверными путями.

**Причина:** После сборки Vite создаёт папку `dist/`. При копировании `cp -r dist/* /var/www/html/dashboard-react/` создаётся вложенная `/var/www/html/dashboard-react/dist/` со старым `index.html`.

**Решение:**
```bash
rm -rf /var/www/html/dashboard-react/dist
cp -r /root/LabDoctorM/syncthing-dashboard/dist/* /var/www/html/dashboard-react/
```

---

### 9. Чёрный экран на Safari iOS (ES модули)

**Симптом:** Дашборд работает в Chrome/FF, но на iPhone/iPad — чёрный экран.

**Причина:** Safari iOS плохо работает с ES модулями (`type="module"`).

**Решение:** Установить и настроить `@vitejs/plugin-legacy`:
```bash
cd /root/LabDoctorM/syncthing-dashboard
npm install --save-dev @vitejs/plugin-legacy@^5.0.0 --legacy-peer-deps
npm install --save-dev terser
```

```typescript
// vite.config.ts
import legacy from '@vitejs/plugin-legacy';

export default defineConfig({
  // ...
  plugins: [
    react(),
    legacy({
      targets: ['defaults', 'not IE 11'],
      additionalLegacyPolyfills: ['regenerator-runtime/runtime']
    })
  ],
});
```

После сборки генерируется два JS-файла:
- `index-XXX.js` — современный (ES модули)
- `index-legacy-XXX.js` — легаси (IIFE, для Safari iOS)

В `index.html` автоматически добавляются теги:
```html
<script type="module" crossorigin src="/assets/index-XXX.js"></script>
<script nomodule crossorigin src="/assets/index-legacy-XXX.js"></script>
```

---

### 10. SWR не используется

**Проверка:** В `package.json` и исходном коде SWR не найден. Проблема была не в нём.

```bash
grep -r "swr\|useSWR" /root/LabDoctorM/syncthing-dashboard/src/
# Результат: пусто (SWR не используется)
```

---

## 📋 Чек-лист для следующей сессии

Перед началом работы с дашбордом:

- [ ] Проверить статус сервисов: `systemctl status nginx os-lab-dashboard-api`
- [ ] Проверить слушаемые порты: `ss -tlnp | grep -E ':(80|443|8000|8001|8002)'`
- [ ] Проверить, что в `/etc/nginx/sites-enabled/` нет бэкапов (`*.bak*`)
- [ ] Проверить `API_BASE` в `src/hooks/useApi.ts` (должно быть `''`)
- [ ] Проверить `proxy_pass` для `/api/` в nginx (должно быть `8002`)
- [ ] Проверить размер JS файлов: `ls -lh /var/www/html/dashboard-react/assets/*.js`
  - Modern должен быть >50KB
  - Legacy должен быть >50KB
- [ ] Проверить `base` в `vite.config.ts` (должно быть `'/'`)
- [ ] **Важно:** Сделать жёсткую перезагрузку в браузере (`Ctrl+Shift+R` / `Cmd+Shift+R`) или открыть в режиме инкогнито

---

## 🏗️ Структура проекта

```
/root/LabDoctorM/syncthing-dashboard/
├── src/
│   ├── hooks/
│   │   └── useApi.ts          # API_BASE = ''
│   ├── pages/
│   │   ├── Monitoring.tsx     # Исправлены пути fetch
│   │   ├── LabMap.tsx
│   │   └── Files.tsx
│   ├── App.tsx
│   └── main.tsx
├── vite.config.ts            # base: '/', plugin-legacy подключен
├── package.json
└── dist/                    # Сборка (не коммитить!)

/var/www/html/dashboard-react/
├── index.html               # base href="/", script src="/assets/..."
└── assets/
    ├── index-XXX.js        # Modern (ES modules)
    ├── index-legacy-XXX.js # Legacy (IIFE для Safari iOS)
    ├── polyfills-legacy-XXX.js
    └── index-XXX.css
```

---

## 🔧 Полезные команды

```bash
# Пересборка и деплой
cd /root/LabDoctorM/syncthing-dashboard
npm run build
cp -r dist/* /var/www/html/dashboard-react/
rm -rf /var/www/html/dashboard-react/dist  # Важно!
systemctl reload nginx

# Проверка
curl -s -o /dev/null -w "%{http_code}\n" https://localhost/ -k
curl -s https://127.0.0.1/ -k | grep -E "base|script.*js"
curl -s -o /dev/null -w "%{http_code}\n" https://127.0.0.1/api/monitoring/servers -k

# Логи
tail -f /var/log/nginx/error.log
journalctl -u os-lab-dashboard-api -f
```

---

**Дата дебага:** 1 мая 2026  
**Статус:** ✅ Исправлено, дашборд работает
