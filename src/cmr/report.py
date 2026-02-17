"""
CMR report generation utilities (Sprint 10 Task 3.3).
"""

from __future__ import annotations

from typing import Any


DOMAIN_PARAMETER_TARGETS = {
    "L": [
        {"parameter": "illuminance_lux", "target": "300-500 lux"},
        {"parameter": "luminance_contrast_cv", "target": "balanced contrast (CV <= 0.35)"},
    ],
    "MAT": [
        {"parameter": "operative_temp_c", "target": "within adaptive neutral +/-2C"},
        {"parameter": "surface_effusivity", "target": "avoid abrupt thermal shock"},
    ],
    "SC": [
        {"parameter": "wayfinding_cues_count", "target": ">= 3 clear channels"},
        {"parameter": "layout_legibility", "target": "high connectivity, low confusion"},
    ],
    "SOC": [
        {"parameter": "visual_privacy_index", "target": ">= 0.6 in focused zones"},
        {"parameter": "acoustic_isolation_db", "target": ">= 35 dB where privacy matters"},
    ],
    "VIEW": [
        {"parameter": "view_quality_index", "target": ">= 60"},
        {"parameter": "nature_view_exposure", "target": "daily direct visual access"},
    ],
}


def _verdict_for_score(score: float) -> str:
    if score >= 75.0:
        return "strong environmental support with mostly healthy domain performance"
    if score >= 55.0:
        return "mixed performance with targeted remediation opportunities"
    if score >= 40.0:
        return "fragile performance with multiple active deficits"
    return "high-risk profile requiring immediate design remediation"


def _confidence_bucket(confidence: float) -> str:
    if confidence >= 0.75:
        return "high"
    if confidence >= 0.5:
        return "moderate"
    return "low"


def _targets_for_domain(domain: str) -> list[dict[str, str]]:
    domain_upper = domain.upper()
    for prefix, targets in DOMAIN_PARAMETER_TARGETS.items():
        if domain_upper.startswith(prefix):
            return targets
    return [{"parameter": "domain_specific_inputs", "target": "collect missing Tier A/B measurements"}]


def _calibration_summary(evaluation_result: dict[str, Any]) -> tuple[int, int]:
    details = evaluation_result.get("template_details")
    if isinstance(details, list):
        empirical = 0
        expert = 0
        for item in details:
            if not isinstance(item, dict):
                continue
            status = str(item.get("calibration_status", "")).lower()
            if status in {"substantial", "partial", "supported", "established"}:
                empirical += 1
            elif status:
                expert += 1
        return empirical, expert

    breakdown = evaluation_result.get("calibration_breakdown")
    if isinstance(breakdown, dict):
        empirical = int(breakdown.get("empirical", 0))
        expert = int(breakdown.get("expert_estimate", 0))
        return empirical, expert

    # Fallback: infer using domain confidence as a proxy.
    empirical = 0
    expert = 0
    for row in evaluation_result.get("domain_scores", []):
        if not isinstance(row, dict):
            continue
        n_templates = int(row.get("n_templates", 1))
        if float(row.get("confidence", 0.0)) >= 0.5:
            empirical += n_templates
        else:
            expert += n_templates
    return empirical, expert


def _score_interval(
    score: float,
    *,
    lower: float | None = None,
    upper: float | None = None,
    confidence: float | None = None,
) -> tuple[float, float, float]:
    if lower is not None and upper is not None:
        lo = max(0.0, min(100.0, float(lower)))
        hi = max(0.0, min(100.0, float(upper)))
        if hi < lo:
            lo, hi = hi, lo
        return lo, hi, hi - lo

    conf = 0.5 if confidence is None else max(0.0, min(1.0, float(confidence)))
    half_width = (1.0 - conf) * 20.0
    lo = max(0.0, float(score) - half_width)
    hi = min(100.0, float(score) + half_width)
    return lo, hi, hi - lo


def generate_report(evaluation_result: dict) -> dict:
    """Generate a structured human-readable assessment report."""
    overall_wis = float(evaluation_result.get("overall_wis", 0.0))
    domain_scores = list(evaluation_result.get("domain_scores", []))
    data_gaps = list(evaluation_result.get("data_gaps", []))

    overall_confidence = float(
        evaluation_result.get(
            "overall_confidence",
            (sum(float(d.get("confidence", 0.0)) for d in domain_scores) / len(domain_scores))
            if domain_scores
            else 0.0,
        )
    )

    overall_lower, overall_upper, overall_width = _score_interval(
        overall_wis,
        lower=evaluation_result.get("overall_wis_lower"),
        upper=evaluation_result.get("overall_wis_upper"),
        confidence=overall_confidence,
    )

    domain_details = []
    for item in domain_scores:
        wis = float(item.get("wis", 0.0))
        lower, upper, width = _score_interval(
            wis,
            lower=item.get("wis_lower") or item.get("domain_wis_lower"),
            upper=item.get("wis_upper") or item.get("domain_wis_upper"),
            confidence=item.get("confidence"),
        )
        domain_details.append(
            {
                "domain": item["domain"],
                "wis": wis,
                "wis_lower": round(lower, 1),
                "wis_upper": round(upper, 1),
                "confidence_width": round(width, 1),
                "confidence": float(item.get("confidence", 0.0)),
                "n_templates": int(item.get("n_templates", 0)),
                "template_ids": list(item.get("template_ids", [])),
            }
        )

    strengths = [
        {
            "domain": item["domain"],
            "wis": float(item["wis"]),
            "wis_lower": item["wis_lower"],
            "wis_upper": item["wis_upper"],
            "why": "domain performance is in the resilient range",
        }
        for item in domain_details
        if float(item.get("wis", 0.0)) > 70.0
    ]

    deficits = [
        {
            "domain": item["domain"],
            "wis": float(item["wis"]),
            "wis_lower": item["wis_lower"],
            "wis_upper": item["wis_upper"],
            "risk_level": "high" if float(item["wis"]) < 30.0 else "moderate",
            "templates": list(item.get("template_ids", [])),
        }
        for item in domain_details
        if float(item.get("wis", 0.0)) < 40.0
    ]

    recommendations = []
    for deficit in deficits:
        domain = deficit["domain"]
        recommendations.append(
            {
                "domain": domain,
                "priority": "urgent" if deficit["wis"] < 30.0 else "targeted",
                "template_focus": deficit["templates"],
                "target_parameters": _targets_for_domain(domain),
            }
        )

    empirical_count, expert_count = _calibration_summary(evaluation_result)
    n_templates = int(
        evaluation_result.get(
            "n_templates",
            sum(int(item.get("n_templates", 1)) for item in domain_scores),
        )
    )

    report = {
        "summary": {
            "overall_wis": overall_wis,
            "overall_wis_lower": round(overall_lower, 1),
            "overall_wis_upper": round(overall_upper, 1),
            "confidence_width": round(overall_width, 1),
            "confidence": _confidence_bucket(overall_confidence),
            "confidence_value": overall_confidence,
            "verdict": _verdict_for_score(overall_wis),
        },
        "domain_details": domain_details,
        "strengths": strengths,
        "deficits": deficits,
        "data_gaps": data_gaps,
        "recommendations": recommendations,
        "uncertainty_flags": [
            {
                "domain": item["domain"],
                "confidence_width": item["confidence_width"],
                "message": "High score uncertainty (>20 WIS points). Prioritize higher-quality measurement.",
            }
            for item in domain_details
            if item["confidence_width"] > 20.0
        ],
        "uncertainty_disclosure": {
            "empirically_calibrated_templates": empirical_count,
            "expert_estimate_templates": expert_count,
            "note": "Calibration labels are derived from template calibration_status metadata.",
        },
        "methodology_note": (
            f"Assessment based on {n_templates} templates, "
            f"{empirical_count} with empirical calibration, "
            f"{expert_count} with expert estimates."
        ),
    }
    return report


def format_report_text(report: dict) -> str:
    """Plain text formatter for terminal/log output."""
    summary = report.get("summary", {})
    lines = [
        "CMR ASSESSMENT REPORT",
        (
            f"Overall WIS: {summary.get('overall_wis', 0.0):.1f} "
            f"[{summary.get('overall_wis_lower', 0.0):.1f}, {summary.get('overall_wis_upper', 0.0):.1f}]"
        ),
        f"Confidence: {summary.get('confidence', 'low')} ({summary.get('confidence_value', 0.0):.2f})",
        f"Verdict: {summary.get('verdict', 'n/a')}",
        "",
        "Strengths:",
    ]

    strengths = report.get("strengths", [])
    if strengths:
        for item in strengths:
            lines.append(f"- {item['domain']}: WIS {item['wis']:.1f} ({item['why']})")
    else:
        lines.append("- None identified")

    lines.extend(["", "Deficits:"])
    deficits = report.get("deficits", [])
    if deficits:
        for item in deficits:
            lines.append(
                f"- {item['domain']}: WIS {item['wis']:.1f}, risk={item['risk_level']}"
            )
    else:
        lines.append("- None identified")

    lines.extend(["", "Data Gaps:"])
    data_gaps = report.get("data_gaps", [])
    if data_gaps:
        for gap in data_gaps:
            lines.append(f"- {gap}")
    else:
        lines.append("- None")

    lines.extend(["", "Recommendations:"])
    recs = report.get("recommendations", [])
    if recs:
        for rec in recs:
            lines.append(f"- {rec['domain']} ({rec['priority']})")
            for target in rec.get("target_parameters", []):
                lines.append(f"  * {target['parameter']}: {target['target']}")
    else:
        lines.append("- No targeted interventions required")

    uncertainty = report.get("uncertainty_disclosure", {})
    lines.extend(
        [
            "",
            "Uncertainty Flags:",
        ]
    )
    flags = report.get("uncertainty_flags", [])
    if flags:
        for flag in flags:
            lines.append(
                f"- {flag['domain']}: width={flag['confidence_width']:.1f} ({flag['message']})"
            )
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "Uncertainty Disclosure:",
            (
                "- Empirical templates: "
                f"{uncertainty.get('empirically_calibrated_templates', 0)}"
            ),
            (
                "- Expert-estimate templates: "
                f"{uncertainty.get('expert_estimate_templates', 0)}"
            ),
            f"- {uncertainty.get('note', '')}",
            "",
            "Methodology:",
            report.get("methodology_note", ""),
        ]
    )

    return "\n".join(lines)


def get_domain_plot_data(report: dict) -> dict[str, list[float | str]]:
    """Prepare domain-level data for bar charts with error bars."""
    details = report.get("domain_details", []) or []
    return {
        "domains": [str(item.get("domain", "")) for item in details],
        "scores": [float(item.get("wis", 0.0)) for item in details],
        "lower": [float(item.get("wis_lower", item.get("wis", 0.0))) for item in details],
        "upper": [float(item.get("wis_upper", item.get("wis", 0.0))) for item in details],
    }
