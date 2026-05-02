import sqlite3

# Connect to the database
conn = sqlite3.connect('/root/protocol/data/protocol.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Run the first query
cursor.execute("SELECT id, source, text, created_at FROM memory_fragments ORDER BY created_at LIMIT 20")
rows = cursor.fetchall()

output = ["=== memory_fragments ==="]
for row in rows:
    output.append(f"id={row['id']} source={row['source']} created_at={row['created_at']}")
    output.append(f"  text={row['text'][:100] if row['text'] else 'NULL'}...")
    output.append("")

# Check for test records
cursor.execute("SELECT id, source, text FROM memory_fragments WHERE source = 'test' OR text LIKE '%тест%' OR text LIKE '%test%' LIMIT 10")
rows2 = cursor.fetchall()

output.append("=== test records ===")
for row in rows2:
    output.append(f"id={row['id']} source={row['source']} text={row['text'][:50] if row['text'] else 'NULL'}...")

conn.close()

# Write to file
with open('/root/protocol/db_output.txt', 'w') as f:
    f.write('\n'.join(output))

print("Done - wrote output to /root/protocol/db_output.txt")