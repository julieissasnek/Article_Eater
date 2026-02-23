#!/usr/bin/env python3
"""Rebuild Web of Belief database from structured claims (Sprint D.11)."""

from __future__ import annotations

import argparse
import json
import logging
import re
import shutil
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.services.web_of_belief import (
    Belief,
    BeliefStatus,
    Constraint,
    ConstraintType,
    Credence,
    EpistemicLevel,
    WebOfBelief,
)
from src.services.web_persistence import WebPersistenceService
from src.services.extraction_to_web import claim_to_belief

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "web_persistence_v2.db"
DEFAULT_INPUT_PATH = PROJECT_ROOT / "data" / "production" / "structured_claims_codex_semantic.json"
DEFAULT_BASELINE_DB = PROJECT_ROOT / "data" / "web_persistence.db"
DEFAULT_GOLD_STANDARD = PROJECT_ROOT / "data" / "gold_standard" / "gold_standard_papers.json"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "docs" / "web_health_report_post_rebuild.md"
MASTER_WEB_ID = "master:web:accumulated"

def backup_database(db_path: Path):
    """Create a timestamped backup of the database."""
    if not db_path.exists():
        logger.info(f"No existing database at {db_path}, skipping backup.")
        return

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_path = db_path.with_name(f"{db_path.name}.{timestamp}.bak")
    
    try:
        shutil.copy2(db_path, backup_path)
        logger.info(f"Backed up database to {backup_path}")
    except Exception as e:
        logger.error(f"Failed to backup database: {e}")
        sys.exit(1)

def load_claims(input_path: Path) -> list[dict[str, Any]]:
    """Load claims from JSONL, JSON list, or JSON payload with `claims` field."""
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        sys.exit(1)

    claims: list[dict[str, Any]] = []
    suffix = input_path.suffix.lower()

    if suffix == ".jsonl":
        with input_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    logger.warning("Skipping invalid JSONL line.")
                    continue
                if isinstance(payload, dict):
                    claims.append(payload)
    else:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            claims = [item for item in payload if isinstance(item, dict)]
        elif isinstance(payload, dict):
            maybe_claims = payload.get("claims")
            if isinstance(maybe_claims, list):
                claims = [item for item in maybe_claims if isinstance(item, dict)]
            else:
                logger.error("JSON payload missing list field `claims`.")
                sys.exit(1)
        else:
            logger.error("Unsupported input format for claims payload.")
            sys.exit(1)

    logger.info(f"Loaded {len(claims)} claims from {input_path}")
    return claims


def load_gold_standard_papers(path: Path) -> set[str]:
    """Load paper IDs from Sprint D gold-standard registry."""
    if not path.exists():
        return set()
    payload = json.loads(path.read_text(encoding="utf-8"))
    papers = payload.get("papers", [])
    selected = set()
    for row in papers:
        if not isinstance(row, dict):
            continue
        paper_id = str(row.get("paper_id") or "").strip()
        if not paper_id:
            continue
        status = str(row.get("gold_standard_status") or "").strip().lower()
        if status in {"selected", "candidate"}:
            selected.add(paper_id)
    return selected


def _safe_belief_id(claim_id: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_]+", "_", claim_id).strip("_")
    if not cleaned:
        cleaned = "unknown_id"
    return f"b_{cleaned}"


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> int | None:
    numeric = _to_float(value)
    if numeric is None:
        return None
    return int(numeric)


def compute_credence(claim: dict[str, Any], gold_standard_paper_ids: set[str]) -> float:
    """Assign credence using the D.11 scoring rubric."""
    score = 0.5

    if claim.get("effect_size") is not None:
        score += 0.1

    sample_n = _to_int(claim.get("sample_n"))
    if sample_n is not None and sample_n > 50:
        score += 0.1
    if sample_n is not None and sample_n > 200:
        score += 0.05

    if str(claim.get("paper_id") or "") in gold_standard_paper_ids:
        score += 0.1

    if bool(claim.get("iv_mapped")) and bool(claim.get("dv_mapped")):
        score += 0.05

    confidence = _to_float(claim.get("extraction_confidence"))
    if confidence is not None and confidence < 0.5:
        score -= 0.1

    if str(claim.get("effect_size_type") or "").strip().lower() == "p_value_only":
        score -= 0.05

    return max(0.2, min(0.95, score))


def convert_claim_to_belief(claim: dict[str, Any], gold_standard_paper_ids: set[str] | None = None) -> Belief:
    """Convert an extracted claim into a WebOfBelief belief."""
    gold_standard_paper_ids = gold_standard_paper_ids or set()
    
    # 1. First run the rich extraction mapping
    result = claim_to_belief(claim)
    if not result.success or not result.entity:
        raise ValueError(f"Failed to map claim: {result.warnings}")
        
    belief = result.entity
    
    # 2. Override the credence score using the Sprint D scoring rubric
    credence_value = compute_credence(claim, gold_standard_paper_ids)
    
    # Keep the uncertainty and evidential direction calculated by claim_to_belief
    belief.credence.value = credence_value
    
    # 3. Enhance tags like the original script did
    if "source:extraction_pipeline" not in belief.tags:
        belief.tags.append("source:extraction_pipeline")
    if claim.get("semantic_type"):
        belief.tags.append(f"type:{claim['semantic_type']}")
    if claim.get("context"):
        belief.tags.append(f"context:{claim['context']}")
    if claim.get("batch_id"):
        belief.tags.append(f"batch:{claim['batch_id']}")
        
    return belief


def _constraint_id(prefix: str, source_id: str, target_id: str) -> str:
    ordered = sorted([source_id, target_id])
    return f"{prefix}:{ordered[0]}:{ordered[1]}"


def _iter_pairs(values: list[str]) -> Iterable[tuple[str, str]]:
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            yield values[i], values[j]


def _is_contradiction(direction_a: str, direction_b: str) -> bool:
    a = (direction_a or "").strip().lower()
    b = (direction_b or "").strip().lower()
    return (
        (a in {"positive", "increase"} and b in {"negative", "decrease"})
        or (a in {"negative", "decrease"} and b in {"positive", "increase"})
    )


def _direction_trust(claim: dict[str, Any]) -> float:
    """Estimate trust in claim direction for contradiction edge calibration."""
    direction = str(claim.get("direction") or "unknown").strip().lower()
    if direction not in {"increase", "decrease", "positive", "negative"}:
        return 0.0
    trust = 0.45
    direction_conf = _to_float(claim.get("direction_confidence"))
    if direction_conf is not None:
        trust = max(trust, min(1.0, direction_conf))
    extraction_conf = _to_float(claim.get("extraction_confidence"))
    if extraction_conf is not None and extraction_conf >= 0.8:
        trust += 0.08
    if claim.get("p_value") is not None:
        trust += 0.08
    if claim.get("is_significant") is True:
        trust += 0.06
    if claim.get("theory_direction_tension"):
        trust -= 0.25
    if claim.get("direction_demoted_reason"):
        trust -= 0.35
    return max(0.0, min(1.0, trust))


def _derive_domain(claim: dict[str, Any]) -> str | None:
    context = str(claim.get("context") or "").strip().lower()
    if context:
        return context
    iv = str(claim.get("iv") or "").strip().lower()
    if "light" in iv or "lumin" in iv or "cct" in iv:
        return "light"
    if "noise" in iv or "acoustic" in iv or "sound" in iv:
        return "acoustics"
    if "temperature" in iv or "thermal" in iv:
        return "thermal"
    if "view" in iv or "nature" in iv:
        return "view"
    return None


def add_relationship_constraints(web: WebOfBelief, claim_by_belief_id: dict[str, dict[str, Any]]) -> dict[str, int]:
    """Add D.11 constraint layers: intra-paper, replication, scope, contradiction, bridges."""
    counts = defaultdict(int)

    def add_once(prefix: str, source_id: str, target_id: str, ctype: ConstraintType, strength: float) -> None:
        cid = _constraint_id(prefix, source_id, target_id)
        if cid in web.constraints:
            return
        web.add_constraint(
            Constraint(
                constraint_id=cid,
                source_id=source_id,
                target_id=target_id,
                constraint_type=ctype,
                strength=strength,
                bidirectional=True,
            )
        )
        counts[prefix] += 1

    by_paper: dict[str, list[str]] = defaultdict(list)
    by_iv_dv: dict[tuple[str, str], list[str]] = defaultdict(list)
    by_iv: dict[str, list[str]] = defaultdict(list)
    by_template: dict[str, list[str]] = defaultdict(list)
    by_domain: dict[str, list[str]] = defaultdict(list)

    for belief_id, claim in claim_by_belief_id.items():
        paper_id = str(claim.get("paper_id") or "").strip()
        iv = str(claim.get("iv") or "").strip().lower()
        dv = str(claim.get("dv") or "").strip().lower()
        template_id = str(claim.get("template_id") or "").strip()
        domain = _derive_domain(claim)

        if paper_id:
            by_paper[paper_id].append(belief_id)
        if iv and dv:
            by_iv_dv[(iv, dv)].append(belief_id)
        if iv:
            by_iv[iv].append(belief_id)
        if template_id:
            by_template[template_id].append(belief_id)
        if domain:
            by_domain[domain].append(belief_id)

    for belief_ids in by_paper.values():
        for source_id, target_id in _iter_pairs(sorted(set(belief_ids))):
            add_once("intra", source_id, target_id, ConstraintType.SUPPORTS, 0.55)

    for belief_ids in by_iv_dv.values():
        unique_ids = sorted(set(belief_ids))
        for source_id, target_id in _iter_pairs(unique_ids):
            left = claim_by_belief_id[source_id]
            right = claim_by_belief_id[target_id]
            if left.get("paper_id") == right.get("paper_id"):
                continue
            if _is_contradiction(str(left.get("direction")), str(right.get("direction"))):
                trust = min(_direction_trust(left), _direction_trust(right))
                if trust < 0.55:
                    counts["contradiction_suppressed_low_trust"] += 1
                    continue
                contradiction_strength = min(0.9, 0.45 + 0.4 * trust)
                add_once("contradiction", source_id, target_id, ConstraintType.CONTRADICTS, contradiction_strength)
            else:
                add_once("replication", source_id, target_id, ConstraintType.SUPPORTS, 0.7)

    for belief_ids in by_iv.values():
        unique_ids = sorted(set(belief_ids))
        for source_id, target_id in _iter_pairs(unique_ids):
            left = claim_by_belief_id[source_id]
            right = claim_by_belief_id[target_id]
            if left.get("paper_id") == right.get("paper_id"):
                continue
            left_dv = str(left.get("dv") or "").strip().lower()
            right_dv = str(right.get("dv") or "").strip().lower()
            if left_dv and right_dv and left_dv != right_dv:
                add_once("scope", source_id, target_id, ConstraintType.BRIDGES, 0.45)

    for belief_ids in by_template.values():
        for source_id, target_id in _iter_pairs(sorted(set(belief_ids))):
            add_once("template_bridge", source_id, target_id, ConstraintType.BRIDGES, 0.6)

    for belief_ids in by_domain.values():
        for source_id, target_id in _iter_pairs(sorted(set(belief_ids))):
            add_once("domain_bridge", source_id, target_id, ConstraintType.BRIDGES, 0.35)

    return dict(counts)


def _count_connected_components(web: WebOfBelief) -> int:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for constraint in web.constraints.values():
        adjacency[constraint.source_id].add(constraint.target_id)
        adjacency[constraint.target_id].add(constraint.source_id)
    for belief_id in web.beliefs:
        adjacency.setdefault(belief_id, set())

    remaining = set(adjacency.keys())
    components = 0
    while remaining:
        components += 1
        stack = [remaining.pop()]
        while stack:
            node = stack.pop()
            for neighbor in adjacency.get(node, set()):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    stack.append(neighbor)
    return components


def collect_web_health(db_path: Path) -> dict[str, Any]:
    if not db_path.exists():
        return {"db_exists": False}
    service = WebPersistenceService(str(db_path))
    master_id = service.get_master_web_id() or service.create_or_get_master_web()
    web, _ = service.load_web(master_id)
    if web is None:
        return {"db_exists": True, "load_ok": False}

    beliefs = list(web.beliefs.values())
    mapped = sum(1 for b in beliefs if b.environment_id and b.outcome_id)
    garbage_like = sum(
        1
        for b in beliefs
        if len(b.content) > 220 or "(cid:" in b.content.lower() or "env.unresolved" in b.content.lower()
    )
    unresolved_env = sum(
        1 for b in beliefs if str(b.environment_id or "").lower().startswith("env.unresolved")
    )

    return {
        "db_exists": True,
        "load_ok": True,
        "beliefs": len(web.beliefs),
        "constraints": len(web.constraints),
        "coherence": web.coherence_score(),
        "connected_components": _count_connected_components(web),
        "mapped_beliefs": mapped,
        "garbage_like_beliefs": garbage_like,
        "unresolved_env_ids": unresolved_env,
    }


def write_report(
    report_path: Path,
    *,
    input_path: Path,
    claims_loaded: int,
    constraints_added: dict[str, int],
    baseline: dict[str, Any],
    rebuilt: dict[str, Any],
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Web Health Report Post Rebuild (D.11)",
        "",
        f"- Generated: {datetime.now(timezone.utc).isoformat()}",
        f"- Input claims: `{input_path}`",
        f"- Claims loaded: **{claims_loaded}**",
        "",
        "## Constraint Layers Added",
        "",
        f"- Intra-paper coherence: {constraints_added.get('intra', 0)}",
        f"- Replication links: {constraints_added.get('replication', 0)}",
        f"- Scope extensions: {constraints_added.get('scope', 0)}",
        f"- Contradictions: {constraints_added.get('contradiction', 0)}",
        f"- Contradictions suppressed (low direction trust): {constraints_added.get('contradiction_suppressed_low_trust', 0)}",
        f"- Template bridges: {constraints_added.get('template_bridge', 0)}",
        f"- Domain bridges: {constraints_added.get('domain_bridge', 0)}",
        "",
        "## Old vs New Web",
        "",
        "| Metric | Old web_persistence.db | New web_persistence_v2.db |",
        "|---|---:|---:|",
        f"| Beliefs | {baseline.get('beliefs', 'n/a')} | {rebuilt.get('beliefs', 'n/a')} |",
        f"| Constraints | {baseline.get('constraints', 'n/a')} | {rebuilt.get('constraints', 'n/a')} |",
        f"| Coherence | {baseline.get('coherence', 'n/a')} | {rebuilt.get('coherence', 'n/a')} |",
        f"| Connected components | {baseline.get('connected_components', 'n/a')} | {rebuilt.get('connected_components', 'n/a')} |",
        f"| Mapped beliefs (IV+DV) | {baseline.get('mapped_beliefs', 'n/a')} | {rebuilt.get('mapped_beliefs', 'n/a')} |",
        f"| Garbage-like beliefs | {baseline.get('garbage_like_beliefs', 'n/a')} | {rebuilt.get('garbage_like_beliefs', 'n/a')} |",
        f"| Unresolved env IDs | {baseline.get('unresolved_env_ids', 'n/a')} | {rebuilt.get('unresolved_env_ids', 'n/a')} |",
        "",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Rebuild web_persistence_v2.db from structured claims.")
    parser.add_argument("--db-path", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--baseline-db", type=Path, default=DEFAULT_BASELINE_DB)
    parser.add_argument("--gold-standard", type=Path, default=DEFAULT_GOLD_STANDARD)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--no-backup", action="store_true", help="Skip backup")
    args = parser.parse_args()

    # 1. Backup
    if not args.no_backup:
        backup_database(args.db_path)

    # 2. Load claims + gold standard
    claims = load_claims(args.input)
    gold_standard_paper_ids = load_gold_standard_papers(args.gold_standard)

    # 3. Build in-memory web
    web = WebOfBelief()
    claim_by_belief_id: dict[str, dict[str, Any]] = {}
    converted_count = 0
    for claim in claims:
        try:
            belief = convert_claim_to_belief(claim, gold_standard_paper_ids)
            web.add_belief(belief)
            claim_by_belief_id[belief.belief_id] = claim
            converted_count += 1
        except Exception as e:
            logger.error(f"Failed to convert claim {claim.get('claim_id')}: {e}")

    logger.info(f"Converted {converted_count} beliefs into WebOfBelief")
    constraint_counts = add_relationship_constraints(web, claim_by_belief_id)
    logger.info("Added constraints: %s", constraint_counts)

    # 4. Persist
    if args.db_path.exists():
        logger.info(f"Removing existing DB at {args.db_path} for clean rebuild...")
        args.db_path.unlink()

    persistence = WebPersistenceService(str(args.db_path))
    persistence.create_or_get_master_web()
    persistence.save_web(web, MASTER_WEB_ID)

    logger.info(f"Successfully saved {len(web.beliefs)} beliefs to {args.db_path}")

    # 5. Verification + health report
    reloaded_web, _ = persistence.load_web(MASTER_WEB_ID)
    if not reloaded_web:
        logger.error("Failed to reload web from DB")
        sys.exit(1)

    logger.info(f"Verification: Reloaded {len(reloaded_web.beliefs)} beliefs from DB.")
    if len(reloaded_web.beliefs) == len(web.beliefs):
        logger.info("rebuild_web_db SUCCESS")
    else:
        logger.error("rebuild_web_db VERIFICATION FAILED: Counts do not match")
        return 1

    baseline_metrics = collect_web_health(args.baseline_db)
    rebuilt_metrics = collect_web_health(args.db_path)
    write_report(
        args.report_path,
        input_path=args.input,
        claims_loaded=len(claims),
        constraints_added=constraint_counts,
        baseline=baseline_metrics,
        rebuilt=rebuilt_metrics,
    )
    logger.info("Wrote report to %s", args.report_path)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
