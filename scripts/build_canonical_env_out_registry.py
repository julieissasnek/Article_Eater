#!/usr/bin/env python3
"""
Build canonical env/out registry from lookup contracts + observed production IDs.

This provides a single machine-readable source for valid env.* and out.* node IDs.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _iter_jsonl(path: Path) -> Iterable[dict]:
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def _extract_rule_var(items: object, prefix: str) -> Optional[str]:
    if not isinstance(items, list):
        return None
    for item in items:
        if isinstance(item, dict):
            var = item.get("var")
            if isinstance(var, str) and var.startswith(prefix):
                return var
    return None


def _build_from_lookup(lookup: Dict[str, str], prefix: str) -> Tuple[Set[str], Set[str]]:
    canonical_ids: Set[str] = set()
    generic_ids: Set[str] = set()
    for canonical in lookup.values():
        if not isinstance(canonical, str):
            continue
        c = canonical.strip()
        if not c:
            continue
        if c.startswith(f"{prefix}.generic."):
            generic_ids.add(c)
            continue
        node_id = _canonical_to_node_id(c, prefix)
        if node_id:
            canonical_ids.add(node_id)
    return canonical_ids, generic_ids


def _safe_node_component(name: str) -> str:
    s = (name or "").strip().lower()
    s = re.sub(r"[^a-z0-9_.]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("._")
    return s


def _canonical_to_node_id(canonical_id: str, prefix: str) -> str:
    cid = (canonical_id or "").strip().lower()
    if not cid or cid.startswith("unresolved:"):
        return ""
    if cid.startswith(prefix + "."):
        cid = cid[len(prefix) + 1 :]
    normalized = _safe_node_component(cid)
    if not normalized:
        return ""
    return f"{prefix}.{normalized}"


def _normalize_observed_id(value: str, prefix: str) -> str:
    v = (value or "").strip()
    if not v:
        return v
    if v.startswith(prefix + "."):
        return v
    # Safety fallback for IDs accidentally stored without env./out. prefix.
    return f"{prefix}.{v}"


def _summarize_side(
    *,
    side: str,
    lookup_map: Dict[str, str],
    observed_ids: List[str],
) -> dict:
    canonical_ids, lookup_generic_ids = _build_from_lookup(lookup_map, side)
    observed_counter = Counter(_normalize_observed_id(v, side) for v in observed_ids if v)
    observed_unique = set(observed_counter.keys())

    unresolved_prefix = f"{side}.unresolved."
    generic_prefix = f"{side}.generic."

    observed_unresolved = sorted(v for v in observed_unique if v.startswith(unresolved_prefix))
    observed_generic = sorted(v for v in observed_unique if v.startswith(generic_prefix))
    observed_unknown = sorted(
        v
        for v in observed_unique
        if not v.startswith(unresolved_prefix)
        and not v.startswith(generic_prefix)
        and v not in canonical_ids
    )

    allowed_ids = sorted(canonical_ids | lookup_generic_ids | set(observed_generic))

    return {
        "prefix": f"{side}.",
        "unresolved_prefix": unresolved_prefix,
        "generic_prefix": generic_prefix,
        "canonical_ids": sorted(canonical_ids),
        "allowed_ids": allowed_ids,
        "observed_generic_ids": observed_generic,
        "observed_unresolved_ids": observed_unresolved,
        "observed_unknown_ids": observed_unknown,
        "stats": {
            "lookup_entries": len(lookup_map),
            "canonical_ids": len(canonical_ids),
            "allowed_ids": len(allowed_ids),
            "observed_unique_ids": len(observed_unique),
            "observed_rows": sum(observed_counter.values()),
            "observed_unresolved_rows": sum(
                count for key, count in observed_counter.items() if key.startswith(unresolved_prefix)
            ),
            "observed_generic_rows": sum(
                count for key, count in observed_counter.items() if key.startswith(generic_prefix)
            ),
            "observed_unknown_rows": sum(
                count
                for key, count in observed_counter.items()
                if key in observed_unknown
            ),
        },
        "top_unresolved_ids": [
            {"id": key, "count": count}
            for key, count in observed_counter.most_common()
            if key.startswith(unresolved_prefix)
        ][:25],
        "top_unknown_ids": [
            {"id": key, "count": count}
            for key, count in observed_counter.most_common()
            if key in observed_unknown
        ][:25],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build canonical env/out registry artifact.")
    parser.add_argument(
        "--environment-lookup",
        default="contracts/vocab/environment_lookup.json",
        help="Environment lookup contract JSON path",
    )
    parser.add_argument(
        "--outcome-lookup",
        default="contracts/outcome_vocab/outcome_lookup.json",
        help="Outcome lookup contract JSON path",
    )
    parser.add_argument(
        "--tables-jsonl",
        default="data/production/realtime_tables.jsonl",
        help="Production table records JSONL path",
    )
    parser.add_argument(
        "--rules-jsonl",
        default="data/production/realtime_rules.jsonl",
        help="Production rules JSONL path",
    )
    parser.add_argument(
        "--output",
        default="contracts/vocab/canonical_env_out_registry.json",
        help="Output registry JSON path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    env_lookup_path = Path(args.environment_lookup)
    out_lookup_path = Path(args.outcome_lookup)
    tables_path = Path(args.tables_jsonl)
    rules_path = Path(args.rules_jsonl)
    output_path = Path(args.output)

    env_lookup = _load_json(env_lookup_path).get("lookup", {})
    out_lookup = _load_json(out_lookup_path).get("lookup", {})

    observed_env: List[str] = []
    observed_out: List[str] = []
    rules_env: List[str] = []
    rules_out: List[str] = []

    # Prefer table node IDs when present.
    for row in _iter_jsonl(tables_path):
        env_id = row.get("environment_node_id")
        out_id = row.get("outcome_node_id")
        if isinstance(env_id, str) and env_id:
            observed_env.append(env_id)
        if isinstance(out_id, str) and out_id:
            observed_out.append(out_id)

    # Rule layer is captured separately for drift diagnostics.
    for row in _iter_jsonl(rules_path):
        env_id = _extract_rule_var(row.get("lhs"), "env.")
        out_id = _extract_rule_var(row.get("rhs"), "out.")
        if isinstance(env_id, str) and env_id:
            rules_env.append(env_id)
        if isinstance(out_id, str) and out_id:
            rules_out.append(out_id)

    payload = {
        "schema": "ae.canonical_env_out_registry.v1",
        "version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sources": {
            "environment_lookup": str(env_lookup_path),
            "outcome_lookup": str(out_lookup_path),
            "tables_jsonl": str(tables_path),
            "rules_jsonl": str(rules_path),
            "table_row_count": len(observed_env),
            "rule_row_count": len(rules_env),
        },
        "environment": _summarize_side(side="env", lookup_map=env_lookup, observed_ids=observed_env),
        "outcome": _summarize_side(side="out", lookup_map=out_lookup, observed_ids=observed_out),
        "table_rule_alignment": {
            "env_exact_row_alignment": len(observed_env) == len(rules_env) and observed_env == rules_env,
            "out_exact_row_alignment": len(observed_out) == len(rules_out) and observed_out == rules_out,
            "env_mismatch_rows": sum(1 for t, r in zip(observed_env, rules_env) if t != r),
            "out_mismatch_rows": sum(1 for t, r in zip(observed_out, rules_out) if t != r),
        },
        "validation": {
            "rule": "A valid ID must either be listed in allowed_ids, or match unresolved_prefix.",
            "notes": [
                "canonical_ids are normalized to include env./out. prefixes.",
                "generic IDs are allowed but tracked separately from canonical IDs.",
            ],
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print(f"wrote {output_path}")
    print(f"environment canonical IDs: {payload['environment']['stats']['canonical_ids']}")
    print(f"outcome canonical IDs: {payload['outcome']['stats']['canonical_ids']}")
    print(f"environment observed unresolved rows: {payload['environment']['stats']['observed_unresolved_rows']}")
    print(f"outcome observed unresolved rows: {payload['outcome']['stats']['observed_unresolved_rows']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
