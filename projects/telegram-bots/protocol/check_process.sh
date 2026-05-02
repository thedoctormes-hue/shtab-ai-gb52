#!/bin/bash
echo "=== Processes ===" > /root/protocol/process_check.txt
ps aux | grep -E "(protocol|main\.py|aiogram|bot)" >> /root/protocol/process_check.txt 2>&1
echo "" >> /root/protocol/process_check.txt
echo "=== Systemctl status ===" >> /root/protocol/process_check.txt
systemctl status protocol-bot.service >> /root/protocol/process_check.txt 2>&1
echo "Done"