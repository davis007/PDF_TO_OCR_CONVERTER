"""
除外領域の設定を管理するモジュール
"""

class RegionSelector:
    """
    OCR処理時に除外する領域を管理するクラス
    """
    def __init__(self):
        self.exclude_regions = []

    def add_top_region(self, height_percentage=10):
        """ページ上部の特定割合を除外領域として追加"""
        self.exclude_regions.append({
            'type': 'top',
            'height_percentage': height_percentage
        })

    def add_bottom_region(self, height_percentage=5):
        """ページ下部の特定割合を除外領域として追加"""
        self.exclude_regions.append({
            'type': 'bottom',
            'height_percentage': height_percentage
        })

    def add_pixel_region(self, x1, y1, x2, y2):
        """ピクセル単位で指定された領域を除外領域として追加"""
        self.exclude_regions.append({
            'type': 'pixel',
            'coordinates': (x1, y1, x2, y2)
        })

    def add_regions_from_config(self, regions_config):
        """設定から複数の除外領域を追加"""
        for region in regions_config:
            if region['type'] == 'top':
                self.add_top_region(region.get('height_percentage', 10))
            elif region['type'] == 'bottom':
                self.add_bottom_region(region.get('height_percentage', 5))
            elif region['type'] == 'pixel':
                coords = region['coordinates']
                self.add_pixel_region(coords[0], coords[1], coords[2], coords[3])

    def get_exclude_regions_for_page(self, page_width, page_height):
        """ページサイズに基づいて除外領域の座標を計算"""
        regions = []
        for region in self.exclude_regions:
            if region['type'] == 'top':
                height = page_height * region['height_percentage'] / 100
                regions.append((0, 0, page_width, height))
            elif region['type'] == 'bottom':
                height = page_height * region['height_percentage'] / 100
                bottom_y = page_height - height
                regions.append((0, bottom_y, page_width, page_height))
            elif region['type'] == 'pixel':
                # ピクセル単位の座標はそのまま使用
                regions.append(region['coordinates'])
        return regions
