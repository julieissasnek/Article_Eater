#!/usr/bin/env python3
"""
Extract stimulus images from PDFs.

For each PDF, extracts all embedded images above a minimum size threshold,
saves them to data/gold_standard/stimulus_images/PDF-NNNN/, and outputs
a manifest JSON with page numbers and image metadata.

Usage:
    python3 scripts/extract_stimulus_images.py PDF-0007
    python3 scripts/extract_stimulus_images.py PDF-0007 --pdf-path /path/to/paper.pdf
    python3 scripts/extract_stimulus_images.py --batch PDF-0007 PDF-0008 PDF-0009

The script can also render full pages as images (useful for figures that
are composed of vector graphics rather than embedded raster images):
    python3 scripts/extract_stimulus_images.py PDF-0007 --pages 3,5,7
"""

import sys
import json
import argparse
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF not installed. Run: pip3 install pymupdf --break-system-packages")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).parent.parent
INVENTORY_FILE = PROJECT_ROOT / "data" / "pdf_inventory.json"
IMAGES_DIR = PROJECT_ROOT / "data" / "gold_standard" / "stimulus_images"
ZOTERO_BASE = Path("/sessions/keen-busy-turing/mnt/REPOS/__Zotero whole bibliography/files")

# Minimum image dimensions to extract (skip tiny icons, logos)
MIN_WIDTH = 150
MIN_HEIGHT = 150
# Minimum image area (width * height) — filters out narrow banners
MIN_AREA = 40000


def get_pdf_path(pdf_id: str) -> Path:
    """Look up PDF path from inventory."""
    if not INVENTORY_FILE.exists():
        print(f"ERROR: Inventory file not found: {INVENTORY_FILE}")
        sys.exit(1)

    with open(INVENTORY_FILE) as f:
        raw = json.load(f)

    # Handle nested structure: {"metadata": ..., "inventory": {...}}
    inventory = raw.get("inventory", raw)

    if pdf_id not in inventory:
        print(f"ERROR: {pdf_id} not found in inventory")
        sys.exit(1)

    entry = inventory[pdf_id]
    # Build full path
    pdf_path = ZOTERO_BASE / entry["folder"] / entry["filename"]
    if not pdf_path.exists():
        # Try neuroarch_batch
        neuroarch_base = PROJECT_ROOT / "data" / "pdfs" / "neuroarch_batch"
        pdf_path = neuroarch_base / entry["filename"]

    return pdf_path


def extract_embedded_images(pdf_path: Path, output_dir: Path, pdf_id: str) -> list:
    """Extract all embedded images above size threshold from PDF."""
    doc = fitz.open(str(pdf_path))
    manifest = []
    img_count = 0

    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)

        for img_index, img_info in enumerate(image_list):
            xref = img_info[0]

            try:
                base_image = doc.extract_image(xref)
            except Exception as e:
                continue

            if not base_image:
                continue

            width = base_image["width"]
            height = base_image["height"]
            area = width * height

            # Filter small images (logos, icons, decorative elements)
            if width < MIN_WIDTH or height < MIN_HEIGHT or area < MIN_AREA:
                continue

            img_count += 1
            ext = base_image["ext"]
            filename = f"{pdf_id}_p{page_num + 1}_img{img_count}.{ext}"
            filepath = output_dir / filename

            with open(filepath, "wb") as f:
                f.write(base_image["image"])

            manifest.append({
                "image_id": f"{pdf_id}_img{img_count}",
                "filename": filename,
                "page": page_num + 1,
                "width": width,
                "height": height,
                "format": ext,
                "size_bytes": len(base_image["image"]),
                "path": str(filepath)
            })

    doc.close()
    return manifest


def render_pages_as_images(pdf_path: Path, output_dir: Path, pdf_id: str,
                           pages: list, dpi: int = 200) -> list:
    """Render specific pages as high-resolution images.

    This catches figures composed of vector graphics (charts, diagrams,
    architectural drawings) that aren't embedded raster images.
    """
    doc = fitz.open(str(pdf_path))
    manifest = []

    for page_num in pages:
        if page_num < 1 or page_num > len(doc):
            print(f"  WARNING: Page {page_num} out of range (1-{len(doc)})")
            continue

        page = doc[page_num - 1]  # 0-indexed
        zoom = dpi / 72  # 72 is default PDF DPI
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)

        filename = f"{pdf_id}_page{page_num}_full.png"
        filepath = output_dir / filename
        pix.save(str(filepath))

        manifest.append({
            "image_id": f"{pdf_id}_page{page_num}",
            "filename": filename,
            "page": page_num,
            "width": pix.width,
            "height": pix.height,
            "format": "png",
            "size_bytes": filepath.stat().st_size,
            "path": str(filepath),
            "render_type": "full_page",
            "dpi": dpi
        })

    doc.close()
    return manifest


def extract_all(pdf_id: str, pdf_path: Path = None, pages: list = None) -> dict:
    """Extract all images from a PDF and save manifest."""
    if pdf_path is None:
        pdf_path = get_pdf_path(pdf_id)

    if not pdf_path.exists():
        print(f"ERROR: PDF not found: {pdf_path}")
        return {"error": f"PDF not found: {pdf_path}"}

    output_dir = IMAGES_DIR / pdf_id
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Extracting images from {pdf_id}: {pdf_path.name}")
    print(f"  Output: {output_dir}")

    # Step 1: Extract embedded raster images
    embedded = extract_embedded_images(pdf_path, output_dir, pdf_id)
    print(f"  Embedded images extracted: {len(embedded)}")

    # Step 2: Optionally render specific pages
    rendered = []
    if pages:
        rendered = render_pages_as_images(pdf_path, output_dir, pdf_id, pages)
        print(f"  Pages rendered: {len(rendered)}")

    # Build manifest
    manifest = {
        "pdf_id": pdf_id,
        "pdf_path": str(pdf_path),
        "pdf_filename": pdf_path.name,
        "total_images": len(embedded) + len(rendered),
        "embedded_images": embedded,
        "rendered_pages": rendered
    }

    # Save manifest
    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"  Manifest saved: {manifest_path}")

    return manifest


def main():
    parser = argparse.ArgumentParser(description="Extract stimulus images from PDFs")
    parser.add_argument("pdf_ids", nargs="+", help="PDF IDs (e.g., PDF-0007)")
    parser.add_argument("--pdf-path", help="Override PDF path (for single extraction)")
    parser.add_argument("--pages", help="Comma-separated page numbers to render as full images")
    parser.add_argument("--dpi", type=int, default=200, help="DPI for page rendering (default: 200)")

    args = parser.parse_args()

    pages = None
    if args.pages:
        pages = [int(p.strip()) for p in args.pages.split(",")]

    for pdf_id in args.pdf_ids:
        pdf_path = Path(args.pdf_path) if args.pdf_path and len(args.pdf_ids) == 1 else None
        manifest = extract_all(pdf_id, pdf_path, pages)

        if "error" not in manifest:
            print(f"\n  === {pdf_id} SUMMARY ===")
            print(f"  Total images: {manifest['total_images']}")
            for img in manifest["embedded_images"]:
                print(f"    [{img['page']}] {img['filename']} ({img['width']}x{img['height']}, {img['size_bytes']//1024}KB)")
            for img in manifest.get("rendered_pages", []):
                print(f"    [p{img['page']}] {img['filename']} ({img['width']}x{img['height']}, {img['size_bytes']//1024}KB, rendered)")
        print()


if __name__ == "__main__":
    main()
