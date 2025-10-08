# 実装手順（CLIエージェント最優先）
_最終更新: 2025-10-08

> 失敗しても継続。**警告＋フォールバック**を徹底。各ステップで `git add -A && git commit -m "step X: ..."`。

## 0) 事前規約
- ルート: `/workspaces/aituber`
- すべて冪等（存在すれば上書き）。
- main 以外はトピックブランチで作業。

---

## 1) 初期化
- `git init -b main`
- `.gitignore` に `__pycache__/ venv/ .env models/ *.wav .pytest_cache/ .vscode/`

---

## 2) 骨組み生成
- ディレクトリ：`apps/brain/{llm,stt,tts,persona}`, `apps/overlay/static`, `scripts`, `tests`, `models/{stt,tts}`, `.devcontainer`, `docs`
- 空ファイル：`config.py, utils.py, vad.py` など一式。

---

## 3) Dev Container
- `.devcontainer/Dockerfile`（Ubuntu 24.04 + Python 3.12, ffmpeg, portaudio）
- `.devcontainer/devcontainer.json`（postCreateで `pip install -r requirements.txt`）
- `requirements.txt`（固定版）

**検証**: VS Code で Reopen in Container → `python -V` が 3.12 系。

---

## 4) .env.example
- プロバイダ切替とポート・モデルパス・APIキーのダミーを記載。
- `cp .env.example .env` で編集可能に。

---

## 5) Persona
- `apps/brain/persona/system_prompt.ja.md` に口調/NG/優先順位。

---

## 6) Overlay MVP
- `apps/overlay/server.py` に `/`（index.html）・`/ws`（WS）実装。
- `static/index.html/client.js/styles.css` を最小で作成。

**検証**: `uvicorn apps.overlay.server:app --host 0.0.0.0 --port 5173` → Ready 表示。

---

## 7) Makefile & run_dev.sh
- `dev / overlay / brain / test` ターゲット。
- `run_dev.sh` は overlay 起動後に brain を起動。

---

## 8) 設定ローダ
- `dotenv` で `.env` を読み、`getenv/as_int/as_float` を提供。

---

## 9) base IF
- `llm/stt/tts` に `generate/transcribe/synthesize` の抽象関数。

---

## 10) ダミー経路
- LLM: 入力のエコーを返す。
- STT: 固定文字列を返す。
- TTS: 無音WAV（1秒）を作って返す。

**検証**: `pytest -q`（後述の最小テストで Green）。

---

## 11) Orchestrator 骨組み
- STT→LLM→Overlay(utter_start)→TTS→mouth（ダミー）→utter_end。

**検証**: `make dev` で Console に WS イベント。

---

## 12) 最小テスト
- `tests/test_llm.py`：`str` 返却
- `tests/test_stt.py`：例外にならない
- `tests/test_tts.py`：WAV パスを返す

---

## 13) Overlay UI（字幕/口パク）
- `client.js` が `utter_start/mouth/utter_end` を描画・反映。

---

## 14) TTS Piper（ローカル）
- `PIPER_VOICE` があれば実音声、なければ無音フォールバック。
- 生成WAVの RMS → 0〜1 正規化 → `mouth` を 30–60Hz で送信。

---

## 15) STT faster-whisper
- `WHISPER_MODEL_DIR` があれば実処理、なければダミー。

---

## 16) マイク/VAD
- `segment_audio_from_mic()` を実装してループへ。

---

## 17) LLM（Ollama / OpenAI）
- API未設定時はダミー応答。リトライ/タイムアウト有り。

---

## 18) 同期改善
- 再生中に短フレームごとの `mouth` を送る。

---

## 19) 例外対策
- すべての provider で例外→警告→フォールバック。

---

## 20) 受け入れ基準の確認
- `make dev` → 字幕 ≤5s, 再生 ≤8s, mouth 0.0〜1.0 推移。

---

## 21) ドキュメント
- README へ導線、`docs/` を最新化（本ファイル含む）。

---

## 22) リリース
- `release/v0.1.0` で最終調整 → `main` へマージ → タグ。
