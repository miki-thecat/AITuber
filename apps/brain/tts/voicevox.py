"""VOICEVOX TTS implementation."""
import tempfile

import httpx

from apps.brain.config import VOICEVOX_SPEAKER_ID, VOICEVOX_URL
from apps.brain.tts import TTSProvider


class VoicevoxTTS(TTSProvider):
    """VOICEVOX HTTP API TTS provider."""

    def __init__(self):
        self.base_url = VOICEVOX_URL
        self.speaker_id = VOICEVOX_SPEAKER_ID

        # Check if VOICEVOX is available
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/speakers")
                response.raise_for_status()
            print(f"VOICEVOX TTS initialized: {self.base_url}, speaker: {self.speaker_id}")
        except Exception as e:
            raise RuntimeError(f"VOICEVOX not available: {e}")

    def synthesize(self, text: str) -> str:
        try:
            with httpx.Client(timeout=30.0) as client:
                # Generate audio query
                query_response = client.post(
                    f"{self.base_url}/audio_query",
                    params={"text": text, "speaker": self.speaker_id}
                )
                query_response.raise_for_status()
                audio_query = query_response.json()

                # Synthesize
                synthesis_response = client.post(
                    f"{self.base_url}/synthesis",
                    params={"speaker": self.speaker_id},
                    json=audio_query
                )
                synthesis_response.raise_for_status()

                # Save to file
                temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                output_path = temp_wav.name
                temp_wav.write(synthesis_response.content)
                temp_wav.close()

                return output_path
        except Exception as e:
            print(f"VOICEVOX synthesis error: {e}, falling back to silent")
            from apps.brain.utils import generate_silent_wav
            return generate_silent_wav(duration=len(text) * 0.1)
