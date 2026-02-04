# THEORETICAL PAPER EXTRACTION TEMPLATE v1.0

**Version**: 1.0.0
**Date**: February 3, 2026
**Derived From**: Complete Requirements Specification (96 questions)
**Panel Review**: Pearl, Cartwright, Simon, Bates, Kaplan

---

## PURPOSE

Theoretical papers provide **proposed causal structures** without new empirical data. They uniquely contribute:
- Constraint rules (forbidden edges based on logic/definitions)
- Proposed edge rules (causal hypotheses to be tested)
- Scope condition specifications
- Derivation chains linking established findings to new predictions

---

## WHAT THIS TEMPLATE CAN ANSWER

| Category | Coverage | Notes |
|----------|----------|-------|
| Causal Structure | PROPOSED | Hypothesized, not empirically tested |
| Scope | SPECIFIED | Theorist states intended scope |
| Bridge Warrants | PROPOSED | Mechanisms articulated |
| Testable Predictions | UNIQUE | Novel predictions for future test |
| Constraints | UNIQUE | What CANNOT cause what |

## WHAT THIS TEMPLATE CANNOT ANSWER

- Effect sizes (no empirical data)
- Sample characteristics (no study conducted)
- Statistical results (no data)
- Ecological validity (no methodology)

---

## HUMAN-READABLE OUTPUT STRUCTURE

When constructing the human-readable extraction document for a **theoretical paper**, follow this structure:

### 1. INTRODUCTION SECTION

**Structure**: Theoretical Question + Why This Theory + Positioning

```
## Introduction

**Theoretical Question**: [What theoretical problem is being addressed?]

**Why This Theory Now**:
- Gap: [What theoretical gap exists?]
- Problem: [What's wrong with current theories?]
- Stakes: [What do we lose without better theory?]

**Relationship to Existing Theories**:

| Theory | Relationship |
|--------|-------------|
| [Theory A] | Extends / Contradicts / Subsumes / Complements |

**Key Terms Defined**:

| Term | Author's Definition | Standard Definition | Differs? |
|------|--------------------|--------------------|----------|
| [Term 1] | [Definition] | [Standard] | Yes/No |
```

### 2. PROPOSITIONS SECTION

**Structure**: Core Claims → Derivation Chain → Auxiliary Assumptions

```
## Theoretical Propositions

### Core Propositions

| P# | Statement | Type | Falsifiable? |
|----|-----------|------|--------------|
| P1 | [Core claim 1] | Stipulated/Derived | Yes/No |
| P2 | [Core claim 2] | Stipulated/Derived | Yes/No |

**If stipulated**: Why this axiom?
**If derived**: From which premises?

### Derivation Chain (Pearl)

**Premises**:
1. [Premise 1] — Source: Stipulated / From [citation]
2. [Premise 2] — Source: Stipulated / From [citation]

**Logical Steps**:

```
Premise 1: A → B
Premise 2: B → C
---------------
∴ Conclusion: A → C (by transitivity)
```

**Auxiliary Assumptions** (unstated but required):

| Assumption | Testable? |
|------------|-----------|
| [Hidden assumption 1] | Yes/No |
```

### 3. CAUSAL STRUCTURE SECTION

**Structure**: Variables → Proposed Edges → Forbidden Edges → Mediators

```
## Proposed Causal Structure

### Variables (Nodes)

| Variable | Definition | Observable? | Canonical ID |
|----------|------------|-------------|--------------|
| X | [Definition] | Yes/Latent | ENV_XXX |
| Y | [Definition] | Yes/Latent | OUT_XXX |

### Proposed Causal Edges

```
    [Mechanism 1]        [Mechanism 2]
X ─────────────────→ M ─────────────────→ Y
         ↑
         │ [Blocks]
         W
```

| From | To | Mechanism | Evidence |
|------|----|-----------| ---------|
| X | M | [Mechanism] | Proposed / Established |
| M | Y | [Mechanism] | Proposed / Established |

### Forbidden Edges (Constraints)

| From | To | Reason Why Forbidden |
|------|----|--------------------|
| Y | X | [Logical/Definitional/Empirical] |

**Constraint Rules for BN**: These relationships CANNOT exist

### Mediating Pathways

| Path | Full Chain | Testable Prediction |
|------|------------|---------------------|
| X → Y | X → M1 → M2 → Y | If M1 blocked, X ⊥ Y |
```

### 4. SCOPE & TESTABILITY SECTION

**Structure**: Scope Conditions → Novel Predictions → Falsification Criteria

```
## Scope Conditions (Cartwright)

### Explicit Scope

| Dimension | Stated Scope | Quote/Page |
|-----------|--------------|------------|
| Population | [Scope] | p. X |
| Setting | [Scope] | p. X |
| Temporal | [Scope] | p. X |

### Implicit Scope (from examples)

| Dimension | Implied | Basis |
|-----------|---------|-------|
| [Dimension] | [Implied scope] | Example on p. X |

### Boundary Silence

| Dimension | Unknown Applicability |
|-----------|-----------------------|
| [Dimension] | Theory doesn't speak to [X] |

**⚠️ Universal Scope Claim?**: [If theory claims universal applicability, flag as suspicious]

## Testability Assessment (Simon)

### Novel Predictions

| Prediction | Not Already Known? | How to Test |
|------------|-------------------|-------------|
| [Prediction 1] | Yes/No | [Experimental design] |

### Falsification Criteria

| If This Occurs | Theory Is | Severity |
|----------------|-----------|----------|
| [Observation 1] | Refuted/Weakened | Core/Peripheral |
```

### 5. DISCUSSION SECTION

**Structure**: Comparison to Competitors → Strengths → Weaknesses → Assessment

```
## Discussion

### Comparison to Competing Theories

| Theory | Agreement | Disagreement | This Theory's Advantage |
|--------|-----------|--------------|------------------------|
| [Competitor] | [Shared] | [Differs] | [Advantage] |

### Bridge Warrants

| Source Domain | Target Domain | Bridge Type | Mechanism? |
|---------------|---------------|-------------|------------|
| [Domain A] | [Domain B] | MECHANISM/FUNCTIONAL/ANALOGICAL | Yes: [what] / No |

### Our Assessment

**Strengths**:
- [Strength 1]
- [Strength 2]

**Weaknesses**:
- [Weakness 1]
- [Weakness 2]

**Derivation Quality**: Strong / Moderate / Weak
**Testability**: High / Moderate / Low
**Scope Clarity**: Explicit / Implicit / Unclear

### Inferential Boundaries

What this theory does NOT claim:

1. ❌ [Non-claim 1]
2. ❌ [Non-claim 2]
3. ❌ [Non-claim 3]

### Rules Generated

**Constraint rules** (primary output):
- [Variable A] ⊥ [Variable B] (forbidden edge because [reason])

**Proposed edge rules** (secondary, pending test):
- [Variable A] → [Variable B] (proposed, confidence: proposed)
```

---

## CAUSAL DIAGRAM GUIDANCE

**If authors provide a diagram**:
- Include figure directly
- Caption with: theory name, source page

**If creating ASCII representation**:

```
                    ┌──────────────┐
                    │   Mediator   │
                    │      M       │
                    └──────┬───────┘
                           │
         Mechanism A       │       Mechanism B
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
┌──────────────┐                ┌──────────────┐
│  Antecedent  │                │   Outcome    │
│      X       │ ════════╳═══> │      Y       │
└──────────────┘   forbidden    └──────────────┘
                   (no direct
                    effect)
```

**Notation**:
- `→` proposed edge
- `╳` forbidden edge (constraint)
- `--→` established edge (from prior work)
- `┌─┐` latent variable

---

## RULE CONVERSION: FROM THEORY TO QUINEAN WEB

Theoretical papers primarily produce **constraint rules** (forbidden edges) and **proposed edge rules** (hypotheses awaiting test). They do NOT produce cpd_hints (no empirical data).

### REQUIRED ELEMENTS FOR RULE INCORPORATION

#### 1. Argument Structure (What Warrants Theoretical Claims?)

| Element | Required? | Source | If Missing |
|---------|-----------|--------|------------|
| **Proposition statement** | ✅ Required | CORE PROPOSITIONS | Cannot create rule |
| **Derivation chain** | ✅ Required | DERIVATION CHAIN | Weak constraint |
| **Auxiliary assumptions** | ✅ Required | DERIVATION CHAIN | Hidden premises flagged |
| **Falsification criteria** | Recommended | TESTABILITY | Theory strength affected |

**Theoretical Argument Structure**:
```yaml
argument:
  claim: "[Theoretical proposition]"
  warrant_type: "theoretical_derivation|conceptual_analysis|logical_necessity"
  premises:
    - "[Premise 1]"
    - "[Premise 2]"
  logical_steps:
    - "[Step 1: operation]"
    - "[Step 2: operation]"
  conclusion: "[Derived conclusion]"
  auxiliary_assumptions:
    - assumption: "[Hidden assumption]"
      stated: true|false
      testable: true|false
  derivation_quality: "strong|moderate|weak"
```

#### 2. Interrogative Structure (What Questions Does Theory Answer?)

| Question | Theory Answers | How |
|----------|---------------|-----|
| "What CANNOT cause what?" | ✅ Yes | Constraint rules (forbidden edges) |
| "What MIGHT cause what?" | ✅ Yes | Proposed edge rules |
| "What is the mechanism?" | ✅ Yes | Mediating pathways |
| "What is the effect size?" | ❌ No | No empirical data |
| "What enables the effect?" | ⚠️ Sometimes | If theory specifies |

```yaml
interrogative_completeness:
  # Theory DOES answer
  what_is_forbidden: true  # Constraints
  what_is_proposed: true   # Hypotheses
  what_mechanism: true|false
  what_scope: true|false   # If specified

  # Theory CANNOT answer
  what_effect_size: false
  what_confidence_interval: false
  how_strong: false
```

#### 3. Rule Types from Theoretical Papers

| Theoretical Element | → Rule Type | Confidence |
|--------------------|-------------|------------|
| Forbidden edge (logical) | `constraint` | High (0.90) |
| Forbidden edge (definitional) | `constraint` | High (0.85) |
| Forbidden edge (empirical disconfirmation) | `constraint` | Moderate (0.70) |
| Proposed causal edge | `edge` (status: proposed) | Low (0.40-0.60) |
| Proposed mediation | `edge` chain (status: proposed) | Low (0.35-0.55) |
| Scope specification | `constraint` (scope) | Per derivation quality |

---

### RULE TYPE DECISION TREE FOR THEORETICAL PAPERS

```
                    ┌─────────────────────────────┐
                    │  What type of theoretical   │
                    │  claim?                     │
                    └──────────────┬──────────────┘
                                   │
      ┌────────────────────────────┼────────────────────────────┐
      │                            │                            │
      ▼                            ▼                            ▼
┌───────────┐              ┌───────────┐              ┌───────────┐
│ Forbidden │              │ Proposed  │              │ Scope     │
│ relationship│            │ causal    │              │ condition │
│            │              │ edge     │              │           │
└─────┬─────┘              └─────┬─────┘              └─────┬─────┘
      │                          │                          │
      ▼                          ▼                          ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│ CONSTRAINT    │          │ EDGE rule     │          │ CONSTRAINT    │
│ rule          │          │ (proposed)    │          │ (scope)       │
│               │          │               │          │               │
│ confidence:   │          │ confidence:   │          │               │
│ by reason     │          │ 0.40-0.60     │          │               │
└───────────────┘          │ (awaits test) │          └───────────────┘
      │                    └───────────────┘
      │
      ├─── Logical necessity → 0.90
      ├─── Definitional → 0.85
      └─── Empirical disconfirm → 0.70
```

---

### COMPLETE CONVERSION EXAMPLES

**Example 1: Forbidden Edge (Logical) → Constraint Rule**

*From ART theory (Kaplan & Kaplan)*:
```yaml
theoretical_claim:
  statement: "Fascination cannot directly cause directed attention capacity"
  reason: "Fascination is the mechanism BY WHICH attention is restored;
           it is not a separate cause of capacity"
  reason_type: "logical"
  derivation:
    premise_1: "Fascination = involuntary attention engagement"
    premise_2: "Directed attention capacity = resource for voluntary attention"
    premise_3: "Involuntary engagement replenishes voluntary capacity (definitional)"
    conclusion: "Fascination is the mechanism, not a parallel cause"
```

*Converted to rule*:
```yaml
rules:
  - rule_id: "art_constraint_1"
    rule_type: "constraint"

    constraint_type: "forbidden_edge"
    from_var: "FASCINATION"
    to_var: "DIRECTED_ATTENTION_CAPACITY"
    edge_forbidden: true

    reason: "Fascination is the mechanism of restoration, not a separate cause"
    reason_type: "logical"

    derivation:
      premises:
        - id: 1
          statement: "Fascination = involuntary attention engagement"
          source: "Kaplan & Kaplan (1989) definition"
        - id: 2
          statement: "Capacity replenishment occurs via involuntary engagement"
          source: "ART core claim"
      logical_operation: "If A is the mechanism of B→C, A cannot independently cause C"
      derivation_quality: "strong"

    # Theory source
    source_theory: "Attention Restoration Theory"
    source_paper: "kaplan_kaplan_1989"

    # Constraint confidence by reason type
    ae_confidence: 0.90  # Logical necessity

    # What this constraint does in BN
    bn_implication:
      forbids_edge: true
      in_structure: "FASCINATION → DIRECTED_ATTENTION_CAPACITY"
      allows: "NATURE → FASCINATION → RESTORATION → CAPACITY"
```

**Example 2: Proposed Causal Edge → Edge Rule (Proposed)**

*From SRT (Ulrich)*:
```yaml
theoretical_claim:
  statement: "Natural scenes trigger parasympathetic activation"
  mechanism: "Innate biophilic response to savanna-like features"
  status: "proposed"
  falsifiable: true
  test_prediction: "HR variability should increase within 3 minutes of nature exposure"
```

*Converted to rule*:
```yaml
rules:
  - rule_id: "srt_proposed_1"
    rule_type: "edge"

    lhs:
      - var: "ENV_NATURE_SCENE"
        state: "viewed"
        canonical_id: "ENV_NATURE_VISUAL"
    rhs:
      - var: "PARASYMPATHETIC_ACTIVATION"
        state: "increased"
        canonical_id: "PHYS_PNS_ACTIVATION"
    polarity: "positive"

    # CRITICAL: Status is PROPOSED, not established
    status: "proposed"

    strength:
      kind: "theoretical"
      confidence: "proposed"  # NOT "established"
      awaits_empirical_test: true

    # Mechanism proposed
    mechanism:
      proposed: "biophilic_innate_response"
      specified: true
      testable: true

    # Testable prediction
    test_prediction:
      prediction: "HRV increase within 3 min of nature exposure"
      falsification_criterion: "No HRV change or decrease"
      severity: "core"  # Would refute theory if false

    # Theory source
    source_theory: "Stress Reduction Theory"
    source_paper: "ulrich_1984"

    # Low confidence until tested
    ae_confidence: 0.50  # Proposed only

    # Questions this WOULD answer if confirmed
    questions_answerable_if_confirmed:
      - "C.3"  # Mechanism
      - "C.1"  # Causal direction (if tested experimentally)
```

**Example 3: Scope Specification → Constraint Rule**

*From Kaplan's writings on ART scope*:
```yaml
scope_claim:
  dimension: "population"
  claim: "ART applies to humans with intact attention systems"
  excludes: "Severe ADHD, dementia, acute psychosis"
  basis: "Theory assumes directed attention capacity exists to be restored"
```

*Converted to rule*:
```yaml
rules:
  - rule_id: "art_scope_1"
    rule_type: "constraint"

    constraint_type: "scope_boundary"

    description: "ART predictions do not apply to populations with
                  fundamentally impaired attention systems"

    scope_limitation:
      dimension: "population"
      applies_to: ["healthy_adults", "children_typical", "mild_fatigue"]
      does_not_apply_to: ["severe_adhd", "dementia", "acute_psychosis"]
      reason: "Theory presumes directed attention capacity exists"

    source_theory: "Attention Restoration Theory"

    ae_confidence: 0.80  # Explicit scope statement

    # What this does in inference
    bn_implication:
      any_art_prediction:
        requires: "population ∈ [healthy_adults, children_typical, mild_fatigue]"
        invalid_if: "population ∈ [severe_adhd, dementia, acute_psychosis]"
```

**Example 4: Mediating Pathway → Chain of Proposed Edge Rules**

*From ART mediating structure*:
```yaml
mediation_claim:
  path: "Nature → Being Away → Soft Fascination → Extent → Compatibility → Restoration"
  each_link: "proposed"
  full_chain: "Restoration requires all four components"
```

*Converted to rules*:
```yaml
rules:
  # Edge 1: Nature → Being Away
  - rule_id: "art_path_1a"
    rule_type: "edge"
    lhs: [{var: "ENV_NATURE", state: "present"}]
    rhs: [{var: "ART_BEING_AWAY", state: "experienced"}]
    polarity: "positive"
    status: "proposed"
    mechanism: "Physical/psychological distance from demands"
    ae_confidence: 0.55

  # Edge 2: Nature → Fascination
  - rule_id: "art_path_1b"
    rule_type: "edge"
    lhs: [{var: "ENV_NATURE", state: "present"}]
    rhs: [{var: "ART_FASCINATION", state: "engaged"}]
    polarity: "positive"
    status: "proposed"
    mechanism: "Innate interest in natural stimuli"
    ae_confidence: 0.60

  # [Additional edges for Extent, Compatibility...]

  # Constraint: Restoration requires all components
  - rule_id: "art_requirement_1"
    rule_type: "constraint"
    constraint_type: "enabling_condition"
    description: "Full restoration requires all four ART components"
    required_for: "RESTORATION"
    requires_all:
      - "ART_BEING_AWAY"
      - "ART_FASCINATION"
      - "ART_EXTENT"
      - "ART_COMPATIBILITY"
    ae_confidence: 0.70
```

---

### CONFIDENCE SCORING FOR THEORETICAL RULES

| Factor | Impact | Rationale |
|--------|--------|-----------|
| **Constraint reason type** | | |
| Logical necessity | 0.90 | Cannot be otherwise |
| Definitional | 0.85 | By definition |
| Empirical disconfirmation | 0.70 | Could be revised |
| **Derivation quality** | | |
| Explicit premises, valid logic | +0.10 | Strong derivation |
| Some gaps in derivation | 0 | Moderate |
| Mostly stipulation | -0.15 | Weak derivation |
| **Falsifiability** | | |
| Clear falsification criteria | +0.05 | Scientific |
| Vague criteria | -0.05 | Less scientific |
| Unfalsifiable | -0.15 | Pseudoscience flag |
| **Scope clarity** | | |
| Explicit scope stated | +0.05 | Honest limitation |
| Claims universal scope | -0.10 | Cartwright warning |

**Base confidence for proposed edges**: 0.50
**Base confidence for constraints**: 0.80
**Range**: 0.35 (weak theory) to 0.90 (strong logical constraint)

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
| Article type | THEORETICAL |
| Source depth | [ ] Full text [ ] Abstract only [ ] Metadata only |

---

## OUR SUMMARY

- Plain-language summary of theoretical contribution (1-3 sentences)
- Key causal claims proposed
- Novel predictions made

---

## THEORY IDENTIFICATION

**Q: What theory is this paper about?**

| Element | Value |
|---------|-------|
| Theory name | |
| Original proponent | |
| Year introduced | |
| This paper's contribution | Extension / Critique / Synthesis / Novel theory |

**Q: What is the relationship to existing theories?**

| Related Theory | Relationship |
|----------------|--------------|
| | Extends / Contradicts / Subsumes / Complements |

---

## RESEARCH QUESTION

**Q.RQ.1: What theoretical question does this address?**

**Q.RQ.2: What gap in theoretical understanding does this fill?**

**Q.RQ.3: Why is this theoretical contribution needed now?**

---

## CORE PROPOSITIONS

**Q: What are the core theoretical claims?**

| Prop # | Statement | Type | Falsifiable? | Falsification Criteria |
|--------|-----------|------|--------------|----------------------|
| P1 | | Stipulated / Derived | Yes / No / Unclear | |
| P2 | | Stipulated / Derived | Yes / No / Unclear | |
| P3 | | Stipulated / Derived | Yes / No / Unclear | |

**Q: For each proposition, what is the basis?**

| Prop # | If Stipulated | If Derived |
|--------|---------------|------------|
| P1 | Why this axiom? | From which premises? |

---

## PROPOSED CAUSAL STRUCTURE *(Pearl)*

### Nodes (Variables)

**Q: What variables does the theory posit?**

| Node | Definition | Observable? | Canonical ID |
|------|------------|-------------|--------------|
| | | Yes / Latent | |

### Proposed Edges

**Q: What causal relationships does the theory propose?**

| From | To | Mechanism | Confidence | Evidence Cited |
|------|----|-----------|-----------:|----------------|
| | | | Proposed / Established | |

### Forbidden Edges (Constraints)

**Q: What relationships does the theory say CANNOT exist?**

| From | To | Reason (why forbidden) |
|------|----|-----------------------|
| | | Logical / Definitional / Empirical disconfirmation |

### Mediating Pathways

**Q: What mediating structures does the theory propose?**

| Path | Mediators | Full Chain |
|------|-----------|------------|
| A → Z | M1, M2 | A → M1 → M2 → Z |

---

## SCOPE CONDITIONS *(Cartwright)*

**Q.SC: What is the intended scope of this theory?**

### Explicit Scope

| Dimension | Stated Scope | Quote/Page |
|-----------|--------------|------------|
| Population | | |
| Setting | | |
| Temporal | | |
| Cultural | | |

### Implicit Scope *(inferred from examples)*

| Dimension | Implied Scope | Basis |
|-----------|---------------|-------|
| | | From examples in text |

### Boundary Silence *(where theory doesn't speak)*

| Dimension | Silent On | Implication |
|-----------|-----------|-------------|
| | | Unknown applicability |

**⚠️ If theory claims universal scope, flag as suspicious** (Cartwright)

---

## DERIVATION CHAIN *(Pearl)*

**Q: How are conclusions derived from premises?**

### Premises

| # | Premise | Source |
|---|---------|--------|
| 1 | | Stipulated / From prior work [citation] |
| 2 | | |

### Logical Steps

| Step | From | Operation | Yields |
|------|------|-----------|--------|
| 1 | Premise 1, 2 | [logical operation] | Intermediate conclusion |
| 2 | | | |

### Auxiliary Assumptions

**Q: What auxiliary assumptions are required?**

| Assumption | Stated? | Testable? |
|------------|---------|-----------|
| | Yes / No | Yes / No |

### Conclusion

| Conclusion | Derived From | Confidence |
|------------|--------------|------------|
| | Steps X, Y | Strong / Weak derivation |

---

## TESTABILITY ASSESSMENT *(Simon)*

**Q.TA.1: Is this theory falsifiable?**
[ ] Yes [ ] No [ ] Unclear

**Q.TA.2: What would count as evidence AGAINST this theory?**

| Prediction | If False, Theory Is | Severity |
|------------|---------------------|----------|
| | Refuted / Weakened / Unaffected | Core / Peripheral |

**Q.TA.3: What NOVEL predictions does this theory make?**

| Prediction | Not Already Known? | Testable How? |
|------------|-------------------|---------------|
| | Yes / No | [Experimental design] |

---

## TERM DEFINITIONS *(Bates)*

**Q: How does the theorist define key terms?**

| Term | Author's Definition | Standard Definition | Differs? |
|------|--------------------|--------------------|----------|
| | | | Yes / No |

**Q: What canonical ID maps to each term?**

| Author's Term | Canonical ID | Confidence |
|---------------|--------------|------------|
| | | High / Low |

---

## BRIDGE WARRANTS *(Cartwright)*

**Q.BW: Does this theory propose bridges between domains?**

| Source Domain | Target Domain | Bridge Type | Mechanism Specified? |
|---------------|---------------|-------------|---------------------|
| | | MECHANISM / FUNCTIONAL / ANALOGICAL / CONSTITUTIVE / CAPACITY | Yes → [what] / No |

**Q: What licenses the transfer?**

| Bridge | Warrant Statement | Confidence |
|--------|-------------------|------------|
| | Why should findings transfer? | High / Medium / Low |

---

## TEMPORAL SPECIFICATIONS *(If theory addresses)*

**Q: Does the theory specify temporal dynamics?**

| Parameter | Specified? | Value |
|-----------|------------|-------|
| Onset latency | Yes / No | |
| Duration requirements | Yes / No | |
| Decay/persistence | Yes / No | |
| Timescale (acute/chronic) | Yes / No | |

---

## ENABLING CONDITIONS *(If theory addresses)*

**Q: Does the theory specify enabling conditions?**

| Condition | Specified? | Value |
|-----------|------------|-------|
| Baseline state required | Yes / No | |
| Concurrent factors | Yes / No | |
| Blocking factors | Yes / No | |
| Threshold | Yes / No | |

---

## COMPARISON TO COMPETING THEORIES

**Q: How does this theory relate to competitors?**

| Competing Theory | Agreement | Disagreement | This Theory's Advantage |
|------------------|-----------|--------------|------------------------|
| | | | |

---

## OUR ASSESSMENT

**Strengths**
- [What this theory does well]

**Weaknesses**
- [Gaps in the theory]

**Derivation Quality**
[ ] Strong (explicit premises, valid logic)
[ ] Moderate (some gaps in derivation)
[ ] Weak (mostly stipulation)

**Testability**
[ ] High (clear falsifiable predictions)
[ ] Moderate (some testable aspects)
[ ] Low (largely unfalsifiable)

---

## PRACTICAL IMPLICATIONS *(If theory addresses)*

**Q: What design implications follow from this theory?**

| If Theory True | Design Implication |
|----------------|-------------------|
| | |

---

## Q&A SECTION

**Q: What is the core theoretical claim?**
A:

**Q: Is this falsifiable?**
A:

**Q: What predictions does it make?**
A:

**Q: What scope does it apply to?**
A:

**Q: How does it relate to [competing theory]?**
A:

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
# QUESTIONS ANSWERED
# ============================================
questions:
  # Identification
  ID.1_citation: ""
  ID.2_article_type: "theoretical"
  ID.3_source_depth: ""

  # Research Question
  RQ.1_primary_question: ""
  RQ.2_gap_addressed: ""
  RQ.3_timeliness: ""

# ============================================
# THEORY IDENTIFICATION
# ============================================
theory:
  name: ""
  original_proponent: ""
  year_introduced:
  this_paper_contribution: "extension|critique|synthesis|novel"
  related_theories:
    - theory: ""
      relationship: "extends|contradicts|subsumes|complements"

# ============================================
# CORE PROPOSITIONS
# ============================================
propositions:
  - id: "P1"
    statement: ""
    type: "stipulated|derived"
    falsifiable: true|false|null
    falsification_criteria: ""
    basis: ""

# ============================================
# CAUSAL STRUCTURE (Pearl)
# ============================================
causal_structure:
  # Nodes
  nodes:
    - id: ""
      definition: ""
      observable: true|false
      canonical_id: ""

  # Proposed Edges
  proposed_edges:
    - from: ""
      to: ""
      mechanism: ""
      confidence: "proposed|established"
      evidence_cited: ""

  # Forbidden Edges (CONSTRAINT rules)
  forbidden_edges:
    - from: ""
      to: ""
      reason: ""
      reason_type: "logical|definitional|empirical"

  # Mediating Pathways
  mediating_pathways:
    - path_id: ""
      full_chain: []
      mediators: []

# ============================================
# SCOPE CONDITIONS (Cartwright)
# ============================================
scope:
  explicit:
    population: ""
    setting: ""
    temporal: ""
    cultural: ""
  implicit:
    - dimension: ""
      implied_scope: ""
      basis: ""
  boundary_silence:
    - dimension: ""
      implication: ""
  claims_universal: true|false  # Flag if true

# ============================================
# DERIVATION CHAIN (Pearl)
# ============================================
derivation:
  premises:
    - id: 1
      statement: ""
      source: "stipulated|prior_work"
      citation: ""

  logical_steps:
    - step: 1
      from_premises: []
      operation: ""
      yields: ""

  auxiliary_assumptions:
    - assumption: ""
      stated: true|false
      testable: true|false

  conclusion:
    statement: ""
    derived_from: []
    derivation_strength: "strong|moderate|weak"

# ============================================
# TESTABILITY (Simon)
# ============================================
testability:
  falsifiable: true|false|null
  evidence_against:
    - prediction: ""
      if_false: "refuted|weakened|unaffected"
      severity: "core|peripheral"
  novel_predictions:
    - prediction: ""
      not_already_known: true|false
      testable_how: ""

# ============================================
# TERM DEFINITIONS (Bates)
# ============================================
term_definitions:
  - term: ""
    author_definition: ""
    standard_definition: ""
    differs: true|false
    canonical_id: ""

# ============================================
# BRIDGE WARRANTS (Cartwright)
# ============================================
bridge_warrants:
  - source_domain: ""
    target_domain: ""
    bridge_type: "MECHANISM|FUNCTIONAL|ANALOGICAL|CONSTITUTIVE|CAPACITY"
    mechanism_specified: true|false
    assumed_mechanism: ""
    warrant_statement: ""
    confidence: "high|medium|low"

# ============================================
# TEMPORAL (If specified)
# ============================================
temporal_specified:
  onset_latency: ""
  duration_requirements: ""
  decay_persistence: ""
  timescale: "acute|chronic|both|unspecified"

# ============================================
# ENABLING CONDITIONS (If specified)
# ============================================
enabling_specified:
  baseline_state: ""
  concurrent_factors: []
  blocking_factors: []
  threshold: ""

# ============================================
# RULES GENERATED
# ============================================
rules:
  # Constraint rules (primary output)
  - rule_id: ""
    rule_type: "constraint"
    constraint_type: "forbidden_edge"
    from_var: ""
    to_var: ""
    reason: ""
    ae_confidence:

  # Proposed edge rules (secondary)
  - rule_id: ""
    rule_type: "edge"
    lhs:
      - var: ""
        state: ""
    rhs:
      - var: ""
        state: ""
    polarity: "positive|negative"
    strength:
      kind: "theoretical"
      confidence: "proposed"  # Not "established" until tested
    derivation_quality: "strong|moderate|weak"
    ae_confidence:

# ============================================
# QUALITY ASSESSMENT
# ============================================
quality:
  derivation_quality: "strong|moderate|weak"
  testability: "high|moderate|low"
  scope_clarity: "explicit|implicit|unclear"
  our_confidence:
```

---

**END OF THEORETICAL PAPER TEMPLATE**
