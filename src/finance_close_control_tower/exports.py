from __future__ import annotations

from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path

import pandas as pd

from finance_close_control_tower.config import DEFAULT_CONFIG
from finance_close_control_tower.scoring import (
    calculate_overall_scores,
    calculate_process_scores,
    process_scores_to_frame,
)
from finance_close_control_tower.validations import (
    run_all_validations,
    validation_results_to_frame,
)

SYNTHETIC_DISCLAIMER = (
    "Synthetic data demo only. No employer, client, bank, payroll, customer, supplier, "
    "tax authority, or confidential company data is included."
)

PROCESS_GUIDANCE = {
    "reconciliations": {
        "what_it_means": "A material balance sheet account has not completed prepare-and-review.",
        "why_it_matters": (
            "Unreviewed reconciliations weaken balance sheet support and close sign-off."
        ),
        "finance_action": "Complete review, attach support, and clear reviewer comments.",
    },
    "suspense": {
        "what_it_means": "A suspense or clearing account still carries a material balance.",
        "why_it_matters": (
            "Suspense can hide miscoding, timing breaks, or unresolved accounting noise."
        ),
        "finance_action": "Investigate, reclassify valid items, and clear unsupported balances.",
    },
    "bank_rec": {
        "what_it_means": "A bank reconciliation item is aged, unknown, or under investigation.",
        "why_it_matters": "Unexplained cash items reduce confidence in reported cash.",
        "finance_action": "Match to bank or ledger support and post any required correction.",
    },
    "vat": {
        "what_it_means": "The VAT control movement does not reconcile to the closing balance.",
        "why_it_matters": "VAT breaks can create statutory reporting and filing risk.",
        "finance_action": (
            "Reperform the VAT bridge and investigate payments, refunds, inputs, outputs, "
            "and adjustments."
        ),
    },
    "intercompany": {
        "what_it_means": "An intercompany balance does not eliminate between entity records.",
        "why_it_matters": "Group reporting needs mirrored balances before consolidation.",
        "finance_action": (
            "Confirm counterparty posting, currency, reference, and book the missing side "
            "or correction."
        ),
    },
}


def _pluralize_exception(count: int) -> str:
    return "exception" if count == 1 else "exceptions"


def _add_exception_guidance(exception_frame: pd.DataFrame) -> pd.DataFrame:
    enriched = exception_frame.copy()
    if enriched.empty:
        return enriched
    enriched["what_it_means"] = enriched["process_area"].map(
        lambda process: PROCESS_GUIDANCE.get(str(process), {}).get("what_it_means", "")
    )
    enriched["why_it_matters"] = enriched["process_area"].map(
        lambda process: PROCESS_GUIDANCE.get(str(process), {}).get("why_it_matters", "")
    )
    enriched["finance_action"] = enriched["process_area"].map(
        lambda process: PROCESS_GUIDANCE.get(str(process), {}).get("finance_action", "")
    )
    return enriched


def build_close_pack_artifacts(
    datasets: dict[str, pd.DataFrame],
    *,
    period: str = "2026-05",
) -> tuple[str, bytes]:
    generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    validation_results = run_all_validations(datasets)
    exception_frame = validation_results_to_frame(validation_results)
    enriched_exception_frame = _add_exception_guidance(exception_frame)
    process_scores = calculate_process_scores(datasets, validation_results)
    process_score_frame = process_scores_to_frame(process_scores)
    overall_score_frame = calculate_overall_scores(process_scores)
    selected_overall = overall_score_frame[overall_score_frame["period"].astype(str) == period]

    row_lines = "\n".join(
        f"- {filename}: {len(frame):,} rows, {len(frame.columns):,} columns"
        for filename, frame in sorted(datasets.items())
    )
    score_lines = "\n".join(
        f"- {row.entity}: {row.score}/100 ({row.status}), {row.exception_count} "
        f"{_pluralize_exception(row.exception_count)}"
        for row in selected_overall.itertuples(index=False)
    )
    exception_lines = "\n".join(
        f"- [{row.severity.upper()}] {row.process_area} | {row.entity} | {row.message} "
        f"Action: {row.finance_action}"
        for row in enriched_exception_frame.itertuples(index=False)
    )
    content = f"""# Finance Close Control Tower - Sample Close Pack

Built by Zahidah Murira | Finance Engineer Portfolio | Synthetic Data Demo

{SYNTHETIC_DISCLAIMER}

## Run Metadata

- Generated at: {generated_at}
- Selected period: {period}
- Rule version: {DEFAULT_CONFIG.rule_version}
- Source files: {len(datasets)}

## Source File Summary

{row_lines}

## CFO Review Lens

This pack shows whether the synthetic close is ready for reporting, where control risk is
concentrated, and which finance actions should happen before close sign-off.

## Close-Readiness Scores

{score_lines}

## Exceptions

{exception_lines}

## Suggested Finance Actions

- Clear or review critical reconciliation and VAT exceptions before sign-off.
- Investigate aged cash and suspense items before final management reporting.
- Resolve intercompany mismatches before consolidation or group reporting.
- Keep the synthetic-data disclaimer with any shared portfolio outputs.

## Management Summary

The MVP sample pipeline loaded bundled synthetic finance exports, applied schema and privacy
checks, ran deterministic close-control validation rules, calculated close-readiness scores,
and produced exception detail for management review.
"""
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        _write_excel_close_pack(
            writer,
            generated_at=generated_at,
            period=period,
            overall_score_frame=overall_score_frame,
            process_score_frame=process_score_frame,
            exception_frame=enriched_exception_frame,
            datasets=datasets,
        )

    return content, excel_buffer.getvalue()


def _write_excel_close_pack(
    writer: pd.ExcelWriter,
    *,
    generated_at: str,
    period: str,
    overall_score_frame: pd.DataFrame,
    process_score_frame: pd.DataFrame,
    exception_frame: pd.DataFrame,
    datasets: dict[str, pd.DataFrame],
) -> None:
    pd.DataFrame(
        [
            {
                "project": "Finance Close Control Tower",
                "author": "Zahidah Murira",
                "generated_at": generated_at,
                "selected_period": period,
                "rule_version": DEFAULT_CONFIG.rule_version,
                "disclaimer": SYNTHETIC_DISCLAIMER,
            }
        ]
    ).to_excel(writer, sheet_name="Cover", index=False)
    overall_score_frame.to_excel(writer, sheet_name="Overall Scores", index=False)
    process_score_frame.to_excel(writer, sheet_name="Process Scores", index=False)
    exception_frame.to_excel(writer, sheet_name="Exceptions", index=False)
    pd.DataFrame(
        [
            {
                "process_area": process_area,
                **guidance,
            }
            for process_area, guidance in PROCESS_GUIDANCE.items()
        ]
    ).to_excel(writer, sheet_name="Finance Guidance", index=False)
    pd.DataFrame(
        [
            {"source_file": filename, "rows": len(frame), "columns": len(frame.columns)}
            for filename, frame in sorted(datasets.items())
        ]
    ).to_excel(writer, sheet_name="Source Files", index=False)

    workbook = writer.book
    workbook.properties.creator = "Zahidah Murira"
    workbook.properties.title = "Finance Close Control Tower Sample Close Pack"
    workbook.properties.subject = "Synthetic data demo close pack"


def write_sample_close_pack(
    datasets: dict[str, pd.DataFrame],
    output_dir: Path,
    *,
    period: str = "2026-05",
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = output_dir / "sample_close_pack_summary.md"
    excel_path = output_dir / "sample_close_pack.xlsx"
    markdown_content, excel_bytes = build_close_pack_artifacts(datasets, period=period)

    markdown_path.write_text(markdown_content, encoding="utf-8")
    excel_path.write_bytes(excel_bytes)

    return markdown_path, excel_path
