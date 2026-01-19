# Implementation Plan: Expert Panel Sprint 6-8 Fixes

**Date**: Sunday, January 19, 2026
**Status**: ALL FIXES COMPLETE ✓
**Priority**: Complete before proceeding to Sprint 9

---

## Implementation Summary

All 5 panel fixes have been implemented and tested:

| Fix | Status | Tests |
|-----|--------|-------|
| Fix 1: Require mediator for MEDIATED | COMPLETE | 3 new tests |
| Fix 2: Coherence contribution metric | COMPLETE | 8 new tests |
| Fix 3: Add scope_specified field | COMPLETE | 7 new tests |
| Fix 4: Rename configurational to config | COMPLETE | 1 test updated |
| Fix 5: Ecological validity → uncertainty | COMPLETE | 6 new tests |

**Total: 197 tests passing**

---

## Overview

The expert panel (Pearl, Cartwright, Simon, Bates, Kaplan) reviewed Sprints 6-8 and identified 5 issues requiring immediate attention. This document plans the implementation of each fix.

---

## Fix 1: Require mediator for MEDIATED causal direction (Pearl)

**File**: `src/services/web_of_belief.py`

**Issue**: The `MEDIATED` causal direction currently allows `mediator=None`, which prevents proper causal reasoning about blocking and confounding.

**Implementation**:
1. Add a `mediator: Optional[str]` field to the `Belief` dataclass (or wherever causal metadata is stored)
2. Add validation in `WebOfBelief.add_belief()` that raises `ValueError` if `causal_direction == CausalDirection.MEDIATED` and `mediator is None`
3. Update tests to verify this validation

**Test Cases**:
- `test_mediated_requires_mediator_raises_on_none`
- `test_mediated_with_mediator_succeeds`
- `test_non_mediated_directions_allow_none_mediator`

---

## Fix 2: Fix theoretical pass thresholds logic (Simon)

**File**: `src/services/validation.py`

**Issue**: Theoretical F1=0.55 is too low for consequential beliefs. Lower thresholds make it *easier* to pass, but theoretical claims should arguably be *harder* to validate (higher bar).

**Options**:
- A: Raise theoretical thresholds (F1=0.65, credence=0.70)
- B: Add `coherence_contribution_flag` that flags low-confidence theoretical beliefs for review

**Decision**: Implement Option B (add flag) - this preserves the current pragmatic thresholds while adding visibility into which theoretical beliefs are weakly supported.

**Implementation**:
1. Add `coherence_contribution: Literal["high", "medium", "low"]` field to validation results
2. Compute based on: number of supporting constraints, strength of constraints, consistency with empirical findings
3. Flag beliefs with `coherence_contribution="low"` in validation reports
4. Keep current thresholds but add warning when theoretical beliefs have low coherence contribution

**Test Cases**:
- `test_coherence_contribution_high_when_well_supported`
- `test_coherence_contribution_low_when_isolated`
- `test_theoretical_with_low_coherence_flagged`

---

## Fix 3: Add unknown scope handling (Cartwright)

**Files**: `src/services/web_of_belief.py`, `src/services/web_persistence.py`

**Issue**: `None` scope is treated as universal (overlaps with everything), but unknown ≠ universal. Papers that don't specify scope shouldn't be assumed to apply everywhere.

**Implementation**:
1. Add `scope_specified: bool = False` field to `ScopeConditions` dataclass
2. Update scope overlap logic:
   - If both scopes have `scope_specified=False`: overlap=True (both unknown, be charitable)
   - If one has `scope_specified=True` and one `False`: overlap=True with warning (unknown may not apply)
   - If both have `scope_specified=True`: apply current dimension-matching logic
3. Add `scope_overlap_confidence: float` to overlap results to indicate certainty
4. Update persistence layer to serialize the new field

**Test Cases**:
- `test_unknown_scope_overlaps_with_unknown`
- `test_specified_scope_overlaps_with_unknown_with_warning`
- `test_specified_scopes_use_dimension_matching`
- `test_scope_specified_persisted_correctly`

---

## Fix 4: Fix config/configurational naming inconsistency (Bates)

**File**: `src/services/environment_taxonomy.py`

**Issue**: Category is named "configurational" but IDs are "config.*" - this is inconsistent and confusing.

**Decision**: Keep "config.*" IDs (they're shorter), rename category key to "config" for consistency.

**Implementation**:
1. Rename top-level category from "configurational" to "config" in `ENVIRONMENT_HIERARCHY`
2. Update any references to "configurational" in code
3. Update tests

**Test Cases**:
- `test_config_category_exists`
- `test_config_ids_resolve_correctly`

---

## Fix 5: Ecological validity affects uncertainty, not credence (Kaplan)

**File**: `src/services/validation.py`

**Issue**: Current weights discount credence directly (e.g., LAB_PHOTOS × 0.65 = reduce credence). This conflates validity with certainty. Instead, lower ecological validity should *increase uncertainty* about the effect size, not reduce the effect estimate itself.

**Implementation**:
1. Change `ECOLOGICAL_VALIDITY_WEIGHTS` to `ECOLOGICAL_VALIDITY_UNCERTAINTY_FACTORS`
2. Instead of `credence *= weight`, compute `uncertainty *= 1/weight`
3. Example: LAB_PHOTOS (0.65) → uncertainty factor = 1/0.65 ≈ 1.54 → uncertainty increases by 54%
4. Update all references to this weighting system
5. Update documentation to clarify the semantics

**Test Cases**:
- `test_field_natural_no_uncertainty_increase`
- `test_lab_photos_increases_uncertainty`
- `test_lab_abstract_highest_uncertainty_increase`
- `test_credence_value_unchanged_by_ecological_validity`

---

## Implementation Order

1. Fix 4 (naming) - Simplest, no logic changes
2. Fix 1 (mediator) - Clear validation addition
3. Fix 3 (scope_specified) - Requires dataclass and persistence changes
4. Fix 5 (uncertainty) - Requires semantic change to validation
5. Fix 2 (coherence contribution) - Most complex, adds new concept

---

## Files to Modify

| File | Fixes |
|------|-------|
| `src/services/environment_taxonomy.py` | Fix 4 |
| `src/services/web_of_belief.py` | Fix 1, Fix 3 |
| `src/services/web_persistence.py` | Fix 3 |
| `src/services/validation.py` | Fix 2, Fix 5 |
| `tests/test_environment_taxonomy.py` | Fix 4 |
| `tests/test_web_persistence.py` | Fix 1, Fix 3 |
| `tests/test_validation.py` | Fix 2, Fix 5 |

---

## Success Criteria

- All 5 fixes implemented
- All existing tests still pass
- New tests for each fix pass
- CLAUDE.md updated with panel fix status
