#!/usr/bin/env python3
"""
SCHOLAR QUERY EXPANDER
======================

Uses template mechanism terms and molecule descriptions to generate
targeted search queries, then discovers papers not in our corpus via:
1. Semantic Scholar API (free, has abstract + citations + TLDR)
2. CrossRef text search (free, broadest coverage)
3. OpenAlex search (free, newer alternative to Microsoft Academic)

Discovered DOIs are scored by topic relevance (same vocabulary as
snowball_expand_corpus.py) and output as expansion candidates.

Usage:
    python scripts/scholar_query_expander.py --scan           # Generate queries & search
    python scripts/scholar_query_expander.py --status         # Show results
    python scripts/scholar_query_expander.py --export         # Export new DOIs for snowball

Author: AG (Pipeline Sprint)
Date: 2026-02-25
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# ── Paths ──
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
EXTRACTIONS_DIR = DATA_DIR / "extractions"
TEMPLATES_DIR = DATA_DIR / "templates"
MOLECULES_DIR = DATA_DIR / "molecules"
RESULTS_FILE = EXTRACTIONS_DIR / "scholar_expansion_candidates.json"
QUERY_LOG_FILE = EXTRACTIONS_DIR / "scholar_query_log.json"

# ── API Endpoints ──
S2_SEARCH_API = "https://api.semanticscholar.org/graph/v1/paper/search"
CROSSREF_WORKS_API = "https://api.crossref.org/works"
OPENALEX_WORKS_API = "https://api.openalex.org/works"
EMAIL = "dkirsh@gmail.com"  # Polite pool

# ── Rate limits ──
S2_DELAY = 1.0       # S2 allows 100/5min for unauthenticated
CROSSREF_DELAY = 0.5
OPENALEX_DELAY = 0.3

# ── Domain vocabulary (shared with snowball) ──
DOMAIN_KEYWORDS = {
    # Tier 1: Core domain (weight 3)
    "architecture": 3, "built environment": 3, "indoor environment": 3,
    "building design": 3, "environmental psychology": 3,
    "neuroarchitecture": 3, "biophilic": 3, "biophilia": 3,
    "prospect refuge": 3, "restorative environment": 3,
    # Tier 2: Mechanism-level (weight 2)
    "prediction error": 2, "fractal": 2, "complexity": 2,
    "attention restoration": 2, "stress recovery": 2,
    "thermal comfort": 2, "acoustic": 2, "soundscape": 2,
    "circadian": 2, "melanopic": 2, "daylight": 2,
    "wayfinding": 2, "spatial cognition": 2, "isovist": 2,
    "affordance": 2, "embodied cognition": 2,
    "wellbeing": 2, "well-being": 2, "mood": 2,
    "arousal": 2, "valence": 2,
    "eeg": 2, "fmri": 2, "neuroimaging": 2,
    "haptic": 2, "tactile": 2, "olfactory": 2,
    # Tier 3: Broader context (weight 1)
    "perception": 1, "sensation": 1, "attention": 1,
    "memory": 1, "learning": 1, "creativity": 1, "productivity": 1,
    "cortisol": 1, "autonomic": 1, "heart rate variability": 1,
    "noise": 1, "reverb": 1, "music": 1,
    "nature": 1, "green": 1, "plants": 1, "vegetation": 1,
    "window": 1, "view": 1, "light": 1,
    "material": 1, "texture": 1, "surface": 1, "wood": 1,
    "privacy": 1, "density": 1, "crowding": 1,
}


def load_existing_dois() -> set:
    """Load DOIs already in our corpus."""
    existing = set()
    if EXTRACTIONS_DIR.exists():
        for fpath in EXTRACTIONS_DIR.glob("10.*.json"):
            doi = fpath.stem.replace("_", "/", 1)
            existing.add(doi.lower())
    return existing


def generate_queries() -> list[dict]:
    """Generate search queries from templates and molecules."""
    queries = []

    # From molecules — use name + short_description
    if MOLECULES_DIR.exists():
        for fpath in sorted(MOLECULES_DIR.glob("*.json")):
            try:
                data = json.loads(fpath.read_text())
                name = data.get("name", "")
                desc = data.get("short_description", "")
                mid = data.get("molecule_id", fpath.stem)

                # Generate 2-3 queries per molecule
                if name:
                    queries.append({
                        "query": f"{name} architecture neuroscience",
                        "source": f"molecule:{mid}",
                        "priority": "high",
                    })
                if desc and len(desc) > 20:
                    # Extract key terms from description
                    terms = desc.split()[:6]
                    queries.append({
                        "query": " ".join(terms) + " built environment",
                        "source": f"molecule:{mid}",
                        "priority": "medium",
                    })
            except Exception as e:
                import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")

    # From templates — use mechanism_chain terms
    if TEMPLATES_DIR.exists():
        seen_queries = set()
        for fpath in sorted(TEMPLATES_DIR.glob("*.json")):
            try:
                data = json.loads(fpath.read_text())
                tid = data.get("display_id", data.get("template_id", fpath.stem))
                chain = data.get("mechanism_chain", [])
                name = data.get("name", "")

                if chain and len(chain) >= 2:
                    # Use first two steps of mechanism chain as query
                    step1 = str(chain[0])[:40]
                    step2 = str(chain[1])[:40]
                    q = f"{step1} {step2}"
                    if q not in seen_queries:
                        seen_queries.add(q)
                        queries.append({
                            "query": q,
                            "source": f"template:{tid}",
                            "priority": "medium",
                        })

                # Also search by template name
                if name and name not in seen_queries:
                    seen_queries.add(name)
                    queries.append({
                        "query": f"{name} neural mechanism",
                        "source": f"template:{tid}",
                        "priority": "low",
                    })
            except Exception as e:
                import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")

    print(f"Generated {len(queries)} queries from molecules and templates")
    return queries


def score_relevance(title: str, abstract: str = "") -> float:
    """Score topic relevance based on domain vocabulary match."""
    text = (title + " " + abstract).lower()
    score = 0
    matches = 0
    for keyword, weight in DOMAIN_KEYWORDS.items():
        if keyword in text:
            score += weight
            matches += 1
    # Normalize: max theoretical score ~100, normalize to 0-1
    normalized = min(score / 20.0, 1.0) if score > 0 else 0.0
    return normalized


def search_semantic_scholar(query: str, limit: int = 10) -> list[dict]:
    """Search Semantic Scholar API."""
    results = []
    try:
        params = urllib.parse.urlencode({
            "query": query,
            "limit": limit,
            "fields": "externalIds,title,abstract,year,citationCount,tldr",
        })
        url = f"{S2_SEARCH_API}?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "ArticleEater/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            for paper in data.get("data", []):
                doi = None
                ext_ids = paper.get("externalIds", {})
                if ext_ids:
                    doi = ext_ids.get("DOI")
                if doi:
                    tldr = paper.get("tldr", {})
                    results.append({
                        "doi": doi,
                        "title": paper.get("title", ""),
                        "abstract": paper.get("abstract", ""),
                        "year": paper.get("year"),
                        "citation_count": paper.get("citationCount"),
                        "tldr": tldr.get("text") if tldr else "",
                        "source": "semantic_scholar",
                    })
    except Exception as e:
        print(f"  S2 error for '{query[:40]}': {e}")
    return results


def search_crossref(query: str, limit: int = 10) -> list[dict]:
    """Search CrossRef text search API."""
    results = []
    try:
        params = urllib.parse.urlencode({
            "query": query,
            "rows": limit,
            "mailto": EMAIL,
            "select": "DOI,title,abstract,published-print,is-referenced-by-count",
        })
        url = f"{CROSSREF_WORKS_API}?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": f"ArticleEater/1.0 (mailto:{EMAIL})"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            for item in data.get("message", {}).get("items", []):
                doi = item.get("DOI", "")
                title = item.get("title", [""])[0] if isinstance(item.get("title"), list) else str(item.get("title", ""))
                abstract = item.get("abstract", "")
                # Clean abstract HTML tags
                import re
                abstract = re.sub(r"<[^>]+>", " ", abstract) if abstract else ""
                year = None
                pub = item.get("published-print") or item.get("published-online")
                if pub and pub.get("date-parts"):
                    year = pub["date-parts"][0][0] if pub["date-parts"][0] else None

                if doi:
                    results.append({
                        "doi": doi,
                        "title": title,
                        "abstract": abstract[:500],
                        "year": year,
                        "citation_count": item.get("is-referenced-by-count"),
                        "source": "crossref",
                    })
    except Exception as e:
        print(f"  CrossRef error for '{query[:40]}': {e}")
    return results


def search_openalex(query: str, limit: int = 10) -> list[dict]:
    """Search OpenAlex API (free, no auth needed)."""
    results = []
    try:
        params = urllib.parse.urlencode({
            "search": query,
            "per_page": limit,
            "mailto": EMAIL,
        })
        url = f"{OPENALEX_WORKS_API}?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": f"ArticleEater/1.0 (mailto:{EMAIL})"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            for work in data.get("results", []):
                doi = work.get("doi", "")
                if doi and doi.startswith("https://doi.org/"):
                    doi = doi.replace("https://doi.org/", "")

                if doi:
                    results.append({
                        "doi": doi,
                        "title": work.get("title", ""),
                        "abstract": "",  # OpenAlex has inverted abstract, skip for now
                        "year": work.get("publication_year"),
                        "citation_count": work.get("cited_by_count"),
                        "source": "openalex",
                        "oa_url": work.get("open_access", {}).get("oa_url"),
                    })
    except Exception as e:
        print(f"  OpenAlex error for '{query[:40]}': {e}")
    return results


def run_scan(max_queries: int = 50, results_per_query: int = 10):
    """Run the full scan: generate queries, search all three APIs."""
    existing_dois = load_existing_dois()
    print(f"Existing corpus: {len(existing_dois)} DOIs")

    queries = generate_queries()
    # Prioritize: high > medium > low, take top N
    priority_order = {"high": 0, "medium": 1, "low": 2}
    queries.sort(key=lambda q: priority_order.get(q.get("priority", "low"), 2))
    queries = queries[:max_queries]
    print(f"Running {len(queries)} queries (capped at {max_queries})")

    all_candidates = {}  # DOI -> metadata
    query_log = []

    for i, qobj in enumerate(queries):
        query = qobj["query"]
        source = qobj["source"]
        print(f"\n[{i+1}/{len(queries)}] '{query[:50]}' (from {source})")

        found = 0

        # Search Semantic Scholar
        s2_results = search_semantic_scholar(query, results_per_query)
        time.sleep(S2_DELAY)

        for r in s2_results:
            doi_lower = r["doi"].lower()
            if doi_lower not in existing_dois and doi_lower not in all_candidates:
                relevance = score_relevance(r.get("title", ""), r.get("abstract", ""))
                r["relevance_score"] = relevance
                r["discovered_via"] = source
                r["query"] = query
                all_candidates[doi_lower] = r
                found += 1

        # Search CrossRef (alternate with S2 to spread load)
        if i % 2 == 0:
            cr_results = search_crossref(query, results_per_query)
            time.sleep(CROSSREF_DELAY)
            for r in cr_results:
                doi_lower = r["doi"].lower()
                if doi_lower not in existing_dois and doi_lower not in all_candidates:
                    relevance = score_relevance(r.get("title", ""), r.get("abstract", ""))
                    r["relevance_score"] = relevance
                    r["discovered_via"] = source
                    r["query"] = query
                    all_candidates[doi_lower] = r
                    found += 1

        # Search OpenAlex (every 3rd query)
        if i % 3 == 0:
            oa_results = search_openalex(query, results_per_query)
            time.sleep(OPENALEX_DELAY)
            for r in oa_results:
                doi_lower = r["doi"].lower()
                if doi_lower not in existing_dois and doi_lower not in all_candidates:
                    relevance = score_relevance(r.get("title", ""), r.get("abstract", ""))
                    r["relevance_score"] = relevance
                    r["discovered_via"] = source
                    r["query"] = query
                    all_candidates[doi_lower] = r
                    found += 1

        query_log.append({
            "query": query,
            "source": source,
            "new_found": found,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        print(f"  → {found} new candidates")

    # Sort by relevance and save
    sorted_candidates = sorted(
        all_candidates.values(),
        key=lambda x: (x.get("relevance_score", 0), x.get("citation_count") or 0),
        reverse=True,
    )

    results = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "queries_run": len(queries),
        "total_new_candidates": len(sorted_candidates),
        "high_relevance": sum(1 for c in sorted_candidates if c.get("relevance_score", 0) >= 0.3),
        "candidates": sorted_candidates,
    }

    RESULTS_FILE.write_text(json.dumps(results, indent=2, default=str))
    QUERY_LOG_FILE.write_text(json.dumps(query_log, indent=2))

    print(f"\n{'='*50}")
    print(f"RESULTS: {len(sorted_candidates)} new candidates found")
    print(f"  High relevance (≥0.3): {results['high_relevance']}")
    print(f"  Saved to: {RESULTS_FILE}")

    # Show top 10
    print(f"\nTOP 10:")
    for c in sorted_candidates[:10]:
        print(f"  [{c.get('relevance_score', 0):.2f}] {c.get('title', '')[:60]}")
        print(f"       DOI: {c['doi']} | Cited: {c.get('citation_count', '?')} | Via: {c.get('source')}")


def show_status():
    """Show current expansion status."""
    if not RESULTS_FILE.exists():
        print("No scholar expansion results yet. Run with --scan first.")
        return

    data = json.loads(RESULTS_FILE.read_text())
    print(f"\n═══ SCHOLAR EXPANSION STATUS ═══\n")
    print(f"Last scan: {data.get('generated_at', '?')}")
    print(f"Queries run: {data.get('queries_run', 0)}")
    print(f"Total new candidates: {data.get('total_new_candidates', 0)}")
    print(f"High relevance: {data.get('high_relevance', 0)}")

    candidates = data.get("candidates", [])
    if candidates:
        print(f"\nTOP 15:")
        for c in candidates[:15]:
            print(f"  [{c.get('relevance_score', 0):.2f}] {c.get('title', '')[:60]}")
            print(f"       DOI: {c['doi']} | Cited: {c.get('citation_count', '?')}")

    # Show source breakdown
    from collections import Counter
    sources = Counter(c.get("source", "?") for c in candidates)
    print(f"\nSource breakdown: {dict(sources)}")

    via = Counter(c.get("discovered_via", "?") for c in candidates)
    print(f"Discovered via: {dict(via)}")


def export_for_snowball():
    """Export discovered DOIs in format compatible with snowball pipeline."""
    if not RESULTS_FILE.exists():
        print("No results to export. Run --scan first.")
        return

    data = json.loads(RESULTS_FILE.read_text())
    candidates = data.get("candidates", [])

    # Filter to high-relevance only
    high_rel = [c for c in candidates if c.get("relevance_score", 0) >= 0.3]
    print(f"Exporting {len(high_rel)} high-relevance candidates for snowball pipeline")

    # Format as snowball candidates
    snowball_format = []
    for c in high_rel:
        snowball_format.append({
            "doi": c["doi"],
            "title": c.get("title", ""),
            "year": c.get("year"),
            "citation_count": c.get("citation_count"),
            "relevance_score": c.get("relevance_score", 0),
            "source": f"scholar_expander:{c.get('source', '?')}",
            "abstract": c.get("abstract", "")[:300],
            "tldr": c.get("tldr", ""),
        })

    out_path = EXTRACTIONS_DIR / "scholar_expansion_for_snowball.json"
    out_path.write_text(json.dumps(snowball_format, indent=2, default=str))
    print(f"Saved to: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Scholar-based corpus expansion")
    parser.add_argument("--scan", action="store_true",
                       help="Generate queries from templates/molecules and search APIs")
    parser.add_argument("--status", action="store_true",
                       help="Show current expansion results")
    parser.add_argument("--export", action="store_true",
                       help="Export high-relevance DOIs for snowball pipeline")
    parser.add_argument("--max-queries", type=int, default=50,
                       help="Max queries to run (default: 50)")
    parser.add_argument("--results-per-query", type=int, default=10,
                       help="Results per query per API (default: 10)")
    args = parser.parse_args()

    if args.status:
        show_status()
    elif args.export:
        export_for_snowball()
    elif args.scan:
        run_scan(max_queries=args.max_queries, results_per_query=args.results_per_query)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
