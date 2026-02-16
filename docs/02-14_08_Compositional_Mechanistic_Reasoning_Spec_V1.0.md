# Compositional Mechanistic Reasoning: A Specification
## The Generative Engine for Article Eater
## Version 1.0 — February 14, 2026

---

# PART I: WHY THIS MATTERS MORE THAN THE BN

## 1.1 The Insight

Article Eater currently has three reasoning engines planned or partially built:

1. **Bayesian Network inference** — parameter estimation within a fixed graph. Given variables and edges, compute conditional probabilities. Useful for answering: "Given that we observe X, what's the probability of Y?"

2. **Coherence assessment** — constraint satisfaction across the web of belief. Check whether claims fit together. Useful for answering: "Is this new finding consistent with what we already believe?"

3. **Entrenchment dynamics** — updating confidence based on new evidence, replication, critique. Useful for answering: "How much should we trust this claim now?"

All three are *conservative* — they operate on existing structure. The BN estimates parameters on a graph someone else built. Coherence checks consistency among existing claims. Entrenchment adjusts weights on existing nodes. None of them *generates* anything new.

What we demonstrated in the Ulrich (1984) nature-view example is qualitatively different. From the conjunction of:
- A finding (nature views speed hospital recovery)
- Eight Tier 1 frameworks (predictive processing, DMN/TPN dynamics, neuromodulatory systems, interoception, etc.)

We derived six novel testable predictions that no single framework or finding contained. This is **compositional mechanistic reasoning** (CMR) — the ability to trace causal mechanisms through multiple theoretical frameworks and generate new hypotheses by asking: "If this mechanism is correct, what else must be true?"

This is the difference between a system that organizes knowledge and a system that participates in scientific discovery. And it's what Article Eater should do.

## 1.2 What Changes

If we build an explicit CMR engine, the ROI per processed paper changes fundamentally:

| Without CMR | With CMR |
|---|---|
| Paper → extracted claims → web nodes | Paper → extracted claims → web nodes → **novel predictions** |
| Value: one more data point | Value: potential generator of new science |
| Output: literature review | Output: hypothesis generation engine |
| Metric: coverage | Metric: prediction quality + novelty |

The web of belief transforms from a knowledge repository into a **scientific reasoning partner** — something that doesn't just organize what's known but reveals what should be investigated next.

---

# PART II: THE REASONING PIPELINE

What I did in the Ulrich example is not one operation. It's a pipeline of six distinct inference types, each with its own logic, prerequisites, failure modes, and computational requirements. Formalizing each step is what makes the system auditable and improvable.

## Step 1: Causal Decomposition

**What it does**: Takes a finding and decomposes it into component causal variables.

**Example**: "Nature views speed hospital recovery" → {environmental stimulus = nature view; outcome = recovery time; mediators = ?cortisol, ?immune function, ?sleep, ?pain perception, ?mood; population = hospital patients; context = post-surgical}.

**Formal basis**: This is Bechtel and Richardson's (1993/2010) *decomposition strategy* — the most basic operation in mechanistic explanation. Break the phenomenon into component parts and look for contributions of each part.

**What the system needs**:
- An ontology of causal variable types relevant to cognitive neuroarchitecture (environmental features, perceptual processes, neural systems, physiological responses, psychological states, behavioral outcomes, wellbeing measures)
- A set of decomposition templates for common finding types (e.g., "environmental feature X affects outcome Y" → decompose Y into physiological, cognitive, affective, behavioral components)
- The ability to identify which variables in a finding are observed vs. inferred

**Failure modes**: Under-decomposition (treating "recovery" as atomic when it has components). Over-decomposition (splitting into so many variables that the mechanism becomes intractable). Decomposing along the wrong dimensions (physiological when the mechanism is cognitive, or vice versa).

**Current system status**: Not formalized. I did this implicitly using general neuroscience knowledge. Article Eater would need the variable ontology and decomposition templates to do it systematically.

---

## Step 2: Framework Matching

**What it does**: For each decomposed variable, searches the Tier 1 framework library to find frameworks that have something to say about that variable.

**Example**: "cortisol" → matched by {neuromodulatory systems (HPA axis), interoceptive inference (physiological state → affect construction), DMN/TPN dynamics (cortisol linked to DMN suppression)}. "Recovery time" → matched by {memory systems (consolidation during rest), neuromodulatory systems (allostatic load)}.

**Formal basis**: This is Darden's (2002) *schema instantiation* — the application of an abstract mechanism framework to a specific case. The framework provides the schema; the finding provides the specific entities that fill the schema's roles.

**What the system needs**:
- For each Tier 1 framework, an explicit **scope declaration**: what variables does this framework address? What processes does it cover? Where does it NOT apply?
- A variable-to-framework index: which frameworks speak to which variables? This is a many-to-many mapping (cortisol is addressed by neuromodulatory systems, interoceptive inference, and memory systems).
- Matching strength grades: some frameworks speak centrally to a variable (HPA axis → cortisol is central), others peripherally (DMN/TPN dynamics → cortisol is secondary).

**Failure modes**: Missing matches (framework is relevant but not retrieved — the retrieval problem Gentner, 1993, identified for analogical reasoning). False matches (framework seems relevant on surface features but the mechanism doesn't actually apply). Overmatching (every framework gets matched to everything, producing an unmanageable explosion of mechanism traces).

**Current system status**: The Tier 1 framework nodes exist (in the theory tier architecture document), but they lack explicit scope declarations and variable-to-framework indices. Building these is a prerequisite.

---

## Step 3: Mechanism Tracing

**What it does**: For each matched framework, traces the causal mechanism from the environmental stimulus through intermediate variables to the outcome variable.

**Example**: Predictive processing matched to "nature views":
```
Nature view → visual processing of scene statistics →
LOW prediction error (1/f spectral match to generative model) →
LOW precision-weighting demand →
LOW metabolic cost of perceptual processing →
REDUCED noradrenergic arousal →
REDUCED HPA axis activation →
LOWER cortisol →
(connects to recovery outcome via immune function, hippocampal integrity)
```

**Formal basis**: This is Darden and Craver's (2002) *forward chaining* — starting from known (or hypothesized) mechanism components and reasoning forward to trace the productive continuity of the mechanism. Each step in the chain is a causal link with specific entities performing specific activities.

The critical insight from Machamer, Darden, and Craver (2000) is that mechanisms are sequences of *activities* performed by *entities* that are *productive* of changes from start to finish. Each link in the trace must specify: what entity is acting, what activity it performs, and what change it produces.

**What the system needs**:
- **Mechanistic Templates** (already specified in the tier architecture as "Tier 1 → Template" connections). Each template is a small DAG fragment:
  ```
  [Entity A] --performs--> [Activity 1] --produces--> [Change in Entity B]
  [Entity B] --performs--> [Activity 2] --produces--> [Change in Entity C]
  ...
  ```
- **Cross-framework bridging rules**: When a trace exits one framework and enters another (e.g., "reduced noradrenergic arousal" exits the predictive processing framework and enters the neuromodulatory framework), the system needs explicit bridge rules specifying which variables are shared between frameworks and how they connect.
- **Parameter constraints**: Each link should carry estimated effect magnitude, temporal dynamics (onset, duration, decay), and dose-response shape where known. Without these, traces are qualitatively plausible but quantitatively unconstrained.
- **Scope conditions**: Each link should carry conditions under which it holds. "1/f spectral match → low prediction error" holds for typical visual systems but may not hold for individuals with visual processing disorders.

**Failure modes**: 
- **Gap-jumping**: Skipping intermediate steps that are necessary (going directly from "nature view" to "lower cortisol" without specifying the perceptual mechanism).
- **Confabulated links**: Inserting a plausible-sounding step that isn't actually supported by evidence (my greatest vulnerability as an LLM).
- **Level confusion**: Mixing levels of analysis inappropriately (neural → psychological → neural without proper cross-level bridging — see Craver, 2007, on multilevel mechanisms).
- **Scope violation**: Applying a mechanism outside its validated scope conditions.

**Current system status**: The mechanistic templates exist conceptually (described in the tier architecture) but are not formalized as queryable data structures. Building the template library with explicit entities, activities, parameter constraints, and scope conditions is the core engineering task.

---

## Step 4: Prediction Generation via Interventionist Reasoning

**What it does**: Once a mechanism trace is complete, generates novel predictions by applying Woodward's (2003) interventionist logic: "If we intervene on variable X in the mechanism, what happens to downstream variables?"

**Example**: The mechanism trace says nature views reduce cortisol because of spectral match → low prediction error. Woodward's framework asks:

1. **Substitute the cause**: If the mechanism is spectral match (not "natureness" per se), then ANY stimulus with 1/f spectral statistics should produce the same effect. → **Prediction 1**: Artificial fractal scenes should produce similar recovery benefits.

2. **Vary a moderator**: If the mechanism goes through noradrenergic arousal reduction, then individuals with higher baseline arousal have more dynamic range for reduction. → **Prediction 2**: High-anxiety patients should benefit more.

3. **Block the pathway**: If the mechanism requires noradrenergic reduction, then pharmacologically preventing that reduction should block the benefit. → **Prediction 3**: Beta-blockers should not affect the benefit (they block a different pathway), but noradrenergic agonists should.

4. **Change the temporal context**: If cortisol reduction is the key mediator, the effect should be largest when cortisol is highest. → **Prediction 4**: Pre-surgical nature views should be more effective than post-recovery views.

5. **Vary the individual**: If affect is constructed from interoceptive prediction, then individuals with poor interoceptive sensitivity should show reduced affective benefit. → **Prediction 5**: Alexithymic patients should show physiological benefit but reduced subjective wellbeing improvement.

6. **Cross-cultural variation**: If the mechanism depends on the generative model's priors (evolutionary calibration to natural statistics), then the benefit should vary with individuals' visual ecology. → **Prediction 6**: Cultures with extensive natural scene experience should show larger effects.

**Formal basis**: Woodward's (2003) interventionist theory of causation, which defines causation in terms of "what-if-things-had-been-different" (w-questions). A causal claim "X causes Y" is true if and only if there exists an intervention on X that would change Y. Each prediction follows from asking a specific w-question about a specific link in the mechanism trace.

This connects directly to Craver's (2007) account of multilevel mechanistic explanation: each level of the mechanism provides different intervention points, and predictions at different levels have different testability characteristics (molecular interventions are more precise but less ecologically valid; environmental interventions are more ecologically valid but less mechanistically specific).

**What the system needs**:
- A **prediction generation grammar** — a set of formal rules for deriving predictions from mechanism traces. The six prediction types above (substitute cause, vary moderator, block pathway, change temporal context, vary individual, cross-cultural variation) should be formalized as reusable operations.
- Each generated prediction should carry:
  - **Derivation chain**: Which framework(s), which mechanism trace, which interventionist operation
  - **Confidence grading**: How well-supported is each link in the derivation? (If any link is weak, the prediction inherits that weakness)
  - **Testability assessment**: What experimental design would test this prediction? What measures would be needed? What effect size is expected?
  - **Novelty assessment**: Is this prediction already known/tested? (Check against existing Tier 3 claims in the web)
  - **Independence assessment**: Does this prediction follow from multiple independent mechanism traces, or only one? (Multi-framework convergence → higher priority)

**Failure modes**:
- **Generating predictions that are already known** (waste of effort, but easy to check against the web)
- **Generating predictions that are untestable** (no feasible experimental design — e.g., predictions requiring interventions on evolutionary history)
- **Over-confident predictions from weak derivation chains** (a single uncertain link makes the whole prediction uncertain, but this is easy to lose track of in long chains)
- **Assuming linearity when mechanisms are nonlinear** (e.g., predicting that double the prediction error reduction produces double the cortisol reduction, when the HPA axis has threshold effects and ceiling effects)

**Current system status**: Not formalized at all. This is entirely new machinery.

---

## Step 5: Cross-Framework Convergence Assessment

**What it does**: Checks whether multiple independent frameworks generate the same (or compatible) predictions, and flags cases where frameworks generate contradictory predictions.

**Example**: For "nature views reduce cortisol":
- Predictive processing: predicts reduction via spectral match → low prediction error
- DMN/TPN dynamics: predicts reduction via low attentional demand → DMN engagement → parasympathetic dominance
- Embodied cognition: predicts reduction via natural affordances → relaxed postural adjustments → reduced muscle tension → vagal tone increase

Three frameworks, three different mechanism traces, same directional prediction. This is strong convergence. But note: predictive processing and interoceptive inference are NOT independent (interoceptive inference IS predictive processing applied to the body). So it's really 2.5 independent lines, not 3.

**Formal basis**: This is a form of Thagard's (1989, 1992) explanatory coherence, but specifically focused on *prediction-level* coherence rather than belief-level coherence. Multiple independent derivation paths to the same prediction provide stronger warrant than any single path.

Gentner and Markman's (1997) work on structural alignment is relevant here: the convergence is informative precisely when the frameworks share relational structure (same prediction) but differ in surface features (different entities, different activities). The more structurally diverse the frameworks that converge, the more informative the convergence.

**What the system needs**:
- A **framework independence matrix** — which frameworks share theoretical commitments, neural substrates, or key assumptions? This determines whether convergence is genuine or pseudo-convergence.
  - Predictive processing ↔ interoceptive inference: HIGH dependence (shared theoretical core)
  - Predictive processing ↔ spatial navigation: LOW dependence (different neural substrates, different theoretical origins)
  - DMN/TPN ↔ neuromodulatory systems: MEDIUM dependence (shared neural substrate, somewhat independent theoretical development)
- An **effective independence score** for each multi-framework prediction
- **Contradiction detection**: When frameworks generate contradictory predictions, this is epistemically interesting — it identifies either a boundary condition, a scope limitation, or a genuine theoretical conflict that needs empirical resolution.

**Current system status**: The cross-framework integration links exist in the tier architecture specification, but the independence matrix and effective independence scoring are not formalized.

---

## Step 6: Prediction Prioritization

**What it does**: Ranks generated predictions by expected scientific value, using multiple criteria.

**Ranking criteria**:
1. **Convergence score**: How many independent frameworks support this prediction?
2. **Derivation chain strength**: What's the weakest link in the derivation? (The chain is only as strong as its weakest link)
3. **Novelty**: Is this prediction already tested? If untested, how surprising would confirmation/disconfirmation be?
4. **Testability**: How feasible is the required experiment? What sample size? What measures?
5. **Theoretical leverage**: Would confirming/disconfirming this prediction discriminate between competing frameworks? (Predictions that only follow from one framework, and whose failure would refute that framework, have high theoretical leverage — the Popperian quality)
6. **Practical import**: Would confirming this prediction change architectural design practice?

**Formal basis**: This is a combination of Myung and Pitt's (1997) model selection criteria, Popper's (1963) falsificationist logic (bold predictions carry more epistemic weight), and the Value of Information (VOI) framework from decision theory (the value of a prediction is proportional to how much the web's structure would change if it were confirmed or disconfirmed).

**What the system needs**:
- VOI computation integrated with the existing web (Sprint 5 already planned)
- A ranking function that combines the criteria above
- Output format: a prioritized list of predictions with full derivation chains, confidence gradings, and suggested experimental designs

---

# PART III: WHAT MUST BE BUILT

## 3.1 The Mechanistic Template Library

This is the core knowledge structure that makes CMR possible. Each template is a small causal DAG fragment encoding a known mechanism pathway.

**Structure of a template**:
```yaml
template_id: PP_SPECTRAL_MATCH_001
template_name: "Visual spectral match → prediction error reduction"
source_framework: PREDICTIVE_PROCESSING
derivation_quality: HIGH  # tight deduction from framework principles

entities:
  - visual_stimulus: {type: environmental_feature, measurable: true}
  - spatial_frequency_spectrum: {type: stimulus_property, unit: "cycles/degree"}
  - visual_generative_model: {type: neural_model, location: "visual cortex hierarchy"}
  - prediction_error: {type: neural_signal, measurable_via: ["EEG_MMN", "fMRI_prediction_error"]}
  - precision_weighting: {type: neural_process, modulated_by: ["attention", "neuromodulators"]}

causal_chain:
  - step1: visual_stimulus → spatial_frequency_spectrum
    type: physical_property
    certainty: HIGH (directly measurable)
  - step2: spatial_frequency_spectrum + visual_generative_model → prediction_error
    type: computational
    certainty: HIGH (well-established in predictive coding literature)
    moderators: [observer_familiarity, cultural_visual_ecology, attention_state]
  - step3: prediction_error → metabolic_cost
    type: neurophysiological
    certainty: MEDIUM (supported but magnitude estimates vary)
    parameter_range: {onset_ms: 50-200, scaling: approximately_linear_below_threshold}

scope_conditions:
  - requires: intact visual system
  - requires: conscious visual processing (not subliminal)
  - applies_to: static and dynamic visual scenes
  - uncertain_for: very brief exposures (<100ms)

connected_templates:
  - DOWNSTREAM: NM_METABOLIC_COST_TO_HPA_001
  - DOWNSTREAM: DMN_PROCESSING_DEMAND_001
  - CROSS_FRAMEWORK: IC_PREDICTION_ERROR_TO_AFFECT_001

key_references:
  - Rao & Ballard (1999), cited ~5000
  - Friston (2005), cited ~8000
  - Bastos et al. (2012), cited ~2500
```

**How many templates are needed?** For the initial implementation focused on cognitive neuroarchitecture, I estimate:
- ~8-12 templates per Tier 1 framework (covering major mechanism pathways)
- × 8 frameworks
- = ~64-96 templates total
- Plus ~20-30 cross-framework bridging templates
- = **~85-125 templates** for initial coverage

This is tractable. Each template is 10-20 structured fields. The knowledge exists in the literature — it needs to be formalized, not discovered.

## 3.2 The Prediction Generation Grammar

A set of formal operations that take a mechanism trace and produce predictions:

| Operation | Input | Output | Formal Basis |
|---|---|---|---|
| SUBSTITUTE_CAUSE | mechanism trace + alternative cause with same relevant properties | prediction: alternative cause → same effect | Woodward interventionism |
| VARY_MODERATOR | mechanism trace + identified moderator | prediction: moderator variation → effect variation | Standard moderation logic |
| BLOCK_PATHWAY | mechanism trace + identified mediator | prediction: blocking mediator → blocking effect | Woodward interventionism |
| VARY_TEMPORAL_CONTEXT | mechanism trace + temporal dynamics | prediction: temporal manipulation → effect variation | Mechanism temporal parameters |
| VARY_INDIVIDUAL | mechanism trace + individual difference variable linked to mechanism component | prediction: individual variation → effect variation | Standard individual differences |
| CROSS_CULTURAL | mechanism trace + culturally variable parameter | prediction: cultural variation → effect variation | Generative model calibration |
| COMBINE_MECHANISMS | two mechanism traces with shared intermediate variable | prediction: combined manipulation → combined effect | Compositional mechanism logic |
| DOSE_RESPONSE | mechanism trace + parameter ranges | prediction: dose variation → response curve shape | Mechanism quantitative constraints |

Each operation has:
- **Preconditions**: What must be true of the mechanism trace for this operation to apply?
- **Postconditions**: What kind of prediction is generated?
- **Confidence propagation rule**: How does uncertainty in the trace affect certainty of the prediction?
- **Novelty check**: Search the web for existing findings that test this prediction

## 3.3 The Framework Independence Matrix

An 8×8 matrix encoding shared theoretical commitments between Tier 1 frameworks:

```
                    PP   SN   DP   DMN   NM   IC   MS   EC
Predictive Proc.    1.0  0.3  0.4  0.5   0.6  0.9  0.3  0.4
Spatial Navigation  0.3  1.0  0.2  0.3   0.2  0.2  0.8  0.5
Dual-Process        0.4  0.2  1.0  0.5   0.4  0.3  0.3  0.3
DMN/TPN            0.5  0.3  0.5  1.0   0.6  0.4  0.4  0.2
Neuromodulatory    0.6  0.2  0.4  0.6   1.0  0.5  0.3  0.3
Interoception      0.9  0.2  0.3  0.4   0.5  1.0  0.2  0.4
Memory Systems     0.3  0.8  0.3  0.4   0.3  0.2  1.0  0.3
Embodied Cognition 0.4  0.5  0.3  0.2   0.3  0.4  0.3  1.0
```

Values = degree of theoretical/mechanistic dependence (0 = fully independent, 1 = identical). The high PP↔IC value (0.9) reflects that interoceptive inference IS predictive processing applied to the body. The high SN↔MS value (0.8) reflects shared hippocampal substrate.

**Effective independence for a multi-framework prediction** = product of (1 - pairwise dependence) for all framework pairs supporting the prediction. If PP, DMN, and NM all predict the same thing:
- PP↔DMN independence: 1 - 0.5 = 0.5
- PP↔NM independence: 1 - 0.6 = 0.4
- DMN↔NM independence: 1 - 0.6 = 0.4
- Effective independence ≈ geometric mean of pairwise independences = 0.43
- Adjusted convergence score: 3 frameworks × 0.43 independence = ~1.3 effective independent lines

Compare: PP, SN, and EC all predict the same thing:
- PP↔SN: 1 - 0.3 = 0.7
- PP↔EC: 1 - 0.4 = 0.6
- SN↔EC: 1 - 0.5 = 0.5
- Effective independence ≈ 0.60
- Adjusted convergence score: 3 × 0.60 = ~1.8 effective independent lines

The second case provides stronger warrant despite the same number of frameworks, because the frameworks are more independent.

## 3.4 Scope Declaration Registry

For each Tier 1 framework, explicit boundaries:

```yaml
framework: PREDICTIVE_PROCESSING
applies_to:
  - all perceptual processing (visual, auditory, somatosensory, olfactory)
  - motor planning and execution (active inference)
  - affective processing (interoceptive prediction)
  - learning and memory (model updating)
  - social cognition (prediction of others' behavior)

does_not_apply_to:
  - reflexive/spinal processes (too low-level for hierarchical prediction)
  - early developmental processes before cortical hierarchy established
  - [CONTESTED] consciousness per se (some argue PP explains it, others disagree)

known_problems:
  - dark_room_problem: framework predicts organisms should minimize prediction error by seeking low-stimulation environments; organisms don't do this. Resolution attempts: expected free energy (Friston et al., 2015), epistemic foraging (Schwartenbeck et al., 2013).
  - unfalsifiability_concern: framework may be so flexible it can accommodate any finding post hoc. Counter: specific implementations (e.g., specific neural circuit predictions) ARE testable.
  - precision_weighting_vagueness: "precision" is invoked to explain many phenomena but is hard to independently measure.

contested_aspects:
  - whether precision IS attention (Feldman & Friston, 2010) or merely correlated
  - whether active inference replaces or supplements reinforcement learning
  - whether the Free Energy Principle is a substantive empirical claim or a mathematical truism
```

Each framework gets one of these. This is what makes derivations auditable — when a prediction depends on a contested aspect of a framework, the system flags it.

---

# PART IV: THE PHILOSOPHICAL FOUNDATIONS

## 4.1 Mechanistic Explanation (Machamer, Darden, & Craver, 2000)

The CMR system is grounded in the "new mechanistic philosophy of science" that has become the dominant framework for understanding explanation in the biological and cognitive sciences over the past 25 years. Machamer, Darden, and Craver's (2000) foundational paper defines mechanisms as "entities and activities organized such that they are productive of regular changes from start or set-up to finish or termination conditions." This definition provides the ontology for mechanism traces: every link in a trace must specify an entity performing an activity that produces a change.

Darden's subsequent work (2002, 2006) identified specific reasoning strategies for mechanism discovery: **schema instantiation** (our Step 2: Framework Matching), **forward chaining/backtracking** (our Step 3: Mechanism Tracing), and **modular subassembly** (composing known mechanism modules into novel configurations — our Step 4's COMBINE_MECHANISMS operation). Importantly, Darden showed these strategies are not just post hoc rationalizations of discovery; they are genuinely *generative* — they produce new hypotheses that can then be tested.

Craver's (2007) *Explaining the Brain* extended this framework to multilevel mechanisms in neuroscience, providing the formal apparatus for reasoning across levels (molecular → cellular → circuit → system → behavioral → psychological). Our Tier 1 frameworks span these levels — predictive processing operates at the circuit/system level, neuromodulatory systems at the molecular/cellular level, DMN/TPN at the system level, embodied cognition at the behavioral level. The mechanistic template library must encode the level(s) at which each template operates, and cross-level bridging templates must be explicit about how they connect levels.

## 4.2 Interventionist Causation (Woodward, 2003)

Woodward's *Making Things Happen* provides the formal logic for Step 4 (Prediction Generation). The key idea is that causal claims are claims about what would happen under interventions. A mechanism trace is a series of causal claims, each of which can be interrogated interventionistically: "If we intervened to change this variable, what would happen downstream?"

This is enormously productive because each intervention point in a mechanism trace generates a family of predictions — substitution predictions, blocking predictions, dose-response predictions, moderator predictions. The prediction generation grammar formalizes these families.

The important constraint from Woodward is that interventions must be *surgical* — they must change the target variable without changing other variables except through the causal pathway. In our system, this means checking whether a proposed prediction could be tested with a clean intervention or whether confounds are unavoidable. Predictions requiring confounded interventions should be flagged as "testable in principle but hard in practice."

## 4.3 Analogical Reasoning (Gentner, 1983; Holyoak & Thagard, 1995)

When the CMR system encounters a finding that partially matches a mechanism template but doesn't fit perfectly, the reasoning shifts from deduction to analogy. Gentner's (1983) structure-mapping theory provides the formal apparatus: analogies map relational structure (not surface features) from a base domain to a target domain. The quality of the analogy depends on the degree of structural alignment — how much of the relational structure transfers.

In our system, analogical reasoning is invoked specifically when:
- A finding involves variables that are *similar to but not identical with* a template's variables (e.g., "acoustic complexity" instead of "visual complexity" — the predictive processing template may apply analogically)
- A mechanism trace from one domain (vision) is being applied to another (audition, olfaction) — the structural relationships (complexity → prediction error → arousal) may transfer even though the entities differ
- A new finding doesn't match any existing template exactly but structurally resembles an exemplar node — the analogy to the exemplar supports tentative mechanistic interpretation

Holyoak and Thagard's (1995) multi-constraint theory adds that analogical mapping is guided not just by structural similarity but also by pragmatic goals and semantic similarity. In our system, the pragmatic goal is always "find a mechanistic explanation for this finding" — which constrains the mapping toward causally relevant structural correspondences.

**Critical limitation**: As Gentner et al. (1993) showed, people (and LLMs) are better at *evaluating* analogies than *retrieving* them. The system needs to do deliberate retrieval — systematically searching the template library for structural matches — rather than relying on surface similarity. This argues for the template library to be indexed by relational structure (causal pattern type, variable roles) rather than by surface content (specific brain areas, specific environmental features).

## 4.4 Inference to the Best Explanation (Lipton, 2004)

When multiple mechanism traces can explain the same finding, the system needs criteria for selecting among them. Lipton's (2004) *Inference to the Best Explanation* provides the philosophical framework: we should prefer the explanation that would, if true, provide the most understanding of the phenomenon.

"Best" decomposes into several dimensions that our system can operationalize:
- **Scope**: Does the explanation account for related phenomena or just this one?
- **Precision**: Does the explanation make specific, testable predictions or only vague directional ones?
- **Mechanism**: Does the explanation specify the causal pathway or just the correlation?
- **Unification**: Does the explanation connect this phenomenon to well-understood mechanisms in other domains?
- **Simplicity**: Does the explanation invoke the minimum number of novel entities and processes?

These dimensions are computable from the derivation chain and the framework properties.

---

# PART V: IMPLEMENTATION STRATEGY

## 5.1 Where This Fits in the Article Eater Architecture

CMR is NOT a replacement for the BN, coherence engine, or entrenchment dynamics. It's a layer that sits *on top* of them:

```
[Level 1] Extraction: Papers → Claims + Relations
[Level 2] Web: Claims + Relations → Coherent belief network
[Level 3] BN: Belief network → Causal graph with parameters
[Level 4] CMR: Causal graph + Framework templates → Novel predictions ← NEW
```

The BN tells you what's probable given what you know. CMR tells you what you should investigate next and why.

## 5.2 Implementation Phases

**Phase 1: Build the Template Library (4-6 weeks)**
- Formalize ~100 mechanistic templates across 8 Tier 1 frameworks
- Each template: entities, activities, causal chain, scope conditions, parameters, references
- Index by relational structure for analogical retrieval
- This is labor-intensive knowledge engineering but the knowledge exists in the literature
- Could be partially automated: LLM reads framework review papers → generates candidate templates → expert review

**Phase 2: Build the Prediction Generation Grammar (2-3 weeks)**
- Implement 8 prediction generation operations (substitute, vary moderator, block, temporal, individual, cross-cultural, combine, dose-response)
- Each operation: preconditions, postconditions, confidence propagation
- Novelty checker: search web for existing findings that test each prediction
- Output: structured prediction objects with full derivation chains

**Phase 3: Build the Independence Matrix and Scope Registry (1-2 weeks)**
- Framework independence matrix (8×8, manually constructed with expert input)
- Scope declaration for each framework
- Known problems and contested aspects catalogued
- This is expert knowledge — needs David's input

**Phase 4: Integration Testing (2-3 weeks)**
- Gold standard test case: Ulrich (1984) nature-view finding → should reproduce the 6 predictions (or better ones)
- Second test case: Mehaffy & Salingaros complexity-preference finding → should generate predictions about fractal dimension, cultural variation, temporal dynamics
- Third test case: Joye & Dewitte (2018) theoretical paper → should generate predictions from their proposed mechanisms
- Anomaly detection test: Give the system a finding that contradicts a well-supported framework → should flag the contradiction and generate discriminating predictions

**Phase 5: Production Integration (2-3 weeks)**
- Connect CMR engine to the web of belief (read web structure, write predictions as new nodes)
- Generated predictions become DERIVED_HYPOTHESIS nodes (from the non-empirical spec)
- Each prediction linked to its derivation chain via THEORETICALLY_PREDICTS edges
- Predictions queued for VOI assessment (Sprint 5)
- Top-ranked predictions surfaced to the user as "suggested investigations"

## 5.3 Total Timeline

~11-17 weeks, overlapping with existing sprints. Critical dependency: the mechanistic template library (Phase 1) can start immediately and is the longest pole.

## 5.4 What This Requires from David

This is not fully automatable. The system needs:
1. **Expert review of templates**: Are the mechanism traces correct? Are scope conditions accurate? Are the parameter ranges reasonable?
2. **Independence matrix calibration**: Only an expert who works across all 8 frameworks can judge how independent they really are.
3. **Scope declaration review**: Where I (Claude) describe framework boundaries, you need to check whether I'm being too generous or too conservative.
4. **Gold standard prediction evaluation**: When the system generates predictions, you need to evaluate whether they're genuinely novel, testable, and scientifically interesting — or obvious, untestable, or trivial.

---

# PART VI: WHAT THIS IS AND ISN'T

## 6.1 What it is

- A formalization of the reasoning that trained scientists do when they interpret findings through theoretical frameworks
- An auditable, transparent version of what I did conversationally with the Ulrich example
- A system for generating *candidates* for scientific investigation — hypotheses, not conclusions
- A way to maximize the scientific value extracted from each paper processed

## 6.2 What it isn't

- A replacement for human scientific judgment (it generates candidates; humans evaluate them)
- A proof system (the predictions are *plausible inferences*, not deductive certainties)
- A way to bypass empirical testing (every prediction must still be tested experimentally)
- Complete (the template library will always be incomplete; the independence matrix will always be approximate; scope conditions will always be partially unknown)
- Immune to the garbage-in-garbage-out problem (if Tier 1 frameworks are wrong, CMR generates wrong predictions — but it generates them transparently, so the error is traceable)

## 6.3 The key advantage over doing this conversationally

When I do this reasoning in conversation, you get:
- Predictions that seem compelling but whose derivation is invisible
- No way to check whether I'm relying on contested framework assumptions
- No way to detect whether my "convergence across frameworks" is genuine or pseudo-convergence
- No way to reproduce the reasoning or apply it systematically to other findings
- No audit trail

When Article Eater's CMR engine does this reasoning, you get:
- Every prediction tagged with its full derivation chain
- Every link in the derivation tagged with its confidence, source, and contestation status
- Convergence scores adjusted for framework independence
- Systematic application to every finding in the web (not just the ones we happen to discuss)
- A permanent, queryable record of what was predicted, when, from what, and what happened when tested

That's the difference between science and conversation.

---

# REFERENCES

Bastos, A. M., Usrey, W. M., Adams, R. A., Mangun, G. R., Fries, P., & Friston, K. J. (2012). Canonical microcircuits for predictive coding. *Neuron*, *76*(4), 695–711. https://doi.org/10.1016/j.neuron.2012.10.038 (Cited by ~2,500)

Bechtel, W., & Richardson, R. C. (1993/2010). *Discovering complexity: Decomposition and localization as strategies in scientific research*. Princeton University Press. (Cited by ~3,000)

Craver, C. F. (2007). *Explaining the brain: Mechanisms and the mosaic unity of neuroscience*. Oxford University Press. (Cited by ~4,000)

Darden, L. (2002). Strategies for discovering mechanisms: Schema instantiation, modular subassembly, forward/backward chaining. *Philosophy of Science*, *69*(S3), S354–S365. (Cited by ~300)

Darden, L. (2006). *Reasoning in biological discoveries: Essays on mechanisms, interfield relations, and anomaly resolution*. Cambridge University Press. (Cited by ~400)

Darden, L., & Craver, C. F. (2002). Strategies in the interfield discovery of the mechanism of protein synthesis. *Studies in History and Philosophy of Biological and Biomedical Sciences*, *33*(1), 1–28. (Cited by ~300)

Gentner, D. (1983). Structure-mapping: A theoretical framework for analogy. *Cognitive Science*, *7*(2), 155–170. (Cited by ~5,000)

Gentner, D., Rattermann, M. J., & Forbus, K. D. (1993). The roles of similarity in transfer: Separating retrievability from inferential soundness. *Cognitive Psychology*, *25*(4), 524–575. (Cited by ~1,000)

Gentner, D., & Markman, A. B. (1997). Structure mapping in analogy and similarity. *American Psychologist*, *52*(1), 45–56. (Cited by ~2,500)

Holyoak, K. J., & Thagard, P. (1995). *Mental leaps: Analogy in creative thought*. MIT Press. (Cited by ~3,000)

Lipton, P. (2004). *Inference to the best explanation* (2nd ed.). Routledge. (Cited by ~4,500)

Machamer, P., Darden, L., & Craver, C. F. (2000). Thinking about mechanisms. *Philosophy of Science*, *67*(1), 1–25. (Cited by ~5,000)

Myung, I. J., & Pitt, M. A. (1997). Applying Occam's razor in modeling cognition: A Bayesian approach. *Psychonomic Bulletin & Review*, *4*(1), 79–95. (Cited by ~800)

Popper, K. R. (1963). *Conjectures and refutations: The growth of scientific knowledge*. Routledge. (Cited by ~20,000)

Thagard, P. (1989). Explanatory coherence. *Behavioral and Brain Sciences*, *12*(3), 435–467. (Cited by ~1,500)

Thagard, P. (1992). *Conceptual revolutions*. Princeton University Press. (Cited by ~1,500)

Woodward, J. (2003). *Making things happen: A theory of causal explanation*. Oxford University Press. (Cited by ~8,000)

---

**Source conversation**: Article Eater session, February 14, 2026
**Transcript reference**: current session

**END OF DOCUMENT**
