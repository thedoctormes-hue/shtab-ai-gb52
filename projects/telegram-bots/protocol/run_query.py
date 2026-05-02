import subprocess
import os

os.makedirs("/root/protocol/data", exist_ok=True)

result1 = subprocess.run(
    ["sqlite3", "/root/protocol/data/protocol.db",
     "DELETE FROM memory_fragments WHERE user_id IN (SELECT id FROM users WHERE tg_id IN ('999999','tg_test_user_fts','fts_test_99','fts_test_3c8849ba','fts_9e9f2a72','fts_e1159a08'));"],
    capture_output=True, text=True)

result2 = subprocess.run(
    ["sqlite3", "/root/protocol/data/protocol.db",
     "DELETE FROM users WHERE tg_id IN ('999999','tg_test_user_fts','fts_test_99','fts_test_3c8849ba','fts_9e9f2a72','fts_e1159a08');"],
    capture_output=True, text=True)

result3 = subprocess.run(
    ["sqlite3", "/root/protocol/data/protocol.db", "SELECT COUNT(*) FROM users;"],
    capture_output=True, text=True)

with open("/root/protocol/cleanup_output.txt", "w") as f:
    f.write("Users count: " + result3.stdout)