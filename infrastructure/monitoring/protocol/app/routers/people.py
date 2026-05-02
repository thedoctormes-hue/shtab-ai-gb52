"""
Роутер для работы с людьми (people)
GET  /people       — список людей (с количеством фрагментов и связей)
GET  /people/{person_id}  — детали человека + связанные фрагменты + связи
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from app.database import get_db
from app.deps import get_current_user

router = APIRouter()


@router.get("")
async def list_people(
    user=Depends(get_current_user),
    db=Depends(get_db),
    limit: int = Query(50, le=100),
):
    """Список людей, упомянутых в фрагментах пользователя."""
    async with db.execute(
        """
        SELECT 
            p.id,
            p.name,
            COUNT(DISTINCT pe.fragment_id) as fragment_count,
            COUNT(DISTINCT me.id) as edge_count
        FROM people p
        LEFT JOIN people_edges pe ON p.id = pe.person_id
        LEFT JOIN memory_fragments mf ON pe.fragment_id = mf.id AND mf.user_id = ?
        LEFT JOIN memory_edges me ON (me.from_id = mf.id OR me.to_id = mf.id)
        WHERE p.user_id = ?
        GROUP BY p.id
        ORDER BY p.name
        LIMIT ?
        """,
        (user["id"], user["id"], limit),
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


@router.get("/{person_id}")
async def get_person(
    person_id: str,
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    """Детали человека + его фрагменты и связи."""
    # Проверяем, что человек принадлежит пользователю
    async with db.execute(
        "SELECT id, name FROM people WHERE id = ? AND user_id = ?",
        (person_id, user["id"]),
    ) as cur:
        person = await cur.fetchone()
    if not person:
        raise HTTPException(404, "Человек не найден")

    # Фрагменты
    async with db.execute(
        """
        SELECT mf.id, mf.text, mf.summary, mf.source, mf.privacy, mf.created_at
        FROM memory_fragments mf
        JOIN people_edges pe ON mf.id = pe.fragment_id
        WHERE pe.person_id = ? AND mf.user_id = ?
        ORDER BY mf.created_at DESC
        """,
        (person_id, user["id"]),
    ) as cur:
        fragments = [dict(r) for r in await cur.fetchall()]

    # Связи (edges), где фрагменты принадлежат этому человеку
    async with db.execute(
        """
        SELECT me.id, me.relation_type, 
               CASE WHEN mf.id = me.from_id THEN mf2.user_id ELSE mf.id END as other_person_id,
               p2.name as other_name
        FROM memory_edges me
        JOIN memory_fragments mf ON (me.from_id = mf.id OR me.to_id = mf.id)
        JOIN people_edges pe ON mf.id = pe.fragment_id
        LEFT JOIN memory_fragments mf2 ON (me.from_id = mf2.id OR me.to_id = mf2.id) AND mf2.id != mf.id
        LEFT JOIN people_edges pe2 ON mf2.id = pe2.fragment_id
        LEFT JOIN people p2 ON pe2.person_id = p2.id AND p2.id != ?
        WHERE pe.person_id = ? AND mf.user_id = ?
        LIMIT 50
        """,
        (person_id, person_id, user["id"]),
    ) as cur:
        edges_rows = await cur.fetchall()
    
    edges = []
    seen = set()
    for r in edges_rows:
        if r["id"] not in seen:
            seen.add(r["id"])
            edges.append({
                "id": r["id"],
                "person_id": r["other_person_id"] or "",
                "relation_type": r["relation_type"],
                "name": r["other_name"] or "Unknown"
            })

    return {
        "id": person["id"],
        "name": person["name"],
        "fragment_count": len(fragments),
        "edge_count": len(edges),
        "fragments": fragments,
        "edges": edges,
    }
