from __future__ import annotations

import json
from pathlib import Path

from .evaluation import validate_scored_rubric
from .storage import load_rows, save_rows


ACCURACY_MAP = {
    "incorrect": 0,
    "partially_correct": 0.5,
    "appropriately_uncertain": 0.75,
    "correct": 1,
}

HALLUCINATION_MAP = {
    "fabricated_or_misattributed": 1,
    "no_citation": 0,
    "accurate_citation": 0,
}


def analyze_results(responses_path: str, rubric_path: str, output_dir: Path) -> dict[str, Path]:
    responses = load_rows(responses_path)
    rubric = validate_scored_rubric(rubric_path)

    rubric_lookup = {
        (row["prompt_id"], row["domain"], row["method"], row["model_name"]): row for row in rubric
    }
    merged: list[dict] = []
    for response in responses:
        key = (
            response["prompt_id"],
            response["domain"],
            response["method"],
            response["model_name"],
        )
        scored = rubric_lookup.get(key, {})
        merged_row = dict(response)
        merged_row["factual_accuracy"] = scored.get("factual_accuracy", "")
        merged_row["citation_integrity"] = scored.get("citation_integrity", "")
        merged_row["confidence_calibration"] = scored.get("confidence_calibration", "")
        merged_row["reviewer_id"] = scored.get("reviewer_id", "")
        merged_row["notes"] = scored.get("notes", "")
        merged_row["accuracy_score"] = ACCURACY_MAP.get(merged_row["factual_accuracy"], "")
        merged_row["hallucination_flag"] = HALLUCINATION_MAP.get(merged_row["citation_integrity"], "")
        merged.append(merged_row)

    summary_by_model_method = _summarize(
        merged,
        group_keys=["model_name", "method"],
    )
    summary_by_domain = _summarize(
        merged,
        group_keys=["domain", "model_name"],
    )

    analysis_dir = output_dir / "analysis"
    merged_path = save_rows(merged, analysis_dir / "merged_scored_results.csv")
    model_method_path = save_rows(summary_by_model_method, analysis_dir / "summary_by_model_method.csv")
    domain_path = save_rows(summary_by_domain, analysis_dir / "summary_by_domain.csv")
    json_path = analysis_dir / "summary.json"
    json_path.write_text(
        json.dumps(
            {
                "summary_by_model_method": summary_by_model_method,
                "summary_by_domain": summary_by_domain,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    return {
        "merged": merged_path,
        "model_method_summary": model_method_path,
        "domain_summary": domain_path,
        "summary_json": json_path,
    }


def _summarize(rows: list[dict], group_keys: list[str]) -> list[dict]:
    grouped: dict[tuple, dict] = {}
    for row in rows:
        key = tuple(row[group_key] for group_key in group_keys)
        bucket = grouped.setdefault(
            key,
            {
                **{group_key: row[group_key] for group_key in group_keys},
                "accuracy_total": 0.0,
                "accuracy_count": 0,
                "hallucination_total": 0.0,
                "hallucination_count": 0,
                "sample_size": 0,
            },
        )
        bucket["sample_size"] += 1
        if row["accuracy_score"] != "":
            bucket["accuracy_total"] += float(row["accuracy_score"])
            bucket["accuracy_count"] += 1
        if row["hallucination_flag"] != "":
            bucket["hallucination_total"] += float(row["hallucination_flag"])
            bucket["hallucination_count"] += 1

    summaries: list[dict] = []
    for bucket in grouped.values():
        accuracy_count = bucket.pop("accuracy_count")
        hallucination_count = bucket.pop("hallucination_count")
        accuracy_total = bucket.pop("accuracy_total")
        hallucination_total = bucket.pop("hallucination_total")
        bucket["mean_accuracy"] = (
            round(accuracy_total / accuracy_count, 4) if accuracy_count else ""
        )
        bucket["hallucination_rate"] = (
            round(hallucination_total / hallucination_count, 4) if hallucination_count else ""
        )
        summaries.append(bucket)
    return summaries
