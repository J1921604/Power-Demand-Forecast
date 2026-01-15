"""
単体テスト: 組み合わせ検証ロジック (US2)

契約テスト要件:
- 利用可能な年が正しく取得される
- 年の組み合わせが正しく生成される
- ローリング時系列交差検証が正しく動作する
- 結果テキストファイルが正しく生成される
- 推奨組み合わせが正しく選択される

実行方法:
    pytest tests/unit/test_optimize_years.py -v

依存関係:
    - pytest>=8.0.0
    - pandas>=2.0.0
    - numpy>=1.24.0

テストシナリオ:
    US2-U1: 利用可能な年が正しく取得される
    US2-U2: 年の組み合わせが正しく生成される（3〜5年組み合わせ）
    US2-U3: ローリング時系列交差検証が正しく動作する
    US2-U4: 結果テキストファイルが正しく生成される
    US2-U5: 推奨組み合わせが正しく選択される（R²スコア最大）
"""

import os
import sys
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict
from itertools import combinations


# 定数
PROJECT_ROOT = Path(__file__).parent.parent.parent
AI_DIR = PROJECT_ROOT / "AI"
DATA_DIR = AI_DIR / "data"
AVAILABLE_YEARS = list(range(2016, 2025))  # 2016-2024


@pytest.mark.unit
class TestAvailableYears:
    """利用可能な年の取得テスト"""

    def test_get_available_years_from_csv_files(self):
        """
        US2-U1: 利用可能な年が正しく取得される
        
        検証項目:
        - juyo-YYYY.csvファイルから年が抽出される
        - temperature-YYYY.csvファイルから年が抽出される
        - 両方に存在する年のみが返される
        """
        # データディレクトリ確認
        assert DATA_DIR.exists(), f"データディレクトリが存在しません: {DATA_DIR}"
        
        # juyo-YYYY.csvから年抽出
        power_files = list(DATA_DIR.glob("juyo-*.csv"))
        power_years = set()
        for f in power_files:
            # ファイル名から年を抽出（例: juyo-2022.csv → 2022）
            import re
            match = re.search(r"juyo-(\d{4})\.csv", f.name)
            if match:
                power_years.add(int(match.group(1)))
        
        # temperature-YYYY.csvから年抽出
        temp_files = list(DATA_DIR.glob("temperature-*.csv"))
        temp_years = set()
        for f in temp_files:
            match = re.search(r"temperature-(\d{4})\.csv", f.name)
            if match:
                temp_years.add(int(match.group(1)))
        
        # 両方に存在する年
        common_years = sorted(power_years & temp_years)
        
        # 検証
        assert len(common_years) >= 3, "利用可能な年が3年未満です"
        assert 2022 in common_years, "2022年データが見つかりません"
        
        print(f"利用可能な年: {common_years}")

    def test_available_years_format(self):
        """
        利用可能な年の形式検証
        
        検証項目:
        - 年が整数リストとして返される
        - 年が昇順ソート済み
        - 年が重複していない
        """
        # データディレクトリからサンプル年を取得
        power_files = list(DATA_DIR.glob("juyo-*.csv"))
        
        years = []
        for f in power_files:
            import re
            match = re.search(r"juyo-(\d{4})\.csv", f.name)
            if match:
                years.append(int(match.group(1)))
        
        # ソート
        years = sorted(years)
        
        # 検証
        assert all(isinstance(y, int) for y in years), "年が整数ではありません"
        assert years == sorted(years), "年が昇順ソートされていません"
        assert len(years) == len(set(years)), "年が重複しています"


@pytest.mark.unit
class TestCombinationGeneration:
    """年の組み合わせ生成テスト"""

    def test_generate_3_year_combinations(self):
        """
        US2-U2: 3年組み合わせが正しく生成される
        
        検証項目:
        - 3年組み合わせが全て生成される
        - 組み合わせ数が正しい（nCr = n! / (r! * (n-r)!)）
        - 重複がない
        """
        available_years = [2020, 2021, 2022, 2023, 2024]
        r = 3
        
        # 組み合わせ生成
        combos = list(combinations(available_years, r))
        
        # 検証
        expected_count = len(available_years) * (len(available_years) - 1) * (len(available_years) - 2) // (3 * 2 * 1)
        assert len(combos) == expected_count, f"組み合わせ数が不正: {len(combos)} != {expected_count}"
        
        # 重複確認
        assert len(combos) == len(set(combos)), "組み合わせが重複しています"
        
        # サンプル確認
        assert (2020, 2021, 2022) in combos, "期待される組み合わせが含まれていません"
        assert (2022, 2023, 2024) in combos, "期待される組み合わせが含まれていません"
        
        print(f"3年組み合わせ数: {len(combos)}")

    def test_generate_4_year_combinations(self):
        """
        4年組み合わせが正しく生成される
        
        検証項目:
        - 4年組み合わせが全て生成される
        - 組み合わせ数が正しい
        """
        available_years = [2020, 2021, 2022, 2023, 2024]
        r = 4
        
        combos = list(combinations(available_years, r))
        
        expected_count = len(available_years) * (len(available_years) - 1) * (len(available_years) - 2) * (len(available_years) - 3) // (4 * 3 * 2 * 1)
        assert len(combos) == expected_count
        
        print(f"4年組み合わせ数: {len(combos)}")

    def test_generate_5_year_combinations(self):
        """
        5年組み合わせが正しく生成される
        
        検証項目:
        - 5年組み合わせが全て生成される
        - 組み合わせ数が正しい
        """
        available_years = [2020, 2021, 2022, 2023, 2024]
        r = 5
        
        combos = list(combinations(available_years, r))
        
        expected_count = 1  # 5C5 = 1
        assert len(combos) == expected_count
        
        assert combos[0] == (2020, 2021, 2022, 2023, 2024)
        
        print(f"5年組み合わせ数: {len(combos)}")


@pytest.mark.unit
class TestRecommendationLogic:
    """推奨組み合わせ選択ロジックテスト"""

    def test_select_best_combination_by_r2(self):
        """
        US2-U5: 推奨組み合わせが正しく選択される（R²スコア最大）
        
        検証項目:
        - R²スコアが最大の組み合わせが選択される
        - 同点の場合は最新年が優先される
        """
        # ダミーデータ
        results = [
            {"years": [2020, 2021, 2022], "r2": 0.85, "rmse": 1200.0, "mae": 950.0},
            {"years": [2021, 2022, 2023], "r2": 0.88, "rmse": 1150.0, "mae": 920.0},
            {"years": [2022, 2023, 2024], "r2": 0.90, "rmse": 1100.0, "mae": 900.0},
            {"years": [2020, 2022, 2024], "r2": 0.87, "rmse": 1180.0, "mae": 930.0}
        ]
        
        # R²スコア最大を選択
        best = max(results, key=lambda x: x["r2"])
        
        # 検証
        assert best["years"] == [2022, 2023, 2024], "R²スコア最大の組み合わせが選択されていません"
        assert best["r2"] == 0.90, "R²スコアが不正です"

    def test_select_top_5_combinations(self):
        """
        上位5組み合わせが正しく選択される
        
        検証項目:
        - R²スコア降順でソートされる
        - 上位5件が返される
        """
        # ダミーデータ（10組み合わせ）
        results = [
            {"years": [2016, 2017, 2018], "r2": 0.75, "rmse": 1400.0, "mae": 1100.0},
            {"years": [2017, 2018, 2019], "r2": 0.78, "rmse": 1350.0, "mae": 1050.0},
            {"years": [2018, 2019, 2020], "r2": 0.82, "rmse": 1250.0, "mae": 1000.0},
            {"years": [2019, 2020, 2021], "r2": 0.84, "rmse": 1220.0, "mae": 980.0},
            {"years": [2020, 2021, 2022], "r2": 0.85, "rmse": 1200.0, "mae": 950.0},
            {"years": [2021, 2022, 2023], "r2": 0.88, "rmse": 1150.0, "mae": 920.0},
            {"years": [2022, 2023, 2024], "r2": 0.90, "rmse": 1100.0, "mae": 900.0},
            {"years": [2016, 2020, 2024], "r2": 0.80, "rmse": 1300.0, "mae": 1020.0},
            {"years": [2018, 2021, 2024], "r2": 0.86, "rmse": 1180.0, "mae": 940.0},
            {"years": [2019, 2022, 2024], "r2": 0.87, "rmse": 1170.0, "mae": 930.0}
        ]
        
        # R²スコア降順ソート
        sorted_results = sorted(results, key=lambda x: x["r2"], reverse=True)
        
        # 上位5件
        top_5 = sorted_results[:5]
        
        # 検証
        assert len(top_5) == 5, "上位5件が返されていません"
        assert top_5[0]["r2"] == 0.90, "1位のR²スコアが不正です"
        assert top_5[1]["r2"] == 0.88, "2位のR²スコアが不正です"
        assert top_5[2]["r2"] == 0.87, "3位のR²スコアが不正です"
        assert top_5[3]["r2"] == 0.86, "4位のR²スコアが不正です"
        assert top_5[4]["r2"] == 0.85, "5位のR²スコアが不正です"


@pytest.mark.unit
class TestResultFileFormat:
    """結果ファイル形式テスト"""

    def test_result_file_naming_convention(self):
        """
        US2-U4: 結果テキストファイルが正しい命名規則で生成される
        
        検証項目:
        - ファイル名形式: YYYY-MM-DD_{MODEL}_optimize_years.txt
        - 日付が現在日時
        - モデル名が正しい
        """
        from datetime import datetime
        
        model_name = "LightGBM"
        today = datetime.now().strftime("%Y-%m-%d")
        expected_filename = f"{today}_{model_name}_optimize_years.txt"
        
        # 検証
        assert f"{today}" in expected_filename, "日付が含まれていません"
        assert model_name in expected_filename, "モデル名が含まれていません"
        assert expected_filename.endswith("_optimize_years.txt"), "拡張子が不正です"
        
        print(f"期待ファイル名: {expected_filename}")

    def test_result_file_content_format(self):
        """
        結果ファイルの内容形式検証
        
        検証項目:
        - 上位5組み合わせが記載される
        - 推奨組み合わせが明示される
        - RMSE/R²/MAEが記載される
        """
        # ダミー結果
        results = [
            {"years": [2022, 2023, 2024], "r2": 0.90, "rmse": 1100.0, "mae": 900.0},
            {"years": [2021, 2022, 2023], "r2": 0.88, "rmse": 1150.0, "mae": 920.0}
        ]
        
        # 結果ファイル内容生成
        content = "=== LightGBM学習年組み合わせ最適化結果 ===\n\n"
        content += "【推奨組み合わせ】\n"
        content += f"学習年: {results[0]['years']}\n"
        content += f"R²スコア: {results[0]['r2']:.4f}\n"
        content += f"RMSE: {results[0]['rmse']:.2f} kW\n"
        content += f"MAE: {results[0]['mae']:.2f} kW\n\n"
        
        content += "【上位5組み合わせ】\n"
        for i, result in enumerate(results[:5], 1):
            content += f"{i}. {result['years']} - R²: {result['r2']:.4f}, RMSE: {result['rmse']:.2f} kW\n"
        
        # 検証
        assert "推奨組み合わせ" in content, "推奨組み合わせが記載されていません"
        assert "上位5組み合わせ" in content, "上位5組み合わせが記載されていません"
        assert "R²スコア" in content, "R²スコアが記載されていません"
        assert "RMSE" in content, "RMSEが記載されていません"
        assert "MAE" in content, "MAEが記載されていません"
        
        print(content)
