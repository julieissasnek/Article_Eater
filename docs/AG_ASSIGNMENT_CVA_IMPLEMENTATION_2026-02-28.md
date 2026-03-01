# AG ASSIGNMENT: CVA Implementation — 7 Phases, 7 Weeks

**Date**: February 28, 2026
**Assigned to**: AG (Claude Opus)
**Assigned by**: Professor David Kirsh, UCSD Cognitive Science
**Specification by**: Cowork Session 12
**Priority**: CRITICAL — Begin immediately. Work fast. Ship tested code.

---

## EXECUTIVE BRIEF

AG, this is your master assignment. You have 7 phases of work to translate ~15,000 lines of theoretical specification into ~8,250 lines of tested, integrated, overseer-managed code. The existing ATLAS codebase is mature and solid. Your job is to **extend it — not rewrite it**.

**The cardinal rule**: CVA is an extension layer (strangler fig pattern). The existing Quinean web of belief, the 14-step integration orchestrator, the notification service, the annotation system — all of these keep working unchanged. CVA adds constraint vectors, valuation vectors, attractor dynamics, and cultural parameterization *on top of* existing infrastructure. If at any point your changes break existing tests, **stop and fix before proceeding**.

---

## 1. KEY REFERENCE DOCUMENTS

Read these BEFORE writing any code. They contain the specifications you are implementing. If a spec is ambiguous, consult these docs first; if still unclear, ask David.

| Document | Contains | Used In |
|----------|----------|---------|
| **RASA_AS_ATTRACTORS_CVA_DYNAMICS_2026-02-28.md** | Attractor math, 9 rasa configs, Lyapunov analysis, 4 new molecules, bifurcation dynamics | Phases 2, 3, 6 |
| **CVA_SUBJECT_CHARACTERISTICS_ARCHITECTURE_2026-02-28.md** | ψ parameter space, 10 neurotype profiles, two-tier constraints, δ population transfer | Phases 1, 2, 5 |
| **THREE_HARD_PROBLEMS_EXPERT_PANEL_2026-02-28.md** | Recognition model c~p(c\|x,A), decomposed feedback, precision modulation, panel recommendations | Phase 2 |
| **CVA_Technical_Paper_Three_Hard_Problems.docx** | Chat's solutions: ActivityFrame, constraints before valuation, feedback decomposition, Appendix A dynamics | Phase 2 (primary source) |
| **CVA_CULTURE_AWARE_ARCHITECT_PANEL_2026-02-28.md** | Culture-parametric valuations, amae/àṣà/rasa variants, design scenarios | Phases 1, 3 |
| **WEB_CONNECTIVITY_AUDIT_AND_ANNOTATION_BRIEF_2026-02-27.md** | Connectivity gaps, annotation schema, pipeline utilization audit | Phases 0, 4, 5 |
| **IMPLEMENTATION_PLAN_THEORY_TO_CODE_2026-02-28.md** | Full plan with code snippets and design decisions | ALL phases |

---

## 2. CARDINAL RULES

These rules are non-negotiable. Violating any of them will create technical debt that compounds across phases.

### Rule 1: Test First, Code Second

Every task has a corresponding test file listed. Write the test skeleton BEFORE implementing the code. This ensures you understand the expected behavior. Run tests after every task. Green suite = proceed. Red suite = stop and fix.

### Rule 2: Strangler Fig — Extend, Never Replace

All CVA code lives in NEW files (`src/models/cva_*.py`, `src/services/cva_*.py`). You modify existing files only to add hooks, not to change existing behavior. The web of belief, overseer, orchestrator, notification service, annotation service, and extraction pipeline must all continue to work exactly as before.

### Rule 3: Architecture Decision Records

Before making any non-trivial design choice, write a lightweight ADR in `src/adr/`. Format: Context → Decision → Consequences → Fitness Function. The fitness function is an automated test that verifies the decision holds. ADRs are cheap; wrong architectural decisions are expensive.

### Rule 4: Descriptive Names, Dated Files

Never use generic names. `cva_constraint_engine.py` not `utils.py`. `rasa_attractors.json` not `config.json`. Every new data file gets a creation date in its metadata. Every new module gets a docstring explaining its role in the system.

### Rule 5: Report Progress

At the end of each phase, update `TASKS.md` with what was completed, what was deferred, and any decisions that need David's input. Update `ACTIVE_TASKS.md` if running in parallel with other terminals.

### Rule 6: Accessibility

Never use dark blue text on dark backgrounds. All terminal output, logging, and any future UI must meet WCAG 2.1 AA contrast ratios. Use cyan, yellow, green, white on dark backgrounds. Refer to the root `CLAUDE.md` for the full color palette.

---

## 3. PHASE 0: Foundation Hardening

**Timeline**: Week 1 (days 1–3) · **Effort**: 14 hours · **Dependencies**: None

Before building anything new, make sure the house is solid. This phase ensures the existing 213 tests pass, the overseer monitors what matters, and logging is structured for debugging.

### Task 0.1: Fix Overseer INV-4 (Coherence Delta Monitoring)

- **File**: `src/services/overseer.py`
- **Test**: `tests/test_overseer_inv4.py`
- **Time**: 2 hrs

INV-4 checks that coherence decline ≤5% per integration. Verify it is wired into `post_integration_check()`. If it fires, the system should quarantine the offending beliefs AND log which paper caused the decline. **Test**: integrate a paper that introduces a contradiction; confirm INV-4 fires and identifies the source.

### Task 0.2: Add Coverage Invariants INV-6 through INV-9

- **File**: `src/services/overseer.py`
- **Test**: `tests/test_overseer_coverage.py`
- **Time**: 4 hrs

These are the invariants the overseer was missing — the reason it didn't catch the 18/1,046 pipeline utilization problem or the orphaned theories:

- **INV-6**: Pipeline utilization — at least 1 paper processed per 7 days. Check `extraction_queue` for recent completions.
- **INV-7**: Template coverage — no theory with 0 linked templates. Query theory registry + template linkage.
- **INV-8**: Evidence diversity — each molecule sourced from ≥2 papers. Single-source molecules are fragile.
- **INV-9**: Annotation freshness — no template >90 days without a review annotation. Stale templates drift.

**Implementation advice**: Model these as methods on the Overseer class following the pattern of existing invariant checks. Each returns a list of violations. Wire them into `periodic_audit()` and `post_integration_check()` where appropriate. INV-6 only makes sense in `periodic_audit()`; INV-7 and INV-8 should run post-integration too.

### Task 0.3: Wire Pipeline Registry into overseer.db

- **Files**: `src/services/overseer.py`, `scripts/scheduled_pipeline.py`
- **Test**: `tests/test_pipeline_registry.py`
- **Time**: 3 hrs

The overseer has its own database (`overseer.db`, per Parnas information hiding). The pipeline should register each stage execution (discovery, triage, extract, tables, integrate) with timestamp, paper count, and outcome. This feeds INV-6 and enables trend analysis in Phase 4.

### Task 0.4: Run All 213 Existing Tests

- **Command**: `pytest tests/ -v --tb=short`
- **Time**: 2 hrs

Fix any failures. Do not skip or xfail tests without documenting why in `TASKS.md`. If a test is genuinely obsolete, remove it with a note. The goal is a fully green suite that serves as the regression baseline for all subsequent phases.

### Task 0.5: Add Structured JSON Logging

- **File**: `src/utils/logging_config.py` (NEW)
- **Test**: `tests/test_logging_config.py`
- **Time**: 3 hrs

Create a centralized logging configuration that outputs structured JSON. Every log entry should include: timestamp, level, module, message, and optional context dict. Wire it into the overseer, orchestrator, extraction pipeline, and notification service. Use Python's standard `logging` module with a custom `JSONFormatter`. This is essential for Phase 4's predictive health analysis.

> **Phase 0 Deliverable**: Green test suite + overseer monitoring utilization/coverage + structured logging.
> **Commit**: `"Phase 0: Foundation hardening — coverage invariants, pipeline registry, structured logging"`

---

## 4. PHASE 1: CVA Core Data Structures

**Timeline**: Week 1–2 (days 3–7) · **Effort**: 19 hours · **Dependencies**: Phase 0 complete

This phase creates the data models that all subsequent CVA work depends on. No computation yet — just dataclasses, enums, and type definitions. Get the data structures right and everything else follows.

### ADR-001: CVA is an Extension Layer

Write this ADR FIRST (`src/adr/ADR-001-cva-as-extension-not-replacement.md`). The decision: CVA data structures are optional metadata attached to templates and beliefs. Nothing in the existing system requires CVA to function. The fitness function: run all 213 existing tests with CVA modules imported but no CVA data present; all must pass.

### Task 1.1: CVAConstraint Dataclass (8 Constraints)

- **File**: `src/models/cva_constraint.py` (NEW, ~200 lines)
- **Test**: `tests/test_cva_constraint.py`
- **Time**: 3 hrs

Define `CVAConstraintVector` with 8 float fields (`processing_cost`, `load_rate`, `prediction_error`, `control_efficacy`, `affordance_density`, `social_cue_density`, `multisensory_coherence`, `narrative_coherence`), each normalized to [0, 1]. Include `tier` field (1 = universal primitive, 2 = ψ-calibrated), optional `psi` reference, and validation that values are in range. Add `from_tiers()` classmethod that combines Tier 1 and Tier 2 vectors. Add `distance()` method (Euclidean in constraint space) for attractor basin computation later. Add `to_dict()` and `from_dict()` for serialization.

### Task 1.2: CVAValuation Dataclass (9 Valuations + Auxiliary)

- **File**: `src/models/cva_valuation.py` (NEW, ~250 lines)
- **Test**: `tests/test_cva_valuation.py`
- **Time**: 3 hrs

Define `CVAValuationVector` with 9 core axes (SafetyValue, InterestValue, RestorationValue, StatusValue, BelongingValue, IdentityCongruenceValue, AutonomySupportValue, CompetenceSupportValue, RelatednessSupportValue) plus an `aux_valuations` dict for frame-specific axes (e.g., SacrednessValue, RitualFitValue). Include `CulturalValuationVariant` enum (`WESTERN`, `JAPANESE`, `WEST_AFRICAN`, `INDIAN`) and a factory method `from_culture()` that returns the appropriate dimensional structure.

For WEST_AFRICAN: Status + Belonging + Identity + Relatedness collapse into a single ÀṣàValue. For INDIAN: Rasa replaces Safety + Interest + Restoration.

**Implementation advice**: Use a common interface (e.g., `as_vector()` returning numpy array) regardless of variant, but allow the dimensionality to differ. The attractor engine (Phase 3) needs to work with vectors of varying dimension.

### Task 1.3: SubjectCharacteristics (ψ Parameter Space)

- **File**: `src/models/subject_characteristics.py` (NEW, ~350 lines)
- **Test**: `tests/test_subject_characteristics.py`
- **Time**: 4 hrs

This is the largest data model. Define `SubjectCharacteristics` with 6 components:

- `CulturalContext` (κ_self, κ_social, κ_aesthetics, κ_ecology)
- `NeurotypeProfile` (ν_sensory, ν_integration, ν_learning, ν_threat, ν_social, ν_reward)
- `DevelopmentalStage` (age, m_visual, m_motor, m_exec, m_social)
- `ExperienceProfile` (e_domain, e_years, e_mastery)
- `PsychologicalState` (ρ_fatigue, ρ_arousal, ρ_stress, ρ_affect)
- `TraitProfile` (τ_openness, τ_conscientiousness, τ_extraversion, τ_sensitivity, τ_risk)

Include **10 named neurotype factory methods**: `PTSD()`, `ASD()`, `ADHD()`, `DEPRESSION()`, `ANXIETY()`, `BIPOLAR_MANIC()`, `BIPOLAR_DEPRESSED()`, `ALZHEIMERS()`, `OLDER_ADULT()`, `GIFTED()`, `CHILD_5_12()`. Each returns a pre-configured `NeurotypeProfile` with the parameter values specified in `CVA_SUBJECT_CHARACTERISTICS_ARCHITECTURE_2026-02-28.md`. Also include `TYPICAL()` as the default/baseline.

Include `population_transfer_delta(source_psi, target_psi)` method that computes the δ discount factor per the formula in Section 5 of the architecture doc. This is critical for ATLAS integration.

### Task 1.4: ActivityFrame Enum + Precision Modulation

- **File**: `src/models/activity_frame.py` (NEW, ~100 lines)
- **Test**: `tests/test_activity_frame.py`
- **Time**: 2 hrs

Define `ActivityFrame` enum: `RESTING`, `STUDYING`, `SOCIALIZING`, `WORKING`, `EXPLORING`, `WORSHIPPING`, `HEALING`, `CREATING`, `NEGOTIATING`, `PLAYING`. Each has `precision_weights` (dict mapping valuation axis to gain multiplier) and `auxiliary_axes` (list of auxiliary valuations activated). This implements Chat's Q1 solution: ActivityFrame is precision modulation + prior shifting over a stable core with sparse auxiliaries.

### Task 1.5: Two-Tier Constraint Architecture

- **File**: `src/models/cva_constraint.py` (extend)
- **Test**: `tests/test_two_tier_constraints.py`
- **Time**: 3 hrs

Add `Tier1ConstraintVector` (6 universal primitives: edge_detection, motion_detection, figure_ground, luminance_contrast, temporal_coherence, symmetry_detection) and the Tier1-to-Tier2 mapping function. Tier 1 is invariant to ψ except for aging. Tier 2 is the existing 8-constraint vector, now explicitly derived from Tier 1 + ψ.

### Task 1.6: Cultural Valuation Variants

- **File**: `src/models/cva_valuation.py` (extend)
- **Test**: `tests/test_cultural_valuations.py`
- **Time**: 4 hrs

Implement the 4 cultural valuation structures from Section 2.2 of the architecture doc: Western (9D orthogonal), Japanese (Amae replaces Autonomy, Ma added), West African (Àṣà collapses 4 axes), Indian (Rasa + Dharma replace decomposed axes). **Test**: verify that each variant produces valid valuation vectors, that dimensionality matches specification, and that distance computations work across variants (using shared axes).

> **Phase 1 Deliverable**: All CVA data models with tests. All 213 original tests still green.
> **Commit**: `"Phase 1: CVA data structures — constraints, valuations, ψ, activity frames, cultural variants"`

---

## 5. PHASE 2: CVA Computation Engine

**Timeline**: Weeks 2–3 · **Effort**: 42 hours · **Dependencies**: Phase 1 complete

This is the largest and most mathematically demanding phase. You are implementing the computational heart of CVA: constraint inference, valuation computation, dynamics, and beauty readout.

**Key design insight from Chat's Three Hard Problems paper**: Constraints are not deterministic functions of features; they are context-conditioned latent inferences. Valuations are not static mappings; they are dynamical variables with coupled feedback.

### Task 2.1: Constraint Engine — c = f(x; θ(ψ))

- **File**: `src/services/cva_constraint_engine.py` (NEW, ~400 lines)
- **Test**: `tests/test_cva_engine.py`
- **Time**: 6 hrs

Implement `CVAConstraintEngine` with `compute_constraints(scene_features, activity_frame, psi)`. Internally: (a) compute Tier 1 universals from raw features, (b) calibrate θ(ψ) parameters using subject characteristics, (c) compute Tier 2 interpretive constraints via Tier 1 + θ(ψ) + activity frame. Start with deterministic MAP estimates; Task 2.3 upgrades to probabilistic.

**Implementation advice**: Use numpy arrays internally for constraint vectors. Each constraint function (`processing_cost`, `load_rate`, etc.) should be a separate method that takes Tier 1 inputs and θ parameters. This makes testing and debugging individual constraints straightforward. Include a `calibrate_theta(psi)` method that returns a dict of per-constraint parameters; the mapping from ψ to θ is specified in the table in Section 2.1 of the architecture doc.

### Task 2.2: Valuation Engine — v = V(c; g(ψ), τ(ψ), κ(ψ))

- **File**: `src/services/cva_valuation_engine.py` (NEW, ~350 lines)
- **Test**: `tests/test_valuation_engine.py`
- **Time**: 6 hrs

Implement `CVAValuationEngine` with `compute_valuations(constraints, activity_frame, psi)`. This maps the 8-constraint vector to the valuation space, using culture-selected structure, neurotype-modulated weights, and activity-frame precision. Use the sigmoid nonlinearity σ(c_i − θ) from the dynamics formalization for constraint-to-valuation coupling.

**Key**: The weight matrix W_{ji}(A) is activity-frame-dependent. RESTING amplifies RestorationValue and SafetyValue. STUDYING amplifies CompetenceSupportValue and ControlEfficacy. Each ActivityFrame has a `precision_weights` dict (from Task 1.4) that modulates the W matrix.

### Task 2.3: Recognition Model — c ~ p(c|x,A) (Chat's Q2)

- **File**: `src/services/cva_constraint_engine.py` (extend)
- **Test**: `tests/test_recognition_model.py`
- **Time**: 4 hrs

Upgrade the deterministic constraint computation to a probabilistic recognition model. Instead of c = f(x), compute c ~ p(c|x,A) where the posterior has mean = f(x; θ(ψ)) and precision = π(A). This means constraints have uncertainty, and that uncertainty varies with activity frame (exploring = lower precision on some constraints; resting = higher precision on safety-related constraints). For initial implementation, use Gaussian posteriors with diagonal covariance. Return both MAP estimate and uncertainty.

### Task 2.4: Decomposed Feedback (Chat's Q3)

- **File**: `src/services/cva_feedback.py` (NEW, ~200 lines)
- **Test**: `tests/test_decomposed_feedback.py`
- **Time**: 6 hrs

Implement the three feedback pathways from valuation to perception:

- **ε_attn** (sampling bias — valuations change what you look at)
- **ε_prec** (precision/gain — valuations change how you weight evidence)
- **ε_prior** (expectation shift — valuations change what you expect to see)

Each pathway has its own magnitude and timescale. The `CVAFeedback` class takes current valuations + activity frame and returns feedback terms that modify the next constraint computation. Wire into the dynamics loop (Task 2.6).

### Task 2.5: ActivityFrame Precision Modulation (Chat's Q1)

- **File**: `src/services/cva_valuation_engine.py` (extend)
- **Test**: `tests/test_activity_frame_modulation.py`
- **Time**: 4 hrs

Implement the "stable core + sparse auxiliary" model. The 9 core valuations are always present; their gains are modulated by activity frame (`precision_weights`). Sparse auxiliary axes (SacrednessValue for WORSHIPPING, RitualFitValue, etc.) are activated only in specific frames. **Test**: same constraint vector + different activity frames = different valuation profiles. RESTING + moderate constraints → high RestorationValue. NEGOTIATING + same constraints → high StatusValue.

### Task 2.6: Continuous-Time Dynamics

- **File**: `src/services/cva_dynamics.py` (NEW, ~500 lines)
- **Test**: `tests/test_cva_dynamics.py`
- **Time**: 8 hrs

**This is the most critical file.** Implement the coupled ODE system from Chat's Appendix A:

```
ċ = −D_c(c − f̃(x,A)) + φ_c(K_cc·c + K_cv·v)
v̇ = −D_v(v − Ṽ(c,A,τ,κ)) + φ_v(K_vv·v + K_vc·c)
```

Use Euler integration with adaptive step size. Timescale parameters: τ_c = 0.2s (constraints fast), τ_v = 2.0s (valuations slow). The cross-coupling matrices K_cv and K_vc implement feedback; K_vv implements valuation-valuation interactions (critical for attractors in Phase 3).

Include a `simulate(scene_features, psi, activity_frame, t_max=10.0, dt=0.01)` method that returns full trajectory.

**Implementation advice**: Use `scipy.integrate.solve_ivp` with RK45 for production; Euler for testing. Store trajectories as numpy arrays. Include convergence detection (stop when ||dv/dt|| < threshold).

### Task 2.7: Jacobian + Stability Analysis

- **File**: `src/services/cva_dynamics.py` (extend)
- **Test**: `tests/test_jacobian_stability.py`
- **Time**: 4 hrs

Compute the Jacobian of the coupled system at equilibrium. Verify eigenvalues have negative real parts (stability). Compute κ_loop = max(||K_cv|| · ||K_vc||) / (min eigenvalue product) — this is the separability metric. Target: κ_loop < 0.5 (Panel's requirement; current theoretical value ≈ 0.038). **Test**: for default parameters, κ_loop < 0.1; for pathological parameters (K_cv = K_vc = I), κ_loop > 1.0.

### Task 2.8: Beauty Readout — B = L(v)

- **File**: `src/services/cva_beauty.py` (NEW, ~200 lines)
- **Test**: `tests/test_beauty_models.py`
- **Time**: 4 hrs

Implement 4 beauty models:

1. **Linear**: B = β^T v
2. **Categorical/GMM**: B = argmax_k p(k|v) with learned mixture components
3. **KL-divergence**: B = −D_KL(v || v*_culture) where v* is the cultural prototype
4. **Residual-holistic**: B = α·g(F) + (1−α)·h(v) where F = formal properties

Start with Model 1 for testing; all 4 must be implemented and selectable.

> **Phase 2 Deliverable**: Full CVA computation pipeline: features → constraints → valuations → beauty. Dynamics converge for default parameters. κ_loop < 0.1. All 4 beauty models selectable.
> **Commit**: `"Phase 2: CVA computation engine — constraints, valuations, dynamics, beauty"`

---

## 6. PHASE 3: Attractor Engine

**Timeline**: Weeks 3–4 · **Effort**: 33 hours · **Dependencies**: Phase 2 complete

This phase implements David's key theoretical contribution: holistic aesthetic states (rasas) as attractors in the valuation dynamical system. The cross-coupling matrix K_vv creates the nonlinearity needed for multistability. Different cultural parameters κ(ψ) determine which attractors exist. The full formalization is in `RASA_AS_ATTRACTORS_CVA_DYNAMICS_2026-02-28.md`.

### Task 3.1: Fixed-Point Solver

- **File**: `src/services/cva_attractor.py` (NEW, ~600 lines)
- **Test**: `tests/test_attractor_solver.py`
- **Time**: 6 hrs

Implement `find_fixed_points(dynamics, scene_features, psi, activity_frame, n_starts=100)` that searches for all stable equilibria of the v̇ = 0 equation. Use multiple random initial conditions. Classify each fixed point as stable (all eigenvalues negative) or unstable. Return list of `AttractorState` objects (position in valuation space, eigenvalues, basin volume estimate).

### Task 3.2: Lyapunov Stability Analysis

- **Test**: `tests/test_lyapunov.py`
- **Time**: 4 hrs

For each fixed point, compute the Lyapunov function V(v) = (v − v*)^T P (v − v*) where P solves the Lyapunov equation J^T P + P J = −Q. This proves the basin of attraction exists and gives its local shape. Return the Lyapunov exponents.

### Task 3.3: Basin-of-Attraction Computation

- **Test**: `tests/test_basins.py`
- **Time**: 6 hrs

Estimate basin volumes by running many trajectories from random initial conditions and recording which attractor each converges to. Return a `BasinMap` object mapping each attractor to its basin volume (fraction of state space) and boundary geometry. This is computationally expensive; implement with configurable resolution (`n_trajectories` parameter, default 1000).

### Task 3.4: Nine Rasa Configurations

- **File**: `data/cva/rasa_attractors.json` (NEW)
- **Test**: `tests/test_rasa_configurations.py`
- **Time**: 3 hrs

Create the JSON file with the 9 classical rasa configurations from the formalization doc. Each rasa has a target valuation vector, expected basin size, and neuroscientific correlates:

- **Śānta** (peace): High Restoration, High Safety, Low Interest → stable rest state
- **Śṛṅgāra** (beauty/love): High Belonging, High Identity, moderate Interest → aesthetic engagement
- **Vīra** (heroism): High Competence, High Autonomy, moderate Status → active mastery
- **Raudra** (fury): inverted Safety, elevated Status → threat mobilization
- **Hāsya** (mirth): High Interest, moderate Social, low Processing → playful exploration
- **Karuṇā** (compassion): High Belonging, elevated Social → empathic engagement
- **Bībhatsa** (disgust): inverted Interest, elevated PredictionError → withdrawal
- **Bhayānaka** (fear): extreme Safety drive, suppressed all else → freeze/flight
- **Adbhuta** (wonder): extreme Interest, moderate PredictionError → sublime engagement

### Task 3.5: Cultural Attractor Variants

- **File**: `data/cva/cultural_attractors/` (NEW directory with 4 JSON files)
- **Test**: `tests/test_cultural_attractors.py`
- **Time**: 4 hrs

Create JSON files for each culture. Different κ values produce different attractor landscapes: Japanese aesthetics stabilize Ma-related attractors (serene emptiness) not present in Western space. West African Àṣà creates a collective-dignity attractor. Implement `get_attractors_for_culture(cultural_context)` that returns the culture-specific attractor set.

### Task 3.6: Attractor Transition Dynamics

- **Test**: `tests/test_transitions.py`
- **Time**: 6 hrs

Implement `compute_transitions(attractor_map, perturbation_range)` that models how the system moves between attractors when activity frame changes (frame switch = bifurcation). Show hysteresis: approaching a space from Śānta vs. from Raudra may settle in different attractors. This is the key empirical prediction.

### Task 3.7: Neurotype Basin Modulation

- **Test**: `tests/test_neurotype_basins.py`
- **Time**: 4 hrs

Implement `modulate_basins(attractor_map, neurotype_profile)` showing how neurotypes reshape basins: PTSD → enlarged Bhayānaka basin, shrunken Śānta basin. Depression → collapsed Vīra and Adbhuta basins. ASD → altered Hāsya basin. Use the neurotype profiles from Task 1.3.

> **Phase 3 Deliverable**: Working attractor engine. At least 5 stable rasas found for default parameters. Cultural variants produce different attractor sets. Neurotype modulation demonstrable.
> **Commit**: `"Phase 3: Attractor engine — rasas, basins, transitions, cultural variants"`

---

## 7. PHASE 4: Overseer Self-Healing Upgrade

**Timeline**: Weeks 4–5 · **Effort**: 32 hours · **Dependencies**: Phase 0 (invariants), Phase 2 (CVA stability)

Transform the overseer from a passive monitor into an active self-healing agent. Currently it detects violations, quarantines, and notifies. After this phase, it will also diagnose root causes, execute automated remediations for known patterns, learn which remediations succeed, predict violations before they occur, and monitor CVA-specific health.

### Task 4.1: Remediation Playbooks

- **File**: `src/services/overseer_playbooks.py` (NEW, ~400 lines)
- **Test**: `tests/test_playbooks.py`
- **Time**: 6 hrs

Create a `PLAYBOOKS` dict mapping each invariant code to a diagnosis function, remediation steps (tried in order), and escalation threshold. Key playbooks:

```python
PLAYBOOKS = {
    "INV-1": {  # Belief missing provenance
        "diagnose": "check_provenance_gap",
        "remediate": [
            "search_extraction_artifacts_for_source",
            "annotate_as_PROVENANCE_PATCH",
            "quarantine_if_unfound",
        ],
        "escalate_after": 3,
    },
    "INV-4": {  # Coherence decline > 5%
        "diagnose": "identify_conflicting_beliefs",
        "remediate": [
            "check_if_new_integration_caused_it",
            "rollback_if_recent_and_quality_low",
            "annotate_as_SENSITIVITY_FLAG_if_genuine_disagreement",
        ],
        "escalate_after": 1,  # Human immediately if rollback needed
    },
    "INV-6": {  # Pipeline utilization low
        "diagnose": "check_wishlist_and_gap_predictor",
        "remediate": [
            "run_gap_predictor_to_identify_targets",
            "add_top_5_gaps_to_wishlist",
            "trigger_discovery_stage",
        ],
        "escalate_after": 7,
    },
    "INV-7": {  # Theory with 0 templates
        "diagnose": "find_orphaned_theories",
        "remediate": [
            "search_existing_templates_for_implicit_links",
            "create_placeholder_templates_from_theory_definition",
            "annotate_as_OPEN_QUESTION",
        ],
        "escalate_after": 2,
    },
}
```

Playbooks must be conservative. Level 3 authority (auto-remediate) only for well-understood patterns. Unknown violations escalate to human immediately.

### Task 4.2: Auto-Remediation Engine

- **File**: `src/services/overseer.py` (extend)
- **Test**: `tests/test_auto_remediation.py`
- **Time**: 8 hrs

Extend overseer with a `_process_violations()` method that, for each detected violation: (a) runs the diagnosis function, (b) attempts remediation steps in order, (c) verifies the violation is resolved after each step, (d) logs all actions with timestamps and outcomes. If remediation succeeds, annotate the affected beliefs/templates with a `PROVENANCE_PATCH`. If it fails after all steps, escalate via notification service.

### Task 4.3: Learning Loop

- **Time**: 4 hrs

Track remediation success rates in `overseer.db`. For each invariant + remediation step: count attempts, count successes, compute success rate. If a remediation's success rate drops below 50% over the last 10 attempts, mark it as degraded and recommend review.

### Task 4.4: Predictive Health

- **File**: `src/services/overseer_predictive.py` (NEW, ~300 lines)
- **Test**: `tests/test_predictive_health.py`
- **Time**: 6 hrs

Use structured logs from Phase 0 + health metrics history to forecast next-day AESHI score. Simple implementation: linear trend on last 7 days + alert if predicted AESHI < 60. More sophisticated: detect patterns (coherence dips after bulk integration; utilization drops on weekends). Report predictions in the nightly report.

### Task 4.5: CVA-Aware Invariants INV-10 through INV-13

- **Time**: 4 hrs

Add 4 new invariants:

- **INV-10**: CVA constraint stability — κ_loop < 0.5 for all computed scenes
- **INV-11**: Attractor reachability — each named rasa reachable from at least one initial condition
- **INV-12**: Cultural variant consistency — each loaded cultural variant produces stable valuations
- **INV-13**: ψ-computation determinism — same ψ + same scene = same constraint vector (within tolerance 1e-6)

Wire into `periodic_audit()`.

### Task 4.6: Unified Nightly Report v3

- **File**: `scripts/overseer_nightly_v3.py` (NEW, ~400 lines)
- **Test**: `tests/test_nightly_v3.py`
- **Time**: 4 hrs

Runs all invariants (INV-0..INV-13), computes AESHI, checks pipeline utilization, template/theory coverage, annotation freshness, CVA stability, runs predictive health, executes playbooks for violations, generates unified report (JSON + markdown), and notifies if AESHI dropped >5 or new CRITICAL violations.

> **Phase 4 Deliverable**: Self-healing overseer with playbooks, auto-remediation, learning loop, predictive health, CVA invariants, nightly report v3.
> **Commit**: `"Phase 4: Self-healing overseer — playbooks, auto-remediation, predictive health"`

---

## 8. PHASE 5: QA Annotation Completion

**Timeline**: Week 5 · **Effort**: 20 hours · **Dependencies**: Phase 0 (annotation service exists)

### New Annotation Types (7)

Add to the existing `annotation_service.py`:

| Type | Purpose | Metadata Schema |
|------|---------|----------------|
| `MEASUREMENT_MODALITY` | HR, eye-tracking, fMRI, EDA, cortisol, self-report, behavioral | modality, measures[], temporal_resolution_ms, sample_size, equipment |
| `STIMULUS_DESCRIPTION` | Modality, abstraction level, parametric control, VR vs photo vs text | presentation_modality, abstraction_level, parametric_control, stimulus_count, duration_sec, cultural_origin |
| `MOLECULE_T15_LINK` | Enhanced molecule link with strength and direction | molecule_id, link_strength, direction, mechanism |
| `NEUROTYPE_RELEVANCE` | Which ψ_neuro profiles this finding applies to | neurotypes[], exclusions[], confidence |
| `CULTURAL_SCOPE` | Which ψ_culture profiles this finding was tested in | cultures[], generalizability, sample_description |
| `CVA_CONSTRAINT_MAP` | Which CVA constraints this template addresses | constraints[], strengths[], directions[] |
| `CVA_VALUATION_MAP` | Which CVA valuations this template affects | valuations[], weights[], mechanisms[] |

### Tasks

| # | Task | File | Time |
|---|------|------|------|
| 5.1 | Add MEASUREMENT_MODALITY annotation type | `annotation_service.py` | 3 hrs |
| 5.2 | Add STIMULUS_DESCRIPTION annotation type | `annotation_service.py` | 3 hrs |
| 5.3 | Add MOLECULE_T15_LINK annotation type (enhanced) | `annotation_service.py` | 2 hrs |
| 5.4 | Batch-annotate templates with measurement types | `scripts/batch_annotate_measurements.py` (NEW) | 4 hrs |
| 5.5 | Batch-annotate stimulus descriptions | `scripts/batch_annotate_stimuli.py` (NEW) | 4 hrs |
| 5.6 | Wire annotations into QA preprocessing | `src/qa/preprocessor.py` | 4 hrs |

Target: measurement + stimulus tags on ≥50% of the 209 templates.

> **Phase 5 Deliverable**: 17 annotation types operational. ≥50% templates tagged with measurement and stimulus info.
> **Commit**: `"Phase 5: QA annotations — measurement modality, stimulus descriptions, CVA maps"`

---

## 9. PHASE 6: New Molecules and Ontology

**Timeline**: Weeks 5–6 · **Effort**: 18 hours · **Dependencies**: Phase 1 (data models)

### New Molecules (5)

| Molecule | Contents | Parent T1.5 | Templates |
|----------|----------|-------------|-----------|
| **M-Rasa** | Holistic aesthetic-emotional states as attractors | aesthetics, appraisal | T-related to beauty, affect, emotion |
| **M-CulturalValuationStructure** | Culture-specific dimensional geometries | cross_cultural_psych | T-related to culture, preference |
| **M-AttractorTransition** | State change dynamics, mood shifts, frame changes | dynamical_systems | T-related to temporal dynamics |
| **M-BeautyAsCompression** | Aesthetic distance hypothesis, B = L(v) | berlyne_arousal, aesthetics | T-related to beauty, preference |
| **M-CCTPreference** | Color temperature cultural preferences | chronobiology, visual_comfort | T-related to lighting, visual comfort |

### Tasks

| # | Task | File | Time |
|---|------|------|------|
| 6.1 | Create M-Rasa molecule | `data/molecules/M_RASA.json` | 3 hrs |
| 6.2 | Create M-CulturalValuationStructure | `data/molecules/M_CULTURAL_VALUATION.json` | 3 hrs |
| 6.3 | Create M-AttractorTransition | `data/molecules/M_ATTRACTOR_TRANSITION.json` | 2 hrs |
| 6.4 | Create M-BeautyAsCompression | `data/molecules/M_BEAUTY_COMPRESSION.json` | 2 hrs |
| 6.5 | Create M-CCTPreference | `data/molecules/M_CCT_PREFERENCE.json` | 2 hrs |
| 6.6 | Link new molecules to existing templates | `molecule_linker.py` | 4 hrs |
| 6.7 | Register molecules with overseer | Overseer molecule tracking | 2 hrs |

> **Phase 6 Deliverable**: 5 new molecules created, linked, and registered.
> **Commit**: `"Phase 6: New molecules — Rasa, CulturalValuation, AttractorTransition, Beauty, CCT"`

---

## 10. PHASE 7: Integration Testing

**Timeline**: Weeks 6–7 · **Effort**: 26 hours · **Dependencies**: All prior phases

### Tests to Create

| # | Test | Type | Time |
|---|------|------|------|
| 7.1 | Paper → extraction → CVA annotation → integration | E2E | 6 hrs |
| 7.2 | Overseer detects CVA violation → auto-remediates | E2E | 4 hrs |
| 7.3 | Cultural variant switching (Western → Japanese) | E2E | 3 hrs |
| 7.4 | Attractor computation for 3 design scenarios | E2E | 4 hrs |
| 7.5 | 100 papers through pipeline, check health | Stress | 4 hrs |
| 7.6 | Overseer nightly v3 dry run | Manual | 2 hrs |
| 7.7 | Comprehensive system health report | Report | 3 hrs |

> **Phase 7 Deliverable**: All ~250+ tests green. AESHI > 70. System report generated.
> **Commit**: `"Phase 7: Integration testing — E2E, stress, system report"`

---

## 11. MASTER TIMELINE

| Week | Phase | Key Deliverable | Hours |
|------|-------|-----------------|-------|
| 1 | **Phase 0** | Foundation hardened, tests green, logging, INV-6..9 | 14 |
| 1–2 | **Phase 1** | CVA data models + ψ + cultural variants | 19 |
| 2–3 | **Phase 2** | CVA computation engine (constraints, valuations, dynamics) | 42 |
| 3–4 | **Phase 3** | Attractor engine (rasas, basins, transitions) | 33 |
| 4–5 | **Phase 4** | Self-healing overseer (playbooks, prediction) | 32 |
| 5 | **Phase 5** | QA annotations (measurement, stimulus, molecule) | 20 |
| 5–6 | **Phase 6** | 5 new molecules registered and linked | 18 |
| 6–7 | **Phase 7** | Integration + stress tests, system report | 26 |
| | **TOTAL** | | **204 hrs** |

---

## 12. DEFINITION OF DONE

The system is "living" when ALL of the following hold:

| # | Criterion | Measurement | Phase |
|---|-----------|-------------|-------|
| 1 | All ~250+ tests pass (213 existing + ~40 new) | `pytest` exit 0 | 7 |
| 2 | AESHI health score > 70 | Nightly report | 4 |
| 3 | Pipeline running: ≥1 paper/week | INV-6 | 0 |
| 4 | CVA computable: constraint + valuation vectors for any template | Unit tests | 2 |
| 5 | At least 5 rasa-like attractors with computed basins | Attractor tests | 3 |
| 6 | ≥3 invariant violations auto-remediated successfully | Overseer log | 4 |
| 7 | All 17 annotation types operational; 50% templates tagged | Query count | 5 |
| 8 | 5 new molecules linked to templates | Molecule registry | 6 |
| 9 | Overseer nightly v3 generating daily reports | Report exists | 4 |
| 10 | 4 cultural valuation structures loaded and tested | Cultural tests | 1 |

---

## 13. RISK REGISTER

| Risk | Impact | Mitigation |
|------|--------|------------|
| CVA computation too slow | MEDIUM | Offline computation + caching. Pre-compute attractors for common ψ profiles. Lazy evaluation. |
| Attractor solver doesn't converge | MEDIUM | Multiple starting points (n_starts=100). Fallback to MAP estimates. Adaptive step size. |
| Existing tests break during CVA addition | LOW | Strangler fig pattern. CVA is opt-in. Run full suite after every task. |
| Auto-remediation makes things worse | HIGH | Conservative playbooks. Level 3 only for known patterns. Fast human escalation. |
| ψ space too large to test exhaustively | MEDIUM | Representative profiles: 10 neurotypes × 4 cultures × 3 ages = 120 combos. |

---

## 14. NEW FILE INVENTORY (Complete)

| Phase | File | Type | Est. Lines |
|-------|------|------|-----------|
| 0 | `src/utils/logging_config.py` | NEW | ~100 |
| 1 | `src/models/cva_constraint.py` | NEW | ~200 |
| 1 | `src/models/cva_valuation.py` | NEW | ~250 |
| 1 | `src/models/subject_characteristics.py` | NEW | ~350 |
| 1 | `src/models/activity_frame.py` | NEW | ~100 |
| 2 | `src/services/cva_constraint_engine.py` | NEW | ~400 |
| 2 | `src/services/cva_valuation_engine.py` | NEW | ~350 |
| 2 | `src/services/cva_feedback.py` | NEW | ~200 |
| 2 | `src/services/cva_dynamics.py` | NEW | ~500 |
| 2 | `src/services/cva_beauty.py` | NEW | ~200 |
| 3 | `src/services/cva_attractor.py` | NEW | ~600 |
| 3 | `data/cva/rasa_attractors.json` | NEW | ~200 |
| 3 | `data/cva/cultural_attractors/*.json` | NEW | ~400 |
| 4 | `src/services/overseer_playbooks.py` | NEW | ~400 |
| 4 | `src/services/overseer_predictive.py` | NEW | ~300 |
| 4 | `scripts/overseer_nightly_v3.py` | NEW | ~400 |
| 5 | `scripts/batch_annotate_measurements.py` | NEW | ~150 |
| 5 | `scripts/batch_annotate_stimuli.py` | NEW | ~150 |
| 7 | `scripts/generate_system_report.py` | NEW | ~200 |
| — | Tests (~40 new test files) | NEW | ~3,000 |
| — | ADR records (~10) | NEW | ~500 |
| **TOTAL** | ~22 new files + 40 test files + 10 ADRs | | **~8,250** |

---

## 15. FINAL INSTRUCTIONS

AG, you have the specification, the reference documents, the task breakdown, and the timeline. Here is what David expects:

**Speed**: Work as fast as you can while maintaining test quality. Every phase should end with a git commit. Don't over-engineer; get working code first, then refine.

**Communication**: Update `TASKS.md` at the end of each phase. If you encounter a design ambiguity, note it in the ADR and make a reasonable choice — don't block waiting for clarification unless it's a high-risk decision.

**Testing**: Every task has a test file. Write it. Run it. Green = proceed. The test suite is the contract. It's also how David knows the system works without reading every line of code.

**The goal**: At the end of 7 weeks, ATLAS should be a living, self-healing system that computes constraint-valuation architectures, identifies aesthetic attractors, respects cultural and neurotype diversity, monitors its own health, and heals itself when things go wrong. That's the standard. Meet it.

---

*Assigned by Professor David Kirsh · UCSD Cognitive Science · February 28, 2026*
