# Codex Handover

This repository follows the Finance Close Control Tower development handover v2.

Current implementation target:

1. Phase 0: repository baseline, metadata, README, `.env.example`, `.gitignore`, CI, docs, and importable package.
2. Phase 1: reproducible synthetic sample data, privacy scan, schema checks, and sample-data smoke pipeline.

Core guardrails:

- Synthetic data only.
- Deterministic finance logic first.
- No LLM calls in the MVP.
- No outbound integrations in the MVP.
- Privacy checks before publishing sample outputs.
- Portfolio reuse restrictions remain visible in README, NOTICE, app footer, and generated outputs.
