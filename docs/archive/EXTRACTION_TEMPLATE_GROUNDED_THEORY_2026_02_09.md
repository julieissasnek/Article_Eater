# GROUNDED THEORY STUDY EXTRACTION TEMPLATE v1.0

**Version**: 1.0.0
**Date**: February 9, 2026
**Status**: Complete (with panel additions)
**Panel Review**: Pearl, Cartwright, Simon, Bates, Kaplan, Walton, Lipton, Hearst, Teufel
**Tradition**: Glaser & Strauss (1967), Strauss & Corbin, Charmaz (constructivist)

---

## PURPOSE

Grounded theory studies **generate theory inductively from data**. They uniquely contribute:
- New theoretical frameworks grounded in empirical data
- Process models explaining how phenomena unfold
- Category systems derived from participant perspectives
- Substantive theories for specific contexts
- Hypotheses for future quantitative testing

**Key Feature**: Theory emerges from data through systematic comparison, not from prior hypotheses.

---

## GROUNDED THEORY TRADITIONS

| Tradition | Founder | Epistemology | Core Feature |
|-----------|---------|--------------|--------------|
| **Classic/Glaserian** | Glaser | Post-positivist | Theory emerges, researcher discovers |
| **Straussian** | Strauss & Corbin | Pragmatist | Structured coding paradigm |
| **Constructivist** | Charmaz | Interpretivist | Theory co-constructed with participants |

---

## WHAT THIS TEMPLATE CAN ANSWER

| Category | Coverage | Notes |
|----------|----------|-------|
| Theory Generation | YES | Core purpose |
| Process Models | YES | How phenomena unfold over time |
| Category Systems | YES | Conceptual organization |
| Causal Mechanisms | LIMITED | Theoretical, not tested |
| Generalization | THEORETICAL | To similar contexts |

---

## HUMAN-READABLE OUTPUT STRUCTURE

### 1. INTRODUCTION

```
## Introduction

**Phenomenon Under Study**: [What is being theorized?]

**Research Question**:
| Element | Value |
|---------|-------|
| Central question | [What process/phenomenon is being explained?] |
| Scope | [Substantive area] |

**Grounded Theory Approach**:
| Element | Value |
|---------|-------|
| Tradition | Glaserian / Straussian / Constructivist |
| Key methodologist | [Glaser / Strauss & Corbin / Charmaz] |
| Epistemological stance | [Post-positivist / Pragmatist / Interpretivist] |

**Justification for GT**:
- No adequate existing theory
- Process/change is central
- Participant perspectives essential
- Context-specific understanding needed
```

### 2. METHODS

```
## Methods

### Sampling

| Element | Value |
|---------|-------|
| Initial sampling | [How first participants selected] |
| Theoretical sampling | [How sampling evolved based on emerging theory] |
| Total N | |
| Saturation achieved | Yes / No / Partial |
| Evidence of saturation | [How determined] |

### Data Collection

| Source | N | Purpose |
|--------|---|---------|
| Interviews | | [Primary / Secondary] |
| Observations | | |
| Documents | | |
| Other | | |

**Interview Approach**:
| Element | Value |
|---------|-------|
| Structure | Unstructured / Semi-structured |
| Duration | |
| Iterations | [Did interviews evolve with theory?] |

### Analysis

| Element | Value |
|---------|-------|
| Coding approach | Open → Axial → Selective / Initial → Focused / Line-by-line |
| Constant comparison | Yes / No |
| Memo writing | Documented / Not documented |
| Software | [NVivo / Atlas.ti / Manual] |

**Coding Phases**:
| Phase | Description | Output |
|-------|-------------|--------|
| Open/Initial | [Breaking data into concepts] | [N concepts] |
| Axial/Focused | [Relating categories] | [N categories] |
| Selective/Theoretical | [Integrating around core] | [Core category] |
```

### 3. FINDINGS

```
## Findings

### Core Category

**Name**: [The central phenomenon]

**Definition**:
> [What this category captures]

**Properties**:
| Property | Description | Dimensional Range |
|----------|-------------|-------------------|
| | | Low ←→ High |

### Category System

| Category | Definition | Relationship to Core |
|----------|------------|---------------------|
| [Category 1] | | [Condition / Action / Consequence] |
| [Category 2] | | |

### Theoretical Model

**Process/Structure**:
```
[Visual representation or description of the theory]

Conditions → Context → Actions/Interactions → Consequences
```

### Categories in Detail

#### Category 1: [Name]

**Definition**: [What this category means]

**Properties**:
| Property | Dimensions |
|----------|------------|
| | |

**Indicators** (from data):
- [Quote/observation 1]
- [Quote/observation 2]

**Relationship to Core**: [How connected to central phenomenon]

### Process Stages (if applicable)

| Stage | Description | Key Actions | Triggers for Transition |
|-------|-------------|-------------|------------------------|
| 1. | | | |
| 2. | | | |

### Conditional Matrix (Straussian)

| Level | Conditions | How They Affect Process |
|-------|------------|------------------------|
| Micro | | |
| Meso | | |
| Macro | | |

### Environmental Factors (CNfA)

| Environmental Element | Category Connection | Theoretical Role |
|----------------------|---------------------|------------------|
| [Nature element] | [Which category] | [Condition / Context / Mediator] |
```

### 4. THEORY STATEMENT

```
## Theory

### Formal Theory Statement

> [One paragraph stating the theory: Under conditions X, people engage in Y process, which involves Z actions, resulting in W outcomes]

### Theory Type

| Element | Value |
|---------|-------|
| Scope | Substantive / Formal |
| Domain | [Specific area] |
| Core process | [Central action/interaction] |

### Theoretical Propositions

| ID | Proposition | Evidence Strength |
|----|-------------|-------------------|
| P1 | [If X, then Y] | Strong / Moderate / Tentative |
| P2 | | |

### Relationship to Existing Theory

| Theory | Relationship | Notes |
|--------|--------------|-------|
| | Extends / Challenges / Complements / New | |

### Limitations

| Limitation | Impact on Theory |
|------------|-----------------|
| Sample scope | |
| Context specificity | |
| Saturation concerns | |

### Testable Hypotheses

| Hypothesis | Variables | Suggested Design |
|------------|-----------|------------------|
| H1 | [IV → DV] | [Experimental / Survey / etc.] |
```

---

## RULE CONVERSION

Grounded theory produces:
- **Theoretical rules** (propositions about relationships)
- **Process rules** (stage transitions)
- **Conditional rules** (context-dependent relationships)

### Causal Level

| Finding Type | Causal Level | Justification |
|--------------|--------------|---------------|
| Theoretical proposition | `association` | Inductively derived, not tested |
| Process model | `association` | Temporal, not experimental |
| Conditional relationship | `association` | Observational |

**Critical Note**: GT theories are *hypotheses* requiring subsequent testing for causal upgrade.

### Argument Scheme

**Primary**: `argument_from_sign` (observed patterns indicate relationships) + `abductive_argument` (inference to best explanation)

**Critical Questions**:
1. Was theoretical sampling conducted?
2. Was saturation achieved?
3. Is the theory grounded in data (quotes/instances)?
4. Are the categories well-defined and distinct?
5. Does the theory explain the core phenomenon?

### Rule Template

```yaml
rules:
  # Theoretical proposition → Theoretical rule
  - rule_id: "[author]_gt_[year]_prop"
    rule_type: "theoretical"

    description: "[Proposition in natural language]"

    proposition:
      if_condition: "[antecedent]"
      then_outcome: "[consequent]"
      scope: "[when this applies]"

    categories_involved:
      - category: "[category name]"
        role: "condition|action|consequence"

    evidence:
      n_participants:
      n_instances:
      illustrative_quotes: []

    # PANEL ADDITIONS (v2)
    causal_level: "association"  # GT generates hypotheses
    argument_scheme: "abductive_argument"
    critical_questions:
      - "Was theoretical sampling conducted?"
      - "Was saturation achieved?"
      - "Is proposition grounded in data?"

    theory_status: "generated"  # Not tested
    testable: true
    suggested_test: "[How to test this proposition]"

    extraction_difficulty: "hard"
    source_zone: "results"

    applicability:
      scope: "substantive"
      domain: "[specific area]"
      transferable_to: "[similar contexts]"

    ae_confidence: [0.40-0.60]

  # Process stage → Process rule
  - rule_id: "[author]_gt_[year]_process"
    rule_type: "process"

    description: "In [context], [actors] move from [stage A] to [stage B] when [trigger]"

    process:
      stages:
        - stage: "[name]"
          description: "[what happens]"
          conditions: "[when entered]"
      transitions:
        - from: "[stage A]"
          to: "[stage B]"
          trigger: "[what causes transition]"

    temporal_order: true
    reversible: true|false

    causal_level: "association"
    argument_scheme: "argument_from_sign"

    ae_confidence:

  # Conditional relationship → Conditional rule
  - rule_id: "[author]_gt_[year]_conditional"
    rule_type: "conditional"

    description: "When [condition], [relationship holds]"

    condition:
      context: "[situational factors]"
      level: "micro|meso|macro"

    relationship:
      between: ["[category A]", "[category B]"]
      nature: "[how related]"
      strength_qualifier: "strong|moderate|weak"

    ae_confidence:
```

### Confidence Scoring

| Factor | Impact | Rationale |
|--------|--------|-----------|
| **Base** | 0.45 | Theory generation (untested) |
| **Saturation** | | |
| Clearly achieved | +0.10 | Theoretical completeness |
| Claimed but not evidenced | +0.00 | Standard |
| Not achieved / unclear | -0.10 | Incomplete theory |
| **Theoretical sampling** | | |
| Documented and iterative | +0.10 | GT rigor |
| Initial purposive only | +0.00 | Partial GT |
| Convenience only | -0.10 | Not true GT |
| **Grounding** | | |
| Rich quotes supporting categories | +0.05 | Well-grounded |
| Limited evidence shown | +0.00 | Standard |
| **Memo trail** | | |
| Documented | +0.05 | Audit trail |
| Not documented | +0.00 | Common |
| **Member checking** | | |
| Performed | +0.05 | Validation |

**Range**: 0.35 (weak GT) to 0.70 (rigorous GT with saturation)

---

## MACHINE-READABLE DATA

```yaml
# ============================================
# HEADER
# ============================================
paper_id: ""
doi: ""
extraction_date: "YYYY-MM-DD"
article_type: "grounded_theory"
source_depth: "full_text|abstract|metadata"

# ============================================
# GROUNDED THEORY APPROACH
# ============================================
approach:
  tradition: "glaserian|straussian|constructivist"
  key_methodologist: ""
  epistemology: "post_positivist|pragmatist|interpretivist"

# ============================================
# PHENOMENON
# ============================================
phenomenon:
  name: ""
  description: ""
  substantive_area: ""
  research_question: ""

# ============================================
# SAMPLING
# ============================================
sampling:
  initial_sampling: ""
  theoretical_sampling: true|false
  theoretical_sampling_description: ""
  total_n:
  saturation:
    achieved: true|false|partial
    evidence: ""

# ============================================
# DATA COLLECTION
# ============================================
data_collection:
  sources:
    - type: "interviews|observations|documents|other"
      n:
      description: ""

  interviews:
    structure: "unstructured|semi_structured"
    average_duration_minutes:
    evolved_with_theory: true|false

# ============================================
# ANALYSIS
# ============================================
analysis:
  coding_approach: "open_axial_selective|initial_focused|line_by_line"
  constant_comparison: true|false
  memo_writing: true|false
  software: ""

  coding_phases:
    - phase: "open|initial"
      output: ""
      n_concepts:
    - phase: "axial|focused"
      output: ""
      n_categories:
    - phase: "selective|theoretical"
      output: ""
      core_category: ""

# ============================================
# FINDINGS
# ============================================
findings:
  core_category:
    name: ""
    definition: ""
    properties:
      - property: ""
        dimensions: ""

  categories:
    - name: ""
      definition: ""
      relationship_to_core: "condition|action|consequence|context"
      properties:
        - property: ""
          dimensions: ""
      indicators: []

  process_stages:
    - stage: ""
      description: ""
      key_actions: []
      transition_trigger: ""

  conditional_matrix:
    micro: ""
    meso: ""
    macro: ""

  environmental_factors:
    - element: ""
      category_connection: ""
      theoretical_role: ""

# ============================================
# THEORY
# ============================================
theory:
  formal_statement: ""
  scope: "substantive|formal"
  domain: ""
  core_process: ""

  propositions:
    - id: ""
      statement: ""
      evidence_strength: "strong|moderate|tentative"

  relationship_to_existing:
    - theory: ""
      relationship: "extends|challenges|complements|new"

  testable_hypotheses:
    - hypothesis: ""
      variables: ""
      suggested_design: ""

# ============================================
# RULES GENERATED
# ============================================
rules:
  - rule_id: ""
    rule_type: "theoretical|process|conditional"

    description: ""

    proposition:
      if_condition: ""
      then_outcome: ""
      scope: ""

    categories_involved:
      - category: ""
        role: ""

    evidence:
      n_participants:
      n_instances:
      quotes: []

    # v2 panel additions
    causal_level: "association"
    argument_scheme: "abductive_argument"
    critical_questions: []
    extraction_difficulty: "hard"
    source_zone: "results"

    theory_status: "generated"
    testable: true

    applicability:
      scope: "substantive"
      domain: ""

    ae_confidence:

# ============================================
# QUALITY
# ============================================
quality:
  sampling_rigor: "high|moderate|low"
  saturation_evidence: "high|moderate|low"
  grounding_depth: "high|moderate|low"
  theoretical_integration: "high|moderate|low"
  our_confidence:

  # Charmaz criteria
  credibility:
    intimate_familiarity: true|false
    sufficient_data: true|false
    systematic_comparisons: true|false
    strong_logical_links: true|false

  originality:
    fresh_categories: true|false
    new_insights: true|false
    social_significance: true|false

  resonance:
    makes_sense_to_participants: true|false
    offers_deeper_insights: true|false

  usefulness:
    practical_implications: true|false
    sparks_further_research: true|false
```

---

## CNfA DOMAIN FEATURES

For environment-focused grounded theory:

```yaml
environmental_categories:
  # Nature elements as categories
  nature_categories:
    - category: ""
      definition: ""
      role_in_theory: "condition|mediator|outcome"

  # Environmental processes
  environment_process:
    - stage: ""
      environmental_element: ""
      human_response: ""

  # Conditional relationships
  environment_conditions:
    - condition: ""
      environmental_context: ""
      effect_on_process: ""

  # Design implications from theory
  design_propositions:
    - proposition: ""
      environmental_element: ""
      design_implication: ""
      theory_grounding: ""
```

---

## VALIDATION CHECKLIST

- [ ] **Tradition identified** — Glaserian/Straussian/Constructivist
- [ ] **Theoretical sampling documented** — Evolved based on theory
- [ ] **Saturation assessed** — Evidence provided
- [ ] **Core category identified** — Central phenomenon
- [ ] **Categories defined** — With properties and dimensions
- [ ] **Grounding shown** — Quotes support categories
- [ ] **Theory stated** — Formal proposition(s)
- [ ] **Causal level = association** — GT generates, doesn't test
- [ ] **Testable hypotheses derived** — For future research

---

**END OF GROUNDED THEORY TEMPLATE**
