#!/usr/bin/env python3
"""
SNOWBALL CORPUS EXPANSION
=========================

Uses the CrossRef + S2 citation graph to find papers that are highly cited
by our existing corpus but not yet included. Filters by topic relevance,
resolves metadata, and generates a ranked acquisition list.

Strategy:
  1. Load snowball_expansion_candidates.json (DOIs cited by 2+ corpus papers)
  2. Fetch CrossRef metadata for top candidates (title, year, journal, abstract)
  3. Score topic relevance via keyword matching against our domain vocabulary
  4. Produce a ranked acquisition list with actionable download URLs
  5. For candidates with open access PDFs (via Unpaywall), optionally download

USAGE:
    python scripts/snowball_expand_corpus.py                     # Full pipeline
    python scripts/snowball_expand_corpus.py --status            # Show expansion stats
    python scripts/snowball_expand_corpus.py --min-citations 3   # Only 3+ co-cited
    python scripts/snowball_expand_corpus.py --fetch-metadata    # Step 1: resolve metadata
    python scripts/snowball_expand_corpus.py --score-relevance   # Step 2: topic scoring
    python scripts/snowball_expand_corpus.py --find-pdfs         # Step 3: find OA PDFs
    python scripts/snowball_expand_corpus.py --download-top N    # Step 4: download top N PDFs

Author: AG (Pipeline Sprint)
Date: 2026-02-25
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from collections import Counter

# ── Paths ──
PROJECT_ROOT = Path(__file__).parent.parent
EXTRACTIONS_DIR = PROJECT_ROOT / "data" / "extractions"
CANDIDATES_FILE = EXTRACTIONS_DIR / "snowball_expansion_candidates.json"
METADATA_CACHE = EXTRACTIONS_DIR / "snowball_metadata_cache.json"
SCORED_FILE = EXTRACTIONS_DIR / "snowball_scored.json"
PDF_DOWNLOAD_DIR = PROJECT_ROOT / "data" / "pdfs_snowball"

# CrossRef config
CROSSREF_API = "https://api.crossref.org/works"
UNPAYWALL_API = "https://api.unpaywall.org/v2"
EMAIL = "dkirsh@gmail.com"  # Polite pool

# ── Domain vocabulary for topic relevance scoring ──
# These keywords define what's relevant to the Article Eater BN/Web domain
DOMAIN_KEYWORDS = {
    # Tier 1: Core domain (weight 3)
    "architecture": 3, "built environment": 3, "indoor environment": 3,
    "building design": 3, "environmental psychology": 3,
    "neuroarchitecture": 3, "biophilic": 3, "biophilia": 3,
    "thermal comfort": 3, "acoustic": 3, "daylighting": 3,
    "lighting design": 3, "interior design": 3, "workspace design": 3,
    "office design": 3, "classroom design": 3, "hospital design": 3,
    "healing environment": 3, "restorative environment": 3,
    "wayfinding": 3, "spatial navigation": 3,

    # Tier 2: Related neuroscience and psychology (weight 2)
    "multisensory": 2, "crossmodal": 2, "cross-modal": 2,
    "embodied cognition": 2, "affordance": 2, "peripersonal space": 2,
    "place attachment": 2, "sense of place": 2,
    "circadian": 2, "melatonin": 2, "cortisol": 2,
    "stress recovery": 2, "attention restoration": 2,
    "prospect and refuge": 2, "savanna hypothesis": 2,
    "environmental stress": 2, "noise": 2, "soundscape": 2,
    "visual complexity": 2, "fractal": 2, "aesthetic": 2,
    "nature exposure": 2, "green space": 2, "urban green": 2,
    "occupant": 2, "post-occupancy": 2,
    "cognitive performance": 2, "task performance": 2,
    "wellbeing": 2, "well-being": 2, "mood": 2,
    "arousal": 2, "valence": 2,
    "eeg": 2, "fmri": 2, "neuroimaging": 2,
    "haptic": 2, "tactile": 2, "olfactory": 2,
    "color temperature": 2, "colour temperature": 2,
    "illuminance": 2, "luminance": 2,

    # Tier 3: Broader context (weight 1)
    "perception": 1, "sensation": 1, "attention": 1,
    "memory": 1, "learning": 1, "creativity": 1, "productivity": 1,
    "physiological": 1, "heart rate": 1, "skin conductance": 1,
    "virtual reality": 1, "immersive": 1,
    "survey": 1, "questionnaire": 1,
    "comfort": 1, "discomfort": 1, "satisfaction": 1,
    "preference": 1, "rating": 1,
    "indoor air": 1, "ventilation": 1, "humidity": 1,
    "window": 1, "view": 1, "outlook": 1,
    "urban": 1, "pedestrian": 1, "street": 1,
    "material": 1, "texture": 1, "surface": 1, "wood": 1,
    "crowding": 1, "density": 1, "privacy": 1, "territory": 1,
}


def fetch_crossref_metadata(doi: str) -> Optional[dict]:
    """Fetch metadata from CrossRef for a single DOI."""
    encoded = urllib.parse.quote(doi, safe="")
    url = f"{CROSSREF_API}/{encoded}"
    headers = {
        "User-Agent": f"ArticleEater/2.0 (mailto:{EMAIL})",
        "Accept": "application/json",
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        msg = data.get("message", {})

        # Parse
        titles = msg.get("title", [])
        title = titles[0] if titles else None

        authors = []
        for a in msg.get("author", []):
            parts = []
            if a.get("given"): parts.append(a["given"])
            if a.get("family"): parts.append(a["family"])
            authors.append(" ".join(parts) if parts else "Unknown")

        year = None
        for df in ["published-print", "published-online", "published", "created"]:
            dp = msg.get(df, {}).get("date-parts", [[]])
            if dp and dp[0]:
                year = dp[0][0]
                break

        containers = msg.get("container-title", [])
        journal = containers[0] if containers else None

        abstract = msg.get("abstract", "")
        if abstract:
            abstract = re.sub(r"<[^>]+>", "", abstract).strip()

        return {
            "doi": msg.get("DOI", doi),
            "title": title,
            "authors": authors[:5],  # First 5 authors
            "year": year,
            "journal": journal,
            "type": msg.get("type"),
            "citation_count": msg.get("is-referenced-by-count", 0),
            "abstract": abstract,
            "subjects": msg.get("subject", []),
            "publisher": msg.get("publisher"),
            "url": msg.get("URL"),
        }
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"doi": doi, "_error": "not_found"}
        return {"doi": doi, "_error": f"http_{e.code}"}
    except Exception as e:
        return {"doi": doi, "_error": str(e)[:80]}


def score_relevance(metadata: dict) -> float:
    """
    Score topic relevance based on domain vocabulary match.

    Checks title, abstract, journal, and subjects against weighted keywords.
    Returns a score from 0.0 to 1.0.
    """
    if metadata.get("_error"):
        return 0.0

    # Build searchable text
    text_parts = []
    if metadata.get("title"):
        text_parts.append(metadata["title"])
    if metadata.get("abstract"):
        text_parts.append(metadata["abstract"])
    if metadata.get("journal"):
        text_parts.append(metadata["journal"])
    for subj in metadata.get("subjects", []):
        text_parts.append(subj)

    text = " ".join(text_parts).lower()

    if not text.strip():
        return 0.0

    # Score against domain keywords
    total_weight = 0
    matched_keywords = []

    for keyword, weight in DOMAIN_KEYWORDS.items():
        if keyword.lower() in text:
            total_weight += weight
            matched_keywords.append((keyword, weight))

    # Normalize: max possible ~20 for a highly relevant paper
    score = min(1.0, total_weight / 12.0)

    return round(score, 3)


def fetch_metadata_batch(candidates: list[dict], cache: dict) -> dict:
    """Fetch CrossRef metadata for expansion candidates, with caching."""
    fetched = 0
    cached_count = 0
    errors = 0

    for i, cand in enumerate(candidates, 1):
        doi = cand["doi"]

        if doi in cache and not cache[doi].get("_error"):
            cached_count += 1
            continue

        meta = fetch_crossref_metadata(doi)
        if meta:
            meta["cited_by_corpus_count"] = cand["cited_by_count"]
            cache[doi] = meta
            if meta.get("_error"):
                errors += 1
            else:
                fetched += 1
        else:
            errors += 1

        if i % 100 == 0:
            print(f"  [{i}/{len(candidates)}] Fetched: {fetched} | Cached: {cached_count} | Errors: {errors}")

        time.sleep(0.05)

    print(f"\nMetadata fetch: {fetched} new, {cached_count} cached, {errors} errors")
    return cache


def check_unpaywall(doi: str) -> Optional[str]:
    """Check Unpaywall for open access PDF URL."""
    encoded = urllib.parse.quote(doi, safe="")
    url = f"{UNPAYWALL_API}/{encoded}?email={EMAIL}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        # Check for OA PDF
        best = data.get("best_oa_location")
        if best and best.get("url_for_pdf"):
            return best["url_for_pdf"]
        if best and best.get("url"):
            return best["url"]

        # Check all locations
        for loc in data.get("oa_locations", []):
            if loc.get("url_for_pdf"):
                return loc["url_for_pdf"]

        return None
    except Exception:
        return None


def download_pdf(url: str, dest: Path) -> bool:
    """Download a PDF to disk."""
    try:
        headers = {"User-Agent": "ArticleEater/2.0 (mailto:dkirsh@gmail.com)"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=60) as resp:
            content = resp.read()
            if len(content) < 1000:
                return False  # Too small, probably an error page
            dest.write_bytes(content)
            return True
    except Exception:
        return False


def run_full_pipeline(min_citations: int = 3, download_top: int = 0):
    """Run the full snowball expansion pipeline."""
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║  SNOWBALL CORPUS EXPANSION                                  ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    # Load candidates
    if not CANDIDATES_FILE.exists():
        print("No candidates file. Run enrich_crossref.py first.")
        return

    candidates_data = json.loads(CANDIDATES_FILE.read_text())
    all_candidates = candidates_data.get("candidates", [])
    print(f"\nTotal expansion candidates: {len(all_candidates)}")

    # Filter by minimum corpus co-citations
    candidates = [c for c in all_candidates if c["cited_by_count"] >= min_citations]
    print(f"After filtering (≥{min_citations} co-citations): {len(candidates)}")

    # Step 1: Fetch metadata
    print(f"\n── Step 1: Fetching CrossRef metadata ──")
    cache = {}
    if METADATA_CACHE.exists():
        cache = json.loads(METADATA_CACHE.read_text())
        print(f"Loaded {len(cache)} cached entries")

    cache = fetch_metadata_batch(candidates, cache)
    METADATA_CACHE.write_text(json.dumps(cache, indent=2))
    print(f"Saved metadata cache: {METADATA_CACHE}")

    # Step 2: Score topic relevance
    print(f"\n── Step 2: Scoring topic relevance ──")
    scored = []

    for cand in candidates:
        doi = cand["doi"]
        meta = cache.get(doi, {})
        if meta.get("_error"):
            continue

        relevance = score_relevance(meta)
        scored.append({
            "doi": doi,
            "title": meta.get("title", "?"),
            "year": meta.get("year"),
            "journal": meta.get("journal"),
            "authors": meta.get("authors", [])[:3],
            "citation_count": meta.get("citation_count", 0),
            "cited_by_corpus": cand["cited_by_count"],
            "relevance_score": relevance,
            # Combined score: co-citation × relevance
            "expansion_score": round(cand["cited_by_count"] * (0.3 + 0.7 * relevance), 2),
            "abstract": (meta.get("abstract") or "")[:200],
            "type": meta.get("type"),
            "url": meta.get("url"),
        })

    # Sort by expansion_score (co-citation × relevance)
    scored.sort(key=lambda x: -x["expansion_score"])

    # Save
    scored_output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "min_citations": min_citations,
        "total_scored": len(scored),
        "high_relevance": sum(1 for s in scored if s["relevance_score"] >= 0.5),
        "candidates": scored,
    }
    SCORED_FILE.write_text(json.dumps(scored_output, indent=2))

    # Stats
    high_rel = [s for s in scored if s["relevance_score"] >= 0.5]
    med_rel = [s for s in scored if 0.2 <= s["relevance_score"] < 0.5]
    low_rel = [s for s in scored if s["relevance_score"] < 0.2]

    print(f"\nRelevance distribution:")
    print(f"  High (≥0.5):  {len(high_rel)} papers")
    print(f"  Medium:       {len(med_rel)} papers")
    print(f"  Low (<0.2):   {len(low_rel)} papers")

    print(f"\nTop 20 expansion candidates (by expansion_score):")
    print(f"{'Score':>6s}  {'CC':>3s}  {'Rel':>4s}  {'Year':>5s}  {'GCite':>6s}  Title")
    print(f"{'─'*6}  {'─'*3}  {'─'*4}  {'─'*5}  {'─'*6}  {'─'*50}")
    for s in scored[:20]:
        title = (s["title"] or "?")[:50]
        print(f"{s['expansion_score']:6.1f}  {s['cited_by_corpus']:3d}  {s['relevance_score']:.2f}  "
              f"{s.get('year', '?'):>5}  {s.get('citation_count', 0):6d}  {title}")

    # Step 3: Find OA PDFs for top candidates (if requested)
    if download_top > 0:
        print(f"\n── Step 3: Finding open access PDFs for top {download_top} ──")
        PDF_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

        downloaded = 0
        oa_urls = 0
        top_scored = [s for s in scored if s["relevance_score"] >= 0.3][:download_top]

        for i, s in enumerate(top_scored, 1):
            doi = s["doi"]
            doi_safe = doi.replace("/", "_")
            pdf_dest = PDF_DOWNLOAD_DIR / f"{doi_safe}.pdf"

            if pdf_dest.exists():
                downloaded += 1
                continue

            print(f"  [{i}/{len(top_scored)}] {s['title'][:45]}...", end=" ", flush=True)
            pdf_url = check_unpaywall(doi)

            if pdf_url:
                oa_urls += 1
                if download_pdf(pdf_url, pdf_dest):
                    downloaded += 1
                    print(f"✓ downloaded")
                else:
                    print(f"⚠ URL found but download failed")
            else:
                print(f"✗ no OA PDF")

            time.sleep(0.2)

        print(f"\n  OA URLs found: {oa_urls}")
        print(f"  PDFs downloaded: {downloaded}")
        print(f"  Location: {PDF_DOWNLOAD_DIR}")

    # Summary
    print(f"\n{'═'*60}")
    print(f"SNOWBALL EXPANSION SUMMARY")
    print(f"{'═'*60}")
    print(f"Candidates scored:      {len(scored)}")
    print(f"High relevance (≥0.5):  {len(high_rel)}")
    print(f"Ready for acquisition:  {len([s for s in scored if s['relevance_score'] >= 0.3])}")
    print(f"\nOutput: {SCORED_FILE}")
    if download_top > 0:
        print(f"PDFs:   {PDF_DOWNLOAD_DIR}")


def show_status():
    """Show current expansion status."""
    print(f"\n═══ SNOWBALL EXPANSION STATUS ═══\n")

    if CANDIDATES_FILE.exists():
        cands = json.loads(CANDIDATES_FILE.read_text())
        print(f"Candidates file: {len(cands.get('candidates', []))} DOIs")

    if METADATA_CACHE.exists():
        cache = json.loads(METADATA_CACHE.read_text())
        resolved = sum(1 for v in cache.values() if not v.get("_error"))
        errors = sum(1 for v in cache.values() if v.get("_error"))
        print(f"Metadata cache: {resolved} resolved, {errors} errors")

    if SCORED_FILE.exists():
        scored = json.loads(SCORED_FILE.read_text())
        candidates = scored.get("candidates", [])
        print(f"Scored candidates: {len(candidates)}")
        high = sum(1 for c in candidates if c.get("relevance_score", 0) >= 0.5)
        print(f"  High relevance: {high}")
        print(f"  Top score: {candidates[0]['expansion_score'] if candidates else 0}")

    if PDF_DOWNLOAD_DIR.exists():
        pdfs = list(PDF_DOWNLOAD_DIR.glob("*.pdf"))
        print(f"Downloaded PDFs: {len(pdfs)}")


def main():
    parser = argparse.ArgumentParser(description="Snowball corpus expansion via citation graph")
    parser.add_argument("--min-citations", type=int, default=3,
                        help="Minimum corpus co-citations to consider (default: 3)")
    parser.add_argument("--status", action="store_true", help="Show expansion stats")
    parser.add_argument("--fetch-metadata", action="store_true", help="Only fetch metadata (step 1)")
    parser.add_argument("--score-relevance", action="store_true", help="Only score relevance (step 2)")
    parser.add_argument("--find-pdfs", action="store_true", help="Find OA PDFs for top candidates")
    parser.add_argument("--download-top", type=int, default=0,
                        help="Download top N PDFs (requires OA access)")
    args = parser.parse_args()

    if args.status:
        show_status()
        return

    run_full_pipeline(
        min_citations=args.min_citations,
        download_top=args.download_top,
    )


if __name__ == "__main__":
    main()
