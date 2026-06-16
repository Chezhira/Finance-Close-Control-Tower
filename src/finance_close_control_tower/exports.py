from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path

import pandas as pd
from fpdf import FPDF

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


@dataclass(frozen=True)
class ClosePackArtifacts:
    markdown: str
    excel: bytes
    pdf: bytes


@dataclass(frozen=True)
class ClosePackModel:
    generated_at: str
    period: str
    entity_scope: str
    exception_frame: pd.DataFrame
    overall_score_frame: pd.DataFrame
    process_score_frame: pd.DataFrame
    datasets: dict[str, pd.DataFrame]


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


def _build_close_pack_model(
    datasets: dict[str, pd.DataFrame],
    *,
    period: str,
    entity_scope: str,
) -> ClosePackModel:
    validation_results = run_all_validations(datasets)
    exception_frame = _add_exception_guidance(validation_results_to_frame(validation_results))
    process_scores = calculate_process_scores(datasets, validation_results)
    return ClosePackModel(
        generated_at=datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC"),
        period=period,
        entity_scope=entity_scope,
        exception_frame=exception_frame,
        overall_score_frame=calculate_overall_scores(process_scores),
        process_score_frame=process_scores_to_frame(process_scores),
        datasets=datasets,
    )


def build_close_pack_artifacts(
    datasets: dict[str, pd.DataFrame],
    *,
    period: str = "2026-05",
    entity_scope: str = "All sample entities",
) -> ClosePackArtifacts:
    model = _build_close_pack_model(datasets, period=period, entity_scope=entity_scope)
    selected_overall = model.overall_score_frame[
        model.overall_score_frame["period"].astype(str) == period
    ]

    row_lines = "\n".join(
        f"- {filename}: {len(frame):,} rows, {len(frame.columns):,} columns"
        for filename, frame in sorted(model.datasets.items())
    )
    score_lines = "\n".join(
        f"- {row.entity}: {row.score}/100 ({row.status}), {row.exception_count} "
        f"{_pluralize_exception(row.exception_count)}"
        for row in selected_overall.itertuples(index=False)
    )
    exception_lines = "\n".join(
        f"- [{row.severity.upper()}] {row.process_area} | {row.entity} | {row.message} "
        f"Action: {row.finance_action}"
        for row in model.exception_frame.itertuples(index=False)
    )
    content = f"""# Finance Close Control Tower - Sample Close Pack

Built by Zahidah Murira | Finance Engineer Portfolio | Synthetic Data Demo

{SYNTHETIC_DISCLAIMER}

## Run Metadata

- Generated at: {model.generated_at}
- Entity scope: {model.entity_scope}
- Selected period: {model.period}
- Rule version: {DEFAULT_CONFIG.rule_version}
- Source files: {len(model.datasets)}

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
            generated_at=model.generated_at,
            period=model.period,
            overall_score_frame=model.overall_score_frame,
            process_score_frame=model.process_score_frame,
            exception_frame=model.exception_frame,
            datasets=model.datasets,
        )

    pdf_bytes = _build_pdf_close_pack(model)
    return ClosePackArtifacts(
        markdown=content,
        excel=excel_buffer.getvalue(),
        pdf=pdf_bytes,
    )


class ClosePackPDF(FPDF):
    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("Helvetica", size=8)
        self.set_text_color(90, 90, 90)
        self.cell(
            0,
            6,
            "Synthetic portfolio demo | Finance Close Control Tower | Zahidah Murira",
            align="C",
        )


def _format_process_area(process_area: str) -> str:
    return process_area.replace("_", " ").title()


def _truncate_cell(value: object, max_chars: int) -> str:
    text = "" if pd.isna(value) else str(value)
    text = " ".join(text.split())
    if len(text) <= max_chars:
        return text
    return f"{text[: max_chars - 3]}..."


def _ensure_pdf_space(pdf: FPDF, height: float) -> None:
    if pdf.get_y() + height > pdf.page_break_trigger:
        pdf.add_page()


def _write_pdf_heading(pdf: FPDF, title: str) -> None:
    _ensure_pdf_space(pdf, 14)
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT", border="B")
    pdf.ln(2)


def _write_pdf_paragraph(pdf: FPDF, text: str, *, fill: bool = False) -> None:
    _ensure_pdf_space(pdf, 18)
    pdf.set_font("Helvetica", size=9)
    pdf.set_text_color(45, 45, 45)
    pdf.set_x(pdf.l_margin)
    if fill:
        pdf.set_fill_color(245, 246, 248)
        pdf.set_draw_color(210, 214, 220)
        pdf.multi_cell(0, 5.5, text, border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.multi_cell(0, 5.5, text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)


def _write_pdf_table(
    pdf: FPDF,
    headers: list[str],
    rows: list[list[object]],
    widths: list[float],
    *,
    max_chars: list[int],
    aligns: list[str] | None = None,
) -> None:
    aligns = aligns or ["L"] * len(headers)
    row_height = 6.5
    _ensure_pdf_space(pdf, row_height * (min(len(rows), 3) + 2))
    pdf.set_draw_color(190, 196, 204)
    pdf.set_line_width(0.2)
    pdf.set_font("Helvetica", style="B", size=8)
    pdf.set_text_color(30, 30, 30)
    pdf.set_fill_color(232, 235, 239)
    for header, width in zip(headers, widths, strict=True):
        pdf.cell(width, row_height, header, border=1, fill=True)
    pdf.ln(row_height)

    pdf.set_font("Helvetica", size=7.5)
    pdf.set_text_color(40, 40, 40)
    if not rows:
        pdf.cell(sum(widths), row_height, "No exceptions detected.", border=1)
        pdf.ln(row_height)
        pdf.ln(3)
        return

    for row in rows:
        _ensure_pdf_space(pdf, row_height * 2)
        for value, width, max_char, align in zip(row, widths, max_chars, aligns, strict=True):
            pdf.cell(
                width,
                row_height,
                _truncate_cell(value, max_char),
                border=1,
                align=align,
            )
        pdf.ln(row_height)
    pdf.ln(3)


def _exception_rows(frame: pd.DataFrame) -> list[list[object]]:
    return [
        [
            str(row.severity).upper(),
            row.entity,
            _format_process_area(str(row.process_area)),
            row.message,
            row.finance_action,
        ]
        for row in frame.itertuples(index=False)
    ]


def _score_rows(frame: pd.DataFrame) -> list[list[object]]:
    return [
        [
            row.entity,
            f"{float(row.score):.1f}/100",
            str(row.status).title(),
            int(row.exception_count),
        ]
        for row in frame.itertuples(index=False)
    ]


def _build_pdf_close_pack(model: ClosePackModel) -> bytes:
    selected_overall = model.overall_score_frame[
        model.overall_score_frame["period"].astype(str) == model.period
    ]
    high_risk = model.exception_frame[
        model.exception_frame["severity"].astype(str).isin(["critical", "high"])
    ]
    bank_and_suspense = model.exception_frame[
        model.exception_frame["process_area"].astype(str).isin(["bank_rec", "suspense"])
    ]
    vat_exceptions = model.exception_frame[
        model.exception_frame["process_area"].astype(str) == "vat"
    ]
    intercompany = model.exception_frame[
        model.exception_frame["process_area"].astype(str) == "intercompany"
    ]

    pdf = ClosePackPDF()
    pdf.set_compression(False)
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()
    pdf.set_title("Finance Close Control Tower CFO Close Pack")
    pdf.set_author("Zahidah Murira")
    pdf.set_subject("Synthetic data portfolio demo")

    pdf.set_fill_color(242, 244, 247)
    pdf.set_draw_color(180, 186, 194)
    pdf.rect(pdf.l_margin, 12, 190, 38, style="DF")
    pdf.set_xy(pdf.l_margin + 5, 17)
    pdf.set_font("Helvetica", style="B", size=17)
    pdf.set_text_color(25, 25, 25)
    pdf.cell(0, 8, "Finance Close Control Tower", new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(pdf.l_margin + 5)
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.cell(0, 7, "CFO Close Pack", new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(pdf.l_margin + 5)
    pdf.set_font("Helvetica", size=9)
    pdf.multi_cell(
        180,
        5,
        f"Entity: {model.entity_scope}    Period: {model.period}    "
        f"Generated: {model.generated_at}    Rule version: {DEFAULT_CONFIG.rule_version}",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.set_y(56)

    _write_pdf_paragraph(pdf, SYNTHETIC_DISCLAIMER, fill=True)

    _write_pdf_heading(pdf, "Executive summary")
    _write_pdf_paragraph(
        pdf,
        "This CFO close pack summarizes synthetic month-end close readiness using "
        "deterministic finance control checks. It highlights reporting readiness, "
        "critical exceptions, ageing and suspense exposure, VAT control risk, and "
        "intercompany mismatches before close sign-off.",
    )

    _write_pdf_heading(pdf, "Overall close-readiness scores")
    _write_pdf_table(
        pdf,
        ["Entity", "Close Readiness Score", "Status", "Exception Count"],
        _score_rows(selected_overall),
        [55, 45, 30, 35],
        max_chars=[28, 24, 16, 10],
        aligns=["L", "R", "C", "R"],
    )

    table_headers = ["Risk Level", "Entity", "Process", "Exception", "Suggested Action"]
    table_widths = [22, 34, 28, 64, 42]
    table_chars = [12, 22, 16, 54, 34]

    _write_pdf_heading(pdf, "High-risk exception summary")
    _write_pdf_table(
        pdf,
        table_headers,
        _exception_rows(high_risk),
        table_widths,
        max_chars=table_chars,
    )

    _write_pdf_heading(pdf, "Ageing and suspense highlights")
    _write_pdf_table(
        pdf,
        table_headers,
        _exception_rows(bank_and_suspense),
        table_widths,
        max_chars=table_chars,
    )

    _write_pdf_heading(pdf, "VAT / tax control exceptions")
    _write_pdf_table(
        pdf,
        table_headers,
        _exception_rows(vat_exceptions),
        table_widths,
        max_chars=table_chars,
    )

    _write_pdf_heading(pdf, "Intercompany mismatch summary")
    _write_pdf_table(
        pdf,
        table_headers,
        _exception_rows(intercompany),
        table_widths,
        max_chars=table_chars,
    )

    _write_pdf_heading(pdf, "Management Action Plan")
    action_items = [
        "1. Clear or review critical reconciliation and VAT exceptions before sign-off.",
        "2. Investigate aged cash and suspense items before final management reporting.",
        "3. Resolve intercompany mismatches before consolidation or group reporting.",
        "4. Retain the synthetic-data disclaimer with any shared portfolio outputs.",
    ]
    _write_pdf_paragraph(
        pdf,
        "\n".join(action_items),
    )

    return bytes(pdf.output())


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
) -> tuple[Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = output_dir / "sample_close_pack_summary.md"
    excel_path = output_dir / "sample_close_pack.xlsx"
    pdf_path = output_dir / "sample_close_pack.pdf"
    artifacts = build_close_pack_artifacts(datasets, period=period)

    markdown_path.write_text(artifacts.markdown, encoding="utf-8")
    excel_path.write_bytes(artifacts.excel)
    pdf_path.write_bytes(artifacts.pdf)

    return markdown_path, excel_path, pdf_path
