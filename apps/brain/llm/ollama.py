"""Ollama LLM provider implementation."""
import httpx

from apps.brain.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from apps.brain.llm import LLMProvider


class OllamaLLM(LLMProvider):
    """Ollama local LLM provider."""

    def __init__(self):
        self.base_url = OLLAMA_BASE_URL
        self.model = OLLAMA_MODEL
        print(f"Ollama LLM initialized: {self.base_url}, model: {self.model}")

    def generate(self, prompt: str, system_prompt: str = None) -> str:
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result.get("message", {}).get("content", "")
        except Exception as e:
            print(f"Ollama error: {e}, falling back to dummy")
            return f"（Ollama接続失敗）{prompt}"
