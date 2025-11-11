"""OpenAI TTS implementation."""
import tempfile
from pathlib import Path
from openai import OpenAI
from apps.brain.tts import TTSProvider
from apps.brain.config import OPENAI_API_KEY, OPENAI_TTS_VOICE, OPENAI_TTS_FORMAT


class OpenAITTS(TTSProvider):
    """OpenAI TTS API provider."""
    
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set")
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.voice = OPENAI_TTS_VOICE
        self.format = OPENAI_TTS_FORMAT
        print(f"OpenAI TTS initialized: voice={self.voice}, format={self.format}")
    
    def synthesize(self, text: str) -> str:
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=self.voice,
                input=text,
                response_format=self.format
            )
            
            suffix = f".{self.format}" if self.format != "opus" else ".opus"
            temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
            output_path = temp_file.name
            temp_file.write(response.content)
            temp_file.close()
            
            # Convert to WAV if needed
            if self.format != "wav":
                import subprocess
                wav_path = output_path.replace(suffix, ".wav")
                subprocess.run(
                    ["ffmpeg", "-i", output_path, "-y", wav_path],
                    capture_output=True,
                    check=True
                )
                Path(output_path).unlink(missing_ok=True)
                return wav_path
            
            return output_path
        except Exception as e:
            print(f"OpenAI TTS error: {e}, falling back to silent")
            from apps.brain.utils import generate_silent_wav
            return generate_silent_wav(duration=len(text) * 0.1)
