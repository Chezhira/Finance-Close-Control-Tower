# Finance Close Control Tower

Finance Close Control Tower is a finance systems control layer for month-end close readiness, built as a production-style portfolio project by Zahidah Murira. It converts synthetic accounting exports into a CFO-ready view of what is reconciled, what is unresolved, what is ageing, what is materially risky, and what needs action before reporting.

All data in this repository is synthetic. No employer, client, bank, payroll, customer, supplier, tax authority, or confidential company data is included.

Target portfolio roles: Finance Systems Analyst, Finance Automation Specialist, Finance Engineer, FP&A Systems Analyst, Close and Controls Analyst, and Analytics Engineer for finance operations.

## Finance Problem

Month-end close is often slowed down by fragmented spreadsheets, manual trackers, unclear reconciliation status, aged suspense items, unresolved bank reconciliation breaks, VAT control variances, and intercompany mismatches. Finance managers need a concise control view that answers three practical questions:

- Can we trust the numbers enough to report?
- Which entities or process areas are blocking close readiness?
- What action should the finance team take before CFO sign-off?

This project demonstrates how finance systems thinking can turn ordinary accounting exports into structured controls, exceptions, scores, and management-ready reporting.

## What The App Does

- Loads bundled synthetic sample files from `data/sample/`.
- Validates file schemas and public-demo privacy guardrails.
- Runs deterministic close-control checks for trial balance integrity, reconciliations, suspense, bank rec, VAT, and intercompany.
- Calculates close-readiness scores by entity and process area.
- Displays a Streamlit dashboard with exception context and recommended finance actions.
- Exports a CFO close pack in Markdown and Excel.

## Why The Controls Matter

| Control area | Business question | Why it matters |
| --- | --- | --- |
| Trial balance integrity | Do debits and credits balance by entity and period? | An unbalanced trial balance is a hard stop for reliable reporting. |
| Reconciliation completion | Are material balance sheet accounts prepared and reviewed? | Unreviewed reconciliations weaken balance sheet support and audit readiness. |
| Suspense clearing | Are clearing accounts still carrying material balances? | Suspense balances can hide miscoding, timing breaks, or unresolved accounting noise. |
| Bank reconciliation | Are cash reconciling items aged or unexplained? | Old or unknown cash items reduce confidence in reported cash. |
| VAT control movement | Does the VAT bridge reconcile to the closing balance? | VAT breaks can create statutory reporting and filing risk. |
| Intercompany matching | Do paired balances eliminate across entities? | Group reporting depends on mirrored intercompany balances before consolidation. |

## MVP Scope

- Validate standard finance export schemas before analysis.
- Generate reproducible synthetic trial balance, GL, reconciliation, ageing, bank, VAT, and intercompany files.
- Run privacy guardrails before sample data and close-pack outputs are published.
- Produce Markdown and Excel close-pack artifacts for portfolio review.
- Keep all core logic deterministic and testable outside Streamlit.

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .[dev]
.\.venv\Scripts\python.exe scripts\generate_sample_data.py
.\.venv\Scripts\python.exe scripts\run_pipeline.py --data-dir data\sample --output-dir outputs\sample_close_pack
.\.venv\Scripts\python.exe -m pytest -q
```

To launch the Streamlit shell after installing dependencies:

```powershell
streamlit run app.py
```

The app runs entirely from bundled synthetic sample data. It does not require secrets, user uploads, external APIs, private files, database persistence, or cloud services.

## Demo Outputs

The sample pipeline writes portfolio-review artifacts to `outputs/sample_close_pack/`:

- `sample_close_pack_summary.md`: management summary, readiness scores, source files, and exception explanations.
- `sample_close_pack.xlsx`: CFO-style workbook with cover, overall scores, process scores, exceptions, and source-file summary.

## Screenshots

Screenshots are not committed yet. Capture instructions are available in `docs/screenshots/README.md`. Suggested placeholders for the public README once captured:

- `docs/screenshots/executive-dashboard.png`: CFO close-readiness score and entity status.
- `docs/screenshots/process-scores.png`: process-area scoring by entity.
- `docs/screenshots/exceptions.png`: exception table with meaning, risk, and finance action.
- `docs/screenshots/export-center.png`: Markdown and Excel close-pack download view.

Capture after running `streamlit run app.py` locally or after Streamlit Community Cloud deployment.

## Deployment Modes

This project supports two deployment modes:

1. Portfolio demo deployment on Streamlit Community Cloud.
2. Production-style deployment with Docker and Google Cloud Run.

Streamlit Community Cloud is the primary MVP target and must run only with the committed synthetic sample data. The public app is read-only and demo-oriented. Upload handling, when added, must process files in memory only and must not persist uploaded files.

Docker and Google Cloud Run are secondary/stretch deployment targets. Local container runs may load environment variables from `.env`; hosted environments must use cloud secret management. No secrets, API keys, client data, employer data, or real accounting exports may be committed.

GitHub Pages may be used only for static documentation, screenshots, and a project landing page. It is not a host for the Python Streamlit application.

See [docs/deployment.md](docs/deployment.md) for exact commands, environment variables, and billing guardrails.

## Streamlit Community Cloud Public Demo

Public demo URL: `TODO: add Streamlit Community Cloud app URL after deployment`.

Deployment path:

1. Push this repository to GitHub.
2. In Streamlit Community Cloud, create an app from the GitHub repository.
3. Set the app entrypoint to `app.py`.
4. Use `requirements.txt` for runtime dependencies.
5. Do not add secrets for the MVP public demo.
6. Deploy with committed synthetic sample data only.

Public demo defaults:

- Read-only demo mode.
- No file upload widget in the current MVP shell.
- No API keys, tokens, LLM calls, live integrations, private exports, or real company data.
- GitHub Pages, if used later, is only for static documentation and screenshots.

## Portfolio Use and Reuse Restrictions

This repository is published as a professional portfolio project by Zahidah Murira. The code, finance logic, scoring model, documentation, and sample outputs are provided for demonstration and review purposes only. They may not be copied, republished, sold, incorporated into commercial products, or used to train competing systems without written permission.

All data is synthetic. No employer, client, bank, payroll, customer, supplier, tax authority, or confidential company data is included.

See `LICENSE`, `NOTICE`, and `SECURITY.md` before reusing, reviewing, or sharing this project.

## Current Status

The current MVP implements the core sample-data workflow: bundled synthetic finance files, schema checks, deterministic validation rules, close-readiness scoring, Streamlit dashboard views, exception explanations, CFO close-pack exports, and tests for finance calculations.
