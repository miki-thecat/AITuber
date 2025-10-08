AITuber 実装オーダー（CLI実行用・決定版）
0) 事前規約（すべてのステップに共通）

すべてのコマンドは リポジトリルート /workspaces/aituber で実行。

すべてのファイル生成は 存在しなければ作成／あれば上書き（冪等）。

例外は失敗で終了しない。代替案・フォールバック・警告ログで継続。

変更はステップ単位でコミット（git add -A && git commit -m "step X: ..."）。

1) リポジトリ初期化 & .gitignore

作業

git init -b main

.gitignore を作成：__pycache__/ venv/ .env models/ *.wav .pytest_cache/ .vscode/

検証

git status が空でない（.gitignore だけ変更表示）

成果物

.git/, .gitignore

2) ディレクトリ骨組み

作業

mkdir -p apps/brain/{llm,stt,tts,persona} apps/overlay/static scripts tests models/{stt,tts} .devcontainer
touch apps/brain/{__init__.py,config.py,utils.py,vad.py}
touch apps/brain/llm/{__init__.py,base.py,provider_openai.py,provider_ollama.py}
touch apps/brain/stt/{__init__.py,base.py,provider_faster_whisper.py,provider_openai.py}
touch apps/brain/tts/{__init__.py,base.py,provider_piper.py,provider_voicevox.py,provider_openai.py}
touch apps/brain/persona/system_prompt.ja.md
touch apps/overlay/{server.py} apps/overlay/static/{index.html,client.js,styles.css}
touch scripts/{run_dev.sh,download_models.sh}
touch tests/{test_llm.py,test_stt.py,test_tts.py}
touch requirements.txt Makefile README.md .env.example


検証

find . -maxdepth 3 | sort で上記が存在

成果物

ディレクトリ/空ファイル一式

3) Dev Container 定義

作業

.devcontainer/Dockerfile を作成（Ubuntu 24.04, Python3.11, ffmpeg, portaudio19-dev を入れる）。

.devcontainer/devcontainer.json を作成（postCreateCommand で pip install -r requirements.txt && ./scripts/download_models.sh || true）。

requirements.txt を追加（FastAPI/uvicorn/websockets/sounddevice/numpy/scipy/pydub/python-dotenv/faster-whisper/openai/httpx/pytest）。

検証

VS Code → “Reopen in Container” 後、python --version が 3.11 系

pip list | grep fastapi が表示

成果物

.devcontainer/ 完備、依存の導入

4) .env.example を配置

作業

下記キーだけ必須（空でよい）：

STT_PROVIDER=local
LLM_PROVIDER=local
TTS_PROVIDER=local
WHISPER_MODEL_DIR=./models/stt/whisper-small-ct2
PIPER_VOICE=./models/tts/ja-JP-xxx.onnx
PIPER_SAMPLERATE=22050
OVERLAY_HOST=0.0.0.0
OVERLAY_PORT=5173
BRAIN_HOST=0.0.0.0
BRAIN_PORT=8000
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.1:8b
VOICEVOX_URL=http://host.docker.internal:50021
VOICEVOX_SPEAKER_ID=3


検証

cp .env.example .env && cat .env | wc -l が0でない

成果物

.env.example

5) Persona 最小定義

作業

apps/brain/persona/system_prompt.ja.md に配信用ガイド（口調/NG/優先順位）を記述。

検証

grep -i "一人称" apps/brain/persona/system_prompt.ja.md

成果物

ペルソナプロンプト

6) Overlay（HTTP+WS）MVP

作業

apps/overlay/server.py: FastAPI で / に index.html、/ws に WebSocket を実装。サーバ側はクライアントの接続/切断ログを出すだけ。

static/index.html: 透過背景・中央に “AITuber Overlay Ready”。

static/client.js: WS 接続し、受信 JSON を console.log。

static/styles.css: 透過と簡単なレイアウトのみ。

検証

uvicorn apps.overlay.server:app --host 0.0.0.0 --port 5173

ブラウザ http://localhost:5173/ → “Ready” 表示

DevTools の Console に「connected」ログ

成果物

Overlay 単体起動可

7) Makefile & スクリプト雛形

作業

Makefile に以下を作成：

dev: overlay をバックグラウンド起動 → python -m apps.brain.main

overlay: uvicorn reload

brain: python -m apps.brain.main

test: pytest -q

fmt: ruff/black（存在しなければ no-op でも可）

scripts/run_dev.sh: set -euo pipefail で overlay→brain の順に起動。

検証

make overlay が起動する

pkill -f uvicorn で停止できる

成果物

コマンド運用の足場

8) Config ローダ

作業

apps/brain/config.py:

dotenv で .env 読み込み

getenv(key, default=None) と as_int/as_float/as_bool

Provider 判定ヘルパ provider("STT_PROVIDER") 等

検証

python - <<'PY'\nfrom apps.brain import config; print(config.getenv('STT_PROVIDER'))\nPY

成果物

汎用設定ヘルパ

9) LLM/STT/TTS の base IF（空実装）

作業

llm/base.py: generate(system_prompt, history, user_text) -> str（NotImplementedError）

stt/base.py: transcribe(wav_path) -> str

tts/base.py: synthesize(text, voice_id=None) -> wav_path

検証

python - <<'PY' ... で import 成功（例外は未実装でOK）

成果物

安定したインターフェース

10) ダミープロバイダ（エコー運転）

作業

llm/provider_ollama.py/provider_openai.py にダミー実装：return f"（テスト）{user_text}"。

stt/provider_faster_whisper.py にダミー：常に "テスト入力" を返す。

tts/provider_piper.py にダミー：無音WAV（1秒）を生成してパス返却。

apps/brain/utils.py に write_silence_wav(path, secs=1, sr=22050)

検証

pytest -q → まだテスト未記述でも import 可能

後続の orchestrator で動作確認予定

成果物

APIキー／モデル無しでも動く最小経路

11) Orchestrator（brain/main.py）骨組み

作業

フロー：STT → LLM → Overlay(utter_start) → TTS → mouthストリーム（ダミー）→ utter_end

現段階は マイク不要：STT はダミー文字列を返す。

Overlay には WebSocket クライアントとして接続し、{"type":"utter_start","text":...} 等を送る。

検証

make dev

ブラウザ Console に受信 JSON ログ（utter_start/utter_end）が見える

成果物

配管通し（ダミーで往復）

12) 最小テストの作成と緑化

作業

tests/test_llm.py：generate(...,"hello") が str を返す

tests/test_stt.py：任意WAVパス投入→str（空でも可）

tests/test_tts.py：synthesize("テスト") → 実在WAVパス

検証

pytest -q が失敗しない

成果物

最初の受け入れ基準を自動検証

13) Overlay UI 拡張（字幕・口パク）

作業

client.js：受信 utter_start で字幕表示、mouth で 0.0~1.0 に応じて口画像orスプライトを変形、utter_end でリセット。

styles.css：背景透過、テキスト縁取り、画像レイヤ。

検証

make overlay → ブラウザで JS の DOM 変化を確認（document.querySelector(...)）

成果物

表示系の目視OK

14) TTS（ローカル Piper）実装

作業

provider_piper.py：PIPER_VOICE が存在すれば Piper 実行、なければ無音WAVでフォールバック。

生成WAVのRMSから mouth 値をおよそ30–60Hzで配信するロジックを utils.py に追加（短いフレーム RMS → 0–1 正規化）。

検証

PIPER_VOICE 未設定 → 無音WAVで継続（口パクは0のまま）

設定済み → 音が出る、mouth が変動

成果物

オフライン TTS 経路

15) STT（faster-whisper）実装

作業

provider_faster_whisper.py：WHISPER_MODEL_DIR が存在すればロード、無ければダミー文字列を返す。

vad.py は後回し。ここではWAVファイル入力 API の形を確立。

検証

ダミーWAVで transcribe() が空文字でなく返る

モデル未配置でも落ちない

成果物

ローカル STT 経路

16) マイク入力・VAD 追加

作業

vad.py に WebRTC VAD もしくは Silero VAD で発話区間を WAV で切り出す segment_audio_from_mic() を実装。

main.py を差し替え：ループで for seg in segment_audio_from_mic(): ...

検証

短く発話 → 数秒以内に字幕が表示、TTS が再生開始

無音連続で CPU を浪費しない（スリープや閾値あり）

成果物

リアルタイム化

17) LLM（Ollama / OpenAI）実装

作業

provider_ollama.py：OLLAMA_BASE_URL へ /api/chat。失敗時はダミー応答。

provider_openai.py：OPENAI_API_KEY が無ければダミー、あれば ChatCompletions/Responses を使用。

config.py のヘルパで LLM_PROVIDER に応じファクトリ生成。

検証

LLM_PROVIDER=local でも返る（= ダミー）

API キーを適切に入れると本応答に切替

成果物

切替可能な脳

18) Overlay 同期強化（mouth ストリーム）

作業

再生時、WAV バッファを 短フレームで読み取り→RMS→mouth イベントを 一定レートで WS 送信。

再生終了で utter_end。

検証

再生中に Console で mouth が連続到達し、UI で口パクが同期

成果物

体感品質の向上

19) エラーハンドリング・フォールバック一括整備

作業

すべての Provider で：

入力検証

タイムアウト/リトライ

未設定/失敗 → ローカル/ダミーへフォールバック

例外はログに収め、プロセスは継続

ログレベル：INFO/WARNING/ERROR を使い分け

検証

各 API をわざと未設定にして make dev が落ちないこと

成果物

実運用に耐える最低限の堅牢性

20) tests の充実 & 受け入れ基準チェック

作業

受け入れ基準：

pytest -q が成功

make dev で overlay+brain 起動

発話→数秒以内に字幕／続いて音声再生

mouth 値が 0.0–1.0 を推移

.env 切替で例外終了せず

検証

手動・自動の両方で満たすことを確認

成果物

「最小構成 AITuber」完成

21) ドキュメント整備

作業

README.md：

Dev Container 手順

.env 設定例

models/ への配置方法（ファイル名例）

OBS Browser Source 追加手順

既知の制約と TODO

検証

README の手順だけでクリーン環境から再現できる

成果物

再現性の担保

22) 将来タスク（任意）

VOICEVOX HTTP 実装の本配線

Live2D / VRM の口形状ブレンドシェイプ駆動

コメント拾い（配信プラットフォーム API）

ノイズ抑制 / AEC（WebRTC）

メモ（CLIエージェント向け）

すべての外部依存（モデル・APIキー）は未設定でも動作するように。ダミー/無音/エコーで代替。

落とさないことが最優先。常に警告を出し、可能な限り継続。

生成・編集したファイルは 逐次コミット。失敗時は前ステップにロールバック可能にすること。
