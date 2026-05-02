"""app/routers/patterns.py"""
from fastapi import APIRouter, Depends
from app.database import get_db
from app.deps import get_current_user

router = APIRouter()


@router.get("")
async def list_patterns(user=Depends(get_current_user), db=Depends(get_db)):
    async with db.execute(
        """
        SELECT id, description, occurrences, first_seen_at, last_seen_at
        FROM patterns
        WHERE user_id=?
        ORDER BY last_seen_at DESC
        """,
        (user["id"],),
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]
