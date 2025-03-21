#!/usr/bin/env python3
"""
画像PDFからOCRでテキストを抽出し検索可能なPDFを生成するツール
"""
import argparse
import os
from .pdf_processor import PDFProcessor
from .batch_handler import BatchProcessor
from .region_selector import RegionSelector
from .config import ExcludeConfig

def main():
    parser = argparse.ArgumentParser(description='画像PDFからOCRでテキストを抽出し検索可能なPDFを生成')

    # 入力と出力の指定方法をグループ化
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('-f', '--file', help='処理する単一のPDFファイルパス')
    input_group.add_argument('-d', '--directory', help='処理するPDFファイルを含むディレクトリパス')

    # 出力先の指定（オプション）
    parser.add_argument('-o', '--output', help='出力先（ファイルまたはディレクトリ）')

    # 上書きオプション
    parser.add_argument('--overwrite', action='store_true', help='元のファイルを上書き保存')

    # 除外領域の設定 - 上部/下部
    parser.add_argument('--exclude-top', action='store_true', help='ページ上部を除外')
    parser.add_argument('--top-percentage', type=int, default=10, help='除外する上部の割合（％）')
    parser.add_argument('--exclude-bottom', action='store_true', help='ページ下部を除外')
    parser.add_argument('--bottom-percentage', type=int, default=5, help='除外する下部の割合（％）')

    # 除外領域の設定 - カスタム/設定ファイル
    parser.add_argument('--exclude-region', action='append', type=int, nargs=4,
                        metavar=('X1', 'Y1', 'X2', 'Y2'),
                        help='除外する領域をピクセル座標で指定 (複数指定可)')
    parser.add_argument('--config', help='除外領域設定ファイルのパス')

    # その他のオプション
    parser.add_argument('-l', '--language', default='jpn', help='OCRの言語設定（デフォルト: jpn）')
    parser.add_argument('-w', '--workers', type=int, default=4, help='並列処理のワーカー数（デフォルト: 4）')
    parser.add_argument('--dpi', type=int, default=300, help='画像変換時の解像度（デフォルト: 300）')

    args = parser.parse_args()

    # 設定ファイルの読み込み
    exclude_config = None
    if args.config:
        exclude_config = ExcludeConfig(args.config)

    # 処理の実行
    if args.file:
        # 単一ファイルの処理
        output = args.output if not args.overwrite else args.file

        # 除外領域の設定
        region_selector = RegionSelector()

        # 上部/下部の除外設定
        if args.exclude_top:
            region_selector.add_top_region(args.top_percentage)
        if args.exclude_bottom:
            region_selector.add_bottom_region(args.bottom_percentage)

        # カスタム領域の追加
        if args.exclude_region:
            for region in args.exclude_region:
                region_selector.add_pixel_region(*region)

        # 設定ファイルからの設定
        if exclude_config:
            regions_config = exclude_config.get_regions_for_file(args.file)
            region_selector.add_regions_from_config(regions_config)

        # PDFを処理
        processor = PDFProcessor(args.file, output, args.language)
        processor.process(exclude_regions=region_selector, dpi=args.dpi)

        print(f"処理完了: {args.file} -> {output}")
    else:
        # ディレクトリ内のすべてのPDFを処理
        output_dir = args.output if not args.overwrite else args.directory
        batch_processor = BatchProcessor(
            args.directory,
            output_dir,
            language=args.language,
            exclude_config=exclude_config,
            exclude_top=args.exclude_top,
            top_percentage=args.top_percentage,
            exclude_bottom=args.exclude_bottom,
            bottom_percentage=args.bottom_percentage,
            custom_regions=args.exclude_region,
            overwrite=args.overwrite,
            max_workers=args.workers
        )
        batch_processor.process_all()

if __name__ == "__main__":
    main()
