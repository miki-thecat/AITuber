"""OpenAI Whisper API STT implementation."""
import numpy as np
import tempfile
import wave
from pathlib import Path
from openai import OpenAI
from apps.brain.stt import STTProvider
from apps.brain.config import OPENAI_API_KEY


class OpenAISTT(STTProvider):
    """OpenAI Whisper API STT provider."""
    
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set")
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        print("OpenAI STT initialized")
    
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
            
            with open(temp_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ja"
                )
            
            Path(temp_path).unlink(missing_ok=True)
            return transcript.text.strip()
        except Exception as e:
            print(f"OpenAI STT error: {e}")
            return ""
