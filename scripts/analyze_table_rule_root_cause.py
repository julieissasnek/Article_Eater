#!/usr/bin/env python3
"""Compare production vs re-audit table-derived rules to attribute garbling root cause."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

UTC = timezone.utc


@dataclass
class PaperStats:
    table_rows: int = 0
    garbled_rows: int = 0

    @property
    def garbled_rate(self) -> Optional[float]:
        if self.table_rows <= 0:
            return None
        return float(self.garbled_rows) / float(self.table_rows)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--queue-csv",
        type=Path,
        default=Path("data/review/garbled_rules_reaudit_queue.csv"),
        help="Queue file used for re-audit selection",
    )
    p.add_argument(
        "--production-confirmed-csv",
        type=Path,
        default=Path("data/production/realtime_pdf_confirmed_rows.csv"),
    )
    p.add_argument(
        "--reaudit-confirmed-csv",
        type=Path,
        default=Path("data/review/garbled_rules_reaudit_confirmed.csv"),
    )
    p.add_argument(
        "--output-json",
        type=Path,
        default=Path("data/review/garbled_rules_root_cause_report.json"),
    )
    p.add_argument(
        "--output-csv",
        type=Path,
        default=Path("data/review/garbled_rules_root_cause_report.csv"),
    )
    p.add_argument(
        "--include-all-queued",
        action="store_true",
        help="Analyze all queue papers; default is only completed_pdf_extracted",
    )
    p.add_argument(
        "--high-garbled-threshold",
        type=float,
        default=0.40,
        help="Rate threshold considered clearly garbled",
    )
    p.add_argument(
        "--low-garbled-threshold",
        type=float,
        default=0.20,
        help="Rate threshold considered low/clean",
    )
    return p.parse_args()


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


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
    return False


def iter_rows(path: Path) -> Iterable[Dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            yield row


def collect_target_papers(queue_csv: Path, include_all: bool) -> Set[str]:
    wanted: Set[str] = set()
    for row in iter_rows(queue_csv):
        pid = normalize(row.get("paper_id", ""))
        status = normalize(row.get("status", ""))
        if not pid:
            continue
        if include_all:
            wanted.add(pid)
            continue
        if status == "completed_pdf_extracted":
            wanted.add(pid)
    return wanted


def collect_stats(confirmed_csv: Path, target_papers: Set[str]) -> Dict[str, PaperStats]:
    stats: Dict[str, PaperStats] = defaultdict(PaperStats)
    for row in iter_rows(confirmed_csv):
        pid = normalize(row.get("paper_id", ""))
        if pid not in target_papers:
            continue
        if normalize(row.get("evidence_level", "")) != "pdf_table_extracted":
            continue
        paper = stats[pid]
        paper.table_rows += 1
        if is_garbled_statement(row.get("statement", "")):
            paper.garbled_rows += 1
    return stats


def classify(
    prod_rate: Optional[float],
    reaudit_rate: Optional[float],
    prod_rows: int,
    reaudit_rows: int,
    high: float,
    low: float,
) -> str:
    if prod_rows <= 0 and reaudit_rows <= 0:
        return "no_table_rows"
    if prod_rows > 0 and reaudit_rows <= 0:
        return "reaudit_missing_table_rows"
    if reaudit_rows > 0 and prod_rows <= 0:
        return "prod_missing_table_rows"

    if prod_rate is None or reaudit_rate is None:
        return "insufficient_data"

    if prod_rate >= high and reaudit_rate >= high:
        return "table_fault_reproduced"
    if prod_rate >= high and reaudit_rate <= low:
        return "mapping_or_historical_fault_likely"
    if prod_rate <= low and reaudit_rate >= high:
        return "possible_reaudit_extraction_regression"
    return "mixed_or_borderline"


def main() -> int:
    args = parse_args()

    for required in (args.queue_csv, args.production_confirmed_csv, args.reaudit_confirmed_csv):
        if not required.exists():
            raise SystemExit(f"Missing required file: {required}")

    target_papers = collect_target_papers(args.queue_csv, include_all=args.include_all_queued)
    prod_stats = collect_stats(args.production_confirmed_csv, target_papers)
    rea_stats = collect_stats(args.reaudit_confirmed_csv, target_papers)

    rows: List[Dict[str, object]] = []
    classification_counts: Counter[str] = Counter()

    prod_total_rows = 0
    prod_total_garbled = 0
    rea_total_rows = 0
    rea_total_garbled = 0

    for pid in sorted(target_papers):
        prod = prod_stats.get(pid, PaperStats())
        rea = rea_stats.get(pid, PaperStats())

        prod_rate = prod.garbled_rate
        rea_rate = rea.garbled_rate

        classification = classify(
            prod_rate=prod_rate,
            reaudit_rate=rea_rate,
            prod_rows=prod.table_rows,
            reaudit_rows=rea.table_rows,
            high=args.high_garbled_threshold,
            low=args.low_garbled_threshold,
        )
        classification_counts[classification] += 1

        prod_total_rows += prod.table_rows
        prod_total_garbled += prod.garbled_rows
        rea_total_rows += rea.table_rows
        rea_total_garbled += rea.garbled_rows

        rows.append(
            {
                "paper_id": pid,
                "production_table_rows": prod.table_rows,
                "production_garbled_rows": prod.garbled_rows,
                "production_garbled_rate": None if prod_rate is None else round(prod_rate, 6),
                "reaudit_table_rows": rea.table_rows,
                "reaudit_garbled_rows": rea.garbled_rows,
                "reaudit_garbled_rate": None if rea_rate is None else round(rea_rate, 6),
                "classification": classification,
            }
        )

    prod_rate_global = (float(prod_total_garbled) / float(prod_total_rows)) if prod_total_rows else None
    rea_rate_global = (float(rea_total_garbled) / float(rea_total_rows)) if rea_total_rows else None

    report = {
        "generated_at": datetime.now(tz=UTC).isoformat(),
        "queue_csv": str(args.queue_csv),
        "production_confirmed_csv": str(args.production_confirmed_csv),
        "reaudit_confirmed_csv": str(args.reaudit_confirmed_csv),
        "scope": "all_queue_papers" if args.include_all_queued else "completed_pdf_extracted_only",
        "thresholds": {
            "high_garbled_threshold": args.high_garbled_threshold,
            "low_garbled_threshold": args.low_garbled_threshold,
        },
        "summary": {
            "target_paper_count": len(target_papers),
            "classification_counts": dict(classification_counts),
            "production_total_table_rows": prod_total_rows,
            "production_total_garbled_rows": prod_total_garbled,
            "production_global_garbled_rate": None if prod_rate_global is None else round(prod_rate_global, 6),
            "reaudit_total_table_rows": rea_total_rows,
            "reaudit_total_garbled_rows": rea_total_garbled,
            "reaudit_global_garbled_rate": None if rea_rate_global is None else round(rea_rate_global, 6),
        },
        "papers": rows,
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "paper_id",
                "production_table_rows",
                "production_garbled_rows",
                "production_garbled_rate",
                "reaudit_table_rows",
                "reaudit_garbled_rows",
                "reaudit_garbled_rate",
                "classification",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(json.dumps(report["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
