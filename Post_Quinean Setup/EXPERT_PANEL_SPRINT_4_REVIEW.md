# Expert Panel Review Request: Sprint 4 - Outcome Taxonomy Extensions

**Date**: 2026-01-18
**Sprint**: 4 (Outcome Taxonomy Extensions)
**Status**: Implementation Complete, Awaiting Expert Review
**Author**: Claude Code Implementation

---

## Executive Summary

Sprint 4 extends the outcome taxonomy system to support the Quinean Web of Belief integration. The implementation adds:

1. **Theory-Outcome Mappings**: Bidirectional mappings between theories (ART, SRT, Biophilia) and outcome domains
2. **Epistemic Level Assignment**: Default epistemic levels for outcomes based on abstraction
3. **CNFA Extensions**: New architectural perception outcomes (arch.spatial, arch.aesthetic, etc.)
4. **Stub Outcome Management**: Unresolved outcomes become stubs with domain inference
5. **Bridge Candidate Suggestion**: Cross-domain relationships for bridge warrant generation

**All 26 tests pass.**

---

## Background for Expert Panel

### Current System Context

Article Eater extracts evidence-backed rules from scientific articles. The **Outcome Taxonomy** defines a controlled vocabulary for research outcomes (e.g., "sustained attention" → `cog.attention.sustained`).

The **Quinean Web of Belief** (Sprint 1-3) represents beliefs with:
- Epistemic levels (THEORETICAL → INTERMEDIATE → EMPIRICAL → OBSERVATIONAL)
- Theory attachments (beliefs can belong to ART, SRT, Biophilia, etc.)
- Credence values with uncertainty
- Constraints between beliefs (SUPPORTS, CONTRADICTS, BRIDGES)

Sprint 4 connects these systems by adding epistemic metadata to outcomes.

### Key Files

| File | Purpose |
|------|---------|
| `src/services/outcome_taxonomy.py` | Extended taxonomy implementation |
| `contracts/ae_af/schemas/ae.extended_outcome_lookup.v1.schema.json` | Schema definition |
| `tests/test_outcome_taxonomy.py` | 26 comprehensive tests |
| `contracts/vocab/outcome_lookup.json` | Base taxonomy (unmodified) |

---

## Decisions Requiring Expert Review

### Decision 4.1: Theory-Outcome Relevance Scores

**Implementation**: Numeric relevance scores (0-1) map outcomes to theories.

```python
THEORY_OUTCOME_RELEVANCE = {
    "ART": {
        "cog.attention.sustained": 1.0,
        "cog.attention.selective": 0.9,
        "cog.memory.working": 0.8,
        "physio.fatigue": 0.8,
        ...
    },
    "SRT": {
        "affect.stress": 1.0,
        "affect.anxiety": 0.9,
        "physio": 0.9,
        ...
    }
}
```

**Questions for Expert Panel**:
1. Are the relevance scores reasonable based on the literature?
2. Should scores be derived empirically (from corpus analysis) rather than expert-assigned?
3. Is 0.4 a reasonable threshold for theory attachment (currently used in Sprint 1)?

---

### Decision 4.2: Epistemic Level Defaults

**Implementation**: Outcomes have default epistemic levels based on abstraction.

```python
OUTCOME_EPISTEMIC_LEVELS = {
    "cog": EpistemicLevel.INTERMEDIATE,      # Abstract domain
    "cog.attention": EpistemicLevel.INTERMEDIATE,
    "cog.attention.sustained": EpistemicLevel.EMPIRICAL,  # Specific measure
    "physio.alertness": EpistemicLevel.OBSERVATIONAL,     # Direct observation
    "affect.mood": EpistemicLevel.INTERMEDIATE,           # Construct
    "affect.mood.positive": EpistemicLevel.EMPIRICAL,     # Measured state
}
```

**Rationale**:
- OBSERVATIONAL: Direct physiological measurements (heart rate, cortisol)
- EMPIRICAL: Validated psychological measures (attention tasks, stress scales)
- INTERMEDIATE: Higher-order constructs (mood, cognitive performance)
- THEORETICAL: Core theoretical commitments (not assigned to outcomes)

**Questions for Expert Panel**:
1. Is this hierarchy philosophically defensible?
2. Should epistemic level be contextual (depending on how outcome is measured)?
3. Are physiological measures truly "more observational" than self-report?

---

### Decision 4.3: CNFA Domain Extensions

**Implementation**: Added `arch` domain for architectural perception outcomes.

```python
CNFA_OUTCOME_EXTENSIONS = {
    "arch": {"name": "Architectural", "domain": "arch"},
    "arch.spatial": {"name": "Spatial Perception", ...},
    "arch.spatial.openness": {"name": "Perceived Openness", ...},
    "arch.spatial.prospect_refuge": {"name": "Prospect-Refuge Balance", ...},
    "arch.aesthetic": {"name": "Aesthetic Perception", ...},
    "arch.aesthetic.beauty": {"name": "Perceived Beauty", ...},
    "arch.aesthetic.complexity": {"name": "Visual Complexity", ...},
    "arch.environ": {"name": "Environmental Perception", ...},
    "arch.environ.biophilic": {"name": "Biophilic Elements", ...},
    "arch.affect": {"name": "Spatial Affect", ...},
}
```

**Questions for Expert Panel**:
1. Is the proposed hierarchy appropriate for CNFA?
2. Are there important architectural outcomes missing?
3. Should "prospect-refuge" be under spatial or affect?
4. How should geometric outcomes (angular vs. curved) be categorized?

---

### Decision 4.4: Stub Outcome Management

**Implementation**: Unresolved outcome terms create stub outcomes with inferred domains.

```python
def resolve_or_stub(self, raw_term: str, paper_id: str) -> ExtendedOutcome:
    resolved = self.resolve(raw_term)
    if resolved:
        return resolved

    # Create stub with inferred domain
    stub_id = f"STUB:{raw_term.lower().replace(' ', '_')}"
    domain = self._infer_domain(raw_term)  # Keyword-based inference

    stub = ExtendedOutcome(
        outcome_id=stub_id,
        is_stub=True,
        stub_reason=f"Unresolved from paper {paper_id}"
    )
    return stub
```

**Questions for Expert Panel**:
1. Should stubs immediately create beliefs in the web, or queue for review?
2. How should stub credence be initialized (currently default)?
3. What happens when a stub is later resolved (merge or replace)?

---

### Decision 4.5: Bridge Candidate Identification

**Implementation**: Architectural outcomes automatically identify potential bridge candidates.

```python
arch_to_other_mappings = {
    "arch.affect.calming": ["affect.mood.positive", "affect.stress"],
    "arch.environ.biophilic": ["affect.stress", "health.wellbeing", "cog.attention.sustained"],
    "arch.aesthetic.naturalness": ["affect.mood.positive", "health.wellbeing"],
}
```

**Questions for Expert Panel**:
1. Should bridge candidates be auto-generated or manually curated?
2. What determines a "reasonable" cross-domain bridge?
3. How should bridge type (mechanism, functional, analogical) be inferred from outcomes?

---

## Implementation Details

### ExtendedOutcome Data Class

```python
@dataclass
class ExtendedOutcome:
    outcome_id: str          # e.g., "cog.attention.sustained"
    name: str                # e.g., "Sustained Attention"
    domain: str              # e.g., "cog"
    parent: Optional[str]    # e.g., "cog.attention"

    # Extensions
    epistemic_level: EpistemicLevel = EpistemicLevel.EMPIRICAL
    theory_relevance: Dict[str, float] = {}  # theory_id → score
    is_stub: bool = False
    stub_reason: Optional[str] = None
    bridge_candidates: List[str] = []  # Other outcome_ids
```

### Key Functions

| Function | Purpose |
|----------|---------|
| `resolve(raw_term)` | Resolve term to ExtendedOutcome |
| `resolve_or_stub(raw_term, paper_id)` | Resolve or create stub |
| `get_theories_for_outcome(outcome_id)` | Get relevant theories |
| `get_outcomes_for_theory(theory_id)` | Get relevant outcomes |
| `suggest_bridges_for_outcome(outcome_id)` | Get bridge suggestions |
| `infer_theory_from_outcomes(outcomes)` | Infer most likely theory |

---

## Test Coverage

All 26 tests pass:

- **Theory-Outcome Mapping**: 4 tests
- **Epistemic Level Assignment**: 4 tests
- **CNFA Extensions**: 4 tests
- **Stub Management**: 4 tests
- **Bridge Suggestion**: 3 tests
- **Export/Import**: 4 tests
- **Theory Inference**: 2 tests
- **Belief Metadata**: 1 test

---

## Integration Points

### With Sprint 1 (extraction_to_web.py)

The `infer_theory_from_outcomes()` function can replace or augment the existing theory inference:

```python
# Current approach (Sprint 1)
theory_inferences = infer_theory_relevance(claim, outcome_lookup)

# New approach (Sprint 4)
from src.services.outcome_taxonomy import ExtendedOutcomeTaxonomy, infer_theory_from_outcomes
taxonomy = ExtendedOutcomeTaxonomy()
outcomes = [taxonomy.resolve_or_stub(o["id"]) for o in claim["constructs"]["outcomes"]]
primary_theory, scores = infer_theory_from_outcomes(outcomes)
```

### With Sprint 3 (bridge_warrants.py)

Bridge suggestions can inform automatic bridge creation:

```python
from src.services.outcome_taxonomy import ExtendedOutcomeTaxonomy
from src.services.bridge_warrants import create_bridge, BridgeType

taxonomy = ExtendedOutcomeTaxonomy()
suggestions = taxonomy.suggest_bridges_for_outcome("arch.environ.biophilic")

for suggestion in suggestions:
    bridge = create_bridge(
        source_domain=suggestion["source_domain"],
        target_domain=suggestion["target_domain"],
        bridge_type=BridgeType(suggestion["bridge_type"].upper()),
        warrant_statement=f"Evidence from {suggestion['source_outcome']} may transfer to {suggestion['target_outcome']}"
    )
```

---

## Requested Expert Panel Composition

For Sprint 4, we request input from:

1. **Dr. Judea Pearl** — Theory-outcome causal relationships, inference validity
2. **Dr. Nancy Cartwright** — Bridge warrant connections, domain transfer
3. **Dr. Rachel Kaplan** — Environmental psychology outcomes, CNFA extensions
4. **Dr. Marcia Bates** — Information organization, taxonomy structure
5. **Dr. Herbert Simon** — Bounded rationality in outcome categorization

---

## Questions Summary

1. Are theory-outcome relevance scores reasonable?
2. Is the epistemic level hierarchy philosophically defensible?
3. Is the CNFA outcome hierarchy appropriate?
4. How should stub outcomes be handled?
5. Should bridge candidates be auto-generated or curated?

---

**End of Sprint 4 Expert Panel Request**
