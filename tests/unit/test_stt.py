"""Unit tests for STT providers."""
import numpy as np

from apps.brain.stt import DummySTT, get_stt_provider


def test_dummy_stt_returns_string():
    """Test DummySTT returns string."""
    stt = DummySTT()
    audio = np.zeros(16000, dtype=np.int16)
    result = stt.transcribe(audio)
    assert isinstance(result, str)
    assert len(result) > 0


def test_get_stt_provider_dummy():
    """Test STT provider factory returns dummy."""
    stt = get_stt_provider("unknown")
    assert isinstance(stt, DummySTT)
