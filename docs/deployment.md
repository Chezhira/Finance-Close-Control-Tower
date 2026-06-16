# Deployment Strategy

Finance Close Control Tower supports two deployment modes. Both modes are synthetic-data first and must not include private finance exports, secrets, employer names, client names, API keys, bank data, payroll data, tax identifiers, or real accounting records.

## Portfolio Demo: Streamlit Community Cloud

Streamlit Community Cloud is the primary public MVP deployment target.

Required settings:

- Repository entry point: `app.py`.
- Python dependencies: `requirements.txt`.
- Data source: committed files under `data/sample/` only.
- Secrets: none required for MVP.
- LLM commentary: disabled with `ENABLE_LLM_COMMENTARY=false`.
- Demo mode: `READ_ONLY_DEMO=true`.
- Uploads: disabled by default with `ALLOW_FILE_UPLOADS=false`.

If upload functionality is enabled in a later phase, uploaded files must be processed in memory only and must not be written to the repository, output folders, logs, or durable storage.

Recommended Streamlit Cloud environment variables:

```text
APP_ENV=streamlit_cloud
DEPLOYMENT_MODE=portfolio_demo
READ_ONLY_DEMO=true
ALLOW_FILE_UPLOADS=false
PERSIST_UPLOADED_FILES=false
ENABLE_LLM_COMMENTARY=false
PII_SCAN_ENABLED=true
STRICT_SYNTHETIC_MODE=true
```

Before deploying, run:

```powershell
python scripts\generate_sample_data.py
python scripts\run_pipeline.py --data-dir data\sample --output-dir outputs\sample_close_pack
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
```

## Production-Style: Docker and Google Cloud Run

Docker and Google Cloud Run are secondary/stretch deployment targets for production-style demonstration. This mode still defaults to synthetic sample data and does not imply live client use.

Build and run locally:

```powershell
docker build -t finance-close-control-tower .
docker run --rm -p 8080:8080 --env-file .env finance-close-control-tower
```

The app will be available at `http://localhost:8080`.

Example Cloud Run deployment:

```powershell
gcloud run deploy finance-close-control-tower `
  --source . `
  --region europe-west2 `
  --allow-unauthenticated `
  --cpu 1 `
  --memory 512Mi `
  --min-instances 0 `
  --max-instances 1 `
  --concurrency 10 `
  --set-env-vars APP_ENV=cloud_run,DEPLOYMENT_MODE=production_style,READ_ONLY_DEMO=true,ALLOW_FILE_UPLOADS=false,PERSIST_UPLOADED_FILES=false,ENABLE_LLM_COMMENTARY=false,PII_SCAN_ENABLED=true,STRICT_SYNTHETIC_MODE=true
```

Hosted secrets must be supplied through Google Cloud Secret Manager or Cloud Run secret bindings. Do not commit `.env`, credentials, tokens, service account files, webhook URLs, or real service endpoints.

## Billing Guardrails

- Keep Cloud Run `min-instances` at `0` unless there is a clear reason to pay for idle capacity.
- Keep `max-instances` low for demo deployments; the default recommendation is `1`.
- Use low resource limits for the MVP: `1` CPU and `512Mi` memory.
- Do not add always-on background workers, schedulers, polling loops, or external integrations in the MVP.
- Keep `ENABLE_LLM_COMMENTARY=false` by default. Any future LLM feature must be opt-in, bounded, cached, privacy-scanned, and documented before deployment.
- Avoid durable storage for uploaded files. Use in-memory processing and temporary storage only when explicitly required.
- Review Cloud Run logs and billing after deployment tests, then disable or delete unused demo services.

## GitHub Pages Boundary

GitHub Pages may be used only for static documentation, screenshots, and a project landing page. It must not be treated as the host for the Python Streamlit application.
