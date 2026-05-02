#!/bin/bash
sqlite3 /root/protocol/data/protocol.db "
DELETE FROM memory_fragments 
WHERE user_id IN (
    SELECT id FROM users 
    WHERE tg_id IN (
        '999999','tg_test_user_fts','fts_test_99',
        'fts_test_3c8849ba','fts_9e9f2a72','fts_e1159a08'
    )
);
DELETE FROM users 
WHERE tg_id IN (
    '999999','tg_test_user_fts','fts_test_99',
    'fts_test_3c8849ba','fts_9e9f2a72','fts_e1159a08'
);
"
echo "Users count:"
sqlite3 /root/protocol/data/protocol.db "SELECT COUNT(*) FROM users;"