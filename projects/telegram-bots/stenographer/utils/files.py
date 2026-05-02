import os
from pathlib import Path
from typing import Tuple

ALLOWED_EXTENSIONS = {".ogg", ".mp3", ".wav", ".m4a", ".flac"}

def is_allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS

def check_file_size(file_path: str, max_size: int) -> Tuple[bool, str]:
    try:
        size = os.path.getsize(file_path)
        if size > max_size:
            return False, f"Файл слишком большой: {size / 1024 / 1024:.1f} МБ. Максимум 50 МБ."
        return True, ""
    except FileNotFoundError:
        return False, "Файл не найден"
    except Exception as e:
        return False, f"Ошибка проверки файла: {e}"
