from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from finance_close_control_tower.exports import (  # noqa: E402
    SYNTHETIC_DISCLAIMER,
    build_close_pack_artifacts,
)
from finance_close_control_tower.ingestion import load_sample_data  # noqa: E402
from finance_close_control_tower.scoring import (
    calculate_overall_scores,
    calculate_process_scores,
    process_scores_to_frame,
)  # noqa: E402
from finance_close_control_tower.validations import (
    run_all_validations,
    validation_results_to_frame,
)  # noqa: E402

st.set_page_config(page_title="Finance Close Control Tower", layout="wide")

DATA_DIR = ROOT / "data" / "sample"

PROCESS_CONTEXT = {
    "reconciliations": {
        "meaning": (
            "A material balance sheet account has not completed the prepare-and-review cycle."
        ),
        "why": (
            "Unreviewed reconciliations weaken confidence that the balance sheet is supportable."
        ),
        "action": (
            "Assign the owner to complete review, attach support, and clear reviewer comments "
            "before close sign-off."
        ),
    },
    "suspense": {
        "meaning": "A suspense or clearing account still holds a material balance.",
        "why": (
            "Suspense balances can hide miscoding, timing breaks, or unresolved accounting noise."
        ),
        "action": (
            "Investigate the balance, reclassify valid items, and clear unsupported amounts "
            "before reporting."
        ),
    },
    "bank_rec": {
        "meaning": "A bank reconciliation item is aged, unknown, or still under investigation.",
        "why": (
            "Old or unexplained cash items reduce confidence in reported cash and working capital."
        ),
        "action": (
            "Match the item to bank or ledger support, categorize it, and post any required "
            "correction."
        ),
    },
    "vat": {
        "meaning": "The VAT control movement does not reconcile to the reported closing balance.",
        "why": (
            "VAT control breaks can lead to misstated liabilities, late corrections, or "
            "statutory filing risk."
        ),
        "action": (
            "Reperform the VAT bridge and investigate payments, refunds, inputs, outputs, "
            "and adjustments."
        ),
    },
    "intercompany": {
        "meaning": (
            "An intercompany balance does not eliminate across entity and counterparty records."
        ),
        "why": (
            "Group reporting needs mirrored balances before consolidation and elimination "
            "entries are reliable."
        ),
        "action": (
            "Confirm the counterparty posting, currency, and transaction reference, then book "
            "the missing side or correction."
        ),
    },
}

DISPLAY_LABELS = {
    "amount": "Amount",
    "entity": "Entity",
    "exception_count": "Exception count",
    "finance_action": "Finance action",
    "message": "Exception explanation",
    "period": "Period",
    "process_area": "Process area",
    "score": "Score",
    "severity": "Exception type",
    "status": "Status",
    "why_it_matters": "Why it matters",
}


@st.cache_data
def load_mvp_model() -> tuple[dict[str, pd.DataFrame], pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    datasets = load_sample_data(DATA_DIR)
    validation_results = run_all_validations(datasets)
    exception_frame = validation_results_to_frame(validation_results)
    process_scores = calculate_process_scores(datasets, validation_results)
    process_score_frame = process_scores_to_frame(process_scores)
    overall_score_frame = calculate_overall_scores(process_scores)
    return datasets, exception_frame, process_score_frame, overall_score_frame


def filter_frame(frame: pd.DataFrame, entity: str, period: str) -> pd.DataFrame:
    filtered = frame.copy()
    if entity != "All" and "entity" in filtered.columns:
        filtered = filtered[filtered["entity"].astype(str).str.contains(entity, regex=False)]
    if period != "All" and "period" in filtered.columns:
        filtered = filtered[filtered["period"].astype(str) == period]
    return filtered


def add_exception_context(frame: pd.DataFrame) -> pd.DataFrame:
    enriched = frame.copy()
    if enriched.empty:
        return enriched
    enriched["what_it_means"] = enriched["process_area"].map(
        lambda process: PROCESS_CONTEXT.get(str(process), {}).get("meaning", "")
    )
    enriched["why_it_matters"] = enriched["process_area"].map(
        lambda process: PROCESS_CONTEXT.get(str(process), {}).get("why", "")
    )
    enriched["finance_action"] = enriched["process_area"].map(
        lambda process: PROCESS_CONTEXT.get(str(process), {}).get("action", "")
    )
    return enriched


def prepare_display_table(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    display = frame[columns].copy()
    if "score" in display.columns:
        display["score"] = display["score"].map(lambda score: f"{float(score):.1f}")
    if "status" in display.columns:
        display["status"] = display["status"].astype(str).str.title()
    if "severity" in display.columns:
        display["severity"] = display["severity"].astype(str).str.title()
    if "process_area" in display.columns:
        display["process_area"] = (
            display["process_area"].astype(str).str.replace("_", " ").str.title()
        )
    if "amount" in display.columns:
        display["amount"] = display["amount"].map(
            lambda amount: "" if pd.isna(amount) else f"{float(amount):,.1f}"
        )
    return display.rename(columns=DISPLAY_LABELS)


def show_exception_view(process_area: str, title: str) -> None:
    context = PROCESS_CONTEXT[process_area]
    st.subheader(title)
    st.write(context["meaning"])
    st.caption(f"Why it matters: {context['why']}")
    st.caption(f"Typical finance action: {context['action']}")
    process_exceptions = add_exception_context(
        filtered_exceptions[filtered_exceptions["process_area"] == process_area]
    )
    st.dataframe(
        prepare_display_table(
            process_exceptions,
            [
                "severity",
                "entity",
                "period",
                "message",
                "why_it_matters",
                "finance_action",
                "amount",
            ],
        ),
        use_container_width=True,
        hide_index=True,
    )


datasets, exceptions, process_scores, overall_scores = load_mvp_model()
periods = sorted(overall_scores["period"].astype(str).unique())
entities = sorted(overall_scores["entity"].astype(str).unique())

st.title("Finance Close Control Tower")
st.caption("Month-end finance systems control layer | Synthetic data demo")
with st.expander("Synthetic-data and privacy note", expanded=False):
    st.caption(SYNTHETIC_DISCLAIMER)
st.write(
    "This demo turns standard finance exports into a close-readiness view: what is "
    "reconciled, what is unresolved, what is ageing, and what needs action before CFO sign-off."
)

with st.sidebar:
    st.header("Close View")
    selected_period = st.selectbox("Period", ["All", *periods], index=1 if periods else 0)
    selected_entity = st.selectbox("Entity", ["All", *entities])
    st.caption("Built by Zahidah Murira | Finance Engineer Portfolio | Synthetic Data Demo")

filtered_overall = filter_frame(overall_scores, selected_entity, selected_period)
filtered_process = filter_frame(process_scores, selected_entity, selected_period)
filtered_exceptions = filter_frame(exceptions, selected_entity, selected_period)

score_average = 0.0 if filtered_overall.empty else filtered_overall["score"].mean()
exception_count = 0 if filtered_exceptions.empty else len(filtered_exceptions)
red_count = (
    0
    if filtered_overall.empty
    else int(filtered_overall["status"].astype(str).str.lower().eq("red").sum())
)

metric_cols = st.columns(4)
metric_cols[0].metric("Average readiness", f"{score_average:.1f}/100")
metric_cols[1].metric("Open exceptions", f"{exception_count}")
metric_cols[2].metric("Entities at risk", f"{red_count}")
metric_cols[3].metric("Sample files checked", f"{len(datasets)}")

tabs = st.tabs(
    [
        "Executive Dashboard",
        "Reconciliations",
        "Suspense",
        "Bank Rec",
        "VAT",
        "Intercompany",
        "Export Center",
    ]
)

with tabs[0]:
    st.subheader("CFO Close-Readiness by Entity")
    st.write(
        "The score summarizes whether each entity is ready for reporting based on core "
        "month-end controls. Red status means a critical exception needs finance review."
    )
    st.dataframe(
        prepare_display_table(
            filtered_overall,
            ["entity", "period", "score", "status", "exception_count"],
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Control Area Scores")
    st.write(
        "Each control area is scored separately so reviewers can see whether the close risk "
        "comes from reconciliations, cash, statutory controls, or group reporting."
    )
    st.dataframe(
        prepare_display_table(
            filtered_process,
            ["entity", "period", "process_area", "score", "status", "exception_count"],
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Top Management Exceptions")
    st.write(
        "These are the items a finance team would review before sign-off. Each exception "
        "links back to a process area, severity, business meaning, and recommended action."
    )
    display_exceptions = add_exception_context(filtered_exceptions)
    st.dataframe(
        prepare_display_table(
            display_exceptions,
            [
                "severity",
                "process_area",
                "entity",
                "period",
                "message",
                "why_it_matters",
                "finance_action",
                "amount",
            ],
        ),
        use_container_width=True,
        hide_index=True,
    )

with tabs[1]:
    show_exception_view("reconciliations", "Reconciliation Review Exceptions")

with tabs[2]:
    show_exception_view("suspense", "Suspense and Clearing Exceptions")

with tabs[3]:
    show_exception_view("bank_rec", "Bank Reconciliation Exceptions")

with tabs[4]:
    show_exception_view("vat", "VAT Control Movement Exceptions")

with tabs[5]:
    show_exception_view("intercompany", "Intercompany Elimination Exceptions")

with tabs[6]:
    st.subheader("CFO Close Pack Export")
    markdown_content, excel_bytes = build_close_pack_artifacts(datasets)
    st.write(
        "The close pack is generated in memory from bundled synthetic sample data and "
        "summarizes readiness scores, source files, exceptions, and management actions."
    )
    st.download_button(
        "Download Markdown Close Pack",
        data=markdown_content,
        file_name="sample_close_pack_summary.md",
        mime="text/markdown",
    )
    st.download_button(
        "Download Excel Close Pack",
        data=excel_bytes,
        file_name="sample_close_pack.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

st.markdown("---")
st.caption("Built by Zahidah Murira | Finance Engineer Portfolio | Synthetic Data Demo")
