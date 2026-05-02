"""app/routers/users.py — регистрация и профиль"""
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from app.database import get_db
from app.deps import get_current_user
from app.limiter import limiter
from app.jwt_utils import create_access_token

router = APIRouter()


class UserRegister(BaseModel):
    tg_id: str


@router.post("/register")
@limiter.limit("5/minute")
async def register(request: Request, body: UserRegister, db=Depends(get_db)):
    # Проверяем существующего
    async with db.execute(
        "SELECT id, plan FROM users WHERE tg_id=?", (body.tg_id,)
    ) as cur:
        existing = await cur.fetchone()

    if existing:
        user_id = existing["id"]
        plan = existing["plan"]
        new = False
    else:
        user_id = str(uuid.uuid4())
        plan = "free"
        new = True
        await db.execute(
            "INSERT INTO users (id, tg_id) VALUES (?,?)",
            (user_id, body.tg_id),
        )
        await db.commit()

    # Генерируем JWT
    token = create_access_token(tg_id=body.tg_id, user_id=user_id)
    
    return {
        "user_id": user_id, 
        "plan": plan, 
        "new": new,
        "access_token": token,
        "token_type": "bearer"
    }


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
