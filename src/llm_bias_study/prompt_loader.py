from __future__ import annotations
import csv

from .schemas import PROMPT_METHODS, PromptRecord, PromptVariant


PROMPT_TEMPLATES = {
    "direct": (
        "Answer the following fact-based question as accurately as possible.\n\n"
        "Question: {question}\n\n"
        "Return a concise answer and briefly explain your reasoning."
    ),
    "chain_of_thought": (
        "You are answering a fact-based research question.\n\n"
        "Question: {question}\n\n"
        "Reason step by step before giving your final answer. After your reasoning, "
        "write a line that starts with 'Final Answer:'."
    ),
    "delayed_answer": (
        "You are answering a fact-based research question.\n\n"
        "Question: {question}\n\n"
        "Do not give a final answer immediately. First consider at least three plausible "
        "interpretations or answer paths, then decide which one is best supported by evidence. "
        "After that, write a line that starts with 'Final Answer:'."
    ),
    "devils_advocate": (
        "You are answering a fact-based research question.\n\n"
        "Question: {question}\n\n"
        "First provide your best answer. Then argue the strongest opposing position. "
        "Finally explain what assumption would make your initial answer wrong and end with "
        "a line that starts with 'Final Answer:'."
    ),
}


def load_prompt_records(csv_path: str) -> list[PromptRecord]:
    required_columns = {
        "prompt_id",
        "domain",
        "base_question",
        "ground_truth",
        "source",
        "is_contested",
    }
    records: list[PromptRecord] = []
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("Prompt file is empty or missing a header row.")
        missing_columns = required_columns.difference(reader.fieldnames)
        if missing_columns:
            missing_display = ", ".join(sorted(missing_columns))
            raise ValueError(f"Prompt file is missing required columns: {missing_display}")

        for row in reader:
            records.append(
                PromptRecord(
                    prompt_id=str(row["prompt_id"]).strip(),
                    domain=str(row["domain"]).strip(),
                    base_question=str(row["base_question"]).strip(),
                    ground_truth=str(row["ground_truth"]).strip(),
                    source=str(row["source"]).strip(),
                    is_contested=_to_bool(row["is_contested"]),
                )
            )
    return records


def build_prompt_variants(records: list[PromptRecord]) -> list[PromptVariant]:
    variants: list[PromptVariant] = []
    for record in records:
        for method in PROMPT_METHODS:
            template = PROMPT_TEMPLATES[method]
            variants.append(
                PromptVariant(
                    prompt_id=record.prompt_id,
                    domain=record.domain,
                    method=method,
                    prompt_text=template.format(question=record.base_question),
                    ground_truth=record.ground_truth,
                    source=record.source,
                    is_contested=record.is_contested,
                )
            )
    return variants


def _to_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}
