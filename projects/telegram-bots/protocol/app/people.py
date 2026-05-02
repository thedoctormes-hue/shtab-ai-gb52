"""app/people.py — сохранение людей из NER классификатора"""
import uuid
from datetime import datetime


async def extract_and_save_people(db, user_id: str, fragment_id: str, names: list, emotion: dict):
    """
    Сохраняет людей из фрагмента.
    Если человек уже есть — только добавляет связь с фрагментом.
    """
    dominant_emotion = max(emotion, key=emotion.get) if emotion else "neutral"

    for name in names:
        # Ищем существующего
        async with db.execute(
            "SELECT id FROM people WHERE user_id=? AND name=?", (user_id, name)
        ) as cur:
            existing = await cur.fetchone()

        if existing:
            person_id = existing["id"]
        else:
            person_id = str(uuid.uuid4())
            await db.execute(
                "INSERT INTO people (id, user_id, name) VALUES (?,?,?)",
                (person_id, user_id, name),
            )

        # Связь person ↔ fragment
        edge_id = str(uuid.uuid4())
        await db.execute(
            "INSERT INTO people_edges (id, person_id, fragment_id, emotion) VALUES (?,?,?,?)",
            (edge_id, person_id, fragment_id, dominant_emotion),
        )

    await db.commit()
