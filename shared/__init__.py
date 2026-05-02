"""Shared library for LabDoctorM bots."""
from .database import (
    get_db,
    get_connection,
    init_db,
    search_fragments,
    get_today_fragments,
    get_user_by_tg_id,
    get_user_by_id,
    get_last_fragment_date,
    get_patterns,
    upsert_pattern,
    get_recent_fragments,
    get_people_edges,
    get_all_user_ids,
)
from .config import BaseSettings, ExtendedSettings
from .logging import setup_logging

__all__ = [
    # Database
    "get_db",
    "get_connection",
    "init_db",
    "search_fragments",
    "get_today_fragments",
    "get_user_by_tg_id",
    "get_user_by_id",
    "get_last_fragment_date",
    "get_patterns",
    "upsert_pattern",
    "get_recent_fragments",
    "get_people_edges",
    "get_all_user_ids",
    # Config
    "BaseSettings",
    "ExtendedSettings",
    # Logging
    "setup_logging",
]