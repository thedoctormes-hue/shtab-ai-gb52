#!/bin/bash
echo "=== Process check ===" > /root/protocol/logs.txt
ps aux | grep -E "(protocol|main\.py|aiogram)" >> /root/protocol/logs.txt 2>&1
echo "" >> /root/protocol/logs.txt
echo "=== Systemctl status ===" >> /root/protocol/logs.txt
systemctl status protocol-bot.service >> /root/protocol/logs.txt 2>&1
echo "" >> /root/protocol/logs.txt
echo "=== Journalctl ===" >> /root/protocol/logs.txt
journalctl -u protocol-bot.service -n 20 --no-pager >> /root/protocol/logs.txt 2>&1
echo "Done" >> /root/protocol/logs.txt