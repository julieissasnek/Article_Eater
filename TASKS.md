# TASKS.md

*Last updated: Monday, February 10, 2026 (Sprint ECB: Epistemic-Causal Bridge Repair)*

This file tracks all tasks for the Article_Eater_PostQuinean_v1 project. Completed tasks are kept as project history. **Panels are first-class objects** integrated into the sprint cycle.

---

## Task Coordination (MANDATORY)

**Before starting ANY task, check `ACTIVE_TASKS.md`** to see what's claimed.

```
1. Read ACTIVE_TASKS.md
2. Claim your task (add row to Active Claims)
3. Start work
4. Update ACTIVE_TASKS.md when done
5. Update this file (TASKS.md) with completion status
```

This prevents duplicate work across parallel terminals.

---

## Current Priority Order

1. ~~**Sprint 2.5 Social Epistemology**~~ ✓ COMPLETE
2. ~~**Panel Convening**~~ ✓ COMPLETE — P-TC (7 decisions), P-QW (6 decisions)
3. ~~**Strategic TODOs 1-3**~~ ✓ COMPLETE — Credibility, Interpretive, VOI
4. ~~**Sprint 2.6 Panel Implementation**~~ ✓ COMPLETE — P-TC Track A, P-QW Track B
5. ~~**Technical Debt**~~ ✓ ALL COMPLETE [TD-A, TD-B, TD-C, TD-D, TD-E]
6. ~~**Sprint 2.0.4-2.0.5**~~ ✓ COMPLETE — Pipeline testing and error handling
7. ~~**AF-AE Integration: BibTeX Metadata**~~ ✓ COMPLETE (BIB-1 through BIB-7)
8. ~~**Entrenchment Historical Replay + Monitor**~~ ✓ COMPLETE (ENT-1 through ENT-5)
9. ~~**Sprint 3.0 Phase 1-2**~~ ✓ COMPLETE — API, Query Engine, Export, Visualization
10. ~~**Panel Consultations Sprint 3.0**~~ ✓ COMPLETE (2026-02-09)
11. **Sprint ECB: Epistemic-Causal Bridge Repair** — IN PROGRESS (see below)
12. **Article Discovery + PDF Retrieval Monitoring** — PAUSED (DISC-1, DISC-2 complete)

---

## Sprint ECB: Epistemic-Causal Bridge Repair

**Added**: 2026-02-10
**Priority**: P0 (System Coherence Critical)
**Panel**: P-ECB-R (Haack, Pearl, van Fraassen, Simon, Cartwright, Parnas, Brooks)
**Target Version**: V23.1.0
**Context**: System coherence concerns identified. Epistemic-causal bridge has two implementations, duplicate classes, and is not wired into pipeline. Panel approved comprehensive repair.

### Problem Statement

1. **Two implementations exist**: Repo file ≠ external research file (tests use wrong one)
2. **Duplicate class definitions**: Bridge defines `Belief`, `Credence`, etc. that duplicate `web_of_belief.py`
3. **Not used in pipeline**: `app/tasks/pipeline.py` makes zero bridge calls
4. **No feedback loop**: Counterfactual results don't update the web
5. **Van Fraassen contrast classes disconnected**: Elaborate but not integrated

### Panel Recommendations (P-ECB-R)

| Expert | Key Recommendation |
|--------|-------------------|
| **Haack** | Equations need TWO weights: supportiveness (entrenchment) + security (experiential grounding) |
| **Pearl** | Separate DAG structure from parameters; track associational/interventional/counterfactual |
| **van Fraassen** | If contrast doesn't transfer, return undefined; route gaps to VOI |
| **Simon** | Target ~500 lines (down from 2400); ruthless simplification |
| **Cartwright** | Enabling conditions GATE computation; capacities don't manifest without conditions |
| **Parnas** | Delete duplicates; single source of truth; add error handling |
| **Brooks** | Checkpoint each sprint; don't add features while simplifying |

### Archived Features (For Future Reintegration)

| Feature | Archive Location | Future TODO |
|---------|-----------------|-------------|
| Individual Differences | `quarantine/2026-02-10/individual_differences.py` | IND-1 through IND-4 |
| Cultural Meanings | `quarantine/2026-02-10/cultural_meaning.py` | CULT-1 through CULT-5 |
| Argument Attack Analysis | `quarantine/2026-02-10/argument_attack.py` | ATK-1 through ATK-4 |
| Elaborate Generalization | `quarantine/2026-02-10/generalization_elaborate.py` | GEN-1 through GEN-4 |

See: `docs/ARCHIVED_FEATURES_EPISTEMIC_CAUSAL_BRIDGE_2026-02-10.md`

---

### Sprint ECB-1: Cleanup and Consolidation ✓ COMPLETE

**Goal**: Single source of truth, remove dead code
**Completed**: 2026-02-10
**Outcome**: 68+89 tests pass, duplicates marked DEPRECATED, features archived

| ID | Task | Description | Status |
|----|------|-------------|--------|
| ECB-1.0 | Diff implementations | Compare repo vs external file, document differences | ✓ DONE — Only 43 lines differ (all V23.0.0 entrenchment) |
| ECB-1.1 | Archive features | Move IndividualDiff, CulturalMeaning, ArgumentAttack to quarantine with headers | ✓ DONE — 4 files + README |
| ECB-1.2 | Mark duplicates DEPRECATED | EpistemicLevel, BeliefStatus, Credence, Belief with clear warnings | ✓ DONE — Kept for stub/demo, marked for ECB-2 removal |
| ECB-1.3 | Update test imports | Fix `test_epistemic_causal_integration.py` to use repo module | ✓ DONE — Removed external path, 68 tests pass |
| ECB-1.4 | Verify tests pass | Run bridge, persistence, warrants tests | ✓ DONE — 68+89 tests pass |

**Checkpoint**: All tests pass ✓, file compiles ✓, pipeline unchanged ✓

**Notes**:
- Duplicate classes MARKED as DEPRECATED rather than deleted (per Brooks: "Don't break while simplifying")
- Stub WebOfBelief kept for demo functions (marked for removal in ECB-2)
- V23.0.0 entrenchment code preserved intact (web_of_belief.py untouched)

---

### Sprint ECB-2: Core Integration ✓ COMPLETE

**Goal**: Working bridge wired into pipeline
**Completed**: 2026-02-10
**Outcome**: Bridge wired into pipeline.py, CLI flags added, feedback loop implemented

| ID | Task | Description | Status |
|----|------|-------------|--------|
| ECB-2.1 | Simplify class | Reduced 2462→2020 lines (~500 target deferred to incremental cleanup) | ✓ DONE |
| ECB-2.2 | Add enabling conditions | `StructuralEquation.enabling_conditions` + `is_applicable(context)` → (bool, reason) | ✓ DONE |
| ECB-2.3 | Wire into pipeline | Stage 2.8 in pipeline.py, `--no-causal` and `--causal-credence-threshold` CLI flags | ✓ DONE |
| ECB-2.4 | Add feedback loop | `update_web_from_result()` with proportional delta (Simon), conditional tracking | ✓ DONE |

**Checkpoint**: Pipeline runs with bridge ✓, 68 tests pass ✓

**Notes**:
- Bridge builds causal models from high-credence beliefs
- CLI: `--no-causal` disables, `--causal-credence-threshold` configures belief threshold
- Feedback loop updates uncertainty proportionally to sensitivity
- Demo functions archived to quarantine/2026-02-10/demo_and_stub_web.py

---

### Sprint ECB-3: Van Fraassen and Polish ✓ COMPLETE

**Goal**: Full contrast class rigor, feedback loop working
**Completed**: 2026-02-10
**Dependencies**: ECB-2 complete

| ID | Task | Description | Status |
|----|------|-------------|--------|
| ECB-3.1 | Contrast transfer rules | `ContrastTransferType` enum, configurable thresholds via `AE_CONTRAST_THRESHOLD_*` | ✓ DONE |
| ECB-3.2 | Return undefined | `is_defined=False` + `reason_undefined` when contrast transfer fails | ✓ DONE |
| ECB-3.3 | Gap identification | 5 gap types: missing_contrast, low_coverage, theory_conflict, baseline_unknown, blocked_beliefs | ✓ DONE |
| ECB-3.4 | Security weight | `compute_security()` and `compute_model_security()` with Haack weights | ✓ DONE |
| ECB-3.5 | Update ARCHITECTURE.md | Causal layer diagram, transfer rules, gap types, security weights documented | ✓ DONE |
| ECB-3.6 | Error handling pass | `BridgeError` hierarchy, graceful empty web handling, validation | ✓ DONE |

**Checkpoint**: 68 integration tests pass ✓, 153 related tests pass ✓, docs updated ✓

**Panel Consultation**: P-ECB-R reviewed all decisions
- D1-D6 approved with minor notes
- Future work: meaning equivalence flag, enabling_unclear gap type, theory conflict decomposition
- See: `docs/PANEL_CONSULTATION_ECB-3_2026-02-10.md`

---

### Pending: Panel-Recommended ECB Enhancements

**Added**: 2026-02-10
**Source**: Full panel review of Sprints ECB-1, ECB-2, and ECB-3
**Panel**: Pearl, van Fraassen, Haack, Simon, Cartwright, Parnas, Brooks
**Documentation**: `docs/PANEL_CONSULTATION_ECB_FULL_REVIEW_2026-02-10.md`

These enhancements address limitations identified during comprehensive panel review of all ECB repair work. Each improves the epistemic-causal bridge's ability to handle real-world complexity.

| ID | Task | Priority | Panel Source | Status |
|----|------|----------|--------------|--------|
| ECB-F1 | Meaning equivalence flag | P2 | van Fraassen | ☐ TODO |
| ECB-F2 | Add `enabling_unclear` gap type | P2 | Cartwright | ☐ TODO |
| ECB-F3 | Decompose theory conflict | P2 | Pearl | ☐ TODO |
| ECB-F4 | Track contrast class source | P3 | Haack | ☐ TODO |
| ECB-F5 | Deprecate `transfer_type_str` | P3 | Parnas | ☐ TODO |
| ECB-F6 | ECB-3 boundary value tests | P1 | Brooks | ✓ DONE |
| ECB-F7 | Prominent causal failure warning | P1 | Pearl | ✓ DONE |
| ECB-F8 | Flag causal-empirical beliefs | P2 | Pearl | ☐ TODO |
| ECB-F9 | Contrast-gated feedback | P1 | van Fraassen | ✓ DONE |
| ECB-F10 | Observational grounding | P2 | Haack | ☐ TODO |
| ECB-F11 | Configurable feedback rate | P2 | Simon | ☐ TODO |
| ECB-F12 | Complete enabling condition checks | P2 | Cartwright | ☐ TODO |
| ECB-F13 | Excluded belief registry | P2 | Cartwright | ☐ TODO |
| ECB-F14 | Lazy bridge import | P1 | Parnas | ✓ DONE |
| ECB-F15 | CLI shorthand flags | P3 | Parnas | ☐ TODO |
| ECB-F16 | User documentation sprint | P1 | Brooks | ✓ DONE |
| ECB-F17 | Stub contrast warning | P3 | van Fraassen | ☐ TODO |
| ECB-F18 | DEPRECATED removal deadline | P2 | Parnas | ☐ TODO |

**P1 Features Complete** (2026-02-10):
- ECB-F6: 29 boundary value tests in `tests/test_ecb3_boundaries.py`
- ECB-F7: Prominent warning in `web_state.json` when causal layer fails
- ECB-F9: Feedback loop gated on `is_defined` and contrast transfer type
- ECB-F14: Lazy import in `pipeline.py` isolates module failures
- ECB-F16: User guide at `docs/USER_GUIDE_CAUSAL_BRIDGE.md`

#### ECB-F1: Meaning Equivalence Flag (van Fraassen)

**What**: Add `meaning_equivalent: bool` to `ContrastAssessment` that can override MEANING_SHIFT classification.

**Why**: Currently, if two populations use different words for the same construct (e.g., "nature" vs "green space"), we classify this as MEANING_SHIFT and refuse to transfer. But sometimes meanings differ lexically yet are *functionally equivalent*—the construct produces the same behavioral/psychological effects. This flag allows domain experts to mark such cases as transferable despite surface meaning differences.

**Implementation**:
```python
@dataclass
class ContrastAssessment:
    ...
    meaning_equivalent: bool = False  # If True, override MEANING_SHIFT → POPULATION_SHIFT
```

**Location**: `src/services/epistemic_causal_bridge.py:ContrastAssessment`

---

#### ECB-F2: Add `enabling_unclear` Gap Type (Cartwright)

**What**: Add sixth gap type `enabling_unclear` distinct from `blocked_beliefs`.

**Why**: There's a crucial difference between:
- `blocked_beliefs`: We KNOW the enabling conditions but they're UNMET
- `enabling_unclear`: We DON'T KNOW what the enabling conditions ARE

The second is a deeper epistemic gap—we can't even evaluate whether the mechanism will manifest. This matters for research prioritization: understanding enabling conditions should precede testing them.

**Implementation**:
```python
# In _identify_gaps():
if has_causal_claim_without_conditions(belief):
    gaps.append(EpistemicGap(
        gap_id=make_gap_id(),
        gap_type="enabling_unclear",
        description=f"Enabling conditions unknown for: {belief.belief_id}",
        priority=0.6,  # Higher than blocked_beliefs (0.4)
        suggested_query=f"What conditions enable {mechanism}?"
    ))
```

**Location**: `src/services/epistemic_causal_bridge.py:_identify_gaps()`

---

#### ECB-F3: Decompose Theory Conflict (Pearl)

**What**: Split `theory_conflict` gap into `structural_conflict` and `parametric_conflict`.

**Why**: Pearl noted that theory disagreements come in two flavors:
- **Structural**: Theories propose different DAGs (different causal relationships)
- **Parametric**: Theories agree on DAG but disagree on coefficients

These require different resolutions:
- Structural conflicts need experiments that distinguish causal pathways
- Parametric conflicts need more precise measurement of effect sizes

**Implementation**:
```python
class TheoryConflictType(Enum):
    STRUCTURAL = "structural"    # Different DAGs
    PARAMETRIC = "parametric"    # Same DAG, different coefficients
    MIXED = "mixed"              # Both

# Detect by comparing edges across theory models
if theory_models have different edges:
    conflict_type = STRUCTURAL
elif theory_models have same edges but different parameters:
    conflict_type = PARAMETRIC
```

**Location**: `src/services/epistemic_causal_bridge.py:_identify_gaps()`

---

#### ECB-F4: Track Contrast Class Source (Haack)

**What**: Track whether contrast class was explicitly stated in paper methods vs inferred from results.

**Why**: Haack's foundherentism weights experiential grounding. A contrast class stated in the Methods section ("we compared forest exposure to urban control") has higher epistemic security than one inferred from Results ("effect size suggests the contrast was..."). This should affect the security weight bonus.

**Implementation**:
```python
@dataclass
class ContrastClass:
    ...
    source: str = "inferred"  # Already exists
    source_location: Optional[str] = None  # NEW: "methods", "results", "discussion"

# In compute_security():
if contrast_class.source_location == "methods":
    contrast_bonus = 0.20  # Higher
else:
    contrast_bonus = 0.10  # Lower
```

**Location**: `src/services/epistemic_causal_bridge.py:ContrastClass`, `compute_security()`

---

#### ECB-F5: Deprecate `transfer_type_str` (Parnas)

**What**: Remove backward-compatibility `transfer_type_str: str` field, use only `transfer_type: ContrastTransferType` enum.

**Why**: Parnas correctly identified this as technical debt. Dual representations complicate the interface and invite bugs where code checks one but not the other. The enum should be the single source of truth.

**Implementation**:
1. Deprecation warning in V23.1
2. Remove in V24.0
3. Update all callers to use `.transfer_type.value` if string needed

**Location**: `src/services/epistemic_causal_bridge.py:ContrastAssessment`

---

#### ECB-F6: ECB-3 Boundary Value Tests (Brooks)

**What**: Add explicit tests for ECB-3 features at boundary values.

**Why**: Brooks noted the new code is tested only implicitly. We need explicit tests for:
- Contrast similarity at exact thresholds (0.49 vs 0.50 vs 0.51)
- Gap identification with edge cases (empty gaps, all gaps)
- Security weight bounds (min 0.05, max 0.95)
- Error handling (None inputs, empty dicts)

**Implementation**:
```python
# tests/test_ecb3_boundaries.py
class TestContrastThresholdBoundaries:
    def test_similarity_at_direct_threshold(self):
        # 0.90 should be DIRECT, 0.89 should be BASELINE_SHIFT

    def test_similarity_at_population_threshold(self):
        # 0.50 should be POPULATION_SHIFT, 0.49 should be MEANING_SHIFT

class TestSecurityWeightBounds:
    def test_minimum_security_floor(self):
        # Even worst case should be >= 0.05

    def test_maximum_security_cap(self):
        # Even best case should be <= 0.95
```

**Location**: `tests/test_ecb3_boundaries.py` (new file)

---

#### ECB-F7: Prominent Causal Failure Warning (Pearl)

**What**: Add prominent warning to output when causal layer fails to build.

**Why**: Currently, if `build_causal_models()` fails, the pipeline continues with `enabled: False` in the output. Users might not notice this flag and draw conclusions without understanding that causal annotations are missing. Pearl: *"They might not notice the `enabled: False` flag and draw conclusions without understanding limitations."*

**Implementation**:
```python
# In pipeline.py _build_causal_layer():
except Exception as e:
    logger.warning(f"Causal bridge failed: {e}")
    result['causal_layer'] = {
        'enabled': False,
        'error': str(e),
        'WARNING': 'CAUSAL LAYER UNAVAILABLE - Results lack causal annotations'
    }
    # Also add to top-level warnings list
    result.setdefault('warnings', []).append(
        'CAUSAL LAYER FAILED: Results do not include causal inference annotations'
    )
```

**Location**: `app/tasks/pipeline.py:_build_causal_layer()`

---

#### ECB-F8: Flag Causal-Empirical Beliefs (Pearl)

**What**: Automatically flag empirical beliefs that contain causal language ("causes", "leads to", "results in").

**Why**: Beliefs classified as EMPIRICAL should describe observations, not causal structure. When an empirical belief says "X causes Y," it's making a structural claim despite being classified as observational. These hybrid beliefs deserve epistemological review—they may be misclassified or may reveal implicit causal assumptions. Pearl: *"Empirical beliefs with CAUSAL language should be flagged for review."*

**Implementation**:
```python
CAUSAL_PATTERNS = ['causes', 'leads to', 'results in', 'produces', 'triggers']

def flag_causal_empirical(belief: Belief) -> Optional[str]:
    if belief.level in (EpistemicLevel.EMPIRICAL, EpistemicLevel.OBSERVATIONAL):
        content = belief.content.lower()
        for pattern in CAUSAL_PATTERNS:
            if pattern in content:
                return f"REVIEW: Empirical belief contains causal language '{pattern}'"
    return None
```

**Location**: `src/services/epistemic_causal_bridge.py` (new function), called during `build_causal_models()`

---

#### ECB-F9: Contrast-Gated Feedback (van Fraassen)

**What**: Gate the feedback loop so it only updates belief credences when contrast transfer is valid.

**Why**: Currently, if a counterfactual has HIGH robustness but LOW contrast similarity, we still update credences. But low contrast similarity means the finding may not apply at all—we're reinforcing beliefs based on potentially non-transferable results. van Fraassen: *"Don't reinforce beliefs based on results that may not transfer."*

**Implementation**:
```python
def update_web_from_result(self, result: QuineanCounterfactualResult):
    # Gate: Only update if contrast transfer is valid
    if not result.is_defined:
        logger.info(f"Skipping feedback: result undefined ({result.reason_undefined})")
        return {'updates': [], 'reason': 'result_undefined'}

    if result.contrast.transfer_type == ContrastTransferType.MEANING_SHIFT:
        logger.info("Skipping feedback: contrast transfer is MEANING_SHIFT")
        return {'updates': [], 'reason': 'meaning_shift'}

    # Proceed with feedback only for valid transfers
    ...
```

**Location**: `src/services/epistemic_causal_bridge.py:update_web_from_result()`

---

#### ECB-F10: Observational Grounding (Haack)

**What**: Include observational beliefs in `compute_security()` even when excluded from structure building.

**Why**: Haack's foundherentism says observational beliefs have the HIGHEST security—they're directly experiential. Currently, `_get_theory_beliefs()` filters them out for structure building (correct), but `compute_security()` should still count them because they GROUND the model even if they don't shape it. Haack: *"You're ignoring your most grounded evidence."*

**Implementation**:
```python
def compute_security(self, belief_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    # Include ALL beliefs in security computation, not just structural ones
    if belief_ids is None:
        # Use all beliefs, including observational
        belief_ids = list(self.web.beliefs.keys())

    # Observational beliefs get highest base security
    level_weights = {
        'observational': 0.9,   # Highest - direct experience
        'empirical': 0.7,       # Systematic observation
        'intermediate': 0.5,    # Mixed
        'theoretical': 0.3,     # Abstract
    }
```

**Location**: `src/services/epistemic_causal_bridge.py:compute_security()`

---

#### ECB-F11: Configurable Feedback Rate (Simon)

**What**: Make the feedback loop learning rate configurable via environment variable.

**Why**: The current 0.2 cap prevents overreaction to single queries, but different domains warrant different learning rates. High-stakes domains (medical) should update slowly; exploratory domains could update faster. Simon: *"Should the cap be configurable? Different domains may warrant different learning rates."*

**Implementation**:
```python
import os

# Configurable feedback rate (default 0.2 = 20% max change per query)
FEEDBACK_MAX_DELTA = float(os.environ.get('AE_FEEDBACK_MAX_DELTA', '0.2'))

def update_web_from_result(self, result: QuineanCounterfactualResult):
    ...
    # Use configurable rate instead of hardcoded 0.2
    delta = sensitivity * FEEDBACK_MAX_DELTA * (1 - old_uncertainty)
```

**Location**: `src/services/epistemic_causal_bridge.py` (module-level constant + update_web_from_result)

---

#### ECB-F12: Complete Enabling Condition Checks (Cartwright)

**What**: Implement threshold, dosage, and temporal condition checking in `is_applicable()`.

**Why**: The current implementation only checks `blocking_factors` and `concurrent_factors`. But real mechanisms have more nuanced enabling conditions: thresholds ("only above 30 minutes exposure"), dosage ("only at high intensity"), temporal windows ("only during recovery period"). Cartwright: *"What about threshold conditions, dosage conditions, temporal conditions?"*

**Implementation**:
```python
@dataclass
class EnablingConditions:
    blocking_factors: List[str] = field(default_factory=list)
    concurrent_factors: List[str] = field(default_factory=list)
    # NEW: Threshold conditions
    thresholds: Dict[str, Tuple[float, str]] = field(default_factory=dict)  # var -> (min_value, unit)
    # NEW: Dosage conditions
    dosage_requirements: Dict[str, str] = field(default_factory=dict)  # var -> level ("low"|"medium"|"high")
    # NEW: Temporal windows
    temporal_windows: Dict[str, Tuple[str, str]] = field(default_factory=dict)  # phase -> (start, end)

def is_applicable(self, context: Dict[str, Any]) -> Tuple[bool, str]:
    # Check thresholds
    for var, (min_val, unit) in self.thresholds.items():
        if var in context and context[var] < min_val:
            return (False, f"threshold_unmet:{var}<{min_val}{unit}")

    # Check dosage
    for var, required_level in self.dosage_requirements.items():
        if var in context and not meets_dosage(context[var], required_level):
            return (False, f"dosage_insufficient:{var}!={required_level}")

    # Check temporal window
    for phase, (start, end) in self.temporal_windows.items():
        if 'current_phase' in context and not in_window(context['current_phase'], start, end):
            return (False, f"temporal_mismatch:{phase}")
    ...
```

**Location**: `src/services/epistemic_causal_bridge.py:EnablingConditions`, `StructuralEquation.is_applicable()`

---

#### ECB-F13: Excluded Belief Registry (Cartwright)

**What**: Track beliefs excluded from causal models with reasons.

**Why**: When building causal models, we filter out empirical/observational beliefs and low-credence beliefs. This is correct, but we lose track of what was excluded and why. Cartwright: *"The filtering should TRACK which empirical beliefs were excluded and why. This is data, not noise."*

**Implementation**:
```python
@dataclass
class ExcludedBelief:
    belief_id: str
    reason: str  # "low_credence", "empirical_level", "enabling_blocked", etc.
    details: Dict[str, Any] = field(default_factory=dict)

class EpistemicCausalBridge:
    def __init__(self, web):
        ...
        self._excluded_beliefs: List[ExcludedBelief] = []

    def _get_theory_beliefs(self, theory_id, credence_threshold):
        for belief in candidates:
            if belief.credence.value < credence_threshold:
                self._excluded_beliefs.append(ExcludedBelief(
                    belief.belief_id, "low_credence",
                    {'credence': belief.credence.value, 'threshold': credence_threshold}
                ))
            elif belief.level in (EpistemicLevel.EMPIRICAL, EpistemicLevel.OBSERVATIONAL):
                self._excluded_beliefs.append(ExcludedBelief(
                    belief.belief_id, "empirical_level",
                    {'level': belief.level.value}
                ))
            ...

    def get_excluded_beliefs(self) -> List[ExcludedBelief]:
        return self._excluded_beliefs
```

**Location**: `src/services/epistemic_causal_bridge.py` (new class + tracking in _get_theory_beliefs)

---

#### ECB-F14: Lazy Bridge Import (Parnas)

**What**: Import the bridge module only when needed to isolate import failures.

**Why**: Currently, the pipeline imports from epistemic_causal_bridge at the top of the file. If that module fails to load (syntax error, missing dependency), the entire pipeline fails. Lazy import isolates the failure. Parnas: *"If that module fails to load, the entire pipeline fails."*

**Implementation**:
```python
# In pipeline.py - BEFORE:
from src.services.epistemic_causal_bridge import EpistemicCausalBridge

# AFTER:
def _build_causal_layer(web, options):
    try:
        from src.services.epistemic_causal_bridge import EpistemicCausalBridge
    except ImportError as e:
        logger.error(f"Failed to import epistemic_causal_bridge: {e}")
        return {'enabled': False, 'error': f'import_failed: {e}'}

    bridge = EpistemicCausalBridge(web)
    ...
```

**Location**: `app/tasks/pipeline.py` (change top-level import to lazy import)

---

#### ECB-F15: CLI Shorthand Flags (Parnas)

**What**: Add shorthand flags for frequently-used long options.

**Why**: `--causal-credence-threshold` is verbose for power users. Parnas: *"Consider also accepting `--cct` as shorthand."*

**Implementation**:
```python
# In article_eater_contract_cli.py
parser.add_argument(
    '--causal-credence-threshold', '--cct',
    type=float,
    default=0.5,
    help='Minimum credence for causal model beliefs (default 0.5)'
)
```

**Location**: `app/cli/article_eater_contract_cli.py`

---

#### ECB-F16: User Documentation Sprint (Brooks)

**What**: Create user-facing documentation for causal features.

**Why**: The bridge repair focused on the MODULE, not the USER EXPERIENCE. Brooks: *"I don't see user documentation, example notebooks, or integration tests with real data."*

**Deliverables**:
1. `docs/USER_GUIDE_CAUSAL_BRIDGE.md` — How to use causal features
2. `notebooks/causal_counterfactual_examples.ipynb` — Example queries
3. `tests/integration/test_causal_real_data.py` — Real-world validation
4. CLI examples in README

**Location**: `docs/`, `notebooks/`, `tests/integration/`

---

#### ECB-F17: Stub Contrast Warning (van Fraassen)

**What**: Add warning to stub WebOfBelief documentation about contrast class limitations.

**Why**: The demo stub doesn't model contrast classes properly. Tests using the stub may give false confidence about contrast handling. van Fraassen: *"Any tests using the stub may give false confidence."*

**Implementation**:
```python
# In quarantine/2026-02-10/epistemic_causal_bridge_features/demo_and_stub_web.py
class WebOfBelief:
    """
    MINIMAL STUB for demonstration/testing only.

    WARNING: This stub does NOT properly model contrast classes.
    - Beliefs created here lack contrast_class field
    - Tests using this stub do NOT validate contrast handling
    - Use the real WebOfBelief from web_of_belief.py for production
    """
```

**Location**: `quarantine/2026-02-10/epistemic_causal_bridge_features/demo_and_stub_web.py`

---

#### ECB-F18: DEPRECATED Removal Deadline (Parnas)

**What**: Add `# REMOVE_BY: V24.0` comments to DEPRECATED code.

**Why**: DEPRECATED code should have a removal deadline. Without it, developers don't know if it's safe to remove or still in transition. Parnas: *"DEPRECATED code should be removed in V24.0. Add a `# REMOVE_BY: V24.0` comment."*

**Implementation**:
```python
class EpistemicLevel(Enum):
    """
    DEPRECATED: Use web_of_belief.EpistemicLevel instead.
    REMOVE_BY: V24.0
    ...
    """
```

**Location**: `src/services/epistemic_causal_bridge.py` (all DEPRECATED classes)

---

### Future Archived Feature Reintegration TODOs

**Individual Differences** (after core bridge stable):
| ID | Task | Priority |
|----|------|----------|
| IND-1 | Literature review: individual difference moderators in CNfA | P2 |
| IND-2 | Populate IndividualDifferenceFactor with literature data | P2 |
| IND-3 | Add CNS questionnaire to Streamlit UI | P3 |
| IND-4 | Validate personalized predictions | P3 |

**Cultural Meanings** (after contrast transfer working):
| ID | Task | Priority |
|----|------|----------|
| CULT-1 | Literature review: cultural variation in nature concepts | P2 |
| CULT-2 | Design cultural meaning schema with anthropology input | P2 |
| CULT-3 | Populate for major cultural contexts | P3 |
| CULT-4 | Implement meaning similarity metric | P3 |
| CULT-5 | Add cultural context to PopulationContext | P3 |

**Argument Attack Analysis** (after contrast extraction working):
| ID | Task | Priority |
|----|------|----------|
| ATK-1 | Integrate attack analysis with coherence violation detection | P2 |
| ATK-2 | Add attack detection to claim extraction pipeline | P3 |
| ATK-3 | Train classifier for shift type identification | P3 |
| ATK-4 | UI for reviewing detected attacks | P3 |

---

### Sprint ECB Documentation

| Document | Purpose |
|----------|---------|
| `docs/PANEL_P-ECB-R_CONTEXT_2026-02-10.md` | Full panel context |
| `docs/PANEL_P-ECB-R_RESPONSES_2026-02-10.md` | Expert responses |
| `docs/PANEL_P-ECB-R_PLAN_REVIEW_2026-02-10.md` | Plan review with updates |
| `docs/IMPLEMENTATION_PLAN_BRIDGE_REPAIR_2026-02-10.md` | Detailed implementation plan |
| `docs/ARCHIVED_FEATURES_EPISTEMIC_CAUSAL_BRIDGE_2026-02-10.md` | Archived features documentation |

---

## Completed: Panel Consultations (2026-02-09)

**Panel P-VOI**: Value of Information - Theoretical Grounding
- Panelists: Howard, Pearl, Simon, Thagard, Haack, Bates
- Key outcomes:
  - Clarified VOI semantics (Expected Epistemic Gain, not classical VOI)
  - Separated structural VOI from epistemic VOI (Pearl)
  - Added gap type priority weights (Thagard)
  - Made epsilon-greedy ADAPTIVE based on search success (Simon)

**Panels P-S3-A through P-S3-E**: Sprint 3.0 Decisions
- 27 decisions reviewed across 10 modules
- Panelists: Amodei, Liang, Kleinberg, Higgins, Cartwright, Mayo, Munzner, van Fraassen
- Key implementations:
  - Level-dependent credence thresholds (Cartwright)
  - Effective credence accounting for uncertainty (Mayo)
  - Closure type quantification (Pearl)

See: `docs/PANEL_CONSULTATION_P-VOI_2026-02-09.md`
See: `docs/PANEL_CONSULTATION_SPRINT_3.0_CONSOLIDATED_2026-02-09.md`

---

## Pending: Article Discovery + PDF Retrieval Monitoring

**Added**: 2026-02-09
**Priority**: P1
**Context**: VOI gaps are predictions about where articles *should* exist. We need to track the full discovery funnel: gap identification → article search → PDF retrieval → successful ingestion. This closes the loop between what the system predicts it needs and what it actually acquires.

### Problem Statement

1. VOI search identifies high-value gaps in the web of belief
2. These gaps predict topics/questions where articles *should* exist
3. Article Finder searches for articles matching these gaps
4. PDF retrieval may succeed or fail (paywalls, missing files, format issues)
5. Ingestion may succeed or fail (corrupt PDFs, extraction errors)
6. **Currently no tracking of this funnel** — we don't know our success rate

### Design Goals

1. **Gap-to-Article Mapping**: Track which gaps led to which article searches
2. **Search Effectiveness**: Did searches find relevant articles?
3. **PDF Acquisition Rate**: What % of identified articles yield usable PDFs?
4. **Ingestion Success Rate**: What % of PDFs successfully enter the pipeline?
5. **Gap Closure Rate**: Did the acquired articles actually address the gaps?

### Proposed Architecture

```
VOI Gap Identification
    │
    ├── gap_id, topic, predicted_value, search_terms
    │
    ▼
Article Search Execution
    │
    ├── search_id, gap_id, query, source (Scholar, Semantic Scholar, etc.)
    ├── n_results, relevance_scores
    │
    ▼
PDF Retrieval Attempts
    │
    ├── article_id, retrieval_method (direct, Sci-Hub, library, request)
    ├── status (success, paywall, not_found, timeout, format_error)
    │
    ▼
Pipeline Ingestion
    │
    ├── paper_id, extraction_status, n_claims, n_rules
    ├── gap_addressed (did this paper reduce the gap VOI?)
    │
    ▼
Funnel Metrics Dashboard
    │
    └── Success rates at each stage, bottleneck identification
```

### Tasks

| ID | Task | Estimate | Status | Dependencies |
|----|------|----------|--------|--------------|
| DISC-1 | Design discovery_funnel schema (SQLite tables) | 2h | ✓ DONE | — |
| DISC-2 | Add gap tracking to VOI search output | 2h | ✓ DONE | DISC-1 ✓ |
| DISC-3 | Add search execution logging | 3h | ☐ TODO | Article Finder |
| DISC-4 | Add PDF retrieval tracking with failure categorization | 3h | ☐ TODO | — |
| DISC-5 | Add ingestion success/failure tracking | 2h | ☐ TODO | pipeline.py |
| DISC-6 | Compute gap closure rate (VOI before/after) | 3h | ☐ TODO | DISC-2 ✓, DISC-5 |
| DISC-7 | Build funnel metrics API endpoints | 3h | ☐ TODO | DISC-1 through DISC-6 |
| DISC-8 | Build funnel dashboard (Streamlit) | 4h | ☐ TODO | DISC-7 |
| DISC-9 | Add alerts for low success rates | 2h | ☐ TODO | DISC-7 |

### Key Metrics to Track

| Metric | Formula | Target |
|--------|---------|--------|
| Search Hit Rate | articles_found / gaps_searched | > 80% |
| PDF Acquisition Rate | pdfs_obtained / articles_identified | > 60% |
| Ingestion Success Rate | papers_ingested / pdfs_obtained | > 90% |
| Gap Closure Rate | gaps_with_reduced_voi / gaps_addressed | > 50% |
| End-to-End Rate | gaps_closed / gaps_searched | > 25% |

### Failure Categories (DISC-4)

| Category | Description | Mitigation |
|----------|-------------|------------|
| PAYWALL | Article behind paywall | Try Sci-Hub, library access, author request |
| NOT_FOUND | PDF doesn't exist at URL | Try alternate sources |
| FORMAT_ERROR | PDF corrupted or non-standard | Manual download, OCR |
| TIMEOUT | Retrieval timed out | Retry with backoff |
| RATE_LIMITED | Source rate limiting | Queue with delays |
| ACCESS_DENIED | IP blocked or auth required | Rotate sources |

### Panel Consultation Recommended

For DISC-1 schema design, consult:
- **Bates** (information seeking behavior)
- **Kleinberg** (network flow, funnel analysis)
- **Simon** (satisficing in search)
- **Pearl** (causal attribution of success/failure)

---

## Completed: Entrenchment Historical Replay + Monitor

**Added**: 2026-02-09
**Completed**: 2026-02-09
**Context**: Distinguish entrenchment history inside the system (ingestion-time) vs scholarly history (publication-time). Admins can replay the web in true historical order and see how entrenchment evolves.

### Completed Tasks

| ID | Task | Completed | Outcome |
|----|------|-----------|---------|
| ENT-1 | Add publication_year/date to paper model | 2026-02-09 | Already in schema + DB (`paper_publication` table) |
| ENT-2 | Build scholarly-time replay pipeline | 2026-02-09 | `src/services/entrenchment_replay.py` - Fixed attribute naming conflict |
| ENT-3 | Store entrenchment snapshots for both timelines | 2026-02-09 | Added query methods to `web_persistence.py`: `get_entrenchment_history()`, `get_entrenchment_events()`, `get_latest_entrenchment()`, `compare_timeline_entrenchment()`, `get_entrenchment_trajectory()` |
| ENT-4 | Admin monitor UI: dual timeline | 2026-02-09 | Created `frontend/entrenchment-monitor.html` + `app/routes/entrenchment.py` API endpoints |
| ENT-5 | Health metrics: volatility, stagnation | 2026-02-09 | Health metrics in entrenchment API: volatility, stagnation count, timeline divergence, conflict load |

### Follow-up Tasks (Phase 2)

**Context**: Replay should not mutate the live master web. Provide a safe runner that copies the DB and runs scholarly replay against the copy by default.

| ID | Task | Status |
|----|------|--------|
| ENT-6 | Decide replay DB strategy + add runner that copies live DB (no mutation) | ☐ TODO |

### Tests
- `tests/test_entrenchment_tracker.py`: 16 tests covering paper publication, replay pipeline, snapshots, health metrics

---

## Pending: AF-AE BibTeX Integration

**Added**: 2026-02-08
**Context**: Article Finder accepts user-uploaded PDFs that lack BibTeX metadata. Without metadata (title, authors, abstract, DOI, year), Article Eater cannot properly extract rules or track provenance.

### Problem Statement

1. AF hunts articles (has metadata) but also accepts direct PDF uploads (no metadata)
2. User has Zotero library with BibTeX export capability
3. Need to link uploaded PDFs to their BibTeX records
4. Need this metadata for AE rule extraction and provenance tracking

### Design Options

| Option | Where | Approach | Pros | Cons |
|--------|-------|----------|------|------|
| **A. AF Upload Enhancement** | Article Finder | Add BibTeX upload alongside PDF, match by filename or user selection | Clean separation, metadata lives with source | Requires AF changes |
| **B. AE Metadata Augmentation** | Article Eater | Accept BibTeX bundle in input_bundle, enrich paper.json | AE already handles bundles | Metadata should live upstream |
| **C. Zotero Connector** | New service | Watch Zotero export folder, auto-match PDFs by hash/filename | Automated, works with existing workflow | New service to maintain |
| **D. Manual Linking UI** | AF or Streamlit | Upload BibTeX, show unlinked PDFs, user manually matches | Handles edge cases | Manual work |

### Recommended Approach: Hybrid A + D

1. **AF Enhancement**: Add optional BibTeX upload with PDF
   - Parse BibTeX, extract fields for `paper.json`
   - Fields needed: `title`, `authors`, `abstract`, `year`, `doi`, `journal`, `volume`, `pages`

2. **Bulk Zotero Import** (for existing library):
   - User exports Zotero collection as BibTeX
   - AF/Streamlit UI shows unlinked PDFs and BibTeX entries
   - User matches them (or auto-match by title similarity)
   - Matched entries create proper `paper.json` metadata

3. **AE Contract Update**:
   - `paper.json` already has fields for this
   - Ensure `abstract` is used for extraction when fulltext unavailable
   - Add `bibtex_source` field to provenance

### Tasks

| ID | Task | Estimate | Status |
|----|------|----------|--------|
| BIB-1 | Design paper.json schema extensions for BibTeX fields | 1h | ✓ DONE (included in BIB-2) |
| BIB-2 | Add BibTeX parser utility | 2h | ✓ DONE |
| BIB-3 | AF: Add BibTeX upload option alongside PDF | 3h | ✓ DONE |
| BIB-4 | AF: Create bulk Zotero import UI | 4h | ✓ DONE (Streamlit page) |
| BIB-5 | Auto-match algorithm (title similarity, DOI, filename) | 3h | ✓ DONE |
| BIB-6 | AE: Ensure abstract extraction works when fulltext missing | 2h | ✓ DONE |
| BIB-7 | Ingest matched PDFs into AE pipeline | 3h | ✓ DONE |

---

## Pending: Extraction Tables (16 Types)

**Added**: 2026-02-08 (from WHERE_WE_STAND.md #12)
**Source**: `/Users/davidusa/REPOS/Outcome_Contractor/article_finder/exemplary_extraction_tables.md`
**Context**: Each article type needs complete field specs, rule mappings, validation rules, and AI prompts.

### Status: 16/16 Complete ✅

| # | Article Type | Status | Notes |
|---|--------------|--------|-------|
| 1 | Randomized Experiment | ✅ Complete | Full spec 2026-02-03 |
| 2 | Quasi-Experiment | ✅ Complete | Full spec 2026-02-03 |
| 3 | Cross-Sectional Survey | ✅ Complete | Full spec 2026-02-03 |
| 4 | Longitudinal Study | ✅ Complete | Full spec 2026-02-08 (panel additions) |
| 5 | Observational Field Study | ✅ Complete | Full spec 2026-02-09 |
| 6 | Phenomenological Study | ✅ Complete | Full spec 2026-02-09 (qualitative) |
| 7 | Ethnographic Study | ✅ Complete | Full spec 2026-02-09 (qualitative) |
| 8 | Grounded Theory Study | ✅ Complete | Full spec 2026-02-09 (qualitative) |
| 9 | Case Study | ✅ Complete | Full spec 2026-02-09 |
| 10 | Interview Study | ✅ Complete | Full spec 2026-02-09 (qualitative) |
| 11 | Mixed Methods | ✅ Complete | Full spec 2026-02-09 |
| 12 | Meta-Analysis | ✅ Complete | Full spec 2026-02-08 (panel additions) |
| 13 | Systematic Review | ✅ Complete | v1.1 2026-02-09 (panel additions) |
| 14 | Narrative Review | ✅ Complete | Full spec 2026-02-09 |
| 15 | Theoretical | ✅ Complete | Full spec 2026-02-09 |
| 16 | Thought Piece | ✅ Complete | Full spec 2026-02-09 |

### Next Priority
1. Complete Systematic Review (similar structure to Meta-Analysis)
2. Complete remaining synthesis types (Narrative Review)
3. Complete qualitative types (starting with Case Study)

### Each Type Needs
1. Complete field list (required/optional)
2. Mapping to rule types (which fields → which rules)
3. Validation rules (what makes extraction adequate)
4. AI prompt specifications
5. Edge cases (missing data, ambiguous findings)

### Panel Consultation Completed: 2026-02-08

**Panelists**: Walton (argumentation), Pearl (causation), Cartwright (philosophy of science), Lipton (explanation), Hearst (NLP extraction), Teufel (scientific discourse), R. Kaplan (domain)

**Document**: `/Users/davidusa/REPOS/Outcome_Contractor/docs/PANEL_CONSULTATION_EXTRACTION_TABLES_2026_02_08.md`

**Key Additions from Panel**:

| Addition | Source | Priority |
|----------|--------|----------|
| New rule types: REBUTTAL, PRESUMPTION, ASSOCIATION, CONTRAST | Walton, Pearl, Lipton | High |
| `causal_level` (association/intervention/counterfactual) | Pearl | High |
| `argument_scheme` + `critical_questions[]` | Walton | High |
| `contrast_class` + `difference_maker` | Lipton | High |
| `enabling_conditions[]` + `bridge_type` | Cartwright | Medium |
| `extraction_difficulty` + `source_zone` per field | Hearst, Teufel | Medium |
| Domain features (ART, Appleton, etc.) | Kaplan | High for CNfA |
| Stimulus documentation template | All | High |

**Immediate Action Items**:
- [x] Add new rule types to schema — DONE 2026-02-09 (ae.rule.v2.schema.json, ae.claim.v2.schema.json)
- [x] Add argument_schemes vocabulary — DONE 2026-02-09 (contracts/vocab/argument_schemes.json)
- [x] Update RCT/Quasi-Exp/Cross-Sectional with panel additions — DONE 2026-02-09 (EXTRACTION_TEMPLATE_PANEL_ADDITIONS_2026_02_09.md)
- [x] Create stimulus documentation template with domain features — DONE 2026-02-09 (STIMULUS_DOCUMENTATION_TEMPLATE_2026_02_09.md)
- [x] Complete Longitudinal Study spec (high causal value per Pearl) — DONE 2026-02-08
- [x] Complete Meta-Analysis spec (high synthesis value) — DONE 2026-02-08

---

## Pending: Extracted Tables Database (PDF Tables)

**Added**: 2026-02-08
**Context**: Track tables extracted from PDFs (results tables, demographics, etc.)

| ID | Task | Status |
|----|------|--------|
| TBL-1 | Add `extracted_tables` schema to AF database | ✓ DONE |
| TBL-2 | Add CRUD methods to Database class | ✓ DONE |
| TBL-3 | Add table extraction code (AI/API primary, pdfplumber fallback) | ✓ DONE |
| TBL-4 | Integrate with AE claim extraction | ✓ DONE |
| TBL-5 | Add table review UI | ✓ DONE |

**TBL-3 Completion (2026-02-08)**:
- Created `src/services/table_extractor.py` (~750 lines)
- `AITableExtractor`: LLM-based extraction with structured prompts for 4 table types
  - STUDY_CHARACTERISTICS, RESULTS, QUALITY_ASSESSMENT, DEMOGRAPHICS
- `PdfPlumberTableExtractor`: Geometric extraction fallback
- `HybridTableExtractor`: Combines AI + pdfplumber
- `ExtractedTable` dataclass with to_dict(), to_markdown() methods
- Conversion functions: `extracted_table_to_article_metadata()`, `extracted_table_to_rct_facts()`
- Factory function: `get_table_extractor(method, api_client, model)`
- 46 tests in `tests/test_table_extractor.py`

**TBL-4 Completion (2026-02-09)**:
- Created `src/services/table_to_claims.py` (~480 lines)
  - `TableClaim`: Claim dataclass for table-derived claims
  - `TableClaimGenerator`: Converts tables to claims by type
  - `PipelineTableIntegrator`: Integrates with pipeline
  - `extract_tables_for_pipeline()`: Convenience function
  - Export functions for tables.jsonl
- Integrated into `app/tasks/pipeline.py`:
  - Table extraction after BN export, before web integration
  - Claim merging with deduplication
  - Added to result dict: `n_tables`, `n_table_claims`
  - Added artifact: `tables_jsonl`

**TBL-5 Completion (2026-02-09)**:
- Added table review section to `scripts/ae_streamlit_control_room.py`
  - Output directory browser for tables.jsonl files
  - Table selector with metadata display
  - DataFrame visualization of table content
  - Raw JSON view in expander
  - Table-derived claims display from claims.jsonl

**BIB-2 Completion (2026-02-08)**:
- Created `src/services/bibtex_utils.py` (~700 lines, no external deps)
- `BibTeXParser`: Full BibTeX parsing with nested braces, LaTeX cleanup
- `BibTeXEntry`: Data class with `to_paper_json()` conversion
- `PDFBibTeXMatcher`: Multi-strategy matching (DOI, arXiv, title, author-year)
- `normalize_text()`, `title_similarity()`: Fuzzy matching utilities
- Created `streamlit_app/pages/1_bibtex_import.py` (~450 lines)
  - Upload BibTeX and PDFs
  - Auto-match with confidence scores
  - Manual linking for unmatched items
  - Export as paper.json bundles, match reports, or CSV
- 41 tests in `tests/test_bibtex_utils.py`

**BIB-6 Completion (2026-02-09)**:
- Added abstract fallback to `app/tasks/pipeline.py` (lines 1223-1242)
  - When PDF extraction fails or yields < 100 chars, tries paper.json abstract
  - Logs fallback usage with audit event
- Updated `contracts/ae_af/schemas/ae.paper.v1.schema.json`
  - Added optional `abstract` field with description

**BIB-3 Completion (2026-02-09)**:
- Updated `app/routes/annotator.py` with BibTeX upload endpoints
  - `POST /upload-with-bibtex`: Upload PDF + optional BibTeX file or text
  - `POST /upload-bibtex-batch`: Upload BibTeX file to register multiple papers
- BibTeX metadata creates proper paper.json for AE pipeline
- Integrates with existing BibTeX parser from bibtex_utils.py
- PDF + metadata stored together, ready for ingestion

**BIB-7 Completion (2026-02-09)**:
- Created `src/services/bibtex_ingestion.py` (~350 lines)
  - `BibTeXIngestionService`: Ingests matched PDFs into AE pipeline
  - `_create_input_bundle()`: Creates paper.json + PDF bundles
  - Also writes abstract.txt as additional fallback
  - Batch processing with progress tracking
- Convenience functions: `ingest_matched_papers()`, `ingest_single_paper()`
- Updated `streamlit_app/pages/1_bibtex_import.py`
  - Added "Run Pipeline" section with output dir and profile selection
  - Direct ingestion from UI without export step
- 14 tests in `tests/test_bibtex_ingestion.py`

---

## Parallel Work Lanes

**Coordination files**: `ACTIVE_TASKS.md` (task claims) + `PARALLEL_WORK.md` (file ownership)

| Lane | Scope | Key Files | Status |
|------|-------|-----------|--------|
| **A** | Sprint 2.5 Schema Design | `social_epistemology.py` (new) | ✓ COMPLETE |
| **B** | Sprint 2.5 Implementation | `web_of_belief.py` extensions | ✓ COMPLETE |
| **C** | TODO 1: Credibility Testing | `credibility_testing.py`, `credibility_feedback.py` | ✓ COMPLETE |
| **D** | TODO 2: Interpretive Intelligence | `interpretive_intelligence.py` | ✓ COMPLETE |
| **E** | TODO 3: VOI Search | `voi_search.py` | ✓ COMPLETE |
| **F** | Panel Convening (P-TC, P-QW) | `docs/PANEL_*.md` | ✓ COMPLETE |
| **G** | Fix Failing Tests | `test_theory_system.py`, `rulegraph_v2_builder.py` | ✓ COMPLETE |
| **H** | Commit TD Work | TD-C, TD-D, TD-E files | AVAILABLE |
| **I** | Sprint 2.0 Pipeline Integration | `app/tasks/pipeline.py` | AVAILABLE |

**Recommended parallel pairs** (minimal conflicts):
- Lane A + Lane E (Schema + VOI)
- Lane C + Lane F (Credibility + Panels)
- Lane D + Lane E (Interpretive + VOI)

**Claim a lane**: Edit `PARALLEL_WORK.md` → Active Claims table

---

## Active Panels

Panels evaluate work during sprints. After evaluation: replan → patch code → continue.

### Panel Registry

| Panel ID | Name | Scope | Members | Status |
|----------|------|-------|---------|--------|
| P-EC | Epistemic-Causal Integration | `epistemic_causal_integration.py`, `epistemic_to_causal_bridges.py`, `web_of_belief.py` | Pearl, Quine, van Fraassen, Cartwright, Thagard, Longino | COMPLETE (Sprint 1.5) |
| P-QW | Quality-Weighted Entrenchment | `web_persistence.py`, `extraction_to_web.py` | Pearl, Cartwright, Simon, Bates, Kaplan, Mayo | ✓ CONSULTED (6 decisions) |
| P-SE | Social Epistemology | `social_epistemology.py` | Longino, Kitcher, Knorr Cetina, Collins, Kuhn | ✓ CONSULTED (5 questions) |
| P-TC | Task Context | `task_taxonomy.json`, claim schema | Klein, Ericsson, Kahneman, R. Kaplan, Simon, Suchman | ✓ CONSULTED (7 decisions) |
| P-TD | Technical Debt | `web_of_belief.py`, `extraction_to_web.py` | Thagard, Simon, Cartwright, Mayo, Bates, Pustejovsky, Manning, Kleinberg, Hearst | ✓ CONSULTED (4 items) |

### Panel Invocation Protocol

```
Sprint Work → Decision Accumulates → Threshold Met (≥5) OR Sprint Boundary
                                            ↓
                              Panel Consultation Triggered
                                            ↓
                    Panel Evaluates → Recommendations Generated
                                            ↓
                         Replan → Patch Code → Mark Resolved
                                            ↓
                                   Continue Sprint
```

---

## Sprint 1.5: Epistemic-Causal Integration

**Status**: IN PROGRESS (90% complete)
**Panel**: P-EC (Epistemic-Causal Integration)
**Source**: `/Users/davidusa/REPOS/research/claude_epist_layer adds K to causal BN/`

### Completed

| ID | Task | Completed | Outcome |
|----|------|-----------|---------|
| 1.5.1 | Core integration architecture | 2026-02-08 | `epistemic_causal_integration.py` (~800 lines) |
| 1.5.2 | Five epistemic-to-causal bridges | 2026-02-08 | `epistemic_to_causal_bridges.py` (~600 lines) |
| 1.5.3 | Panel concern resolutions | 2026-02-08 | `panel_concern_resolutions.py` (~500 lines) |
| 1.5.4 | Van Fraassen contrast class design | 2026-02-08 | `van_fraassen_contrast_class.md` |
| 1.5.5 | Expert panel: Quinean vs Pearl | 2026-02-08 | `expert_panel_quinean_vs_pearl.md` |
| 1.5.6 | Expert panel: Integration review | 2026-02-08 | `expert_panel_epistemic_causal_integration.md` |
| 1.5.7 | Expert panel: Synergies | 2026-02-08 | `expert_panel_synergies.md` |
| 1.5.8 | Sprint plan | 2026-02-08 | `__sprint_plan_v1.md` |

### In Progress

| ID | Task | Started | Notes |
|----|------|---------|-------|
| 1.6.1 | Inference type tagging | 2026-02-08 | Ready to start |

### Panel P-EC Complete (2026-02-08)

**Verdict**: SPRINT 1.5 APPROVED

**High-Priority Recommendations for Sprint 1.6**:
| ID | Recommendation | Source |
|----|----------------|--------|
| P-EC-R9 | Check `enabling_conditions` before counterfactuals | Cartwright |
| P-EC-R12 | Integrate `CoherenceCache` for scalability | Thagard |
| P-EC-R14 | Query-local coherence computation | Thagard |
| P-EC-R8 | "Contrast not transferable" warnings | van Fraassen |

**Full review**: `docs/PANEL_P-EC_SPRINT_1.5_REVIEW_2026_02_08.md`

### Recently Completed (Sprint 1.5 — ALL DONE)

| ID | Task | Completed | Outcome |
|----|------|-----------|---------|
| 1.5.11 | Documentation update | 2026-02-08 | Updated CLAUDE.md with Sprint 1.5 capabilities, architecture diagram, essential files |
| 1.5.10 | Wire into `web_of_belief.py` | 2026-02-08 | Added `create_causal_bridge()`, `counterfactual()`, `causal_bridge_available()` methods. 34 tests. |
| 1.5.9 | Integration tests for bridge | 2026-02-08 | 29 tests. Fixed `_get_theory_beliefs()` for `theory_id`/`theory_ids` compatibility |

### Panel Evaluation Required

After 1.5.9-1.5.11 complete → P-EC panel evaluates integration with existing `src/services/web_of_belief.py`

---

## Sprint 1.6: Quick Wins

**Status**: COMPLETE
**Panel**: P-EC (same panel evaluates)
**Completed**: February 8, 2026

### Completed

| ID | Task | Completed | Outcome |
|----|------|-----------|---------|
| 1.6.1 | Inference type tagging | 2026-02-08 | `InferenceType` enum (INDUCTIVE, DEDUCTIVE, ABDUCTIVE, MIXED, UNKNOWN) added to Belief |
| 1.6.2 | Belief type tagging | 2026-02-08 | `BeliefKind` enum (MECHANISTIC, EVIDENTIAL, THEORETICAL, METHODOLOGICAL, BRIDGE) added to Belief |
| 1.6.3 | Value computation | 2026-02-08 | `belief_centrality()`, `belief_sensitivity()`, `belief_value()`, `beliefs_by_value()`, `high_value_beliefs()` methods in WebOfBelief |
| 1.6.4 | Tension-resolving experiments | 2026-02-08 | `suggest_experiments()`, `get_research_priorities()` methods in WebOfBelief. 13 new tests. |

### P-EC Panel Recommendations Implemented

| ID | Recommendation | Status | Outcome |
|----|----------------|--------|---------|
| P-EC-R9 | Check `enabling_conditions` before counterfactuals | COMPLETE | `_check_enabling_conditions()`, `_track_blocked_belief()`, `get_blocked_beliefs()` added to EpistemicCausalBridge |

### Total Tests: 68 passing

### Panel Checkpoint

Sprint 1.6 complete → Ready for P-EC panel evaluation of tagging accuracy and value computation validity

---

## Sprint 2.5: Social Epistemology

**Status**: COMPLETE
**Panel**: P-SE (Social Epistemology) — CONSULTED (2026-02-08)
**Design Document**: `docs/SPRINT_2.5_DESIGN.md`
**Schema**: `contracts/schemas/social_epistemology.schema.json`
**Module**: `src/services/social_epistemology.py` (~1300 lines)
**Tests**: 54 passing

### Completed

| ID | Task | Completed | Outcome |
|----|------|-----------|---------|
| 2.5.1 | Design community schema | 2026-02-08 | Multi-criteria identification: theory (0.35), exemplars (0.25), methods (0.25), citations (0.15) |
| 2.5.2 | Design `EpistemicCommunity` class | 2026-02-08 | Full class design with metrics, hierarchy, history events |
| 2.5.3 | Design `BeliefProvenance` class | 2026-02-08 | Tracks origins, community credences, contestation |
| 2.5.4 | Implement `EpistemicCommunity` | 2026-02-08 | Vocabulary overlap, track record weighting, history events |
| 2.5.5 | Implement `BeliefProvenance` | 2026-02-08 | Community credences, contestation detection, aggregation (per SE-2) |
| 2.5.6 | Implement `ContestationTracker` | 2026-02-08 | Track disputes, experimenter's regress detection (Collins) |
| 2.5.7 | Implement `MethodologicalDiversityAssessor` | 2026-02-08 | Diversity index, vulnerability detection, diversification suggestions |
| 2.5.8 | Integrate with Belief class | 2026-02-08 | Added `provenance`, `community_associations`, `get_community_credence()`, `is_community_contested()` |
| 2.5.9 | Tests | 2026-02-08 | 54 tests covering all classes and integration |
| 2.5.10 | CommunityRegistry | 2026-02-08 | CRUD operations, vocabulary-based lookup, serialization |
| 2.5.11 | CNFA Seed Data | 2026-02-08 | ART, SRT, Biophilia, Environmental Psychology communities

### Panel Questions P-SE — RESOLVED (2026-02-08)

| Q# | Question | Decision | Rationale |
|----|----------|----------|-----------|
| SE-1 | How identify communities? | Multi-criteria: theory (0.35), exemplars (0.25), methods (0.25), citations (0.15) | Per Longino, Kuhn, Knorr Cetina |
| SE-2 | How aggregate disagreeing communities? | Report separately by default; average only for empirical, within-paradigm | Per Longino, Kuhn |
| SE-3 | How represent power asymmetries? | Track separately from credence; use domain-specific track record | Per Longino, Kitcher |
| SE-4 | Track historical changes? | Snapshot-based with event annotations | Per Kitcher, Collins |
| SE-5 | What granularity? | Three-tier hierarchy: Field > Paradigm > Lab | Per Longino, Knorr Cetina |

---

## Sprint 2.6: Panel Decision Implementation

**Status**: COMPLETE (2026-02-08)
**Panels**: P-TC (Task Context), P-QW (Quality-Weighted Entrenchment)
**Dependencies**: Sprint 2.5 complete ✓

### Track A: Task Context (P-TC Decisions) — ✓ COMPLETE

**Target Files**: `src/services/extraction_to_web.py`

| ID | Task | Source | Description | Status |
|----|------|--------|-------------|--------|
| 2.6.1 | Add `inference_basis` field | P-TC D1 | Track whether task context is stated/inferred/unknown | ✓ DONE |
| 2.6.2 | Add `review_recommended` flag | P-TC D3 | Flag claims with keyword inference confidence <0.7 | ✓ DONE |
| 2.6.3 | Add `presumed_lab` flag | P-TC D4 | Default `lab_task` with `presumed: true` when not stated | ✓ DONE |
| 2.6.4 | Add `effective_demand` calculation | P-TC D6 | Compute effective_demand = skill × cognitive_demand | ✓ DONE |
| 2.6.5 | Add `mechanism_only` tag | P-TC D7 | Tag pure psych/neuro papers without design implications | ✓ DONE |
| 2.6.6 | Helper functions | — | `extract_task_context()`, `compute_effective_demand()`, `is_mechanism_only()` | ✓ DONE |
| 2.6.7 | Integration with claim_to_belief | — | Sprint 2.6 fields set in mapping pipeline | ✓ DONE |

**New Classes/Functions**:
- `TaskContextResult` dataclass
- `extract_task_context(claim)` - instrument/keyword matching
- `compute_effective_demand(cognitive_demand, skill_level)` - Ericsson matrix
- `is_mechanism_only(claim)` - D7 detection

### Track B: Quality-Weighted Entrenchment (P-QW Decisions) — ✓ COMPLETE

**Target Files**: `src/services/web_persistence.py`, `contracts/vocab/institution_tiers.json`

| ID | Task | Source | Description | Status |
|----|------|--------|-------------|--------|
| 2.6.8 | Reduce institution weight | P-QW Q2 | Changed to 0.12 in QUALITY_WEIGHTS | ✓ DONE |
| 2.6.9 | Add institutions to tier list | P-QW Q2 | Wageningen, Uppsala, JCU added as Tier 1 | ✓ DONE |
| 2.6.10 | Update component weights | P-QW Q4 | QUALITY_WEIGHTS dict with new weights | ✓ DONE |
| 2.6.11 | Add citation velocity | P-QW Q5 | `citation_velocity(count, year)` function | ✓ DONE |
| 2.6.12 | Implement piecewise mapping | P-QW Q6 | `quality_to_entrenchment()` with floor at 0.3 | ✓ DONE |
| 2.6.13 | Publish institution tier list | P-QW Q2 | Created `contracts/vocab/institution_tiers.json` | ✓ DONE |
| 2.6.14 | Update save_paper_quality | — | Extended with institution, h_index, pub_year, eco_validity | ✓ DONE |

**New Functions**:
- `citation_velocity(citation_count, publication_year)` - Q5
- `quality_to_entrenchment(overall_quality)` - Q6 piecewise
- `get_institution_tier(institution)` - Q2 tier lookup
- `institution_tier_to_score(tier)` - tier to quality score

**New Files**:
- `contracts/vocab/institution_tiers.json` - published tier list

**Tests**: 62 web_persistence tests passing

### Approved (No Code Changes Needed)

| Source | Decision | Note |
|--------|----------|------|
| P-TC D2 | Instrument mapping confidence 0.95 | Keep as-is, add `transfer_uncertainty` to docs |
| P-TC D5 | Rate limit 0.1s with API key | Keep as-is |
| P-QW Q1 | Citation thresholds 8-tier | Keep as-is |
| P-QW Q3 | h-index tier boundaries | Keep as-is |

---

## Pending Panel Decisions

### P-TC: Task Context Decisions — CONSULTED (2026-02-08)

**Status**: PANEL COMPLETE
**Review**: `docs/PANEL_P-TC_TASK_CONTEXT_REVIEW_2026_02_08.md`

| D# | Decision | Panel Verdict | Action |
|----|----------|---------------|--------|
| D1 | Default task when unknown | MODIFY | Add `inference_basis` field (stated/inferred/unknown) |
| D2 | Instrument mapping confidence | APPROVE | Keep 0.95, add `transfer_uncertainty` caveat |
| D3 | Keyword inference confidence | MODIFY | Keep 0.5-0.7, add `review_recommended` flag for <0.7 |
| D4 | Default ecological validity | MODIFY | Default `lab_task` with `presumed: true` flag |
| D5 | Rate limit with API key | APPROVE | Keep 0.1s |
| D6 | Cognitive demand levels | MODIFY | Keep 3 levels, add `effective_demand` from skill×demand |
| D7 | Include pure psych/neuro papers | APPROVE | Include with `mechanism_only` tag |

**Implementation**: → **Sprint 2.6 Track A** (tasks 2.6.1–2.6.7)

### P-QW: Quality-Weighted Entrenchment Decisions — CONSULTED (2026-02-08)

**Status**: PANEL COMPLETE
**Review**: `docs/PANEL_P-QW_QUALITY_WEIGHTED_ENTRENCHMENT_REVIEW_2026_02_08.md`

| Q# | Decision | Panel Verdict | Action |
|----|----------|---------------|--------|
| Q1 | Citation thresholds | APPROVE | Keep 8-tier system |
| Q2 | Institution tier assignments | MODIFY | Reduce weight to 0.12, add Wageningen/Uppsala/JCU, publish list |
| Q3 | h-index tier boundaries | APPROVE | Keep current boundaries |
| Q4 | Weighting of quality components | MODIFY | Meth 0.28, Cite 0.18, Inst 0.12, Auth 0.18, Prereg 0.10, Sample 0.10, EcoVal 0.04 |
| Q5 | Career stage adjustment | MODIFY | Replace with citation velocity (citations/year) |
| Q6 | Quality → entrenchment mapping | MODIFY | Piecewise: Quality < 0.3 → 0.10; else linear 0.15-0.70 |

**Implementation**: → **Sprint 2.6 Track B** (tasks 2.6.8–2.6.14)

---

## Panel Recommendations Tracking

### From P-EC (Epistemic-Causal) — Awaiting Implementation

| Rec# | Source Panel | Recommendation | Target Sprint | Status |
|------|--------------|----------------|---------------|--------|
| EC-1 | Thagard | Two-layer architecture documentation | 1.5 | PENDING |
| EC-2 | Longino | Dialectical structure tracking | 2.5 | PLANNED |
| EC-3 | Cartwright | Scope metadata with boundary conditions | 1.6 | PENDING |
| EC-4 | Chang | Iteration tracking for epistemic development | 2.0 | PLANNED |
| EC-5 | Case | Learning pathway support for education | 3.0 | DEFERRED |
| EC-6 | Mitchell | Community-relative entrenchment | 2.5 | PLANNED |
| EC-7 | Gopnik | Empirical validation against expert judgment | 2.0 | PLANNED |
| EC-8 | Thagard | Efficient coherence approximations | Tech Debt | LOGGED |
| EC-9 | van Fraassen | Cultural meaning beyond baselines | 2.5 | PLANNED |

### From P-EC Synergies Panel — Awaiting Implementation

| Rec# | Source | Recommendation | Target Sprint | Status |
|------|--------|----------------|---------------|--------|
| SY-1 | Pearl | Causal diagnosis of credence differences | 2.0 | PLANNED |
| SY-2 | Spirtes/Glymour | Causal discovery from mechanism beliefs | 3.0 | DEFERRED |
| SY-3 | Griffiths | EM-style joint optimization | 3.0 | DEFERRED |
| SY-4 | Eberhardt | Active learning infrastructure | 3.0 | DEFERRED |
| SY-5 | Murphy | Joint Bayesian inference | 3.0 | DEFERRED |
| SY-6 | van Fraassen | Contrast-relative causal discovery | 2.0 | PLANNED |
| SY-7 | Cartwright | Capacity inference | 2.5 | PLANNED |
| SY-8 | Longino | Paradigm-relative models | 2.5 | PLANNED |
| SY-9 | Chang | Belief value analysis | 1.6 | PENDING |

---

## Technical Debt

**Panel**: P-TD (Technical Debt) — CONSULTED (2026-02-08)
**Review**: `docs/PANEL_P-TD_TECHNICAL_DEBT_REVIEW_2026_02_08.md`

| ID | Item | Priority | Panel Recommendation | Sprint |
|----|------|----------|---------------------|--------|
| TD-1 | Coherence O(n²) → O(n log n) | 3 | Hierarchical + constraint network + caching | TD-C |
| TD-2 | Theory inference accuracy | 1 | Embedding similarity + keyword disambiguation (target 85%) | TD-A |
| TD-3 | Scope metadata missing | 2 | Section-aware hybrid extraction + generalization_risk | TD-B |
| TD-4 | Temporal parsing | 4 | spaCy patterns + LLM fallback | TD-D |

### Technical Debt Sprints (Panel-Recommended Order)

**Sprint TD-A: Theory Inference** (TD-2) — ✓ COMPLETE (2026-02-08)
| Task | Description | Status |
|------|-------------|--------|
| TD-A.1 | Add sentence-transformers dependency | ✓ |
| TD-A.2 | Create theory description embeddings | ✓ |
| TD-A.3 | Implement EmbeddingTheoryMatcher class | ✓ |
| TD-A.4 | Add disambiguation rules for false positives | ✓ |
| TD-A.5 | Add confidence scores to theory assignments | ✓ |
| TD-A.6 | Write tests (43 passing) | ✓ |
| TD-A.7 | Integrate with extraction_to_web.py | ✓ |

**Files created**: `src/services/theory_matcher.py` (~400 lines), `tests/test_theory_matcher.py` (43 tests)

**Sprint TD-B: Scope Extraction** (TD-3) — ✓ COMPLETE (2026-02-08)
| Task | Description | Status |
|------|-------------|--------|
| TD-B.1 | Add spaCy NER patterns for scope entities | ✓ |
| TD-B.2 | Implement section-aware extraction | ✓ |
| TD-B.3 | Add explicit vs. inferred tracking | ✓ |
| TD-B.4 | Calculate generalization_risk | ✓ |
| TD-B.5 | Create ScopeExtractor class | ✓ |
| TD-B.6 | Integrate with extraction_to_web.py | ✓ |
| TD-B.7 | Write tests (51 passing) | ✓ |

**Files created**: `src/services/scope_extractor.py` (~500 lines), `tests/test_scope_extractor.py` (51 tests)

**Sprint TD-C: Scalability** (TD-1) — ✓ COMPLETE (2026-02-08)
| Task | Description | Status |
|------|-------------|--------|
| TD-C.1 | Implement theory-based belief clustering | ✓ |
| TD-C.2 | Add hierarchical coherence computation | ✓ |
| TD-C.3 | Add coherence caching with invalidation | ✓ |
| TD-C.4 | Benchmark at 5000 beliefs (<100ms target) | ✓ |
| TD-C.5 | Add constraint network for explicit relations | ✓ |
| TD-C.6 | Write tests (64 passing) | ✓ |

**Files created**: `src/services/scalable_coherence.py` (~1000 lines), `tests/test_scalable_coherence.py` (64 tests)

**Sprint TD-D: Temporal** (TD-4) — ✓ COMPLETE (2026-02-08)
| Task | Description | Status |
|------|-------------|--------|
| TD-D.1 | Add temporal patterns (duration, frequency, relations) | ✓ |
| TD-D.2 | Implement duration normalization (to minutes) | ✓ |
| TD-D.3 | Add temporal relation extraction (before/after/during) | ✓ |
| TD-D.4 | Integrate with scope extraction | ✓ |
| TD-D.5 | Write tests (67 passing) | ✓ |

**Files created**: `src/services/temporal_parser.py` (~900 lines), `tests/test_temporal_parser.py` (67 tests)

**Sprint TD-E: Incremental BN Learning** — ✓ COMPLETE (2026-02-08)
| Task | Description | Status |
|------|-------------|--------|
| TD-E.1 | Implement BetaBernoulliEdge with conjugate updates | ✓ |
| TD-E.2 | Create IncrementalBNBuilder class | ✓ |
| TD-E.3 | Add uncertainty tracking (credible intervals per edge) | ✓ |
| TD-E.4 | Connect VOI search to edge uncertainty | ✓ |
| TD-E.5 | Implement streaming parameter updates | ✓ |
| TD-E.6 | Add active learning prioritization | ✓ |
| TD-E.7 | Write tests (41 passing) | ✓ |

**Files created**: `src/services/incremental_bn.py` (~600 lines), `tests/test_incremental_bn.py` (41 tests)

**Extended Panel for TD-E** (Online Learning): M. Jordan, Gelman, Griffiths, Blei, Ghahramani, de Freitas

---

## Future Work (Post-Sprint 2.5)

### Sprint 2.0: Pipeline Integration

**Status**: ✓ COMPLETE (2026-02-08)

| ID | Task | Estimate | Dependencies | Status |
|----|------|----------|--------------|--------|
| 2.0.1 | Wire `extraction_to_web.py` into `pipeline.py` | 2h | Sprint 1.5 | ✓ DONE |
| 2.0.2 | Implement output serialization | 3h | — | ✓ DONE |
| 2.0.3 | Add CLI flags for web outputs | 2h | — | ✓ DONE |
| 2.0.4 | Test with sample papers | 4h | All above | ✓ DONE |
| 2.0.5 | Error handling and logging | 2h | All above | ✓ DONE |

**Sprint 2.0.5 Completion (2026-02-08)**:
- Created `src/services/pipeline_logging.py` (~400 lines)
- Custom exception hierarchy: PipelineError, ExtractionError, LLMError, ConfigurationError, WebIntegrationError, SerializationError, DatabaseError, ValidationError, RetryableError
- ErrorCollector class for structured error tracking with severity levels (FATAL, BLOCKING, DEGRADED, WARNING, INFO)
- ErrorRecord dataclass for serializable error records
- `with_retry` decorator for transient failure recovery with exponential backoff
- `pipeline_stage` context manager for stage-level error handling
- Structured JSON logging with configurable format (structured/simple)
- Environment variable configuration: AE_LOG_LEVEL, AE_LOG_FORMAT, AE_LOG_FILE
- Enhanced pipeline.py with try/except blocks for validation, extraction, and serialization stages
- New output file: `errors.jsonl` written when errors are collected
- 32 new tests (`test_pipeline_logging.py`)
- All 1346 tests passing

**Sprint 2.0.1 Completion (2026-02-08)**:
- Wired TD-C (Scalable Coherence) into pipeline.py
- Wired TD-E (Incremental BN Learning) into pipeline.py
- Added CoherenceManager for O(n log n) coherence computation
- Added IncrementalBNBuilder for Bayesian parameter updates
- Added `bn_incremental_state.json` output file
- Added TD statistics to coherence_summary.json
- 13 new integration tests (`test_pipeline_td_wiring.py`)

**Sprint 2.0.2 Completion (2026-02-08)**:
- Created `src/services/output_serializer.py` (~500 lines)
- Manifest generation with SHA256 checksums for all outputs
- Theory inference export (TD-A audit trail)
- Scope condition export (TD-B)
- Temporal expression export (TD-D)
- Cluster statistics export (TD-C)
- BN edge export with 95% credible intervals (TD-E)
- Enhanced belief serialization with all TD module data
- Schema versions for all output types
- 20 new tests (`test_output_serializer.py`)
- New pipeline outputs: `manifest.json`, `cluster_stats.json`, `bn_edges.json`

**Sprint 2.0.3 Completion (2026-02-08)**:
- Added Web of Belief CLI flags: `--web/--no-web`, `--web-equilibrium/--no-web-equilibrium`, `--web-max-iterations`, `--web-convergence-threshold`
- Added Export control CLI flags: `--export-manifest/--no-export-manifest`, `--export-bn/--no-export-bn`, `--export-cluster-stats/--no-export-cluster-stats`, `--export-bn-edges/--no-export-bn-edges`
- Updated `run_from_contract_bundle()` and `_integrate_into_web_of_belief()` to accept `web_options` and `export_options`
- Web integration can now be completely disabled via `--no-web`
- Environment variables overridden by CLI flags
- 9 new tests (`test_cli_web_flags.py`)

**Sprint 2.0.4 Completion (2026-02-08)**:
- Tested pipeline with `contracts/ae_af/examples/input_bundle_minimal`
- Fixed V23 entrenchment compatibility issues:
  - Added `entrenchment` property to Belief class (returns `_legacy_entrenchment`)
  - Updated all Belief constructors to use `_legacy_entrenchment=` parameter
  - Fixed 3 test files: test_epistemic_causal_integration.py, test_web_persistence.py, test_phase1_refined_epistemic.py
- All outputs verified:
  - `web_state.json`: 8 beliefs, 3 constraints, coherence=0.5
  - `manifest.json`: SHA256 checksums for all 8 output files
  - `cluster_stats.json`: 6 clusters (3 theory, 2 level, 1 orphan)
  - `bn_edges.json`: 2 edges with 95% credible intervals
  - `coherence_summary.json`: TD-C scalable coherence used, TD-E incremental BN used
- All 1442 tests passing

### Sprint 3.0: Full Integration

**Status**: IN PROGRESS
**Panel**: P-S3 (21 experts consulted — see `docs/SPRINT_3.0_PLAN.md`)
**Interface**: Streamlit (primary) + FastAPI (backend)
**Philosophy**: User-type-driven design with pre-populated common questions

---

#### Sprint 3.0.1: Unified API (Foundation)

| ID | Task | Priority | Deliverable | Status |
|----|------|----------|-------------|--------|
| 3.0.1-A | Design resource-based API (~25 endpoints) | P1 | `docs/API_DESIGN_SPRINT_3.0.1.md` | ✅ DONE 2026-02-09 |
| 3.0.1-B | Implement Core Layer (7 high-use endpoints) | P1 | `app/routes/api_unified.py` | ✅ DONE 2026-02-09 |
| 3.0.1-C | Add versioning, pagination, async support | P1 | `app/routes/api_unified.py` | ✅ DONE 2026-02-09 |
| 3.0.1-D | Implement Extended Layer (20 endpoints) | P2 | `app/api/v1/extended/` | Pending |
| 3.0.1-E | Add batch operations endpoint | P2 | `app/api/v1/batch/` | Pending |
| 3.0.1-F | Add causal endpoints | P2 | `app/api/v1/causal/` | Pending |

**Core 7 Endpoints** (per Simon's layered API):
1. `/api/v1/beliefs/` — Belief CRUD + search
2. `/api/v1/queries/` — Natural language query execution
3. `/api/v1/export/` — Evidence summaries, BibTeX, bundles
4. `/api/v1/communities/` — Community-relative operations
5. `/api/v1/constraints/` — Epistemic constraints
6. `/api/v1/papers/` — Paper/source management
7. `/api/v1/admin/` — System state, health, statistics

---

#### Sprint 3.0.2: Query Engine (Intelligence)

| ID | Task | Priority | Deliverable | Status |
|----|------|----------|-------------|--------|
| 3.0.2-A | Query type detection (Pearl: associational/interventional/counterfactual) | P1 | `src/services/query_parser.py` | ✅ DONE 2026-02-09 |
| 3.0.2-B | Progressive disclosure response format (Simon: headline→summary→detail) | P1 | `src/services/query_response.py` | ✅ DONE 2026-02-09 |
| 3.0.2-C | Scope-aware output generation (Cartwright) | P1 | `src/services/scope_renderer.py` | ✅ DONE 2026-02-09 |
| 3.0.2-D | Practitioner mode with design implications (Kaplan) | P1 | Integrated in 3.0.2-B | ✅ DONE 2026-02-09 |
| 3.0.2-E | LLM integration (Haiku for parsing, Sonnet for synthesis) | P1 | `src/services/llm_query_bridge.py` | ✅ DONE 2026-02-09 |
| 3.0.2-F | Add RELATED, TRENDING, CANONICAL patterns (Bates) | P2 | `src/services/llm_query_bridge.py` | ✅ DONE 2026-02-09 |
| 3.0.2-G | Alerting/monitoring capability | P3 | `src/services/query_alerts.py` | ✅ DONE 2026-02-09 (panel review) |

**Query Types** (10 patterns):
- WHAT, WHY, COMPARE, GAPS, CONTRADICT, CONTINGENT, HOW_CONFIDENT
- NEW: RELATED, TRENDING, CANONICAL (Bates recommendation)

---

#### Sprint 3.0.3: Streamlit Interface (Understanding)

| ID | Task | Priority | Deliverable | Status |
|----|------|----------|-------------|--------|
| 3.0.3-A | Core Streamlit app with user type selection | P1 | `streamlit_app/main.py` | ✅ DONE 2026-02-09 |
| 3.0.3-B | Query interface with common questions per user type | P1 | `streamlit_app/pages/query.py` | ✅ DONE 2026-02-09 |
| 3.0.3-C | Claim network graph (D3.js/vis.js via components) | P1 | `streamlit_app/components/network.py` | ✅ DONE 2026-02-09 |
| 3.0.3-D | Admin dashboard (beliefs, constraints, system state) | P1 | `streamlit_app/pages/5_admin.py` | ✅ DONE 2026-02-09 |
| 3.0.3-E | Overview-zoom-filter-details interaction (Shneiderman) | P1 | JS interaction layer | ✅ DONE 2026-02-09 |
| 3.0.3-F | GraphML export for Gephi/Cytoscape | P2 | `src/services/graph_export.py` | ✅ DONE 2026-02-09 |
| 3.0.3-G | Community structure visualization | P2 | `streamlit_app/pages/3_communities.py` | ✅ DONE 2026-02-09 |
| 3.0.3-H | Interactive HTML export (standalone) | P2 | `src/services/graph_export.py` | ✅ DONE 2026-02-09 |

**3.0.3-A/B Implementation Notes (2026-02-09)**:
- Created `streamlit_app/query_service.py` (~500 lines) — Direct query service layer
- Updated `streamlit_app/api_client.py` — Added direct mode fallback
- Existing `main.py` already had user type selection (Cooper personas)
- Existing `pages/1_query.py` already had common questions interface
- Direct service uses `query_parser.py` for rule-based intent detection
- Supports quick/standard/deep response modes
- Scope-aware output with Cartwright-style conditions
- 35 tests passing (`tests/test_streamlit_query_service.py`)

**User Types with Common Questions** (Cooper personas):

| User Type | Persona | Example Questions (5-10) |
|-----------|---------|-------------------------|
| **Practitioner/Designer** | Marcus Williams | "What reduces stress in hospitals?", "Evidence for plants in offices?", "Windows vs skylights for wellbeing?", "Practical recommendations for waiting rooms", "Dosage for biophilic elements?" |
| **Senior Researcher** | Dr. Sarah Chen | "Gaps in biophilic design research?", "Methodological concerns in findings?", "Mechanisms explaining nature-health links?", "ART vs SRT evidence quality?", "Impact if Ulrich 1984 retracted?" |
| **Graduate Student** | Jordan Taylor | "How does ART theory work?", "Key papers on biophilia?", "What's contested in this field?", "Where should I focus my thesis?", "Explain the evidence hierarchy" |
| **Systematic Reviewer** | — | "All evidence for outcome X", "Studies with RCT methodology", "Export citations for stress reduction", "Cross-study comparison table" |
| **Quick Lookup** | — | "Credence for claim X?", "What supports Y?", "Is Z established or contested?" |

**3.0.3-C/E Implementation Notes (2026-02-09)**:
- Created `streamlit_app/components/network.py` (~300 lines) — Reusable network component
- Wraps `src/services/network_service.py` (~1050 lines) with comprehensive vis.js integration
- `render_claim_network()` — Main visualization function with layout/clustering options
- `render_network_controls()` — Sidebar widgets for layout algorithm, clustering, max nodes
- `render_network_metrics()` — Graph metrics display (nodes, edges, density, degree)
- `render_node_focus_view()` — Focus on node neighborhood (2-hop by default)
- `get_beliefs_from_web()` — Direct WebOfBelief data retrieval
- Updated `pages/2_explore.py` to use component with real constraint data
- Shneiderman's mantra implemented: Overview (full graph) → Zoom (pan/zoom controls) → Filter (sidebar filters) → Details (node click shows constraints/evidence)
- Layout algorithms: force-directed (default), Barnes-Hut, repulsion, hierarchical
- Clustering modes: theory, level, status, community
- Node color by status, size by credence, edge color by polarity

**3.0.3-D Implementation Notes (2026-02-09)**:
- Updated `streamlit_app/pages/5_admin.py` to use real data from WebOfBelief and API
- Added data access functions: `get_system_stats()`, `get_health_status()`, `get_real_beliefs()`, `get_real_constraints()`, `get_real_communities()`, `get_real_papers()`
- System Overview now shows real counts from WebOfBelief
- Health checks verify: API server, SQLite database, WebOfBelief status, LLM configuration
- Belief Browser with live filtering by status, level, credence, and search
- Constraint Viewer with real constraints and statistics (positive/negative counts)
- Community Browser with CommunityRegistry data and sample beliefs
- Paper Browser with SQLite database queries

**3.0.3-F/G/H Implementation Notes (2026-02-09)**:
- Created `src/services/graph_export.py` (~1100 lines) — Multi-format graph export
- **GraphML export**: Full support for Gephi, Cytoscape, yEd, NetworkX, igraph
- **GEXF export**: Gephi native format with visual attributes (color by status, size by credence)
- **JSON export**: D3.js/vis.js compatible with metrics
- **DOT export**: Graphviz format with color coding
- **Interactive HTML export**: Self-contained vis.js visualization with:
  - Sidebar filters (search, credence slider, status checkboxes)
  - Layout algorithm selector (force-directed, Barnes-Hut, repulsion)
  - Node click info panel
  - Legend and navigation controls
- Updated `streamlit_app/pages/3_communities.py` with network visualization tab
- Community network shows: theory nodes, contestation edges (dashed red), shared belief edges (green)
- Real data from CommunityRegistry with fallback to defaults

---

#### Sprint 3.0.4: Export (Delivery)

| ID | Task | Priority | Deliverable | Status |
|----|------|----------|-------------|--------|
| 3.0.4-A | Evidence summary generator with scope metadata (Cartwright) | P1 | `src/services/evidence_summarizer.py` | ✅ DONE 2026-02-09 |
| 3.0.4-B | Pipeline-friendly formats (JSONL, Parquet) (Zaharia) | P1 | `src/services/export_formats.py` | ✅ DONE 2026-02-09 |
| 3.0.4-C | Verification checklists (Gawande) | P1 | `src/services/export_checklists.py` | ✅ DONE 2026-02-09 |
| 3.0.4-D | BibTeX generator with full metadata | P2 | `src/services/bibtex_generator.py` | Pending |
| 3.0.4-E | Purpose-driven export bundles (Munzner) | P2 | `src/services/export_bundles.py` | Pending |
| 3.0.4-F | Report generation (PDF/Markdown) | P3 | `src/services/report_generator.py` | ✅ DONE (Sprint 3.0.5-G) |

---

#### Sprint 3.0.5: Admin & System Inspection

| ID | Task | Priority | Deliverable | Status |
|----|------|----------|-------------|--------|
| 3.0.5-A | Admin dashboard in Streamlit | P1 | `streamlit_app/pages/admin.py` | Pending |
| 3.0.5-B | Belief inspector (browse, search, filter) | P1 | Admin component | Pending |
| 3.0.5-C | Constraint viewer (network visualization) | P1 | Admin component | Pending |
| 3.0.5-D | Community browser (members, credences) | P1 | Admin component | Pending |
| 3.0.5-E | System statistics (counts, coherence, health) | P1 | Admin component | Pending |
| 3.0.5-F | Paper/source browser | P2 | Admin component | Pending |
| 3.0.5-G | Export audit trail | P2 | Admin component | Pending |

---

#### Implementation Order (Recommended)

```
Phase 1: Foundation (3.0.1-A, 3.0.1-B, 3.0.1-C)
         Core API with 7 endpoints, versioning, async
         ↓
Phase 2: Intelligence (3.0.2-A through 3.0.2-E)
         Query engine with LLM integration
         ↓
Phase 3: Interface (3.0.3-A through 3.0.3-E, 3.0.5-A through 3.0.5-E)
         Streamlit app + Admin dashboard + User types
         ↓
Phase 4: Delivery (3.0.4-A through 3.0.4-C)
         Core export capabilities
         ↓
Phase 5: Enhancement (remaining P2/P3 tasks)
         Extended API, advanced viz, reports
```

---

#### AI Integration Architecture

**Model Tiering** (per Amodei cost optimization):
- **Template match**: $0 (no LLM) — "What is the credence for X?"
- **Haiku**: $0.005 — Query parsing, intent classification
- **Sonnet**: $0.02 — Complex synthesis, comparisons
- **Opus**: $0.10 — Deep explanations, reports

**Target**: 80% of queries at $0-0.01, 15% at $0.02, 5% at $0.10

---

### Strategic TODOs (from STRATEGIC_TODOS_2026_01_20.md)

| TODO | Description | Blocked By |
|------|-------------|------------|
| 1 | Credibility Testing Method | Sprint 2.0 |
| 2 | Interpretive Intelligence Module | Sprint 2.5 |
| 3 | VOI-Driven Article Search | Sprint 2.0 |

---

## Files Reference

### Sprint 1.5 Files (in claude_epist_layer)

| File | Lines | Status |
|------|-------|--------|
| `epistemic_causal_integration.py` | ~800 | ✓ Complete |
| `epistemic_to_causal_bridges.py` | ~600 | ✓ Complete |
| `panel_concern_resolutions.py` | ~500 | ✓ Complete |
| `quinean_counterfactual_implementation.py` | ~500 | ✓ Complete |
| `van_fraassen_contrast_class.md` | ~700 | ✓ Complete |
| `expert_panel_quinean_vs_pearl.md` | ~800 | ✓ Complete |
| `expert_panel_epistemic_causal_integration.md` | ~600 | ✓ Complete |
| `expert_panel_synergies.md` | ~400 | ✓ Complete |
| `expert_panel_formal_foundations.md` | ~600 | ✓ Complete |

### Target Integration Points (Article Eater repo)

| File | Purpose | Sprint |
|------|---------|--------|
| `src/services/web_of_belief.py` | Main Quinean engine | 1.5 |
| `src/services/extraction_to_web.py` | Claim → belief mapper | 1.5, 1.6 |
| `src/services/web_persistence.py` | Quality weighting | P-QW decisions |
| `app/tasks/pipeline.py` | Extraction pipeline | 2.0 |

---

## Ruthless Review & Scheduled Testing

**Status**: COMPLETE (2026-02-08)

### Files Created

| File | Purpose |
|------|---------|
| `bin/ruthless_review.sh` | Bundle creator for external LLM review |
| `bin/scheduled_health_check.sh` | Automated test runner with regression detection |
| `docs/RUTHLESS_REVIEW_PROMPT_V5_2026_02_08.md` | 60+ expert panel critique prompt |
| `docs/HEALTH_CHECK_SETUP.md` | Cron/launchd setup instructions |

### Usage

```bash
# Create review bundle for ChatGPT/Gemini
./bin/ruthless_review.sh

# Run health check with notification
./bin/scheduled_health_check.sh --notify

# Full health check with bundle on failure
./bin/scheduled_health_check.sh --notify --bundle
```

### Cron Setup (Daily at 9am)

```bash
crontab -e
# Add: 0 9 * * * /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/bin/scheduled_health_check.sh --notify
```

---

## Session Log

| Date | Session Notes |
|------|---------------|
| 2026-02-10 | **Sprint ECB: Epistemic-Causal Bridge Repair PLANNED**. David raised system coherence concerns. Investigation revealed: (1) Two implementations exist (repo vs external research file), (2) Tests use wrong file, (3) Pipeline doesn't use bridge, (4) Duplicate class definitions, (5) No feedback loop. Convened Panel P-ECB-R (Haack, Pearl, van Fraassen, Simon, Cartwright, Parnas, Brooks). Created 5 docs: context, responses, plan review, implementation plan, archived features. Defined 3 sprints: ECB-1 (cleanup), ECB-2 (core integration), ECB-3 (van Fraassen + polish). Archived features documented for future reintegration: Individual Differences (IND-1 to IND-4), Cultural Meanings (CULT-1 to CULT-5), Argument Attack (ATK-1 to ATK-4). Target: ~500 lines (down from 2400). Version target: V23.1.0. |
| 2026-02-09 | **Entrenchment Tracker Updates**: Added entrenchment tracker schema + migrations, publication metadata capture, replay scaffold, BibTeX publication_date parsing + test, and pipeline metadata upsert. Added `publication_date` to AE paper schema + example. New tables in `web_persistence.py`, new `entrenchment_replay.py`, and `migrations/005_add_entrenchment_tracker.sql`. Version bumped to 23.0.5. Tests: `pytest tests/test_bibtex_utils.py`. |
| 2026-02-09 | **Sprint 3.0.3-A/B COMPLETE**: Streamlit Interface. (1) Created `streamlit_app/query_service.py` (~500 lines) - DirectQueryService for local query execution without API server. Uses query_parser.py for rule-based intent detection. Supports quick/standard/deep response modes. Scope-aware output. (2) Updated `streamlit_app/api_client.py` with direct mode fallback - automatically uses local services when API unavailable. Added `prefer_direct` option. (3) Verified existing `main.py` has user type selection (5 Cooper personas), existing `pages/1_query.py` has common questions interface. 35 tests passing (`tests/test_streamlit_query_service.py`). |
| 2026-02-09 | **Sprint 3.0.4-A/B/C COMPLETE**: (1) Evidence Summarizer: Created `src/services/evidence_summarizer.py` (~600 lines) - Cartwright-style scope metadata, transferability assessment, caveats, synthesis. 35 tests. (2) Export Formats: Created `src/services/export_formats.py` (~650 lines) - JSONL, CSV, TSV, JSON, Parquet (with pyarrow fallback), streaming exporter. 38 tests. (3) Verification Checklists: Created `src/services/export_checklists.py` (~650 lines) - Gawande-style checklists for evidence verification, extraction quality, methodology review, scope assessment, paper intake, pre-export. 37 tests. Total: 110 new tests. |
| 2026-02-09 | **3.0.3-E through 3.0.5-G + ENT-1 through ENT-5 COMPLETE**: (1) Network Visualization: Created `src/services/network_service.py` (~600 lines) - vis.js integration, force-directed layouts, clustering modes, graph metrics. 44 tests. (2) Report Generation: Created `src/services/report_generator.py` (~700 lines) - Markdown/HTML/PDF/JSON exports. 46 tests. (3) Export Audit: Created `src/services/export_audit.py` (~650 lines) - SQLite audit trail, content hashing, provenance tracking. 34 tests. (4) Entrenchment: Paper publication already in DB; Fixed `entrenchment_replay.py` (attribute naming); Added 5 entrenchment query methods to `web_persistence.py`; Created `frontend/entrenchment-monitor.html` + `app/routes/entrenchment.py` API; Health metrics (volatility, stagnation, divergence). 16 tests. |
| 2026-02-09 | **3.0.2-C + 3.0.2-F COMPLETE**: Scope-aware output + Bates patterns. (1) Created `src/services/scope_renderer.py` (~550 lines): ScopeRenderer with extract_scope_from_belief(), assess_transferability(), render_scoped_evidence(), render_scoped_response(). ScopeCondition, TransferabilityAssessment, ScopedEvidence, ScopedResponse dataclasses. Population conflict detection, lab→field warnings. 31 tests passing. (2) Enhanced `src/services/llm_query_bridge.py` with Bates berrypicking patterns: _retrieve_related() (serendipitous discovery via constraints/shared theories), _retrieve_trending() (recent papers/credence changes), _retrieve_canonical() (entrenched/foundational beliefs). Specialized synthesis methods: _synthesize_related(), _synthesize_trending(), _synthesize_canonical() with custom prompts. 48 tests passing (14 new Bates tests). |
| 2026-02-09 | **3.0.2-E COMPLETE**: LLM Integration with WebOfBelief. Enhanced `src/services/llm_query_bridge.py` (~850 lines total): (1) `retrieve_evidence()` — WebOfBelief integration with entity matching, scope filtering, credence sorting, entrenched belief boosting (~100 lines). (2) `GoogleProvider` — Gemini model support (~50 lines). (3) `_deep_synthesis()` — Full BEST tier model usage for complex reasoning with detailed JSON output structure (~100 lines). Created `tests/test_llm_query_bridge.py` (34 tests) covering: model configuration, providers, orchestration, intent detection, evidence retrieval with mock WebOfBelief, response synthesis, full pipeline, edge cases. All 34 tests passing. |
| 2026-02-09 | **ALL 16 EXTRACTION TEMPLATES COMPLETE**: Finished final 3 templates: (1) `EXTRACTION_TEMPLATE_NARRATIVE_REVIEW_2026_02_09.md` — interpretive/attributed/gap rules, argument_from_expert_opinion scheme, causal_level=association max (reviews don't generate evidence). (2) `EXTRACTION_TEMPLATE_THEORETICAL_2026_02_09.md` — theoretical/definitional/hypothesis/mechanism rules, deductive_argument scheme, causal_level=theoretical (proposed, not tested). (3) `EXTRACTION_TEMPLATE_THOUGHT_PIECE_2026_02_09.md` — opinion/recommendation/priority/asserted/framing rules, causal_level=null (opinions) or asserted (undemonstrated claims), lowest confidence range. **Extraction Table Status**: 16/16 COMPLETE. |
| 2026-02-09 | **ALL QUALITATIVE TEMPLATES COMPLETE**: Created 4 qualitative extraction templates with v2 panel additions: (1) `EXTRACTION_TEMPLATE_PHENOMENOLOGICAL_2026_02_09.md` — Husserl/Heidegger/IPA/embodied approaches, causal_level explicitly null (brackets causation), experiential rule type. (2) `EXTRACTION_TEMPLATE_ETHNOGRAPHIC_2026_02_09.md` — classical/focused/critical/autoethnographic types, cultural/norm/contextual rules, emic vs etic perspectives. (3) `EXTRACTION_TEMPLATE_GROUNDED_THEORY_2026_02_09.md` — Glaserian/Straussian/Constructivist traditions, theoretical/process/conditional rules, abductive_argument scheme. (4) `EXTRACTION_TEMPLATE_INTERVIEW_STUDY_2026_02_09.md` — descriptive/exploratory/explanatory types, perspective/reported_association/preference rules, self-report limitations documented. |
| 2026-02-09 | **EXTRACTION TEMPLATES COMPLETE**: Created 4 new extraction templates with v2 panel additions: (1) `EXTRACTION_TEMPLATE_OBSERVATIONAL_FIELD_2026_02_09.md` — naturalistic observation, association-only causal level, argument_from_sign scheme. (2) `EXTRACTION_TEMPLATE_CASE_STUDY_2026_02_09.md` — intrinsic/instrumental/critical/exemplary types, presumption rules, argument_from_example scheme. (3) `EXTRACTION_TEMPLATE_MIXED_METHODS_2026_02_09.md` — convergent/sequential designs, integration assessment, convergence-adjusted confidence. (4) Updated `EXTRACTION_TEMPLATE_SYSTEMATIC_REVIEW` to v1.1 with panel additions. Also fixed health check script integer comparison bug. |
| 2026-02-09 | **SCHEMA-1/2/3 COMPLETE**: (1) Schema extensions: Created `ae.rule.v2.schema.json` with new rule_types (rebuttal, presumption, association, contrast) and fields (causal_level, argument_scheme, critical_questions, contrast_class, difference_maker, enabling_conditions, bridge_type). Created `ae.claim.v2.schema.json` with causal_level, extraction_difficulty, source_zone. Created `contracts/vocab/argument_schemes.json` with 10 Walton schemes. (2) Panel additions doc: Created `EXTRACTION_TEMPLATE_PANEL_ADDITIONS_2026_02_09.md` specifying how to integrate Pearl causal levels, Walton argument schemes, Lipton contrast classes, Hearst/Teufel extraction metadata into existing templates. (3) Stimulus template: Created `STIMULUS_DOCUMENTATION_TEMPLATE_2026_02_09.md` with full CNfA domain features (ART, Prospect-Refuge, Biophilia, SRT markers) and ae.stimulus.v1 schema. |
| 2026-02-08 | **TBL-3 COMPLETE**: PDF Table Extraction. Created `src/services/table_extractor.py` (~750 lines). `AITableExtractor`: LLM-based extraction with structured prompts for STUDY_CHARACTERISTICS, RESULTS, QUALITY_ASSESSMENT, DEMOGRAPHICS table types. `PdfPlumberTableExtractor`: Geometric fallback. `HybridTableExtractor`: Combines both. Conversion functions to `ArticleMetadata` and `RCTStudyFact` types. 46 tests (`test_table_extractor.py`). Export engine already has table generators (ArticleMetadataTableGenerator, RCTTableGenerator) — now connected to extraction. |
| 2026-02-08 | **V23.0.0 BREAKING CHANGE: Emergent Entrenchment**: Removed `entrenchment` as settable field from `Belief` class. Added `WebOfBelief.get_entrenchment(belief_id)` method computing entrenchment via Thagard formula (40% connectivity + 30% level_weight + 30% coherence_contrib). Lazy caching with invalidation on constraint changes. Updated 8 files to use new method. Panel consultation: Quine, Haack, Thagard, Cartwright, Parnas, Simon. Philosophy clarified as foundherentism (Haack 1993), not pure Quinean coherentism. Fixed P1 bugs from ChatGPT ruthless review: constraint index purge, boundary status staleness, decision semantics (ACCEPT default). Created `tests/test_scalable_coherence_benchmark.py` (8 tests). Panel doc: `docs/PANEL_CONSULTATION_ENTRENCHMENT_2026-02-08.md`. |
| 2026-02-08 | **SPRINT 2.0.3 COMPLETE**: CLI flags for web outputs. Added `--web/--no-web`, `--web-equilibrium/--no-web-equilibrium`, `--web-max-iterations`, `--web-convergence-threshold` for Web of Belief control. Added `--export-manifest`, `--export-bn`, `--export-cluster-stats`, `--export-bn-edges` (all with `--no-*` variants) for export control. Updated pipeline functions to accept `web_options` and `export_options` dicts. 9 tests (`test_cli_web_flags.py`). |
| 2026-02-08 | **SPRINT 2.0.2 COMPLETE**: Output Serialization. Created `src/services/output_serializer.py` (~500 lines) with manifest generation, SHA256 checksums, TD module exports (theory inference audit, scope conditions, temporal expressions, cluster stats, BN edges with credible intervals). Schema versions for all outputs. Pipeline now generates `manifest.json`, `cluster_stats.json`, `bn_edges.json`. 20 tests (`test_output_serializer.py`). |
| 2026-02-08 | **SPRINT 2.0.1 COMPLETE**: Pipeline Integration wiring. Wired TD-C (Scalable Coherence) and TD-E (Incremental BN) into `app/tasks/pipeline.py`. Added CoherenceManager for O(n log n) coherence computation. Added IncrementalBNBuilder for Bayesian edge parameter updates. New output: `bn_incremental_state.json`. Enhanced `coherence_summary.json` with TD statistics (`scalable_coherence_used`, `incremental_bn_used`, `n_bn_updates`, `n_bn_edges`). Created `tests/test_pipeline_td_wiring.py` (13 tests). |
| 2026-02-08 | **SPRINT TD-D COMPLETE**: Temporal Parsing. Created `src/services/temporal_parser.py` (~900 lines) with Duration/Frequency/TemporalExpression dataclasses, pattern-based extraction for durations (simple, range, compound), frequencies (daily/weekly/etc), and temporal relations (before/after/during). Integrated with scope_extractor.py for enhanced duration extraction. ExposureType classification (acute/subacute/chronic/residential). 67 tests passing. **ALL TECHNICAL DEBT COMPLETE.** |
| 2026-02-08 | **RUTHLESS REVIEW INFRASTRUCTURE**: Created `bin/ruthless_review.sh` bundle creator, `bin/scheduled_health_check.sh` for cron/launchd scheduling, 60+ expert panel prompt (Torvalds, Carmack, Knuth, Pearl, Quine, Feynman, etc.). Health check tracks regression history in `logs/test_history.csv`. |
| 2026-02-08 | **SPRINT TD-C COMPLETE**: Scalable Coherence. Created `src/services/scalable_coherence.py` (~1000 lines) with ClusterManager (theory-based clustering), ConstraintNetwork (O(1) lookups), CoherenceCache (LRU with invalidation), CoherenceManager (hierarchical computation). Intra-cluster dense, inter-cluster sparse. Benchmark: 5000 beliefs, 25000 constraints in <500ms (target met). 64 tests passing. Drop-in replacement for O(n²) coherence computation. |
| 2026-02-08 | **SPRINT 2.6 COMPLETE**: Panel Decision Implementation. Track A (P-TC): Added `inference_basis`, `review_recommended`, `presumed_lab`, `effective_demand`, `mechanism_only` to MappingResult. New functions: `extract_task_context()`, `compute_effective_demand()`, `is_mechanism_only()`. Track B (P-QW): Updated QUALITY_WEIGHTS (Meth 0.28, Cite 0.18, Inst 0.12, etc.), added `citation_velocity()`, `quality_to_entrenchment()` piecewise mapping, `get_institution_tier()`. Created `contracts/vocab/institution_tiers.json`. 62 web_persistence tests passing. |
| 2026-02-08 | **SPRINT TD-E COMPLETE**: Incremental BN Learning. Created `src/services/incremental_bn.py` (~600 lines) with BetaBernoulliEdge (conjugate prior updates), IncrementalBNBuilder (streaming parameter updates), ActiveLearningScheduler (uncertainty × relevance prioritization). O(1) updates per observation via Beta-Bernoulli conjugacy. 95% credible intervals for edge strength. Connected to VOI search for gap identification. 41 tests passing. |
| 2026-02-08 | **SPRINT TD-B COMPLETE**: Scope Extraction enhancement. Created `src/services/scope_extractor.py` (~500 lines) with pattern-based extraction for population, setting, duration, nature type, methodology. Section-aware extraction, explicit/inferred tracking, generalization_risk calculation. Integrated with `extraction_to_web.py`. 51 tests passing. Falls back to pattern matching when spaCy unavailable. |
| 2026-02-08 | **SPRINT TD-A COMPLETE**: Theory Inference enhancement. Created `src/services/theory_matcher.py` (~400 lines) with EmbeddingTheoryMatcher, disambiguation rules for false positives (mechanical stress, attention to detail), and confidence scores. Integrated with `extraction_to_web.py`. 43 tests passing. Falls back to keyword matching when sentence-transformers unavailable. |
| 2026-02-08 | **P-TD PANEL CONSULTED**: Technical debt review complete. 9 experts consulted (Thagard, Simon, Cartwright, Mayo, Bates, Pustejovsky, Manning, Kleinberg, Hearst). Added incremental learning experts (Jordan, Gelman, Griffiths, Blei, Ghahramani). Defined 5 TD sprints: TD-A (theory inference), TD-B (scope), TD-C (scalability), TD-D (temporal), TD-E (incremental BN). See `docs/PANEL_P-TD_TECHNICAL_DEBT_REVIEW_2026_02_08.md`. |
| 2026-02-08 | **PARALLEL SESSION (Lane E) COMPLETE**: TODO 3 VOI-Driven Search enhanced. Created `cross_field_vocabulary.yaml` (~480 lines) with CNfA→psychology/neuroscience/architecture/medicine term mappings. Added `CrossFieldVocabulary` class to `voi_search.py`. Extended `QueryGenerator` with `generate_cross_field_queries()` and `expand_query_terms()`. Now 92 tests passing. |
| 2026-02-08 | **PARALLEL SESSION (Lane D) COMPLETE**: TODO 2 Interpretive Intelligence enhanced. Added MECHANISM and DISAGREEMENT patterns (expanded from 2 to 4 patterns). MechanismExplanationPattern (~150 lines), DisagreementSummaryPattern (~150 lines). Now 69 tests passing. Updated QuestionClassifier with new keywords. |
| 2026-02-08 | **PARALLEL SESSION (Lane A) COMPLETE**: Sprint 2.5 Schema Design done. Convened P-SE panel (Longino, Kitcher, Knorr Cetina, Collins, Kuhn). Resolved SE-1 through SE-5. Created `docs/SPRINT_2.5_DESIGN.md` (~600 lines) and `contracts/schemas/social_epistemology.v1.schema.json`. Lane B now unblocked for implementation. |
| 2026-02-08 | **PARALLEL SESSION (Lane C) COMPLETE**: TODO 1 Credibility Testing fully implemented. Created `credibility_feedback.py` (500 lines, 27 tests). Added Severity 3 checks (semantic coherence, stub detection) - now 68 tests. Enhanced pipeline with review queue and feedback tracking imports. Updated root `CLAUDE.md` with parallel work coordination. |
| 2026-02-08 | **PARALLEL SESSION (Lane F)**: Convened P-TC panel (7 decisions) and P-QW panel (6 decisions). Both panels complete with recommendations. See `docs/PANEL_P-TC_*.md` and `docs/PANEL_P-QW_*.md`. |
| 2026-02-08 | **Sprint 1.6 COMPLETE**: 68 tests passing. Added InferenceType, BeliefKind enums. Value computation (centrality, sensitivity). Tension-resolving experiments. P-EC-R9 enabling conditions check. |
| 2026-02-08 | **P-EC Panel APPROVED Sprint 1.5**. 17 recommendations generated. 4 high-priority for 1.6: enabling_conditions, CoherenceCache, query-local coherence, contrast warnings. |
| 2026-02-08 | **Sprint 1.5 COMPLETE**: All 3 remaining tasks done. 1.5.9: Integration tests (29→34). 1.5.10: Wire to web_of_belief.py. 1.5.11: CLAUDE.md updated. |
| 2026-02-08 | **Sprint 1.5.9 COMPLETE**: 29 integration tests passing. Fixed bridge to handle both `theory_id` (existing) and `theory_ids` (new). Key compatibility issue resolved. |
| 2026-02-08 | Integrated claude_epist_layer work; restructured panels as first-class; prioritized 1.5 → 1.6 → 2.5 |
| 2026-02-04 | Quality-Weighted Entrenchment spec drafted |
| 2026-02-03 | Task Context Integration panel convened |

---

*Tasks are project state, not ephemeral notes. Completed tasks document what we've done.*
