#!/usr/bin/env python3
"""
Merge per-shard PDF completion outputs back into master production artifacts.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, Iterable, List, Sequence


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Merge shard queue/confirmed outputs into master files.")
    p.add_argument("--shards-dir", type=Path, default=Path("data/production/ag9_shards"))
    p.add_argument(
        "--master-queue",
        type=Path,
        default=Path("data/production/realtime_pdf_completion_queue.csv"),
    )
    p.add_argument(
        "--master-confirmed",
        type=Path,
        default=Path("data/production/realtime_pdf_confirmed_rows.csv"),
    )
    p.add_argument(
        "--master-no-claims",
        type=Path,
        default=Path("data/production/realtime_pdf_no_claims_review.csv"),
    )
    p.add_argument(
        "--master-audit-jsonl",
        type=Path,
        default=Path("data/production/realtime_extraction_audit.jsonl"),
    )
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        return [], []
    with path.open(encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames or []), list(r)


def write_csv_rows(path: Path, fieldnames: Sequence[str], rows: Sequence[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(fieldnames))
        w.writeheader()
        w.writerows(rows)


def list_shard_paths(shards_dir: Path, suffix: str) -> List[Path]:
    return sorted(shards_dir.glob(f"shard_*_{suffix}"))


def merge_queue(master_queue: Path, shard_queues: Iterable[Path], dry_run: bool) -> int:
    mf, master_rows = read_csv_rows(master_queue)
    if not master_rows:
        return 0

    shard_updates: Dict[str, dict[str, str]] = {}
    for sp in shard_queues:
        _, rows = read_csv_rows(sp)
        for row in rows:
            pid = str(row.get("paper_id", "")).strip()
            if pid:
                shard_updates[pid] = row

    changed = 0
    for row in master_rows:
        pid = str(row.get("paper_id", "")).strip()
        update = shard_updates.get(pid)
        if not update:
            continue
        if row != update:
            row.update(update)
            changed += 1

    if dry_run:
        return changed

    out_fields = list(mf)
    for r in master_rows:
        for k in r.keys():
            if k not in out_fields:
                out_fields.append(k)
    write_csv_rows(master_queue, out_fields, master_rows)
    return changed


def merge_no_claims(master_no_claims: Path, shard_no_claims: Iterable[Path], dry_run: bool) -> int:
    mf, master_rows = read_csv_rows(master_no_claims)
    existing = {str(r.get("paper_id", "")).strip() for r in master_rows if str(r.get("paper_id", "")).strip()}
    add_rows: List[dict[str, str]] = []
    for sp in shard_no_claims:
        sf, rows = read_csv_rows(sp)
        if sf:
            for col in sf:
                if col not in mf:
                    mf.append(col)
        for r in rows:
            pid = str(r.get("paper_id", "")).strip()
            if not pid or pid in existing:
                continue
            add_rows.append(r)
            existing.add(pid)

    if dry_run:
        return len(add_rows)

    if add_rows:
        write_csv_rows(master_no_claims, mf, master_rows + add_rows)
    return len(add_rows)


def merge_confirmed(master_confirmed: Path, shard_confirmed: Iterable[Path], dry_run: bool) -> int:
    # Collect union header first.
    fieldnames: List[str] = []
    if master_confirmed.exists():
        with master_confirmed.open(encoding="utf-8", newline="") as f:
            r = csv.DictReader(f)
            fieldnames = list(r.fieldnames or [])

    shard_paths = list(shard_confirmed)
    for sp in shard_paths:
        with sp.open(encoding="utf-8", newline="") as f:
            r = csv.DictReader(f)
            for col in list(r.fieldnames or []):
                if col not in fieldnames:
                    fieldnames.append(col)

    if not fieldnames:
        return 0

    if dry_run:
        existing = set()
        if master_confirmed.exists():
            with master_confirmed.open(encoding="utf-8", newline="") as f:
                r = csv.DictReader(f)
                for row in r:
                    cid = str(row.get("claim_id", "")).strip()
                    if cid:
                        existing.add(cid)
        added = 0
        for sp in shard_paths:
            with sp.open(encoding="utf-8", newline="") as f:
                r = csv.DictReader(f)
                for row in r:
                    cid = str(row.get("claim_id", "")).strip()
                    key = cid or f"__line__{hash(tuple(sorted(row.items())))}"
                    if key in existing:
                        continue
                    existing.add(key)
                    added += 1
        return added

    master_confirmed.parent.mkdir(parents=True, exist_ok=True)
    tmp = NamedTemporaryFile("w", encoding="utf-8", newline="", delete=False, dir=str(master_confirmed.parent))
    added = 0
    existing = set()
    try:
        writer = csv.DictWriter(tmp, fieldnames=fieldnames)
        writer.writeheader()

        if master_confirmed.exists():
            with master_confirmed.open(encoding="utf-8", newline="") as f:
                r = csv.DictReader(f)
                for row in r:
                    cid = str(row.get("claim_id", "")).strip()
                    key = cid or f"__line__{hash(tuple(sorted(row.items())))}"
                    existing.add(key)
                    writer.writerow(row)

        for sp in shard_paths:
            with sp.open(encoding="utf-8", newline="") as f:
                r = csv.DictReader(f)
                for row in r:
                    cid = str(row.get("claim_id", "")).strip()
                    key = cid or f"__line__{hash(tuple(sorted(row.items())))}"
                    if key in existing:
                        continue
                    existing.add(key)
                    writer.writerow(row)
                    added += 1
    finally:
        tmp.close()

    Path(tmp.name).replace(master_confirmed)
    return added


def append_jsonl(master_path: Path, shard_paths: Iterable[Path], dry_run: bool) -> int:
    lines = 0
    for sp in shard_paths:
        if not sp.exists():
            continue
        with sp.open(encoding="utf-8") as f:
            for _ in f:
                lines += 1
    if dry_run or lines == 0:
        return lines
    master_path.parent.mkdir(parents=True, exist_ok=True)
    with master_path.open("a", encoding="utf-8") as out:
        for sp in shard_paths:
            if not sp.exists():
                continue
            with sp.open(encoding="utf-8") as src:
                for line in src:
                    out.write(line)
    return lines


def main() -> int:
    args = parse_args()
    shard_queues = list_shard_paths(args.shards_dir, "queue.csv")
    shard_confirmed = list_shard_paths(args.shards_dir, "confirmed.csv")
    shard_no_claims = list_shard_paths(args.shards_dir, "no_claims.csv")
    shard_audits = list_shard_paths(args.shards_dir, "audit.jsonl")

    queue_changed = merge_queue(args.master_queue, shard_queues, args.dry_run)
    confirmed_added = merge_confirmed(args.master_confirmed, shard_confirmed, args.dry_run)
    no_claims_added = merge_no_claims(args.master_no_claims, shard_no_claims, args.dry_run)
    audit_lines = append_jsonl(args.master_audit_jsonl, shard_audits, args.dry_run)

    print(f"queue_rows_updated={queue_changed}")
    print(f"confirmed_rows_added={confirmed_added}")
    print(f"no_claims_rows_added={no_claims_added}")
    print(f"audit_lines_appended={audit_lines}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
