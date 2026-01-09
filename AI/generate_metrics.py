#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Metrics Aggregator for GitHub Pages Deployment
各モデルの予測精度指標をJSON形式で集約する
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

def extract_metrics_from_csv(csv_path: Path, ytest_path: Path) -> Optional[Dict[str, float]]:
    """
    CSVファイルから予測値を読み込み、実測値と比較して精度指標を計算
    
    Args:
        csv_path: 予測値CSVのパス
        ytest_path: 実測値CSVのパス
        
    Returns:
        Dict[str, float]: RMSE, R2, MAEを含む辞書、または None
    """
    try:
        import pandas as pd
        import numpy as np
        from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
        
        if not csv_path.exists() or not ytest_path.exists():
            return None
        
        # 予測値読み込み
        pred_df = pd.read_csv(csv_path)
        y_pred = pred_df.iloc[:, 0].values
        
        # 実測値読み込み
        y_test_df = pd.read_csv(ytest_path)
        y_test = y_test_df.iloc[:, 0].values
        
        # 長さを合わせる
        min_len = min(len(y_pred), len(y_test))
        y_pred = y_pred[:min_len]
        y_test = y_test[:min_len]
        
        # 指標計算
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        r2 = float(r2_score(y_test, y_pred))
        mae = float(mean_absolute_error(y_test, y_pred))
        
        return {
            "rmse": round(rmse, 3),
            "r2": round(r2, 4),
            "mae": round(mae, 3)
        }
    except Exception as e:
        print(f"Error extracting metrics from {csv_path}: {e}")
        return None

def aggregate_metrics() -> Dict[str, Any]:
    """
    全モデルの精度指標を集約
    
    Returns:
        Dict[str, Any]: 全モデルの指標を含むJSON
    """
    import os
    base_path = Path(__file__).parent
    tomorrow_dir = base_path / "tomorrow"
    ytest_path = tomorrow_dir / "Ytest.csv"
    
    models = {
        "lightgbm": "LightGBM",
        "keras": "Keras",
        "randomforest": "RandomForest",
        "pycaret": "Pycaret"
    }
    
    # 環境変数から学習年を取得、デフォルトは2022,2023,2024
    training_years = os.environ.get('AI_TARGET_YEARS', '2022,2023,2024')
    
    metrics = {
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "training_years": training_years,
        "models": {}
    }
    
    for model_key, model_name in models.items():
        model_dir = tomorrow_dir / model_name
        csv_path = model_dir / f"{model_name}_tomorrow.csv"
        
        model_metrics = extract_metrics_from_csv(csv_path, ytest_path)
        if model_metrics:
            metrics[model_key] = model_metrics
            print(f"✓ {model_name}: RMSE={model_metrics['rmse']}, R2={model_metrics['r2']}, MAE={model_metrics['mae']}")
        else:
            print(f"✗ {model_name}: メトリクス抽出失敗")
    
    return metrics

def main():
    """メイン処理"""
    print("=" * 60)
    print("Metrics Aggregation for GitHub Pages")
    print("=" * 60)
    
    metrics = aggregate_metrics()
    
    # JSONファイルに保存
    output_path = Path(__file__).parent / "metrics.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Metrics saved to: {output_path}")
    print(f"✓ Total models processed: {len(metrics) - 1}")  # updated_at除く
    print("=" * 60)

if __name__ == "__main__":
    main()
