# -*- coding: utf-8 -*-
"""
Unit Tests for data.py module
"""

import os
import sys
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import module under test
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "AI"))
from data import data as data_module


class TestCSVValidation:
    """CSVバリデーション関数のテスト"""
    
    def test_validate_csv_success(self, sample_power_csv):
        """正常なCSVファイルの検証成功"""
        result = data_module.validate_csv_file(
            str(sample_power_csv),
            required_columns=["DATE", "TIME", "KW"],
            skiprows=3,
            encoding='shift_jis'
        )
        assert result is True
    
    def test_validate_csv_file_not_found(self, temp_dir):
        """存在しないファイルでFileNotFoundError発生"""
        with pytest.raises(FileNotFoundError, match="CSVファイルが見つかりません"):
            data_module.validate_csv_file(
                str(temp_dir / "nonexistent.csv"),
                required_columns=["DATE"],
                skiprows=0,
                encoding='utf-8'
            )
    
    def test_validate_csv_empty_file(self, temp_dir):
        """空ファイルでValueError発生"""
        empty_file = temp_dir / "empty.csv"
        empty_file.write_text("", encoding='utf-8')
        
        with pytest.raises(ValueError, match="CSVファイルが空です"):
            data_module.validate_csv_file(
                str(empty_file),
                required_columns=["DATE"],
                skiprows=0,
                encoding='utf-8'
            )
    
    def test_validate_csv_column_mismatch(self, temp_dir):
        """カラム数不足でValueError発生"""
        csv_file = temp_dir / "short.csv"
        csv_file.write_text("col1,col2\n1,2\n", encoding='utf-8')
        
        with pytest.raises(ValueError, match="カラム数不足"):
            data_module.validate_csv_file(
                str(csv_file),
                required_columns=["col1", "col2", "col3", "col4"],
                skiprows=0,
                encoding='utf-8'
            )


class TestAITargetYears:
    """AI_TARGET_YEARS環境変数のテスト"""
    
    def test_env_years_simple(self, mock_env_target_years):
        """AI_TARGET_YEARS環境変数が設定されることを確認"""
        mock_env_target_years("2022,2024")
        assert os.environ.get('AI_TARGET_YEARS') == "2022,2024"
    
    def test_env_years_unset(self, monkeypatch):
        """AI_TARGET_YEARS環境変数が未設定の場合"""
        monkeypatch.delenv('AI_TARGET_YEARS', raising=False)
        assert os.environ.get('AI_TARGET_YEARS') is None


class TestFloat32Conversion:
    """float32型変換のテスト"""
    
    def test_kw_int32_conversion(self):
        """KWカラムがint32に変換される"""
        # サンプルデータ作成
        data = {'KW': [2500, 2400, 2300, 2200]}
        df = pd.DataFrame(data)
        
        # int32変換
        df['KW'] = df['KW'].astype('int32')
        
        assert df['KW'].dtype == np.int32
        assert df['KW'].memory_usage(deep=True) < df['KW'].astype('int64').memory_usage(deep=True)
    
    def test_temp_float32_conversion(self):
        """気温データがfloat32に変換される"""
        # サンプルデータ作成
        data = {'TEMP': [15.5, 16.2, 14.8, 13.5]}
        df = pd.DataFrame(data)
        
        # float32変換
        df['TEMP'] = df['TEMP'].astype('float32')
        
        assert df['TEMP'].dtype == np.float32
        assert df['TEMP'].memory_usage(deep=True) < df['TEMP'].astype('float64').memory_usage(deep=True)


class TestDataIntegration:
    """データ統合のテスト"""
    
    def test_common_years_extraction(self):
        """共通年抽出のテスト"""
        power_files = [
            "data/juyo-2022.csv",
            "data/juyo-2023.csv",
            "data/juyo-2024.csv"
        ]
        temp_files = [
            "data/temperature-2022.csv",
            "data/temperature-2024.csv"
        ]
        
        common_years, power_map, temp_map = data_module.get_common_years(power_files, temp_files)
        
        assert set(common_years) == {"2022", "2024"}
        assert "2023" not in common_years
    
    def test_no_common_years_error(self):
        """共通年が存在しない場合のエラー"""
        power_files = ["data/juyo-2022.csv"]
        temp_files = ["data/temperature-2024.csv"]
        
        with pytest.raises(ValueError, match="共通年が見つかりません"):
            data_module.get_common_years(power_files, temp_files)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
