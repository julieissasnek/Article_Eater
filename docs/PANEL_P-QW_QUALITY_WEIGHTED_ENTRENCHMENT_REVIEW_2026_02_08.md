# Panel P-QW: Quality-Weighted Entrenchment Review

**Date**: February 8, 2026
**Panel**: P-QW (Quality-Weighted Entrenchment)
**Trigger**: 6 decisions accumulated (≥5 threshold met)
**Status**: CONVENED

---

## Panel Members

| Expert | Expertise | Focus |
|--------|-----------|-------|
| Dr. Judea Pearl | Bayesian networks, causal inference | Probabilistic weighting |
| Dr. Nancy Cartwright | Philosophy of science, capacities | External validity, generalization |
| Dr. Herbert Simon | Bounded rationality, system design | Satisficing, practical trade-offs |
| Dr. Marcia Bates | Information science | Citation analysis, knowledge organization |
| Dr. Rachel Kaplan | Environmental psychology | Domain expertise for CNfA |
| Dr. Deborah Mayo | Philosophy of statistics | Severe testing, error statistics |

---

## Decisions Under Review

### Q1: Citation Thresholds

**Context**: Converting raw citation counts to entrenchment bonuses requires breakpoints. The proposed scale uses: 10, 100, 500, 1000, 2000, 3000, 5000, 10000.

**Current Choice**: 8-tier system with breakpoints at 10, 100, 500, 1K, 2K, 3K, 5K, 10K

**Alternatives**:
- Fewer tiers (5-tier: 10, 100, 1K, 5K, 20K)
- Logarithmic scale (smooth function, no discrete breakpoints)
- Field-normalized citations (percentiles rather than absolutes)

**Risk**: Absolute thresholds may disadvantage newer papers; field differences ignored.

---

### Q2: Institution Tier Assignments

**Context**: How to determine which universities are Tier 1, 2, etc. for CNFA-relevant fields.

**Current Choice**: Manual seed list of domain-relevant programs (MIT CogSci, Michigan EnvPsych, etc.)

**Alternatives**:
- Use QS/THE rankings by subject
- Citation-based analysis (which institutions produce most-cited CNFA papers)
- Ignore institution entirely (focus on paper and author metrics)

**Risk**: Manual lists become outdated; ranking services may not capture domain-specific strength.

---

### Q3: h-index Tier Boundaries

**Context**: Converting author h-index to quality contribution. Proposed boundaries: 5, 15, 30, 50, 80.

**Current Choice**: 5 tiers as specified

**Alternatives**:
- Different cutoffs (e.g., 10, 25, 50, 75, 100)
- Field-normalized h-index (percentiles within environmental psychology)
- m-quotient (h-index / years active) instead of raw h-index

**Risk**: h-index accumulates over time; may disadvantage junior researchers.

---

### Q4: Weighting of Quality Components

**Context**: Combining different quality signals into composite score.

**Current Choice**:
- Methodology: 0.25
- Citations: 0.20
- Institution: 0.15
- Author quality: 0.20
- Preregistration: 0.10
- Sample size: 0.10

**Alternatives**:
- Equal weighting (0.167 each for 6 components)
- Methodology-dominant (0.40, others split evenly)
- Evidence-based weighting (use meta-research on replication)

**Risk**: Wrong weights → over/underweight certain factors in coherence calculations.

---

### Q5: Career Stage Adjustment

**Context**: Interpreting metrics relative to career length. A paper with 500 citations from 2020 is more impressive than one from 1990.

**Current Choice**: 5/15/30 year boundaries with multipliers (1.5, 1.2, 1.0, 0.9)

**Alternatives**:
- Ignore career stage entirely (simpler)
- Citation velocity (citations per year since publication)
- Altmetric-style attention score

**Risk**: Career stage adjustment may be confounded with quality; simpler metrics may suffice.

---

### Q6: Quality → Entrenchment Mapping

**Context**: How does paper quality translate to belief entrenchment?

**Current Choice**: Linear mapping from quality [0, 1] to entrenchment [0.1, 0.7]

**Alternatives**:
- Sigmoid (S-curve) mapping (compressed extremes)
- Threshold-based (quality < 0.4 → floor entrenchment)
- Polynomial (steeper at high quality)

**Risk**: Linear may not reflect actual importance of quality differences.

---

## Panel Responses

### Dr. Judea Pearl (Causal Inference)

**On Q1 (Citation Thresholds)**:
The 8-tier system is sensible, but I'd recommend considering **citation half-life**. Fields differ in how quickly papers accumulate citations. Environmental psychology papers may take longer to reach 500 citations than machine learning papers.

However, for a Quinean web system, what matters is *relative* entrenchment within the domain. If all CNfA papers are scaled similarly, absolute thresholds are fine.

**Recommendation**: Keep the 8-tier system. Add field-calibration as optional future enhancement.

**On Q4 (Weighting)**:
The weights should reflect our uncertainty about each signal's reliability. Methodology (0.25) is appropriate because it's what we can assess directly from the paper. Citations (0.20) are a lagging indicator—good but delayed.

I'd argue for **slightly higher weight on replication status** when available. A replicated finding is qualitatively different from an original study.

**Recommendation**: Keep current weights. Add conditional weight boost when replication_status = 'replicated' (multiply entire score by 1.2 as specified).

**On Q6 (Quality → Entrenchment)**:
Linear is too simplistic. Very low-quality papers shouldn't have proportionally low entrenchment—they should have *floor* entrenchment. There's a quality threshold below which evidence is essentially worthless.

**Recommendation**: Piecewise linear with floor:
- Quality < 0.3 → entrenchment = 0.1 (floor)
- Quality 0.3-1.0 → linear from 0.15 to 0.7

---

### Dr. Nancy Cartwright (Philosophy of Science)

**On Q2 (Institution Tiers)**:
I'm skeptical of institution-based quality assessment. What matters is the *work*, not the address. Einstein at the Swiss patent office; McClintock's corn.

However, I understand the practical need for prior probabilities when detailed assessment isn't feasible. If we must use institutional proxies:

1. Use them with low weight (you have 0.15, which is acceptable)
2. Ensure manual list includes non-obvious strong programs
3. Allow paper-level override when quality is evident

**Recommendation**: Keep institutional tier but reduce weight to 0.10. Add explicit override mechanism for exceptional papers from low-tier institutions.

**On Q4 (Weighting)**:
Methodology should be higher. The capacity to generalize depends on whether the study design actually tests what it claims. Sample size and preregistration are secondary to whether the right things were measured.

**Recommendation**:
- Methodology: 0.30 (up from 0.25)
- Sample size: 0.10 (unchanged)
- Institution: 0.10 (down from 0.15)
- Other components adjust accordingly

**On Q5 (Career Stage)**:
Career stage adjustment conflates two things: (1) time for citations to accumulate, and (2) inherent quality. A brilliant early-career paper deserves recognition; a mediocre senior-career paper with lots of citations does not deserve extra credit.

**Recommendation**: Replace career stage adjustment with **citation velocity** (citations per year since publication). This directly addresses citation accumulation time without assumptions about career quality.

---

### Dr. Herbert Simon (Bounded Rationality)

**On Q1 (Citation Thresholds)**:
Eight tiers are probably more than necessary. The cognitive difference between 2000 and 3000 citations is negligible for practical purposes.

**Satisficing principle**: Use the simplest system that works. 5 tiers would likely suffice:
- Tier 0: 0-99 (minimal)
- Tier 1: 100-999 (moderate)
- Tier 2: 1000-4999 (high)
- Tier 3: 5000-9999 (major)
- Tier 4: 10000+ (foundational)

**Recommendation**: Consider 5-tier simplification. But if 8 tiers are already implemented, keep them—the cost of over-precision is low.

**On Q3 (h-index Boundaries)**:
h-index is a satisficing metric itself—it captures "enough" about career impact without being perfect. The boundaries should reflect meaningful distinctions:

- h=15 is roughly associate professor level
- h=30 is full professor with field visibility
- h=50+ is major figure

**Recommendation**: Keep current boundaries. They map reasonably to academic career stages.

**On Q4 (Weighting)**:
Weights are design decisions, not truths to be discovered. The current weights seem reasonable as a starting point. **Track outcomes** and adjust based on calibration.

**Recommendation**: Implement current weights. Add calibration tracking: compare system quality assessments to expert judgments on sample papers, adjust weights quarterly.

---

### Dr. Marcia Bates (Information Science)

**On Q1 (Citation Thresholds)**:
Citation patterns vary dramatically by field. Environmental psychology is a relatively small field; 1000 citations may be exceptional. In medicine, 1000 citations is common for review articles.

**Recommendation**: Add field calibration factor. For CNfA specifically:
- CNfA-multiplier: 2.0 (500 CNfA citations ≈ 1000 general citations)
- Apply before threshold lookup

**On Q2 (Institution Tiers)**:
The manual seed list is appropriate for domain-specific assessment. QS/THE rankings don't capture interdisciplinary strength. However, the list should be:

1. **Transparent**: Published as part of the system documentation
2. **Updatable**: Clear process for adding/modifying entries
3. **Evidence-based**: Track whether tier correlates with paper quality outcomes

**Recommendation**: Keep manual list. Publish it. Add "institution_tier_review_date" to track staleness.

**On Q4 (Weighting)**:
Sample size at 0.10 is appropriate. It matters, but it's often reported incompletely. Preregistration at 0.10 is also right—it's increasingly important but not universal in older literature.

I'd increase **methodology weight slightly** because it's the most content-focused signal.

**Recommendation**:
- Methodology: 0.28
- Citations: 0.18
- Institution: 0.14
- Author: 0.20
- Preregistration: 0.10
- Sample size: 0.10

---

### Dr. Rachel Kaplan (Environmental Psychology)

**On Q2 (Institution Tiers)**:
The seed list looks reasonable for environmental psychology. Michigan (my own institution) rightfully appears—the Attention Restoration Theory work originated there. I'd add:

- **Wageningen University** (Netherlands) - strong environmental psychology program
- **Uppsala University** (Sweden) - environmental aesthetics
- **James Cook University** (Australia) - tropical environmental psychology

**Recommendation**: Add these three to Tier 1 for environmental psychology domain.

**On Q3 (h-index)**:
Environmental psychology is a smaller field. h-index of 30 is quite senior here—Ulrich, Hartig, Kuo are in that range. h-index of 50+ is rare. The boundaries should perhaps be lower for this field:

- 5, 12, 25, 40, 60 instead of 5, 15, 30, 50, 80

**Recommendation**: Consider field-specific h-index tiers, or use lower boundaries for environmental psychology specifically.

**On Q4 (Weighting)**:
For CNfA specifically, **ecological validity should be a component**. A well-conducted field study is more valuable for architectural application than a perfectly controlled lab study.

**Recommendation**: Add ecological validity as 7th component (0.10), reduce others proportionally. Or: ecological validity moderates methodology score (lab methodology capped at 0.8 of field methodology).

---

### Dr. Deborah Mayo (Philosophy of Statistics)

**On Q4 (Weighting)**:
The weighting scheme assumes all quality signals are independent, which they're not. Author quality correlates with institution; citations correlate with journal impact. You're double-counting prestige.

**Recommendation**: Either:
1. Use only methodology + citations + sample size (more independent signals)
2. Apply explicit correlation correction
3. Use hierarchical model: prestige cluster (institution + author) and content cluster (methodology + sample + prereg)

**On Q5 (Career Stage)**:
The career stage adjustment is statistically problematic. It's trying to normalize for exposure time, but this conflates real quality differences with temporal artifacts.

**Recommendation**: Use **Scopus field-weighted citation impact** or similar normalized metric if available. Otherwise, use citation velocity (citations/year since publication) which directly addresses the temporal issue.

**On Q6 (Quality → Entrenchment)**:
Linear mapping implies equal marginal value of quality improvements across the range. This is almost certainly wrong. The difference between quality 0.3 and 0.4 should matter more than between 0.8 and 0.9.

**Recommendation**: Use inverse-logistic (compressed at extremes, steep in middle):
```
entrenchment = 0.1 + 0.6 * sigmoid((quality - 0.5) * 4)
```
This gives:
- quality 0.2 → entrenchment ~0.13
- quality 0.5 → entrenchment 0.40
- quality 0.8 → entrenchment ~0.67

---

## Panel Synthesis

### Consensus Positions

1. **Q1 (Citation Thresholds)**: 8 tiers acceptable; 5 tiers would also work. Consider field calibration for future enhancement.

2. **Q3 (h-index Boundaries)**: Current boundaries acceptable. Consider field-specific adjustment for smaller fields like environmental psychology.

3. **Q5 (Career Stage)**: Replace with **citation velocity** (citations/year since publication) per Cartwright and Mayo.

### Divided Positions

4. **Q2 (Institution Tiers)**:
   - Cartwright: Reduce weight to 0.10
   - Bates: Keep, publish list, track correlation
   - Kaplan: Add three more institutions to EnvPsych Tier 1
   - **Compromise**: Keep at 0.15, add suggested institutions, publish list with review date

5. **Q4 (Weighting)**:
   - Pearl: Keep current, boost for replication
   - Cartwright: Methodology to 0.30, institution to 0.10
   - Mayo: Restructure to avoid correlation issues
   - Kaplan: Add ecological validity
   - **Compromise**: Methodology 0.28, Citation 0.18, Institution 0.12, Author 0.18, Preregistration 0.10, Sample 0.10, Ecological Validity 0.04 (new, optional)

6. **Q6 (Quality → Entrenchment)**:
   - Pearl: Piecewise linear with floor at 0.3
   - Mayo: Sigmoid/logistic for compressed extremes
   - **Compromise**: Piecewise with floor: Quality < 0.3 → 0.10, else linear 0.15-0.70

---

## Panel Verdict

### Recommendations Summary

| Q# | Decision | Panel Verdict | Action Required |
|----|----------|---------------|-----------------|
| Q1 | Citation thresholds | APPROVE | Keep 8-tier system. Optional: add field calibration factor. |
| Q2 | Institution tiers | MODIFY | Keep at 0.12 weight. Add Wageningen, Uppsala, JCU to EnvPsych Tier 1. Publish list. |
| Q3 | h-index boundaries | APPROVE | Keep current boundaries. Document as approximation for multi-disciplinary field. |
| Q4 | Weighting | MODIFY | Adjust to: Meth 0.28, Cite 0.18, Inst 0.12, Auth 0.18, Prereg 0.10, Sample 0.10, EcoVal 0.04 |
| Q5 | Career stage | MODIFY | Replace with citation velocity (citations/year since publication). |
| Q6 | Quality→Entrenchment | MODIFY | Piecewise: Quality < 0.3 → 0.10; Quality ≥ 0.3 → linear 0.15-0.70. |

### Implementation Priority

1. **High Priority** (affects core computation):
   - Q4: Implement revised weights
   - Q5: Add citation velocity calculation
   - Q6: Implement piecewise quality→entrenchment mapping

2. **Medium Priority** (improves accuracy):
   - Q2: Add three institutions to EnvPsych Tier 1
   - Q2: Publish institution tier list as documentation

3. **Low Priority** (enhancements):
   - Q1: Field calibration factor
   - Q4: Ecological validity component (optional)

---

## Schema Changes Required

```python
# Q5: Citation velocity instead of career stage
def citation_velocity(citation_count: int, publication_year: int, current_year: int = 2026) -> float:
    """Citations per year since publication."""
    years = max(1, current_year - publication_year)
    return citation_count / years

# Q6: Piecewise quality→entrenchment
def quality_to_entrenchment(overall_quality: float) -> float:
    """Piecewise linear with floor."""
    if overall_quality < 0.3:
        return 0.10  # Floor for low-quality papers
    else:
        # Linear from 0.15 at quality=0.3 to 0.70 at quality=1.0
        return 0.15 + (overall_quality - 0.3) * (0.70 - 0.15) / (1.0 - 0.3)
```

```sql
-- Q2: Add review date to institution table
ALTER TABLE institution_quality ADD COLUMN tier_review_date TEXT;

-- Q2: Add three institutions
INSERT INTO institution_quality (institution_id, institution_name, env_psych_rank, overall_tier)
VALUES
    ('wageningen', 'Wageningen University', 1, 2),
    ('uppsala', 'Uppsala University', 1, 2),
    ('jcu', 'James Cook University', 1, 3);
```

### Revised Weights (Q4)

```python
QUALITY_WEIGHTS = {
    'methodology': 0.28,
    'citations': 0.18,
    'institution': 0.12,
    'author_quality': 0.18,
    'preregistration': 0.10,
    'sample_size': 0.10,
    'ecological_validity': 0.04  # Optional, use 0.0 if not available
}
```

---

*Panel consultation complete: February 8, 2026*
*Decisions Q1-Q6: Reviewed with modifications*
*Implementation: Lane B or separate sprint*
