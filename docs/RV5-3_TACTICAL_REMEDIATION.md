# RV5-3 Tactical Remediation Plan
**Date**: 2026-02-28
**Status**: DRAFT — Ready for David's prioritization

---

## ISSUES TO FIX (Priority Order)

### P1: Direction Field Contamination

**Scope**: 5,673 findings (17.3% of corpus) have non-canonical direction values

**Non-canonical Values to Remap**:
```
'modulates' (602)           → 'unknown' or 'mixed'
'associational' (364)       → Move to claim_type; set direction='unknown'
'causal' (318)              → Move to claim_type; set direction='unknown'
'influence' (202)           → 'unknown' or 'mixed'
'descriptive' (161)         → Remove direction; mark finding as non-relational
'unclear' (128)             → 'unknown'
'significant' (106)         → 'increase' (context-dependent; manual check)
'curvilinear' (98)          → Add new field effect_shape='curvilinear'; direction='unknown'
[17 other values] (719)     → Triage manually
```

**Script Template**:
```python
# fix_direction_field.py
import json, os

canonical = {'increase', 'decrease', 'no_effect', 'mixed'}

for fname in os.listdir('data/extractions/'):
    with open(f'data/extractions/{fname}') as f:
        d = json.load(f)

    for finding in d.get('findings', []):
        direction = finding.get('direction')
        if direction not in canonical and direction:
            # Log the violation
            log_remap(fname, direction, finding)
            # Remap
            if direction in ['modulates', 'influence']:
                finding['direction'] = 'mixed'
            elif direction in ['associational', 'causal']:
                finding['claim_type'] = direction
                finding['direction'] = 'unknown'
            # ... etc
```

**Effort**: 2–3 hours scripting + 2 hours validation
**Blocking**: YES — Do this first

---

### P2: Missing Statistical Fields (Empirical Claims)

**Scope**:
- 1,688 findings with effect_size but no p_value
- 1,506 findings with p_value but no effect_size
- ~27,000 findings with no sample_size

**Root Cause**: Extraction prompt doesn't enforce "extract stats from Results section"

**Fix Strategy**:

Option A (Quick): Mark empirical claims as "statistically_incomplete = true"
- Effort: 1 hour
- Gain: Downstream systems can filter/weight appropriately
- Risk: Doesn't fix underlying problem

Option B (Proper): Re-extract from papers
- Modify extraction prompt: "For empirical studies, extract p-value, effect size, and sample size from the **Results section** (not Methods)"
- Validate: If claim_type = "empirical", require all three fields OR return null
- Effort: 8–12 hours (prompt engineering, LLM re-runs, validation)
- Gain: 62–92% improvement in statistical field completeness

**Recommendation**: Start with Option A (marking), plan Option B for next sprint

**Blocking**: MODERATE — Blocks meta-analysis use, not blocking basic corpus use

---

### P3: Over-Extraction (>50 Findings Per Article)

**Scope**: 193 articles with >50 findings each (mostly reviews/meta-syntheses)

**Examples**:
- 10.3390_s21062193.json: 183 findings (review article)
- 10.1016_j.scs.2023.104929.json: 178 findings
- Buildings_as_Habitat_Adaptive_Investments_in_Publi.json: 173 findings

**Problem**: These are flattened literature reviews, not primary empirical findings

**Fix Strategy**:

1. Classify article type first
   ```python
   def classify_article_type(title, abstract):
       review_keywords = ['review', 'systematic', 'meta-analysis', 'overview', 'survey']
       empirical_keywords = ['study', 'experiment', 'measured', 'analyzed', 'observed']
       if any(kw in title.lower() for kw in review_keywords):
           return 'review'
       elif any(kw in title.lower() for kw in empirical_keywords):
           return 'empirical'
       return 'unknown'
   ```

2. For review articles: Extract meta-claims only
   - Instead of 180 findings: "This paper reviews X studies showing that A increases B"
   - Add field: finding_type = 'meta_claim' or 'primary_result'

3. For empirical: Extract specific results as now

**Effort**: 6–8 hours (prompt engineering + validation)
**Blocking**: MODERATE — Affects corpus statistics/weighting, not blocking basic use

---

### P4: Claim Type Schema Violations

**Scope**: 22% of sample (estimated 25% of corpus) have invalid claim_type values

**Invalid Values Observed**:
- "correlational" (should be "associational")
- "observational" (should be "empirical")
- null (should default or infer)
- Other non-enum values

**Fix**: Implement enum validation at extraction time
```python
VALID_CLAIM_TYPES = {
    'empirical',
    'associational',
    'causal',
    'theoretical_proposition'
}

def validate_claim_type(finding):
    ct = finding.get('claim_type')
    if ct not in VALID_CLAIM_TYPES:
        log_error(f"Invalid claim_type: {ct}")
        finding['claim_type'] = 'unknown'  # or re-extraction
```

**Effort**: 1–2 hours
**Blocking**: LOW — Doesn't prevent use, just adds data quality flag

---

### P5: Copy-Paste & Uniform-Direction Articles

**Scope**: 31 articles where ALL findings have identical direction

**Examples**:
- 10.1016_j.jenvp.2006.12.002.json: 37 findings, all 'increase'
- of_the_Requirements_for_the_Degree.json: 9 findings, all 'no_effect'

**Problem**: Indicates either:
1. Prompt bias (systematically preferring positive findings)
2. Poor extraction (all claims from same section, not diverse)

**Fix**:
1. Flag articles with uniformity_score > 0.95 (all same direction)
2. Manual review sample (~10 articles)
3. If prompt bias confirmed: Redesign extraction prompt

**Effort**: 2–3 hours (detection + manual review)
**Blocking**: LOW — Doesn't prevent use, but quality flag important

---

## RECOMMENDED SPRINT PLAN

### Sprint 1 (This Week) — Critical Fixes
- [ ] P1: Normalize direction field (2–3 hours)
- [ ] P4: Implement claim_type enum validation (1–2 hours)
- [ ] Mark empirical claims with incomplete statistical fields (1 hour)
- [ ] Test: Re-run extraction_field_validator on fixed corpus
- **Effort**: 5–6 hours
- **Gain**: Direction field recovers from 4/10 → 9/10; claim_type 6/10 → 8/10
- **New overall score**: 4.5/10 → 5.5/10

### Sprint 2 (Next Week) — Medium Priority
- [ ] P2: Re-extract statistical fields from papers (8–12 hours)
- [ ] P3: Classify article types; re-extract review articles (6–8 hours)
- [ ] P5: Investigate uniform-direction articles (2–3 hours)
- **Effort**: 16–23 hours
- **Gain**: Statistical fields 2/10 → 6/10; Over-extraction 2/10 → 6/10
- **New overall score**: 5.5/10 → 6.5/10 (approaching production-ready)

### Sprint 3 (Planning) — Architecture
- [ ] Redesign extraction schema (4–6 hours)
- [ ] Build multi-stage validation pipeline (8–10 hours)
- [ ] Panel review (expert assessment of high-risk findings)
- **Effort**: 12–16 hours
- **Gain**: 6.5/10 → 8/10+ (production-ready with warnings)

---

## VALIDATION CHECKLIST (Post-Fix)

### Direction Field
- [ ] Zero non-canonical direction values in corpus
- [ ] All 32,819 findings use {increase, decrease, no_effect, mixed, unknown}
- [ ] Spot-check 20 random findings: manual review

### Statistical Fields (Empirical Claims)
- [ ] All empirical findings have p_value OR effect_size (not null)
- [ ] Sample: 50 empirical claims, all have ≥2 of {p_value, effect_size, sample_size}
- [ ] No more "significant" as p_value; use <0.05 or similar

### Claim Type
- [ ] 100% of claim_type values in VALID_CLAIM_TYPES enum
- [ ] No more unrecognized values

### Over-Extraction
- [ ] Article type classification complete (empirical vs. review)
- [ ] Review articles flagged; meta-claims separated from primary findings
- [ ] Maximum findings per article capped at 50 (with justification for >50)

### Copy-Paste
- [ ] All articles flagged with uniform direction reviewed manually
- [ ] No confirmed prompt bias

---

## SUCCESS METRICS

| Metric | Before | Target | Success Threshold |
|--------|--------|--------|---|
| Canonical direction values | 82.7% | 100% | 99.5% |
| Empirical claims with complete stats | 8% | 80% | 70% |
| Articles >50 findings | 18% | <5% | <8% |
| Claim type validation pass rate | 78% | 100% | 98% |
| Overall quality score | 3.5/10 | 7.5/10 | 6.5/10 |

---

## QUESTIONS FOR DAVID

1. **Re-extraction cost**: Is re-running Gemini on 1,078 papers acceptable in terms of API cost & latency?
   - Estimated cost: $50–100 (Gemini 2.0 flash pricing)
   - Estimated time: 2–4 hours (batch processing)

2. **Article type classification**: Should we use keyword heuristics (fast) or LLM-based (slow but accurate)?

3. **Panel review threshold**: If we fix critical issues, should we do expert panel review on a sample (10–20% of findings) before declaring production-ready?

4. **Backwards compatibility**: How should we handle downstream systems currently consuming the old (broken) direction field?

---

**Ready to triage with David.**
