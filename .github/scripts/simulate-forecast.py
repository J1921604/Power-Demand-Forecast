#!/usr/bin/env python3
"""GitHub Actions Issue自動作成機能テストスクリプト"""

import sys
import os

def simulate_low_accuracy():
    """R² < 0.8のケースをシミュレート"""
    print("=" * 60)
    print("LightGBM翌日電力需要予測 開始")
    print("=" * 60)
    print()
    print("学習データ形状: (1000, 4)")
    print("テストデータ形状: (100,)")
    print("翌日データ形状: (24, 4)")
    print()
    print("モデル読み込み完了: train/LightGBM/LightGBM_model.sav")
    print()
    print("テスト精度: 0.7654")
    print()
    # この行がメトリクス抽出対象
    print("最終結果 - RMSE: 234.567 kW, R2: 0.7654, MAE: 189.012 kW")
    print()
    print("予測結果保存完了: tomorrow/LightGBM/LightGBM_tomorrow.csv (24行)")
    print()
    print("グラフ保存完了: tomorrow/LightGBM/Keras_tomorrow.png")
    print()
    print("=" * 60)
    print("LightGBM翌日電力需要予測 完了")
    print("最終結果 - RMSE: 234.57 kW, スコア: 0.77")
    print("=" * 60)

def simulate_high_accuracy():
    """R² >= 0.8のケースをシミュレート"""
    print("=" * 60)
    print("LightGBM翌日電力需要予測 開始")
    print("=" * 60)
    print()
    print("最終結果 - RMSE: 113.385 kW, R2: 0.9190, MAE: 81.076 kW")
    print()
    print("=" * 60)
    print("LightGBM翌日電力需要予測 完了")
    print("=" * 60)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("使用法: python simulate-forecast.py [low|high]")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    if mode == 'low':
        simulate_low_accuracy()
    elif mode == 'high':
        simulate_high_accuracy()
    else:
        print(f"❌ 不正なモード: {mode}")
        print("使用法: python simulate-forecast.py [low|high]")
        sys.exit(1)
