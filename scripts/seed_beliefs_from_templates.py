"""
Seed beliefs from template JSON files into the Web of Belief.

Addresses Audit Structural Risk #3: calibrated templates sit on disk
but never populate the beliefs table.

Usage:
    python scripts/seed_beliefs_from_templates.py              # seed to default DB
    python scripts/seed_beliefs_from_templates.py --dry-run    # report without writing
    python scripts/seed_beliefs_from_templates.py --clear-existing  # clear old template beliefs first
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Project imports
# ---------------------------------------------------------------------------
from src.services.web_of_belief import (
    Belief,
    BeliefStatus,
    Constraint,
    ConstraintType,
    Credence,
    EpistemicLevel,
    WebOfBelief,
)
from src.services.bridge_warrants import compute_bridged_credence
from src.services.db_locator import get_web_db
from src.services.web_persistence import WebPersistenceService

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Bridge warrant type → prior probability (from the authoritative hierarchy)
BRIDGE_WARRANT_PRIORS: Dict[str, float] = {
    "CONSTITUTIVE": 0.75,
    "MECHANISM": 0.60,
    "EMPIRICAL_ASSOCIATION": 0.60,
    "EMPIRICAL_ASSOCIATION": 0.60,
    "FUNCTIONAL": 0.50,
    "CAPACITY": 0.45,
    "ANALOGICAL": 0.35,
    "THEORY_DERIVED": 0.25,  # For uncalibrated templates
}

# Default T1 framework prior credence (established neurally-grounded frameworks)
T1_FRAMEWORK_PRIOR = 0.70

# Statuses that qualify a template for belief seeding
CALIBRATED_STATUSES = {"calibrated"}
CALIBRATION_FIELD_STATUSES = {"substantial", "partial"}

TEMPLATE_BELIEF_PREFIX = "template:"

# Theory ID aliases (from staging_theory_loader.py)
_THEORY_ALIASES: Dict[str, str] = {
    "attention_restoration_theory": "ART",
    "stress_reduction_theory": "SRT",
    "prospect_refuge_theory": "BIOPHILIA",
    "biophilia": "BIOPHILIA",
    "art": "ART",
    "srt": "SRT",
    "predictive_processing": "PP",
    "spatial_navigation": "SN",
    "dual_process": "DP",
    "dmn_tpn": "DT",
    "neuromodulatory": "NM",
    "interoception": "IC",
    "memory_systems": "MS",
    "embodied_cognition": "EC",
    "chronobiological": "CB",
    "multisensory_integration": "MSI",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalize_theory_id(raw: str) -> str:
    """Normalize a theory/framework ID to its canonical short form."""
    key = raw.strip().lower().replace("-", "_").replace(" ", "_")
    if key in _THEORY_ALIASES:
        return _THEORY_ALIASES[key]
    # Already a short canonical ID (e.g. "PP", "SN")
    if len(raw.strip()) <= 6 and raw.strip().isupper():
        return raw.strip()
    return raw.strip().upper()


def _normalize_framework_id(entry: Any) -> Optional[str]:
    """Extract the framework ID from a t1_frameworks entry.

    Handles both plain strings ("PP") and dict format ({"id": "PP", "role": "..."}).
    """
    if isinstance(entry, str):
        raw = entry.strip()
        return _normalize_theory_id(raw) if raw else None
    if isinstance(entry, dict):
        fid = entry.get("id")
        return _normalize_theory_id(str(fid).strip()) if fid else None
    return None


def _get_framework_ids(payload: Dict[str, Any]) -> List[str]:
    """Extract all framework IDs from a template payload, handling both formats."""
    raw = payload.get("t1_frameworks", [])
    if not isinstance(raw, list):
        return []
    ids = []
    for entry in raw:
        fid = _normalize_framework_id(entry)
        if fid:
            ids.append(fid)
    return ids


def _is_calibrated(payload: Dict[str, Any]) -> bool:
    """Check whether a template JSON qualifies as calibrated."""
    status = (payload.get("status") or "").strip().lower()
    if status in CALIBRATED_STATUSES:
        return True
    cal_status = (payload.get("calibration_status") or "").strip().lower()
    return cal_status in CALIBRATION_FIELD_STATUSES


def _extract_confidence_scores(payload: Dict[str, Any]) -> List[float]:
    """Recursively extract all 'confidence' values from calibrated_parameters."""
    scores: List[float] = []

    def _walk(obj: Any) -> None:
        if isinstance(obj, dict):
            if "confidence" in obj:
                val = obj["confidence"]
                if isinstance(val, (int, float)):
                    scores.append(float(val))
            for v in obj.values():
                _walk(v)
        elif isinstance(obj, list):
            for item in obj:
                _walk(item)

    params = payload.get("calibrated_parameters", {})
    _walk(params)
    return scores


def _compute_template_credence(
    payload: Dict[str, Any],
    parent_prior: float = T1_FRAMEWORK_PRIOR,
) -> Tuple[float, float]:
    """
    Compute credence value and uncertainty for a template belief.

    Returns (credence_value, uncertainty).
    """
    # Bridge confidence: use explicit bridge_prior if available, else look up by warrant type
    bridge_prior = payload.get("bridge_prior")
    if bridge_prior is None:
        warrant_type = (payload.get("bridge_warrant") or "").upper()
        bridge_prior = BRIDGE_WARRANT_PRIORS.get(warrant_type, 0.50)

    # CNFA-specific: average of per-parameter confidence scores
    conf_scores = _extract_confidence_scores(payload)
    cnfa_specific = sum(conf_scores) / len(conf_scores) if conf_scores else 0.50

    credence_value = compute_bridged_credence(parent_prior, bridge_prior, cnfa_specific)

    # Uncertainty: higher when fewer confidence scores are available
    if len(conf_scores) >= 5:
        uncertainty = 0.15  # Well-calibrated
    elif len(conf_scores) >= 2:
        uncertainty = 0.25  # Moderate calibration
    else:
        uncertainty = 0.40  # Sparse calibration

    return credence_value, uncertainty


def _build_content_summary(payload: Dict[str, Any]) -> str:
    """Build a belief content string from template fields."""
    name = payload.get("name", "Unnamed template")
    chain = payload.get("mechanism_chain", [])
    if isinstance(chain, list) and chain:
        # Trim arrow prefixes for cleaner content
        steps = [s.lstrip("→ ").strip() for s in chain if isinstance(s, str)]
        chain_summary = " → ".join(steps[:4])  # First 4 steps
        if len(steps) > 4:
            chain_summary += " → ..."
        return f"{name}: {chain_summary}"
    # Fallback: use causal_links for uncalibrated templates
    causal_links = payload.get("causal_links", [])
    if isinstance(causal_links, list) and causal_links:
        link_summaries = []
        for link in causal_links[:3]:
            if isinstance(link, dict):
                cause = link.get("cause", "?")
                effect = link.get("effect", "?")
                link_summaries.append(f"{cause} → {effect}")
        if link_summaries:
            return f"{name}: {'; '.join(link_summaries)}"
    return name


def _get_template_id(payload: Dict[str, Any]) -> Optional[str]:
    """Extract template_id from payload, falling back to id."""
    tid = payload.get("template_id") or payload.get("id")
    return str(tid).strip() if tid else None


# ---------------------------------------------------------------------------
# Core seeder
# ---------------------------------------------------------------------------

def scan_calibrated_templates(
    templates_dir: Path,
) -> List[Tuple[Path, Dict[str, Any]]]:
    """Scan templates directory and return list of (path, payload) for calibrated templates."""
    results = []
    for template_path in sorted(templates_dir.glob("*.json")):
        try:
            payload = json.loads(template_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Skipping %s: %s", template_path.name, exc)
            continue

        if not _is_calibrated(payload):
            continue

        tid = _get_template_id(payload)
        if not tid:
            logger.warning("Skipping %s: no template_id", template_path.name)
            continue

        results.append((template_path, payload))
    return results


def scan_all_templates(
    templates_dir: Path,
) -> Tuple[List[Tuple[Path, Dict[str, Any]]], List[Tuple[Path, Dict[str, Any]]]]:
    """
    Scan templates directory and return calibrated and uncalibrated separately.

    Returns (calibrated, uncalibrated) tuple.
    EN-0B extension.
    """
    calibrated = []
    uncalibrated = []
    for template_path in sorted(templates_dir.glob("*.json")):
        try:
            payload = json.loads(template_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Skipping %s: %s", template_path.name, exc)
            continue

        tid = _get_template_id(payload)
        if not tid:
            logger.warning("Skipping %s: no template_id", template_path.name)
            continue

        if _is_calibrated(payload):
            calibrated.append((template_path, payload))
        else:
            uncalibrated.append((template_path, payload))

    return calibrated, uncalibrated


def create_belief_from_template(
    payload: Dict[str, Any],
    source_path: Path,
    is_uncalibrated: bool = False,
) -> Belief:
    """Create a Belief object from a template JSON payload.

    For uncalibrated templates (EN-0B), assigns lower epistemic level
    and provisional status with appropriate provenance tags.
    """
    tid = _get_template_id(payload)
    assert tid is not None

    # Compute credence
    credence_value, uncertainty = _compute_template_credence(payload)

    # Determine primary theory
    frameworks = _get_framework_ids(payload)
    theory_id = frameworks[0] if frameworks else None

    # Build tags
    tags = ["template_seeded"]
    if is_uncalibrated:
        tags.append("uncalibrated")
        tags.append("en-0b-seeded")
    panel_id = payload.get("panel_id")
    if panel_id:
        tags.append(f"panel:{panel_id}")
    bridge_warrant = payload.get("bridge_warrant")
    if bridge_warrant:
        tags.append(f"bridge:{bridge_warrant}")
    bridge_inferred = payload.get("bridge_inferred", False)
    if bridge_inferred:
        tags.append("bridge_inferred")
    status_field = payload.get("status") or payload.get("calibration_status") or ""
    tags.append(f"calibration:{status_field}")

    # Uncalibrated templates get lower epistemic standing
    level = EpistemicLevel.INTERMEDIATE if is_uncalibrated else EpistemicLevel.THEORETICAL
    status = BeliefStatus.TENTATIVE if is_uncalibrated else BeliefStatus.ESTABLISHED

    return Belief(
        belief_id=f"{TEMPLATE_BELIEF_PREFIX}{tid}",
        content=_build_content_summary(payload),
        level=level,
        status=status,
        credence=Credence(value=credence_value, uncertainty=uncertainty),
        theory_id=theory_id,
        domain="cnfa",
        tags=tags,
    )


def create_interaction_constraints(
    beliefs_by_tid: Dict[str, Belief],
    templates_by_tid: Dict[str, Dict[str, Any]],
) -> List[Constraint]:
    """Create Constraint edges between templates that declare interactions."""
    constraints: List[Constraint] = []
    seen_pairs: set = set()

    for tid, payload in templates_by_tid.items():
        interactions = payload.get("interaction_templates", [])
        if not isinstance(interactions, list):
            continue

        for other_tid in interactions:
            other_tid = str(other_tid).strip()
            if not other_tid or other_tid == tid:
                continue

            # Normalize pair to avoid duplicates
            pair = tuple(sorted([tid, other_tid]))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)

            bid_a = f"{TEMPLATE_BELIEF_PREFIX}{tid}"
            bid_b = f"{TEMPLATE_BELIEF_PREFIX}{other_tid}"

            # Only create constraint if both beliefs exist
            if tid not in beliefs_by_tid or other_tid not in beliefs_by_tid:
                continue

            # Determine if same T1 family (supports) or cross-family (instantiates)
            frameworks_a = set(_get_framework_ids(templates_by_tid[tid]))
            frameworks_b = set(_get_framework_ids(templates_by_tid.get(other_tid, {})))
            shared = frameworks_a & frameworks_b

            constraint_type = ConstraintType.SUPPORTS if shared else ConstraintType.INSTANTIATES
            strength = 0.5

            constraint = Constraint(
                constraint_id=f"interaction:{pair[0]}:{pair[1]}",
                source_id=bid_a,
                target_id=bid_b,
                constraint_type=constraint_type,
                strength=strength,
            )
            constraints.append(constraint)

    return constraints


def seed_beliefs(
    templates_dir: Path = Path("data/templates"),
    db_path: str = str(get_web_db()),
    dry_run: bool = False,
    clear_existing: bool = False,
    include_uncalibrated: bool = False,
) -> Dict[str, Any]:
    """
    Main entry point: scan templates, create beliefs, persist to WoB.

    Returns summary dict with counts and details.

    If include_uncalibrated=True (EN-0B), also seeds beliefs from
    uncalibrated templates at lower epistemic standing.
    """
    # 1. Scan templates
    if include_uncalibrated:
        calibrated, uncalibrated = scan_all_templates(templates_dir)
        logger.info("Found %d calibrated + %d uncalibrated templates",
                    len(calibrated), len(uncalibrated))
        all_templates = [
            (path, payload, False) for path, payload in calibrated
        ] + [
            (path, payload, True) for path, payload in uncalibrated
        ]
    else:
        calibrated = scan_calibrated_templates(templates_dir)
        logger.info("Found %d calibrated templates", len(calibrated))
        all_templates = [(path, payload, False) for path, payload in calibrated]

    # 2. Create beliefs
    beliefs: Dict[str, Belief] = {}
    templates_by_tid: Dict[str, Dict[str, Any]] = {}
    per_theory: Counter = Counter()
    per_warrant: Counter = Counter()
    n_calibrated = 0
    n_uncalibrated = 0

    for path, payload, is_uncal in all_templates:
        tid = _get_template_id(payload)
        assert tid is not None

        belief = create_belief_from_template(payload, path, is_uncalibrated=is_uncal)
        beliefs[tid] = belief
        templates_by_tid[tid] = payload

        if is_uncal:
            n_uncalibrated += 1
        else:
            n_calibrated += 1

        if belief.theory_id:
            per_theory[belief.theory_id] += 1
        warrant = payload.get("bridge_warrant", "UNKNOWN")
        per_warrant[warrant] += 1

    # 3. Create interaction constraints
    constraints = create_interaction_constraints(beliefs, templates_by_tid)
    logger.info("Created %d interaction constraints", len(constraints))

    # 4. Build summary
    summary = {
        "templates_scanned": len(list(templates_dir.glob("*.json"))),
        "calibrated_seeded": n_calibrated,
        "uncalibrated_seeded": n_uncalibrated,
        "beliefs_created": len(beliefs),
        "constraints_created": len(constraints),
        "per_theory": dict(sorted(per_theory.items())),
        "per_warrant": dict(sorted(per_warrant.items())),
        "belief_ids": sorted(beliefs.keys()),
        "include_uncalibrated": include_uncalibrated,
    }

    if dry_run:
        summary["mode"] = "DRY_RUN"
        print("\n=== DRY RUN — Template → Belief Seeder ===")
        if include_uncalibrated:
            print("(EN-0B: including uncalibrated templates)")
        print(f"\nTemplates directory: {templates_dir}")
        print(f"Calibrated templates: {n_calibrated}")
        if include_uncalibrated:
            print(f"Uncalibrated templates: {n_uncalibrated}")
        print(f"Total beliefs that would be created: {len(beliefs)}")
        print(f"Constraints that would be created: {len(constraints)}")
        print(f"\nPer T1 framework: {dict(per_theory)}")
        print(f"Per bridge warrant: {dict(per_warrant)}")
        print("\nBeliefs (first 20):")
        for i, (tid, belief) in enumerate(sorted(beliefs.items())):
            if i >= 20:
                print(f"  ... and {len(beliefs) - 20} more")
                break
            uncal_marker = " [UNCAL]" if "uncalibrated" in belief.tags else ""
            print(f"  {belief.belief_id}: credence={belief.credence.value:.3f} "
                  f"±{belief.credence.uncertainty:.2f} | theory={belief.theory_id} | "
                  f"{belief.content[:70]}{uncal_marker}")
        print("\nConstraints:")
        for c in constraints:
            print(f"  {c.constraint_id}: {c.source_id} → {c.target_id} "
                  f"({c.constraint_type.value}, strength={c.strength})")
        return summary

    # 5. Persist to WebOfBelief via WebPersistenceService
    summary["mode"] = "LIVE"
    print(f"\n=== LIVE — Seeding {len(beliefs)} beliefs to {db_path} ===")
    if include_uncalibrated:
        print(f"  ({n_calibrated} calibrated + {n_uncalibrated} uncalibrated)")

    service = WebPersistenceService(db_path)
    master_web_id = service.create_or_get_master_web()

    if clear_existing:
        # Remove previously seeded template beliefs and touching constraints.
        like_pattern = f"{TEMPLATE_BELIEF_PREFIX}%"
        with service._get_connection() as conn:  # type: ignore[attr-defined]
            beliefs_to_remove = conn.execute(
                "SELECT COUNT(*) AS n FROM beliefs WHERE web_id = ? AND belief_id LIKE ?",
                (master_web_id, like_pattern),
            ).fetchone()["n"]
            constraints_to_remove = conn.execute(
                """
                SELECT COUNT(*) AS n
                FROM constraints
                WHERE web_id = ?
                  AND (source_id LIKE ? OR target_id LIKE ?)
                """,
                (master_web_id, like_pattern, like_pattern),
            ).fetchone()["n"]

            conn.execute(
                """
                DELETE FROM constraints
                WHERE web_id = ?
                  AND (source_id LIKE ? OR target_id LIKE ?)
                """,
                (master_web_id, like_pattern, like_pattern),
            )
            conn.execute(
                "DELETE FROM beliefs WHERE web_id = ? AND belief_id LIKE ?",
                (master_web_id, like_pattern),
            )
            # Best-effort cleanup for timeline artifacts if table exists.
            try:
                conn.execute(
                    "DELETE FROM entrenchment_snapshots WHERE web_id = ? AND belief_id LIKE ?",
                    (master_web_id, like_pattern),
                )
            except Exception as e:
                logger.debug(f"Non-critical: {e}")

        print(
            "Cleared existing template-seeded rows: "
            f"{beliefs_to_remove} beliefs, {constraints_to_remove} constraints."
        )
        summary["cleared"] = int(beliefs_to_remove)
        summary["cleared_constraints"] = int(constraints_to_remove)

    # Build a WebOfBelief in memory, add beliefs and constraints, then save
    web = WebOfBelief(domain="cnfa")

    for belief in beliefs.values():
        web.add_belief(belief)

    for constraint in constraints:
        # Ensure both source and target exist before adding
        if constraint.source_id in web.beliefs and constraint.target_id in web.beliefs:
            web.constraints[constraint.constraint_id] = constraint

    # Save to persistence layer
    service.save_web(web, master_web_id, name="Master Accumulated Web", is_master=True)

    print(f"Saved {len(web.beliefs)} beliefs and {len(web.constraints)} constraints "
          f"to web {master_web_id}")
    print(f"\nPer T1 framework: {dict(per_theory)}")
    print(f"Per bridge warrant: {dict(per_warrant)}")

    return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Seed beliefs from calibrated template JSON into the Web of Belief."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would be seeded without writing to DB",
    )
    parser.add_argument(
        "--db-path",
        default=str(get_web_db()),
        help="Path to the web persistence SQLite DB (default: data/web_persistence_v2.db)",
    )
    parser.add_argument(
        "--templates-dir",
        default="data/templates",
        help="Path to templates directory (default: data/templates)",
    )
    parser.add_argument(
        "--clear-existing",
        action="store_true",
        help="Clear existing template-seeded beliefs before re-seeding",
    )
    parser.add_argument(
        "--include-uncalibrated",
        action="store_true",
        help="EN-0B: Also seed beliefs from uncalibrated/scaffold templates (at lower epistemic standing)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    summary = seed_beliefs(
        templates_dir=Path(args.templates_dir),
        db_path=args.db_path,
        dry_run=args.dry_run,
        clear_existing=args.clear_existing,
        include_uncalibrated=args.include_uncalibrated,
    )

    print(f"\nDone. Summary: {summary['beliefs_created']} beliefs, "
          f"{summary['constraints_created']} constraints.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
