#!/usr/bin/env python3
"""
Build a safe, topic-broad table extraction queue from Article Finder DB.

Policy goals:
1. Respect pruning protections (allowlist/neuro/high-citation).
2. Prefer broad topic coverage, not single-domain domination.
3. Preserve important/high-citation papers (must-include seeds + citation score).
4. Produce explicit review files for protected rejects.
"""

from __future__ import annotations

import argparse
import csv
import math
import re
import sqlite3
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


TOPIC_KEYWORDS = {
    "acoustic": ["noise", "sound", "acoustic", "auditory", "speech", "soundscape"],
    "air": ["air quality", "iaq", "ventilation", "co2", "voc", "indoor air"],
    "light": ["daylight", "lighting", "illuminance", "lux", "circadian", "window"],
    "biophilic": ["biophilic", "biophilia", "nature", "plant", "green", "vegetation"],
    "thermal": ["thermal", "temperature", "heat", "humidity", "hvac", "comfort"],
    "spatial": ["layout", "density", "ceiling", "wayfinding", "open plan", "enclosure"],
    "restoration": ["restoration", "restorative", "recovery", "stress recovery"],
    "cognition": ["attention", "cognitive", "memory", "focus", "executive function"],
    "affect": ["mood", "emotion", "stress", "anxiety", "wellbeing", "affect"],
}


@dataclass
class PaperRecord:
    paper_id: str
    doi: str
    title: str
    venue: str
    year: int
    abstract: str
    topic_decision: str
    triage_decision: str
    pdf_path: str
    citation_count: int
    topic_bucket: str
    protected_reasons: str
    must_include: bool
    priority_score: float
    selection_reason: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build topic-broad table extraction queue.")
    parser.add_argument(
        "--db",
        default="/Users/davidusa/REPOS/Article_Finder_v3_2_3/data/article_finder.db",
        help="Path to article_finder.db",
    )
    parser.add_argument(
        "--reject-csv",
        default="/Users/davidusa/REPOS/Article_Finder_v3_2_3/data/review/reject_candidates.csv",
        help="Reject candidates CSV from production_run.py",
    )
    parser.add_argument(
        "--must-include-seeds",
        default="config/table_must_include_seeds.txt",
        help="DOI/title seed file for forced inclusion priority",
    )
    parser.add_argument(
        "--output-dir",
        default="data/table_queue",
        help="Output folder for queue CSVs and summary",
    )
    parser.add_argument(
        "--per-topic-target",
        type=int,
        default=8,
        help="Initial target count per topic bucket before global fill",
    )
    parser.add_argument(
        "--max-total",
        type=int,
        default=120,
        help="Maximum total papers in queue",
    )
    parser.add_argument(
        "--high-cite-threshold",
        type=int,
        default=150,
        help="High-citation threshold; these are always protected",
    )
    return parser.parse_args()


def normalize(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.strip().lower())


def load_seed_rules(path: Path) -> Tuple[set[str], List[str]]:
    doi_seeds: set[str] = set()
    title_seeds: List[str] = []
    if not path.exists():
        return doi_seeds, title_seeds
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith("doi:"):
            doi_seeds.add(normalize(line.split(":", 1)[1]))
        elif line.lower().startswith("title:"):
            title_seeds.append(normalize(line.split(":", 1)[1]))
    return doi_seeds, title_seeds


def load_reject_protection(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    mapping: Dict[str, str] = {}
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            mapping[row.get("paper_id", "")] = row.get("protected_reasons", "")
    return mapping


def get_paper_columns(cursor: sqlite3.Cursor) -> set:
    return {row[1] for row in cursor.execute("PRAGMA table_info(papers)")}


def pick_citation_column(columns: set) -> str:
    for candidate in ("cited_by_count", "citation_count"):
        if candidate in columns:
            return candidate
    return ""


def fetch_local_citations(cursor: sqlite3.Cursor) -> Dict[str, int]:
    cursor.execute(
        "SELECT cited_paper_id, COUNT(*) FROM citations "
        "WHERE cited_paper_id IS NOT NULL GROUP BY cited_paper_id"
    )
    return {row[0]: int(row[1]) for row in cursor.fetchall()}


def classify_topic(title: str, abstract: str) -> str:
    text = normalize(f"{title} {abstract}")
    scores = {}
    for topic, keywords in TOPIC_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if kw in text:
                score += 1
        scores[topic] = score
    best_topic = max(scores, key=scores.get)
    return best_topic if scores[best_topic] > 0 else "other"


def is_must_include(doi: str, title: str, doi_seeds: set[str], title_seeds: List[str]) -> bool:
    doi_n = normalize(doi)
    title_n = normalize(title)
    if doi_n and doi_n in doi_seeds:
        return True
    return any(seed in title_n for seed in title_seeds)


def compute_priority(citation_count: int, year: int, must_include: bool, protected: bool) -> float:
    citation_score = math.log1p(max(citation_count, 0)) * 10.0
    recency_score = max(0, min((year or 0) - 1990, 40)) * 0.3
    must_include_boost = 100.0 if must_include else 0.0
    protected_boost = 25.0 if protected else 0.0
    return citation_score + recency_score + must_include_boost + protected_boost


def build_queue(args: argparse.Namespace) -> Tuple[List[PaperRecord], List[PaperRecord], Dict[str, int], str]:
    db_path = Path(args.db)
    reject_map = load_reject_protection(Path(args.reject_csv))
    doi_seeds, title_seeds = load_seed_rules(Path(args.must_include_seeds))

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    columns = get_paper_columns(cur)
    citation_column = pick_citation_column(columns)
    local_citations = fetch_local_citations(cur) if not citation_column else {}
    citation_mode = "global" if citation_column else "local"

    select_fields = [
        "paper_id",
        "doi",
        "title",
        "venue",
        "year",
        "abstract",
        "topic_decision",
        "triage_decision",
        "pdf_path",
    ]
    if citation_column:
        select_fields.append(f"{citation_column} AS citation_count")
    query = (
        f"SELECT {', '.join(select_fields)} FROM papers "
        "WHERE pdf_path IS NOT NULL AND pdf_path != ''"
    )
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()

    candidate_pool: List[PaperRecord] = []
    protected_review: List[PaperRecord] = []
    pool_counts = Counter()

    for row in rows:
        paper_id = row["paper_id"]
        title = row["title"] or ""
        abstract = row["abstract"] or ""
        topic_decision = normalize(row["topic_decision"] or "")
        triage_decision = normalize(row["triage_decision"] or "")
        protected_reasons = reject_map.get(paper_id, "")
        protected = bool(protected_reasons)
        citation_count = int(row["citation_count"] or 0) if citation_column else local_citations.get(paper_id, 0)
        high_cite = citation_count >= args.high_cite_threshold
        must_include = is_must_include(row["doi"] or "", title, doi_seeds, title_seeds)
        reject_candidate = paper_id in reject_map
        non_protected_reject = reject_candidate and not protected and not high_cite

        if non_protected_reject and not must_include:
            pool_counts["excluded_non_protected_reject"] += 1
            continue

        if topic_decision != "on_topic" and not (protected or high_cite or must_include):
            pool_counts["excluded_not_on_topic"] += 1
            continue

        topic_bucket = classify_topic(title, abstract)
        priority_score = compute_priority(citation_count, int(row["year"] or 0), must_include, protected)

        if must_include:
            reason = "must_include_seed"
        elif protected:
            reason = "protected_reject_review"
        elif high_cite:
            reason = f"high_citation>={args.high_cite_threshold}"
        else:
            reason = "on_topic_pdf"

        rec = PaperRecord(
            paper_id=paper_id,
            doi=row["doi"] or "",
            title=title,
            venue=row["venue"] or "",
            year=int(row["year"] or 0),
            abstract=abstract,
            topic_decision=topic_decision,
            triage_decision=triage_decision,
            pdf_path=row["pdf_path"] or "",
            citation_count=citation_count,
            topic_bucket=topic_bucket,
            protected_reasons=protected_reasons,
            must_include=must_include,
            priority_score=priority_score,
            selection_reason=reason,
        )

        if protected:
            protected_review.append(rec)
        candidate_pool.append(rec)
        pool_counts["pool_total"] += 1

    grouped: Dict[str, List[PaperRecord]] = defaultdict(list)
    for rec in candidate_pool:
        grouped[rec.topic_bucket].append(rec)
    for topic in grouped:
        grouped[topic].sort(
            key=lambda r: (r.must_include, r.priority_score, r.citation_count, r.year),
            reverse=True,
        )

    selected_ids = set()
    queue: List[PaperRecord] = []

    for topic in sorted(grouped.keys()):
        for rec in grouped[topic][: args.per_topic_target]:
            if rec.paper_id not in selected_ids:
                queue.append(rec)
                selected_ids.add(rec.paper_id)

    remaining = []
    for topic_recs in grouped.values():
        for rec in topic_recs:
            if rec.paper_id not in selected_ids:
                remaining.append(rec)
    remaining.sort(
        key=lambda r: (r.must_include, r.priority_score, r.citation_count, r.year),
        reverse=True,
    )

    for rec in remaining:
        if len(queue) >= args.max_total:
            break
        queue.append(rec)
        selected_ids.add(rec.paper_id)

    must_include_missing = [r for r in candidate_pool if r.must_include and r.paper_id not in selected_ids]
    for rec in must_include_missing:
        if rec.paper_id not in selected_ids:
            queue.append(rec)
            selected_ids.add(rec.paper_id)

    queue.sort(
        key=lambda r: (r.must_include, r.priority_score, r.citation_count, r.year),
        reverse=True,
    )
    return queue, protected_review, dict(pool_counts), citation_mode


def write_csv(path: Path, rows: List[PaperRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "paper_id",
        "doi",
        "title",
        "venue",
        "year",
        "topic_decision",
        "triage_decision",
        "topic_bucket",
        "citation_count",
        "priority_score",
        "selection_reason",
        "protected_reasons",
        "must_include",
        "pdf_path",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(
                {
                    "paper_id": r.paper_id,
                    "doi": r.doi,
                    "title": r.title,
                    "venue": r.venue,
                    "year": r.year,
                    "topic_decision": r.topic_decision,
                    "triage_decision": r.triage_decision,
                    "topic_bucket": r.topic_bucket,
                    "citation_count": r.citation_count,
                    "priority_score": f"{r.priority_score:.3f}",
                    "selection_reason": r.selection_reason,
                    "protected_reasons": r.protected_reasons,
                    "must_include": str(r.must_include).lower(),
                    "pdf_path": r.pdf_path,
                }
            )


def write_summary(path: Path, queue: List[PaperRecord], protected_review: List[PaperRecord], pool_counts: Dict[str, int], citation_mode: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    topic_counts = Counter(r.topic_bucket for r in queue)
    reason_counts = Counter(r.selection_reason for r in queue)
    must_include_count = sum(1 for r in queue if r.must_include)
    protected_in_queue = sum(1 for r in queue if r.protected_reasons)

    lines = []
    lines.append("# Table Extraction Queue Summary")
    lines.append("")
    lines.append(f"- Queue size: {len(queue)}")
    lines.append(f"- Must-include in queue: {must_include_count}")
    lines.append(f"- Protected records in queue: {protected_in_queue}")
    lines.append(f"- Protected review records: {len(protected_review)}")
    lines.append(f"- Citation mode: {citation_mode}")
    if pool_counts:
        lines.append("")
        lines.append("## Pool Filters")
        for key in sorted(pool_counts):
            lines.append(f"- {key}: {pool_counts[key]}")
    lines.append("")
    lines.append("## Topic Coverage")
    for topic, count in sorted(topic_counts.items()):
        lines.append(f"- {topic}: {count}")
    lines.append("")
    lines.append("## Selection Reasons")
    for reason, count in sorted(reason_counts.items()):
        lines.append(f"- {reason}: {count}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    queue, protected_review, pool_counts, citation_mode = build_queue(args)
    write_csv(output_dir / "table_extraction_queue.csv", queue)
    write_csv(output_dir / "protected_rejects_review.csv", protected_review)
    write_summary(
        output_dir / "table_extraction_queue_summary.md",
        queue=queue,
        protected_review=protected_review,
        pool_counts=pool_counts,
        citation_mode=citation_mode,
    )
    print(f"Wrote queue: {output_dir / 'table_extraction_queue.csv'} ({len(queue)} rows)")
    print(f"Wrote protected review: {output_dir / 'protected_rejects_review.csv'} ({len(protected_review)} rows)")
    print(f"Wrote summary: {output_dir / 'table_extraction_queue_summary.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
