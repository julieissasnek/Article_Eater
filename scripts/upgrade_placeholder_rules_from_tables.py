#!/usr/bin/env python3
"""Upgrade placeholder table-rule statements using re-audit outputs and table row text."""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, List, Sequence

UTC = timezone.utc
PLACEHOLDER = "Table extraction text is low quality; manual verification required."


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--production-csv", type=Path, default=Path("data/production/realtime_pdf_confirmed_rows.csv"))
    p.add_argument("--reaudit-csv", type=Path, default=Path("data/review/garbled_rules_reaudit_confirmed.csv"))
    p.add_argument("--backup", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument(
        "--report-json",
        type=Path,
        default=None,
        help="Optional report path (default: data/production/placeholder_upgrade_report_<ts>.json)",
    )
    return p.parse_args()


def now_ts() -> str:
    return datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def append_flag(flags: str, flag: str) -> str:
    items = [x.strip() for x in normalize(flags).split("|") if x.strip()]
    if flag not in items:
        items.append(flag)
    return "|".join(items)


def clean_quote(text: str, max_len: int = 180) -> str:
    t = normalize(text)
    if len(t) > max_len:
        t = t[: max_len - 3].rstrip() + "..."
    return t


def unresolved_to_hint(value: str, default_label: str) -> str:
    v = normalize(value)
    if not v:
        return default_label
    if not v.upper().startswith("UNRESOLVED:"):
        return v
    parts = v.split(":", 2)
    if len(parts) == 3 and parts[2].strip():
        return parts[2].strip().replace("_", " ")
    return default_label


def synthesize_table_statement(row: Dict[str, str]) -> str:
    env = unresolved_to_hint(row.get("environment_canonical_id", ""), "environment factor")
    out = unresolved_to_hint(row.get("outcome_canonical_id", ""), "outcome metric")

    if env == "environment factor":
        env_var = normalize(row.get("environment_variable", ""))
        if env_var:
            env = env_var
    if out == "outcome metric":
        out_var = normalize(row.get("outcome_variable", ""))
        if out_var:
            out = out_var

    direction = normalize(row.get("effect_direction", "")).lower()
    direction_phrase = "association"
    if direction in {"positive", "negative", "null"}:
        direction_phrase = f"{direction} association"

    quote = clean_quote(row.get("source_quote", ""))
    if quote:
        return f"Table-derived claim: {env} -> {out} ({direction_phrase}); extracted row text: {quote}."
    return f"Table-derived claim: {env} -> {out} ({direction_phrase}); extracted from low-fidelity table row."


def load_csv(path: Path) -> tuple[List[str], List[Dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames or []), list(r)


def write_csv_atomic(path: Path, fieldnames: Sequence[str], rows: Sequence[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = NamedTemporaryFile("w", encoding="utf-8", newline="", delete=False, dir=str(path.parent))
    try:
        w = csv.DictWriter(tmp, fieldnames=list(fieldnames))
        w.writeheader()
        w.writerows(rows)
    finally:
        tmp.close()
    Path(tmp.name).replace(path)


def merge_quality_flags(prod_flags: str, rea_flags: str) -> str:
    out = normalize(prod_flags)
    for f in [x.strip() for x in normalize(rea_flags).split("|") if x.strip()]:
        out = append_flag(out, f)
    return out


def main() -> int:
    args = parse_args()

    if not args.production_csv.exists():
        raise SystemExit(f"Missing production CSV: {args.production_csv}")
    if not args.reaudit_csv.exists():
        raise SystemExit(f"Missing re-audit CSV: {args.reaudit_csv}")

    re_rows_by_claim: Dict[str, Dict[str, str]] = {}
    for row in csv.DictReader(args.reaudit_csv.open(encoding="utf-8", newline="")):
        cid = normalize(row.get("claim_id", ""))
        if cid:
            re_rows_by_claim[cid] = row

    fieldnames, prod_rows = load_csv(args.production_csv)
    for col in ["quality_flag", "needs_verification", "statement", "node_type", "edge_type"]:
        if col not in fieldnames:
            fieldnames.append(col)

    stats = {
        "rows_total": len(prod_rows),
        "placeholder_rows_before": 0,
        "placeholder_rows_after": 0,
        "matched_claim_ids_in_reaudit": 0,
        "upgraded_from_reaudit": 0,
        "auto_reconstructed_from_table": 0,
        "flagged_auto_reconstructed": 0,
    }

    for row in prod_rows:
        if normalize(row.get("evidence_level", "")) != "pdf_table_extracted":
            continue
        if normalize(row.get("statement", "")) != PLACEHOLDER:
            continue

        stats["placeholder_rows_before"] += 1
        cid = normalize(row.get("claim_id", ""))
        rea = re_rows_by_claim.get(cid)

        upgraded = False
        if rea is not None:
            stats["matched_claim_ids_in_reaudit"] += 1
            rea_statement = normalize(rea.get("statement", ""))
            if rea_statement and rea_statement != PLACEHOLDER:
                row["statement"] = rea_statement
                for key in [
                    "node_type",
                    "edge_type",
                    "relation_type_hint",
                    "argument_relation_type",
                    "argument_relation",
                    "environment_canonical_id",
                    "outcome_canonical_id",
                    "effect_direction",
                ]:
                    rv = normalize(rea.get(key, ""))
                    if rv:
                        row[key] = rv
                row["quality_flag"] = merge_quality_flags(row.get("quality_flag", ""), rea.get("quality_flag", ""))
                upgraded = True
                stats["upgraded_from_reaudit"] += 1

        if not upgraded:
            row["statement"] = synthesize_table_statement(row)
            row["quality_flag"] = append_flag(row.get("quality_flag", ""), "auto_reconstructed_from_table")
            row["needs_verification"] = "true"
            stats["auto_reconstructed_from_table"] += 1
            stats["flagged_auto_reconstructed"] += 1

        if normalize(row.get("statement", "")) == PLACEHOLDER:
            stats["placeholder_rows_after"] += 1

    ts = now_ts()
    report_path = args.report_json or Path(f"data/production/placeholder_upgrade_report_{ts}.json")
    report = {
        "timestamp": datetime.now(tz=UTC).isoformat(),
        "production_csv": str(args.production_csv),
        "reaudit_csv": str(args.reaudit_csv),
        "dry_run": bool(args.dry_run),
        "stats": stats,
    }

    if args.dry_run:
        print(json.dumps(report, indent=2))
        return 0

    if args.backup:
        backup_path = args.production_csv.with_name(f"{args.production_csv.stem}.backup_before_placeholder_upgrade_{ts}{args.production_csv.suffix}")
        shutil.copy2(args.production_csv, backup_path)
        report["backup_csv"] = str(backup_path)

    write_csv_atomic(args.production_csv, fieldnames, prod_rows)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
