#!/usr/bin/env python3
"""Quick structural QA for PDF->DOCX outputs.

Checks whether a DOCX is truly reconstructed text/tables vs embedded PDF stream text.
"""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path
from typing import Any


def _extract_doc_xml(docx_path: Path) -> str:
    with zipfile.ZipFile(docx_path) as zf:
        if "word/document.xml" not in zf.namelist():
            return ""
        return zf.read("word/document.xml").decode("utf-8", errors="ignore")


def evaluate_docx(docx_path: Path) -> dict[str, Any]:
    xml = _extract_doc_xml(docx_path)
    if not xml:
        return {
            "docx_path": str(docx_path),
            "valid_docx": False,
            "error": "missing word/document.xml",
        }
    texts = re.findall(r"<w:t[^>]*>(.*?)</w:t>", xml, re.S)
    joined = " ".join(t.strip() for t in texts if t.strip())
    w_tbl = xml.count("<w:tbl")
    w_tr = xml.count("<w:tr")
    w_tc = xml.count("<w:tc")
    contains_pdf_stream = ("%PDF-" in joined) or ("startxref" in joined and "endobj" in joined)
    stats_cues = {
        "F(": len(re.findall(r"\bF\s*\(", joined, re.I)),
        "t(": len(re.findall(r"\bt\s*\(", joined, re.I)),
        "p<": len(re.findall(r"\bp\s*[<=>]\s*0?\.\d+", joined, re.I)),
        "table_word": len(re.findall(r"\bTable\s+\d+", joined, re.I)),
    }
    quality = "good_table_reconstruction"
    if contains_pdf_stream:
        quality = "bad_embedded_pdf_stream"
    elif w_tbl == 0:
        quality = "poor_no_word_tables"
    return {
        "docx_path": str(docx_path),
        "valid_docx": True,
        "quality_label": quality,
        "w_tbl_count": w_tbl,
        "w_tr_count": w_tr,
        "w_tc_count": w_tc,
        "w_t_count": len(texts),
        "text_chars": len(joined),
        "contains_pdf_stream_markers": contains_pdf_stream,
        "stats_cues": stats_cues,
        "sample_text": joined[:400],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate table quality of converted DOCX files.")
    parser.add_argument("docx", nargs="+", help="DOCX file(s) to evaluate")
    parser.add_argument("--output", default="", help="Optional JSON output path")
    args = parser.parse_args()

    results = []
    for p in args.docx:
        path = Path(p)
        if not path.exists():
            results.append({"docx_path": str(path), "valid_docx": False, "error": "file_not_found"})
            continue
        results.append(evaluate_docx(path))

    payload = {"count": len(results), "results": results}
    print(json.dumps(payload, indent=2))
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"written={out}")


if __name__ == "__main__":
    main()
