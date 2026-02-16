#!/usr/bin/env python3
"""
Repair problematic PDFs and update queue to use repaired copies.

Targets rows marked with preprocess_status in {error, quarantine} by default.
Repair strategy:
1) qpdf rewrite
2) ghostscript rewrite fallback
3) validate text extractability with pdfplumber
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_AF_ROOT = Path("/Users/davidusa/REPOS/Article_Finder_v3_2_3")


def _maybe_unwrap_quotes(raw: str) -> str:
    s = (raw or "").strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in {"'", '"'}:
        return s[1:-1].strip()
    return s


def safe_slug(text: str) -> str:
    out = "".join(ch if ch.isalnum() or ch in {"-", "_", "."} else "_" for ch in (text or "").strip())
    out = "_".join(p for p in out.split("_") if p)
    return out[:120] or "unknown"


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


def validate_pdf_text(pdf_path: Path, max_pages: int = 10, min_total_chars: int = 100) -> Tuple[bool, int]:
    try:
        import pdfplumber
    except Exception:
        return False, 0
    total = 0
    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            for idx, page in enumerate(pdf.pages, start=1):
                if idx > max_pages:
                    break
                txt = (page.extract_text() or "").strip()
                total += len(txt)
        return total >= min_total_chars, total
    except Exception:
        return False, total


@dataclass
class RepairResult:
    paper_id: str
    status: str
    src_path: str
    repaired_path: str = ""
    method: str = ""
    extracted_chars: int = 0
    error: str = ""


def run_cmd(cmd: List[str]) -> Tuple[bool, str]:
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if p.returncode == 0:
            return True, ""
        return False, (p.stderr or p.stdout or "").strip()[:400]
    except Exception as exc:
        return False, str(exc)


def repair_one(src: Path, out_path: Path) -> Tuple[bool, str, str]:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    qpdf_cmd = [
        "qpdf",
        "--linearize",
        "--object-streams=disable",
        str(src),
        str(out_path),
    ]
    ok, err = run_cmd(qpdf_cmd)
    if ok:
        return True, "qpdf", ""

    gs_out = out_path.with_name(out_path.stem + "_gs.pdf")
    gs_cmd = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dNOPAUSE",
        "-dBATCH",
        "-dSAFER",
        f"-sOutputFile={gs_out}",
        str(src),
    ]
    ok2, err2 = run_cmd(gs_cmd)
    if ok2 and gs_out.exists():
        gs_out.replace(out_path)
        return True, "ghostscript", ""

    return False, "", f"qpdf={err}; gs={err2}"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Repair problematic PDFs and update queue.")
    p.add_argument("--queue-csv", default="data/production/realtime_pdf_completion_queue.csv")
    p.add_argument("--output-dir", default="data/production/pdf_repaired")
    p.add_argument("--audit-jsonl", default="data/production/pdf_repair_audit.jsonl")
    p.add_argument("--statuses", default="error,quarantine", help="Comma-separated preprocess statuses to target")
    p.add_argument("--limit", type=int, default=0, help="0 means no limit")
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def write_queue(path: Path, rows: List[Dict[str, Any]]) -> None:
    fields = set()
    for r in rows:
        fields.update(r.keys())
    ordered = [
        "paper_id",
        "doi",
        "title",
        "year",
        "venue",
        "pdf_path",
        "status",
        "article_type_family",
        "preprocess_status",
        "preprocess_checked_at",
        "preprocess_cache_path",
        "preprocess_warning_flags",
        "preprocess_page_count",
        "preprocess_nonempty_pages",
        "preprocess_text_chars",
        "preprocess_cid_hits",
        "preprocess_cid_density",
        "preprocess_error",
        "resolved_pdf_path",
        "reason",
        "queued_at",
        "processed_at",
        "n_tables",
        "n_claims",
        "error",
        "source",
    ]
    for f in sorted(fields):
        if f not in ordered:
            ordered.append(f)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=ordered)
        w.writeheader()
        w.writerows(rows)


def append_audit(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=True) + "\n")


def main() -> int:
    args = parse_args()
    queue_csv = Path(args.queue_csv)
    out_dir = Path(args.output_dir)
    audit_path = Path(args.audit_jsonl)
    target_statuses = {s.strip().lower() for s in args.statuses.split(",") if s.strip()}

    with queue_csv.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))

    targets: List[Tuple[int, Dict[str, Any], Path]] = []
    for idx, row in enumerate(rows):
        pstatus = str(row.get("preprocess_status", "")).strip().lower()
        if pstatus not in target_statuses:
            continue
        src = resolve_pdf_path(row.get("pdf_path", ""), queue_csv)
        if not src.exists():
            continue
        targets.append((idx, row, src))

    if args.limit and args.limit > 0:
        targets = targets[: args.limit]

    print(f"repair_targets={len(targets)}")
    if args.dry_run:
        return 0

    audits: List[Dict[str, Any]] = []
    now = datetime.now(timezone.utc).isoformat()
    repaired = 0
    failed = 0

    for idx, row, src in targets:
        paper_id = str(row.get("paper_id", "")).strip()
        stem = safe_slug(paper_id or src.stem)
        out_path = out_dir / f"{stem}.pdf"
        ok, method, err = repair_one(src, out_path)
        if ok:
            valid, chars = validate_pdf_text(out_path)
            if valid:
                row["pdf_path"] = str(out_path)
                row["resolved_pdf_path"] = str(out_path)
                row["preprocess_status"] = "ready"
                row["preprocess_error"] = ""
                flags = (row.get("preprocess_warning_flags", "") or "").strip()
                row["preprocess_warning_flags"] = "|".join([x for x in [flags, f"repaired:{method}"] if x]).strip("|")
                row["reason"] = "repaired_problem_pdf"
                repaired += 1
                audits.append(
                    {
                        "generated_at": now,
                        "paper_id": paper_id,
                        "status": "repaired",
                        "method": method,
                        "src_path": str(src),
                        "repaired_path": str(out_path),
                        "extracted_chars": chars,
                    }
                )
                continue
            err = f"repaired_but_unreadable(chars={chars})"

        failed += 1
        audits.append(
            {
                "generated_at": now,
                "paper_id": paper_id,
                "status": "repair_failed",
                "method": method or "",
                "src_path": str(src),
                "repaired_path": str(out_path),
                "error": err,
            }
        )

    write_queue(queue_csv, rows)
    append_audit(audit_path, audits)
    print(f"repaired={repaired}")
    print(f"repair_failed={failed}")
    print(f"queue_updated={queue_csv}")
    print(f"audit_appended={audit_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

