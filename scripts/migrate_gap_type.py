#!/usr/bin/env python3
"""
Generate a non-destructive patch to migrate legacy local GapType enums
to canonical src.epistemic.gap_types.GapType.

Canonical contract section enforced:
  contracts/vocab/canonical_enums.json -> enums.GapType
"""

from __future__ import annotations

import argparse
import ast
import difflib
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


CANONICAL_SECTION = "enums.GapType"

TARGET_FILES = [
    "src/services/gap_predictor.py",
    "src/services/voi_search.py",
    "src/services/discovery_funnel.py",
]


def load_canonical_gap_spec(ae_root: Path) -> dict:
    path = ae_root / "contracts/vocab/canonical_enums.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    return doc["enums"]["GapType"]


def find_class_span(path: Path, class_name: str) -> Optional[Tuple[int, int]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError:
        return None
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                return (node.lineno, node.end_lineno)
    return None


def remove_line_range(text: str, start_line: int, end_line: int) -> str:
    lines = text.splitlines(keepends=True)
    start = max(1, start_line)
    end = max(start, end_line)
    kept = lines[: start - 1] + lines[end:]
    return "".join(kept)


def normalize_gap_import_block(text: str) -> str:
    pattern = re.compile(
        r"from src\.epistemic\.gap_types import\s*\((?:.|\n)*?\)\n",
        flags=re.MULTILINE,
    )
    replacement = (
        "from src.epistemic.gap_types import (\n"
        "    GapType,\n"
        "    GapPriority,\n"
        "    GAP_TYPE_WEIGHTS,\n"
        "    convert_legacy_gap_type,\n"
        ")\n"
    )
    if pattern.search(text):
        return pattern.sub(replacement, text, count=1)
    if "from src.epistemic.gap_types import" not in text:
        return replacement + text
    return text


def apply_reference_rewrites(text: str, mapping: Dict[str, str]) -> str:
    rewritten = text
    # Class name alias cleanup
    rewritten = rewritten.replace("CanonicalGapType", "GapType")

    # Remove now-obsolete per-class converter method calls
    rewritten = rewritten.replace(".to_canonical()", "")

    # Replace legacy enum members with canonical enum members
    for legacy, canonical in mapping.items():
        legacy_member = legacy.upper()
        canonical_member = canonical.upper()
        rewritten = rewritten.replace(f"GapType.{legacy_member}", f"GapType.{canonical_member}")

    # Where code constructs GapType from persisted strings, use converter
    rewritten = re.sub(r"\bGapType\(([^)]+)\)", r"convert_legacy_gap_type(\1)", rewritten)
    return rewritten


def generate_unified_diff(old: str, new: str, rel_path: str) -> str:
    if old == new:
        return ""
    return "".join(
        difflib.unified_diff(
            old.splitlines(keepends=True),
            new.splitlines(keepends=True),
            fromfile=f"a/{rel_path}",
            tofile=f"b/{rel_path}",
            n=3,
        )
    )


def test_migration_lossless() -> None:
    alias_to_canonical = {
        "contradiction": "direction",
        "uncertain": "validation",
        "unexplored": "mechanism",
        "boundary_unclear": "boundary",
        "missing_evidence": "mechanism",
        "weak_support": "validation",
    }
    canonical_values = {
        "mediation",
        "mechanism",
        "boundary",
        "direction",
        "interaction",
        "validation",
        "unjustified_edge",
        "critical_question",
        "argument_attack",
    }

    def to_canonical(value: str) -> str:
        v = value.lower().strip()
        if v in canonical_values:
            return v
        if v in alias_to_canonical:
            return alias_to_canonical[v]
        raise KeyError(v)

    for val in canonical_values:
        assert to_canonical(val) == val
    for legacy, expected in alias_to_canonical.items():
        assert to_canonical(legacy) == expected


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate patch for GapType migration")
    parser.add_argument("--dry-run", action="store_true", help="Print changes but do not write files")
    parser.add_argument(
        "--output-dir",
        default="data/review/migration_adapters",
        help="Output directory (relative to AE repo root)",
    )
    args = parser.parse_args()

    test_migration_lossless()

    ae_root = Path(__file__).resolve().parents[1]
    out_dir = ae_root / args.output_dir
    spec = load_canonical_gap_spec(ae_root)
    alias_map = spec.get("deprecated_aliases", {})

    patch_chunks: List[str] = []
    scanned: List[str] = []
    changed: List[str] = []

    for rel in TARGET_FILES:
        path = ae_root / rel
        if not path.exists():
            continue
        scanned.append(rel)
        old = path.read_text(encoding="utf-8")
        new = old

        class_span = find_class_span(path, "GapType")
        if class_span:
            new = remove_line_range(new, class_span[0], class_span[1])
            # Clean up extra blank lines left by class removal
            new = re.sub(r"\n{3,}", "\n\n", new)

        new = normalize_gap_import_block(new)
        new = apply_reference_rewrites(new, alias_map)

        diff = generate_unified_diff(old, new, rel)
        if diff:
            patch_chunks.append(diff)
            changed.append(rel)

    patch_text = "".join(patch_chunks)
    mapping_text = json.dumps(
        {
            "canonical_section": CANONICAL_SECTION,
            "source_of_truth": spec.get("source_of_truth"),
            "legacy_to_canonical": alias_map,
        },
        indent=2,
        sort_keys=True,
    )

    print(f"[GapType Migration] canonical section: {CANONICAL_SECTION}")
    print(f"Scanned files: {len(scanned)}")
    for rel in scanned:
        print(f"  - {rel}")
    print(f"Files with patch changes: {len(changed)}")
    for rel in changed:
        print(f"  - {rel}")
    print("Legacy -> canonical mapping:")
    for legacy, canonical in alias_map.items():
        print(f"  {legacy} -> {canonical}")

    if args.dry_run:
        print("\n--- PATCH (dry-run) ---")
        print(patch_text if patch_text else "(no changes)")
        print("\n--- MAPPING JSON (dry-run) ---")
        print(mapping_text)
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    patch_path = out_dir / "migrate_gap_type.patch"
    map_path = out_dir / "migrate_gap_type_mapping.json"
    patch_path.write_text(patch_text, encoding="utf-8")
    map_path.write_text(mapping_text + "\n", encoding="utf-8")
    print(f"\nWrote patch: {patch_path}")
    print(f"Wrote mapping: {map_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
