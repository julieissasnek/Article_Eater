#!/usr/bin/env python3
"""
Compute Web/BN health metrics and evaluate configured thresholds.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Dict, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WEB_DB = PROJECT_ROOT / "data" / "web_persistence.db"
DEFAULT_BN_JSON = PROJECT_ROOT / "data" / "production" / "realtime_incremental_bn.json"
DEFAULT_THRESHOLDS = PROJECT_ROOT / "config" / "web_bn_health_thresholds.json"
MASTER_WEB_ID = "master:web:accumulated"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Check Web/BN health against threshold gates.")
    p.add_argument("--web-db", default=str(DEFAULT_WEB_DB), help="Path to web_persistence.db")
    p.add_argument("--bn-json", default=str(DEFAULT_BN_JSON), help="Path to realtime_incremental_bn.json")
    p.add_argument("--thresholds", default=str(DEFAULT_THRESHOLDS), help="Path to thresholds JSON")
    p.add_argument("--json", action="store_true", help="Emit JSON report")
    return p.parse_args()


def _safe_pct(numer: float, denom: float) -> float:
    if denom <= 0:
        return 0.0
    return (100.0 * numer) / denom


def collect_web_metrics(web_db: Path) -> Dict[str, Any]:
    conn = sqlite3.connect(str(web_db))
    conn.row_factory = sqlite3.Row
    try:
        beliefs = conn.execute(
            "SELECT belief_id FROM beliefs WHERE web_id = ?",
            (MASTER_WEB_ID,),
        ).fetchall()
        constraints = conn.execute(
            "SELECT source_id, target_id, constraint_type FROM constraints WHERE web_id = ?",
            (MASTER_WEB_ID,),
        ).fetchall()
        bridges = conn.execute(
            "SELECT source_beliefs, target_beliefs FROM bridges WHERE web_id = ?",
            (MASTER_WEB_ID,),
        ).fetchall()

        belief_ids = [str(r["belief_id"]) for r in beliefs]
        bset = set(belief_ids)
        n_beliefs = len(belief_ids)
        n_constraints = len(constraints)
        n_bridges = len(bridges)

        indeg: Dict[str, int] = defaultdict(int)
        outdeg: Dict[str, int] = defaultdict(int)
        ctype = Counter()
        for r in constraints:
            s = str(r["source_id"])
            t = str(r["target_id"])
            ctype[str(r["constraint_type"])] += 1
            if s in bset:
                outdeg[s] += 1
            if t in bset:
                indeg[t] += 1

        isolated = 0
        both_sides = 0
        total_in = 0
        total_out = 0
        for b in belief_ids:
            i = indeg.get(b, 0)
            o = outdeg.get(b, 0)
            total_in += i
            total_out += o
            if i == 0 and o == 0:
                isolated += 1
            if i > 0 and o > 0:
                both_sides += 1

        bridge_with_source = 0
        for r in bridges:
            try:
                src = json.loads(r["source_beliefs"] or "[]")
            except Exception:
                src = []
            if isinstance(src, list) and len(src) > 0:
                bridge_with_source += 1

        explains = ctype.get("explains", 0)
        supports = ctype.get("supports", 0)
        contradicts = ctype.get("contradicts", 0)

        return {
            "beliefs": n_beliefs,
            "constraints": n_constraints,
            "bridges": n_bridges,
            "supports_count": supports,
            "explains_count": explains,
            "contradicts_count": contradicts,
            "supports_share_pct": _safe_pct(supports, n_constraints),
            "explains_share_pct": _safe_pct(explains, n_constraints),
            "contradicts_share_pct": _safe_pct(contradicts, n_constraints),
            "isolated_count": isolated,
            "isolated_pct": _safe_pct(isolated, n_beliefs),
            "both_sides_count": both_sides,
            "both_sides_pct": _safe_pct(both_sides, n_beliefs),
            "avg_indeg": (total_in / n_beliefs) if n_beliefs else 0.0,
            "avg_outdeg": (total_out / n_beliefs) if n_beliefs else 0.0,
            "bridge_with_source_pct": _safe_pct(bridge_with_source, n_bridges),
        }
    finally:
        conn.close()


def collect_bn_metrics(bn_json: Path) -> Dict[str, Any]:
    data = json.loads(bn_json.read_text(encoding="utf-8"))
    nodes = [str(n) for n in data.get("nodes", []) if n is not None]
    node_set = set(nodes)

    raw_edges = data.get("edges", {})
    pairs: List[Tuple[str, str]] = []
    if isinstance(raw_edges, dict):
        for _, e in raw_edges.items():
            if not isinstance(e, dict):
                continue
            s = e.get("source")
            t = e.get("target")
            if s is None or t is None:
                continue
            pairs.append((str(s), str(t)))
    elif isinstance(raw_edges, list):
        for e in raw_edges:
            if not isinstance(e, dict):
                continue
            s = e.get("source") or e.get("from")
            t = e.get("target") or e.get("to")
            if s is None or t is None:
                continue
            pairs.append((str(s), str(t)))

    indeg: Dict[str, int] = defaultdict(int)
    outdeg: Dict[str, int] = defaultdict(int)
    und: Dict[str, set] = defaultdict(set)
    dangling = 0
    for s, t in pairs:
        if s not in node_set or t not in node_set:
            dangling += 1
            continue
        outdeg[s] += 1
        indeg[t] += 1
        und[s].add(t)
        und[t].add(s)

    isolated = 0
    for n in node_set:
        if indeg.get(n, 0) == 0 and outdeg.get(n, 0) == 0:
            isolated += 1

    # Largest weakly connected component
    seen = set()
    largest = 0
    for n in node_set:
        if n in seen:
            continue
        q = deque([n])
        seen.add(n)
        size = 0
        while q:
            u = q.popleft()
            size += 1
            for v in und.get(u, set()):
                if v not in seen:
                    seen.add(v)
                    q.append(v)
        largest = max(largest, size)

    # DAG cycle check
    adj: Dict[str, List[str]] = defaultdict(list)
    for s, t in pairs:
        if s in node_set and t in node_set:
            adj[s].append(t)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in node_set}

    def dfs(u: str) -> bool:
        color[u] = GRAY
        for v in adj.get(u, []):
            if color[v] == GRAY:
                return True
            if color[v] == WHITE and dfs(v):
                return True
        color[u] = BLACK
        return False

    has_cycle = False
    for n in node_set:
        if color[n] == WHITE and dfs(n):
            has_cycle = True
            break

    unresolved = sum(1 for n in node_set if ".unresolved." in n)

    return {
        "nodes": len(node_set),
        "edges": len(pairs),
        "dangling_edges": dangling,
        "has_cycle": 1 if has_cycle else 0,
        "isolated_count": isolated,
        "isolated_pct": _safe_pct(isolated, len(node_set)),
        "largest_component_count": largest,
        "largest_component_pct": _safe_pct(largest, len(node_set)),
        "unresolved_count": unresolved,
        "unresolved_pct": _safe_pct(unresolved, len(node_set)),
    }


def lookup_metric(metrics: Dict[str, Dict[str, Any]], metric_path: str) -> Any:
    layer, key = metric_path.split(".", 1)
    return metrics[layer][key]


def evaluate_checks(metrics: Dict[str, Dict[str, Any]], checks: List[Dict[str, Any]]) -> Dict[str, Any]:
    out = {"passed": 0, "failed": 0, "results": []}
    for chk in checks:
        metric = chk["metric"]
        op = chk["op"]
        val = chk["value"]
        actual = lookup_metric(metrics, metric)
        if op == ">=":
            ok = actual >= val
        elif op == "<=":
            ok = actual <= val
        elif op == "==":
            ok = actual == val
        else:
            raise ValueError(f"Unsupported op: {op}")
        out["results"].append(
            {
                "metric": metric,
                "op": op,
                "value": val,
                "actual": actual,
                "ok": ok,
                "description": chk.get("description", ""),
            }
        )
        if ok:
            out["passed"] += 1
        else:
            out["failed"] += 1
    out["ok"] = out["failed"] == 0
    return out


def main() -> int:
    args = parse_args()
    web_metrics = collect_web_metrics(Path(args.web_db))
    bn_metrics = collect_bn_metrics(Path(args.bn_json))
    thresholds = json.loads(Path(args.thresholds).read_text(encoding="utf-8"))

    metrics = {"web": web_metrics, "bn": bn_metrics}
    minimum = evaluate_checks(metrics, thresholds.get("minimum_viable", []))
    target = evaluate_checks(metrics, thresholds.get("target", []))

    report = {
        "metrics": metrics,
        "minimum_viable": minimum,
        "target": target,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Web metrics:")
        for k, v in web_metrics.items():
            print(f"  {k}: {v}")
        print("BN metrics:")
        for k, v in bn_metrics.items():
            print(f"  {k}: {v}")

        print(
            f"minimum_viable: {'PASS' if minimum['ok'] else 'FAIL'} "
            f"({minimum['passed']} passed, {minimum['failed']} failed)"
        )
        if not minimum["ok"]:
            for r in minimum["results"]:
                if not r["ok"]:
                    print(f"  FAIL {r['metric']} {r['op']} {r['value']} (actual={r['actual']})")

        print(
            f"target: {'PASS' if target['ok'] else 'FAIL'} "
            f"({target['passed']} passed, {target['failed']} failed)"
        )
        if not target["ok"]:
            for r in target["results"]:
                if not r["ok"]:
                    print(f"  TARGET MISS {r['metric']} {r['op']} {r['value']} (actual={r['actual']})")

    return 0 if minimum["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
