# 60k План: VLESS + REALITY, Белый Список, Сценарии, Логи, Мониторинг

## Обзор
Документация для реализации плана на 60k пользователей с использованием VLESS + REALITY, белых списков, автоматизированных сценариев, логирования и мониторинга.

## Архитектура

### Состав Проекта
1. **VPNDaemonRobot** - Основной проект VLESS + REALITY с поддержкой двух серверов (Warsaw + Florida)
2. **Protocol** - Система личной памяти с ИИ-классификацией
3. **AiderDMrobot** - AI-ассистент для кода (промежуточный этап)
4. **VPNDaemonRobot** - Активный VPN-бот с полным функционалом

### Серверная Инфраструктура
- **Warsaw**: 185.138.90.150:443 (реальный сервер)
- **Florida**: 104.253.1.210:10086 (флористская версия)
- Оба используют VLESS + REALITY с TLS

## Настройки REALITY

### Основные Параметры (Оба Сервера)
- Протокол: VLESS
- Сеть: TCP
- Безопасность: REALITY
- Порт: 443 (Warsaw), 10086 (Florida)
- СNI: www.microsoft.com
- Вывод: false
- Порт XVer: 0

### Серверные Имена (serverNames)
1. www.google.com
2. www.cloudflare.com
3. www.microsoft.com

### Ключи и ID
**Warsaw (локальный):**
- Private Key: iJPbrf-Vv1pePgDQHroLYlnLu3-V6MbndZmJhK7zhns
- Short IDs: a1b2c3d4

**Florida (удаленный):**
- Private Key: SI87jchWXJfK2GOr3e2FL51F-djNDVgVWPiSHq5GfFI
- Short IDs: Анонимные

## Скрипты и Автоматизация

### Основные Функции в VPNDaemonRobot

1. **Генерация Ссылок** (gen_link):
   - Создает VLESS ссылки с реалити
   - Поддерживает выбор сервера (Warsaw/Florida)
   - Формат: vless://UUID@IP:PORT?type=tcp&security=reality&...#email

2. **Подписка** (generate_subscription_content):
   - Баз64 закодированный контент со всеми клиентами
   - Автоматическая генерация для импорта

3. **Логирование:**
   - Xray Access Log: /root/LabDoctorM/VPNDaemonRobot/logs/xray-access.log
   - Xray Error Log: /root/LabDoctorM/VPNDaemonRobot/logs/xray-error.log
   - Bot Log: /root/LabDoctorM/VPNDaemonRobot/logs/bot.log

4. **Мониторинг Клиентов:**
   - get_active() - Количество онлайн пользователей
   - get_last_activity(email) - Последняя активность
   - is_client_online(email, minutes) - Проверка активности за N минут
   - get_recent_activity(limit) - Последние активности

5. **Управление Клиентами:**
   - add_client_to_server() - Добавление клиента на сервер
   - cleanup_inactive_clients() - Очистка неактивных (30/60 дней)

6. **Перезагрузка Xray:**
   - reload_xray() - Перезапуск сервиса

### Сценарии Управления

#### Добавление Клиента
```python
# Локально (Warsaw)
cfg['inbounds'][0]['settings']['clients'].append({
    'id': uuid,
    'email': email,
    'flow': ''
})

# На Florida через SSH
ssh_exec(server_name, f"cat > {cfg_path} << 'XRAYEOF'\n{new_cfg_str}\nXRAYEOF")
ssh_exec(server_name, 'systemctl reload-or-restart xray')
```

#### Генерация Подписки
http://{SERVER_IP}:8081/sub/{TOKEN}

#### Статус Системы
```bash
# Перезапуск Xray
systemctl restart demonvpn

# Статус Xray
systemctl status demonvpn

# Логи Xray
journalctl -u demonvpn -f
```

## Белый Список (Whitelist)

### Настройка в Xray
```json
{
  "inbounds": [{
    "port": 10086,
    "protocol": "vless",
    "settings": {
      "clients": [],
      "decryption": "none"
    }
  }]
}
```

### Управление Белым Списком
- Клиенты добавляются через clients.json
- Формат: {"uuid": "...", "email": "user@example.com", "active": true}
- Проверка происходит на уровне логов и API

## Мониторинг и Логи

### Структура Логов
```
/root/LabDoctorM/VPNDaemonRobot/logs/
├── bot.log
├── xray-access.log
└── xray-error.log
```

### Формат Лога Xray (access)
2026/04/28 10:30:15 accepted tcp email=@DoctorMES from=IP ...

### Формат Лога Бота
2026-04-28 10:30:15| message

### Метрики Мониторинга

#### Пользовательские Метрики
- active_users - Количество активных пользователей
- traffic_inbound - Входящий трафик
- traffic_outbound - Исходящий трафик
- uptime - Время работы

#### Системные Метрики
- CPU Load
- RAM Usage
- Disk Usage
- Xray Process Status

## Эндпоинты API

### Основные Эндпоинты
- GET /settings/exit - Получить настройки
- PUT /settings/exit - Обновить настройки
- /sub/{token} - Подписка (баз64)

### Эндпоинты Бота (Telegram)
- /start - Начало работы
- /status - Статус системы
- /settings - Настройки
- /clients_list - Список клиентов

## Процедуры Обслуживания

### Повседневные
1. Проверка активности пользователей
2. Просмотр логов
3. Проверка статуса серверов

### Ежедневные
1. Очистка старых логов
2. Проверка дискового пространства
3. Резервное копирование

### Еженедельные
1. Очистка неактивных клиентов (30 дней)
2. Проверка целостности конфигурации
3. Обновление сертификатов

### Ежемесячные
1. Полная проверка системы
2. Оптимизация конфигурации
3. Анализ трафика

## Безопасность

### Рекомендации
1. Храните private key в безопасности
2. Используйте сильные пароли для SSH
3. Включайте двухфакторную аутентификацию
4. Регулярно обновляйте зависимости
5. Мониторьте логи на подозрительную активность

### Ограничения
- Максимум 60k клиентов
- Белый список по email
- Трафик ограничен по тарифам
- Автоматическая очистка после 30/60 дней неактивности

## Интеграции

### С Устройства
- Поддержка всех VLESS-клиентов
- Автоматическое получение ссылок
- Статус реального времени

### С Серверов
- Поддержка двух регионов (Warsaw + Florida)
- Автоматическое распределение нагрузки
- Резервирование

### С Телеграм Ботом
- Полный контроль через бота
- Уведомления
- Управление через команды
