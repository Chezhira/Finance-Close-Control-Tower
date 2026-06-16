from __future__ import annotations

from pathlib import Path

from finance_close_control_tower.ingestion import load_sample_data
from finance_close_control_tower.schema import SCHEMAS, missing_required_columns

DATA_DIR = Path("data/sample")


def test_required_sample_files_exist() -> None:
    for filename in SCHEMAS:
        assert (DATA_DIR / filename).exists(), filename


def test_sample_files_have_required_columns() -> None:
    datasets = load_sample_data(DATA_DIR)
    assert set(datasets) == set(SCHEMAS)

    for filename, frame in datasets.items():
        missing = missing_required_columns(list(frame.columns), SCHEMAS[filename])
        assert missing == []
