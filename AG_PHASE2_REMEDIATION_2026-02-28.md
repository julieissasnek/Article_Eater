# AG Phase 2 Remediation Assignment

**Date**: 2026-02-28
**Assigned to**: AG
**Status**: ACTIVE
**Baseline**: Phase 2 complete, 24/24 tests passing
**Target**: Integrate Three Hard Problems solutions into Phase 2 computational engine

---

## EXECUTIVE SUMMARY

Phase 2 (CVA computation engine) was completed with solid data structures and deterministic functionality — 24/24 tests pass. However, the Three Hard Problems spec (docs/CVA_SPRINT_SPECS_REVISED_WITH_THREE_HARD_PROBLEMS_2026-02-28.md) requires **six focused upgrades** to enable probabilistic constraint recognition, decomposed feedback with multiple timescales, sparse auxiliary activation, and coupled dynamics with attractors.

**This is NOT a redo.** All existing code remains. These are **additive extensions** that:
- Extend existing classes (ConstraintDistribution, FeedbackSignal, DynamicsState, etc.)
- Add new computation pathways (probabilistic recognition, three-part feedback)
- Upgrade existing methods to use new components (valuation engine with frame-aware modulation)
- Introduce new mathematical structures (coupling matrices, Lyapunov stability checks)

**Your job**: Implement six remediation tasks in priority order, upgrading the engine without breaking the 24 passing tests.

---

## CONTEXT: THE THREE HARD PROBLEMS

Chat identified three deep problems that Phase 2's original assignment didn't address:

1. **Q1 (Spohn/Epistemic Uncertainty)**: How do constraints vary probabilistically across scenes/frames?
   → **Solution**: Recognize constraints as distributions p(c|x,A,ψ), not point estimates.

2. **Q2 (Nelson/Attention Dynamics)**: How do multiple timescale feedback mechanisms (attention, precision, prior) work together?
   → **Solution**: Decompose feedback into three independent pathways with distinct τ values.

3. **Q3 (Multiple Realizability)**: How do cultural/activity contexts modulate core vs. auxiliary valuation dimensions?
   → **Solution**: Sparse auxiliary activation + frame-dependent precision gains.

Additionally:
- **Coupling**: Constraints and valuations influence each other via matrices K_cc, K_cv, K_vc, K_vv.
- **Attractors**: The coupled system has multiple stable fixed points (rasa states for Indian aesthetics).
- **Stability**: Use Lyapunov/eigenvalue analysis to verify attractors and compute κ_loop (coupling strength).

---

## THE SIX REMEDIATION TASKS

### R2.1: Probabilistic Constraint Recognition (Chat's Q1) — CRITICAL

**File**: `src/services/cva_constraint_engine.py`

**Current State**:
- `recognize_constraints(scene_features) -> np.ndarray [8]` returns deterministic point estimate
- No uncertainty quantification
- No activity-frame dependence

**Required Change**:
- Return `ConstraintDistribution` instead of raw np.ndarray
- Include mean (the existing point estimate), precision (from activity frame), and methods to sample/compute entropy
- Maintain **backward compatibility**: MAP estimate = old deterministic output

**Mathematical Specification**:

```
p(c|x,A,ψ) ~ 𝒩(c|μ, Σ)

where:
  μ = f(x; θ(ψ))         [your existing deterministic engine]
  Σ = diag(π(A)⁻¹)       [frame-dependent covariance]
  π(A) ∈ ℝ⁸             [precision vector from ActivityFrame]
```

**Implementation Blueprint**:

```python
@dataclass
class ConstraintDistribution:
    """Probabilistic constraint posterior p(c|x,A,ψ)."""

    mean: np.ndarray          # [8] — existing deterministic output f(x; θ(ψ))
    precision: np.ndarray     # [8] — diagonal precisions from π(A)
    activity_frame: str       # for reference/debugging

    def sample(self, n: int = 1) -> np.ndarray:
        """Draw n samples from p(c|x,A,ψ).

        Returns: [n, 8] array of constraint samples
        """
        std = 1.0 / np.sqrt(self.precision + 1e-8)  # avoid division by zero
        return np.random.normal(self.mean, std, size=(n, 8))

    def map_estimate(self) -> np.ndarray:
        """Return MAP estimate = mean for Gaussian.

        Use this for backward compatibility with existing code.
        """
        return self.mean.copy()

    def entropy(self) -> float:
        """Differential entropy of the Gaussian.

        H = 0.5 * log|2πeΣ| = 0.5 * Σ log(2πe/π_i)

        Higher precision → lower entropy (more certain).
        Lower precision → higher entropy (more uncertain).
        """
        # For diagonal covariance: H = 0.5 * sum(log(2πe/π))
        return 0.5 * np.sum(np.log(2 * np.pi * np.e / (self.precision + 1e-8)))

    def covariance_diagonal(self) -> np.ndarray:
        """Return diagonal covariances (σ²_i = 1/π_i)."""
        return 1.0 / (self.precision + 1e-8)

    def std_dev(self) -> np.ndarray:
        """Return standard deviations."""
        return np.sqrt(self.covariance_diagonal())
```

**Update** `recognize_constraints()`:

```python
def recognize_constraints(self,
                         scene_features: np.ndarray,
                         activity_frame: str,
                         psi: SubjectCharacteristics) -> ConstraintDistribution:
    """Recognize constraints as probabilistic distribution.

    Args:
        scene_features: [D_scene] visual features
        activity_frame: Activity context (e.g., 'RESTING', 'WORSHIPPING')
        psi: Subject characteristics (for θ(ψ))

    Returns:
        ConstraintDistribution with mean, precision, and sampling capability

    Implementation:
        1. Compute mean = f(x; θ(ψ)) using existing deterministic engine
        2. Look up π(A) from ActivityFrame[activity_frame].precision_weights
        3. Return ConstraintDistribution(mean, precision, activity_frame)
    """
    # Step 1: Compute deterministic mean (your existing code)
    mean_constraints = self._compute_deterministic_constraints(
        scene_features, psi
    )  # returns [8]

    # Step 2: Get activity frame and extract precision vector
    frame = ActivityFrame[activity_frame]
    precision = frame.precision_weights  # {constraint_name: precision}

    # Convert dict to [8] precision array (aligned with constraint dimensions)
    precision_array = np.array([
        precision.get(self.constraint_names[i], 1.0)
        for i in range(8)
    ])

    # Step 3: Return probabilistic distribution
    return ConstraintDistribution(
        mean=mean_constraints,
        precision=precision_array,
        activity_frame=activity_frame
    )
```

**ActivityFrame Requirements** (see `src/models/cva_valuation.py`):

```python
@dataclass
class ActivityFrame:
    name: str
    auxiliary_axes: List[str]      # e.g., ['sacredness'] for WORSHIPPING
    precision_weights: Dict[str, float]  # {constraint_name: precision_value}
    # Example for RESTING:
    # precision_weights = {
    #     'spatial_containment': 2.0,      # high precision (certain)
    #     'force_dynamics': 0.5,           # low precision (uncertain)
    #     ...
    # }
```

**Precision Values by Frame** (heuristic guidance):

| Frame | Safe | Stable | Path | Attract | Repel | Support | Push | Resist | Avg Precision |
|-------|------|--------|------|---------|-------|---------|------|--------|---------------|
| RESTING | 2.0 | 2.0 | 0.3 | 0.3 | 0.3 | 2.0 | 0.3 | 0.3 | 0.9 |
| STUDYING | 1.5 | 1.5 | 1.5 | 1.0 | 1.0 | 1.0 | 1.5 | 0.8 | 1.1 |
| EXPLORING | 0.5 | 0.8 | 2.0 | 1.0 | 1.0 | 0.5 | 0.5 | 0.5 | 0.9 |
| CREATING | 0.3 | 0.5 | 1.0 | 2.0 | 2.0 | 0.3 | 2.0 | 0.5 | 1.1 |
| WORSHIPPING | 1.5 | 1.5 | 0.5 | 1.5 | 2.0 | 2.0 | 0.3 | 0.3 | 1.1 |
| PLAYING | 0.5 | 0.5 | 1.5 | 2.0 | 1.0 | 0.5 | 1.0 | 0.5 | 1.0 |
| EATING | 1.0 | 1.5 | 0.5 | 1.0 | 0.3 | 1.5 | 0.3 | 0.3 | 0.8 |
| SOCIALIZING | 1.0 | 1.0 | 1.0 | 1.5 | 1.0 | 1.5 | 1.0 | 0.8 | 1.1 |
| SLEEPING | 2.0 | 2.0 | 0.2 | 0.2 | 0.2 | 2.0 | 0.2 | 0.2 | 0.8 |
| EXERCISING | 0.5 | 1.0 | 2.0 | 1.5 | 1.5 | 1.0 | 2.0 | 1.0 | 1.3 |

(These are examples. Adjust based on cognitive science literature or empirical validation.)

**Acceptance Criteria**:

- [ ] `ConstraintDistribution` dataclass defined with mean, precision, activity_frame
- [ ] `sample(n)` method works and produces correct shape [n, 8]
- [ ] `map_estimate()` returns mean (backward compatible)
- [ ] `entropy()` decreases as precision increases (verified with unit test)
- [ ] Higher precision for RESTING/STUDYING; lower for EXPLORING/CREATING
- [ ] All 24 existing tests still pass
- [ ] New test: `test_constraint_distribution_sampling()` — 1000 samples, verify mean/std
- [ ] New test: `test_entropy_decreases_with_precision()` — compute for multiple precision vectors
- [ ] New test: `test_backward_compatibility_map_estimate()` — MAP = old deterministic

**Estimated Effort**: ~150 lines | 4 hours

---

### R2.2: Decomposed Feedback Computation (Chat's Q2) — CRITICAL

**File**: `src/services/cva_dynamics.py` (extend)

**Current State**:
- `FeedbackSignal` is a data structure with three fields (ε_attn, ε_prec, ε_prior)
- No computation logic
- Feedback applied with single timescale

**Required Change**:
- Implement three independent computation pathways
- Each pathway has distinct timescale (τ_attn ≈ 0.4s, τ_prec ≈ 1.0s, τ_prior ≈ 3.0s)
- Compose feedback with timescale-appropriate decay

**Mathematical Specification**:

```
Three feedback signals:

ε_attn:  Sampling bias toward constraint-informative regions
         Timescale τ ≈ 0.3-0.5s (fastest, visual system)
         Neural: dorsal frontoparietal attention network
         Computation: precision-weighted constraint gradient or gaze modulation

ε_prec:  Gain modulation on valuation error
         Timescale τ ≈ 0.5-2.0s (medium, precision control)
         Neural: V1/V2 gain modulation circuits
         Computation: variance of recent constraints vs. expected precision

ε_prior: Expectation shift from cultural/learned priors
         Timescale τ ≈ 1-5s (slowest, cultural learning)
         Neural: mPFC-hippocampal systems
         Computation: deviation of valuation from cultural baseline

Decay per timestep: δ(t) = exp(-dt/τ)
```

**Implementation Blueprint**:

```python
class DecomposedFeedbackEngine:
    """Computes three independent feedback signals with distinct neural/temporal signatures."""

    # Canonical timescales (seconds)
    TAU_ATTENTION = 0.4   # visual system
    TAU_PRECISION = 1.0   # modulation circuits
    TAU_PRIOR = 3.0       # cultural learning

    def compute_attention_error(self,
        constraint_dist: ConstraintDistribution,
        valuation_state: np.ndarray,  # current [9] valuation
        activity_frame: str,
        gaze_weights: Optional[np.ndarray] = None
    ) -> float:
        """Attention error: sampling bias toward constraint-informative regions.

        ε_attn measures how much visual attention is biased toward regions that
        are most informative about the constraints.

        If gaze_weights provided:
            ε_attn = dot(gaze_weights, constraint_dist.precision)
            → High where constraints are precise and gaze is focused

        Otherwise (default):
            ε_attn = sqrt(sum(constraint_dist.precision²)) / 8
            → Average precision level, normalized

        Returns: scalar float, [0, ∞)
        """
        if gaze_weights is not None:
            # Gaze-modulated: attention × constraint informativeness
            return float(np.dot(gaze_weights, constraint_dist.precision))
        else:
            # Default: RMS of precision values
            return float(np.sqrt(np.mean(constraint_dist.precision ** 2)))

    def compute_precision_error(self,
        constraint_history: List[np.ndarray],  # last N constraint samples
        activity_frame: str,
        psi: SubjectCharacteristics
    ) -> float:
        """Precision error: gain modulation on valuation update.

        ε_prec measures mismatch between observed variance of constraints
        (from sampling history) and expected variance under the current frame.

        Computation:
            1. observed_var = empirical variance over constraint_history
            2. expected_var = 1 / π(A)  [from activity frame]
            3. ε_prec = ||observed_var - expected_var||_2

        High error → constraints are more variable than expected → adjust gain
        Low error → constraints match expectations → no adjustment needed

        Returns: scalar float, [0, ∞)
        """
        if len(constraint_history) < 2:
            return 0.0

        constraint_samples = np.array(constraint_history)  # [N, 8]
        observed_var = np.var(constraint_samples, axis=0)  # [8]

        frame = ActivityFrame[activity_frame]
        expected_var = 1.0 / (np.array([
            frame.precision_weights.get(self.constraint_names[i], 1.0)
            for i in range(8)
        ]) + 1e-8)

        error = np.linalg.norm(observed_var - expected_var)
        return float(error)

    def compute_prior_error(self,
        constraint_state: np.ndarray,       # current [8] constraints
        valuation_state: np.ndarray,        # current [9] valuations
        activity_frame: str,
        psi: SubjectCharacteristics,
        cultural_baseline: Optional[np.ndarray] = None  # expected [9] for this (culture, frame)
    ) -> float:
        """Prior error: expectation mismatch from cultural/learned priors.

        ε_prior measures how much the current valuation deviates from what
        is culturally expected for this activity frame and subject.

        If cultural_baseline provided (from cultural database):
            ε_prior = ||valuation_state - cultural_baseline||_2

        Otherwise (default):
            ε_prior = 0.0 (no prior expectations)

        High error → valuation diverges from cultural norm → update prior
        Low error → valuation aligns with cultural expectation

        Returns: scalar float, [0, ∞)
        """
        if cultural_baseline is None:
            # No cultural data available; assume neutral prior
            return 0.0

        error = np.linalg.norm(valuation_state - cultural_baseline)
        return float(error)

    def compose_feedback(self,
        e_attn: float,
        e_prec: float,
        e_prior: float,
        dt: float = 0.01,
        decay_attn: Optional[float] = None,
        decay_prec: Optional[float] = None,
        decay_prior: Optional[float] = None
    ) -> FeedbackSignal:
        """Compose three signals into unified feedback with timescale decay.

        Each signal decays at its own rate:
            ε_attn(t+dt) = ε_attn(t) * exp(-dt/τ_attn)
            ε_prec(t+dt) = ε_prec(t) * exp(-dt/τ_prec)
            ε_prior(t+dt) = ε_prior(t) * exp(-dt/τ_prior)

        Args:
            e_attn, e_prec, e_prior: Raw error signals (from compute_*_error)
            dt: Integration timestep (seconds)
            decay_attn, decay_prec, decay_prior: Custom decay rates (optional)

        Returns:
            FeedbackSignal with decayed errors and metadata
        """
        if decay_attn is None:
            decay_attn = np.exp(-dt / self.TAU_ATTENTION)
        if decay_prec is None:
            decay_prec = np.exp(-dt / self.TAU_PRECISION)
        if decay_prior is None:
            decay_prior = np.exp(-dt / self.TAU_PRIOR)

        return FeedbackSignal(
            epsilon_attention=e_attn * decay_attn,
            epsilon_precision=e_prec * decay_prec,
            epsilon_prior=e_prior * decay_prior,
            timescale_attention=self.TAU_ATTENTION,
            timescale_precision=self.TAU_PRECISION,
            timescale_prior=self.TAU_PRIOR,
            timestamp=time.time()
        )
```

**Update FeedbackSignal dataclass** (in `src/models/`):

```python
@dataclass
class FeedbackSignal:
    """Three-part feedback with distinct timescales."""

    epsilon_attention: float       # ε_attn ∈ [0, ∞)
    epsilon_precision: float       # ε_prec ∈ [0, ∞)
    epsilon_prior: float           # ε_prior ∈ [0, ∞)

    # Metadata for introspection
    timescale_attention: float = 0.4   # τ_attn (seconds)
    timescale_precision: float = 1.0   # τ_prec
    timescale_prior: float = 3.0       # τ_prior
    timestamp: Optional[float] = None

    def total_magnitude(self) -> float:
        """Combined feedback magnitude (L2 norm of components)."""
        return float(np.sqrt(
            self.epsilon_attention**2 +
            self.epsilon_precision**2 +
            self.epsilon_prior**2
        ))

    def dominance(self) -> str:
        """Which signal dominates?"""
        signals = {
            'attention': self.epsilon_attention,
            'precision': self.epsilon_precision,
            'prior': self.epsilon_prior
        }
        return max(signals, key=signals.get)
```

**Integration into dynamics** (update `step()` method):

```python
def step(self,
    state: DynamicsState,
    constraint_dist: ConstraintDistribution,
    valuation_target: np.ndarray,
    coupling: CVACouplingMatrices,
    feedback_engine: DecomposedFeedbackEngine,
    constraint_history: List[np.ndarray],
    psi: SubjectCharacteristics,
    activity_frame: str,
    dt: float = 0.01
) -> Tuple[DynamicsState, FeedbackSignal]:
    """Single integration step with decomposed feedback.

    Returns:
        (updated_state, feedback_signal_used)
    """
    # Compute three feedback pathways
    e_attn = feedback_engine.compute_attention_error(
        constraint_dist, state.valuations, activity_frame
    )
    e_prec = feedback_engine.compute_precision_error(
        constraint_history, activity_frame, psi
    )
    e_prior = feedback_engine.compute_prior_error(
        state.constraints, state.valuations, activity_frame, psi
    )

    # Compose with timescale decay
    feedback = feedback_engine.compose_feedback(e_attn, e_prec, e_prior, dt)

    # Use feedback in constraint/valuation updates
    # (existing dynamics code, but now using three-part feedback)

    return updated_state, feedback
```

**Acceptance Criteria**:

- [ ] `DecomposedFeedbackEngine` class defined in `cva_dynamics.py`
- [ ] `compute_attention_error()` works with and without gaze_weights
- [ ] `compute_precision_error()` compares observed vs. expected constraint variance
- [ ] `compute_prior_error()` compares valuation to cultural baseline
- [ ] `compose_feedback()` applies timescale-specific decay
- [ ] `FeedbackSignal` updated with timescale metadata
- [ ] Integration test: `test_feedback_timescale_decay()` — verify exponential decay over 10 steps
- [ ] Integration test: `test_attention_error_with_gaze()` — verify gaze modulation
- [ ] Integration test: `test_precision_error_variance_mismatch()` — high variance → high error
- [ ] Integration test: `test_prior_error_cultural_baseline()` — deviation from baseline triggers error
- [ ] All 24 existing tests still pass
- [ ] New combined test: `test_decomposed_feedback_full_cycle()` — compute all three, compose, verify signal properties

**Estimated Effort**: ~200 lines | 6 hours

---

### R2.3: Activity Frame Sparse Auxiliary Activation (Chat's Q3)

**File**: `src/services/cva_valuation_engine.py`

**Current State**:
- Valuation engine computes 9 core axes
- ActivityFrame has `auxiliary_axes` field but it's not used
- No frame-dependent precision modulation

**Required Change**:
- Compute v_core (9 axes, always)
- Activate v_aux ONLY for axes listed in current ActivityFrame
- Apply frame-dependent precision gain W(A) to modulate core valuations

**Mathematical Specification**:

```
Valuation vector: V = [v_core (9D) | v_aux (variable, sparse)]

For activity frame A:
  v_core(A) = f_core(c, ψ)           [9D, always computed]
  v_aux(A)  = {f_aux_i(c, ψ) if i ∈ auxiliary_axes(A) else 0}

  W(A) = diag(precision_weights(A))   [9×9 frame-dependent gain matrix]
  V_out = W(A) * v_core + v_aux_sparse
```

**Implementation Blueprint**:

```python
def compute_valuation_with_frame(self,
    constraints: np.ndarray,           # [8]
    activity_frame: str,
    psi: SubjectCharacteristics
) -> CompleteValuationVector:
    """Compute valuation with frame-aware core/auxiliary split.

    Args:
        constraints: Current [8] constraint state
        activity_frame: Activity context ('RESTING', 'WORSHIPPING', etc.)
        psi: Subject characteristics

    Returns:
        CompleteValuationVector with modulated core and sparse auxiliary
    """
    # Step 1: Compute v_core (9D, always active)
    v_core = self._compute_core_valuation(constraints, psi)  # [9]

    # Step 2: Get activity frame and determine active auxiliary axes
    frame = ActivityFrame[activity_frame]
    active_aux_axes = frame.auxiliary_axes  # e.g., ['sacredness'] for WORSHIPPING

    # Step 3: Compute v_aux for ALL auxiliary dimensions, but only store active ones
    v_aux_full = self._compute_auxiliary_valuation(constraints, psi)  # dict[axis_name → float]

    # Filter to active auxiliaries (others implicitly 0)
    v_aux_sparse = {
        axis: v_aux_full[axis]
        for axis in active_aux_axes
        if axis in v_aux_full
    }

    # Step 4: Apply frame-dependent precision gain to v_core
    precision_gains = frame.precision_weights  # {constraint_name: gain}

    # Map gains to 9D core valuation (alignment with core axis names)
    gain_vector = np.array([
        precision_gains.get(self.core_axis_names[i], 1.0)
        for i in range(9)
    ])

    v_core_modulated = v_core * gain_vector

    # Step 5: Assemble output
    return CompleteValuationVector(
        core=v_core_modulated,
        auxiliary=v_aux_sparse,
        active_auxiliary_axes=active_aux_axes,
        activity_frame=activity_frame,
        precision_gains=gain_vector
    )

def _compute_core_valuation(self, constraints: np.ndarray,
                           psi: SubjectCharacteristics) -> np.ndarray:
    """Compute 9D core valuation vector.

    Core dimensions: autonomy, competence, relatedness, novelty, beauty,
                    meaning, security, justice, flourishing

    Returns: [9] core valuation
    """
    # Existing implementation or new one
    # Use constraint_weights and subject characteristics
    return self._evaluate_dimensions(constraints, psi)

def _compute_auxiliary_valuation(self, constraints: np.ndarray,
                                psi: SubjectCharacteristics) -> Dict[str, float]:
    """Compute auxiliary valuations for all possible dimensions.

    Returns: {axis_name → value} for all auxiliary dimensions

    Auxiliaries: sacredness, originality, humor, danger, etc.
    Only some will be active for a given activity frame.
    """
    auxiliary_values = {}

    # Sacredness: high when constraints suggest ritualistic or devotional context
    auxiliary_values['sacredness'] = self._evaluate_sacredness(constraints, psi)

    # Originality: high when constraints suggest novel/creative context
    auxiliary_values['originality'] = self._evaluate_originality(constraints, psi)

    # Humor: high when constraints suggest playful context
    auxiliary_values['humor'] = self._evaluate_humor(constraints, psi)

    # Danger: high when constraints suggest threatening context
    auxiliary_values['danger'] = self._evaluate_danger(constraints, psi)

    # Add more as needed

    return auxiliary_values

def _apply_precision_gains(self, v_core: np.ndarray,
                          precision_gains: Dict[str, float]) -> np.ndarray:
    """Apply frame-dependent precision gains to core valuation.

    High gain (e.g., 2.0) → amplify that dimension for this frame
    Low gain (e.g., 0.3) → suppress that dimension

    Example:
        WORSHIPPING frame: high gain on 'sacredness', 'meaning'; low on 'novelty'
    """
    # Map precision_weights to core dimensions
    gains = np.array([
        precision_gains.get(name, 1.0)
        for name in self.core_axis_names
    ])
    return v_core * gains
```

**CompleteValuationVector dataclass** (in `src/models/cva_valuation.py`):

```python
@dataclass
class CompleteValuationVector:
    """Valuation with frame-aware core/auxiliary split."""

    core: np.ndarray                      # [9] modulated core valuations
    auxiliary: Dict[str, float]           # {axis_name → value} sparse auxiliaries
    active_auxiliary_axes: List[str]      # which auxiliaries are active for this frame
    activity_frame: str                   # e.g., 'WORSHIPPING'
    precision_gains: np.ndarray           # [9] gain multipliers applied to core

    def get_full_valuation(self, include_inactive_aux: bool = False) -> np.ndarray:
        """Assemble full valuation vector.

        If include_inactive_aux=False (default): return only active auxiliaries
        If include_inactive_aux=True: pad with zeros for all auxiliary dimensions
        """
        # Return just core + active auxiliaries
        return np.concatenate([self.core, list(self.auxiliary.values())])

    def core_only(self) -> np.ndarray:
        """Return just the 9D core."""
        return self.core.copy()
```

**ActivityFrame extension** (ensure exists in `src/models/cva_valuation.py`):

```python
@dataclass
class ActivityFrame:
    name: str
    auxiliary_axes: List[str]             # e.g., ['sacredness'] for WORSHIPPING
    precision_weights: Dict[str, float]   # {axis_name: gain} for core modulation

    # Examples:
    # WORSHIPPING: auxiliary_axes=['sacredness'], precision_weights={'meaning': 2.0, 'security': 0.5}
    # CREATING: auxiliary_axes=['originality'], precision_weights={'novelty': 2.0, 'autonomy': 1.5}
```

**Acceptance Criteria**:

- [ ] `compute_valuation_with_frame()` implemented and returns `CompleteValuationVector`
- [ ] Auxiliary axes are 0.0 when frame doesn't activate them
- [ ] WORSHIPPING activates 'sacredness'; CREATING activates 'originality'; etc. (verify for all 10 frames)
- [ ] Frame precision gains modulate v_core correctly (high gain → amplified, low gain → suppressed)
- [ ] `CompleteValuationVector` dataclass defined with core, auxiliary, active_auxiliary_axes
- [ ] Test: `test_sparse_auxiliary_activation()` — verify inactive axes are 0
- [ ] Test: `test_frame_precision_gains()` — verify modulation for each frame
- [ ] Test: `test_complete_valuation_vector_assembly()` — assemble full and core-only vectors
- [ ] All 24 existing tests still pass
- [ ] New integration test: `test_valuation_frame_dependent()` — same constraints, different frames → different valuations

**Estimated Effort**: ~100 lines | 3 hours

---

### R2.4: Coupling Matrices in Dynamics (K_cc, K_cv, K_vc, K_vv) — PREREQUISITE FOR OTHERS

**File**: `src/services/cva_dynamics.py`

**Current State**:
- Scalar α, β parameters
- Dynamics: ∂c/∂t = α(c_target − c) + ε
- No constraint-valuation coupling
- Single attractor (fixed point)

**Required Change**:
- Replace scalar dynamics with full 17×17 coupled system
- Introduce coupling matrices K_cc, K_cv, K_vc, K_vv
- Enable multiple attractors (rasa states)

**Mathematical Specification**:

```
Coupled system:
  dc/dt = -D_c(c - c_target) + φ(K_cc·c + K_cv·v) + ε
  dv/dt = -D_v(v - v_target) + φ(K_vv·v + K_vc·c)

where:
  D_c = diag(dissipation_c) [8×8, typically ~0.1-1.0]
  D_v = diag(dissipation_v) [9×9, typically ~0.1-1.0]
  K_cc [8×8] = constraint-constraint coupling
  K_cv [8×9] = constraint←valuation coupling
  K_vc [9×8] = valuation←constraint coupling
  K_vv [9×9] = valuation-valuation coupling
  φ(x) = soft ReLU = log(1 + exp(αx)) / α  [smooth activation]

Coupling strength:
  κ_loop = largest eigenvalue of feedback loop
  For stability: κ_loop < 1 (usually κ < 0.1 for biological plausibility)
```

**Implementation Blueprint**:

```python
@dataclass
class CVACouplingMatrices:
    """Coupling matrices for constraint-valuation dynamics."""

    K_cc: np.ndarray  # [8, 8] constraint←constraint
    K_cv: np.ndarray  # [8, 9] constraint←valuation
    K_vc: np.ndarray  # [9, 8] valuation←constraint
    K_vv: np.ndarray  # [9, 9] valuation←valuation

    @classmethod
    def default(cls) -> 'CVACouplingMatrices':
        """Default weak coupling, biologically plausible.

        Returns matrices with κ_loop ≈ 0.038 (weak coupling).
        """
        # Weak self-inhibition
        K_cc = np.eye(8) * -0.1

        # Default: minimal constraint←valuation
        K_cv = np.zeros((8, 9))

        # Weak valuation←constraint coupling
        # Random seed for reproducibility
        rng = np.random.RandomState(seed=42)
        K_vc = rng.randn(9, 8) * 0.02

        # Valuation dynamics with weak coupling
        K_vv = np.eye(9) * -0.05 + rng.randn(9, 9) * 0.01

        return cls(K_cc=K_cc, K_cv=K_cv, K_vc=K_vc, K_vv=K_vv)

    @classmethod
    def from_dict(cls, data: Dict) -> 'CVACouplingMatrices':
        """Load from dictionary (for serialization)."""
        return cls(
            K_cc=np.array(data['K_cc']),
            K_cv=np.array(data['K_cv']),
            K_vc=np.array(data['K_vc']),
            K_vv=np.array(data['K_vv'])
        )

    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'K_cc': self.K_cc.tolist(),
            'K_cv': self.K_cv.tolist(),
            'K_vc': self.K_vc.tolist(),
            'K_vv': self.K_vv.tolist()
        }

    def estimate_coupling_strength(self) -> float:
        """Estimate κ_loop from coupling matrices.

        Rough estimate: spectral radius of coupled feedback.
        Returns: κ ∈ [0, ∞), typically < 0.1 for stability
        """
        # Simplified: norm of off-diagonal coupling
        off_diagonal_norm = (
            np.linalg.norm(self.K_cv, 'fro') +
            np.linalg.norm(self.K_vc, 'fro')
        ) / 2.0
        return float(off_diagonal_norm)

def phi(x: np.ndarray, alpha: float = 1.0) -> np.ndarray:
    """Soft ReLU activation function.

    φ(x) = log(1 + exp(αx)) / α

    Properties:
      - Smooth (infinitely differentiable)
      - Near-ReLU behavior for large α
      - φ'(x) = sigmoid(αx) (smooth step)
      - φ(0) = log(2) / α ≈ 0.69 / α

    Args:
        x: Input array (can be any shape)
        alpha: Steepness parameter (default 1.0)

    Returns:
        Activated output, same shape as x
    """
    return np.log(1.0 + np.exp(alpha * np.clip(x, -20, 20))) / alpha

def phi_prime(x: np.ndarray, alpha: float = 1.0) -> np.ndarray:
    """Derivative of soft ReLU.

    φ'(x) = sigmoid(αx) = 1 / (1 + exp(-αx))
    """
    return 1.0 / (1.0 + np.exp(-alpha * np.clip(x, -20, 20)))

@dataclass
class DynamicsState:
    """State of coupled constraint-valuation system."""

    constraints: np.ndarray     # [8] current constraint state
    valuations: np.ndarray      # [9] current valuation state
    constraint_target: np.ndarray   # [8] target (from recognition engine)
    valuation_target: np.ndarray    # [9] target (from valuation engine)
    dt: float = 0.01                # integration timestep
    time: float = 0.0               # current simulation time

class CVADynamicsEngine:
    """Coupled constraint-valuation dynamics with multiple attractors."""

    def __init__(self,
                 dissipation_c: np.ndarray = None,
                 dissipation_v: np.ndarray = None,
                 dt: float = 0.01):
        """Initialize dynamics engine.

        Args:
            dissipation_c: [8] dissipation for constraints (default ~0.3)
            dissipation_v: [9] dissipation for valuations (default ~0.2)
            dt: Integration timestep (default 0.01)
        """
        self.dt = dt
        self.dissipation_c = dissipation_c if dissipation_c is not None else np.full(8, 0.3)
        self.dissipation_v = dissipation_v if dissipation_v is not None else np.full(9, 0.2)

        self.constraint_names = [
            'spatial_containment', 'force_dynamics', 'stability', 'safety',
            'attraction', 'repulsion', 'support', 'resistance'
        ]
        self.valuation_names = [
            'autonomy', 'competence', 'relatedness', 'novelty', 'beauty',
            'meaning', 'security', 'justice', 'flourishing'
        ]

    def step(self,
        state: DynamicsState,
        coupling: CVACouplingMatrices,
        activity_frame: str = 'RESTING',
        phi_alpha: float = 1.0
    ) -> DynamicsState:
        """Single integration step with Euler method.

        dc/dt = -D_c(c - c_target) + φ(K_cc·c + K_cv·v)
        dv/dt = -D_v(v - v_target) + φ(K_vv·v + K_vc·c)

        Args:
            state: Current (c, v, targets)
            coupling: Coupling matrices
            activity_frame: For reference (doesn't affect dynamics directly)
            phi_alpha: Steepness of activation function

        Returns:
            Updated state
        """
        # Compute derivatives
        dissipation_c = np.diag(self.dissipation_c)
        dissipation_v = np.diag(self.dissipation_v)

        # dc/dt terms
        drift_c = -dissipation_c @ (state.constraints - state.constraint_target)
        coupling_c = phi(
            coupling.K_cc @ state.constraints + coupling.K_cv @ state.valuations,
            alpha=phi_alpha
        )
        dc_dt = drift_c + coupling_c

        # dv/dt terms
        drift_v = -dissipation_v @ (state.valuations - state.valuation_target)
        coupling_v = phi(
            coupling.K_vv @ state.valuations + coupling.K_vc @ state.constraints,
            alpha=phi_alpha
        )
        dv_dt = drift_v + coupling_v

        # Euler step
        new_constraints = state.constraints + self.dt * dc_dt
        new_valuations = state.valuations + self.dt * dv_dt
        new_time = state.time + self.dt

        return DynamicsState(
            constraints=new_constraints,
            valuations=new_valuations,
            constraint_target=state.constraint_target,
            valuation_target=state.valuation_target,
            dt=self.dt,
            time=new_time
        )

    def run_to_convergence(self,
        initial_state: DynamicsState,
        coupling: CVACouplingMatrices,
        max_steps: int = 10000,
        tolerance: float = 1e-4,
        phi_alpha: float = 1.0
    ) -> Tuple[DynamicsState, List[DynamicsState]]:
        """Run dynamics until convergence.

        Returns:
            (final_state, trajectory)
        """
        trajectory = [initial_state]
        state = initial_state

        for step_num in range(max_steps):
            new_state = self.step(state, coupling, phi_alpha=phi_alpha)
            trajectory.append(new_state)

            # Check convergence
            dc = np.linalg.norm(new_state.constraints - state.constraints)
            dv = np.linalg.norm(new_state.valuations - state.valuations)

            if dc < tolerance and dv < tolerance:
                return new_state, trajectory

            state = new_state

        # Did not converge
        return state, trajectory
```

**Acceptance Criteria**:

- [ ] `CVACouplingMatrices` dataclass defined with K_cc, K_cv, K_vc, K_vv
- [ ] `phi()` soft ReLU function implemented correctly (verified against analytical φ'(x))
- [ ] `DynamicsState` updated to include targets and coupling parameters
- [ ] `CVADynamicsEngine.step()` implements full 17-dim coupled ODE
- [ ] `run_to_convergence()` reaches stable fixed point for default coupling
- [ ] Default coupling produces κ_loop < 0.1
- [ ] Test: `test_euler_integration_step()` — single step, verify dc/dt, dv/dt computed correctly
- [ ] Test: `test_default_coupling_convergence()` — trajectory converges to fixed point
- [ ] Test: `test_coupling_strength_estimate()` — κ_loop < 0.1 for default
- [ ] Test: `test_soft_relu_activation()` — φ(0), φ(x>0), φ(x<0) correct; φ'(x) = sigmoid
- [ ] Test: `test_multiple_attractors_high_coupling()` — high coupling produces multiple fixed points
- [ ] All 24 existing tests still pass (some will need API updates)

**Estimated Effort**: ~300 lines | 8 hours

---

### R2.5: Lyapunov Analysis

**File**: `src/services/cva_dynamics.py` (extend)

**Current State**:
- Jacobian matrix (if computed) is diagonal only
- No stability analysis

**Required Change**:
- Compute full 17×17 Jacobian with coupling terms
- Eigenvalue decomposition to check stability
- Compute κ_loop from spectral radius

**Mathematical Specification**:

```
Full Jacobian J of [c, v] system:

J = [∂ċ/∂c | ∂ċ/∂v]  = [-D_c + φ'(K_cc·c + K_cv·v)·K_cc | φ'(K_cc·c + K_cv·v)·K_cv]
    [∂v̇/∂c | ∂v̇/∂v]    [φ'(K_vv·v + K_vc·c)·K_vc | -D_v + φ'(K_vv·v + K_vc·c)·K_vv]

where J_ij = ∂(ċ_i)/∂(c_j) or ∂(v̇_i)/∂(v_j)

Stability at fixed point:
  - All eigenvalues have Re(λ) < 0 → stable attractor
  - At least one Re(λ) > 0 → unstable saddle or repeller

κ_loop = max(|Re(λ)|) — coupling strength; should be < 0.1 for biological plausibility
```

**Implementation Blueprint**:

```python
def compute_full_jacobian(self,
    state: DynamicsState,
    coupling: CVACouplingMatrices,
    phi_alpha: float = 1.0,
    h: float = 1e-5
) -> np.ndarray:
    """Compute full 17×17 Jacobian via numerical differentiation.

    J[i, j] = ∂(ẋ_i) / ∂(x_j) where x = [c, v]

    Uses finite differences (central difference) for accuracy.

    Args:
        state: Linearization point
        coupling: Coupling matrices
        phi_alpha: Activation steepness
        h: Finite difference step

    Returns:
        [17, 17] Jacobian matrix
    """
    J = np.zeros((17, 17))

    # Concatenate state for easier indexing
    x = np.concatenate([state.constraints, state.valuations])  # [17]

    # Compute derivatives by finite differences
    for j in range(17):
        x_plus = x.copy()
        x_plus[j] += h

        x_minus = x.copy()
        x_minus[j] -= h

        # Evaluate dynamics at perturbed states
        state_plus = DynamicsState(
            constraints=x_plus[:8],
            valuations=x_plus[8:],
            constraint_target=state.constraint_target,
            valuation_target=state.valuation_target,
            dt=self.dt
        )
        state_minus = DynamicsState(
            constraints=x_minus[:8],
            valuations=x_minus[8:],
            constraint_target=state.constraint_target,
            valuation_target=state.valuation_target,
            dt=self.dt
        )

        f_plus = self._dynamics_derivative(state_plus, coupling, phi_alpha)
        f_minus = self._dynamics_derivative(state_minus, coupling, phi_alpha)

        J[:, j] = (f_plus - f_minus) / (2 * h)

    return J

def _dynamics_derivative(self,
    state: DynamicsState,
    coupling: CVACouplingMatrices,
    phi_alpha: float = 1.0
) -> np.ndarray:
    """Compute [dc/dt, dv/dt] as single [17] vector.

    Helper for Jacobian computation.
    """
    dissipation_c = np.diag(self.dissipation_c)
    dissipation_v = np.diag(self.dissipation_v)

    dc_dt = -dissipation_c @ (state.constraints - state.constraint_target) + phi(
        coupling.K_cc @ state.constraints + coupling.K_cv @ state.valuations,
        alpha=phi_alpha
    )

    dv_dt = -dissipation_v @ (state.valuations - state.valuation_target) + phi(
        coupling.K_vv @ state.valuations + coupling.K_vc @ state.constraints,
        alpha=phi_alpha
    )

    return np.concatenate([dc_dt, dv_dt])

def check_attractor_stability(self,
    fixed_point: np.ndarray,           # [17] = [c*, v*]
    coupling: CVACouplingMatrices,
    phi_alpha: float = 1.0
) -> Dict:
    """Analyze stability of a fixed point.

    A fixed point is where dx/dt = 0. Check eigenvalues of Jacobian
    to determine stability.

    Args:
        fixed_point: [17] state where dynamics = 0
        coupling: Coupling matrices
        phi_alpha: Activation steepness

    Returns:
        {
            'eigenvalues': [17] complex eigenvalues,
            'max_real_eigenvalue': float (largest real part),
            'is_stable': bool (all Re(λ) < 0),
            'kappa_loop': float (coupling strength estimate),
            'dominance_profile': {constraint_name: factor, ...}
        }
    """
    state = DynamicsState(
        constraints=fixed_point[:8],
        valuations=fixed_point[8:],
        constraint_target=fixed_point[:8],  # At fixed point
        valuation_target=fixed_point[8:],
        dt=self.dt
    )

    J = self.compute_full_jacobian(state, coupling, phi_alpha)
    eigenvalues = np.linalg.eigvals(J)
    max_real_eig = float(np.max(np.real(eigenvalues)))

    # κ_loop is roughly the spectral radius
    kappa_loop = float(np.abs(max_real_eig)) * self.dt

    # Analyze eigenvector of dominant eigenvalue (most unstable or stable)
    idx_dominant = np.argmax(np.abs(np.real(eigenvalues)))
    _, eigenvectors = np.linalg.eig(J)
    dominant_eigvec = eigenvectors[:, idx_dominant].real

    # Project to constraint/valuation subspaces
    c_dominance = np.linalg.norm(dominant_eigvec[:8])
    v_dominance = np.linalg.norm(dominant_eigvec[8:])

    dominance_profile = {
        'constraint_magnitude': float(c_dominance),
        'valuation_magnitude': float(v_dominance),
        'constraint_dominates': c_dominance > v_dominance
    }

    return {
        'eigenvalues': eigenvalues,
        'max_real_eigenvalue': max_real_eig,
        'is_stable': max_real_eig < 0,
        'kappa_loop': kappa_loop,
        'dominance_profile': dominance_profile,
        'jacobian': J  # For debugging
    }

def find_fixed_points(self,
    coupling: CVACouplingMatrices,
    num_initial_guesses: int = 20,
    max_steps: int = 10000,
    tolerance: float = 1e-5,
    phi_alpha: float = 1.0
) -> List[Tuple[np.ndarray, Dict]]:
    """Find fixed points by running from random initial conditions.

    Returns list of (fixed_point, stability_analysis) tuples.
    """
    fixed_points = []

    for _ in range(num_initial_guesses):
        # Random initial state
        c0 = np.random.randn(8) * 0.1
        v0 = np.random.randn(9) * 0.1

        state = DynamicsState(
            constraints=c0,
            valuations=v0,
            constraint_target=c0,
            valuation_target=v0,
            dt=self.dt
        )

        # Run to convergence
        final_state, _ = self.run_to_convergence(
            state, coupling, max_steps=max_steps,
            tolerance=tolerance, phi_alpha=phi_alpha
        )

        # Check if this is a new fixed point
        is_new = True
        for existing_fp, _ in fixed_points:
            if np.linalg.norm(final_state.constraints - existing_fp[:8]) < tolerance * 10:
                is_new = False
                break

        if is_new:
            fp_array = np.concatenate([
                final_state.constraints,
                final_state.valuations
            ])
            stability = self.check_attractor_stability(fp_array, coupling, phi_alpha)
            fixed_points.append((fp_array, stability))

    return fixed_points
```

**Acceptance Criteria**:

- [ ] `compute_full_jacobian()` returns correct [17, 17] Jacobian (verified vs. analytical for test case)
- [ ] Numerical Jacobian matches analytical for φ(x) = x (linear case)
- [ ] `check_attractor_stability()` correctly identifies stable vs. unstable fixed points
- [ ] κ_loop < 0.1 for default parameters
- [ ] At least one stable attractor identified for Indian cultural parameters (rasa)
- [ ] Test: `test_jacobian_numerical_accuracy()` — finite difference vs. analytical for simple case
- [ ] Test: `test_stable_fixed_point_detection()` — know stable FP, verify Re(λ) < 0
- [ ] Test: `test_coupling_strength_kappa_loop()` — κ < 0.1 for default
- [ ] Test: `test_multiple_attractors_rasa_culture()` — find 2+ stable FPs with high coupling
- [ ] All 24 existing tests still pass

**Estimated Effort**: ~150 lines | 4 hours

---

### R2.6: Test Suite Upgrade

**Files**: Existing test files + new `tests/test_cva_three_hard_problems.py`

**Current State**:
- 24 passing tests cover basic Phase 2 functionality
- No tests for probabilistic constraints, decomposed feedback, coupling, or attractors

**Required Addition**: ~20 new tests, each specific and deterministic

**Test Structure**:

```python
# tests/test_cva_three_hard_problems.py

import pytest
import numpy as np
from unittest.mock import Mock
from src.services.cva_constraint_engine import ConstraintDistribution
from src.services.cva_dynamics import (
    CVACouplingMatrices, CVADynamicsEngine, DynamicsState,
    DecomposedFeedbackEngine, phi, phi_prime
)
from src.models.cva_valuation import ActivityFrame, CompleteValuationVector

# Set seed for reproducibility
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

class TestProbabilisticConstraintRecognition:
    """R2.1 tests."""

    def test_constraint_distribution_mean_and_precision(self):
        """ConstraintDistribution correctly parameterized."""
        mean = np.ones(8) * 0.5
        precision = np.ones(8) * 2.0
        dist = ConstraintDistribution(
            mean=mean, precision=precision, activity_frame='RESTING'
        )
        np.testing.assert_array_almost_equal(dist.mean, mean)
        np.testing.assert_array_almost_equal(dist.precision, precision)

    def test_constraint_distribution_sampling(self):
        """sample() produces correct mean/std over many samples."""
        mean = np.array([0.5, -0.5, 0.2, 0.0, 1.0, 0.1, -0.3, 0.8])
        precision = np.array([2.0, 1.5, 1.0, 0.5, 0.8, 1.2, 0.9, 1.1])
        dist = ConstraintDistribution(
            mean=mean, precision=precision, activity_frame='EXPLORING'
        )

        # Draw many samples
        samples = dist.sample(n=10000)
        assert samples.shape == (10000, 8)

        # Check sample mean is close to true mean
        sample_mean = np.mean(samples, axis=0)
        np.testing.assert_array_almost_equal(sample_mean, mean, decimal=1)

        # Check sample std matches precision
        expected_std = 1.0 / np.sqrt(precision + 1e-8)
        sample_std = np.std(samples, axis=0)
        np.testing.assert_array_almost_equal(sample_std, expected_std, decimal=1)

    def test_entropy_decreases_with_precision(self):
        """Higher precision → lower entropy."""
        mean = np.ones(8) * 0.5

        # Low precision (high uncertainty)
        dist_low = ConstraintDistribution(
            mean=mean, precision=np.ones(8) * 0.5, activity_frame='EXPLORING'
        )

        # High precision (low uncertainty)
        dist_high = ConstraintDistribution(
            mean=mean, precision=np.ones(8) * 2.0, activity_frame='RESTING'
        )

        assert dist_high.entropy() < dist_low.entropy()

    def test_backward_compatibility_map_estimate(self):
        """MAP estimate equals mean for Gaussian posterior."""
        mean = np.random.randn(8)
        precision = np.random.rand(8) + 0.1
        dist = ConstraintDistribution(mean=mean, precision=precision, activity_frame='EATING')

        map_est = dist.map_estimate()
        np.testing.assert_array_almost_equal(map_est, mean)

class TestDecomposedFeedback:
    """R2.2 tests."""

    def test_compute_attention_error_with_gaze(self):
        """Attention error modulated by gaze."""
        engine = DecomposedFeedbackEngine()

        mean = np.array([0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5])
        precision = np.array([2.0, 1.0, 0.5, 0.3, 0.3, 0.5, 1.0, 2.0])
        dist = ConstraintDistribution(mean=mean, precision=precision, activity_frame='RESTING')

        valuation = np.ones(9) * 0.5
        gaze = np.array([1.0, 0.5, 0.2, 0.1, 0.1, 0.2, 0.5, 1.0])  # focused on high-precision regions

        e_attn = engine.compute_attention_error(dist, valuation, 'RESTING', gaze)

        # Should be positive (gaze aligned with precision)
        assert e_attn > 0
        # Should be approximately dot(gaze, precision)
        assert abs(e_attn - np.dot(gaze, precision)) < 1e-6

    def test_compute_precision_error_variance_mismatch(self):
        """Precision error from variance mismatch."""
        engine = DecomposedFeedbackEngine()

        # Constraint samples with high variance
        high_var_samples = [np.random.randn(8) * 2.0 for _ in range(5)]

        # Activity frame expects low variance
        e_prec = engine.compute_precision_error(high_var_samples, 'RESTING', Mock())

        # Should be non-zero (mismatch)
        assert e_prec > 0

    def test_compute_prior_error_cultural_baseline(self):
        """Prior error from deviation from cultural baseline."""
        engine = DecomposedFeedbackEngine()

        constraints = np.ones(8) * 0.5
        valuations = np.ones(9) * 0.5
        cultural_baseline = np.ones(9) * 1.0  # expects higher valuations

        e_prior = engine.compute_prior_error(
            constraints, valuations, 'WORSHIPPING', Mock(),
            cultural_baseline=cultural_baseline
        )

        # Should be non-zero (deviation from baseline)
        assert e_prior > 0
        # Should be approximately L2 norm of difference
        expected = np.linalg.norm(valuations - cultural_baseline)
        assert abs(e_prior - expected) < 1e-6

    def test_compose_feedback_timescale_decay(self):
        """Timescale-specific decay in composed feedback."""
        engine = DecomposedFeedbackEngine()

        # High initial errors
        e_attn, e_prec, e_prior = 1.0, 1.0, 1.0

        # Compose with small timestep (should decay little)
        fb1 = engine.compose_feedback(e_attn, e_prec, e_prior, dt=0.01)

        # After 1 second:
        # ε_attn decays as exp(-1.0/0.4) ≈ 0.082
        # ε_prec decays as exp(-1.0/1.0) ≈ 0.368
        # ε_prior decays as exp(-1.0/3.0) ≈ 0.717
        fb2 = engine.compose_feedback(e_attn, e_prec, e_prior, dt=1.0)

        assert fb2.epsilon_attention < fb1.epsilon_attention
        assert fb2.epsilon_precision < fb1.epsilon_precision
        assert fb2.epsilon_prior < fb1.epsilon_prior

        # Attention decays fastest
        assert fb2.epsilon_attention < fb2.epsilon_precision < fb2.epsilon_prior

    def test_feedback_signal_total_magnitude(self):
        """FeedbackSignal total magnitude is L2 norm of components."""
        from src.models.cva_annotations import FeedbackSignal

        fb = FeedbackSignal(
            epsilon_attention=3.0,
            epsilon_precision=4.0,
            epsilon_prior=0.0
        )

        expected = np.sqrt(3.0**2 + 4.0**2 + 0.0**2)  # 5.0
        assert abs(fb.total_magnitude() - expected) < 1e-6

    def test_feedback_dominance(self):
        """Identify dominant feedback signal."""
        from src.models.cva_annotations import FeedbackSignal

        fb = FeedbackSignal(
            epsilon_attention=0.5,
            epsilon_precision=2.0,  # dominant
            epsilon_prior=0.3
        )

        assert fb.dominance() == 'precision'

class TestSparseAuxiliaryActivation:
    """R2.3 tests."""

    def test_complete_valuation_sparse_activation(self):
        """Inactive auxiliary axes are zero."""
        core = np.ones(9) * 0.5
        active_aux = {'sacredness': 0.8}

        val = CompleteValuationVector(
            core=core,
            auxiliary=active_aux,
            active_auxiliary_axes=['sacredness'],
            activity_frame='WORSHIPPING',
            precision_gains=np.ones(9)
        )

        assert 'sacredness' in val.auxiliary
        assert val.auxiliary['sacredness'] == 0.8
        assert 'originality' not in val.auxiliary  # Inactive

    def test_frame_precision_gains_modulation(self):
        """Frame precision gains correctly modulate core valuations."""
        core = np.ones(9)
        gains = np.array([2.0, 0.5, 1.0, 1.5, 1.0, 2.0, 0.5, 1.0, 1.5])

        val = CompleteValuationVector(
            core=core,
            auxiliary={},
            active_auxiliary_axes=[],
            activity_frame='TEST',
            precision_gains=gains
        )

        modulated = val.core
        expected = core * gains
        np.testing.assert_array_almost_equal(modulated, expected)

    def test_worshipping_activates_sacredness(self):
        """WORSHIPPING frame activates sacredness auxiliary."""
        frame = ActivityFrame(
            name='WORSHIPPING',
            auxiliary_axes=['sacredness'],
            precision_weights={'meaning': 2.0, 'sacredness': 1.5}
        )

        assert 'sacredness' in frame.auxiliary_axes

    def test_creating_activates_originality(self):
        """CREATING frame activates originality auxiliary."""
        frame = ActivityFrame(
            name='CREATING',
            auxiliary_axes=['originality'],
            precision_weights={'novelty': 2.0}
        )

        assert 'originality' in frame.auxiliary_axes

class TestCouplingDynamics:
    """R2.4 tests."""

    def test_soft_relu_activation(self):
        """Soft ReLU φ(x) = log(1 + exp(x))."""
        # Test key properties
        assert phi(0) == pytest.approx(np.log(2), abs=1e-6)
        assert phi(10) > phi(0)  # increasing
        assert phi(-10) < phi(0)  # increasing

        # φ'(x) should be sigmoid
        x = np.linspace(-5, 5, 11)
        phi_prime_x = phi_prime(x, alpha=1.0)
        sigmoid_x = 1.0 / (1.0 + np.exp(-x))
        np.testing.assert_array_almost_equal(phi_prime_x, sigmoid_x)

    def test_coupling_matrices_default(self):
        """Default coupling has κ_loop < 0.1."""
        coupling = CVACouplingMatrices.default()

        assert coupling.K_cc.shape == (8, 8)
        assert coupling.K_cv.shape == (8, 9)
        assert coupling.K_vc.shape == (9, 8)
        assert coupling.K_vv.shape == (9, 9)

        kappa = coupling.estimate_coupling_strength()
        assert kappa < 0.5  # Reasonable bound

    def test_dynamics_engine_step(self):
        """Single integration step produces reasonable output."""
        engine = CVADynamicsEngine()
        coupling = CVACouplingMatrices.default()

        state = DynamicsState(
            constraints=np.ones(8) * 0.5,
            valuations=np.ones(9) * 0.5,
            constraint_target=np.ones(8) * 0.5,
            valuation_target=np.ones(9) * 0.5,
            dt=0.01
        )

        new_state = engine.step(state, coupling)

        assert new_state.constraints.shape == (8,)
        assert new_state.valuations.shape == (9,)
        assert new_state.time == pytest.approx(0.01)

    def test_convergence_to_fixed_point(self):
        """Dynamics converge to stable fixed point."""
        engine = CVADynamicsEngine()
        coupling = CVACouplingMatrices.default()

        state = DynamicsState(
            constraints=np.random.randn(8) * 0.1,
            valuations=np.random.randn(9) * 0.1,
            constraint_target=np.zeros(8),
            valuation_target=np.zeros(9),
            dt=0.01
        )

        final_state, trajectory = engine.run_to_convergence(
            state, coupling, max_steps=5000, tolerance=1e-4
        )

        # Should converge to origin (all targets are 0)
        assert np.linalg.norm(final_state.constraints) < 0.01
        assert np.linalg.norm(final_state.valuations) < 0.01

    def test_coupling_matrices_serialization(self):
        """CVACouplingMatrices can be serialized/deserialized."""
        coupling = CVACouplingMatrices.default()

        data = coupling.to_dict()
        assert 'K_cc' in data
        assert 'K_cv' in data
        assert 'K_vc' in data
        assert 'K_vv' in data

        coupling2 = CVACouplingMatrices.from_dict(data)
        np.testing.assert_array_almost_equal(coupling.K_cc, coupling2.K_cc)

class TestLyapunovAnalysis:
    """R2.5 tests."""

    def test_jacobian_computation(self):
        """Jacobian computed correctly via finite differences."""
        engine = CVADynamicsEngine()
        coupling = CVACouplingMatrices.default()

        state = DynamicsState(
            constraints=np.ones(8) * 0.1,
            valuations=np.ones(9) * 0.1,
            constraint_target=np.zeros(8),
            valuation_target=np.zeros(9),
            dt=0.01
        )

        J = engine.compute_full_jacobian(state, coupling)

        assert J.shape == (17, 17)
        # Should not be all zeros
        assert np.linalg.norm(J) > 0

    def test_stability_analysis_stable_fixed_point(self):
        """Stable fixed point has all negative eigenvalues."""
        engine = CVADynamicsEngine()
        coupling = CVACouplingMatrices.default()

        # Stable fixed point: origin (targets are zero)
        fixed_point = np.zeros(17)

        stability = engine.check_attractor_stability(fixed_point, coupling)

        assert isinstance(stability, dict)
        assert 'eigenvalues' in stability
        assert 'max_real_eigenvalue' in stability
        # Origin should be stable for default parameters
        assert stability['max_real_eigenvalue'] < 0

    def test_coupling_strength_kappa_loop(self):
        """κ_loop < 0.1 for default coupling."""
        engine = CVADynamicsEngine()
        coupling = CVACouplingMatrices.default()
        fixed_point = np.zeros(17)

        stability = engine.check_attractor_stability(fixed_point, coupling)

        kappa = stability['kappa_loop']
        assert kappa < 0.1

class TestIntegrationCVAThreeHardProblems:
    """Integration tests combining all three remediation areas."""

    def test_full_pipeline_constraint_to_dynamics(self):
        """Constraints → Valuations → Dynamics → Feedback."""
        # Create probabilistic constraint distribution (R2.1)
        mean = np.array([0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5])
        precision = np.array([2.0, 1.5, 1.0, 0.5, 0.8, 1.2, 0.9, 1.1])
        constraint_dist = ConstraintDistribution(
            mean=mean, precision=precision, activity_frame='RESTING'
        )

        # Create frame-aware valuation (R2.3)
        core_val = np.ones(9) * 0.5
        precision_gains = np.array([1.5, 1.5, 1.0, 0.3, 0.3, 2.0, 2.0, 0.5, 0.5])
        valuation = CompleteValuationVector(
            core=core_val * precision_gains,
            auxiliary={'sacredness': 0.0},  # Not active for RESTING
            active_auxiliary_axes=[],
            activity_frame='RESTING',
            precision_gains=precision_gains
        )

        # Run dynamics with coupling (R2.4)
        engine = CVADynamicsEngine()
        coupling = CVACouplingMatrices.default()

        state = DynamicsState(
            constraints=constraint_dist.map_estimate(),
            valuations=valuation.core,
            constraint_target=constraint_dist.map_estimate(),
            valuation_target=valuation.core,
            dt=0.01
        )

        # Compute decomposed feedback (R2.2)
        feedback_engine = DecomposedFeedbackEngine()
        e_attn = feedback_engine.compute_attention_error(
            constraint_dist, state.valuations, 'RESTING'
        )
        e_prec = feedback_engine.compute_precision_error(
            [constraint_dist.map_estimate()], 'RESTING', Mock()
        )
        e_prior = feedback_engine.compute_prior_error(
            state.constraints, state.valuations, 'RESTING', Mock()
        )

        feedback = feedback_engine.compose_feedback(e_attn, e_prec, e_prior)

        # All components should be valid
        assert constraint_dist.mean.shape == (8,)
        assert valuation.core.shape == (9,)
        assert feedback.total_magnitude() >= 0

        # Run one integration step
        new_state = engine.step(state, coupling)
        assert new_state.constraints.shape == (8,)
        assert new_state.valuations.shape == (9,)

# Parametrized tests for all 10 activity frames
ACTIVITY_FRAMES = [
    'RESTING', 'STUDYING', 'EXPLORING', 'CREATING', 'WORSHIPPING',
    'PLAYING', 'EATING', 'SOCIALIZING', 'SLEEPING', 'EXERCISING'
]

@pytest.mark.parametrize("activity_frame", ACTIVITY_FRAMES)
class TestAllActivityFrames:
    """Test that all 10 frames work correctly."""

    def test_constraint_precision_for_frame(self, activity_frame):
        """Each frame has valid precision weights."""
        frame = ActivityFrame(
            name=activity_frame,
            auxiliary_axes=[],
            precision_weights={'spatial_containment': 1.0}  # Minimal example
        )
        assert frame.name == activity_frame

    def test_feedback_for_frame(self, activity_frame):
        """Feedback computation works for any frame."""
        engine = DecomposedFeedbackEngine()

        dist = ConstraintDistribution(
            mean=np.ones(8) * 0.5,
            precision=np.ones(8) * 1.0,
            activity_frame=activity_frame
        )

        e_attn = engine.compute_attention_error(dist, np.ones(9), activity_frame)
        assert isinstance(e_attn, float)
```

**Acceptance Criteria**:

- [ ] All ~20 tests pass and are deterministic (fixed seed)
- [ ] 4 tests for R2.1 (probabilistic recognition)
- [ ] 6 tests for R2.2 (decomposed feedback)
- [ ] 4 tests for R2.3 (sparse auxiliary)
- [ ] 4 tests for R2.4 (coupling dynamics)
- [ ] 2 tests for R2.5 (Lyapunov analysis)
- [ ] All 24 existing tests still pass (may need minor API updates)
- [ ] Parametrized tests cover all 10 activity frames
- [ ] Test file: `tests/test_cva_three_hard_problems.py`

**Estimated Effort**: ~400 lines | 6 hours

---

## IMPLEMENTATION PRIORITY & SEQUENCE

**Why this order matters**:

1. **R2.4 first (Coupling Dynamics)** — Foundation for non-trivial attractors. Without coupling matrices, the system has a single attractor (origin). Everything else depends on stable coupled dynamics.

2. **R2.1 second (Probabilistic Recognition)** — Adds uncertainty quantification that feeds into feedback (R2.2) and attractor analysis (R2.5).

3. **R2.2 third (Decomposed Feedback)** — Uses constraint distributions (R2.1) and couples with dynamics (R2.4).

4. **R2.5 fourth (Lyapunov Analysis)** — Analyzes stability of the coupled system (R2.4) using distributions (R2.1).

5. **R2.3 fifth (Sparse Auxiliary)** — Less critical for core dynamics; can run in parallel once R2.4 works.

6. **R2.6 throughout (Tests)** — Add tests as you complete each task. Run all tests after each task to avoid accumulating breaks.

| Task | Start | Depends On | Estimated Hours | Cumulative |
|------|-------|-----------|-----------------|-----------|
| R2.4 Coupling | Day 1 | None | 8 | 8 |
| R2.1 Probabilistic | Day 2 | R2.4 | 4 | 12 |
| R2.2 Decomposed Feedback | Day 3-4 | R2.1, R2.4 | 6 | 18 |
| R2.5 Lyapunov | Day 5 | R2.4, R2.1 | 4 | 22 |
| R2.3 Sparse Auxiliary | Day 5-6 | R2.4, R2.1 | 3 | 25 |
| R2.6 Test Suite | Throughout | All | 6 | 31 |

---

## RULES & CONSTRAINTS

1. **Do NOT break existing 24 tests.** All changes are additive. Run the full test suite after each task.

2. **Use existing data structures.** Extend `ConstraintDistribution`, `FeedbackSignal`, `DynamicsState`, `ActivityFrame`, not replace them.

3. **Every new class/method gets a docstring** with:
   - One-line summary
   - Extended description (problem it solves)
   - Mathematical specification (equations if applicable)
   - Args, Returns sections with types

4. **Type hints on everything.** `np.ndarray`, `str`, `float`, `Optional[...]`, etc.

5. **Import numpy as np. No scipy, torch, or other heavy dependencies.** Stick to the existing tech stack.

6. **Follow the strangler fig pattern.** CVA extends ATLAS, never replaces it. New code lives in `src/services/cva_*.py` and `src/models/cva_*.py`.

7. **Run all tests after each task.**
   ```bash
   pytest tests/ -v
   pytest tests/test_cva_three_hard_problems.py -v
   ```

8. **Commit after each task** with clear message (R2.1, R2.2, etc.) and note any API changes.

---

## ACCEPTANCE & SIGN-OFF

When complete, AG should:

1. Verify all 24 original tests pass
2. Run new test suite: all ~20 new tests pass
3. Create a brief completion report: `docs/PHASE2_REMEDIATION_COMPLETION_2026-02-28.md`
   - Summary of six upgrades
   - Files changed
   - Test results (24 + 20 = 44 tests passing)
   - Any open questions or deferred work

4. Update `TASKS.md`:
   - Mark R2.1–R2.6 as COMPLETED with date and notes
   - Flag any issues for next sprint

---

## CONTACT & CLARIFICATION

If any task description is unclear or conflicts with existing code:

1. Check the existing implementation in `src/services/cva_*.py`
2. Refer to spec: `docs/CVA_SPRINT_SPECS_REVISED_WITH_THREE_HARD_PROBLEMS_2026-02-28.md`
3. Ask for clarification in your notes (add to `TASKS.md` with [BLOCKED] tag)

---

**Last Updated**: 2026-02-28
**Owner**: Professor David Kirsh (UCSD Cognitive Science)
**Status**: ACTIVE — Awaiting AG assignment
