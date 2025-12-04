#!/usr/bin/env python3
"""予測結果メトリクス抽出スクリプト（GitHub Actions対応）"""

import re
import sys

def extract_metrics(output_file):
    """
    LightGBM予測結果から RMSE, R2, MAE を抽出する
    
    出力形式: "最終結果 - RMSE: 123.456 kW, R2: 0.8765, MAE: 98.765 kW"
    """
    try:
        # エンコーディング自動検出（UTF-8-BOM、UTF-16LE対応）
        encodings = ['utf-8-sig', 'utf-8', 'utf-16-le', 'cp932', 'shift-jis']
        content = None
        
        for encoding in encodings:
            try:
                with open(output_file, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        if content is None:
            print(f'❌ エンコーディング検出失敗: {output_file}', file=sys.stderr)
            return None, None, None
        
        # 最終結果行を検索
        pattern = r'最終結果 - RMSE: ([\d.]+) kW, R2: ([\d.]+), MAE: ([\d.]+) kW'
        matches = re.findall(pattern, content)
        
        if not matches:
            print('❌ メトリクス抽出失敗: 「最終結果」行が見つかりません', file=sys.stderr)
            print(f'ファイル内容:\n{content}', file=sys.stderr)
            return None, None, None
        
        # 最後の結果を使用
        rmse, r2, mae = matches[-1]
        
        print(f'=== メトリクス抽出成功 ===')
        print(f'RMSE: {rmse} kW')
        print(f'R2: {r2}')
        print(f'MAE: {mae} kW')
        
        return rmse, r2, mae
        
    except FileNotFoundError:
        print(f'❌ ファイルが見つかりません: {output_file}', file=sys.stderr)
        return None, None, None
    except Exception as e:
        print(f'❌ エラー発生: {e}', file=sys.stderr)
        return None, None, None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('使用法: python extract-metrics.py <output-file>')
        sys.exit(1)
    
    rmse, r2, mae = extract_metrics(sys.argv[1])
    
    if rmse is None:
        sys.exit(1)
    
    # GitHub Actions環境変数出力形式
    print(f'\nrmse={rmse}')
    print(f'r2={r2}')
    print(f'mae={mae}')
