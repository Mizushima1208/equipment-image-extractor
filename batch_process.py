"""Batch processing for multiple images with Excel output."""
import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from extractor import extract_equipment_info_sync
from excel_output import create_excel_report, format_result_for_excel
from image_processor import load_image
from PIL import Image


def process_directory(
    input_dir: Path,
    output_dir: Path = None,
    method: str = "easyocr"
):
    """Process all images in a directory and create Excel report.

    Args:
        input_dir: Directory containing images
        output_dir: Output directory for Excel report
        method: Extraction method to use
    """
    if output_dir is None:
        output_dir = input_dir / "output"

    output_dir.mkdir(parents=True, exist_ok=True)

    # Find image files
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tif', '.tiff')
    image_files = sorted([
        f for f in input_dir.iterdir()
        if f.suffix.lower() in image_extensions
    ])

    if not image_files:
        print(f"No image files found in: {input_dir}")
        return

    print("=" * 70)
    print("Equipment Image Batch Processor")
    print("=" * 70)
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Method: {method}")
    print(f"Images found: {len(image_files)}")
    print("=" * 70)

    results = []

    for idx, image_path in enumerate(image_files, 1):
        print(f"\nProcessing ({idx}/{len(image_files)}): {image_path.name}")
        print("-" * 50)

        try:
            # Get image info
            img = Image.open(image_path)
            img_width, img_height = img.size
            file_size_kb = image_path.stat().st_size / 1024

            # Read image bytes
            with open(image_path, "rb") as f:
                image_bytes = f.read()

            # Extract information
            extracted = extract_equipment_info_sync(image_bytes, method=method)

            # Format for Excel
            result = format_result_for_excel(
                idx=idx,
                filename=image_path.name,
                extracted_info=extracted,
                image_width=img_width,
                image_height=img_height,
                file_size_kb=file_size_kb,
                method_used=extracted.get("method_used")
            )
            results.append(result)

            print(f"  Equipment: {extracted.get('equipment_name') or '-'}")
            print(f"  Model: {extracted.get('model_number') or '-'}")
            print(f"  Manufacturer: {extracted.get('manufacturer') or '-'}")

        except Exception as e:
            print(f"  Error: {str(e)}")
            results.append({
                "No.": idx,
                "ファイル名": image_path.name,
                "機械名": "エラー",
                "メーカー": "エラー",
                "型番": "エラー",
                "シリアル番号": "エラー",
                "管理番号": "エラー",
                "重量": "-",
                "出力": "-",
                "画像サイズ": "エラー",
                "ファイルサイズ(KB)": 0,
                "抽出テキスト(全文)": f"エラー: {str(e)}",
                "OCR信頼度": "-",
                "テキスト検出数": 0,
                "処理方法": "error",
                "処理日時": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

    # Create Excel report
    output_file = output_dir / f"機器情報抽出結果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    create_excel_report(results, output_file)

    print(f"\n{'=' * 70}")
    print("Processing complete!")
    print(f"{'=' * 70}")
    print(f"Output file: {output_file}")
    print(f"Processed: {len(results)} images")
    print(f"{'=' * 70}")


def main():
    """Main entry point for batch processing."""
    if len(sys.argv) < 2:
        print("Usage: python batch_process.py <input_directory> [output_directory] [method]")
        print("")
        print("Methods:")
        print("  easyocr (default) - Local EasyOCR + pattern matching (no cloud)")
        print("  gemini-vision     - Gemini Vision direct analysis")
        print("  google-vision-gemini - Google Vision OCR + Gemini")
        print("  easyocr-gemini    - Local EasyOCR + Gemini analysis")
        print("")
        print("Example:")
        print("  python batch_process.py ./data ./output easyocr")
        return

    input_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    method = sys.argv[3] if len(sys.argv) > 3 else "easyocr"

    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        return

    process_directory(input_dir, output_dir, method)


if __name__ == "__main__":
    main()
