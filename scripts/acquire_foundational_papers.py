#!/usr/bin/env python3
"""
acquire_foundational_papers.py — Cascade PDF acquisition for theoretical foundations
===================================================================================

Downloads PDFs for the 53 foundational papers that our T1/T1.5 theories are
built on, using a cascade of free/cheap APIs before falling back to manual.

Cascade order:
  1. OpenAlex Content API ($0.01/PDF) — has 60M+ PDFs
  2. Unpaywall API (free) — open-access only
  3. CORE API (free) — institutional repository copies
  4. Fallback list — for manual acquisition via Elicit/Academia.edu

Usage:
  python scripts/acquire_foundational_papers.py
  python scripts/acquire_foundational_papers.py --dry-run    # check availability only
  python scripts/acquire_foundational_papers.py --doi 10.1038/nrn2787  # single DOI

Author: AG (Antigravity)
Date: 2026-03-02
"""

import json
import os
import sys
import time
import argparse
import logging
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Tuple
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# =============================================================================
# API CONFIGURATION
# =============================================================================

API_KEYS = {
    "openalex": "LdFrQE7lT9a2Lu2iiOZ67p",
    "semantic_scholar": "oXhGSyVyUi6mzyyOITIKg1mSsV3LQtGy2PcvS9TL",
    "pubmed": "09f9932a53a12dc409bfb7398747f8b2008",
    "crossref_mailto": "dkirsh@ucsd.edu",
    "core": "fXs5vqICUhjkPRlAgunaQiKOTW2m30xZ",  # expires 2026-04-02
    "ncbi": "6bb6071567491455d7bc925c9f2aba0f6908",  # PMC/PubMed
}

OPENALEX_API = "https://api.openalex.org"
OPENALEX_CONTENT = "https://content.openalex.org"
UNPAYWALL_API = "https://api.unpaywall.org/v2"
CORE_API = "https://api.core.ac.uk/v3"
NCBI_CONVERT = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0"
PMC_OA = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi"

PDF_DIR = Path("data/pdfs_incoming")
REPORT_FILE = Path("data/acquisition/foundational_acquisition_report.json")

RATE_LIMIT = 0.5  # seconds between requests


# =============================================================================
# FOUNDATIONAL PAPERS — 53 papers across T1/T1.5
# =============================================================================

FOUNDATIONAL_PAPERS = [
    # T1: Predictive Processing
    {"doi": "10.1017/S0140525X12000477", "author": "Clark 2013", "theory": "Predictive Processing", "type": "journal"},
    {"doi": None, "isbn": "978-0190217013", "author": "Clark 2015", "theory": "Predictive Processing", "type": "book", "title": "Surfing Uncertainty"},
    {"doi": "10.1038/nrn2787", "author": "Friston 2010", "theory": "Predictive Processing", "type": "journal"},
    {"doi": None, "isbn": "978-0199682737", "author": "Hohwy 2013", "theory": "Predictive Processing", "type": "book", "title": "The Predictive Mind"},

    # T1: Embodied Cognition
    {"doi": None, "isbn": "978-0898599596", "author": "Gibson 1979", "theory": "Embodied Cognition", "type": "book", "title": "The Ecological Approach to Visual Perception"},
    {"doi": "10.1146/annurev.psych.59.103006.093639", "author": "Barsalou 2008", "theory": "Embodied Cognition", "type": "journal"},
    {"doi": None, "isbn": "978-0262531566", "author": "Clark 1997", "theory": "Embodied Cognition", "type": "book", "title": "Being There"},
    {"doi": None, "isbn": "978-0262720212", "author": "Varela 1991", "theory": "Embodied Cognition", "type": "book", "title": "The Embodied Mind"},

    # T1: Spatial Navigation
    {"doi": None, "author": "O'Keefe 1978", "theory": "Spatial Navigation", "type": "book", "title": "The Hippocampus as a Cognitive Map"},
    {"doi": "10.1146/annurev.neuro.31.061307.090723", "author": "Moser 2008", "theory": "Spatial Navigation", "type": "journal"},
    {"doi": "10.1037/h0061626", "author": "Tolman 1948", "theory": "Spatial Navigation", "type": "journal"},

    # T1: Neuromodulatory
    {"doi": "10.1016/j.tins.2009.05.001", "author": "Berridge 2009", "theory": "Neuromodulatory", "type": "journal"},
    {"doi": "10.1126/science.275.5306.1593", "author": "Schultz 1997", "theory": "Neuromodulatory", "type": "journal"},
    {"doi": "10.1146/annurev.neuro.051508.135607", "author": "Dayan 2009", "theory": "Neuromodulatory", "type": "journal"},

    # T1: Interoceptive
    {"doi": "10.1038/nrn894", "author": "Craig 2002", "theory": "Interoceptive", "type": "journal"},
    {"doi": "10.1016/j.tics.2013.09.007", "author": "Seth 2013", "theory": "Interoceptive", "type": "journal"},
    {"doi": "10.1098/rstb.2016.0010", "author": "Barrett 2017", "theory": "Interoceptive", "type": "journal"},

    # T1: DMN/TPN
    {"doi": "10.1073/pnas.98.2.676", "author": "Raichle 2001", "theory": "DMN/TPN", "type": "journal"},
    {"doi": "10.1073/pnas.0504136102", "author": "Fox 2005", "theory": "DMN/TPN", "type": "journal"},
    {"doi": "10.1196/annals.1440.011", "author": "Buckner 2008", "theory": "DMN/TPN", "type": "journal"},

    # T1: Active Inference
    {"doi": "10.1007/s00422-010-0364-z", "author": "Friston 2010b", "theory": "Active Inference", "type": "journal"},
    {"doi": "10.1162/neco_a_01136", "author": "Pezzulo 2018", "theory": "Active Inference", "type": "journal"},

    # T1: Circadian/Homeostatic
    {"doi": None, "pmid": "7185792", "author": "Borbely 1982", "theory": "Circadian", "type": "journal", "title": "A two process model of sleep regulation"},
    {"doi": "10.1126/science.284.5423.2177", "author": "Czeisler 1999", "theory": "Circadian", "type": "journal"},

    # T1: Allostatic
    {"doi": "10.1016/S0893-133X(99)00129-3", "author": "McEwen 2000", "theory": "Allostatic", "type": "journal"},
    {"doi": "10.1016/j.physbeh.2011.06.004", "author": "Sterling 2012", "theory": "Allostatic", "type": "journal"},

    # T1: Social
    {"doi": "10.1017/S0140525X05000129", "author": "Tomasello 2005", "theory": "Social", "type": "journal"},
    {"doi": "10.1002/(SICI)1520-6505(1998)6:5<178::AID-EVAN5>3.0.CO;2-8", "author": "Dunbar 1998", "theory": "Social", "type": "journal"},

    # T1.5: ART
    {"doi": None, "isbn": "978-0521341394", "author": "Kaplan 1989", "theory": "ART", "type": "book", "title": "The Experience of Nature"},
    {"doi": "10.1016/0272-4944(95)90001-2", "author": "Kaplan 1995", "theory": "ART", "type": "journal"},

    # T1.5: SRT
    {"doi": "10.1007/978-1-4613-3539-9_4", "author": "Ulrich 1983", "theory": "SRT", "type": "book_chapter"},
    {"doi": "10.1016/S0272-4944(05)80184-7", "author": "Ulrich 1991", "theory": "SRT", "type": "journal"},

    # T1.5: Biophilia
    {"doi": None, "isbn": "978-0674074422", "author": "Wilson 1984", "theory": "Biophilia", "type": "book", "title": "Biophilia"},
    {"doi": None, "isbn": "978-1559631471", "author": "Kellert 1993", "theory": "Biophilia", "type": "book", "title": "The Biophilia Hypothesis"},

    # T1.5: Prospect-Refuge
    {"doi": None, "isbn": "978-0471032564", "author": "Appleton 1975", "theory": "Prospect-Refuge", "type": "book", "title": "The Experience of Landscape"},
    {"doi": "10.1186/s40410-016-0033-1", "author": "Dosen 2016", "theory": "Prospect-Refuge", "type": "journal"},

    # T1.5: Privacy Regulation
    {"doi": None, "isbn": "978-0818501685", "author": "Altman 1975", "theory": "Privacy Regulation", "type": "book", "title": "The Environment and Social Behavior"},

    # T1.5: Kaplan Preference
    {"doi": None, "isbn": "978-0030623172", "author": "Kaplan 1982", "theory": "Kaplan Preference", "type": "book", "title": "Cognition and Environment"},

    # T1.5: Adaptive Thermal
    {"doi": None, "author": "de Dear 1998", "theory": "Adaptive Thermal", "type": "journal", "title": "Developing an adaptive model of thermal comfort"},
    {"doi": None, "author": "Humphreys 1998", "theory": "Adaptive Thermal", "type": "journal", "title": "Understanding the adaptive approach to thermal comfort"},

    # T1.5: Space Syntax
    {"doi": None, "isbn": "978-0521367844", "author": "Hillier 1984", "theory": "Space Syntax", "type": "book", "title": "The Social Logic of Space"},
    {"doi": None, "isbn": "978-0521646581", "author": "Hillier 1996", "theory": "Space Syntax", "type": "book", "title": "Space Is the Machine"},

    # T1.5: Soundscape
    {"doi": None, "isbn": "978-0892814558", "author": "Schafer 1977", "theory": "Soundscape", "type": "book", "title": "The Soundscape"},
    {"doi": "10.1016/j.apacoust.2011.01.001", "author": "Brown 2011", "theory": "Soundscape", "type": "journal"},

    # T1.5: Place Attachment
    {"doi": "10.1016/j.jenvp.2010.10.001", "author": "Lewicka 2011", "theory": "Place Attachment", "type": "journal"},
    {"doi": "10.1016/j.jenvp.2009.09.006", "author": "Scannell 2010", "theory": "Place Attachment", "type": "journal"},

    # T1.5: BRECVEMA
    {"doi": "10.1016/j.plrev.2013.05.008", "author": "Juslin 2013", "theory": "BRECVEMA", "type": "journal"},

    # T1.5: Flow
    {"doi": None, "isbn": "978-0061339202", "author": "Csikszentmihalyi 1990", "theory": "Flow", "type": "book", "title": "Flow"},

    # T1.5: Goldilocks
    {"doi": None, "isbn": "978-0390085955", "author": "Berlyne 1971", "theory": "Goldilocks", "type": "book", "title": "Aesthetics and Psychobiology"},

    # Epistemological
    {"doi": None, "isbn": "978-0631118510", "author": "Haack 1993", "theory": "Epistemology", "type": "book", "title": "Evidence and Inquiry"},
    {"doi": "10.2307/2181906", "author": "Quine 1951", "theory": "Epistemology", "type": "journal"},
    {"doi": None, "isbn": "978-0075536093", "author": "Quine & Ullian 1978", "theory": "Epistemology", "type": "book", "title": "The Web of Belief"},
]


# =============================================================================
# API FUNCTIONS
# =============================================================================

@dataclass
class AcquisitionResult:
    author: str
    theory: str
    doi: Optional[str] = None
    paper_type: str = "journal"
    openalex_id: Optional[str] = None
    openalex_has_content: bool = False
    unpaywall_oa: bool = False
    unpaywall_pdf_url: Optional[str] = None
    core_has_fulltext: bool = False
    core_pdf_url: Optional[str] = None
    downloaded: bool = False
    local_path: Optional[str] = None
    source: Optional[str] = None
    error: Optional[str] = None


def query_openalex_by_doi(doi: str) -> Optional[Dict]:
    """Query OpenAlex for work metadata by DOI."""
    try:
        url = f"{OPENALEX_API}/works/doi:{doi}"
        params = {"mailto": API_KEYS["crossref_mailto"]}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            return r.json()
        else:
            logger.debug(f"OpenAlex lookup failed for {doi}: {r.status_code}")
            return None
    except Exception as e:
        logger.debug(f"OpenAlex error for {doi}: {e}")
        return None


def check_openalex_content(openalex_id: str) -> bool:
    """Check if OpenAlex has downloadable content for a work."""
    try:
        url = f"{OPENALEX_CONTENT}/works/{openalex_id}.pdf"
        params = {"api_key": API_KEYS["openalex"]}
        r = requests.head(url, params=params, timeout=10, allow_redirects=False)
        return r.status_code in (200, 302)
    except Exception:
        return False


def download_openalex_pdf(openalex_id: str, dest_path: str) -> bool:
    """Download PDF from OpenAlex Content API."""
    try:
        url = f"{OPENALEX_CONTENT}/works/{openalex_id}.pdf"
        params = {"api_key": API_KEYS["openalex"]}
        r = requests.get(url, params=params, timeout=30, allow_redirects=True)
        if r.status_code == 200 and len(r.content) > 1000:
            with open(dest_path, "wb") as f:
                f.write(r.content)
            return True
        return False
    except Exception as e:
        logger.warning(f"OpenAlex download failed for {openalex_id}: {e}")
        return False


def query_unpaywall(doi: str) -> Optional[str]:
    """Query Unpaywall for OA PDF URL."""
    try:
        url = f"{UNPAYWALL_API}/{doi}"
        params = {"email": API_KEYS["crossref_mailto"]}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            # Check best OA location
            best = data.get("best_oa_location", {})
            if best and best.get("url_for_pdf"):
                return best["url_for_pdf"]
            # Check all OA locations
            for loc in data.get("oa_locations", []):
                if loc.get("url_for_pdf"):
                    return loc["url_for_pdf"]
        return None
    except Exception:
        return None


def query_core(doi: str) -> Optional[str]:
    """Query CORE API for repository full text by DOI."""
    try:
        url = f"{CORE_API}/search/works"
        headers = {"Authorization": f"Bearer {API_KEYS['core']}"}
        params = {"q": f'doi:"{doi}"', "limit": 1}
        r = requests.get(url, headers=headers, params=params, timeout=15)
        if r.status_code == 200:
            data = r.json()
            results = data.get("results", [])
            if results:
                for result in results:
                    dl_url = result.get("downloadUrl")
                    if dl_url and dl_url.endswith(".pdf"):
                        return dl_url
                    for ft_url in result.get("sourceFulltextUrls", []):
                        if ft_url and "pdf" in ft_url.lower():
                            return ft_url
                    for link in result.get("links", []):
                        link_url = link.get("url", "")
                        if link_url and "pdf" in link_url.lower():
                            return link_url
        return None
    except Exception as e:
        logger.debug(f"CORE error for {doi}: {e}")
        return None


def query_pmc(doi: str) -> Optional[str]:
    """Query PMC for open-access full text via DOI→PMCID conversion."""
    try:
        # Step 1: Convert DOI to PMCID
        params = {
            "ids": doi,
            "format": "json",
            "tool": "ArticleEater",
            "email": API_KEYS["crossref_mailto"],
            "api_key": API_KEYS["ncbi"],
        }
        r = requests.get(NCBI_CONVERT, params=params, timeout=10)
        if r.status_code != 200:
            return None

        data = r.json()
        records = data.get("records", [])
        if not records:
            return None

        pmcid = records[0].get("pmcid")
        if not pmcid:
            return None

        # Step 2: Check PMC OA service for PDF
        oa_params = {"id": pmcid, "format": "json"}
        r2 = requests.get(PMC_OA, params=oa_params, timeout=10)
        if r2.status_code == 200:
            oa_data = r2.json()
            records2 = oa_data.get("records", [])
            if records2:
                for rec in records2:
                    link = rec.get("link")
                    if link:
                        href = link if isinstance(link, str) else link.get("href", "")
                        if href:
                            return href

        # Fallback: direct PMC PDF URL
        return f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/"

    except Exception as e:
        logger.debug(f"PMC error for {doi}: {e}")
        return None


def download_pdf(url: str, dest_path: str) -> bool:
    """Download a PDF from a URL."""
    try:
        headers = {"User-Agent": "ArticleEater/1.0 (mailto:dkirsh@ucsd.edu)"}
        r = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        if r.status_code == 200 and len(r.content) > 1000:
            content_type = r.headers.get("Content-Type", "")
            if "pdf" in content_type or r.content[:5] == b"%PDF-":
                with open(dest_path, "wb") as f:
                    f.write(r.content)
                return True
        return False
    except Exception:
        return False


# =============================================================================
# MAIN CASCADE
# =============================================================================

def acquire_paper(paper: Dict, dry_run: bool = False) -> AcquisitionResult:
    """Run the acquisition cascade for one paper."""
    result = AcquisitionResult(
        author=paper["author"],
        theory=paper["theory"],
        doi=paper.get("doi"),
        paper_type=paper.get("type", "journal"),
    )

    doi = paper.get("doi")
    if not doi:
        result.error = f"No DOI — {paper.get('type', 'unknown')} (need manual acquisition)"
        return result

    safe_doi = doi.replace("/", "_").replace(":", "_")
    dest_path = str(PDF_DIR / f"{safe_doi}.pdf")

    # Check if already downloaded
    if os.path.exists(dest_path):
        result.downloaded = True
        result.local_path = dest_path
        result.source = "already_exists"
        return result

    # Step 1: OpenAlex
    logger.info(f"  [1/3] OpenAlex lookup: {doi}")
    oa_data = query_openalex_by_doi(doi)
    if oa_data:
        result.openalex_id = oa_data.get("id", "").split("/")[-1]
        content_url = oa_data.get("content_url")
        if content_url:
            result.openalex_has_content = True
            if not dry_run and result.openalex_id:
                if download_openalex_pdf(result.openalex_id, dest_path):
                    result.downloaded = True
                    result.local_path = dest_path
                    result.source = "openalex"
                    return result

    time.sleep(RATE_LIMIT)

    # Step 2: Unpaywall
    logger.info(f"  [2/3] Unpaywall lookup: {doi}")
    pdf_url = query_unpaywall(doi)
    if pdf_url:
        result.unpaywall_oa = True
        result.unpaywall_pdf_url = pdf_url
        if not dry_run:
            if download_pdf(pdf_url, dest_path):
                result.downloaded = True
                result.local_path = dest_path
                result.source = "unpaywall"
                return result

    time.sleep(RATE_LIMIT)

    # Step 3: CORE API — repository full texts
    logger.info(f"  [3/5] CORE lookup: {doi}")
    core_url = query_core(doi)
    if core_url:
        result.core_has_fulltext = True
        result.core_pdf_url = core_url
        if not dry_run:
            if download_pdf(core_url, dest_path):
                result.downloaded = True
                result.local_path = dest_path
                result.source = "core"
                return result

    time.sleep(RATE_LIMIT)

    # Step 4: PMC — NIH-funded open access
    logger.info(f"  [4/5] PMC lookup: {doi}")
    pmc_url = query_pmc(doi)
    if pmc_url:
        if not dry_run:
            if download_pdf(pmc_url, dest_path):
                result.downloaded = True
                result.local_path = dest_path
                result.source = "pmc"
                return result
        else:
            # In dry-run, count PMC as available
            result.core_has_fulltext = True  # reuse field for availability

    time.sleep(RATE_LIMIT)

    # Step 5: OpenAlex OA URL fallback
    if oa_data:
        oa_info = oa_data.get("open_access", {})
        oa_url = oa_info.get("oa_url")
        if oa_url and not dry_run:
            logger.info(f"  [5/5] OpenAlex OA URL fallback: {oa_url}")
            if download_pdf(oa_url, dest_path):
                result.downloaded = True
                result.local_path = dest_path
                result.source = "openalex_oa_url"
                return result

    if not result.downloaded:
        result.error = "Not available via automated sources — needs manual acquisition"

    return result


def main():
    parser = argparse.ArgumentParser(description="Acquire foundational theory papers")
    parser.add_argument("--dry-run", action="store_true", help="Check availability without downloading")
    parser.add_argument("--doi", type=str, help="Acquire a single DOI")
    parser.add_argument("--journals-only", action="store_true", help="Skip books (no DOI)")
    args = parser.parse_args()

    # Ensure directories exist
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Filter papers
    papers = FOUNDATIONAL_PAPERS
    if args.doi:
        papers = [p for p in papers if p.get("doi") == args.doi]
        if not papers:
            logger.error(f"DOI {args.doi} not found in foundational papers list")
            sys.exit(1)
    if args.journals_only:
        papers = [p for p in papers if p.get("doi")]

    # Stats
    total = len(papers)
    with_doi = sum(1 for p in papers if p.get("doi"))
    books = sum(1 for p in papers if not p.get("doi"))

    logger.info(f"=" * 60)
    logger.info(f"Foundational Paper Acquisition — {'DRY RUN' if args.dry_run else 'LIVE'}")
    logger.info(f"Total: {total} papers ({with_doi} with DOI, {books} books/no DOI)")
    logger.info(f"PDF directory: {PDF_DIR}")
    logger.info(f"=" * 60)

    results = []
    downloaded = 0
    available = 0
    manual_needed = 0

    for i, paper in enumerate(papers, 1):
        logger.info(f"\n[{i}/{total}] {paper['author']} — {paper['theory']}")
        result = acquire_paper(paper, dry_run=args.dry_run)
        results.append(result)

        if result.downloaded:
            downloaded += 1
            logger.info(f"  ✅ Downloaded via {result.source}")
        elif result.openalex_has_content or result.unpaywall_oa:
            available += 1
            logger.info(f"  📋 Available (dry run) — OpenAlex: {result.openalex_has_content}, Unpaywall: {result.unpaywall_oa}")
        else:
            manual_needed += 1
            logger.info(f"  ❌ {result.error}")

    # Summary
    logger.info(f"\n{'=' * 60}")
    logger.info(f"RESULTS SUMMARY")
    logger.info(f"{'=' * 60}")
    logger.info(f"Downloaded:     {downloaded}/{total}")
    if args.dry_run:
        logger.info(f"Available:      {available}/{total}")
    logger.info(f"Manual needed:  {manual_needed}/{total}")
    logger.info(f"")

    # Group manual-needed by type
    manual_journals = [r for r in results if r.error and r.paper_type == "journal"]
    manual_books = [r for r in results if r.error and r.paper_type in ("book", "book_chapter")]

    if manual_books:
        logger.info(f"BOOKS (no DOI — search Academia.edu or university library):")
        for r in manual_books:
            logger.info(f"  📚 {r.author} — {r.theory}")

    if manual_journals:
        logger.info(f"\nJOURNALS needing manual acquisition:")
        for r in manual_journals:
            logger.info(f"  📄 {r.author} ({r.doi}) — {r.theory}")

    # Save report
    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "mode": "dry_run" if args.dry_run else "live",
        "total": total,
        "downloaded": downloaded,
        "available_not_downloaded": available,
        "manual_needed": manual_needed,
        "results": [asdict(r) for r in results],
    }
    with open(REPORT_FILE, "w") as f:
        json.dump(report, f, indent=2)
    logger.info(f"\nReport saved to {REPORT_FILE}")

    # Generate Elicit prompt for manual papers
    manual_dois = [r.doi for r in results if r.error and r.doi]
    if manual_dois:
        elicit_file = Path("data/acquisition/elicit_batch_dois.txt")
        with open(elicit_file, "w") as f:
            f.write("# Paste these DOIs into Elicit for batch lookup:\n\n")
            for doi in manual_dois:
                f.write(f"{doi}\n")
        logger.info(f"Elicit batch DOI list saved to {elicit_file}")


if __name__ == "__main__":
    main()
