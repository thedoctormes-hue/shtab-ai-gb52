"""
Shared logging configuration for LabDoctorM bots.
"""
import logging
import sys


def setup_logging(name: str = "app", level: int = logging.INFO) -> logging.Logger:
    """Настройка логгера с единым форматом."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def get_logger(name: str = "app") -> logging.Logger:
    """Получить настроенный логгер."""
    return logging.getLogger(name)