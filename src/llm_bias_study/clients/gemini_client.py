from __future__ import annotations

import requests
from requests import HTTPError

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
        try:
            response.raise_for_status()
        except HTTPError as exc:
            error_detail = _extract_error_text(response)
            if error_detail:
                raise RuntimeError(
                    f"Gemini API request failed with status {response.status_code}: {error_detail}"
                ) from exc
            raise
        payload = response.json()
        candidates = payload.get("candidates", [])
        if not candidates:
            return ""
        parts = candidates[0].get("content", {}).get("parts", [])
        return "".join(part.get("text", "") for part in parts).strip()


def _extract_error_text(response: requests.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return response.text.strip()

    error = payload.get("error")
    if isinstance(error, dict):
        message = error.get("message", "")
        status = error.get("status", "")
        if message and status:
            return f"{status}: {message}"
        return message or status
    return response.text.strip()
