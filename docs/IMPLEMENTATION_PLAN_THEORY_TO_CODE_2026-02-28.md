# ATLAS Implementation Plan: From Theory to Living, Self-Healing System

**Date**: February 28, 2026
**Author**: Cowork Session 12 (continued)
**Purpose**: Practical plan to translate accumulated theoretical work into tested, integrated, overseer-managed code
**Status**: ACTIONABLE — all prerequisites met
**Audience**: David Kirsh, AG (implementation), Chat (theory review)

---

## 1. THE GAP: THEORY vs. CODE

### What We Have in Theory (Docs, ~15,000 lines of specification)

| Document | Key Concepts | Lines | Code Representation |
|----------|-------------|-------|-------------------|
| RASA_AS_ATTRACTORS_CVA_DYNAMICS | Attractor formalization, 9 rasas mapped, Lyapunov stability, 4 new molecules | ~2,800 | **0%** |
| CVA_SUBJECT_CHARACTERISTICS_ARCHITECTURE | ψ parameter space, 10 neurotype profiles, two-tier constraints | ~1,240 | **0%** |
| THREE_HARD_PROBLEMS_EXPERT_PANEL | Recognition model c~p(c|x,A), decomposed feedback, panel recommendations | ~621 | **0%** |
| CVA_CULTURE_AWARE_ARCHITECT_PANEL | Culture-parametric valuations, amae/àṣà/rasa variants | ~1,385 | **0%** |
| CONSTRAINT_UNIVERSALITY_REVIEW | Two-tier constraint evidence, 30+ citations | ~775 | **0%** |
| WEB_CONNECTIVITY_AUDIT | Annotation schema, connectivity gaps, pipeline utilization | ~217 | **~70%** (annotation service exists) |
| SPRINT_INTEGRATION_WEB_CONNECTIVITY | Unified sprint plan, 10 decisions | ~400 | **0%** (plan only) |
| CVA_SPECIALIZED_PANELS (4 panels) | Cultural sorting, architect evaluation, math formalization | ~1,489 | **0%** |
| CVA_PANEL_RECONVENE | 11 ADOPT PARTIALLY, empirical requirements | ~297 | **0%** |

### What We Have in Code (Working Infrastructure)

| Component | Status | Maturity |
|-----------|--------|----------|
| Web of Belief (Quinean coherentism) | **WORKING** | Mature |
| Overseer (6 invariants, health monitoring) | **WORKING** | Mature |
| 14-Step Paper Integration Orchestrator | **WORKING** | Complete |
| Extraction Pipeline (Gemini) | **WORKING** | Production |
| Notification Service | **WORKING** | Complete |
| Extraction Approval (HITL gate) | **WORKING** | Complete |
| Annotation Service (10 types, 3 layers) | **WORKING** | Complete |
| 209 Calibrated Templates | **LOADED** | Complete |
| 50+ Theories | **LOADED** | Complete |
| Molecules (Tier 2) | **SCHEMA DONE** | Population ongoing |
| BN Integration | **WORKING** | Parameter inference |
| 213 Test Files | **GOOD** | ~75% coverage |

### The Critical Disconnect

The theory documents describe a system that is epistemically richer, culturally aware, dynamically modeled, and self-healing. The code describes a system that is epistemically solid, culturally blind, statically organized, and human-monitored. Bridging this gap requires a disciplined, incremental approach — not a rewrite, but a series of well-tested extensions to working infrastructure.

---

## 2. BEST PRACTICES FOR LIVING, SELF-HEALING KNOWLEDGE SYSTEMS

Drawing from software engineering best practices (Architecture Decision Records, fitness functions, observability engineering) and from the scientific knowledge management literature, the following principles should govern our implementation:

### 2.1 Architecture Decision Records (ADRs)

Every implementation decision gets a lightweight record (Nygard, 2011). We already have `docs/*_DECISIONS_LOG.md` files; we formalize this into the codebase:

```
src/adr/
  ADR-001-cva-as-extension-not-replacement.md
  ADR-002-attractor-computation-offline.md
  ADR-003-psi-as-metadata-not-schema-change.md
  ...
```

Each ADR: Context → Decision → Consequences → Fitness Function (how to test the decision holds).

### 2.2 Fitness Functions (Automated Decision Verification)

For every architectural decision, write an automated test that verifies the decision is still being honored. These run in CI alongside unit tests:

```python
# tests/fitness/test_adr_001_cva_extends_web.py
def test_cva_does_not_break_existing_web_operations():
    """ADR-001: CVA is an extension layer, not a replacement."""
    web = WebOfBelief(...)
    web.accept(belief, reason)  # Must work without CVA
    assert web.get_global_coherence() > 0.5

    cva = CVALayer(web)  # CVA wraps, doesn't replace
    cva.compute_constraints(scene)
    assert web.get_global_coherence() > 0.5  # Web still works
```

### 2.3 Self-Healing Pattern: Detect → Diagnose → Remediate → Learn

The overseer currently does Detect (invariant violations) and partially Diagnose (quarantine). We need to add:

- **Remediate**: Automated corrective actions for known violation patterns
- **Learn**: Track which remediations succeed, adjust thresholds over time

Implementation: Remediation playbooks (predefined response sequences for each invariant violation type).

### 2.4 Observability Triad: Metrics + Logs + Traces

- **Metrics**: AESHI score, per-theory coherence, pipeline throughput, template coverage
- **Logs**: Structured JSON logs for every integration event, annotation, notification
- **Traces**: Paper-level trace from discovery → triage → extraction → approval → integration → health check

### 2.5 Incremental Extension (Strangler Fig Pattern)

New theoretical capabilities (CVA, ψ-space, attractors) are implemented as **layers that wrap existing infrastructure**, not as replacements. The existing Quinean web continues to work unchanged; CVA adds interpretive structure on top.

---

## 3. IMPLEMENTATION PHASES

### Phase 0: Foundation Hardening (AG — 1 week)

**Goal**: Ensure existing infrastructure is solid before extending.

| Task | Owner | Files | Test | Time |
|------|-------|-------|------|------|
| **0.1** Fix Overseer INV-4 (coherence delta monitoring) | AG | `src/services/overseer.py` | `tests/test_overseer_inv4.py` | 2 hrs |
| **0.2** Add coverage invariants INV-6..INV-9 | AG | `src/services/overseer.py` | `tests/test_overseer_coverage.py` | 4 hrs |
| **0.3** Wire pipeline registry into overseer.db | AG | `src/services/overseer.py`, `scripts/scheduled_pipeline.py` | `tests/test_pipeline_registry.py` | 3 hrs |
| **0.4** Run ALL 213 existing tests, fix any failures | AG | `tests/` | Green suite | 2 hrs |
| **0.5** Add structured JSON logging throughout | AG | `src/utils/logging_config.py` (new) | Log format tests | 3 hrs |

**New Overseer Invariants**:

```python
# INV-6: Pipeline utilization — at least 1 paper processed per 7 days
# INV-7: Template coverage — no theory with 0 linked templates
# INV-8: Evidence diversity — each molecule sourced from ≥2 papers
# INV-9: Annotation freshness — no template >90 days without review annotation
```

**Fitness Function**: `tests/fitness/test_phase0_foundation.py` — runs all invariants, checks pipeline registry populated.

**Deliverable**: Green test suite + overseer monitoring utilization/coverage + structured logging.

---

### Phase 1: CVA Core Data Structures (Cowork + AG — 1 week)

**Goal**: Implement CVA constraint and valuation data models as extensions to existing template/belief system.

**ADR-001**: CVA is an extension layer. Templates and beliefs continue to work without CVA. CVA adds constraint vectors and valuation vectors as optional metadata.

| Task | Owner | Files | Test | Time |
|------|-------|-------|------|------|
| **1.1** `CVAConstraint` dataclass (8 constraints) | Cowork spec → AG impl | `src/models/cva_constraint.py` (new) | `tests/test_cva_constraint.py` | 3 hrs |
| **1.2** `CVAValuation` dataclass (9 valuations + aux) | Cowork spec → AG impl | `src/models/cva_valuation.py` (new) | `tests/test_cva_valuation.py` | 3 hrs |
| **1.3** `SubjectCharacteristics` (ψ parameter space) | Cowork spec → AG impl | `src/models/subject_characteristics.py` (new) | `tests/test_subject_characteristics.py` | 4 hrs |
| **1.4** `ActivityFrame` enum + precision modulation | Cowork spec → AG impl | `src/models/activity_frame.py` (new) | `tests/test_activity_frame.py` | 2 hrs |
| **1.5** Two-tier constraint architecture (Tier 1 universal, Tier 2 ψ-calibrated) | Cowork spec → AG impl | `src/models/cva_constraint.py` (extend) | `tests/test_two_tier_constraints.py` | 3 hrs |
| **1.6** Cultural valuation variants (Western, Japanese, West African, Indian) | Cowork spec → AG impl | `src/models/cva_valuation.py` (extend) | `tests/test_cultural_valuations.py` | 4 hrs |

**Key Design Decisions**:

```python
# ADR-001: CVA wraps, doesn't replace
@dataclass
class CVAConstraintVector:
    """8-dimensional constraint vector, optionally attached to a Template or Scene."""
    processing_cost: float       # [0, 1] normalized
    load_rate: float
    prediction_error: float
    control_efficacy: float
    affordance_density: float
    social_cue_density: float
    multisensory_coherence: float
    narrative_coherence: float
    tier: int = 2                # 1 = universal primitive, 2 = ψ-calibrated
    psi: Optional[SubjectCharacteristics] = None  # if tier 2

@dataclass
class SubjectCharacteristics:
    """ψ parameter space — modulates all CVA layers."""
    culture: CulturalContext
    neurotype: NeurotypeProfile
    development: DevelopmentalStage
    experience: ExperienceProfile
    state: PsychologicalState
    trait: TraitProfile
```

**Fitness Function**: `tests/fitness/test_adr001_cva_extends_web.py` — existing web operations work with and without CVA layer.

**Deliverable**: Data models + tests. No behavioral changes to existing system.

---

### Phase 2: CVA Computation Engine (AG — 2 weeks)

**Goal**: Implement the constraint and valuation computation, including dynamics.

| Task | Owner | Files | Test | Time |
|------|-------|-------|------|------|
| **2.1** Constraint computation: c = f(x; θ(ψ)) | AG | `src/services/cva_constraint_engine.py` (new) | `tests/test_cva_engine.py` | 6 hrs |
| **2.2** Valuation computation: v = V(c; g(ψ), τ(ψ), κ(ψ)) | AG | `src/services/cva_valuation_engine.py` (new) | `tests/test_valuation_engine.py` | 6 hrs |
| **2.3** Recognition model: c ~ p(c|x,A) (Chat's Q2) | AG | `src/services/cva_constraint_engine.py` (extend) | `tests/test_recognition_model.py` | 4 hrs |
| **2.4** Decomposed feedback: ε_attn, ε_prec, ε_prior (Chat's Q3) | AG | `src/services/cva_feedback.py` (new) | `tests/test_decomposed_feedback.py` | 6 hrs |
| **2.5** ActivityFrame precision modulation (Chat's Q1) | AG | `src/services/cva_valuation_engine.py` (extend) | `tests/test_activity_frame_modulation.py` | 4 hrs |
| **2.6** Continuous-time dynamics: ċ, v̇ equations with Euler integration | AG | `src/services/cva_dynamics.py` (new) | `tests/test_cva_dynamics.py` | 8 hrs |
| **2.7** Jacobian computation + stability analysis (κ_loop) | AG | `src/services/cva_dynamics.py` (extend) | `tests/test_jacobian_stability.py` | 4 hrs |
| **2.8** Beauty readout: B = L(v) with 4 models | AG | `src/services/cva_beauty.py` (new) | `tests/test_beauty_models.py` | 4 hrs |

**Key Implementation Detail** (from Chat's Three Hard Problems):

```python
class CVAConstraintEngine:
    """Implements c ~ p(c|x,A) — context-conditioned recognition model."""

    def compute_constraints(self, scene_features: np.ndarray,
                           activity_frame: ActivityFrame,
                           psi: SubjectCharacteristics) -> CVAConstraintVector:
        # Tier 1: Universal primitives (invariant to ψ except aging)
        c_tier1 = self._compute_tier1(scene_features, psi.development.age)

        # Tier 2: ψ-calibrated interpretive constraints
        theta = self._calibrate_theta(psi)  # θ(ψ)
        c_tier2 = self._compute_tier2(c_tier1, scene_features, theta, activity_frame)

        return CVAConstraintVector.from_tiers(c_tier1, c_tier2, psi=psi)

    def _compute_tier2(self, c_tier1, x, theta, A):
        """Context-conditioned recognition: c ~ p(c|x,A) not c = f(x)."""
        # Mean of recognition distribution
        c_mean = self._recognition_mean(c_tier1, x, theta, A)
        # Precision from activity frame
        precision = self._frame_precision(A)
        # Sample (or return MAP estimate)
        return c_mean  # MAP for deterministic mode
```

**Fitness Function**: `tests/fitness/test_cva_computation.py` — constraint vectors computed, valuations stable, dynamics converge.

---

### Phase 3: Attractor Engine (AG — 1.5 weeks)

**Goal**: Implement the rasa-as-attractors dynamical system.

| Task | Owner | Files | Test | Time |
|------|-------|-------|------|------|
| **3.1** Fixed-point solver for v̇ = 0 | AG | `src/services/cva_attractor.py` (new) | `tests/test_attractor_solver.py` | 6 hrs |
| **3.2** Lyapunov stability analysis for fixed points | AG | `src/services/cva_attractor.py` (extend) | `tests/test_lyapunov.py` | 4 hrs |
| **3.3** Basin-of-attraction computation | AG | `src/services/cva_attractor.py` (extend) | `tests/test_basins.py` | 6 hrs |
| **3.4** 9 rasa configurations as named attractors | AG | `data/cva/rasa_attractors.json` (new) | `tests/test_rasa_configurations.py` | 3 hrs |
| **3.5** Cultural attractor variants (κ → attractor set) | AG | `data/cva/cultural_attractors/` (new) | `tests/test_cultural_attractors.py` | 4 hrs |
| **3.6** Attractor transition dynamics (bifurcation tracking) | AG | `src/services/cva_attractor.py` (extend) | `tests/test_transitions.py` | 6 hrs |
| **3.7** Neurotype basin modulation (ψ_neuro → basin sizes) | AG | `src/services/cva_attractor.py` (extend) | `tests/test_neurotype_basins.py` | 4 hrs |

**Deliverable**: Working attractor engine that computes stable aesthetic states, their basins, and transitions. Testable against known rasa configurations.

---

### Phase 4: Overseer Self-Healing Upgrade (AG — 1.5 weeks)

**Goal**: Transform the overseer from monitor to active self-healing system.

| Task | Owner | Files | Test | Time |
|------|-------|-------|------|------|
| **4.1** Remediation playbooks for each invariant | AG | `src/services/overseer_playbooks.py` (new) | `tests/test_playbooks.py` | 6 hrs |
| **4.2** Auto-remediation engine (detect → diagnose → act) | AG | `src/services/overseer.py` (extend) | `tests/test_auto_remediation.py` | 8 hrs |
| **4.3** Learning loop (track remediation success rates) | AG | `src/services/overseer.py` (extend) | `tests/test_remediation_learning.py` | 4 hrs |
| **4.4** Predictive health (trend analysis, AESHI forecasting) | AG | `src/services/overseer_predictive.py` (new) | `tests/test_predictive_health.py` | 6 hrs |
| **4.5** CVA-aware invariants (INV-10..INV-13) | AG | `src/services/overseer.py` (extend) | `tests/test_cva_invariants.py` | 4 hrs |
| **4.6** Unified nightly report v3 (includes CVA health) | AG | `scripts/overseer_nightly_v3.py` (new) | `tests/test_nightly_v3.py` | 4 hrs |

**Remediation Playbooks**:

```python
PLAYBOOKS = {
    "INV-1": {  # Belief missing provenance
        "diagnose": "check_provenance_gap",
        "remediate": [
            "search_extraction_artifacts_for_source",  # Try to find source
            "annotate_as_PROVENANCE_PATCH",            # If found, patch
            "quarantine_if_unfound",                    # If not, quarantine
        ],
        "escalate_after": 3,  # Human after 3 failed attempts
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
        "escalate_after": 7,  # Human if no papers found after 7 days
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

**New CVA Invariants**:

```python
# INV-10: CVA constraint stability — κ_loop < 0.5 for all computed scenes
# INV-11: Attractor reachability — each named rasa reachable from at least one initial condition
# INV-12: Cultural variant consistency — each loaded cultural variant produces stable valuations
# INV-13: ψ-computation determinism — same ψ + same scene = same constraint vector (within tolerance)
```

**Deliverable**: Self-healing overseer that automatically remediates known violations, tracks success, and predicts health trends.

---

### Phase 5: QA Annotation Completion (Cowork spec + AG impl — 1 week)

**Goal**: Complete the annotation taxonomy with measurement modality, stimulus description, and molecule/T1.5 tags.

| Task | Owner | Files | Test | Time |
|------|-------|-------|------|------|
| **5.1** Add MEASUREMENT_MODALITY annotation type | AG | `src/services/annotation_service.py` | `tests/test_measurement_annotations.py` | 3 hrs |
| **5.2** Add STIMULUS_DESCRIPTION annotation type | AG | `src/services/annotation_service.py` | `tests/test_stimulus_annotations.py` | 3 hrs |
| **5.3** Add MOLECULE_T15_LINK annotation type (enhanced) | AG | `src/services/annotation_service.py` | `tests/test_molecule_annotations.py` | 2 hrs |
| **5.4** Batch-annotate existing templates with measurement types | AG | `scripts/batch_annotate_measurements.py` (new) | Spot-check 20 templates | 4 hrs |
| **5.5** Batch-annotate stimulus descriptions from extraction artifacts | AG | `scripts/batch_annotate_stimuli.py` (new) | Spot-check 20 templates | 4 hrs |
| **5.6** Wire annotations into QA preprocessing | AG | `src/qa/preprocessor.py` | `tests/test_qa_with_annotations.py` | 4 hrs |

**New Annotation Types**:

```python
class AnnotationType(Enum):
    # Existing (10 types)...

    # NEW: Scientific measurement annotations
    MEASUREMENT_MODALITY = "MEASUREMENT_MODALITY"    # HR, eye-tracking, fMRI, EDA, cortisol, self-report, behavioral
    STIMULUS_DESCRIPTION = "STIMULUS_DESCRIPTION"    # Modality, abstraction level, parametric control, VR vs photo vs text
    MOLECULE_T15_LINK = "MOLECULE_T15_LINK"          # Enhanced: includes molecule ID, link strength, direction
    NEUROTYPE_RELEVANCE = "NEUROTYPE_RELEVANCE"      # Which ψ_neuro profiles this finding applies to
    CULTURAL_SCOPE = "CULTURAL_SCOPE"                # Which ψ_culture profiles this finding was tested in
    CVA_CONSTRAINT_MAP = "CVA_CONSTRAINT_MAP"        # Which CVA constraints this template addresses
    CVA_VALUATION_MAP = "CVA_VALUATION_MAP"          # Which CVA valuations this template affects
```

**Metadata Schema for MEASUREMENT_MODALITY**:
```json
{
    "modality": "eye_tracking",
    "measures": ["fixation_duration", "saccade_frequency", "pupil_dilation"],
    "temporal_resolution_ms": 1,
    "spatial_resolution": "foveal",
    "sample_size": 45,
    "equipment": "Tobii Pro Spectrum"
}
```

**Metadata Schema for STIMULUS_DESCRIPTION**:
```json
{
    "presentation_modality": "VR_immersive",
    "abstraction_level": "concrete_scene",
    "parametric_control": "high",
    "stimulus_count": 24,
    "duration_sec": 60,
    "cultural_origin": "Western_modernist",
    "description": "360-degree walkthrough of minimalist hospital room"
}
```

---

### Phase 6: New Molecules and Ontology (Cowork + AG — 1 week)

**Goal**: Add the 4 new molecules identified in rasa-as-attractors work plus resolve beauty/CVA molecules.

| Task | Owner | Files | Test | Time |
|------|-------|-------|------|------|
| **6.1** Create M-Rasa molecule (holistic aesthetic states) | Cowork spec → AG | `data/molecules/M_RASA.json` | `tests/test_molecule_rasa.py` | 3 hrs |
| **6.2** Create M-CulturalValuationStructure molecule | Cowork spec → AG | `data/molecules/M_CULTURAL_VALUATION.json` | Test | 3 hrs |
| **6.3** Create M-AttractorTransition molecule | Cowork spec → AG | `data/molecules/M_ATTRACTOR_TRANSITION.json` | Test | 2 hrs |
| **6.4** Create M-BeautyAsCompression molecule | Cowork spec → AG | `data/molecules/M_BEAUTY_COMPRESSION.json` | Test | 2 hrs |
| **6.5** Create M-CCTPreference molecule (color temp, see lighting finding) | Cowork spec → AG | `data/molecules/M_CCT_PREFERENCE.json` | Test | 2 hrs |
| **6.6** Link new molecules to existing templates | AG | `src/qa/molecules/molecule_linker.py` | `tests/test_new_molecule_links.py` | 4 hrs |
| **6.7** Register molecules with overseer | AG | Overseer molecule tracking | Test | 2 hrs |

---

### Phase 7: Integration Testing and Overseer Management (AG — 1 week)

**Goal**: End-to-end testing of the full extended system under overseer management.

| Task | Owner | Files | Test | Time |
|------|-------|-------|------|------|
| **7.1** Integration test: paper → extraction → CVA annotation → integration | AG | `tests/integration/test_full_pipeline_with_cva.py` | E2E | 6 hrs |
| **7.2** Integration test: overseer detects CVA invariant violation → auto-remediates | AG | `tests/integration/test_self_healing.py` | E2E | 4 hrs |
| **7.3** Integration test: cultural variant switching (Western → Japanese) | AG | `tests/integration/test_cultural_switch.py` | E2E | 3 hrs |
| **7.4** Integration test: attractor computation for 3 design scenarios | AG | `tests/integration/test_attractor_scenarios.py` | E2E | 4 hrs |
| **7.5** Stress test: 100 papers through pipeline, check health | AG | `tests/stress/test_bulk_integration.py` | Perf | 4 hrs |
| **7.6** Overseer nightly v3 dry run | AG | `scripts/overseer_nightly_v3.py --dry-run` | Manual | 2 hrs |
| **7.7** Generate comprehensive system health report | AG | `scripts/generate_system_report.py` (new) | Manual | 3 hrs |

---

## 4. NEW FILE INVENTORY

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

## 5. OVERSEER MANAGEMENT CONTROL: THE LIVING SYSTEM

### 5.1 What "Living" Means

A living system:
1. **Grows**: New papers → new beliefs → new constraints → new valuations → new attractors
2. **Heals**: Violations detected → diagnosed → remediated → learned from
3. **Reports**: Daily health reports with trends, predictions, action items
4. **Adapts**: Remediation playbooks evolve based on success rates
5. **Governs**: Overseer has authority to quarantine, rollback, notify, and (for low-risk actions) auto-fix

### 5.2 Overseer Authority Levels

```
Level 0 (MONITOR):  Detect and log. Current state.
Level 1 (NOTIFY):   Detect, log, and notify human. Current for most violations.
Level 2 (ANNOTATE): Detect, log, notify, and create annotation. Phase 5 target.
Level 3 (REMEDIATE): Detect, diagnose, auto-fix for known patterns. Phase 4 target.
Level 4 (PREVENT):  Predict violations before they occur. Phase 4.4 target.
Level 5 (EVOLVE):   Modify own playbooks based on learning. Future phase.
```

### 5.3 Daily Health Cycle

```
06:00  Overseer nightly v3 runs
         ├── Run all invariants (INV-0..INV-13)
         ├── Compute AESHI score
         ├── Check pipeline utilization (INV-6)
         ├── Check template/theory coverage (INV-7)
         ├── Check annotation freshness (INV-9)
         ├── Check CVA stability (INV-10..INV-13) [Phase 4+]
         ├── Run predictive health model
         ├── Execute playbooks for any violations
         ├── Generate unified report (JSON + markdown)
         └── Notify if AESHI dropped >5 or new CRITICAL violations

08:00  David reviews report (or summary notification)
         ├── Approve/override any remediation actions
         └── Flag items for deeper attention

Continuous:
         ├── Pipeline processes new papers (discovery → integration)
         ├── Post-integration checks run after each paper
         └── Real-time coherence monitoring
```

### 5.4 Observability Dashboard (Future Phase)

While a full web UI is deferred, the immediate deliverable is CLI-based observability:

```bash
# System status (one-line summary)
python scripts/atlas_status.py

# Full health report
python scripts/overseer_nightly_v3.py --report

# Pipeline status
python scripts/scheduled_pipeline.py status

# Pending notifications
python scripts/check_notifications.py pending

# CVA attractor landscape for a scene
python scripts/cva_query.py --scene hospital_room --culture japanese --neurotype typical

# Recent remediation actions
python scripts/overseer_query.py remediations --last 7d
```

---

## 6. TIMELINE

| Week | Phase | Key Deliverable | Owner |
|------|-------|-----------------|-------|
| 1 | **Phase 0** | Foundation hardened, tests green, structured logging | AG |
| 1-2 | **Phase 1** | CVA data models + ψ parameter space | Cowork spec → AG |
| 2-3 | **Phase 2** | CVA computation engine (constraints, valuations, dynamics) | AG |
| 3-4 | **Phase 3** | Attractor engine (rasa, basins, transitions) | AG |
| 4-5 | **Phase 4** | Self-healing overseer (playbooks, auto-remediation, prediction) | AG |
| 5 | **Phase 5** | QA annotations complete (measurement, stimulus, molecule) | Cowork spec → AG |
| 5-6 | **Phase 6** | New molecules and ontology registered | Cowork spec → AG |
| 6-7 | **Phase 7** | Integration testing, stress testing, system report | AG |

**Total**: ~7 weeks for full implementation. Phases can overlap where dependencies allow.

---

## 7. RISK REGISTER

| Risk | Impact | Mitigation |
|------|--------|------------|
| CVA computation too slow for real-time | Medium | Offline computation + caching; attractor pre-computation |
| Attractor solver doesn't converge | Medium | Fallback to MAP estimates; multiple starting points |
| Existing tests break during CVA addition | Low | Strangler fig pattern; CVA is opt-in |
| Auto-remediation makes things worse | High | Conservative: only Level 3 for well-understood violations; human escalation fast |
| 1,046 papers overwhelm extraction pipeline | Medium | Batch processing with rate limits; quality triage first |
| ψ parameter space too large to test exhaustively | Medium | Representative profiles (10 neurotypes × 4 cultures × 3 ages = 120 combos) |

---

## 8. DEFINITION OF DONE

The system is "living" when:

1. **Green tests**: All ~250+ tests pass (existing 213 + ~40 new)
2. **AESHI > 70**: System health score above threshold
3. **Pipeline running**: At least 1 paper/week flowing through
4. **CVA computable**: Constraint and valuation vectors generated for any template
5. **Attractors computed**: At least 5 rasa-like attractors identified with basins
6. **Self-healing active**: At least 3 invariant violations auto-remediated successfully
7. **Annotations complete**: All 17 annotation types operational; measurement + stimulus tags on ≥50% of templates
8. **Molecules registered**: 4 new molecules linked to templates
9. **Overseer reports daily**: Unified health report generated and trended
10. **Cultural variants loaded**: At least 4 cultural valuation structures (Western, Japanese, West African, Indian)

---

*This plan transforms ATLAS from a well-engineered static knowledge system into a living, growing, self-healing organism. The theory has been done; now we build.*
