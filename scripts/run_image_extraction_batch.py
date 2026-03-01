#!/usr/bin/env python3
"""Batch image extraction orchestration for HIGH-priority articles.

Orchestrates extraction of images from 56 HIGH-priority articles identified by
AG's figure scanner. Uses existing extract_pdf_images.py infrastructure.

Date: 2026-02-28
Version: V1.0

Usage:
    python scripts/run_image_extraction_batch.py --dry-run
    python scripts/run_image_extraction_batch.py --extract
    python scripts/run_image_extraction_batch.py --report
    python scripts/run_image_extraction_batch.py --validate-pdfs
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional
from collections import defaultdict

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

# =============================================================================
# Configuration
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
HIGH_PRIORITY_LIST = PROJECT_ROOT / "data" / "figure_scan" / "high_priority_articles.json"
IMAGE_POOL_DIR = PROJECT_ROOT / "data" / "image_pool"
IMAGES_DIR = IMAGE_POOL_DIR / "images"
EXTRACTION_MANIFEST = IMAGE_POOL_DIR / "extraction_manifest.json"

# PDF source: Article_Finder expected location
ARTICLE_FINDER_ROOT = Path("/Users/davidusa/REPOS/Article_Finder_v3_2_3")
AF_PDF_DIR = ARTICLE_FINDER_ROOT / "data" / "pdfs"

# Fallback: check local data/pdfs as well
LOCAL_PDF_DIR = PROJECT_ROOT / "data" / "pdfs"

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(PROJECT_ROOT / "logs" / "image_extraction_batch.log", mode="a")
    ]
)
logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ExtractionResult:
    """Result of extraction for a single article."""
    doi: str
    pdf_path: Optional[str]
    success: bool
    images_extracted: int = 0
    image_files: List[str] = field(default_factory=list)
    image_metadata: List[Dict[str, Any]] = field(default_factory=list)
    error_message: Optional[str] = None
    extraction_time_sec: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "doi": self.doi,
            "pdf_path": self.pdf_path,
            "success": self.success,
            "images_extracted": self.images_extracted,
            "image_files": self.image_files,
            "image_metadata": self.image_metadata,
            "error_message": self.error_message,
            "extraction_time_sec": self.extraction_time_sec,
        }


@dataclass
class ExtractionManifest:
    """Complete manifest of batch extraction results."""
    extraction_date: str
    script_version: str
    total_articles: int = 0
    articles_with_pdfs: int = 0
    articles_processed: int = 0
    articles_successful: int = 0
    articles_failed: int = 0
    total_images_extracted: int = 0
    total_extraction_time_sec: float = 0.0
    results: List[ExtractionResult] = field(default_factory=list)
    pdfs_not_found: List[Dict[str, Any]] = field(default_factory=list)
    errors_by_type: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "extraction_date": self.extraction_date,
            "script_version": self.script_version,
            "summary": {
                "total_articles": self.total_articles,
                "articles_with_pdfs": self.articles_with_pdfs,
                "articles_processed": self.articles_processed,
                "articles_successful": self.articles_successful,
                "articles_failed": self.articles_failed,
                "total_images_extracted": self.total_images_extracted,
                "total_extraction_time_sec": self.total_extraction_time_sec,
            },
            "results": [r.to_dict() for r in self.results],
            "pdfs_not_found": self.pdfs_not_found,
            "errors_by_type": dict(self.errors_by_type),
        }


# =============================================================================
# PDF Location Functions
# =============================================================================

def find_pdf(doi: str) -> Optional[Path]:
    """Find PDF file for a given DOI.

    Searches in:
    1. Local data/pdfs/
    2. Article_Finder data/pdfs/

    Args:
        doi: DOI string (already converted with / replaced by _)

    Returns:
        Path to PDF if found, None otherwise
    """
    pdf_filename = f"{doi}.pdf"

    # Try local first
    local_path = LOCAL_PDF_DIR / pdf_filename
    if local_path.exists():
        return local_path

    # Try Article_Finder
    af_path = AF_PDF_DIR / pdf_filename
    if af_path.exists():
        return af_path

    return None


def extract_images_from_pdf(
    pdf_path: Path,
    output_dir: Path,
    doi: str,
    min_size: int = 5000
) -> Dict[str, Any]:
    """Extract images from a PDF file.

    Uses PyMuPDF (fitz) to extract all images above a minimum size threshold.
    Adapted from scripts/extract_pdf_images.py.

    Args:
        pdf_path: Path to PDF file
        output_dir: Directory to save extracted images
        doi: DOI identifier for naming
        min_size: Minimum image size in bytes (default 5000)

    Returns:
        Dictionary with extraction results:
        {
            "success": bool,
            "images_extracted": int,
            "image_files": [str],
            "image_metadata": [dict],
            "error": str or None
        }
    """
    if not fitz:
        return {
            "success": False,
            "images_extracted": 0,
            "image_files": [],
            "image_metadata": [],
            "error": "PyMuPDF not installed"
        }

    if not pdf_path.exists():
        return {
            "success": False,
            "images_extracted": 0,
            "image_files": [],
            "image_metadata": [],
            "error": f"PDF not found: {pdf_path}"
        }

    try:
        output_dir.mkdir(parents=True, exist_ok=True)

        # Open PDF
        try:
            doc = fitz.open(str(pdf_path))
        except Exception as e:
            return {
                "success": False,
                "images_extracted": 0,
                "image_files": [],
                "image_metadata": [],
                "error": f"Failed to open PDF: {e}"
            }

        extracted = []
        image_files = []

        # Use DOI (with slashes converted to underscores) as base name
        doi_safe = doi

        # Extract images from each page
        for page_num in range(len(doc)):
            try:
                page = doc[page_num]
                image_list = page.get_images(full=True)

                for img_index, img in enumerate(image_list):
                    xref = img[0]  # Image reference number

                    try:
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]

                        # Filter small images (likely icons/buttons)
                        if len(image_bytes) < min_size:
                            continue

                        # Save image
                        img_filename = f"{doi_safe}_p{page_num + 1:02d}_img{img_index + 1:02d}.{image_ext}"
                        img_path = output_dir / img_filename

                        with open(img_path, "wb") as f:
                            f.write(image_bytes)

                        # Record metadata
                        metadata = {
                            "page": page_num + 1,
                            "index": img_index + 1,
                            "filename": img_filename,
                            "size_bytes": len(image_bytes),
                            "width": base_image.get("width"),
                            "height": base_image.get("height"),
                            "colorspace": base_image.get("colorspace"),
                            "ext": image_ext,
                        }
                        extracted.append(metadata)
                        image_files.append(img_filename)

                    except Exception as e:
                        logger.warning(
                            f"Could not extract image {xref} on page {page_num + 1}: {e}"
                        )

            except Exception as e:
                logger.warning(f"Error processing page {page_num}: {e}")

        doc.close()

        return {
            "success": True,
            "images_extracted": len(extracted),
            "image_files": image_files,
            "image_metadata": extracted,
            "error": None
        }

    except Exception as e:
        logger.error(f"Extraction failed for {pdf_path}: {e}")
        return {
            "success": False,
            "images_extracted": 0,
            "image_files": [],
            "image_metadata": [],
            "error": str(e)
        }


# =============================================================================
# Main Orchestration Functions
# =============================================================================

def load_high_priority_articles() -> List[Dict[str, Any]]:
    """Load the list of 56 HIGH-priority articles.

    Returns:
        List of article dictionaries with keys: doi, has_pdf, figure_count, stimulus_indicators
    """
    if not HIGH_PRIORITY_LIST.exists():
        raise FileNotFoundError(f"High priority list not found: {HIGH_PRIORITY_LIST}")

    with open(HIGH_PRIORITY_LIST) as f:
        return json.load(f)


def validate_pdfs(dry_run: bool = False) -> Dict[str, Any]:
    """Validate which PDFs are available.

    Args:
        dry_run: If True, don't print (just collect stats)

    Returns:
        Dictionary with validation results
    """
    articles = load_high_priority_articles()

    available = []
    missing = []

    for article in articles:
        doi = article["doi"]
        pdf_path = find_pdf(doi)

        if pdf_path:
            available.append({
                "doi": doi,
                "pdf_path": str(pdf_path),
                "figure_count": article["figure_count"]
            })
        else:
            missing.append({
                "doi": doi,
                "figure_count": article["figure_count"],
                "stimulus_indicators": article.get("stimulus_indicators", [])
            })

    if not dry_run:
        logger.info(f"PDF Validation Results:")
        logger.info(f"  Total articles: {len(articles)}")
        logger.info(f"  PDFs available: {len(available)}")
        logger.info(f"  PDFs missing: {len(missing)}")

        if available:
            logger.info(f"\nAvailable PDFs ({len(available)}):")
            for item in available[:5]:
                logger.info(f"  {item['doi']}: {item['figure_count']} figures")
            if len(available) > 5:
                logger.info(f"  ... and {len(available) - 5} more")

        if missing:
            logger.info(f"\nMissing PDFs ({len(missing)}):")
            for item in missing[:5]:
                logger.info(f"  {item['doi']}: {item['figure_count']} figures")
            if len(missing) > 5:
                logger.info(f"  ... and {len(missing) - 5} more")

    return {
        "total_articles": len(articles),
        "available": len(available),
        "missing": len(missing),
        "available_list": available,
        "missing_list": missing
    }


def run_extraction_batch(dry_run: bool = False) -> ExtractionManifest:
    """Run image extraction for all available HIGH-priority articles.

    Args:
        dry_run: If True, only validate PDFs without extracting

    Returns:
        ExtractionManifest with results
    """
    articles = load_high_priority_articles()

    manifest = ExtractionManifest(
        extraction_date=datetime.now(timezone.utc).isoformat(),
        script_version="V1.0",
        total_articles=len(articles)
    )

    logger.info(f"Starting batch extraction: {len(articles)} HIGH-priority articles")

    if dry_run:
        logger.info("DRY-RUN MODE: Validating PDFs without extraction")

    # Create image pool directories
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    import time
    start_time = time.time()

    for i, article in enumerate(articles, 1):
        doi = article["doi"]
        figure_count = article["figure_count"]
        stimulus_indicators = article.get("stimulus_indicators", [])

        logger.info(
            f"[{i}/{len(articles)}] Processing {doi} "
            f"({figure_count} figures, {len(stimulus_indicators)} stimulus types)"
        )

        # Find PDF
        pdf_path = find_pdf(doi)

        if not pdf_path:
            logger.warning(f"  ✗ PDF not found")
            manifest.pdfs_not_found.append({
                "doi": doi,
                "figure_count": figure_count,
                "stimulus_indicators": stimulus_indicators
            })
            manifest.articles_failed += 1
            continue

        manifest.articles_with_pdfs += 1
        logger.info(f"  ✓ PDF found: {pdf_path.name}")

        if dry_run:
            logger.info(f"  [DRY-RUN] Would extract from: {pdf_path}")
            manifest.articles_processed += 1
            continue

        # Extract images
        article_extract_start = time.time()

        # Create article-specific output directory
        article_img_dir = IMAGES_DIR / doi

        result = extract_images_from_pdf(pdf_path, article_img_dir, doi)

        article_extract_time = time.time() - article_extract_start

        if result["success"]:
            logger.info(
                f"  ✓ Extracted {result['images_extracted']} images "
                f"({article_extract_time:.2f}s)"
            )

            # Create extraction result
            extraction_result = ExtractionResult(
                doi=doi,
                pdf_path=str(pdf_path),
                success=True,
                images_extracted=result["images_extracted"],
                image_files=result["image_files"],
                image_metadata=result["image_metadata"],
                extraction_time_sec=article_extract_time
            )
            manifest.results.append(extraction_result)
            manifest.articles_processed += 1
            manifest.articles_successful += 1
            manifest.total_images_extracted += result["images_extracted"]
        else:
            logger.error(f"  ✗ Extraction failed: {result['error']}")

            extraction_result = ExtractionResult(
                doi=doi,
                pdf_path=str(pdf_path),
                success=False,
                error_message=result["error"],
                extraction_time_sec=article_extract_time
            )
            manifest.results.append(extraction_result)
            manifest.articles_processed += 1
            manifest.articles_failed += 1

            # Track error type
            error_type = "unknown"
            if "PDF not found" in result["error"]:
                error_type = "pdf_not_found"
            elif "Failed to open" in result["error"]:
                error_type = "pdf_corrupted"
            elif "PyMuPDF not installed" in result["error"]:
                error_type = "pymupdf_missing"
            manifest.errors_by_type[error_type] += 1

    manifest.total_extraction_time_sec = time.time() - start_time

    return manifest


def save_extraction_manifest(manifest: ExtractionManifest) -> None:
    """Save extraction manifest to JSON file.

    Args:
        manifest: ExtractionManifest to save
    """
    IMAGE_POOL_DIR.mkdir(parents=True, exist_ok=True)

    with open(EXTRACTION_MANIFEST, "w") as f:
        json.dump(manifest.to_dict(), f, indent=2)

    logger.info(f"Extraction manifest saved: {EXTRACTION_MANIFEST}")


def print_extraction_report(manifest: ExtractionManifest) -> None:
    """Print a formatted extraction report.

    Args:
        manifest: ExtractionManifest to report on
    """
    print("\n" + "=" * 80)
    print("IMAGE EXTRACTION BATCH REPORT")
    print("=" * 80)
    print(f"\nDate: {manifest.extraction_date}")
    print(f"Version: {manifest.script_version}")

    print(f"\nSummary:")
    print(f"  Total HIGH-priority articles: {manifest.total_articles}")
    print(f"  Articles with PDFs available: {manifest.articles_with_pdfs}")
    print(f"  Articles processed: {manifest.articles_processed}")
    print(f"  Successful extractions: {manifest.articles_successful}")
    print(f"  Failed extractions: {manifest.articles_failed}")
    print(f"  Total images extracted: {manifest.total_images_extracted}")
    print(f"  Total extraction time: {manifest.total_extraction_time_sec:.1f} seconds")

    if manifest.articles_with_pdfs > 0:
        success_rate = (manifest.articles_successful / manifest.articles_processed) * 100
        print(f"  Success rate: {success_rate:.1f}%")

    if manifest.pdfs_not_found:
        print(f"\nPDFs Not Found ({len(manifest.pdfs_not_found)}):")
        for item in manifest.pdfs_not_found[:10]:
            print(f"  • {item['doi']} ({item['figure_count']} figures)")
        if len(manifest.pdfs_not_found) > 10:
            print(f"  ... and {len(manifest.pdfs_not_found) - 10} more")

    if manifest.errors_by_type:
        print(f"\nErrors by Type:")
        for error_type, count in sorted(manifest.errors_by_type.items(), key=lambda x: -x[1]):
            print(f"  • {error_type}: {count}")

    if manifest.results:
        print(f"\nSuccessful Extractions (first 10):")
        for result in manifest.results[:10]:
            if result.success:
                print(f"  • {result.doi}: {result.images_extracted} images")

        failed = [r for r in manifest.results if not r.success]
        if failed:
            print(f"\nFailed Extractions ({len(failed)}):")
            for result in failed[:5]:
                print(f"  • {result.doi}: {result.error_message}")
            if len(failed) > 5:
                print(f"  ... and {len(failed) - 5} more")

    print("\n" + "=" * 80 + "\n")


def create_image_pool_readme() -> None:
    """Create README for the image pool directory."""
    readme_path = IMAGE_POOL_DIR / "README.md"

    readme_content = """# Image Pool

Local repository of images extracted from HIGH-priority scientific articles.

**Purpose**: Support stimulus analysis for environmental psychology experiments.
Extracted images serve as reference material for hypothesis testing and method
validation across stimulus modalities (photographs, diagrams, rendered scenes).

## Directory Structure

```
image_pool/
├── images/              # Image files organized by DOI
│   ├── 10.1007_s00530-024-01514-6/
│   ├── 10.1016_j.actpsy.2021.103285/
│   └── ... (54 more article directories)
├── extraction_manifest.json   # Complete extraction metadata
├── image_pool.db              # SQLite pool database
├── thumbnails/                # Thumbnail cache (if generated)
└── README.md                  # This file
```

## Extraction Manifest

`extraction_manifest.json` contains:
- Article metadata (DOI, PDF location, extraction timestamp)
- Per-image metadata (page number, dimensions, file size, colorspace)
- Extraction statistics (total images, extraction time, error tracking)
- Missing PDF locations (articles not yet in local storage)

## Image Organization

Images are stored in article-specific subdirectories:
```
image_pool/images/{DOI}/
├── {DOI}_p01_img01.png    # Page 1, Image 1
├── {DOI}_p01_img02.jpg    # Page 1, Image 2
├── {DOI}_p02_img01.png    # Page 2, Image 1
└── ...
```

Filename convention: `{DOI}_p{PAGE:02d}_img{INDEX:02d}.{EXT}`

## Extraction Workflow

1. **Scan**: `scripts/figure_scanner.py` identified 56 HIGH-priority articles
   (with both figure references AND stimulus experiments)

2. **Orchestration**: `scripts/run_image_extraction_batch.py` batch extracts
   images from available PDFs using PyMuPDF (fitz)

3. **Classification** (next phase): Images classified by VLM into:
   - Stimulus images (photographs, rendered scenes, stimuli)
   - Charts/diagrams (results, data visualization)
   - Other (logos, formatting, etc.)

4. **Annotation** (next phase): Images tagged with feature taxonomy:
   - Constraint features (refuge, prospect, complexity, etc.)
   - Methodological context (experimental protocol, apparatus)

## PDF Source

PDFs are expected at:
- Primary: `/Users/davidusa/REPOS/Article_Finder_v3_2_3/data/pdfs/`
- Fallback: `data/pdfs/` (local)

If a PDF is not available locally, use Article_Finder to download it.

## Statistics

As of 2026-02-28:
- **Total HIGH-priority articles**: 56
- **With figure references**: All (requirement for HIGH classification)
- **With stimulus experiments**: All (requirement for HIGH classification)
- **PDFs available locally**: [See extraction_manifest.json for current status]
- **Images extracted**: [See extraction_manifest.json for current status]

## Next Steps

1. Run image extraction: `python scripts/run_image_extraction_batch.py --extract`
2. Generate extraction report: `python scripts/run_image_extraction_batch.py --report`
3. Classify images by type (VLM-based)
4. Annotate images with feature taxonomy
5. Link images to findings in original papers

## Technical Details

### PyMuPDF (fitz) Configuration

- **Min image size**: 5,000 bytes (filters out icons/buttons)
- **Output formats**: PNG, JPG, TIFF, BMP (preserves original)
- **Page extraction**: Full page image lists via `page.get_images(full=True)`
- **Metadata captured**:
  - Dimensions (width, height)
  - File size in bytes
  - Colorspace (RGB, CMYK, etc.)
  - File extension

### Error Handling

Extraction errors are logged with type classification:
- `pdf_not_found`: PDF not in local storage
- `pdf_corrupted`: PDF cannot be opened
- `pymupdf_missing`: PyMuPDF package not installed
- `unknown`: Unclassified extraction error

## References

- PyMuPDF documentation: https://pymupdf.readthedocs.io/
- Figure scanner results: `data/figure_scan/figure_scan_report.md`
- HIGH-priority articles list: `data/figure_scan/high_priority_articles.json`

---
Generated: 2026-02-28
"""

    with open(readme_path, "w") as f:
        f.write(readme_content)

    logger.info(f"Image pool README created: {readme_path}")


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Batch image extraction orchestration for HIGH-priority articles"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate PDFs without extracting (dry-run mode)"
    )
    parser.add_argument(
        "--extract",
        action="store_true",
        help="Run full extraction batch"
    )
    parser.add_argument(
        "--validate-pdfs",
        action="store_true",
        help="Validate PDF availability and report missing PDFs"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Print extraction report from manifest"
    )

    args = parser.parse_args()

    # Check PyMuPDF availability for extraction modes (not for validation/report)
    if args.extract:
        if not fitz:
            logger.error("PyMuPDF not installed. Install with: pip install PyMuPDF")
            sys.exit(1)

    try:
        # Default to validation if no action specified
        if not (args.extract or args.dry_run or args.validate_pdfs or args.report):
            args.validate_pdfs = True

        if args.validate_pdfs:
            logger.info("Validating PDF availability...")
            results = validate_pdfs(dry_run=True)
            logger.info(f"Available: {results['available']}/{results['total_articles']}")
            logger.info(f"Missing: {results['missing']}/{results['total_articles']}")

        if args.dry_run:
            logger.info("\n" + "=" * 80)
            logger.info("DRY-RUN: Image Extraction Batch")
            logger.info("=" * 80)
            manifest = run_extraction_batch(dry_run=True)
            print_extraction_report(manifest)
            save_extraction_manifest(manifest)

        if args.extract:
            logger.info("\n" + "=" * 80)
            logger.info("Running Image Extraction Batch")
            logger.info("=" * 80)

            # Create README
            create_image_pool_readme()

            # Run extraction
            manifest = run_extraction_batch(dry_run=False)

            # Save manifest
            save_extraction_manifest(manifest)

            # Print report
            print_extraction_report(manifest)

        if args.report:
            if EXTRACTION_MANIFEST.exists():
                with open(EXTRACTION_MANIFEST) as f:
                    manifest_dict = json.load(f)

                # Reconstruct manifest object for reporting
                manifest = ExtractionManifest(
                    extraction_date=manifest_dict["extraction_date"],
                    script_version=manifest_dict["script_version"],
                    total_articles=manifest_dict["summary"]["total_articles"],
                    articles_with_pdfs=manifest_dict["summary"]["articles_with_pdfs"],
                    articles_processed=manifest_dict["summary"]["articles_processed"],
                    articles_successful=manifest_dict["summary"]["articles_successful"],
                    articles_failed=manifest_dict["summary"]["articles_failed"],
                    total_images_extracted=manifest_dict["summary"]["total_images_extracted"],
                    total_extraction_time_sec=manifest_dict["summary"]["total_extraction_time_sec"],
                )

                print_extraction_report(manifest)
            else:
                logger.error(f"No extraction manifest found: {EXTRACTION_MANIFEST}")
                logger.info("Run extraction first: python scripts/run_image_extraction_batch.py --extract")

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
