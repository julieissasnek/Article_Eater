# Sprint Integration: Web Connectivity Audit + CVA + Subject Characteristics

**Date**: February 28, 2026
**Context**: Integrating three streams of work: (1) Chat's WEB_CONNECTIVITY_AUDIT_AND_ANNOTATION_BRIEF, (2) CVA Sprint Plan (CVA-1 through CVA-9), and (3) new Subject-Characteristics Architecture (culture, neurotype, developmental stage)
**Status**: REVISED SPRINT PLAN — For David's Review

---

## THE THREE STREAMS AND HOW THEY CONNECT

The WEB_CONNECTIVITY_AUDIT identifies critical infrastructure gaps in the EN (Epistemic Network) that must be addressed *regardless* of whether CVA is adopted. The CVA sprint plan assumes a functioning EN with adequate evidence density. The Subject-Characteristics Architecture (ψ-parameterization) requires both the EN and CVA infrastructure to be operational.

**Dependency chain**:
```
EN Infrastructure (connectivity + annotations)
    ↓
ATLAS Core Sprints (0.5, 1-REV, 2-REV, 3-7)
    ↓
CVA Foundation (CVA-1, CVA-2, CVA-3)  ←  ψ Subject-Characteristics Architecture feeds into CVA-1 and CVA-2
    ↓
CVA Pilot + Empirical (CVA-4 through CVA-9)
```

---

## REVISED SPRINT PLAN

### TIER 0: EN INFRASTRUCTURE (Connectivity Gaps — from WEB_CONNECTIVITY_AUDIT)

These are preconditions for everything else. The audit identified three gaps; we add sprint items for each.

#### Sprint EN-0A: Bridge Template Worlds (1-2 days)
**Source**: Gap ① — calibrated and uncalibrated templates use different field schemas
**Script status**: READY (per audit: "script ready")
**Tasks**:
1. Run the bridging script to make all 208 templates queryable by common QA features
2. Verify: all 208 templates accessible through unified query interface
3. Non-destructive: original schemas preserved, bridging layer added

**Why now**: This is the lowest-effort, highest-impact action in the entire sprint plan. Unlocks querying across the full template library. Everything downstream benefits.

#### Sprint EN-0B: Belief Seeder Extension + Theory/Molecule Backfill (2-3 days)
**Source**: Gap ② + Gap ③
**Tasks**:
1. Run belief seeder on uncalibrated templates (currently only calibrated) — adds ~105 beliefs to web
2. Backfill 5 theories with 0 constituent_templates links
3. Verify bidirectional molecule→template links (13 molecules, 85 template links)
4. Reference resolution: match 326 author-year references to DOIs for paper linkage

**Why now**: Increases evidence density in the web before any CVA or panel work attempts to use it. Without this, the web has ~103 beliefs from seed script + ~18 from papers — far too sparse for serious analysis.

#### Sprint EN-0C: Paper Integration Pipeline Activation (1-2 weeks)
**Source**: Gap ③ — only 18/1,046 extractions made it through pipeline
**Tasks**:
1. Quality review of 1,046 extractions (triage into: ready, needs-review, reject)
2. Run PaperIntegrationOrchestrator on "ready" extractions in batches of 50
3. Monitor: coherence deltas, belief count growth, error rate
4. Target: ≥200 article-sourced beliefs integrated (from current 18)

**Why now**: The extraction pipeline exists and has been tested. The Gemini extraction run produced 1,046 files. The bottleneck is execution, not engineering. This dramatically increases the EN's evidence base.

**Dependency**: EN-0A should complete first (so new beliefs can be linked to all 208 templates).

#### Sprint EN-0D: Annotation System Implementation (1 week)
**Source**: Section 2 of WEB_CONNECTIVITY_AUDIT + existing Panel Decision D-B2
**Note**: This maps directly to existing SPRINT-0.5 in TASKS.md ("Three-Layer Annotation Model")

**Design decisions (proposed — for David's review)**:

| Question | Proposed Answer | Rationale |
|----------|----------------|-----------|
| Storage | Separate annotation store (SQLite table) | Decouples annotations from template JSON; allows versioning without touching data |
| Authorship | System + named human experts (no crowdsourcing initially) | Maintains quality; crowdsourcing is Phase 2 |
| Lifecycle | Immutable append-only with supersession | Audit trail; never lose history |
| Priority order | SENSITIVITY_FLAG + CALIBRATION_NOTE first | Highest information density per audit |
| Molecule links | Annotations (lightweight, versionable) | Easier to iterate than hardcoded JSON |
| Preprocessing | Applied at query time (always fresh) | Avoids stale caches; performance acceptable at current scale |

**Schema**: Use the Annotation dataclass from WEB_CONNECTIVITY_AUDIT §2, implemented as:
- New migration: `024_annotation_system.sql`
- New service: `src/services/annotation_service.py`
- 10 annotation types across 3 layers (Evidence, Relational, QA)

**Integration with existing D-B2**: The three-layer annotation model from Panel B Decision B2 maps cleanly:
- Layer 1 (web molecules/T1.5s) → MOLECULE_LINK + CROSS_REFERENCE annotations
- Layer 2 (stimulus feature tags) → extends TagAssignmentEngine with annotation support
- Layer 3 (methodological tags) → PROVENANCE_PATCH + EVIDENCE_OVERRIDE annotations

---

### TIER 1: ATLAS CORE SPRINTS (Existing — now with clear sequencing)

These are the previously defined sprints, now sequenced after EN infrastructure:

| Sprint | Name | Duration | Depends On | Status |
|--------|------|----------|------------|--------|
| 0.5 | Three-Layer Annotation Model | 1 week | EN-0D (merged) | → MERGED INTO EN-0D |
| 1-REV | Three-Number Separation (ω, d, CPT) | 1 week | EN-0A, EN-0B | PENDING |
| 2-REV | π Projection Deployment | 1 week | 1-REV | PARTIALLY DONE (epistemic_projection.py exists) |
| 3 | Coherence Dashboard | 3 days | 2-REV | PENDING |
| 4 | Argumentation Graph + AESHI | 3 days | 2-REV | PARTIALLY DONE |
| 5 | Nightly Batch Infrastructure | 3 days | 4 | PARTIALLY DONE |
| 6 | Expert Calibration Prep | 3 days | 5 | PENDING |
| 7 | T2 Mechanism Templates | 1 week | Parallel | PENDING |

**Change from previous plan**: Sprint 0.5 is merged into EN-0D (annotation system) to avoid duplication.

---

### TIER 2: CVA FOUNDATION (Sprints CVA-1 to CVA-3 — NOW WITH ψ INTEGRATION)

These sprints are modified to incorporate the Subject-Characteristics Architecture from today's session.

#### Sprint CVA-1-REV: Constraint Variable Registry + Two-Tier Architecture (2 weeks)
**Original**: Define 8 constraints with measurement protocols
**NEW additions from today**:
1. **Two-tier constraint architecture**: Split each constraint into Tier 1 (universal perceptual primitives) and Tier 2 (ψ-calibrated interpretive thresholds)
2. **ψ modulation of constraints**: Each constraint function parameterized by θ(ψ) — e.g., ProcessingCost depends on ψ_neuro (ADHD vs. neurotypical), ψ_culture (holistic vs. analytic scanning), ψ_dev (age-related processing speed)
3. **Neurotype sensitivity profiles**: For each constraint, document how PTSD, ASD, ADHD, Alzheimer's, older adults, children, depression, anxiety, bipolar, and gifted populations differ
4. **Connection to ATLAS δ**: Show that the population transfer factor δ(pop, pop_target) can be derived from ψ-distance between source and target populations

**Key reference**: `docs/CVA_SUBJECT_CHARACTERISTICS_ARCHITECTURE_2026-02-28.md`
**Key reference**: `docs/CONSTRAINT_UNIVERSALITY_REVIEW_2026-02-28.md`

**Deliverables**:
- `constraint_variables.py` (updated with two-tier architecture)
- `subject_characteristics.py` (ψ parameter space dataclass)
- Neurotype constraint sensitivity table (10 neurotypes × 8 constraints)
- Tier 1/Tier 2 split documentation

#### Sprint CVA-2-REV: Valuation Axes Schema + Cultural Decomposition (2 weeks)
**Original**: Define 9 VL axes with interactions
**NEW additions from today**:
1. **Culture-parametric valuation structure**: κ(ψ) selects not just weights but STRUCTURE — different cultures have different decompositions (Japanese: amae + ma; West African: àṣà cluster; Indian: rasa-based)
2. **Neurotype valuation modulation**: PTSD → SafetyValue hyperactivation; Depression → InterestValue/RestorationValue suppression; ASD → CompetenceSupport prioritization
3. **Rasa-as-attractors formalization**: Model holistic aesthetic states as stable attractors in valuation dynamics — clusters in v-space that the system converges to, rather than decomposable dimensions (resolves Barrett/Indian panel concerns)

**Key reference**: `docs/CVA_CULTURE_AWARE_ARCHITECT_PANEL_2026-02-28.md`
**Key reference**: `docs/CVA_SPECIALIZED_PANELS_2026-02-27.md` (Panels A, C)

**Deliverables**:
- `valuation_axes.py` (updated with cultural decomposition κ)
- Cultural variant specifications (Western, Japanese, West African, Indian — at minimum)
- Neurotype valuation modulation profiles (10 neurotypes × valuation changes)
- Rasa-as-attractors mathematical formulation

#### Sprint CVA-3: ActivityFrame Implementation (2 weeks)
**Unchanged** — but now with explicit connection to ψ_state (current psychological state affects frame selection).

---

### TIER 3: CVA PILOT + EMPIRICAL (Sprints CVA-4 through CVA-9)

| Sprint | Name | Duration | Key Modification |
|--------|------|----------|-----------------|
| CVA-4 | 20-Template Pilot Reclassification | 3 weeks | Include ψ-aware reclassification for 3 neurotype populations |
| CVA-5 | Goal-Modulated Projection | 2 weeks | Extend π with ψ parameter: logit(p) = d(τ, g, ψ) · ω · δ(ψ_source, ψ_target) · logit(p_lab) |
| CVA-6 | Beauty Compression Testing | 2 weeks | Test cultural beauty models (KL-divergence Model 3) alongside linear/categorical |
| CVA-7 | Identifiability Experiment Design | 2 weeks | **NEW**: Include VR stimulus generation protocol (see VR section below) |
| CVA-8 | Cross-Cultural Validation Design | 2 weeks | **EXPANDED**: Include neurotype populations alongside cultural groups |
| CVA-9 | Integration Decision + Master Doc | 4 weeks | Updated with all new architecture |

---

### VR STIMULUS GENERATION (for CVA-7)

David confirmed he can run VR experiments if stimuli can be generated automatically. Options:

1. **Procedural VR generation using existing tools**:
   - Unity/Unreal with parametric room generators (vary ceiling height, lighting, material, density)
   - Open-source options: A-Frame (web VR), Three.js scenes, or Vizard (Python-based VR)
   - Each constraint can be independently manipulated: ProcessingCost (visual clutter), ControlEfficacy (signage clarity), SocialCueDensity (avatar count), etc.

2. **AI-generated architectural environments**:
   - Use image generation (DALL-E, Midjourney) for 2D stimulus arrays (faster, cheaper)
   - Use 3D scene generation (e.g., Blockade Labs Skybox, Luma AI) for immersive environments
   - Validate: does AI-generated VR produce same psychometric properties as hand-designed VR?

3. **Hybrid approach (RECOMMENDED)**:
   - Design 4-5 base room templates in Unity (hospital room, office, café, meditation space, community center)
   - Parametrically vary each constraint variable (8 constraints × 3 levels = 24 variants per room)
   - Generate 120 unique VR scenes (5 rooms × 24 variants)
   - Run adaptive preference tests (pairwise comparisons) to measure valuation responses
   - This provides the constraint-manipulation data Jordan requires for identifiability

**UCSD resources**: UCSD has VR labs in CogSci (Contextual Robotics Institute) and Design Lab. Check with Hollan or Kirsh Lab colleagues for shared equipment access.

---

### PAPER SERIES STRATEGY

David confirmed preference for a series of shorter papers. Proposed sequence:

| # | Paper | Target Journal | CVA Sprint Dependency | Estimated Length |
|---|-------|---------------|----------------------|-----------------|
| 1 | **ATLAS Architecture: Epistemic Networks, Projection, and Bayesian Integration** | *Psychological Review* or *Psychonomic Bulletin & Review* | Sprints 1-REV, 2-REV, 8 (Master Doc) | 15,000 words |
| 2 | **Constraint-Valuation Architecture: A Meta-Framework for Environmental Psychology** | *Journal of Environmental Psychology* | CVA-1, CVA-2, CVA-3 | 12,000 words |
| 3 | **Cultural Contingency in Environmental Valuation: Evidence from Cross-Cultural Expert Panels** | *Culture and Brain* or *Journal of Cross-Cultural Psychology* | CVA-8, culture panels | 10,000 words |
| 4 | **Subject-Dependent Environmental Constraints: Neurotype, Culture, and Age as Modulators** | *Environment and Behavior* or *Neuropsychologia* | CVA-1-REV, ψ architecture, neurotype profiles | 12,000 words |
| 5 | **Beauty as Compression: Four Models of Aesthetic Judgment in Built Environments** | *Empirical Studies of the Arts* or *British Journal of Aesthetics* | CVA-6, beauty models | 8,000 words |
| 6 | **Empirical Validation of CVA: VR Experiments on Constraint Identifiability** | *Behavior Research Methods* or *PNAS* | CVA-7, VR experiments | 8,000 words |
| 7 | **The Goldilocks Principle Across Populations: Optimal Complexity in Environmental Design** | *Cognitive Science* or *Trends in Cognitive Sciences* | ψ-parameterized Goldilocks, VR data | 10,000 words |

**Paper 1** can be written now (ATLAS architecture is mature). **Paper 2** requires CVA foundation sprints. **Papers 3-7** require empirical work.

---

## MASTER TIMELINE

```
WEEK 1-2:    EN-0A (bridge templates) + EN-0B (belief seeder + backfill)
WEEK 2-3:    EN-0C (paper integration pipeline, first 200 extractions)
WEEK 2-3:    EN-0D/Sprint 0.5 (annotation system implementation)
WEEK 3-4:    Sprint 1-REV (three-number separation)
WEEK 4-5:    Sprint 2-REV (π projection — partially done)
WEEK 5-6:    Sprints 3-6 (dashboard, AESHI, nightly, calibration)
WEEK 5-6:    Sprint 7 (T2 templates — parallel)
WEEK 6-8:    CVA-1-REV (constraints + two-tier + ψ)
WEEK 8-10:   CVA-2-REV (valuations + cultural decomposition + rasa-attractors)
WEEK 10-12:  CVA-3 (activity frames)
WEEK 12-15:  CVA-4 (20-template pilot with ψ-aware reclassification)
WEEK 15-17:  CVA-5 + CVA-6 (projection + beauty compression)
WEEK 17-19:  CVA-7 (identifiability experiment design + VR stim generation)
WEEK 19-21:  CVA-8 (cross-cultural + neurotype validation design)
WEEK 21-25:  CVA-9 (integration decision)

PARALLEL TRACK (starting week 1):
- Paper 1 writing (ATLAS architecture)
- VR stimulus prototyping
- Collaborator outreach (India, Japan)
```

---

## DECISION LOG

| ID | Decision | Date | Context |
|----|----------|------|---------|
| D-2028-01 | Constraint layer approximately universal; valuation layer culturally parameterized | 2026-02-28 | David's explicit endorsement |
| D-2028-02 | Subject characteristics (ψ) as major factor throughout CVA | 2026-02-28 | David: "The more we know about subjects the better" |
| D-2028-03 | Neurotype expansion: collect evidence on PTSD, Bipolar, Alzheimer's, older adults, children, gifted, ASD, ADHD, depression, anxiety | 2026-02-28 | David's explicit request |
| D-2028-04 | Two-tier constraint architecture (universal primitives + ψ-calibrated thresholds) | 2026-02-28 | Supported by literature review; David agrees perception of visual complexity varies culturally |
| D-2028-05 | CVA purpose: diagnostic/screening tool + theory tool for VOI + deep field understanding | 2026-02-28 | David: "not where we must be in temporal dynamics" but current scope is sufficient |
| D-2028-06 | Rasa-like holistic states as attractors in CVA dynamical system | 2026-02-28 | David prefers this over treating rasa as incommensurable alternative |
| D-2028-07 | Publication strategy: series of shorter papers | 2026-02-28 | David's explicit preference |
| D-2028-08 | VR experiments feasible if stimuli can be auto-generated | 2026-02-28 | David: "if you can help me create the VR stims or find an automated method" |
| D-2028-09 | India collaborator possible; Japan uncertain; adaptive preference tests viable | 2026-02-28 | David's assessment of empirical feasibility |
| D-2028-10 | Annotation system: separate store, system + named experts, append-only, SENSITIVITY_FLAG first | 2026-02-28 | Proposed based on WEB_CONNECTIVITY_AUDIT; awaiting David's confirmation |

---

## OPEN QUESTIONS FOR DAVID

1. **EN-0D Annotation decisions**: Do you agree with the proposed design choices (separate store, immutable, SENSITIVITY_FLAG first)? Or do you have a preference for storing annotations within template JSONs?

2. **Paper integration pipeline**: The audit notes 1,046 extractions exist but quality is uncertain. Should we (a) quality-review all before integration, (b) integrate aggressively and flag low-quality post-hoc, or (c) run a 50-extraction pilot to estimate quality rate?

3. **VR lab access**: Can you confirm access to VR equipment at UCSD (CogSci, Design Lab, or elsewhere)? This determines whether CVA-7 is feasible as planned.

4. **Collaborator in India**: Who would this be? Having a name lets us design culturally appropriate stimuli and factor analysis protocols tailored to the collaboration.

5. **Sprint 0.5 vs EN-0D merger**: The WEB_CONNECTIVITY_AUDIT's annotation system is essentially the same as Sprint 0.5's Three-Layer Annotation Model (Panel B Decision D-B2). I've merged them. Correct?

---

**Prepared for**: David Kirsh, UCSD Cognitive Science
**Files referenced**:
- `docs/WEB_CONNECTIVITY_AUDIT_AND_ANNOTATION_BRIEF_2026-02-27.md` (Chat's audit)
- `docs/CVA_SPRINT_PLAN_2026-02-27.md` (original CVA sprints)
- `docs/CVA_SUBJECT_CHARACTERISTICS_ARCHITECTURE_2026-02-28.md` (new today)
- `docs/CONSTRAINT_UNIVERSALITY_REVIEW_2026-02-28.md` (new today)
- `docs/CVA_CULTURE_AWARE_ARCHITECT_PANEL_2026-02-28.md` (new today)
