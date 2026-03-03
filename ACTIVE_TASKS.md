# ACTIVE_TASKS.md

*Auto-updated by Claude Code sessions*

This file tracks which tasks are actively being worked on by which terminal. **Check this file BEFORE starting any task.**

---

## Protocol

### Before Starting Work
1. **Read this file** to see what's claimed
2. **Claim your task** by adding a row to Active Claims
3. **Start work** only after claiming

### While Working
- Update status periodically if long-running
- Note any blockers in the Notes column

### When Done
1. **Move to Completed Today** section with outcome
2. **Remove from Active Claims**
3. **Update TASKS.md** with completion status

---

## Active Claims

| Task ID | Description | Terminal | Claimed At | Status | Notes |
|---------|-------------|----------|------------|--------|-------|
| RUTHLESS-V8 | Comprehensive end-to-end system audit + fix | CW-COWORK-0302 | 2026-03-02 20:00 | IN_PROGRESS | Full pipeline audit, all subsystems, improvement recommendations |
| V3-BACKFILL | Quantitative backfill of extraction fields | DK-TERMINAL | 2026-03-02 | COMPLETE | 887/920 success (96.4%), 117 findings backfilled, sample_size 4%→5%, effect_size 21% |

---

## Completed Today (2026-02-19)

| Task ID | Description | Terminal | Completed At | Outcome |
|---------|-------------|----------|--------------|---------|
| 1.1 | Enum Drift Fix | CODEX-20260219-0046 | 00:47 CET | `python3 scripts/check_enum_drift.py` reports 0 drift issues |
| 1.3 | Load Staging Theory-Links | CODEX-20260219-T1 | 00:55 CET | Added CMR staging model + loader, loaded 1045 rows into `ae.db` |
| 1.4 | WIS Conversion Module | CODEX-20260219-T2 | 00:53 CET | Added `to_wis()` in `effect_size_converter.py` + tests |
| D.11 | Web of Belief Rebuild | CODEX-20260219-T3 | 00:54 CET | Rebuilt `data/web_persistence_v2.db` from structured claims and generated `docs/web_health_report_post_rebuild.md` |
| D.13 | Sprint D Validation | CODEX-20260219-T4 | 00:58 CET | Generated `docs/sprint_d_validation_report.md` (verdict: NEEDS WORK) |
| 1.5.C2a | ClaimType aliases in article_decomposer.py | CODEX-20260219-T5 | 01:30 CET | Verified canonical alias mapping in BN_graphical; drift check clean |
| 1.5.C2b | EvidenceType alias in enhanced_edge.py | CODEX-20260219-T6 | 01:30 CET | Verified `empirical -> observational` in BN_graphical; drift check clean |
| 1.5.C2d | CI shape schema fix | CODEX-20260219-T7 | 01:30 CET | Verified CI object shape in BN_graphical contract; drift check clean |
| 1.5.C3a | ArticleTypeCrosswalk in article_extraction_contracts.py | CODEX-20260219-T8 | 01:30 CET | Verified canonical crosswalk mapping in Outcome_Contractor; drift check clean |
| 1.5.C3b | ArticleTypeCrosswalk in article_type_classifier.py | CODEX-20260219-T9 | 01:30 CET | Verified canonical crosswalk mapping in Outcome_Contractor; drift check clean |
| EC-3 | Cartwright scope metadata | CODEX-20260219-T10 | 01:30 CET | Added `scope_population/context/temporal` fields to Belief + serialization |
| ARCH-5d | Break up web_of_belief.py | CODEX-20260219-T11 | 01:30 CET | Extracted modular helpers (`web_of_belief_modules`) + compatibility wiring |
| 3.0.5-A | Admin dashboard | CODEX-20260219-T12 | 01:30 CET | Added `streamlit_app/pages/admin.py` with overview, belief inspector, constraint viewer |
| ATK-2 | Attack pattern extraction | CODEX-20260219-T13 | 01:30 CET | Added ATK pattern annotations to claim semantics + tests |
| ATK-4 | Attack review UI | CODEX-20260219-T14 | 01:30 CET | Added `streamlit_app/pages/7_attack_review.py` for attack cue review |

---

## Completed Today (2026-02-18)

| Task ID | Description | Terminal | Completed At | Outcome |
|---------|-------------|----------|--------------|---------|
| D.10 | Batch extraction pipeline | Codex | 02:45 | 72 claims from 116 papers |
| D.12 | CMR integration | CC | 02:50 | 22 papers, 67 claims, 50 matched |

---

## MVP Integration Tasks (ARCHIVED - COMPLETE)

**See `PARALLEL_WORK.md` for full lane details and file ownership.**

### Phase A: Can Start Immediately (3 parallel terminals)

| Lane | Description | Terminal | Status | Dependencies |
|------|-------------|----------|--------|--------------|
| MVP-0 | Contracts & Schemas | T2 | ✓ COMPLETE | None |
| MVP-1 | Persistent Web State | T1 | ✓ COMPLETE | None |
| MVP-GUI | Streamlit Scaffold | T3 | READY | None |

### Phase B: After MVP-1 Complete (2 can run parallel)

| Lane | Description | Terminal | Status | Dependencies |
|------|-------------|----------|--------|--------------|
| MVP-2 | Batch Processing | T1 | ✓ COMPLETE | MVP-1 ✓ |
| MVP-3 | Query Engine | T2 | ✓ COMPLETE | MVP-0 ✓, MVP-1 ✓ |

### Phase C: Final Integration

| Lane | Description | Terminal | Status | Dependencies |
|------|-------------|----------|--------|--------------|
| MVP-GUI | Wire Backends | T3 | READY | MVP-1 ✓, MVP-3 ✓ |
| MVP-5 | Polish & Demo | T3 | BLOCKED | MVP-GUI |

---

## Available Tasks (Not Claimed)

**SEE: `docs/CODEX_BACKLOG_PROMPT.md` for full task list with context and instructions.**

### Priority 1: Sprint D Completion (if AG hasn't done)
| Task ID | Description | Owner | Status |
|---------|-------------|-------|--------|
| D.11 | Web of Belief Rebuild | AG/Codex | COMPLETE |
| D.13 | Sprint D Validation | AG/Codex | COMPLETE |

### Priority 2: Sprint 10 Residuals
| Task ID | Description | Status |
|---------|-------------|--------|
| 1.1 | Enum Drift Fix | COMPLETE |
| 1.3 | Load Staging Theory-Links | COMPLETE |
| 1.4 | WIS Conversion Module | COMPLETE |

### Priority 3: Enum Drift Fixes
| Task ID | Description | Status |
|---------|-------------|--------|
| 1.5.C2a | ClaimType aliases in article_decomposer.py | COMPLETE |
| 1.5.C2b | EvidenceType alias in enhanced_edge.py | COMPLETE |
| 1.5.C2d | CI Shape schema fix | COMPLETE |
| 1.5.C3a | ArticleTypeCrosswalk in article_extraction_contracts.py | COMPLETE |
| 1.5.C3b | ArticleTypeCrosswalk in article_type_classifier.py | COMPLETE |

### Priority 4-6: See docs/CODEX_BACKLOG_PROMPT.md
- Panel recommendations (EC-1, EC-3, SY-9)
- Architectural tasks (ARCH-*)
- Admin/API features

---

## Completed Today (2026-02-17)

| Task ID | Description | Terminal | Completed At | Outcome |
|---------|-------------|----------|--------------|---------|
| 13.10 | Field Validation Protocol Generator | CC-0217 | 2026-02-17 20:15 UTC | src/cmr/field_validation.py (5 templates: L2, VF3, VIEW1, SOC2, MAT1), 45 tests passing |
| 12.21 | Full System Regression Suite | CC-0217 | 2026-02-17 20:35 UTC | 281 CMR tests passed, Tier 2 validation passed, Ulrich 1984 pipeline passed, report at docs/SPRINT_12_REGRESSION_REPORT_2026-02-17.md |
| CMR-3.2 | Batch 2 Template Computations (20 templates) | CLAUDE-0217-CTX | 2026-02-17 UTC | 20 compute functions in template_computations.py, 52 tests, DECISIONS.md D3.2.1-D3.2.6 |
| GEA-1 | Grounded expert retrieval + recursion hardening | Codex-Terminal | 2026-02-17 08:16 UTC | Alias-safe interaction traversal and `overall_maturity` confidence mapping |
| GEA-2 | Grounded expert empirical evidence layer | Codex-Terminal | 2026-02-17 08:20 UTC | WebOfBelief SQLite empirical claim integration into grounded responses |
| GEA-3 | Grounded expert BN calibration layer | Codex-Terminal | 2026-02-17 08:31 UTC | BN posterior calibration summary added to response model + output formatting; tests passing |
| P8.1 | Variable mapping coverage audit | Codex-Terminal | 2026-02-17 08:36 UTC | Created `docs/P8_1_VARIABLE_MAPPING_AUDIT_2026-02-17.md` (12,596-row production audit + root-cause summary) |
| P8.2 | Canonical env/out variable registry | Codex-Terminal | 2026-02-17 08:55 UTC | Added `scripts/build_canonical_env_out_registry.py` and generated `contracts/vocab/canonical_env_out_registry.json` |
| P8.3 | LLM fallback for unmapped variables | Codex-Terminal | 2026-02-17 09:06 UTC | Added staged resolver fallback in realtime intake + PDF completion (`llm_lookup_fallback`, `semantic_lookup_fallback`, queueing safeguards) |
| P8.4 | pgmpy BN inference wiring | Codex-Terminal | 2026-02-17 09:16 UTC | Added optional pgmpy model/query APIs (posterior, d-separation, Markov blanket) in `incremental_bn.py` with graceful fallback |
| P8.5 | Zotero->BibTeX->extraction E2E verification | Codex-Terminal | 2026-02-17 09:13 UTC | Added `tests/test_bibtex_e2e_flow.py` and validated BibTeX parsing/matching/ingestion suite (`57 passed`) |
| P8.6 | Extraction quality metrics | Codex-Terminal | 2026-02-17 09:10 UTC | Added match-type/fallback-rate instrumentation and JSON reporting in quality gate + per-paper audit enrichment |
| P8.6-FIX | Quality gate denominator correction | Codex-Terminal | 2026-02-17 09:32 UTC | Corrected article type metadata coverage denominator to typed rows; quality gate now PASS |
| CODEX-TASKS-2026-02-12/TASK-2 | Fix Major Issues from evaluation | Codex-Terminal | 2026-02-17 12:30 UTC | Added canonical-ingestion and OpenAPI operationId uniqueness wiring tests in `tests/test_main_wiring.py`; added BN frontend `npm test` build gate in `BN_graphical/frontend-v2/package.json`; deprecation cleanup (`lifespan`, `pattern`, timezone-aware UTC); post-closure compatibility hardening restored legacy enum aliases/surfaces (`ClaimType`, VOI/discovery `GapType`) and argument query handler routing in `QueryEngine`; verification: `./venv/bin/pytest -q` => `2935 passed, 9 skipped`. |
| ENT-6 | Replay DB strategy + safe replay runner | Codex-Terminal | 2026-02-17 12:45 UTC | Added `ScholarlyReplayService.with_safe_replay_copy()` + master-filtered loader in `src/services/entrenchment_replay.py`; added `scripts/run_entrenchment_replay_safe.py`; added `tests/test_entrenchment_replay_safe.py`; verification: `19 passed` for entrenchment test subset. |
| I9.1 | ResearchQueueService implementation | Codex-Terminal | 2026-02-17 09:47 UTC | Added queue models + service (`refresh_queue`, assignment, result reporting) with persisted state and fallback query generation; tests added. |
| I9.2 | Theory-driven gap detection | Codex-Terminal | 2026-02-17 09:48 UTC | Added Tier 1 prediction-driven target generation and queue-level theory coverage metrics with tests. |
| I9.3 | Queue to Zotero watcher integration | Codex-Terminal | 2026-02-17 09:50 UTC | Added BibTeX delta watcher + passive target matching and `sync_zotero_to_queue()` auto-report flow with tests. |
| I9.4 | VOI collector registration | Codex-Terminal | 2026-02-17 09:56 UTC | Added collector profile models + queue registration/list/claim APIs with capacity checks, deadlines, and search guidance generation. |
| I9.5 | Research opportunity registry | Codex-Terminal | 2026-02-17 10:10 UTC | Added opportunity lifecycle model + registry methods with auto-creation from `NOT_FOUND` outcomes and persisted state. |
| I9.6 | Streamlit queue dashboard | Codex-Terminal | 2026-02-17 10:15 UTC | Added `streamlit_app/pages/6_research_queue.py` with queue metrics, assignment/status controls, collector forms, opportunity management, and automation triggers. |
| I9.7 | Automated searcher bot | Codex-Terminal | 2026-02-17 10:16 UTC | Added Semantic Scholar-backed bot in `src/queue/automated_searcher.py` plus queue wrapper `run_automated_searcher()` and bot tests. |
| V15-CX-1 | Update task board with Docs 64/65 | Codex-Terminal | 2026-02-17 10:22 UTC | Recorded Sprint V15 Doc 64 (VF-II) and Doc 65 (CREA-III) status + verification in `TASKS.md`. |
| V15-CX-2 | Validate VF3 → CREA2B single-chain | Codex-Terminal | 2026-02-17 10:24 UTC | Confirmed `VF3 -> Affect -> CREA2B -> Divergent Thinking` linkage and no direct VF3→CREA2 interaction path (double-count guard). |
| V15-CX-3 | Verify CREA2 interaction matrix sub-additivity lookup | Codex-Terminal | 2026-02-17 10:25 UTC | Confirmed all 7 combinations return expected sub-additivity (`A+B 0.84`, `A+C 0.76`, `B+C 0.80`, `A+B+C 0.70`, singleton 1.0). |
| V15-CX-STAB | Restore V14 smoke gate compatibility post-CREA4 | Codex-Terminal | 2026-02-17 10:28 UTC | Backfilled missing V14 lifespan root fields on `CREA4`; `./bin/prod_smoke.sh` now passes. |

## Completed Today (2026-02-12)

| Task ID | Description | Terminal | Completed At | Outcome |
|---------|-------------|----------|--------------|---------|
| CODEX-TASKS-2026-02-12/TASK-0 | Ruthless System Evaluation | Codex-Terminal | 2026-02-12 01:23 GMT | `docs/CODEX_EVALUATION_REPORT_2026-02-12.md` |
| CODEX-TASKS-2026-02-12/TASK-1 | Fix Critical Issues | Codex-Terminal | 2026-02-12 01:45 GMT | Ingestion path+enum+gap predictor fixes; profile key hardening; BN TS compile fixed (`npx tsc -b`) |
| CODEX-TASKS-2026-02-12/TASK-3 | Integration Test Suite | Codex-Terminal | 2026-02-12 01:40 GMT | Added `tests/test_full_integration.py` (3 tests passing) |
| CODEX-TASKS-2026-02-12/TASK-4 | Documentation Audit | Codex-Terminal | 2026-02-12 03:20 GMT | Updated `CLAUDE.md`, `docs/SECRETS_AND_KEYS.md`, `docs/RUN_INSTRUCTIONS.md`, and continuation handoff |
| CODEX-TASKS-2026-02-12/TASK-5 | Performance Profiling | Codex-Terminal | 2026-02-12 01:52 GMT | Added `docs/PERFORMANCE_REPORT_2026-02-12.md` |
| CODEX-TASKS-2026-02-12/TASK-6 | Security Hardening | Codex-Terminal | 2026-02-12 03:15 GMT | Guarded `/admin`, `/usage/admin/summary`, and `/api/v1/web/admin/*`; added auth tests |

## Completed Today (2026-02-11)

| Task ID | Description | Terminal | Completed At | Outcome |
|---------|-------------|----------|--------------|---------|
| MVP-0 | Contracts & Schemas | Terminal-2 | — | 3 schemas + docs/MVP_CONTRACTS.md |
| MVP-3 | Query Engine | Terminal-2 | — | query_engine.py (711 lines), CLI, 44 tests, panel review |
| ATK-1 | Wire ArgumentAttack into tensions.jsonl | Terminal-1 | 00:45 | Enhanced get_tensions(), structured evidence in output |
| ATK-3 | Shift classification heuristics | Terminal-1 | 00:45 | StructuredAttackDetector (6 methods), ShiftClassifier (text fallback), 24 tests pass |
| DIAGRAM | Architecture diagram generation | Terminal-1 | 00:30 | docs/diagrams/architecture_layers_2026-02-11.png |

## Completed Yesterday (2026-02-10)

| Task ID | Description | Terminal | Completed At | Outcome |
|---------|-------------|----------|--------------|---------|
| ECB-R2 | Panel P-ECB-R2 Implementation (PA-1 to PA-6) | Terminal-1 | Evening | operator_inferred, dosage_satisfies, TemporalSpec, configurable near_threshold, two-tier tracking |
| ECB-PA | Panel Action Items (D1.1, D1.3, D2.3, D2.5, D2.6) | Terminal-1 | Evening | REMOVE_BY comments, stub warning, --cct flag, complete enabling checks, excluded belief registry |
| ECB-P1 | P1 Features (F6, F7, F9, F14, F16) | Terminal-1 | Evening | 29 boundary tests, prominent warning, contrast-gated feedback, lazy import, user guide |
| ECB-3 | Sprint ECB-3: Van Fraassen and Polish | Terminal-1 | Evening | ContrastTransferType enum, gap identification (5 types), Haack security weight, error handling, 68+153 tests pass, panel review |
| ECB-2 | Sprint ECB-2: Core Integration | Terminal-1 | Afternoon | Pipeline wired (Stage 2.8), CLI flags (--no-causal), feedback loop, 68 tests pass |
| ECB-1 | Sprint ECB-1: Cleanup and Consolidation | Terminal-1 | Morning | Duplicates marked DEPRECATED, features archived to quarantine, test imports fixed, 68+89 tests pass |
| ECB-PLAN | Sprint ECB Planning | Terminal-1 | 12:00 | Panel P-ECB-R convened, 5 docs created, 3 sprints defined |

## Completed Yesterday (2026-02-09)

| Task ID | Description | Terminal | Completed At | Outcome |
|---------|-------------|----------|--------------|---------|
| 3.0.2-G | Alerting/monitoring capability | Terminal-5 | 23:30 | query_alerts.py (~1400 lines), 80 tests, panel review |
| 3.0.1-D | Extended API layer (20 endpoints) | Terminal-5 | 22:45 | api_extended.py (~950 lines), 37 tests |
| 3.0.4-E | Purpose-driven export bundles (Munzner) | Terminal-5 | 22:15 | export_bundles.py (~1000 lines), 54 tests |
| 3.0.4-D | BibTeX generator with full metadata | Terminal-5 | 21:45 | bibtex_generator.py (~700 lines), 83 tests |
| DISC-2 | Wire VOI search to emit gaps | Terminal-1 | 20:30 | voi_search.py funnel integration, 4 tests |
| DISC-1 | Discovery funnel schema + service | Terminal-1 | 20:00 | 006_discovery_funnel.sql, discovery_funnel.py (~900 lines), 31 tests |
| 3.0.3-C | Claim network graph component | Terminal-1 | 18:30 | components/network.py (~300 lines), 2_explore.py updated |
| 3.0.3-D | Admin dashboard wired to real data | Terminal-1 | 18:45 | 5_admin.py with WebOfBelief/API integration |
| 3.0.3-E | Network visualization (vis.js) | Terminal-3 | 17:00 | network_service.py (~1000 lines), 44 tests |
| 3.0.3-F | GraphML/GEXF/DOT export | Terminal-1 | 19:15 | graph_export.py (~1100 lines) |
| 3.0.3-G | Community network visualization | Terminal-1 | 19:20 | 3_communities.py network tab |
| 3.0.3-H | Interactive HTML export | Terminal-1 | 19:30 | graph_export.py to_html() method |
| 3.0.4-F | Report generation (PDF/Markdown) | Terminal-3 | 17:00 | report_generator.py (~958 lines), 46 tests |
| 3.0.5-G | Export audit trail | Terminal-3 | 17:00 | export_audit.py (~650 lines), 34 tests |
| ENT-1-5 | Entrenchment historical replay | Terminal-3 | 17:00 | entrenchment_replay.py, API routes, monitor UI, 16 tests |
| 3.0.2-C | Scope-aware output generation | Terminal-3 | 13:15 | scope_renderer.py (~550 lines), 31 tests |
| 3.0.2-E | LLM integration - WebOfBelief integration | Terminal-4 | 13:30 | llm_query_bridge.py enhancements, 34 tests |
| 3.0.2-F | RELATED, TRENDING, CANONICAL patterns | Terminal-3 | 14:00 | Bates berrypicking extensions, 48 tests |
| 3.0.4-A | Evidence summary generator | Terminal-3 | 14:30 | evidence_summarizer.py (~600 lines), 35 tests |
| 3.0.4-B | Pipeline-friendly formats | Terminal-3 | 14:45 | export_formats.py (~650 lines), 38 tests |
| 3.0.4-C | Verification checklists | Terminal-3 | 15:00 | export_checklists.py (~650 lines), 37 tests |
| SCHEMA-1/2/3 | V2 schemas + extraction templates | Terminal-3 | 09:45 | ae.rule.v2, ae.claim.v2, argument_schemes.json |
| EXT-1-16 | All 16 extraction templates | Terminal-3 | 12:45 | Complete coverage for all article types |
| BIB-1-7 | BibTeX integration | Terminal-2 | Earlier | bibtex_utils.py, ingestion, Streamlit page |

---

## Completed (2026-02-08)

| Task ID | Description | Terminal | Completed At | Outcome |
|---------|-------------|----------|--------------|---------|
| V23.0.0 | Emergent Entrenchment | Terminal-1 | 17:55 | Breaking change committed |
| 3.0-PLAN | Sprint 3.0 Planning | Terminal-1 | 20:30 | 21 expert panel consultation |
| 3.0.1-A/B/C | Unified API (Core 7 endpoints) | Terminal-1 | 20:30 | api_unified.py (~700 lines) |
| 3.0.2-A/B/D | Query Engine + Progressive Disclosure | Terminal-1 | 20:30 | query_parser.py, query_response.py |
| 3.0.3-A/B | Streamlit Interface Core | Terminal-1 | 20:30 | streamlit_app/ (~2000 lines) |
| 2.0.4/2.0.5 | Pipeline testing + Error handling | Terminal-2 | 19:05 | pipeline_logging.py, 1346 tests |
| TD-A/B/C/D/E | All Technical Debt sprints | Various | Earlier | theory_matcher, scope_extractor, scalable_coherence, temporal_parser, incremental_bn |

---

## Blocked Tasks

| Task ID | Description | Blocked By | Since |
|---------|-------------|------------|-------|
| — | — | — | — |

---

## Rules

1. **One task per terminal** at a time (focus)
2. **Claim before work** — no silent starts
3. **Update on completion** — don't leave stale claims
4. **Check dependencies** — don't start blocked tasks
5. **Communicate blockers** — update Blocked section if stuck

---

## Terminal Identification

Terminals should self-identify using a consistent ID pattern:
- `Terminal-1`, `Terminal-2`, etc. (simple)
- `CLAUDE-{timestamp}` (unique per session)
- Or use the session ID from the transcript path

---

*Last coordination check: 2026-02-11 (MVP lanes defined)*
