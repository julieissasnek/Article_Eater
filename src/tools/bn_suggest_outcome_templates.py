#!/usr/bin/env python3
"""
bn_suggest_outcome_templates.py

Given a RuleGraph BN export JSON produced by
/api/admin/rulegraph_v2/export_bn, this script proposes a set of
**outcome variable templates** and their parent sets, suitable as
starting points for BN-Maker CPD design.

It does **not** assign probabilities. Instead, it reads:

- subject nodes and moderator nodes connected to each rule node;
- rule text and summaries;

and emits a CSV where each row describes a candidate outcome node
and its recommended parents.

Usage
-----

    python -m src.tools.bn_suggest_outcome_templates \
        --input article_eater_bn_export_2025-11-25T10-30-00.json \
        --out bn_outcome_templates.csv

Output CSV columns
-------------------

- outcome_node_id
- outcome_family
- outcome_label
- paper_id
- rule_id
- rule_node_id
- rule_text
- subject_parents_ids
- subject_parent_types
- moderator_parent_ids
- recommended_parent_nodes
- notes

The idea is that BN-Maker (or a human modeller) can take this CSV
and decide which outcome families to keep, rename, or split, and
then attach CPDs.
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


def load_export(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _rule_node_id(rule: Dict[str, Any]) -> str:
    paper_id = rule.get("paper_id") or "<unknown>"
    rid = rule.get("rule_id") or ""
    if rid:
        return f"rule:{paper_id}:{rid}"
    return f"rule:{paper_id}"


def _build_index(export: Dict[str, Any]) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
    nodes = export.get("nodes") or []
    edges = export.get("edges") or []

    nodes_by_id: Dict[str, Dict[str, Any]] = {}
    for n in nodes:
        nid = n.get("id")
        if nid:
            nodes_by_id[nid] = n

    edges_by_to: Dict[str, List[Dict[str, Any]]] = {}
    for e in edges:
        to_id = e.get("to")
        if not to_id:
            continue
        edges_by_to.setdefault(to_id, []).append(e)

    return nodes_by_id, edges_by_to


def _heuristic_outcome_family(text: str) -> str:
    """Very simple keyword heuristic to categorize outcome family.

    This is intentionally conservative and should be treated as a
    suggestion, not a ground truth label.
    """
    t = (text or "").lower()

    # preference / choice
    pref_keywords = [
        "preference", "prefer", "preferred", "liking", "like more",
        "choice", "chose", "chosen", "aesthetic", "beauty", "beautiful",
    ]
    if any(k in t for k in pref_keywords):
        return "preference"

    # stress / arousal / anxiety
    stress_keywords = [
        "stress", "stressed", "cortisol", "anxiety", "tense",
        "tension", "arousal", "overarousal",
    ]
    if any(k in t for k in stress_keywords):
        return "stress_arousal"

    # restoration / recovery / fatigue
    rest_keywords = [
        "restorative", "restoration", "recovery", "fatigue",
        "mental fatigue", "depletion",
    ]
    if any(k in t for k in rest_keywords):
        return "restoration"

    # performance / accuracy / rt
    perf_keywords = [
        "performance", "accuracy", "error", "errors",
        "response time", "rt ", "rt.", "speed", "task performance",
    ]
    if any(k in t for k in perf_keywords):
        return "performance"

    # memory / recall / recognition
    mem_keywords = [
        "memory", "recall", "recognition", "remembered",
    ]
    if any(k in t for k in mem_keywords):
        return "memory"

    # attention
    att_keywords = [
        "attention", "attentional", "focus", "focused",
    ]
    if any(k in t for k in att_keywords):
        return "attention"

    # affect / valence more generally
    affect_keywords = [
        "valence", "pleasant", "unpleasant", "enjoyable",
        "mood", "affect",
    ]
    if any(k in t for k in affect_keywords):
        return "affect_valence"

    return "unspecified"


def _collect_parents_for_rule(
    rule_node_id: str,
    nodes_by_id: Dict[str, Dict[str, Any]],
    edges_by_to: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, Any]:
    edges = edges_by_to.get(rule_node_id, []) or []

    subject_parent_ids: List[str] = []
    subject_parent_types: List[str] = []
    moderator_parent_ids: List[str] = []

    for e in edges:
        src = e.get("from")
        etype = e.get("type")
        if not src:
            continue
        n = nodes_by_id.get(src) or {}
        ntype = n.get("type") or ""

        if etype == "subject_scope":
            subject_parent_ids.append(src)
            if ntype and ntype not in subject_parent_types:
                subject_parent_types.append(ntype)
        elif etype == "subject_moderator":
            moderator_parent_ids.append(src)
            if ntype and ntype not in subject_parent_types:
                subject_parent_types.append(ntype)

    subject_parent_ids = sorted(set(subject_parent_ids))
    moderator_parent_ids = sorted(set(moderator_parent_ids))
    subject_parent_types = sorted(subject_parent_types)

    recommended_parent_nodes = subject_parent_ids + moderator_parent_ids + [rule_node_id]

    return {
        "subject_parent_ids": subject_parent_ids,
        "subject_parent_types": subject_parent_types,
        "moderator_parent_ids": moderator_parent_ids,
        "recommended_parent_nodes": recommended_parent_nodes,
    }


def write_outcome_templates_csv(export: Dict[str, Any], out_path: Path) -> None:
    import csv

    nodes_by_id, edges_by_to = _build_index(export)
    rules = export.get("rules") or []

    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "outcome_node_id",
            "outcome_family",
            "outcome_label",
            "paper_id",
            "rule_id",
            "rule_node_id",
            "rule_text",
            "subject_parents_ids",
            "subject_parent_types",
            "moderator_parent_ids",
            "recommended_parent_nodes",
            "notes",
        ])

        for r in rules:
            paper_id = r.get("paper_id") or "<unknown>"
            rid = r.get("rule_id") or ""
            rule_node_id = _rule_node_id(r)
            rt = (r.get("rule_text") or "") + " " + (r.get("subject_scope_summary") or "") + " " + (r.get("moderators_summary") or "")

            family = _heuristic_outcome_family(rt)
            outcome_label = family if family != "unspecified" else "outcome_from_rule"

            outcome_node_id = f"outcome:{paper_id}:{rid or 'rule'}:{family}"

            parent_info = _collect_parents_for_rule(rule_node_id, nodes_by_id, edges_by_to)

            writer.writerow([
                outcome_node_id,
                family,
                outcome_label,
                paper_id,
                rid,
                rule_node_id,
                (r.get("rule_text") or "").replace("\n", " ").strip(),
                ";".join(parent_info["subject_parent_ids"]),
                ";".join(parent_info["subject_parent_types"]),
                ";".join(parent_info["moderator_parent_ids"]),
                ";".join(parent_info["recommended_parent_nodes"]),
                "",
            ])


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Suggest BN outcome variable templates from a RuleGraph BN export JSON."
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
        "--out",
        "-o",
        type=str,
        required=True,
        help="Path to output CSV file for outcome templates.",
    )

    args = parser.parse_args(argv)
    in_path = Path(args.input)
    out_path = Path(args.out)

    if not in_path.is_file():
        raise SystemExit(f"Input JSON not found: {in_path}")

    export = load_export(in_path)
    write_outcome_templates_csv(export, out_path)


if __name__ == "__main__":
    main()
