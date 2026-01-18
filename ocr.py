"""OCR engines - Multiple local and cloud options.

Supported engines:
- Tesseract: Traditional OCR, requires system installation
- EasyOCR: Deep learning based, easy to use
- PaddleOCR: High accuracy, multilingual (109 languages)
- Surya: Modern OCR with layout analysis (90+ languages)
- docTR: Document-focused OCR (TensorFlow/PyTorch)
- Google Cloud Vision: Cloud-based, high accuracy
"""
import os
import io
import json
from typing import Optional, List, Union
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
            img = Image.open(io.BytesIO(image_path_or_bytes))
            img_array = np.array(img)
            results = reader.readtext(img_array)
        else:
            results = reader.readtext(str(image_path_or_bytes))

        return results
    except Exception as e:
        print(f"EasyOCR error: {e}")
        return []


# =============================================================================
# PaddleOCR - High accuracy, multilingual (109 languages)
# =============================================================================

def ocr_with_paddleocr(image_path_or_bytes, lang: str = 'japan', gpu: bool = False) -> Optional[str]:
    """Perform OCR using PaddleOCR.

    PaddleOCR by Baidu supports 109 languages with high accuracy.
    Lightweight (<10MB) and fast.

    Args:
        image_path_or_bytes: Image file path or bytes
        lang: Language code (default: 'japan')
            Common: 'en', 'japan', 'korean', 'chinese_cht', 'french', 'german'
        gpu: Whether to use GPU (default: False)

    Returns:
        Extracted text from image
    """
    try:
        from paddleocr import PaddleOCR
    except ImportError:
        print("paddleocr not installed. Install with: pip install paddleocr")
        return None

    try:
        ocr = PaddleOCR(use_angle_cls=True, lang=lang, use_gpu=gpu, show_log=False)

        if isinstance(image_path_or_bytes, bytes):
            img = Image.open(io.BytesIO(image_path_or_bytes))
            img_array = np.array(img)
            result = ocr.ocr(img_array, cls=True)
        else:
            result = ocr.ocr(str(image_path_or_bytes), cls=True)

        # Extract text from results
        texts = []
        if result and result[0]:
            for line in result[0]:
                if line and len(line) >= 2:
                    texts.append(line[1][0])  # line[1] = (text, confidence)

        return "\n".join(texts)
    except Exception as e:
        print(f"PaddleOCR error: {e}")
        return None


def ocr_with_paddleocr_detailed(image_path_or_bytes, lang: str = 'japan', gpu: bool = False) -> List[dict]:
    """Perform OCR using PaddleOCR with detailed results.

    Args:
        image_path_or_bytes: Image file path or bytes
        lang: Language code (default: 'japan')
        gpu: Whether to use GPU (default: False)

    Returns:
        List of dicts: {'bbox': [...], 'text': str, 'confidence': float}
    """
    try:
        from paddleocr import PaddleOCR
    except ImportError:
        print("paddleocr not installed. Install with: pip install paddleocr")
        return []

    try:
        ocr = PaddleOCR(use_angle_cls=True, lang=lang, use_gpu=gpu, show_log=False)

        if isinstance(image_path_or_bytes, bytes):
            img = Image.open(io.BytesIO(image_path_or_bytes))
            img_array = np.array(img)
            result = ocr.ocr(img_array, cls=True)
        else:
            result = ocr.ocr(str(image_path_or_bytes), cls=True)

        # Format results
        detailed = []
        if result and result[0]:
            for line in result[0]:
                if line and len(line) >= 2:
                    detailed.append({
                        'bbox': line[0],
                        'text': line[1][0],
                        'confidence': line[1][1]
                    })

        return detailed
    except Exception as e:
        print(f"PaddleOCR error: {e}")
        return []


# =============================================================================
# Surya OCR - Modern OCR with layout analysis (90+ languages)
# =============================================================================

def ocr_with_surya(image_path_or_bytes, langs: List[str] = None) -> Optional[str]:
    """Perform OCR using Surya.

    Surya supports 90+ languages with excellent layout analysis.
    Good for documents with tables, images, and complex layouts.

    Args:
        image_path_or_bytes: Image file path or bytes
        langs: Language codes (default: ['ja', 'en'])
            Uses ISO 639-1 codes: 'ja', 'en', 'zh', 'ko', 'fr', 'de', etc.

    Returns:
        Extracted text from image
    """
    try:
        from surya.ocr import run_ocr
        from surya.model.detection.model import load_model as load_det_model, load_processor as load_det_processor
        from surya.model.recognition.model import load_model as load_rec_model
        from surya.model.recognition.processor import load_processor as load_rec_processor
    except ImportError:
        print("surya-ocr not installed. Install with: pip install surya-ocr")
        return None

    if langs is None:
        langs = ['ja', 'en']

    try:
        # Load models
        det_processor, det_model = load_det_processor(), load_det_model()
        rec_model, rec_processor = load_rec_model(), load_rec_processor()

        # Load image
        if isinstance(image_path_or_bytes, bytes):
            img = Image.open(io.BytesIO(image_path_or_bytes))
        else:
            img = Image.open(image_path_or_bytes)

        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Run OCR
        predictions = run_ocr(
            [img],
            [langs],
            det_model,
            det_processor,
            rec_model,
            rec_processor
        )

        # Extract text
        texts = []
        if predictions and predictions[0]:
            for line in predictions[0].text_lines:
                texts.append(line.text)

        return "\n".join(texts)
    except Exception as e:
        print(f"Surya OCR error: {e}")
        return None


# =============================================================================
# docTR - Document Text Recognition (Mindee)
# =============================================================================

def ocr_with_doctr(image_path_or_bytes, detect_lang: bool = False) -> Optional[str]:
    """Perform OCR using docTR.

    docTR by Mindee is optimized for document understanding.
    Uses deep learning for both detection and recognition.

    Args:
        image_path_or_bytes: Image file path or bytes
        detect_lang: Whether to detect language automatically (default: False)

    Returns:
        Extracted text from image
    """
    try:
        from doctr.io import DocumentFile
        from doctr.models import ocr_predictor
    except ImportError:
        print("python-doctr not installed. Install with: pip install python-doctr")
        return None

    try:
        # Load model
        model = ocr_predictor(pretrained=True)

        # Load image
        if isinstance(image_path_or_bytes, bytes):
            doc = DocumentFile.from_images(image_path_or_bytes)
        else:
            doc = DocumentFile.from_images(str(image_path_or_bytes))

        # Run OCR
        result = model(doc)

        # Extract text
        texts = []
        for page in result.pages:
            for block in page.blocks:
                for line in block.lines:
                    line_text = " ".join([word.value for word in line.words])
                    texts.append(line_text)

        return "\n".join(texts)
    except Exception as e:
        print(f"docTR error: {e}")
        return None


def ocr_with_doctr_detailed(image_path_or_bytes) -> List[dict]:
    """Perform OCR using docTR with detailed results.

    Args:
        image_path_or_bytes: Image file path or bytes

    Returns:
        List of dicts with word-level details
    """
    try:
        from doctr.io import DocumentFile
        from doctr.models import ocr_predictor
    except ImportError:
        print("python-doctr not installed. Install with: pip install python-doctr")
        return []

    try:
        model = ocr_predictor(pretrained=True)

        if isinstance(image_path_or_bytes, bytes):
            doc = DocumentFile.from_images(image_path_or_bytes)
        else:
            doc = DocumentFile.from_images(str(image_path_or_bytes))

        result = model(doc)

        detailed = []
        for page in result.pages:
            for block in page.blocks:
                for line in block.lines:
                    for word in line.words:
                        detailed.append({
                            'text': word.value,
                            'confidence': word.confidence,
                            'bbox': word.geometry
                        })

        return detailed
    except Exception as e:
        print(f"docTR error: {e}")
        return []


# =============================================================================
# Utility function to list available OCR engines
# =============================================================================

def get_available_ocr_engines() -> dict:
    """Check which OCR engines are available.

    Returns:
        Dictionary with engine names and availability status
    """
    engines = {}

    # Tesseract
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        engines['tesseract'] = True
    except:
        engines['tesseract'] = False

    # EasyOCR
    try:
        import easyocr
        engines['easyocr'] = True
    except ImportError:
        engines['easyocr'] = False

    # PaddleOCR
    try:
        from paddleocr import PaddleOCR
        engines['paddleocr'] = True
    except ImportError:
        engines['paddleocr'] = False

    # Surya
    try:
        from surya.ocr import run_ocr
        engines['surya'] = True
    except ImportError:
        engines['surya'] = False

    # docTR
    try:
        from doctr.models import ocr_predictor
        engines['doctr'] = True
    except ImportError:
        engines['doctr'] = False

    # Google Vision (check for credentials)
    try:
        from google.cloud import vision
        engines['google_vision'] = True
    except ImportError:
        engines['google_vision'] = False

    return engines
