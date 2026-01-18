"""OCR engines - Local (Tesseract, EasyOCR) and Cloud (Google Vision)."""
import os
import json
from typing import Optional, List
from PIL import Image
import numpy as np


def ocr_with_google_vision(image_bytes: bytes, credentials_json: str = None) -> str:
    """Perform OCR using Google Cloud Vision API.

    Args:
        image_bytes: Image data as bytes
        credentials_json: Google service account JSON string (optional)

    Returns:
        Extracted text from image
    """
    from google.cloud import vision
    from google.oauth2 import service_account

    client = None

    # 1. Use provided credentials JSON
    if credentials_json:
        try:
            credentials_info = json.loads(credentials_json)
            credentials = service_account.Credentials.from_service_account_info(credentials_info)
            client = vision.ImageAnnotatorClient(credentials=credentials)
        except Exception as e:
            raise Exception(f"Failed to parse credentials JSON: {e}")

    # 2. Environment variable with JSON content
    if not client:
        service_account_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        if service_account_json:
            try:
                credentials_info = json.loads(service_account_json)
                credentials = service_account.Credentials.from_service_account_info(credentials_info)
                client = vision.ImageAnnotatorClient(credentials=credentials)
            except Exception as e:
                print(f"Failed to use GOOGLE_SERVICE_ACCOUNT_JSON: {e}")

    # 3. GOOGLE_APPLICATION_CREDENTIALS environment variable (file path)
    if not client and os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        client = vision.ImageAnnotatorClient()

    if not client:
        raise Exception(
            "Google Vision API credentials not configured. "
            "Set GOOGLE_SERVICE_ACCOUNT_JSON env var or provide credentials_json parameter."
        )

    image = vision.Image(content=image_bytes)

    # Use document_text_detection for better Japanese text recognition
    response = client.document_text_detection(
        image=image,
        image_context=vision.ImageContext(
            language_hints=['ja', 'en']
        )
    )

    if response.error.message:
        raise Exception(f"Google Vision API error: {response.error.message}")

    # Get full text annotation
    if response.full_text_annotation:
        return response.full_text_annotation.text

    # Fallback to text_annotations
    if response.text_annotations:
        return response.text_annotations[0].description

    return ""


def ocr_with_tesseract(image_path_or_bytes, tesseract_cmd: str = None, langs: str = 'jpn+eng') -> Optional[str]:
    """Perform OCR using Tesseract.

    Args:
        image_path_or_bytes: Image file path or bytes
        tesseract_cmd: Path to tesseract executable (optional)
        langs: Languages for OCR (default: 'jpn+eng')

    Returns:
        Extracted text from image
    """
    try:
        import pytesseract
    except ImportError:
        print("pytesseract not installed. Install with: pip install pytesseract")
        return None

    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    try:
        if isinstance(image_path_or_bytes, bytes):
            import io
            img = Image.open(io.BytesIO(image_path_or_bytes))
        else:
            img = Image.open(image_path_or_bytes)
        return pytesseract.image_to_string(img, lang=langs)
    except Exception as e:
        print(f"Tesseract OCR error: {e}")
        return None


def ocr_with_easyocr(image_path_or_bytes, langs: List[str] = None, gpu: bool = False) -> Optional[str]:
    """Perform OCR using EasyOCR.

    Args:
        image_path_or_bytes: Image file path or bytes
        langs: Languages for OCR (default: ['ja', 'en'])
        gpu: Whether to use GPU (default: False)

    Returns:
        Extracted text from image
    """
    try:
        import easyocr
    except ImportError:
        print("easyocr not installed. Install with: pip install easyocr")
        return None

    if langs is None:
        langs = ['ja', 'en']

    try:
        reader = easyocr.Reader(langs, gpu=gpu)

        if isinstance(image_path_or_bytes, bytes):
            import io
            img = Image.open(io.BytesIO(image_path_or_bytes))
            img_array = np.array(img)
            results = reader.readtext(img_array, detail=0, paragraph=True)
        else:
            results = reader.readtext(str(image_path_or_bytes), detail=0, paragraph=True)

        return "\n".join(results)
    except Exception as e:
        print(f"EasyOCR error: {e}")
        return None


def ocr_with_easyocr_detailed(image_path_or_bytes, langs: List[str] = None, gpu: bool = False) -> List[tuple]:
    """Perform OCR using EasyOCR with detailed results.

    Args:
        image_path_or_bytes: Image file path or bytes
        langs: Languages for OCR (default: ['ja', 'en'])
        gpu: Whether to use GPU (default: False)

    Returns:
        List of tuples: (bbox, text, confidence)
    """
    try:
        import easyocr
    except ImportError:
        print("easyocr not installed. Install with: pip install easyocr")
        return []

    if langs is None:
        langs = ['ja', 'en']

    try:
        reader = easyocr.Reader(langs, gpu=gpu)

        if isinstance(image_path_or_bytes, bytes):
            import io
            img = Image.open(io.BytesIO(image_path_or_bytes))
            img_array = np.array(img)
            results = reader.readtext(img_array)
        else:
            results = reader.readtext(str(image_path_or_bytes))

        return results
    except Exception as e:
        print(f"EasyOCR error: {e}")
        return []
