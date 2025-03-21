"""
除外領域設定ファイルを管理するモジュール
"""
import json
import os

class ExcludeConfig:
    """
    除外領域の設定ファイルを管理するクラス
    """
    def __init__(self, config_file=None):
        self.config = {
            "global": {"regions": []},
            "specific_files": {}
        }

        if config_file and os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)

    def get_regions_for_file(self, filename):
        """特定のファイル用の除外領域設定を取得"""
        regions = []

        # グローバル設定を適用
        if "global" in self.config and "regions" in self.config["global"]:
            regions.extend(self.config["global"]["regions"])

        # ファイル固有の設定を適用（存在する場合）
        basename = os.path.basename(filename)
        if "specific_files" in self.config and basename in self.config["specific_files"]:
            if "regions" in self.config["specific_files"][basename]:
                # ファイル固有の設定で上書き
                regions = self.config["specific_files"][basename]["regions"]

        return regions
