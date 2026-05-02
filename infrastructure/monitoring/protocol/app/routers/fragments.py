"""
Роутер фрагментов памяти
POST /fragments        — создать + классифицировать
GET  /fragments        — список с фильтрами
GET  /fragments/search — FTS поиск
GET  /fragments/{id}   — один фрагмент
"""

import json
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel

from app.database import get_db
from app.classifier import classify_fragment
from app.people import extract_and_save_people
from app.deps import get_current_user
from app.limiter import limiter

router = APIRouter()

MAGIC_TRIGGER = 47  # момент магии


# ── Схемы ────────────────────────────────────────────────────────────────────

class FragmentIn(BaseModel):
    text: str
    source: str = "text"   # voice / text / file
    privacy: str = "private"


class FragmentOut(BaseModel):
    id: str
    summary: str
    semantic_vector: dict
    emotion: dict
    three_interpretations: list
    conflict_detected: bool
    unknown_type: bool
    people: list
    tags: list
    confidence: float
    source: str
    privacy: str
    created_at: str
    magic_trigger: bool = False  # флаг: ты на 47-м фрагменте


# ── Эндпоинты ────────────────────────────────────────────────────────────────

@router.post("", response_model=FragmentOut)
@limiter.limit("30/minute")
async def create_fragment(
    request: Request,
    body: FragmentIn,
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    # 1. Классифицируем
    classified = await classify_fragment(body.text)

    fragment_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    # 2. Сохраняем фрагмент
    await db.execute(
        """
        INSERT INTO memory_fragments
            (id, user_id, text, summary, semantic_vector, emotion,
             three_interpretations, conflict_detected, unknown_type,
             confidence, source, privacy, created_at, last_accessed_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            fragment_id,
            user["id"],
            body.text,
            classified["summary"],
            json.dumps(classified["semantic_vector"], ensure_ascii=False),
            json.dumps(classified["emotion"], ensure_ascii=False),
            json.dumps(classified["three_interpretations"], ensure_ascii=False),
            int(classified["conflict_detected"]),
            int(classified["unknown_type"]),
            classified["confidence"],
            body.source,
            body.privacy,
            now,
            now,
        ),
    )
    await db.commit()

    # 3. Люди (NER из классификатора)
    if classified.get("people"):
        await extract_and_save_people(
            db, user["id"], fragment_id, classified["people"], classified["emotion"]
        )

    # 4. Считаем фрагменты — проверяем магический триггер
    async with db.execute(
        "SELECT COUNT(*) FROM memory_fragments WHERE user_id=?", (user["id"],)
    ) as cur:
        row = await cur.fetchone()
        total = row[0]

    magic = (total == MAGIC_TRIGGER)

    return FragmentOut(
        id=fragment_id,
        summary=classified["summary"],
        semantic_vector=classified["semantic_vector"],
        emotion=classified["emotion"],
        three_interpretations=classified["three_interpretations"],
        conflict_detected=classified["conflict_detected"],
        unknown_type=classified["unknown_type"],
        people=classified.get("people", []),
        tags=classified.get("tags", []),
        confidence=classified["confidence"],
        source=body.source,
        privacy=body.privacy,
        created_at=now,
        magic_trigger=magic,
    )


@router.get("")
async def list_fragments(
    limit: int = Query(20, le=100),
    offset: int = 0,
    count_only: bool = Query(False),
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    if count_only:
        async with db.execute(
            "SELECT COUNT(*) as total FROM memory_fragments WHERE user_id=?",
            (user["id"],),
        ) as cur:
            row = await cur.fetchone()
        return {"total": row["total"]}

    async with db.execute(
        """
        SELECT id, text, summary, semantic_vector, emotion, confidence,
               source, privacy, created_at, conflict_detected
        FROM memory_fragments
        WHERE user_id=?
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
        """,
        (user["id"], limit, offset),
    ) as cur:
        rows = await cur.fetchall()

    return [dict(r) for r in rows]


@router.get("/search")
async def search_fragments(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, le=50),
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    """FTS5 полнотекстовый поиск по фрагментам пользователя"""
    async with db.execute(
        """
        SELECT f.id, f.summary, f.created_at, f.confidence
        FROM memory_fts
        JOIN memory_fragments f ON f.rowid = memory_fts.rowid
        WHERE memory_fts MATCH ?
          AND f.user_id = ?
        ORDER BY rank
        LIMIT ?
        """,
        (q, user["id"], limit),
    ) as cur:
        rows = await cur.fetchall()

    return [dict(r) for r in rows]


@router.get("/{fragment_id}")
async def get_fragment(
    fragment_id: str,
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    async with db.execute(
        "SELECT * FROM memory_fragments WHERE id=? AND user_id=?",
        (fragment_id, user["id"]),
    ) as cur:
        row = await cur.fetchone()

    if not row:
        raise HTTPException(404, "Фрагмент не найден")

    # Обновляем last_accessed_at
    await db.execute(
        "UPDATE memory_fragments SET last_accessed_at=datetime('now') WHERE id=?",
        (fragment_id,),
    )
    await db.commit()

    return dict(row)
