import logging
import time
from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np
from pdf2image import convert_from_path
from PIL import Image

from ..utils.file_handler import delete_temp_path, get_file_extension
from .preprocessing import preprocess_image
from .tesseract_engine import TesseractOCREngine

logger = logging.getLogger(__name__)

class OCRPipeline:
    """Orchestrates the OCR process from file input to text output."""

    def __init__(self):
        self.tesseract_engine = TesseractOCREngine()

    async def process_document(self, file_path: Path, language: str = "eng") -> Tuple[str, float]:
        """Processes a document (image or PDF) to extract text and confidence."""
        start_time = time.time()
        all_extracted_text = []
        all_confidences = []
        temp_image_paths: List[Path] = []

        try:
            file_extension = get_file_extension(file_path.name)

            if file_extension == ".pdf":
                logger.info(f"Processing PDF file: {file_path}")
                # Convert PDF to a list of PIL images
                images = convert_from_path(file_path)
                logger.info(f"Converted PDF to {len(images)} images.")
            elif file_extension in [".jpg", ".jpeg", ".png"]:
                logger.info(f"Processing image file: {file_path}")
                images = [Image.open(file_path)]
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")

            for i, pil_image in enumerate(images):
                logger.debug(f"Processing image {i+1}/{len(images)}.")
                # Convert PIL Image to OpenCV format (numpy array)
                opencv_image = np.array(pil_image)
                # Convert RGB to BGR for OpenCV if necessary (PIL is RGB, OpenCV expects BGR)
                if len(opencv_image.shape) == 3 and opencv_image.shape[2] == 3:
                    opencv_image = cv2.cvtColor(opencv_image, cv2.COLOR_RGB2BGR)

                # Preprocess image
                processed_image_np = preprocess_image(opencv_image)

                # Convert back to PIL Image for Tesseract
                processed_pil_image = Image.fromarray(processed_image_np)

                # Perform OCR
                text, confidence = self.tesseract_engine.process_image_for_ocr(processed_pil_image, language)
                all_extracted_text.append(text)
                all_confidences.append(confidence)

        except Exception as e:
            logger.error(f"Error during OCR pipeline processing: {e}")
            raise
        finally:
            # Clean up temporary images if any were created (e.g., from PDF conversion)
            for img_path in temp_image_paths:
                delete_temp_path(img_path)
            # Ensure the original uploaded file is also deleted
            delete_temp_path(file_path)

        total_raw_text = "\n".join(all_extracted_text).strip()
        average_confidence = np.mean(all_confidences) if all_confidences else 0.0
        processing_time_ms = int((time.time() - start_time) * 1000)

        logger.info(f"Document processing finished in {processing_time_ms} ms. Total text length: {len(total_raw_text)}")
        return total_raw_text, float(f"{average_confidence:.2f}")
