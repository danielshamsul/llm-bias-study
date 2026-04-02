from __future__ import annotations

from typing import Iterable

from .clients.anthropic_client import AnthropicClient
from .clients.base import LLMClient
from .clients.mock_client import MockClient
from .clients.openai_client import OpenAIClient
from .clients.xai_client import XAIClient
from .config import Settings
from .prompt_loader import build_prompt_variants, load_prompt_records
from .schemas import ResponseRecord
from .storage import save_responses


def build_clients(settings: Settings, selected_models: Iterable[str] | None = None) -> dict[str, LLMClient]:
    requested = {name.lower() for name in selected_models} if selected_models else {"openai", "anthropic", "xai", "mock"}
    clients: dict[str, LLMClient] = {}

    if "openai" in requested and settings.openai_api_key:
        clients["openai"] = OpenAIClient(
            api_key=settings.openai_api_key,
            model_name=settings.openai_model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
        )
    if "anthropic" in requested and settings.anthropic_api_key:
        clients["anthropic"] = AnthropicClient(
            api_key=settings.anthropic_api_key,
            model_name=settings.anthropic_model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
        )
    if "xai" in requested and settings.xai_api_key:
        clients["xai"] = XAIClient(
            api_key=settings.xai_api_key,
            model_name=settings.xai_model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
        )
    if "mock" in requested and settings.mock_enabled:
        clients["mock"] = MockClient(
            model_name=settings.mock_model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
        )

    if not clients:
        raise RuntimeError(
            "No model clients were configured. Add an API key or enable MOCK_ENABLED=true in your .env file."
        )
    return clients


def run_collection(prompt_file: str, settings: Settings, selected_models: list[str] | None = None) -> tuple[list[ResponseRecord], str]:
    prompt_records = load_prompt_records(prompt_file)
    prompt_variants = build_prompt_variants(prompt_records)
    clients = build_clients(settings, selected_models)

    responses: list[ResponseRecord] = []
    for variant in prompt_variants:
        for provider_name, client in clients.items():
            raw_response = client.generate(variant.prompt_text)
            responses.append(
                ResponseRecord.build(
                    prompt_id=variant.prompt_id,
                    domain=variant.domain,
                    method=variant.method,
                    model_name=f"{provider_name}:{client.model_name}",
                    prompt_text=variant.prompt_text,
                    raw_response=raw_response,
                    ground_truth=variant.ground_truth,
                    source=variant.source,
                    is_contested=variant.is_contested,
                )
            )

    output_path = save_responses(responses, settings.output_dir)
    return responses, str(output_path)
