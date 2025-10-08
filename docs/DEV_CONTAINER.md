# Dev Container 構築ガイド
_最終更新: 2025-10-08

## 前提
- Docker Desktop（WSL2 推奨）
- VS Code + Dev Containers 拡張

## ファイル
### `.devcontainer/Dockerfile`
- Ubuntu 24.04 + Python 3.12
- `ffmpeg`, `portaudio19-dev`, `curl`, `git`, `ca-certificates`

### `.devcontainer/devcontainer.json`
- `postCreateCommand`: `pip install -r requirements.txt && ./scripts/download_models.sh || true`
- `forwardPorts`: 5173 (Overlay), 8000 (Brain)

### `requirements.txt`
- `fastapi`, `uvicorn[standard]`, `websockets`, `sounddevice`, `numpy 2.x`, `scipy 1.13.x`, `pydub`, `python-dotenv`, `faster-whisper`, `openai`, `httpx`, `pytest`

## 使い方
1. VS Code でフォルダを開く → **Reopen in Container**
2. `.env.example` をコピーして `.env` を作成・編集
3. `models/` に STT/TTS モデルを配置（例は `scripts/download_models.sh` を参照）
4. `make dev` で Overlay+Brain 同時起動

## トラブルシューティング
- **Docker/WSL が不安定**: `wsl --shutdown` → Docker Desktop 再起動
- **pip が遅い/失敗**: `--timeout 120 --retries 3 --no-cache-dir`
- **PortAudio エラー**: `portaudio19-dev` と `sounddevice` を再インストール
- **faster-whisper が落ちる**: CTranslate2 形式モデルの配置を再確認
