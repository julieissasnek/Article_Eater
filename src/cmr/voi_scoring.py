"""Value-of-information scoring utilities (Sprint 11 Task 11.20)."""

from __future__ import annotations

from typing import Any


_WELL_CALIBRATED = {
    "supported",
    "established",
    "substantial",
    "mature",
    "high",
}


def _is_well_calibrated(maturity: Any) -> bool:
    if isinstance(maturity, list):
        return any(_is_well_calibrated(item) for item in maturity)
    return str(maturity or "").strip().lower() in _WELL_CALIBRATED


def _effect_size_abs(finding: dict[str, Any]) -> float:
    raw = finding.get("effect_size")
    if raw is None and isinstance(finding.get("claim"), dict):
        raw = finding["claim"].get("effect_size")
    try:
        return abs(float(raw or 0.0))
    except (TypeError, ValueError):
        return 0.0


def _score_single_finding(finding: dict[str, Any]) -> float:
    assessment = str(
        finding.get("assessment")
        or finding.get("category")
        or finding.get("type")
        or "gap"
    ).lower()
    calibrated = _is_well_calibrated(
        finding.get("template_maturity")
        or finding.get("maturity")
        or finding.get("template_maturities")
    )
    effect_size = _effect_size_abs(finding)

    if assessment == "contradiction":
        return 1.0 if calibrated else 0.7
    if assessment == "gap":
        return 0.8 if effect_size > 0.5 else 0.4
    if assessment == "extension":
        return 0.6
    if assessment == "confirmation":
        return 0.2 if calibrated else 0.5
    return 0.4


def score_voi(findings: list[dict]) -> list[dict]:
    """
    Score and sort findings by VOI (highest first).

    Returns a new list where each finding has:
      - voi_score: float in [0, 1]
      - voi_bucket: "high" | "medium" | "low"
    """
    scored: list[dict[str, Any]] = []
    for finding in findings:
        score = max(0.0, min(1.0, _score_single_finding(finding)))
        if score >= 0.8:
            bucket = "high"
        elif score >= 0.5:
            bucket = "medium"
        else:
            bucket = "low"
        scored.append({**finding, "voi_score": score, "voi_bucket": bucket})

    scored.sort(key=lambda item: float(item.get("voi_score", 0.0)), reverse=True)
    return scored


def aggregate_paper_voi(findings: list[dict]) -> dict[str, Any]:
    """Compute aggregate paper-level VOI summary."""
    scored = score_voi(findings)
    if not scored:
        return {
            "aggregate_voi": 0.0,
            "expected_information_gain": "low",
            "high_value_findings": 0,
            "n_findings": 0,
        }

    mean_score = sum(float(item["voi_score"]) for item in scored) / len(scored)
    high_value = sum(1 for item in scored if float(item["voi_score"]) >= 0.8)

    if mean_score >= 0.8:
        eig = "high"
    elif mean_score >= 0.5:
        eig = "medium"
    else:
        eig = "low"

    return {
        "aggregate_voi": round(mean_score, 3),
        "expected_information_gain": eig,
        "high_value_findings": high_value,
        "n_findings": len(scored),
    }

