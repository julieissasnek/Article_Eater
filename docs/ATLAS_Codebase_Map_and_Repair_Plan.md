# ATLAS Codebase Architecture Map & Health Repair Plan
## February 26, 2026

---

## 1. CODEBASE OVERVIEW

875 canonical Python files across 18 architectural layers. The system is fully built — not merely specified. What follows is a structural map organized by functional role, followed by a prioritized repair plan that integrates (a) AG's corpus health findings, (b) the panel's credence formula audit, and (c) the ceiling violation analysis.

---

## 2. ARCHITECTURAL LAYERS

### 2.1 Web of Belief Core (20 files)

The epistemic layer — the "geological map" in our cartographic metaphor — is implemented across two packages:

**WoB Components** (4 files) — `src/services/web_of_belief_components/`
- `enums.py` — warrant types, edge types, belief states (the 7-type hierarchy lives here)
- `graph_models.py` — typed graph representation of the epistemic warrant graph
- `scope_models.py` — scope/boundary modeling for applicability

**WoB Modules** (16 files) — `src/services/web_of_belief_modules/`
- `coherence.py` — coherence satisfaction computation (Thagard-style ECHO?)
- `entrenchment.py` — Quinean entrenchment ranking
- `equilibrium.py` — reflective equilibrium computation
- `evidence_updates.py` — Bayesian updating of belief strengths
- `experiments.py` — experimental design support
- `independence.py` — conditional independence testing (critical for formula debate)
- `mutations.py` — controlled belief revision
- `reporting.py` — web state reporting
- `severity.py` — Mayo-style severity assessment
- `snapshots.py` — state persistence/versioning
- `theory_worlds.py` — possible world semantics
- `value_metrics.py` — value of information computation
- `web_state.py` — current web state management
- `engines.py` — inference engines
- `analysis_ops.py` — analytical operations over the web

### 2.2 Epistemic Infrastructure (28 files)

**Epistemic Core** — `src/epistemic/`
- `bn_edges.py`, `bn_nodes.py` — Bayesian network graph primitives
- `edge_types.py`, `node_types.py` — typed edge/node taxonomies
- `source_quality.py` — source quality assessment
- `warrant_scaling.py` — **KEY FILE**: implements warrant ceiling scaling (the ceiling logic)
- `gap_types.py` — epistemic gap taxonomy

**Epistemic Contracts** — `src/epistemic/contracts/`
- `claim_v2.py`, `edge_v2.py` — v2 claim and edge data contracts

**Entrenchment** — `src/epistemic/entrenchment/` (6 files)
- `critique_propagation.py` — how critiques propagate through the web
- `expert_discount.py` — expert reliability discounting
- `node_type_entrenchment.py` — type-specific entrenchment rules
- `prediction_ledger.py` — prediction tracking for calibration
- `synthesis_rules.py` — belief synthesis rules
- `theory_updating.py` — theory-level updating

**Extraction** — `src/epistemic/extraction/` (8 files)
- Paper classification, pathway classification, rule mapping, source quality

**Monitors** — `src/epistemic/monitors/` (6 files)
- `adversarial_review.py` — adversarial review generation
- `asymmetry_monitor.py` — evidential asymmetry detection
- `bias_detection.py` — systematic bias monitoring
- `coherence_audit.py` — **KEY FILE**: coherence health audit
- `cross_type_coherence.py` — cross-warrant-type coherence checking
- `theory_monitor.py` — theory-level health monitoring

**Validation** — `src/epistemic/validation/`
- `node_template_mapping.py` — validates node-template alignment

### 2.3 Core Services (87 files) — `src/services/`

The main service layer. Key files for health/repair:

- `web_of_belief.py` — **THE** web of belief service (primary orchestrator)
- `epistemic_causal_bridge.py` — the EWG→BN projection function π
- `bridge_warrants.py` — bridge warrant assignment and ceiling enforcement
- `overseer.py` — **THE** overseer service (the governance brain)
- `bn_coherence_client.py` — BN-side coherence checking
- `graph_confidence_service.py` — confidence propagation service
- `incremental_bn.py` — incremental BN updates
- `scalable_coherence.py` — scalable coherence computation
- `stability_engine.py` — belief stability assessment
- `validation.py` — general validation service
- `warrant_service.py` — warrant management
- `web_accumulator.py` — evidence accumulation into the web
- `web_persistence.py` — web state persistence
- `bbn_calibrator.py` — Bayesian belief network calibration
- `dual_epistemology.py` — dual-layer epistemic architecture management

### 2.4 ECB Sub-modules (4 files) — `src/services/ecb_modules/`

The Epistemic Causal Bridge's internal modules:
- `causal_models.py` — causal model representation
- `contrast_classes.py` — contrastive explanation support
- `counterfactuals.py` — counterfactual reasoning

### 2.5 CMR/ATLAS Template Engine (22 files) — `src/cmr/`

The template processing layer (still uses `cmr/` directory name — a renaming target):
- `worked_examples.py` — **KEY FILE**: the worked example computations (where the formula lives)
- `template_matching.py` — template-to-evidence matching
- `template_scanner.py` — template scanning and discovery
- `validation.py` — template validation
- `sensitivity.py` — sensitivity analysis
- `web_template_bridge.py` — web↔template bridge
- `wis.py` — warrant information summary
- `tier2_scores.py` — tier-2 scoring
- `learning/bayesian_update.py` — Bayesian learning updates
- `learning/evidence_accumulation.py` — evidence accumulation
- `learning/update_proposals.py` — proposed belief updates
- `template_computations/` — domain-specific computations (circadian, social, thermal, visual)

### 2.6 Paper Integration (7 files) — `src/services/paper_integration/`

The paper ingestion pipeline:
- `orchestrator.py` — orchestrates full paper integration
- `molecule_linker.py` — links paper findings to molecular-level claims
- `rollback.py` — safe rollback of failed integrations
- `supersession.py` — handles paper supersession logic
- `tag_engine.py` — tag management

### 2.7 Extraction Pipeline (25 files) — `src/extraction/`

From raw papers to structured claims:
- `llm_extraction_service.py` — LLM-based extraction
- `batch_extract.py`, `batch_processor.py` — batch processing
- `claim_extractor.py` — claim extraction
- `paper_triage.py`, `paper_triage_ag.py` — paper triage (AG's version)
- `pipeline_repairs.py` — pipeline self-repair
- `table_classifier.py`, `table_semantics_codex.py` — table extraction
- `effect_size_converter.py` — effect size normalization
- `evidence_risk.py` — evidence risk assessment

### 2.8 Agents (7 files) — `src/agents/`

- `agent_core.py` — base agent infrastructure
- `agent_panels_v2.py` — panel-based multi-agent deliberation
- `agent_aggregator.py` — agent output aggregation
- `bbn_calibrator.py` — BBN calibration agent
- `grounded_expert_agent.py` (in services) — grounded expert reasoning

### 2.9 Theory Profiles (13 files) — `src/theories/`

Theory-specific profiles (biophilia, predictive processing, embodied cognition, etc.):
- `theory_agent_council.py` — multi-theory deliberation
- `learning_agent.py` — theory learning agent
- 11 domain-specific profiles (biophilia, CB, DP, DT, EC, IC, MS, MSI, NM, PP, SN)

### 2.10 Application Layer

**API Routes** (20 files) — `app/routes/`
- `health.py` — **KEY FILE**: HTTP health endpoint
- `web_of_belief.py` — WoB API routes
- `entrenchment.py` — entrenchment API
- `graph.py` — graph query API

**App Core** (24 files) — `app/`
- `main.py` — application entry point
- `worker.py`, `worker_complete.py` — background workers
- `websocket.py` — real-time updates

**Streamlit Dashboard** (27 files) — `streamlit_app/`
- `pages/8_system_health.py` — **KEY FILE**: health dashboard page
- `pages/0_corpus_stats.py` — corpus statistics
- `pages/7_attack_review.py` — adversarial review interface

### 2.11 Tests (211 files) — `tests/`

Comprehensive test suite including:
- `test_web_of_belief.py` — web service tests
- `test_web_of_belief_invariants.py` — **KEY**: invariant tests (formula invariants?)
- `test_web_of_belief_health_baseline_runner.py` — health baseline tests
- `test_web_of_belief_mutation_safeguards.py` — mutation safety tests
- `test_bridge_warrants.py`, `test_bridge_ceilings.py` — bridge/ceiling tests
- `test_bn_health.py` — BN health tests
- `test_scalable_coherence.py` — coherence tests
- `test_compute_system_health.py` — system health tests

---

## 3. THE OVERSEER COLLECTION

The overseer is the governance layer that monitors system health. It consists of:

### 3.1 The Core Overseer

| File | Role |
|------|------|
| `src/services/overseer.py` | The overseer service — orchestrates all monitoring |
| `scripts/overseer_nightly.py` | Nightly overseer run (scheduled health checks) |
| `scripts/maintenance.py` | General maintenance tasks |

### 3.2 Health Check Scripts (Tiered by Scope)

**Tier A: Full System Health**

| Script | Scope |
|--------|-------|
| `scripts/compute_system_health.py` | Aggregate system health score |
| `scripts/full_web_health_test.py` | Comprehensive web + BN health |
| `scripts/run_all_checks.py` | Run all validation checks |
| `scripts/sanity_check.py` | Quick sanity check |

**Tier B: Web-Specific Health**

| Script | Scope |
|--------|-------|
| `scripts/check_web_bn_health.py` | Web ↔ BN alignment |
| `scripts/analyze_web_health.py` | Web health analysis |
| `scripts/probe_web_of_belief_health.py` | Deep web health probe |
| `scripts/run_web_of_belief_health_baseline.py` | Baseline health metrics |
| `scripts/web_health_diagnostic.py` | Diagnostic report |

**Tier C: Specific Validators**

| Script | Scope |
|--------|-------|
| `scripts/corpus_health_report.py` | AG's corpus-level report (the one already run) |
| `scripts/validate_all_templates.py` | All template validation |
| `scripts/validate_templates.py` | Individual template validation |
| `scripts/validate_toulmin.py` | Toulmin argument structure validation |
| `scripts/audit_template_compliance.py` | Template compliance audit |

**Tier D: Ceiling & Bridge Linters**

| Script | Scope |
|--------|-------|
| `scripts/lint_bridge_ceilings.py` | Bridge warrant ceiling violations |
| `scripts/lint_ceilings.py` | General ceiling violations |
| `scripts/ceiling_adjudicator.py` | Adjudicates ceiling disputes |

**Tier E: Repair & Improvement**

| Script | Scope |
|--------|-------|
| `scripts/improve_web_health.py` | Automated health improvement |
| `scripts/safe_improve_web_health.py` | Safe (conservative) health improvement |
| `scripts/repair_templates.py` | Template repair |
| `scripts/repair_interactions.py` | Interaction repair |
| `scripts/fix_validation_errors.py` | Validation error repair |
| `scripts/bn_unresolved_repair.py` | BN unresolved node repair |
| `scripts/break_bn_cycles.py` | BN cycle breaking |
| `scripts/remove_bn_cycles.py` | BN cycle removal |
| `scripts/maintain_bn.py` | BN maintenance |
| `scripts/maintain_web.py` | Web maintenance |
| `scripts/rebuild_web_db.py` | Full web database rebuild |
| `scripts/force_bn_rebuild.py` | Force BN rebuild |

**Tier F: Quarantined (Deprecated/Risky)**

| Script | Scope |
|--------|-------|
| `scripts/quarantine/apply_ceiling_decisions.py` | Quarantined ceiling application |
| `scripts/quarantine/auto_cap_ceilings.py` | Quarantined auto-capping |
| `scripts/quarantine/repair_bridge_ceilings.py` | Quarantined bridge ceiling repair |
| `scripts/quarantine/repair_bridge_ceilings2.py` | Quarantined bridge ceiling repair v2 |

### 3.3 Epistemic Monitors (In-Process)

| File | Role |
|------|------|
| `src/epistemic/monitors/coherence_audit.py` | Runtime coherence auditing |
| `src/epistemic/monitors/adversarial_review.py` | Adversarial review generation |
| `src/epistemic/monitors/asymmetry_monitor.py` | Evidence asymmetry detection |
| `src/epistemic/monitors/bias_detection.py` | Systematic bias detection |
| `src/epistemic/monitors/cross_type_coherence.py` | Cross-warrant-type coherence |
| `src/epistemic/monitors/theory_monitor.py` | Theory-level monitoring |

### 3.4 Dashboard

| File | Role |
|------|------|
| `app/routes/health.py` | HTTP health API |
| `streamlit_app/pages/8_system_health.py` | Visual health dashboard |

---

## 4. IMPLEMENTATION STATUS: WEB AND BN

### 4.1 Web of Belief — FULLY BUILT

The web of belief is implemented across 20+ dedicated files with:
- Typed graph model (`graph_models.py`)
- 7-type warrant hierarchy (`enums.py`)
- Coherence engine (`coherence.py`, `scalable_coherence.py`)
- Entrenchment ranking (`entrenchment.py`)
- Reflective equilibrium (`equilibrium.py`)
- Evidence updating (`evidence_updates.py`)
- Independence testing (`independence.py`)
- Severity testing (`severity.py`)
- State management and snapshots (`web_state.py`, `snapshots.py`)
- Mutation control (`mutations.py`)
- Full persistence (`web_persistence.py`)

### 4.2 Bayesian Network — FULLY BUILT

The BN layer is implemented via:
- `bn_edges.py`, `bn_nodes.py` — graph primitives
- `incremental_bn.py` — incremental BN updates
- `bbn_calibrator.py` — BBN calibration (agent + service versions)
- `bn_coherence_client.py` — BN-side coherence
- `graph_confidence_service.py` — confidence propagation

### 4.3 The Bridge (π function) — FULLY BUILT

The EWG→BN projection:
- `epistemic_causal_bridge.py` — the main bridge service
- `ecb_modules/causal_models.py` — causal model translation
- `ecb_modules/contrast_classes.py` — contrastive reasoning
- `ecb_modules/counterfactuals.py` — counterfactual reasoning
- `bridge_warrants.py` — bridge warrant assignment
- `warrant_scaling.py` — ceiling enforcement
- `web_template_bridge.py` — template↔web bridge

### 4.4 Dual Architecture — CONFIRMED

`dual_epistemology.py` confirms the system implements the dual-layer architecture described in the master document: the web of belief as the primary epistemic structure, and the BN as a derivative computational layer.

---

## 5. DIAGNOSES AND REPAIR PLAN

Three sources of diagnostic information:

| Source | Findings |
|--------|----------|
| AG's `corpus_health_report.py` | 100 missing confidence values, 103 missing bridge warrants, 40 unclassified templates, 1 ceiling violation |
| Our health audit (this session) | ALL 7 worked examples violate the multiplicative credence formula (30-80% overstatement). 6 of 7 have bridge values above ceiling. |
| Expert panel (this session) | Multiplicative formula is not operational. Weighted additive (0.50/0.30/0.20) fits actual data. |

### 5.1 PHASE 1: Immediate — Ceiling & Formula Alignment (AG should run)

**Step 1.1**: Run the existing ceiling linters to establish baseline
```
python scripts/lint_bridge_ceilings.py
python scripts/lint_ceilings.py
```
These will report all ceiling violations in the live database, not just the 7 worked examples in the master doc. The quarantined scripts (`quarantine/repair_bridge_ceilings.py` etc.) exist because earlier automated ceiling repairs were problematic — proceed with `ceiling_adjudicator.py` which presumably has human-in-the-loop review.

**Step 1.2**: Run the full web-BN health check
```
python scripts/check_web_bn_health.py
```
This checks alignment between the web and BN layers. Any misalignment here may compound the formula issue.

**Step 1.3**: Run template validation
```
python scripts/validate_all_templates.py
python scripts/validate_toulmin.py
```
The 40 unclassified templates AG found need classification before ceiling enforcement can be applied uniformly.

**Step 1.4**: Examine the formula implementation
The credence formula lives in one (or more) of these files:
- `src/cmr/worked_examples.py` — the worked example computations
- `src/services/graph_confidence_service.py` — confidence propagation
- `src/epistemic/warrant_scaling.py` — warrant ceiling scaling
- `src/services/bridge_warrants.py` — bridge warrant logic

AG needs to check: **Is the code actually using the multiplicative formula, or has the code already been doing weighted additive (or holistic) computation while the documentation says multiplicative?** This is the central diagnostic question. If the code matches the documentation (multiplicative), then the formula divergence is happening at the expert-judgment stage before data entry. If the code is already doing something else, the documentation needs to catch up.

### 5.2 PHASE 2: Serialization Gap Closure

AG's health report found 100 missing confidence values and 103 missing bridge warrants. The catalog confirms the relevant serialization infrastructure exists:

- `scripts/enrich_template_json_fields.py` — enriches JSON template data
- `scripts/extract_panel_json.py` — extracts panel data to JSON
- `src/data/template_loader.py` — template loading from JSON/DB

**Step 2.1**: Identify which templates lack JSON serialization
```
python scripts/corpus_health_report.py --verbose
```
(Re-run with verbose output to get per-template breakdown)

**Step 2.2**: Run enrichment
```
python scripts/enrich_template_json_fields.py
```
This should backfill missing confidence and bridge warrant fields from the master document into JSON.

**Step 2.3**: Validate the results
```
python scripts/validate_all_templates.py
```

### 5.3 PHASE 3: Formula Decision and Implementation

Based on the panel recommendation, one of three paths:

**Path A (Conservative)**: Keep multiplicative formula but recompute all worked examples so that stated composites match P(parent) × P(bridge) × P(CNFA). This means the composites go DOWN. VIEW1 goes from 0.55 to 0.416.

**Path B (Revisionist)**: Adopt weighted additive formula: Composite = 0.50 × P(parent) + 0.30 × P(bridge) + 0.20 × P(CNFA). This preserves current composite values approximately. Requires updating:
- `src/cmr/worked_examples.py`
- `src/services/graph_confidence_service.py`
- The master document §3.1 and all worked examples
- build_doc.js §3.1, §4

**Path C (Panel-recommended)**: Weighted additive baseline + coherence adjustment (±0.05), with explicit documentation that composites reflect holistic assessment. This requires:
- All Path B changes
- Addition of a coherence adjustment step in the computation pipeline
- Documentation of deviation justification

**David needs to make this decision.** The panel recommended Path C.

### 5.4 PHASE 4: Full Health Baseline

After formula/ceiling/serialization fixes:
```
python scripts/run_web_of_belief_health_baseline.py
python scripts/compute_system_health.py
python scripts/full_web_health_test.py
```
This establishes a post-repair baseline.

### 5.5 PHASE 5: Nightly Oversight Activation

Ensure the nightly overseer is running:
```
python scripts/overseer_nightly.py --dry-run
```
The overseer should be checking:
1. No new ceiling violations
2. Formula consistency (composite = weighted sum ± coherence adjustment)
3. All templates have confidence, bridge warrant, and classification
4. Web↔BN alignment holds
5. No orphaned beliefs or cycles

### 5.6 PHASE 6: Code Renaming (Lower Priority)

The codebase still has a `src/cmr/` directory and many `test_cmr_*.py` files. These should eventually be renamed to `src/atlas/` and `test_atlas_*.py` to match the documentation rename. But this is cosmetic relative to the health issues.

---

## 6. KEY FILES AG SHOULD UPLOAD FOR DEEP ANALYSIS

To produce a truly precise repair plan — not inference from filenames but analysis of actual logic — the following files would be most valuable:

**Priority 1 (Formula & Ceilings)**:
1. `src/cmr/worked_examples.py` — how the formula is actually computed
2. `src/epistemic/warrant_scaling.py` — how ceilings are enforced
3. `src/services/bridge_warrants.py` — bridge warrant logic
4. `src/services/graph_confidence_service.py` — confidence propagation

**Priority 2 (Overseer & Health)**:
5. `src/services/overseer.py` — the overseer's governance logic
6. `scripts/overseer_nightly.py` — what the nightly run checks
7. `scripts/check_web_bn_health.py` — web↔BN health check logic
8. `scripts/corpus_health_report.py` — AG's original health report (what exactly it checks)
9. `scripts/lint_bridge_ceilings.py` — ceiling linting logic

**Priority 3 (Web Core)**:
10. `src/services/web_of_belief_components/enums.py` — the actual warrant type enum (does it have all 7 types?)
11. `src/services/web_of_belief_modules/coherence.py` — coherence computation
12. `src/services/web_of_belief_modules/independence.py` — independence testing (relevant to the panel's finding that factors are correlated)

---

## 7. SUMMARY OF THE STATE OF PLAY

The system is architecturally complete and impressively built. 875 files, dual-layer epistemic architecture, full extraction pipeline, multi-agent deliberation, Streamlit dashboard, comprehensive test suite. This is not a prototype — it is a production system.

The health issues are real but bounded:
1. **The formula discrepancy** is the most theoretically important finding. It requires a decision from David about which formula to canonize.
2. **The serialization gap** (100 missing confidence, 103 missing bridge warrants) is an infrastructure issue with existing tooling to fix it.
3. **The ceiling violations** need to be resolved either by clamping values or revising ceilings.
4. **The 40 unclassified templates** need warrant type assignment.

None of these threaten the architecture. They are calibration and consistency issues within a fundamentally sound system.

---

*Generated: February 26, 2026*
*Sources: python_source_catalog.md (AG, auto-generated 2026-02-26 09:00 UTC), Panel_Review_Credence_Formula.md (this session), ATLAS_Health_Audit_Feb26.txt (this session)*
