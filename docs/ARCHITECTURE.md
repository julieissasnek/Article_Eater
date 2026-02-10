# Article Eater - Integrated Architecture

*Last updated: 2026-02-10 (Sprint ECB-3)*

## Module Overview

The system has four architectural layers:

1. **Extraction Layer** — PDF → structured claims
2. **Epistemic Layer** — Quinean coherentist belief management
3. **Causal Layer** — Pearlian causal inference via epistemic-causal bridge
4. **Output Layer** — Queries, reports, and research recommendations

### Core Epistemic Architecture (Quinean Coherentist)

| Module | Purpose | Key Features |
|--------|---------|--------------|
| `web_of_belief.py` | Core epistemic state | Joint probability over theory-worlds, stubs, reflective equilibrium |
| `refined_epistemic.py` | Refined epistemology | Semantic status (Boghossian), typed dependencies (Glymour), Bovens-Hartmann coherence |
| `abstraction_levels.py` | Theory nesting | Theories grounded in deeper theories, criterial rules, model zoom |
| `evidence_integration.py` | Integration layer | PDF extraction → epistemic state updates |
| `dual_epistemology.py` | Comparative analysis | Foundationalist vs coherentist contrast |

### Epistemic-Causal Bridge (Sprint 1.5 + ECB Repair)

| Module | Purpose | Key Features |
|--------|---------|--------------|
| `epistemic_causal_bridge.py` | Quinean→Pearlian bridge | Multi-theory causal models, counterfactuals, van Fraassen contrast classes |

**Key Classes:**
- `EpistemicCausalBridge` — Main orchestration class
- `ContrastClass` — Van Fraassen contrast specification
- `PopulationContext` — Baseline-dependent meaning
- `MultiTheoryModel` — Per-theory structural equations
- `QuineanCounterfactualResult` — Counterfactual with epistemic annotations

**Sprint ECB-3 Features (2026-02-10):**

| Feature | Description | Panel Source |
|---------|-------------|--------------|
| Contrast Transfer Rules | DIRECT, BASELINE_SHIFT, POPULATION_SHIFT, MEANING_SHIFT classification | van Fraassen, Simon |
| Undefined Results | Returns `is_defined=False` when contrast classes don't transfer | van Fraassen |
| Gap Identification | Detects epistemic gaps, routes to VOI search | Simon |
| Security Weight | Haack's foundherentist grounding measure | Haack |
| Configurable Thresholds | `AE_CONTRAST_THRESHOLD_*` environment variables | Simon |

### Extraction Pipeline

| Module | Purpose | Method |
|--------|---------|--------|
| `pdf_extraction.py` | Pattern-based extraction | Regex patterns for theories, effect sizes, temporal params |
| `theory_extraction.py` (Claude Code) | LLM-based extraction | Prompts for deep semantic analysis of theory structure |
| `theory_testing.py` (Claude Code) | Theory-paper linking | Identifies how papers engage with theories |

## Integration Points

```
                    ┌─────────────────────────────┐
                    │        PDF Corpus           │
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────▼───────────────┐
                    │     EXTRACTION LAYER        │
                    │  ┌─────────┐ ┌───────────┐  │
                    │  │ Pattern │ │ LLM-based │  │
                    │  │ (fast)  │ │ (deep)    │  │
                    │  └────┬────┘ └─────┬─────┘  │
                    └───────┼────────────┼────────┘
                            │            │
                            ▼            ▼
                    ┌───────────────────────────┐
                    │    EPISTEMIC LAYER        │
                    │                           │
                    │ ┌─ COHERENTIST ─────────┐ │
                    │ │ web_of_belief.py      │ │
                    │ │ refined_epistemic.py  │ │
                    │ │ abstraction_levels.py │ │
                    │ └───────────────────────┘ │
                    │                           │
                    │ ┌─ FOUNDATIONALIST ─────┐ │
                    │ │ propagation.py        │ │
                    │ │ (simple confidence)   │ │
                    │ └───────────────────────┘ │
                    └────────────┬──────────────┘
                                 │
                    ┌────────────▼──────────────┐
                    │      CAUSAL LAYER         │
                    │  epistemic_causal_bridge  │
                    │                           │
                    │ ┌── VAN FRAASSEN ───────┐ │
                    │ │ Contrast classes      │ │
                    │ │ Population contexts   │ │
                    │ │ Transfer rules        │ │
                    │ └───────────────────────┘ │
                    │                           │
                    │ ┌── PEARLIAN ───────────┐ │
                    │ │ MultiTheoryModel      │ │
                    │ │ StructuralEquation    │ │
                    │ │ Counterfactuals       │ │
                    │ └───────────────────────┘ │
                    │                           │
                    │ ┌── HAACK ──────────────┐ │
                    │ │ Security weights      │ │
                    │ │ Foundherentist ground │ │
                    │ └───────────────────────┘ │
                    └────────────┬──────────────┘
                                 │
                    ┌────────────▼──────────────┐
                    │   GAP IDENTIFICATION      │
                    │                           │
                    │  Epistemic gaps route to  │
                    │  VOI search / discovery   │
                    │  funnel for prioritized   │
                    │  evidence gathering       │
                    └────────────┬──────────────┘
                                 │
                    ┌────────────▼──────────────┐
                    │      OUTPUT LAYER         │
                    │  - Theory credences       │
                    │  - Research priorities    │
                    │  - Stubs identified       │
                    │  - Counterfactual results │
                    │  - Epistemic gaps (VOI)   │
                    │  - Security assessments   │
                    └───────────────────────────┘
```

## Causal Layer Details (ECB-3)

### Contrast Transfer Classification

When generalizing findings across populations, the bridge classifies transfer type:

| Type | Similarity | Action | Defined? |
|------|------------|--------|----------|
| DIRECT | ≥0.9 | No adjustment | Yes |
| BASELINE_SHIFT | ≥0.7 | Adjust for ceiling/floor | Yes |
| POPULATION_SHIFT | ≥0.5 | Increased uncertainty | Yes |
| MEANING_SHIFT | <0.5 | **Refuse to transfer** | No |

Thresholds are configurable via environment variables:
- `AE_CONTRAST_THRESHOLD_DIRECT` (default: 0.9)
- `AE_CONTRAST_THRESHOLD_BASELINE` (default: 0.7)
- `AE_CONTRAST_THRESHOLD_POPULATION` (default: 0.5)

### Gap Types

The bridge identifies five types of epistemic gaps:

| Gap Type | Description | Priority |
|----------|-------------|----------|
| `missing_contrast` | No explicit contrast class in source beliefs | 0.7 |
| `low_coverage` | Target population has limited evidence | 0.8 × (1 - coverage) |
| `theory_conflict` | Theories disagree on estimate | 0.6 × range |
| `baseline_unknown` | Missing baseline data for target | 0.5 |
| `blocked_beliefs` | Enabling conditions unmet | 0.4 |

Gaps are returned in `QuineanCounterfactualResult.gaps` for pipeline routing to VOI search.

### Security Weight (Haack)

Security measures foundherentist grounding:

```python
base_security = {
    'observational': 0.9,  # Direct experience
    'empirical': 0.7,      # Systematic observation
    'intermediate': 0.5,   # Mixed
    'theoretical': 0.3     # Abstract
}

# Bonuses
+ 0.15 for explicit contrast class (from paper methods)
+ 0.05 for inferred contrast class
+ 0.10 for entrenched status
+ 0.05 for established status
```

Higher security = more empirically grounded, better methodology.

## Recommended Use of Each Extraction Method

### Pattern-Based (`pdf_extraction.py`)
**Use for:**
- Fast batch processing
- Effect size extraction (regex very reliable)
- Temporal parameter detection
- Initial theory detection

**Strengths:**
- Fast (17 PDFs in seconds)
- Deterministic
- No API costs

**Limitations:**
- Shallow — catches surface patterns only
- Misses implicit theory references
- Can't assess argument structure

### LLM-Based (`theory_extraction.py`)
**Use for:**
- Deep analysis of key papers
- Extracting theory structure (claims, assumptions, boundary conditions)
- Understanding paper-theory relationships

**Strengths:**
- Semantic understanding
- Can extract nuanced relationships
- Handles implicit references

**Limitations:**
- Slow (API calls)
- Costly at scale
- Non-deterministic

### Recommended Workflow

1. **Batch extract** with pattern-based (`pdf_extraction.py`) — get 80% of info fast
2. **Flag high-importance papers** — those with unclear theory attachment or potential stubs
3. **Deep extract** flagged papers with LLM-based (`theory_extraction.py`)
4. **Integrate** into epistemic state
5. **Compare** foundationalist vs coherentist conclusions

## The Pedagogical Payoff

For the lecture, the dual-epistemology comparison demonstrates:

| Concept | How System Illustrates It |
|---------|---------------------------|
| Epistemology shapes conclusions | Same data → different credences |
| Theory-ladenness of observation | What counts as "theory-relevant" depends on model |
| Coherentism vs foundationalism | Explicit computation of both |
| Value of Information | Different frameworks recommend different experiments |
| Stubs as research opportunities | Coherentist model tracks unintegrated findings |
| Cross-domain evidence | Coherentist captures outside-domain support |

## Files for Lecture

1. `demonstration_report.md` — Full corpus analysis
2. `dual_epistemology_report.md` — Framework comparison with expert commentary
3. `extraction_results.json` — Raw extraction data for students to explore
4. Python modules — Students can run the analysis themselves

## Next Development Priorities

1. **Wire up LLM extraction** — Connect Claude Code's prompts to actual API calls
2. **Temporal parameter aggregation** — Meta-analyze timing data across studies
3. **Social epistemology layer** — Track disagreement across research communities
4. **Living review mode** — Incremental updates as new papers appear
