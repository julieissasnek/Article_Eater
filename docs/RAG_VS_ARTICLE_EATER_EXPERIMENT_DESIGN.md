# RAG vs. Article Eater QA — Experimental Comparison Design

**Objective**: Empirically demonstrate that structured epistemic infrastructure (EN + interpretation layer + tier taxonomy) produces qualitatively different answers than standard Retrieval-Augmented Generation using the same corpus.

**Thesis**: A small LLM with the Article Eater's epistemic network and interpretation layer can produce *deeper, more nuanced, and more epistemically responsible* answers than a large LLM with naive RAG over the same article set. The difference reveals what "deep knowledge" means vs. "book knowledge."

---

## Experimental Design

### Independent Variable: QA System Type

| Condition | System | What It Has | What It Lacks |
|-----------|--------|-------------|---------------|
| **RAG-Baseline** | LLM + vector embeddings of article texts | Full text of all ~1,100 articles | Belief structure, credence, warrants, theory, taxonomy |
| **RAG-Enhanced** | LLM + vector embeddings of extraction JSONs | Structured findings (33K+) as documents | Belief synthesis, coherence, tier structure |
| **Article Eater** | LLM + full EN/BN/interpretation layer | 4,888 beliefs, 13 T1.5 theories, provenance, warrants | — |
| **Article Eater (no LLM)** | Template-based QA only | Same as above but no LLM generation | Fluency, novel synthesis |

### Dependent Variables (scored by blind raters)

| DV | Description | Scale | What it measures |
|----|-------------|-------|------------------|
| **Factual Accuracy** | Are the stated facts correct per the source papers? | 1-5 | Basic retrieval quality |
| **Evidential Grounding** | Does the answer cite specific studies, sample sizes, effect sizes? | 1-5 | Evidence depth |
| **Theoretical Integration** | Does the answer connect findings to T1/T1.5 frameworks? | 1-5 | Deep knowledge |
| **Uncertainty Honesty** | Does the answer express appropriate confidence/uncertainty? | 1-5 | Epistemic responsibility |
| **Contradiction Awareness** | Does the answer acknowledge conflicting evidence? | 1-5 | Dialectical sophistication |
| **Practical Specificity** | Are design recommendations concrete and caveated? | 1-5 | Actionability |
| **Cross-Domain Integration** | Does the answer link across sensory modalities or domains? | 1-5 | Synthesis breadth |
| **Explanation Depth** | Does the answer explain *why*, not just *what*? | 1-5 | Mechanistic understanding |

### Question Battery (40 questions, 8 categories × 5 each)

#### Category 1: Simple factual (RAG should do well)
1. What is the optimal illuminance for office work?
2. What temperature range is most comfortable?
3. What noise level impairs cognitive performance?
4. Does biophilic design reduce stress?
5. What is the effect of daylight on sleep quality?

#### Category 2: Evidence synthesis (should differentiate systems)
6. What is the overall effect size of natural light on productivity?
7. How many studies support attention restoration theory?
8. What is the sample-size-weighted effect of noise on creativity?
9. Is the evidence for biophilia stronger than for prospect-refuge theory?
10. What percentage of green space studies find positive health outcomes?

#### Category 3: Theoretical mechanism (Article Eater should excel)
11. How does predictive processing explain the restorative effect of nature?
12. What neural mechanisms mediate the CCT-alertness relationship?
13. How does spatial navigation theory predict wayfinding in complex buildings?
14. What is the embodied cognition account of thermal comfort?
15. How do neuromodulatory systems explain the interaction between light and mood?

#### Category 4: Contradictions and disagreements
16. Do open offices help or hurt productivity? What explains the disagreement?
17. Is high visual complexity good or bad for wellbeing?
18. Does background music enhance or impair cognitive performance?
19. Why do some studies find green views restorative and others don't?
20. Is the optimal CCT for alertness 4000K or 6500K?

#### Category 5: Cross-domain integration
21. How do lighting and acoustic conditions interact to affect stress?
22. What is the combined effect of temperature and air quality on cognitive performance?
23. How might biophilic design principles apply across visual, acoustic, and olfactory domains?
24. What is the Goldilocks principle and how does it manifest across sensory modalities?
25. How do cultural differences moderate environmental preference across domains?

#### Category 6: Design recommendations (practical)
26. How should I design a hospital waiting room to reduce patient anxiety?
27. What environmental design interventions have the strongest evidence for improving student learning?
28. How should office lighting change throughout the day?
29. What are evidence-based guidelines for acoustic privacy in open-plan workspaces?
30. How would you design a restorative garden for a dementia care facility?

#### Category 7: Methodological assessment
31. What are the main confounders in daylight-health studies?
32. Why is it hard to run RCTs on architectural interventions?
33. What sample sizes are typical in environmental psychology studies?
34. How should we handle publication bias in this field?
35. What study designs would resolve the open office productivity debate?

#### Category 8: Meta-epistemic (hardest for RAG)
36. How confident should we be in the biophilia hypothesis?
37. What is the weakest link in the evidence chain from CCT to alertness?
38. Which T1 theoretical framework has the most empirical support?
39. Where are the biggest gaps in the environmental psychology evidence base?
40. If you could fund one study, what would resolve the most uncertainty?

---

## Implementation Plan

### Phase 1: Build RAG baselines (1-2 hours)

```python
# scripts/rag_comparison/build_rag_baseline.py

# 1. Create vector store from article texts
# Use sentence-transformers (all-MiniLM-L6-v2) to embed:
#   - RAG-Baseline: full article PDFs/abstracts (raw text)
#   - RAG-Enhanced: extraction JSONs (structured findings)
# Store in FAISS or ChromaDB

# 2. RAG query function:
def rag_answer(question: str, top_k: int = 10) -> str:
    """Retrieve top-k chunks, feed to LLM with question."""
    chunks = vector_store.similarity_search(question, k=top_k)
    prompt = f"Based on the following research excerpts, answer: {question}\n\n{chunks}"
    return llm.generate(prompt)
```

### Phase 2: Run Article Eater QA (already built)

```python
# Use existing arbitrary_qa_handler + enrichment orchestrator
from src.services.arbitrary_qa_handler import ArbitraryQAHandler
from src.services.answer_enrichment_orchestrator import enrich_answer

def article_eater_answer(question: str) -> dict:
    handler = ArbitraryQAHandler()
    base_answer = handler.answer(question)
    enriched = enrich_answer(base_answer, question)
    return enriched.to_dict()
```

### Phase 3: Collect answers (scripted)

```python
# scripts/rag_comparison/run_comparison.py
# For each of 40 questions:
#   1. Get RAG-Baseline answer
#   2. Get RAG-Enhanced answer
#   3. Get Article Eater answer
#   4. Get Article Eater (no LLM) answer
# Save all 160 answers (40 × 4) to JSON
# Strip system identifiers for blinding
```

### Phase 4: Blind rating

- **Raters**: 3 experts (environmental psychologist, epistemologist, architect)
- **Protocol**: Each rater scores each answer on all 8 DVs (1-5)
- **Blinding**: Answers presented in random order without system labels
- **IRR**: Compute Krippendorff's alpha for inter-rater reliability

### Phase 5: Analysis

```python
# scripts/rag_comparison/analyze_results.py
# 1. Mixed-effects ANOVA: System × Category → each DV
# 2. Post-hoc pairwise comparisons (Tukey HSD)
# 3. Radar chart: mean scores per system across 8 DVs
# 4. Heat map: System × Category × DV
# 5. Qualitative coding: What does Article Eater say that RAG doesn't?
```

---

## Predicted Results and Interpretation

| Category | RAG-Baseline | RAG-Enhanced | Article Eater | Why |
|----------|-------------|--------------|---------------|-----|
| Simple factual | ★★★★ | ★★★★★ | ★★★★★ | Both can retrieve facts |
| Evidence synthesis | ★★ | ★★★ | ★★★★★ | RAG can't compute weighted meta-analyses |
| Theoretical mechanism | ★★ | ★★ | ★★★★★ | RAG has no T1 framework layer |
| Contradictions | ★★ | ★★★ | ★★★★★ | RAG lacks dialectical structure |
| Cross-domain | ★★ | ★★ | ★★★★ | RAG can't traverse taxonomy links |
| Design recommendations | ★★★ | ★★★ | ★★★★★ | Article Eater has CVA + practical implications |
| Methodological | ★★ | ★★★ | ★★★★ | Article Eater tracks study design metadata |
| Meta-epistemic | ★ | ★★ | ★★★★★ | RAG fundamentally cannot reason about its own uncertainty |

### Key Predicted Findings

1. **RAG and Article Eater converge on simple factual questions** — this is expected and validates that both systems have access to the same corpus.

2. **Article Eater dominates on theoretical integration, contradiction awareness, and meta-epistemic questions** — this is where structured epistemic infrastructure provides value that retrieval alone cannot.

3. **The gap widens as questions become more epistemically complex** — the "staircase of epistemic sophistication."

4. **RAG-Enhanced outperforms RAG-Baseline** — showing that structured extraction helps, but not as much as full belief synthesis.

---

## What This Proves

> **A small LLM + epistemic infrastructure > large LLM + retrieval**

The comparison demonstrates that:
- **Book knowledge** (RAG) = knowing what studies say
- **Deep knowledge** (Article Eater) = knowing what studies *mean*, how they relate, where they conflict, and how confident to be

This is the difference between an encyclopedia and an expert. The Article Eater's EN + interpretation layer + tier taxonomy functions as **crystallized epistemic expertise** that a naive LLM cannot replicate through retrieval alone.

### Implications for the field
- Small LLMs need structured knowledge infrastructure (EN, BN, interpretation layers) to compete with large LLMs on domain expertise
- RAG is necessary but not sufficient for epistemic competence
- The investment in belief networks, uncertainty quantification, and theoretical grounding pays dividends in answer quality
