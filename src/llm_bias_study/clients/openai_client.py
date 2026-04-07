from __future__ import annotations

from openai import BadRequestError
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
        request_kwargs = {
            "model": self.model_name,
            "input": prompt,
            "temperature": self.temperature,
            "max_output_tokens": self.max_tokens,
        }
        try:
            response = self.client.responses.create(**request_kwargs)
        except BadRequestError as exc:
            message = _extract_error_message(exc)
            if "temperature" in message.lower() and "not supported" in message.lower():
                request_kwargs.pop("temperature", None)
                response = self.client.responses.create(**request_kwargs)
            else:
                raise
        output_text = getattr(response, "output_text", "") or ""
        if output_text.strip():
            return output_text.strip()
        return _extract_response_text(response)


def _extract_error_message(exc: BadRequestError) -> str:
    body = getattr(exc, "body", None)
    if isinstance(body, dict):
        error = body.get("error")
        if isinstance(error, dict):
            return str(error.get("message", ""))
    return str(exc)


def _extract_response_text(response: object) -> str:
    output_items = getattr(response, "output", None) or []
    text_chunks: list[str] = []

    for item in output_items:
        content_blocks = getattr(item, "content", None) or []
        for block in content_blocks:
            text_value = getattr(block, "text", None)
            if isinstance(text_value, str) and text_value.strip():
                text_chunks.append(text_value)
                continue

            annotation_text = getattr(block, "output_text", None)
            if isinstance(annotation_text, str) and annotation_text.strip():
                text_chunks.append(annotation_text)

    return "\n".join(chunk.strip() for chunk in text_chunks if chunk.strip())
