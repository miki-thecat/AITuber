#!/bin/bash
set -e

echo "Downloading AI models..."

# Create directories
mkdir -p models/stt models/tts

# Whisper model (placeholder - user needs to download manually)
echo "To download Whisper model:"
echo "  pip install huggingface-hub"
echo "  huggingface-cli download Systran/faster-whisper-large-v3 --local-dir models/stt/faster-whisper-large-v3"

# Piper model (placeholder)
echo ""
echo "To download Piper voice model:"
echo "  Visit: https://github.com/rhasspy/piper/releases"
echo "  Download a Japanese voice model (e.g., ja_JP-nanami-medium.onnx)"
echo "  Place in: models/tts/"

echo ""
echo "Models directory structure created!"
echo "Please manually download models as indicated above."
