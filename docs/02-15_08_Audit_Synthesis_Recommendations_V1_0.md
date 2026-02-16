# §7 CRITICAL RECOMMENDATIONS
## Synthesized from Opus Template Audit + Codex Codebase Audit
## February 15, 2026 — Version 1.0

---

# EXECUTIVE SUMMARY

Two independent audits converge on the same conclusion: **the theory tier cannot be
built on top of the current codebase without first resolving 5 blocking issues.**
The good news: the epistemic tier (web of belief, coherence engine, gap detection,
bridge warrants) is substantially built and working. The theory tier (templates,
frameworks, CMR pipeline) is 0-15% implemented — mostly docs.

**Decision count**: David needs to make 8 decisions before CC starts Sprint 0.
Most are naming choices. Two require theoretical judgment.

---

# TOP 5 FIXES BEFORE STARTING SPRINTS

## Fix 1: Broken Tests (BLOCKS EVERYTHING)

**Finding** (Codex §1): 12 test files have collection errors. Tests cannot run.
96 test files exist but the suite is broken.

**Action**: Sprint 0 Task 0.0 (NEW): Fix test collection errors before anything else.
CC can do this autonomously — it's import errors, not theoretical decisions.

**Why it blocks**: Sprint 9 (Pipeline Health) is meaningless without working tests.
Sprint 0-5 need regression testing. Can't merge anything safely without green CI.

## Fix 2: GapType Enum Collision (BLOCKS Sprint 6)

**Finding** (Codex §5.1, §2.3, Top 25 Collision #2): Three competing GapType
taxonomies exist:

| Location | Values |
|----------|--------|
| `gap_predictor.py:38` | MEDIATION, MECHANISM, BOUNDARY, DIRECTION, INTERACTION, VALIDATION, UNJUSTIFIED_EDGE, CRITICAL_QUESTION, ARGUMENT_ATTACK |
| `voi_search.py:254` | uncertain, unexplored, conflicting, (+ others) |
| `discovery_funnel.py:43` | missing_evidence, weak_support, (+ others) |

**DECISION NEEDED** (David): Which taxonomy is canonical?

**Recommendation**: Keep `gap_predictor.py`'s 8-value enum as canonical. It's the
most granular and maps cleanly to the queue prioritization panel's gap weights.
The VOI and discovery funnel services should import this enum, not define their own.
Last two values (CRITICAL_QUESTION, ARGUMENT_ATTACK) need stub implementations
to prevent runtime errors.

## Fix 3: Template ID Canonicalization (BLOCKS Sprint 7)

**Finding** (Codex §2.3, Opus §4): Two ID problems:

1. **Long vs short names**: The body of CMR V2.0 uses long IDs
   (e.g., `IC_INTEROCEPTIVE_AFFECT_CONSTRUCTION_001`) while the summary table
   uses short IDs (`IC_INTEROCEPTIVE_AFFECT_001`). Opus's seed encodings used
   the short forms.

2. **Template 31 collision**: Panel II proposed T31 as olfactory; Panel III
   finalized it as auditory (`AUD_SCENE_ANALYSIS_001`). The olfactory template
   became T35.

**DECISION NEEDED** (David): Which ID form is canonical — long or short?

**Recommendation**: Use the **summary table short forms** as canonical IDs.
They're what the seed encodings use. Create an alias map for the long forms.
For T31, the Panel III assignment (auditory) is final.

## Fix 4: Tier 1 Framework Count (BLOCKS Sprint 7 Task 7.3)

**Finding** (Codex §2.3): Three different counts exist in docs:

| Source | Count | Frameworks |
|--------|-------|-----------|
| Sprint Plan / `theory_bootstrap.py` | 8 | PP, SN, DP, DT, NM, IC, MS, EC |
| Panel II | 9 | + Chronobiological (CB) |
| Panel III | 10 | + Multisensory Integration (MSI) |

**DECISION NEEDED** (David): How many Tier 1 frameworks does the system launch with?

**Recommendation**: **10 frameworks**. The panels recommended both promotions and
the template library already has templates for both CB and MSI. The code in
`theory_bootstrap.py` currently seeds 8 — CC should update to 10.
My Sprint 7 Theory Artifacts (document 07) already provides scope declarations
for all 10.

## Fix 5: Pathway Taxonomy (BLOCKS Sprint 4b)

**Finding** (Codex §2.3, Top 25 Collision #3): Two competing taxonomies:

| Location | Values |
|----------|--------|
| `pathway_classifier.py:5`, `web_of_belief.py:257` | SUBPERSONAL, PERSONAL_EPISTEMIC, MIXED |
| `CLAUDE.md:53`, `IMPLEMENTATION_TASKS.md:1129` | EXPLICIT, IMPLICIT_COGNITIVE, IMPLICIT_PHYSIOLOGICAL, MIXED |

**DECISION NEEDED** (David): Which taxonomy?

**Recommendation**: Keep **SUBPERSONAL / PERSONAL_EPISTEMIC / MIXED** — it's what's
actually implemented in code. It's also more theoretically defensible (it's a
mechanism-level distinction, not a phenomenological one). Update CLAUDE.md and
IMPLEMENTATION_TASKS.md to match.

---

# 3 ADDITIONAL DECISIONS NEEDED

## Decision 6: Causal Chain Endpoint Naming (Collision #7)

Two naming conventions for template chain endpoints:
- My seed encodings (document 07): `from_variable` / `to_variable`
- BN_graphical + Outcome_Contractor: `antecedent` / `consequent` / `mediators`

**Recommendation**: Use `from_variable` / `to_variable` in the template data
structures (they're describing a causal link direction, not a logical relation).
Use `antecedent` / `consequent` / `mediators` only in the BN bridge layer
where the logical interpretation matters. Add adapter.

## Decision 7: Confidence/Quality Stack (Collision #16)

Four overlapping confidence fields exist: `ae_confidence`, `extraction_confidence`,
`mechanism_confidence`, `evidence_strength`.

**Recommendation**: Make these **four explicitly separate dimensions**:
- `extraction_confidence`: How well did the AI extract this from the paper?
- `statistical_confidence`: p-value, CI, effect size — the paper's own numbers
- `mechanism_confidence`: Bridging quality + maturity from template chain
- `epistemic_confidence`: Entrenchment in web of belief (emergent, not assigned)

Each is independent. Never average them into one score.

## Decision 8: Epistemic Certainty Model (Collision #1 — Highest Risk)

Codex's #1 collision: `credence/entrenchment` (AE) vs `rank/neg_rank/warrant_status`
(BN_graphical bridge). "Semantic inversion risk in bridge math."

**Recommendation**: The ARCH-4 model (rank-based) is the more recent design.
Make it canonical in bridge payloads. Keep `credence` as a read-only legacy
adapter inside AE. This is Codex's recommendation too — I agree.

---

# RECONCILED VARIABLE VOCABULARY FOR THEORY TIER

This section resolves the `# AUDIT-CHECK` markers from my Sprint 7 Theory
Artifacts (document 07) against what Codex found in the codebase.

## Framework Scope Variables — Reconciled Names

In document 07, I provisionally named variables in the framework scope declarations.
Here's what they should actually be, reconciled against existing code:

### Variables that ALREADY EXIST in code (use as-is):

| My Provisional Name | Actual Code Name | Location | Action |
|---------------------|-----------------|----------|--------|
| `cortisol_level` | `cortisol` | Not in code as variable; referenced in free text | **CREATE**: `cortisol_level` as new controlled vocab entry |
| `hpa_axis_activation` | `hpa_axis_activation` | Referenced in specs but not as enum/field | **CREATE** |
| `effect_size` | `effect_size` | 4 repos, 44 sources | **USE AS-IS** |
| `p_value` | `p_value` | 4 repos, 32 sources | **USE AS-IS** |
| `boundary_conditions` | `boundary_conditions` | 4 repos, 10 sources | **USE AS-IS** |
| `claim_type` | `claim_type` | 3 repos, 12 sources | **USE AS-IS** |
| `ae_confidence` | `ae_confidence` | 3 repos, 25 sources | **USE AS-IS** (maps to `extraction_confidence` in new 4-layer model) |
| `coherence_score` | `coherence_score` | 2 repos, 4 sources | **USE AS-IS** |
| `cognitive_load` | `cognitive_load` | 2 repos, 3 sources | **USE AS-IS** |

### Variables that DON'T EXIST in code (theory tier creates them):

These are new — the theory tier introduces variables the epistemic tier doesn't have.
CC should create these as part of the `Tier1Framework.owned_variables` registry.

| Variable | Framework | Notes |
|----------|-----------|-------|
| `prediction_error_magnitude` | PP | Core PP variable. No existing code equivalent. |
| `precision_weighting` | PP | No code equivalent. |
| `cognitive_map_quality` | SN | No code equivalent. |
| `place_cell_stability` | SN | Neural measure, not in extraction pipeline. |
| `theta_sequence_coherence` | SN | Neural measure. |
| `directed_attention_fatigue` | DT | Conceptual variable, not coded. |
| `dmn_engagement_level` | DT | Neural measure. |
| `explore_exploit_state` | NM | Behavioral state variable. |
| `allostatic_load` | NM | Systems-level measure. |
| `interoceptive_prediction_error` | IC | Core IC variable. |
| `interoceptive_sensitivity` | IC | Individual difference moderator. |
| `affordance_perception` | EC | Ecological psychology variable. |
| `postural_state` | EC | Behavioral measure. |
| `circadian_phase` | CB | Chronobiological variable. |
| `scn_entrainment_quality` | CB | Neural measure. |
| `crossmodal_congruency` | MSI | Core MSI variable. |
| `inverse_effectiveness_factor` | MSI | Quantitative parameter. |
| `stimulus_complexity` | PP (Goldilocks) | Domain-general dimension. |
| `cultural_visual_ecology_density` | PP (Cultural) | India fieldwork variable. |

### Variables with NAMING CONFLICTS to resolve:

| My Name | Code Name | Conflict | Resolution |
|---------|-----------|----------|------------|
| `environmental_threat_cues` | (no code equivalent) | But `environment_factors` exists (4 repos) | **Keep both**: `environment_factors` is the extraction-level field; `environmental_threat_cues` is the template-level theoretical variable that gets populated from `environment_factors` during CMR tracing |
| `spatial_layout_properties` | (no code equivalent) | But `environment_type` exists | Same pattern: extraction field vs theoretical variable |
| `environmental_legibility` | (no code equivalent) | Might overlap with SN `spatial_layout_legibility` | **Merge**: use `environmental_legibility` as EC's name, note it overlaps with SN. The independence matrix already scores EC↔SN at 0.5 |

### Template-Internal Variables (Don't Need Reconciliation):

These are variables internal to causal chains — they don't appear in the
extraction pipeline or web of belief. They exist only inside MechanisticTemplate
objects. No naming conflict possible because they're new:

`amygdala_activation`, `hippocampal_entorhinal_sampling`, `tpn_deactivation`,
`dmn_reengagement`, `asa_parsing_demand`, `cortical_processing_load`,
`retinal_light_input`, `scn_activation`, `generative_model_calibration`,
`shifted_prediction_error_function`, `interoceptive_signal_change`,
`constructed_affect`, `subsystem_maintenance_operations`

---

# REVISED SPRINT PLAN RECOMMENDATIONS

Based on both audits, the sprint plan needs these modifications:

## Sprint 0: Add Task 0.0 — Fix Test Suite

**Before** the existing Sprint 0 tasks, CC must fix the 12 test collection errors.
Without this, nothing downstream can be regression-tested.

**Estimated**: 2-4 hours (import errors, naming conflicts with Test* enums)

## Sprint 6: Reconcile GapType Before Implementing

Sprint 6 Task 6.1 (ResearchTarget model) CANNOT proceed until the GapType
collision is resolved. Add a pre-task:

**Task 6.0 (NEW)**: Unify GapType enum. Create single canonical `src/epistemic/gap_types.py`,
import in `gap_predictor.py`, `voi_search.py`, `discovery_funnel.py`. Add stub
implementations for `find_critical_question_gaps()` and `find_argument_attack_gaps()`.

## Sprint 7: Use Document 07 Directly

My Sprint 7 Theory Artifacts (document 07) provide everything CC needs:
- Framework scope declarations → Task 7.3 (Tier1Framework model)
- Independence matrix → Task 7.4
- Seed template encodings → Task 7.5
- Data class definitions → schema for MechanisticTemplate + CausalLink

**Key change**: Update `theory_bootstrap.py` from 8 to 10 frameworks (add CB, MSI).

## Sprint 7 Task 7.5: Template ID Alias Map

CC should create a `template_id_aliases.json` that maps:
- Long form → short form (e.g., `IC_INTEROCEPTIVE_AFFECT_CONSTRUCTION_001` → `IC_INTEROCEPTIVE_AFFECT_001`)
- Panel II proposed IDs → Panel III final IDs (T31 collision)

This lets the CMR pipeline look up templates by either form.

## Sprint Ordering: Revised Critical Path

```
0.0 (fix tests) → 0 → 1 → 2 → 3 → 5 → 9     (epistemic core)
                   1 → 6.0 (GapType) → 6         (queue, after reconciliation)
                   1 → 7 → 8                      (theory + CMR)
                   1 → 4/4b → 5                   (extraction)
```

**New dependency**: Sprint 6 now depends on GapType reconciliation (Task 6.0).
Sprint 7 depends on David's 8 decisions above (mostly naming).

## Path Conventions

Codex found that the sprint plan references paths that don't exist:
- `src/queue/*` → should be `src/services/queue/` or new package
- `src/theory/*` → should be `src/theories/` (already exists) + `src/theory/` (new for templates)
- `src/cmr/*` → new, to be created

CC should create these directories in Sprint 0, even if empty, so the path
structure matches the sprint plan.

---

# TEMPLATES 31-40: GAP ANALYSIS

Both audits agree: Templates 31-40 have quantitative parameters but lack
structured link-level bridging quality, maturity, and evidence citations.

**Opus's assessment** (document 06): 6 of 10 are "MOSTLY" ready, needing minor
filling; the params are excellent (especially T31, T34, T35, T36).

**Codex's assessment** (§4): 0/10 "fully specified" by strict criteria (missing
bridging quality per link and link-level evidence).

**Resolution**: The information IS in the Panel III document — it just wasn't
structured in the same rigid format as Templates 1-30. My seed encoding of T31
(in document 07) demonstrates how to upgrade a Panel III template to full
specification. CC can follow this pattern for T32-T40 using the Panel III
document as source. This is mechanical work, not theoretical judgment —
the bridging qualities and evidence are stated in the prose.

---

# WHAT'S READY NOW vs. WHAT'S WAITING

| Artifact | Status | Waiting On |
|----------|--------|-----------|
| Framework scope declarations (10 frameworks) | **READY** (doc 07 §1) | Nothing |
| Independence matrix | **READY** (doc 07 §2) | Nothing |
| 8 seed template encodings | **READY** (doc 07 §3) | Variable name reconciliation (this document resolves it) |
| Prediction generation grammar | **READY** (doc 06 Part 2) | Nothing |
| Cross-framework bridging rules | **READY** (doc 06 Part 3) | Nothing |
| Remaining 32 template encodings | CC can produce mechanically | David's 8 decisions + T31-40 need link-level filling |
| Controlled variable vocabulary | **READY** (this document) | David confirms naming decisions |
| GapType reconciliation | **SPECIFIED** (this document) | David confirms canonical enum |
| Sprint 0 test fixes | CC can do autonomously | Nothing |

**Bottom line**: Once David makes the 8 decisions, CC can begin Sprint 0 immediately
with a complete theory reference shelf: documents 06, 07, and this document (08).
