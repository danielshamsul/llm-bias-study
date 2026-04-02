from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from .schemas import ResponseRecord


def save_responses(records: list[ResponseRecord], output_dir: Path) -> Path:
    response_dir = output_dir / "responses"
    response_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    versioned_path = response_dir / f"responses_{timestamp}.csv"
    latest_path = response_dir / "latest_responses.csv"

    rows = [record.to_dict() for record in records]
    _write_csv(rows, versioned_path)
    _write_csv(rows, latest_path)
    return versioned_path


def save_rows(rows: list[dict], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    _write_csv(rows, path)
    return path


def load_rows(path: str | Path) -> list[dict]:
    with open(path, "r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write("")
        return

    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
