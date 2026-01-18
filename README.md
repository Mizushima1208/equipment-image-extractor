# Image Extractor

製品の銘板・ラベル画像から情報を抽出するライブラリ。複数のOCRエンジンに対応。

## フォルダ構成

```
image-extractor/
├── data/
│   ├── input/     # ここに画像を配置
│   └── output/    # ここに結果（Excel）が出力される
├── batch_process.py   # バッチ処理スクリプト
├── example.py         # 単一画像処理
└── ...
```

## クイックスタート

1. `data/input/` フォルダに画像を配置
2. `python batch_process.py` を実行
3. `data/output/` に結果のExcelファイルが出力される

## 対応OCRエンジン

| エンジン | 特徴 | 言語数 | クラウド |
|---------|------|--------|---------|
| **EasyOCR** | 使いやすい、GPU不要 | 80+ | 不要 |
| **PaddleOCR** | 高精度、軽量(<10MB) | 109 | 不要 |
| **Surya** | レイアウト解析が得意 | 90+ | 不要 |
| **docTR** | ドキュメント特化 | 多数 | 不要 |
| **Tesseract** | 伝統的OCR | 100+ | 不要 |
| **Google Vision** | クラウド、高精度 | 多数 | 必要 |

## インストール

```bash
# 基本パッケージ
pip install -r requirements.txt

# 追加OCRエンジン（必要なものだけ）
pip install paddleocr paddlepaddle  # PaddleOCR
pip install surya-ocr               # Surya
pip install "python-doctr[torch]"   # docTR (PyTorch版)
pip install pytesseract             # Tesseract
pip install google-cloud-vision     # Google Vision
```

## 環境変数

```bash
# Gemini API (gemini-vision, *-gemini 系メソッド使用時)
export GEMINI_API_KEY="your-api-key"

# Google Cloud Vision (google-vision-gemini 使用時)
export GOOGLE_SERVICE_ACCOUNT_JSON='{"type": "service_account", ...}'
```

## 使い方

### コマンドライン（単一画像）

```bash
# ローカルOCR（クラウド不要）
python example.py image.jpg easyocr
python example.py image.jpg paddleocr
python example.py image.jpg surya
python example.py image.jpg doctr

# ローカルOCR + Gemini解析
python example.py image.jpg easyocr-gemini
python example.py image.jpg paddleocr-gemini

# Gemini Vision（推奨、高速）
python example.py image.jpg gemini-vision

# Google Vision + Gemini（高精度）
python example.py image.jpg google-vision-gemini
```

### コマンドライン（バッチ処理）

```bash
# デフォルト: data/input → data/output
python batch_process.py

# カスタムディレクトリを指定
python batch_process.py ./images ./results paddleocr
```

### Pythonコード

```python
from extractor import extract_equipment_info_sync, AVAILABLE_METHODS
from ocr import get_available_ocr_engines

# 利用可能なOCRエンジンを確認
print(get_available_ocr_engines())

# 利用可能なメソッド一覧
print(AVAILABLE_METHODS)

# 画像を読み込み
with open("label.jpg", "rb") as f:
    image_bytes = f.read()

# 情報抽出
result = extract_equipment_info_sync(image_bytes, method="paddleocr")

print(f"製品名: {result['equipment_name']}")
print(f"型番: {result['model_number']}")
print(f"メーカー: {result['manufacturer']}")
```

### 非同期

```python
import asyncio
from extractor import extract_equipment_info

async def main():
    with open("label.jpg", "rb") as f:
        image_bytes = f.read()

    result = await extract_equipment_info(image_bytes, method="paddleocr-gemini")
    print(result)

asyncio.run(main())
```

## 抽出方法の比較

| メソッド | OCRエンジン | AI解析 | クラウド | 精度 |
|---------|------------|--------|---------|------|
| `easyocr` | EasyOCR | パターン | 不要 | 中 |
| `paddleocr` | PaddleOCR | パターン | 不要 | 高 |
| `surya` | Surya | パターン | 不要 | 高 |
| `doctr` | docTR | パターン | 不要 | 高 |
| `easyocr-gemini` | EasyOCR | Gemini | 必要 | 高 |
| `paddleocr-gemini` | PaddleOCR | Gemini | 必要 | 最高 |
| `surya-gemini` | Surya | Gemini | 必要 | 最高 |
| `doctr-gemini` | docTR | Gemini | 必要 | 最高 |
| `gemini-vision` | Gemini Vision | Gemini | 必要 | 高 |
| `google-vision-gemini` | Google Vision | Gemini | 必要 | 最高 |

## 抽出フィールド

| フィールド | 説明 |
|-----------|------|
| equipment_name | 製品名・品名 |
| model_number | 型番・MODEL |
| manufacturer | メーカー名 |
| serial_number | シリアル番号 |
| management_number | 管理番号 |
| weight | 重量 |
| output_power | 出力・定格 |
| engine_model | モーター型式 |
| year_manufactured | 製造年 |
| specifications | その他の仕様 |
| raw_text | OCRテキスト |
| method_used | 使用した抽出方法 |

## ブランド検出のカスタマイズ

`tool_patterns.py` の `BRANDS` リストにブランド名を追加することで、自動検出できます：

```python
BRANDS = [
    'YOUR_BRAND_1',
    'YOUR_BRAND_2',
    # ...
]
```

## API Key取得

- **Gemini**: https://aistudio.google.com/app/apikey
- **Google Vision**: https://console.cloud.google.com/apis/credentials

## 参考リンク

- [EasyOCR](https://github.com/JaidedAI/EasyOCR)
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- [Surya](https://github.com/VikParuchuri/surya)
- [docTR](https://github.com/mindee/doctr)
- [Tesseract](https://github.com/tesseract-ocr/tesseract)
