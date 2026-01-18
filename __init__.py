"""Image Extractor - Extract product information from label and nameplate images."""
from .extractor import extract_equipment_info, extract_equipment_info_sync, AVAILABLE_METHODS
from .ocr import (
    ocr_with_google_vision,
    ocr_with_tesseract,
    ocr_with_easyocr,
    ocr_with_easyocr_detailed,
    ocr_with_paddleocr,
    ocr_with_paddleocr_detailed,
    ocr_with_surya,
    ocr_with_doctr,
    ocr_with_doctr_detailed,
    get_available_ocr_engines,
)
from .llm_extractor import extract_from_image, extract_from_text, format_extracted_info
from .tool_patterns import detect_brands, extract_model_numbers, extract_tool_info_from_ocr
from .image_processor import fix_image_orientation, load_image, preprocess_image_variants, image_to_bytes
from .excel_output import create_excel_report, format_result_for_excel

__version__ = "2.0.0"

__all__ = [
    # Main extraction
    "extract_equipment_info",
    "extract_equipment_info_sync",
    "AVAILABLE_METHODS",
    # OCR engines
    "ocr_with_google_vision",
    "ocr_with_tesseract",
    "ocr_with_easyocr",
    "ocr_with_easyocr_detailed",
    "ocr_with_paddleocr",
    "ocr_with_paddleocr_detailed",
    "ocr_with_surya",
    "ocr_with_doctr",
    "ocr_with_doctr_detailed",
    "get_available_ocr_engines",
    # LLM extraction
    "extract_from_image",
    "extract_from_text",
    "format_extracted_info",
    # Tool patterns
    "detect_brands",
    "extract_model_numbers",
    "extract_tool_info_from_ocr",
    # Image processing
    "fix_image_orientation",
    "load_image",
    "preprocess_image_variants",
    "image_to_bytes",
    # Excel output
    "create_excel_report",
    "format_result_for_excel",
]
