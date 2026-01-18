"""Pattern matching for product information detection."""
import re
from typing import Dict, List, Set

# Brand list - Add your own brands here
# Example: BRANDS = ['SONY', 'SAMSUNG', 'APPLE', ...]
BRANDS = []

# Model number patterns (generic patterns for various products)
MODEL_PATTERNS = [
    r'[A-Z]{2,4}[-]?\d{2,4}[A-Z]?\d*',  # ABC-1234, XY123
    r'[A-Z]{2,3}\d{3,4}[-]?[A-Z]{0,2}\d*',  # AB1234, ABC123-X
    r'[A-Z]{1,2}[-]?\d{1,3}[A-Z]?',  # A-123, B1
    r'[A-Z]{3,}\d+[A-Z]*',  # MODEL123
]

# ID/Management number patterns
MANAGEMENT_PATTERNS = [
    r'\d{7,10}',  # 7-10 digit numbers
    r'\d{5,6}',   # 5-6 digits
]

# Serial number patterns
SERIAL_PATTERNS = [
    r'S/?N[:\s]*([A-Z0-9]+)',
    r'Serial[:\s]*([A-Z0-9]+)',
    r'製造番号[:\s]*([A-Z0-9]+)',
    r'シリアル[:\s]*([A-Z0-9]+)',
]


def detect_brands(text: str) -> List[str]:
    """Detect brand names from text.

    Args:
        text: Text to search for brands

    Returns:
        List of detected brand names
    """
    text_upper = text.upper()
    detected = []

    for brand in BRANDS:
        pattern = brand.replace('*', '.*')
        if re.search(pattern, text_upper, re.IGNORECASE):
            detected.append(brand.replace('.*', ' '))

    return sorted(set(detected))


def extract_model_numbers(text: str) -> List[str]:
    """Extract model numbers from text.

    Args:
        text: Text to search for model numbers

    Returns:
        List of detected model numbers
    """
    model_numbers = set()

    for pattern in MODEL_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            if len(m) >= 2:
                model_numbers.add(m.upper())

    return sorted(model_numbers)[:5]  # Limit to top 5


def extract_management_numbers(text: str) -> List[str]:
    """Extract management numbers (handwritten) from text.

    Args:
        text: Text to search for management numbers

    Returns:
        List of detected management numbers
    """
    numbers = set()

    for pattern in MANAGEMENT_PATTERNS:
        matches = re.findall(pattern, text)
        for m in matches:
            # Exclude phone numbers or dates
            if len(m) >= 5 and not m.startswith('20') and not m.startswith('19'):
                numbers.add(m)

    return sorted(numbers)[:3]  # Limit to top 3


def extract_serial_numbers(text: str) -> List[str]:
    """Extract serial numbers from text.

    Args:
        text: Text to search for serial numbers

    Returns:
        List of detected serial numbers
    """
    serials = []

    for pattern in SERIAL_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        serials.extend(matches)

    return serials[:2]  # Limit to top 2


def extract_tool_info_from_ocr(ocr_results: List) -> Dict:
    """Extract power tool information from OCR results.

    Args:
        ocr_results: List of OCR results, either strings or tuples (bbox, text, confidence)

    Returns:
        Dictionary with extracted tool information
    """
    # Handle different result formats
    if ocr_results and isinstance(ocr_results[0], tuple):
        all_text = "\n".join([r[1] for r in ocr_results])
    else:
        all_text = "\n".join(str(r) for r in ocr_results)

    brands = detect_brands(all_text)
    models = extract_model_numbers(all_text)
    management = extract_management_numbers(all_text)
    serials = extract_serial_numbers(all_text)

    return {
        'brand': ', '.join(brands) if brands else None,
        'model_number': ', '.join(models) if models else None,
        'management_number': ', '.join(management) if management else None,
        'serial_number': ', '.join(serials) if serials else None,
        'raw_text': all_text
    }
