import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import json

# Ytestを読み込む
ytest = pd.read_csv('AI/tomorrow/Ytest.csv')
actual = ytest['KW'].values

models = ['LightGBM', 'Keras', 'RandomForest', 'Pycaret']
results = {}

for model in models:
    csv_path = f'AI/tomorrow/{model}/{model}_tomorrow.csv'
    try:
        pred_df = pd.read_csv(csv_path)
        pred = pred_df['KW'].values
        
        # 長さを揃える（短い方に合わせる）
        min_len = min(len(actual), len(pred))
        actual_trimmed = actual[:min_len]
        pred_trimmed = pred[:min_len]
        
        # 評価指標を計算
        rmse = np.sqrt(mean_squared_error(actual_trimmed, pred_trimmed))
        r2 = r2_score(actual_trimmed, pred_trimmed)
        mae = mean_absolute_error(actual_trimmed, pred_trimmed)
        
        results[model.lower()] = {
            'rmse': round(rmse, 2),
            'r2': round(r2, 4),
            'mae': round(mae, 2)
        }
        
        print(f'{model}:')
        print(f'  RMSE: {rmse:.2f}')
        print(f'  R2: {r2:.4f}')
        print(f'  MAE: {mae:.2f}')
        print()
        
    except Exception as e:
        print(f'{model}のCSVファイル読み込みエラー: {e}')

# metrics.jsonに保存
import datetime
results['updated_at'] = datetime.datetime.now().isoformat()

with open('AI/metrics.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print('AI/metrics.jsonを更新しました')
