"""TTS provider interface and implementations."""
from abc import ABC, abstractmethod


class TTSProvider(ABC):
    """Abstract base class for TTS providers."""
    
    @abstractmethod
    def synthesize(self, text: str) -> str:
        """Synthesize text to speech and return WAV file path."""
        pass


class DummyTTS(TTSProvider):
    """Dummy TTS that generates silent audio."""
    
    def synthesize(self, text: str) -> str:
        from apps.brain.utils import generate_silent_wav
        return generate_silent_wav(duration=1.0)


def get_tts_provider(provider_type: str = "local") -> TTSProvider:
    """Factory function to get TTS provider."""
    if provider_type == "local":
        try:
            from apps.brain.tts.piper import PiperTTS
            return PiperTTS()
        except Exception as e:
            print(f"Warning: Piper not available, using dummy: {e}")
            return DummyTTS()
    elif provider_type == "api":
        api_provider = _try_api_providers()
        if api_provider:
            return api_provider
        print("Warning: No API TTS available, using dummy")
        return DummyTTS()
    else:
        print(f"Warning: Unknown provider {provider_type}, using dummy")
        return DummyTTS()


def _try_api_providers() -> TTSProvider:
    """Try to initialize API TTS providers in order."""
    try:
        from apps.brain.tts.voicevox import VoicevoxTTS
        return VoicevoxTTS()
    except Exception:
        pass
    
    try:
        from apps.brain.tts.openai_tts import OpenAITTS
        return OpenAITTS()
    except Exception:
        pass
    
    return None
