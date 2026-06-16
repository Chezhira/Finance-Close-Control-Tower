from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
DATA_DIR = ROOT / "data" / "sample"


def write_csv(name: str, rows: list[dict[str, object]]) -> None:
    pd.DataFrame(rows).to_csv(DATA_DIR / name, index=False)


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    write_csv(
        "sample_trial_balance.csv",
        [
            {
                "entity": "Northstar Retail Ltd",
                "period": "2026-05",
                "account_code": "1000",
                "account_name": "Cash Control",
                "account_type": "Asset",
                "debit": 85000.00,
                "credit": 0.00,
                "closing_balance": 85000.00,
                "currency": "GBP",
            },
            {
                "entity": "Northstar Retail Ltd",
                "period": "2026-05",
                "account_code": "4000",
                "account_name": "Sales Revenue",
                "account_type": "Revenue",
                "debit": 0.00,
                "credit": 85000.00,
                "closing_balance": -85000.00,
                "currency": "GBP",
            },
            {
                "entity": "Harbour Services Ltd",
                "period": "2026-05",
                "account_code": "1000",
                "account_name": "Cash Control",
                "account_type": "Asset",
                "debit": 62000.00,
                "credit": 0.00,
                "closing_balance": 62000.00,
                "currency": "GBP",
            },
            {
                "entity": "Harbour Services Ltd",
                "period": "2026-05",
                "account_code": "4000",
                "account_name": "Service Revenue",
                "account_type": "Revenue",
                "debit": 0.00,
                "credit": 62000.00,
                "closing_balance": -62000.00,
                "currency": "GBP",
            },
        ],
    )

    write_csv(
        "sample_gl_detail.csv",
        [
            {
                "entity": "Northstar Retail Ltd",
                "period": "2026-05",
                "journal_id": "JNL-2026-0501",
                "journal_date": "2026-05-31",
                "account_code": "5000",
                "account_name": "Month-End Accruals",
                "debit": 4500.00,
                "credit": 0.00,
                "description": "Synthetic accrual for demo services",
                "preparer": "Finance Owner A",
                "source_system": "Synthetic ERP",
                "is_manual": True,
            },
            {
                "entity": "Harbour Services Ltd",
                "period": "2026-05",
                "journal_id": "JNL-2026-0502",
                "journal_date": "2026-05-31",
                "account_code": "2100",
                "account_name": "Accrued Costs",
                "debit": 0.00,
                "credit": 12000.00,
                "description": "Synthetic management adjustment",
                "preparer": "Finance Owner B",
                "source_system": "Synthetic ERP",
                "is_manual": True,
            },
        ],
    )

    pd.DataFrame(
        [
            {
                "entity": "Northstar Retail Ltd",
                "period": "2026-05",
                "account_code": "1000",
                "account_name": "Cash Control",
                "balance": 85000.00,
                "materiality_flag": "Material",
                "preparer_status": "Prepared",
                "reviewer_status": "Reviewed",
                "owner": "Finance Owner A",
                "due_date": "2026-06-03",
            },
            {
                "entity": "Harbour Services Ltd",
                "period": "2026-05",
                "account_code": "1300",
                "account_name": "Suspense Clearing",
                "balance": 7500.00,
                "materiality_flag": "Material",
                "preparer_status": "Prepared",
                "reviewer_status": "Pending",
                "owner": "Finance Owner B",
                "due_date": "2026-06-03",
            },
        ]
    ).to_excel(DATA_DIR / "sample_reconciliation_tracker.xlsx", index=False)

    write_csv(
        "sample_ar_ageing.csv",
        [
            {
                "entity": "Northstar Retail Ltd",
                "period": "2026-05",
                "customer": "Fictional Customer Alpha",
                "invoice_no": "INV-SYN-001",
                "invoice_date": "2026-05-02",
                "due_date": "2026-06-01",
                "amount": 9800.00,
                "currency": "GBP",
                "ageing_bucket": "Current",
            }
        ],
    )

    write_csv(
        "sample_ap_ageing.csv",
        [
            {
                "entity": "Harbour Services Ltd",
                "period": "2026-05",
                "supplier": "Fictional Supplier Beta",
                "bill_no": "BILL-SYN-001",
                "bill_date": "2026-05-05",
                "due_date": "2026-06-04",
                "amount": 6400.00,
                "currency": "GBP",
                "ageing_bucket": "Current",
            }
        ],
    )

    write_csv(
        "sample_bank_rec_exceptions.csv",
        [
            {
                "entity": "Northstar Retail Ltd",
                "period": "2026-05",
                "bank_account": "Synthetic Operating Account",
                "item_date": "2026-05-14",
                "description": "Deposit in transit from synthetic settlement batch",
                "amount": 3200.00,
                "currency": "GBP",
                "category": "Deposit in transit",
                "status": "Open",
                "owner": "Finance Owner A",
            },
            {
                "entity": "Harbour Services Ltd",
                "period": "2026-05",
                "bank_account": "Synthetic Operating Account",
                "item_date": "2026-05-09",
                "description": "Unknown synthetic bank charge pending coding",
                "amount": -185.00,
                "currency": "GBP",
                "category": "Unknown bank charge",
                "status": "Investigating",
                "owner": "Finance Owner B",
            },
        ],
    )

    write_csv(
        "sample_vat_control.csv",
        [
            {
                "entity": "Northstar Retail Ltd",
                "period": "2026-05",
                "opening_balance": 10000.00,
                "output_vat": 6000.00,
                "input_vat": 2500.00,
                "payments": 3000.00,
                "refunds": 0.00,
                "adjustments": 0.00,
                "closing_balance": 10500.00,
            },
            {
                "entity": "Harbour Services Ltd",
                "period": "2026-05",
                "opening_balance": 8000.00,
                "output_vat": 4200.00,
                "input_vat": 1100.00,
                "payments": 2500.00,
                "refunds": 0.00,
                "adjustments": 0.00,
                "closing_balance": 8700.00,
            },
        ],
    )

    write_csv(
        "sample_intercompany_balances.csv",
        [
            {
                "period": "2026-05",
                "entity": "Northstar Retail Ltd",
                "counterparty": "Harbour Services Ltd",
                "account_type": "Receivable",
                "amount": 15000.00,
                "currency": "GBP",
                "transaction_ref": "IC-SYN-001",
            },
            {
                "period": "2026-05",
                "entity": "Harbour Services Ltd",
                "counterparty": "Northstar Retail Ltd",
                "account_type": "Payable",
                "amount": -15000.00,
                "currency": "GBP",
                "transaction_ref": "IC-SYN-001",
            },
            {
                "period": "2026-05",
                "entity": "Harbour Services Ltd",
                "counterparty": "Northstar Retail Ltd",
                "account_type": "Receivable",
                "amount": 2500.00,
                "currency": "GBP",
                "transaction_ref": "IC-SYN-002",
            },
        ],
    )


if __name__ == "__main__":
    main()
