from __future__ import annotations

from pathlib import Path

from finance_close_control_tower.ingestion import load_sample_data
from finance_close_control_tower.scoring import (
    calculate_overall_scores,
    calculate_process_scores,
    process_scores_to_frame,
)
from finance_close_control_tower.validations import run_all_validations


def test_process_scores_are_calculated_by_entity_and_process_area() -> None:
    datasets = load_sample_data(Path("data/sample"))
    results = run_all_validations(datasets)

    process_scores = calculate_process_scores(datasets, results)
    frame = process_scores_to_frame(process_scores)

    assert len(frame) == 12
    assert set(frame["entity"]) == {"Northstar Retail Ltd", "Harbour Services Ltd"}
    assert set(frame["process_area"]) == {
        "trial_balance",
        "reconciliations",
        "suspense",
        "bank_rec",
        "vat",
        "intercompany",
    }


def test_critical_exceptions_drive_red_status() -> None:
    datasets = load_sample_data(Path("data/sample"))
    results = run_all_validations(datasets)
    frame = process_scores_to_frame(calculate_process_scores(datasets, results))

    harbour_vat = frame[
        (frame["entity"] == "Harbour Services Ltd") & (frame["process_area"] == "vat")
    ].iloc[0]
    northstar_trial_balance = frame[
        (frame["entity"] == "Northstar Retail Ltd") & (frame["process_area"] == "trial_balance")
    ].iloc[0]

    assert harbour_vat["score"] == 0.0
    assert harbour_vat["status"] == "red"
    assert northstar_trial_balance["score"] == 100.0
    assert northstar_trial_balance["status"] == "green"


def test_overall_scores_include_top_drivers_and_exception_counts() -> None:
    datasets = load_sample_data(Path("data/sample"))
    results = run_all_validations(datasets)
    overall = calculate_overall_scores(calculate_process_scores(datasets, results))

    harbour = overall[overall["entity"] == "Harbour Services Ltd"].iloc[0]
    northstar = overall[overall["entity"] == "Northstar Retail Ltd"].iloc[0]

    assert harbour["status"] == "red"
    assert harbour["exception_count"] == 5
    assert any("VAT closing balance variance" in driver for driver in harbour["top_drivers"])
    assert northstar["exception_count"] == 1
