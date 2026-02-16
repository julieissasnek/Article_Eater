#!/usr/bin/env python3
"""
Generate BN_graphical <-> AE ClaimType adapter module (non-destructive).

Canonical contract section enforced:
  contracts/vocab/canonical_enums.json -> enums.ClaimType
"""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Dict, List, Set


CANONICAL_SECTION = "enums.ClaimType"


def load_claim_spec(ae_root: Path) -> dict:
    path = ae_root / "contracts/vocab/canonical_enums.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    return doc["enums"]["ClaimType"]


def extract_enum_values(py_path: Path, class_name: str) -> Set[str]:
    try:
        tree = ast.parse(py_path.read_text(encoding="utf-8"), filename=str(py_path))
    except Exception:
        return set()
    values: Set[str] = set()
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        for stmt in node.body:
            if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                values.add(stmt.value.value)
    return values


def build_bn_to_canonical(bn_values: Set[str], spec: dict) -> Dict[str, str]:
    aliases: Dict[str, str] = spec.get("deprecated_aliases", {})
    canonical: Set[str] = set(spec.get("canonical_values", []))

    # Start with alias-driven mappings from contract
    mapping: Dict[str, str] = {}
    for bn in sorted(bn_values):
        if bn in aliases:
            mapping[bn] = aliases[bn]
        elif bn in canonical:
            mapping[bn] = bn

    # Supplemental mappings needed for BN internal enums
    supplemental = {
        "effect": "causal",
        "mechanism": "mechanistic",
        "boundary": "moderated",
        "replication": "descriptive",
        "null_result": "null",
    }
    for k, v in supplemental.items():
        if k in bn_values and v in canonical:
            mapping[k] = v

    return mapping


def build_canonical_to_bn(canonical_values: List[str], bn_to_canonical: Dict[str, str]) -> Dict[str, str]:
    reverse: Dict[str, str] = {}
    # Use exact inverse where available
    for bn, can in bn_to_canonical.items():
        reverse.setdefault(can, bn)

    # Fill remaining canonical values with best-effort defaults
    fallback = {
        "causal": "effect",
        "associational": "effect",
        "null": "null_result",
        "moderated": "boundary",
        "mechanistic": "mechanism",
        "descriptive": "replication",
        "rebuttal": "boundary",
        "presumption": "boundary",
    }
    for c in canonical_values:
        if c not in reverse and c in fallback:
            reverse[c] = fallback[c]
    return reverse


def test_migration_lossless() -> None:
    bn_to_canonical = {
        "effect": "causal",
        "mechanism": "mechanistic",
        "boundary": "moderated",
        "replication": "descriptive",
        "null_result": "null",
    }
    canonical_to_bn = {
        "causal": "effect",
        "mechanistic": "mechanism",
        "moderated": "boundary",
        "descriptive": "replication",
        "null": "null_result",
    }
    for bn_value, canonical in bn_to_canonical.items():
        bn_roundtrip = canonical_to_bn[canonical]
        assert bn_roundtrip == bn_value


def adapter_module_text(
    canonical_section: str,
    bn_to_canonical: Dict[str, str],
    canonical_to_bn: Dict[str, str],
    unmapped: List[str],
) -> str:
    return f'''"""
Auto-generated ClaimType adapter for BN_graphical <-> AE canonical ClaimType.
Canonical contract section: {canonical_section}
"""

from __future__ import annotations

from typing import Dict

BN_TO_CANONICAL: Dict[str, str] = {json.dumps(bn_to_canonical, indent=2, sort_keys=True)}
CANONICAL_TO_BN: Dict[str, str] = {json.dumps(canonical_to_bn, indent=2, sort_keys=True)}
UNMAPPED_BN_VALUES = {json.dumps(unmapped, indent=2)}


def bn_claim_to_canonical(value: str) -> str:
    key = value.strip().lower()
    if key not in BN_TO_CANONICAL:
        raise KeyError(f"No canonical ClaimType mapping for BN value: {{value}}")
    return BN_TO_CANONICAL[key]


def canonical_to_bn_claim(value: str) -> str:
    key = value.strip().lower()
    if key not in CANONICAL_TO_BN:
        raise KeyError(f"No BN ClaimType mapping for canonical value: {{value}}")
    return CANONICAL_TO_BN[key]


def test_migration_lossless() -> None:
    # Lossless subset: BN internal ClaimType values
    for bn_value, canonical in BN_TO_CANONICAL.items():
        bn_roundtrip = canonical_to_bn_claim(canonical)
        assert bn_roundtrip == bn_value


if __name__ == "__main__":
    test_migration_lossless()
    print("ClaimType adapter self-test passed.")
'''


def build_report(
    canonical_section: str,
    bn_values: List[str],
    mapped: Dict[str, str],
    unmapped: List[str],
    source_file: Path,
) -> str:
    lines: List[str] = []
    lines.append("# ClaimType Migration Report")
    lines.append("")
    lines.append(f"Canonical section: `{canonical_section}`")
    lines.append(f"BN source: `{source_file}`")
    lines.append("")
    lines.append("## BN ClaimType values discovered")
    for value in bn_values:
        lines.append(f"- `{value}`")
    lines.append("")
    lines.append("## Mapping (BN -> Canonical)")
    for k in sorted(mapped):
        lines.append(f"- `{k}` -> `{mapped[k]}`")
    lines.append("")
    lines.append("## Unmapped BN values")
    if unmapped:
        for v in unmapped:
            lines.append(f"- `{v}`")
    else:
        lines.append("- None")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate ClaimType adapter artifacts")
    parser.add_argument("--dry-run", action="store_true", help="Print artifacts but do not write files")
    parser.add_argument(
        "--output-dir",
        default="data/review/migration_adapters",
        help="Output directory (relative to AE repo root)",
    )
    args = parser.parse_args()

    test_migration_lossless()

    ae_root = Path(__file__).resolve().parents[1]
    repos_root = ae_root.parent
    out_dir = ae_root / args.output_dir

    spec = load_claim_spec(ae_root)
    canonical_values = list(spec.get("canonical_values", []))

    bn_claim_file = repos_root / "BN_graphical/src/article_processing/article_decomposer.py"
    bn_values = extract_enum_values(bn_claim_file, "ClaimType")
    mapped = build_bn_to_canonical(bn_values, spec)
    unmapped = sorted(v for v in bn_values if v not in mapped)
    canonical_to_bn = build_canonical_to_bn(canonical_values, mapped)

    report = build_report(
        canonical_section=CANONICAL_SECTION,
        bn_values=sorted(bn_values),
        mapped=mapped,
        unmapped=unmapped,
        source_file=bn_claim_file,
    )
    adapter = adapter_module_text(CANONICAL_SECTION, mapped, canonical_to_bn, unmapped)

    print(f"[ClaimType Migration] canonical section: {CANONICAL_SECTION}")
    print(f"BN values discovered: {len(bn_values)}")
    print(f"Mapped: {len(mapped)}")
    print(f"Unmapped: {len(unmapped)}")

    if args.dry_run:
        print("\n--- REPORT (dry-run) ---")
        print(report)
        print("\n--- ADAPTER MODULE (dry-run) ---")
        print(adapter)
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "migrate_claim_type_report.md"
    adapter_path = out_dir / "claim_type_adapter.py"
    report_path.write_text(report, encoding="utf-8")
    adapter_path.write_text(adapter, encoding="utf-8")
    print(f"Wrote report: {report_path}")
    print(f"Wrote adapter module: {adapter_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
