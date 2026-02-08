# Panel P-TD: Technical Debt Implementation Review

**Date**: February 8, 2026
**Panel ID**: P-TD
**Scope**: Implementation strategies for technical debt items TD-1 through TD-4
**Status**: CONSULTATION COMPLETE

---

## Panel Composition

### Core Panel Members

| Panelist | Affiliation | Expertise | Primary Focus |
|----------|-------------|-----------|---------------|
| **Paul Thagard** | U. Waterloo | Coherence theory, computational epistemology | TD-1 |
| **Herbert Simon** | CMU (historical) | Bounded rationality, satisficing, system design | TD-1 |
| **Nancy Cartwright** | Durham/UCSD | Capacities, scope conditions, philosophy of science | TD-3 |
| **Deborah Mayo** | Virginia Tech | Statistical methodology, error statistics | TD-3 |
| **Marcia Bates** | UCLA | Information science, knowledge organization | TD-2 |

### Computational/NLP Experts

| Panelist | Affiliation | Expertise | Primary Focus |
|----------|-------------|-----------|---------------|
| **James Pustejovsky** | Brandeis | TimeML, temporal semantics, event structure | TD-4 |
| **Christopher Manning** | Stanford | NLP, information extraction, deep learning for text | TD-2, TD-3, TD-4 |
| **Jon Kleinberg** | Cornell | Algorithm design, network analysis, graph algorithms | TD-1 |
| **Marti Hearst** | UC Berkeley | Text mining, entity extraction, search interfaces | TD-2, TD-3 |

---

## Technical Debt Items Under Review

| ID | Issue | Current State | Impact |
|----|-------|---------------|--------|
| TD-1 | Coherence computation O(n²) | Pairwise belief comparison | Scales poorly beyond ~500 beliefs |
| TD-2 | Theory inference accuracy | Keyword matching | ~60% accuracy, many false positives |
| TD-3 | Scope metadata missing | ScopeConditions class exists but underpopulated | Findings lack boundary conditions |
| TD-4 | Temporal parsing | Not implemented | "After 20 minutes" unparsed |

---

## TD-1: Coherence Computation Scalability

### Current Implementation

```python
# web_of_belief.py - current approach
def _compute_coherence_score(self) -> float:
    total = 0.0
    count = 0
    for b1 in self.beliefs.values():
        for b2 in self.beliefs.values():
            if b1.id != b2.id:
                total += self._pairwise_coherence(b1, b2)
                count += 1
    return total / count if count > 0 else 0.0
```

This is O(n²) where n = number of beliefs. At 1000 beliefs, that's ~1M comparisons.

### Panel Discussion

---

**Dr. Paul Thagard** (Coherence Theory):

The key insight from my ECHO system is that **not all beliefs need to cohere with all others**. Coherence is fundamentally *local*—a belief about stress recovery doesn't need to cohere with a belief about wayfinding unless they share theoretical commitments.

**Recommendation**: Implement **constraint-based coherence** where:
1. Beliefs only cohere/incohere with beliefs they're *connected* to
2. Connection is via shared theories, shared constructs, or explicit relations
3. Global coherence emerges from propagation, not exhaustive comparison

```python
# Proposed: constraint network approach
def _compute_coherence_score(self) -> float:
    # Only compute for connected belief pairs
    coherence_sum = 0.0
    for constraint in self.coherence_constraints:
        b1, b2, weight = constraint
        coherence_sum += weight * self._pairwise_coherence(b1, b2)
    return coherence_sum / len(self.coherence_constraints)
```

This reduces to O(E) where E = number of edges, typically << n².

---

**Dr. Herbert Simon** (Bounded Rationality):

The question isn't "how do we compute perfect coherence?" but "how do we compute *good enough* coherence efficiently?" This is satisficing.

**Recommendation**: Accept approximation with known error bounds:
1. **Sampling**: Compute coherence on random sample of pairs, estimate global
2. **Hierarchical**: Compute within-cluster coherence, then between-cluster
3. **Lazy evaluation**: Only recompute when beliefs change

For Article Eater's scale (likely <10,000 beliefs per corpus), hierarchical with theory-based clusters is ideal:

```python
# Cluster by theory, compute within-cluster coherence (fast)
# Then compute between-cluster coherence (few clusters)
def _hierarchical_coherence(self) -> float:
    within_scores = []
    for theory_id, beliefs in self._beliefs_by_theory().items():
        within_scores.append(self._cluster_coherence(beliefs))

    between_score = self._between_cluster_coherence()

    return 0.7 * mean(within_scores) + 0.3 * between_score
```

---

**Dr. Jon Kleinberg** (Algorithm Design):

From a graph algorithms perspective, coherence is computing aggregate edge weights in a weighted graph. Several proven techniques apply:

**Recommendation**: Use **locality-sensitive hashing (LSH)** for approximate nearest neighbors:

1. Embed beliefs into vector space (using their construct signatures)
2. Use LSH to find approximately-coherent pairs in O(n)
3. Compute exact coherence only for candidate pairs

Alternatively, **spectral methods** can approximate global coherence:
- Coherence matrix eigenvalues give global coherence measure
- Power iteration finds dominant eigenvalue in O(n) per iteration
- Usually converges in 10-20 iterations

```python
# Spectral coherence approximation
import numpy as np
from scipy.sparse.linalg import eigsh

def _spectral_coherence(self, k=5) -> float:
    # Build sparse coherence matrix (only connected pairs)
    C = self._build_sparse_coherence_matrix()

    # Top-k eigenvalues capture global coherence structure
    eigenvalues, _ = eigsh(C, k=k, which='LM')

    # Normalized sum of positive eigenvalues
    return sum(max(0, ev) for ev in eigenvalues) / k
```

---

### TD-1 Synthesis

| Approach | Complexity | Accuracy | Best For |
|----------|------------|----------|----------|
| Constraint network (Thagard) | O(E) | Exact for connected pairs | Sparse belief networks |
| Hierarchical (Simon) | O(k·m² + k²) | ~95% | Theory-clustered beliefs |
| LSH approximation (Kleinberg) | O(n) | ~90% | Large uniform belief sets |
| Spectral (Kleinberg) | O(n·iter) | ~85% global | Quick global estimate |

**Panel Verdict**: Implement **hierarchical with constraint network fallback**:
1. Primary: Cluster by theory, compute within/between coherence
2. Constraint network for explicit coherence/incoherence relations
3. Cache aggressively, invalidate on belief changes
4. Target: <100ms for 5000 beliefs

---

## TD-2: Theory Inference Accuracy

### Current Implementation

```python
# extraction_to_web.py - current approach
THEORY_KEYWORDS = {
    "SRT": ["stress", "recovery", "ulrich", "restorative"],
    "ART": ["attention", "kaplan", "directed attention", "fascination"],
    ...
}

def infer_theory(text: str) -> Optional[str]:
    text_lower = text.lower()
    for theory, keywords in THEORY_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return theory
    return None
```

Problems:
- "Mechanical stress" → SRT (false positive)
- "Attention to detail" → ART (false positive)
- Novel terminology missed

### Panel Discussion

---

**Dr. Marcia Bates** (Information Science):

This is a classic **vocabulary problem**. The same concept has multiple expressions, and the same expression has multiple meanings. Keyword matching fails on both counts.

**Recommendation**: Build a **semantic vocabulary bridge**:

1. **Controlled vocabulary** with preferred terms and synonyms
2. **Disambiguation rules** based on context (co-occurring terms)
3. **Hierarchical classification**: First domain, then theory within domain

```yaml
# vocabulary_bridge.yaml
SRT:
  preferred_term: "Stress Recovery Theory"
  requires_context:
    - must_include_any: ["nature", "environment", "greenspace", "restoration"]
    - must_exclude: ["mechanical", "engineering", "material"]
  synonyms:
    - "psychophysiological stress recovery"
    - "Ulrich's stress recovery"
    - "restorative environment"
```

---

**Dr. Christopher Manning** (NLP):

Modern NLP offers better solutions than keyword matching:

**Recommendation 1: Fine-tuned classifier**
- Train a small BERT/RoBERTa classifier on labeled examples
- Input: claim text + surrounding context
- Output: theory probabilities
- Requires ~100-500 labeled examples per theory

```python
from transformers import AutoModelForSequenceClassification

class TheoryClassifier:
    def __init__(self, model_path="./models/theory_classifier"):
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)

    def predict(self, text: str) -> Dict[str, float]:
        # Returns probability distribution over theories
        inputs = self.tokenizer(text, return_tensors="pt")
        outputs = self.model(**inputs)
        probs = softmax(outputs.logits, dim=-1)
        return {theory: prob for theory, prob in zip(THEORIES, probs[0])}
```

**Recommendation 2: Embedding similarity** (no training required)
- Embed theory descriptions and claim text
- Assign to most similar theory
- Use threshold for "no clear theory"

```python
from sentence_transformers import SentenceTransformer

class EmbeddingTheoryMatcher:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.theory_embeddings = self._embed_theories()

    def _embed_theories(self):
        descriptions = {
            "SRT": "Stress Recovery Theory proposes that natural environments promote psychophysiological recovery from stress through innate responses to nature",
            "ART": "Attention Restoration Theory proposes that natural environments restore directed attention capacity depleted by mental fatigue",
            ...
        }
        return {t: self.model.encode(d) for t, d in descriptions.items()}

    def match(self, text: str, threshold=0.5) -> Optional[str]:
        text_emb = self.model.encode(text)
        similarities = {t: cosine_similarity(text_emb, emb)
                       for t, emb in self.theory_embeddings.items()}
        best = max(similarities, key=similarities.get)
        return best if similarities[best] > threshold else None
```

---

**Dr. Marti Hearst** (Text Mining):

Both approaches have merit. The practical question is: **what's your error budget?**

**Recommendation**: Hybrid approach with confidence-based routing:

1. **High confidence**: Embedding similarity > 0.8 → auto-assign
2. **Medium confidence**: 0.5-0.8 → use keyword disambiguation
3. **Low confidence**: < 0.5 → flag for human review or leave unassigned

```python
def infer_theory_hybrid(text: str) -> Tuple[Optional[str], float, str]:
    """Returns (theory, confidence, method)"""

    # Try embedding first
    emb_result, emb_conf = embedding_matcher.match(text)

    if emb_conf > 0.8:
        return (emb_result, emb_conf, "embedding")

    # Fall back to keyword with disambiguation
    kw_result, kw_conf = keyword_matcher.match_with_context(text)

    if kw_conf > 0.7:
        return (kw_result, kw_conf, "keyword")

    # Low confidence - combine signals
    if emb_result == kw_result and emb_conf > 0.5:
        return (emb_result, (emb_conf + kw_conf) / 2, "consensus")

    return (None, 0.0, "uncertain")
```

---

### TD-2 Synthesis

| Approach | Accuracy | Latency | Requirements |
|----------|----------|---------|--------------|
| Keyword (current) | ~60% | <1ms | None |
| Keyword + disambiguation | ~75% | <5ms | Context rules |
| Embedding similarity | ~85% | ~50ms | Sentence transformer model |
| Fine-tuned classifier | ~92% | ~100ms | Labeled training data |
| Hybrid | ~88% | ~60ms | Embedding model + rules |

**Panel Verdict**: Implement **hybrid (embedding + keyword disambiguation)**:
1. Use sentence-transformers for embedding similarity
2. Add disambiguation rules for known false-positive patterns
3. Return confidence score with every classification
4. Flag low-confidence (<0.6) for review
5. Target: 85% accuracy, <100ms latency

---

## TD-3: Scope Metadata Extraction

### Current Implementation

```python
# web_of_belief.py
@dataclass
class ScopeConditions:
    population: Optional[str] = None      # "adults", "children", "elderly"
    setting: Optional[str] = None         # "urban", "rural", "laboratory"
    duration: Optional[str] = None        # "acute", "chronic", ">30 minutes"
    geography: Optional[str] = None       # "North America", "Europe"
    methodology: Optional[str] = None     # "RCT", "observational"
    scope_specified: bool = False         # Was scope explicitly stated?
```

Problem: This structure exists but is rarely populated. Extractions don't capture scope.

### Panel Discussion

---

**Dr. Nancy Cartwright** (Philosophy of Science):

Scope conditions are *everything* for scientific claims. A finding without scope is an abstraction—potentially useful, but not directly applicable.

**Key insight**: Scope conditions come in two types:
1. **Explicit**: "In adults aged 18-65 in urban settings..."
2. **Implicit**: Inferred from sample description, methods, materials

**Recommendation**: Extract both, but mark them differently:

```python
@dataclass
class ScopeConditions:
    # Explicit scope (stated in claims)
    explicit_population: Optional[str] = None
    explicit_setting: Optional[str] = None
    explicit_duration: Optional[str] = None

    # Implicit scope (inferred from methods)
    sample_demographics: Dict[str, Any] = field(default_factory=dict)
    study_setting: Optional[str] = None
    exposure_duration: Optional[str] = None

    # Metadata
    scope_source: Literal["explicit", "inferred", "mixed"] = "inferred"
    generalization_risk: float = 0.5  # Higher = more risk in generalizing
```

For CNFA specifically, the critical scope dimensions are:
1. **Population age** (children/adults/elderly respond differently)
2. **Exposure duration** (acute vs. chronic effects differ)
3. **Nature type** (forest vs. park vs. indoor plants)
4. **Outcome measurement timing** (immediate vs. delayed)

---

**Dr. Deborah Mayo** (Error Statistics):

From a methodological standpoint, scope is about **severity of test**. A finding has been severely tested for a scope if:
1. The study *could have* found different results for that scope
2. The study *did* include variation in that scope dimension

**Recommendation**: Track not just scope, but **scope coverage**:

```python
@dataclass
class ScopeCoverage:
    dimension: str           # e.g., "age_group"
    values_tested: List[str] # e.g., ["young_adults", "middle_aged"]
    values_untested: List[str]  # e.g., ["children", "elderly"]
    variation_sufficient: bool  # Was there enough variation to test?
```

This lets you identify **scope gaps**—dimensions where the finding is untested.

---

**Dr. Christopher Manning** (NLP):

Scope extraction is a classic **information extraction** task. The challenge is that scope is often:
- Buried in methods sections
- Expressed implicitly ("participants were recruited from...")
- Scattered across multiple sentences

**Recommendation**: Named Entity Recognition (NER) + Relation Extraction:

```python
# Use spaCy with custom NER for scope entities
import spacy
from spacy.tokens import Span

class ScopeExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_lg")
        # Add custom entity recognizer for scope entities
        self._add_scope_patterns()

    def _add_scope_patterns(self):
        patterns = [
            {"label": "POPULATION", "pattern": [{"LOWER": {"IN": ["adults", "children", "elderly", "participants"]}}]},
            {"label": "SETTING", "pattern": [{"LOWER": {"IN": ["urban", "rural", "laboratory", "field"]}}]},
            {"label": "DURATION", "pattern": [{"LIKE_NUM": True}, {"LOWER": {"IN": ["minutes", "hours", "days", "weeks"]}}]},
        ]
        # Add to pipeline

    def extract(self, text: str) -> ScopeConditions:
        doc = self.nlp(text)
        scope = ScopeConditions()

        for ent in doc.ents:
            if ent.label_ == "POPULATION":
                scope.explicit_population = ent.text
            elif ent.label_ == "SETTING":
                scope.explicit_setting = ent.text
            # etc.

        return scope
```

For higher accuracy, use a **few-shot LLM approach**:

```python
SCOPE_EXTRACTION_PROMPT = """
Extract scope conditions from this scientific text.

Text: {text}

Return JSON with:
- population: Who was studied? (age, health status, demographics)
- setting: Where? (lab, field, urban, rural, specific location type)
- duration: How long was exposure/intervention?
- timing: When were outcomes measured?
- methodology: Study design (RCT, observational, etc.)

If not explicitly stated, return null for that field.
"""
```

---

**Dr. Marti Hearst** (Text Mining):

The methods section is your friend. 80% of scope information is there.

**Recommendation**: Section-aware extraction:

1. **Methods section**: Primary source for sample, setting, duration
2. **Results section**: Confirms what was actually measured
3. **Abstract**: Often summarizes key scope
4. **Discussion/Limitations**: Explicitly states scope boundaries

```python
class SectionAwareScopeExtractor:
    def extract(self, paper: Paper) -> ScopeConditions:
        scope = ScopeConditions()

        # Methods: sample characteristics
        if paper.methods:
            scope.sample_demographics = self._extract_sample(paper.methods)
            scope.study_setting = self._extract_setting(paper.methods)
            scope.exposure_duration = self._extract_duration(paper.methods)

        # Discussion/Limitations: explicit scope boundaries
        if paper.discussion:
            limitations = self._extract_limitations(paper.discussion)
            scope.generalization_risk = self._assess_risk(limitations)

        return scope
```

---

### TD-3 Synthesis

| Dimension | Extraction Strategy | Expected Accuracy |
|-----------|--------------------|--------------------|
| Population age | NER + pattern matching | 85% |
| Study setting | Section-aware keyword + NER | 80% |
| Duration | Temporal parsing (→ TD-4) | 75% |
| Geography | NER (GPE entities) | 90% |
| Methodology | Keyword classification | 85% |
| Limitations | LLM few-shot extraction | 80% |

**Panel Verdict**: Implement **section-aware hybrid extraction**:
1. Parse papers into sections (abstract, methods, results, discussion)
2. Use spaCy NER for entities (population, setting, geography)
3. Use pattern matching for methodology classification
4. Use LLM for limitations/explicit scope boundaries
5. Track explicit vs. inferred scope
6. Calculate generalization_risk based on scope coverage
7. Target: 80% recall on critical scope dimensions

---

## TD-4: Temporal Expression Parsing

### Current Implementation

None. Temporal expressions like "after 20 minutes" are not parsed.

### Panel Discussion

---

**Dr. James Pustejovsky** (Temporal Semantics):

Temporal expressions are well-studied in NLP. The TimeML specification covers:
- **TIMEX3**: Time expressions ("20 minutes", "3 days later")
- **EVENT**: Events in time ("exposure", "measurement")
- **TLINK**: Temporal relations (BEFORE, AFTER, DURING)

For Article Eater, you care about:
1. **Exposure duration**: "20 minutes of nature exposure"
2. **Measurement timing**: "measured immediately after" vs. "measured 1 hour later"
3. **Effect persistence**: "effects lasted 3 hours"

**Recommendation**: Use existing temporal taggers, then map to your ontology:

```python
from sutime import SUTime  # Stanford's temporal tagger

class TemporalExtractor:
    def __init__(self):
        self.sutime = SUTime(mark_time_ranges=True)

    def extract(self, text: str) -> List[TemporalExpression]:
        results = self.sutime.parse(text)

        expressions = []
        for r in results:
            expr = TemporalExpression(
                text=r['text'],
                type=r['type'],  # DURATION, TIME, DATE
                value=r['value'],  # ISO-8601 or duration
                start=r['start'],
                end=r['end']
            )
            expressions.append(expr)

        return expressions
```

Key temporal patterns in CNFA literature:
- "after X minutes/hours of exposure"
- "following a X-minute walk"
- "effects persisted for X hours/days"
- "measured at baseline and X minutes post-exposure"

---

**Dr. Christopher Manning** (NLP):

SUTime works but requires Java. For pure Python, consider:

**Option 1: spaCy + rule-based**
```python
import spacy
from spacy.matcher import Matcher

class TemporalMatcher:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_lg")
        self.matcher = Matcher(self.nlp.vocab)
        self._add_patterns()

    def _add_patterns(self):
        # "after 20 minutes"
        pattern1 = [
            {"LOWER": {"IN": ["after", "following"]}},
            {"LIKE_NUM": True},
            {"LOWER": {"IN": ["minutes", "hours", "days", "weeks"]}}
        ]
        self.matcher.add("AFTER_DURATION", [pattern1])

        # "for 3 hours"
        pattern2 = [
            {"LOWER": "for"},
            {"LIKE_NUM": True},
            {"LOWER": {"IN": ["minutes", "hours", "days", "weeks"]}}
        ]
        self.matcher.add("DURATION", [pattern2])
```

**Option 2: dateparser library**
```python
import dateparser

# Handles many temporal expressions
dateparser.parse("20 minutes ago")  # Returns datetime
dateparser.parse("in 3 hours")      # Returns datetime
```

**Option 3: LLM extraction** (most flexible)
```python
TEMPORAL_PROMPT = """
Extract temporal information from this text about a nature/environment study.

Text: {text}

Return JSON:
- exposure_duration: How long was the nature exposure? (in minutes)
- measurement_timing: When were outcomes measured relative to exposure?
- effect_duration: How long did effects last? (if mentioned)
- temporal_design: "immediate", "delayed", "longitudinal", or "unknown"
"""
```

---

### TD-4 Synthesis

| Approach | Coverage | Accuracy | Dependencies |
|----------|----------|----------|--------------|
| SUTime | Comprehensive | 90% | Java |
| spaCy + rules | Common patterns | 80% | spaCy |
| dateparser | Date/time only | 70% | None |
| LLM extraction | Flexible | 85% | API costs |

**Panel Verdict**: Implement **spaCy + rules with LLM fallback**:
1. Primary: spaCy matcher for common patterns (covers 80% of cases)
2. Fallback: LLM extraction for complex/ambiguous cases
3. Normalize all durations to minutes for comparison
4. Extract temporal relations (before/after/during)
5. Target: 85% extraction rate for exposure duration

---

## Implementation Priorities

Based on panel discussion, here's the recommended implementation order:

| Priority | TD | Reason | Effort | Impact |
|----------|-----|--------|--------|--------|
| 1 | TD-2 | Theory classification affects everything downstream | Medium | High |
| 2 | TD-3 | Scope metadata critical for claim validity | Medium | High |
| 3 | TD-1 | Only matters at scale (>1000 beliefs) | Low | Medium |
| 4 | TD-4 | Nice-to-have, improves precision | Low | Low |

### Recommended Sprint Structure

**Sprint TD-A: Theory Inference** (TD-2)
1. Add sentence-transformers dependency
2. Create theory description embeddings
3. Implement EmbeddingTheoryMatcher
4. Add disambiguation rules for known false positives
5. Add confidence scores to theory assignments
6. Test on existing extractions

**Sprint TD-B: Scope Extraction** (TD-3)
1. Add spaCy NER patterns for scope entities
2. Implement section-aware extraction
3. Add explicit vs. inferred tracking
4. Calculate generalization_risk
5. Update ScopeConditions dataclass
6. Integrate with extraction_to_web.py

**Sprint TD-C: Scalability** (TD-1)
1. Implement theory-based belief clustering
2. Add hierarchical coherence computation
3. Add coherence caching with invalidation
4. Benchmark at 5000 beliefs
5. Add constraint network for explicit relations

**Sprint TD-D: Temporal** (TD-4)
1. Add spaCy temporal patterns
2. Implement duration normalization
3. Add temporal relation extraction
4. Integrate with scope extraction

---

## Action Items

| ID | Action | Owner | Target |
|----|--------|-------|--------|
| TD-1-A | Implement hierarchical coherence | Lane B | Sprint TD-C |
| TD-1-B | Add coherence caching | Lane B | Sprint TD-C |
| TD-2-A | Add sentence-transformers to requirements | Lane B | Sprint TD-A |
| TD-2-B | Create EmbeddingTheoryMatcher class | Lane B | Sprint TD-A |
| TD-2-C | Add disambiguation rules | Lane B | Sprint TD-A |
| TD-3-A | Add spaCy scope NER patterns | Lane B | Sprint TD-B |
| TD-3-B | Implement section-aware extraction | Lane B | Sprint TD-B |
| TD-3-C | Update ScopeConditions dataclass | Lane B | Sprint TD-B |
| TD-4-A | Add spaCy temporal patterns | Lane B | Sprint TD-D |
| TD-4-B | Implement duration normalization | Lane B | Sprint TD-D |

---

## Panel Signatures

This review represents the constructed expert opinions based on published work and methodological commitments of:

- Dr. Paul Thagard — Coherence and constraint satisfaction
- Dr. Herbert Simon — Bounded rationality and satisficing
- Dr. Nancy Cartwright — Capacities and scope conditions
- Dr. Deborah Mayo — Error statistics and severity
- Dr. Marcia Bates — Information science and vocabulary
- Dr. James Pustejovsky — Temporal semantics
- Dr. Christopher Manning — NLP and information extraction
- Dr. Jon Kleinberg — Algorithm design
- Dr. Marti Hearst — Text mining

---

---

## Addendum: Incremental Learning Architecture

### Context (User Insight)

The BN is not built in one shot. Articles drip in over time, rules accumulate in Article Eater, then flow to the BN where they're parameterized. The system should get smarter the longer it runs.

### Extended Panel: Online Learning / Incremental Algorithms

| Panelist | Affiliation | Expertise |
|----------|-------------|-----------|
| **Michael I. Jordan** | UC Berkeley | Bayesian ML, variational inference |
| **Andrew Gelman** | Columbia | Bayesian statistics, posterior updating |
| **Tom Griffiths** | Princeton | Computational cognitive science, rational models |
| **David Blei** | Columbia | Topic models, variational inference, streaming |
| **Zoubin Ghahramani** | Cambridge/Uber | Bayesian nonparametrics, online learning |
| **Nando de Freitas** | DeepMind | Sequential Monte Carlo, online inference |

---

### Panel Discussion: Incremental BN Construction

**Dr. Michael Jordan** (Bayesian ML):

The key insight is that **posterior updating is inherently incremental**. Each new paper updates the posterior over BN parameters:

```
P(θ | D₁...Dₙ) ∝ P(Dₙ | θ) × P(θ | D₁...Dₙ₋₁)
```

The previous posterior becomes the new prior. No need to reprocess all papers.

**Recommendation**: Store sufficient statistics, not raw data:
```python
@dataclass
class IncrementalEdgeEstimate:
    edge: Tuple[str, str]  # parent → child

    # Sufficient statistics
    n_observations: int = 0
    sum_concordant: float = 0.0  # Times parent=high → child=high
    sum_discordant: float = 0.0  # Times parent=high → child=low

    # Derived parameters (updated incrementally)
    strength_estimate: float = 0.5
    confidence_interval: Tuple[float, float] = (0.0, 1.0)

    def update(self, observation: Observation):
        self.n_observations += 1
        if observation.concordant:
            self.sum_concordant += observation.weight
        else:
            self.sum_discordant += observation.weight
        self._recompute_estimate()
```

---

**Dr. Andrew Gelman** (Bayesian Statistics):

For credences and BN edge strengths, use **conjugate priors** for closed-form updates:

- **Beta-Binomial** for edge presence/strength
- **Dirichlet-Multinomial** for categorical outcomes
- **Normal-Inverse-Gamma** for continuous outcomes

```python
class BetaBernoulliEdge:
    """Edge strength with Beta prior, Bernoulli likelihood."""

    def __init__(self, prior_alpha=1.0, prior_beta=1.0):
        self.alpha = prior_alpha  # Prior successes
        self.beta = prior_beta    # Prior failures

    def update(self, successes: int, failures: int):
        """Update with new observations."""
        self.alpha += successes
        self.beta += failures

    @property
    def mean(self) -> float:
        """Posterior mean (point estimate)."""
        return self.alpha / (self.alpha + self.beta)

    @property
    def credible_interval(self) -> Tuple[float, float]:
        """95% credible interval."""
        from scipy.stats import beta
        return beta.ppf([0.025, 0.975], self.alpha, self.beta)

    @property
    def effective_sample_size(self) -> float:
        """How much data underlies this estimate."""
        return self.alpha + self.beta - 2  # Subtract prior
```

---

**Dr. David Blei** (Streaming Inference):

For large-scale systems, consider **streaming variational inference**:

1. Process articles in mini-batches
2. Update global parameters with stochastic gradient
3. Never revisit old articles

```python
class StreamingBNLearner:
    def __init__(self, learning_rate=0.01, batch_size=10):
        self.lr = learning_rate
        self.batch_size = batch_size
        self.global_params = {}  # Edge strengths

    def process_article(self, article: Article):
        """Process one article, update global params."""
        local_evidence = self._extract_evidence(article)

        for edge, observation in local_evidence.items():
            if edge not in self.global_params:
                self.global_params[edge] = BetaBernoulliEdge()

            # Stochastic natural gradient update
            self.global_params[edge].update(
                successes=observation.positive,
                failures=observation.negative
            )

    def get_bn_parameters(self) -> Dict[str, float]:
        """Export current best estimates."""
        return {edge: param.mean for edge, param in self.global_params.items()}
```

---

**Dr. Tom Griffiths** (Computational Cognitive Science):

The system should also track **what it doesn't know** and prioritize learning:

1. **Uncertainty reduction**: Which articles would most reduce parameter uncertainty?
2. **Information gain**: Which edges need more evidence?
3. **Value of information**: Where does uncertainty matter most for decisions?

This connects back to **VOI search** (TD-3)—the system should actively seek papers that fill gaps.

```python
class ActiveLearningScheduler:
    def prioritize_gaps(self, bn: BayesianNetwork) -> List[EdgeGap]:
        """Find edges with high uncertainty AND high decision relevance."""
        gaps = []
        for edge in bn.edges:
            param = self.global_params.get(edge)
            if param is None:
                # Completely unknown edge
                gaps.append(EdgeGap(edge, uncertainty=1.0, relevance=self._compute_relevance(edge)))
            else:
                # Known but uncertain
                ci_width = param.credible_interval[1] - param.credible_interval[0]
                if ci_width > 0.3:  # Wide interval = uncertain
                    gaps.append(EdgeGap(edge, uncertainty=ci_width, relevance=self._compute_relevance(edge)))

        return sorted(gaps, key=lambda g: g.uncertainty * g.relevance, reverse=True)
```

---

**Dr. Zoubin Ghahramani** (Bayesian Nonparametrics):

The BN structure itself should be able to grow. Use **nonparametric priors** to:
1. Add new nodes (concepts) as they're discovered
2. Add new edges as relationships emerge
3. Never commit to a fixed structure

```python
class NonparametricBN:
    """BN that can grow as new concepts are discovered."""

    def __init__(self):
        self.nodes = {}  # Concept → Node
        self.edges = {}  # (parent, child) → EdgeParams

    def observe_concept(self, concept: str, context: Dict):
        """Add concept if new, update if known."""
        if concept not in self.nodes:
            self.nodes[concept] = self._create_node(concept, context)
            self._infer_edges(concept)  # Infer relationships to existing nodes

    def _infer_edges(self, new_concept: str):
        """Infer edges between new concept and existing nodes."""
        for existing in self.nodes:
            if self._should_edge_exist(new_concept, existing):
                self.edges[(new_concept, existing)] = BetaBernoulliEdge()
```

---

### Incremental Architecture Summary

```
                    ┌─────────────────────────────────────────────────────┐
                    │                  ARTICLE EATER                       │
                    │  ┌─────────────────────────────────────────────────┐ │
Article Stream ───► │  │ extraction_to_web.py                           │ │
                    │  │ ─────────────────────                          │ │
                    │  │ • Extract claims                                │ │
                    │  │ • Infer theories (TD-2: embedding match)        │ │
                    │  │ • Extract scope (TD-3: section-aware)           │ │
                    │  │ • Parse temporal (TD-4: spaCy patterns)         │ │
                    │  └──────────────────────┬──────────────────────────┘ │
                    │                         ▼                            │
                    │  ┌─────────────────────────────────────────────────┐ │
                    │  │ web_of_belief.py                                │ │
                    │  │ ─────────────────                              │ │
                    │  │ • Add beliefs incrementally                     │ │
                    │  │ • Compute coherence (TD-1: hierarchical)        │ │
                    │  │ • Track provenance                              │ │
                    │  │ • Identify gaps → VOI search                    │ │
                    │  └──────────────────────┬──────────────────────────┘ │
                    └─────────────────────────┼───────────────────────────┘
                                              ▼
                    ┌─────────────────────────────────────────────────────┐
                    │                  BAYESIAN NETWORK                    │
                    │  ┌─────────────────────────────────────────────────┐ │
                    │  │ IncrementalBNBuilder                           │ │
                    │  │ ─────────────────────                          │ │
                    │  │ • Beta-Bernoulli edge priors                    │ │
                    │  │ • Conjugate posterior updates                   │ │
                    │  │ • Streaming parameter estimation                │ │
                    │  │ • Uncertainty tracking per edge                 │ │
                    │  │ • Active learning: prioritize uncertain edges   │ │
                    │  └──────────────────────┬──────────────────────────┘ │
                    │                         ▼                            │
                    │  ┌─────────────────────────────────────────────────┐ │
                    │  │ Self-Improving Loop                             │ │
                    │  │ ────────────────────                            │ │
                    │  │ 1. Identify high-uncertainty edges              │ │
                    │  │ 2. Generate VOI search queries                  │ │
                    │  │ 3. Find articles addressing gaps                │ │
                    │  │ 4. Process → reduce uncertainty                 │ │
                    │  │ 5. Repeat                                       │ │
                    │  └─────────────────────────────────────────────────┘ │
                    └─────────────────────────────────────────────────────┘
```

### New Sprint: TD-E Incremental BN Learning

| Task | Description |
|------|-------------|
| TD-E.1 | Implement BetaBernoulliEdge with conjugate updates |
| TD-E.2 | Create IncrementalBNBuilder class |
| TD-E.3 | Add uncertainty tracking (credible intervals) |
| TD-E.4 | Connect VOI search to edge uncertainty |
| TD-E.5 | Implement streaming parameter updates |
| TD-E.6 | Add active learning prioritization |

**Priority**: After TD-A (theory inference) — needs accurate classifications first

---

*Panel consultation extended: February 8, 2026*
*Document: PANEL_P-TD_TECHNICAL_DEBT_REVIEW_2026_02_08.md*
