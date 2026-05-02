# Инциденты лаборатории Doctorm&Ai

## 2026-04-28: Утечка памяти и рестарт-петля Protocol

### ⏰ Время
- **Обнаружение**: 2026-04-28 11:20 MSK
- **Разрешение**: 2026-04-28 11:30 MSK
- **Длительность**: ~10 минут

### 🚨 Симптомы
1. **Memory leak**: Used 2.7 GiB / 3.8 GiB, Swap 1.0 GiB / 2.0 GiB
2. **protocol-bot.service**: рестарт каждые 4-5 секунд (restart loop)
3. **High CPU**: protocol-bot процесс жрал 98.5% CPU
4. **Journald**: раздут до 2.4 GB на диске

### 🔍 Корень зла (Root Cause)
**Цепная реакция:**
1. Порт 8000 был занят старым зомби-процессом `python3` (PID 198547)
2. `protocol.service` (FastAPI) падал с ошибкой: `[Errno 98] Address already in use`
3. `protocol-bot.service` имел директиву `Requires=protocol.service`
4. При падении FastAPI → systemd убивал и перезапускал бота
5. Старые процессы бота НЕ убивались → накапливались зомби
6. Journald раздувался из-за бесконечных логов рестартов

### 🛠️ Что сделали
1. ✅ Нашли и убили процесс-зомби на порту 8000 (PID 198547)
2. ✅ Пофиксили запуск protocol-bot (добавили `run_bot.sh` для чтения .env)
3. ✅ Остановили рестарт-петлю: `systemctl stop protocol-bot && systemctl disable protocol-bot`
4. ✅ Очистили journald: `journalctl --vacuum-size=100M` (свободили 2.3 GB)
5. ✅ Создали drop-in конфиг `/etc/systemd/journald.conf.d/size.conf` (лимит 100M)
6. ✅ Перезапустили `systemd-journald` (память упала с 237 MB → 24 MB)
7. ✅ Запустили `protocol.service` и `protocol-bot.service` (стабильно работают)

### ✅ Финальный статус (на 11:30 MSK)
| Сервис | Статус | PID | Память | CPU |
|--------|--------|-----|--------|-----|
| `protocol` (FastAPI) | ✅ active | 214204 | 43.9M | норма |
| `protocol-bot` (Telegram) | ✅ active | 214205 | 183M | 20% (норма) |
| `demonvpn` (Xray VPN) | ✅ active | 196907 | 7.7M | норма |
| `systemd-journald` | ✅ active | 213194 | 24M | норма |

**Своп**: 1.0 GiB (не очищался, но под контролем)  
**Свободно RAM**: 322 MiB

### 📋 Уроки
1. **Всегда проверяй порты**: `ss -tnp | grep :PORT` перед рестартом сервиса
2. **Не используй `Requires=` для сервисов**: лучше `Wants=` или проверка в ExecStartPre
3. **Лимитируй journald**: прописывай `RuntimeMaxUse=` сразу при развёртывании
4. **Убивай зомби**: `pkill -9 -f "pattern"` при рестарт-петле

### 🔗 Связанные файлы
- `/etc/systemd/system/protocol-bot.service` — исправлен (добавлен `run_bot.sh`)
- `/root/LabDoctorM/protocol/run_bot.sh` — создан (wrapper для .env)
- `/etc/systemd/journald.conf.d/size.conf` — создан (лимиты логов)

---
*Зафиксировано: КотОлизатОр, 2026-04-28 11:32 MSK*

## 2026-04-28: Рестарт-петля x-ui (XRAY REALITY)

### ⏰ Время
- **Обнаружение**: 2026-04-28 17:01 MSK
- **Разрешение**: 2026-04-28 17:22 MSK
- **Длительность**: ~21 минута

### 🚨 Симптомы
1. **x-ui.service**: рестарт каждые 2 секунды (restart loop)
2. **Логи**: `XRAY: Failed to start: non-empty "serverNames", please use "serverName" instead`
3. **Exit code**: 23 при запуске xray
4. **Systemd**: спам ошибками в journald

### 🔍 Корень зла (Root Cause)
**Несовместимость версий x-ui и xray-core 26.x:**
1. x-ui генерил `serverName` (строка) в `realitySettings` для XRAY inbound
2. Xray 26.x **ОЖИДАЕТ** `serverNames` (массив), несмотря на обманчивое сообщение об ошибке
3. Сообщение `"please use "serverName" instead"` — **ЛОЖНОЕ УКАЗАНИЕ** (баг в xray)
4. Дополнительно: xray 26.x требует поле `dest` в `realitySettings`
5. x-ui перезаписывал `/usr/local/x-ui/bin/config.json` при каждом рестарте

**Цепочка событий:**
- Запуск x-ui → генерация config.json со `serverName` → xray падает с exit 23
- Systemd рестарит сервис (Restart=on-failure, RestartSec=5s)
- x-ui снова генерит неверный конфиг → бесконечный цикл

### 🛠️ Что сделали
1. ✅ Остановили x-ui: `systemctl stop x-ui`
2. ✅ Обновили xray до 26.3.27 (было 26.2.6): скачали с GitHub releases
3. ✅ Выяснили истинную причину: xray 26.x требует `serverNames` (массив)
4. ✅ Пофиксили базу x-ui `/etc/x-ui/x-ui.db`:
   - Добавили `serverNames: ["www.tesla.com"]` в `realitySettings`
   - Убрали `serverName` (установили в null)
   - Добавили поле `dest: "www.tesla.com:443"`
5. ✅ Запустили x-ui: `systemctl start x-ui`
6. ✅ Проверили статус: xray запустился успешно, слушает порты 55272 и 48541

### ✅ Финальный статус (на 17:22 MSK)
| Сервис | Статус | PID | Память | CPU |
|--------|--------|-----|--------|-----|
| `x-ui` (Web panel) | ✅ active | 346309 | 33.1M | норма |
| `xray-linux-amd64` | ✅ running | 346317 | ~36M | норма |
| `demonvpn` (Xray VPN) | ✅ active | 196907 | 7.7M | норма |

**Ошибок в логах**: нет
**Рестарт-петля**: прекращена

### 📋 Уроки
1. **Проверяй версии**: x-ui может не поддерживать новые версии xray-core
2. **Читай между строк**: сообщения об ошибках xray могут быть ложными (баги в валидации)
3. **Правь базу, а не конфиг**: x-ui перезаписывает config.json из SQLite базы
4. **Тестируй xray напрямую**: `/usr/local/x-ui/bin/xray-linux-amd64 run -config config.json`
5. **Ложные указания**: сообщение "please use X instead" может означать обратное

### 🔗 Связанные файлы
- `/etc/x-ui/x-ui.db` — пофикшена таблица `inbounds` (stream_settings)
- `/usr/local/x-ui/bin/config.json` — сгенерирован корректно после фикса
- `/usr/local/x-ui/bin/xray-linux-amd64` — обновлён до v26.3.27

### 🐛 Баг xray
Xray 26.x выдаёт ошибку: `infra/conf: non-empty "serverNames", please use "serverName" instead`
**На самом деле**: нужно использовать ИМЕННО `serverNames` (массив), а не `serverName`.

---
*Зафиксировано: КотОлизатОр, 2026-04-28 17:23 MSK*
