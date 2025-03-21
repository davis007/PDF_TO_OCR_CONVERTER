"""
バッチ処理を行うモジュール
"""
import os
import glob
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from .pdf_processor import PDFProcessor
from .region_selector import RegionSelector
from .ocr_engine import OCREngine

class BatchProcessor:
    """
    複数のPDFファイルを一括処理するクラス
    """
    def __init__(self, input_dir, output_dir=None, language='jpn',
                 exclude_config=None, exclude_top=False, top_percentage=10,
                 exclude_bottom=False, bottom_percentage=5,
                 custom_regions=None, overwrite=False, max_workers=4,
                 orientation=OCREngine.AUTO):
        self.input_dir = input_dir
        self.output_dir = output_dir if output_dir else input_dir
        self.language = language
        self.exclude_config = exclude_config
        self.exclude_top = exclude_top
        self.top_percentage = top_percentage
        self.exclude_bottom = exclude_bottom
        self.bottom_percentage = bottom_percentage
        self.custom_regions = custom_regions
        self.overwrite = overwrite
        self.max_workers = max_workers
        self.orientation = orientation

        # 出力ディレクトリが存在しない場合は作成（上書きでない場合）
        if not overwrite and output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def get_pdf_files(self):
        """入力ディレクトリからPDFファイルのリストを取得"""
        return glob.glob(os.path.join(self.input_dir, "*.pdf"))

    def process_single_file(self, pdf_path):
        """単一のPDFファイルを処理"""
        try:
            if self.overwrite:
                output_path = pdf_path
            else:
                filename = os.path.basename(pdf_path)
                output_path = os.path.join(self.output_dir, filename)

            # 除外領域の設定
            region_selector = RegionSelector()

            # 上部/下部の除外設定
            if self.exclude_top:
                region_selector.add_top_region(self.top_percentage)
            if self.exclude_bottom:
                region_selector.add_bottom_region(self.bottom_percentage)

            # カスタム領域の追加
            if self.custom_regions:
                for region in self.custom_regions:
                    region_selector.add_pixel_region(*region)

            # 設定ファイルからの設定
            if self.exclude_config:
                regions_config = self.exclude_config.get_regions_for_file(pdf_path)
                region_selector.add_regions_from_config(regions_config)

            # PDFを処理
            processor = PDFProcessor(pdf_path, output_path, self.language)
            processor.process(exclude_regions=region_selector, orientation=self.orientation)

            return True, pdf_path
        except Exception as e:
            return False, f"{pdf_path}: {str(e)}"

    def process_all(self):
        """すべてのPDFファイルを処理"""
        pdf_files = self.get_pdf_files()
        total_files = len(pdf_files)

        if total_files == 0:
            print(f"指定されたディレクトリ '{self.input_dir}' にPDFファイルが見つかりませんでした。")
            return

        print(f"{total_files}個のPDFファイルを処理します...")
        print(f"テキスト向き設定: {'自動検出' if self.orientation == OCREngine.AUTO else '横書き' if self.orientation == OCREngine.HORIZONTAL else '縦書き'}")

        # 進行状況表示用のtqdmを使用
        with tqdm(total=total_files, desc="処理中") as pbar:
            results = []

            # ThreadPoolExecutorを使用して並列処理
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {executor.submit(self.process_single_file, pdf): pdf for pdf in pdf_files}

                for future in futures:
                    success, result = future.result()
                    if success:
                        results.append((True, result))
                    else:
                        results.append((False, result))
                    pbar.update(1)

        # 結果の表示
        success_count = sum(1 for r in results if r[0])
        print(f"\n処理完了: {success_count}/{total_files} 成功")

        # エラーがあれば表示
        errors = [r[1] for r in results if not r[0]]
        if errors:
            print("\nエラーが発生したファイル:")
            for error in errors:
                print(f"- {error}")
