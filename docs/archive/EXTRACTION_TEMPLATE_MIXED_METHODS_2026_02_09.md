# MIXED METHODS EXTRACTION TEMPLATE v1.0

**Version**: 1.0.0
**Date**: February 9, 2026
**Status**: Complete (with panel additions)
**Panel Review**: Pearl, Cartwright, Simon, Bates, Kaplan, Walton, Lipton, Hearst, Teufel
**Framework**: Creswell & Plano Clark (2018) mixed methods typology

---

## PURPOSE

Mixed methods studies combine quantitative and qualitative approaches. They uniquely contribute:
- Convergent validity (quan + qual agreement)
- Complementary insights (different facets of phenomenon)
- Explanation of mechanisms behind statistical patterns
- Development and testing in sequence
- Participant voice alongside statistical evidence

**Key Complexity**: Must extract from BOTH strands and evaluate integration quality

---

## MIXED METHODS DESIGNS

| Design | Notation | Timing | Priority | Integration Point |
|--------|----------|--------|----------|-------------------|
| **Convergent** | QUAN + QUAL | Concurrent | Equal | Interpretation |
| **Explanatory Sequential** | QUAN → qual | Sequential | Quantitative | After quan results |
| **Exploratory Sequential** | QUAL → quan | Sequential | Qualitative | Instrument/theory dev |
| **Embedded** | QUAN(qual) or QUAL(quan) | Concurrent | One dominant | Within design |
| **Multiphase** | Multiple iterations | Iterative | Varies | Throughout program |

---

## WHAT THIS TEMPLATE CAN ANSWER

| Category | Coverage | Notes |
|----------|----------|-------|
| Statistical Effects | FROM QUAN | Effect sizes, correlations |
| Process/Mechanism | FROM QUAL | How/why patterns occur |
| Convergence | UNIQUE | Do strands agree? |
| Contextual Understanding | FROM QUAL | Meaning, experience |
| Generalization | FROM QUAN | Statistical inference |

---

## HUMAN-READABLE OUTPUT STRUCTURE

### 1. MIXED METHODS DESIGN

```
## Study Design

### Design Type

| Element | Value |
|---------|-------|
| Design type | Convergent / Explanatory / Exploratory / Embedded / Multiphase |
| Notation | QUAN + QUAL / QUAN → qual / QUAL → quan / etc. |
| Timing | Concurrent / Sequential |
| Priority | Equal / Quantitative / Qualitative |
| Integration point | Design / Methods / Interpretation / Reporting |

### Rationale for Mixed Methods

**Why both approaches?**
| Strand | Purpose |
|--------|---------|
| Quantitative | [What quan strand contributes] |
| Qualitative | [What qual strand contributes] |
| Integration | [What integration achieves beyond either alone] |
```

### 2. QUANTITATIVE STRAND

```
## Quantitative Strand

### Design

| Element | Value |
|---------|-------|
| Design type | RCT / Quasi-exp / Survey / Correlational |
| Sample N | |
| Sampling | Random / Convenience / Purposive |

### Measures

| Variable | Measure | Reliability |
|----------|---------|-------------|
| IV | | |
| DV | | α = |
| Covariates | | |

### Results

| Analysis | Result | Effect Size [95% CI] |
|----------|--------|---------------------|
| | | |

### Quan Conclusions

- [Key quantitative findings]
```

### 3. QUALITATIVE STRAND

```
## Qualitative Strand

### Design

| Element | Value |
|---------|-------|
| Tradition | Phenomenology / Grounded theory / Ethnographic / Thematic |
| Sample N | |
| Sampling | Purposive / Theoretical / Snowball |
| Data collection | Interviews / Focus groups / Observations |

### Analysis

| Approach | Software |
|----------|----------|
| [Thematic / Content / etc.] | [NVivo / etc.] |

### Themes

| Theme | Description | Prevalence |
|-------|-------------|------------|
| | | All / Most / Some participants |

### Qual Conclusions

- [Key qualitative findings]
```

### 4. INTEGRATION

```
## Integration of Strands

### Integration Strategy

| Element | Value |
|---------|-------|
| Mixing point | [Where integration occurred] |
| Integration technique | Joint display / Data transformation / Narrative weaving |

### Joint Display

| Quantitative Finding | Qualitative Finding | Integration |
|---------------------|---------------------|-------------|
| [Quan result] | [Qual theme] | Converge / Diverge / Expand |

### Convergence Assessment

| Aspect | Quan | Qual | Agreement |
|--------|------|------|-----------|
| [Finding 1] | [Quan evidence] | [Qual evidence] | Yes / No / Partial |

### Meta-Inferences

**What integration reveals beyond either strand**:
1. [Meta-inference 1]
2. [Meta-inference 2]

### Divergence (if any)

| Divergent Finding | Possible Explanation | Resolution |
|-------------------|---------------------|------------|
| | | |
```

### 5. OVERALL CONCLUSIONS

```
## Conclusions

### Integrated Findings

| Finding | Evidence Type | Confidence |
|---------|--------------|------------|
| | Quan only / Qual only / Convergent | |

### Causal Claims

| Claim | Quan Support | Qual Support | Combined Causal Level |
|-------|-------------|-------------|----------------------|
| | [Effect?] | [Mechanism?] | association / intervention |

### Limitations

| Strand | Limitation |
|--------|------------|
| Quantitative | |
| Qualitative | |
| Integration | |
```

---

## RULE CONVERSION

Mixed methods produce rules from BOTH strands. Key decisions:
1. Extract from each strand separately
2. Assess convergence
3. Upgrade confidence if convergent
4. Note divergence as uncertainty

### Causal Level

The combined causal level is determined by the STRONGER strand:

| Quan Design | Qual Contribution | Combined Level |
|-------------|------------------|----------------|
| RCT | Mechanism explanation | `intervention` (strengthened) |
| Survey | Experience description | `association` |
| Quasi-exp | Context understanding | `intervention` (with caveats) |

### Integration-Based Confidence Adjustment

| Convergence | Adjustment | Rationale |
|-------------|------------|-----------|
| Full convergence | +0.15 | Triangulation strengthens |
| Partial convergence | +0.05 | Some support |
| Divergence | -0.10 | Uncertainty increased |
| Divergence explained | +0.00 | Understood boundary |

### Rule Template

```yaml
rules:
  # Rule from quantitative strand
  - rule_id: "[author]_mm_[year]_quan"
    rule_type: "edge"

    lhs:
      - var: "[IV]"
        state: "[state]"
    rhs:
      - var: "[DV]"
        state: "[state]"
    polarity: "positive|negative"

    strength:
      kind: "effect_size"
      type: "d"
      value:
      ci95: []

    # v2 panel additions
    causal_level: "[from quan design]"
    argument_scheme: "causal_argument"
    extraction_difficulty: "moderate"
    source_zone: "results"

    # Mixed methods metadata
    mm_strand: "quantitative"
    mm_integration:
      convergent_with_qual: true|false
      qual_rule_id: "[link to qual rule]"
      meta_inference: "[what integration adds]"

    ae_confidence: [base + convergence adjustment]

  # Rule from qualitative strand
  - rule_id: "[author]_mm_[year]_qual"
    rule_type: "association"  # Qual typically association

    lhs:
      - var: "[CONTEXT]"
        state: "[observed]"
    rhs:
      - var: "[EXPERIENCE/PROCESS]"
        state: "[observed]"
    polarity: "positive"

    strength:
      kind: "thematic"
      prevalence: "all|most|some"
      n_participants:

    causal_level: "association"
    argument_scheme: "argument_from_position_to_know"  # Participant reports
    extraction_difficulty: "moderate"
    source_zone: "results"

    mm_strand: "qualitative"
    mm_integration:
      convergent_with_quan: true|false
      quan_rule_id: "[link to quan rule]"
      mechanism_provided: true|false

    ae_confidence:

  # Meta-inference rule (from integration)
  - rule_id: "[author]_mm_[year]_meta"
    rule_type: "edge"

    description: "[Insight from integration beyond either strand]"

    # Combines evidence from both strands
    evidence_integration:
      quan_rule: "[quan_rule_id]"
      qual_rule: "[qual_rule_id]"
      integration_technique: "joint_display|transformation|narrative"
      convergence: "full|partial|divergent"

    # Takes causal level from stronger strand
    causal_level: "[higher of the two]"
    argument_scheme: "practical_reasoning"  # Integrative inference

    ae_confidence: [higher due to convergence]
```

### Confidence Scoring

| Factor | Impact | Rationale |
|--------|--------|-----------|
| **Base (quan strand)** | Per design | RCT=0.75, Survey=0.55, etc. |
| **Base (qual strand)** | 0.50 | Interpretive |
| **Convergence bonus** | | |
| Full convergence | +0.15 | Strong triangulation |
| Partial convergence | +0.05 | Some support |
| Divergence | -0.10 | Uncertainty |
| **Integration quality** | | |
| Joint display/rigorous | +0.05 | Transparent integration |
| Narrative only | +0.00 | Weak integration |
| No real integration | -0.10 | Parallel not mixed |
| **Sample adequacy** | | |
| Quan N > 100, Qual N > 15 | +0.05 | Both adequate |
| Either strand weak | -0.05 | Limits integration |

---

## MACHINE-READABLE DATA

```yaml
# ============================================
# HEADER
# ============================================
paper_id: ""
doi: ""
extraction_date: "YYYY-MM-DD"
article_type: "mixed_methods"
source_depth: "full_text|abstract|metadata"

# ============================================
# MIXED METHODS DESIGN
# ============================================
mm_design:
  type: "convergent|explanatory_sequential|exploratory_sequential|embedded|multiphase"
  notation: "QUAN + QUAL|QUAN → qual|QUAL → quan|QUAN(qual)|QUAL(quan)"
  timing: "concurrent|sequential"
  priority: "equal|quantitative|qualitative"
  integration_point: "design|methods|interpretation|reporting"
  rationale:
    quan_purpose: ""
    qual_purpose: ""
    integration_purpose: ""

# ============================================
# QUANTITATIVE STRAND
# ============================================
quan_strand:
  design: "rct|quasi_exp|survey|correlational"
  sample:
    n:
    sampling: "random|convenience|purposive"
  measures:
    - variable: ""
      measure: ""
      reliability:
  analysis:
    - type: ""
      result: ""
      effect_size:
      ci95: []
  conclusions: []

# ============================================
# QUALITATIVE STRAND
# ============================================
qual_strand:
  tradition: "phenomenology|grounded_theory|ethnographic|thematic|content"
  sample:
    n:
    sampling: "purposive|theoretical|snowball"
    saturation_reached: true|false
  data_collection: "interviews|focus_groups|observations|documents"
  analysis:
    approach: ""
    software: ""
  themes:
    - name: ""
      description: ""
      prevalence: "all|most|some"
  conclusions: []

# ============================================
# INTEGRATION
# ============================================
integration:
  technique: "joint_display|data_transformation|narrative_weaving|following_thread"

  joint_display:
    - quan_finding: ""
      qual_finding: ""
      integration: "converge|diverge|expand"

  convergence_assessment:
    - aspect: ""
      quan_evidence: ""
      qual_evidence: ""
      agreement: "yes|no|partial"

  meta_inferences:
    - ""

  divergence:
    - finding: ""
      explanation: ""
      resolution: ""

# ============================================
# CAUSAL ASSESSMENT
# ============================================
causal:
  quan_causal_level: "association|intervention"
  qual_contribution: "mechanism|context|meaning"
  combined_causal_level: "association|intervention"
  mechanism_identified: true|false
  mechanism_description: ""

# ============================================
# RULES GENERATED
# ============================================
rules:
  # Quantitative strand rule
  - rule_id: ""
    rule_type: "edge"
    mm_strand: "quantitative"
    lhs: []
    rhs: []
    polarity: ""
    strength: {}
    causal_level: ""
    argument_scheme: ""
    ae_confidence:
    mm_integration:
      convergent_with_qual:
      qual_rule_id: ""

  # Qualitative strand rule
  - rule_id: ""
    rule_type: "association"
    mm_strand: "qualitative"
    lhs: []
    rhs: []
    polarity: ""
    strength: {}
    causal_level: "association"
    argument_scheme: "argument_from_position_to_know"
    ae_confidence:
    mm_integration:
      convergent_with_quan:
      mechanism_provided:

  # Meta-inference rule
  - rule_id: ""
    rule_type: "edge"
    mm_strand: "integration"
    evidence_integration:
      quan_rule: ""
      qual_rule: ""
      convergence: ""
    causal_level: ""
    ae_confidence:

# ============================================
# QUALITY ASSESSMENT
# ============================================
quality:
  quan_quality: "high|moderate|low"
  qual_quality: "high|moderate|low"
  integration_quality: "high|moderate|low"
  overall_mm_quality: "high|moderate|low"
  our_confidence:

  # Legitimation criteria (Onwuegbuzie & Johnson, 2006)
  legitimation:
    sample_integration: "high|moderate|low"
    inside_outside: "high|moderate|low"
    weakness_minimization: "high|moderate|low"
    sequential: "high|moderate|low|na"
    conversion: "high|moderate|low|na"
    paradigmatic_mixing: "high|moderate|low"
    commensurability: "high|moderate|low"
    multiple_validities: "high|moderate|low"
    political: "high|moderate|low"
```

---

## VALIDATION CHECKLIST

Before finalizing extraction:

- [ ] **Both strands extracted** — Quan AND qual documented
- [ ] **Design type identified** — Convergent/Explanatory/etc.
- [ ] **Integration assessed** — How were strands combined?
- [ ] **Convergence evaluated** — Do strands agree?
- [ ] **Meta-inferences identified** — What does integration add?
- [ ] **Divergence explained** — If strands disagree, why?
- [ ] **Causal level assigned** — From stronger strand
- [ ] **Confidence adjusted** — For convergence/divergence

---

**END OF MIXED METHODS TEMPLATE**
