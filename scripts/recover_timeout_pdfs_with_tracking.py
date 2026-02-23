#!/usr/bin/env python3
"""
Recover timeout PDFs via staged preprocess/repair/re-extract with gain tracking.

Default behavior:
- Fast retry stage (short timeout, higher throughput)
- Slow retry stage for remaining timeouts (long timeout, lower throughput)
- Dedicated unresolved timeout queue artifact for later targeted processing
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
        help="Source status marker to recover",
    )
    parser.add_argument(
        "--status-field",
        choices=("auto", "status", "retry_status"),
        default="auto",
        help="Which queue column to match against --status (auto tries status then retry_status)",
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
        help="Base queue status prefix used for recovery processing",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=0,
        help="Backward-compatible override: if >0, applies to both fast/slow timeout values",
    )
    parser.add_argument(
        "--fast-timeout-seconds",
        type=int,
        default=120,
        help="Per-paper extraction timeout for fast retry stage",
    )
    parser.add_argument(
        "--slow-timeout-seconds",
        type=int,
        default=300,
        help="Per-paper extraction timeout for slow retry stage",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=8,
        help="Preprocess worker count in fast stage",
    )
    parser.add_argument(
        "--slow-max-workers",
        type=int,
        default=2,
        help="Preprocess worker count in slow stage",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=30,
        help="Max pages scanned per PDF during preprocess",
    )
    parser.add_argument(
        "--skip-slow-stage",
        action="store_true",
        help="Only run fast stage; do not run slow retry stage",
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
        "--remaining-timeout-csv",
        default="data/review/timeout_retry_queue.csv",
        help="Dedicated queue artifact with still-timeout papers after recovery",
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
    fieldnames: list[str] = []
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


def to_int(value: object) -> int:
    try:
        return int(float(value or 0))
    except (TypeError, ValueError):
        return 0


def ids_by_status(rows: List[Dict[str, str]], paper_ids: set[str]) -> Counter:
    c = Counter()
    for row in rows:
        pid = row.get("paper_id", "")
        if pid in paper_ids:
            c[str(row.get("status", "")).strip()] += 1
    return c


def apply_requeue_status(
    rows: List[Dict[str, str]],
    selected_ids: set[str],
    requeue_status: str,
    reason_tag: str,
) -> None:
    now_iso = datetime.now(timezone.utc).isoformat()
    for row in rows:
        pid = row.get("paper_id", "")
        if pid not in selected_ids:
            continue
        row["prior_status"] = row.get("status", "")
        row["prior_n_claims"] = row.get("n_claims", row.get("prior_n_claims", "0"))
        row["prior_n_tables"] = row.get("n_tables", row.get("prior_n_tables", "0"))
        row["status"] = requeue_status
        row["queued_at"] = now_iso
        row["processed_at"] = ""
        row["error"] = ""
        row["retry_error"] = ""
        row["retry_status"] = ""
        reason = str(row.get("reason", "") or "").strip()
        row["reason"] = f"{reason}|{reason_tag}" if reason else reason_tag


def run_stage(
    queue_path: Path,
    selected_ids: set[str],
    requeue_status: str,
    timeout_seconds: int,
    max_workers: int,
    max_pages: int,
    stage_name: str,
) -> None:
    if not selected_ids:
        return

    rows = read_rows(queue_path)
    apply_requeue_status(rows, selected_ids, requeue_status, reason_tag=f"timeout_recovery_{stage_name}")
    write_rows(queue_path, rows)

    batch_size = len(selected_ids)
    run(
        [
            "python3",
            "scripts/preprocess_pdf_queue.py",
            "--queue-csv",
            str(queue_path),
            "--queued-only",
            "--force",
            "--batch-size",
            str(batch_size),
            "--max-workers",
            str(max(1, int(max_workers))),
            "--max-pages",
            str(max(1, int(max_pages))),
        ]
    )
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
    run(
        [
            "python3",
            "scripts/preprocess_pdf_queue.py",
            "--queue-csv",
            str(queue_path),
            "--queued-only",
            "--force",
            "--batch-size",
            str(batch_size),
            "--max-workers",
            str(max(1, int(max_workers))),
            "--max-pages",
            str(max(1, int(max_pages))),
        ]
    )
    run(
        [
            "python3",
            "scripts/reprocess_article_type_tranche_safe.py",
            "--queue-csv",
            str(queue_path),
            "--status-prefix",
            requeue_status,
            "--max-rows",
            str(batch_size),
            "--timeout-seconds",
            str(max(30, int(timeout_seconds))),
            "--prioritize-preprocessed",
            "--skip-preprocess-quarantine",
            "--confirmed-csv",
            f"data/review/timeout_recovery_{stage_name}_confirmed_rows.csv",
            "--no-claims-csv",
            f"data/review/timeout_recovery_{stage_name}_no_claims_review.csv",
            "--audit-jsonl",
            f"data/review/timeout_recovery_{stage_name}_extraction_audit.jsonl",
            "--manual-review-csv",
            f"data/review/timeout_recovery_{stage_name}_table_quality_manual_queue.csv",
            "--article-type-review-csv",
            f"data/review/timeout_recovery_{stage_name}_article_type_manual_queue.csv",
        ]
    )


def write_remaining_timeout_queue(
    out_path: Path,
    post_rows: List[Dict[str, str]],
    selected_ids: set[str],
) -> int:
    remaining = []
    for row in post_rows:
        pid = row.get("paper_id", "")
        if pid not in selected_ids:
            continue
        if str(row.get("status", "")).strip() != "error_pdf_timeout":
            continue
        cloned = dict(row)
        cloned["status"] = "queued_timeout_recovery_backlog"
        reason = str(cloned.get("reason", "") or "").strip()
        tag = "timeout_backlog_queue"
        cloned["reason"] = f"{reason}|{tag}" if reason else tag
        remaining.append(cloned)

    write_rows(out_path, remaining if remaining else [])
    return len(remaining)


def main() -> int:
    args = parse_args()
    queue_path = Path(args.queue_csv)
    rows = read_rows(queue_path)

    def matches(row: Dict[str, str]) -> bool:
        target = str(args.status).strip()
        if args.status_field == "status":
            return str(row.get("status", "")).strip() == target
        if args.status_field == "retry_status":
            return str(row.get("retry_status", "")).strip() == target
        # auto: status first, then retry_status fallback.
        return (
            str(row.get("status", "")).strip() == target
            or str(row.get("retry_status", "")).strip() == target
        )

    selected = [r for r in rows if matches(r)]
    if args.limit and args.limit > 0:
        selected = selected[: args.limit]
    selected_ids = {r.get("paper_id", "") for r in selected}

    fast_timeout = int(args.fast_timeout_seconds)
    slow_timeout = int(args.slow_timeout_seconds)
    if int(args.timeout_seconds) > 0:
        fast_timeout = int(args.timeout_seconds)
        slow_timeout = int(args.timeout_seconds)

    print(f"selected_rows={len(selected)}")
    if not selected:
        return 0

    baseline = {
        r["paper_id"]: {
            "status": r.get("status", ""),
            "n_claims": to_int(r.get("n_claims")),
            "n_tables": to_int(r.get("n_tables")),
            "preprocess_status": r.get("preprocess_status", ""),
            "pdf_path": r.get("pdf_path", ""),
        }
        for r in selected
    }

    if args.dry_run:
        dry_report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "dry_run": True,
            "selected_rows": len(selected),
            "source_status": args.status,
            "status_field": args.status_field,
            "fast_timeout_seconds": fast_timeout,
            "slow_timeout_seconds": slow_timeout,
            "skip_slow_stage": bool(args.skip_slow_stage),
        }
        print(json.dumps(dry_report, indent=2))
        return 0

    # Stage 1: fast retry lane.
    fast_status = f"{args.requeue_status}_fast"
    run_stage(
        queue_path=queue_path,
        selected_ids=selected_ids,
        requeue_status=fast_status,
        timeout_seconds=fast_timeout,
        max_workers=int(args.max_workers),
        max_pages=int(args.max_pages),
        stage_name="fast",
    )

    after_fast_rows = read_rows(queue_path)
    after_fast_by_id = {r.get("paper_id", ""): r for r in after_fast_rows}
    slow_ids = {
        pid
        for pid in selected_ids
        if str(after_fast_by_id.get(pid, {}).get("status", "")).strip() == "error_pdf_timeout"
    }

    # Stage 2: slow retry lane for unresolved timeouts.
    if slow_ids and not args.skip_slow_stage:
        slow_status = f"{args.requeue_status}_slow"
        run_stage(
            queue_path=queue_path,
            selected_ids=slow_ids,
            requeue_status=slow_status,
            timeout_seconds=slow_timeout,
            max_workers=int(args.slow_max_workers),
            max_pages=int(args.max_pages),
            stage_name="slow",
        )

    post_rows = read_rows(queue_path)
    post_by_id = {r.get("paper_id", ""): r for r in post_rows}

    details: List[Dict[str, str]] = []
    gains = {
        "selected_rows": len(selected),
        "fast_stage_timeout_seconds": fast_timeout,
        "slow_stage_timeout_seconds": slow_timeout if not args.skip_slow_stage else 0,
        "slow_stage_candidates": len(slow_ids),
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
        p_claims = to_int(p.get("n_claims"))
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
                "retry_status": str(p.get("retry_status", "")),
                "retry_error": str(p.get("retry_error", "")),
                "title": str(p.get("title", "")),
            }
        )

    details.sort(key=lambda r: int(r.get("claim_delta", "0")), reverse=True)

    remaining_timeout_count = write_remaining_timeout_queue(
        out_path=Path(args.remaining_timeout_csv),
        post_rows=post_rows,
        selected_ids=selected_ids,
    )
    gains["remaining_timeout_queue_rows"] = remaining_timeout_count

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_status": args.status,
        "status_field": args.status_field,
        "requeue_status_base": args.requeue_status,
        "fast_requeue_status": fast_status,
        "fast_timeout_seconds": fast_timeout,
        "slow_timeout_seconds": slow_timeout if not args.skip_slow_stage else 0,
        "slow_stage_enabled": not bool(args.skip_slow_stage),
        "gains": gains,
        "post_status_counts": dict(ids_by_status(post_rows, selected_ids)),
        "remaining_timeout_csv": args.remaining_timeout_csv,
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
