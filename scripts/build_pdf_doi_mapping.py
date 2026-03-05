#!/usr/bin/env python3
"""
build_pdf_doi_mapping.py — Create DOI → PDF path mapping
========================================================

This script:
1. Parses all available bib files (Zotero main + HBE export)
2. Scans all PDF directories (Zotero files/, All_PDFs/, HBE_Zotero_export/files/)
3. For each of the 1,069 existing extraction DOIs, finds the corresponding PDF
4. Outputs data/pdf_doi_mapping.json mapping DOI → absolute PDF path
5. Reports coverage and identifies missing PDFs

Deduplication rule: if a DOI has multiple PDF copies, prefer Zotero main over others.

Usage:
  python scripts/build_pdf_doi_mapping.py
  python scripts/build_pdf_doi_mapping.py --dry-run
  python scripts/build_pdf_doi_mapping.py --verbose

Author: Claude (AI Assistant for David Kirsh)
Date: 2026-03-05
"""

import json
import logging
import sys
import argparse
from pathlib import Path
from typing import Dict, Optional, Set, Tuple
from datetime import datetime, timezone
import re

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [PDF_MAPPING] %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ZOTERO_ROOT = Path("/sessions/keen-busy-turing/mnt/REPOS/__Zotero whole bibliography")
COLLECTING_ROOT = Path("/sessions/keen-busy-turing/mnt/REPOS/_Collecting Articles")

ZOTERO_BIB = ZOTERO_ROOT / "__Zotero whole bibliography.bib"
ZOTERO_FILES = ZOTERO_ROOT / "files"

HBE_BIB = COLLECTING_ROOT / "HBE_Zotero_export" / "HBE_Zotero_export.bib"
HBE_FILES = COLLECTING_ROOT / "HBE_Zotero_export" / "files"

ALL_PDFS_DIR = COLLECTING_ROOT / "All_PDFs"

EXTRACTIONS_DIR = PROJECT_ROOT / "data" / "extractions"
OUTPUT_FILE = PROJECT_ROOT / "data" / "pdf_doi_mapping.json"


def normalize_doi(doi_str: Optional[str]) -> Optional[str]:
    """Normalize a DOI string for consistent matching."""
    if not doi_str:
        return None
    doi = doi_str.strip().lower()
    if doi.startswith("http://doi.org/"):
        doi = doi.replace("http://doi.org/", "")
    elif doi.startswith("https://doi.org/"):
        doi = doi.replace("https://doi.org/", "")
    return doi


def extract_doi_from_bib_entry(entry: Dict) -> Optional[str]:
    """Extract DOI from a BibTeX entry."""
    doi = entry.get("doi", "")
    if doi:
        return normalize_doi(doi)
    return None


def extract_files_from_bib_entry(entry: Dict) -> Optional[str]:
    """Extract file path from a BibTeX entry."""
    file_field = entry.get("file", "")
    if not file_field:
        return None

    # Zotero format: "description:path/to/file.pdf:filetype"
    # We want the path component
    parts = file_field.split(":")
    if len(parts) >= 2:
        # Return the middle part (the path)
        return parts[1].strip()
    return None


def parse_bib_file(bib_path: Path) -> Dict[str, Dict]:
    """Parse a BibTeX file and return dict of DOI -> entry data (simple regex-based parser)."""
    if not bib_path.exists():
        logger.warning(f"Bib file not found: {bib_path}")
        return {}

    try:
        with open(bib_path, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Failed to read {bib_path}: {e}")
        return {}

    doi_to_entry = {}

    # Simple regex-based BibTeX parser
    # Match @article{...}, @book{...}, etc.
    entry_pattern = r'@\w+\{[^}]*\}'
    entries = re.findall(entry_pattern, content, re.DOTALL)

    for entry_text in entries:
        entry_dict = {}

        # Extract DOI
        doi_match = re.search(r'doi\s*=\s*["\'{]([^}"\']*)[}"\']', entry_text, re.IGNORECASE)
        if doi_match:
            doi = normalize_doi(doi_match.group(1))
            if doi:
                entry_dict["doi"] = doi

        # Extract file path
        file_match = re.search(r'file\s*=\s*["\'{]([^}"\']*)[}"\']', entry_text, re.IGNORECASE)
        if file_match:
            file_path = file_match.group(1)
            # Zotero format: "description:path/to/file.pdf:filetype"
            parts = file_path.split(":")
            if len(parts) >= 2:
                entry_dict["file_path"] = parts[1].strip()

        # Extract title
        title_match = re.search(r'title\s*=\s*["\'{]([^}"\']*)[}"\']', entry_text, re.IGNORECASE)
        if title_match:
            entry_dict["title"] = title_match.group(1)

        if "doi" in entry_dict:
            doi = entry_dict["doi"]
            doi_to_entry[doi] = {
                "entry": entry_dict,
                "file_path": entry_dict.get("file_path"),
                "source": bib_path.name,
            }

    logger.debug(f"  Parsed {len(doi_to_entry)} DOIs from {bib_path.name}")
    return doi_to_entry


def scan_zotero_files() -> Dict[str, Path]:
    """Scan Zotero files/ directory and map PDFs by filename."""
    doi_to_path = {}

    if not ZOTERO_FILES.exists():
        logger.warning(f"Zotero files directory not found: {ZOTERO_FILES}")
        return doi_to_path

    # Zotero uses numbered folders like files/12345/
    for numbered_dir in ZOTERO_FILES.iterdir():
        if not numbered_dir.is_dir():
            continue

        pdfs = list(numbered_dir.glob("*.pdf"))
        if pdfs:
            # Usually one PDF per numbered folder
            pdf_path = pdfs[0]
            logger.debug(f"Found Zotero PDF: {pdf_path}")
            # Try to extract DOI from filename or use as placeholder
            doi_to_path[str(pdf_path)] = pdf_path

    return doi_to_path


def scan_hbe_files() -> Dict[str, Path]:
    """Scan HBE Zotero export files/ directory."""
    doi_to_path = {}

    if not HBE_FILES.exists():
        logger.warning(f"HBE files directory not found: {HBE_FILES}")
        return doi_to_path

    for numbered_dir in HBE_FILES.iterdir():
        if not numbered_dir.is_dir():
            continue

        pdfs = list(numbered_dir.glob("*.pdf"))
        if pdfs:
            pdf_path = pdfs[0]
            logger.debug(f"Found HBE PDF: {pdf_path}")
            doi_to_path[str(pdf_path)] = pdf_path

    return doi_to_path


def scan_all_pdfs_dir() -> Dict[str, Path]:
    """Scan All_PDFs directory (author-title named PDFs)."""
    doi_to_path = {}

    if not ALL_PDFS_DIR.exists():
        logger.warning(f"All_PDFs directory not found: {ALL_PDFS_DIR}")
        return doi_to_path

    pdfs = list(ALL_PDFS_DIR.glob("*.pdf"))
    logger.info(f"Found {len(pdfs)} PDFs in All_PDFs/")

    for pdf_path in pdfs:
        logger.debug(f"Found PDF: {pdf_path.name}")
        doi_to_path[str(pdf_path)] = pdf_path

    return doi_to_path


def build_mapping(dry_run: bool = False, verbose: bool = False) -> Tuple[Dict, Dict]:
    """
    Build the complete DOI -> PDF mapping.

    Returns:
        (mapping dict, stats dict)
    """
    if verbose:
        logger.setLevel(logging.DEBUG)

    logger.info("=" * 70)
    logger.info("Building DOI → PDF Mapping")
    logger.info("=" * 70)

    # Step 1: Parse all bib files
    logger.info("\n📖 Parsing BibTeX files...")
    zotero_bib_data = parse_bib_file(ZOTERO_BIB)
    logger.info(f"  Zotero main:    {len(zotero_bib_data)} DOIs")

    hbe_bib_data = parse_bib_file(HBE_BIB)
    logger.info(f"  HBE export:     {len(hbe_bib_data)} DOIs")

    # Merge, preferring Zotero main
    all_bib_data = {**hbe_bib_data, **zotero_bib_data}
    logger.info(f"  Total unique:   {len(all_bib_data)} DOIs")

    # Step 2: Get list of extraction DOIs
    logger.info("\n📂 Scanning extractions directory...")
    extraction_dois = set()
    if EXTRACTIONS_DIR.exists():
        for json_file in EXTRACTIONS_DIR.glob("*.json"):
            stem = json_file.stem
            # Convert filename to DOI (e.g., "10.1002_ad.2031" -> "10.1002/ad.2031")
            doi = stem.replace("_", "/", 1)
            extraction_dois.add(doi)

    logger.info(f"  Found {len(extraction_dois)} extraction JSONs")

    # Step 3: Scan PDF directories
    logger.info("\n🔍 Scanning PDF directories...")

    # Build inverse mapping: PDF file path -> full path
    all_pdfs_by_name = {}

    # Scan All_PDFs first (fastest, named by author-title)
    all_pdfs_data = scan_all_pdfs_dir()
    for pdf_path in all_pdfs_data.values():
        all_pdfs_by_name[pdf_path.name] = pdf_path
    logger.info(f"  All_PDFs:       {len(all_pdfs_by_name)} PDFs")

    # Scan HBE files (numbered folders)
    hbe_pdfs_data = scan_hbe_files()
    logger.info(f"  HBE files:      {len(hbe_pdfs_data)} PDFs")

    # Scan Zotero files (numbered folders, priority)
    zotero_pdfs_data = scan_zotero_files()
    logger.info(f"  Zotero files:   {len(zotero_pdfs_data)} PDFs")

    # Step 4: Build mapping for extraction DOIs
    logger.info("\n🔗 Matching DOIs to PDFs...")
    mapping = {}
    matched = 0
    missing = []

    for doi in sorted(extraction_dois):
        bib_entry = all_bib_data.get(doi)
        pdf_path = None
        source = None

        if bib_entry and bib_entry.get("file_path"):
            # Try to resolve file path from bib
            file_rel_path = bib_entry["file_path"]

            # Try relative to Zotero root first
            candidate = ZOTERO_ROOT / file_rel_path
            if candidate.exists():
                pdf_path = candidate
                source = "Zotero (bib file path)"
            else:
                # Try relative to HBE root
                candidate = COLLECTING_ROOT / "HBE_Zotero_export" / file_rel_path
                if candidate.exists():
                    pdf_path = candidate
                    source = "HBE (bib file path)"

        # If not found via bib, try other strategies
        if not pdf_path:
            # Look in Zotero files/ by searching all PDFs
            for zotero_pdf in zotero_pdfs_data.values():
                if zotero_pdf.exists():
                    pdf_path = zotero_pdf
                    source = "Zotero (numbered search)"
                    break

        if not pdf_path:
            # Look in HBE files/
            for hbe_pdf in hbe_pdfs_data.values():
                if hbe_pdf.exists():
                    pdf_path = hbe_pdf
                    source = "HBE (numbered search)"
                    break

        # Try by name in All_PDFs (slower, but catches some)
        if not pdf_path:
            # Build query from bib entry
            if bib_entry:
                title = bib_entry.get("entry", {}).get("title", "").strip()
                if title:
                    # Try to find a PDF with matching title words
                    title_words = title[:30].lower()
                    for pdf_name, pdf_full_path in all_pdfs_by_name.items():
                        if title_words in pdf_name.lower():
                            pdf_path = pdf_full_path
                            source = f"All_PDFs (title match: {pdf_name[:40]}...)"
                            break

        if pdf_path:
            mapping[doi] = {
                "pdf_path": str(pdf_path.resolve()),
                "source": source,
            }
            matched += 1
        else:
            missing.append(doi)

    logger.info(f"  ✓ Matched: {matched}/{len(extraction_dois)}")
    logger.info(f"  ✗ Missing: {len(missing)}/{len(extraction_dois)}")

    # Report missing DOIs
    if missing and len(missing) <= 20:
        logger.info("\n  Missing DOIs:")
        for doi in missing[:20]:
            logger.info(f"    - {doi}")
        if len(missing) > 20:
            logger.info(f"    ... and {len(missing) - 20} more")

    # Step 5: Write output
    stats = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_extractions": len(extraction_dois),
        "mapped": matched,
        "missing": len(missing),
        "coverage_percent": round(100.0 * matched / len(extraction_dois), 1) if extraction_dois else 0,
        "sources": {
            "zotero_main_bib": len(zotero_bib_data),
            "hbe_export_bib": len(hbe_bib_data),
            "all_pdfs_dir": len(all_pdfs_by_name),
            "hbe_files_dir": len(hbe_pdfs_data),
            "zotero_files_dir": len(zotero_pdfs_data),
        },
        "missing_dois": missing,
    }

    if not dry_run:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w") as f:
            json.dump({
                "mapping": mapping,
                "stats": stats,
            }, f, indent=2)
        logger.info(f"\n✅ Output saved to: {OUTPUT_FILE}")
    else:
        logger.info(f"\n[DRY RUN] Would save to: {OUTPUT_FILE}")

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("SUMMARY")
    logger.info("=" * 70)
    logger.info(f"  Total extractions:     {stats['total_extractions']}")
    logger.info(f"  Mapped:                {stats['mapped']}")
    logger.info(f"  Missing:               {stats['missing']}")
    logger.info(f"  Coverage:              {stats['coverage_percent']}%")

    return mapping, stats


def main():
    parser = argparse.ArgumentParser(
        description="Build DOI -> PDF path mapping from all sources"
    )
    parser.add_argument("--dry-run", action="store_true", help="Don't write output file")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    try:
        mapping, stats = build_mapping(dry_run=args.dry_run, verbose=args.verbose)
        return 0
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
