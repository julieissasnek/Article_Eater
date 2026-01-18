# Article Eater: Evidence Synthesis for Neuroarchitecture

## System Demonstration with Real CNFA Corpus

**Date:** January 2026  
**Corpus:** 17 papers from cognitive neuroscience of architecture  
**System Version:** Phase 1 Complete

---

## Executive Summary

This report demonstrates the Article Eater system processing a real corpus of neuroarchitecture research. The system successfully:

1. **Extracted** structured information from 17 PDFs (398 effect sizes, 69 temporal parameters)
2. **Integrated** evidence into a coherent epistemic state
3. **Tracked** theory credences based on accumulated evidence
4. **Identified** 6 "stubs" — findings awaiting theory integration
5. **Computed** Value of Information for research prioritization

---

## Theoretical Architecture

The system implements a **Quinean coherentist epistemology** rather than a foundationalist one:

| Feature | Foundationalism | Article Eater (Coherentism) |
|---------|-----------------|----------------------------|
| Epistemic bedrock | Observations certain | All levels uncertain |
| Warrant direction | Upward from data | Bidirectional constraint |
| Theory status | Derived from data | First-class epistemic objects |
| Orphan findings | Must attach to theory | Can exist as stubs |
| Criterion of acceptance | Correspondence with data | Coherence across web |

### Key Philosophical Innovations

1. **Semantic Status** (following Boghossian): Beliefs have different revisability based on their role:
   - Criterial rules (e.g., "cortisol measures stress") — almost semantic, very hard to revise
   - Framework beliefs — constitute paradigms
   - Synthetic beliefs — ordinary empirical claims

2. **Dependency Types** (following Glymour): Different inferential relationships:
   - Constitutive (B defines what A means)
   - Presuppositional (A cannot be true unless B)
   - Evidential (A raises/lowers probability of B)

3. **Bovens-Hartmann Coherence**: Principled measure comparing joint probability to independence

---

## Corpus Analysis

### Papers by Type

| Type | Count | Effect Sizes | Temporal Params |
|------|-------|--------------|-----------------|
| Empirical | 8 | 160 | 10 |
| Meta-analysis | 8 | 238 | 59 |
| Unknown | 1 | 0 | 0 |

### Theory References

| Theory | Papers | Primary Relation |
|--------|--------|------------------|
| Stress Recovery Theory (SRT) | 7 | cites (6), tests (1) |
| Biophilia Hypothesis | 6 | cites (5), tests (1) |
| Embodied Cognition | 4 | cites (4) |
| Attention Restoration Theory (ART) | 3 | cites (3) |
| Perceptual Fluency | 3 | cites (2), tests (1) |
| Predictive Processing | 1 | cites (1) |

---

## Epistemic State After Integration

### Theory Credences

```
Stress Recovery Theory         [0.87] █████████████████████
Perceptual Fluency             [0.85] █████████████████████
Biophilia Hypothesis           [0.80] ███████████████████
Predictive Processing          [0.78] ███████████████████
Attention Restoration Theory   [0.75] ██████████████████
Embodied Cognition             [0.70] █████████████████
```

**Interpretation:** SRT has the strongest evidential support in this corpus, with 7 papers citing or testing it. ART, despite being foundational to the field, has fewer papers in this particular corpus sample.

### Global Coherence

- Initial: 0.756
- After integration: 0.820

The increase in coherence indicates the corpus evidence is internally consistent — papers generally support rather than contradict each other.

---

## Key Quantitative Findings

### Exposure Durations

- N = 30 observations
- Range: 5–80 minutes
- Median: 15 minutes
- Mode: ~20 minutes

**Implication:** Most studies use relatively brief exposures (15-20 min). Longer-term effects (chronic exposure, residential environments) are understudied.

### Effect Sizes (Cohen's d)

- N = 56 observations
- Range: -1.14 to 0.82
- Mean: 0.17
- Median: 0.10

**Interpretation:** Small average effects, consistent with environmental psychology norms. This is not a weakness — small effects on important outcomes (stress, attention, health) can have large population-level impacts.

---

## Stubs: Findings Awaiting Integration

Six papers had findings but no clear attachment to the major theories:

1. **Chronic stress detection (physiological parameters)** — Meta-analysis with 14 effect sizes. Potentially extends SRT to chronic timescales.

2. **Forest bathing cardiovascular effects** — 42 effect sizes on BP, HR, HRV. Strong evidence, but mechanism unclear (SRT? ART? Other?).

3. **Therapeutic landscapes** — Conceptual piece awaiting empirical integration.

4. **Light and colour effects** — Cross-cultural study. Could connect to predictive processing or perceptual fluency.

**Research Opportunity:** These stubs represent theory extension opportunities. The forest bathing paper in particular has substantial effect size data that could strengthen SRT if properly linked.

---

## Value of Information Analysis

Where should research investment go? VOI quantifies where additional evidence would most shift our beliefs:

| Theory | VOI Score | Credence | Papers | Recommendation |
|--------|-----------|----------|--------|----------------|
| Predictive Processing | 1.03 | 0.78 | 1 | **High priority** — promising theory, minimal direct tests |
| Embodied Cognition | 0.84 | 0.70 | 4 | High priority — moderate credence, room to move |
| ART | 0.76 | 0.75 | 3 | Medium priority — foundational but needs more CNFA-specific tests |
| Biophilia | 0.64 | 0.80 | 6 | Lower priority — already well-supported |
| Perceptual Fluency | 0.52 | 0.85 | 3 | Lower priority — high credence |
| SRT | 0.44 | 0.87 | 7 | Lowest priority — already well-evidenced |

---

## Technical Implementation

### Modules

| Module | LOC | Function |
|--------|-----|----------|
| `web_of_belief.py` | 1,100 | Quinean coherentist epistemic state |
| `abstraction_levels.py` | 600 | Theory nesting, criterial rules, model zoom |
| `refined_epistemic.py` | 600 | Semantic status, typed dependencies, Bovens-Hartmann |
| `pdf_extraction.py` | 400 | PDF → structured data |
| `evidence_integration.py` | 250 | Extraction → epistemic state |

### Test Coverage

- 29/29 tests passing
- Unit tests for coherence, dependencies, quantities
- Philosophical tests for Quinean properties
- Integration tests for full pipeline

---

## Comparison to Standard Approaches

| Feature | Standard Meta-Analysis | Standard BN | Article Eater |
|---------|------------------------|-------------|---------------|
| Question | "What is average effect?" | "What causes what?" | "How well do theories cohere with evidence?" |
| Theories | Moderators at best | Nodes in network | First-class epistemic objects |
| Temporal params | Often ignored | Static | Meta-level uncertain quantities |
| Disagreement | Heterogeneity stat | Not modeled | Can track |
| Stubs | Excluded | Must fit network | Explicit category |
| Output | Effect size ± CI | Causal graph | Credence distribution over theories |

---

## Next Steps

### Phase 2 (With more PDFs)

1. **Meta-analytic integration** — Pool effect sizes properly, update theory credences
2. **Hierarchical moderators** — Temporal parameters by exposure type, population, setting
3. **Temporal parameter extraction** — Onset, peak, decay from methods sections

### Phase 3

1. **Social epistemology** — Track disagreement across research communities
2. **Living review** — Incremental updates as literature grows
3. **Publication/funder pitch** — Formal write-up of innovation

---

## For the Publication

**Core innovation:** A Bayesian evidence synthesis system that treats theories as first-class epistemic objects with credences that update based on coherence with accumulated evidence, not just statistical aggregation.

**Why it matters:**
1. Neuroarchitecture has multiple competing theories — we need to track relative evidential support
2. Findings exist without homes — stubs are a real category
3. Evidence from outside the domain matters — CNFA theories rest on basic science
4. Temporal dynamics are underspecified — we need to extract and aggregate timing parameters

**What we demonstrate:**
- Working system processing real papers
- Coherence-based theory evaluation
- Stub identification
- Value of Information for research prioritization

---

*Report generated by Article Eater v0.1*
