# CVA Sprint Specifications: Revised with Chat's Three Hard Problems Solutions
## Comprehensive Engineering Specification for AG Implementation

**Date**: February 28, 2026
**Version**: CVA-SPECIFICATIONS-2.0-FINAL
**Status**: READY FOR AG IMPLEMENTATION
**Audience**: Claude Code (AG), with secondary review by David Kirsh and expert panels
**Target**: Directly executable specifications with concrete method signatures and test requirements

---

## EXECUTIVE SUMMARY

Chat's Three Hard Problems panel (12 experts: Scherer, Zumthor, Barrett, Kitayama, Friston, Strogatz, Jordan, Eisenberger, Ramachandran, Cartwright, Haack, Pollock) produced three foundational solutions that restructure the CVA implementation plan:

### Q2 SOLUTION: Recognition as Probabilistic Process (for CVA-1-REV)

**Original approach**: Constraint function c = f(x) is deterministic; constraint values treated as ground truth.

**Chat's solution**: Replace with probabilistic recognition model:
```
c ~ p(c|x, A, ψ)
```

Constraints are recognized (attended to, categorized) through learned inference—not computed from stimuli. ActivityFrame modulates constraint recognition via attention gating.

**Implementation impact**:
- Constraints become stochastic rather than deterministic
- ActivityFrame controls recognition salience (A→c attention pathway)
- Recognition model must be trained/calibrated on behavioral data
- Constraint values become posterior means: c_post = E[c | x, A, ψ]

---

### Q1 SOLUTION: Two-Tier Valuation Architecture (for CVA-2-REV)

**Original approach**: Single monolithic valuation vector with 9 axes.

**Chat's solution**: Decompose into **stable core + sparse context-activated auxiliary**:
```
v_core = {SafetyValue, InterestValue, RestorationValue, StatusValue,
          BelongingValue, IdentityCongruenceValue, AutonomySupportValue,
          CompetenceSupportValue, RelatednessSupportValue}

v_aux(A, ψ) = context-activated dimensions {SacrednessValue, RitualFitValue,
              MarketValueEstimate, ...}
```

**Interpretation**: Cultural universals in v_core; cultural specificity in v_aux. ActivityFrame enables/disables auxiliary axes.

**Implementation impact**:
- All cultures recognize v_core universally
- Auxiliary dimensions activated by ActivityFrame and modulated by ψ_culture
- Valuation vector dimension can vary (9 for Western, 10 for others with auxiliaries)
- Enables efficient representation and cultural variation

---

### Q3 SOLUTION: Decomposed Feedback with Three Error Signals (for CVA-2-REV & CVA-3)

**Original approach**: Single valuation error drives updates; no mechanistic separation.

**Chat's solution**: Three independent feedback pathways:

```
ε_attn: Attentional error → shifts where gaze goes (sampling bias toward
        constraint-informative regions). Mechanism: dorsal frontoparietal
        gating of saccades. Timescale: 0.3–0.5s.

ε_prec: Precision error → scales valuation gain via learned π(A, ψ).
        Mechanism: V1/V2 gain modulation (contrast gain); state-dependent
        weighting of constraints. Timescale: 0.5–2.0s.

ε_prior: Prior-expectation error → shifts β(A, ψ_culture) pre-activation
        of valuation priors. Mechanism: mPFC-hippocampal prediction error.
        Timescale: 1–5s.
```

**Implementation impact**:
- CVA-2-REV: Add `ε_attn`, `ε_prec`, `ε_prior` computation functions
- CVA-3: ActivityFrame controls all three via lookup tables {A → (Δπ, Δβ, attention_mask)}
- Each error signal has distinct units and neural target (enables Eisenberger validation)
- Feedback composition: v̇ = -D_v(v - V̄) + ε_prec·φ_v(K_vv·v) + ε_prior·β(A)

---

## PART 1: CVA-1-REV REVISED SPECIFICATION

### Scope: Probabilistic Constraint Recognition + Two-Tier Architecture

**Duration**: 2.5 weeks | **Effort**: 19 person-days | **Dependencies**: Phase 0 complete

---

### 1.1 Constraint Recognition Model (Probabilistic)

#### Overview

Constraints are now recognized through a learned classifier p(c|x,A,ψ) rather than computed deterministically. This addresses Scherer's concern that constraint recognition is attention-dependent and Friston's requirement that constraint changes precede valuation changes with measurable mechanism.

#### Data Structures

**File**: `src/models/cva_constraint_recognition.py` (NEW, ~300 lines)

```python
from dataclasses import dataclass
from typing import Optional, Callable
import numpy as np
from enum import Enum

class ConstraintType(Enum):
    """Eight constraint variables, formalized as recognizable patterns."""
    PROCESSING_COST = "processing_cost"
    LOAD_RATE = "load_rate"
    PREDICTION_ERROR = "prediction_error"
    CONTROL_EFFICACY = "control_efficacy"
    AFFORDANCE_DENSITY = "affordance_density"
    SOCIAL_CUE_DENSITY = "social_cue_density"
    MULTISENSORY_COHERENCE = "multisensory_coherence"
    NARRATIVE_COHERENCE = "narrative_coherence"

@dataclass
class Tier1ConstraintVector:
    """
    Tier 1: Universal perceptual primitives (invariant across subjects except for aging).
    These are the low-level feature detectors present in all human visual/auditory systems.

    Normalized to [0, 1]. Represent raw feature presence/salience.
    """
    edge_detection: float          # Presence of contours/boundaries [0,1]
    motion_detection: float        # Temporal change rate [0,1]
    figure_ground: float           # Separation clarity [0,1]
    luminance_contrast: float      # Light/dark variation [0,1]
    temporal_coherence: float      # Predictability of motion/change [0,1]
    symmetry_detection: float      # Bilateral/rotational symmetry [0,1]

    tier: int = 1
    timestamp_created: str = ""    # ISO format timestamp

    def validate(self) -> bool:
        """Ensure all fields in [0, 1]."""
        for field in [self.edge_detection, self.motion_detection,
                     self.figure_ground, self.luminance_contrast,
                     self.temporal_coherence, self.symmetry_detection]:
            if not (0 <= field <= 1):
                return False
        return True

    def as_vector(self) -> np.ndarray:
        """Return as numpy array [6]."""
        return np.array([
            self.edge_detection, self.motion_detection, self.figure_ground,
            self.luminance_contrast, self.temporal_coherence, self.symmetry_detection
        ])

@dataclass
class Tier2ConstraintVector:
    """
    Tier 2: Interpreted constraint values, computed from Tier 1 + ψ (subject characteristics).
    These are the high-level constraint interpretations: "this environment is visually complex"
    (ProcessingCost), "this place has many action possibilities" (AffordanceDensity), etc.

    Normalized to [0, 1]. Computed via posterior means from recognition model p(c|x,A,ψ).
    """
    processing_cost: float              # Computational burden [0,1]
    load_rate: float                    # Temporal event density [0,1]
    prediction_error: float             # Surprise/entropy [0,1]
    control_efficacy: float             # Actionability/wayfindability [0,1]
    affordance_density: float           # Action possibility density [0,1]
    social_cue_density: float           # Social information presence [0,1]
    multisensory_coherence: float       # Cross-modal alignment [0,1]
    narrative_coherence: float          # Spatial storytelling consistency [0,1]

    tier: int = 2
    psi_culture: Optional[str] = None        # Cultural context hash
    psi_neuro: Optional[str] = None          # Neurotype identifier
    psi_dev_age: Optional[float] = None      # Age in years
    uncertainty_bounds: dict = None          # {constraint: (lower, upper)} credible intervals
    timestamp_created: str = ""              # ISO format

    def __post_init__(self):
        if self.uncertainty_bounds is None:
            self.uncertainty_bounds = {}

    def validate(self) -> bool:
        """Ensure all constraint values in [0, 1]."""
        for field in [self.processing_cost, self.load_rate, self.prediction_error,
                     self.control_efficacy, self.affordance_density, self.social_cue_density,
                     self.multisensory_coherence, self.narrative_coherence]:
            if not (0 <= field <= 1):
                return False
        return True

    def as_vector(self) -> np.ndarray:
        """Return as numpy array [8]."""
        return np.array([
            self.processing_cost, self.load_rate, self.prediction_error,
            self.control_efficacy, self.affordance_density, self.social_cue_density,
            self.multisensory_coherence, self.narrative_coherence
        ])

    @classmethod
    def from_tier1_and_psi(cls, tier1: Tier1ConstraintVector,
                           psi_neuro: str, psi_culture: str, psi_dev_age: float,
                           transform_fn: Callable) -> 'Tier2ConstraintVector':
        """
        Derive Tier 2 from Tier 1 using ψ-parameterized transformation function.

        Args:
            tier1: Tier1ConstraintVector with raw features
            psi_neuro: Neurotype identifier (TYPICAL, PTSD, ASD, ADHD, etc.)
            psi_culture: Cultural context identifier
            psi_dev_age: Age in years (used for developmental stage calculation)
            transform_fn: Function(tier1_vec, psi_dict) -> tier2_vec (learned mapping)

        Returns:
            Tier2ConstraintVector with posterior means and uncertainty bounds.
        """
        psi_dict = {
            'neuro': psi_neuro,
            'culture': psi_culture,
            'dev_age': psi_dev_age
        }
        tier2_vec, uncertainty = transform_fn(tier1.as_vector(), psi_dict)

        return cls(
            processing_cost=tier2_vec[0],
            load_rate=tier2_vec[1],
            prediction_error=tier2_vec[2],
            control_efficacy=tier2_vec[3],
            affordance_density=tier2_vec[4],
            social_cue_density=tier2_vec[5],
            multisensory_coherence=tier2_vec[6],
            narrative_coherence=tier2_vec[7],
            psi_culture=psi_culture,
            psi_neuro=psi_neuro,
            psi_dev_age=psi_dev_age,
            uncertainty_bounds=uncertainty
        )

@dataclass
class ConstraintRecognitionModel:
    """
    Probabilistic constraint recognition: p(c|x, A, ψ).

    This is a learned mapping from (stimulus x, ActivityFrame A, subject characteristics ψ)
    to constraint posterior distributions. Can be instantiated as:
    - Logistic regression (simple baseline)
    - Neural network classifier (production)
    - Gaussian process (for uncertainty quantification)
    """
    model_type: str                         # 'logistic', 'neural', 'gp'
    model_path: str                         # Path to saved model weights
    feature_extractor: Callable             # Function(x) -> features [D]
    temperature: float = 1.0                # Softmax temperature for calibration

    def recognize(self, stimulus: np.ndarray, activity_frame: str,
                 psi_dict: dict) -> tuple[Tier2ConstraintVector, dict]:
        """
        Recognize constraints from stimulus given activity frame and ψ.

        Args:
            stimulus: Environment features [D]; can be ATLAS feature vector
            activity_frame: Activity frame identifier (STUDYING, SOCIALIZING, etc.)
            psi_dict: Subject characteristics {neuro, culture, dev_age, ...}

        Returns:
            (tier2_constraint_vector, uncertainty_estimates)

        Implementation notes:
        - Extract features: features = self.feature_extractor(stimulus)
        - Condition on activity_frame: embed A as one-hot or learned representation
        - Condition on ψ: embed psi_dict or use as direct input features
        - Predict: p(c|features, A, ψ) via model
        - Return posterior mean as Tier2ConstraintVector, uncertainty from model
        """
        # Stub: to be filled by AG with model-specific logic
        pass

    def update_from_feedback(self, stimulus: np.ndarray, activity_frame: str,
                            psi_dict: dict, constraint_rating: Tier2ConstraintVector,
                            learning_rate: float = 0.01) -> None:
        """
        Lightweight online update of recognition model given human feedback on constraint recognition.

        This enables the system to calibrate constraint recognition post-deployment.
        For production: consider using importance weighting or Bayesian online learning.
        """
        pass

class ConstraintRecognitionRegistry:
    """Registry of recognized constraint types and their recognition models."""

    def __init__(self):
        self.constraints: dict[ConstraintType, ConstraintRecognitionModel] = {}
        self.tier1_extractor: Optional[Callable] = None  # Function to extract Tier 1 from raw stimulus

    def register(self, constraint_type: ConstraintType,
                model: ConstraintRecognitionModel) -> None:
        """Register a recognition model for a constraint type."""
        self.constraints[constraint_type] = model

    def recognize_all(self, stimulus: np.ndarray, activity_frame: str,
                     psi_dict: dict, tier1: Tier1ConstraintVector) -> Tier2ConstraintVector:
        """
        Recognize all 8 constraints for given stimulus + context.

        Implementation strategy:
        1. For each of 8 constraint types, call recognize() via registered model
        2. Collect posterior means into Tier2ConstraintVector
        3. Collect uncertainty bounds
        4. Return combined Tier2ConstraintVector
        """
        pass

    def set_tier1_extractor(self, fn: Callable) -> None:
        """Set function to extract Tier 1 primitives from raw stimulus."""
        self.tier1_extractor = fn

    def extract_tier1(self, stimulus: np.ndarray) -> Tier1ConstraintVector:
        """Extract Tier 1 features from stimulus using registered function."""
        if not self.tier1_extractor:
            raise ValueError("Tier 1 extractor not set. Call set_tier1_extractor() first.")
        features = self.tier1_extractor(stimulus)
        return Tier1ConstraintVector(*features)
```

---

#### Test Specification

**File**: `tests/test_cva_constraint_recognition.py` (~250 lines)

```python
import pytest
import numpy as np
from src.models.cva_constraint_recognition import (
    Tier1ConstraintVector, Tier2ConstraintVector, ConstraintRecognitionModel,
    ConstraintRecognitionRegistry, ConstraintType
)

class TestTier1ConstraintVector:
    """Tests for Tier 1 (universal) constraints."""

    def test_tier1_creation_and_validation(self):
        """Tier 1 vector should validate [0,1] range."""
        tier1 = Tier1ConstraintVector(
            edge_detection=0.5, motion_detection=0.3, figure_ground=0.7,
            luminance_contrast=0.4, temporal_coherence=0.6, symmetry_detection=0.2
        )
        assert tier1.validate()
        assert tier1.tier == 1
        assert tier1.as_vector().shape == (6,)

    def test_tier1_rejects_out_of_range(self):
        """Out-of-range values should fail validation."""
        tier1 = Tier1ConstraintVector(
            edge_detection=1.5, motion_detection=0.3, figure_ground=0.7,
            luminance_contrast=0.4, temporal_coherence=0.6, symmetry_detection=0.2
        )
        assert not tier1.validate()

class TestTier2ConstraintVector:
    """Tests for Tier 2 (ψ-calibrated) constraints."""

    def test_tier2_creation_and_validation(self):
        """Tier 2 should validate and store ψ metadata."""
        tier2 = Tier2ConstraintVector(
            processing_cost=0.6, load_rate=0.3, prediction_error=0.4,
            control_efficacy=0.7, affordance_density=0.5, social_cue_density=0.2,
            multisensory_coherence=0.8, narrative_coherence=0.6,
            psi_neuro='TYPICAL', psi_culture='WESTERN', psi_dev_age=25.0
        )
        assert tier2.validate()
        assert tier2.tier == 2
        assert tier2.psi_neuro == 'TYPICAL'

    def test_tier2_from_tier1_transformation(self):
        """Tier 2 should derive from Tier 1 via learned mapping."""
        tier1 = Tier1ConstraintVector(
            edge_detection=0.5, motion_detection=0.3, figure_ground=0.7,
            luminance_contrast=0.4, temporal_coherence=0.6, symmetry_detection=0.2
        )

        # Stub transformation: just scale and reorder
        def simple_transform(tier1_vec, psi_dict):
            tier2_vec = np.array([
                tier1_vec[0] * 0.9,  # processing_cost = edge_detection * neuro_factor
                tier1_vec[1] * 0.8,  # load_rate = motion_detection * culture_factor
                tier1_vec[2] * 0.7,  # prediction_error
                # ... etc
            ])
            uncertainty = {f'constraint_{i}': (tier2_vec[i] - 0.1, tier2_vec[i] + 0.1)
                          for i in range(8)}
            return tier2_vec, uncertainty

        tier2 = Tier2ConstraintVector.from_tier1_and_psi(
            tier1, psi_neuro='TYPICAL', psi_culture='WESTERN',
            psi_dev_age=25.0, transform_fn=simple_transform
        )
        assert tier2.validate()
        assert tier2.psi_neuro == 'TYPICAL'

class TestConstraintRecognitionRegistry:
    """Tests for registry functionality."""

    def test_registry_register_and_retrieve(self):
        """Registry should store and retrieve recognition models."""
        registry = ConstraintRecognitionRegistry()
        model = ConstraintRecognitionModel(
            model_type='logistic',
            model_path='models/constraint_recognition_logistic.pkl',
            feature_extractor=lambda x: x[:10],  # Stub: take first 10 features
            temperature=1.0
        )
        registry.register(ConstraintType.PROCESSING_COST, model)
        assert ConstraintType.PROCESSING_COST in registry.constraints

    def test_tier1_extractor_integration(self):
        """Registry should use Tier 1 extractor."""
        registry = ConstraintRecognitionRegistry()

        # Stub extractor: return random [0,1] values
        def stub_extractor(stimulus):
            return [0.5, 0.3, 0.7, 0.4, 0.6, 0.2]

        registry.set_tier1_extractor(stub_extractor)
        tier1 = registry.extract_tier1(np.zeros(50))
        assert tier1.validate()
        assert tier1.tier == 1

class TestActivityFrameModulation:
    """
    Integration test: ActivityFrame modulates constraint recognition.
    Same stimulus, different activity frames → different constraint recognition (focus).
    """

    def test_activity_frame_attention_modulation(self):
        """
        Constraint recognition should be modulated by ActivityFrame.
        E.g., in STUDYING frame, ProcessingCost recognition is heightened;
        in SOCIALIZING frame, SocialCueDensity is heightened.
        """
        # Create registry with models
        registry = ConstraintRecognitionRegistry()
        registry.set_tier1_extractor(lambda x: [0.5] * 6)

        # Stub models that respond to activity frame
        def processing_cost_model(stimulus, activity_frame, psi_dict):
            # In STUDYING, recognize cost more strongly
            base = 0.5
            if activity_frame == 'STUDYING':
                return base * 1.2  # 20% amplification
            return base

        # Test: same stimulus, different frames → different recognition
        stimulus = np.ones(50)
        psi = {'neuro': 'TYPICAL', 'culture': 'WESTERN', 'dev_age': 25}

        # (Details: fill in with actual recognition calls once models registered)
```

---

#### Integration with Attention (A→c Pathway)

**File**: `src/services/cva_constraint_attention.py` (NEW, ~200 lines)

This module implements the attention-to-constraint pathway: ActivityFrame gates which constraints are recognized/attended to.

```python
from dataclasses import dataclass
from typing import Optional, List
import numpy as np

@dataclass
class AttentionGating:
    """
    Attention gating mechanism: ActivityFrame controls recognition salience.

    For each constraint, specifies an attention weight ω_attn ∈ [0, 1].
    Higher weight = more likely to recognize this constraint in this frame.
    """
    activity_frame: str
    attention_weights: dict[str, float]  # {constraint_name: ω_attn}

    def gate_constraint_recognition(self,
                                   constraint_name: str,
                                   base_recognition: float) -> float:
        """
        Apply attention gating to constraint recognition.

        Recognition given attention: c_recognized = c_base * ω_attn^(1/α)
        where α ~ 1-2 controls gating sharpness. Higher α = sharper gating.
        """
        weight = self.attention_weights.get(constraint_name, 1.0)
        alpha = 1.5  # Empirically calibrated
        gated = base_recognition * (weight ** (1.0 / alpha))
        return np.clip(gated, 0, 1)

class AttentionGatingRegistry:
    """
    Registry of attention gating patterns for each ActivityFrame.

    Key insight: Gating patterns encode "what matters in this context."
    STUDYING frame: heighten attention to ProcessingCost, PredictionError
    SOCIALIZING frame: heighten attention to SocialCueDensity, BelongingValue
    """

    def __init__(self):
        self.gating_patterns: dict[str, AttentionGating] = {}

    def register_frame(self, activity_frame: str, gating: AttentionGating) -> None:
        """Register attention gating pattern for activity frame."""
        self.gating_patterns[activity_frame] = gating

    def get_gating(self, activity_frame: str) -> AttentionGating:
        """Retrieve gating pattern; default to uniform if not found."""
        if activity_frame in self.gating_patterns:
            return self.gating_patterns[activity_frame]
        # Default: all constraints equally weighted
        return AttentionGating(
            activity_frame=activity_frame,
            attention_weights={c: 1.0 for c in [
                'processing_cost', 'load_rate', 'prediction_error', 'control_efficacy',
                'affordance_density', 'social_cue_density', 'multisensory_coherence',
                'narrative_coherence'
            ]}
        )
```

---

### 1.2 Constraint Recognition Validation Protocol

#### Measurement & Calibration (Scherer requirement)

**File**: `src/services/cva_constraint_validation.py` (NEW, ~250 lines)

Per Scherer's appraisal framework, validate that constraint recognition correlates with behavioral response. Use gaze-contingent paradigms:

```python
from dataclasses import dataclass
from typing import List
import numpy as np

@dataclass
class GazeContingentTrial:
    """
    Empirical validation trial: present stimulus, measure gaze distribution,
    ask subject to rate constraint, measure constraint-gaze correlation.
    """
    stimulus_id: str
    gaze_regions: List[tuple]          # List of (x, y, duration_ms) gaze samples
    constraint_ratings: dict           # {constraint_name: human_rating [0-10]}
    recognized_constraints: dict       # {constraint_name: model_p_recognized [0,1]}
    condition: str                     # 'BASELINE', 'HIGH_PROCESSING_COST', etc.
    subject_psi: dict                  # Subject characteristics {neuro, culture, ...}

class ConstraintValidationAnalysis:
    """
    Validate constraint recognition model using:
    1. Constraint-gaze correlation: Pearson r(attention_to_regions, constraint_recognition)
    2. Constraint-rating correlation: Correlation between model recognition and human ratings
    3. Temporal precedence: Does ε_attn (attention shift) precede constraint-recognition change?
    """

    def compute_constraint_gaze_correlation(self, trials: List[GazeContingentTrial],
                                           constraint_name: str) -> float:
        """
        Compute Pearson correlation between gaze distribution and constraint recognition.

        Hypothesis: High ProcessingCost constraint recognition should correlate with
        gaze spread (looking at many regions) or gaze fixation (high variance in gaze location).

        Returns:
            r ∈ [-1, 1]: Pearson correlation coefficient
            Target: r ≥ 0.6 per Scherer's appraisal validation standards
        """
        pass

    def compute_constraint_rating_correlation(self, trials: List[GazeContingentTrial],
                                             constraint_name: str) -> float:
        """
        Compute Pearson correlation between model p(c|x,A,ψ) and human constraint ratings.

        Returns:
            r: correlation coefficient
            Target: r ≥ 0.75 per specification
        """
        pass

    def compute_temporal_precedence(self, trials: List[GazeContingentTrial]) -> dict:
        """
        Temporal analysis: ε_attn (gaze shift) should precede constraint-recognition change.

        Methodology:
        1. Detect gaze shift events (rapid change in fixation location)
        2. Detect constraint-recognition changes (from frame t-1 to t)
        3. Measure lag: does gaze shift occur 0.2-0.3s before recognition change?

        Returns:
            {'mean_lag_ms': float, 'confidence': float, 'n_events': int}
            Target: mean_lag in [200, 300]ms range
        """
        pass
```

---

### 1.3 Two-Tier Constraint Implementation

The Tier 1 → Tier 2 transformation is the core of CVA-1-REV.

**File**: `src/services/cva_tier_transformation.py` (NEW, ~350 lines)

```python
from typing import Callable, Optional
import numpy as np
from src.models.subject_characteristics import SubjectCharacteristics
from src.models.cva_constraint_recognition import Tier1ConstraintVector, Tier2ConstraintVector

class TierTransformation:
    """
    Maps Tier 1 (universal primitives) → Tier 2 (ψ-calibrated interpretations).

    Key mechanism: Each Tier 2 constraint is derived from a subset of Tier 1 primitives,
    weighted by ψ parameters.

    Example:
    ProcessingCost (Tier 2) = w₀ * edge_detection + w₁ * luminance_contrast
                            + w₂ * symmetry_detection + ...
    where w_i depend on ψ_neuro, ψ_culture, ψ_dev_age
    """

    def __init__(self):
        self.transformation_matrix: Optional[np.ndarray] = None
        self.psi_parameter_functions: dict = {}

    def register_psi_function(self, constraint_name: str,
                             fn: Callable[[dict], np.ndarray]) -> None:
        """
        Register a function that computes Tier 1 weights given ψ.

        Args:
            constraint_name: e.g., 'processing_cost'
            fn: Function(psi_dict) -> weights [6], where weights are Tier 1 coefficients

        Example:
            def processing_cost_weights(psi_dict):
                # ADHD individuals are more sensitive to visual complexity
                neuro_factor = 1.2 if psi_dict['neuro'] == 'ADHD' else 1.0

                # Older adults process slower
                age = psi_dict['dev_age']
                age_factor = 1.0 + 0.01 * (age - 25)  # 1% increase per year after 25

                # Base weights: [edge, motion, figure_ground, luminance, temporal, symmetry]
                base_weights = np.array([0.3, 0.1, 0.25, 0.2, 0.1, 0.05])

                return base_weights * neuro_factor * age_factor
        """
        self.psi_parameter_functions[constraint_name] = fn

    def transform(self, tier1: Tier1ConstraintVector,
                 psi: SubjectCharacteristics) -> Tier2ConstraintVector:
        """
        Transform Tier 1 → Tier 2 using ψ-dependent weights.

        Args:
            tier1: Universal constraint primitives
            psi: Subject characteristics (culture, neurotype, age, etc.)

        Returns:
            Tier2ConstraintVector with posterior means and uncertainty bounds.

        Pseudocode:
            1. Extract psi_dict from SubjectCharacteristics
            2. For each of 8 constraints:
                a. Compute weights w_i = psi_function_i(psi_dict)
                b. Compute tier2_value = dot(w_i, tier1_vector)
                c. Compute uncertainty via Bayesian model averaging or dropout
            3. Return Tier2ConstraintVector
        """

        tier1_vec = tier1.as_vector()
        psi_dict = psi.to_dict()

        tier2_values = []
        uncertainty_bounds = {}

        constraint_names = [
            'processing_cost', 'load_rate', 'prediction_error', 'control_efficacy',
            'affordance_density', 'social_cue_density', 'multisensory_coherence',
            'narrative_coherence'
        ]

        for constraint_name in constraint_names:
            if constraint_name not in self.psi_parameter_functions:
                raise ValueError(f"No transformation registered for {constraint_name}")

            # Get ψ-dependent weights for this constraint
            weights = self.psi_parameter_functions[constraint_name](psi_dict)

            # Compute posterior mean
            posterior_mean = np.dot(weights, tier1_vec)
            posterior_mean = np.clip(posterior_mean, 0, 1)

            # Estimate uncertainty (placeholder: assume 10% margin)
            uncertainty = 0.1
            uncertainty_bounds[constraint_name] = (
                np.clip(posterior_mean - uncertainty, 0, 1),
                np.clip(posterior_mean + uncertainty, 0, 1)
            )

            tier2_values.append(posterior_mean)

        return Tier2ConstraintVector(
            processing_cost=tier2_values[0],
            load_rate=tier2_values[1],
            prediction_error=tier2_values[2],
            control_efficacy=tier2_values[3],
            affordance_density=tier2_values[4],
            social_cue_density=tier2_values[5],
            multisensory_coherence=tier2_values[6],
            narrative_coherence=tier2_values[7],
            psi_culture=psi.cultural_context.name if psi.cultural_context else 'UNKNOWN',
            psi_neuro=psi.neurotype_profile.name if psi.neurotype_profile else 'TYPICAL',
            psi_dev_age=psi.developmental_stage.age_years if psi.developmental_stage else 25.0,
            uncertainty_bounds=uncertainty_bounds
        )

class PopulationTransferFactor:
    """
    Compute δ(ψ_source, ψ_target): discount factor for transferring constraints
    from one population to another (used in ATLAS integration).

    Formula: δ = exp(-λ * d_ψ(source, target))
    where d_ψ is Euclidean distance in ψ-space, λ ~ 0.5-1.0.
    """

    @staticmethod
    def compute_delta(psi_source: SubjectCharacteristics,
                     psi_target: SubjectCharacteristics,
                     lambda_decay: float = 0.75) -> float:
        """
        Compute population transfer factor.

        Args:
            psi_source: Source population characteristics
            psi_target: Target population characteristics
            lambda_decay: Decay rate (higher = faster decay with distance)

        Returns:
            δ ∈ (0, 1]: discount factor
                δ=1.0: identical populations
                δ=0.5: moderately different populations
                δ<0.1: very different populations (low transferability)
        """

        # Compute distance in ψ-space
        # This requires a metric on the ψ-manifold
        # Placeholder: use Euclidean distance in normalized coordinates

        psi_source_vec = psi_source.to_normalized_vector()  # Stub: implement in SubjectCharacteristics
        psi_target_vec = psi_target.to_normalized_vector()

        d_psi = np.linalg.norm(psi_source_vec - psi_target_vec)

        delta = np.exp(-lambda_decay * d_psi)
        return delta
```

---

### 1.4 CVA-1-REV Deliverables

| Deliverable | File | LOC | Purpose |
|------------|------|-----|---------|
| Tier 1/2 data structures | `src/models/cva_constraint_recognition.py` | 300 | Define Tier 1 (universal) and Tier 2 (ψ-calibrated) constraints |
| Recognition model | `src/services/cva_constraint_attention.py` | 200 | ActivityFrame→constraint attention gating |
| Tier transformation | `src/services/cva_tier_transformation.py` | 350 | Tier 1→Tier 2 mapping with ψ parameters; population transfer δ |
| Validation protocol | `src/services/cva_constraint_validation.py` | 250 | Empirical validation: gaze-contingent paradigms, Scherer's framework |
| Tests | `tests/test_cva_constraint_recognition.py` | 250 | Comprehensive unit + integration tests |
| Documentation | `docs/CVA_CONSTRAINT_RECOGNITION_PROTOCOL_2026-02-28.md` | 500 | Detailed measurement protocols, neurotype sensitivity tables, examples |

**Total LOC**: ~1,850 | **Test Coverage**: ≥90%

---

### 1.5 CVA-1-REV Test Acceptance Criteria

```
✓ All 213 original ATLAS tests pass
✓ Tier 1 vectors validate correctly (6-dimensional, [0,1] range)
✓ Tier 2 vectors validate correctly (8-dimensional, [0,1] range)
✓ ψ-parameterized transformation works for all 10 neurotypes
✓ ActivityFrame gating modulates constraint recognition (ω ∈ [0,1])
✓ Population transfer factor δ ∈ (0, 1] with expected decay behavior
✓ Constraint-gaze correlation r ≥ 0.6 (Scherer appraisal validation)
✓ Constraint-rating correlation r ≥ 0.75 (human agreement)
✓ Temporal precedence: gaze shift precedes recognition change by 200-300ms
✓ No regression in ATLAS overseer invariants (INV-1 through INV-9)
```

---

---

## PART 2: CVA-2-REV REVISED SPECIFICATION

### Scope: Two-Tier Valuations + Decomposed Feedback + Rasa Attractors

**Duration**: 3 weeks | **Effort**: 24 person-days | **Dependencies**: CVA-1-REV complete

---

### 2.1 Two-Tier Valuation Architecture (Core + Auxiliary)

#### Overview

Chat's Q1 solution: Separate stable universal core (v_core) from sparse context-activated auxiliary (v_aux).

**Key insight**: All cultures recognize v_core; structural variation happens in v_aux.

#### Data Structures

**File**: `src/models/cva_valuation_two_tier.py` (NEW, ~400 lines)

```python
from dataclasses import dataclass, field
from typing import Optional, List, dict as Dict
from enum import Enum
import numpy as np

class ValuationAxis(Enum):
    """Nine universal core valuation axes."""
    SAFETY_VALUE = "safety_value"
    INTEREST_VALUE = "interest_value"
    RESTORATION_VALUE = "restoration_value"
    STATUS_VALUE = "status_value"
    BELONGING_VALUE = "belonging_value"
    IDENTITY_CONGRUENCE_VALUE = "identity_congruence_value"
    AUTONOMY_SUPPORT_VALUE = "autonomy_support_value"
    COMPETENCE_SUPPORT_VALUE = "competence_support_value"
    RELATEDNESS_SUPPORT_VALUE = "relatedness_support_value"

class AuxiliaryValuationAxis(Enum):
    """Context-specific auxiliary axes (culture + activity-dependent)."""
    SACREDNESS_VALUE = "sacredness_value"
    RITUAL_FIT_VALUE = "ritual_fit_value"
    MARKET_VALUE = "market_value"
    ECOLOGICAL_COHERENCE = "ecological_coherence"
    TRADITION_ADHERENCE = "tradition_adherence"

@dataclass
class CoreValuationVector:
    """
    Stable core: 9 universal valuation dimensions.
    These are present in all humans; their salience is culturally modulated via π(A, ψ).

    Normalized to [0, 1]. Represent posterior means of cultural-universal value dimensions.
    """
    safety_value: float                     # Preference for predictability, safety
    interest_value: float                   # Preference for information, learning
    restoration_value: float                # Preference for restorative calm
    status_value: float                     # Preference for status congruence
    belonging_value: float                  # Preference for community, group membership
    identity_congruence_value: float        # Preference for self-consistency
    autonomy_support_value: float           # Preference for volition, self-determination
    competence_support_value: float         # Preference for challenge, mastery
    relatedness_support_value: float        # Preference for connection, intimacy

    tier: int = 1
    timestamp_created: str = ""

    def validate(self) -> bool:
        """Ensure all axes in [0, 1]."""
        for val in [self.safety_value, self.interest_value, self.restoration_value,
                   self.status_value, self.belonging_value, self.identity_congruence_value,
                   self.autonomy_support_value, self.competence_support_value,
                   self.relatedness_support_value]:
            if not (0 <= val <= 1):
                return False
        return True

    def as_vector(self) -> np.ndarray:
        """Return as numpy array [9]."""
        return np.array([
            self.safety_value, self.interest_value, self.restoration_value,
            self.status_value, self.belonging_value, self.identity_congruence_value,
            self.autonomy_support_value, self.competence_support_value,
            self.relatedness_support_value
        ])

@dataclass
class AuxiliaryValuationSet:
    """
    Context-activated auxiliary valuations (activity frame + culture dependent).

    Example: In WORSHIPPING frame with INDIAN culture, activate SacrednessValue + RitualFitValue.
    In SHOPPING frame with WESTERN culture, activate MarketValueEstimate.

    Sparse by design: most contexts activate 0-2 auxiliary axes.
    """
    sacredness_value: float = 0.0           # Default: inactive
    ritual_fit_value: float = 0.0
    market_value: float = 0.0
    ecological_coherence: float = 0.0
    tradition_adherence: float = 0.0

    # Allow arbitrary auxiliary dimensions
    custom_auxiliaries: Dict[str, float] = field(default_factory=dict)

    def validate(self) -> bool:
        """Ensure all values in [0, 1]."""
        for val in [self.sacredness_value, self.ritual_fit_value, self.market_value,
                   self.ecological_coherence, self.tradition_adherence]:
            if not (0 <= val <= 1):
                return False
        for val in self.custom_auxiliaries.values():
            if not (0 <= val <= 1):
                return False
        return True

    def active_axes(self) -> List[str]:
        """Return names of active auxiliary axes (value > 0.05 threshold)."""
        active = []
        threshold = 0.05
        if self.sacredness_value > threshold:
            active.append('sacredness_value')
        if self.ritual_fit_value > threshold:
            active.append('ritual_fit_value')
        if self.market_value > threshold:
            active.append('market_value')
        if self.ecological_coherence > threshold:
            active.append('ecological_coherence')
        if self.tradition_adherence > threshold:
            active.append('tradition_adherence')
        for name, val in self.custom_auxiliaries.items():
            if val > threshold:
                active.append(name)
        return active

    def as_vector(self) -> np.ndarray:
        """Return active auxiliaries as numpy array [≤5]."""
        active = self.active_axes()
        values = [self.get_axis_value(ax) for ax in active]
        return np.array(values) if values else np.array([])

    def get_axis_value(self, axis_name: str) -> float:
        """Get value of named auxiliary axis."""
        if axis_name == 'sacredness_value':
            return self.sacredness_value
        elif axis_name == 'ritual_fit_value':
            return self.ritual_fit_value
        elif axis_name == 'market_value':
            return self.market_value
        elif axis_name == 'ecological_coherence':
            return self.ecological_coherence
        elif axis_name == 'tradition_adherence':
            return self.tradition_adherence
        elif axis_name in self.custom_auxiliaries:
            return self.custom_auxiliaries[axis_name]
        else:
            return 0.0

@dataclass
class CompleteValuationVector:
    """
    Complete valuation state: v = (v_core, v_aux(A, ψ)).

    The core is always present (though some axes may be near-zero in some individuals);
    auxiliary is sparse and frame/culture-dependent.
    """
    core: CoreValuationVector
    auxiliary: AuxiliaryValuationSet
    activity_frame: Optional[str] = None    # Which frame activated these auxiliaries
    psi_culture: Optional[str] = None       # Cultural context
    psi_neuro: Optional[str] = None         # Neurotype
    psi_dev_age: Optional[float] = None     # Age

    def validate(self) -> bool:
        """Both core and auxiliary must validate."""
        return self.core.validate() and self.auxiliary.validate()

    def as_vector(self, include_auxiliary: bool = True) -> np.ndarray:
        """
        Return as combined vector.

        If include_auxiliary=False: return only core [9]
        If include_auxiliary=True: return [core (9), active_auxiliaries (≤5)]
        """
        core_vec = self.core.as_vector()
        if not include_auxiliary:
            return core_vec

        aux_vec = self.auxiliary.as_vector()
        if len(aux_vec) == 0:
            return core_vec

        # Pad to fixed dimension or return variable-dimension vector
        # For now: concatenate (variable dimension)
        return np.concatenate([core_vec, aux_vec])

    def dimensionality(self, include_auxiliary: bool = True) -> int:
        """Return vector dimensionality."""
        if not include_auxiliary:
            return 9
        return 9 + len(self.auxiliary.active_axes())
```

---

### 2.2 Cultural Valuation Variants

Different cultures have different valuation structures. This is not just weight rebalancing; it's structural decomposition.

**File**: `src/models/cva_cultural_variants.py` (NEW, ~500 lines)

```python
from dataclasses import dataclass
from typing import Optional, Callable
import numpy as np
from enum import Enum

class CulturalValuationVariant(Enum):
    """Supported cultural valuation structures."""
    WESTERN = "western"                 # 9-dimensional orthogonal
    JAPANESE = "japanese"               # Amae replaces autonomy; Ma added
    WEST_AFRICAN = "west_african"       # Àṣà collapses 4 axes
    INDIAN = "indian"                   # Rasa-based (not decomposable into axes)

@dataclass
class WesternValuationStructure:
    """
    Western cultural variant: 9-dimensional independent axes.
    All axes co-present; weights vary by individual.
    Basis: SDT (Deci), Barrett (dimensional emotion), Western individuality.
    """

    @staticmethod
    def get_core_axes() -> list:
        return [
            'safety_value', 'interest_value', 'restoration_value',
            'status_value', 'belonging_value', 'identity_congruence_value',
            'autonomy_support_value', 'competence_support_value',
            'relatedness_support_value'
        ]

    @staticmethod
    def get_auxiliary_axes_for_frame(activity_frame: str) -> dict:
        """Activity-dependent auxiliary axes for Western culture."""
        auxiliary_map = {
            'STUDYING': {'market_value': 0.3, 'ecological_coherence': 0.1},
            'WORKING': {'market_value': 0.5, 'status_value': 0.2},
            'WORSHIPPING': {'sacredness_value': 0.4, 'ritual_fit_value': 0.3},
            'CREATING': {'aesthetic_value': 0.6},
            'HEALING': {'restoration_value': 0.7, 'sacredness_value': 0.2},
            'PLAYING': {'novelty_value': 0.5},
            'SOCIALIZING': {'belonging_value': 0.6, 'relatedness_support_value': 0.5},
            'NEGOTIATING': {'status_value': 0.4, 'autonomy_support_value': 0.3},
            'EXPLORING': {'interest_value': 0.7, 'novelty_value': 0.6},
            'RESTING': {'restoration_value': 0.8, 'safety_value': 0.6}
        }
        return auxiliary_map.get(activity_frame, {})

    @staticmethod
    def interaction_matrix() -> np.ndarray:
        """
        9×9 interaction matrix: K_vv for Western culture.
        Diagonal: self-inhibition (negative values)
        Off-diagonal: cross-inhibition (negative) or support (positive)

        Specification (to be reviewed by Deci, Kitayama):
        - Autonomy × Relatedness: slightly negative (tension: autonomy vs. embeddedness)
        - Competence × Interest: positive (challenge + learning align)
        - Belonging × Status: mildly positive (status within group matters)
        """
        K_vv = np.array([
            # Rows: [safety, interest, restoration, status, belonging, identity, autonomy, competence, relatedness]
            [-0.4,  0.1,   0.2,  -0.05,  0.15, -0.1,  0.05,  0.05,   0.1],      # safety
            [ 0.1, -0.3,   0.0,   0.05,  0.0,  -0.15, 0.1,   0.3,   -0.1],      # interest
            [ 0.2,  0.0,  -0.4,  -0.1,   0.15, 0.0,   -0.2,  0.0,    0.15],    # restoration
            [-0.05, 0.05, -0.1,  -0.3,   0.2,  0.25,  -0.15, 0.1,    0.0],     # status
            [ 0.15, 0.0,   0.15,  0.2,  -0.35, 0.0,   -0.1,  0.0,    0.3],     # belonging
            [-0.1, -0.15,  0.0,   0.25,  0.0, -0.3,   0.0,   0.1,   -0.05],    # identity
            [ 0.05, 0.1,  -0.2,  -0.15, -0.1,  0.0,   -0.25, 0.0,   -0.2],     # autonomy
            [ 0.05, 0.3,   0.0,   0.1,   0.0,  0.1,    0.0,  -0.3,    0.1],    # competence
            [ 0.1, -0.1,   0.15,  0.0,   0.3, -0.05,  -0.2,   0.1,   -0.3]     # relatedness
        ])
        return K_vv

@dataclass
class JapaneseValuationStructure:
    """
    Japanese cultural variant: Amae (dependent trust) replaces autonomy;
    Ma (space/emptiness) is added.

    Basis: Kitayama research, Japanese aesthetics, relational independence.
    """

    @staticmethod
    def get_core_axes() -> list:
        return [
            'safety_value', 'interest_value', 'restoration_value',
            'status_value', 'belonging_value', 'identity_congruence_value',
            'amae_value',  # Replaces autonomy_support_value
            'competence_support_value',
            'relatedness_support_value'
        ]

    @staticmethod
    def get_auxiliary_axes_for_frame(activity_frame: str) -> dict:
        """Japanese-specific auxiliary axes."""
        auxiliary_map = {
            'STUDYING': {'ma_value': 0.4},  # Emptiness, breathing room
            'WORKING': {'harmony_value': 0.5, 'group_efficacy': 0.3},
            'WORSHIPPING': {'sacredness_value': 0.5, 'ritual_fit_value': 0.6, 'ma_value': 0.3},
            'CREATING': {'ma_value': 0.6, 'aesthetic_value': 0.5},
            'HEALING': {'ma_value': 0.7, 'harmony_value': 0.4},
            'PLAYING': {'playfulness_value': 0.6},
            'SOCIALIZING': {'harmony_value': 0.6, 'amae_value': 0.5},
            'NEGOTIATING': {'harmony_value': 0.4, 'group_status': 0.3},
            'EXPLORING': {'interest_value': 0.6, 'ma_value': 0.3},
            'RESTING': {'ma_value': 0.8, 'restoration_value': 0.7}
        }
        return auxiliary_map.get(activity_frame, {})

    @staticmethod
    def interaction_matrix() -> np.ndarray:
        """9×9 interaction matrix for Japanese culture."""
        # Amae (dependent trust) is strongly coupled with Relatedness
        # Ma (emptiness) modulates all aesthetic experience
        K_vv = np.array([
            [-0.4,  0.1,   0.2,  -0.05,  0.15, -0.1,  0.2,  0.05,   0.1],      # safety
            [ 0.1, -0.3,   0.0,   0.05,  0.0,  -0.15, 0.15, 0.25,  -0.1],      # interest
            [ 0.2,  0.0,  -0.4,  -0.1,   0.2,  0.0,   0.0,  0.0,    0.2],      # restoration
            [-0.05, 0.05, -0.1,  -0.3,   0.15, 0.2,  -0.2,  0.1,    0.05],    # status
            [ 0.15, 0.0,   0.2,   0.15, -0.35, 0.0,   0.3,  0.0,    0.4],     # belonging
            [-0.1, -0.15,  0.0,   0.2,   0.0, -0.3,   0.1,  0.1,   -0.05],    # identity
            [ 0.2,  0.15,  0.0,  -0.2,   0.3,  0.1,  -0.3,  0.0,    0.35],    # amae (high coupling with relatedness)
            [ 0.05, 0.25,  0.0,   0.1,   0.0,  0.1,   0.0,  -0.3,   0.15],    # competence
            [ 0.1, -0.1,   0.2,   0.05,  0.4, -0.05,  0.35,  0.15,  -0.3]     # relatedness
        ])
        return K_vv

@dataclass
class WestAfricanValuationStructure:
    """
    West African cultural variant: Àṣà (aesthetic-social coherence) collapses
    Status + Belonging + Identity + Relatedness into single holistic dimension.

    Basis: Barrett's work on culture-specific emotion structures, Gbadegesin.
    """

    @staticmethod
    def get_core_axes() -> list:
        return [
            'safety_value', 'interest_value', 'restoration_value',
            'asha_value',  # Collapses status, belonging, identity, relatedness
            'autonomy_support_value',
            'competence_support_value',
            'embodied_balance'  # Added: physical/social harmony
        ]

    @staticmethod
    def get_auxiliary_axes_for_frame(activity_frame: str) -> dict:
        """West African cultural auxiliary axes."""
        auxiliary_map = {
            'STUDYING': {'community_learning': 0.4, 'elder_respect': 0.3},
            'WORKING': {'collective_efficacy': 0.6, 'asha_value': 0.4},
            'WORSHIPPING': {'spiritual_connection': 0.7, 'ancestral_alignment': 0.5},
            'CREATING': {'cultural_continuity': 0.5, 'community_resonance': 0.4},
            'HEALING': {'communal_healing': 0.6, 'spiritual_connection': 0.4},
            'PLAYING': {'playfulness_value': 0.5, 'group_joy': 0.6},
            'SOCIALIZING': {'asha_value': 0.8, 'community_belonging': 0.7},
            'NEGOTIATING': {'consensus_seeking': 0.5, 'elder_wisdom': 0.3},
            'EXPLORING': {'cultural_discovery': 0.4, 'interest_value': 0.5},
            'RESTING': {'embodied_balance': 0.7, 'restoration_value': 0.6}
        }
        return auxiliary_map.get(activity_frame, {})

    @staticmethod
    def interaction_matrix() -> np.ndarray:
        """7×7 interaction matrix (Àṣà collapses 4 dimensions to 1)."""
        K_vv = np.array([
            [-0.4,  0.1,   0.2,   0.15,  0.05,  0.05,   0.1],      # safety
            [ 0.1, -0.3,   0.0,   0.0,   0.15,  0.25,  -0.1],      # interest
            [ 0.2,  0.0,  -0.4,   0.2,   -0.2,  0.0,    0.2],      # restoration
            [ 0.15, 0.0,   0.2,  -0.35,  0.0,   0.1,    0.3],      # asha (high connectivity)
            [ 0.05, 0.15, -0.2,   0.0,  -0.25,  0.0,   -0.15],     # autonomy
            [ 0.05, 0.25,  0.0,   0.1,   0.0,  -0.3,    0.2],      # competence
            [ 0.1, -0.1,   0.2,   0.3,  -0.15,  0.2,   -0.3]       # embodied_balance
        ])
        return K_vv

@dataclass
class IndianValuationStructure:
    """
    Indian cultural variant: Rasa-based (holistic, not decomposable into axes).

    Instead of 9 independent axes, Indian valuation is structured as stable attractors
    (rasa states). The 9 rasas (Raudra, Veera, Pathetika, etc.) are holistic states.

    This is formalized in RASA_AS_ATTRACTORS_CVA_DYNAMICS.
    """

    @staticmethod
    def get_core_axes() -> list:
        """
        Return names of the 9 rasas as "axes" (though they are not independent).
        This is a convention for compatibility with 9D system.
        """
        return [
            'rasa_shanta',      # Tranquility
            'rasa_raudra',      # Fury
            'rasa_veera',       # Heroism
            'rasa_pathetika',   # Pathetic/compassion
            'rasa_karuna',      # Tender compassion
            'rasa_sringara',    # Romantic love
            'rasa_hasya',       # Mirth
            'rasa_bibhatsa',    # Disgust/horror
            'rasa_adbhuta'      # Wonder/amazement
        ]

    @staticmethod
    def get_auxiliary_axes_for_frame(activity_frame: str) -> dict:
        """Indian-specific auxiliary axes."""
        auxiliary_map = {
            'STUDYING': {'dharma_alignment': 0.5, 'knowledge_sacredness': 0.4},
            'WORKING': {'karma_fulfillment': 0.6, 'duty_alignment': 0.4},
            'WORSHIPPING': {'spiritual_transcendence': 0.8, 'mantra_resonance': 0.5},
            'CREATING': {'artistic_rasa': 0.7, 'lineage_continuation': 0.3},
            'HEALING': {'ayurvedic_balance': 0.5, 'doshas_harmony': 0.4},
            'PLAYING': {'lila_value': 0.6, 'playfulness_value': 0.5},
            'SOCIALIZING': {'rasa_sringara_aux': 0.5, 'community_dharma': 0.4},
            'NEGOTIATING': {'satya_alignment': 0.5, 'dharma_consensus': 0.3},
            'EXPLORING': {'pilgrimage_value': 0.4, 'discovery_sacredness': 0.3},
            'RESTING': {'brahman_connection': 0.6, 'restoration_value': 0.7}
        }
        return auxiliary_map.get(activity_frame, {})

    @staticmethod
    def interaction_matrix() -> np.ndarray:
        """
        9×9 interaction matrix for rasa attractors.
        Unlike Western, these represent basilar (base) rasa compatibility.
        """
        K_vv = np.array([
            # Rows/cols: [shanta, raudra, veera, pathetika, karuna, sringara, hasya, bibhatsa, adbhuta]
            [-0.5,  -0.6, -0.3,  -0.2,  -0.1,  -0.4, -0.4, -0.7, -0.2],      # shanta
            [-0.6,  -0.5,  0.2,  -0.5,  -0.5,  -0.8, -0.7, -0.3,  0.1],      # raudra
            [-0.3,   0.2, -0.4,  -0.1,  -0.2,  -0.5, -0.6,  0.0,  0.15],     # veera
            [-0.2,  -0.5, -0.1,  -0.4,   0.3,  -0.3, -0.5, -0.2,  0.0],      # pathetika
            [-0.1,  -0.5, -0.2,   0.3,  -0.4,  -0.2, -0.3, -0.3,  0.1],      # karuna
            [-0.4,  -0.8, -0.5,  -0.3,  -0.2,  -0.3, -0.1, -0.8,  0.0],      # sringara
            [-0.4,  -0.7, -0.6,  -0.5,  -0.3,  -0.1, -0.4, -0.6,  0.2],      # hasya
            [-0.7,  -0.3,  0.0,  -0.2,  -0.3,  -0.8, -0.6, -0.5, -0.4],      # bibhatsa
            [-0.2,   0.1,  0.15,  0.0,   0.1,   0.0,  0.2, -0.4, -0.3]       # adbhuta
        ])
        return K_vv

class ValuationStructureFactory:
    """Factory to create culturally appropriate valuation structures."""

    @staticmethod
    def create(variant: CulturalValuationVariant) -> object:
        """Create valuation structure instance."""
        if variant == CulturalValuationVariant.WESTERN:
            return WesternValuationStructure()
        elif variant == CulturalValuationVariant.JAPANESE:
            return JapaneseValuationStructure()
        elif variant == CulturalValuationVariant.WEST_AFRICAN:
            return WestAfricanValuationStructure()
        elif variant == CulturalValuationVariant.INDIAN:
            return IndianValuationStructure()
        else:
            raise ValueError(f"Unknown variant: {variant}")

    @staticmethod
    def interaction_matrix(variant: CulturalValuationVariant) -> np.ndarray:
        """Get interaction matrix K_vv for culture."""
        factory = ValuationStructureFactory.create(variant)
        return factory.interaction_matrix()
```

---

### 2.3 Decomposed Feedback: Three Error Signals

Chat's Q3 solution: Replace monolithic valuation error with three mechanistically distinct signals.

**File**: `src/services/cva_decomposed_feedback.py` (NEW, ~400 lines)

```python
from dataclasses import dataclass
from typing import Optional, Callable
import numpy as np

@dataclass
class DecomposedFeedbackSignals:
    """
    Three independent feedback pathways driving constraint and valuation changes.
    Each signal has distinct neural mechanism, timescale, and function.
    """

    epsilon_attn: float                 # Attentional error: ∈ [-1, 1]
    epsilon_prec: float                 # Precision error: ∈ [0, 1] (gain modulation)
    epsilon_prior: float                # Prior-expectation error: ∈ [-1, 1]

    timestamp_created: str = ""
    source_description: str = ""        # For debugging: where did this come from?

    def validate(self) -> bool:
        """Ensure all signals in expected ranges."""
        return (-1 <= self.epsilon_attn <= 1) and \
               (0 <= self.epsilon_prec <= 1) and \
               (-1 <= self.epsilon_prior <= 1)

class AttentionalErrorSignal:
    """
    ε_attn: Attentional error, drives gaze shifts and constraint attention allocation.

    Mechanism: Dorsal frontoparietal gating of saccades (Corbetta & Shulman).
    Computation: Prediction error between expected and actual salient region.

    If ε_attn > 0: should have attended to high-value region but didn't → shift attention there
    If ε_attn < 0: attended to low-value region unnecessarily → shift attention away
    Timescale: 300-500ms (eye movement latency)
    """

    def __init__(self, saliency_model: Callable):
        """
        Args:
            saliency_model: Function(constraint_vector, activity_frame) -> saliency_map [H, W]
                           Predicts which regions are informative for current context
        """
        self.saliency_model = saliency_model

    def compute(self,
               constraint_vector: np.ndarray,       # Current constraint state [8]
               activity_frame: str,                # Current activity
               gaze_location: tuple,                # (x, y) of current gaze
               stimulus_shape: tuple) -> float:    # (height, width) of visual field
        """
        Compute attentional error: how informative is current gaze location?

        Args:
            constraint_vector: [8] constraint values
            activity_frame: ActivityFrame identifier
            gaze_location: (x, y) current gaze fixation
            stimulus_shape: (H, W) visual field size

        Returns:
            ε_attn ∈ [-1, 1]:
            > 0: should shift attention toward more informative regions
            < 0: current attention is excessive
            ≈ 0: attention allocation is optimal
        """

        # Generate expected saliency map for this constraint state + frame
        saliency = self.saliency_model(constraint_vector, activity_frame)

        # Extract saliency at current gaze location
        gx, gy = gaze_location
        gx = np.clip(int(gx), 0, stimulus_shape[1] - 1)
        gy = np.clip(int(gy), 0, stimulus_shape[0] - 1)
        saliency_at_gaze = saliency[gy, gx]

        # Compute max saliency in entire field (best possible attention)
        max_saliency = np.max(saliency)

        # ε_attn = (best - current) / best, rescaled to [-1, 1]
        if max_saliency > 0:
            epsilon_attn = (max_saliency - saliency_at_gaze) / max_saliency
            epsilon_attn = 2 * epsilon_attn - 1  # Rescale to [-1, 1]
        else:
            epsilon_attn = 0.0

        return np.clip(epsilon_attn, -1, 1)

class PrecisionErrorSignal:
    """
    ε_prec: Precision error, scales gain on valuation responses (contrast gain modulation).

    Mechanism: V1/V2 contrast gain modulation (Kohn & Movshon), state-dependent
    weighting of constraint influence on valuation.
    Computation: Variability in constraint observations relative to expected variability.

    Formula: ε_prec = [observed_variance - expected_variance] / expected_variance
    Rescaled to [0, 1]: higher → increase gain on sensory input
    Timescale: 500-2000ms (cortical integration)
    """

    def __init__(self, precision_model: Callable):
        """
        Args:
            precision_model: Function(activity_frame, psi) -> expected_std_dev [8]
                           Predicts typical variability in constraint observations
        """
        self.precision_model = precision_model

    def compute(self,
               constraint_history: list,           # List of past constraint_vector [Nx8]
               activity_frame: str,
               psi_dict: dict) -> float:
        """
        Compute precision error: how variable are constraints in this context?

        Args:
            constraint_history: List of Tier2ConstraintVector or [8] arrays from recent history
            activity_frame: Current activity
            psi_dict: Subject characteristics

        Returns:
            ε_prec ∈ [0, 1]:
            → 1.0: constraints highly variable, increase gain to detect changes
            → 0.0: constraints stable, reduce gain (risk of over-sensitivity)
            → 0.5: typical variability
        """

        if len(constraint_history) < 2:
            return 0.5  # Default if insufficient history

        # Convert history to numpy array if needed
        constraint_array = np.array(constraint_history)  # [N, 8]

        # Compute observed standard deviation across time for each constraint
        observed_std = np.std(constraint_array, axis=0)  # [8]

        # Get expected std from precision model
        expected_std = self.precision_model(activity_frame, psi_dict)  # [8]

        # Compute mean relative error across constraints
        relative_error = np.where(expected_std > 0,
                                 observed_std / expected_std,
                                 np.ones(8))

        # Average and rescale to [0, 1]
        mean_relative_error = np.mean(relative_error)
        epsilon_prec = np.clip(mean_relative_error, 0, 2) / 2.0  # Saturate at 2x expected

        return epsilon_prec

class PriorErrorSignal:
    """
    ε_prior: Prior-expectation error, shifts pre-activation of valuation priors β(A, ψ).

    Mechanism: mPFC-hippocampal prediction error (Rangel, O'Doherty).
    Computation: Deviation of constraint state from prior expectations.

    If ε_prior > 0: constraint state is better than expected → upward prior shift (optimism)
    If ε_prior < 0: constraint state is worse than expected → downward prior shift (pessimism)
    Timescale: 1-5s (slow prefrontal integration)
    """

    def __init__(self, prior_model: Callable):
        """
        Args:
            prior_model: Function(activity_frame, psi) -> prior_constraint_vector [8]
                        Predicts expected constraint state in this context
        """
        self.prior_model = prior_model

    def compute(self,
               constraint_vector: np.ndarray,      # Current constraint state [8]
               activity_frame: str,
               psi_dict: dict,
               valuation_vector: np.ndarray) -> float:  # Current valuation [9]
        """
        Compute prior error: are constraints better or worse than expected?

        Args:
            constraint_vector: [8] current constraint state
            activity_frame: Current activity
            psi_dict: Subject characteristics
            valuation_vector: [9] current valuation (used to weight which constraints matter)

        Returns:
            ε_prior ∈ [-1, 1]:
            > 0: constraints exceeded expectations (positive prediction error)
            < 0: constraints fell short of expectations
            ≈ 0: expectations matched reality
        """

        # Get expected constraint state
        prior_constraint = self.prior_model(activity_frame, psi_dict)  # [8]

        # Compute constraint surprise: (actual - expected)
        constraint_surprise = constraint_vector - prior_constraint  # [8]

        # Weight by valuation importance: which constraints drive this activity's value?
        # Stub: simple weighting (to be refined with learned importance)
        constraint_importance = np.abs(self.compute_constraint_importance(
            activity_frame, psi_dict
        ))  # [8]

        # Weighted average surprise
        weighted_surprise = np.mean(constraint_surprise * constraint_importance)

        # Rescale to [-1, 1]
        epsilon_prior = np.clip(weighted_surprise, -1, 1)

        return epsilon_prior

    @staticmethod
    def compute_constraint_importance(activity_frame: str, psi_dict: dict) -> np.ndarray:
        """Stub: return importance weights for each constraint in this context."""
        # Placeholder implementation
        return np.ones(8) / 8.0

class FeedbackComposer:
    """
    Combines three error signals into unified feedback on valuation dynamics.

    Master equation:
    v̇ = -D_v(v - V̄) + ε_prec * φ_v(K_vv·v + K_vc·c) + β(A, ψ) + Δβ(ε_prior)

    where:
    - First term: dissipation toward target valuation
    - Second term: internal coupling, modulated by precision error
    - Third term: prior pre-activation, shifted by prior error
    """

    def __init__(self):
        self.attn_signal: Optional[AttentionalErrorSignal] = None
        self.prec_signal: Optional[PrecisionErrorSignal] = None
        self.prior_signal: Optional[PriorErrorSignal] = None

    def register_signals(self,
                        attn: AttentionalErrorSignal,
                        prec: PrecisionErrorSignal,
                        prior: PriorErrorSignal) -> None:
        """Register the three error signal computers."""
        self.attn_signal = attn
        self.prec_signal = prec
        self.prior_signal = prior

    def compose(self,
               constraint_vector: np.ndarray,
               constraint_history: list,
               activity_frame: str,
               gaze_location: tuple,
               stimulus_shape: tuple,
               psi_dict: dict,
               valuation_vector: np.ndarray) -> DecomposedFeedbackSignals:
        """
        Compute all three feedback signals from current state.

        Returns:
            DecomposedFeedbackSignals with ε_attn, ε_prec, ε_prior
        """

        if not all([self.attn_signal, self.prec_signal, self.prior_signal]):
            raise ValueError("Not all signals registered. Call register_signals() first.")

        epsilon_attn = self.attn_signal.compute(
            constraint_vector, activity_frame, gaze_location, stimulus_shape
        )

        epsilon_prec = self.prec_signal.compute(
            constraint_history, activity_frame, psi_dict
        )

        epsilon_prior = self.prior_signal.compute(
            constraint_vector, activity_frame, psi_dict, valuation_vector
        )

        return DecomposedFeedbackSignals(
            epsilon_attn=epsilon_attn,
            epsilon_prec=epsilon_prec,
            epsilon_prior=epsilon_prior,
            source_description=f"Activity: {activity_frame}, Attn: {epsilon_attn:.3f}, "
                              f"Prec: {epsilon_prec:.3f}, Prior: {epsilon_prior:.3f}"
        )
```

---

### 2.4 Rasa-Attractor Identification Protocol

**File**: `src/services/cva_rasa_attractors.py` (NEW, ~300 lines)

Per panel requirement (Scherer, Kitayama, Friston), identify stable valuation states (rasa) and characterize basin structure.

```python
from dataclasses import dataclass
from typing import List, Optional
import numpy as np

@dataclass
class RasaAttractor:
    """
    Stable fixed point in valuation dynamics: v* where v̇(v*) ≈ 0.

    Rasa = holistic emotional-aesthetic state (not decomposable into independent axes).
    """

    name: str                               # "Śānta", "Raudra", etc.
    valuation_state: np.ndarray            # v* ∈ ℝ⁹ (or cultural variant dimension)
    stability_measure: float                # Lyapunov exponent: λ_max < 0 for stable
    basin_volume: float                    # Estimated volume of basin of attraction
    culture: str                            # "WESTERN", "INDIAN", etc.
    examples: List[str] = None             # Examples: "deep tranquility in meditation", etc.

    def is_stable(self, threshold: float = -0.01) -> bool:
        """Attractor is stable if Lyapunov exponent < threshold."""
        return self.stability_measure < threshold

class RasaIdentificationProtocol:
    """
    Algorithm to identify rasa attractors from dynamical system specification.

    Steps:
    1. Define valuation dynamics ∈(v, c, A, ψ, κ)
    2. Simulate from random initial conditions → collect fixed points
    3. Characterize stability and basin structure
    4. Validate against empirical rasa identification (Scherer cluster analysis)
    """

    def __init__(self, interaction_matrix: np.ndarray, dissipation_matrix: np.ndarray):
        """
        Args:
            interaction_matrix: K_vv ∈ ℝ⁹×⁹ (culture-specific coupling)
            dissipation_matrix: D_v ∈ ℝ⁹×⁹ (timescale; usually diagonal)
        """
        self.K_vv = interaction_matrix
        self.D_v = dissipation_matrix

    def find_fixed_points(self,
                         constraint_state: np.ndarray,          # c [8]
                         activity_frame: str,
                         psi_dict: dict,
                         kappa_loop: float = 0.038,
                         num_trials: int = 100) -> List[np.ndarray]:
        """
        Find fixed points by iterating dynamics from random initial conditions.

        Args:
            constraint_state: [8] constraint values (held fixed, quasi-stationary)
            activity_frame: Current activity
            psi_dict: Subject characteristics
            kappa_loop: Loop coupling strength
            num_trials: Number of random starting points to try

        Returns:
            List of distinct fixed points (attractors), deduplicated
        """

        fixed_points = []

        for trial in range(num_trials):
            # Random initial condition in [0, 1]^9
            v0 = np.random.uniform(0, 1, 9)

            # Integrate dynamics until convergence
            v = v0
            for step in range(1000):
                v_dot = self.valuation_dynamics(v, constraint_state, activity_frame,
                                               psi_dict, kappa_loop)
                v = v + 0.01 * v_dot  # Euler step
                v = np.clip(v, 0, 1)

            # Check if this is a new fixed point
            if not self.is_duplicate(v, fixed_points, tolerance=0.05):
                fixed_points.append(v)

        return fixed_points

    def valuation_dynamics(self, v: np.ndarray, constraint_state: np.ndarray,
                          activity_frame: str, psi_dict: dict,
                          kappa_loop: float) -> np.ndarray:
        """
        Evaluate v̇(v, c, A, ψ) using master equation.

        v̇ = -D_v(v - Ṽ(c,A)) + φ_v(K_vv·v + K_vc·c)
        """

        # Target valuation function (depends on context)
        v_tilde = self.target_valuation(constraint_state, activity_frame, psi_dict)

        # Coupling term
        coupling = self.compute_coupling(v, constraint_state, kappa_loop)

        # Dynamics: dissipation + coupling
        v_dot = -self.D_v @ (v - v_tilde) + self.activation_function(coupling)

        return v_dot

    def target_valuation(self, constraint_state: np.ndarray,
                        activity_frame: str, psi_dict: dict) -> np.ndarray:
        """
        Compute target valuation Ṽ(c, A, ψ) given constraint state.

        This maps constraints to preferred valuation state.
        Stub: implement based on constraint-valuation mapping (to be learned).
        """
        # Placeholder: high safety constraint → high safety valuation
        v_tilde = constraint_state[:8]  # First 8 constraints map to first 8 valuations
        return np.concatenate([v_tilde, [np.mean(v_tilde)]])  # Pad to 9D

    def compute_coupling(self, v: np.ndarray, constraint_state: np.ndarray,
                        kappa_loop: float) -> np.ndarray:
        """K_vv·v + K_vc·c"""

        # K_vv·v: within-valuation coupling
        vv_coupling = self.K_vv @ v

        # K_vc·c: constraint-to-valuation coupling (simplified: use first 8 constraints)
        # K_vc ∈ ℝ⁹×⁸, typically sparse
        K_vc = np.random.randn(9, 8) * 0.1  # Placeholder
        vc_coupling = K_vc @ constraint_state

        return kappa_loop * (vv_coupling + vc_coupling)

    @staticmethod
    def activation_function(x: np.ndarray) -> np.ndarray:
        """φ_v: rectified linear or sigmoid. Placeholder: ReLU."""
        return np.maximum(x, 0)

    @staticmethod
    def is_duplicate(point: np.ndarray, point_list: List[np.ndarray],
                    tolerance: float = 0.05) -> bool:
        """Check if point is already in list (within tolerance)."""
        for existing in point_list:
            if np.linalg.norm(point - existing) < tolerance:
                return True
        return False

    def characterize_stability(self, fixed_point: np.ndarray,
                              constraint_state: np.ndarray,
                              activity_frame: str,
                              psi_dict: dict) -> float:
        """
        Compute Lyapunov exponent at fixed point via linearization.

        Returns:
            λ_max: largest eigenvalue of Jacobian
            < 0: stable attractor
            = 0: bifurcation point
            > 0: unstable fixed point (saddle)
        """

        # Jacobian = ∂v̇/∂v at fixed point
        eps = 1e-6
        jacobian = np.zeros((9, 9))

        for i in range(9):
            v_plus = fixed_point.copy()
            v_plus[i] += eps
            v_minus = fixed_point.copy()
            v_minus[i] -= eps

            dv_plus = self.valuation_dynamics(v_plus, constraint_state, activity_frame,
                                            psi_dict, kappa_loop=0.038)
            dv_minus = self.valuation_dynamics(v_minus, constraint_state, activity_frame,
                                             psi_dict, kappa_loop=0.038)

            jacobian[:, i] = (dv_plus - dv_minus) / (2 * eps)

        # Largest eigenvalue
        eigenvalues = np.linalg.eigvals(jacobian)
        lambda_max = np.max(np.real(eigenvalues))

        return lambda_max

    def estimate_basin_volume(self, fixed_point: np.ndarray,
                             constraint_state: np.ndarray,
                             activity_frame: str,
                             psi_dict: dict,
                             num_samples: int = 1000) -> float:
        """
        Estimate basin of attraction volume via Monte Carlo.

        Sample random points; count what fraction converge to this fixed point.
        """

        count_converging = 0

        for _ in range(num_samples):
            v0 = np.random.uniform(0, 1, 9)
            v = v0

            # Integrate
            for step in range(500):
                v_dot = self.valuation_dynamics(v, constraint_state, activity_frame,
                                               psi_dict, kappa_loop=0.038)
                v = v + 0.01 * v_dot
                v = np.clip(v, 0, 1)

            # Check if converged to this fixed point
            if np.linalg.norm(v - fixed_point) < 0.1:
                count_converging += 1

        basin_volume = count_converging / num_samples
        return basin_volume
```

---

### 2.5 CVA-2-REV Deliverables

| Deliverable | File | LOC | Purpose |
|------------|------|-----|---------|
| Two-tier valuation | `src/models/cva_valuation_two_tier.py` | 400 | Core + auxiliary decomposition |
| Cultural variants | `src/models/cva_cultural_variants.py` | 500 | Western, Japanese, W. African, Indian structures |
| Decomposed feedback | `src/services/cva_decomposed_feedback.py` | 400 | ε_attn, ε_prec, ε_prior computation |
| Rasa attractors | `src/services/cva_rasa_attractors.py` | 300 | Fixed-point identification, stability analysis |
| Tests | `tests/test_cva_valuation.py` | 300 | Cultural variant validation, attractor identification |
| Documentation | `docs/CVA_VALUATION_AND_FEEDBACK_2026-02-28.md` | 600 | Detailed specifications, cultural examples, neuro predictions |

**Total LOC**: ~2,500 | **Test Coverage**: ≥90%

---

### 2.6 CVA-2-REV Test Acceptance Criteria

```
✓ All 213 original ATLAS tests pass
✓ Core valuation vectors validate (9-dimensional, [0,1] range)
✓ Auxiliary valuation sparse activation (typically 0-2 axes active)
✓ Cultural variants produce correct core/auxiliary structures
✓ Interaction matrices K_vv culture-specific and appropriately coupled
✓ ε_attn: gaze-saliency mismatches detected correctly
✓ ε_prec: constraint variability produces gain modulation ∈ [0, 1]
✓ ε_prior: prior-expectation mismatches computed with correct sign/magnitude
✓ Rasa attractors identified for Indian culture (≥5 distinct basins)
✓ Lyapunov exponents negative for stable attractors, positive for saddle points
✓ Basin volumes decrease with culture parameter κ (fewer attractors at low κ)
✓ No regression in ATLAS overseer invariants
```

---

---

## PART 3: CVA-3 UPDATES

### Scope: ActivityFrame as Precision Modulation Controller

**Duration**: 1.5 weeks | **Effort**: 12 person-days | **Dependencies**: CVA-1-REV, CVA-2-REV complete

---

### 3.1 ActivityFrame Implementation (Revised)

Per Chat's Q1, ActivityFrame now controls precision modulation (π) and prior shifting (β).

**File**: `src/models/activity_frame.py` (REVISED, ~250 lines)

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List
import numpy as np

class ActivityFrame(Enum):
    """
    Activity frames: context-dependent modes that modulate constraint recognition,
    valuation precision (π), and prior expectation (β).
    """
    RESTING = "resting"
    STUDYING = "studying"
    SOCIALIZING = "socializing"
    WORKING = "working"
    EXPLORING = "exploring"
    WORSHIPPING = "worshipping"
    HEALING = "healing"
    CREATING = "creating"
    NEGOTIATING = "negotiating"
    PLAYING = "playing"

@dataclass
class PrecisionModulationTable:
    """
    Maps Activity Frame to precision-gain multipliers on each constraint.

    π(A) = [π_processing, π_load, π_prediction, π_control, π_affordance,
            π_social, π_multisensory, π_narrative]

    Each π_i ∈ [0, 2]: how much does this constraint contribute to valuation
    in this activity frame?
    """
    activity_frame: ActivityFrame

    # Precision gains for each constraint [8]
    processing_cost_gain: float = 1.0
    load_rate_gain: float = 1.0
    prediction_error_gain: float = 1.0
    control_efficacy_gain: float = 1.0
    affordance_density_gain: float = 1.0
    social_cue_density_gain: float = 1.0
    multisensory_coherence_gain: float = 1.0
    narrative_coherence_gain: float = 1.0

    # Auxiliary axes activated
    auxiliary_axes_activated: List[str] = field(default_factory=list)

    # Attention gating (which regions matter)
    attention_mask: Dict[str, float] = field(default_factory=dict)

    def as_vector(self) -> np.ndarray:
        """Return as [8] precision gain vector."""
        return np.array([
            self.processing_cost_gain, self.load_rate_gain, self.prediction_error_gain,
            self.control_efficacy_gain, self.affordance_density_gain,
            self.social_cue_density_gain, self.multisensory_coherence_gain,
            self.narrative_coherence_gain
        ])

@dataclass
class PriorExpectationShift:
    """
    Modulation of valuation priors β(A, ψ) by ActivityFrame.

    β is pre-activation of valuation axes before constraint-driven adjustment.
    In STUDYING frame: higher prior on InterestValue, CompetenceValue
    In HEALING frame: higher prior on RestorationValue, SafetyValue
    """
    activity_frame: ActivityFrame

    # Prior adjustments Δβ [9] (added to default priors)
    safety_prior_delta: float = 0.0
    interest_prior_delta: float = 0.0
    restoration_prior_delta: float = 0.0
    status_prior_delta: float = 0.0
    belonging_prior_delta: float = 0.0
    identity_prior_delta: float = 0.0
    autonomy_prior_delta: float = 0.0
    competence_prior_delta: float = 0.0
    relatedness_prior_delta: float = 0.0

    def as_vector(self) -> np.ndarray:
        """Return as [9] delta-prior vector."""
        return np.array([
            self.safety_prior_delta, self.interest_prior_delta, self.restoration_prior_delta,
            self.status_prior_delta, self.belonging_prior_delta, self.identity_prior_delta,
            self.autonomy_prior_delta, self.competence_prior_delta, self.relatedness_prior_delta
        ])

class ActivityFrameModulationRegistry:
    """
    Registry of how each ActivityFrame modulates constraint precision and valuation priors.
    """

    def __init__(self):
        self.precision_tables: Dict[ActivityFrame, PrecisionModulationTable] = {}
        self.prior_shifts: Dict[ActivityFrame, PriorExpectationShift] = {}

    def register_frame(self, frame: ActivityFrame,
                      precision_table: PrecisionModulationTable,
                      prior_shift: PriorExpectationShift) -> None:
        """Register modulation pattern for activity frame."""
        self.precision_tables[frame] = precision_table
        self.prior_shifts[frame] = prior_shift

    def get_precision_gains(self, frame: ActivityFrame) -> np.ndarray:
        """Get [8] precision gain vector for frame."""
        if frame in self.precision_tables:
            return self.precision_tables[frame].as_vector()
        else:
            return np.ones(8)  # Default: all constraints equally weighted

    def get_prior_shift(self, frame: ActivityFrame) -> np.ndarray:
        """Get [9] prior shift vector for frame."""
        if frame in self.prior_shifts:
            return self.prior_shifts[frame].as_vector()
        else:
            return np.zeros(9)  # Default: no shift

    def populate_defaults(self) -> None:
        """Populate registry with default frame modulations."""

        # STUDYING: high processing cost and prediction error gain; high interest prior
        studying_precision = PrecisionModulationTable(
            activity_frame=ActivityFrame.STUDYING,
            processing_cost_gain=1.5,
            prediction_error_gain=1.4,
            competence_support_gain=1.3,
            other_gains=0.7  # De-emphasize others
        )
        studying_prior = PriorExpectationShift(
            activity_frame=ActivityFrame.STUDYING,
            interest_prior_delta=0.3,
            competence_prior_delta=0.2
        )
        self.register_frame(ActivityFrame.STUDYING, studying_precision, studying_prior)

        # SOCIALIZING: high social cue density gain; high belonging + relatedness prior
        socializing_precision = PrecisionModulationTable(
            activity_frame=ActivityFrame.SOCIALIZING,
            social_cue_density_gain=1.6,
            narrative_coherence_gain=1.2,
            prediction_error_gain=0.8  # Lower: social interactions have inherent uncertainty
        )
        socializing_prior = PriorExpectationShift(
            activity_frame=ActivityFrame.SOCIALIZING,
            belonging_prior_delta=0.3,
            relatedness_prior_delta=0.25
        )
        self.register_frame(ActivityFrame.SOCIALIZING, socializing_precision, socializing_prior)

        # HEALING: high narrative coherence, multisensory coherence; high restoration prior
        healing_precision = PrecisionModulationTable(
            activity_frame=ActivityFrame.HEALING,
            narrative_coherence_gain=1.5,
            multisensory_coherence_gain=1.4,
            processing_cost_gain=0.6  # Minimize distraction
        )
        healing_prior = PriorExpectationShift(
            activity_frame=ActivityFrame.HEALING,
            restoration_prior_delta=0.4,
            safety_prior_delta=0.2
        )
        self.register_frame(ActivityFrame.HEALING, healing_precision, healing_prior)

        # (Continue for other 7 frames...)
```

---

### 3.2 Integration with Feedback Signals

**File**: `src/services/cva_activity_frame_integration.py` (NEW, ~200 lines)

ActivityFrame controls all three feedback signals: attention allocation, precision weighting, prior shifts.

```python
import numpy as np
from src.models.activity_frame import ActivityFrame, ActivityFrameModulationRegistry
from src.services.cva_decomposed_feedback import DecomposedFeedbackSignals

class ActivityFrameFeedbackIntegration:
    """
    Central point where ActivityFrame modulates all three feedback pathways.

    For given (constraint_state, activity_frame, ψ):
    1. Get precision gains π(A) from registry
    2. Get prior shift Δβ(A) from registry
    3. Scale ε_attn by attention gating (A → attention_weights)
    4. Scale ε_prec by π(A) gains
    5. Add Δβ(A) to ε_prior
    """

    def __init__(self, frame_registry: ActivityFrameModulationRegistry):
        self.frame_registry = frame_registry

    def modulate_feedback(self,
                         raw_feedback: DecomposedFeedbackSignals,
                         activity_frame: ActivityFrame) -> DecomposedFeedbackSignals:
        """
        Apply activity frame modulation to raw feedback signals.

        Args:
            raw_feedback: DecomposedFeedbackSignals from neuromechanistic computation
            activity_frame: Current ActivityFrame

        Returns:
            Modulated DecomposedFeedbackSignals with activity frame adjustments applied
        """

        # Get frame-specific modulation parameters
        precision_gains = self.frame_registry.get_precision_gains(activity_frame)  # [8]
        prior_shift = self.frame_registry.get_prior_shift(activity_frame)  # [9]

        # Modulate ε_prec: multiply by mean precision gain
        mean_precision_gain = np.mean(precision_gains)
        modulated_epsilon_prec = raw_feedback.epsilon_prec * mean_precision_gain
        modulated_epsilon_prec = np.clip(modulated_epsilon_prec, 0, 1)

        # Modulate ε_prior: add frame-specific shift
        modulated_epsilon_prior = raw_feedback.epsilon_prior + np.mean(prior_shift)
        modulated_epsilon_prior = np.clip(modulated_epsilon_prior, -1, 1)

        # ε_attn: unchanged at signal level (but affects gaze via attention gating)
        modulated_epsilon_attn = raw_feedback.epsilon_attn

        return DecomposedFeedbackSignals(
            epsilon_attn=modulated_epsilon_attn,
            epsilon_prec=modulated_epsilon_prec,
            epsilon_prior=modulated_epsilon_prior,
            source_description=f"Frame-modulated: {activity_frame.value}"
        )
```

---

### 3.3 CVA-3 Deliverables

| Deliverable | File | LOC | Purpose |
|------------|------|-----|---------|
| ActivityFrame revisioñ | `src/models/activity_frame.py` | 250 | Frame-to-modulation mapping |
| Integration | `src/services/cva_activity_frame_integration.py` | 200 | ActivityFrame modulation of feedback |
| Tests | `tests/test_cva_activity_frame.py` | 150 | Modulation correctness |
| Documentation | `docs/CVA_ACTIVITY_FRAME_INTEGRATION_2026-02-28.md` | 300 | Frame specifications, modulation tables |

**Total LOC**: ~900 | **Test Coverage**: ≥85%

---

---

## PART 4: CROSS-SPRINT INTEGRATION POINTS

### How Chat's Solutions Connect Across Sprints

```
CVA-1-REV (Probabilistic Constraints)
    ↓
    Outputs: Tier 1 + Tier 2 constraint vectors with recognition probabilities
    Used by: CVA-2-REV (constraint-to-valuation mapping)

CVA-2-REV (Two-Tier Valuations + Feedback)
    ↓
    Outputs: v_core + v_aux(A, ψ); ε_attn, ε_prec, ε_prior signals
    Used by: CVA-3 (ActivityFrame modulation), ATLAS integration (projection)

CVA-3 (ActivityFrame Modulation)
    ↓
    Outputs: Modulated feedback π(A), Δβ(A), attention gating
    Used by: Rasa-attractor dynamics, ATLAS coherence computation

CVA-4 (20-Template Pilot)
    ↓
    Inputs: All of above + pilot template data
    Outputs: ψ-aware constraint/valuation estimates for 20 templates × 3 neurotypes

CVA-7 (Identifiability Experiments)
    ↓
    Inputs: VR stimulus protocol + parametric constraint manipulation
    Validates: That ε_attn → gaze shifts, ε_prec → behavioral gain changes, etc.
    Outputs: Empirical evidence for Chat's solutions
```

---

---

## PART 5: PARAMETER MANAGEMENT STRATEGY

### Jordan's Regularization Recommendations

**Problem**: CVA introduces ~200 new parameters (constraint recognition model, K_vv interaction matrices, π tables, etc.). Risk of overfitting and parameter explosion.

**Jordan's solution**: Use structured sparsity and hierarchical priors.

**File**: `src/services/cva_parameter_regularization.py` (NEW, ~200 lines)

```python
import numpy as np
from scipy.sparse import csr_matrix
from typing import Optional

class ConstraintRecognitionRegularization:
    """L1 sparsity on constraint recognition: which Tier 1 features matter for each Tier 2 constraint?"""

    def apply_l1_sparsity(self, feature_weights: np.ndarray, lambda_l1: float = 0.01) -> np.ndarray:
        """
        Apply soft-thresholding: weights below threshold set to zero.
        This forces recognition models to use only most informative Tier 1 features.

        Args:
            feature_weights: [8×6] matrix (8 constraints × 6 Tier 1 features)
            lambda_l1: Sparsity parameter

        Returns:
            Sparsified weights with ~30-40% zeros (target: 5-6 active features per constraint)
        """
        threshold = lambda_l1
        sparsified = np.where(np.abs(feature_weights) > threshold, feature_weights, 0)
        return sparsified

class InteractionMatrixRegularization:
    """
    K_vv interaction matrices: enforce that couplings are sparse (no universal all-to-all).
    Use hierarchical priors on coupling strengths.
    """

    @staticmethod
    def apply_sparsity_to_kvv(K_vv: np.ndarray, sparsity_target: float = 0.5) -> np.ndarray:
        """
        Enforce sparsity: zero out weakest edges until target sparsity achieved.

        Args:
            K_vv: [9×9] interaction matrix
            sparsity_target: Fraction of entries to zero (0.5 = 50% zero)

        Returns:
            Sparse K_vv with hierarchical structure (strong core interactions, weak periphery)
        """

        K_flat = np.abs(K_vv.flatten())
        threshold_idx = int(len(K_flat) * sparsity_target)
        threshold = np.sort(K_flat)[threshold_idx]

        sparse_Kvv = np.where(np.abs(K_vv) >= threshold, K_vv, 0)
        return sparse_Kvv

class HierarchicalPriorOnParameters:
    """
    Constraint recognition weights grouped by constraint → shared hyperpriors.
    Interaction matrix entries grouped by coupling type → shared hyperpriors.
    This reduces effective parameter count from ~200 to ~50 learned hyperparameters.
    """

    def compute_hyperprior_variance(self, param_group: np.ndarray,
                                   group_type: str = 'constraint_weight') -> float:
        """
        Estimate variance hyperprior for group of related parameters.

        Strategy: Use empirical Bayes (Type II ML).
        - Group all weights for "processing_cost" constraint across subjects
        - Estimate group-level variance from data
        - Use as prior for new subjects

        This induces parameter sharing across subjects with similar ψ.
        """
        # Stub implementation
        return np.var(param_group)
```

---

---

## PART 6: EMPIRICAL VALIDATION ROADMAP

### Mapping Panel Recommendations to Experiments

| Panel Recommendation | CVA Sprint | Experiment | Acceptance Criterion |
|---------------------|-----------|-----------|----------------------|
| **Scherer**: Constraint recognition must be measurable via appraisal (gaze-contingent paradigms) | CVA-1-REV | Gaze-constraint correlation study | r ≥ 0.6 per constraint |
| **Zumthor**: Design thinking utility: can architects use CVA to generate designs? | CVA-4, CVA-7 | Architect workshop + design generation task | ≥70% architects report utility |
| **Barrett**: Cultural variation in valuation is structural, not just weights | CVA-2-REV | Multi-group CFA across 4 cultures | CFI ≥ 0.90 (Western, Japanese, W. African, Indian) |
| **Kitayama**: Interaction matrices K_vv must be culture-specific | CVA-2-REV | Bifurcation analysis of K_vv across cultures | Different κ_crit thresholds per culture |
| **Friston**: Free-energy equivalence: are Chat's ODEs variational derivatives of F? | CVA-2-REV, 3 | Formal derivation + numerical verification | F decreases monotonically in simulation |
| **Eisenberger**: Neural predictions: ε_attn → dorsal FP, ε_prec → V1/V2, ε_prior → mPFC | CVA-7 | fMRI validation in 30 subjects | Activation overlap ≥ 70% with predicted regions |
| **Strogatz**: Timescale separation: τ_c << τ_v. Is bifurcation theory applicable? | CVA-2-REV | Phase-plane analysis, slow-fast decomposition | Separation of timescales verified numerically |
| **Jordan**: Parameter explosion: regularization prevents overfitting | CVA-3, 4 | Cross-validation on held-out data | Generalization error <5% vs. in-sample error |

---

---

## PART 7: NEW INVARIANTS FOR OVERSEER MONITORING

Chat's solutions introduce new system properties to monitor:

**File**: `src/services/cva_overseer_invariants.py` (NEW, ~200 lines)

```python
class CVAHealthInvariants:
    """
    Invariants specific to CVA system health. Monitored by OVERSEER.
    """

    # INV-10: Constraint recognition calibration
    # c_recognized should correlate with human constraint ratings (r ≥ 0.75)

    # INV-11: Valuation core stability
    # All cultures must recognize v_core universally. No culture should have >3 v_core axes at zero.

    # INV-12: Rasa-attractor stability
    # For cultures with multi-attractor regime (κ > κ_crit), all attractors must be Lyapunov stable.
    # If Lyapunov exponent > 0, system is in bifurcation region → alert.

    # INV-13: Feedback signal independence
    # ε_attn, ε_prec, ε_prior should be weakly correlated (|ρ| < 0.4).
    # High correlation suggests mechanistic redundancy.

    # INV-14: ActivityFrame coverage
    # All 10 ActivityFrames must have registered modulation tables.
    # Missing frame → log warning, use defaults.

    # INV-15: ψ-population diversity
    # In pilot (CVA-4), ensure ψ-parameters span full neurotype + culture space.
    # Warning if >50% subjects are within single neurotype cluster.
```

---

---

## PART 8: DEFINITION OF DONE

CVA-1-REV, CVA-2-REV, CVA-3 are complete when:

### Code Quality
- [ ] All new code has docstrings (class, method, function)
- [ ] All functions have type hints
- [ ] All files follow PEP 8 (linting via `ruff check`)
- [ ] Test coverage ≥90% per module

### Testing
- [ ] All 213 original ATLAS tests pass
- [ ] All CVA unit tests pass (new tests for new code)
- [ ] Integration tests: CVA-1-REV + CVA-2-REV + CVA-3 work together
- [ ] No regressions in ATLAS overseer invariants (INV-1 through INV-9)

### Specification Adherence
- [ ] All method signatures match this specification exactly
- [ ] All data structures match this specification exactly
- [ ] All file paths match this specification exactly
- [ ] All test acceptance criteria pass

### Documentation
- [ ] Docstrings explain all parameters and return values
- [ ] Architecture Decision Records (ADRs) written for non-trivial choices
- [ ] Measurement protocols documented (CVA-1-REV constraint validation)
- [ ] Cultural variant specifications documented with examples

### Performance
- [ ] Constraint recognition inference: <100ms per stimulus
- [ ] Valuation dynamics integration: <50ms per timestep
- [ ] Rasa-attractor identification: <5s for 100 random starts
- [ ] No memory leaks (checked with `memory_profiler`)

### Panel Review Readiness
- [ ] Specification document complete (this document)
- [ ] Code ready for Scherer/Kitayama/Friston review comments
- [ ] Empirical validation plan drafted for panel sign-off

---

---

## PART 9: RISK REGISTER (UPDATED)

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|-----------|
| Constraint recognition model overfitting (small dataset) | HIGH | MEDIUM | Use L1 regularization, ensemble methods, cross-validation |
| Cultural valuation variation overstated (universals actually dominate) | MEDIUM | MEDIUM | Multi-group CFA with large samples (n≥200 per culture) |
| Rasa-attractors unstable at empirical parameters (bifurcation analysis fails) | HIGH | MEDIUM | Adjust κ_loop, K_vv coupling; work with Kitayama on calibration |
| Parameter explosion (>200 new parameters) | HIGH | LOW | Structured sparsity + hierarchical priors (Jordan's approach) |
| Integration with ATLAS projection (π) breaks existing behavior | HIGH | MEDIUM | Extensive regression testing; strangler fig approach (CVA optional) |
| Temporal dynamics (Strogatz) show τ_c ≈ τ_v (no separation) | MEDIUM | LOW | Include in formal analysis; may require model revision |
| Neural predictions (Eisenberger) falsified by fMRI data | MEDIUM | LOW | Treat as hypothesis; can revise without breaking core CVA |
| Identifiability experiments (Friston) show confounds in constraint manipulation | HIGH | MEDIUM | Pre-register protocol; use causal inference techniques |

---

---

## PART 10: REFERENCE DOCUMENTS & DEPENDENCIES

### Primary Specification Sources
1. **RASA_AS_ATTRACTORS_CVA_DYNAMICS_2026-02-28.md** — Attractor math, bifurcation analysis, Lyapunov stability
2. **CVA_SUBJECT_CHARACTERISTICS_ARCHITECTURE_2026-02-28.md** — ψ parameter space, neurotype profiles, population transfer δ
3. **CVA_CULTURE_AWARE_ARCHITECT_PANEL_2026-02-28.md** — Cultural valuation variants, amae/ma/àṣà/rasa details
4. **CVA_Technical_Paper_Three_Hard_Problems.docx** — Chat's solutions: Q1 (two-tier), Q2 (recognition), Q3 (decomposed feedback)

### Existing ATLAS Infrastructure (to integrate with)
- **src/services/overseer.py** — System health monitoring; extend with CVA invariants
- **src/services/notification_service.py** — Alerts; use for CVA anomaly reporting
- **src/models/epistemic_projection.py** — Projection function π(·); extend with ψ parameterization
- **src/services/extraction_pipeline.py** — Integration orchestrator; add CVA annotation step

### Paper Series (downstream outputs)
- **Paper 1**: ATLAS Architecture + Projection (Sprints 1-REV, 2-REV)
- **Paper 2**: CVA Meta-Framework (Sprints CVA-1-REV, CVA-2-REV, CVA-3)
- **Paper 3**: Cultural Contingency (Sprints CVA-2-REV + expert panels)
- **Paper 4**: Subject-Dependent Constraints (Sprints CVA-1-REV + ψ-architecture)

---

---

## CONCLUSION

This document specifies three major CVA sprints (CVA-1-REV, CVA-2-REV, CVA-3) integrating Chat's Three Hard Problems solutions. The implementation is modular (Tier 1/2 constraints, core/auxiliary valuations, decomposed feedback), empirically grounded (Scherer's appraisal validation, Friston's free energy), and theoretically principled (rasa-as-attractors, culture-aware dynamics).

**Total new code**: ~5,250 LOC across ~15 files
**Total tests**: ~900 LOC across ~8 test files
**Documentation**: ~1,500 LOC in 5-6 markdown files

**Estimated timeline**: 6–7 weeks for AG to implement Phases 1–3.

---

**Document Version**: CVA-SPECIFICATIONS-2.0-FINAL
**Date**: February 28, 2026
**Status**: READY FOR AG IMPLEMENTATION
**Approvals**: Pending David Kirsh + Panel review

