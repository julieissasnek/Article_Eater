"""Severity scoring utilities for evidential claims (ARCH-6b)."""

from __future__ import annotations

import math
from typing import Optional


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def compute_severity_score(
    *,
    credence: float,
    uncertainty: float,
    sample_n: Optional[int] = None,
    effect_size: Optional[float] = None,
    p_value: Optional[float] = None,
    alpha: float = 0.05,
) -> float:
    """Approximate Mayo-style severity: stronger tests + robust signal => higher severity.

    This is intentionally conservative and bounded to [0, 1].
    """
    credence = _clamp(float(credence))
    uncertainty = _clamp(float(uncertainty))

    signal_strength = _clamp(credence * (1.0 - uncertainty))

    n_component = 0.0
    if sample_n is not None and sample_n > 0:
        n_component = _clamp(math.log10(sample_n + 1) / math.log10(1001))

    effect_component = 0.0
    if effect_size is not None:
        effect_component = _clamp(abs(float(effect_size)) / 0.8)

    p_component = 0.5
    if p_value is not None and p_value > 0:
        p = float(p_value)
        # Lower p-values provide stronger severe testing signal.
        p_component = _clamp(1.0 - (min(p, alpha * 4) / (alpha * 4)))

    test_strength = (
        0.4 * n_component
        + 0.35 * effect_component
        + 0.25 * p_component
    )
    return _clamp(0.5 * signal_strength + 0.5 * test_strength)
