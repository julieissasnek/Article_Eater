# Article Eater Observability Profile

This document summarizes the current logging and metrics story for
Article Eater.

## 1. Metrics

- `app/main.py` exposes Prometheus-compatible metrics at `/metrics`.
- A `Counter("app_requests_total", "Total HTTP requests", ["method", "path"])`
  is incremented for each HTTP request.
- `tests/test_api_smoke.py` verifies that `/metrics` is reachable and
  includes `app_requests_total` in the payload.

Recommended practice:

- Point a Prometheus scraper at `/metrics` in lab/production deployments.
- Use basic alerts on elevated error rates or abnormal traffic patterns.

## 2. Logging

- Logging configuration is defined in `config/logging.conf`.
- Application components should use the standard Python `logging` module.
- For admin-sensitive actions, `src/security/admin_guard.py` also writes
  an audit log to `logs/admin_audit.log`.

## 3. Governance and CI Hooks

- Governance scripts (`scripts/check_governance.py`,
  `scripts/orphan_sweep.py`, `scripts/public_surface_ledger.py`,
  `scripts/manifest_sha256.py`) are wired into the
  `.github/workflows/governance.yml` workflow.
- `tests/test_enterprise_configs.py` ensures that key observability and
  governance files (Dockerfile, CI v3 workflow, pre-commit config, and
  logging configuration) are present.

## 4. Future Enhancements

- Add more granular metrics (e.g., job durations, LLM token usage,
  rulegraph and BN export counts).
- Centralize logs via a structured logging sink (e.g., ELK, OpenTelemetry).
- Wire cost telemetry into the same metrics pathway for per-job cost
  dashboards.
