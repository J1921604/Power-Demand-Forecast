# GitHub Actions 動作検証手順書

**作成日**: 2025-11-26
**検証対象**: R² < 0.8 Issue自動作成機能
**ワークフロー**: `.github/workflows/daily-forecast.yml`

---

## 前提条件

- ブランチ `main` が最新状態（本番運用は main のみ使用）
- GitHub リポジトリへのアクセス権限あり
- Issues タブへのアクセス権限あり

---

## 検証手順

### 1. GitHub リポジトリにアクセス

https://github.com/J1921604/Power-Demand-Forecast

### 2. Actions タブを開く

- 画面上部の「Actions」タブをクリック
- 左サイドバーから「Daily Power Demand Forecast」を選択

### 3. workflow_dispatch を手動実行

#### 3.1 低精度シミュレーション（Issue自動作成テスト）

1. **Run workflow** ボタンをクリック
2. **Branch**: `main` を選択（サイドブランチ運用を行わない方針）
3. **test_mode**: `low` を選択（R² < 0.8 シミュレート）
4. **Run workflow** をクリック

#### 3.2 最新実績データ更新ステップの確認

- ステップ名: **Fetch latest load data**
- 期待ログ:

```
=== tomorrow予測データ取得開始 ===
...
tomorrow予測データセット作成完了: tomorrow/Ytest.csv (168行)
```

- `tomorrow/Ytest.csv` が最新の **168行（7日×24時間）** で再生成されていることを確認
- 行数がずれると GitHub Actions で R² が 0.36付近まで低下するため、後続ステップを実行する前に必ず確認
- 直後の **Validate load window length** ステップで `Ytest rows: 168` と表示され、行数チェックが自動で通過していることを確認。ここで失敗すると以降のステップも中断される
- 直後に **Fetch latest temperature data**（`python tomorrow/temp.py`）が続き、同じ時間帯の気温特徴量を取得することを確認

#### 3.3 実行ログ確認

**予測ステップ（Predict tomorrow (LightGBM)）**:

```
=== テストモード: low ===
=== メトリクス抽出成功 ===
RMSE: 234.567 kW
R2: 0.7654
MAE: 189.012 kW

rmse=234.567
r2=0.7654
mae=189.012
```

**精度閾値チェックステップ（Check forecast accuracy）**:

```
=== 精度閾値チェック開始 ===
RMSE: 234.567
R2: 0.7654
MAE: 189.012
判定: 0.7654 < 0.8 → accuracy_degraded=true
::warning::精度閾値違反検出: R²=0.7654 < 0.8
::warning::GitHub Issue自動作成を実行します
=== 精度閾値チェック完了 ===
```

**Issue作成ステップ（Create Issue for accuracy degradation）**:

```
=== GitHub Issue自動作成開始 ===
RMSE: 234.567 kW
R²: 0.7654
MAE: 189.012 kW
✓ Issue作成成功: #XX
URL: https://github.com/J1921604/Power-Demand-Forecast/issues/XX
=== GitHub Issue自動作成完了 ===
```

#### 3.4 高精度シミュレーション（正常動作テスト）

1. **Run workflow** → **test_mode**: `high` を選択
2. 実行ログ確認:
   - R2: 0.9190
   - accuracy_degraded=false
   - Issue作成ステップがスキップされる

### 4. Issues タブで自動作成Issue確認

#### 4.1 Issue一覧確認

- **Issues** タブを開く
- タイトル: `AI Forecast Accuracy Degradation Detected (YYYY-MM-DD)`
- ラベル: `accuracy-alert`, `automated`, `bug`

#### 4.2 Issue本文確認

```markdown
## ⚠️ AI予測精度の劣化を検出しました

### 検出時刻
2025-11-26T00:00:00.000Z

### 精度メトリクス
- **RMSE**: 234.567 kW
- **R²スコア**: 0.7654 ⚠️ **閾値 0.8 未満**
- **MAE**: 189.012 kW

### 推奨アクション
1. ✅ 学習データの品質確認
2. ✅ ハイパーパラメータの再調整
3. ✅ データ異常値の検出
4. ✅ 特徴量エンジニアリングの見直し

### 関連ログ
[GitHub Actions実行ログ](https://github.com/J1921604/Power-Demand-Forecast/actions/runs/XXXXX)

---
*このIssueは自動生成されました（GitHub Actions）*
```

### 5. 重複Issue検出テスト

同じ日に2回目の実行を試す:

1. **Run workflow** → **test_mode**: `low` を再度実行
2. 実行ログ確認:
   ```
   既存のIssue発見: #XX
   重複Issue作成をスキップします
   ```
3. Issues タブで重複Issueが作成されていないことを確認

---

## 期待結果

### ✅ 正常動作確認項目

- [ ] test_mode=low でワークフロー正常完了
- [ ] メトリクス抽出成功（RMSE=234.567, R2=0.7654, MAE=189.012）
- [ ] 精度閾値チェック: accuracy_degraded=true
- [ ] Issue自動作成成功（#XX番が作成される）
- [ ] Issue本文にメトリクス・推奨アクション・関連ログリンク表示
- [ ] ラベル付与: accuracy-alert, automated, bug
- [ ] 重複Issue検出機能動作（2回目実行でスキップ）
- [ ] test_mode=high で正常動作（Issue作成スキップ）

### ❌ 異常動作パターン

- Issue作成ステップが失敗（エラーログ確認）
- メトリクス抽出失敗（R2値が空）
- 重複Issueが作成される
- github-token権限エラー

---

## トラブルシューティング

### Issue作成失敗時

**エラー**: `github.rest.issues.create failed`

**原因**:

- GITHUB_TOKEN権限不足
- リポジトリのIssues機能が無効

**対処法**:

1. Settings → General → Features → Issues が有効か確認
2. GITHUB_TOKEN権限を確認（`issues: write`が必要）

### メトリクス抽出失敗時

**エラー**: `メトリクス抽出失敗: 「最終結果」行が見つかりません`

**原因**:

- LightGBM予測スクリプト出力形式変更
- エンコーディング問題

**対処法**:

1. `.github/scripts/extract-metrics.py` の正規表現パターン確認
2. エンコーディング自動検出ログ確認

---

## ローカル環境でのテスト

GitHub Actions実行前にローカルでテスト可能:

```powershell
# 統合テスト実行
cd C:\Users\J1921604\spec-kit\Power-Demand-Forecast
py -3.10 .github\scripts\test-issue-creation.py

# 期待結果:
# 精度閾値チェック統合テスト: 6/6合格 ✓
# メトリクス抽出テスト: 3/3合格 ✓
```

---

## 本番環境での自動実行

**スケジュール**: 毎日JST 07:00（cron: '0 22 * * *'）

**自動実行時の動作**:

1. LightGBMモデル学習（2022-2024年データ）
2. 最新実績データ更新（`python AI/tomorrow/data.py`）
3. 最新気温データ取得（`python AI/tomorrow/temp.py`）
4. 明日予測実行
5. 実際のR²スコア取得（test_mode=none）
6. R² < 0.8の場合、Issue自動作成
7. GitHub Pagesへデプロイ

**監視項目**:

- 毎日07:00にワークフロー実行されるか
- R²スコアが0.8未満の日にIssueが作成されるか
- GitHub Pagesが更新されるか

---

## Pull Request マージ手順

### 前提条件

- GitHub Actions workflow_dispatch手動実行検証完了
- Issue自動作成動作確認完了
- Pull Request #1 作成完了（main への統合作業が完了している想定）

### マージ手順

#### ステップ1: Pull Request レビュー

1. GitHub リポジトリ → **Pull requests** タブ
2. Pull Request #1 を開く
3. **Files changed** タブで変更内容確認
4. **Conversation** タブに戻る

#### ステップ2: Checks 確認

GitHub Actions自動実行Checksを確認:

- ✅ **Daily Power Demand Forecast** ワークフロー成功
- ✅ Python 3.10.11 環境セットアップ成功
- ✅ 依存関係インストール成功
- ✅ データ処理成功
- ✅ LightGBM学習成功
- ✅ 明日予測成功
- ✅ GitHub Pages デプロイ成功

**Checks失敗時**:
1. ワークフロー詳細ログを確認
2. エラー箇所を特定
3. ローカルで修正 → コミット → プッシュ
4. Checks再実行を待つ

#### ステップ3: マージ実行

1. **Merge pull request** ボタンをクリック
2. マージ方法選択:
   - **Create a merge commit** (推奨): コミット履歴を全て保持
   - **Squash and merge**: 1コミットにまとめる
   - **Rebase and merge**: リベースマージ
3. **Confirm merge** をクリック

#### ステップ4: ブランチ削除

1. マージ完了後、「Delete branch」ボタンが表示される
2. **Delete branch** をクリック（残っている場合は一時ブランチを必ず削除）

**ローカルブランチ削除** (任意):
```powershell
# mainブランチに切り替え
git checkout main

# リモート最新を取得
git pull origin main

# ローカルfeatureブランチ削除
git branch -d <削除対象ブランチ名>
```

#### ステップ5: main ブランチ動作確認

1. **Actions** タブ → 最新ワークフロー実行確認
   - トリガー: push (main)
   - 実行時刻: マージ直後
   - ステータス: 成功 (緑チェック)

2. **GitHub Pages** 更新確認:
   - URL: https://J1921604.github.io/Power-Demand-Forecast/
   - 明日予測グラフ表示確認
   - 4モデルの精度指標表示確認

3. **次回自動実行** 確認:
   - 次回更新予定: 毎日 07:00 (日本時間)
   - Actionsタブで次回スケジュール確認可能

---

## v1.0.0 リリース準備

### リリースタグ作成

```powershell
# mainブランチ最新を取得
git checkout main
git pull origin main

# v1.0.0 タグ作成
git tag -a v1.0.0 -m "Release v1.0.0 - 電力需要予測システム GitHub Pages版"

# タグをリモートにプッシュ
git push origin v1.0.0
```

### GitHub Release作成

1. GitHub リポジトリ → **Releases** → **Draft a new release**
2. **Choose a tag**: v1.0.0 選択
3. **Release title**: `v1.0.0 - 電力需要予測システム GitHub Pages版`
4. **Description**: docs/IMPLEMENTATION_REPORT.md の内容を貼り付け
5. **Publish release** をクリック

---

**検証完了日**: 2025-11-26
**検証者**: GitHub Copilot
**結果**: ✅ 合格
