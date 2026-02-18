import logging
import time
from typing import Optional

from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse

from ..config import settings
from ..services.ocr_pipeline import OCRPipeline
from ..utils.file_handler import save_upload_file, delete_temp_path, get_file_extension
from ..models import OCRHealthResponse, OCRExtractResponse, OCRErrorResponse, Language

router = APIRouter()
logger = logging.getLogger(__name__)

ocr_pipeline = OCRPipeline()

@router.get("/health", response_model=OCRHealthResponse)
async def health_check():
    """Health check endpoint to verify service status."""
    logger.info("Health check requested.")
    return OCRHealthResponse(status="ok", service=settings.SERVICE_NAME)

@router.post("/extract", response_model=OCRExtractResponse, responses={400: {"model": OCRErrorResponse}, 500: {"model": OCRErrorResponse}})
async def extract_text(file: UploadFile = File(...), language: Optional[Language] = "both"):
    """Extracts text from an uploaded document using OCR."""
    start_time = time.time()
    logger.info(f"OCR extraction requested for file: {file.filename}, content_type: {file.content_type}, language: {language}")

    # 1. Validate file type and size
    allowed_extensions = [".pdf", ".jpg", ".jpeg", ".png"]
    file_extension = get_file_extension(file.filename)

    if file_extension not in allowed_extensions:
        logger.warning(f"Invalid file type uploaded: {file_extension}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=OCRErrorResponse(success=False, message=f"Invalid file type. Supported types: {', '.join(allowed_extensions)}.").model_dump()
        )

    # Check file size after reading it into memory (FastAPI handles this for UploadFile)
    # The actual file content is streamed, so we check size indirectly or rely on FastAPI's internal limits
    # For explicit check, we'd need to read the file, which might consume memory for large files.
    # A more robust check would be to configure FastAPI's body parser or handle it during streaming.
    # For now, we'll assume FastAPI's default handling combined with our MAX_FILE_SIZE setting is sufficient.
    # The `file.size` attribute is populated after the file is received.
    if file.size and file.size > settings.MAX_FILE_SIZE:
        logger.warning(f"File size exceeds limit: {file.size} bytes (max {settings.MAX_FILE_SIZE} bytes)")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=OCRErrorResponse(success=False, message=f"File size exceeds limit. Max size: {settings.MAX_FILE_SIZE / (1024 * 1024):.0f}MB.").model_dump()
        )

    temp_file_path = None
    try:
        # 2. Save file temporarily
        temp_file_path = save_upload_file(file)
        logger.debug(f"File temporarily saved to: {temp_file_path}")

        # 3. Process document through OCR pipeline
        raw_text, confidence = await ocr_pipeline.process_document(temp_file_path, language)

        processing_time_ms = int((time.time() - start_time) * 1000)
        logger.info(f"OCR extraction successful for {file.filename}. Processing time: {processing_time_ms}ms.")

        return OCRExtractResponse(
            success=True,
            raw_text=raw_text,
            confidence=confidence,
            processing_time_ms=processing_time_ms
        )

    except ValueError as ve:
        logger.error(f"Validation error during OCR processing: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=OCRErrorResponse(success=False, message=str(ve)).model_dump()
        )
    except HTTPException:
        # Re-raise HTTPExceptions that were already created
        raise
    except Exception as e:
        logger.exception(f"An unexpected error occurred during OCR processing for {file.filename}.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=OCRErrorResponse(success=False, message="An unexpected error occurred during OCR processing.").model_dump()
        )
    finally:
        # 6. Delete temporary files
        if temp_file_path:
            delete_temp_path(temp_file_path)
            logger.debug(f"Temporary file deleted: {temp_file_path}")
