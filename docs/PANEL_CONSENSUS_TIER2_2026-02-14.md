# Panel Consensus Analysis: Epistemic Tier 2 Sprints 1-3

**Date**: Friday, February 14, 2026
**Analyst**: Claude Opus 4.5

---

## Consensus Summary

After simulating panel deliberation on the 8 key decisions, the following consensus emerged:

| Decision | Original | Panel Verdict | Action |
|----------|----------|---------------|--------|
| D1.5 Coherence warrant | 0.55 fixed | **Approve with enhancement** | Add scaling by link count |
| D1.6 Argumentative warrant | 0.70 fixed | **Approve** | Keep as-is |
| D1.7 Vigilance warrant | 0.65 fixed | **Revise** | Scale by source quality |
| D2.8 Source weights | 0.40/0.25/0.20/0.15 | **Revise** | Bump independence to 0.30 |
| D2.9 Commitment inversion | Always inverted | **Revise** | Context-dependent penalty |
| D3.1 Drift threshold | 0.10 | **Approve** | Keep as-is |
| D3.2 Asymmetry threshold | 3.0 fixed | **Approve with note** | Make configurable |
| D3.5 Adversarial boost | 1.5x | **Approve** | Keep as-is |

---

## PART I: Warrant Confidence Analysis

### D1.5: EPISTEMIC_COHERENCE_WARRANT = 0.55

**Haack (Foundherentism)**:
> "0.55 appropriately reflects that coherence provides genuine but modest epistemic support. However, the DEGREE of coherence matters. A claim supported by mutual coherence with 10 other claims has stronger warrant than one coherent with only 2."

**Spohn (Ranking Theory)**:
> "From a ranking-theoretic perspective, coherence strength should scale with the rank-sum of supporting beliefs. A fixed value ignores the cumulative nature of coherence support."

**Consensus**: Keep 0.55 as BASE, but add optional scaling factor based on coherence link count.

**Implementation**:
```python
def compute_coherence_warrant(base: float = 0.55, link_count: int = 1, max_boost: float = 0.15) -> float:
    """Scale coherence warrant by number of supporting links."""
    # Diminishing returns: sqrt scaling
    boost = min(max_boost, 0.05 * (link_count ** 0.5))
    return min(0.75, base + boost)  # Cap at 0.75
```

---

### D1.6: ARGUMENTATIVE_WARRANT = 0.70

**Pollock (Defeasible Reasoning)**:
> "Surviving adversarial scrutiny is strong evidence of robustness. 0.70 is appropriate—high enough to reward survival, not so high as to override direct evidence."

**Longino (Social Epistemology)**:
> "I accept 0.70, but note that 'adversarial' must be operationally defined. The warrant applies when critics have genuine theoretical motivation to find flaws, not merely when different labs replicate."

**Consensus**: **Approve as-is.** Document operational definition of adversarial scrutiny.

**Operational Definition**: Adversarial scrutiny occurs when:
1. Researchers from a competing theoretical tradition attempt to replicate/challenge
2. OR a meta-analysis includes studies from multiple theoretical camps
3. OR the finding has survived formal commentary/response cycles

---

### D1.7: EPISTEMIC_VIGILANCE_WARRANT = 0.65

**Cartwright (Evidence Theory)**:
> "A fixed 0.65 is inappropriate. The warrant should scale with the actual source quality score. Passing a quality check with score 0.9 warrants more confidence than passing with score 0.55."

**Consensus**: **Revise to scale with source quality.**

**Implementation**:
```python
def compute_vigilance_warrant(source_quality: float, base: float = 0.50, scale: float = 0.25) -> float:
    """Scale vigilance warrant by source quality score."""
    # Range: 0.50 (quality=0) to 0.75 (quality=1)
    return base + (scale * source_quality)
```

---

## PART II: Source Quality Analysis

### D2.8: Source Quality Weights

**Cartwright**:
> "Given the replication crisis, independence should be weighted MORE heavily. I recommend 0.30 for independence, reducing rigor to 0.35. The current weights undervalue the 'same lab, same method' problem."

**Haack**:
> "Methodological rigor remains important but shouldn't dominate. The proposed rebalancing is acceptable."

**Consensus**: **Revise weights.**

| Component | Original | Revised | Rationale |
|-----------|----------|---------|-----------|
| Methodological rigor | 0.40 | **0.35** | Still primary, but reduced |
| Independence | 0.25 | **0.30** | Elevated for replication crisis |
| Replication status | 0.20 | 0.20 | Unchanged |
| Commitment penalty | 0.15 | 0.15 | Unchanged |

---

### D2.9: Commitment Inversion

**Longino**:
> "The penalty is epistemically justified but should be CONTEXT-DEPENDENT. Confirmatory studies designed to support a specific prediction deserve full penalty. Exploratory studies within a theoretical framework deserve reduced penalty."

**Pollock**:
> "Theory-ladenness enables precise prediction. Penalizing all theoretical commitment conflates motivated reasoning with legitimate hypothesis testing. I support Longino's distinction."

**Consensus**: **Revise to context-dependent penalty.**

**Implementation**:
```python
class StudyType(str, Enum):
    CONFIRMATORY = "confirmatory"      # Full penalty (1.0x)
    EXPLORATORY = "exploratory"        # Reduced penalty (0.5x)
    REPLICATION = "replication"        # No penalty (0.0x)
    META_ANALYSIS = "meta_analysis"    # No penalty (0.0x)

COMMITMENT_PENALTY_MULTIPLIER = {
    StudyType.CONFIRMATORY: 1.0,
    StudyType.EXPLORATORY: 0.5,
    StudyType.REPLICATION: 0.0,
    StudyType.META_ANALYSIS: 0.0,
}
```

---

## PART III: Monitor Threshold Analysis

### D3.1: Coherence Drift Threshold = 0.10

**Haack**:
> "10% is a reasonable threshold for flagging. Smaller changes are within normal belief dynamics. Larger changes warrant investigation."

**Consensus**: **Approve as-is.**

---

### D3.2: Asymmetry Ratio Threshold = 3.0

**Spohn**:
> "3.0 is reasonable for general use, but should be CONFIGURABLE. Fields with few replications (like CNFA) may need different thresholds than fields with robust replication practices."

**Consensus**: **Approve but make configurable.** Add domain-specific override capability.

---

### D3.5: Adversarial Boost = 1.5x

**Pollock**:
> "1.5x represents 'careful skeptic' appropriately. Not so aggressive as to make all beliefs appear vulnerable, not so mild as to miss genuine weaknesses. Approve."

**Consensus**: **Approve as-is.**

---

## Implementation Plan

### Changes Required

1. **bridge_warrants.py**: Add `compute_coherence_warrant()` with link-count scaling
2. **bridge_warrants.py**: Add `compute_vigilance_warrant()` with quality scaling
3. **source_quality.py**: Update DEFAULT_SOURCE_QUALITY_WEIGHTS (rigor=0.35, independence=0.30)
4. **source_quality.py**: Add `StudyType` enum and context-dependent commitment penalty
5. **asymmetry_monitor.py**: Make threshold a configurable parameter (already is, just document)

### Changes NOT Required

- D1.6 (0.70): Keep as-is
- D3.1 (0.10): Keep as-is
- D3.5 (1.5x): Keep as-is

---

## Decision Log Updates

Add to TIER2_DECISIONS_LOG.md:

### D-PANEL.1: Coherence warrant scales with link count
- **Panel consensus**: Haack + Spohn agree coherence strength should scale
- **Implementation**: Base 0.55 + sqrt-scaled boost (max 0.15)
- **Cap**: 0.75 maximum warrant confidence

### D-PANEL.2: Vigilance warrant scales with source quality
- **Panel consensus**: Cartwright argues fixed value is inappropriate
- **Implementation**: 0.50 + 0.25 * source_quality
- **Range**: 0.50 to 0.75

### D-PANEL.3: Revised source quality weights
- **Panel consensus**: Independence underweighted given replication crisis
- **Implementation**: rigor=0.35, independence=0.30, replication=0.20, commitment=0.15

### D-PANEL.4: Context-dependent commitment penalty
- **Panel consensus**: Longino + Pollock agree confirmatory vs. exploratory matters
- **Implementation**: Full penalty for confirmatory, 0.5x for exploratory, 0x for replications

---

*Panel consensus analysis complete. Ready for implementation.*
