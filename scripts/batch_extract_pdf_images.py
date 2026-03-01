#!/usr/bin/env python3
"""
Sprint S-2: Batch PDF Image Extraction & Classification
========================================================

Extracts images from HIGH-priority PDFs, co-extracts captions,
classifies each image (stimulus/chart/diagram/decorative/photo),
links figures to findings, and generates a structured report.

Two-pass strategy:
  Pass 1 (free, local): Extract all images > 5KB via PyMuPDF
  Pass 2 (heuristic): Classify using image metadata + surrounding text

Usage:
    python scripts/batch_extract_pdf_images.py
    python scripts/batch_extract_pdf_images.py --max 10         # First 10 only
    python scripts/batch_extract_pdf_images.py --dry-run        # Report only
"""

import argparse
import json
import re
import sys
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF not installed. Run: pip install PyMuPDF")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

PDF_DIR = Path("/Users/davidusa/REPOS/Article_Finder_v3_2_3/data/pdfs")
TARGETS_PATH = PROJECT_ROOT / "data" / "figure_scan" / "high_priority_targets.json"
OUTPUT_DIR = PROJECT_ROOT / "data" / "extracted_images"
REPORT_DIR = PROJECT_ROOT / "data" / "image_extraction_reports"

MIN_IMAGE_SIZE = 5000  # bytes — filters tiny icons
MIN_DIMENSION = 100    # pixels — both width and height


# =============================================================================
# Pass 1: Image Extraction with Caption Co-extraction
# =============================================================================

def extract_images_from_pdf(pdf_path: Path, doi: str, output_dir: Path) -> list:
    """Extract images from a single PDF with caption co-extraction.
    
    Returns list of image metadata dicts.
    """
    if not pdf_path.exists():
        return []
    
    output_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(pdf_path))
    extracted = []
    doi_safe = doi.replace("/", "_").replace(":", "_")
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)
        page_text = page.get_text("text")
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            
            try:
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                width = base_image.get("width", 0)
                height = base_image.get("height", 0)
                
                # Filter: too small
                if len(image_bytes) < MIN_IMAGE_SIZE:
                    continue
                if width < MIN_DIMENSION or height < MIN_DIMENSION:
                    continue
                
                # Filter: extreme aspect ratio (likely banner/rule)
                if width > 0 and height > 0:
                    ratio = max(width, height) / min(width, height)
                    if ratio > 8:
                        continue
                
                # Save image
                img_filename = f"{doi_safe}_p{page_num+1:02d}_img{img_index+1:02d}.{image_ext}"
                img_path = output_dir / img_filename
                
                with open(img_path, "wb") as f:
                    f.write(image_bytes)
                
                # Co-extract caption
                caption = extract_caption(page_text, page_num + 1, img_index + 1)
                
                extracted.append({
                    "doi": doi,
                    "page": page_num + 1,
                    "index": img_index + 1,
                    "filename": img_filename,
                    "path": str(img_path),
                    "size_bytes": len(image_bytes),
                    "width": width,
                    "height": height,
                    "ext": image_ext,
                    "caption": caption,
                    "classification": None,  # Filled in Pass 2
                })
                
            except Exception as e:
                pass  # Skip problematic images silently
    
    doc.close()
    return extracted


def extract_caption(page_text: str, page_num: int, img_index: int) -> str:
    """Extract figure caption from page text."""
    # Look for Fig/Figure patterns
    patterns = [
        re.compile(r'(Fig(?:ure)?\.?\s*\d+[a-z]?[\.\:]\s*[^\n]{10,200})', re.IGNORECASE),
        re.compile(r'(Figure\s+\d+[a-z]?\.?\s*[^\n]{10,200})', re.IGNORECASE),
        re.compile(r'(Plate\s+\d+[\.\:]\s*[^\n]{10,200})', re.IGNORECASE),
    ]
    
    captions = []
    for pattern in patterns:
        matches = pattern.findall(page_text)
        captions.extend(matches)
    
    if captions:
        # Return the one most likely matching this image index
        for cap in captions:
            nums = re.findall(r'(?:Fig|Figure|Plate)\.?\s*(\d+)', cap, re.IGNORECASE)
            if nums and int(nums[0]) == img_index:
                return cap.strip()
        return captions[0].strip()  # Fallback: first caption on page
    
    return ""


# =============================================================================
# Pass 2: Heuristic Image Classification
# =============================================================================

IMAGE_TYPES = {
    "stimulus": "Architectural/environmental image used as experimental stimulus",
    "chart": "Data visualization (bar, line, scatter plot, etc.)",
    "diagram": "Conceptual diagram, flowchart, or schematic",
    "floor_plan": "Architectural floor plan or layout",
    "photograph": "Real-world photograph of environment/building",
    "screenshot": "Software interface or VR environment screenshot",
    "decorative": "Logo, icon, header, or non-content image",
}


def classify_image(img_meta: dict) -> str:
    """Classify an extracted image using heuristic rules.
    
    Uses image metadata (size, aspect ratio, caption text) to classify.
    For real classification, replace with VLM (Gemini Flash).
    """
    caption = (img_meta.get("caption") or "").lower()
    width = img_meta.get("width", 0)
    height = img_meta.get("height", 0)
    size = img_meta.get("size_bytes", 0)
    
    # Chart indicators in caption
    chart_words = ["graph", "plot", "chart", "histogram", "bar chart",
                   "scatter", "distribution", "regression", "correlation",
                   "data", "results", "analysis", "mean", "standard deviation"]
    if any(w in caption for w in chart_words):
        return "chart"
    
    # Diagram indicators
    diagram_words = ["diagram", "flowchart", "schematic", "model", "framework",
                     "pathway", "process", "conceptual", "theoretical"]
    if any(w in caption for w in diagram_words):
        return "diagram"
    
    # Floor plan indicators
    plan_words = ["floor plan", "layout", "plan view", "section", "elevation",
                  "blueprint", "axonometric"]
    if any(w in caption for w in plan_words):
        return "floor_plan"
    
    # Stimulus indicators
    stimulus_words = ["stimulus", "stimuli", "scene", "environment", "view",
                      "interior", "exterior", "room", "space", "building",
                      "facade", "street", "park", "garden", "landscape",
                      "photograph", "photo", "image used", "presented to"]
    if any(w in caption for w in stimulus_words):
        return "stimulus"
    
    # Screenshot/VR indicators
    vr_words = ["screenshot", "vr", "virtual", "rendering", "3d model",
                "simulated", "unity", "unreal"]
    if any(w in caption for w in vr_words):
        return "screenshot"
    
    # Size heuristic: large colorful images are likely photos/stimuli
    if size > 50000 and width > 400 and height > 300:
        aspect = width / max(height, 1)
        if 0.5 < aspect < 2.5:
            return "photograph"
    
    # Small images without captions → decorative
    if size < 15000 or not caption:
        return "decorative"
    
    return "photograph"  # Default for unclassified


# =============================================================================
# Pass 3: Link Figures to Findings
# =============================================================================

def link_figures_to_findings(doi: str, images: list) -> list:
    """Link extracted images to extraction findings that reference them."""
    links = []
    
    # Load extraction JSON
    extractions_dir = PROJECT_ROOT / "data" / "extractions"
    doi_safe = doi.replace("/", "_").replace(":", "_")
    
    # Try multiple naming conventions
    for pattern in [f"{doi_safe}.json", f"{doi_safe}_extraction.json"]:
        ext_path = extractions_dir / pattern
        if ext_path.exists():
            try:
                with open(ext_path) as f:
                    extraction = json.load(f)
                
                findings = extraction.get("findings", extraction.get("claims", []))
                if not isinstance(findings, list):
                    break
                
                for finding in findings:
                    if not isinstance(finding, dict):
                        continue
                    
                    # Search finding text for figure references
                    text = " ".join(str(v) for v in finding.values() if isinstance(v, str))
                    fig_refs = re.findall(r'(?:Fig(?:ure)?|fig)\.?\s*(\d+)', text, re.IGNORECASE)
                    
                    for ref_num in fig_refs:
                        for img in images:
                            if img["index"] == int(ref_num) or img["page"] == int(ref_num):
                                links.append({
                                    "image": img["filename"],
                                    "finding_index": findings.index(finding),
                                    "figure_ref": f"Fig {ref_num}",
                                    "finding_text": text[:150],
                                })
            except Exception:
                pass
            break
    
    return links


# =============================================================================
# Main Pipeline
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Batch extract PDF images")
    parser.add_argument("--max", type=int, default=0, help="Max articles to process (0=all)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    # Load targets
    with open(TARGETS_PATH) as f:
        targets_data = json.load(f)
    
    targets = targets_data["targets"]
    if args.max > 0:
        targets = targets[:args.max]
    
    print(f"Processing {len(targets)} HIGH-priority articles...")
    print(f"PDF directory: {PDF_DIR}")
    print(f"Output: {OUTPUT_DIR}")
    print()
    
    all_images = []
    all_links = []
    stats = Counter()
    article_reports = []
    
    for i, target in enumerate(targets):
        doi = target["doi"]
        pdf_path = Path(target["pdf_path"])
        
        print(f"[{i+1}/{len(targets)}] {doi}...")
        
        if not pdf_path.exists():
            stats["pdf_missing"] += 1
            continue
        
        # Pass 1: Extract
        doi_dir = OUTPUT_DIR / doi.replace("/", "_")
        
        if args.dry_run:
            # Just check PDF structure
            doc = fitz.open(str(pdf_path))
            total_images = sum(len(page.get_images(full=True)) for page in doc)
            doc.close()
            stats["images_found"] += total_images
            stats["articles_scanned"] += 1
            article_reports.append({
                "doi": doi,
                "total_images_in_pdf": total_images,
                "status": "dry_run",
            })
            continue
        
        images = extract_images_from_pdf(pdf_path, doi, doi_dir)
        
        if not images:
            stats["articles_no_images"] += 1
            continue
        
        # Pass 2: Classify
        for img in images:
            img["classification"] = classify_image(img)
        
        # Pass 3: Link to findings
        links = link_figures_to_findings(doi, images)
        
        # Stats
        stats["articles_processed"] += 1
        stats["images_extracted"] += len(images)
        for img in images:
            stats[f"type_{img['classification']}"] += 1
        stats["figure_finding_links"] += len(links)
        
        all_images.extend(images)
        all_links.extend(links)
        
        article_reports.append({
            "doi": doi,
            "images_extracted": len(images),
            "classifications": Counter(img["classification"] for img in images),
            "links_found": len(links),
            "captions_found": sum(1 for img in images if img.get("caption")),
        })
        
        print(f"  → {len(images)} images ({', '.join(f'{c}:{n}' for c, n in Counter(img['classification'] for img in images).items())})")
    
    # Save reports
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Full extraction manifest
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "articles_processed": stats.get("articles_processed", stats.get("articles_scanned", 0)),
        "total_images": stats.get("images_extracted", stats.get("images_found", 0)),
        "stats": dict(stats),
        "images": all_images,
        "figure_finding_links": all_links,
        "article_reports": article_reports,
    }
    
    manifest_path = REPORT_DIR / f"extraction_manifest_{date_str}.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2, default=str)
    
    # Summary report (markdown)
    md_path = REPORT_DIR / f"extraction_report_{date_str}.md"
    with open(md_path, "w") as f:
        f.write(generate_markdown_report(stats, article_reports, all_images, all_links))
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"BATCH PDF IMAGE EXTRACTION {'(DRY RUN)' if args.dry_run else 'COMPLETE'}")
    print(f"{'='*60}")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v}")
    
    stim_count = stats.get("type_stimulus", 0) + stats.get("type_photograph", 0) + stats.get("type_screenshot", 0)
    total = stats.get("images_extracted", stats.get("images_found", 0))
    print(f"\n  Stimulus/photo/VR: {stim_count}/{total}")
    print(f"  Figure→Finding links: {stats.get('figure_finding_links', 0)}")
    print(f"\n  Reports: {REPORT_DIR}")


def generate_markdown_report(stats, articles, images, links):
    """Generate markdown extraction report."""
    stim_count = stats.get("type_stimulus", 0)
    photo_count = stats.get("type_photograph", 0)
    chart_count = stats.get("type_chart", 0)
    
    lines = [
        "# PDF Image Extraction Report",
        f"**Date**: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Summary",
        "",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Articles processed | {stats.get('articles_processed', 0)} |",
        f"| Total images extracted | {stats.get('images_extracted', 0)} |",
        f"| Stimuli / env photos | {stim_count + photo_count} |",
        f"| Charts / diagrams | {chart_count + stats.get('type_diagram', 0)} |",
        f"| Floor plans | {stats.get('type_floor_plan', 0)} |",
        f"| VR screenshots | {stats.get('type_screenshot', 0)} |",
        f"| Decorative (filtered) | {stats.get('type_decorative', 0)} |",
        f"| Figure→Finding links | {stats.get('figure_finding_links', 0)} |",
        "",
        "## Per-Article Breakdown",
        "",
        "| DOI | Images | Stimuli | Charts | Plans | Links |",
        "|-----|--------|---------|--------|-------|-------|",
    ]
    
    for art in articles:
        cls = art.get("classifications", {})
        lines.append(
            f"| `{art['doi'][:40]}` | {art.get('images_extracted', 0)} "
            f"| {cls.get('stimulus', 0) + cls.get('photograph', 0)} "
            f"| {cls.get('chart', 0)} | {cls.get('floor_plan', 0)} "
            f"| {art.get('links_found', 0)} |"
        )
    
    lines.extend([
        "",
        "## Classification Distribution",
        "",
    ])
    
    type_stats = {k: v for k, v in stats.items() if k.startswith("type_")}
    for k, v in sorted(type_stats.items(), key=lambda x: -x[1]):
        name = k.replace("type_", "")
        bar = "█" * max(1, v // 2)
        lines.append(f"- **{name}**: {v} {bar}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    main()
