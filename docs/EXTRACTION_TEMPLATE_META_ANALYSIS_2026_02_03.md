# META-ANALYSIS EXTRACTION TEMPLATE v1.0

**Version**: 1.0.0
**Date**: February 3, 2026
**Derived From**: Complete Requirements Specification (96 questions)
**Panel Review**: Pearl, Cartwright, Simon, Bates, Kaplan

---

## PURPOSE

Meta-analyses provide **aggregated effect estimates** across multiple primary studies. They uniquely contribute:
- Pooled effect sizes with confidence/prediction intervals (`cpd_hint` rules)
- Heterogeneity assessment (bounds on generalizability)
- Moderator analyses (interaction rules)
- Publication bias assessment

---

## WHAT THIS TEMPLATE CAN ANSWER

| Category | Coverage | Notes |
|----------|----------|-------|
| Statistics | POOLED | Best estimates across studies |
| Scope | FROM MODERATORS | Boundary conditions from subgroup analyses |
| Causal Structure | AGGREGATED | Strength of evidence, not new causal claims |
| Conflicts | HETEROGENEITY | I² tells us if findings conflict |
| Temporal/Enabling | IF REPORTED | Only if primary studies reported |

## WHAT THIS TEMPLATE CANNOT ANSWER

- New causal mechanisms (only aggregates existing)
- Individual study details (summarized, not extracted individually)
- Theoretical derivations

---

## HUMAN-READABLE OUTPUT STRUCTURE

When constructing the human-readable extraction document for a **meta-analysis**, follow this structure:

### 1. INTRODUCTION SECTION

**Structure**: Research Question + Why This Synthesis + Scope

```
## Introduction

**Research Question**: [What pooled relationship is being estimated?]

**Why This Synthesis**:
- Gap addressed: [Why aggregate evidence now?]
- Problem: [Conflicting findings / need for precision / moderator identification]
- Prior meta-analyses: [None / superseded / limited scope]

**Scope of Synthesis**:
| Inclusion | Exclusion |
|-----------|-----------|
| [What studies included] | [What studies excluded and why] |

**Terminology Notes**: [How different terms across studies were mapped]
```

### 2. METHODS SECTION

**Structure**: Search → Screening → Coding → Pooling

```
## Methods

### Search Strategy

| Database | Date Range | Records |
|----------|------------|---------|
| PubMed | 2000-2025 | 1,234 |

**Search string**: [Actual search string]

### PRISMA Flow

[Include PRISMA diagram or table]

Identified → Screened → Eligible → Included (k = X studies, N = Y participants)

### Coding Protocol

| Variable | How Coded | Inter-rater Agreement |
|----------|-----------|----------------------|
| Effect size | [Extraction method] | κ = X |

### Pooling Approach

**Model**: Fixed-effects / Random-effects / Both
**Heterogeneity assessment**: I², Q, τ²
**Publication bias**: Egger's test, funnel plot, trim-and-fill
```

### 3. RESULTS SECTION

**Structure**: Overall Effect → Forest Plot → Moderators → Sensitivity

```
## Results

### Overall Pooled Effect

| Metric | Value |
|--------|-------|
| Effect type | d / r / OR |
| Pooled estimate | X.XX |
| 95% CI | [X.XX, X.XX] |
| Prediction interval | [X.XX, X.XX] |
| k studies | X |
| N participants | X,XXX |

**Interpretation**: [Plain-language meaning of pooled effect]

### Forest Plot

[Include forest plot image or ASCII representation]

### Heterogeneity Assessment

| Metric | Value | Interpretation |
|--------|-------|----------------|
| I² | X% | Low/Moderate/High |
| Q | X.XX (p = .XX) | |
| τ² | X.XX | |

**Concern**: [If I² > 50%, note implications for pooled estimate]

### Moderator Analyses

| Moderator | Levels | k | Effect [95% CI] | Q_between (p) |
|-----------|--------|---|-----------------|---------------|
| Setting | Lab | X | X.XX [X.XX, X.XX] | |
| | Field | X | X.XX [X.XX, X.XX] | X.XX (.XX) |

**Key finding**: [Which moderators explained heterogeneity]

### Publication Bias

| Test | Result | Interpretation |
|------|--------|----------------|
| Funnel plot | Symmetric / Asymmetric | |
| Egger's test | p = .XX | Bias / No bias |
| Trim-and-fill | Adjusted ES = X.XX | |
```

### 4. DISCUSSION SECTION

**Structure**: Summary → Moderator Interpretation → Limitations → Implications

```
## Discussion

### Summary of Evidence

**Pooled effect**: [X.XX, 95% CI [X.XX, X.XX]] — [small/medium/large] effect
**Consistency**: [High/Low heterogeneity interpretation]
**Scope**: [What populations/settings the estimate applies to]

### Moderator Interpretation

| Moderator | Finding | Implication for BN |
|-----------|---------|-------------------|
| Setting | Effect stronger in field | Ecological validity matters |

### Homogeneity Assessment (Cartwright Check)

| Dimension | Homogeneous? | If Mixed |
|-----------|--------------|----------|
| Same IV manipulation? | Yes/No/Mixed | [How handled] |
| Same DV measurement? | Yes/No/Mixed | |
| Same population? | Yes/No/Mixed | |
| Lab/field mixed? | Yes/No | [Moderator analysis?] |

**⚠️ If pooling is causally incoherent**: [Flag and recommend moderator-conditional estimates]

### Limitations

| Limitation | Impact | Severity |
|------------|--------|----------|
| Publication bias | [Effect] | Low/Mod/High |
| Study quality variance | [Effect] | Low/Mod/High |
| Heterogeneity | [Effect] | Low/Mod/High |

### Inferential Boundaries

What CANNOT be concluded from this meta-analysis:

1. ❌ [Over-interpretation 1]
2. ❌ [Over-interpretation 2]
3. ❌ [Over-interpretation 3]

### Decision Summary (Simon)

| Element | Value |
|---------|-------|
| Best current estimate | d/r = X.XX [95% CI] |
| Confidence bounds | Prediction interval [X.XX, X.XX] |
| Apply to field settings? | Yes/No/Conditional |
| Key moderators | [List] |
| What would raise estimate | [Conditions] |
| What would lower estimate | [Conditions] |
```

---

## FOREST PLOT GUIDANCE

**If forest plot image is available**:
- Include figure directly
- Caption with: k studies, model type, heterogeneity

**If creating ASCII representation**:

```
Study          Effect [95% CI]
---------------------------------------
Smith 2010     ├──●──┤         0.45 [0.20, 0.70]
Jones 2012       ├───●───┤     0.62 [0.30, 0.94]
Brown 2015    ├●┤               0.15 [-0.05, 0.35]
---------------------------------------
POOLED        ├──◆──┤          0.42 [0.28, 0.56]
              |     |     |     |
              0    0.25  0.5  0.75
```

---

## RULE CONVERSION: FROM META-ANALYSIS TO QUINEAN WEB

Meta-analyses produce **cpd_hint rules** with pooled estimates. They are the strongest source of quantitative strength information but require careful attention to heterogeneity.

### REQUIRED ELEMENTS FOR RULE INCORPORATION

#### 1. Argument Structure (What Warrants Pooled Claims?)

| Element | Required? | Source in Template | If Missing |
|---------|-----------|-------------------|------------|
| **Pooled estimate** | ✅ Required | POOLED ESTIMATES | Cannot create cpd_hint |
| **Heterogeneity assessment** | ✅ Required | POOLING METHODOLOGY | Affects confidence |
| **Publication bias check** | ✅ Required | POOLING METHODOLOGY | Affects confidence |
| **Homogeneity assessment** | ✅ Required | HOMOGENEITY section | May invalidate pooling |
| **k studies** | ✅ Required | POOLED ESTIMATES | Affects weight |
| **Total N** | ✅ Required | POOLED ESTIMATES | Affects precision |

**Meta-Analysis Argument Structure**:
```yaml
argument:
  claim: "Pooled effect of [IV] on [DV] is [estimate]"
  warrant_type: "quantitative_synthesis"
  premises:
    - "Primary studies measured same construct"
    - "Studies are exchangeable (random effects assumption)"
    - "Publication bias is minimal or corrected"
  backing:
    - "k = [N] studies"
    - "I² = [X]% (heterogeneity)"
    - "Egger's p = [X] (bias)"
  qualifier: "Conditional on moderators: [list]"
  rebuttal: "High heterogeneity suggests pooling may be incoherent"
```

#### 2. Interrogative Structure (What Questions Does MA Answer?)

| Question | MA Can Answer | Conditions |
|----------|---------------|------------|
| "What is the effect size?" | ✅ Yes | Primary purpose |
| "How precise is the estimate?" | ✅ Yes | From CI |
| "How variable across studies?" | ✅ Yes | From I², prediction interval |
| "What moderates the effect?" | ✅ If analyzed | Moderator analysis needed |
| "Is the effect causal?" | ⚠️ Depends | On designs of included studies |
| "What's the mechanism?" | ❌ No | MA doesn't establish mechanism |

```yaml
interrogative_completeness:
  # MA answers these
  what_pooled_effect: true
  what_precision: true
  what_heterogeneity: true
  what_moderators: true|false  # If analyzed

  # MA answers these CONDITIONALLY
  what_causal_direction: "only_if_all_rcts|mixed|correlational"

  # MA CANNOT answer these
  what_mechanism: false
  what_enables_effect: false  # Unless synthesized from primaries
```

#### 3. Coherence Requirements (Cartwright Homogeneity Check)

**CRITICAL**: Before pooling enters web, verify studies are causally coherent:

```yaml
homogeneity_check:
  # Must ALL be true for valid pooling
  same_iv_construct: true|false
  same_dv_construct: true|false
  same_causal_mechanism_assumed: true|false

  # If any are false, pooled estimate may be meaningless
  if_heterogeneous:
    action: "extract_moderator_conditional_estimates"
    warning: "Pooled estimate causally incoherent"
```

#### 4. Heterogeneity Interpretation

| I² Value | Interpretation | Rule Creation |
|----------|----------------|---------------|
| <25% | Low | Create single cpd_hint |
| 25-75% | Moderate | Create cpd_hint with wide uncertainty |
| >75% | High | Create CONDITIONAL rules by moderator |

---

### RULE TYPE DECISION TREE FOR META-ANALYSIS

```
                    ┌─────────────────────────────┐
                    │   What is heterogeneity?    │
                    └──────────────┬──────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         │                         │                         │
         ▼                         ▼                         ▼
   ┌───────────┐            ┌───────────┐            ┌───────────┐
   │ I² < 25%  │            │ I² 25-75% │            │ I² > 75%  │
   │ (low)     │            │ (moderate)│            │ (high)    │
   └─────┬─────┘            └─────┬─────┘            └─────┬─────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Single CPD_HINT │    │ CPD_HINT with   │    │ CONDITIONAL     │
│ rule            │    │ prediction      │    │ rules by        │
│                 │    │ interval        │    │ moderator       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                      │
                                              ┌───────┴───────┐
                                              │ Moderator     │
                                              │ analysis done?│
                                              └───────┬───────┘
                                         Yes ─────────┼───────── No
                                              │               │
                                              ▼               ▼
                                    ┌───────────┐   ┌───────────┐
                                    │ INTERACTION│   │ CONSTRAINT│
                                    │ rules by  │   │ rule:     │
                                    │ moderator │   │ "pooling  │
                                    └───────────┘   │ invalid"  │
                                                    └───────────┘
```

---

### COMPLETE CONVERSION EXAMPLES

**Example 1: Low Heterogeneity → Single CPD_HINT Rule**

*Extracted data*:
```yaml
pooled_estimate:
  effect_type: "d"
  value: 0.48
  ci95: [0.35, 0.61]
  prediction_interval: [0.22, 0.74]
  k_studies: 28
  n_participants: 3450

heterogeneity:
  I2: 18%
  interpretation: "low"

publication_bias:
  egger_p: 0.32
  funnel: "symmetric"

homogeneity_check:
  same_iv_type: true
  same_dv_type: true
  same_population: true
  ecological_validity_mixed: false  # All field studies
```

*Converted to rule*:
```yaml
rules:
  - rule_id: "chen_ma_2024_overall"
    rule_type: "cpd_hint"

    lhs:
      - var: "ENV_NATURE_EXPOSURE"
        state: "present"
        canonical_id: "ENV_NATURE_ANY"
    rhs:
      - var: "OUT_STRESS"
        state: "decreased"
        canonical_id: "OUT_STRESS_SELF_REPORT"
    polarity: "negative"

    # POOLED STRENGTH (unique to MA)
    strength:
      kind: "pooled_effect"
      type: "d"
      value: 0.48
      ci95: [0.35, 0.61]
      prediction_interval: [0.22, 0.74]  # Critical for BN
      k_studies: 28
      n_total: 3450
      heterogeneity:
        I2: 0.18
        interpretation: "low"
        pooling_valid: true

    # Causal warrant aggregated
    causal:
      direction: "FORWARD"
      warrant: "aggregated_from_primaries"
      n_rcts: 15
      n_observational: 13
      causal_strength: "moderate"  # Mixed designs

    # Scope from inclusion criteria
    applicability:
      population: ["adults"]  # From inclusion
      setting: ["field_natural"]  # From homogeneity check
      scope_specified: true
      derived_from: "inclusion_criteria"

    # Ecological validity synthesized
    ecological_validity: "FIELD_NATURAL"
    ecological_validity_mixed: false

    # Publication bias assessment
    publication_bias:
      assessed: true
      detected: false
      correction_applied: false

    # Coherence
    coherence:
      supports_theories: ["ART", "SRT"]
      aggregates_k_studies: 28
      updates_prior_with: "precision"

    # Questions answered
    questions_answered:
      - "S.1"   # Effect size
      - "S.2"   # Confidence interval
      - "S.3"   # Prediction interval
      - "S.5"   # Heterogeneity
      - "SC.1"  # Population scope

    ae_confidence: 0.85  # High due to k=28, low I²
```

**Example 2: High Heterogeneity → Conditional Rules by Moderator**

*Extracted data*:
```yaml
pooled_estimate:
  effect_type: "d"
  value: 0.42
  ci95: [0.18, 0.66]
  k_studies: 35

heterogeneity:
  I2: 78%
  interpretation: "high"

moderator_analysis:
  - moderator: "setting"
    significant: true
    p_interaction: 0.003
    levels:
      - level: "field"
        k: 18
        effect: 0.61
        ci95: [0.42, 0.80]
      - level: "lab"
        k: 17
        effect: 0.23
        ci95: [0.05, 0.41]
```

*Converted to rules*:
```yaml
rules:
  # DO NOT create single pooled rule (heterogeneity too high)

  # Instead: Conditional rule for FIELD studies
  - rule_id: "wong_ma_2024_field"
    rule_type: "cpd_hint"

    lhs:
      - var: "ENV_NATURE"
        state: "exposed"
    rhs:
      - var: "OUT_RESTORATION"
        state: "increased"
    polarity: "positive"

    strength:
      kind: "pooled_effect_conditional"
      type: "d"
      value: 0.61
      ci95: [0.42, 0.80]
      k_studies: 18
      conditional_on:
        moderator: "ecological_validity"
        level: "FIELD"

    applicability:
      setting: ["field_natural", "field_structured"]
      scope_specified: true
      moderator_derived: true

    ecological_validity: "FIELD_NATURAL"

    ae_confidence: 0.80

  # Conditional rule for LAB studies
  - rule_id: "wong_ma_2024_lab"
    rule_type: "cpd_hint"

    lhs:
      - var: "ENV_NATURE"
        state: "exposed"
    rhs:
      - var: "OUT_RESTORATION"
        state: "increased"
    polarity: "positive"

    strength:
      kind: "pooled_effect_conditional"
      type: "d"
      value: 0.23
      ci95: [0.05, 0.41]
      k_studies: 17
      conditional_on:
        moderator: "ecological_validity"
        level: "LAB"

    applicability:
      setting: ["lab_vr", "lab_video", "lab_photos"]
      scope_specified: true
      moderator_derived: true

    ecological_validity: "LAB_MIXED"

    # Bridge warrant needed for lab→field transfer
    bridge:
      required_for_field_application: true
      bridge_type: "FUNCTIONAL"
      transfer_discount: 0.35  # Lab findings discounted

    ae_confidence: 0.65  # Lower due to lab validity

  # INTERACTION rule capturing moderator
  - rule_id: "wong_ma_2024_mod"
    rule_type: "interaction"

    lhs:
      - var: "ENV_NATURE"
        state: "exposed"
      - var: "MOD_SETTING"
        state: "field"
    rhs:
      - var: "OUT_RESTORATION"
        state: "large_increase"
    polarity: "positive"

    strength:
      kind: "moderator_interaction"
      moderator_effect: 0.38  # field - lab difference
      p_interaction: 0.003

    ae_confidence: 0.75
```

**Example 3: Publication Bias Detected → Adjusted Rule**

```yaml
rules:
  - rule_id: "kim_ma_2024_adjusted"
    rule_type: "cpd_hint"

    lhs:
      - var: "ENV_GREENSPACE"
        state: "high_access"
    rhs:
      - var: "OUT_MENTAL_HEALTH"
        state: "improved"
    polarity: "positive"

    strength:
      kind: "pooled_effect"
      type: "d"

      # BOTH estimates provided
      unadjusted:
        value: 0.52
        ci95: [0.38, 0.66]
      adjusted:  # After trim-and-fill
        value: 0.38
        ci95: [0.22, 0.54]
        adjustment_method: "trim_and_fill"
        n_imputed: 4

      # Use adjusted for BN
      value: 0.38  # Adjusted estimate
      ci95: [0.22, 0.54]

    publication_bias:
      detected: true
      egger_p: 0.02
      funnel_asymmetry: "moderate"
      correction_applied: true
      correction_impact: "reduced_effect_by_27%"

    ae_confidence: 0.68  # Reduced due to bias
```

---

### CONFIDENCE SCORING FOR META-ANALYSES

| Factor | Impact | Rationale |
|--------|--------|-----------|
| **k studies** | | |
| k > 20 | +0.10 | Robust synthesis |
| k = 10-20 | +0.05 | Adequate |
| k < 10 | -0.05 | Limited |
| **Heterogeneity** | | |
| I² < 25% | +0.10 | Pooling valid |
| I² 25-50% | 0 | Neutral |
| I² 50-75% | -0.10 | Concerning |
| I² > 75% | -0.20 | Pooling questionable |
| **Publication bias** | | |
| None detected | +0.05 | Clean synthesis |
| Detected & corrected | -0.05 | Uncertainty added |
| Detected & uncorrected | -0.15 | Estimate biased |
| **Homogeneity (Cartwright)** | | |
| All same IV type | +0.05 | Causally coherent |
| Mixed IV types | -0.10 | May be apples/oranges |
| Lab/field mixed (no moderator) | -0.15 | Ecological validity unclear |

**Base confidence**: 0.75 for meta-analysis
**Range**: 0.50 (weak MA) to 0.90 (excellent MA)

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
| Article type | META-ANALYSIS |
| Source depth | [ ] Full text [ ] Abstract only [ ] Metadata only |

---

## OUR SUMMARY

- Plain-language summary of pooled findings (1-3 sentences)
- Key effect size and confidence interval
- Main moderators identified

---

## RESEARCH QUESTION

**Q.RQ.1: What is the primary research question?**

**Q.RQ.2: What gap does this meta-analysis address?**

**Q.RQ.3: Why now?** (sufficient primary studies accumulated, conflicting findings to resolve, etc.)

---

## SEARCH & INCLUSION

### Search Protocol

**Q: What databases were searched?**
| Database | Date Range |
|----------|------------|
| | |

**Q: What was the search string?**
```
[Search string]
```

**Q: Was grey literature included?**
[ ] Yes [ ] No

### PRISMA Flow

| Stage | N |
|-------|---|
| Records identified | |
| Duplicates removed | |
| Records screened | |
| Full-text assessed | |
| Studies included | |

**Q: What were the exclusion criteria?** *(These define scope boundaries - Bates)*

| Exclusion Criterion | N Excluded | Implication for Scope |
|---------------------|------------|----------------------|
| | | |

### Terminology Harmonization *(Bates)*

**Q: How were different terms across studies mapped?**

| Original Term (Study) | Canonical ID | Studies Using |
|-----------------------|--------------|---------------|
| | | |

---

## POOLING METHODOLOGY

**Q.PM.1: What model was used?**
[ ] Fixed effects [ ] Random effects [ ] Both reported

**Q.PM.2: What is the heterogeneity?**

| Metric | Value | Interpretation |
|--------|-------|----------------|
| I² | | Low (<25%) / Moderate (25-75%) / High (>75%) |
| Q | | |
| τ² | | |
| p (heterogeneity) | | |

**Q.PM.3: Was publication bias assessed?**

| Test | Result | Interpretation |
|------|--------|----------------|
| Egger's test p | | |
| Funnel plot | Symmetric / Asymmetric | |
| Trim-and-fill adjustment | | |

---

## HOMOGENEITY ASSESSMENT *(Cartwright)*

**Q: Are pooled studies homogeneous on key dimensions?**

| Dimension | Status | If Mixed, How Handled? |
|-----------|--------|------------------------|
| Same IV manipulation type? | Yes / No / Mixed | |
| Same DV measurement method? | Yes / No / Mixed | |
| Same population type? | Yes / No / Mixed | |
| Same temporal parameters? | Yes / No / Mixed | |
| Ecological validity mixed? (lab/field) | Yes / No | *(Kaplan: critical check)* |
| Nature type distinguished? | Yes / No | *(Kaplan: urban park vs wilderness)* |

**If I² > 75% or homogeneity = "Mixed":**
> ⚠️ Pooled estimate may be causally incoherent. Extract moderator-conditional estimates instead.

---

## POOLED ESTIMATES

### Overall Effect

| Metric | Value |
|--------|-------|
| Effect type | d / r / OR / RR / SMD |
| Pooled estimate | |
| 95% CI | [ , ] |
| Prediction interval | [ , ] *(if random effects)* |
| N studies | |
| Total N participants | |

### Interpretation Box

> **Plain-language meaning**: [What this pooled effect means]

### Concern Box *(if heterogeneity high)*

> **Concern**: High heterogeneity (I² = X%) suggests moderators operating
> **Impact**: Pooled estimate may not apply uniformly

---

## MODERATOR ANALYSES

**Q: What moderators were tested?**

| Moderator | Tested? | Significant? | Effect by Level |
|-----------|---------|--------------|-----------------|
| | Yes/No | Yes/No/p=X | |

**Q: What moderators were significant?**

| Moderator | Levels | Effect at Each Level | p (interaction) |
|-----------|--------|---------------------|-----------------|
| | | | |

---

## SCOPE CONDITIONS *(Derived from moderators)*

| Scope Dimension | Value | Source |
|-----------------|-------|--------|
| Population | | From moderator analysis / inclusion criteria |
| Setting | | |
| Duration | | |
| Measurement type | | |

**Q.SC.5: Is scope explicitly specified?**
[ ] Yes - from moderator analysis [ ] No - assumed from pooling

---

## ECOLOGICAL VALIDITY *(Kaplan)*

**Q: How was ecological validity handled?**

| Check | Status |
|-------|--------|
| Lab/field studies pooled together? | Yes / No |
| If yes, moderator analysis by setting? | Yes / No |
| VR/Video/Photos distinguished? | Yes / No |
| Stimulus heterogeneity addressed? | Yes / No |

**Ecological Validity Assessment**:
[ ] All field studies → FIELD validity
[ ] All lab studies → LAB validity (specify: VR/Video/Photos)
[ ] Mixed without moderator analysis → VALIDITY UNCLEAR
[ ] Mixed with moderator analysis → CONDITIONAL validity

---

## TEMPORAL DYNAMICS *(If reported across studies)*

| Parameter | Pooled Estimate | N Studies Reporting |
|-----------|-----------------|---------------------|
| Onset latency | | |
| Minimum duration | | |
| Effect persistence | | |
| Dose-response | | |

---

## CAUSAL STRUCTURE

**Q.CS.1: What causal direction is supported by the pooled evidence?**

| Element | Assessment |
|---------|------------|
| Direction | FORWARD / CORRELATIONAL / MIXED |
| Strength of causal evidence | Based on designs of included studies |
| N RCTs included | |
| N observational included | |

**Q: Does pooling strengthen or weaken causal inference?**
- If all RCTs: Strengthens (aggregated experimental evidence)
- If mixed designs: Depends on moderator analysis by design
- If all observational: Remains correlational despite pooling

---

## BRIDGE WARRANT SIGNALS

**Q.BW: Does this meta-analysis pool across domains?**

| Element | Value |
|---------|-------|
| Source domain(s) | |
| Target domain | |
| Cross-domain pooling? | Yes / No |
| If yes, bridge type implied | MECHANISM / FUNCTIONAL / ANALOGICAL |

---

## CONFLICT ASSESSMENT

**Q: Does heterogeneity indicate conflicts in the literature?**

| Assessment | Value |
|------------|-------|
| I² interpretation | Low = consistent / High = conflicting |
| Conflict type | SCOPE_BOUNDARY / METHODOLOGICAL_DIVERGENCE / GENUINE |
| Resolution | Via moderator analysis / Unresolved |

---

## AUTHORS' CONCLUSIONS

**Q: What do authors conclude from pooled evidence?**

| Claim # | Conclusion | Supported by Data? |
|---------|------------|-------------------|
| 1 | | Yes / Partially / Overstated |

**Q: Do conclusions exceed what pooling warrants?**
- [ ] Conclusions match pooled estimate
- [ ] Conclusions overstate certainty (ignore heterogeneity)
- [ ] Conclusions appropriately hedged

---

## OUR ASSESSMENT

**Strengths**
- [What this meta-analysis does well]

**Limitations**
- [Methodological concerns]

**Confidence in pooled estimate**:
[ ] High (low heterogeneity, no pub bias, homogeneous studies)
[ ] Moderate (some heterogeneity, addressed via moderators)
[ ] Low (high heterogeneity, pub bias, mixed study types)

---

## DECISION SUMMARY *(Simon)*

| Element | Value |
|---------|-------|
| Best current estimate | d/r = X [CI] |
| Confidence bounds | Prediction interval if available |
| Key moderators | |
| What would raise estimate | |
| What would lower estimate | |
| Gaps for future research | |

---

## Q&A SECTION

**Q: What is the pooled effect?**
A:

**Q: How confident should we be?**
A: [Based on heterogeneity and bias assessment]

**Q: Does this apply to all populations?**
A: [Based on moderator analysis]

**Q: Does this apply to field settings?**
A: [Based on ecological validity assessment]

**Q: What are the key moderators?**
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
article_type: "meta_analysis"
source_depth: "full_text|abstract|metadata"

# ============================================
# QUESTIONS ANSWERED
# ============================================
questions:
  # Identification
  ID.1_citation: ""
  ID.2_article_type: "meta_analysis"
  ID.3_source_depth: ""

  # Research Question
  RQ.1_primary_question: ""
  RQ.2_gap_addressed: ""
  RQ.3_timeliness: ""

  # Search & Inclusion
  search:
    databases: []
    date_range: {start: "", end: ""}
    search_string: ""
    grey_literature: true|false

  prisma:
    n_identified:
    n_screened:
    n_eligible:
    n_included:
    exclusion_reasons: []

  # Terminology Harmonization (Bates)
  terminology_mapping:
    - original_term: ""
      canonical_id: ""
      studies: []

# ============================================
# POOLING
# ============================================
pooling:
  model: "fixed|random"

  heterogeneity:
    I2:
    I2_interpretation: "low|moderate|high"
    Q:
    tau2:
    p_heterogeneity:

  publication_bias:
    egger_p:
    funnel_asymmetry: "none|mild|severe"
    trim_fill_adjustment:

# ============================================
# HOMOGENEITY ASSESSMENT (Cartwright)
# ============================================
homogeneity:
  same_iv_type: "yes|no|mixed"
  same_dv_type: "yes|no|mixed"
  same_population: "yes|no|mixed"
  same_temporal: "yes|no|mixed"
  ecological_validity_mixed: true|false
  nature_type_distinguished: true|false

# ============================================
# POOLED ESTIMATES
# ============================================
estimates:
  overall:
    effect_type: "d|r|OR|RR|SMD"
    value:
    ci95: [, ]
    prediction_interval: [, ]
    n_studies:
    n_participants:

  by_moderator:
    - moderator: ""
      levels:
        - level: ""
          effect:
          ci95: [, ]
          n_studies:

# ============================================
# MODERATORS
# ============================================
moderators:
  tested: []
  significant: []
  effects_by_level: {}

# ============================================
# SCOPE (Derived)
# ============================================
scope:
  population: ""
  setting: ""
  duration: ""
  measurement: ""
  scope_specified: true|false
  derived_from: "moderator_analysis|inclusion_criteria|assumed"

# ============================================
# ECOLOGICAL VALIDITY (Kaplan)
# ============================================
ecological_validity:
  level: "FIELD|LAB_VR|LAB_VIDEO|LAB_PHOTOS|MIXED|UNCLEAR"
  lab_field_mixed: true|false
  moderator_by_setting: true|false
  stimulus_heterogeneity_addressed: true|false

# ============================================
# CAUSAL STRUCTURE
# ============================================
causal:
  direction: "FORWARD|CORRELATIONAL|MIXED"
  n_rcts:
  n_observational:
  causal_strength: "strong|moderate|weak"

# ============================================
# BRIDGE
# ============================================
bridge:
  cross_domain_pooling: true|false
  source_domains: []
  target_domain: ""
  bridge_type: "MECHANISM|FUNCTIONAL|ANALOGICAL|NONE"

# ============================================
# CONFLICTS
# ============================================
conflicts:
  heterogeneity_indicates_conflict: true|false
  conflict_type: "SCOPE_BOUNDARY|METHODOLOGICAL_DIVERGENCE|GENUINE|NONE"
  resolution: ""

# ============================================
# DECISION SUMMARY (Simon)
# ============================================
decision_summary:
  best_estimate:
  confidence_bounds: [, ]
  key_moderators: []
  what_would_raise: ""
  what_would_lower: ""

# ============================================
# RULES GENERATED
# ============================================
rules:
  - rule_id: ""
    rule_type: "cpd_hint"  # Primary output of meta-analysis
    lhs:
      - var: ""
        state: ""
    rhs:
      - var: ""
        state: ""
    polarity: "positive|negative|null|u_shaped"
    strength:
      kind: "pooled_effect"
      type: "d|r|OR"
      value:
      ci95: [, ]
      prediction_interval: [, ]
      heterogeneity_I2:
    applicability:
      population: []
      setting: []
      boundary_conditions: []
      conditional_on_moderator: []
    ae_confidence:

# ============================================
# QUALITY ASSESSMENT
# ============================================
quality:
  cochrane_rob: ""
  grade_certainty: "high|moderate|low|very_low"
  our_confidence:
```

---

**END OF META-ANALYSIS TEMPLATE**
