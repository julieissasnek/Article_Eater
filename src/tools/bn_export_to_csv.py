#!/usr/bin/env python3
"""
bn_export_to_csv.py

Utility for converting an Article Eater RuleGraph BN export JSON
(from /api/admin/rulegraph_v2/export_bn) into a small family of
CSV files that are convenient to ingest into BN-Maker or similar
tools.

This script does **not** compute CPDs; it simply flattens the BN
skeleton (nodes, edges) and rule payloads into three tables:

1. nodes.csv
   - id, type, label, paper_id

2. edges.csv
   - from, to, type

3. rules.csv
   - rule_id, paper_id, age_bands, traits, rule_text,
     subject_scope_json, subject_moderators_json, evidence_json,
     provenance_json, status

BN-Maker can then use these tables as a starting point to define
variables and CPDs.

Usage
-----

Example:

    python -m src.tools.bn_export_to_csv \
        --input article_eater_bn_export_2025-11-25T10-30-00.json \
        --out-dir bn_csv/

This will create:

    bn_csv/nodes.csv
    bn_csv/edges.csv
    bn_csv/rules.csv
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def _ensure_out_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_export(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_nodes_csv(export: Dict[str, Any], out_dir: Path) -> None:
    import csv

    nodes = export.get("nodes") or []
    out_path = out_dir / "nodes.csv"
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "type", "label", "paper_id"])
        for n in nodes:
            writer.writerow([
                n.get("id", ""),
                n.get("type", ""),
                n.get("label", ""),
                n.get("paper_id", ""),
            ])


def write_edges_csv(export: Dict[str, Any], out_dir: Path) -> None:
    import csv

    edges = export.get("edges") or []
    out_path = out_dir / "edges.csv"
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["from", "to", "type"])
        for e in edges:
            writer.writerow([
                e.get("from", ""),
                e.get("to", ""),
                e.get("type", ""),
            ])


def _extract_scope_descriptors(scope: Dict[str, Any]) -> Dict[str, Any]:
    demographics = scope.get("demographics") or {}
    clinical = scope.get("clinical_status") or {}
    culture = scope.get("culture") or {}

    age_band = demographics.get("age_band")
    education_band = demographics.get("education_band")
    clinical_population = clinical.get("population")
    culture_region = culture.get("region")
    self_construal = culture.get("self_construal_profile")

    traits_raw = scope.get("traits_measured") or []
    traits: List[str] = []
    for t in traits_raw:
        name = (t or {}).get("name")
        if name:
            traits.append(name)

    ages = [age_band] if age_band else []
    return {
        "age_bands": ages,
        "traits": traits,
        "clinical_population": clinical_population,
        "culture_region": culture_region,
        "self_construal_profile": self_construal,
        "education_band": education_band,
    }



def _extract_moderator_descriptors(moderators: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    dimensions: List[str] = []
    attributes: List[str] = []
    for m in moderators or []:
        dim = (m or {}).get("dimension")
        attr = (m or {}).get("attribute")
        if dim and dim not in dimensions:
            dimensions.append(dim)
        if attr and attr not in attributes:
            attributes.append(attr)
    return {
        "dimensions": dimensions,
        "attributes": attributes,
    }


def write_rules_csv(export: Dict[str, Any], out_dir: Path) -> None:
    import csv

    rules = export.get("rules") or []
    out_path = out_dir / "rules.csv"
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "rule_id",
            "paper_id",
            "age_bands",
            "traits",
            "rule_text",
            "subject_scope_json",
            "subject_moderators_json",
            "evidence_json",
            "provenance_json",
            "status",
        ])
        for r in rules:
            scope = r.get("subject_scope") or {}
            moderators = r.get("subject_moderators") or []
            evidence = r.get("evidence") or {}
            provenance = r.get("provenance") or {}
            desc = _extract_scope_descriptors(scope)

            writer.writerow([
                r.get("rule_id", ""),
                r.get("paper_id", ""),
                ";".join(desc["age_bands"]),
                ";".join(desc["traits"]),
                (r.get("rule_text") or "").replace("\n", " ").strip(),
                json.dumps(scope, ensure_ascii=False),
                json.dumps(moderators, ensure_ascii=False),
                json.dumps(evidence, ensure_ascii=False),
                json.dumps(provenance, ensure_ascii=False),
                r.get("status", ""),
            ])


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Convert an Article Eater RuleGraph BN export JSON "
            "into CSV tables suitable for BN-Maker."
        )
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        required=True,
        help="Path to BN export JSON file produced by /api/admin/rulegraph_v2/export_bn",
    )
    parser.add_argument(
        "--out-dir",
        "-o",
        type=str,
        required=True,
        help="Output directory where CSV files will be written",
    )

    args = parser.parse_args(argv)

    in_path = Path(args.input)
    out_dir = Path(args.out_dir)

    if not in_path.is_file():
        raise SystemExit(f"Input JSON not found: {in_path}")

    _ensure_out_dir(out_dir)
    export = load_export(in_path)

    write_nodes_csv(export, out_dir)
    write_edges_csv(export, out_dir)
    write_rules_csv(export, out_dir)


if __name__ == "__main__":
    main()
