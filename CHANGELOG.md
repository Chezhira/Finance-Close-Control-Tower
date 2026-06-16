# Changelog

## v0.1.0 - Public Portfolio MVP

Initial public release candidate for Finance Close Control Tower.

### Added

- Streamlit dashboard using bundled synthetic sample finance data only.
- Schema checks and privacy guardrails for public-demo sample files.
- Deterministic validation rules for trial balance integrity, reconciliations, suspense, bank reconciliation, VAT control movement, and intercompany matching.
- Close-readiness scoring by entity and process area.
- Plain-English exception views explaining what each exception means, why it matters, and what finance action to take.
- Markdown and Excel CFO close-pack outputs under `outputs/sample_close_pack/`.
- Synthetic sample data under `data/sample/`.
- Streamlit Community Cloud readiness documentation and URL placeholder.
- Docker and Google Cloud Run stretch deployment notes.
- CI workflow running `ruff check`, `ruff format --check`, `pytest`, and the sample pipeline.
- Portfolio-use-only copyright, security, privacy, and release-readiness documentation.

### Guardrails

- Synthetic data only.
- No authentication, uploads, LLM commentary, Odoo integrations, database persistence, notifications, or cloud automation in the MVP.
- No committed secrets, `.env` files, private folders, or real accounting exports.
