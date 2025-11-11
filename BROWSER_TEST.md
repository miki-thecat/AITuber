# ブラウザテスト手順

## 問題: ページが真っ暗 / 古いファイルが表示される

### 解決手順:

## 1. 強制リロード (キャッシュクリア)

### Windows/Linux:
- `Ctrl + Shift + R`
- または `Ctrl + F5`

### Mac:
- `Cmd + Shift + R`

## 2. 開発者ツールでキャッシュを無効化

1. `F12` で開発者ツールを開く
2. `Network` タブを開く
3. **"Disable cache"** にチェックを入れる
4. 開発者ツールを開いたままリロード

## 3. テストページで確認

以下のURLにアクセス:
```
http://localhost:5173/test.html
```

**期待される表示:**
- カラフルなグラデーション背景
- 黄色い枠
- "✅ テスト成功！" という大きな文字
- 時刻が1秒ごとに更新

このページが見えれば、サーバーは正常です。

## 4. メインページを確認

```
http://localhost:5173/
```

**期待される表示:**
- 暗いグレーの背景
- "Ready" という白文字
- 3秒ごとに "こんにちは！" 

## 5. それでもダメなら

### A. ブラウザの開発者ツール > Application タブ
1. `Application` タブを開く
2. 左側の `Storage` を展開
3. `Clear site data` をクリック
4. ページをリロード

### B. シークレットモード/プライベートブラウジング
新しいシークレットウィンドウで開く
- Chrome: `Ctrl + Shift + N`
- Firefox: `Ctrl + Shift + P`

### C. ポート転送URLを再確認
VS Codeの「ポート」タブで:
1. ポート5173を右クリック
2. "Stop Forwarding Port" で一度停止
3. もう一度ポート5173を追加
4. 新しいURLでアクセス

## 6. サーバー側確認

```bash
cd /workspaces/aituber
./scripts/diagnose.sh
```

## 7. 情報共有

以下をコピーして共有してください:

```bash
# ファイルの最終更新時刻
ls -l apps/overlay/static/

# ファイルの内容確認
head -10 apps/overlay/static/styles.css

# 配信されているファイル
curl http://localhost:5173/styles.css | head -10
```
