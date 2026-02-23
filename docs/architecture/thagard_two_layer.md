# Thagard Two-Layer Architecture (EC-1)

## Summary

The system now explicitly follows a two-layer explanatory coherence architecture:

1. **Epistemic Coherence Layer** (`src/services/web_of_belief.py`)
2. **Causal Inference Layer** (`src/services/epistemic_causal_bridge.py`)

This mirrors Thagard-style coherence: candidate explanations are evaluated by
their support/contradiction structure before downstream causal use.

## Layer 1: Epistemic Coherence

- Core object: `WebOfBelief`
- Unit: `Belief` nodes + `Constraint` edges
- Function:
  - maintain coherence under mutual support/tension
  - compute entrenchment and belief value (`belief_value`)
  - identify high-value beliefs for targeted revision

Outputs of Layer 1:
- coherence-scored belief network
- ranked beliefs for investigation
- contradiction/tension structure

## Layer 2: Causal Inference

- Core object: `EpistemicCausalBridge`
- Function:
  - derive theory-relative causal models from high-credence beliefs
  - run interventions/counterfactuals under epistemic constraints
  - apply contrast and transportability checks before transfer

Inputs from Layer 1:
- beliefs above inclusion thresholds
- coherence-conditioned constraints
- scope and provenance metadata

## Why Two Layers

- Prevents “causal model from raw extraction” failure mode.
- Forces explanatory and evidential coherence checks before intervention claims.
- Keeps uncertainty visible rather than collapsed into a single posterior number.

## Implementation Note

`src/services/epistemic_causal_bridge.py` consumes web beliefs directly, so the
coherence layer remains epistemically prior while still allowing fast causal queries.
