"""
Роутер настроек выхода (exit_settings)
GET    /settings/exit    — получить настройки
PUT    /settings/exit    — обновить настройки
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.database import get_db
from app.deps import get_current_user

router = APIRouter()

# Whitelist разрешенных полей для обновления
ALLOWED_SETTINGS_FIELDS = {
    "export_format",
    "public_categories",
    "trusted_tg_id",
    "auto_delete_days",
    "farewell_message",
}


# ── Схемы ────────────────────────────────────────────────────────────────────

class ExitSettingsUpdate(BaseModel):
    export_format: str = None      # bundle / json / txt
    public_categories: list = None  # список категорий
    trusted_tg_id: str = None
    auto_delete_days: int = None
    farewell_message: str = None


class ExitSettingsOut(BaseModel):
    user_id: str
    export_format: str
    public_categories: list
    trusted_tg_id: str = None
    auto_delete_days: int
    farewell_message: str = None


# ── Эндпоинты ────────────────────────────────────────────────────────────────

@router.get("/exit", response_model=ExitSettingsOut)
async def get_exit_settings(
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    try:
        async with db.execute(
            "SELECT * FROM exit_settings WHERE user_id = ?", (user["id"],)
        ) as cur:
            row = await cur.fetchone()

        if not row:
            # Возвращаем дефолтные настройки
            return ExitSettingsOut(
                user_id=user["id"],
                export_format="bundle",
                public_categories=[],
                trusted_tg_id=None,
                auto_delete_days=90,
                farewell_message=None,
            )

        import json
        return ExitSettingsOut(
            user_id=row["user_id"],
            export_format=row["export_format"],
            public_categories=json.loads(row["public_categories"]) if row["public_categories"] else [],
            trusted_tg_id=row["trusted_tg_id"],
            auto_delete_days=row["auto_delete_days"],
            farewell_message=row["farewell_message"],
        )
    except Exception as e:
        import logging
        logging.error(f"Get settings error: {e}")
        raise HTTPException(500, "Internal server error")


@router.put("/exit", response_model=ExitSettingsOut)
async def update_exit_settings(
    body: ExitSettingsUpdate,
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    import json
    import logging

    try:
        # Подготавливаем данные для обновления
        update_fields = {}
        if body.export_format is not None:
            update_fields["export_format"] = body.export_format
        if body.public_categories is not None:
            update_fields["public_categories"] = json.dumps(body.public_categories, ensure_ascii=False)
        if body.trusted_tg_id is not None:
            update_fields["trusted_tg_id"] = body.trusted_tg_id
        if body.auto_delete_days is not None:
            update_fields["auto_delete_days"] = body.auto_delete_days
        if body.farewell_message is not None:
            update_fields["farewell_message"] = body.farewell_message

        if not update_fields:
            return await get_exit_settings(user, db)

        # Проверка на разрешенные поля
        invalid_fields = set(update_fields.keys()) - ALLOWED_SETTINGS_FIELDS
        if invalid_fields:
            invalid_list = ", ".join(invalid_fields)
            raise HTTPException(400, f"Invalid fields: {invalid_list}")

        # Upsert logic
        # Check if exists
        async with db.execute(
            "SELECT user_id FROM exit_settings WHERE user_id = ?", (user["id"],)
        ) as cur:
            existing = await cur.fetchone()

        if existing:
            set_clause = ", ".join(f"{k} = ?" for k in update_fields.keys())
            values = list(update_fields.values()) + [user["id"]]
            sql = f"UPDATE exit_settings SET {set_clause} WHERE user_id = ?"
            await db.execute(sql, values)
        else:
            fields = ["user_id"] + list(update_fields.keys())
            placeholders = ["?"] * len(fields)
            fields_str = ", ".join(fields)
            placeholders_str = ", ".join(placeholders)
            sql = f"INSERT INTO exit_settings ({fields_str}) VALUES ({placeholders_str})"
            values = [user["id"]] + list(update_fields.values())
            await db.execute(sql, values)

        await db.commit()
        return await get_exit_settings(user, db)

    except Exception as e:
        logging.error(f"Update settings error: {e}")
        raise HTTPException(500, "Internal server error")
