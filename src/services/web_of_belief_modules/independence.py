"""Independence/diversity scoring utilities (ARCH-3b)."""

from __future__ import annotations

from collections import Counter
from typing import Iterable, Mapping


def _normalized_diversity(values: list[str]) -> float:
    if not values:
        return 0.0
    cleaned = [v.strip().lower() for v in values if v and v.strip()]
    if not cleaned:
        return 0.0
    unique = len(set(cleaned))
    return unique / len(cleaned)


def _cluster_penalty(values: list[str]) -> float:
    if not values:
        return 1.0
    cleaned = [v.strip().lower() for v in values if v and v.strip()]
    if not cleaned:
        return 1.0
    largest_cluster = max(Counter(cleaned).values())
    # 1.0 means perfectly independent, 0.0 means all from one cluster.
    return 1.0 - (largest_cluster / len(cleaned))


def compute_independence_score(records: Iterable[Mapping[str, str | None]]) -> dict[str, float]:
    """Score evidential independence via lab × method × population diversity."""
    labs: list[str] = []
    methods: list[str] = []
    populations: list[str] = []

    total = 0
    for row in records:
        total += 1
        labs.append(str(row.get("lab") or ""))
        methods.append(str(row.get("method") or ""))
        populations.append(str(row.get("population") or ""))

    lab_div = _normalized_diversity(labs)
    method_div = _normalized_diversity(methods)
    pop_div = _normalized_diversity(populations)

    lab_cluster = _cluster_penalty(labs)
    method_cluster = _cluster_penalty(methods)
    pop_cluster = _cluster_penalty(populations)

    # Weighted mixture: diversity breadth + anti-clustering.
    score = (
        0.2 * lab_div + 0.2 * method_div + 0.2 * pop_div
        + 0.2 * lab_cluster + 0.1 * method_cluster + 0.1 * pop_cluster
    )

    return {
        "n_records": float(total),
        "lab_diversity": lab_div,
        "method_diversity": method_div,
        "population_diversity": pop_div,
        "lab_cluster_penalty": lab_cluster,
        "method_cluster_penalty": method_cluster,
        "population_cluster_penalty": pop_cluster,
        "independence_score": max(0.0, min(1.0, score)),
    }
