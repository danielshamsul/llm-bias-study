from __future__ import annotations

from pathlib import Path

from .storage import load_rows, save_rows


RUBRIC_COLUMNS = [
    "reviewer_id",
    "factual_accuracy",
    "citation_integrity",
    "confidence_calibration",
    "notes",
]


def build_rubric_template(responses_path: str, output_dir: Path) -> Path:
    rows = load_rows(responses_path)
    rubric_rows: list[dict] = []
    for row in rows:
        rubric_row = dict(row)
        for column in RUBRIC_COLUMNS:
            rubric_row[column] = ""
        rubric_rows.append(rubric_row)

    output_path = output_dir / "analysis" / "rubric_template.csv"
    return save_rows(rubric_rows, output_path)


def validate_scored_rubric(rubric_path: str) -> list[dict]:
    rows = load_rows(rubric_path)
    if not rows:
        raise ValueError("Rubric file is empty.")
    required_columns = {
        "prompt_id",
        "domain",
        "method",
        "model_name",
        "factual_accuracy",
        "citation_integrity",
        "confidence_calibration",
    }
    missing_columns = required_columns.difference(rows[0].keys())
    if missing_columns:
        missing_display = ", ".join(sorted(missing_columns))
        raise ValueError(f"Rubric file is missing required columns: {missing_display}")
    return rows
