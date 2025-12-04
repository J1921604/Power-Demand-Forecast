"""
統合テスト: R²スコア閾値テスト (US1 MVP)

契約テスト要件:
- 全モデル（LightGBM、Keras、RandomForest、PyCaret）でR² >= 0.80
- 学習完了後にメトリクスファイルが生成される
- メトリクスファイルにrmse、r2、maeが記録される
- 閾値未達の場合は警告が出力される

実行方法:
    pytest tests/integration/test_metrics.py -v

前提条件:
    1. HTTPサーバーが起動している（python AI/server.py）
    2. データ処理が完了している（/run-data実行済み）

依存関係:
    - pytest>=8.0.0
    - pandas>=2.0.0
    - numpy>=1.24.0

テストシナリオ:
    US1-M1: LightGBM R²スコア >= 0.80
    US1-M2: Keras R²スコア >= 0.80
    US1-M3: RandomForest R²スコア >= 0.80
    US1-M4: PyCaret R²スコア >= 0.80
    US1-M5: メトリクスファイルが生成される
"""

import os
import sys
import subprocess
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple


# 定数
PROJECT_ROOT = Path(__file__).parent.parent.parent
AI_DIR = PROJECT_ROOT / "AI"
TRAIN_DIR = AI_DIR / "train"
MIN_R2_SCORE = 0.80
VALID_MODELS = ["LightGBM", "Keras", "RandomForest", "Pycaret"]


@pytest.fixture(scope="module")
def setup_data():
    """
    データ処理実行フィクスチャ
    
    前提条件:
        AI/data/data.py が実行可能
    """
    data_script = AI_DIR / "data" / "data.py"
    
    if not data_script.exists():
        pytest.skip(f"データ処理スクリプトが見つかりません: {data_script}")
    
    # データ処理実行
    result = subprocess.run(
        [sys.executable, str(data_script)],
        cwd=str(AI_DIR),
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode != 0:
        pytest.fail(f"データ処理に失敗しました: {result.stderr}")
    
    # X.csv、Y.csv生成確認
    x_csv = AI_DIR / "data" / "X.csv"
    y_csv = AI_DIR / "data" / "Y.csv"
    
    assert x_csv.exists(), "X.csvが生成されていません"
    assert y_csv.exists(), "Y.csvが生成されていません"


@pytest.fixture(scope="module", params=VALID_MODELS)
def train_model(request, setup_data) -> Tuple[str, Dict[str, float]]:
    """
    モデル学習実行フィクスチャ
    
    Returns:
        Tuple[str, Dict[str, float]]: (モデル名, メトリクス辞書)
    
    Note:
        各モデルを学習し、標準出力からメトリクスを抽出
    """
    model_name = request.param
    train_script = TRAIN_DIR / model_name / f"{model_name}_train.py"
    
    if not train_script.exists():
        pytest.skip(f"学習スクリプトが見つかりません: {train_script}")
    
    # 学習実行
    result = subprocess.run(
        [sys.executable, str(train_script)],
        cwd=str(TRAIN_DIR / model_name),
        capture_output=True,
        text=True,
        timeout=120  # Keras対応で120秒
    )
    
    if result.returncode != 0:
        pytest.fail(f"{model_name}学習に失敗しました: {result.stderr}")
    
    # 標準出力からメトリクス抽出
    output = result.stdout
    metrics = _extract_metrics_from_output(output)
    
    return model_name, metrics


def _extract_metrics_from_output(output: str) -> Dict[str, float]:
    """
    標準出力からメトリクス抽出
    
    期待フォーマット:
        最終結果 - RMSE: 1234.56 kW, R2スコア: 0.8523, MAE: 987.65 kW
        または
        最終結果 - RMSE: 1234.56 kW, R2: 0.8523, MAE: 987.65 kW
    
    Args:
        output: 標準出力文字列
    
    Returns:
        Dict[str, float]: {"rmse": 1234.56, "r2": 0.8523, "mae": 987.65}
    """
    import re
    
    # 正規表現でメトリクス抽出
    rmse_match = re.search(r"RMSE[:\s]+([\d.]+)", output)
    r2_match = re.search(r"R[2²][:\s]*([:\s]+)?([\d.]+)", output)
    mae_match = re.search(r"MAE[:\s]+([\d.]+)", output)
    
    if not all([rmse_match, r2_match, mae_match]):
        # フォールバック: CSVファイルから読み込み
        return {}
    
    rmse = float(rmse_match.group(1))
    # R²スコアは正規表現グループ2または3に数値が入る
    r2_str = r2_match.group(2) if r2_match.group(2) and r2_match.group(2).replace('.', '').isdigit() else r2_match.group(3) if len(r2_match.groups()) > 2 else r2_match.group(1)
    r2 = float(r2_str)
    mae = float(mae_match.group(1))
    
    return {"rmse": rmse, "r2": r2, "mae": mae}


@pytest.mark.integration
class TestMetricsThreshold:
    """R²スコア閾値テスト（US1 MVP）"""

    def test_r2_score_threshold(self, train_model):
        """
        US1-M1〜M4: 全モデルでR² >= 0.80
        
        検証項目:
        - R²スコアが0.80以上
        - RMSEが正の数値
        - MAEが正の数値
        """
        model_name, metrics = train_model
        
        # メトリクス抽出失敗時はCSVから読み込み
        if not metrics:
            metrics = _extract_metrics_from_csv(model_name)
        
        # メトリクス検証
        assert "rmse" in metrics, f"{model_name}: RMSEが取得できません"
        assert "r2" in metrics, f"{model_name}: R²スコアが取得できません"
        assert "mae" in metrics, f"{model_name}: MAEが取得できません"
        
        rmse = metrics["rmse"]
        r2 = metrics["r2"]
        mae = metrics["mae"]
        
        # 数値検証
        assert rmse > 0, f"{model_name}: RMSEが0以下: {rmse}"
        assert mae > 0, f"{model_name}: MAEが0以下: {mae}"
        
        # R²スコア閾値検証（US1要件）
        assert r2 >= MIN_R2_SCORE, (
            f"{model_name}: R²スコアが閾値未満\n"
            f"  実測値: {r2:.4f}\n"
            f"  閾値: {MIN_R2_SCORE}\n"
            f"  差分: {r2 - MIN_R2_SCORE:.4f}\n"
            f"  → データ品質またはハイパーパラメータの見直しを推奨"
        )


def _extract_metrics_from_csv(model_name: str) -> Dict[str, float]:
    """
    CSVファイルからメトリクス抽出（フォールバック）
    
    Args:
        model_name: モデル名（LightGBM、Keras等）
    
    Returns:
        Dict[str, float]: メトリクス辞書
    """
    # 予測結果CSVから逆算
    ypred_csv = TRAIN_DIR / model_name / f"{model_name}_Ypred.csv"
    
    if not ypred_csv.exists():
        pytest.fail(f"{model_name}_Ypred.csvが見つかりません")
    
    # Ytest.csv読み込み
    ytest_csv = AI_DIR / "data" / "Ytest.csv"
    if not ytest_csv.exists():
        pytest.fail("Ytest.csvが見つかりません")
    
    y_pred = pd.read_csv(ypred_csv).values.flatten()
    y_test_full = pd.read_csv(ytest_csv).values.flatten()
    
    # 予測結果の長さに合わせてy_testを切り出す（時系列データなので末尾を使用）
    y_test = y_test_full[-len(y_pred):]
    
    # メトリクス計算
    from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
    
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    
    return {"rmse": rmse, "r2": r2, "mae": mae}


@pytest.mark.integration
class TestMetricsFiles:
    """メトリクスファイル生成テスト"""

    @pytest.mark.parametrize("model_name", VALID_MODELS)
    def test_ypred_csv_generated(self, setup_data, model_name: str):
        """
        US1-M5: メトリクスファイルが生成される
        
        検証項目:
        - {MODEL}_Ypred.csvが生成される
        - CSVに予測値が記録される
        - 予測値が数値形式
        """
        # 学習実行
        train_script = TRAIN_DIR / model_name / f"{model_name}_train.py"
        
        if not train_script.exists():
            pytest.skip(f"学習スクリプトが見つかりません: {train_script}")
        
        result = subprocess.run(
            [sys.executable, str(train_script)],
            cwd=str(TRAIN_DIR / model_name),
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            pytest.fail(f"{model_name}学習に失敗しました: {result.stderr}")
        
        # Ypred.csv生成確認
        ypred_csv = TRAIN_DIR / model_name / f"{model_name}_Ypred.csv"
        assert ypred_csv.exists(), f"{model_name}_Ypred.csvが生成されていません"
        
        # CSV読み込み
        df = pd.read_csv(ypred_csv)
        assert not df.empty, f"{model_name}_Ypred.csvが空です"
        
        # 数値形式検証
        assert df.select_dtypes(include=[np.number]).shape[1] > 0, "数値カラムが存在しません"

    @pytest.mark.parametrize("model_name", VALID_MODELS)
    def test_model_file_generated(self, setup_data, model_name: str):
        """
        US1-M6: 学習済みモデルファイルが生成される
        
        検証項目:
        - LightGBM/RandomForest/PyCaret: {MODEL}_model.sav
        - Keras: Keras_model.h5
        """
        # 学習実行
        train_script = TRAIN_DIR / model_name / f"{model_name}_train.py"
        
        if not train_script.exists():
            pytest.skip(f"学習スクリプトが見つかりません: {train_script}")
        
        result = subprocess.run(
            [sys.executable, str(train_script)],
            cwd=str(TRAIN_DIR / model_name),
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            pytest.fail(f"{model_name}学習に失敗しました: {result.stderr}")
        
        # モデルファイル生成確認
        if model_name == "Keras":
            model_file = TRAIN_DIR / model_name / "Keras_model.h5"
        elif model_name == "Pycaret":
            model_file = TRAIN_DIR / model_name / "Pycaret_model.pkl"
        else:
            model_file = TRAIN_DIR / model_name / f"{model_name}_model.sav"
        
        assert model_file.exists(), f"{model_name}モデルファイルが生成されていません: {model_file}"


@pytest.mark.integration
@pytest.mark.slow
class TestMetricsConsistency:
    """メトリクス一貫性テスト"""

    def test_all_models_r2_consistency(self, setup_data):
        """
        全モデルのR²スコア一貫性テスト
        
        検証項目:
        - 全モデルでR² >= 0.80を満たす
        - 全モデルのR²スコアが妥当な範囲（0.0〜1.0）
        """
        results = {}
        
        for model_name in VALID_MODELS:
            train_script = TRAIN_DIR / model_name / f"{model_name}_train.py"
            
            if not train_script.exists():
                continue
            
            # 学習実行
            result = subprocess.run(
                [sys.executable, str(train_script)],
                cwd=str(TRAIN_DIR / model_name),
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                continue
            
            # メトリクス抽出
            metrics = _extract_metrics_from_output(result.stdout)
            if not metrics:
                metrics = _extract_metrics_from_csv(model_name)
            
            results[model_name] = metrics
        
        # 全モデルのR²スコア検証
        for model_name, metrics in results.items():
            r2 = metrics["r2"]
            
            # 範囲検証
            assert 0.0 <= r2 <= 1.0, f"{model_name}: R²スコアが範囲外: {r2}"
            
            # 閾値検証
            assert r2 >= MIN_R2_SCORE, f"{model_name}: R²スコアが閾値未満: {r2:.4f} < {MIN_R2_SCORE}"
        
        # 最低1モデル以上が成功
        assert len(results) > 0, "実行可能なモデルが見つかりません"
