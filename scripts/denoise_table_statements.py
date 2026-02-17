#!/usr/bin/env python3
"""Rewrite garbled table statements into stable, non-garbled summaries."""

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


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--confirmed-csv", type=Path, default=Path("data/production/realtime_pdf_confirmed_rows.csv"))
    p.add_argument("--backup", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--report-json", type=Path, default=None)
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


def is_garbled_statement(text: str) -> bool:
    s = normalize(text)
    if not s:
        return True
    low = s.lower()
    if low.startswith("col_") or "col_1:" in low or "col_2:" in low:
        return True
    letters = sum(ch.isalpha() for ch in s)
    digits = sum(ch.isdigit() for ch in s)
    non_space = sum(not ch.isspace() for ch in s)
    punctuation = sum(not ch.isalnum() and not ch.isspace() for ch in s)
    if letters < 12 and len(s) < 50:
        return True
    if letters > 0 and digits / max(1, letters) > 1.8:
        return True
    if non_space > 0 and punctuation / non_space > 0.35 and len(s) < 80:
        return True
    if re.search(r"\b\d+\.\d+\s+\d+\.\d+\b", s):
        return True
    if re.search(r"\b[a-z]{0,2}\d{1,2}\.\d\b", low):
        return True
    return False


def safe_summary(row: Dict[str, str]) -> str:
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
    relation = "association"
    if direction in {"positive", "negative", "null"}:
        relation = f"{direction} association"
    return (
        f"Table-derived finding links {env} to {out} with {relation}; "
        "numeric row text was denoised due OCR fragmentation."
    )


def load_rows(path: Path) -> tuple[List[str], List[Dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames or []), list(r)


def write_rows_atomic(path: Path, fieldnames: Sequence[str], rows: Sequence[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = NamedTemporaryFile("w", encoding="utf-8", newline="", delete=False, dir=str(path.parent))
    try:
        w = csv.DictWriter(tmp, fieldnames=list(fieldnames))
        w.writeheader()
        w.writerows(rows)
    finally:
        tmp.close()
    Path(tmp.name).replace(path)


def main() -> int:
    args = parse_args()
    if not args.confirmed_csv.exists():
        raise SystemExit(f"Missing CSV: {args.confirmed_csv}")

    fieldnames, rows = load_rows(args.confirmed_csv)
    for col in ["quality_flag", "needs_verification", "statement"]:
        if col not in fieldnames:
            fieldnames.append(col)

    stats = {
        "rows_total": len(rows),
        "table_rows_scanned": 0,
        "garbled_rows_found": 0,
        "garbled_rows_rewritten": 0,
    }

    for row in rows:
        if normalize(row.get("evidence_level", "")) != "pdf_table_extracted":
            continue
        stats["table_rows_scanned"] += 1
        statement = normalize(row.get("statement", ""))
        if not is_garbled_statement(statement):
            continue
        stats["garbled_rows_found"] += 1
        row["statement"] = safe_summary(row)
        row["quality_flag"] = append_flag(row.get("quality_flag", ""), "auto_denoised_statement")
        row["needs_verification"] = "true"
        stats["garbled_rows_rewritten"] += 1

    ts = now_ts()
    report_path = args.report_json or Path(f"data/production/table_statement_denoise_report_{ts}.json")
    report = {
        "timestamp": datetime.now(tz=UTC).isoformat(),
        "confirmed_csv": str(args.confirmed_csv),
        "dry_run": bool(args.dry_run),
        "stats": stats,
    }

    if args.dry_run:
        print(json.dumps(report, indent=2))
        return 0

    if args.backup:
        backup_path = args.confirmed_csv.with_name(f"{args.confirmed_csv.stem}.backup_before_denoise_{ts}{args.confirmed_csv.suffix}")
        shutil.copy2(args.confirmed_csv, backup_path)
        report["backup_csv"] = str(backup_path)

    write_rows_atomic(args.confirmed_csv, fieldnames, rows)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
