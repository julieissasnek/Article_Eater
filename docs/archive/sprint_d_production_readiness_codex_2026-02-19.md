# Sprint D Production Readiness (Codex Candidate)

Generated: 2026-02-19

## Scope

- Focused on extraction quality hardening only.
- No code edits to `src/services/web_of_belief*` (parallel web refactor safety).
- All outputs written to `codex_candidate` files for side-by-side comparison.

## Candidate Artifacts

- `data/production/structured_claims.codex_candidate.json` (baseline snapshot)
- `data/production/structured_claims.codex_candidate_v2.json` (hardened)
- `data/production/structured_claims.codex_release_candidate.json` (packaged RC)
- `data/web_persistence_v2.codex_candidate.db`
- `data/web_persistence_v2.codex_release_candidate.db`
- `docs/web_health_report_post_rebuild.codex_candidate.md`
- `docs/web_health_report_post_rebuild.codex_release_candidate.md`

## Extraction Metrics (Before vs After)

- Baseline (`structured_claims.codex_candidate.json`)
  - Total claims: 502
  - Unknown direction: 51.39%
  - Table claims: 123 (unknown direction: 95)
  - Conflicts: 47
  - Mapped IV+DV: 96.02%

- Hardened (`structured_claims.codex_candidate_v2.json`)
  - Total claims: 382
  - Unknown direction: 45.03%
  - Table claims: 31 (unknown direction: 18)
  - Conflicts: 0
  - Mapped IV+DV: 100.0%

- Release Candidate (`structured_claims.codex_release_candidate.json`)
  - Total claims: 382
  - Unknown direction: 44.76%
  - Table claims: 31 (unknown direction: 18)
  - Conflicts: 0
  - Mapped IV+DV: 100.0%

## Gold-Standard Heuristic Validation (scripts/validate_extraction.py matcher)

- Baseline:
  - TP: 1, FP: 31, FN: 138
  - Precision: 0.0312
  - Recall: 0.0072
  - F1: 0.0117

- Hardened:
  - TP: 1, FP: 12, FN: 138
  - Precision: 0.0769
  - Recall: 0.0072
  - F1: 0.0132

- Release Candidate:
  - TP: 1, FP: 12, FN: 138
  - Precision: 0.0769
  - Recall: 0.0072
  - F1: 0.0132

Interpretation: precision improves substantially under this matcher; recall does not improve.

## Web/BN Build Check from Hardened Claims

- Candidate build command:
  - `python3 scripts/rebuild_web_db.py --input data/production/structured_claims.codex_candidate_v2.json --db-path data/web_persistence_v2.codex_candidate.db --report-path docs/web_health_report_post_rebuild.codex_candidate.md --no-backup`
- Release-candidate build command:
  - `python3 scripts/rebuild_web_db.py --input data/production/structured_claims.codex_release_candidate.json --db-path data/web_persistence_v2.codex_release_candidate.db --report-path docs/web_health_report_post_rebuild.codex_release_candidate.md --no-backup`
- Result:
  - 382 beliefs persisted
  - 12,228 constraints persisted
  - 0 unresolved environment IDs
- Deterministic stress probe:
  - `python3 scripts/probe_web_of_belief_health.py --iterations 1000 --seed 1337`
  - Passed

## Current Status

- Candidate is stronger on precision/cleanliness and safer for downstream web ingestion.
- Main remaining gap is recall and directional completeness, especially in table-derived claims.
