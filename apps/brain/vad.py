"""
Voice Activity Detection (VAD) module.
Detects speech segments from microphone input.
"""
from typing import Generator

import numpy as np

try:
    import sounddevice as sd
except ImportError:  # pragma: no cover - optional dependency
    sd = None  # type: ignore[assignment]
from apps.brain.config import VAD_SILENCE_DURATION, VAD_THRESHOLD


class VoiceActivityDetector:
    """Simple energy-based VAD for microphone input."""

    def __init__(self, sample_rate: int = 16000, threshold: float = VAD_THRESHOLD,
                 silence_duration: float = VAD_SILENCE_DURATION):
        """
        Initialize VAD.

        Args:
            sample_rate: Audio sample rate in Hz
            threshold: RMS threshold for voice activity
            silence_duration: Duration of silence to end speech segment (seconds)
        """
        self.sample_rate = sample_rate
        self.threshold = threshold
        self.silence_duration = silence_duration
        self.silence_frames = int(silence_duration * sample_rate / 1024)

    def calculate_rms(self, audio_data: np.ndarray) -> float:
        """Calculate RMS energy of audio frame."""
        return np.sqrt(np.mean(audio_data.astype(float) ** 2))

    def segment_audio_from_mic(self, chunk_duration: float = 0.1) -> Generator[np.ndarray, None, None]:
        """
        Capture audio from microphone and yield speech segments.

        Args:
            chunk_duration: Duration of each audio chunk in seconds

        Yields:
            Audio segments as numpy arrays
        """
        if sd is None:
            raise RuntimeError(
                "sounddevice is not installed. Install it to use microphone mode or run text mode."
            )
        chunk_samples = int(self.sample_rate * chunk_duration)
        is_speaking = False
        silence_count = 0
        current_segment = []

        print("VAD: Listening for speech...")

        with sd.InputStream(samplerate=self.sample_rate, channels=1,
                           dtype='int16', blocksize=chunk_samples) as stream:
            while True:
                try:
                    audio_chunk, overflowed = stream.read(chunk_samples)
                    if overflowed:
                        print("Warning: Audio buffer overflow")

                    audio_data = audio_chunk.flatten()
                    rms = self.calculate_rms(audio_data)

                    if rms > self.threshold:
                        # Voice detected
                        if not is_speaking:
                            print(f"VAD: Speech started (RMS: {rms:.4f})")
                            is_speaking = True
                        silence_count = 0
                        current_segment.append(audio_data)
                    else:
                        # Silence
                        if is_speaking:
                            current_segment.append(audio_data)
                            silence_count += 1

                            if silence_count >= self.silence_frames:
                                # End of speech segment
                                print(f"VAD: Speech ended (silence: {silence_count} frames)")
                                if current_segment:
                                    segment = np.concatenate(current_segment)
                                    yield segment
                                current_segment = []
                                is_speaking = False
                                silence_count = 0

                except KeyboardInterrupt:
                    print("\nVAD: Stopped by user")
                    break
                except Exception as e:
                    print(f"VAD Error: {e}")
                    break

        # Yield remaining segment if any
        if current_segment:
            segment = np.concatenate(current_segment)
            yield segment


def get_dummy_audio_segment() -> np.ndarray:
    """
    Generate a dummy audio segment for testing without microphone.

    Returns:
        Dummy audio data as numpy array
    """
    sample_rate = 16000
    duration = 2.0
    num_samples = int(sample_rate * duration)

    # Generate sine wave as dummy audio
    frequency = 440  # A4 note
    t = np.linspace(0, duration, num_samples, False)
    audio = np.sin(2 * np.pi * frequency * t) * 5000

    return audio.astype(np.int16)
