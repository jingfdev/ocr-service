import pytesseract
import logging
from PIL import Image
from typing import Tuple

from ..config import settings

logger = logging.getLogger(__name__)

class TesseractOCREngine:
    """Handles OCR processing using Tesseract."""

    def __init__(self):
        if settings.TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
            logger.info(f"Tesseract command path set to: {settings.TESSERACT_CMD}")
        else:
            logger.info("Using default Tesseract command path.")

    def _get_tesseract_lang(self, lang: str) -> str:
        """Maps input language to Tesseract-compatible language string."""
        if lang == "kh":
            return "khm"
        elif lang == "en":
            return "eng"
        elif lang == "both":
            return "khm+eng"
        else:
            logger.warning(f"Unsupported language \'{lang}\' detected. Defaulting to \'eng\'.")
            return "eng"

    def process_image_for_ocr(self, image: Image.Image, lang: str = "eng") -> Tuple[str, float]:
        """Processes a single image with Tesseract OCR and returns text and confidence."""
        tesseract_lang = self._get_tesseract_lang(lang)
        logger.info(f"Processing image with Tesseract using language: {tesseract_lang}")

        try:
            # Perform OCR
            # --oem 3: Use LSTM OCR engine
            # --psm 3: Assume an image of a single column of text of variable sizes
            custom_config = r'--oem 3 --psm 3'
            data = pytesseract.image_to_data(image, lang=tesseract_lang, output_type=pytesseract.Output.DICT, config=custom_config)
            text = pytesseract.image_to_string(image, lang=tesseract_lang, config=custom_config)

            # Calculate average confidence
            # Filter out -1 confidence scores (often for non-text regions)
            confidences = []
            for c in data['conf']:
                try:
                    conf_val = int(c) if isinstance(c, (int, float)) else int(float(c))
                    if conf_val > 0:
                        confidences.append(conf_val)
                except (ValueError, TypeError):
                    continue
            average_confidence = sum(confidences) / len(confidences) / 100 if confidences else 0.0

            logger.info(f"OCR completed. Extracted text length: {len(text)}, Confidence: {average_confidence:.2f}")
            return text.strip(), average_confidence
        except pytesseract.TesseractError as e:
            logger.error(f"Tesseract OCR error: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during OCR processing: {e}")
            raise
