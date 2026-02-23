# Codex System Evaluation Report

**Date**: 2026-02-12
**Evaluator**: Codex
**Task ID**: CODEX-TASKS-2026-02-12/TASK-0

## Executive Summary
The system has an ambitious and intellectually coherent target architecture: epistemic extraction in Article_Eater feeding causal interaction surfaces in BN_graphical. The conceptual scaffolding is strong, and a lot of implementation volume exists across both repos. However, the operational integration is brittle. Multiple externally visible failures still exist at the API and frontend boundaries, including a broken public ingestion path and a non-buildable frontend.

The most serious problems are not theoretical. They are wiring and reliability defects that directly block expected workflows: canonical ingestion endpoints fail, one valid ingestion enum value crashes at runtime, and the BN frontend currently fails TypeScript build. In parallel, security posture is inconsistent: some write/key endpoints are intentionally unauthenticated, one profile key path stores plaintext secrets, and authentication is barely enforced in route dependencies.

Testing volume is high, but test design does not fully protect production behavior. Several suites pass while integration defects remain, and the default `pytest` command fails collection due stale or mislocated test artifacts. Net result: strong research-engine potential with weak release engineering discipline at repo boundaries.

## Critical Issues (Must Fix)
1. Canonical ingestion endpoint is broken due double-prefix route composition (`/api/v1/ingestion/*` expected, `/api/v1/api/ingestion/*` actually mounted).
   - Evidence: `app/routes/ingestion.py:28`, `app/main.py:954`
   - Runtime proof (2026-02-12): `POST /api/v1/ingestion/paper -> 405`, `POST /api/v1/api/ingestion/paper -> 200`, `GET /api/v1/ingestion/stats -> 404`, `GET /api/v1/api/ingestion/stats -> 200`.

2. Ingestion accepts `"observation"` in request model but crashes when converting to core enum.
   - Evidence: `app/routes/ingestion.py:42`, `app/routes/ingestion.py:44`, `app/routes/ingestion.py:339`, `src/services/web_of_belief.py:97`
   - Impact: valid payload causes unhandled `ValueError: 'observation' is not a valid EpistemicLevel`.

3. Gap predictor level filtering is logically broken for enum-backed beliefs; mechanism/validation gaps can be silently missed.
   - Evidence: `src/services/gap_predictor.py:596`, `src/services/gap_predictor.py:597`, `src/services/gap_predictor.py:599`, `src/services/gap_predictor.py:828`, `src/services/gap_predictor.py:829`, `src/services/gap_predictor.py:831`
   - Root cause: compares `str(level).upper()` against bare names; enum stringification yields `EPISTEMICLEVEL.*`.

4. BN frontend is not shippable: production build fails with TypeScript type/export errors.
   - Evidence: `frontend-v2/src/features/explorer/BeliefNodes.tsx:28`, `frontend-v2/src/features/explorer/WebView.tsx:267`, `frontend-v2/src/lib/api-client.ts:411`, `frontend-v2/src/lib/api-client.ts:412`, `frontend-v2/src/lib/api-client.ts:413`, `frontend-v2/src/lib/api-client.ts:414`
   - Runtime proof (2026-02-12): `npm run build` exits non-zero with TS errors.

5. Secrets handling is unsafe/inconsistent on user-facing profile routes.
   - Evidence: `app/routes/profile.py:11`, `app/routes/profile.py:22`, `app/routes/profile.py:27`, `app/routes/profile.py:29`
   - Impact: plaintext API keys stored in `kv` with default `user_id=1`, no auth dependency, direct write surface.

## Major Issues (Should Fix)
1. Duplicate OpenAPI operation IDs from duplicate router mounting and duplicated endpoint path declarations.
   - Evidence: `app/main.py:3`, `app/main.py:5`, `app/main.py:971`, `app/main.py:973`, `app/routes/interactions.py:8`, `src/services/admin_service.py:140`, `src/services/admin_service.py:166`
   - Impact: unstable schema generation, client codegen ambiguity.

2. Authentication is effectively optional for most of the app; only one route clearly consumes `get_current_user`.
   - Evidence: `app/main.py:48`, `app/main.py:51`, `app/main.py:323`
   - Related write/key surfaces without auth: `app/routes/keys.py:12`, `app/routes/keys.py:17`, `app/routes/profile.py:22`.

3. Test blind spot allows broken path composition to pass route tests.
   - Evidence: `tests/test_ingestion_routes.py:35`, `tests/test_main_wiring.py:48`
   - Impact: tests assert router internals or substring presence, not canonical public endpoint contract.

4. Default test command reliability is poor: repo-level `pytest -q` fails collection on stale/misplaced tests.
   - Evidence: `_review_package_2026_01_23/test_claim_gallery_builder.py:14`, `scripts/test_extract_7panel_parsing.py:12`
   - Impact: CI/dev confidence degrades because baseline command is not clean.

5. Hardcoded absolute filesystem paths reduce portability and break reproducibility across machines.
   - Evidence: `app/routes/annotator.py:41`, `app/routes/annotator.py:42`, `app/routes/annotator.py:43`

6. BN frontend test discipline is incomplete (`npm test` is undefined).
   - Evidence: `frontend-v2/package.json:6`, `frontend-v2/package.json:11`

7. BN required Python environment is brittle in this workspace (`bn_venv/bin/python3` points to missing `/opt/anaconda3/bin/python3`).
   - Evidence: `BN_graphical/bn_venv/bin/python3` symlink target
   - Impact: documented local commands (`make check-env`, local pytest) fail immediately here.

## Minor Issues (Nice to Fix)
1. FastAPI lifecycle deprecation usage (`@app.on_event`) persists.
   - Evidence: `app/main.py:897`, `app/main.py:920`

2. Deprecated `regex=` query argument still used.
   - Evidence: `app/routes/entrenchment.py:95`, `app/routes/entrenchment.py:124`, `app/routes/entrenchment.py:313`

3. Deprecated UTC API usage in cross-layer query timestamps.
   - Evidence: `src/services/cross_layer_query.py:480`

4. Task list documentation drift for BN frontend paths (points to non-existent legacy locations).
   - Evidence: `docs/CODEX_TASK_LIST_2026-02-12.md:147`, `docs/CODEX_TASK_LIST_2026-02-12.md:149`

5. Core service files are oversized and mixed-concern, raising long-term maintenance and regression risk.
   - Evidence: `src/services/web_of_belief.py` (~2925 LOC), `src/services/epistemic_causal_bridge.py` (~3472 LOC), `src/services/web_persistence.py` (~3077 LOC), `app/main.py` (~1151 LOC)

## Architecture Assessment
The architecture intent is credible: epistemic web state, causal bridge logic, and frontend evidence interaction are conceptually aligned and unusually rich for a research system. The layered framing (attribute -> mediator -> outcome with epistemic warrants) is defensible and gives a strong basis for explanatory UI.

The implementation problem is boundary coherence, not lack of components. Route prefix conventions are inconsistent (`/api/v1/api/...` leakage), route registration is duplicated, and backend/frontend contracts drifted enough that build-time and runtime breakages are now routine. Security model assumptions (local-only) are documented, but real route surfaces and auth usage do not reliably enforce safe defaults if deployment context changes.

Overall: architecture strategy is strong; architecture execution discipline is weak. The system can become robust, but only if integration contracts, endpoint governance, and build/test gates are treated as first-class engineering constraints.

## Scores

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Architecture | 5/10 | Strong conceptual design; weak operational consistency across routing, contracts, and integration boundaries. |
| Code Quality | 4/10 | Multiple concrete logic bugs, duplicated route declarations, path hardcoding, and oversized mixed-concern modules. |
| Security | 3/10 | Unauthenticated key/write surfaces, plaintext key storage path, optional auth dependency pattern. Acceptable only under strict localhost discipline. |
| Testing | 6/10 | High test volume and many passing suites, but critical blind spots and default test command instability remain. |
| Documentation | 6/10 | Extensive docs exist, but critical drift/mismatch with real paths and operational behavior. |
| Scalability | 4/10 | SQLite everywhere and single-process assumptions; workable for small research loads, risky for larger or concurrent workloads. |
| **OVERALL** | **4.7/10** | Weighted score. Research-grade prototype with serious integration, security, and release-readiness deficits. |

## Recommended Refactors (Priority Order)
1. Fix ingestion public contract immediately: normalize router prefixes and lock canonical path tests to `/api/v1/ingestion/*`.
2. Fix ingestion enum mismatch (`observation` vs `observational`) and add explicit validation/error mapping instead of raw enum exceptions.
3. Repair `gap_predictor` level classification using enum `.value` (or typed checks), then add regression tests for mechanism/validation gap detection.
4. Restore BN frontend build green state (React Flow node typing + duplicate export cleanup) and gate merges on `npm run build`.
5. Consolidate key management: remove/lock plaintext profile key route, enforce authenticated ownership semantics on key APIs.
6. Remove duplicate router includes and duplicate endpoint declarations to eliminate OpenAPI operation-id collisions.
7. Harden test harness: ensure repo-root `pytest -q` is clean, quarantine stale test artifacts, and require app-level integration assertions (not substring path checks).
8. Eliminate hardcoded absolute paths in route modules; use configurable env/path resolution.
9. Migrate deprecated FastAPI patterns (`on_event`, `regex`) and modernize timestamp handling (`datetime.now(timezone.utc)`).
10. Start modular decomposition of oversized service modules with explicit interfaces and contract tests.

## Questions for Developer
1. Is `/api/v1/ingestion/*` the intended public contract, or do you intentionally want `/api/v1/api/ingestion/*`? Current docs and behavior conflict.
2. Should `observation` and `observational` both be valid external inputs, or should one be canonical and the other rejected with clear 422?
3. Do you want to formally deprecate `app/routes/profile.py` in favor of `app/routes/keys.py` (encrypted path), or keep both?
4. Should local-only security assumptions remain acceptable for all current deployments, or should auth be enforced by default now?
5. For BN_graphical, is `frontend-v2` now the canonical frontend for integration sprints (replacing older `src/components/*` references in task docs)?
6. Should TASK-1 prioritize functional reliability first (ingestion + build + gap predictor), or security hardening first (key endpoints + auth dependencies)?

## Verification Commands Run
- `./venv/bin/python` route probes against `app.main` (ingestion path behavior, enum crash case).
- `./venv/bin/pytest -q tests/test_gap_predictor.py tests/test_edge_justification.py tests/test_int_pipeline.py tests/test_ingestion_routes.py tests/test_main_wiring.py` -> `100 passed` with warnings.
- `./venv/bin/pytest -q` -> collection errors from non-canonical test locations.
- `npm run build` in `BN_graphical/frontend-v2` -> TypeScript compile failure.
- `npm test` in `BN_graphical/frontend-v2` -> missing script.
