from __future__ import annotations

import requests

from .base import LLMClient


class GeminiClient(LLMClient):
    def __init__(
        self,
        api_key: str,
        model_name: str,
        temperature: float,
        max_tokens: int,
        api_version: str = "v1beta",
    ) -> None:
        super().__init__(model_name=model_name, temperature=temperature, max_tokens=max_tokens)
        self.api_key = api_key
        self.api_version = api_version
        self.base_url = (
            f"https://generativelanguage.googleapis.com/{self.api_version}/models/"
            f"{self.model_name}:generateContent"
        )

    def generate(self, prompt: str) -> str:
        response = requests.post(
            self.base_url,
            headers={
                "x-goog-api-key": self.api_key,
                "Content-Type": "application/json",
            },
            json={
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": prompt}],
                    }
                ],
                "generationConfig": {
                    "temperature": self.temperature,
                    "maxOutputTokens": self.max_tokens,
                },
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        candidates = payload.get("candidates", [])
        if not candidates:
            return ""
        parts = candidates[0].get("content", {}).get("parts", [])
        return "".join(part.get("text", "") for part in parts).strip()
