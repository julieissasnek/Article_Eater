#!/usr/bin/env python3
"""Compare claim extraction quality between PDF and Acrobat-exported DOCX.

This is a pilot evaluator for a paired set where each basename has:
- <name>.pdf
- <name>.docx

For each pair:
1) Extract tables from PDF (pdfplumber fallback extractor).
2) Extract tables from DOCX (Word table XML).
3) Normalize into claim_extractor table payloads.
4) Run the same claim extraction method for both sides.
5) Report count + direction + mapping quality deltas.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.extraction.claim_extractor import extract_claims_from_table
from src.extraction.vocabulary import load_vocabulary
from src.services.table_extractor import ExtractionMethod, get_table_extractor

W_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def _norm(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _paper_id_from_stem(stem: str) -> str:
    if stem.startswith("doi_"):
        return f"doi:{stem[4:].replace('_', '/')}"
    return stem


def _infer_table_type(text_blob: str) -> str:
    t = text_blob.lower()
    if ("correlation" in t or "pearson" in t) and re.search(r"\b[rR]\b", t):
        return "RESULTS_CORRELATION"
    if "anova" in t or re.search(r"\bf\(", t):
        return "RESULTS_ANOVA"
    if "regression" in t or "beta" in t or "step" in t or "model" in t:
        return "RESULTS_REGRESSION"
    if "mean" in t and ("sd" in t or "std" in t):
        return "RESULTS_DESCRIPTIVE"
    return "UNKNOWN"


def _row_to_text(cells: list[str]) -> str:
    if len(cells) <= 1:
        return _norm(cells[0] if cells else "")
    return "; ".join(f"col_{i + 1}: {_norm(c)}" for i, c in enumerate(cells))


def _table_rows_payload(rows_2d: list[list[str]]) -> list[dict[str, Any]]:
    rows_payload: list[dict[str, Any]] = []
    for row in rows_2d:
        clean = [_norm(c) for c in row]
        if not any(clean):
            continue
        rec: dict[str, Any] = {
            "text": _row_to_text(clean),
            "source_quote": _row_to_text(clean),
        }
        for idx, cell in enumerate(clean, start=1):
            rec[f"col_{idx}"] = cell
        rows_payload.append(rec)
    return rows_payload


def _extract_docx_tables(docx_path: Path) -> list[list[list[str]]]:
    with zipfile.ZipFile(docx_path) as zf:
        xml = zf.read("word/document.xml")
    root = ET.fromstring(xml)
    out: list[list[list[str]]] = []
    for tbl in root.findall(".//w:tbl", W_NS):
        table_rows: list[list[str]] = []
        for tr in tbl.findall("./w:tr", W_NS):
            cells: list[str] = []
            for tc in tr.findall("./w:tc", W_NS):
                texts = [t.text for t in tc.findall(".//w:t", W_NS) if t.text]
                cell = _norm(" ".join(texts))
                cells.append(cell)
            if cells:
                table_rows.append(cells)
        if table_rows:
            out.append(table_rows)
    return out


def _pdf_tables_to_payloads(
    pdf_path: Path,
    paper_id: str,
    max_pages: int,
    extractor_method: ExtractionMethod,
) -> list[dict[str, Any]]:
    extractor = get_table_extractor(method=extractor_method)
    tables = extractor.extract_tables(pdf_path=pdf_path, pages=list(range(1, max_pages + 1)))
    payloads: list[dict[str, Any]] = []
    for i, t in enumerate(tables, start=1):
        rows2d: list[list[str]] = []
        if t.headers:
            rows2d.append([_norm(h) for h in t.headers])
        rows2d.extend([[_norm(c) for c in row] for row in t.rows])
        rows_payload = _table_rows_payload(rows2d)
        if not rows_payload:
            continue
        blob = " ".join(r.get("text", "") for r in rows_payload[:12])
        payloads.append(
            {
                "paper_id": paper_id,
                "table_id": f"{paper_id}:PDF:T{i}",
                "type": _infer_table_type(blob),
                "page": t.page_number,
                "rows": rows_payload,
                "sample_content": t.to_markdown(),
                "title": t.title,
                "caption": t.caption,
            }
        )
    return payloads


def _docx_tables_to_payloads(docx_path: Path, paper_id: str) -> list[dict[str, Any]]:
    raw_tables = _extract_docx_tables(docx_path)
    payloads: list[dict[str, Any]] = []
    for i, rows2d in enumerate(raw_tables, start=1):
        rows_payload = _table_rows_payload(rows2d)
        if not rows_payload:
            continue
        blob = " ".join(r.get("text", "") for r in rows_payload[:12])
        payloads.append(
            {
                "paper_id": paper_id,
                "table_id": f"{paper_id}:DOCX:T{i}",
                "type": _infer_table_type(blob),
                "page": None,
                "rows": rows_payload,
                "sample_content": "\n".join(r.get("text", "") for r in rows_payload[:30]),
            }
        )
    return payloads


def _extract_claims(table_payloads: list[dict[str, Any]], method: str, vocab: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for tbl in table_payloads:
        out.extend(extract_claims_from_table(tbl, vocabulary=vocab, method=method))
    return out


def _claim_key(claim: dict[str, Any]) -> tuple[str, str, str]:
    iv = _norm(claim.get("iv") or claim.get("iv_raw")).lower()
    dv = _norm(claim.get("dv") or claim.get("dv_raw")).lower()
    direction = _norm(claim.get("direction")).lower()
    return (iv, dv, direction)


def _side_metrics(claims: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(claims)
    if n == 0:
        return {
            "claims": 0,
            "direction_unknown": 0,
            "direction_unknown_rate": 0.0,
            "mapped_both_rate": 0.0,
            "has_stat_signal_rate": 0.0,
            "mean_extraction_confidence": 0.0,
        }
    unknown = sum(1 for c in claims if _norm(c.get("direction")).lower() == "unknown")
    mapped = sum(1 for c in claims if bool(c.get("iv_mapped")) and bool(c.get("dv_mapped")))
    stat = sum(1 for c in claims if c.get("effect_size") is not None or c.get("p_value") is not None)
    confs = [float(c.get("extraction_confidence") or 0.0) for c in claims]
    return {
        "claims": n,
        "direction_unknown": unknown,
        "direction_unknown_rate": round(unknown / n, 4),
        "mapped_both_rate": round(mapped / n, 4),
        "has_stat_signal_rate": round(stat / n, 4),
        "mean_extraction_confidence": round(mean(confs), 4) if confs else 0.0,
        "direction_counts": dict(Counter(_norm(c.get("direction")).lower() for c in claims)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare DOCX-vs-PDF claim extraction on paired files.")
    parser.add_argument("--input-dir", default="/Users/davidusa/Downloads/docx_pilot_input")
    parser.add_argument("--output", default="data/production/llm_pilot/docx_vs_pdf_claim_compare.json")
    parser.add_argument("--method", default="enhanced", choices=["enhanced", "rule_based", "llm"])
    parser.add_argument("--max-pages", type=int, default=30)
    parser.add_argument("--pdf-extractor-method", default="ai_api", choices=["ai_api", "pdfplumber"])
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        raise SystemExit(f"missing input dir: {input_dir}")

    vocab = load_vocabulary()

    pdf_by_stem = {p.stem: p for p in input_dir.glob("*.pdf")}
    docx_by_stem = {p.stem: p for p in input_dir.glob("*.docx")}
    stems = sorted(set(pdf_by_stem).intersection(docx_by_stem))
    if not stems:
        raise SystemExit("no paired pdf/docx files found")

    extractor_method = (
        ExtractionMethod.AI_API if args.pdf_extractor_method == "ai_api" else ExtractionMethod.PDFPLUMBER
    )

    results: list[dict[str, Any]] = []
    for stem in stems:
        pdf_path = pdf_by_stem[stem]
        docx_path = docx_by_stem[stem]
        paper_id = _paper_id_from_stem(stem)

        pdf_tables = _pdf_tables_to_payloads(
            pdf_path,
            paper_id=paper_id,
            max_pages=max(1, args.max_pages),
            extractor_method=extractor_method,
        )
        docx_tables = _docx_tables_to_payloads(docx_path, paper_id=paper_id)

        pdf_claims = _extract_claims(pdf_tables, method=args.method, vocab=vocab)
        docx_claims = _extract_claims(docx_tables, method=args.method, vocab=vocab)

        pdf_keys = {_claim_key(c) for c in pdf_claims}
        docx_keys = {_claim_key(c) for c in docx_claims}
        overlap = pdf_keys.intersection(docx_keys)

        results.append(
            {
                "stem": stem,
                "paper_id": paper_id,
                "pdf_path": str(pdf_path),
                "docx_path": str(docx_path),
                "pdf_tables": len(pdf_tables),
                "docx_tables": len(docx_tables),
                "pdf_metrics": _side_metrics(pdf_claims),
                "docx_metrics": _side_metrics(docx_claims),
                "claim_key_overlap": {
                    "shared": len(overlap),
                    "pdf_only": len(pdf_keys - docx_keys),
                    "docx_only": len(docx_keys - pdf_keys),
                },
            }
        )

    summary = {
        "paired_files": len(results),
        "method": args.method,
        "pdf_extractor_method": args.pdf_extractor_method,
        "mean_pdf_claims": round(mean(r["pdf_metrics"]["claims"] for r in results), 3),
        "mean_docx_claims": round(mean(r["docx_metrics"]["claims"] for r in results), 3),
        "mean_pdf_unknown_rate": round(mean(r["pdf_metrics"]["direction_unknown_rate"] for r in results), 4),
        "mean_docx_unknown_rate": round(mean(r["docx_metrics"]["direction_unknown_rate"] for r in results), 4),
        "mean_pdf_mapped_rate": round(mean(r["pdf_metrics"]["mapped_both_rate"] for r in results), 4),
        "mean_docx_mapped_rate": round(mean(r["docx_metrics"]["mapped_both_rate"] for r in results), 4),
    }

    payload = {"summary": summary, "results": results}
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps(summary, indent=2))
    print(f"written={out_path}")


if __name__ == "__main__":
    main()
