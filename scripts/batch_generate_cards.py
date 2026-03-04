#!/usr/bin/env python3
"""
Batch Card Generation — Two-Pass with Mandatory Opus Polish
=============================================================

Generates ATLAS cards at scale using parallel API calls. Every card
gets TWO passes:

    Pass 1 (Haiku/Sonnet): Async parallel via API — extracts evidence,
        structures data, writes draft prose. Stores all structured_data
        and draft prose for Opus consumption.

    Pass 2 (Opus): Queued for CW/CC/AG sessions (free monthly allocation).
        Rewrites every tab to publication quality. Receives full Pass 1
        context: source_data + structured_data + draft prose.

No card ships without Opus polish. This is non-negotiable.

Cost-optimized Pass 1 model tiers:
  Haiku  ($0.25/$1.25 per M)  → T3 belief cards (simple, high-volume)
  Sonnet ($3/$15 per M)       → T2 mechanism, Layer, Competition,
                                 T1, T1.5, Molecule, Method, Math

Estimated costs (4,002 cards, Pass 1 only — Pass 2 is free in sessions):
  All-Haiku:   ~$19    (fast draft, Opus does the real writing)
  Tiered:      ~$28    (recommended — Sonnet for complex cards)

Usage:
    # Dry run — show what would be generated and estimated cost
    python scripts/batch_generate_cards.py --dry-run

    # Generate all cards with tiered Pass 1 models (recommended)
    python scripts/batch_generate_cards.py --tiered

    # Generate only T3 belief cards with Haiku (cheap bulk)
    python scripts/batch_generate_cards.py --type t3-belief --model haiku

    # Generate with specific concurrency
    python scripts/batch_generate_cards.py --tiered --concurrency 30

    # Resume from where you left off (skips already-generated cards)
    python scripts/batch_generate_cards.py --tiered --resume

    # Generate a small test batch first
    python scripts/batch_generate_cards.py --tiered --max-cards 20

    # Process the Opus polish queue (run from CW/CC/AG session)
    python scripts/batch_generate_cards.py --process-opus-queue

Author: CW (Claude/Cowork)
Date: 2026-03-04
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.qa.cards import CardType, CARD_TYPE_REGISTRY
from src.qa.cards.card_schema import Card, CardTab, CardBody, CardSurface, CardIceberg
from src.qa.cards.card_types import get_card_type_spec
from src.qa.card_tab_generators import (
    generate_tab_with_llm,
    TAB_GENERATOR_CONFIG,
    _build_overview_context,
    _parse_llm_response,
    _check_prose_health,
    _omega_to_confidence,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Model Tier Configuration
# ---------------------------------------------------------------------------

# Pass 1 model allocation (Pass 2 is ALWAYS Opus, queued for sessions)
BATCH_MODEL_TIERS = {
    # Haiku for simple, high-volume cards
    CardType.T3_BELIEF: "haiku",
    # Sonnet for everything else (good enough for structured extraction)
    CardType.T2_MECHANISM: "sonnet",
    CardType.LAYER: "sonnet",
    CardType.COMPETITION: "sonnet",
    CardType.T1_FRAMEWORK: "sonnet",       # Opus reserved for Pass 2
    CardType.T1_5_DOMAIN_THEORY: "sonnet", # Opus reserved for Pass 2
    CardType.MOLECULE: "sonnet",           # Opus reserved for Pass 2
    CardType.METHOD: "sonnet",             # Opus reserved for Pass 2
    CardType.MATH: "sonnet",              # Opus reserved for Pass 2
}

# Cost per million tokens by model
COST_TABLE = {
    "haiku":  {"input": 0.25,  "output": 1.25},
    "sonnet": {"input": 3.00,  "output": 15.00},
    "opus":   {"input": 15.00, "output": 75.00},
}

# Tokens per card (estimated)
TOKENS_PER_CARD = {
    "input": 7200,   # 6 tabs × ~1200 tokens each
    "output": 2400,  # 6 tabs × ~400 tokens each
}


@dataclass
class BatchConfig:
    """Configuration for a batch generation run."""
    concurrency: int = 25           # Parallel API calls
    max_cards: int = 0              # 0 = all
    card_type_filter: Optional[str] = None  # e.g., "t3-belief"
    model_override: Optional[str] = None    # Force Pass 1 to this model
    resume: bool = False            # Skip already-generated cards
    dry_run: bool = False           # Show plan, don't execute
    process_opus_queue: bool = False  # Process queued Opus polish passes


@dataclass
class BatchResult:
    """Result of a batch generation run."""
    total_attempted: int = 0
    total_completed: int = 0
    total_failed: int = 0
    total_skipped: int = 0
    opus_queued: int = 0            # Cards queued for Opus Pass 2
    opus_processed: int = 0         # Cards polished by Opus (if --process-opus-queue)
    elapsed_seconds: float = 0.0
    estimated_cost: float = 0.0
    actual_input_tokens: int = 0
    actual_output_tokens: int = 0
    errors: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Source Data Loading (reuse from populate_all_cards.py)
# ---------------------------------------------------------------------------

def load_all_source_data() -> Dict[CardType, List[Dict]]:
    """Load source data for all card types."""
    # Import loaders from populate script
    from scripts.populate_all_cards import (
        load_t1_frameworks,
        load_molecules,
        load_t2_mechanisms,
        load_t3_beliefs,
        load_competitions,
        load_system_cards,
    )

    return {
        CardType.T1_FRAMEWORK: load_t1_frameworks(),
        CardType.T1_5_DOMAIN_THEORY: [],  # TODO: domain theories
        CardType.T2_MECHANISM: load_t2_mechanisms(),
        CardType.MOLECULE: load_molecules(),
        CardType.T3_BELIEF: load_t3_beliefs(),
        CardType.COMPETITION: load_competitions(),
        CardType.LAYER: load_system_cards(CardType.LAYER),
        CardType.METHOD: load_system_cards(CardType.METHOD),
        CardType.MATH: load_system_cards(CardType.MATH),
    }


def get_card_output_path(card_type: CardType, entity_id: str) -> Path:
    """Get the output path for a generated card."""
    spec = get_card_type_spec(card_type)
    tier_dir = spec.tier.value  # "A", "B", or "C"
    return (
        PROJECT_ROOT / "data" / "materialized_views" / "cards"
        / tier_dir / card_type.value / f"{entity_id}.json"
    )


def card_already_exists(card_type: CardType, entity_id: str) -> bool:
    """Check if a card has already been generated."""
    return get_card_output_path(card_type, entity_id).exists()


# ---------------------------------------------------------------------------
# Async LLM Caller
# ---------------------------------------------------------------------------

class AsyncLLMCaller:
    """
    Async wrapper around LLM providers for parallel batch calls.

    Uses asyncio.Semaphore to limit concurrency and avoid rate limits.
    """

    def __init__(self, concurrency: int = 25):
        self.semaphore = asyncio.Semaphore(concurrency)
        self._provider = None
        self._model_configs = {}
        self._setup_providers()

    def _setup_providers(self):
        """Initialize LLM providers."""
        try:
            from src.services.llm_query_bridge import (
                AnthropicProvider, MODEL_REGISTRY
            )
            self._provider = AnthropicProvider()
            self._model_configs = MODEL_REGISTRY
        except ImportError:
            logger.warning("llm_query_bridge not available")

    async def call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str,
    ) -> Tuple[str, int, int]:
        """
        Make an async LLM call with concurrency limiting.

        Returns: (response_text, input_tokens, output_tokens)
        """
        async with self.semaphore:
            # Run the synchronous LLM call in a thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                self._sync_call,
                system_prompt,
                user_prompt,
                model,
            )

    def _sync_call(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str,
    ) -> Tuple[str, int, int]:
        """Synchronous LLM call."""
        model_key_map = {
            "opus": "claude-opus",
            "sonnet": "claude-sonnet",
            "haiku": "claude-haiku",
        }
        model_key = model_key_map.get(model, model)
        config = self._model_configs.get(model_key)

        if self._provider and config:
            try:
                return self._provider.complete(user_prompt, config, system=system_prompt)
            except Exception as e:
                logger.error(f"LLM call failed: {e}")
                # Fall through to mock

        # Mock response for testing or when no API key
        from src.qa.card_tab_generators import _mock_llm_response
        return _mock_llm_response(system_prompt, user_prompt), 500, 300


# ---------------------------------------------------------------------------
# Async Card Generator
# ---------------------------------------------------------------------------

async def generate_single_card(
    card_type: CardType,
    source_data: Dict,
    model: str,
    caller: AsyncLLMCaller,
    opus_queue: Optional[List] = None,
) -> Tuple[Optional[Card], Dict]:
    """
    Generate all tabs for a single card asynchronously (Pass 1).

    After Pass 1 completes, queues the card for Opus polish (Pass 2).
    Opus receives: original source_data + all structured_data + all draft prose.

    Args:
        card_type: Type of card to generate
        source_data: Source evidence/data for the card
        model: Pass 1 model (haiku or sonnet)
        caller: Async LLM caller with concurrency control
        opus_queue: Shared list to append Opus polish requests to

    Returns: (Card or None, stats_dict)
    """
    entity_id = source_data.get("entity_id", "unknown")
    spec = get_card_type_spec(card_type)
    all_tabs = spec.required_tabs | spec.optional_tabs
    stats = {
        "entity_id": entity_id,
        "card_type": card_type.value,
        "model": model,
        "input_tokens": 0,
        "output_tokens": 0,
        "tabs_generated": 0,
        "tabs_failed": 0,
        "elapsed_ms": 0,
        "opus_queued": False,
    }

    start = time.time()

    # Generate all tabs concurrently
    tab_tasks = []
    for tab_name in sorted(all_tabs):
        if tab_name == "history":
            continue
        if tab_name not in TAB_GENERATOR_CONFIG:
            continue
        tab_tasks.append(_generate_tab_async(tab_name, card_type, entity_id, source_data, model, caller))

    tab_results = await asyncio.gather(*tab_tasks, return_exceptions=True)

    # Collect results
    tabs_dict = {}
    for result in tab_results:
        if isinstance(result, Exception):
            logger.error(f"Tab generation error for {entity_id}: {result}")
            stats["tabs_failed"] += 1
            continue
        if result is None:
            stats["tabs_failed"] += 1
            continue

        tab, input_tok, output_tok = result
        tabs_dict[tab.tab_name] = tab
        stats["input_tokens"] += input_tok
        stats["output_tokens"] += output_tok
        stats["tabs_generated"] += 1

    # Add history tab (not LLM-generated)
    if "history" in all_tabs:
        from src.qa.card_tab_generators import _generate_history_tab
        history_result = _generate_history_tab(entity_id, source_data, int(time.time() * 1000))
        if history_result.tab:
            tabs_dict["history"] = history_result.tab
            stats["tabs_generated"] += 1

    stats["elapsed_ms"] = int((time.time() - start) * 1000)

    if not tabs_dict:
        return None, stats

    # Build card
    try:
        from src.qa.cards.card_schema import (
            create_card, CardSurface, CardBody, CardIceberg,
            IcebergSourceMap, IcebergAgentContext, IcebergQualityScores,
        )

        # Surface
        omega = source_data.get("omega", source_data.get("confidence_omega", 0.5))
        surface = CardSurface(
            title=source_data.get("title", entity_id),
            card_type=card_type,
            confidence_omega=omega,
            confidence_label=_omega_to_confidence(omega),
            n_findings=source_data.get("n_findings", 0),
            n_papers=source_data.get("n_papers", 0),
        )

        # Body
        body = CardBody(tabs=tabs_dict)

        # Iceberg
        iceberg = CardIceberg(
            source_map=IcebergSourceMap(),
            agent_context=IcebergAgentContext(
                agent_id="batch_generate_cards_pass1",
                model_used=model,
                token_count_input=stats["input_tokens"],
                token_count_output=stats["output_tokens"],
                generation_duration_ms=stats["elapsed_ms"],
            ),
            quality_scores=IcebergQualityScores(),
        )

        card = create_card(
            card_type=card_type,
            entity_id=entity_id,
            surface=surface,
            body=body,
            iceberg=iceberg,
        )

        # Save Pass 1 to disk
        output_path = get_card_output_path(card_type, entity_id)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        card.save(output_path)

        # ---------------------------------------------------------------
        # Queue Opus polish (Pass 2) — MANDATORY for every card
        # ---------------------------------------------------------------
        # Opus receives the full context: original source_data, PLUS all
        # structured_data extracted by Pass 1, PLUS all draft prose.
        # This is the "extra material in an appendix" that Opus uses to
        # rewrite to publication quality.
        # ---------------------------------------------------------------
        opus_request = {
            "card_type": card_type,
            "entity_id": entity_id,
            "source_data": {
                **source_data,
                "_pass": 2,
                "_pass1_card_id": card.card_id if hasattr(card, "card_id") else entity_id,
                "_pass1_structured_data": {
                    tab_name: tab.structured_data
                    for tab_name, tab in tabs_dict.items()
                    if tab.structured_data
                },
                "_pass1_prose": {
                    tab_name: tab.prose
                    for tab_name, tab in tabs_dict.items()
                },
            },
            "priority": 2,  # Higher priority for polish
        }

        if opus_queue is not None:
            opus_queue.append(opus_request)
            stats["opus_queued"] = True

        return card, stats

    except Exception as e:
        logger.error(f"Card assembly failed for {entity_id}: {e}")
        return None, stats


async def _generate_tab_async(
    tab_name: str,
    card_type: CardType,
    entity_id: str,
    source_data: Dict,
    model: str,
    caller: AsyncLLMCaller,
) -> Optional[Tuple[CardTab, int, int]]:
    """Generate a single tab using async LLM call."""
    system_prompt, context_builder = TAB_GENERATOR_CONFIG[tab_name]
    user_prompt = context_builder(source_data, card_type)
    user_prompt += (
        f"\n\nWrite the {tab_name.upper()} tab for this entity. "
        f"Follow all norms in the system prompt. "
        f"If you include a structured data block, wrap it in ```json ... ``` markers."
    )

    try:
        response_text, input_tokens, output_tokens = await caller.call_llm(
            system_prompt, user_prompt, model
        )

        prose, structured_data = _parse_llm_response(response_text)
        prose_health = _check_prose_health(prose)

        if prose_health < 3.0 and prose:
            prose = f"[DRAFT — prose_health={prose_health:.1f}] {prose}"

        tab = CardTab(
            tab_name=tab_name,
            prose=prose,
            structured_data=structured_data,
        )

        return tab, input_tokens, output_tokens

    except Exception as e:
        logger.error(f"Tab {tab_name} generation failed for {entity_id}: {e}")
        return None


# ---------------------------------------------------------------------------
# Batch Orchestration
# ---------------------------------------------------------------------------

def _queue_opus_polish(opus_requests: List[Dict], base_dir: str) -> int:
    """
    Queue all Opus polish requests through the CardGenerationOrchestrator.

    This persists the queue so it survives across sessions. The next
    CW/CC/AG session calls --process-opus-queue to execute the polish.
    """
    from src.qa.card_generation_orchestrator import (
        CardGenerationOrchestrator,
        GenerationRequest,
    )

    orch = CardGenerationOrchestrator(base_dir=base_dir)
    queued = 0

    for req in opus_requests:
        gen_request = GenerationRequest(
            card_type=req["card_type"],
            entity_id=req["entity_id"],
            source_data=req["source_data"],
            priority=req.get("priority", 2),
            requested_by="batch_pass2_polish",
            session_mode=True,  # Queue for CW/CC/AG session (free Opus)
            force_model="opus",
        )
        orch._queue.enqueue(gen_request)
        queued += 1

    orch._save_queue_state()
    logger.info(f"Queued {queued} cards for Opus polish (Pass 2)")
    return queued


def _process_opus_queue(base_dir: str, max_cards: int = 0) -> int:
    """
    Process the Opus polish queue. Run this from a CW/CC/AG session.

    Returns number of cards polished.
    """
    from src.qa.card_generation_orchestrator import CardGenerationOrchestrator
    from src.qa.card_tab_generators import register_llm_generators

    orch = CardGenerationOrchestrator(base_dir=base_dir)
    register_llm_generators(orch)

    results = orch.process_polish_queue(max_cards=max_cards)
    completed = sum(1 for r in results if r.status.value == "complete")
    failed = sum(1 for r in results if r.status.value in ("failed", "failed_quality"))

    logger.info(f"Opus polish: {completed} complete, {failed} failed out of {len(results)}")
    return completed


async def run_batch(config: BatchConfig) -> BatchResult:
    """
    Run the full batch generation (Pass 1) and queue Opus polish (Pass 2).

    Architecture:
        1. Async parallel Pass 1 (Haiku/Sonnet) — extracts evidence, structures data
        2. Queue every card for Pass 2 (Opus) — persisted in orchestrator queue
        3. Pass 2 runs later in CW/CC/AG session via --process-opus-queue
    """
    result = BatchResult()
    start = time.time()

    # Handle Opus queue processing mode
    if config.process_opus_queue:
        logger.info("Processing Opus polish queue (Pass 2)...")
        result.opus_processed = _process_opus_queue(
            str(PROJECT_ROOT), max_cards=config.max_cards
        )
        result.elapsed_seconds = time.time() - start
        return result

    # Load source data
    logger.info("Loading source data for all card types...")
    all_data = load_all_source_data()

    # Build work items
    work_items: List[Tuple[CardType, Dict, str]] = []

    for card_type, items in all_data.items():
        if not items:
            continue

        # Filter by type if specified
        if config.card_type_filter and card_type.value != config.card_type_filter:
            continue

        # Determine Pass 1 model (never Opus — that's reserved for Pass 2)
        if config.model_override:
            model = config.model_override
            if model == "opus":
                model = "sonnet"  # Opus is for Pass 2 only
        else:
            model = BATCH_MODEL_TIERS.get(card_type, "sonnet")

        for item in items:
            entity_id = item.get("entity_id", "unknown")

            # Skip already-generated cards in resume mode
            if config.resume and card_already_exists(card_type, entity_id):
                result.total_skipped += 1
                continue

            work_items.append((card_type, item, model))

    # Apply max_cards limit
    if config.max_cards > 0:
        work_items = work_items[:config.max_cards]

    # Cost estimate (Pass 1 only — Pass 2 is free in sessions)
    cost_estimate = estimate_cost(work_items)
    result.estimated_cost = cost_estimate["total"]

    # Report plan
    logger.info(f"\n{'='*60}")
    logger.info(f"BATCH GENERATION PLAN (Pass 1 + Opus Queue)")
    logger.info(f"{'='*60}")
    logger.info(f"  Cards to generate (Pass 1): {len(work_items)}")
    logger.info(f"  Cards skipped:              {result.total_skipped}")
    logger.info(f"  Concurrency:                {config.concurrency}")
    logger.info(f"  Pass 1 est. cost:           ${cost_estimate['total']:.2f}")
    logger.info(f"  Pass 2 (Opus polish):       FREE (queued for CW/CC/AG session)")
    logger.info(f"  Breakdown:")
    for model_name, count in cost_estimate["by_model"].items():
        model_cost = cost_estimate["cost_by_model"].get(model_name, 0)
        logger.info(f"    {model_name}: {count} cards → ${model_cost:.2f}")
    logger.info(f"{'='*60}\n")

    if config.dry_run:
        logger.info("DRY RUN — no cards generated")
        result.opus_queued = len(work_items)  # Would queue this many
        return result

    # Execute Pass 1
    result.total_attempted = len(work_items)
    caller = AsyncLLMCaller(concurrency=config.concurrency)
    opus_queue: List[Dict] = []  # Collects Opus polish requests

    # Process in chunks for progress reporting
    chunk_size = max(10, config.concurrency)
    for i in range(0, len(work_items), chunk_size):
        chunk = work_items[i:i + chunk_size]
        tasks = [
            generate_single_card(card_type, source_data, model, caller, opus_queue)
            for card_type, source_data, model in chunk
        ]

        chunk_results = await asyncio.gather(*tasks, return_exceptions=True)

        for cr in chunk_results:
            if isinstance(cr, Exception):
                result.total_failed += 1
                result.errors.append(str(cr))
                continue

            card, stats = cr
            if card:
                result.total_completed += 1
                result.actual_input_tokens += stats["input_tokens"]
                result.actual_output_tokens += stats["output_tokens"]
            else:
                result.total_failed += 1

        # Progress
        done = min(i + chunk_size, len(work_items))
        pct = done / len(work_items) * 100
        logger.info(
            f"  Progress: {done}/{len(work_items)} ({pct:.0f}%) — "
            f"{result.total_completed} complete, {result.total_failed} failed"
        )

    # Queue ALL completed cards for Opus polish (Pass 2)
    if opus_queue:
        logger.info(f"\nQueuing {len(opus_queue)} cards for Opus polish (Pass 2)...")
        result.opus_queued = _queue_opus_polish(opus_queue, str(PROJECT_ROOT))
    else:
        logger.info("\nNo cards to queue for Opus polish (all failed?)")

    result.elapsed_seconds = time.time() - start
    return result


def estimate_cost(work_items: List[Tuple[CardType, Dict, str]]) -> Dict:
    """Estimate cost for a batch of work items."""
    by_model = {}
    cost_by_model = {}

    for card_type, item, model in work_items:
        by_model[model] = by_model.get(model, 0) + 1

    total = 0.0
    for model, count in by_model.items():
        costs = COST_TABLE.get(model, COST_TABLE["sonnet"])
        input_cost = (count * TOKENS_PER_CARD["input"] / 1_000_000) * costs["input"]
        output_cost = (count * TOKENS_PER_CARD["output"] / 1_000_000) * costs["output"]
        model_cost = input_cost + output_cost
        cost_by_model[model] = model_cost
        total += model_cost

    return {
        "total": total,
        "by_model": by_model,
        "cost_by_model": cost_by_model,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Batch generate ATLAS cards: Pass 1 (Haiku/Sonnet) via API, "
            "then queue every card for Opus polish (Pass 2)"
        )
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show plan and estimated cost without generating"
    )
    parser.add_argument(
        "--tiered", action="store_true",
        help="Use cost-optimized Pass 1 tiers (Haiku for T3, Sonnet for rest)"
    )
    parser.add_argument(
        "--type", dest="card_type",
        help="Generate only this card type (e.g., t3-belief, t2-mechanism)"
    )
    parser.add_argument(
        "--model",
        choices=["haiku", "sonnet"],
        help="Force all Pass 1 cards to use this model (Opus reserved for Pass 2)"
    )
    parser.add_argument(
        "--concurrency", type=int, default=25,
        help="Number of parallel API calls (default: 25)"
    )
    parser.add_argument(
        "--max-cards", type=int, default=0,
        help="Maximum number of cards to generate (0 = all)"
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="Skip already-generated cards"
    )
    parser.add_argument(
        "--process-opus-queue", action="store_true",
        help="Process queued Opus polish passes (run from CW/CC/AG session)"
    )

    args = parser.parse_args()

    config = BatchConfig(
        concurrency=args.concurrency,
        max_cards=args.max_cards,
        card_type_filter=args.card_type,
        model_override=args.model,
        resume=args.resume,
        dry_run=args.dry_run,
        process_opus_queue=args.process_opus_queue,
    )

    # Sanity check
    if not args.process_opus_queue and not args.tiered and not args.model and not args.card_type:
        logger.info("Two-pass architecture: every card gets Opus polish.")
        logger.info("  Step 1: python scripts/batch_generate_cards.py --tiered")
        logger.info("          (Pass 1 via API — Haiku/Sonnet, ~$28)")
        logger.info("  Step 2: python scripts/batch_generate_cards.py --process-opus-queue")
        logger.info("          (Pass 2 from CW/CC/AG session — free Opus)")
        logger.info("")

    # If --tiered but no other flags, enable it
    if args.tiered and not args.model:
        config.model_override = None  # Use BATCH_MODEL_TIERS

    result = asyncio.run(run_batch(config))

    # Final report
    print(f"\n{'='*60}")
    if config.process_opus_queue:
        print(f"OPUS POLISH COMPLETE")
        print(f"{'='*60}")
        print(f"  Cards polished: {result.opus_processed}")
    else:
        print(f"BATCH GENERATION COMPLETE (Pass 1)")
        print(f"{'='*60}")
        print(f"  Pass 1 attempted:  {result.total_attempted}")
        print(f"  Pass 1 completed:  {result.total_completed}")
        print(f"  Pass 1 failed:     {result.total_failed}")
        print(f"  Skipped:           {result.total_skipped}")
        print(f"  Opus queued:       {result.opus_queued}")
        print(f"  Pass 1 cost:       ${result.estimated_cost:.2f}")
    print(f"  Time:              {result.elapsed_seconds:.1f}s")
    if result.actual_input_tokens > 0:
        print(f"  Tokens in:         {result.actual_input_tokens:,}")
        print(f"  Tokens out:        {result.actual_output_tokens:,}")
    if result.errors:
        print(f"  Errors ({len(result.errors)}):")
        for err in result.errors[:5]:
            print(f"    - {err[:100]}")
    if result.opus_queued and not config.process_opus_queue:
        print(f"\n  Next step: process Opus polish queue:")
        print(f"    python scripts/batch_generate_cards.py --process-opus-queue")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
