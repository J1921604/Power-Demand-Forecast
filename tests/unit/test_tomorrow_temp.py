# -*- coding: utf-8 -*-
"""Unit tests for `AI/tomorrow/temp.py`.

目的:
- tomorrow 用特徴量CSV (`tomorrow/tomorrow.csv`) の列順が学習時と一致していることを保証する。
- 必須特徴量が欠けた場合に早期に検知できることを保証する。

注意:
- Open-Meteo API など外部ネットワークにはアクセスしない。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

# Import module under test
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "AI"))
from tomorrow import temp as temp_module  # type: ignore


def test_save_temperature_csv_orders_columns(tmp_path: Path):
    """保存されるCSVが `MONTH,WEEK,HOUR,TEMP` の順であること。"""

    df = pd.DataFrame(
        {
            # 現実の生成順に近い並び（TEMP が先頭に来がち）をあえて作る
            "time": pd.date_range("2026-01-07 00:00:00", periods=3, freq="h"),
            "TEMP": [10.0, 11.0, 12.0],
            "MONTH": [1, 1, 1],
            "WEEK": [2, 2, 2],
            "HOUR": [0, 1, 2],
        }
    )

    out_csv = tmp_path / "tomorrow.csv"
    temp_module.save_temperature_csv(df, str(out_csv), period_info_path=None)

    saved = pd.read_csv(out_csv)
    assert list(saved.columns) == ["MONTH", "WEEK", "HOUR", "TEMP"]


def test_save_temperature_csv_missing_required_columns_raises(tmp_path: Path):
    """必須特徴量が不足している場合は例外となること。"""

    df = pd.DataFrame(
        {
            "time": pd.date_range("2026-01-07 00:00:00", periods=3, freq="h"),
            "TEMP": [10.0, 11.0, 12.0],
            "MONTH": [1, 1, 1],
            # WEEK/HOUR が不足
        }
    )

    out_csv = tmp_path / "tomorrow.csv"
    with pytest.raises(ValueError, match="必須カラムが不足"):
        temp_module.save_temperature_csv(df, str(out_csv), period_info_path=None)
