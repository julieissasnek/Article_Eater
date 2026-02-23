#!/usr/bin/env python3
"""
Extract Justification Narratives from Panel Docs
===================================================
For each template, finds the relevant section in its source panel document
and extracts the surrounding prose as a raw reasoning excerpt. This captures
the *argument* the panel made for why the template should exist — not just
reference lists, but the synthetic reasoning connecting evidence to claims.

Stores in each template JSON:
  - panel_reasoning_excerpt : str  — the raw prose extract
  - justification_status   : str  — 'raw_excerpt' | 'missing'
  - excerpt_source          : str  — path to source panel doc
  - excerpt_char_range      : list — [start, end] in source doc

Usage:
    python scripts/extract_justification_narratives.py --dry-run
    python scripts/extract_justification_narratives.py --apply
    python scripts/extract_justification_narratives.py --template PP_SPECTRAL_MATCH_001
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = PROJECT_ROOT / "data" / "templates"
DOCS_DIR = PROJECT_ROOT / "docs"

# All known panel docs (order = search priority)
PANEL_DOCS = [
    "docs/VISUAL_I_Panel_Output_Feb21.md",
    "docs/02-16_01_47_Panel_VIEW_I_Nature_View_V1_0.md",
    "docs/02-15_27_Panel_EI_Memory_Encoding_V1_0.md",
    "docs/02-15_25_Panel_VI_Gap_Closure_V1_0.md",
    "docs/02-15_20_Panel_V_Social_Brain_V1_0.md",
    "docs/02-15_14_Panel_IV_Cognitive_Control_Reward_V1_0.md",
    "docs/02-15_03_Panel_III_Multimodal_Senses_HigherCognition_V1.0.md",
    "docs/02-15_02_Neuroscience_Panel_Templates_and_Taxonomy_V1.0.md",
    "docs/02-15_01_Neuroscience_Panel_Tier1_Frameworks_V1.0.md",
    "docs/02-14_09_CMR_Revised_Spec_Panel_Templates_V2.0.md",
    "docs/44_Panel_SOC_I_Social_Config.md",
    "docs/42_Panel_TP_I_Temporal.md",
    "docs/38_Panel_SC_I_Spatial_Config.md",
    "docs/37_Panel_MAT_I_Materials.md",
    "docs/30_Panel_MIII_Musical_Emotion_Mechanisms_V1_0.md",
    "docs/29_Panel_MII_Rhythm_Groove_Motor_V1_0.md",
]


def load_panel_docs() -> Dict[str, str]:
    """Load all panel docs into memory."""
    docs = {}
    for pd in PANEL_DOCS:
        full_path = PROJECT_ROOT / pd
        if full_path.exists():
            try:
                docs[pd] = full_path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                pass
    return docs


def find_section_boundaries(content: str, template_id: str) -> Optional[Tuple[int, int]]:
    """Find the section of a panel doc that discusses this template.

    Strategy:
    1. Find the template_id mention
    2. Walk backward to the nearest heading (# or ##)
    3. Walk forward to the next heading or end of section
    4. Return the character range
    """
    pos = content.find(template_id)
    if pos < 0:
        return None

    # Walk backward to find section start (nearest heading or double newline)
    start = pos
    # Find the nearest markdown heading before this position
    before = content[:pos]
    heading_matches = list(re.finditer(r'\n(#{1,4}\s)', before))
    if heading_matches:
        start = heading_matches[-1].start() + 1  # Start at the heading
    else:
        # Fall back to double newline
        dn = before.rfind("\n\n")
        if dn >= 0:
            start = dn + 2
        else:
            start = max(0, pos - 2000)

    # Walk forward to find section end (next same-level heading or ## heading)
    after = content[pos:]
    # Find the next heading
    next_heading = re.search(r'\n(#{1,3}\s)', after[100:])  # Skip 100 chars to avoid self-match
    if next_heading:
        end = pos + 100 + next_heading.start()
    else:
        end = min(len(content), pos + 4000)

    # Enforce reasonable bounds (500-4000 chars)
    section_len = end - start
    if section_len < 200:
        # Section too small — expand window
        start = max(0, pos - 1000)
        end = min(len(content), pos + 3000)
    elif section_len > 6000:
        # Section too large — trim to reasonable excerpt
        end = start + 5000

    return (start, end)


def extract_reasoning_excerpt(content: str, start: int, end: int) -> str:
    """Clean up the extracted section into a readable excerpt."""
    raw = content[start:end]

    # Remove JSON code blocks (we want the prose, not the JSON)
    raw = re.sub(r'```json\s*\n[\s\S]*?\n```', '[JSON block omitted]', raw)
    raw = re.sub(r'```\w*\s*\n[\s\S]*?\n```', '[code block omitted]', raw)

    # Remove very long lines that are likely tables or data
    lines = raw.split("\n")
    cleaned = []
    for line in lines:
        if len(line) > 500 and "|" in line:
            continue  # Skip table rows
        cleaned.append(line)

    result = "\n".join(cleaned).strip()

    # Truncate if still too long
    if len(result) > 4000:
        result = result[:4000] + "\n\n[... excerpt truncated at 4000 chars]"

    return result


def process_template(
    template: Dict[str, Any],
    panel_docs: Dict[str, str],
) -> Dict[str, Any]:
    """Extract justification narrative for one template.

    Returns dict of new fields to add, or empty dict if nothing found.
    """
    tid = template.get("template_id", "")
    display_id = template.get("display_id", "")

    # Already has a narrative? Skip.
    if template.get("panel_reasoning_excerpt"):
        return {}

    # Search panel docs in priority order
    # First check the template's own panel_docs pointer
    known_docs = template.get("panel_docs", [])
    search_order = list(known_docs) + [d for d in PANEL_DOCS if d not in known_docs]

    for doc_path in search_order:
        doc_content = panel_docs.get(doc_path)
        if not doc_content:
            continue

        # Try template_id first, then display_id
        bounds = find_section_boundaries(doc_content, tid)
        if bounds is None and display_id:
            bounds = find_section_boundaries(doc_content, display_id)
        if bounds is None:
            continue

        start, end = bounds
        excerpt = extract_reasoning_excerpt(doc_content, start, end)

        if len(excerpt) < 100:
            continue  # Too short to be meaningful

        return {
            "panel_reasoning_excerpt": excerpt,
            "justification_status": "raw_excerpt",
            "excerpt_source": doc_path,
            "excerpt_char_range": [start, end],
        }

    return {
        "justification_status": "missing",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract justification narratives from panel docs.")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--apply", action="store_true", help="Write to template JSONs")
    parser.add_argument("--template", type=str, help="Process a single template")
    parser.add_argument("--show-excerpts", action="store_true", help="Print excerpts in dry-run")
    args = parser.parse_args()

    dry_run = not args.apply

    print("Loading panel documents...")
    panel_docs = load_panel_docs()
    print(f"  Loaded {len(panel_docs)} docs ({sum(len(v) for v in panel_docs.values()) // 1024}KB)")

    # Load templates
    templates = []
    template_paths = {}
    for fp in sorted(glob.glob(str(TEMPLATE_DIR / "*.json"))):
        if fp.endswith(".bak"):
            continue
        try:
            with open(fp) as f:
                t = json.load(f)
            if args.template and not t.get("template_id", "").startswith(args.template):
                continue
            templates.append(t)
            template_paths[t.get("template_id", "")] = fp
        except Exception:
            pass

    print(f"  Templates: {len(templates)}")

    # Process
    stats = {"processed": 0, "extracted": 0, "missing": 0, "already_has": 0}
    excerpt_lengths = []

    for t in templates:
        tid = t.get("template_id", "")
        stats["processed"] += 1

        if t.get("panel_reasoning_excerpt"):
            stats["already_has"] += 1
            continue

        changes = process_template(t, panel_docs)

        if changes.get("panel_reasoning_excerpt"):
            stats["extracted"] += 1
            excerpt_lengths.append(len(changes["panel_reasoning_excerpt"]))

            if args.show_excerpts:
                print(f"\n{'─'*60}")
                print(f"  {tid} ({changes.get('excerpt_source', '?')})")
                print(f"{'─'*60}")
                print(changes["panel_reasoning_excerpt"][:500])
                print("...")

            if not dry_run:
                for key, value in changes.items():
                    t[key] = value
                fp = template_paths.get(tid, "")
                if fp:
                    with open(fp, "w") as f:
                        json.dump(t, f, indent=2, ensure_ascii=False)
        else:
            stats["missing"] += 1

    # Report
    avg_len = sum(excerpt_lengths) / max(len(excerpt_lengths), 1)

    print(f"\n{'='*60}")
    print(f"JUSTIFICATION NARRATIVE EXTRACTION {'(DRY RUN)' if dry_run else 'RESULTS'}")
    print(f"{'='*60}")
    print(f"  Templates processed:    {stats['processed']}")
    print(f"  Already had narrative:  {stats['already_has']}")
    print(f"  Excerpts extracted:     {stats['extracted']}")
    print(f"  No panel doc match:     {stats['missing']}")
    print(f"  Avg excerpt length:     {avg_len:.0f} chars")

    if dry_run:
        print(f"\n  [DRY RUN] Use --apply to write to template JSONs")
        print(f"  Tip: Use --show-excerpts to preview the extracted text")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
