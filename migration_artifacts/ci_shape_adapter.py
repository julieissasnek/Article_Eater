"""
Auto-generated CI shape adapter.
Canonical contract section: enums.ConfidenceIntervalShape
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple


def ci_object_to_scalars(ci_obj: Optional[object]) -> Tuple[Optional[float], Optional[float]]:
    if ci_obj is None:
        return None, None
    if isinstance(ci_obj, dict):
        lower = ci_obj.get("ci_lower")
        upper = ci_obj.get("ci_upper")
        if lower is None and upper is None:
            return None, None
        if lower is None or upper is None:
            raise ValueError("CI object must contain both ci_lower and ci_upper.")
        return float(lower), float(upper)
    if isinstance(ci_obj, (list, tuple)):
        if len(ci_obj) != 2:
            raise ValueError("CI array must have exactly two elements.")
        return float(ci_obj[0]), float(ci_obj[1])
    raise TypeError(f"Unsupported CI object type: {type(ci_obj)!r}")


def scalars_to_ci_object(ci_lower: Optional[float], ci_upper: Optional[float]) -> Optional[Dict[str, float]]:
    if ci_lower is None and ci_upper is None:
        return None
    if ci_lower is None or ci_upper is None:
        raise ValueError("Both ci_lower and ci_upper are required, or both must be None.")
    return {"ci_lower": float(ci_lower), "ci_upper": float(ci_upper)}


def test_migration_lossless() -> None:
    obj = {"ci_lower": 0.11, "ci_upper": 0.93}
    lo, hi = ci_object_to_scalars(obj)
    assert (lo, hi) == (0.11, 0.93)
    assert scalars_to_ci_object(lo, hi) == obj

    lo2, hi2 = ci_object_to_scalars([0.25, 0.75])
    assert scalars_to_ci_object(lo2, hi2) == {"ci_lower": 0.25, "ci_upper": 0.75}


if __name__ == "__main__":
    test_migration_lossless()
    print("CI adapter self-test passed.")
