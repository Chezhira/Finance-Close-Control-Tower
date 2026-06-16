from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DatasetSchema:
    filename: str
    required_columns: tuple[str, ...]


SCHEMAS: dict[str, DatasetSchema] = {
    "sample_trial_balance.csv": DatasetSchema(
        filename="sample_trial_balance.csv",
        required_columns=(
            "entity",
            "period",
            "account_code",
            "account_name",
            "account_type",
            "debit",
            "credit",
            "closing_balance",
            "currency",
        ),
    ),
    "sample_gl_detail.csv": DatasetSchema(
        filename="sample_gl_detail.csv",
        required_columns=(
            "entity",
            "period",
            "journal_id",
            "journal_date",
            "account_code",
            "account_name",
            "debit",
            "credit",
            "description",
            "preparer",
            "source_system",
            "is_manual",
        ),
    ),
    "sample_reconciliation_tracker.xlsx": DatasetSchema(
        filename="sample_reconciliation_tracker.xlsx",
        required_columns=(
            "entity",
            "period",
            "account_code",
            "account_name",
            "balance",
            "materiality_flag",
            "preparer_status",
            "reviewer_status",
            "owner",
            "due_date",
        ),
    ),
    "sample_ar_ageing.csv": DatasetSchema(
        filename="sample_ar_ageing.csv",
        required_columns=(
            "entity",
            "period",
            "customer",
            "invoice_no",
            "invoice_date",
            "due_date",
            "amount",
            "currency",
            "ageing_bucket",
        ),
    ),
    "sample_ap_ageing.csv": DatasetSchema(
        filename="sample_ap_ageing.csv",
        required_columns=(
            "entity",
            "period",
            "supplier",
            "bill_no",
            "bill_date",
            "due_date",
            "amount",
            "currency",
            "ageing_bucket",
        ),
    ),
    "sample_bank_rec_exceptions.csv": DatasetSchema(
        filename="sample_bank_rec_exceptions.csv",
        required_columns=(
            "entity",
            "period",
            "bank_account",
            "item_date",
            "description",
            "amount",
            "currency",
            "category",
            "status",
            "owner",
        ),
    ),
    "sample_vat_control.csv": DatasetSchema(
        filename="sample_vat_control.csv",
        required_columns=(
            "entity",
            "period",
            "opening_balance",
            "output_vat",
            "input_vat",
            "payments",
            "refunds",
            "adjustments",
            "closing_balance",
        ),
    ),
    "sample_intercompany_balances.csv": DatasetSchema(
        filename="sample_intercompany_balances.csv",
        required_columns=(
            "period",
            "entity",
            "counterparty",
            "account_type",
            "amount",
            "currency",
            "transaction_ref",
        ),
    ),
}


def normalize_column_name(column: str) -> str:
    return column.strip().lower().replace(" ", "_").replace("-", "_")


def missing_required_columns(columns: list[str], schema: DatasetSchema) -> list[str]:
    normalized = {normalize_column_name(column) for column in columns}
    return [column for column in schema.required_columns if column not in normalized]
