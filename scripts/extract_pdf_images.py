#!/usr/bin/env python3
"""Extract images from PDFs using PyMuPDF.

Usage:
    python scripts/extract_pdf_images.py --pdf path/to/paper.pdf
    python scripts/extract_pdf_images.py --doi 10.1177/03010066221124872
    python scripts/extract_pdf_images.py --doi 10.1177/03010066221124872 --min-size 10000
"""

import argparse
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF not installed. Run: pip install PyMuPDF")
    sys.exit(1)

# Paths
AF_ROOT = Path("/Users/davidusa/REPOS/Article_Finder_v3_2_3")
PDF_DIR = AF_ROOT / "data" / "pdfs"
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "extracted_images"


def extract_images(pdf_path: Path, output_dir: Path, min_size: int = 5000) -> list[dict]:
    """Extract images from a PDF.

    Args:
        pdf_path: Path to PDF file
        output_dir: Directory to save extracted images
        min_size: Minimum image size in bytes (filters out tiny icons)

    Returns:
        List of extracted image metadata
    """
    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}")
        return []

    output_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(pdf_path))
    extracted = []

    doi_safe = pdf_path.stem  # Already has / replaced with _

    for page_num in range(len(doc)):
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

                extracted.append({
                    "page": page_num + 1,
                    "index": img_index + 1,
                    "filename": img_filename,
                    "size_bytes": len(image_bytes),
                    "width": base_image.get("width"),
                    "height": base_image.get("height"),
                    "colorspace": base_image.get("colorspace"),
                    "ext": image_ext,
                })

            except Exception as e:
                print(f"  Warning: Could not extract image {xref} on page {page_num + 1}: {e}")

    doc.close()
    return extracted


def main():
    parser = argparse.ArgumentParser(description="Extract images from PDFs")
    parser.add_argument("--pdf", type=str, help="Path to PDF file")
    parser.add_argument("--doi", type=str, help="DOI (will look up PDF in standard location)")
    parser.add_argument("--min-size", type=int, default=5000, help="Min image size in bytes (default 5000)")
    parser.add_argument("--output", type=str, help="Output directory (default: data/extracted_images)")
    args = parser.parse_args()

    if args.pdf:
        pdf_path = Path(args.pdf)
    elif args.doi:
        pdf_path = PDF_DIR / (args.doi.replace("/", "_") + ".pdf")
    else:
        parser.print_help()
        return

    output_dir = Path(args.output) if args.output else OUTPUT_DIR

    print(f"Extracting images from: {pdf_path}")
    print(f"Output directory: {output_dir}")
    print(f"Minimum image size: {args.min_size} bytes")
    print()

    extracted = extract_images(pdf_path, output_dir, min_size=args.min_size)

    if extracted:
        print(f"\nExtracted {len(extracted)} images:")
        for img in extracted:
            print(f"  Page {img['page']}: {img['filename']} ({img['width']}x{img['height']}, {img['size_bytes']:,} bytes)")
    else:
        print("\nNo images extracted (either none found or all below size threshold)")


if __name__ == "__main__":
    main()
