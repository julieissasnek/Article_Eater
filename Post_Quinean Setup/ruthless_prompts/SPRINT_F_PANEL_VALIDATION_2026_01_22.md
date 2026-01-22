# Sprint F Implementation Validation: Panel Responses

**Date**: January 22, 2026
**Review Type**: Implementation Decision Validation
**Panel**: Original 10 experts + AI/CS additions

---

## Kaplan (Environmental Psychology) - Domain Validity

### F1.1: Neuroarchitecture Causal Patterns
**Assessment**: MODIFY (MEDIUM priority)

**Specific feedback**:
1. `thermal comfort` should be SUGGESTIVE, not CAUSAL - it's typically an outcome variable, not an intervention. Move to `NEUROARCH_SUGGESTIVE_PATTERNS`.

2. `\bLEED\b` is too broad - could match "leed" as a verb or name. Change to `\bLEED\s+(certified|certification|rating|platinum|gold|silver)`.

3. Missing critical terms:
   - `post-occupancy evaluation` / `POE`
   - `workstation design`
   - `open-plan office` / `open office`
   - `private office`
   - `activity-based working` / `ABW`

**Action**: Move `thermal comfort` to suggestive, tighten LEED pattern, add missing terms.

### F1.2: Theoretical Framework Patterns
**Assessment**: MODIFY (HIGH priority)

**Specific feedback**:
1. `extent` and `compatibility` ARE too generic without context. Remove them as standalone patterns - they'll cause false positives in non-ART contexts.

2. `mystery` and `complexity` are problematic - these words appear everywhere. Require co-occurrence with `landscape`, `preference`, or `Appleton`.

3. Author names are APPROPRIATE triggers - when researchers cite "Kaplan" or "Ulrich" they're typically invoking the theory.

4. **Missing frameworks** (CRITICAL):
   - **Place Attachment Theory**: `place attachment`, `place identity`, `place dependence`
   - **Restorative Environments**: `restorative environment`, `perceived restorativeness`, `PRS` (Perceived Restorativeness Scale)
   - **Environmental Preference**: `preference matrix`, `coherence`, `legibility` (Kaplan & Kaplan)

5. Stress Recovery vs Stress Reduction: These are often used interchangeably in literature. Keep both patterns but note they refer to the same theory (Ulrich's SRT).

**Action**: Remove generic terms, add co-occurrence requirements, add missing frameworks.

### F1.3: Fallback Outcomes
**Assessment**: APPROVE with minor MODIFY (LOW priority)

**Specific feedback**:
1. Taxonomy hierarchy is correct.
2. `physio.circadian` placement is fine - it's a physiological measure.
3. `cog.focus` vs `cog.attention` - keep both, they ARE distinct in literature (sustained attention vs selective focus).

4. **Missing outcomes** (add these):
   - `behav.social` - social interaction, communication frequency
   - `affect.privacy` - perceived privacy satisfaction
   - `cog.wayfinding` - navigation, spatial orientation
   - `affect.control` - perceived environmental control

**Action**: Add four missing outcome categories.

### F1.4: Domain Confounders
**Assessment**: APPROVE with MODIFY (MEDIUM priority)

**Add these confounders**:
- `age`, `gender`, `education` (demographic)
- `noise sensitivity`, `thermal sensitivity` (individual differences)
- `window access`, `view content` (environmental)
- `organizational culture`, `management style` (organizational)

The `Model 2`, `Model 3` pattern is acceptable - this is standard practice in reporting adjusted models.

---

## Cartwright (Philosophy of Science) - Evidence Portability

### F2.1: CAPACITY Bridge Type
**Assessment**: MODIFY (HIGH priority)

**Specific feedback**:
1. P(bridge) = 0.55 is **too high** for capacity claims. Capacity claims are often unfalsifiable assertions. Recommend **0.45**.

2. Reducing CONSTITUTIVE to 0.75 was correct.

3. **Problem with keywords**: "tends to" and "able to" are NOT capacity claims - they're statistical tendencies or possibility claims. True capacity language is:
   - "has the capacity to"
   - "possesses the capacity"
   - "inherent capacity"
   - "intrinsic ability"
   - "dispositional property"

4. **CAPACITY vs FUNCTIONAL distinction**:
   - FUNCTIONAL: Same effect, potentially different mechanisms
   - CAPACITY: Asserts stable causal power without specifying mechanism or outcome details

   Example: "Plants reduce stress" (FUNCTIONAL - same outcome)
   vs "Plants have the capacity to influence psychological states" (CAPACITY - stable power)

**Action**: Reduce P(bridge) to 0.45, tighten keywords to true capacity language.

### F2.2: Measurement Categories
**Assessment**: MODIFY (MEDIUM priority)

**Missing categories**:
1. **Observational/Behavioral coding** - researcher observation, not self-report or physiological
2. **Ecological Momentary Assessment (EMA)** - repeated in-situ sampling
3. **Archival/Administrative** - absenteeism records, HR data

**Physiological should be separate from objective** - physiological measures are objective but form a distinct modality with different validity concerns.

Proposed categorization:
- Self-report (subjective)
- Behavioral/Performance (task-based)
- Physiological (biomarkers)
- Environmental/Physical (sensors)
- Observational (researcher-coded)
- Archival (records)

**Action**: Expand to 6 measurement modalities.

---

## Pearl (Causality) - Inference

### F1.4: Confounder Patterns
**Assessment**: APPROVE with MODIFY (LOW priority)

The `Model 2`, `Model 3` pattern is crude but acceptable for abstract-level detection.

**Add these implicit control indicators**:
- `propensity score` (already have)
- `inverse probability weighting`
- `doubly robust`
- `g-computation`
- `marginal structural model`

These are stronger indicators of proper causal adjustment than "Model 2".

### Design-First Approach Validation
**Assessment**: APPROVE

The implementation correctly prioritizes:
1. Experimental design → CAUSAL
2. Quasi-experimental + causal language → CAUSAL
3. Causal language + mechanism → CAUSAL
4. Causal language alone → SUGGESTIVE

This is epistemically correct.

---

## Naur (Theory Building) - Theory Preservation

### F3.1: DESIGN_RATIONALE.md
**Assessment**: APPROVE with MODIFY (MEDIUM priority)

**What's good**:
- Captures the key epistemological commitments
- Decision log is valuable
- References are appropriate

**What's missing**:
1. **Worked examples**: The document explains WHAT but not HOW. Add 2-3 concrete examples showing the theory in action:
   - Example of how a claim becomes a belief with credence
   - Example of how directional opposition is detected
   - Example of how a bridge warrant transfers knowledge

2. **Negative examples**: Show what the system DOESN'T do and why:
   - Why we don't use Bayesian updating
   - Why we don't have a fourth tier
   - What happens to claims that don't fit

**Action**: Add worked examples section and negative examples.

---

## Lamport (Formal Methods) - Consistency

### F3.2: INVARIANTS.md
**Assessment**: MODIFY (HIGH priority)

**Specific feedback**:

1. **Formality level is appropriate** for documentation - TLA+ would be overkill. However, consider adding precondition/postcondition contracts to critical functions.

2. **Consistency model is UNDER-SPECIFIED**. You say "queries operate on snapshot" but don't specify:
   - When is the snapshot taken? (At query start? At first belief access?)
   - What happens if the web changes during query execution?
   - Is the snapshot explicit (copy) or implicit (no concurrent writes)?

3. **Missing invariant** (CRITICAL):
   ```
   INV-W8: Credence updates must preserve transitivity
           If A supports B and B supports C,
           then credence(A) change should propagate to C
   ```

4. **Runtime enforcement priorities**:
   - MUST enforce at runtime: INV-B3, INV-B4 (credence bounds)
   - SHOULD enforce at runtime: INV-BR4 (bridge bounds)
   - MAY defer to tests: INV-W1 (DAG structure - expensive to check)

### Centralized Web State
**Assessment**: MODIFY (HIGH priority)

Shared mutable global is acceptable for single-worker deployment but NOT for production multi-worker.

**Minimum viable fix**:
```python
# In each route handler that reads the web:
def query_endpoint(...):
    web_snapshot = get_web().snapshot()  # Immutable copy
    # All operations use web_snapshot
```

Add a `snapshot()` method to WebOfBelief that returns a frozen copy.

**Action**: Add `snapshot()` method, update route handlers to use snapshots for reads.

---

## Bates (Information Science) - User Interface

### F4.1: Vocabulary Expansion Display
**Assessment**: APPROVE with MODIFY (LOW priority)

**Feedback**:
1. Display is sufficiently prominent.
2. Showing matched separately is correct - users need to see what actually worked.
3. **Enhancement**: Add "why expanded" tooltip on hover (e.g., "synonym", "broader term", "related concept").
4. Legend is sufficient.

### F4.2: Faceted Filtering
**Assessment**: MODIFY (MEDIUM priority)

**Feedback**:
1. Facets are appropriate.
2. AND logic is correct for faceted filtering.
3. Sliders for credence are fine, but add preset buttons: "High (>70%)", "Medium (40-70%)", "Low (<40%)".
4. **Add theoretical framework facet** - YES, this is important for domain researchers.
5. **Missing facets**:
   - Publication year range
   - Study type (experimental, observational, review, meta-analysis)

**Action**: Add credence presets, theoretical framework facet, year range, study type.

---

## Simon (Bounded Rationality) - Satisficing

### Overall Assessment: APPROVE

The implementation maintains satisficing principles:
- Three tiers preserved (not expanded to four)
- Exactly 3 follow-ups preserved
- Filter options are manageable (not overwhelming)
- Vocabulary expansion is informative without being exhaustive

No modifications needed for satisficing concerns.

---

## Summary: Required Actions

### CRITICAL (Must fix)
| ID | Issue | Action | Owner |
|----|-------|--------|-------|
| C1 | Missing invariant INV-W8 | Add credence propagation invariant | Lamport |

### HIGH Priority
| ID | Issue | Action | Owner |
|----|-------|--------|-------|
| H1 | CAPACITY P(bridge) too high | Reduce from 0.55 to 0.45 | Cartwright |
| H2 | Capacity keywords too broad | Remove "tends to", "able to" | Cartwright |
| H3 | Missing theoretical frameworks | Add Place Attachment, Restorative Environments | Kaplan |
| H4 | Generic ART terms | Remove `extent`, `compatibility` as standalone | Kaplan |
| H5 | Consistency model under-specified | Add snapshot() method | Lamport |
| H6 | Missing measurement modalities | Expand to 6 categories | Cartwright |

### MEDIUM Priority
| ID | Issue | Action | Owner |
|----|-------|--------|-------|
| M1 | `thermal comfort` in wrong tier | Move to SUGGESTIVE | Kaplan |
| M2 | LEED pattern too broad | Add certification context | Kaplan |
| M3 | Missing outcome categories | Add social, privacy, wayfinding, control | Kaplan |
| M4 | Missing confounders | Add demographic, sensitivity, organizational | Kaplan |
| M5 | Missing facets | Add year range, study type, framework | Bates |
| M6 | DESIGN_RATIONALE needs examples | Add worked examples section | Naur |

### LOW Priority
| ID | Issue | Action | Owner |
|----|-------|--------|-------|
| L1 | Add causal method indicators | Add IPW, doubly robust, g-computation | Pearl |
| L2 | Add vocabulary expansion tooltips | Show "why expanded" on hover | Bates |
| L3 | Add credence presets | High/Medium/Low buttons | Bates |

---

## Implementation Plan

### Phase 1: Critical + High Priority
1. Add INV-W8 to INVARIANTS.md
2. Update bridge_warrants.py: P(CAPACITY) = 0.45, tighten keywords
3. Update causal_classifier.py: Add frameworks, remove generic terms
4. Add snapshot() to WebOfBelief
5. Expand measurement categories in query_response.py

### Phase 2: Medium Priority
6. Move `thermal comfort` to suggestive
7. Tighten LEED pattern
8. Add outcome categories to reporting.py
9. Add confounders to reporting.py
10. Add facets to evidence-explorer.html
11. Add worked examples to DESIGN_RATIONALE.md

### Phase 3: Low Priority
12. Add causal method indicators
13. Add vocabulary tooltips
14. Add credence presets

---

## Panel Sign-Off

This validation identifies 6 HIGH priority items that should be addressed before considering Sprint F complete. The implementation is fundamentally sound but needs refinement in pattern specificity and measurement categorization.

**Recommendation**: Implement Phase 1 items, re-validate, then proceed to Phase 2.
