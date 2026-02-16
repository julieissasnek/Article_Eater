#!/usr/bin/env python3
"""
Generate EvidenceType migration adapter + mapping table (non-destructive)
across BN_graphical, Tagging_Contractor, and Article_Finder.

Canonical contract section enforced:
  contracts/vocab/canonical_enums.json -> enums.EvidenceType
"""

from __future__ import annotations

import argparse
import ast
import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple


CANONICAL_SECTION = "enums.EvidenceType"


def load_spec(ae_root: Path) -> dict:
    path = ae_root / "contracts/vocab/canonical_enums.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    return doc["enums"]["EvidenceType"]


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


def extract_sql_enum(sql_path: Path, type_name: str) -> Set[str]:
    text = sql_path.read_text(encoding="utf-8", errors="ignore")
    pattern = re.compile(
        rf"CREATE\s+TYPE\s+{re.escape(type_name)}\s+AS\s+ENUM\s*\((.*?)\)",
        flags=re.IGNORECASE | re.DOTALL,
    )
    m = pattern.search(text)
    if not m:
        return set()
    return {x.strip() for x in re.findall(r"'([^']+)'", m.group(1))}


def extract_csv_column(csv_path: Path, field_name: str) -> Set[str]:
    values: Set[str] = set()
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if field_name not in (reader.fieldnames or []):
            return values
        for row in reader:
            v = (row.get(field_name) or "").strip().lower()
            if v:
                values.add(v)
    return values


def collect_values(repos_root: Path) -> Dict[str, Set[str]]:
    values: Dict[str, Set[str]] = {}

    # BN sources
    bn_root = repos_root / "BN_graphical"
    values["bn_enhanced_edge"] = extract_enum_values(
        bn_root / "src/schemas/enhanced_edge.py", "EvidenceType"
    )
    values["bn_mechanism_spec"] = extract_enum_values(
        bn_root / "src/schemas/mechanism_specification.py", "MechanismEvidenceType"
    )
    values["bn_literature_linker"] = extract_enum_values(
        bn_root / "src/literature_integration/literature_linker.py", "EvidenceType"
    )
    values["bn_sql_evidence_type"] = extract_sql_enum(
        bn_root / "migrations/006_sprint2_enhanced_edges.sql", "evidence_type"
    )
    values["bn_sql_mechanism_evidence_type"] = extract_sql_enum(
        bn_root / "migrations/005_sprint1_schemas.sql", "mechanism_evidence_type"
    )

    # Tagging source (report as de facto taxonomy usage)
    tagging_root = repos_root / "Tagging_Contractor"
    values["tagging_csv"] = extract_csv_column(
        tagging_root / "reports/tag_extractability_evidence.csv", "evidence_type"
    )

    # Article Finder currently has no explicit EvidenceType enum (scan remains explicit)
    af_root = repos_root / "Article_Finder_v3_2_3"
    af_values: Set[str] = set()
    if af_root.exists():
        for py_path in af_root.rglob("*.py"):
            if any(p in {".venv", "venv", "__pycache__", ".git"} for p in py_path.parts):
                continue
            text = py_path.read_text(encoding="utf-8", errors="ignore")
            for token in re.findall(r"evidence_type['\"]?\s*[:=]\s*['\"]([a-zA-Z0-9_]+)['\"]", text):
                af_values.add(token.lower())
    values["article_finder_detected"] = af_values

    return values


def build_mapping(values: Dict[str, Set[str]], spec: dict) -> Tuple[Dict[str, str], Dict[str, List[str]]]:
    canonical_values = set(spec.get("canonical_values", []))
    aliases = dict(spec.get("deprecated_aliases", {}))

    # Supplemental mappings for known drift beyond canonical aliases.
    supplemental = {
        "meta": "meta_analysis",
        "review": "theoretical",
        "direct": "observational",
        "indirect": "observational",
    }

    resolved = {**aliases, **supplemental}
    mapping: Dict[str, str] = {}
    unmapped_by_source: Dict[str, List[str]] = {}

    for source, vals in values.items():
        missing: List[str] = []
        for v in sorted(vals):
            if v in canonical_values:
                mapping[v] = v
            elif v in resolved and resolved[v] in canonical_values:
                mapping[v] = resolved[v]
            else:
                missing.append(v)
        unmapped_by_source[source] = missing

    return mapping, unmapped_by_source


def build_reverse_for_source(source: str, canonical_values: List[str]) -> Dict[str, str]:
    """
    Preferred canonical->source projection by source context.
    """
    if source in {"bn_enhanced_edge", "bn_sql_evidence_type"}:
        # BN enhanced uses empirical/meta/theoretical/replication_*.
        return {
            "observational": "empirical",
            "experimental": "empirical",
            "correlational": "empirical",
            "meta_analysis": "meta_analysis",
            "theoretical": "theoretical",
            "replication_success": "replication_success",
            "replication_failure": "replication_failure",
            "neuroscientific": "theoretical",
            "neuroimaging": "theoretical",
            "computational_model": "theoretical",
        }
    if source in {"bn_mechanism_spec", "bn_sql_mechanism_evidence_type"}:
        return {
            "theoretical": "theoretical",
            "observational": "correlational",
            "correlational": "correlational",
            "experimental": "experimental",
            "neuroscientific": "neuroscientific",
            "neuroimaging": "neuroscientific",
            "computational_model": "computational_model",
            "meta_analysis": "theoretical",
            "replication_success": "experimental",
            "replication_failure": "experimental",
        }
    if source == "bn_literature_linker":
        return {
            "observational": "direct",
            "experimental": "direct",
            "correlational": "indirect",
            "meta_analysis": "meta",
            "theoretical": "theoretical",
            "replication_success": "direct",
            "replication_failure": "direct",
            "neuroscientific": "indirect",
            "neuroimaging": "indirect",
            "computational_model": "theoretical",
        }
    # Tagging and Article Finder currently do not have canonical-compatible evidence enums.
    return {k: "" for k in canonical_values}


def test_migration_lossless() -> None:
    # Lossless subset checks for BN mechanism surface.
    bn_mech_map = {
        "theoretical": "theoretical",
        "correlational": "correlational",
        "experimental": "experimental",
        "neuroscientific": "neuroscientific",
        "computational_model": "computational_model",
    }
    reverse = {
        "theoretical": "theoretical",
        "correlational": "correlational",
        "experimental": "experimental",
        "neuroscientific": "neuroscientific",
        "computational_model": "computational_model",
    }
    for source_value, canonical in bn_mech_map.items():
        assert reverse[canonical] == source_value


def adapter_module_text(
    canonical_section: str,
    value_to_canonical: Dict[str, str],
    source_reverse_maps: Dict[str, Dict[str, str]],
    unmapped_by_source: Dict[str, List[str]],
) -> str:
    return f'''"""
Auto-generated EvidenceType adapter.
Canonical contract section: {canonical_section}
"""

from __future__ import annotations

from typing import Dict, Optional

VALUE_TO_CANONICAL: Dict[str, str] = {json.dumps(value_to_canonical, indent=2, sort_keys=True)}
SOURCE_CANONICAL_TO_LOCAL: Dict[str, Dict[str, str]] = {json.dumps(source_reverse_maps, indent=2, sort_keys=True)}
UNMAPPED_BY_SOURCE = {json.dumps(unmapped_by_source, indent=2, sort_keys=True)}


def source_evidence_to_canonical(source: str, value: str) -> Optional[str]:
    key = value.strip().lower()
    return VALUE_TO_CANONICAL.get(key)


def canonical_to_source_evidence(source: str, canonical_value: str) -> Optional[str]:
    source_key = source.strip().lower()
    canonical_key = canonical_value.strip().lower()
    table = SOURCE_CANONICAL_TO_LOCAL.get(source_key, {{}})
    result = table.get(canonical_key)
    if result == "":
        return None
    return result


def test_migration_lossless() -> None:
    # Lossless check on BN mechanism surface.
    sample = {{
      "theoretical": "theoretical",
      "correlational": "correlational",
      "experimental": "experimental",
      "neuroscientific": "neuroscientific",
      "computational_model": "computational_model"
    }}
    for source_value, canonical in sample.items():
        mapped = source_evidence_to_canonical("bn_mechanism_spec", source_value)
        assert mapped == canonical
        back = canonical_to_source_evidence("bn_mechanism_spec", mapped)
        assert back == source_value


if __name__ == "__main__":
    test_migration_lossless()
    print("EvidenceType adapter self-test passed.")
'''


def report_text(
    canonical_section: str,
    values: Dict[str, Set[str]],
    mapping: Dict[str, str],
    unmapped: Dict[str, List[str]],
) -> str:
    lines: List[str] = []
    lines.append("# EvidenceType Migration Report")
    lines.append("")
    lines.append(f"Canonical section: `{canonical_section}`")
    lines.append("")
    lines.append("## Discovered values by source")
    for source in sorted(values):
        lines.append(f"- `{source}`: {sorted(values[source])}")
    lines.append("")
    lines.append("## Value -> canonical mapping")
    for value in sorted(mapping):
        lines.append(f"- `{value}` -> `{mapping[value]}`")
    lines.append("")
    lines.append("## Unmapped values by source")
    for source in sorted(unmapped):
        vals = unmapped[source]
        if vals:
            lines.append(f"- `{source}`: {vals}")
    if not any(unmapped.values()):
        lines.append("- None")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate EvidenceType migration artifacts")
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

    spec = load_spec(ae_root)
    values = collect_values(repos_root)
    mapping, unmapped = build_mapping(values, spec)

    source_reverse_maps: Dict[str, Dict[str, str]] = {}
    canonical_values = list(spec.get("canonical_values", []))
    for source in values:
        source_reverse_maps[source] = build_reverse_for_source(source, canonical_values)

    report = report_text(CANONICAL_SECTION, values, mapping, unmapped)
    adapter = adapter_module_text(CANONICAL_SECTION, mapping, source_reverse_maps, unmapped)

    print(f"[EvidenceType Migration] canonical section: {CANONICAL_SECTION}")
    print(f"Discovered source groups: {len(values)}")
    print(f"Mapped values: {len(mapping)}")
    print(f"Unmapped values: {sum(len(v) for v in unmapped.values())}")

    if args.dry_run:
        print("\n--- REPORT (dry-run) ---")
        print(report)
        print("\n--- ADAPTER MODULE (dry-run) ---")
        print(adapter)
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "migrate_evidence_type_report.md"
    adapter_path = out_dir / "evidence_type_adapter.py"
    report_path.write_text(report, encoding="utf-8")
    adapter_path.write_text(adapter, encoding="utf-8")
    print(f"Wrote report: {report_path}")
    print(f"Wrote adapter module: {adapter_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
