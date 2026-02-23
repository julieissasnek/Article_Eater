# ⚠️ SUPERSEDED — See (newer version exists) for current version

# NARRATIVE REVIEW EXTRACTION TEMPLATE v1.0

**Version**: 1.0.0
**Date**: February 3, 2026
**Derived From**: Complete Requirements Specification (96 questions)
**Panel Review**: Pearl, Cartwright, Simon, Bates, Kaplan

---

## PURPOSE

Narrative reviews provide **expert synthesis** without systematic search protocols. They contribute:
- Historical context and field evolution
- Expert intuition about important papers
- Synthesis of expert opinion
- Suggested gaps and future directions

**⚠️ IMPORTANT**: All claims from narrative reviews carry LOW confidence unless corroborated by systematic evidence. Expert opinion is the weakest form of warrant.

---

## WHAT THIS TEMPLATE CAN ANSWER

| Category | Coverage | Confidence |
|----------|----------|------------|
| Historical Context | UNIQUE | Moderate (factual) |
| Field Evolution | UNIQUE | Moderate (factual) |
| Expert Synthesis | EXPERT OPINION | LOW |
| Suggested Gaps | EXPERT OPINION | LOW |
| Seminal Papers | USEFUL | Moderate |

## WHAT THIS TEMPLATE CANNOT RELIABLY ANSWER

- Effect sizes (no systematic data)
- Scope boundaries (no systematic inclusion criteria)
- Evidence strength (selection bias in citations)
- Causal structure (expert intuition only)

---

## HUMAN-READABLE OUTPUT STRUCTURE

When constructing the human-readable extraction document for a **narrative review**, follow this structure:

### 1. INTRODUCTION SECTION

**Structure**: Review Purpose + Author Expertise + Scope Declaration

```
## Introduction

**Review Purpose**: [What synthesis is being offered?]

**⚠️ CONFIDENCE WARNING**: This is a narrative review — all claims are expert opinion without systematic warrant. Confidence is LOW unless corroborated by systematic evidence.

### Author Expertise

| Author | Credentials | H-index | Expertise Area |
|--------|-------------|---------|----------------|
| [Name] | [Credentials] | [H-index] | [Area] |

**Prior work in this area**:
| Publication | Year | Relevance |
|-------------|------|-----------|
| [Title] | [Year] | Core / Peripheral |

**Potential biases**:
| Bias Type | Evidence |
|-----------|----------|
| Theoretical commitment | [Evidence] |
| Prior findings to defend | [Evidence] |
| Funding sources | [Evidence] |

### Scope Declaration

| Dimension | Stated Scope |
|-----------|--------------|
| Time period | [Coverage] |
| Subtopics included | [List] |
| Subtopics excluded | [List] |
| Stated purpose | [Purpose] |

**Scope explicitly delimited?**: Yes / No
```

### 2. KEY CLAIMS SECTION

**Structure**: Claims → Evidence Basis → Confidence Rating

```
## Key Claims

**⚠️ For each claim, distinguish evidence basis**

| Claim # | Statement | Evidence Basis | Confidence |
|---------|-----------|----------------|------------|
| 1 | [Claim] | Cited evidence / Expert opinion / Claimed consensus | LOW |
| 2 | [Claim] | Cited evidence / Expert opinion / Claimed consensus | LOW |

### Claim 1: [Statement]

**Evidence basis**: [Type]

**If cited evidence**:
- Citation: [Paper cited]
- ⚠️ ACTION: Extract that paper separately for direct evidence

**If expert opinion**:
- No systematic basis
- Weight by author credentials

**If "consensus"** ("It is widely accepted that..."):
- ⚠️ Verify independently before accepting
- Claimed consensus ≠ actual consensus

**Confidence**: LOW
```

### 3. HISTORICAL CONTEXT SECTION *(Unique Contribution)*

**Structure**: Evolution → Seminal Papers → Paradigm Shifts

```
## Historical Context

### Field Evolution

| Era/Period | Key Development | Seminal Paper(s) |
|------------|-----------------|------------------|
| 1980s | [Development] | [Papers] |
| 1990s | [Development] | [Papers] |

### Seminal Papers Identified

| Paper | Year | Why Seminal (per author) | Extract? |
|-------|------|--------------------------|----------|
| Ulrich (1984) | 1984 | Founded SRT | Yes / Already have / Not relevant |
| Kaplan & Kaplan (1989) | 1989 | Founded ART | Yes / Already have / Not relevant |

**⚠️ ACTION**: Papers identified as seminal should be queued for systematic extraction

### Paradigm Shifts

| Shift | From | To | When | Evidence Type |
|-------|------|----|----- |---------------|
| [Shift name] | [Old view] | [New view] | [Date] | Documented / Author interpretation |
```

### 4. EXPERT INTUITIONS SECTION *(Low Confidence)*

**Structure**: Predictions → Gaps → Recommended Directions

```
## Expert Intuitions

**⚠️ All intuitions carry LOW confidence — use only to guide research priorities**

### Author's Predictions

| Prediction | Basis | Confidence |
|------------|-------|------------|
| [Prediction 1] | Expert intuition | LOW |

### Identified Gaps

| Gap | Why Important (per author) | Confidence |
|-----|---------------------------|------------|
| [Gap 1] | [Rationale] | LOW (expert opinion) |

**⚠️ Use for VOI calculation, not as established facts**

### Recommended Directions

| Direction | Rationale | Confidence |
|-----------|-----------|------------|
| [Direction 1] | [Author's reasoning] | LOW (expert opinion) |
```

### 5. DISCUSSION SECTION

**Structure**: Theory Comparison → Term Usage → Our Assessment

```
## Discussion

### Theoretical Claims

| Theory | Author's Claim | Evidence Cited | Confidence |
|--------|----------------|----------------|------------|
| [Theory] | [Claim] | [Evidence] | LOW unless systematic |

**Does author favor particular theories?**

| Favored Theory | Evidence of Bias |
|----------------|------------------|
| [Theory] | [Evidence of favoritism] |

### Terminology Usage (Bates)

| Term | Author's Usage | Standard Usage | Differs? |
|------|---------------|----------------|----------|
| [Term] | [Definition] | [Standard] | Yes/No |

**⚠️ Flag idiosyncratic usage for term harmonization**

### Comparison to Systematic Reviews

| Systematic Review | Agreement | Disagreement |
|-------------------|-----------|--------------|
| [SR on same topic] | [Where agrees] | [Where disagrees] |

**⚠️ When narrative differs from systematic, trust systematic**

### Our Assessment

**Strengths**:
- Historical context (typically high quality)
- Seminal paper identification (useful)
- Expert-suggested gaps (useful for VOI)

**Limitations**:
- Selection bias (author-chosen citations)
- No systematic search
- No quality assessment of cited studies
- Expert opinion ≠ systematic evidence

**Overall Confidence**: LOW (narrative review without systematic warrant)

### Inferential Boundaries

What CANNOT be taken from this review:

1. ❌ Effect sizes (no systematic data)
2. ❌ Scope boundaries (no systematic inclusion criteria)
3. ❌ Evidence strength (selection bias in citations)
4. ❌ Causal structure claims (expert intuition only)

### Value to BN

| Use | Appropriate? |
|-----|-------------|
| Historical context | ✅ Yes |
| Identify papers for extraction | ✅ Yes |
| Corroborate (not establish) findings | ✅ Yes |
| Suggested gaps for VOI | ✅ Yes |
| Direct entry of claims to BN | ❌ No |
| Effect size estimation | ❌ No |
| Scope condition setting | ❌ No |
```

---

## USAGE PROTOCOL FOR NARRATIVE REVIEWS

**Step 1**: Extract as documented above (human-readable + YAML)

**Step 2**: Identify actionable items:
- [ ] Seminal papers to extract systematically
- [ ] Gaps to inform VOI search
- [ ] Historical context for background

**Step 3**: DO NOT:
- Enter claims directly into BN
- Use as evidence for effect sizes
- Treat expert opinion as equivalent to systematic evidence

**Step 4**: Use narrative review claims ONLY to:
- Set weak priors (to be updated by data)
- Corroborate findings from systematic sources
- Guide literature search priorities

---

## RULE CONVERSION: FROM NARRATIVE REVIEW TO QUINEAN WEB

Narrative reviews produce **prior rules** (weak beliefs) and **gap rules** (VOI signals). They should NEVER produce high-confidence edge or cpd_hint rules.

### ⚠️ CRITICAL WARNING

**Narrative reviews are expert opinion without systematic warrant.**

- All rules from narrative reviews require `requires_corroboration: true`
- Confidence should NEVER exceed 0.50
- Rules enter the web as weak priors, not established findings

### REQUIRED ELEMENTS FOR RULE INCORPORATION

#### 1. Argument Structure (What Warrants Expert Claims?)

| Element | Required? | Source | If Missing |
|---------|-----------|--------|------------|
| **Author credentials** | ✅ Required | AUTHOR EXPERTISE | Weight affected |
| **Claim statement** | ✅ Required | KEY CLAIMS | Cannot create rule |
| **Evidence basis** | ✅ Required | KEY CLAIMS | Must classify |
| **Potential biases** | Recommended | AUTHOR EXPERTISE | Flag if missing |

**Narrative Review Argument Structure**:
```yaml
argument:
  claim: "[Expert's claim]"
  warrant_type: "expert_opinion"  # ALWAYS this type
  strength: "weak"  # ALWAYS weak

  # Evidence basis matters
  evidence_basis:
    type: "cited_evidence|expert_opinion|claimed_consensus"
    if_cited: "Extract cited paper separately"
    if_opinion: "Low confidence, requires corroboration"
    if_consensus: "Verify independently; claimed ≠ actual"

  # Author credibility
  author:
    credentials: "[Credentials]"
    h_index: "[If known]"
    potential_biases: ["[List]"]
    bias_impact: "May favor [theory/direction]"
```

#### 2. Interrogative Structure (What Questions Does Narrative Answer?)

| Question | Narrative Answers | Reliability |
|----------|------------------|-------------|
| "What do experts believe?" | ✅ Yes | Moderate (for expert opinion) |
| "What seminal papers exist?" | ✅ Yes | High (factual) |
| "What gaps are suggested?" | ✅ Yes | Moderate (for research direction) |
| "What is the effect size?" | ❌ No | N/A |
| "What is the scope?" | ⚠️ Unreliable | LOW |
| "Is the relationship causal?" | ⚠️ Unreliable | LOW |

```yaml
interrogative_completeness:
  # Narrative CAN provide (with caveats)
  what_experts_believe: true  # But = opinion
  what_seminal_papers: true   # Factual, useful
  what_gaps_suggested: true   # Useful for VOI
  what_historical_context: true  # Unique contribution

  # Narrative CANNOT reliably answer
  what_effect_size: false
  what_scope_conditions: false  # Opinion only
  what_causal_direction: false  # Opinion only
```

#### 3. Rule Types from Narrative Reviews

| Narrative Element | → Rule Type | Max Confidence |
|-------------------|-------------|----------------|
| Expert claim | `prior` | 0.40-0.50 |
| Suggested gap | `constraint` (gap) | N/A |
| Seminal paper identified | Action: extract that paper | N/A |
| Historical fact | `prior` (factual) | 0.70 |

---

### RULE TYPE DECISION TREE FOR NARRATIVE REVIEWS

```
                    ┌─────────────────────────────┐
                    │  What type of content?      │
                    └──────────────┬──────────────┘
                                   │
    ┌──────────────────────────────┼──────────────────────────────┐
    │                              │                              │
    ▼                              ▼                              ▼
┌─────────────┐            ┌─────────────┐            ┌─────────────┐
│ Expert claim│            │ Suggested   │            │ Seminal     │
│ about effect│            │ research gap│            │ paper ID    │
└──────┬──────┘            └──────┬──────┘            └──────┬──────┘
       │                          │                          │
       ▼                          ▼                          ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│ PRIOR rule    │          │ CONSTRAINT    │          │ NOT A RULE    │
│               │          │ (gap)         │          │               │
│ confidence:   │          │               │          │ ACTION:       │
│ ≤ 0.50        │          │ For VOI       │          │ Queue paper   │
│               │          │ calculation   │          │ for extraction│
│ requires_     │          │               │          │               │
│ corroboration:│          │               │          │               │
│ true          │          │               │          │               │
└───────────────┘          └───────────────┘          └───────────────┘
       │
       │ What is evidence basis?
       ▼
┌────────────────────────────────────────────┐
│ Cited evidence → Extract that paper instead│
│ Expert opinion → Prior (conf ≤ 0.45)       │
│ "Consensus" → Verify; prior (conf ≤ 0.40)  │
└────────────────────────────────────────────┘
```

---

### COMPLETE CONVERSION EXAMPLES

**Example 1: Expert Claim (Opinion) → Prior Rule**

*Extracted data*:
```yaml
claim:
  statement: "Nature exposure reduces stress through parasympathetic activation"
  evidence_basis: "expert_opinion"
  author:
    name: "Dr. Expert"
    h_index: 45
    expertise: "environmental_psychology"
    potential_biases: ["Advocates for urban greening policy"]
```

*Converted to rule*:
```yaml
rules:
  - rule_id: "expert_2024_claim1"
    rule_type: "prior"  # Not edge, not cpd_hint

    lhs:
      - var: "ENV_NATURE"
        state: "exposed"
    rhs:
      - var: "OUT_STRESS"
        state: "decreased"
    polarity: "negative"

    # WEAK strength (expert opinion)
    strength:
      kind: "expert_opinion"
      basis: "narrative_review"
      systematic_warrant: false  # Critical flag

    # LOW confidence, capped
    ae_confidence: 0.45
    max_confidence: 0.50  # Cannot exceed without corroboration

    # REQUIRES corroboration
    requires_corroboration: true
    until_corroborated:
      status: "weak_prior"
      use_for: "initial_belief_only"
      do_not_use_for: "inference"

    # Source reliability assessment
    source:
      type: "narrative_review"
      author_h_index: 45
      potential_bias: "policy_advocacy"
      bias_direction: "may_favor_positive_effects"

    # What this rule IS and ISN'T
    rule_status:
      establishes: "expert believes this"
      does_not_establish: "empirical truth"
      action_needed: "find_systematic_evidence"
```

**Example 2: Expert Claim (Cited Evidence) → Redirect**

*Extracted data*:
```yaml
claim:
  statement: "Ulrich (1984) showed that nature views speed hospital recovery"
  evidence_basis: "cited_evidence"
  citation: "Ulrich, R. S. (1984). View through a window..."
```

*Converted to action, NOT rule*:
```yaml
# DO NOT create rule from narrative review's summary of Ulrich

actions:
  - action: "extract_primary_source"
    paper: "ulrich_1984"
    doi: "10.1126/science.6143402"
    reason: "Narrative review cites this; extract directly for reliable evidence"
    priority: "high"

# IF primary not available, create minimal prior:
rules:
  - rule_id: "expert_2024_ref1"
    rule_type: "prior"
    status: "placeholder_pending_extraction"
    statement: "Ulrich 1984 reportedly found nature views speed recovery"
    ae_confidence: 0.35  # Very low until we extract primary
    requires_primary_extraction: true
```

**Example 3: Claimed Consensus → Highly Skeptical Prior**

*Extracted data*:
```yaml
claim:
  statement: "It is widely accepted that nature exposure benefits mental health"
  evidence_basis: "claimed_consensus"
```

*Converted to rule*:
```yaml
rules:
  - rule_id: "expert_2024_consensus1"
    rule_type: "prior"

    lhs:
      - var: "ENV_NATURE"
        state: "exposed"
    rhs:
      - var: "OUT_MENTAL_HEALTH"
        state: "improved"
    polarity: "positive"

    strength:
      kind: "claimed_consensus"
      warning: "Claimed consensus ≠ verified consensus"
      action_required: "Verify with systematic review or meta-analysis"

    ae_confidence: 0.40  # LOW for unverified consensus

    requires_corroboration: true
    verification_needed:
      type: "systematic_review_or_meta_analysis"
      until_verified: "treat_as_weak_prior"

    # Flag for attention
    attention_flag: "UNVERIFIED_CONSENSUS"
```

**Example 4: Suggested Gap → Constraint Rule (VOI)**

*Extracted data*:
```yaml
gap:
  description: "Few studies examine nature exposure in clinical PTSD populations"
  author_rationale: "May have therapeutic applications"
```

*Converted to rule*:
```yaml
rules:
  - rule_id: "expert_2024_gap1"
    rule_type: "constraint"

    constraint_type: "gap"
    description: "Expert identifies lack of research on nature × PTSD"

    gap_details:
      type: "missing_population"
      population: "clinical_ptsd"
      current_evidence: "few_or_no_studies"

    voi_signal:
      source: "expert_suggestion"
      priority: "medium"  # Expert opinion on priority
      potential_value: "therapeutic_application"
      research_needed: "RCT of nature exposure in PTSD treatment"

    ae_confidence: null  # Gaps don't have confidence

    # NOTE: Expert-suggested gap, not systematic gap identification
    gap_reliability: "expert_opinion"
    compare_with: "systematic_review_gap_analysis"
```

**Example 5: Seminal Paper Identified → Action Item**

*Extracted data*:
```yaml
seminal_paper:
  citation: "Kaplan, S. (1995). The restorative benefits of nature..."
  why_seminal: "Introduced directed attention fatigue concept"
```

*Converted to action*:
```yaml
# This is NOT a rule; it's a queue action

actions:
  - action: "queue_for_extraction"
    paper_type: "seminal_theoretical"
    citation: "Kaplan, S. (1995). The restorative benefits of nature..."
    extraction_template: "THEORETICAL"
    priority: "high"
    reason: "Identified as foundational by expert review"

# No rule created from narrative review's mention
```

---

### CONFIDENCE CAPS FOR NARRATIVE REVIEWS

| Content Type | Maximum Confidence | Rationale |
|--------------|-------------------|-----------|
| Expert opinion on effects | 0.45 | No systematic warrant |
| Claimed consensus | 0.40 | Unverified |
| Historical fact | 0.70 | Factual, verifiable |
| Gap identification | N/A | Not a belief |
| Seminal paper ID | N/A | Action, not rule |

**Absolute maximum**: 0.50 for any claim from narrative review

---

### CORROBORATION REQUIREMENTS

**Before narrative-derived prior can be upgraded:**

1. Find systematic review or meta-analysis on same topic
2. Extract and compare
3. If systematic evidence confirms:
   - Upgrade confidence based on systematic source
   - Mark as "corroborated"
4. If systematic evidence contradicts:
   - Trust systematic over narrative
   - Mark narrative claim as "superseded"

```yaml
corroboration_protocol:
  narrative_claim: "Nature reduces stress"
  narrative_confidence: 0.45

  if_corroborated_by:
    meta_analysis:
      new_confidence: "from_meta_analysis"
      status: "corroborated"
    systematic_review:
      new_confidence: "from_systematic_review"
      status: "corroborated"

  if_contradicted_by:
    meta_analysis:
      action: "trust_meta_analysis"
      narrative_status: "superseded"
    systematic_review:
      action: "trust_systematic"
      narrative_status: "superseded"
```

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
| Article type | NARRATIVE REVIEW |
| Source depth | [ ] Full text [ ] Abstract only [ ] Metadata only |

---

## OUR SUMMARY

- Plain-language summary of review contribution (1-3 sentences)
- Key expert claims
- ⚠️ Confidence level: LOW (narrative review)

---

## AUTHOR EXPERTISE *(Critical for weighting)*

**Q: What are the author's credentials?**

| Author | Credentials | H-index (if known) | Expertise Area |
|--------|-------------|-------------------|----------------|
| | | | |

**Q: What is the author's prior work in this area?**

| Prior Publication | Year | Relevance |
|-------------------|------|-----------|
| | | Core / Peripheral |

**Q: What potential biases might the author have?**

| Potential Bias | Evidence |
|----------------|----------|
| Theoretical commitment to [theory] | |
| Prior findings to defend | |
| Funding sources | |
| Professional relationships | |

---

## SCOPE DECLARATION

**Q: What scope does the review claim to cover?**

| Dimension | Stated Scope |
|-----------|--------------|
| Time period | |
| Subtopics included | |
| Subtopics excluded | |
| Stated purpose | |

**Q: Is scope explicitly delimited?**
[ ] Yes - clear boundaries stated
[ ] No - scope vague or unstated

---

## RESEARCH QUESTION / PURPOSE

**Q.RQ.1: What question does this review address?**

**Q.RQ.2: What is the stated purpose?**

**Q.RQ.3: Why is this review needed?** (author's justification)

---

## KEY CLAIMS

**Q: What are the main claims made?**

| Claim # | Statement | Evidence Basis | Confidence |
|---------|-----------|----------------|------------|
| 1 | | Cited evidence / Expert opinion / Consensus | LOW |
| 2 | | Cited evidence / Expert opinion / Consensus | LOW |
| 3 | | Cited evidence / Expert opinion / Consensus | LOW |

**⚠️ For each claim, distinguish:**
- **Cited evidence**: Author cites specific studies → Extract those studies separately
- **Expert opinion**: Author's interpretation without specific citation → LOW confidence
- **Claimed consensus**: "It is widely accepted that..." → Verify independently

---

## HISTORICAL CONTEXT *(Unique contribution)*

**Q: What historical evolution does the review trace?**

| Era/Period | Key Development | Seminal Paper(s) |
|------------|-----------------|------------------|
| | | |

### Seminal Papers Identified

**Q: What papers does the author identify as foundational?**

| Paper | Year | Why Seminal (per author) | Should We Extract? |
|-------|------|--------------------------|-------------------|
| | | | Yes / Already have / Not relevant |

### Paradigm Shifts

**Q: What paradigm shifts does the author identify?**

| Shift | From | To | When | Evidence |
|-------|------|----|----- |----------|
| | | | | Documented / Author's interpretation |

---

## EXPERT INTUITIONS *(Low confidence)*

### Predictions

**Q: What predictions does the author make?**

| Prediction | Basis | Confidence |
|------------|-------|------------|
| | Expert intuition | LOW |

### Identified Gaps

**Q: What gaps does the author identify?**

| Gap | Why Important (per author) | Confidence |
|-----|---------------------------|------------|
| | | LOW (expert opinion) |

### Recommended Directions

**Q: What future directions does the author recommend?**

| Direction | Rationale | Confidence |
|-----------|-----------|------------|
| | | LOW (expert opinion) |

---

## TERMINOLOGY USAGE *(Bates)*

**Q: How does the author use key terms?**

| Term | Author's Usage | Standard Usage | Differs? |
|------|---------------|----------------|----------|
| | | | Yes / No |

**⚠️ Flag if author uses terms idiosyncratically**

---

## THEORETICAL CLAIMS

**Q: Does the author make theoretical claims?**

| Theory | Claim | Evidence Cited | Confidence |
|--------|-------|----------------|------------|
| | | | LOW unless systematic evidence |

**Q: Does the author favor particular theories?**

| Favored Theory | Evidence of Bias |
|----------------|------------------|
| | |

---

## SCOPE CONDITIONS *(Expert opinion only)*

**Q: What scope does the author imply for findings?**

| Dimension | Author's Implication | Confidence |
|-----------|---------------------|------------|
| Population | | LOW |
| Setting | | LOW |
| Temporal | | LOW |

**⚠️ Scope claims from narrative reviews should not constrain BN without corroboration**

---

## CAUSAL CLAIMS *(Expert opinion only)*

**Q: Does the author make causal claims?**

| Claim | Evidence Type | Confidence |
|-------|---------------|------------|
| | Expert synthesis / Cited experiments / Speculation | LOW unless experimental |

---

## COMPARISON TO OTHER REVIEWS

**Q: How does this compare to systematic reviews on the same topic?**

| Systematic Review | Agreement | Disagreement |
|-------------------|-----------|--------------|
| | | |

---

## OUR ASSESSMENT

**Strengths**
- [What this review does well - typically historical context, identifying seminal work]

**Limitations**
- Selection bias (author-chosen citations)
- No systematic search
- No quality assessment of cited studies
- Expert opinion ≠ systematic evidence

**Overall Confidence**: LOW (narrative review without systematic warrant)

**Value to BN**:
- [ ] Historical context only
- [ ] Identifies papers to extract systematically
- [ ] Expert synthesis to corroborate (not establish) findings
- [ ] Suggested gaps for VOI calculation

---

## Q&A SECTION

**Q: What does this review claim?**
A: [Summary] — ⚠️ Confidence: LOW

**Q: How confident should we be?**
A: LOW - This is a narrative review without systematic methodology

**Q: What is useful from this review?**
A: Historical context, seminal paper identification, expert-suggested gaps

**Q: Should claims from this review enter the BN directly?**
A: NO - Use only to identify papers for systematic extraction, or as low-confidence priors

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
# CONFIDENCE WARNING
# ============================================
confidence_warning: "Narrative review - all claims are expert synthesis without systematic warrant. Confidence is LOW unless corroborated."

# ============================================
# QUESTIONS ANSWERED
# ============================================
questions:
  ID.1_citation: ""
  ID.2_article_type: "narrative_review"
  ID.3_source_depth: ""
  RQ.1_primary_question: ""
  RQ.2_purpose: ""

# ============================================
# AUTHOR EXPERTISE
# ============================================
author:
  - name: ""
    credentials: ""
    h_index:
    expertise_area: ""
    prior_work:
      - title: ""
        year:
        relevance: "core|peripheral"
    potential_biases:
      - bias_type: ""
        evidence: ""

# ============================================
# SCOPE
# ============================================
scope:
  period_covered: ""
  subtopics_included: []
  subtopics_excluded: []
  stated_purpose: ""
  explicitly_delimited: true|false

# ============================================
# KEY CLAIMS
# ============================================
claims:
  - id: 1
    statement: ""
    evidence_basis: "cited_evidence|expert_opinion|claimed_consensus"
    citations: []
    confidence: "low"  # Always low for narrative review

# ============================================
# HISTORICAL CONTEXT (Unique)
# ============================================
historical_context:
  evolution:
    - era: ""
      development: ""
      seminal_papers: []

  seminal_papers:
    - citation: ""
      year:
      why_seminal: ""
      should_extract: true|false|already_have

  paradigm_shifts:
    - name: ""
      from: ""
      to: ""
      when: ""
      evidence: "documented|author_interpretation"

# ============================================
# EXPERT INTUITIONS (Low confidence)
# ============================================
expert_intuitions:
  predictions:
    - prediction: ""
      basis: "expert_intuition"
      confidence: "low"

  gaps:
    - gap: ""
      why_important: ""
      confidence: "low"

  recommended_directions:
    - direction: ""
      rationale: ""
      confidence: "low"

# ============================================
# TERMINOLOGY (Bates)
# ============================================
terminology:
  - term: ""
    author_usage: ""
    standard_usage: ""
    differs: true|false
    idiosyncratic: true|false

# ============================================
# THEORETICAL CLAIMS
# ============================================
theoretical_claims:
  - theory: ""
    claim: ""
    evidence_cited: ""
    confidence: "low"

favored_theories:
  - theory: ""
    evidence_of_bias: ""

# ============================================
# CAUSAL CLAIMS (Low confidence)
# ============================================
causal_claims:
  - claim: ""
    evidence_type: "expert_synthesis|cited_experiments|speculation"
    confidence: "low"

# ============================================
# RULES GENERATED
# ============================================
rules:
  # Prior rules only (low confidence)
  - rule_id: ""
    rule_type: "prior"
    description: ""
    confidence: "low"
    source: "expert_opinion"
    requires_corroboration: true

  # Gap identification for VOI
  - rule_id: ""
    rule_type: "gap"
    description: ""
    priority: ""
    source: "expert_suggestion"

# ============================================
# VALUE TO BN
# ============================================
bn_value:
  historical_context: true|false
  papers_to_extract: []
  gaps_for_voi: []
  claims_enter_bn: false  # Never directly
  use_for: "corroboration|gap_identification|historical_context"

# ============================================
# QUALITY
# ============================================
quality:
  author_expertise: "high|moderate|low"
  scope_clarity: "explicit|implicit|unclear"
  selection_bias_risk: "high"  # Always high for narrative
  overall_confidence: "low"  # Always low for narrative
```

---

## USAGE NOTES

### How to Use Narrative Review Extractions

1. **DO**: Use to identify seminal papers for systematic extraction
2. **DO**: Use historical context as factual background
3. **DO**: Use expert-suggested gaps to inform VOI search
4. **DO NOT**: Enter claims directly into BN without corroboration
5. **DO NOT**: Use as evidence for effect sizes or causal structure
6. **DO NOT**: Treat expert opinion as equivalent to systematic evidence

### Confidence Inheritance

If a finding is supported ONLY by narrative review:
- Credence: Based on expert credentials, but uncertainty HIGH
- Should be flagged for systematic verification

---

**END OF NARRATIVE REVIEW TEMPLATE**
