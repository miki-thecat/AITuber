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
