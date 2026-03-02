#!/usr/bin/env python3
"""
Backfill argument-structure constraints for existing Web beliefs.

Creates lightweight directed links based on:
- shared (environment_id, outcome_id)
- argument language in belief content
- temporal lag between source and target paper years
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
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.db_locator import resolve_article_finder_db, resolve_web_db

MASTER_WEB_ID = "master:web:accumulated"


@dataclass
class BeliefRow:
    belief_id: str
    content: str
    environment_id: str
    outcome_id: str
    paper_id: str
    year: int


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Backfill argument constraints into web_persistence.db")
    p.add_argument("--web-db", default=None, help="Path to web DB (auto-resolved if omitted)")
    p.add_argument(
        "--web-db-prefer",
        choices=("integrated", "latest"),
        default="integrated",
        help="Auto-resolution policy when --web-db is omitted",
    )
    p.add_argument("--af-db", default=None, help="Path to article_finder.db (auto-resolved if omitted)")
    p.add_argument("--neighbors", type=int, default=3, help="How many prior beliefs to link per belief")
    p.add_argument("--dry-run", action="store_true", help="Compute counts without writing")
    return p.parse_args()


def normalize(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def classify_argument_relation(text: str) -> Tuple[str, float, str]:
    t = normalize(text)
    contradict_markers = [
        "failed to replicate",
        "fails to replicate",
        "no effect",
        "no significant",
        "null effect",
        "contradict",
        "challenge",
        "inconsistent",
        "did not support",
        "not supported",
        "attenuated",
    ]
    explain_markers = [
        "mechanism",
        "mediat",
        "pathway",
        "explains",
        "refine",
        "elaborat",
        "nuance",
        "boundary condition",
        "moderator",
        "heterogeneity",
    ]
    support_markers = [
        "support",
        "verify",
        "replicat",
        "consistent with",
        "convergen",
        "confirm",
        "test",
        "validated",
        "robust",
    ]

    if any(m in t for m in contradict_markers):
        return ("contradicts", 0.65, "argument:challenge_or_failure")
    if any(m in t for m in explain_markers):
        return ("explains", 0.55, "argument:elaborate_or_refine")
    if any(m in t for m in support_markers):
        return ("supports", 0.50, "argument:verify_or_test")
    return ("supports", 0.35, "argument:default_convergent")


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
    strength = base_strength
    prov = base_provenance
    rel = relation_type

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


def make_constraint_id(source_id: str, target_id: str, ctype: str, provenance: str) -> str:
    raw = f"{source_id}|{target_id}|{ctype}|{provenance}"
    return f"c:arg:{hashlib.sha1(raw.encode('utf-8')).hexdigest()[:20]}"


def first_paper_id(raw: str) -> str:
    try:
        vals = json.loads(raw or "[]")
        if isinstance(vals, list) and vals:
            return str(vals[0])
    except Exception as e:
        import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")
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


def main() -> int:
    args = parse_args()
    web_db = resolve_web_db(args.web_db, prefer=args.web_db_prefer)
    af_db = resolve_article_finder_db(args.af_db)
    print(f"[backfill_argument_constraints] using af_db={af_db} web_db={web_db}")
    now = datetime.now(timezone.utc).isoformat()
    year_map = load_year_map(af_db)

    conn = sqlite3.connect(str(web_db))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT belief_id, content, environment_id, outcome_id, paper_ids
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
            beliefs.append(
                BeliefRow(
                    belief_id=str(r["belief_id"]),
                    content=str(r["content"] or ""),
                    environment_id=str(r["environment_id"] or ""),
                    outcome_id=str(r["outcome_id"] or ""),
                    paper_id=paper_id,
                    year=year_map.get(paper_id, 0),
                )
            )

        by_pair: Dict[Tuple[str, str], List[BeliefRow]] = defaultdict(list)
        for b in beliefs:
            by_pair[(b.environment_id, b.outcome_id)].append(b)

        existing = {
            r[0]
            for r in conn.execute(
                "SELECT constraint_id FROM constraints WHERE web_id = ?",
                (MASTER_WEB_ID,),
            ).fetchall()
        }

        to_insert: List[Tuple] = []
        neighbors = max(1, int(args.neighbors))
        for _, group in by_pair.items():
            group.sort(key=lambda b: (b.year, b.belief_id))
            for i, src in enumerate(group):
                start = max(0, i - neighbors)
                for j in range(start, i):
                    tgt = group[j]
                    rel_type, rel_strength, rel_prov = classify_argument_relation(src.content)
                    rel_type, rel_strength, rel_prov = temporal_adjust(
                        rel_type, rel_strength, src.year, tgt.year, rel_prov
                    )
                    cid = make_constraint_id(src.belief_id, tgt.belief_id, rel_type, rel_prov)
                    if cid in existing:
                        continue
                    existing.add(cid)
                    to_insert.append(
                        (
                            cid,
                            MASTER_WEB_ID,
                            src.belief_id,
                            tgt.belief_id,
                            rel_type,
                            float(rel_strength),
                            0,
                            json.dumps([src.paper_id] if src.paper_id else []),
                            "backfill_argument_relation",
                            rel_prov,
                            now,
                        )
                    )

        if args.dry_run:
            print(f"Beliefs loaded: {len(beliefs)}")
            print(f"Pairs: {len(by_pair)}")
            print(f"Would insert constraints: {len(to_insert)}")
            return 0

        conn.executemany(
            """
            INSERT OR REPLACE INTO constraints (
                constraint_id, web_id, source_id, target_id, constraint_type,
                strength, bidirectional, evidence_ids, warrant_type, provenance, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            to_insert,
        )
        conn.commit()

        total = conn.execute(
            "SELECT COUNT(*) FROM constraints WHERE web_id = ?",
            (MASTER_WEB_ID,),
        ).fetchone()[0]
        print(f"Inserted constraints: {len(to_insert)}")
        print(f"Total constraints: {total}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
