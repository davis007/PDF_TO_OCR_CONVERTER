"""
除外領域設定ファイルのテンプレートを作成するヘルパースクリプト
"""
import json
import os
import argparse
import fitz  # PyMuPDF

def create_config_template(pdf_files, output_file):
    """
    PDFファイルのリストから設定ファイルのテンプレートを作成

    Args:
        pdf_files: PDFファイルのリスト
        output_file: 出力する設定ファイルのパス
    """
    config = {
        "global": {
            "regions": [
                {"type": "top", "height_percentage": 10},
                {"type": "bottom", "height_percentage": 5}
            ]
        },
        "specific_files": {}
    }

    for pdf_file in pdf_files:
        basename = os.path.basename(pdf_file)

        # PDFの最初のページのサイズを取得（参考情報として）
        try:
            doc = fitz.open(pdf_file)
            if doc.page_count > 0:
                page = doc[0]
                width, height = page.rect.width, page.rect.height
                config["specific_files"][basename] = {
                    "info": f"Page size: {width}x{height} points",
                    "regions": [
                        # サンプルの除外領域（実際の値に置き換える必要あり）
                        {"type": "pixel", "coordinates": [50, 100, 500, 150]}
                    ]
                }
            doc.close()
        except Exception as e:
            print(f"警告: {pdf_file} を開けませんでした: {e}")
            config["specific_files"][basename] = {
                "regions": []
            }

    # 設定ファイルを保存
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"設定テンプレートを {output_file} に保存しました。")
    print("必要に応じて除外領域の座標を編集してください。")

def main():
    parser = argparse.ArgumentParser(description='PDF除外領域設定ファイルのテンプレートを作成')
    parser.add_argument('pdf_files', nargs='+', help='設定を作成するPDFファイル')
    parser.add_argument('-o', '--output', default='exclude_regions.json', help='出力する設定ファイル名')

    args = parser.parse_args()
    create_config_template(args.pdf_files, args.output)

if __name__ == "__main__":
    main()
