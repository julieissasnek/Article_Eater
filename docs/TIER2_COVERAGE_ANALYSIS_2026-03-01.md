# Tier2 Coverage Analysis — Session 2026-03-01

**Date**: 2026-03-01
**Status**: Diagnostic complete — root cause identified
**Author**: Claude Code (CW)

---

## Executive Summary

The AESHI "annotation debt" is not actually a debt of missing annotations. **All 3,420 beliefs ARE annotated** with epistemic_v2 data. The real issue is **low template matching coverage**: only 807/3,420 beliefs (23.6%) achieve sufficient template match scores (≥0.45) to be assigned Tier2 frameworks.

This is a **finding quality problem**, not an annotation infrastructure problem.

---

## Current State

### Database Inspection Results

**From `web_persistence_v2.db` (as of 2026-03-01 02:29 UTC)**:

| Metric | Value | Status |
|--------|-------|--------|
| Total beliefs | 3,420 | ✅ |
| Beliefs with epistemic_v2 column | 3,420 | ✅ 100% |
| Beliefs with non-null epistemic_v2 | 3,420 | ✅ 100% |
| Beliefs with non-empty epistemic_v2 | 3,420 | ✅ 100% |
| Beliefs with template_relevance_v1 key | 3,420 | ✅ 100% |
| Beliefs with Tier1 relevance (any) | 3,420 | ✅ 100% |
| Beliefs with Tier2 relevance (any) | 3,420 | ✅ 100% |
| **Beliefs with non-empty Tier2 relevance** | **807** | ⚠️ **23.6%** |

### Template Matching Breakdown

**Resolution Statistics** (from `data/production/finding_template_theory_links.json`):

```
findings_total                    3,420
findings_with_template_candidates 3,017  (88.2% have at least 1 candidate)
findings_with_tier1_relevance       964  (28.2% inferred Tier1 from claim)
findings_with_tier2_relevance       807  (23.6% assigned Tier2 frameworks)

unique_templates_linked              80  (out of 208 total)
unique_tier2_frameworks_linked       45  (out of how many total?)
candidate_template_links_total   12,120  (avg 3.5 per finding)
```

### The Coverage Gap

- **Findings with Tier2 matches**: 807/3,420 = **23.6%**
- **Findings without Tier2 matches**: 2,613/3,420 = **76.4%**
- **AESHI target**: 90%
- **Gap to close**: 67.4 percentage points

---

## Root Cause Analysis

### The Template Matching Pipeline

When the finding_template_relevance script runs, for each of the 3,420 beliefs:

1. **Score all 208 templates** against the finding (environment + outcome)
2. **Keep candidates with score ≥ 0.35** (min_template_score)
3. **Top-k ranking** by score (up to 5 templates per finding)
4. **Extract Tier1 frameworks** from top candidates with score ≥ 0.45 (min_tier_support_score)
5. **Extract Tier2 frameworks** from template profiles of qualifying candidates

**Current Results**:
- Step 2: 3,017/3,420 findings (88.2%) get at least one candidate (score ≥ 0.35)
- Step 4: Only 807/3,420 findings (23.6%) qualify for Tier2 (have candidates with score ≥ 0.45)

### Why Tier2 Matching is Low

The template matching algorithm (`_score_template_for_finding()`) computes:

```
score = 0.25 * environment_score +
        0.25 * outcome_score +
        0.30 * bridge_score +
        0.08 * mechanism_overlap +
        domain_multiplier
```

For a candidate to qualify for Tier2, it must reach **0.45 out of 1.0** — a fairly high bar.

**Problems**:
1. **Insufficient finding metadata**: Many findings lack explicit environment_id or outcome_id, or have vague antecedent/consequent text
2. **Narrow template library**: Only 80 templates are well-calibrated enough to match diverse findings. Many finding types (methodological, behavioral, sensory) don't have corresponding templates
3. **Threshold too high**: The 0.45 threshold may be overly conservative. Only ~23% of matches reach it

### Evidence from COORDINATION.md

From latest AESHI diagnosis:
- Tier2 coverage 23.6% (target 90%) — confirmed
- Infrastructure healthy: 88.2% template matching, 45 frameworks, 12,120 candidate links — confirmed
- Annotation debt described as "116 annotated beliefs vs 3,420 findings" — **INACCURATE**. All 3,420 are annotated; only 116 had prior manual verification before this session.

---

## Solution Options

### Option A: Improve Finding Quality (Upstream Fix)

**Approach**: Re-extract articles using improved v3 prompts to generate findings with better antecedent/consequent alignment.

**Pros**:
- Fixes root cause (poor finding quality)
- Provides better data for downstream systems
- Aligns with Phase 2 of Extraction Pipeline Overhaul already in flight

**Cons**:
- Labor-intensive (AG must re-extract 1,043 articles)
- Requires new extraction infrastructure (Gemini batch runner)
- Takes ~8 hrs estimated for Tier 1 (59 articles) + additional for full corpus

**Implementation**:
- H9 (Tier 1 re-extraction, 59 zero-finding articles) — READY
- H3 expansion (re-extract all 1,043 with v3 prompts) — NEW proposal

**Expected Impact**: Could raise matching from 23.6% → 60%+ if findings are more template-aligned.

### Option B: Broaden Template Library (Horizontal Expansion)

**Approach**: Create new domain-specific templates for underrepresented finding types.

**Pros**:
- Directly increases coverage
- No re-extraction needed

**Cons**:
- Requires significant new template development
- Domain expertise needed for each new template
- Resource-intensive (estimated 40-60 hrs)

**Not Recommended**: Lower impact per hour than Option A.

### Option C: Lower the Threshold (Quick Fix)

**Approach**: Reduce `min_tier_support_score` from 0.45 to (e.g.) 0.35.

**Pros**:
- Immediate effect (could reach 90% coverage)
- Requires only 1-line code change + 1 re-run

**Cons**:
- Lowers quality of Tier2 matches
- Increases false-positive template assignments
- Violates the principle that Tier2 should be high-confidence

**Not Recommended**: Trades quality for quantity; violates system integrity.

### Option D: Hybrid (Recommended)

**Approach**: Combine Option A + pragmatic threshold adjustment.

1. Lower `min_tier_support_score` from 0.45 → 0.40 (modest)
2. Run H9 (re-extract 59 zero-finding articles)
3. Monitor coverage improvement
4. If still <80%, expand H9 to full corpus re-extraction
5. Develop templates for highest-error finding types

**Expected Timeline**:
- Weeks 1-2: H9 re-extraction (59 articles)
- Week 3: Threshold adjustment + coverage re-measurement
- Weeks 4+: Full re-extraction if needed

**Expected Impact**: Could reach 70-85% coverage; combined with Phase 2 of pipeline overhaul.

---

## Data-Driven Recommendations

### Immediate Actions (CW, Session 2026-03-01)

1. ✅ **Diagnosis complete**: Tier2 coverage is 23.6% due to finding-template mismatch, not missing annotations
2. **Update COORDINATION.md**: Clarify that "annotation debt" is a misnomer; real issue is template matching
3. **Recommend to AG**: Prioritize H9 (Tier 1 re-extraction) + full extraction overhaul (Phase 2)
4. **Consider**: Threshold adjustment (0.45 → 0.40) after H9, re-measurement needed

### Medium-term (2-3 weeks, AG)

- Execute H9 (59 zero-finding articles with v3 prompts)
- Re-run finding_template_relevance.py
- Re-measure Tier2 coverage
- If <80%, expand to full 1,043 article re-extraction

### Long-term (4+ weeks)

- Phase 2 of Extraction Pipeline Overhaul (comprehensive improvements)
- Develop templates for underrepresented domains
- Refine matching algorithm thresholds based on empirical data

---

## Misconceptions Clarified

| Misconception | Reality |
|---------------|---------|
| "Only 116 beliefs are annotated" | All 3,420 have epistemic_v2 annotations with template_relevance_v1 data |
| "Annotation persistence is broken" | Persistence works 100%; all beliefs successfully store Tier1 + Tier2 data |
| "We need to manually annotate 900+ beliefs" | No; we need to re-extract findings to improve template matching |
| "Tier2 coverage is 0%" | It's 23.6% (807 beliefs); progress is real but insufficient |
| "The issue is in the database layer" | The issue is in template matching algorithm inputs (finding quality) |

---

## Files for Reference

| File | Purpose | Key Data |
|------|---------|----------|
| `data/web_persistence_v2.db` | Source database | 3,420 beliefs with epistemic_v2 |
| `data/production/finding_template_theory_links.json` | Template matching output | 807 Tier2 matches (23.6%) |
| `src/services/finding_template_relevance.py` | Matching algorithm | Lines 749-807, threshold = 0.45 |
| `scripts/run_finding_template_relevance.py` | CLI runner | --persist-to-web-db flag |
| `docs/EXTRACTION_FIELD_QUALITY_FRAMEWORK_2026-02-28.md` | Quality rules | 50+ field validation rules |

---

## Next Steps

CW to:
1. Update COORDINATION.md with accurate diagnosis ✅
2. Add this analysis to decision log (D-CW-2026-03-01)
3. Recommend H9 + Phase 2 extraction overhaul to AG

AG to review and execute H8-H10 per COORDINATION.md priorities.
