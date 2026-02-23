#!/usr/bin/env python3
"""Audit and dry-run repair suggestions for unresolved BN nodes.

Safety model:
- default mode is dry-run
- replacement candidates are accepted only with deterministic contracts
- alias-rule replacements can be limited to existing BN targets with --require-existing-targets
- optional fallback can move remaining unresolved nodes to explicit unknown namespaces
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_BN_JSON = PROJECT_ROOT / "data" / "production" / "realtime_incremental_bn.json"
DEFAULT_ENV_LOOKUP = PROJECT_ROOT / "contracts" / "vocab" / "environment_lookup.json"
DEFAULT_OUTCOME_LOOKUP = PROJECT_ROOT / "contracts" / "outcome_vocab" / "outcome_lookup.json"
DEFAULT_ALIAS_RULES = PROJECT_ROOT / "config" / "bn_unresolved_alias_rules.json"
DEFAULT_REPORT_JSON = PROJECT_ROOT / "data" / "review" / "bn_unresolved_repair_report.json"
DEFAULT_MAPPING_JSONL = PROJECT_ROOT / "data" / "review" / "bn_unresolved_replacement_map.jsonl"
DEFAULT_CANDIDATE_JSON = PROJECT_ROOT / "data" / "production" / "realtime_incremental_bn.candidate.json"

RAW_PREFIX_ENV = "env.unresolved."
RAW_PREFIX_OUT = "out.unresolved."

LEADING_NOISE_TOKENS = {
    "col",
    "row",
    "tbl",
    "table",
    "var",
    "variable",
    "result",
    "results",
    "measure",
    "metric",
    "item",
    "topic",
    "code",
    "figure",
}

GLOBAL_NOISE_TOKENS = {
    "abstract",
    "author",
    "bulletin",
    "cid",
    "day",
    "doi",
    "figure",
    "fig",
    "introduction",
    "journal",
    "methods",
    "month",
    "paper",
    "reports",
    "results",
    "review",
    "reviews",
    "scientific",
    "study",
    "table",
    "tables",
    "week",
    "year",
}

TOKEN_RE = re.compile(r"[a-z0-9]+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bn-json", type=Path, default=DEFAULT_BN_JSON)
    parser.add_argument("--env-lookup", type=Path, default=DEFAULT_ENV_LOOKUP)
    parser.add_argument("--outcome-lookup", type=Path, default=DEFAULT_OUTCOME_LOOKUP)
    parser.add_argument("--alias-rules", type=Path, default=DEFAULT_ALIAS_RULES)
    parser.add_argument("--disable-alias-rules", action="store_true")
    parser.add_argument("--require-existing-targets", action="store_true")
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--mapping-jsonl", type=Path, default=DEFAULT_MAPPING_JSONL)
    parser.add_argument("--candidate-bn-json", type=Path, default=DEFAULT_CANDIDATE_JSON)
    parser.add_argument("--write-candidate", action="store_true")
    parser.add_argument("--enable-fuzzy", action="store_true")
    parser.add_argument("--fuzzy-cutoff", type=float, default=0.96)
    parser.add_argument(
        "--fallback-unknown-namespace",
        action="store_true",
        help="Map unmatched unresolved nodes to env.unknown.* / out.unknown.* (typed mode preserves raw suffix).",
    )
    parser.add_argument(
        "--alias-resolution-mode",
        choices=("typed", "merge"),
        default="typed",
        help="typed preserves per-term suffix under canonical family; merge maps directly to canonical node",
    )
    parser.add_argument("--max-term-tokens", type=int, default=8)
    parser.add_argument("--max-noise-tokens", type=int, default=1)
    parser.add_argument("--max-examples", type=int, default=20)
    return parser.parse_args()


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"[._\-]+", " ", text)
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def safe_node_component(name: str) -> str:
    s = (name or "").strip().lower()
    s = re.sub(r"[\s\-]+", "_", s)
    s = re.sub(r"[^a-z0-9_.]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("._")
    return s or "unknown"


def make_node_id(kind: str, canonical_id: str) -> str:
    canonical_id = (canonical_id or "").strip()
    if not canonical_id:
        return ""
    if canonical_id.startswith(("env.", "out.")):
        return canonical_id if canonical_id.startswith(f"{kind}.") else ""
    return f"{kind}.{safe_node_component(canonical_id)}"


def make_typed_alias_node_id(
    kind: str,
    canonical_id: str,
    raw_component: str,
    *,
    force_hash_suffix: bool = False,
) -> str:
    base = make_node_id(kind, canonical_id)
    if not base:
        return ""
    suffix = safe_node_component(raw_component)
    digest = hashlib.sha1((raw_component or "").encode("utf-8")).hexdigest()[:8]
    if not suffix:
        suffix = digest if force_hash_suffix else "unknown"
    if len(suffix) > 64:
        suffix = f"{suffix[:55]}_{digest}"
    elif force_hash_suffix:
        suffix = f"{suffix}_{digest}"
    return f"{base}.{suffix}"


def load_lookup(path: Path) -> tuple[dict[str, str], dict[str, str], list[str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw_lookup = payload.get("lookup", {})
    if not isinstance(raw_lookup, dict):
        return {}, {}, []
    norm_to_canonical: dict[str, str] = {}
    canonical_norm_to_raw: dict[str, str] = {}
    terms: list[str] = []
    for raw, canonical in raw_lookup.items():
        if not isinstance(raw, str) or not isinstance(canonical, str):
            continue
        n_raw = normalize(raw)
        if n_raw:
            norm_to_canonical[n_raw] = canonical
            terms.append(n_raw)
        n_canon = normalize(canonical)
        if n_canon:
            canonical_norm_to_raw[n_canon] = canonical
    return norm_to_canonical, canonical_norm_to_raw, sorted(set(terms))


def load_alias_rules(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    rules = payload.get("rules", []) if isinstance(payload, dict) else []
    out: list[dict[str, Any]] = []
    for index, rule in enumerate(rules):
        if not isinstance(rule, dict):
            continue
        kind = str(rule.get("kind", "")).strip().lower()
        canonical_id = str(rule.get("canonical_id", "")).strip()
        anchors = rule.get("anchors_any", [])
        if kind not in {"env", "out"} or not canonical_id or not isinstance(anchors, list):
            continue
        parsed = {
            "id": str(rule.get("id", f"rule_{index + 1}")),
            "kind": kind,
            "canonical_id": canonical_id,
            "anchors_any": [normalize(str(item)) for item in anchors if str(item).strip()],
            "tokens_all": [
                normalize(str(item)) for item in rule.get("tokens_all", []) if str(item).strip()
            ],
            "tokens_none": [
                normalize(str(item)) for item in rule.get("tokens_none", []) if str(item).strip()
            ],
            "max_tokens": int(rule.get("max_tokens", 8)),
            "max_noise_tokens": int(rule.get("max_noise_tokens", 1)),
            "confidence": float(rule.get("confidence", 0.92)),
        }
        if parsed["anchors_any"]:
            out.append(parsed)
    return out


def tokenize(raw_component: str) -> list[str]:
    raw = raw_component.lower().replace(".", "_")
    parts = TOKEN_RE.findall(raw)
    out: list[str] = []
    for token in parts:
        trimmed = token
        for prefix in LEADING_NOISE_TOKENS:
            if trimmed.startswith(prefix) and len(trimmed) > len(prefix) + 2:
                trimmed = trimmed[len(prefix) :]
        if trimmed:
            out.append(trimmed)
    return out


def token_matches_anchor(token: str, anchor: str) -> bool:
    if len(anchor) <= 4:
        return token == anchor
    return token == anchor or token.startswith(anchor) or token.endswith(anchor)


def variant_candidates(raw_component: str) -> list[str]:
    base = (raw_component or "").strip()
    variants = {base, base.replace("_", " "), base.replace(".", " ")}

    tokens = [t for t in re.split(r"[._\s]+", base.lower()) if t]
    trimmed = list(tokens)
    while trimmed and trimmed[0] in LEADING_NOISE_TOKENS:
        trimmed = trimmed[1:]
    if trimmed:
        variants.add(" ".join(trimmed))

    if len(tokens) >= 2 and len(tokens[0]) <= 2:
        variants.add(" ".join(tokens[1:]))

    normalized = [normalize(v) for v in variants]
    return [v for v in normalized if v]


def match_canonical(
    raw_component: str,
    lookup_map: dict[str, str],
    canonical_map: dict[str, str],
    lookup_terms: list[str],
    *,
    enable_fuzzy: bool,
    fuzzy_cutoff: float,
) -> tuple[str, str, float]:
    for variant in variant_candidates(raw_component):
        if variant in lookup_map:
            return lookup_map[variant], "lookup_exact", 1.0
        if variant in canonical_map:
            return canonical_map[variant], "canonical_exact", 1.0

    if enable_fuzzy and lookup_terms:
        for variant in variant_candidates(raw_component):
            match = difflib.get_close_matches(variant, lookup_terms, n=1, cutoff=fuzzy_cutoff)
            if match:
                canonical = lookup_map.get(match[0], "")
                if canonical:
                    return canonical, "lookup_fuzzy", fuzzy_cutoff
    return "", "unmatched", 0.0


def match_alias_rule(
    raw_component: str,
    kind: str,
    rules: list[dict[str, Any]],
    *,
    existing_node_ids: set[str],
    require_existing_targets: bool,
    max_term_tokens: int,
    max_noise_tokens: int,
) -> tuple[str, str, float, str]:
    tokens = tokenize(raw_component)
    if not tokens:
        return "", "alias_unmatched", 0.0, ""
    if len(tokens) > max_term_tokens:
        return "", "alias_unmatched", 0.0, ""

    noise_count = sum(1 for token in tokens if token in GLOBAL_NOISE_TOKENS)
    token_set = set(tokens)

    candidates: list[tuple[str, str, float]] = []
    for rule in rules:
        if rule["kind"] != kind:
            continue
        if len(tokens) > min(rule["max_tokens"], max_term_tokens):
            continue
        if noise_count > min(rule["max_noise_tokens"], max_noise_tokens):
            continue

        anchors = rule["anchors_any"]
        if not any(token_matches_anchor(token, anchor) for token in tokens for anchor in anchors):
            continue

        tokens_all = rule["tokens_all"]
        if tokens_all and not all(
            any(token_matches_anchor(token, required) for token in tokens)
            for required in tokens_all
        ):
            continue

        tokens_none = rule["tokens_none"]
        if any(
            forbidden in token_set
            or any(token_matches_anchor(token, forbidden) for token in tokens)
            for forbidden in tokens_none
        ):
            continue

        target_node = make_node_id(kind, rule["canonical_id"])
        if not target_node:
            continue
        if require_existing_targets and target_node not in existing_node_ids:
            continue
        candidates.append((rule["canonical_id"], rule["id"], rule["confidence"]))

    if not candidates:
        return "", "alias_unmatched", 0.0, ""

    canonical_targets = {canonical for canonical, _rule_id, _confidence in candidates}
    if len(canonical_targets) > 1:
        return "", "alias_conflict", 0.0, ",".join(sorted({rule_id for _c, rule_id, _s in candidates}))

    canonical, rule_id, confidence = max(candidates, key=lambda item: item[2])
    return canonical, "alias_rule", confidence, rule_id


def parse_edges(data: dict[str, Any]) -> list[dict[str, str]]:
    edges = data.get("edges", {})
    pairs: list[dict[str, str]] = []
    if isinstance(edges, dict):
        for edge in edges.values():
            if not isinstance(edge, dict):
                continue
            s = edge.get("source")
            t = edge.get("target")
            if s is None or t is None:
                continue
            pairs.append({"source": str(s), "target": str(t)})
    elif isinstance(edges, list):
        for edge in edges:
            if not isinstance(edge, dict):
                continue
            s = edge.get("source") or edge.get("from")
            t = edge.get("target") or edge.get("to")
            if s is None or t is None:
                continue
            pairs.append({"source": str(s), "target": str(t)})
    return pairs


def graph_metrics(data: dict[str, Any]) -> dict[str, float]:
    nodes = [str(n) for n in data.get("nodes", []) if n is not None]
    node_set = set(nodes)
    unresolved_count = sum(1 for n in nodes if ".unresolved." in n)
    unresolved_pct = (100.0 * unresolved_count / len(nodes)) if nodes else 0.0

    pairs = parse_edges(data)
    und: dict[str, set[str]] = defaultdict(set)
    for pair in pairs:
        s, t = pair["source"], pair["target"]
        if s in node_set and t in node_set:
            und[s].add(t)
            und[t].add(s)

    seen: set[str] = set()
    largest = 0
    components = 0
    for node in node_set:
        if node in seen:
            continue
        components += 1
        q = deque([node])
        seen.add(node)
        size = 0
        while q:
            cur = q.popleft()
            size += 1
            for nxt in und.get(cur, set()):
                if nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
        largest = max(largest, size)

    largest_pct = (100.0 * largest / len(nodes)) if nodes else 0.0
    return {
        "nodes": float(len(nodes)),
        "edges": float(len(pairs)),
        "unresolved_count": float(unresolved_count),
        "unresolved_pct": unresolved_pct,
        "connected_components": float(components),
        "largest_component_count": float(largest),
        "largest_component_pct": largest_pct,
    }


def apply_replacements(data: dict[str, Any], replacements: dict[str, str]) -> dict[str, Any]:
    out = json.loads(json.dumps(data))

    nodes = [str(n) for n in out.get("nodes", []) if n is not None]
    dedup_nodes: list[str] = []
    seen_nodes: set[str] = set()
    for node in nodes:
        new_node = replacements.get(node, node)
        if new_node not in seen_nodes:
            dedup_nodes.append(new_node)
            seen_nodes.add(new_node)
    out["nodes"] = dedup_nodes

    edges = out.get("edges", {})
    if isinstance(edges, dict):
        for edge in edges.values():
            if not isinstance(edge, dict):
                continue
            for key in ("source", "target", "from", "to"):
                value = edge.get(key)
                if isinstance(value, str) and value in replacements:
                    edge[key] = replacements[value]
    elif isinstance(edges, list):
        for edge in edges:
            if not isinstance(edge, dict):
                continue
            for key in ("source", "target", "from", "to"):
                value = edge.get(key)
                if isinstance(value, str) and value in replacements:
                    edge[key] = replacements[value]
    return out


def main() -> int:
    args = parse_args()
    if not args.bn_json.exists():
        raise FileNotFoundError(f"BN JSON not found: {args.bn_json}")
    if not args.env_lookup.exists():
        raise FileNotFoundError(f"Environment lookup not found: {args.env_lookup}")
    if not args.outcome_lookup.exists():
        raise FileNotFoundError(f"Outcome lookup not found: {args.outcome_lookup}")

    data = json.loads(args.bn_json.read_text(encoding="utf-8"))
    nodes = [str(n) for n in data.get("nodes", []) if n is not None]
    existing_node_ids = set(nodes)

    env_lookup, env_canonical, env_terms = load_lookup(args.env_lookup)
    out_lookup, out_canonical, out_terms = load_lookup(args.outcome_lookup)
    alias_rules = [] if args.disable_alias_rules else load_alias_rules(args.alias_rules)

    replacements: dict[str, str] = {}
    mapping_rows: list[dict[str, Any]] = []
    by_method: Counter[str] = Counter()
    unresolved_counter: Counter[str] = Counter()

    for node in nodes:
        canonical = ""
        method = "unmatched"
        confidence = 0.0
        matched_rule_id = ""

        if node.startswith(RAW_PREFIX_ENV):
            kind = "env"
            raw_component = node[len(RAW_PREFIX_ENV) :]
            canonical, method, confidence = match_canonical(
                raw_component,
                env_lookup,
                env_canonical,
                env_terms,
                enable_fuzzy=args.enable_fuzzy,
                fuzzy_cutoff=args.fuzzy_cutoff,
            )
        elif node.startswith(RAW_PREFIX_OUT):
            kind = "out"
            raw_component = node[len(RAW_PREFIX_OUT) :]
            canonical, method, confidence = match_canonical(
                raw_component,
                out_lookup,
                out_canonical,
                out_terms,
                enable_fuzzy=args.enable_fuzzy,
                fuzzy_cutoff=args.fuzzy_cutoff,
            )
        else:
            continue

        unresolved_counter[f"{kind}.{raw_component}"] += 1

        if not canonical:
            alias_canonical, alias_method, alias_confidence, alias_rule_id = match_alias_rule(
                raw_component,
                kind,
                alias_rules,
                existing_node_ids=existing_node_ids,
                require_existing_targets=args.require_existing_targets,
                max_term_tokens=args.max_term_tokens,
                max_noise_tokens=args.max_noise_tokens,
            )
            if alias_canonical:
                canonical = alias_canonical
                method = alias_method
                confidence = alias_confidence
                matched_rule_id = alias_rule_id
            elif alias_method == "alias_conflict":
                by_method[alias_method] += 1

        if not canonical and args.fallback_unknown_namespace:
            canonical = f"{kind}.unknown"
            method = "fallback_unknown_namespace"
            confidence = 0.5

        if not canonical:
            by_method["unmatched"] += 1
            continue

        if method == "alias_rule" and args.alias_resolution_mode == "typed":
            new_node = make_typed_alias_node_id(kind, canonical, raw_component)
        elif method == "fallback_unknown_namespace" and args.alias_resolution_mode == "typed":
            new_node = make_typed_alias_node_id(
                kind,
                canonical,
                raw_component,
                force_hash_suffix=True,
            )
        else:
            new_node = make_node_id(kind, canonical)
        if not new_node:
            by_method["invalid_target"] += 1
            continue
        if new_node == node:
            continue

        replacements[node] = new_node
        by_method[method] += 1
        mapping_rows.append(
            {
                "old_node_id": node,
                "new_node_id": new_node,
                "kind": kind,
                "raw_component": raw_component,
                "canonical_id": canonical,
                "match_method": method,
                "confidence": confidence,
                "alias_rule_id": matched_rule_id,
            }
        )

    before = graph_metrics(data)
    candidate_data = apply_replacements(data, replacements)
    after = graph_metrics(candidate_data)

    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.mapping_jsonl.parent.mkdir(parents=True, exist_ok=True)

    with args.mapping_jsonl.open("w", encoding="utf-8") as handle:
        for row in sorted(mapping_rows, key=lambda item: item["old_node_id"]):
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    report = {
        "generated_at_utc": _now_utc(),
        "paths": {
            "bn_json": str(args.bn_json),
            "env_lookup": str(args.env_lookup),
            "outcome_lookup": str(args.outcome_lookup),
            "alias_rules": str(args.alias_rules),
            "candidate_bn_json": str(args.candidate_bn_json),
            "mapping_jsonl": str(args.mapping_jsonl),
        },
        "config": {
            "enable_fuzzy": bool(args.enable_fuzzy),
            "fuzzy_cutoff": float(args.fuzzy_cutoff),
            "alias_rules_enabled": not bool(args.disable_alias_rules),
            "alias_resolution_mode": str(args.alias_resolution_mode),
            "require_existing_targets": bool(args.require_existing_targets),
            "fallback_unknown_namespace": bool(args.fallback_unknown_namespace),
            "max_term_tokens": int(args.max_term_tokens),
            "max_noise_tokens": int(args.max_noise_tokens),
            "write_candidate": bool(args.write_candidate),
        },
        "before": before,
        "after_if_applied": after,
        "delta": {
            "unresolved_count": int(after["unresolved_count"] - before["unresolved_count"]),
            "unresolved_pct": round(after["unresolved_pct"] - before["unresolved_pct"], 4),
            "largest_component_pct": round(after["largest_component_pct"] - before["largest_component_pct"], 4),
        },
        "proposed_replacements": {
            "count": len(replacements),
            "by_method": dict(by_method),
            "examples": sorted(mapping_rows, key=lambda item: item["confidence"], reverse=True)[
                : args.max_examples
            ],
        },
        "top_unresolved_samples": [
            {"node_id": node_id, "count": count}
            for node_id, count in unresolved_counter.most_common(args.max_examples)
        ],
    }
    args.report_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if args.write_candidate:
        args.candidate_bn_json.parent.mkdir(parents=True, exist_ok=True)
        args.candidate_bn_json.write_text(json.dumps(candidate_data, indent=2), encoding="utf-8")
        wrote = f"candidate written: {args.candidate_bn_json}"
    else:
        wrote = "candidate not written (dry-run)"

    print(
        "BN unresolved repair audit complete | "
        f"proposed_replacements={len(replacements)} | "
        f"unresolved_pct_before={before['unresolved_pct']:.3f} | "
        f"unresolved_pct_after={after['unresolved_pct']:.3f}"
    )
    print(f"report: {args.report_json}")
    print(f"mapping: {args.mapping_jsonl}")
    print(wrote)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
