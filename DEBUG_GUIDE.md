# デバッグガイド - ブラウザで何も映らない問題

## 1. ブラウザの開発者ツールを開く

### Chrome/Edge
- `F12` または `Ctrl+Shift+I` (Windows/Linux)
- `Cmd+Option+I` (Mac)

### Firefox
- `F12` または `Ctrl+Shift+I`

## 2. 確認すべきタブ

### A. Console タブ
JavaScriptエラーを確認：
```
エラー例:
❌ WebSocket connection failed
❌ Failed to load resource
❌ Uncaught TypeError
```

**スクリーンショットを撮って共有してください**

### B. Network タブ
1. Network タブを開く
2. ページをリロード (F5)
3. 以下を確認:
   - `index.html` - Status: 200 OK?
   - `client.js` - Status: 200 OK?
   - `styles.css` - Status: 200 OK?
   - `ws` (WebSocket) - Status: 101?

**失敗しているリクエストがあれば教えてください**

### C. Elements タブ
HTML構造を確認：
```html
<body>
  <div id="container">
    <div id="subtitle"></div>  ← この中に "Ready" が表示されるはず
    <div id="mouth"></div>
  </div>
</body>
```

## 3. サーバー側ログの確認

ターミナルで実行：
```bash
# ログファイルを確認
cat /tmp/overlay.log

# リアルタイムでログを見る
tail -f /tmp/overlay.log

# サーバープロセス確認
ps aux | grep uvicorn
```

## 4. 簡単な診断コマンド

```bash
cd /workspaces/aituber

# サーバーが動いているか
curl -I http://localhost:5173/

# HTMLが取得できるか
curl http://localhost:5173/ | head -20

# WebSocketテスト (wscat が必要)
# npm install -g wscat
# wscat -c ws://localhost:5173/ws
```

## 5. よくある問題と解決策

### 問題: 真っ白な画面
**原因**: CSSが読み込まれていない
**確認**: Network タブで `styles.css` が 404

### 問題: "Ready" が表示されない
**原因**: WebSocket接続失敗
**確認**: Console に WebSocket エラー

### 問題: 画面真っ黒
**原因**: CSSの `background: transparent` 
**解決**: `styles.css` で `background: black` に変更

## 6. 最小限のテスト

test_overlay.html を開いて：
- 「接続中...」→「✅ 接続成功」に変わるか?
- ログメッセージが表示されるか?

## 7. 必要な情報

以下をコピーして共有してください：

```bash
# 1. サーバーステータス
ps aux | grep uvicorn | grep -v grep

# 2. ポート状態
netstat -tln | grep 5173

# 3. サーバーログ (最後の30行)
tail -30 /tmp/overlay.log

# 4. curlテスト結果
curl -I http://localhost:5173/
```

そして：
- **ブラウザのConsoleタブのスクリーンショット**
- **Networkタブのスクリーンショット**
- **実際に表示されている画面のスクリーンショット**
