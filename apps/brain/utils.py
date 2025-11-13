"""
Utility functions for AITuber Brain.
Handles audio processing, WAV generation, and mouth value calculation.
"""
import tempfile
import wave
from pathlib import Path
from typing import Tuple

import numpy as np


def generate_silent_wav(duration: float = 1.0, sample_rate: int = 22050) -> str:
    """
    Generate a silent WAV file.

    Args:
        duration: Duration in seconds
        sample_rate: Sample rate in Hz

    Returns:
        Path to the generated WAV file
    """
    num_samples = int(duration * sample_rate)
    silent_audio = np.zeros(num_samples, dtype=np.int16)

    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    temp_path = temp_file.name
    temp_file.close()

    with wave.open(temp_path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(silent_audio.tobytes())

    return temp_path


def read_wav_data(wav_path: str) -> Tuple[np.ndarray, int]:
    """
    Read WAV file and return audio data and sample rate.

    Args:
        wav_path: Path to WAV file

    Returns:
        Tuple of (audio_data as numpy array, sample_rate)
    """
    with wave.open(wav_path, 'r') as wf:
        sample_rate = wf.getframerate()
        n_frames = wf.getnframes()
        audio_bytes = wf.readframes(n_frames)

        # Convert to numpy array
        if wf.getsampwidth() == 2:
            audio_data = np.frombuffer(audio_bytes, dtype=np.int16)
        else:
            audio_data = np.frombuffer(audio_bytes, dtype=np.uint8)

        return audio_data, sample_rate


def calculate_rms(audio_data: np.ndarray) -> float:
    """
    Calculate RMS (Root Mean Square) of audio data.

    Args:
        audio_data: Audio data as numpy array

    Returns:
        RMS value
    """
    return np.sqrt(np.mean(audio_data.astype(float) ** 2))


def audio_to_mouth_values(audio_data: np.ndarray, sample_rate: int,
                          frame_duration: float = 0.033) -> list[float]:
    """
    Convert audio data to mouth values (0.0 to 1.0) for lip-sync.

    Args:
        audio_data: Audio data as numpy array
        sample_rate: Sample rate in Hz
        frame_duration: Duration of each frame in seconds (default: 33ms for ~30Hz)

    Returns:
        List of mouth values normalized to 0.0-1.0
    """
    frame_samples = int(sample_rate * frame_duration)
    mouth_values = []

    # Calculate RMS for each frame
    for i in range(0, len(audio_data), frame_samples):
        frame = audio_data[i:i + frame_samples]
        if len(frame) == 0:
            break

        rms = calculate_rms(frame)
        mouth_values.append(rms)

    if not mouth_values:
        return [0.0]

    # Normalize to 0.0-1.0
    max_rms = max(mouth_values) if max(mouth_values) > 0 else 1.0
    normalized = [min(1.0, val / max_rms) for val in mouth_values]

    return normalized


def cleanup_temp_file(file_path: str) -> None:
    """
    Remove temporary file if it exists.

    Args:
        file_path: Path to file to remove
    """
    try:
        Path(file_path).unlink(missing_ok=True)
    except Exception as e:
        print(f"Warning: Failed to cleanup {file_path}: {e}")
