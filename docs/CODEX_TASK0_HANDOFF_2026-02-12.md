# CODEX TASK-0 HANDOFF

**Date**: 2026-02-12  
**Task**: `CODEX-TASKS-2026-02-12 / TASK-0 (Ruthless System Evaluation)`  
**Repos**:
- `/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1`
- `/Users/davidusa/REPOS/BN_graphical`

## Resume Prompt (copy into next instance)
Continue TASK-0 only. Do not start TASK-1.  
Use this handoff file as source of truth. Re-validate critical findings quickly, then produce:
`/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/docs/CODEX_EVALUATION_REPORT_2026-02-12.md`

Required report format is in:
`/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/docs/CODEX_TASK_LIST_2026-02-12.md`

## Current Status
- Investigation done, report not yet written.
- No code changes were made by this Codex instance.
- Critical runtime behavior already validated for ingestion routing mismatch.

## High-Confidence Confirmed Findings

1. Ingestion endpoint wiring mismatch causes 405/404 on expected paths.
- Route defines prefix `/api/ingestion`: `app/routes/ingestion.py:28`
- App mounts with extra `/api/v1` prefix: `app/main.py:954`
- Effective path is `/api/v1/api/ingestion/*`, not `/api/v1/ingestion/*`.
- Runtime proof already observed:
  - `POST /api/v1/ingestion/paper -> 405`
  - `POST /api/v1/api/ingestion/paper -> 200`
  - `GET /api/v1/ingestion/stats -> 404`
  - `GET /api/v1/api/ingestion/stats -> 200`

2. Duplicate operation IDs are present (OpenAPI warnings).
- Duplicate router include path for interactions:
  - `app/main.py:971`
  - `app/main.py:973`
  - endpoint: `app/routes/interactions.py:8`
- Duplicate admin prompt update endpoints:
  - `src/services/admin_service.py:140`
  - `src/services/admin_service.py:166`

3. Legacy profile key route stores API keys in plaintext with fake user identity semantics.
- `app/routes/profile.py:11`
- `app/routes/profile.py:22`
- Uses query/form-like params and default `user_id=1`; no auth dependency.

4. Encryption key management for `app/security/keys.py` is unstable without persisted env key.
- `app/security/keys.py:7`
- `app/security/keys.py:9`
- If `AE_MASTER_KEY` missing on process restart, previously encrypted keys become undecryptable.

5. Test blind spot: ingestion route tests bypass app-level wiring.
- Tests mount router directly with `FastAPI().include_router(router)`: `tests/test_ingestion_routes.py:35`
- Therefore they miss `app.main` path composition defects.

6. Main wiring test is too weak for ingestion.
- Only checks any path containing `/ingestion`: `tests/test_main_wiring.py:48`
- Does not assert canonical public path (`/api/v1/ingestion/...`).

7. FastAPI deprecations and route-pattern deprecations present in active paths.
- `on_event` deprecated warnings emitted from `app/main.py:897` and `app/main.py:920`
- `regex` deprecated in query params under entrenchment routes:
  - `app/routes/entrenchment.py:95`
  - `app/routes/entrenchment.py:124`
  - `app/routes/entrenchment.py:313`

8. BN repo path assumptions in task list are stale.
- Expected paths from task list (`src/components/...`) do not exist.
- Actual frontend integration code is under:
  - `frontend-v2/src/features/explorer/CausalGraphView.tsx`
  - `frontend-v2/src/features/explorer/EvidencePanel.tsx`
  - `frontend-v2/src/lib/api-client.ts`

9. BN frontend currently fails build (non-shippable).
- `npm run build` failed with TS errors in:
  - `frontend-v2/src/features/explorer/BeliefNodes.tsx`
  - `frontend-v2/src/features/explorer/WebView.tsx`
  - `frontend-v2/src/lib/api-client.ts:411` (duplicate export conflict)
  - `frontend-v2/src/features/explorer/CausalGraphView.tsx:17` (unused import)

10. BN Python venv execution is broken in this environment.
- `bn_venv/bin/python` symlink points to missing interpreter path here.
- Could not run BN pytest from that venv in this session.

11. Core service scale/maintainability risk: extreme file size and mixed concerns.
- `src/services/web_of_belief.py` ~2925 LOC
- `src/services/epistemic_causal_bridge.py` ~3472 LOC
- `src/services/web_persistence.py` ~3077 LOC

12. Security posture mismatch between docs and implementation.
- Project describes local-only assumptions in docs, but app includes many open write/admin-like surfaces and fallback auth behavior.
- `app/main.py` exposes numerous routes; several do not enforce auth dependencies consistently.

## Important Likely Finding Requiring Final Recheck

Potential enum-level mismatch in gap prediction filters:
- `src/services/gap_predictor.py:596`
- `src/services/gap_predictor.py:597`
- `src/services/gap_predictor.py:598`
- `src/services/gap_predictor.py:599`
- `src/services/gap_predictor.py:828`
- `src/services/gap_predictor.py:829`
- `src/services/gap_predictor.py:830`
- `src/services/gap_predictor.py:831`

Pattern uses `str(b.level).upper()` comparisons, which may not match canonical enum-string style consistently.
Need a quick runtime unit check with real `WebOfBelief` beliefs before calling it critical.

## Commands Already Run (Key Results)

1. Targeted AE tests passed:
```bash
./venv/bin/pytest -q tests/test_gap_predictor.py tests/test_edge_justification.py tests/test_int_pipeline.py
```
Result: `71 passed`.

2. Wiring/smoke subset passed but emitted warnings:
```bash
./venv/bin/pytest -q tests/test_ingestion_routes.py tests/test_api_smoke.py tests/test_main_wiring.py
```
Result: `31 passed`, with duplicate operation ID warnings + deprecations.

3. Runtime route/path probe (with `TestClient`) validated ingestion mismatch:
- Expected `/api/v1/ingestion/...` path fails.
- Actual `/api/v1/api/ingestion/...` succeeds.

4. BN frontend build failed:
```bash
cd /Users/davidusa/REPOS/BN_graphical/frontend-v2
npm run build
```
Result: TypeScript errors, build failed.

## Fast Revalidation Checklist (first 5 minutes after resume)

```bash
cd /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1

# 1) Reconfirm ingestion mismatch quickly
./venv/bin/python - <<'PY'
from fastapi.testclient import TestClient
from app.main import app
c=TestClient(app)
for m,p,j in [
 ("POST","/api/v1/ingestion/paper",{"paper":{"paper_id":"p1","title":"t1"},"beliefs":[]}),
 ("POST","/api/v1/api/ingestion/paper",{"paper":{"paper_id":"p2","title":"t2"},"beliefs":[]}),
]:
    r=c.post(p,json=j); print(m,p,r.status_code)
PY

# 2) Re-run key tests
./venv/bin/pytest -q tests/test_gap_predictor.py tests/test_edge_justification.py tests/test_int_pipeline.py tests/test_ingestion_routes.py tests/test_main_wiring.py

# 3) BN frontend status
cd /Users/davidusa/REPOS/BN_graphical/frontend-v2
npm run build
```

## Remaining Work to Finish TASK-0

1. Final pass: classify all findings by severity (Critical / Major / Minor) with file:line references.
2. Fill scoring section (Architecture, Code Quality, Security, Testing, Documentation, Scalability, Overall).
3. Confirm/assess known debt items from task list:
- ingestion 405: **confirmed**
- hot reload requiring restart: likely still true in integration pathing (documented in repo docs)
- duplicate operation IDs: **confirmed**
- SQLite scaling ceiling: architectural risk, evaluate against workload assumptions
4. Write final report to:
`docs/CODEX_EVALUATION_REPORT_2026-02-12.md`

## Suggested Report Framing (for next instance)

- Executive summary should explicitly state:
  - Strong conceptual architecture intent.
  - Weak operational coherence at integration boundaries.
  - Security posture inconsistent with claimed deployment assumptions.
  - Test suite breadth is high but has key blind spots.
- Findings list should lead with externally visible failures (ingestion path, frontend build).

