# Ngrok Setup для Xiaomi Stick (САМЫЙ ПРОСТОЙ СПОСОБ)

## Как это работает:
1. Ngrok создаёт обратный туннель наружу
2. Ты даёшь мне ссылку - я сразу захожу на твой Android TV
3. Никаких серверов - всё через облако ngrok

## Шаг 1: Установи ngrok
```bash
pkg install wget
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm.tgz
tar -xzf ngrok-v3-stable-linux-arm.tgz
./ngrok config add-authtoken YOUR_AUTHTOKEN  # бесплатный аккаунт
```

## Шаг 2: Запусти SSH туннель
```bash
pkg install openssh
sshd  # стартует SSH сервер на порту 8022

# Открой туннель наружу:
./ngrok tcp 8022
```

## Шаг 3: Дай мне вывод
После запуска ты увидишь:
```
Forwarding  tcp://0.tcp.ngrok.io:12345 -> localhost:8022
```

**Скинь мне эту строку - и я сразу захожу на твой Xiaomi Stick!**

## Автозапуск:
```bash
# ~/start_ngrok.sh
#!/bin/bash
cd /data/data/com.termux/files/home
while true; do
  ./ngrok tcp 8022 > /dev/null 2>&1 &
  sleep 3600  # каждый час перезапуск
done
```