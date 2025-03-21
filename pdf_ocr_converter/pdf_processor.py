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

    def process(self, exclude_regions=None, dpi=300, orientation=OCREngine.AUTO):
        """
        PDFを処理し、検索可能なテキストレイヤーを追加する

        Args:
            exclude_regions: RegionSelector オブジェクト
            dpi: 画像変換時の解像度
            orientation: テキストの向き ('auto', 'horizontal', 'vertical')
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

            # OCRでテキストと位置情報を抽出（向きも検出）
            ocr_data, detected_orientation = self.ocr_engine.process_image(
                page_image, page_regions, orientation
            )

            # テキストレイヤーを追加
            self._add_text_layer(page, ocr_data, dpi, detected_orientation)

            # 検出された向きを表示
            print(f"ページ {page_num+1}: {'縦書き' if detected_orientation == OCREngine.VERTICAL else '横書き'} テキスト検出")

        # PDFを保存
        if self.input_pdf == self.output_pdf:
            # 上書き保存
            doc.save(self.output_pdf, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
        else:
            # 新規保存
            doc.save(self.output_pdf)

        doc.close()

    def _add_text_layer(self, page, ocr_data, dpi, orientation):
        """
        ページにテキストレイヤーを追加する

        Args:
            page: fitz.Page オブジェクト
            ocr_data: OCR結果（pytesseract.image_to_data の出力形式）
            dpi: 画像変換時の解像度
            orientation: 検出されたテキストの向き ('horizontal' または 'vertical')
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
                if orientation == OCREngine.HORIZONTAL:
                    # 横書きテキストの場合
                    page.insert_text(
                        (x, y),
                        ocr_data['text'][i],
                        fontsize=h,
                        color=(0, 0, 0, 0)  # 透明
                    )
                else:
                    # 縦書きテキストの場合
                    # 縦書きテキストの場合は、テキストを90度回転させて配置
                    # PyMuPDFでは直接縦書きテキストを配置する方法が限られているため、
                    # 文字ごとに配置する方法を採用
                    text = ocr_data['text'][i]
                    char_height = h / len(text) if len(text) > 0 else h

                    for j, char in enumerate(text):
                        if char.strip():  # 空白文字はスキップ
                            # 縦書きの場合、文字を上から下に配置
                            char_y = y + j * char_height
                            page.insert_text(
                                (x, char_y),
                                char,
                                fontsize=w,  # 縦書きの場合は幅をフォントサイズとして使用
                                color=(0, 0, 0, 0)  # 透明
                            )
