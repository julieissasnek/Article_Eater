# Implementation Plan: Epistemic-Causal Bridge Repair

**Date**: 2026-02-10
**Version**: V23.1.0 target
**Panel**: P-ECB-R (approved approach)
**Status**: PENDING REVIEW

---

## Executive Summary

This plan repairs the epistemic-causal bridge integration in 6 phases across 3 sprints. The goal is a working, simplified bridge (~500 lines) that:

1. Extracts causal models from the foundherentist web of belief
2. Computes counterfactuals with van Fraassen contrast class rigor
3. Feeds results back to update the web
4. Is actually wired into the pipeline

---

## Pre-Implementation: File Inventory

### Source Files

| File | Lines | Status | Action |
|------|-------|--------|--------|
| `src/services/epistemic_causal_bridge.py` | 2381 | Exists, untested | REFACTOR → ~500 lines |
| `src/services/web_of_belief.py` | 2918 | Core, tested | MINOR UPDATES |
| `app/tasks/pipeline.py` | ~1600 | Production | ADD BRIDGE CALLS |
| External: `research/.../epistemic_causal_integration.py` | ~84KB | Tests use this | CONSOLIDATE |

### Test Files

| File | Lines | Status | Action |
|------|-------|--------|--------|
| `tests/test_epistemic_causal_integration.py` | ~1000 | Uses wrong path | FIX IMPORTS |
| NEW: `tests/test_epistemic_causal_bridge.py` | — | Doesn't exist | CREATE |

---

## Sprint ECB-1: Cleanup and Consolidation (Phase 1-2)

**Duration**: 1-2 days
**Goal**: Single source of truth, remove dead code

### Task ECB-1.1: Archive Features to Quarantine

**Files created**:
```
quarantine/2026-02-10/epistemic_causal_bridge_features/
├── individual_differences.py
├── cultural_meaning.py
├── argument_attack.py
├── generalization_elaborate.py
└── README.md
```

**Acceptance criteria**:
- [ ] All archived code extracted to separate files
- [ ] README.md documents each feature (already written in docs/)
- [ ] Original file size reduced by ~600 lines

**Code to extract** (from `epistemic_causal_bridge.py`):
- Lines 352-406: `IndividualDifferenceProfile`, `IndividualDifferenceFactor`
- Lines 232-238: `CulturalMeaning`
- Lines 413-465: `ArgumentAttack`, `AttackContrastAnalysis`
- Lines 84-102: `AttackType`, `ContrastShiftType` enums (keep ContrastShiftType, archive AttackType)
- Lines 811-850: `GeneralizationAssessment`

### Task ECB-1.2: Delete Duplicate Class Definitions

**Target**: Remove classes that duplicate `web_of_belief.py`

**Classes to delete** (from `epistemic_causal_bridge.py`):
- Lines 46-51: `EpistemicLevel` enum — duplicate of `web_of_belief.py:87`
- Lines 54-60: `BeliefStatus` enum — duplicate of `web_of_belief.py:100`
- Lines 63-71: `ConstraintType` enum — duplicate of `web_of_belief.py:109`
- Lines 110-146: `Credence` class — duplicate of `web_of_belief.py:363`
- Lines 150-192: `Belief` class — duplicate of `web_of_belief.py:451`
- Lines 320-345: `BeliefScope` class — duplicate of `web_of_belief.py` ScopeConditions

**Replace with imports**:
```python
from src.services.web_of_belief import (
    Belief,
    Credence,
    Constraint,
    EpistemicLevel,
    BeliefStatus,
    ConstraintType,
    ScopeConditions,
    EnablingConditions,
)
```

**Acceptance criteria**:
- [ ] No duplicate class definitions remain
- [ ] All imports from `web_of_belief.py`
- [ ] File compiles without errors

### Task ECB-1.3: Consolidate Implementations

**Problem**: Tests import from external path:
```python
EPIST_LAYER_PATH = Path("/Users/davidusa/REPOS/research/claude_epist_layer adds K to causal BN")
sys.path.insert(0, str(EPIST_LAYER_PATH))
import epistemic_causal_integration as eci
```

**Action**:
1. Compare repo file to external file
2. Merge any useful differences into repo file
3. Update test imports to use repo file:
```python
from src.services.epistemic_causal_bridge import EpistemicCausalBridge
```

**Acceptance criteria**:
- [ ] Tests import from `src/services/epistemic_causal_bridge`
- [ ] External file no longer needed (can archive)
- [ ] All existing tests pass with new imports

### Task ECB-1.4: Create Quarantine Directory Structure

```bash
mkdir -p quarantine/2026-02-10/epistemic_causal_bridge_features
# Move archived code there
```

**Acceptance criteria**:
- [ ] Directory created
- [ ] Files moved
- [ ] git status shows moves, not deletes

---

## Sprint ECB-2: Core Integration (Phase 3-4)

**Duration**: 2-3 days
**Goal**: Working bridge wired into pipeline

### Task ECB-2.1: Simplify EpistemicCausalBridge Class

**Target structure** (~500 lines total):

```python
class EpistemicCausalBridge:
    """Bridge between foundherentist web and Pearlian causal layer."""

    def __init__(self, web: 'WebOfBelief'):
        self.web = web
        self.multi_theory_model: Optional[MultiTheoryModel] = None
        self.population_contexts: Dict[str, PopulationContext] = {}

    # === MODEL CONSTRUCTION ===

    def build_causal_models(
        self,
        credence_threshold: float = 0.5,
        include_theories: Optional[List[str]] = None
    ) -> MultiTheoryModel:
        """Extract causal models from web. High-credence beliefs → equations."""

    def _get_theory_beliefs(self, theory_id: str, credence_threshold: float) -> List[Belief]:
        """Get beliefs for a theory, checking enabling conditions."""

    def _build_theory_model(self, theory_id: str, beliefs: List[Belief]) -> TheoryRelativeModel:
        """Build DAG + equations for one theory."""

    # === COUNTERFACTUAL COMPUTATION ===

    def counterfactual(
        self,
        intervention: Dict[str, float],
        outcome: str,
        evidence: Optional[Dict[str, float]] = None,
        contrast_class: Optional[ContrastClass] = None,
        target_population: Optional[str] = None
    ) -> QuineanCounterfactualResult:
        """Compute counterfactual with full Quinean analysis."""

    # === FEEDBACK LOOP (NEW) ===

    def update_web_from_result(
        self,
        result: QuineanCounterfactualResult
    ) -> List[Dict[str, Any]]:
        """
        Feed counterfactual results back to web.
        Returns list of changes made.
        """

    # === CONTRAST CLASS HANDLING ===

    def _assess_contrast_transfer(self, query, theory_results) -> ContrastAssessment:
        """Van Fraassen: Is the contrast class appropriate?"""

    def _contrasts_equivalent(self, source: ContrastClass, target: ContrastClass) -> bool:
        """Check if two contrast classes are equivalent."""
```

**Classes to keep** (simplified):
- `MultiTheoryModel`
- `TheoryRelativeModel`
- `StructuralEquation` (add `enabling_conditions` field per Cartwright)
- `ContrastClass`
- `PopulationContext` (simplified)
- `ContrastType` enum
- `ContrastShiftType` enum
- `CounterfactualQuery`
- `QuineanCounterfactualResult`
- `RobustnessAnalysis`
- `CoherenceAssessment`
- `ScopeAssessment`
- `ContrastAssessment`

**Acceptance criteria**:
- [ ] File is <600 lines
- [ ] All kept classes documented
- [ ] `mypy` passes (if configured)

### Task ECB-2.2: Add Feedback Loop Method

**New method** in `EpistemicCausalBridge`:

```python
def update_web_from_result(
    self,
    result: QuineanCounterfactualResult,
    auto_update: bool = False
) -> List[Dict[str, Any]]:
    """
    Feed counterfactual results back to web.

    Per panel P-ECB-R:
    - HIGH robustness + coherence → small credence increase for supporting beliefs
    - LOW robustness → flag sensitive beliefs for review (no auto-update)
    - COHERENCE violation → prefer revising less entrenched belief
    - CONTRAST mismatch → create gap, route to VOI search

    Args:
        result: The counterfactual result
        auto_update: If True, apply updates automatically. If False, return suggestions only.

    Returns:
        List of suggested/applied changes
    """
    changes = []

    # HIGH robustness: increase credence of supporting beliefs
    if result.robustness.robustness_score > 0.7 and result.coherence.coherence_score > 0.7:
        for belief_info in result.robustness.sensitive_beliefs:
            belief_id = belief_info['belief_id']
            if belief_id in self.web.beliefs:
                change = {
                    'type': 'credence_increase',
                    'belief_id': belief_id,
                    'reason': 'supported_by_robust_counterfactual',
                    'delta': 0.02  # Small increase
                }
                changes.append(change)
                if auto_update:
                    belief = self.web.beliefs[belief_id]
                    belief.credence = Credence(
                        value=min(0.95, belief.credence.value + 0.02),
                        uncertainty=belief.credence.uncertainty,
                        n_supporting=belief.credence.n_supporting + 1,
                        n_contradicting=belief.credence.n_contradicting,
                        n_observations=belief.credence.n_observations + 1
                    )

    # LOW robustness: flag for review
    if result.robustness.robustness_score < 0.4:
        for belief_info in result.robustness.sensitive_beliefs[:3]:  # Top 3
            changes.append({
                'type': 'review_recommended',
                'belief_id': belief_info['belief_id'],
                'reason': 'fragile_counterfactual_depends_on_this',
                'sensitivity': belief_info['sensitivity']
            })

    # COHERENCE violation: suggest revision of less entrenched
    if not result.coherence.is_coherent:
        for violation in result.coherence.violations:
            involved = violation.involved_beliefs
            if len(involved) >= 2:
                # Find less entrenched
                entrenchments = [(b, self.web.get_entrenchment(b)) for b in involved if b in self.web.beliefs]
                if entrenchments:
                    least_entrenched = min(entrenchments, key=lambda x: x[1])
                    changes.append({
                        'type': 'revision_suggested',
                        'belief_id': least_entrenched[0],
                        'reason': f'coherence_violation: {violation.description}',
                        'entrenchment': least_entrenched[1]
                    })

    # CONTRAST mismatch: create gap
    if result.contrast.contrast_similarity < 0.5:
        changes.append({
            'type': 'gap_identified',
            'reason': 'contrast_class_mismatch',
            'source_contrast': str(result.contrast.source_contrast.describe() if result.contrast.source_contrast else 'unknown'),
            'needed_contrast': str(result.query.describe()),
            'route_to': 'voi_search'
        })

    return changes
```

**Acceptance criteria**:
- [ ] Method implemented
- [ ] Returns structured change list
- [ ] Auto-update is optional (default False)
- [ ] Gaps routed to VOI search format

### Task ECB-2.3: Wire Bridge into Pipeline

**Target file**: `app/tasks/pipeline.py`

**Add near end of `run_from_contract_bundle()` or `_integrate_into_web_of_belief()`**:

```python
# === CAUSAL BRIDGE INTEGRATION (Sprint ECB-2) ===
from src.services.epistemic_causal_bridge import EpistemicCausalBridge

def _build_causal_layer(web: WebOfBelief, options: Dict[str, Any]) -> Dict[str, Any]:
    """Build causal layer from web of belief."""
    if not options.get('enable_causal_bridge', True):
        return {'causal_bridge_enabled': False}

    bridge = EpistemicCausalBridge(web)

    # Build causal models
    multi_model = bridge.build_causal_models(
        credence_threshold=options.get('credence_threshold', 0.5)
    )

    result = {
        'causal_bridge_enabled': True,
        'n_theories_modeled': len(multi_model.theory_models),
        'n_variables': len(multi_model.get_all_variables()),
        'n_equations': sum(len(m.equations) for m in multi_model.theory_models.values())
    }

    logger.info(f"Causal bridge: {result['n_theories_modeled']} theories, {result['n_equations']} equations")

    return result
```

**Call from pipeline**:
```python
# After web integration
if web_options.get('enable_web', True):
    web_result = _integrate_into_web_of_belief(...)

    # NEW: Build causal layer
    causal_result = _build_causal_layer(web_result['web'], causal_options)
    result['causal_bridge'] = causal_result
```

**Acceptance criteria**:
- [ ] Pipeline calls bridge when enabled
- [ ] Causal model stats in pipeline output
- [ ] Can be disabled via options
- [ ] Doesn't break existing pipeline tests

### Task ECB-2.4: Add Enabling Conditions to StructuralEquation

**Per Cartwright**: Equations should be conditional

```python
@dataclass
class StructuralEquation:
    equation_id: str
    outcome_var: str
    parent_vars: List[str]

    # Functional form
    functional_form: str
    parameters: Dict[str, float] = field(default_factory=dict)

    # Epistemic metadata
    supporting_beliefs: List[str] = field(default_factory=list)
    credence: float = 0.5
    entrenchment: float = 0.3

    # NEW: Enabling conditions (Cartwright)
    enabling_conditions: Optional[EnablingConditions] = None
    blocking_factors: List[str] = field(default_factory=list)

    def is_applicable(self, context: Dict[str, Any]) -> bool:
        """Check if equation applies given context."""
        if self.enabling_conditions is None:
            return True

        # Check minimum exposure
        if self.enabling_conditions.minimum_exposure:
            # Parse and check... simplified for now
            pass

        # Check blocking factors absent
        for blocker in self.blocking_factors:
            if context.get(blocker, False):
                return False

        return True
```

**Acceptance criteria**:
- [ ] `enabling_conditions` field added
- [ ] `is_applicable()` method implemented
- [ ] Counterfactual checks applicability before computing

---

## Sprint ECB-3: Van Fraassen and Feedback (Phase 5-6)

**Duration**: 2-3 days
**Goal**: Full contrast class rigor, feedback loop working

### Task ECB-3.1: Implement Contrast Transfer Rules

**Per van Fraassen panel response**:

```python
class ContrastTransferType(Enum):
    DIRECT = "direct"              # Same contrast, 1.0 adjustment
    BASELINE_SHIFT = "baseline"    # Different baseline level
    POPULATION_SHIFT = "population"  # Different population
    MEANING_SHIFT = "meaning"      # Different construct meaning — CANNOT TRANSFER

def assess_contrast_transfer(
    source: ContrastClass,
    target: ContrastClass
) -> ContrastAssessment:
    """
    Assess whether contrast can transfer from source to target.

    Van Fraassen rules:
    - DIRECT: Same focal and contrast conditions → adjustment = 1.0
    - BASELINE_SHIFT: Same variables, different baseline → estimate difference
    - POPULATION_SHIFT: Different population → check baseline similarity
    - MEANING_SHIFT: Different constructs → CANNOT TRANSFER, return undefined
    """
    # Check focal condition match
    focal_match = _compare_conditions(source.focal, target.focal)

    # Check contrast conditions match
    contrast_match = _compare_contrast_sets(source.contrasts, target.contrasts)

    # Check population match
    population_match = _compare_populations(
        source.population_context,
        target.population_context
    )

    # Determine transfer type
    if focal_match > 0.9 and contrast_match > 0.9 and population_match > 0.8:
        transfer_type = ContrastTransferType.DIRECT
        adjustment = 1.0
        can_transfer = True
    elif focal_match > 0.7 and contrast_match > 0.7:
        if population_match > 0.5:
            transfer_type = ContrastTransferType.POPULATION_SHIFT
            adjustment = population_match
            can_transfer = True
        else:
            transfer_type = ContrastTransferType.BASELINE_SHIFT
            adjustment = _estimate_baseline_adjustment(source, target)
            can_transfer = True
    elif focal_match < 0.5 or contrast_match < 0.5:
        transfer_type = ContrastTransferType.MEANING_SHIFT
        adjustment = 0.0
        can_transfer = False
    else:
        transfer_type = ContrastTransferType.BASELINE_SHIFT
        adjustment = 0.7  # Default penalty
        can_transfer = True

    warnings = []
    if not can_transfer:
        warnings.append(
            f"CONTRAST MISMATCH: Cannot transfer. "
            f"Source: {source.describe()}, Target: {target.describe()}"
        )

    return ContrastAssessment(
        source_contrast=source,
        target_contrast=target,
        contrast_preserved=(transfer_type == ContrastTransferType.DIRECT),
        contrast_similarity=focal_match * contrast_match * population_match,
        transfer_type=transfer_type.value,
        adjustment_factor=adjustment,
        warnings=warnings,
        can_transfer=can_transfer  # NEW FIELD
    )
```

**Acceptance criteria**:
- [ ] All four transfer types handled
- [ ] MEANING_SHIFT returns `can_transfer=False`
- [ ] Warnings generated for mismatches
- [ ] Adjustment factors reasonable

### Task ECB-3.2: Return Undefined for Non-Transferable Contrasts

**Modify `counterfactual()` method**:

```python
def counterfactual(self, ...):
    # ... existing code ...

    # Step 6: Contrast transfer (van Fraassen)
    contrast = self._assess_contrast_transfer(query, theory_results)

    # NEW: If contrast doesn't transfer, return undefined
    if hasattr(contrast, 'can_transfer') and not contrast.can_transfer:
        return QuineanCounterfactualResult(
            query=query,
            point_estimate=None,  # Explicitly undefined
            confidence_interval=(None, None),
            by_theory={},
            robustness=RobustnessAnalysis(
                robustness_score=0.0,
                min_revision_cost=0.0,
                sensitive_beliefs=[],
                path_entrenchment=0.0
            ),
            coherence=CoherenceAssessment(
                is_coherent=False,
                coherence_score=0.0,
                violations=[CoherenceViolation(
                    violation_type='contrast_mismatch',
                    description=contrast.warnings[0] if contrast.warnings else 'Contrast does not transfer',
                    involved_beliefs=[],
                    severity=1.0
                )],
                required_co_revisions=[]
            ),
            scope=scope,
            contrast=contrast,
            epistemic_quality=0.0,
            warnings=contrast.warnings + ['RESULT UNDEFINED: Contrast class does not transfer'],
            is_defined=False  # NEW FIELD
        )

    # ... continue with existing computation ...
```

**Acceptance criteria**:
- [ ] `is_defined` field added to `QuineanCounterfactualResult`
- [ ] Undefined results have `point_estimate=None`
- [ ] Clear warning message
- [ ] Downstream code handles undefined results

### Task ECB-3.3: Route Gaps to VOI Search

**Connect feedback loop to VOI**:

```python
def route_gaps_to_voi(
    changes: List[Dict[str, Any]],
    voi_search: 'VOISearch'  # Import from src.services.voi_search
) -> List[str]:
    """Route identified gaps to VOI search for prioritization."""
    gap_ids = []

    for change in changes:
        if change.get('type') == 'gap_identified':
            gap_id = voi_search.register_gap(
                source='epistemic_causal_bridge',
                description=change.get('reason', ''),
                needed_contrast=change.get('needed_contrast', ''),
                priority=0.7  # Contrast gaps are high priority
            )
            gap_ids.append(gap_id)

    return gap_ids
```

**Acceptance criteria**:
- [ ] Gaps from contrast mismatch feed to VOI
- [ ] Gap IDs returned for tracking
- [ ] Integration with existing VOI search

### Task ECB-3.4: Add Haack's Security Weight

**Per Haack**: Track experiential grounding separately from supportiveness

**Modify `StructuralEquation`**:

```python
@dataclass
class StructuralEquation:
    # ... existing fields ...

    # Epistemic metadata
    credence: float = 0.5
    entrenchment: float = 0.3  # Supportiveness (from web position)

    # NEW: Haack's security weight (experiential grounding)
    security: float = 0.5  # How directly grounded in experience?

    # Derive security from belief level
    @classmethod
    def compute_security(cls, beliefs: List[Belief]) -> float:
        """
        Compute security (experiential grounding) from supporting beliefs.

        Security is higher when:
        - More EMPIRICAL/OBSERVATIONAL beliefs support
        - Contrast classes are explicit (not inferred)
        """
        if not beliefs:
            return 0.3

        level_weights = {
            EpistemicLevel.OBSERVATIONAL: 1.0,
            EpistemicLevel.EMPIRICAL: 0.8,
            EpistemicLevel.INTERMEDIATE: 0.4,
            EpistemicLevel.THEORETICAL: 0.2,
        }

        total_security = sum(
            level_weights.get(b.level, 0.3) * b.credence.value
            for b in beliefs
        )
        return total_security / len(beliefs)
```

**Acceptance criteria**:
- [ ] `security` field added
- [ ] Computed from belief levels
- [ ] Used in robustness/quality calculations

---

## Testing Plan

### New Test File: `tests/test_epistemic_causal_bridge.py`

```python
"""
Tests for the repaired epistemic-causal bridge.

Sprint ECB-1/2/3 deliverable.
"""

import pytest
from src.services.web_of_belief import WebOfBelief, Belief, Credence, EpistemicLevel, BeliefStatus
from src.services.epistemic_causal_bridge import (
    EpistemicCausalBridge,
    MultiTheoryModel,
    ContrastClass,
    QuineanCounterfactualResult,
)


class TestBridgeConstruction:
    """Test model construction from web."""

    def test_build_causal_models_empty_web(self):
        """Empty web produces empty model."""
        web = WebOfBelief(domain="test")
        bridge = EpistemicCausalBridge(web)
        model = bridge.build_causal_models()
        assert len(model.theory_models) == 0

    def test_build_causal_models_single_theory(self):
        """Single theory web produces one model."""
        # ... setup web with one theory ...
        pass

    def test_credence_threshold_filters_beliefs(self):
        """Beliefs below threshold excluded."""
        pass


class TestCounterfactual:
    """Test counterfactual computation."""

    def test_counterfactual_basic(self):
        """Basic counterfactual computation."""
        pass

    def test_counterfactual_contrast_mismatch_returns_undefined(self):
        """Contrast mismatch returns undefined result."""
        pass

    def test_counterfactual_enabling_conditions_gate(self):
        """Unmet enabling conditions block computation."""
        pass


class TestFeedbackLoop:
    """Test web update from results."""

    def test_high_robustness_increases_credence(self):
        """High robustness → credence increase."""
        pass

    def test_low_robustness_flags_for_review(self):
        """Low robustness → review flag, no auto-update."""
        pass

    def test_coherence_violation_suggests_revision(self):
        """Coherence violation → suggest revising less entrenched."""
        pass

    def test_contrast_mismatch_creates_gap(self):
        """Contrast mismatch → gap routed to VOI."""
        pass


class TestContrastTransfer:
    """Test van Fraassen contrast transfer rules."""

    def test_direct_transfer(self):
        """Same contrast class → direct transfer."""
        pass

    def test_population_shift(self):
        """Different population → population shift."""
        pass

    def test_meaning_shift_cannot_transfer(self):
        """Different meaning → cannot transfer."""
        pass
```

**Acceptance criteria**:
- [ ] >80% coverage of new code
- [ ] All edge cases tested
- [ ] Integration with existing web tests

---

## Acceptance Criteria Summary

### Sprint ECB-1 (Cleanup)
- [ ] Archived features in quarantine with documentation
- [ ] No duplicate class definitions
- [ ] Single implementation (repo file)
- [ ] Tests use repo file
- [ ] File compiles without errors

### Sprint ECB-2 (Core)
- [ ] Bridge <600 lines
- [ ] Wired into pipeline
- [ ] Feedback loop method implemented
- [ ] Enabling conditions on equations
- [ ] Pipeline tests pass

### Sprint ECB-3 (Van Fraassen + Feedback)
- [ ] Contrast transfer rules implemented
- [ ] Undefined returned for non-transferable
- [ ] Gaps route to VOI search
- [ ] Security weight added (Haack)
- [ ] All new tests pass

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking existing tests | Medium | High | Run full test suite after each task |
| Performance regression | Low | Medium | Benchmark before/after |
| VOI search integration fails | Low | Medium | Mock VOI in tests |
| Contrast transfer too strict | Medium | Medium | Add logging, tune thresholds |

---

## Rollback Plan

If integration fails:
1. Revert pipeline changes (`git checkout app/tasks/pipeline.py`)
2. Keep simplified bridge in place (it works standalone)
3. Document what failed for next attempt

---

*Implementation plan complete. Ready for panel + developer review.*
