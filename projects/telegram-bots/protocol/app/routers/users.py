"""app/routers/users.py — регистрация и профиль"""
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.database import get_db
from app.deps import get_current_user

router = APIRouter()


class UserRegister(BaseModel):
    tg_id: str


@router.post("/register")
async def register(body: UserRegister, db=Depends(get_db)):
    # Проверяем существующего
    async with db.execute(
        "SELECT id, plan FROM users WHERE tg_id=?", (body.tg_id,)
    ) as cur:
        existing = await cur.fetchone()

    if existing:
        return {"user_id": existing["id"], "plan": existing["plan"], "new": False}

    user_id = str(uuid.uuid4())
    await db.execute(
        "INSERT INTO users (id, tg_id) VALUES (?,?)",
        (user_id, body.tg_id),
    )
    await db.commit()
    return {"user_id": user_id, "plan": "free", "new": True}


@router.get("/me")
async def me(user=Depends(get_current_user)):
    return user


@router.get("/me/stats")
async def my_stats(user=Depends(get_current_user), db=Depends(get_db)):
    async with db.execute(
        "SELECT COUNT(*) as total FROM memory_fragments WHERE user_id=?",
        (user["id"],),
    ) as cur:
        row = await cur.fetchone()
    total = row["total"]

    async with db.execute(
        "SELECT COUNT(*) as cnt FROM people WHERE user_id=?", (user["id"],)
    ) as cur:
        people_row = await cur.fetchone()

    return {
        "fragments_total": total,
        "people_total": people_row["cnt"],
        "magic_trigger_distance": max(0, 47 - total),
        "plan": user["plan"],
    }
