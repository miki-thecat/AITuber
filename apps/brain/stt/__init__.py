"""STT provider interface and implementations."""
from abc import ABC, abstractmethod
import numpy as np


class STTProvider(ABC):
    """Abstract base class for STT providers."""
    
    @abstractmethod
    def transcribe(self, audio_data: np.ndarray, sample_rate: int = 16000) -> str:
        """Transcribe audio data to text."""
        pass


class DummySTT(STTProvider):
    """Dummy STT for testing."""
    
    def transcribe(self, audio_data: np.ndarray, sample_rate: int = 16000) -> str:
        return "（テスト音声入力）こんにちは"


def get_stt_provider(provider_type: str = "local") -> STTProvider:
    """Factory function to get STT provider."""
    if provider_type == "local":
        try:
            from apps.brain.stt.whisper import WhisperSTT
            return WhisperSTT()
        except Exception as e:
            print(f"Warning: Whisper not available, using dummy: {e}")
            return DummySTT()
    elif provider_type == "api":
        try:
            from apps.brain.stt.openai_stt import OpenAISTT
            return OpenAISTT()
        except Exception as e:
            print(f"Warning: OpenAI STT not available, using dummy: {e}")
            return DummySTT()
    else:
        print(f"Warning: Unknown provider {provider_type}, using dummy")
        return DummySTT()
