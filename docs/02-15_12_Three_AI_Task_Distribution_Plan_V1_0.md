# THREE-AI TASK DISTRIBUTION PLAN
## Article Eater — Sprint Execution
## February 15, 2026

---

# AI CAPABILITIES

| AI | Strengths | Weaknesses | Repo Access |
|---|---|---|---|
| **Claude Code** | Complex new modules, system wiring, refactoring, multi-file changes, test writing | Slower on mechanical repetition | Article Eater (primary) |
| **Codex** | Cross-repo analysis, schema validation, migration scripts, contract enforcement, diffing | No runtime execution, can't test | All 5 repos |
| **Antigravity** | Bounded mechanical tasks, file editing, data extraction, reliable on clear specs | Needs very precise instructions | Article Eater |

---

# SPRINT 0: FOUNDATION (Current)

| Task | Assigned To | Status | Notes |
|---|---|---|---|
| 0.0 Fix test suite | **Antigravity** | ✅ DONE | 2578 passing, 1 failure (theory registry seed) |
| 0.1 Create directory structure | **CC** | ASSIGNED | `src/queue/`, `src/theory/`, `src/cmr/` |
| 0.2 GapType reconciliation | **CC** | ASSIGNED | New canonical enum, update 3 services |
| 0.3 Update framework bootstrap to 10 | **CC** | ASSIGNED | Add CB, MSI to theory_bootstrap.py |
| 0.4 Update stale docs | **Antigravity** | ASSIGNED | CLAUDE.md + IMPLEMENTATION_TASKS.md pathway/tier fixes |
| 0.5 Template ID alias map | **Antigravity** | ASSIGNED | template_id_aliases.json from panel docs |
| 0.6 Cross-repo vocab contract | **Codex** | ✅ DONE | canonical_enums.json + check_enum_drift.py |
| 0.7 Migration backlog from drift checker | **Codex** | NEXT | See below |

### Codex Next Task: Migration Scripts

```
TASK: Write migration adapter scripts for the top 5 collisions.

You created canonical_enums.json and check_enum_drift.py. Now create the
actual migration code:

1. scripts/migrate_gap_type.py
   - Reads gap_predictor.py, voi_search.py, discovery_funnel.py
   - Outputs a patch that replaces local enum definitions with imports
     from the canonical location
   - CC will review and apply the patch

2. scripts/migrate_ci_shape.py
   - Scans all 5 repos for ci_lower/ci_upper scalar pairs and
     confidence_interval object usage
   - Outputs a report: which files use which shape, with line numbers
   - Proposes adapter functions for each boundary

3. scripts/migrate_claim_type.py
   - Maps BN_graphical's internal ClaimType enum values to AE canonical
   - Outputs adapter code for the BN→AE bridge

4. scripts/migrate_evidence_type.py
   - Same pattern for EvidenceType across BN_graphical, Tagging, AF

5. scripts/migrate_article_type.py
   - Implements the crosswalk table from canonical_enums.json
   - Outputs adapter for AE TemplateFamily ↔ Outcome ArticleType

For each script:
- Input: canonical_enums.json + current repo source files
- Output: either a patch file or adapter module
- Do NOT apply changes directly — output for CC review
- Include a test function that validates the migration is lossless

Reference: docs/02-15_09_Canonical_Decisions_Record_V1_0.md for all decisions.
```

---

# SPRINT 1-3: EPISTEMIC CORE

These sprints build/extend the web of belief. Mostly CC territory with
Codex handling cross-repo contract validation.

| Sprint | Task | Assigned To | Dependency |
|---|---|---|---|
| **1** | 1.1 Claim node extensions (argument_scheme, critical_questions) | **CC** | Sprint 0 complete |
| **1** | 1.2 Edge type consolidation (ConstraintType + EdgeType → one enum) | **CC** | Decision Record collision #18 |
| **1** | 1.3 Node type consolidation (NodeDomain + NodeTypeFamily → one) | **CC** | Decision Record collision #19 |
| **1** | 1.4 Validate cross-repo contract compliance after enum changes | **Codex** | CC finishes 1.2-1.3 |
| **2** | 2.1 Bayesian network: add d-separation, conditional queries | **CC** | Sprint 1 |
| **2** | 2.2 Schema migration: add new fields to SQLAlchemy models | **CC** | Sprint 1 |
| **3** | 3.1 Coherence engine upgrade (scalable_coherence.py) | **CC** | Sprint 2 |
| **3** | 3.2 Bridge warrant service extensions | **CC** | Sprint 2 |
| **3** | 3.3 Run check_enum_drift.py, report any new drift | **Codex** | Periodic check |

---

# SPRINT 4/4b: EXTRACTION PIPELINE

| Sprint | Task | Assigned To | Notes |
|---|---|---|---|
| **4** | 4.1 Extraction pipeline extensions (argument_scheme, CQ fields) | **CC** | New extraction fields |
| **4** | 4.2 Source quality scoring refinement | **CC** | |
| **4b** | 4b.1 Method registry implementation | **CC** | |
| **4b** | 4b.2 Ecological validity scoring | **CC** | Uses method registry |
| **4b** | 4b.3 Extract method metadata from 7 existing finding files | **Antigravity** | Mechanical: read each JSONL, add study_design field |
| **4b** | 4b.4 Validate extraction output against canonical schemas | **Codex** | Cross-repo schema check |

---

# SPRINT 5: INTEGRATION

| Task | Assigned To | Notes |
|---|---|---|
| 5.1 Wire extraction → web of belief → BN pipeline | **CC** | Complex system integration |
| 5.2 End-to-end pipeline test (paper in → beliefs out) | **CC** | |
| 5.3 Cross-repo contract compliance for full pipeline | **Codex** | Final pre-theory-tier validation |

---

# SPRINT 6: RESEARCH QUEUE

| Task | Assigned To | Notes |
|---|---|---|
| 6.1 ResearchTarget model (with canonical GapType) | **CC** | Contract exists, no implementation |
| 6.2 ResearchQueueService implementation | **CC** | |
| 6.3 VOI scoring integration (using canonical GapType) | **CC** | |
| 6.4 Queue prioritization panel weights | **Antigravity** | Mechanical: encode panel weights from docs into config |

---

# SPRINT 7: THEORY TIER ← CRITICAL

This is where the Opus theory documents get encoded. Heavy CC sprint,
with Antigravity handling mechanical template encoding.

| Task | Assigned To | Source Document | Notes |
|---|---|---|---|
| 7.1 Tier1Framework model in DB | **CC** | doc 07 §1 | 10 frameworks with scope declarations |
| 7.2 Independence matrix in DB | **CC** | doc 07 §2 | 10×10 symmetric matrix |
| 7.3 MechanisticTemplate + CausalLink models in DB | **CC** | doc 07 §3 preamble | Dataclass definitions → SQLAlchemy |
| 7.4 Encode 12 seed templates | **CC** | docs 07 + 10 | The 12 seeds I wrote — CC validates and loads |
| 7.5 Encode remaining 28 templates (T1-T40 minus seeds) | **Antigravity** | Panel docs I-III | Mechanical: follow seed pattern, fill from panel docs |
| 7.6 Template ID alias map integration | **Antigravity** | template_id_aliases.json | Already building this |
| 7.7 Cross-framework bridging rules in DB | **CC** | doc 06 Part 3 | Bridge catalog → queryable table |
| 7.8 Validate all 40 templates load and cross-reference correctly | **Codex** | All template docs | Schema validation, FK integrity |

### Antigravity Instructions for Task 7.5

```
TASK: Encode remaining 28 templates into the same Python format as the
12 seed templates in docs 07 and 10.

Source documents:
- docs/02-14_09_CMR_Revised_Spec_Panel_Templates_V2_0.md (Templates 1-20)
- docs/02-15_02_Neuroscience_Panel_Templates_and_Taxonomy_V1_0.md (Templates 21-30)
- docs/02-15_03_Panel_III_Multimodal_Senses_HigherCognition_V1_0.md (Templates 31-40)

Already encoded (SKIP these): T2, T3, T5, T8, T9, T12, T15, T25, T27, T29, T30, T31

Encode these 28: T1, T4, T6, T7, T10, T11, T13, T14, T16, T17, T18, T19, T20,
T21, T22, T23, T24, T26, T28, T32, T33, T34, T35, T36, T37, T38, T39, T40

For each template, follow EXACTLY the MechanisticTemplate dataclass pattern
from docs/02-15_07_Sprint7_Theory_Artifacts_V1_0.md Section 3.

Fill in ALL fields:
- template_id (use short canonical form per Decision 2)
- name, structural_pattern, higher_order_principle, transferable_to
- framework_ids
- causal_links (each with from_variable, to_variable, activity,
  from_level, to_level, bridging_quality, maturity, key_evidence, parameters)
- scope_conditions
- moderators
- interactions
- overall_maturity
- key_references

For Templates 31-40 (Panel III): the bridging quality and maturity ARE in the
prose even though Codex's audit said they're missing from "structured fields."
Read the narrative carefully — each link's maturity and quality are stated
in the text. Extract them.

Output: One Python file per batch of 7 templates. Four files total.
Name them: templates_batch_1.py through templates_batch_4.py
```

---

# SPRINT 8: CMR PIPELINE ← CRITICAL

Heaviest sprint. CC builds it, Antigravity helps with mechanical parts,
Codex validates contracts.

| Task | Assigned To | Source | Notes |
|---|---|---|---|
| 8.1 CMR data models (models.py) | **CC** | doc 11 Part 2 | All CMR-specific dataclasses |
| 8.2 Step 1: Causal Decomposition | **CC** | doc 11 Part 3 | LLM-based, needs prompt engineering |
| 8.3 Step 2: Framework Matching | **CC** | doc 11 Part 3 | Deterministic variable overlap |
| 8.4 Step 3: Mechanism Tracing (single-template) | **CC** | doc 11 Part 3 | MVP: one template per trace |
| 8.5 Step 4: Three core operations | **CC** | doc 11 Part 3 + doc 06 Part 2 | SUBSTITUTE, VARY_MOD, BLOCK |
| 8.6 Step 4: Remaining 7 operations | **Antigravity** | doc 06 Part 2 | Mechanical: follow pattern from first 3 |
| 8.7 Step 5: Convergence assessment | **CC** | doc 11 Part 3 | Uses independence matrix |
| 8.8 Step 6: Composition failure detection | **CC** | doc 11 Part 3 | Barrett's R10 |
| 8.9 Step 7: Prioritization | **CC** | doc 11 Part 3 | Weighted scoring |
| 8.10 Pipeline orchestrator + integration | **CC** | doc 11 Part 3 | Wire everything together |
| 8.11 Step 3 upgrade: multi-template composition | **CC** | doc 11 Part 3 | Uses bridging rules from doc 06 Part 3 |
| 8.12 Validate CMR output schema against web of belief | **Codex** | doc 11 Part 6 | DERIVED_HYPOTHESIS nodes |
| 8.13 End-to-end test: Ulrich 1984 worked example | **CC** | doc 11 Part 4 | Compare output to expected predictions |

---

# SPRINT 9: PIPELINE HEALTH

| Task | Assigned To | Notes |
|---|---|---|
| 9.1 Run full test suite, report coverage | **CC** | Depends on tests being green |
| 9.2 Cross-repo drift check (final) | **Codex** | Run check_enum_drift.py, report |
| 9.3 Pipeline expectation tests | **CC** | Verify extraction → web → CMR chain |
| 9.4 Performance profiling | **CC** | How long does CMR take per finding? |

---

# SUMMARY: WHO DOES WHAT

| AI | Sprint 0 | Sprint 1-3 | Sprint 4-5 | Sprint 6 | Sprint 7 | Sprint 8 | Sprint 9 |
|---|---|---|---|---|---|---|---|
| **CC** | 0.1-0.3 | All core code | All core code | All code | 7.1-7.4, 7.7 | 8.1-8.5, 8.7-8.11, 8.13 | 9.1, 9.3-9.4 |
| **Codex** | 0.6-0.7 | 1.4, periodic drift | 4b.4, 5.3 | — | 7.8 | 8.12 | 9.2 |
| **Antigravity** | 0.0✅, 0.4-0.5 | — | 4b.3 | 6.4 | 7.5-7.6 | 8.6 | — |
| **Opus** | Theory docs | Available for theory questions | Available | Available | Review templates | Review CMR output | — |

**CC**: ~70% of total work. All complex system code.
**Codex**: ~15%. Cross-repo validation, migration scripts, drift enforcement.
**Antigravity**: ~15%. Mechanical encoding, file editing, bounded tasks.
**Opus**: Theory referee. Called when CC/AG hit a theoretical judgment call.
