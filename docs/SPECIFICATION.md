# AITuber 仕様書（CLI/人間共用）
_最終更新: 2025-10-08

## 0. ゴール / 非ゴール
**ゴール**
- ローカル PC 上で動く会話型 **AITuber** の最小構成を提供し、OBS の Browser Source に重ねて配信できる。
- STT/LLM/TTS の **プロバイダ切替**（ローカル/クラウド）に対応し、コストと速度を調整可能。
- **Dev Container だけで再現**できる開発/実行環境。

**非ゴール**
- 高度な3Dモデル/L2D/モーションキャプチャ。
- YouTube/Twitch への自動配信機能（OBS 側の設定で配信）。
- 商用ボイスの調達/配布（TTS は OSS/外部API切替のみ）。

---

## 1. 全体アーキテクチャ（概念）
**リアルタイム・パイプライン**
```
Mic → VAD → STT → LLM → TTS(Audio/WAV) ┐
                            │            │
                            └→ Overlay WS└─（字幕・口パク）→ OBS Browser Source
```

### 1.1 モジュール
- **Overlay（FastAPI + WebSocket + HTML/JS）**: 字幕と口パクをブラウザに描画（OBS で取り込む）。
- **STT**: faster-whisper (ローカル) / OpenAI Whisper (API)。
- **LLM**: Ollama (ローカル) / OpenAI (API)。
- **TTS**: Piper (ローカル) / VOICEVOX HTTP / OpenAI TTS。
- **Orchestrator**: STT→LLM→TTS をつなぎ、Overlay にイベント送出。

---

## 2. 技術スタック
- **言語**: Python 3.12（Dev Container 基準）
- **Web**: FastAPI, WebSocket, Uvicorn, HTML/JS
- **Audio**: sounddevice/pyaudio（再生）, ffmpeg（変換）
- **STT**: faster-whisper
- **LLM**: openai / Ollama HTTP
- **TTS**: piper-tts / VOICEVOX HTTP / OpenAI TTS
- **テスト**: pytest
- **整形**: （任意）ruff, black

---

## 3. ディレクトリと主要ファイル
```
aituber/
├─ apps/
│  ├─ brain/
│  │  ├─ main.py                 # オーケストレーション
│  │  ├─ config.py               # 環境変数ローダ
│  │  ├─ vad.py                  # 音声区間検出
│  │  ├─ llm/ stt/ tts/          # 各 provider 実装
│  │  ├─ persona/system_prompt.ja.md
│  │  └─ utils.py                # 音声RMS→mouth値 など
│  └─ overlay/
│     ├─ server.py               # FastAPI + WS / 静的配信
│     └─ static/{index.html,client.js,styles.css,assets/...}
├─ models/                        # STT/TTSモデル（git管理外）
├─ .devcontainer/{Dockerfile,devcontainer.json}
├─ scripts/{run_dev.sh,download_models.sh}
├─ tests/
└─ docs/（本ディレクトリ）
```

---

## 4. Overlay API（WSイベント）
- `utter_start` : `{"type":"utter_start","text":"...", "subtitle":"..."}`
- `mouth`       : `{"type":"mouth","value":0.0~1.0}`（30〜60Hz）
- `utter_end`   : `{"type":"utter_end"}`

---

## 5. 環境変数（.env）
- プロバイダ切替: `STT_PROVIDER|LLM_PROVIDER|TTS_PROVIDER` に `local` or `api`
- Whisper: `WHISPER_MODEL_DIR`
- Piper: `PIPER_VOICE`, `PIPER_SAMPLERATE`
- VOICEVOX: `VOICEVOX_URL`, `VOICEVOX_SPEAKER_ID`
- OpenAI: `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_TTS_VOICE`, `OPENAI_TTS_FORMAT`
- Ollama: `OLLAMA_BASE_URL`, `OLLAMA_MODEL`
- Overlay: `OVERLAY_HOST`, `OVERLAY_PORT`
- Brain: `BRAIN_HOST`, `BRAIN_PORT`

詳細は `docs/DEV_CONTAINER.md` を参照。

---

## 6. 受け入れ基準（MVP）
- `make dev` で Overlay と Brain が同時起動。
- マイク発話→**5秒以内に字幕**、**8秒以内に音声再生**。
- 再生中 `mouth` が 0.0〜1.0 で推移し口パクが視認可能。
- `.env` の切替時でも例外終了せず、未設定は警告＋フォールバック。

---

## 7. セーフティガイドライン（出力制御）
- 誹謗中傷/差別/犯罪助長/医療・法律の断定助言/個人情報は出さない。
- あいまいな事実は「可能性」表現＋出典確認を促す。
- 音量上限・クリッピング回避を実装。

---

## 8. 参考
- 詳細実装手順: `docs/IMPLEMENTATION_PLAN.md`
- ブランチ運用: `docs/BRANCHING_RULES.md`
- 構成図: `docs/ARCHITECTURE.md`
- Dev Container: `docs/DEV_CONTAINER.md`
- タスク: `docs/TODO.md`
- ロードマップ: `docs/ROADMAP.md`
