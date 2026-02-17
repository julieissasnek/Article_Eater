#!/usr/bin/env python3
"""
Create shard queue CSV files from queued PDF completion rows.

Designed for multi-terminal processing without queue write collisions:
- each terminal processes its own shard queue file
- each shard writes to its own confirmed/no-claims/audit outputs
- results are merged back later
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Split queued PDF rows into shard queue CSV files.")
    p.add_argument(
        "--queue-csv",
        type=Path,
        default=Path("data/production/realtime_pdf_completion_queue.csv"),
        help="Master queue CSV",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/production/ag9_shards"),
        help="Output directory for shard files",
    )
    p.add_argument("--num-shards", type=int, default=4, help="Number of shard queues")
    p.add_argument(
        "--status-prefix",
        default="queued_",
        help="Only rows whose status starts with this prefix are sharded",
    )
    p.add_argument("--dry-run", action="store_true", help="Report only")
    return p.parse_args()


def read_rows(path: Path) -> tuple[list[str], list[Dict[str, Any]]]:
    if not path.exists():
        raise FileNotFoundError(f"Queue file not found: {path}")
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_rows(path: Path, fieldnames: Sequence[str], rows: Sequence[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(fieldnames))
        w.writeheader()
        w.writerows(rows)


def stable_shard_index(paper_id: str, num_shards: int) -> int:
    digest = hashlib.sha1(paper_id.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % num_shards


def main() -> int:
    args = parse_args()
    if args.num_shards < 1:
        raise SystemExit("--num-shards must be >= 1")

    fieldnames, rows = read_rows(args.queue_csv)
    queued = [r for r in rows if str(r.get("status", "")).startswith(args.status_prefix)]

    shard_rows: List[List[Dict[str, Any]]] = [[] for _ in range(args.num_shards)]
    for row in queued:
        pid = str(row.get("paper_id", "")).strip()
        if not pid:
            continue
        idx = stable_shard_index(pid, args.num_shards)
        shard_rows[idx].append(row)

    manifest = {
        "source_queue_csv": str(args.queue_csv),
        "output_dir": str(args.output_dir),
        "num_shards": int(args.num_shards),
        "status_prefix": args.status_prefix,
        "queued_rows_total": len(queued),
        "shard_counts": {f"shard_{i+1:02d}": len(shard_rows[i]) for i in range(args.num_shards)},
    }

    print(json.dumps(manifest, indent=2))
    if args.dry_run:
        return 0

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for i in range(args.num_shards):
        shard_id = i + 1
        queue_path = args.output_dir / f"shard_{shard_id:02d}_queue.csv"
        write_rows(queue_path, fieldnames, shard_rows[i])

    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote shard queues to: {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
