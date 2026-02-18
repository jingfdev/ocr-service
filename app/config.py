_# ocr-service/app/config.py

import os
from pydantic import BaseModel
from typing import Literal

class Settings(BaseModel):
    """Configuration settings for the application."""
    # File settings
    TEMP_DIR: str = os.getenv("TEMP_DIR", "/tmp/ocr-uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10 MB

    # Tesseract settings
    TESSERACT_CMD: str | None = os.getenv("TESSERACT_CMD")

    # Logging
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = os.getenv("LOG_LEVEL", "INFO")

    # Service metadata
    SERVICE_NAME: str = "ocr-service"

settings = Settings()
