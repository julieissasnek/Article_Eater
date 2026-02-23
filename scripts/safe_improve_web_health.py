#!/usr/bin/env python3
"""
Safe Web Health Improvement — Template Bridges Only
====================================================
Only runs Strategy 1 (template keyword bridges) which connects isolated
beliefs to the main web via expert-calibrated template vocabulary.

This is the safest strategy because:
  - Edges are low-strength (0.3) "explains" type — they suggest relevance,
    they do NOT assert strong causal claims
  - The connection is mediated by expert-panel-calibrated templates
  - No new beliefs or claims are created
  - All edges are tagged with provenance for easy rollback

Also runs the 5 contradiction edges found by Strategy 3. These are safe
because they only flag beliefs that explicitly claim opposite directions
on the same environment→outcome pair.
"""

from __future__ import annotations

import glob
import json
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


def load_templates() -> List[Dict[str, Any]]:
    templates = []
    for fp in glob.glob(str(TEMPLATE_DIR / "*.json")):
        if fp.endswith(".bak"):
            continue
        try:
            with open(fp) as f:
                templates.append(json.load(f))
        except Exception:
            pass
    return templates


def build_template_keyword_index(templates: List[Dict]) -> Dict[str, List[str]]:
    index: Dict[str, List[str]] = defaultdict(list)
    for t in templates:
        tid = t.get("template_id", "")
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


def get_isolated_beliefs(conn: sqlite3.Connection) -> List[Tuple[str, str]]:
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


def strategy_template_bridge(
    isolated: List[Tuple[str, str]],
    keyword_index: Dict[str, List[str]],
    all_beliefs: List[Tuple[str, str]],
) -> List[Dict]:
    new_edges = []
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

    for iso_id, iso_content in isolated:
        iso_lower = iso_content.lower()
        matched_templates: Set[str] = set()
        for kw, tids in keyword_index.items():
            if kw in iso_lower:
                matched_templates.update(tids)

        for tid in matched_templates:
            targets = template_to_connected.get(tid, [])
            if targets:
                target = targets[0]
                new_edges.append({
                    "source_id": iso_id,
                    "target_id": target,
                    "constraint_type": "explains",
                    "strength": 0.3,
                    "provenance": f"safe_template_bridge:{tid}",
                })
                break
    return new_edges


def strategy_contradiction_discovery(
    all_beliefs: List[Tuple[str, str]],
) -> List[Dict]:
    DIRECTION_POSITIVE = {"positive", "increase", "increases", "higher", "enhance", "enhances"}
    DIRECTION_NEGATIVE = {"negative", "decrease", "decreases", "lower", "reduce", "reduces"}

    env_outcome_beliefs: Dict[str, List[Tuple[str, str]]] = defaultdict(list)

    for bid, content in all_beliefs:
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
                        "provenance": f"safe_contradiction:{key}",
                    })
    return new_edges


def main() -> int:
    db_path = resolve_web_db(None, prefer="integrated")
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    print(f"Database: {db_path}")

    isolated = get_isolated_beliefs(conn)
    all_beliefs = get_all_beliefs(conn)
    print(f"Total beliefs: {len(all_beliefs)}")
    print(f"Isolated beliefs (before): {len(isolated)}")

    templates = load_templates()
    keyword_index = build_template_keyword_index(templates)
    print(f"Template keywords: {len(keyword_index)} from {len(templates)} templates")

    # Strategy 1: Template bridges (SAFE — all uncapped)
    print("\n--- Strategy 1: Template Keyword Bridge (SAFE, uncapped) ---")
    s1_edges = strategy_template_bridge(isolated, keyword_index, all_beliefs)
    print(f"  Edges to add: {len(s1_edges)}")

    # Strategy 3: Contradictions (SAFE — only explicit direction conflicts)
    print("\n--- Strategy 3: Contradiction Discovery (SAFE, explicit only) ---")
    s3_edges = strategy_contradiction_discovery(all_beliefs)
    print(f"  Contradictions found: {len(s3_edges)}")

    all_new = s1_edges + s3_edges
    print(f"\nTotal safe edges: {len(all_new)}")

    # Skip any already inserted in previous run
    existing = set()
    rows = conn.execute(
        "SELECT constraint_id FROM constraints WHERE web_id = ? AND provenance LIKE 'health_improve%' OR provenance LIKE 'safe_%'",
        (MASTER_WEB_ID,)
    ).fetchall()
    for r in rows:
        existing.add(r[0])

    added = 0
    skipped = 0
    for edge in all_new:
        cid = f"safe:{edge['source_id'][:35]}:{edge['target_id'][:35]}"
        if cid in existing:
            skipped += 1
            continue
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
            print(f"  Error: {e}")
    conn.commit()

    new_isolated = get_isolated_beliefs(conn)
    print(f"\nInserted {added} new constraints (skipped {skipped} duplicates)")
    print(f"Isolated beliefs BEFORE: {len(isolated)}")
    print(f"Isolated beliefs AFTER:  {len(new_isolated)}")
    print(f"Beliefs connected:       {len(isolated) - len(new_isolated)}")

    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
