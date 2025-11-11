"""Piper TTS implementation."""
import subprocess
import tempfile
from pathlib import Path
from apps.brain.tts import TTSProvider
from apps.brain.config import PIPER_VOICE, PIPER_SAMPLERATE


class PiperTTS(TTSProvider):
    """Piper local TTS provider."""
    
    def __init__(self):
        voice_path = Path(PIPER_VOICE)
        if not voice_path.exists():
            raise FileNotFoundError(f"Piper voice model not found: {voice_path}")
        
        self.voice_path = voice_path
        self.sample_rate = PIPER_SAMPLERATE
        print(f"Piper TTS initialized: {self.voice_path}")
    
    def synthesize(self, text: str) -> str:
        try:
            temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            output_path = temp_wav.name
            temp_wav.close()
            
            result = subprocess.run(
                ["piper", "--model", str(self.voice_path), "--output_file", output_path],
                input=text.encode("utf-8"),
                capture_output=True,
                timeout=10
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Piper failed: {result.stderr.decode()}")
            
            return output_path
        except Exception as e:
            print(f"Piper synthesis error: {e}, falling back to silent")
            from apps.brain.utils import generate_silent_wav
            return generate_silent_wav(duration=len(text) * 0.1)
