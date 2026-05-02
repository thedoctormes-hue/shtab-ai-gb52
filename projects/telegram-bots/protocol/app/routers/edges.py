"""
Роутер связей между фрагментами памяти (memory_edges)
POST   /edges      — создать связь
GET    /edges      — список связей (фильтр by from_id/to_id)
GET    /edges/{id} — получить связь
DELETE /edges/{id} — удалить связь
"""

import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.database import get_db
from app.deps import get_current_user

router = APIRouter()


# ── Схемы ────────────────────────────────────────────────────────────────────

class EdgeCreate(BaseModel):
    from_id: str
    to_id: str
    relation_type: str = "similar"  # similar / contradicts / evolves / causes
    weight: float = 1.0


class EdgeOut(BaseModel):
    id: str
    from_id: str
    to_id: str
    relation_type: str
    weight: float
    created_at: str


# ── Эндпоинты ────────────────────────────────────────────────────────────────

@router.post("", response_model=EdgeOut)
async def create_edge(
    body: EdgeCreate,
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    # Проверяем, что оба фрагмента принадлежат пользователю
    async with db.execute(
        "SELECT id FROM memory_fragments WHERE id IN (?, ?) AND user_id=?",
        (body.from_id, body.to_id, user["id"]),
    ) as cur:
        rows = await cur.fetchall()

    if len(rows) != 2:
        raise HTTPException(403, "Фрагменты не найдены или не принадлежат вам")

    edge_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    await db.execute(
        """INSERT INTO memory_edges (id, from_id, to_id, relation_type, weight, created_at)
           VALUES (?,?,?,?,?,?)""",
        (edge_id, body.from_id, body.to_id, body.relation_type, body.weight, now),
    )
    await db.commit()

    return EdgeOut(
        id=edge_id,
        from_id=body.from_id,
        to_id=body.to_id,
        relation_type=body.relation_type,
        weight=body.weight,
        created_at=now,
    )


@router.get("", response_model=list[EdgeOut])
async def list_edges(
    from_id: str = Query(None, description="Фильтр по исходному фрагменту"),
    to_id: str = Query(None, description="Фильтр по целевому фрагменту"),
    limit: int = Query(50, le=100),
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    # Базовый запрос с join на fragments для проверки прав
    sql = """
        SELECT e.* FROM memory_edges e
        JOIN memory_fragments f1 ON e.from_id = f1.id
        JOIN memory_fragments f2 ON e.to_id = f2.id
        WHERE f1.user_id = ? AND f2.user_id = ?
    """
    params = [user["id"], user["id"]]

    if from_id:
        sql += " AND e.from_id = ?"
        params.append(from_id)
    if to_id:
        sql += " AND e.to_id = ?"
        params.append(to_id)

    sql += " ORDER BY e.created_at DESC LIMIT ?"
    params.append(limit)

    async with db.execute(sql, params) as cur:
        rows = await cur.fetchall()

    return [EdgeOut(**dict(r)) for r in rows]


@router.get("/{edge_id}", response_model=EdgeOut)
async def get_edge(
    edge_id: str,
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    sql = """
        SELECT e.* FROM memory_edges e
        JOIN memory_fragments f1 ON e.from_id = f1.id
        JOIN memory_fragments f2 ON e.to_id = f2.id
        WHERE e.id = ? AND f1.user_id = ? AND f2.user_id = ?
    """
    async with db.execute(sql, (edge_id, user["id"], user["id"])) as cur:
        row = await cur.fetchone()

    if not row:
        raise HTTPException(404, "Связь не найдена")

    return EdgeOut(**dict(row))


@router.delete("/{edge_id}")
async def delete_edge(
    edge_id: str,
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    sql = """
        DELETE FROM memory_edges
        WHERE id = (
            SELECT e.id FROM memory_edges e
            JOIN memory_fragments f1 ON e.from_id = f1.id
            JOIN memory_fragments f2 ON e.to_id = f2.id
            WHERE e.id = ? AND f1.user_id = ? AND f2.user_id = ?
        )
    """
    cursor = await db.execute(sql, (edge_id, user["id"], user["id"]))
    await db.commit()

    if cursor.rowcount == 0:
        raise HTTPException(404, "Связь не найдена")

    return {"ok": True, "message": "Связь удалена"}
