#!/usr/bin/env python3
"""
Backfill Template Provenance from Panel Docs
==============================================
Mines the 16 panel source markdown documents to enrich template JSONs
with provenance data that was not captured during initial JSON extraction.

Safe backfill targets (never overwrites existing data):
  - panel_docs       — backward pointer to source doc(s)
  - panel_source     — human-readable panel name
  - key_references   — APA citations found near template mention

Usage:
    python scripts/backfill_provenance.py --dry-run     # Preview changes
    python scripts/backfill_provenance.py --apply        # Write to JSONs
    python scripts/backfill_provenance.py --template T1  # Single template
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = PROJECT_ROOT / "data" / "templates"
DOCS_DIR = PROJECT_ROOT / "docs"

# All known panel docs
PANEL_DOCS = [
    "docs/02-14_09_CMR_Revised_Spec_Panel_Templates_V2.0.md",
    "docs/02-15_01_Neuroscience_Panel_Tier1_Frameworks_V1.0.md",
    "docs/02-15_02_Neuroscience_Panel_Templates_and_Taxonomy_V1.0.md",
    "docs/02-15_03_Panel_III_Multimodal_Senses_HigherCognition_V1.0.md",
    "docs/02-15_14_Panel_IV_Cognitive_Control_Reward_V1_0.md",
    "docs/02-15_20_Panel_V_Social_Brain_V1_0.md",
    "docs/02-15_25_Panel_VI_Gap_Closure_V1_0.md",
    "docs/02-15_27_Panel_EI_Memory_Encoding_V1_0.md",
    "docs/02-16_01_47_Panel_VIEW_I_Nature_View_V1_0.md",
    "docs/29_Panel_MII_Rhythm_Groove_Motor_V1_0.md",
    "docs/30_Panel_MIII_Musical_Emotion_Mechanisms_V1_0.md",
    "docs/37_Panel_MAT_I_Materials.md",
    "docs/38_Panel_SC_I_Spatial_Config.md",
    "docs/42_Panel_TP_I_Temporal.md",
    "docs/44_Panel_SOC_I_Social_Config.md",
    "docs/VISUAL_I_Panel_Output_Feb21.md",
]

# Panel name extraction patterns
PANEL_NAME_PATTERNS = [
    (r"Panel_SC_I", "SC-I (Spatial Configuration)"),
    (r"Panel_MAT_I", "MAT-I (Materials)"),
    (r"Panel_TP_I", "TP-I (Temporal)"),
    (r"Panel_SOC_I", "SOC-I (Social Configuration)"),
    (r"Panel_MII", "M-II (Rhythm & Groove Motor)"),
    (r"Panel_MIII", "M-III (Musical Emotion)"),
    (r"Panel_III", "Panel III (Multimodal Senses)"),
    (r"Panel_IV", "Panel IV (Cognitive Control & Reward)"),
    (r"Panel_V", "Panel V (Social Brain)"),
    (r"Panel_VI", "Panel VI (Gap Closure)"),
    (r"Panel_EI", "EI (Memory Encoding)"),
    (r"Panel_VIEW_I|VIEW_I", "VIEW-I (Nature View)"),
    (r"VISUAL_I", "VISUAL-I (Visual Cognition)"),
    (r"Tier1_Frameworks", "Tier 1 Frameworks"),
    (r"Neuroscience_Panel_Templates", "Neuroscience Panel (Templates & Taxonomy)"),
    (r"CMR_Revised", "CMR (Revised Spec)"),
]


def extract_panel_name(doc_path: str) -> str:
    """Extract a human-readable panel name from a doc path."""
    basename = os.path.basename(doc_path)
    for pattern, name in PANEL_NAME_PATTERNS:
        if re.search(pattern, basename):
            return name
    return basename


# ═══════════════════════════════════════════════════════════════════════
# Panel document loading and indexing
# ═══════════════════════════════════════════════════════════════════════

def load_panel_docs() -> Dict[str, str]:
    """Load all panel docs into memory. Returns {path: content}."""
    docs = {}
    for pd in PANEL_DOCS:
        full_path = PROJECT_ROOT / pd
        if full_path.exists():
            try:
                docs[pd] = full_path.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                print(f"  Warning: could not read {pd}: {e}")
    return docs


def find_template_in_doc(template_id: str, doc_content: str) -> Optional[int]:
    """Find the character position of a template ID mention in a doc."""
    # Try exact match first
    pos = doc_content.find(template_id)
    if pos >= 0:
        return pos

    # Try display_id variants (e.g., "T1" for PP_SPECTRAL_MATCH_001)
    return None


def extract_surrounding_references(doc_content: str, pos: int, window: int = 5000) -> List[str]:
    """Extract APA-style references near a template mention."""
    start = max(0, pos - window)
    end = min(len(doc_content), pos + window)
    context = doc_content[start:end]

    refs = []
    for line in context.split("\n"):
        line = line.strip().lstrip("- •*>")
        # Look for lines that look like APA references:
        # - Contains (YYYY) and is reasonably long
        # - Starts with a capitalized word (likely author name)
        if (len(line) > 50
                and re.search(r'\(\d{4}[a-z]?\)', line)
                and re.match(r'[A-Z]', line)
                and not line.startswith(('#', '|', '**Key', '**PANEL', '**Panel',
                                         '```', '<!--', 'PHASE', 'Step'))):
            # Clean up
            ref = line.strip()
            if len(ref) > 30:
                refs.append(ref)

    return list(dict.fromkeys(refs))[:15]  # Deduplicate, cap at 15


def extract_confidence_mentions(doc_content: str, pos: int, window: int = 2000) -> Optional[str]:
    """Extract confidence/maturity mentions near a template."""
    start = max(0, pos - window)
    end = min(len(doc_content), pos + window)
    context = doc_content[start:end]

    # Look for confidence patterns
    patterns = [
        r'confidence[:\s]+(\d+\.?\d*)',
        r'maturity[:\s]+"?(\w+[-\w]*)"?',
        r'overall_confidence[:\s]+(\d+\.?\d*)',
        r'warrant[:\s]+"?(\w+[-\w]*)"?',
    ]
    for pat in patterns:
        m = re.search(pat, context, re.IGNORECASE)
        if m:
            return m.group(0)
    return None


# ═══════════════════════════════════════════════════════════════════════
# Main backfill logic
# ═══════════════════════════════════════════════════════════════════════

def backfill_template(
    template: Dict[str, Any],
    panel_docs: Dict[str, str],
) -> Dict[str, Any]:
    """Attempt to backfill provenance fields for a single template.

    Returns dict of fields that would be added/updated.
    """
    tid = template.get("template_id", "")
    display_id = template.get("display_id", "")
    name = template.get("name", template.get("template_name", ""))
    changes: Dict[str, Any] = {}

    # ─── Find which panel docs mention this template ───
    found_in_docs: List[str] = []
    doc_positions: Dict[str, int] = {}

    existing_panel_docs = template.get("panel_docs", [])

    for doc_path, doc_content in panel_docs.items():
        # Search by template_id
        pos = find_template_in_doc(tid, doc_content)
        if pos is None and display_id:
            pos = find_template_in_doc(display_id, doc_content)
        if pos is not None:
            found_in_docs.append(doc_path)
            doc_positions[doc_path] = pos

    # ─── Backfill panel_docs (backward pointers) ───
    if not existing_panel_docs and found_in_docs:
        changes["panel_docs"] = found_in_docs
    elif existing_panel_docs:
        # Add any new docs not already listed
        new_docs = [d for d in found_in_docs if d not in existing_panel_docs]
        if new_docs:
            changes["panel_docs"] = existing_panel_docs + new_docs

    # ─── Backfill panel_source ───
    if not template.get("panel_source") and not template.get("panel"):
        if found_in_docs:
            changes["panel_source"] = extract_panel_name(found_in_docs[0])

    # ─── Backfill key_references ───
    existing_refs = (
        template.get("key_references")
        or template.get("citations")
        or template.get("references")
        or template.get("apa_references")
    )
    if not existing_refs:
        all_refs = []
        for doc_path, pos in doc_positions.items():
            refs = extract_surrounding_references(panel_docs[doc_path], pos)
            all_refs.extend(refs)
        if all_refs:
            # Deduplicate
            unique_refs = list(dict.fromkeys(all_refs))[:15]
            changes["key_references"] = unique_refs

    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill template provenance from panel docs.")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--apply", action="store_true", help="Write changes to template JSONs")
    parser.add_argument("--template", type=str, help="Backfill a single template")
    args = parser.parse_args()

    dry_run = not args.apply

    # Load panel docs
    print("Loading panel documents...")
    panel_docs = load_panel_docs()
    print(f"  Loaded {len(panel_docs)} panel docs ({sum(len(v) for v in panel_docs.values()) // 1024}KB total)")

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

    print(f"  Templates to process: {len(templates)}")

    # Process each template
    stats = {
        "processed": 0,
        "enriched": 0,
        "panel_docs_added": 0,
        "panel_source_added": 0,
        "references_added": 0,
        "no_match": 0,
    }

    for t in templates:
        tid = t.get("template_id", "")
        changes = backfill_template(t, panel_docs)
        stats["processed"] += 1

        if changes:
            stats["enriched"] += 1
            if "panel_docs" in changes:
                stats["panel_docs_added"] += 1
            if "panel_source" in changes:
                stats["panel_source_added"] += 1
            if "key_references" in changes:
                stats["references_added"] += 1

            if not dry_run:
                # Apply changes to template
                for key, value in changes.items():
                    t[key] = value

                # Write back
                fp = template_paths.get(tid, "")
                if fp:
                    with open(fp, "w") as f:
                        json.dump(t, f, indent=2, ensure_ascii=False)
        else:
            # Check if template was found in any doc
            found = False
            for doc_content in panel_docs.values():
                if tid in doc_content:
                    found = True
                    break
            if not found:
                stats["no_match"] += 1

    # Report
    print(f"\n{'='*60}")
    print(f"PROVENANCE BACKFILL {'(DRY RUN)' if dry_run else 'RESULTS'}")
    print(f"{'='*60}")
    print(f"  Templates processed: {stats['processed']}")
    print(f"  Templates enriched:  {stats['enriched']}")
    print(f"  Panel docs added:    {stats['panel_docs_added']}")
    print(f"  Panel source added:  {stats['panel_source_added']}")
    print(f"  References added:    {stats['references_added']}")
    print(f"  No panel match:      {stats['no_match']}")

    if dry_run:
        print(f"\n  [DRY RUN] Use --apply to write changes to template JSONs")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
