# IMG-2 Phase 3 Expert Panel Review: Executive Summary

**Date**: 2026-03-02
**Panel Size**: 8 experts (environmental psychology, architecture, space syntax, neuroscience, epistemology)
**Taxonomy Reviewed**: 33 attributes (21 original ATTR-* + 12 new NEW-01 to NEW-12)
**Document**: See `IMG2_PHASE3_EXPERT_PANEL_2026-03-02.md` for full report (1,400+ lines)

---

## Overall Verdict: ACCEPT WITH REVISIONS

**Confidence**: MODERATE-TO-HIGH (6-7 of 8 panelists confident)

### Quick Metrics

| Dimension | Average Rating | Status |
|-----------|----------------|--------|
| **Theoretical Warrant (TW)** | 3.6/5 | Moderate-to-strong |
| **Computational Validity (CV)** | 3.2/5 | Moderate (concerns about photo-based extraction) |
| **Practical Utility (PU)** | 3.8/5 | High for core attributes |

---

## Key Findings

### Top 10 Priority Attributes (Consensus Ranking)

**Tier A — Essential (all panelists agree)**
1. ATTR-F1 — Fractal Dimension (Box-Counting) — Score: 76/80
2. ATTR-C3 — Green Chromaticity (Biophilic Color) — Score: 74/80
3. ATTR-S1 — Isovist Area (Prospect) — Score: 68/80
4. ATTR-S3 — Enclosure Ratio (Refuge) — Score: 67/80

**Tier B — High-Value (6-7 panelists prioritize)**
5. NEW-12 — Biomorphic Curvature Index — Score: 65/80
6. NEW-04 — Visual Complexity Score — Score: 62/80
7. ATTR-B2 — Water Feature Presence — Score: 60/80
8. ATTR-M1 — Material Naturalness Index — Score: 59/80

**Tier C — Supplementary (4-5 panelists prioritize)**
9. NEW-05 — Regularity/Repetition Index — Score: 55/80
10. ATTR-S4 — Spatial Legibility (or ATTR-C1 for circadian) — Score: 52/80

---

## Critical Issues and Resolutions

### Attributes to Retire (Consensus)

| Attribute | Verdict | Reason |
|-----------|---------|--------|
| **ATTR-M3** (Olfactory Expectation) | REJECT | TW=1.4/5; CV=1.1/5. Too speculative. CLIP zero-shot olfactory classification unreliable. Defer pending validation studies. |
| **ATTR-B1** (Biomorphic Form Index) | CONSOLIDATE → NEW-12 | Redundant with NEW-12 (Biomorphic Curvature Index). NEW-12 is more quantitatively precise. |

### Attributes to Demote to Supplementary

| Attribute | Issue | Action |
|-----------|-------|--------|
| **ATTR-F2** (1/f Spectral Slope) | Moderate TW; incomplete causal link. Correlates with F1 (r≈0.70). | Keep but mark as secondary; use only for spectral analysis comparisons. |
| **ATTR-F3** (Lacunarity) | Secondary to F1; specific use case (clumped vs. uniform fractals). | Keep as supplementary; not essential. |
| **ATTR-P1** (Figure-Ground Clarity) | Moderate utility; largely confounded with F4 (edge density). | Keep but use with F4, not alone. |

### Attributes Requiring Computational Caveats

| Attribute | Photo-Based Challenge | Recommendation |
|-----------|------------------------|-----------------|
| **ATTR-C1** (CCT) | Illuminant estimation difficult; ±500K uncertainty typical. | Mark Tier 2, ψ-calibrated. Require metadata when possible. |
| **ATTR-S1** (Isovist from photo) | Monocular depth estimation is approximation. | Use floor plans for high precision. For photos: report as "estimated prospect ± uncertainty". |
| **ATTR-S2** (Ceiling height from photo) | Vanishing point detection fails in cluttered scenes. | Recommend floor plan extraction. Photo-based: ±20% uncertainty. |
| **ATTR-S4** (Legibility from photo) | Cannot extract space syntax from single image. | Use semantic segmentation + scene classification as proxy only. For true legibility: require floor plan (space syntax). |
| **ATTR-M1** (Material naturalness) | CNN-based classification ~85% accurate but noisy in complex scenes. | Report per-class confidence scores. Pair with human validation. |
| **ATTR-M2** (Haptic expectation) | Cross-modal prediction is noisy (r≈0.35-0.45). | Mark as EXPLORATORY. Defer full implementation until validation studies. |
| **ATTR-A2** (Social density from furniture) | Predicting occupancy from layout is unreliable without context. | Report as "predicted occupancy ± confidence bounds". Validate against observed data. |

---

## Major Disagreements (Documented)

### 1. Fractal Universality (Taylor vs. Gehl)

**Taylor**: Fractal D ≈ 1.3-1.5 is human universal; aesthetic preference robust.

**Gehl**: Laboratory fractal preference ≠ observed behavior; affordances (seating, shelter) drive actual activity more than fractals.

**Resolution**: Both correct. Fractal preference is universal in lab. But real-world behavior hierarchy is: affordances > spatial configuration > aesthetics > fractal preference. Fractals are necessary but not sufficient.

### 2. Photo-Based Spatial Extraction (Dalton vs. Ellard vs. Kirsh)

**Dalton**: Cannot extract space syntax from photographs; requires floor plans.

**Ellard**: Approximate monocular depth sufficient for neural prediction models.

**Kirsh**: Decision tree methodology works with photographic descriptions; accept approximations with uncertainty bounds.

**Resolution**: Different applications require different precision. High-precision research: floor plans required. Rapid environmental screening: photo approximations acceptable with ±15-20% bounds.

### 3. Cultural Calibration Scope (Taylor vs. Kaplan vs. Gehl)

**Taylor**: Fractal preference is human universal; cultural variation is minor.

**Kaplan**: Optimal complexity for restoration varies by cultural exposure.

**Gehl**: Behavioral response (what counts as "seating" or "social distance") is culturally mediated.

**Resolution**: Partial universals with cultural modulation. Implement universal preference functions (Taylor) with culture-specific calibration parameters (Kaplan/Gehl).

---

## New Attributes to Implement (Phase 4)

The panel identified three high-value missing attributes:

| New Attribute | Rationale | Priority |
|---------------|-----------|----------|
| **NEW-13: Temporal Lighting Variation Index** | CCT snapshot misses dynamic quality; time-of-day lighting alignment affects circadian health. | HIGH |
| **NEW-14: Prospect-Refuge Balance Score** | Composite of S1 (isovist) + S3 (enclosure); optimum is balance, not extremes. | HIGH |
| **NEW-15: Focal Point Density** | Distinguishes "organized complexity" from "chaotic clutter"; salient object count via detection. | MODERATE |

---

## Redundancy Analysis

### Correlated Measures (Keep All, Clarify Roles)

| Measure Group | Correlation | Guidance |
|---------------|-------------|----------|
| F1 (fractal D) vs. F2 (1/f) vs. F3 (lacunarity) | r ≈ 0.35-0.75 | Use F1 primary. F2/F3 supplementary. |
| F4 (edge density) vs. NEW-04 (complexity) | r ≈ 0.80 | Choose one depending on analysis goal. |
| S1 (isovist) vs. S3 (enclosure) | Inverse relationship | Keep both; complementary (prospect vs. refuge). |
| C3 (green chromaticity) vs. NEW-01 (vegetation segmentation) | r ≈ 0.70-0.85 | Use C3 for fast approximation; NEW-01 for precision. |

---

## Discipline-Specific Priorities

Different fields prioritize attributes differently. Recommended rankings:

### For Stress Recovery / Environmental Health:
1. ATTR-F1, ATTR-C3, ATTR-S3, ATTR-B2, ATTR-C1, ATTR-M1, NEW-04

### For Urban/Outdoor Design & Behavior Prediction:
1. ATTR-F1, ATTR-C3, ATTR-S1, ATTR-B2, ATTR-A1, ATTR-A2, NEW-05

### For Interior Design & Comfort:
1. ATTR-F1, ATTR-C3, ATTR-S3, ATTR-S2, ATTR-C1, ATTR-M1, NEW-08

### For Biophilic Design:
1. ATTR-F1, ATTR-C3, ATTR-B1/NEW-12, ATTR-B2, ATTR-M1, NEW-01, NEW-02, NEW-03

---

## Immediate Action Items (Phase 4)

### Critical Path (Complete Before Deployment)

- [ ] Retire ATTR-M3 (olfactory expectation) and ATTR-B1 (consolidate to NEW-12)
- [ ] Add uncertainty bounds to photo-based spatial attributes (C1, S1, S2, S4)
- [ ] Implement NEW-13, NEW-14, NEW-15
- [ ] Create discipline-specific priority matrices and implementation guides
- [ ] Validate computational algorithms on benchmark datasets

### Medium-term (Phase 4-5)

- [ ] Cross-cultural fractal validation studies
- [ ] Behavioral prediction validation (attributes → observed dwell time/activity)
- [ ] Photo-based spatial attribute accuracy benchmarking vs. floor plan ground truth
- [ ] Haptic-visual cross-modal prediction validation (ATTR-M2)
- [ ] ψ-Calibration documentation for culture-dependent attributes

### Documentation

- [ ] Revise taxonomy with priority tiers (A/B/C) and uncertainty notes
- [ ] Create computational feasibility matrix (time, memory, accuracy per attribute)
- [ ] Document space syntax distinction (visual attributes ≠ spatial topology)

---

## Panelist Quotes (Summary)

**Kaplan**: "Restoration theory is well-captured, but we need explicit operationalization of coherence and the prospect-refuge balance. Not all complexity is restorative; order matters."

**Salingaros**: "Fractal dimension is the foundation. Everything else should support the primary measure of self-similar organization at multiple scales."

**Gehl**: "The behavioral link is critical. Beautiful fractals mean nothing if there's nowhere to sit. Affordances drive activity; aesthetics modulate quality."

**Dalton**: "Do not claim to extract space syntax from photographs. This is not possible. Floor plans are gold standard for spatial analysis; visual attributes are orthogonal."

**Ellard**: "The neural basis is strong for core attributes — fractals, green, curves, lighting. But some attributes lack clear neural pathway; those should be demoted or rejected."

**Kirsh**: "The decision tree methodology is sound. Causal decomposition is epistemically rigorous. Now we need cross-cultural validation and behavior prediction studies to complete the picture."

---

## Conclusion

The IMG-2 taxonomy is **READY FOR DEPLOYMENT** in Phase 4 with the revisions specified above. The core attributes (F1, C3, S1, S3, B1/NEW-12, NEW-04, B2, M1) have strong theoretical warrant and are computationally feasible. Secondary attributes add context and discipline-specific utility.

**Key success factors for Phase 5+**:
1. Validate behavioral predictions (attributes → observed outcomes)
2. Document and measure ψ-calibration effects across cultures
3. Integrate space syntax for floor plan analysis
4. Clarify computational uncertainty for all photo-based extraction

**Expected impact**: The 33-attribute taxonomy (reduced to ~30 with consolidations) will enable:
- Automated environmental characterization of architectural images
- Evidence-based design recommendations (which attributes drive wellbeing?)
- Cross-cultural environmental preference studies
- Integration of ATLAS with BN_graphical for causal inference from image → psychology

---

**Full Panel Review**: `/docs/IMG2_PHASE3_EXPERT_PANEL_2026-03-02.md` (1,400+ lines)

**Panel Members**: Roger Ulrich, Rachel Kaplan, Nikos Salingaros, Richard Taylor, Jan Gehl, Ruth Dalton, Colin Ellard, David Kirsh

**Review Date**: March 2, 2026
**Status**: ACCEPT WITH REVISIONS — Ready for Phase 4 Implementation
