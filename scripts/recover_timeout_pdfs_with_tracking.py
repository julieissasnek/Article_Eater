#!/usr/bin/env python3
"""
Recover timeout PDFs via staged preprocess/repair/re-extract with gain tracking.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Recover timeout PDFs with tracked gains.")
    parser.add_argument(
        "--queue-csv",
        default="data/production/realtime_pdf_completion_queue.csv",
        help="Queue CSV path",
    )
    parser.add_argument(
        "--status",
        default="error_pdf_timeout",
        help="Source status to recover",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="0 means all timeout rows",
    )
    parser.add_argument(
        "--requeue-status",
        default="queued_timeout_recovery",
        help="Queue status used for recovery processing",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=180,
        help="Per-paper extraction timeout for safe runner",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=8,
        help="Preprocess worker count",
    )
    parser.add_argument(
        "--report-json",
        default="data/review/timeout_recovery_report.json",
        help="Report JSON output path",
    )
    parser.add_argument(
        "--report-csv",
        default="data/review/timeout_recovery_details.csv",
        help="Report CSV output path",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Prepare report only without mutating queue",
    )
    return parser.parse_args()


def read_rows(path: Path) -> List[Dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_rows(path: Path, rows: List[Dict[str, str]]) -> None:
    fieldnames = []
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


def run(cmd: List[str]) -> None:
    subprocess.run(cmd, check=True)


def main() -> int:
    args = parse_args()
    queue_path = Path(args.queue_csv)
    rows = read_rows(queue_path)
    selected = [r for r in rows if str(r.get("status", "")).strip() == args.status]
    if args.limit and args.limit > 0:
        selected = selected[: args.limit]
    selected_ids = {r.get("paper_id", "") for r in selected}
    print(f"selected_rows={len(selected)}")
    if not selected:
        return 0

    baseline = {
        r["paper_id"]: {
            "status": r.get("status", ""),
            "n_claims": int(float(r.get("n_claims") or 0)),
            "n_tables": int(float(r.get("n_tables") or 0)),
            "preprocess_status": r.get("preprocess_status", ""),
            "pdf_path": r.get("pdf_path", ""),
        }
        for r in selected
    }

    if args.dry_run:
        print("dry_run=True; no recovery executed")
        return 0

    now_iso = datetime.now(timezone.utc).isoformat()
    for row in rows:
        pid = row.get("paper_id", "")
        if pid not in selected_ids:
            continue
        row["prior_status"] = row.get("status", "")
        row["status"] = args.requeue_status
        row["queued_at"] = now_iso
        row["processed_at"] = ""
        row["error"] = ""
        reason = str(row.get("reason", "") or "").strip()
        tag = "timeout_recovery_pipeline"
        row["reason"] = f"{reason}|{tag}" if reason else tag
    write_rows(queue_path, rows)

    project = queue_path.parent.parent
    root = queue_path.parent.parent.parent
    # Run preprocess on queued timeout tranche
    run(
        [
            "python3",
            "scripts/preprocess_pdf_queue.py",
            "--queue-csv",
            str(queue_path),
            "--queued-only",
            "--force",
            "--batch-size",
            str(len(selected)),
            "--max-workers",
            str(max(1, int(args.max_workers))),
            "--max-pages",
            "30",
        ]
    )
    # Repair problematic preprocess rows (global by status, but usually limited)
    run(
        [
            "python3",
            "scripts/repair_problem_pdfs.py",
            "--queue-csv",
            str(queue_path),
            "--statuses",
            "quarantine,error",
        ]
    )
    # Re-preprocess to refresh status after repair
    run(
        [
            "python3",
            "scripts/preprocess_pdf_queue.py",
            "--queue-csv",
            str(queue_path),
            "--queued-only",
            "--force",
            "--batch-size",
            str(len(selected)),
            "--max-workers",
            str(max(1, int(args.max_workers))),
            "--max-pages",
            "30",
        ]
    )
    # Safe extraction pass with timeout and preprocess filtering
    run(
        [
            "python3",
            "scripts/reprocess_article_type_tranche_safe.py",
            "--queue-csv",
            str(queue_path),
            "--status-prefix",
            args.requeue_status,
            "--max-rows",
            str(len(selected)),
            "--timeout-seconds",
            str(max(30, int(args.timeout_seconds))),
            "--prioritize-preprocessed",
            "--skip-preprocess-quarantine",
            "--confirmed-csv",
            "data/review/timeout_recovery_confirmed_rows.csv",
            "--no-claims-csv",
            "data/review/timeout_recovery_no_claims_review.csv",
            "--audit-jsonl",
            "data/review/timeout_recovery_extraction_audit.jsonl",
            "--manual-review-csv",
            "data/review/timeout_recovery_table_quality_manual_queue.csv",
            "--article-type-review-csv",
            "data/review/timeout_recovery_article_type_manual_queue.csv",
        ]
    )

    post_rows = read_rows(queue_path)
    post_by_id = {r.get("paper_id", ""): r for r in post_rows}

    details: List[Dict[str, str]] = []
    gains = {
        "selected_rows": len(selected),
        "recovered_to_extracted": 0,
        "still_no_claims": 0,
        "still_timeout": 0,
        "new_processing_errors": 0,
        "total_claim_delta": 0,
        "positive_claim_delta_rows": 0,
        "preprocess_ready_after": 0,
        "preprocess_quarantine_after": 0,
        "preprocess_error_after": 0,
        "repaired_pdf_path_rows": 0,
    }

    for pid in selected_ids:
        b = baseline.get(pid, {})
        p = post_by_id.get(pid, {})
        b_status = str(b.get("status", ""))
        p_status = str(p.get("status", ""))
        b_claims = int(b.get("n_claims", 0))
        p_claims = int(float(p.get("n_claims") or 0))
        d_claims = p_claims - b_claims
        gains["total_claim_delta"] += d_claims
        if d_claims > 0:
            gains["positive_claim_delta_rows"] += 1
        if p_status == "completed_pdf_extracted":
            gains["recovered_to_extracted"] += 1
        elif p_status == "completed_pdf_no_claims":
            gains["still_no_claims"] += 1
        elif p_status == "error_pdf_timeout":
            gains["still_timeout"] += 1
        elif p_status.startswith("error_"):
            gains["new_processing_errors"] += 1

        pre = str(p.get("preprocess_status", "")).strip().lower()
        if pre == "ready":
            gains["preprocess_ready_after"] += 1
        elif pre == "quarantine":
            gains["preprocess_quarantine_after"] += 1
        elif pre == "error":
            gains["preprocess_error_after"] += 1

        repaired = "data/production/pdf_repaired/" in str(p.get("pdf_path", ""))
        if repaired:
            gains["repaired_pdf_path_rows"] += 1

        details.append(
            {
                "paper_id": pid,
                "baseline_status": b_status,
                "post_status": p_status,
                "baseline_n_claims": str(b_claims),
                "post_n_claims": str(p_claims),
                "claim_delta": str(d_claims),
                "baseline_preprocess_status": str(b.get("preprocess_status", "")),
                "post_preprocess_status": str(p.get("preprocess_status", "")),
                "post_pdf_path": str(p.get("pdf_path", "")),
                "was_repaired_pdf_path": "yes" if repaired else "no",
                "title": str(p.get("title", "")),
            }
        )

    details.sort(key=lambda r: int(r.get("claim_delta", "0")), reverse=True)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_status": args.status,
        "requeue_status": args.requeue_status,
        "timeout_seconds": int(args.timeout_seconds),
        "gains": gains,
        "post_status_counts": dict(Counter(r["post_status"] for r in details)),
    }
    report_json = Path(args.report_json)
    report_csv = Path(args.report_csv)
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding="utf-8")
    write_rows(report_csv, details)

    print(json.dumps(report, indent=2))
    print(f"details_csv={report_csv}")
    print(f"report_json={report_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

