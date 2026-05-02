#!/bin/bash
# OpenClawBox deployment script

set -e

echo "🔧 Deploying OpenClawBox..."

# Create venv
python -m venv .venv
source .venv/bin/activate

# Install deps
pip install -r requirements.txt

# Copy services
cp openclawbox-api.service /etc/systemd/system/
cp openclawbox-bot.service /etc/systemd/system/

# Reload systemd
systemctl daemon-reload

# Enable services
systemctl enable openclawbox-api
systemctl enable openclawbox-bot

# Start services
systemctl restart openclawbox-api
systemctl restart openclawbox-bot

echo "✅ OpenClawBox deployed!"
echo "API: http://localhost:8000"
echo "Bot: @OpenClawBoxBot"