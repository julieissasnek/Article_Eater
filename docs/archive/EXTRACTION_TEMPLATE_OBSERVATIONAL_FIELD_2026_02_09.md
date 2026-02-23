# OBSERVATIONAL FIELD STUDY EXTRACTION TEMPLATE v1.0

**Version**: 1.0.0
**Date**: February 9, 2026
**Status**: Complete (with panel additions)
**Panel Review**: Pearl, Cartwright, Simon, Bates, Kaplan, Walton, Lipton, Hearst, Teufel

---

## PURPOSE

Observational field studies provide **naturalistic evidence** without experimental manipulation. They uniquely contribute:
- High ecological validity (real-world behavior in situ)
- Discovery of natural variation and patterns
- Context-rich data about behavior-environment relationships
- Baseline data for future experimental work

**Causal Limitation**: No manipulation → association level only (Pearl Rung 1)

---

## WHAT THIS TEMPLATE CAN ANSWER

| Category | Coverage | Notes |
|----------|----------|-------|
| Associations | YES | Correlations, co-occurrence patterns |
| Natural Variation | YES | Range of behaviors observed |
| Context Factors | YES | Environmental features present |
| Ecological Validity | HIGHEST | Real-world, uncontrolled settings |
| Causal Direction | NO | Observational only |
| Effect Sizes | LIMITED | Correlations, not experimental effects |

## WHAT THIS TEMPLATE CANNOT ANSWER

- Causal effects (no manipulation)
- Counterfactual claims (what would happen if...)
- Controlled comparisons (no experimental conditions)

---

## HUMAN-READABLE OUTPUT STRUCTURE

### 1. INTRODUCTION SECTION

```
## Introduction

**Research Question**: [What patterns/associations does this study explore?]

**Why Observational**:
- Natural setting required
- Manipulation not ethical/feasible
- Discovery/exploratory phase
- Ecological validity priority

**Theoretical Framework**:
| Theory | Prediction | Observation Target |
|--------|------------|-------------------|
| [Theory] | [What to look for] | [Where/how observed] |
```

### 2. METHODS SECTION

```
## Methods

### Observation Design

| Element | Specification |
|---------|---------------|
| Observation type | Naturalistic / Participant / Structured |
| Recording method | In-situ / Video / Audio / Notes |
| Sampling strategy | Time / Event / Focal / Scan |
| Blinding | Observers blind to hypotheses? |

### Setting

| Element | Specification |
|---------|---------------|
| Location | [Specific sites] |
| Setting type | [Urban park / Hospital / Office / etc.] |
| N sites | |
| Selection criteria | [How sites chosen] |
| Time of observation | [Season, day, time] |
| Duration | [Total observation hours] |

### Participants (if applicable)

| Element | Value |
|---------|-------|
| N observed | |
| Recruitment | Convenience / Random / Purposive |
| Consent | Informed / Waived (public space) / N/A |
| Demographics | [If collected] |

### Observation Protocol

**Behaviors Coded**:
| Behavior | Operational Definition | Coding Scheme |
|----------|----------------------|---------------|
| | | Frequency / Duration / Presence-absence |

**Environmental Features Coded**:
| Feature | Measurement | Reliability |
|---------|-------------|-------------|
| | | Inter-rater κ = |

### Inter-Rater Reliability

| Measure | Value |
|---------|-------|
| N raters | |
| Training | [Hours/method] |
| Cohen's κ / ICC | |
```

### 3. RESULTS SECTION

```
## Results

### Descriptive Statistics

| Variable | M | SD | Range |
|----------|---|----| ------|
| [Behavior 1] | | | |
| [Environment feature 1] | | | |

### Associations Found

| Association | r | p | 95% CI | Interpretation |
|-------------|---|---|--------|----------------|
| [Env feature] ↔ [Behavior] | | | | |

### Patterns Observed

**Pattern 1**: [Description]
- Context: [When/where observed]
- Frequency: [How often]
- Confidence: [Based on observation quality]

### Environmental Context

| Feature Present | % of Observations | Associated With |
|-----------------|-------------------|-----------------|
| [Feature] | | [Behavior] |
```

### 4. DISCUSSION SECTION

```
## Discussion

### Associations Summary

| Association | Direction | Strength | Causal Interpretation |
|-------------|-----------|----------|----------------------|
| | +/−/null | Weak/Mod/Strong | ASSOCIATION ONLY |

### Ecological Validity Assessment

| Dimension | Rating | Justification |
|-----------|--------|---------------|
| Naturalness of setting | High/Mod/Low | |
| Naturalness of behavior | High/Mod/Low | |
| Observer reactivity | Low/Mod/High | |

### Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| No experimental control | Cannot infer causation | Frame as association |
| Observer bias | May affect coding | Inter-rater reliability |
| Selection effects | Sites may not be representative | Describe selection |
| Temporal confounds | Season/time effects | Document timing |

### What This Study CANNOT Conclude

1. ❌ [Env feature] causes [behavior] — no manipulation
2. ❌ Effect would generalize to other settings — only studied [X]
3. ❌ Mechanism linking [env] to [behavior] — not tested

### Hypotheses for Future Experimental Work

| Observation | Suggested Experiment | Priority |
|-------------|---------------------|----------|
| [Pattern observed] | [RCT to test causation] | High/Med/Low |
```

---

## RULE CONVERSION

Observational field studies produce **association rules** (never causal edges) and **constraint rules** (scope from setting).

### Causal Level

**ALWAYS**: `association` (Pearl Rung 1)

No observational study can produce intervention or counterfactual level evidence without experimental manipulation.

### Argument Scheme

**Primary**: `argument_from_sign`
- Observed behavior is a SIGN of underlying relationship
- Cannot establish causation

**Critical Questions**:
1. Is the association reliable (inter-rater reliability)?
2. Are there alternative explanations (confounds)?
3. Could the relationship be spurious?
4. Is the observation sample representative?

### Rule Template

```yaml
rules:
  - rule_id: "[author]_obs_[year]_[finding]"
    rule_type: "association"  # NOT edge

    lhs:
      - var: "[ENV_FEATURE]"
        state: "[observed_state]"
    rhs:
      - var: "[BEHAVIOR]"
        state: "[observed_state]"
    polarity: "positive|negative|null"

    strength:
      kind: "correlation"
      type: "r"
      value: [correlation coefficient]
      ci95: [lower, upper]

    # PANEL ADDITIONS (v2)
    causal_level: "association"  # ALWAYS for observational
    argument_scheme: "argument_from_sign"
    critical_questions:
      - "Is the observation reliable?"
      - "Are there confounding factors?"
      - "Is the sample representative?"
    contrast_class: "[observed vs not observed]"
    difference_maker: null  # Cannot identify without manipulation

    extraction_difficulty: "easy|moderate|hard"
    source_zone: "results"

    applicability:
      population:
        stated: ["[observed population]"]
        implied: []
      setting:
        ecological_validity: "FIELD_NATURAL"
        specific: ["[observed sites]"]
      scope_specified: true

    # Causal limitation flag
    causal_limitation:
      level: "association_only"
      upgrade_requires: "experimental_manipulation"
      hypothesis_for_experiment: "[suggested RCT]"

    ae_confidence: [0.40-0.65]  # Lower than experimental
```

### Confidence Scoring

| Factor | Impact | Rationale |
|--------|--------|-----------|
| **Base** | 0.50 | Observational limitation |
| **Reliability** | | |
| κ > 0.80 | +0.10 | Excellent reliability |
| κ = 0.60-0.80 | +0.05 | Good reliability |
| κ < 0.60 | -0.10 | Questionable reliability |
| **Sample size** | | |
| N > 100 observations | +0.05 | |
| N < 30 observations | -0.10 | |
| **Multiple sites** | | |
| ≥ 3 sites | +0.05 | Generalizability |
| 1 site | -0.05 | Limited |
| **Observer effects** | | |
| Unobtrusive | +0.05 | Natural behavior |
| Participant observation | -0.05 | Potential reactivity |

**Range**: 0.35 (weak observational) to 0.65 (excellent observational)

---

## MACHINE-READABLE DATA

```yaml
# ============================================
# HEADER
# ============================================
paper_id: ""
doi: ""
extraction_date: "YYYY-MM-DD"
article_type: "observational_field"
source_depth: "full_text|abstract|metadata"

# ============================================
# STUDY DESIGN
# ============================================
design:
  type: "observational_field"
  observation_type: "naturalistic|participant|structured"
  recording_method: "in_situ|video|audio|notes"
  sampling_strategy: "time|event|focal|scan"
  observers_blinded: true|false

# ============================================
# SETTING
# ============================================
setting:
  location: ""
  setting_type: ""
  n_sites:
  site_selection: ""
  observation_period:
    start_date: ""
    end_date: ""
    total_hours:
  time_of_day: ""
  season: ""

# ============================================
# PARTICIPANTS
# ============================================
participants:
  n_observed:
  recruitment: "convenience|random|purposive|not_applicable"
  consent: "informed|waived|not_applicable"
  demographics:
    age_range: ""
    gender_distribution: ""
    other: ""

# ============================================
# OBSERVATIONS
# ============================================
observations:
  behaviors_coded:
    - name: ""
      definition: ""
      coding_scheme: "frequency|duration|presence"

  environmental_features:
    - name: ""
      measurement: ""
      reliability_kappa:

  inter_rater:
    n_raters:
    training_hours:
    agreement_metric: "kappa|icc|percent"
    agreement_value:

# ============================================
# RESULTS
# ============================================
results:
  descriptive:
    - variable: ""
      mean:
      sd:
      range: [min, max]

  associations:
    - var1: ""
      var2: ""
      r:
      p:
      ci95: [lower, upper]
      interpretation: ""

  patterns:
    - description: ""
      context: ""
      frequency: ""
      confidence: "high|moderate|low"

# ============================================
# ECOLOGICAL VALIDITY
# ============================================
ecological_validity:
  level: "FIELD_NATURAL"
  naturalness_setting: "high|moderate|low"
  naturalness_behavior: "high|moderate|low"
  observer_reactivity: "low|moderate|high"

# ============================================
# LIMITATIONS
# ============================================
limitations:
  causal_limitation: "association_only"
  other:
    - type: ""
      impact: ""
      mitigation: ""

# ============================================
# HYPOTHESES FOR EXPERIMENTS
# ============================================
future_experiments:
  - observation: ""
    suggested_experiment: ""
    priority: "high|medium|low"

# ============================================
# RULES GENERATED
# ============================================
rules:
  - rule_id: ""
    rule_type: "association"  # NEVER "edge" for observational

    lhs:
      - var: ""
        state: ""
    rhs:
      - var: ""
        state: ""
    polarity: "positive|negative|null"

    strength:
      kind: "correlation"
      type: "r"
      value:
      ci95: []

    # v2 panel additions
    causal_level: "association"
    argument_scheme: "argument_from_sign"
    critical_questions: []
    contrast_class: ""
    extraction_difficulty: ""
    source_zone: ""

    applicability:
      population: []
      setting: ["FIELD_NATURAL"]
      scope_specified: true

    causal_limitation:
      level: "association_only"
      upgrade_requires: "experimental_manipulation"

    ae_confidence:

# ============================================
# QUALITY
# ============================================
overall_quality:
  observation_quality: "high|moderate|low"
  reliability: "high|moderate|low"
  our_confidence:
```

---

## DOMAIN FEATURES (CNfA)

For environmental psychology observational studies:

```yaml
domain_features:
  # Observed nature elements
  nature_elements:
    - element: "vegetation|water|wildlife|etc."
      presence: true|false
      quantification: "[%coverage, count, etc.]"

  # Behavior categories (from environment behavior literature)
  behaviors_observed:
    - category: "restorative|social|physical_activity|wayfinding|dwelling"
      specific_behaviors: []

  # Appleton prospect-refuge in setting
  prospect_refuge:
    prospect_available: true|false
    refuge_available: true|false
    observations_aligned: "[did behavior vary with P-R?]"

  # Design implications
  design_relevance:
    patterns_for_design: []
    needs_experimental_confirmation: true
```

---

## VALIDATION CHECKLIST

Before finalizing extraction:

- [ ] **Causal level set to "association"** — No exceptions for observational
- [ ] **Rule type is "association" not "edge"** — Critical distinction
- [ ] **Inter-rater reliability documented** — κ or ICC reported
- [ ] **Multiple sites if possible** — Generalizability
- [ ] **Limitations explicitly stated** — Cannot infer causation
- [ ] **Hypotheses for experiments generated** — Value of observational work

---

**END OF OBSERVATIONAL FIELD STUDY TEMPLATE**
