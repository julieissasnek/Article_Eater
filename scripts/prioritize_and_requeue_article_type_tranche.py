#!/usr/bin/env python3
"""
Prioritize article-type review rows and optionally requeue a top tranche
for full PDF re-extraction.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prioritize/requeue article-type review tranche.")
    parser.add_argument(
        "--queue-csv",
        default="data/production/realtime_pdf_completion_queue.csv",
        help="Queue CSV path",
    )
    parser.add_argument(
        "--review-csv",
        default="data/review/article_type_manual_queue.csv",
        help="Article-type review CSV path",
    )
    parser.add_argument(
        "--output-csv",
        default="data/review/article_type_priority_tranche.csv",
        help="Priority ranking output CSV path",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=80,
        help="Number of highest-priority papers to mark for reprocessing",
    )
    parser.add_argument(
        "--apply-requeue",
        action="store_true",
        help="Apply status update in queue CSV for selected top tranche",
    )
    return parser.parse_args()


def _to_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _to_int(value: object, default: int = 0) -> int:
    try:
        return int(float(value))
    except Exception:
        return default


def read_rows(path: Path) -> List[Dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_rows(path: Path, rows: List[Dict[str, str]]) -> None:
    fieldnames: List[str] = []
    seen = set()
    for row in rows:
        for key in row.keys():
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def score_row(queue_row: Dict[str, str], review_row: Dict[str, str]) -> Tuple[float, List[str]]:
    score = 0.0
    reasons: List[str] = []
    status = str(queue_row.get("status", "")).strip()
    family = str(queue_row.get("article_type_family", "")).strip()
    predicted = str(queue_row.get("article_type_predicted_family", "")).strip()
    confidence = _to_float(queue_row.get("article_type_confidence", 0.0), default=0.0)
    margin = _to_float(queue_row.get("article_type_margin", 0.0), default=0.0)
    n_claims = _to_int(queue_row.get("n_claims", 0), default=0)
    flags = str(review_row.get("type_review_flags", "")).strip()

    if status == "error_pdf_processing":
        score += 110
        reasons.append("status:error")
    elif status == "completed_pdf_no_claims":
        score += 85
        reasons.append("status:no_claims")
    elif status == "completed_pdf_extracted":
        score += 30
        reasons.append("status:extracted")

    if family == "unknown" and predicted and predicted != "unknown":
        score += 55
        reasons.append("unknown_with_predicted_family")

    if predicted == "empirical_v2":
        score += 40
        reasons.append("predicted_empirical")
        if status == "completed_pdf_no_claims":
            score += 30
            reasons.append("empirical_no_claims")
    elif predicted in {"meta_analysis", "systematic_review", "narrative_review"}:
        score += 18
        reasons.append("predicted_synthesis")
    elif predicted in {"theoretical", "conceptual_framework"}:
        score += 16
        reasons.append("predicted_theoretical")

    if confidence >= 0.80:
        score += 20
        reasons.append("high_confidence")
    elif confidence >= 0.70:
        score += 12
        reasons.append("mid_confidence")

    if margin >= 1.0:
        score += 10
        reasons.append("high_margin")
    elif margin >= 0.6:
        score += 6
        reasons.append("mid_margin")

    if "low_margin" in flags:
        score += 4
        reasons.append("low_margin_flag")
    if "low_confidence" in flags and predicted and predicted != "unknown":
        score += 6
        reasons.append("low_confidence_with_predicted_family")

    claim_boost = min(n_claims, 250) / 10.0
    if claim_boost > 0:
        score += claim_boost
        reasons.append("claim_volume")

    return score, reasons


def main() -> int:
    args = parse_args()
    queue_path = Path(args.queue_csv)
    review_path = Path(args.review_csv)
    output_path = Path(args.output_csv)
    if not queue_path.exists():
        print(f"Queue CSV not found: {queue_path}")
        return 1
    if not review_path.exists():
        print(f"Review CSV not found: {review_path}")
        return 1

    queue_rows = read_rows(queue_path)
    review_rows = read_rows(review_path)
    queue_by_pid = {str(r.get("paper_id", "")).strip(): r for r in queue_rows}

    ranked: List[Dict[str, str]] = []
    for r in review_rows:
        pid = str(r.get("paper_id", "")).strip()
        q = queue_by_pid.get(pid)
        if not q:
            continue
        score, reasons = score_row(q, r)
        ranked.append(
            {
                "paper_id": pid,
                "doi": q.get("doi", ""),
                "title": q.get("title", ""),
                "year": q.get("year", ""),
                "venue": q.get("venue", ""),
                "status_before": q.get("status", ""),
                "n_tables_before": q.get("n_tables", ""),
                "n_claims_before": q.get("n_claims", ""),
                "article_type_family": q.get("article_type_family", ""),
                "article_type_predicted_family": q.get("article_type_predicted_family", ""),
                "article_type_confidence": q.get("article_type_confidence", ""),
                "article_type_margin": q.get("article_type_margin", ""),
                "type_review_flags": r.get("type_review_flags", ""),
                "priority_score": f"{score:.3f}",
                "priority_reasons": "|".join(reasons),
            }
        )

    ranked.sort(key=lambda row: float(row.get("priority_score", "0") or 0.0), reverse=True)
    top_n = max(1, int(args.top_n))
    selected = ranked[:top_n]
    for i, row in enumerate(ranked, start=1):
        row["priority_rank"] = str(i)
        row["selected_for_reprocess"] = "yes" if i <= top_n else "no"
    write_rows(output_path, ranked)

    print(f"Review rows ranked: {len(ranked)}")
    print(f"Top tranche size: {len(selected)}")
    print(f"Priority CSV: {output_path}")

    if args.apply_requeue and selected:
        now_iso = datetime.now(timezone.utc).isoformat()
        selected_ids = {row["paper_id"] for row in selected}
        touched = 0
        for row in queue_rows:
            pid = str(row.get("paper_id", "")).strip()
            if pid not in selected_ids:
                continue
            if str(row.get("status", "")).startswith("queued_"):
                continue
            row["prior_status"] = row.get("status", "")
            row["prior_n_tables"] = row.get("n_tables", "")
            row["prior_n_claims"] = row.get("n_claims", "")
            row["status"] = "queued_article_type_reprocess"
            row["queued_at"] = now_iso
            row["processed_at"] = ""
            prev_reason = str(row.get("reason", "") or "").strip()
            suffix = "article_type_priority_tranche_reprocess"
            row["reason"] = f"{prev_reason}|{suffix}" if prev_reason else suffix
            touched += 1
        write_rows(queue_path, queue_rows)
        print(f"Rows requeued: {touched}")
        print(f"Queue updated: {queue_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

