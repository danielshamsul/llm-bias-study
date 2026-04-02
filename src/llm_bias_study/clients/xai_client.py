from __future__ import annotations

import requests

from .base import LLMClient


class XAIClient(LLMClient):
    def __init__(
        self,
        api_key: str,
        model_name: str,
        temperature: float,
        max_tokens: int,
    ) -> None:
        super().__init__(model_name=model_name, temperature=temperature, max_tokens=max_tokens)
        self.api_key = api_key
        self.base_url = "https://api.x.ai/v1/chat/completions"

    def generate(self, prompt: str) -> str:
        response = requests.post(
            self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model_name,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        return payload["choices"][0]["message"]["content"].strip()
