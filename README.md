# AITuber

ローカルPCで動作する会話型AITuber（最小構成）

## 特徴

- **完全ローカル実行**: faster-whisper(STT), Ollama(LLM), Piper(TTS)によるローカル動作
- **クラウドAPI対応**: OpenAI APIへの切り替えも可能
- **OBS連携**: Browser Sourceで字幕・口パクを配信に重ねられる
- **Dev Container**: 環境構築不要で即座に開発可能

## クイックスタート

### 1. Dev Containerで起動

VS Codeで本リポジトリを開き、"Reopen in Container"を選択。

### 2. 環境設定

```bash
cp .env.example .env
# .envを編集してプロバイダを設定
```

### 3. 起動

```bash
# Overlay + Brainを同時起動
make dev

# または個別起動
make overlay  # 別ターミナル
make brain
```

### 4. OBSで表示

OBS Studio > ソース > Browser
- URL: `http://localhost:5173`
- 幅: 1920, 高さ: 1080
- カスタムCSS: 透明背景を設定

## プロジェクト構成

```
aituber/
├── apps/
│   ├── brain/          # STT→LLM→TTSのオーケストレーション
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── llm/        # LLMプロバイダ
│   │   ├── stt/        # STTプロバイダ
│   │   ├── tts/        # TTSプロバイダ
│   │   └── persona/
│   └── overlay/        # WebSocket + HTML/JS
│       ├── server.py
│       └── static/
├── tests/              # pytest
├── docs/               # 仕様書
├── .github/workflows/  # CI/CD
└── Makefile
```

## 使い方

### テキスト入力モード

```bash
python -m apps.brain.main --text "こんにちは"
```

### マイクモード

```bash
python -m apps.brain.main --mic
```

### テスト実行

```bash
make test           # 全テスト
make test-unit      # ユニットテストのみ
```

## プロバイダ切り替え

`.env`ファイルで切り替え：

```env
# ローカル
STT_PROVIDER=local
LLM_PROVIDER=local
TTS_PROVIDER=local

# API
STT_PROVIDER=api
LLM_PROVIDER=api
TTS_PROVIDER=api
```

## ドキュメント

- [仕様書](docs/SPECIFICATION.md)
- [アーキテクチャ](docs/ARCHITECTURE.md)
- [実装計画](docs/IMPLEMENTATION_PLAN.md)
- [テスト仕様](docs/TEST_SPEC.md)
- [ブランチ運用](docs/BRANCHING_RULES.md)

## ライセンス

MIT License

## 開発状況

- [x] Dev Container環境
- [x] Overlay (WebSocket + HTML)
- [x] Brain オーケストレータ
- [x] LLM/STT/TTSプロバイダ
- [x] ユニットテスト
- [x] CI/CD (GitHub Actions)
- [ ] E2Eテスト
- [ ] パフォーマンス最適化
- [ ] Live2D/VRM対応
