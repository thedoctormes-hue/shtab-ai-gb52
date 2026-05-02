"""app/config.py — re-exports from shared с расширенными настройками."""
import os
os.environ["EXTENDED_SETTINGS"] = "1"  # Включаем расширенные настройки

from shared.config import ExtendedSettings as Settings, settings

__all__ = ["Settings", "settings"]