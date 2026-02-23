"""Effect size conversion utilities for Sprint D extraction remediation."""

from __future__ import annotations

import math
from statistics import NormalDist
from typing import Any

from src.cmr.wis import cohens_d_to_wis


_NORMAL = NormalDist()


def _normalize_stat_type(stat_type: str) -> str:
    normalized = (stat_type or "").strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "f": "f_value",
        "t": "t_value",
        "eta2": "eta_squared",
        "eta_sq": "eta_squared",
        "or": "odds_ratio",
        "d": "cohens_d",
    }
    return aliases.get(normalized, normalized)


def _validate_positive(name: str, value: int | float | None) -> float:
    if value is None:
        raise ValueError(f"{name} is required")
    as_float = float(value)
    if as_float <= 0:
        raise ValueError(f"{name} must be > 0")
    return as_float


def _estimate_n_total(n: int | None, n1: int | None, n2: int | None) -> int | None:
    if n is not None and n > 0:
        return int(n)
    if n1 is not None and n2 is not None and n1 > 0 and n2 > 0:
        return int(n1 + n2)
    return None


def _estimate_se(d: float, n_total: int | None, n1: int | None, n2: int | None) -> float | None:
    if n1 and n2 and (n1 + n2) > 2:
        numerator = n1 + n2
        return math.sqrt((numerator / (n1 * n2)) + (d * d) / (2 * (numerator - 2)))
    if n_total and n_total > 2:
        return math.sqrt((1 / n_total) + (d * d) / (2 * (n_total - 1)))
    return None


def _hedges_g(d: float, n_total: int | None) -> float | None:
    if not n_total or n_total <= 3:
        return None
    correction = 1 - (3 / (4 * n_total - 9))
    return d * correction


def to_cohens_d(
    value: float,
    stat_type: str,
    df1: int | None = None,
    df2: int | None = None,
    n: int | None = None,
    n1: int | None = None,
    n2: int | None = None,
) -> dict[str, Any]:
    """Convert common statistics to Cohen's d with uncertainty metadata."""
    if value is None:
        raise ValueError("value is required")
    value = float(value)

    stat = _normalize_stat_type(stat_type)
    assumptions: list[str] = []
    method = stat
    n_total = _estimate_n_total(n, n1, n2)

    if stat == "cohens_d":
        d = value
        method = "cohens_d_passthrough"
    elif stat == "t_value":
        if n1 and n2:
            _validate_positive("n1", n1)
            _validate_positive("n2", n2)
            d = value * math.sqrt((1 / n1) + (1 / n2))
            method = "t_to_d_unequal_groups"
            n_total = n1 + n2
        else:
            t_df = df2
            if t_df is None and n_total is not None and n_total > 2:
                t_df = n_total - 2
                assumptions.append("df inferred as n - 2 for two-group t-test.")
            if t_df is None:
                raise ValueError("t_value conversion requires df2 (t df) or n/n1+n2")
            d = 2 * value / math.sqrt(t_df)
            method = "t_to_d_equal_groups"
            if n_total is None and t_df > 0:
                n_total = int(t_df + 2)
    elif stat == "f_value":
        if df2 is None:
            raise ValueError("f_value conversion requires df2")
        if df1 is None:
            assumptions.append("df1 missing; assuming numerator df = 1.")
        elif int(df1) > 1:
            assumptions.append(
                "F-test has df1 > 1 (omnibus); d is an approximate directional effect."
            )
        d = 2 * math.sqrt(value / float(df2))
        method = "f_to_d_df1_one"
    elif stat == "r":
        if not -1 < value < 1:
            raise ValueError("r must be strictly between -1 and 1")
        d = (2 * value) / math.sqrt(1 - value * value)
        method = "r_to_d"
    elif stat == "eta_squared":
        if not 0 <= value < 1:
            raise ValueError("eta_squared must be in [0, 1)")
        if value == 1:
            raise ValueError("eta_squared of 1 cannot be converted to finite d")
        d = 2 * math.sqrt(value / (1 - value))
        method = "eta_squared_to_d"
    elif stat == "beta":
        if not -1 < value < 1:
            raise ValueError("beta must be strictly between -1 and 1 for this approximation")
        d = (2 * value) / math.sqrt(1 - value * value)
        assumptions.append(
            "Beta-to-d is approximate and assumes a simple standardized relation."
        )
        method = "beta_to_d_approx"
    elif stat == "odds_ratio":
        _validate_positive("odds_ratio", value)
        d = math.log(value) * (math.sqrt(3) / math.pi)
        method = "odds_ratio_to_d"
    elif stat == "p_value_only":
        p = value
        if not 0 < p < 1:
            raise ValueError("p_value_only must be in (0, 1)")
        if n_total is None:
            raise ValueError("p_value_only conversion requires n")
        z = _NORMAL.inv_cdf(1 - p / 2)
        d = 2 * z / math.sqrt(n_total)
        assumptions.append("Direction is unknown from p-value alone; returned d is magnitude only.")
        assumptions.append("p-value-only conversion is low confidence.")
        method = "p_to_z_to_d"
    else:
        raise ValueError(f"Unsupported stat_type: {stat_type}")

    if n_total and n_total < 20:
        assumptions.append("Small sample can inflate d; review Hedges' g.")

    se = _estimate_se(d, n_total, n1, n2)
    ci_lower = None
    ci_upper = None
    if se is not None:
        ci_lower = d - 1.96 * se
        ci_upper = d + 1.96 * se

    result = {
        "d": d,
        "se": se,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "method": method,
        "assumptions": assumptions,
        "hedges_g": _hedges_g(d, n_total),
    }
    return result


def to_wis(
    value: float,
    stat_type: str,
    df1: int | None = None,
    df2: int | None = None,
    n: int | None = None,
    n1: int | None = None,
    n2: int | None = None,
) -> dict[str, Any]:
    """Convert an effect statistic into a Within-study Information Score (WIS)."""
    effect = to_cohens_d(
        value=value,
        stat_type=stat_type,
        df1=df1,
        df2=df2,
        n=n,
        n1=n1,
        n2=n2,
    )
    wis = cohens_d_to_wis(effect["d"])
    return {
        "wis": wis,
        "d": effect["d"],
        "method": effect["method"],
        "assumptions": effect["assumptions"],
        "conversion": effect,
    }
