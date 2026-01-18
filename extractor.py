"""Main equipment information extractor from images."""
import asyncio
from typing import Optional
from .ocr import (
    ocr_with_google_vision,
    ocr_with_easyocr,
    ocr_with_easyocr_detailed,
    ocr_with_paddleocr,
    ocr_with_surya,
    ocr_with_doctr,
)
from .llm_extractor import extract_from_image, extract_from_text, format_extracted_info
from .tool_patterns import extract_tool_info_from_ocr


# Available OCR methods
AVAILABLE_METHODS = [
    "gemini-vision",        # Gemini Vision direct analysis
    "google-vision-gemini", # Google Vision OCR + Gemini
    "easyocr",              # EasyOCR only (local)
    "easyocr-gemini",       # EasyOCR + Gemini
    "paddleocr",            # PaddleOCR only (local)
    "paddleocr-gemini",     # PaddleOCR + Gemini
    "surya",                # Surya OCR only (local)
    "surya-gemini",         # Surya + Gemini
    "doctr",                # docTR only (local)
    "doctr-gemini",         # docTR + Gemini
]


def has_valid_info(info: dict) -> bool:
    """Check if extracted info has any meaningful data."""
    if not info:
        return False
    important_fields = ["equipment_name", "model_number", "manufacturer", "serial_number"]
    return any(info.get(field) for field in important_fields)


async def extract_equipment_info(
    image_bytes: bytes,
    method: str = "gemini-vision",
    gemini_api_key: str = None,
    vision_credentials_json: str = None
) -> dict:
    """Extract equipment information from image.

    Args:
        image_bytes: Image data as bytes
        method: Extraction method
            - "gemini-vision": Direct image analysis with Gemini (recommended)
            - "google-vision-gemini": Google Vision OCR + Gemini (high accuracy)
            - "easyocr": EasyOCR only (local, no cloud)
            - "easyocr-gemini": EasyOCR + Gemini
            - "paddleocr": PaddleOCR only (local, high accuracy)
            - "paddleocr-gemini": PaddleOCR + Gemini
            - "surya": Surya OCR only (local, 90+ languages)
            - "surya-gemini": Surya + Gemini
            - "doctr": docTR only (local, document-focused)
            - "doctr-gemini": docTR + Gemini
        gemini_api_key: Gemini API key (optional, uses env var if not provided)
        vision_credentials_json: Google Cloud credentials JSON (optional)

    Returns:
        Dictionary with extracted equipment information
    """
    raw_text = ""
    extracted_info = None
    used_method = method

    # Method 1: Gemini Vision - Direct image analysis
    if method == "gemini-vision":
        try:
            print(f"Using Gemini Vision for direct image extraction...")
            extracted = await extract_from_image(image_bytes, api_key=gemini_api_key)
            extracted_info = format_extracted_info(extracted)
            if has_valid_info(extracted_info):
                raw_text = "(Gemini Vision - direct image extraction)"
                print(f"Gemini Vision extraction successful")
            else:
                print("Gemini Vision returned empty result, falling back to OCR + Gemini")
                used_method = "google-vision-gemini"
        except Exception as e:
            print(f"Gemini Vision error: {e}, falling back to OCR + Gemini")
            used_method = "google-vision-gemini"

    # Method 2: Google Vision OCR + Gemini Analysis
    if used_method == "google-vision-gemini" and not has_valid_info(extracted_info):
        try:
            print(f"Using Google Vision OCR...")
            raw_text = ocr_with_google_vision(image_bytes, credentials_json=vision_credentials_json)
            print(f"OCR result: {raw_text[:200]}..." if len(raw_text) > 200 else f"OCR result: {raw_text}")

            if raw_text:
                print(f"Analyzing OCR text with Gemini...")
                extracted = await extract_from_text(raw_text, api_key=gemini_api_key)
                extracted_info = format_extracted_info(extracted)
                if not has_valid_info(extracted_info):
                    print("Gemini analysis failed to extract meaningful info")
                    extracted_info = {}
        except Exception as e:
            print(f"Google Vision OCR error: {e}")
            raise

    # Method 3: EasyOCR only (local, pattern matching)
    if method == "easyocr":
        try:
            print(f"Using EasyOCR for local text extraction...")
            ocr_results = ocr_with_easyocr_detailed(image_bytes)
            if ocr_results:
                tool_info = extract_tool_info_from_ocr(ocr_results)
                extracted_info = {
                    "equipment_name": None,
                    "model_number": tool_info.get("model_number"),
                    "manufacturer": tool_info.get("brand"),
                    "serial_number": tool_info.get("serial_number"),
                    "management_number": tool_info.get("management_number"),
                    "weight": None,
                    "output_power": None,
                    "engine_model": None,
                    "year_manufactured": None,
                    "specifications": None,
                }
                raw_text = tool_info.get("raw_text", "")
                print(f"EasyOCR extraction completed")
        except Exception as e:
            print(f"EasyOCR error: {e}")
            extracted_info = {}

    # Method 4: EasyOCR + Gemini Analysis
    if method == "easyocr-gemini":
        try:
            print(f"Using EasyOCR for local text extraction...")
            raw_text = ocr_with_easyocr(image_bytes)
            if raw_text:
                print(f"OCR result: {raw_text[:200]}..." if len(raw_text) > 200 else f"OCR result: {raw_text}")
                print(f"Analyzing OCR text with Gemini...")
                extracted = await extract_from_text(raw_text, api_key=gemini_api_key)
                extracted_info = format_extracted_info(extracted)
                if not has_valid_info(extracted_info):
                    print("Gemini analysis failed to extract meaningful info")
                    extracted_info = {}
        except Exception as e:
            print(f"EasyOCR + Gemini error: {e}")
            extracted_info = {}

    # Method 5: PaddleOCR only (local)
    if method == "paddleocr":
        try:
            print(f"Using PaddleOCR for local text extraction...")
            raw_text = ocr_with_paddleocr(image_bytes)
            if raw_text:
                tool_info = extract_tool_info_from_ocr([raw_text])
                extracted_info = {
                    "equipment_name": None,
                    "model_number": tool_info.get("model_number"),
                    "manufacturer": tool_info.get("brand"),
                    "serial_number": tool_info.get("serial_number"),
                    "management_number": tool_info.get("management_number"),
                    "weight": None,
                    "output_power": None,
                    "engine_model": None,
                    "year_manufactured": None,
                    "specifications": None,
                }
                raw_text = tool_info.get("raw_text", raw_text)
                print(f"PaddleOCR extraction completed")
        except Exception as e:
            print(f"PaddleOCR error: {e}")
            extracted_info = {}

    # Method 6: PaddleOCR + Gemini Analysis
    if method == "paddleocr-gemini":
        try:
            print(f"Using PaddleOCR for local text extraction...")
            raw_text = ocr_with_paddleocr(image_bytes)
            if raw_text:
                print(f"OCR result: {raw_text[:200]}..." if len(raw_text) > 200 else f"OCR result: {raw_text}")
                print(f"Analyzing OCR text with Gemini...")
                extracted = await extract_from_text(raw_text, api_key=gemini_api_key)
                extracted_info = format_extracted_info(extracted)
                if not has_valid_info(extracted_info):
                    print("Gemini analysis failed to extract meaningful info")
                    extracted_info = {}
        except Exception as e:
            print(f"PaddleOCR + Gemini error: {e}")
            extracted_info = {}

    # Method 7: Surya OCR only (local)
    if method == "surya":
        try:
            print(f"Using Surya OCR for local text extraction...")
            raw_text = ocr_with_surya(image_bytes)
            if raw_text:
                tool_info = extract_tool_info_from_ocr([raw_text])
                extracted_info = {
                    "equipment_name": None,
                    "model_number": tool_info.get("model_number"),
                    "manufacturer": tool_info.get("brand"),
                    "serial_number": tool_info.get("serial_number"),
                    "management_number": tool_info.get("management_number"),
                    "weight": None,
                    "output_power": None,
                    "engine_model": None,
                    "year_manufactured": None,
                    "specifications": None,
                }
                raw_text = tool_info.get("raw_text", raw_text)
                print(f"Surya OCR extraction completed")
        except Exception as e:
            print(f"Surya OCR error: {e}")
            extracted_info = {}

    # Method 8: Surya + Gemini Analysis
    if method == "surya-gemini":
        try:
            print(f"Using Surya OCR for local text extraction...")
            raw_text = ocr_with_surya(image_bytes)
            if raw_text:
                print(f"OCR result: {raw_text[:200]}..." if len(raw_text) > 200 else f"OCR result: {raw_text}")
                print(f"Analyzing OCR text with Gemini...")
                extracted = await extract_from_text(raw_text, api_key=gemini_api_key)
                extracted_info = format_extracted_info(extracted)
                if not has_valid_info(extracted_info):
                    print("Gemini analysis failed to extract meaningful info")
                    extracted_info = {}
        except Exception as e:
            print(f"Surya + Gemini error: {e}")
            extracted_info = {}

    # Method 9: docTR only (local)
    if method == "doctr":
        try:
            print(f"Using docTR for local text extraction...")
            raw_text = ocr_with_doctr(image_bytes)
            if raw_text:
                tool_info = extract_tool_info_from_ocr([raw_text])
                extracted_info = {
                    "equipment_name": None,
                    "model_number": tool_info.get("model_number"),
                    "manufacturer": tool_info.get("brand"),
                    "serial_number": tool_info.get("serial_number"),
                    "management_number": tool_info.get("management_number"),
                    "weight": None,
                    "output_power": None,
                    "engine_model": None,
                    "year_manufactured": None,
                    "specifications": None,
                }
                raw_text = tool_info.get("raw_text", raw_text)
                print(f"docTR extraction completed")
        except Exception as e:
            print(f"docTR error: {e}")
            extracted_info = {}

    # Method 10: docTR + Gemini Analysis
    if method == "doctr-gemini":
        try:
            print(f"Using docTR for local text extraction...")
            raw_text = ocr_with_doctr(image_bytes)
            if raw_text:
                print(f"OCR result: {raw_text[:200]}..." if len(raw_text) > 200 else f"OCR result: {raw_text}")
                print(f"Analyzing OCR text with Gemini...")
                extracted = await extract_from_text(raw_text, api_key=gemini_api_key)
                extracted_info = format_extracted_info(extracted)
                if not has_valid_info(extracted_info):
                    print("Gemini analysis failed to extract meaningful info")
                    extracted_info = {}
        except Exception as e:
            print(f"docTR + Gemini error: {e}")
            extracted_info = {}

    # Build result
    result = {
        "equipment_name": extracted_info.get("equipment_name") if extracted_info else None,
        "model_number": extracted_info.get("model_number") if extracted_info else None,
        "manufacturer": extracted_info.get("manufacturer") if extracted_info else None,
        "serial_number": extracted_info.get("serial_number") if extracted_info else None,
        "management_number": extracted_info.get("management_number") if extracted_info else None,
        "weight": extracted_info.get("weight") if extracted_info else None,
        "output_power": extracted_info.get("output_power") if extracted_info else None,
        "engine_model": extracted_info.get("engine_model") if extracted_info else None,
        "year_manufactured": extracted_info.get("year_manufactured") if extracted_info else None,
        "specifications": extracted_info.get("specifications") if extracted_info else None,
        "raw_text": raw_text,
        "method_used": used_method
    }

    return result


def extract_equipment_info_sync(
    image_bytes: bytes,
    method: str = "gemini-vision",
    gemini_api_key: str = None,
    vision_credentials_json: str = None
) -> dict:
    """Synchronous wrapper for extract_equipment_info."""
    return asyncio.run(extract_equipment_info(
        image_bytes,
        method=method,
        gemini_api_key=gemini_api_key,
        vision_credentials_json=vision_credentials_json
    ))
