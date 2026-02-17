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
from typing import Any, Callable, Dict, Optional

from src.cmr.template_computations import (
    TEMPLATE_COMPUTE_FUNCTIONS,
    get_compute_function,
    get_lifespan_multiplier,
    ComputeResult,
)


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

    # Extract WIS from result
    # Different templates return WIS in different formats
    if 'wis_raw' in result_dict.get('details', {}):
        wis = float(result_dict['details']['wis_raw'])
    elif result_dict.get('output_type') == 'score':
        # Score type returns normalized 0-1, convert to 0-100
        wis = float(result_dict['value']) * 100.0
    else:
        # Default: value is the WIS
        wis = float(result_dict.get('value', 50.0))

    return {
        "template": template_id,
        "wis": wis,
        "raw_output": result_dict,
        "needs_computation": False,
        "lifespan_applied": True,
        "age": extract_occupant_age(occupant_profile),
        "lifespan_multiplier": result_dict.get('details', {}).get('lifespan_multiplier', 1.0),
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
