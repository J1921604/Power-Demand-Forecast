"""
パフォーマンステスト: 組み合わせ検証実行時間 (US2)

契約テスト要件:
- LightGBM組み合わせ検証実行時間 < 360秒（6分）
- Keras組み合わせ検証実行時間 < 600秒（10分）
- RandomForest組み合わせ検証実行時間 < 480秒（8分）
- PyCaret組み合わせ検証実行時間 < 720秒（12分）

実行方法:
    pytest tests/performance/test_optimize_time.py -v

前提条件:
    データ処理が完了している（AI/data/X.csv、Y.csv存在）

依存関係:
    - pytest>=8.0.0

テストシナリオ:
    US2-P1: LightGBM組み合わせ検証実行時間 < 360秒
    US2-P2: Keras組み合わせ検証実行時間 < 600秒
    US2-P3: RandomForest組み合わせ検証実行時間 < 480秒
    US2-P4: PyCaret組み合わせ検証実行時間 < 720秒
"""

import os
import sys
import time
import subprocess
import pytest
from pathlib import Path


# 定数
PROJECT_ROOT = Path(__file__).parent.parent.parent
AI_DIR = PROJECT_ROOT / "AI"
TRAIN_DIR = AI_DIR / "train"
DATA_DIR = AI_DIR / "data"

# パフォーマンス閾値（秒）
MAX_OPTIMIZE_TIME = {
    "LightGBM": 360.0,  # 6分
    "Keras": 600.0,     # 10分
    "RandomForest": 480.0,  # 8分
    "Pycaret": 720.0    # 12分
}


@pytest.fixture(scope="module")
def setup_data():
    """
    データ処理実行フィクスチャ
    
    前提条件:
        AI/data/data.py が実行可能
    """
    data_script = DATA_DIR / "data.py"
    
    if not data_script.exists():
        pytest.skip(f"データ処理スクリプトが見つかりません: {data_script}")
    
    # X.csv、Y.csv存在確認
    x_csv = DATA_DIR / "X.csv"
    y_csv = DATA_DIR / "Y.csv"
    
    if x_csv.exists() and y_csv.exists():
        print("データ処理済み（X.csv、Y.csv存在）")
        return
    
    # データ処理実行
    print("データ処理実行中...")
    result = subprocess.run(
        [sys.executable, str(data_script)],
        cwd=str(AI_DIR),
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode != 0:
        pytest.fail(f"データ処理に失敗しました: {result.stderr}")
    
    assert x_csv.exists(), "X.csvが生成されていません"
    assert y_csv.exists(), "Y.csvが生成されていません"


@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.skip(reason="組み合わせ検証は実行時間が長いため手動テストのみ実施")
class TestOptimizeYearsPerformance:
    """組み合わせ検証パフォーマンステスト"""

    @pytest.mark.parametrize("model_name,max_time", [
        ("LightGBM", MAX_OPTIMIZE_TIME["LightGBM"]),
        pytest.param("Keras", MAX_OPTIMIZE_TIME["Keras"], marks=pytest.mark.skip(reason="実行時間が長いためスキップ")),
        pytest.param("RandomForest", MAX_OPTIMIZE_TIME["RandomForest"], marks=pytest.mark.skip(reason="実行時間が長いためスキップ")),
        pytest.param("Pycaret", MAX_OPTIMIZE_TIME["Pycaret"], marks=pytest.mark.skip(reason="実行時間が長いためスキップ"))
    ])
    def test_optimize_time_threshold(self, setup_data, model_name: str, max_time: float):
        """
        US2-P1〜P4: 組み合わせ検証実行時間閾値テスト
        
        検証項目:
        - 組み合わせ検証実行時間が閾値以内
        - 組み合わせ検証が正常完了する
        - 結果ファイルが生成される
        
        Args:
            model_name: モデル名（LightGBM、Keras等）
            max_time: 最大許容時間（秒）
        
        Note:
            実行時間が長いため、通常はスキップされます。
            手動テストで実行する場合は@pytest.mark.skipを削除してください。
        """
        optimize_script = TRAIN_DIR / model_name / f"{model_name}_optimize_years.py"
        
        if not optimize_script.exists():
            pytest.skip(f"組み合わせ検証スクリプトが見つかりません: {optimize_script}")
        
        # 組み合わせ検証実行（時間計測）
        print(f"\n{model_name}組み合わせ検証開始...")
        start_time = time.time()
        
        result = subprocess.run(
            [sys.executable, str(optimize_script)],
            cwd=str(TRAIN_DIR / model_name),
            capture_output=True,
            text=True,
            timeout=max_time + 60  # タイムアウトは閾値+60秒
        )
        
        elapsed_time = time.time() - start_time
        
        # 組み合わせ検証成功確認
        assert result.returncode == 0, f"{model_name}組み合わせ検証に失敗しました: {result.stderr}"
        
        # 実行時間閾値検証
        assert elapsed_time <= max_time, (
            f"{model_name}組み合わせ検証時間が閾値超過\n"
            f"  実測値: {elapsed_time:.2f}秒 ({elapsed_time/60:.1f}分)\n"
            f"  閾値: {max_time}秒 ({max_time/60:.1f}分)\n"
            f"  超過時間: {elapsed_time - max_time:.2f}秒\n"
            f"  → 組み合わせ数削減またはアルゴリズム最適化を推奨"
        )
        
        print(f"{model_name}組み合わせ検証時間: {elapsed_time:.2f}秒 ({elapsed_time/60:.1f}分) / {max_time}秒 ({max_time/60:.1f}分)")
        
        # 結果ファイル生成確認
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        result_file = TRAIN_DIR / model_name / f"{today}_{model_name}_optimize_years.txt"
        
        assert result_file.exists(), f"結果ファイルが生成されていません: {result_file}"
        print(f"結果ファイル生成確認: {result_file.name}")


@pytest.mark.performance
class TestOptimizeMemoryUsage:
    """組み合わせ検証メモリ使用量テスト（オプション）"""

    @pytest.mark.skip(reason="メモリ使用量テストは手動テストのみ実施")
    def test_optimize_memory_consumption(self, setup_data):
        """
        組み合わせ検証メモリ使用量テスト
        
        検証項目:
        - 組み合わせ検証中のメモリ使用量が妥当な範囲
        - メモリリークが発生していない
        
        Note:
            このテストはpsutilが必要です
            pip install psutil
        """
        try:
            import psutil
        except ImportError:
            pytest.skip("psutilがインストールされていません")
        
        model_name = "LightGBM"
        optimize_script = TRAIN_DIR / model_name / f"{model_name}_optimize_years.py"
        
        if not optimize_script.exists():
            pytest.skip(f"組み合わせ検証スクリプトが見つかりません")
        
        # プロセス起動
        process = subprocess.Popen(
            [sys.executable, str(optimize_script)],
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
                    time.sleep(1)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    break
            
            # プロセス完了待機
            stdout, stderr = process.communicate(timeout=420)
            
            # 組み合わせ検証成功確認
            assert process.returncode == 0, f"組み合わせ検証に失敗しました: {stderr.decode()}"
            
            # メモリ使用量出力
            print(f"{model_name}組み合わせ検証最大メモリ使用量: {max_memory_mb:.2f} MB")
            
            # メモリ閾値検証（8GB以下を推奨）
            MAX_MEMORY_MB = 8192.0
            if max_memory_mb > MAX_MEMORY_MB:
                pytest.warn(
                    f"{model_name}メモリ使用量が推奨値を超過: {max_memory_mb:.2f} MB > {MAX_MEMORY_MB} MB"
                )
        
        finally:
            # プロセスクリーンアップ
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=10)


@pytest.mark.performance
@pytest.mark.manual
class TestOptimizeManualPerformanceGuide:
    """組み合わせ検証手動パフォーマンステストガイド"""

    def test_manual_performance_guide(self):
        """
        組み合わせ検証手動パフォーマンステストガイド
        
        手動テスト手順:
        1. データ処理実行: python AI/data/data.py
        2. LightGBM組み合わせ検証実行:
           python AI/train/LightGBM/LightGBM_optimize_years.py
        3. 実行時間計測（Stopwatchまたはtime.timeで計測）
        4. 結果ファイル生成確認:
           AI/train/LightGBM/YYYY-MM-DD_LightGBM_optimize_years.txt
        5. メモ帳で結果が自動オープンされることを確認
        
        合格基準:
        - LightGBM: < 360秒（6分）
        - Keras: < 600秒（10分）
        - RandomForest: < 480秒（8分）
        - PyCaret: < 720秒（12分）
        
        実行コマンド例:
            # PowerShell
            Measure-Command { py -3.10 AI/train/LightGBM/LightGBM_optimize_years.py }
            
            # Python time測定
            import time
            start = time.time()
            # スクリプト実行
            print(f"実行時間: {time.time() - start:.2f}秒")
        """
        print("\n=== 組み合わせ検証手動パフォーマンステストガイド ===")
        print("1. データ処理実行: python AI/data/data.py")
        print("2. LightGBM組み合わせ検証実行:")
        print("   python AI/train/LightGBM/LightGBM_optimize_years.py")
        print("3. 実行時間計測")
        print("4. 結果ファイル生成確認")
        print("5. メモ帳で結果が自動オープンされることを確認")
        print("\n合格基準:")
        print("- LightGBM: < 360秒（6分）")
        print("- Keras: < 600秒（10分）")
        print("- RandomForest: < 480秒（8分）")
        print("- PyCaret: < 720秒（12分）")
        print("\nPowerShellコマンド例:")
        print("Measure-Command { py -3.10 AI/train/LightGBM/LightGBM_optimize_years.py }")
        
        # 自動スキップ（手動テストのみ）
        pytest.skip("手動テストガイドのため自動実行なし")
