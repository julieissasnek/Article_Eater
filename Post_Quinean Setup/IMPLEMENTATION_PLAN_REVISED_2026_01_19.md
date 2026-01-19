# Revised Implementation Plan: Addressing Expert Panel Validation Concerns

**Date**: Sunday, January 19, 2026
**Status**: FINAL (Panel Approved with Modifications Incorporated)
**Sprints Covered**: 6-9
**Panel Documents Incorporated**:
- `EXPERT_PANEL_VALIDATION_RESPONSES_2026_01_19.md`
- `EXPERT_PANEL_PLAN_REVIEW_2026_01_19.md`
- `EXPERT_PANEL_FOLLOWUP_QA_2026_01_19.md`

---

## Executive Summary

This revised plan addresses all expert panel concerns and incorporates their answers to the three follow-up questions. Key additions:
- Multi-theory paper handling with evidence clustering
- Phased validation with connectivity gates
- Strict corpus versioning with provenance tracking

---

## Sprint 6: Causal Structure & Scope Conditions

**Duration**: ~1 week
**Priority**: HIGH

### 6.1 Causal Direction (Enhanced per Pearl)

```python
class CausalDirection(Enum):
    UNKNOWN = "unknown"              # Default for theoretical claims
    CORRELATIONAL = "correlational"  # Default for empirical findings
    FORWARD = "forward"              # source → target (experimental evidence)
    REVERSE = "reverse"              # target → source
    BIDIRECTIONAL = "bidirectional"  # mutual causation
    COMMON_CAUSE = "common_cause"    # C → A, C → B
    MEDIATED = "mediated"            # A → M → B (NEW per Pearl)

@dataclass
class Constraint:
    constraint_id: str
    source_id: str
    target_id: str
    constraint_type: ConstraintType
    strength: float = 0.5
    causal_direction: CausalDirection = CausalDirection.UNKNOWN
    causal_evidence: Optional[str] = None  # "experimental", "longitudinal", "cross_sectional", "theoretical"
    mediator: Optional[str] = None  # For MEDIATED: what's the M?
```

**Default Assignment Rules**:
| Paper Type | Default Causal Direction |
|------------|-------------------------|
| Experimental | `FORWARD` eligible |
| Longitudinal observational | `FORWARD` with elevated uncertainty |
| Cross-sectional observational | `CORRELATIONAL` |
| Theoretical/review | `UNKNOWN` |

### 6.2 Scope Conditions (Enhanced per Cartwright)

```python
@dataclass
class ScopeConditions:
    population: Optional[str] = None      # "adults", "children", "clinical", "healthy"
    setting: Optional[str] = None         # "lab", "field", "simulated"
    duration: Optional[str] = None        # "acute", "chronic", "single_exposure"
    measurement: Optional[str] = None     # "self_report", "physiological", "behavioral"
    geography: Optional[str] = None       # "urban", "rural", "Western", "global"
    moderators: List[str] = field(default_factory=list)

def _scopes_overlap(self, s1: ScopeConditions, s2: ScopeConditions) -> bool:
    """
    Scopes overlap if compatible in ALL specified dimensions.
    Any dimension mismatch → no overlap (per Cartwright).
    """
    for field in ['population', 'setting', 'duration', 'measurement', 'geography']:
        v1 = getattr(s1, field)
        v2 = getattr(s2, field)
        if v1 and v2 and not self._values_compatible(v1, v2):
            return False
    return True
```

### 6.3 Conflict Types (Enhanced per Cartwright)

```python
class ConflictType(Enum):
    GENUINE_CONTRADICTION = "genuine_contradiction"
    SCOPE_BOUNDARY = "scope_boundary"
    METHODOLOGICAL_DIVERGENCE = "methodological_divergence"
    PRECISION_BOUNDARY = "precision_boundary"  # NEW: same direction, different magnitude
    UNKNOWN = "unknown"
```

**Precision Boundary Detection**:
```python
def _is_precision_boundary(self, b1: Belief, b2: Belief) -> bool:
    """Same direction effect, different magnitude → not a conflict."""
    # Check if both positive or both negative direction
    # Check if credences differ by < 0.3
    # If so, it's precision difference, not contradiction
    same_direction = self._same_effect_direction(b1.content, b2.content)
    magnitude_similar = abs(b1.credence.value - b2.credence.value) < 0.3
    return same_direction and not magnitude_similar
```

### 6.4 Tests for Sprint 6

- [ ] Causal direction extraction from experimental vs. observational papers
- [ ] Scope overlap detection with partial matches
- [ ] Precision boundary vs. genuine contradiction classification
- [ ] Mediated causation detection

---

## Sprint 7: Environment Ontology & Construct Identity

**Duration**: ~1 week
**Priority**: HIGH

### 7.1 Environment Taxonomy (Enhanced per Bates)

Create `src/services/environment_taxonomy.py`:

```python
ENVIRONMENT_HIERARCHY = {
    "spatial": {
        "_description": "Volumetric and geometric properties",
        "spatial.volume": {
            "_synonyms": ["ceiling height", "room volume", "volumetric capacity"],
            "_related": ["spatial.openness"],
            "_measurement_units": ["meters", "cubic_meters", "feet"]
        },
        "spatial.openness": {
            "_synonyms": ["open plan", "visual openness", "spaciousness", "expansiveness"],
            "_related": ["spatial.volume", "spatial.prospect"],
            "_antonym": "spatial.enclosure"  # NEW per Bates
        },
        "spatial.enclosure": {
            "_synonyms": ["enclosed", "contained", "bounded"],
            "_antonym": "spatial.openness"
        },
        "spatial.prospect": {
            "_synonyms": ["view distance", "overlook", "vantage"],
            "_related": ["spatial.openness"],
            "_theory_link": "prospect_refuge"
        },
        "spatial.refuge": {
            "_synonyms": ["shelter", "protected space", "nook"],
            "_antonym": "spatial.prospect",
            "_theory_link": "prospect_refuge"
        }
    },
    "natural": {
        "_description": "Biophilic and natural elements",
        "natural.vegetation": {
            "_synonyms": ["plants", "greenery", "biophilic", "flora"],
            "_related": ["natural.views"]
        },
        "natural.water": {
            "_synonyms": ["water features", "fountains", "aquatic", "blue space"]
        },
        "natural.daylight": {
            "_synonyms": ["natural light", "sunlight", "daylighting"],
            "_related": ["sensory.lighting"]
        },
        "natural.views": {
            "_synonyms": ["nature views", "window views", "green views", "prospect"],
            "_ecological_validity_note": "photos vs. real differ"
        }
    },
    "sensory": {
        "_description": "Non-visual environmental qualities",
        "sensory.lighting": {
            "_synonyms": ["artificial lighting", "illumination", "light levels", "lux"]
        },
        "sensory.acoustics": {
            "_synonyms": ["noise", "sound", "acoustic quality", "sound masking"]
        },
        "sensory.thermal": {
            "_synonyms": ["temperature", "thermal comfort", "HVAC"]
        },
        "sensory.air": {
            "_synonyms": ["air quality", "ventilation", "IAQ", "CO2"]
        }
    },
    "configurational": {
        "_description": "Layout and spatial organization",
        "config.wayfinding": {
            "_synonyms": ["navigation", "legibility", "orientation"]
        },
        "config.complexity": {
            "_synonyms": ["spatial complexity", "layout complexity"],
            "_note": "DISTINCT from aesthetic.complexity"
        },
        "config.connectivity": {
            "_synonyms": ["integration", "accessibility", "permeability"]
        },
        "config.density": {
            "_synonyms": ["occupant density", "crowding"],
            "_note": "DISTINCT from building density"
        }
    },
    "aesthetic": {
        "_description": "Visual and stylistic properties",
        "aesthetic.complexity": {
            "_synonyms": ["visual complexity", "ornamentation", "detail"],
            "_note": "DISTINCT from config.complexity"
        },
        "aesthetic.color": {
            "_synonyms": ["hue", "chromatic", "color temperature"]
        },
        "aesthetic.materials": {
            "_synonyms": ["texture", "surface", "materiality"]
        },
        "aesthetic.order": {
            "_synonyms": ["symmetry", "pattern", "regularity"],
            "_antonym": "aesthetic.complexity"
        }
    }
}
```

### 7.2 Antonym-Aware Conflict Detection (per Bates)

```python
def _check_antonym_equivalence(self, b1: Belief, b2: Belief) -> bool:
    """
    If environments are antonyms and effects are opposite,
    this is the SAME finding expressed differently, not a conflict.

    "Openness increases wellbeing" ≡ "Enclosure decreases wellbeing"
    """
    env1 = self._get_environment_id(b1)
    env2 = self._get_environment_id(b2)

    if not (env1 and env2):
        return False

    # Check if antonyms
    if not self._are_antonyms(env1, env2):
        return False

    # Check if opposite effect directions
    dir1 = self._get_effect_direction(b1.content)  # "increases", "decreases"
    dir2 = self._get_effect_direction(b2.content)

    return dir1 != dir2  # Opposite directions = same finding
```

### 7.3 Diversity Index (per Bates)

```python
def compute_diversity_index(self, beliefs: List[Belief]) -> float:
    """
    Shannon entropy over domains.
    Weight: 0.6 environment, 0.4 outcome (per Bates).
    """
    env_counts = Counter(b.environment_id for b in beliefs if b.environment_id)
    out_counts = Counter(b.outcome_id for b in beliefs if b.outcome_id)

    env_entropy = self._shannon_entropy(env_counts)
    out_entropy = self._shannon_entropy(out_counts)

    return 0.6 * env_entropy + 0.4 * out_entropy
```

### 7.4 Tests for Sprint 7

- [ ] Synonym resolution across terminology variations
- [ ] Antonym equivalence detection
- [ ] Same-word, different-construct separation (complexity test)
- [ ] Diversity index calculation

---

## Sprint 8: Multi-Theory Handling & Validation Infrastructure

**Duration**: ~1 week
**Priority**: HIGH

### 8.1 Multi-Theory Paper Handling (per Panel Consensus)

```python
@dataclass
class Belief:
    # ... existing fields ...
    evidence_cluster_id: Optional[str] = None  # Groups beliefs from same study

class ConstraintType(Enum):
    # ... existing ...
    SHARED_EVIDENCE = "shared_evidence"  # Same study supports both (NEW)

class BridgeType(Enum):
    # ... existing ...
    EMPIRICAL_COVARIANCE = "empirical_covariance"  # Co-tested in same study (NEW)
```

**Extraction Logic for Multi-Theory Papers**:
```python
def extract_multi_theory_paper(self, paper: Paper) -> ExtractionResult:
    """
    When paper tests multiple theories:
    1. Extract separate beliefs for each theory
    2. Assign same evidence_cluster_id
    3. Create SHARED_EVIDENCE constraints (no credence boost)
    4. Generate EMPIRICAL_COVARIANCE bridges
    """
    theories_found = self._detect_theories(paper)
    evidence_cluster = f"cluster:{paper.id}"

    beliefs = []
    for theory in theories_found:
        theory_beliefs = self._extract_for_theory(paper, theory)
        for b in theory_beliefs:
            b.evidence_cluster_id = evidence_cluster
        beliefs.extend(theory_beliefs)

    # Create bridges between theories
    bridges = []
    for t1, t2 in combinations(theories_found, 2):
        bridges.append(BridgeCandidate(
            source_theory=t1,
            target_theory=t2,
            bridge_type=BridgeType.EMPIRICAL_COVARIANCE,
            confidence=0.6,  # Higher than analogical
            evidence=[paper.id]
        ))

    return ExtractionResult(beliefs=beliefs, bridges=bridges)
```

**Credence Merge with Cluster Awareness**:
```python
def _merge_credences(self, c1: Credence, c2: Credence) -> Credence:
    # Check evidence clusters
    if (c1.evidence_cluster_id and c2.evidence_cluster_id and
        c1.evidence_cluster_id == c2.evidence_cluster_id):
        # Same study - don't boost credence (would be double-counting)
        # Return more recent or average without uncertainty reduction
        return Credence(
            value=(c1.value + c2.value) / 2,
            uncertainty=max(c1.uncertainty, c2.uncertainty),  # No reduction
            n_observations=c1.n_observations  # Don't sum
        )

    # Different studies - normal inverse-variance merge
    return self._inverse_variance_merge(c1, c2)
```

### 8.2 Phased Validation Protocol (per Panel Consensus)

```python
class ValidationPhase(Enum):
    PHASE_1_ANNOTATION = "annotation"      # N≥10: Gold Standard comparison
    PHASE_2_CALIBRATION = "calibration"    # N≥20: Credence calibration
    PHASE_3_LOO = "loo"                    # N≥30: Leave-one-out prediction
    PHASE_4_BRIDGES = "bridges"            # N≥50: Bridge validation

@dataclass
class ValidationGate:
    phase: ValidationPhase
    min_papers: int
    min_connectivity: float  # Mean constraint degree
    min_lcc: float  # Largest connected component fraction

VALIDATION_GATES = {
    ValidationPhase.PHASE_1_ANNOTATION: ValidationGate(
        phase=ValidationPhase.PHASE_1_ANNOTATION,
        min_papers=10, min_connectivity=0, min_lcc=0
    ),
    ValidationPhase.PHASE_2_CALIBRATION: ValidationGate(
        phase=ValidationPhase.PHASE_2_CALIBRATION,
        min_papers=20, min_connectivity=1.5, min_lcc=0.5
    ),
    ValidationPhase.PHASE_3_LOO: ValidationGate(
        phase=ValidationPhase.PHASE_3_LOO,
        min_papers=30, min_connectivity=2.0, min_lcc=0.7
    ),
    ValidationPhase.PHASE_4_BRIDGES: ValidationGate(
        phase=ValidationPhase.PHASE_4_BRIDGES,
        min_papers=50, min_connectivity=2.5, min_lcc=0.8
    ),
}

def check_validation_eligibility(web: WebOfBelief, papers: List[Paper]) -> List[ValidationPhase]:
    """Return which validation phases the corpus is eligible for."""
    eligible = []
    n_papers = len(papers)
    connectivity = compute_mean_degree(web)
    lcc = compute_lcc_fraction(web)

    for phase, gate in VALIDATION_GATES.items():
        if (n_papers >= gate.min_papers and
            connectivity >= gate.min_connectivity and
            lcc >= gate.min_lcc):
            eligible.append(phase)

    return eligible
```

### 8.3 Leave-One-Out with Stratification (per Simon)

```python
@dataclass
class StratifiedLOOReport:
    overall: LOOMetrics
    by_theory: Dict[str, LOOMetrics]
    single_theory_papers: LOOMetrics
    multi_theory_papers: LOOMetrics
    prediction_mode_distribution: Dict[str, int]  # DIRECT, CONSTRAINED, NOVEL

def run_stratified_loo(
    service: WebPersistenceService,
    papers: List[Paper]
) -> StratifiedLOOReport:
    """
    Run LOO with stratification by theory and paper type.
    """
    single_theory = [p for p in papers if len(p.theories) == 1]
    multi_theory = [p for p in papers if len(p.theories) > 1]

    # Overall LOO
    overall = run_loo(service, papers)

    # By theory (only if ≥5 papers per theory)
    by_theory = {}
    for theory in get_all_theories(papers):
        theory_papers = [p for p in papers if theory in p.theories]
        if len(theory_papers) >= 5:
            by_theory[theory] = run_loo(service, theory_papers)

    return StratifiedLOOReport(
        overall=overall,
        by_theory=by_theory,
        single_theory_papers=run_loo(service, single_theory) if len(single_theory) >= 10 else None,
        multi_theory_papers=run_loo(service, multi_theory) if len(multi_theory) >= 5 else None,
        prediction_mode_distribution=overall.mode_counts
    )
```

### 8.4 Ecological Validity (Enhanced per Kaplan)

```python
class EcologicalValidity(Enum):
    FIELD_NATURAL = "field_natural"       # Real environment, natural behavior
    FIELD_STRUCTURED = "field_structured" # Real environment, structured task
    LAB_VR = "lab_vr"                     # VR immersion (NEW distinction)
    LAB_VIDEO = "lab_video"               # Video walkthrough (NEW distinction)
    LAB_PHOTOS = "lab_photos"             # Static images
    LAB_ABSTRACT = "lab_abstract"         # No environment reference

ECOLOGICAL_VALIDITY_WEIGHTS = {
    EcologicalValidity.FIELD_NATURAL: 1.0,
    EcologicalValidity.FIELD_STRUCTURED: 0.95,
    EcologicalValidity.LAB_VR: 0.85,
    EcologicalValidity.LAB_VIDEO: 0.75,
    EcologicalValidity.LAB_PHOTOS: 0.65,
    EcologicalValidity.LAB_ABSTRACT: 0.50,
}
```

### 8.5 Tests for Sprint 8

- [ ] Multi-theory paper extraction creates evidence clusters
- [ ] Credence merge doesn't double-count same-study evidence
- [ ] EMPIRICAL_COVARIANCE bridges generated correctly
- [ ] Validation gates enforce minimums
- [ ] Stratified LOO produces separate metrics

---

## Sprint 9: Gold Standard Corpus & Calibration

**Duration**: ~2 weeks
**Priority**: HIGH

### 9.1 Corpus Assembly (Revised per Kaplan)

**Final Test Corpus (12 papers)**:

| # | Paper | Domain | Type | Why Included |
|---|-------|--------|------|--------------|
| 1 | Kaplan & Kaplan (1989) | ART | Theory | Foundational theory |
| 2 | Ulrich (1984) | SRT | Empirical | Classic observational |
| 3 | Berman et al. (2008) | ART | Experimental | Experimental test of ART |
| 4 | Appleton (1975) | Prospect-Refuge | Theory | Alternative theory |
| 5 | Kellert & Wilson (1993) | Biophilia | Hypothesis | Hypothesis framing |
| 6 | Evans & McCoy (1998) | Built Env | Review | Non-nature focus |
| 7 | Stamps (2000) | Preference | Quantitative | Modeling approach |
| 8 | Hartig et al. (2003) | ART+SRT | Multi-theory | Tests multiple theories |
| 9 | Berto (2005) | ART+Preference | Multi-theory | Distinguishes constructs |
| 10 | [Lighting paper TBD] | Sensory | Empirical | Expand beyond nature |
| 11 | [Wayfinding paper TBD] | Config | Empirical | Expand beyond nature |
| 12 | [Null result TBD] | Various | Null | Null handling test |

**Stratification Check**:
- ART: Papers 1, 3, 8, 9 (4 papers ✓)
- SRT: Papers 2, 8 (2 papers - need 1 more)
- Prospect-Refuge: Paper 4 (need more)
- Non-nature: Papers 6, 7, 10, 11 (4 papers ✓)
- Multi-theory: Papers 8, 9 (2 papers ✓)

### 9.2 Annotation Schema with Provenance (per Pearl, Bates)

```yaml
# gold_standard/v1.0/annotations/kaplan_1989.yaml
paper_id: "kaplan_1989"
citation: "Kaplan, R., & Kaplan, S. (1989). The experience of nature."
version: "1.0"

metadata:
  annotator: "panel_consensus"
  annotation_date: "2026-01-19"
  review_status: "approved"

paper_characteristics:
  type: "theory_book"
  theories: ["ART"]
  is_multi_theory: false
  ecological_validity: "field_natural"
  methodology_score: [0.5, 0.7]

expected_beliefs:
  - id: "kaplan_1989_b1"
    content: "Directed attention is a limited resource that becomes fatigued with use"
    expected_credence: [0.6, 0.8]
    epistemic_level: "theoretical"
    theory: "ART"
    environment_id: null  # Theoretical, not about specific environment
    outcome_id: "psych.attention.fatigue"
    scope:
      population: "general"
      setting: null
      duration: null
    annotation_metadata:
      confidence: "high"
      basis: "Core theoretical claim of ART, widely cited"

  - id: "kaplan_1989_b2"
    content: "Natural environments facilitate recovery from directed attention fatigue"
    expected_credence: [0.5, 0.7]
    epistemic_level: "intermediate"
    theory: "ART"
    environment_id: "natural.views"
    outcome_id: "psych.attention.restoration"
    causal_direction: "forward"
    scope:
      population: "general"
      setting: "natural_environments"
    annotation_metadata:
      confidence: "high"
      basis: "Central ART prediction"

expected_constraints:
  - source: "kaplan_1989_b1"
    target: "kaplan_1989_b2"
    type: "supports"
    causal_direction: "forward"
    expected_strength: [0.6, 0.8]
    annotation_metadata:
      confidence: "high"
      basis: "Logical connection in ART framework"

expected_bridges:
  - source_theory: "ART"
    target_theory: "SRT"
    bridge_type: "analogical"
    expected_confidence: [0.3, 0.5]
    annotation_metadata:
      confidence: "medium"
      basis: "Both address restoration; different mechanisms proposed"

should_NOT_extract:
  - pattern: "ART is proven"
    reason: "Overstates certainty"
  - pattern: "Nature always restores"
    reason: "Overgeneralization"
  - pattern: "credence > 0.85"
    reason: "Theory book, not experimental confirmation"

red_flags:
  - "Any specific effect size claim (book doesn't report them)"
  - "Claims about specific populations not discussed"
```

### 9.3 Corpus Versioning Protocol (per Panel Consensus)

```
gold_standard/
├── v1.0/
│   ├── manifest.yaml
│   │   ├── version: "1.0"
│   │   ├── release_date: "2026-01-25"
│   │   ├── papers: [list of 12 papers]
│   │   ├── annotators: ["panel_consensus"]
│   │   └── notes: "Initial release"
│   ├── annotations/
│   │   ├── kaplan_1989.yaml
│   │   ├── ulrich_1984.yaml
│   │   └── ... (12 files)
│   ├── baseline_results.json
│   │   ├── extraction_f1: 0.72
│   │   ├── credence_in_range: 0.68
│   │   └── ...
│   └── FROZEN  # Empty file indicating immutability
├── CHANGELOG.md
│   └── "v1.0 (2026-01-25): Initial release with 12 papers"
└── current -> v1.0/  # Symlink
```

**Versioning Rules**:
1. v1.0 → v1.1: Paper additions only (minor)
2. v1.x → v2.0: Annotation changes (major)
3. Never modify files in released version
4. Run migration tests when releasing new major version

### 9.4 Validation Metrics (Enhanced per Simon)

```python
@dataclass
class ValidationReport:
    # Core metrics
    belief_recall: float
    belief_precision: float
    belief_f1: float

    # Stratified F1 (per Simon)
    f1_by_level: Dict[str, float]  # empirical, intermediate, theoretical

    # Credence calibration
    credence_mae: float
    credence_in_range: float
    credence_by_level: Dict[str, float]

    # Constraint metrics
    constraint_recall: float
    constraint_precision: float

    # Negative tests
    false_extractions: List[str]
    should_not_extract_violations: int

    # Phase eligibility
    phases_passed: List[ValidationPhase]

    # Confidence
    corpus_version: str
    statistical_power: str  # "sufficient", "preliminary", "insufficient"

PASS_THRESHOLDS = {
    "empirical": {"f1": 0.75, "credence_in_range": 0.75},
    "intermediate": {"f1": 0.65, "credence_in_range": 0.70},
    "theoretical": {"f1": 0.55, "credence_in_range": 0.65},
    "overall": {"f1": 0.70, "credence_in_range": 0.70},
}

def passed(self) -> bool:
    """Check if validation passed at each level."""
    for level, thresholds in PASS_THRESHOLDS.items():
        if level == "overall":
            if self.belief_f1 < thresholds["f1"]:
                return False
            if self.credence_in_range < thresholds["credence_in_range"]:
                return False
        else:
            if self.f1_by_level.get(level, 0) < thresholds["f1"]:
                return False
    return self.should_not_extract_violations == 0
```

### 9.5 Tests for Sprint 9

- [ ] All 12 papers annotated in YAML format
- [ ] Validation metrics computed correctly
- [ ] Pass thresholds enforced by level
- [ ] Versioning system works (create v1.0, attempt modification fails)
- [ ] Migration test framework ready

---

## Implementation Schedule

```
Week 1: Sprint 6 - Causal Structure & Scope
├── Day 1-2: CausalDirection enum + constraint changes
├── Day 3-4: ScopeConditions + overlap detection
├── Day 5: Conflict type enhancements
└── Day 6-7: Testing + documentation

Week 2: Sprint 7 - Environment Ontology
├── Day 1-3: environment_taxonomy.py
├── Day 4-5: Antonym detection + diversity index
└── Day 6-7: Testing + panel checkpoint

Week 3: Sprint 8 - Multi-Theory & Validation Infra
├── Day 1-2: Evidence clustering + SHARED_EVIDENCE
├── Day 3-4: Phased validation gates
├── Day 5: Stratified LOO
└── Day 6-7: Ecological validity + testing

Week 4-5: Sprint 9 - Gold Standard
├── Day 1-4: Annotate 12 papers
├── Day 5-7: Validation metrics implementation
├── Day 8-10: Run calibration, iterate
└── Final: Baseline report + versioning
```

---

## Success Criteria

**Sprint 6**:
- Causal direction populated for test extractions
- Scope overlap correctly identifies boundaries
- No regression on 57 existing tests

**Sprint 7**:
- Environment taxonomy resolves terminology variations
- Antonym equivalence prevents false conflicts
- Panel approves ontology before proceeding

**Sprint 8**:
- Multi-theory papers don't double-count evidence
- Validation gates enforce corpus requirements
- Stratified LOO produces meaningful metrics

**Sprint 9**:
- 12 papers annotated with full provenance
- F1 ≥ 0.70 overall, meeting level-specific thresholds
- Zero "should_NOT_extract" violations
- Corpus versioning operational

**Overall**:
- Panel signs off on Sprint 7 ontology
- Baseline validation report demonstrates credibility
- System outputs framed as "auditable literature summary"

---

## Open Items

1. **Identify remaining Gold Standard papers**: Lighting paper, wayfinding paper, null result paper, additional SRT paper
2. **Panel checkpoint after Sprint 7**: Review environment ontology before validation
3. **Annual review schedule**: Plan first major version update for 2027-01

---

*Plan finalized. Ready for implementation.*
