# User Guide: Epistemic-Causal Bridge

*Version: ECB-3 (2026-02-10)*

This guide explains how to use Article Eater's causal inference features, which bridge the Quinean epistemic layer with Pearlian causal inference.

---

## Overview

The Epistemic-Causal Bridge lets you:
1. **Build causal models** from your web of belief
2. **Run counterfactual queries** ("What if we increased nature exposure?")
3. **Assess generalization** across populations (via van Fraassen contrast classes)
4. **Identify epistemic gaps** that warrant further research

### Philosophical Foundation

The bridge implements **foundherentism** (Haack, 1993):
- Epistemic layer is PRIOR to causal layer
- You cannot build a causal model without knowing what the field believes
- The epistemic layer constrains, informs, and qualifies causal inference

---

## Quick Start

### CLI Usage

```bash
# Run pipeline with causal bridge (default)
./bin/article_eater eat --in corpus/pdfs --out output/

# Disable causal bridge
./bin/article_eater eat --in corpus/pdfs --out output/ --no-causal

# Set credence threshold for causal models
./bin/article_eater eat --in corpus/pdfs --out output/ --causal-credence-threshold 0.6
```

### Python API

```python
from src.services.web_of_belief import WebOfBelief
from src.services.epistemic_causal_bridge import EpistemicCausalBridge

# Create or load a web of belief
web = WebOfBelief(domain="neuroarchitecture")
# ... add beliefs and constraints ...

# Create the bridge
bridge = EpistemicCausalBridge(web)

# Build causal models from high-credence beliefs
model = bridge.build_causal_models(credence_threshold=0.5)

# Run a counterfactual query
result = bridge.counterfactual(
    intervention={"nature_exposure": 1},
    outcome="stress_reduction"
)

print(f"Estimate: {result.point_estimate:.2f}")
print(f"CI: {result.confidence_interval}")
print(f"Epistemic quality: {result.epistemic_quality:.2f}")
```

---

## Key Concepts

### Contrast Classes (van Fraassen)

A contrast class specifies WHAT you're comparing. "Does nature reduce stress?" is meaningless without knowing:
- Compared to WHAT? (urban environment? indoor?)
- For WHOM? (office workers? patients? children?)
- Under WHAT conditions? (30 minutes? 8 hours?)

```python
from src.services.epistemic_causal_bridge import (
    ContrastClass, ConditionSpec, ContrastType
)

# Define explicit contrast class
contrast = ContrastClass(
    contrast_id="nature_vs_urban",
    focal=ConditionSpec(
        variable="environment",
        value="forest",
        description="Forest exposure"
    ),
    contrasts=[ConditionSpec(
        variable="environment",
        value="urban",
        description="Urban environment"
    )],
    contrast_type=ContrastType.ALTERNATIVE,
    explicit=True  # From paper methods section
)

# Use in counterfactual
result = bridge.counterfactual(
    intervention={"nature_exposure": 1},
    outcome="stress",
    contrast_class=contrast
)
```

### Contrast Transfer Types

When generalizing across populations, the bridge classifies transfer validity:

| Type | Similarity | Meaning | Result |
|------|------------|---------|--------|
| **DIRECT** | ≥ 0.90 | Contrast classes are equivalent | Full transfer |
| **BASELINE_SHIFT** | ≥ 0.70 | Same construct, different baseline | Adjust for ceiling/floor |
| **POPULATION_SHIFT** | ≥ 0.50 | Different population, similar construct | Increased uncertainty |
| **MEANING_SHIFT** | < 0.50 | Construct means different things | **Result undefined** |

When transfer type is MEANING_SHIFT, the result's `is_defined` is `False`:

```python
result = bridge.counterfactual(...)
if not result.is_defined:
    print(f"Result undefined: {result.reason_undefined}")
```

### Configuring Thresholds

Thresholds can be adjusted via environment variables:

```bash
export AE_CONTRAST_THRESHOLD_DIRECT=0.95    # Stricter DIRECT threshold
export AE_CONTRAST_THRESHOLD_BASELINE=0.75  # Stricter BASELINE_SHIFT
export AE_CONTRAST_THRESHOLD_POPULATION=0.6 # Stricter POPULATION_SHIFT
```

---

## Understanding Results

### QuineanCounterfactualResult

Every counterfactual returns a `QuineanCounterfactualResult` with:

```python
result.point_estimate      # Central effect estimate
result.confidence_interval # (lower, upper) bounds
result.epistemic_quality   # 0.0-1.0 overall quality score
result.is_defined          # False if contrast transfer failed
result.reason_undefined    # Why result is undefined (if applicable)

# Detailed assessments
result.robustness          # How robust is this estimate?
result.coherence           # Is it coherent with the web?
result.scope               # Are we extrapolating?
result.contrast            # Contrast transfer assessment
result.gaps                # Epistemic gaps identified
```

### Robustness Analysis

Shows how sensitive the result is to belief changes:

```python
print(f"Robustness score: {result.robustness.robustness_score:.2f}")
print(f"Sensitive beliefs: {result.robustness.sensitive_beliefs}")
```

### Epistemic Gaps

The bridge identifies gaps that warrant further research:

```python
for gap in result.gaps:
    print(f"Gap: {gap.gap_type} - {gap.description}")
    print(f"Priority: {gap.priority:.2f}")
    print(f"Suggested query: {gap.suggested_query}")
```

Gap types:
- `missing_contrast`: Source beliefs lack explicit contrast class
- `low_coverage`: Limited evidence for target population
- `theory_conflict`: Theories disagree significantly
- `baseline_unknown`: Missing baseline data
- `blocked_beliefs`: Enabling conditions unmet

---

## Security Weight (Haack)

The bridge computes "security" — how well-grounded beliefs are in experience:

```python
security = bridge.compute_security()
print(f"Mean security: {security['mean_security']:.2f}")
print(f"Empirical ratio: {security['empirical_ratio']:.1%}")
print(f"Explicit contrast ratio: {security['explicit_contrast_ratio']:.1%}")

# Per-belief security
for belief_id, score in security['belief_securities'].items():
    print(f"  {belief_id}: {score:.2f}")
```

Security weights:
- Observational beliefs: 0.9 base
- Empirical beliefs: 0.7 base
- Theoretical beliefs: 0.3 base
- +0.15 for explicit contrast class
- +0.10 for entrenched status

---

## Feedback Loop

The bridge can update the web based on counterfactual results:

```python
# Run counterfactual
result = bridge.counterfactual(
    intervention={"nature_exposure": 1},
    outcome="stress"
)

# Update web based on findings
updates = bridge.update_web_from_result(result)

print(f"Updated {updates['n_beliefs_updated']} beliefs")
for update in updates['updates']:
    print(f"  {update['belief_id']}: {update['type']}")
```

**Important**: The feedback loop is gated by contrast transfer. If the result is undefined or has MEANING_SHIFT, no updates are made:

```python
if updates.get('gated'):
    print(f"Feedback gated: {updates['gate_reason']}")
```

---

## Pipeline Integration

When running the full pipeline, causal results are included in `web_state.json`:

```json
{
  "causal_bridge": {
    "built": true,
    "enabled": true,
    "summary": {
      "n_theories": 3,
      "theories": ["ART", "SRT", "Biophilia"],
      "n_variables": 12,
      "credence_threshold": 0.5
    },
    "warning": null
  },
  "warnings": []
}
```

If the causal layer fails, you'll see a prominent warning:

```json
{
  "causal_bridge": {
    "built": false,
    "warning": "CAUSAL LAYER FAILED: ..."
  },
  "warnings": ["CAUSAL LAYER FAILED: Results do not include causal inference annotations"]
}
```

---

## Troubleshooting

### "Result undefined" errors

This means contrast classes don't transfer. Check:
1. Are source and target populations similar?
2. Do constructs mean the same thing in both contexts?
3. Consider lowering `AE_CONTRAST_THRESHOLD_POPULATION`

### Empty causal models

If `build_causal_models()` returns no theories:
1. Check if beliefs have theory associations
2. Lower the credence threshold
3. Verify beliefs are THEORETICAL or INTERMEDIATE level

### Feedback loop not updating

The feedback loop is gated. Check:
1. Is `result.is_defined` True?
2. Is `result.contrast.transfer_type` not MEANING_SHIFT?
3. Use `update_mode="track_only"` to just track without updating

---

## API Reference

### EpistemicCausalBridge

```python
bridge = EpistemicCausalBridge(web)

# Build models
model = bridge.build_causal_models(
    credence_threshold=0.5,      # Minimum credence for beliefs
    include_theories=None        # Specific theories, or all
)

# Run counterfactual
result = bridge.counterfactual(
    intervention={"var": value},  # do(var=value)
    outcome="outcome_var",        # Query variable
    evidence=None,                # Conditioning evidence
    contrast_class=None,          # Explicit contrast class
    target_population=None        # Target population ID
)

# Compute security
security = bridge.compute_security(belief_ids=None)

# Update web from result
updates = bridge.update_web_from_result(
    result,
    update_mode="uncertainty_only"  # or "full" or "track_only"
)
```

### ContrastTransferType

```python
from src.services.epistemic_causal_bridge import ContrastTransferType

ContrastTransferType.DIRECT          # ≥0.90 similarity
ContrastTransferType.BASELINE_SHIFT  # ≥0.70 similarity
ContrastTransferType.POPULATION_SHIFT # ≥0.50 similarity
ContrastTransferType.MEANING_SHIFT   # <0.50 similarity (undefined)
ContrastTransferType.UNDEFINED       # Cannot assess
```

---

## Further Reading

- `docs/ARCHITECTURE.md` — System architecture with causal layer diagram
- `docs/PANEL_CONSULTATION_ECB_FULL_REVIEW_2026-02-10.md` — Panel review of design decisions
- Pearl, J. (2009). *Causality*. Cambridge University Press.
- van Fraassen, B. (1980). *The Scientific Image*. Oxford University Press.
- Haack, S. (1993). *Evidence and Inquiry*. Blackwell.
