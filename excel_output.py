"""Excel output functionality for batch processing results."""
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd


def create_excel_report(
    results: List[Dict],
    output_path: Optional[Path] = None,
    sheet_name: str = "OCR解析結果"
) -> Path:
    """Create Excel report from extraction results.

    Args:
        results: List of dictionaries with extraction results
        output_path: Output file path (auto-generated if not provided)
        sheet_name: Name of the Excel sheet

    Returns:
        Path to the created Excel file
    """
    if output_path is None:
        output_path = Path(f"機器情報抽出結果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")

    # Create DataFrame
    df = pd.DataFrame(results)

    # Save to Excel
    df.to_excel(output_path, index=False, sheet_name=sheet_name)

    # Apply styling
    try:
        from openpyxl import load_workbook
        from openpyxl.styles import Alignment, Font, PatternFill

        wb = load_workbook(output_path)
        ws = wb.active

        # Header styling
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")

        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # Column widths
        column_widths = {
            'A': 6,   # No.
            'B': 18,  # File name
            'C': 15,  # Equipment name
            'D': 15,  # Brand/Manufacturer
            'E': 25,  # Model number
            'F': 18,  # Serial number
            'G': 18,  # Management number
            'H': 12,  # Weight
            'I': 12,  # Output power
            'J': 14,  # Image size
            'K': 14,  # File size
            'L': 50,  # Extracted text
            'M': 12,  # Confidence
            'N': 15,  # Method
            'O': 20,  # Process time
        }

        for col, width in column_widths.items():
            if col in ws.column_dimensions:
                ws.column_dimensions[col].width = width

        # Text column wrap
        text_col = None
        for idx, cell in enumerate(ws[1]):
            if '抽出テキスト' in str(cell.value) or 'raw_text' in str(cell.value).lower():
                text_col = cell.column_letter
                break

        if text_col:
            for row in range(2, len(results) + 2):
                ws[f'{text_col}{row}'].alignment = Alignment(wrap_text=True, vertical="top")

        wb.save(output_path)

    except ImportError:
        pass  # openpyxl styling features not available
    except Exception as e:
        print(f"Excel styling error: {e}")

    return output_path


def format_result_for_excel(
    idx: int,
    filename: str,
    extracted_info: Dict,
    image_width: int = None,
    image_height: int = None,
    file_size_kb: float = None,
    confidence: float = None,
    text_count: int = None,
    method_used: str = None
) -> Dict:
    """Format extraction result for Excel output.

    Args:
        idx: Row number
        filename: Image file name
        extracted_info: Extracted equipment information
        image_width: Image width in pixels
        image_height: Image height in pixels
        file_size_kb: File size in KB
        confidence: OCR confidence score
        text_count: Number of text regions detected
        method_used: Extraction method used

    Returns:
        Dictionary formatted for Excel output
    """
    return {
        "No.": idx,
        "ファイル名": filename,
        "機械名": extracted_info.get("equipment_name") or "不明",
        "メーカー": extracted_info.get("manufacturer") or "不明",
        "型番": extracted_info.get("model_number") or "不明",
        "シリアル番号": extracted_info.get("serial_number") or "不明",
        "管理番号": extracted_info.get("management_number") or "不明",
        "重量": extracted_info.get("weight") or "-",
        "出力": extracted_info.get("output_power") or "-",
        "画像サイズ": f"{image_width}x{image_height}" if image_width and image_height else "-",
        "ファイルサイズ(KB)": round(file_size_kb, 1) if file_size_kb else "-",
        "抽出テキスト(全文)": extracted_info.get("raw_text", "")[:500] if extracted_info.get("raw_text") else "",
        "OCR信頼度": f"{confidence:.1%}" if confidence else "-",
        "テキスト検出数": text_count if text_count else "-",
        "処理方法": method_used or "-",
        "処理日時": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
