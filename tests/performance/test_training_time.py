"""
パフォーマンステスト: 学習時間・API応答時間 (US1 MVP)

契約テスト要件:
- LightGBM学習時間 < 30秒
- Keras学習時間 < 60秒
- RandomForest学習時間 < 45秒
- PyCaret学習時間 < 90秒
- API /run-data レスポンスタイム < 2秒
- API /run-train レスポンスタイム < 60秒（LightGBM）

実行方法:
    pytest tests/performance/test_training_time.py -v

前提条件:
    1. HTTPサーバーが起動している（python AI/server.py）
    2. データ処理が完了している（/run-data実行済み）

依存関係:
    - pytest>=8.0.0
    - requests>=2.31.0

テストシナリオ:
    US1-P1: LightGBM学習時間 < 30秒
    US1-P2: Keras学習時間 < 60秒
    US1-P3: RandomForest学習時間 < 45秒
    US1-P4: PyCaret学習時間 < 90秒
    US1-P5: API /run-data レスポンスタイム < 2秒
    US1-P6: API /run-train レスポンスタイム < 60秒
"""

import os
import sys
import time
import subprocess
import pytest
import requests
from pathlib import Path
from typing import Tuple


# 定数
PROJECT_ROOT = Path(__file__).parent.parent.parent
AI_DIR = PROJECT_ROOT / "AI"
TRAIN_DIR = AI_DIR / "train"
API_BASE_URL = "http://localhost:8002"
RUN_DATA_ENDPOINT = f"{API_BASE_URL}/run-data"
RUN_TRAIN_ENDPOINT = f"{API_BASE_URL}/run-train"

# パフォーマンス閾値（秒）
MAX_TRAINING_TIME = {
    "LightGBM": 30.0,
    "Keras": 60.0,
    "RandomForest": 45.0,
    "Pycaret": 90.0
}
MAX_API_DATA_TIME = 2.0
MAX_API_TRAIN_TIME = 60.0


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
    start_time = time.time()
    result = subprocess.run(
        [sys.executable, str(data_script)],
        cwd=str(AI_DIR),
        capture_output=True,
        text=True,
        timeout=30
    )
    elapsed_time = time.time() - start_time
    
    if result.returncode != 0:
        pytest.fail(f"データ処理に失敗しました: {result.stderr}")
    
    print(f"データ処理時間: {elapsed_time:.2f}秒")
    
    # X.csv、Y.csv生成確認
    x_csv = AI_DIR / "data" / "X.csv"
    y_csv = AI_DIR / "data" / "Y.csv"
    
    assert x_csv.exists(), "X.csvが生成されていません"
    assert y_csv.exists(), "Y.csvが生成されていません"


@pytest.fixture(scope="module")
def verify_server_running():
    """
    HTTPサーバー起動確認フィクスチャ
    
    前提条件:
        python AI/server.py でサーバーが起動している
    """
    try:
        response = requests.get(API_BASE_URL, timeout=5)
        # サーバーが起動していればOK
    except requests.exceptions.RequestException as e:
        pytest.skip(f"HTTPサーバーが起動していません: {e}")


@pytest.mark.performance
class TestModelTrainingTime:
    """モデル学習時間パフォーマンステスト"""

    @pytest.mark.parametrize("model_name,max_time", [
        ("LightGBM", MAX_TRAINING_TIME["LightGBM"]),
        ("Keras", MAX_TRAINING_TIME["Keras"]),
        ("RandomForest", MAX_TRAINING_TIME["RandomForest"]),
        ("Pycaret", MAX_TRAINING_TIME["Pycaret"])
    ])
    def test_training_time_threshold(self, setup_data, model_name: str, max_time: float):
        """
        US1-P1〜P4: モデル学習時間閾値テスト
        
        検証項目:
        - 学習時間が閾値以内
        - 学習が正常完了する
        
        Args:
            model_name: モデル名（LightGBM、Keras等）
            max_time: 最大許容時間（秒）
        """
        train_script = TRAIN_DIR / model_name / f"{model_name}_train.py"
        
        if not train_script.exists():
            pytest.skip(f"学習スクリプトが見つかりません: {train_script}")
        
        # 学習実行（時間計測）
        start_time = time.time()
        result = subprocess.run(
            [sys.executable, str(train_script)],
            cwd=str(TRAIN_DIR / model_name),
            capture_output=True,
            text=True,
            timeout=max_time + 30  # タイムアウトは閾値+30秒
        )
        elapsed_time = time.time() - start_time
        
        # 学習成功確認
        assert result.returncode == 0, f"{model_name}学習に失敗しました: {result.stderr}"
        
        # 学習時間閾値検証
        assert elapsed_time <= max_time, (
            f"{model_name}学習時間が閾値超過\n"
            f"  実測値: {elapsed_time:.2f}秒\n"
            f"  閾値: {max_time}秒\n"
            f"  超過時間: {elapsed_time - max_time:.2f}秒\n"
            f"  → ハイパーパラメータまたはデータサイズの見直しを推奨"
        )
        
        print(f"{model_name}学習時間: {elapsed_time:.2f}秒 / {max_time}秒")


@pytest.mark.performance
class TestAPIResponseTime:
    """API応答時間パフォーマンステスト"""

    def test_run_data_response_time(self, verify_server_running):
        """
        US1-P5: /run-data API応答時間 < 2秒
        
        検証項目:
        - レスポンスタイムが2秒以内
        - API呼び出しが正常完了する
        """
        payload = {"years": [2022, 2023, 2024]}
        
        # API呼び出し（時間計測）
        start_time = time.time()
        response = requests.post(RUN_DATA_ENDPOINT, json=payload, timeout=30)
        elapsed_time = time.time() - start_time
        
        # API成功確認
        assert response.status_code == 200, f"/run-data APIが失敗: {response.status_code}"
        
        # 応答時間閾値検証
        assert elapsed_time <= MAX_API_DATA_TIME, (
            f"/run-data API応答時間が閾値超過\n"
            f"  実測値: {elapsed_time:.2f}秒\n"
            f"  閾値: {MAX_API_DATA_TIME}秒\n"
            f"  超過時間: {elapsed_time - MAX_API_DATA_TIME:.2f}秒\n"
            f"  → データ処理ロジックの最適化を推奨"
        )
        
        print(f"/run-data API応答時間: {elapsed_time:.2f}秒 / {MAX_API_DATA_TIME}秒")

    @pytest.mark.slow
    def test_run_train_response_time(self, verify_server_running):
        """
        US1-P6: /run-train API応答時間 < 60秒（LightGBM）
        
        検証項目:
        - レスポンスタイムが60秒以内（LightGBM）
        - API呼び出しが正常完了する
        - メトリクスが返却される
        """
        # データ処理実行
        data_payload = {"years": [2022, 2023, 2024]}
        data_response = requests.post(RUN_DATA_ENDPOINT, json=data_payload, timeout=30)
        assert data_response.status_code == 200, "データ処理に失敗しました"
        
        # 学習実行（時間計測）
        train_payload = {"model": "LightGBM"}
        start_time = time.time()
        response = requests.post(RUN_TRAIN_ENDPOINT, json=train_payload, timeout=90)
        elapsed_time = time.time() - start_time
        
        # API成功確認
        assert response.status_code == 200, f"/run-train APIが失敗: {response.status_code}"
        
        # 応答時間閾値検証
        assert elapsed_time <= MAX_API_TRAIN_TIME, (
            f"/run-train API応答時間が閾値超過\n"
            f"  実測値: {elapsed_time:.2f}秒\n"
            f"  閾値: {MAX_API_TRAIN_TIME}秒\n"
            f"  超過時間: {elapsed_time - MAX_API_TRAIN_TIME:.2f}秒\n"
            f"  → 学習アルゴリズムまたはハイパーパラメータの最適化を推奨"
        )
        
        # メトリクス検証
        data = response.json()
        assert "rmse" in data, "レスポンスにrmseが含まれていません"
        assert "r2" in data, "レスポンスにr2が含まれていません"
        assert "mae" in data, "レスポンスにmaeが含まれていません"
        
        print(f"/run-train API応答時間: {elapsed_time:.2f}秒 / {MAX_API_TRAIN_TIME}秒")


@pytest.mark.performance
@pytest.mark.integration
class TestEndToEndPerformance:
    """エンドツーエンドパフォーマンステスト"""

    @pytest.mark.slow
    def test_full_workflow_performance(self, verify_server_running):
        """
        完全ワークフローパフォーマンステスト
        
        シナリオ:
        1. データ処理（< 2秒）
        2. LightGBM学習（< 60秒）
        3. 合計時間 < 65秒
        
        検証項目:
        - 合計実行時間が閾値以内
        - 各ステップが正常完了する
        """
        total_max_time = MAX_API_DATA_TIME + MAX_API_TRAIN_TIME + 3.0  # バッファ3秒
        
        # 1. データ処理
        data_payload = {"years": [2022, 2023, 2024]}
        start_time = time.time()
        
        data_response = requests.post(RUN_DATA_ENDPOINT, json=data_payload, timeout=30)
        data_time = time.time() - start_time
        
        assert data_response.status_code == 200, "データ処理に失敗しました"
        print(f"データ処理時間: {data_time:.2f}秒")
        
        # 2. 学習
        train_payload = {"model": "LightGBM"}
        train_start_time = time.time()
        
        train_response = requests.post(RUN_TRAIN_ENDPOINT, json=train_payload, timeout=90)
        train_time = time.time() - train_start_time
        
        assert train_response.status_code == 200, "学習に失敗しました"
        print(f"学習時間: {train_time:.2f}秒")
        
        # 3. 合計時間検証
        total_time = time.time() - start_time
        
        assert total_time <= total_max_time, (
            f"完全ワークフロー実行時間が閾値超過\n"
            f"  実測値: {total_time:.2f}秒\n"
            f"  閾値: {total_max_time}秒\n"
            f"  内訳: データ処理 {data_time:.2f}秒 + 学習 {train_time:.2f}秒\n"
            f"  → パイプライン全体の最適化を推奨"
        )
        
        print(f"完全ワークフロー時間: {total_time:.2f}秒 / {total_max_time}秒")


@pytest.mark.performance
class TestMemoryUsage:
    """メモリ使用量パフォーマンステスト（オプション）"""

    @pytest.mark.parametrize("model_name", ["LightGBM", "Keras", "RandomForest", "Pycaret"])
    def test_memory_consumption(self, setup_data, model_name: str):
        """
        メモリ使用量テスト（オプション）
        
        検証項目:
        - 学習中のメモリ使用量が妥当な範囲
        - メモリリークが発生していない
        
        Note:
            このテストはpsutilが必要です
            pip install psutil
        """
        try:
            import psutil
        except ImportError:
            pytest.skip("psutilがインストールされていません")
        
        train_script = TRAIN_DIR / model_name / f"{model_name}_train.py"
        
        if not train_script.exists():
            pytest.skip(f"学習スクリプトが見つかりません: {train_script}")
        
        # プロセス起動
        process = subprocess.Popen(
            [sys.executable, str(train_script)],
            cwd=str(TRAIN_DIR / model_name),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # メモリ使用量監視
        max_memory_mb = 0.0
        
        try:
            psutil_process = psutil.Process(process.pid)
            
            while process.poll() is None:
                try:
                    memory_info = psutil_process.memory_info()
                    memory_mb = memory_info.rss / 1024 / 1024  # MB
                    max_memory_mb = max(max_memory_mb, memory_mb)
                    time.sleep(0.1)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    break
            
            # プロセス完了待機
            stdout, stderr = process.communicate(timeout=120)
            
            # 学習成功確認
            assert process.returncode == 0, f"{model_name}学習に失敗しました: {stderr.decode()}"
            
            # メモリ使用量出力
            print(f"{model_name}最大メモリ使用量: {max_memory_mb:.2f} MB")
            
            # メモリ閾値検証（4GB以下を推奨）
            MAX_MEMORY_MB = 4096.0
            if max_memory_mb > MAX_MEMORY_MB:
                pytest.warn(
                    f"{model_name}メモリ使用量が推奨値を超過: {max_memory_mb:.2f} MB > {MAX_MEMORY_MB} MB"
                )
        
        finally:
            # プロセスクリーンアップ
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
