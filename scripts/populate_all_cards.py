"""
Populate All Cards — Initial Generation for All Nine Card Types
================================================================

Reads source data for each card type and queues generation through
the CardGenerationOrchestrator. Supports both immediate processing
and session-queue mode (for Opus-allocated types to be processed
in CW/CC/AG sessions at zero marginal API cost).

Usage:
    # Queue all cards for generation
    python scripts/populate_all_cards.py --queue-only

    # Queue and immediately process Sonnet-allocated cards (API batch)
    python scripts/populate_all_cards.py --process-sonnet

    # Queue and immediately process ALL cards (costs Opus API credits)
    python scripts/populate_all_cards.py --process-all

    # Process only session-queued cards (run from CW/CC session)
    python scripts/populate_all_cards.py --process-session

    # Status report
    python scripts/populate_all_cards.py --status

Success Conditions:
    SC-POP-1: All 9 card types have at least 1 generation request queued
    SC-POP-2: Session queue contains Opus-allocated types (T1, T1.5, Molecule, etc.)
    SC-POP-3: API queue contains Sonnet-allocated types (T2, T3, Layer)
    SC-POP-4: After --process-all, card index has entries for all processed cards
    SC-POP-5: Overseer health report shows non-zero card counts

Author: CW (Claude/Cowork)
Date: 2026-03-04
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.qa.card_generation_orchestrator import (
    CardGenerationOrchestrator,
    GenerationRequest,
)
from src.qa.cards import CardType, CardTier, CARD_TYPE_REGISTRY
from src.qa.cards.card_types import get_card_type_spec, get_types_for_tier

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enriched Source Data Loaders
# ---------------------------------------------------------------------------
# Try enriched sources from data/card_sources/ first (produced by
# scripts/enrich_card_sources.py), falling back to original loaders.
# This ensures cards get corpus-grounded data with real findings,
# provenance, and quality-filtered fields.
# ---------------------------------------------------------------------------

ENRICHED_DIR = PROJECT_ROOT / "data" / "card_sources"


def _load_enriched_sources(card_type_dir: str) -> list:
    """Load enriched card sources from data/card_sources/{type}/ if available."""
    src_dir = ENRICHED_DIR / card_type_dir
    if not src_dir.exists():
        return []
    items = []
    for p in sorted(src_dir.glob("*.json")):
        try:
            with open(p) as f:
                data = json.load(f)
            items.append(data)
        except Exception as e:
            logger.warning(f"Failed to load enriched source {p.name}: {e}")
    if items:
        logger.info(f"Loaded {len(items)} enriched sources from {src_dir}")
    return items


def load_t1_frameworks() -> list:
    """Load T1 Framework source data — enriched first, then fallback."""
    enriched = _load_enriched_sources("t1-framework")
    if enriched:
        return enriched
    # Fallback to original loader
    path = PROJECT_ROOT / "data" / "theories" / "t1_frameworks.json"
    if not path.exists():
        logger.warning("No T1 framework data found — run scripts/enrich_card_sources.py first")
        return []
    with open(path) as f:
        return json.load(f)


def load_molecules() -> list:
    """Load Molecule source data — enriched first, then fallback."""
    enriched = _load_enriched_sources("molecule")
    if enriched:
        return enriched
    # Original fallback
    mol_dir = PROJECT_ROOT / "data" / "molecules"
    items = []
    if mol_dir.exists():
        for p in sorted(mol_dir.glob("*.json")):
            try:
                with open(p) as f:
                    data = json.load(f)
                data["entity_id"] = data.get("molecule_id", p.stem)
                items.append(data)
            except Exception as e:
                logger.warning(f"Failed to load molecule {p.name}: {e}")
    return items


def load_t2_mechanisms() -> list:
    """Load T2 Mechanism source data — enriched first, then fallback."""
    enriched = _load_enriched_sources("t2-mechanism")
    if enriched:
        return enriched
    # Original fallback
    templates_dir = PROJECT_ROOT / "data" / "templates"
    items = []
    if templates_dir.exists():
        for p in sorted(templates_dir.glob("*.json")):
            try:
                with open(p) as f:
                    data = json.load(f)
                data["entity_id"] = data.get("template_id", p.stem)
                data.setdefault("title", data.get("template_name", p.stem))
                items.append(data)
            except Exception:
                pass
    return items


def load_t3_beliefs() -> list:
    """Load T3 Belief source data — enriched first, then fallback."""
    enriched = _load_enriched_sources("t3-belief")
    if enriched:
        return enriched
    # Original fallback
    clusters_path = PROJECT_ROOT / "data" / "materialized_views" / "belief_clusters.json"
    if not clusters_path.exists():
        return []
    with open(clusters_path) as f:
        data = json.load(f)
    items = []
    for cluster in data.get("clusters", []):
        items.append({
            "entity_id": cluster.get("cluster_id", ""),
            "title": f"{cluster.get('antecedent_theme', '?')} → {cluster.get('consequent_theme', '?')}",
            "description": cluster.get("description", ""),
            "n_findings": cluster.get("n_findings", 0),
            "n_papers": cluster.get("n_papers", 0),
            "direction_consensus": cluster.get("direction_consensus", "mixed"),
            "theory_links": cluster.get("theory_links", []),
        })
    return items


def load_competitions() -> list:
    """Load Competition card source data."""
    competitions_path = PROJECT_ROOT / "data" / "competitions"
    if competitions_path.exists():
        items = []
        for p in sorted(competitions_path.glob("*.json")):
            try:
                with open(p) as f:
                    data = json.load(f)
                data["entity_id"] = data.get("competition_id", p.stem)
                items.append(data)
            except Exception:
                pass
        return items
    return []


def load_system_cards(card_type: CardType) -> list:
    """Load system card source data (Layer, Method, Math)."""
    type_name = card_type.value.split("-")[-1]  # "layer", "method", "math"
    sys_dir = PROJECT_ROOT / "data" / "system_cards" / type_name
    if sys_dir.exists():
        items = []
        for p in sorted(sys_dir.glob("*.json")):
            try:
                with open(p) as f:
                    data = json.load(f)
                data["entity_id"] = data.get("id", p.stem)
                items.append(data)
            except Exception:
                pass
        return items
    return []


# ---------------------------------------------------------------------------
# Main Population Logic
# ---------------------------------------------------------------------------

SOURCE_LOADERS = {
    CardType.T1_FRAMEWORK: load_t1_frameworks,
    CardType.T1_5_DOMAIN_THEORY: lambda: [],  # TODO: load from domain theories
    CardType.T2_MECHANISM: load_t2_mechanisms,
    CardType.MOLECULE: load_molecules,
    CardType.T3_BELIEF: load_t3_beliefs,
    CardType.COMPETITION: load_competitions,
    CardType.LAYER: lambda: load_system_cards(CardType.LAYER),
    CardType.METHOD: lambda: load_system_cards(CardType.METHOD),
    CardType.MATH: lambda: load_system_cards(CardType.MATH),
}



def populate_queue(orch: CardGenerationOrchestrator) -> dict:
    """Queue all card types for generation. Returns stats."""
    stats = {}
    for card_type, loader in SOURCE_LOADERS.items():
        spec = get_card_type_spec(card_type)
        items = loader()
        if items:
            queued = orch.queue_all_for_type(card_type, items)
        else:
            queued = 0
        stats[card_type.value] = {
            "loaded": len(items),
            "queued": queued,
            "model": spec.model_allocation,
            "expected": spec.approximate_count,
        }
        logger.info(
            f"  {card_type.value}: {len(items)} loaded, {queued} queued "
            f"(model={spec.model_allocation}, expected≈{spec.approximate_count})"
        )
    return stats


def main():
    parser = argparse.ArgumentParser(description="Populate ATLAS cards for all 9 types")
    parser.add_argument("--queue-only", action="store_true", help="Queue without processing")
    parser.add_argument("--process-sonnet", action="store_true", help="Process Sonnet-allocated cards via API")
    parser.add_argument("--process-all", action="store_true", help="Process ALL cards (costs Opus API credits)")
    parser.add_argument("--process-session", action="store_true", help="Process session-queued cards (from CW/CC)")
    parser.add_argument("--status", action="store_true", help="Show current status only")
    parser.add_argument("--max-cards", type=int, default=0, help="Max cards to process (0=all)")
    args = parser.parse_args()

    orch = CardGenerationOrchestrator(base_dir=str(PROJECT_ROOT))

    if args.status:
        report = orch.get_overseer_health_report()
        print(json.dumps(report, indent=2))
        return

    # Queue all types
    logger.info("=== Populating card generation queue ===")
    stats = populate_queue(orch)

    total_loaded = sum(s["loaded"] for s in stats.values())
    total_queued = sum(s["queued"] for s in stats.values())
    logger.info(f"\nTotal: {total_loaded} items loaded, {total_queued} queued")
    logger.info(f"Queue stats: {json.dumps(orch._queue.stats(), indent=2)}")

    if args.queue_only:
        logger.info("Queue-only mode — cards queued but not processed")
        return

    # Process based on mode
    start = time.time()
    results = []

    if args.process_sonnet:
        logger.info("\n=== Processing Sonnet-allocated cards ===")
        results = orch.process_queue(
            max_cards=args.max_cards,
            model_filter="sonnet",
        )
    elif args.process_session:
        logger.info("\n=== Processing session-queued cards (Opus) ===")
        results = orch.process_queue(
            max_cards=args.max_cards,
            session_only=True,
        )
    elif args.process_all:
        logger.info("\n=== Processing ALL cards ===")
        results = orch.process_queue(max_cards=args.max_cards)

    elapsed = time.time() - start

    # Report
    completed = sum(1 for r in results if r.status.value == "complete")
    failed = sum(1 for r in results if r.status.value in ("failed", "failed_quality"))
    logger.info(
        f"\nProcessed {len(results)} cards in {elapsed:.1f}s: "
        f"{completed} complete, {failed} failed"
    )

    # Final health report
    report = orch.get_overseer_health_report()
    logger.info(f"\nHealth report:")
    logger.info(f"  Total cards indexed: {report['total_cards']}")
    logger.info(f"  Queue remaining: {report['queue']['queued']}")
    logger.info(f"  Staleness: {report['staleness_distribution']}")


if __name__ == "__main__":
    main()
