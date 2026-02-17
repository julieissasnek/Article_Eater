"""Feature-to-template input mapping utilities for CMR building evaluation."""

from __future__ import annotations

import inspect
import math
from typing import Any, Callable, Dict, Iterable, Optional

from src.cmr.template_computations import get_compute_function, list_implemented_templates


# Standard flat feature keys expected from building assessment inputs.
STANDARD_BUILDING_FEATURES = {
    "ceiling_height_m",
    "floor_area_m2",
    "illuminance_lux",
    "ambient_noise_dba",
    "window_area_ratio",
    "primary_material",
    "secondary_material",
    "has_nature_view",
    "rt60_seconds",
    "view_content",
    "privacy_visual",
    "privacy_acoustic",
    "density_m2_per_person",
    "operative_temp_c",
    "running_mean_outdoor_c",
    "surface_effusivity",
    "contact_temperature_c",
    "cct_kelvin",
    "time_of_day",
    "view_layers",
    "nature_content_ratio",
    "luminance_contrast_cv",
    "spatial_integration_score",
    "layout_legibility",
    "depth_from_entrance",
    "has_vertical_transitions",
    "atrium_present",
    "visual_connectivity",
    "edge_richness",
    "expected_encounter_context",
    "shared_area_ratio",
    "phone_booths_per_worker",
    "quiet_rooms_per_worker",
    "visual_privacy_score",
    "acoustic_privacy_stc",
    "surface_type",
    "step_height_mm",
    "coefficient_of_friction",
    "calibration_context",
    "context_type",
}


# Canonical mapping: template function arg -> measured feature key.
FEATURE_TO_TEMPLATE_INPUT: Dict[str, Dict[str, str]] = {
    "VF3": {
        "ceiling_height_m": "ceiling_height_m",
        "floor_area_m2": "floor_area_m2",
    },
    "L1": {
        "cv_luminance": "luminance_contrast_cv",
    },
    "L2": {
        "medi_lux": "illuminance_lux",
        "exposure_duration_hours": "daylight_exposure_hours",
        "time_of_day": "time_of_day",
    },
    "L3": {
        "circadian_score": "l2_score",
        "view_score": "view_score",
        "luminance_contrast_score": "l1_score",
        "cct_score": "l4_score",
        "dynamic_variation_score": "l5_score",
    },
    "L4": {
        "cct_kelvin": "cct_kelvin",
        "time_of_day": "time_of_day",
        "context_type": "context_type",
    },
    "L5": {
        "has_daylight_variation": "has_daylight_variation",
        "has_designed_dynamics": "has_designed_dynamics",
        "static_exposure_hours": "static_exposure_hours",
        "change_rate_hz": "change_rate_hz",
    },
    "CREA2": {
        "noise_db": "ambient_noise_dba",
        "ambient_lux": "illuminance_lux",
        "baseline_creativity": "baseline_creativity",
    },
    "MAT1": {
        "surface_effusivity": "surface_effusivity",
        "contact_temperature_c": "contact_temperature_c",
        "climate": "climate_context",
    },
    "MAT2": {
        "operative_temperature_c": "operative_temp_c",
        "running_mean_outdoor_c": "running_mean_outdoor_c",
        "ventilation_type": "ventilation_type",
    },
    "MAT4": {
        "material_type": "primary_material",
        "surface_ratio": "natural_material_ratio",
    },
    "SOC2": {
        "shared_area_ratio": "shared_area_ratio",
        "phone_booths_per_worker": "phone_booths_per_worker",
        "quiet_rooms_per_worker": "quiet_rooms_per_worker",
        "visual_privacy_score": "visual_privacy_score",
        "acoustic_privacy_stc": "acoustic_privacy_stc",
    },
    "SC1": {
        "integration_normalized": "spatial_integration_score",
        "intelligibility": "layout_legibility",
        "depth_from_entrance": "depth_from_entrance",
        "has_vertical_transitions": "has_vertical_transitions",
        "atrium_present": "atrium_present",
    },
    "SC4": {
        "integration_normalized": "spatial_integration_score",
        "visual_connectivity": "visual_connectivity",
        "edge_richness": "edge_richness",
        "expected_encounter_context": "expected_encounter_context",
    },
    "VIEW1": {
        "view_area_ratio": "window_area_ratio",
        "view_layers": "view_layers",
        "nature_content_ratio": "nature_content_ratio",
        "dynamic_content": "dynamic_content",
    },
    "TP1": {
        "surface_type": "surface_type",
        "step_height_mm": "step_height_mm",
        "coefficient_of_friction": "coefficient_of_friction",
    },
}


# Template defaults when no direct building feature is provided.
TEMPLATE_INPUT_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "L1": {"cv_luminance": 1.0},
    "L2": {"exposure_duration_hours": 2.0, "time_of_day": "morning"},
    "L4": {"cct_kelvin": 4000.0, "time_of_day": "morning", "context_type": "office"},
    "L5": {
        "has_daylight_variation": True,
        "has_designed_dynamics": False,
        "static_exposure_hours": 8.0,
        "change_rate_hz": 0.2,
    },
    "CREA2": {"baseline_creativity": "medium"},
    "MAT1": {"climate": "temperate"},
    "MAT2": {"running_mean_outdoor_c": 20.0, "ventilation_type": "mixed"},
    "MAT4": {"surface_ratio": 0.3},
    "SOC2": {
        "shared_area_ratio": 0.5,
        "phone_booths_per_worker": 0.10,
        "quiet_rooms_per_worker": 0.04,
        "visual_privacy_score": 0.5,
        "acoustic_privacy_stc": 40.0,
    },
    "SC1": {
        "integration_normalized": 0.6,
        "intelligibility": 0.6,
        "depth_from_entrance": 3,
        "has_vertical_transitions": False,
        "atrium_present": False,
    },
    "SC4": {
        "integration_normalized": 0.6,
        "visual_connectivity": 0.5,
        "edge_richness": 0.5,
        "expected_encounter_context": "work",
    },
    "VIEW1": {
        "view_layers": 2,
        "nature_content_ratio": 0.5,
        "dynamic_content": True,
    },
    "TP1": {
        "surface_type": "level",
        "coefficient_of_friction": 0.6,
    },
}


def _derive_ceiling_rh(features: Dict[str, Any]) -> Optional[float]:
    height = features.get("ceiling_height_m")
    area = features.get("floor_area_m2")
    if height is None or area is None:
        return None
    if area <= 0:
        return None
    return float(height) / math.sqrt(float(area))


def _derive_view_type(features: Dict[str, Any]) -> str:
    content = str(features.get("view_content", "")).lower()
    if features.get("has_nature_view") or "tree" in content or "ocean" in content:
        return "nature"
    if content in {"none", "interior_only"}:
        return "none"
    return "urban"


def _derive_visual_privacy_score(features: Dict[str, Any]) -> Optional[float]:
    value = features.get("privacy_visual")
    if isinstance(value, (float, int)):
        return float(value)
    levels = {
        "none": 0.1,
        "low": 0.3,
        "moderate": 0.6,
        "high": 0.85,
    }
    if isinstance(value, str):
        return levels.get(value.lower())
    return None


def _derive_acoustic_privacy_stc(features: Dict[str, Any]) -> Optional[float]:
    value = features.get("privacy_acoustic")
    if isinstance(value, (float, int)):
        return float(value)
    levels = {
        "none": 28.0,
        "low": 34.0,
        "moderate": 42.0,
        "high": 50.0,
    }
    if isinstance(value, str):
        return levels.get(value.lower())
    return None


def _derive_shared_area_ratio(features: Dict[str, Any]) -> Optional[float]:
    if "shared_area_ratio" in features:
        try:
            return float(features["shared_area_ratio"])
        except (TypeError, ValueError):
            return None
    density = features.get("density_m2_per_person")
    if density is None:
        return None
    try:
        density_val = float(density)
    except (TypeError, ValueError):
        return None
    if density_val <= 0:
        return None
    return max(0.0, min(1.0, density_val / 20.0))


TEMPLATE_INPUT_DERIVERS: Dict[str, Dict[str, Callable[[Dict[str, Any]], Optional[Any]]]] = {
    "CREA2": {"ceiling_rh": _derive_ceiling_rh},
    "VIEW1": {"view_type": _derive_view_type},
    "SOC2": {
        "shared_area_ratio": _derive_shared_area_ratio,
        "visual_privacy_score": _derive_visual_privacy_score,
        "acoustic_privacy_stc": _derive_acoustic_privacy_stc,
    },
}


# Representative feature payload used for static coverage checks.
STANDARD_BUILDING_FEATURE_EXAMPLE: Dict[str, Any] = {
    "ceiling_height_m": 3.0,
    "floor_area_m2": 60.0,
    "illuminance_lux": 400.0,
    "ambient_noise_dba": 40.0,
    "window_area_ratio": 0.30,
    "primary_material": "timber",
    "secondary_material": "linoleum",
    "has_nature_view": True,
    "rt60_seconds": 0.4,
    "view_content": "playground_trees",
    "privacy_visual": "moderate",
    "privacy_acoustic": "moderate",
    "density_m2_per_person": 8.0,
    "operative_temp_c": 23.0,
    "running_mean_outdoor_c": 20.0,
    "surface_effusivity": 550.0,
    "contact_temperature_c": 31.0,
    "cct_kelvin": 4000.0,
    "time_of_day": "morning",
    "view_layers": 3,
    "nature_content_ratio": 0.8,
    "luminance_contrast_cv": 0.9,
    "spatial_integration_score": 0.7,
    "layout_legibility": 0.75,
    "depth_from_entrance": 2,
    "has_vertical_transitions": False,
    "atrium_present": False,
    "visual_connectivity": 0.5,
    "edge_richness": 0.6,
    "expected_encounter_context": "work",
    "shared_area_ratio": 0.48,
    "phone_booths_per_worker": 0.125,
    "quiet_rooms_per_worker": 0.04,
    "surface_type": "level",
    "step_height_mm": 170.0,
    "coefficient_of_friction": 0.62,
    "context_type": "school",
}


def get_required_template_args(template_id: str) -> list[str]:
    fn = get_compute_function(template_id)
    if fn is None:
        return []
    required: list[str] = []
    for param in inspect.signature(fn).parameters.values():
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue
        if param.default is inspect.Parameter.empty:
            required.append(param.name)
    return required


def map_features_to_template_inputs(
    template_id: str,
    measured_features: Dict[str, Any],
    occupant_profile: Optional[Dict[str, Any]] = None,
) -> tuple[Dict[str, Any], list[str]]:
    """
    Build kwargs for a template compute function from flat building features.

    Returns:
      (mapped_inputs, missing_required_args)
    """
    fn = get_compute_function(template_id)
    if fn is None:
        return {}, ["template_not_implemented"]

    arg_map = FEATURE_TO_TEMPLATE_INPUT.get(template_id, {})
    defaults = TEMPLATE_INPUT_DEFAULTS.get(template_id, {})
    derivers = TEMPLATE_INPUT_DERIVERS.get(template_id, {})

    mapped: Dict[str, Any] = {}
    missing: list[str] = []
    age = (occupant_profile or {}).get("age")

    for param in inspect.signature(fn).parameters.values():
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue
        name = param.name

        if name == "occupant_age":
            if age is not None:
                mapped[name] = age
            elif name in defaults:
                mapped[name] = defaults[name]
            elif param.default is inspect.Parameter.empty:
                missing.append(name)
            continue

        source_key = arg_map.get(name)
        if source_key and source_key in measured_features:
            mapped[name] = measured_features[source_key]
            continue

        if name in measured_features:
            mapped[name] = measured_features[name]
            continue

        derive_fn = derivers.get(name)
        if derive_fn is not None:
            derived = derive_fn(measured_features)
            if derived is not None:
                mapped[name] = derived
                continue

        if name in defaults:
            mapped[name] = defaults[name]
            continue

        if param.default is inspect.Parameter.empty:
            missing.append(name)

    return mapped, missing


def resolve_template_inputs(
    template_id: str,
    measured_features: Dict[str, Any],
    occupant_profile: Optional[Dict[str, Any]] = None,
) -> tuple[Dict[str, Any], list[str]]:
    """
    Compatibility wrapper used by building_eval step 2.

    Returns mapped kwargs and missing required args for a template.
    """
    return map_features_to_template_inputs(template_id, measured_features, occupant_profile)


def audit_feature_mapping_coverage(
    template_ids: Optional[Iterable[str]] = None,
    standard_feature_example: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Validate mapping coverage against a standard building feature payload.

    Returns dict with supported templates and templates that still have missing
    required inputs.
    """
    templates = list(template_ids) if template_ids is not None else list_implemented_templates()
    features = dict(standard_feature_example or STANDARD_BUILDING_FEATURE_EXAMPLE)
    profile = {"age": 35}

    missing_by_template: Dict[str, list[str]] = {}
    for template_id in templates:
        _, missing = map_features_to_template_inputs(template_id, features, profile)
        if missing:
            missing_by_template[template_id] = missing

    supported = [template for template in templates if template not in missing_by_template]
    return {
        "total_templates": len(templates),
        "supported_templates": supported,
        "supported_count": len(supported),
        "missing_by_template": missing_by_template,
    }


def resolve_template_inputs(
    template_id: str,
    measured_features: Dict[str, Any],
    occupant_profile: Optional[Dict[str, Any]] = None,
) -> tuple[Dict[str, Any], list[str]]:
    """Backward-compatible alias used by Sprint 11 orchestrator wiring."""
    return map_features_to_template_inputs(template_id, measured_features, occupant_profile)


def audit_feature_mapping(
    standard_feature_keys: Optional[set[str]] = None,
) -> Dict[str, Any]:
    """Backward-compatible audit schema used by Sprint 11 mapping tests."""
    if standard_feature_keys is None:
        coverage = audit_feature_mapping_coverage()
    else:
        constrained_example = {
            key: value
            for key, value in STANDARD_BUILDING_FEATURE_EXAMPLE.items()
            if key in standard_feature_keys
        }
        coverage = audit_feature_mapping_coverage(standard_feature_example=constrained_example)

    variadic_templates: list[str] = []
    for template_id in list_implemented_templates():
        fn = get_compute_function(template_id)
        if fn is None:
            continue
        for param in inspect.signature(fn).parameters.values():
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                variadic_templates.append(template_id)
                break

    return {
        "total_templates": coverage["total_templates"],
        "templates_with_full_required_mapping": coverage["supported_templates"],
        "templates_missing_required_inputs": coverage["missing_by_template"],
        "templates_with_variadic_signature": sorted(variadic_templates),
    }
