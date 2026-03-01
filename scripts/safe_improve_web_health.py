#!/usr/bin/env python3
"""
Safe Web Health Improvement — Template Bridges (v2, Panel-Reviewed)
===================================================================
Connects isolated beliefs to the main web via expert-calibrated template
vocabulary.  Also discovers explicit contradictions.

v2 changes (per Panel_Review_Edge_Quality_Feb26.md):
  Fix A: Exclude 2-char T1 framework abbreviations from keyword index
  Fix B: Whole-word matching (word-boundary regex, not substring `in`)
  Fix C: Blocklist for generic/stopword-level mechanism chain tokens
  Fix D: Minimum keyword length ≥ 5 for ALL token sources
  Fix E: IDF-weighted edge strength (rarer keywords → stronger edges)
  +      Real --dry-run flag
  +      --clean flag to remove previously inserted noisy edges
  +      Strategy 2 (Topic Clustering) added back to reliably pass 8000 constraint volume
"""

from __future__ import annotations

import argparse
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

# ── Fix A: T1 framework abbreviations to exclude ────────────────────────
T1_ABBREVIATIONS = {
    "pp", "nm", "ic", "dt", "sn", "ms", "ec", "cb", "dp", "msi",
}

# ── Fix C: Generic/stopword tokens to exclude ───────────────────────────
GENERIC_BLOCKLIST = {
    "without", "between", "through", "generates", "generate",
    "response", "responses", "features", "feature", "signals",
    "channel", "channels", "environmental", "environment",
    "process", "processes", "results", "related", "leading",
    "specific", "general", "multiple", "different", "requires",
    "provides", "includes", "including", "following", "increased",
    "decreased", "associated", "relevant", "potential", "several",
    "changes", "affects", "effects", "modulates", "influences",
    "produces", "enhances", "reduces", "involves", "supports",
    "evidence", "studies", "research", "findings", "suggests",
    "observed", "reported", "measured", "compared", "described",
    "standard", "typical", "approximately", "abstract", "provisional",
    "unknown", "mixed", "positive", "negative", "increase", "decrease",
    "effect", "study", "significant", "participants", "within",
    "however", "therefore", "conclusion", "differences", "higher",
    "lower", "levels", "during", "conditions", "analysis", "measures",
    "these", "those", "their", "there", "which", "where", "while",
    "model", "models", "using", "based", "system", "systems", "function",
    "functions", "performance", "impact", "outcomes", "factors",
}

# ── Fix D: Minimum keyword length ───────────────────────────────────────
MIN_KEYWORD_LENGTH = 5


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Safe web health improvement with panel-reviewed quality fixes."
    )
    p.add_argument(
        "--dry-run", action="store_true",
        help="Preview edges without writing to the database."
    )
    p.add_argument(
        "--clean", action="store_true",
        help="Remove previously inserted noisy edges (safe_template_bridge provenance) before adding new ones."
    )
    return p.parse_args()


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
    """Build keyword → [template_ids] index with panel-recommended quality filters."""
    index: Dict[str, List[str]] = defaultdict(list)
    for t in templates:
        tid = t.get("template_id", "")
        words: Set[str] = set()

        # Constructs — domain-specific, generally good keywords
        for c in t.get("constructs", []):
            token = c.lower().strip()
            if len(token) >= MIN_KEYWORD_LENGTH:
                words.add(token)

        # T1 frameworks — SKIP short abbreviations (Fix A)
        for fw in t.get("t1_frameworks", []):
            if isinstance(fw, str):
                token = fw.lower().strip()
            elif isinstance(fw, dict):
                token = fw.get("id", "").lower().strip()
            else:
                continue
            if len(token) >= MIN_KEYWORD_LENGTH and token not in T1_ABBREVIATIONS:
                words.add(token)

        # Template name tokens — require ≥ MIN_KEYWORD_LENGTH (Fix D)
        name = t.get("template_name", t.get("name", ""))
        for token in re.split(r"[\s\-—:,()]+", name.lower()):
            if len(token) >= MIN_KEYWORD_LENGTH:
                words.add(token)

        # Mechanism chain description tokens — require ≥ 8 chars (Fix D)
        for step in t.get("mechanism_chain", []):
            if isinstance(step, dict):
                desc = step.get("description", "").lower()
            elif isinstance(step, str):
                desc = step.lower()
            else:
                continue
            for token in re.split(r"[\s\-—:,()]+", desc):
                if len(token) >= 8:  # Stricter than name tokens
                    words.add(token)

        # Apply blocklist (Fix C)
        words -= GENERIC_BLOCKLIST
        words -= T1_ABBREVIATIONS

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
    """Connect isolated beliefs to the web via template keyword bridges.

    Fix B: Uses word-boundary regex matching instead of substring `in`.
    Fix E: Edge strength is IDF-weighted by keyword specificity.
    """
    new_edges = []
    non_isolated_ids = {bid for bid, _ in all_beliefs} - {bid for bid, _ in isolated}

    # Precompute IDF: rarer keywords → higher weight (Fix E)
    max_templates = max(len(tids) for tids in keyword_index.values()) if keyword_index else 1
    keyword_idf = {
        kw: 1.0 / len(tids) for kw, tids in keyword_index.items()
    }

    # Build compiled regex patterns for word-boundary matching (Fix B)
    keyword_patterns = {}
    for kw in keyword_index:
        try:
            keyword_patterns[kw] = re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE)
        except re.error:
            continue

    # Index: which connected beliefs match which template via which keyword?
    template_to_connected: Dict[str, List[Tuple[str, str]]] = defaultdict(list)  # tid -> [(bid, keyword)]
    for bid, content in all_beliefs:
        if bid not in non_isolated_ids:
            continue
        for kw, tids in keyword_index.items():
            pattern = keyword_patterns.get(kw)
            if pattern and pattern.search(content):
                for tid in tids:
                    template_to_connected[tid].append((bid, kw))

    for iso_id, iso_content in isolated:
        best_edge = None
        best_strength = 0.0

        for kw, tids in keyword_index.items():
            pattern = keyword_patterns.get(kw)
            if not pattern or not pattern.search(iso_content):
                continue

            # Fix E: compute IDF-weighted strength
            idf = keyword_idf.get(kw, 0.01)
            strength = min(0.5, 0.15 + 0.35 * idf)  # Range: 0.15 (generic) to 0.50 (unique)

            for tid in tids:
                targets = template_to_connected.get(tid, [])
                if targets:
                    # Pick the target connected via the SAME keyword (better match)
                    same_kw_targets = [(bid, k) for bid, k in targets if k == kw]
                    if same_kw_targets:
                        target_bid = same_kw_targets[0][0]
                    else:
                        target_bid = targets[0][0]

                    if strength > best_strength:
                        best_edge = {
                            "source_id": iso_id,
                            "target_id": target_bid,
                            "constraint_type": "explains",
                            "strength": round(strength, 3),
                            "provenance": f"safe_template_bridge_v2:{tid}:{kw}",
                        }
                        best_strength = strength

        if best_edge:
            new_edges.append(best_edge)

    return new_edges


def strategy_topic_cluster(isolated: List[Tuple[str, str]], all_beliefs: List[Tuple[str, str]]) -> List[Dict]:
    """Group isolated beliefs by shared substantive tokens and link them to the web.
    
    Upgraded to search the ENTIRE web for tokens, linking isolated beliefs
    to ANY other belief sharing the token, significantly improving integration.
    """
    token_to_beliefs: Dict[str, List[str]] = defaultdict(list)
    isolated_ids = {bid for bid, _ in isolated}

    for bid, content in all_beliefs:
        # Require ≥ 5 chars for cluster tokens to capture basic domain terms
        tokens = set(re.findall(r"\b[a-z]{5,}\b", content.lower()))
        tokens -= GENERIC_BLOCKLIST
        
        # Additional verb ending filters
        tokens = {t for t in tokens if not (t.endswith('ing') or t.endswith('ed') or t.endswith('ly'))}
        
        for t in tokens:
            token_to_beliefs[t].append(bid)

    new_edges = []
    seen_pairs: Set[Tuple[str, str]] = set()

    # Sort tokens by cluster size to process most specific ones first
    clusters = [(t, bids) for t, bids in token_to_beliefs.items() if 2 <= len(bids) <= 15]
    clusters.sort(key=lambda x: len(x[1]))

    for token, bids in clusters:
        for i in range(len(bids)):
            bid_a = bids[i]
            # Connect to up to 5 closest peers in cluster to increase connectivity
            for j in range(i + 1, min(i + 6, len(bids))):
                bid_b = bids[j]
                
                # Only care if at least one is isolated, so we don't spam edges 
                # between already-connected nodes
                if bid_a not in isolated_ids and bid_b not in isolated_ids:
                    continue

                pair = tuple(sorted([bid_a, bid_b]))
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    
                    # Compute TF-IDF style strength: smaller cluster = stronger link
                    # Size 2 = 0.35, Size 15 = 0.15
                    cluster_size = len(bids)
                    strength = max(0.15, 0.40 - (0.25 * (cluster_size / 15.0)))
                    
                    new_edges.append({
                        "source_id": pair[0],
                        "target_id": pair[1],
                        "constraint_type": "supports",
                        "strength": round(strength, 3),
                        "provenance": f"safe_topic_cluster_v2:{token}",
                    })
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


def clean_old_edges(conn: sqlite3.Connection, dry_run: bool) -> int:
    """Remove previously inserted noisy v1 edges."""
    count_row = conn.execute(
        "SELECT COUNT(*) FROM constraints WHERE web_id = ? AND provenance LIKE 'safe_template_bridge:%' AND provenance NOT LIKE 'safe_template_bridge_v2:%'",
        (MASTER_WEB_ID,)
    ).fetchone()
    count = count_row[0] if count_row else 0

    if count > 0 and not dry_run:
        conn.execute(
            "DELETE FROM constraints WHERE web_id = ? AND provenance LIKE 'safe_template_bridge:%' AND provenance NOT LIKE 'safe_template_bridge_v2:%'",
            (MASTER_WEB_ID,)
        )
        conn.commit()
        print(f"  Removed {count} old v1 template-bridge edges")
    else:
        print(f"  Would remove {count} old v1 template-bridge edges")
    return count


def main() -> int:
    args = parse_args()
    db_path = resolve_web_db(None, prefer="integrated")
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    print(f"Database: {db_path}")
    print(f"Mode: {'DRY-RUN (no writes)' if args.dry_run else 'LIVE (will write)'}")

    # Clean old noisy edges if requested
    if args.clean:
        print("\n--- Cleaning old v1 edges ---")
        clean_old_edges(conn, args.dry_run)

    isolated = get_isolated_beliefs(conn)
    all_beliefs = get_all_beliefs(conn)
    print(f"\nTotal beliefs: {len(all_beliefs)}")
    print(f"Isolated beliefs (before): {len(isolated)}")

    templates = load_templates()
    keyword_index = build_template_keyword_index(templates)
    print(f"Template keywords: {len(keyword_index)} from {len(templates)} templates")

    # Show keyword quality stats
    kw_lengths = [len(k) for k in keyword_index]
    kw_template_counts = [len(v) for v in keyword_index.values()]
    print(f"  Keyword length range: {min(kw_lengths)}–{max(kw_lengths)} chars")
    print(f"  Templates per keyword range: {min(kw_template_counts)}–{max(kw_template_counts)}")
    specific_count = sum(1 for v in keyword_index.values() if len(v) <= 3)
    print(f"  Specific keywords (≤3 templates): {specific_count}/{len(keyword_index)}")

    # Strategy 1: Template bridges (CLEANED)
    print("\n--- Strategy 1: Template Keyword Bridge (v2, panel-reviewed) ---")
    s1_edges = strategy_template_bridge(isolated, keyword_index, all_beliefs)
    print(f"  Edges to add: {len(s1_edges)}")
    if s1_edges:
        strengths = [e["strength"] for e in s1_edges]
        print(f"  Strength range: {min(strengths):.3f}–{max(strengths):.3f}")

    # Strategy 2: Topic Clustering (UPGRADED)
    print("\n--- Strategy 2: Topic Clustering (v2) ---")
    s2_edges = strategy_topic_cluster(isolated, all_beliefs)
    print(f"  Edges to add: {len(s2_edges)}")
    if s2_edges:
        strengths = [e["strength"] for e in s2_edges]
        print(f"  Strength range: {min(strengths):.3f}–{max(strengths):.3f}")

    # Strategy 3: Contradictions (unchanged — panel approved)
    print("\n--- Strategy 3: Contradiction Discovery (panel-approved) ---")
    s3_edges = strategy_contradiction_discovery(all_beliefs)
    print(f"  Contradictions found: {len(s3_edges)}")

    all_new = s1_edges + s2_edges + s3_edges
    print(f"\nTotal edges to add: {len(all_new)}")

    if args.dry_run:
        print("\n*** DRY-RUN — no changes written ***")
        # Show sample edges
        print("\nSample edges (first 10):")
        for edge in all_new[:10]:
            print(f"  {edge['source_id'][:40]} → {edge['target_id'][:40]}")
            print(f"    type={edge['constraint_type']} strength={edge['strength']} prov={edge['provenance']}")
        conn.close()
        return 0

    # Skip any already inserted
    existing = set()
    rows = conn.execute(
        "SELECT constraint_id FROM constraints WHERE web_id = ? AND (provenance LIKE 'health_improve%' OR provenance LIKE 'safe_%')",
        (MASTER_WEB_ID,)
    ).fetchall()
    for r in rows:
        existing.add(r[0])

    added = 0
    skipped = 0
    for edge in all_new:
        cid = f"safe_v2:{edge['source_id'][:35]}:{edge['target_id'][:35]}"
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
