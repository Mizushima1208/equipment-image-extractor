"""Example usage of equipment-image-extractor."""
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from extractor import extract_equipment_info_sync


def main():
    """Example: Extract equipment info from an image file."""

    # Check for image path argument
    if len(sys.argv) < 2:
        print("Usage: python example.py <image_path> [method]")
        print("")
        print("Methods:")
        print("  gemini-vision (default) - Fast, direct image analysis with Gemini")
        print("  google-vision-gemini    - High accuracy Google Vision OCR + Gemini AI")
        print("  easyocr                 - Local EasyOCR + pattern matching (no cloud)")
        print("  easyocr-gemini          - Local EasyOCR + Gemini AI analysis")
        print("")
        print("Environment variables:")
        print("  GEMINI_API_KEY                - Gemini API key (required for gemini methods)")
        print("  GOOGLE_SERVICE_ACCOUNT_JSON   - Google Cloud credentials (for google-vision)")
        print("")
        print("Examples:")
        print("  python example.py nameplate.jpg")
        print("  python example.py tool.png easyocr")
        print("  python example.py machine.jpg google-vision-gemini")
        return

    image_path = sys.argv[1]
    method = sys.argv[2] if len(sys.argv) > 2 else "gemini-vision"

    # Check API key for Gemini methods
    if "gemini" in method and not os.environ.get("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable not set")
        print("Get your API key from: https://aistudio.google.com/app/apikey")
        return

    # Read image
    if not os.path.exists(image_path):
        print(f"Error: File not found: {image_path}")
        return

    print(f"Reading image: {image_path}")
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    print(f"Image size: {len(image_bytes)} bytes")
    print(f"Method: {method}")
    print("")

    # Extract info
    try:
        result = extract_equipment_info_sync(image_bytes, method=method)

        print("=" * 50)
        print("Extracted Information:")
        print("=" * 50)
        print(f"Equipment Name:     {result.get('equipment_name') or '-'}")
        print(f"Model Number:       {result.get('model_number') or '-'}")
        print(f"Manufacturer:       {result.get('manufacturer') or '-'}")
        print(f"Serial Number:      {result.get('serial_number') or '-'}")
        print(f"Management Number:  {result.get('management_number') or '-'}")
        print(f"Weight:             {result.get('weight') or '-'}")
        print(f"Output Power:       {result.get('output_power') or '-'}")
        print(f"Engine Model:       {result.get('engine_model') or '-'}")
        print(f"Year Manufactured:  {result.get('year_manufactured') or '-'}")
        print(f"Specifications:     {result.get('specifications') or '-'}")
        print("")
        print(f"Method Used: {result.get('method_used')}")

        if result.get('raw_text') and not result['raw_text'].startswith('('):
            print("")
            print("OCR Text:")
            print("-" * 50)
            print(result['raw_text'][:500])
            if len(result['raw_text']) > 500:
                print("... (truncated)")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
