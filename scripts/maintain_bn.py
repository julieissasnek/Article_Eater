#!/usr/bin/env python3
"""
BN Maintenance Script
======================
Performs maintenance operations on the Bayesian Network:

  1. PRUNE    — Remove/flag BN nodes linked to off-topic beliefs
  2. ORPHAN   — Detect BN nodes with no matching web belief
  3. WEAK     — Identify edges with very low confidence (alpha+beta < 2)
  4. STALE    — Flag nodes not updated since a threshold date
  5. REPORT   — Summary of BN health and maintenance actions

Usage:
    python scripts/maintain_bn.py --dry-run
    python scripts/maintain_bn.py --apply
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.db_locator import resolve_web_db

BN_JSON = PROJECT_ROOT / "data" / "production" / "realtime_incremental_bn.json"
MASTER_WEB_ID = "master:web:accumulated"


def load_bn() -> Dict[str, Any]:
    with open(BN_JSON) as f:
        return json.load(f)


def save_bn(bn: Dict[str, Any]):
    # Backup first
    backup = BN_JSON.with_suffix(f".{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak")
    import shutil
    shutil.copy2(BN_JSON, backup)
    with open(BN_JSON, "w") as f:
        json.dump(bn, f, indent=2)
    print(f"  Backup: {backup}")


# ═══════════════════════════════════════════════════════════════════════
# PHASE 1: PRUNE OFF-TOPIC NODES
# ═══════════════════════════════════════════════════════════════════════

def phase_prune_offtopic(bn: Dict, conn: sqlite3.Connection, dry_run: bool) -> Dict[str, Any]:
    """Remove BN nodes whose source beliefs are tagged off-topic."""
    # Get off-topic belief IDs from web DB
    cols = [r[1] for r in conn.execute("PRAGMA table_info(beliefs)").fetchall()]
    if "off_topic" not in cols:
        print("  No off_topic column found — skipping prune.")
        return {"pruned": 0, "reason": "no_off_topic_column"}

    off_topic_ids = set(r[0] for r in conn.execute(
        "SELECT belief_id FROM beliefs WHERE web_id = ? AND off_topic = 1",
        (MASTER_WEB_ID,)
    ).fetchall())

    if not off_topic_ids:
        print("  No off-topic beliefs found.")
        return {"pruned": 0}

    # Find BN nodes that partially match off-topic belief IDs
    nodes_to_remove = set()
    for node_id in bn.get("nodes", []):
        # BN nodes are like env.noise, out.cognition etc.
        # They don't directly correspond to belief IDs, but we check
        # if any off-topic belief references this env/outcome pair
        pass

    # More realistic: check if any BN edge key references off-topic content
    # Since BN edges are env→outcome, we check if the env or outcome
    # tokens appear in off-topic beliefs more than on-topic ones
    off_topic_contents = set()
    for bid in off_topic_ids:
        content = conn.execute(
            "SELECT content FROM beliefs WHERE belief_id = ? AND web_id = ?",
            (bid, MASTER_WEB_ID)
        ).fetchone()
        if content:
            off_topic_contents.add(content[0].lower())

    # Check for BN nodes that ONLY appear in off-topic beliefs
    all_beliefs_content = conn.execute(
        "SELECT content FROM beliefs WHERE web_id = ? AND (off_topic IS NULL OR off_topic = 0)",
        (MASTER_WEB_ID,)
    ).fetchall()
    on_topic_text = " ".join(r[0].lower() for r in all_beliefs_content)

    flagged_nodes = []
    for node_id in bn.get("nodes", []):
        # Extract the meaningful part of node ID (e.g., "noise" from "env.noise")
        parts = node_id.split(".")
        token = parts[-1] if len(parts) > 1 else node_id

        # Skip common tokens
        if token in ("unknown", "general", "other"):
            continue

        # Check if this token appears ONLY in off-topic content
        in_off_topic = any(token in c for c in off_topic_contents)
        in_on_topic = token in on_topic_text

        if in_off_topic and not in_on_topic:
            flagged_nodes.append(node_id)

    print(f"\n{'='*60}")
    print(f"PHASE 1: PRUNE OFF-TOPIC BN NODES")
    print(f"{'='*60}")
    print(f"  Off-topic beliefs in web: {len(off_topic_ids)}")
    print(f"  BN nodes flagged: {len(flagged_nodes)}")
    if flagged_nodes:
        for n in flagged_nodes[:10]:
            print(f"    - {n}")

    if not dry_run and flagged_nodes:
        bn["nodes"] = [n for n in bn["nodes"] if n not in set(flagged_nodes)]
        edges_to_remove = []
        for edge_key, edge_data in bn.get("edges", {}).items():
            src = edge_data.get("source", "")
            tgt = edge_data.get("target", "")
            if src in set(flagged_nodes) or tgt in set(flagged_nodes):
                edges_to_remove.append(edge_key)
        for ek in edges_to_remove:
            del bn["edges"][ek]
        print(f"  ✅ Removed {len(flagged_nodes)} nodes, {len(edges_to_remove)} edges")
    elif dry_run:
        print(f"  [DRY RUN] Would remove {len(flagged_nodes)} nodes")

    return {"flagged": len(flagged_nodes)}


# ═══════════════════════════════════════════════════════════════════════
# PHASE 2: ORPHAN NODE DETECTION
# ═══════════════════════════════════════════════════════════════════════

def phase_orphan_detection(bn: Dict, conn: sqlite3.Connection) -> Dict[str, Any]:
    """Find BN nodes with no edges (isolated)."""
    nodes_in_edges = set()
    for edge_key, edge_data in bn.get("edges", {}).items():
        nodes_in_edges.add(edge_data.get("source", ""))
        nodes_in_edges.add(edge_data.get("target", ""))

    orphan_nodes = [n for n in bn.get("nodes", []) if n not in nodes_in_edges]

    print(f"\n{'='*60}")
    print(f"PHASE 2: ORPHAN BN NODE DETECTION")
    print(f"{'='*60}")
    print(f"  Total BN nodes: {len(bn.get('nodes', []))}")
    print(f"  Nodes in edges: {len(nodes_in_edges)}")
    print(f"  Orphan nodes: {len(orphan_nodes)}")

    # Categorize orphans
    env_orphans = [n for n in orphan_nodes if n.startswith("env.")]
    out_orphans = [n for n in orphan_nodes if n.startswith("out.")]
    other_orphans = [n for n in orphan_nodes if not n.startswith("env.") and not n.startswith("out.")]

    print(f"    env.* orphans: {len(env_orphans)}")
    print(f"    out.* orphans: {len(out_orphans)}")
    print(f"    other orphans: {len(other_orphans)}")

    if orphan_nodes[:5]:
        print(f"  Samples: {orphan_nodes[:5]}")

    return {
        "total_orphans": len(orphan_nodes),
        "env_orphans": len(env_orphans),
        "out_orphans": len(out_orphans),
    }


# ═══════════════════════════════════════════════════════════════════════
# PHASE 3: WEAK EDGE DETECTION
# ═══════════════════════════════════════════════════════════════════════

def phase_weak_edges(bn: Dict) -> Dict[str, Any]:
    """Identify edges with very weak evidence (low alpha+beta = few observations)."""
    WEAK_THRESHOLD = 2.0  # alpha + beta < 2 means < 2 effective observations

    weak = []
    strong = 0
    moderate = 0

    for edge_key, edge_data in bn.get("edges", {}).items():
        alpha = edge_data.get("alpha", 0)
        beta = edge_data.get("beta", 0)
        total_obs = alpha + beta

        if total_obs < WEAK_THRESHOLD:
            weak.append({
                "edge": edge_key,
                "alpha": alpha,
                "beta": beta,
                "mean": edge_data.get("mean", 0),
                "observations": total_obs,
            })
        elif total_obs < 10:
            moderate += 1
        else:
            strong += 1

    print(f"\n{'='*60}")
    print(f"PHASE 3: WEAK BN EDGE DETECTION")
    print(f"{'='*60}")
    print(f"  Total edges: {len(bn.get('edges', {}))}")
    print(f"  Strong (≥10 obs): {strong}")
    print(f"  Moderate (2-10 obs): {moderate}")
    print(f"  Weak (<2 obs): {len(weak)}")

    if weak[:5]:
        print(f"  Weakest edges:")
        for w in sorted(weak, key=lambda x: x["observations"])[:5]:
            print(f"    {w['edge']}: α={w['alpha']:.2f}, β={w['beta']:.2f}, mean={w['mean']:.4f}")

    return {
        "strong": strong,
        "moderate": moderate,
        "weak": len(weak),
    }


# ═══════════════════════════════════════════════════════════════════════
# PHASE 4: NODE TYPE AUDIT
# ═══════════════════════════════════════════════════════════════════════

def phase_node_type_audit(bn: Dict) -> Dict[str, Any]:
    """Categorize BN nodes by type prefix and check naming consistency."""
    type_counts: Dict[str, int] = defaultdict(int)
    unknown_nodes = []

    for node_id in bn.get("nodes", []):
        parts = node_id.split(".")
        if len(parts) >= 2:
            prefix = parts[0]
            type_counts[prefix] += 1
            if "unknown" in node_id:
                unknown_nodes.append(node_id)
        else:
            type_counts["no_prefix"] += 1

    print(f"\n{'='*60}")
    print(f"PHASE 4: BN NODE TYPE AUDIT")
    print(f"{'='*60}")
    for prefix, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {prefix}: {count}")
    print(f"  Nodes with 'unknown': {len(unknown_nodes)}")

    return {
        "type_counts": dict(type_counts),
        "unknown_count": len(unknown_nodes),
    }


# ═══════════════════════════════════════════════════════════════════════
# PHASE 5: EDGE DISTRIBUTION ANALYSIS
# ═══════════════════════════════════════════════════════════════════════

def phase_edge_distribution(bn: Dict) -> Dict[str, Any]:
    """Analyze the distribution of edge strengths and types."""
    means = []
    stds = []
    edge_types: Dict[str, int] = defaultdict(int)
    very_strong = []
    very_weak_effect = []

    for edge_key, edge_data in bn.get("edges", {}).items():
        mean = edge_data.get("mean", 0)
        std = edge_data.get("std", 0)
        etype = edge_data.get("edge_type", "unknown")

        means.append(mean)
        stds.append(std)
        edge_types[etype] += 1

        if mean > 0.5:
            very_strong.append((edge_key, mean))
        elif mean < 0.01 and (edge_data.get("alpha", 0) + edge_data.get("beta", 0)) > 5:
            very_weak_effect.append((edge_key, mean))

    import statistics
    avg_mean = statistics.mean(means) if means else 0
    median_mean = statistics.median(means) if means else 0

    print(f"\n{'='*60}")
    print(f"PHASE 5: BN EDGE DISTRIBUTION")
    print(f"{'='*60}")
    print(f"  Edge types: {dict(edge_types)}")
    print(f"  Mean effect size: {avg_mean:.4f}")
    print(f"  Median effect size: {median_mean:.4f}")
    print(f"  Very strong (mean > 0.5): {len(very_strong)}")
    print(f"  Very weak effect (mean < 0.01, 5+ obs): {len(very_weak_effect)}")

    if very_strong[:3]:
        print(f"  Strongest edges:")
        for ek, m in sorted(very_strong, key=lambda x: -x[1])[:3]:
            print(f"    {ek}: {m:.4f}")

    return {
        "avg_mean": round(avg_mean, 4),
        "median_mean": round(median_mean, 4),
        "very_strong": len(very_strong),
        "very_weak_effect": len(very_weak_effect),
        "edge_types": dict(edge_types),
    }


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

def main() -> int:
    parser = argparse.ArgumentParser(description="BN maintenance.")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--apply", action="store_true", help="Apply maintenance changes")
    args = parser.parse_args()

    dry_run = not args.apply

    if not BN_JSON.exists():
        print(f"ERROR: BN file not found: {BN_JSON}")
        return 1

    bn = load_bn()
    db_path = resolve_web_db(None, prefer="integrated")
    conn = sqlite3.connect(str(db_path))

    print(f"BN File: {BN_JSON}")
    print(f"Web DB: {db_path}")
    print(f"Mode: {'DRY RUN' if dry_run else 'APPLY'}")
    print(f"Time: {datetime.now().isoformat()}")
    print(f"BN: {len(bn.get('nodes', []))} nodes, {len(bn.get('edges', {}))} edges")

    results = {}
    results["prune"] = phase_prune_offtopic(bn, conn, dry_run)
    results["orphans"] = phase_orphan_detection(bn, conn)
    results["weak_edges"] = phase_weak_edges(bn)
    results["node_types"] = phase_node_type_audit(bn)
    results["edge_distribution"] = phase_edge_distribution(bn)

    # Save if applying changes
    if args.apply and results.get("prune", {}).get("flagged", 0) > 0:
        save_bn(bn)
        print(f"\n  ✅ BN saved with changes")

    # Summary
    print(f"\n{'='*60}")
    print(f"BN MAINTENANCE SUMMARY")
    print(f"{'='*60}")
    print(f"  Off-topic nodes flagged: {results['prune'].get('flagged', 0)}")
    print(f"  Orphan nodes: {results['orphans']['total_orphans']}")
    print(f"  Weak edges (<2 obs): {results['weak_edges']['weak']}")
    print(f"  Unknown-type nodes: {results['node_types']['unknown_count']}")
    print(f"  Mean effect size: {results['edge_distribution']['avg_mean']}")

    # Write report
    report_path = PROJECT_ROOT / "data" / "production" / "bn_maintenance_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump({"timestamp": datetime.now().isoformat(), **results}, f, indent=2)
    print(f"\n  Report: {report_path}")

    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
