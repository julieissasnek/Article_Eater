# Implementation Plan: Addressing Expert Panel Validation Concerns

**Date**: Sunday, January 19, 2026
**Status**: Draft for Panel Review
**Sprints Covered**: 6-9 (proposed)

---

## Executive Summary

This plan addresses the expert panel's concerns from the Validation Challenge review. We organize work into four sprints, prioritizing foundational issues (causal structure, scope conditions) before validation infrastructure (Gold Standard Test Set).

---

## Sprint 6: Causal Structure & Scope Conditions

**Duration**: ~1 week
**Priority**: HIGH (Pearl, Cartwright concerns)

### 6.1 Add Causal Direction to Constraints

**Problem**: Constraints currently track correlation without causal direction.

**Implementation**:

```python
class CausalDirection(Enum):
    UNKNOWN = "unknown"           # Default - no causal claim
    FORWARD = "forward"           # source → target (causal)
    REVERSE = "reverse"           # target → source (causal)
    BIDIRECTIONAL = "bidirectional"  # mutual causation
    COMMON_CAUSE = "common_cause"    # shared cause, no direct link
    CORRELATIONAL = "correlational"  # explicitly non-causal

@dataclass
class Constraint:
    # ... existing fields ...
    causal_direction: CausalDirection = CausalDirection.UNKNOWN
    causal_evidence: Optional[str] = None  # "experimental", "longitudinal", "theoretical", "none"
```

**Extraction Changes**:
- Parse for causal language ("causes", "leads to", "results in", "produces")
- Parse for correlational hedging ("associated with", "related to", "correlated")
- Mark experimental studies as eligible for `FORWARD` causal claims
- Mark observational studies as `CORRELATIONAL` by default

**Test Cases**:
- Ulrich (1984): observational → constraints should be `CORRELATIONAL`
- Berman et al. (2008): experimental → constraints can be `FORWARD`

### 6.2 Explicit Scope Conditions

**Problem**: Conflicts often reflect scope boundaries, not genuine contradictions.

**Implementation**:

```python
@dataclass
class ScopeConditions:
    population: Optional[str] = None      # "adults", "children", "clinical", "healthy"
    setting: Optional[str] = None         # "lab", "field", "simulated"
    duration: Optional[str] = None        # "acute", "chronic", "single_exposure"
    measurement: Optional[str] = None     # "self_report", "physiological", "behavioral"
    geography: Optional[str] = None       # "urban", "rural", "Western", "global"
    moderators: List[str] = field(default_factory=list)

@dataclass
class Belief:
    # ... existing fields ...
    scope: ScopeConditions = field(default_factory=ScopeConditions)
```

**Conflict Detection Update**:
```python
def _detect_conflict_type(self, b1: Belief, b2: Belief) -> ConflictType:
    # Check scope overlap BEFORE declaring genuine contradiction
    if not self._scopes_overlap(b1.scope, b2.scope):
        return ConflictType.SCOPE_BOUNDARY
    # ... existing logic ...
```

### 6.3 Measurement Method Tracking

**Problem**: "Stress" measured by cortisol ≠ "stress" measured by self-report.

**Implementation**:
- Extend `MeasurementMethod` enum (already exists in Sprint 4)
- Add `measurement_method` to Belief extraction
- Treat same-construct, different-method findings as **complementary**, not **identical**

**Decision Rule**:
| Same Construct | Same Method | Action |
|---------------|-------------|--------|
| Yes | Yes | Merge beliefs |
| Yes | No | Create `methodological_complement` constraint |
| No | - | Keep separate |

---

## Sprint 7: Environment Ontology & Construct Identity

**Duration**: ~1 week
**Priority**: HIGH (Bates concern)

### 7.1 Environment Feature Ontology

**Problem**: No canonical mapping for architectural features (parallel to outcome_taxonomy.py).

**Implementation**: Create `src/services/environment_taxonomy.py`

```python
ENVIRONMENT_DOMAINS = {
    "spatial": {
        "spatial.volume": ["ceiling height", "room volume", "volumetric"],
        "spatial.openness": ["open plan", "visual openness", "spaciousness"],
        "spatial.enclosure": ["enclosure", "boundaries", "containment"],
        "spatial.prospect": ["view distance", "prospect", "overlook"],
        "spatial.refuge": ["refuge", "shelter", "protected space"],
    },
    "natural": {
        "natural.vegetation": ["plants", "greenery", "biophilic", "vegetation"],
        "natural.water": ["water features", "fountains", "aquatic"],
        "natural.daylight": ["natural light", "daylight", "sunlight"],
        "natural.views": ["nature views", "window views", "green views"],
    },
    "sensory": {
        "sensory.lighting": ["artificial lighting", "illumination", "light levels"],
        "sensory.acoustics": ["noise", "sound", "acoustics", "quiet"],
        "sensory.thermal": ["temperature", "thermal comfort", "HVAC"],
        "sensory.air": ["air quality", "ventilation", "IAQ"],
    },
    "configurational": {
        "config.wayfinding": ["navigation", "wayfinding", "legibility"],
        "config.complexity": ["visual complexity", "spatial complexity"],
        "config.connectivity": ["connectivity", "integration", "accessibility"],
        "config.density": ["density", "crowding", "occupancy"],
    },
    "aesthetic": {
        "aesthetic.color": ["color", "hue", "chromatic"],
        "aesthetic.materials": ["materials", "texture", "surface"],
        "aesthetic.order": ["order", "symmetry", "pattern"],
        "aesthetic.style": ["architectural style", "design style"],
    }
}
```

**Belief Enhancement**:
```python
@dataclass
class Belief:
    # ... existing fields ...
    environment_id: Optional[str] = None  # e.g., "spatial.openness"
    outcome_id: Optional[str] = None      # e.g., "psych.stress"
```

### 7.2 Semantic Construct Matching

**Problem**: String similarity conflates different constructs with same words.

**Implementation**: Two-stage identity check (enhanced)

```python
def _beliefs_same_construct(self, b1: Belief, b2: Belief) -> bool:
    # Stage 1: Canonical ID match (definitive)
    if b1.environment_id and b2.environment_id:
        if b1.environment_id != b2.environment_id:
            return False  # Different architectural features

    if b1.outcome_id and b2.outcome_id:
        if b1.outcome_id != b2.outcome_id:
            return False  # Different outcomes

    # Stage 2: If IDs match (or missing), check content similarity
    return self._content_similar(b1.content, b2.content)
```

### 7.3 Terminological Variation Tests

**Test Cases**:
- "nature exposure" / "green space" / "biophilic elements" → should map to same `natural.*` domain
- "complexity" (visual) vs. "complexity" (navigational) → should map to different IDs

---

## Sprint 8: Coherence Dashboard Enhancement & Validation Infrastructure

**Duration**: ~1 week
**Priority**: MEDIUM (Simon, Bates concerns)

### 8.1 Diversity Index

**Problem**: Coherence alone doesn't distinguish noise from genuine fragmentation.

**Implementation**:
```python
@dataclass
class CoherenceDashboard:
    # ... existing fields ...
    diversity_index: float          # Shannon entropy over domains
    domain_coverage: Dict[str, int] # beliefs per domain
    theory_coverage: Dict[str, int] # beliefs per theory

    def compute_diversity(self, beliefs: List[Belief]) -> float:
        """Shannon entropy over environment + outcome domains."""
        domain_counts = Counter(b.environment_id for b in beliefs if b.environment_id)
        domain_counts.update(b.outcome_id for b in beliefs if b.outcome_id)

        total = sum(domain_counts.values())
        if total == 0:
            return 0.0

        entropy = -sum(
            (c/total) * log(c/total)
            for c in domain_counts.values() if c > 0
        )
        return entropy
```

**Interpretation Matrix**:
| Coherence | Diversity | Interpretation |
|-----------|-----------|----------------|
| Low | Low | Noise or narrow extraction |
| Low | High | Genuinely fragmented field |
| High | Low | Narrow consensus |
| High | High | **Integrated structure (goal)** |

### 8.2 Leave-One-Out Validation

**Problem**: Need to test if structure is generalizable, not memorized.

**Implementation**:
```python
class LeaveOneOutValidator:
    def validate(self, service: WebPersistenceService, paper_ids: List[str]) -> LOOReport:
        results = []

        for held_out in paper_ids:
            # Build web without held_out paper
            partial_web = self._build_web_excluding(service, held_out)

            # Get beliefs from held_out paper
            held_out_beliefs = self._get_paper_beliefs(service, held_out)

            # Can we "predict" held_out findings from partial web?
            for belief in held_out_beliefs:
                prediction = self._predict_belief(partial_web, belief)
                results.append(LOOResult(
                    paper_id=held_out,
                    belief_id=belief.belief_id,
                    actual_credence=belief.credence.value,
                    predicted_credence=prediction.credence,
                    prediction_confidence=prediction.confidence
                ))

        return LOOReport(results)
```

### 8.3 Lab vs. Field Marker

**Problem**: Lab findings about photos don't generalize to real environments.

**Implementation**:
```python
class EcologicalValidity(Enum):
    FIELD_REAL = "field_real"           # Real environment, real behavior
    FIELD_SIMULATED = "field_simulated" # Real environment, simulated task
    LAB_IMMERSIVE = "lab_immersive"     # VR or high-fidelity simulation
    LAB_PHOTOS = "lab_photos"           # Photo viewing studies
    LAB_ABSTRACT = "lab_abstract"       # Geometric shapes, no environment

@dataclass
class Belief:
    # ... existing fields ...
    ecological_validity: EcologicalValidity = EcologicalValidity.LAB_PHOTOS
```

**Credence Adjustment**:
- Field studies: no adjustment
- Lab immersive: -10% credence for generalization claims
- Lab photos: -20% credence for generalization claims
- Lab abstract: flag as `limited_ecological_validity`

---

## Sprint 9: Gold Standard Test Set & Calibration

**Duration**: ~1-2 weeks
**Priority**: HIGH (All panelists)

### 9.1 Test Corpus Assembly

**Papers to include** (per panel recommendations):

| # | Paper | Focus | Expected Output |
|---|-------|-------|-----------------|
| 1 | Kaplan & Kaplan (1989) | Theory extraction | ART framework, moderate empirical |
| 2 | Ulrich (1984) | Causal restraint | Empirical, correlational only |
| 3 | Berman et al. (2008) | Cross-paper links | Supports Kaplan, causal OK |
| 4 | Appleton (1975) | Theory vs. evidence | Theoretical, low empirical |
| 5 | Kellert & Wilson (1993) | Epistemic level | Hypothesis, not finding |
| 6 | [Null result - TBD] | Null handling | Null extracted correctly |
| 7 | [Weak methods - TBD] | Quality detection | High uncertainty |
| 8 | [Conflict pair A] | Conflict detection | Genuine contradiction |
| 9 | [Conflict pair B] | Scope detection | Scope boundary |
| 10 | [Terminology set] | Semantic identity | Same construct recognized |

### 9.2 Annotation Schema

```yaml
# gold_standard/kaplan_1989.yaml
paper_id: "kaplan_1989"
citation: "Kaplan, R., & Kaplan, S. (1989). The experience of nature."
domain: "ART"

expected_beliefs:
  - id: "art_directed_attention_fatigue"
    content: "Directed attention is a limited resource that becomes fatigued"
    expected_credence: [0.6, 0.8]
    epistemic_level: "theoretical"
    theory: "ART"

  - id: "art_nature_restoration"
    content: "Natural environments facilitate recovery from directed attention fatigue"
    expected_credence: [0.5, 0.7]
    epistemic_level: "intermediate"
    theory: "ART"
    scope:
      setting: "natural_environments"
      population: "general"

expected_constraints:
  - source: "art_directed_attention_fatigue"
    target: "art_nature_restoration"
    type: "supports"
    causal_direction: "forward"
    expected_strength: [0.6, 0.8]

should_NOT_extract:
  - "ART is proven"
  - "Nature always restores attention"
  - Any claim with credence > 0.85

quality_expectations:
  methodology_score: [0.5, 0.7]  # Theory book, not empirical study
  ecological_validity: "field_real"
```

### 9.3 Validation Metrics

```python
@dataclass
class ValidationReport:
    # Belief extraction
    belief_recall: float      # % expected beliefs found
    belief_precision: float   # % extracted beliefs that were expected
    belief_f1: float

    # Credence calibration
    credence_mae: float       # Mean absolute error vs. expected range
    credence_in_range: float  # % credences within expected range

    # Constraint extraction
    constraint_recall: float
    constraint_precision: float

    # Epistemic level accuracy
    level_accuracy: float     # % correct epistemic levels

    # Negative tests
    false_extractions: List[str]  # Things extracted that shouldn't be
    missed_scope_conditions: int

    # Overall
    pass_threshold: float = 0.7

    def passed(self) -> bool:
        return (
            self.belief_f1 >= self.pass_threshold and
            self.credence_in_range >= self.pass_threshold and
            self.level_accuracy >= 0.6
        )
```

### 9.4 Calibration Testing

**Protocol**:
1. Extract beliefs from Gold Standard papers
2. Compare to expert annotations
3. Compute ValidationReport
4. If failed:
   - Analyze failure modes
   - Adjust extraction prompts or thresholds
   - Re-run
5. If passed:
   - Document baseline performance
   - Monitor for regression on new papers

---

## Risk Mitigation (Panel Concerns)

### "Coherent Nonsense" Risk (Pearl)

**Mitigation**:
- All outputs include disclaimer: "Represents literature claims, not verified truth"
- Coherence dashboard shows diversity (low diversity + high coherence = suspicious)
- Causal direction explicitly marked (prevents causal overclaiming)

### "Scope Collapse" Risk (Cartwright)

**Mitigation**:
- Scope conditions extracted for every belief
- Conflicts only flagged as `GENUINE_CONTRADICTION` if scopes overlap
- Scope boundary conflicts tracked separately (not errors, information)

### "Construct Conflation" Risk (Bates)

**Mitigation**:
- Environment ontology provides canonical IDs
- Same-word, different-construct cases explicitly tested
- Merge requires ID match, not just string similarity

### "Publication Bias Inheritance" Risk (All)

**Mitigation**:
- Cannot fix, but explicitly acknowledge
- Add `publication_bias_note` to all summary outputs
- Weight replications higher (already implemented in Sprint 5)

---

## Implementation Order

```
Sprint 6 (Week 1): Causal Structure & Scope
├── 6.1 CausalDirection enum + constraint field
├── 6.2 ScopeConditions dataclass + overlap detection
├── 6.3 Measurement method in belief identity
└── Tests: causal extraction, scope boundary detection

Sprint 7 (Week 2): Environment Ontology
├── 7.1 environment_taxonomy.py (parallel to outcome_taxonomy.py)
├── 7.2 Semantic construct matching (two-stage)
├── 7.3 Terminological variation tests
└── Tests: cross-terminology recognition

Sprint 8 (Week 3): Dashboard & Validation Infra
├── 8.1 Diversity index in CoherenceDashboard
├── 8.2 LeaveOneOutValidator
├── 8.3 EcologicalValidity marker
└── Tests: diversity calculation, LOO protocol

Sprint 9 (Week 4-5): Gold Standard & Calibration
├── 9.1 Assemble 10 test papers
├── 9.2 Create annotation YAML for each
├── 9.3 ValidationReport implementation
├── 9.4 Run calibration, iterate until pass
└── Deliverable: Baseline validation report
```

---

## Success Criteria

**Sprint 6-8 Success**:
- All new fields populated for test extractions
- No regression on existing 57 tests
- New tests for causal direction, scope conditions, diversity

**Sprint 9 Success**:
- Gold Standard Test Set: 10 papers annotated
- Validation F1 ≥ 0.7 on belief extraction
- Credence calibration: ≥ 70% within expected ranges
- Zero "should_NOT_extract" items appearing in output

**Overall Success**:
- Panel re-review approves approach
- System outputs can be framed as "auditable literature summary"
- Clear documentation of limitations and caveats

---

## Questions for Panel Review

1. **Causal direction defaults**: Should `UNKNOWN` be the default, or `CORRELATIONAL`?
2. **Scope overlap threshold**: How much overlap required before declaring genuine conflict?
3. **Diversity index weighting**: Equal weight for environment and outcome domains?
4. **Gold Standard papers**: Are the 10 nominated papers appropriate? Substitutions?
5. **Pass threshold**: Is 0.7 F1 appropriate, or should we be stricter/looser?

---

*Plan submitted for Expert Panel review.*
