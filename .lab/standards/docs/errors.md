# 🚨 Лаборатория ошибок: учимся на человеческих косяках

## Шаблон записи
```
## YYYY-MM-DD: Краткое название
### Симптомы
- Что не работает
### Корень зла
- Почему так случилось
### Исправление
- Что делали
### Паттерн
- [error-type] категория ошибки (frontend/browser/mobile/ios/safari/api/etc)
### Скилл
- Название скилла, который предотвращает
```

---

## 2026-05-01: Safari/iOS чёрный экран из-за SWR модуля

### Симптомы
- Сайт работает в Chrome/Firefox/Linux
- На Safari/iOS — чёрный экран, JS не запускается
- Ошибка в консоли: `SWR: Cannot read properties of undefined`

### Корень зла
- SWR модуль использовал `window` и `localStorage` без проверки существования
- iOS Safari в некоторых режимах блокирует `localStorage` в iframe/private mode
- Код не имел fallback для мобильных браузеров
- Тестировался только на десктопных Chrome

### Исправление
- Добавлен проверочный wrapper: `if (typeof window !== 'undefined' && window.localStorage)`
- Fallback на sessionStorage + cookie-based storage
- Теперь работает в iOS Safari

### Паттерн
- [frontend/browser/mobile/ios/safari] - Не проверял мобильную совместимость

### Скилл
- `safari-mobile-check`

---

## 2026-04-28: Утечка памяти и рестарт-петля Protocol

### Симптомы
- Memory leak: Used 2.7 GiB / 3.8 GiB
- protocol-bot.service: рестарт каждые 4-5 секунд

### Корень зла
- Порт 8000 занят старым зомби-процессом
- Цепная реакция сервисов с Requires=
- Зомби-процессы не убивались

### Исправление
- Убить процесс-зомби на порту
- Пофиксить run_bot.sh для .env
- Лимит journald до 100M

### Паттерн
- [backend/system] - Systemd рестарт-петля из-за зомби-процессов

### Скилл
- `systemd-zombie-killer`

---

## 2026-04-28: Рестарт-петля x-ui (XRAY REALITY)

### Симптомы
- x-ui.service: рестарт каждые 2 секунды
- `XRAY: Failed to start: non-empty "serverNames", please use "serverName" instead`

### Корень зла
- Несовместимость x-ui и xray-core 26.x
- Ложное сообщение об ошибке (баг в xray)
- Xray 26.x требует `serverNames` (массив), а не `serverName`

### Исправление
- Обновить xray до 26.3.27
- Править базу x-ui вместо конфига

### Паттерн
- [backend/api] - Ложные сообщения об ошибках в логах

### Скилл
- `xray-config-validator`
