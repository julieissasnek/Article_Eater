# Semantic Matching Challenges: Theory Predictions ↔ Extracted Claims

**Date**: February 14, 2026
**Context**: Sprint 6 Pipeline Integration

---

## The Problem

We need to connect:
- **Theory predictions** (Tier 1): Abstract outcomes like "stress_recovery", "attention_restoration"
- **Extracted claims** (Tier 3): Paper-specific variables like "aged_materials → emotional_response"

But the matching is not purely lexical. It requires understanding:
1. What the paper authors actually tested (specific stimuli, comparisons)
2. How constructs relate (is "spatial perception" a proxy for "attention"?)
3. Whether the claim is evidence FOR the theory or ABOUT the theory

---

## Taxonomy of Challenges

### TYPE 1: Construct Boundary Ambiguity

**Example**: `aged_materials → emotional_response`

Is this about:
- Natural environments? (if wood, stone)
- Predictive processing? (familiar patterns → positive affect)
- Wabi-sabi aesthetics? (impermanence → emotional response)
- Something else entirely?

**The wabi-sabi problem**: Does rusty steel count as "natural"? The answer depends on:
- Cultural context (Japanese aesthetics value patina)
- What specific materials the paper tested
- How the authors framed their generalization

**Resolution requires**: Reading the paper to see what materials were actually tested.

---

### TYPE 2: Theory vs. Evidence About Theory

**Example**: `biophilia_integration → sustainability_and_well_being`

The claim mentions "biophilia_integration" in the LHS — but this is about applying the THEORY as a design principle, not about natural environment features.

- **This IS**: A design recommendation (if you apply biophilia principles, you get wellbeing)
- **This is NOT**: Empirical evidence that nature exposure → wellbeing (which would test the theory)

**Resolution requires**: Distinguishing meta-level claims (about theory application) from object-level claims (testing theory predictions).

---

### TYPE 3: Outcome Variable Mismatch

**Example**:
- Theory predicts: `directed_attention_performance`
- Claim measures: `spatial_perception`

Are these:
- The same construct measured differently? (possibly)
- Related but distinct constructs? (likely)
- Completely different things? (needs domain expertise)

**Resolution requires**: A construct validity mapping that says what instruments measure what constructs.

---

### TYPE 4: Contrast Class Inference

**Example**:
- Claim: `artificial_illumination HURTS spatial_perception`
- Theory: `natural_environments HELP attention`

Is artificial the contrast class to natural? If so:
- "Artificial hurts X" ≈ "Natural helps X" (potential confirmation)
- But only if X (spatial perception) = Y (attention)

**Resolution requires**: Knowing the paper's experimental design (what was compared to what?).

---

### TYPE 5: Critique vs. Disconfirmation

**Example**: Paper argues biophilia hypothesis is theoretically invalid (rule_type: rebuttal)

This is NOT empirical disconfirmation of a prediction.
This IS a methodological/theoretical critique of the theory itself.

**Resolution requires**: Different edge types:
- `CHALLENGES_THEORY` (for critiques)
- `DISCONFIRMS_PREDICTION` (for empirical evidence against)

---

### TYPE 6: Scope/Generalizability Uncertainty

**Example**: `lighting_colour → thermal_comfort_perception` (crossmodal effect)

Predictive Processing could explain this (brain predicts thermal state from visual cues), but:
- The theory's explicit predictions are about fractals, not color
- This is a very specific perceptual illusion
- Does the theory even claim to cover crossmodal effects?

**Resolution requires**: Understanding theory scope conditions and boundary claims.

---

## Real Examples from Data

### Challenge Instance 1: Aged Materials

**Claim** (paper: iccaua2024in0317):
```
LHS: [env.aged_materials, env.weathered_materials]
RHS: aff.emotional_response
Polarity: positive
```

**Candidate Theory**: Stress Recovery Theory
**Prediction**: stress_recovery (positive) for landscapes with scattered_trees, water

**Problem**: The theory specifies savanna-like features. Aged materials evoke time/authenticity, not savanna. This might be:
- Unrelated to SRT entirely
- Better matched to Predictive Processing (familiarity → positive affect)
- A novel mechanism not covered by existing theories

---

### Challenge Instance 2: Biophilia Meta-Claim

**Claim** (paper: archnet-ijar.v9i2.464):
```
LHS: [theory.biomimicry_approach, theory.biophilia_integration, env.historical_architecture_examples]
RHS: aff.sustainability_and_well_being
Polarity: positive
Rule_type: presumption
```

**Candidate Theory**: Biophilia Hypothesis
**Prediction**: occupant_wellbeing (positive) for built environments with plants, natural_materials, water, daylight

**Problem**: This is a theoretical presumption (rule_type: presumption) that APPLYING biophilia principles leads to wellbeing. It's an argument FOR biophilia, not evidence TESTING biophilia. Should create a different edge type.

---

### Challenge Instance 3: Glass Curtain Walls

**Claim** (paper: ryerson.14655804.v1):
```
LHS: [env.glass_curtain_wall, env.artificial_illumination, env.homogeneous_lighting]
RHS: cog.spatial_perception
Polarity: negative
```

**Candidate Theory**: Attention Restoration Theory
**Prediction**: directed_attention_performance (positive) for natural environments

**Problem**:
- The claim is NEGATIVE (artificial hurts), theory is POSITIVE (natural helps)
- The outcome is spatial_perception, not attention
- Is this a disconfirmation? A confirmation by contrast? Or orthogonal?

---

## Implications

### No Purely Algorithmic Solution

The matching problem requires:

1. **Access to papers**: Need to read what authors actually did
   - What specific materials/stimuli did they test?
   - What was the comparison condition?
   - How did they operationalize outcomes?

2. **Construct mapping**: Need domain expertise
   - Is "spatial perception" a proxy for "attention"?
   - Does "emotional response" include "stress recovery"?

3. **Theory scope understanding**: Need to know boundary conditions
   - What does biophilia claim to explain?
   - What is outside predictive processing scope?

4. **Edge type selection**: Different relationships need different edges
   - CONFIRMS_PREDICTION (empirical support)
   - DISCONFIRMS_PREDICTION (empirical challenge)
   - CHALLENGES_THEORY (methodological critique)
   - EXTENDS_THEORY (expands scope)
   - ORTHOGONAL (different domain entirely)

---

## Proposed Approach

### Option A: Human-in-the-Loop

1. **Generate candidate matches** using keyword overlap + embeddings
2. **Surface for expert review** with structured questions:
   - What did the paper actually test?
   - Is this claim evidence FOR, ABOUT, or AGAINST the theory?
   - What edge type is appropriate?
3. **Build curated mapping table** from reviewed examples

### Option B: Extraction-Time Annotation

During PDF extraction, ask the LLM:
- Does this paper test any known theory predictions?
- If so, which ones, and what was the result (confirm/disconfirm/mixed)?
- What constructs does this operationalize?

Store these as explicit `theory_links` in the extraction output.

### Option C: Hybrid

1. Use extraction-time annotation for new papers
2. Use candidate generation + human review for existing corpus
3. Build construct taxonomy iteratively from reviewed examples

---

## Files Created

- `src/epistemic/extraction/rule_to_claim_mapper.py` — Basic ae.rule.v2 → ClaimV2 conversion
- `tests/test_rule_to_claim_mapper.py` — Tests for the mapper
- This document — Analysis of the matching challenge

---

## Next Steps

1. **Decide on approach** (A, B, C, or other)
2. **If human-in-the-loop**: Build UI for expert review
3. **If extraction-time**: Add theory-link prompts to extraction templates
4. **Either way**: Start building construct taxonomy from concrete examples
