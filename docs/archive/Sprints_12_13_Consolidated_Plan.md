# SPRINTS 12–13 CONSOLIDATED EXECUTION PLAN
## Single Document for All Agents
## February 17, 2026

---

## READ THIS FIRST — ALL AGENTS

This document contains ALL tasks for Sprints 12 and 13 (38 tasks total). Every task is **pre-assigned to a specific agent**. There is no claiming system — your tasks are yours. Just do them in order, respecting dependencies.

### WHY NO MORE TASK_CLAIMS.md

The claiming system caused concurrency failures because multiple agents read the file simultaneously, both saw AVAILABLE, and both claimed the same task. We are eliminating this race condition by **pre-assigning every task**. You do not need to check TASK_CLAIMS.md. You do not need to claim anything. Find your agent name below, do your tasks in order, skip any task whose dependency isn't done yet (come back to it), and move on.

### HOW DEPENDENCIES WORK

Each task lists dependencies like "needs 12.1." If another agent owns 12.1, you need to know when they're done. Use this protocol:

1. When you FINISH a task, create or update the file `docs/DONE.md` by appending one line:
   ```
   12.1 DONE [CC] 2026-02-17T14:30
   ```
2. Before starting a task with a dependency, read `docs/DONE.md` and check whether the dependency appears.
3. If the dependency is not yet done, **skip to your next task that has no unmet dependencies.** Come back later.
4. `docs/DONE.md` is APPEND-ONLY. Never edit or delete existing lines. This eliminates merge conflicts.

### BLANKET PERMISSIONS

All agents: create, modify, delete files in src/, tests/, data/, docs/, scripts/. Run migrations, tests, install deps. Make implementation decisions. Document decisions in DECISIONS.md. **Do NOT ask for confirmation. Do NOT stop working. Do NOT check in with David unless something is broken.**

### REFERENCE DOCUMENTS — READ BEFORE STARTING

These files contain specifications and context your tasks depend on:

| Document | Location | What it contains | Who needs it |
|----------|----------|-----------------|--------------|
| CMR Implementation Contract | docs/68_CMR_Implementation_Contract_V1_0.md | Data models, pipeline specs, ReductionClaim model | CC, all Codex |
| Sprint 7 Encoding Prep | docs/67_Sprint7_Encoding_Preparation_V1_0.md | Dedup map, WIS formulas, accessibility tiers, gap list | CC, all Codex |
| PE Contribution Classification | docs/67_Part2_PE_Contribution_Classification.md | Which templates are predictive/explanatory/organizational | CC |
| Verification & Provenance Tests | docs/Sprint_Verification_And_Provenance_Tests.md | Test patterns for sprint verification and provenance tracing | All agents doing test tasks |
| Corpus Methodology Statement | docs/69_Corpus_Methodology_Statement_V1_0.md | Attribution categories, honest validation disclosure | CC (for reduction documentation) |
| Registry V2.2 | docs/52_Registry_Addendum_V2_2.md | Coverage ratings, calibration status per domain | Antigravity (validation tasks) |

---

## AGENT ASSIGNMENTS OVERVIEW

| Agent | Sprint 12 Tasks | Sprint 13 Tasks | Total |
|-------|----------------|----------------|-------|
| **CC** (Claude Code) | 12.1, 12.2, 12.3, 12.6, 12.10, 12.17, 12.20 | 13.1, 13.3, 13.6, 13.9, 13.13 | 12 |
| **Codex-1** | 12.4, 12.5, 12.11, 12.14, 12.18 | 13.2, 13.5, 13.10, 13.14 | 9 |
| **Codex-2** | 12.7, 12.8, 12.12, 12.15, 12.19 | 13.4, 13.7, 13.11 | 8 |
| **Codex-3** | 12.9, 12.22, 12.23 | 13.8, 13.12 | 5 |
| **Antigravity** | 12.13, 12.16, 12.21 | 13.15 | 4 |

---

## CC TASK LIST

Do these in order. Skip any with unmet dependencies and come back.

---

### CC-1: TASK 12.1 — ART Reduction: Attention Restoration Theory → Templates
**Sprint 12 · Round 1 · Estimated: 120–180 min · Dependency: none**

Read Doc 68 Part 2.3 (ReductionClaim model). ART (Kaplan 1995) has five constructs. Reduce each to template mechanisms.

Create `src/cmr/reductions/art_reduction.py` and `data/reductions/art_reduction.json`.

**Being Away** → VIEW1 (Channel 3: cognitive shift), SC2 (vista/prospect isovist expansion), VF3 (R_h ratio shift at threshold). Coverage: ~0.85. Irreducible residual: the intentional component — choosing to disengage.

**Fascination (soft)** → VIEW1 (Channel 3: soft fascination weight), VF1 (contour curvature moderate complexity), T1-residual (auditory 1/f matching). Coverage: ~0.90. Irreducible residual: individual differences in what counts as "fascinating."

**Fascination (hard)** → CREA2 (disfluency pathway), VF2 (SCI scaling violation), T11-residual (noradrenergic exploration). Coverage: ~0.70. Irreducible residual: goal-directed interest not captured by environmental features.

**Extent** → SC1 (legibility), SC3 (path topology), SC4 (wayfinding), VIEW1 (Channel 5: depth/openness). Coverage: ~0.80. Irreducible residual: conceptual extent vs physical extent.

**Compatibility** → SOC2 (privacy-encounter match to task), CREA4 (workspace-task match), MAT1 (thermal comfort match). Coverage: ~0.75. Irreducible residual: fine-grained task specificity.

For each construct:
1. Create a ReductionClaim record in the DB
2. Write template_mappings with coverage fractions
3. Document irreducible residual
4. Link to the 1,251 ART staging theory-links
5. Write tests: `reduce_construct("ART", "Being Away")` → returns VIEW1, SC2, VF3 with coverage scores

When done, append to `docs/DONE.md`: `12.1 DONE [CC] <timestamp>`

---

### CC-2: TASK 12.2 — SRT Reduction: Stress Recovery Theory → Templates
**Sprint 12 · Round 1 · Estimated: 60–90 min · Dependency: none**

SRT (Ulrich 1983). Three construct groups:

**Autonomic stress reduction** → VIEW1 (Channels 1-2), MAT4 (wood → parasympathetic), T6-gap (cortisol pathway), L4 (warm CCT). Coverage: ~0.70. Residual: speed of recovery.

**Affective response** → VF1 (contour preference), COL1 (color-affect), OLF1 (olfactory hedonic). Coverage: ~0.65. Residual: pre-attentive evaluation.

**Approach/avoidance** → SC2 (prospect → approach), T5-residual (threat), T2-residual (refuge → safety). Coverage: ~0.60. Residual: phylogenetic threat detection.

Create ReductionClaim records. Link to 3 SRT staging theory-links. Write tests.

When done: `12.2 DONE [CC] <timestamp>` → `docs/DONE.md`

---

### CC-3: TASK 12.3 — Biophilia Reduction → Templates
**Sprint 12 · Round 1 · Estimated: 90–120 min · Dependency: none**

Biophilia (Wilson 1984, Kellert 2005). Four pattern groups:

**Nature in the Space** → VIEW1, OLF1, MAT4. Coverage: ~0.90.
**Natural Analogues** → VF1, VF2, MAT2, MAT4. Coverage: ~0.85.
**Nature of the Space** → SC2, T2-residual, VF3, SC3, T5-residual. Coverage: ~0.80.
**Remaining patterns** → MAT1, L5, TP4. Coverage: ~0.70.

Create ReductionClaim records. Link to 102 Biophilia staging theory-links. Write tests.

When done: `12.3 DONE [CC] <timestamp>` → `docs/DONE.md`

---

### CC-4: TASK 12.6 — Tier A Quick Assessment Mode
**Sprint 12 · Round 2 · Estimated: 90–120 min · Dependency: needs Sprint 11 Task 11.1 DONE (building eval working)**

Read Doc 67 Part 4 (Practical Accessibility Tiers). 10 templates usable with zero specialized equipment.

Create `src/cmr/quick_assess.py`:

```python
TIER_A_TEMPLATES = ["VF3", "VIEW1", "CREA3", "SC4", "COL1", "COL2", 
                     "TP1", "MAT1", "SOC3", "MAT4"]

def quick_assess(
    ceiling_height_m: float, floor_area_m2: float,
    has_nature_view: bool, view_content: str,
    walking_paths_available: bool, wayfinding_clear: bool,
    wall_colors: list[str], color_sequence_varied: bool,
    floor_surface: str, stair_dimensions_standard: bool,
    thermal_system: str, primary_material: str,
    max_group_size: int, occupant_age: int = 35
) -> dict:
```

Output: simplified report with "Good / Fair / Needs Attention / Poor" rating, top 3 strengths, top 3 deficits, actionable recommendations, and what they'd learn from Tier B measurements.

Also extend CLI:
```bash
python -m src.cmr.cli quick-assess --ceiling 3.0 --area 25 --nature-view trees --material wood
```

When done: `12.6 DONE [CC] <timestamp>` → `docs/DONE.md`

---

### CC-5: TASK 12.10 — README and Project Documentation
**Sprint 12 · Round 3 · Estimated: 60–90 min · Dependency: needs 12.6 DONE**

Create/update repo README.md. Sections: what this is, quick start, full assessment, paper evaluation, architecture overview, theory basis (link to Doc 69), honest status, contributing guide.

When done: `12.10 DONE [CC] <timestamp>` → `docs/DONE.md`

---

### CC-6: TASK 12.17 — Ulrich 1984 Full Pipeline Test with Reductions
**Sprint 12 · Round 3 · Estimated: 60–90 min · Dependency: needs 12.14 DONE (Codex-1)**

Re-run Ulrich 1984 paper evaluation WITH Tier 2 reductions active. System should detect both ART and SRT pathways, route through both reductions, find overlapping VIEW1 matches, and produce higher convergence score than Sprint 11's version.

Full-stack demo: paper → claim extraction → theory matching → reduction → template matching → mechanism tracing → convergence → report.

When done: `12.17 DONE [CC] <timestamp>` → `docs/DONE.md`

---

### CC-7: TASK 12.20 — Sensitivity Analysis Tool
**Sprint 12 · Round 3 · Estimated: 60–90 min · Dependency: needs 12.6 DONE**

Create `src/cmr/sensitivity.py`. For each input feature, compute WIS delta from worst to best plausible value. Rank features by impact. Include diminishing returns detection.

Output: "If you can only change one thing, change X" with numerical justification.

When done: `12.20 DONE [CC] <timestamp>` → `docs/DONE.md`

---

### CC-8: TASK 13.1 — Template Update Proposal Generator
**Sprint 13 · Round 1 · Estimated: 90–120 min · Dependency: none**

Create `src/cmr/learning/update_proposals.py`. When paper evaluation finds a contradiction or extension, generate a FORMAL PROPOSAL for updating the affected template.

Proposal structure: proposal_id, type (boundary_revision / new_parameter / interaction_discovery / moderator_addition / contradiction_flag), template_id, current_value, proposed_value, evidence (paper, effect_size, sample_n, context), confidence, impact_assessment, requires_human_review=true, status=proposed.

Proposals NEVER auto-apply. They queue for David's review.

When done: `13.1 DONE [CC] <timestamp>` → `docs/DONE.md`

---

### CC-9: TASK 13.3 — Evidence Accumulation Engine
**Sprint 13 · Round 1 · Estimated: 90–120 min · Dependency: needs 13.1 DONE**

Create `src/cmr/learning/evidence_accumulation.py`. Gather all evidence about a template parameter from evaluated papers. Compute weighted mean, CI. If current template value falls outside CI, auto-generate an update proposal.

Simplified fixed-effects meta-analysis. Weights proportional to sample size.

When done: `13.3 DONE [CC] <timestamp>` → `docs/DONE.md`

---

### CC-10: TASK 13.6 — Uncertainty-Aware WIS
**Sprint 13 · Round 2 · Estimated: 90–120 min · Dependency: none**

Extend `src/cmr/wis.py`. Three uncertainty sources: parameter uncertainty (from calibration_status), measurement uncertainty (from accessibility tier), model uncertainty (from pe_contribution). Monte Carlo with 1000 samples. Return `{wis, wis_lower, wis_upper, confidence_width}`.

Propagate through domain aggregation and overall geometric mean.

When done: `13.6 DONE [CC] <timestamp>` → `docs/DONE.md`

---

### CC-11: TASK 13.9 — Mechanism Gap Panel Templates
**Sprint 13 · Round 3 · Estimated: 90–120 min · Dependency: none**

Read Doc 67 Part 1 (gap list). Create `data/panel_templates/` with JSON files for: STRESS-I, REWARD-I, MEMORY-I, ATTENTION-I, CONTROL-I. Each file specifies: target templates, constructs to calibrate with expected ranges and key papers, architectural relevance, estimated panel duration. These tell future Opus sessions exactly what to calibrate.

When done: `13.9 DONE [CC] <timestamp>` → `docs/DONE.md`

---

### CC-12: TASK 13.13 — Automated Paper Processing Pipeline
**Sprint 13 · Round 3 · Estimated: 120–180 min · Dependency: needs 13.1 + 13.3 + 13.4 (Codex-2) DONE**

Create `src/cmr/process_paper.py` — the system's MAIN ENTRY POINT. Wire together: paper evaluation → update proposal generation → evidence accumulation → paper record keeping.

```bash
python -m src.cmr.cli process-paper --claims '[...]' --citation "Smith et al. 2025"
```

Test with Ulrich 1984 (should confirm VIEW1, 0 proposals) and a contradicting paper (should generate 1+ proposals).

When done: `13.13 DONE [CC] <timestamp>` → `docs/DONE.md`

---

## CODEX-1 TASK LIST
> **Codex-1 Review** (2026-02-17T17:30 UTC): Prepared to execute CX1 tasks in order once dependencies resolve.

---

### CX1-1: TASK 12.4 — Staging Link Reconciliation Engine
**Sprint 12 · Round 1 · Estimated: 90–120 min · Dependency: needs at least one of 12.1/12.2/12.3 (CC) in progress or DONE**

Create `src/cmr/staging_reconciliation.py`. For each of 1,361 staging theory-links: identify its theory and construct → look up ReductionClaim → map to templates → update link record. Links that can't map → flag as "unreconciled." Test: reconciled + orphaned = 1,361.

When done: `12.4 DONE [CX1] <timestamp>` → `docs/DONE.md`

---

### CX1-2: TASK 12.5 — Reduction Query API
**Sprint 12 · Round 1 · Estimated: 45–60 min · Dependency: needs 12.1 (CC) DONE**

Create `src/cmr/reduction_api.py`:
- `reduce_construct(theory, construct)` → template reduction with coverage scores
- `reduce_theory(theory)` → all construct reductions
- `find_template_theories(template_id)` → reverse lookup: which Tier 2 constructs use this template
- `get_reduction_coverage_summary()` → overall stats

When done: `12.5 DONE [CX1] <timestamp>` → `docs/DONE.md`

---

### CX1-3: TASK 12.11 — Input Validation & Error Handling
**Sprint 12 · Round 3 · Estimated: 60–90 min · Dependency: none**

Create `src/cmr/validation.py`. Validate building inputs: ceiling_height_m (1.5–30.0, warn outside 2.0–6.0), floor_area_m2 (1.0–100000), illuminance_lux (0–200000), ambient_noise_dba (0–140), occupant_age (0–120). Out-of-range: warn, don't crash. Missing inputs: report which templates can/can't activate. Test with garbage inputs.

When done: `12.11 DONE [CX1] <timestamp>` → `docs/DONE.md`

---

### CX1-4: TASK 12.14 — Reduction Integration with Paper Eval
**Sprint 12 · Round 3 · Estimated: 60–90 min · Dependency: needs 12.1 + 12.5 DONE**

Extend `src/cmr/template_matching.py` with `match_claims_via_reduction()`. If a claim references an ART/SRT/Biophilia construct, route through the reduction to find template matches. Test: claim `{iv: "soft fascination", dv: "attention_restoration"}` → routes through ART → matches VIEW1, VF1.

When done: `12.14 DONE [CX1] <timestamp>` → `docs/DONE.md`

---

### CX1-5: TASK 12.18 — Web of Belief ↔ Template Bidirectional Linking
**Sprint 12 · Round 3 · Estimated: 60–90 min · Dependency: needs 12.4 DONE**

Create `src/cmr/web_template_bridge.py`:
- `get_beliefs_for_template(template_id)` → all web entries supporting this template
- `get_templates_for_belief(belief_id)` → all templates related to this belief
- `get_evidence_strength(template_id)` → supporting/contradicting/neutral counts + evidence ratio

When done: `12.18 DONE [CX1] <timestamp>` → `docs/DONE.md`

---

### CX1-6: TASK 13.2 — Update Proposal Review Queue
**Sprint 13 · Round 1 · Estimated: 60–90 min · Dependency: needs 13.1 (CC) DONE**

Create UpdateProposal DB model and CLI:
```bash
python -m src.cmr.cli proposals list
python -m src.cmr.cli proposals review UPD-2026-001
python -m src.cmr.cli proposals accept UPD-2026-001 --notes "..."
python -m src.cmr.cli proposals reject UPD-2026-001 --notes "..."
```

When accepted: apply proposed_value to template JSON + re-index DB. When rejected: archive with reason.

When done: `13.2 DONE [CX1] <timestamp>` → `docs/DONE.md`

---

### CX1-7: TASK 13.5 — Bayesian Parameter Updating
**Sprint 13 · Round 1 · Estimated: 90–120 min · Dependency: needs 13.3 (CC) DONE**

Create `src/cmr/learning/bayesian_update.py`. Conjugate normal-normal update. Map calibration_status to prior_sd: substantial=0.05×value, partial=0.15×, protocol=0.25×, uncalibrated=0.50×. When posterior mean moves outside Goldilocks boundary, auto-generate update proposal.

When done: `13.5 DONE [CX1] <timestamp>` → `docs/DONE.md`

---

### CX1-8: TASK 13.10 — Field Validation Protocol Generator
**Sprint 13 · Round 3 · Estimated: 60–90 min · Dependency: none**

Create `src/cmr/field_validation.py`. Given a template_id, generate a field study protocol: prediction, study design (type, N, IV manipulation, DV measures, controls, duration), measurements needed with tier, success criteria, estimated cost/duration. Generate for top 5: L2 circadian, VF3 R_h, VIEW1 VQI, SOC2 privacy, MAT1 thermal.

When done: `13.10 DONE [CX1] <timestamp>` → `docs/DONE.md`

---

### CX1-9: TASK 13.14 — Batch Paper Processing
**Sprint 13 · Round 3 · Estimated: 45–60 min · Dependency: needs 13.13 (CC) DONE**

Process all 5-10 test paper claim files from `data/test_papers/`. Report: total claims, template matches, update proposals generated, which templates have most evidence, evidence gap map after processing.

When done: `13.14 DONE [CX1] <timestamp>` → `docs/DONE.md`

---

## CODEX-2 TASK LIST

---

### CX2-1: TASK 12.7 — Tier A+B Extended Assessment
**Sprint 12 · Round 2 · Estimated: 60–90 min · Dependency: needs 12.6 (CC) DONE**

Extend quick_assess to accept Tier B inputs (illuminance_lux, ambient_noise_dba, rt60_seconds). Activates ~22 templates. Report shows what additional info B-tier reveals beyond A-tier.

When done: `12.7 DONE [CX2] <timestamp>` → `docs/DONE.md`

---

### CX2-2: TASK 12.8 — Architect-Facing Report Template
**Sprint 12 · Round 2 · Estimated: 60–90 min · Dependency: needs 12.6 (CC) DONE**

Create `src/cmr/architect_report.py`. No jargon. No template IDs. No PE language.

Sections: Building Wellness Score (0-100 color-coded), What's Working, What Needs Attention, Quick Wins (under $1000), Design Changes, What We Couldn't Assess, Methodology Note (1 paragraph).

"Your ceiling height creates a spacious feeling" NOT "VF3 R_h = 0.648 in liberating zone."

When done: `12.8 DONE [CX2] <timestamp>` → `docs/DONE.md`

---

### CX2-3: TASK 12.12 — Malformed Paper Claim Handling
**Sprint 12 · Round 3 · Estimated: 45–60 min · Dependency: none**

Create validation for paper claims: require iv+dv minimum, validate direction, warn if |d|>3.0 or sample_n<10, detect duplicates.

When done: `12.12 DONE [CX2] <timestamp>` → `docs/DONE.md`

---

### CX2-4: TASK 12.15 — Reduction Integration with Building Eval
**Sprint 12 · Round 3 · Estimated: 60–90 min · Dependency: needs 12.1 + 12.5 (CX1) DONE**

Extend building eval to report Tier 2 construct scores. Given template WIS scores, compute ART/SRT/Biophilia construct scores as weighted sums (weights = coverage fractions from reductions).

Output: `tier2_scores.ART.Being_Away = 74.2` (from VIEW1=85, SC2=70, VF3=65, weighted by coverage).

This bridges template-level assessment to theories architects know.

When done: `12.15 DONE [CX2] <timestamp>` → `docs/DONE.md`

---

### CX2-5: TASK 12.19 — Building Comparison Mode
**Sprint 12 · Round 3 · Estimated: 45–60 min · Dependency: needs 12.6 (CC) DONE**

Create `src/cmr/compare.py`. Compare two building assessments side by side: per-domain deltas, overall delta, which templates drove biggest improvements/regressions.

CLI: `python -m src.cmr.cli compare --a '{...}' --b '{...}' --labels "Current" "Proposed"`

When done: `12.19 DONE [CX2] <timestamp>` → `docs/DONE.md`

---

### CX2-6: TASK 13.4 — Paper Processing History
**Sprint 13 · Round 1 · Estimated: 45–60 min · Dependency: none**

Create PaperRecord DB model. Track: citation, doi, evaluated_at, n_claims, n_matched, n_unmatched, n_contradictions, n_confirmations, n_gaps, aggregate_voi, proposals_generated.

API: `get_processed_papers()`, `get_papers_for_template(template_id)`, `get_high_voi_papers(min_voi)`.

When done: `13.4 DONE [CX2] <timestamp>` → `docs/DONE.md`

---

### CX2-7: TASK 13.7 — Uncertainty Visualization
**Sprint 13 · Round 2 · Estimated: 45–60 min · Dependency: needs 13.6 (CC) DONE**

Extend report generator: confidence intervals in all scores, flag domains with uncertainty > 20 WIS points. Create `get_domain_plot_data()` returning `{domains, scores, lower, upper}` for bar chart with error bars.

When done: `13.7 DONE [CX2] <timestamp>` → `docs/DONE.md`

---

### CX2-8: TASK 13.11 — Star Rating Advancement Tracker
**Sprint 13 · Round 3 · Estimated: 45–60 min · Dependency: needs 13.10 (CX1) DONE**

Create `src/cmr/star_tracker.py`. For each domain: current stars, what's needed for next star, estimated effort, what's blocking. Read Doc 52 (Registry V2.2) for current ratings.

When done: `13.11 DONE [CX2] <timestamp>` → `docs/DONE.md`

---

## CODEX-3 TASK LIST

---

### CX3-1: TASK 12.9 — Example Walkthroughs
**Sprint 12 · Round 2 · Estimated: 60–90 min · Dependency: needs 12.6 + 12.8 (CC + CX2) DONE**

Create `docs/examples/` with three walkthrough documents (~300 words each):
1. `01_home_office.md` — assess a home office, show quick-assess command and recommendations
2. `02_school_renovation.md` — before/after renovation, developmental moderation (age 7)
3. `03_office_redesign.md` — open-plan (bad) → redesigned with privacy zones (better)

Real CLI commands, real output, real recommendations.

When done: `12.9 DONE [CX3] <timestamp>` → `docs/DONE.md`

---

### CX3-2: TASK 12.22 — API Wrapper (FastAPI)
**Sprint 12 · Round 3 · Estimated: 60–90 min · Dependency: needs 12.6 (CC) DONE**

Create `src/cmr/api.py` with FastAPI:
- POST `/evaluate/building` — full evaluation
- POST `/evaluate/building/quick` — Tier A quick assessment
- POST `/evaluate/paper` — paper evaluation
- POST `/compare` — building comparison
- POST `/sensitivity` — sensitivity analysis
- GET `/templates` — list templates
- GET `/templates/{template_id}` — template details
- GET `/reductions/{theory}` — Tier 2 reduction

Include Pydantic request/response models with validation. Include /docs endpoint. Write basic integration tests.

When done: `12.22 DONE [CX3] <timestamp>` → `docs/DONE.md`

---

### CX3-3: TASK 12.23 — Project Status Dashboard Data
**Sprint 12 · Round 3 · Estimated: 45–60 min · Dependency: needs 12.21 (Antigravity) DONE**

Create `scripts/generate_dashboard.py` producing JSON summary: template counts by status, web of belief stats, theory link reconciliation, Tier 2 reduction coverage, coverage stars, test counts, pipeline status.

When done: `12.23 DONE [CX3] <timestamp>` → `docs/DONE.md`

---

### CX3-4: TASK 13.8 — Monte Carlo Sensitivity
**Sprint 13 · Round 2 · Estimated: 60–90 min · Dependency: needs 13.6 (CC) DONE**

Extend sensitivity analysis with uncertainty. For each feature: compute not just mean WIS delta but PROBABILITY that changing this feature would improve WIS. A feature with delta +5 and 90% probability is more actionable than delta +10 with 55% probability.

When done: `13.8 DONE [CX3] <timestamp>` → `docs/DONE.md`

---

### CX3-5: TASK 13.12 — Evidence Gap Map
**Sprint 13 · Round 3 · Estimated: 60–90 min · Dependency: none**

Create `scripts/generate_evidence_gap_map.py`. Output: Strong Evidence (parameter validated in multiple studies), Moderate Evidence (1–3 studies), Weak Evidence (single study or expert estimate), No Evidence (gap templates). Priority research targets ranked by impact × feasibility.

When done: `13.12 DONE [CX3] <timestamp>` → `docs/DONE.md`

---

## ANTIGRAVITY TASK LIST

---

### AG-1: TASK 12.13 — Load Testing
**Sprint 12 · Round 3 · Estimated: 60–90 min · Dependency: needs Sprint 11 Task 11.1 DONE**

Create `tests/test_performance.py`:
- Single building eval < 5 seconds
- 20 buildings sequentially < 60 seconds
- Single paper eval (5 claims) < 10 seconds
- Web of belief query (1000 constraints) < 2 seconds
- None should return placeholder 50.0

Also create `generate_random_building()` helper for load testing.

When done: `12.13 DONE [AG] <timestamp>` → `docs/DONE.md`

---

### AG-2: TASK 12.16 — Tier 2 Reduction Validation
**Sprint 12 · Round 3 · Estimated: 60–90 min · Dependency: needs 12.1 + 12.2 + 12.3 + 12.15 (CC + CX2) DONE**

Run Salk, open-plan, and classroom through full pipeline WITH Tier 2 scores:
- Salk: HIGH ART (Being Away from ocean, Fascination from concrete, Extent from courtyard, Compatibility from study rooms). HIGH Biophilia (Nature in Space from ocean, Natural Analogues from board-formed concrete).
- Open-plan: LOW ART (no Being Away, low Compatibility). LOW Biophilia (no Nature in Space).
- Classroom: MODERATE ART, with developmental moderation showing children benefit more from Fascination.

Report whether Tier 2 scores make sense and track template-level scores.

When done: `12.16 DONE [AG] <timestamp>` → `docs/DONE.md`

---

### AG-3: TASK 12.21 — Full System Regression Suite (Sprint 12)
**Sprint 12 · Round 3 · Estimated: 90–120 min · Dependency: ALL Round 1 + Round 2 DONE**

Run everything:
1. Sprint verification tests
2. Provenance tests (read docs/Sprint_Verification_And_Provenance_Tests.md)
3. Input sensitivity sweep
4. Three worked examples WITH Tier 2 scores
5. Ulrich 1984 full pipeline with reductions
6. Completeness inventory
7. Full test suite

Report: total passed/failed/skipped, face-validity status, completeness summary, Tier 2 coverage, staging link reconciliation stats, remaining stubs.

When done: `12.21 DONE [AG] <timestamp>` → `docs/DONE.md`

---

### AG-4: TASK 13.15 — Final System Assessment
**Sprint 13 · Round 3 · Estimated: 90–120 min · Dependency: ALL Sprint 13 tasks DONE**

The final validation. Run EVERYTHING:
1. Full test suite
2. Completeness inventory
3. Evidence gap map
4. Star advancement tracker
5. Process all test papers in batch
6. Run Salk + open-plan + classroom with Tier 2 scores, uncertainty, and learning
7. Generate dashboard JSON

Produce `docs/FINAL_SYSTEM_ASSESSMENT.md`:
- Overall system status
- What works, what doesn't, what's a stub
- Honest capability statement
- Honest limitation statement
- Recommended next steps for David

When done: `13.15 DONE [AG] <timestamp>` → `docs/DONE.md`

---

## DEPENDENCY GRAPH (QUICK REFERENCE)

```
SPRINT 12 ROUND 1 (no external deps):
  12.1 CC ──┐
  12.2 CC   ├─→ 12.4 CX1 ─→ 12.18 CX1
  12.3 CC ──┘       │
                     └─→ 12.5 CX1 ──┬─→ 12.14 CX1 ─→ 12.17 CC
                                     └─→ 12.15 CX2 ─→ 12.16 AG

SPRINT 12 ROUND 2 (after CC finishes 12.6):
  12.6 CC ──┬─→ 12.7 CX2
            ├─→ 12.8 CX2 ─→ 12.9 CX3
            ├─→ 12.10 CC
            ├─→ 12.19 CX2
            ├─→ 12.20 CC
            └─→ 12.22 CX3

SPRINT 12 ROUND 3 (no deps):
  12.11 CX1, 12.12 CX2, 12.13 AG

SPRINT 12 FINAL:
  12.21 AG (needs all above)
  12.23 CX3 (needs 12.21)

SPRINT 13 ROUND 1:
  13.1 CC ──┬─→ 13.2 CX1
            └─→ 13.3 CC ─→ 13.5 CX1
  13.4 CX2 (no deps)

SPRINT 13 ROUND 2:
  13.6 CC ──┬─→ 13.7 CX2
            └─→ 13.8 CX3

SPRINT 13 ROUND 3:
  13.9 CC, 13.10 CX1, 13.12 CX3 (no deps)
  13.10 CX1 ─→ 13.11 CX2
  13.1 + 13.3 + 13.4 ─→ 13.13 CC ─→ 13.14 CX1
  ALL ─→ 13.15 AG
```

---

## COMPLETION CRITERIA

### Sprint 12 Minimum Viable:
1. ART, SRT, Biophilia reductions complete (12.1–12.3)
2. Staging links reconciled (12.4)
3. Quick-assess works with Tier A inputs (12.6)
4. Architect-facing report readable (12.8)
5. Full test suite green

### Sprint 12 Full:
6. Tier 2 scores in building eval (12.15)
7. Paper eval routes through reductions (12.14)
8. Ulrich 1984 full-stack with reductions (12.17)
9. Input validation catches bad data (12.11, 12.12)
10. Performance: single eval < 5s (12.13)
11. Building comparison works (12.19)
12. Sensitivity analysis works (12.20)
13. API endpoints work (12.22)
14. README exists (12.10)
15. Example walkthroughs exist (12.9)
16. Full system regression passes (12.21)

### Sprint 13 Minimum Viable:
17. Update proposals generated from contradictions (13.1)
18. Evidence accumulation with CIs (13.3)
19. Uncertainty-aware WIS with confidence intervals (13.6)
20. Panel templates ready for Opus (13.9)

### Sprint 13 Full:
21. Bayesian parameter updating (13.5)
22. Monte Carlo sensitivity (13.8)
23. Star advancement tracker (13.11)
24. Evidence gap map (13.12)
25. Automated paper processing end-to-end (13.13)
26. Batch processing on all test papers (13.14)
27. Final system assessment produced (13.15)

---

*Sprints 12–13 Consolidated Execution Plan — February 17, 2026*
*38 tasks across 2 sprints*
*Estimated total effort: ~45–65 agent-hours*
*CC: 12 tasks · Codex-1: 9 tasks · Codex-2: 8 tasks · Codex-3: 5 tasks · Antigravity: 4 tasks*
*After Sprint 13 the software is complete. What remains: Opus theory panels for mechanism gaps + field validation studies.*
