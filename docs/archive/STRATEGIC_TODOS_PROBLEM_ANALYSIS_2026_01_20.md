# Problem Analysis: Sharpening the Three Strategic TODOs

**Date:** January 20, 2026
**Purpose:** Pre-panel refinement of problem statements
**Status:** Ready for review before expert consultation

---

## TODO 1: Credibility Testing — Refined Problem Analysis

### The Core Problem, Stated Crisply

**Problem:** When the system ingests an article and updates the web, we currently have no automated way to distinguish *legitimate epistemic updates* from *extraction errors, overfitting, or pathological dynamics*.

A human expert watching the system process articles would occasionally say: "That update doesn't seem right." We need to operationalize that judgment.

### Why This Is Hard

The difficulty is that we're trying to evaluate *epistemic appropriateness*, not just *computational correctness*. The system might execute perfectly (no bugs) while producing epistemically inappropriate results:

1. **Credence magnification:** A weak study causes large belief shifts because it happens to be the first evidence on a topic. Computationally correct, epistemically excessive.

2. **Spurious coherence:** Two beliefs become linked because they share surface vocabulary, not because they're genuinely related. The coherence score improves, but it's fake coherence.

3. **Extraction hallucination:** The LLM extracts a belief that isn't actually in the paper, or assigns a credence that doesn't match the paper's evidence strength.

4. **Scope overreach:** A study of college students gets scope conditions implying universal applicability.

These are *meaning* problems, not *computation* problems. That's why they're hard to detect automatically.

### The Key Insight

The insight is that we can't directly measure "epistemic appropriateness" but we can measure **consistency with expectations**. If we have well-calibrated expectations about how the system should behave, deviations signal potential problems.

**Expectations we can operationalize:**

| Expectation | Operationalization |
|-------------|-------------------|
| Credence changes should be proportionate to evidence strength | Compare Δcredence to n, effect size, methodology quality |
| New constraints should connect semantically related beliefs | Measure semantic similarity of constrained belief pairs |
| Global coherence should not degrade spuriously | Track coherence trajectory; flag unexpected drops |
| Stub rates should be stable or declining | Monitor stub count; flag unexpected spikes |
| Extraction should match paper type | Theory papers → theoretical beliefs; empirical → empirical |

### Proposed Technical Approach

**Baseline calibration:** Process the Gold Standard corpus with known-good extractions. Compute distributions of:
- Credence change magnitudes per evidence type
- Constraint semantic similarity scores
- Coherence change per article
- Belief type distribution per paper type

**Anomaly detection:** For each new article, compare its profile to the baseline distribution. Flag articles where metrics fall outside 2σ (or some calibrated threshold).

**Structured report:** For flagged articles, generate a report explaining which metrics deviated and by how much. This enables targeted human review rather than reviewing every article.

### What Success Looks Like

**Minimum viable product:**
- A `credibility_check(article_id)` function that returns PASS/FLAG/FAIL
- For FLAG/FAIL, a structured explanation of what triggered the flag
- False positive rate < 20% (we don't want to flag good articles too often)
- True positive rate > 80% (we want to catch most problematic updates)

**Stretch goal:**
- Specific diagnosis: "Credence change excessive" vs "Constraint semantically inappropriate" vs "Scope overreach"
- Suggested remediation: "Consider narrowing scope to X" or "Consider lowering credence to Y"

### Open Questions for Expert Panel

1. **What counts as "excessive" credence change?** Is there a principled relationship between evidence strength and appropriate credence shift? (Bayesian answer: use likelihood ratios. But our system isn't purely Bayesian.)

2. **How do we measure "semantic appropriateness" of constraints without using LLMs?** Current options: embedding similarity, taxonomy path distance, co-citation frequency.

3. **Should the system ever reject an article outright, or always flag for human review?** Trade-off between automation and safety.

4. **How do we handle the cold-start problem?** The first few articles have no baseline to compare against.

---

## TODO 2: Interpretive Intelligence — Refined Problem Analysis

### The Core Problem, Stated Crisply

**Problem:** The web contains rich epistemic structure, but users can only access it through programmatic queries. We need a *reasoning layer* that can traverse this structure and produce *explanations* that answer the kinds of questions humans ask about knowledge.

This is NOT retrieval-augmented generation. RAG answers "What do the documents say about X?" We need to answer "Why does the *system* believe X, how confident should we be, and what could change that?"

### Why This Is Hard

1. **Explanation is harder than computation.** Computing coherence is O(n²) in constraints. Explaining *why* coherence is high or low requires reasoning about which constraints matter most, which is NP-hard in general.

2. **User questions are underspecified.** "Why does the system believe plants reduce stress?" could mean:
   - What evidence supports this?
   - What theories predict this?
   - What mechanisms explain this?
   - What scope conditions apply?
   - What would change our mind?

   We need to infer intent and provide appropriately scoped answers.

3. **Explanations must be *epistemically honest*.** We shouldn't overstate confidence or hide contingencies. But we also shouldn't overwhelm users with every caveat.

4. **The web's structure is complex.** A single belief might be connected to 20 other beliefs through constraints of varying types and strengths. Flattening this into prose is non-trivial.

### The Key Insight

The insight is that most user questions fall into a small number of **explanation patterns**:

| Pattern | Question Type | Traversal Required |
|---------|--------------|-------------------|
| Evidence trace | "What evidence supports X?" | Backward from X to empirical beliefs |
| Theory trace | "What theories predict X?" | Backward from X to theoretical beliefs |
| Interaction map | "What affects X?" | Outward from X via all constraints |
| Credibility assessment | "How reliable is X?" | Meta-analysis of X's constraint network |
| Contingency map | "What assumptions does X rest on?" | Backward through constraint chains |
| What-if analysis | "What if Y were false?" | Counterfactual propagation |

If we can implement these patterns well, we cover 80%+ of user questions.

### Proposed Technical Approach

**Template-based generation:** For each explanation pattern, define:
1. A traversal algorithm over the web
2. A template for rendering the traversal results
3. Heuristics for deciding how much detail to include

**Example for "Evidence trace":**
```
Algorithm:
  1. Get all constraints where target = belief_id and type = SUPPORTS
  2. Filter to source beliefs with level = EMPIRICAL or OBSERVATIONAL
  3. Sort by constraint strength × source credence
  4. Take top N (default 5)

Template:
  "This belief is supported by {N} empirical findings:
   - {belief_1.content} (credence: {c1}, from {paper_1}) — {strength_1} support
   - {belief_2.content} (credence: {c2}, from {paper_2}) — {strength_2} support
   ...
   The strongest support comes from {top_belief}, which {explanation_of_why}."

Detail heuristic:
  If N > 5: "and {N-5} additional studies (use 'deep' mode to see all)"
  If any contradicting: "Note: {M} studies report contrary findings (see below)"
```

**Relevance filtering:** Use simple heuristics to decide what to include:
- Include constraints with strength > 0.3
- Include contradicting evidence even if weak (users need to know)
- Include scope conditions if they differ from user's implied context
- Include theoretical backing if user asked a "why" question

### What Success Looks Like

**Minimum viable product:**
- Implement 4 core patterns: evidence trace, theory trace, credibility assessment, contingency map
- Generate readable prose without LLM calls for standard cases
- Response time < 1 second for typical queries

**Stretch goal:**
- Natural language question parsing (via lightweight LLM or pattern matching)
- Interactive drill-down ("tell me more about assumption #3")
- Visualization of constraint network focused on query

### Open Questions for Expert Panel

1. **How do we decide when contingencies are "worth mentioning"?** A belief might rest on 50 transitive assumptions. Which ones matter to users?

2. **How do we communicate uncertainty without paralysis?** Users need to make decisions. "Everything is uncertain" is true but unhelpful.

3. **Should explanations differ by user expertise?** A researcher wants different detail than a practitioner. How do we calibrate?

4. **How do we explain cross-theory bridges without confusing users?** "SRT and ART are connected via functional equivalence" requires epistemological background.

---

## TODO 3: VOI-Driven Article Search — Refined Problem Analysis

### The Core Problem, Stated Crisply

**Problem:** The web has epistemic gaps—beliefs with high uncertainty, untested mechanisms, unexplored scope boundaries, weak bridge warrants. Literature exists that could address these gaps, but standard keyword search doesn't find it because:

1. The gap is conceptual, not terminological ("we need studies testing SRT mechanisms" doesn't translate to obvious keywords)
2. The relevant literature uses different vocabulary (psychology vs neuroscience vs architecture)
3. The gap might be best addressed by adjacent fields we're not searching

We need a system that translates *epistemic needs* into *effective search strategies*.

### Why This Is Hard

1. **Epistemic gaps are abstract.** "High uncertainty in ART→SRT bridge" is not a search query. We need to operationalize what evidence would reduce this uncertainty and then find papers providing such evidence.

2. **The translation is many-to-many.** One gap might be addressable by many kinds of papers. One paper might address many gaps. We need to handle this complexity.

3. **Cross-field vocabulary divergence.** "Stress recovery" in CNfA might be "autonomic regulation" in neuroscience, "relaxation response" in psychology, "healing environment" in healthcare. A naive keyword search misses the others.

4. **Negative evidence is hard to find.** We need null results and replication failures to calibrate credences, but these are rarely indexed well and often not published.

5. **Quality varies.** A VOI-optimal search finds the most *informative* papers, not just the most *relevant* by keyword. A small, well-designed experiment might be more valuable than a large correlational study.

### The Key Insight

The insight is that epistemic gaps have **types**, and each type suggests specific **search strategies**:

| Gap Type | What We Need | Search Strategy |
|----------|-------------|-----------------|
| Scope boundary | Studies in unexplored populations/settings | Restrict to missing scope + core concepts |
| Mechanism test | Studies that measure proposed mechanism | Search for mechanism terms + methodological terms |
| Bridge evidence | Studies measuring constructs from both theories | Search for co-occurrence of both theory terms |
| Replication need | Independent replication of key finding | Citation search + methodological filter |
| Null result | Studies finding no effect | "no effect" OR "not significant" + concepts |
| Theory challenge | Papers critiquing the theory | "critique" OR "challenge" OR "alternative" |

By categorizing gaps and applying type-specific strategies, we get much better search results than naive keyword search.

### Proposed Technical Approach

**Gap typing and prioritization:**
```python
def identify_gaps(web: WebOfBelief) -> List[EpistemicGap]:
    gaps = []

    # Scope boundaries
    for belief in web.beliefs.values():
        missing_scopes = identify_missing_scopes(belief)
        for scope in missing_scopes:
            gaps.append(ScopeBoundaryGap(belief, scope, voi=compute_scope_voi(...)))

    # Mechanism uncertainty
    for belief in web.beliefs.values():
        if belief.level == INTERMEDIATE and belief.credence.uncertainty > 0.3:
            gaps.append(MechanismGap(belief, voi=compute_mechanism_voi(...)))

    # Weak bridges
    for bridge in web.bridges.values():
        if bridge.confidence < 0.5:
            gaps.append(BridgeGap(bridge, voi=compute_bridge_voi(...)))

    return sorted(gaps, key=lambda g: g.voi, reverse=True)
```

**Query generation by type:**
```python
def generate_queries(gap: EpistemicGap) -> List[SearchQuery]:
    if isinstance(gap, ScopeBoundaryGap):
        return scope_search_strategy(gap)
    elif isinstance(gap, MechanismGap):
        return mechanism_search_strategy(gap)
    elif isinstance(gap, BridgeGap):
        return bridge_search_strategy(gap)
    ...
```

**Cross-field vocabulary expansion:**
```python
def expand_for_fields(term: str, fields: List[str]) -> List[str]:
    """Expand CNfA term to equivalents in other fields."""
    expansions = [term]
    for field in fields:
        if (term, field) in VOCABULARY_MAP:
            expansions.extend(VOCABULARY_MAP[(term, field)])
    return expansions

# Example:
expand_for_fields("stress recovery", ["neuroscience", "psychology"])
# → ["stress recovery", "autonomic regulation", "HPA axis recovery",
#    "psychophysiological recovery", "relaxation response"]
```

**Result ranking by information gain:**
```python
def rank_results(results: List[Paper], gap: EpistemicGap) -> List[RankedPaper]:
    """Rank search results by expected information gain, not just relevance."""
    ranked = []
    for paper in results:
        relevance = compute_relevance(paper, gap)
        quality = estimate_paper_quality(paper)  # Citations, journal, methodology
        novelty = estimate_novelty(paper, web)    # Does it bring new info?
        expected_ig = relevance * quality * novelty
        ranked.append(RankedPaper(paper, expected_ig))
    return sorted(ranked, key=lambda r: r.expected_ig, reverse=True)
```

### What Success Looks Like

**Minimum viable product:**
- Given a high-VOI gap, generate 5-10 search queries that outperform naive keyword search
- Cross-field expansion working for top 20 CNfA concepts
- Precision@10 at least 2x better than keyword baseline

**Stretch goal:**
- Fully automated gap→search→acquisition pipeline
- Citation chain following for mechanism papers
- Integration with reference managers (Zotero export)
- Feedback loop: track which acquired papers actually reduced uncertainty

### Open Questions for Expert Panel

1. **How do we estimate VOI without knowing what we'll find?** The value of a search depends on results we haven't seen yet. What heuristics work?

2. **How do we balance exploration vs exploitation?** Should we search for papers that definitely address known gaps, or exploratory searches that might reveal unknown gaps?

3. **What's the right granularity for cross-field vocabulary?** Too fine-grained = unmaintainable. Too coarse = misses relevant papers.

4. **How do we handle the "no papers found" case?** If no literature addresses a gap, that's valuable information (suggests original research needed), but how do we distinguish "no papers exist" from "our search was bad"?

---

## Summary: The Three Problems at Their Core

| TODO | Core Challenge | Key Insight | Technical Crux |
|------|---------------|-------------|----------------|
| **Credibility Testing** | Distinguish legitimate updates from errors | Deviation from calibrated expectations signals problems | Baseline calibration + anomaly detection |
| **Interpretive Intelligence** | Translate structure into explanations | Most questions follow a few patterns | Template-based traversal + relevance filtering |
| **VOI-Driven Search** | Translate gaps into effective queries | Gap types suggest search strategies | Gap typing + cross-field expansion |

All three share a common theme: **making the web's implicit knowledge explicit and actionable**.

- Credibility testing makes the *quality* of updates explicit
- Interpretive intelligence makes the *structure* of beliefs explicit
- VOI search makes the *gaps* in knowledge explicit

Together, they transform the web from a passive knowledge store into an active epistemic agent.

---

## Recommended Next Steps

1. **Review this analysis** — Does it sharpen the problems appropriately?
2. **Prioritize** — Which TODO should we tackle first? (I recommend Credibility Testing, since it protects the system's integrity)
3. **Select experts** — The panel composition may vary by TODO
4. **Draft expert prompts** — Use this analysis to frame questions for the panel

---

*Document created: January 20, 2026*
