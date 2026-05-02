# Serveo Setup (БЕЗ РЕГИСТРАЦИИ!)

## Как это работает:
- SSH в облако → туннель наружу
- Никаких аккаунтов, никаких регистраций
- Просто SSH!

## Шаг 1: Запусти SSH сервер на Xiaomi Stick
```bash
pkg install openssh
sshd -p 8022
# Порт 8022 чтобы не конфликтовать с Termux SSH
```

## Шаг 2: Создай туннель через Serveo
```bash
ssh -R 8022:localhost:8022 serveo.net
```

## Шаг 3: Получи ссылку
В ответ получишь:
```
Forwarding TCP connections from tcp://serveo.net:12345
```

**Скинь мне эту строку - и я сразу захожу на твой Xiaomi Stick!**

## Автозапуск:
```bash
# ~/start_serveo.sh
#!/bin/bash
while true; do
  ssh -R 8022:localhost:8022 serveo.net
  sleep 5
done
```

**ПРЕИМУЩЕСТВА:**
- ❌ Без регистрации
- ❌ Без API ключей  
- ❌ Без лимитов трафика
- ✅ Просто SSH!