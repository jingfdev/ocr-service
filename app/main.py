_# ocr-service/app/main.py

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from .config import settings
from .routes import ocr
from .utils.file_handler import delete_temp_path

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL, format=
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Context manager for application startup and shutdown events."""
    logger.info("OCR Service starting up...")
    # The temp directory is created on demand by file_handler.save_upload_file
    yield
    logger.info("OCR Service shutting down...")
    # Clean up the main temporary directory on shutdown
    delete_temp_path(settings.TEMP_DIR)

app = FastAPI(
    title="Medicord OCR Microservice",
    description="RESTful API for extracting text from medical documents using Tesseract OCR and OpenCV.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(ocr.router, prefix="/api/v1/ocr", tags=["OCR"]) # Base path: /api/v1/ocr

@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

logger.info("FastAPI application initialized.")
