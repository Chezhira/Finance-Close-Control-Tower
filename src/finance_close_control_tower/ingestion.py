from __future__ import annotations

from pathlib import Path

import pandas as pd

from finance_close_control_tower.privacy import scan_file
from finance_close_control_tower.schema import (
    SCHEMAS,
    missing_required_columns,
    normalize_column_name,
)

ALLOWED_SUFFIXES = {".csv", ".xlsx"}


class IngestionError(ValueError):
    """Raised when a sample file cannot be safely loaded or validated."""


def read_dataset(path: Path) -> pd.DataFrame:
    if path.suffix.lower() not in ALLOWED_SUFFIXES:
        raise IngestionError(f"Unsupported file type for {path.name}")

    if path.suffix.lower() == ".csv":
        frame = pd.read_csv(path)
    else:
        frame = pd.read_excel(path, engine="openpyxl")

    frame.columns = [normalize_column_name(column) for column in frame.columns]
    return frame


def load_sample_dataset(path: Path) -> pd.DataFrame:
    schema = SCHEMAS.get(path.name)
    if schema is None:
        raise IngestionError(f"No registered schema for {path.name}")

    frame = read_dataset(path)
    missing = missing_required_columns(list(frame.columns), schema)
    if missing:
        raise IngestionError(f"{path.name} is missing required columns: {', '.join(missing)}")

    scan_file(frame, path)
    return frame


def load_sample_data(data_dir: Path) -> dict[str, pd.DataFrame]:
    datasets: dict[str, pd.DataFrame] = {}
    for filename in sorted(SCHEMAS):
        path = data_dir / filename
        if not path.exists():
            raise IngestionError(f"Missing required sample file: {filename}")
        datasets[filename] = load_sample_dataset(path)
    return datasets
