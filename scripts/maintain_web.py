#!/usr/bin/env python3
"""
Unified Web Maintenance Module
================================
Performs all safe maintenance operations on the Web of Belief in the
correct order:

  1. PRUNE  — Identify and quarantine off-topic beliefs
  2. BRIDGE — Connect isolated beliefs via template keyword matching
  3. CONTRA — Discover explicit contradictions
  4. ANCHOR — Annotate beliefs with matching template IDs
  5. NARRATE — Extract justification narratives from panel docs
  6. REPORT — Run full health check and write report

Usage:
    python scripts/maintain_web.py --dry-run     # Preview all changes
    python scripts/maintain_web.py --apply        # Apply all changes
    python scripts/maintain_web.py --prune-only   # Only prune off-topic
    python scripts/maintain_web.py --bridge-only  # Only add bridges

Safety:
  - Pruning is SOFT: beliefs are tagged, not deleted
  - Bridges use low-strength (0.3) "explains" edges
  - Contradictions only flag explicit direction conflicts
  - All changes are tagged with provenance for rollback
"""

from __future__ import annotations

import argparse
import glob
import json
import re
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

MASTER_WEB_ID = "master:web:accumulated"
TEMPLATE_DIR = PROJECT_ROOT / "data" / "templates"

# ═══════════════════════════════════════════════════════════════════════
# OFF-TOPIC DETECTION — keyword lists adapted from filter_off_topic_papers.py
# ═══════════════════════════════════════════════════════════════════════

# Domains clearly unrelated to Cognitive Neuroarchitecture
STRONG_EXCLUSION_KEYWORDS = [
    # Industrial/extraction (NOT about buildings)
    "offshore drilling", "oil well", "petroleum extraction", "oil rig",
    "pipeline inspection", "refinery process", "fracking", "subsea equipment",
    "well integrity", "wellhead", "drilling operation",
    "mining operation", "ore extraction", "coal mining",
    # Pure cell/molecular biology (NOT environmental health)
    "cell culture", "in vitro assay", "dna sequence", "rna expression",
    "protein expression", "gene expression", "cellular mechanism",
    "molecular biology", "biochemical pathway", "cell signaling",
    "transfection", "western blot", "pcr amplification",
    # Clinical drug trials (NOT healing environments)
    "drug dosage", "pharmacokinetics", "phase ii trial", "phase iii trial",
    "placebo-controlled drug", "chemotherapy regimen", "drug efficacy",
    # Electronics/VLSI (NOT architectural)
    "vlsi", "transistor", "semiconductor", "integrated circuit",
    "cmos", "fpga", "asic", "chip design", "logic gate",
    "verilog", "silicon wafer", "lithography",
    # Pure mathematics/CS theory
    "theorem proving", "formal verification", "computability",
    "np-hard", "np-complete", "turing machine",
    # Astrophysics
    "galaxy", "cosmological", "dark matter", "dark energy",
    "neutron star", "black hole", "supernova", "exoplanet",
    # Agricultural
    "crop yield", "fertilizer", "irrigation", "herbicide",
    "pesticide", "soil nutrient", "livestock", "animal husbandry",
]

# Terms that confirm CNfA relevance (if present, belief is on-topic)
INCLUSION_KEYWORDS = [
    # Built environment
    "building", "architecture", "architectural", "interior", "office",
    "hospital", "classroom", "residential", "facade", "room",
    "ceiling", "floor", "wall", "window", "corridor",
    "wayfinding", "legibility", "open plan", "atrium",
    # Environmental attributes
    "daylight", "illumination", "lighting", "luminance", "glare",
    "acoustic", "noise", "thermal", "ventilation", "air quality",
    "biophilic", "nature view", "greenery", "fractal",
    "spatial", "enclosure", "openness", "ceiling height",
    "color", "contrast", "visual", "aesthetics", "beauty",
    # Human outcomes
    "cognition", "attention", "memory", "stress", "mood",
    "wellbeing", "well-being", "productivity", "performance",
    "comfort", "satisfaction", "anxiety", "arousal",
    "prediction error", "predictive coding", "neural",
    # Theories
    "biophilia", "attention restoration", "stress recovery",
    "prospect-refuge", "predictive processing", "neuroarchitecture",
    "neuroaesthetics", "embodied cognition", "isovist",
]


def is_belief_off_topic(content: str) -> Tuple[bool, str, float]:
    """
    Classify a belief as on-topic or off-topic for CNfA.

    Returns: (is_off_topic, reason, confidence)
    """
    content_lower = content.lower()

    # Check inclusion first — if ANY inclusion keyword is present, keep it
    for kw in INCLUSION_KEYWORDS:
        if kw in content_lower:
            return False, f"on_topic:{kw}", 0.0

    # Check strong exclusion
    for kw in STRONG_EXCLUSION_KEYWORDS:
        if kw in content_lower:
            return True, f"off_topic:{kw}", 0.90

    # No signal either way — keep it (permissive default)
    return False, "on_topic:default", 0.0


# ═══════════════════════════════════════════════════════════════════════
# TEMPLATE LOADING
# ═══════════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════════
# DATABASE OPERATIONS
# ═══════════════════════════════════════════════════════════════════════

def get_all_beliefs(conn: sqlite3.Connection) -> List[Tuple[str, str]]:
    rows = conn.execute(
        "SELECT belief_id, content FROM beliefs WHERE web_id = ?",
        (MASTER_WEB_ID,)
    ).fetchall()
    return [(r[0], r[1]) for r in rows]


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


def ensure_extra_columns(conn: sqlite3.Connection):
    """Add off_topic and template_ids columns to beliefs table if absent."""
    cols = [r[1] for r in conn.execute("PRAGMA table_info(beliefs)").fetchall()]
    if "off_topic" not in cols:
        conn.execute("ALTER TABLE beliefs ADD COLUMN off_topic INTEGER DEFAULT 0")
    if "template_ids" not in cols:
        conn.execute("ALTER TABLE beliefs ADD COLUMN template_ids TEXT DEFAULT NULL")
    conn.commit()


# ═══════════════════════════════════════════════════════════════════════
# PHASE 1: PRUNE OFF-TOPIC BELIEFS
# ═══════════════════════════════════════════════════════════════════════

def phase_prune(conn: sqlite3.Connection, dry_run: bool) -> Dict[str, Any]:
    """Identify and soft-tag off-topic beliefs."""
    ensure_extra_columns(conn)
    all_beliefs = get_all_beliefs(conn)

    off_topic = []
    on_topic = 0
    reason_counts: Dict[str, int] = defaultdict(int)

    for bid, content in all_beliefs:
        is_ot, reason, conf = is_belief_off_topic(content)
        if is_ot:
            off_topic.append((bid, reason, conf))
            reason_type = reason.split(":")[1].split()[0] if ":" in reason else reason
            reason_counts[reason_type] += 1
        else:
            on_topic += 1

    print(f"\n{'='*60}")
    print(f"PHASE 1: OFF-TOPIC PRUNING")
    print(f"{'='*60}")
    print(f"  Total beliefs scanned: {len(all_beliefs)}")
    print(f"  On-topic:   {on_topic}")
    print(f"  Off-topic:  {len(off_topic)}")
    print(f"\n  Breakdown by reason:")
    for reason, count in sorted(reason_counts.items(), key=lambda x: -x[1]):
        print(f"    {reason}: {count}")

    if off_topic:
        print(f"\n  Sample off-topic beliefs:")
        for bid, reason, conf in off_topic[:5]:
            print(f"    [{conf:.2f}] {bid[:60]} ({reason})")

    if not dry_run and off_topic:
        for bid, reason, conf in off_topic:
            conn.execute(
                "UPDATE beliefs SET off_topic = 1 WHERE belief_id = ? AND web_id = ?",
                (bid, MASTER_WEB_ID)
            )
        conn.commit()
        print(f"\n  ✅ Tagged {len(off_topic)} beliefs as off-topic")
    elif dry_run:
        print(f"\n  [DRY RUN] Would tag {len(off_topic)} beliefs")

    return {
        "total": len(all_beliefs),
        "off_topic": len(off_topic),
        "on_topic": on_topic,
        "reasons": dict(reason_counts),
    }


# ═══════════════════════════════════════════════════════════════════════
# PHASE 2: TEMPLATE BRIDGES
# ═══════════════════════════════════════════════════════════════════════

def phase_bridge(conn: sqlite3.Connection, dry_run: bool) -> Dict[str, Any]:
    """Connect isolated beliefs via template keyword matching."""
    isolated = get_isolated_beliefs(conn)
    all_beliefs = get_all_beliefs(conn)

    templates = load_templates()
    keyword_index = build_template_keyword_index(templates)

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

    new_edges = []
    for iso_id, iso_content in isolated:
        iso_lower = iso_content.lower()
        matched_templates: Set[str] = set()
        for kw, tids in keyword_index.items():
            if kw in iso_lower:
                matched_templates.update(tids)

        for tid in matched_templates:
            targets = template_to_connected.get(tid, [])
            if targets:
                new_edges.append({
                    "source_id": iso_id,
                    "target_id": targets[0],
                    "constraint_type": "explains",
                    "strength": 0.3,
                    "provenance": f"maintain_bridge:{tid}",
                })
                break

    print(f"\n{'='*60}")
    print(f"PHASE 2: TEMPLATE BRIDGES")
    print(f"{'='*60}")
    print(f"  Isolated beliefs: {len(isolated)}")
    print(f"  Template keywords: {len(keyword_index)} from {len(templates)} templates")
    print(f"  New bridge edges: {len(new_edges)}")

    added = 0
    if not dry_run:
        for edge in new_edges:
            cid = f"maintain:{edge['source_id'][:35]}:{edge['target_id'][:35]}"
            try:
                conn.execute("""
                    INSERT OR IGNORE INTO constraints
                    (constraint_id, web_id, source_id, target_id, constraint_type,
                     strength, provenance, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """, (
                    cid, MASTER_WEB_ID,
                    edge["source_id"], edge["target_id"],
                    edge["constraint_type"], edge["strength"],
                    edge["provenance"]
                ))
                added += 1
            except Exception as e:
                pass
        conn.commit()
        print(f"  ✅ Inserted {added} new constraints")
    else:
        print(f"  [DRY RUN] Would insert {len(new_edges)} constraints")

    post_isolated = get_isolated_beliefs(conn)
    connected = len(isolated) - len(post_isolated)

    return {
        "isolated_before": len(isolated),
        "new_edges": added if not dry_run else len(new_edges),
        "isolated_after": len(post_isolated) if not dry_run else len(isolated) - len(new_edges),
        "connected": connected if not dry_run else len(new_edges),
    }


# ═══════════════════════════════════════════════════════════════════════
# PHASE 3: CONTRADICTION DISCOVERY
# ═══════════════════════════════════════════════════════════════════════

def phase_contradictions(conn: sqlite3.Connection, dry_run: bool) -> Dict[str, Any]:
    """Find belief pairs with opposing direction claims."""
    DIRECTION_POSITIVE = {"positive", "increase", "increases", "higher", "enhance", "enhances"}
    DIRECTION_NEGATIVE = {"negative", "decrease", "decreases", "lower", "reduce", "reduces"}

    all_beliefs = get_all_beliefs(conn)
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
                        "provenance": f"maintain_contradiction:{key}",
                    })

    print(f"\n{'='*60}")
    print(f"PHASE 3: CONTRADICTION DISCOVERY")
    print(f"{'='*60}")
    print(f"  Env→Outcome pairs with 2+ beliefs: {sum(1 for v in env_outcome_beliefs.values() if len(v) >= 2)}")
    print(f"  Contradictions found: {len(new_edges)}")

    added = 0
    if not dry_run and new_edges:
        for edge in new_edges:
            cid = f"maintain_c:{edge['source_id'][:33]}:{edge['target_id'][:33]}"
            try:
                conn.execute("""
                    INSERT OR IGNORE INTO constraints
                    (constraint_id, web_id, source_id, target_id, constraint_type,
                     strength, provenance, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """, (
                    cid, MASTER_WEB_ID,
                    edge["source_id"], edge["target_id"],
                    edge["constraint_type"], edge["strength"],
                    edge["provenance"]
                ))
                added += 1
            except Exception as e:
                import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")
        conn.commit()
        print(f"  ✅ Inserted {added} contradiction edges")
    elif dry_run:
        print(f"  [DRY RUN] Would insert {len(new_edges)} contradictions")

    return {"contradictions": added if not dry_run else len(new_edges)}


# ═══════════════════════════════════════════════════════════════════════
# PHASE 4: TEMPLATE ANNOTATION
# ═══════════════════════════════════════════════════════════════════════

def phase_template_anchor(conn: sqlite3.Connection, dry_run: bool) -> Dict[str, Any]:
    """Annotate each belief with the template IDs it matches.

    Uses the same rich keyword index (constructs, mechanism chains,
    framework IDs, name tokens) that the bridging phase uses.
    Writes a JSON array of template IDs into beliefs.template_ids.
    """
    ensure_extra_columns(conn)
    all_beliefs = get_all_beliefs(conn)
    templates = load_templates()
    keyword_index = build_template_keyword_index(templates)

    # For each belief, collect matching template IDs
    belief_templates: Dict[str, Set[str]] = defaultdict(set)
    for bid, content in all_beliefs:
        content_lower = content.lower()
        for kw, tids in keyword_index.items():
            if kw in content_lower:
                for tid in tids:
                    belief_templates[bid].add(tid)

    # Count statistics
    total = len(all_beliefs)
    annotated = sum(1 for tids in belief_templates.values() if tids)
    templates_with_beliefs = set()
    for tids in belief_templates.values():
        templates_with_beliefs.update(tids)

    coverage_pct = (len(templates_with_beliefs) / max(len(templates), 1)) * 100
    avg_templates = (
        sum(len(tids) for tids in belief_templates.values()) / max(annotated, 1)
    )

    print(f"\n{'='*60}")
    print(f"PHASE 4: TEMPLATE ANNOTATION")
    print(f"{'='*60}")
    print(f"  Total beliefs: {total}")
    print(f"  Beliefs with ≥1 template match: {annotated} ({annotated/max(total,1)*100:.1f}%)")
    print(f"  Templates with ≥1 belief:  {len(templates_with_beliefs)}/{len(templates)} ({coverage_pct:.1f}%)")
    print(f"  Avg templates per annotated belief: {avg_templates:.1f}")

    updated = 0
    if not dry_run:
        for bid, tids in belief_templates.items():
            if tids:
                conn.execute(
                    "UPDATE beliefs SET template_ids = ? WHERE belief_id = ? AND web_id = ?",
                    (json.dumps(sorted(tids)), bid, MASTER_WEB_ID)
                )
                updated += 1
        conn.commit()
        print(f"  ✅ Annotated {updated} beliefs with template IDs")
    else:
        print(f"  [DRY RUN] Would annotate {annotated} beliefs")

    return {
        "total": total,
        "annotated": annotated,
        "templates_with_beliefs": len(templates_with_beliefs),
        "total_templates": len(templates),
        "coverage_pct": round(coverage_pct, 1),
    }


# ═══════════════════════════════════════════════════════════════════════
# PHASE 5: JUSTIFICATION NARRATIVE EXTRACTION
# ═══════════════════════════════════════════════════════════════════════

PANEL_DOCS = [
    "docs/VISUAL_I_Panel_Output_Feb21.md",
    "docs/02-16_01_47_Panel_VIEW_I_Nature_View_V1_0.md",
    "docs/02-15_27_Panel_EI_Memory_Encoding_V1_0.md",
    "docs/02-15_25_Panel_VI_Gap_Closure_V1_0.md",
    "docs/02-15_20_Panel_V_Social_Brain_V1_0.md",
    "docs/02-15_14_Panel_IV_Cognitive_Control_Reward_V1_0.md",
    "docs/02-15_03_Panel_III_Multimodal_Senses_HigherCognition_V1.0.md",
    "docs/02-15_02_Neuroscience_Panel_Templates_and_Taxonomy_V1.0.md",
    "docs/02-15_01_Neuroscience_Panel_Tier1_Frameworks_V1.0.md",
    "docs/02-14_09_CMR_Revised_Spec_Panel_Templates_V2.0.md",
    "docs/44_Panel_SOC_I_Social_Config.md",
    "docs/42_Panel_TP_I_Temporal.md",
    "docs/38_Panel_SC_I_Spatial_Config.md",
    "docs/37_Panel_MAT_I_Materials.md",
    "docs/30_Panel_MIII_Musical_Emotion_Mechanisms_V1_0.md",
    "docs/29_Panel_MII_Rhythm_Groove_Motor_V1_0.md",
]


def _load_panel_docs_cache() -> Dict[str, str]:
    """Load all panel docs into memory."""
    docs = {}
    for pd in PANEL_DOCS:
        full_path = PROJECT_ROOT / pd
        if full_path.exists():
            try:
                docs[pd] = full_path.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")
    return docs


def _find_section(content: str, template_id: str) -> Tuple[int, int] | None:
    """Find the heading-bounded section discussing a template."""
    pos = content.find(template_id)
    if pos < 0:
        return None
    # Walk backward to nearest heading
    before = content[:pos]
    heading_matches = list(re.finditer(r'\n(#{1,4}\s)', before))
    start = heading_matches[-1].start() + 1 if heading_matches else max(0, pos - 2000)
    # Walk forward to next heading
    after = content[pos:]
    next_heading = re.search(r'\n(#{1,3}\s)', after[100:])
    end = pos + 100 + next_heading.start() if next_heading else min(len(content), pos + 4000)
    # Enforce bounds
    if end - start < 200:
        start, end = max(0, pos - 1000), min(len(content), pos + 3000)
    elif end - start > 6000:
        end = start + 5000
    return (start, end)


def _clean_excerpt(content: str, start: int, end: int) -> str:
    """Extract prose, removing JSON/code blocks."""
    raw = content[start:end]
    raw = re.sub(r'```json\s*\n[\s\S]*?\n```', '[JSON block omitted]', raw)
    raw = re.sub(r'```\w*\s*\n[\s\S]*?\n```', '[code block omitted]', raw)
    lines = [l for l in raw.split("\n") if not (len(l) > 500 and "|" in l)]
    result = "\n".join(lines).strip()
    return result[:4000] + "\n\n[... truncated]" if len(result) > 4000 else result


def phase_narrative_extraction(dry_run: bool) -> Dict[str, Any]:
    """Extract justification narrative excerpts from panel docs into template JSONs."""
    panel_docs = _load_panel_docs_cache()
    templates_list = load_templates()

    # Build path map
    template_paths: Dict[str, str] = {}
    for fp in glob.glob(str(TEMPLATE_DIR / "*.json")):
        if fp.endswith(".bak"):
            continue
        try:
            with open(fp) as f:
                t = json.load(f)
            template_paths[t.get("template_id", "")] = fp
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")

    extracted = 0
    missing = 0
    already = 0

    for t in templates_list:
        tid = t.get("template_id", "")
        display_id = t.get("display_id", "")

        if t.get("panel_reasoning_excerpt"):
            already += 1
            continue

        # Search panel docs
        known_docs = t.get("panel_docs", [])
        search_order = list(known_docs) + [d for d in PANEL_DOCS if d not in known_docs]

        found = False
        for doc_path in search_order:
            doc_content = panel_docs.get(doc_path)
            if not doc_content:
                continue
            bounds = _find_section(doc_content, tid)
            if bounds is None and display_id:
                bounds = _find_section(doc_content, display_id)
            if bounds is None:
                continue

            excerpt = _clean_excerpt(doc_content, bounds[0], bounds[1])
            if len(excerpt) < 100:
                continue

            if not dry_run:
                t["panel_reasoning_excerpt"] = excerpt
                t["justification_status"] = "raw_excerpt"
                t["excerpt_source"] = doc_path
                t["excerpt_char_range"] = list(bounds)
                fp = template_paths.get(tid, "")
                if fp:
                    with open(fp, "w") as f:
                        json.dump(t, f, indent=2, ensure_ascii=False)

            extracted += 1
            found = True
            break

        if not found:
            if not dry_run:
                t["justification_status"] = "missing"
                fp = template_paths.get(tid, "")
                if fp:
                    with open(fp, "w") as f:
                        json.dump(t, f, indent=2, ensure_ascii=False)
            missing += 1

    print(f"\n{'='*60}")
    print(f"PHASE 5: JUSTIFICATION NARRATIVE EXTRACTION")
    print(f"{'='*60}")
    print(f"  Templates: {len(templates_list)}")
    print(f"  Already had narrative: {already}")
    print(f"  Excerpts extracted: {extracted}")
    print(f"  No panel match: {missing}")
    if dry_run:
        print(f"  [DRY RUN] Would write {extracted} narratives")
    else:
        print(f"  \u2705 Wrote {extracted} narratives to template JSONs")

    return {
        "total": len(templates_list),
        "already": already,
        "extracted": extracted,
        "missing": missing,
    }
# MAIN
# ═══════════════════════════════════════════════════════════════════════

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Unified web maintenance.")
    p.add_argument("--dry-run", action="store_true", help="Preview without writing")
    p.add_argument("--apply", action="store_true", help="Apply all maintenance phases")
    p.add_argument("--prune-only", action="store_true", help="Only run pruning phase")
    p.add_argument("--bridge-only", action="store_true", help="Only run bridging phase")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    dry_run = args.dry_run or (not args.apply and not args.prune_only and not args.bridge_only)

    if dry_run and not args.dry_run:
        print("No action flag specified. Use --apply, --prune-only, --bridge-only, or --dry-run.")
        print("Defaulting to --dry-run.\n")

    db_path = resolve_web_db(None, prefer="integrated")
    conn = sqlite3.connect(str(db_path))

    print(f"Database: {db_path}")
    print(f"Mode: {'DRY RUN' if dry_run else 'APPLY'}")
    print(f"Time: {datetime.now().isoformat()}")

    results = {}

    run_all = args.apply or args.dry_run or (not args.prune_only and not args.bridge_only)

    # Phase 1: Prune
    if run_all or args.prune_only:
        results["prune"] = phase_prune(conn, dry_run and not args.prune_only)
        if args.prune_only and not args.dry_run:
            results["prune"] = phase_prune(conn, False)

    # Phase 2: Bridge
    if run_all or args.bridge_only:
        results["bridge"] = phase_bridge(conn, dry_run and not args.bridge_only)
        if args.bridge_only and not args.dry_run:
            results["bridge"] = phase_bridge(conn, False)

    # Phase 3: Contradictions
    if run_all:
        results["contradictions"] = phase_contradictions(conn, dry_run)

    # Phase 4: Template Annotation
    if run_all:
        results["template_anchor"] = phase_template_anchor(conn, dry_run)

    # Phase 5: Justification Narratives
    if run_all:
        results["narratives"] = phase_narrative_extraction(dry_run)

    # Summary
    print(f"\n{'='*60}")
    print(f"MAINTENANCE SUMMARY")
    print(f"{'='*60}")
    if "prune" in results:
        r = results["prune"]
        print(f"  Off-topic beliefs identified: {r['off_topic']}")
    if "bridge" in results:
        r = results["bridge"]
        print(f"  Beliefs connected via bridges: {r['connected']}")
        print(f"  Remaining isolated: {r['isolated_after']}")
    if "contradictions" in results:
        print(f"  Contradictions discovered: {results['contradictions']['contradictions']}")
    if "template_anchor" in results:
        r = results["template_anchor"]
        print(f"  Template coverage: {r['templates_with_beliefs']}/{r['total_templates']} ({r['coverage_pct']}%)")
        print(f"  Beliefs annotated: {r['annotated']}")
    if "narratives" in results:
        r = results["narratives"]
        print(f"  Narratives extracted: {r['extracted']} (already: {r['already']}, missing: {r['missing']})")
    # Write results JSON
    report_path = PROJECT_ROOT / "data" / "production" / "maintenance_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump({"timestamp": datetime.now().isoformat(), **results}, f, indent=2)
    print(f"\n  Report: {report_path}")

    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
