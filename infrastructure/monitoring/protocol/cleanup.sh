#!/bin/bash
# Delete command fragments
sqlite3 /root/protocol/data/protocol.db "DELETE FROM memory_fragments WHERE user_id='99c709eb-878c-41eb-9541-1858320d87e3' AND text IN ('/search','/today','/patterns');"
# Count remaining
sqlite3 /root/protocol/data/protocol.db "SELECT COUNT(*) FROM memory_fragments WHERE user_id='99c709eb-878c-41eb-9541-1858320d87e3' AND text LIKE '/%';"
# Restart service
systemctl restart protocol-bot.service
# Check logs
journalctl -u protocol-bot.service -n 10 --no-pager