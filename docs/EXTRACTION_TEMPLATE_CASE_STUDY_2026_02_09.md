# CASE STUDY EXTRACTION TEMPLATE v1.0

**Version**: 1.0.0
**Date**: February 9, 2026
**Status**: Complete (with panel additions)
**Panel Review**: Pearl, Cartwright, Simon, Bates, Kaplan, Walton, Lipton, Hearst, Teufel

---

## PURPOSE

Case studies provide **in-depth examination** of specific instances. They uniquely contribute:
- Rich contextual understanding
- Process tracing and mechanism discovery
- Theory development and hypothesis generation
- Documentation of unique, exemplary, or critical cases
- Integration of multiple data sources

**Key Limitation**: Limited generalizability from single/few cases

---

## CASE STUDY TYPES

| Type | Purpose | Generalization Strategy |
|------|---------|------------------------|
| **Intrinsic** | Understand this specific case | None (case is the interest) |
| **Instrumental** | Case illuminates broader phenomenon | Theoretical (not statistical) |
| **Collective** | Multiple cases studied together | Cross-case patterns |
| **Critical** | Case that definitively tests theory | Logical (if theory fails here, fails generally) |
| **Exemplary** | Model case for design/practice | Design precedent |
| **Deviant** | Anomalous case that challenges theory | Boundary identification |

---

## WHAT THIS TEMPLATE CAN ANSWER

| Category | Coverage | Notes |
|----------|----------|-------|
| Process/Mechanism | YES | How things unfold in context |
| Contextual Factors | YES | Rich environmental description |
| Theory Development | YES | Hypotheses for testing |
| Design Precedent | YES | What worked in this case |
| Statistical Generalization | NO | N=1 or few |
| Causal Effects | LIMITED | Process tracing possible |

---

## HUMAN-READABLE OUTPUT STRUCTURE

### 1. INTRODUCTION SECTION

```
## Introduction

**Case Identification**:
| Element | Value |
|---------|-------|
| Case name/ID | |
| Case type | Intrinsic / Instrumental / Collective / Critical / Exemplary / Deviant |
| Why this case | [Justification for selection] |

**Research Question**: [What does this case help us understand?]

**Theoretical Framework**:
| Theory | How Case Relates | Expectation |
|--------|-----------------|-------------|
| [Theory] | Tests / Develops / Challenges | [What to look for] |
```

### 2. CASE DESCRIPTION

```
## Case Description

### Context

| Dimension | Description |
|-----------|-------------|
| Physical setting | |
| Temporal context | |
| Social context | |
| Institutional context | |
| Historical context | |

### The Case Itself

**Narrative Description**: [Rich description of the case]

**Key Features**:
| Feature | Description | Significance |
|---------|-------------|--------------|
| | | |

### Timeline of Events

| Date/Period | Event | Significance |
|-------------|-------|--------------|
| | | |
```

### 3. DATA SOURCES

```
## Data Sources

| Source Type | Specifics | Role in Analysis |
|-------------|-----------|------------------|
| Documents | [What documents] | [How used] |
| Interviews | [N, with whom] | [How used] |
| Observations | [When, what] | [How used] |
| Archival | [What records] | [How used] |
| Physical artifacts | [What] | [How used] |

**Triangulation**: [How sources were combined/cross-validated]
```

### 4. ANALYSIS

```
## Analysis

### Themes/Patterns

| Theme | Evidence | Confidence |
|-------|----------|------------|
| | [Sources supporting] | High/Mod/Low |

### Process Tracing (if applicable)

| Step | Observation | Mechanism Implied |
|------|-------------|-------------------|
| 1 | | |
| 2 | | |

### Environmental Features (CNfA)

| Feature | Present/Absent | Role in Case |
|---------|----------------|--------------|
| Natural elements | | |
| Spatial configuration | | |
| Sensory qualities | | |

### Outcomes Observed

| Outcome | Measurement | Value |
|---------|-------------|-------|
| | | |
```

### 5. INTERPRETATION

```
## Interpretation

### What This Case Shows

| Finding | Confidence | Type |
|---------|------------|------|
| | High/Mod/Low | Pattern / Mechanism / Anomaly |

### Theoretical Implications

| Theory | Implication | Status |
|--------|-------------|--------|
| | Supported / Extended / Challenged | |

### Generalization Assessment

| Question | Answer |
|----------|--------|
| Is statistical generalization claimed? | Yes / No (should be No) |
| Is theoretical generalization claimed? | Yes / No — [to what] |
| What are the boundary conditions? | [When this case's lessons apply] |

### What This Case CANNOT Tell Us

1. ❌ [Limitation 1]
2. ❌ [Limitation 2]
3. ❌ [Limitation 3]

### Hypotheses Generated (for future research)

| Hypothesis | Suggested Test | Priority |
|------------|---------------|----------|
| | | High/Med/Low |
```

---

## RULE CONVERSION

Case studies produce:
- **Presumption rules** (default assumptions from exemplary cases)
- **Constraint rules** (boundary conditions from deviant cases)
- **Prior rules** (weak hypotheses for testing)

### Causal Level

| Case Type | Causal Level | Justification |
|-----------|--------------|---------------|
| With process tracing | `association` (can approach intervention logic) | Mechanism observed |
| Without process tracing | `association` | Correlation only |
| Critical case | Can inform `counterfactual` | If fails here, fails generally |

### Argument Scheme

**Primary for case studies**: `argument_from_example` or `argument_from_analogy`

**Critical Questions**:
1. Is this case representative or exceptional?
2. Are there relevant differences from target cases?
3. What boundary conditions limit transfer?
4. Was the case selected to confirm prior beliefs?

### Rule Template

```yaml
rules:
  # Exemplary case → Presumption rule
  - rule_id: "[author]_case_[year]_presumption"
    rule_type: "presumption"  # Default until contradicted

    description: "In [context], [feature] is associated with [outcome]"

    lhs:
      - var: "[CONTEXT_FEATURE]"
        state: "[observed]"
    rhs:
      - var: "[OUTCOME]"
        state: "[observed]"
    polarity: "positive|negative"

    strength:
      kind: "case_based"
      case_type: "exemplary|critical|deviant"
      n_cases: 1
      process_tracing: true|false
      replicability: "single_instance"

    # PANEL ADDITIONS (v2)
    causal_level: "association"  # Rarely higher for case studies
    argument_scheme: "argument_from_example"
    critical_questions:
      - "Is this case representative?"
      - "What makes this case transferable?"
      - "What boundary conditions apply?"
    contrast_class: "[this case vs. typical cases]"
    difference_maker: "[unique features of this case]"

    extraction_difficulty: "moderate|hard"  # Case studies require interpretation
    source_zone: "results|discussion"

    applicability:
      scope_specified: true
      scope_source: "case_boundaries"
      generalizes_to:
        - "[similar contexts]"
      does_not_generalize_to:
        - "[different contexts]"

    # Case-specific metadata
    case_metadata:
      case_type: "intrinsic|instrumental|collective|critical|exemplary|deviant"
      selection_rationale: ""
      data_sources: []
      triangulation: true|false

    ae_confidence: [0.35-0.55]  # Lower than experimental

  # Deviant case → Constraint rule
  - rule_id: "[author]_case_[year]_constraint"
    rule_type: "constraint"
    constraint_type: "boundary"

    description: "Finding X does not hold in context Y"

    constraint:
      any_rule_about: "[phenomenon]"
      boundary_identified: "[what case shows is a limit]"
      evidence: "deviant_case"

    ae_confidence: 0.60  # Deviant cases are informative about boundaries

  # Hypothesis from case → Prior rule
  - rule_id: "[author]_case_[year]_hypothesis"
    rule_type: "prior"

    description: "[Hypothesis generated from case observation]"

    prior:
      belief: "[What the case suggests]"
      strength: "weak"  # Until tested
      requires_test: true
      suggested_test: "[Experimental design to test]"

    ae_confidence: 0.40  # Hypothesis, not established
```

### Confidence Scoring

| Factor | Impact | Rationale |
|--------|--------|-----------|
| **Base** | 0.40 | Single case limitation |
| **Case type** | | |
| Critical case | +0.10 | Logically powerful |
| Exemplary case | +0.05 | Design precedent value |
| Intrinsic case | +0.00 | Not intended to generalize |
| Deviant case | +0.05 | Boundary identification |
| **Data quality** | | |
| Multiple data sources | +0.10 | Triangulation |
| Single source | -0.05 | Weak evidence |
| **Process tracing** | | |
| Mechanism identified | +0.10 | Causal insight |
| No mechanism | +0.00 | Correlation only |
| **Researcher positionality** | | |
| Disclosed and reflexive | +0.05 | Transparent |
| Not discussed | -0.05 | Potential bias |

**Range**: 0.30 (weak case study) to 0.60 (rigorous case study)

---

## MACHINE-READABLE DATA

```yaml
# ============================================
# HEADER
# ============================================
paper_id: ""
doi: ""
extraction_date: "YYYY-MM-DD"
article_type: "case_study"
source_depth: "full_text|abstract|metadata"

# ============================================
# CASE IDENTIFICATION
# ============================================
case:
  name: ""
  type: "intrinsic|instrumental|collective|critical|exemplary|deviant"
  selection_rationale: ""
  n_cases: 1  # Or more for collective
  if_collective:
    cases: []

# ============================================
# CONTEXT
# ============================================
context:
  physical_setting: ""
  temporal: ""
  social: ""
  institutional: ""
  historical: ""

# ============================================
# DATA SOURCES
# ============================================
data_sources:
  - type: "documents|interviews|observations|archival|artifacts"
    specifics: ""
    role: ""
triangulation: true|false
triangulation_method: ""

# ============================================
# ANALYSIS
# ============================================
analysis:
  approach: "thematic|pattern_matching|process_tracing|cross_case"

  themes:
    - name: ""
      evidence: []
      confidence: "high|moderate|low"

  process_tracing:
    performed: true|false
    steps:
      - observation: ""
        mechanism_implied: ""

  environmental_features:
    - feature: ""
      present: true|false
      role: ""

  outcomes:
    - outcome: ""
      measurement: ""
      value: ""

# ============================================
# INTERPRETATION
# ============================================
interpretation:
  findings:
    - finding: ""
      confidence: ""
      type: "pattern|mechanism|anomaly"

  theoretical_implications:
    - theory: ""
      implication: "supported|extended|challenged"

  generalization:
    statistical_claimed: false  # Should be false
    theoretical_claimed: true|false
    generalizes_to: []
    boundary_conditions: []

  limitations:
    - ""

  hypotheses_generated:
    - hypothesis: ""
      suggested_test: ""
      priority: "high|medium|low"

# ============================================
# DOMAIN FEATURES (CNfA)
# ============================================
domain_features:
  natural_elements:
    - element: ""
      role_in_case: ""
  spatial_configuration: ""
  sensory_qualities: []
  design_features:
    - feature: ""
      significance: ""

# ============================================
# RULES GENERATED
# ============================================
rules:
  - rule_id: ""
    rule_type: "presumption|constraint|prior"

    description: ""

    # For presumption/prior
    lhs:
      - var: ""
        state: ""
    rhs:
      - var: ""
        state: ""
    polarity: ""

    strength:
      kind: "case_based"
      case_type: ""
      n_cases:
      process_tracing:

    # v2 panel additions
    causal_level: "association"
    argument_scheme: "argument_from_example"
    critical_questions: []
    contrast_class: ""
    difference_maker: ""
    extraction_difficulty: ""
    source_zone: ""

    applicability:
      generalizes_to: []
      does_not_generalize_to: []

    case_metadata:
      case_type: ""
      data_sources: []
      triangulation:

    ae_confidence:

# ============================================
# QUALITY
# ============================================
overall_quality:
  rigor: "high|moderate|low"
  transparency: "high|moderate|low"
  transferability: "high|moderate|low"
  our_confidence:
```

---

## VALIDATION CHECKLIST

Before finalizing extraction:

- [ ] **Case type identified** — Intrinsic/Instrumental/etc.
- [ ] **Selection rationale documented** — Why this case
- [ ] **Data sources triangulated** — Multiple sources preferred
- [ ] **Generalization claims appropriate** — Theoretical, not statistical
- [ ] **Boundary conditions specified** — When lessons apply
- [ ] **Hypotheses generated** — Future research directions
- [ ] **Confidence appropriately low** — Single case limitations acknowledged

---

**END OF CASE STUDY TEMPLATE**
