# INTERVIEW STUDY EXTRACTION TEMPLATE v1.0

**Version**: 1.0.0
**Date**: February 9, 2026
**Status**: Complete (with panel additions)
**Panel Review**: Pearl, Cartwright, Simon, Bates, Kaplan, Walton, Lipton, Hearst, Teufel
**Tradition**: Qualitative interview research (Kvale, Rubin & Rubin, Seidman)

---

## PURPOSE

Interview studies systematically gather **participant perspectives and experiences** through direct conversation. They uniquely contribute:
- Direct access to participant viewpoints and reasoning
- Rich descriptions of experiences, beliefs, and practices
- Understanding of meaning-making processes
- Exploration of sensitive or complex topics
- Stakeholder perspectives on phenomena

**Distinction**: Unlike phenomenology (essence of experience) or grounded theory (theory generation), interview studies primarily describe and report participant perspectives without specific analytic framework commitment.

---

## INTERVIEW STUDY TYPES

| Type | Focus | Structure | Output |
|------|-------|-----------|--------|
| **Descriptive** | Document perspectives | Semi-structured | Themes/patterns |
| **Exploratory** | Understand new phenomenon | Unstructured | Initial categories |
| **Explanatory** | Why/how questions | Semi-structured | Participant explanations |
| **Evaluative** | Assess program/intervention | Structured | Stakeholder judgments |
| **Expert** | Specialist knowledge | Semi-structured | Expert opinions |

---

## WHAT THIS TEMPLATE CAN ANSWER

| Category | Coverage | Notes |
|----------|----------|-------|
| Participant Perspectives | YES | What people think/believe/report |
| Reported Experiences | YES | What people say happened |
| Stakeholder Views | YES | Multiple viewpoint synthesis |
| Perceived Relationships | YES | What participants think causes what |
| Actual Causation | NO | Self-report, not observation |
| Generalization | LIMITED | Purposive samples |

---

## HUMAN-READABLE OUTPUT STRUCTURE

### 1. INTRODUCTION

```
## Introduction

**Research Focus**: [What perspectives are being gathered?]

**Research Questions**:
| Question | Type |
|----------|------|
| [RQ1] | Descriptive / Exploratory / Explanatory |

**Interview Study Type**:
| Element | Value |
|---------|-------|
| Type | Descriptive / Exploratory / Explanatory / Evaluative / Expert |
| Rationale | [Why interviews for this question?] |
| Epistemological stance | Realist / Critical realist / Interpretivist |
```

### 2. METHODS

```
## Methods

### Participants

| Element | Value |
|---------|-------|
| N | |
| Selection criteria | [Who was eligible] |
| Sampling strategy | Purposive / Stratified / Snowball / Maximum variation |
| Recruitment | [How recruited] |

**Participant Characteristics**:
| Characteristic | Distribution |
|----------------|--------------|
| [Relevant characteristic] | [N or %] |

### Interview Design

| Element | Value |
|---------|-------|
| Structure | Structured / Semi-structured / Unstructured |
| Format | Individual / Dyad / Focus group |
| Mode | In-person / Phone / Video / Written |
| Duration | [Average] |
| N interviews per participant | |
| Language | |

**Interview Guide**:
| Domain | Sample Questions |
|--------|------------------|
| [Topic 1] | [Key questions] |
| [Topic 2] | [Key questions] |

### Analysis

| Element | Value |
|---------|-------|
| Approach | Thematic / Content / Framework / Descriptive |
| Software | [NVivo / Atlas.ti / Manual] |
| Coding | Inductive / Deductive / Hybrid |
| Reliability | [Inter-rater if applicable] |

**Analysis Steps**:
1. [Step 1]
2. [Step 2]
```

### 3. FINDINGS

```
## Findings

### Overview

**Key Perspectives Identified**:
| Perspective | Prevalence | Brief Description |
|-------------|------------|-------------------|
| [Perspective 1] | N (%) | |

### Themes

#### Theme 1: [Name]

**Description**: [What this theme captures]

**Prevalence**: [All / Most / Some / Few] participants

**Sub-themes** (if applicable):
| Sub-theme | Description |
|-----------|-------------|
| | |

**Representative Quotes**:
> "[Quote 1]" — Participant X (characteristics)
> "[Quote 2]" — Participant Y (characteristics)

**Variation**: [How perspectives varied across participants]

#### Theme 2: [Name]

[Same structure]

### Relationships Between Themes

| Theme A | Theme B | Relationship (per participants) |
|---------|---------|--------------------------------|
| | | [How participants connected these] |

### Participant-Reported Factors

**What participants said influences [phenomenon]**:
| Factor | N mentioning | Typical explanation |
|--------|--------------|---------------------|
| | | [In their words] |

### Points of Consensus and Divergence

**Consensus**:
- [What most/all participants agreed on]

**Divergence**:
| Issue | Perspective A | Perspective B | Who held each |
|-------|---------------|---------------|---------------|
| | | | |

### Environmental Perspectives (CNfA)

| Environmental Feature | Participant Perceptions | N mentioning |
|----------------------|------------------------|--------------|
| [Nature element] | [What they said about it] | |
```

### 4. INTERPRETATION

```
## Interpretation

### Summary of Perspectives

**Participants generally reported that**:
1. [Key finding 1]
2. [Key finding 2]

### Credibility of Reports

| Finding | Evidence Quality | Notes |
|---------|-----------------|-------|
| | Self-report / Corroborated / Inconsistent | |

### What This Study REVEALS

1. Participant perspectives on [topic]
2. Variation in how [topic] is understood
3. Factors participants believe matter

### What This Study CANNOT Conclude

1. ❌ Causal relationships — self-report only
2. ❌ Accuracy of reports — not verified
3. ❌ Generalization — purposive sample
4. ❌ Behavior — reports may differ from action

### Implications

| Domain | Implication |
|--------|-------------|
| Practice | [How to work with this population] |
| Design | [What participants want/value] |
| Research | [What to investigate further] |

### Limitations

| Limitation | Impact |
|------------|--------|
| Self-report bias | |
| Social desirability | |
| Sample specificity | |
| Recall limitations | |
```

---

## RULE CONVERSION

Interview studies produce:
- **Perspective rules** (what stakeholders think/believe)
- **Reported association rules** (what participants say relates to what)
- **Preference rules** (what participants value)

### Causal Level

| Finding Type | Causal Level | Justification |
|--------------|--------------|---------------|
| Reported belief/perspective | Not applicable | Descriptive |
| Participant-claimed causation | `association` | Self-report, unverified |
| Consensus on factors | `association` | Multiple reports, still observational |

**Critical Note**: Even when participants claim "X causes Y," this is their *perception*, not verified causation.

### Argument Scheme

**Primary**: `argument_from_position_to_know` (participants as informants on their own views)

**Critical Questions**:
1. Are participants in a position to know?
2. Might they have motivation to misreport?
3. Were questions leading?
4. Is there convergent evidence?
5. Were diverse perspectives sampled?

### Rule Template

```yaml
rules:
  # Reported perspective → Perspective rule
  - rule_id: "[author]_interview_[year]_perspective"
    rule_type: "perspective"  # Stakeholder viewpoint

    description: "[Stakeholders] report that [perspective on phenomenon]"

    perspective:
      stakeholder: "[who holds this view]"
      content: "[what they believe/think]"
      about: "[phenomenon]"
      prevalence: "[all/most/some]"

    evidence:
      n_participants:
      n_mentioning:
      quotes: []

    # PANEL ADDITIONS (v2)
    causal_level: null  # Perspectives aren't causal claims
    argument_scheme: "argument_from_position_to_know"
    critical_questions:
      - "Are participants positioned to know?"
      - "Might there be reporting bias?"
      - "Were diverse perspectives sampled?"

    extraction_difficulty: "moderate"
    source_zone: "results"

    applicability:
      scope: "perspectival"
      stakeholder_group: "[who this represents]"
      not_generalizable_to: "[other groups]"

    ae_confidence: [0.45-0.65]

  # Participant-reported association → Reported association rule
  - rule_id: "[author]_interview_[year]_reported_assoc"
    rule_type: "reported_association"

    description: "Participants report that [X] is associated with [Y]"

    reported_relationship:
      factor: "[what participants say matters]"
      outcome: "[what they say it affects]"
      direction: "[how they describe relationship]"
      prevalence: "[how many report this]"

    # This is what PARTICIPANTS CLAIM, not verified
    epistemic_status: "participant_report"
    verification: "not_independently_verified"

    evidence:
      n_reporting:
      typical_explanation: "[in their words]"
      quotes: []

    causal_level: "association"  # Their claim, unverified
    argument_scheme: "argument_from_position_to_know"

    ae_confidence:  # Lower due to self-report

  # Preference/value → Preference rule
  - rule_id: "[author]_interview_[year]_preference"
    rule_type: "preference"

    description: "[Stakeholders] prefer/value [X] because [reason]"

    preference:
      stakeholder: ""
      prefers: "[what they want]"
      over: "[alternative, if stated]"
      reason: "[why they prefer it]"

    design_implication:
      insight: "[how to design for this preference]"
      confidence: "stakeholder_reported"

    ae_confidence:
```

### Confidence Scoring

| Factor | Impact | Rationale |
|--------|--------|-----------|
| **Base** | 0.50 | Direct stakeholder input |
| **Sample size** | | |
| N ≥ 20 | +0.05 | Broader perspectives |
| N = 10-19 | +0.00 | Adequate |
| N < 10 | -0.05 | Limited diversity |
| **Sampling strategy** | | |
| Maximum variation / Stratified | +0.05 | Diverse perspectives |
| Purposive adequate | +0.00 | Standard |
| Convenience only | -0.05 | Potential bias |
| **Consensus level** | | |
| Strong consensus (>80%) | +0.10 | Convergent validity |
| Moderate (50-80%) | +0.00 | Standard |
| Divergent (<50%) | -0.05 | Contested |
| **Quote support** | | |
| Rich quotes from multiple participants | +0.05 | Well-documented |
| Limited quotes | +0.00 | Standard |
| **Potential bias** | | |
| Social desirability likely | -0.05 | Reporting concerns |
| Sensitive topic well-handled | +0.00 | Standard |

**Range**: 0.40 (weak interview study) to 0.70 (rigorous with consensus)

---

## MACHINE-READABLE DATA

```yaml
# ============================================
# HEADER
# ============================================
paper_id: ""
doi: ""
extraction_date: "YYYY-MM-DD"
article_type: "interview_study"
source_depth: "full_text|abstract|metadata"

# ============================================
# STUDY TYPE
# ============================================
study_type:
  type: "descriptive|exploratory|explanatory|evaluative|expert"
  epistemology: "realist|critical_realist|interpretivist"
  rationale: ""

# ============================================
# RESEARCH QUESTIONS
# ============================================
research_questions:
  - question: ""
    type: "descriptive|exploratory|explanatory"

# ============================================
# PARTICIPANTS
# ============================================
participants:
  n:
  selection_criteria: ""
  sampling: "purposive|stratified|snowball|maximum_variation"
  recruitment: ""
  characteristics:
    - characteristic: ""
      distribution: ""

# ============================================
# INTERVIEW DESIGN
# ============================================
interview_design:
  structure: "structured|semi_structured|unstructured"
  format: "individual|dyad|focus_group"
  mode: "in_person|phone|video|written"
  average_duration_minutes:
  interviews_per_participant:
  language: ""

  guide_domains:
    - domain: ""
      sample_questions: []

# ============================================
# ANALYSIS
# ============================================
analysis:
  approach: "thematic|content|framework|descriptive"
  software: ""
  coding: "inductive|deductive|hybrid"
  inter_rater_reliability:
  steps: []

# ============================================
# FINDINGS
# ============================================
findings:
  themes:
    - name: ""
      description: ""
      prevalence: "all|most|some|few"
      subthemes:
        - name: ""
          description: ""
      quotes: []
      variation: ""

  relationships_between_themes:
    - theme_a: ""
      theme_b: ""
      relationship: ""

  participant_reported_factors:
    - factor: ""
      n_mentioning:
      typical_explanation: ""

  consensus:
    - ""

  divergence:
    - issue: ""
      perspectives: []
      who_held_each: []

  environmental_perspectives:
    - feature: ""
      perceptions: ""
      n_mentioning:

# ============================================
# INTERPRETATION
# ============================================
interpretation:
  key_findings: []

  credibility_assessment:
    - finding: ""
      evidence_quality: "self_report|corroborated|inconsistent"

  implications:
    practice: ""
    design: ""
    research: ""

  limitations:
    - limitation: ""
      impact: ""

# ============================================
# RULES GENERATED
# ============================================
rules:
  - rule_id: ""
    rule_type: "perspective|reported_association|preference"

    description: ""

    # Perspective rule fields
    perspective:
      stakeholder: ""
      content: ""
      about: ""
      prevalence: ""

    # Reported association fields
    reported_relationship:
      factor: ""
      outcome: ""
      direction: ""

    evidence:
      n_participants:
      n_mentioning:
      quotes: []

    # v2 panel additions
    causal_level: null|"association"
    argument_scheme: "argument_from_position_to_know"
    critical_questions: []
    extraction_difficulty: "moderate"
    source_zone: "results"

    epistemic_status: "participant_report"

    applicability:
      scope: "perspectival"
      stakeholder_group: ""

    ae_confidence:

# ============================================
# QUALITY
# ============================================
quality:
  sampling_adequacy: "high|moderate|low"
  interview_rigor: "high|moderate|low"
  analysis_transparency: "high|moderate|low"
  quote_support: "high|moderate|low"
  our_confidence:
```

---

## CNfA DOMAIN FEATURES

For environment-focused interview studies:

```yaml
environmental_perspectives:
  # What participants say about environments
  reported_environment_effects:
    - environment_feature: ""
      reported_effect: ""
      n_mentioning:
      typical_explanation: ""

  # Environmental preferences
  environmental_preferences:
    - preference: ""
      reason_given: ""
      n_mentioning:

  # Perceived environmental relationships
  perceived_relationships:
    - factor: ""
      outcome: ""
      participant_explanation: ""
      epistemic_status: "participant_perception"

  # Design implications from stakeholders
  stakeholder_design_input:
    - what_they_want: ""
      why: ""
      design_implication: ""
      confidence: "stakeholder_preference"
```

---

## SPECIAL CONSIDERATIONS

### Self-Report Limitations

Interview data is **self-report**. Always note:
1. Participants report their *perceptions*, not necessarily *reality*
2. Social desirability may affect responses
3. Retrospective reports are subject to memory bias
4. Reported behavior may differ from actual behavior

### When to Upgrade Evidence

Interview findings can be upgraded when:
- Corroborated by observation (mixed methods)
- Consistent across diverse stakeholders
- Triangulated with other data sources
- Supported by expert consensus

### Expert Interviews

For expert interviews specifically:
- Note expert credentials
- Distinguish expert opinion from expert knowledge
- Consider whether experts have direct experience or derived knowledge

---

## VALIDATION CHECKLIST

- [ ] **Study type identified** — Descriptive/Exploratory/etc.
- [ ] **Sampling strategy documented** — How participants selected
- [ ] **Interview structure specified** — Structured/Semi/Unstructured
- [ ] **Analysis approach named** — Thematic/Content/etc.
- [ ] **Themes supported by quotes** — Evidence provided
- [ ] **Prevalence noted** — How many held each view
- [ ] **Self-report limitation acknowledged** — Not verified causation
- [ ] **Causal level appropriate** — null for perspectives, association for reported relationships
- [ ] **Stakeholder scope specified** — Who this represents

---

**END OF INTERVIEW STUDY TEMPLATE**
