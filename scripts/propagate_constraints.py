#!/usr/bin/env python3
"""
Constraint Propagation Script — connects isolated beliefs in the Web of Belief.

Run:  python3 scripts/propagate_constraints.py [--dry-run] [--db PATH]

Logic:
  1. Loads the web from the DB
  2. Identifies beliefs with no constraints (isolated)
  3. For each isolated belief, finds other beliefs that share:
     a) Same template match (from finding_template_theory_links.json)
     b) Same environment_id or outcome_id (from extraction data)
  4. Creates 'supports' constraints between them
  5. Saves the web back to the DB

Expected impact: reduces isolated% from ~25% to <15%, boosting web_bn subscore.
"""
import argparse
import json
import logging
import sqlite3
import sys
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def load_similarity_data():
    """Load all similarity data from the theory links file.
    
    Returns: (belief_templates, belief_env, belief_out)
        - belief_templates: belief_id → set of template IDs
        - belief_env: belief_id → environment_id
        - belief_out: belief_id → outcome_id
    """
    links_path = PROJECT_ROOT / "data" / "production" / "finding_template_theory_links.json"
    if not links_path.exists():
        logger.warning("No theory links file found at %s", links_path)
        return {}, {}, {}

    links = json.loads(links_path.read_text(errors="replace"))
    
    belief_templates = {}
    belief_env = {}
    belief_out = {}
    
    for res in links.get("resolutions", []):
        bid = res.get("belief_id", "")
        if not bid:
            continue
        
        # Templates: field is "top_templates" (list of dicts with "template_id")
        top_tpl = res.get("top_templates", [])
        if isinstance(top_tpl, list):
            tpl_ids = set()
            for t in top_tpl:
                if isinstance(t, dict):
                    tpl_ids.add(t.get("template_id", ""))
                elif isinstance(t, str):
                    tpl_ids.add(t)
            tpl_ids.discard("")
            if tpl_ids:
                belief_templates[bid] = tpl_ids
        
        # Also use tier2_relevance keys as template family proxies
        tier2 = res.get("tier2_relevance", {})
        if tier2 and bid not in belief_templates:
            belief_templates[bid] = set(tier2.keys())
        elif tier2:
            belief_templates[bid].update(tier2.keys())
        
        # Environment and outcome IDs are directly in the resolution
        env_id = res.get("environment_id", "")
        out_id = res.get("outcome_id", "")
        if env_id:
            belief_env[bid] = env_id
        if out_id:
            belief_out[bid] = out_id
    
    return belief_templates, belief_env, belief_out


def get_db_path(explicit=None):
    """Find the web DB using centralized resolver."""
    if explicit:
        p = Path(explicit)
        if p.exists():
            return p
        raise FileNotFoundError(f"Specified DB not found: {explicit}")
    
    try:
        from src.services.db_locator import resolve_web_db
        return resolve_web_db(prefer="integrated")
    except Exception:
        # Fallback: check known locations (v2 first)
        for c in [
            PROJECT_ROOT / "data" / "web_persistence_v2.db",
            PROJECT_ROOT / "data" / "web_persistence.db",
        ]:
            if c.exists():
                return c
        raise FileNotFoundError("No web DB found")


def load_web_beliefs_and_constraints(db_path):
    """Load belief IDs and existing constraints from the DB."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    
    # Get web_id from metadata
    row = conn.execute("SELECT web_id FROM web_metadata LIMIT 1").fetchone()
    web_id = row["web_id"] if row else "master"
    
    # Get all belief IDs
    cursor = conn.execute("SELECT belief_id FROM beliefs")
    all_beliefs = {row["belief_id"] for row in cursor.fetchall()}
    
    # Get all existing constraints (column is constraint_type, not type)
    cursor = conn.execute(
        "SELECT constraint_id, source_id, target_id, constraint_type, strength FROM constraints"
    )
    existing = {}
    connected_beliefs = set()
    for row in cursor.fetchall():
        cid = row["constraint_id"]
        existing[cid] = {
            "source_id": row["source_id"],
            "target_id": row["target_id"],
            "constraint_type": row["constraint_type"],
            "strength": row["strength"],
        }
        connected_beliefs.add(row["source_id"])
        connected_beliefs.add(row["target_id"])
    
    isolated = all_beliefs - connected_beliefs
    
    conn.close()
    return all_beliefs, existing, isolated, connected_beliefs, web_id


def build_similarity_index(belief_templates, belief_env, belief_out):
    """Build reverse indexes for efficient similarity matching."""
    # template → set of belief_ids
    template_to_beliefs = defaultdict(set)
    for bid, templates in belief_templates.items():
        for t in templates:
            template_to_beliefs[t].add(bid)
    
    # environment → set of belief_ids
    env_to_beliefs = defaultdict(set)
    for bid, env in belief_env.items():
        env_to_beliefs[env].add(bid)
    
    # outcome → set of belief_ids 
    out_to_beliefs = defaultdict(set)
    for bid, out in belief_out.items():
        out_to_beliefs[out].add(bid)
    
    return template_to_beliefs, env_to_beliefs, out_to_beliefs


def find_connections_for_isolated(
    isolated_belief,
    belief_templates,
    template_to_beliefs,
    env_to_beliefs,
    out_to_beliefs,
    belief_env,
    belief_out,
    connected_beliefs,
    max_connections=3,
):
    """Find the best connections for an isolated belief."""
    candidates = defaultdict(float)  # target_id → score
    
    # Strategy 1: Same template (strongest signal)
    templates = belief_templates.get(isolated_belief, set())
    for t in templates:
        for peer in template_to_beliefs.get(t, set()):
            if peer != isolated_belief and peer in connected_beliefs:
                candidates[peer] += 0.6
    
    # Strategy 2: Same environment_id 
    env = belief_env.get(isolated_belief)
    if env:
        for peer in env_to_beliefs.get(env, set()):
            if peer != isolated_belief and peer in connected_beliefs:
                candidates[peer] += 0.3
    
    # Strategy 3: Same outcome_id
    out = belief_out.get(isolated_belief)
    if out:
        for peer in out_to_beliefs.get(out, set()):
            if peer != isolated_belief and peer in connected_beliefs:
                candidates[peer] += 0.3
    
    # Sort by score, take top N
    sorted_candidates = sorted(candidates.items(), key=lambda x: -x[1])
    return sorted_candidates[:max_connections]


def propagate_constraints(db_path, dry_run=False, max_per_belief=3):
    """Main constraint propagation logic."""
    logger.info("Loading web from %s", db_path)
    all_beliefs, existing_constraints, isolated, connected, web_id = load_web_beliefs_and_constraints(db_path)
    
    logger.info(
        "Web state: %d beliefs, %d constraints, %d isolated (%.1f%%), web_id=%s",
        len(all_beliefs), len(existing_constraints), len(isolated),
        100 * len(isolated) / len(all_beliefs) if all_beliefs else 0,
        web_id,
    )
    
    if not isolated:
        logger.info("No isolated beliefs — nothing to do!")
        return
    
    # Load similarity data (all from theory links file)
    belief_templates, belief_env, belief_out = load_similarity_data()
    template_to_beliefs, env_to_beliefs, out_to_beliefs = build_similarity_index(
        belief_templates, belief_env, belief_out
    )
    
    logger.info(
        "Similarity data: %d beliefs with templates, %d with env, %d with outcome",
        len(belief_templates), len(belief_env), len(belief_out),
    )
    
    # Find connections for each isolated belief
    new_constraints = []
    connected_count = 0
    now = datetime.now(timezone.utc).isoformat()
    
    for iso_belief in sorted(isolated):
        connections = find_connections_for_isolated(
            iso_belief, belief_templates, template_to_beliefs,
            env_to_beliefs, out_to_beliefs, belief_env, belief_out,
            connected, max_connections=max_per_belief,
        )
        
        if connections:
            connected_count += 1
            for target_id, score in connections:
                cid = f"auto:{uuid.uuid4().hex[:12]}"
                strength = min(0.4, score * 0.5)  # Conservative strength
                new_constraints.append({
                    "constraint_id": cid,
                    "web_id": web_id,
                    "source_id": iso_belief,
                    "target_id": target_id,
                    "constraint_type": "supports",
                    "strength": round(strength, 3),
                    "bidirectional": 1,
                    "evidence_ids": "[]",
                    "created_at": now,
                })
    
    logger.info(
        "Found connections for %d/%d isolated beliefs → %d new constraints",
        connected_count, len(isolated), len(new_constraints),
    )
    
    if dry_run:
        logger.info("[DRY RUN] Would insert %d constraints. Sample:", len(new_constraints))
        for c in new_constraints[:5]:
            logger.info("  %s → %s (strength=%.3f)", c["source_id"][:40], c["target_id"][:40], c["strength"])
        return
    
    # Insert into DB
    conn = sqlite3.connect(str(db_path))
    inserted = 0
    try:
        for c in new_constraints:
            try:
                conn.execute(
                    """INSERT OR IGNORE INTO constraints 
                       (constraint_id, web_id, source_id, target_id, constraint_type,
                        strength, bidirectional, evidence_ids, created_at) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (c["constraint_id"], c["web_id"], c["source_id"], c["target_id"],
                     c["constraint_type"], c["strength"], c["bidirectional"],
                     c["evidence_ids"], c["created_at"]),
                )
                inserted += 1
            except sqlite3.Error as e:
                logger.warning("Failed to insert %s: %s", c["constraint_id"], e)
        
        conn.commit()
        logger.info("Inserted %d new constraints", inserted)
    finally:
        conn.close()
    
    # Re-check isolation
    _, _, new_isolated, _, _ = load_web_beliefs_and_constraints(db_path)
    logger.info(
        "After propagation: %d isolated (%.1f%%) — was %d (%.1f%%)",
        len(new_isolated), 100 * len(new_isolated) / len(all_beliefs),
        len(isolated), 100 * len(isolated) / len(all_beliefs),
    )


def main():
    parser = argparse.ArgumentParser(description="Propagate constraints to connect isolated beliefs")
    parser.add_argument("--db", type=str, help="Path to web DB (auto-detected if not specified)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without writing")
    parser.add_argument("--max-per-belief", type=int, default=3, help="Max constraints per isolated belief")
    args = parser.parse_args()
    
    db_path = get_db_path(args.db)
    propagate_constraints(db_path, dry_run=args.dry_run, max_per_belief=args.max_per_belief)


if __name__ == "__main__":
    main()
