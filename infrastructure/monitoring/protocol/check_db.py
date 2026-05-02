#!/usr/bin/env python3
import sqlite3
import sys

conn = sqlite3.connect("/root/LabDoctorM/protocol/data/protocol.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Сначала посмотреть что есть
print("=== memory_fragments ===")
cursor.execute("SELECT id, source, text, created_at FROM memory_fragments ORDER BY created_at LIMIT 20")
rows = cursor.fetchall()
for row in rows:
    print(f"id={row['id']} source={row['source']} created_at={row['created_at']}")
    print(f"  text={row['text'][:100] if row['text'] else 'NULL'}...")
    print()

# Проверить есть ли тестовые записи
print("\n=== test records ===")
cursor.execute("SELECT id, source, text FROM memory_fragments WHERE source = 'test' OR text LIKE '%тест%' OR text LIKE '%test%' LIMIT 10")
rows = cursor.fetchall()
for row in rows:
    print(f"id={row['id']} source={row['source']} text={row['text'][:50] if row['text'] else 'NULL'}...")

conn.close()