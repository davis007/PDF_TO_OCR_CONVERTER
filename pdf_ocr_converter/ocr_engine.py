"""
OCR処理を行うモジュール
"""
import pytesseract
from PIL import Image, ImageDraw
import numpy as np

class OCREngine:
    """
    OCR処理を行うクラス
    """
    # テキストの向き定数
    AUTO = 'auto'
    HORIZONTAL = 'horizontal'
    VERTICAL = 'vertical'

    def __init__(self, language='jpn'):
        self.language = language

    def process_image(self, image, exclude_regions=None, orientation=AUTO):
        """
        画像からテキストを抽出する

        Args:
            image: PIL.Image オブジェクト
            exclude_regions: 除外領域のリスト [(x1, y1, x2, y2), ...]
            orientation: テキストの向き ('auto', 'horizontal', 'vertical')

        Returns:
            dict: OCR結果（pytesseract.image_to_data の出力形式）
            str: 検出されたテキストの向き ('horizontal' または 'vertical')
        """
        # 画像のコピーを作成
        img_copy = image.copy()

        # 除外領域をマスク処理
        if exclude_regions:
            draw = ImageDraw.Draw(img_copy)
            for region in exclude_regions:
                # 指定領域を白で塗りつぶし
                draw.rectangle(region, fill="white")

        # テキストの向きに基づいて処理
        if orientation == self.AUTO:
            # 自動判別モード
            horizontal_data = self._process_with_orientation(img_copy, self.HORIZONTAL)
            vertical_data = self._process_with_orientation(img_copy, self.VERTICAL)

            # 信頼度スコアを計算して比較
            horizontal_score = self._calculate_confidence_score(horizontal_data)
            vertical_score = self._calculate_confidence_score(vertical_data)

            print(f"横書き信頼度: {horizontal_score:.2f}, 縦書き信頼度: {vertical_score:.2f}")

            if vertical_score > horizontal_score:
                return vertical_data, self.VERTICAL
            else:
                return horizontal_data, self.HORIZONTAL
        else:
            # 指定された向きで処理
            ocr_data = self._process_with_orientation(img_copy, orientation)
            return ocr_data, orientation

    def _process_with_orientation(self, image, orientation):
        """
        指定された向きでOCR処理を行う

        Args:
            image: PIL.Image オブジェクト
            orientation: テキストの向き ('horizontal' または 'vertical')

        Returns:
            dict: OCR結果
        """
        # PSMの設定
        config = ''
        if orientation == self.HORIZONTAL:
            config = '--psm 3'  # 3 = 自動ページセグメンテーション（横書き）
        else:
            config = '--psm 5'  # 5 = 縦書きテキスト

        # OCRでテキストと位置情報を抽出
        ocr_data = pytesseract.image_to_data(
            image,
            lang=self.language,
            config=config,
            output_type=pytesseract.Output.DICT
        )

        return ocr_data

    def _calculate_confidence_score(self, ocr_data):
        """
        OCR結果の信頼度スコアを計算する

        Args:
            ocr_data: OCR結果

        Returns:
            float: 信頼度スコア
        """
        # 有効なテキストのみを対象
        valid_indices = [i for i, text in enumerate(ocr_data['text']) if text.strip()]

        if not valid_indices:
            return 0.0

        # 信頼度の平均を計算
        confidences = [ocr_data['conf'][i] for i in valid_indices]
        avg_confidence = np.mean([c for c in confidences if c > 0])

        # テキスト量も考慮
        text_amount = sum(len(ocr_data['text'][i]) for i in valid_indices)

        # 最終スコア = 平均信頼度 × テキスト量の対数
        if text_amount > 0:
            return avg_confidence * np.log1p(text_amount)
        return 0.0

    def get_text_only(self, image, exclude_regions=None, orientation=AUTO):
        """
        画像からテキストのみを抽出する（位置情報なし）

        Args:
            image: PIL.Image オブジェクト
            exclude_regions: 除外領域のリスト [(x1, y1, x2, y2), ...]
            orientation: テキストの向き ('auto', 'horizontal', 'vertical')

        Returns:
            str: 抽出されたテキスト
            str: 検出されたテキストの向き ('horizontal' または 'vertical')
        """
        # 画像のコピーを作成
        img_copy = image.copy()

        # 除外領域をマスク処理
        if exclude_regions:
            draw = ImageDraw.Draw(img_copy)
            for region in exclude_regions:
                # 指定領域を白で塗りつぶし
                draw.rectangle(region, fill="white")

        # テキストの向きに基づいて処理
        if orientation == self.AUTO:
            # 自動判別モード
            config_h = '--psm 3'  # 横書き
            config_v = '--psm 5'  # 縦書き

            text_h = pytesseract.image_to_string(img_copy, lang=self.language, config=config_h)
            text_v = pytesseract.image_to_string(img_copy, lang=self.language, config=config_v)

            # 簡易的な判定（テキスト量で比較）
            if len(text_v.strip()) > len(text_h.strip()) * 1.2:  # 縦書きの方が20%以上多い場合
                return text_v, self.VERTICAL
            else:
                return text_h, self.HORIZONTAL
        else:
            # 指定された向きで処理
            config = '--psm 3' if orientation == self.HORIZONTAL else '--psm 5'
            text = pytesseract.image_to_string(img_copy, lang=self.language, config=config)
            return text, orientation
