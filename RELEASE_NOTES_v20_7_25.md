# v20.7.25 – Research worker hardening

**Date**: 2025-11-26

This release responds to the "Potemkin village" critique by ensuring that the
default worker entrypoint used in research and classroom deployments is a
fully wired, non-mocking engine.

## Changes

1. **Research worker as default**

   - `app/worker.py` now runs as the canonical v20.x queue worker and routes
     jobs through the real Semantic Scholar + LLM pipeline (via
     `app.services.semantic_scholar` and `app.services.extract_7panel`).

2. **Mock isolation**

   - Any simulated behavior is isolated to offline smoke tests
     (e.g., `scripts/offline_pipeline_smoke.py`) and clearly marked
     legacy/experimental worker modules (e.g., `app/worker_complete.py`)
     that are not referenced from the README quick start or standard
     research deployment paths. These are intended only for demos,
     CI smoke tests, or future refactoring.

3. **Policy-driven safety**

   - `config/app.policy.json` now includes an `engine.use_mocks` flag
     (default: `false`). When set to `true`, the research worker exits with an
     explicit error rather than silently serving mock data.

## Impact

- Scientists and students who follow the README.md quick start will now
  always execute the real pipeline.
- Demo / teaching workflows can continue to rely on the offline smoke
  scripts without risk of contaminating research runs.
