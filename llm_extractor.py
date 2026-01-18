"""LLM-based equipment information extraction using Gemini."""
import base64
import json
import os
import re
import httpx
from typing import Optional


# Default Gemini API Key (override with GEMINI_API_KEY env var)
DEFAULT_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Vision prompt - for reading product labels/nameplates
VISION_PROMPT = """この画像は製品の銘板（ネームプレート）、ラベル、または本体の写真です。
以下の情報を読み取ってください。

以下のJSON形式で出力してください（他の文字は含めないでください）:
{
    "equipment_name": "製品名・品名",
    "model_number": "型番・MODEL",
    "manufacturer": "メーカー名・製造者",
    "serial_number": "シリアル番号・製造番号",
    "management_number": "管理番号（手書きの番号がある場合）",
    "weight": "重量",
    "output_power": "出力・定格",
    "engine_model": "エンジン型式・モーター型式",
    "year_manufactured": "製造年",
    "specifications": "その他の仕様（読み取れた情報）"
}

注意:
- 銘板・ラベルに書かれている情報を正確に読み取ってください
- 汚れや傷で読めない部分はnull
- 型番（MODEL）は最も重要な情報です
- メーカーは銘板のロゴや会社名から特定してください
"""

# Text extraction prompt - for OCR text analysis
EXTRACTION_PROMPT = """以下は製品の銘板・ラベルのOCRテキストです。情報を抽出してください。

OCRテキスト:
{text}

以下のJSON形式で出力してください（他の文字は含めないでください）:
{{
    "equipment_name": "製品名・品名",
    "model_number": "型番・MODEL",
    "manufacturer": "メーカー名",
    "serial_number": "シリアル番号",
    "management_number": "管理番号",
    "weight": "重量",
    "output_power": "出力・定格",
    "engine_model": "エンジン型式・モーター型式",
    "year_manufactured": "製造年",
    "specifications": "その他の仕様"
}}

注意:
- 見つからない項目はnull
- 型番（MODEL）を最優先で抽出
"""


def extract_json_from_response(text: str) -> Optional[dict]:
    """Extract JSON from LLM response."""
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    return None


async def extract_from_image(image_bytes: bytes, api_key: str = None) -> Optional[dict]:
    """Extract product info directly from image using Gemini Vision.

    Args:
        image_bytes: Image data as bytes
        api_key: Gemini API key (optional, uses GEMINI_API_KEY env var if not provided)

    Returns:
        Dictionary with extracted equipment information
    """
    key = api_key or DEFAULT_API_KEY
    if not key:
        raise Exception("Gemini API Key not set. Set GEMINI_API_KEY env var or provide api_key parameter.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent?key={key}"

    # Encode image to base64
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

    # Detect mime type
    mime_type = "image/jpeg"
    if image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
        mime_type = "image/png"
    elif image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
        mime_type = "image/webp"

    payload = {
        "contents": [{
            "parts": [
                {"text": VISION_PROMPT},
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": image_base64
                    }
                }
            ]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 2048
        }
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=payload)

        if response.status_code != 200:
            raise Exception(f"Gemini Vision API error: {response.status_code} - {response.text}")

        result = response.json()
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        return extract_json_from_response(text)


async def extract_from_text(ocr_text: str, api_key: str = None) -> Optional[dict]:
    """Extract product info from OCR text using Gemini.

    Args:
        ocr_text: OCR extracted text
        api_key: Gemini API key (optional)

    Returns:
        Dictionary with extracted equipment information
    """
    key = api_key or DEFAULT_API_KEY
    if not key:
        raise Exception("Gemini API Key not set. Set GEMINI_API_KEY env var or provide api_key parameter.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent?key={key}"

    payload = {
        "contents": [{
            "parts": [{
                "text": EXTRACTION_PROMPT.format(text=ocr_text)
            }]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 1024
        }
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)

        if response.status_code != 200:
            raise Exception(f"Gemini API error: {response.status_code} - {response.text}")

        result = response.json()
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        return extract_json_from_response(text)


def format_extracted_info(extracted: dict) -> Optional[dict]:
    """Format extracted info to clean dictionary."""
    if not extracted:
        return None

    # Format weight
    weight = extracted.get("weight")
    if weight:
        weight_num = re.sub(r'[^\d\.]', '', str(weight))
        weight = f"{weight_num} kg" if weight_num else None

    return {
        "equipment_name": extracted.get("equipment_name"),
        "model_number": extracted.get("model_number"),
        "manufacturer": extracted.get("manufacturer"),
        "serial_number": extracted.get("serial_number"),
        "management_number": extracted.get("management_number"),
        "weight": weight,
        "output_power": extracted.get("output_power"),
        "engine_model": extracted.get("engine_model"),
        "year_manufactured": extracted.get("year_manufactured"),
        "specifications": extracted.get("specifications")
    }
