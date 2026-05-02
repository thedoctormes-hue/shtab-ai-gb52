import sqlite3
conn = sqlite3.connect("/root/LabDoctorM/protocol/data/protocol.db")
cursor = conn.cursor()

# Delete test fragments
cursor.execute("""
DELETE FROM memory_fragments 
WHERE user_id IN (
    SELECT id FROM users 
    WHERE tg_id IN (
        '999999','tg_test_user_fts','fts_test_99',
        'fts_test_3c8849ba','fts_9e9f2a72','fts_e1159a08'
    )
)
""")

# Delete test users
cursor.execute("""
DELETE FROM users 
WHERE tg_id IN (
    '999999','tg_test_user_fts','fts_test_99',
    'fts_test_3c8849ba','fts_9e9f2a72','fts_e1159a08'
)
""")

conn.commit()

# Check count
cursor.execute("SELECT COUNT(*) FROM users")
count = cursor.fetchone()[0]
print(f"Users count: {count}")

conn.close()