#!/usr/bin/env python3
"""
DOI Mapping Verifier
====================
Reads page 1 of each PDF, extracts the title, and cross-checks against the
BibTeX-derived DOI mapping. Uses three verification sources:

1. PDF first-page title vs. BibTeX filename title
2. DOI printed in the PDF vs. claimed DOI
3. CrossRef API title lookup (optional, rate-limited)

Outputs a verified mapping with confidence scores.

Usage:
    python3 scripts/verify_doi_mapping.py [--limit N] [--start-at DOI] [--crossref]
    python3 scripts/verify_doi_mapping.py --status
"""

import json
import os
import re
import sys
import argparse
import time
from pathlib import Path
from difflib import SequenceMatcher

try:
    import pdfplumber
except ImportError:
    print("Installing pdfplumber...", file=sys.stderr)
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pdfplumber", "--break-system-packages", "-q"])
    import pdfplumber

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MAPPING_FILE = PROJECT_ROOT / "data" / "pdf_doi_mapping_CORRECTED.json"
VERIFIED_FILE = PROJECT_ROOT / "data" / "pdf_doi_mapping_VERIFIED.json"
REPORT_FILE = PROJECT_ROOT / "data" / "doi_verification_report.json"


def extract_page1_text(pdf_path: str, max_pages: int = 2) -> str:
    """Extract text from first 1-2 pages of a PDF."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            parts = []
            for i, page in enumerate(pdf.pages[:max_pages]):
                txt = page.extract_text()
                if txt:
                    parts.append(txt)
            return "\n".join(parts)
    except Exception as e:
        return f"ERROR: {e}"


def extract_doi_from_text(text: str) -> str:
    """Find a DOI in the extracted text."""
    # Match DOI patterns: 10.NNNN/...
    patterns = [
        r'(?:doi[:\s]*|DOI[:\s]*|https?://doi\.org/)?(10\.\d{4,}/[^\s,;"\'\]}>]+)',
        r'(10\.\d{4,}/\S+?)(?:\s|$|,|;)',
    ]
    for pat in patterns:
        matches = re.findall(pat, text[:3000])  # Only search first ~3000 chars
        for m in matches:
            # Clean trailing punctuation
            m = m.rstrip('.')
            if len(m) > 10:  # Reasonable DOI length
                return m
    return None


def title_from_filename(filename: str) -> str:
    """Extract expected title from Zotero-style filename: 'Author - Year - Title.pdf'"""
    parts = filename.replace(".pdf", "").split(" - ")
    if len(parts) >= 3:
        return " ".join(parts[2:]).strip()
    elif len(parts) == 2:
        return parts[1].strip()
    return filename.replace(".pdf", "")


def extract_title_from_text(text: str) -> str:
    """Heuristic: the title is usually the first substantial line of text."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    # Skip very short lines (page numbers, headers) and journal names
    candidates = []
    for line in lines[:15]:
        # Skip lines that look like journal headers, page numbers, DOIs
        if re.match(r'^\d+$', line):  # page number
            continue
        if re.match(r'^(Volume|Vol\.|Issue|No\.|pp\.|Pages)', line, re.I):
            continue
        if 'doi' in line.lower() or '10.' in line[:5]:
            continue
        if len(line) > 20:
            candidates.append(line)

    if candidates:
        # The longest of the first few candidates is likely the title
        return max(candidates[:3], key=len)
    return ""


def title_similarity(t1: str, t2: str) -> float:
    """Fuzzy string similarity between two titles."""
    t1 = re.sub(r'[^a-z0-9\s]', '', t1.lower())
    t2 = re.sub(r'[^a-z0-9\s]', '', t2.lower())
    return SequenceMatcher(None, t1, t2).ratio()


def crossref_lookup(doi: str) -> dict:
    """Look up a DOI on CrossRef. Returns {title, doi} or None."""
    try:
        import urllib.request
        url = f"https://api.crossref.org/works/{doi}"
        req = urllib.request.Request(url, headers={"User-Agent": "ArticleEater/1.0 (mailto:dkirsh@gmail.com)"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            msg = data.get("message", {})
            title = msg.get("title", [""])[0]
            return {"title": title, "doi": doi, "source": "crossref"}
    except Exception as e:
        return None


def verify_single(doi: str, info: dict, use_crossref: bool = False) -> dict:
    """Verify a single DOI-PDF pair."""
    pdf_path = info.get("pdf_path", "")
    filename = os.path.basename(pdf_path)

    result = {
        "doi": doi,
        "pdf_path": pdf_path,
        "filename_title": title_from_filename(filename),
        "pdf_title": None,
        "pdf_doi": None,
        "crossref_title": None,
        "title_similarity": 0.0,
        "doi_match": None,
        "confidence": "unverified",
        "verified": False,
        "notes": []
    }

    if not os.path.exists(pdf_path):
        result["notes"].append("PDF file not found")
        result["confidence"] = "missing"
        return result

    # Extract text from page 1
    text = extract_page1_text(pdf_path)
    if text.startswith("ERROR:"):
        result["notes"].append(f"PDF read error: {text}")
        result["confidence"] = "error"
        return result

    # Extract title from PDF text
    pdf_title = extract_title_from_text(text)
    result["pdf_title"] = pdf_title

    # Extract DOI from PDF text
    pdf_doi = extract_doi_from_text(text)
    result["pdf_doi"] = pdf_doi

    # Compare DOI
    if pdf_doi:
        doi_clean = doi.lower().strip()
        pdf_doi_clean = pdf_doi.lower().strip()
        result["doi_match"] = doi_clean == pdf_doi_clean or doi_clean in pdf_doi_clean or pdf_doi_clean in doi_clean

    # Compare titles
    if pdf_title and result["filename_title"]:
        sim = title_similarity(pdf_title, result["filename_title"])
        result["title_similarity"] = round(sim, 3)

    # CrossRef check
    if use_crossref:
        cr = crossref_lookup(doi)
        if cr:
            result["crossref_title"] = cr["title"]
            if pdf_title and cr["title"]:
                cr_sim = title_similarity(pdf_title, cr["title"])
                result["notes"].append(f"CrossRef title similarity: {cr_sim:.3f}")

    # Determine confidence
    doi_ok = result["doi_match"] is True
    title_ok = result["title_similarity"] > 0.5

    if doi_ok and title_ok:
        result["confidence"] = "high"
        result["verified"] = True
    elif doi_ok or title_ok:
        result["confidence"] = "medium"
        result["verified"] = True
    elif result["doi_match"] is False:
        result["confidence"] = "mismatch"
        result["verified"] = False
        result["notes"].append("DOI in PDF does not match claimed DOI")
    elif result["title_similarity"] < 0.3 and result["title_similarity"] > 0:
        result["confidence"] = "likely_mismatch"
        result["verified"] = False
        result["notes"].append("Title similarity very low")
    else:
        result["confidence"] = "uncertain"
        result["verified"] = False

    return result


def main():
    parser = argparse.ArgumentParser(description="Verify DOI-PDF mapping")
    parser.add_argument("--limit", type=int, default=0, help="Max papers to verify (0=all)")
    parser.add_argument("--start-at", type=str, default=None, help="Start at this DOI")
    parser.add_argument("--crossref", action="store_true", help="Also check CrossRef (slower)")
    parser.add_argument("--status", action="store_true", help="Show verification status")
    args = parser.parse_args()

    # Load mapping
    with open(MAPPING_FILE) as f:
        data = json.load(f)
    mapping = data["mapping"]

    # Load existing verification results
    existing = {}
    if REPORT_FILE.exists():
        with open(REPORT_FILE) as f:
            existing = {r["doi"]: r for r in json.load(f)}

    if args.status:
        total = len(mapping)
        verified = sum(1 for r in existing.values() if r.get("verified"))
        mismatches = sum(1 for r in existing.values() if r.get("confidence") in ("mismatch", "likely_mismatch"))
        uncertain = sum(1 for r in existing.values() if r.get("confidence") == "uncertain")
        print(f"Verification status:")
        print(f"  Total DOIs:     {total}")
        print(f"  Verified:       {len(existing)} checked, {verified} confirmed")
        print(f"  Mismatches:     {mismatches}")
        print(f"  Uncertain:      {uncertain}")
        print(f"  Unchecked:      {total - len(existing)}")
        return

    # Determine which DOIs to verify
    dois = sorted(mapping.keys())
    if args.start_at:
        try:
            idx = dois.index(args.start_at)
            dois = dois[idx:]
        except ValueError:
            print(f"DOI {args.start_at} not found in mapping")
            return

    # Skip already verified
    dois = [d for d in dois if d not in existing]

    if args.limit:
        dois = dois[:args.limit]

    print(f"Verifying {len(dois)} DOIs...")
    results = list(existing.values())

    for i, doi in enumerate(dois):
        info = mapping[doi]
        result = verify_single(doi, info, use_crossref=args.crossref)
        results.append(result)

        # Progress
        status_char = "✓" if result["verified"] else ("✗" if "mismatch" in result["confidence"] else "?")
        conf = result["confidence"]
        sim = result["title_similarity"]
        doi_match = "DOI✓" if result["doi_match"] else ("DOI✗" if result["doi_match"] is False else "DOI?")
        print(f"  [{i+1}/{len(dois)}] {status_char} {doi[:35]:35s} {conf:15s} title_sim={sim:.2f} {doi_match}")

        if args.crossref:
            time.sleep(0.5)  # Rate limit

    # Save results
    with open(REPORT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    # Summary
    verified = sum(1 for r in results if r["verified"])
    mismatches = [r for r in results if r["confidence"] in ("mismatch", "likely_mismatch")]
    uncertain = sum(1 for r in results if r["confidence"] == "uncertain")

    print(f"\nResults: {verified} verified, {len(mismatches)} mismatches, {uncertain} uncertain")
    if mismatches:
        print("\nMISMATCHES:")
        for m in mismatches:
            print(f"  {m['doi']}")
            print(f"    Expected: {m['filename_title'][:60]}")
            print(f"    Found:    {m['pdf_title'][:60] if m['pdf_title'] else 'N/A'}")
            if m['pdf_doi']:
                print(f"    PDF DOI:  {m['pdf_doi']}")

    # Build verified mapping
    verified_mapping = {}
    for r in results:
        if r["verified"]:
            verified_mapping[r["doi"]] = {
                "pdf_path": r["pdf_path"],
                "confidence": r["confidence"],
                "title_similarity": r["title_similarity"]
            }

    with open(VERIFIED_FILE, "w") as f:
        json.dump({
            "metadata": {
                "verified_count": len(verified_mapping),
                "total_checked": len(results),
                "mismatches": len(mismatches),
                "last_run": time.strftime("%Y-%m-%dT%H:%M:%S")
            },
            "mapping": verified_mapping
        }, f, indent=2)

    print(f"\nVerified mapping saved: {len(verified_mapping)} DOIs → {VERIFIED_FILE}")


if __name__ == "__main__":
    main()
