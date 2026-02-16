#!/usr/bin/env python3
"""
Parallel PDF preprocess stage for realtime extraction queue.

Goals:
1. Front-load PDF parse diagnostics.
2. Cache page-level extracted text for discourse/QA.
3. Mark problematic PDFs so schedulers can prioritize likely-good files first.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_AF_ROOT = Path("/Users/davidusa/REPOS/Article_Finder_v3_2_3")

CID_PATTERN = re.compile(r"\(cid:\d+\)")


def _maybe_unwrap_quotes(raw: str) -> str:
    s = (raw or "").strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in {"'", '"'}:
        return s[1:-1].strip()
    return s


def resolve_pdf_path(raw_path: str, queue_csv_path: Path) -> Path:
    queue_dir = queue_csv_path.resolve().parent
    candidates: List[Path] = []
    variants: List[str] = []
    raw = (raw_path or "").strip()
    if raw:
        variants.append(raw)
        unwrapped = _maybe_unwrap_quotes(raw)
        if unwrapped and unwrapped != raw:
            variants.append(unwrapped)

    for variant in variants:
        p = Path(variant)
        if p.is_absolute():
            candidates.append(p)
        else:
            candidates.append((queue_dir / p).resolve())
            candidates.append((PROJECT_ROOT / p).resolve())
            candidates.append((DEFAULT_AF_ROOT / p).resolve())

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0] if candidates else Path(raw_path or "")


@dataclass
class PreprocessResult:
    row_index: int
    preprocess_status: str
    resolved_pdf_path: str = ""
    page_count: int = 0
    nonempty_pages: int = 0
    text_chars: int = 0
    cid_hits: int = 0
    cid_density: float = 0.0
    cache_path: str = ""
    warning_flags: str = ""
    error: str = ""


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Parallel PDF preprocess for realtime queue.")
    p.add_argument("--queue-csv", default="data/production/realtime_pdf_completion_queue.csv")
    p.add_argument("--cache-dir", default="data/production/pdf_preprocess_cache")
    p.add_argument("--audit-jsonl", default="data/production/realtime_pdf_preprocess_audit.jsonl")
    p.add_argument("--batch-size", type=int, default=200)
    p.add_argument("--max-workers", type=int, default=8)
    p.add_argument(
        "--max-pages",
        type=int,
        default=25,
        help="Max pages to scan per PDF during preprocess (fast diagnostics mode)",
    )
    p.add_argument("--queued-only", action="store_true", help="Process only rows with status queued_*")
    p.add_argument("--force", action="store_true", help="Reprocess even if preprocess_status already exists")
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def classify_quality(
    page_count: int,
    nonempty_pages: int,
    text_chars: int,
    cid_hits: int,
) -> Tuple[str, List[str]]:
    flags: List[str] = []
    if page_count <= 0:
        return "quarantine", ["no_pages"]

    nonempty_ratio = nonempty_pages / float(page_count)
    avg_chars = text_chars / float(max(page_count, 1))
    cid_density = cid_hits / float(max(text_chars, 1))

    if nonempty_ratio < 0.30:
        flags.append("low_nonempty_page_ratio")
    if avg_chars < 80:
        flags.append("low_text_density")
    if cid_density > 0.02:
        flags.append("high_cid_density")

    if flags:
        return "quarantine", flags
    return "ready", []


def preprocess_single(
    row_index: int,
    row: Dict[str, Any],
    queue_csv_path: Path,
    cache_dir: Path,
    max_pages: int,
) -> PreprocessResult:
    paper_id = str(row.get("paper_id", "")).strip()
    pdf_path = resolve_pdf_path(row.get("pdf_path", ""), queue_csv_path)
    if not pdf_path.exists():
        return PreprocessResult(
            row_index=row_index,
            preprocess_status="missing_pdf",
            resolved_pdf_path=str(pdf_path),
            error="pdf_not_found",
        )

    try:
        import pdfplumber
    except Exception as exc:
        return PreprocessResult(
            row_index=row_index,
            preprocess_status="error",
            resolved_pdf_path=str(pdf_path),
            error=f"pdfplumber_unavailable:{exc}",
        )

    page_rows: List[Dict[str, Any]] = []
    page_count = 0
    nonempty_pages = 0
    text_chars = 0
    cid_hits = 0

    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page_idx, page in enumerate(pdf.pages, start=1):
                if max_pages > 0 and page_idx > max_pages:
                    break
                page_count += 1
                text = page.extract_text() or ""
                text_norm = text.strip()
                if text_norm:
                    nonempty_pages += 1
                text_chars += len(text_norm)
                cid_hits += len(CID_PATTERN.findall(text))
                page_rows.append(
                    {
                        "page": page_idx,
                        "text": text,
                    }
                )
    except Exception as exc:
        return PreprocessResult(
            row_index=row_index,
            preprocess_status="error",
            resolved_pdf_path=str(pdf_path),
            error=f"pdf_parse_error:{exc}",
        )

    status, flags = classify_quality(
        page_count=page_count,
        nonempty_pages=nonempty_pages,
        text_chars=text_chars,
        cid_hits=cid_hits,
    )
    cid_density = cid_hits / float(max(text_chars, 1))

    cache_rel = ""
    if paper_id:
        cache_rel = f"{paper_id}.json"
    else:
        cache_rel = f"row_{row_index}.json"
    cache_path = cache_dir / cache_rel
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_payload = {
        "paper_id": paper_id,
        "pdf_path": str(pdf_path),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "page_count": page_count,
        "nonempty_pages": nonempty_pages,
        "text_chars": text_chars,
        "cid_hits": cid_hits,
        "cid_density": round(cid_density, 8),
        "preprocess_status": status,
        "warning_flags": flags,
        "pages": page_rows,
    }
    cache_path.write_text(json.dumps(cache_payload, ensure_ascii=True), encoding="utf-8")

    return PreprocessResult(
        row_index=row_index,
        preprocess_status=status,
        resolved_pdf_path=str(pdf_path),
        page_count=page_count,
        nonempty_pages=nonempty_pages,
        text_chars=text_chars,
        cid_hits=cid_hits,
        cid_density=cid_density,
        cache_path=str(cache_path),
        warning_flags="|".join(flags),
        error="",
    )


def write_queue(path: Path, rows: List[Dict[str, Any]]) -> None:
    fieldnames = set()
    for row in rows:
        fieldnames.update(row.keys())
    ordered = [
        "paper_id",
        "doi",
        "title",
        "year",
        "venue",
        "pdf_path",
        "status",
        "preprocess_status",
        "preprocess_checked_at",
        "preprocess_cache_path",
        "preprocess_warning_flags",
        "preprocess_page_count",
        "preprocess_nonempty_pages",
        "preprocess_text_chars",
        "preprocess_cid_hits",
        "preprocess_cid_density",
        "queued_at",
        "processed_at",
        "reason",
        "source",
        "resolved_pdf_path",
        "n_tables",
        "n_claims",
        "error",
    ]
    for k in sorted(fieldnames):
        if k not in ordered:
            ordered.append(k)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=ordered)
        writer.writeheader()
        writer.writerows(rows)


def append_audits(path: Path, audits: List[Dict[str, Any]]) -> None:
    if not audits:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for a in audits:
            f.write(json.dumps(a, ensure_ascii=True) + "\n")


def main() -> int:
    args = parse_args()
    queue_csv_path = Path(args.queue_csv)
    cache_dir = Path(args.cache_dir)
    audit_jsonl_path = Path(args.audit_jsonl)

    if not queue_csv_path.exists():
        print(f"Queue file not found: {queue_csv_path}")
        return 1

    with queue_csv_path.open(encoding="utf-8", newline="") as f:
        queue_rows = list(csv.DictReader(f))

    target_indices: List[int] = []
    for idx, row in enumerate(queue_rows):
        status = str(row.get("status", "")).strip()
        if args.queued_only and not status.startswith("queued_"):
            continue
        if not str(row.get("pdf_path", "")).strip():
            continue
        if not args.force and str(row.get("preprocess_status", "")).strip() in {"ready", "quarantine", "missing_pdf"}:
            continue
        target_indices.append(idx)

    if args.batch_size > 0:
        target_indices = target_indices[: args.batch_size]

    print(f"preprocess_target_rows={len(target_indices)}")
    if args.dry_run:
        return 0

    if not target_indices:
        print("No rows selected for preprocess.")
        return 0

    results: List[PreprocessResult] = []
    with ThreadPoolExecutor(max_workers=max(1, int(args.max_workers))) as ex:
        futures = {
            ex.submit(
                preprocess_single,
                idx,
                queue_rows[idx],
                queue_csv_path,
                cache_dir,
                int(args.max_pages),
            ): idx
            for idx in target_indices
        }
        for fut in as_completed(futures):
            results.append(fut.result())

    results.sort(key=lambda r: r.row_index)
    now_iso = datetime.now(timezone.utc).isoformat()
    audits: List[Dict[str, Any]] = []
    for res in results:
        row = queue_rows[res.row_index]
        row["resolved_pdf_path"] = res.resolved_pdf_path or row.get("resolved_pdf_path", "")
        row["preprocess_status"] = res.preprocess_status
        row["preprocess_checked_at"] = now_iso
        row["preprocess_cache_path"] = res.cache_path
        row["preprocess_warning_flags"] = res.warning_flags
        row["preprocess_page_count"] = str(res.page_count)
        row["preprocess_nonempty_pages"] = str(res.nonempty_pages)
        row["preprocess_text_chars"] = str(res.text_chars)
        row["preprocess_cid_hits"] = str(res.cid_hits)
        row["preprocess_cid_density"] = f"{res.cid_density:.8f}"
        if res.error:
            row["preprocess_error"] = res.error
        else:
            row["preprocess_error"] = ""

        audits.append(
            {
                "generated_at": now_iso,
                "paper_id": row.get("paper_id", ""),
                "pdf_path": row.get("pdf_path", ""),
                "resolved_pdf_path": res.resolved_pdf_path,
                "preprocess_status": res.preprocess_status,
                "page_count": res.page_count,
                "nonempty_pages": res.nonempty_pages,
                "text_chars": res.text_chars,
                "cid_hits": res.cid_hits,
                "cid_density": round(res.cid_density, 8),
                "warning_flags": res.warning_flags.split("|") if res.warning_flags else [],
                "cache_path": res.cache_path,
                "error": res.error,
            }
        )

    write_queue(queue_csv_path, queue_rows)
    append_audits(audit_jsonl_path, audits)

    status_counts: Dict[str, int] = {}
    for r in results:
        status_counts[r.preprocess_status] = status_counts.get(r.preprocess_status, 0) + 1

    print(f"preprocess_done_rows={len(results)}")
    for k in sorted(status_counts):
        print(f"  {k}={status_counts[k]}")
    print(f"queue_updated={queue_csv_path}")
    print(f"audit_appended={audit_jsonl_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
