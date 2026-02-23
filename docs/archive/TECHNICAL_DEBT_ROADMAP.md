# Technical Debt Roadmap

*Created: February 8, 2026*
*Panel: P-TD (Technical Debt)*

---

## What We're Building

Article Eater extracts scientific findings and builds a **self-improving Bayesian Network**. The system gets smarter the longer it runs:

```
Articles drip in → AE extracts rules → Beliefs accumulate → BN params refine
                                              ↑
         VOI search finds gaps ← Uncertainty tracking identifies weak edges
```

Each new article:
1. Updates posterior over edge strengths (conjugate Bayesian updates)
2. Reduces uncertainty on relevant edges
3. Identifies remaining gaps → drives next literature search

---

## Technical Debt Sprints

| Sprint | Focus | Priority | Key Technique |
|--------|-------|----------|---------------|
| **TD-A** | Theory inference | 1 (HIGH) | Embedding similarity + disambiguation |
| **TD-B** | Scope extraction | 2 (HIGH) | Section-aware NER + LLM fallback |
| **TD-C** | Coherence O(n²) | 3 (MED) | Hierarchical + constraint network |
| **TD-D** | Temporal parsing | 4 (LOW) | spaCy patterns |
| **TD-E** | Incremental BN | ARCH | Beta-Bernoulli conjugate + streaming |

---

## Expert Panel

### Core TD Panel (9 experts)

| Expert | Domain | Advises On |
|--------|--------|------------|
| Paul Thagard | Coherence theory | TD-C: Constraint-based coherence |
| Herbert Simon | Bounded rationality | TD-C: Satisficing, approximation |
| Nancy Cartwright | Philosophy of science | TD-B: Scope conditions |
| Deborah Mayo | Error statistics | TD-B: Severity, scope coverage |
| Marcia Bates | Information science | TD-A: Vocabulary bridging |
| James Pustejovsky | Temporal semantics | TD-D: TimeML, temporal parsing |
| Christopher Manning | NLP | TD-A, TD-B, TD-D: Extraction |
| Jon Kleinberg | Algorithms | TD-C: Scalable graph algorithms |
| Marti Hearst | Text mining | TD-A, TD-B: Entity extraction |

### Incremental Learning Panel (6 experts)

| Expert | Domain | Advises On |
|--------|--------|------------|
| Michael Jordan | Bayesian ML | TD-E: Posterior updating |
| Andrew Gelman | Bayesian statistics | TD-E: Conjugate priors |
| Tom Griffiths | Computational cogsci | TD-E: Active learning |
| David Blei | Variational inference | TD-E: Streaming updates |
| Zoubin Ghahramani | Bayesian nonparametrics | TD-E: Growing structures |
| Nando de Freitas | Sequential Monte Carlo | TD-E: Online inference |

---

## Implementation Order

1. **TD-A** (Theory Inference) — Must be accurate before BN can learn
2. **TD-B** (Scope Extraction) — Critical for claim validity
3. **TD-E** (Incremental BN) — Enables self-improvement
4. **TD-C** (Scalability) — Only needed at scale
5. **TD-D** (Temporal) — Enhancement, lower priority

---

## Key Files

| File | Purpose |
|------|---------|
| `docs/PANEL_P-TD_TECHNICAL_DEBT_REVIEW_2026_02_08.md` | Full panel consultation |
| `src/services/extraction_to_web.py` | TD-A, TD-B target |
| `src/services/web_of_belief.py` | TD-C target |
| `src/services/voi_search.py` | TD-E integration point |

---

*"The system should get smarter the longer you run it."*
