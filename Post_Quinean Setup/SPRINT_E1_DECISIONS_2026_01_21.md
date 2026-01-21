# Sprint E1 Implementation Decisions for Panel Review

**Date**: January 21, 2026
**Sprint**: E1 (Panel HIGH Priority Implementations)
**Total Tests**: 136 passing

## Summary

Sprint E1 implemented the 5 HIGH priority items from the expert panel review of Phases C-D. This document captures the autonomous design decisions made during implementation for future panel review.

---

## Implementation Summary

| Item | Description | New Tests | Status |
|------|-------------|-----------|--------|
| H4 | Clickable follow-up queries | 4 | Complete |
| H5 | Contested evidence section | 6 | Complete |
| H2 | Outcome categories from taxonomy | 5 | Complete |
| H3 | Confounder coverage gap | 7 | Complete |
| H1 | Three-tier causal classifier | 43 | Complete |

---

## Decision Points for Future Review

### E1.D1: Follow-up Type Nomenclature Change

**Decision**: Changed second follow-up type from "broader" to "scope"

**Rationale**: Per Cartwright/Simon panel compromise. "Scope" better captures the intention of understanding boundary conditions (when/for whom the effect applies) rather than simply broader exploration.

**Implementation**:
- `src/services/query_response.py`: Updated `_generate_follow_ups()`
- Follow-up now asks "Under what conditions does X affect Y?" instead of broader questions

**Panel Review Needed**: Confirm "scope" is the right term. Alternative: "boundary" or "conditions"

---

### E1.D2: Contested Evidence Structure

**Decision**: Created `ContestedEvidence` dataclass with grouped supporting/contradicting evidence plus "reasons for disagreement" field

**Rationale**: Per Cartwright/Simon - epistemic transparency requires showing controversy prominently

**Implementation**:
- `src/services/query_response.py`: Added `ContestedEvidence` dataclass
- Includes: `topic`, `supporting`, `contradicting`, `summary`, `reasons_for_disagreement`
- Section only appears when `is_contested=True` OR when there are both supporting (credence≥0.5) and contradicting (credence<0.5) beliefs

**Decisions made autonomously**:
1. Credence threshold of 0.5 for supporting vs contradicting classification
2. Maximum of 5 evidence items per side in the contested section
3. Reasons for disagreement are inferred from: source depth differences, population scope differences, methodology keywords (lab vs field)

**Panel Review Needed**:
- Is 0.5 the right threshold for support vs contradict?
- Should more reasons for disagreement be added (e.g., temporal differences, geographic differences)?

---

### E1.D3: Taxonomy-Driven Outcomes

**Decision**: Get expected outcome categories dynamically from `ExtendedOutcomeTaxonomy` instead of hardcoding

**Rationale**: Per Kaplan - outcomes should evolve with the taxonomy

**Implementation**:
- `src/services/reporting.py`: Added `_get_expected_outcomes()` method
- Falls back to hardcoded set if taxonomy import fails
- Includes domains and immediate children (depth ≤ 2)

**Decisions made autonomously**:
1. Fallback outcomes: `behav.productivity`, `cog.performance`, `affect.stress`, `health.wellbeing`, `health`, `cog.attention`, `affect.mood`
2. Taxonomy depth limit of 2 (domain + immediate children)
3. Reports now indicate whether outcomes came from "taxonomy" or "fallback" source

**Panel Review Needed**:
- Should depth be configurable?
- Are the fallback outcomes appropriate?

---

### E1.D4: Confounder Coverage Gap Detection

**Decision**: Added gap type for causal claims that don't acknowledge confounders

**Rationale**: Per Pearl - causal claims should acknowledge potential confounders for validity

**Implementation**:
- `src/services/reporting.py`: Added `_find_causal_without_confounders()` method
- Keywords checked: `confounder`, `confounding`, `controlled for`, `adjusted for`, `covariate`, `mediator`, `moderator`, `held constant`, `accounted for`, `independent of`, `after adjusting`, `after controlling`, `net of`, `spurious`, `third variable`

**Decisions made autonomously**:
1. Keyword-based detection (same as causal claim detection)
2. Only applies to beliefs already classified as causal claims
3. Gap report includes belief IDs for tracking

**Panel Review Needed**:
- Are the confounder keywords comprehensive?
- Should this be weighted by source depth (abstract-only claims more concerning)?

---

### E1.D5: Three-Tier Causal Classification

**Decision**: Created `CausalClassifier` service with CAUSAL/SUGGESTIVE/ASSOCIATIONAL tiers

**Rationale**: Per Pearl - distinguish causal from correlational evidence explicitly

**Implementation**:
- New file: `src/services/causal_classifier.py` (400+ lines)
- Three tiers with confidence scores and evidence types
- Pattern-based classification with context modifiers

**Key Pattern Categories**:

1. **CAUSAL patterns** (strong causal language):
   - `causes`, `results in`, `leads to`, `produces`, `determines`
   - Experimental language: `randomized`, `RCT`, `intervention`, `treatment effect`
   - `causal effect`, `causal mechanism`, `causal pathway`

2. **SUGGESTIVE patterns** (moderate causal language):
   - `affects`, `impacts`, `influences`, `improves`, `reduces`, `increases`, `decreases`
   - Hedged: `may cause`, `might cause`, `appears to affect`, `suggests that...affects`

3. **ASSOCIATIONAL patterns** (correlational language):
   - `correlated with`, `associated with`, `related to`, `linked to`
   - Observational: `observed that`, `noted that`, `found that`

**Decisions made autonomously**:

1. **Hedged causal language handling**: Phrases like "may cause" are classified as SUGGESTIVE, not CAUSAL. Implemented `_has_hedged_causal_language()` check.

2. **Experimental context boost**: Experimental context (RCT, randomized) can upgrade SUGGESTIVE to CAUSAL tier.

3. **Confidence scoring formula**:
   - CAUSAL: base 0.6 + (causal_count * 0.4) + experimental_boost(0.3) + mechanism_boost(0.1)
   - SUGGESTIVE: base 0.5 + (suggestive_count * 0.25)
   - ASSOCIATIONAL: base 0.5 + (associational_count * 0.2)
   - All capped at 0.95

4. **Warning generation**:
   - Warns for causal claims without confounder acknowledgment
   - Warns for causal claims from abstract-only sources
   - Warns for causal language in observational studies
   - Warns for mixed causal/correlational language

5. **Mechanism detection**: Checks for mechanism keywords (pathway, mediated by, via) to boost confidence

**Panel Review Needed**:
- Are the tier definitions appropriate?
- Should confidence weights be configurable?
- Are there domain-specific patterns that should be added for neuroarchitecture?
- How should "quasi-experimental" designs be classified?

---

## Files Modified/Created

### Modified
- `src/services/query_response.py` - Added ContestedEvidence, clickable follow-ups, "scope" type
- `src/services/reporting.py` - Added taxonomy-driven outcomes, confounder gap detection
- `app/routes/query.py` - Added ContestedEvidenceResponse, updated FollowUpResponse
- `tests/test_query_response.py` - Added 6 H5 tests, updated follow-up type expectations
- `tests/test_reporting.py` - Added 5 H2 tests, 7 H3 tests
- `tests/test_query_routes.py` - Updated follow-up type expectation

### Created
- `src/services/causal_classifier.py` - New three-tier classifier (400+ lines)
- `tests/test_causal_classifier.py` - 43 tests for causal classifier

---

## Test Coverage

| Test File | Tests | Status |
|-----------|-------|--------|
| test_query_response.py | 28 | PASS |
| test_reporting.py | 40 | PASS |
| test_causal_classifier.py | 43 | PASS |
| test_query_routes.py | 25 | PASS |
| **Total** | **136** | **PASS** |

---

## Recommendations for Future Work

1. **Integrate CausalClassifier with Web of Belief**: Currently standalone; should be called during belief ingestion to add `causal_tier` field to beliefs.

2. **Add causal tier to API responses**: Query responses should include the causal classification for each evidence item.

3. **Panel review of MEDIUM priority items**: 12 MEDIUM priority items from the Phase C-D review await implementation.

4. **Domain-specific pattern tuning**: Neuroarchitecture may have specific causal language patterns worth capturing (e.g., "environmental exposure", "design intervention").
