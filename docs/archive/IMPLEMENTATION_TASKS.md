# IMPLEMENTATION_TASKS.md — Epistemic Tier 2 Integration

Work through these tasks **in order**. Each task has:
- **Do**: exactly what to implement
- **Test**: how to verify it works
- **Commit**: message format

Do NOT skip ahead. Do NOT proceed if a test fails.

---

## Sprint 0: Discovery (Do This First)

### Task 0.1: Map the existing codebase

**Do**: Run these commands and record the output in `docs/CODEBASE_MAP.md`:

```bash
# Project structure (top 3 levels)
find . -maxdepth 3 -type f \( -name "*.py" -o -name "*.ts" -o -name "*.js" \) | head -60

# Where are the data models / schemas?
grep -rl "class.*Node\|class.*Edge\|class.*Claim\|interface.*Node" --include="*.py" --include="*.ts" .

# Where are the enums?
grep -rl "class.*Enum\|NodeDomain\|LinkType\|node_domain\|link_type" --include="*.py" --include="*.ts" .

# Where is the BN assembly?
grep -rl "bayesian\|bn_assembly\|dag\|causal_graph\|assemble" --include="*.py" --include="*.ts" .

# Where is the extraction pipeline?
grep -rl "extract.*claim\|pipeline\|parse.*paper" --include="*.py" --include="*.ts" .

# Where is entrenchment / coherence?
grep -rl "entrenchment\|coherence\|constraint_satisfaction" --include="*.py" --include="*.ts" .

# Where are the tests?
find . -name "test_*" -o -name "*.test.*" | head -20

# What test framework?
cat pytest.ini 2>/dev/null || cat pyproject.toml 2>/dev/null | head -30
```

Write the actual file paths into `docs/CODEBASE_MAP.md` using this format:

```
## Actual File Locations
- Node model: <path>
- Edge model: <path>
- Enums: <path>
- BN assembly: <path>
- Extraction pipeline: <path>
- Entrenchment: <path>
- Tests directory: <path>
- Bridge warrants: <path>
```

**Test**: The file `docs/CODEBASE_MAP.md` exists and has all 8 paths filled in.

**Commit**: `[Sprint 0 / Task 0.1] Map existing codebase structure`

### Task 0.2: Verify baseline tests pass

**Do**: Run the full test suite. Fix nothing — just confirm the current state.

```bash
pytest tests/ -v 2>&1 | tail -20
```

Record the result (pass count, fail count) at the top of `docs/CODEBASE_MAP.md`.

**Test**: You know how many tests exist and how many pass.

**Commit**: `[Sprint 0 / Task 0.2] Record baseline test state`

---

## Sprint 1: Schema Extensions

### Task 1.1: Add EPISTEMIC to node_domain enum

**Do**: Find the file containing node domain/type enums (from Task 0.1).
Add a new value `EPISTEMIC` to the node_domain enum.

If the enum looks like:
```python
class NodeDomain(str, Enum):
    AFFECT_AESTHETICS = "affect_aesthetics"
    ENVIRONMENTAL_PSYCH = "environmental_psych"
    ...
```

Add:
```python
    EPISTEMIC = "epistemic"
```

If it's TypeScript, same idea with the appropriate syntax.

**Test**: Import the enum in a Python shell or test and confirm `NodeDomain.EPISTEMIC` exists.

```python
from <module> import NodeDomain
assert NodeDomain.EPISTEMIC == "epistemic"
```

**Commit**: `[Sprint 1 / Task 1.1] Add EPISTEMIC node domain`

### Task 1.2: Add epistemic node subtypes

**Do**: In the same or related enum file, add four new node subtype values:

```python
E1_COHERENCE_BELIEF_MAINTENANCE = "e1_coherence_belief_maintenance"
E2_SOCIAL_EPISTEMICS = "e2_social_epistemics"
E3_EPISTEMIC_EMOTIONS = "e3_epistemic_emotions"
E4_REFLECTIVE_EQUILIBRIUM = "e4_reflective_equilibrium"
```

**Test**:
```python
from <module> import NodeSubtype  # or whatever the enum is called
assert hasattr(NodeSubtype, 'E1_COHERENCE_BELIEF_MAINTENANCE')
assert hasattr(NodeSubtype, 'E2_SOCIAL_EPISTEMICS')
assert hasattr(NodeSubtype, 'E3_EPISTEMIC_EMOTIONS')
assert hasattr(NodeSubtype, 'E4_REFLECTIVE_EQUILIBRIUM')
```

**Commit**: `[Sprint 1 / Task 1.2] Add four epistemic node subtypes`

### Task 1.3: Add epistemic link types

**Do**: In the link/edge type enum, add these seven values:

```python
EPISTEMIC_DERIVATION = "epistemic_derivation"           # Tier 1 → Tier 2 template
EPISTEMIC_CROSS_TEMPLATE = "epistemic_cross_template"   # between Tier 2 templates
EPISTEMIC_MEDIATION = "epistemic_mediation"             # claim mediated by interpretation
COHERENCE_SUPPORT = "coherence_support"                 # A increases coherence of B
COHERENCE_TENSION = "coherence_tension"                 # A decreases coherence of B
ARGUMENTATIVE_SUPPORT = "argumentative_support"         # finding supports via argument
ARGUMENTATIVE_CHALLENGE = "argumentative_challenge"     # finding challenges via argument
```

**Test**:
```python
from <module> import LinkType
for lt in ['EPISTEMIC_DERIVATION', 'EPISTEMIC_CROSS_TEMPLATE', 'EPISTEMIC_MEDIATION',
           'COHERENCE_SUPPORT', 'COHERENCE_TENSION',
           'ARGUMENTATIVE_SUPPORT', 'ARGUMENTATIVE_CHALLENGE']:
    assert hasattr(LinkType, lt), f"Missing: {lt}"
```

**Commit**: `[Sprint 1 / Task 1.3] Add seven epistemic link types`

### Task 1.4: Add pathway_type enum

**Do**: Create a new enum (in the enums file or a new file if appropriate):

```python
class PathwayType(str, Enum):
    SUBPERSONAL = "subpersonal"            # direct physiological, no interpretation
    PERSONAL_EPISTEMIC = "personal_epistemic"  # fully interpretation-mediated
    MIXED = "mixed"                        # both channels active
```

**Test**:
```python
from <module> import PathwayType
assert PathwayType.SUBPERSONAL == "subpersonal"
assert PathwayType.PERSONAL_EPISTEMIC == "personal_epistemic"
assert PathwayType.MIXED == "mixed"
```

**Commit**: `[Sprint 1 / Task 1.4] Add PathwayType enum`

### Task 1.5: Add replication_status enum

**Do**:
```python
class ReplicationStatus(str, Enum):
    REPLICATED = "replicated"
    PARTIALLY_REPLICATED = "partially_replicated"
    UNREPLICATED = "unreplicated"
    FAILED_REPLICATION = "failed_replication"
```

**Test**: All four values accessible.

**Commit**: `[Sprint 1 / Task 1.5] Add ReplicationStatus enum`

### Task 1.6: Add pe_subtype enum

**Do**:
```python
class PESubtype(str, Enum):
    FUNCTIONAL_PE = "functional_pe"      # affordance mismatch
    NAVIGATIONAL_PE = "navigational_pe"  # spatial model mismatch
    SOCIAL_PE = "social_pe"              # social script mismatch
```

**Test**: All three values accessible.

**Commit**: `[Sprint 1 / Task 1.6] Add PESubtype enum`

### Task 1.7: Add bridge warrant subtypes

**Do**: In the bridge warrant type enum (or wherever warrant types are defined), add:

```python
EPISTEMIC_COHERENCE_WARRANT = "epistemic_coherence_warrant"   # accepted via web coherence
ARGUMENTATIVE_WARRANT = "argumentative_warrant"               # survived adversarial scrutiny
EPISTEMIC_VIGILANCE_WARRANT = "epistemic_vigilance_warrant"   # evaluated via source quality
```

**Test**: All three values accessible.

**Commit**: `[Sprint 1 / Task 1.7] Add three epistemic bridge warrant subtypes`

### Task 1.8: Extend the Node model with epistemic template fields

**Do**: Find the Node model class (from Task 0.1). Add these optional fields
to the model (only populated when node is an epistemic template):

```python
# These fields are Optional — only set for epistemic template nodes
derivation_path: Optional[List[str]] = None       # Tier 1 framework IDs this derives from
core_claims: Optional[List[dict]] = None           # [{text: str, citation: str, status: str}]
bayesian_coherentist_mode: Optional[float] = None  # 0.0=Bayesian, 1.0=coherentist (E1 only)
empirical_status: Optional[str] = None             # well_established|supported|contested|speculative
normative_weight: Optional[float] = None           # 0.0=descriptive, 1.0=normative
key_references: Optional[List[dict]] = None        # [{citation: str, year: int, google_scholar_count: int}]
```

Adapt the field style to match how the existing model handles optional fields
(dataclass with defaults, Pydantic model, TypedDict, whatever pattern is in use).

**Test**: Create a Node with `domain=EPISTEMIC`, `subtype=E1_COHERENCE_BELIEF_MAINTENANCE`,
and populate all new fields. Confirm it serializes and deserializes correctly.

**Commit**: `[Sprint 1 / Task 1.8] Add epistemic template fields to Node model`

### Task 1.9: Extend the Edge model with pathway_type

**Do**: Add an optional `pathway_type` field to the Edge model:

```python
pathway_type: Optional[str] = None  # PathwayType value, only for BN edges
```

**Test**: Create an Edge with `pathway_type="subpersonal"`. Confirm it
serializes correctly.

**Commit**: `[Sprint 1 / Task 1.9] Add pathway_type to Edge model`

### Task 1.10: Extend claim nodes with argumentative fields

**Do**: Add these optional fields to claim-type nodes (however claims are
represented in the existing model):

```python
argument_for: Optional[str] = None            # theoretical position this supports
argument_against: Optional[str] = None        # theoretical position this challenges
adversarial_scrutiny_survived: Optional[bool] = None  # tested by rival group?
replication_type: Optional[str] = None        # original|direct_replication|conceptual_replication|meta_analysis
pe_subtype: Optional[str] = None              # PESubtype value, if claim involves prediction error
```

**Test**: Create a claim node with all new fields populated. Confirm serialization.

**Commit**: `[Sprint 1 / Task 1.10] Add argumentative and PE fields to claim nodes`

### Task 1.11: Run full test suite

**Do**: `pytest tests/ -v`

**Test**: Same pass count as Task 0.2 (no regressions). All new enum and
model tests also pass.

**Commit**: `[Sprint 1 / Task 1.11] Sprint 1 complete — schema extensions verified`

---

## Sprint 2: BN Integration

### Task 2.1: Add epistemic BN node definitions

**Do**: Find how BN variable nodes are defined in the BN assembly module.
Add definitions for these 10 new variables:

| Variable Name          | Type       | Range    | Description                                    |
|------------------------|------------|----------|------------------------------------------------|
| environmental_legibility | continuous | [0, 1]  | How well environment supports belief formation |
| belief_coherence       | continuous | [0, 1]   | Internal consistency of environmental model    |
| epistemic_fluency      | continuous | [0, 1]   | Speed/ease of coherent interpretation          |
| epistemic_affect       | continuous | [-1, 1]  | Hedonic signal from epistemic processing       |
| functional_PE          | continuous | [0, 1]   | Affordance mismatch                            |
| navigational_PE        | continuous | [0, 1]   | Spatial model mismatch                         |
| social_PE              | continuous | [0, 1]   | Social script mismatch                         |
| source_quality         | continuous | [0, 1]   | Composite evidence quality score               |
| claim_acceptance       | continuous | [0, 1]   | Posterior acceptance probability               |
| claim_coherence        | continuous | [0, 1]   | How well claim fits existing web               |

Match whatever pattern the existing BN nodes use (dict, class, config file, etc.).

**Test**: All 10 nodes can be instantiated and appear in a BN graph.

**Commit**: `[Sprint 2 / Task 2.1] Add 10 epistemic BN variable nodes`

### Task 2.2: Add epistemic BN edges (environmental subgraph)

**Do**: Wire these causal edges:

```
environmental_legibility → epistemic_fluency
epistemic_fluency → epistemic_affect
epistemic_affect → overall_wellbeing   (connect to existing wellbeing node if present)
functional_PE → epistemic_affect
navigational_PE → epistemic_affect
social_PE → epistemic_affect
environmental_legibility → wayfinding_success  (connect to existing node if present)
epistemic_affect → allostatic_regulation       (connect to existing node if present)
```

If target nodes (overall_wellbeing, wayfinding_success, allostatic_regulation)
don't exist, create stub nodes for them.

**Test**: The BN DAG remains acyclic after adding edges. All new edges exist.

```python
# Pseudocode — adapt to actual BN library
assert bn.has_edge("environmental_legibility", "epistemic_fluency")
assert bn.has_edge("functional_PE", "epistemic_affect")
assert nx.is_directed_acyclic_graph(bn.graph)  # or equivalent
```

**Commit**: `[Sprint 2 / Task 2.2] Wire epistemic environmental BN edges`

### Task 2.3: Add source quality BN subgraph

**Do**: Add four component nodes and wire them:

```
methodological_rigor → source_quality
theoretical_commitment → source_quality     (negative influence)
independence_of_evidence → source_quality
replication_status → source_quality
source_quality → claim_acceptance
claim_coherence → claim_acceptance
```

These are nodes in the BN, not computed properties on claim nodes (that comes
in Sprint 3). For now just wire the structure.

**Test**: All 4 component → source_quality edges exist. DAG still acyclic.

**Commit**: `[Sprint 2 / Task 2.3] Add source quality BN subgraph`

### Task 2.4: Tag all BN edges with pathway_type

**Do**: Create a lookup table that maps environmental variable categories to
default pathway types:

```python
PATHWAY_DEFAULTS = {
    # Subpersonal — direct physiological, no interpretation needed
    "temperature": PathwayType.SUBPERSONAL,
    "thermal": PathwayType.SUBPERSONAL,
    "circadian": PathwayType.SUBPERSONAL,
    "air_quality": PathwayType.SUBPERSONAL,
    "ventilation": PathwayType.SUBPERSONAL,
    "acoustic_db": PathwayType.SUBPERSONAL,

    # Personal epistemic — fully interpretation-mediated
    "spatial_layout": PathwayType.PERSONAL_EPISTEMIC,
    "wayfinding": PathwayType.PERSONAL_EPISTEMIC,
    "legibility": PathwayType.PERSONAL_EPISTEMIC,
    "social_meaning": PathwayType.PERSONAL_EPISTEMIC,
    "aesthetic_judgment": PathwayType.PERSONAL_EPISTEMIC,
    "functional_meaning": PathwayType.PERSONAL_EPISTEMIC,

    # Mixed — both channels
    "lighting": PathwayType.MIXED,
    "color": PathwayType.MIXED,
    "biophilic_elements": PathwayType.MIXED,
    "noise_meaning": PathwayType.MIXED,
    "crowding": PathwayType.MIXED,
    "ceiling_height": PathwayType.MIXED,
}
```

Write a function `assign_pathway_type(edge, lookup=PATHWAY_DEFAULTS)` that:
1. Checks if the edge's source node matches a key in the lookup
2. Assigns the pathway_type
3. Defaults to MIXED if no match

Run it on all existing BN edges. All new epistemic edges should be tagged
PERSONAL_EPISTEMIC by default (they are interpretation-mediated).

**Test**: Every edge in the BN has a non-null pathway_type.

```python
for edge in bn.edges():
    assert edge.pathway_type is not None, f"Edge {edge} missing pathway_type"
```

**Commit**: `[Sprint 2 / Task 2.4] Tag all BN edges with pathway_type`

### Task 2.5: Implement source_quality computation function

**Do**: Create a function:

```python
def compute_source_quality(
    methodological_rigor: float,      # [0, 1]
    theoretical_commitment: float,    # [0, 1] high = more potential bias
    independence_of_evidence: float,  # [0, 1]
    replication_status: float,        # [0, 1]
    weights: dict = None
) -> float:
    """
    Weighted combination of four source quality components.
    Default weights: rigor=0.40, commitment=0.15, independence=0.25, replication=0.20
    Note: theoretical_commitment is inverted (high commitment = lower quality).
    """
    if weights is None:
        weights = {
            "rigor": 0.40,
            "commitment": 0.15,
            "independence": 0.25,
            "replication": 0.20
        }
    return (
        weights["rigor"] * methodological_rigor +
        weights["commitment"] * (1.0 - theoretical_commitment) +
        weights["independence"] * independence_of_evidence +
        weights["replication"] * replication_status
    )
```

Place it in a new file or in the existing source quality / evidence evaluation module.

**Test**:
```python
# High quality: good methods, independent, replicated, low commitment
assert compute_source_quality(0.9, 0.1, 0.9, 0.9) > 0.8

# Low quality: weak methods, single lab, unreplicated, high commitment
assert compute_source_quality(0.2, 0.9, 0.1, 0.0) < 0.3

# Commitment penalty: identical except commitment differs
high_commit = compute_source_quality(0.8, 0.8, 0.7, 0.7)
low_commit = compute_source_quality(0.8, 0.2, 0.7, 0.7)
assert low_commit > high_commit
```

**Commit**: `[Sprint 2 / Task 2.5] Implement source_quality computation`

### Task 2.6: Full test suite

**Do**: `pytest tests/ -v`

**Test**: No regressions. All Sprint 2 tests pass.

**Commit**: `[Sprint 2 / Task 2.6] Sprint 2 complete — BN integration verified`

---

## Sprint 3: Reflexive Monitoring Algorithms

### Task 3.1: Coherence audit algorithm

**Do**: Create `src/web/coherence_audit.py` (or equivalent location). Implement:

```python
def run_coherence_audit(
    web,                    # the web-of-belief graph
    pre_snapshot: dict,     # {node_id: entrenchment_score} before integration
    post_snapshot: dict,    # {node_id: entrenchment_score} after integration
    new_claim_ids: list,    # IDs of newly integrated claims
    threshold: float = 0.1  # minimum delta to flag
) -> dict:
    """
    Detects nodes whose entrenchment changed purely from coherence settling
    (not from new direct evidence).

    Returns:
    {
        "flagged_nodes": [
            {
                "node_id": str,
                "old_entrenchment": float,
                "new_entrenchment": float,
                "coherence_delta": float,
                "direct_evidence_delta": float,
                "flag_type": "COHERENCE_DRIFT_POSITIVE" | "COHERENCE_DRIFT_NEGATIVE",
                "triggering_claims": [str]  # new claims that caused the web shift
            }
        ],
        "total_nodes_checked": int,
        "total_flagged": int
    }
    """
```

**Algorithm**:
1. For each node in the web (excluding the new claims themselves):
2. Compute `coherence_delta = post_snapshot[node_id] - pre_snapshot[node_id]`
3. Compute `direct_evidence_delta`: did any of the new claims provide direct
   evidence about this specific node? (Check if any new claim has this node
   as its subject/target.)
4. If `abs(coherence_delta) > threshold` AND `direct_evidence_delta ≈ 0`:
   flag it.

**Test**: Create a small test web with 5 nodes. Add a new claim that supports
Node A. After re-convergence, Node B (connected to A via coherence links)
should have increased entrenchment even though no new evidence mentions B.
The audit should flag Node B as COHERENCE_DRIFT_POSITIVE.

**Commit**: `[Sprint 3 / Task 3.1] Implement coherence audit`

### Task 3.2: Entrenchment asymmetry monitor

**Do**: Create `src/web/asymmetry_monitor.py` (or equivalent). Implement:

```python
def run_asymmetry_monitor(
    web,
    threshold: float = 3.0,  # entrenchment / direct_evidence ratio
    epsilon: float = 0.01    # avoid division by zero
) -> dict:
    """
    Identifies nodes that are highly entrenched (many coherence connections)
    but have weak direct empirical support.

    Returns:
    {
        "flagged_nodes": [
            {
                "node_id": str,
                "entrenchment_score": float,
                "direct_evidence_score": float,
                "asymmetry_ratio": float,
                "recommendation": str  # e.g., "Needs independent replication"
            }
        ],
        "total_checked": int,
        "total_flagged": int
    }
    """
```

**Algorithm**:
1. For each claim node, compute:
   - `entrenchment_score`: number and strength of coherence connections
   - `direct_evidence_score`: quality-weighted count of studies specifically
     about this claim (use `source_quality` if available, else count)
2. `asymmetry_ratio = entrenchment_score / max(direct_evidence_score, epsilon)`
3. Flag if `asymmetry_ratio > threshold`

**Test**: Create a node with 10 coherence links but only 1 direct study.
It should be flagged. A node with 10 coherence links and 10 direct studies
should NOT be flagged.

**Commit**: `[Sprint 3 / Task 3.2] Implement entrenchment asymmetry monitor`

### Task 3.3: Structural bias detection

**Do**: Create `src/web/bias_detection.py` (or equivalent). Implement:

```python
def run_structural_bias_detection(
    web,
    node_id: str,
    independence_threshold: float = 0.3,
    paradigm_threshold: float = 0.2,
    method_threshold: float = 0.2
) -> dict:
    """
    Checks whether supporting evidence for a claim comes from diverse,
    independent sources.

    Returns:
    {
        "node_id": str,
        "evidence_independence": float,   # [0, 1] — 1 = fully independent labs
        "paradigm_diversity": float,      # [0, 1] — 1 = diverse theoretical traditions
        "method_diversity": float,        # [0, 1] — 1 = diverse measurement methods
        "flags": [str],                   # list of triggered flag names
        "details": str                    # human-readable explanation
    }
    """
```

**Algorithm**:
1. Collect all evidence nodes supporting this claim
2. `evidence_independence`: Build author/lab graph from evidence metadata.
   Compute 1 - (largest connected component / total evidence nodes).
3. `paradigm_diversity`: Count distinct theoretical traditions among evidence.
   Normalize by total evidence count.
4. `method_diversity`: Count distinct measurement modalities (EEG, fMRI,
   behavioral, cortisol, self-report, etc.). Normalize.
5. Flag if any dimension below its threshold.

**Test**: A claim supported by 5 studies all from the same lab, same paradigm,
same method → all three flags triggered. A claim supported by 5 studies from
5 different labs, 3 paradigms, 4 methods → no flags.

**Commit**: `[Sprint 3 / Task 3.3] Implement structural bias detection`

### Task 3.4: Adversarial review cycle

**Do**: Create `src/web/adversarial_review.py` (or equivalent). Implement:

```python
def run_adversarial_review(
    web,
    n_top_nodes: int = 10,
    precision_boost: float = 1.5  # how much to boost counter-evidence
) -> dict:
    """
    Stress-tests the most entrenched claims by boosting counter-evidence.

    Returns:
    {
        "reviewed_nodes": [
            {
                "node_id": str,
                "pre_review_entrenchment": float,
                "post_review_entrenchment": float,
                "vulnerability_score": float,  # magnitude of drop
                "survived": bool,              # still above acceptance threshold?
                "counter_evidence_summary": [str],
                "recommendation": str
            }
        ]
    }
    """
```

**Algorithm**:
1. Identify N most entrenched claim nodes
2. For each, find all COHERENCE_TENSION links and FAILED_REPLICATION evidence
3. Temporarily multiply counter-evidence weight by `precision_boost`
4. Re-run constraint satisfaction (or re-compute entrenchment)
5. Record which nodes survived and which became vulnerable
6. Restore original weights

**Test**: Create a test web where Node X is entrenched but has one study with
FAILED_REPLICATION. Boosting that counter-evidence should reduce X's
entrenchment measurably.

**Commit**: `[Sprint 3 / Task 3.4] Implement adversarial review cycle`

### Task 3.5: Full test suite

**Do**: `pytest tests/ -v`

**Test**: No regressions. All Sprint 3 tests pass.

**Commit**: `[Sprint 3 / Task 3.5] Sprint 3 complete — reflexive monitoring verified`

---

## Sprint 4: Extraction Pipeline Extensions

### Task 4.1: Extract argumentative structure from papers

**Do**: In the extraction pipeline, extend the claim extraction to also capture:

```python
@dataclass
class ArgumentativeMetadata:
    argument_for: Optional[str] = None       # which theory this supports
    argument_against: Optional[str] = None   # which theory this challenges
    adversarial_scrutiny_survived: bool = False
    replication_type: str = "original"       # original|direct_replication|conceptual_replication|meta_analysis
```

**How to detect these**:
- `argument_for` / `argument_against`: Look in Introduction and Discussion
  sections for phrases like "consistent with [Theory]", "supports [Theory]",
  "challenges [Theory]", "contrary to [Theory]", "in contrast to [Theory]"
- `replication_type`: Check title and methods for "replication", "meta-analysis",
  "conceptual replication"
- `adversarial_scrutiny_survived`: Check if authors' affiliations differ from
  the theory's originators (requires author metadata)

Add these fields to the claim output object.

**Test**: Run extraction on a test paper that explicitly supports one theory
and challenges another. Confirm `argument_for` and `argument_against` are
correctly populated.

**Commit**: `[Sprint 4 / Task 4.1] Extract argumentative structure`

### Task 4.2: Extract source quality metadata

**Do**: Extend the extraction to capture:

```python
@dataclass
class SourceQualityMetadata:
    study_design: str          # rct|quasi_experimental|correlational|case_study|qualitative
    sample_size: Optional[int] = None
    pre_registered: Optional[bool] = None
    author_affiliations: List[str] = field(default_factory=list)
    funding_source: Optional[str] = None
    paper_type: str = "primary"  # primary|review|meta_analysis|commentary
```

**How to detect**:
- `study_design`: Scan methods section for "random assignment", "quasi-experimental",
  "correlational", "case study"
- `sample_size`: Extract N from methods (regex: `N\s*=\s*\d+`, `n\s*=\s*\d+`,
  `(\d+)\s*participants`)
- `pre_registered`: Look for "pre-registered", "OSF", "AsPredicted"
- `author_affiliations`: Extract from author metadata
- `paper_type`: Check if "review", "meta-analysis" in title/abstract

**Test**: Run on a test paper. Confirm study_design and sample_size are extracted.

**Commit**: `[Sprint 4 / Task 4.2] Extract source quality metadata`

### Task 4.3: Classify epistemic mediation pathway

**Do**: Add a classifier that tags each extracted claim with a pathway type:

```python
EPISTEMIC_KEYWORDS = [
    "interpretation", "comprehension", "legibility", "meaning", "understanding",
    "sense-making", "wayfinding", "recognition", "categorization", "expectation",
    "prediction", "belief", "judgment", "appraisal", "evaluation"
]

SUBPERSONAL_KEYWORDS = [
    "thermal", "circadian", "acoustic", "cortisol", "physiological", "autonomic",
    "hormonal", "illuminance", "air quality", "ventilation", "temperature",
    "humidity", "decibel", "lux"
]

def classify_pathway(claim_text: str) -> str:
    has_epistemic = any(kw in claim_text.lower() for kw in EPISTEMIC_KEYWORDS)
    has_subpersonal = any(kw in claim_text.lower() for kw in SUBPERSONAL_KEYWORDS)

    if has_epistemic and has_subpersonal:
        return "mixed"
    elif has_epistemic:
        return "personal_epistemic"
    elif has_subpersonal:
        return "subpersonal"
    else:
        return "mixed"  # default to mixed when uncertain
```

**Test**:
```python
assert classify_pathway("Temperature affects circadian rhythm") == "subpersonal"
assert classify_pathway("Spatial legibility affects wayfinding comprehension") == "personal_epistemic"
assert classify_pathway("Lighting color temperature affects mood interpretation") == "mixed"
```

**Commit**: `[Sprint 4 / Task 4.3] Classify epistemic mediation pathway`

### Task 4.4: Classify PE subtype

**Do**: Add a classifier for prediction error subtypes:

```python
FUNCTIONAL_PE_KEYWORDS = ["affordance", "function", "purpose", "use", "activity", "what the space is for"]
NAVIGATIONAL_PE_KEYWORDS = ["wayfinding", "lost", "disorientation", "route", "layout", "spatial structure", "navigate"]
SOCIAL_PE_KEYWORDS = ["appropriate behavior", "social norm", "who belongs", "institutional meaning", "social coding", "etiquette"]

def classify_pe_subtype(claim_text: str) -> Optional[str]:
    """Returns PE subtype if claim involves prediction error, else None."""
    pe_indicators = ["prediction error", "surprise", "expectation violation", "mismatch", "unexpected"]
    if not any(ind in claim_text.lower() for ind in pe_indicators):
        return None

    # Check which subtype
    scores = {
        "functional_pe": sum(1 for kw in FUNCTIONAL_PE_KEYWORDS if kw in claim_text.lower()),
        "navigational_pe": sum(1 for kw in NAVIGATIONAL_PE_KEYWORDS if kw in claim_text.lower()),
        "social_pe": sum(1 for kw in SOCIAL_PE_KEYWORDS if kw in claim_text.lower()),
    }
    if max(scores.values()) == 0:
        return "functional_pe"  # default for unclassified PE claims
    return max(scores, key=scores.get)
```

**Test**:
```python
assert classify_pe_subtype("wayfinding mismatch causes disorientation") == "navigational_pe"
assert classify_pe_subtype("affordance prediction error in hospital design") == "functional_pe"
assert classify_pe_subtype("cortisol levels increased") is None  # no PE
```

**Commit**: `[Sprint 4 / Task 4.4] Classify PE subtype`

### Task 4.5: Full test suite

**Do**: `pytest tests/ -v`

**Test**: No regressions.

**Commit**: `[Sprint 4 / Task 4.5] Sprint 4 complete — extraction extensions verified`

---

## Sprint 5: Integration Testing

### Task 5.1: Create the Ulrich test corpus

**Do**: Create `tests/fixtures/ulrich_test_corpus.json` containing ~20 synthetic
claims related to the Ulrich (1984) nature-view hospital recovery finding.
Include a mix of:

- Claims supporting nature-health effects (varied quality, varied labs)
- Claims challenging nature-health effects (replication failures)
- Claims about mechanism (circadian, stress reduction, attention restoration)
- Claims from single-lab clusters (for bias detection testing)

Each claim should have all fields: causal text, study_design, sample_size,
author_affiliations, argument_for/against, replication_type.

**Test**: File loads and validates against the claim schema.

**Commit**: `[Sprint 5 / Task 5.1] Create Ulrich test corpus`

### Task 5.2: End-to-end pipeline test

**Do**: Write `tests/test_e2e_epistemic.py`:

1. Load Ulrich test corpus
2. Run extraction to populate claim fields
3. Compute source_quality for each claim
4. Insert claims into a test web
5. Run coherence settling
6. Run BN assembly
7. Run all four monitoring tools (coherence audit, asymmetry, bias, adversarial)

Assert:
- Pipeline completes without errors
- BN is acyclic
- All edges have pathway_type
- Source quality scores are in [0, 1]
- Monitoring reports are non-empty

**Test**: `pytest tests/test_e2e_epistemic.py -v` passes.

**Commit**: `[Sprint 5 / Task 5.2] End-to-end epistemic pipeline test`

### Task 5.3: Validate three-pathway separation

**Do**: In the test corpus, include:
- A circadian/lighting claim (should be SUBPERSONAL or MIXED)
- A spatial legibility claim (should be PERSONAL_EPISTEMIC)
- A nature-view claim (should be MIXED)

Assert that pathway classification is correct for all three.

**Test**: These specific assertions pass in the e2e test.

**Commit**: `[Sprint 5 / Task 5.3] Validate three-pathway separation`

### Task 5.4: Validate bias detection catches planted bias

**Do**: In the test corpus, include 4 claims all from the same lab
(same author_affiliations) supporting the same hypothesis.

Assert that structural_bias_detection flags this cluster with
evidence_independence < 0.3.

**Test**: The bias flag is triggered.

**Commit**: `[Sprint 5 / Task 5.4] Validate bias detection on planted cluster`

### Task 5.5: Validate source quality ordering

**Do**: Include in the test corpus:
- Claim A: RCT, n=200, pre-registered, replicated, independent lab
- Claim B: Correlational, n=30, not pre-registered, unreplicated, same lab as theory authors

Assert: `source_quality(A) > source_quality(B)` by a substantial margin.

**Test**: The ordering is correct and the gap is > 0.3.

**Commit**: `[Sprint 5 / Task 5.5] Validate source quality ordering`

### Task 5.6: Final full test suite

**Do**: `pytest tests/ -v`

**Test**: All tests pass including all Sprint 5 integration tests.

**Commit**: `[Sprint 5 / Task 5.6] All sprints complete — epistemic Tier 2 fully integrated`

---

# IMPLEMENTATION_TASKS_ADDENDUM.md — Method Registry + Task-Ecological Validity

**Append these tasks to the existing IMPLEMENTATION_TASKS.md**
**These tasks form Sprint 4b (parallel with Sprint 4) and extend Sprint 5.**

---

## Sprint 4b: Method Registry and Task-Ecological Validity

### Task 4b.1: Create method_registry data structure

**Do**: Create `src/methods/registry.py` (or equivalent). Define:

```python
from dataclasses import dataclass, field
from typing import Optional, Dict, List
from enum import Enum

class MethodType(str, Enum):
    PHYSIOLOGICAL_BIOMARKER = "physiological_biomarker"
    NEURAL_IMAGING = "neural_imaging"
    BEHAVIORAL_MEASURE = "behavioral_measure"
    SELF_REPORT = "self_report"
    PRESENTATION_MODALITY = "presentation_modality"
    EXPERIMENTAL_DESIGN = "experimental_design"

class MovementCompatibility(str, Enum):
    YES = "yes"
    CONFOUNDED = "confounded"
    NO = "no"

class ProfileStatus(str, Enum):
    WELL_CHARACTERIZED = "well_characterized"
    PARTIALLY_CHARACTERIZED = "partially_characterized"
    UNCHARACTERIZED = "uncharacterized"

@dataclass
class MethodEntry:
    method_id: str
    method_type: MethodType
    construct_measured: str
    temporal_onset: Optional[str] = None
    temporal_peak: Optional[str] = None
    temporal_recovery: Optional[str] = None
    minimum_sampling_window: Optional[str] = None
    spatial_resolution: Optional[str] = None
    confounds: List[str] = field(default_factory=list)
    vr_specific_confounds: List[str] = field(default_factory=list)
    valence_sensitivity: bool = False
    movement_compatible: MovementCompatibility = MovementCompatibility.CONFOUNDED
    construct_validity_map: Dict[str, float] = field(default_factory=dict)
    hardware_variants: List[dict] = field(default_factory=list)
    first_encountered: Optional[str] = None
    profile_status: ProfileStatus = ProfileStatus.UNCHARACTERIZED
    evidence_count: int = 0
    last_updated: Optional[str] = None

class MethodRegistry:
    def __init__(self):
        self._entries: Dict[str, MethodEntry] = {}

    def add(self, entry: MethodEntry):
        self._entries[entry.method_id] = entry

    def get(self, method_id: str) -> Optional[MethodEntry]:
        return self._entries.get(method_id)

    def find_by_type(self, method_type: MethodType) -> List[MethodEntry]:
        return [e for e in self._entries.values() if e.method_type == method_type]

    def list_uncharacterized(self) -> List[MethodEntry]:
        return [e for e in self._entries.values()
                if e.profile_status == ProfileStatus.UNCHARACTERIZED]

    def update_evidence_count(self, method_id: str):
        if method_id in self._entries:
            self._entries[method_id].evidence_count += 1
```

**Test**: Create a MethodRegistry, add an entry, retrieve it, query by type.

**Commit**: `[Sprint 4b / Task 4b.1] Create method registry data structure`

### Task 4b.2: Seed registry with initial entries

**Do**: Create `src/methods/seed_data.py` with initial entries for at least
15 common CNFA instruments. Here are the first 5 as examples — create the
rest following the same pattern:

```python
SEED_ENTRIES = [
    MethodEntry(
        method_id="salivary_cortisol",
        method_type=MethodType.PHYSIOLOGICAL_BIOMARKER,
        construct_measured="HPA axis stress response",
        temporal_onset="15-20 min",
        temporal_peak="20-40 min",
        temporal_recovery="40-60 min",
        minimum_sampling_window="20 min post-stressor",
        confounds=["diurnal_curve", "caffeine", "oral_contraceptives",
                   "menstrual_phase", "exercise_within_2hr", "food_intake_30min",
                   "seasonal_variation", "medications_corticosteroids_SSRIs"],
        vr_specific_confounds=["headset_novelty_stress", "cybersickness"],
        valence_sensitivity=False,
        movement_compatible=MovementCompatibility.YES,
        construct_validity_map={
            "hpa_stress_reactivity": 0.95,
            "subjective_stress": 0.40,
            "autonomic_arousal": 0.20,
            "mood": 0.15
        },
        profile_status=ProfileStatus.WELL_CHARACTERIZED,
    ),
    MethodEntry(
        method_id="hrv_frequency_domain",
        method_type=MethodType.PHYSIOLOGICAL_BIOMARKER,
        construct_measured="Autonomic nervous system balance",
        temporal_onset="seconds",
        temporal_peak="seconds",
        temporal_recovery="minutes",
        minimum_sampling_window="5 min for frequency domain",
        confounds=["physical_activity", "respiratory_rate", "age",
                   "fitness_level", "body_position", "medication"],
        vr_specific_confounds=["cybersickness_elevates_sympathetic"],
        valence_sensitivity=False,  # partial via HF-HRV
        movement_compatible=MovementCompatibility.CONFOUNDED,
        construct_validity_map={
            "parasympathetic_activity": 0.85,
            "sympathovagal_balance": 0.50,  # LF/HF ratio unreliable
            "relaxation": 0.70,
            "stress": 0.60
        },
        profile_status=ProfileStatus.WELL_CHARACTERIZED,
    ),
    MethodEntry(
        method_id="eeg_frequency_bands",
        method_type=MethodType.NEURAL_IMAGING,
        construct_measured="Cortical oscillatory activity",
        temporal_onset="immediate",
        minimum_sampling_window="2 sec for spectral analysis",
        spatial_resolution="centimeters (volume conduction)",
        confounds=["movement_artifacts", "eye_blinks", "electrical_noise",
                   "scalp_thickness", "hair_density"],
        vr_specific_confounds=["hmd_pressure_artifacts", "hmd_electromagnetic_interference",
                               "electrode_coverage_blocked_by_hmd"],
        valence_sensitivity=True,  # via frontal asymmetry
        movement_compatible=MovementCompatibility.NO,
        construct_validity_map={
            "cortical_arousal": 0.80,
            "relaxation_alpha": 0.75,
            "cognitive_engagement_beta": 0.70,
            "approach_withdrawal_motivation": 0.65,
            "specific_brain_region_activation": 0.30  # poor spatial resolution
        },
        profile_status=ProfileStatus.WELL_CHARACTERIZED,
    ),
    MethodEntry(
        method_id="self_report_preference",
        method_type=MethodType.SELF_REPORT,
        construct_measured="Conscious evaluative judgment",
        temporal_onset="retrospective",
        confounds=["demand_characteristics", "social_desirability", "scale_anchoring",
                   "question_order", "mood_state", "fatigue"],
        vr_specific_confounds=["technology_novelty_bias"],
        valence_sensitivity=True,
        movement_compatible=MovementCompatibility.YES,
        construct_validity_map={
            "explicit_preference": 0.90,
            "actual_behavior": 0.50,
            "implicit_affect": 0.30,
            "physiological_response": 0.25
        },
        profile_status=ProfileStatus.WELL_CHARACTERIZED,
    ),
    MethodEntry(
        method_id="vr_hmd_room_scale",
        method_type=MethodType.PRESENTATION_MODALITY,
        construct_measured="Immersive visual environment with locomotion",
        confounds=["fov_restriction_110deg", "resolution_20ppd",
                   "haptic_absence", "thermal_absence", "olfactory_absence"],
        vr_specific_confounds=["vestibular_visual_conflict_reduced",
                               "tracking_boundary_artifacts"],
        movement_compatible=MovementCompatibility.YES,
        construct_validity_map={
            "visual_preference": 0.85,
            "wayfinding": 0.70,
            "stress_response": 0.65,
            "spatial_cognition": 0.70,
            "attention_restoration": 0.55,
            "material_preference": 0.20,
            "social_behavior": 0.35,
            "temporal_comprehension": 0.50
        },
        profile_status=ProfileStatus.WELL_CHARACTERIZED,
    ),
]
```

Create similar entries for: eda_scr, eda_scl, fmri_bold, fnirs,
eye_tracking, self_report_stai, self_report_panas, self_report_prs,
blood_pressure, photographs_2d, vr_hmd_stationary, vr_cave,
real_building_controlled.

**Test**: Load seed data into registry. Confirm 15+ entries. Query for all
PHYSIOLOGICAL_BIOMARKER entries — should return at least 5.

**Commit**: `[Sprint 4b / Task 4b.2] Seed method registry with initial entries`

### Task 4b.3: Add task-ecological validity enums and scoring

**Do**: Create `src/methods/task_ecology.py`:

```python
class TaskClass(str, Enum):
    EXPLICIT_EVALUATION = "explicit_evaluation"        # rate, judge, evaluate
    LAB_COGNITIVE_TASK = "lab_cognitive_task"           # Stroop, digit span
    SIMULATED_ECOLOGICAL = "simulated_ecological"      # VR wayfinding, TSST
    REAL_TASK_CONTROLLED = "real_task_controlled"       # real work, real navigation
    NATURAL_BEHAVIOR = "natural_behavior"              # POE, ESM, longitudinal

TASK_AUTHENTICITY_SCORES = {
    TaskClass.EXPLICIT_EVALUATION: 0.2,
    TaskClass.LAB_COGNITIVE_TASK: 0.4,
    TaskClass.SIMULATED_ECOLOGICAL: 0.6,
    TaskClass.REAL_TASK_CONTROLLED: 0.8,
    TaskClass.NATURAL_BEHAVIOR: 1.0,
}

class EffectPathway(str, Enum):
    """Per Canonical Decision 4: SUBPERSONAL / PERSONAL_EPISTEMIC / MIXED"""
    SUBPERSONAL = "subpersonal"               # direct physiological, no interpretation
    PERSONAL_EPISTEMIC = "personal_epistemic" # fully interpretation-mediated
    MIXED = "mixed"                           # both channels active

class ClaimType(str, Enum):
    EVALUATIVE_RESPONSE = "evaluative_response"   # Type A: "people prefer X"
    FUNCTIONAL_EFFECT = "functional_effect"        # Type B: "X reduces stress"

@dataclass
class StateCharacterization:
    affective_state: float = 0.0    # 0=not addressed, 0.3=mentioned, 0.7=measured, 1.0=controlled
    cognitive_load: float = 0.0
    goal_urgency: float = 0.0
    familiarity: float = 0.0
    physical_state: float = 0.0
    social_context: float = 0.0

    @property
    def score(self) -> float:
        vals = [self.affective_state, self.cognitive_load, self.goal_urgency,
                self.familiarity, self.physical_state, self.social_context]
        return sum(vals) / len(vals)

def compute_task_ecological_validity(
    task_class: TaskClass,
    state: StateCharacterization,
    attention_directed_to_features: bool = True,
    exposure_representative: bool = False,
    social_context_representative: bool = False,
    weights: dict = None
) -> float:
    if weights is None:
        weights = {"task": 0.30, "state": 0.20, "attention": 0.20,
                   "temporal": 0.15, "social": 0.15}

    task_score = TASK_AUTHENTICITY_SCORES[task_class]
    attention_score = 0.3 if attention_directed_to_features else 0.9
    temporal_score = 0.9 if exposure_representative else 0.3
    social_score = 0.9 if social_context_representative else 0.2

    return (weights["task"] * task_score +
            weights["state"] * state.score +
            weights["attention"] * attention_score +
            weights["temporal"] * temporal_score +
            weights["social"] * social_score)
```

**Test**:
```python
# Photo preference rating: low ecological validity
state_none = StateCharacterization()  # all zeros — nothing measured
score_low = compute_task_ecological_validity(
    TaskClass.EXPLICIT_EVALUATION, state_none, True, False, False)
assert score_low < 0.3

# Real hospital wayfinding with state measurement: high ecological validity
state_good = StateCharacterization(0.7, 0.7, 1.0, 1.0, 0.3, 0.7)
score_high = compute_task_ecological_validity(
    TaskClass.REAL_TASK_CONTROLLED, state_good, False, True, True)
assert score_high > 0.7
```

**Commit**: `[Sprint 4b / Task 4b.3] Add task-ecological validity scoring`

### Task 4b.4: Add claim type bifurcation to web

**Do**: Extend the claim node schema (from Sprint 1) with:

```python
claim_type: Optional[str] = None          # ClaimType value
effect_pathway: Optional[str] = None       # EffectPathway value
task_ecological_validity: Optional[float] = None  # [0, 1]
```

Add a new link type to the edge schema:

```python
GENERALIZABILITY_WARRANT = "generalizability_warrant"  # Type A → Type B
```

When the system creates a GENERALIZABILITY_WARRANT link, it should carry a
default weight of 0.5 (moderate confidence that evaluative findings generalize
to functional effects), adjustable based on converging field evidence.

**Test**: Create a Type A claim and a Type B claim about the same construct.
Connect them with a GENERALIZABILITY_WARRANT. Confirm link exists with
weight 0.5.

**Commit**: `[Sprint 4b / Task 4b.4] Add claim type bifurcation and generalizability warrants`

### Task 4b.5: Add method identification to extraction pipeline

**Do**: Add a preprocessing step in the extraction pipeline that runs before
claim extraction:

```python
def identify_methods(paper_text: str, registry: MethodRegistry) -> dict:
    """
    Scans the Methods section (or abstract) for instruments and protocols.

    Returns:
    {
        "instruments_found": [
            {"method_id": str, "confidence": float, "details": str}
        ],
        "presentation_modality": {"method_id": str, "confidence": float},
        "task_class": TaskClass,
        "state_measured": StateCharacterization,
        "uncharacterized_methods": [str],  # flagged for expert review
        "temporal_alignment_flags": [str],  # e.g., "cortisol sampled < 20 min"
    }
    """
```

**Method detection keywords** (expandable):
- Cortisol: "cortisol", "salivary", "HPA", "endocrine"
- HRV: "heart rate variability", "HRV", "RMSSD", "HF-HRV", "LF/HF"
- EDA: "skin conductance", "galvanic skin", "electrodermal", "GSR", "SCR", "SCL"
- EEG: "electroencephalog", "EEG", "alpha power", "theta", "ERP", "P300"
- fMRI: "fMRI", "BOLD", "functional magnetic"
- Eye tracking: "eye track", "fixation", "saccade", "pupil", "gaze"
- VR: "virtual reality", "VR", "HMD", "head-mounted", "CAVE", "immersive"
- Self-report: "questionnaire", "survey", "Likert", "PANAS", "STAI", "PSS"

For each match, look up in registry. If not found, add to uncharacterized list.

Check temporal alignment: if cortisol found AND sampling interval < 20 min,
flag "cortisol_temporal_misalignment".

**Test**: Run on a synthetic methods section mentioning cortisol and VR.
Confirm both are identified and matched to registry entries.

**Commit**: `[Sprint 4b / Task 4b.5] Add method identification to extraction pipeline`

### Task 4b.6: Compute per-claim validity scores

**Do**: After method identification and claim extraction, compute three
validity scores for each claim:

```python
def compute_claim_validity(
    claim,
    methods_info: dict,
    registry: MethodRegistry
) -> dict:
    """
    Returns:
    {
        "presentation_validity": float,    # [0, 1]
        "measurement_validity": float,     # [0, 1]
        "task_ecological_validity": float,  # [0, 1]
        "composite_validity": float,       # weighted combination
        "auto_challenges": [str],          # automatically generated challenges
    }
    """
```

The auto_challenges should include any of:
- "cortisol_temporal_misalignment" if cortisol sampled too early
- "construct_presentation_mismatch" if the construct depends on channels the
  presentation strips (look up construct_validity_map in registry)
- "vr_confound_uncontrolled" if VR used but cybersickness not measured
- "single_modality" if only one measurement modality used
- "exposure_duration_inadequate" if exposure < minimum for construct
- "attention_directed" if task is EXPLICIT_EVALUATION and claim is about
  implicit effects

**Test**: A claim about wayfinding based on photograph ratings should get
low presentation_validity and a "construct_presentation_mismatch" challenge.
A claim about cortisol from Fich et al. should get high scores across the board.

**Commit**: `[Sprint 4b / Task 4b.6] Compute per-claim validity scores with auto-challenges`

### Task 4b.7: Full test suite

**Do**: `pytest tests/ -v`

**Test**: No regressions. All Sprint 4b tests pass.

**Commit**: `[Sprint 4b / Task 4b.7] Sprint 4b complete — method registry and task-ecology verified`

---

## Sprint 5 Updates: Additional Integration Tests

### Task 5.6b: Validate claim type bifurcation

**Do**: In the Ulrich test corpus, include:
- A Type A claim: "Participants rated nature-view rooms as more pleasant" (from photo study)
- A Type B claim: "Patients in nature-view rooms recovered faster" (from Ulrich 1984)

Assert: Both claims exist in the web. A GENERALIZABILITY_WARRANT connects them.
The Type A claim has higher task_ecological_validity (it's studying what photos
actually measure: preference). The Type B claim from Ulrich 1984 has high
task_ecological_validity (real patients, real hospital, real recovery outcome).

**Test**: Link exists. Claim types are correct.

**Commit**: `[Sprint 5 / Task 5.6b] Validate claim type bifurcation`

### Task 5.7: Validate auto-challenge generation

**Do**: Include in the test corpus a synthetic claim about "wayfinding efficiency"
based on a photograph-rating study with self-report-only measurement.

Assert: Auto-challenges generated include:
- "construct_presentation_mismatch" (wayfinding from photos)
- "single_modality" (self-report only)
- "attention_directed" (evaluation task for functional claim)

**Test**: All three challenges present.

**Commit**: `[Sprint 5 / Task 5.7] Validate auto-challenge generation`

### Task 5.8: Validate method registry lookup and flagging

**Do**: Include a claim based on a study using "salivary alpha-amylase" (a
biomarker not in the seed registry).

Assert: The method is flagged as UNCHARACTERIZED and appears in the
registry's uncharacterized queue.

**Test**: Uncharacterized flag is set. Method appears in `registry.list_uncharacterized()`.

**Commit**: `[Sprint 5 / Task 5.8] Validate method registry uncharacterized flagging`

---

## Updated Sprint Summary

| Sprint | Focus | Duration | Depends On | Key Deliverable |
|--------|-------|----------|------------|-----------------|
| 1 | Schema extensions, template scaffolds | 2 weeks | — | Extended schema + 4 templates |
| 2 | BN nodes, edges, 3-pathway model | 2 weeks | Sprint 1 | Epistemic BN subgraph |
| 3 | Reflexive monitoring algorithms | 2–3 weeks | Sprint 2 | 4 monitoring tools |
| 4 | Extraction pipeline extensions | 2 weeks | Sprint 1 | Extended extractor |
| **4b** | **Method registry + task-ecological validity** | **2 weeks** | **Sprint 1** | **Method registry + validity scoring** |
| 5 | Integration testing, CNFA validation | 2–3 weeks | Sprints 1–4b | Validated system |

**Updated total: 12–14 weeks**
**Sprint 4b runs in parallel with Sprints 2–4.**
