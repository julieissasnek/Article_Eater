# CVA-1-REV: Constraint Variable Registry Specification

**Sprint CVA-1-REV — Phase A: Foundation**
**Reference**: CVA Sprint Plan §CVA-1, Revised Specs §Three Hard Problems

---

## Registry Overview

The CVA constraint space is a 14-dimensional vector:
- **Tier 1** (6 primitives): approximately invariant across subjects, decline only with aging
- **Tier 2** (8 interpretive constraints): ψ-calibrated — same scene produces different constraint values for different subjects

```
c = [c_Tier1, c_Tier2(ψ)]
c_Tier1 = f_universal(x; a, ν_sensory)      [6D]
c_Tier2 = g(c_Tier1; θ(ψ))                  [8D]
```

---

## Tier 1: Universal Perceptual Primitives (6)

| Primitive | Symbol | Source | Range | Aging Effect |
|-----------|--------|--------|-------|-------------|
| Edge Detection | edge | V1 orientation columns | [0,1] | Minimal |
| Motion Detection | motion | V5/MT | [0,1] | Decline >70 |
| Luminance Contrast | contrast | Retinal ganglion M/P | [0,1] | -0.3%/yr after 40 |
| Figure-Ground Segregation | figure_ground | V2 border ownership | [0,1] | Decline >60 |
| Temporal Coherence | temporal_coherence | STS, auditory cortex | [0,1] | -0.2%/yr after 40 |
| Symmetry Detection | symmetry | V4, LOC | [0,1] | Minimal |

### Measurement Protocol (Tier 1)
- **Edge**: Gabor filter bank energy at 4 orientations × 3 spatial frequencies
- **Motion**: Optical flow magnitude from video / temporal derivative
- **Contrast**: RMS contrast of luminance channel (Michelson or Weber)
- **Figure-Ground**: Saliency map entropy (Itti & Koch, 2001)
- **Temporal Coherence**: Autocorrelation of auditory/visual time series
- **Symmetry**: Fourier phase congruency at bilateral frequencies

### Implementation
File: `src/models/cva_constraint.py` → `Tier1ConstraintVector`
Engine: `src/services/cva_constraint_engine.py` → `_extract_tier1()`

---

## Tier 2: ψ-Calibrated Interpretive Constraints (8)

### C1: Processing Cost (ProcessingCost)
- **Definition**: Cognitive effort required to build a mental model of the environment
- **Computation**: `θ₁(edge, contrast, symmetry; mastery)` — higher edge/contrast complexity raises cost; expertise reduces it by up to 40%
- **Measurement**: Response time on scene categorization + pupil dilation
- **Neurotype modulation**: PTSD ×1.5, Alzheimer's ×2.0, Gifted ×0.6, ADHD ×0.7
- **Dalton caveat**: Processing cost depends on navigation familiarity, not just visual complexity — a repeated visitor to a complex hospital has lower processing cost than a first-timer to a simple one

### C2: Load Rate (LoadRate)
- **Definition**: Temporal density of information requiring active processing
- **Computation**: `θ₂(motion, temporal_coherence; age)`
- **Measurement**: RSME workload probe + blink rate
- **Neurotype modulation**: Older adult ×0.7, ADHD ×1.3, Bipolar manic ×1.5

### C3: Prediction Error (PredictionError)
- **Definition**: Mismatch between expected and observed environmental features
- **Computation**: `θ₃(all primitives; familiarity, expertise)` — larger discrepancy from internal model = higher prediction error
- **Measurement**: Surprise rating (1-7) + skin conductance response + N400 ERP
- **Neurotype modulation**: PTSD ×2.0, Anxiety ×1.8, Alzheimer's ×1.8
- **Friston note**: This IS the core active inference quantity — prediction error drives precision-weighted updating in both constraint and valuation layers

### C4: Control Efficacy (ControlEfficacy)
- **Definition**: Perceived ability to navigate and act within the environment
- **Computation**: `θ₄(figure_ground, edge; spatial_ability)` — clear paths and legible layouts increase efficacy
- **Measurement**: Wayfinding confidence + observed navigation success rate
- **Neurotype modulation**: PTSD ×0.6, Older adult ×0.7, Alzheimer's ×0.3, Anxiety ×0.6

### C5: Affordance Density (AffordanceDensity)
- **Definition**: Richness of action possibilities in the environment (Gibsonian)
- **Computation**: `θ₅(edge, figure_ground; motor_ability)` — more distinct objects/surfaces = more affordances
- **Measurement**: Action enumeration task + behavioral clipping (observer codes available actions)
- **Neurotype modulation**: ADHD ×1.3, Bipolar manic ×1.5, Gifted ×1.3

### C6: Social Cue Density (SocialCueDensity)
- **Definition**: Density of signals about other people's presence, intentions, and activities
- **Computation**: `θ₆(motion, temporal_coherence; social_sensitivity)`
- **Measurement**: Social scene count + perceived crowding scale
- **Neurotype modulation**: ASD ×0.7, Anxiety ×1.5

### C7: Multisensory Coherence (MultisensoryCoherence)
- **Definition**: Degree to which visual, auditory, olfactory, and haptic signals form a unified percept
- **Computation**: `θ₇(temporal_coherence, symmetry; sensory_sensitivity)` — coherent multisensory environments have lower conflict
- **Measurement**: Gestalt completion task + cross-modal matching accuracy
- **Neurotype modulation**: ASD ×0.5, Older adult ×0.7

### C8: Narrative Coherence (NarrativeCoherence)
- **Definition**: Degree to which the environment tells a legible story or fits a cultural meaning script
- **Computation**: `θ₈(figure_ground, symmetry; cultural_knowledge)`
- **Measurement**: Narrative completion task + meaning rating (1-7) + place identity scale
- **Neurotype modulation**: Alzheimer's ×0.3, Gifted ×1.3

---

## Constraint Distributions (Probabilistic Extension)

Per R2.1 (Three Hard Problems), constraints are not point values but distributions:

```
p(c|x,A,ψ) ~ N(μ, Σ)
  μ = f(x; θ(ψ))                   [deterministic engine output]
  Σ = diag(π(A)⁻¹)                 [frame-dependent covariance]
  π(A) ∈ ℝ⁸                        [precision vector from ActivityFrame]
```

Implementation: `ConstraintDistribution` class in `cva_constraint_engine.py`

---

## Activity Frame Modulation

Frame precision vectors (10 frames × 8 constraints) in `FRAME_PRECISIONS`.
Canonical frame registry in `src/services/cva/activity_frame_registry.py`.

---

## Files

| File | Purpose |
|------|---------|
| `src/models/cva_constraint.py` | Data structures (286 LOC) |
| `src/services/cva_constraint_engine.py` | Computation engine (343 LOC) |
| `src/services/cva/activity_frame_registry.py` | Frame registry (400+ LOC) |
| `tests/test_cva_engines.py` | Engine tests |
| `tests/test_cva_models.py` | Model tests |
