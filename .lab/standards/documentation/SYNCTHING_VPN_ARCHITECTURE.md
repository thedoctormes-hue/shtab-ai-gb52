# Архитектура: Syncthing vs VPN

> **ВАЖНО:** Это два НЕЗАВИСИМЫХ компонента. Не смешивать!

---

## Syncthing — Синхронизация файлов

### Назначение
Синхронизация конфигураций и файлов между серверами ЗавЛаба.

### Конфигурация
- **Файл:** `/root/.syncthing/config.xml`
- **Папка:** `/root/.qwen` (ID: qwen-sync)
- **Порт:** 22000/tcp (трафик), 8384/tcp (GUI localhost)

### Устройства (Devices)
| ID | Имя | Адрес | Назначение |
|----|-----|-------|------------|
| TSRGEAU-CIU5PH4... | warsaw | dynamic | РФ-прокси сервер |
| UD6TZSA-O7E7I5U... | florida | tcp://104.253.1.210:22000 | VPN сервер (НЕ для VPN трафика!) |
| W2RCJNY-VZLN6OT... | rf-proxy | tcp://89.169.4.51:22000 | DPI-обход |

### Что синхронизуется
- `/root/.qwen/` — настройки Qwen Code
- `/root/.qwen/shares/` — файлики для расшаривания
- `/root/.qwen/uploads/` — загрузки
- `/root/.qwen/memory/` — память проектов
- `/root/.qwen/todos/` — задачи

---

## VPN Services — Трафик

### Florida VPN Server (185.138.90.150)

#### Сервисы
| Порт | Сервис | Описание |
|------|--------|----------|
| 443/tcp | Xray | VLESS Reality |
| 22000/tcp | Syncthing | Синхронизация (НЕ VPN!) |
| 8384/tcp | Syncthing GUI | Local only |
| 10086/tcp | Xray (alt) | VMess для iOS |

#### Дашборд
- **URL:** `http://185.138.90.150/dashboard-react/`
- **Frontend:** готовый билд (не хранится в LabDoctorM)
- **API:** `/api/backlog/evolution_backlog.json`

#### Проект в LabDoctorM
- **Папка:** `/root/LabDoctorM/vpn-florida-site/`
- **Стек:** React + FastAPI (для лендинга и кабинета, НЕ основного дашборда!)

---

## ИЕРАРХИЯ ПРОЕКТОВ

```
LabDoctorM/
├── vpn-florida-site/         # React лендинг + кабинет (старый, НЕ дашборд)
├── .syncthing/               # Syncthing config (это отдельный сервис!)
└── docs/SYNCTHING_VPN_ARCHITECTURE.md  # Этот файл
```

---

## ПРАВИЛА

1. **Syncthing ≠ VPN** — разные службы, разные порты
2. **Файлы VPN сервера** хранятся в `/root/.qwen/` (через Syncthing)
3. **Дашборд** на Florida (`dashboard-react/`) — отдельный проект
4. **vpn-florida-site** — React-лендинг (не дашборд!)