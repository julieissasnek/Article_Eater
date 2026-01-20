# Phase C: Implementation Plan Critique

**Date:** January 20, 2026
**Phase:** C (Critique by Team + System Designer)
**Reviewers:**
- Core Panel: Pearl, Cartwright, Simon, Bates, Kaplan
- TODO 1 Specialist: Mayo
- TODO 2 Specialist: Wilson
- TODO 3 Specialist: Giles
- System Designer: Butler Lampson

---

## Part I: System-Wide Critique (Butler Lampson)

*Drawing from "Hints for Computer System Design" (1983) and decades of systems building experience.*

### General Observations

These three plans share architectural patterns that deserve scrutiny before implementation. Let me identify cross-cutting concerns.

### Critique 1: Premature Abstraction

**Observation:** All three plans define rich type hierarchies upfront (Severity enums, GapType enums, ExplanationPattern enums). This is a common trap.

**The Problem:** You don't yet know what categories you need. The TODO 1 plan distinguishes 12 FlagTypes across 3 severity levels—but you've never run the system. You're guessing.

**Recommendation:** Start with a simpler model:
- TODO 1: Begin with just two categories (STOP vs PROCEED_WITH_CAUTION). Add subcategories only when you find yourself repeatedly wishing you had them.
- TODO 2: Start with ONE explanation pattern (Evidence Trace). Add others when users ask questions your single pattern can't answer.
- TODO 3: Start with TWO gap types (UNCERTAIN and UNDEREXPLORED). Refine the taxonomy after you've seen 100 real gaps.

**Principle:** "Make it work, make it right, make it fast—in that order." You're trying to make it right before you've made it work.

### Critique 2: Interface Complexity

**Observation:** The interfaces between components are data-rich. For example, `CredibilityReport` contains 10+ fields; `EpistemicGap` contains 8+ fields.

**The Problem:** Rich interfaces create tight coupling. If TODO 3's gap identifier produces a field that TODO 1's credibility tester expects, you've created an implicit contract that's hard to change.

**Recommendation:** Define the minimal interface first:
```python
# Instead of rich CredibilityReport
class SimpleDecision:
    action: Literal["accept", "reject", "review"]
    reason: str
    confidence: float
```

Only expand when the simple version proves insufficient. You can always add fields; removing them is painful.

### Critique 3: State Management Ambiguity

**Observation:** All three systems need to interact with `WebOfBelief`, but the state management pattern isn't clear. TODO 1 mentions "transactions" but doesn't specify isolation levels. TODO 2 traverses the web but doesn't lock. TODO 3 reads the web state to identify gaps.

**The Problem:** If TODO 1 is evaluating a credibility check while TODO 3 is reading gaps, what happens if the web changes mid-operation?

**Recommendation:** Make the concurrency model explicit:
- **Option A:** Single-writer. One operation at a time on the web.
- **Option B:** Snapshot isolation. Each operation works on a frozen snapshot.
- **Option C:** Eventual consistency. Operations may see stale data; handle conflicts.

I recommend **Option B** for this system. The web's coherence constraints mean operations should see consistent state. Implement `web.get_snapshot() -> WebSnapshot` and have all three TODOs work from snapshots.

### Critique 4: Feedback Loop Complexity

**Observation:** All three plans include feedback tracking (FlagResolution, AcquisitionFeedback, user test results). Each has its own SQLite database.

**The Problem:** Three separate feedback stores means:
1. Three separate schemas to maintain
2. No cross-cutting analysis (e.g., "Did credibility flags correlate with unhelpful search results?")
3. Three times the migration burden

**Recommendation:** Create a unified feedback store:
```python
@dataclass
class SystemFeedback:
    timestamp: datetime
    component: str  # "credibility", "explanation", "search"
    operation_id: str
    outcome: str  # "positive", "negative", "neutral"
    details: Dict[str, Any]
```

Centralize before you diversify.

### Critique 5: Missing Failure Modes

**Observation:** The plans specify success paths well but underspecify failure handling.

**Questions to answer:**
- TODO 1: What if Gold Standard corpus is empty? What if a check throws an exception mid-evaluation?
- TODO 2: What if vocabulary bridge has no mapping for a term? What if template rendering fails?
- TODO 3: What if Semantic Scholar API is down? What if a gap produces zero search results?

**Recommendation:** For each component, list the three most likely failure modes and specify behavior. Don't over-engineer (no circuit breakers yet), but at least document: "If X fails, return Y and log Z."

### Critique 6: Testing Strategy

**Observation:** Each plan mentions tests, but the testing approach varies:
- TODO 1: Adversarial Failure Standard
- TODO 2: User comprehension testing
- TODO 3: Precision@10 metrics

**The Problem:** These are all evaluation metrics, not unit tests. Where are the component tests that verify individual functions work correctly?

**Recommendation:** Each plan should specify:
1. **Unit tests** — Individual functions with mock data
2. **Integration tests** — Components working together
3. **System tests** — End-to-end with real data
4. **Evaluation metrics** — The precision/recall numbers you're tracking

### Bottom Line

**What to do now:**
1. Simplify the type hierarchies (≤3 categories per enum initially)
2. Define minimal interfaces (3-5 fields, not 10+)
3. Specify the concurrency model (I recommend snapshot isolation)
4. Unify feedback tracking
5. Document failure modes before coding
6. Distinguish unit tests from evaluation metrics

**What's good:**
- Clear separation of concerns
- Thoughtful use of expert recommendations
- Sprint structure is reasonable
- Success metrics are measurable

---

## Part II: TODO 1 Critique — Credibility Testing

### Pearl's Critique

**On causal_status_mismatch check:**

The check correctly flags causal claims from non-experimental studies. But the implementation is too binary. Many observational studies use methods that strengthen causal inference (instrumental variables, regression discontinuity, natural experiments).

**Recommendation:** Add a middle category:
```python
DESIGN_STRENGTHS = {
    "quasi_experiment": 0.7,  # Partial support for causal claims
    "natural_experiment": 0.8,
    "regression_discontinuity": 0.85,
    "instrumental_variable": 0.75,
    "rct": 1.0
}
```

Flag if credence exceeds the design's maximum warranted strength, not if design lacks full experimental control.

### Cartwright's Critique

**On scope_overreach check:**

The check is too crude. It flags missing scope when sample is specific, but "specific" doesn't mean "ungenerable." A study on "Western adults" may generalize to other WEIRD populations; a study on "children with ADHD" may not generalize at all.

**Recommendation:** Add scope distance metric:
```python
def scope_distance(sample_description: str, claimed_scope: Scope) -> float:
    """How far does the claim extend beyond the sample?"""
    # Categories: same, similar, distant, universal
    ...
```

Flag when scope_distance > threshold, not when scope_specified is False.

### Mayo's Critique

**On Failure Standard corpus:**

The plan correctly includes adversarial test cases. But the cases are too obvious (negative sample size, p > 1). Real problems are subtle: a study with N=200 but only N=45 for the critical comparison; an effect size that's valid for one measure but reported for another.

**Recommendation:** Add "subtle failure" cases:
- Subgroup N vs total N confusion
- Effect size Cohen's d vs Hedges' g confusion
- Confidence interval spanning zero but reported as "marginally significant"
- Multiple comparison correction missing

These test whether the system catches realistic errors, not just absurdities.

### Simon's Critique

**On threshold tuning:**

The plan sets thresholds (2σ for excessive_credence_change) without specifying how they'll be calibrated. "Tune based on false positive rate" is too vague.

**Recommendation:** Specify the calibration procedure:
1. Process 50 articles with very low thresholds (catch everything)
2. Have expert review all flags
3. Compute ROC curve for each flag type
4. Select threshold at 80% sensitivity target
5. Document selected threshold with justification

This makes threshold selection reproducible.

### Decision Points to Add:
1. How to handle missing methodology metadata?
2. What's the minimum Gold Standard size for stable baselines?
3. How to prioritize which flag types to implement first?

---

## Part III: TODO 2 Critique — Interpretive Intelligence

### Wilson's Critique

**On question classification:**

The keyword-based classifier is fragile. "How does biophilic design help with stress?" contains "how" (→ mechanism), "design" (→ practical), and "stress" (could be any pattern).

**Recommendation:** Don't classify, ask:
```python
def clarify_question_type(question: str) -> ClarifyingQuestion:
    """If classification is uncertain, ask user."""
    confidence = classifier.confidence
    if confidence < 0.7:
        return ClarifyingQuestion(
            "What kind of answer are you looking for?",
            options=["Evidence summary", "How it works", "Design recommendations"]
        )
```

Per my Relevance Theory: better to ask once than guess wrong.

### Bates' Critique

**On vocabulary bridge:**

The mapping is static (YAML file) but vocabulary evolves. New terms emerge; old terms shift meaning. "Biophilic" meant something different in 1990 than 2026.

**Recommendation:** Add temporal markers:
```yaml
biophilic_design:
  internal: "design.biophilic"
  academic:
    - term: "biophilic design"
      introduced: 2008
    - term: "biophilia hypothesis"
      introduced: 1984
    - term: "nature-based design"
      introduced: 2015
```

When searching old literature, use period-appropriate terms.

### Kaplan's Critique

**On practical implications:**

The design action mappings are too generic. "Provide visual access to natural elements in high-stress areas" doesn't tell a designer *what* natural elements, *how much* visual access, or *which* high-stress areas.

**Recommendation:** Add specificity levels:
```python
@dataclass
class DesignRecommendation:
    action: str
    specificity: str  # "principle", "guideline", "specification"
    quantitative_guidance: Optional[str]  # e.g., "≥3 plants per 10m²"
    reference_examples: List[str]
```

At minimum, flag when evidence is too weak for specification-level guidance.

### Simon's Critique (User Modes)

**On UserMode:**

Four modes (quick, standard, deep, novice) cross two dimensions: detail level and expertise level. This conflates things that should be separate.

**Recommendation:** Separate dimensions:
```python
class DetailLevel(Enum):
    SUMMARY = 1  # One paragraph
    STANDARD = 2  # Full explanation
    COMPREHENSIVE = 3  # All details

class ExpertiseLevel(Enum):
    NOVICE = 1  # Define technical terms
    PRACTITIONER = 2  # Assume domain knowledge
    RESEARCHER = 3  # Assume methodological sophistication
```

Then compose: novice+summary, researcher+comprehensive, etc.

### Decision Points to Add:
1. How to handle questions the system can't answer?
2. What's the update strategy for vocabulary bridge?
3. How to measure explanation quality (beyond comprehension quiz)?

---

## Part IV: TODO 3 Critique — VOI-Driven Search

### Giles' Critique

**On search sources:**

The plan includes Semantic Scholar and PubMed, but these have different strengths:
- Semantic Scholar: Better citation data, faster, but less comprehensive for older literature
- PubMed: Comprehensive for biomedical, but poor for architecture/design

**Recommendation:** Add source selection logic:
```python
def select_sources(gap: EpistemicGap) -> List[str]:
    """Choose sources based on gap characteristics."""
    if gap.details.get("field") in ["neuroscience", "healthcare"]:
        return ["pubmed", "semantic_scholar"]
    elif gap.details.get("field") in ["architecture", "design"]:
        return ["semantic_scholar", "web_of_science", "avery_index"]
    else:
        return ["semantic_scholar"]
```

Different gaps need different sources.

### Pearl's Critique

**On causal_identification gap:**

The plan correctly identifies beliefs needing experimental evidence. But it doesn't distinguish between:
1. "We need RCT confirmation" (gold standard but expensive)
2. "We need quasi-experimental evidence" (often sufficient)
3. "We need better observational with careful controls" (adequate for many claims)

**Recommendation:** Stratify causal evidence needs:
```python
class CausalEvidenceNeed(Enum):
    OBSERVATIONAL_CONTROLLED = 1  # Observational with confound control
    QUASI_EXPERIMENTAL = 2  # Natural experiments, RDD
    EXPERIMENTAL = 3  # RCT required
```

This focuses search on what's actually findable (most causal questions don't have RCTs).

### Bates' Critique

**On cross-field vocabulary:**

20 concepts is a good start, but the selection criteria aren't explicit. Which 20? Why those?

**Recommendation:** Prioritize by:
1. Frequency in current web (most-used concepts first)
2. Cross-field translation difficulty (easy translations are less valuable)
3. Gap prevalence (concepts appearing in many gaps)

Document the selection rationale so it can be revisited.

### Cartwright's Critique

**On null result search:**

Searching for "no effect" + "no significant" will find some null results, but many null results use different language:
- "We failed to replicate..."
- "The effect was not robust..."
- "Results did not reach significance..."
- "Contrary to hypotheses..."

**Recommendation:** Build a null result vocabulary:
```yaml
null_result_indicators:
  direct: ["no effect", "no significant", "null result"]
  replication_failure: ["failed to replicate", "did not replicate", "replication failure"]
  hedged: ["not robust", "did not reach significance", "marginally significant"]
  contrary: ["contrary to hypotheses", "unexpected null", "surprising absence"]
```

Use all categories, weighted by reliability.

### Simon's Critique

**On epsilon-greedy:**

Epsilon = 0.2 means 20% random exploration. But early in the system's life, you know nothing—exploration should be higher. Later, once you have data, exploitation should dominate.

**Recommendation:** Decay epsilon over time:
```python
def current_epsilon(total_searches: int, initial_epsilon: float = 0.3, decay: float = 0.99) -> float:
    """Epsilon decays as experience accumulates."""
    return max(initial_epsilon * (decay ** total_searches), 0.05)
```

Start at 30% exploration, decay to 5% minimum.

### Decision Points to Add:
1. What's the stopping rule for search (when is "enough" papers found)?
2. How to handle duplicate papers across sources?
3. What's the minimum VOI threshold for pursuing a gap?

---

## Part V: Cross-TODO Integration Critique

### Lampson's Integration Concerns

The three TODOs interact but the interfaces aren't specified:

1. **TODO 1 → TODO 2:** Credibility flags should be explainable. If a paper is rejected, user may ask "Why?" The interpretive system needs access to credibility reasoning.

2. **TODO 2 → TODO 3:** Explanations may reveal gaps ("Why is credence only 55%?" → "Because we lack replication"). The interpretive system should feed gaps to search.

3. **TODO 3 → TODO 1:** Papers acquired by search will be evaluated by credibility testing. The search system should anticipate credibility requirements.

**Recommendation:** Define the integration interfaces now:
```python
# TODO 1 produces:
CredibilityReport.to_explanation_context() -> ExplanationContext

# TODO 2 produces:
ExplanationResult.identified_gaps() -> List[EpistemicGap]

# TODO 3 produces:
AcquiredPaper.expected_credibility_profile() -> Dict[str, float]
```

### Sequencing Recommendation

The plans assume parallel development, but there are dependencies:

1. **Build TODO 1 first (Sprints B-D):** Credibility testing is foundational. Without it, you can't trust anything you add to the web.

2. **Build TODO 2 second (Sprints E-G):** Once you can trust additions, you need to explain them. Also, vocabulary work in TODO 2 informs TODO 3.

3. **Build TODO 3 last (Sprints H-K):** Search depends on knowing what gaps exist (needs populated web), what terms to use (needs vocabulary bridge), and what quality to expect (needs credibility baselines).

**Revised Timeline:**
```
Sprints B-D: TODO 1 (Credibility Testing)
Sprints E-G: TODO 2 (Interpretive Intelligence)
Sprints H-K: TODO 3 (VOI Search)
Sprint L: Integration testing
```

---

## Part VI: Consolidated Recommendations

### Must Fix Before Implementation

1. **Simplify enums** — Start with ≤3 categories each; expand based on data
2. **Define minimal interfaces** — 3-5 fields, not 10+
3. **Specify concurrency model** — Recommend snapshot isolation
4. **Unify feedback storage** — Single store, not three
5. **Document failure modes** — Three most likely per component
6. **Distinguish tests from metrics** — Unit/integration/system tests separate from evaluation

### Should Fix During Sprint B

1. **TODO 1:** Add study design strength gradations (Pearl)
2. **TODO 1:** Add scope distance metric (Cartwright)
3. **TODO 1:** Add subtle failure cases (Mayo)
4. **TODO 2:** Add question clarification (Wilson)
5. **TODO 2:** Separate detail level from expertise level (Simon)
6. **TODO 3:** Add source selection logic (Giles)
7. **TODO 3:** Add epsilon decay (Simon)

### Consider for Later Sprints

1. Temporal markers in vocabulary (Bates)
2. Specificity levels for recommendations (Kaplan)
3. Stratified causal evidence needs (Pearl)
4. Null result vocabulary expansion (Cartwright)

---

## Part VII: Revised Success Criteria

Based on the critique, add these criteria:

### TODO 1: Credibility Testing
- [ ] System handles missing metadata gracefully
- [ ] Thresholds documented with calibration procedure
- [ ] Subtle failure cases detected (not just obvious ones)
- [ ] Failure modes documented and handled

### TODO 2: Interpretive Intelligence
- [ ] Uncertain classifications trigger clarification
- [ ] Vocabulary bridge has update procedure
- [ ] Detail and expertise levels are separate
- [ ] Integration with credibility explanations

### TODO 3: VOI Search
- [ ] Source selection varies by gap type
- [ ] Epsilon decays with experience
- [ ] Stopping rule defined
- [ ] Integration with credibility expectations

---

*Critique complete*
*Next step: Phase D — Replan based on critique*
