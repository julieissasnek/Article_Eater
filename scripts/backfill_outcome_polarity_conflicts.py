#!/usr/bin/env python3
"""
Backfill contradiction constraints from strict outcome-polarity conflicts.

Rule:
- Source belief has negative/null direction
- Target belief has positive direction
- Both share the exact same outcome_id
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.db_locator import resolve_web_db

MASTER_WEB_ID = "master:web:accumulated"

NEGATIVE_EFFECT_MARKERS = [
    "decrease",
    "decreased",
    "reduce",
    "reduced",
    "lower",
    "worse",
    "impaired",
    "impairment",
    "decline",
    "attenuated",
]

NULL_MARKERS = [
    "no significant",
    "not significant",
    "no effect",
    "null effect",
    "did not support",
]

POSITIVE_MARKERS = [
    "increase",
    "improve",
    "improved",
    "enhance",
    "enhanced",
    "better",
    "higher",
    "support",
    "confirm",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Backfill outcome polarity conflicts into constraints.")
    p.add_argument("--web-db", default=None, help="Path to web DB (auto-resolved if omitted)")
    p.add_argument(
        "--web-db-prefer",
        choices=("integrated", "latest"),
        default="integrated",
        help="Auto-resolution policy when --web-db is omitted",
    )
    p.add_argument("--max-targets-per-source", type=int, default=8, help="Limit positive targets per negative/null source")
    p.add_argument("--dry-run", action="store_true", help="Compute counts without writing")
    return p.parse_args()


def normalize(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def first_paper_id(raw: str) -> str:
    try:
        vals = json.loads(raw or "[]")
        if isinstance(vals, list) and vals:
            return str(vals[0])
    except Exception as e:
        import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")
    return ""


def infer_direction(content: str, tags_raw: str) -> str:
    try:
        tags = json.loads(tags_raw or "[]")
        if isinstance(tags, list):
            for t in tags:
                if isinstance(t, str) and t.startswith("effect_direction:"):
                    v = t.split(":", 1)[1].strip().lower()
                    if v:
                        return v
    except Exception as e:
        import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")

    text = normalize(content)
    if any(m in text for m in NULL_MARKERS):
        return "null"
    if any(m in text for m in NEGATIVE_EFFECT_MARKERS):
        return "negative"
    if any(m in text for m in POSITIVE_MARKERS):
        return "positive"
    return "unknown"


def make_constraint_id(source_id: str, target_id: str, outcome_id: str, provenance: str) -> str:
    raw = f"{source_id}|{target_id}|{outcome_id}|{provenance}"
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:20]
    return f"c:polarity:{digest}"


def main() -> int:
    args = parse_args()
    db = resolve_web_db(args.web_db, prefer=args.web_db_prefer)
    print(f"[backfill_outcome_polarity_conflicts] using web_db={db}")
    now = datetime.now(timezone.utc).isoformat()

    conn = sqlite3.connect(str(db), timeout=60.0)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT belief_id, content, tags, outcome_id, paper_ids
            FROM beliefs
            WHERE web_id = ?
              AND outcome_id IS NOT NULL AND outcome_id != ''
            """,
            (MASTER_WEB_ID,),
        ).fetchall()

        by_outcome: Dict[str, Dict[str, List[Dict[str, str]]]] = {}
        for r in rows:
            outcome_id = str(r["outcome_id"] or "")
            if not outcome_id:
                continue
            direction = infer_direction(str(r["content"] or ""), str(r["tags"] or "[]"))
            rec = {
                "belief_id": str(r["belief_id"]),
                "paper_id": first_paper_id(str(r["paper_ids"] or "[]")),
            }
            bucket = by_outcome.setdefault(
                outcome_id,
                {"positive": [], "negative_or_null": []},
            )
            if direction == "positive":
                bucket["positive"].append(rec)
            elif direction in {"negative", "null"}:
                bucket["negative_or_null"].append(rec)

        existing_ids = {
            row[0]
            for row in conn.execute(
                "SELECT constraint_id FROM constraints WHERE web_id = ?",
                (MASTER_WEB_ID,),
            ).fetchall()
        }

        inserts: List[Tuple[Any, ...]] = []
        per_outcome_counts: Dict[str, int] = {}
        max_targets = max(1, int(args.max_targets_per_source))
        for outcome_id, groups in by_outcome.items():
            positives = groups["positive"]
            negatives = groups["negative_or_null"]
            if not positives or not negatives:
                continue

            # Deterministic order.
            positives = sorted(positives, key=lambda x: x["belief_id"])
            negatives = sorted(negatives, key=lambda x: x["belief_id"])

            added_here = 0
            for src in negatives:
                targets = 0
                for tgt in positives:
                    if src["belief_id"] == tgt["belief_id"]:
                        continue
                    if src["paper_id"] and tgt["paper_id"] and src["paper_id"] == tgt["paper_id"]:
                        continue
                    provenance = f"reprocess:outcome_polarity_conflict|{outcome_id}"
                    cid = make_constraint_id(src["belief_id"], tgt["belief_id"], outcome_id, provenance)
                    if cid in existing_ids:
                        continue
                    existing_ids.add(cid)
                    inserts.append(
                        (
                            cid,
                            MASTER_WEB_ID,
                            src["belief_id"],
                            tgt["belief_id"],
                            "contradicts",
                            0.60,
                            0,
                            json.dumps([src["paper_id"]] if src["paper_id"] else []),
                            "reprocessed_polarity_conflict",
                            provenance,
                            now,
                        )
                    )
                    added_here += 1
                    targets += 1
                    if targets >= max_targets:
                        break
            if added_here:
                per_outcome_counts[outcome_id] = added_here

        if args.dry_run:
            print(f"outcomes_with_conflicts={len(per_outcome_counts)}")
            print(f"would_insert={len(inserts)}")
            print(f"per_outcome_counts={per_outcome_counts}")
            return 0

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
            conn.commit()

        counts = conn.execute(
            "SELECT constraint_type, COUNT(*) FROM constraints WHERE web_id = ? GROUP BY constraint_type ORDER BY COUNT(*) DESC",
            (MASTER_WEB_ID,),
        ).fetchall()
        print(f"inserted={len(inserts)}")
        print(f"outcomes_with_conflicts={len(per_outcome_counts)}")
        print(f"per_outcome_counts={per_outcome_counts}")
        print(f"constraint_type_counts={[(r[0], r[1]) for r in counts]}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
