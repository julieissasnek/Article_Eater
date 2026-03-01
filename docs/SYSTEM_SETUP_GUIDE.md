# System Setup Guide: 12-Phase CMR Initialization

**File**: `src/services/system_setup.py`
**Status**: Production-ready
**Created**: 2026-02-25
**Lines of Code**: 1,145

## Overview

The `SystemSetup` class implements a 12-phase bulk initialization procedure for the Compositional Mechanistic Reasoning (CMR) system. This is **architecturally distinct** from the per-paper `integrate_paper()` pipeline and creates the OPERATIONAL system from scratch.

## Key Design Principles

### 1. Dijkstra State Invariant
The system progresses through well-defined states:
- `UNINITIALIZED` → `INITIALIZING` → `OPERATIONAL`
- Critical phases (1-5) must succeed; non-critical phases (6-12) log errors but continue
- This prevents the system from entering an ERROR state due to optional features

### 2. Quine Temporal Ordering (Phase 2)
Papers are loaded in chronological order (oldest first) to respect:
- W.V.O. Quine's principle of minimal revision
- Earlier theory commitments are more entrenched
- Later empirical findings adjust a stable theoretical backdrop

### 3. Spohn Convergence (Phase 5)
Global reflective equilibrium replaces per-paper 5-iteration cycles:
- Iterative coherence seeking until `coherence_delta < 0.001`
- Maximum 100 iterations (safety valve)
- Captures inter-theoretical dependencies that per-paper integration misses

### 4. Haack Foundherentism (Phase 3)
Beliefs require **both** coherence AND grounding:
- `Directness` mapping ensures beliefs connect to experience
- `grounding_score` weighted by sample size and study design
- Prevents dangerous COHERENT_ONLY states (per 2026-01-18 panel resolution)

### 5. Pearl Causal Structure (Phases 6-7)
Bayesian Network DAG construction and parameterization:
- Edges derived from constraint polarity (SUPPORTS → unidirectional, CONTRADICTS → bidirectional)
- Priors: `edge_prior_p = 0.3 + 0.7 × credence × quality_weight`
- O-4 coupling: web constraints → BN parameters (unidirectional flow)

## Phase-by-Phase Guide

### Phase 0: Metadata Enrichment (Optional)
```python
_phase_0_enrich_metadata() -> Dict[str, Any]
```

**Purpose**: Fetch publication metadata from SemanticScholar API.

**Input**:
- Papers from `data/extractions/*.json` without `paper_metadata.enriched = True`

**Output**:
- Updated extraction JSONs with publication year, author affiliations, citation count
- Sorted by publication year for Phase 2

**Graceful Degradation**: If SemanticScholar module unavailable, logs warning and continues.

**Decision Point (D0)**:
- Should metadata enrichment be mandatory or optional?
- Current: Optional (Phase 0 failure doesn't abort setup)

---

### Phase 1: Scaffold (Critical)
```python
_phase_1_scaffold() -> Dict[str, Any]
```

**Purpose**: Initialize core epistemological structures.

**Actions**:
1. Create `WebOfBelief` via `create_neuroarchitecture_web()`
2. Load theory definitions from `data/theories/*.json`
3. Load template definitions from `data/templates/*.json`
4. Initialize `WebPersistenceService` for database operations

**Output**:
- Populated `self.web` with neuroarchitecture beliefs
- `self.persistence` service ready
- Theory/template registries loaded

**Critical Invariant**: Must succeed; provides foundation for all downstream phases.

---

### Phase 2: Bulk Load (Critical)
```python
_phase_2_bulk_load() -> Dict[str, Any]
```

**Purpose**: Load all extraction JSONs in temporal order (Quine principle).

**Actions**:
1. Find all `data/extractions/*.json` files
2. Parse JSON for `findings` array
3. Sort by `paper_metadata.publication_year` (ascending)
4. Track year distribution

**Output**:
- Stored in `self._papers` (list of paper dicts, sorted by year)
- Year distribution histogram for audit

**Decision Point (D1)**:
- Is temporal ordering truly necessary for coherence-seeking?
- Alternative: Random order (tests whether Quine principle matters)
- Current: Enforce chronological order (most conservative)

**Example Output**:
```
Found 247 papers:
  Year 1950-1959: 3 papers
  Year 1960-1969: 12 papers
  Year 1970-1979: 45 papers
  Year 1980-2025: 187 papers
```

---

### Phase 3: Batch Provenance (Critical)
```python
_phase_3_batch_provenance() -> Dict[str, Any]
```

**Purpose**: Construct Haack-style grounding evidence for each finding (Foundherentism).

**Actions**:
1. For each paper's findings:
   - Create `Source` object (DOI, title, authors)
   - Map `claim_type` → `StudyType` (EXPERIMENTAL, OBSERVATIONAL, META_ANALYSIS, THEORETICAL)
   - Map evidence metadata → `Directness` (DIRECT, ONE_HOP, MULTI_HOP, THEORETICAL)
   - Compute `grounding_score` based on directness and sample size
   - Construct `Provenance` object

**Mapping Tables**:

| Claim Type | Study Type |
|------------|-----------|
| experimental, experiment | EXPERIMENTAL |
| meta, review | META_ANALYSIS |
| observational | OBSERVATIONAL |
| theoretical | THEORETICAL |
| *default* | OBSERVATIONAL |

| Evidence Type | Directness |
|---------------|-----------|
| direct, observational | DIRECT |
| experimental, measured | ONE_HOP |
| theoretical, inferred | MULTI_HOP |
| *default* | ONE_HOP |

**Grounding Score Formula**:
```
base_score = {DIRECT: 0.9, ONE_HOP: 0.7, MULTI_HOP: 0.4, THEORETICAL: 0.1}[directness]
if sample_size > 100: base_score += 0.1
elif sample_size > 30: base_score += 0.05
final = min(base_score, 1.0)
```

**Output**:
- Provenances stored as attributes on beliefs (in Phase 4)
- Count: number of provenances created
- Embarrassingly parallel (can be sharded per-paper)

**Decision Point (D2)**:
- Should grounding_score decay by study age?
- Current: No temporal decay (all evidence equally grounded)

---

### Phase 4: Web Insertion (Critical)
```python
_phase_4_web_insertion() -> Dict[str, Any]
```

**Purpose**: Insert all extracted claims and rules into the `WebOfBelief`.

**Actions**:
1. For each paper (in order):
   - Call `integrate_extraction(web, extraction_data, seek_equilibrium=False)`
   - Defer coherence-seeking to Phase 5 (GLOBAL phase)
   - Accumulate integration reports

2. Track:
   - Papers successfully integrated
   - Claims parsed (successes + failures)
   - Rules created
   - Theory attachments
   - Stub findings (unattached to theory)

**Output**:
- `self.web` populated with beliefs and constraints
- Integration reports logged
- Ready for Phase 5

**Key Difference from Per-Paper Pipeline**:
- Per-paper `integrate_paper()`: runs 5 local equilibrium iterations
- Phase 4+5: defer ALL equilibrium to Phase 5 (global)
- Allows inter-paper constraint resolution

---

### Phase 5: Global Reflective Equilibrium (Critical) — THE KEY PHASE
```python
_phase_5_reflective_equilibrium() -> Dict[str, Any]
```

**Purpose**: Seek global coherence across all beliefs (Spohn + Rawls).

**Algorithm**:
```python
prev_coherence = 0.0
for iteration in range(max_equilibrium_iterations):
    web.seek_equilibrium(num_iterations=1)
    current_coherence = web.compute_coherence()
    coherence_delta = abs(current_coherence - prev_coherence)

    if coherence_delta < convergence_threshold:
        return CONVERGED at iteration

    prev_coherence = current_coherence

# If loop completes without convergence, log warning but don't fail
return INCOMPLETE at iteration = max_equilibrium_iterations
```

**Configuration** (constructor parameters):
- `max_equilibrium_iterations`: 100 (safety valve)
- `equilibrium_convergence_threshold`: 0.001 (tight convergence)

**Output**:
- Coherence history: list of credences at each iteration
- Final coherence value
- Number of iterations needed
- Boolean `convergence_achieved`

**Log Output** (every 10 iterations + convergence):
```
Iteration 0: coherence=0.5321, delta=0.5321
Iteration 10: coherence=0.6847, delta=0.0145
Iteration 20: coherence=0.7102, delta=0.0062
...
Iteration 47: coherence=0.7234, delta=0.0008
✓ CONVERGENCE ACHIEVED at iteration 47
```

**Decision Point (D3)** (CRITICAL FOR PANEL REVIEW):
- Is `convergence_threshold = 0.001` too tight?
  - Tighter → higher coherence but more iterations
  - Looser → faster convergence but lower final coherence
- Empirical question: What delta do real systems typically achieve?
- Recommendation: Run benchmark suite to measure convergence rates

---

### Phase 6: BN Structure (Non-Critical)
```python
_phase_6_bn_structure() -> Dict[str, Any]
```

**Purpose**: Derive Bayesian Network DAG structure from web constraints.

**Actions**:
1. Identify empirical nodes: beliefs with level ∈ {EMPIRICAL, OBSERVATIONAL}
2. For each constraint:
   - If both endpoints are empirical: create BN edge
   - Directionality:
     - CONTRADICTS → bidirectional edge
     - SUPPORTS → unidirectional (source → target)
   - Store constraint strength as edge weight

**Output**:
- Edge list: `[{source, target, direction, constraint_type, strength}, ...]`
- Stored in `self._bn_edges`

**Decision Point (D4)**:
- Should directionality be inferred automatically, or hand-curated per constraint?
- Current: Automatic (CONTRADICTS → bidirectional, SUPPORTS → unidirectional)

---

### Phase 7: BN Parameterization (Non-Critical)
```python
_phase_7_bn_parameterize() -> Dict[str, Any]
```

**Purpose**: Assign conditional probability parameters to BN edges.

**Algorithm**:
For each edge:
```python
edge_prior_p = 0.3 + 0.7 × source_credence × source_quality_weight
```

Where:
- `source_credence`: belief credence value (0.0 - 1.0)
- `source_quality_weight`: entrenchment (epistemic centrality)
- `0.3`: base prior (before observing source)
- `0.7 × credence × quality`: observed evidence strength

**Output**:
- Each edge augmented with `prior_p` parameter
- Average prior_p across all edges

**Decision Point (D5)**:
- Should edges inherit theory entrenchment (not just source credence)?
- Current: Uses source entrenchment as quality proxy
- Alternative: Use constraint strength as weight

---

### Phase 8: Coherence Baseline (Non-Critical)
```python
_phase_8_coherence_baseline() -> Dict[str, Any]
```

**Purpose**: Create OVERSEER statistical reference baseline.

**Actions**:
1. Create `CoherenceManager()` instance
2. Call `build_from_web(web)`
3. Compute global coherence
4. Compute per-theory coherence (mean credence per theory)

**Output**:
- Global coherence value
- Per-theory coherence scores (dict)
- Stored for future OVERSEER health monitoring

**Use Case**: OVERSEER module uses these as reference to detect drift.

---

### Phase 9: QA Cache (Non-Critical)
```python
_phase_9_qa_cache() -> Dict[str, Any]
```

**Purpose**: Pre-compute QA cache data for all beliefs.

**Actions**:
- For each belief: generate QA cache (single pass, not incremental)
- *Implementation detail: placeholder in current version*

**Output**:
- Count of QA caches generated

---

### Phase 10: Social Epistemology (Non-Critical)
```python
_phase_10_social_epistemology() -> Dict[str, Any]
```

**Purpose**: Initialize community registry and assign beliefs to epistemic communities.

**Actions**:
1. Create `CommunityRegistry()`
2. Generate seed communities via `create_cnfa_seed_communities()`
3. For each belief: identify community via `identify_community_for_belief()`
4. Create `BeliefProvenance` (tracks contestation, community affiliation)

**Output**:
- Community count
- Beliefs assigned to communities

**Decision Point (D6)**:
- Community detection strategy: co-authorship network vs. citation network?
- Current: Uses provided `identify_community_for_belief()` function

---

### Phase 11: VOI Gaps (Non-Critical)
```python
_phase_11_voi_gaps() -> Dict[str, Any]
```

**Purpose**: Initialize discovery funnel with value-of-information gaps.

**Actions**:
1. Create `DiscoveryFunnelService()`
2. Identify gaps: beliefs with level == STUB
3. Seed with initial VOI estimates

**Output**:
- Gap count
- Ready for discovery module to prioritize research

---

### Phase 12: OVERSEER Baseline (Non-Critical)
```python
_phase_12_overseer_baseline() -> Dict[str, Any]
```

**Purpose**: Create baseline health snapshot for OVERSEER monitoring.

**Actions**:
1. Compute baseline metrics:
   - `n_beliefs`: total beliefs in web
   - `n_constraints`: total constraints
   - `avg_credence`: mean credence across beliefs
   - `final_coherence`: from Phase 5

2. Set system state: `OPERATIONAL`

**Output**:
- Baseline snapshot (JSON serializable)
- System state = OPERATIONAL

---

## Usage Example

```python
from src.services.system_setup import SystemSetup, SystemState

# Initialize setup service
setup = SystemSetup(
    db_path="data/articles.db",
    extractions_dir="data/extractions",
    theories_dir="data/theories",
    templates_dir="data/templates",
    output_dir="data/setup_output",
    max_equilibrium_iterations=100,
    equilibrium_convergence_threshold=0.001,
)

# Execute 12-phase setup
report = setup.setup()

# Inspect report
print(f"State: {report.state.value}")
print(f"Papers: {report.n_papers_loaded}")
print(f"Beliefs: {report.n_beliefs_created}")
print(f"Coherence: {report.final_coherence:.4f}")
print(f"Converged: {report.convergence_achieved}")

# Access detailed phase results
for phase_name, phase_result in report.phases.items():
    print(f"{phase_name}: {phase_result.get('success', False)}")

# Save report
import json
with open("setup_report.json", "w") as f:
    json.dump(report.to_dict(), f, indent=2)
```

## Error Handling & Resilience

### Critical Phase Failure (Phases 1-5)
If any critical phase fails:
- System state → ERROR
- Setup aborted immediately
- Exception raised to caller

### Non-Critical Phase Failure (Phases 6-12)
If any non-critical phase fails:
- Error logged to `report.warnings`
- Setup continues to next phase
- Final state = OPERATIONAL (if critical phases succeeded)

### Optional Import Failures
For optional modules (provenance, social epistemology, discovery funnel):
- Try/except with graceful degradation
- Phase skipped with warning logged
- Setup continues normally

## Testing & Validation

### Unit Tests (Recommended)
```python
def test_phase_1_scaffold():
    setup = SystemSetup()
    result = setup._phase_1_scaffold()
    assert result["success"] == True
    assert setup.web is not None
    assert setup.persistence is not None

def test_phase_5_convergence():
    setup = SystemSetup(equilibrium_convergence_threshold=0.01)
    result = setup._phase_5_reflective_equilibrium()
    assert result["convergence_achieved"] == True
    assert result["iterations"] < 100
```

### Integration Tests (Recommended)
```python
def test_full_setup():
    setup = SystemSetup()
    report = setup.setup()
    assert report.state == SystemState.OPERATIONAL
    assert report.n_beliefs_created > 0
    assert report.convergence_achieved == True
```

### Benchmarks (Recommended)
- Time per phase (wall-clock and CPU time)
- Coherence convergence rate vs. corpus size
- Memory usage during Phase 5 iterations

## Performance Considerations

### Bottlenecks
1. **Phase 5** (Global Reflective Equilibrium): O(B²) per iteration where B = number of beliefs
2. **Phase 4** (Web Insertion): O(B × C) where C = number of constraints per belief

### Optimization Strategies
1. Use `CoherenceManager` (Phase 8) for O(n log n) coherence computation
2. Parallelize Phase 3 (Batch Provenance) per-paper
3. Batch Phase 9 (QA Cache) generation
4. Consider checkpoints between phases for long-running setups

### Memory Usage
- Phase 4: O(B + C) for web structure
- Phase 5: Additional O(B) for coherence history
- Phase 8: O(B + C) for coherence manager network

## Configuration

### Environment Variables
```bash
# Phase 0: SemanticScholar enrichment
export AE_SEMANTIC_SCHOLAR_ENABLED=true
export AE_SEMANTIC_SCHOLAR_API_KEY="your-key"

# Phase 2: Temporal ordering
export AE_QUINE_TEMPORAL_ORDERING=true  # Always True

# Phase 5: Convergence parameters
export AE_EQUILIBRIUM_MAX_ITERATIONS=100
export AE_EQUILIBRIUM_CONVERGENCE_THRESHOLD=0.001
```

## Expert Panel Decision Points

These are flagged for review:

| ID | Question | Current Decision | Rationale | Risk |
|----|----------|-----------------|-----------|------|
| D1 | Is Quine temporal ordering necessary? | Yes | Minimal revision principle | Low |
| D2 | Should grounding decay by age? | No | All evidence equally grounded | Medium |
| D3 | Is convergence threshold 0.001 tight enough? | Yes | High-precision coherence | High |
| D4 | Infer edge direction automatically? | Yes | CONTRADICTS → bidirectional | Low |
| D5 | Use entrenchment in edge parameterization? | Yes | Quality-weighted priors | Medium |
| D6 | Community detection method? | Co-authorship | Stable over time | Medium |

## References

- **Quine, W.V.O.** (1951). Two Dogmas of Empiricism. *Philosophical Review*, 60(1), 20-43.
- **Rawls, J.** (1971). A Theory of Justice. Harvard University Press.
- **Haack, S.** (1993). Evidence and Inquiry. Blackwell.
- **Spohn, W.** (2012). The Laws of Belief. Oxford University Press.
- **Pearl, J.** (2000). Causality. Oxford University Press.
- **Thagard, P.** (1989). Explanatory Coherence. *Behavioral and Brain Sciences*, 12(3), 435-467.
