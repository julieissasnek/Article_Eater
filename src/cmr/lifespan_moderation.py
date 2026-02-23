"""
Lifespan Moderation Module (Sprint 11 Task 11.3).

Provides utilities to extract occupant age and apply lifespan moderation
to template computations.

Per AGE-I and DEV-I panels:
- Children (age < 25): Higher PE sensitivity (DEV-I U-curve)
- Adults 25-50: Reference band (multiplier 1.0)
- Elderly (age > 50): Higher PE sensitivity (AGE-I multiplier)
"""

from __future__ import annotations

import inspect
from typing import Any, Dict, Optional

from src.cmr.template_computations import (
    get_compute_function,
    get_lifespan_multiplier,
    ComputeResult,
)


# Zone-to-WIS mapping for templates that return zone classifications
# Maps zone strings to approximate WIS scores based on PE semantics
ZONE_TO_WIS: Dict[str, float] = {
    # Negative/aversive zones (WIS 15-35)
    "confinement": 25.0,
    "extreme_low": 15.0,
    "extreme_high": 15.0,
    "aversive": 20.0,
    "severely_deficient": 15.0,
    "deficient": 30.0,
    "insufficient": 35.0,
    "too_low": 30.0,
    "too_high": 30.0,
    "below_threshold": 35.0,
    "poor": 25.0,
    "low": 30.0,
    "crowded": 25.0,
    "no_privacy": 20.0,
    "exposed": 25.0,

    # Neutral zones (WIS 45-55)
    "neutral": 50.0,
    "standard": 50.0,
    "baseline": 50.0,
    "moderate": 50.0,
    "adequate": 55.0,
    "acceptable": 50.0,
    "mixed": 50.0,

    # Positive zones (WIS 60-80)
    "good": 65.0,
    "optimal": 75.0,
    "liberating": 70.0,
    "expansive": 80.0,
    "high": 70.0,
    "sufficient": 65.0,
    "above_threshold": 70.0,
    "comfortable": 70.0,
    "private": 75.0,
    "restorative": 75.0,
    "natural": 75.0,
    "biophilic": 80.0,
    "high_quality": 80.0,
    "excellent": 85.0,

    # Special zones
    "awe": 65.0,  # Expansive but less target-fit than liberating proportions
    "overwhelming": 55.0,  # Too much of a good thing
    "high_enhancement_potential": 75.0,
    "low_enhancement_potential": 50.0,
}


def extract_occupant_age(occupant_profile: Dict[str, Any]) -> Optional[int]:
    """
    Extract age from occupant_profile dict.

    Accepts various key formats:
    - 'age': direct integer
    - 'occupant_age': direct integer
    - 'age_years': direct integer

    Returns None if not found or invalid.
    """
    for key in ['age', 'occupant_age', 'age_years']:
        if key in occupant_profile:
            try:
                return int(occupant_profile[key])
            except (ValueError, TypeError):
                continue
    return None


def call_compute_with_age(
    template_id: str,
    measured_features: Dict[str, Any],
    occupant_profile: Dict[str, Any],
) -> Optional[ComputeResult]:
    """
    Call a template's compute function with proper age handling.

    This function:
    1. Looks up the compute function for the template
    2. Extracts age from occupant_profile
    3. Maps measured_features to the function's parameters
    4. Calls the function with occupant_age passed through

    Returns None if no compute function exists for the template.
    """
    compute_fn = get_compute_function(template_id)
    if compute_fn is None:
        return None

    # Extract age
    age = extract_occupant_age(occupant_profile)

    # Get function signature to know what parameters it accepts
    sig = inspect.signature(compute_fn)
    params = sig.parameters

    # Build kwargs for the function call
    kwargs: Dict[str, Any] = {}

    for param_name, param in params.items():
        # Always pass occupant_age if the function accepts it
        if param_name == 'occupant_age':
            kwargs['occupant_age'] = age
            continue

        # Try to get the value from measured_features
        if param_name in measured_features:
            kwargs[param_name] = measured_features[param_name]
        elif param.default is not inspect.Parameter.empty:
            # Has a default, will use it
            pass
        else:
            # Required parameter without value - can't call
            return None

    try:
        return compute_fn(**kwargs)
    except Exception:
        return None


def get_age_adjustment_factor(
    base_wis: float,
    age: Optional[int],
    pe_direction: str = "neutral",
) -> float:
    """
    Calculate age-adjusted WIS based on lifespan sensitivity.

    For positive PE effects (good environment features):
    - Higher sensitivity (children/elderly) -> higher WIS (more benefit)

    For negative PE effects (bad environment features):
    - Higher sensitivity (children/elderly) -> lower WIS (more harm)

    Args:
        base_wis: Base WIS score (0-100)
        age: Occupant age (None = use reference band)
        pe_direction: 'positive', 'negative', or 'neutral'

    Returns:
        Age-adjusted WIS score
    """
    multiplier = get_lifespan_multiplier(age)

    if pe_direction == "neutral" or multiplier == 1.0:
        return base_wis

    # Distance from neutral (50)
    delta = base_wis - 50.0

    if pe_direction == "positive" and delta > 0:
        # Good feature: higher sensitivity = more benefit
        adjusted_delta = delta * multiplier
    elif pe_direction == "negative" and delta < 0:
        # Bad feature: higher sensitivity = more harm
        adjusted_delta = delta * multiplier
    else:
        # Mixed or neutral
        adjusted_delta = delta

    # Clamp to valid range
    return max(0.0, min(100.0, 50.0 + adjusted_delta))


def compute_template_with_lifespan(
    template_id: str,
    measured_features: Dict[str, Any],
    occupant_profile: Dict[str, Any],
    feature_mapping: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Full computation wrapper that handles feature mapping and lifespan moderation.

    Args:
        template_id: Template identifier (e.g., 'VF3', 'L2')
        measured_features: Raw measured features from building evaluation
        occupant_profile: Occupant profile including age
        feature_mapping: Optional mapping from measured_feature keys to compute function params

    Returns:
        Dict with computed result, WIS, and metadata. If computation fails,
        returns a placeholder with needs_computation=True.
    """
    # Apply feature mapping if provided
    if feature_mapping:
        mapped_features = {}
        for target_key, source_key in feature_mapping.items():
            if source_key in measured_features:
                mapped_features[target_key] = measured_features[source_key]
        # Merge with original (mapped takes precedence)
        effective_features = {**measured_features, **mapped_features}
    else:
        effective_features = measured_features

    # Try to call the compute function
    result = call_compute_with_age(template_id, effective_features, occupant_profile)

    if result is None:
        # No compute function or missing inputs
        return {
            "template": template_id,
            "wis": 50.0,
            "needs_computation": True,
            "lifespan_applied": False,
            "age": extract_occupant_age(occupant_profile),
        }

    # Convert ComputeResult to dict
    result_dict = result.to_dict()

    # Extract WIS from result based on output_type
    output_type = result_dict.get('output_type', '')
    zone = result_dict.get('zone', '')
    details = result_dict.get('details', {})
    raw_value = float(result_dict.get('value', 0.0))

    # Priority 1: If wis_raw is explicitly provided, use it
    if 'wis_raw' in details:
        wis = float(details['wis_raw'])
    # Priority 2: For goldilocks zones, convert zone to WIS
    elif output_type == 'goldilocks_zone' and zone:
        wis = ZONE_TO_WIS.get(zone.lower(), 50.0)
    # Priority 3: For threshold checks, use zone mapping
    elif output_type == 'threshold_check' and zone:
        wis = ZONE_TO_WIS.get(zone.lower(), 50.0)
    # Priority 4: For score outputs - check if value is WIS-scale or normalized
    elif output_type == 'score':
        # If value is clearly WIS-scale (>1.0 and <=100), use directly
        if raw_value > 1.0 and raw_value <= 100.0:
            wis = raw_value
        # If value is normalized (0-1) AND zone is provided, prefer zone
        elif 0.0 <= raw_value <= 1.0 and zone:
            wis = ZONE_TO_WIS.get(zone.lower(), raw_value * 100.0)
        # Otherwise scale normalized value
        elif 0.0 <= raw_value <= 1.0:
            wis = raw_value * 100.0
        else:
            wis = 50.0
    # Priority 5: For matrix lookups with zone, use zone
    elif output_type == 'matrix_lookup' and zone:
        wis = ZONE_TO_WIS.get(zone.lower(), 50.0)
    # Priority 6: If zone is provided without specific output_type
    elif zone:
        wis = ZONE_TO_WIS.get(zone.lower(), 50.0)
    # Fallback: Use raw value if in WIS range, else default to 50
    elif 0.0 <= raw_value <= 100.0:
        wis = raw_value
    else:
        wis = 50.0

    # Clamp base WIS to valid range
    base_wis = max(0.0, min(100.0, wis))

    # Apply lifespan moderation: age affects sensitivity to environmental features
    # Determine PE direction from the base WIS relative to neutral (50)
    age = extract_occupant_age(occupant_profile)
    lifespan_multiplier = result_dict.get('details', {}).get('lifespan_multiplier', 1.0)

    if base_wis > 55:
        pe_direction = "positive"  # Good environmental feature
    elif base_wis < 45:
        pe_direction = "negative"  # Bad environmental feature
    else:
        pe_direction = "neutral"   # Near-neutral feature

    # Apply age adjustment - children and elderly are more sensitive
    adjusted_wis = get_age_adjustment_factor(base_wis, age, pe_direction)

    return {
        "template": template_id,
        "wis": adjusted_wis,
        "wis_before_age_adjustment": base_wis,
        "raw_output": result_dict,
        "needs_computation": False,
        "lifespan_applied": True,
        "age": age,
        "lifespan_multiplier": lifespan_multiplier,
        "pe_direction": pe_direction,
    }


# Feature mapping presets for common templates
FEATURE_MAPPINGS = {
    "VF3": {
        "ceiling_height_m": "ceiling_height_m",
        "floor_area_m2": "floor_area_m2",
    },
    "L1": {
        "illuminance_lux": "illuminance_lux",
        "cv_luminance": "cv_luminance",
    },
    "L2": {
        "m_edi_lux": "m_edi_lux",
    },
    "SOC2": {
        "acoustic_isolation_db": "acoustic_isolation_db",
        "visual_privacy_index": "visual_privacy_index",
        "density_m2_per_person": "density_m2_per_person",
    },
    "VIEW1": {
        "view_content": "view_content",
        "view_layers": "view_layers",
        "view_sky_fraction": "view_sky_fraction",
        "has_nature_view": "has_nature_view",
        "view_distance_m": "view_distance_m",
    },
    "CREA2": {
        "ambient_noise_dba": "ambient_noise_dba",
        "ceiling_height_m": "ceiling_height_m",
        "illuminance_lux": "illuminance_lux",
    },
}


def get_feature_mapping(template_id: str) -> Dict[str, str]:
    """Get the feature mapping preset for a template, or empty dict if none."""
    return FEATURE_MAPPINGS.get(template_id, {})
