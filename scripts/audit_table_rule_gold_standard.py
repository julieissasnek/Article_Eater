#!/usr/bin/env python3
"""Gold-standard audit: compare table-derived rules against extracted table row text.

Outputs:
- row-level audit CSV
- table-level audit CSV
- table remake queue CSV (inadequate tables)
- JSON summary report
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

UTC = timezone.utc


@dataclass
class RowEval:
    row_status: str
    reasons: List[str]
    source_informative: bool
    statement_informative: bool
    overlap_ratio: float
    env_resolved: bool
    out_resolved: bool
    effect_known: bool


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--confirmed-csv",
        type=Path,
        default=Path("data/production/realtime_pdf_confirmed_rows.csv"),
    )
    p.add_argument(
        "--row-audit-csv",
        type=Path,
        default=Path("data/review/table_rule_gold_audit_rows.csv"),
    )
    p.add_argument(
        "--table-audit-csv",
        type=Path,
        default=Path("data/review/table_rule_gold_audit_tables.csv"),
    )
    p.add_argument(
        "--table-remake-csv",
        type=Path,
        default=Path("data/review/table_remake_queue.csv"),
    )
    p.add_argument(
        "--report-json",
        type=Path,
        default=Path("data/review/table_rule_gold_audit_report.json"),
    )
    p.add_argument("--min-overlap", type=float, default=0.20)
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def tokenize(text: str) -> List[str]:
    t = normalize(text).lower()
    return re.findall(r"[a-z][a-z0-9_\-]{1,}", t)


def unresolved(value: str) -> bool:
    v = normalize(value)
    return bool(v) and v.upper().startswith("UNRESOLVED:")


def informative_text(text: str) -> bool:
    s = normalize(text)
    if not s:
        return False
    tokens = tokenize(s)
    if len(tokens) < 3:
        return False
    alpha = sum(ch.isalpha() for ch in s)
    digits = sum(ch.isdigit() for ch in s)
    if alpha <= 0:
        return False
    if digits / max(1, alpha) > 2.2:
        return False
    return True


def overlap_ratio(a: str, b: str) -> float:
    ta = set(tokenize(a))
    tb = set(tokenize(b))
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    denom = len(ta)
    return inter / max(1, denom)


def reason_join(items: Sequence[str]) -> str:
    return "|".join(sorted(set(i for i in items if i)))


def evaluate_row(row: Dict[str, str], min_overlap: float) -> RowEval:
    reasons: List[str] = []

    statement = normalize(row.get("statement", ""))
    quote = normalize(row.get("source_quote", ""))
    qflags = normalize(row.get("quality_flag", ""))

    env = normalize(row.get("environment_canonical_id", ""))
    out = normalize(row.get("outcome_canonical_id", ""))
    effect = normalize(row.get("effect_direction", "")).lower()
    translation_status = normalize(row.get("translation_status", "")).lower()

    env_resolved = bool(env) and not unresolved(env)
    out_resolved = bool(out) and not unresolved(out)
    effect_known = effect in {"positive", "negative", "null"}

    if translation_status == "noncausal":
        # Noncausal rows should not be penalized for missing causal mappings.
        env_resolved = True
        out_resolved = True
        effect_known = True

    src_info = informative_text(quote)
    stmt_info = informative_text(statement)
    ov = overlap_ratio(statement, quote)

    if not src_info:
        reasons.append("source_row_low_information")
    if not stmt_info:
        reasons.append("statement_low_information")
    if ov < min_overlap:
        reasons.append("low_statement_source_overlap")
    if not env_resolved:
        reasons.append("environment_unresolved")
    if not out_resolved:
        reasons.append("outcome_unresolved")
    if not effect_known:
        reasons.append("effect_unknown")
    if translation_status:
        reasons.append(f"translation_status:{translation_status}")
    if "auto_reconstructed_from_table" in qflags:
        reasons.append("auto_reconstructed")
    if "auto_denoised_statement" in qflags:
        reasons.append("auto_denoised")
    if "needs_manual_rule_cleanup" in qflags:
        reasons.append("legacy_manual_cleanup_flag")

    # Status policy:
    # - suspect_table: source row itself is weak/noisy and unresolved dominates.
    # - suspect_rule: source row informative enough but rule alignment/fields are weak.
    # - verified_weak: acceptable but unresolved in one key field.
    # - verified_strong: good alignment + resolved env/out + known effect.
    if translation_status == "noncausal":
        status = "verified_weak"
    elif translation_status == "untranslatable_noise":
        status = "suspect_table" if not src_info else "suspect_rule"
    elif not src_info and (not env_resolved or not out_resolved):
        status = "suspect_table"
    elif src_info and (ov < min_overlap or not stmt_info):
        status = "suspect_rule"
    elif src_info and (env_resolved and out_resolved and effect_known) and ov >= min_overlap:
        status = "verified_strong"
    else:
        status = "verified_weak"

    return RowEval(
        row_status=status,
        reasons=reasons,
        source_informative=src_info,
        statement_informative=stmt_info,
        overlap_ratio=ov,
        env_resolved=env_resolved,
        out_resolved=out_resolved,
        effect_known=effect_known,
    )


def main() -> int:
    args = parse_args()
    if not args.confirmed_csv.exists():
        raise SystemExit(f"Missing CSV: {args.confirmed_csv}")

    rows_out: List[Dict[str, str]] = []
    table_stats: Dict[Tuple[str, str], Dict[str, object]] = defaultdict(
        lambda: {
            "paper_id": "",
            "source_table_id": "",
            "rows_total": 0,
            "verified_strong": 0,
            "verified_weak": 0,
            "suspect_rule": 0,
            "suspect_table": 0,
            "env_resolved_rows": 0,
            "out_resolved_rows": 0,
            "effect_known_rows": 0,
            "low_info_source_rows": 0,
            "auto_reconstructed_rows": 0,
            "auto_denoised_rows": 0,
            "reasons": Counter(),
        }
    )

    totals = Counter()

    with args.confirmed_csv.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if normalize(row.get("evidence_level", "")) != "pdf_table_extracted":
                continue
            totals["table_rows_total"] += 1

            ev = evaluate_row(row, min_overlap=args.min_overlap)

            paper_id = normalize(row.get("paper_id", ""))
            table_id = normalize(row.get("source_table_id", "")) or "UNSPECIFIED_TABLE"
            key = (paper_id, table_id)
            ts = table_stats[key]
            ts["paper_id"] = paper_id
            ts["source_table_id"] = table_id
            ts["rows_total"] = int(ts["rows_total"]) + 1
            ts[ev.row_status] = int(ts[ev.row_status]) + 1
            if ev.env_resolved:
                ts["env_resolved_rows"] = int(ts["env_resolved_rows"]) + 1
            if ev.out_resolved:
                ts["out_resolved_rows"] = int(ts["out_resolved_rows"]) + 1
            if ev.effect_known:
                ts["effect_known_rows"] = int(ts["effect_known_rows"]) + 1
            if not ev.source_informative:
                ts["low_info_source_rows"] = int(ts["low_info_source_rows"]) + 1

            qf = normalize(row.get("quality_flag", ""))
            if "auto_reconstructed_from_table" in qf:
                ts["auto_reconstructed_rows"] = int(ts["auto_reconstructed_rows"]) + 1
            if "auto_denoised_statement" in qf:
                ts["auto_denoised_rows"] = int(ts["auto_denoised_rows"]) + 1

            for reason in ev.reasons:
                ts["reasons"][reason] += 1
                totals[f"reason:{reason}"] += 1

            totals[f"row_status:{ev.row_status}"] += 1

            rows_out.append(
                {
                    "paper_id": paper_id,
                    "source_table_id": table_id,
                    "source_table_row": normalize(row.get("source_table_row", "")),
                    "claim_id": normalize(row.get("claim_id", "")),
                    "claim_type": normalize(row.get("claim_type", "")),
                    "row_status": ev.row_status,
                    "reasons": reason_join(ev.reasons),
                    "source_informative": str(ev.source_informative).lower(),
                    "statement_informative": str(ev.statement_informative).lower(),
                    "overlap_ratio": f"{ev.overlap_ratio:.4f}",
                    "env_resolved": str(ev.env_resolved).lower(),
                    "out_resolved": str(ev.out_resolved).lower(),
                    "effect_known": str(ev.effect_known).lower(),
                    "translation_status": normalize(row.get("translation_status", "")),
                    "translation_confidence": normalize(row.get("translation_confidence", "")),
                    "translation_warnings": normalize(row.get("translation_warnings", "")),
                    "needs_verification": normalize(row.get("needs_verification", "")),
                    "quality_flag": normalize(row.get("quality_flag", "")),
                    "statement": normalize(row.get("statement", "")),
                    "source_quote": normalize(row.get("source_quote", "")),
                }
            )

    table_rows: List[Dict[str, str]] = []
    remake_rows: List[Dict[str, str]] = []

    for (_pid, _tid), stats in table_stats.items():
        rows_total = int(stats["rows_total"])
        suspect_table = int(stats["suspect_table"])
        suspect_rule = int(stats["suspect_rule"])
        verified_strong = int(stats["verified_strong"])
        verified_weak = int(stats["verified_weak"])
        low_info = int(stats["low_info_source_rows"])

        suspect_table_rate = suspect_table / max(1, rows_total)
        suspect_any_rate = (suspect_table + suspect_rule) / max(1, rows_total)

        if suspect_table_rate >= 0.50 or low_info >= 3:
            table_status = "inadequate_table_remake"
        elif suspect_any_rate >= 0.50:
            table_status = "suspect_rule_alignment"
        elif verified_strong == rows_total:
            table_status = "verified_strong"
        else:
            table_status = "verified_mixed"

        top_reasons = ",".join(
            [f"{k}:{v}" for k, v in stats["reasons"].most_common(6)]
        )

        row_obj = {
            "paper_id": str(stats["paper_id"]),
            "source_table_id": str(stats["source_table_id"]),
            "table_status": table_status,
            "rows_total": str(rows_total),
            "verified_strong": str(verified_strong),
            "verified_weak": str(verified_weak),
            "suspect_rule": str(suspect_rule),
            "suspect_table": str(suspect_table),
            "low_info_source_rows": str(low_info),
            "env_resolved_rows": str(stats["env_resolved_rows"]),
            "out_resolved_rows": str(stats["out_resolved_rows"]),
            "effect_known_rows": str(stats["effect_known_rows"]),
            "auto_reconstructed_rows": str(stats["auto_reconstructed_rows"]),
            "auto_denoised_rows": str(stats["auto_denoised_rows"]),
            "top_reasons": top_reasons,
        }
        table_rows.append(row_obj)

        if table_status == "inadequate_table_remake":
            remake_rows.append(
                {
                    "paper_id": str(stats["paper_id"]),
                    "source_table_id": str(stats["source_table_id"]),
                    "status": "queued_table_remake",
                    "reason": "high_low_info_or_table_suspect_rate",
                    "rows_total": str(rows_total),
                    "suspect_table": str(suspect_table),
                    "low_info_source_rows": str(low_info),
                    "top_reasons": top_reasons,
                    "queued_at": datetime.now(tz=UTC).isoformat(),
                }
            )

    table_status_counts = Counter(r["table_status"] for r in table_rows)

    report = {
        "generated_at": datetime.now(tz=UTC).isoformat(),
        "confirmed_csv": str(args.confirmed_csv),
        "min_overlap": args.min_overlap,
        "row_counts": {
            "table_rows_total": totals["table_rows_total"],
            "verified_strong": totals["row_status:verified_strong"],
            "verified_weak": totals["row_status:verified_weak"],
            "suspect_rule": totals["row_status:suspect_rule"],
            "suspect_table": totals["row_status:suspect_table"],
        },
        "table_counts": {
            "tables_total": len(table_rows),
            **dict(table_status_counts),
        },
        "reason_counts": {
            k.replace("reason:", ""): v
            for k, v in totals.items()
            if k.startswith("reason:")
        },
        "outputs": {
            "row_audit_csv": str(args.row_audit_csv),
            "table_audit_csv": str(args.table_audit_csv),
            "table_remake_csv": str(args.table_remake_csv),
            "report_json": str(args.report_json),
        },
        "dry_run": bool(args.dry_run),
    }

    if args.dry_run:
        print(json.dumps(report, indent=2))
        return 0

    args.row_audit_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.row_audit_csv.open("w", encoding="utf-8", newline="") as f:
        fields = [
            "paper_id",
            "source_table_id",
            "source_table_row",
            "claim_id",
            "claim_type",
            "row_status",
            "reasons",
            "source_informative",
            "statement_informative",
            "overlap_ratio",
            "env_resolved",
            "out_resolved",
            "effect_known",
            "translation_status",
            "translation_confidence",
            "translation_warnings",
            "needs_verification",
            "quality_flag",
            "statement",
            "source_quote",
        ]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows_out)

    args.table_audit_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.table_audit_csv.open("w", encoding="utf-8", newline="") as f:
        fields = [
            "paper_id",
            "source_table_id",
            "table_status",
            "rows_total",
            "verified_strong",
            "verified_weak",
            "suspect_rule",
            "suspect_table",
            "low_info_source_rows",
            "env_resolved_rows",
            "out_resolved_rows",
            "effect_known_rows",
            "auto_reconstructed_rows",
            "auto_denoised_rows",
            "top_reasons",
        ]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(sorted(table_rows, key=lambda r: (r["table_status"], r["paper_id"], r["source_table_id"])))

    args.table_remake_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.table_remake_csv.open("w", encoding="utf-8", newline="") as f:
        fields = [
            "paper_id",
            "source_table_id",
            "status",
            "reason",
            "rows_total",
            "suspect_table",
            "low_info_source_rows",
            "top_reasons",
            "queued_at",
        ]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(sorted(remake_rows, key=lambda r: (r["paper_id"], r["source_table_id"])))

    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.report_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
