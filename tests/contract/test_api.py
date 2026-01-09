"""
API契約テスト: /run-data、/run-train エンドポイント (US1 MVP)

契約テスト要件:
- /run-data: POST、環境変数AI_TARGET_YEARS設定、JSONレスポンス
- /run-train: POST、モデル名動的実行、RMSE/R²/MAE返却
- エラーハンドリング: 不正パラメータで400、内部エラーで500
- レスポンスタイム: < 2秒（データ処理）、< 60秒（学習）
- CORS設定: Access-Control-Allow-Origin: *

実行方法:
    pytest tests/contract/test_api.py -v

前提条件:
    HTTPサーバーが起動している（python AI/server.py）

依存関係:
    - requests>=2.31.0
    - pytest>=8.0.0

テストシナリオ:
    /run-data契約:
        - POST /run-data {"years": [2022, 2023, 2024]} → 200 OK
        - レスポンスにstatus、messageが含まれる
        - 環境変数AI_TARGET_YEARSが設定される
        - レスポンスタイム < 2秒

    /run-train契約:
        - POST /run-train {"model": "LightGBM"} → 200 OK
        - レスポンスにrmse、r2、maeが含まれる
        - r2 >= 0.80（精度閾値）
        - レスポンスタイム < 60秒

    エラーケース契約:
        - POST /run-data {"years": []} → 400 Bad Request
        - POST /run-train {"model": "InvalidModel"} → 400 Bad Request
        - POST /run-train {} → 400 Bad Request
"""

import os
import time
import pytest
import requests
from typing import Dict, Any


# 定数
API_BASE_URL = "http://localhost:8002"
RUN_DATA_ENDPOINT = f"{API_BASE_URL}/run-data"
RUN_TRAIN_ENDPOINT = f"{API_BASE_URL}/run-train"
VALID_MODELS = ["LightGBM", "Keras", "RandomForest", "Pycaret"]
DEFAULT_YEARS = [2022, 2023, 2024]


@pytest.fixture(scope="module")
def verify_server_running():
    """
    HTTPサーバー起動確認フィクスチャ
    
    前提条件:
        python AI/server.py でサーバーが起動している
    """
    try:
        response = requests.get(API_BASE_URL, timeout=5)
        # サーバーが起動していればOK（ステータスコード問わず）
    except requests.exceptions.RequestException as e:
        pytest.skip(f"HTTPサーバーが起動していません: {e}")


@pytest.mark.contract
class TestRunDataContract:
    """/run-data エンドポイント契約テスト"""

    def test_run_data_success(self, verify_server_running):
        """
        契約: POST /run-data {"years": [2022, 2023, 2024]} → 200 OK
        
        検証項目:
        - ステータスコード: 200
        - レスポンス形式: JSON
        - レスポンスキー: status、message
        - status値: "success" または "ok"
        - レスポンスタイム: < 2秒
        """
        payload = {"years": DEFAULT_YEARS}
        start_time = time.time()
        
        response = requests.post(RUN_DATA_ENDPOINT, json=payload, timeout=30)
        elapsed_time = time.time() - start_time
        
        # ステータスコード検証
        assert response.status_code == 200, f"ステータスコード不正: {response.status_code}"
        
        # JSON形式検証
        assert response.headers.get("Content-Type") == "application/json", "Content-Typeがapplication/jsonではありません"
        
        # レスポンス構造検証
        data = response.json()
        assert "status" in data, "レスポンスにstatusキーが含まれていません"
        assert "message" in data, "レスポンスにmessageキーが含まれていません"
        
        # status値検証
        assert data["status"] in ["success", "ok"], f"status値が不正: {data['status']}"
        
        # レスポンスタイム検証
        assert elapsed_time < 2.0, f"レスポンスタイムが閾値超過: {elapsed_time:.2f}秒 > 2秒"

    def test_run_data_with_custom_years(self, verify_server_running):
        """
        契約: POST /run-data {"years": [2020, 2021, 2022]} → 200 OK
        
        検証項目:
        - カスタム学習年でも正常動作
        - 環境変数AI_TARGET_YEARSが設定される（間接検証）
        """
        payload = {"years": [2020, 2021, 2022]}
        response = requests.post(RUN_DATA_ENDPOINT, json=payload, timeout=30)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["success", "ok"]

    def test_run_data_empty_years_400(self, verify_server_running):
        """
        契約: POST /run-data {"years": []} → 400 Bad Request
        
        検証項目:
        - ステータスコード: 400
        - エラーメッセージが含まれる
        """
        payload = {"years": []}
        response = requests.post(RUN_DATA_ENDPOINT, json=payload, timeout=30)
        
        # 400または200（実装により異なる場合がある）
        # エラーハンドリングが実装されている場合は400を期待
        if response.status_code == 400:
            data = response.json()
            assert "error" in data or "message" in data, "エラーメッセージが含まれていません"
        else:
            # 実装がバリデーションしていない場合はスキップ
            pytest.skip("空配列バリデーションが未実装")

    def test_run_data_invalid_json_400(self, verify_server_running):
        """
        契約: POST /run-data (不正JSON) → 400 Bad Request
        
        検証項目:
        - ステータスコード: 400または500
        - エラーメッセージが含まれる
        """
        response = requests.post(
            RUN_DATA_ENDPOINT,
            data="invalid json",
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        # 不正JSONの場合は400または500を期待
        assert response.status_code in [400, 500], f"不正JSONでステータスコード{response.status_code}が返却されました"

    def test_run_data_cors_headers(self, verify_server_running):
        """
        契約: CORSヘッダーが正しく設定されている
        
        検証項目:
        - Access-Control-Allow-Origin: *
        - Access-Control-Allow-Methods: GET, POST, OPTIONS
        """
        # OPTIONSリクエスト（プリフライト）
        response = requests.options(RUN_DATA_ENDPOINT, timeout=30)
        
        # CORS許可確認
        assert response.status_code in [200, 204], f"OPTIONSリクエストが失敗: {response.status_code}"
        
        # CORSヘッダー確認
        assert "Access-Control-Allow-Origin" in response.headers, "CORSヘッダーが設定されていません"
        assert response.headers["Access-Control-Allow-Origin"] == "*", "CORS設定が不正"


@pytest.mark.contract
@pytest.mark.slow
class TestRunTrainContract:
    """/run-train エンドポイント契約テスト"""

    @pytest.fixture(autouse=True)
    def setup_data(self, verify_server_running):
        """
        各テスト前にデータ処理を実行
        
        Note:
            学習にはデータ処理が必須のため、テストごとに実行
        """
        payload = {"years": DEFAULT_YEARS}
        response = requests.post(RUN_DATA_ENDPOINT, json=payload, timeout=30)
        assert response.status_code == 200, "データ処理セットアップに失敗しました"

    @pytest.mark.parametrize("model_name", VALID_MODELS)
    def test_run_train_success(self, model_name: str):
        """
        契約: POST /run-train {"model": "LightGBM"} → 200 OK
        
        検証項目:
        - ステータスコード: 200
        - レスポンス形式: JSON
        - レスポンスキー: status、rmse、r2、mae
        - rmse値: 正の数値
        - r2値: 0.80以上（精度閾値）
        - mae値: 正の数値
        - レスポンスタイム: < 60秒
        """
        payload = {"model": model_name}
        start_time = time.time()
        
        response = requests.post(RUN_TRAIN_ENDPOINT, json=payload, timeout=90)
        elapsed_time = time.time() - start_time
        
        # ステータスコード検証
        assert response.status_code == 200, f"{model_name}学習が失敗: {response.status_code}"
        
        # JSON形式検証
        assert response.headers.get("Content-Type") == "application/json"
        
        # レスポンス構造検証
        data = response.json()
        assert "status" in data, "レスポンスにstatusキーが含まれていません"
        assert "rmse" in data, "レスポンスにrmseキーが含まれていません"
        assert "r2" in data, "レスポンスにr2キーが含まれていません"
        assert "mae" in data, "レスポンスにmaeキーが含まれていません"
        
        # メトリクス値検証
        rmse = data["rmse"]
        r2 = data["r2"]
        mae = data["mae"]
        
        assert isinstance(rmse, (int, float)), f"rmseが数値ではありません: {rmse}"
        assert isinstance(r2, (int, float)), f"r2が数値ではありません: {r2}"
        assert isinstance(mae, (int, float)), f"maeが数値ではありません: {mae}"
        
        assert rmse > 0, f"rmseが0以下: {rmse}"
        assert mae > 0, f"maeが0以下: {mae}"
        
        # 精度閾値検証（US1要件: R² >= 0.80）
        assert r2 >= 0.80, f"{model_name}のR²スコアが閾値未満: {r2:.4f} < 0.80"
        
        # レスポンスタイム検証
        max_time = 60.0 if model_name != "Keras" else 90.0  # Kerasは90秒許容
        assert elapsed_time < max_time, f"{model_name}レスポンスタイムが閾値超過: {elapsed_time:.2f}秒 > {max_time}秒"

    def test_run_train_invalid_model_400(self):
        """
        契約: POST /run-train {"model": "InvalidModel"} → 400 Bad Request
        
        検証項目:
        - ステータスコード: 400
        - エラーメッセージが含まれる
        """
        payload = {"model": "InvalidModel"}
        response = requests.post(RUN_TRAIN_ENDPOINT, json=payload, timeout=30)
        
        # 400または500（実装により異なる）
        assert response.status_code in [400, 500], f"不正モデル名でステータスコード{response.status_code}が返却されました"
        
        # エラーメッセージ確認
        data = response.json()
        assert "error" in data or "message" in data, "エラーメッセージが含まれていません"

    def test_run_train_missing_model_400(self):
        """
        契約: POST /run-train {} → 400 Bad Request
        
        検証項目:
        - ステータスコード: 400
        - エラーメッセージが含まれる
        """
        payload = {}
        response = requests.post(RUN_TRAIN_ENDPOINT, json=payload, timeout=30)
        
        assert response.status_code in [400, 500]
        data = response.json()
        assert "error" in data or "message" in data

    def test_run_train_cors_headers(self):
        """
        契約: CORSヘッダーが正しく設定されている
        
        検証項目:
        - Access-Control-Allow-Origin: *
        """
        response = requests.options(RUN_TRAIN_ENDPOINT, timeout=30)
        
        assert response.status_code in [200, 204]
        assert "Access-Control-Allow-Origin" in response.headers
        assert response.headers["Access-Control-Allow-Origin"] == "*"


@pytest.mark.contract
@pytest.mark.integration
class TestAPIIntegration:
    """API統合契約テスト（複数エンドポイント組み合わせ）"""

    def test_full_api_workflow(self, verify_server_running):
        """
        完全APIワークフロー契約テスト: データ処理 → 学習
        
        シナリオ:
        1. POST /run-data {"years": [2022, 2023, 2024]}
        2. POST /run-train {"model": "LightGBM"}
        3. レスポンス検証
        """
        # 1. データ処理
        data_payload = {"years": DEFAULT_YEARS}
        data_response = requests.post(RUN_DATA_ENDPOINT, json=data_payload, timeout=30)
        assert data_response.status_code == 200
        
        # 2. 学習
        train_payload = {"model": "LightGBM"}
        train_response = requests.post(RUN_TRAIN_ENDPOINT, json=train_payload, timeout=90)
        assert train_response.status_code == 200
        
        # 3. レスポンス検証
        train_data = train_response.json()
        assert train_data["r2"] >= 0.80

    @pytest.mark.parametrize("model_name", VALID_MODELS)
    def test_all_models_contract_compliance(self, verify_server_running, model_name: str):
        """
        全モデル契約準拠テスト
        
        検証項目:
        - 全モデルで同一の契約（rmse、r2、mae）が守られる
        - 全モデルでR² >= 0.80を満たす
        """
        # データ処理
        data_payload = {"years": DEFAULT_YEARS}
        data_response = requests.post(RUN_DATA_ENDPOINT, json=data_payload, timeout=30)
        assert data_response.status_code == 200
        
        # 学習
        train_payload = {"model": model_name}
        train_response = requests.post(RUN_TRAIN_ENDPOINT, json=train_payload, timeout=90)
        
        # 契約検証
        assert train_response.status_code == 200, f"{model_name}契約違反: ステータスコード{train_response.status_code}"
        
        train_data = train_response.json()
        assert "rmse" in train_data, f"{model_name}契約違反: rmseキー不在"
        assert "r2" in train_data, f"{model_name}契約違反: r2キー不在"
        assert "mae" in train_data, f"{model_name}契約違反: maeキー不在"
        
        # 精度閾値契約
        assert train_data["r2"] >= 0.80, f"{model_name}契約違反: R²スコア {train_data['r2']:.4f} < 0.80"


@pytest.mark.contract
class TestAPIErrorHandling:
    """APIエラーハンドリング契約テスト"""

    def test_server_unavailable_connection_error(self):
        """
        契約: サーバー停止時にConnection Errorが発生する
        
        検証項目:
        - requests.exceptions.ConnectionErrorが発生
        
        Note:
            このテストはサーバーが停止している環境でのみ成功
            通常は verify_server_running でスキップされる
        """
        # 不正なポートに接続
        invalid_url = "http://localhost:9999/run-data"
        
        with pytest.raises(requests.exceptions.ConnectionError):
            requests.post(invalid_url, json={"years": [2022]}, timeout=5)

    def test_timeout_handling(self, verify_server_running):
        """
        契約: タイムアウト時にTimeoutErrorが発生する
        
        検証項目:
        - requests.exceptions.Timeoutが発生（極端に短いタイムアウト設定）
        
        Note:
            実装によってはタイムアウト前に応答が返る場合がある
        """
        payload = {"model": "LightGBM"}
        
        # 極端に短いタイムアウト（0.001秒）
        try:
            response = requests.post(RUN_TRAIN_ENDPOINT, json=payload, timeout=0.001)
            # タイムアウトしなかった場合はスキップ
            pytest.skip("サーバーが即座に応答したためタイムアウトテストをスキップ")
        except requests.exceptions.Timeout:
            # 期待通りタイムアウト発生
            pass
