# THOUGHT PIECE / COMMENTARY EXTRACTION TEMPLATE v1.0

**Version**: 1.0.0
**Date**: February 9, 2026
**Status**: Complete (with panel additions)
**Panel Review**: Pearl, Cartwright, Simon, Bates, Kaplan, Walton, Lipton, Hearst, Teufel
**Tradition**: Opinion, commentary, perspective articles

---

## PURPOSE

Thought pieces provide **expert opinion, commentary, or provocative perspectives**. They uniquely contribute:
- Expert viewpoints and interpretations
- Novel perspectives and provocations
- Agenda-setting for future research
- Policy recommendations
- Field-level reflections and critiques

**Key Feature**: Persuasive argumentation based on author's expertise and judgment, not systematic evidence or formal theory.

---

## THOUGHT PIECE TYPES

| Type | Focus | Tone | Output |
|------|-------|------|--------|
| **Opinion/Editorial** | Author's view on issue | Persuasive | Position statement |
| **Commentary** | Response to other work | Analytical | Critique or endorsement |
| **Perspective** | Novel viewpoint | Exploratory | New angle on topic |
| **Call to Action** | Future directions | Urgent | Research/policy agenda |
| **Reflection** | Looking back | Retrospective | Lessons learned |
| **Debate/Response** | Engaging disagreement | Adversarial | Counterargument |

---

## WHAT THIS TEMPLATE CAN ANSWER

| Category | Coverage | Notes |
|----------|----------|-------|
| Expert Opinion | YES | Author's views |
| Policy Recommendations | YES | Author's proposals |
| Research Priorities | YES | What author thinks matters |
| Novel Framings | YES | New ways to think about issues |
| Evidence | NO | Not evidence source |
| Causal Claims | NO | Opinion, not data |

---

## HUMAN-READABLE OUTPUT STRUCTURE

### 1. INTRODUCTION

```
## Introduction

**Topic**: [What is the author opining on?]

**Piece Type**:
| Element | Value |
|---------|-------|
| Type | Opinion / Commentary / Perspective / Call to action / Reflection / Debate |
| Trigger | [What prompted this piece?] |
| Stakes | [Why does author think this matters?] |

**Author Position**:
| Element | Value |
|---------|-------|
| Main claim | [Author's central position] |
| Stance | Advocating / Critiquing / Questioning / Proposing |
| Tone | Strong / Moderate / Exploratory |

**Author Credentials**:
| Element | Value |
|---------|-------|
| Expertise area | |
| Position/affiliation | |
| Potential interests | [If declared or apparent] |
```

### 2. ARGUMENT/POSITION

```
## Author's Argument

### Central Claim

> [Author's main position in their words or paraphrase]

### Supporting Arguments

| Argument | Type | Evidence Offered |
|----------|------|------------------|
| [Arg 1] | Logical / Empirical cite / Appeal to authority / Rhetorical | [If any] |
| [Arg 2] | | |

### Rhetorical Strategies

| Strategy | Example |
|----------|---------|
| Appeal to expertise | |
| Appeal to values | |
| Appeal to consequences | |
| Appeal to consensus | |
| Contrast/comparison | |

### Counterarguments Addressed

| Counterargument | Author's Response |
|-----------------|-------------------|
| | |

### Unstated Assumptions

| Assumption | Role in Argument |
|------------|------------------|
| | |
```

### 3. CLAIMS AND RECOMMENDATIONS

```
## Claims and Recommendations

### Factual Claims Made

| Claim | Support Provided | Verifiable |
|-------|-----------------|------------|
| [Claim 1] | Citation / None / Personal experience | Yes / No |

### Value Claims Made

| Claim | Values Invoked |
|-------|---------------|
| [Claim 1] | [What values underpin this] |

### Causal Claims Made

| Claim | Evidence Type | Status |
|-------|--------------|--------|
| [X causes Y] | Opinion / Cited study / None | Asserted, not demonstrated |

### Recommendations

| Recommendation | For Whom | Basis |
|----------------|----------|-------|
| [Rec 1] | Researchers / Practitioners / Policymakers | [Argument supporting] |

### Research Priorities Proposed

| Priority | Rationale |
|----------|-----------|
| | |

### Environmental/Design Implications (CNfA)

| Implication | Author's Reasoning |
|-------------|-------------------|
| | |
```

### 4. CRITICAL ASSESSMENT

```
## Critical Assessment

### Argument Quality

| Criterion | Assessment | Notes |
|-----------|------------|-------|
| Clarity of position | Clear / Moderate / Vague | |
| Logical coherence | Coherent / Gaps / Contradictions | |
| Evidence support | Strong / Moderate / Weak / None | |
| Addresses counterarguments | Yes / Partially / No | |

### Author Credibility

| Factor | Assessment |
|--------|------------|
| Domain expertise | Expert / Knowledgeable / Unclear |
| Track record | Established / Emerging / Unknown |
| Potential conflicts | Declared / Possible / None apparent |

### Rhetorical Assessment

| Factor | Assessment |
|--------|------------|
| Persuasiveness | High / Moderate / Low |
| Balance | Balanced / One-sided |
| Acknowledgment of uncertainty | Good / Poor |

### What This Piece CAN Provide

1. Expert perspective on an issue
2. Proposed research directions
3. Policy recommendations
4. Novel framings of problems

### What This Piece CANNOT Provide

1. ❌ Evidence for claims (opinion piece)
2. ❌ Causal demonstration (no data)
3. ❌ Systematic coverage (selective)
4. ❌ Neutral assessment (advocacy)
```

---

## RULE CONVERSION

Thought pieces produce:
- **Opinion rules** (author's views)
- **Recommendation rules** (proposed actions)
- **Priority rules** (research/policy priorities)
- **Framing rules** (how to think about issues)

### Causal Level

| Finding Type | Causal Level | Justification |
|--------------|--------------|---------------|
| Author's opinion | Not applicable | Opinion, not evidence |
| Causal claim made | `asserted` | Claimed but not demonstrated |
| Cited evidence | INHERIT | From cited source |
| Recommendation | Not applicable | Prescriptive, not descriptive |

**Critical Note**: Thought pieces express views—they do not generate evidence. Even when authors make causal claims, these are assertions requiring verification.

### Argument Scheme

**Primary**: `argument_from_expert_opinion` + `practical_reasoning`

**Critical Questions** (Walton):
1. Is the author credible in this domain?
2. Does the opinion fall within their expertise?
3. Are there other credible experts who disagree?
4. Is the opinion adequately supported?
5. Could there be bias or conflict of interest?

### Rule Template

```yaml
rules:
  # Author's opinion → Opinion rule
  - rule_id: "[author]_opinion_[year]_view"
    rule_type: "opinion"

    description: "[Author] opines that [opinion]"

    opinion:
      claim: "[what author believes]"
      topic: "[what it's about]"
      stance: "advocating|critiquing|questioning|proposing"
      strength: "strong|moderate|tentative"

    author:
      name: ""
      expertise: ""
      credentials: ""
      potential_conflict: ""

    support_offered:
      evidence_cited: []
      logical_argument: ""
      appeal_type: "expertise|values|consequences|consensus"

    # PANEL ADDITIONS (v2)
    causal_level: null  # Opinions are not causal claims
    argument_scheme: "argument_from_expert_opinion"
    critical_questions:
      - "Is author credible in this domain?"
      - "Within their expertise?"
      - "Other experts disagree?"
      - "Adequately supported?"
      - "Potential bias?"

    extraction_difficulty: "easy"
    source_zone: "body"

    # Opinion-specific
    epistemic_status: "expert_opinion"
    requires_verification: true
    weight_in_web: "low"  # Opinions have low epistemic weight

    applicability:
      scope: "opinion"
      domain: "[topic area]"

    ae_confidence: [0.20-0.40]  # Low for opinions

  # Recommendation → Recommendation rule
  - rule_id: "[author]_opinion_[year]_rec"
    rule_type: "recommendation"

    description: "[Author] recommends that [recommendation]"

    recommendation:
      content: "[what is recommended]"
      for_whom: "researchers|practitioners|policymakers"
      basis: "[author's reasoning]"
      urgency: "high|moderate|low"

    causal_level: null  # Recommendations are prescriptive
    argument_scheme: "practical_reasoning"

    # For design extraction
    design_relevance:
      applicable: true|false
      confidence: "expert_opinion_only"

    ae_confidence:

  # Research priority → Priority rule
  - rule_id: "[author]_opinion_[year]_priority"
    rule_type: "priority"

    description: "[Author] prioritizes research on [topic]"

    priority:
      topic: ""
      rationale: ""
      urgency: "high|moderate|low"

    # Useful for VOI search
    voi_relevance: "high"  # Expert-identified priorities
    suggested_by_expert: true

    ae_confidence:

  # Asserted causal claim → Asserted rule
  - rule_id: "[author]_opinion_[year]_asserted"
    rule_type: "asserted"

    description: "[Author] asserts that [X causes Y] (without demonstration)"

    asserted_claim:
      cause: "[X]"
      effect: "[Y]"
      mechanism_proposed: "[if any]"

    causal_level: "asserted"  # Special level for undemonstrated claims
    requires_evidence: true
    verification_status: "unverified"

    ae_confidence: [0.15-0.25]  # Very low for assertions

  # Novel framing → Framing rule
  - rule_id: "[author]_opinion_[year]_frame"
    rule_type: "framing"

    description: "[Author] proposes framing [topic] as [frame]"

    framing:
      topic: "[what is being framed]"
      proposed_frame: "[how to think about it]"
      contrast_with: "[traditional frame if stated]"
      implications: "[what this framing suggests]"

    causal_level: null
    epistemic_status: "proposed_framing"

    ae_confidence:
```

### Confidence Scoring

| Factor | Impact | Rationale |
|--------|--------|-----------|
| **Base** | 0.25 | Opinion (not evidence) |
| **Author expertise** | | |
| Recognized expert | +0.10 | Domain authority |
| Relevant background | +0.05 | Some credibility |
| Outside expertise | -0.05 | Limited credibility |
| **Argument quality** | | |
| Well-reasoned, addresses counterarguments | +0.10 | Strong argumentation |
| Reasonable but one-sided | +0.00 | Standard |
| Poorly supported | -0.10 | Weak case |
| **Evidence cited** | | |
| Strong evidence base | +0.05 | Grounded opinion |
| Some citations | +0.00 | Standard |
| No evidence cited | -0.05 | Pure opinion |
| **Conflict of interest** | | |
| No apparent conflict | +0.00 | Neutral |
| Possible/disclosed conflict | -0.10 | Bias risk |

**Range**: 0.10 (poorly supported opinion) to 0.45 (well-argued expert opinion)

---

## MACHINE-READABLE DATA

```yaml
# ============================================
# HEADER
# ============================================
paper_id: ""
doi: ""
extraction_date: "YYYY-MM-DD"
article_type: "thought_piece"
source_depth: "full_text|abstract|metadata"

# ============================================
# PIECE TYPE
# ============================================
piece_type:
  type: "opinion|commentary|perspective|call_to_action|reflection|debate"
  trigger: ""
  stakes: ""

# ============================================
# AUTHOR
# ============================================
author:
  name: ""
  expertise_area: ""
  position: ""
  affiliation: ""
  potential_conflicts: ""
  credibility_assessment: "expert|knowledgeable|unclear"

# ============================================
# POSITION
# ============================================
position:
  main_claim: ""
  stance: "advocating|critiquing|questioning|proposing"
  tone: "strong|moderate|exploratory"

# ============================================
# ARGUMENTS
# ============================================
arguments:
  central_claim: ""

  supporting_arguments:
    - argument: ""
      type: "logical|empirical_cite|appeal_to_authority|rhetorical"
      evidence: ""

  rhetorical_strategies:
    - strategy: ""
      example: ""

  counterarguments_addressed:
    - counterargument: ""
      response: ""

  unstated_assumptions:
    - assumption: ""
      role: ""

# ============================================
# CLAIMS AND RECOMMENDATIONS
# ============================================
claims:
  factual_claims:
    - claim: ""
      support: "citation|none|personal_experience"
      verifiable: true|false

  value_claims:
    - claim: ""
      values_invoked: ""

  causal_claims:
    - claim: ""
      evidence_type: "opinion|cited_study|none"
      status: "asserted"

recommendations:
  - recommendation: ""
    for_whom: ""
    basis: ""

research_priorities:
  - priority: ""
    rationale: ""

# ============================================
# QUALITY ASSESSMENT
# ============================================
quality:
  argument_quality:
    clarity: "clear|moderate|vague"
    coherence: "coherent|gaps|contradictions"
    evidence_support: "strong|moderate|weak|none"
    addresses_counterarguments: "yes|partially|no"

  rhetorical_quality:
    persuasiveness: "high|moderate|low"
    balance: "balanced|one_sided"
    uncertainty_acknowledged: "good|poor"

  our_confidence:

# ============================================
# RULES GENERATED
# ============================================
rules:
  # Opinion rule
  - rule_id: ""
    rule_type: "opinion"

    description: ""

    opinion:
      claim: ""
      topic: ""
      stance: ""
      strength: ""

    author:
      name: ""
      expertise: ""

    causal_level: null
    argument_scheme: "argument_from_expert_opinion"
    critical_questions: []
    extraction_difficulty: "easy"
    source_zone: "body"

    epistemic_status: "expert_opinion"
    weight_in_web: "low"

    ae_confidence:

  # Recommendation rule
  - rule_id: ""
    rule_type: "recommendation"

    recommendation:
      content: ""
      for_whom: ""
      basis: ""

    causal_level: null
    ae_confidence:

  # Asserted causal claim
  - rule_id: ""
    rule_type: "asserted"

    asserted_claim:
      cause: ""
      effect: ""

    causal_level: "asserted"
    requires_evidence: true
    ae_confidence:
```

---

## CNfA DOMAIN FEATURES

For environment-focused thought pieces:

```yaml
environmental_opinion:
  # Author's views on environmental factors
  environmental_claims:
    - factor: ""
      author_view: ""
      support_offered: ""
      status: "opinion"

  # Design recommendations (opinion-based)
  design_opinions:
    - recommendation: ""
      author_reasoning: ""
      evidence_cited: ""
      confidence: "expert_opinion_only"

  # Research priorities for environment
  environmental_research_priorities:
    - priority: ""
      rationale: ""
      voi_signal: "expert_identified"

  # Proposed framings of nature-human relationship
  nature_framings:
    - framing: ""
      implications: ""
```

---

## SPECIAL CONSIDERATIONS

### Distinguishing Opinion from Evidence

Thought pieces may cite evidence, but the piece itself is not evidence:
- **Cited studies**: Extract separately with proper causal level
- **Author's interpretation**: Extract as opinion
- **Assertions**: Mark as `asserted`, requiring verification

### When Opinions Have Value

Despite low confidence, opinions matter for:
- **VOI search**: Expert-identified priorities signal research needs
- **Framing**: Novel perspectives can inform research questions
- **Practical wisdom**: Experienced practitioners offer insights
- **Agenda-setting**: Influential opinions shape fields

### Handling Controversial Opinions

When extracting contested views:
- Note if opinion contradicts established evidence
- Flag potential conflicts of interest
- Record dissenting expert views if mentioned
- Lower confidence for claims against consensus

---

## VALIDATION CHECKLIST

- [ ] **Piece type identified** — Opinion/Commentary/etc.
- [ ] **Author credentials assessed** — Expertise documented
- [ ] **Main claim captured** — Central position extracted
- [ ] **Arguments mapped** — Supporting reasons listed
- [ ] **Rhetorical strategies noted** — How author persuades
- [ ] **Recommendations extracted** — Practical proposals
- [ ] **Causal claims flagged** — As `asserted`, requiring evidence
- [ ] **Conflicts noted** — Potential bias documented
- [ ] **Confidence appropriately low** — Opinion, not evidence

---

**END OF THOUGHT PIECE TEMPLATE**
