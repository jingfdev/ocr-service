_# ocr-service/app/utils/file_handler.py

import os
import shutil
import logging
from pathlib import Path
from typing import Union
from uuid import uuid4

from fastapi import UploadFile

from ..config import settings

logger = logging.getLogger(__name__)

def save_upload_file(upload_file: UploadFile) -> Path:
    """Saves an uploaded file to a temporary directory and returns the path."""
    Path(settings.TEMP_DIR).mkdir(parents=True, exist_ok=True)
    # Use a unique filename to avoid collisions
    ext = Path(upload_file.filename).suffix
    temp_filename = f"{uuid4()}{ext}"
    temp_filepath = Path(settings.TEMP_DIR) / temp_filename
    try:
        with temp_filepath.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        logger.info(f"File saved temporarily to {temp_filepath}")
        return temp_filepath
    except Exception as e:
        logger.error(f"Could not save file: {e}")
        raise
    finally:
        upload_file.file.close()

def delete_temp_path(path: Union[str, Path]):
    """Deletes a file or directory at the given path."""
    path = Path(path)
    try:
        if path.is_dir():
            shutil.rmtree(path)
            logger.info(f"Temporary directory deleted: {path}")
        elif path.is_file():
            path.unlink()
            logger.info(f"Temporary file deleted: {path}")
    except OSError as e:
        logger.error(f"Error deleting path {path}: {e}")

def get_file_extension(filename: str) -> str:
    """Extracts the file extension from a filename."""
    return Path(filename).suffix.lower()
