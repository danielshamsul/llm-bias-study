from __future__ import annotations

from abc import ABC, abstractmethod


class LLMClient(ABC):
    def __init__(self, model_name: str, temperature: float, max_tokens: int) -> None:
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

    @property
    def provider_name(self) -> str:
        return self.__class__.__name__.replace("Client", "").lower()

    @abstractmethod
    def generate(self, prompt: str) -> str:
        raise NotImplementedError
