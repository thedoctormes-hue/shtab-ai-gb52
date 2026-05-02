"""
Database module — re-exports from shared.
Синхронизировано с /root/LabDoctorM/shared/database.py
"""
from shared.database import (
    get_db,
    get_connection,
    init_db,
    search_fragments,
    get_today_fragments,
    get_today_pattern,
    get_user_by_tg_id,
    get_user_by_id,
    get_last_fragment_date,
    get_patterns,
    upsert_pattern,
    get_recent_fragments,
    get_people_edges,
    get_all_user_ids,
    SCHEMA,
    DB_PATH,
)

__all__ = [
    "get_db",
    "get_connection",
    "init_db",
    "search_fragments",
    "get_today_fragments",
    "get_today_pattern",
    "get_user_by_tg_id",
    "get_user_by_id",
    "get_last_fragment_date",
    "get_patterns",
    "upsert_pattern",
    "get_recent_fragments",
    "get_people_edges",
    "get_all_user_ids",
    "SCHEMA",
    "DB_PATH",
]