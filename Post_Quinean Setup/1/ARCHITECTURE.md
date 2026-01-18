# Article Eater - Integrated Architecture

## Module Overview

The system now has components from two development streams that complement each other:

### Core Epistemic Architecture (Quinean Coherentist)

| Module | Purpose | Key Features |
|--------|---------|--------------|
| `web_of_belief.py` | Core epistemic state | Joint probability over theory-worlds, stubs, reflective equilibrium |
| `refined_epistemic.py` | Refined epistemology | Semantic status (Boghossian), typed dependencies (Glymour), Bovens-Hartmann coherence |
| `abstraction_levels.py` | Theory nesting | Theories grounded in deeper theories, criterial rules, model zoom |
| `evidence_integration.py` | Integration layer | PDF extraction → epistemic state updates |
| `dual_epistemology.py` | Comparative analysis | Foundationalist vs coherentist contrast |

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
                    │    COMPARISON LAYER       │
                    │  dual_epistemology.py     │
                    │                           │
                    │  "Same data, different    │
                    │   philosophical lenses"   │
                    └────────────┬──────────────┘
                                 │
                    ┌────────────▼──────────────┐
                    │      OUTPUT LAYER         │
                    │  - Theory credences       │
                    │  - Research priorities    │
                    │  - Stubs identified       │
                    │  - Divergence analysis    │
                    └───────────────────────────┘
```

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
