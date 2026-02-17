"""Input validation helpers for the building evaluation pipeline (Sprint 12 Task 12.11)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from src.cmr.feature_mapping import STANDARD_BUILDING_FEATURES, FEATURE_TO_TEMPLATE_INPUT


RANGE_CONFIG: Dict[str, Tuple[float, float, float, float]] = {
    "ceiling_height_m": (1.5, 30.0, 2.0, 6.0),
    "floor_area_m2": (1.0, 100000.0, 10.0, 1000.0),
    "illuminance_lux": (0.0, 200000.0, 100.0, 2000.0),
    "ambient_noise_dba": (0.0, 140.0, 30.0, 60.0),
    "occupant_age": (0.0, 120.0, 0.0, 120.0),
}


@dataclass
class ValidationResult:
    warnings: List[str]
    missing_features: List[str]
    templates_status: Dict[str, Dict[str, Any]]
    valid: bool


def _normalize_value(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _validate_range(key: str, value: float, config: Tuple[float, float, float, float]) -> List[str]:
    min_allowed, max_allowed, warn_min, warn_max = config
    warnings: List[str] = []
    if value < min_allowed or value > max_allowed:
        warnings.append(
            f"{key}={value} outside absolute range [{min_allowed}, {max_allowed}]."
        )
    elif value < warn_min or value > warn_max:
        warnings.append(
            f"{key}={value} is outside preferred band [{warn_min}, {warn_max}]."
        )
    return warnings


def validate_building_inputs(inputs: Dict[str, Any]) -> ValidationResult:
    warnings: List[str] = []
    missing: List[str] = []

    for feature in STANDARD_BUILDING_FEATURES:
        if feature not in inputs or inputs[feature] in {None, ""}:
            missing.append(feature)
            continue
        config = RANGE_CONFIG.get(feature)
        if config:
            numeric = _normalize_value(inputs[feature])
            if numeric is None:
                warnings.append(f"{feature} value '{inputs[feature]}' is not numeric.")
            else:
                warnings.extend(_validate_range(feature, numeric, config))

    template_status: Dict[str, Dict[str, Any]] = {}
    for template_id, mapping in FEATURE_TO_TEMPLATE_INPUT.items():
        required = list(mapping.values())
        missing_inputs = [feat for feat in set(required) if feat not in inputs]
        template_status[template_id] = {
            "can_activate": not missing_inputs,
            "missing_features": missing_inputs,
            "required_features": required,
        }
        if missing_inputs:
            warnings.append(
                f"Template {template_id} missing inputs: {', '.join(sorted(missing_inputs))}."
            )

    valid = not missing and not warnings
    return ValidationResult(
        warnings=warnings,
        missing_features=sorted(set(missing)),
        templates_status=template_status,
        valid=valid,
    )


def summarize_validation(result: ValidationResult) -> str:
    lines = []
    status = "VALID" if result.valid else "INVALID"
    lines.append(f"Input validation status: {status}")
    if result.missing_features:
        lines.append("Missing features: " + ", ".join(result.missing_features))
    if result.warnings:
        lines.append("Warnings:")
        lines.extend(f"  - {warning}" for warning in result.warnings)
    return "\n".join(lines)


__all__ = ["validate_building_inputs", "ValidationResult", "summarize_validation"]
