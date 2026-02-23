"""Table reconstruction and semantic classification for Sprint D remediation."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from src.extraction.contracts import assert_valid_payload

TABLE_TYPES = [
    "RESULTS_ANOVA",
    "RESULTS_REGRESSION",
    "RESULTS_CORRELATION",
    "RESULTS_TTEST",
    "RESULTS_DESCRIPTIVE",
    "LITERATURE_REVIEW",
    "META_ANALYTIC",
    "DEMOGRAPHICS",
    "MODEL_FIT",
    "PROTOCOL",
    "MATERIALS",
    "MEASUREMENT_SPECS",
    "GARBAGE",
    "OTHER",
]

EXTRACTABLE_TYPES = {
    "RESULTS_ANOVA",
    "RESULTS_REGRESSION",
    "RESULTS_CORRELATION",
    "RESULTS_TTEST",
    "RESULTS_DESCRIPTIVE",
    "LITERATURE_REVIEW",
    "META_ANALYTIC",
}

_TYPE_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "RESULTS_ANOVA": [
        re.compile(r"\bf\s*\(\s*\d+\s*,\s*\d+\s*\)", re.IGNORECASE),
        re.compile(r"\banova\b", re.IGNORECASE),
    ],
    "RESULTS_REGRESSION": [
        re.compile(r"(?:\bbeta\b|β|\bb\b)\s*=?\s*[-+]?\d", re.IGNORECASE),
        re.compile(r"\br\^?2\b|r²|adjusted\s+r", re.IGNORECASE),
        re.compile(r"\bse\b", re.IGNORECASE),
    ],
    "RESULTS_CORRELATION": [
        re.compile(r"\bcorrelation(?:s| matrix)?\b", re.IGNORECASE),
        re.compile(r"\br\s*=\s*[-+]?\d\.\d+", re.IGNORECASE),
        re.compile(r"\bpearson\b", re.IGNORECASE),
    ],
    "RESULTS_TTEST": [
        re.compile(r"\bt\s*\(\s*\d+\s*\)", re.IGNORECASE),
        re.compile(r"\bt[-\s]?test\b", re.IGNORECASE),
    ],
    "RESULTS_DESCRIPTIVE": [
        re.compile(r"\bmean\b|\bm\b", re.IGNORECASE),
        re.compile(r"\bsd\b|\bstdev\b", re.IGNORECASE),
        re.compile(r"\bn\s*=\s*\d+|\bn\b", re.IGNORECASE),
    ],
    "LITERATURE_REVIEW": [
        re.compile(r"\b[A-Z][a-z]+(?:\s+et al\.)?\s*\(\d{4}\)"),
        re.compile(r"\bstudy\b|\bfindings?\b", re.IGNORECASE),
    ],
    "META_ANALYTIC": [
        re.compile(r"\bmeta[-\s]?analysis\b|\bforest plot\b", re.IGNORECASE),
        re.compile(r"\beffect size\b|\bweight\b|\bci\b", re.IGNORECASE),
    ],
    "DEMOGRAPHICS": [
        re.compile(r"\bage\b|\bgender\b|\bsex\b|\beducation\b", re.IGNORECASE),
        re.compile(r"\bparticipants?\b|\bsample\b", re.IGNORECASE),
    ],
    "MODEL_FIT": [
        re.compile(r"χ²|chi[-\s]?square|rmsea|cfi|gfi|aic|bic", re.IGNORECASE),
        re.compile(r"χ²\s*/\s*df|chi[-\s]?square\s*/\s*df", re.IGNORECASE),
    ],
    "PROTOCOL": [
        re.compile(r"\bstep\s+\d+\b|\bprocedure\b|\bprotocol\b", re.IGNORECASE),
        re.compile(r"\binstruction\b|\btask\b", re.IGNORECASE),
    ],
    "MATERIALS": [
        re.compile(r"\bstimuli\b|\bmaterials?\b", re.IGNORECASE),
        re.compile(r"\btexture\b|\bcolor\b|\bswatch\b", re.IGNORECASE),
    ],
    "MEASUREMENT_SPECS": [
        re.compile(r"\bcalibration\b|\binstrument\b|\bsensor\b", re.IGNORECASE),
        re.compile(r"\bmicrophone\b|\blux meter\b|\bthermometer\b", re.IGNORECASE),
    ],
}


def _safe_int(value: str | int | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    value = str(value).strip()
    if not value:
        return None
    try:
        return int(float(value))
    except ValueError:
        return None


def _row_sort_key(row: dict[str, Any]) -> tuple[int, int]:
    row_num = row.get("row_index")
    if row_num is None:
        return (1, row.get("_seq", 0))
    return (0, int(row_num))


def _row_text(row: dict[str, str]) -> str:
    return (
        row.get("source_quote")
        or row.get("statement")
        or row.get("content")
        or ""
    ).strip()


def reconstruct_tables(csv_path: str, paper_ids: list[str]) -> dict[str, dict[str, Any]]:
    """Group CSV rows by source_table_id for the supplied paper set."""
    allowed = set(paper_ids)
    tables: dict[str, dict[str, Any]] = {}

    with open(csv_path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for seq, row in enumerate(reader):
            table_id = (row.get("source_table_id") or "").strip()
            paper_id = (row.get("paper_id") or "").strip()
            if not table_id or not paper_id or paper_id not in allowed:
                continue

            entry = tables.setdefault(
                table_id,
                {
                    "paper_id": paper_id,
                    "page": _safe_int(row.get("source_page_start")),
                    "rows": [],
                },
            )

            row_payload = {
                "row_index": _safe_int(row.get("source_table_row")),
                "text": _row_text(row),
                "statement": (row.get("statement") or "").strip(),
                "source_quote": (row.get("source_quote") or "").strip(),
                "quality_flag": (row.get("quality_flag") or "").strip(),
                "_seq": seq,
            }
            entry["rows"].append(row_payload)

    for table in tables.values():
        table["rows"].sort(key=_row_sort_key)
        for row in table["rows"]:
            row.pop("_seq", None)

    return tables


def _detect_ocr_artifacts(text: str) -> tuple[str, list[str], float]:
    lowered = text.lower()
    letters = [ch for ch in lowered if ch.isalpha()]
    duplicate_adjacent = 0
    if letters:
        duplicate_adjacent = sum(1 for i in range(len(letters) - 1) if letters[i] == letters[i + 1])
    duplicate_ratio = duplicate_adjacent / max(len(letters), 1)

    artifact_flags: list[str] = []
    score = 0.0

    if duplicate_ratio > 0.08:
        artifact_flags.append("doubled_characters")
        score += 1.0
    if re.search(r"\b[a-z]{22,}\b", lowered):
        artifact_flags.append("concatenated_words")
        score += 1.0
    if re.search(r"[^\w\s]{5,}", text):
        artifact_flags.append("non_word_sequences")
        score += 0.5

    quality = "clean"
    if score >= 1.5:
        quality = "garbled"
    elif score > 0:
        quality = "noisy"
    return quality, artifact_flags, score


def classify_table(table: dict[str, Any]) -> dict[str, Any]:
    """Classify one reconstructed table into a semantic table type."""
    rows = table.get("rows", [])
    joined = "\n".join((row.get("text") or "") for row in rows if row.get("text"))
    joined = joined.strip()

    if not joined:
        return {
            "type": "OTHER",
            "confidence": 0.3,
            "extractable": False,
            "ocr_quality": "clean",
            "ocr_artifacts": [],
            "sample_content": "",
        }

    ocr_quality, ocr_artifacts, artifact_score = _detect_ocr_artifacts(joined)
    scores: Counter[str] = Counter()
    for table_type, patterns in _TYPE_PATTERNS.items():
        for pattern in patterns:
            if pattern.search(joined):
                scores[table_type] += 1

    if ocr_quality == "garbled" and artifact_score >= 1.5:
        chosen_type = "GARBAGE"
        confidence = 0.9
    else:
        chosen_type = "OTHER"
        top_score = 0
        if scores:
            chosen_type, top_score = max(scores.items(), key=lambda item: (item[1], item[0]))
        confidence = 0.35 if top_score == 0 else min(0.95, 0.55 + 0.12 * top_score)
        if ocr_quality == "noisy":
            confidence = max(0.4, confidence - 0.1)

    return {
        "type": chosen_type,
        "confidence": round(confidence, 2),
        "extractable": chosen_type in EXTRACTABLE_TYPES,
        "ocr_quality": ocr_quality,
        "ocr_artifacts": ocr_artifacts,
        "sample_content": joined[:280],
    }


def _load_triaged_paper_ids(triage_path: str, strict_contracts: bool = True) -> list[str]:
    with open(triage_path, "r", encoding="utf-8") as handle:
        triage_data = json.load(handle)
    assert_valid_payload("paper_triage", triage_data, strict=strict_contracts)
    if isinstance(triage_data, dict) and isinstance(triage_data.get("papers"), list):
        paper_ids: list[str] = []
        for paper in triage_data["papers"]:
            if not isinstance(paper, dict):
                continue
            triage_type = (paper.get("triage_type") or paper.get("type") or "").strip()
            if triage_type in {"empirical", "review", "meta_analysis"}:
                paper_id = (paper.get("paper_id") or "").strip()
                if paper_id:
                    paper_ids.append(paper_id)
        return paper_ids

    if isinstance(triage_data, dict):
        return [
            paper_id
            for paper_id, info in triage_data.items()
            if isinstance(info, dict)
            and (info.get("type") or info.get("triage_type")) in {"empirical", "review", "meta_analysis"}
        ]

    raise ValueError(f"Unsupported triage file format: {triage_path}")


def classify_tables(
    csv_path: str = "data/production/realtime_pdf_confirmed_rows.csv",
    triage_path: str = "data/production/paper_triage.json",
    output_path: str = "data/production/table_classifications.json",
    strict_contracts: bool = True,
) -> dict[str, Any]:
    """Reconstruct and classify tables for triaged extractable papers."""
    paper_ids = _load_triaged_paper_ids(triage_path, strict_contracts=strict_contracts)
    tables = reconstruct_tables(csv_path=csv_path, paper_ids=paper_ids)

    classifications: dict[str, dict[str, Any]] = {}
    type_counter: Counter[str] = Counter()
    ocr_counter: Counter[str] = Counter()

    for table_id, table in tables.items():
        classified = classify_table(table)
        record = {
            "paper_id": table.get("paper_id"),
            "page": table.get("page"),
            "type": classified["type"],
            "confidence": classified["confidence"],
            "n_rows": len(table.get("rows", [])),
            "extractable": classified["extractable"],
            "ocr_quality": classified["ocr_quality"],
            "ocr_artifacts": classified["ocr_artifacts"],
            "sample_content": classified["sample_content"],
        }
        classifications[table_id] = record
        type_counter.update([record["type"]])
        ocr_counter.update([record["ocr_quality"]])

    assert_valid_payload("table_classifications", classifications, strict=strict_contracts)

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(classifications, handle, indent=2, ensure_ascii=True, sort_keys=True)

    return {
        "tables_total": len(classifications),
        "tables_extractable": sum(1 for c in classifications.values() if c["extractable"]),
        "tables_garbage": sum(1 for c in classifications.values() if c["type"] == "GARBAGE"),
        "counts_by_type": dict(type_counter),
        "counts_by_ocr_quality": dict(ocr_counter),
        "paper_ids_total": len(paper_ids),
        "output_path": str(out_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Reconstruct and classify extracted PDF tables.")
    parser.add_argument(
        "--csv-path",
        default="data/production/realtime_pdf_confirmed_rows.csv",
        help="Path to realtime PDF extraction CSV.",
    )
    parser.add_argument(
        "--triage-path",
        default="data/production/paper_triage.json",
        help="Path to paper triage JSON.",
    )
    parser.add_argument(
        "--output-path",
        default="data/production/table_classifications.json",
        help="Where to write table classifications.",
    )
    args = parser.parse_args()
    summary = classify_tables(
        csv_path=args.csv_path,
        triage_path=args.triage_path,
        output_path=args.output_path,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
