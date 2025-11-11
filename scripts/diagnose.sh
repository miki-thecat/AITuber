#!/bin/bash
echo "=========================================="
echo "AITuber Overlay 診断スクリプト"
echo "=========================================="
echo ""

echo "1. サーバープロセス確認"
ps aux | grep uvicorn | grep -v grep || echo "❌ サーバーが起動していません"
echo ""

echo "2. ポート確認"
netstat -tln | grep 5173 && echo "✅ ポート5173リスニング中" || echo "❌ ポート5173が開いていません"
echo ""

echo "3. HTTP接続テスト"
curl -I http://localhost:5173/ 2>&1 | head -5
echo ""

echo "4. HTMLファイル取得テスト"
curl -s http://localhost:5173/ | head -3
echo ""

echo "5. 静的ファイル確認"
ls -lh apps/overlay/static/
echo ""

echo "6. サーバーログ (最新20行)"
tail -20 /tmp/overlay.log 2>/dev/null || echo "ログファイルが見つかりません"
echo ""

echo "=========================================="
echo "診断完了"
echo "=========================================="
echo ""
echo "次のステップ:"
echo "1. ブラウザで http://localhost:5173/ を開く"
echo "2. F12 で開発者ツールを開く"
echo "3. Console タブでエラーを確認"
echo "4. Network タブでリソース読み込みを確認"
