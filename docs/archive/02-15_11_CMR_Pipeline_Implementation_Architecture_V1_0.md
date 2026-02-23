# CMR PIPELINE: IMPLEMENTATION ARCHITECTURE
## Article Eater — Sprint 8 Reference
## Version 1.0 — February 15, 2026

**Purpose**: Turn the 89KB CMR narrative spec into implementable code architecture.
This document provides: module structure, function signatures, data flow, a complete
worked example, and the minimal viable pipeline (MVP) that CC should build first.

**Prerequisite**: Sprint 7 must be complete (frameworks, templates, independence matrix in DB).

---

# PART 1: MODULE STRUCTURE

```
src/cmr/
├── __init__.py
├── pipeline.py              # Main orchestrator: run_cmr_pipeline()
├── step1_decomposition.py   # Causal Decomposition
├── step2_matching.py        # Framework Matching
├── step3_tracing.py         # Mechanism Tracing
├── step4_prediction.py      # Prediction Generation
├── step5_convergence.py     # Cross-Framework Convergence
├── step6_failure.py         # Composition Failure Detection
├── step7_prioritization.py  # Prediction Prioritization
├── step8_learning.py        # Template Learning (deferred)
├── models.py                # All CMR-specific data classes
└── operations.py            # The 10 prediction generation operations
```

---

# PART 2: DATA MODELS

All models extend the dataclasses from Sprint 7 (doc 07 Section 3).
These are the CMR-SPECIFIC models that don't exist yet.

```python
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple, Set
from enum import Enum

# --- From Sprint 7 (already exist) ---
# MaturityLevel, BridgingQuality, AnalysisLevel, CausalLink,
# MechanisticTemplate, ScopeCondition, Moderator, ParameterEstimate

# --- CMR-specific models ---

class ReasoningGoal(Enum):
    """R13: What is the CMR pipeline trying to do?"""
    EXPLAIN = "explain"             # Find mechanism behind known finding
    PREDICT = "predict"             # Generate novel testable predictions
    DESIGN_EXPERIMENT = "design"    # Suggest experiments to test mechanisms
    FIND_BOUNDARY = "boundary"      # Identify scope limits of a finding
    CROSS_CULTURAL = "cultural"     # Explore cultural variation

class PredictionLevel(Enum):
    """R6: Woodward's type vs token distinction"""
    TYPE = "type"       # Population-level: "high-anxiety people should..."
    TOKEN = "token"     # Individual-level: "this patient should..."

class CauseType(Enum):
    """R7: Woodward's total vs contributing cause"""
    TOTAL = "total"             # Blocking this eliminates the entire effect
    CONTRIBUTING = "contributing"  # Blocking this reduces but doesn't eliminate

class PredictionOperation(Enum):
    """The 10 interventionist operations from CMR spec"""
    SUBSTITUTE_CAUSE = "substitute_cause"
    VARY_MODERATOR = "vary_moderator"
    BLOCK_PATHWAY = "block_pathway"
    VARY_TEMPORAL = "vary_temporal"
    VARY_INDIVIDUAL = "vary_individual"
    CROSS_CULTURAL = "cross_cultural"
    COMBINE_MECHANISMS = "combine_mechanisms"
    DOSE_RESPONSE = "dose_response"
    TOTAL_VS_CONTRIBUTING = "total_vs_contributing"     # R7
    TYPE_VS_TOKEN = "type_vs_token"                     # R6

class CompositionFailureType(Enum):
    """R10: Barrett's failure taxonomy"""
    DEFINITIONAL = "definitional"     # Same term, different meaning
    MECHANISTIC = "mechanistic"       # Incompatible mechanisms for same phenomenon
    SCOPE = "scope"                   # Agree on mechanism, disagree on where it applies
    PARAMETER = "parameter"           # Same mechanism, different predicted values

# --- Pipeline I/O types ---

@dataclass
class DecomposedFinding:
    """Output of Step 1: Causal Decomposition"""
    finding_id: str
    source_paper_id: str
    original_text: str
    # Decomposed variables with role labels
    environmental_features: List[str]      # e.g., ["nature_view", "window_size"]
    perceptual_processes: List[str]        # e.g., ["visual_processing", "lsf_extraction"]
    neural_systems: List[str]             # e.g., ["V1", "amygdala", "HPA_axis"]
    physiological_responses: List[str]    # e.g., ["cortisol_reduction"]
    psychological_states: List[str]       # e.g., ["stress_reduction", "positive_affect"]
    behavioral_outcomes: List[str]        # e.g., ["faster_recovery"]
    population: Optional[str]             # e.g., "post-surgical patients"
    context_factors: List[str]            # e.g., ["hospital_setting", "48hr_exposure"]
    all_variables: List[str]              # flat union of above for matching

@dataclass
class FrameworkMatch:
    """Output of Step 2: one matched framework"""
    framework_id: str                     # e.g., "PP"
    match_quality: float                  # 0.0-1.0
    matched_variables: List[str]          # which decomposed variables matched
    unmatched_variables: List[str]        # which didn't — these are alignable differences (R5)
    relevant_template_ids: List[str]      # which templates in this framework are relevant
    structural_match: bool                # did it match at structural level (R4)?

@dataclass
class MechanismTrace:
    """Output of Step 3: a complete traced mechanism"""
    trace_id: str
    finding_id: str
    framework_ids: List[str]              # which frameworks contribute
    template_ids: List[str]               # which templates were composed
    links: List[CausalLink]               # the actual causal chain
    overall_maturity: MaturityLevel        # weakest link
    weakest_link_index: int               # which link is the bottleneck
    composition_warnings: List[str]       # R3: interference flags
    unmatched_variables: List[str]        # R5: alignable differences

@dataclass
class GeneratedPrediction:
    """Output of Step 4: a single prediction"""
    prediction_id: str
    statement: str                         # human-readable
    # Derivation
    operation: PredictionOperation
    source_trace_ids: List[str]
    template_ids: List[str]
    derivation_reasoning: str              # why this follows from the trace
    # Quality tags (R1, R6, R7, R8)
    confidence: float                      # 0.0-1.0, inherits weakest maturity
    weakest_maturity: MaturityLevel
    prediction_level: PredictionLevel      # R6
    cause_type: CauseType                  # R7
    modularity_concerns: List[str]         # R8
    # Testability
    suggested_design: Optional[str]
    suggested_measures: List[str]
    feasibility: Optional[str]             # HIGH/MEDIUM/LOW
    # Metadata
    novelty_assessment: Optional[str]
    theoretical_leverage: Optional[str]

@dataclass
class ConvergenceResult:
    """Output of Step 5 for a group of predictions about same outcome"""
    outcome_variable: str
    supporting_predictions: List[str]      # prediction_ids
    supporting_frameworks: List[str]       # framework_ids
    effective_independence: float           # R14: per-prediction independence score
    is_contradicted: bool
    contradicting_predictions: List[str]

@dataclass
class CompositionFailure:
    """Output of Step 6: where frameworks conflict"""
    failure_type: CompositionFailureType
    framework_a: str
    framework_b: str
    conflicting_variable: str
    description: str
    discriminating_prediction: Optional[GeneratedPrediction]

@dataclass
class PrioritizedPrediction:
    """Output of Step 7: prediction with priority score"""
    prediction: GeneratedPrediction
    convergence_score: float               # from Step 5
    novelty_score: float
    testability_score: float
    theoretical_leverage_score: float
    is_discriminating: bool                # from Step 6
    composite_priority: float              # weighted combination

@dataclass
class CMRPipelineResult:
    """Complete output of one pipeline run"""
    finding_id: str
    decomposition: DecomposedFinding
    framework_matches: List[FrameworkMatch]
    mechanism_traces: List[MechanismTrace]
    predictions: List[GeneratedPrediction]
    convergence_results: List[ConvergenceResult]
    composition_failures: List[CompositionFailure]
    prioritized_predictions: List[PrioritizedPrediction]
    # Summary stats
    n_predictions: int
    n_novel: int
    n_discriminating: int
    pipeline_metadata: Dict                # timing, template versions used, etc.
```

---

# PART 3: FUNCTION SIGNATURES

## Pipeline Orchestrator

```python
# src/cmr/pipeline.py

class CMRPipeline:
    """Main orchestrator. Stateless — all state comes from DB."""

    def __init__(self, db_session, template_library, framework_registry,
                 independence_matrix):
        self.db = db_session
        self.templates = template_library      # Dict[str, MechanisticTemplate]
        self.frameworks = framework_registry   # Dict[str, Tier1Framework]
        self.independence = independence_matrix # Dict[str, Dict[str, float]]

    def run(self, finding_text: str, source_paper_id: str,
            reasoning_goal: ReasoningGoal = ReasoningGoal.PREDICT
            ) -> CMRPipelineResult:
        """Execute the full 8-step pipeline on a single finding."""
        # Step 1
        decomposition = decompose_finding(finding_text, source_paper_id)
        # Step 2
        matches = match_frameworks(decomposition, self.frameworks,
                                   reasoning_goal)
        # Step 3
        traces = trace_mechanisms(matches, self.templates, decomposition)
        # Step 4
        predictions = generate_predictions(traces, reasoning_goal)
        # Step 5
        convergence = assess_convergence(predictions, self.independence)
        # Step 6
        failures = detect_composition_failures(traces, self.frameworks)
        # Step 6b: generate discriminating predictions from failures
        discriminators = generate_discriminating_predictions(failures)
        predictions.extend(discriminators)
        # Step 7
        prioritized = prioritize_predictions(predictions, convergence,
                                              failures)
        # Step 8: Template learning (deferred — needs confirmed predictions)

        return CMRPipelineResult(
            finding_id=decomposition.finding_id,
            decomposition=decomposition,
            framework_matches=matches,
            mechanism_traces=traces,
            predictions=predictions,
            convergence_results=convergence,
            composition_failures=failures,
            prioritized_predictions=prioritized,
            n_predictions=len(predictions),
            n_novel=sum(1 for p in prioritized if p.novelty_score > 0.5),
            n_discriminating=sum(1 for p in prioritized if p.is_discriminating),
            pipeline_metadata={"reasoning_goal": reasoning_goal.value},
        )

    def run_batch(self, findings: List[Tuple[str, str]],
                  reasoning_goal: ReasoningGoal = ReasoningGoal.PREDICT
                  ) -> List[CMRPipelineResult]:
        """Run pipeline on multiple findings. Future: parallelize."""
        return [self.run(text, paper_id, reasoning_goal)
                for text, paper_id in findings]
```

## Step 1: Causal Decomposition

```python
# src/cmr/step1_decomposition.py

def decompose_finding(finding_text: str, source_paper_id: str,
                      variable_ontology: Optional[Dict] = None
                      ) -> DecomposedFinding:
    """
    Decompose a finding into typed causal variables.

    MVP IMPLEMENTATION: Use LLM extraction with structured prompt.
    The variable_ontology constrains extraction to known variables.

    Future: hybrid approach — LLM extraction + fuzzy matching against
    controlled vocabulary from canonical decisions record.
    """
    # 1. Extract variables from finding text using LLM
    # 2. Classify each into role category (environmental, neural, etc.)
    # 3. Normalize to controlled vocabulary where possible
    # 4. Return structured DecomposedFinding
    pass
```

**Implementation note**: Step 1 is the only step that REQUIRES an LLM call.
Steps 2-7 are deterministic algorithms operating on the template library.
Step 8 requires human confirmation. This means the pipeline is mostly deterministic
and testable — only Step 1 has non-deterministic output.

## Step 2: Framework Matching

```python
# src/cmr/step2_matching.py

def match_frameworks(decomposition: DecomposedFinding,
                     frameworks: Dict[str, 'Tier1Framework'],
                     reasoning_goal: ReasoningGoal,
                     min_match_quality: float = 0.3
                     ) -> List[FrameworkMatch]:
    """
    Match decomposed variables against framework scope declarations.

    Algorithm:
    1. For each framework, compute variable overlap:
       matched = decomposition.all_variables ∩ framework.owned_variables
       match_quality = len(matched) / len(decomposition.all_variables)
    2. Filter by min_match_quality
    3. For each matched framework, find relevant templates:
       templates where any link.from_variable or link.to_variable
       is in the matched variable set
    4. Rank by match_quality
    5. R13: Adjust ranking by reasoning_goal
       - EXPLAIN: boost frameworks with complete causal chains
       - PREDICT: boost frameworks with well-characterized intervention points
       - BOUNDARY: boost frameworks with explicit scope conditions

    Returns: List[FrameworkMatch] sorted by match_quality descending
    """
    pass


def _compute_structural_match(decomposition: DecomposedFinding,
                               template: 'MechanisticTemplate') -> bool:
    """
    R4 (Gentner): Match at structural level, not just surface.

    Check if the decomposed finding's RELATIONAL STRUCTURE matches
    the template's structural_pattern, even if surface entities differ.

    Example: finding about "music complexity → preference" matches
    PP_COMPLEXITY_GOLDILOCKS_002 even though the template was specified
    for visual complexity — because the structural pattern
    (stimulus_dimension → optimization_zone → hedonic_evaluation)
    is shared.
    """
    pass
```

## Step 3: Mechanism Tracing

```python
# src/cmr/step3_tracing.py

def trace_mechanisms(matches: List[FrameworkMatch],
                     templates: Dict[str, 'MechanisticTemplate'],
                     decomposition: DecomposedFinding
                     ) -> List[MechanismTrace]:
    """
    For each matched framework, trace causal mechanism from stimulus
    to outcome using templates.

    Algorithm:
    1. For each FrameworkMatch:
       a. Retrieve relevant templates
       b. Find template(s) whose from_variable matches an environmental
          feature and whose chain reaches an outcome variable
       c. If single template covers the path: use it directly
       d. If path requires multiple templates: compose them
          (check composition rules from bridging_rules doc 06 Part 3)
       e. Check for composition interference (R3)
    2. Build MechanismTrace with all links, maturity tags, warnings
    3. Identify unmatched variables (R5: alignable differences)

    Returns: List[MechanismTrace] — may be multiple per framework
    """
    pass


def compose_templates(template_a: 'MechanisticTemplate',
                      template_b: 'MechanisticTemplate',
                      bridging_rules: Dict
                      ) -> Tuple[List['CausalLink'], List[str]]:
    """
    Compose two templates into a single causal chain.

    Composition rules (R3):
    1. Find shared variable: template_a.links[-1].to_variable
       must equal template_b.links[0].from_variable
       (or be in the bridging rules as a legitimate bridge)
    2. Check independence matrix for the two frameworks
    3. Check for known interference patterns
    4. If interaction type unknown: add composition warning

    Returns: (composed_links, warnings)
    """
    pass


def _check_composition_interference(
    template_a_id: str, template_b_id: str,
    shared_variable: str,
    templates: Dict[str, 'MechanisticTemplate']
) -> List[str]:
    """
    R3 (Darden): Check if composing these templates has known
    interference effects.

    Checks:
    - template_a.interactions for entries mentioning template_b_id
    - template_b.interactions for entries mentioning template_a_id
    - Known interaction types: additive, multiplicative, ceiling,
      compensatory, antagonistic

    Returns: list of warning strings (empty = safe to compose)
    """
    pass
```

## Step 4: Prediction Generation

```python
# src/cmr/step4_prediction.py

def generate_predictions(traces: List[MechanismTrace],
                         reasoning_goal: ReasoningGoal
                         ) -> List[GeneratedPrediction]:
    """
    Apply prediction generation grammar to each trace.

    For each trace, apply all applicable operations (see
    Operation Applicability Matrix in doc 06 Part 2).

    Returns: List[GeneratedPrediction]
    """
    all_predictions = []
    for trace in traces:
        all_predictions.extend(_apply_operations(trace, reasoning_goal))
    return all_predictions


def _apply_operations(trace: MechanismTrace,
                      goal: ReasoningGoal
                      ) -> List[GeneratedPrediction]:
    """Apply each applicable operation to the trace."""
    predictions = []
    for op in PredictionOperation:
        if _is_applicable(op, trace, goal):
            new_preds = OPERATION_REGISTRY[op](trace)
            predictions.extend(new_preds)
    return predictions
```

```python
# src/cmr/operations.py

"""
The 10 prediction generation operations.
Each takes a MechanismTrace and returns List[GeneratedPrediction].
"""

def op_substitute_cause(trace: MechanismTrace) -> List[GeneratedPrediction]:
    """
    Operation 1: If X → Y because of property P of X,
    then any stimulus with property P should → Y.

    Implementation:
    1. Get first link's from_variable
    2. Get template's transferable_to list
    3. For each transferable domain, generate prediction
    """
    predictions = []
    first_link = trace.links[0]
    for template_id in trace.template_ids:
        template = _get_template(template_id)
        for domain in template.transferable_to:
            pred = GeneratedPrediction(
                prediction_id=_generate_id(),
                statement=f"{domain} should produce {trace.links[-1].to_variable} "
                          f"via same mechanism as {first_link.from_variable}",
                operation=PredictionOperation.SUBSTITUTE_CAUSE,
                source_trace_ids=[trace.trace_id],
                template_ids=[template_id],
                derivation_reasoning=f"Template {template_id} transfers to {domain} "
                                     f"because shared structural pattern: {template.structural_pattern}",
                confidence=_maturity_to_confidence(trace.overall_maturity),
                weakest_maturity=trace.overall_maturity,
                prediction_level=PredictionLevel.TYPE,
                cause_type=CauseType.CONTRIBUTING,
                modularity_concerns=[],
                suggested_design=None,
                suggested_measures=[],
                feasibility=None,
                novelty_assessment=None,
                theoretical_leverage=None,
            )
            predictions.append(pred)
    return predictions


def op_vary_moderator(trace: MechanismTrace) -> List[GeneratedPrediction]:
    """
    Operation 2: For each moderator, predict how variation changes outcome.

    Implementation:
    1. Collect all moderators from all templates in trace
    2. For each moderator, generate prediction about high vs low values
    """
    predictions = []
    for template_id in trace.template_ids:
        template = _get_template(template_id)
        for mod in template.moderators:
            pred = GeneratedPrediction(
                prediction_id=_generate_id(),
                statement=f"Variation in {mod.variable} should modulate "
                          f"{trace.links[-1].to_variable}: "
                          f"{mod.effect_direction} ({mod.mechanism})",
                operation=PredictionOperation.VARY_MODERATOR,
                source_trace_ids=[trace.trace_id],
                template_ids=[template_id],
                derivation_reasoning=f"Moderator {mod.variable} {mod.effect_direction}: {mod.mechanism}",
                confidence=_maturity_to_confidence(trace.overall_maturity) * 0.8,
                weakest_maturity=trace.overall_maturity,
                prediction_level=PredictionLevel.TYPE,
                cause_type=CauseType.CONTRIBUTING,
                modularity_concerns=[],
                suggested_design=None,
                suggested_measures=[],
                feasibility=None,
                novelty_assessment=None,
                theoretical_leverage=None,
            )
            predictions.append(pred)
    return predictions


def op_block_pathway(trace: MechanismTrace) -> List[GeneratedPrediction]:
    """
    Operation 3: For each interior link, predict result of blocking it.
    """
    predictions = []
    for i, link in enumerate(trace.links):
        if i == 0 or i == len(trace.links) - 1:
            continue  # skip endpoints
        pred = GeneratedPrediction(
            prediction_id=_generate_id(),
            statement=f"Blocking {link.to_variable} should eliminate downstream "
                      f"{trace.links[-1].to_variable}, if mechanism goes through "
                      f"{link.activity}",
            operation=PredictionOperation.BLOCK_PATHWAY,
            source_trace_ids=[trace.trace_id],
            template_ids=trace.template_ids,
            derivation_reasoning=f"If the causal chain passes through {link.to_variable}, "
                                 f"interrupting it should break the downstream effect",
            confidence=_maturity_to_confidence(link.maturity),
            weakest_maturity=link.maturity,
            prediction_level=PredictionLevel.TYPE,
            cause_type=CauseType.TOTAL,
            modularity_concerns=_assess_modularity(link),
            suggested_design=None,
            suggested_measures=[],
            feasibility=_assess_block_feasibility(link),
            novelty_assessment=None,
            theoretical_leverage="HIGH — directly tests pathway specificity",
        )
        predictions.append(pred)
    return predictions


# Operations 4-10 follow the same pattern.
# Full implementations in doc 06 Part 2 (prediction grammar).

OPERATION_REGISTRY = {
    PredictionOperation.SUBSTITUTE_CAUSE: op_substitute_cause,
    PredictionOperation.VARY_MODERATOR: op_vary_moderator,
    PredictionOperation.BLOCK_PATHWAY: op_block_pathway,
    PredictionOperation.VARY_TEMPORAL: op_vary_temporal,
    PredictionOperation.VARY_INDIVIDUAL: op_vary_individual,
    PredictionOperation.CROSS_CULTURAL: op_cross_cultural,
    PredictionOperation.COMBINE_MECHANISMS: op_combine_mechanisms,
    PredictionOperation.DOSE_RESPONSE: op_dose_response,
    PredictionOperation.TOTAL_VS_CONTRIBUTING: op_total_vs_contributing,
    PredictionOperation.TYPE_VS_TOKEN: op_type_vs_token,
}
```

## Step 5: Cross-Framework Convergence

```python
# src/cmr/step5_convergence.py

def assess_convergence(predictions: List[GeneratedPrediction],
                       independence_matrix: Dict[str, Dict[str, float]]
                       ) -> List[ConvergenceResult]:
    """
    Group predictions by outcome variable. For each group,
    compute effective independence of supporting frameworks.

    Algorithm:
    1. Group predictions by their terminal outcome variable
    2. For each group with predictions from 2+ frameworks:
       a. Get the framework pairs
       b. Look up independence scores
       c. Compute effective independence = mean pairwise independence
       d. Check for contradictions (predictions going opposite directions)
    3. Score: convergence = n_supporting * effective_independence

    Usage rule (from doc 07 Section 2):
    - independence >= 0.7: approximately additive, strong convergence
    - 0.4-0.7: partial overlap, moderate convergence
    - < 0.4: substantially overlapping, weak convergence
    """
    pass
```

## Step 6: Composition Failure Detection

```python
# src/cmr/step6_failure.py

def detect_composition_failures(traces: List[MechanismTrace],
                                frameworks: Dict[str, 'Tier1Framework']
                                ) -> List[CompositionFailure]:
    """
    R10 (Barrett): Find where frameworks make incompatible claims.

    Algorithm:
    1. For each pair of traces that share a variable:
       a. Check if they assign different values/directions/timescales
       b. Classify the conflict type (definitional, mechanistic, scope, parameter)
    2. For each conflict, attempt to generate a discriminating prediction

    Returns: List[CompositionFailure]
    """
    pass


def generate_discriminating_predictions(
    failures: List[CompositionFailure]
) -> List[GeneratedPrediction]:
    """
    For each composition failure, generate a prediction that would
    distinguish between the conflicting frameworks.

    These are automatically flagged as high-priority in Step 7.
    """
    pass
```

## Step 7: Prioritization

```python
# src/cmr/step7_prioritization.py

def prioritize_predictions(
    predictions: List[GeneratedPrediction],
    convergence: List[ConvergenceResult],
    failures: List[CompositionFailure],
    weights: Optional[Dict[str, float]] = None
) -> List[PrioritizedPrediction]:
    """
    Score and rank predictions.

    Default weights:
    - convergence_score: 0.25
    - novelty_score: 0.20
    - testability_score: 0.20
    - theoretical_leverage_score: 0.20
    - is_discriminating bonus: 0.15

    Returns: List[PrioritizedPrediction] sorted by composite_priority desc
    """
    pass
```

---

# PART 4: COMPLETE WORKED EXAMPLE

## Input Finding

From Ulrich (1984):
> "Post-surgical patients assigned to rooms with views of natural scenery
> had shorter hospital stays (7.96 vs 8.70 days), took fewer analgesic
> doses, and received fewer negative comments from nurses compared to
> patients with views of a brick wall."

## Step 1 Output: DecomposedFinding

```python
DecomposedFinding(
    finding_id="FIND_ulrich_1984_001",
    source_paper_id="ulrich_1984",
    original_text="Post-surgical patients...",
    environmental_features=["nature_view", "window_view_content"],
    perceptual_processes=["visual_processing"],
    neural_systems=[],                    # not measured in original study
    physiological_responses=[],           # not measured
    psychological_states=["pain_reduction", "positive_affect"],
    behavioral_outcomes=["shorter_hospital_stay", "fewer_analgesic_doses",
                         "fewer_negative_nurse_comments"],
    population="post-surgical_patients",
    context_factors=["hospital_setting", "multi-day_exposure"],
    all_variables=["nature_view", "window_view_content", "visual_processing",
                   "pain_reduction", "positive_affect", "shorter_hospital_stay",
                   "fewer_analgesic_doses", "hospital_setting"],
)
```

## Step 2 Output: Framework Matches

| Framework | Match Quality | Matched Variables | Relevant Templates |
|-----------|-------------|-------------------|-------------------|
| PP | 0.6 | nature_view → visual_processing → positive_affect | T1, T2 |
| NM | 0.5 | nature_view → pain_reduction (cortisol pathway) | T5, T7 |
| DT | 0.4 | nature_view → positive_affect (DMN restoration) | T4, T27 |
| IC | 0.3 | pain_reduction → positive_affect (interoceptive) | T12 |
| EC | 0.2 | nature_view → postural (if window requires standing) | T8 |

## Step 3 Output: Mechanism Traces

**Trace A** (PP pathway):
```
nature_view →[T1: 1/f spectral match]→ low_visual_PE
  →[T1 link 2: efficient coding]→ reduced_cortical_metabolic_demand
  →[T29: allostatic budget]→ freed_resources → pain_reduction + positive_affect
Maturity: how-plausibly (bottleneck: link T1.3, PE → metabolic cost)
```

**Trace B** (NM pathway):
```
nature_view →[T5 reverse: low threat]→ reduced_amygdala_activation
  →[T5 link 2 reverse]→ reduced_cortisol
  →[T29: allostatic budget]→ freed_resources → immune_enhancement → faster_recovery
Maturity: how-plausibly (bottleneck: reverse pathway less characterized than forward)
```

**Trace C** (DT pathway):
```
nature_view →[T4 reverse: low attentional demand]→ TPN_disengagement
  →[T27: DMN re-engagement]→ MTL_subsystem → memory_consolidation + restoration
  →[T27 link 4]→ improved_self-regulation → pain_coping
Maturity: how-plausibly (bottleneck: T27 link 4, DMN → self-regulation)
```

**Trace D** (IC pathway):
```
nature_view →[any body-changing trace above]→ body_state_change
  →[T12: interoceptive PE]→ affect_construction
  →[T12 link 3]→ constructed positive affect → fewer_negative_evaluations
Maturity: how-plausibly (bottleneck: T12 link 3, constructionism)
```

## Step 4 Output: Selected Predictions

**P1** (SUBSTITUTE_CAUSE from Trace A):
> "Artificial fractal scenes with 1/f spectral statistics should produce
> comparable recovery benefits to nature views, because the active mechanism
> is spectral match, not naturalness."
- Template: T1, Operation: SUBSTITUTE_CAUSE
- Confidence: 0.55 (how-plausibly)
- Level: TYPE, Cause: CONTRIBUTING

**P2** (BLOCK_PATHWAY from Trace B):
> "If the nature-view recovery effect operates through cortisol reduction,
> then patients already on corticosteroid therapy should show reduced
> benefit, because the HPA pathway is pharmacologically saturated."
- Template: T5, Operation: BLOCK_PATHWAY
- Confidence: 0.70 (how-actually for HPA pathway)
- Level: TYPE, Cause: CONTRIBUTING
- Modularity concern: corticosteroids affect multiple systems

**P3** (VARY_MODERATOR from Trace C):
> "High-anxiety patients should show larger benefit from nature views than
> low-anxiety patients, because they have greater DMN suppression at baseline
> and therefore more restoration headroom."
- Template: T27, Operation: VARY_MODERATOR
- Confidence: 0.50 (how-plausibly)
- Level: TYPE, Cause: CONTRIBUTING

**P4** (CROSS_CULTURAL from Trace A + T15):
> "Patients from high-density visual ecologies (urban India, Tokyo) may
> show DIFFERENT optimal view content than Western patients, because their
> generative models are calibrated to higher visual complexity."
- Template: T15 + T2, Operation: CROSS_CULTURAL
- Confidence: 0.30 (how-possibly — T15 is most speculative template)
- Level: TYPE, Cause: CONTRIBUTING

**P5** (COMBINE_MECHANISMS from Traces A + B):
> "A hospital room with BOTH nature view AND good acoustic design should
> produce greater recovery benefit than nature view alone, because PP and
> NM pathways are partially independent."
- Templates: T1 + T31, Operation: COMBINE_MECHANISMS
- Independence PP↔NM: 0.5 (partial overlap)
- Combined effect estimate: 50-70% greater than nature view alone

**P6** (VARY_TEMPORAL from Trace B):
> "Morning nature-view exposure should produce larger cortisol reduction
> than evening exposure, because cortisol is higher in the morning."
- Template: T5 + T30, Operation: VARY_TEMPORAL
- Confidence: 0.75 (cortisol diurnal rhythm is how-actually)

## Step 5: Convergence

P1-P3 are supported by 3 frameworks (PP, NM, DT).
Mean pairwise independence: (PP-NM: 0.5) + (PP-DT: 0.5) + (NM-DT: 0.4) / 3 = 0.47
→ Moderate convergence. The three pathways partially overlap (all affect cortisol)
but have genuinely independent components (spectral processing ≠ DMN dynamics).

No contradictions detected.

## Step 6: Composition Failures

**Failure 1**: SCOPE conflict between PP and IC on "positive affect"
- PP says: positive affect arises from PE reduction (fast, automatic)
- IC says: positive affect is constructed from interoceptive signals (requires body state change)
- Discriminating prediction: "Does positive affect occur BEFORE body state changes
  (supporting PP) or ONLY AFTER (supporting IC)? Measure timing: EEG valence markers
  vs autonomic onset."

## Step 7: Prioritization

| Rank | Prediction | Composite Score | Reason |
|------|-----------|----------------|--------|
| 1 | P6 (morning > evening cortisol) | 0.82 | High confidence, high testability, novel |
| 2 | P2 (corticosteroid patients) | 0.78 | High confidence, tests pathway specificity |
| 3 | Discriminator (affect timing) | 0.75 | Discriminating bonus, high theoretical leverage |
| 4 | P5 (nature + acoustics combined) | 0.70 | Practical design implication |
| 5 | P3 (anxiety moderator) | 0.65 | Clinically relevant, moderate confidence |
| 6 | P1 (artificial fractals) | 0.60 | Novel but lower confidence |
| 7 | P4 (cross-cultural view) | 0.45 | Low confidence (how-possibly) but high novelty |

---

# PART 5: MVP IMPLEMENTATION PLAN

## What CC Should Build First

The MVP pipeline needs to work end-to-end for a SINGLE finding before
any optimization. Target: given a finding string, produce a prioritized
prediction list.

### Phase 1 (Week 1): Data structures + Step 2-3

1. Implement all data classes from Part 2 (models.py) — 1 day
2. Implement Step 2 (framework matching) — deterministic variable overlap — 1 day
3. Implement Step 3 (mechanism tracing) for SINGLE-template traces only — 2 days
   - Skip multi-template composition for MVP
   - Each trace uses exactly one template
4. Test: given a manually decomposed finding + the 12 seed templates,
   does the matcher find the right frameworks and the tracer produce valid traces?

### Phase 2 (Week 2): Steps 4-5 + Step 1

5. Implement 3 core operations (SUBSTITUTE_CAUSE, VARY_MODERATOR, BLOCK_PATHWAY) — 2 days
6. Implement Step 5 convergence (simple: mean pairwise independence) — 1 day
7. Implement Step 1 (LLM-based decomposition) with structured prompt — 1 day
8. Test end-to-end: Ulrich finding → predictions. Compare with worked example above.

### Phase 3 (Week 3): Steps 6-7 + remaining operations

9. Implement remaining 7 operations — 2 days
10. Implement Step 6 (composition failure detection) — 1 day
11. Implement Step 7 (prioritization with weighted scoring) — 1 day
12. Implement multi-template composition in Step 3 — 1 day

### Phase 4 (Week 4): Integration + Step 8

13. Wire CMR pipeline output back into web of belief as DERIVED_HYPOTHESIS nodes — 1 day
14. Implement Step 8 template learning stubs (mark for human review) — 1 day
15. Integration tests with 5 different findings from the 1,170-paper corpus — 2 days
16. Documentation and API — 1 day

### Deferred (Post-Sprint 8)

- Structural-level matching (R4) — requires embedding similarity, not just variable overlap
- Nersessian simulation step (R11) — requires runnable template models
- Thought experiments (R12) — requires interactive mode
- Template ID alias resolution — Antigravity is building the alias map now

---

# PART 6: INTEGRATION POINTS

## Where CMR Connects to Existing Code

| CMR Component | Reads From | Writes To |
|---|---|---|
| Step 1 (Decomposition) | `data/extracted_findings/*.jsonl` | Nothing (produces DecomposedFinding) |
| Step 2 (Matching) | `src/data/theory_bootstrap.py` frameworks, `src/theory/` template library | Nothing |
| Step 3 (Tracing) | Template library, bridging rules (doc 06 Part 3) | Nothing |
| Step 4 (Prediction) | Template moderators, scope conditions, parameters | Nothing |
| Step 5 (Convergence) | Independence matrix (doc 07 Section 2) | Nothing |
| Step 6 (Failure) | Framework scope declarations | Nothing |
| Step 7 (Prioritization) | All above | Nothing |
| **Pipeline output** | All steps | `src/services/web_of_belief.py` — creates new Belief nodes with `level=DERIVED_HYPOTHESIS` and Constraint edges linking to source beliefs |
| Step 8 (Learning) | Confirmed/disconfirmed predictions | Template library (update maturity, create composed templates) |

## New Node Type Needed

```python
# Add to EpistemicLevel enum in web_of_belief.py:
DERIVED_HYPOTHESIS = "derived_hypothesis"  # CMR-generated prediction
```

## New Edge Type Needed

```python
# Add to edge_types.py:
MECHANISTIC_DERIVATION = "mechanistic_derivation"
# Links a DERIVED_HYPOTHESIS to the template(s) and finding(s) it was derived from
```

---

# REFERENCES

All references are in the source panel documents. Key architectural sources:
- Bechtel & Richardson (1993/2010) — decomposition strategy (Step 1)
- Darden & Craver (2002) — forward chaining mechanism tracing (Step 3)
- Woodward (2003) — interventionist prediction generation (Step 4)
- Thagard (1989, 1992) — coherence-based convergence (Step 5)
- Barrett (2017) — composition failure as theoretical opportunity (Step 6)
- Gentner & Markman (1997) — structural matching and alignable differences (Steps 2, 4)
