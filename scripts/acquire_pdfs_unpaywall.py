#!/usr/bin/env python3
"""
acquire_pdfs_unpaywall.py — Automated PDF acquisition via Unpaywall API
=======================================================================

Queries the Unpaywall API for open-access PDF links for all 56 HIGH-priority
articles from the figure scanner. Downloads available PDFs to data/pdfs/.

Usage:
    # Check what's available (no downloads)
    python scripts/acquire_pdfs_unpaywall.py --check-only

    # Download available OA PDFs
    python scripts/acquire_pdfs_unpaywall.py --download

    # Export DOI list for manual tools (Zotero, Elicit, etc.)
    python scripts/acquire_pdfs_unpaywall.py --export-dois

    # Export Zotero-importable RIS file
    python scripts/acquire_pdfs_unpaywall.py --export-ris

Created: 2026-02-28
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

UNPAYWALL_EMAIL = os.getenv("UNPAYWALL_EMAIL", "dkirsh@gmail.com")
SCAN_FILE = "data/figure_scan/high_priority_articles.json"
PDF_DIR = "data/pdfs"
REPORT_FILE = "data/figure_scan/pdf_acquisition_report.json"
DOI_EXPORT_FILE = "data/figure_scan/dois_for_manual_acquisition.txt"
RIS_EXPORT_FILE = "data/figure_scan/articles_for_zotero.ris"

RATE_LIMIT_DELAY = 1.1  # Unpaywall asks for ≤1 req/sec for polite pool


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class AcquisitionResult:
    doi: str
    doi_standard: str  # with / instead of _
    is_title_based: bool
    unpaywall_status: str  # "found_oa", "found_closed", "not_found", "error", "skipped"
    pdf_url: Optional[str] = None
    oa_status: Optional[str] = None  # "gold", "green", "hybrid", "bronze"
    journal: Optional[str] = None
    title: Optional[str] = None
    downloaded: bool = False
    local_path: Optional[str] = None
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# DOI normalization
# ---------------------------------------------------------------------------

def normalize_doi(raw_doi: str) -> tuple:
    """Convert filesystem DOI (underscores) to standard DOI (slashes/dots).
    Returns (standard_doi, is_title_based)."""
    if not raw_doi.startswith("10."):
        return (raw_doi, True)

    # Split at first underscore to get prefix/suffix
    parts = raw_doi.split("_", 1)
    if len(parts) == 2:
        # Reconstruct: 10.XXXX/rest.with.dots
        doi = parts[0] + "/" + parts[1].replace("_", ".")
        # Fix edge cases: parenthetical DOIs like s0097-8493(97)00030-7
        # These should have been preserved
        return (doi, False)
    return (raw_doi, False)


# ---------------------------------------------------------------------------
# Unpaywall query
# ---------------------------------------------------------------------------

def query_unpaywall(doi: str) -> Dict:
    """Query Unpaywall API for a single DOI. Returns parsed JSON or error dict."""
    url = f"https://api.unpaywall.org/v2/{doi}?email={UNPAYWALL_EMAIL}"

    req = urllib.request.Request(url, headers={
        "User-Agent": "ATLAS-ArticleEater/1.0 (mailto:{})".format(UNPAYWALL_EMAIL)
    })

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"error": "not_found", "code": 404}
        return {"error": str(e), "code": e.code}
    except Exception as e:
        return {"error": str(e), "code": -1}


def find_best_pdf_url(unpaywall_data: Dict) -> Optional[str]:
    """Extract the best PDF URL from Unpaywall response."""
    # Prefer best_oa_location
    best = unpaywall_data.get("best_oa_location")
    if best and best.get("url_for_pdf"):
        return best["url_for_pdf"]

    # Fall back to any OA location with PDF
    for loc in unpaywall_data.get("oa_locations", []):
        if loc.get("url_for_pdf"):
            return loc["url_for_pdf"]

    # Last resort: landing page URL (not a direct PDF but can be navigated)
    if best and best.get("url"):
        return None  # Don't auto-download landing pages

    return None


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------

def download_pdf(url: str, dest_path: str) -> bool:
    """Download a PDF file. Returns True on success."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "ATLAS-ArticleEater/1.0"
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()
            # Basic PDF validation
            if not content[:5] == b"%PDF-":
                return False
            Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
            with open(dest_path, "wb") as f:
                f.write(content)
            return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Export helpers
# ---------------------------------------------------------------------------

def export_dois(articles: List[Dict], output_path: str):
    """Export DOIs in multiple formats for different tools."""
    dois = []
    titles = []
    for a in articles:
        std_doi, is_title = normalize_doi(a["doi"])
        if is_title:
            titles.append(std_doi)
        else:
            dois.append(std_doi)

    with open(output_path, "w") as f:
        f.write("# DOIs for 56 HIGH-Priority Articles (ATLAS Figure Scanner)\n")
        f.write(f"# Generated: {time.strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"# Standard DOIs: {len(dois)}, Title-based: {len(titles)}\n\n")

        f.write("# === STANDARD DOIs (paste into Zotero Add by Identifier, or Elicit/Consensus) ===\n")
        for d in sorted(dois):
            f.write(f"{d}\n")

        f.write(f"\n# === TITLE-BASED (search manually in Google Scholar or Semantic Scholar) ===\n")
        for t in sorted(titles):
            readable = t.replace("_", " ")
            f.write(f"# {readable}\n")

        f.write(f"\n# === COMMA-SEPARATED (for bulk tools) ===\n")
        f.write(", ".join(sorted(dois)))
        f.write("\n")

        f.write(f"\n# === NEWLINE-SEPARATED DOI URLs (for browser batch open) ===\n")
        for d in sorted(dois):
            f.write(f"https://doi.org/{d}\n")

    print(f"  Exported {len(dois)} DOIs + {len(titles)} titles to {output_path}")


def export_ris(articles: List[Dict], results: List[AcquisitionResult], output_path: str):
    """Export RIS file for Zotero import (triggers Find Available PDF)."""
    with open(output_path, "w") as f:
        for r in results:
            if r.is_title_based:
                continue
            f.write("TY  - JOUR\n")
            if r.title:
                f.write(f"TI  - {r.title}\n")
            f.write(f"DO  - {r.doi_standard}\n")
            if r.journal:
                f.write(f"JO  - {r.journal}\n")
            if r.pdf_url:
                f.write(f"UR  - {r.pdf_url}\n")
            else:
                f.write(f"UR  - https://doi.org/{r.doi_standard}\n")
            f.write("ER  - \n\n")

    print(f"  Exported RIS to {output_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse
    parser = argparse.ArgumentParser(description="PDF acquisition for HIGH-priority articles")
    parser.add_argument("--check-only", action="store_true", help="Query Unpaywall but don't download")
    parser.add_argument("--download", action="store_true", help="Download available OA PDFs")
    parser.add_argument("--export-dois", action="store_true", help="Export DOI list for manual tools")
    parser.add_argument("--export-ris", action="store_true", help="Export RIS file for Zotero import")
    parser.add_argument("--all", action="store_true", help="Do everything: check + download + export")
    args = parser.parse_args()

    if not any([args.check_only, args.download, args.export_dois, args.export_ris, args.all]):
        parser.print_help()
        return

    # Load articles
    articles = json.load(open(SCAN_FILE))
    print(f"Loaded {len(articles)} HIGH-priority articles")

    # Quick DOI export (no API needed)
    if args.export_dois or args.all:
        export_dois(articles, DOI_EXPORT_FILE)

    # Query Unpaywall
    results: List[AcquisitionResult] = []

    if args.check_only or args.download or args.export_ris or args.all:
        print(f"\nQuerying Unpaywall API (email: {UNPAYWALL_EMAIL})...")
        print(f"Rate limit: {RATE_LIMIT_DELAY}s between requests\n")

        for i, article in enumerate(articles):
            raw_doi = article["doi"]
            std_doi, is_title = normalize_doi(raw_doi)

            result = AcquisitionResult(
                doi=raw_doi,
                doi_standard=std_doi,
                is_title_based=is_title,
                unpaywall_status="skipped"
            )

            if is_title:
                result.unpaywall_status = "skipped"
                result.error = "Title-based ID, no DOI for API lookup"
                results.append(result)
                print(f"  [{i+1:2d}/56] SKIP  {std_doi[:60]}... (no DOI)")
                continue

            # Query API
            data = query_unpaywall(std_doi)
            time.sleep(RATE_LIMIT_DELAY)

            if "error" in data:
                result.unpaywall_status = "not_found" if data.get("code") == 404 else "error"
                result.error = data["error"]
                results.append(result)
                print(f"  [{i+1:2d}/56] MISS  {std_doi} — {data['error']}")
                continue

            # Extract metadata
            result.title = data.get("title", "")
            result.journal = data.get("journal_name", "")
            is_oa = data.get("is_oa", False)
            result.oa_status = data.get("oa_status", "closed")

            pdf_url = find_best_pdf_url(data)

            if pdf_url:
                result.unpaywall_status = "found_oa"
                result.pdf_url = pdf_url
                status_str = f"OA ({result.oa_status})"

                # Download if requested
                if args.download or args.all:
                    safe_name = raw_doi.replace("/", "_").replace(".", "_") + ".pdf"
                    dest = os.path.join(PDF_DIR, safe_name)

                    if os.path.exists(dest):
                        result.downloaded = True
                        result.local_path = dest
                        status_str += " [already exists]"
                    else:
                        ok = download_pdf(pdf_url, dest)
                        if ok:
                            result.downloaded = True
                            result.local_path = dest
                            status_str += " [DOWNLOADED]"
                        else:
                            status_str += " [download failed]"
            elif is_oa:
                result.unpaywall_status = "found_oa"
                result.oa_status = data.get("oa_status", "unknown")
                # OA but no direct PDF link
                best = data.get("best_oa_location", {})
                result.pdf_url = best.get("url", f"https://doi.org/{std_doi}")
                status_str = f"OA ({result.oa_status}) — landing page only"
            else:
                result.unpaywall_status = "found_closed"
                status_str = "CLOSED access"

            results.append(result)
            title_short = (result.title or "")[:50]
            print(f"  [{i+1:2d}/56] {status_str:40s} {std_doi}")

        # Export RIS if requested
        if args.export_ris or args.all:
            export_ris(articles, results, RIS_EXPORT_FILE)

        # Save report
        report = {
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total_articles": len(articles),
            "summary": {
                "found_oa": sum(1 for r in results if r.unpaywall_status == "found_oa"),
                "found_closed": sum(1 for r in results if r.unpaywall_status == "found_closed"),
                "not_found": sum(1 for r in results if r.unpaywall_status == "not_found"),
                "skipped_title_based": sum(1 for r in results if r.unpaywall_status == "skipped"),
                "errors": sum(1 for r in results if r.unpaywall_status == "error"),
                "downloaded": sum(1 for r in results if r.downloaded),
                "with_pdf_url": sum(1 for r in results if r.pdf_url),
            },
            "results": [
                {
                    "doi": r.doi,
                    "doi_standard": r.doi_standard,
                    "status": r.unpaywall_status,
                    "oa_status": r.oa_status,
                    "pdf_url": r.pdf_url,
                    "title": r.title,
                    "journal": r.journal,
                    "downloaded": r.downloaded,
                    "local_path": r.local_path,
                    "error": r.error,
                }
                for r in results
            ],
            "needs_manual": [
                {
                    "doi": r.doi_standard,
                    "title": r.title,
                    "reason": r.unpaywall_status,
                    "url": f"https://doi.org/{r.doi_standard}" if not r.is_title_based else None,
                }
                for r in results
                if not r.downloaded and r.unpaywall_status != "skipped"
            ],
        }

        Path(REPORT_FILE).parent.mkdir(parents=True, exist_ok=True)
        with open(REPORT_FILE, "w") as f:
            json.dump(report, f, indent=2)

        # Print summary
        s = report["summary"]
        print(f"\n{'='*60}")
        print(f"PDF ACQUISITION SUMMARY")
        print(f"{'='*60}")
        print(f"  Total articles:      {len(articles)}")
        print(f"  Open Access (PDF):   {s['found_oa']}")
        print(f"  Closed access:       {s['found_closed']}")
        print(f"  Not in Unpaywall:    {s['not_found']}")
        print(f"  Title-based (skip):  {s['skipped_title_based']}")
        print(f"  Errors:              {s['errors']}")
        print(f"  Downloaded:          {s['downloaded']}")
        print(f"  With PDF URL:        {s['with_pdf_url']}")
        print(f"{'='*60}")

        remaining = [r for r in results if not r.downloaded]
        if remaining:
            print(f"\n  {len(remaining)} articles still need PDFs.")
            print(f"  See: {REPORT_FILE}")
            print(f"  Manual DOIs: {DOI_EXPORT_FILE}")

            closed = [r for r in remaining if r.unpaywall_status == "found_closed"]
            if closed:
                print(f"\n  CLOSED ACCESS ({len(closed)} articles) — try these methods:")
                print(f"    1. Zotero: Import RIS file → select all → Find Available PDFs")
                print(f"    2. UCSD Library proxy: https://doi.org/DOI via VPN")
                print(f"    3. ChatGPT ScholarAI GPT: ask for each DOI")
                print(f"    4. Consensus.app or Elicit.com: search by DOI")


if __name__ == "__main__":
    main()
