#!/usr/bin/env python3
"""
Assemble MASTER_DOC_CMR from individual Part files.

Reads all parts in order, concatenates them, and verifies against original.
"""

import argparse
import hashlib
import json
from pathlib import Path
from datetime import datetime

# Directories
PARTS_DIR = Path("/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/docs/master_doc_parts")
ORIGINAL_DOC = Path("/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/docs/MASTER_DOC_CMR_2026-02-25.md")
BACKUP_DIR = Path("/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/docs/backups")

# Part order (must match split_master_doc.py)
PART_ORDER = [
    "00_FRONTMATTER",
    "PART_I_EXPLANATION_GAP",
    "PART_II_THEORETICAL",
    "PART_III_PREDICTION",
    "PART_IV_CREDENCE",
    "PART_VI_DOMAIN_PANELS",
    "PART_VII_T15_REDUCTIONS",
    "PART_VIII_IE_DPT",
    "PART_IX_WEB_OF_BELIEF",
    "PART_X_TEMPLATE_LIBRARY",
    "PART_XI_ARCH_TYPOLOGY",
    "PART_XII_INTERACTIONS",
    "PART_XIII_LIMITATIONS",
    "PART_XIV_APPLICATIONS",
    "PART_XV_TECHNICAL",
    "PART_XVI_PHILOSOPHY",
    "PART_XVII_META_EPISTEMOLOGY",
    "PART_XVIII_INFRASTRUCTURE",
    "PART_XIX_TERMINOLOGY",
    "PART_XX_APPENDIX",
    "PART_XXI_SOURCE_INDEX",
]

def compute_hash(content):
    """Compute SHA-256 hash of content."""
    if isinstance(content, str):
        content = content.encode('utf-8')
    return hashlib.sha256(content).hexdigest()

def read_original():
    """Read and hash the original document."""
    with open(ORIGINAL_DOC, 'r', encoding='utf-8') as f:
        content = f.read()
    return content, compute_hash(content)

def assemble_parts():
    """Assemble all parts in order."""
    assembled = []
    part_info = []

    for part_name in PART_ORDER:
        part_file = PARTS_DIR / f"{part_name}.md"
        if not part_file.exists():
            print(f"WARNING: {part_file} not found, skipping")
            continue

        with open(part_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assembled.append(content)

        # Track metadata
        part_hash = compute_hash(content)
        stat = part_file.stat()
        part_info.append({
            'name': part_name,
            'lines': len(content.splitlines()),
            'chars': len(content),
            'sha256': part_hash,
            'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        })

    assembled_content = ''.join(assembled)
    return assembled_content, part_info

def write_manifest(part_info):
    """Write MANIFEST.md listing all parts."""
    manifest_path = PARTS_DIR / "MANIFEST.md"

    timestamp = datetime.now().isoformat()
    lines = [
        "# Master Doc Parts Manifest\n",
        f"\nGenerated: {timestamp}\n",
        f"\nTotal parts: {len(part_info)}\n",
        f"Total lines: {sum(p['lines'] for p in part_info)}\n",
        f"Total size: {sum(p['chars'] for p in part_info)} bytes\n",
        "\n## Parts\n",
        "\n| Part | Lines | Bytes | SHA-256 | Last Modified |\n",
        "|------|-------|-------|---------|---------------|\n",
    ]

    for part in part_info:
        lines.append(
            f"| {part['name']} | {part['lines']} | {part['chars']} | "
            f"{part['sha256']} | {part['last_modified']} |\n"
        )

    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    return manifest_path

def main():
    parser = argparse.ArgumentParser(description='Assemble MASTER_DOC from parts')
    parser.add_argument('--output', type=str, default=str(ORIGINAL_DOC.parent / 'MASTER_DOC_CMR_ASSEMBLED.md'),
                       help='Output path for assembled document')
    parser.add_argument('--diff', action='store_true',
                       help='Show diff from original (requires git)')
    args = parser.parse_args()

    print("Assembling MASTER_DOC from parts...")
    assembled_content, part_info = assemble_parts()
    assembled_hash = compute_hash(assembled_content)

    print(f"  {len(part_info)} parts assembled")
    print(f"  {len(assembled_content)} characters")
    print(f"  {len(assembled_content.splitlines())} lines")

    # Read original for comparison
    original_content, original_hash = read_original()

    print("\nVerifying assembly...")
    if assembled_hash == original_hash:
        print("✓ Perfect match with original")
    else:
        print("✗ Hash mismatch:")
        print(f"  Original:    {original_hash}")
        print(f"  Assembled:   {assembled_hash}")

        if len(assembled_content) != len(original_content):
            print(f"  Size mismatch: {len(original_content)} vs {len(assembled_content)}")

    # Write assembled doc
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(assembled_content)

    print(f"\nAssembled document written to: {output_path}")

    # Write manifest
    manifest_path = write_manifest(part_info)
    print(f"Manifest written to: {manifest_path}")

    # Show diff if requested
    if args.diff:
        import subprocess
        try:
            result = subprocess.run(
                ['git', 'diff', '--no-color', str(ORIGINAL_DOC), str(output_path)],
                capture_output=True, text=True
            )
            if result.stdout:
                print("\nDiff output:")
                print(result.stdout[:2000])  # First 2000 chars
                if len(result.stdout) > 2000:
                    print(f"... ({len(result.stdout)} total characters)")
            else:
                print("\n✓ No differences (files are identical)")
        except FileNotFoundError:
            print("\nWARNING: git not found, skipping diff")

if __name__ == '__main__':
    main()
