import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

def preprocess_image(image: np.ndarray) -> np.ndarray:
    """Applies a series of image preprocessing steps using OpenCV."""
    logger.info("Starting image preprocessing.")

    # 1. Convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    logger.debug("Converted to grayscale.")

    # 2. Apply adaptive threshold
    # Using ADAPTIVE_THRESH_GAUSSIAN_C for better results on varying lighting
    thresh_image = cv2.adaptiveThreshold(gray_image, 255,
                                         cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY, 11, 2)
    logger.debug("Applied adaptive threshold.")

    # 3. Denoise (optional, can be computationally intensive)
    # For grayscale, we can use FastNlMeansDenoising
    denoised_image = cv2.fastNlMeansDenoising(thresh_image, None, 30, 7, 21)
    logger.debug("Applied denoising.")

    # 4. Sharpen (optional, can enhance text edges)
    kernel = np.array([[-1, -1, -1],
                       [-1,  9, -1],
                       [-1, -1, -1]])
    sharpened_image = cv2.filter2D(denoised_image, -1, kernel)
    logger.debug("Applied sharpening.")

    logger.info("Image preprocessing completed.")
    return sharpened_image
