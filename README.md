# Power-Demand-Forecast

[![Python](https://img.shields.io/badge/Python-3.10.11-blue)](https://www.python.org/)
[![LightGBM](https://img.shields.io/badge/LightGBM-4.5.0-green)](https://lightgbm.readthedocs.io/)
[![Keras](https://img.shields.io/badge/Keras-2.15.0-red)](https://keras.io/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com/J1921604/Power-Demand-Forecast/releases/tag/v1.0.0)

機械学習モデルを用いた電力需要予測システム | GitHub Actions自動更新 | Open-Meteo API連携

**🌐 Live Demo**: https://j1921604.github.io/Power-Demand-Forecast/
**📊 GitHub Actions**: [ワークフロー実行状況](https://github.com/J1921604/Power-Demand-Forecast/actions)
**📦 最新リリース**: [v1.0.0](https://github.com/J1921604/Power-Demand-Forecast/releases/tag/v1.0.0)
**最終更新**: 2025年11月26日

---

## 📋 目次

- [概要](#概要)
- [主要機能](#主要機能)
- [技術スタック](#技術スタック)
- [クイックスタート](#クイックスタート)
- [開発環境セットアップ](#開発環境セットアップ)
- [使い方](#使い方)
- [プロジェクト構造](#プロジェクト構造)
- [デプロイ](#デプロイ)
- [開発ガイド](#開発ガイド)
- [トラブルシューティング](#トラブルシューティング)
- [ライセンス](#ライセンス)

---

## 概要

Power-Demand-Forecast は、複数の機械学習モデルを用いて電力需要を予測するシステムです。
GitHub Actionsによる完全自動化、Open-Meteo APIからのリアルタイム気温データ取得により、毎日自動で予測を更新します。

### 🎯 プロジェクトの目的

- 複数の機械学習モデル（LightGBM、Keras、RandomForest、PyCaret）による電力需要予測
- Open-Meteo APIを活用したリアルタイム気温データ取得
- GitHub ActionsによるCI/CDパイプラインの完全自動化
- GitHub Pagesでの予測結果の可視化と公開
- 組み合わせ検証機能による最適学習年の自動探索

---

## 主要機能

### ✅ コア機能

- **4つの機械学習モデル**

  - LightGBM: 勾配ブースティング（推奨、高速・高精度）
  - Keras: 深層学習ニューラルネットワーク
  - RandomForest: ランダムフォレスト
  - PyCaret: AutoML自動最適化
- **組み合わせ検証機能（v3.0新機能）**

  - ローリング時系列交差検証
  - 最適学習年組み合わせ自動探索
  - 上位5組み合わせ表示
  - 2025年予測推奨組み合わせ提示
- **Webダッシュボード**

  - ブラウザ操作による直感的UI
  - リアルタイムグラフ表示（16:9）
  - RMSE/R²/MAE自動計算・表示
  - localStorage学習年記憶機能
  - **現在選択中の学習年をリアルタイム表示**
- **データ永続化**

  - localStorageによる学習年自動保存
  - モデル別独立記憶
  - ページリロード後も自動復元
  - **デフォルト学習年: 2022, 2023, 2024**（初回起動時）

---

## 技術スタック

### Python環境

| 技術         | バージョン | 用途               |
| ------------ | ---------- | ------------------ |
| Python       | 3.10.11    | 実行環境           |
| LightGBM     | 4.5.0      | 勾配ブースティング |
| Keras        | 2.15.0     | 深層学習           |
| scikit-learn | 1.3.2      | 機械学習           |
| PyCaret      | 3.0.4      | AutoML             |
| pandas       | 2.1.4      | データ処理         |
| matplotlib   | 3.8.2      | グラフ描画         |

### フロントエンド

| 技術       | バージョン | 用途             |
| ---------- | ---------- | ---------------- |
| HTML5      | -          | ページ構造       |
| CSS3       | -          | スタイリング     |
| JavaScript | ES2022     | インタラクション |

### CI/CD

| 技術           | 用途                   | 設定                                                        |
| -------------- | ---------------------- | ----------------------------------------------------------- |
| GitHub Actions | 自動ビルド・デプロイ   | Python 3.10.11, 学習年: 2022,2023,2024 (環境変数で一括管理) |
| GitHub Pages   | 静的サイトホスティング | https://j1921604.github.io/Power-Demand-Forecast/           |

---

## クイックスタート

### 前提条件

- **Python 3.10.11**: 必須（他のバージョンは非対応）
- pipインストール済み
- GitHubアカウント作成済み

**環境確認スクリプト**を実行して、Python 3.10.11が正しくインストールされているか確認できます：

```powershell
# Python環境確認（プロジェクトルートで実行）
.\.github\scripts\check-python.ps1

# 詳細モード
.\.github\scripts\check-python.ps1 -Verbose
```

スクリプトが以下を自動確認します：

- ✅ Python 3.10.11の検出
- ✅ 実行可能パスの確認
- ✅ requirements.txtの全パッケージインストール状況
- ✅ 重要モジュール（pandas、numpy、sklearn、lightgbm、tensorflow、pycaret）のインポート確認

### 5分でデプロイ

#### ステップ1: リポジトリクローン

```bash
git clone https://github.com/J1921604/Power-Demand-Forecast.git
cd Power-Demand-Forecast
```

#### ステップ2: Python環境確認

```powershell
# Python 3.10.11環境確認
.\.github\scripts\check-python.ps1
```

**Python 3.10.11がない場合**:

1. [Python 3.10.11をダウンロード](https://www.python.org/downloads/release/python-31011/)
2. インストーラー実行時に「**Add Python to PATH**」をチェック
3. 確認: `py -3.10 --version`

#### ステップ3: 依存関係インストール

```powershell
# プロジェクトルートで実行（推奨: .venv）
py -3.10 -m venv .venv
.venv\Scripts\Activate.ps1

# 依存関係インストール（requirementsはAI/配下）
py -3.10 -m pip install -r AI\requirements.txt
```

#### ステップ4: ローカルダッシュボード起動

**方法1: ワンコマンド起動（推奨）**

```powershell
# プロジェクトルートで実行
.\start-dashboard.ps1
```

自動的に以下が実行されます：

- Python 3.10検出
- 依存パッケージチェック
- HTTPサーバー起動（ポート8002）
- ブラウザ自動起動（http://localhost:8002/dashboard/）

**方法2: 手動起動**

```bash
# HTTPサーバー起動
cd AI
py -3.10 server.py

# ブラウザ自動起動（http://localhost:8002/dashboard/）
```

#### ステップ5: GitHub Pages設定（初回のみ）

**✅ 正しい設定**: `GitHub Actions` (Source) を選択してください。

1. リポジトリの **Settings** → **Pages** を開く
2. **Source**: 「**GitHub Actions**」を選択
3. **自動で更新される**

**注意**: 「Deploy from a branch」設定は使用しません。GitHub Actions ワークフローが自動的にデプロイを行います。

#### ステップ5: デプロイ実行

```bash
# mainブランチへプッシュ
git add .
git commit -m "deploy: Initial release"
git push origin main
```

#### ステップ6: ワークフロー手動実行（任意）

**注意**: ワークフローは **毎日 JST 07:00 に Cron トリガーで自動実行**されるため、手動実行は任意です。

1. https://github.com/J1921604/Power-Demand-Forecast/actions を開く
2. 左側で「Daily Power Demand Forecast」を選択
3. 右上の「Run workflow」→ 「Run workflow」をクリック
4. ワークフロー実行完了を待つ（約5-10分）

#### ステップ7: 公開サイトアクセス

```
https://j1921604.github.io/Power-Demand-Forecast/
```

✅ 4モデルの予測グラフと精度指標が表示されれば成功!

---

## 開発環境セットアップ

### VS Codeでフォルダを開く

1. VS Codeを起動
2. `Ctrl + K, Ctrl + O` または「ファイル」→「フォルダーを開く」
3. プロジェクトルートを開く

### PowerShellターミナルを開く

1. VS Codeで `Ctrl + Shift + P`
2. 「Terminal: Create New Terminal」を選択

### Python環境設定

```powershell
# Python バージョン確認（3.10.11必須）
py -3.10 --version

# 仮想環境作成
py -3.10 -m venv .venv

# 仮想環境有効化
.venv\Scripts\Activate.ps1

# 仮想環境Python確認
.venv\Scripts\python.exe --version
```

### VS Code Pythonインタープリター選択

1. `Ctrl+Shift+P`でコマンドパレット
2. 「Python: Select Interpreter」と入力
3. `.venv\Scripts\python.exe` を選択

### 依存関係インストール

```powershell
cd AI
pip install -r requirements.txt
```

---

## 使い方

### ワンコマンド起動（最速）

```powershell
# プロジェクトルートで実行
.\start-dashboard.ps1
```

自動的に以下が実行されます：

- Python 3.10検出・バージョン確認
- 依存パッケージチェック
- HTTPサーバー起動（http://localhost:8002/）
- ブラウザ自動起動
- 終了: Ctrl+C

---

### 組み合わせ検証機能（推奨・初心者向け）

#### Webダッシュボード経由

**方法1: ワンコマンド起動**

```powershell
.\start-dashboard.ps1
```

**方法2: 手動起動**

```powershell
# HTTPサーバー起動
cd AI
py -3.10 server.py
# ブラウザ自動起動: http://localhost:8002/
```

1. モデル選択（例: [LightGBM]ボタン）
2. [組み合わせ検証シミュレーション]ボタンクリック
3. 実行中: マゼンタ系発光アニメーション（約5分）
4. 結果自動表示: テキストファイル自動生成・メモ帳オープン
5. 推奨組み合わせ確認（例: 2022,2023,2024）
6. 推奨年を選択（例: [2022][2023][2024]ボタンクリック）
7. [データ処理]ボタン → 実行完了待ち
8. [学習]ボタン → 実行完了待ち（緑ネオン発光）
9. 結果自動表示: RMSE/R²/MAE、グラフ（16:9）

#### CLI経由

```powershell
cd AI

# LightGBM組み合わせ検証（約5分）
py -3.10 train\LightGBM\LightGBM_optimize_years.py

# 結果確認（メモ帳自動オープン）
# 推奨組み合わせで学習実行
$env:AI_TARGET_YEARS = "2022,2023,2024"
py -3.10 data\data.py
py -3.10 train\LightGBM\LightGBM_train.py
```

### Webダッシュボード操作（日常運用）

1. **モデル選択**: [LightGBM][Keras][PyCaret][RandomForest]
2. **学習年選択**: 年ボタンクリック（複数選択可）
3. **データ処理**: [データ処理]ボタン（学習年変更時のみ）
4. **モデル学習**: [学習]ボタン → RMSE/R²/MAE表示
5. **明日予測**: [最新データ取得]→[予測]ボタン → グラフ表示

### localStorage機能

- **自動保存**: 学習年ボタンクリック時に即座保存
- **モデル別記憶**: 各モデルで独立した学習年を記憶
- **自動復元**: ページリロード時に自動復元
- **視覚的一貫性**: ボタンの光るエフェクトも完全保持

---

## プロジェクト構造

```
Power-Demand-Forecast/
├── .github/
│   └── workflows/
│       └── daily-forecast.yml    # GitHub Actions自動実行
├── AI/
│   ├── calculate_metrics.py      # メトリクス計算
│   ├── generate_metrics.py       # メトリクス生成
│   ├── server.py                 # HTTPサーバー
│   ├── requirements.txt          # 依存パッケージ
│   ├── metrics.json              # 精度指標JSON
│   ├── dashboard/
│   │   └── index.html            # Webダッシュボード
│   ├── data/
│   │   ├── data.py               # データ処理
│   │   ├── juyo-YYYY.csv         # 電力需要データ (2016-2026)
│   │   ├── temperature-YYYY.csv  # 気温データ (2016-2024)
│   │   ├── X.csv, Y.csv          # 統合データ
│   │   ├── Xtrain.csv, Ytrain.csv # 訓練データ
│   │   └── Xtest.csv, Ytest.csv  # テストデータ
│   ├── train/
│   │   ├── LightGBM/
│   │   │   ├── LightGBM_train.py         # 学習
│   │   │   ├── LightGBM_optimize_years.py # 組み合わせ検証
│   │   │   ├── LightGBM_model.sav        # 学習済みモデル
│   │   │   └── LightGBM_Ypred.csv        # 予測結果
│   │   ├── Keras/
│   │   │   ├── Keras_train.py
│   │   │   ├── Keras_optimize_years.py
│   │   │   └── Keras_model.h5
│   │   ├── RandomForest/
│   │   │   ├── RandomForest_train.py
│   │   │   ├── RandomForest_optimize_years.py
│   │   │   └── RandomForest_model.sav
│   │   └── Pycaret/
│   │       ├── Pycaret_train.py
│   │       ├── Pycaret_optimize_years.py
│   │       └── Pycaret_Ypred.csv
│   └── tomorrow/
│       ├── data.py                # 明日予測用データ処理
│       ├── temp.py                # Open-Meteo API気温取得
│       ├── tomorrow.csv           # 明日の気温データ
│       ├── Ytest.csv              # テストデータ
│       ├── LightGBM/
│       │   ├── LightGBM_tomorrow.py  # 予測実行
│       │   ├── LightGBM_tomorrow.csv # 予測結果CSV
│       │   └── LightGBM_tomorrow.png # 予測グラフ
│       ├── Keras/
│       │   ├── Keras_tomorrow.py
│       │   ├── Keras_tomorrow.csv
│       │   └── Keras_tomorrow.png
│       ├── RandomForest/
│       │   ├── RandomForest_tomorrow.py
│       │   ├── RandomForest_tomorrow.csv
│       │   └── RandomForest_tomorrow.png
│       └── Pycaret/
│           ├── Pycaret_tomorrow.py
│           ├── Pycaret_tomorrow.csv
│           └── Pycaret_tomorrow.png
├── docs/
│   ├── DEPLOY_GUIDE.md           # デプロイガイド
│   ├── GITHUB_ACTIONS_TEST.md    # GitHub Actions手動実行検証手順
│   ├── IMPLEMENTATION_REPORT.md  # 実装完了レポート
│   ├── PULL_REQUEST_TEMPLATE.md  # Pull Requestテンプレート
│   ├── RELEASE_NOTES_v1.0.0.md   # v1.0.0リリースノート
│   ├── TESTING_GUIDE.md          # 最終検証手順書
│   ├── 使用手順書.md              # ローカル環境での使用手順書
│   └── 完全仕様書.md              # 完全仕様書
├── index.html                    # GitHub Pages静的ページ
└── README.md                     # 本ドキュメント
```

---

## デプロイ

### GitHub Actions自動デプロイ

- **トリガー**: mainブランチへのPush、毎日JST 07:00（Cron）、手動実行
- **Python バージョン**: 3.10.11
- **学習年設定**: 2022,2023,2024 (環境変数 `AI_TARGET_YEARS` で一括管理)
- **実行内容**: 気温取得 → 最新実績データ更新 → データ処理 → モデル訓練 → 予測 → GitHub Pages更新
- **所要時間**: 約5-10分
- **R² < 0.8検出時**: GitHub Issue自動作成

### 学習年の変更方法

`.github/workflows/daily-forecast.yml` の環境変数を変更:

```yaml
jobs:
  forecast:
    runs-on: ubuntu-latest
    env:
      AI_TARGET_YEARS: '2022,2023,2024'  # ← ここを変更
      PYTHONIOENCODING: 'utf-8'
```

### ローカルプレビュー

```powershell
cd AI
py -3.10 server.py
# http://localhost:8002/
```

---

## 開発ガイド

### 利用可能なコマンド

```bash
# HTTPサーバー起動
cd AI
py -3.10 server.py

# 組み合わせ検証
py -3.10 train\LightGBM\LightGBM_optimize_years.py

# データ処理
py -3.10 data\data.py

# 翌日予測用データ更新（TEPCO実績）
py -3.10 tomorrow\data.py

# モデル訓練
py -3.10 train\LightGBM\LightGBM_train.py

# 明日予測
py -3.10 tomorrow\LightGBM\LightGBM_tomorrow.py

# メトリクス生成
py -3.10 generate_metrics.py
```

### コーディング規約

- **Python**: PEP 8準拠
- **インデント**: 4スペース
- **文字コード**: UTF-8
- **改行コード**: LF

---

## トラブルシューティング

### データ時刻の並び・重複問題

**症状**: 日時の並びが崩れてR²が低下する、または同時刻の重複行が混在する

**対処**:

- `AI/tomorrow/data.py` の **最新データ取得** で、`juyo-2026.csv` を **日時型でソート** し、`DATE/TIME` を **ゼロパディング（例: 2026/02/01, 00:00）** に正規化
- 同一日時の重複行は **最新優先で1行のみ残す**（`download_and_extract_latest_data`）
- `AI/data/data.py` でも **日時インデックスのソート** と **重複時刻の除去（先頭採用）** を実施

### Python依存関係エラー

```powershell
# pipアップグレード
py -3.10 -m pip install --upgrade pip

# 依存関係再インストール
pip install -r AI/requirements.txt

# 個別パッケージ確認
pip list | Select-String "lightgbm|keras|pandas"
```

### グラフが表示されない

```powershell
# 予測画像確認
Get-ChildItem -Recurse -Filter *.png AI/tomorrow/

# ローカルで予測実行
cd AI
py -3.10 tomorrow\LightGBM\LightGBM_tomorrow.py
```

### GitHub Actions失敗

**問題1: ワークフローが全く実行されない**

1. **Settings → Actions → General** で Actions が有効か確認
2. **Settings → Pages → Source** が「**GitHub Actions**」になっているか確認
   - 「Deploy from a branch」になっていたら「GitHub Actions」に変更
3. 手動トリガー: https://github.com/J1921604/Power-Demand-Forecast/actions → Run workflow

**問題2: ワークフローは実行されるがデプロイ失敗**

1. Settings → Pages → Source: GitHub Actions を確認
2. Actionsログで詳細エラー確認
3. ローカルで同じコマンド実行してエラー特定

**問題3: R² < 0.8（精度閾値違反）**

**原因**:

- モデルが適切な学習年で訓練されていない
- 翌日予測用データの整合性崩れ（`period_info.json` の参照先違い、`tomorrow.csv` の列順違い など）

**解決方法**:

1. **環境変数 `AI_TARGET_YEARS` を設定してモデルを再学習**

   ```powershell
   cd AI
   $env:AI_TARGET_YEARS = "2022,2023,2024"  # 推奨組み合わせ

   # データ前処理（指定された年のみ使用）
   py -3.10 data\data.py

   # 全モデルの再学習
   py -3.10 train\LightGBM\LightGBM_train.py      # R²=0.92以上期待
   py -3.10 train\Keras\Keras_train.py            # R²=0.90以上期待
   py -3.10 train\RandomForest\RandomForest_train.py  # R²=0.90以上期待
   py -3.10 train\Pycaret\Pycaret_train.py        # R²=0.90以上期待
   ```
2. **最新データで予測を実行**

   ```powershell
   # 最新の電力実績と気温データを取得
   py -3.10 tomorrow\data.py
   py -3.10 tomorrow\temp.py

   # 予測実行
   py -3.10 tomorrow\LightGBM\LightGBM_tomorrow.py
   ```
3. **データ整合性の確認**

   `tomorrow/Ytest.csv` の行数が **168行**（7日 × 24時間）であることを確認:

   ```powershell
   (Import-Csv AI/tomorrow/Ytest.csv).Count
   ```

   `tomorrow/tomorrow.csv` の行数が **336行**（過去7日+未来7日 × 24時間）であることを確認:

   ```powershell
   (Import-Csv AI/tomorrow/tomorrow.csv).Count
   ```

  `tomorrow/tomorrow.csv` の列順が **MONTH,WEEK,HOUR,TEMP** であることを確認（重要）:

```powershell
  (Import-Csv AI/tomorrow/tomorrow.csv | Select-Object -First 1 | Get-Member -MemberType NoteProperty).Name
```

  `tomorrow/period_info.json` が存在し、最新のYtest期間（例: 2026-01-07 00:00:00〜）で保存されていることを確認:

```powershell
  Get-Content AI/tomorrow/period_info.json
```

4. **GitHub Actionsでの対処**

   `.github/workflows/daily-forecast.yml` の環境変数を確認:

   ```yaml
   env:
     AI_TARGET_YEARS: '2022,2023,2024'  # 推奨組み合わせ
   ```

   手動実行で精度を確認:

   - https://github.com/J1921604/Power-Demand-Forecast/actions
   - "Run workflow" をクリック
   - ワークフロー完了後、Actionsログで `最終結果 - RMSE: XXX kW, R2: X.XXXX, MAE: XXX kW` を確認

**問題4: メトリクスがGitHub Pagesと一致しない**

**症状**: ローカルの評価スコアとGitHub Pagesの表示が一致しない

**解決手順**:

1. ローカルでメトリクスを再生成

  ```powershell
  C:\Users\h-ham\spec-kit\Power-Demand-Forecast\.venv\Scripts\python.exe AI\generate_metrics.py
  ```

  **補足**: 明日予測は常に再生成します（既存の予測CSVは再利用しません）。

2. 出力が以下と一致することを確認

  ```
  Metrics Aggregation for GitHub Pages
  ============================================================
  ✓ LightGBM: RMSE=226.351, R2=0.8134, MAE=182.596
  ✓ Keras: RMSE=209.131, R2=0.8407, MAE=163.672
  ✓ RandomForest: RMSE=220.661, R2=0.8227, MAE=177.785
  ✓ Pycaret: RMSE=226.942, R2=0.8124, MAE=181.483
  ```

3. `AI/metrics.json` が更新されたことを確認し、GitHub Pagesを再デプロイ

**期待される結果（目安）**:

- 学習（train/*_train.py）: LightGBM R² ≥ 0.92 / Keras・RandomForest・Pycaret R² ≥ 0.90
- 翌日予測（tomorrow/*_tomorrow.py のバックテスト部）: R² ≥ 0.80（ワークフロー閾値）

---

## ライセンス

MIT License

---

## リンク

- **Live Demo**: https://j1921604.github.io/Power-Demand-Forecast/
- **GitHub Actions**: https://github.com/J1921604/Power-Demand-Forecast/actions
- **ローカル環境での使用手順書**: [使用手順書.md](https://github.com/J1921604/Power-Demand-Forecast/blob/main/docs/使用手順書.md)
- **デプロイガイド**: [DEPLOY_GUIDE.md](https://github.com/J1921604/Power-Demand-Forecast/blob/main/docs/DEPLOY_GUIDE.md)
- **完全仕様書**: [完全仕様書.md](https://github.com/J1921604/Power-Demand-Forecast/blob/main/docs/完全仕様書.md)
- **GitHub Actions検証手順**: [GITHUB_ACTIONS_TEST.md](https://github.com/J1921604/Power-Demand-Forecast/blob/main/docs/GITHUB_ACTIONS_TEST.md)
- **最終検証手順書**: [TESTING_GUIDE.md](https://github.com/J1921604/Power-Demand-Forecast/blob/main/docs/TESTING_GUIDE.md)
- **実装完了レポート**: [IMPLEMENTATION_REPORT.md](https://github.com/J1921604/Power-Demand-Forecast/blob/main/docs/IMPLEMENTATION_REPORT.md)
- **v1.0.0リリースノート**: [RELEASE_NOTES_v1.0.0.md](https://github.com/J1921604/Power-Demand-Forecast/blob/main/docs/RELEASE_NOTES_v1.0.0.md)
