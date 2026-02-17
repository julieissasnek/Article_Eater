#!/usr/bin/env python3
"""
Generate an evidence gap map for template coverage (Sprint 13 Task 13.12).

Outputs:
  1) JSON summary for programmatic consumption
  2) Markdown report for human review

Evidence tiers:
  - Strong Evidence
  - Moderate Evidence
  - Weak Evidence
  - No Evidence (gap templates)

Research targets are ranked by priority = impact * feasibility.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.cmr.feature_mapping import FEATURE_TO_TEMPLATE_INPUT
from src.cmr.models import TemplateRecord, get_session
from src.cmr.template_computations import TEMPLATE_COMPUTE_FUNCTIONS
from src.cmr.template_scanner import scan_templates


SERIES_IMPACT_WEIGHT = {
    "L": 1.00,
    "MAT": 1.00,
    "VIEW": 1.00,
    "SC": 0.95,
    "SOC": 0.95,
    "VF": 0.95,
    "CREA": 0.95,
    "TP": 0.90,
    "COL": 0.85,
    "OLF": 0.80,
    "T": 0.90,
}

STATUS_IMPACT_WEIGHT = {
    "active": 1.00,
    "gap": 0.95,
    "residual": 0.85,
    "reference": 0.70,
    "superseded": 0.40,
}

ACCESSIBILITY_FEASIBILITY = {
    "A": 1.00,
    "B": 0.85,
    "C": 0.65,
    "D": 0.45,
}

CALIBRATION_FEASIBILITY = {
    "protocol": 0.95,
    "partial": 0.80,
    "uncalibrated": 0.70,
    "framework_specified": 0.65,
    "good": 0.55,
    "substantial": 0.45,
    "well_calibrated": 0.35,
}

LOW_EVIDENCE_BONUS = {
    "no_evidence": 1.00,
    "weak": 0.80,
    "moderate": 0.35,
    "strong": 0.10,
}


@dataclass
class TemplateEvidenceRow:
    display_id: str
    template_id: str
    name: str
    series: str
    dedup_status: str
    maturity: str
    calibration_status: str
    practical_accessibility: str
    ecological_validation: bool
    has_compute_function: bool
    has_feature_mapping: bool
    evidence_tier: str
    impact_score: float
    feasibility_score: float
    priority_score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "display_id": self.display_id,
            "template_id": self.template_id,
            "name": self.name,
            "series": self.series,
            "dedup_status": self.dedup_status,
            "maturity": self.maturity,
            "calibration_status": self.calibration_status,
            "practical_accessibility": self.practical_accessibility,
            "ecological_validation": self.ecological_validation,
            "has_compute_function": self.has_compute_function,
            "has_feature_mapping": self.has_feature_mapping,
            "evidence_tier": self.evidence_tier,
            "impact_score": round(self.impact_score, 3),
            "feasibility_score": round(self.feasibility_score, 3),
            "priority_score": round(self.priority_score, 3),
        }


def _normalize(value: str | None) -> str:
    return str(value or "").strip().lower()


def _classify_evidence_tier(template: TemplateRecord) -> str:
    dedup = _normalize(template.dedup_status)
    if dedup == "gap":
        return "no_evidence"

    maturity = _normalize(template.maturity)
    calibration = _normalize(template.calibration_status)

    strong_maturity_markers = ("established", "how-actually")
    moderate_maturity_markers = ("supported", "preliminary", "how-plausibly", "good")

    strong_calibration_markers = ("substantial", "well_calibrated", "good")
    moderate_calibration_markers = ("partial", "protocol", "framework_specified")

    has_strong_maturity = any(marker in maturity for marker in strong_maturity_markers)
    has_moderate_maturity = any(marker in maturity for marker in moderate_maturity_markers)
    has_strong_calibration = any(marker in calibration for marker in strong_calibration_markers)
    has_moderate_calibration = any(marker in calibration for marker in moderate_calibration_markers)

    if has_strong_maturity and (has_strong_calibration or template.ecological_validation):
        return "strong"
    if has_strong_maturity or has_moderate_maturity or has_moderate_calibration:
        return "moderate"
    return "weak"


def _compute_impact_score(
    template: TemplateRecord,
    *,
    has_compute_function: bool,
    has_feature_mapping: bool,
    evidence_tier: str,
) -> float:
    series_weight = SERIES_IMPACT_WEIGHT.get(template.series, 0.70)
    status_weight = STATUS_IMPACT_WEIGHT.get(_normalize(template.dedup_status), 0.60)
    pipeline_weight = 0.50
    if has_compute_function:
        pipeline_weight += 0.25
    if has_feature_mapping:
        pipeline_weight += 0.25
    low_evidence_weight = LOW_EVIDENCE_BONUS.get(evidence_tier, 0.30)
    return (
        100.0
        * (
            0.35 * series_weight
            + 0.30 * status_weight
            + 0.20 * pipeline_weight
            + 0.15 * low_evidence_weight
        )
    )


def _compute_feasibility_score(
    template: TemplateRecord,
    *,
    has_compute_function: bool,
) -> float:
    accessibility = ACCESSIBILITY_FEASIBILITY.get(template.practical_accessibility.upper(), 0.60)
    calibration = CALIBRATION_FEASIBILITY.get(_normalize(template.calibration_status), 0.60)
    compute_ready = 0.95 if has_compute_function else 0.55
    return 100.0 * (0.45 * accessibility + 0.35 * calibration + 0.20 * compute_ready)


def _load_templates(db_path: str) -> list[TemplateRecord]:
    session = get_session(db_path)
    try:
        rows = session.query(TemplateRecord).all()
        if rows:
            return rows
    finally:
        session.close()

    # Auto-seed template records if absent.
    scan_templates(db_path=db_path)
    session = get_session(db_path)
    try:
        return session.query(TemplateRecord).all()
    finally:
        session.close()


def generate_evidence_gap_map(db_path: str) -> dict[str, Any]:
    templates = _load_templates(db_path)
    compute_templates = set(TEMPLATE_COMPUTE_FUNCTIONS.keys())
    mapped_templates = set(FEATURE_TO_TEMPLATE_INPUT.keys())

    rows: list[TemplateEvidenceRow] = []
    for template in templates:
        has_compute = template.display_id in compute_templates
        has_mapping = template.display_id in mapped_templates
        tier = _classify_evidence_tier(template)
        impact = _compute_impact_score(
            template,
            has_compute_function=has_compute,
            has_feature_mapping=has_mapping,
            evidence_tier=tier,
        )
        feasibility = _compute_feasibility_score(template, has_compute_function=has_compute)
        priority = impact * feasibility / 100.0
        rows.append(
            TemplateEvidenceRow(
                display_id=template.display_id,
                template_id=template.template_id,
                name=template.name,
                series=template.series,
                dedup_status=template.dedup_status,
                maturity=template.maturity,
                calibration_status=template.calibration_status,
                practical_accessibility=template.practical_accessibility,
                ecological_validation=bool(template.ecological_validation),
                has_compute_function=has_compute,
                has_feature_mapping=has_mapping,
                evidence_tier=tier,
                impact_score=impact,
                feasibility_score=feasibility,
                priority_score=priority,
            )
        )

    by_tier: dict[str, list[TemplateEvidenceRow]] = {
        "strong": [],
        "moderate": [],
        "weak": [],
        "no_evidence": [],
    }
    for row in rows:
        by_tier[row.evidence_tier].append(row)

    for key in by_tier:
        by_tier[key].sort(key=lambda item: (-item.priority_score, item.display_id))

    research_targets = sorted(
        [row for row in rows if row.evidence_tier in {"no_evidence", "weak", "moderate"}],
        key=lambda item: (-item.priority_score, item.display_id),
    )

    tier_counts = {tier: len(items) for tier, items in by_tier.items()}
    coverage_counts = Counter(row.series for row in rows)
    now = datetime.now(timezone.utc).isoformat()

    return {
        "generated_at": now,
        "db_path": db_path,
        "methodology": {
            "classification": "heuristic from maturity + calibration + dedup_status",
            "notes": [
                "No direct per-parameter study-count table exists in current schema.",
                "Gap templates are classified as no_evidence by definition.",
                "Priority score is impact * feasibility (both 0-100 scaled).",
            ],
        },
        "summary": {
            "total_templates": len(rows),
            "tier_counts": tier_counts,
            "series_counts": dict(coverage_counts),
            "compute_function_count": len([row for row in rows if row.has_compute_function]),
            "feature_mapping_count": len([row for row in rows if row.has_feature_mapping]),
        },
        "evidence_tiers": {
            "strong": [row.to_dict() for row in by_tier["strong"]],
            "moderate": [row.to_dict() for row in by_tier["moderate"]],
            "weak": [row.to_dict() for row in by_tier["weak"]],
            "no_evidence": [row.to_dict() for row in by_tier["no_evidence"]],
        },
        "priority_research_targets": [row.to_dict() for row in research_targets],
    }


def _write_markdown_report(payload: dict[str, Any], output_path: Path, top_n: int) -> None:
    summary = payload["summary"]
    tiers = payload["evidence_tiers"]
    targets = payload["priority_research_targets"][:top_n]

    lines: list[str] = []
    lines.append("# Evidence Gap Map")
    lines.append("")
    lines.append(f"Generated: {payload['generated_at']}")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Total templates: {summary['total_templates']}")
    lines.append(f"- Strong Evidence: {summary['tier_counts']['strong']}")
    lines.append(f"- Moderate Evidence: {summary['tier_counts']['moderate']}")
    lines.append(f"- Weak Evidence: {summary['tier_counts']['weak']}")
    lines.append(f"- No Evidence (gap templates): {summary['tier_counts']['no_evidence']}")
    lines.append("")
    lines.append("## Method")
    lines.append("- Classification uses maturity, calibration status, ecological validation, and dedup status.")
    lines.append("- Priority score = impact_score × feasibility_score / 100.")
    lines.append("- Impact favors active/high-leverage templates and lower-evidence areas.")
    lines.append("- Feasibility favors accessible measurements and templates with existing compute pathways.")
    lines.append("")
    lines.append("## Top Research Targets")
    lines.append("| Rank | Template | Tier | Impact | Feasibility | Priority |")
    lines.append("|---|---|---:|---:|---:|---:|")
    for idx, row in enumerate(targets, start=1):
        lines.append(
            f"| {idx} | {row['display_id']} ({row['series']}) | {row['evidence_tier']} | "
            f"{row['impact_score']:.1f} | {row['feasibility_score']:.1f} | {row['priority_score']:.1f} |"
        )
    lines.append("")
    lines.append("## Tier Detail Counts")
    lines.append(f"- Strong: {len(tiers['strong'])}")
    lines.append(f"- Moderate: {len(tiers['moderate'])}")
    lines.append(f"- Weak: {len(tiers['weak'])}")
    lines.append(f"- No Evidence: {len(tiers['no_evidence'])}")
    lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate evidence gap map for templates.")
    parser.add_argument("--db-path", default="ae.db", help="SQLite database path.")
    parser.add_argument(
        "--json-out",
        default="data/review/evidence_gap_map.json",
        help="Output JSON file path.",
    )
    parser.add_argument(
        "--md-out",
        default="docs/evidence_gap_map.md",
        help="Output Markdown file path.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=25,
        help="How many top research targets to include in Markdown.",
    )
    args = parser.parse_args()

    payload = generate_evidence_gap_map(args.db_path)

    json_path = Path(args.json_out)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    _write_markdown_report(payload, Path(args.md_out), top_n=args.top_n)

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {args.md_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
