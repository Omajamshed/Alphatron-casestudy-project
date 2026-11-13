import logging
from typing import Optional

logger = logging.getLogger("contractguard.ocr")


def extract_ocr_text(page_bytes: bytes) -> Optional[str]:
    """Optional OCR fallback using pytesseract if available, otherwise returns None."""
    try:
        import pytesseract
        from PIL import Image
        import io
        image = Image.open(io.BytesIO(page_bytes))
        return pytesseract.image_to_string(image)
    except Exception as e:
        logger.debug(f"OCR not available or failed: {e}")
        return None
