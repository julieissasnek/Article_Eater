#!/usr/bin/env python3
"""
Cross-repo enum drift checker.

Loads contracts/vocab/canonical_enums.json and checks enum-like definitions
across:
- Article_Eater_PostQuinean_v1
- Article_Finder_v3_2_3
- BN_graphical
- Outcome_Contractor
- Tagging_Contractor

Exits nonzero if any drift is detected.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple


@dataclass
class Observation:
    category: str
    repo: str
    path: Path
    source: str
    values: Set[str]
    strict: bool = False


TARGET_CLASS_TO_CATEGORY: Dict[str, str] = {
    "GapType": "GapType",
    "ClaimType": "ClaimType",
    "EvidenceType": "EvidenceType",
    "MechanismEvidenceType": "EvidenceType",
    "PathwayType": "PathwayType",
    "EffectPathway": "PathwayType",
    "TemplateFamily": "ArticleTypeCrosswalk",
    "ArticleType": "ArticleTypeCrosswalk",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_enum_values_from_class(class_node: ast.ClassDef) -> Set[str]:
    values: Set[str] = set()
    for stmt in class_node.body:
        if isinstance(stmt, ast.Assign):
            if not stmt.targets:
                continue
            val = stmt.value
            if isinstance(val, ast.Constant) and isinstance(val.value, str):
                values.add(val.value)
        elif isinstance(stmt, ast.AnnAssign):
            val = stmt.value
            if isinstance(val, ast.Constant) and isinstance(val.value, str):
                values.add(val.value)
    return values


def collect_python_enum_observations(repo_name: str, repo_root: Path) -> List[Observation]:
    observations: List[Observation] = []
    for py_file in repo_root.rglob("*.py"):
        if any(
            part in {".git", ".venv", "venv", "site-packages", "__pycache__", "ruthless_bundle_2026-02-08"}
            for part in py_file.parts
        ):
            continue
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Skipped: {e}")
            continue
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            category = TARGET_CLASS_TO_CATEGORY.get(node.name)
            if not category:
                continue
            values = extract_enum_values_from_class(node)
            if not values:
                continue
            observations.append(
                Observation(
                    category=category,
                    repo=repo_name,
                    path=py_file,
                    source=f"class {node.name}",
                    values=values,
                )
            )
    return observations


def extract_dict_keys(path: Path, dict_name: str) -> Set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except Exception:
        return set()

    keys: Set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == dict_name and isinstance(node.value, ast.Dict):
                for k in node.value.keys:
                    if isinstance(k, ast.Constant) and isinstance(k.value, str):
                        keys.add(k.value)
    return keys


def extract_schema_enum(path: Path, pointer: str) -> Set[str]:
    doc = load_json(path)
    if not pointer.startswith("#/"):
        return set()
    node = doc
    for part in pointer[2:].split("/"):
        if isinstance(node, dict):
            node = node.get(part)
        elif isinstance(node, list):
            try:
                node = node[int(part)]
            except Exception:
                return set()
        else:
            return set()
        if node is None:
            return set()
    if isinstance(node, list):
        return {str(v) for v in node}
    return set()


def extract_sql_enum_values(path: Path, type_name: str) -> Set[str]:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"CREATE\s+TYPE\s+{re.escape(type_name)}\s+AS\s+ENUM\s*\((.*?)\)",
        re.IGNORECASE | re.DOTALL,
    )
    m = pattern.search(text)
    if not m:
        return set()
    body = m.group(1)
    return {v.strip("'\" ") for v in re.findall(r"'([^']+)'", body)}


def detect_ci_shape_ae_claim(path: Path) -> Set[str]:
    doc = load_json(path)
    ci = (
        doc.get("properties", {})
        .get("statistics", {})
        .get("properties", {})
        .get("ci95", {})
    )
    if ci.get("type") == ["array", "null"] or ci.get("type") == "array":
        return {"ci95_array"}
    return set()


def detect_ci_shape_bn_api(path: Path) -> Set[str]:
    doc = load_json(path)
    out: Set[str] = set()
    defs = doc.get("definitions", {})
    for obj_name in ("CausalEffect", "OutcomePrediction"):
        prop = defs.get(obj_name, {}).get("properties", {}).get("confidence_interval", {})
        if prop.get("type") == "array":
            out.add("confidence_interval_array")
        elif prop.get("type") == "object":
            props = set(prop.get("properties", {}).keys())
            if {"ci_lower", "ci_upper"}.issubset(props):
                out.add("ci_lower_ci_upper_object")
    return out


def detect_ci_shape_table_extractor(path: Path) -> Set[str]:
    text = path.read_text(encoding="utf-8")
    if '"ci_lower"' in text and '"ci_upper"' in text:
        return {"ci_lower_ci_upper_object"}
    return set()


def normalize(values: Iterable[str]) -> Set[str]:
    return {v.strip() for v in values if v and v.strip()}


def check_category(
    category: str,
    spec: dict,
    observations: List[Observation],
    source_of_truth_rel: Optional[str] = None,
) -> Tuple[int, List[str]]:
    mismatches = 0
    lines: List[str] = []

    canonical = normalize(spec.get("canonical_values", []))
    aliases = spec.get("deprecated_aliases", {}) or {}
    alias_keys = normalize(aliases.keys())
    allowed = canonical | alias_keys

    if not observations:
        lines.append(f"[WARN] {category}: no observed definitions found")
        return mismatches, lines

    for obs in observations:
        actual = normalize(obs.values)
        unknown = sorted(actual - allowed)
        aliases_used = sorted(actual & alias_keys)

        strict = obs.strict
        if source_of_truth_rel:
            try:
                strict = strict or str(obs.path).endswith(source_of_truth_rel)
            except Exception as e:
                import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")

        header = f"[{obs.repo}] {obs.path}:{obs.source}"
        local_issues: List[str] = []

        if unknown:
            local_issues.append(f"unknown values: {unknown}")

        if aliases_used:
            mapped = {k: aliases[k] for k in aliases_used if k in aliases}
            local_issues.append(f"deprecated aliases in use: {mapped}")

        if strict:
            missing = sorted(canonical - actual)
            extra_non_alias = sorted(actual - canonical - alias_keys)
            if missing:
                local_issues.append(f"missing canonical values: {missing}")
            if extra_non_alias:
                local_issues.append(f"extra non-canonical values: {extra_non_alias}")

        if local_issues:
            mismatches += 1
            lines.append(f"[DRIFT] {category} -> {header}")
            for issue in local_issues:
                lines.append(f"  - {issue}")
        else:
            lines.append(f"[OK] {category} -> {header}")

    return mismatches, lines


def main() -> int:
    warnings.filterwarnings("ignore", category=SyntaxWarning)

    parser = argparse.ArgumentParser(description="Check cross-repo enum drift against canonical contract")
    parser.add_argument(
        "--canonical",
        default="contracts/vocab/canonical_enums.json",
        help="Path to canonical enums JSON (relative to AE repo root)"
    )
    args = parser.parse_args()

    ae_root = Path(__file__).resolve().parents[1]
    repos_root = ae_root.parent

    repos = {
        "Article_Eater_PostQuinean_v1": ae_root,
        "Article_Finder_v3_2_3": repos_root / "Article_Finder_v3_2_3",
        "BN_graphical": repos_root / "BN_graphical",
        "Outcome_Contractor": repos_root / "Outcome_Contractor",
        "Tagging_Contractor": repos_root / "Tagging_Contractor",
    }

    canonical_path = (ae_root / args.canonical).resolve()
    canonical_doc = load_json(canonical_path)
    enums = canonical_doc.get("enums", {})

    all_observations: List[Observation] = []

    for repo_name, repo_root in repos.items():
        if repo_root.exists():
            all_observations.extend(collect_python_enum_observations(repo_name, repo_root))

    # Extra explicit observations not represented as python Enum classes
    # ClaimType from AE schema
    ae_claim_schema = ae_root / "contracts/ae_af/schemas/ae.claim.v2.schema.json"
    claim_enum = extract_schema_enum(ae_claim_schema, "#/properties/claim_type/enum")
    if claim_enum:
        all_observations.append(
            Observation("ClaimType", "Article_Eater_PostQuinean_v1", ae_claim_schema, "schema claim_type enum", claim_enum, strict=True)
        )

    # ClaimType from Outcome extractor dict + default fallback
    oc_claim_path = repos["Outcome_Contractor"] / "article_finder/ae_claim_extractor.py"
    if oc_claim_path.exists():
        oc_claim_types = extract_dict_keys(oc_claim_path, "CLAIM_TYPE_PATTERNS")
        if oc_claim_types:
            oc_claim_types.add("associational")  # default return in _determine_claim_type
            all_observations.append(
                Observation("ClaimType", "Outcome_Contractor", oc_claim_path, "CLAIM_TYPE_PATTERNS + default", oc_claim_types)
            )

    # EvidenceType from BN SQL enum
    bn_sql = repos["BN_graphical"] / "migrations/005_sprint1_schemas.sql"
    if bn_sql.exists():
        sql_vals = extract_sql_enum_values(bn_sql, "mechanism_evidence_type")
        if sql_vals:
            all_observations.append(
                Observation("EvidenceType", "BN_graphical", bn_sql, "SQL mechanism_evidence_type", sql_vals)
            )

    # Confidence interval shape observations
    bn_api = repos["BN_graphical"] / "contracts/bn.api.v2.schema.json"
    if bn_api.exists():
        ci_vals = detect_ci_shape_bn_api(bn_api)
        if ci_vals:
            all_observations.append(
                Observation("ConfidenceIntervalShape", "BN_graphical", bn_api, "schema confidence_interval shape", ci_vals)
            )

    if ae_claim_schema.exists():
        ci_vals = detect_ci_shape_ae_claim(ae_claim_schema)
        if ci_vals:
            all_observations.append(
                Observation("ConfidenceIntervalShape", "Article_Eater_PostQuinean_v1", ae_claim_schema, "schema statistics.ci95 shape", ci_vals)
            )

    ae_table_extractor = ae_root / "src/services/table_extractor.py"
    if ae_table_extractor.exists():
        ci_vals = detect_ci_shape_table_extractor(ae_table_extractor)
        if ci_vals:
            all_observations.append(
                Observation("ConfidenceIntervalShape", "Article_Eater_PostQuinean_v1", ae_table_extractor, "table extractor ci fields", ci_vals)
            )

    # Partition observations by category
    by_category: Dict[str, List[Observation]] = {}
    for obs in all_observations:
        by_category.setdefault(obs.category, []).append(obs)

    # Ensure strict checks on canonical source files
    source_map = {
        "GapType": "src/epistemic/gap_types.py",
        "ClaimType": "contracts/ae_af/schemas/ae.claim.v2.schema.json",
        "PathwayType": "src/services/web_of_belief.py",
        "ArticleTypeCrosswalk": "src/epistemic/extraction/paper_classifier.py",
    }

    total_mismatches = 0
    output_lines: List[str] = []

    for category, spec in enums.items():
        observations = by_category.get(category, [])
        mm, lines = check_category(
            category=category,
            spec=spec,
            observations=observations,
            source_of_truth_rel=source_map.get(category),
        )
        total_mismatches += mm
        output_lines.extend(lines)

    # Crosswalk structural checks
    cross_spec = enums.get("ArticleTypeCrosswalk", {})
    crosswalk = cross_spec.get("crosswalk", {})
    outcome_to_ae = crosswalk.get("outcome_to_ae", {})
    ae_to_outcome = crosswalk.get("ae_to_outcome", {})
    canonical_article = normalize(cross_spec.get("canonical_values", []))

    # Discover Outcome ArticleType values from parsed observations
    outcome_types: Set[str] = set()
    for obs in by_category.get("ArticleTypeCrosswalk", []):
        if obs.repo == "Outcome_Contractor" and obs.source == "class ArticleType":
            outcome_types |= obs.values

    # Discover AE TemplateFamily values
    ae_types: Set[str] = set()
    for obs in by_category.get("ArticleTypeCrosswalk", []):
        if obs.repo == "Article_Eater_PostQuinean_v1" and obs.source == "class TemplateFamily":
            ae_types |= obs.values

    if outcome_types:
        missing_outcome_map = sorted(outcome_types - set(outcome_to_ae.keys()))
        if missing_outcome_map:
            total_mismatches += 1
            output_lines.append("[DRIFT] ArticleTypeCrosswalk -> missing outcome_to_ae mappings")
            output_lines.append(f"  - missing outcome types: {missing_outcome_map}")

    if ae_types:
        missing_ae_map = sorted(ae_types - set(ae_to_outcome.keys()))
        if missing_ae_map:
            total_mismatches += 1
            output_lines.append("[DRIFT] ArticleTypeCrosswalk -> missing ae_to_outcome mappings")
            output_lines.append(f"  - missing AE template families: {missing_ae_map}")

    invalid_targets = {
        k: v for k, v in outcome_to_ae.items() if v not in canonical_article
    }
    if invalid_targets:
        total_mismatches += 1
        output_lines.append("[DRIFT] ArticleTypeCrosswalk -> outcome_to_ae maps to non-canonical values")
        output_lines.append(f"  - invalid mappings: {invalid_targets}")

    print("\n".join(output_lines))
    print(f"\nSummary: {total_mismatches} drift issue(s) detected.")

    return 1 if total_mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
