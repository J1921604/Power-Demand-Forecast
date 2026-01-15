# 要件定義書: 電力需要予測システム

**機能ブランチ**: `001-Power-Demand-Forecast`
**作成日**: 2025-11-26
**バージョン**: 1.0.0

---

## 1. 機能要件

### 1.1. モデル訓練機能

**FR-001**: システムは、LightGBM/Keras/RandomForest/PyCaretの4つの機械学習モデルで電力需要を予測できなければならない

- **詳細**: 各モデルは独立して訓練可能であり、ハイパーパラメータは事前定義される
- **入力**: 学習年（例: 2022,2023,2024）、電力需要データ（juyo-YYYY.csv）、気温データ（temperature-YYYY.csv）
- **出力**: 学習済みモデルファイル（.sav/.h5）、RMSE/R²/MAE精度指標、予測グラフPNG
- **検証**: pytest単体テストでモデル訓練後にRMSE≤500kW、R²≥0.80を確認

**FR-002**: システムは、環境変数AI_TARGET_YEARSで学習年を指定できなければならない

- **詳細**: カンマ区切りで複数年指定可能（例: "2022,2023,2024"）
- **入力**: 環境変数 `AI_TARGET_YEARS="2022,2023,2024"`
- **出力**: 指定した年のデータのみで訓練実行
- **検証**: 環境変数設定後、data.pyが指定年のみをロードすることをログで確認

---

### 1.2. 予測機能

**FR-003**: システムは、Open-Meteo APIから最新の気温データ（過去7日+未来7日）を取得できなければならない

- **詳細**: HTTP GETリクエストでJSON形式の気温データ（hourly.temperature_2m）を取得
- **APIエンドポイント**: `https://api.open-meteo.com/v1/forecast?latitude=35.6785&longitude=139.6823&hourly=temperature_2m&timezone=Asia%2FTokyo&past_days=7&forecast_days=7`
- **出力**: tomorrow.csv（336行: 過去7日×24時間 + 未来7日×24時間）
  - **特徴量列順**: `MONTH,WEEK,HOUR,TEMP`（学習時と同一）
- **検証**: tomorrow/temp.pyを実行し、tomorrow.csvに**336行**のデータが保存され、列が `MONTH,WEEK,HOUR,TEMP` の順になっていることを確認

**FR-004**: システムは、データ前処理パイプライン（data.py）で電力需要データと気温データを統合し、特徴量（MONTH/WEEK/HOUR/TEMP）を生成できなければならない

- **詳細**: pandas.DataFrameで時系列データを結合し、特徴量エンジニアリングを実行
- **入力**: juyo-YYYY.csv、temperature-YYYY.csv
- **出力**: X.csv（特徴量: MONTH/WEEK/HOUR/TEMP）、Y.csv（目的変数: KW）
- **検証**: data.pyを実行し、X.csvとY.csvが生成され、カラム数が正しいことを確認

**FR-005**: システムは、モデル訓練後にRMSE/R²/MAEの精度指標を計算し、予測グラフ（PNG）を生成できなければならない

- **詳細**: sklearn.metricsで精度指標を計算し、matplotlib.pyplotでグラフを描画
- **入力**: 学習済みモデル、テストデータ（Xtest.csv/Ytest.csv）
- **出力**: RMSE/R²/MAE数値、予測グラフPNG（16:9比率）
- **検証**: train/*_train.pyを実行し、RMSEが標準出力に表示され、PNGファイルが生成されることを確認

**FR-006**: システムは、翌日予測結果をCSV形式で出力できなければならない

- **詳細**: 過去7日分（バックテスト用）+ 未来7日分（予測用）の電力需要予測値をCSVに保存
- **入力**: 学習済みモデル、tomorrow.csv（気温データ）
- **出力**: *_tomorrow.csv（`KW`列のみ）
- **検証**: tomorrow/*_tomorrow.pyを実行し、CSVに**336行**（168+168）のデータが保存されることを確認

---

### 1.3. Webダッシュボード機能

**FR-007**: システムは、Webダッシュボード（http://localhost:8002/AI/dashboard/）でモデル選択・学習年選択・データ処理・学習・予測をブラウザ操作できなければならない

- **詳細**: HTML5/CSS3/JavaScriptで実装されたシングルページアプリケーション
- **入力**: ブラウザ操作（ボタンクリック）
- **出力**: ブラウザ上にRMSE/R²/MAE、予測グラフ表示
- **検証**: E2Eテスト（Playwright）でボタンクリック後に結果が表示されることを確認

**FR-008**: システムは、localStorageで学習年選択状態をモデル別に保存し、ページリロード後に自動復元できなければならない

- **詳細**: localStorage APIでモデル別にキー `ai_training_years_{model}` に学習年配列を保存
- **入力**: 学習年ボタンクリック（例: [2022][2023][2024]）
- **出力**: ページリロード後に選択状態が復元される
- **検証**: E2Eテストで学習年選択→リロード→選択状態が維持されることを確認

**FR-009**: システムは、組み合わせ検証機能で最適学習年組み合わせを自動探索できなければならない

- **詳細**: ローリング時系列交差検証で7組み合わせ（2016,2017→2018 ～ 2022,2023→2024）を自動実行
- **入力**: モデル選択（LightGBM/Keras/RandomForest/PyCaret）
- **出力**: テキストファイル（YYYY-MM-DD_{model}_optimize_years.txt）に上位5組み合わせと2025年推奨組み合わせを出力
- **検証**: train/*_optimize_years.pyを実行し、テキストファイルに7組み合わせの結果が記録されることを確認

---

### 1.4. CI/CD機能

**FR-010**: システムは、GitHub Actionsで毎日JST 07:00にCronトリガーで自動実行できなければならない

- **詳細**: .github/workflows/daily-forecast.ymlでCron設定 `0 22 * * *`（UTC 22:00 = JST 07:00）
- **入力**: Cronトリガー、またはmainブランチへのPush
- **出力**: 気温データ取得→データ処理→訓練→予測→GitHub Pagesデプロイ
- **検証**: ワークフロー手動実行で全ステップが成功することを確認

**FR-011**: システムは、R²<0.80を検出した場合にGitHub Issueを自動作成できなければならない

- **詳細**: ワークフロー内でR²スコアをチェックし、閾値違反時にgithub-script actionでIssue作成
- **入力**: LightGBM予測結果のR²スコア
- **出力**: GitHub Issue（タイトル: "AI Forecast Accuracy Degradation Detected (YYYY-MM-DD)"）
- **検証**: テストモードでR²<0.80をシミュレートし、Issueが作成されることを確認

**FR-012**: システムは、予測結果をGitHub Pagesで公開できなければならない

- **詳細**: actions/deploy-pages@v4で静的ファイル（index.html, metrics.json, PNG）をデプロイ
- **公開URL**: https://j1921604.github.io/Power-Demand-Forecast/
- **出力**: 4モデルの予測グラフと精度指標が表示される
- **検証**: ブラウザでURL アクセスし、グラフとmetrics.jsonが表示されることを確認

---

## 2. 非機能要件

### 2.1. パフォーマンス要件

**NFR-001**: モデル訓練時間（LightGBM）は10秒以内であること

- **測定方法**: time.time()で訓練開始～終了時間を計測
- **目標値**: ≤10秒
- **アラート閾値**: >30秒

**NFR-002**: 翌日予測実行時間は30秒以内であること

- **測定方法**: tomorrow/*_tomorrow.py実行時間をログ出力
- **目標値**: ≤30秒
- **アラート閾値**: >60秒

**NFR-003**: Webダッシュボード初回表示速度は2秒以内であること

- **測定方法**: ブラウザDevToolsでDOMContentLoadedイベント時間を計測
- **目標値**: ≤2秒
- **アラート閾値**: >5秒

**NFR-004**: GitHub Actionsワークフロー実行時間は10分以内であること

- **測定方法**: GitHub Actionsダッシュボードで実行時間を確認
- **目標値**: ≤5分
- **アラート閾値**: >10分

---

### 2.2. 信頼性要件

**NFR-005**: Open-Meteo API接続失敗時は3回リトライし、それでも失敗した場合はエラーを出力すること

- **実装**: try-except-retryロジックをtomorrow/temp.pyに実装
- **リトライ間隔**: 5秒
- **最大リトライ回数**: 3回

**NFR-006**: R²<0.80を検出した場合は自動的にGitHub Issueを作成すること

- **実装**: ワークフロー内でR²スコアをチェックし、閾値違反時にgithub-script actionを実行
- **Issue内容**: RMSE/R²/MAE、検出時刻、推奨アクション

**NFR-007**: 学習済みモデルファイルは訓練日時・学習年・精度指標をメタデータとして記録すること

- **実装**: モデルファイル保存時にpickle/h5メタデータに記録
- **メタデータ**: 訓練日時（YYYY-MM-DD HH:MM:SS）、学習年（例: 2022,2023,2024）、RMSE/R²/MAE

---

### 2.3. セキュリティ要件

**NFR-008**: Open-Meteo APIはHTTPS経由で通信すること

- **実装**: requests.get("https://...")でHTTPS接続
- **検証**: HTTP通信を禁止

**NFR-009**: GitHub SecretsにAPIキーなどの機密情報を保存すること

- **実装**: Open-Meteo APIは無料でAPIキー不要だが、将来的に有料API使用時はGitHub Secretsに保存
- **検証**: リポジトリにAPIキーをコミットしない

**NFR-010**: 依存パッケージの脆弱性スキャンを定期実行すること

- **実装**: pip-audit または GitHub Dependabotを有効化
- **頻度**: 週1回

---

### 2.4. 保守性要件

**NFR-011**: 全コードにPEP 8準拠のPythonコーディング規約を適用すること

- **実装**: flake8またはblackで自動フォーマット
- **検証**: CI/CDでlintチェック

**NFR-012**: 全ドキュメントをUTF-8エンコーディングで保存すること

- **実装**: ファイル保存時にUTF-8指定
- **検証**: 文字化けチェック

**NFR-013**: モデルファイル命名規則は `{model_name}_model.sav` または `{model_name}_model.h5` とすること

- **実装**: train/*_train.pyでファイル名を標準化
- **検証**: ファイル名パターンマッチングテスト

---

## 3. 制約事項

### 3.1. 技術的制約

**CON-001**: Python 3.10.11を標準実行環境とする

- **理由**: 依存パッケージの互換性保証
- **影響**: GitHub ActionsとローカルPython環境を統一

**CON-002**: GitHub Pagesの静的ホスティング制約を考慮し、学習済みモデルファイルは50MB未満とする

- **理由**: GitHub Pages推奨ファイルサイズ制限
- **影響**: モデル圧縮またはGitHub LFS使用を検討

**CON-003**: Open-Meteo APIは無料枠で使用するため、APIキー不要だがレート制限を遵守する

- **レート制限**: 1分あたり60リクエスト
- **影響**: 1日1回のCron実行では問題なし

**CON-004**: localStorageは5MBまで保存可能だが、学習年選択状態は1KB未満とする

- **実装**: JSON.stringify()で学習年配列を保存
- **影響**: 最大100年分の学習年を保存可能

---

### 3.2. ビジネス制約

**CON-005**: 電力需要実績データ（juyo-YYYY.csv）はGitリポジトリに含める

- **理由**: データの永続化と再現性保証
- **影響**: リポジトリサイズが増加（約10MB）

**CON-006**: 予測結果は毎日GitHub Pagesで公開する

- **理由**: ステークホルダーへの透明性確保
- **影響**: Cronトリガーの安定稼働が必須

**CON-007**: GitHub Actionsの無料枠（月2000分）を超えないようにワークフロー実行時間を最適化する

- **月間実行回数**: 30日×1回=30回
- **1回あたり目標時間**: ≤5分
- **月間合計**: 150分（無料枠の7.5%）

---

## 4. データモデル

### 4.1. 電力需要データ（juyo-YYYY.csv）

| カラム名 | データ型 | 説明                   | 例         |
| -------- | -------- | ---------------------- | ---------- |
| DATE     | Date     | 日付                   | 2024-01-01 |
| TIME     | Time     | 時刻                   | 00:00      |
| KW       | Integer  | 電力需要（キロワット） | 150000     |

### 4.2. 気温データ（temperature-YYYY.csv）

| カラム名 | データ型 | 説明       | 例         |
| -------- | -------- | ---------- | ---------- |
| DATE     | Date     | 日付       | 2024-01-01 |
| TIME     | Time     | 時刻       | 00:00      |
| TEMP     | Float    | 気温（℃） | 12.5       |

### 4.3. 特徴量データ（X.csv）

| カラム名 | データ型 | 説明         | 例   |
| -------- | -------- | ------------ | ---- |
| MONTH    | Integer  | 月（1-12）   | 1    |
| WEEK     | Integer  | 曜日（0-6）  | 0    |
| HOUR     | Integer  | 時刻（0-23） | 0    |
| TEMP     | Float    | 気温（℃）   | 12.5 |

### 4.4. 目的変数データ（Y.csv）

| カラム名 | データ型 | 説明                   | 例     |
| -------- | -------- | ---------------------- | ------ |
| KW       | Integer  | 電力需要（キロワット） | 150000 |

### 4.5. 精度指標（metrics.json）

```json
{
  "LightGBM": {
    "rmse": 450.5,
    "r2": 0.92,
    "mae": 350.2
  },
  "Keras": {
    "rmse": 480.3,
    "r2": 0.89,
    "mae": 380.5
  },
  "RandomForest": {
    "rmse": 520.1,
    "r2": 0.87,
    "mae": 410.3
  },
  "Pycaret": {
    "rmse": 470.2,
    "r2": 0.90,
    "mae": 370.8
  }
}
```

---

## 5. インターフェース定義

### 5.1. Open-Meteo API

**エンドポイント**: `https://api.open-meteo.com/v1/forecast`

**リクエストパラメータ**:

| パラメータ    | 型      | 必須 | 説明         | 例             |
| ------------- | ------- | ---- | ------------ | -------------- |
| latitude      | Float   | Yes  | 緯度         | 35.6785        |
| longitude     | Float   | Yes  | 経度         | 139.6823       |
| hourly        | String  | Yes  | 取得データ   | temperature_2m |
| timezone      | String  | Yes  | タイムゾーン | Asia/Tokyo     |
| past_days     | Integer | Yes  | 過去日数     | 7              |
| forecast_days | Integer | Yes  | 未来日数     | 7              |

**レスポンス**:

```json
{
  "hourly": {
    "time": ["2024-12-01T00:00", "2024-12-01T01:00", ...],
    "temperature_2m": [12.5, 12.3, ...]
  }
}
```

### 5.2. HTTPサーバー（server.py）

**ポート**: 8002**ルート**:

- `/`: プロジェクトルート（index.html）
- `/AI/dashboard/`: Webダッシュボード
- `/AI/metrics.json`: 精度指標JSON
- `/AI/tomorrow/*/*.png`: 予測グラフ画像

---

## 6. テスト要件

### 6.1. 単体テスト（pytest）

- **tests/unit/test_data.py**: data.pyの特徴量生成ロジック
- **tests/unit/test_optimize_years.py**: 組み合わせ検証ロジック

### 6.2. 統合テスト（pytest）

- **tests/integration/test_metrics.py**: metrics.json生成ロジック
- **tests/integration/test_rolling_cv.py**: ローリング時系列交差検証

### 6.3. 契約テスト（pytest）

- **tests/contract/test_api.py**: Open-Meteo APIレスポンス検証

### 6.4. E2Eテスト（Playwright/Selenium）

- **tests/e2e/test_dashboard.py**: Webダッシュボード操作
- **tests/e2e/test_optimize.py**: 組み合わせ検証ボタンクリック

### 6.5. パフォーマンステスト（pytest）

- **tests/performance/test_training_time.py**: モデル訓練時間≤10秒
- **tests/performance/test_optimize_time.py**: 組み合わせ検証時間≤5分

---

## 7. 受入基準

### 7.1. 機能受入基準

- [ ] LightGBMモデルでR²≥0.90、RMSE≤500kW、MAE≤400kWを達成
- [ ] 環境変数AI_TARGET_YEARSで学習年を指定できる
- [ ] Open-Meteo APIから168行（7日×24時間×2）の気温データを取得できる
- [ ] data.pyでX.csv（4列）とY.csv（1列）が生成される
- [ ] 翌日予測で24行のCSVと予測グラフPNGが生成される
- [ ] Webダッシュボードでモデル選択・学習年選択・データ処理・学習・予測が操作できる
- [ ] localStorageで学習年選択状態が保存され、リロード後に復元される
- [ ] 組み合わせ検証で7組み合わせの結果がテキストファイルに出力される
- [ ] GitHub ActionsでCronトリガー（UTC 22:00）が毎日実行される
- [ ] R²<0.80検出時にGitHub Issueが自動作成される
- [ ] GitHub Pagesで予測結果が公開される

### 7.2. 非機能受入基準

- [ ] LightGBM訓練時間≤10秒
- [ ] 翌日予測実行時間≤30秒
- [ ] Webダッシュボード初回表示速度≤2秒
- [ ] GitHub Actionsワークフロー実行時間≤10分
- [ ] Open-Meteo API接続失敗時に3回リトライする
- [ ] 全コードがPEP 8準拠である
- [ ] 全ドキュメントがUTF-8エンコーディングである

---

**バージョン**: 1.0.0
**最終更新**: 2025-11-26
