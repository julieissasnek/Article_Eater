"""
Template Computation Functions — Batch 1 Core Templates.

This module implements the computation functions for the 12 core templates
specified in Doc 68 Task 2.1.

Each function:
- Takes the template's inputs_required as arguments
- Applies calibration parameters and Goldilocks boundaries from JSON
- Applies lifespan moderation if occupant_age is provided
- Returns a raw output dict: {output_type: str, value: float, unit: str, ...}

Templates implemented:
1. VF3 - Ceiling Height Goldilocks (R_h ratio)
2. L1 - Luminance Contrast Goldilocks (CV)
3. L2 - Circadian M-EDI Threshold (age-corrected)
4. L3 - Daylight Multi-Channel Composite
5. CREA2 - Processing Style Modulation (2x2x2 matrix)
6. MAT1 - CT-Afferent Touch Pathway
7. MAT2 - Thermal Adaptive PE
8. MAT4 - Natural Material Convergence
9. SOC2 - Privacy-Encounter Gradient
10. SC1 - Spatial Integration / Legibility
11. SC4 - Wayfinding / Social Encounter
12. VIEW1 - View Quality Index (VQI)
"""

import math
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union


# =============================================================================
# OUTPUT TYPES
# =============================================================================

class OutputType(str, Enum):
    """Standard output types for template computations."""
    GOLDILOCKS = "goldilocks_zone"
    THRESHOLD = "threshold_check"
    COMPOSITE = "weighted_composite"
    MATRIX = "matrix_lookup"
    SCORE = "score"
    RATIO = "ratio"


@dataclass
class ComputeResult:
    """Standard result container for template computations."""
    output_type: str
    value: float
    unit: str
    zone: Optional[str] = None
    confidence: float = 1.0
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "output_type": self.output_type,
            "value": self.value,
            "unit": self.unit,
        }
        if self.zone:
            result["zone"] = self.zone
        if self.confidence < 1.0:
            result["confidence"] = self.confidence
        if self.details:
            result["details"] = self.details
        return result


# =============================================================================
# LIFESPAN MODERATION
# =============================================================================

LIFESPAN_SENSITIVITY_MULTIPLIERS = {
    # Per template JSON: u_curve_piecewise model
    "age_0_6": 1.6,
    "age_6_12": 1.35,
    "age_12_25": 1.15,
    "age_25_50": 1.0,  # Reference band
    "age_50_65": 1.2,
    "age_65_80": 1.45,
    "age_80_plus": 1.7,
}


def get_lifespan_multiplier(age: Optional[int]) -> float:
    """
    Get the lifespan sensitivity multiplier for a given age.

    Per template calibration: U-curve model with reference band 25-50.
    Higher values indicate greater sensitivity to environmental effects.
    """
    if age is None:
        return 1.0  # Default to reference band

    if age < 6:
        return LIFESPAN_SENSITIVITY_MULTIPLIERS["age_0_6"]
    elif age < 12:
        return LIFESPAN_SENSITIVITY_MULTIPLIERS["age_6_12"]
    elif age < 25:
        return LIFESPAN_SENSITIVITY_MULTIPLIERS["age_12_25"]
    elif age < 50:
        return LIFESPAN_SENSITIVITY_MULTIPLIERS["age_25_50"]
    elif age < 65:
        return LIFESPAN_SENSITIVITY_MULTIPLIERS["age_50_65"]
    elif age < 80:
        return LIFESPAN_SENSITIVITY_MULTIPLIERS["age_65_80"]
    else:
        return LIFESPAN_SENSITIVITY_MULTIPLIERS["age_80_plus"]


def get_age_band(age: Optional[int]) -> str:
    """Get the age band string for a given age."""
    if age is None:
        return "young_20_40"  # Default

    if age < 3:
        return "toddler_0_3"
    elif age < 6:
        return "age_3_6"
    elif age < 9:
        return "age_6_9"
    elif age < 12:
        return "age_9_12"
    elif age < 16:
        return "age_12_16"
    elif age < 25:
        return "emerging_adult_16_25"
    elif age < 40:
        return "young_20_40"
    elif age < 65:
        return "middle_40_65"
    elif age < 80:
        return "older_65_80"
    else:
        return "frail_80_plus"


# =============================================================================
# VF3: CEILING HEIGHT GOLDILOCKS
# =============================================================================

def compute_vf3_ceiling_height(
    ceiling_height_m: float,
    floor_area_m2: float,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """
    VF3: Ceiling Height and Cognitive Mode.

    Computes R_h (height ratio) = ceiling_height / sqrt(floor_area)
    and maps to Goldilocks zone for processing style priming.

    Zones per VF3 calibration:
    - R_h < 0.25: Confinement (concrete, item-specific processing)
    - R_h 0.25-0.35: Standard (neutral)
    - R_h 0.35-0.50: Liberating (abstract, relational processing)
    - R_h 0.50-0.80: Expansive (strong abstract priming)
    - R_h > 0.80: Awe-inducing (may overwhelm)

    Args:
        ceiling_height_m: Ceiling height in meters
        floor_area_m2: Floor area in square meters
        occupant_age: Optional age for lifespan moderation

    Returns:
        ComputeResult with R_h value and zone classification
    """
    if floor_area_m2 <= 0:
        raise ValueError("Floor area must be positive")
    if ceiling_height_m <= 0:
        raise ValueError("Ceiling height must be positive")

    # Compute R_h ratio
    r_h = ceiling_height_m / math.sqrt(floor_area_m2)

    # Classify into zones
    if r_h < 0.25:
        zone = "confinement"
        pe_direction = "negative"
    elif r_h < 0.35:
        zone = "standard"
        pe_direction = "neutral"
    elif r_h < 0.50:
        zone = "liberating"
        pe_direction = "positive"
    elif r_h < 0.80:
        zone = "expansive"
        pe_direction = "strongly_positive"
    else:
        zone = "awe"
        pe_direction = "overwhelming"

    # Lifespan moderation
    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.GOLDILOCKS,
        value=r_h,
        unit="ratio",
        zone=zone,
        confidence=0.85,  # VF3 maturity: supported_partially_calibrated
        details={
            "ceiling_height_m": ceiling_height_m,
            "floor_area_m2": floor_area_m2,
            "pe_direction": pe_direction,
            "processing_style": "abstract" if r_h >= 0.35 else "concrete",
            "lifespan_multiplier": lifespan_mult,
            "optimal_for_creativity": 0.35 <= r_h <= 0.50,
        },
    )


# =============================================================================
# L1: LUMINANCE CONTRAST GOLDILOCKS
# =============================================================================

def compute_l1_luminance_contrast(
    cv_luminance: float,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """
    L1: Luminance Contrast Prediction Error.

    Maps coefficient of variation (CV) of luminance to Goldilocks zone.

    Zones per L1 calibration_parameters.cv_luminance_goldilocks_boundaries:
    - CV < 0.5: Comfort zone (uniform, calm, low PE)
    - CV 0.5-1.5: Aesthetic zone (Goldilocks optimum)
    - CV 1.5-3.0: Dramatic zone (high PE, shaft/chiaroscuro)
    - CV > 3.0: Glare zone (aversive, discomfort)

    Args:
        cv_luminance: Coefficient of variation of luminance distribution
        occupant_age: Optional age for lifespan moderation

    Returns:
        ComputeResult with CV value and zone classification
    """
    if cv_luminance < 0:
        raise ValueError("CV luminance cannot be negative")

    # Classify into zones
    if cv_luminance < 0.5:
        zone = "comfort"
        pe_level = "low"
        plummer_type = "wash"
    elif cv_luminance < 1.5:
        zone = "aesthetic"
        pe_level = "moderate_optimal"
        plummer_type = "dapple"
    elif cv_luminance < 3.0:
        zone = "dramatic"
        pe_level = "high"
        plummer_type = "shaft_chiaroscuro"
    else:
        zone = "glare"
        pe_level = "excessive"
        plummer_type = "discomfort"

    # Lifespan moderation: older adults have lower glare tolerance
    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.GOLDILOCKS,
        value=cv_luminance,
        unit="cv_ratio",
        zone=zone,
        confidence=0.80,  # L1 maturity: supported
        details={
            "pe_level": pe_level,
            "plummer_light_type": plummer_type,
            "optimal_aesthetic": 0.5 <= cv_luminance <= 1.5,
            "lifespan_multiplier": lifespan_mult,
            "awe_potential": cv_luminance >= 1.5 and cv_luminance < 3.0,
        },
    )


# =============================================================================
# L2: CIRCADIAN M-EDI THRESHOLD
# =============================================================================

def compute_l2_circadian_medi(
    medi_lux: float,
    exposure_duration_hours: float,
    time_of_day: str,  # "morning" | "afternoon" | "evening"
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """
    L2: Circadian Architectural Regulation via M-EDI.

    Checks if melanopic Equivalent Daylight Illuminance meets threshold
    with age correction per L2 calibration.

    Thresholds per L2 calibration_parameters:
    - Standard (age 20-45): M-EDI >= 250 lux for >= 2 hours
    - Age-corrected: M-EDI(age) = M-EDI(25) × (1 + 0.015 × (age - 25))

    Args:
        medi_lux: Melanopic EDI at eye level in lux
        exposure_duration_hours: Duration of exposure
        time_of_day: When exposure occurs
        occupant_age: Age for dose correction

    Returns:
        ComputeResult with threshold check and circadian adequacy
    """
    if medi_lux < 0:
        raise ValueError("M-EDI cannot be negative")
    if exposure_duration_hours < 0:
        raise ValueError("Exposure duration cannot be negative")

    # Calculate age-corrected threshold
    base_threshold = 250.0  # lux for young adults
    age = occupant_age if occupant_age is not None else 30

    # Age correction: ~1.5% increase per year over 25
    if age > 25:
        age_correction = 1 + 0.015 * (age - 25)
    else:
        age_correction = 1.0

    adjusted_threshold = base_threshold * age_correction

    # Duration threshold
    duration_threshold = 2.0  # hours

    # Check adequacy
    medi_adequate = medi_lux >= adjusted_threshold
    duration_adequate = exposure_duration_hours >= duration_threshold

    # Time-of-day effects
    if time_of_day == "morning":
        timing_effect = "phase_advance"
        timing_score = 1.0
    elif time_of_day == "afternoon":
        timing_effect = "maintenance"
        timing_score = 0.8
    else:  # evening
        timing_effect = "phase_delay"
        timing_score = 0.3  # Evening light can disrupt

    # Overall circadian adequacy
    circadian_adequate = medi_adequate and duration_adequate and time_of_day != "evening"

    return ComputeResult(
        output_type=OutputType.THRESHOLD,
        value=medi_lux / adjusted_threshold,  # Ratio to threshold
        unit="ratio_to_threshold",
        zone="adequate" if circadian_adequate else "insufficient",
        confidence=0.90,  # L2 maturity: established
        details={
            "medi_lux": medi_lux,
            "adjusted_threshold_lux": adjusted_threshold,
            "age_correction_factor": age_correction,
            "exposure_hours": exposure_duration_hours,
            "duration_adequate": duration_adequate,
            "medi_adequate": medi_adequate,
            "timing_effect": timing_effect,
            "timing_score": timing_score,
            "circadian_adequate": circadian_adequate,
        },
    )


# =============================================================================
# L3: DAYLIGHT MULTI-CHANNEL COMPOSITE
# =============================================================================

def compute_l3_daylight_composite(
    circadian_score: float,  # 0-1, from L2
    view_score: float,  # 0-1, from VIEW1
    luminance_contrast_score: float,  # 0-1, from L1
    cct_score: float,  # 0-1, from L4 if available
    dynamic_variation_score: float,  # 0-1, from L5 if available
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """
    L3: Daylight as Multi-Channel Stimulus.

    Computes weighted composite of 5 daylight channels per L3 calibration.

    Channel weights from L3 calibration_parameters.channel_weights:
    - circadian_L2: 0.35
    - view_VIEW1: 0.25
    - luminance_contrast_L1: 0.15
    - ecological_CCT_L4: 0.10
    - dynamic_variation_L5: 0.15

    Super-additivity: 15-25% bonus when all channels active.

    Args:
        circadian_score: L2 circadian contribution (0-1)
        view_score: VIEW1 view quality contribution (0-1)
        luminance_contrast_score: L1 luminance contribution (0-1)
        cct_score: L4 color temperature contribution (0-1)
        dynamic_variation_score: L5 temporal variation contribution (0-1)
        occupant_age: Optional age for lifespan moderation

    Returns:
        ComputeResult with weighted composite daylight score
    """
    # Channel weights from L3 calibration
    weights = {
        "circadian": 0.35,
        "view": 0.25,
        "luminance_contrast": 0.15,
        "cct": 0.10,
        "dynamic_variation": 0.15,
    }

    scores = {
        "circadian": circadian_score,
        "view": view_score,
        "luminance_contrast": luminance_contrast_score,
        "cct": cct_score,
        "dynamic_variation": dynamic_variation_score,
    }

    # Validate inputs
    for name, score in scores.items():
        if not 0 <= score <= 1:
            raise ValueError(f"{name} score must be between 0 and 1, got {score}")

    # Compute weighted sum
    base_composite = sum(weights[k] * scores[k] for k in weights)

    # Super-additivity bonus when multiple channels are active
    active_channels = sum(1 for s in scores.values() if s >= 0.5)
    if active_channels >= 4:
        super_additivity = 0.20  # 20% bonus for 4+ active channels
    elif active_channels >= 3:
        super_additivity = 0.10  # 10% bonus for 3 active channels
    else:
        super_additivity = 0.0

    final_composite = min(1.0, base_composite * (1 + super_additivity))

    # Lifespan moderation
    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.COMPOSITE,
        value=final_composite,
        unit="score_0_1",
        zone="excellent" if final_composite >= 0.8 else "good" if final_composite >= 0.6 else "adequate" if final_composite >= 0.4 else "poor",
        confidence=0.75,  # L3 maturity: supported (channel weights preliminary)
        details={
            "channel_scores": scores,
            "channel_weights": weights,
            "base_composite": base_composite,
            "active_channels": active_channels,
            "super_additivity_bonus": super_additivity,
            "lifespan_multiplier": lifespan_mult,
        },
    )


# =============================================================================
# CREA2: PROCESSING STYLE MODULATION (2x2x2 MATRIX)
# =============================================================================

# CREA2 interaction matrix from calibration_data.interaction_matrix
CREA2_MATRIX = {
    # Single factors
    "A": {"d_divergent": 0.42, "d_convergent": -0.18, "sub_additivity": 1.0},
    "B": {"d_divergent": 0.35, "d_convergent": -0.10, "sub_additivity": 1.0},
    "C": {"d_divergent": 0.30, "d_convergent": -0.08, "sub_additivity": 1.0},
    # Two-factor combinations
    "A+B": {"d_divergent": 0.65, "d_convergent": -0.25, "sub_additivity": 0.84},
    "A+C": {"d_divergent": 0.55, "d_convergent": -0.32, "sub_additivity": 0.76},
    "B+C": {"d_divergent": 0.52, "d_convergent": -0.15, "sub_additivity": 0.80},
    # Three-factor combination
    "A+B+C": {"d_divergent": 0.75, "d_convergent": -0.40, "sub_additivity": 0.70},
    # No factors
    "none": {"d_divergent": 0.0, "d_convergent": 0.0, "sub_additivity": 1.0},
}


def compute_crea2_processing_style(
    noise_db: float,
    ceiling_rh: float,
    ambient_lux: float,
    baseline_creativity: str = "medium",  # "low" | "medium" | "high"
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """
    CREA2: Multi-Channel Processing Style Modulation.

    Maps environmental features to divergent/convergent thinking effects
    via 2x2x2 matrix lookup.

    Pathways:
    - A (Disfluency): Noise 65-75 dB
    - B (Spaciousness): Ceiling R_h 0.35-0.50
    - C (Resource): Dim lighting ~150 lux

    Args:
        noise_db: Ambient noise level in dB
        ceiling_rh: Ceiling height ratio (from VF3)
        ambient_lux: Ambient light level in lux
        baseline_creativity: Occupant baseline creativity level
        occupant_age: Optional age for lifespan moderation

    Returns:
        ComputeResult with divergent/convergent effect sizes
    """
    # Classify each pathway
    pathway_a = 65 <= noise_db <= 75  # Optimal disfluency noise
    pathway_b = 0.35 <= ceiling_rh <= 0.50  # Liberating ceiling
    pathway_c = 100 <= ambient_lux <= 200  # Dim lighting

    # Build matrix key
    active = []
    if pathway_a:
        active.append("A")
    if pathway_b:
        active.append("B")
    if pathway_c:
        active.append("C")

    matrix_key = "+".join(active) if active else "none"

    # Get effects from matrix
    effects = CREA2_MATRIX[matrix_key]
    d_divergent = effects["d_divergent"]
    d_convergent = effects["d_convergent"]
    sub_additivity = effects["sub_additivity"]

    # Baseline creativity multiplier
    baseline_multipliers = {"low": 1.5, "medium": 1.0, "high": 0.75}
    baseline_mult = baseline_multipliers.get(baseline_creativity, 1.0)

    adjusted_d_divergent = d_divergent * baseline_mult

    # Lifespan moderation
    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.MATRIX,
        value=adjusted_d_divergent,
        unit="cohens_d",
        zone="generative" if d_divergent >= 0.5 else "balanced" if d_divergent >= 0.25 else "evaluative",
        confidence=0.70,  # CREA2 maturity: expert_estimate for combinations
        details={
            "matrix_key": matrix_key,
            "pathway_a_noise": pathway_a,
            "pathway_b_ceiling": pathway_b,
            "pathway_c_light": pathway_c,
            "raw_d_divergent": d_divergent,
            "raw_d_convergent": d_convergent,
            "sub_additivity": sub_additivity,
            "baseline_creativity": baseline_creativity,
            "baseline_multiplier": baseline_mult,
            "adjusted_d_divergent": adjusted_d_divergent,
            "convergent_tradeoff": d_convergent,
            "lifespan_multiplier": lifespan_mult,
            "design_recommendation": (
                "generative_zone" if d_divergent >= 0.5 else
                "balanced_zone" if d_divergent >= 0.25 else
                "evaluative_zone"
            ),
        },
    )


# =============================================================================
# MAT1: CT-AFFERENT TOUCH PATHWAY
# =============================================================================

# Thermal effusivity categories from MAT1 calibration
EFFUSIVITY_CATEGORIES = {
    "warm_pleasant": {"max": 500, "pe_type": "positive"},
    "neutral": {"min": 500, "max": 1500, "pe_type": "low"},
    "cool_alerting": {"min": 1500, "max": 3000, "pe_type": "moderate_negative"},
    "cold_aversive": {"min": 7000, "pe_type": "high_negative"},
}


def compute_mat1_ct_afferent(
    surface_effusivity: float,
    contact_temperature_c: float,
    ambient_temperature_c: float = 22.0,
    climate: str = "temperate",  # "hot" | "temperate" | "cold"
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """
    MAT1: C-Tactile Affective Touch Pathway.

    Evaluates surface material for CT-afferent activation based on
    thermal effusivity and contact temperature.

    CT-optimal parameters:
    - Velocity: 1-10 cm/s (assumed in contact)
    - Temperature: skin temp ±2°C (~30-34°C)
    - Surface: low effusivity (<500 W·s^½·m⁻²·K⁻¹)

    Args:
        surface_effusivity: Material thermal effusivity
        contact_temperature_c: Surface temperature on contact
        ambient_temperature_c: Ambient air temperature
        climate: Climate zone (affects valence)
        occupant_age: Optional age for lifespan moderation

    Returns:
        ComputeResult with CT-afferent evaluation
    """
    skin_temp = 32.0  # Typical skin temperature

    # Classify effusivity
    if surface_effusivity < 500:
        effusivity_zone = "warm_pleasant"
        base_valence = 0.8
    elif surface_effusivity < 1500:
        effusivity_zone = "neutral"
        base_valence = 0.5
    elif surface_effusivity < 3000:
        effusivity_zone = "cool_alerting"
        base_valence = 0.3
    else:
        effusivity_zone = "cold_aversive"
        base_valence = 0.1

    # Contact temperature evaluation
    temp_deviation = abs(contact_temperature_c - skin_temp)
    if temp_deviation <= 2:
        temp_zone = "pleasurable"
        temp_modifier = 1.0
    elif temp_deviation <= 6:
        temp_zone = "neutral"
        temp_modifier = 0.7
    else:
        temp_zone = "aversive"
        temp_modifier = 0.3

    # Climate adjustment
    if climate == "hot" and effusivity_zone in ["cool_alerting", "cold_aversive"]:
        climate_modifier = 1.5  # Cool surfaces positive in hot climate
    elif climate == "cold" and effusivity_zone in ["cool_alerting", "cold_aversive"]:
        climate_modifier = 0.5  # Cool surfaces negative in cold climate
    else:
        climate_modifier = 1.0

    # Compute final CT-afferent score
    ct_score = base_valence * temp_modifier * climate_modifier
    ct_score = max(0, min(1, ct_score))

    # Lifespan moderation
    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=ct_score,
        unit="score_0_1",
        zone=effusivity_zone,
        confidence=0.80,  # MAT1 maturity: supported
        details={
            "surface_effusivity": surface_effusivity,
            "effusivity_zone": effusivity_zone,
            "contact_temperature_c": contact_temperature_c,
            "temp_zone": temp_zone,
            "temp_deviation": temp_deviation,
            "climate": climate,
            "climate_modifier": climate_modifier,
            "ct_activation": ct_score >= 0.5,
            "lifespan_multiplier": lifespan_mult,
        },
    )


# =============================================================================
# MAT2: THERMAL ADAPTIVE PE
# =============================================================================

def compute_mat2_thermal_adaptive(
    operative_temperature_c: float,
    running_mean_outdoor_c: float,
    ventilation_type: str = "mixed",  # "hvac" | "natural" | "mixed"
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """
    MAT2: Thermal Comfort as Adaptive Prediction Error.

    Computes deviation from adaptive neutral temperature per
    de Dear & Brager (ASHRAE 55).

    Adaptive neutral formula: T_n = 0.31 × T_running_mean + 17.8°C

    Zones:
    - ±1°C: Neutral (near-zero PE)
    - ±1-3°C: Positive PE (alliesthesia potential)
    - ±3-5°C: Tolerance (mildly negative)
    - >±5°C: Discomfort (high PE)

    Args:
        operative_temperature_c: Actual operative temperature
        running_mean_outdoor_c: Running mean outdoor temperature
        ventilation_type: Building ventilation strategy
        occupant_age: Optional age for lifespan moderation

    Returns:
        ComputeResult with thermal PE evaluation
    """
    # Compute adaptive neutral temperature
    t_neutral = 0.31 * running_mean_outdoor_c + 17.8

    # Compute deviation
    deviation = operative_temperature_c - t_neutral
    abs_deviation = abs(deviation)

    # Classify into zones
    if abs_deviation <= 1:
        zone = "neutral"
        pe_magnitude = "near_zero"
        valence = "neutral"
    elif abs_deviation <= 3:
        zone = "alliesthesia"
        pe_magnitude = "moderate"
        valence = "potentially_positive"
    elif abs_deviation <= 5:
        zone = "tolerance"
        pe_magnitude = "moderate_high"
        valence = "mildly_negative"
    else:
        zone = "discomfort"
        pe_magnitude = "high"
        valence = "negative"

    # Ventilation type affects tolerance
    if ventilation_type == "natural":
        tolerance_bonus = 1.0  # Naturally ventilated buildings have wider tolerance
    elif ventilation_type == "mixed":
        tolerance_bonus = 0.5
    else:  # HVAC
        tolerance_bonus = 0.0

    # Compute comfort score
    if abs_deviation <= 1:
        comfort_score = 1.0
    elif abs_deviation <= 3:
        comfort_score = 0.8 - (abs_deviation - 1) * 0.1
    elif abs_deviation <= 5:
        comfort_score = 0.6 - (abs_deviation - 3) * 0.15
    else:
        comfort_score = max(0, 0.3 - (abs_deviation - 5) * 0.1)

    # Lifespan moderation (older adults have narrower thermoregulation)
    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.GOLDILOCKS,
        value=deviation,
        unit="celsius_deviation",
        zone=zone,
        confidence=0.90,  # MAT2 maturity: substantially_calibrated
        details={
            "operative_temperature_c": operative_temperature_c,
            "running_mean_outdoor_c": running_mean_outdoor_c,
            "adaptive_neutral_c": t_neutral,
            "deviation_c": deviation,
            "abs_deviation_c": abs_deviation,
            "pe_magnitude": pe_magnitude,
            "valence": valence,
            "ventilation_type": ventilation_type,
            "tolerance_bonus": tolerance_bonus,
            "comfort_score": comfort_score,
            "thermal_delight_possible": 1 <= abs_deviation <= 3,
            "lifespan_multiplier": lifespan_mult,
        },
    )


# =============================================================================
# MAT4: NATURAL MATERIAL CONVERGENCE
# =============================================================================

# Channel weights from MAT4 calibration_parameters.wood_channel_weights
MAT4_WOOD_WEIGHTS = {
    "visual_grain_fractal": 0.30,
    "haptic_thermal": 0.20,
    "acoustic_absorption": 0.10,
    "olfactory_vocs": 0.15,
    "biophilic_cultural": 0.25,
}

# Non-wood material profiles from MAT4 calibration
MAT4_MATERIAL_PROFILES = {
    "wood": MAT4_WOOD_WEIGHTS,
    "stone": {
        "visual": 0.35,
        "haptic_thermal": 0.30,
        "acoustic": 0.20,
        "olfactory": 0.05,
        "cultural": 0.10,
    },
    "concrete": {
        "visual": 0.40,
        "haptic_thermal": 0.20,
        "acoustic": 0.15,
        "olfactory": 0.05,
        "cultural": 0.20,
    },
    "metal": {
        "visual": 0.35,
        "haptic_thermal": 0.25,
        "acoustic": 0.25,
        "olfactory": 0.05,
        "cultural": 0.10,
    },
}


def compute_mat4_material_convergence(
    material_type: str,  # "wood" | "stone" | "concrete" | "metal"
    surface_ratio: float,  # Proportion of material in space (0-1)
    exposure_duration_min: float = 60.0,
    climate: str = "temperate",
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """
    MAT4: Natural Material Stress Reduction via Multi-Modal Convergence.

    Computes multi-channel stress reduction from natural materials.

    Optimal wood ratio: ~45% (Tsunetsugu et al., 2007) - inverted-U

    Args:
        material_type: Type of natural material
        surface_ratio: Proportion of space covered by material
        exposure_duration_min: Duration of exposure in minutes
        climate: Climate zone (affects haptic-thermal valence)
        occupant_age: Optional age for lifespan moderation

    Returns:
        ComputeResult with material stress-reduction score
    """
    if material_type not in MAT4_MATERIAL_PROFILES:
        raise ValueError(f"Unknown material type: {material_type}")

    if not 0 <= surface_ratio <= 1:
        raise ValueError("Surface ratio must be between 0 and 1")

    profile = MAT4_MATERIAL_PROFILES[material_type]

    # Optimal ratio follows inverted-U (peak at ~0.45)
    optimal_ratio = 0.45
    ratio_deviation = abs(surface_ratio - optimal_ratio)
    ratio_score = max(0, 1 - ratio_deviation * 2)

    # Compute base stress reduction score
    channel_sum = sum(profile.values())
    base_score = channel_sum * ratio_score

    # Olfactory time decay (adapts after 15-20 min)
    if material_type == "wood" and exposure_duration_min > 15:
        olfactory_decay = max(0, 1 - (exposure_duration_min - 15) / 30)
        olfactory_weight = profile.get("olfactory_vocs", 0.15)
        base_score -= olfactory_weight * (1 - olfactory_decay) * ratio_score

    # Climate adjustment for haptic-thermal
    if material_type in ["stone", "concrete", "metal"]:
        if climate == "hot":
            climate_bonus = 0.1  # Cool materials positive in hot climate
        elif climate == "cold":
            climate_bonus = -0.1  # Cool materials negative in cold climate
        else:
            climate_bonus = 0
        base_score += climate_bonus

    # Super-additivity
    super_add = {"wood": 0.25, "stone": 0.125, "concrete": 0.125, "metal": 0.175}
    super_additivity_bonus = super_add.get(material_type, 0.15)

    final_score = min(1.0, base_score * (1 + super_additivity_bonus))

    # Lifespan moderation
    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.COMPOSITE,
        value=final_score,
        unit="score_0_1",
        zone="optimal" if 0.35 <= surface_ratio <= 0.55 else "suboptimal",
        confidence=0.70,  # MAT4 maturity: preliminary for non-wood
        details={
            "material_type": material_type,
            "surface_ratio": surface_ratio,
            "optimal_ratio": optimal_ratio,
            "ratio_score": ratio_score,
            "channel_profile": profile,
            "super_additivity_bonus": super_additivity_bonus,
            "lifespan_multiplier": lifespan_mult,
        },
    )


# =============================================================================
# SOC2: PRIVACY-ENCOUNTER GRADIENT
# =============================================================================

def compute_soc2_privacy_encounter(
    shared_area_ratio: float,
    phone_booths_per_worker: float,
    quiet_rooms_per_worker: float,
    visual_privacy_score: float,  # 0-1
    acoustic_privacy_stc: float,  # STC rating
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """
    SOC2: Architectural Privacy Gradient.

    Computes privacy-encounter adequacy based on spatial provisions.

    Per SOC2 calibration:
    - Optimal shared ratio: 0.50 (±0.08)
    - Knee at 0.70 (satisfaction drops sharply above)
    - Encounter paradox threshold: 0.80

    Minimum prescriptions:
    - 1 phone booth per 8 workers (0.125)
    - 1 quiet room per 25 workers (0.04)

    Args:
        shared_area_ratio: Proportion of shared vs. total area
        phone_booths_per_worker: Ratio of phone booths to workers
        quiet_rooms_per_worker: Ratio of quiet rooms to workers
        visual_privacy_score: Visual privacy level (0-1)
        acoustic_privacy_stc: Sound Transmission Class rating
        occupant_age: Optional age for lifespan moderation

    Returns:
        ComputeResult with privacy-encounter score
    """
    if not 0 <= shared_area_ratio <= 1:
        raise ValueError("Shared area ratio must be between 0 and 1")

    # Shared ratio satisfaction (concave with knee)
    optimal_ratio = 0.50
    tolerance = 0.08
    knee = 0.70

    if shared_area_ratio <= optimal_ratio + tolerance:
        ratio_score = 1 - 2.0 * (shared_area_ratio - optimal_ratio) ** 2
    else:
        ratio_score = 1 - 2.0 * (shared_area_ratio - optimal_ratio) ** 2
        if shared_area_ratio > knee:
            ratio_score -= 4.0 * (shared_area_ratio - knee) ** 2
    ratio_score = max(0, min(1, ratio_score))

    # Encounter paradox check
    encounter_paradox = shared_area_ratio > 0.80

    # Withdrawal space adequacy
    phone_adequate = phone_booths_per_worker >= 0.125
    quiet_adequate = quiet_rooms_per_worker >= 0.04
    withdrawal_score = (
        (1 if phone_adequate else phone_booths_per_worker / 0.125) * 0.5 +
        (1 if quiet_adequate else quiet_rooms_per_worker / 0.04) * 0.5
    )

    # Acoustic privacy (STC rating)
    # STC 50+ = good privacy, STC 35- = poor
    if acoustic_privacy_stc >= 50:
        acoustic_score = 1.0
    elif acoustic_privacy_stc >= 40:
        acoustic_score = 0.7
    elif acoustic_privacy_stc >= 35:
        acoustic_score = 0.4
    else:
        acoustic_score = 0.2

    # Composite privacy score
    weights = {
        "ratio": 0.30,
        "withdrawal": 0.30,
        "visual": 0.20,
        "acoustic": 0.20,
    }
    privacy_score = (
        weights["ratio"] * ratio_score +
        weights["withdrawal"] * withdrawal_score +
        weights["visual"] * visual_privacy_score +
        weights["acoustic"] * acoustic_score
    )

    # Lifespan moderation
    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=privacy_score,
        unit="score_0_1",
        zone="adequate" if privacy_score >= 0.6 else "insufficient",
        confidence=0.85,  # SOC2 maturity: established
        details={
            "shared_area_ratio": shared_area_ratio,
            "ratio_score": ratio_score,
            "encounter_paradox_risk": encounter_paradox,
            "phone_booths_adequate": phone_adequate,
            "quiet_rooms_adequate": quiet_adequate,
            "withdrawal_score": withdrawal_score,
            "visual_privacy_score": visual_privacy_score,
            "acoustic_privacy_stc": acoustic_privacy_stc,
            "acoustic_score": acoustic_score,
            "lifespan_multiplier": lifespan_mult,
        },
    )


# =============================================================================
# SC1: SPATIAL INTEGRATION / LEGIBILITY
# =============================================================================

def compute_sc1_spatial_integration(
    integration_normalized: float,  # 0-1 normalized integration
    intelligibility: float,  # Correlation local-global (0-1)
    depth_from_entrance: int,  # Number of turns from entrance
    has_vertical_transitions: bool = False,
    atrium_present: bool = False,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """
    SC1: Spatial Integration as Navigational Prediction.

    Computes wayfinding/legibility score based on Space Syntax metrics.

    Per SC1 calibration:
    - Integration-valence correlation: r = 0.55
    - Vertical PE multiplier: 1.5x to 2.5x
    - Atrium mitigation: 0.30-0.50 reduction

    Args:
        integration_normalized: Normalized integration value (0-1)
        intelligibility: Local-global correlation (0-1)
        depth_from_entrance: Syntactic depth
        has_vertical_transitions: Whether floor changes exist
        atrium_present: Whether visual atrium connects floors
        occupant_age: Optional age for lifespan moderation

    Returns:
        ComputeResult with spatial legibility score
    """
    if not 0 <= integration_normalized <= 1:
        raise ValueError("Integration must be normalized to 0-1")
    if not 0 <= intelligibility <= 1:
        raise ValueError("Intelligibility must be 0-1")

    # Base legibility from integration (valence regression)
    base_valence = 2.5 + 3.5 * integration_normalized  # 1-7 scale
    legibility_base = (base_valence - 1) / 6  # Normalize to 0-1

    # Intelligibility modifier
    intel_modifier = 0.5 + 0.5 * intelligibility

    # Depth penalty
    if depth_from_entrance <= 2:
        depth_penalty = 0
    elif depth_from_entrance <= 5:
        depth_penalty = 0.05 * (depth_from_entrance - 2)
    else:
        depth_penalty = 0.15 + 0.1 * (depth_from_entrance - 5)
    depth_penalty = min(0.4, depth_penalty)

    # Vertical transition penalty
    if has_vertical_transitions:
        vertical_pe_mult = 2.0  # Average of 1.5-2.5
        if atrium_present:
            vertical_pe_mult *= 0.6  # 40% reduction from atrium
        vertical_penalty = 0.15 * vertical_pe_mult / 2.0
    else:
        vertical_penalty = 0

    # Compute final legibility score
    legibility_score = legibility_base * intel_modifier - depth_penalty - vertical_penalty
    legibility_score = max(0, min(1, legibility_score))

    # Classify navigational confidence
    if legibility_score >= 0.7:
        nav_confidence = "confident"
    elif legibility_score >= 0.4:
        nav_confidence = "moderate"
    else:
        nav_confidence = "disoriented"

    # Lifespan moderation (older adults more affected)
    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=legibility_score,
        unit="score_0_1",
        zone=nav_confidence,
        confidence=0.75,  # SC1 maturity: supported
        details={
            "integration_normalized": integration_normalized,
            "intelligibility": intelligibility,
            "depth_from_entrance": depth_from_entrance,
            "base_valence": base_valence,
            "intel_modifier": intel_modifier,
            "depth_penalty": depth_penalty,
            "has_vertical_transitions": has_vertical_transitions,
            "atrium_present": atrium_present,
            "vertical_penalty": vertical_penalty,
            "nav_confidence": nav_confidence,
            "lifespan_multiplier": lifespan_mult,
        },
    )


# =============================================================================
# SC4: WAYFINDING / SOCIAL ENCOUNTER
# =============================================================================

def compute_sc4_wayfinding_social(
    integration_normalized: float,
    visual_connectivity: float,  # 0-1, isovist-based
    edge_richness: float,  # 0-1, availability of edges/alcoves
    expected_encounter_context: str = "social",  # "social" | "work" | "isolated"
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """
    SC4: Spatial Configuration for Social Encounter.

    Evaluates spatial support for social encounter frequency and quality.

    Per SC4:
    - High integration → high encounter frequency
    - High visual connectivity → high monitoring load
    - Edge conditions → optional engagement

    Args:
        integration_normalized: Space Syntax integration (0-1)
        visual_connectivity: Visual openness / isovist area (0-1)
        edge_richness: Availability of edges/alcoves (0-1)
        expected_encounter_context: Social context expectations
        occupant_age: Optional age for lifespan moderation

    Returns:
        ComputeResult with social encounter adequacy
    """
    if not 0 <= integration_normalized <= 1:
        raise ValueError("Integration must be 0-1")
    if not 0 <= visual_connectivity <= 1:
        raise ValueError("Visual connectivity must be 0-1")
    if not 0 <= edge_richness <= 1:
        raise ValueError("Edge richness must be 0-1")

    # Encounter frequency (positive correlation with integration)
    encounter_frequency = integration_normalized

    # Monitoring load (too much visual connectivity = fatigue)
    if visual_connectivity < 0.3:
        monitoring_load = "low"
        monitoring_score = 0.9
    elif visual_connectivity < 0.6:
        monitoring_load = "moderate"
        monitoring_score = 0.7
    elif visual_connectivity < 0.8:
        monitoring_load = "high"
        monitoring_score = 0.4
    else:
        monitoring_load = "excessive"
        monitoring_score = 0.2

    # Edge availability (enables choice)
    edge_score = edge_richness

    # Context-dependent valence
    if expected_encounter_context == "social":
        context_mult = 1.0  # High encounters are positive
    elif expected_encounter_context == "work":
        context_mult = 0.6  # High encounters may be distracting
    else:  # isolated
        context_mult = 0.3  # Encounters are unwanted

    # Compute composite score
    # Balance: want moderate encounters, low monitoring, high edge choice
    encounter_score = (
        0.3 * encounter_frequency * context_mult +
        0.4 * monitoring_score +
        0.3 * edge_score
    )

    # Open-plan problem detection
    open_plan_risk = visual_connectivity > 0.7 and edge_richness < 0.3

    # Lifespan moderation
    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=encounter_score,
        unit="score_0_1",
        zone="balanced" if encounter_score >= 0.6 else "problematic",
        confidence=0.75,  # SC4 maturity: supported
        details={
            "integration_normalized": integration_normalized,
            "encounter_frequency": encounter_frequency,
            "visual_connectivity": visual_connectivity,
            "monitoring_load": monitoring_load,
            "monitoring_score": monitoring_score,
            "edge_richness": edge_richness,
            "edge_score": edge_score,
            "expected_context": expected_encounter_context,
            "context_multiplier": context_mult,
            "open_plan_risk": open_plan_risk,
            "lifespan_multiplier": lifespan_mult,
        },
    )


# =============================================================================
# VIEW1: VIEW QUALITY INDEX (VQI)
# =============================================================================

def compute_view1_vqi(
    view_type: str,  # "nature" | "urban" | "sky" | "built" | "none"
    view_layers: int,  # Number of depth layers visible (1-3+)
    view_area_ratio: float,  # Window-to-wall ratio
    nature_content_ratio: float,  # Proportion of nature in view (0-1)
    dynamic_content: bool = True,  # Sky, trees, activity visible
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """
    VIEW1: Nature View Convergence — View Quality Index.

    Computes VQI based on 5 convergent channels:
    1. Fractal fluency (nature patterns)
    2. Prospect/refuge (depth layers)
    3. Soft fascination (nature content)
    4. Temporal variation (dynamic content)
    5. Biophilic safety signal

    Args:
        view_type: Primary view content type
        view_layers: Number of visible depth layers
        view_area_ratio: Window-to-wall ratio
        nature_content_ratio: Proportion nature in view
        dynamic_content: Whether view has movement/change
        occupant_age: Optional age for lifespan moderation

    Returns:
        ComputeResult with VQI score (0-100)
    """
    if not 0 <= view_area_ratio <= 1:
        raise ValueError("View area ratio must be 0-1")
    if not 0 <= nature_content_ratio <= 1:
        raise ValueError("Nature content ratio must be 0-1")
    if view_layers < 0:
        raise ValueError("View layers must be non-negative")

    # View type base scores
    view_type_scores = {
        "nature": 1.0,
        "sky": 0.7,
        "urban": 0.5,
        "built": 0.3,
        "none": 0.0,
    }
    view_base = view_type_scores.get(view_type, 0.3)

    # Channel 1: Fractal fluency (nature provides 1/f patterns)
    fractal_score = nature_content_ratio * 0.8 + 0.2  # Min 0.2

    # Channel 2: Prospect/refuge (depth layers)
    if view_layers >= 3:
        depth_score = 1.0
    elif view_layers == 2:
        depth_score = 0.7
    elif view_layers == 1:
        depth_score = 0.4
    else:
        depth_score = 0.1

    # Channel 3: Soft fascination (nature content)
    fascination_score = nature_content_ratio

    # Channel 4: Temporal variation
    temporal_score = 0.8 if dynamic_content else 0.3

    # Channel 5: Biophilic safety signal
    safety_score = view_base * (1 + nature_content_ratio) / 2

    # View area modifier (WWR)
    if view_area_ratio >= 0.4:
        area_modifier = 1.0
    elif view_area_ratio >= 0.2:
        area_modifier = 0.5 + view_area_ratio * 1.25
    else:
        area_modifier = view_area_ratio * 2.5

    # Weighted composite
    channel_weights = {
        "fractal": 0.20,
        "depth": 0.20,
        "fascination": 0.25,
        "temporal": 0.15,
        "safety": 0.20,
    }

    raw_vqi = (
        channel_weights["fractal"] * fractal_score +
        channel_weights["depth"] * depth_score +
        channel_weights["fascination"] * fascination_score +
        channel_weights["temporal"] * temporal_score +
        channel_weights["safety"] * safety_score
    )

    # Apply area modifier and scale to 0-100
    vqi = raw_vqi * area_modifier * 100
    vqi = max(0, min(100, vqi))

    # Super-additivity for multi-channel activation
    active_channels = sum([
        fractal_score >= 0.5,
        depth_score >= 0.5,
        fascination_score >= 0.5,
        temporal_score >= 0.5,
        safety_score >= 0.5,
    ])
    if active_channels >= 4:
        vqi = min(100, vqi * 1.15)  # 15% bonus

    # Classify quality
    if vqi >= 80:
        quality = "excellent"
    elif vqi >= 60:
        quality = "good"
    elif vqi >= 40:
        quality = "adequate"
    elif vqi >= 20:
        quality = "poor"
    else:
        quality = "insufficient"

    # Lifespan moderation (restoration multipliers from VIEW1)
    age_band = get_age_band(occupant_age)
    restoration_mults = {
        "young_20_40": 1.0,
        "middle_40_65": 1.1,
        "older_65_80": 1.2,
        "frail_80_plus": 1.3,
        "age_3_6": 1.5,
        "age_6_9": 1.4,
        "age_9_12": 1.3,
        "age_12_16": 1.15,
    }
    restoration_mult = restoration_mults.get(age_band, 1.0)

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=vqi,
        unit="vqi_0_100",
        zone=quality,
        confidence=0.85,  # VIEW1 maturity: established
        details={
            "view_type": view_type,
            "view_layers": view_layers,
            "view_area_ratio": view_area_ratio,
            "nature_content_ratio": nature_content_ratio,
            "dynamic_content": dynamic_content,
            "channel_scores": {
                "fractal": fractal_score,
                "depth": depth_score,
                "fascination": fascination_score,
                "temporal": temporal_score,
                "safety": safety_score,
            },
            "active_channels": active_channels,
            "area_modifier": area_modifier,
            "restoration_multiplier": restoration_mult,
        },
    )


# =============================================================================
# BATCH 2: L4 - CCT TEMPORAL ECOLOGICAL
# =============================================================================

# CCT ranges from L4 calibration
L4_CCT_RANGES = {
    "warm_firelight": {"min": 1500, "max": 2500, "context": "intimate, evening, rest"},
    "warm_incandescent": {"min": 2500, "max": 3200, "context": "evening, residential"},
    "neutral": {"min": 3800, "max": 4500, "context": "balanced, transitional"},
    "cool_daylight": {"min": 4800, "max": 6500, "context": "midday, alertness, activity"},
    "overcast_sky": {"min": 6500, "max": 10000, "context": "exterior, exposed"},
}


def compute_l4_cct_temporal(
    cct_kelvin: float,
    time_of_day: str,  # "morning" | "midday" | "afternoon" | "evening"
    context_type: str = "office",  # "residential" | "office" | "healthcare" | "hospitality"
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """
    L4: CCT as Temporal and Ecological Prediction Signal.

    Evaluates CCT congruence with time of day and context.
    Match = fluency; Violation = temporal-ecological PE.

    Per L4 calibration:
    - Morning/midday optimal: cool 5000-6500K
    - Evening optimal: warm 2700-3000K
    - Context modulates acceptable range

    Args:
        cct_kelvin: Color temperature in Kelvin
        time_of_day: Time context
        context_type: Building/space type
        occupant_age: Optional age for lifespan moderation

    Returns:
        ComputeResult with congruence evaluation
    """
    if cct_kelvin < 1500 or cct_kelvin > 10000:
        raise ValueError("CCT must be between 1500K and 10000K")

    # Classify CCT
    if cct_kelvin < 2500:
        cct_zone = "warm_firelight"
    elif cct_kelvin < 3200:
        cct_zone = "warm_incandescent"
    elif cct_kelvin < 4500:
        cct_zone = "neutral"
    elif cct_kelvin < 6500:
        cct_zone = "cool_daylight"
    else:
        cct_zone = "overcast_sky"

    # Expected CCT by time of day
    expected_cct = {
        "morning": {"optimal": 5500, "min": 4500, "max": 6500},
        "midday": {"optimal": 6000, "min": 5000, "max": 7000},
        "afternoon": {"optimal": 4500, "min": 3500, "max": 5500},
        "evening": {"optimal": 2800, "min": 2000, "max": 3500},
    }

    time_expectation = expected_cct.get(time_of_day, expected_cct["midday"])

    # Calculate deviation from optimal
    deviation = abs(cct_kelvin - time_expectation["optimal"])
    range_size = time_expectation["max"] - time_expectation["min"]

    if time_expectation["min"] <= cct_kelvin <= time_expectation["max"]:
        congruence_score = 1.0 - (deviation / range_size) * 0.3
        congruence_zone = "congruent"
    else:
        # Outside expected range - calculate PE magnitude
        if cct_kelvin < time_expectation["min"]:
            outside_deviation = time_expectation["min"] - cct_kelvin
        else:
            outside_deviation = cct_kelvin - time_expectation["max"]
        congruence_score = max(0, 0.7 - outside_deviation / 1000)
        congruence_zone = "incongruent"

    # Context adjustment (hospitality expects warmer, healthcare expects brighter)
    context_adjustments = {
        "residential": 0.0,
        "office": -200,  # Slightly cooler expected
        "healthcare": -400,  # Cooler/brighter expected
        "hospitality": 300,  # Warmer expected
    }
    context_adj = context_adjustments.get(context_type, 0)

    # Processing style effect (from L4 calibration)
    if cct_kelvin >= 5000:
        processing_style = "analytical"
        arousal = "heightened"
    elif cct_kelvin <= 3200:
        processing_style = "creative"
        arousal = "lowered"
    else:
        processing_style = "balanced"
        arousal = "moderate"

    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.GOLDILOCKS,
        value=congruence_score,
        unit="score_0_1",
        zone=congruence_zone,
        confidence=0.70,  # L4: supported_with_acknowledged_dissent
        details={
            "cct_kelvin": cct_kelvin,
            "cct_zone": cct_zone,
            "time_of_day": time_of_day,
            "expected_optimal_cct": time_expectation["optimal"],
            "deviation_from_optimal": deviation,
            "context_type": context_type,
            "processing_style": processing_style,
            "arousal_level": arousal,
            "circadian_impact": time_of_day == "evening" and cct_kelvin > 4000,
            "lifespan_multiplier": lifespan_mult,
        },
    )


# =============================================================================
# BATCH 2: L5 - DYNAMIC LIGHT TEMPORAL PE
# =============================================================================

def compute_l5_dynamic_light(
    has_daylight_variation: bool,
    has_designed_dynamics: bool,
    change_rate_hz: Optional[float] = None,  # If artificial, rate of change
    static_exposure_hours: float = 0.0,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """
    L5: Dynamic Light Variation as Sustained Temporal PE Engagement.

    Static lighting habituates; dynamic variation sustains engagement.

    Per L5 calibration:
    - Flicker > 3 Hz: discomfort
    - Minutes-to-hours timescale: positive engagement
    - Static: sensory monotony

    Args:
        has_daylight_variation: Natural daylight present
        has_designed_dynamics: Designed dynamic lighting
        change_rate_hz: Rate of artificial change (None = natural)
        static_exposure_hours: Hours in static lighting
        occupant_age: Optional age for lifespan moderation

    Returns:
        ComputeResult with dynamic engagement score
    """
    # Natural daylight provides optimal dynamics
    if has_daylight_variation:
        dynamics_score = 0.9
        dynamics_zone = "natural_optimal"
        habituation_risk = False
    elif has_designed_dynamics:
        if change_rate_hz is not None:
            if change_rate_hz > 3.0:
                dynamics_score = 0.2
                dynamics_zone = "flicker_discomfort"
                habituation_risk = False
            elif change_rate_hz > 0.01:  # Changes faster than minutes
                dynamics_score = 0.5
                dynamics_zone = "too_rapid"
                habituation_risk = False
            else:
                dynamics_score = 0.75
                dynamics_zone = "designed_moderate"
                habituation_risk = False
        else:
            dynamics_score = 0.7
            dynamics_zone = "designed_moderate"
            habituation_risk = False
    else:
        # Static lighting
        if static_exposure_hours > 4:
            dynamics_score = 0.2
            dynamics_zone = "static_monotony"
            habituation_risk = True
        elif static_exposure_hours > 2:
            dynamics_score = 0.4
            dynamics_zone = "static_habituating"
            habituation_risk = True
        else:
            dynamics_score = 0.5
            dynamics_zone = "static_brief"
            habituation_risk = False

    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=dynamics_score,
        unit="score_0_1",
        zone=dynamics_zone,
        confidence=0.60,  # L5: uncalibrated / supported_preliminary
        details={
            "has_daylight_variation": has_daylight_variation,
            "has_designed_dynamics": has_designed_dynamics,
            "change_rate_hz": change_rate_hz,
            "static_exposure_hours": static_exposure_hours,
            "habituation_risk": habituation_risk,
            "temporal_awareness": dynamics_score >= 0.6,
            "needs_calibration": True,
            "lifespan_multiplier": lifespan_mult,
        },
    )


# =============================================================================
# BATCH 2: MAT3 - MATERIAL IDENTITY INTEGRATION
# =============================================================================

def compute_mat3_material_identity(
    visual_material: str,  # Material appears to be
    haptic_material: str,  # Material feels like
    thermal_material: str,  # Material thermal character
    acoustic_material: str = "unknown",  # Optional acoustic properties
    olfactory_match: bool = True,  # Smell matches visual
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """
    MAT3: Multi-Modal Material Identity Integration.

    Brain predicts haptic/thermal/acoustic from visual; violations
    produce cross-modal PE and material inauthenticity.

    Per MAT3 calibration:
    - Full congruence vs incongruence: d ≈ 0.8-1.2 on pleasantness
    - Haptic incongruence: d ≈ 0.6-0.8 (larger than visual)

    Args:
        visual_material: What material looks like
        haptic_material: What material feels like
        thermal_material: Thermal character (warm/cool)
        acoustic_material: Acoustic properties
        olfactory_match: Whether smell matches appearance
        occupant_age: Optional age for lifespan moderation

    Returns:
        ComputeResult with authenticity score
    """
    # Material categories
    material_categories = {
        "wood": {"thermal": "warm", "haptic": "natural_grain"},
        "stone": {"thermal": "cool", "haptic": "smooth_hard"},
        "metal": {"thermal": "cold", "haptic": "smooth_hard"},
        "plastic": {"thermal": "neutral", "haptic": "smooth"},
        "laminate": {"thermal": "neutral", "haptic": "smooth"},
        "fabric": {"thermal": "warm", "haptic": "soft"},
        "concrete": {"thermal": "cool", "haptic": "rough_hard"},
        "glass": {"thermal": "cold", "haptic": "smooth_hard"},
    }

    # Check congruence
    congruence_channels = 0
    incongruence_channels = 0

    # Visual-haptic congruence (highest weight per MAT3)
    if visual_material == haptic_material:
        congruence_channels += 2  # Double weight
    else:
        incongruence_channels += 2

    # Thermal congruence
    visual_expected = material_categories.get(visual_material, {})
    haptic_expected = material_categories.get(haptic_material, {})

    if visual_expected.get("thermal") == thermal_material or thermal_material == "neutral":
        congruence_channels += 1
    else:
        incongruence_channels += 1

    # Olfactory
    if olfactory_match:
        congruence_channels += 1
    else:
        incongruence_channels += 1

    # Calculate authenticity score
    total_channels = congruence_channels + incongruence_channels
    authenticity_score = congruence_channels / total_channels if total_channels > 0 else 0.5

    # Classify authenticity gradient
    if authenticity_score >= 0.9:
        authenticity_zone = "high_authenticity"
        pe_level = "low"
    elif authenticity_score >= 0.7:
        authenticity_zone = "moderate_authenticity"
        pe_level = "moderate"
    elif authenticity_score >= 0.5:
        authenticity_zone = "low_authenticity"
        pe_level = "high"
    else:
        authenticity_zone = "fake"
        pe_level = "very_high"

    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=authenticity_score,
        unit="score_0_1",
        zone=authenticity_zone,
        confidence=0.65,  # MAT3: protocol_specified
        details={
            "visual_material": visual_material,
            "haptic_material": haptic_material,
            "thermal_material": thermal_material,
            "olfactory_match": olfactory_match,
            "congruent_channels": congruence_channels,
            "incongruent_channels": incongruence_channels,
            "pe_level": pe_level,
            "environmental_trust": authenticity_score >= 0.7,
            "needs_calibration": True,
            "lifespan_multiplier": lifespan_mult,
        },
    )


# =============================================================================
# BATCH 2: MAT5 - MATERIAL CULTURAL CONDITIONING
# =============================================================================

def compute_mat5_material_cultural(
    material_type: str,
    context_type: str,  # "luxury" | "institutional" | "domestic" | "commercial"
    cultural_cluster: str = "north_american",
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """
    MAT5: Material-Cultural Conditioning and Evaluative Association.

    Materials acquire evaluative associations through cultural exposure.
    Activates on recognition (~150ms) and biases affective response.

    Per MAT5: calibration_status = framework_specified (stub implementation)

    Args:
        material_type: Material being evaluated
        context_type: Building/space context
        cultural_cluster: Cultural background
        occupant_age: Optional age for lifespan moderation

    Returns:
        ComputeResult with cultural association score
    """
    # Canonical associations from MAT5
    material_associations = {
        "marble": {"valence": 0.8, "associations": ["prestige", "permanence", "luxury"]},
        "raw_concrete": {"valence": 0.4, "associations": ["brutalism", "honesty", "austerity"]},
        "polished_wood": {"valence": 0.85, "associations": ["warmth", "craft", "tradition"]},
        "glass_steel": {"valence": 0.6, "associations": ["modernity", "transparency", "efficiency"]},
        "brick": {"valence": 0.75, "associations": ["warmth", "tradition", "solidity"]},
        "raw_earth": {"valence": 0.65, "associations": ["vernacular", "sustainability", "authenticity"]},
    }

    material_info = material_associations.get(material_type, {"valence": 0.5, "associations": ["neutral"]})
    base_valence = material_info["valence"]

    # Context appropriateness adjustment
    context_match = {
        ("marble", "luxury"): 0.15,
        ("marble", "institutional"): 0.05,
        ("marble", "domestic"): -0.10,  # Potentially pretentious
        ("raw_concrete", "institutional"): 0.10,
        ("raw_concrete", "domestic"): -0.15,
        ("polished_wood", "domestic"): 0.15,
        ("polished_wood", "luxury"): 0.10,
        ("glass_steel", "commercial"): 0.10,
    }

    context_adj = context_match.get((material_type, context_type), 0)
    adjusted_valence = max(0, min(1, base_valence + context_adj))

    # Cultural moderation (MAT5 specifies this varies significantly)
    cultural_mult = 1.0  # Placeholder - would vary by cultural cluster

    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=adjusted_valence,
        unit="score_0_1",
        zone="positive" if adjusted_valence >= 0.6 else "neutral" if adjusted_valence >= 0.4 else "negative",
        confidence=0.50,  # MAT5: preliminary / framework_specified
        details={
            "material_type": material_type,
            "associations": material_info["associations"],
            "base_valence": base_valence,
            "context_type": context_type,
            "context_adjustment": context_adj,
            "cultural_cluster": cultural_cluster,
            "needs_calibration": True,
            "lifespan_multiplier": lifespan_mult,
        },
    )


# =============================================================================
# BATCH 2: TP1 - MOTOR PREDICTION ERROR
# =============================================================================

# MFI ranges from TP1 calibration
TP1_MFI_RANGES = {
    "baseline": {"min": 0.95, "max": 1.00},
    "optimal_stairs": {"min": 0.80, "max": 0.90},
    "steep_stairs": {"min": 0.65, "max": 0.80},
    "irregular": {"min": 0.60, "max": 0.75},
    "challenging": {"min": 0.45, "max": 0.65},
}


def compute_tp1_motor_pe(
    surface_type: str,  # "level" | "stairs_optimal" | "stairs_steep" | "irregular" | "ramp"
    step_height_mm: Optional[float] = None,
    coefficient_of_friction: float = 0.6,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """
    TP1: Motor Prediction Error in Architectural Surfaces.

    Architecture matching motor predictions = fluency (low PE).
    Violations force conscious control (high PE).

    Per TP1 calibration:
    - Optimal step height: ~0.25 × leg_length
    - Warren (1984) affordance thresholds
    - Age factor: 20-40y = 1.0x; 65-80y = 1.5-2.5x; 80+ = 2.5-4.0x

    Args:
        surface_type: Type of walking surface
        step_height_mm: Step riser height if applicable
        coefficient_of_friction: Surface friction coefficient
        occupant_age: Optional age for cost multiplier

    Returns:
        ComputeResult with motor fluency score
    """
    # Base MFI by surface type
    mfi_bases = {
        "level": 0.97,
        "stairs_optimal": 0.85,
        "stairs_steep": 0.72,
        "irregular": 0.65,
        "ramp": 0.90,
    }
    base_mfi = mfi_bases.get(surface_type, 0.80)

    # Step height adjustment (optimal ~175mm for adults)
    if step_height_mm is not None:
        optimal_step = 175
        step_deviation = abs(step_height_mm - optimal_step)
        if step_deviation <= 15:
            step_modifier = 1.0
        elif step_deviation <= 30:
            step_modifier = 0.95
        elif step_deviation <= 50:
            step_modifier = 0.85
        else:
            step_modifier = 0.70
        base_mfi *= step_modifier

    # Friction adjustment
    if coefficient_of_friction >= 0.55:
        friction_modifier = 1.0
    elif coefficient_of_friction >= 0.4:
        friction_modifier = 0.9
    else:
        friction_modifier = 0.7  # Slip hazard
    base_mfi *= friction_modifier

    # Age-based attentional cost multiplier
    attentional_cost_mults = {
        "young": 1.0,
        "middle": 1.35,
        "older": 2.0,
        "frail": 3.25,
    }

    age_band = get_age_band(occupant_age)
    if age_band in ["young_20_40", "emerging_adult_16_25"]:
        age_category = "young"
    elif age_band in ["middle_40_65"]:
        age_category = "middle"
    elif age_band in ["older_65_80"]:
        age_category = "older"
    elif age_band in ["frail_80_plus"]:
        age_category = "frail"
    else:
        age_category = "young"

    attentional_cost = attentional_cost_mults[age_category]

    # Adjusted motor fluency
    mfi_adjusted = base_mfi / attentional_cost
    mfi_adjusted = max(0, min(1, mfi_adjusted))

    # Classify PE level
    if mfi_adjusted >= 0.85:
        pe_level = "low"
        zone = "fluent"
    elif mfi_adjusted >= 0.65:
        pe_level = "moderate"
        zone = "attention_required"
    else:
        pe_level = "high"
        zone = "conscious_control"

    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.RATIO,
        value=mfi_adjusted,
        unit="mfi_ratio",
        zone=zone,
        confidence=0.80,  # TP1: supported
        details={
            "surface_type": surface_type,
            "step_height_mm": step_height_mm,
            "coefficient_of_friction": coefficient_of_friction,
            "base_mfi": base_mfi,
            "age_category": age_category,
            "attentional_cost_multiplier": attentional_cost,
            "pe_level": pe_level,
            "fall_risk": mfi_adjusted < 0.6 or coefficient_of_friction < 0.4,
            "lifespan_multiplier": lifespan_mult,
        },
    )


# =============================================================================
# BATCH 2: TP2 - THRESHOLD EPISODIC BOUNDARY
# =============================================================================

def compute_tp2_threshold_boundary(
    spatial_change: bool,
    light_change: bool,
    sound_change: bool,
    material_change: bool,
    olfactory_change: bool = False,
    traversal_active: bool = True,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """
    TP2: Architectural Threshold as Episodic Boundary.

    Multi-modal change at thresholds creates episodic boundaries
    (Doorway Effect). More channels = stronger segmentation.

    Per TP2 calibration:
    - 1 channel (spatial): d ≈ 0.25
    - 2 channels: d ≈ 0.45
    - 3 channels: d ≈ 0.68
    - 4 channels: d ≈ 0.88
    - Super-additivity: +15-20%

    Args:
        spatial_change: Room/volume change
        light_change: Illumination change
        sound_change: Acoustic change
        material_change: Surface material change
        olfactory_change: Scent change
        traversal_active: Active navigation (vs. passive)
        occupant_age: Optional age for lifespan moderation

    Returns:
        ComputeResult with boundary strength
    """
    # Channel weights from TP2 calibration
    channel_weights = {
        "spatial": 0.25,
        "light": 0.20,
        "sound": 0.18,
        "material": 0.15,
        "olfactory": 0.12,
    }

    # Count active channels
    active_channels = {
        "spatial": spatial_change,
        "light": light_change,
        "sound": sound_change,
        "material": material_change,
        "olfactory": olfactory_change,
    }

    channels_active = sum(1 for v in active_channels.values() if v)
    weighted_sum = sum(channel_weights[k] for k, v in active_channels.items() if v)

    # Base boundary strength by channel count
    strength_by_count = {
        0: 0.0,
        1: 0.25,
        2: 0.45,
        3: 0.68,
        4: 0.82,
        5: 0.92,
    }
    base_strength = strength_by_count.get(channels_active, 0.92)

    # Super-additivity bonus (synchronized change)
    if channels_active >= 3:
        super_additivity = 0.17  # ~17%
    elif channels_active >= 2:
        super_additivity = 0.08
    else:
        super_additivity = 0.0

    boundary_strength = min(1.0, base_strength * (1 + super_additivity))

    # Active traversal modifier
    if not traversal_active:
        boundary_strength *= 0.7  # Passive movement reduces effect

    # Memory effects
    wm_reset_probability = boundary_strength * 0.8
    encoding_enhancement = boundary_strength * 0.5

    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=boundary_strength,
        unit="d_effect_size",
        zone="strong" if boundary_strength >= 0.6 else "moderate" if boundary_strength >= 0.3 else "weak",
        confidence=0.85,  # TP2: established
        details={
            "active_channels": active_channels,
            "channels_count": channels_active,
            "weighted_channel_sum": weighted_sum,
            "base_strength": base_strength,
            "super_additivity": super_additivity,
            "traversal_active": traversal_active,
            "wm_reset_probability": wm_reset_probability,
            "transition_encoding_boost": encoding_enhancement,
            "doorway_effect_magnitude": boundary_strength,
            "lifespan_multiplier": lifespan_mult,
        },
    )


# =============================================================================
# BATCH 2: TP3 - TEMPORAL RHYTHM (STUB)
# =============================================================================

def compute_tp3_temporal_rhythm(
    occupant_age: Optional[int] = None,
    **kwargs,
) -> ComputeResult:
    """
    TP3: Temporal Rhythm and Architectural Cadence.

    Stub implementation - needs calibration data.

    Args:
        occupant_age: Optional age for lifespan moderation
        **kwargs: Placeholder for future parameters

    Returns:
        ComputeResult with needs_calibration flag
    """
    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=0.5,  # Neutral default
        unit="score_0_1",
        zone="unknown",
        confidence=0.40,
        details={
            "needs_calibration": True,
            "stub_implementation": True,
            "lifespan_multiplier": lifespan_mult,
        },
    )


# =============================================================================
# BATCH 2: TP4 - TEMPORAL HIERARCHY (STUB)
# =============================================================================

def compute_tp4_temporal_hierarchy(
    occupant_age: Optional[int] = None,
    **kwargs,
) -> ComputeResult:
    """
    TP4: Temporal Hierarchy in Architectural Experience.

    Stub implementation - needs calibration data.

    Args:
        occupant_age: Optional age for lifespan moderation
        **kwargs: Placeholder for future parameters

    Returns:
        ComputeResult with needs_calibration flag
    """
    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=0.5,
        unit="score_0_1",
        zone="unknown",
        confidence=0.40,
        details={
            "needs_calibration": True,
            "stub_implementation": True,
            "lifespan_multiplier": lifespan_mult,
        },
    )


# =============================================================================
# BATCH 2: SOC1 - PROXEMIC PE
# =============================================================================

# Zone boundaries from SOC1 calibration (Hall's four zones)
SOC1_ZONE_BOUNDARIES = {
    "intimate": {"max_cm": 45},
    "personal": {"min_cm": 45, "max_cm": 120},
    "social": {"min_cm": 120, "max_cm": 360},
    "public": {"min_cm": 360},
}

# Cultural calibration from SOC1
SOC1_CULTURAL_DISTANCES = {
    "latin_american": {"stranger_cm": 78, "cpp": 0.5},
    "north_american": {"stranger_cm": 95, "cpp": 0.8},
    "northern_european": {"stranger_cm": 100, "cpp": 0.85},
    "east_asian": {"stranger_cm": 102, "cpp": 0.45},
    "middle_eastern": {"stranger_cm": 115, "cpp": 0.7},
}


def compute_soc1_proxemic_pe(
    actual_distance_cm: float,
    relationship_type: str,  # "stranger" | "acquaintance" | "friend" | "intimate"
    cultural_cluster: str = "north_american",
    duration_minutes: float = 5.0,
    choice_available: bool = True,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """
    SOC1: Proxemic Prediction Error.

    Architecture determines interpersonal distance; mismatch with
    social expectations produces proxemic PE.

    Per SOC1 calibration:
    - Too close: inhibition (gaze aversion, stiffening)
    - Too far: approach frustration

    Args:
        actual_distance_cm: Actual interpersonal distance
        relationship_type: Relationship with others
        cultural_cluster: Cultural background
        duration_minutes: Duration of proximity
        choice_available: Whether distance is chosen
        occupant_age: Optional age for lifespan moderation

    Returns:
        ComputeResult with proxemic adequacy score
    """
    # Get expected distance by relationship
    expected_distances = {
        "stranger": 120,
        "acquaintance": 90,
        "friend": 60,
        "intimate": 30,
    }
    expected_cm = expected_distances.get(relationship_type, 100)

    # Cultural adjustment
    cultural_data = SOC1_CULTURAL_DISTANCES.get(cultural_cluster, SOC1_CULTURAL_DISTANCES["north_american"])
    cultural_mult = cultural_data["stranger_cm"] / 95  # Relative to NA baseline
    expected_cm *= cultural_mult

    # Calculate deviation
    deviation_cm = actual_distance_cm - expected_cm
    abs_deviation = abs(deviation_cm)

    # Classify PE direction
    if deviation_cm < -30:  # Too close
        pe_direction = "too_close"
        response = "inhibition"
        comfort_score = max(0, 1 - abs_deviation / 100)
    elif deviation_cm > 60:  # Too far
        pe_direction = "too_far"
        response = "approach_frustration"
        comfort_score = max(0, 1 - abs_deviation / 200)
    else:
        pe_direction = "appropriate"
        response = "comfortable"
        comfort_score = 1.0 - (abs_deviation / 100) * 0.3

    # Duration modifier (sustained PE is worse)
    if duration_minutes > 30:
        duration_penalty = 0.2
    elif duration_minutes > 15:
        duration_penalty = 0.1
    else:
        duration_penalty = 0.0

    comfort_score = max(0, comfort_score - duration_penalty)

    # Choice modifier (forced proximity is worse)
    if not choice_available and pe_direction == "too_close":
        comfort_score *= 0.7

    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=comfort_score,
        unit="score_0_1",
        zone=pe_direction,
        confidence=0.85,  # SOC1: established (Hall ~10,000 citations)
        details={
            "actual_distance_cm": actual_distance_cm,
            "expected_distance_cm": expected_cm,
            "deviation_cm": deviation_cm,
            "relationship_type": relationship_type,
            "cultural_cluster": cultural_cluster,
            "pe_direction": pe_direction,
            "behavioral_response": response,
            "duration_minutes": duration_minutes,
            "choice_available": choice_available,
            "chronic_stress_risk": duration_minutes > 30 and comfort_score < 0.5,
            "lifespan_multiplier": lifespan_mult,
        },
    )


# =============================================================================
# BATCH 2: SOC3 - TERRITORIAL AFFORDANCE
# =============================================================================

def compute_soc3_territorial(
    zone_type: str,  # "private" | "semi_private" | "semi_public" | "public"
    boundary_clarity: float,  # 0-1, how clear are zone transitions
    group_size: int,
    has_back_stage: bool = True,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """
    SOC3: Territorial Affordance and Social Prediction Gradient.

    Clear territorial hierarchy enables social brain calibration.
    Collapse produces diffuse social PE.

    Per SOC3 calibration:
    - Private: near-zero processing load (back stage)
    - Public: high processing load, categorical processing
    - Dunbar layers map to architectural scale

    Args:
        zone_type: Current territorial zone
        boundary_clarity: Clarity of zone boundaries (0-1)
        group_size: Number of people sharing zone
        has_back_stage: Whether private retreat is available
        occupant_age: Optional age for lifespan moderation

    Returns:
        ComputeResult with territorial adequacy score
    """
    # Processing load by zone
    zone_processing = {
        "private": {"load": 0.1, "goffman": "back_stage"},
        "semi_private": {"load": 0.3, "goffman": "relaxed_back_stage"},
        "semi_public": {"load": 0.6, "goffman": "front_stage_familiar"},
        "public": {"load": 0.9, "goffman": "full_front_stage"},
    }

    zone_info = zone_processing.get(zone_type, zone_processing["semi_public"])
    base_load = zone_info["load"]

    # Group size adjustment (Dunbar layers)
    if group_size <= 5:
        size_modifier = 0.0
    elif group_size <= 15:
        size_modifier = 0.1
    elif group_size <= 50:
        size_modifier = 0.2
    elif group_size <= 150:
        size_modifier = 0.3
    else:
        size_modifier = 0.5  # Beyond Dunbar's number

    adjusted_load = min(1.0, base_load + size_modifier)

    # Boundary clarity reduces PE
    pe_magnitude = adjusted_load * (2 - boundary_clarity)

    # Back stage availability
    if not has_back_stage and zone_type in ["semi_public", "public"]:
        pe_magnitude *= 1.3  # Presentation fatigue

    # Territorial adequacy (inverse of PE)
    adequacy_score = 1 - (pe_magnitude / 2)
    adequacy_score = max(0, min(1, adequacy_score))

    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=adequacy_score,
        unit="score_0_1",
        zone=zone_type,
        confidence=0.80,  # SOC3: supported
        details={
            "zone_type": zone_type,
            "goffman_stage": zone_info["goffman"],
            "base_processing_load": base_load,
            "group_size": group_size,
            "size_modifier": size_modifier,
            "boundary_clarity": boundary_clarity,
            "adjusted_processing_load": adjusted_load,
            "pe_magnitude": pe_magnitude,
            "has_back_stage": has_back_stage,
            "presentation_fatigue_risk": not has_back_stage and adjusted_load > 0.6,
            "lifespan_multiplier": lifespan_mult,
        },
    )


# =============================================================================
# BATCH 2: CREA1 - CREATIVE NETWORK DYNAMICS
# =============================================================================

def compute_crea1_creative_network(
    phase: str,  # "generative" | "evaluative" | "transition"
    noise_db: float,
    light_lux: float,
    ceiling_rh: float,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """
    CREA1: Creative Network Dynamics (DMN-ECN Coupling).

    Creativity requires flexible DMN-ECN coupling. Environment
    modulates coupling through sensory richness.

    Per CREA1 calibration:
    - Generative zone: 65-70 dBA, 100-200 lux, R_h > 0.35
    - Evaluative zone: <45 dBA, 400-500 lux, R_h 0.25-0.35

    Args:
        phase: Current creative phase
        noise_db: Ambient noise level
        light_lux: Ambient light level
        ceiling_rh: Ceiling height ratio
        occupant_age: Optional age for lifespan moderation

    Returns:
        ComputeResult with phase-environment match score
    """
    # Phase-optimal conditions from CREA1
    phase_optimal = {
        "generative": {
            "noise_range": (65, 75),
            "light_range": (100, 200),
            "ceiling_min": 0.35,
        },
        "evaluative": {
            "noise_range": (0, 45),
            "light_range": (400, 500),
            "ceiling_range": (0.25, 0.35),
        },
        "transition": {
            "noise_range": (50, 60),
            "light_range": (200, 400),
            "ceiling_min": 0.30,
        },
    }

    optimal = phase_optimal.get(phase, phase_optimal["transition"])

    # Score each dimension
    noise_min, noise_max = optimal.get("noise_range", (50, 60))
    if noise_min <= noise_db <= noise_max:
        noise_score = 1.0
    elif noise_db < noise_min:
        noise_score = max(0, 1 - (noise_min - noise_db) / 20)
    else:
        noise_score = max(0, 1 - (noise_db - noise_max) / 20)

    light_min, light_max = optimal.get("light_range", (200, 400))
    if light_min <= light_lux <= light_max:
        light_score = 1.0
    elif light_lux < light_min:
        light_score = max(0, 1 - (light_min - light_lux) / 100)
    else:
        light_score = max(0, 1 - (light_lux - light_max) / 200)

    ceiling_min = optimal.get("ceiling_min", 0.30)
    ceiling_range = optimal.get("ceiling_range")
    if ceiling_range:
        if ceiling_range[0] <= ceiling_rh <= ceiling_range[1]:
            ceiling_score = 1.0
        else:
            ceiling_score = max(0, 0.7)
    else:
        if ceiling_rh >= ceiling_min:
            ceiling_score = 1.0
        else:
            ceiling_score = max(0, ceiling_rh / ceiling_min)

    # Composite match score
    match_score = (noise_score * 0.35 + light_score * 0.35 + ceiling_score * 0.30)

    # Phase-appropriate processing prediction
    if phase == "generative" and match_score >= 0.7:
        network_state = "dmn_dominant"
        creativity_boost = 0.42  # From CREA2 pathway A
    elif phase == "evaluative" and match_score >= 0.7:
        network_state = "ecn_dominant"
        creativity_boost = 0.0
    else:
        network_state = "mixed"
        creativity_boost = 0.15

    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=match_score,
        unit="score_0_1",
        zone=phase,
        confidence=0.65,  # CREA1: how-plausibly for environmental modulation
        details={
            "phase": phase,
            "noise_db": noise_db,
            "light_lux": light_lux,
            "ceiling_rh": ceiling_rh,
            "noise_score": noise_score,
            "light_score": light_score,
            "ceiling_score": ceiling_score,
            "network_state": network_state,
            "predicted_creativity_boost_d": creativity_boost,
            "environment_phase_match": match_score >= 0.7,
            "lifespan_multiplier": lifespan_mult,
        },
    )


# =============================================================================
# BATCH 2: CREA3 - INCUBATION ARCHITECTURE
# =============================================================================

def compute_crea3_incubation(
    is_walking: bool,
    path_has_nature: bool,
    walk_duration_min: float,
    is_indoors: bool = True,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """
    CREA3: Incubation Architecture (Walking and Mind-Wandering).

    Walking produces large divergent thinking benefit (d ≈ 0.8).
    Soft fascination maintains meta-aware mind-wandering.

    Per CREA3 calibration:
    - Walking effect: d ≈ 0.8 divergent
    - Outdoor bonus: +15-20%
    - Optimal duration: 5-20 minutes

    Args:
        is_walking: Whether walking during incubation
        path_has_nature: Soft fascination elements present
        walk_duration_min: Duration of walk
        is_indoors: Indoor vs outdoor path
        occupant_age: Optional age for lifespan moderation

    Returns:
        ComputeResult with incubation effectiveness score
    """
    # Base effect from walking
    if is_walking:
        if is_indoors:
            base_effect_d = 0.58  # From CREA3: indoor_d 0.55-0.60
        else:
            base_effect_d = 0.74  # From CREA3: outdoor_d 0.70-0.78
    else:
        base_effect_d = 0.0

    # Nature/soft fascination bonus
    if path_has_nature:
        nature_bonus = 0.17 if is_walking else 0.08
    else:
        nature_bonus = 0.0

    total_effect_d = base_effect_d + nature_bonus

    # Duration optimization (5-20 min optimal)
    if 5 <= walk_duration_min <= 20:
        duration_modifier = 1.0
    elif walk_duration_min < 5:
        duration_modifier = walk_duration_min / 5
    else:
        # Diminishing returns after 20 min
        duration_modifier = max(0.7, 1 - (walk_duration_min - 20) / 60)

    adjusted_effect_d = total_effect_d * duration_modifier

    # Convert to 0-1 score (d of 0.8 = good, 1.0 = excellent)
    incubation_score = min(1.0, adjusted_effect_d / 0.8)

    # Convergent tradeoff
    convergent_penalty = -0.15 if is_walking else 0.0

    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=incubation_score,
        unit="score_0_1",
        zone="effective" if incubation_score >= 0.6 else "moderate" if incubation_score >= 0.3 else "minimal",
        confidence=0.75,  # CREA3: supported for walking effect
        details={
            "is_walking": is_walking,
            "path_has_nature": path_has_nature,
            "walk_duration_min": walk_duration_min,
            "is_indoors": is_indoors,
            "base_effect_d": base_effect_d,
            "nature_bonus_d": nature_bonus,
            "duration_modifier": duration_modifier,
            "total_divergent_d": adjusted_effect_d,
            "convergent_tradeoff_d": convergent_penalty,
            "meta_awareness_maintained": is_walking and walk_duration_min >= 5,
            "lifespan_multiplier": lifespan_mult,
        },
    )


# =============================================================================
# BATCH 2: CREA4 - COLLABORATIVE CREATIVITY (STUB)
# =============================================================================

def compute_crea4_collaborative(
    occupant_age: Optional[int] = None,
    **kwargs,
) -> ComputeResult:
    """
    CREA4: Collaborative Creativity Architecture.

    Stub implementation - needs calibration data for collaborative dynamics.

    Args:
        occupant_age: Optional age for lifespan moderation
        **kwargs: Placeholder for future parameters

    Returns:
        ComputeResult with needs_calibration flag
    """
    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=0.5,
        unit="score_0_1",
        zone="unknown",
        confidence=0.40,
        details={
            "needs_calibration": True,
            "stub_implementation": True,
            "lifespan_multiplier": lifespan_mult,
        },
    )


# =============================================================================
# BATCH 2: SC2 - ISOVIST VISUAL PREDICTION (STUB)
# =============================================================================

def compute_sc2_isovist(
    isovist_area_m2: float,
    isovist_perimeter_m: float,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """
    SC2: Isovist Visual Prediction.

    Computes visual exposure and enclosure from isovist properties.

    Args:
        isovist_area_m2: Visible floor area
        isovist_perimeter_m: Isovist boundary length
        occupant_age: Optional age for lifespan moderation

    Returns:
        ComputeResult with visual prediction score
    """
    # Compactness ratio (circle = 1.0, complex shapes < 1.0)
    if isovist_perimeter_m > 0:
        compactness = (4 * math.pi * isovist_area_m2) / (isovist_perimeter_m ** 2)
    else:
        compactness = 0.5

    # Classify visual exposure
    if isovist_area_m2 > 500:
        exposure = "very_high"
        exposure_score = 0.4  # May be overwhelming
    elif isovist_area_m2 > 200:
        exposure = "high"
        exposure_score = 0.6
    elif isovist_area_m2 > 50:
        exposure = "moderate"
        exposure_score = 0.9  # Goldilocks
    else:
        exposure = "enclosed"
        exposure_score = 0.7

    visual_score = exposure_score * (0.5 + compactness * 0.5)

    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=visual_score,
        unit="score_0_1",
        zone=exposure,
        confidence=0.60,  # SC2: partially calibrated
        details={
            "isovist_area_m2": isovist_area_m2,
            "isovist_perimeter_m": isovist_perimeter_m,
            "compactness": compactness,
            "exposure_level": exposure,
            "needs_calibration": True,
            "lifespan_multiplier": lifespan_mult,
        },
    )


# =============================================================================
# BATCH 2: SC3 - ARCHITECTURAL PROMENADE (STUB)
# =============================================================================

def compute_sc3_promenade(
    sequence_length: int,
    pe_variation: float,  # 0-1, variation in PE along path
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """
    SC3: Architectural Promenade PE Orchestration.

    Stub implementation - models PE orchestration along movement paths.

    Args:
        sequence_length: Number of distinct spaces in sequence
        pe_variation: Variation in PE magnitude along path
        occupant_age: Optional age for lifespan moderation

    Returns:
        ComputeResult with promenade quality score
    """
    # More variety = richer experience (up to a point)
    if 3 <= sequence_length <= 7:
        sequence_score = 1.0
    elif sequence_length < 3:
        sequence_score = sequence_length / 3
    else:
        sequence_score = max(0.6, 1 - (sequence_length - 7) / 10)

    # PE variation should be moderate
    if 0.3 <= pe_variation <= 0.7:
        variation_score = 1.0
    else:
        variation_score = 0.7

    promenade_score = sequence_score * 0.6 + variation_score * 0.4

    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=promenade_score,
        unit="score_0_1",
        zone="rich" if promenade_score >= 0.7 else "moderate",
        confidence=0.50,  # SC3: needs calibration
        details={
            "sequence_length": sequence_length,
            "pe_variation": pe_variation,
            "sequence_score": sequence_score,
            "variation_score": variation_score,
            "needs_calibration": True,
            "lifespan_multiplier": lifespan_mult,
        },
    )


# =============================================================================
# BATCH 2: COL1 - CHROMATIC PE
# =============================================================================

def compute_col1_chromatic_pe(
    dominant_hue: str,  # "red" | "orange" | "yellow" | "green" | "blue" | "purple" | "neutral"
    saturation: float,  # 0-1
    context_type: str = "office",
    cultural_cluster: str = "north_american",
    exposure_days: int = 0,  # For habituation
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """
    COL1: Chromatic Prediction Error.

    Three sources: ecological (Palmer EVT), cultural-contextual (Elliot),
    regional expectation (Lenclos). Habituation over days-weeks.

    Per COL1: calibration not yet complete - uses general principles.

    Args:
        dominant_hue: Primary color
        saturation: Color saturation
        context_type: Building context
        cultural_cluster: Cultural background
        exposure_days: Days of exposure (habituation)
        occupant_age: Optional age for lifespan moderation

    Returns:
        ComputeResult with chromatic PE evaluation
    """
    # Ecological valence (Palmer EVT)
    ecological_valence = {
        "blue": 0.8,  # Sky, water
        "green": 0.75,  # Nature
        "yellow": 0.5,  # Mixed associations
        "orange": 0.55,
        "red": 0.4,  # Context-dependent
        "purple": 0.6,
        "neutral": 0.65,
    }
    base_valence = ecological_valence.get(dominant_hue, 0.5)

    # Context appropriateness (Elliot color-in-context)
    context_match = {
        ("red", "restaurant"): 0.2,
        ("red", "office"): -0.2,
        ("blue", "healthcare"): 0.15,
        ("green", "healthcare"): 0.15,
        ("neutral", "office"): 0.1,
    }
    context_adj = context_match.get((dominant_hue, context_type), 0)

    # Saturation effect (high saturation = more PE)
    if saturation > 0.7:
        saturation_effect = -0.1  # May be overwhelming
    elif saturation < 0.2:
        saturation_effect = -0.05  # Dull
    else:
        saturation_effect = 0.05

    # Habituation (PE diminishes over days)
    if exposure_days > 14:
        habituation = 0.5  # Strong habituation
    elif exposure_days > 7:
        habituation = 0.75
    elif exposure_days > 3:
        habituation = 0.9
    else:
        habituation = 1.0

    final_score = (base_valence + context_adj + saturation_effect) * habituation
    final_score = max(0, min(1, final_score))

    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=final_score,
        unit="score_0_1",
        zone="positive" if final_score >= 0.6 else "neutral" if final_score >= 0.4 else "negative",
        confidence=0.60,  # COL1: supported but complex
        details={
            "dominant_hue": dominant_hue,
            "saturation": saturation,
            "ecological_valence": base_valence,
            "context_type": context_type,
            "context_adjustment": context_adj,
            "saturation_effect": saturation_effect,
            "exposure_days": exposure_days,
            "habituation_factor": habituation,
            "needs_calibration": True,
            "lifespan_multiplier": lifespan_mult,
        },
    )


# =============================================================================
# BATCH 2: COL2 - COLOR HARMONY (STUB)
# =============================================================================

def compute_col2_color_harmony(
    occupant_age: Optional[int] = None,
    **kwargs,
) -> ComputeResult:
    """
    COL2: Color Harmony and Palette Composition.

    Stub implementation - needs calibration data.

    Args:
        occupant_age: Optional age for lifespan moderation
        **kwargs: Placeholder for future parameters

    Returns:
        ComputeResult with needs_calibration flag
    """
    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=0.5,
        unit="score_0_1",
        zone="unknown",
        confidence=0.40,
        details={
            "needs_calibration": True,
            "stub_implementation": True,
            "lifespan_multiplier": lifespan_mult,
        },
    )


# =============================================================================
# BATCH 2: VF1 - CONTOUR PE CURVATURE
# =============================================================================

def compute_vf1_contour_curvature(
    curvature_ratio: float,  # Proportion of curved vs angular contours (0-1)
    dominant_contour: str = "mixed",  # "angular" | "curved" | "mixed"
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """
    VF1: Contour PE and Curvature Preference.

    Curved contours are generally preferred (Bar & Neta, 2006).
    Sharp angles may trigger threat-related processing.

    Args:
        curvature_ratio: Proportion of curved elements
        dominant_contour: Overall contour character
        occupant_age: Optional age for lifespan moderation

    Returns:
        ComputeResult with curvature preference score
    """
    # Curvature preference (0.6-0.8 preferred based on Bar & Neta)
    if 0.4 <= curvature_ratio <= 0.8:
        curvature_score = 0.8 + (curvature_ratio - 0.4) * 0.25
    elif curvature_ratio > 0.8:
        curvature_score = 0.9  # Very curved is also good
    else:
        # Angular dominated - may trigger threat
        curvature_score = max(0.3, 0.5 + curvature_ratio)

    # Dominant contour effect
    contour_modifiers = {
        "angular": -0.1,
        "curved": 0.1,
        "mixed": 0.0,
    }
    contour_adj = contour_modifiers.get(dominant_contour, 0)

    final_score = max(0, min(1, curvature_score + contour_adj))

    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=final_score,
        unit="score_0_1",
        zone="curved_preferred" if curvature_ratio >= 0.5 else "angular",
        confidence=0.70,  # VF1: supported
        details={
            "curvature_ratio": curvature_ratio,
            "dominant_contour": dominant_contour,
            "base_curvature_score": curvature_score,
            "contour_adjustment": contour_adj,
            "threat_activation_risk": curvature_ratio < 0.3,
            "lifespan_multiplier": lifespan_mult,
        },
    )


# =============================================================================
# BATCH 2: VF2 - VISUAL RHYTHM SCALING (STUB)
# =============================================================================

def compute_vf2_visual_rhythm(
    occupant_age: Optional[int] = None,
    **kwargs,
) -> ComputeResult:
    """
    VF2: Visual Rhythm and Scale Relationships.

    Stub implementation - needs calibration data for rhythm parameters.

    Args:
        occupant_age: Optional age for lifespan moderation
        **kwargs: Placeholder for future parameters

    Returns:
        ComputeResult with needs_calibration flag
    """
    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=0.5,
        unit="score_0_1",
        zone="unknown",
        confidence=0.40,
        details={
            "needs_calibration": True,
            "stub_implementation": True,
            "lifespan_multiplier": lifespan_mult,
        },
    )


# =============================================================================
# BATCH 2: OLF1 - OLFACTORY PE TRANSITION
# =============================================================================

def compute_olf1_olfactory_pe(
    material_scent_match: bool,
    functional_scent_match: bool,
    is_threshold_crossing: bool,
    exposure_minutes: float = 0.0,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """
    OLF1: Olfactory PE at Architectural Transitions.

    Olfaction has direct limbic access. Rapid adaptation (2-10 min)
    makes it primarily a transition modality.

    Per OLF1 calibration:
    - Adaptation: 2-10 minutes
    - Proust effect: strong episodic encoding

    Args:
        material_scent_match: Smell matches visual materials
        functional_scent_match: Smell matches space function
        is_threshold_crossing: At a spatial transition
        exposure_minutes: Duration in current scent zone
        occupant_age: Optional age for lifespan moderation

    Returns:
        ComputeResult with olfactory PE evaluation
    """
    # Congruence scores
    material_score = 1.0 if material_scent_match else 0.4
    functional_score = 1.0 if functional_scent_match else 0.5

    base_score = material_score * 0.5 + functional_score * 0.5

    # Adaptation (rapid, 2-10 minutes)
    if exposure_minutes > 10:
        adaptation = 0.1  # Fully adapted
    elif exposure_minutes > 5:
        adaptation = 0.4
    elif exposure_minutes > 2:
        adaptation = 0.7
    else:
        adaptation = 1.0  # Fresh entry

    # Threshold crossing enhances encoding
    if is_threshold_crossing:
        encoding_boost = 0.3
        episodic_encoding = "enhanced"
    else:
        encoding_boost = 0.0
        episodic_encoding = "normal"

    # Olfactory contribution (decays with adaptation)
    olfactory_score = base_score * adaptation + encoding_boost
    olfactory_score = max(0, min(1, olfactory_score))

    lifespan_mult = get_lifespan_multiplier(occupant_age)

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=olfactory_score,
        unit="score_0_1",
        zone="congruent" if base_score >= 0.7 else "incongruent",
        confidence=0.70,  # OLF1: supported
        details={
            "material_scent_match": material_scent_match,
            "functional_scent_match": functional_scent_match,
            "is_threshold_crossing": is_threshold_crossing,
            "exposure_minutes": exposure_minutes,
            "adaptation_factor": adaptation,
            "episodic_encoding": episodic_encoding,
            "proust_effect_potential": is_threshold_crossing and adaptation > 0.5,
            "lifespan_multiplier": lifespan_mult,
        },
    )


# =============================================================================
# BATCH 3: GAP TEMPLATE COMPUTATIONS (TASK 3.8)
# =============================================================================

RISK_TO_WIS = {
    "low": 65.0,
    "moderate": 45.0,
    "high": 25.0,
}


def _risk_level_from_index(index: float) -> str:
    if index >= 0.67:
        return "high"
    if index >= 0.34:
        return "moderate"
    return "low"


def _gap_result(
    *,
    template_id: str,
    risk_index: float,
    mechanism: str,
    occupant_age: Optional[int] = None,
    inputs: Optional[Dict[str, Any]] = None,
) -> ComputeResult:
    risk_level = _risk_level_from_index(max(0.0, min(1.0, risk_index)))
    wis = RISK_TO_WIS[risk_level]
    return ComputeResult(
        output_type=OutputType.SCORE,
        value=wis,
        unit="wis_0_100",
        zone=risk_level,
        confidence=0.35,
        details={
            "template_id": template_id,
            "risk_level": risk_level,
            "mechanism": mechanism,
            "needs_calibration": True,
            "lifespan_multiplier": get_lifespan_multiplier(occupant_age),
            "inputs": inputs or {},
        },
    )


def compute_t4_attention_demand(
    distraction_rate_per_hour: float,
    attentional_switch_cost: float,
    recovery_breaks_per_hour: float,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    risk_index = (
        min(distraction_rate_per_hour / 12.0, 1.0) * 0.45
        + max(0.0, min(attentional_switch_cost, 1.0)) * 0.35
        + max(0.0, 1.0 - min(recovery_breaks_per_hour / 4.0, 1.0)) * 0.20
    )
    return _gap_result(
        template_id="T4",
        risk_index=risk_index,
        mechanism="Sustained attentional demand without adequate recovery.",
        occupant_age=occupant_age,
        inputs={
            "distraction_rate_per_hour": distraction_rate_per_hour,
            "attentional_switch_cost": attentional_switch_cost,
            "recovery_breaks_per_hour": recovery_breaks_per_hour,
        },
    )


def compute_t6_cortisol_cascade(
    chronic_noise_exposure_dba: float,
    sleep_quality: float,
    control_perception: float,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    risk_index = (
        min(max(chronic_noise_exposure_dba - 45.0, 0.0) / 25.0, 1.0) * 0.45
        + max(0.0, 1.0 - min(sleep_quality, 1.0)) * 0.35
        + max(0.0, 1.0 - min(control_perception, 1.0)) * 0.20
    )
    return _gap_result(
        template_id="T6",
        risk_index=risk_index,
        mechanism="Stress hormone escalation under chronic noise and low control.",
        occupant_age=occupant_age,
        inputs={
            "chronic_noise_exposure_dba": chronic_noise_exposure_dba,
            "sleep_quality": sleep_quality,
            "control_perception": control_perception,
        },
    )


def compute_t7_allostatic_anticipation(
    unpredictability_index: float,
    perceived_control: float,
    exposure_duration_hours: float,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    risk_index = (
        max(0.0, min(unpredictability_index, 1.0)) * 0.50
        + max(0.0, 1.0 - min(perceived_control, 1.0)) * 0.30
        + min(exposure_duration_hours / 10.0, 1.0) * 0.20
    )
    return _gap_result(
        template_id="T7",
        risk_index=risk_index,
        mechanism="Anticipatory allostatic load from persistent unpredictability.",
        occupant_age=occupant_age,
        inputs={
            "unpredictability_index": unpredictability_index,
            "perceived_control": perceived_control,
            "exposure_duration_hours": exposure_duration_hours,
        },
    )


def compute_t10_sleep_consolidation(
    night_noise_dba: float,
    light_intrusion_lux: float,
    bedtime_regular: bool,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    risk_index = (
        min(max(night_noise_dba - 30.0, 0.0) / 25.0, 1.0) * 0.45
        + min(light_intrusion_lux / 25.0, 1.0) * 0.35
        + (0.20 if not bedtime_regular else 0.0)
    )
    return _gap_result(
        template_id="T10",
        risk_index=risk_index,
        mechanism="Impaired sleep consolidation from nighttime sensory disruption.",
        occupant_age=occupant_age,
        inputs={
            "night_noise_dba": night_noise_dba,
            "light_intrusion_lux": light_intrusion_lux,
            "bedtime_regular": bedtime_regular,
        },
    )


def compute_t14_navigation_stress_loop(
    wayfinding_error_rate: float,
    crowding_level: float,
    time_pressure: float,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    risk_index = (
        min(wayfinding_error_rate / 8.0, 1.0) * 0.45
        + max(0.0, min(crowding_level, 1.0)) * 0.30
        + max(0.0, min(time_pressure, 1.0)) * 0.25
    )
    return _gap_result(
        template_id="T14",
        risk_index=risk_index,
        mechanism="Navigation errors reinforce stress and attentional narrowing.",
        occupant_age=occupant_age,
        inputs={
            "wayfinding_error_rate": wayfinding_error_rate,
            "crowding_level": crowding_level,
            "time_pressure": time_pressure,
        },
    )





def compute_t17_dopaminergic_novelty(
    novelty_density: float,
    monotony_days: float,
    exploration_access: float,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    risk_index = (
        max(0.0, 1.0 - min(novelty_density, 1.0)) * 0.40
        + min(monotony_days / 14.0, 1.0) * 0.35
        + max(0.0, 1.0 - min(exploration_access, 1.0)) * 0.25
    )
    return _gap_result(
        template_id="T17",
        risk_index=risk_index,
        mechanism="Novelty deprivation suppresses dopaminergic exploratory drive.",
        occupant_age=occupant_age,
        inputs={
            "novelty_density": novelty_density,
            "monotony_days": monotony_days,
            "exploration_access": exploration_access,
        },
    )


def compute_t18_vestibular_spatial(
    vertical_transition_count: float,
    vestibular_cue_quality: float,
    motion_disorientation_events: float,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    risk_index = (
        min(vertical_transition_count / 20.0, 1.0) * 0.25
        + max(0.0, 1.0 - min(vestibular_cue_quality, 1.0)) * 0.45
        + min(motion_disorientation_events / 6.0, 1.0) * 0.30
    )
    return _gap_result(
        template_id="T18",
        risk_index=risk_index,
        mechanism="Vestibular-spatial mismatch increases disorientation burden.",
        occupant_age=occupant_age,
        inputs={
            "vertical_transition_count": vertical_transition_count,
            "vestibular_cue_quality": vestibular_cue_quality,
            "motion_disorientation_events": motion_disorientation_events,
        },
    )


def compute_t23_context_memory(
    context_stability: float,
    cue_congruence: float,
    transition_frequency: float,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    risk_index = (
        max(0.0, 1.0 - min(context_stability, 1.0)) * 0.40
        + max(0.0, 1.0 - min(cue_congruence, 1.0)) * 0.35
        + min(transition_frequency / 12.0, 1.0) * 0.25
    )
    return _gap_result(
        template_id="T23",
        risk_index=risk_index,
        mechanism="Weak context cues undermine memory retrieval and encoding.",
        occupant_age=occupant_age,
        inputs={
            "context_stability": context_stability,
            "cue_congruence": cue_congruence,
            "transition_frequency": transition_frequency,
        },
    )


def compute_t28_cognitive_offloading(
    external_memory_support_score: float,
    signage_clarity: float,
    working_memory_load: float,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    risk_index = (
        max(0.0, 1.0 - min(external_memory_support_score, 1.0)) * 0.40
        + max(0.0, 1.0 - min(signage_clarity, 1.0)) * 0.30
        + max(0.0, min(working_memory_load, 1.0)) * 0.30
    )
    return _gap_result(
        template_id="T28",
        risk_index=risk_index,
        mechanism="Insufficient offloading support overloads working memory.",
        occupant_age=occupant_age,
        inputs={
            "external_memory_support_score": external_memory_support_score,
            "signage_clarity": signage_clarity,
            "working_memory_load": working_memory_load,
        },
    )


# =============================================================================
# BATCH 4: RESIDUAL TEMPLATE COMPUTATIONS
# =============================================================================

def compute_t1_temporal_spectral_match(
    spectral_slope: float,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """T1 Residual: 1/f Temporal Spectral Matching (Auditory)."""
    # Target slope: -1.0 (pink noise) -> optimal
    diff = abs(spectral_slope - (-1.0))
    
    if diff < 0.2:
        zone = "optimal_1_f"
        wis_raw = 85
    elif diff < 0.5:
        zone = "near_optimal"
        wis_raw = 65
    else:
        zone = "non_fractal"
        wis_raw = 35

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=wis_raw / 100.0,
        unit="wis_normalized",
        zone=zone,
        confidence=0.5,
        details={"spectral_slope": spectral_slope, "diff": diff}
    )

def compute_t2_prospect_refuge_residual(
    is_enclosed_niche: bool,
    rear_protection: bool,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """T2 Residual: Refuge Component (Safety Niche)."""
    if is_enclosed_niche and rear_protection:
        zone = "strong_refuge"
        wis_raw = 85
    elif is_enclosed_niche or rear_protection:
        zone = "partial_refuge"
        wis_raw = 60
    else:
        zone = "exposed"
        wis_raw = 30

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=wis_raw / 100.0,
        unit="wis_normalized",
        zone=zone,
        confidence=0.6,
        details={"is_enclosed_niche": is_enclosed_niche, "rear_protection": rear_protection}
    )

def compute_t5_enclosure_threat_residual(
    ceiling_height_m: float,
    floor_area_m2: float,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """T5 Residual: Visceral Threat Detection at Extreme Confinement."""
    r_h = ceiling_height_m / math.sqrt(floor_area_m2) if floor_area_m2 > 0 else 0
    
    if r_h < 0.20:
        zone = "visceral_threat"
        wis_raw = 15  # Active harm
        confidence = 0.8
    else:
        zone = "baseline_safe"
        wis_raw = 50  # Neutral (handled by VF3 above this)
        confidence = 0.5

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=wis_raw / 100.0,
        unit="wis_normalized",
        zone=zone,
        confidence=confidence,
        details={"r_h": r_h, "threshold": 0.20}
    )

def compute_t8_neural_grid_constraint(
    visual_access_grid: bool,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """T8 Residual: Neural Grid/Place Cell Constraint."""
    if visual_access_grid:
        zone = "supported"
        wis_raw = 70
    else:
        zone = "unsupported"
        wis_raw = 40

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=wis_raw / 100.0,
        unit="wis_normalized",
        zone=zone,
        confidence=0.4,
        details={"visual_access_grid": visual_access_grid}
    )

def compute_t11_exploration_mode(
    environmental_novelty_score: float,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """T11 Residual: LC-NE Arousal / Exploration Mode."""
    if environmental_novelty_score > 0.8:
        zone = "exploration_mode"
        wis_raw = 75
    elif environmental_novelty_score > 0.4:
        zone = "balanced_mode"
        wis_raw = 65
    else:
        zone = "habituation_mode"
        wis_raw = 50

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=wis_raw / 100.0,
        unit="wis_normalized",
        zone=zone,
        confidence=0.5,
        details={"novelty_score": environmental_novelty_score}
    )

def compute_t15_personal_control(
    has_thermostat_control: bool,
    has_operable_windows: bool,
    has_movable_furniture: bool,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """T15 Residual: Environmental Mastery / Personal Control."""
    score = sum([has_thermostat_control, has_operable_windows, has_movable_furniture])
    
    if score >= 2:
        zone = "high_control"
        wis_raw = 85
    elif score == 1:
        zone = "moderate_control"
        wis_raw = 65
    else:
        zone = "low_control"
        wis_raw = 35

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=wis_raw / 100.0,
        unit="wis_normalized",
        zone=zone,
        confidence=0.7,
        details={"control_points": score}
    )

def compute_t16_restoration_timecourse(
    exposure_duration_min: float,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """T16 Residual: Restoration Time-Course Dynamics."""
    if exposure_duration_min < 5:
        zone = "insufficient"
        wis_raw = 30
    elif exposure_duration_min < 20:
        zone = "partial_restoration"
        wis_raw = 60
    else:
        zone = "full_restoration"
        wis_raw = 85

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=wis_raw / 100.0,
        unit="wis_normalized",
        zone=zone,
        confidence=0.6,
        details={"duration_min": exposure_duration_min}
    )

def compute_t20_convergent_performance(
    distraction_free_ratio: float,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """T20 Residual: Convergent Cognitive Performance."""
    if distraction_free_ratio > 0.8:
        zone = "high_focus"
        wis_raw = 80
    elif distraction_free_ratio > 0.5:
        zone = "moderate_focus"
        wis_raw = 60
    else:
        zone = "low_focus"
        wis_raw = 35

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=wis_raw / 100.0,
        unit="wis_normalized",
        zone=zone,
        confidence=0.6,
        details={"distraction_free_ratio": distraction_free_ratio}
    )

def compute_t22_rapid_gist(
    scene_gist_clarity: float,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """T22 Residual: Rapid Gist / LSF Magnocellular Processing."""
    if scene_gist_clarity > 0.7:
        zone = "high_clarity"
        wis_raw = 75
    else:
        zone = "low_clarity"
        wis_raw = 45

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=wis_raw / 100.0,
        unit="wis_normalized",
        zone=zone,
        confidence=0.4,
        details={"scene_gist_clarity": scene_gist_clarity}
    )

def compute_t24_theta_sequence(
    spatial_sequence_clarity: float,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """T24 Residual: Theta Sequence / Spatial Navigation Constraint."""
    if spatial_sequence_clarity > 0.6:
        zone = "supported"
        wis_raw = 70
    else:
        zone = "unsupported"
        wis_raw = 40

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=wis_raw / 100.0,
        unit="wis_normalized",
        zone=zone,
        confidence=0.3,
        details={"spatial_sequence_clarity": spatial_sequence_clarity}
    )

def compute_t27_non_thermal_interoception(
    iaq_co2_ppm: float,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """T27 Residual: Non-Thermal Interoception (Air Quality)."""
    if iaq_co2_ppm < 800:
        zone = "good_iaq"
        wis_raw = 80
    elif iaq_co2_ppm < 1200:
        zone = "moderate_iaq"
        wis_raw = 55
    else:
        zone = "poor_iaq"
        wis_raw = 25

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=wis_raw / 100.0,
        unit="wis_normalized",
        zone=zone,
        confidence=0.7,
        details={"iaq_co2_ppm": iaq_co2_ppm}
    )

def compute_t32_subcortical_auditory(
    acoustic_snr_db: float,
    rt60: float,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """T32 Residual: Subcortical Auditory Encoding."""
    if acoustic_snr_db > 15:
        zone = "high_intelligibility"
        wis_raw = 80
    elif acoustic_snr_db > 5:
        zone = "moderate_intelligibility"
        wis_raw = 60
    else:
        zone = "poor_intelligibility"
        wis_raw = 30

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=wis_raw / 100.0,
        unit="wis_normalized",
        zone=zone,
        confidence=0.6,
        details={"acoustic_snr_db": acoustic_snr_db, "rt60": rt60}
    )

def compute_t33_reverberation_space(
    rt60: float,
    room_volume_m3: float,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """T33 Residual: Reverberation-Space Congruence."""
    # Sabin estimate (very rough): T = 0.161 * V / A
    # Expect larger rooms to have longer RT60
    expected_rt60 = 0.5 * math.log10(max(1, room_volume_m3 / 10.0))
    deviation = abs(rt60 - expected_rt60)
    
    if deviation < 0.3:
        zone = "congruent"
        wis_raw = 70
    else:
        zone = "incongruent"
        wis_raw = 40

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=wis_raw / 100.0,
        unit="wis_normalized",
        zone=zone,
        confidence=0.4,
        details={"rt60": rt60, "expected_rt60": expected_rt60, "deviation": deviation}
    )

def compute_t38_hierarchical_control_depth(
    spatial_nesting_levels: int,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """T38 Residual: Hierarchical Control Nesting Depth."""
    if spatial_nesting_levels <= 3:
        zone = "optimal_depth"
        wis_raw = 80
    elif spatial_nesting_levels == 4:
        zone = "max_depth"
        wis_raw = 60
    else:
        zone = "cognitive_overload"
        wis_raw = 30

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=wis_raw / 100.0,
        unit="wis_normalized",
        zone=zone,
        confidence=0.5,
        details={"nesting_levels": spatial_nesting_levels}
    )

def compute_t40_msi_inverse_effectiveness(
    unisensory_strength_avg: float,
    occupant_age: Optional[int] = None,
) -> ComputeResult:
    """T40 Residual: MSI Inverse Effectiveness Principle."""
    # Enhancement is greater when individual signals are weak
    if unisensory_strength_avg < 0.4:
        zone = "high_enhancement_potential"
        wis_raw = 75
    else:
        zone = "low_enhancement_potential"
        wis_raw = 50

    return ComputeResult(
        output_type=OutputType.SCORE,
        value=wis_raw / 100.0,
        unit="wis_normalized",
        zone=zone,
        confidence=0.3,
        details={"unisensory_strength": unisensory_strength_avg}
    )


# =============================================================================
# EXPORT REGISTRY
# =============================================================================

TEMPLATE_COMPUTE_FUNCTIONS = {
    # Batch 1
    "VF3": compute_vf3_ceiling_height,
    "L1": compute_l1_luminance_contrast,
    "L2": compute_l2_circadian_medi,
    "L3": compute_l3_daylight_composite,
    "CREA2": compute_crea2_processing_style,
    "MAT1": compute_mat1_ct_afferent,
    "MAT2": compute_mat2_thermal_adaptive,
    "MAT4": compute_mat4_material_convergence,
    "SOC2": compute_soc2_privacy_encounter,
    "SC1": compute_sc1_spatial_integration,
    "SC4": compute_sc4_wayfinding_social,
    "VIEW1": compute_view1_vqi,
    
    # Batch 2
    "L4": compute_l4_cct_temporal,
    "L5": compute_l5_dynamic_light,
    "MAT3": compute_mat3_material_identity,
    "MAT5": compute_mat5_material_cultural,
    "TP1": compute_tp1_motor_pe,
    "TP2": compute_tp2_threshold_boundary,
    "TP3": compute_tp3_temporal_rhythm,
    "TP4": compute_tp4_temporal_hierarchy,
    "SOC1": compute_soc1_proxemic_pe,
    "SOC3": compute_soc3_territorial,
    "CREA1": compute_crea1_creative_network,
    "CREA3": compute_crea3_incubation,
    "CREA4": compute_crea4_collaborative,
    "SC2": compute_sc2_isovist,
    "SC3": compute_sc3_promenade,
    "COL1": compute_col1_chromatic_pe,
    "COL2": compute_col2_color_harmony,
    "VF1": compute_vf1_contour_curvature,
    "VF2": compute_vf2_visual_rhythm,
    "OLF1": compute_olf1_olfactory_pe,

    # Batch 4 (Residuals)
    "T1": compute_t1_temporal_spectral_match,
    "T2": compute_t2_prospect_refuge_residual,
    "T5": compute_t5_enclosure_threat_residual,
    "T8": compute_t8_neural_grid_constraint,
    "T11": compute_t11_exploration_mode,
    "T15": compute_t15_personal_control,
    "T16": compute_t16_restoration_timecourse,
    "T20": compute_t20_convergent_performance,
    "T22": compute_t22_rapid_gist,
    "T24": compute_t24_theta_sequence,
    "T27": compute_t27_non_thermal_interoception,
    "T32": compute_t32_subcortical_auditory,
    "T33": compute_t33_reverberation_space,
    "T38": compute_t38_hierarchical_control_depth,
    "T40": compute_t40_msi_inverse_effectiveness,

    # Batch 3
    "T4": compute_t4_attention_demand,
    "T6": compute_t6_cortisol_cascade,
    "T7": compute_t7_allostatic_anticipation,
    "T10": compute_t10_sleep_consolidation,
    "T14": compute_t14_navigation_stress_loop,
    "T17": compute_t17_dopaminergic_novelty,
    "T18": compute_t18_vestibular_spatial,
    "T23": compute_t23_context_memory,
    "T28": compute_t28_cognitive_offloading,
}


def get_compute_function(template_id: str):
    """Get the compute function for a given template ID."""
    return TEMPLATE_COMPUTE_FUNCTIONS.get(template_id)


def list_implemented_templates() -> List[str]:
    """List IDs of all implemented templates."""
    return sorted(list(TEMPLATE_COMPUTE_FUNCTIONS.keys()))

