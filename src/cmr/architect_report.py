"""Architect-facing report formatter (Sprint 12 Task 12.8)."""

from __future__ import annotations

from typing import Any


def _rating(score: float) -> str:
    if score >= 75:
        return "Strong"
    if score >= 60:
        return "Good"
    if score >= 45:
        return "Needs Attention"
    return "Critical"


def _color(score: float) -> str:
    if score >= 75:
        return "green"
    if score >= 60:
        return "yellow"
    if score >= 45:
        return "orange"
    return "red"


def _domain_name(code: str) -> str:
    mapping = {
        "L": "Lighting",
        "MAT": "Materials & Thermal Comfort",
        "SC": "Spatial Clarity",
        "SOC": "Social Comfort & Privacy",
        "VIEW": "Views & Nature Connection",
        "VF": "Visual Form",
        "TP": "Safety & Transitions",
        "CREA": "Creative Support",
        "COL": "Color Experience",
    }
    upper = str(code or "").upper()
    for prefix, label in mapping.items():
        if upper.startswith(prefix):
            return label
    return f"{upper} Domain".strip()


def _quick_win(domain: str) -> str:
    quick_map = {
        "L": "Replace bulbs to achieve consistent 350-500 lux in key work areas.",
        "MAT": "Add portable fans/heaters and occupant controls in problem zones.",
        "SC": "Add wayfinding cues: room labels, landmark colors, and path markers.",
        "SOC": "Use low-cost acoustic panels and furniture screens in focus zones.",
        "VIEW": "Add plants and orient desks toward available exterior views.",
        "VF": "Reconfigure furniture to increase perceived openness and sight lines.",
        "TP": "Add anti-slip strips and improve edge contrast on level changes.",
        "CREA": "Create one low-distraction and one stimulation-rich work zone.",
        "COL": "Introduce balanced warm-natural accent colors on key surfaces.",
    }
    return quick_map.get(domain, "Address the weakest zone first with a low-cost pilot intervention.")


def _design_change(domain: str) -> str:
    design_map = {
        "L": "Redesign daylight and electric lighting layers to support circadian timing and task contrast.",
        "MAT": "Upgrade envelope and material palette for stable thermal comfort and tactile quality.",
        "SC": "Rework circulation and entry hierarchy to reduce confusion and navigation friction.",
        "SOC": "Rezone plan for clear privacy gradients (focus, collaboration, social).",
        "VIEW": "Increase high-quality exterior view access and layered nature exposure.",
        "VF": "Adjust section and room proportions to improve spaciousness and cognitive flexibility.",
        "TP": "Re-detail thresholds and transitions for safer movement and clearer boundaries.",
        "CREA": "Provide differentiated settings for ideation, incubation, and focused execution.",
        "COL": "Adopt a coherent color strategy tied to function and wayfinding.",
    }
    return design_map.get(domain, "Plan a targeted redesign package for the weakest-performing domain.")


def generate_architect_report(evaluation_result: dict[str, Any]) -> dict[str, Any]:
    """
    Build a plain-language architect report from building evaluation output.

    Intended for design teams; avoids internal template jargon.
    """
    overall_wis = float(evaluation_result.get("overall_wis", 0.0))
    domains = sorted(
        (evaluation_result.get("domain_scores") or []),
        key=lambda row: float(row.get("wis", 0.0)),
        reverse=True,
    )
    data_gaps = list(evaluation_result.get("data_gaps") or [])

    working = domains[:3]
    needs = [row for row in reversed(domains) if float(row.get("wis", 0.0)) < 60][:3]
    if not needs:
        needs = domains[-3:]

    whats_working = [
        f"{_domain_name(row.get('domain', ''))}: performing at {float(row.get('wis', 0.0)):.1f}/100."
        for row in working
    ]
    what_needs_attention = [
        f"{_domain_name(row.get('domain', ''))}: currently {float(row.get('wis', 0.0)):.1f}/100."
        for row in needs
    ]

    quick_wins = [_quick_win(str(row.get("domain", ""))) for row in needs][:3]
    design_changes = [_design_change(str(row.get("domain", ""))) for row in needs][:3]
    couldnt_assess = data_gaps[:6] if data_gaps else ["No major assessment gaps detected from provided inputs."]

    methodology_note = (
        "This report summarizes measured and observed environmental conditions into a 0-100 wellness score. "
        "It highlights practical interventions first, then longer-horizon design moves. "
        "Scores should be interpreted as decision support, not as a substitute for post-occupancy validation."
    )

    return {
        "building_wellness_score": {
            "score": round(overall_wis, 1),
            "rating": _rating(overall_wis),
            "color": _color(overall_wis),
        },
        "whats_working": whats_working,
        "what_needs_attention": what_needs_attention,
        "quick_wins_under_1000": quick_wins,
        "design_changes": design_changes,
        "what_we_couldnt_assess": couldnt_assess,
        "methodology_note": methodology_note,
    }


def format_architect_report_text(report: dict[str, Any]) -> str:
    """Render architect report to plain text."""
    score = report.get("building_wellness_score", {})
    lines = [
        "ARCHITECT REPORT",
        f"Building Wellness Score: {score.get('score', 0.0)}/100 "
        f"({score.get('rating', 'Unknown')}, {score.get('color', 'gray')})",
        "",
        "What's Working:",
    ]
    for item in report.get("whats_working", [])[:3]:
        lines.append(f"- {item}")

    lines.extend(["", "What Needs Attention:"])
    for item in report.get("what_needs_attention", [])[:3]:
        lines.append(f"- {item}")

    lines.extend(["", "Quick Wins (under $1000):"])
    for item in report.get("quick_wins_under_1000", [])[:3]:
        lines.append(f"- {item}")

    lines.extend(["", "Design Changes:"])
    for item in report.get("design_changes", [])[:3]:
        lines.append(f"- {item}")

    lines.extend(["", "What We Couldn't Assess:"])
    for item in report.get("what_we_couldnt_assess", [])[:6]:
        lines.append(f"- {item}")

    lines.extend(["", "Methodology Note:", str(report.get("methodology_note", ""))])
    return "\n".join(lines)


__all__ = ["generate_architect_report", "format_architect_report_text"]
