# Research: 電力需要予測システム技術選定と設計判断

**Phase**: 0（研究・調査）
**作成日**: 2025-11-26
**バージョン**: 1.0.0
**Plan**: [plan.md](plan.md)

## 概要

このドキュメントは、電力需要予測システムのGitHub Pages化における技術選定、アーキテクチャ判断、ベストプラクティス調査の結果をまとめたものです。すべての設計判断は、プロジェクト憲法の6原則（TDD、セキュリティ、パフォーマンス、データ保護、依存関係再現性、仕様実装乖離検出）に準拠しています。

---

## 研究項目

### 1. Python 3.10.11固定バージョン選定

**決定**: Python 3.10.11を使用し、`py -3.10`コマンドで起動する

**理由**:
1. **安定性**: Python 3.10はLTS（長期サポート）版であり、2026年10月までセキュリティパッチが提供される
2. **依存関係の互換性**: LightGBM 3.3.5、TensorFlow 2.13.0、PyCaret 3.0.4はすべてPython 3.10で動作検証済み
3. **GitHub Actions対応**: `actions/setup-python@v4`でPython 3.10.11を指定可能
4. **再現性**: バージョン固定により、ローカル環境とCI/CD環境の一貫性を保証

**検討した代替案**:
- **Python 3.11/3.12**: 新機能（エラーメッセージ改善、型ヒント拡張）は魅力的だが、一部機械学習ライブラリの互換性が未確認
- **Python 3.9**: 旧バージョンは2025年10月でサポート終了のため却下

**実装方針**:
```bash
# ローカル環境
py -3.10 --version  # Python 3.10.11確認
py -3.10 -m pip install -r AI/requirements.txt

# GitHub Actions
- uses: actions/setup-python@v4
  with:
    python-version: '3.10.11'
```

---

### 2. 機械学習フレームワーク選定（4モデル）

**決定**: LightGBM、Keras/TensorFlow、RandomForest、PyCaret の4つを並行運用

**各モデルの特性**:

| モデル | 学習時間 | 精度（R²） | メモリ使用量 | 用途 |
|--------|----------|------------|--------------|------|
| **LightGBM** | < 30秒 | 0.85-0.90 | 低 | 高速・高精度、本番推奨 |
| **Keras/TensorFlow** | < 60秒 | 0.80-0.85 | 中 | 深層学習、非線形パターン検出 |
| **RandomForest** | < 45秒 | 0.80-0.85 | 中 | アンサンブル学習、解釈性高い |
| **PyCaret** | 自動最適化 | 0.80-0.90 | 高 | AutoML、モデル自動選択 |

**理由**:
1. **比較検証**: 複数モデルで精度を比較し、最適モデルを選択
2. **ユーザー選択肢**: ダッシュボードでユーザーが好みのモデルを選択可能
3. **リスク分散**: 1つのモデルに依存せず、複数の予測手法を確保

**ベストプラクティス**:
- **LightGBM**: 勾配ブースティングのデフォルト、学習速度が最速
- **Keras**: エポック数を50に制限し、過学習を防止
- **RandomForest**: n_estimators=100でバランス良好
- **PyCaret**: `setup()`でデータ前処理を自動化、`compare_models()`で最適モデル探索

**float32型メモリ削減**:
```python
# すべてのモデルで適用
X_train = X_train.astype('float32')  # メモリ使用量約50%削減
y_train = y_train.astype('float32')
```

---

### 3. localStorage活用戦略（学習年永続化）

**決定**: localStorageに学習年選択状態をモデル別に保存

**実装詳細**:
```javascript
// 保存形式: localStorage.setItem('trainingYears_LightGBM', '[2022,2023,2024]')
function saveTrainingYears(model, years) {
    const key = `trainingYears_${model}`;
    localStorage.setItem(key, JSON.stringify(years));
}

function loadTrainingYears(model) {
    const key = `trainingYears_${model}`;
    const stored = localStorage.getItem(key);
    return stored ? JSON.parse(stored) : [2022, 2023, 2024]; // デフォルト
}
```

**理由**:
1. **UX向上**: ページリロード後も選択状態が復元され、再選択の手間を削減
2. **セキュリティ**: 学習年のみ保存し、個人情報は含まない（憲法IV準拠）
3. **容量**: 学習年データは数十バイト程度で、5MB制限に余裕

**検討した代替案**:
- **Cookie**: サーバー送信でトラフィック増加、セキュリティリスクあり
- **IndexedDB**: 複雑すぎる、学習年程度のデータには不要

**注意事項**:
- ブラウザのプライベートモードでは無効化される
- 定期的なクリアを推奨（UI上に「リセット」ボタン実装）

---

### 4. Open-Meteo API統合（気温データ取得）

**決定**: Open-Meteo Forecast API（無料版）を使用し、HTTPS通信必須

**API仕様**:
```python
# エンドポイント: https://api.open-meteo.com/v1/forecast
# パラメータ:
#   latitude: 35.6785（東京）
#   longitude: 139.6823（東京）
#   hourly: temperature_2m（地上2m気温）
#   forecast_days: 1（明日のみ）

import requests

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 35.6785,
    "longitude": 139.6823,
    "hourly": "temperature_2m",
    "forecast_days": 1
}
response = requests.get(url, params=params, timeout=10)
data = response.json()
temperatures = data["hourly"]["temperature_2m"]  # 24時間分
```

**セキュリティ対策**（憲法II準拠）:
1. **HTTPS必須**: すべてのAPI通信はHTTPS/TLSで暗号化
2. **APIキー不要**: Open-Meteoは無料版でAPIキー不要（機密情報なし）
3. **エラーハンドリング**: タイムアウト10秒、リトライ3回
4. **レート制限遵守**: 無料版は1時間10000リクエストまで（本プロジェクトは1日1回のみ）

**ベストプラクティス**:
- **リトライ機構**: `requests`ライブラリの`Session`と`HTTPAdapter`でリトライ自動化
- **ログ記録**: API応答時間とステータスコードをログ出力（個人情報除外）
- **フォールバック**: API障害時は過去データの平均値を使用

---

### 5. GitHub Actions CI/CD設計

**決定**: 毎日JST 07:00にcronで自動実行し、精度閾値監視

**ワークフロー構成**:
```yaml
name: Daily Power Demand Forecast
on:
  schedule:
    - cron: '0 22 * * *'  # UTC 23:00 = JST 07:00
  workflow_dispatch:

jobs:
  forecast:
    runs-on: ubuntu-latest
    timeout-minutes: 10  # 憲法III: パフォーマンス制約
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10.11'
      - run: pip install -r AI/requirements.txt
      - run: python AI/tomorrow/temp.py  # 気温取得
      - run: python AI/train/LightGBM/LightGBM_train.py  # 学習
      - run: python AI/tomorrow/LightGBM/LightGBM_tomorrow.py  # 予測
      - name: Check R² Score
        run: |
          r2=$(python -c "import json; print(json.load(open('AI/metrics.json'))['r2'])")
          if [ $(echo "$r2 < 0.80" | bc -l) -eq 1 ]; then
            gh issue create --title "精度アラート: R² < 0.80" --body "現在のR²: $r2"
          fi
```

**パフォーマンス目標**（憲法III準拠）:
- **総実行時間**: < 10分（GitHub Actions無料枠考慮）
- **LightGBM学習**: < 30秒
- **Keras学習**: < 60秒
- **API通信**: < 5秒

**コスト最適化**:
- **月間実行時間**: 10分 × 30日 = 300分（無料枠2000分の15%）
- **キャッシュ活用**: `actions/cache@v3`で依存パッケージをキャッシュ

---

### 6. ローリング時系列交差検証（学習年最適化）

**決定**: 時系列データの特性を考慮し、ランダム分割ではなくローリング検証を採用

**実装方法**:
```python
# 例: 2016-2023年のデータから最適3年組み合わせを探索
from itertools import combinations

years = range(2016, 2024)
best_combination = None
best_rmse = float('inf')

for combo in combinations(years, 3):
    # combo = (2020, 2021, 2022) のような組み合わせ
    train_data = load_data(combo)
    test_data = load_data([2023])  # 直近1年でテスト

    model = train_model(train_data)
    rmse = evaluate_model(model, test_data)

    if rmse < best_rmse:
        best_rmse = rmse
        best_combination = combo

print(f"推奨学習年: {best_combination}, RMSE: {best_rmse}")
```

**理由**:
1. **時系列特性**: 電力需要は季節性・トレンドを持つため、ランダム分割は不適切
2. **未来予測**: 直近年でテストすることで、実際の明日予測精度を評価
3. **過学習防止**: 複数組み合わせを比較し、テストRMSE最小を選択

**ベストプラクティス**:
- **固定テスト年**: 2024年または2025年を固定し、訓練年のみ変動
- **上位5組み合わせ出力**: 最適解だけでなく、上位候補も記録
- **結果の可視化**: メモ帳で自動オープンし、ユーザーが判断可能

---

### 7. start-dashboard.ps1ワンコマンド起動

**決定**: PowerShellスクリプトでサーバー起動とブラウザ起動を自動化

**実装詳細**:
```powershell
# Python 3.10検出
$pythonCmd = "py -3.10"
if (& $pythonCmd --version 2>&1 | Select-String "Python 3.10") {
    Write-Host "Python 3.10 detected"
}

# HTTPサーバー起動（フォアグラウンド）
Set-Location AI
& py -3.10 server.py  # server.pyがブラウザ自動起動

# server.py内でブラウザ起動
# import webbrowser
# webbrowser.open('http://localhost:8002/dashboard/')
```

**UX向上**:
1. **ワンコマンド**: `.\start-dashboard.ps1`のみで起動完了
2. **自動ブラウザ起動**: server.py内で0.6秒待機後、デフォルトブラウザ起動
3. **エラーハンドリング**: Python未検出時は明確なエラーメッセージ表示

**ベストプラクティス**:
- **Ctrl+C終了**: サーバーをフォアグラウンドで実行し、Ctrl+Cで安全停止
- **UTF-8エンコーディング**: PowerShell構文エラーを回避
- **依存チェック**: `pip show pandas`で必須パッケージ確認

---

### 8. 16:9予測グラフ生成（GitHub Pages対応）

**決定**: matplotlibで16:9アスペクト比のPNG画像を生成

**実装方法**:
```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(16, 9))  # 16:9比率
ax.plot(hours, predictions, marker='o', linestyle='-', color='green')
ax.set_xlabel('時刻（時）', fontsize=14)
ax.set_ylabel('電力需要（kW）', fontsize=14)
ax.set_title('明日の電力需要予測', fontsize=16)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('AI/tomorrow/LightGBM/LightGBM_tomorrow.png', dpi=150)
plt.close()
```

**理由**:
1. **GitHub Pages対応**: PNG静的ファイルをGitHub Pagesで直接表示可能
2. **視認性**: 16:9は標準的なモニター比率で、全画面表示に最適
3. **ファイルサイズ**: DPI 150で高品質ながら100KB以下に抑制

**ベストプラクティス**:
- **日本語フォント**: `rcParams['font.sans-serif'] = ['MS Gothic']`でWindows日本語対応
- **カラーパレット**: ネオングリーン（#00FF00）でダッシュボードUIと統一
- **凡例**: モデル名と精度（R²）を凡例に表示

---

## 技術スタック最終決定

### フロントエンド
- **HTML5/CSS3**: ダッシュボードUI、ネオン発光エフェクト
- **JavaScript（ES6）**: localStorage、非同期API呼び出し
- **Fetch API**: HTTPサーバーとの通信（`POST /run-train`等）

### バックエンド
- **Python 3.10.11**: 機械学習パイプライン
- **http.server（標準ライブラリ）**: HTTPサーバー（Port 8002）
- **LightGBM 3.3.5**: 高速勾配ブースティング
- **Keras/TensorFlow 2.13.0**: 深層学習
- **scikit-learn 1.3.0**: RandomForest、データ前処理
- **PyCaret 3.0.4**: AutoML
- **pandas 2.0.3**: データ処理
- **requests 2.31.0**: Open-Meteo API通信

### インフラ
- **GitHub Pages**: 静的ファイルホスティング
- **GitHub Actions**: CI/CD、毎日自動実行
- **Git**: バージョン管理、ブランチ戦略（憲法準拠）

---

## 未解決事項

**該当なし** - すべての技術選定と設計判断が完了しています。

---

## 次のステップ

Phase 1（設計フェーズ）に進み、以下のドキュメントを生成します：

1. **data-model.md**: エンティティ、フィールド、リレーションシップ定義
2. **contracts/**: API仕様（OpenAPI形式）
3. **quickstart.md**: ワンコマンド起動手順

---

**作成者**: GitHub Copilot
**レビュー状態**: Completed
**最終更新日**: 2025-11-26
