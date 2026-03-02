#!/usr/bin/env python3
"""
Split MASTER_DOC_CMR_2026-02-25.md into individual Part files.

This script is lossless: concatenating all parts reproduces the original exactly.
Part boundaries are detected dynamically by scanning for Part header patterns.
"""

import os
import re
from pathlib import Path

# Document to split
MASTER_DOC = "/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/docs/MASTER_DOC_CMR_2026-02-25.md"
OUTPUT_DIR = "/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/docs/master_doc_parts"

# Map Part header patterns to filenames
# Order matters: we scan top-to-bottom and assign each range
PART_PATTERNS = [
    (r"^#{1,2}\s+PART\s+I[:\s]", "PART_I_EXPLANATION_GAP"),
    (r"^#{1,2}\s+PART\s+II[:\s]", "PART_II_THEORETICAL"),
    (r"^#{1,2}\s+PART\s+III[:\s]", "PART_III_PREDICTION"),
    (r"^#{1,2}\s+PART\s+IV[:\s]", "PART_IV_CREDENCE"),
    (r"^#{1,2}\s+PART\s+V[:\s]", "PART_V_PANEL_CONVENING"),
    (r"^#{1,2}\s+PART\s+VI[:\s]", "PART_VI_DOMAIN_PANELS"),
    (r"^#{1,2}\s+PART\s+VII[:\s]", "PART_VII_T15_REDUCTIONS"),
    (r"^#{1,2}\s+PART\s+VIII[:\s]", "PART_VIII_IE_DPT"),
    (r"^#{1,2}\s+PART\s+IX[:\s]", "PART_IX_WEB_OF_BELIEF"),
    (r"^#{1,2}\s+PARTS?\s+X[:\s–-]", "PART_X_TEMPLATE_LIBRARY"),
    (r"^#{1,2}\s+PART\s+XI[:\s]", "PART_XI_ARCH_TYPOLOGY"),
    (r"^#{1,2}\s+PARTS?\s+XII[:\s]", "PART_XII_INTERACTIONS"),
    (r"^#{1,2}\s+PARTS?\s+XIII[:\s–-]", "PART_XIII_LIMITATIONS"),
    (r"^#{1,2}\s+PART\s+XIV[:\s]", "PART_XIV_APPLICATIONS"),
    (r"^#{1,2}\s+PART\s+XV[:\s]", "PART_XV_TECHNICAL"),
    (r"^#{1,2}\s+PART\s+XVI[:\s]", "PART_XVI_PHILOSOPHY"),
    (r"^#{1,2}\s+PART\s+XVII[:\s]", "PART_XVII_META_EPISTEMOLOGY"),
    (r"^#{1,2}\s+PART\s+XVIII[:\s]", "PART_XVIII_INFRASTRUCTURE"),
    (r"^#{1,2}\s+PART\s+XIX[:\s]", "PART_XIX_TERMINOLOGY"),
    (r"^#{1,2}\s+PART\s+XX[:\s]", "PART_XX_APPENDIX"),
    (r"^#{1,2}\s+PART\s+XXI[:\s]", "PART_XXI_SOURCE_INDEX"),
]

# Some parts appear multiple times (e.g., "PART II" as TOC entry and later as content).
# We handle this by taking the FIRST content occurrence after line 155 (past the TOC).
FRONTMATTER_END_HEURISTIC = 155  # TOC and navigation typically in first ~155 lines


def read_master_doc():
    """Read the master document as a list of lines (preserving newlines)."""
    with open(MASTER_DOC, 'r', encoding='utf-8') as f:
        return f.readlines()


def find_part_boundaries(all_lines):
    """
    Dynamically detect Part boundaries by scanning for header patterns.

    Returns list of (part_name, start_line_1indexed, end_line_1indexed) in document order.
    """
    total = len(all_lines)

    # First pass: find ALL occurrences of each Part header
    header_hits = []  # (line_number_1indexed, part_name)

    for line_idx, line in enumerate(all_lines):
        line_num = line_idx + 1
        stripped = line.strip()
        for pattern, part_name in PART_PATTERNS:
            if re.match(pattern, stripped):
                header_hits.append((line_num, part_name))
                break  # only match first pattern per line

    # Deduplicate: for each part_name, keep the FIRST occurrence that is
    # either (a) after the TOC region, or (b) the only occurrence.
    # But some parts genuinely start in the TOC as a one-liner placeholder
    # (e.g., "## PART I: THE EXPLANATION GAP AND 30 WORKED EXAMPLES (Sections 1–32)")
    # We want those too — they are the actual content start.

    # Strategy: group by part_name, take first occurrence
    seen = {}
    unique_hits = []
    for line_num, part_name in header_hits:
        if part_name not in seen:
            seen[part_name] = line_num
            unique_hits.append((line_num, part_name))

    # Sort by line number
    unique_hits.sort(key=lambda x: x[0])

    # Determine frontmatter: everything before the first Part header
    if unique_hits:
        frontmatter_end = unique_hits[0][0] - 1
    else:
        frontmatter_end = total

    # Build part ranges
    parts = [("00_FRONTMATTER", 1, frontmatter_end)]

    for i, (start, part_name) in enumerate(unique_hits):
        if i + 1 < len(unique_hits):
            end = unique_hits[i + 1][0] - 1
        else:
            end = total
        parts.append((part_name, start, end))

    return parts


def write_part(filename, lines):
    """Write part to file."""
    output_path = Path(OUTPUT_DIR) / f"{filename}.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    line_count = len(lines)
    char_count = sum(len(line) for line in lines)
    print(f"  {filename}: {line_count} lines, {char_count} characters")
    return line_count


def main():
    print(f"Reading master document from: {MASTER_DOC}")
    all_lines = read_master_doc()
    total_lines = len(all_lines)
    print(f"Total lines in master doc: {total_lines}\n")

    print(f"Creating output directory: {OUTPUT_DIR}")
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    # Detect boundaries dynamically
    parts = find_part_boundaries(all_lines)
    print(f"Detected {len(parts)} parts\n")
    print("Splitting into parts...\n")

    total_written = 0
    part_order = []
    for part_name, start, end in parts:
        part_lines = all_lines[start - 1 : end]
        n = write_part(part_name, part_lines)
        total_written += n
        part_order.append(part_name)

    # Verify losslessness
    print(f"\nVerifying losslessness... (wrote {total_written} lines, original {total_lines})")
    reconstructed = []
    for part_name in part_order:
        part_path = Path(OUTPUT_DIR) / f"{part_name}.md"
        with open(part_path, 'r', encoding='utf-8') as f:
            reconstructed.extend(f.readlines())

    if len(reconstructed) == total_lines:
        print("✓ Line count matches")
    else:
        print(f"✗ Line count mismatch: reconstructed {len(reconstructed)}, original {total_lines}")

    # Character-level check
    original_text = ''.join(all_lines)
    reconstructed_text = ''.join(reconstructed)

    if original_text == reconstructed_text:
        print("✓ Perfect byte-for-byte match")
        print(f"\nSplit complete: {len(parts)} parts created")
    else:
        print(f"✗ Content mismatch:")
        print(f"  Original: {len(original_text)} characters")
        print(f"  Reconstructed: {len(reconstructed_text)} characters")
        for i, (o, r) in enumerate(zip(original_text, reconstructed_text)):
            if o != r:
                context_start = max(0, i - 40)
                print(f"  First difference at character {i}")
                print(f"  Original context: ...{repr(original_text[context_start:i+40])}...")
                print(f"  Reconstructed:    ...{repr(reconstructed_text[context_start:i+40])}...")
                break

    # Write manifest
    manifest_path = Path(OUTPUT_DIR) / "MANIFEST.md"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write("# Master Document Parts Manifest\n\n")
        f.write(f"*Generated from split of {total_lines}-line master doc*\n\n")
        f.write("| Part | File | Lines | Characters |\n")
        f.write("|------|------|------:|----------:|\n")
        for part_name, start, end in parts:
            part_path = Path(OUTPUT_DIR) / f"{part_name}.md"
            with open(part_path, 'r', encoding='utf-8') as pf:
                content = pf.read()
            nlines = content.count('\n')
            nchars = len(content)
            f.write(f"| {part_name} | {part_name}.md | {nlines} | {nchars} |\n")
        f.write(f"\n**Total**: {total_lines} lines\n")


if __name__ == '__main__':
    main()
