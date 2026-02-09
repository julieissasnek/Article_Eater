# SYSTEMATIC REVIEW EXTRACTION TEMPLATE v1.1

**Version**: 1.1.0
**Date**: February 9, 2026 (panel additions)
**Original**: February 3, 2026
**Derived From**: Complete Requirements Specification (96 questions)
**Panel Review**: Pearl, Cartwright, Simon, Bates, Kaplan + Walton, Lipton, Hearst, Teufel (2026-02-08)

---

## PURPOSE

Systematic reviews provide **qualitative evidence synthesis** following explicit search and inclusion criteria. They uniquely contribute:
- Evidence direction assessment (consistent/mixed/insufficient)
- Gap identification (what remains untested)
- Quality-stratified findings
- Scope boundaries defined by exclusion criteria

Unlike meta-analyses, systematic reviews do NOT pool effect sizes quantitatively.

---

## WHAT THIS TEMPLATE CAN ANSWER

| Category | Coverage | Notes |
|----------|----------|-------|
| Evidence Direction | SYNTHESIZED | Consistent positive/negative/mixed |
| Scope | FROM INCLUSION CRITERIA | Exclusions define boundaries |
| Gaps | UNIQUE | What questions remain unanswered |
| Quality | AGGREGATED | Quality scores across studies |
| Causal Structure | SYNTHESIZED | From included studies |

## WHAT THIS TEMPLATE CANNOT ANSWER

- Pooled effect sizes (no quantitative synthesis)
- Precise confidence intervals
- Prediction intervals

---

## HUMAN-READABLE OUTPUT STRUCTURE

When constructing the human-readable extraction document for a **systematic review** (qualitative synthesis without pooled effects), follow this structure:

### 1. INTRODUCTION SECTION

**Structure**: Review Question + Why Systematic Synthesis + Scope Definition

```
## Introduction

**Review Question**: [What question does this systematic review address?]

**Why This Review**:
- Gap: [What was unclear before?]
- Problem: [Conflicting findings / no prior synthesis / needed update]
- Timeliness: [Sufficient primary studies now available]

**Protocol Registration**:
| Element | Value |
|---------|-------|
| Registered | Yes/No |
| ID | PROSPERO/OSF: [ID] |
| PRISMA compliant | Yes/No/Partial |

**Scope Defined by Inclusion Criteria**:
| Criterion | Specification |
|-----------|---------------|
| Population | [Who] |
| Intervention/Exposure | [What] |
| Comparator | [Vs. what] |
| Outcome | [What measured] |
| Study design | [RCT/observational/etc.] |
```

### 2. METHODS SECTION

**Structure**: Search → PRISMA Flow → Quality Assessment → Synthesis Approach

```
## Methods

### Search Strategy

| Database | Date Searched | Date Range |
|----------|---------------|------------|
| PubMed | 2026-01-15 | 2000-2025 |
| PsycINFO | 2026-01-15 | 2000-2025 |

**Search string**:
```
(nature OR green space OR park) AND (stress OR anxiety OR well-being)
```

**Grey literature**: Included/Excluded — [What sources]

### PRISMA Flow

```
Records identified (n = X)
        │
        ▼
Duplicates removed (n = X)
        │
        ▼
Records screened (n = X) ──→ Excluded (n = X)
        │
        ▼
Full-text assessed (n = X) ──→ Excluded (n = X)
        │                       Reasons:
        │                       - Wrong population (n = X)
        │                       - Wrong intervention (n = X)
        │                       - Wrong outcome (n = X)
        ▼
Studies included (n = X)
```

### Quality Assessment

**Tool used**: [Cochrane RoB / Newcastle-Ottawa / GRADE / etc.]

| Quality Level | N Studies | % |
|---------------|-----------|---|
| High | X | X% |
| Moderate | X | X% |
| Low | X | X% |

### Synthesis Approach

**Method**: Narrative synthesis / Vote counting / Effect direction analysis
**Why not meta-analysis**: [Too few studies / High heterogeneity / Incompatible measures]
```

### 3. RESULTS SECTION

**Structure**: Findings by Theme → Evidence Direction → Quality Stratification

```
## Results

### Included Studies Summary

| Study | Year | Design | N | Quality |
|-------|------|--------|---|---------|
| Smith et al. | 2020 | RCT | 120 | High |
| Jones et al. | 2019 | Quasi-exp | 85 | Moderate |

### Theme 1: [Outcome Name]

**Evidence Direction**: Consistent Positive / Consistent Negative / Mixed / Insufficient

| Study | Direction | Quality | Sample | Effect (if reported) |
|-------|-----------|---------|--------|---------------------|
| Smith 2020 | + | High | N=120 | d = 0.45 |
| Jones 2019 | + | Moderate | N=85 | d = 0.38 |
| Brown 2018 | null | Low | N=40 | d = 0.12 |

**Synthesis Statement**:
> [What the evidence shows for this theme — hedged appropriately for quality]

**Quality Stratification**:
- High-quality studies (k=2): Consistent positive effects
- Low-quality studies (k=1): Null effect

### Theme 2: [Outcome Name]

**Evidence Direction**: [Direction]

[Same structure as Theme 1]

### Ecological Validity (Kaplan)

| Check | Status |
|-------|--------|
| Lab/field distinguished? | Yes/No |
| If both, reported separately? | Yes/No |
| VR/Video/Photos distinguished? | Yes/No |
| Predominant validity | Field / Lab / Mixed |
```

### 4. DISCUSSION SECTION

**Structure**: Summary → Gaps → Conflicts → Conclusions

```
## Discussion

### Summary of Evidence

| Theme | Direction | Confidence | N Studies |
|-------|-----------|------------|-----------|
| [Theme 1] | Consistent + | Moderate | k = X |
| [Theme 2] | Mixed | Low | k = X |

### Scope Conditions (from inclusion criteria)

| Dimension | Applies To | Does NOT Apply To |
|-----------|------------|-------------------|
| Population | [Included] | [Excluded] |
| Setting | [Included] | [Excluded] |
| Duration | [Included] | [Excluded] |

### Identified Gaps

| Gap Type | Description | Priority |
|----------|-------------|----------|
| Missing population | [What population not studied] | High/Med/Low |
| Missing setting | [What setting not studied] | High/Med/Low |
| Missing outcome | [What outcome not measured] | High/Med/Low |
| Methodological | [What design needed] | High/Med/Low |

### Conflict Assessment

| Finding | Studies Supporting | Studies Opposing | Conflict Type |
|---------|-------------------|------------------|---------------|
| [Finding] | Smith 2020, Jones 2019 | Brown 2018 | SCOPE_BOUNDARY / METHODOLOGICAL / GENUINE |

**Resolution**: [How conflicts were handled — quality-based / subgroup / unresolved]

### Authors' Conclusions vs. Evidence

| Conclusion | Evidence Basis | Our Assessment |
|------------|----------------|----------------|
| [Conclusion 1] | [Evidence] | Supported / Overstated / Hedged appropriately |

### Inferential Boundaries

What CANNOT be concluded from this review:

1. ❌ Pooled effect sizes (no quantitative synthesis)
2. ❌ [Specific over-interpretation]
3. ❌ [Another boundary]

### Our Assessment

**Synthesis Quality**: High / Moderate / Low

**Strengths**:
- [Strength 1]
- [Strength 2]

**Limitations**:
- [Limitation 1]
- [Limitation 2]
```

---

## PRISMA FLOW GUIDANCE

**If PRISMA diagram available**:
- Include figure directly
- Verify numbers add up

**If creating from text**:
- Use ASCII flow diagram (shown above)
- Ensure all exclusion reasons are documented
- Note: Exclusions define scope boundaries (Bates)

---

## EVIDENCE TABLE GUIDANCE

**For each included study, capture**:

| Element | Purpose |
|---------|---------|
| Citation | Identification |
| Year | For temporal analysis |
| Design | For causal strength |
| Sample N | For weighting |
| Quality rating | For stratification |
| Effect direction | For vote counting |
| Effect size (if reported) | For context |
| Key limitations | For quality interpretation |

---

## RULE CONVERSION: FROM SYSTEMATIC REVIEW TO QUINEAN WEB

Systematic reviews produce **edge rules** (evidence direction) and **constraint rules** (gaps, scope boundaries). They do NOT produce cpd_hints (no pooled estimates).

### REQUIRED ELEMENTS FOR RULE INCORPORATION

#### 1. Argument Structure (What Warrants Synthesis Claims?)

| Element | Required? | Source | If Missing |
|---------|-----------|--------|------------|
| **Evidence direction** | ✅ Required | FINDINGS BY THEME | Cannot create rule |
| **Quality assessment** | ✅ Required | QUALITY ASSESSMENT | Confidence affected |
| **N studies** | ✅ Required | PRISMA | Weight affected |
| **Inclusion criteria** | ✅ Required | INCLUSION/EXCLUSION | Scope undefined |
| **Conflict assessment** | Recommended | CONFLICT ASSESSMENT | Uncertainty increased |

**Systematic Review Argument Structure**:
```yaml
argument:
  claim: "Evidence [supports/does not support] [relationship]"
  warrant_type: "systematic_synthesis"
  premises:
    - "Systematic search identified k relevant studies"
    - "Studies were quality-assessed"
    - "Evidence direction was consistent/mixed"
  backing:
    - "k = [N] studies"
    - "Quality distribution: [high/mod/low]"
    - "Direction: [consistent +/-/mixed]"
  qualifier: "Within scope of inclusion criteria"
  rebuttal: "Mixed evidence or low quality weakens conclusion"
```

#### 2. Interrogative Structure (What Questions Does SR Answer?)

| Question | SR Answers | How |
|----------|-----------|-----|
| "What is the evidence direction?" | ✅ Yes | Consistent +/−/mixed |
| "What populations have been studied?" | ✅ Yes | Inclusion criteria |
| "What gaps exist?" | ✅ Yes | Gap identification |
| "What is the effect size?" | ❌ No | No pooling |
| "How precise is the estimate?" | ❌ No | No pooling |

```yaml
interrogative_completeness:
  # SR DOES answer
  what_evidence_direction: true
  what_populations_studied: true
  what_settings_studied: true
  what_gaps_exist: true
  what_conflicts_exist: true

  # SR CANNOT answer
  what_effect_size: false  # Use meta-analysis
  what_confidence_interval: false
```

#### 3. Rule Types from Systematic Reviews

| SR Element | → Rule Type | Confidence |
|------------|-------------|------------|
| Consistent positive evidence | `edge` (polarity: positive) | By quality |
| Consistent negative evidence | `edge` (polarity: negative) | By quality |
| Consistent null evidence | `edge` (polarity: null) | By quality |
| Mixed evidence | `edge` (polarity: mixed) | Lower |
| Identified gap | `constraint` (gap) | N/A |
| Scope boundary | `constraint` (scope) | From inclusion |

---

### RULE TYPE DECISION TREE FOR SYSTEMATIC REVIEWS

```
                    ┌─────────────────────────────┐
                    │  What is evidence direction?│
                    └──────────────┬──────────────┘
                                   │
    ┌──────────────────────────────┼──────────────────────────────┐
    │                              │                              │
    ▼                              ▼                              ▼
┌─────────┐                  ┌─────────┐                  ┌─────────┐
│Consistent│                  │ Mixed   │                  │Insufficient│
│(+, −, or │                  │         │                  │         │
│  null)   │                  │         │                  │         │
└────┬────┘                  └────┬────┘                  └────┬────┘
     │                            │                            │
     ▼                            ▼                            ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│ EDGE rule     │          │ EDGE rule     │          │ CONSTRAINT    │
│ polarity:     │          │ polarity:     │          │ (gap)         │
│ +/−/null      │          │ mixed         │          │               │
│               │          │               │          │ "Insufficient │
│ confidence:   │          │ confidence:   │          │  evidence"    │
│ by quality    │          │ lower         │          │               │
└───────────────┘          └───────────────┘          └───────────────┘
     │
     │ Quality stratification?
     ▼
┌───────────────┐
│ If HQ studies │
│ differ from   │
│ LQ studies:   │
│               │
│ Create        │
│ quality-      │
│ conditional   │
│ rules         │
└───────────────┘
```

---

### COMPLETE CONVERSION EXAMPLES

**Example 1: Consistent Positive Evidence → Edge Rule**

*Extracted data*:
```yaml
theme: "Nature exposure and stress reduction"
evidence_direction: "consistent_positive"
k_studies: 12
quality_distribution:
  high: 4
  moderate: 5
  low: 3
studies:
  - {id: "smith_2020", direction: "+", quality: "high"}
  - {id: "jones_2019", direction: "+", quality: "high"}
  # ... etc
```

*Converted to rule*:
```yaml
rules:
  - rule_id: "chen_sr_2024_theme1"
    rule_type: "edge"

    lhs:
      - var: "ENV_NATURE_EXPOSURE"
        state: "present"
    rhs:
      - var: "OUT_STRESS"
        state: "decreased"
    polarity: "positive"  # Consistent positive direction

    # Strength is DIRECTION, not magnitude
    strength:
      kind: "evidence_direction"
      direction: "consistent_positive"
      k_studies: 12
      quality_distribution:
        high: 4
        moderate: 5
        low: 3
      # NO effect size (SR doesn't pool)
      effect_size: null
      note: "Direction established; magnitude requires meta-analysis"

    # Causal warrant from study designs
    causal:
      n_rcts: 3
      n_quasi: 4
      n_observational: 5
      causal_strength: "moderate"

    # Scope from inclusion criteria
    applicability:
      population: ["adults"]  # From inclusion
      setting: ["field", "lab"]  # From inclusion
      derived_from: "inclusion_criteria"

    # Quality-weighted confidence
    ae_confidence: 0.72

    # What this rule establishes
    establishes: "direction"
    does_not_establish: "magnitude"
```

**Example 2: Mixed Evidence → Edge Rule with Mixed Polarity**

*Extracted data*:
```yaml
theme: "Indoor plants and productivity"
evidence_direction: "mixed"
k_studies: 8
studies:
  - {id: "a", direction: "+", quality: "high"}
  - {id: "b", direction: "+", quality: "moderate"}
  - {id: "c", direction: "null", quality: "high"}
  - {id: "d", direction: "-", quality: "low"}
  # ...
conflict_assessment:
  type: "SCOPE_BOUNDARY"
  resolution: "Effect positive in offices, null in labs"
```

*Converted to rule*:
```yaml
rules:
  # Main rule: Mixed overall
  - rule_id: "wong_sr_2024_theme2"
    rule_type: "edge"

    lhs:
      - var: "ENV_INDOOR_PLANT"
        state: "present"
    rhs:
      - var: "OUT_PRODUCTIVITY"
        state: "changed"
    polarity: "mixed"  # Inconsistent evidence

    strength:
      kind: "evidence_direction"
      direction: "mixed"
      k_studies: 8
      conflict_type: "SCOPE_BOUNDARY"
      conflict_resolution: "setting_moderates"

    ae_confidence: 0.55  # Lower due to inconsistency

  # Conditional rule: Positive in offices
  - rule_id: "wong_sr_2024_theme2_office"
    rule_type: "edge"

    lhs:
      - var: "ENV_INDOOR_PLANT"
        state: "present"
    rhs:
      - var: "OUT_PRODUCTIVITY"
        state: "increased"
    polarity: "positive"

    strength:
      kind: "evidence_direction"
      direction: "consistent_positive"
      k_studies: 4
      conditional_on: "setting = office"

    applicability:
      setting: ["office"]
      scope_specified: true

    ae_confidence: 0.68

  # Conditional rule: Null in labs
  - rule_id: "wong_sr_2024_theme2_lab"
    rule_type: "edge"

    lhs:
      - var: "ENV_INDOOR_PLANT"
        state: "present"
    rhs:
      - var: "OUT_PRODUCTIVITY"
        state: "changed"
    polarity: "null"

    strength:
      kind: "evidence_direction"
      direction: "consistent_null"
      k_studies: 4
      conditional_on: "setting = lab"

    applicability:
      setting: ["lab"]

    ae_confidence: 0.60
```

**Example 3: Identified Gap → Constraint Rule**

*Extracted data*:
```yaml
gaps:
  - type: "missing_population"
    description: "No studies on children under 12"
    priority: "high"
  - type: "missing_setting"
    description: "No studies in tropical climates"
    priority: "medium"
```

*Converted to rules*:
```yaml
rules:
  - rule_id: "lee_sr_2024_gap1"
    rule_type: "constraint"

    constraint_type: "gap"

    description: "No evidence exists for children under 12"
    gap_type: "missing_population"

    scope_implication:
      any_rule_about: "nature_stress_reduction"
      does_not_apply_to: ["children_under_12"]
      reason: "No studies, not negative evidence"

    voi_signal:
      priority: "high"
      research_needed: "Studies with children < 12"
      would_answer: "Does effect generalize to children?"

    ae_confidence: null  # Gaps don't have confidence

  - rule_id: "lee_sr_2024_gap2"
    rule_type: "constraint"

    constraint_type: "gap"
    description: "No evidence for tropical climates"
    gap_type: "missing_setting"

    scope_implication:
      any_rule_about: "nature_stress_reduction"
      does_not_apply_to: ["tropical_climate"]

    voi_signal:
      priority: "medium"
      research_needed: "Studies in tropical settings"
```

**Example 4: Scope Boundary from Exclusions → Constraint Rule**

*Extracted data*:
```yaml
exclusion_criteria:
  - criterion: "Studies with clinical populations"
    n_excluded: 23
    implication: "Findings may not apply to clinical populations"
```

*Converted to rule*:
```yaml
rules:
  - rule_id: "kim_sr_2024_scope1"
    rule_type: "constraint"

    constraint_type: "scope_boundary"

    description: "Review excluded clinical populations;
                  findings do not generalize to clinical samples"

    scope_limitation:
      any_finding_in_this_review:
        applies_to: ["healthy_adults", "subclinical"]
        does_not_apply_to: ["clinical_depression", "clinical_anxiety", "ptsd"]
      reason: "Systematically excluded from synthesis"

    ae_confidence: 0.85  # Clear exclusion criterion
```

---

### CONFIDENCE SCORING FOR SYSTEMATIC REVIEWS

| Factor | Impact | Rationale |
|--------|--------|-----------|
| **Evidence direction** | | |
| Consistent | +0.10 | Clear signal |
| Mixed | -0.10 | Uncertain signal |
| Insufficient | N/A | Gap, not rule |
| **Quality distribution** | | |
| >50% high quality | +0.10 | Robust evidence |
| Mostly moderate | 0 | Adequate |
| >50% low quality | -0.15 | Weak evidence |
| **k studies** | | |
| k > 15 | +0.05 | Comprehensive |
| k = 5-15 | 0 | Adequate |
| k < 5 | -0.10 | Limited |
| **Search comprehensiveness** | | |
| Multiple databases + grey lit | +0.05 | Thorough |
| Limited search | -0.10 | May miss studies |

**Base confidence**: 0.65 for systematic review
**Range**: 0.45 (weak SR) to 0.80 (excellent SR)

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
| Article type | SYSTEMATIC REVIEW |
| Source depth | [ ] Full text [ ] Abstract only [ ] Metadata only |

---

## OUR SUMMARY

- Plain-language summary of synthesis findings (1-3 sentences)
- Direction of evidence
- Key gaps identified

---

## RESEARCH QUESTION

**Q.RQ.1: What is the primary review question?**

**Q.RQ.2: What gap does this review address?**

**Q.RQ.3: Why now?** (sufficient studies accumulated, need for synthesis, conflicting findings)

---

## PROTOCOL & REGISTRATION

**Q: Was this review pre-registered?**

| Element | Value |
|---------|-------|
| Registered | Yes / No |
| Registration ID | PROSPERO/OSF/etc. |
| Protocol published | Yes / No |
| PRISMA compliant | Yes / No / Partially |

---

## SEARCH STRATEGY

### Databases Searched

| Database | Date Searched | Date Range |
|----------|---------------|------------|
| | | |

### Search Terms

**Q: What search terms were used?**

```
[Search string]
```

**Q: How do search terms map to canonical IDs?** *(Bates)*

| Search Term | Canonical ID | Captures |
|-------------|--------------|----------|
| | | Full / Partial / Approximate |

### Grey Literature

| Source | Included? |
|--------|-----------|
| Dissertations | Yes / No |
| Conference proceedings | Yes / No |
| Unpublished studies | Yes / No |

---

## INCLUSION/EXCLUSION CRITERIA

### Inclusion Criteria

| Criterion | Specification |
|-----------|---------------|
| Population | |
| Intervention/Exposure | |
| Comparator | |
| Outcome | |
| Study design | |
| Date range | |
| Language | |

### Exclusion Criteria *(Bates: These define scope boundaries)*

| Exclusion Criterion | Rationale | Implication for Scope |
|---------------------|-----------|----------------------|
| | | What this excludes from conclusions |

---

## PRISMA FLOW

| Stage | N | Notes |
|-------|---|-------|
| Records identified | | |
| Duplicates removed | | |
| Records screened (title/abstract) | | |
| Records excluded (screening) | | |
| Full-text articles assessed | | |
| Full-text excluded | | |
| Studies included in synthesis | | |

**Q: What were the main reasons for full-text exclusion?**

| Reason | N Excluded |
|--------|------------|
| Wrong population | |
| Wrong intervention | |
| Wrong outcome | |
| Wrong study design | |
| Insufficient data | |

---

## QUALITY ASSESSMENT

**Q: What quality assessment tool was used?**

| Element | Value |
|---------|-------|
| Tool name | Cochrane RoB / Newcastle-Ottawa / GRADE / Other: |
| Assessed by | N assessors |
| Inter-rater reliability | |

### Quality Ratings

| Quality Level | N Studies | % |
|---------------|-----------|---|
| High | | |
| Moderate | | |
| Low | | |
| Critical/Very Low | | |

### Quality by Study

| Study | Quality Rating | Key Concerns |
|-------|----------------|--------------|
| | | |

---

## SYNTHESIS METHOD

**Q: What synthesis method was used?**

[ ] Narrative synthesis
[ ] Vote counting
[ ] Effect direction analysis
[ ] Thematic synthesis
[ ] Framework synthesis
[ ] Other: ___________

**Q: Why was quantitative synthesis (meta-analysis) not performed?**

| Reason |
|--------|
| [ ] Too few studies |
| [ ] High heterogeneity in methods |
| [ ] Insufficient statistical reporting |
| [ ] Incompatible outcome measures |
| [ ] Authors' choice |

---

## FINDINGS BY THEME/OUTCOME

### Theme 1: [Name]

**Evidence Direction**: Consistent Positive / Consistent Negative / Mixed / Insufficient

| Study | Direction | Quality | Sample | Effect (if reported) |
|-------|-----------|---------|--------|---------------------|
| | +/−/null | H/M/L | N= | |

**Synthesis Statement**:
> [What the evidence shows for this theme]

### Theme 2: [Name]

**Evidence Direction**: Consistent Positive / Consistent Negative / Mixed / Insufficient

| Study | Direction | Quality | Sample | Effect (if reported) |
|-------|-----------|---------|--------|---------------------|
| | +/−/null | H/M/L | N= | |

**Synthesis Statement**:
> [What the evidence shows for this theme]

---

## SCOPE CONDITIONS *(Derived from inclusion criteria)*

| Dimension | Value | Source |
|-----------|-------|--------|
| Population | | Inclusion criterion |
| Setting | | Inclusion criterion |
| Intervention type | | Inclusion criterion |
| Outcome type | | Inclusion criterion |

**Q.SC.5: Is scope explicitly constrained by exclusion?**
[ ] Yes - exclusion criteria clearly define boundaries
[ ] Partially - some boundaries implicit
[ ] No - scope unclear

---

## ECOLOGICAL VALIDITY *(Kaplan)*

**Q: How is ecological validity handled in inclusion criteria?**

| Check | Status |
|-------|--------|
| Lab/field distinguished? | Yes / No |
| If included both, reported separately? | Yes / No |
| VR/Video/Photos distinguished? | Yes / No |

**Q: What is the predominant ecological validity of included studies?**
[ ] Mostly field [ ] Mostly lab [ ] Mixed (reported separately) [ ] Mixed (not distinguished)

---

## CAUSAL STRUCTURE *(Synthesized)*

**Q: What can be concluded about causal direction?**

| Element | Synthesis |
|---------|-----------|
| N studies with experimental designs | |
| N studies observational | |
| Direction of evidence | Supports causal / Correlational only / Mixed |
| Causal conclusion warranted? | Yes / No / Insufficient |

---

## GAP IDENTIFICATION *(Unique contribution)*

**Q: What gaps did the review identify?**

| Gap Type | Description | Priority |
|----------|-------------|----------|
| Unanswered question | | High / Medium / Low |
| Missing population | | |
| Missing setting | | |
| Missing outcome | | |
| Missing study design | | |
| Methodological gap | | |

---

## CONFLICT ASSESSMENT

**Q: Did included studies conflict?**

| Finding | Studies Supporting | Studies Opposing | Conflict Type |
|---------|-------------------|------------------|---------------|
| | | | GENUINE / SCOPE_BOUNDARY / METHODOLOGICAL |

**Q: How were conflicts resolved?**

| Resolution Method |
|-------------------|
| [ ] Quality-based (prioritize high-quality) |
| [ ] Subgroup analysis |
| [ ] Not resolved |

---

## AUTHORS' CONCLUSIONS

**Q: What do authors conclude?**

| Conclusion | Evidence Basis | Confidence |
|------------|----------------|------------|
| | Supported / Partially supported / Overstated | |

**Q: Do conclusions match evidence strength?**
[ ] Yes - appropriately hedged
[ ] No - overstate certainty
[ ] No - understate findings

---

## OUR ASSESSMENT

**Strengths**
- [What this review does well]

**Limitations**
- [Methodological concerns]

**Quality of Synthesis**
[ ] High (rigorous protocol, comprehensive search, quality assessment)
[ ] Moderate (some limitations)
[ ] Low (significant limitations)

---

## PRACTICAL IMPLICATIONS

**Q: What recommendations do authors make?**

| Recommendation | Evidence Strength |
|----------------|-------------------|
| | Strong / Moderate / Weak |

---

## Q&A SECTION

**Q: What is the direction of evidence?**
A:

**Q: How confident should we be?**
A:

**Q: What populations does this apply to?**
A:

**Q: What settings does this apply to?**
A:

**Q: What are the key gaps?**
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
article_type: "systematic_review"
source_depth: "full_text|abstract|metadata"

# ============================================
# QUESTIONS ANSWERED
# ============================================
questions:
  ID.1_citation: ""
  ID.2_article_type: "systematic_review"
  ID.3_source_depth: ""
  RQ.1_primary_question: ""
  RQ.2_gap_addressed: ""
  RQ.3_timeliness: ""

# ============================================
# PROTOCOL
# ============================================
protocol:
  registered: true|false
  registration_id: ""
  protocol_published: true|false
  prisma_compliant: true|false|partial

# ============================================
# SEARCH
# ============================================
search:
  databases:
    - name: ""
      date_searched: ""
      date_range: {start: "", end: ""}
  search_string: ""
  search_terms_to_canonical:
    - term: ""
      canonical_id: ""
  grey_literature:
    dissertations: true|false
    conference_proceedings: true|false
    unpublished: true|false

# ============================================
# INCLUSION/EXCLUSION
# ============================================
inclusion:
  population: ""
  intervention: ""
  comparator: ""
  outcome: ""
  study_design: ""
  date_range: ""
  language: ""

exclusion:
  - criterion: ""
    rationale: ""
    scope_implication: ""

# ============================================
# PRISMA
# ============================================
prisma:
  n_identified:
  n_duplicates_removed:
  n_screened:
  n_excluded_screening:
  n_full_text_assessed:
  n_full_text_excluded:
  n_included:
  exclusion_reasons:
    wrong_population:
    wrong_intervention:
    wrong_outcome:
    wrong_design:
    insufficient_data:

# ============================================
# QUALITY ASSESSMENT
# ============================================
quality:
  tool: ""
  n_assessors:
  inter_rater_reliability:
  ratings:
    high:
    moderate:
    low:
    critical:
  by_study:
    - study: ""
      rating: ""
      concerns: []

# ============================================
# SYNTHESIS
# ============================================
synthesis:
  method: "narrative|vote_counting|effect_direction|thematic|framework"
  why_not_meta_analysis: ""

  findings:
    - theme: ""
      evidence_direction: "consistent_positive|consistent_negative|mixed|insufficient"
      n_studies:
      synthesis_statement: ""
      studies:
        - id: ""
          direction: "+|-|null"
          quality: "high|moderate|low"
          sample_n:

# ============================================
# SCOPE (Derived)
# ============================================
scope:
  population: ""
  setting: ""
  intervention_type: ""
  outcome_type: ""
  scope_explicitly_constrained: true|false|partial
  derived_from: "inclusion_criteria"

# ============================================
# ECOLOGICAL VALIDITY
# ============================================
ecological_validity:
  lab_field_distinguished: true|false
  reported_separately: true|false
  vr_video_photos_distinguished: true|false
  predominant: "field|lab|mixed_separate|mixed_undistinguished"

# ============================================
# CAUSAL
# ============================================
causal:
  n_experimental:
  n_observational:
  direction_of_evidence: "supports_causal|correlational|mixed|insufficient"
  causal_conclusion_warranted: true|false|insufficient

# ============================================
# GAPS (Unique)
# ============================================
gaps:
  - type: "unanswered_question|missing_population|missing_setting|missing_outcome|missing_design|methodological"
    description: ""
    priority: "high|medium|low"

# ============================================
# CONFLICTS
# ============================================
conflicts:
  - finding: ""
    studies_supporting: []
    studies_opposing: []
    conflict_type: "GENUINE|SCOPE_BOUNDARY|METHODOLOGICAL"
    resolution: "quality_based|subgroup|not_resolved"

# ============================================
# RULES GENERATED (v2 with panel additions)
# ============================================
rules:
  # Edge rules from consistent findings
  - rule_id: ""
    rule_type: "edge"
    lhs:
      - var: ""
        state: ""
    rhs:
      - var: ""
        state: ""
    polarity: "positive|negative|null|mixed"
    strength:
      kind: "synthesis"
      evidence_direction: ""
      n_studies:
      quality_distribution: {}
    applicability:
      population: []
      setting: []
    ae_confidence:

    # === PANEL ADDITIONS (2026-02-09) ===
    # Pearl: Causal level (SR inherits LOWEST level from included studies)
    causal_level: "association|intervention"  # rarely counterfactual for SR

    # Walton: Argument scheme for synthesis claims
    argument_scheme: "argument_from_expert_opinion"  # synthesis = expert aggregation
    critical_questions:
      - "Are included studies homogeneous?"
      - "Is there publication bias?"
      - "Is the search comprehensive?"
    critical_questions_addressed: []

    # Lipton: Contrast class (what is the foil for SR findings?)
    contrast_class: ""  # e.g., "exposed vs not exposed"
    difference_maker: ""  # e.g., "nature exposure"

    # Hearst/Teufel: Extraction metadata
    extraction_difficulty: "easy|moderate|hard"
    source_zone: "results|discussion|abstract"

  # Constraint rules from gaps
  - rule_id: ""
    rule_type: "constraint"
    constraint_type: "gap"
    description: ""
    priority: ""

    # Panel addition: VOI signal
    voi_signal:
      research_needed: ""
      would_answer: ""

# ============================================
# QUALITY
# ============================================
overall_quality:
  synthesis_quality: "high|moderate|low"
  our_confidence:
```

---

**END OF SYSTEMATIC REVIEW TEMPLATE**
