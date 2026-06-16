from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

import pandas as pd

from finance_close_control_tower.config import DEFAULT_CONFIG, CloseControlConfig


@dataclass(frozen=True)
class ValidationResult:
    rule_id: str
    process_area: str
    severity: str
    entity: str | None
    period: str | None
    message: str
    source_rows: int
    amount: float | None = None


PROCESS_AREAS = (
    "trial_balance",
    "reconciliations",
    "suspense",
    "bank_rec",
    "vat",
    "intercompany",
)

SEVERITY_RANK = {"info": 0, "warning": 1, "high": 2, "critical": 3}


def _period_end(period: str) -> pd.Timestamp:
    return pd.Period(str(period), freq="M").end_time.normalize()


def _as_number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0.0)


def validate_trial_balance(
    trial_balance: pd.DataFrame,
    config: CloseControlConfig = DEFAULT_CONFIG,
) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    grouped = trial_balance.groupby(["entity", "period"], dropna=False)

    for (entity, period), frame in grouped:
        debit_total = _as_number(frame["debit"]).sum()
        credit_total = _as_number(frame["credit"]).sum()
        imbalance = round(float(debit_total - credit_total), 2)
        if abs(imbalance) > config.tb_tolerance:
            results.append(
                ValidationResult(
                    rule_id="TB_BALANCE",
                    process_area="trial_balance",
                    severity="critical",
                    entity=str(entity),
                    period=str(period),
                    message=f"Trial balance is out of balance by {imbalance:,.2f}.",
                    source_rows=len(frame),
                    amount=imbalance,
                )
            )

    missing_type = trial_balance["account_type"].isna() | (
        trial_balance["account_type"].astype(str).str.strip() == ""
    )
    if missing_type.any():
        for (entity, period), frame in trial_balance[missing_type].groupby(["entity", "period"]):
            results.append(
                ValidationResult(
                    rule_id="TB_ACCOUNT_TYPE",
                    process_area="trial_balance",
                    severity="warning",
                    entity=str(entity),
                    period=str(period),
                    message="Trial balance rows are missing account type.",
                    source_rows=len(frame),
                )
            )

    return results


def validate_reconciliations(reconciliations: pd.DataFrame) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    material = reconciliations["materiality_flag"].astype(str).str.lower().eq("material")
    prepared = reconciliations["preparer_status"].astype(str).str.lower().eq("prepared")
    reviewed = reconciliations["reviewer_status"].astype(str).str.lower().eq("reviewed")

    incomplete = reconciliations[material & (~prepared | ~reviewed)]
    for _, row in incomplete.iterrows():
        severity = "critical" if not reviewed.loc[row.name] else "high"
        results.append(
            ValidationResult(
                rule_id="REC_MATERIAL_STATUS",
                process_area="reconciliations",
                severity=severity,
                entity=str(row["entity"]),
                period=str(row["period"]),
                message=(
                    f"Material reconciliation for {row['account_code']} {row['account_name']} "
                    f"is {row['preparer_status']} / {row['reviewer_status']}."
                ),
                source_rows=1,
                amount=float(row["balance"]),
            )
        )

    return results


def validate_suspense(
    reconciliations: pd.DataFrame,
    config: CloseControlConfig = DEFAULT_CONFIG,
) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    account_name = reconciliations["account_name"].astype(str).str.lower()
    balances = _as_number(reconciliations["balance"])
    suspense = reconciliations[
        account_name.str.contains("suspense", regex=False)
        & (balances.abs() >= config.suspense_materiality)
    ]

    for _, row in suspense.iterrows():
        results.append(
            ValidationResult(
                rule_id="SUSPENSE_MATERIAL_BALANCE",
                process_area="suspense",
                severity="high",
                entity=str(row["entity"]),
                period=str(row["period"]),
                message=(
                    f"Suspense account {row['account_code']} has material balance "
                    f"{float(row['balance']):,.2f}."
                ),
                source_rows=1,
                amount=float(row["balance"]),
            )
        )

    return results


def validate_bank_rec(
    bank_exceptions: pd.DataFrame,
    config: CloseControlConfig = DEFAULT_CONFIG,
) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    frame = bank_exceptions.copy()
    frame["item_date"] = pd.to_datetime(frame["item_date"], errors="coerce")

    for _, row in frame.iterrows():
        period_end = _period_end(str(row["period"]))
        item_date = row["item_date"]
        age_days = 0 if pd.isna(item_date) else int((period_end - item_date.normalize()).days)
        category = str(row["category"]).lower()
        status = str(row["status"]).lower()
        is_unknown = "unknown" in category or "investigat" in status
        is_old = age_days > config.bank_exception_ageing_days

        if is_unknown or is_old:
            severity = "high" if is_unknown else "warning"
            results.append(
                ValidationResult(
                    rule_id="BANK_EXCEPTION_AGEING",
                    process_area="bank_rec",
                    severity=severity,
                    entity=str(row["entity"]),
                    period=str(row["period"]),
                    message=(
                        f"Bank rec item is {age_days} days old with category "
                        f"{row['category']} and status {row['status']}."
                    ),
                    source_rows=1,
                    amount=float(row["amount"]),
                )
            )

    return results


def validate_vat_control(
    vat_control: pd.DataFrame,
    config: CloseControlConfig = DEFAULT_CONFIG,
) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    numeric_columns = [
        "opening_balance",
        "output_vat",
        "input_vat",
        "payments",
        "refunds",
        "adjustments",
        "closing_balance",
    ]
    frame = vat_control.copy()
    for column in numeric_columns:
        frame[column] = _as_number(frame[column])

    calculated = (
        frame["opening_balance"]
        + frame["output_vat"]
        - frame["input_vat"]
        - frame["payments"]
        - frame["refunds"]
        + frame["adjustments"]
    )
    frame["variance"] = frame["closing_balance"] - calculated

    for _, row in frame[frame["variance"].abs() > config.vat_tolerance].iterrows():
        results.append(
            ValidationResult(
                rule_id="VAT_MOVEMENT_VARIANCE",
                process_area="vat",
                severity="critical",
                entity=str(row["entity"]),
                period=str(row["period"]),
                message=f"VAT closing balance variance is {float(row['variance']):,.2f}.",
                source_rows=1,
                amount=float(row["variance"]),
            )
        )

    return results


def validate_intercompany(
    intercompany: pd.DataFrame,
    config: CloseControlConfig = DEFAULT_CONFIG,
) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    frame = intercompany.copy()
    frame["amount"] = _as_number(frame["amount"])
    grouped = frame.groupby(["period", "currency", "transaction_ref"], dropna=False)

    for (period, currency, transaction_ref), group in grouped:
        variance = round(float(group["amount"].sum()), 2)
        if abs(variance) > config.tb_tolerance:
            entities = ", ".join(sorted(group["entity"].astype(str).unique()))
            results.append(
                ValidationResult(
                    rule_id="IC_MISMATCH",
                    process_area="intercompany",
                    severity="high",
                    entity=entities,
                    period=str(period),
                    message=(
                        f"Intercompany transaction {transaction_ref} in {currency} "
                        f"does not eliminate; variance {variance:,.2f}."
                    ),
                    source_rows=len(group),
                    amount=variance,
                )
            )

    return results


def run_all_validations(
    datasets: dict[str, pd.DataFrame],
    config: CloseControlConfig = DEFAULT_CONFIG,
) -> list[ValidationResult]:
    return [
        *validate_trial_balance(datasets["sample_trial_balance.csv"], config),
        *validate_reconciliations(datasets["sample_reconciliation_tracker.xlsx"]),
        *validate_suspense(datasets["sample_reconciliation_tracker.xlsx"], config),
        *validate_bank_rec(datasets["sample_bank_rec_exceptions.csv"], config),
        *validate_vat_control(datasets["sample_vat_control.csv"], config),
        *validate_intercompany(datasets["sample_intercompany_balances.csv"], config),
    ]


def validation_results_to_frame(results: list[ValidationResult]) -> pd.DataFrame:
    if not results:
        return pd.DataFrame(
            columns=[
                "rule_id",
                "process_area",
                "severity",
                "entity",
                "period",
                "message",
                "source_rows",
                "amount",
            ]
        )
    return pd.DataFrame([result.__dict__ for result in results])


def current_run_timestamp() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
