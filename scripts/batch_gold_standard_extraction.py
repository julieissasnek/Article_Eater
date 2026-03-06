#!/usr/bin/env python3
"""
Batch Gold Standard Extraction Script
======================================
Reads PDFs from the corrected DOI mapping and extracts findings.
Designed to be called by a Cowork scheduled task — each invocation
processes BATCH_SIZE papers that haven't been extracted yet.

Usage:
    python3 scripts/batch_gold_standard_extraction.py [--batch N] [--status]

Output:
    data/gold_standard/batch_<doi_slug>.json per paper
    data/gold_standard/batch_progress.json (tracking file)
"""

import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GS_DIR = PROJECT_ROOT / "data" / "gold_standard"
MAPPING_FILE = PROJECT_ROOT / "data" / "pdf_doi_mapping_CORRECTED.json"
PROGRESS_FILE = GS_DIR / "batch_progress.json"

DEFAULT_BATCH = 25


def doi_to_slug(doi: str) -> str:
    """Convert DOI to filesystem-safe slug."""
    return doi.replace("/", "_").replace(".", "_")


def load_progress() -> dict:
    """Load or initialize progress tracking."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {
        "started": datetime.now().isoformat(),
        "extracted": [],
        "failed": [],
        "skipped": [],
        "total_findings": 0,
        "last_run": None
    }


def save_progress(progress: dict):
    """Save progress tracking."""
    progress["last_run"] = datetime.now().isoformat()
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


def get_already_extracted() -> set:
    """Find DOIs that already have gold standard extractions."""
    extracted = set()
    for f in GS_DIR.glob("*.json"):
        if f.name in ("batch_progress.json", "comparison_report.json",
                       "gold_standard_papers.json", "unmatched_dois.json"):
            continue
        try:
            with open(f) as fh:
                data = json.load(fh)
                if isinstance(data, dict) and "doi" in data:
                    extracted.add(data["doi"])
        except (json.JSONDecodeError, KeyError):
            pass
    return extracted


def get_pending_dois(mapping: dict, already_done: set) -> list:
    """Get DOIs that still need extraction, sorted for deterministic ordering."""
    pending = []
    for doi, info in mapping.items():
        if doi in already_done:
            continue
        pdf_path = info.get("pdf_path", "") if isinstance(info, dict) else ""
        if pdf_path and os.path.exists(pdf_path):
            pending.append((doi, pdf_path))
    return sorted(pending, key=lambda x: x[0])


def show_status():
    """Print current extraction status."""
    with open(MAPPING_FILE) as f:
        data = json.load(f)
    mapping = data["mapping"]

    already_done = get_already_extracted()
    pending = get_pending_dois(mapping, already_done)
    progress = load_progress()

    print(f"=== Gold Standard Extraction Status ===")
    print(f"Total DOIs in mapping:     {len(mapping)}")
    print(f"Already extracted:         {len(already_done)}")
    print(f"Pending (with PDFs):       {len(pending)}")
    print(f"Failed:                    {len(progress.get('failed', []))}")
    print(f"Total findings extracted:  {progress.get('total_findings', 0)}")
    print(f"Last run:                  {progress.get('last_run', 'never')}")

    if pending:
        print(f"\nNext 5 papers to extract:")
        for doi, path in pending[:5]:
            fname = os.path.basename(path)[:60]
            print(f"  {doi} → {fname}")

    return len(pending)


def main():
    parser = argparse.ArgumentParser(description="Batch gold standard extraction")
    parser.add_argument("--batch", type=int, default=DEFAULT_BATCH,
                        help=f"Number of papers to process (default: {DEFAULT_BATCH})")
    parser.add_argument("--status", action="store_true",
                        help="Show status and exit")
    parser.add_argument("--list-next", type=int, default=0,
                        help="List next N papers to extract")
    args = parser.parse_args()

    if args.status:
        show_status()
        return

    # Load mapping
    with open(MAPPING_FILE) as f:
        data = json.load(f)
    mapping = data["mapping"]

    already_done = get_already_extracted()
    pending = get_pending_dois(mapping, already_done)

    if args.list_next > 0:
        for doi, path in pending[:args.list_next]:
            print(json.dumps({"doi": doi, "pdf_path": path}))
        return

    print(f"Papers pending: {len(pending)}, batch size: {args.batch}")
    batch = pending[:args.batch]

    if not batch:
        print("No papers to extract. All done!")
        return

    # Output the batch for the scheduled task to pick up
    batch_file = GS_DIR / "current_batch.json"
    with open(batch_file, "w") as f:
        json.dump([{"doi": doi, "pdf_path": path} for doi, path in batch], f, indent=2)

    print(f"Wrote {len(batch)} papers to {batch_file}")
    print("Ready for extraction by Cowork subagents.")


if __name__ == "__main__":
    main()
