#!/usr/bin/env python3
"""
Historical reprocess of Web relations + bridge warrants.

Actions:
1) Reclassify legacy constraints (`restored:legacy_*`) using current relation logic.
2) Backfill cross-paper constraints for beliefs sharing (environment_id, outcome_id).
3) Backfill bridge warrants from historical belief content.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.services.bridge_warrants import BridgeRegistry, detect_bridge_from_claim
from src.services.db_locator import resolve_article_finder_db, resolve_web_db

MASTER_WEB_ID = "master:web:accumulated"

CONTRADICT_MARKERS = [
    "failed to replicate",
    "fails to replicate",
    "no effect",
    "no significant",
    "not significant",
    "null effect",
    "contradict",
    "challenge",
    "inconsistent",
    "did not support",
    "not supported",
    "attenuated",
]

EXPLAIN_MARKERS = [
    "mechanism",
    "mediate",
    "mediated",
    "pathway",
    "explains",
    "refine",
    "elaborate",
    "nuance",
    "boundary condition",
    "moderator",
    "heterogeneity",
]

SUPPORT_MARKERS = [
    "support",
    "verify",
    "replicate",
    "consistent with",
    "convergent",
    "confirm",
    "validated",
    "robust",
]


@dataclass
class BeliefRow:
    belief_id: str
    content: str
    tags: List[str]
    environment_id: str
    outcome_id: str
    paper_id: str
    year: int


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Reprocess web relation diversity + bridges for historical data.")
    p.add_argument("--web-db", default=None, help="Path to web DB (auto-resolved if omitted)")
    p.add_argument("--af-db", default=None, help="Path to article_finder.db (auto-resolved if omitted)")
    p.add_argument(
        "--web-db-prefer",
        choices=("integrated", "latest"),
        default="integrated",
        help="Auto-resolution policy when --web-db is omitted",
    )
    p.add_argument("--neighbors", type=int, default=3, help="Prior beliefs to connect per belief for shared env/out")
    p.add_argument("--dry-run", action="store_true", help="Compute changes without writing")
    return p.parse_args()


def normalize(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def first_paper_id(raw: str) -> str:
    try:
        vals = json.loads(raw or "[]")
        if isinstance(vals, list) and vals:
            return str(vals[0])
    except Exception:
        pass
    return ""


def load_year_map(af_db: Path) -> Dict[str, int]:
    conn = sqlite3.connect(str(af_db))
    try:
        cur = conn.cursor()
        cur.execute("SELECT paper_id, year FROM papers WHERE paper_id IS NOT NULL")
        out: Dict[str, int] = {}
        for pid, year in cur.fetchall():
            if not pid:
                continue
            try:
                out[str(pid)] = int(year) if year is not None else 0
            except Exception:
                out[str(pid)] = 0
        return out
    finally:
        conn.close()


def make_constraint_id(source_id: str, target_id: str, ctype: str, provenance: str) -> str:
    raw = f"{source_id}|{target_id}|{ctype}|{provenance}"
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:20]
    return f"c:reproc:{digest}"


def classify_relation(content: str, tags: List[str], default_relation: str = "supports") -> Tuple[str, float, str]:
    t = normalize(content)
    effect_direction = ""
    claim_type = ""
    for tag in tags:
        if tag.startswith("effect_direction:"):
            effect_direction = tag.split(":", 1)[1]
        elif tag.startswith("claim_type:"):
            claim_type = tag.split(":", 1)[1]

    if effect_direction in {"negative", "null"}:
        if effect_direction == "negative":
            return ("contradicts", 0.62, "reprocess:negative_direction_effect")
        return ("contradicts", 0.62, "reprocess:null_or_negative_effect")
    if any(m in t for m in CONTRADICT_MARKERS):
        return ("contradicts", 0.65, "reprocess:challenge_or_failure")
    if any(m in t for m in EXPLAIN_MARKERS):
        return ("explains", 0.58, "reprocess:elaborate_or_refine")
    if claim_type in {"methodology", "sample"}:
        return ("explains", 0.45, "reprocess:method_or_sample_context")
    if any(m in t for m in SUPPORT_MARKERS):
        return ("supports", 0.52, "reprocess:verify_or_test")
    # Default is caller-controlled (legacy edges should stay conservative).
    if default_relation == "explains":
        return ("explains", 0.40, "reprocess:default_contextual")
    if default_relation == "contradicts":
        return ("contradicts", 0.40, "reprocess:default_preserve_contradiction")
    return ("supports", 0.40, "reprocess:default_preserve_support")


def temporal_adjust(
    relation_type: str,
    base_strength: float,
    source_year: int,
    target_year: int,
    base_provenance: str,
) -> Tuple[str, float, str]:
    if not source_year or not target_year:
        return relation_type, base_strength, base_provenance
    lag = source_year - target_year
    rel = relation_type
    strength = base_strength
    prov = base_provenance
    if rel == "supports" and lag >= 3:
        strength = min(0.85, strength + min(0.2, 0.03 * lag))
        prov = f"{prov}|temporal:consolidation_lag_{lag}"
    if rel == "contradicts" and 0 <= lag <= 2:
        strength = min(0.8, strength + 0.05)
        prov = f"{prov}|temporal:early_challenge_lag_{lag}"
    if rel == "explains" and lag >= 4:
        strength = min(0.8, strength + 0.08)
        prov = f"{prov}|temporal:maturation_lag_{lag}"
    return rel, strength, prov


def load_beliefs(conn: sqlite3.Connection, year_map: Dict[str, int]) -> List[BeliefRow]:
    rows = conn.execute(
        """
        SELECT belief_id, content, tags, environment_id, outcome_id, paper_ids
        FROM beliefs
        WHERE web_id = ?
          AND environment_id IS NOT NULL AND environment_id != ''
          AND outcome_id IS NOT NULL AND outcome_id != ''
        """,
        (MASTER_WEB_ID,),
    ).fetchall()

    beliefs: List[BeliefRow] = []
    for r in rows:
        paper_id = first_paper_id(r["paper_ids"] or "[]")
        try:
            tags = json.loads(r["tags"] or "[]")
            if not isinstance(tags, list):
                tags = []
        except Exception:
            tags = []
        beliefs.append(
            BeliefRow(
                belief_id=str(r["belief_id"]),
                content=str(r["content"] or ""),
                tags=[str(t) for t in tags],
                environment_id=str(r["environment_id"] or ""),
                outcome_id=str(r["outcome_id"] or ""),
                paper_id=paper_id,
                year=year_map.get(paper_id, 0),
            )
        )
    return beliefs


def main() -> int:
    args = parse_args()
    web_db = resolve_web_db(args.web_db, prefer=args.web_db_prefer)
    af_db = resolve_article_finder_db(args.af_db)
    now = datetime.now(timezone.utc).isoformat()

    year_map = load_year_map(af_db)
    conn = sqlite3.connect(str(web_db), timeout=60.0)
    conn.row_factory = sqlite3.Row

    try:
        beliefs = load_beliefs(conn, year_map)
        belief_by_id = {b.belief_id: b for b in beliefs}

        # Reclassify legacy constraints.
        legacy_rows = conn.execute(
            """
            SELECT constraint_id, source_id, target_id, constraint_type, strength, provenance
            FROM constraints
            WHERE web_id = ?
              AND provenance LIKE 'restored:legacy_%'
            """,
            (MASTER_WEB_ID,),
        ).fetchall()

        updates: List[Tuple[Any, ...]] = []
        reclass_counts: Dict[str, int] = defaultdict(int)
        for r in legacy_rows:
            source_id = str(r["source_id"])
            b = belief_by_id.get(source_id)
            if not b:
                continue
            old_type = str(r["constraint_type"])
            new_type, new_strength, new_prov = classify_relation(
                b.content,
                b.tags,
                default_relation=old_type,
            )
            if old_type != new_type:
                reclass_counts[f"{old_type}->{new_type}"] += 1
            updates.append(
                (
                    new_type,
                    float(new_strength),
                    new_prov,
                    "reprocessed_relation",
                    str(r["constraint_id"]),
                )
            )

        # Add cross-paper constraints.
        by_pair: Dict[Tuple[str, str], List[BeliefRow]] = defaultdict(list)
        for b in beliefs:
            by_pair[(b.environment_id, b.outcome_id)].append(b)

        existing_ids = {
            row[0]
            for row in conn.execute(
                "SELECT constraint_id FROM constraints WHERE web_id = ?",
                (MASTER_WEB_ID,),
            ).fetchall()
        }

        inserts: List[Tuple[Any, ...]] = []
        insert_type_counts: Dict[str, int] = defaultdict(int)
        neighbors = max(1, int(args.neighbors))
        for _, group in by_pair.items():
            group.sort(key=lambda b: (b.year, b.belief_id))
            for i, src in enumerate(group):
                rel_type, rel_strength, rel_prov = classify_relation(
                    src.content,
                    src.tags,
                    default_relation="explains",
                )
                start = max(0, i - neighbors)
                for j in range(start, i):
                    tgt = group[j]
                    adj_type, adj_strength, adj_prov = temporal_adjust(
                        rel_type, rel_strength, src.year, tgt.year, rel_prov
                    )
                    provenance = f"reprocess:shared_env_out|{adj_prov}"
                    cid = make_constraint_id(src.belief_id, tgt.belief_id, adj_type, provenance)
                    if cid in existing_ids:
                        continue
                    existing_ids.add(cid)
                    inserts.append(
                        (
                            cid,
                            MASTER_WEB_ID,
                            src.belief_id,
                            tgt.belief_id,
                            adj_type,
                            float(adj_strength),
                            0,
                            json.dumps([src.paper_id] if src.paper_id else []),
                            "reprocessed_cross_paper_relation",
                            provenance,
                            now,
                        )
                    )
                    insert_type_counts[adj_type] += 1

        # Build bridge additions from historical beliefs.
        bridge_registry = BridgeRegistry()
        bridge_keys = set()

        existing_bridge_rows = conn.execute(
            """
            SELECT source_domain, target_domain, bridge_type, source_beliefs
            FROM bridges
            WHERE web_id = ?
            """,
            (MASTER_WEB_ID,),
        ).fetchall()
        for row in existing_bridge_rows:
            try:
                src_beliefs = json.loads(row["source_beliefs"] or "[]")
            except Exception:
                src_beliefs = []
            first_src = src_beliefs[0] if src_beliefs else ""
            bridge_keys.add(
                (
                    str(row["source_domain"]),
                    str(row["target_domain"]),
                    str(row["bridge_type"]),
                    str(first_src),
                )
            )

        bridge_candidates = 0
        for b in beliefs:
            claim = {
                "claim_id": b.belief_id,
                "statement": b.content,
                "constructs": {
                    "outcomes": [{"id": b.outcome_id}],
                    "inputs": [{"id": b.environment_id}],
                },
            }
            br = detect_bridge_from_claim(claim, target_domain="architectural_perception")
            if not br:
                continue
            if not br.source_beliefs:
                br.source_beliefs = [b.belief_id]
            if b.belief_id not in br.target_beliefs:
                br.target_beliefs.append(b.belief_id)
            key = (br.source_domain, br.target_domain, br.bridge_type.value, b.belief_id)
            if key in bridge_keys:
                continue
            bridge_keys.add(key)
            bridge_registry.add(br)
            bridge_candidates += 1

        if args.dry_run:
            print(f"beliefs={len(beliefs)}")
            print(f"legacy_constraints={len(legacy_rows)}")
            print(f"legacy_updates={len(updates)}")
            print(f"reclass_counts={dict(reclass_counts)}")
            print(f"new_cross_paper_constraints={len(inserts)}")
            print(f"new_cross_paper_type_counts={dict(insert_type_counts)}")
            print(f"new_bridges={bridge_candidates}")
            return 0

        if updates:
            conn.executemany(
                """
                UPDATE constraints
                SET constraint_type = ?, strength = ?, provenance = ?, warrant_type = ?
                WHERE constraint_id = ?
                """,
                updates,
            )

        if inserts:
            conn.executemany(
                """
                INSERT OR REPLACE INTO constraints (
                    constraint_id, web_id, source_id, target_id, constraint_type,
                    strength, bidirectional, evidence_ids, warrant_type, provenance, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                inserts,
            )

        bridge_inserts: List[Tuple[Any, ...]] = []
        for bridge in bridge_registry.all():
            failure_record_json = None
            if getattr(bridge, "failure_record", None):
                try:
                    failure_record_json = json.dumps(bridge.failure_record.to_dict())
                except Exception:
                    failure_record_json = None
            created_at = now
            try:
                created_at = bridge.provenance.created_at.isoformat()
            except Exception:
                pass
            bridge_inserts.append(
                (
                    bridge.bridge_id,
                    MASTER_WEB_ID,
                    bridge.source_domain,
                    bridge.target_domain,
                    bridge.bridge_type.value,
                    bridge.warrant_statement,
                    bridge.assumed_mechanism,
                    float(bridge.confidence),
                    bridge.confidence_source.value,
                    bridge.status.value,
                    json.dumps(bridge.source_beliefs),
                    json.dumps(bridge.target_beliefs),
                    json.dumps(bridge.evidence_for),
                    json.dumps(bridge.evidence_against),
                    failure_record_json,
                    1 if bool(bridge.voi_flag) else 0,
                    created_at,
                    now,
                )
            )
        if bridge_inserts:
            conn.executemany(
                """
                INSERT OR REPLACE INTO bridges (
                    bridge_id, web_id, source_domain, target_domain, bridge_type,
                    warrant_statement, assumed_mechanism, confidence, confidence_source,
                    status, source_beliefs, target_beliefs, evidence_for, evidence_against,
                    failure_record, voi_flag, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                bridge_inserts,
            )

        conn.commit()

        # Summary
        constraint_counts = conn.execute(
            "SELECT constraint_type, COUNT(*) FROM constraints WHERE web_id = ? GROUP BY constraint_type ORDER BY COUNT(*) DESC",
            (MASTER_WEB_ID,),
        ).fetchall()
        bridge_count = conn.execute(
            "SELECT COUNT(*) FROM bridges WHERE web_id = ?",
            (MASTER_WEB_ID,),
        ).fetchone()[0]

        print(f"beliefs={len(beliefs)}")
        print(f"legacy_constraints={len(legacy_rows)}")
        print(f"legacy_updates={len(updates)}")
        print(f"reclass_counts={dict(reclass_counts)}")
        print(f"new_cross_paper_constraints={len(inserts)}")
        print(f"new_cross_paper_type_counts={dict(insert_type_counts)}")
        print(f"new_bridges={bridge_candidates}")
        print(f"constraint_type_counts={[(r[0], r[1]) for r in constraint_counts]}")
        print(f"bridge_count={bridge_count}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
