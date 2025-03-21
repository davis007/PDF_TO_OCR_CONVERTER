# PDF OCR Converter

画像のみのPDFからOCRを用いてテキストを抽出し、検索可能なPDFを生成するツールです。

## 機能

- 画像PDFからテキストを抽出し、検索可能なPDFを生成
- 元のレイアウトを完全に保持したまま、透明なテキストレイヤーを追加
- 上部や下部など、特定の領域をOCR処理から除外する機能
- ピクセル単位で除外領域を指定可能
- バッチ処理機能（複数のPDFを一括処理）
- 並列処理による高速化

## インストール

### 必要なソフトウェア

- Python 3.6以上
- Tesseract OCR

#### Tesseract OCRのインストール

macOSの場合:

```bash
brew install tesseract
brew install tesseract-lang  # 追加言語パックをインストール
```

### Pythonパッケージのインストール

```bash
# 開発版としてインストール
pip install -e .
```

または

```bash
# 依存ライブラリのみインストール
pip install -r requirements.txt
```

## 使用方法

### 基本的な使い方

```bash
# 単一ファイルの処理
python main.py -f input.pdf -o output.pdf

# ディレクトリ内のすべてのPDFを処理
python main.py -d input_folder -o output_folder
```

### 上書き保存

```bash
# 元のファイルを上書き
python main.py -f input.pdf --overwrite

# ディレクトリ内のすべてのPDFを上書き
python main.py -d input_folder --overwrite
```

### 除外領域の指定

```bash
# 上部を除外
python main.py -f input.pdf --exclude-top

# 上部と下部を除外
python main.py -f input.pdf --exclude-top --exclude-bottom

# 上部の除外割合を20%、下部の除外割合を10%に設定
python main.py -f input.pdf --exclude-top --top-percentage 20 --exclude-bottom --bottom-percentage 10
```

### ピクセル単位の除外領域指定

```bash
# ピクセル座標で除外領域を指定
python main.py -f input.pdf --exclude-region 50 100 500 150

# 複数の除外領域を指定
python main.py -f input.pdf --exclude-region 50 100 500 150 --exclude-region 50 700 500 750
```

### 設定ファイルの使用

設定ファイルを使用すると、PDF毎に異なる除外領域を指定できます。

#### 設定ファイルのテンプレート作成

```bash
python pdf_ocr_converter/config_helper.py input1.pdf input2.pdf -o exclude_regions.json
```

生成された設定ファイルを編集して、除外領域を調整します。

#### 設定ファイルを使用した処理

```bash
python main.py -f input.pdf --config exclude_regions.json
python main.py -d input_folder --config exclude_regions.json
```

### その他のオプション

```bash
# OCRの言語設定を変更（日本語と英語）
python main.py -f input.pdf -l jpn+eng

# 並列処理のワーカー数を指定
python main.py -d input_folder -w 8

# 画像変換時の解像度を指定
python main.py -f input.pdf --dpi 600
```

## 設定ファイルの形式

設定ファイルはJSON形式で、以下のような構造になっています：

```json
{
  "global": {
    "regions": [
      {"type": "top", "height_percentage": 10},
      {"type": "bottom", "height_percentage": 5}
    ]
  },
  "specific_files": {
    "document1.pdf": {
      "regions": [
        {"type": "pixel", "coordinates": [50, 100, 500, 150]},
        {"type": "pixel", "coordinates": [50, 700, 500, 750]}
      ]
    },
    "document2.pdf": {
      "regions": [
        {"type": "pixel", "coordinates": [100, 200, 400, 300]}
      ]
    }
  }
}
```

- `global`: すべてのPDFに適用される設定
- `specific_files`: 特定のPDFファイルに適用される設定（ファイル名をキーとして使用）
- `regions`: 除外領域のリスト
  - `type`: 領域のタイプ（`top`, `bottom`, `pixel`）
  - `height_percentage`: 上部/下部の場合の高さの割合（%）
  - `coordinates`: ピクセル座標 [x1, y1, x2, y2]

## ライセンス

MIT
