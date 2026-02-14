# Panel Consensus: Epistemic Tier 2 — Sprints 4 + 4b

**Date**: Friday, February 14, 2026
**Panel**: Haack, Pollock, Longino, Cartwright, Pearl, Kaplan (simulated)
**Purpose**: Record panel consensus on Sprint 4/4b decisions

---

## Executive Consensus

**Proceed to Sprint 5**: YES, with the revisions noted below.

The panel found the Sprint 4/4b implementation sound with several targeted refinements needed.

---

## PART I: Sprint 4 Decisions — APPROVED with Notes

### D4.1: Argumentative Structure Extraction

**Panel Consensus**: APPROVED

**Pollock's Comment**: The weighted approach is appropriate for defeasible reasoning. However, I recommend treating "challenges" and "contradicts" patterns with equivalent weight to "supports" — defeat and confirmation are epistemically symmetric.

**Haack's Comment**: The distinction between "consistent with" (0.7) and "confirms" (1.0) is appropriate. Coherence is weaker than confirmation.

**No changes required.**

---

### D4.2: Replication Type Hierarchy

**Panel Consensus**: APPROVED

**Cartwright's Comment**: The hierarchy aligns with evidence-based medicine principles. Meta-analysis > direct replication is correct.

**No changes required.**

---

### D4.3: Adversarial Scrutiny Detection

**Panel Consensus**: APPROVED with REFINEMENT

**Longino's Comment**: Single indicator is too permissive. I recommend requiring EITHER:
- Two weak indicators (e.g., "independent" + "critics"), OR
- One strong indicator (e.g., "registered report", "multi-lab", "adversarial collaboration")

**REVISION D-PANEL.5**: Tiered adversarial detection
- Strong indicators (any one sufficient): registered_report, multi-lab, adversarial_collaboration
- Weak indicators (require two): independent_lab, different_tradition, competing_hypothesis, critics

---

### D4.4: Three-Pathway Classification

**Panel Consensus**: APPROVED

**Pearl's Comment**: The keyword-based approach is appropriate for initial classification. The conservative MIXED default is correct — uncertainty should not be resolved arbitrarily.

**No changes required.**

---

### D4.5: PE Indicator Requirement

**Panel Consensus**: APPROVED

**Conservative approach endorsed by all panelists.**

---

## PART II: Sprint 4b Decisions — APPROVED with Revisions

### D4b.1: Task-Ecological Validity Weights

**Panel Consensus**: APPROVED with ADJUSTMENT

**Kaplan's Comment**: The 0.30 weight for task_authenticity appropriately captures the passive observer concern. This is the central issue.

**Haack's Comment**: State characterization at 0.20 is acceptable, but I recommend the system FLAG when state_characterization = 0.0 (completely unmeasured) as a distinct epistemic vulnerability.

**REVISION D-PANEL.6**: Add state_characterization_warning when all state dimensions are 0.0

---

### D4b.2: Task Authenticity Score Hierarchy

**Panel Consensus**: APPROVED with CLARIFICATION

**Kaplan's Comment**: 0.2 for EXPLICIT_EVALUATION is appropriate — this is not zero, acknowledging that aesthetic judgment has value, but it fundamentally differs from ecological tasks.

**Cartwright's Comment**: The TSST question is important. When a simulated task genuinely stresses participants (not play-acting), it should score higher. However, this is correctly captured by the SIMULATED_ECOLOGICAL category at 0.6.

**No changes required.**

---

### D4b.3: Construct Validity Maps

**Panel Consensus**: APPROVED with STRONG CAVEATS

**Longino's Comment**: These values MUST be marked as provisional. I recommend:
1. Add `provenance` field to each validity score
2. Add `confidence_level` to indicate empirical support

**Cartwright's Comment**: Values >0.8 should require explicit citation. The 0.86 photo-preference value is well-supported (Stamps 1990), but values like 0.95 for cortisol→HPA need clearer sourcing.

**Kaplan's Comment**: The photo-to-in-situ estimates are defensible for preference (Stamps meta-analysis), but the 0.20 for wayfinding may be too generous — photos provide zero wayfinding information.

**REVISION D-PANEL.7**:
1. Change photographs_2d wayfinding validity from 0.20 to 0.10
2. Add `ProfileStatus.PROVISIONAL` marker for values without explicit citations
3. Document that high (>0.8) values should be considered provisional until validated

---

### D4b.4: Auto-Challenge Generation Thresholds

**Panel Consensus**: APPROVED with REFINEMENT

**Cartwright's Comment**: The 20-minute threshold for cortisol is conservative but correct. Literature suggests 15-20 min onset, 20-40 min peak. Sampling before 20 min measures baseline, not response.

**Pollock's Comment**: Auto-challenges should include a confidence level. I recommend:
- `confidence: 0.9` for temporal_misalignment (well-established physiology)
- `confidence: 0.7` for construct_presentation_mismatch (depends on construct definition)
- `confidence: 0.8` for vr_confound_uncontrolled (documented issue)

**REVISION D-PANEL.8**: Add challenge_confidence field to ClaimValidityResult
- temporal_misalignment: 0.9
- construct_presentation_mismatch: 0.7
- vr_confound_uncontrolled: 0.8
- single_modality: 0.6
- attention_directed: 0.7

---

### D4b.5: Channel Requirements for Constructs

**Panel Consensus**: APPROVED with REFINEMENT

**Kaplan's Comment**: The claim that stress_response requires no specific channels is defensible but should be nuanced. Visual-only stress response is valid for ACUTE stress from threatening imagery, but CHRONIC stress effects (allostatic load) require full ecological exposure.

**REVISION D-PANEL.9**: Split stress_response into:
- acute_stress_response: [] (no channel requirements)
- chronic_stress_effects: [temporal_extended, ecological_exposure] (requires prolonged real exposure)

---

### D4b.6: Generalizability Warrant

**Panel Consensus**: APPROVED with CONDITIONAL WEIGHTING

**Longino's Comment**: The 0.5 default is reasonable, but should vary by presentation modality as follows:
- real_building → real_building: 0.9 (nearly direct transfer)
- vr_hmd_room_scale → real_building: 0.6
- vr_hmd_stationary → real_building: 0.5
- photographs_2d → real_building: 0.35

**Pearl's Comment**: From a causal perspective, the warrant weight should reflect the causal pathway fidelity. The modality-conditional weights proposed by Longino are appropriate.

**REVISION D-PANEL.10**: Implement modality-conditional generalizability warrant weights
```python
GENERALIZABILITY_WEIGHTS = {
    "real_building_controlled": 0.9,
    "vr_cave": 0.7,
    "vr_hmd_room_scale": 0.6,
    "vr_hmd_stationary": 0.5,
    "photographs_2d": 0.35,
}
```

---

## PART III: Cross-Cutting Concerns — Panel Guidance

### Concern A: Method Registry Versioning

**Panel Consensus**: YES, versioning is needed

**Longino's Recommendation**: Each validity value should have:
- Version number
- Date added/modified
- Source citation (if available)
- Confidence level (provisional/established/validated)

**Defer to Sprint 5**: Add basic versioning infrastructure; full provenance tracking can be Sprint 6.

---

### Concern B: Task Ecology vs. Source Quality

**Panel Consensus**: KEEP SEPARATE

**Haack's Comment**: Task-ecological validity addresses a distinct epistemic concern (ecological generalization) from source quality (internal validity). They should remain separate in the four-channel model.

**No changes required.**

---

### Concern C: Missing Construct Defaults

**Panel Consensus**: DEFAULT TO 0.3 (not 0.0 or 0.5)

**Rationale**:
- 0.0 is too harsh (assumes no validity)
- 0.5 is too generous (assumes unknown = neutral)
- 0.3 reflects conservative uncertainty with a mild penalty

**REVISION D-PANEL.11**: Change default construct validity from 0.0 to 0.3 for missing entries

---

## Summary of Panel-Approved Revisions

| ID | Revision | Applies To | Priority |
|----|----------|------------|----------|
| D-PANEL.5 | Tiered adversarial detection | D4.3 | Sprint 5 |
| D-PANEL.6 | State characterization warning at 0.0 | D4b.1 | Sprint 5 |
| D-PANEL.7 | Photo wayfinding 0.20→0.10; add provisional markers | D4b.3 | Immediate |
| D-PANEL.8 | Challenge confidence levels | D4b.4 | Sprint 5 |
| D-PANEL.9 | Split stress_response into acute/chronic | D4b.5 | Sprint 5 |
| D-PANEL.10 | Modality-conditional generalizability weights | D4b.6 | Immediate |
| D-PANEL.11 | Default construct validity 0.0→0.3 | D4b.3 | Immediate |

---

## Implementation Priority

### Immediate (Before Sprint 5):
1. **D-PANEL.7**: Update photographs_2d wayfinding validity to 0.10
2. **D-PANEL.10**: Implement modality-conditional generalizability weights
3. **D-PANEL.11**: Change default construct validity to 0.3

### Sprint 5 (Integration):
4. **D-PANEL.5**: Tiered adversarial detection
5. **D-PANEL.6**: State characterization warning
6. **D-PANEL.8**: Challenge confidence levels
7. **D-PANEL.9**: Acute/chronic stress split

---

## Panel Sign-Off

All panelists approve proceeding to Sprint 5 (Integration Testing) with the immediate revisions implemented.

| Panelist | Approval | Key Concern Addressed |
|----------|----------|----------------------|
| Haack | YES | State characterization warning |
| Pollock | YES | Challenge confidence levels |
| Longino | YES | Provisional markers, modality weights |
| Cartwright | YES | Temporal thresholds, channel requirements |
| Pearl | YES | Pathway classification, warrant weights |
| Kaplan | YES | Task authenticity scores, photo validity |

---

*Panel consensus document prepared by Claude Opus 4.5*
*Simulated deliberation for Article Eater Epistemic Tier 2*
*Date: 2026-02-14*
