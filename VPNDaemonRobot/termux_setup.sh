#!/data/data/com.termux/files/usr/bin/bash
# Auto-setup honeynet worker на Xiaomi Stick

pkg update && pkg upgrade -y
pkg install python wget curl proot-distro -y

# Tailscale для удалённого доступа
curl -fsSL https://tailscale.com/install.sh | sh

# Клонируем honeynet
mkdir -p ~/honeynet
cd ~/honeynet

# Worker скрипт (создаст отдельно)
cat > honeynet_worker.py << 'EOF'
import asyncio, json, random, time
from pathlib import Path

CONFIGS_URL = "http://YOUR_CLOUD_FLARE_TUNNEL/api/configs"

async def spam_dpi():
    while True:
        # Имитируем VLESS/XHTTP соединение
        print(f"[{time.strftime('%H:%M:%S')}] 🔁 Трафик к honeynet")
        await asyncio.sleep(random.randint(30, 90))

if __name__ == "__main__":
    print("🐝 Honeynet Worker запущен на Xiaomi Stick!")
    asyncio.run(spam_dpi())
EOF

# Автозапуск при старте Android TV
mkdir -p ~/.termux/boot
cat > ~/.termux/boot/start_honeynet.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/honeynet
python honeynet_worker.py
EOF
chmod +x ~/.termux/boot/start_honeynet.sh

echo "✅ Termux setup завершён!"
echo "Запусти: tailscale up --ssh"
echo "Затем: cd ~/honeynet && python honeynet_worker.py"