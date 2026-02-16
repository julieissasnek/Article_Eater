#!/usr/bin/env python3
"""
Data-level checks to verify pipeline behavior matches policy intent.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify realtime pipeline expectations.")
    parser.add_argument(
        "--queue-csv",
        default="data/production/realtime_pdf_completion_queue.csv",
        help="Queue CSV path",
    )
    parser.add_argument(
        "--confirmed-csv",
        default="data/review/tranche80_confirmed_rows.csv",
        help="Confirmed rows CSV path (tranche/review output)",
    )
    parser.add_argument(
        "--recent-rows",
        type=int,
        default=1901,
        help="How many trailing confirmed rows to evaluate",
    )
    parser.add_argument(
        "--min-needs-verification-rate",
        type=float,
        default=0.95,
        help="Minimum expected rate for needs_verification=true in recent rows",
    )
    parser.add_argument(
        "--min-quality-flag-rate",
        type=float,
        default=0.95,
        help="Minimum expected rate for needs_article_type_verification marker",
    )
    return parser.parse_args()


def read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def to_bool(value: str) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


def pct(n: int, d: int) -> float:
    return (n / d) if d else 0.0


def main() -> int:
    args = parse_args()
    queue_rows = read_csv(Path(args.queue_csv))
    confirmed_rows = read_csv(Path(args.confirmed_csv))

    degraded_rows = 0
    for row in queue_rows:
        prior = str(row.get("prior_status", "")).strip()
        now = str(row.get("status", "")).strip()
        if prior == "completed_pdf_extracted" and now in {
            "error_pdf_timeout",
            "error_pdf_processing",
            "completed_pdf_no_claims",
        }:
            degraded_rows += 1

    recent = confirmed_rows[-max(1, int(args.recent_rows)) :] if confirmed_rows else []
    needs_verification_true = sum(1 for row in recent if to_bool(row.get("needs_verification", "")))
    quality_flag_marked = sum(
        1
        for row in recent
        if "needs_article_type_verification" in str(row.get("quality_flag", "") or "")
    )

    needs_rate = pct(needs_verification_true, len(recent))
    quality_rate = pct(quality_flag_marked, len(recent))

    print("Pipeline expectation checks:")
    print(f"  queue_rows: {len(queue_rows)}")
    print(f"  confirmed_rows_total: {len(confirmed_rows)}")
    print(f"  recent_rows_checked: {len(recent)}")
    print(f"  degraded_from_prior_extracted: {degraded_rows}")
    print(f"  needs_verification_true: {needs_verification_true} ({needs_rate:.4f})")
    print(f"  qualityflag_type_verification: {quality_flag_marked} ({quality_rate:.4f})")

    failures: List[str] = []
    if degraded_rows > 0:
        failures.append("degraded_rows_present")
    if recent and needs_rate < float(args.min_needs_verification_rate):
        failures.append("needs_verification_rate_below_threshold")
    if recent and quality_rate < float(args.min_quality_flag_rate):
        failures.append("quality_flag_rate_below_threshold")

    if failures:
        print("expectation_gate: FAIL")
        print(f"failure_reasons: {'|'.join(failures)}")
        return 1

    print("expectation_gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
