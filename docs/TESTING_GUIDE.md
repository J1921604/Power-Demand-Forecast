# 最終検証手順書

**バージョン**: v1.0.0  
**作成日**: 2025-11-26  
**対象**: /run-tomorrow-data エラーハンドリング改善検証

---

## 検証環境

- **OS**: Windows 11
- **Python**: 3.10.11
- **ブラウザ**: Google Chrome 最新版
- **サーバー**: http://localhost:8002/

---

## 検証手順

### 1. サーバー起動

```powershell
# プロジェクトルートで実行
.\start-dashboard.ps1
```

**期待結果**:
- サーバーが http://localhost:8002/ で起動
- ブラウザが自動で開く
- ダッシュボードが表示される

### 2. ブラウザ開発者ツール準備

1. `F12`キーを押して開発者ツールを開く
2. **Console**タブを開く
3. **Network**タブを開く
4. "Preserve log"にチェックを入れる

### 3. 最新データ取得テスト

#### 3.1 LightGBMモデル選択

1. [LightGBM]ボタンをクリック
2. ボタンがネオングリーンに光ることを確認

#### 3.2 最新データ取得実行

1. [最新データ取得]ボタンをクリック
2. ボタンが「実行中...」に変わることを確認
3. **Consoleタブ**で以下のログを確認:
   ```
   [postJson] リクエスト送信: http://localhost:8002/run-tomorrow-data {}
   [postJson] レスポンスステータス: 200
   [postJson] レスポンスデータ: {status: "ok", stdout: "...", stderr: "...", returncode: 0}
   [最新データ取得] レスポンス: {status: "ok", ...}
   ```
4. **Networkタブ**で`run-tomorrow-data`リクエストを確認:
   - **Method**: POST
   - **Status**: 200
   - **Response Headers**: `Content-Type: application/json; charset=utf-8`
   - **Response**: `{status: "ok", ...}`

#### 3.3 エラー確認

**期待結果**:
- アラート「最新データ取得完了」が表示される
- **エラーなし**

**もしエラーが発生する場合**:
1. **Consoleタブ**のエラーメッセージをコピー
2. **Networkタブ**でリクエストの詳細を確認:
   - Headers
   - Payload
   - Response
   - Timing
3. エラー内容をスクリーンショット

### 4. 予測実行テスト

1. [予測]ボタンをクリック
2. 予測グラフ(PNG)が表示されることを確認

---

## 既知の改善点

### server.py

- **行318-364**: `_run_script`メソッドにreturncode追加
  ```python
  return { 'status': 'error', 'message': f'file not found: {script_relpath}', 'returncode': 1 }
  ```
- **行358-361**: 例外トレースバック追加
  ```python
  import traceback
  tb = traceback.format_exc()
  _log(f"Traceback:\n{tb}")
  return { 'status': 'error', 'message': str(e), 'traceback': tb, 'returncode': 1 }
  ```

### dashboard/index.html

- **行1015-1047**: `postJson`関数にデバッグログ追加
  ```javascript
  console.log(`[postJson] リクエスト送信: ${url}`, body);
  console.log(`[postJson] レスポンスステータス: ${res.status}`);
  console.log(`[postJson] レスポンスデータ:`, j);
  ```
- **行1111-1133**: 最新データ取得ボタンのエラーハンドリング改善
  ```javascript
  const message = res.status === 'ok' 
      ? '最新データ取得完了' 
      : `最新データ取得エラー: ${res.message || res.stderr || 'Unknown error'}`;
  ```

---

## トラブルシューティング

### エラー: TypeError: Failed to fetch

**原因1: CORS設定不足**
- server.pyの`end_headers`メソッドでCORS設定を確認
- `Access-Control-Allow-Origin: *`が設定されているか確認

**原因2: サーバー未起動**
- `http://localhost:8002/`にアクセスしてサーバーが起動しているか確認

**原因3: ファイアウォール**
- Windowsファイアウォールでポート8002が許可されているか確認

### エラー: HTTP 500

**原因: スクリプト実行エラー**
1. `AI/server.log`を確認
2. エラーメッセージ・トレースバックを確認
3. tomorrow/data.py、tomorrow/temp.pyを個別に実行してエラー特定

---

## 検証結果記録

### 実行日時

- 日時: _______________________

### 検証結果

- [ ] サーバー起動成功
- [ ] ダッシュボード表示成功
- [ ] 最新データ取得成功（エラーなし）
- [ ] 予測実行成功（グラフ表示）

### エラー詳細（もしあれば）

```
（ここにエラーメッセージ・スクリーンショットを記録）
```

---

## server.log確認コマンド

```powershell
# 最新50行を確認（UTF-8）
Get-Content "AI\server.log" -Encoding UTF8 | Select-Object -Last 50

# 特定エラーを検索
Get-Content "AI\server.log" -Encoding UTF8 | Select-String "Error|error|exception|Exception"
```

---

**作成者**: GitHub Copilot  
**最終更新**: 2025-11-26
