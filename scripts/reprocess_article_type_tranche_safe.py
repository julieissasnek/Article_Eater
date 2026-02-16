#!/usr/bin/env python3
"""
Safely reprocess queued article-type tranche rows with per-paper timeout.
"""

from __future__ import annotations

import argparse
import csv
import multiprocessing as mp
import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

_rtq_path = PROJECT_ROOT / "scripts" / "process_realtime_pdf_completion_queue.py"
_spec = importlib.util.spec_from_file_location("process_realtime_pdf_completion_queue", str(_rtq_path))
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Unable to load module from {_rtq_path}")
rtq = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = rtq
_spec.loader.exec_module(rtq)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Safe tranche reprocessor with timeout.")
    parser.add_argument(
        "--queue-csv",
        default="data/production/realtime_pdf_completion_queue.csv",
        help="Queue CSV path",
    )
    parser.add_argument(
        "--status-prefix",
        default="queued_article_type_reprocess",
        help="Only process rows whose status starts with this prefix",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=80,
        help="Maximum queued rows to process",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=120,
        help="Per-paper timeout in seconds",
    )
    parser.add_argument(
        "--prioritize-preprocessed",
        action="store_true",
        help="Process preprocess_status=ready first",
    )
    parser.add_argument(
        "--skip-preprocess-quarantine",
        action="store_true",
        help="Skip rows with preprocess_status in {quarantine,error}",
    )
    parser.add_argument(
        "--confirmed-csv",
        default="data/review/tranche80_confirmed_rows.csv",
        help="Output CSV for confirmed rows",
    )
    parser.add_argument(
        "--no-claims-csv",
        default="data/review/tranche80_no_claims_review.csv",
        help="Output CSV for no-claims review",
    )
    parser.add_argument(
        "--audit-jsonl",
        default="data/review/tranche80_extraction_audit.jsonl",
        help="Output JSONL for extraction audits",
    )
    parser.add_argument(
        "--manual-review-csv",
        default="data/review/tranche80_table_quality_manual_queue.csv",
        help="Output CSV for manual table quality review",
    )
    parser.add_argument(
        "--article-type-review-csv",
        default="data/review/tranche80_article_type_manual_queue.csv",
        help="Output CSV for article-type review",
    )
    parser.add_argument(
        "--quality-thresholds",
        default="config/table_extraction_quality_thresholds.json",
        help="Quality threshold config path",
    )
    return parser.parse_args()


def _worker(
    result_queue: mp.Queue,
    row_index: int,
    row: Dict[str, Any],
    queue_csv_path: str,
    article_type_family: str,
    article_type_needs_review: bool,
) -> None:
    try:
        res = rtq.process_single_row(
            row_index=row_index,
            row=row,
            queue_csv_path=Path(queue_csv_path),
            article_type_family=article_type_family,
            article_type_needs_review=article_type_needs_review,
        )
        result_queue.put(
            {
                "ok": True,
                "row_index": res.row_index,
                "status": res.status,
                "n_tables": res.n_tables,
                "n_claims": res.n_claims,
                "resolved_pdf_path": res.resolved_pdf_path,
                "error": res.error,
                "confirmed_rows": res.confirmed_rows,
                "extraction_audit": res.extraction_audit,
            }
        )
    except Exception as exc:
        result_queue.put(
            {
                "ok": False,
                "row_index": row_index,
                "status": "error_pdf_processing",
                "n_tables": 0,
                "n_claims": 0,
                "resolved_pdf_path": str(row.get("pdf_path", "")),
                "error": str(exc),
                "confirmed_rows": [],
                "extraction_audit": {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "paper_id": row.get("paper_id", ""),
                    "pdf_path": row.get("pdf_path", ""),
                    "status": "error_pdf_processing",
                    "warnings": ["worker_exception"],
                    "error": str(exc),
                },
            }
        )


def main() -> int:
    args = parse_args()
    queue_csv_path = Path(args.queue_csv)
    if not queue_csv_path.exists():
        print(f"Queue not found: {queue_csv_path}")
        return 1

    with queue_csv_path.open(encoding="utf-8", newline="") as f:
        queue_rows = list(csv.DictReader(f))

    queued_indices = [
        idx
        for idx, row in enumerate(queue_rows)
        if str(row.get("status", "")).startswith(args.status_prefix)
    ]
    if args.skip_preprocess_quarantine:
        queued_indices = [
            idx
            for idx in queued_indices
            if str(row_value(queue_rows[idx], "preprocess_status")).lower() not in {"quarantine", "error"}
        ]
    if args.prioritize_preprocessed:
        queued_indices.sort(key=lambda idx: preprocess_priority(queue_rows[idx]))
    selected_indices = queued_indices[: max(1, int(args.max_rows))]
    if not selected_indices:
        print("No queued tranche rows found.")
        return 0

    print(f"Queued tranche rows found: {len(queued_indices)}")
    print(f"Processing now: {len(selected_indices)}")

    confirmed_rows: List[Dict[str, Any]] = []
    extraction_audits: List[Dict[str, Any]] = []
    timeout_count = 0
    error_count = 0
    completed_count = 0

    family_by_paper = rtq.load_family_context_for_papers(queue_rows, selected_indices)

    for pos, idx in enumerate(selected_indices, start=1):
        row = queue_rows[idx]
        paper_id = str(row.get("paper_id", "")).strip()
        fam_meta = family_by_paper.get(paper_id, {})
        article_type_family = str(fam_meta.get("family", row.get("article_type_family", "unknown")))
        article_type_needs_review = bool(fam_meta.get("needs_review", False))
        result_queue: mp.Queue = mp.Queue()
        proc = mp.Process(
            target=_worker,
            args=(result_queue, idx, row, str(queue_csv_path), article_type_family, article_type_needs_review),
        )
        proc.start()
        proc.join(timeout=max(1, int(args.timeout_seconds)))

        if proc.is_alive():
            proc.terminate()
            proc.join(timeout=5)
            timeout_count += 1
            now_iso = datetime.now(timezone.utc).isoformat()
            next_status = "error_pdf_timeout"
            if should_preserve_prior_extracted(row, next_status):
                row["status"] = row_value(row, "prior_status")
                row["n_tables"] = row_value(row, "prior_n_tables")
                row["n_claims"] = row_value(row, "prior_n_claims")
                row["retry_status"] = next_status
                row["retry_error"] = f"timeout_after_{int(args.timeout_seconds)}s"
            else:
                row["status"] = next_status
                row["retry_status"] = next_status
                row["retry_error"] = f"timeout_after_{int(args.timeout_seconds)}s"
            row["processed_at"] = now_iso
            row["error"] = row.get("retry_error", "")
            extraction_audits.append(
                {
                    "generated_at": now_iso,
                    "paper_id": paper_id,
                    "pdf_path": row.get("pdf_path", ""),
                    "status": next_status,
                    "warnings": ["worker_timeout"],
                    "error": row["error"],
                }
            )
            print(f"[{pos}/{len(selected_indices)}] timeout {paper_id}")
            continue

        payload = result_queue.get() if not result_queue.empty() else None
        now_iso = datetime.now(timezone.utc).isoformat()
        if not payload:
            error_count += 1
            row["status"] = "error_pdf_processing"
            row["processed_at"] = now_iso
            row["error"] = "worker_no_payload"
            print(f"[{pos}/{len(selected_indices)}] error {paper_id}: no payload")
            continue

        payload_status = payload.get("status", "error_pdf_processing")
        row["status"] = payload_status
        row["processed_at"] = now_iso
        row["resolved_pdf_path"] = payload.get("resolved_pdf_path", "")
        row["n_tables"] = str(payload.get("n_tables", 0))
        row["n_claims"] = str(payload.get("n_claims", 0))
        row["error"] = payload.get("error", "")
        row["article_type_family"] = article_type_family
        row["article_type_predicted_family"] = fam_meta.get("predicted_family", row.get("article_type_predicted_family", ""))
        row["article_type_confidence"] = fam_meta.get("confidence", row.get("article_type_confidence", ""))
        row["article_type_runner_up"] = fam_meta.get("runner_up", row.get("article_type_runner_up", ""))
        row["article_type_margin"] = fam_meta.get("margin", row.get("article_type_margin", ""))
        row["article_type_needs_review"] = fam_meta.get("needs_review", row.get("article_type_needs_review", ""))
        row["article_type_signals"] = fam_meta.get("signals", row.get("article_type_signals", ""))
        row["article_type_diagnostics"] = fam_meta.get("diagnostics", row.get("article_type_diagnostics", ""))
        row["article_type_classifier_version"] = fam_meta.get(
            "classifier_version",
            row.get("article_type_classifier_version", ""),
        )

        if should_preserve_prior_extracted(row, payload_status):
            row["status"] = row_value(row, "prior_status")
            row["n_tables"] = row_value(row, "prior_n_tables")
            row["n_claims"] = row_value(row, "prior_n_claims")
            row["retry_status"] = payload_status
            row["retry_error"] = payload.get("error", "")

        confirmed_rows.extend(payload.get("confirmed_rows", []))
        audit = payload.get("extraction_audit")
        if isinstance(audit, dict):
            extraction_audits.append(audit)

        if str(row["status"]).startswith("completed_"):
            completed_count += 1
        elif str(row["status"]).startswith("error_"):
            error_count += 1

        print(f"[{pos}/{len(selected_indices)}] {paper_id} -> {row['status']} claims={row.get('n_claims','0')}")

    rtq.append_confirmed_rows(Path(args.confirmed_csv), confirmed_rows)
    rtq.write_queue(queue_csv_path, queue_rows)
    rtq.write_no_claims_review(Path(args.no_claims_csv), queue_rows)
    rtq.append_extraction_audits(Path(args.audit_jsonl), extraction_audits)
    thresholds = rtq.load_quality_thresholds(Path(args.quality_thresholds))
    rtq.write_manual_review_queue(
        Path(args.manual_review_csv),
        queue_rows=queue_rows,
        audits=extraction_audits,
        thresholds=thresholds,
    )
    rtq.write_article_type_review(
        Path(args.article_type_review_csv),
        queue_rows=queue_rows,
        min_confidence=0.60,
        min_margin=0.35,
    )

    print(f"Completed rows: {completed_count}")
    print(f"Timeout rows: {timeout_count}")
    print(f"Error rows: {error_count}")
    print(f"Confirmed rows written: {len(confirmed_rows)} -> {args.confirmed_csv}")
    print(f"Queue updated: {queue_csv_path}")
    return 0


def row_value(row: Dict[str, Any], key: str) -> str:
    return str(row.get(key, "") or "").strip()


def preprocess_priority(row: Dict[str, Any]) -> int:
    status = row_value(row, "preprocess_status").lower()
    if status == "ready":
        return 0
    if not status:
        return 1
    if status in {"quarantine", "error"}:
        return 3
    return 2


def should_preserve_prior_extracted(row: Dict[str, Any], new_status: str) -> bool:
    prior_status = row_value(row, "prior_status")
    if prior_status != "completed_pdf_extracted":
        return False
    return new_status in {"error_pdf_timeout", "error_pdf_processing", "completed_pdf_no_claims"}


if __name__ == "__main__":
    raise SystemExit(main())
