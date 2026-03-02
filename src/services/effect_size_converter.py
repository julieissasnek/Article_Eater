"""
effect_size_converter.py — Effect Size Standardization
========================================================

Expert Panel Guidance:
  - Research Methodologist (#18): "Need r→d, OR→d, η²→d conversion before aggregation"
  - Data Engineer (#4): "Effect sizes are sparse and on different scales"

Converts between common effect size metrics:
  - Cohen's d ↔ Pearson's r
  - η² → d
  - OR → d (log odds ratio)
  - f² → d
  - Hedges' g → d

All conversions output Cohen's d as the canonical scale.
"""

import math
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class StandardizedEffectSize:
    """A standardized effect size in Cohen's d."""
    d: float                     # Cohen's d (canonical)
    original_value: float        # Original value
    original_metric: str         # Original metric name
    conversion_method: str       # How it was converted
    confidence: float = 1.0      # Confidence in conversion (0-1)

    @property
    def r(self) -> float:
        """Convert to Pearson's r."""
        return self.d / math.sqrt(self.d ** 2 + 4)

    @property
    def interpretation(self) -> str:
        """Cohen's magnitude interpretation."""
        abs_d = abs(self.d)
        if abs_d < 0.2:
            return "negligible"
        elif abs_d < 0.5:
            return "small"
        elif abs_d < 0.8:
            return "medium"
        else:
            return "large"


def detect_metric(raw_text: str) -> Optional[str]:
    """
    Detect which effect size metric a raw string represents.
    
    Examples:
        "0.42" → None (ambiguous)
        "d = 0.42" → "d"
        "r = 0.31" → "r"
        "η² = 0.15" → "eta_squared"
        "OR = 2.1" → "odds_ratio"
        "f² = 0.10" → "f_squared"
        "g = 0.55" → "hedges_g"
    """
    import re
    text = raw_text.strip().lower()

    patterns = [
        (r"(?:cohen'?s?\s*)?d\s*[=:]\s*", "d"),
        (r"(?:hedges'?\s*)?g\s*[=:]\s*", "hedges_g"),
        (r"(?:pearson'?s?\s*)?r\s*[=:]\s*", "r"),
        (r"(?:eta|η)\s*(?:²|2|sq)\s*[=:]\s*", "eta_squared"),
        (r"(?:partial\s+)?(?:eta|η)\s*(?:²|2)\s*[=:]\s*", "partial_eta_squared"),
        (r"(?:odds?\s*ratio|or)\s*[=:]\s*", "odds_ratio"),
        (r"f\s*(?:²|2)\s*[=:]\s*", "f_squared"),
        (r"r\s*(?:²|2)\s*[=:]\s*", "r_squared"),
        (r"(?:cliff'?s?\s*)?delta\s*[=:]\s*", "cliffs_delta"),
    ]

    for pattern, metric in patterns:
        if re.search(pattern, text):
            return metric

    return None


def r_to_d(r: float) -> float:
    """Convert Pearson's r to Cohen's d."""
    if abs(r) >= 1.0:
        return float('inf') if r > 0 else float('-inf')
    return 2 * r / math.sqrt(1 - r ** 2)


def d_to_r(d: float) -> float:
    """Convert Cohen's d to Pearson's r."""
    return d / math.sqrt(d ** 2 + 4)


def eta_squared_to_d(eta_sq: float) -> float:
    """Convert η² to Cohen's d."""
    if eta_sq >= 1.0 or eta_sq <= 0.0:
        return 0.0
    return 2 * math.sqrt(eta_sq / (1 - eta_sq))


def odds_ratio_to_d(odds_ratio: float) -> float:
    """Convert odds ratio to Cohen's d using Hasselblad-Hedges method."""
    if odds_ratio <= 0:
        return 0.0
    return math.log(odds_ratio) * math.sqrt(3) / math.pi


def f_squared_to_d(f_sq: float) -> float:
    """Convert Cohen's f² to d."""
    return 2 * math.sqrt(f_sq)


def r_squared_to_d(r_sq: float) -> float:
    """Convert R² to Cohen's d."""
    if r_sq >= 1.0 or r_sq <= 0.0:
        return 0.0
    r = math.sqrt(r_sq)
    return r_to_d(r)


def hedges_g_to_d(g: float, n: Optional[int] = None) -> float:
    """
    Convert Hedges' g to Cohen's d.
    
    If n is provided, applies the exact correction factor.
    Otherwise, g ≈ d for large samples.
    """
    if n and n > 3:
        # J correction factor: g = d * J, so d = g / J
        j = 1 - 3 / (4 * (n - 1) - 1)
        return g / j if j > 0 else g
    return g  # g ≈ d for large n


def standardize(
    value: float,
    metric: str,
    n: Optional[int] = None,
) -> StandardizedEffectSize:
    """
    Convert any recognized effect size metric to standardized Cohen's d.

    Args:
        value: The effect size value
        metric: The metric type (d, r, eta_squared, odds_ratio, f_squared, hedges_g, r_squared)
        n: Optional sample size for corrections

    Returns:
        StandardizedEffectSize with d as canonical
    """
    converters = {
        "d": lambda v: v,
        "r": r_to_d,
        "eta_squared": eta_squared_to_d,
        "partial_eta_squared": eta_squared_to_d,
        "odds_ratio": odds_ratio_to_d,
        "f_squared": f_squared_to_d,
        "r_squared": r_squared_to_d,
        "hedges_g": lambda v: hedges_g_to_d(v, n),
    }

    confidence_map = {
        "d": 1.0,
        "hedges_g": 0.95,
        "r": 0.90,
        "eta_squared": 0.85,
        "partial_eta_squared": 0.80,
        "f_squared": 0.85,
        "r_squared": 0.80,
        "odds_ratio": 0.75,
    }

    converter = converters.get(metric)
    if converter is None:
        # Unknown metric — assume it's d-like
        return StandardizedEffectSize(
            d=value,
            original_value=value,
            original_metric=metric or "unknown",
            conversion_method="assumed_d",
            confidence=0.5,
        )

    d_value = converter(value)

    return StandardizedEffectSize(
        d=d_value,
        original_value=value,
        original_metric=metric,
        conversion_method=f"{metric}_to_d",
        confidence=confidence_map.get(metric, 0.5),
    )


def standardize_from_text(
    raw_text: str,
    value: float,
    n: Optional[int] = None,
) -> StandardizedEffectSize:
    """
    Auto-detect metric from text description and standardize.

    Args:
        raw_text: Text describing the effect size (e.g., "η² = 0.15")
        value: The numeric value
        n: Optional sample size

    Returns:
        StandardizedEffectSize
    """
    metric = detect_metric(raw_text) or "d"
    return standardize(value, metric, n)
