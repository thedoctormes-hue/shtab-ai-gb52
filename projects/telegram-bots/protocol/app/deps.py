"""app/deps.py — зависимости FastAPI"""
from fastapi import Header, HTTPException, Depends
import aiosqlite
from app.database import DB_PATH
from app.jwt_utils import decode_token


async def get_db():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("PRAGMA foreign_keys=ON")
        yield db


async def get_current_user(
    authorization: str = Header(None, alias="Authorization"),
    db=Depends(get_db),
):
    """
    JWT-авторизация через заголовок Authorization: Bearer <token>
    """
    if not authorization:
        raise HTTPException(401, "Missing Authorization header")
    scheme, _, token = authorization.partition(' ')
    if scheme.lower() != 'bearer' or not token:
        raise HTTPException(401, "Invalid Authorization header format")

    payload = decode_token(token)
    tg_id = payload.get("tg_id")
    if not tg_id:
        raise HTTPException(401, "Invalid token payload")

    async with db.execute(
        "SELECT id, tg_id, plan, meta FROM users WHERE tg_id=?", (tg_id,)
    ) as cur:
        user = await cur.fetchone()

    if not user:
        raise HTTPException(401, "Пользователь не найден")

    # Обновляем last_active_at
    await db.execute(
        "UPDATE users SET last_active_at=datetime('now') WHERE id=?", (user["id"],)
    )
    await db.commit()

    return dict(user)
