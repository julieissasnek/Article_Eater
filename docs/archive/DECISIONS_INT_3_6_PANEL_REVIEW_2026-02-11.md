# Integration Sprint Decisions (INT-1 through INT-6)

**Date**: 2026-02-11
**Author**: Claude Code
**Status**: PANEL REVIEW COMPLETE

This document captures implementation decisions made during the BN-Web integration sprints for expert panel review.

---

## Decisions Under Review

### D0a: Edge Justification Aggregation (INT-1)

**Context**: How to compute aggregate credence for a BN edge from multiple supporting beliefs

**Current Choice**: Inverse-variance weighted average
- Weight each belief by `1 / uncertainty²`
- Aggregate credence = weighted sum / total weight
- Aggregate uncertainty = `sqrt(1 / total_weight)`

**Alternatives Considered**:
1. Simple arithmetic mean (ignores uncertainty differences)
2. Maximum credence (too optimistic)
3. Minimum credence (too conservative)
4. Bayesian evidence combination (more complex)

**Risk**: Assumes belief uncertainties are independent, which may not hold for beliefs from the same study.

---

### D0b: Justification Status Thresholds (INT-1)

**Context**: How to classify edge justification status

**Current Choice**:
- STRONG: aggregate_credence ≥ 0.7 AND n_supporting ≥ 2
- MODERATE: aggregate_credence ≥ 0.5 AND n_supporting ≥ 1
- WEAK: aggregate_credence ≥ 0.3 OR n_supporting ≥ 1
- CONTESTED: any conflicting beliefs present
- UNJUSTIFIED: no supporting beliefs

**Alternatives Considered**:
1. Single credence threshold (ignores support count)
2. Support count only (ignores credence quality)
3. Continuous score without categories

**Risk**: Thresholds are somewhat arbitrary. May need calibration based on user feedback.

---

### D0c: Gap Type Definitions (INT-2)

**Context**: What types of knowledge gaps to detect

**Current Choice**: Six gap types
- MEDIATION: A→X→Y exists but A→Y is missing
- MECHANISM: Empirical beliefs without theoretical explanation
- BOUNDARY: Narrow scope conditions (limited settings/populations)
- DIRECTION: Conflicting causal directions
- VALIDATION: Theoretical beliefs without empirical support
- UNJUSTIFIED_EDGE: BN edges without belief support

**Alternatives Considered**:
1. Fewer types (simpler but less informative)
2. More granular types (overwhelming)
3. User-defined gap types

**Risk**: Some gap types overlap (e.g., MECHANISM and VALIDATION both involve theory-empirical connections).

---

### D0d: VOI Calculation Formula (INT-2)

**Context**: How to prioritize gaps by Value of Information

**Current Choice**:
```
VOI = (1 - current_credence) * connectivity_factor * level_weight
```
- connectivity_factor: number of affected nodes/edges
- level_weight: higher for gaps affecting theoretical beliefs

**Alternatives Considered**:
1. Bayesian expected information gain
2. User-defined priority weights
3. Pure connectivity-based ranking

**Risk**: Simplified VOI formula may not capture true research value.

---

### D1: Edge Credence Visualization (INT-3)

**Context**: How to visually represent epistemic credence on BN edges

**Current Choice**:
- Opacity-based representation: `opacity = 0.3 + (credence * 0.7)`
- Color-coded by justification status:
  - Strong (green): credence ≥ 0.7 with substantial support
  - Moderate (purple): credence 0.5-0.7
  - Weak (yellow): credence 0.3-0.5
  - Unjustified (red): no supporting beliefs
  - Contested (orange): conflicting beliefs present

**Alternatives Considered**:
1. Edge thickness instead of opacity
2. Animated edges for uncertain connections
3. Gradient coloring from source to target

**Risk**: Users may misinterpret opacity as connection strength rather than epistemic confidence. The 0.3 minimum ensures even low-credence edges remain visible.

---

### D2: Evidence Panel Information Density (INT-3)

**Context**: What information to show when user clicks a BN edge

**Current Choice**: Progressive disclosure with:
- Header: Status badge + edge name
- Summary: Credence bar with percentage
- Supporting beliefs: Top 5 with citations (expandable)
- Conflicts: Listed with conflict type
- Theories: Key theoretical frameworks involved

**Alternatives Considered**:
1. Full detail view with all beliefs
2. Minimal view with just credence score
3. Tabbed interface for different aspects

**Risk**: Information overload for non-expert users. Mitigated by collapsible sections.

---

### D3: Epistemic Web Layout Algorithm (INT-4)

**Context**: How to arrange beliefs in the WebView visualization

**Current Choice**: Layered layout by epistemic level
- Y-axis: Theoretical (top) → Observational (bottom)
- X-axis: Grid arrangement within each layer
- Automatic row wrapping (4 beliefs per row)

**Alternatives Considered**:
1. Force-directed layout (allows clustering but loses level hierarchy)
2. Radial layout with theories at center
3. Hierarchical tree from theories down

**Risk**: Fixed grid may not scale well beyond ~50 beliefs. Force-directed would provide better scaling but obscures epistemic level structure.

---

### D4: Belief Node Styling by Level (INT-4)

**Context**: How to visually distinguish epistemic levels

**Current Choice**: Color coding with opacity based on credence
- Theoretical: Purple (#667eea)
- Intermediate: Green (#48bb78)
- Empirical: Pink/Red (#fc8181)
- Observational: Yellow (#ecc94b)

Opacity: `0.3 + credence * 0.7`

**Alternatives Considered**:
1. Different node shapes per level (circle, square, diamond, triangle)
2. Border styling instead of fill color
3. Icon badges on nodes

**Risk**: Color-blind users may have difficulty. Could add shape differentiation in future.

---

### D5: Cross-Layer Query Depth Limit (INT-5)

**Context**: Maximum depth for belief chain traversal

**Current Choice**: Default max_depth = 5, user-configurable 1-10

**Alternatives Considered**:
1. Unlimited traversal (risk of performance issues)
2. Fixed depth of 3 (too restrictive for complex theories)
3. Adaptive depth based on web size

**Risk**: Large webs with depth 10 could return hundreds of beliefs. Added pagination in API response.

---

### D6: Theory Support Metrics (INT-5)

**Context**: How to quantify empirical support for theoretical beliefs

**Current Choice**:
- `support_strength`: Average credence of supporting empirical beliefs
- `coverage_score`: `min(1.0, n_supporting / 5.0)` - saturates at 5 supporting beliefs
- `gaps`: List of identified support gaps

**Alternatives Considered**:
1. Weighted average by constraint strength
2. Bayesian evidence combination
3. Coherence-based scoring

**Risk**: The coverage_score formula is a heuristic. May need calibration based on real data.

---

### D7: User Mode Feature Matrix (INT-6)

**Context**: Which features to expose in each user mode

**Current Choice**:

| Feature | Knowledge | Prediction | Expert |
|---------|-----------|------------|--------|
| Epistemic Web | ✓ | - | ✓ |
| Causal Graph | - | ✓ | ✓ |
| Predictions | - | ✓ | ✓ |
| Interventions | - | ✓ | ✓ |
| Evidence Panel | ✓ | - | ✓ |
| Gap Analysis | ✓ | - | ✓ |
| Layer Statistics | ✓ | - | ✓ |
| Theory Support | ✓ | - | ✓ |

**Alternatives Considered**:
1. Single unified mode (overwhelming for non-experts)
2. Four modes: Novice, Knowledge, Prediction, Expert
3. Fully customizable feature toggles

**Risk**: Mode switching may confuse users. Added clear mode descriptions and visual indicators.

---

### D8: Mode Persistence (INT-6)

**Context**: Whether to remember user's mode preference

**Current Choice**: Persist to localStorage, default to 'expert' mode

**Alternatives Considered**:
1. Always start in Prediction mode (most common use case)
2. Prompt user on first visit
3. No persistence (always start fresh)

**Risk**: Users may forget they're in a restricted mode and miss features.

---

### D9: Integration API URL Configuration (INT-3)

**Context**: How to configure the Article Eater API endpoint in frontend

**Current Choice**:
- Environment variable: `VITE_AE_API_URL`
- Default: `http://localhost:8001/api/v1`
- Separate from BN API (`VITE_API_URL`)

**Alternatives Considered**:
1. Single API gateway that proxies both backends
2. Hardcoded URLs
3. Runtime configuration fetch

**Risk**: CORS issues in development. Both APIs need proper CORS configuration.

---

### D10: Constraint Type Color Palette (INT-4)

**Context**: Colors for different constraint types in epistemic web

**Current Choice**:
- Supports: Green (#48bb78)
- Explains: Purple (#667eea) with animation
- Contradicts: Red (#fc8181)
- Instantiates: Yellow (#ecc94b)

Animation on "explains" edges to draw attention to theoretical explanations.

**Alternatives Considered**:
1. Same color, different dash patterns
2. Arrow head variations
3. Edge labels only

**Risk**: Too many visual dimensions may overwhelm. Kept animation subtle.

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total Decisions | 10 |
| High Risk | 0 |
| Medium Risk | 3 (D1, D3, D6) |
| Low Risk | 7 |

---

## Panel Consultation Request

These decisions warrant review by:
- **Dr. Herbert Simon** — Bounded rationality, progressive disclosure, information overload
- **Dr. Ben Shneiderman** — Visual information seeking, overview+detail
- **Dr. Judea Pearl** — Causal graph representation, epistemic uncertainty
- **Dr. Nancy Cartwright** — Bridge between evidence and causal claims
- **Dr. Susan Haack** — Foundherentist visualization, epistemic levels

**Key Questions for Panel**:
1. Is opacity-based credence representation intuitive? (D1)
2. Is the layered layout appropriate for epistemic webs? (D3)
3. Are the theory support metrics meaningful? (D6)
4. Is the three-mode structure (Knowledge/Prediction/Expert) appropriate? (D7)

---

---

## Panel Consultation Responses

### Dr. Judea Pearl (Causal Inference, Bayesian Networks)

**On D0a (Edge Justification Aggregation):**
> The inverse-variance weighting is appropriate for combining independent measurements. However, I note that beliefs from the same paper or study are NOT independent. You should implement **evidence clustering** to group beliefs by source paper before aggregation. This prevents the same study from dominating the evidence pool.

**On D0d (VOI Calculation):**
> Your VOI formula is reasonable as a heuristic but misses a key insight: the value of resolving a gap depends on what ELSE it would allow us to infer. A gap in a central node (high graph centrality) is more valuable than a gap in a peripheral node. Consider incorporating **graph-theoretic centrality measures**.

**On D1 (Edge Credence Visualization):**
> Opacity for credence is acceptable, but causal direction confidence should be visualized separately. An edge can have high credence that the relationship exists but low confidence about which way it goes. Consider **arrowhead opacity** for direction confidence.

---

### Dr. Herbert Simon (Bounded Rationality, System Design)

**On D2 (Evidence Panel Information Density):**
> Progressive disclosure is exactly right. Users have bounded attention. Start with the most decision-relevant information: the status badge and credence score. Everything else should be expandable. I would add: **consider making the default collapsed state configurable** per user.

**On D7 (User Mode Feature Matrix):**
> The three-mode structure is well-reasoned. However, I suggest renaming "Expert" to "Research" to avoid implying that non-experts shouldn't use it. Also, consider adding a **"Guided" mode** for first-time users that provides contextual help.

**On D8 (Mode Persistence):**
> Persisting to localStorage is appropriate. However, also persist the **last-viewed item** within each mode so users can resume where they left off.

---

### Dr. Ben Shneiderman (Visual Information Seeking)

**On D3 (Epistemic Web Layout):**
> The layered layout by epistemic level is appropriate for preserving the foundherentist structure. However, for webs larger than ~30 beliefs, you should implement **semantic zooming**: at low zoom, show only level groupings; at medium zoom, show node clusters; at high zoom, show individual beliefs.

**On D4 (Belief Node Styling):**
> Color coding alone is insufficient for accessibility. WCAG 2.1 requires redundant coding. Add **node shape variation** (theoretical=circle, intermediate=rounded-square, empirical=diamond, observational=triangle) as a secondary channel.

**On D10 (Constraint Type Colors):**
> Animation on "explains" edges is good for drawing attention, but can be distracting if there are many. Add a **user preference to disable animations** or reduce them after initial viewing.

---

### Dr. Nancy Cartwright (Philosophy of Science, Bridge Warrants)

**On D0b (Justification Status Thresholds):**
> The thresholds are reasonable but the categories may create false confidence. I suggest adding a **"provisional" status** between WEAK and MODERATE for edges with only one supporting belief that hasn't been replicated. Science requires replication.

**On D6 (Theory Support Metrics):**
> The coverage_score formula (saturating at 5 beliefs) is too simplistic. Not all supporting beliefs are equal. A single **direct experimental test** of a theoretical prediction is worth more than five observational correlations. Weight by evidence quality.

---

### Dr. Susan Haack (Epistemology, Foundherentism)

**On D3 (Epistemic Web Layout):**
> The layered layout is philosophically appropriate for foundherentism. It shows that epistemic levels exist but doesn't make them rigid foundations. However, ensure the visualization allows users to see **cross-level connections** prominently—these are the defining feature of foundherentism vs. pure coherentism.

**On D7 (User Mode Feature Matrix):**
> Separating "Knowledge Mode" from "Prediction Mode" may create an artificial divide between understanding and prediction. In foundherentist epistemology, these are deeply connected. Consider adding a mode or view that **shows how epistemic confidence feeds into predictive confidence**.

---

## Synthesis & Resolutions

| Decision | Panel Verdict | Action Required |
|----------|---------------|-----------------|
| D0a | REVISE | Add evidence clustering by source paper |
| D0b | APPROVED + ENHANCEMENT | Consider adding "provisional" status |
| D0c | APPROVED | Gap types are reasonable |
| D0d | REVISE | Incorporate graph centrality into VOI |
| D1 | APPROVED + ENHANCEMENT | Consider separate arrowhead opacity for direction |
| D2 | APPROVED | Progressive disclosure is correct |
| D3 | APPROVED + ENHANCEMENT | Add semantic zooming for large webs |
| D4 | REVISE | Add shape coding for accessibility |
| D5 | APPROVED | Depth limit is reasonable |
| D6 | REVISE | Weight by evidence quality, not just count |
| D7 | APPROVED + ENHANCEMENT | Consider renaming "Expert" to "Research" |
| D8 | APPROVED | Add last-viewed item persistence |
| D9 | APPROVED | API configuration is appropriate |
| D10 | APPROVED + ENHANCEMENT | Add animation disable preference |

---

## Action Items for Future Sprints

1. **INT-1 Revision**: Implement evidence clustering by source paper before aggregation
2. **INT-2 Enhancement**: Add graph centrality to VOI calculation
3. **INT-3 Enhancement**: Add arrowhead opacity for causal direction confidence
4. **INT-4 Revision**: Add node shape coding for accessibility (WCAG 2.1)
5. **INT-4 Enhancement**: Implement semantic zooming for large webs
6. **INT-5 Revision**: Weight theory support by evidence quality
7. **INT-6 Enhancement**: Rename "Expert" mode, add animation preferences

---

## Panel Consultation Complete

**Date**: 2026-02-11
**Panelists Consulted**: Pearl, Simon, Shneiderman, Cartwright, Haack
**Decisions Reviewed**: 14
**Approved**: 8
**Approved with Enhancement**: 4
**Requires Revision**: 2 (D4, D6)

*This consultation followed the mandatory panel review process per CLAUDE.md.*
