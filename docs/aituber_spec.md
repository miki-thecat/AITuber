AITuber（CLI向け）実装仕様書

（開発支援AI／CLIエージェントが読む前提。Dev Containerで完全隔離）

0. ゴール / 非ゴール

ゴール

ローカル PC 上で動く「会話型 AITuber」を最小構成で実装し、OBS の Browser Source に重ねて配信できる。

完全オフライン／低コスト運用を意識し、STT/LLM/TTS は切替可能なプロバイダ設計にする。

Dev Container（VS Code）だけで再現性ある開発・実行ができる。

非ゴール

高度な3Dモデルやモーションキャプチャの導入（将来ロードマップに回す）

YouTube/Twitch への自動配信（OBS 側の設定で配信する前提）

商用ボイスの調達・同梱（TTS は OSS/外部APIの選択式に留める）

1. 全体アーキテクチャ

リアルタイム・パイプライン

Mic → VAD → STT  → LLM  → TTS(Audio/WAV) ┐
                            │              │
                            └→ Overlay WS ←┘（字幕・口パク）→ OBS Browser Source


STT: faster-whisper（ローカル）/ OpenAI Whisper（API）

LLM: Ollama（ローカル）/ OpenAI（API）

TTS: Piper（ローカル）/ VOICEVOX HTTP / OpenAI TTS（API）

Overlay: FastAPI + WebSocket + 静的HTML/JS（OBS の Browser Source で表示）

口パク: 生成音声の短時間RMSから mouth openness を算出して Overlay に送信

2. 技術スタック

言語: Python 3.11（統一）

Web/Overlay: FastAPI（ASGI）, WebSocket, HTML/JS（バンドラ不要）

音声: sounddevice or pyaudio（再生）, ffmpeg（変換）

STT: faster-whisper

LLM: openai or ollama HTTP

TTS: piper-tts（CLI） or VOICEVOX HTTP or OpenAI TTS

Dev Container: Ubuntu 24.04 ベース、Python 3.11、ffmpeg、PortAudio、Node 不要

テスト: pytest

整形: ruff / black（任意）

3. リポジトリ構成（CLIエージェントはこの構成でファイル生成）
aituber/
├─ apps/
│  ├─ brain/
│  │  ├─ main.py                 # オーケストレーション（ループ）
│  │  ├─ config.py               # 環境変数/設定読込
│  │  ├─ vad.py                  # 音声区間検出（SileroVAD か WebRTC VAD）
│  │  ├─ llm/
│  │  │  ├─ __init__.py
│  │  │  ├─ base.py              # IF: generate(prompt, history) -> text
│  │  │  ├─ provider_openai.py
│  │  │  └─ provider_ollama.py
│  │  ├─ stt/
│  │  │  ├─ __init__.py
│  │  │  ├─ base.py              # IF: transcribe(audio_path) -> text
│  │  │  ├─ provider_faster_whisper.py
│  │  │  └─ provider_openai.py
│  │  ├─ tts/
│  │  │  ├─ __init__.py
│  │  │  ├─ base.py              # IF: synthesize(text, voice) -> wav_path
│  │  │  ├─ provider_piper.py
│  │  │  ├─ provider_voicevox.py
│  │  │  └─ provider_openai.py
│  │  ├─ persona/
│  │  │  └─ system_prompt.ja.md  # 口調・一人称・配信スタイル
│  │  └─ utils.py                # wav のRMS→mouth値等
│  └─ overlay/
│     ├─ server.py               # FastAPI+WS：/ で index.html, /ws で双方向
│     └─ static/
│        ├─ index.html
│        ├─ client.js            # WS受信→口パク/字幕レンダリング
│        ├─ styles.css
│        └─ assets/avatar/       # avatar.png, mouth_a.png, mouth_i.png...
├─ models/                        # STT/TTS ローカルモデル配置（git管理外）
├─ scripts/
│  ├─ run_dev.sh                 # 開発同時起動（overlay+brain）
│  └─ download_models.sh         # Piper/Whisper の最小モデルDL
├─ tests/
│  ├─ test_tts.py
│  ├─ test_stt.py
│  └─ test_llm.py
├─ .devcontainer/
│  ├─ devcontainer.json
│  └─ Dockerfile
├─ requirements.txt
├─ Makefile
├─ .env.example
└─ README.md

4. Dev Container 設定（生成物の唯一ソース）

.devcontainer/devcontainer.json

{
  "name": "aituber-dev",
  "build": {
    "dockerfile": "Dockerfile"
  },
  "features": {},
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-toolsai.jupyter"
      ]
    }
  },
  "remoteUser": "vscode",
  "forwardPorts": [5173, 8000],
  "postCreateCommand": "pip install -r requirements.txt && ./scripts/download_models.sh || true"
}


.devcontainer/Dockerfile

FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

# 基本ツール
RUN apt-get update && apt-get install -y \
    python3.11 python3.11-venv python3-pip \
    portaudio19-dev ffmpeg curl git \
    && rm -rf /var/lib/apt/lists/*

# pip のデフォルトを python3.11 に
RUN ln -sf /usr/bin/python3.11 /usr/bin/python && \
    python -m pip install --upgrade pip

# piper はパッケージ版/バイナリを使う想定（後続スクリプトでDLする）
# 音声APIなどは後述の requirements で入る

USER vscode
WORKDIR /workspaces/aituber


requirements.txt

fastapi==0.115.*
uvicorn[standard]==0.30.*
websockets==13.*
sounddevice==0.4.*
numpy==2.*
scipy==1.*
pydub==0.25.*
python-dotenv==1.*
faster-whisper==1.*
openai==1.*
httpx==0.27.*
pytest==8.*


scripts/download_models.sh（CPU前提の最小）

#!/usr/bin/env bash
set -e
mkdir -p models/stt models/tts

# Whisper small or base（サイズは環境で調整）
# 実ファイルDLはここに記述（例：wget で CTranslate2 形式の small）
echo "Place your faster-whisper CTranslate2 model into models/stt/"
echo "Example: models/stt/whisper-small-ct2/"

# Piper 日本語音声（軽量）例：ja-JP-xxx.onnx
echo "Place your piper voice into models/tts/"
echo "Example: models/tts/ja-JP-xxx.onnx"

5. 環境変数（.env.example）
# Provider switches: "local" or "api"
STT_PROVIDER=local
LLM_PROVIDER=local
TTS_PROVIDER=local

# Whisper (local)
WHISPER_MODEL_DIR=./models/stt/whisper-small-ct2

# Piper (local)
PIPER_VOICE=./models/tts/ja-JP-xxx.onnx
PIPER_SAMPLERATE=22050

# VOICEVOX (HTTP) optional
VOICEVOX_URL=http://host.docker.internal:50021
VOICEVOX_SPEAKER_ID=3

# OpenAI (optional)
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
OPENAI_TTS_VOICE=alloy
OPENAI_TTS_FORMAT=wav

# Ollama (local) optional
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.1:8b

# Overlay
OVERLAY_HOST=0.0.0.0
OVERLAY_PORT=5173

# Brain
BRAIN_HOST=0.0.0.0
BRAIN_PORT=8000

6. 主要モジュールの仕様
6.1 VAD（apps/brain/vad.py）

IF: def segment_audio_from_mic() -> Iterable[path_to_wav]

役割: マイク音声をバッファリングし、発話区間毎に WAV を出力。

実装方針: WebRTC VAD or Silero VAD（簡易で可）。無音閾値・最長時間を設定可能。

6.2 STT（apps/brain/stt/base.py 他）

IF: transcribe(wav_path: str) -> str

provider_faster_whisper: CTranslate2 モデルを WHISPER_MODEL_DIR から読み込み。

provider_openai: Whisper API 呼び出し（キー未設定なら例外ではなく警告+フォールバック）。

6.3 LLM（apps/brain/llm/base.py 他）

IF: generate(system_prompt: str, history: list[dict], user_text: str) -> str

provider_openai: ChatCompletions / responses API を単純化。

provider_ollama: /api/chat に history（role/content）で投げる。

いずれもタイムアウト/リトライ実装。失敗時は「遅延応答」メッセージでしのぐ。

6.4 TTS（apps/brain/tts/base.py 他）

IF: synthesize(text: str, voice_id: str|None) -> str # return wav_path

provider_piper: piper CLI または python ラッパーで onnx 音声を生成。

provider_voicevox: HTTP API（/audio_query→/synthesis）。URL/スピーカーIDは環境変数。

provider_openai: TTS API。WAV で保存。

生成後、RMS エンベロープを utils.py で計算して mouth シグナルに変換。

6.5 Overlay（apps/overlay/server.py, static/*）

FastAPI で / に index.html を返す。

/ws（WebSocket）に対し、brain → overlay で JSON イベント送信：

{"type":"utter_start","text":"...", "subtitle":"..."}

{"type":"mouth","value":0.0~1.0}（約30〜60 FPS程度のタイムステップで送る）

{"type":"utter_end"}

client.js は mouth 値に応じて口画像を切替 or スプライト拡大率で口パクを表現。

OBS 側は Browser Source で http://localhost:5173/ を追加（透過背景CSS）。

6.6 Orchestrator（apps/brain/main.py）

無限ループ：

segment_audio_from_mic() で WAV 取り出し

STT→ユーザー発話テキスト

LLM→返信テキスト

Overlay に utter_start & 字幕送出

TTS→WAV 生成、再生しながら mouth 値を WS でストリーミング

utter_end 送出

persona/system_prompt.ja.md を読み込み、配信者キャラでの応答を固定。

7. Persona（最小プロンプト雛形：apps/brain/persona/system_prompt.ja.md）

一人称は「ボク」

砕けた配信者口調。視聴者を名前で呼ばない。煽らない。誤情報を避ける。

短く、まず一言で結論→必要なら補足の順。

学術/技術は正確さ優先、根拠が曖昧な話題は「可能性」表現にする。

NG: 誹謗中傷、センシティブな助言、医療/法律の断定助言、暴力/自傷表現の助長。

8. CLIエージェント用タスクリスト（順守）

Task 1: 雛形生成

上記のディレクトリ/ファイルを正確に作成。

すべての __init__.py を空でよいので配置。

Task 2: Dev Container

.devcontainer/ のファイルをそのまま生成。

requirements.txt をインストール可能に保つ（バージョン固定のまま）。

Task 3: Overlay 実装

server.py：/ と /ws を実装。CORS 無効で可。

static/index.html + client.js + styles.css：PNG アバター+口パク。

Task 4: STT/LLM/TTS 各 base & provider

base IF を満たす最小実装を先に作り、provider で分岐。

config.py で ENV を読み、factory 関数でプロバイダを決定。

Task 5: Orchestrator

main.py に「発話→応答→音声→口パク配信」の直列実装。

音声再生はブロッキングでOK。mouth は 30〜60Hz でWS送信。

Task 6: テスト

tests/test_*.py を作成。

test_llm.py: ダミーLLM（エコー）で generate が文字列を返すこと

test_tts.py: provider_piper をモック化し WAV ファイルを生成した体裁を検証

test_stt.py: ダミーWAVに対して空文字列で返ること（例外にならない）

CI は不要。ローカル pytest で緑にする。

Task 7: ドキュメント

README.md に以下を記載：

Dev Container で開く → make dev 実行

OBS Browser Source の追加方法

モデル配置方法（models/）と .env 設定例

9. 主要コマンド / Makefile

Makefile

.PHONY: dev overlay brain test fmt

dev:
\tuvicorn apps.overlay.server:app --host 0.0.0.0 --port 5173 & \\
\tpython -m apps.brain.main

overlay:
\tuvicorn apps.overlay.server:app --host 0.0.0.0 --port 5173 --reload

brain:
\tpython -m apps.brain.main

test:
\tpytest -q

fmt:
\truff check . || true
\tblack .

10. 実行手順（人間/エージェント共通）

VS Code で「Reopen in Container」

.env.example を .env にコピーし、必要な箇所を編集

models/ に Whisper / Piper の最小モデルを配置

make dev

OBS → Browser Source → http://localhost:5173/ を追加（幅・透過は任意）

マイクに話しかける → 返答音声と口パク・字幕が同期表示される

11. 受け入れ基準（Acceptance Criteria）

 make test がすべてパスする（APIキー未設定でも落ちない）

 make dev で Overlay と Brain が同時起動する

 マイク発話→5秒以内に字幕テキストが表示され、8秒以内に音声再生が開始

 音声再生中に mouth 値が 0.0〜1.0 で変動し、口パクが視認できる

 .env の各 Provider を切替えても例外終了せず、未設定時はフォールバック/警告

12. エラーハンドリング指針

APIキー未設定: ログ警告→ローカルプロバイダに自動フォールバック

モデル未配置: 初回起動時に人間に案内（パス例を表示）

音声入出力失敗: デバイス一覧をログ出力し、デフォルトに再挑戦

WS切断: Overlay 側が再接続するまで再試行（指数バックオフ）

13. 安全・配信ガイドライン（必ず実装）

出力前フィルタ：NGワード/ジャンル（誹謗中傷、差別、犯罪助長、医療/法務の断定助言、個人情報）を検知→安全化（一般論・相談窓口案内・話題転換）

未成年視聴を想定し、R-指定相当の話題は避ける

事実関係が曖昧な質問には「確証がない」旨を明示

音量・音圧の上限を設け、ピーククリップを避ける

14. 将来ロードマップ（任意）

Live2D/VRM 対応（口形状推定からブレンドシェイプ駆動）

歌枠向けリアルタイムリップシンク（音節推定）

配信プラットフォーム（YouTube/Twitch）API 連携（コメント取得→LLM反応）

シーン切替・SE/BGM 自動ミキシング

15. 開発支援AIへの追加指示（メタ）

生成ファイルは上記パス/ファイル名を厳守すること

例外は落とさず、「警告＋フォールバック」を必ず実装

音声・モデルは実体を同梱しない。README に取得手順だけを書く

仕様の疑義は最小機能で実装→コメントに TODO を残すこと
