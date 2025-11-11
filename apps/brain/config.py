"""
Configuration loader for AITuber Brain.
Loads environment variables from .env file with fallback defaults.
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parents[2] / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"Loaded .env from {env_path}")
else:
    print(f"Warning: .env not found at {env_path}, using environment defaults")


def getenv(key: str, default: str = "") -> str:
    """Get environment variable as string."""
    value = os.getenv(key, default)
    if not value and default:
        print(f"Warning: {key} not set, using default: {default}")
    return value


def as_int(key: str, default: int = 0) -> int:
    """Get environment variable as integer."""
    value = os.getenv(key)
    if value is None:
        print(f"Warning: {key} not set, using default: {default}")
        return default
    try:
        return int(value)
    except ValueError:
        print(f"Warning: {key}={value} is not valid int, using default: {default}")
        return default


def as_float(key: str, default: float = 0.0) -> float:
    """Get environment variable as float."""
    value = os.getenv(key)
    if value is None:
        print(f"Warning: {key} not set, using default: {default}")
        return default
    try:
        return float(value)
    except ValueError:
        print(f"Warning: {key}={value} is not valid float, using default: {default}")
        return default


def as_bool(key: str, default: bool = False) -> bool:
    """Get environment variable as boolean."""
    value = os.getenv(key)
    if value is None:
        print(f"Warning: {key} not set, using default: {default}")
        return default
    return value.lower() in ("true", "1", "yes", "on")


# Provider settings
STT_PROVIDER = getenv("STT_PROVIDER", "local")
LLM_PROVIDER = getenv("LLM_PROVIDER", "local")
TTS_PROVIDER = getenv("TTS_PROVIDER", "local")

# Whisper (STT)
WHISPER_MODEL_DIR = getenv("WHISPER_MODEL_DIR", "models/stt/faster-whisper-large-v3")

# Piper (TTS)
PIPER_VOICE = getenv("PIPER_VOICE", "models/tts/ja_JP-nanami-medium.onnx")
PIPER_SAMPLERATE = as_int("PIPER_SAMPLERATE", 22050)

# VOICEVOX (TTS)
VOICEVOX_URL = getenv("VOICEVOX_URL", "http://localhost:50021")
VOICEVOX_SPEAKER_ID = as_int("VOICEVOX_SPEAKER_ID", 1)

# OpenAI
OPENAI_API_KEY = getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = getenv("OPENAI_MODEL", "gpt-4o")
OPENAI_TTS_VOICE = getenv("OPENAI_TTS_VOICE", "nova")
OPENAI_TTS_FORMAT = getenv("OPENAI_TTS_FORMAT", "opus")

# Ollama
OLLAMA_BASE_URL = getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = getenv("OLLAMA_MODEL", "gemma:2b")

# Overlay
OVERLAY_HOST = getenv("OVERLAY_HOST", "0.0.0.0")
OVERLAY_PORT = as_int("OVERLAY_PORT", 5173)

# Brain
BRAIN_HOST = getenv("BRAIN_HOST", "0.0.0.0")
BRAIN_PORT = as_int("BRAIN_PORT", 8000)

# Mic/VAD
USE_MIC = as_bool("USE_MIC", False)
VAD_THRESHOLD = as_float("VAD_THRESHOLD", 0.02)
VAD_SILENCE_DURATION = as_float("VAD_SILENCE_DURATION", 1.5)
