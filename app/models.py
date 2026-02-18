_# ocr-service/app/models.py

from pydantic import BaseModel, Field
from typing import Literal

class OCRHealthResponse(BaseModel):
    status: str = Field(..., example="ok")
    service: str = Field(..., example="ocr-service")

class OCRExtractResponse(BaseModel):
    success: bool = Field(..., example=True)
    raw_text: str = Field(..., example="This is the extracted text from the document.")
    confidence: float = Field(..., example=0.87)
    processing_time_ms: int = Field(..., example=1320)

class OCRErrorResponse(BaseModel):
    success: bool = Field(..., example=False)
    message: str = Field(..., example="Invalid file type or size. Supported types: PDF, JPG, PNG. Max size: 10MB.")

# Using an Enum for language parameter for stricter validation
Language = Literal["kh", "en", "both"]
