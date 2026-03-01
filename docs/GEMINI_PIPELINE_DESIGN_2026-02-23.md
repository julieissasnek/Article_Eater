# Gemini Native PDF Extraction Pipeline Design

**Date**: 2026-02-23
**Version**: Draft 1.0
**Author**: Claude (with David Kirsh)

---

## 1. Executive Summary

This document proposes a new extraction pipeline using Google Gemini's native PDF reading capability. The key innovations:

1. **Native PDF reading** — Bypasses OCR/table reconstruction issues that caused 68.5% garbled extraction rate
2. **Article-type-aware prompts** — Different prompts for empirical, review, meta-analysis, theoretical, qualitative papers
3. **Multi-run verification** — 2 runs minimum, 3rd run if disagreement, to ensure field correctness

---

## 2. Why Native PDF Reading Matters

### Problem with Current Pipeline
The existing pipeline:
1. Extracts text from PDF (OCR or text layer)
2. Reconstructs tables (often fails)
3. Classifies tables
4. Extracts claims from reconstructed tables

**Failure modes:**
- OCR errors (esp. in older papers)
- Table reconstruction failures (merged cells, complex layouts)
- Loss of visual context

### Gemini Advantage
Gemini 2.5 Pro/Flash can:
- Read PDFs natively (no OCR needed)
- See tables as visual elements
- Understand context from surrounding text
- Handle complex layouts

**Test results**: 5/5 previously-garbled papers extracted successfully with Gemini.

---

## 3. Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         STAGE 0: UPLOAD                             │
│   Upload PDF to Gemini Files API → Wait for ACTIVE state           │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    STAGE 1: ARTICLE TYPE TRIAGE                     │
│   Quick classification prompt → empirical/review/meta/theoretical   │
│   Model: gemini-2.5-flash (cheap, fast)                             │
│   Output: article_type, confidence, domains[]                       │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    STAGE 2: EXTRACTION RUN 1                        │
│   Article-type-specific prompt                                      │
│   Model: gemini-2.5-pro (quality) or flash (cost)                   │
│   Output: findings[], mechanisms[], metadata                        │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    STAGE 3: EXTRACTION RUN 2                        │
│   Same prompt, different seed/temperature                           │
│   Model: same as Run 1                                              │
│   Output: findings[], mechanisms[], metadata                        │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    STAGE 4: VERIFICATION                            │
│   Compare Run 1 vs Run 2 on critical fields:                        │
│   - direction (increase/decrease/no_effect)                         │
│   - independent_variable / dependent_variable                       │
│   - p_value, effect_size                                            │
│                                                                     │
│   If AGREE → merge with high confidence                             │
│   If DISAGREE → trigger Run 3                                       │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                          ┌────────┴────────┐
                          │   DISAGREE?     │
                          └────────┬────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
┌─────────────────────────────┐   ┌─────────────────────────────────┐
│     STAGE 5a: RUN 3         │   │    STAGE 5b: MERGE & OUTPUT     │
│  Tie-breaker extraction     │   │    Consensus merge              │
│  Model: gemini-2.5-pro      │   │    Output: verified findings    │
│  Higher temp or diff model  │   │                                 │
└─────────────────────────────┘   └─────────────────────────────────┘
                    │                             │
                    └──────────────┬──────────────┘
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    STAGE 6: POST-PROCESSING                         │
│   - Map variables to vocabulary (canonical IV/DV)                   │
│   - Convert effect sizes to Cohen's d                               │
│   - Apply quality thresholds                                        │
│   - Flag uncertain claims for review                                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. Article-Type-Specific Prompts

### 4.1 Prompt Selection Logic

```python
PROMPT_MAP = {
    "empirical_v2": EMPIRICAL_PROMPT,
    "observational_field": EMPIRICAL_PROMPT,
    "case_study": EMPIRICAL_PROMPT,
    "mixed_methods": MIXED_METHODS_PROMPT,

    "meta_analysis": META_ANALYSIS_PROMPT,
    "systematic_review": SYSTEMATIC_REVIEW_PROMPT,
    "narrative_review": NARRATIVE_REVIEW_PROMPT,

    "theoretical": THEORETICAL_PROMPT,
    "conceptual_framework": THEORETICAL_PROMPT,
    "thought_piece": THEORETICAL_PROMPT,

    "interview_study": QUALITATIVE_PROMPT,
    "ethnographic": QUALITATIVE_PROMPT,
    "grounded_theory": QUALITATIVE_PROMPT,
    "phenomenological": QUALITATIVE_PROMPT,
}
```

### 4.2 Empirical Study Prompt

```
Extract all statistical findings from this empirical study.

For EACH finding, extract:
- antecedent: The independent variable / causal factor
- consequent: The dependent variable / outcome
- direction: "increase" | "decrease" | "no_effect"
- measure_type: "physiological" | "behavioral" | "self_report" | "cognitive"
- statistics:
  - p_value: exact value or "<0.05" etc.
  - effect_size: numeric value
  - effect_size_type: "Cohen_d" | "r" | "eta_squared" | "beta" | "odds_ratio"
  - sample_size: N
  - ci_lower, ci_upper: confidence interval bounds (if available)
- source: table_id or "text" with page number
- quote: exact text supporting this finding

CRITICAL RULES:
1. Extract EVERY distinct finding, even if null/non-significant
2. For non-significant results, set direction = "no_effect"
3. For regression tables: predictors are antecedents, criterion is consequent
4. For correlation matrices: extract each significant cell as a finding
5. Include exact quotes to anchor each finding

Return JSON array of findings.
```

### 4.3 Meta-Analysis Prompt

```
Extract all pooled effects and heterogeneity findings from this meta-analysis.

For EACH pooled effect, extract:
- antecedent: The intervention/exposure
- consequent: The outcome
- direction: "increase" | "decrease" | "no_effect"
- pooled_effect:
  - effect_size: numeric value
  - effect_size_type: "SMD" | "OR" | "RR" | "r" | "d"
  - ci_lower, ci_upper: confidence interval
  - p_value: significance
  - k: number of studies
  - total_n: combined sample size
- heterogeneity:
  - I_squared: percentage
  - Q_statistic: chi-square value
  - Q_p_value: significance of heterogeneity
- moderators: list of significant moderating variables
- source: table or forest plot reference

CRITICAL RULES:
1. Extract EACH subgroup analysis separately
2. Note publication bias indicators (funnel plot, Egger's test)
3. Include sensitivity analyses if reported
4. For network meta-analyses, extract each comparison

Return JSON array of pooled effects.
```

### 4.4 Review Article Prompt

```
Extract all synthesized findings and cited claims from this review article.

For EACH key finding, extract:
- antecedent: The causal/independent factor
- consequent: The outcome/dependent factor
- direction: "increase" | "decrease" | "mixed" | "unclear"
- evidence_strength: "strong" | "moderate" | "weak" | "emerging"
- n_studies: approximate number of studies supporting this
- source_citations: list of key citations mentioned
- mechanisms: theoretical explanations proposed
- quote: text where this finding is stated

CRITICAL RULES:
1. Distinguish between findings the review REPORTS vs. PROPOSES
2. Note when evidence is conflicting (direction = "mixed")
3. Extract proposed mechanisms/theories separately
4. Include limitations and gaps identified

Return JSON with:
- findings: array of synthesized findings
- mechanisms: array of theoretical explanations
- gaps: array of identified research gaps
```

### 4.5 Theoretical Paper Prompt

```
Extract the theoretical propositions and testable hypotheses from this paper.

Extract:
- central_proposition: The main theoretical claim
- concept_definitions: key terms and their definitions
- causal_claims: proposed relationships
  - antecedent: cause/predictor
  - consequent: effect/outcome
  - direction: "increase" | "decrease" | "modulates"
  - mechanism: explanation of how/why
  - testable: true | false
- bridge_warrants: links between this theory and empirical phenomena
- derived_hypotheses: specific testable predictions

CRITICAL RULES:
1. This is THEORY, not empirical findings - no p-values expected
2. Note the LEVEL of each claim (theory, mechanism, prediction)
3. Identify any empirical evidence cited to support claims
4. Extract explicit hypotheses that could be tested

Return JSON with propositions, mechanisms, and hypotheses.
```

### 4.6 Qualitative Study Prompt

```
Extract themes, constructs, and evidence from this qualitative study.

For EACH theme/finding, extract:
- theme: The named theme or construct
- description: What this theme means
- antecedents: contributing factors (if identified)
- consequences: outcomes (if identified)
- supporting_quotes: array of participant quotes
- transferability: contexts where this might apply
- saturation: whether this theme was saturated

Also extract:
- methodology: interview/ethnography/grounded theory etc.
- sample: participant description
- analysis_approach: coding method used

CRITICAL RULES:
1. Use IN VIVO codes where provided
2. Note researcher interpretations vs. participant voice
3. Include negative cases / disconfirming evidence
4. Note reflexivity considerations

Return JSON with themes array and methodology metadata.
```

---

## 5. Multi-Run Verification Logic

### 5.1 Rationale

LLM extraction is non-deterministic. Critical fields like **direction** (increase/decrease/no_effect) must be verified because:
- Wrong direction = wrong causal claim = corrupted knowledge base
- Effect sizes and p-values must be accurately transcribed
- Variable names must consistently map to vocabulary

### 5.2 Verification Algorithm

```python
def verify_extractions(run1: list, run2: list) -> VerificationResult:
    """Compare two extraction runs and determine agreement."""

    CRITICAL_FIELDS = ["antecedent", "consequent", "direction"]
    IMPORTANT_FIELDS = ["p_value", "effect_size", "sample_size"]

    # Match findings between runs (by antecedent+consequent pair)
    matched_pairs = match_findings(run1, run2)

    agreements = []
    disagreements = []

    for finding1, finding2 in matched_pairs:
        # Check critical fields
        critical_agree = all(
            normalize(finding1.get(f)) == normalize(finding2.get(f))
            for f in CRITICAL_FIELDS
        )

        # Check important fields (with tolerance for numerics)
        important_agree = all(
            values_match(finding1.get(f), finding2.get(f), tolerance=0.01)
            for f in IMPORTANT_FIELDS
        )

        if critical_agree and important_agree:
            agreements.append(merge_findings(finding1, finding2))
        else:
            disagreements.append({
                "finding1": finding1,
                "finding2": finding2,
                "disagreement_fields": identify_disagreements(finding1, finding2)
            })

    return VerificationResult(
        agreed_findings=agreements,
        disagreed_findings=disagreements,
        needs_run3=len(disagreements) > 0,
        agreement_rate=len(agreements) / len(matched_pairs)
    )
```

### 5.3 Run 3 Tie-Breaking

When disagreement occurs:

**Option A: Majority Vote**
```python
def run3_majority_vote(finding1, finding2, finding3, field):
    """Take majority vote across 3 runs."""
    values = [finding1.get(field), finding2.get(field), finding3.get(field)]
    return Counter(values).most_common(1)[0][0]
```

**Option B: Higher-Quality Model**
```python
# Run 3 uses gemini-2.5-pro even if runs 1-2 used flash
# Or use a different provider (Claude, GPT-4o) for independence
```

**Option C: Targeted Re-extraction**
```python
# Only re-extract the specific disagreed findings
# Use a more explicit prompt: "Is the effect increase, decrease, or no effect?"
```

### 5.4 Verification Thresholds

| Field | Agreement Method | Tolerance |
|-------|-----------------|-----------|
| direction | Exact match | None |
| antecedent | Normalized string match | Levenshtein < 0.2 |
| consequent | Normalized string match | Levenshtein < 0.2 |
| p_value | Numeric with tolerance | ±0.005 |
| effect_size | Numeric with tolerance | ±0.05 |
| sample_size | Numeric with tolerance | ±5% |

---

## 6. Cost Analysis

### 6.1 Per-Paper Costs

| Stage | Model | Input Tokens | Output Tokens | Cost |
|-------|-------|--------------|---------------|------|
| Triage | flash | ~500 | ~100 | $0.0001 |
| Run 1 | pro | ~20,000 | ~5,000 | $0.075 |
| Run 2 | pro | ~20,000 | ~5,000 | $0.075 |
| Run 3 (if needed) | pro | ~20,000 | ~5,000 | $0.075 |

**Total per paper**: $0.15 - $0.23 (depending on Run 3)

### 6.2 Batch API Discount

Gemini Batch API offers 50% discount:
- **With batch**: $0.075 - $0.115 per paper
- For 500 papers: $37.50 - $57.50

### 6.3 Cost Optimization

1. **Use Flash for simple papers**: Papers with <5 tables → flash only ($0.02)
2. **Skip Run 3 when agreement is high**: >90% field agreement → trust merge
3. **Cache uploaded PDFs**: Reuse file_uri within 48 hours

---

## 7. Implementation Plan

### Phase 1: Core Pipeline (Week 1)
- [ ] Create `GeminiExtractor` class with native PDF support
- [ ] Implement article-type triage prompt
- [ ] Create 5 article-type-specific extraction prompts
- [ ] Basic two-run extraction with comparison

### Phase 2: Verification Logic (Week 2)
- [ ] Implement finding matching algorithm
- [ ] Build field comparison with tolerances
- [ ] Create Run 3 tie-breaker logic
- [ ] Add confidence scoring to output

### Phase 3: Integration (Week 3)
- [ ] Connect to existing vocabulary mapping
- [ ] Integrate with database storage
- [ ] Add quality threshold filtering
- [ ] Create batch processing mode

### Phase 4: Validation (Week 4)
- [ ] Run against gold standard papers
- [ ] Measure precision/recall vs. manual extraction
- [ ] Compare to legacy pipeline results
- [ ] Document failure modes

---

## 8. Open Questions for Expert Panel

### Q1: Verification Strategy
Should Run 2 use:
- Same model, different temperature (0.1 vs 0.3)?
- Same model, different prompt ordering?
- Different model entirely (flash vs pro)?

### Q2: Disagreement Threshold
What level of disagreement triggers Run 3?
- Any disagreement on direction?
- >10% of findings disagree?
- Only statistical value disagreements?

### Q3: Ground Truth
How do we establish ground truth for verification testing?
- Manual extraction by domain experts?
- Consensus across multiple human coders?
- Use existing gold_standard/ directory?

### Q4: Batch vs. Real-time
Should verification run:
- Synchronously (wait for all runs)?
- Asynchronously (batch overnight)?
- Hybrid (real-time for urgent, batch for bulk)?

---

## 9. Appendix: File Structure

```
src/extraction/
├── gemini_pipeline.py       # NEW: Main pipeline orchestrator
├── gemini_extractor.py      # NEW: Gemini API wrapper
├── gemini_prompts.py        # NEW: Article-type-specific prompts
├── verification.py          # NEW: Multi-run verification logic
├── finding_matcher.py       # NEW: Cross-run finding alignment
│
├── claim_extractor.py       # EXISTING: Keep for vocabulary mapping
├── paper_triage.py          # EXISTING: Augment with LLM triage
├── article_type_contract.py # EXISTING: Field contracts
└── vocabulary.py            # EXISTING: IV/DV vocabulary
```

---

## 10. Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Direction accuracy | >95% | vs. gold standard |
| Variable mapping accuracy | >90% | vs. vocabulary |
| Effect size accuracy | >98% | vs. manual check |
| Run agreement rate | >85% | Run 1 vs Run 2 |
| Cost per paper | <$0.20 | with verification |
| Processing time | <3 min | per paper |

---

*End of Design Document*
