#!/usr/bin/env python3
"""
Compare model table extraction output against codex gold rows.

Expected schema for both files (CSV):
- paper_id, table_id, row_index, claim_type, content,
- intervention, control, outcome, sample_size,
- effect_size, effect_size_type, ci_lower, ci_upper, p_value
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
from typing import Dict, Tuple


KEY_FIELDS = [
    "claim_type",
    "content",
    "intervention",
    "control",
    "outcome",
    "sample_size",
    "effect_size",
    "effect_size_type",
    "ci_lower",
    "ci_upper",
    "p_value",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare model rows to codex gold rows.")
    parser.add_argument(
        "--gold-csv",
        default="data/table_gold/codex_gold_v1/codex_gold_rows.csv",
        help="Codex gold rows CSV",
    )
    parser.add_argument(
        "--model-csv",
        required=True,
        help="Model output CSV to compare (Haiku or other)",
    )
    parser.add_argument(
        "--output-md",
        default="data/table_gold/comparison_report.md",
        help="Output markdown report",
    )
    return parser.parse_args()


def norm(v: str) -> str:
    return (v or "").strip().lower()


def row_key(row: Dict[str, str]) -> Tuple[str, str, str]:
    return (norm(row.get("paper_id", "")), norm(row.get("table_id", "")), norm(row.get("row_index", "")))


def load_csv(path: Path) -> Dict[Tuple[str, str, str], Dict[str, str]]:
    data = {}
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            data[row_key(row)] = row
    return data


def main() -> int:
    args = parse_args()
    gold_path = Path(args.gold_csv)
    model_path = Path(args.model_csv)

    gold = load_csv(gold_path)
    model = load_csv(model_path)

    keys_gold = set(gold.keys())
    keys_model = set(model.keys())
    overlap = sorted(keys_gold & keys_model)

    field_hits = Counter()
    field_total = Counter()

    for key in overlap:
        g = gold[key]
        m = model[key]
        for field in KEY_FIELDS:
            gv = norm(g.get(field, ""))
            mv = norm(m.get(field, ""))
            field_total[field] += 1
            if gv == mv:
                field_hits[field] += 1

    lines = []
    lines.append("# Gold vs Model Table Comparison")
    lines.append("")
    lines.append(f"- Gold rows: {len(keys_gold)}")
    lines.append(f"- Model rows: {len(keys_model)}")
    lines.append(f"- Overlap rows: {len(overlap)}")
    lines.append(f"- Gold-only rows: {len(keys_gold - keys_model)}")
    lines.append(f"- Model-only rows: {len(keys_model - keys_gold)}")
    lines.append("")
    lines.append("## Field Exact-Match Accuracy")
    for field in KEY_FIELDS:
        total = field_total[field]
        hits = field_hits[field]
        acc = (hits / total) if total else 0.0
        lines.append(f"- {field}: {hits}/{total} ({acc:.1%})")

    Path(args.output_md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_md).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote comparison report: {args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
