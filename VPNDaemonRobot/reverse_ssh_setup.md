# Reverse SSH Tunnel для Xiaomi Stick

## Шаг 1: Установи SSH клиент на Xiaomi Stick
```bash
pkg install openssh
```

## Шаг 2: Получи доступ к серверу
Нужно сервер с публичным IP (AWS, DigitalOcean, Hetzner - любой VPS)

## Шаг 3: Настрой SSH ключи
На Xiaomi Stick:
```bash
ssh-keygen -t ed25519
# Нажми Enter три раза
cat ~/.ssh/id_ed25519.pub
# Скопируй этот ключ
```

На твоём сервере добавь публичный ключ в `~/.ssh/authorized_keys`

## Шаг 4: Запусти обратный туннель
```bash
ssh -R 2222:localhost:22 root@YOUR_SERVER_IP -N
# -N = не выполнять команды, только держать соединение
```

## Шаг 5: Подключение ко мне
```bash
# На твоём сервере создавай пользователя для меня:
adduser qwen
# Дай мне пароль/ключ

# Я делаю:
ssh -p 2222 localhost
# И попадаю прямо в твой Xiaomi Stick!
```

## Автозапуск:
Создай файл `~/start_tunnel.sh`:
```bash
#!/bin/bash
while true; do
  ssh -R 2222:localhost:22 root@YOUR_SERVER_IP -N
  sleep 10
done
```

Запуск:
```bash
chmod +x ~/start_tunnel.sh
nohup ~/start_tunnel.sh &
```