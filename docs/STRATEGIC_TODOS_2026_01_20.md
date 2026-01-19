# Strategic Development Initiatives: Three Major TODOs

**Date:** January 20, 2026
**Status:** Planning Phase
**Owner:** David Kirsh, UCSD Cognitive Science

---

## Overview

This document defines three substantial development initiatives for Article Eater Post-Quinean. Each initiative follows our established methodology:

```
a) Expert consultation → b) Implementation plan → c) Plan critique (team + world-class designer)
→ d) Replan → e) Implement → f) Collect decision points → g) Sprint-end expert review
→ h) Incorporate recommendations → i) Next sprint
```

These initiatives address fundamental capabilities that distinguish the Quinean web from simpler knowledge systems:

1. **Credibility Testing** — Continuous validation that the system behaves epistemically sound
2. **Interpretive Intelligence** — Harnessing explicit structure for user understanding
3. **VOI-Driven Search** — Using epistemic gaps to guide literature acquisition

---

## TODO 1: Credibility Testing Method

### 1.1 Problem Statement

When a new article is added to the web, the system updates beliefs, creates constraints, and seeks equilibrium. But how do we know these changes are *credible*? A human expert reviewing the same article would have intuitions about:

- Whether the extracted beliefs are reasonable
- Whether the credence assignments are appropriate
- Whether the constraint relationships make sense
- Whether the equilibrium shift is proportionate to the evidence

We need a testing method that can evaluate credibility *automatically* and *continuously*, without requiring human review of every article.

### 1.2 Key Questions for Expert Panel

**For Dr. Judea Pearl (Causal Inference):**
- What causal consistency checks should we apply when new evidence enters the system?
- How do we detect when a new article creates causal cycles or implausible dependencies?
- What does "credible update" mean in a causal graphical model?

**For Dr. Nancy Cartwright (Philosophy of Science):**
- What epistemic norms should govern belief revision magnitude?
- When is a large credence shift warranted vs. suspicious?
- How do we distinguish legitimate paradigm-challenging evidence from extraction errors?

**For Dr. Herbert Simon (Bounded Rationality):**
- What satisficing criteria make sense for automated credibility assessment?
- How do we balance thoroughness against computational cost?
- What "red flags" should trigger human review?

**For Dr. Marcia Bates (Information Science):**
- How do we validate that extracted concepts map correctly to the taxonomy?
- What metadata consistency checks matter most?
- How do we detect systematic extraction drift over time?

**For Dr. Rachel Kaplan (Environmental Psychology):**
- What domain-specific sanity checks apply to CNfA findings?
- What effect sizes are plausible vs. implausible for environmental interventions?
- What methodological red flags are common in this literature?

**Additional Expert — Dr. Deborah Mayo (Philosophy of Statistics):**
- What severe testing criteria should the system apply to itself?
- How do we operationalize "the system passed a severe test"?
- What error-statistical framework fits coherentist updating?

### 1.3 Proposed Credibility Dimensions

Based on preliminary analysis, credibility testing should evaluate:

**A. Extraction Credibility**
- Do extracted beliefs have appropriate content for the paper type?
- Are credence values within reasonable ranges for the evidence quality?
- Do scope conditions match what the paper actually studied?

**B. Constraint Credibility**
- Are newly created constraints semantically appropriate?
- Do constraint strengths reflect the actual evidential relationship?
- Are there unexpected constraint patterns (e.g., self-loops, cycles)?

**C. Update Credibility**
- Is the magnitude of credence change proportionate to evidence strength?
- Do changes propagate reasonably through the constraint network?
- Does equilibrium converge in reasonable iterations?

**D. Coherence Credibility**
- Does global coherence improve or stay stable (not degrade spuriously)?
- Are new tensions genuine or artifacts of extraction errors?
- Do stub counts change appropriately?

### 1.4 Implementation Sketch

```python
# Location: src/services/credibility_testing.py

class CredibilityReport:
    """Report from evaluating article addition credibility."""
    article_id: str
    timestamp: datetime

    # Dimension scores (0-1, higher = more credible)
    extraction_score: float
    constraint_score: float
    update_score: float
    coherence_score: float

    # Aggregate
    overall_credibility: float

    # Flags
    red_flags: List[str]
    requires_human_review: bool

    # Detailed diagnostics
    diagnostics: Dict[str, Any]

class CredibilityTester:
    """Evaluates credibility of article addition to the web."""

    def __init__(self, web: WebOfBelief, config: CredibilityConfig):
        self.web = web
        self.config = config
        self.baseline_metrics = self._compute_baseline()

    def evaluate_article_addition(
        self,
        article_id: str,
        pre_state: WebState,
        post_state: WebState,
        extracted_beliefs: List[Belief],
        extracted_constraints: List[Constraint]
    ) -> CredibilityReport:
        """
        Evaluate credibility of adding one article.

        Called AFTER extraction but BEFORE committing to persistent state.
        Returns report; caller decides whether to accept, reject, or flag.
        """
        ...

    def _check_extraction_credibility(self, ...) -> Tuple[float, List[str]]:
        """Check extracted beliefs and constraints for sanity."""
        ...

    def _check_update_credibility(self, ...) -> Tuple[float, List[str]]:
        """Check that credence updates are proportionate."""
        ...

    def _check_coherence_credibility(self, ...) -> Tuple[float, List[str]]:
        """Check that global coherence behaves reasonably."""
        ...
```

### 1.5 Cost Considerations

**Goal:** Minimize or eliminate LLM API calls for routine credibility testing.

**Approach:**
- Use statistical/heuristic checks for most evaluations
- Pre-compute expected ranges from Gold Standard corpus
- Reserve LLM calls for "borderline" cases flagged by heuristics
- If LLM needed: estimate ~$0.01-0.05 per article (using Haiku or equivalent)

**Fallback:** If LLM review necessary, batch flagged articles and review weekly.

### 1.6 Success Criteria

The credibility testing method succeeds if:
- It catches >90% of extraction errors that a human would catch
- False positive rate (flagging good articles) is <10%
- Runs in <5 seconds per article without API calls
- Produces interpretable reports that explain why flags were raised

### 1.7 Sprint Structure

**Sprint A:** Expert consultation, baseline metric design
**Sprint B:** Implement extraction and constraint credibility checks
**Sprint C:** Implement update and coherence credibility checks
**Sprint D:** Integration testing with Gold Standard corpus
**Sprint E:** Calibration and threshold tuning

---

## TODO 2: Interpretive Intelligence Module

### 2.1 Problem Statement

The Quinean web contains rich epistemic structure—beliefs at multiple levels, constraints with varying strengths, bridge warrants across theories, scope conditions, tensions, and stubs. But this structure is currently accessible only through programmatic queries.

Users need an *interpretive layer* that can answer natural questions by reasoning over the web's structure:

- "Why does the system believe plants reduce stress?"
- "How reliable is this belief? What could undermine it?"
- "What theories support this? Do any contradict it?"
- "What don't we know that would strengthen or weaken this?"

This is fundamentally different from RAG: we're not retrieving passages, we're *reasoning over explicit epistemic structure*.

### 2.2 Key Questions for Expert Panel

**For Dr. Judea Pearl:**
- How do we explain causal chains through the web in user-friendly terms?
- What causal counterfactuals can we support? ("If we rejected ART, what would change?")
- How do we communicate causal uncertainty vs. evidential uncertainty?

**For Dr. Nancy Cartwright:**
- How do we explain scope limitations without overwhelming users?
- What's the right way to communicate "this might not apply to your context"?
- How do we surface auxiliary assumptions that users might not realize exist?

**For Dr. Herbert Simon:**
- What level of explanation detail is appropriate for different user types?
- How do we chunk complex epistemic structures into digestible explanations?
- What "explanation templates" would serve most queries?

**For Dr. Marcia Bates:**
- How do we organize interpretive output for scannability?
- What visualization aids would help users understand web structure?
- How do we support both quick answers and deep dives?

**For Dr. Rachel Kaplan:**
- What domain-specific explanatory frames resonate with CNfA practitioners?
- How do we translate epistemic concepts (credence, coherence) into practical terms?
- What misconceptions do practitioners commonly have that we should address?

**Additional Expert — Dr. Deirdre Wilson (Pragmatics/Relevance Theory):**
- How do we determine what's relevant to include in an explanation?
- How do we structure explanations for optimal cognitive effect?
- What implicatures should we avoid in interpretive output?

### 2.3 Proposed Interpretive Capabilities

**A. Rule Explanation**
```
User: "Explain the rule about nature views and stress recovery."

System:
BELIEF: Natural views support stress recovery in hospital settings
CREDENCE: 0.75 (moderate-high confidence)
UNCERTAINTY: ±0.15 (well-constrained)

EVIDENCE BASE:
- Primary: Ulrich (1984) - surgical patients, nature vs brick wall views
- Supporting: 3 additional studies in healthcare settings
- Scope: Hospital/healthcare settings, physiological + behavioral outcomes

THEORETICAL BACKING:
- Stress Recovery Theory (SRT) - primary theoretical home
- Bridge to ART via functional equivalence (confidence: 0.50)

POTENTIAL VULNERABILITIES:
- Limited to healthcare settings (scope boundary)
- Mechanism (SRT) not directly tested in original studies
- Alternative explanation: Distraction rather than restoration
```

**B. Interaction Analysis**
```
User: "What interacts with the ceiling height effect on creativity?"

System:
KNOWN INTERACTIONS:
- Task type: Effect stronger for divergent vs convergent thinking
- Cultural background: Western samples show larger effects
- Baseline arousal: Effect may reverse under high stress

SUSPECTED BUT UNCONFIRMED:
- Individual differences in spatial processing
- Room proportions (height-to-width ratio)
- Lighting conditions

THEORETICAL PREDICTIONS (not yet tested):
- ART predicts interaction with attentional fatigue
- Prospect-Refuge predicts interaction with enclosure on other axes
```

**C. Credibility Assessment**
```
User: "How reliable is the biophilia effect?"

System:
OVERALL ASSESSMENT: Moderately reliable (0.68) with significant uncertainty (±0.20)

STRENGTHS:
- Consistent direction across 12+ studies
- Multiple operational measures converge
- Strong theoretical backing (Wilson, Kellert)

WEAKNESSES:
- Publication bias likely (few null results)
- Mechanism contested (innate vs learned)
- Effect sizes vary widely (d = 0.2 to 0.8)

CONTINGENCIES (things that could change this):
- Large pre-registered replication failure
- Demonstration of confounding (novelty, not nature)
- Cross-cultural studies showing reversal
```

**D. Contingency Mapping**
```
User: "What assumptions is this belief resting on?"

System:
DIRECT ASSUMPTIONS:
1. Ulrich (1984) methodology was sound
2. Hospital setting results generalize to other healthcare contexts
3. Self-report and physiological measures capture same construct

BRIDGING ASSUMPTIONS:
1. SRT mechanism (psychophysiological stress recovery) is valid
2. Functional bridge to ART is appropriate
3. Natural views category is coherent (trees, water, etc. grouped correctly)

THEORETICAL ASSUMPTIONS:
1. Stress is a meaningful construct
2. Environmental features can causally affect stress
3. Effects are systematic enough to study scientifically

FRAGILITY ANALYSIS:
- If assumption #1 fails: Credence drops to 0.45
- If bridging assumption #2 fails: Loses ART-derived support
- If theoretical assumption #1 fails: Entire research program collapses
```

### 2.4 Implementation Sketch

```python
# Location: src/services/interpretive_intelligence.py

class InterpretiveEngine:
    """Generates human-readable interpretations of web structure."""

    def __init__(self, web: WebOfBelief, config: InterpretiveConfig):
        self.web = web
        self.config = config
        self.templates = load_explanation_templates()

    def explain_belief(
        self,
        belief_id: str,
        depth: Literal["summary", "standard", "deep"] = "standard",
        audience: Literal["researcher", "practitioner", "student"] = "researcher"
    ) -> BeliefExplanation:
        """Generate explanation of a single belief."""
        ...

    def analyze_interactions(
        self,
        belief_id: str,
        interaction_types: List[str] = ["empirical", "theoretical", "suspected"]
    ) -> InteractionAnalysis:
        """Identify known and suspected interactions."""
        ...

    def assess_credibility(
        self,
        belief_id: str,
        include_contingencies: bool = True
    ) -> CredibilityAssessment:
        """Comprehensive credibility assessment with vulnerabilities."""
        ...

    def map_contingencies(
        self,
        belief_id: str,
        depth: int = 3  # How many levels of assumptions to trace
    ) -> ContingencyMap:
        """Trace assumptions the belief rests on."""
        ...

    def answer_question(
        self,
        question: str,
        context: Optional[Dict] = None
    ) -> InterpretiveResponse:
        """
        General question-answering over the web.

        Uses template matching for common question types;
        falls back to structured traversal for novel queries.
        """
        ...
```

### 2.5 Cost Considerations

**Goal:** Run most interpretations without LLM API calls.

**Approach:**
- Pre-define explanation templates for common query types
- Use rule-based natural language generation for structured output
- Traverse web structure algorithmically (not via LLM reasoning)
- Reserve LLM for: (a) novel question parsing, (b) natural language polishing

**Estimated costs:**
- Template-based responses: $0 (no API)
- LLM-assisted parsing: ~$0.01 per query (Haiku)
- Full LLM generation: ~$0.05 per query (Sonnet) — use sparingly

### 2.6 Success Criteria

The interpretive module succeeds if:
- Users report understanding increases vs. raw data access
- Domain experts validate explanations as accurate
- Contingency maps identify assumptions experts would identify
- 80%+ of queries answered without LLM calls

### 2.7 Sprint Structure

**Sprint A:** Expert consultation, explanation template design
**Sprint B:** Implement belief explanation and evidence tracing
**Sprint C:** Implement interaction analysis and credibility assessment
**Sprint D:** Implement contingency mapping and fragility analysis
**Sprint E:** Natural language generation and user testing

---

## TODO 3: VOI-Driven Article Search

### 3.1 Problem Statement

The current article search is fundamentally misaligned with the web's epistemic needs:

- Standard keyword search finds obvious CNfA papers
- But the web needs articles that address *specific epistemic gaps*:
  - Papers testing contested mechanisms
  - Papers from adjacent fields with relevant bridging evidence
  - Papers with null results that could calibrate credences
  - Papers from different populations that could map scope boundaries

A good VOI metric identifies *what information we need*. We need a system that translates these needs into *targeted search queries* that can find the right literature.

### 3.2 Key Questions for Expert Panel

**For Dr. Judea Pearl:**
- How do we identify which causal parameters most need empirical constraint?
- What search strategies find papers that test causal mechanisms?
- How do we search for instrumental variable studies in adjacent domains?

**For Dr. Nancy Cartwright:**
- How do we search for studies that test scope boundaries?
- What query patterns find "mechanism" papers vs "effect" papers?
- How do we find philosophical/theoretical papers that bear on our assumptions?

**For Dr. Herbert Simon:**
- How do we prioritize which gaps to search for first?
- What satisficing criteria determine "good enough" literature coverage?
- How do we balance breadth vs depth in literature acquisition?

**For Dr. Marcia Bates:**
- What berrypicking strategies work for finding non-obvious relevant literature?
- How do we construct queries that escape the "CNfA bubble"?
- What citation chaining and bibliometric methods should we employ?

**For Dr. Rachel Kaplan:**
- What adjacent fields (neuroscience, architecture, psychology) have relevant findings?
- What terminology differences make cross-field search difficult?
- Which journals outside CNfA publish relevant work?

**Additional Expert — Dr. C. Lee Giles (Information Retrieval/CiteSeer):**
- What query expansion techniques work for scientific literature?
- How do we leverage citation networks for gap-directed search?
- What semantic similarity methods help find conceptually related papers?

### 3.3 Proposed VOI-Driven Search Capabilities

**A. Gap-Directed Query Generation**
```python
# Input: Epistemic gap identified by VOI analysis
gap = {
    "type": "scope_boundary",
    "belief": "nature_views_reduce_stress",
    "missing_scope": "children",
    "current_scope": "adults",
    "voi_score": 0.73
}

# Output: Targeted search queries
queries = [
    '"nature views" AND (children OR pediatric OR "young people") AND stress',
    '"restorative environment" AND "child development"',
    'biophilia AND (school OR classroom) AND wellbeing',
    # Citation-based
    'citing:ulrich1984 AND (children OR pediatric)',
    # Adjacent field
    '"environmental psychology" AND children AND "natural environment"'
]
```

**B. Mechanism-Testing Article Search**
```python
# Input: Uncertain mechanism
mechanism = {
    "name": "attention_restoration_mechanism",
    "theory": "ART",
    "confidence": 0.55,
    "tests_needed": ["direct_attention_measurement", "fatigue_manipulation"]
}

# Output: Queries for mechanism evidence
queries = [
    '"attention restoration" AND (fMRI OR EEG OR "cognitive load")',
    '"directed attention fatigue" AND (measurement OR assessment)',
    'Kaplan AND "cognitive restoration" AND experiment',
    # Negative evidence
    '"attention restoration theory" AND (critique OR "failed to replicate")'
]
```

**C. Bridge Warrant Evidence Search**
```python
# Input: Uncertain bridge warrant
bridge = {
    "source_theory": "SRT",
    "target_theory": "ART",
    "bridge_type": "functional",
    "confidence": 0.50,
    "evidence_needed": "covariance_data"
}

# Output: Queries for bridge evidence
queries = [
    '"stress recovery" AND "attention restoration" AND (compare OR both)',
    'Ulrich AND Kaplan AND (nature OR restorative)',
    '"psychophysiological" AND "cognitive" AND "natural environment"',
    # Studies measuring both
    'cortisol AND attention AND nature'
]
```

**D. High-Level Theory Evidence Search**
```python
# Input: Theory needing support/challenge
theory = {
    "name": "biophilia_hypothesis",
    "credence": 0.60,
    "uncertainty": 0.25,
    "challenge_needed": True  # High uncertainty suggests we need challenge evidence
}

# Output: Balanced search for support and challenge
support_queries = [
    '"biophilia hypothesis" AND (evidence OR support OR confirmed)',
    'Wilson AND biophilia AND (study OR experiment)',
    '"innate" AND nature AND preference AND human'
]
challenge_queries = [
    '"biophilia hypothesis" AND (critique OR challenge OR "not supported")',
    '"learned preference" AND nature AND (cultural OR social)',
    '"biophilia" AND ("alternative explanation" OR confound)'
]
```

### 3.4 Implementation Sketch

```python
# Location: src/services/voi_search.py

class VOISearchEngine:
    """Translates epistemic gaps into literature search queries."""

    def __init__(self, web: WebOfBelief, voi_analyzer: VOIAnalyzer):
        self.web = web
        self.voi = voi_analyzer
        self.query_templates = load_query_templates()
        self.field_vocabulary = load_field_vocabulary()  # Cross-field term mappings

    def identify_search_priorities(
        self,
        max_priorities: int = 10
    ) -> List[SearchPriority]:
        """
        Analyze web and return prioritized list of literature needs.

        Combines VOI scores with feasibility estimates.
        """
        ...

    def generate_queries(
        self,
        priority: SearchPriority,
        query_types: List[str] = ["keyword", "citation", "semantic"]
    ) -> List[SearchQuery]:
        """Generate diverse queries for a single priority."""
        ...

    def expand_query(
        self,
        base_query: str,
        expansion_methods: List[str] = ["synonyms", "related_terms", "field_variants"]
    ) -> List[str]:
        """Expand query to catch relevant papers with different terminology."""
        ...

    def search_and_rank(
        self,
        queries: List[SearchQuery],
        sources: List[str] = ["semantic_scholar", "pubmed", "google_scholar"],
        max_results: int = 50
    ) -> List[RankedArticle]:
        """
        Execute searches and rank results by relevance to epistemic need.

        Ranking considers:
        - Query match quality
        - Citation metrics
        - Recency
        - Journal quality
        - Predicted information gain
        """
        ...

    def generate_acquisition_report(
        self,
        search_results: List[RankedArticle],
        priorities: List[SearchPriority]
    ) -> AcquisitionReport:
        """
        Generate report recommending which articles to acquire.

        Includes:
        - Top recommendations per priority
        - Expected VOI if acquired
        - Estimated acquisition effort
        """
        ...

class SearchPriority:
    """A prioritized epistemic need for literature search."""
    gap_type: Literal["scope", "mechanism", "bridge", "theory", "replication", "null"]
    description: str
    voi_score: float
    feasibility: float  # Estimate of finding relevant literature
    affected_beliefs: List[str]
    current_evidence: int  # How many papers currently address this

class SearchQuery:
    """A structured search query."""
    query_string: str
    query_type: Literal["keyword", "citation", "semantic", "author"]
    target_sources: List[str]
    expected_precision: float
    expected_recall: float
```

### 3.5 Cross-Field Vocabulary Mapping

A critical component: mapping CNfA concepts to terminology in adjacent fields.

```yaml
# Location: contracts/vocab/cross_field_vocabulary.yaml

stress_recovery:
  cnfa_terms: ["stress recovery", "restorative environment", "nature restoration"]
  psychology_terms: ["stress reduction", "psychophysiological recovery", "relaxation response"]
  neuroscience_terms: ["autonomic regulation", "HPA axis", "parasympathetic activation"]
  architecture_terms: ["healing environment", "therapeutic design", "salutogenic"]

attention_restoration:
  cnfa_terms: ["attention restoration", "directed attention fatigue", "soft fascination"]
  psychology_terms: ["executive function recovery", "cognitive restoration", "mental fatigue"]
  neuroscience_terms: ["prefrontal recovery", "attentional control", "cognitive load"]
  education_terms: ["concentration", "focus recovery", "learning environment"]
```

### 3.6 Cost Considerations

**API costs:**
- Semantic Scholar API: Free (rate limited)
- PubMed API: Free
- Google Scholar: Scraping (problematic) or SerpAPI (~$0.01/query)
- Semantic similarity: Local embeddings (free) or API (~$0.001/query)

**LLM costs for query generation:**
- Template-based: $0
- LLM-assisted expansion: ~$0.02 per priority (Haiku)

**Estimated total:** ~$0.05-0.10 per search priority, assuming 5-10 queries each.

### 3.7 Success Criteria

The VOI-driven search succeeds if:
- Precision improves 2x over keyword-only search
- Recall of relevant adjacent-field papers improves 5x
- At least 30% of recommendations are papers we wouldn't have found otherwise
- Acquired papers measurably reduce web uncertainty

### 3.8 Sprint Structure

**Sprint A:** Expert consultation, gap taxonomy and query template design
**Sprint B:** Implement gap identification and basic query generation
**Sprint C:** Implement cross-field vocabulary and query expansion
**Sprint D:** Implement multi-source search and ranking
**Sprint E:** Integration with VOI analyzer and acquisition reporting

---

## Cross-Cutting Concerns

### Decision Point Collection

During implementation of all three TODOs, we will collect decision points in a structured format:

```yaml
# Location: docs/decision_points/SPRINT_X_DECISIONS.yaml

decisions:
  - id: "CRED-001"
    sprint: "Credibility Testing Sprint B"
    date: "2026-02-XX"
    topic: "Credence change threshold for flagging"
    options:
      - "Fixed threshold (e.g., >0.2 change flags for review)"
      - "Adaptive threshold based on evidence strength"
      - "Percentile-based (top 5% largest changes flagged)"
    chosen: "TBD"
    rationale: "TBD"
    expert_review_needed: true

  - id: "INTERP-001"
    sprint: "Interpretive Intelligence Sprint A"
    topic: "Explanation depth default"
    ...
```

### Expert Review Protocol

At each sprint end:

1. **Compile decision points** from the sprint
2. **Write context document** explaining the system state and decisions made
3. **Generate expert prompt** asking for review and recommendations
4. **Collect responses** from simulated expert panel
5. **Synthesize recommendations** into actionable implementation changes
6. **Document in** `docs/expert_reviews/SPRINT_X_REVIEW.md`

### Integration Points

The three TODOs have natural integration points:

```
                    ┌─────────────────────┐
                    │   Web of Belief     │
                    └─────────┬───────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  Credibility  │    │  Interpretive │    │  VOI-Driven   │
│    Testing    │    │  Intelligence │    │    Search     │
└───────┬───────┘    └───────┬───────┘    └───────┬───────┘
        │                     │                     │
        │    "Is this        │   "Explain          │   "What literature
        │     update         │    this             │    would help?"
        │     credible?"     │    belief"          │
        │                     │                     │
        └─────────────────────┴─────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │   Better Knowledge  │
                    │   Better Decisions  │
                    └─────────────────────┘
```

- **Credibility Testing → Interpretive:** If an article fails credibility, the interpretive module can explain why
- **Interpretive → VOI Search:** When explaining contingencies, identify gaps that search should address
- **VOI Search → Credibility Testing:** New articles from search need credibility evaluation
- **All three → Web:** Each improves the web's quality and utility

---

## Timeline Overview

| Month | TODO 1: Credibility | TODO 2: Interpretive | TODO 3: VOI Search |
|-------|--------------------|--------------------|-------------------|
| Feb 2026 | Sprint A: Expert consultation | — | — |
| Mar 2026 | Sprints B-C: Core implementation | Sprint A: Expert consultation | — |
| Apr 2026 | Sprints D-E: Testing & calibration | Sprints B-C: Core implementation | Sprint A: Expert consultation |
| May 2026 | Integration & refinement | Sprints D-E: NLG & testing | Sprints B-C: Core implementation |
| Jun 2026 | — | Integration & refinement | Sprints D-E: Search & ranking |
| Jul 2026 | — | — | Integration & refinement |

**Total estimated duration:** 6 months for all three initiatives, with overlap.

---

## Next Steps

1. **Immediate:** Review this document and refine priorities
2. **Week 1:** Begin TODO 1 Sprint A — convene expert panel on credibility testing
3. **Ongoing:** Update this document as sprints complete and plans evolve

---

*Document created: January 20, 2026*
*Last updated: January 20, 2026*
