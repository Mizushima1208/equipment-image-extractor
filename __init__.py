"""Equipment Image Extractor - Extract equipment information from nameplate and tool images."""
from .extractor import extract_equipment_info, extract_equipment_info_sync
from .ocr import ocr_with_google_vision, ocr_with_tesseract, ocr_with_easyocr, ocr_with_easyocr_detailed
from .llm_extractor import extract_from_image, extract_from_text, format_extracted_info
from .tool_patterns import detect_brands, extract_model_numbers, extract_tool_info_from_ocr
from .image_processor import fix_image_orientation, load_image, preprocess_image_variants, image_to_bytes
from .excel_output import create_excel_report, format_result_for_excel

__version__ = "1.0.0"

__all__ = [
    # Main extraction
    "extract_equipment_info",
    "extract_equipment_info_sync",
    # OCR engines
    "ocr_with_google_vision",
    "ocr_with_tesseract",
    "ocr_with_easyocr",
    "ocr_with_easyocr_detailed",
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
