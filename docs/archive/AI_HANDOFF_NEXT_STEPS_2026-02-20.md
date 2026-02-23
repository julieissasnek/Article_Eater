# AI Handoff: Next Steps (2026-02-20)

## Current Snapshot
- Health report: `docs/system_health_report_app_streamlit_db_contracts_2026-02-20.md`
- Health JSON: `data/production/system_health_report_app_streamlit_db_contracts_2026-02-20.json`
- Web/BN check: `data/production/check_web_bn_health_app_streamlit_db_contracts_2026-02-20.json`
- Overall score: `76.14` (`YELLOW`, `PASS`, hard gates `PASS`)

## Main Defects To Improve
From target checks in the current health report:
1. `web.isolated_pct` too high (`22.50` vs target `<= 10.0`)
2. `web.contradicts_count` too low (`171` vs target `>= 200`)
3. `web.contradicts_share_pct` too low (`0.604%` vs target `>= 2.0%`)
4. `bn.edges` too low (`4271` vs target `>= 5000`)
5. `bn.largest_component_pct` too low (`24.91%` vs target `>= 50.0%`)

## Safety Contracts (Do Not Violate)
- Always run dry-run first for any script that mutates web/BN.
- Back up mutable artifacts before writes:
  - `data/web_persistence.db`
  - `data/production/realtime_incremental_bn.json`
- Keep DB path contracts intact:
  - No hardcoded absolute AF/Web DB paths in `scripts/`, `src/`, `app/`, `streamlit_app/`
  - Keep `tests/test_db_path_contracts.py` passing.
- If any hard gate regresses to fail, stop and roll back from backups.

## Prioritized Execution Plan

### P1: Safely increase cross-paper integration density
Goal: lower `web.isolated_pct`, improve BN connectivity.
- Start with:
  - `python3 scripts/reprocess_web_relations_and_bridges.py --dry-run`
- If dry-run looks healthy, execute bounded write run.
- Re-run:
  - `python3 scripts/check_web_bn_health.py --json`
  - `python3 scripts/compute_system_health.py --json-out data/production/system_health_report_after_p1.json --markdown-out docs/system_health_report_after_p1.md`

Acceptance:
- `web.isolated_pct` strictly decreases from baseline (`22.50`).
- No drop in `minimum_viable` pass count (must stay `12/12`).

### P2: Increase contradiction coverage with conservative rules
Goal: raise `web.contradicts_count` and `web.contradicts_share_pct`.
- Start with:
  - `python3 scripts/backfill_outcome_polarity_conflicts.py --dry-run`
- Then run bounded write if dry-run is valid.
- Optionally follow with argument-structure pass:
  - `python3 scripts/backfill_argument_constraints.py --dry-run`

Acceptance:
- `web.contradicts_count >= 200`
- `web.contradicts_share_pct` improves vs baseline, with no min-viable regression.

### P3: Improve BN edges/component safely
Goal: raise `bn.edges`, `bn.largest_component_pct`.
- After P1/P2, refresh BN derivation/update via existing production-safe scripts.
- Validate with:
  - `python3 scripts/check_web_bn_health.py --json`

Acceptance:
- `bn.edges` increases vs baseline (`4271`)
- `bn.largest_component_pct` increases vs baseline (`24.91%`)
- `bn.unresolved_count` remains `0`

### P4: Lock in regression safeguards
- Keep passing:
  - `pytest -q tests/test_db_path_contracts.py tests/test_db_locator.py tests/test_compute_system_health.py tests/test_sanity_check.py tests/test_bn_unresolved_repair.py`
- Add/extend targeted tests for any new contradiction/integration rule logic before merge.

## Required Deliverables
- Updated health artifacts:
  - `docs/system_health_report_<suffix>.md`
  - `data/production/system_health_report_<suffix>.json`
  - `data/production/check_web_bn_health_<suffix>.json`
- Change log summary in `docs/` including:
  - what changed
  - before/after metric table for the 5 defect metrics above
  - rollback notes

## Copy/Paste Operator Prompt For Another AI
Use this exact prompt:

```text
Read docs/AI_HANDOFF_NEXT_STEPS_2026-02-20.md and execute P1->P4 in order.
Hard requirements:
1) Dry-run before any write.
2) Back up web DB and BN JSON before writes.
3) Do not introduce hardcoded absolute DB paths in scripts/src/app/streamlit_app.
4) Keep all hard gates passing.
5) After each phase, regenerate check_web_bn_health and compute_system_health reports.
6) Save final metric report in docs/ and provide before/after values for:
   web.isolated_pct, web.contradicts_count, web.contradicts_share_pct, bn.edges, bn.largest_component_pct.
If any phase worsens hard-gate status or min-viable checks, stop and roll back.
```
