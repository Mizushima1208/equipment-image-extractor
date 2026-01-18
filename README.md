# Equipment Image Extractor

建設機械・産業機器・電動工具の銘板画像から情報を抽出するライブラリ。

## フォルダ構成

```
equipment-image-extractor/
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

## 機能

- **複数のOCRエンジン対応**
  - EasyOCR (ローカル、GPU不要)
  - Tesseract (ローカル)
  - Google Cloud Vision API (クラウド、高精度)

- **AI解析**
  - Gemini Vision (画像から直接抽出)
  - Gemini Text (OCRテキストを解析)

- **画像前処理**
  - EXIF回転補正
  - コントラスト強調、シャープ化
  - 複数角度でのOCR試行

- **バッチ処理**
  - フォルダ内の画像を一括処理
  - Excel形式で結果出力

## インストール

```bash
pip install -r requirements.txt
```

## 環境変数

```bash
# Gemini API (gemini-vision, easyocr-gemini 使用時に必要)
export GEMINI_API_KEY="your-api-key"

# Google Cloud Vision (google-vision-gemini 使用時に必要)
export GOOGLE_SERVICE_ACCOUNT_JSON='{"type": "service_account", ...}'
```

## 使い方

### コマンドライン（単一画像）

```bash
# EasyOCR (ローカル、クラウド不要)
python example.py image.jpg easyocr

# Gemini Vision (推奨、高速)
python example.py image.jpg gemini-vision

# Google Vision + Gemini (高精度)
python example.py image.jpg google-vision-gemini
```

### コマンドライン（バッチ処理）

```bash
# デフォルト: data/input → data/output
python batch_process.py

# カスタムディレクトリを指定
python batch_process.py ./images ./results easyocr
```

### Pythonコード

```python
from equipment_image_extractor import extract_equipment_info_sync

# 画像を読み込み
with open("nameplate.jpg", "rb") as f:
    image_bytes = f.read()

# 情報抽出（ローカルOCR）
result = extract_equipment_info_sync(image_bytes, method="easyocr")

# 情報抽出（Gemini Vision）
result = extract_equipment_info_sync(image_bytes, method="gemini-vision")

print(f"機械名: {result['equipment_name']}")
print(f"型番: {result['model_number']}")
print(f"メーカー: {result['manufacturer']}")
```

### 非同期

```python
import asyncio
from equipment_image_extractor import extract_equipment_info

async def main():
    with open("nameplate.jpg", "rb") as f:
        image_bytes = f.read()

    result = await extract_equipment_info(image_bytes, method="gemini-vision")
    print(result)

asyncio.run(main())
```

## 抽出方法の比較

| メソッド | 速度 | 精度 | クラウド | 用途 |
|---------|------|------|---------|------|
| `easyocr` | 中 | 中 | 不要 | オフライン処理 |
| `gemini-vision` | 高速 | 高 | 必要 | 推奨 |
| `google-vision-gemini` | 中 | 最高 | 必要 | 高精度が必要な場合 |
| `easyocr-gemini` | 中 | 高 | 必要 | ローカルOCR+AI解析 |

## 抽出フィールド

| フィールド | 説明 |
|-----------|------|
| equipment_name | 機械名・製品名 |
| model_number | 型番・MODEL |
| manufacturer | メーカー名 |
| serial_number | シリアル番号 |
| management_number | 管理番号（手書き） |
| weight | 重量 |
| output_power | 出力 |
| engine_model | エンジン型式 |
| year_manufactured | 製造年 |
| specifications | その他の仕様 |
| raw_text | OCRテキスト |
| method_used | 使用した抽出方法 |

## 対応ブランド（自動検出）

- DEWALT, MAKITA, HIKOKI, HITACHI, BOSCH
- MILWAUKEE, RYOBI, HILTI, FESTOOL, METABO
- PANASONIC, MAX, KYOCERA, TAJIMA
- MIKASA, WACKER, BOMAG, AMMANN
- その他多数

## API Key取得

- **Gemini**: https://aistudio.google.com/app/apikey
- **Google Vision**: https://console.cloud.google.com/apis/credentials
