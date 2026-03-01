# Expert Panels 1 & 2: Comparison and Synthesis

**Dates**: Panel 1: 2026-02-26 (health assessment), Panel 2: 2026-02-27 (empirical association deep-dive)
**Panel Composition**: 6 core members (Spohn, Pearl, Haack, Woodward, Glymour, Laudan) — consistent across both

---

## Context

**Panel 1** focused on broader ATLAS system health and architecture soundness. Addressed 4 major questions about EN/BN separation, projection formula, warrant hierarchy, and population transfer.

**Panel 2** was a critical follow-up addressing a finding from Panel 1: **EMPIRICAL_ASSOCIATION d=0.80 is too high**. Deep debate on whether empirical track records (without known mechanism) transfer as reliably as mechanistic evidence.

---

## Panel 1 → Panel 2 Chain

### What Panel 1 Found

Panel 1 Q8 (final question) tested whether canonical discount factors were justified by Woodward's invariance framework:

**Finding**: EMPIRICAL_ASSOCIATION at d=0.80 appears over-confident.

- Black-box associations (observed covariation, no mechanism) are MORE vulnerable to confounding than mechanistic associations
- Woodward's invariance framework: unknown-mechanism associations have NARROWER invariance ranges
- Historical cases (HRT, vitamin E, coffee→heart disease) show reversals under context change
- This suggests d should be LOWER for empirical associations than mechanisms

**Panel 1 Consensus** (from Q8): Recommend revisiting EMPIRICAL_ASSOCIATION in a dedicated Panel 2.

### Panel 2's Mandate

Convene same panel to decide:
1. Is Panel 1's concern justified?
2. What should EMPIRICAL_ASSOCIATION d actually be?
3. Can we avoid penalizing empirical evidence?
4. Should d vary based on replication quality?
5. How do serial chains aggregate uncertainty?

---

## Key Differences Between Panels

| Dimension | Panel 1 | Panel 2 |
|---|---|---|
| **Scope** | Broad: entire ATLAS architecture (8 questions) | Narrow: one warrant type deep-dive (5 questions) |
| **Starting Consensus** | EN/BN separation is sound (unanimous) | EMPIRICAL_ASSOCIATION d might be wrong (concern raised) |
| **Outcome Stance** | Constructive validation with reservations | Constructive revision with consensus |
| **Risk Level** | Medium (architectural) | Medium-High (impacts calibration) |

---

## Synthesis: EMPIRICAL_ASSOCIATION Journey

### Session 2 Decision (Original)
```
EMPIRICAL_ASSOCIATION = d=0.80
Rationale: Replicated statistical evidence; replication signals invariance
```

### Panel 1 Finding
```
Concern: d=0.80 is too high for black-box associations
Evidence: Woodward invariance, historical reversals
Recommendation: Revisit in Panel 2
```

### Panel 2 Verdict
```
EMPIRICAL_ASSOCIATION d ∈ [0.55, 0.80] — TIERED by replication profile
- 1 study: d=0.55
- 2-3 studies, same population: d=0.60
- 2-3 studies, diverse populations: d=0.70
- 5-10 studies, diverse populations: d=0.75
- 10+ studies, very diverse: d=0.80
+ Partial mechanism: +0.05–0.10

Rationale: Replication DIVERSITY signals invariance; mechanism understanding boosts confidence
```

**Resolution**: Car mechanic principle is PRESERVED. A mechanic with 20 repairs across 20 garages (diverse contexts) still gets d=0.80. Same mechanic in one garage → d=0.65. Empirical practitioners are credited, but context-diversity matters.

---

## Panel 1 Questions & Panel 2 Implications

### Panel 1 Q1: Log-Odds Projection Formula
**Verdict**: AFFIRMED UNANIMOUS
**Implication for Panel 2**: The π projection formula works fine. Tiering d doesn't break it — just creates metadata-sensitive d values within types.

### Panel 1 Q2: Serial Combination Rules
**Verdict**: AFFIRMED (min d for serial, product ω) with geometric mean challenge
**Implication for Panel 2**: Panel 2 reaffirmed PRODUCT RULE (d_eff = ∏ d_i) with bottleneck analysis. Long chains with tiered d values will have even lower d_eff — appropriate given compound uncertainty.

### Panel 1 Q3: EN/BN Separation Novelty
**Verdict**: AFFIRMED UNANIMOUS
**Implication for Panel 2**: EN's ability to carry tiered d values without breaking BN interface is a strength. Metadata on EN edges doesn't propagate to BN (consumed by π).

### Panel 1 Q4: Theory Tags
**Verdict**: AFFIRMED UNANIMOUS
**Implication for Panel 2**: THEORY_DERIVED [theory_name] remains at d=0.25. Panel 2 ensures EMPIRICAL_ASSOCIATION tiering doesn't invert the epistemic order.

### Panel 1 Q5: Population Transfer Factor δ
**Verdict**: AFFIRMED UNANIMOUS (new architecture component)
**Implication for Panel 2**: δ is crucial for Panel 2's solution. Black-box associations get tiered d (0.60–0.70) but δ handles population-specific transfer risk. Example: d=0.70 · δ=0.40 = 0.28 for radically different context.

### Panel 1 Q6: Explanatory Boost
**Verdict**: AFFIRMED WITH QUALIFICATIONS
**Implication for Panel 2**: When a mechanism is discovered for an existing empirical association, both effects increase confidence. Panel 2 formalizes this: mechanism understanding = part of d tiering.

### Panel 1 Q7: Dual-BN Trichotomy
**Verdict**: AFFIRMED (Empirically grounded / Theory-augmented / Theory-scaffolded)
**Implication for Panel 2**: Tiering EMPIRICAL_ASSOCIATION sharpens these categories. "Theory-scaffolded" claims rely on theory more when empirical associations are d=0.60 vs. d=0.80.

### Panel 1 Q8: Canonical Discount Factors (by Invariance)
**Verdict**: FLAGGED — EMPIRICAL_ASSOCIATION needs revision
**Direct Link to Panel 2**: This question directly triggered Panel 2's convening. Panel 2 answered: d ∈ [0.55, 0.80] tiered by diversity.

---

## Discount Factor Comparison: Session 2 vs. Panel 2

| Warrant Type | Session 2 (Current) | Panel 2 Revision | Change | Rationale |
|---|---|---|---|---|
| CONSTITUTIVE | 0.95 | 0.95 | — | No change (definitions, no transfer risk) |
| MECHANISM | 0.80 | 0.80 | — | No change (causal structure enables invariance) |
| EMPIRICAL_ASSOCIATION | **0.80** | **0.55–0.80** | **TIERED** | Replication diversity, mechanism understanding matter |
| FUNCTIONAL | 0.65 | 0.65 | — | No change |
| CAPACITY | 0.55 | 0.55 | — | No change |
| ANALOGICAL | 0.40 | 0.40 | — | No change |
| THEORY_DERIVED | 0.25 | 0.25 | — | No change |

**Only EMPIRICAL_ASSOCIATION changes** (from flat 0.80 to tiered 0.55–0.80).

---

## What Changes in Practice

### Before (Session 2)
```
Edge: Drug X → Outcome Y
τ = EMPIRICAL_ASSOCIATION
d = 0.80 (fixed)
ω = 0.60 (quality of evidence)
Full confidence = d · ω · δ = 0.80 · 0.60 · δ
```

### After (Panel 2)
```
Edge: Drug X → Outcome Y
τ = EMPIRICAL_ASSOCIATION
Metadata: (replication_count=12, population_diversity=5, mechanism_detail=40%, publication_bias=none)
d = 0.75 (metadata-informed within type)
ω = 0.70 (evidence quality)
Full confidence = d · ω · δ = 0.75 · 0.70 · δ
```

π projection function now uses metadata to select appropriate d ∈ [0.55, 0.80].

---

## Open Questions (Deferred to Implementation)

### From Panel 1
- Q6a: How fragile is explanatory boost to effect size mismatch?
- Q7a: Should fourth "Contradicted" category be added to dual-BN trichotomy?
- Q8a: Sensitivity analysis on EMPIRICAL_ASSOCIATION revision?

### From Panel 2
- Q1a: How many populations = "diverse"? (5? 10?)
- Q2a: Should population distance be quantified (Hofstede dimensions, WEIRD index)?
- Q3a: How to handle publication bias in d assignment?
- Q4a: Geometric mean vs. product for very long chains (>8 links)?
- Q5a: How to infer mechanism_detail from literature?

---

## Integration Timeline

**Phase 1 (Immediate)**:
1. Update bridge_warrants.py to support EMPIRICAL_ASSOCIATION d ∈ [0.55, 0.80]
2. Add metadata schema to EN edge specification
3. Update π projection to use metadata-informed d

**Phase 2 (SPRINT-1 Revision)**:
1. Rename EMPIRICAL_COVARIANCE → EMPIRICAL_ASSOCIATION throughout codebase
2. Update worked examples with tiered d values
3. Test suite: verify d tiering doesn't break projection formula

**Phase 3 (SPRINT-8, Master Document)**:
1. Rewrite §51 (Bridge Warrants) with tiered d values and justification
2. Add new section: "EMPIRICAL_ASSOCIATION Tiering by Replication Profile"
3. Worked examples showing old d=0.80 vs. new tiered values
4. Cross-reference Panel 1 & 2 findings

---

## Consensus Metrics

| Panel | Q Count | Unanimous | Consensus | Dissent |
|---|---|---|---|---|
| Panel 1 | 8 | 4 | 4 | 0 |
| Panel 2 | 5 | 4 | 1 | 0 |
| **Combined** | **13** | **8 (62%)** | **5 (38%)** | **0 (0%)** |

Both panels achieved consensus on all decisions. No panelist stood alone in dissent.

---

## Epistemic Significance

**Panel 1** provided foundational validation: ATLAS architecture (EN, π, BN, warrant types) is philosophically coherent and methodologically sound.

**Panel 2** provided calibration: The specific d-values must reflect actual invariance properties. EMPIRICAL_ASSOCIATION d=0.80 was over-confident; tiering is epistemically justified by Woodward's framework and historical evidence of reversals.

**Combined impact**: ATLAS moves from "architecturally sound but needs calibration" to "architecturally sound AND appropriately calibrated for empirical vs. mechanistic evidence."

---

**Status**: Ready for implementation. Both panels recommend proceeding with tiered EMPIRICAL_ASSOCIATION d values and full EN/BN architecture as designed.

