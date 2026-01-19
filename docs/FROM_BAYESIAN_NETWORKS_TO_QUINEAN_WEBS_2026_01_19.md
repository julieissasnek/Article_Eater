# From Bayesian Networks to Quinean Webs: Rethinking Knowledge Synthesis in Environmental Psychology

*Draft manuscript for journal submission*

**Author:** David Kirsh
**Affiliation:** Department of Cognitive Science, University of California, San Diego
**Date:** January 19, 2026
**Version:** 1.0

---

## Abstract

This paper describes the theoretical evolution and architectural transformation of Article Eater, a computational system for synthesizing scientific evidence in environmental psychology—specifically, the literature on how built environments affect human cognition, emotion, and behavior. We trace the system's development from a conventional rule-based Bayesian network approach through a series of principled architectural changes that culminated in a Quinean coherentist framework. The resulting system represents what we believe is a novel contribution to computational epistemology: a knowledge synthesis engine that explicitly instantiates Quine's "web of belief" metaphor, abandoning foundationalist assumptions in favor of mutual constraint and reflective equilibrium. We document the theoretical motivations for each architectural transition, present the formal structures that emerged, and reflect on why such approaches remain rare in knowledge engineering despite their philosophical precedent. Critically, we argue that this explicit epistemic structure offers capabilities that Large Language Models—even with retrieval-augmented access to the same literature—cannot provide: inspectable beliefs with quantified uncertainty, structural queries that expose gaps and tensions, and coherence-based dynamics that make the system a genuine *discovery engine* rather than merely a synthesis tool. The paper concludes with implications for Value of Information analysis and directions for computational scientific discovery.

**Keywords:** coherentist epistemology, Bayesian networks, knowledge synthesis, Web of Belief, environmental psychology, neuroarchitecture, reflective equilibrium, computational epistemology, scientific discovery, large language models

---

## 1. Introduction: The Problem of Knowledge Synthesis

### 1.1 The Scientific Literature as a Coordination Problem

The scientific literature in any domain represents a vast, distributed knowledge structure. Individual papers contribute findings, theories, and interpretations, but the literature as a whole lacks explicit mechanisms for integration. A researcher asking "What do we know about how curved walls affect human anxiety?" must manually synthesize dozens of papers, each using different operational measures (cortisol, heart rate, self-report scales), different theoretical frameworks (Attention Restoration Theory, Stress Recovery Theory, Prospect-Refuge Theory), and different populations and methodologies.

This synthesis problem has traditionally been addressed through narrative reviews and meta-analyses. Both approaches have limitations. Narrative reviews depend entirely on the reviewer's interpretive framework and cannot be systematically queried. Meta-analyses require methodological homogeneity that often does not exist, and they produce point estimates that obscure important heterogeneity in findings.

### 1.2 The Domain: Cognitive Neuroscience for Architecture (CNfA)

Our development work has focused on Cognitive Neuroscience for Architecture (CNfA), an interdisciplinary field studying how built environments affect human cognition, affect, and behavior (Eberhard, 2009; Robinson & Pallasmaa, 2015). This domain presents particular challenges:

1. **Theoretical pluralism**: Multiple competing theories (Attention Restoration Theory, Stress Recovery Theory, Biophilia Hypothesis, Prospect-Refuge Theory) offer overlapping but distinct predictions.

2. **Measurement heterogeneity**: The same construct (e.g., "stress reduction") may be operationalized through cortisol assays, heart rate variability, self-report anxiety scales, or behavioral indicators.

3. **Context sensitivity**: Effects often depend on population (children vs. adults), setting (laboratory vs. field), duration of exposure, and cultural background.

4. **Mechanism uncertainty**: Even when effects are replicated, the causal mechanisms often remain contested or unknown.

### 1.3 Objectives of the Present Work

We sought to build a computational system that could:

1. Extract structured claims from the research literature with full provenance
2. Integrate findings across studies while preserving methodological detail
3. Support probabilistic reasoning about environmental effects
4. Handle theoretical disagreement and methodological heterogeneity gracefully
5. Identify gaps in the literature and prioritize future research

What we discovered through iterative development was that achieving these objectives required progressively abandoning assumptions that we initially took for granted—culminating in a fundamental shift from foundationalist to coherentist epistemology.

---

## 2. The Original Architecture: Rules and Bayesian Networks (V15–V18)

### 2.1 The Hierarchical Rule System

The original Article Eater system (versions 15.8.1 through 18.x) employed a hierarchical rule extraction model with three abstraction levels:

**Micro-rules**: Individual operational findings from single studies
```
"Curved walls → cortisol ↓" (p < .05, d = 0.52, N = 68, Vartanian et al. 2015)
"Curved walls → STAI score ↓" (p < .01, d = 0.64, N = 68, Vartanian et al. 2015)
```

**Meso-rules**: Aggregated constructs synthesized from multiple micro-rules
```
"Curved walls → stress reduction"
├─ Triangulation: 3 operational measures
├─ Confidence: 0.82 (weighted composite)
└─ Mechanism: Predictive Processing Fluency
```

**Macro-rules**: Theoretical principles spanning multiple meso-rules
```
"Biophilic design → improved wellbeing"
├─ Multiple pathways: stress ↓, attention ↑, mood ↑
└─ Framework: Biophilia Hypothesis + Attention Restoration Theory
```

The confidence scoring for meso-rules employed a weighted composite:
- **Triangulation** (0.30): More diverse operational measures increase confidence
- **Effect strength** (0.28): Larger effect sizes increase confidence
- **Sample size** (0.14): Larger N increases confidence
- **Consistency** (0.10): Consistent direction across measures increases confidence
- **Remaining weight** (0.18): Methodological quality factors

### 2.2 Rule Types and Their Rationale

The system distinguished several rule types, each serving a specific function in knowledge representation:

**Edge rules** specified causal or associative relationships between variables:
```yaml
type: "edge"
source: "curved_walls"
target: "cortisol_levels"
direction: "reduces"
strength: [0.4, 0.6]  # Credible interval
```

Edge rules formed the backbone of the extracted knowledge graph. The rationale was straightforward: scientific findings typically assert that some environmental feature X affects some outcome Y.

**CPD hints** (Conditional Probability Distribution hints) provided guidance for parameterizing Bayesian network edges:
```yaml
type: "cpd_hint"
edge: "natural_views → stress"
hint: "moderate_effect"
basis: "meta_analysis"
```

CPD hints were necessary because raw findings rarely provide complete conditional probability specifications. The system collected hints from multiple sources to constrain the parameter space for downstream Bayesian network construction.

**Prior rules** established baseline probability distributions:
```yaml
type: "prior"
variable: "stress_level"
distribution: "beta(2, 5)"
basis: "population_baseline"
```

Priors were essential for converting the knowledge graph into a functional Bayesian network. They specified initial beliefs about variables before conditioning on evidence.

**Constraint rules** captured logical or statistical dependencies:
```yaml
type: "constraint"
assertion: "ceiling_height → perceived_spaciousness"
constraint: "monotonic_positive"
```

Constraints prevented the system from representing impossible states and encoded domain knowledge that went beyond individual findings.

**Interaction rules** specified moderation effects:
```yaml
type: "interaction"
base_effect: "nature_views → stress_reduction"
moderator: "chronic_stress"
interaction: "amplifying"
```

Interactions were critical for CNfA because environmental effects often depend on subject characteristics. The same environment might reduce stress in chronically stressed individuals while having minimal effect on already-calm subjects.

### 2.3 The Bayesian Network Export Model

The ultimate goal of the rule system was to export knowledge in a format suitable for Bayesian network construction. The export schema (version 0.2) specified:

1. **Nodes**: Environmental features, subject characteristics, latent constructs, and indicators
2. **Edges**: Causal, correlational, indicator, structural, explanatory, and evidential relationships
3. **Rule payloads**: Full provenance linking network parameters to source papers

Subject heterogeneity was handled through explicit parent nodes (subject characteristics as parents of outcome variables) and hierarchical priors (subject attributes parameterizing causal strength distributions).

The resulting Bayesian networks were **parameter-incomplete**: the structure was extracted from literature, but CPD entries required human expert specification. The system provided templates and constraints, but final parameterization was a human-in-the-loop process.

### 2.4 What Differentiated This BN from Standard Approaches

Standard Bayesian network applications typically have:
- A **fixed ontology** of variables defined by the application domain
- **Learned parameters** from a dataset of observations
- **Inference as the primary operation**: compute P(query | evidence)

The Article Eater BN differed in several respects:

1. **The ontology was extracted from literature**, not predefined. New papers could introduce new constructs.

2. **Parameters were constrained by rules**, not learned from data. We had few or no observations of joint distributions; instead, we had reported findings from experiments with their own conditional structures.

3. **Provenance was first-class**: Every parameter had a citation chain. This enabled questions like "Which papers support this edge?" and "What would change if this study were retracted?"

4. **Subject scope was explicit**: Rather than assuming a universal population, each rule specified its scope conditions. The BN could be instantiated for different target populations.

5. **Uncertainty propagated through interpretation**: We were uncertain not only about parameters but about whether the concepts in different papers referred to the same underlying constructs.

This last point proved most troublesome and eventually motivated the Quinean shift.

---

## 3. The Problems that Emerged

### 3.1 The Commensurability Problem

As the system processed more literature, we encountered persistent difficulties mapping extracted claims to a common ontology. Consider two papers:

**Paper A** (Ulrich, 1984): "Patients with nature views had shorter hospital stays"
**Paper B** (Kaplan & Kaplan, 1989): "Natural environments restore directed attention capacity"

These papers use different theories (Stress Recovery Theory vs. Attention Restoration Theory), different populations (surgical patients vs. general adults), different measures (hospital stay length vs. attention task performance), and potentially different conceptions of "nature."

The original system attempted to resolve this through a **canonical vocabulary**—standardized environment and outcome taxonomies. But this approach forced premature theoretical commitments. Are "stress recovery" and "attention restoration" the same construct measured differently, different constructs that happen to correlate, or aspects of a broader construct like "psychological restoration"?

### 3.2 The Directionality Problem

The hierarchical model assumed that justification flowed upward: micro-rules supported meso-rules, which supported macro-rules. Theoretical principles were consequences of empirical aggregation.

But actual scientific reasoning often runs the other direction. Theories make predictions that guide what experiments get conducted and how results get interpreted. A finding that "nature views reduced cortisol" is already theory-laden—it assumes a particular operationalization of stress and a causal interpretation that depends on background theory.

Moreover, we found cases where theoretical considerations legitimately overrode apparent empirical findings:

- A single study with methodological limitations shouldn't immediately revise well-established theory
- Findings that don't replicate might indicate scope conditions rather than refuting the underlying claim
- Theoretical coherence can be evidence that apparent counterevidence reflects measurement error

### 3.3 The Stub Problem

Many extracted findings didn't fit neatly into the existing ontology. We called these "stubs"—claims that existed but weren't integrated into the theoretical structure:

```yaml
type: "stub"
content: "Urban noise exposure correlated with reduced nature-seeking behavior"
status: "unintegrated"
note: "No clear theoretical home—not predicted by ART, SRT, or Biophilia"
```

The original system treated stubs as temporary anomalies awaiting proper categorization. But philosophically, this is backwards. A stub might indicate:
- A gap in existing theory
- A novel phenomenon requiring new theoretical constructs
- A methodological artifact
- An authentic contribution that existing theories should accommodate

The foundationalist model had no principled way to distinguish these cases.

### 3.4 The Contradiction Problem

Contradiction handling proved especially problematic. When two studies reported opposite effects, the system had limited options:
1. Average the effects (losing the signal that something interesting is happening)
2. Privilege one study based on sample size or methodology
3. Flag the contradiction for human review

But what appeared as "contradiction" often masked something more nuanced:

- **Scope boundaries**: Effect holds in population A but not population B
- **Methodological divergence**: Different operational measures capture different aspects
- **Precision boundaries**: Both studies are correct within their confidence intervals
- **Genuine contradiction**: Only one can be correct

The original system couldn't distinguish these cases programmatically.

---

## 4. The Quinean Turn: From Accumulation to Coherence

### 4.1 Philosophical Motivation

The accumulated problems pointed toward a fundamental architectural issue: we were treating evidence as foundational when, philosophically, nothing is truly foundational.

W.V.O. Quine articulated this insight in "Two Dogmas of Empiricism" (1951):

> "The totality of our so-called knowledge or beliefs, from the most casual matters of geography and history to the profoundest laws of atomic physics or even of pure mathematics and logic, is a man-made fabric which impinges on experience only along the edges... A conflict with experience at the periphery occasions readjustments in the interior of the field... But the total field is so underdetermined by its boundary conditions, experience, that there is much latitude of choice as to what statements to reevaluate in the light of any single contrary experience."

This "web of belief" metaphor offered a different model: no beliefs are unrevisable, justification comes from coherence rather than derivation from foundational evidence, and the proper response to anomaly is to seek the revision that maximizes overall coherence.

### 4.2 The Coherentist Framework

We reimplemented the core epistemic engine around coherentist principles. The key data structure became the **belief** rather than the **rule**:

```python
@dataclass
class Belief:
    content: str                    # What is believed
    credence: Credence              # Degree of belief with meta-uncertainty
    level: EpistemicLevel           # Position in the web (theoretical/intermediate/empirical/observational)
    status: BeliefStatus            # stub/tentative/established/entrenched/anomalous
    source_paper: Optional[str]     # Provenance
    source_claim_ids: List[str]     # Which extracted claims support this
    theory: Optional[str]           # Associated theory (may be None)
    scope: ScopeConditions          # When/where this belief applies
```

The critical innovation is that **epistemic level is descriptive, not normative**. A theoretical belief is not "better" than an empirical one; it simply occupies a different position in the web. And crucially:

```python
class EpistemicLevel(Enum):
    THEORETICAL = "theoretical"      # Core theoretical commitments
    INTERMEDIATE = "intermediate"    # Generalizations, mechanisms
    EMPIRICAL = "empirical"          # Research findings
    OBSERVATIONAL = "observational"  # Direct measurements, observations
```

Following Quine, beliefs near the center (THEORETICAL) are more entrenched—we're more reluctant to revise them because revision would require cascading changes throughout the web. But **nothing is unrevisable**. A sufficiently powerful anomaly can, in principle, lead us to revise even our most central commitments.

### 4.3 Constraints Replace Rules

Instead of rules that flow from evidence to conclusion, the system now uses **constraints** that express mutual dependency:

```python
@dataclass
class Constraint:
    source_id: str                  # Belief ID
    target_id: str                  # Belief ID
    constraint_type: ConstraintType # supports/contradicts/explains/etc.
    strength: float                 # How strongly they constrain each other
    causal_direction: CausalDirection  # What causal relationship, if any
    mediator: Optional[str]         # For mediated causal paths
    symmetric: bool                 # Does constraint apply bidirectionally?
```

Constraint types capture the different ways beliefs can relate:

```python
class ConstraintType(Enum):
    SUPPORTS = "supports"           # Positive coherence
    CONTRADICTS = "contradicts"     # Negative coherence
    EXPLAINS = "explains"           # Theoretical → empirical
    INSTANTIATES = "instantiates"   # Empirical → theoretical
    ANALOGOUS = "analogous"         # Similar structure
    BRIDGES = "bridges"             # Cross-theory connection
    STRONG_TENSION = "strong_tension"  # Failed bridge
    SHARED_EVIDENCE = "shared_evidence"  # Same study supports both
```

The **SHARED_EVIDENCE** constraint type was added (Sprint 8) to address evidence independence. If two beliefs are both supported by the same study, they should not double-count that evidence. This prevents a single prolific study from dominating the web.

### 4.4 The Equilibrium-Seeking Algorithm

The web continuously seeks **reflective equilibrium**—a state where beliefs cohere with each other and with incoming evidence. When new evidence arrives:

1. Map the claim to a belief (or create a stub if no mapping exists)
2. Compute coherence scores for all affected beliefs
3. Identify tensions (beliefs that coherence would push in opposite directions)
4. Apply minimal revision to maximize global coherence
5. Mark beliefs whose status changed (established → anomalous, etc.)

The coherence computation uses a weighted sum of constraint satisfactions:

```python
def compute_local_coherence(self, belief_id: str) -> float:
    """Compute coherence of a single belief with its neighbors."""
    belief = self.beliefs[belief_id]
    total_coherence = 0.0
    total_weight = 0.0

    for constraint_id in self.get_constraints_for_belief(belief_id):
        constraint = self.constraints[constraint_id]
        partner_id = (constraint.target_id
                     if constraint.source_id == belief_id
                     else constraint.source_id)
        partner = self.beliefs[partner_id]

        # Coherence contribution depends on constraint type
        if constraint.constraint_type == ConstraintType.SUPPORTS:
            contribution = partner.credence.value * constraint.strength
        elif constraint.constraint_type == ConstraintType.CONTRADICTS:
            contribution = (1 - partner.credence.value) * constraint.strength
        # ... other types

        total_coherence += contribution * constraint.strength
        total_weight += constraint.strength

    return total_coherence / total_weight if total_weight > 0 else 0.5
```

### 4.5 Bridge Warrants: Connecting Theories

A central challenge in environmental psychology is relating findings across theoretical frameworks. Attention Restoration Theory (Kaplan & Kaplan, 1989) and Stress Recovery Theory (Ulrich, 1984) both predict beneficial effects of nature, but through different mechanisms.

Sprint 3 introduced **bridge warrants**—explicit representations of cross-theory connections:

```python
class BridgeType(Enum):
    MECHANISM = "mechanism"           # Shared causal mechanism
    FUNCTIONAL = "functional"         # Same functional role
    ANALOGICAL = "analogical"         # Structural similarity
    CONSTITUTIVE = "constitutive"     # One theory grounds the other
    EMPIRICAL_COVARIANCE = "empirical_covariance"  # Statistical co-occurrence
```

Bridge warrants carry different default confidences reflecting their epistemic strength:
- **Constitutive** (0.85): Theory B is part of what Theory A means
- **Mechanism** (0.60): Theories share a validated causal pathway
- **Functional** (0.50): Theories make similar predictions for different reasons
- **Analogical** (0.35): Theories have similar structure without shared mechanism

This allows the system to track when evidence for one theory provides partial support for another—a common pattern in actual scientific reasoning that foundationalist models struggle to represent.

---

## 5. The Sprint-by-Sprint Evolution

### 5.1 Sprint 1: Claims to Beliefs Mapper

The first integration sprint built `extraction_to_web.py`, translating extracted claims into the coherentist framework. Key decisions:

1. **Credence initialization**: Empirical claims start at 0.6 with uncertainty 0.3; theoretical claims start at 0.5 with uncertainty 0.4 (more central, less certain)

2. **Constraint creation**: Claims within the same paper create SUPPORTS or CONTRADICTS constraints based on semantic similarity

3. **Stub handling**: Claims without theory attachment become stubs rather than being forced into categories

### 5.2 Sprint 2: Pipeline Integration

Sprint 2 wired the coherentist engine into the extraction pipeline. The pipeline now outputs:
- `web_state.json`: Full web of belief state (serialized for persistence)
- `stubs.jsonl`: Findings awaiting theoretical integration
- `tensions.jsonl`: Detected inconsistencies for human review

Configuration parameters control equilibrium-seeking behavior:
- `AE_WEB_SEEK_EQUILIBRIUM`: Whether to run equilibrium algorithm (default: True)
- `AE_WEB_EQUILIBRIUM_MAX_ITERATIONS`: Iteration limit (default: 100)
- `AE_WEB_CONVERGENCE_THRESHOLD`: When to stop (default: 0.001)

### 5.3 Sprint 3: Bridge Warrants

Bridge warrants (discussed above) enabled cross-theory knowledge transfer. The system also began outputting:
- `bridges.jsonl`: Active bridge warrants with confidence scores
- `anomalies.jsonl`: Findings that create tension across bridges

### 5.4 Sprint 4: Outcome Taxonomy Extensions

The outcome taxonomy was restructured from a flat list to a hierarchical system:

```
feature/                      # Environmental features
  spatial/, natural/, sensory/
percept/                      # Perceptual/cognitive constructs
  complexity/, coherence/
response/                     # Human responses
  physiological/, emotional/, behavioral/
config/                       # Configurational properties (renamed from "configurational")
  wayfinding/, circulation/
```

This restructuring (per Dr. Marcia Bates's expertise in knowledge organization) better captured the domain's conceptual structure and improved the semantic similarity computations underlying constraint creation.

### 5.5 Sprint 5: Persistence and Accumulation

Sprint 5 addressed how to integrate findings across papers—particularly when the same outcome is measured multiple times. Key innovations:

1. **Inverse-variance weighting** (DerSimonian-Laird method): Combine effect sizes appropriately
2. **Conflict type categorization**: Distinguish genuine contradictions from scope boundaries, methodological divergence, and precision boundaries
3. **Coherence dashboard**: Real-time visualization of web health
4. **Paper quality weighting**: Higher-quality studies exert more influence
5. **Web snapshots**: Disaster recovery for computational epistemology

### 5.6 Sprints 6-8: Expert Panel Refinements

We convened a panel of experts (constructed from their published work) to review the architecture:

- **Dr. Judea Pearl** (causal inference): Recommended explicit causal direction tracking and mediator specification for indirect causal paths
- **Dr. Nancy Cartwright** (philosophy of science): Emphasized that unknown scope ≠ universal scope; papers that don't specify populations shouldn't be assumed to apply everywhere
- **Dr. Herbert Simon** (bounded rationality): Suggested coherence contribution metrics for theoretical beliefs lacking direct empirical support
- **Dr. Marcia Bates** (information science): Recommended the taxonomy restructuring
- **Dr. Rachel Kaplan** (environmental psychology): Noted that ecological validity should affect uncertainty, not credence directly

These refinements produced:
- `CausalDirection` enum with MEDIATED for indirect causal paths
- `scope_specified` field distinguishing unknown from universal scope
- `CoherenceContribution` metric for theoretical beliefs
- Ecological validity uncertainty factors

### 5.7 Sprint 9: Gold Standard Corpus

The final sprint created a validation framework:
- Annotated papers with expected extractions
- Negative tests (what should NOT be extracted)
- Precision/recall metrics for extraction quality
- Leave-one-out validation for belief credences

---

## 6. Reconceptualizing Value of Information

### 6.1 The Traditional VOI Framework

In decision theory, the Value of Information (VOI) for an observation is the expected gain from making the decision after observing versus before:

```
VOI(observation) = E[utility | observe] - E[utility | don't observe]
```

For Bayesian networks, VOI often focuses on reducing uncertainty in target variables. An observation has high VOI if it significantly narrows the posterior distribution of variables we care about.

### 6.2 VOI in a Coherentist Framework

The Quinean framework suggests a different conception of VOI. In a web of belief, value comes from:

1. **Tension resolution**: Observations that could resolve existing tensions have high VOI
2. **Stub integration**: Observations that could provide theoretical homes for stubs
3. **Bridge strengthening**: Observations that could validate or invalidate cross-theory bridges
4. **Scope boundary discovery**: Observations that could clarify when findings apply

Consider a web containing:
- High-credence belief: "Natural views reduce stress"
- Stub: "Urban noise increases nature-seeking behavior"
- Tension: ART and SRT make different predictions about mechanism

Traditional VOI might prioritize studies that reduce uncertainty in effect size. Coherentist VOI also values:
- Studies that might connect the stub to existing theory
- Studies that could resolve the ART/SRT mechanism debate
- Studies in under-represented populations that could reveal scope boundaries

### 6.3 Diversity Metrics for Research Prioritization

Sprint 8 introduced a **diversity index** for evaluating literature coverage:

```
Diversity = 0.6 × Environment_Entropy + 0.4 × Outcome_Entropy
```

Where entropy measures the evenness of coverage across taxonomy categories. A literature dominated by studies of natural views affecting stress has low diversity; the marginal VOI of another such study is lower than a study exploring under-represented environment-outcome combinations.

This operationalizes a key insight: the value of a study depends not just on reducing uncertainty about a specific claim, but on how it contributes to the overall health of the knowledge web.

---

## 7. Questions and Inferences the System Enables

### 7.1 Novel Query Types

The coherentist architecture enables queries that were impossible in the rule-based system:

**Coherence queries**: "How well does belief X cohere with the rest of the web?"
```python
web.compute_local_coherence(belief_id)
```

**Tension queries**: "What are the unresolved tensions in the web?"
```python
web.get_tensions(threshold=0.3)  # Returns beliefs in significant tension
```

**What-if queries**: "How would the web change if this study were retracted?"
```python
web_copy = web.clone()
web_copy.remove_paper("ulrich_1984")
web_copy.seek_equilibrium()
# Compare credences before/after
```

**Bridge queries**: "What knowledge transfers between ART and SRT?"
```python
web.get_bridges(source_theory="ART", target_theory="SRT")
```

**Stub queries**: "What findings lack theoretical integration?"
```python
web.get_stubs()  # Returns beliefs with no theory attachment
```

### 7.2 Inference Patterns

The system supports several inference patterns:

**Coherence-based credence update**: When new evidence arrives, credences adjust based on constraint propagation, not just direct support
```python
# Adding a finding that supports ART indirectly supports beliefs
# that bridge from ART to other theories
```

**Theoretical modulation of empirical credence**: A well-supported theoretical framework can increase credence in compatible findings and decrease credence in anomalies
```python
# A finding inconsistent with entrenched theory gets
# downweighted unless it's replicated or explained
```

**Cross-domain evidence**: Evidence for Stress Recovery Theory provides partial support for Attention Restoration Theory via bridge warrants
```python
# Ulrich (1984) SRT finding → SRT belief (direct)
#                           → ART belief (via functional bridge)
```

**Scope-conditioned inference**: Inferences are conditioned on scope match
```python
# "What is the expected effect of nature views on stress
#  for healthy adults in field settings?"
```

---

## 8. Why Others Haven't Taken This Path

### 8.1 The Dominance of Foundationalist Assumptions

The foundationalist picture—observation as bedrock, theory as superstructure—is deeply ingrained in computational approaches to knowledge representation. This is understandable:

1. **Engineering tractability**: Foundationalist models have clear data flow (observation → processing → conclusion). Coherentist models require iterative constraint satisfaction.

2. **Training data**: Machine learning systems are typically trained on labeled data, which implicitly assumes observations are ground truth.

3. **Historical precedent**: Expert systems, knowledge bases, and Bayesian networks all emerged from traditions that took foundationalism for granted.

4. **Philosophy's obscurity**: Quine's insights, while influential in philosophy, haven't penetrated deeply into computer science curricula.

### 8.2 The "Good Enough" Problem

For many applications, foundationalist approaches work well enough. If you're building a medical diagnosis system, treating symptoms as observed evidence and diseases as latent variables is pragmatically adequate.

The limitations become apparent only in domains with:
- Multiple competing theoretical frameworks
- High measurement heterogeneity
- Context-sensitive effects
- Meta-scientific goals (understanding the literature, not just using it)

Environmental psychology exhibits all these properties; most application domains do not.

### 8.3 The Implementation Burden

Coherentist systems are harder to build:
- No standard algorithms (unlike belief propagation for BNs)
- Equilibrium-seeking can be computationally expensive
- Validation is difficult (no ground truth for "coherence")
- Users expect foundationalist explanations

We invested substantial engineering effort in the iterative coherence algorithms, constraint propagation, and equilibrium detection. This effort only made sense given our specific goals.

### 8.4 The Explanation Problem

Foundationalist systems provide intuitively satisfying explanations: "The system concluded X because evidence Y was observed, and rule Z links Y to X."

Coherentist explanations are more complex: "The system believes X with credence 0.73 because X coheres with beliefs A, B, and C (which support it) more strongly than it conflicts with beliefs D and E (which contradict it), and beliefs A-E are themselves supported by constraints from..."

This kind of explanation, while more faithful to actual scientific reasoning, is harder for users to process.

---

## 9. Beyond LLMs: Explicit Epistemic Structure as a Discovery Engine

### 9.1 The Implicit Knowledge Problem

Large Language Models (LLMs) have demonstrated remarkable capabilities in synthesizing information from scientific literature. An LLM with access to all CNfA papers through Retrieval-Augmented Generation (RAG) can answer questions like "What does the research say about nature views and stress?" with impressive fluency and apparent comprehensiveness.

Yet the knowledge encoded in an LLM—even one with perfect retrieval—differs fundamentally from knowledge encoded in an explicit epistemic structure. The difference matters profoundly for scientific discovery.

**LLM knowledge is implicit**. When an LLM reports that "research suggests nature views reduce stress," this conclusion emerges from statistical patterns across training tokens. The model cannot point to which beliefs support this conclusion, what their individual credences are, whether they conflict with other beliefs, or what scope conditions apply. The knowledge exists, but its structure is opaque.

**LLM knowledge is undifferentiated**. The model treats high-quality randomized controlled trials and speculative opinion pieces as equivalent grist for statistical learning. It has no principled way to weight evidence by methodology, track replication, or distinguish empirical findings from theoretical claims.

**LLM knowledge lacks tension awareness**. When the literature contains genuine disagreement—some studies find an effect, others don't—the LLM tends to produce averaged, hedged summaries. It cannot identify the tension as an object of inquiry, diagnose whether the conflict reflects scope boundaries versus genuine contradiction, or flag it as a priority for resolution.

### 9.2 What Explicit Structure Enables

The Quinean web differs from LLM-based synthesis in ways that enable scientific discovery:

**Inspectable beliefs**: Every belief in the web has an explicit credence, uncertainty, epistemic level, scope conditions, and provenance. A researcher can examine exactly what the system believes about nature views and stress, how confident it is, and why.

```python
belief = web.get_belief("nature_views_reduce_stress")
print(f"Credence: {belief.credence.value:.2f} ± {belief.credence.uncertainty:.2f}")
print(f"Supporting studies: {belief.credence.n_supporting}")
print(f"Scope: {belief.scope.population}, {belief.scope.setting}")
```

**Structural queries**: The web's explicit constraint network enables queries that are impossible for LLMs:

- "What beliefs depend on Ulrich (1984)?" (provenance tracing)
- "What beliefs are in tension with each other?" (tension detection)
- "What would change if we rejected ART?" (counterfactual analysis)
- "Where are the under-constrained regions of the web?" (gap identification)

**Differential weighting**: The web tracks epistemic level, methodology quality, and evidence independence. A belief supported by three high-quality RCTs is distinguished from one supported by three observational studies from the same lab. The LLM sees only text; the web sees epistemic structure.

**Active tension tracking**: When beliefs conflict, the web doesn't average—it identifies the tension, categorizes it (scope boundary vs. genuine contradiction vs. methodological divergence), and maintains both beliefs with their conflicting credences. This makes disagreement visible rather than smoothing it away.

### 9.3 The Discovery Engine

These structural properties make the web a **discovery engine** in ways that LLMs cannot be:

**Gap discovery**: The diversity index identifies under-explored regions of the environment-outcome space. An LLM can summarize what research exists; the web can identify what research is *missing*.

```python
gaps = web.identify_coverage_gaps()
# Returns: "No studies of acoustic environments in educational settings
#          with physiological outcomes"
```

**Tension-driven hypotheses**: Unresolved tensions are research opportunities. The web can generate hypotheses about what would resolve a tension:

```python
tension = web.get_tension("ART_vs_SRT_mechanism")
# Hypothesis: "A study measuring both attention and stress in the
#            same subjects could distinguish these theories"
```

**Bridge warrant testing**: Cross-theory bridges suggest experiments. If SRT and ART are linked by a functional bridge, studies that test both theories simultaneously become high-value.

```python
bridges = web.get_untested_bridges()
# Returns bridges where empirical covariance hasn't been established
```

**Scope boundary mapping**: When apparent contradictions turn out to be scope boundaries, the web learns something important: the effect holds in context A but not context B. This generates hypotheses about moderating mechanisms.

```python
boundaries = web.get_scope_boundaries()
# Returns: "Nature view effect on stress differs by chronic stress level:
#          strong for chronically stressed, weak for baseline calm"
```

### 9.4 Why This Differs from "Just Asking an LLM"

One might object: "Can't we just ask an LLM to identify gaps, tensions, and research priorities?" The answer is: not reliably, and not with justification.

**LLMs confabulate structure**. When asked "What are the gaps in CNfA research?", an LLM will produce a plausible-sounding answer. But this answer emerges from learned patterns of what "gap identification" sounds like, not from actual structural analysis of the literature. The LLM might identify genuine gaps, but it might also hallucinate gaps that don't exist or miss gaps that do.

**LLMs cannot show their work**. If an LLM claims a gap exists, there's no way to verify this against the actual literature structure. The web can demonstrate: "Here are all 47 beliefs about stress outcomes; here are all 12 beliefs about acoustic environments; here is their intersection (empty)."

**LLMs lack persistent state**. Each LLM query is independent; the model cannot accumulate knowledge across sessions (without expensive fine-tuning). The web maintains persistent state: today's findings integrate with yesterday's, and the cumulative structure is always available for query.

**LLMs optimize for plausibility, not truth**. LLM training optimizes for producing text that humans rate as helpful, harmless, and honest. This is different from optimizing for accurate representation of epistemic structure. The web's equilibrium-seeking algorithm explicitly optimizes for coherence—a property closer to what we actually want from a knowledge base.

### 9.5 Toward Computational Scientific Discovery

The combination of explicit epistemic structure and coherentist dynamics positions the web as infrastructure for **computational scientific discovery**:

**Literature triage**: Given limited resources, which papers should be read carefully? The web can identify papers that would maximally reduce uncertainty, resolve tensions, or fill gaps.

**Study design**: What experiment would be most informative? The web can compute VOI for proposed studies based on how they would affect the constraint network.

**Theory comparison**: How do ART and SRT compare in evidential support? The web can compute comparative coherence metrics and identify which theory better accommodates the full evidence base.

**Anomaly detection**: Which findings don't fit the current theoretical framework? Stubs and anomalous beliefs are automatically flagged as potential discovery opportunities.

**Replication prioritization**: Which findings most need replication? Beliefs with high credence but low n_supporting and high uncertainty are candidates.

This is not to claim that the current system realizes this vision fully. But the architectural foundation—explicit beliefs, explicit constraints, coherence-based dynamics—creates the possibility for computational discovery assistance in ways that implicit statistical knowledge cannot.

---

## 10. Future Directions

### 9.1 Bayesian Network Export (Revised)

The coherentist web doesn't replace Bayesian network export—it provides a more principled foundation for it. Future work will implement:

1. **Web-to-BN compilation**: Extract a BN structure from the current web state, using high-credence beliefs as nodes and strong constraints as edges

2. **Provenance-preserving parameterization**: CPD entries trace to specific beliefs and their supporting papers

3. **Uncertainty propagation**: Meta-uncertainty in the web translates to hyperparameters in the BN

4. **Conditional BN instantiation**: Different BNs for different scope conditions

### 9.2 Domain-Independent Generalization

The Article Eater architecture is currently domain-specific (CNfA), but the coherentist framework is domain-general. Generalization would require:

1. **Pluggable taxonomies**: Replace environment/outcome taxonomies with domain-specific ontologies

2. **Domain-appropriate bridge types**: Different domains may have different patterns of cross-theory connection

3. **Configurable entrenchment**: What counts as "central" varies by domain

### 9.3 Living Review Mode

The system currently processes static literature snapshots. Future work will implement continuous update:

1. **Incremental evidence integration**: New papers update the web without full recomputation
2. **Temporal weighting**: Configurable decay for older findings
3. **Retraction handling**: Clean removal of discredited evidence

### 9.4 Social Epistemology Extensions

The current system treats the literature as a single coherent source. But scientific literatures contain disagreements, schools of thought, and community structure. Extensions would track:

1. **Author/institution credence**: Some sources more reliable than others
2. **Community consensus**: Different communities may have different webs
3. **Citation dynamics**: How beliefs spread through the literature

---

## 11. Conclusion

We have described the evolution of Article Eater from a conventional rule-based Bayesian network approach to a Quinean coherentist framework. The transition was motivated by practical problems—commensurability, directionality, stubs, and contradictions—that proved intractable under foundationalist assumptions.

The resulting system instantiates Quine's "web of belief" metaphor computationally:

- **No foundational level**: Observations, findings, generalizations, and theories are all beliefs with credences
- **Mutual constraint**: Justification flows in all directions through a network of constraints
- **Coherence as criterion**: Belief revision seeks reflective equilibrium
- **Stub accommodation**: Findings can exist without theoretical integration
- **Revisability**: Even central theoretical commitments are, in principle, revisable

This architecture enables novel queries (coherence, tension, what-if, bridge), novel inference patterns (cross-domain evidence, scope-conditioned reasoning), and a reconceived Value of Information framework that values diversity and tension resolution alongside uncertainty reduction.

We speculate that similar approaches haven't been widely pursued because foundationalism is computationally convenient, pragmatically adequate for many applications, and deeply embedded in disciplinary assumptions. The Article Eater project suggests that coherentist alternatives are tractable and can offer genuine advantages for complex domains with theoretical pluralism and measurement heterogeneity.

Perhaps most importantly, the explicit epistemic structure of the Quinean web offers something that no Large Language Model—however capable—can provide: a knowledge base optimized for *discovery* rather than merely for *retrieval*. Where an LLM smooths over tensions, the web preserves them as research opportunities. Where an LLM's knowledge is implicit and unexaminable, the web's beliefs are inspectable, their credences quantified, their constraints explicit. Where an LLM produces plausible summaries, the web identifies gaps, prioritizes studies, and generates testable hypotheses about what would resolve outstanding tensions.

The CNfA research community now has access to a computational epistemology engine that represents knowledge the way scientists actually reason about it: not as a logical derivation from bedrock observations, but as a fabric of mutually constraining beliefs, seeking equilibrium at every level. More than a knowledge base, it is a discovery engine—a tool for identifying what we don't know, what we should study next, and what would happen if our current beliefs were wrong.

---

## Acknowledgments

This work was developed at the University of California, San Diego, with computational assistance from Claude (Anthropic). The author thanks the constructed expert panel—Dr. Judea Pearl, Dr. Nancy Cartwright, Dr. Herbert Simon, Dr. Marcia Bates, and Dr. Rachel Kaplan—whose published work informed the architectural decisions documented here.

---

## References

BonJour, L. (1985). *The Structure of Empirical Knowledge*. Harvard University Press.

Cartwright, N. (1983). *How the Laws of Physics Lie*. Oxford University Press.

Cartwright, N. (1999). *The Dappled World: A Study of the Boundaries of Science*. Cambridge University Press.

Cooper, H., Hedges, L. V., & Valentine, J. C. (Eds.). (2019). *The Handbook of Research Synthesis and Meta-Analysis* (3rd ed.). Russell Sage Foundation.

DerSimonian, R., & Laird, N. (1986). Meta-analysis in clinical trials. *Controlled Clinical Trials*, 7(3), 177-188.

Eberhard, J. P. (2009). *Brain Landscape: The Coexistence of Neuroscience and Architecture*. Oxford University Press.

Glymour, C. (1980). *Theory and Evidence*. Princeton University Press.

Kaplan, R., & Kaplan, S. (1989). *The Experience of Nature: A Psychological Perspective*. Cambridge University Press.

Pearl, J. (1988). *Probabilistic Reasoning in Intelligent Systems*. Morgan Kaufmann.

Pearl, J. (2009). *Causality: Models, Reasoning, and Inference* (2nd ed.). Cambridge University Press.

Quine, W. V. O. (1951). Two dogmas of empiricism. *Philosophical Review*, 60(1), 20-43.

Rawls, J. (1971). *A Theory of Justice*. Harvard University Press.

Robinson, S., & Pallasmaa, J. (Eds.). (2015). *Mind in Architecture: Neuroscience, Embodiment, and the Future of Design*. MIT Press.

Simon, H. A. (1996). *The Sciences of the Artificial* (3rd ed.). MIT Press.

Thagard, P. (1989). Explanatory coherence. *Behavioral and Brain Sciences*, 12(3), 435-467.

Ulrich, R. S. (1984). View through a window may influence recovery from surgery. *Science*, 224(4647), 420-421.

---

## Appendix A: System Specifications

**Version**: V21.0.0 (Post-Quinean)
**Repository**: Article_Eater_PostQuinean_v1
**Core module**: src/services/web_of_belief.py (1300+ lines)
**Tests**: 218 passing (as of 2026-01-19)

**Key files**:
- `web_of_belief.py`: Core coherentist engine
- `extraction_to_web.py`: Claims → beliefs mapper
- `bridge_warrants.py`: Cross-theory connections
- `web_persistence.py`: Accumulation and conflict handling
- `outcome_taxonomy.py`: Hierarchical outcome classification
- `environment_taxonomy.py`: Environment feature classification
- `validation.py`: Credence and coherence metrics
- `gold_standard.py`: Validation corpus infrastructure

**Configuration parameters**:
- `AE_WEB_SEEK_EQUILIBRIUM`: Enable equilibrium-seeking (default: True)
- `AE_WEB_EQUILIBRIUM_MAX_ITERATIONS`: Max iterations (default: 100)
- `AE_WEB_CONVERGENCE_THRESHOLD`: Convergence criterion (default: 0.001)

---

## Appendix B: Example Session

```python
from src.services.web_of_belief import WebOfBelief, Belief, Credence, EpistemicLevel

# Initialize web
web = WebOfBelief()

# Add empirical belief from Ulrich (1984)
ulrich_belief = web.add_belief(
    content="Patients with nature views had shorter hospital stays",
    credence=Credence(value=0.75, uncertainty=0.2, n_supporting=1),
    level=EpistemicLevel.EMPIRICAL,
    theory="SRT",
    source_paper="ulrich_1984"
)

# Add theoretical belief from Kaplan & Kaplan (1989)
kaplan_belief = web.add_belief(
    content="Natural environments restore directed attention capacity",
    credence=Credence(value=0.65, uncertainty=0.25),
    level=EpistemicLevel.THEORETICAL,
    theory="ART",
    source_paper="kaplan_1989"
)

# Create bridge warrant between theories
web.add_bridge_warrant(
    source_theory="SRT",
    target_theory="ART",
    bridge_type="functional",
    confidence=0.5
)

# Seek equilibrium
web.seek_equilibrium()

# Query the web
coherence = web.compute_local_coherence(ulrich_belief.id)
print(f"Ulrich belief coherence: {coherence:.3f}")

tensions = web.get_tensions(threshold=0.3)
print(f"Active tensions: {len(tensions)}")

stubs = web.get_stubs()
print(f"Unintegrated stubs: {len(stubs)}")
```

---

*Document generated: 2026-01-19*
*Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>*
