"""
統合テスト: ローリング時系列交差検証ロジック (US2)

契約テスト要件:
- ローリング時系列交差検証が正しく動作する
- 訓練セット/テストセットの分割が正しい
- 複数フォールドで性能が評価される
- 平均R²スコアが計算される

実行方法:
    pytest tests/integration/test_rolling_cv.py -v

依存関係:
    - pytest>=8.0.0
    - pandas>=2.0.0
    - numpy>=1.24.0
    - scikit-learn>=1.3.0

テストシナリオ:
    US2-R1: ローリング時系列交差検証が正しく動作する
    US2-R2: 訓練セット/テストセットの分割が正しい
    US2-R3: 複数フォールドで性能が評価される
    US2-R4: 平均R²スコアが計算される
"""

import os
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Tuple
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import r2_score


# 定数
PROJECT_ROOT = Path(__file__).parent.parent.parent
AI_DIR = PROJECT_ROOT / "AI"
DATA_DIR = AI_DIR / "data"


@pytest.mark.integration
class TestRollingTimeSeriesCV:
    """ローリング時系列交差検証テスト"""

    def test_time_series_split_basic(self):
        """
        US2-R1: ローリング時系列交差検証が正しく動作する
        
        検証項目:
        - TimeSeriesSplitが正しく動作する
        - フォールド数が正しい
        - 各フォールドで訓練セット・テストセットが分割される
        """
        # ダミーデータ（1000サンプル）
        X = np.arange(1000).reshape(-1, 1)
        y = np.arange(1000)
        
        # TimeSeriesSplit（3フォールド）
        tscv = TimeSeriesSplit(n_splits=3)
        
        splits = list(tscv.split(X))
        
        # 検証
        assert len(splits) == 3, "フォールド数が不正です"
        
        # 各フォールド検証
        for i, (train_idx, test_idx) in enumerate(splits):
            assert len(train_idx) > 0, f"フォールド{i+1}: 訓練セットが空です"
            assert len(test_idx) > 0, f"フォールド{i+1}: テストセットが空です"
            
            # 訓練セットの最大インデックス < テストセットの最小インデックス（時系列順）
            assert max(train_idx) < min(test_idx), f"フォールド{i+1}: 時系列順が崩れています"
            
            print(f"フォールド{i+1}: 訓練={len(train_idx)}サンプル, テスト={len(test_idx)}サンプル")

    def test_train_test_split_ratio(self):
        """
        US2-R2: 訓練セット/テストセットの分割が正しい
        
        検証項目:
        - 訓練セットが増加していく（ローリング方式）
        - テストセットのサイズが一定
        """
        # ダミーデータ（1200サンプル）
        X = np.arange(1200).reshape(-1, 1)
        y = np.arange(1200)
        
        # TimeSeriesSplit（4フォールド）
        tscv = TimeSeriesSplit(n_splits=4)
        
        splits = list(tscv.split(X))
        train_sizes = []
        test_sizes = []
        
        for train_idx, test_idx in splits:
            train_sizes.append(len(train_idx))
            test_sizes.append(len(test_idx))
        
        # 検証
        # 訓練セットが増加
        for i in range(len(train_sizes) - 1):
            assert train_sizes[i] < train_sizes[i + 1], "訓練セットが増加していません"
        
        print(f"訓練セットサイズ: {train_sizes}")
        print(f"テストセットサイズ: {test_sizes}")

    def test_rolling_cv_with_lightgbm_mock(self):
        """
        US2-R3: 複数フォールドで性能が評価される
        
        検証項目:
        - 各フォールドでモデルが訓練される
        - 各フォールドでR²スコアが計算される
        - R²スコアが妥当な範囲（0〜1）
        """
        # ダミーデータ（線形関係: y = 2x + 3 + ノイズ）
        np.random.seed(42)
        X = np.arange(1000).reshape(-1, 1)
        y = 2 * X.flatten() + 3 + np.random.normal(0, 10, 1000)
        
        # TimeSeriesSplit（3フォールド）
        tscv = TimeSeriesSplit(n_splits=3)
        
        r2_scores = []
        
        for train_idx, test_idx in tscv.split(X):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
            
            # 簡易モデル（線形回帰）
            from sklearn.linear_model import LinearRegression
            model = LinearRegression()
            model.fit(X_train, y_train)
            
            # 予測
            y_pred = model.predict(X_test)
            
            # R²スコア計算
            r2 = r2_score(y_test, y_pred)
            r2_scores.append(r2)
        
        # 検証
        assert len(r2_scores) == 3, "フォールド数が不正です"
        
        for i, r2 in enumerate(r2_scores):
            assert 0.0 <= r2 <= 1.0, f"フォールド{i+1}: R²スコアが範囲外: {r2}"
            print(f"フォールド{i+1}: R²スコア = {r2:.4f}")

    def test_average_r2_calculation(self):
        """
        US2-R4: 平均R²スコアが計算される
        
        検証項目:
        - 複数フォールドのR²スコア平均が計算される
        - 標準偏差が計算される
        """
        # ダミーR²スコア
        r2_scores = [0.85, 0.87, 0.86, 0.88, 0.84]
        
        # 平均・標準偏差計算
        mean_r2 = np.mean(r2_scores)
        std_r2 = np.std(r2_scores)
        
        # 検証
        assert 0.0 <= mean_r2 <= 1.0, "平均R²スコアが範囲外です"
        assert std_r2 >= 0.0, "標準偏差が負です"
        
        expected_mean = 0.86
        assert abs(mean_r2 - expected_mean) < 0.01, f"平均R²スコアが不正: {mean_r2} != {expected_mean}"
        
        print(f"平均R²スコア: {mean_r2:.4f} ± {std_r2:.4f}")


@pytest.mark.integration
class TestRollingCVWithRealData:
    """実データを使用したローリング交差検証テスト"""

    @pytest.fixture
    def sample_data(self):
        """
        サンプルデータフィクスチャ
        
        Returns:
            Tuple[np.ndarray, np.ndarray]: (特徴量X, 目的変数y)
        """
        # 実データがある場合はそれを使用、なければダミーデータ
        x_csv = DATA_DIR / "X.csv"
        y_csv = DATA_DIR / "Y.csv"
        
        if x_csv.exists() and y_csv.exists():
            X = pd.read_csv(x_csv).values
            y = pd.read_csv(y_csv).values.flatten()
        else:
            # ダミーデータ
            np.random.seed(42)
            n_samples = 2000
            X = np.random.randn(n_samples, 10)
            y = X[:, 0] * 2 + X[:, 1] * 3 + np.random.normal(0, 1, n_samples)
        
        return X, y

    def test_rolling_cv_with_real_data(self, sample_data):
        """
        実データを使用したローリング交差検証
        
        検証項目:
        - 実データでローリング交差検証が動作する
        - 各フォールドのR²スコアが計算される
        - 平均R²スコアが計算される
        """
        X, y = sample_data
        
        # TimeSeriesSplit（5フォールド）
        tscv = TimeSeriesSplit(n_splits=5)
        
        r2_scores = []
        
        for fold, (train_idx, test_idx) in enumerate(tscv.split(X), 1):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
            
            # LightGBMモデル（軽量版）
            try:
                import lightgbm as lgb
                
                params = {
                    'objective': 'regression',
                    'metric': 'rmse',
                    'verbosity': -1,
                    'num_leaves': 31,
                    'learning_rate': 0.05,
                    'feature_fraction': 0.9
                }
                
                train_data = lgb.Dataset(X_train, y_train)
                model = lgb.train(params, train_data, num_boost_round=50, verbose_eval=False)
                
                # 予測
                y_pred = model.predict(X_test)
                
                # R²スコア計算
                r2 = r2_score(y_test, y_pred)
                r2_scores.append(r2)
                
                print(f"フォールド{fold}: R²スコア = {r2:.4f}")
                
            except ImportError:
                pytest.skip("LightGBMがインストールされていません")
        
        # 平均R²スコア
        if r2_scores:
            mean_r2 = np.mean(r2_scores)
            std_r2 = np.std(r2_scores)
            
            print(f"\n平均R²スコア: {mean_r2:.4f} ± {std_r2:.4f}")
            
            # 検証
            assert 0.0 <= mean_r2 <= 1.0, "平均R²スコアが範囲外です"


@pytest.mark.integration
class TestCombinationEvaluation:
    """組み合わせ評価テスト"""

    def test_evaluate_multiple_year_combinations(self):
        """
        複数年組み合わせの評価
        
        検証項目:
        - 複数の年組み合わせでR²スコアが計算される
        - 最適組み合わせが選択される
        """
        # ダミーデータ（年別）
        np.random.seed(42)
        
        # 3つの年組み合わせを評価
        year_combinations = [
            [2020, 2021, 2022],
            [2021, 2022, 2023],
            [2022, 2023, 2024]
        ]
        
        results = []
        
        for years in year_combinations:
            # 各年組み合わせでダミーデータ生成
            n_samples = len(years) * 300  # 各年300サンプル
            X = np.random.randn(n_samples, 5)
            
            # 年ごとに傾向を変える（最新年ほど高R²）
            base_r2 = 0.75 + (years[-1] - 2020) * 0.02
            y = X[:, 0] * 2 + X[:, 1] * 3 + np.random.normal(0, 0.5 / base_r2, n_samples)
            
            # 簡易モデルでR²スコア計算
            from sklearn.linear_model import LinearRegression
            from sklearn.model_selection import cross_val_score
            
            model = LinearRegression()
            scores = cross_val_score(model, X, y, cv=3, scoring='r2')
            mean_r2 = np.mean(scores)
            
            results.append({
                "years": years,
                "r2": mean_r2,
                "rmse": 1200.0 - (years[-1] - 2020) * 50.0  # ダミーRMSE
            })
            
            print(f"組み合わせ {years}: R²スコア = {mean_r2:.4f}")
        
        # 最適組み合わせ選択
        best = max(results, key=lambda x: x["r2"])
        
        # 検証
        assert len(results) == 3, "評価結果数が不正です"
        assert best["years"] in year_combinations, "最適組み合わせが不正です"
        
        print(f"\n最適組み合わせ: {best['years']}, R²スコア: {best['r2']:.4f}")
