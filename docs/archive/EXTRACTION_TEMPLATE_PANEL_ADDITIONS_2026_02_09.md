# EXTRACTION TEMPLATE PANEL ADDITIONS v1.0

**Version**: 1.0.0
**Date**: February 9, 2026
**Status**: APPROVED by Panel (2026-02-08)
**Applies to**: All extraction templates (Empirical, Meta-Analysis, Systematic Review, etc.)

---

## OVERVIEW

This document specifies additions to extraction templates based on expert panel consultation (2026-02-08). These fields extend the existing ae.claim.v1 and ae.rule.v1 schemas to v2.

**Panel Members**:
- Walton (argumentation theory)
- Pearl (causal inference)
- Lipton (explanation theory)
- Cartwright (philosophy of science)
- Hearst (NLP/extraction)
- Teufel (scientific discourse structure)
- R. Kaplan (environmental psychology domain)

---

## NEW REQUIRED FIELDS

### 1. CAUSAL LEVEL (Pearl)

**Location in template**: CAUSAL STRUCTURE section
**Schema field**: `causal_level`
**Required**: Yes for all empirical claims

```yaml
causal:
  causal_level: "association|intervention|counterfactual"
  # Pearl's Ladder of Causation (Book of Why, 2018)
```

| Level | Definition | Typical Evidence | Inference Strength |
|-------|------------|------------------|-------------------|
| **association** | Observational correlation P(Y\|X) | Cross-sectional survey, correlational study | Weak |
| **intervention** | Experimental manipulation P(Y\|do(X)) | RCT, controlled experiment | Moderate |
| **counterfactual** | What-if reasoning P(Y_x\|X', Y') | Natural experiments, twin studies, theoretical derivation | Strong (if valid) |

**Decision rules**:
- RCT with proper randomization → `intervention`
- Quasi-experiment with matched controls → `intervention` (downgrade confidence)
- Cross-sectional survey → `association`
- Longitudinal with temporal precedence → `association` (can support causal inference with caveats)
- Theoretical paper proposing mechanism → `counterfactual` (tentative)

### 2. ARGUMENT SCHEME (Walton)

**Location in template**: ARGUMENT STRUCTURE section
**Schema fields**: `argument_scheme`, `critical_questions`
**Required**: Yes for all claims

```yaml
argument:
  argument_scheme: "causal_argument|argument_from_expert_opinion|argument_from_analogy|..."
  critical_questions:
    - "[Question 1 from scheme]"
    - "[Question 2 from scheme]"
  critical_questions_addressed:
    - "Q1: [How addressed in paper]"
    - "Q2: [How addressed in paper]"
  critical_questions_unaddressed:
    - "Q3: [Not addressed - weakness]"
```

**Common schemes for empirical research**:

| Article Type | Typical Scheme | Key Critical Questions |
|--------------|----------------|----------------------|
| RCT | `causal_argument` | Was randomization proper? Were there confounds? |
| Correlational | `argument_from_correlation_to_cause` | Is there a third factor? Is temporal order correct? |
| Meta-analysis | `argument_from_expert_opinion` (synthesis) | Are included studies homogeneous? Publication bias? |
| Qualitative | `argument_from_position_to_know` | Was participant truthful? In position to know? |
| Theoretical | `practical_reasoning` | Are there other ways? Side effects? |

**Reference**: See `contracts/vocab/argument_schemes.json` for full scheme definitions.

### 3. CONTRAST CLASS (Lipton)

**Location in template**: RESEARCH QUESTION section (new subsection)
**Schema fields**: `contrast_class`, `difference_maker`
**Required**: Yes for explanatory claims

```yaml
explanation:
  contrast_class: "[The foil - 'why X rather than Y?']"
  difference_maker: "[What makes the difference between fact and foil]"

  # Examples:
  # "Why do people in green spaces report lower stress RATHER THAN the same stress as urban settings?"
  # Difference maker: "Presence of vegetation provides attention restoration"
```

**Why this matters** (Lipton, 1991):
- Explanations are always relative to a contrast class
- "Why X?" is incomplete; we need "Why X rather than Y?"
- The contrast class determines what counts as a satisfactory explanation
- Different contrast classes may require different mechanisms

**Extraction guidance**:

| Paper Section | Look for |
|---------------|----------|
| Introduction | "Unlike...", "In contrast to...", "Rather than..." |
| Hypotheses | The control condition defines the contrast |
| Discussion | "What distinguishes our findings from..." |

### 4. EXTRACTION METADATA (Hearst/Teufel)

**Location in template**: Each claim/finding
**Schema fields**: `extraction_difficulty`, `source_zone`
**Required**: Yes for extraction audit trail

```yaml
extraction_meta:
  extraction_difficulty: "easy|moderate|hard"
  source_zone: "abstract|introduction|methods|results|discussion|conclusion|table|figure"
  confidence_calibration: "[Adjust based on difficulty]"
```

**Difficulty classification**:

| Difficulty | Criteria | Confidence Adjustment |
|------------|----------|----------------------|
| **easy** | Explicit statement, clear statistics, standard format | None |
| **moderate** | Implicit claim, requires inference, scattered evidence | -0.10 |
| **hard** | Ambiguous language, conflicting statements, missing data | -0.20 |

**Source zone reliability** (Teufel's scientific discourse structure):

| Zone | Claim Type Typically Found | Reliability for Facts |
|------|---------------------------|----------------------|
| **abstract** | Summary claims, key findings | High (vetted) |
| **introduction** | Background, prior work | Low (not this paper's contribution) |
| **methods** | Procedural facts | High |
| **results** | Empirical findings | Highest |
| **discussion** | Interpretations, speculations | Moderate (opinion element) |
| **conclusion** | Summary, implications | Moderate |
| **table** | Quantitative data | Highest |
| **figure** | Visual data | High |

---

## INTEGRATION WITH EXISTING TEMPLATES

### For EMPIRICAL TEMPLATE (RCT, Quasi-Exp, Cross-Sectional)

Add to **CAUSAL STRUCTURE** section:

```yaml
## CAUSAL STRUCTURE (EXTENDED)

### Causal Level Classification (Pearl)

| Element | Classification |
|---------|---------------|
| **Study design** | RCT / Quasi-exp / Correlational / Observational |
| **Causal level** | intervention / association / counterfactual |
| **Justification** | [Why this level?] |
| **Upgrade possible?** | [What additional evidence would permit higher level?] |

### Argument Scheme (Walton)

**Primary scheme**: [e.g., causal_argument]

**Critical questions**:
| # | Question | Addressed? | Evidence |
|---|----------|------------|----------|
| 1 | [Q1 from scheme] | Yes/No/Partial | [Citation/section] |
| 2 | [Q2 from scheme] | Yes/No/Partial | [Citation/section] |

**Unaddressed questions weaken confidence by**: [0.05-0.15 per question]

### Contrast Class (Lipton)

**Implicit contrast**: "[What is the foil?]"
**Difference maker**: "[What causes the difference?]"
**Contrast transferable?**: Yes/No — [If no, scope conditions affected]
```

### For META-ANALYSIS TEMPLATE

Add to **SYNTHESIS ASSESSMENT** section:

```yaml
### Causal Level of Pooled Estimate

| Element | Value |
|---------|-------|
| **Predominant study design** | [Most common design in pool] |
| **Pooled causal level** | [Lowest common level across studies] |
| **Heterogeneity in levels** | Low/Moderate/High |

Note: Pooled estimate inherits the LOWEST causal level among included studies.
Exception: If all RCTs, pooled estimate is intervention level.

### Argument Scheme for Synthesis

**Primary scheme**: argument_from_expert_opinion (synthesis)

**Critical questions**:
| # | Question | Addressed? |
|---|----------|------------|
| 1 | Are included studies homogeneous? | [I² = X%] |
| 2 | Is there publication bias? | [Funnel plot, trim-fill] |
| 3 | Are studies comparable in scope? | [Population/setting variation] |
| 4 | Is synthesis methodology transparent? | [PRISMA compliance] |
```

### For THEORETICAL TEMPLATE

Add to **DERIVATION STRUCTURE** section:

```yaml
### Causal Level of Proposed Relationships

| Proposed Edge | Causal Level | Status |
|---------------|--------------|--------|
| A → B | counterfactual | Proposed (untested) |
| B → C | intervention | Derived from [cite] |

Note: Theoretical proposals are typically counterfactual level (what would happen if).
Confidence is capped at 0.50 until empirical test.

### Argument Scheme

**Primary scheme**: practical_reasoning (for design implications) OR causal_argument (for mechanism proposals)

**Critical questions for theoretical claims**:
| # | Question | Status |
|---|----------|--------|
| 1 | Is the mechanism plausible? | [Physics, biology, psychology check] |
| 2 | Are there alternative mechanisms? | [Competing theories] |
| 3 | What would falsify this? | [Testable predictions] |
```

---

## RULE CONVERSION UPDATES

### Updated EDGE Rule Template

```yaml
rule:
  schema: "ae.rule.v2"
  rule_type: "edge"

  # Original fields
  lhs: [{var: "ENV_GREENSPACE", state: "high"}]
  rhs: [{var: "OUT_STRESS", state: "low"}]
  polarity: "negative"
  strength: {kind: "effect_size", type: "d", value: -0.45}

  # NEW PANEL ADDITIONS
  causal_level: "intervention"
  argument_scheme: "causal_argument"
  critical_questions:
    - "Is there a causal law linking greenspace to stress?"
    - "Was manipulation successful?"
    - "Were confounds controlled?"
  contrast_class: "greenspace vs. urban built environment"
  difference_maker: "vegetation presence enables attention restoration"
  enabling_conditions:
    - "baseline stress elevated"
    - "exposure duration >= 20 minutes"
  bridge_type: null  # or "mechanism" if cross-domain

  # Extraction metadata
  extraction_difficulty: "easy"
  source_zone: "results"
```

### Updated CLAIM Template

```yaml
claim:
  schema: "ae.claim.v2"
  claim_type: "causal"

  # Original fields preserved...

  # NEW PANEL ADDITIONS
  causal_level: "intervention"
  contrast_class: "experimental vs. control condition"
  difference_maker: "nature exposure"
  extraction_difficulty: "moderate"
  source_zone: "discussion"
  argument_scheme: "causal_argument"
  critical_questions:
    - "Was randomization adequate?"
    - "Were there demand characteristics?"
```

---

## VALIDATION CHECKLIST

Before finalizing extraction, verify:

- [ ] **Causal level assigned** — Every empirical claim has a causal level
- [ ] **Argument scheme identified** — Primary argumentation pattern named
- [ ] **Critical questions listed** — At least 2-3 questions per scheme
- [ ] **Unanswered questions noted** — Affects confidence downgrade
- [ ] **Contrast class explicit** — For explanatory claims
- [ ] **Difference maker stated** — What causes the observed effect
- [ ] **Extraction difficulty rated** — Calibrates confidence
- [ ] **Source zone recorded** — Enables audit trail

---

## REFERENCES

- Pearl, J. (2009). Causality. Cambridge University Press.
- Pearl, J., & Mackenzie, D. (2018). The Book of Why. Basic Books.
- Walton, D., Reed, C., & Macagno, F. (2008). Argumentation Schemes. Cambridge University Press.
- Lipton, P. (1991). Inference to the Best Explanation. Routledge.
- Teufel, S. (1999). Argumentative Zoning. PhD thesis, University of Edinburgh.
- Cartwright, N. (1989). Nature's Capacities and Their Measurement. Oxford University Press.

---

*This document extends existing extraction templates. The v2 schemas (ae.claim.v2, ae.rule.v2) are backward-compatible with v1.*
