"""
OCR処理を行うモジュール
"""
import pytesseract
from PIL import Image, ImageDraw

class OCREngine:
    """
    OCR処理を行うクラス
    """
    def __init__(self, language='jpn'):
        self.language = language

    def process_image(self, image, exclude_regions=None):
        """
        画像からテキストを抽出する

        Args:
            image: PIL.Image オブジェクト
            exclude_regions: 除外領域のリスト [(x1, y1, x2, y2), ...]

        Returns:
            dict: OCR結果（pytesseract.image_to_data の出力形式）
        """
        # 画像のコピーを作成
        img_copy = image.copy()

        # 除外領域をマスク処理
        if exclude_regions:
            draw = ImageDraw.Draw(img_copy)
            for region in exclude_regions:
                # 指定領域を白で塗りつぶし
                draw.rectangle(region, fill="white")

        # OCRでテキストと位置情報を抽出
        ocr_data = pytesseract.image_to_data(
            img_copy,
            lang=self.language,
            output_type=pytesseract.Output.DICT
        )

        return ocr_data

    def get_text_only(self, image, exclude_regions=None):
        """
        画像からテキストのみを抽出する（位置情報なし）

        Args:
            image: PIL.Image オブジェクト
            exclude_regions: 除外領域のリスト [(x1, y1, x2, y2), ...]

        Returns:
            str: 抽出されたテキスト
        """
        # 画像のコピーを作成
        img_copy = image.copy()

        # 除外領域をマスク処理
        if exclude_regions:
            draw = ImageDraw.Draw(img_copy)
            for region in exclude_regions:
                # 指定領域を白で塗りつぶし
                draw.rectangle(region, fill="white")

        # OCRでテキストを抽出
        text = pytesseract.image_to_string(img_copy, lang=self.language)

        return text
