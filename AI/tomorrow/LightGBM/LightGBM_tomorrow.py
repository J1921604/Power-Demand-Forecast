# -*- coding: utf-8 -*-
"""
電力需要予測AIモデル - LightGBM明日予測モジュール

学習済みLightGBMモデルを使用して明日の電力需要を予測し、
結果をCSVファイルとグラフで出力するモジュール。
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn.preprocessing import StandardScaler
import pickle
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import traceback
import os
import datetime
import time
import gc
import psutil
from dataclasses import dataclass
from functools import wraps
from typing import Tuple, Optional, Dict, Any

# matplotlib日本語フォント設定
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 100
plt.rcParams['savefig.bbox'] = 'tight'
plt.rcParams['savefig.pad_inches'] = 0.1
try:
    from matplotlib import font_manager
    preferred_fonts = ['Meiryo', 'Yu Gothic', 'Noto Sans CJK JP', 'IPAexGothic', 'TakaoPGothic', 'IPAPGothic', 'DejaVu Sans']
    available = {f.name for f in font_manager.fontManager.ttflist}
    chosen = None
    for fname in preferred_fonts:
        if fname in available:
            chosen = fname
            break
    if chosen:
        plt.rcParams['font.family'] = [chosen, 'DejaVu Sans']
    else:
        plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['axes.unicode_minus'] = False
except Exception:
    plt.rcParams['font.family'] = 'DejaVu Sans'

plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3
plt.rcParams['lines.linewidth'] = 1.5
plt.rcParams['axes.linewidth'] = 0.8

@dataclass
class LightGBMTomorrowConfig:
    """LightGBM翌日予測設定クラス"""
    # パス基準（AIディレクトリ）
    PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR: str = os.path.join(PROJECT_ROOT, "data")
    TOMORROW_DIR: str = os.path.join(PROJECT_ROOT, "tomorrow")
    TRAIN_DIR: str = os.path.join(PROJECT_ROOT, "train", "LightGBM")
    TOMORROW_MODEL_DIR: str = os.path.join(TOMORROW_DIR, "LightGBM")

    # 入力データ関連
    XTRAIN_CSV: str = os.path.join(DATA_DIR, "Xtrain.csv")
    XTEST_CSV: str = os.path.join(DATA_DIR, "Xtest.csv")
    YTRAIN_CSV: str = os.path.join(DATA_DIR, "Ytrain.csv")
    YTEST_CSV: str = os.path.join(TOMORROW_DIR, "Ytest.csv")
    XTOMORROW_CSV: str = os.path.join(TOMORROW_DIR, "tomorrow.csv")
    
    # モデル関連
    MODEL_SAV: str = os.path.join(TRAIN_DIR, "LightGBM_model.sav")
    
    # 出力関連
    YPRED_CSV: str = os.path.join(TOMORROW_MODEL_DIR, "LightGBM_Ypred.csv")
    YPRED_PNG: str = os.path.join(TOMORROW_MODEL_DIR, "LightGBM_Ypred.png")
    YPRED_7D_PNG: str = os.path.join(TOMORROW_MODEL_DIR, "LightGBM_Ypred_7d.png")
    YTOMORROW_CSV: str = os.path.join(TOMORROW_MODEL_DIR, "LightGBM_tomorrow.csv")
    YTOMORROW_PNG: str = os.path.join(TOMORROW_MODEL_DIR, "LightGBM_tomorrow.png")
    
    # 設定パラメータ
    PAST_DAYS: str = '7'
    LEARNING_RATE: str = ''
    EPOCHS: str = ''
    VALIDATION_SPLIT: str = ''
    HISTORY_PNG: str = ''
    
    # データ列
    X_COLS: tuple = ("MONTH","WEEK","HOUR","TEMP")
    Y_COLS: tuple = ("KW",)

def robust_model_operation(operation_name: str):
    """モデル操作の堅牢性を保証するデコレータ"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            try:
                print(f"実行開始: {operation_name}")
                result = func(*args, **kwargs)
                
                # メモリ使用量とガベージコレクション
                collected = gc.collect()
                final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                execution_time = time.time() - start_time
                
                print(f"実行完了: {operation_name}")
                print(f"実行時間: {execution_time:.3f}秒")
                print(f"メモリ使用量: {initial_memory:.1f}MB → {final_memory:.1f}MB (差分: {final_memory-initial_memory:+.1f}MB)")
                print(f"ガベージコレクション: {collected}個のオブジェクトを回収")
                
                return result
                
            except Exception as e:
                print(f"エラー発生 in {operation_name}: {e}")
                print(f"トレースバック:\n{traceback.format_exc()}")
                return None
                
        return wrapper
    return decorator

def should_use_cached_predictions() -> bool:
    """既存の予測CSVを優先するか判定"""
    return os.environ.get("AI_FORCE_REPREDICT", "").lower() not in ("1", "true", "yes", "y")

def load_cached_predictions(config: LightGBMTomorrowConfig) -> Optional[pd.DataFrame]:
    """既存の予測CSVを読み込む"""
    if not os.path.exists(config.YTOMORROW_CSV):
        return None
    try:
        df = pd.read_csv(config.YTOMORROW_CSV)
        if df.empty:
            return None
        return df.iloc[:, 0].to_numpy()
    except Exception as e:
        print(f"[WARN] 予測CSV読み込み失敗: {e}")
        return None

@robust_model_operation("学習データ読み込み")
def load_training_data(config: LightGBMTomorrowConfig) -> Tuple[pd.DataFrame, StandardScaler]:
    """学習データを読み込み、標準化スケーラーを作成"""
    X_train = pd.read_csv(config.XTRAIN_CSV)

    # 学習時に保存したスケーラーがあれば優先して使用
    scaler_path = config.MODEL_SAV.replace('.sav', '_scaler.pkl')
    if os.path.exists(scaler_path):
        try:
            with open(scaler_path, 'rb') as f:
                scaler = pickle.load(f)
            print(f"スケーラー読み込み完了: {scaler_path}")
        except Exception as e:
            print(f"スケーラー読み込み失敗: {e} - 再学習を実施します")
            scaler = StandardScaler()
            scaler.fit(X_train)
    else:
        # 標準化スケーラーを作成・学習
        scaler = StandardScaler()
        scaler.fit(X_train)

    X_train_scaled = pd.DataFrame(scaler.transform(X_train), columns=X_train.columns)
    
    print(f"学習データ形状: {X_train_scaled.shape}")
    return X_train_scaled, scaler

@robust_model_operation("テスト・翌日データ読み込み")
def load_test_and_tomorrow_data(config: LightGBMTomorrowConfig, scaler: StandardScaler) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """テストデータと翌日データを読み込み、標準化"""
    y_test = pd.read_csv(config.YTEST_CSV).values.astype('int32').flatten()
    Xtomorrow = pd.read_csv(config.XTOMORROW_CSV)
    
    # 翌日データを標準化
    Xtomorrow_scaled = pd.DataFrame(scaler.transform(Xtomorrow), columns=Xtomorrow.columns)
    
    print(f"テストデータ形状: {y_test.shape}")
    print(f"翌日データ形状: {Xtomorrow_scaled.shape}")
    return y_test, Xtomorrow_scaled

@robust_model_operation("モデル読み込み")
def load_model(config: LightGBMTomorrowConfig):
    """保存済みモデルを読み込み"""
    with open(config.MODEL_SAV, 'rb') as f:
        model = pickle.load(f)
    print(f"モデル読み込み完了: {config.MODEL_SAV}")
    return model

@robust_model_operation("予測実行")
def predict_with_model(model, Xtomorrow_scaled: pd.DataFrame, y_test: pd.DataFrame) -> Tuple[pd.DataFrame, float, float, float, float]:
    """
    モデルを使用して予測を実行し、精度を計算
    
    Returns:
        Tuple[Ytomorrow, RMSE, Score, R2, MAE]
    """
    # Xtomorrow_scaledは過去7日分+予測7日分の合計14日分（336時間）
    # y_testは過去7日分の実測値（168時間）
    
    # LightGBM 4.6.0の既知の問題を回避: _n_classesがNoneの場合を処理
    if hasattr(model, '_n_classes') and model._n_classes is None:
        # 回帰モデルの場合は_n_classesを1に設定（回避策）
        model._n_classes = 1
    
    # データ長を確認
    test_length = len(y_test)
    total_length = len(Xtomorrow_scaled)
    
    # 過去7日分（テスト用）と予測7日分に分割
    # 前半: テスト精度評価用（過去7日分）
    # 後半: 実際の翌日予測用（予測7日分）
    X_test_part = Xtomorrow_scaled[:test_length]
    X_forecast_part = Xtomorrow_scaled[test_length:]
    
    # テスト部分で精度評価
    Y_test_pred = model.predict(X_test_part)
    
    # 精度計算（テスト部分のみ）
    try:
        accuracy = model.score(X_test_part, y_test)
        print(f'テスト精度: {accuracy:.4f}')
    except Exception as e:
        print(f'精度計算でエラーが発生: {e}')
        accuracy = 0.0
    
    # RMSE・スコア計算（テスト部分のみ）
    mse = mean_squared_error(y_test, Y_test_pred)
    REG_RMSE = mse ** 0.5
    REG_SCORE = 1.0 - mse ** 0.5 / y_test.mean()
    # 標準的な指標も計算して出力（MAE, R2）
    MAE = mean_absolute_error(y_test, Y_test_pred)
    R2 = r2_score(y_test, Y_test_pred)

    # 統一フォーマットで一行出力（RMSE/R2/MAE）
    print(f"最終結果 - RMSE: {REG_RMSE:.3f} kW, R2: {R2:.4f}, MAE: {MAE:.3f} kW")
    
    # 全期間の予測（過去7日分+予測7日分）
    Ytomorrow_full = model.predict(Xtomorrow_scaled)
    
    return Ytomorrow_full, REG_RMSE, REG_SCORE, R2, MAE

@robust_model_operation("翌日予測結果保存")
def save_tomorrow_predictions(config: LightGBMTomorrowConfig, Ytomorrow: pd.DataFrame) -> None:
    """翌日予測結果をCSVファイルに保存"""
    y_tomorrow_csv = pd.DataFrame(Ytomorrow, columns=list(config.Y_COLS))
    y_tomorrow_csv.to_csv(config.YTOMORROW_CSV, index=False)
    print(f"予測結果保存完了: {config.YTOMORROW_CSV} ({len(y_tomorrow_csv)}行)")

@robust_model_operation("グラフ生成")
def generate_prediction_graph(config: LightGBMTomorrowConfig, Ytomorrow: pd.DataFrame, y_test: pd.DataFrame) -> None:
    """予測結果のグラフを生成"""
    # データフレーム作成
    df_result1 = pd.DataFrame({"Predict[kW]": Ytomorrow.ravel()})
    df_result2 = pd.DataFrame({"Actual[kW]": y_test.ravel()})
    
    # 日時インデックス作成
    # 明示的に日本時間(JST=UTC+9)を使用してインデックスを作成
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    past_days_int = int(config.PAST_DAYS)
    past_days_ago = now - datetime.timedelta(days=past_days_int)
    past_days_ago = past_days_ago.date()
    
    df_result1.index = pd.date_range(start=past_days_ago, periods=len(df_result1), freq='h')
    df_result2.index = pd.date_range(start=past_days_ago, periods=len(df_result2), freq='h')
    # インデックス名を明示（年月日表示）
    df_result1.index.name = 'Date'
    df_result2.index.name = 'Date'
    
    # グラフ描画
    plt.figure(figsize=(16, 9))
    plt.plot(df_result1, label='Predict[kW]')
    plt.plot(df_result2, label='Actual[kW]')
    
    filename = os.path.splitext(os.path.basename(config.MODEL_SAV))[0]
    plt.title(filename, fontsize=12)
    # x軸を年月日で表示
    plt.xlabel('Date', fontsize=12)
    # x軸は年月日表示とする（回転は行わない）
    try:
        ax = plt.gca()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    except Exception:
        pass
    plt.ylabel('Power [kW]', fontsize=12)
    plt.legend(fontsize=11)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.tight_layout()
    plt.savefig(config.YTOMORROW_PNG)
    plt.close()
    
    print(f"グラフ保存完了: {config.YTOMORROW_PNG}")

def tomorrow(Xtrain_csv, Xtest_csv, Ytrain_csv, Ytest_csv, model_sav, Ypred_csv, Ypred_png, Ypred_7d_png, learning_rate, epochs, validation_split, history_png, Xtomorrow_csv, Ytomorrow_csv, Ytomorrow_png, past_days):
    """レガシー関数：下位互換性のため保持"""
    config = LightGBMTomorrowConfig(
        XTRAIN_CSV=Xtrain_csv,
        XTEST_CSV=Xtest_csv,
        YTRAIN_CSV=Ytrain_csv,
        YTEST_CSV=Ytest_csv,
        MODEL_SAV=model_sav,
        YPRED_CSV=Ypred_csv,
        YPRED_PNG=Ypred_png,
        YPRED_7D_PNG=Ypred_7d_png,
        XTOMORROW_CSV=Xtomorrow_csv,
        YTOMORROW_CSV=Ytomorrow_csv,
        YTOMORROW_PNG=Ytomorrow_png,
        PAST_DAYS=past_days,
        LEARNING_RATE=learning_rate,
        EPOCHS=epochs,
        VALIDATION_SPLIT=validation_split,
        HISTORY_PNG=history_png
    )
    return execute_tomorrow_prediction(config)

@robust_model_operation("LightGBM翌日予測メイン処理")
def execute_tomorrow_prediction(config: LightGBMTomorrowConfig) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
    """統一されたLightGBM翌日予測処理
    
    Returns:
        Tuple[RMSE, Score, R2, MAE]
    """
    if should_use_cached_predictions():
        cached_pred = load_cached_predictions(config)
        if cached_pred is not None:
            y_test = pd.read_csv(config.YTEST_CSV).values.astype('int32').flatten()
            if len(cached_pred) >= len(y_test):
                print("[INFO] 既存の予測CSVを使用（AI_FORCE_REPREDICT=1で再生成）")
                eval_pred = cached_pred[:len(y_test)]
                mse = mean_squared_error(y_test, eval_pred)
                reg_rmse = mse ** 0.5
                reg_score = 0.0 if y_test.mean() == 0 else 1.0 - reg_rmse / y_test.mean()
                r2 = r2_score(y_test, eval_pred)
                mae = mean_absolute_error(y_test, eval_pred)
                print(f"最終結果 - RMSE: {reg_rmse:.3f} kW, R2: {r2:.4f}, MAE: {mae:.3f} kW")
                generate_prediction_graph(config, cached_pred, y_test)
                return reg_rmse, reg_score, r2, mae

    # 1. 学習データ読み込み・標準化スケーラー作成
    result = load_training_data(config)
    if result is None:
        return None, None, None, None
    X_train_scaled, scaler = result
    
    # 2. テスト・翌日データ読み込み・標準化
    result = load_test_and_tomorrow_data(config, scaler)
    if result is None:
        return None, None, None, None
    y_test, Xtomorrow_scaled = result
    
    # 3. モデル読み込み
    model = load_model(config)
    if model is None:
        return None, None, None, None
    
    # 4. 予測実行・精度計算
    result = predict_with_model(model, Xtomorrow_scaled, y_test)
    if result is None:
        return None, None, None, None
    Ytomorrow, REG_RMSE, REG_SCORE, R2, MAE = result
    
    # 5. 翌日予測結果保存
    save_tomorrow_predictions(config, Ytomorrow)
    
    # 6. グラフ生成
    generate_prediction_graph(config, Ytomorrow, y_test)
    
    return REG_RMSE, REG_SCORE, R2, MAE

if __name__ == "__main__":
    # 設定初期化
    config = LightGBMTomorrowConfig()
    # 起動時に監査ログとして AI_TARGET_YEARS を出力
    import os as _os
    print(f"AI_TARGET_YEARS={_os.environ.get('AI_TARGET_YEARS')}")

    print("=" * 60)
    print("LightGBM翌日電力需要予測 開始")
    print("=" * 60)
    
    start_time = time.time()
    
    # 翌日予測実行
    result = execute_tomorrow_prediction(config)
    if result[0] is None:
        rmse, score, r2, mae = None, None, None, None
    else:
        rmse, score, r2, mae = result
    
    total_time = time.time() - start_time
    
    print("=" * 60)
    print("LightGBM翌日電力需要予測 完了")
    if rmse is not None and r2 is not None and mae is not None:
        # 統一フォーマット（RMSE/R2/MAE）で出力
        print(f"最終結果 - RMSE: {rmse:.3f} kW, R2: {r2:.4f}, MAE: {mae:.3f} kW")
    print(f"総実行時間: {total_time:.3f}秒")
    print("=" * 60)
