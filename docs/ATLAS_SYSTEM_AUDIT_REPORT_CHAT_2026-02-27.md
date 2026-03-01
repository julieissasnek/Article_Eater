# ATLAS System Audit Report
Date: 2026-02-27
Auditor: Chat (Codex, GPT-5) — I am Chat.

## Executive Summary
ATLAS has a serious architecture/implementation split: the philosophical model is ambitious and often well-commented, but core operational paths are either disconnected or silently degraded. The strongest examples are governance and integration automation. `scheduled_pipeline.py` reports success even when integration is effectively a no-op, and the HITL approval service tries to import a non-existent `IntegrationOrchestrator` class. That means pipeline health can look green while throughput is functionally blocked.

The epistemic core has real strengths. `web_of_belief.py` is substantial, modularized, and explicit about coherentist intent. Coherence, entrenchment, stubs, and theory worlds are all implemented with concrete code paths. But multiple credence/confidence systems (bridge multiplicative, noisy-OR warrant combination, weighted linear graph confidence, plus operational caps and overrides) are not unified under one semantics, so "credence" is used in several non-equivalent ways.

Governance currently under-delivers relative to claims. Invariants are defined, but practical checks are often vacuous because the expected DB/tables (`web.db`, `belief_versions`) are absent or mismatched in this environment, and many failures are swallowed defensively. The result is a robustly non-crashing system that can pass through broken states without surfacing hard failure signals.

## Scores (1-10)
- Philosophical coherence: 6/10
- Architectural integrity: 4/10
- Code quality: 5/10
- Robustness: 5/10
- Intelligibility: 6/10
- Overseer/governance: 3/10
- Overall: 4.8/10

## Level 1 Findings: Philosophy
- Quinean revisability is asserted clearly in `src/services/web_of_belief.py` (module header and class docstrings), and observations are said to be revisable.
- Implementation tension: `WarrantService` gives observational beliefs prima facie warrant (`_identify_observational`, `compute_warrant`), which is a soft privilege and can drift toward foundationalism if not counterbalanced by defeat logic.
- Coherence is mathematically ad hoc but explicit: `src/services/web_of_belief_modules/coherence.py` computes local coherence by constraint type, then averages over constraints.
- Stubs are not just defined; they are active in practice (`add_stub`, `integrate_stub`) and empirically abundant (high isolated/orphan rates in health scripts).
- Theory worlds are implemented (`register_theory`, `_rebuild_theory_worlds`, `update_theory_worlds`) as a Quine extension. This is coherent as an engineering extension but not strict Quine; it is a deliberate hybrid.
- Four credence/confidence layers do not compose into one clean epistemic semantics:
  - Bridge multiplicative: `compute_bridged_credence` in `src/services/bridge_warrants.py`.
  - Noisy-OR warrant aggregation: `compute_total_warrant` in `src/epistemic/warrant_scaling.py`.
  - Ceiling-constrained bridge priors: `DEFAULT_BRIDGE_CONFIDENCE` + linting in `scripts/lint_bridge_ceilings.py`.
  - Weighted linear edge confidence: `GraphConfidenceService` (`0.4/0.3/0.3`) in `src/services/graph_confidence_service.py`.
- Pi projection Web -> BN exists in `EpistemicCausalBridge.build_causal_models`, but it is lossy (tag/keyword and filtered belief selection). Backflow exists (`update_web_from_result`) but is optional and not part of the default integration pipeline.
- `PATHWAY_DEFAULTS` in `src/epistemic/bn_edges.py` is keyword-substring matching, which is brittle rather than principled causal typing.

## Level 2 Findings: Architecture
- Module map run (`python3 scripts/atlas_system_map.py --modules`): 562 modules, 591 edges; hubs dominated by `src.services.web_of_belief` (imported by 46 modules).
- Orphan modules reported by system map: 20.
- Import cycles exist (Tarjan on generated module graph): 2 SCCs >1 node, including:
  - `src.cmr <-> src.cmr.building_eval`
  - `src.services.theory_matcher <-> src.services.extraction_to_web`
- ClaimV2 is not enforced as universal ingress:
  - `ClaimV2` is a dataclass with no strict runtime schema enforcement in `__post_init__`.
  - `extraction_to_web.py` maps raw dicts directly to `Belief`.
  - `orchestrator._step_pre_validate` only checks statement presence.
- NodeType taxonomy (12 values) is defined, but in current queue data usage is near-zero: `10243` findings inspected, `0` with `node_type`.
- Database source-of-truth is fragmented:
  - Health scripts resolve `web_persistence.db` via `db_locator`.
  - `atlas_system_map.py` hardcodes `web_of_belief.db` candidates.
  - Overseer scripts look for `web.db` and `overseer.db`; both missing in this environment.
- Migration strategy exists (`src/services/db_migrations.py`) but appears operationally optional/manual.
- Foreign keys are schema-defined in `web_persistence.py`, but enforcement is connection-local; ad hoc external clients can bypass integrity.
- WAL/concurrency configuration is not standard in core web DB paths (observed journal mode `delete` for `data/web_persistence.db` and `data/web_of_belief.db`).
- 14-step cascade exists in code, but transaction semantics are weak:
  - Step-level try/except with critical/non-critical abort logic.
  - No global transaction rollback for partial writes if later non-critical steps fail.

## Level 3 Findings: Code Quality
- Test run (`pytest tests/ -x --tb=short -q`): `1 failed, 737 passed, 4 skipped, 11 warnings`.
  - Failure: `tests/test_db_path_contracts.py::test_no_hardcoded_absolute_web_or_af_db_paths`.
- Import sweep (297 modules): 4 import failures (`structlog`, `streamlit`, `google`).
- Lint (`ruff check src/ --select E,W --statistics`): 2966 errors.
- Exception-swallowing debt is high:
  - `src`: 117 `except Exception:`
  - `scripts`: 149 `except Exception:`, 16 bare `except:`
- High type-annotation coverage by AST scan: ~96.3% of functions have annotations.
- Severe integration bug:
  - `ExtractionApprovalService._trigger_integration` imports `IntegrationOrchestrator`, but only `PaperIntegrationOrchestrator` exists.
  - This causes integration trigger failure after approval.

## Level 4 Findings: Robustness
- Missing DB adversarial test (temporary move/restore of `data/web_of_belief.db` + `python3 scripts/overseer_nightly_v2.py`):
  - System does not crash hard.
  - `overseer_audit` returns `missing_db`.
  - Other stages continue and produce report/notification.
- Malformed input behavior:
  - Negative p-value and `ae_confidence > 1.0` do not fail validation in `claim_to_belief`; values are clamped and accepted.
  - This favors liveness over strict correctness.
- 10,000-finding stress test:
  - `claim_to_belief` loop handled 10k synthetic items in ~1.88s (embedding disabled), no crash.
  - No explicit guardrails for oversized extraction payloads.
- Circular constraints test (`A supports B`, `B supports A`):
  - No stack overflow.
  - Equilibrium call returned stable coherence.
- Concurrent run risk:
  - Queue operations are JSON read/modify/write without file-locking in `ExtractionApprovalService` and scheduler scripts.
  - Race conditions are plausible during simultaneous pipeline + human approval actions.

## Level 5 Findings: Intelligibility
- `ARCHITECTURE.md` is readable and ambitious, but at least 5 claims are stale/inconsistent with runtime reality:
  - Claims DB files are `data/web.db` and `data/overseer.db`; both missing here.
  - Active web data is in `data/web_persistence.db`.
  - "Every belief derives from ClaimV2" is contradicted by dict-based ingestion paths.
  - System map and health tooling disagree on canonical DB path.
  - Pipeline integration described as active automation, but scheduler integration step only logs "Would integrate".
- `SCHEMA_REGISTRY.md` is useful as a conceptual index but thin on live DB schema/state reconciliation.
- Onboarding assessment:
  1. Understand system in 30 minutes: possible at high level.
  2. Run system in 60 minutes: blocked by env/dependency/path mismatches (`python` missing, optional deps missing, DB aliasing).
  3. Make meaningful change in 120 minutes: possible for experienced contributor, but governance/pipeline path confusion is a major drag.
- Naming discipline is mostly good; no broad `utils.py/helpers.py/misc.py` sprawl found in `src/` and `scripts/`.

## Level 6 Findings: Governance
- Overseer invariants are declared and coded (`check_integrity`), but checks can be vacuous:
  - Expected tables/columns (`belief_versions`, `claim_json`, `provenance_json`, `credence`) do not exist in active DB files here.
  - Exceptions are swallowed to "no violations" defaults.
- `pipeline_registry` support exists in code, but `data/overseer.db` is missing, so registry population is effectively absent.
- Stale-pipeline detection logic exists (`get_pipeline_health` thresholds), but depends on registry availability.
- HITL notification flow exists and is active; escalation and pruning are weak:
  - Queue grows with repeated alerts.
  - Archival requires explicit `archive_read`; no automatic TTL/escalation policy observed.
- Provenance visibility for reviewers is partial (summary/preview), not full trace-to-PDF proof chains in the approval UX.
- AESHI formula is explicit in `scripts/compute_system_health.py`; hard-gate fail caps score at `49.0`, explaining persistent red bands.
- Historical evidence shows AESHI has exceeded 70 before (e.g., archived reports with `76.14`, `83.77`), so current 49 is not a permanent ceiling.

## Level 7 Findings: Integration Tests
- Command 1: `python3 scripts/atlas_system_map.py`
  - Status: PASS
  - Finding: Reports web DB with 0 beliefs due path mismatch with active DB.
  - Classification: DESIGN
- Command 2: `python3 scripts/scheduled_pipeline.py status`
  - Status: PASS
  - Finding: 630 accepted awaiting review, 0 integrated; pipeline "PASS" can be misleading because integration stage is mostly non-operative.
  - Classification: MAJOR
- Command 3: `python3 scripts/check_notifications.py pending`
  - Status: PASS
  - Finding: Repeated warning notifications (health + review backlog), no escalation behavior.
  - Classification: MINOR
- Command 4: `python3 scripts/review_extractions.py list`
  - Status: PASS
  - Finding: Large HITL backlog (630 pending).
  - Classification: MAJOR
- Command 5: `python3 scripts/overseer_nightly_v2.py --dry-run`
  - Status: Non-zero exit behavior + "OVERSEER FAILED" in shell flow
  - Finding: health command fail cascades to non-zero flow; governance reports generated anyway.
  - Classification: MAJOR
- Command 6: `pytest tests/ -x --tb=short -q`
  - Status: FAIL (1 test)
  - Finding: DB path contract regression.
  - Classification: MAJOR
- Command 7: import sweep (`python3 -c ... importlib.import_module(...)`)
  - Status: FAIL (4/297)
  - Finding: missing runtime deps (`structlog`, `streamlit`, `google`).
  - Classification: MAJOR
- Command 8: `ruff check src/ --select E,W --statistics`
  - Status: FAIL-equivalent quality signal (2966 errors)
  - Finding: very high style/quality debt.
  - Classification: MINOR

## Top 10 Critical Issues (Ranked by Severity)
1. Integration automation is broken: approval service imports non-existent `IntegrationOrchestrator`, blocking auto-integration path.
2. Scheduled integration stage is effectively a no-op (`Would integrate` only), yet pipeline status can still report PASS.
3. DB path fragmentation (`web.db` vs `web_of_belief.db` vs `web_persistence.db`) causes contradictory health/map/governance views.
4. Overseer invariants can pass vacuously due schema/table mismatch + defensive exception swallowing.
5. ClaimV2 "universal contract" is not operationally enforced at major ingestion paths.
6. BN update in integration cascade is in-memory and not clearly persisted to canonical BN storage.
7. Queue update paths are lock-free JSON writes, creating race risk under concurrent worker + human actions.
8. Orphan/isolation rate remains very high (~36-50% in observed runs), undermining coherentist objectives.
9. Runtime dependency holes (`structlog`, `streamlit`, `google`) break import completeness.
10. Lint/exception debt is high enough to mask real defects and reduce maintainability.

## Top 5 Strengths
1. Core epistemic engine is explicit, substantial, and philosophically literate in code comments and structure.
2. Type annotation coverage is high (~96%), aiding tooling and refactoring safety.
3. Test suite breadth is substantial (737 passing tests in one run before first failure).
4. System degrades gracefully under missing components instead of hard-crashing.
5. Health/reporting tooling (`check_web_bn_health`, `compute_system_health`, `atlas_system_map`) provides actionable observability when paths are aligned.

## Recommended Priority Actions
1. Unify canonical DB paths across all scripts/services (`db_locator`, `atlas_system_map`, overseer scripts) and remove `web.db`/`web_of_belief.db` ambiguity.
2. Fix integration control plane immediately:
   - replace bad `IntegrationOrchestrator` import with `PaperIntegrationOrchestrator`;
   - make scheduled integration actually invoke integration for approved papers;
   - fail pipeline stage when integration is not executed.
3. Make invariant checks fail-loud on schema mismatch (separate "check unavailable" from "check passed").
4. Enforce ClaimV2 at ingress boundaries with strict validation + quarantine path, not permissive dict pass-through.
5. Add locking/atomic update semantics for queue JSON operations or migrate queue state to SQLite.
6. Persist BN step outputs in integration cascade to canonical BN artifact, with verification in post-validate.
7. Reduce exception swallowing in critical paths; add structured error classes and hard-fail modes for governance.
8. Address the single pytest regression first, then establish a CI gate for path contract + import completeness + selected lint budget.
9. Add explicit stress limits and validation for malformed extraction payloads (negative p-values, confidence bounds, oversized findings).
10. Add escalation/TTL policy for notifications (dedupe, aging, critical escalation after N hours unread).

## References
- Quine, W. V. O. (1951). Two dogmas of empiricism. *The Philosophical Review, 60*(1), 20-43. [15,000+ citations]
- Haack, S. (1993). *Evidence and inquiry: Towards reconstruction in epistemology*. Blackwell. [2,000+ citations]
- Rawls, J. (1971). *A theory of justice*. Harvard University Press. [80,000+ citations]
- Pearl, J. (2009). *Causality: Models, reasoning, and inference* (2nd ed.). Cambridge University Press. [30,000+ citations]
- Thagard, P. (1989). Explanatory coherence. *Behavioral and Brain Sciences, 12*(3), 435-467. [1,500+ citations]
- BonJour, L. (1985). *The structure of empirical knowledge*. Harvard University Press. [2,000+ citations]
- Bovens, L., & Hartmann, S. (2003). *Bayesian epistemology*. Oxford University Press. [1,200+ citations]
- Toulmin, S. E. (1958). *The uses of argument*. Cambridge University Press. [10,000+ citations]
- Pollock, J. L. (1995). *Cognitive carpentry: A blueprint for how to build a person*. MIT Press. [500+ citations]
- Walton, D. (1996). *Argumentation schemes for presumptive reasoning*. Erlbaum. [1,500+ citations]
