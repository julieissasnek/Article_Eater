# Panel Review: Epistemic Tier 2 — Sprints 1-3

**Date**: Friday, February 14, 2026
**Reviewer**: Claude Opus 4.5 (implementation agent)
**Purpose**: Expert panel consultation on key epistemic design decisions before Sprint 4/4b

---

## Executive Summary

Sprints 1-3 of Epistemic Tier 2 are complete. Before proceeding to Sprint 4 (Extraction Pipeline) and Sprint 4b (Method Registry), the following decisions require panel review:

| Category | Decisions | Primary Concern |
|----------|-----------|-----------------|
| **Warrant Confidences** | D1.5, D1.6, D1.7 | How much should different warrant types boost belief credence? |
| **Source Quality Weights** | D2.8, D2.9 | How should evidence quality components be weighted? |
| **Monitor Thresholds** | D3.1, D3.2, D3.5 | When should reflexive monitors flag vulnerabilities? |

---

## Panel Composition

| Panelist | Expertise | Relevant Decisions |
|----------|-----------|-------------------|
| **Spohn** | Ranking theory, belief revision | D1.5, D3.2 (rank calibration) |
| **Haack** | Foundherentism, coherence | D1.5, D2.8, D3.1 (coherence weights) |
| **Pollock** | Defeasible reasoning, defeat | D1.6, D3.5 (adversarial scrutiny) |
| **Longino** | Social epistemology | D1.6, D2.9 (social epistemics, bias) |
| **Cartwright** | Causal inference, evidence | D1.7, D2.8 (source reliability) |
| **Pearl** | Structural equations, BN | D2.6 (edge weights, causal semantics) |

---

## PART I: Warrant Confidence Defaults (Sprint 1)

### D1.5: EPISTEMIC_COHERENCE_WARRANT = 0.55

**Decision**: Set default confidence for coherence-based warrants to 0.55.

**Context**: When a claim gains support purely through coherence with other claims (no direct empirical scrutiny), how much should this boost its credence?

**Rationale**:
- 0.55 is above neutral (0.5) but modest
- Coherence provides genuine epistemic support (Quine, BonJour)
- But coherence alone, without scrutiny, is weaker than tested claims

**Alternatives Considered**:
- 0.40: Too dismissive of coherence (foundationalist bias)
- 0.70: Too generous (coherentist overreach)

**Risk**: Medium — affects how untested theoretical claims propagate credence through the web

**Questions for Panel**:
1. **Haack**: Does 0.55 appropriately balance foundherentist intuitions? Should coherence alone ever exceed 0.6?
2. **Spohn**: How does this interact with ranking theory? Should coherence warrants have variable strength based on number of supporting beliefs?

---

### D1.6: ARGUMENTATIVE_WARRANT = 0.70

**Decision**: Set default confidence for argumentative warrants (survived adversarial scrutiny) to 0.70.

**Context**: When a claim has been tested by researchers from rival theoretical traditions and survived, how much confidence boost is warranted?

**Rationale**:
- Adversarial testing is a strong epistemic filter
- Survival indicates robustness to motivated criticism
- 0.70 reflects significant but not overwhelming confidence

**Alternatives Considered**:
- 0.60: Same as mechanism warrant (doesn't reward adversarial survival)
- 0.80: May overweight adversarial studies (selection bias concerns)

**Risk**: Medium — may systematically favor claims from contentious domains

**Questions for Panel**:
1. **Pollock**: Is 0.70 appropriate given your work on defeat? Should survival of strong defeaters warrant higher confidence?
2. **Longino**: From a social epistemics perspective, does this appropriately value community scrutiny? Any concerns about defining "adversarial"?

---

### D1.7: EPISTEMIC_VIGILANCE_WARRANT = 0.65

**Decision**: Set default confidence for epistemic vigilance warrants (source quality evaluation) to 0.65.

**Context**: When a claim has undergone explicit source quality assessment, how much should passing that assessment boost credence?

**Rationale**:
- Explicit quality check adds confidence beyond passive acceptance
- 0.65 is between coherence (0.55) and adversarial (0.70)
- Reflects that quality assessment is valuable but not equivalent to adversarial testing

**Alternatives Considered**:
- 0.55: Same as coherence (doesn't reward explicit evaluation)
- 0.70: Same as adversarial (conflates different epistemic virtues)

**Risk**: Medium — depends on accuracy of source quality assessment

**Questions for Panel**:
1. **Cartwright**: Given your work on evidence, is 0.65 appropriate for quality-vetted claims? Should this vary by quality score?

---

## PART II: Source Quality Weights (Sprint 2)

### D2.8: Source Quality Component Weights

**Decision**: Weight source quality components as:
- Methodological rigor: 0.40
- Independence of evidence: 0.25
- Replication status: 0.20
- Theoretical commitment (inverted): 0.15

**Context**: How should we combine four dimensions of source quality into a composite score?

**Rationale**:
- Methodological rigor is most directly indicative of internal validity
- Independence addresses "same lab, same method" problem
- Replication is gold standard but often unavailable
- Commitment penalty is smallest because some commitment enables hypothesis testing

**Alternatives Considered**:
- Equal weights (0.25 each): Ignores differential importance
- Literature-derived: No clear consensus exists

**Risk**: Medium — these weights directly affect which claims are accepted

**Questions for Panel**:
1. **Cartwright**: Given your work on external validity, should independence be weighted higher (>0.25)?
2. **Haack**: Does the methodological rigor emphasis reflect foundherentist principles appropriately?

---

### D2.9: Theoretical Commitment Inverted

**Decision**: High theoretical commitment REDUCES source quality score.

**Formula**: `commitment_contribution = weight * (1.0 - theoretical_commitment)`

**Context**: Should a priori theoretical commitment be penalized in source quality assessment?

**Rationale**:
- Confirmation bias literature supports penalty for high commitment
- Studies designed to confirm a specific theory may have biased designs
- Inverted weight captures this as a quality reduction

**Alternatives Considered**:
- Positive influence: Some commitment enables precise predictions
- Separate bias metric: More complex, harder to interpret

**Risk**: Medium — may unfairly penalize theory-driven science

**Questions for Panel**:
1. **Longino**: From social epistemics, is this the right way to handle theory-ladenness?
2. **Pollock**: Does this conflict with your views on how theoretical background enables perception?

**CRITICAL CONCERN**: This decision may systematically disadvantage hypothesis-driven research. Should commitment penalty be context-dependent (e.g., only for confirmatory studies)?

---

## PART III: Monitor Thresholds (Sprint 3)

### D3.1: Coherence Drift Threshold = 0.1

**Decision**: Flag nodes whose entrenchment changed by >10% due to coherence settling (not direct evidence).

**Context**: When is coherence-driven entrenchment change significant enough to warrant attention?

**Rationale**:
- 10% represents a meaningful shift in credence
- Lower threshold would generate too many false positives
- Higher threshold might miss important cascades

**Alternatives Considered**:
- 0.05: More sensitive, but may overwhelm with alerts
- 0.20: Less sensitive, may miss important drift

**Risk**: Medium — affects how much "coherence free-riding" we detect

**Questions for Panel**:
1. **Haack**: What magnitude of coherence-driven change should trigger epistemic concern?

---

### D3.2: Asymmetry Ratio Threshold = 3.0

**Decision**: Flag nodes where entrenchment/direct_evidence ratio exceeds 3.0.

**Context**: When is a belief's credence disproportionately derived from coherence vs. direct support?

**Rationale**:
- 3x suggests belief is more "network-supported" than "evidence-supported"
- Lower threshold would flag too many well-connected beliefs
- Higher threshold might miss genuinely vulnerable claims

**Alternatives Considered**:
- 2.0: Stricter (more flags)
- 5.0: More lenient (fewer flags)

**Risk**: Medium — threshold affects which beliefs are flagged as vulnerable

**Questions for Panel**:
1. **Spohn**: From ranking theory perspective, when does coherence-derived credence become epistemically problematic?

---

### D3.5: Adversarial Precision Boost = 1.5x

**Decision**: In adversarial review, multiply counter-evidence weight by 1.5.

**Context**: How aggressively should we stress-test entrenched beliefs?

**Rationale**:
- 1.5x simulates a "careful skeptic" rather than "hostile critic"
- Identifies beliefs that would fail under moderate scrutiny
- Higher boost might make all beliefs appear vulnerable

**Alternatives Considered**:
- 1.2x: Very mild skepticism
- 2.0x: Aggressive skepticism

**Risk**: Medium — affects which beliefs are flagged as vulnerable

**Questions for Panel**:
1. **Pollock**: Given your work on defeat, what level of "skeptical pressure" is appropriate for stress testing?

---

## PART IV: Cross-Cutting Concerns

### Concern A: Calibration Interdependence

Several decisions interact:
- D1.5 (coherence warrant = 0.55) + D3.1 (drift threshold = 0.1) + D3.2 (asymmetry = 3.0)

If coherence warrants are too generous (higher D1.5), asymmetry monitor (D3.2) becomes more important.

**Question for Panel**: Should these be calibrated together? Should asymmetry threshold depend on warrant confidence levels?

---

### Concern B: CNFA Domain Specificity

These defaults were chosen with CNFA (cognitive neuroscience of architecture) in mind:
- Field has high theoretical commitment (many frameworks, few replications)
- Most studies use single methods (self-report OR physiology, rarely both)
- Independence is low (small field, repeated collaborations)

**Question for Panel**: Should defaults be adjustable per-domain? Or should we maintain universal thresholds for consistency?

---

### Concern C: Sprint 4b Method Registry Impact

Sprint 4b will introduce:
- Task-ecological validity scores
- Method profile registry
- Claim type bifurcation (Type A vs Type B)

These may interact with source quality weights (D2.8).

**Question for Panel**: Any concerns about the current weights that should be addressed BEFORE Sprint 4b introduces additional complexity?

---

## Panel Decisions Requested

Please provide guidance on:

1. **Warrant Confidences (D1.5-D1.7)**: Are the proposed values appropriate? Should any be adjusted?

2. **Source Quality Weights (D2.8)**: Is the weighting scheme defensible? Any components missing or overweighted?

3. **Commitment Inversion (D2.9)**: Is penalizing theoretical commitment the right approach? Should it be context-dependent?

4. **Monitor Thresholds (D3.1, D3.2, D3.5)**: Are these calibrated appropriately? Should they be adjustable?

5. **Proceed to Sprint 4/4b?**: Any blocking concerns that must be resolved first?

---

## Appendix: Decision Summary Table

| ID | Decision | Value | Risk | Primary Panelists |
|----|----------|-------|------|-------------------|
| D1.5 | EPISTEMIC_COHERENCE_WARRANT | 0.55 | Medium | Spohn, Haack |
| D1.6 | ARGUMENTATIVE_WARRANT | 0.70 | Medium | Pollock, Longino |
| D1.7 | EPISTEMIC_VIGILANCE_WARRANT | 0.65 | Medium | Cartwright |
| D2.8 | Source quality weights | 0.40/0.25/0.20/0.15 | Medium | Cartwright, Haack |
| D2.9 | Commitment inversion | 1 - commitment | Medium | Longino, Pollock |
| D3.1 | Coherence drift threshold | 0.10 | Medium | Haack |
| D3.2 | Asymmetry ratio threshold | 3.0 | Medium | Spohn |
| D3.5 | Adversarial precision boost | 1.5x | Medium | Pollock |

---

*Panel review document prepared by Claude Opus 4.5*
*Implementation: Article Eater Epistemic Tier 2*
*Date: 2026-02-14*
