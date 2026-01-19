# Expert Panel Responses: Sprints 6-8 Review

**Date**: Sunday, January 19, 2026
**Status**: RESPONSES RECEIVED

---

## Panel Summary

The expert panel (Pearl, Cartwright, Simon, Bates, Kaplan) reviewed the Sprint 6-8 implementation decisions and provided the following prioritized recommendations.

---

## CHANGES TO MAKE NOW (Before Sprint 9)

### 1. Require mediator for MEDIATED causal direction (Pearl)
- **File**: `src/services/web_of_belief.py`
- **Issue**: MEDIATED allows `mediator=None`, which prevents proper causal reasoning
- **Fix**: Add validation that `mediator is not None` when `causal_direction == MEDIATED`

### 2. Fix "theoretical" pass thresholds logic (Simon)
- **File**: `src/services/validation.py`
- **Issue**: Theoretical F1=0.55 is too low for consequential beliefs
- **Fix**: Either raise theoretical thresholds OR add separate "coherence contribution" metric that flags low-confidence theoretical beliefs

### 3. Add unknown scope handling (Cartwright)
- **Files**: `src/services/web_of_belief.py`, `src/services/web_persistence.py`
- **Issue**: `None` scope is treated as universal, but unknown ≠ universal
- **Fix**: Add `scope_specified: bool` to ScopeConditions; unknown scope should not assume overlap

### 4. Fix config/configurational naming inconsistency (Bates)
- **File**: `src/services/environment_taxonomy.py`
- **Issue**: Category is "configurational" but IDs are "config.*"
- **Fix**: Standardize naming (recommend keeping "config.*" IDs, rename category to "config")

### 5. Ecological validity should affect uncertainty, not credence (Kaplan)
- **File**: `src/services/validation.py`
- **Issue**: Current weights discount credence directly
- **Fix**: Instead increase uncertainty by factor of `1/ecological_validity_weight`

---

## CHANGES FOR NEXT REVISION (Sprint 10+)

1. **Add INSTRUMENTAL causal direction** (Pearl) - for IV designs
2. **Add cluster_independence_fraction** (Pearl) - partial independence within studies
3. **Add mean path length as secondary connectivity metric** (Pearl)
4. **Add SOCIAL facet to environment taxonomy** (Bates)
5. **Add theory diversity to diversity index** (Bates)
6. **Add dose-response metadata to causal claims** (Kaplan)
7. **Add prior_depletion and baseline_nature to ScopeConditions** (Kaplan)
8. **Split VR into VR_IMMERSIVE vs VR_DESKTOP** (Kaplan)
9. **Raise LAB_ABSTRACT from 0.50 to 0.60** (Kaplan)
10. **Make diversity weighting adaptive by corpus maturity** (Simon)

---

## ISSUES REQUIRING EMPIRICAL VALIDATION

1. **Precision boundary thresholds (0.1-0.3)** — Calibrate against gold standard
2. **Diversity weighting (0.6/0.4)** — Test sensitivity on actual corpus
3. **Phase gate thresholds (10/20/30/50 papers)** — Validate statistical power claims
4. **Antonym equivalence symmetry** — Which environment pairs actually exhibit symmetric effects?
5. **Scope hierarchy completeness** — Analyze actual terminology usage in corpus

---

## Detailed Feedback by Expert

### Dr. Judea Pearl
- MEDIATED requires naming M - critical for blocking/confounding analysis
- COMMON_CAUSE also needs to track what C is
- Missing: INSTRUMENTAL for IV designs
- Evidence clustering is sound but too conservative - add partial independence
- LCC is appropriate but add mean path length for diameter concerns

### Dr. Nancy Cartwright
- Unknown scope ≠ Universal scope - major logical error
- Hierarchical compatibility needs empirical grounding from corpus
- Precision boundary thresholds should scale by sample size
- Consider structured moderators (triggers/shields/amplifies/attenuates)

### Dr. Herbert Simon
- Thresholds need empirical calibration - satisficing is fine but validate
- Theoretical pass thresholds are backwards (lower = easier, but should be harder)
- Diversity weighting should be adaptive to corpus maturity
- 30 papers for LOO is minimal but acceptable

### Dr. Marcia Bates
- Fix config/configurational naming inconsistency
- Missing SOCIAL facet for social density/interaction
- Antonym equivalence fails with thresholds, unipolar DVs, asymmetric relationships
- Add theory diversity to diversity index
- Use effective number of categories (exp(entropy))

### Dr. Rachel Kaplan
- Missing dose-response metadata for CNFA claims
- Missing prior_depletion and baseline_nature in scope
- VR > video > photos is empirically supported
- But VR quality varies enormously - split into VR_HIGH/VR_LOW
- LAB_ABSTRACT 0.50 is too harsh - raise to 0.60
- Ecological validity should affect uncertainty, not credence
