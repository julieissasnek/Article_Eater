#!/usr/bin/env python3
"""Merge table-remake outputs into production confirmed rows for target papers."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, List, Sequence

UTC = timezone.utc


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--production-csv", type=Path, default=Path("data/production/realtime_pdf_confirmed_rows.csv"))
    p.add_argument("--remake-confirmed-csv", type=Path, default=Path("data/review/table_remake_confirmed.csv"))
    p.add_argument("--remake-paper-queue-csv", type=Path, default=Path("data/review/table_remake_paper_queue.csv"))
    p.add_argument("--backup", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--report-json", type=Path, default=None)
    return p.parse_args()


def now_ts() -> str:
    return datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")


def normalize(v: str) -> str:
    return str(v or "").strip()


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


def row_to_schema(row: Dict[str, str], schema: Sequence[str]) -> Dict[str, str]:
    return {k: row.get(k, "") for k in schema}


def main() -> int:
    args = parse_args()
    for p in (args.production_csv, args.remake_confirmed_csv, args.remake_paper_queue_csv):
        if not p.exists():
            raise SystemExit(f"Missing file: {p}")

    prod_fields, prod_rows = load_csv(args.production_csv)
    _, remake_rows_raw = load_csv(args.remake_confirmed_csv)
    _, remake_queue_rows = load_csv(args.remake_paper_queue_csv)

    target_papers = {normalize(r.get("paper_id", "")) for r in remake_queue_rows if normalize(r.get("paper_id", ""))}

    prod_table_by_paper: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    kept_rows: List[Dict[str, str]] = []
    removed_table_rows = 0

    for row in prod_rows:
        pid = normalize(row.get("paper_id", ""))
        ev = normalize(row.get("evidence_level", ""))
        if pid in target_papers and ev == "pdf_table_extracted":
            prod_table_by_paper[pid].append(row)
            removed_table_rows += 1
            continue
        kept_rows.append(row)

    # Deduplicate remake rows by claim_id, keeping last occurrence.
    remake_by_claim: Dict[str, Dict[str, str]] = {}
    remake_table_by_paper: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in remake_rows_raw:
        pid = normalize(row.get("paper_id", ""))
        if pid not in target_papers:
            continue
        if normalize(row.get("evidence_level", "")) != "pdf_table_extracted":
            continue
        cid = normalize(row.get("claim_id", ""))
        if not cid:
            continue
        remake_by_claim[cid] = row

    for row in remake_by_claim.values():
        pid = normalize(row.get("paper_id", ""))
        remake_table_by_paper[pid].append(row)

    replacement_rows: List[Dict[str, str]] = []
    papers_with_remake = 0
    papers_fallback_original = 0

    for pid in sorted(target_papers):
        rem = remake_table_by_paper.get(pid, [])
        if rem:
            papers_with_remake += 1
            replacement_rows.extend(row_to_schema(r, prod_fields) for r in rem)
        else:
            papers_fallback_original += 1
            replacement_rows.extend(row_to_schema(r, prod_fields) for r in prod_table_by_paper.get(pid, []))

    merged_rows = kept_rows + replacement_rows

    report = {
        "timestamp": datetime.now(tz=UTC).isoformat(),
        "production_csv": str(args.production_csv),
        "remake_confirmed_csv": str(args.remake_confirmed_csv),
        "target_papers": len(target_papers),
        "papers_with_remake_rows": papers_with_remake,
        "papers_fallback_original_rows": papers_fallback_original,
        "removed_original_table_rows": removed_table_rows,
        "added_replacement_rows": len(replacement_rows),
        "rows_before": len(prod_rows),
        "rows_after": len(merged_rows),
        "dry_run": bool(args.dry_run),
    }

    if args.dry_run:
        print(json.dumps(report, indent=2))
        return 0

    if args.backup:
        ts = now_ts()
        backup_path = args.production_csv.with_name(f"{args.production_csv.stem}.backup_before_table_remake_merge_{ts}{args.production_csv.suffix}")
        shutil.copy2(args.production_csv, backup_path)
        report["backup_csv"] = str(backup_path)

    write_csv_atomic(args.production_csv, prod_fields, merged_rows)

    report_path = args.report_json or Path(f"data/production/table_remake_merge_report_{now_ts()}.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
