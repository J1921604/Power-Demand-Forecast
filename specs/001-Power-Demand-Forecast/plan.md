# 実装計画書: 電力需要予測システム

**ブランチ**: `001-Power-Demand-Forecast` | **作成日**: 2025年11月26日 | **仕様書**: [spec.md](https://github.com/J1921604/Power-Demand-Forecast/blob/main/specs/001-Power-Demand-Forecast/spec.md)
**入力**: 機能仕様書 `https://github.com/J1921604/Power-Demand-Forecast/blob/main/specs/001-Power-Demand-Forecast/spec.md`
**バージョン**: 1.0.0
**リポジトリ**: https://github.com/J1921604/Power-Demand-Forecast

**Note**: この計画書は `/speckit.plan`コマンドにより生成されました。実行ワークフローは `.specify/templates/commands/plan.md`を参照してください。

## 概要

電力需要予測システムは、複数の機械学習モデル（LightGBM、Keras、RandomForest、PyCaret）を用いて翌日の電力需要を予測するシステムです。Open-Meteo APIから最新の気温データを取得し、GitHub Actionsによる完全自動化により、毎日JST 07:00に自動で予測を更新してGitHub Pagesで公開します。

**主要要件:**

- 4つの機械学習モデルによる電力需要予測
- Open-Meteo APIからのリアルタイム気温データ取得
- GitHub ActionsによるCI/CDパイプライン完全自動化
- Webダッシュボードによる直感的UI操作
- R² < 0.8検出時の自動Issue作成
- ローリング時系列交差検証による最適学習年探索

## 技術コンテキスト

**言語/バージョン**: Python 3.10.11（標準実行環境）**主要依存関係**:

- LightGBM 4.5.0（勾配ブースティング）
- Keras 2.15.0（深層学習）
- scikit-learn 1.3.2（機械学習基盤）
- PyCaret 3.0.4（AutoML）
- pandas 2.1.4（データ処理）
- matplotlib 3.8.2（グラフ描画）

**ストレージ**:

- ローカルCSVファイル（電力需要・気温実績データ：2016-2025年）
- Gitリポジトリ（学習済みモデル：.sav/.h5形式、予測結果）

**テスト**:

- pytest（単体・統合・契約・E2E・パフォーマンステスト）
- GitHub Actions CI（全テスト自動実行）

**ターゲットプラットフォーム**:

- ローカル開発環境（Windows/Linux）
- GitHub Actions Ubuntu Latest
- GitHub Pages（静的サイトホスティング）

**プロジェクト種別**: Webアプリケーション + Python機械学習バックエンド

**パフォーマンス目標**:

- LightGBM訓練時間: ≤ 10秒
- 翌日予測実行時間: ≤ 30秒
- GitHub Actionsワークフロー実行時間: ≤ 10分
- Webダッシュボード初回表示速度: ≤ 2秒

**制約条件**:

- Python 3.10.11必須（他バージョン非対応）
- GitHub Pagesファイルサイズ制限（学習済みモデル < 50MB）
- Open-Meteo API無料枠レート制限（60リクエスト/分）
- GitHub Actions無料枠（月2000分）

**スケール/スコープ**:

- データ期間: 2016-2025年（10年分）
- 予測精度目標: R² ≥ 0.80, RMSE ≤ 500kW, MAE ≤ 400kW
- 自動デプロイ頻度: 毎日JST 07:00（Cron）

## 憲法チェック

*GATE: Phase 0リサーチ前に合格必須。Phase 1設計後に再チェック。*

### I. テスト駆動開発の徹底

✅ **合格**:

- 単体テスト（`tests/unit/`）、統合テスト（`tests/integration/`）、契約テスト（`tests/contract/`）、E2Eテスト（`tests/e2e/`）、パフォーマンステスト（`tests/performance/`）の4層構造を実装済み
- pytest実行確認: `pytest tests/ -v`
- GitHub ActionsでCI自動実行

**検証方法**:

- `pytest tests/ --cov=AI --cov-report=term`でカバレッジ80%以上を確認
- `.github/workflows/daily-forecast.yml`でテスト自動実行を確認

### II. セキュリティ要件の優先

✅ **合格**:

- Open-Meteo APIはHTTPS経由で通信（`AI/tomorrow/temp.py`）
- GitHub SecretsでAPIキー管理（将来的な有料API対応）
- 機密データの平文保存なし

**検証方法**:

- `grep -r "http://" AI/`で非HTTPSリクエストがないことを確認
- `.gitignore`に `.env`を含めることを確認

### III. パフォーマンス閾値の定量化

✅ **合格**:

- R² ≥ 0.80, RMSE ≤ 500kW, MAE ≤ 400kWを目標値として定義
- R² < 0.8検出時に自動でGitHub Issue作成（`.github/workflows/daily-forecast.yml`）
- パフォーマンステスト実装済み（`tests/performance/`）

**検証方法**:

- ワークフローログで精度指標を確認
- `python AI/generate_metrics.py`で `metrics.json`生成を確認

### IV. データ品質保証

✅ **合格**:

- 入力データの欠損値・異常値検証（`AI/data/data.py`）
- Open-Meteo APIリトライ機構実装（`AI/tomorrow/temp.py`）
- データ前処理パイプラインのログ出力

**検証方法**:

- `python AI/data/data.py`実行時のログで欠損値検証を確認
- APIリトライロジックのテスト実行

### V. バージョン管理とトレーサビリティ

✅ **合格**:

- 学習済みモデルファイル命名規則: `{model_name}_model.sav` / `{model_name}_model.h5`
- 予測結果CSV命名規則: `{model_name}_tomorrow.csv`
- 毎日の予測結果をGitリポジトリに自動コミット（ワークフロー内）

**検証方法**:

- `git log --oneline --grep="Update daily forecast"`で自動コミット履歴を確認
- モデルファイル名規則の遵守を目視確認

### VI. 自動化とCI/CDの徹底

✅ **合格**:

- GitHub Actions Cron設定: `0 22 * * *`（UTC 22:00 = JST 07:00）
- 完全自動化パイプライン（気温取得→訓練→予測→デプロイ）
- 手動実行オプション（`workflow_dispatch`）

**検証方法**:

- `.github/workflows/daily-forecast.yml`のCron設定を確認
- GitHub Actionsダッシュボードで自動実行履歴を確認

### VII. ドキュメントファーストの原則

✅ **合格**:

- 完全仕様書（`docs/完全仕様書.md`）
- デプロイガイド（`docs/DEPLOY_GUIDE.md`）
- README.md常時更新
- API仕様明記（Open-Meteo API）

**検証方法**:

- ドキュメントファイルの存在確認
- リンク切れチェック

---

**憲法チェック結果**: ✅ 全項目合格

## プロジェクト構造

### ドキュメント（本機能）

```text
specs/001-Power-Demand-Forecast/
├── plan.md              # 本ファイル（/speckit.planコマンド出力）
├── spec.md              # 機能仕様書
├── requirements.md      # 要件定義書
├── research.md          # Phase 0出力（/speckit.planコマンド）
├── data-model.md        # Phase 1出力（/speckit.planコマンド）
├── quickstart.md        # Phase 1出力（/speckit.planコマンド）
├── tasks.md             # Phase 2出力（/speckit.tasksコマンド）
└── contracts/           # Phase 1出力（/speckit.planコマンド）
    └── open-meteo-api.yaml  # Open-Meteo API OpenAPI仕様
```

### ソースコード（リポジトリルート）

```text
Power-Demand-Forecast/
├── .github/
│   └── workflows/
│       └── daily-forecast.yml    # GitHub Actions自動実行ワークフロー
├── .specify/
│   ├── memory/
│   │   └── constitution.md       # プロジェクト憲法
│   └── templates/
│       ├── plan-template.md
│       ├── spec-template.md
│       └── tasks-template.md
├── AI/
│   ├── calculate_metrics.py      # メトリクス計算
│   ├── generate_metrics.py       # メトリクス生成
│   ├── server.py                 # HTTPサーバー
│   ├── requirements.txt          # 依存パッケージ
│   ├── metrics.json              # 精度指標JSON
│   ├── dashboard/
│   │   └── index.html            # Webダッシュボード
│   ├── data/
│   │   ├── data.py               # データ前処理パイプライン
│   │   ├── juyo-2016.csv ~ juyo-2025.csv     # 電力需要データ
│   │   ├── temperature-2016.csv ~ temperature-2024.csv  # 気温データ
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
│   │   ├── RandomForest/
│   │   └── Pycaret/
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
│       ├── RandomForest/
│       └── Pycaret/
├── docs/
│   ├── 完全仕様書.md
│   ├── 使用手順書.md
│   ├── DEPLOY_GUIDE.md
│   ├── GITHUB_ACTIONS_TEST.md
│   ├── IMPLEMENTATION_REPORT.md
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── RELEASE_NOTES_v1.0.0.md
│   └── TESTING_GUIDE.md
├── specs/
│   └── 001-Power-Demand-Forecast/
│       ├── plan.md               # 本ファイル
│       ├── spec.md               # 機能仕様書
│       ├── requirements.md       # 要件定義書
│       ├── research.md           # リサーチ成果
│       ├── data-model.md         # データモデル仕様
│       ├── quickstart.md         # クイックスタート
│       ├── tasks.md              # 実装タスク
│       └── contracts/
│           └── open-meteo-api.yaml
├── tests/
│   ├── conftest.py
│   ├── contract/
│   │   └── test_api.py
│   ├── e2e/
│   │   ├── test_dashboard.py
│   │   └── test_optimize.py
│   ├── integration/
│   │   ├── test_metrics.py
│   │   └── test_rolling_cv.py
│   ├── performance/
│   │   ├── test_optimize_time.py
│   │   └── test_training_time.py
│   └── unit/
│       ├── test_data.py
│       └── test_optimize_years.py
├── index.html                    # GitHub Pages静的ページ
├── pytest.ini
├── README.md
└── start-dashboard.ps1           # ダッシュボード起動スクリプト
```

**構造決定**: Webアプリケーション + Python機械学習バックエンド

本プロジェクトは、以下の理由によりWebアプリケーション構造を採用しています:

1. **フロントエンド**: `AI/dashboard/index.html`（HTML5 + CSS3 + JavaScript ES2022）
2. **バックエンド**: `AI/`配下のPythonスクリプト群（データ処理・訓練・予測）
3. **HTTPサーバー**: `AI/server.py`（ローカル開発用、ポート8002）
4. **GitHub Pages**: 静的サイトホスティング（https://j1921604.github.io/Power-Demand-Forecast/）

この構造により、ローカル開発とGitHub Pages公開の両方をサポートしています。

## 複雑性追跡

> **憲法チェック違反がある場合のみ記入**

本プロジェクトは憲法チェックに全項目合格しているため、複雑性追跡は不要です。
