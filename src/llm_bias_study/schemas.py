from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone


PROMPT_METHODS = (
    "chain_of_thought",
    "delayed_answer",
    "devils_advocate",
)


@dataclass(slots=True)
class PromptRecord:
    prompt_id: str
    domain: str
    base_question: str
    ground_truth: str
    source: str
    is_contested: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class PromptVariant:
    prompt_id: str
    domain: str
    method: str
    prompt_text: str
    ground_truth: str
    source: str
    is_contested: bool

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class ResponseRecord:
    prompt_id: str
    domain: str
    method: str
    model_name: str
    prompt_text: str
    raw_response: str
    ground_truth: str
    source: str
    is_contested: bool
    timestamp_utc: str

    @classmethod
    def build(
        cls,
        prompt_id: str,
        domain: str,
        method: str,
        model_name: str,
        prompt_text: str,
        raw_response: str,
        ground_truth: str,
        source: str,
        is_contested: bool,
    ) -> "ResponseRecord":
        return cls(
            prompt_id=prompt_id,
            domain=domain,
            method=method,
            model_name=model_name,
            prompt_text=prompt_text,
            raw_response=raw_response,
            ground_truth=ground_truth,
            source=source,
            is_contested=is_contested,
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
        )

    def to_dict(self) -> dict:
        return asdict(self)
