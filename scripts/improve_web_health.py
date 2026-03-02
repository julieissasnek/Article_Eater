#!/usr/bin/env python3
"""
Web of Belief Health Improvement Script
========================================
Diagnoses isolated beliefs and attempts to connect them to the main
web by mining the enriched template JSON catalog for keyword overlaps.

Strategies:
  1. TEMPLATE KEYWORD BRIDGE — match isolated belief content against
     template constructs, mechanism chains, and theory keys.
  2. TOPIC CLUSTERING — group isolated beliefs by shared environment
     or outcome vocabulary to create intra-cluster constraints.
  3. CONTRADICTION DISCOVERY — find belief pairs with opposing
     direction claims on the same environment-outcome pair.

Run with --dry-run to preview without writing to DB.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.db_locator import resolve_web_db

MASTER_WEB_ID = "master:web:accumulated"
TEMPLATE_DIR = PROJECT_ROOT / "data" / "templates"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Improve web health by connecting isolated beliefs.")
    p.add_argument("--dry-run", action="store_true", help="Preview without writing")
    p.add_argument("--max-new-constraints", type=int, default=500,
                   help="Cap on new constraints to add per run")
    return p.parse_args()


# ─── Template Loading ───────────────────────────────────────────────

def load_templates() -> List[Dict[str, Any]]:
    templates = []
    for fp in glob.glob(str(TEMPLATE_DIR / "*.json")):
        if fp.endswith(".bak"):
            continue
        try:
            with open(fp) as f:
                templates.append(json.load(f))
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")
    return templates


def build_template_keyword_index(templates: List[Dict]) -> Dict[str, List[str]]:
    """Map lowercased keywords → list of template_ids."""
    index: Dict[str, List[str]] = defaultdict(list)
    for t in templates:
        tid = t.get("template_id", "")
        # Harvest keywords from multiple fields
        words: Set[str] = set()

        for c in t.get("constructs", []):
            words.add(c.lower())

        for fw in t.get("t1_frameworks", []):
            if isinstance(fw, str):
                words.add(fw.lower())
            elif isinstance(fw, dict):
                words.add(fw.get("id", "").lower())

        name = t.get("template_name", t.get("name", ""))
        for token in re.split(r"[\s\-—:,]+", name.lower()):
            if len(token) > 4:
                words.add(token)

        # Mechanism chain descriptions
        for step in t.get("mechanism_chain", []):
            if isinstance(step, dict):
                desc = step.get("description", "").lower()
            elif isinstance(step, str):
                desc = step.lower()
            else:
                continue
            for token in re.split(r"[\s\-—:,]+", desc):
                if len(token) > 6:
                    words.add(token)

        for w in words:
            if w:
                index[w].append(tid)
    return index


# ─── Database Queries ────────────────────────────────────────────────

def get_isolated_beliefs(conn: sqlite3.Connection) -> List[Tuple[str, str]]:
    """Return (belief_id, content) for beliefs with zero constraints."""
    rows = conn.execute("""
        SELECT b.belief_id, b.content
        FROM beliefs b
        WHERE b.web_id = ?
          AND b.belief_id NOT IN (
              SELECT source_id FROM constraints WHERE web_id = ?
              UNION
              SELECT target_id FROM constraints WHERE web_id = ?
          )
    """, (MASTER_WEB_ID, MASTER_WEB_ID, MASTER_WEB_ID)).fetchall()
    return [(r[0], r[1]) for r in rows]


def get_all_beliefs(conn: sqlite3.Connection) -> List[Tuple[str, str]]:
    rows = conn.execute(
        "SELECT belief_id, content FROM beliefs WHERE web_id = ?",
        (MASTER_WEB_ID,)
    ).fetchall()
    return [(r[0], r[1]) for r in rows]


# ─── Strategy 1: Template Keyword Bridge ─────────────────────────────

def strategy_template_bridge(
    isolated: List[Tuple[str, str]],
    keyword_index: Dict[str, List[str]],
    all_beliefs: List[Tuple[str, str]],
) -> List[Dict]:
    """Find isolated beliefs whose content matches template keywords,
    then link them to non-isolated beliefs sharing the same template."""
    new_edges = []
    # Pre-index non-isolated beliefs by matched template
    non_isolated_ids = {bid for bid, _ in all_beliefs} - {bid for bid, _ in isolated}
    template_to_connected: Dict[str, List[str]] = defaultdict(list)

    for bid, content in all_beliefs:
        if bid not in non_isolated_ids:
            continue
        content_lower = content.lower()
        for kw, tids in keyword_index.items():
            if kw in content_lower:
                for tid in tids:
                    template_to_connected[tid].append(bid)

    # Now try to match each isolated belief
    for iso_id, iso_content in isolated:
        iso_lower = iso_content.lower()
        matched_templates: Set[str] = set()
        for kw, tids in keyword_index.items():
            if kw in iso_lower:
                matched_templates.update(tids)

        for tid in matched_templates:
            targets = template_to_connected.get(tid, [])
            if targets:
                # Pick the first connected belief sharing this template
                target = targets[0]
                new_edges.append({
                    "source_id": iso_id,
                    "target_id": target,
                    "constraint_type": "explains",
                    "strength": 0.3,
                    "provenance": f"template_bridge:{tid}",
                })
                break  # One edge per isolated belief is enough
    return new_edges


# ─── Strategy 2: Topic Clustering (Shared Vocabulary) ────────────────

def strategy_topic_cluster(isolated: List[Tuple[str, str]]) -> List[Dict]:
    """Group isolated beliefs by shared substantive tokens and link
    pairs within the same cluster."""
    # Extract significant tokens per belief
    token_to_beliefs: Dict[str, List[str]] = defaultdict(list)
    significant_words = set()

    for bid, content in isolated:
        tokens = set(re.findall(r"[a-z]{5,}", content.lower()))
        # Filter out very common words
        stopwords = {"abstract", "provisional", "unknown", "mixed", "positive",
                     "negative", "increase", "decrease", "effect", "effects",
                     "study", "studies", "research", "results", "found",
                     "significant", "participants", "between", "within",
                     "however", "therefore", "conclusion", "evidence"}
        tokens -= stopwords
        for t in tokens:
            token_to_beliefs[t].append(bid)

    # Find clusters: groups of isolated beliefs sharing 2+ rare tokens
    new_edges = []
    seen_pairs: Set[Tuple[str, str]] = set()

    for token, bids in token_to_beliefs.items():
        if len(bids) < 2 or len(bids) > 20:
            continue
        for i in range(len(bids)):
            for j in range(i + 1, min(i + 3, len(bids))):
                pair = tuple(sorted([bids[i], bids[j]]))
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    new_edges.append({
                        "source_id": pair[0],
                        "target_id": pair[1],
                        "constraint_type": "supports",
                        "strength": 0.2,
                        "provenance": f"topic_cluster:{token}",
                    })
    return new_edges


# ─── Strategy 3: Contradiction Discovery ─────────────────────────────

def strategy_contradiction_discovery(
    all_beliefs: List[Tuple[str, str]],
    conn: sqlite3.Connection
) -> List[Dict]:
    """Find belief pairs with opposing directions on the same
    environment→outcome pair."""
    DIRECTION_POSITIVE = {"positive", "increase", "increases", "higher", "enhance", "enhances"}
    DIRECTION_NEGATIVE = {"negative", "decrease", "decreases", "lower", "reduce", "reduces"}

    env_outcome_beliefs: Dict[str, List[Tuple[str, str]]] = defaultdict(list)

    for bid, content in all_beliefs:
        # Parse "env -> outcome (direction)" pattern
        match = re.match(r".*?:\s*(.+?)\s*->\s*(.+?)\s*\((\w+)\)", content)
        if match:
            env_token = match.group(1).strip().lower()[:40]
            out_token = match.group(2).strip().lower()[:40]
            direction = match.group(3).strip().lower()
            key = f"{env_token}|{out_token}"
            env_outcome_beliefs[key].append((bid, direction))

    new_edges = []
    for key, entries in env_outcome_beliefs.items():
        if len(entries) < 2:
            continue
        for i in range(len(entries)):
            for j in range(i + 1, len(entries)):
                bid_a, dir_a = entries[i]
                bid_b, dir_b = entries[j]
                a_pos = dir_a in DIRECTION_POSITIVE
                a_neg = dir_a in DIRECTION_NEGATIVE
                b_pos = dir_b in DIRECTION_POSITIVE
                b_neg = dir_b in DIRECTION_NEGATIVE
                if (a_pos and b_neg) or (a_neg and b_pos):
                    new_edges.append({
                        "source_id": bid_a,
                        "target_id": bid_b,
                        "constraint_type": "contradicts",
                        "strength": 0.5,
                        "provenance": f"contradiction_discovery:{key}",
                    })
    return new_edges


# ─── Main ────────────────────────────────────────────────────────────

def main() -> int:
    args = parse_args()
    db_path = resolve_web_db(None, prefer="integrated")
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    print(f"Database: {db_path}")

    isolated = get_isolated_beliefs(conn)
    all_beliefs = get_all_beliefs(conn)
    print(f"Total beliefs: {len(all_beliefs)}")
    print(f"Isolated beliefs: {len(isolated)}")

    templates = load_templates()
    keyword_index = build_template_keyword_index(templates)
    print(f"Template keyword index: {len(keyword_index)} keywords from {len(templates)} templates")

    # Run strategies
    print("\n--- Strategy 1: Template Keyword Bridge ---")
    s1_edges = strategy_template_bridge(isolated, keyword_index, all_beliefs)
    print(f"  New edges: {len(s1_edges)}")

    print("\n--- Strategy 2: Topic Clustering ---")
    s2_edges = strategy_topic_cluster(isolated)
    print(f"  New edges: {len(s2_edges)}")

    print("\n--- Strategy 3: Contradiction Discovery ---")
    s3_edges = strategy_contradiction_discovery(all_beliefs, conn)
    print(f"  New contradictions found: {len(s3_edges)}")

    all_new = s1_edges + s2_edges + s3_edges
    print(f"\nTotal new edges proposed: {len(all_new)}")

    if len(all_new) > args.max_new_constraints:
        print(f"  Capping at {args.max_new_constraints}")
        all_new = all_new[:args.max_new_constraints]

    if args.dry_run:
        print("\n[DRY RUN] No changes written.")
        # Show a sample
        for edge in all_new[:10]:
            print(f"  {edge['source_id'][:50]} -> {edge['target_id'][:50]} ({edge['constraint_type']}, {edge['provenance'][:40]})")
        return 0

    # Write to DB
    added = 0
    for edge in all_new:
        cid = f"health_improve:{edge['source_id'][:30]}:{edge['target_id'][:30]}"
        try:
            conn.execute("""
                INSERT OR IGNORE INTO constraints
                (constraint_id, web_id, source_id, target_id, constraint_type, strength, provenance, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                cid, MASTER_WEB_ID,
                edge["source_id"], edge["target_id"],
                edge["constraint_type"], edge["strength"],
                edge["provenance"]
            ))
            added += 1
        except Exception as e:
            print(f"  Error adding edge: {e}")
    conn.commit()
    print(f"\nInserted {added} new constraints into the web.")

    # Post-check
    new_isolated = get_isolated_beliefs(conn)
    print(f"Isolated beliefs BEFORE: {len(isolated)}")
    print(f"Isolated beliefs AFTER:  {len(new_isolated)}")
    print(f"Beliefs connected:       {len(isolated) - len(new_isolated)}")

    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
