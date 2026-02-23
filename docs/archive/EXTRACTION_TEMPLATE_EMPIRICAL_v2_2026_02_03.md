# EMPIRICAL ARTICLE EXTRACTION TEMPLATE v2.0

**Version**: 2.0.0
**Date**: February 3, 2026
**Status**: Complete - Validated against all BN system requirements

---

## PURPOSE

This template captures all information needed to:
1. Populate `ae.claim.v1` and `ae.rule.v1` schemas
2. Feed the Web of Belief system (`web_of_belief.py`)
3. Support bridge warrant detection (`bridge_warrants.py`)
4. Enable conflict resolution (`web_persistence.py`)
5. Classify ecological validity (`validation.py`)
6. Map to environment and outcome taxonomies

---

## HUMAN-READABLE OUTPUT STRUCTURE

When constructing the human-readable extraction document, follow **conventional article structure**:

### 1. INTRODUCTION SECTION

**Structure**: Research Question + Why This Inquiry

```
## Introduction

**Research Question**: [Primary question - what is being asked?]

**Why This Inquiry**:
- Gap addressed: [What gap in knowledge?]
- Timeliness: [Why now?]
- Stakes: [What's at stake if we don't know?]

**Theoretical Context**:
[What was known before this study? Table of prior findings and their implications]
```

### 2. METHODS SECTION

**Structure**: Hypotheses → Experimental Structure → Timeline → Stimuli

```
## Methods

### Hypotheses

| H# | Prediction | Direction | Theoretical Basis |
|----|------------|-----------|-------------------|
| H1 | [Prediction] | +/−/null | [Why expected] |

**Why These Measures**: [Rationale for DV, IV operationalization]

### Experimental Design

| Experiment | Design | N | Conditions | Duration |
|------------|--------|---|------------|----------|
| Exp 1 | [Design] | [N] | [Conditions] | [Time] |

### Participants

| Element | Specification |
|---------|---------------|
| Total N | |
| Sample | |
| Age M (SD) | |
| Gender | |

### Procedure Timeline

[Visual timeline or step-by-step sequence with exact timings]

```
0 min     5 min     10 min    15 min    20 min
|---------|---------|---------|---------|
 Consent   Baseline  Exposure  Post-test Debrief
```

### Stimulus Materials

[INCLUDE IMAGES if available]
[If no images: detailed description sufficient to reconstruct stimuli]

- Physical description: [Size, color, material, etc.]
- Selection criteria: [How stimuli were chosen]
- Number per condition: [N stimuli]
- Presentation parameters: [Duration, distance, etc.]
```

### 3. RESULTS SECTION

**Structure**: Statistics → Effect Sizes → Interpretation → Concerns

```
## Results

### Experiment 1

| Measure | Cond 1 M (SD) | Cond 2 M (SD) | t/F | df | p | d [95% CI] |
|---------|---------------|---------------|-----|----|---|------------|
| [DV] | | | | | | |

**Interpretation**: [Plain-language meaning]

**Concern**: [Any methodological issues] — Severity: Low/Mod/High

**Mitigation**: [Evidence countering concern]

### Effect Sizes Summary

| Comparison | d | Magnitude |
|------------|---|-----------|
| | | Small/Med/Large |
```

### 4. DISCUSSION SECTION

**Structure**: Authors' Claims → Connections → Limitations → Our Assessment

```
## Discussion

### Authors' Key Claims

| Claim | Quote | Page |
|-------|-------|------|
| 1 | "[Exact quote]" | p. X |

### Proposed Mechanism

[What mechanism do authors invoke? Evidence cited?]

### Connections to Prior Work

| Prior Study | Agreement/Disagreement | Explanation |
|-------------|------------------------|-------------|
| | Agrees/Disagrees | |

### Authors' Acknowledged Limitations

| Limitation | Authors' Words |
|------------|---------------|
| | |

### Unacknowledged Limitations

| Limitation | Impact | Severity |
|------------|--------|----------|
| | | Low/Mod/High |

### Inferential Boundaries

What CANNOT be concluded from this study:

1. ❌ [Over-interpretation 1]
2. ❌ [Over-interpretation 2]
3. ❌ [Over-interpretation 3]
4. ❌ [Over-interpretation 4]
5. ❌ [Over-interpretation 5]

### Integration Statement

[How this connects to broader knowledge, what it uniquely contributes]
```

---

## STIMULUS DOCUMENTATION GUIDANCE

**If images of stimuli are available**:
- Include figure/screenshot directly
- Caption with: stimulus type, dimensions, source

**If images are NOT available, construct description**:

| Element | Include |
|---------|---------|
| Physical form | Shape, size, color, texture |
| Spatial arrangement | Layout, distances, angles |
| Temporal parameters | Duration, sequence, timing |
| Sensory modalities | Visual, auditory, haptic |
| Variation | Range of stimuli, counterbalancing |
| Control comparison | What control condition looked like |

**Example stimulus description** (when no image):

> *Nature condition*: 20 photographs of urban parks (mean size 8×10 inches, displayed on 24" monitor at 60cm viewing distance). Images selected from prescaling study (N=30) for high nature ratings (M=6.2/7, SD=0.4). Each displayed for 30 seconds with 5-second ISI. All images contained visible vegetation (>50% green), sky, and no people.
>
> *Control condition*: 20 photographs of built environments matched for luminance and color temperature. No vegetation visible. Same display parameters.

---

## RULE CONVERSION: FROM EXTRACTION TO QUINEAN WEB

This section shows how extracted empirical data becomes rules that enter the **Quinean Web of Belief**. Unlike standard BNs, our system requires:

1. **Argument Structure** — What warrants the claim?
2. **Interrogative Structure** — What questions does this answer?
3. **Coherence Requirements** — How does this fit the web?
4. **Scope & Enabling Conditions** — When does this apply?
5. **Bridge Warrant Signals** — Does this transfer across domains?

### REQUIRED ELEMENTS FOR RULE INCORPORATION

Before an empirical finding can become a rule in the web, verify these elements are present:

#### 1. Argument Structure (What Warrants This Claim?)

| Element | Required? | Source in Template | If Missing |
|---------|-----------|-------------------|------------|
| **Claim statement** | ✅ Required | RESULTS > findings | Cannot create rule |
| **Evidence type** | ✅ Required | METHODS > design | Rule confidence affected |
| **Causal warrant** | ✅ Required | CAUSAL STRUCTURE section | Determines edge vs. association |
| **Sample warrant** | ✅ Required | METHODS > Participants | Scope conditions affected |
| **Measurement warrant** | ✅ Required | METHODS > Measures | AccessLevel determined |
| **Statistical warrant** | ✅ Required | RESULTS > statistics | Strength determined |

**Argument Structure Template**:
```yaml
argument:
  claim: "[What is being claimed]"
  warrant_type: "experimental|quasi_experimental|correlational|observational"
  premises:
    - "[Premise 1: theoretical basis]"
    - "[Premise 2: methodological assumption]"
  backing:
    - "[Evidence supporting premises]"
  qualifier: "[Conditions under which claim holds]"
  rebuttal: "[What would defeat this claim]"
```

#### 2. Interrogative Structure (What Questions Does This Answer?)

Each rule must answer specific questions from the 96-question specification:

| Question Category | Questions Answered | How to Verify |
|-------------------|-------------------|---------------|
| **ID questions** | ID.1-ID.3 | Header complete? |
| **Research questions** | RQ.1-RQ.3 | Research Question section filled? |
| **Methods questions** | M.1-M.15 | Methods section complete? |
| **Statistics questions** | S.1-S.8 | Results section has effect sizes, CIs? |
| **Causal questions** | C.1-C.5 | Causal Structure section complete? |
| **Scope questions** | SC.1-SC.5 | Scope Conditions populated? |
| **Enabling questions** | EN.1-EN.6 | Enabling Conditions populated? |
| **Bridge questions** | BW.1-BW.4 | Domain & Bridge Signals checked? |

**Interrogative Checklist Before Rule Creation**:
```yaml
interrogative_completeness:
  # Must answer these to create ANY rule
  what_is_claimed: true|false
  what_evidence_type: true|false
  what_population: true|false
  what_setting: true|false
  what_measurement: true|false

  # Must answer these for EDGE rules
  what_causal_direction: true|false
  what_mechanism_proposed: true|false

  # Must answer these for CPD_HINT rules
  what_effect_size: true|false
  what_confidence_interval: true|false

  # Must answer these for INTERACTION rules
  what_moderator: true|false
  what_conditions_differ: true|false
```

#### 3. Coherence Requirements (Quinean Web Integration)

**Unlike standard BNs**, rules don't enter in isolation. Each must specify:

| Coherence Element | Description | Template Source |
|-------------------|-------------|-----------------|
| **Theory alignment** | Which theories does this support/challenge? | Theoretical Context |
| **Prior belief status** | Does this confirm, contradict, or extend? | Conflict Assessment |
| **Tension signals** | What existing beliefs does this tension with? | Conflict Assessment |
| **Revision candidates** | If conflicts, what might be revised? | Our Assessment |

```yaml
coherence:
  supports_theories: ["ART", "SRT"]
  contradicts_theories: []
  prior_beliefs_confirmed: ["ENV_NATURE → OUT_STRESS (negative)"]
  prior_beliefs_tensioned: []
  if_conflict:
    revision_candidates:
      - "scope_condition_update"
      - "moderator_discovery"
      - "measurement_artifact"
    revision_priority: "scope_first"  # Cartwright: try scope before theory
```

#### 4. Scope & Enabling Conditions (When Does This Apply?)

**Required for ALL rules** (Cartwright mandate):

```yaml
applicability:
  # SCOPE CONDITIONS (from inclusion criteria)
  scope:
    population:
      stated: ["healthy adults"]
      implied: ["Western", "educated"]
      excluded: ["clinical populations"]
    setting:
      ecological_validity: "FIELD_NATURAL|LAB_VR|etc."
      specific: ["urban parks", "temperate climate"]
    temporal:
      duration: "acute|chronic"
      measurement_timing: "immediate|delayed"
    scope_specified: true|false  # Critical flag

  # ENABLING CONDITIONS (from methods)
  enabling:
    baseline_state: "elevated stress required"
    minimum_exposure: "20 minutes"
    concurrent_factors: ["no phone use", "alone"]
    blocking_factors: ["rain", "crowds"]
    threshold: "vegetation coverage > 50%"
    dosage: "single exposure"
```

#### 5. Bridge Warrant Signals (Cross-Domain Transfer)

If the study implies findings transfer across domains:

```yaml
bridge:
  cross_domain: true|false
  if_true:
    source_domain: "lab_vr"
    target_domain: "field_natural"
    bridge_type: "MECHANISM|FUNCTIONAL|ANALOGICAL|CONSTITUTIVE|CAPACITY"
    mechanism_specified: true|false
    assumed_mechanism: "[What mechanism licenses transfer]"
    transfer_confidence: 0.35-0.85  # By type
```

---

### RULE TYPE DECISION TREE

```
                    ┌─────────────────────────────┐
                    │   What type of finding?     │
                    └──────────────┬──────────────┘
                                   │
            ┌──────────────────────┼──────────────────────┐
            │                      │                      │
            ▼                      ▼                      ▼
    ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
    │ Causal claim  │      │ Effect size   │      │ Moderator     │
    │ (direction)   │      │ (magnitude)   │      │ (interaction) │
    └───────┬───────┘      └───────┬───────┘      └───────┬───────┘
            │                      │                      │
            ▼                      ▼                      ▼
    ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
    │  EDGE rule    │      │ CPD_HINT rule │      │ INTERACTION   │
    │               │      │               │      │ rule          │
    └───────────────┘      └───────────────┘      └───────────────┘
            │
            │ Is it a null finding?
            ▼
    ┌───────────────┐
    │ EDGE rule     │
    │ polarity:null │
    └───────────────┘
```

---

### COMPLETE CONVERSION EXAMPLES

**Example 1: Empirical Finding → Edge Rule (Full)**

*Extracted data* (from template sections):
```yaml
# From RESEARCH QUESTION
research_question: "Does urban park exposure reduce stress?"
why_this_inquiry: "Prior lab studies show effect; field validation needed"

# From HYPOTHESES
hypothesis: "H1: 20-min park walk reduces cortisol vs. urban walk"
rationale: "ART predicts attention restoration reduces stress"

# From METHODS
design: "RCT, between-subjects"
n_total: 120
population: "healthy adults, ages 25-45, urban residents"
ecological_validity: "FIELD_NATURAL"
measures:
  - name: "salivary cortisol"
    method: "physiological"
    access_level: "AUTONOMIC"

# From RESULTS
effect_size:
  type: "d"
  value: -0.52
  ci95: [-0.78, -0.26]
  p: 0.001

# From CAUSAL STRUCTURE
causal_direction: "FORWARD"
causal_warrant: "RCT with random assignment"
mechanism_tested: false
mechanism_proposed: "attention_restoration"

# From SCOPE CONDITIONS
scope_specified: true
population_scope: "healthy adults, Western"
setting_scope: "urban parks, temperate"

# From ENABLING CONDITIONS
minimum_exposure: "20 minutes"
baseline_state: "not specified"

# From CONFLICT ASSESSMENT
conflicts_with: []
conflict_type: null
```

*Converted to rule*:
```yaml
rules:
  - rule_id: "smith_2024_h1"
    rule_type: "edge"

    # Core relationship
    lhs:
      - var: "ENV_URBAN_PARK"
        state: "walk_20min"
        canonical_id: "ENV_URBAN_PARK"
    rhs:
      - var: "OUT_CORTISOL"
        state: "decreased"
        canonical_id: "OUT_CORTISOL_SALIVARY"
    polarity: "negative"

    # Strength with full statistical warrant
    strength:
      kind: "effect_size"
      type: "d"
      value: -0.52
      ci95: [-0.78, -0.26]
      p_value: 0.001
      n_total: 120

    # Causal warrant (what licenses directionality)
    causal:
      direction: "FORWARD"
      warrant: "RCT"
      mechanism_proposed: "attention_restoration"
      mechanism_tested: false

    # Scope conditions (Cartwright)
    applicability:
      population: ["healthy_adults", "ages_25_45", "urban_residents"]
      population_excluded: ["clinical", "children", "elderly"]
      setting: ["field_natural", "urban_park", "temperate_climate"]
      setting_excluded: ["lab", "tropical", "wilderness"]
      temporal: "acute_single_exposure"
      scope_specified: true

    # Enabling conditions
    enabling:
      minimum_exposure: "20_minutes"
      baseline_state: "unspecified"
      concurrent_factors: []
      blocking_factors: []

    # Ecological validity (Kaplan)
    ecological_validity: "FIELD_NATURAL"

    # Measurement classification
    measurement:
      method: "physiological"
      access_level: "AUTONOMIC"
      instrument: "salivary_cortisol_assay"

    # Coherence with web
    coherence:
      supports_theories: ["ART", "SRT"]
      prior_alignment: "confirms"
      tensions: []

    # Bridge signals
    bridge:
      cross_domain: false

    # Interrogative completeness
    questions_answered:
      - "RQ.1"  # Primary question
      - "M.1"   # Design type
      - "M.4"   # Sample
      - "M.8"   # Ecological validity
      - "S.1"   # Effect size
      - "S.2"   # Confidence interval
      - "C.1"   # Causal direction
      - "SC.1"  # Population scope
      - "SC.2"  # Setting scope

    # Article Eater confidence
    ae_confidence: 0.78
    ae_confidence_factors:
      base: 0.65
      rct_bonus: +0.10
      field_validity_bonus: +0.05
      adequate_n_bonus: +0.03
      no_replication_penalty: -0.05
```

**Example 2: Null Finding → Edge Rule with Null Polarity**

*Key difference*: Must capture whether null is meaningful (adequate power) or uninformative.

```yaml
rules:
  - rule_id: "brown_2023_h2"
    rule_type: "edge"

    lhs:
      - var: "ENV_OFFICE_PLANT"
        state: "present"
    rhs:
      - var: "OUT_COGNITIVE_PERFORMANCE"
        state: "changed"
    polarity: "null"  # Critical: null finding

    strength:
      kind: "effect_size"
      type: "d"
      value: 0.08
      ci95: [-0.15, 0.31]
      p_value: 0.42
      n_total: 85

      # NULL-SPECIFIC FIELDS
      null_result: true
      null_meaningful: true  # Power > 0.80 for d = 0.30
      power_analysis:
        target_effect: 0.30
        achieved_power: 0.82
      equivalence_tested: false

    # For VOI search: this is an answered question
    voi_signal:
      question_answered: "Does office plant affect cognition?"
      answer: "No detectable effect (powered for d > 0.30)"
      remaining_uncertainty: "Small effects not ruled out"

    ae_confidence: 0.60  # Lower for null
```

**Example 3: Moderator Finding → Interaction Rule**

```yaml
rules:
  - rule_id: "lee_2024_mod1"
    rule_type: "interaction"

    # Three-way specification: IV × Moderator → DV
    lhs:
      - var: "ENV_NATURE_EXPOSURE"
        state: "present"
      - var: "MOD_BASELINE_STRESS"
        state: "high"
    rhs:
      - var: "OUT_STRESS_REDUCTION"
        state: "large"
    polarity: "positive"  # Interaction is positive

    strength:
      kind: "interaction"
      main_effect:
        value: -0.35
        ci95: [-0.55, -0.15]
      interaction_effect:
        value: -0.42  # Additional effect when moderator = high
        ci95: [-0.68, -0.16]
      conditional_effects:
        - moderator_level: "high_stress"
          effect: -0.77
          ci95: [-1.02, -0.52]
        - moderator_level: "low_stress"
          effect: -0.35
          ci95: [-0.55, -0.15]

    # Scope implications of moderator
    applicability:
      # Moderator REFINES scope
      scope_refinement:
        before: "all adults"
        after: "effect strongest for high-stress individuals"
      conditional_scope:
        high_stress:
          population: ["adults with elevated baseline stress"]
          effect_applies: "strong"
        low_stress:
          population: ["adults with low baseline stress"]
          effect_applies: "weak"

    ae_confidence: 0.72
```

---

### CONFIDENCE SCORING: QUINEAN PRINCIPLES

| Factor | Impact | Rationale |
|--------|--------|-----------|
| **Evidence type** | | |
| RCT/experimental | +0.10 | Causal warrant strongest |
| Quasi-experimental | +0.05 | Partial causal warrant |
| Correlational | -0.05 | No causal warrant |
| **Ecological validity** | | |
| FIELD_NATURAL | +0.10 | Direct generalization |
| LAB_VR | 0 | Bridge warrant needed |
| LAB_PHOTOS | -0.05 | Weak bridge |
| **Sample** | | |
| Large N (>200) | +0.05 | Precision |
| Pre-registered | +0.10 | Reduces bias |
| WEIRD only | -0.05 | Scope limitation |
| Replication | +0.10 | Coherence with web |
| **Coherence** | | |
| Confirms prior beliefs | +0.05 | Web coherence |
| Contradicts prior beliefs | -0.10* | Tension (but may be informative) |
| Novel claim | 0 | Neutral |

*Contradiction penalty can be offset if study quality is higher than prior sources.

**Base confidence**: 0.65 for single empirical study
**Range**: 0.40 (weak) to 0.85 (strong)

---

## TEMPLATE SECTIONS SUMMARY

| # | Section | BN System It Feeds |
|---|---------|-------------------|
| 1 | Header & Metadata | ae.paper.v1, source_depth |
| 2 | Our Summary | Human reference |
| 3 | Research Question | Human reference |
| 4 | Theoretical Context | theory_registry, causal_pathway |
| 5 | Hypotheses | Human reference |
| 6 | Methods | ScopeConditions, EcologicalValidity, MeasurementMethod, AccessLevel, taxonomies |
| 7 | Results | ae.claim.v1.statistics |
| 8 | Temporal Dynamics | EnablingConditions (temporal) |
| 9 | Enabling Conditions | EnablingConditions (full) |
| 10 | Causal Structure | CausalDirection |
| 11 | Domain & Bridge Signals | bridge_warrants |
| 12 | Conclusion Logic | Human reference |
| 13 | Authors' Discussion | Human reference |
| 14 | Our Assessment | Human reference |
| 15 | Conflict Assessment | ConflictType, antonym detection |
| 16 | Context & Meaning | Human reference |
| 17 | Limitations Table | ConflictType mapping |
| 18 | Reproducibility Gaps | Human reference |
| 19 | Q&A Section | Human reference |
| 20 | Machine-Readable Data | All schemas |

---

# THE TEMPLATE

---

## HEADER & METADATA

*Auto-populated from Zotero/BibTeX:*

| Field | Value |
|-------|-------|
| Citation (APA) | |
| DOI | |
| Title | |
| Authors | |
| Year | |
| Journal/Venue | |
| Abstract | [verbatim] |

*Manual classification:*

| Field | Value |
|-------|-------|
| Article type | [ ] Empirical-Experimental [ ] Empirical-Correlational [ ] Meta-Analysis [ ] Systematic Review [ ] Theoretical [ ] Narrative Review [ ] Case Study |
| Source depth | [ ] Full text [ ] Abstract only [ ] Metadata only |

---

## OUR SUMMARY

- Plain-language summary of key findings (1-3 sentences)

---

## RESEARCH QUESTION

**Primary Question**
- What is being asked? (IV → DV relationship)

**Secondary Questions**
- Mediation? Moderation? Dose-response? Boundary conditions?

**Why This Inquiry**

| Element | Response |
|---------|----------|
| What gap does this address? | |
| Why now? | (timeliness, prior conflicts, new methods) |
| What's at stake? | (theoretical stakes, practical consequences) |
| What do we gain by knowing? | |

---

## THEORETICAL CONTEXT (What Was Known)

**Prior Findings**

| Prior Finding | Source | Implication for This Study |
|---------------|--------|---------------------------|
| | | |

**Theory-Outcome Pathways**

| Theory | Relevant Outcome | Prediction Type | Causal Pathway |
|--------|------------------|-----------------|----------------|
| | | core / derived / exploratory | [explicit mechanism chain] |

---

## HYPOTHESES

**Experiment 1:**

| H# | Prediction | Direction | Theoretical Basis |
|----|------------|-----------|-------------------|
| H1 | | +/−/null | Why this is expected |
| H2 | | +/−/null | |

**Why These Measures/Sensors**

| Choice | Rationale |
|--------|-----------|
| Why this DV? | |
| Why this IV manipulation? | |
| Why this measurement timing? | |
| Alternatives considered? | |

---

## METHODS

### Design Overview Table

| Experiment | Design | N | Conditions | Exposure Duration | Random Assignment? |
|------------|--------|---|------------|-------------------|-------------------|
| | | | | | |

### Participants Table

| Element | Specification |
|---------|---------------|
| Total N | |
| Sample source | |
| Age (M, SD) | |
| Gender distribution | |
| Assignment method | |
| Attrition | |
| Power analysis reported? | |

### Scope Conditions *(maps to ScopeConditions)*

| Scope Dimension | Value | Explicitly Specified? |
|-----------------|-------|----------------------|
| Population type | adults / children / clinical / healthy | Yes / No |
| Setting | lab / field / simulated / VR | Yes / No |
| Duration type | acute / chronic / single_exposure | Yes / No |
| Geography | urban / rural / country | Yes / No |

### Ecological Validity Classification *(maps to EcologicalValidity)*

| Study Component | Classification |
|-----------------|----------------|
| Environment presentation | FIELD_NATURAL / FIELD_STRUCTURED / LAB_VR / LAB_VIDEO / LAB_PHOTOS / LAB_ABSTRACT |
| Justification | [why this classification] |

### Measurement Classification *(maps to MeasurementMethod + AccessLevel)*

| Measure | Method | Access Level | Notes |
|---------|--------|--------------|-------|
| [DV1] | self_report / cortisol / HR / EEG / fMRI / behavioral_task / observation | CONSCIOUS / AUTONOMIC / BEHAVIORAL / NEURAL | |
| [DV2] | | | |

### Environment & Outcome Canonical IDs *(maps to environment_taxonomy + outcome_taxonomy)*

| Variable | Role | Raw Term Used | Canonical ID | Synonyms Checked |
|----------|------|---------------|--------------|------------------|
| | IV | | spatial.openness / natural.vegetation / etc. | |
| | DV | | affect.stress / cog.attention / etc. | |

### Stimulus Materials

- Figures showing stimuli (or detailed description)
- Selection criteria (prescaling study?)
- Number and type of stimuli per condition

### Task/Measure Details

| Element | Specification |
|---------|---------------|
| Task name | |
| What participants did | |
| Stimuli per trial | |
| Trial timing | |
| DVs collected | |

### Procedure Timeline

```
0 min     5 min     10 min    15 min    20 min    25 min
|---------|---------|---------|---------|---------|
 [Phase 1] [Phase 2] [Phase 3] [Phase 4] [Phase 5]
```

- Exact sequence with timing for each phase

---

## RESULTS

### Tables per Experiment

| Measure | Condition 1 M (SD) | Condition 2 M (SD) | Test statistic | df | p | d [95% CI] |
|---------|-------------------|-------------------|----------------|----|----|-----------|
| | | | | | | |

### Interpretation Box

> Plain-language meaning: [What this result means in everyday terms]

### Concern Box

> Methodological concern: [e.g., baseline imbalance, demand characteristics]
> Severity: Low / Moderate / High
> Impact on claim: [How this affects confidence]

### Strength/Mitigation Box

> Evidence countering concern: [What mitigates the issue]

### Effect Sizes Summary Table

| Comparison | Reported d | Computed d (if NR) | Magnitude |
|------------|-----------|-------------------|-----------|
| | | | Small / Med / Large |

---

## TEMPORAL DYNAMICS *(maps to EnablingConditions.temporal)*

| Parameter | Value | Evidence Source (page/table) |
|-----------|-------|------------------------------|
| **Onset latency** | How quickly does effect begin? | |
| **Minimum effective duration** | Threshold exposure time | |
| **Peak effect timing** | When is effect strongest? | |
| **Effect persistence** | How long after exposure ends? | |
| **Decay curve** | Linear / Exponential / Step / Unknown | |
| **Dose-response shape** | Linear / Asymptotic / U-shaped / Threshold / Unknown | |
| **Dose-response present?** | Yes / No / Not tested | |
| **Cumulative vs. acute** | Single exposure sufficient or builds over time? | |

*If not reported, mark as "NR" — informative absence*

---

## ENABLING CONDITIONS *(maps to EnablingConditions)*

| Parameter | Value | Evidence Source |
|-----------|-------|-----------------|
| **Baseline state required** | e.g., "fatigued", "stressed", "healthy" | |
| **Concurrent factors required** | What must be present for effect? | |
| **Blocking factors** | What must be absent? | |
| **Threshold (intensity)** | Minimum intensity/magnitude for effect | |
| **Threshold (duration)** | Minimum time required | |
| **Dosage regimen** | Single / daily / repeated / continuous | |
| **Temporal order specified?** | "IV precedes DV by X time" | |

*If not reported, mark as "NR" — this is important: NR ≠ "not required"*

---

## CAUSAL STRUCTURE *(maps to CausalDirection)*

| Element | Evidence | Classification |
|---------|----------|----------------|
| **Causal direction** | What establishes causation? | FORWARD / REVERSE / BIDIRECTIONAL / CORRELATIONAL / MEDIATED / COMMON_CAUSE / UNKNOWN |
| **Temporal precedence** | Does IV measurement precede DV? | Yes / No / Simultaneous |
| **Manipulation** | Was IV experimentally manipulated? | Yes / No (observational) |
| **Mediator tested?** | Was mechanism pathway measured? | Yes → [what mediator] / No |
| **Mediator evidence** | Statistical test for mediation | Sobel / Bootstrap / Baron-Kenny / None |
| **Moderators tested?** | What boundary conditions examined? | [list] |
| **Common causes controlled?** | Confounds addressed? | Yes → [which] / No → [which uncontrolled] |
| **Alternative explanations** | Ruled out? | [List what was/wasn't addressed] |

---

## DOMAIN & BRIDGE SIGNALS *(maps to bridge_warrants.py)*

### Domain Classification

| Element | Value |
|---------|-------|
| **Source domain** | object_perception / basic_neuroscience / environmental_psychology / affect / cognition / architectural_perception |
| **Target domain (if transferring)** | CNFA / architectural_perception / [other] |
| **Domain transfer implied?** | Yes / No |

### Bridge Warrant Detection

| Signal | Present? | Evidence |
|--------|----------|----------|
| **Mechanism conservation claimed?** | Yes / No | [quote if yes] |
| **Specific neural pathway named?** | Yes → [which] / No | |
| **Capacity language used?** | ("has the capacity", "inherent ability", etc.) | Yes / No |
| **Functional equivalence claimed?** | (same outcome, different mechanism) | Yes / No |
| **Constitutive relationship?** | (target contains source) | Yes / No |
| **Analogical reasoning?** | (structural similarity) | Yes / No |

**Suggested Bridge Type**: MECHANISM / FUNCTIONAL / ANALOGICAL / CONSTITUTIVE / CAPACITY / NONE

---

## CONCLUSION LOGIC

**Inferential Chain**

```
Data pattern → Statistical claim → Substantive conclusion
[Raw numbers] → [p < .05, d = X] → [Authors say this means...]
```

**What the Results Actually Show**
- Minimal interpretation (just what the data say)

**What the Authors Conclude**
- Their interpretation (may go beyond data)

**Gap Between Data and Conclusion**
- Where do authors extrapolate?
- What inferential leaps are undefended?

---

## AUTHORS' DISCUSSION

### Key Claims (Quoted)

| Claim # | Direct Quote | Page |
|---------|--------------|------|
| 1 | "[Exact quote]" | p. |
| 2 | "[Exact quote]" | p. |

### Proposed Mechanism

| Element | Value |
|---------|-------|
| Mechanism named | |
| Evidence cited for mechanism | |
| Mechanism tested in this study? | Yes / No |

### Comparison to Prior Work

| Prior Study | Agreement | Authors' Explanation |
|-------------|-----------|---------------------|
| | Agrees / Disagrees | |

### Authors' Acknowledged Limitations

| Limitation | Authors' Words |
|------------|---------------|
| | |

---

## OUR ASSESSMENT

**Strengths**
- [What study does well]
- [Why this matters for validity]

**Unacknowledged Limitations**
- [What authors missed]
- [Impact on conclusions]

---

## CONFLICT ASSESSMENT *(maps to ConflictType)*

| Prior Finding (Citation) | This Study's Position | Conflict Type | Resolution |
|--------------------------|----------------------|---------------|------------|
| | Agrees / Disagrees | GENUINE_CONTRADICTION / SCOPE_BOUNDARY / METHODOLOGICAL_DIVERGENCE / PRECISION_BOUNDARY / N/A | [How conflict is explained] |

### Antonym Detection *(from environment_taxonomy)*

| This Study's IV | Prior Study's IV | Antonym Pair? | Implication |
|-----------------|------------------|---------------|-------------|
| e.g., "openness" | e.g., "enclosure" | Yes / No | Same finding (opposite IV, opposite effect) / True conflict |

---

## CONTEXT & MEANING

### Theoretical Situation

| Question | Where This Study Fits |
|----------|----------------------|
| Does X cause Y? | Provides evidence for / against / neither |
| What mediates X→Y? | Addresses / Does not address |
| What moderates X→Y? | Addresses / Does not address |

### Relation to Competing Theories

| Theory | This Study's Implications |
|--------|--------------------------|
| [Theory A] | Supports / Challenges / Neutral |
| [Theory B] | Supports / Challenges / Neutral |

### Inferential Boundaries

What CANNOT be concluded (minimum 5):

1. ❌
2. ❌
3. ❌
4. ❌
5. ❌

### Practical Implications

| Element | Value |
|---------|-------|
| What practitioners should do | |
| Caveats | |
| What NOT to conclude | |

### Confidence Calibration

| Claim | Author Confidence | Our Assessment | Reason |
|-------|-------------------|----------------|--------|
| | High / Mod / Low | Higher / Same / Lower | |

### Integration Statement

- How this connects to broader knowledge
- Key papers it builds on
- What it uniquely contributes

### Open Questions

- Unanswered questions for future research

---

## LIMITATIONS TABLE

| Limitation | Acknowledged? | Impact | Maps to ConflictType? |
|------------|---------------|--------|----------------------|
| Sample size | Yes / No | Low / Mod / High | |
| WEIRD sample | Yes / No | Low / Mod / High | SCOPE_BOUNDARY |
| Single exposure | Yes / No | Low / Mod / High | |
| Self-report only | Yes / No | Low / Mod / High | METHODOLOGICAL_DIVERGENCE |
| Lab vs. field | Yes / No | Low / Mod / High | SCOPE_BOUNDARY |
| Demand characteristics | Yes / No | Low / Mod / High | |
| No temporal follow-up | Yes / No | Low / Mod / High | |
| No dose-response test | Yes / No | Low / Mod / High | |
| No mediator test | Yes / No | Low / Mod / High | |

---

## REPRODUCIBILITY GAPS

| Element | Status | Impact |
|---------|--------|--------|
| Data available? | Yes / No / Partial | |
| Code available? | Yes / No / Partial | |
| Materials available? | Yes / No / Partial | |
| Stimuli available? | Yes / No / Partial | |
| Preregistered? | Yes / No | |
| Analysis plan specified? | Yes / No | |
| Effect size reported? | Yes / No / Computed | |

---

## Q&A SECTION

Pre-computed answers:

**Q: What was the main finding?**
A:

**Q: How confident should we be?**
A:

**Q: Does this replicate prior work?**
A:

**Q: What population does this apply to?**
A:

**Q: What setting does this apply to?**
A:

**Q: What are the key limitations?**
A:

**Q: How long does the effect last?**
A:

**Q: What's the minimum dose needed?**
A:

**Q: What baseline state is required?**
A:

**Q: Does this support ART, SRT, or other theory?**
A:

---

## MACHINE-READABLE DATA

```yaml
# ============================================
# HEADER (from Zotero)
# ============================================
paper_id: "[from Zotero]"
doi: "[from Zotero]"
extraction_date: "YYYY-MM-DD"
source_depth: "full_text|abstract|metadata"

# ============================================
# SCOPE CONDITIONS (maps to ScopeConditions)
# ============================================
scope:
  population: "adults|children|clinical|healthy"
  setting: "lab|field|simulated|vr"
  duration: "acute|chronic|single_exposure"
  measurement: "self_report|physiological|behavioral"
  geography: ""
  moderators: []
  scope_specified: true|false

# ============================================
# ECOLOGICAL VALIDITY (maps to EcologicalValidity)
# ============================================
ecological_validity: "FIELD_NATURAL|FIELD_STRUCTURED|LAB_VR|LAB_VIDEO|LAB_PHOTOS|LAB_ABSTRACT"

# ============================================
# MEASUREMENT (maps to MeasurementMethod + AccessLevel)
# ============================================
measures:
  - measure_name: ""
    method: "self_report|cortisol|heart_rate|eeg|fmri|behavioral_task|observation"
    access_level: "CONSCIOUS|AUTONOMIC|BEHAVIORAL|NEURAL|ENVIRONMENTAL"

# ============================================
# TEMPORAL DYNAMICS (maps to EnablingConditions temporal fields)
# ============================================
temporal:
  onset_latency: ""
  minimum_duration: ""
  effect_persistence: ""
  decay_curve: "linear|exponential|step|unknown"
  dose_response: "linear|asymptotic|u_shaped|threshold|unknown"
  dose_response_tested: true|false|null

# ============================================
# ENABLING CONDITIONS (maps to EnablingConditions)
# ============================================
enabling:
  minimum_exposure: ""
  baseline_state: ""
  concurrent_factors: []
  blocking_factors: []
  threshold: ""
  dosage: ""
  temporal_order: ""

# ============================================
# CAUSAL STRUCTURE (maps to CausalDirection)
# ============================================
causal:
  direction: "FORWARD|REVERSE|BIDIRECTIONAL|CORRELATIONAL|MEDIATED|COMMON_CAUSE|UNKNOWN"
  temporal_precedence: true|false|null
  manipulation: true|false
  mediator: ""
  mediator_tested: true|false
  confounds_controlled: []
  confounds_uncontrolled: []

# ============================================
# DOMAIN & BRIDGE (maps to bridge_warrants)
# ============================================
bridge:
  source_domain: ""
  target_domain: ""
  bridge_type: "MECHANISM|FUNCTIONAL|ANALOGICAL|CONSTITUTIVE|CAPACITY|NONE"
  mechanism_conserved: true|false|null
  assumed_mechanism: ""
  capacity_language: true|false

# ============================================
# CANONICAL IDs (maps to taxonomies)
# ============================================
environment_id: ""  # e.g., "spatial.openness", "natural.vegetation"
outcome_id: ""      # e.g., "affect.stress", "cog.attention"

# ============================================
# CONFLICT (maps to ConflictType)
# ============================================
conflicts:
  - prior_finding: ""
    conflict_type: "GENUINE_CONTRADICTION|SCOPE_BOUNDARY|METHODOLOGICAL_DIVERGENCE|PRECISION_BOUNDARY"
    resolution: ""

# ============================================
# THEORY MAPPING
# ============================================
theory:
  primary_theory: ""
  prediction_type: "core|derived|exploratory"
  causal_pathway: ""
  secondary_theories: []

# ============================================
# CLAIMS (maps to ae.claim.v1)
# ============================================
claims:
  - claim_id: ""
    claim_type: "causal|associational|null|moderated|mechanistic|descriptive"
    statement: ""
    constructs:
      environment_factors:
        - id: ""
          role: "iv"
      outcomes:
        - id: ""
          role: "dv"
      mediators: []
      moderators: []
    statistics:
      effect_size:
        type: "d|r|eta_sq|OR"
        value:
      p_value:
      ci95: [lower, upper]
    ae_confidence:

# ============================================
# RULES (maps to ae.rule.v1)
# ============================================
rules:
  - rule_id: ""
    rule_type: "edge|cpd_hint|prior|constraint|interaction"
    lhs:
      - var: ""
        state: ""
    rhs:
      - var: ""
        state: ""
    polarity: "positive|negative|null|u_shaped|unknown"
    strength:
      kind: "effect_size"
      value:
    applicability:
      population: []
      setting: []
      boundary_conditions: []
    bn_mapping:
      node_suggestions: []
      discretization_hint: ""
```

---

## CHANGELOG

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-03 | Initial template with Research Question rationale, Hypotheses rationale |
| 2.0 | 2026-02-03 | Added: Temporal Dynamics, Enabling Conditions, Causal Structure, Domain & Bridge Signals, Conflict Assessment, Ecological Validity, Measurement Classification, Canonical IDs, full YAML schema |

---

**END OF TEMPLATE v2.0**
