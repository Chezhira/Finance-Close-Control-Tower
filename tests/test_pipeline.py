from __future__ import annotations

from pathlib import Path

from finance_close_control_tower.exports import (
    SYNTHETIC_DISCLAIMER,
    build_close_pack_artifacts,
    write_sample_close_pack,
)
from finance_close_control_tower.ingestion import load_sample_data


def test_sample_close_pack_export(tmp_path: Path) -> None:
    datasets = load_sample_data(Path("data/sample"))
    markdown_path, excel_path = write_sample_close_pack(datasets, tmp_path)

    assert markdown_path.exists()
    assert excel_path.exists()
    content = markdown_path.read_text(encoding="utf-8")
    assert SYNTHETIC_DISCLAIMER in content
    assert "Built by Zahidah Murira" in content
    assert "Close-Readiness Scores" in content
    assert "Exceptions" in content
    assert "CFO Review Lens" in content
    assert "Suggested Finance Actions" in content


def test_close_pack_artifacts_can_be_built_in_memory() -> None:
    datasets = load_sample_data(Path("data/sample"))
    markdown_content, excel_bytes = build_close_pack_artifacts(datasets)

    assert SYNTHETIC_DISCLAIMER in markdown_content
    assert "VAT closing balance variance" in markdown_content
    assert "Action:" in markdown_content
    assert excel_bytes.startswith(b"PK")
