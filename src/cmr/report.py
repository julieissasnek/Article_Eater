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

    strengths = [
        {
            "domain": item["domain"],
            "wis": float(item["wis"]),
            "why": "domain performance is in the resilient range",
        }
        for item in domain_scores
        if float(item.get("wis", 0.0)) > 70.0
    ]

    deficits = [
        {
            "domain": item["domain"],
            "wis": float(item["wis"]),
            "risk_level": "high" if float(item["wis"]) < 30.0 else "moderate",
            "templates": list(item.get("template_ids", [])),
        }
        for item in domain_scores
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
            "confidence": _confidence_bucket(overall_confidence),
            "confidence_value": overall_confidence,
            "verdict": _verdict_for_score(overall_wis),
        },
        "strengths": strengths,
        "deficits": deficits,
        "data_gaps": data_gaps,
        "recommendations": recommendations,
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
        f"Overall WIS: {summary.get('overall_wis', 0.0):.1f}",
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

