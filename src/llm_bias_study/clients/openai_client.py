from __future__ import annotations

from openai import OpenAI

from .base import LLMClient


class OpenAIClient(LLMClient):
    def __init__(
        self,
        api_key: str,
        model_name: str,
        temperature: float,
        max_tokens: int,
    ) -> None:
        super().__init__(model_name=model_name, temperature=temperature, max_tokens=max_tokens)
        self.client = OpenAI(api_key=api_key)

    def generate(self, prompt: str) -> str:
        response = self.client.responses.create(
            model=self.model_name,
            input=prompt,
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
        )
        return response.output_text.strip()
