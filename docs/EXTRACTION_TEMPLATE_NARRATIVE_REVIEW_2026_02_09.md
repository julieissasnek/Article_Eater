# NARRATIVE REVIEW EXTRACTION TEMPLATE v1.0

**Version**: 1.0.0
**Date**: February 9, 2026
**Status**: Complete (with panel additions)
**Panel Review**: Pearl, Cartwright, Simon, Bates, Kaplan, Walton, Lipton, Hearst, Teufel
**Tradition**: Traditional literature review, expert synthesis

---

## PURPOSE

Narrative reviews provide **expert synthesis and interpretation of a literature**. They uniquely contribute:
- Broad overview of a research area
- Expert interpretation and contextualization
- Identification of themes and trends
- Historical development of ideas
- Accessible summaries for non-specialists

**Key Distinction from Systematic Reviews**: Narrative reviews use expert judgment for study selection and synthesis rather than explicit, reproducible methods.

---

## NARRATIVE REVIEW TYPES

| Type | Focus | Scope | Output |
|------|-------|-------|--------|
| **Traditional** | Broad overview | Wide | Comprehensive summary |
| **Critical** | Evaluation and critique | Focused | Critical assessment |
| **State-of-the-art** | Current knowledge | Recent | Contemporary synthesis |
| **Conceptual** | Theoretical integration | Theoretical | Conceptual framework |
| **Scoping** | Map literature extent | Broad | Literature landscape |

---

## WHAT THIS TEMPLATE CAN ANSWER

| Category | Coverage | Notes |
|----------|----------|-------|
| Literature Overview | YES | What research exists |
| Expert Interpretation | YES | What the literature means |
| Research Trends | YES | How field has developed |
| Evidence Synthesis | LIMITED | Non-systematic, potential bias |
| Causal Claims | INHERITED | From cited studies only |
| Gaps/Future Directions | YES | Expert perspective |

---

## HUMAN-READABLE OUTPUT STRUCTURE

### 1. INTRODUCTION

```
## Introduction

**Review Focus**: [What topic/question is being reviewed?]

**Review Type**:
| Element | Value |
|---------|-------|
| Type | Traditional / Critical / State-of-the-art / Conceptual / Scoping |
| Scope | Broad / Focused |
| Time period | [Years covered] |

**Review Questions**:
| Question | Type |
|----------|------|
| [RQ1] | Descriptive / Evaluative / Integrative |

**Author Expertise**:
| Element | Value |
|---------|-------|
| Domain expertise | [Author background in this area] |
| Stated perspective | [Any declared theoretical stance] |
```

### 2. METHODS (if stated)

```
## Methods

**Note**: Narrative reviews typically do not follow systematic methods.

### Literature Search (if described)

| Element | Value |
|---------|-------|
| Databases | [If stated] |
| Search strategy | [If described] |
| Date range | |
| Inclusion criteria | [If explicit] |

### Selection Process

| Element | Value |
|---------|-------|
| Selection approach | Expert judgment / Convenience / Comprehensive |
| Transparency | High / Moderate / Low / Not stated |

### Synthesis Approach

| Element | Value |
|---------|-------|
| Synthesis method | Narrative / Thematic / Chronological / Conceptual |
| Critical appraisal | Performed / Not performed / Partial |
```

### 3. FINDINGS

```
## Findings

### Literature Overview

**Scope of Literature**:
| Element | Value |
|---------|-------|
| Approximate N studies | |
| Key sources cited | |
| Dominant methodologies | |

### Main Themes/Sections

#### Theme 1: [Name]

**Summary**: [What the literature shows on this theme]

**Key Studies Cited**:
| Study | Finding | Author's Interpretation |
|-------|---------|------------------------|
| [Citation] | [What study found] | [How reviewer interprets it] |

**Author's Synthesis**:
> [Reviewer's integrative statement]

#### Theme 2: [Name]

[Same structure]

### Historical Development (if included)

| Period | Key Developments | Representative Work |
|--------|-----------------|---------------------|
| | | |

### Theoretical Integration (if included)

| Theory | Role in Literature | Author's Assessment |
|--------|-------------------|---------------------|
| | | |

### Environmental Factors (CNfA)

| Factor | Literature Status | Key Citations |
|--------|------------------|---------------|
| [Nature element] | Well-established / Emerging / Contested | |
```

### 4. AUTHOR'S CONCLUSIONS

```
## Author's Conclusions

### Summary Statements

| Conclusion | Evidence Basis | Confidence Level |
|------------|---------------|------------------|
| [Conclusion 1] | [Studies supporting] | Strong / Moderate / Weak |

### Identified Gaps

| Gap | Significance | Suggested Direction |
|-----|--------------|---------------------|
| | | |

### Future Directions

| Direction | Rationale |
|-----------|-----------|
| | |

### Author's Recommendations

| Recommendation | For Whom | Basis |
|----------------|----------|-------|
| [Rec 1] | Practitioners / Researchers / Policy | [Supporting argument] |
```

### 5. CRITICAL ASSESSMENT

```
## Critical Assessment

### Review Quality

| Criterion | Assessment | Notes |
|-----------|------------|-------|
| Search transparency | High / Moderate / Low | |
| Selection bias risk | High / Moderate / Low | |
| Synthesis rigor | High / Moderate / Low | |
| Author expertise | Established / Emerging / Unknown | |

### Limitations

| Limitation | Impact |
|------------|--------|
| Non-systematic selection | Potential bias |
| No quality assessment | Can't weight evidence |
| Expert interpretation | May reflect author's views |

### What We CAN Extract

1. Expert interpretations of literature
2. Claimed relationships (attributed to cited studies)
3. Identified gaps and directions
4. Theoretical frameworks proposed

### What We CANNOT Extract

1. ❌ Novel causal claims (no primary data)
2. ❌ Effect sizes (not synthesized)
3. ❌ Comprehensive evidence (selection unknown)
```

---

## RULE CONVERSION

Narrative reviews produce:
- **Interpretive rules** (author's synthesis of literature)
- **Attributed rules** (claims attributed to cited primary studies)
- **Gap rules** (identified research needs)

### Causal Level

| Finding Type | Causal Level | Justification |
|--------------|--------------|---------------|
| Author's synthesis | `association` max | Expert interpretation |
| Attributed to RCT | INHERIT from source | Pass through |
| Attributed to observational | `association` | Pass through |
| Identified gap | Not applicable | Future research need |

**Critical Note**: Narrative reviews do not generate causal evidence—they interpret existing evidence.

### Argument Scheme

**Primary**: `argument_from_expert_opinion` + `argument_from_position_to_know`

**Critical Questions** (from Walton):
1. Is the author a genuine expert in this domain?
2. Is the author's interpretation within their area of expertise?
3. Are there other experts who disagree?
4. Is the author's opinion based on adequate evidence?
5. Could the author be biased?

### Rule Template

```yaml
rules:
  # Author's interpretive synthesis → Interpretive rule
  - rule_id: "[author]_narrev_[year]_interp"
    rule_type: "interpretive"

    description: "[Author] synthesizes that [interpretation of literature]"

    interpretation:
      claim: "[what author concludes]"
      based_on: "[cited evidence base]"
      scope: "[what literature this covers]"

    author_expertise:
      domain: "[field]"
      credentials: "[relevant background]"
      potential_bias: "[any declared stance]"

    evidence_base:
      n_studies_cited:
      key_citations: []
      selection_method: "expert_judgment|convenience|comprehensive"

    # PANEL ADDITIONS (v2)
    causal_level: "association"  # Max for interpretation
    argument_scheme: "argument_from_expert_opinion"
    critical_questions:
      - "Is author expert in this domain?"
      - "Is interpretation within expertise?"
      - "Are there dissenting experts?"
      - "Is opinion based on adequate evidence?"

    extraction_difficulty: "moderate"
    source_zone: "discussion"

    # Interpretive-specific
    epistemic_status: "expert_interpretation"
    verifiable: false  # Cannot verify selection

    applicability:
      scope: "interpretive"
      applies_to: "[domain covered]"

    ae_confidence: [0.35-0.55]  # Lower due to non-systematic

  # Claim attributed to primary study → Attributed rule
  - rule_id: "[author]_narrev_[year]_attr_[cited_author]"
    rule_type: "attributed"

    description: "[Narrative author] cites [primary author] as showing [finding]"

    attribution:
      primary_source: "[cited study]"
      primary_author: "[cited author]"
      year:
      finding: "[what is attributed]"
      reviewer_interpretation: "[how narrative author frames it]"

    # Causal level INHERITED from primary source
    causal_level: "[from_primary_source]"
    inherited_from: "[primary_source_id]"

    # Flag for verification
    needs_verification: true
    verification_note: "Extract directly from primary source for accurate causal level"

    ae_confidence:  # Discounted from primary

  # Identified gap → Gap rule
  - rule_id: "[author]_narrev_[year]_gap"
    rule_type: "gap"

    description: "[Author] identifies gap: [what is missing in literature]"

    gap:
      content: "[what research is needed]"
      significance: "[why it matters]"
      suggested_direction: "[what to do]"

    causal_level: null  # Gaps are not causal claims
    argument_scheme: "argument_from_ignorance"  # We don't know because no one studied it

    voi_relevance: "high"  # Gaps are high-value for VOI search

    ae_confidence:
```

### Confidence Scoring

| Factor | Impact | Rationale |
|--------|--------|-----------|
| **Base** | 0.40 | Non-systematic review |
| **Author expertise** | | |
| Established expert | +0.10 | Domain authority |
| Emerging scholar | +0.00 | Standard |
| Unknown expertise | -0.05 | Cannot assess |
| **Search transparency** | | |
| Methods described | +0.10 | Can assess coverage |
| Partially described | +0.00 | Limited |
| Not described | -0.10 | Cannot assess selection |
| **Critical appraisal** | | |
| Quality assessment performed | +0.05 | Some rigor |
| No quality assessment | +0.00 | Typical |
| **Scope appropriateness** | | |
| Appropriate to question | +0.05 | Good fit |
| Too narrow/broad | -0.05 | Coverage concerns |

**Range**: 0.25 (poor narrative review) to 0.60 (rigorous expert synthesis)

---

## MACHINE-READABLE DATA

```yaml
# ============================================
# HEADER
# ============================================
paper_id: ""
doi: ""
extraction_date: "YYYY-MM-DD"
article_type: "narrative_review"
source_depth: "full_text|abstract|metadata"

# ============================================
# REVIEW CHARACTERISTICS
# ============================================
review_type:
  type: "traditional|critical|state_of_the_art|conceptual|scoping"
  scope: "broad|focused"
  time_period: ""

# ============================================
# AUTHOR INFORMATION
# ============================================
author:
  expertise_domain: ""
  credentials: ""
  stated_perspective: ""
  potential_bias: ""

# ============================================
# METHODS (if stated)
# ============================================
methods:
  search_described: true|false
  databases: []
  date_range: ""
  selection_approach: "expert_judgment|convenience|comprehensive"
  inclusion_criteria_explicit: true|false
  synthesis_approach: "narrative|thematic|chronological|conceptual"
  critical_appraisal: true|false

# ============================================
# LITERATURE COVERAGE
# ============================================
literature:
  approximate_n_studies:
  key_sources: []
  dominant_methodologies: []
  time_span: ""

# ============================================
# THEMES
# ============================================
themes:
  - name: ""
    summary: ""
    key_studies:
      - citation: ""
        finding: ""
        interpretation: ""
    author_synthesis: ""

# ============================================
# CONCLUSIONS
# ============================================
conclusions:
  summary_statements:
    - conclusion: ""
      evidence_basis: ""
      confidence: "strong|moderate|weak"

  gaps:
    - gap: ""
      significance: ""
      suggested_direction: ""

  future_directions:
    - direction: ""
      rationale: ""

  recommendations:
    - recommendation: ""
      for_whom: ""
      basis: ""

# ============================================
# CRITICAL ASSESSMENT
# ============================================
quality:
  search_transparency: "high|moderate|low"
  selection_bias_risk: "high|moderate|low"
  synthesis_rigor: "high|moderate|low"
  author_expertise: "established|emerging|unknown"
  our_confidence:

# ============================================
# RULES GENERATED
# ============================================
rules:
  # Interpretive rule
  - rule_id: ""
    rule_type: "interpretive"

    description: ""

    interpretation:
      claim: ""
      based_on: ""
      scope: ""

    author_expertise:
      domain: ""
      credentials: ""

    evidence_base:
      n_studies_cited:
      key_citations: []

    causal_level: "association"
    argument_scheme: "argument_from_expert_opinion"
    critical_questions: []
    extraction_difficulty: "moderate"
    source_zone: "discussion"

    epistemic_status: "expert_interpretation"

    ae_confidence:

  # Attributed rule
  - rule_id: ""
    rule_type: "attributed"

    attribution:
      primary_source: ""
      finding: ""
      reviewer_interpretation: ""

    causal_level: ""  # Inherited
    inherited_from: ""
    needs_verification: true

    ae_confidence:

  # Gap rule
  - rule_id: ""
    rule_type: "gap"

    gap:
      content: ""
      significance: ""

    causal_level: null
    voi_relevance: "high"

    ae_confidence:
```

---

## CNfA DOMAIN FEATURES

For environment-focused narrative reviews:

```yaml
environmental_synthesis:
  # Author's interpretation of environmental evidence
  environmental_interpretations:
    - factor: ""
      literature_status: "established|emerging|contested"
      author_assessment: ""
      key_citations: []

  # Identified environmental research gaps
  environmental_gaps:
    - gap: ""
      significance_for_cnfa: ""

  # Design recommendations from synthesis
  design_recommendations:
    - recommendation: ""
      evidence_basis: "strong|moderate|weak"
      author_confidence: ""
```

---

## VALIDATION CHECKLIST

- [ ] **Review type identified** — Traditional/Critical/etc.
- [ ] **Author expertise assessed** — Domain credentials
- [ ] **Methods transparency noted** — Search described?
- [ ] **Key citations captured** — Evidence base documented
- [ ] **Author's interpretations extracted** — Synthesis statements
- [ ] **Attributed claims flagged** — Need verification from primary
- [ ] **Gaps identified** — For VOI search
- [ ] **Causal level = association max** — Reviews don't generate causal evidence
- [ ] **Confidence appropriately discounted** — Non-systematic bias

---

**END OF NARRATIVE REVIEW TEMPLATE**
