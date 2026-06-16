# v0.1.0 Release Checklist

Use this checklist before tagging or publishing the public portfolio MVP.

## Repository Positioning

- [ ] README first paragraph positions the project as a finance systems control layer, not a generic dashboard.
- [ ] README includes the synthetic-data disclaimer.
- [ ] README includes install and run instructions.
- [ ] README includes the Streamlit Community Cloud public demo URL placeholder.
- [ ] README includes sample close-pack outputs.
- [ ] README includes target portfolio roles.
- [ ] README includes a no-private-data warning.

## Legal And Portfolio Protection

- [ ] `LICENSE` is present and uses All Rights Reserved / Portfolio Use Only wording.
- [ ] `NOTICE` is present and identifies Zahidah Murira as owner.
- [ ] Portfolio reuse restrictions are visible in README.

## Security And Data Protection

- [ ] `SECURITY.md` is present.
- [ ] No `.env` file is committed.
- [ ] No `data/private/` or `outputs/private/` folder is committed.
- [ ] No API keys, tokens, service account files, webhook URLs, passwords, local paths, or private exports are present.
- [ ] Sample data and sample outputs are synthetic only.

## Demo Artifacts

- [ ] `outputs/sample_close_pack/sample_close_pack_summary.md` is generated.
- [ ] `outputs/sample_close_pack/sample_close_pack.xlsx` is generated.
- [ ] Close-pack outputs include synthetic-data disclaimers.
- [ ] Screenshot placeholders or captured screenshots exist under `docs/screenshots/`.

## Verification

- [ ] `python scripts\generate_sample_data.py`
- [ ] `python scripts\run_pipeline.py --data-dir data\sample --output-dir outputs\sample_close_pack`
- [ ] `python -m pytest -q --basetemp .pytest_tmp`
- [ ] `python -m ruff check .`
- [ ] `python -m ruff format --check .`
- [ ] `streamlit run app.py` starts without secrets or external services.

## Explicitly Out Of Scope For v0.1.0

- [ ] No authentication.
- [ ] No file uploads.
- [ ] No LLM commentary.
- [ ] No Odoo or ERP integrations.
- [ ] No database persistence.
- [ ] No notifications or workflow automation.
- [ ] No cloud deployment automation.
