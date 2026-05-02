"""SQLite database for OpenClawBox bot."""

import sqlite3
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from contextlib import contextmanager


DB_PATH = Path(__file__).parent.parent / "openclaw.db"


@dataclass
class User:
    telegram_id: int
    api_key: str
    tier: str = "freemium"
    daily_limit: int = 5000
    used_today: int = 0


def init_db():
    """Initialize database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            api_key TEXT UNIQUE NOT NULL,
            tier TEXT DEFAULT 'freemium',
            daily_limit INTEGER DEFAULT 5000,
            used_today INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS usage_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            provider TEXT,
            tokens INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def create_user(telegram_id: int) -> str:
    """Create user and return API key."""
    import secrets
    api_key = f"ocb_sk_{secrets.token_urlsafe(24)}"
    
    with get_db() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT OR IGNORE INTO users (telegram_id, api_key) VALUES (?, ?)",
            (telegram_id, api_key)
        )
        conn.commit()
    
    return api_key


def get_user(telegram_id: int) -> Optional[User]:
    """Get user by telegram_id."""
    with get_db() as conn:
        c = conn.cursor()
        row = c.execute(
            "SELECT * FROM users WHERE telegram_id = ?",
            (telegram_id,)
        ).fetchone()
        
        if not row:
            return None
        
        return User(
            telegram_id=row["telegram_id"],
            api_key=row["api_key"],
            tier=row["tier"],
            daily_limit=row["daily_limit"],
            used_today=row["used_today"]
        )


def increment_usage(telegram_id: int, tokens: int, provider: str):
    """Increment user usage."""
    with get_db() as conn:
        c = conn.cursor()
        c.execute(
            "UPDATE users SET used_today = used_today + ? WHERE telegram_id = ?",
            (tokens, telegram_id)
        )
        c.execute(
            "INSERT INTO usage_log (telegram_id, provider, tokens) VALUES (?, ?, ?)",
            (telegram_id, provider, tokens)
        )
        conn.commit()


def reset_daily_usage():
    """Reset daily usage at midnight."""
    with get_db() as conn:
        conn.execute("UPDATE users SET used_today = 0")
        conn.commit()


def get_usage_stats(telegram_id: int) -> dict:
    """Get usage statistics for user."""
    user = get_user(telegram_id)
    if not user:
        return {}
    
    remaining = user.daily_limit - user.used_today
    percentage = (user.used_today / user.daily_limit) * 100 if user.daily_limit > 0 else 0
    
    return {
        "used_today": user.used_today,
        "daily_limit": user.daily_limit,
        "remaining": remaining,
        "percentage": round(percentage, 1)
    }


# Initialize on import
init_db()