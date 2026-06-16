from __future__ import annotations

from pathlib import Path

import pandas as pd

from finance_close_control_tower.ingestion import load_sample_data
from finance_close_control_tower.validations import (
    run_all_validations,
    validate_bank_rec,
    validate_intercompany,
    validate_reconciliations,
    validate_suspense,
    validate_trial_balance,
    validate_vat_control,
    validation_results_to_frame,
)


def test_trial_balance_passes_for_balanced_sample() -> None:
    datasets = load_sample_data(Path("data/sample"))

    assert validate_trial_balance(datasets["sample_trial_balance.csv"]) == []


def test_trial_balance_flags_imbalance() -> None:
    frame = pd.DataFrame(
        [
            {
                "entity": "Demo Entity",
                "period": "2026-05",
                "account_code": "1000",
                "account_name": "Cash",
                "account_type": "Asset",
                "debit": 100.0,
                "credit": 0.0,
                "closing_balance": 100.0,
                "currency": "GBP",
            }
        ]
    )

    results = validate_trial_balance(frame)

    assert len(results) == 1
    assert results[0].rule_id == "TB_BALANCE"
    assert results[0].severity == "critical"


def test_reconciliation_flags_material_pending_review() -> None:
    datasets = load_sample_data(Path("data/sample"))

    results = validate_reconciliations(datasets["sample_reconciliation_tracker.xlsx"])

    assert len(results) == 1
    assert results[0].rule_id == "REC_MATERIAL_STATUS"
    assert results[0].entity == "Harbour Services Ltd"
    assert results[0].severity == "critical"


def test_suspense_flags_material_suspense_balance() -> None:
    datasets = load_sample_data(Path("data/sample"))

    results = validate_suspense(datasets["sample_reconciliation_tracker.xlsx"])

    assert len(results) == 1
    assert results[0].rule_id == "SUSPENSE_MATERIAL_BALANCE"
    assert results[0].amount == 7500.0


def test_bank_rec_flags_aged_and_unknown_items() -> None:
    datasets = load_sample_data(Path("data/sample"))

    results = validate_bank_rec(datasets["sample_bank_rec_exceptions.csv"])

    assert len(results) == 2
    assert {result.rule_id for result in results} == {"BANK_EXCEPTION_AGEING"}
    assert {result.entity for result in results} == {
        "Northstar Retail Ltd",
        "Harbour Services Ltd",
    }


def test_vat_control_flags_variance() -> None:
    datasets = load_sample_data(Path("data/sample"))

    results = validate_vat_control(datasets["sample_vat_control.csv"])

    assert len(results) == 1
    assert results[0].rule_id == "VAT_MOVEMENT_VARIANCE"
    assert results[0].entity == "Harbour Services Ltd"
    assert results[0].amount == 100.0


def test_intercompany_flags_unmatched_transaction() -> None:
    datasets = load_sample_data(Path("data/sample"))

    results = validate_intercompany(datasets["sample_intercompany_balances.csv"])

    assert len(results) == 1
    assert results[0].rule_id == "IC_MISMATCH"
    assert results[0].amount == 2500.0


def test_run_all_validations_returns_expected_sample_exception_set() -> None:
    datasets = load_sample_data(Path("data/sample"))

    frame = validation_results_to_frame(run_all_validations(datasets))

    assert len(frame) == 6
    assert set(frame["process_area"]) == {
        "reconciliations",
        "suspense",
        "bank_rec",
        "vat",
        "intercompany",
    }
    assert "trial_balance" not in set(frame["process_area"])
