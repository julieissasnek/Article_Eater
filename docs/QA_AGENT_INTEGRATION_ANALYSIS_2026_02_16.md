# QA Agent Integration Analysis: Specification vs Reality

**Date**: February 16, 2026
**Purpose**: Gap analysis between QA Agent Specification and actual Article Eater + BN_graphical data structures

---

## Executive Summary

The existing data structures **substantially support** the QA agent specification. The Web of Belief and BN system together provide most of what's needed for progressive disclosure at all five depth levels. Key gaps are in:

1. **Query classification infrastructure** (not data, but processing)
2. **User model persistence** (session tracking)
3. **Evolutionary-level explanations** (implicit in frameworks, not explicit)
4. **Response template engine** (generation layer)

The **knowledge is there**; the **processing pipeline** needs to be built.

---

## Part I: Depth Level Support Analysis

### Level 1: Direct Answer (1-2 sentences)

| Required Element | Data Source | Status |
|------------------|-------------|--------|
| Yes/No/Mixed answer | `belief.credence.value` > 0.5 = yes | ✅ Available |
| Confidence qualifier | `belief.credence.uncertainty` | ✅ Available |
| Brief qualifier | `belief.scope` summary | ✅ Available |

**Implementation**: Query web for relevant beliefs, check credence distribution, generate direct answer.

### Level 2: Contextualized Answer (1 paragraph)

| Required Element | Data Source | Status |
|------------------|-------------|--------|
| Effect size | `claim.statistics.effect_size` or `enhanced_edge.effect_size` | ✅ Available |
| Key moderator | `belief.scope.moderators[0]` | ✅ Available |
| Mechanism hint | `enhanced_edge.mechanism.name` or `bridge_warrant.assumed_mechanism` | ✅ Available |
| Evidence quality | `belief.credence.n_observations` + `replication_status` | ✅ Available |

**Implementation**: Retrieve claim-level statistics, extract primary moderator, summarize mechanism.

### Level 3: Mechanistic Explanation (3-5 paragraphs)

| Required Element | Data Source | Status |
|------------------|-------------|--------|
| Detailed mechanism | `MechanismSpecification.description` + `level_justification` | ✅ Available |
| Evidence per step | `MechanismSpecification.evidence[]` | ✅ Available |
| Full moderator analysis | `belief.scope.moderators[]` + `enabling_conditions` | ✅ Available |
| Boundary conditions | `belief.scope_specified` + `enabling_conditions.blocking_factors` | ✅ Available |

**Implementation**: Use mechanism specification with evidence list, enumerate all moderators and enabling conditions.

### Level 4: Multi-Level Integration (5-10 paragraphs)

| Required Element | Data Source | Status |
|------------------|-------------|--------|
| Cognitive level | `MechanismSpecification` where `level = ALGORITHMIC` | ✅ Available |
| Neural level | `MechanismSpecification` where `level = IMPLEMENTATIONAL` + `neural_evidence` | ✅ Available |
| Computational level | `MechanismSpecification` where `level = COMPUTATIONAL` + framework alignment PP | ✅ Available |
| Evolutionary level | `theoretical_frameworks` containing EVOLUTIONARY or BIOPHILIA | ⚠️ Partial |
| Cross-level coherence | Must be generated from linked mechanisms | 🔧 Needs generation |

**Gap**: Evolutionary explanations exist in framework tags (BIOPHILIA, PROSPECT_REFUGE) but aren't structured as explicit evolutionary-level mechanisms. The data is implicit.

**Implementation**: Filter mechanisms by Marr level, retrieve framework-specific explanations, generate cross-level narrative.

### Level 5: Critical Scholarly Analysis

| Required Element | Data Source | Status |
|------------------|-------------|--------|
| Study-by-study analysis | `evidence_claim[]` with full metadata | ✅ Available |
| Meta-analytic summary | Evidence type `META_ANALYSIS` claims | ✅ Available |
| Methodological critique | `task_ecological_validity`, `presentation_validity`, `measurement_validity` | ✅ Available |
| Competing explanations | Multiple `theoretical_frameworks` per mechanism | ✅ Available |
| Open questions | `belief.status = TENTATIVE` or `epistemic_status = CONTESTED` | ✅ Available |

**Implementation**: Full evidence enumeration with quality scores, flag methodological issues from validity scores.

---

## Part II: Question Type Support

### Category A: Empirical Questions

| Question Type | Required Data | Available? |
|---------------|---------------|------------|
| Effect existence | `belief.credence.value` | ✅ |
| Effect size | `claim.statistics.effect_size`, `enhanced_edge.effect_size_ci` | ✅ |
| Effect direction | `constraint.polarity` or `rule.polarity` | ✅ |
| Effect reliability | `replication_status`, `n_observations` | ✅ |
| Population variation | `population_qualifier`, `scope.population` | ✅ |
| Boundary conditions | `scope_conditions`, `enabling_conditions` | ✅ |
| Temporal dynamics | `temporal_params`, `scope.duration` | ✅ |

### Category B: Mechanistic Questions

| Question Type | Required Data | Available? |
|---------------|---------------|------------|
| Proximate mechanism | `MechanismSpecification` | ✅ |
| Neural substrate | `mechanism.neural_evidence`, `level = IMPLEMENTATIONAL` | ✅ |
| Computational account | `mechanism.level = COMPUTATIONAL`, PP framework | ✅ |
| Pathway identification | `claim.constructs.mediators`, mediation evidence | ✅ |
| Multi-level integration | Multiple mechanisms, linked by edge | ⚠️ Partial (needs generation) |

### Category C: Explanatory Questions

| Question Type | Required Data | Available? |
|---------------|---------------|------------|
| Functional why | Mechanisms with EVOLUTIONARY, BIOPHILIA frameworks | ⚠️ Implicit |
| Developmental why | Population with age_range, developmental moderators | ⚠️ Sparse |
| Contrastive why | `claim.contrast_class`, `claim.difference_maker` | ✅ |
| Comparative why | Cross-mechanism comparison | 🔧 Needs generation |

### Category D: Methodological Questions

| Question Type | Required Data | Available? |
|---------------|---------------|------------|
| Evidence assessment | Evidence weights, replication status | ✅ |
| Measurement critique | `measurement_validity`, method registry | ✅ |
| Study design | `evidence_type`, task classification | ✅ |
| Paradigm limitations | `task_ecological_validity`, VR confounds | ✅ |

### Category E: Applied Questions

| Question Type | Required Data | Available? |
|---------------|---------------|------------|
| Design recommendation | High-credence beliefs with actionable scope | 🔧 Needs derivation |
| Trade-off navigation | Competing effects on same outcome | 🔧 Needs analysis |
| Confidence assessment | Credence + uncertainty + replication | ✅ |

### Category F: Generative Questions

| Question Type | Required Data | Available? |
|---------------|---------------|------------|
| Topic discovery | Beliefs by domain, high-value beliefs | ✅ via `beliefs_by_value()` |
| Gap identification | `epistemic_status = UNKNOWN`, low credence | ✅ |
| Connection finding | Bridge warrants, shared evidence clusters | ✅ |
| Controversy mapping | `contested = True`, conflicting beliefs | ✅ |

---

## Part III: Gap Analysis

### Gap 1: Query Classification (Processing, not Data)

**What's Missing**: A classifier that maps natural language questions to the 27 question types.

**What Exists**:
- `QuestionClassifier` in `interpretive_intelligence.py` handles some patterns
- Pattern matching for MECHANISM, DISAGREEMENT, etc.

**Implementation Required**:
```python
class QuestionTypeClassifier:
    """Maps natural language questions to QuestionType enum."""

    def classify(self, question: str) -> Tuple[QuestionType, float]:
        """Returns (question_type, confidence)"""

    # Heuristics:
    # - "Does X affect Y" → EFFECT_EXISTENCE
    # - "How much" → EFFECT_SIZE
    # - "How does X work" → PROXIMATE_MECHANISM
    # - "Why" patterns → FUNCTIONAL_WHY / CONTRASTIVE_WHY
    # - "What's the evidence" → EVIDENCE_ASSESSMENT
    # - "What should I" → DESIGN_RECOMMENDATION
```

**Effort**: Medium (pattern matching + optional LLM fallback)

### Gap 2: User Model Persistence

**What's Missing**: Session-level tracking of user expertise, mode, depth trajectory.

**What Exists**: Nothing explicit.

**Implementation Required**:
```python
@dataclass
class UserSession:
    session_id: str
    expertise_level: float  # Updated based on vocabulary analysis
    current_mode: str  # Inferred from question patterns
    depth_trajectory: List[int]  # Depths requested
    topics_discussed: List[str]
    theoretical_orientation: List[str]

    def update_from_query(self, query: str):
        """Update model based on new query."""

    def default_depth(self) -> DepthLevel:
        """Compute default depth from model."""
```

**Effort**: Low (dataclass + simple heuristics)

### Gap 3: Evolutionary-Level Explanations

**What's Missing**: Explicit storage of evolutionary/ultimate-level explanations.

**What Exists**:
- `theoretical_frameworks` including BIOPHILIA, PROSPECT_REFUGE, EVOLUTIONARY
- These imply evolutionary explanations but don't structure them

**Options**:
1. **Generate on demand**: When L4 requested, retrieve mechanisms tagged with evolutionary frameworks and generate narrative
2. **Add explicit field**: Add `evolutionary_rationale` to `MechanismSpecification`
3. **Use bridge warrants**: Create EVOLUTIONARY bridge type linking to ultimate explanations

**Recommendation**: Option 1 (generate on demand) for MVP, Option 2 for robustness.

### Gap 4: Response Template Engine

**What's Missing**: A system that fills templates with retrieved knowledge.

**What Exists**: Nothing explicit.

**Implementation Required**:
```python
class ResponseGenerator:
    """Generates responses at specified depth level."""

    def __init__(self, web: WebOfBelief, bn_adapter: EpistemicAdapter):
        self.web = web
        self.bn = bn_adapter
        self.templates = load_templates()

    def generate(
        self,
        question_type: QuestionType,
        depth: DepthLevel,
        topic_beliefs: List[Belief],
        user_model: UserSession
    ) -> Response:
        """Generate structured response with disclosure options."""

        template = self.templates[question_type][depth]
        filled = self._fill_template(template, topic_beliefs)
        disclosure_prompts = self._get_disclosure_prompts(question_type, depth)
        return Response(content=filled, prompts=disclosure_prompts)
```

**Effort**: Medium-High (template design + generation logic)

### Gap 5: Design Recommendations Derivation

**What's Missing**: Logic to convert evidence into actionable recommendations.

**What Exists**:
- High-credence beliefs with scope conditions
- Effect sizes with confidence intervals
- Boundary conditions

**Implementation Required**:
```python
def derive_recommendation(
    topic: str,
    web: WebOfBelief,
    application_context: str
) -> DesignRecommendation:
    """
    Derive actionable recommendation from evidence.

    1. Find relevant beliefs with credence > 0.7
    2. Check if scope conditions match application context
    3. Extract effect direction and size
    4. Generate recommendation with confidence
    5. List trade-offs from conflicting effects
    """
```

**Effort**: Medium

---

## Part IV: Integration Architecture

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     QA AGENT PIPELINE                        │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                           │
        ▼                                           ▼
┌───────────────────┐                    ┌──────────────────────┐
│  ARTICLE EATER    │                    │    BN_GRAPHICAL      │
│  Web of Belief    │                    │    Statistical       │
│                   │                    │    Engine            │
│  - Beliefs        │                    │                      │
│  - Claims         │                    │  - EnhancedEdges     │
│  - Bridge Warrants│◄──────────────────►│  - Mechanisms        │
│  - Scope/Enabling │   EpistemicAdapter │  - Effect Sizes      │
│  - Credence       │                    │  - Predictions       │
│  - Evidence       │                    │                      │
└───────────────────┘                    └──────────────────────┘
        │                                           │
        └─────────────────────┬─────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │  KNOWLEDGE LAYER    │
                    │                     │
                    │  Unified query API: │
                    │  - get_beliefs()    │
                    │  - get_mechanisms() │
                    │  - get_evidence()   │
                    │  - get_effects()    │
                    └─────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │  QA PROCESSING      │
                    │                     │
                    │  - QuestionClassifier│
                    │  - UserModelManager │
                    │  - DepthSelector    │
                    │  - ResponseGenerator│
                    └─────────────────────┘
```

### Key Integration Points

#### 1. Unified Knowledge Query API

```python
class KnowledgeLayer:
    """Unified interface to both Article Eater and BN systems."""

    def __init__(self, web: WebOfBelief, adapter: EpistemicAdapter):
        self.web = web
        self.adapter = adapter

    def query_topic(self, topic: str) -> TopicKnowledge:
        """Get all knowledge relevant to a topic."""
        beliefs = self.web.get_beliefs_by_domain(topic)
        edges = self.adapter.get_edges_for_nodes(topic)
        mechanisms = [e.mechanism for e in edges if e.mechanism]
        return TopicKnowledge(beliefs, edges, mechanisms)

    def get_effect(self, env_factor: str, outcome: str) -> EffectSummary:
        """Get effect between environment factor and outcome."""
        edge = self.adapter.get_edge(env_factor, outcome)
        beliefs = self.web.get_beliefs_for_edge(edge.edge_id)
        return EffectSummary(
            exists=edge.epistemic_status != EpistemicStatus.UNKNOWN,
            size=edge.effect_size,
            ci=edge.effect_size_ci,
            direction=edge.functional_form,
            mechanism=edge.mechanism,
            supporting_beliefs=beliefs,
            confidence=compute_confidence(edge, beliefs)
        )

    def get_mechanism_chain(self, from_node: str, to_node: str) -> List[MechanismSpecification]:
        """Get all mechanisms in causal path."""
```

#### 2. Question → Knowledge Mapping

| Question Type | Primary Query | Secondary Queries |
|---------------|---------------|-------------------|
| EFFECT_EXISTENCE | `get_effect(env, outcome)` | — |
| EFFECT_SIZE | `get_effect(env, outcome)` | `get_evidence(edge)` |
| PROXIMATE_MECHANISM | `get_mechanism_chain(env, outcome)` | `get_framework_alignment()` |
| NEURAL_SUBSTRATE | `get_mechanism_chain()` + filter `level=IMPLEMENTATIONAL` | `get_neural_evidence()` |
| BOUNDARY_CONDITIONS | `get_effect()` + `belief.scope` + `belief.enabling_conditions` | — |
| POPULATION_VARIATION | `get_evidence()` + `population_qualifier` | WEIRD scores |
| EVIDENCE_ASSESSMENT | `get_evidence()` + quality scores | replication status |
| DESIGN_RECOMMENDATION | `get_effect()` + filter `credence > 0.7` | trade-off analysis |
| GAP_IDENTIFICATION | `web.get_contested_beliefs()` + `epistemic_status = UNKNOWN` | VOI scores |

---

## Part V: Implementation Roadmap

### Phase 1: Foundation (1-2 weeks)

| Task | Description | Files |
|------|-------------|-------|
| 1.1 | Create `KnowledgeLayer` unified query API | `src/qa/knowledge_layer.py` |
| 1.2 | Implement `QuestionTypeClassifier` | `src/qa/question_classifier.py` |
| 1.3 | Create `UserSession` model | `src/qa/user_model.py` |
| 1.4 | Define `QuestionType` enum (27 types) | `src/qa/types.py` |

### Phase 2: Response Generation (2-3 weeks)

| Task | Description | Files |
|------|-------------|-------|
| 2.1 | Create response templates for each question type | `src/qa/templates/` |
| 2.2 | Implement `ResponseGenerator` | `src/qa/response_generator.py` |
| 2.3 | Implement depth-level filtering | `src/qa/depth_filter.py` |
| 2.4 | Add confidence/uncertainty markers | `src/qa/confidence_markers.py` |

### Phase 3: Advanced Features (2-3 weeks)

| Task | Description | Files |
|------|-------------|-------|
| 3.1 | Implement design recommendation derivation | `src/qa/recommendations.py` |
| 3.2 | Add evolutionary explanation generation | `src/qa/evolutionary.py` |
| 3.3 | Implement cross-level integration narratives | `src/qa/multilevel.py` |
| 3.4 | Add trade-off analysis | `src/qa/tradeoffs.py` |

### Phase 4: Testing & Validation (1-2 weeks)

| Task | Description | Files |
|------|-------------|-------|
| 4.1 | Create test questions for each type | `tests/test_qa_questions.py` |
| 4.2 | Validate against gold standard answers | `tests/test_qa_quality.py` |
| 4.3 | User type simulation tests | `tests/test_user_adaptation.py` |
| 4.4 | Integration tests with real data | `tests/test_qa_integration.py` |

---

## Part VI: Validation Test Cases

### Test: High Ceiling Creativity Question

**Question**: "Do high ceilings facilitate creativity, when and for whom?"

**Expected Knowledge Retrieval**:

```python
# From Web of Belief
beliefs = web.query(
    environment_id="spatial.ceiling_height",
    outcome_id="cog.creativity"
)

# Expected to find:
# - Belief: "High ceilings enhance divergent thinking" (credence ~0.7)
# - Scope: population="adults", setting="lab", moderators=["task_type"]
# - Enabling: minimum_exposure="priming_required", task_type="divergent"

# From BN
edge = adapter.get_edge("ceiling_height", "creativity")

# Expected:
# - effect_size: 0.4
# - effect_ci: (0.2, 0.6)
# - mechanism: "conceptual_metaphor_priming"
# - theoretical_frameworks: ["EMBODIED", "COGNITIVE_LOAD"]
```

**Expected L2 Response Generation**:
```
Template: EFFECT_EXISTENCE + BOUNDARY_CONDITIONS

Fill with:
- Answer: Yes (credence 0.7 > 0.5)
- Effect size: d ≈ 0.4 (CI: 0.2-0.6)
- Key moderator: task_type (divergent vs convergent)
- Mechanism hint: conceptual metaphor priming
- Evidence quality: moderate (limited replications)

Disclosure prompts:
- "Why does this work?" → L3 mechanism
- "How strong is the evidence?" → Evidence assessment
- "Does this apply to elderly populations?" → Boundary conditions
```

### Test: Evidence Assessment Question

**Question**: "How strong is the evidence for nature views reducing stress?"

**Expected Knowledge Retrieval**:

```python
# From Web of Belief
beliefs = web.query(
    environment_id="natural.view_quality",
    outcome_id="psych.stress"
)

# Expected to find:
# - Multiple beliefs with replication_status
# - Evidence cluster from Ulrich 1984 onwards
# - Meta-analytic belief (if exists)

evidence = web.get_evidence_for_beliefs(beliefs)
# Expected:
# - List of EvidenceClaims with effect sizes
# - Contribution matrix weights
# - Population diversity (WEIRD scores)
```

**Expected L2 Response Generation**:
```
Template: EVIDENCE_ASSESSMENT

Fill with:
- Overall: Strong evidence (meta-analysis + replications)
- N studies: [count]
- Effect size range: [min-max]
- Replication rate: [successes / total]
- Population diversity: WEIRD = [score], non-WEIRD samples = [count]
- Methodological notes: [key limitations]

Disclosure prompts:
- "Show me the key studies" → L5 study-by-study
- "What are the methodological limitations?" → Methodology detail
- "Does this hold for all populations?" → Population variation
```

---

## Part VII: Conclusions

### What Works Now

1. **Rich knowledge base**: Both systems have extensive, well-structured data
2. **Multi-level mechanisms**: Marr-style levels + theoretical frameworks
3. **Evidence quality tracking**: Replication, validity scores, WEIRD assessment
4. **Epistemic uncertainty**: Credence + uncertainty properly separated
5. **Bridge warrants**: Cross-domain explanation infrastructure
6. **Causal structure**: DAG with d-separation and adjustment sets

### What Needs Building

1. **Query processing layer**: Question classification, user modeling
2. **Response generation**: Template engine, depth filtering
3. **Application derivation**: Converting evidence to recommendations
4. **Evolutionary narratives**: Generating from implicit framework tags

### Feasibility Assessment

| Component | Data Available | Processing Needed | Effort |
|-----------|----------------|-------------------|--------|
| L1 answers | ✅ | Low | Low |
| L2 answers | ✅ | Medium | Medium |
| L3 answers | ✅ | Medium | Medium |
| L4 answers | ✅ (mostly) | High | High |
| L5 answers | ✅ | Medium | Medium |
| User adaptation | ❌ | High | Medium |
| Question classification | ❌ | Medium | Medium |

**Overall**: The specification is **implementable** with the existing data infrastructure. Primary work is in the processing layer, not data collection.

---

*Analysis complete. Ready for implementation planning.*
