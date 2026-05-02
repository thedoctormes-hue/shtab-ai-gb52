"""app/config.py — re-exports from shared."""
from shared.config import BaseSettings as Settings, settings

__all__ = ["Settings", "settings"]