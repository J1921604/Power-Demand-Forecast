# クイックスタート: 電力需要予測システム

**Phase**: 1（設計）
**作成日**: 2025-11-26
**バージョン**: 1.0.0
**Plan**: [plan.md](plan.md)

## 概要

このガイドは、電力需要予測システムを**最短5分**でローカル環境にセットアップし、ダッシュボードで機械学習モデルを実行するための手順を提供します。

---

## 前提条件

以下のソフトウェアがインストールされていることを確認してください：

- [x] **Python 3.10.11**（固定バージョン）
- [x] **Git**（リポジトリクローン用）
- [x] **PowerShell**（Windows環境、start-dashboard.ps1実行用）
- [x] **ブラウザ**（Chrome/Firefox/Edge）

---

## 🚀 ワンコマンド起動（推奨）

### ステップ 1: リポジトリクローン

```powershell
git clone https://github.com/J1921604/Power-Demand-Forecast.git
cd Power-Demand-Forecast
```

### ステップ 2: ワンコマンド起動

```powershell
.\start-dashboard.ps1
```

**実行内容**:
1. Python 3.10.11の検出
2. 依存パッケージの確認（`AI/requirements.txt`）
3. HTTPサーバー起動（`http://localhost:8002`）
4. ブラウザ自動起動（`http://localhost:8002/dashboard/`）

**起動完了**: ブラウザでダッシュボードが自動オープンされます（約3秒）。

---

## 📋 手動セットアップ（詳細手順）

ワンコマンド起動が失敗した場合、以下の手順で手動セットアップしてください。

### ステップ 1: Python 3.10.11のインストール

**Windowsの場合**:
```powershell
# Python 3.10.11をダウンロード
# https://www.python.org/downloads/release/python-31011/
# インストーラーを実行し、「Add Python to PATH」をチェック

# 確認
py -3.10 --version
# 出力: Python 3.10.11
```

**macOS/Linuxの場合**:
```bash
# pyenvを使用
pyenv install 3.10.11
pyenv local 3.10.11

# 確認
python --version
# 出力: Python 3.10.11
```

### ステップ 2: 依存パッケージのインストール

```powershell
cd AI
py -3.10 -m pip install -r requirements.txt
```

**インストールされるパッケージ**:
- LightGBM 3.3.5
- TensorFlow 2.13.0
- scikit-learn 1.3.0
- PyCaret 3.0.4
- pandas 2.0.3
- matplotlib 3.7.2
- requests 2.31.0

**所要時間**: 約3-5分（ネットワーク速度に依存）

### ステップ 3: HTTPサーバー起動

```powershell
# AIディレクトリから実行
cd AI
py -3.10 server.py
```

**出力例**:
```
AI server running at http://localhost:8002/ (serving from C:\...\Power-Demand-Forecast)
```

**ブラウザ起動**: サーバー起動後、自動的にブラウザが開きます（約0.6秒後）。

### ステップ 4: ダッシュボードアクセス

ブラウザで以下のURLにアクセスします：

```
http://localhost:8002/dashboard/
```

**表示内容**:
- 4つのモデル選択ボタン（LightGBM、Keras、RandomForest、PyCaret）
- 学習年選択UI（2016-2024年）
- データ処理・学習・予測ボタン

---

## 🎯 基本的な使い方

### 1. データ処理と学習（LightGBM）

```mermaid
flowchart LR
    A[ダッシュボード<br/>アクセス] --> B[LightGBM<br/>選択]
    B --> C[学習年選択<br/>2022,2023,2024]
    C --> D[データ処理<br/>クリック]
    D --> E[学習<br/>クリック]
    E --> F[RMSE/R²/MAE<br/>表示]
```

**手順**:
1. **LightGBMボタン**をクリック
2. **2022、2023、2024年**をクリック選択（ネオングリーン発光）
3. **[データ処理]**ボタンをクリック
4. 完了メッセージを確認
5. **[学習]**ボタンをクリック
6. RMSE、R²、MAEが表示される（約30秒）

**期待結果**:
- RMSE: 約450-500
- R²: 0.85-0.90（> 0.80が目標）
- MAE: 約350-400

### 2. 明日予測の実行

```mermaid
flowchart LR
    A[学習完了] --> B[最新データ取得<br/>クリック]
    B --> C[Open-Meteo API<br/>気温取得]
    C --> D[予測<br/>クリック]
    D --> E[16:9グラフ<br/>表示]
```

**手順**:
1. モデル学習完了後、**[最新データ取得]**ボタンをクリック
2. Open-Meteo APIから明日の気温データを取得（約3秒）
3. **[予測]**ボタンをクリック
4. 明日24時間の電力需要予測グラフ（16:9）が表示される

**出力ファイル**:
- `AI/tomorrow/LightGBM/LightGBM_tomorrow.csv`
- `AI/tomorrow/LightGBM/LightGBM_tomorrow.png`（16:9比率）

### 3. 組み合わせ検証（学習年最適化）

**手順**:
1. **[組み合わせ検証シミュレーション]**ボタンをクリック
2. ローリング時系列交差検証が開始される（約5分）
3. メモ帳で結果ファイルが自動オープンされる

**結果ファイル**:
- `AI/train/LightGBM/2025-11-25_LightGBM_optimize_years.txt`
- 上位5組み合わせ（RMSE昇順）
- 2025年予測推奨組み合わせ

---

## 🛠️ トラブルシューティング

### 問題 1: Python 3.10が見つからない

**症状**:
```
Error: Python 3.10 not found.
```

**解決策**:
```powershell
# Python 3.10.11をインストール
# https://www.python.org/downloads/release/python-31011/

# 確認
py -3.10 --version
```

### 問題 2: 依存パッケージが不足

**症状**:
```
ModuleNotFoundError: No module named 'pandas'
```

**解決策**:
```powershell
cd AI
py -3.10 -m pip install -r requirements.txt
```

### 問題 3: ポート8002が使用中

**症状**:
```
OSError: [Errno 48] Address already in use
```

**解決策**:
```powershell
# 既存のserver.pyプロセスを終了
# Ctrl+Cでサーバー停止

# または、別のポートを使用
# AI/server.py内のPORT変数を変更
# PORT = 8003  # 例
```

### 問題 4: ブラウザが自動起動しない

**症状**: サーバー起動後、ブラウザが開かない

**解決策**:
```
手動でブラウザを開き、以下のURLにアクセス:
http://localhost:8002/dashboard/
```

### 問題 5: Open-Meteo API通信エラー

**症状**:
```
Error: Failed to fetch temperature data from Open-Meteo API
```

**解決策**:
1. ネットワーク接続を確認
2. HTTPSプロキシ設定を確認
3. Open-Meteo APIステータスを確認: https://open-meteo.com/

---

## 📊 パフォーマンス目標

| 項目 | 目標 | 実測例 |
|------|------|--------|
| **LightGBM学習時間** | < 30秒 | 約25秒 |
| **Keras学習時間** | < 60秒 | 約50秒 |
| **ダッシュボードAPI応答** | < 2秒 | 約1.5秒 |
| **R²スコア** | > 0.80 | 0.85-0.90 |
| **Open-Meteo API通信** | < 5秒 | 約3秒 |

---

## 🔒 セキュリティ確認

### ローカル環境のみ使用

**注意**: このシステムは`http://localhost:8002`でのみ動作します。外部ネットワークには公開されません。

### HTTPS通信

- Open-Meteo API通信は必ずHTTPS/TLS暗号化されます
- APIキーは不要（無料版）

### 個人情報

- localStorageには学習年選択状態のみ保存（個人情報なし）
- 電力需要データと気温データは公開データのみ

---

## 📖 次のステップ

### 1. GitHub Actions自動実行

詳細は`docs/DEPLOY_GUIDE.md`を参照してください。

**概要**:
- 毎日JST 07:00に自動実行
- LightGBMモデルで明日予測
- 精度R² < 0.80でIssue自動作成

### 2. GitHub Pagesデプロイ

**概要**:
- 予測グラフ（PNG）をGitHub Pagesで公開
- 静的ファイルのみホスティング

### 3. モデル精度向上

**改善手法**:
- 学習年の最適組み合わせを組み合わせ検証で探索
- ハイパーパラメータチューニング（GridSearchCV）
- 特徴量エンジニアリング（時間帯グループ、休日フラグ等）

---

## 🆘 サポート

### ドキュメント

- **完全仕様書**: [完全仕様書.md](https://github.com/J1921604/Power-Demand-Forecast/blob/main/docs/完全仕様書.md)
- **使用手順書**: [使用手順書.md](https://github.com/J1921604/Power-Demand-Forecast/blob/main/docs/使用手順書.md)
- **デプロイガイド**: [DEPLOY_GUIDE.md](https://github.com/J1921604/Power-Demand-Forecast/blob/main/docs/DEPLOY_GUIDE.md)

### GitHub Issues

問題や質問がある場合は、GitHubリポジトリでIssueを作成してください：

```
https://github.com/J1921604/Power-Demand-Forecast/issues
```

---

**作成者**: GitHub Copilot
**レビュー状態**: Completed
**最終更新日**: 2025-11-26
