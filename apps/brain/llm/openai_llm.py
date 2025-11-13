"""OpenAI LLM provider implementation."""
from openai import OpenAI

from apps.brain.config import OPENAI_API_KEY, OPENAI_MODEL
from apps.brain.llm import LLMProvider


class OpenAILLM(LLMProvider):
    """OpenAI API LLM provider."""

    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set")
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        print(f"OpenAI LLM initialized: model={self.model}")

    def generate(self, prompt: str, system_prompt: str = None) -> str:
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                timeout=30.0
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI error: {e}, falling back to dummy")
            return f"（OpenAI接続失敗）{prompt}"
