#!/usr/bin/env python3
"""
CROSSREF METADATA ENRICHMENT
=============================

Fetches bibliographic metadata from CrossRef for all extracted DOIs.
Uses the free "polite pool" (50 req/sec with mailto header).

Complements Semantic Scholar — use both sources for best coverage.

USAGE:
    python scripts/enrich_crossref.py                    # Enrich all DOIs
    python scripts/enrich_crossref.py --status           # Show enrichment stats
    python scripts/enrich_crossref.py --doi 10.1073/pnas.1301227110  # Single DOI
    python scripts/enrich_crossref.py --missing-only     # Only DOIs without metadata
    python scripts/enrich_crossref.py --email you@email.com  # Set polite pool email

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
EXTRACTIONS_DIR = PROJECT_ROOT / "data" / "extractions"
CROSSREF_CACHE = EXTRACTIONS_DIR / "crossref_cache.json"
ENRICHMENT_OUTPUT = EXTRACTIONS_DIR / "crossref_metadata.json"

# ── Config ──
CROSSREF_API = "https://api.crossref.org/works"
DEFAULT_EMAIL = "dkirsh@gmail.com"  # Polite pool
RATE_LIMIT_DELAY = 0.05  # 50ms = ~20 req/sec (conservative for polite pool)
MAX_RETRIES = 3


def fetch_crossref(doi: str, email: str = DEFAULT_EMAIL) -> dict:
    """
    Fetch metadata from CrossRef for a single DOI.

    Returns raw CrossRef message dict or error dict.
    """
    encoded_doi = urllib.parse.quote(doi, safe="")
    url = f"{CROSSREF_API}/{encoded_doi}"

    headers = {
        "User-Agent": f"ArticleEater/2.0 (mailto:{email})",
        "Accept": "application/json",
    }

    for attempt in range(MAX_RETRIES):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
                return data.get("message", {})
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {"_error": "not_found", "_doi": doi}
            elif e.code == 429:
                wait = (attempt + 1) * 5
                time.sleep(wait)
                continue
            else:
                return {"_error": f"http_{e.code}", "_doi": doi, "_detail": str(e)}
        except urllib.error.URLError as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(2)
                continue
            return {"_error": "url_error", "_doi": doi, "_detail": str(e)}
        except Exception as e:
            return {"_error": "exception", "_doi": doi, "_detail": str(e)}

    return {"_error": "max_retries", "_doi": doi}


def parse_crossref(raw: dict) -> dict:
    """
    Parse CrossRef raw message into a clean metadata dict.

    Extracts: title, authors, journal, year, volume, issue, pages,
    citation_count, publisher, type, ISSN, subject, abstract, URL, license.
    """
    if raw.get("_error"):
        return raw

    # Title
    titles = raw.get("title", [])
    title = titles[0] if titles else None

    # Authors
    authors = []
    for author in raw.get("author", []):
        name_parts = []
        if author.get("given"):
            name_parts.append(author["given"])
        if author.get("family"):
            name_parts.append(author["family"])
        authors.append({
            "name": " ".join(name_parts) if name_parts else "Unknown",
            "orcid": author.get("ORCID"),
            "affiliation": (author.get("affiliation", [{}])[0].get("name")
                          if author.get("affiliation") else None),
        })

    # Date
    date_parts = None
    year = None
    for date_field in ["published-print", "published-online", "published", "created"]:
        dp = raw.get(date_field, {}).get("date-parts", [[]])
        if dp and dp[0]:
            date_parts = dp[0]
            year = date_parts[0] if date_parts else None
            break

    # Journal / container
    containers = raw.get("container-title", [])
    journal = containers[0] if containers else None
    short_containers = raw.get("short-container-title", [])
    journal_short = short_containers[0] if short_containers else None

    # Citation count
    citation_count = raw.get("is-referenced-by-count", 0)

    # Abstract
    abstract = raw.get("abstract")
    if abstract:
        # Strip JATS XML tags
        import re
        abstract = re.sub(r"<[^>]+>", "", abstract).strip()

    # Subject / keywords
    subjects = raw.get("subject", [])

    # License
    licenses = raw.get("license", [])
    license_url = licenses[0].get("URL") if licenses else None

    # DOI
    doi = raw.get("DOI")

    return {
        "doi": doi,
        "title": title,
        "authors": authors,
        "year": year,
        "date_parts": date_parts,
        "journal": journal,
        "journal_short": journal_short,
        "volume": raw.get("volume"),
        "issue": raw.get("issue"),
        "pages": raw.get("page"),
        "publisher": raw.get("publisher"),
        "type": raw.get("type"),  # journal-article, book-chapter, proceedings-article, etc.
        "citation_count": citation_count,
        "reference_count": raw.get("reference-count", 0),
        "abstract": abstract,
        "subjects": subjects,
        "issn": raw.get("ISSN", []),
        "url": raw.get("URL"),
        "license_url": license_url,
        "source": "crossref",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def load_cache() -> dict:
    """Load CrossRef cache from disk."""
    if CROSSREF_CACHE.exists():
        try:
            return json.loads(CROSSREF_CACHE.read_text())
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")
    return {}


def save_cache(cache: dict):
    """Save CrossRef cache to disk."""
    CROSSREF_CACHE.parent.mkdir(parents=True, exist_ok=True)
    CROSSREF_CACHE.write_text(json.dumps(cache, indent=2))


def get_all_dois() -> list[str]:
    """Get all DOIs from extraction files."""
    dois = set()

    # DOI-based extraction files
    for f in EXTRACTIONS_DIR.glob("10.*.json"):
        try:
            data = json.loads(f.read_text())
            doi = data.get("doi")
            if doi:
                dois.add(doi)
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")

    # Also check non-DOI extraction files for doi field
    for f in EXTRACTIONS_DIR.glob("*.json"):
        if f.name.startswith("10.") or f.name in ("progress_v2.json", "crossref_cache.json",
                                                     "crossref_metadata.json", "work_claims.json",
                                                     "recovery_claims.json"):
            continue
        try:
            data = json.loads(f.read_text())
            doi = data.get("doi")
            if doi and doi.startswith("10."):
                dois.add(doi)
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")

    return sorted(dois)


def enrich_batch(dois: list[str], email: str = DEFAULT_EMAIL, missing_only: bool = False) -> dict:
    """
    Fetch CrossRef metadata for a batch of DOIs.

    Returns dict mapping DOI -> parsed metadata.
    """
    cache = load_cache()
    results = {}
    fetched = 0
    cached = 0
    errors = 0

    for i, doi in enumerate(dois, 1):
        # Check cache
        if doi in cache and not cache[doi].get("_error"):
            if missing_only:
                continue
            results[doi] = cache[doi]
            cached += 1
            continue

        # Fetch from CrossRef
        print(f"[{i}/{len(dois)}] {doi[:55]}", end=" ", flush=True)

        raw = fetch_crossref(doi, email)
        parsed = parse_crossref(raw)
        results[doi] = parsed
        cache[doi] = parsed

        if parsed.get("_error"):
            errors += 1
            print(f"✗ {parsed['_error']}")
        else:
            fetched += 1
            cite = parsed.get("citation_count", 0)
            year = parsed.get("year", "?")
            title = (parsed.get("title") or "")[:40]
            print(f"✓ {year} | {cite} cites | {title}")

        # Save cache periodically
        if fetched % 50 == 0:
            save_cache(cache)

        time.sleep(RATE_LIMIT_DELAY)

    # Final save
    save_cache(cache)

    print(f"\n{'═'*60}")
    print(f"ENRICHMENT COMPLETE")
    print(f"{'═'*60}")
    print(f"Fetched:  {fetched}")
    print(f"Cached:   {cached}")
    print(f"Errors:   {errors}")
    print(f"Total:    {len(results)}")

    return results


def merge_with_extractions(metadata: dict):
    """
    Save merged metadata alongside extraction files.

    Creates/updates crossref_metadata.json with all resolved metadata.
    Also patches individual extraction JSONs with crossref_* fields.
    """
    # Save combined metadata file
    ENRICHMENT_OUTPUT.write_text(json.dumps(metadata, indent=2))
    print(f"\nSaved combined metadata: {ENRICHMENT_OUTPUT}")

    # Patch individual extraction files with crossref fields
    patched = 0
    for doi, meta in metadata.items():
        if meta.get("_error"):
            continue

        doi_safe = doi.replace("/", "_")
        ext_file = EXTRACTIONS_DIR / f"{doi_safe}.json"
        if not ext_file.exists():
            continue

        try:
            ext_data = json.loads(ext_file.read_text())

            # Add crossref-sourced fields (prefixed to avoid conflicts)
            ext_data["crossref_title"] = meta.get("title")
            ext_data["crossref_authors"] = meta.get("authors")
            ext_data["crossref_year"] = meta.get("year")
            ext_data["crossref_journal"] = meta.get("journal")
            ext_data["crossref_citation_count"] = meta.get("citation_count")
            ext_data["crossref_type"] = meta.get("type")
            ext_data["crossref_publisher"] = meta.get("publisher")
            ext_data["crossref_subjects"] = meta.get("subjects")
            ext_data["crossref_abstract"] = meta.get("abstract")
            ext_data["crossref_fetched_at"] = meta.get("fetched_at")

            ext_file.write_text(json.dumps(ext_data, indent=2))
            patched += 1
        except Exception as e:
            print(f"  Warning: Failed to patch {doi_safe}: {e}")

    print(f"Patched {patched} extraction files with crossref_* fields")


def show_status():
    """Show enrichment statistics."""
    cache = load_cache()
    all_dois = get_all_dois()

    print(f"\n═══ CROSSREF ENRICHMENT STATUS ═══\n")
    print(f"Total DOIs in corpus:  {len(all_dois)}")
    print(f"Cached in CrossRef:    {len(cache)}")

    if cache:
        success = sum(1 for v in cache.values() if not v.get("_error"))
        not_found = sum(1 for v in cache.values() if v.get("_error") == "not_found")
        other_err = sum(1 for v in cache.values() if v.get("_error") and v.get("_error") != "not_found")
        print(f"  ✓ Success:           {success}")
        print(f"  ✗ Not found:         {not_found}")
        print(f"  ⚠ Other errors:      {other_err}")

        missing = [d for d in all_dois if d not in cache]
        print(f"\nMissing (not yet fetched): {len(missing)}")

        # Citation stats
        cites = [v.get("citation_count", 0) for v in cache.values() if not v.get("_error")]
        if cites:
            print(f"\nCitation stats:")
            print(f"  Total citations:     {sum(cites)}")
            print(f"  Mean:                {sum(cites)/len(cites):.1f}")
            print(f"  Median:              {sorted(cites)[len(cites)//2]}")
            print(f"  Max:                 {max(cites)}")

            # Top cited
            top = sorted(
                [(v.get("citation_count", 0), v.get("doi", "?"), (v.get("title") or "?")[:50])
                 for v in cache.values() if not v.get("_error")],
                reverse=True
            )[:10]
            print(f"\nTop 10 most cited:")
            for cite_count, doi, title in top:
                print(f"  {cite_count:5d}  {title}")

        # Year distribution
        years = [v.get("year") for v in cache.values() if v.get("year") and not v.get("_error")]
        if years:
            from collections import Counter
            year_counts = Counter(years)
            print(f"\nYear distribution:")
            for yr in sorted(year_counts.keys()):
                bar = "█" * (year_counts[yr] // 2 + 1)
                print(f"  {yr}: {year_counts[yr]:3d} {bar}")


def main():
    parser = argparse.ArgumentParser(description="CrossRef metadata enrichment")
    parser.add_argument("--email", default=DEFAULT_EMAIL, help="Email for polite pool")
    parser.add_argument("--doi", help="Fetch single DOI")
    parser.add_argument("--status", action="store_true", help="Show enrichment stats")
    parser.add_argument("--missing-only", action="store_true", help="Only fetch DOIs not in cache")
    parser.add_argument("--no-patch", action="store_true", help="Don't patch extraction files")
    parser.add_argument("--limit", type=int, help="Max DOIs to fetch")
    args = parser.parse_args()

    if args.status:
        show_status()
        return

    if args.doi:
        raw = fetch_crossref(args.doi, args.email)
        parsed = parse_crossref(raw)
        print(json.dumps(parsed, indent=2))
        return

    # Batch mode
    all_dois = get_all_dois()
    print(f"Found {len(all_dois)} DOIs in corpus")

    if args.missing_only:
        cache = load_cache()
        all_dois = [d for d in all_dois if d not in cache or cache[d].get("_error")]
        print(f"After filtering cached: {len(all_dois)} DOIs to fetch")

    if args.limit:
        all_dois = all_dois[:args.limit]

    if not all_dois:
        print("No DOIs to fetch!")
        return

    metadata = enrich_batch(all_dois, args.email, args.missing_only)

    if not args.no_patch:
        merge_with_extractions(metadata)


if __name__ == "__main__":
    main()
