#!/usr/bin/env python3
"""
Split table outputs into separate files by article type.

Inputs:
- Codex gold rows CSV
- Abstract reduced tables CSV
- Article Finder DB for title/abstract metadata
"""

from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.db_locator import resolve_article_finder_db


ARTICLE_TYPES = [
    "meta_analysis",
    "systematic_review",
    "narrative_review",
    "rct_interventional",
    "quasi_experimental",
    "observational",
    "cross_sectional_survey",
    "qualitative",
    "theoretical_conceptual",
    "methods_protocol",
    "unknown",
]


TEMPLATE_FAMILIES = [
    "empirical_v2",
    "meta_analysis",
    "systematic_review",
    "narrative_review",
    "theoretical",
    "conceptual_framework",
    "mixed_methods",
    "observational_field",
    "case_study",
    "interview_study",
    "ethnographic",
    "grounded_theory",
    "phenomenological",
    "thought_piece",
    "methods_protocol",
    "unknown",
]


def normalize(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def classify_article_type(title: str, abstract: str) -> str:
    text = normalize(f"{title} {abstract}")

    if any(k in text for k in ["meta-analysis", "meta analysis", "pooled effect", "forest plot"]):
        return "meta_analysis"
    if any(k in text for k in ["systematic review", "prisma", "search strategy", "inclusion criteria"]):
        return "systematic_review"
    if any(k in text for k in ["narrative review", "scoping review", "overview"]):
        return "narrative_review"
    if any(k in text for k in ["randomized", "randomised", "rct", "intervention group", "control group", "trial"]):
        return "rct_interventional"
    if any(k in text for k in ["quasi-experimental", "quasi experimental", "pre-post", "before and after"]):
        return "quasi_experimental"
    if any(k in text for k in ["cross-sectional", "cross sectional", "questionnaire", "survey"]):
        return "cross_sectional_survey"
    if any(k in text for k in ["cohort", "case-control", "observational study", "longitudinal"]):
        return "observational"
    if any(k in text for k in ["interview", "focus group", "ethnograph", "thematic analysis", "phenomenolog"]):
        return "qualitative"
    if any(k in text for k in ["conceptual framework", "theoretical framework", "theory", "hypothesis", "model of"]):
        return "theoretical_conceptual"
    if any(k in text for k in ["protocol", "methods paper", "methodological", "validation study"]):
        return "methods_protocol"
    return "unknown"


def classify_template_family(title: str, abstract: str) -> str:
    text = normalize(f"{title} {abstract}")

    if any(k in text for k in ["meta-analysis", "meta analysis", "pooled effect", "forest plot"]):
        return "meta_analysis"
    if any(k in text for k in ["systematic review", "prisma", "search strategy", "inclusion criteria"]):
        return "systematic_review"
    if any(k in text for k in ["narrative review", "scoping review", "overview"]):
        return "narrative_review"
    if any(k in text for k in ["mixed methods", "mixed-methods", "qualitative and quantitative"]):
        return "mixed_methods"
    if any(k in text for k in ["case study", "single case", "case report"]):
        return "case_study"
    if any(k in text for k in ["interview", "semi-structured", "focus group"]):
        return "interview_study"
    if any(k in text for k in ["ethnograph", "participant observation", "fieldwork"]):
        return "ethnographic"
    if any(k in text for k in ["grounded theory", "open coding", "axial coding"]):
        return "grounded_theory"
    if any(k in text for k in ["phenomenolog", "lived experience", "essence"]):
        return "phenomenological"
    if any(k in text for k in ["thought piece", "opinion", "commentary", "perspective"]):
        return "thought_piece"
    if any(k in text for k in ["conceptual framework", "framework", "taxonomy", "organizing principle"]):
        return "conceptual_framework"
    if any(k in text for k in ["theoretical", "theory", "proposition", "mechanism", "model of"]):
        return "theoretical"
    if any(k in text for k in ["observational study", "cohort", "case-control", "naturalistic"]):
        return "observational_field"
    if any(
        k in text
        for k in [
            "randomized",
            "randomised",
            "rct",
            "intervention group",
            "control group",
            "trial",
            "experiment",
            "quasi-experimental",
            "cross-sectional",
        ]
    ):
        return "empirical_v2"
    if any(k in text for k in ["protocol", "methods paper", "methodological", "validation study"]):
        return "methods_protocol"
    return "unknown"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build separate tables by article type.")
    parser.add_argument(
        "--db",
        default=None,
        help="Path to article_finder.db (auto-resolved if omitted)",
    )
    parser.add_argument(
        "--gold-csv",
        default="data/table_gold/codex_gold_v1/codex_gold_rows.csv",
        help="Codex gold rows CSV",
    )
    parser.add_argument(
        "--reduced-csv",
        default="data/table_queue/abstract_reduced_tables.csv",
        help="Abstract reduced rows CSV",
    )
    parser.add_argument(
        "--output-dir",
        default="data/table_gold/by_article_type",
        help="Output directory",
    )
    return parser.parse_args()


def load_paper_metadata(db_path: Path) -> Dict[str, Dict[str, str]]:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT paper_id, title, abstract FROM papers")
    out = {}
    for r in cur.fetchall():
        out[r["paper_id"]] = {"title": r["title"] or "", "abstract": r["abstract"] or ""}
    conn.close()
    return out


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: List[Dict[str, str]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def split_rows(
    rows: List[Dict[str, str]],
    meta: Dict[str, Dict[str, str]],
) -> tuple[Dict[str, List[Dict[str, str]]], Dict[str, List[Dict[str, str]]]]:
    article_type_buckets = defaultdict(list)
    template_family_buckets = defaultdict(list)
    for row in rows:
        pid = row.get("paper_id", "")
        m = meta.get(pid, {})
        article_type = classify_article_type(m.get("title", ""), m.get("abstract", ""))
        template_family = classify_template_family(m.get("title", ""), m.get("abstract", ""))
        row_copy = dict(row)
        row_copy["article_type"] = article_type
        row_copy["template_family"] = template_family
        article_type_buckets[article_type].append(row_copy)
        template_family_buckets[template_family].append(row_copy)
    return article_type_buckets, template_family_buckets


def main() -> int:
    args = parse_args()
    out_dir = Path(args.output_dir)
    af_db = resolve_article_finder_db(args.db)
    print(f"[build_article_type_tables] using af_db={af_db}")
    meta = load_paper_metadata(af_db)

    gold_rows = read_csv_rows(Path(args.gold_csv))
    reduced_rows = read_csv_rows(Path(args.reduced_csv))

    gold_buckets, gold_template_buckets = split_rows(gold_rows, meta)
    reduced_buckets, reduced_template_buckets = split_rows(reduced_rows, meta)

    gold_fields = list(gold_rows[0].keys()) + ["article_type", "template_family"] if gold_rows else ["article_type", "template_family"]
    reduced_fields = list(reduced_rows[0].keys()) + ["article_type", "template_family"] if reduced_rows else ["article_type", "template_family"]

    for t in ARTICLE_TYPES:
        write_csv(out_dir / f"gold_rows__{t}.csv", gold_buckets.get(t, []), gold_fields)
        write_csv(out_dir / f"reduced_rows__{t}.csv", reduced_buckets.get(t, []), reduced_fields)
    for t in TEMPLATE_FAMILIES:
        write_csv(out_dir / f"gold_rows__template__{t}.csv", gold_template_buckets.get(t, []), gold_fields)
        write_csv(out_dir / f"reduced_rows__template__{t}.csv", reduced_template_buckets.get(t, []), reduced_fields)

    summary_lines = []
    summary_lines.append("# Article Type Split Summary")
    summary_lines.append("")
    summary_lines.append("## Gold Rows")
    gold_counts = Counter({t: len(gold_buckets.get(t, [])) for t in ARTICLE_TYPES})
    for t in ARTICLE_TYPES:
        summary_lines.append(f"- {t}: {gold_counts[t]}")
    summary_lines.append("")
    summary_lines.append("## Reduced Rows")
    reduced_counts = Counter({t: len(reduced_buckets.get(t, [])) for t in ARTICLE_TYPES})
    for t in ARTICLE_TYPES:
        summary_lines.append(f"- {t}: {reduced_counts[t]}")
    summary_lines.append("")
    summary_lines.append("## Gold Rows (Template Family)")
    gold_template_counts = Counter({t: len(gold_template_buckets.get(t, [])) for t in TEMPLATE_FAMILIES})
    for t in TEMPLATE_FAMILIES:
        summary_lines.append(f"- {t}: {gold_template_counts[t]}")
    summary_lines.append("")
    summary_lines.append("## Reduced Rows (Template Family)")
    reduced_template_counts = Counter({t: len(reduced_template_buckets.get(t, [])) for t in TEMPLATE_FAMILIES})
    for t in TEMPLATE_FAMILIES:
        summary_lines.append(f"- {t}: {reduced_template_counts[t]}")

    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    print(f"Wrote article-type split tables under: {out_dir}")
    print(f"Summary: {out_dir / 'summary.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
