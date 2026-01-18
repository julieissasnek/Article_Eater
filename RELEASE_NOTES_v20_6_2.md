# v20.6.2 — Engines Powered + Admin Policy + BBN Calibrator (separate output)
- RBAC guard for /api/admin/* via X-Admin-Token + audit log.
- Provider-agnostic LLM core wired into Agent_Finder with JSON Schema validation.
- Seven-panel prompt + schema now capture p, effect size (+ type), N, and 95% CI bounds, and raw_abstract.
- BBN Calibrator produces a separate calibration artifact at calibration/bbn_calibration.json (no mutation of BN inputs).
- Safe overlay: strictly additive; no deletions.