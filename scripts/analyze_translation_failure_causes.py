#!/usr/bin/env python3
"""Attribute table->rule translation failures by stage with concrete counts."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set, Tuple

UTC = timezone.utc


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--row-audit-csv",
        type=Path,
        default=Path("data/review/table_rule_gold_audit_rows.csv"),
        help="Row-level gold audit file.",
    )
    p.add_argument(
        "--output-json",
        type=Path,
        default=Path("data/review/translation_failure_cause_report.json"),
    )
    p.add_argument(
        "--output-csv",
        type=Path,
        default=Path("data/review/translation_failure_cause_report.csv"),
    )
    p.add_argument(
        "--examples-per-cause",
        type=int,
        default=8,
        help="How many row examples to keep per cause bucket.",
    )
    return p.parse_args()


def norm(text: str) -> str:
    return str(text or "").strip()


def parse_reasons(raw: str) -> Set[str]:
    return {x for x in (raw or "").split("|") if x}


def classify_causes(row: Dict[str, str]) -> Set[str]:
    causes: Set[str] = set()
    status = norm(row.get("row_status"))
    reasons = parse_reasons(norm(row.get("reasons")))
    claim_type = norm(row.get("claim_type")).lower()

    source_info = norm(row.get("source_informative")).lower() == "true"
    statement_info = norm(row.get("statement_informative")).lower() == "true"
    env_resolved = norm(row.get("env_resolved")).lower() == "true"
    out_resolved = norm(row.get("out_resolved")).lower() == "true"
    effect_known = norm(row.get("effect_known")).lower() == "true"
    overlap = float(norm(row.get("overlap_ratio")) or 0.0)
    translation_status = norm(row.get("translation_status")).lower()

    if status == "suspect_table" or "source_row_low_information" in reasons or translation_status == "untranslatable_noise":
        causes.add("table_or_pdf_extraction_fault")

    mapper_markers = {
        "low_statement_source_overlap",
        "statement_low_information",
        "auto_reconstructed",
        "auto_denoised",
        "legacy_manual_cleanup_flag",
    }
    if (reasons & mapper_markers or (source_info and not statement_info)) and translation_status not in {
        "untranslatable_noise",
        "noncausal",
    }:
        causes.add("table_to_rule_mapping_fault")

    if translation_status == "noncausal":
        causes.add("no_translation_failure_detected")
        return causes

    if (not env_resolved) or (not out_resolved):
        if translation_status == "untranslatable_noise":
            causes.add("table_or_pdf_extraction_fault")
        elif claim_type in {"methodology", "sample"}:
            causes.add("rule_schema_mismatch_noncausal_claims")
        elif source_info and overlap >= 0.20:
            causes.add("ontology_coverage_or_resolution_gap")
        else:
            causes.add("article_or_row_ambiguity")

    if not effect_known and claim_type in {"finding", "effect"} and translation_status not in {"untranslatable_noise", "noncausal"}:
        causes.add("rule_requirement_effect_direction_gap")

    if not causes and status in {"verified_strong", "verified_weak"}:
        causes.add("no_translation_failure_detected")
    elif not causes:
        causes.add("other_or_unclear")

    return causes


def row_key(row: Dict[str, str]) -> Tuple[str, str, str]:
    return (norm(row.get("paper_id")), norm(row.get("source_table_id")), norm(row.get("claim_id")))


def main() -> int:
    args = parse_args()
    if not args.row_audit_csv.exists():
        raise SystemExit(f"Missing input CSV: {args.row_audit_csv}")

    cause_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    claim_type_counts: Counter[str] = Counter()
    cooccurrence: Counter[Tuple[str, str]] = Counter()
    examples: Dict[str, List[Dict[str, str]]] = defaultdict(list)

    rows_total = 0
    unique_rows = set()
    rows_with_failure = 0

    with args.row_audit_csv.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows_total += 1
            unique_rows.add(row_key(row))
            status = norm(row.get("row_status"))
            claim_type = norm(row.get("claim_type")).lower() or "unknown"
            status_counts[status] += 1
            claim_type_counts[claim_type] += 1

            causes = classify_causes(row)
            if "no_translation_failure_detected" not in causes:
                rows_with_failure += 1
            for c in sorted(causes):
                cause_counts[c] += 1
                if len(examples[c]) < args.examples_per_cause:
                    examples[c].append(
                        {
                            "paper_id": norm(row.get("paper_id")),
                            "source_table_id": norm(row.get("source_table_id")),
                            "claim_id": norm(row.get("claim_id")),
                            "claim_type": claim_type,
                            "row_status": status,
                            "translation_status": norm(row.get("translation_status")),
                            "reasons": norm(row.get("reasons")),
                            "statement": norm(row.get("statement"))[:220],
                            "source_quote": norm(row.get("source_quote"))[:220],
                        }
                    )
            for a in causes:
                for b in causes:
                    if a < b:
                        cooccurrence[(a, b)] += 1

    rows_by_cause = []
    for cause, count in cause_counts.most_common():
        rows_by_cause.append(
            {
                "cause": cause,
                "rows": count,
                "pct_rows": round((count / rows_total) * 100.0, 3) if rows_total else 0.0,
            }
        )

    pair_rows = [
        {"cause_a": a, "cause_b": b, "rows": n}
        for (a, b), n in cooccurrence.most_common(20)
    ]

    report = {
        "generated_at": datetime.now(tz=UTC).isoformat(),
        "input": str(args.row_audit_csv),
        "rows_total": rows_total,
        "rows_unique": len(unique_rows),
        "rows_with_any_failure": rows_with_failure,
        "failure_rate_pct": round((rows_with_failure / rows_total) * 100.0, 3) if rows_total else 0.0,
        "status_counts": dict(status_counts),
        "claim_type_counts": dict(claim_type_counts),
        "rows_by_cause": rows_by_cause,
        "top_cooccurrence_pairs": pair_rows,
        "examples": examples,
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["cause", "rows", "pct_rows"],
        )
        writer.writeheader()
        writer.writerows(rows_by_cause)

    print(json.dumps(report["rows_by_cause"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
