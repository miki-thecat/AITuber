"""Faster-whisper STT implementation."""
import numpy as np
import tempfile
import wave
from pathlib import Path
from apps.brain.stt import STTProvider
from apps.brain.config import WHISPER_MODEL_DIR


class WhisperSTT(STTProvider):
    """Faster-whisper local STT provider."""
    
    def __init__(self):
        model_path = Path(WHISPER_MODEL_DIR)
        if not model_path.exists():
            raise FileNotFoundError(f"Whisper model not found: {model_path}")
        
        try:
            from faster_whisper import WhisperModel
            self.model = WhisperModel(str(model_path), device="cpu", compute_type="int8")
            print(f"Whisper STT initialized: {model_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to load Whisper model: {e}")
    
    def transcribe(self, audio_data: np.ndarray, sample_rate: int = 16000) -> str:
        try:
            temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            temp_path = temp_wav.name
            temp_wav.close()
            
            with wave.open(temp_path, 'w') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(audio_data.tobytes())
            
            segments, info = self.model.transcribe(temp_path, language="ja")
            text = " ".join([seg.text for seg in segments])
            
            Path(temp_path).unlink(missing_ok=True)
            return text.strip()
        except Exception as e:
            print(f"Whisper transcription error: {e}")
            return ""
