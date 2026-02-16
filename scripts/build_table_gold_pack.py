#!/usr/bin/env python3
"""
Build a Codex-authored table gold pack from PDF tables.

This script processes a queue of papers with local PDFs, extracts tables with
the deterministic pdfplumber path, and emits:
1. manifest CSV (processed/missing/error status)
2. raw tables JSONL
3. codex_gold_rows CSV for model benchmarking
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.services.table_extractor import ExtractionMethod  # noqa: E402
from src.services.table_to_claims import PipelineTableIntegrator  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Codex table gold pack from PDF tables.")
    parser.add_argument(
        "--queue-csv",
        default="data/table_queue/table_extraction_queue.csv",
        help="Queue CSV produced by build_table_extraction_queue.py",
    )
    parser.add_argument(
        "--max-papers",
        type=int,
        default=98,
        help="Max papers to process",
    )
    parser.add_argument(
        "--output-dir",
        default="data/table_gold/codex_gold_v1",
        help="Output directory",
    )
    return parser.parse_args()


def safe_float(v: Any) -> str:
    if v is None or v == "":
        return ""
    try:
        return f"{float(v):.6g}"
    except Exception:
        return ""


def write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _maybe_unwrap_quotes(raw: str) -> str:
    s = (raw or "").strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in {"'", '"'}:
        return s[1:-1].strip()
    return s


def resolve_pdf_path(raw_path: str, queue_csv_path: Path) -> Path:
    """
    Resolve PDF path from queue rows.

    Supports:
    - Absolute paths
    - Project-relative paths
    - Queue-relative paths
    - Article Finder repo-relative paths (e.g., data/pdfs/...)
    """
    af_root = Path("/Users/davidusa/REPOS/Article_Finder_v3_2_3")
    queue_dir = queue_csv_path.resolve().parent

    candidates: List[Path] = []
    variants = []
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
            candidates.append((af_root / p).resolve())

    for candidate in candidates:
        if candidate.exists():
            return candidate

    if candidates:
        return candidates[0]
    return Path(raw_path or "")


def main() -> int:
    args = parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    queue_csv_path = Path(args.queue_csv)
    queue_rows = list(csv.DictReader(queue_csv_path.open(encoding="utf-8")))
    queue_rows = queue_rows[: args.max_papers]

    integrator = PipelineTableIntegrator(
        api_client=None,
        extraction_method=ExtractionMethod.PDFPLUMBER,
        model="claude-3-haiku-20240307",
    )

    manifest_rows: List[Dict[str, Any]] = []
    gold_rows: List[Dict[str, Any]] = []
    raw_tables_path = out_dir / "raw_tables.jsonl"

    processed = 0
    missing = 0
    failed = 0

    with raw_tables_path.open("w", encoding="utf-8") as raw_f:
        for row in queue_rows:
            paper_id = row.get("paper_id", "")
            raw_pdf_path = row.get("pdf_path", "")
            pdf_path = resolve_pdf_path(raw_pdf_path, queue_csv_path)
            title = row.get("title", "")
            topic_bucket = row.get("topic_bucket", "")
            if not pdf_path.exists():
                missing += 1
                manifest_rows.append(
                    {
                        "paper_id": paper_id,
                        "title": title,
                        "pdf_path": str(raw_pdf_path),
                        "resolved_pdf_path": str(pdf_path),
                        "status": "missing_pdf",
                        "n_tables": 0,
                        "n_claims": 0,
                        "error": "pdf_not_found",
                    }
                )
                continue

            try:
                result = integrator.extract_and_convert(pdf_path=pdf_path, paper_id=paper_id)
                processed += 1

                for table in result.tables:
                    payload = table.to_dict()
                    payload["paper_id"] = paper_id
                    payload["title"] = title
                    payload["topic_bucket"] = topic_bucket
                    raw_f.write(json.dumps(payload) + "\n")

                for claim in result.claims:
                    meta = claim.metadata or {}
                    gold_rows.append(
                        {
                            "paper_id": paper_id,
                            "title": title,
                            "topic_bucket": topic_bucket,
                            "table_id": claim.source_table_id,
                            "row_index": claim.source_row,
                            "claim_id": claim.claim_id,
                            "claim_type": claim.claim_type,
                            "content": claim.content,
                            "confidence": safe_float(claim.confidence),
                            "citation": meta.get("citation", ""),
                            "intervention": meta.get("intervention", ""),
                            "control": meta.get("control", ""),
                            "outcome": meta.get("outcome", ""),
                            "sample_size": meta.get("sample_size", ""),
                            "effect_size": safe_float(meta.get("effect_size")),
                            "effect_size_type": meta.get("effect_size_type", ""),
                            "ci_lower": safe_float(meta.get("ci_lower")),
                            "ci_upper": safe_float(meta.get("ci_upper")),
                            "p_value": safe_float(meta.get("p_value")),
                            "source": "codex_pdfplumber",
                            "evidence_level": "pdf_table_extracted",
                            "provenance_tier": "pdf_confirmed",
                            "requires_pdf_confirmation": "no",
                        }
                    )

                manifest_rows.append(
                    {
                        "paper_id": paper_id,
                        "title": title,
                        "pdf_path": str(raw_pdf_path),
                        "resolved_pdf_path": str(pdf_path),
                        "status": "processed",
                        "n_tables": len(result.tables),
                        "n_claims": len(result.claims),
                        "error": "; ".join(result.errors) if result.errors else "",
                    }
                )
            except Exception as exc:
                failed += 1
                manifest_rows.append(
                    {
                        "paper_id": paper_id,
                        "title": title,
                        "pdf_path": str(raw_pdf_path),
                        "resolved_pdf_path": str(pdf_path),
                        "status": "error",
                        "n_tables": 0,
                        "n_claims": 0,
                        "error": str(exc),
                    }
                )

    write_csv(
        out_dir / "manifest.csv",
        manifest_rows,
        fieldnames=[
            "paper_id",
            "title",
            "pdf_path",
            "resolved_pdf_path",
            "status",
            "n_tables",
            "n_claims",
            "error",
        ],
    )
    write_csv(
        out_dir / "codex_gold_rows.csv",
        gold_rows,
        fieldnames=[
            "paper_id",
            "title",
            "topic_bucket",
            "table_id",
            "row_index",
            "claim_id",
            "claim_type",
            "content",
            "confidence",
            "citation",
            "intervention",
            "control",
            "outcome",
            "sample_size",
            "effect_size",
            "effect_size_type",
            "ci_lower",
            "ci_upper",
            "p_value",
            "source",
            "evidence_level",
            "provenance_tier",
            "requires_pdf_confirmation",
        ],
    )

    summary_path = out_dir / "summary.md"
    summary_path.write_text(
        "\n".join(
            [
                "# Codex Gold Pack Summary",
                "",
                f"- Queue input rows: {len(queue_rows)}",
                f"- Processed PDFs: {processed}",
                f"- Missing PDFs: {missing}",
                f"- Failed extractions: {failed}",
                f"- Gold rows written: {len(gold_rows)}",
                f"- Manifest: {out_dir / 'manifest.csv'}",
                f"- Raw tables: {out_dir / 'raw_tables.jsonl'}",
                f"- Gold rows: {out_dir / 'codex_gold_rows.csv'}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Wrote manifest: {out_dir / 'manifest.csv'}")
    print(f"Wrote raw tables: {out_dir / 'raw_tables.jsonl'}")
    print(f"Wrote gold rows: {out_dir / 'codex_gold_rows.csv'}")
    print(f"Wrote summary: {out_dir / 'summary.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
