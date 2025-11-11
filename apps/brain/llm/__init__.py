"""LLM provider interface and implementations."""
from abc import ABC, abstractmethod
from typing import Optional


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text response from prompt."""
        pass


class DummyLLM(LLMProvider):
    """Dummy LLM that echoes input for testing."""
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return f"（テスト応答）{prompt}"


def get_llm_provider(provider_type: str = "local") -> LLMProvider:
    """Factory function to get LLM provider."""
    if provider_type == "local":
        try:
            from apps.brain.llm.ollama import OllamaLLM
            return OllamaLLM()
        except Exception as e:
            print(f"Warning: Ollama not available, using dummy: {e}")
            return DummyLLM()
    elif provider_type == "api":
        try:
            from apps.brain.llm.openai_llm import OpenAILLM
            return OpenAILLM()
        except Exception as e:
            print(f"Warning: OpenAI not available, using dummy: {e}")
            return DummyLLM()
    else:
        print(f"Warning: Unknown provider {provider_type}, using dummy")
        return DummyLLM()
