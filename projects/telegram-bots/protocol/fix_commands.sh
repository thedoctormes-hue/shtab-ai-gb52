#!/bin/bash
echo "=== Step 1: Check F.text filter ==="
grep -n "F.text" /root/protocol/bot/main.py

echo ""
echo "=== Step 2: Delete command fragments ==="
sqlite3 /root/protocol/data/protocol.db "DELETE FROM memory_fragments WHERE user_id='99c709eb-878c-41eb-9541-1858320d87e3' AND text IN ('/search','/today','/patterns');"

echo ""
echo "=== Step 3: Check remaining command fragments ==="
sqlite3 /root/protocol/data/protocol.db "SELECT COUNT(*) FROM memory_fragments WHERE user_id='99c709eb-878c-41eb-9541-1858320d87e3' AND text LIKE '/%';"

echo ""
echo "=== Step 4: Restart bot ==="
systemctl restart protocol-bot.service

echo ""
echo "=== Step 5: Check logs ==="
journalctl -u protocol-bot.service -n 10 --no-pager