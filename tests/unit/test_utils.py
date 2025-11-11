"""Unit tests for utils."""
import numpy as np
from pathlib import Path
from apps.brain.utils import (
    generate_silent_wav, read_wav_data, calculate_rms, 
    audio_to_mouth_values, cleanup_temp_file
)


def test_generate_silent_wav():
    """Test silent WAV generation."""
    wav_path = generate_silent_wav(duration=1.0, sample_rate=22050)
    assert Path(wav_path).exists()
    assert wav_path.endswith(".wav")
    cleanup_temp_file(wav_path)


def test_read_wav_data():
    """Test WAV reading."""
    wav_path = generate_silent_wav(duration=0.5)
    audio_data, sample_rate = read_wav_data(wav_path)
    assert isinstance(audio_data, np.ndarray)
    assert sample_rate > 0
    assert len(audio_data) > 0
    cleanup_temp_file(wav_path)


def test_calculate_rms():
    """Test RMS calculation."""
    audio_data = np.array([0, 100, -100, 50], dtype=np.int16)
    rms = calculate_rms(audio_data)
    assert rms > 0


def test_audio_to_mouth_values():
    """Test mouth value generation."""
    audio_data = np.random.randint(-1000, 1000, size=22050, dtype=np.int16)
    mouth_values = audio_to_mouth_values(audio_data, 22050)
    assert len(mouth_values) > 0
    assert all(0.0 <= v <= 1.0 for v in mouth_values)


def test_cleanup_temp_file():
    """Test file cleanup."""
    wav_path = generate_silent_wav(duration=0.1)
    assert Path(wav_path).exists()
    cleanup_temp_file(wav_path)
    assert not Path(wav_path).exists()
