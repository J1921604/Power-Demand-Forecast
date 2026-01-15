#!/usr/bin/env python3
"""GitHub Actions ワークフローYAML構文チェックスクリプト"""

import sys
import yaml

def check_yaml(filepath):
    """YAML構文チェック"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            yaml.safe_load(f)
        print(f'✓ YAML構文チェック合格: {filepath}')
        return 0
    except yaml.YAMLError as e:
        print(f'❌ YAML構文エラー: {filepath}')
        print(e)
        return 1
    except Exception as e:
        print(f'❌ ファイル読み込みエラー: {filepath}')
        print(e)
        return 1

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('使用法: python check-yaml.py <yaml-file>')
        sys.exit(1)

    sys.exit(check_yaml(sys.argv[1]))
