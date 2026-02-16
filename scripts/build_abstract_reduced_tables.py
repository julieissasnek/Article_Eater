#!/usr/bin/env python3
"""
Build abstract-derived reduced table rows for broad coverage, and a human
download priority list for important papers that still lack PDFs.
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

ENV_KEYWORDS = {
    "daylight": ["daylight", "sunlight", "natural light", "illumination", "lux", "lighting"],
    "noise": ["noise", "acoustic", "sound", "soundscape", "speech intelligibility"],
    "air_quality": ["air quality", "iaq", "co2", "ventilation", "voc", "indoor air"],
    "thermal": ["thermal", "temperature", "humidity", "hvac", "heat", "cooling"],
    "biophilia": ["biophilic", "biophilia", "plants", "vegetation", "greenery", "nature"],
    "spatial_layout": ["layout", "open plan", "density", "ceiling", "enclosure", "wayfinding"],
}

OUTCOME_KEYWORDS = {
    "stress": ["stress", "cortisol", "anxiety", "tension"],
    "attention": ["attention", "focus", "concentration", "vigilance"],
    "cognition": ["cognitive", "memory", "executive function", "mental fatigue"],
    "productivity": ["productivity", "performance", "task performance", "efficiency"],
    "mood": ["mood", "affect", "emotion", "wellbeing", "well-being"],
    "sleep": ["sleep", "circadian", "alertness", "fatigue"],
}

BUILT_ENV_CONTEXT = [
    "building",
    "architecture",
    "architectural",
    "interior",
    "office",
    "workplace",
    "hospital",
    "school",
    "classroom",
    "indoor",
    "room",
    "residential",
    "housing",
    "home",
    "urban",
]

OFFTOPIC_STRONG = [
    "underwater",
    "marine",
    "fisher",
    "amphipod",
    "zebrafish",
    "mice",
    "rats",
    "animal model",
    "petroleum",
    "offshore",
    "pipeline",
    "polymer",
    "nanoparticle",
    "agriculture",
    "spaceflight",
    "ocular",
    "chemotherapy",
    "tumor",
]

POSITIVE_TERMS = ["increase", "improve", "enhance", "boost", "higher", "better", "reduce stress"]
NEGATIVE_TERMS = ["decrease", "reduce", "lower", "impair", "worse", "higher stress"]
NULL_TERMS = ["no significant", "not significant", "no association", "null effect", "no effect"]


@dataclass
class ReducedRow:
    paper_id: str
    doi: str
    title: str
    year: int
    venue: str
    topic_bucket: str
    citation_count: int
    environment_variable: str
    outcome_variable: str
    effect_direction: str
    sample_n: str
    confidence_tier: str
    evidence_level: str
    provenance_tier: str
    notes: str
    abstract_snippet: str
    pdf_available: str


@dataclass
class DownloadPriority:
    paper_id: str
    doi: str
    title: str
    year: int
    venue: str
    topic_bucket: str
    citation_count: int
    priority_score: float
    reasons: str
    url: str


def normalize(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.strip().lower())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build abstract reduced tables + PDF download priorities.")
    parser.add_argument(
        "--db",
        default="/Users/davidusa/REPOS/Article_Finder_v3_2_3/data/article_finder.db",
        help="Path to article_finder.db",
    )
    parser.add_argument(
        "--must-include-seeds",
        default="config/table_must_include_seeds.txt",
        help="DOI/title seed file for must-include importance",
    )
    parser.add_argument(
        "--reject-csv",
        default="/Users/davidusa/REPOS/Article_Finder_v3_2_3/data/review/reject_candidates.csv",
        help="Reject candidates CSV from production_run.py",
    )
    parser.add_argument(
        "--hbe-allowlist",
        default="/Users/davidusa/REPOS/Article_Finder_v3_2_3/config/hbe_journals_allowlist.txt",
        help="HBE venue allowlist path",
    )
    parser.add_argument(
        "--neuro-allowlist",
        default="/Users/davidusa/REPOS/Article_Finder_v3_2_3/config/neuroscience_venues_allowlist.txt",
        help="Neuroscience venue allowlist path",
    )
    parser.add_argument(
        "--output-dir",
        default="data/table_queue",
        help="Output directory",
    )
    parser.add_argument(
        "--high-cite-threshold",
        type=int,
        default=150,
        help="High-citation threshold for download prioritization",
    )
    parser.add_argument(
        "--download-top-k",
        type=int,
        default=150,
        help="Max papers in download priority list",
    )
    parser.add_argument(
        "--per-topic-download-floor",
        type=int,
        default=8,
        help="Minimum per-topic items in priority list before global fill",
    )
    return parser.parse_args()


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


def load_allowlist(path: Path) -> set[str]:
    if not path.exists():
        return set()
    values = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        values.add(normalize(line))
    return values


def classify_topic(title: str, abstract: str) -> str:
    text = normalize(f"{title} {abstract}")
    scores = {topic: 0 for topic in TOPIC_KEYWORDS}
    for topic, keywords in TOPIC_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                scores[topic] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "other"


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


def find_canonical_var(text: str, mapping: Dict[str, List[str]], fallback: str) -> str:
    scores = {}
    for canonical, keywords in mapping.items():
        scores[canonical] = sum(1 for kw in keywords if kw in text)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else fallback


def detect_effect_direction(text: str) -> str:
    if any(term in text for term in NULL_TERMS):
        return "null"
    pos = any(term in text for term in POSITIVE_TERMS)
    neg = any(term in text for term in NEGATIVE_TERMS)
    if pos and neg:
        return "mixed"
    if pos:
        return "positive"
    if neg:
        return "negative"
    return "unknown"


def extract_sample_n(text: str) -> str:
    match = re.search(r"\bn\s*=\s*(\d+)\b", text)
    return match.group(1) if match else ""


def has_built_env_signal(text: str) -> bool:
    return any(term in text for term in BUILT_ENV_CONTEXT)


def has_human_outcome_signal(text: str) -> bool:
    for keywords in OUTCOME_KEYWORDS.values():
        if any(term in text for term in keywords):
            return True
    return False


def has_strong_offtopic_signal(text: str) -> bool:
    return any(term in text for term in OFFTOPIC_STRONG)


def has_strict_built_env_signal(text: str) -> bool:
    strict_terms = [
        "architecture",
        "architectural",
        "building",
        "interior",
        "office",
        "workplace",
        "classroom",
        "hospital",
        "indoor",
        "room",
        "housing",
        "campus",
    ]
    return any(term in text for term in strict_terms)


def build_reduced_row(
    paper: sqlite3.Row,
    citation_count: int,
    topic_bucket: str,
) -> ReducedRow:
    abstract = normalize(paper["abstract"] or "")
    environment_var = find_canonical_var(abstract, ENV_KEYWORDS, "unspecified_environment")
    outcome_var = find_canonical_var(abstract, OUTCOME_KEYWORDS, "unspecified_outcome")
    effect_direction = detect_effect_direction(abstract)
    sample_n = extract_sample_n(abstract)

    confidence_tier = "low"
    notes = ["abstract_only"]
    if sample_n:
        notes.append(f"n={sample_n}")
    if effect_direction in {"positive", "negative", "null", "mixed"}:
        confidence_tier = "medium"
    if environment_var == "unspecified_environment" or outcome_var == "unspecified_outcome":
        confidence_tier = "low"
        notes.append("weak_variable_resolution")

    snippet = (paper["abstract"] or "").strip()
    if len(snippet) > 320:
        snippet = snippet[:317] + "..."

    return ReducedRow(
        paper_id=paper["paper_id"],
        doi=paper["doi"] or "",
        title=paper["title"] or "",
        year=int(paper["year"] or 0),
        venue=paper["venue"] or "",
        topic_bucket=topic_bucket,
        citation_count=citation_count,
        environment_variable=environment_var,
        outcome_variable=outcome_var,
        effect_direction=effect_direction,
        sample_n=sample_n,
        confidence_tier=confidence_tier,
        evidence_level="abstract_only_reduced_table",
        provenance_tier="abstract_provisional",
        notes=";".join(notes),
        abstract_snippet=snippet,
        pdf_available="yes" if (paper["pdf_path"] or "").strip() else "no",
    )


def is_must_include(doi: str, title: str, doi_seeds: set[str], title_seeds: List[str]) -> bool:
    doi_n = normalize(doi)
    title_n = normalize(title)
    if doi_n and doi_n in doi_seeds:
        return True
    return any(seed in title_n for seed in title_seeds)


def download_priority_score(citations: int, year: int, must_include: bool, topic_gap_boost: float) -> float:
    citation_term = math.log1p(max(citations, 0)) * 10.0
    recency_term = max(0, min((year or 0) - 1990, 40)) * 0.25
    seed_boost = 120.0 if must_include else 0.0
    return citation_term + recency_term + seed_boost + topic_gap_boost


def write_csv(path: Path, rows: List[dict], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> int:
    args = parse_args()
    out_dir = Path(args.output_dir)
    doi_seeds, title_seeds = load_seed_rules(Path(args.must_include_seeds))
    reject_map = load_reject_protection(Path(args.reject_csv))
    hbe_allowlist = load_allowlist(Path(args.hbe_allowlist))
    neuro_allowlist = load_allowlist(Path(args.neuro_allowlist))

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    columns = {row[1] for row in cur.execute("PRAGMA table_info(papers)")}
    citation_column = pick_citation_column(columns)
    local_citations = fetch_local_citations(cur) if not citation_column else {}

    select_fields = [
        "paper_id",
        "doi",
        "title",
        "venue",
        "year",
        "abstract",
        "url",
        "pdf_path",
        "topic_decision",
        "triage_decision",
    ]
    if citation_column:
        select_fields.append(f"{citation_column} AS citation_count")
    cur.execute(
        f"SELECT {', '.join(select_fields)} FROM papers "
        "WHERE abstract IS NOT NULL AND abstract != ''"
    )
    papers = cur.fetchall()
    conn.close()

    reduced_rows: List[ReducedRow] = []
    no_pdf_candidates: List[DownloadPriority] = []

    topic_density = Counter()
    for p in papers:
        topic = classify_topic(p["title"] or "", p["abstract"] or "")
        topic_density[topic] += 1

    topic_gap_boosts = {}
    for topic, count in topic_density.items():
        topic_gap_boosts[topic] = max(0.0, 30.0 - min(count, 60) * 0.5)

    for p in papers:
        topic = classify_topic(p["title"] or "", p["abstract"] or "")
        citations = int(p["citation_count"] or 0) if citation_column else local_citations.get(p["paper_id"], 0)
        has_pdf = bool((p["pdf_path"] or "").strip())
        topic_decision = normalize(p["topic_decision"] or "")
        text_blob = normalize(f"{p['title'] or ''} {p['abstract'] or ''}")
        venue_norm = normalize(p["venue"] or "")
        must_include = is_must_include(p["doi"] or "", p["title"] or "", doi_seeds, title_seeds)
        high_cite = citations >= args.high_cite_threshold
        protected_reasons = reject_map.get(p["paper_id"], "")
        protected = bool(protected_reasons)
        reject_candidate = p["paper_id"] in reject_map
        non_protected_reject = reject_candidate and not protected and not high_cite and not must_include

        if non_protected_reject:
            continue

        if topic_decision == "off_topic" and not (protected or high_cite or must_include):
            continue

        reduced_rows.append(build_reduced_row(p, citations, topic))

        on_topic_like = topic_decision in {"on_topic", "possibly_off_topic"}
        content_signal_ok = has_built_env_signal(text_blob) and has_human_outcome_signal(text_blob)
        strong_offtopic = has_strong_offtopic_signal(text_blob)
        venue_protected = venue_norm in hbe_allowlist or venue_norm in neuro_allowlist
        strict_built_env = has_strict_built_env_signal(text_blob)

        if not has_pdf and (
            must_include
            or high_cite
            or (on_topic_like and content_signal_ok and not strong_offtopic and (venue_protected or strict_built_env))
        ):
            reasons = []
            if must_include:
                reasons.append("must_include_seed")
            if high_cite:
                reasons.append(f"high_citation>={args.high_cite_threshold}")
            if on_topic_like:
                reasons.append("on_topic")
            if content_signal_ok:
                reasons.append("content_signal_ok")
            if venue_protected:
                reasons.append("venue_allowlist")
            if protected:
                reasons.append("protected_reject_review")
            score = download_priority_score(
                citations,
                int(p["year"] or 0),
                must_include=must_include,
                topic_gap_boost=topic_gap_boosts.get(topic, 0.0),
            )
            no_pdf_candidates.append(
                DownloadPriority(
                    paper_id=p["paper_id"],
                    doi=p["doi"] or "",
                    title=p["title"] or "",
                    year=int(p["year"] or 0),
                    venue=p["venue"] or "",
                    topic_bucket=topic,
                    citation_count=citations,
                    priority_score=score,
                    reasons=";".join(reasons),
                    url=p["url"] or "",
                )
            )

    reduced_csv = out_dir / "abstract_reduced_tables.csv"
    write_csv(
        reduced_csv,
        [
            {
                "paper_id": r.paper_id,
                "doi": r.doi,
                "title": r.title,
                "year": r.year,
                "venue": r.venue,
                "topic_bucket": r.topic_bucket,
                "citation_count": r.citation_count,
                "environment_variable": r.environment_variable,
                "outcome_variable": r.outcome_variable,
                "effect_direction": r.effect_direction,
                "sample_n": r.sample_n,
                "confidence_tier": r.confidence_tier,
                "evidence_level": r.evidence_level,
                "provenance_tier": r.provenance_tier,
                "notes": r.notes,
                "abstract_snippet": r.abstract_snippet,
                "pdf_available": r.pdf_available,
            }
            for r in reduced_rows
        ],
        fieldnames=[
            "paper_id",
            "doi",
            "title",
            "year",
            "venue",
            "topic_bucket",
            "citation_count",
            "environment_variable",
            "outcome_variable",
            "effect_direction",
            "sample_n",
            "confidence_tier",
            "evidence_level",
            "provenance_tier",
            "notes",
            "abstract_snippet",
            "pdf_available",
        ],
    )

    grouped = defaultdict(list)
    for rec in no_pdf_candidates:
        grouped[rec.topic_bucket].append(rec)
    for topic in grouped:
        grouped[topic].sort(key=lambda r: (r.priority_score, r.citation_count, r.year), reverse=True)

    selected: List[DownloadPriority] = []
    selected_ids = set()
    for topic in sorted(grouped):
        for rec in grouped[topic][: args.per_topic_download_floor]:
            if rec.paper_id not in selected_ids:
                selected.append(rec)
                selected_ids.add(rec.paper_id)

    remaining = [r for r in no_pdf_candidates if r.paper_id not in selected_ids]
    remaining.sort(key=lambda r: (r.priority_score, r.citation_count, r.year), reverse=True)
    for rec in remaining:
        if len(selected) >= args.download_top_k:
            break
        selected.append(rec)
        selected_ids.add(rec.paper_id)

    download_csv = out_dir / "download_priority_for_pdf.csv"
    write_csv(
        download_csv,
        [
            {
                "paper_id": r.paper_id,
                "doi": r.doi,
                "title": r.title,
                "year": r.year,
                "venue": r.venue,
                "topic_bucket": r.topic_bucket,
                "citation_count": r.citation_count,
                "priority_score": f"{r.priority_score:.3f}",
                "reasons": r.reasons,
                "url": r.url,
            }
            for r in selected
        ],
        fieldnames=[
            "paper_id",
            "doi",
            "title",
            "year",
            "venue",
            "topic_bucket",
            "citation_count",
            "priority_score",
            "reasons",
            "url",
        ],
    )

    summary_path = out_dir / "abstract_reduced_tables_summary.md"
    topic_counts = Counter(r.topic_bucket for r in reduced_rows)
    lines = []
    lines.append("# Abstract Reduced Tables Summary")
    lines.append("")
    lines.append(f"- Reduced rows written: {len(reduced_rows)}")
    lines.append(f"- Download priority rows: {len(selected)}")
    lines.append(f"- Citation mode: {'global' if citation_column else 'local'}")
    if not citation_column:
        lines.append("- Citation note: global citation column not present; scores use local citation graph counts.")
    lines.append("")
    lines.append("## Topic Coverage")
    for topic, count in sorted(topic_counts.items()):
        lines.append(f"- {topic}: {count}")
    lines.append("")
    lines.append("## Important Notes")
    lines.append("- All rows are marked `abstract_only_reduced_table` and should be treated as provisional evidence.")
    lines.append("- Provenance marker: `provenance_tier=abstract_provisional`.")
    lines.append("- Use these rows for breadth and triage, not final causal calibration.")
    lines.append("- Prioritize `download_priority_for_pdf.csv` for human PDF acquisition.")
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote reduced tables: {reduced_csv} ({len(reduced_rows)} rows)")
    print(f"Wrote download priorities: {download_csv} ({len(selected)} rows)")
    print(f"Wrote summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
