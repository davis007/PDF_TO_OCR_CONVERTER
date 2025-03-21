"""
PDFの処理を行うモジュール
"""
import fitz  # PyMuPDF
from pdf2image import convert_from_path
from PIL import Image
from .ocr_engine import OCREngine
from .region_selector import RegionSelector

class PDFProcessor:
    """
    PDFの処理を行うクラス
    """
    def __init__(self, input_pdf, output_pdf=None, language='jpn'):
        self.input_pdf = input_pdf
        self.output_pdf = output_pdf if output_pdf else input_pdf
        self.language = language
        self.ocr_engine = OCREngine(language)

    def process(self, exclude_regions=None, dpi=300):
        """
        PDFを処理し、検索可能なテキストレイヤーを追加する

        Args:
            exclude_regions: RegionSelector オブジェクト
            dpi: 画像変換時の解像度
        """
        # PDFを画像に変換
        pages = convert_from_path(self.input_pdf, dpi=dpi)

        # 元のPDFを開く
        doc = fitz.open(self.input_pdf)

        # 各ページを処理
        for page_num, page_image in enumerate(pages):
            # 現在のページを取得
            page = doc[page_num]

            # 除外領域を計算
            page_regions = None
            if exclude_regions:
                page_regions = exclude_regions.get_exclude_regions_for_page(
                    page_image.width, page_image.height
                )

            # OCRでテキストと位置情報を抽出
            ocr_data = self.ocr_engine.process_image(page_image, page_regions)

            # テキストレイヤーを追加
            self._add_text_layer(page, ocr_data, dpi)

        # PDFを保存
        if self.input_pdf == self.output_pdf:
            # 上書き保存
            doc.save(self.output_pdf, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
        else:
            # 新規保存
            doc.save(self.output_pdf)

        doc.close()

    def _add_text_layer(self, page, ocr_data, dpi):
        """
        ページにテキストレイヤーを追加する

        Args:
            page: fitz.Page オブジェクト
            ocr_data: OCR結果（pytesseract.image_to_data の出力形式）
            dpi: 画像変換時の解像度
        """
        # OCRデータから有効なテキストのみを抽出
        for i in range(len(ocr_data['text'])):
            if ocr_data['text'][i].strip():
                # 座標とサイズを取得
                x, y, w, h = (
                    ocr_data['left'][i],
                    ocr_data['top'][i],
                    ocr_data['width'][i],
                    ocr_data['height'][i]
                )

                # DPIから座標を変換（画像のDPI → PDFの72dpi）
                scale = 72.0 / dpi
                x, y, w, h = x*scale, y*scale, w*scale, h*scale

                # テキストを透明で配置（検索可能だが表示されない）
                page.insert_text(
                    (x, y),
                    ocr_data['text'][i],
                    fontsize=h,
                    color=(0, 0, 0, 0)  # 透明
                )
