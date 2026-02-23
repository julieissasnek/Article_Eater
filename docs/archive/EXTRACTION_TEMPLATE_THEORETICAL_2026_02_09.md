# THEORETICAL PAPER EXTRACTION TEMPLATE v1.0

**Version**: 1.0.0
**Date**: February 9, 2026
**Status**: Complete (with panel additions)
**Panel Review**: Pearl, Cartwright, Simon, Bates, Kaplan, Walton, Lipton, Hearst, Teufel
**Tradition**: Philosophy of science, theory development

---

## PURPOSE

Theoretical papers develop **conceptual frameworks, models, or arguments** without primary empirical data. They uniquely contribute:
- New theoretical frameworks and models
- Conceptual clarifications and distinctions
- Logical arguments and derivations
- Integration of existing theories
- Predictions and hypotheses for future testing

**Key Feature**: Arguments are based on logic, existing evidence, and conceptual analysis—not new data collection.

---

## THEORETICAL PAPER TYPES

| Type | Focus | Method | Output |
|------|-------|--------|--------|
| **Framework Development** | New conceptual structure | Synthesis + logic | Theoretical framework |
| **Model Building** | Formal representation | Mathematical/logical | Predictive model |
| **Conceptual Analysis** | Clarify concepts | Philosophical analysis | Definitions, distinctions |
| **Theory Integration** | Combine theories | Comparative analysis | Unified framework |
| **Critique/Extension** | Evaluate existing theory | Argumentation | Revised theory |
| **Hypothesis Generation** | Derive predictions | Deduction | Testable hypotheses |

---

## WHAT THIS TEMPLATE CAN ANSWER

| Category | Coverage | Notes |
|----------|----------|-------|
| Theoretical Frameworks | YES | Conceptual structures |
| Logical Arguments | YES | Deductive claims |
| Definitions | YES | Conceptual clarifications |
| Predictions | YES | Derived hypotheses |
| Causal Mechanisms (proposed) | YES | Theoretical, untested |
| Empirical Evidence | NO | No primary data |

---

## HUMAN-READABLE OUTPUT STRUCTURE

### 1. INTRODUCTION

```
## Introduction

**Theoretical Focus**: [What theory/framework/concept is being developed?]

**Paper Type**:
| Element | Value |
|---------|-------|
| Type | Framework / Model / Conceptual analysis / Integration / Critique / Hypothesis |
| Scope | Broad / Focused |
| Domain | [Substantive area] |

**Central Thesis**:
> [Main theoretical claim or contribution]

**Theoretical Context**:
| Element | Value |
|---------|-------|
| Builds on | [Existing theories/frameworks] |
| Addresses gap | [What theoretical need] |
| Novelty claim | [What is new] |
```

### 2. THEORETICAL FOUNDATION

```
## Theoretical Foundation

### Key Concepts

| Concept | Definition | Source |
|---------|------------|--------|
| [Concept 1] | [How defined in this paper] | New / Adopted / Modified |

### Assumptions

| Assumption | Role | Justification |
|------------|------|---------------|
| [A1] | [What it enables] | [Why accepted] |

### Prior Theory (if building on existing)

| Theory | Relationship | What Adopted | What Changed |
|--------|--------------|--------------|--------------|
| | Extends / Critiques / Integrates | | |
```

### 3. THEORETICAL ARGUMENT

```
## Theoretical Argument

### Argument Structure

**Argument Type**: Deductive / Abductive / Integrative / Analogical

**Premise-Conclusion Structure**:
| Step | Statement | Type | Support |
|------|-----------|------|---------|
| P1 | [Premise 1] | Empirical / Definitional / Assumed | [Citation/logic] |
| P2 | [Premise 2] | | |
| C1 | [Intermediate conclusion] | Derived | From P1, P2 |
| C2 | [Final conclusion] | Derived | From C1, P3... |

### Key Arguments

#### Argument 1: [Name]

**Claim**: [What is being argued]

**Supporting Reasons**:
1. [Reason 1]
2. [Reason 2]

**Evidence Cited**: [Empirical studies referenced]

**Logical Form**: [If applicable]

#### Argument 2: [Name]

[Same structure]

### Proposed Mechanisms (if applicable)

| Mechanism | Description | Status |
|-----------|-------------|--------|
| [M1] | [How it works] | Proposed / Hypothesized |
```

### 4. THEORETICAL FRAMEWORK/MODEL

```
## Framework/Model

### Framework Components

| Component | Description | Role |
|-----------|-------------|------|
| | | |

### Relationships

| From | To | Relationship | Proposed Direction |
|------|----|--------------|-------------------|
| | | | Causal / Constitutive / Correlational |

### Visual Representation (if provided)

[Description of any figures/diagrams]

### Scope Conditions

| Condition | Applies When | Does Not Apply When |
|-----------|--------------|---------------------|
| | | |

### Predictions/Hypotheses Derived

| Hypothesis | Derivation | Testability |
|------------|------------|-------------|
| H1 | From [which premises] | Testable via [method] |
```

### 5. ENVIRONMENTAL/CNfA IMPLICATIONS

```
## Environmental Implications (CNfA)

### Theoretical Claims About Environment

| Environmental Factor | Theoretical Role | Proposed Mechanism |
|---------------------|------------------|-------------------|
| [Nature element] | [Role in framework] | [How it works] |

### Design Implications (derived)

| Implication | Theoretical Basis | Confidence |
|-------------|------------------|------------|
| | [From which argument] | Theoretical only |
```

### 6. CRITICAL ASSESSMENT

```
## Critical Assessment

### Argument Quality

| Criterion | Assessment | Notes |
|-----------|------------|-------|
| Logical validity | Valid / Questionable / Invalid | |
| Premise plausibility | High / Moderate / Low | |
| Evidential support | Strong / Moderate / Weak / None | |
| Internal consistency | Consistent / Tensions noted | |

### Theory Quality

| Criterion | Assessment |
|-----------|------------|
| Clarity | Clear / Moderate / Vague |
| Scope | Appropriate / Too broad / Too narrow |
| Parsimony | Parsimonious / Complex |
| Testability | Highly testable / Partially / Difficult |
| Novelty | Novel / Incremental / Synthesis |

### Limitations Acknowledged

| Limitation | Impact |
|------------|--------|
| | |

### What This Paper CAN Provide

1. Theoretical framework for organizing research
2. Proposed mechanisms (requiring test)
3. Derived hypotheses
4. Conceptual clarifications

### What This Paper CANNOT Provide

1. ❌ Empirical evidence (no data collected)
2. ❌ Confirmed causal relationships
3. ❌ Effect sizes
4. ❌ Validated claims
```

---

## RULE CONVERSION

Theoretical papers produce:
- **Theoretical rules** (proposed relationships)
- **Definitional rules** (concept definitions)
- **Derivation rules** (logically derived claims)
- **Hypothesis rules** (predictions for testing)

### Causal Level

| Finding Type | Causal Level | Justification |
|--------------|--------------|---------------|
| Proposed mechanism | `theoretical` | Not empirically tested |
| Derived prediction | `theoretical` | Logical derivation |
| Conceptual definition | Not applicable | Definitional, not causal |
| Cited empirical finding | INHERIT | From cited source |

**Note**: Theoretical papers propose causal mechanisms but cannot establish causal claims without empirical testing.

### Argument Scheme

**Primary**: `deductive_argument` + `argument_from_analogy` + `abductive_argument`

**Critical Questions**:
1. Are the premises true?
2. Is the argument logically valid?
3. Are there hidden assumptions?
4. Does the framework have adequate scope?
5. Is the theory testable?

### Rule Template

```yaml
rules:
  # Proposed theoretical relationship → Theoretical rule
  - rule_id: "[author]_theory_[year]_rel"
    rule_type: "theoretical"

    description: "[Author] proposes that [X] leads to [Y] via [mechanism]"

    theoretical_claim:
      antecedent: "[X]"
      consequent: "[Y]"
      mechanism: "[proposed how]"
      scope: "[when this applies]"

    derivation:
      from_premises: ["P1", "P2"]
      argument_type: "deductive|abductive|analogical"

    # PANEL ADDITIONS (v2)
    causal_level: "theoretical"  # Proposed, not tested
    argument_scheme: "deductive_argument"
    critical_questions:
      - "Are premises true?"
      - "Is argument valid?"
      - "Is theory testable?"

    extraction_difficulty: "hard"
    source_zone: "body"

    # Theory-specific fields
    epistemic_status: "proposed"
    requires_test: true
    suggested_test: "[how to test this claim]"

    applicability:
      scope: "theoretical"
      domain: "[substantive area]"

    ae_confidence: [0.30-0.50]  # Theoretical only

  # Conceptual definition → Definitional rule
  - rule_id: "[author]_theory_[year]_def"
    rule_type: "definitional"

    description: "[Author] defines [concept] as [definition]"

    definition:
      concept: "[term]"
      definition: "[what it means]"
      source: "new|adopted|modified"
      from_prior: "[if modified, from whom]"

    causal_level: null  # Definitions are not causal
    argument_scheme: "argument_from_definition"

    applicability:
      scope: "within_this_framework"

    ae_confidence: [0.70-0.90]  # Definitions can be high confidence

  # Derived hypothesis → Hypothesis rule
  - rule_id: "[author]_theory_[year]_hyp"
    rule_type: "hypothesis"

    description: "From [framework], [Author] derives hypothesis: [prediction]"

    hypothesis:
      content: "[the prediction]"
      derived_from: ["which premises/claims"]
      testable_via: "[suggested method]"

    causal_level: "theoretical"
    argument_scheme: "deductive_argument"

    # Hypothesis-specific
    falsifiable: true|false
    test_design: "[RCT, quasi-exp, survey, etc.]"
    predicted_effect: "[direction and rough magnitude if stated]"

    ae_confidence:  # Based on argument quality

  # Proposed mechanism → Mechanism rule
  - rule_id: "[author]_theory_[year]_mech"
    rule_type: "mechanism"

    description: "[Author] proposes mechanism: [how X affects Y]"

    mechanism:
      trigger: "[what initiates]"
      process: "[what happens]"
      outcome: "[result]"
      level: "psychological|neural|behavioral|social"

    causal_level: "theoretical"
    requires_empirical_validation: true

    # Link to testable hypotheses
    generates_hypotheses:
      - "[hypothesis_rule_id]"

    ae_confidence:
```

### Confidence Scoring

| Factor | Impact | Rationale |
|--------|--------|-----------|
| **Base** | 0.35 | Theoretical (untested) |
| **Argument quality** | | |
| Logically valid, premises supported | +0.15 | Strong argument |
| Valid but premises questionable | +0.05 | Conditional |
| Logical gaps or unsupported premises | -0.10 | Weak argument |
| **Evidential grounding** | | |
| Builds on strong empirical base | +0.10 | Well-grounded theory |
| Some empirical support | +0.05 | Partial grounding |
| Purely conceptual | +0.00 | Standard for theory |
| **Scope appropriateness** | | |
| Well-bounded scope conditions | +0.05 | Clear applicability |
| Scope unclear | -0.05 | Hard to apply |
| **Testability** | | |
| Clearly testable predictions | +0.05 | Scientific value |
| Difficult to test | -0.05 | Limited utility |

**Range**: 0.20 (weak theoretical speculation) to 0.60 (rigorous theoretical argument)

---

## MACHINE-READABLE DATA

```yaml
# ============================================
# HEADER
# ============================================
paper_id: ""
doi: ""
extraction_date: "YYYY-MM-DD"
article_type: "theoretical"
source_depth: "full_text|abstract|metadata"

# ============================================
# PAPER TYPE
# ============================================
paper_type:
  type: "framework|model|conceptual_analysis|integration|critique|hypothesis_generation"
  scope: "broad|focused"
  domain: ""

# ============================================
# CENTRAL THESIS
# ============================================
thesis:
  main_claim: ""
  novelty: ""
  builds_on: []
  addresses_gap: ""

# ============================================
# THEORETICAL FOUNDATION
# ============================================
foundation:
  key_concepts:
    - concept: ""
      definition: ""
      source: "new|adopted|modified"

  assumptions:
    - assumption: ""
      role: ""
      justification: ""

  prior_theories:
    - theory: ""
      relationship: "extends|critiques|integrates"
      what_adopted: ""
      what_changed: ""

# ============================================
# ARGUMENTS
# ============================================
arguments:
  argument_type: "deductive|abductive|integrative|analogical"

  premise_conclusion:
    - step: ""
      statement: ""
      type: "empirical|definitional|assumed|derived"
      support: ""

  key_arguments:
    - name: ""
      claim: ""
      reasons: []
      evidence_cited: []

  proposed_mechanisms:
    - mechanism: ""
      description: ""
      status: "proposed|hypothesized"

# ============================================
# FRAMEWORK/MODEL
# ============================================
framework:
  components:
    - component: ""
      description: ""
      role: ""

  relationships:
    - from: ""
      to: ""
      relationship: "causal|constitutive|correlational"

  scope_conditions:
    - condition: ""
      applies_when: ""
      not_applies_when: ""

  derived_hypotheses:
    - hypothesis: ""
      derivation: ""
      testability: ""

# ============================================
# QUALITY ASSESSMENT
# ============================================
quality:
  argument_quality:
    logical_validity: "valid|questionable|invalid"
    premise_plausibility: "high|moderate|low"
    evidential_support: "strong|moderate|weak|none"
    internal_consistency: "consistent|tensions"

  theory_quality:
    clarity: "clear|moderate|vague"
    scope: "appropriate|too_broad|too_narrow"
    parsimony: "parsimonious|complex"
    testability: "high|partial|difficult"
    novelty: "novel|incremental|synthesis"

  our_confidence:

# ============================================
# RULES GENERATED
# ============================================
rules:
  # Theoretical relationship
  - rule_id: ""
    rule_type: "theoretical"

    description: ""

    theoretical_claim:
      antecedent: ""
      consequent: ""
      mechanism: ""
      scope: ""

    derivation:
      from_premises: []
      argument_type: ""

    causal_level: "theoretical"
    argument_scheme: "deductive_argument"
    critical_questions: []
    extraction_difficulty: "hard"
    source_zone: "body"

    epistemic_status: "proposed"
    requires_test: true

    ae_confidence:

  # Definition
  - rule_id: ""
    rule_type: "definitional"

    definition:
      concept: ""
      definition: ""
      source: ""

    causal_level: null
    ae_confidence:

  # Hypothesis
  - rule_id: ""
    rule_type: "hypothesis"

    hypothesis:
      content: ""
      derived_from: []
      testable_via: ""

    causal_level: "theoretical"
    falsifiable: true
    ae_confidence:
```

---

## CNfA DOMAIN FEATURES

For environment-focused theoretical papers:

```yaml
environmental_theory:
  # Theoretical claims about nature-human relationships
  theoretical_claims:
    - environmental_factor: ""
      proposed_effect: ""
      mechanism: ""
      theoretical_basis: ""

  # Framework components related to environment
  environmental_constructs:
    - construct: ""
      definition: ""
      role_in_framework: ""

  # Derived design implications (theoretical)
  design_implications_theoretical:
    - implication: ""
      derivation: ""
      confidence: "theoretical_only"

  # Testable environmental hypotheses
  environmental_hypotheses:
    - hypothesis: ""
      predicted_direction: ""
      suggested_test: ""
```

---

## VALIDATION CHECKLIST

- [ ] **Paper type identified** — Framework/Model/etc.
- [ ] **Central thesis captured** — Main theoretical claim
- [ ] **Key concepts defined** — Definitions extracted
- [ ] **Argument structure mapped** — Premises → Conclusions
- [ ] **Mechanisms identified** — Proposed causal processes
- [ ] **Hypotheses derived** — Testable predictions
- [ ] **Scope conditions noted** — When theory applies
- [ ] **Argument quality assessed** — Validity and soundness
- [ ] **Causal level = theoretical** — Untested proposals
- [ ] **Confidence appropriately low** — No empirical validation

---

**END OF THEORETICAL PAPER TEMPLATE**
