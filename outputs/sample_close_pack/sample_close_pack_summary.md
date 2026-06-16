# Finance Close Control Tower - Sample Close Pack

Built by Zahidah Murira | Finance Engineer Portfolio | Synthetic Data Demo

Synthetic data demo only. No employer, client, bank, payroll, customer, supplier, tax authority, or confidential company data is included.

## Run Metadata

- Generated at: 2026-06-16 17:06:07 UTC
- Selected period: 2026-05
- Rule version: mvp-0.1.0
- Source files: 8

## Source File Summary

- sample_ap_ageing.csv: 1 rows, 9 columns
- sample_ar_ageing.csv: 1 rows, 9 columns
- sample_bank_rec_exceptions.csv: 2 rows, 10 columns
- sample_gl_detail.csv: 2 rows, 12 columns
- sample_intercompany_balances.csv: 3 rows, 7 columns
- sample_reconciliation_tracker.xlsx: 2 rows, 10 columns
- sample_trial_balance.csv: 4 rows, 9 columns
- sample_vat_control.csv: 2 rows, 9 columns

## CFO Review Lens

This pack shows whether the synthetic close is ready for reporting, where control risk is
concentrated, and which finance actions should happen before close sign-off.

## Close-Readiness Scores

- Harbour Services Ltd: 44.8/100 (red), 5 exceptions
- Northstar Retail Ltd: 97.0/100 (green), 1 exception

## Exceptions

- [CRITICAL] reconciliations | Harbour Services Ltd | Material reconciliation for 1300 Suspense Clearing is Prepared / Pending. Action: Complete review, attach support, and clear reviewer comments.
- [HIGH] suspense | Harbour Services Ltd | Suspense account 1300 has material balance 7,500.00. Action: Investigate, reclassify valid items, and clear unsupported balances.
- [WARNING] bank_rec | Northstar Retail Ltd | Bank rec item is 17 days old with category Deposit in transit and status Open. Action: Match to bank or ledger support and post any required correction.
- [HIGH] bank_rec | Harbour Services Ltd | Bank rec item is 22 days old with category Unknown bank charge and status Investigating. Action: Match to bank or ledger support and post any required correction.
- [CRITICAL] vat | Harbour Services Ltd | VAT closing balance variance is 100.00. Action: Reperform the VAT bridge and investigate payments, refunds, inputs, outputs, and adjustments.
- [HIGH] intercompany | Harbour Services Ltd | Intercompany transaction IC-SYN-002 in GBP does not eliminate; variance 2,500.00. Action: Confirm counterparty posting, currency, reference, and book the missing side or correction.

## Suggested Finance Actions

- Clear or review critical reconciliation and VAT exceptions before sign-off.
- Investigate aged cash and suspense items before final management reporting.
- Resolve intercompany mismatches before consolidation or group reporting.
- Keep the synthetic-data disclaimer with any shared portfolio outputs.

## Management Summary

The MVP sample pipeline loaded bundled synthetic finance exports, applied schema and privacy
checks, ran deterministic close-control validation rules, calculated close-readiness scores,
and produced exception detail for management review.
