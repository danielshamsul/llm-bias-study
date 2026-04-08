from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass(slots=True)
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    xai_api_key: str = os.getenv("XAI_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    mock_enabled: bool = os.getenv("MOCK_ENABLED", "true").strip().lower() in {"true", "1", "yes", "y"}
    mock_model: str = os.getenv("MOCK_MODEL", "demo-model")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1")
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")
    xai_model: str = os.getenv("XAI_MODEL", "grok-2-latest")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    gemini_api_version: str = os.getenv("GEMINI_API_VERSION", "v1beta")
    output_dir: Path = Path(os.getenv("OUTPUT_DIR", "outputs"))
    temperature: float = 0.0
    max_tokens: int = 800

    def ensure_output_dirs(self) -> None:
        (self.output_dir / "responses").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "analysis").mkdir(parents=True, exist_ok=True)


def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_output_dirs()
    return settings
