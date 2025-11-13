"""Unit tests for TTS providers."""
from pathlib import Path

from apps.brain.tts import DummyTTS, get_tts_provider
from apps.brain.utils import cleanup_temp_file


def test_dummy_tts_returns_wav():
    """Test DummyTTS returns WAV file path."""
    tts = DummyTTS()
    wav_path = tts.synthesize("test")
    assert Path(wav_path).exists()
    assert wav_path.endswith(".wav")
    cleanup_temp_file(wav_path)


def test_get_tts_provider_dummy():
    """Test TTS provider factory returns dummy."""
    tts = get_tts_provider("unknown")
    assert isinstance(tts, DummyTTS)
