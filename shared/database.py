"""
Shared database module — SQLite + WAL + FTS5
Схема v2.0 — объединённый вариант из protocol и infrastructure
"""
from typing import Optional
import aiosqlite
from pathlib import Path

DB_PATH = Path("data/protocol.db")


async def get_connection() -> aiosqlite.Connection:
    """Создать и настроить соединение с БД."""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def get_db() -> aiosqlite.Connection:
    """Возвращает соединение с БД."""
    return await get_connection()


async def init_db():
    """Инициализация БД."""
    DB_PATH.parent.mkdir(exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("PRAGMA foreign_keys=ON")
        await db.executescript(SCHEMA)
        await db.commit()


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id              TEXT PRIMARY KEY,
    tg_id           TEXT UNIQUE,
    encryption_key  TEXT,
    plan            TEXT DEFAULT 'free',
    created_at      TEXT DEFAULT (datetime('now')),
    last_active_at  TEXT DEFAULT (datetime('now')),
    meta            TEXT DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS memory_fragments (
    id                  TEXT PRIMARY KEY,
    user_id             TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    text                TEXT NOT NULL,
    summary             TEXT,
    semantic_vector     TEXT DEFAULT '{}',
    emotion             TEXT DEFAULT '{}',
    three_interpretations TEXT DEFAULT '[]',
    conflict_detected   INTEGER DEFAULT 0,
    unknown_type        INTEGER DEFAULT 0,
    weight              REAL DEFAULT 1.0,
    privacy             TEXT DEFAULT 'private',
    source              TEXT DEFAULT 'text',
    confidence          REAL DEFAULT 0.0,
    created_at          TEXT DEFAULT (datetime('now')),
    last_accessed_at    TEXT DEFAULT (datetime('now')),
    meta                TEXT DEFAULT '{}'
);

CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
    fragment_id,
    text,
    summary,
    content='memory_fragments',
    content_rowid='rowid'
);

CREATE TABLE IF NOT EXISTS memory_edges (
    id              TEXT PRIMARY KEY,
    from_id         TEXT NOT NULL REFERENCES memory_fragments(id) ON DELETE CASCADE,
    to_id           TEXT NOT NULL REFERENCES memory_fragments(id) ON DELETE CASCADE,
    weight          REAL DEFAULT 1.0,
    relation_type   TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS people (
    id              TEXT PRIMARY KEY,
    user_id         TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    alias           TEXT,
    role            TEXT,
    first_seen_at   TEXT DEFAULT (datetime('now')),
    meta            TEXT DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS people_edges (
    id          TEXT PRIMARY KEY,
    person_id   TEXT NOT NULL REFERENCES people(id) ON DELETE CASCADE,
    fragment_id TEXT NOT NULL REFERENCES memory_fragments(id) ON DELETE CASCADE,
    emotion     TEXT,
    context     TEXT,
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS patterns (
    id              TEXT PRIMARY KEY,
    user_id         TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    description     TEXT NOT NULL,
    occurrences     INTEGER DEFAULT 1,
    first_seen_at   TEXT DEFAULT (datetime('now')),
    last_seen_at    TEXT DEFAULT (datetime('now')),
    meta            TEXT DEFAULT '{}',
    UNIQUE(user_id, description)
);

CREATE TABLE IF NOT EXISTS exit_settings (
    user_id             TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    export_format       TEXT DEFAULT 'bundle',
    public_categories   TEXT DEFAULT '[]',
    trusted_tg_id       TEXT,
    auto_delete_days    INTEGER DEFAULT 90,
    farewell_message    TEXT,
    meta                TEXT DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_fragments_user     ON memory_fragments(user_id);
CREATE INDEX IF NOT EXISTS idx_fragments_weight   ON memory_fragments(weight DESC);
CREATE INDEX IF NOT EXISTS idx_fragments_created  ON memory_fragments(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_people_user        ON people(user_id);
CREATE INDEX IF NOT EXISTS idx_people_edges       ON people_edges(person_id, fragment_id);
CREATE INDEX IF NOT EXISTS idx_memory_edges_from  ON memory_edges(from_id);
CREATE INDEX IF NOT EXISTS idx_patterns_user      ON patterns(user_id, last_seen_at DESC);

CREATE TRIGGER IF NOT EXISTS fts_insert AFTER INSERT ON memory_fragments BEGIN
    INSERT INTO memory_fts(rowid, fragment_id, text, summary)
    VALUES (new.rowid, new.id, new.text, COALESCE(new.summary, ''));
END;

CREATE TRIGGER IF NOT EXISTS fts_delete AFTER DELETE ON memory_fragments BEGIN
    DELETE FROM memory_fts WHERE rowid = old.rowid;
END;
"""


async def search_fragments(user_id: str, query: str, offset: int = 0) -> list[dict]:
    """Поиск фрагментов по FTS5."""
    db = await get_db()
    try:
        sql = """
            SELECT
                mf.id,
                mf.summary,
                mf.created_at,
                mf.semantic_vector
            FROM memory_fts
            JOIN memory_fragments mf ON memory_fts.rowid = mf.rowid
            WHERE memory_fts MATCH ?
              AND mf.user_id = ?
            ORDER BY rank
            LIMIT 3 OFFSET ?
        """
        fts_query = query.lower()
        cursor = await db.execute(sql, (fts_query, user_id, offset))
        rows = await cursor.fetchall()
        return [{"id": r["id"], "summary": r["summary"], "created_at": r["created_at"], "semantic_vector": r["semantic_vector"]} for r in rows]
    finally:
        await db.close()


async def get_today_fragments(user_id: str) -> list[dict]:
    """Получить фрагменты за сегодня."""
    db = await get_db()
    try:
        sql = """
            SELECT id, summary, text, semantic_vector, weight, confidence, created_at
            FROM memory_fragments
            WHERE user_id = ?
              AND date(created_at, '+3 hours') = date('now', '+3 hours')
            ORDER BY created_at ASC
        """
        cursor = await db.execute(sql, (user_id,))
        rows = await cursor.fetchall()
        return [{"id": r["id"], "summary": r["summary"], "text": r["text"], "semantic_vector": r["semantic_vector"], "weight": r["weight"], "confidence": r["confidence"], "created_at": r["created_at"]} for r in rows]
    finally:
        await db.close()


async def get_user_by_tg_id(tg_id: str) -> Optional[dict]:
    """Получить user_id по tg_id."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT id FROM users WHERE tg_id = ?", (tg_id,))
        row = await cursor.fetchone()
        return {"id": row["id"]} if row else None
    finally:
        await db.close()


async def get_user_by_id(user_id: str) -> Optional[dict]:
    """Получить пользователя по user_id."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT id, tg_id, plan FROM users WHERE id = ?", (user_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None
    finally:
        await db.close()


async def get_last_fragment_date(user_id: str) -> Optional[str]:
    """Получить дату последнего фрагмента."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT created_at FROM memory_fragments WHERE user_id = ? ORDER BY created_at DESC LIMIT 1", (user_id,))
        row = await cursor.fetchone()
        return row["created_at"] if row else None
    finally:
        await db.close()


async def get_patterns(user_id: str) -> list[dict]:
    """Получить паттерны пользователя."""
    db = await get_db()
    try:
        cursor = await db.execute("""
            SELECT description, occurrences, last_seen_at, first_seen_at
            FROM patterns
            WHERE user_id = ?
            ORDER BY last_seen_at DESC
            LIMIT 5
        """, (user_id,))
        rows = await cursor.fetchall()
        return [{"description": r["description"], "occurrences": r["occurrences"], "last_seen_at": r["last_seen_at"], "first_seen_at": r["first_seen_at"]} for r in rows]
    finally:
        await db.close()


async def upsert_pattern(user_id: str, description: str) -> None:
    """Upsert паттерна."""
    import uuid
    db = await get_db()
    try:
        cursor = await db.execute("SELECT id, occurrences FROM patterns WHERE user_id = ? AND description = ?", (user_id, description))
        row = await cursor.fetchone()
        if row:
            await db.execute("UPDATE patterns SET occurrences = ?, last_seen_at = datetime('now') WHERE id = ?", (row["occurrences"] + 1, row["id"]))
        else:
            await db.execute("INSERT INTO patterns (id, user_id, description, occurrences, first_seen_at, last_seen_at, meta) VALUES (?, ?, ?, 1, datetime('now'), datetime('now'), '{}')", (str(uuid.uuid4()), user_id, description))
        await db.commit()
    finally:
        await db.close()


async def get_today_pattern(user_id: str) -> dict | None:
    """Получить паттерн дня."""
    db = await get_db()
    try:
        sql = """
            SELECT description, occurrences
            FROM patterns
            WHERE user_id = ?
              AND date(last_seen_at, '+3 hours') = date('now', '+3 hours')
            ORDER BY occurrences DESC
            LIMIT 1
        """
        cursor = await db.execute(sql, (user_id,))
        row = await cursor.fetchone()

        if row:
            return {
                "description": row["description"],
                "occurrences": row["occurrences"]
            }
        return None
    finally:
        await db.close()


async def get_recent_fragments(user_id: str) -> list[dict]:
    """Получить фрагменты за последние 24 часа."""
    db = await get_db()
    try:
        cursor = await db.execute("""
            SELECT id, text, summary FROM memory_fragments
            WHERE user_id = ? AND created_at >= datetime('now', '-24 hours')
            ORDER BY created_at ASC
        """, (user_id,))
        rows = await cursor.fetchall()
        return [{"id": r["id"], "text": r["text"], "summary": r["summary"]} for r in rows]
    finally:
        await db.close()


async def get_people_edges(fragment_id: Optional[str] = None, person_id: Optional[str] = None) -> list[dict]:
    """Получить связи людей с фрагментами."""
    db = await get_db()
    try:
        sql = "SELECT * FROM people_edges WHERE 1=1"
        params = []
        if fragment_id:
            sql += " AND fragment_id = ?"
            params.append(fragment_id)
        if person_id:
            sql += " AND person_id = ?"
            params.append(person_id)
        sql += " ORDER BY created_at DESC"
        cursor = await db.execute(sql, params)
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        await db.close()


async def get_all_user_ids() -> list[str]:
    """Получить все user_id с фрагментами."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT DISTINCT user_id FROM memory_fragments")
        rows = await cursor.fetchall()
        return [r["user_id"] for r in rows]
    finally:
        await db.close()