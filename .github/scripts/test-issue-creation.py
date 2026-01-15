#!/usr/bin/env python3
"""GitHub Actions Issue自動作成統合テストスクリプト"""

import sys
import os

def test_accuracy_check():
    """精度閾値チェックロジックテスト"""
    print("=" * 80)
    print("精度閾値チェック統合テスト")
    print("=" * 80)
    
    test_cases = [
        ("0.9190", False, "正常: R² >= 0.8"),
        ("0.8000", False, "境界値: R² = 0.8"),
        ("0.7999", True, "閾値違反: R² < 0.8"),
        ("0.7654", True, "閾値違反: R² < 0.8"),
        ("0.5000", True, "重大な劣化: R² < 0.8"),
        ("", True, "R²値取得失敗"),
    ]
    
    passed = 0
    failed = 0
    
    for r2_str, expected_degraded, description in test_cases:
        print(f"\nテストケース: {description}")
        print(f"  R²値: '{r2_str}'")
        
        # GitHub Actionsワークフローと同じロジック
        if not r2_str:
            degraded = True
            print("  判定: R²値が空 → accuracy_degraded=true")
        else:
            try:
                r2_float = float(r2_str)
                degraded = r2_float < 0.8
                print(f"  判定: {r2_float} < 0.8 → accuracy_degraded={str(degraded).lower()}")
            except ValueError:
                degraded = True
                print("  判定: float変換失敗 → accuracy_degraded=true")
        
        if degraded == expected_degraded:
            print(f"  ✓ 合格")
            passed += 1
        else:
            print(f"  ❌ 不合格（期待値: {expected_degraded}, 実際: {degraded}）")
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"テスト結果: {passed}/{passed + failed}合格")
    print("=" * 80)
    
    return 0 if failed == 0 else 1

def test_metrics_extraction():
    """メトリクス抽出テスト"""
    import tempfile
    import subprocess
    
    print("\n" + "=" * 80)
    print("メトリクス抽出テスト")
    print("=" * 80)
    
    test_outputs = [
        ("最終結果 - RMSE: 113.385 kW, R2: 0.9190, MAE: 81.076 kW", "0.9190", "正常ケース"),
        ("最終結果 - RMSE: 234.567 kW, R2: 0.7654, MAE: 189.012 kW", "0.7654", "低精度ケース"),
        ("最終結果 - RMSE: 100.000 kW, R2: 0.8000, MAE: 75.000 kW", "0.8000", "境界値ケース"),
    ]
    
    passed = 0
    failed = 0
    
    for output_line, expected_r2, description in test_outputs:
        print(f"\nテストケース: {description}")
        print(f"  入力: {output_line}")
        
        # 一時ファイルに書き込み
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.txt') as f:
            f.write(output_line + '\n')
            temp_file = f.name
        
        try:
            # extract-metrics.pyを実行
            result = subprocess.run(
                [sys.executable, '.github/scripts/extract-metrics.py', temp_file],
                capture_output=True,
                text=True,
                encoding='cp932',  # Windowsコンソール用
                errors='replace'
            )
            
            if result.returncode != 0:
                print(f"  ❌ スクリプト実行失敗")
                print(f"  stderr: {result.stderr}")
                failed += 1
                continue
            
            # r2値を抽出
            for line in result.stdout.split('\n'):
                if line.startswith('r2='):
                    actual_r2 = line.split('=')[1].strip()
                    break
            else:
                actual_r2 = None
            
            print(f"  出力: r2={actual_r2}")
            
            if actual_r2 == expected_r2:
                print(f"  ✓ 合格")
                passed += 1
            else:
                print(f"  ❌ 不合格（期待値: {expected_r2}, 実際: {actual_r2}）")
                failed += 1
                
        finally:
            os.unlink(temp_file)
    
    print("\n" + "=" * 80)
    print(f"テスト結果: {passed}/{passed + failed}合格")
    print("=" * 80)
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    exit_code1 = test_accuracy_check()
    exit_code2 = test_metrics_extraction()
    
    sys.exit(max(exit_code1, exit_code2))
