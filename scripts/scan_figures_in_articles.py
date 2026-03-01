#!/usr/bin/env python3
"""AI Figure Scanner — Cheap triage to identify articles with images.

Scans extraction JSONs to find references to figures, images, and stimuli
in the article text. Reads extraction metadata + finding text to identify:
  1. Articles that reference figures (fig/figure/image/photo/stimulus)
  2. Caption-like text near figure references
  3. Figure numbering (Fig 1, Figure 2, Image 3, etc.)

Uses only text analysis — no AI API calls needed for basic scan.
For enhanced mode, can use Gemini Flash to classify figure types.

Usage:
    python scripts/scan_figures_in_articles.py                    # Basic text scan
    python scripts/scan_figures_in_articles.py --enhanced         # + AI classification
    python scripts/scan_figures_in_articles.py --output report    # Generate full report
"""

import argparse
import json
import re
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
EXTRACTIONS_DIR = PROJECT_ROOT / "data" / "extractions"
PDF_DIR = Path("/Users/davidusa/REPOS/Article_Finder_v3_2_3/data/pdfs")
OUTPUT_DIR = PROJECT_ROOT / "data" / "figure_scan"


# =============================================================================
# Figure Reference Patterns
# =============================================================================

FIGURE_PATTERNS = [
    # Standard figure references
    re.compile(r'\b(?:fig(?:ure)?|figure)\s*\.?\s*(\d+)', re.IGNORECASE),
    # Image references
    re.compile(r'\b(?:image|photo(?:graph)?|picture|plate)\s*\.?\s*(\d+)', re.IGNORECASE),
    # Table references (useful for context)
    re.compile(r'\b(?:table)\s*\.?\s*(\d+)', re.IGNORECASE),
    # Stimulus references
    re.compile(r'\b(?:stimulus|stimuli)\b', re.IGNORECASE),
    # Visual stimuli patterns
    re.compile(r'\b(?:visual\s+(?:stimulus|stimuli|scene|display|environment))', re.IGNORECASE),
    # Experimental paradigm with images
    re.compile(r'\b(?:photograph|image|picture)\s+(?:of|showing|depicting)', re.IGNORECASE),
]

# Patterns suggesting the article contains experimental stimuli
STIMULUS_PATTERNS = [
    re.compile(r'\b(?:participants?\s+(?:viewed|saw|were\s+shown|rated))', re.IGNORECASE),
    re.compile(r'\b(?:images?\s+(?:were|of)\s+(?:presented|shown|displayed))', re.IGNORECASE),
    re.compile(r'\b(?:visual\s+prefer)', re.IGNORECASE),
    re.compile(r'\b(?:rating\s+(?:task|scale|study))', re.IGNORECASE),
    re.compile(r'\b(?:eye[\s-]?track)', re.IGNORECASE),
    re.compile(r'\b(?:scene\s+(?:perception|viewing|rating|evaluation))', re.IGNORECASE),
    re.compile(r'\b(?:virtual\s+(?:environment|reality|tour))', re.IGNORECASE),
]

# Caption patterns
CAPTION_PATTERNS = [
    re.compile(r'(?:fig(?:ure)?|figure)\s*\.?\s*\d+\s*[.:]\s*(.{10,200})', re.IGNORECASE),
    re.compile(r'(?:image|photo)\s*\d+\s*[.:]\s*(.{10,200})', re.IGNORECASE),
]


def scan_extraction(filepath: Path) -> dict:
    """Scan a single extraction JSON for figure/image references."""
    with open(filepath) as f:
        data = json.load(f)
    
    doi = filepath.stem
    result = {
        "doi": doi,
        "filepath": str(filepath),
        "has_pdf": (PDF_DIR / (doi + ".pdf")).exists(),
        "figure_refs": [],
        "stimulus_indicators": [],
        "captions": [],
        "figure_count_estimate": 0,
        "has_stimulus_experiment": False,
        "priority": "low",  # low, medium, high
    }
    
    # Collect all text from the extraction
    all_text = []
    
    # Check top-level text fields
    for field in ["title", "abstract", "methodology", "discussion", "conclusions"]:
        if field in data and isinstance(data[field], str):
            all_text.append(data[field])
    
    # Check findings text
    if "findings" in data:
        for finding in data["findings"]:
            for text_field in ["antecedent", "consequent", "quote", "mechanism", "source"]:
                if text_field in finding and isinstance(finding[text_field], str):
                    all_text.append(finding[text_field])
    
    # Check panel data if present
    if "panels" in data:
        for panel in data.get("panels", []):
            if isinstance(panel, dict):
                for v in panel.values():
                    if isinstance(v, str):
                        all_text.append(v)
    
    full_text = " ".join(all_text)
    
    # Scan for figure references
    figure_numbers = set()
    for pattern in FIGURE_PATTERNS:
        for match in pattern.finditer(full_text):
            ref_text = match.group(0)
            result["figure_refs"].append(ref_text)
            # Extract number if present
            num_match = re.search(r'\d+', ref_text)
            if num_match:
                figure_numbers.add(int(num_match.group(0)))
    
    result["figure_count_estimate"] = len(figure_numbers)
    
    # Scan for stimulus indicators
    for pattern in STIMULUS_PATTERNS:
        for match in pattern.finditer(full_text):
            result["stimulus_indicators"].append(match.group(0))
    
    result["has_stimulus_experiment"] = len(result["stimulus_indicators"]) > 0
    
    # Extract caption-like text
    for pattern in CAPTION_PATTERNS:
        for match in pattern.finditer(full_text):
            result["captions"].append(match.group(0).strip())
    
    # Classify priority
    if result["has_stimulus_experiment"] and result["figure_count_estimate"] > 0:
        result["priority"] = "high"
    elif result["figure_count_estimate"] > 2 or result["has_stimulus_experiment"]:
        result["priority"] = "medium"
    elif result["figure_count_estimate"] > 0:
        result["priority"] = "low"
    else:
        result["priority"] = "none"
    
    return result


def scan_all_extractions(extractions_dir: Path) -> list:
    """Scan all extraction JSONs in a directory."""
    results = []
    json_files = sorted(extractions_dir.glob("*.json"))
    
    print(f"Scanning {len(json_files)} extraction files...")
    
    for i, filepath in enumerate(json_files):
        try:
            result = scan_extraction(filepath)
            results.append(result)
        except Exception as e:
            print(f"  ERROR scanning {filepath.name}: {e}")
        
        if (i + 1) % 100 == 0:
            print(f"  Scanned {i + 1}/{len(json_files)}...")
    
    return results


def generate_report(results: list, output_dir: Path) -> dict:
    """Generate a summary report from scan results."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Classify
    by_priority = defaultdict(list)
    for r in results:
        by_priority[r["priority"]].append(r)
    
    summary = {
        "scan_date": datetime.utcnow().isoformat() + "Z",
        "total_articles": len(results),
        "with_figures": sum(1 for r in results if r["figure_count_estimate"] > 0),
        "with_stimuli": sum(1 for r in results if r["has_stimulus_experiment"]),
        "with_pdfs": sum(1 for r in results if r["has_pdf"]),
        "priority_high": len(by_priority["high"]),
        "priority_medium": len(by_priority["medium"]),
        "priority_low": len(by_priority["low"]),
        "priority_none": len(by_priority["none"]),
        "total_figure_refs": sum(len(r["figure_refs"]) for r in results),
        "total_captions_found": sum(len(r["captions"]) for r in results),
    }
    
    # Save full results
    with open(output_dir / "figure_scan_results.json", "w") as f:
        json.dump({"summary": summary, "results": results}, f, indent=2)
    
    # Save high-priority list (for focused extraction)
    high_priority = [
        {
            "doi": r["doi"],
            "has_pdf": r["has_pdf"],
            "figure_count": r["figure_count_estimate"],
            "stimulus_indicators": r["stimulus_indicators"][:3],
            "captions": r["captions"][:3],
        }
        for r in by_priority["high"]
    ]
    with open(output_dir / "high_priority_articles.json", "w") as f:
        json.dump(high_priority, f, indent=2)
    
    # Generate markdown report
    md_lines = [
        "# Figure & Stimulus Scan Report",
        f"\n**Scan Date**: {summary['scan_date']}",
        f"\n## Summary\n",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Total articles scanned | {summary['total_articles']} |",
        f"| Articles with figure refs | {summary['with_figures']} |",
        f"| Articles with stimulus experiments | {summary['with_stimuli']} |",
        f"| Articles with available PDFs | {summary['with_pdfs']} |",
        f"| **Priority: HIGH** (figures + stimuli) | **{summary['priority_high']}** |",
        f"| Priority: MEDIUM | {summary['priority_medium']} |",
        f"| Priority: LOW | {summary['priority_low']} |",
        f"| Priority: NONE | {summary['priority_none']} |",
        f"| Total figure references found | {summary['total_figure_refs']} |",
        f"| Total captions extracted | {summary['total_captions_found']} |",
        f"\n## High-Priority Articles (Figures + Stimulus Experiments)\n",
    ]
    
    for r in by_priority["high"][:30]:
        md_lines.append(f"### {r['doi']}")
        md_lines.append(f"- **Figures**: ~{r['figure_count_estimate']} | **PDF available**: {'✅' if r['has_pdf'] else '❌'}")
        if r["stimulus_indicators"]:
            md_lines.append(f"- **Stimulus patterns**: {', '.join(r['stimulus_indicators'][:5])}")
        if r["captions"]:
            md_lines.append(f"- **Captions found**:")
            for cap in r["captions"][:3]:
                md_lines.append(f"  - {cap}")
        md_lines.append("")
    
    if len(by_priority["high"]) > 30:
        md_lines.append(f"\n... and {len(by_priority['high']) - 30} more high-priority articles.\n")
    
    md_lines.append("\n## Extraction Recommendations\n")
    md_lines.append("1. **Run PDF image extraction** on all HIGH-priority articles with available PDFs")
    md_lines.append("2. **Classify extracted images** using cheap VLM (stimulus photo? chart? diagram?)")
    md_lines.append("3. **Link to findings** — match figure references to corresponding findings")
    md_lines.append("4. **Tag with feature taxonomy** — apply image tagger features to stimulus images")
    
    with open(output_dir / "figure_scan_report.md", "w") as f:
        f.write("\n".join(md_lines))
    
    return summary


def main():
    parser = argparse.ArgumentParser(description="Scan extractions for figure/image references")
    parser.add_argument("--dir", type=str, default=str(EXTRACTIONS_DIR),
                        help="Directory of extraction JSONs")
    parser.add_argument("--output", type=str, default=str(OUTPUT_DIR),
                        help="Output directory for reports")
    parser.add_argument("--enhanced", action="store_true",
                        help="Use Gemini Flash for AI classification (costs ~$2-5)")
    parser.add_argument("--single", type=str, help="Scan a single extraction file")
    args = parser.parse_args()
    
    if args.single:
        result = scan_extraction(Path(args.single))
        print(json.dumps(result, indent=2))
        return
    
    extractions_dir = Path(args.dir)
    output_dir = Path(args.output)
    
    results = scan_all_extractions(extractions_dir)
    summary = generate_report(results, output_dir)
    
    print(f"\n{'='*60}")
    print(f"SCAN COMPLETE")
    print(f"{'='*60}")
    print(f"Total articles: {summary['total_articles']}")
    print(f"With figures:   {summary['with_figures']}")
    print(f"With stimuli:   {summary['with_stimuli']}")
    print(f"With PDFs:      {summary['with_pdfs']}")
    print(f"HIGH priority:  {summary['priority_high']}")
    print(f"\nReports saved to: {output_dir}")
    print(f"  - figure_scan_results.json (full data)")
    print(f"  - high_priority_articles.json (extraction targets)")
    print(f"  - figure_scan_report.md (human-readable)")


if __name__ == "__main__":
    main()
