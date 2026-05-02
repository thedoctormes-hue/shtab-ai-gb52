import asyncio, aiosqlite, uuid

async def fix():
    async with aiosqlite.connect("/root/protocol/data/protocol.db") as db:
        db.row_factory = aiosqlite.Row
        uid = str(uuid.uuid4())
        fid = str(uuid.uuid4())
        await db.execute("INSERT INTO users (id, tg_id) VALUES (?,?)", (uid, uid[:8]))
        await db.execute("INSERT INTO memory_fragments (id, user_id, text, summary) VALUES (?,?,?,?)",
            (fid, uid, "контракт Метабокс", "тест"))
        await db.commit()
        async with db.execute("SELECT * FROM memory_fts WHERE memory_fts MATCH ?", ("контракт",)) as cur:
            rows = await cur.fetchall()
            print("FTS results:", len(rows))
            for r in rows:
                print(dict(r))
        await db.execute("DELETE FROM memory_fragments WHERE user_id=?", (uid,))
        await db.execute("DELETE FROM users WHERE id=?", (uid,))
        await db.commit()

asyncio.run(fix())
