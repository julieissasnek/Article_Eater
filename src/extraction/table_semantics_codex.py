"""Table semantic profiling for precision-first extraction gating."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.extraction.row_classifier_codex import RowProfile, classify_row_content


SEMANTIC_TYPES = {
    "statistical_results",
    "correlation_matrix",
    "regression_coefficients",
    "stepwise_regression",
    "study_summary",
    "demographics",
    "model_fit",
    "references",
    "artifact",
    "unknown",
}

EXTRACTABLE_SEMANTICS = {
    "statistical_results",
    "correlation_matrix",
    "regression_coefficients",
    "stepwise_regression",
    "study_summary",
}


def _safe_int(value: str | int | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    raw = str(value).strip()
    if not raw:
        return None
    try:
        return int(float(raw))
    except ValueError:
        return None


def _row_sort_key(row: dict[str, Any]) -> tuple[int, int]:
    row_index = row.get("row_index")
    if isinstance(row_index, int):
        return (0, row_index)
    return (1, int(row.get("_seq", 0)))


def build_table_content_profile(table: dict[str, Any]) -> dict[str, Any]:
    """Build a semantic profile for one reconstructed table."""
    rows = table.get("rows", [])
    row_profiles: list[RowProfile] = []
    for row in rows:
        text = row.get("text") or row.get("source_quote") or row.get("statement") or ""
        row_profiles.append(classify_row_content(text))

    counts = Counter(profile.label for profile in row_profiles)
    total = len(row_profiles)
    total = max(1, total)

    citation_density = counts["CITATION_ROW"] / total
    stat_density = counts["STAT_ROW"] / total
    model_fit_density = counts["MODEL_FIT_ROW"] / total
    demo_density = counts["DEMOGRAPHIC_ROW"] / total
    junk_density = counts["JUNK_ROW"] / total

    normalized_table_text = "\n".join(profile.normalized_text for profile in row_profiles).lower()
    table_type_hint = str(table.get("type") or "").strip()
    semantic_type = "unknown"
    confidence = 0.45
    reasons: list[str] = []

    if junk_density >= 0.35:
        semantic_type = "artifact"
        confidence = 0.9
        reasons.append("high_junk_density")
    elif model_fit_density >= 0.45:
        semantic_type = "model_fit"
        confidence = 0.88
        reasons.append("model_fit_rows_dominate")
    elif citation_density >= 0.5 and stat_density < 0.15:
        semantic_type = "references"
        confidence = 0.86
        reasons.append("citation_density_high")
    elif demo_density >= 0.5 and stat_density < 0.25:
        semantic_type = "demographics"
        confidence = 0.82
        reasons.append("demographic_rows_dominate")
    
    # Stepwise Regression Detection
    elif ("step 1" in normalized_table_text or "model 1" in normalized_table_text) and \
         ("r2" in normalized_table_text or "change" in normalized_table_text or "∆" in normalized_table_text):
        semantic_type = "stepwise_regression"
        confidence = 0.85
        reasons.append("stepwise_signals_present")
        
    elif "beta" in normalized_table_text or "β" in normalized_table_text:
        semantic_type = "regression_coefficients"
        confidence = 0.84
        reasons.append("beta_tokens_present")
    elif "r =" in normalized_table_text and "correlation" in normalized_table_text:
        semantic_type = "correlation_matrix"
        confidence = 0.84
        reasons.append("correlation_signals_present")
    elif stat_density >= 0.25:
        semantic_type = "statistical_results"
        confidence = 0.78
        reasons.append("stat_rows_present")
    elif citation_density >= 0.25 and stat_density >= 0.1:
        semantic_type = "study_summary"
        confidence = 0.72
        reasons.append("mixed_citation_and_stats")

    if semantic_type == "unknown" and table_type_hint:
        if table_type_hint == "RESULTS_REGRESSION":
            semantic_type = "regression_coefficients"
            confidence = 0.62
            reasons.append("table_type_hint")
        elif table_type_hint == "RESULTS_CORRELATION":
            semantic_type = "correlation_matrix"
            confidence = 0.62
            reasons.append("table_type_hint")
        elif table_type_hint in {"RESULTS_ANOVA", "RESULTS_TTEST", "RESULTS_DESCRIPTIVE", "META_ANALYTIC"}:
            semantic_type = "statistical_results"
            confidence = 0.6
            reasons.append("table_type_hint")
        elif table_type_hint == "LITERATURE_REVIEW":
            semantic_type = "study_summary"
            confidence = 0.6
            reasons.append("table_type_hint")

    extractable = semantic_type in EXTRACTABLE_SEMANTICS
    exclusion_reasons: list[str] = []

    if semantic_type in {"artifact", "references", "model_fit", "demographics"}:
        extractable = False
        exclusion_reasons.append(f"semantic_type={semantic_type}")
    if junk_density >= 0.2:
        exclusion_reasons.append("junk_density_high")
    if citation_density >= 0.6 and stat_density < 0.2:
        exclusion_reasons.append("citation_heavy_no_stats")
    if not counts["STAT_ROW"] and semantic_type != "study_summary" and confidence >= 0.75:
        exclusion_reasons.append("no_stat_rows")
    if exclusion_reasons:
        extractable = False

    return {
        "table_id": table.get("table_id") or table.get("source_table_id"),
        "paper_id": table.get("paper_id"),
        "semantic_type": semantic_type,
        "semantic_confidence": round(confidence, 2),
        "table_type_hint": table_type_hint,
        "extractable": extractable,
        "exclusion_reasons": exclusion_reasons,
        "row_label_counts": dict(counts),
        "quality_metrics": {
            "citation_density": round(citation_density, 3),
            "stat_density": round(stat_density, 3),
            "model_fit_density": round(model_fit_density, 3),
            "demographic_density": round(demo_density, 3),
            "junk_density": round(junk_density, 3),
        },
        "sample_rows": [profile.normalized_text[:180] for profile in row_profiles[:3]],
        "row_profiles": [
            {
                "label": profile.label,
                "confidence": round(profile.confidence, 2),
                "artifact_flags": list(profile.artifact_flags),
            }
            for profile in row_profiles
        ],
    }


def _load_table_classes(table_class_path: str) -> dict[str, dict[str, Any]]:
    with open(table_class_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Unsupported table classifications payload: {table_class_path}")
    return {str(table_id): rec for table_id, rec in payload.items() if isinstance(rec, dict)}


def _load_table_rows(csv_path: str, table_ids: set[str]) -> dict[str, list[dict[str, Any]]]:
    rows_by_table: dict[str, list[dict[str, Any]]] = defaultdict(list)
    with open(csv_path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for seq, row in enumerate(reader):
            table_id = (row.get("source_table_id") or "").strip()
            if not table_id or table_id not in table_ids:
                continue
            text = row.get("source_quote") or row.get("statement") or row.get("content") or ""
            rows_by_table[table_id].append(
                {
                    "row_index": _safe_int(row.get("source_table_row")),
                    "text": text.strip(),
                    "_seq": seq,
                }
            )
    for rows in rows_by_table.values():
        rows.sort(key=_row_sort_key)
        for row in rows:
            row.pop("_seq", None)
    return rows_by_table


def profile_tables_from_files(
    csv_path: str = "data/production/realtime_pdf_confirmed_rows.csv",
    table_class_path: str = "data/production/table_classifications.json",
    output_path: str = "data/production/table_content_profiles_codex.json",
    limit: int | None = None,
) -> dict[str, Any]:
    """Profile table semantics from existing table classifications + CSV rows."""
    table_classes = _load_table_classes(table_class_path)
    table_ids = list(table_classes.keys())
    if limit is not None:
        table_ids = table_ids[:limit]
    row_lookup = _load_table_rows(csv_path, set(table_ids))

    profiles: dict[str, dict[str, Any]] = {}
    semantic_counts: Counter[str] = Counter()
    extractable_count = 0

    for table_id in table_ids:
        rec = table_classes[table_id]
        table_obj = {
            "table_id": table_id,
            "paper_id": rec.get("paper_id"),
            "rows": row_lookup.get(table_id, []),
        }
        profile = build_table_content_profile(table_obj)
        profiles[table_id] = profile
        semantic_counts.update([profile["semantic_type"]])
        if profile["extractable"]:
            extractable_count += 1

    out = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tables_profiled": len(profiles),
        "semantic_counts": dict(semantic_counts),
        "extractable_tables": extractable_count,
        "profiles": profiles,
    }
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(out, handle, indent=2, ensure_ascii=True)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Build codex table semantic profiles.")
    parser.add_argument("--csv-path", default="data/production/realtime_pdf_confirmed_rows.csv")
    parser.add_argument("--table-class-path", default="data/production/table_classifications.json")
    parser.add_argument("--output-path", default="data/production/table_content_profiles_codex.json")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    summary = profile_tables_from_files(
        csv_path=args.csv_path,
        table_class_path=args.table_class_path,
        output_path=args.output_path,
        limit=args.limit,
    )
    print(
        json.dumps(
            {
                "tables_profiled": summary["tables_profiled"],
                "extractable_tables": summary["extractable_tables"],
                "semantic_counts": summary["semantic_counts"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
