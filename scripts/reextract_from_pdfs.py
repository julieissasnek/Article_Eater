#!/usr/bin/env python3
"""
reextract_from_pdfs.py — Re-extract weak/empty fields from PDFs using Gemini multimodal
=======================================================================================

This script:
1. Reads data/pdf_doi_mapping.json mapping DOI → PDF path
2. For each DOI with an existing extraction JSON and a PDF:
   - Reads the existing extraction
   - Uses Gemini 2.5 Flash multimodal to fill in empty/weak fields:
     * effect_size, sample_size, stimulus_description, methodology
     * figure references, limitations, author affiliations
3. MERGES results (never overwrites existing good data)
4. Saves back to data/extractions/{DOI}.json

Key features:
- Supports --dry-run, --limit N, --doi SPECIFIC_DOI, --parallel N
- Resume support via data/reextraction_progress.json
- Configurable --zotero-base for different machine file paths
- Reports coverage improvement metrics
- Uses same extraction schema as existing code

Usage (run on YOUR local machine, not sandbox):
  python scripts/reextract_from_pdfs.py \\
    --pdf-mapping data/pdf_doi_mapping.json \\
    --zotero-base /Users/davidusa/Zotero/storage

  python scripts/reextract_from_pdfs.py --limit 10  # Try 10 DOIs first
  python scripts/reextract_from_pdfs.py --dry-run   # Show plan
  python scripts/reextract_from_pdfs.py --parallel 4  # 4 workers
  python scripts/reextract_from_pdfs.py --doi 10.1016/j.example.2020.001  # Specific DOI

Author: Claude (AI Assistant for David Kirsh)
Date: 2026-03-05
"""

import json
import logging
import sys
import argparse
from pathlib import Path
from typing import Dict, Optional, Any, List, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
import base64
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# Gemini imports
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [REEXTRACT] %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXTRACTIONS_DIR = PROJECT_ROOT / "data" / "extractions"
PROGRESS_FILE = PROJECT_ROOT / "data" / "reextraction_progress.json"

# Gemini setup
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_VISION_TIMEOUT = 60  # seconds


@dataclass
class ReextractionTask:
    """Track a single reextraction task."""
    doi: str
    pdf_path: str
    status: str = "pending"  # pending | processing | completed | failed
    error: Optional[str] = None
    fields_filled: List[str] = None
    timestamp: str = None

    def __post_init__(self):
        if self.fields_filled is None:
            self.fields_filled = []
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class GeminiExtractor:
    """Use Gemini 2.5 Flash to extract missing fields from PDF."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini client."""
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai not installed. Install with: pip install google-generativeai")

        key = api_key or os.environ.get("GEMINI_API_KEY")
        if not key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        genai.configure(api_key=key)
        self.model = genai.GenerativeModel(GEMINI_MODEL)

    def extract_fields(self, pdf_path: Path, existing_extraction: Dict) -> Dict[str, Any]:
        """
        Use Gemini to extract specific missing fields from PDF.

        Returns dict of newly extracted fields to merge.
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        try:
            pdf_data = self._load_pdf_as_base64(pdf_path)
        except Exception as e:
            logger.error(f"Failed to load PDF {pdf_path.name}: {e}")
            raise

        # Determine which fields are missing/weak
        fields_to_extract = self._identify_missing_fields(existing_extraction)

        if not fields_to_extract:
            logger.info(f"No missing fields in {pdf_path.name}")
            return {}

        # Build extraction prompt
        prompt = self._build_extraction_prompt(existing_extraction, fields_to_extract)

        try:
            # Call Gemini with PDF
            message = self.model.generate_content(
                [
                    prompt,
                    {
                        "mime_type": "application/pdf",
                        "data": pdf_data,
                    }
                ],
                request_options={"timeout": GEMINI_VISION_TIMEOUT}
            )

            # Parse response
            result = self._parse_gemini_response(message.text)
            result["_fields_filled"] = fields_to_extract
            return result

        except Exception as e:
            logger.error(f"Gemini extraction failed: {e}")
            raise

    def _load_pdf_as_base64(self, pdf_path: Path) -> str:
        """Load PDF and encode as base64."""
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        return base64.standard_b64encode(pdf_bytes).decode("utf-8")

    def _identify_missing_fields(self, extraction: Dict) -> List[str]:
        """Identify which fields are missing or weak."""
        fields_to_check = [
            ("effect_size", "effect_sizes"),
            ("sample_size", "participants"),
            ("stimulus_description", "stimuli_or_exposures"),
            ("methodology", "design_type"),
            ("figure_references", "figures"),
            ("limitations", "limitations"),
            ("author_affiliations", "authors_structured"),
        ]

        missing = []
        for field, alt_field in fields_to_check:
            val = extraction.get(field)
            alt_val = extraction.get(alt_field)

            # Check if weak or missing
            if not val or (isinstance(val, (list, dict)) and not val):
                # Try alternative field
                if not alt_val or (isinstance(alt_val, (list, dict)) and len(alt_val) == 0):
                    missing.append(field)

        return missing

    def _build_extraction_prompt(self, extraction: Dict, fields: List[str]) -> str:
        """Build the extraction prompt for Gemini."""
        title = extraction.get("title", "Unknown")
        doi = extraction.get("doi", "Unknown")

        prompt = f"""You are extracting scientific article metadata. Focus ONLY on these fields:
{', '.join(fields)}

Article: {title} (DOI: {doi})

Current partial extraction:
- Article Type: {extraction.get('article_type', 'unknown')}
- Found {extraction.get('n_findings', 0)} findings so far
- Has methodology: {bool(extraction.get('design_type'))}

Please extract from the PDF and provide JSON with ONLY these fields (use null if not found):
{{
  "effect_size": "string or null - quantitative effect magnitude",
  "effect_size_unit": "string or null - unit of measurement",
  "sample_size": "int or null - N of main sample",
  "stimulus_description": "string or null - detailed description of stimuli/exposures",
  "methodology": "string or null - 2-3 sentence summary of research design",
  "figure_references": ["list of figure numbers and captions if extractable"],
  "limitations": ["list of acknowledged limitations"],
  "author_affiliations": ["Author Name (Institution, Country)"]
}}

Be concise. Return ONLY valid JSON, no other text.
"""
        return prompt

    def _parse_gemini_response(self, text: str) -> Dict:
        """Parse JSON response from Gemini."""
        # Extract JSON from response
        try:
            # Try direct parse
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON block
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(text[start:end])
                except json.JSONDecodeError:
                    pass

        logger.warning("Could not parse Gemini response as JSON")
        return {}


def load_pdf_mapping(mapping_file: Path) -> Dict[str, str]:
    """Load the PDF-DOI mapping."""
    if not mapping_file.exists():
        logger.error(f"Mapping file not found: {mapping_file}")
        return {}

    with open(mapping_file) as f:
        data = json.load(f)

    mapping = {}
    for doi, info in data.get("mapping", {}).items():
        mapping[doi] = info["pdf_path"]

    return mapping


def load_extraction(doi: str) -> Optional[Dict]:
    """Load existing extraction JSON."""
    # Convert DOI to filename (e.g., "10.1002/ad.2031" -> "10.1002_ad.2031")
    filename = doi.replace("/", "_", 1)
    filepath = EXTRACTIONS_DIR / f"{filename}.json"

    if not filepath.exists():
        return None

    try:
        with open(filepath) as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load extraction for {doi}: {e}")
        return None


def save_extraction(doi: str, extraction: Dict) -> bool:
    """Save modified extraction JSON."""
    filename = doi.replace("/", "_", 1)
    filepath = EXTRACTIONS_DIR / f"{filename}.json"

    try:
        EXTRACTIONS_DIR.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(extraction, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save extraction for {doi}: {e}")
        return False


def merge_extractions(existing: Dict, new_fields: Dict) -> Tuple[Dict, List[str]]:
    """
    Merge new fields into existing extraction, never overwriting good data.

    Returns:
        (merged_extraction, list_of_fields_updated)
    """
    merged = existing.copy()
    updated = []
    tracked_fields = new_fields.pop("_fields_filled", [])

    for field in tracked_fields:
        if field in new_fields and new_fields[field]:
            old_val = existing.get(field)

            # Only update if old is missing/empty
            if not old_val or (isinstance(old_val, (list, dict)) and len(old_val) == 0):
                merged[field] = new_fields[field]
                updated.append(field)
            else:
                logger.debug(f"  Field {field} already has value, skipping")

    return merged, updated


def reextract_single_doi(
    doi: str,
    pdf_mapping: Dict,
    extractor: Optional[GeminiExtractor] = None,
    dry_run: bool = False,
) -> ReextractionTask:
    """Reextract a single DOI."""
    task = ReextractionTask(doi=doi, pdf_path="")

    # Check PDF exists
    if doi not in pdf_mapping:
        task.status = "failed"
        task.error = "No PDF mapping found"
        return task

    pdf_path = Path(pdf_mapping[doi])
    task.pdf_path = str(pdf_path)

    if not pdf_path.exists():
        task.status = "failed"
        task.error = f"PDF file not found: {pdf_path}"
        logger.warning(f"  PDF not found: {pdf_path}")
        return task

    # Load existing extraction
    extraction = load_extraction(doi)
    if not extraction:
        task.status = "failed"
        task.error = "No existing extraction found"
        return task

    if dry_run:
        task.status = "completed"
        task.fields_filled = ["(dry-run mode)"]
        return task

    # Call Gemini
    if not extractor:
        task.status = "failed"
        task.error = "No Gemini extractor available"
        return task

    try:
        task.status = "processing"
        new_fields = extractor.extract_fields(pdf_path, extraction)

        # Merge
        merged, updated = merge_extractions(extraction, new_fields)

        # Add metadata
        merged["reextraction_at"] = datetime.now(timezone.utc).isoformat()
        merged["reextraction_model"] = GEMINI_MODEL
        merged["reextraction_fields"] = updated

        # Save
        if save_extraction(doi, merged):
            task.status = "completed"
            task.fields_filled = updated
            logger.info(f"  ✓ Updated fields: {', '.join(updated)}")
        else:
            task.status = "failed"
            task.error = "Failed to save extraction"

    except Exception as e:
        task.status = "failed"
        task.error = str(e)
        logger.error(f"  ✗ {e}")

    return task


def load_progress() -> Dict[str, Any]:
    """Load reextraction progress."""
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE) as f:
                return json.load(f)
        except Exception:
            pass

    return {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_tasks": [],
        "failed_dois": [],
    }


def save_progress(progress: Dict):
    """Save reextraction progress."""
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Re-extract weak fields from PDFs using Gemini multimodal"
    )
    parser.add_argument(
        "--pdf-mapping",
        type=Path,
        default=PROJECT_ROOT / "data" / "pdf_doi_mapping.json",
        help="Path to PDF-DOI mapping JSON",
    )
    parser.add_argument(
        "--zotero-base",
        type=str,
        default=None,
        help="Base path for Zotero files (e.g., /Users/you/Zotero/storage)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit reextraction to N DOIs (0 = all)",
    )
    parser.add_argument(
        "--doi",
        type=str,
        default=None,
        help="Reextract only this specific DOI",
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=1,
        help="Number of parallel workers",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be reextracted",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from progress file",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    if not GEMINI_AVAILABLE and not args.dry_run:
        logger.error("google-generativeai not installed. Install with:")
        logger.error("  pip install google-generativeai")
        return 1

    logger.info("=" * 70)
    logger.info("PDF Reextraction Pipeline (Gemini 2.5 Flash Multimodal)")
    logger.info("=" * 70)

    # Load PDF mapping
    logger.info(f"\n📂 Loading PDF mapping from {args.pdf_mapping}...")
    pdf_mapping = load_pdf_mapping(args.pdf_mapping)
    if not pdf_mapping:
        logger.error("No PDF mappings loaded")
        return 1
    logger.info(f"  Found mappings for {len(pdf_mapping)} DOIs")

    # Adjust paths if Zotero base provided
    if args.zotero_base:
        logger.info(f"  Remapping paths to base: {args.zotero_base}")
        zotero_base = Path(args.zotero_base)
        adjusted = {}
        for doi, pdf_path in pdf_mapping.items():
            old_path = Path(pdf_path)
            # Replace Zotero root with new base
            relative = old_path.relative_to(old_path.parts[0])  # Approximate
            new_path = zotero_base / relative.parts[-2] / relative.parts[-1]
            adjusted[doi] = str(new_path)
        pdf_mapping = adjusted

    # Determine which DOIs to reextract
    dois_to_reextract = []

    if args.doi:
        dois_to_reextract = [args.doi]
    else:
        dois_to_reextract = list(pdf_mapping.keys())

    if args.limit > 0:
        dois_to_reextract = dois_to_reextract[:args.limit]

    logger.info(f"\n🔄 Preparing to reextract {len(dois_to_reextract)} DOI(s)")

    # Load progress if resuming
    progress = load_progress() if args.resume else {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_tasks": [],
        "failed_dois": [],
    }

    # Filter out already completed
    if args.resume:
        completed_dois = {t["doi"] for t in progress["completed_tasks"]}
        dois_to_reextract = [d for d in dois_to_reextract if d not in completed_dois]
        logger.info(f"  Resuming: {len(dois_to_reextract)} DOIs remaining")

    if not dois_to_reextract:
        logger.info("  No DOIs to process")
        return 0

    # Initialize Gemini if not dry-run
    extractor = None
    if not args.dry_run:
        try:
            logger.info("\n🤖 Initializing Gemini 2.5 Flash...")
            extractor = GeminiExtractor()
            logger.info("  ✓ Connected to Gemini API")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            return 1

    # Process DOIs
    logger.info(f"\n{'=' * 70}")
    logger.info(f"Processing {len(dois_to_reextract)} DOI(s) with {args.parallel} worker(s)")
    logger.info(f"{'=' * 70}\n")

    completed = 0
    failed = 0

    if args.parallel > 1:
        # Parallel processing
        with ThreadPoolExecutor(max_workers=args.parallel) as executor:
            futures = {
                executor.submit(reextract_single_doi, doi, pdf_mapping, extractor, args.dry_run): doi
                for doi in dois_to_reextract
            }

            for future in as_completed(futures):
                doi = futures[future]
                try:
                    task = future.result()
                    if task.status == "completed":
                        completed += 1
                        progress["completed_tasks"].append(asdict(task))
                        logger.info(f"✓ {doi}")
                    else:
                        failed += 1
                        progress["failed_dois"].append(doi)
                        logger.error(f"✗ {doi}: {task.error}")
                except Exception as e:
                    failed += 1
                    progress["failed_dois"].append(doi)
                    logger.error(f"✗ {doi}: {e}")

                if (completed + failed) % 10 == 0:
                    save_progress(progress)

    else:
        # Sequential processing
        for i, doi in enumerate(dois_to_reextract, 1):
            logger.info(f"[{i}/{len(dois_to_reextract)}] {doi}")
            task = reextract_single_doi(doi, pdf_mapping, extractor, args.dry_run)

            if task.status == "completed":
                completed += 1
                progress["completed_tasks"].append(asdict(task))
            else:
                failed += 1
                progress["failed_dois"].append(doi)

            if i % 5 == 0:
                save_progress(progress)

    # Summary
    logger.info(f"\n{'=' * 70}")
    logger.info("REEXTRACTION SUMMARY")
    logger.info(f"{'=' * 70}")
    logger.info(f"  Completed:  {completed}")
    logger.info(f"  Failed:     {failed}")
    logger.info(f"  Success rate: {100.0 * completed / (completed + failed):.1f}%" if (completed + failed) > 0 else "  N/A")

    # Save final progress
    progress["completed_at"] = datetime.now(timezone.utc).isoformat()
    save_progress(progress)
    logger.info(f"\n  Progress saved to: {PROGRESS_FILE}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
