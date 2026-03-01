#!/usr/bin/env python3
"""Keyword-based article type triage (NO API CALLS - FREE).

Classifies papers into article types using title/abstract keywords.
Uses same logic as paper_triage.py but works on Article Finder papers.

Usage:
    python scripts/triage_papers_keywords.py --all
    python scripts/triage_papers_keywords.py --stats
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

# Paths
AF_ROOT = Path("/Users/davidusa/REPOS/Article_Finder_v3_2_3")
AF_DB = AF_ROOT / "data" / "article_finder.db"
PDF_DIR = AF_ROOT / "data" / "pdfs"

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "triage"
OUTPUT_FILE = OUTPUT_DIR / "keyword_triage.json"


# Article type keywords and patterns
ARTICLE_TYPE_PATTERNS = {
    "meta_analysis": {
        "required": [r"meta.?analysis", r"meta.?analytic", r"pooled effect", r"forest plot"],
        "supporting": [r"k\s*=\s*\d+", r"I²", r"heterogeneity", r"effect sizes?"],
        "weight": 10,
    },
    "systematic_review": {
        "required": [r"systematic review", r"PRISMA", r"scoping review"],
        "supporting": [r"inclusion criteria", r"exclusion criteria", r"quality assessment", r"risk of bias", r"databases? searched"],
        "weight": 9,
    },
    "empirical": {
        "required": [],  # Any with statistical patterns
        "supporting": [
            r"\bn\s*=\s*\d+", r"participants?", r"subjects?", r"sample",
            r"\bp\s*[<>=]\s*\.?\d+", r"significant", r"ANOVA", r"regression",
            r"t-test", r"correlation", r"experiment", r"study\s+\d",
            r"measured", r"results? (show|indicate|reveal)", r"F\s*\(",
            r"effect size", r"cohen", r"η²",
        ],
        "weight": 5,
    },
    "narrative_review": {
        "required": [r"(literature\s+)?review", r"overview", r"state of the art"],
        "supporting": [r"synthesize", r"summarize", r"examined the literature"],
        "exclude": [r"systematic", r"meta.?analysis", r"PRISMA"],
        "weight": 4,
    },
    "theoretical": {
        "required": [r"theoretical", r"conceptual", r"framework", r"model", r"perspective", r"commentary"],
        "supporting": [r"we propose", r"we argue", r"theory of", r"mechanism"],
        "exclude": [r"\bn\s*=\s*\d+", r"participants?", r"\bp\s*<"],
        "weight": 3,
    },
    "qualitative": {
        "required": [r"qualitative", r"interview", r"ethnograph", r"phenomenolog", r"grounded theory", r"focus group"],
        "supporting": [r"themes?", r"coding", r"thematic analysis", r"participants? (said|reported|described)"],
        "weight": 4,
    },
    "methods": {
        "required": [r"protocol", r"guidelines?", r"(instrument|scale|questionnaire)\s+(development|validation)", r"methodology paper"],
        "supporting": [r"reliability", r"validity", r"psychometric"],
        "weight": 6,
    },
}

# Domain keywords
DOMAIN_KEYWORDS = {
    "A1_Materials": ["material", "wood", "concrete", "stone", "texture", "surface", "biophilic material"],
    "A2_Spatial_Scale": ["ceiling", "height", "volume", "proportion", "scale", "spacious", "room size", "spatial"],
    "A3_Spatial_Config": ["layout", "wayfinding", "navigation", "circulation", "space syntax", "configuration"],
    "A4_Light": ["light", "daylight", "illuminance", "lux", "lighting", "circadian", "window", "glare"],
    "A5_Acoustic": ["noise", "acoustic", "sound", "reverberation", "soundscape", "auditory", "dB"],
    "A6_Visual_Form": ["color", "colour", "visual", "pattern", "fractal", "curvature", "aesthetic", "view"],
    "A7_Haptic_Thermal": ["thermal", "temperature", "comfort", "haptic", "touch", "HVAC", "ventilation"],
    "A8_Social": ["social", "privacy", "collaboration", "interaction", "open plan", "workspace", "density"],
    "A9_Task_Cognition": ["cognitive", "attention", "memory", "creativity", "performance", "productivity", "focus"],
    "A10_Temporal": ["temporal", "time", "duration", "exposure", "circadian", "seasonal", "dynamic"],
}


@dataclass
class TriageResult:
    doi: str
    title: str | None
    article_type: str
    subtype: str | None
    confidence: float
    domains: list[str]
    signals: list[str]
    has_pdf: bool


def classify_text(text: str) -> tuple[str, str | None, float, list[str]]:
    """Classify text into article type."""
    if not text:
        return "unknown", None, 0.0, []

    text_lower = text.lower()
    scores = {}
    all_signals = {}

    for article_type, patterns in ARTICLE_TYPE_PATTERNS.items():
        score = 0
        signals = []

        # Check exclusions first
        if "exclude" in patterns:
            excluded = any(re.search(p, text_lower) for p in patterns["exclude"])
            if excluded:
                continue

        # Check required patterns
        if patterns["required"]:
            required_matches = sum(1 for p in patterns["required"] if re.search(p, text_lower))
            if required_matches > 0:
                score += required_matches * 2
                signals.extend([p for p in patterns["required"] if re.search(p, text_lower)])

        # Check supporting patterns
        supporting_matches = sum(1 for p in patterns["supporting"] if re.search(p, text_lower))
        score += supporting_matches

        # Apply weight
        score *= patterns["weight"]

        if score > 0:
            scores[article_type] = score
            all_signals[article_type] = signals + [p for p in patterns["supporting"] if re.search(p, text_lower)]

    if not scores:
        return "unknown", None, 0.0, []

    # Get best match
    best_type = max(scores, key=scores.get)
    best_score = scores[best_type]

    # Normalize confidence (0-1)
    max_possible = 20  # Rough max score
    confidence = min(1.0, best_score / max_possible)

    # Determine subtype
    subtype = None
    if best_type == "empirical":
        if re.search(r"experiment", text_lower):
            subtype = "experiment"
        elif re.search(r"survey", text_lower):
            subtype = "survey"
        elif re.search(r"field study", text_lower):
            subtype = "field_study"
        elif re.search(r"observational", text_lower):
            subtype = "observational"

    return best_type, subtype, round(confidence, 2), all_signals.get(best_type, [])[:5]


def detect_domains(text: str) -> list[str]:
    """Detect relevant CNFA domains from text."""
    if not text:
        return []

    text_lower = text.lower()
    domains = []

    for domain, keywords in DOMAIN_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                domains.append(domain)
                break

    return domains


def triage_all_papers() -> list[TriageResult]:
    """Triage all papers in Article Finder database."""
    results = []

    # Get papers with PDFs
    pdf_files = {f.stem.replace("_", "/"): f for f in PDF_DIR.glob("*.pdf")}

    conn = sqlite3.connect(AF_DB)
    conn.row_factory = sqlite3.Row

    cursor = conn.execute("""
        SELECT doi, title, abstract, pdf_path
        FROM papers
        WHERE doi IS NOT NULL
    """)

    for row in cursor:
        doi = row["doi"]
        title = row["title"] or ""
        abstract = row["abstract"] or ""
        text = f"{title} {abstract}"

        has_pdf = doi in pdf_files or (row["pdf_path"] and Path(row["pdf_path"]).exists())

        article_type, subtype, confidence, signals = classify_text(text)
        domains = detect_domains(text)

        results.append(TriageResult(
            doi=doi,
            title=title[:100] if title else None,
            article_type=article_type,
            subtype=subtype,
            confidence=confidence,
            domains=domains,
            signals=signals,
            has_pdf=has_pdf,
        ))

    conn.close()

    # Also add PDFs not in database
    db_dois = {r.doi for r in results}
    for doi, pdf_path in pdf_files.items():
        if doi not in db_dois:
            results.append(TriageResult(
                doi=doi,
                title=None,
                article_type="unknown",
                subtype=None,
                confidence=0.0,
                domains=[],
                signals=[],
                has_pdf=True,
            ))

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="Triage all papers")
    parser.add_argument("--stats", action="store_true", help="Show stats only")
    args = parser.parse_args()

    if args.stats and OUTPUT_FILE.exists():
        with open(OUTPUT_FILE) as f:
            data = json.load(f)
        print(f"Total papers: {len(data['papers'])}")
        print(f"\nBy article type:")
        for t, count in sorted(data["summary"]["by_type"].items(), key=lambda x: -x[1]):
            print(f"  {t}: {count}")
        print(f"\nWith PDF: {data['summary']['with_pdf']}")
        print(f"High confidence (≥0.5): {data['summary']['high_confidence']}")
        return

    if not args.all:
        parser.print_help()
        return

    print("Triaging papers using keyword patterns...")
    results = triage_all_papers()

    # Build summary
    by_type = Counter(r.article_type for r in results)
    with_pdf = sum(1 for r in results if r.has_pdf)
    high_confidence = sum(1 for r in results if r.confidence >= 0.5)

    # Group by type for extraction queue
    extraction_queue = {
        "empirical": [],
        "meta_analysis": [],
        "systematic_review": [],
        "narrative_review": [],
        "theoretical": [],
        "qualitative": [],
        "methods": [],
        "unknown": [],
    }

    for r in results:
        if r.has_pdf:
            extraction_queue[r.article_type].append(r.doi)

    # Save results
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_data = {
        "papers": [
            {
                "doi": r.doi,
                "title": r.title,
                "article_type": r.article_type,
                "subtype": r.subtype,
                "confidence": r.confidence,
                "domains": r.domains,
                "signals": r.signals,
                "has_pdf": r.has_pdf,
            }
            for r in results
        ],
        "summary": {
            "total": len(results),
            "by_type": dict(by_type),
            "with_pdf": with_pdf,
            "high_confidence": high_confidence,
        },
        "extraction_queue": {k: v for k, v in extraction_queue.items() if v},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output_data, f, indent=2)

    # Print summary
    print(f"\n{'='*60}")
    print("KEYWORD TRIAGE SUMMARY (FREE - NO API CALLS)")
    print(f"{'='*60}")
    print(f"Total papers: {len(results)}")
    print(f"With PDFs: {with_pdf}")
    print(f"High confidence: {high_confidence}")
    print(f"\nBy article type:")
    for t, count in sorted(by_type.items(), key=lambda x: -x[1]):
        pdf_count = len(extraction_queue.get(t, []))
        print(f"  {t}: {count} ({pdf_count} with PDF)")

    print(f"\nExtraction queue sizes:")
    for t, dois in sorted(extraction_queue.items(), key=lambda x: -len(x[1])):
        print(f"  {t}: {len(dois)} papers ready")

    print(f"\nSaved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
