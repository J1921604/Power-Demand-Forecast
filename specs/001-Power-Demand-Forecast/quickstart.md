# クイックスタートガイド: 電力需要予測システム

**最終更新**: 2025年11月26日
**想定時間**: 5分
**対象**: 初心者開発者
**バージョン**: 1.0.0

## 目的

このガイドに従うことで、5分以内に電力需要予測システムをローカルで起動し、GitHub Pagesにデプロイできます。

## 前提条件

- ✅ Python 3.10.11インストール済み
- ✅ Gitインストール済み
- ✅ GitHubアカウント作成済み

## 5ステップでデプロイ

### ステップ1: リポジトリクローン（30秒）

```powershell
git clone https://github.com/J1921604/Power-Demand-Forecast.git
cd Power-Demand-Forecast
```

### ステップ2: 依存パッケージインストール（1分）

```powershell
cd AI
py -3.10 -m pip install -r requirements.txt
```

### ステップ3: ローカルダッシュボード起動（10秒）

```powershell
# プロジェクトルートに戻る
cd ..

# ワンコマンド起動
.\start-dashboard.ps1
```

→ ブラウザで http://localhost:8002/AI/dashboard/ が自動起動

### ステップ4: GitHub Pages設定（1分）

1. https://github.com/J1921604/Power-Demand-Forecast/settings/pages を開く
2. **Source**: 「**GitHub Actions**」を選択
3. 保存

### ステップ5: 自動デプロイ実行（2分）

```powershell
# mainブランチへプッシュ
git add .
git commit -m "deploy: Initial release"
git push origin main
```

→ GitHub Actionsが自動実行され、約5-10分で https://j1921604.github.io/Power-Demand-Forecast/ にデプロイ完了

## トラブルシューティング

### Python 3.10.11がない

```powershell
# バージョン確認
py -3.10 --version

# インストール: https://www.python.org/downloads/release/python-31011/
```

### GitHub Actions失敗

1. https://github.com/J1921604/Power-Demand-Forecast/actions を開く
2. 失敗したワークフローをクリック
3. ログで詳細エラーを確認

### 404エラー（GitHub Pages）

- Settings → Pages → Source: **GitHub Actions** を確認
- 初回デプロイは最大10分かかる場合があります

## 次のステップ

- [完全仕様書](https://github.com/J1921604/Power-Demand-Forecast/blob/main/docs/完全仕様書.md)を読む
- [デプロイガイド](https://github.com/J1921604/Power-Demand-Forecast/blob/main/docs/DEPLOY_GUIDE.md)で詳細を確認
- [使用手順書](https://github.com/J1921604/Power-Demand-Forecast/blob/main/docs/使用手順書.md)でローカル開発環境をセットアップ

## サポート

- GitHub Issues: https://github.com/J1921604/Power-Demand-Forecast/issues
- リポジトリ: https://github.com/J1921604/Power-Demand-Forecast
