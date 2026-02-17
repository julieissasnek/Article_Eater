"""Paper evaluation report generation utilities (Sprint 11 Task 11.12)."""

from __future__ import annotations

from typing import Any


def _voi_rank(voi: str) -> int:
    value = str(voi or "").lower()
    if value == "high":
        return 0
    if value == "medium":
        return 1
    return 2


def _coverage_ratio(matched: int, extracted: int) -> float:
    if extracted <= 0:
        return 0.0
    return round(matched / extracted, 3)


def _claim_text(claim: dict[str, Any]) -> str:
    return str(
        claim.get("description")
        or claim.get("text")
        or f"{claim.get('iv', 'unknown')} -> {claim.get('dv', 'unknown')}"
    )


def generate_paper_report(evaluation: dict) -> dict:
    """Build a structured paper report from evaluate_paper output."""
    claims_extracted = int(evaluation.get("n_claims_extracted", len(evaluation.get("claims", []))))
    claims_matched = int(
        evaluation.get(
            "n_claims_matched",
            sum(1 for row in evaluation.get("template_matches", []) if row.get("matches")),
        )
    )
    claims_unmatched = int(
        evaluation.get("n_claims_unmatched", max(0, claims_extracted - claims_matched))
    )
    paper_summary = str(
        evaluation.get("paper_summary")
        or f"Processed {claims_extracted} claims; {claims_matched} matched templates."
    )

    findings = list(evaluation.get("findings", []))
    template_matches = list(evaluation.get("template_matches", []))
    match_by_claim: dict[str, list[str]] = {}
    for entry in template_matches:
        claim_key = str(entry.get("claim"))
        match_by_claim[claim_key] = [
            str(item.get("template_id"))
            for item in entry.get("matches", [])
            if item.get("template_id")
        ]

    claim_assessments: list[dict[str, Any]] = []
    for finding in findings:
        claim = finding.get("claim", {})
        claim_key = str(claim)
        claim_assessments.append(
            {
                "claim": _claim_text(claim),
                "assessment": str(finding.get("assessment", "gap")),
                "convergence": str(finding.get("convergence", "unsupported")),
                "confidence": str(finding.get("confidence", "low")),
                "voi": str(finding.get("voi", "low")).lower(),
                "matched_templates": match_by_claim.get(claim_key, []),
            }
        )

    high_voi_findings = sorted(
        [item for item in claim_assessments if item.get("voi") in {"high", "medium"}],
        key=lambda item: (_voi_rank(str(item.get("voi"))), item.get("claim", "")),
    )

    updates = list(evaluation.get("template_system_updates", []))
    template_updates = [
        {
            "type": str(item.get("type", "gap")),
            "template": str(item.get("template", "none")),
            "detail": str(item.get("detail", "")),
        }
        for item in updates
    ]

    consulted_templates = sorted(
        {
            template_id
            for item in claim_assessments
            for template_id in item.get("matched_templates", [])
            if template_id
        }
    )

    report = {
        "summary": {
            "paper_summary": paper_summary,
            "claims_extracted": claims_extracted,
            "claims_matched": claims_matched,
            "claims_unmatched": claims_unmatched,
            "coverage_ratio": _coverage_ratio(claims_matched, claims_extracted),
        },
        "claim_assessments": claim_assessments,
        "high_voi_findings": high_voi_findings,
        "template_system_update_recommendations": template_updates,
        "methodology_note": (
            f"Consulted {len(consulted_templates)} templates across "
            f"{claims_extracted} claims; claim-space coverage "
            f"{_coverage_ratio(claims_matched, claims_extracted):.1%}."
        ),
    }
    return report


def format_paper_report_text(report: dict) -> str:
    """Render a terminal-friendly text report for paper evaluations."""
    summary = report.get("summary", {})
    assessments = list(report.get("claim_assessments", []))
    high_voi = list(report.get("high_voi_findings", []))
    updates = list(report.get("template_system_update_recommendations", []))

    lines = [
        "PAPER EVALUATION REPORT",
        str(summary.get("paper_summary", "No summary available.")),
        (
            "Claims: "
            f"{summary.get('claims_extracted', 0)} extracted, "
            f"{summary.get('claims_matched', 0)} matched, "
            f"{summary.get('claims_unmatched', 0)} unmatched "
            f"(coverage {float(summary.get('coverage_ratio', 0.0)):.1%})"
        ),
        "",
        "Per-Claim Assessment:",
    ]

    if assessments:
        for row in assessments:
            templates = ", ".join(row.get("matched_templates", [])) or "none"
            lines.append(
                "- "
                f"{row.get('claim')} | assessment={row.get('assessment')} | "
                f"convergence={row.get('convergence')} | confidence={row.get('confidence')} | "
                f"VOI={row.get('voi')} | templates={templates}"
            )
    else:
        lines.append("- No claim assessments available")

    lines.extend(["", "High-VOI Findings:"])
    if high_voi:
        for row in high_voi:
            lines.append(f"- [{row.get('voi')}] {row.get('claim')} ({row.get('assessment')})")
    else:
        lines.append("- None")

    lines.extend(["", "Template Update Recommendations:"])
    if updates:
        for row in updates:
            lines.append(
                f"- {row.get('type')} -> {row.get('template')}: {row.get('detail')}"
            )
    else:
        lines.append("- None")

    lines.extend(["", "Methodology:", str(report.get("methodology_note", ""))])
    return "\n".join(lines)

