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
    markdown_path, excel_path, pdf_path = write_sample_close_pack(datasets, tmp_path)

    assert markdown_path.exists()
    assert excel_path.exists()
    assert pdf_path.exists()
    content = markdown_path.read_text(encoding="utf-8")
    assert SYNTHETIC_DISCLAIMER in content
    assert "Built by Zahidah Murira" in content
    assert "Close-Readiness Scores" in content
    assert "Exceptions" in content
    assert "CFO Review Lens" in content
    assert "Suggested Finance Actions" in content


def test_close_pack_artifacts_can_be_built_in_memory() -> None:
    datasets = load_sample_data(Path("data/sample"))
    artifacts = build_close_pack_artifacts(datasets)

    assert SYNTHETIC_DISCLAIMER in artifacts.markdown
    assert "VAT closing balance variance" in artifacts.markdown
    assert "Action:" in artifacts.markdown
    assert artifacts.excel.startswith(b"PK")
    assert artifacts.pdf.startswith(b"%PDF")


def test_pdf_close_pack_contains_required_report_sections() -> None:
    datasets = load_sample_data(Path("data/sample"))
    artifacts = build_close_pack_artifacts(datasets)
    pdf_text = artifacts.pdf.decode("latin-1")

    assert "Finance Close Control Tower" in pdf_text
    assert "CFO Close Pack" in pdf_text
    assert "Synthetic data demo only" in pdf_text
    assert "Executive summary" in pdf_text
    assert "Overall close-readiness scores" in pdf_text
    assert "Close Readiness Score" in pdf_text
    assert "Exception Count" in pdf_text
    assert "High-risk exception summary" in pdf_text
    assert "Risk Level" in pdf_text
    assert "Suggested Action" in pdf_text
    assert "Ageing and suspense highlights" in pdf_text
    assert "VAT / tax control exceptions" in pdf_text
    assert "Intercompany mismatch summary" in pdf_text
    assert "Management Action Plan" in pdf_text
