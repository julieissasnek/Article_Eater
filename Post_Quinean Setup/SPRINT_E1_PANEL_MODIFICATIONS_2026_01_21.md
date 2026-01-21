# Sprint E1 Panel Modifications Implementation

**Date**: January 21, 2026
**Status**: COMPLETE
**Total Tests**: 151 passing (across 4 test files)

## Summary

This document captures the modifications implemented per expert panel review of Sprint E1 decisions.

---

## E1.D4: Confounder Coverage Gap Detection (HIGH Priority)

**Panel Verdict**: MODIFY

**Implementation**:
1. **Expanded keyword list per Pearl**:
   - Added: `propensity score`, `instrumental variable`, `difference-in-differences`, `regression discontinuity`, `matching`, `stratified`, `blocked`, `within-subjects`

2. **Added domain-specific confounders per Cartwright**:
   - Added: `socioeconomic`, `self-selection`, `building age`, `climate`, `latitude`

3. **Added environmental psychology terms per Kaplan**:
   - Added: `baseline`, `pre-post`, `seasonal`, `seasonality`

4. **Implemented severity weighting**:
   - `CRITICAL`: Abstract-only causal claim, no confounder mention
   - `WARNING`: Full-text causal claim, no confounder mention
   - `INFO`: Associational claim, no confounder mention

**Files Modified**:
- `src/services/reporting.py`: Added `_get_confounder_keywords()`, `_get_confounder_gap_severity()`, `_find_causal_without_confounders_with_severity()`

**Tests Added**: 11 tests in `tests/test_reporting.py`

---

## E1.D5: Three-Tier Causal Classification (HIGH Priority)

**Panel Verdict**: MODIFY

**Implementation**:

### 1. Restructured tier logic per Pearl (design-first approach)
```
IF experimental_design THEN
    IF causal_language THEN CAUSAL (high confidence)
    ELIF suggestive_language THEN CAUSAL (medium confidence)
    ELSE ASSOCIATIONAL
ELIF quasi_experimental THEN
    IF causal_language THEN CAUSAL (medium-high confidence)
    ELIF suggestive_language THEN SUGGESTIVE (high confidence)
    ELSE SUGGESTIVE
ELIF causal_language AND (mechanism OR confounder_control) THEN CAUSAL
ELIF causal_language THEN SUGGESTIVE (per Simon: keep 3 tiers)
ELIF suggestive_language THEN SUGGESTIVE
ELSE ASSOCIATIONAL
```

### 2. Removed mechanism as confidence booster per Cartwright
- Mechanism is now a separate indicator (`mechanism_mentioned`)
- Provides plausibility, not causation
- Does NOT boost confidence score

### 3. Added quasi-experimental detection per Pearl
- New patterns: `natural experiment`, `quasi-experimental`, `regression discontinuity`, `difference-in-differences`, `propensity score`, `instrumental variable`, `matched sample`, `before-after`, `pre-post design`, `interrupted time series`
- New field: `is_quasi_experimental` on `CausalClassification`

### 4. Added neuroarchitecture patterns per Kaplan
- **CAUSAL**: `design intervention`, `built environment manipulation`, `lighting intervention`, `architectural intervention`, `environmental manipulation`
- **SUGGESTIVE**: `restorative effect`, `restorative environment`, `biophilic response`, `attention restoration`, `stress recovery`
- **ASSOCIATIONAL**: `preference for`, `preferred`, `rated higher/lower/as`, `rating study`, `subjective assessment`

**Files Modified**:
- `src/services/causal_classifier.py`: Major restructuring of `classify()` and new `_determine_tier_pearl()` method

**Tests Updated**: 49 tests in `tests/test_causal_classifier.py`

---

## E1.D2: Contested Evidence Structure (MEDIUM Priority)

**Panel Verdict**: MODIFY

**Implementation**:

### 1. Revised contested detection logic per Pearl
- **OLD**: Used credence threshold (≥0.5 = supporting, <0.5 = contradicting)
- **NEW**: Uses directional opposition (X increases Y vs X decreases Y)

**Rationale** (Pearl): Credence represents belief strength, not support/contradiction. A belief with credence 0.45 might still *support* a claim—it's just uncertain.

### 2. Added directional opposition detection
- New method: `_get_causal_direction()` detects positive/negative/neutral direction
- Positive terms: increase, improve, enhance, boost, beneficial, etc.
- Negative terms: decrease, reduce, diminish, impair, harmful, etc.
- Handles negation terms

### 3. Added measurement method differences per Cartwright
- Detects self-report vs physiological measurement differences
- Keywords: `self-report`, `questionnaire`, `subjective` vs `cortisol`, `heart rate`, `EEG`, `fMRI`
- Added to reasons for disagreement

### 4. Added temporal differences per Kaplan
- Detects short-term vs long-term study differences
- Added to reasons for disagreement

**Files Modified**:
- `src/services/query_response.py`: Added `_get_causal_direction()`, `_has_directional_opposition()`, updated `_identify_disagreement_reasons()`

**Tests Added**: 5 new tests in `TestDirectionalOpposition` class

---

## E1.D3: Taxonomy-Driven Outcomes (LOW Priority)

**Panel Verdict**: APPROVE with minor change

**Implementation**:
- Added `physio.stress` to fallback outcomes (distinct from `affect.stress`)
- Per Kaplan: Physiological stress measures are distinct from affect.stress

**Files Modified**:
- `src/services/reporting.py`: Updated `_FALLBACK_OUTCOME_CATEGORIES`

---

## Test Summary

| Test File | Tests | Status |
|-----------|-------|--------|
| test_causal_classifier.py | 49 | PASS |
| test_reporting.py | 44 | PASS |
| test_query_response.py | 33 | PASS |
| test_query_routes.py | 25 | PASS |
| **Total** | **151** | **PASS** |

---

## Files Modified

| File | Changes |
|------|---------|
| `src/services/causal_classifier.py` | Pearl restructure, quasi-experimental, neuroarch patterns |
| `src/services/query_response.py` | Directional opposition, measurement method differences |
| `src/services/reporting.py` | Expanded confounders, severity weighting, physio.stress |
| `tests/test_causal_classifier.py` | Updated for Pearl logic, added quasi-exp and neuroarch tests |
| `tests/test_query_response.py` | Added directional opposition tests |
| `tests/test_reporting.py` | Added severity weighting and expanded keyword tests |

---

## Panel Recommendations Status

| Decision | Panel Verdict | Implementation Status |
|----------|---------------|----------------------|
| E1.D1 | APPROVE | No changes needed |
| E1.D2 | MODIFY | COMPLETE |
| E1.D3 | APPROVE (minor) | COMPLETE |
| E1.D4 | MODIFY | COMPLETE |
| E1.D5 | MODIFY | COMPLETE |

---

## Deferred Items (for future sprints)

Per panel recommendation:
- E1.D2 controversy severity indicator
- E1.D2 vocabulary comparison between opposing sides
- E1.D5 four-tier consideration (kept 3 per Simon)
