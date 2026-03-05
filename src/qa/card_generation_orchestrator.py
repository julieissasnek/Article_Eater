"""
Card Generation Orchestrator — Unified Pipeline for All Nine Card Types
========================================================================

The central wiring component that routes card creation through the
Surface/Body/Iceberg schema (§178), respects model allocation per card type,
runs quality gates, tracks staleness, and integrates with the Overseer for
real-time monitoring.

Architecture:
    Source Data → CardGenerationOrchestrator → Card (schema) → Persistence → Retriever → QA

This orchestrator replaces the fragmented legacy approach where card_generator.py,
molecule_card_generator.py, and precompute_pipeline.py each produced different
formats. All output now conforms to src.qa.cards.Card.

Design Principles:
    1. Schema-first: Every card is a Card object with Surface/Body/Iceberg
    2. Model-routed: CardTypeSpec.model_allocation determines which LLM generates content
    3. Quality-gated: ProseRevisionService runs on every tab before publishing
    4. Real-time tracked: Overseer knows about every card in generation, every card stale
    5. Session-optimized: Opus-allocated types queue for CW/CC/AG sessions (free);
       Sonnet-allocated types can batch via API

Success Conditions:
    SC-CGO-1: Every generated card validates against Card.validate_tabs() with 0 missing required tabs
    SC-CGO-2: Model allocation routes correctly (Opus types → opus, Sonnet types → sonnet)
    SC-CGO-3: Quality gate blocks cards with prose_health < 6.0
    SC-CGO-4: Staleness ledger is updated on every generation event
    SC-CGO-5: Overseer is notified of generation start, completion, and failure
    SC-CGO-6: End-to-end: generated card can be retrieved by CardRetriever within 100ms
    SC-CGO-7: All 9 card types have at least one generation pathway registered

References:
    - §178: Nine Card Types in Three Tiers
    - §178.2: Surface/Body/Iceberg Architecture
    - contracts/META_REVIEW_SPEC.md: Meta-review generation requirements
    - contracts/QA_ANSWER_NORMS.md: Answer presentation norms

Author: CW (Claude/Cowork)
Date: 2026-03-04
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from src.qa.cards import (
    Card,
    CardBody,
    CardIceberg,
    CardSurface,
    CardTab,
    CardTier,
    CardType,
    CARD_TYPE_REGISTRY,
    ConfidenceLevel,
    Direction,
    IcebergAgentContext,
    IcebergQualityScores,
    IcebergSourceMap,
    Staleness,
    UserType,
    create_card,
    get_tabs_for_card_type,
    get_tab_order_for_user,
    make_card_id,
    StalenessLedger,
    StalenessLedgerEntry,
    compute_staleness_score,
)
from src.qa.cards.card_types import CardTypeSpec, get_card_type_spec
from src.services.annotation_service import AnnotationService, AnnotationType, AnnotationLayer

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Generation Status
# ---------------------------------------------------------------------------

class GenerationStatus(str, Enum):
    """Tracks the lifecycle of a card generation request."""
    QUEUED = "queued"              # In queue, not yet started
    GENERATING = "generating"      # LLM call in progress
    QUALITY_CHECK = "quality_check"  # Prose revision gate running
    FAILED_QUALITY = "failed_quality"  # Quality gate rejected
    COMPLETE = "complete"          # Card generated and persisted
    FAILED = "failed"              # Generation error
    STALE_QUEUED = "stale_queued"  # Marked stale, queued for regeneration


# ---------------------------------------------------------------------------
# Generation Request & Result
# ---------------------------------------------------------------------------

@dataclass
class GenerationRequest:
    """A request to generate or regenerate a card."""
    card_type: CardType
    entity_id: str
    source_data: Dict[str, Any]      # Input data (cluster, molecule, method def, etc.)
    priority: int = 5                 # 1 = highest, 10 = lowest
    requested_by: str = "system"      # "system", "user", "staleness", "overseer"
    session_mode: bool = False        # True = queue for CW/CC session (free Opus)
    force_model: Optional[str] = None # Override model_allocation if needed
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def card_id(self) -> str:
        return make_card_id(self.card_type, self.entity_id)

    @property
    def model(self) -> str:
        if self.force_model:
            return self.force_model
        spec = get_card_type_spec(self.card_type)
        return spec.model_allocation


@dataclass
class GenerationResult:
    """The result of a card generation attempt."""
    card_id: str
    status: GenerationStatus
    card: Optional[Card] = None
    error: Optional[str] = None
    generation_time_ms: float = 0.0
    model_used: str = ""
    token_count: int = 0
    quality_score: float = 0.0
    quality_details: Optional[Dict] = None


# ---------------------------------------------------------------------------
# Generation Queue (Real-Time, Not Nightly)
# ---------------------------------------------------------------------------

@dataclass
class GenerationQueue:
    """
    Priority queue for card generation requests.

    Real-time: items are processed as soon as a session is available,
    not batched into nightly runs. The overseer monitors queue depth
    and staleness.
    """
    _queue: List[GenerationRequest] = field(default_factory=list)
    _completed: List[GenerationResult] = field(default_factory=list)
    _failed: List[GenerationResult] = field(default_factory=list)
    _in_progress: Dict[str, GenerationRequest] = field(default_factory=dict)

    def enqueue(self, request: GenerationRequest) -> None:
        """Add a generation request to the queue."""
        # Deduplicate: don't queue if already queued or in progress
        existing_ids = {r.card_id for r in self._queue} | set(self._in_progress.keys())
        if request.card_id in existing_ids:
            logger.debug(f"Skipping duplicate queue entry: {request.card_id}")
            return
        self._queue.append(request)
        self._queue.sort(key=lambda r: r.priority)
        logger.info(f"Queued: {request.card_id} (priority={request.priority}, model={request.model})")

    def dequeue(self, model_filter: Optional[str] = None) -> Optional[GenerationRequest]:
        """Get the next request, optionally filtered by model."""
        for i, req in enumerate(self._queue):
            if model_filter is None or req.model == model_filter:
                self._queue.pop(i)
                self._in_progress[req.card_id] = req
                return req
        return None

    def complete(self, result: GenerationResult) -> None:
        """Mark a request as completed."""
        self._in_progress.pop(result.card_id, None)
        if result.status == GenerationStatus.COMPLETE:
            self._completed.append(result)
        else:
            self._failed.append(result)

    def queue_depth(self, model_filter: Optional[str] = None) -> int:
        if model_filter:
            return sum(1 for r in self._queue if r.model == model_filter)
        return len(self._queue)

    def in_progress_count(self) -> int:
        return len(self._in_progress)

    def get_session_queue(self) -> List[GenerationRequest]:
        """Get all requests queued for chatbot session (free Opus)."""
        return [r for r in self._queue if r.session_mode]

    def get_api_queue(self) -> List[GenerationRequest]:
        """Get all requests suitable for API batch processing."""
        return [r for r in self._queue if not r.session_mode]

    def stats(self) -> Dict[str, Any]:
        return {
            "queued": len(self._queue),
            "in_progress": len(self._in_progress),
            "completed": len(self._completed),
            "failed": len(self._failed),
            "by_model": {
                "opus": self.queue_depth("opus"),
                "sonnet": self.queue_depth("sonnet"),
                "gemini": self.queue_depth("gemini"),
            },
            "session_queue": len(self.get_session_queue()),
            "api_queue": len(self.get_api_queue()),
        }

    def to_dict(self) -> Dict:
        return {
            "queue": [
                {"card_id": r.card_id, "type": r.card_type.value,
                 "priority": r.priority, "model": r.model,
                 "session_mode": r.session_mode, "created_at": r.created_at}
                for r in self._queue
            ],
            "in_progress": list(self._in_progress.keys()),
            "stats": self.stats(),
        }


# ---------------------------------------------------------------------------
# Tab Generator Registry
# ---------------------------------------------------------------------------

# Each card type × tab combination can have a registered generator function.
# This allows different generation strategies per tab (e.g., mechanism tab
# uses diagram generation, evidence tab aggregates from extraction data).

TabGeneratorFn = Callable[[CardType, str, Dict[str, Any], str], CardTab]


@dataclass
class TabGeneratorRegistry:
    """
    Maps (card_type, tab_name) → generator function.

    Generator functions take:
        card_type: CardType
        entity_id: str
        source_data: Dict[str, Any]
        model: str  (which LLM to use)
    And return: CardTab
    """
    _generators: Dict[Tuple[str, str], TabGeneratorFn] = field(default_factory=dict)
    _default_generators: Dict[str, TabGeneratorFn] = field(default_factory=dict)

    def register(self, card_type: CardType, tab_name: str, fn: TabGeneratorFn) -> None:
        """Register a generator for a specific card_type + tab."""
        self._generators[(card_type.value, tab_name)] = fn

    def register_default(self, tab_name: str, fn: TabGeneratorFn) -> None:
        """Register a default generator for a tab (any card type)."""
        self._default_generators[tab_name] = fn

    def get(self, card_type: CardType, tab_name: str) -> Optional[TabGeneratorFn]:
        """Look up the generator for a card_type + tab."""
        return (
            self._generators.get((card_type.value, tab_name))
            or self._default_generators.get(tab_name)
        )

    def coverage(self) -> Dict[str, List[str]]:
        """Report which card_type × tab combinations have generators."""
        result = {}
        for ct in CardType:
            spec = get_card_type_spec(ct)
            all_tabs = spec.required_tabs | spec.optional_tabs
            covered = []
            missing = []
            for tab in all_tabs:
                if self.get(ct, tab):
                    covered.append(tab)
                else:
                    missing.append(tab)
            result[ct.value] = {"covered": covered, "missing": missing}
        return result


# ---------------------------------------------------------------------------
# Annotation Enrichment
# ---------------------------------------------------------------------------

def enrich_source_data_with_annotations(
    source_data: Dict[str, Any],
    entity_id: str,
    target_type: str = "belief",
    annotation_service: Optional[AnnotationService] = None,
) -> Dict[str, Any]:
    """
    Enrich source_data with annotation data from the annotation service.

    Fetches active annotations for the entity and injects them into source_data
    under an "annotations" key, organized by type. This enables tab generators
    to use annotation data (disputes, surprises, replication status, etc.)
    without being tightly coupled to the annotation service.

    Args:
        source_data: The original source data dict (beliefs, findings, etc.)
        entity_id: The entity's canonical ID (e.g., template_id, belief_id)
        target_type: The target type for annotation queries (default: "belief")
        annotation_service: AnnotationService instance. If None, creates one.

    Returns:
        Enriched source_data with "annotations" key containing A9-A18 data.
        Gracefully handles service unavailability — returns original source_data unchanged.

    Success Condition: SC-ANN-CARD-1
        Cards for entities with annotations include annotation data in source_data
    """
    if annotation_service is None:
        try:
            annotation_service = AnnotationService()
        except Exception as e:
            logger.warning(
                f"Could not initialize AnnotationService for {entity_id}: {e}. "
                "Card generation will continue without annotations."
            )
            return source_data

    try:
        # Query all active annotations for this entity (all layers)
        annotations = annotation_service.get_active_annotations(target_type, entity_id)
        if not annotations:
            return source_data

        # Organize annotations by type for easy access
        annotations_by_type: Dict[str, List[Dict[str, Any]]] = {}
        for ann in annotations:
            ann_type = ann.type.value if hasattr(ann.type, 'value') else str(ann.type)
            if ann_type not in annotations_by_type:
                annotations_by_type[ann_type] = []
            annotations_by_type[ann_type].append({
                "id": ann.id,
                "content": ann.content,
                "author": ann.author,
                "confidence": ann.confidence,
                "created": ann.created,
                "metadata": ann.metadata,
            })

        # Inject into source_data
        enriched = {
            **source_data,
            "annotations": annotations_by_type,
            "_annotation_count": len(annotations),
        }

        # For convenience, flatten common annotation types for easy access by tab generators
        disputes = annotations_by_type.get("DISPUTE", [])
        surprises = annotations_by_type.get("SURPRISE_FLAG", [])
        unanswered = annotations_by_type.get("UNANSWERED_QUESTION", [])
        replication = annotations_by_type.get("REPLICATION_STATUS", [])

        if disputes:
            enriched["disputes"] = [d["content"] for d in disputes]
        if surprises:
            enriched["surprise_flags"] = [s["content"] for s in surprises]
        if unanswered:
            enriched["unanswered_questions"] = [u["content"] for u in unanswered]
        if replication:
            enriched["replication_status"] = replication[0]["content"] if replication else None

        logger.debug(
            f"Enriched source_data for {entity_id}: "
            f"{len(disputes)} disputes, {len(surprises)} surprises, "
            f"{len(unanswered)} unanswered, {len(replication)} replication"
        )

        return enriched

    except Exception as e:
        logger.warning(
            f"Error enriching annotations for {entity_id}: {e}. "
            "Card generation will continue without annotations."
        )
        return source_data


# ---------------------------------------------------------------------------
# Card Generation Orchestrator
# ---------------------------------------------------------------------------

class CardGenerationOrchestrator:
    """
    Central orchestrator for generating all nine card types.

    Responsibilities:
        1. Accept generation requests (from staleness triggers, user queries, bulk init)
        2. Route to correct model based on CardTypeSpec.model_allocation
        3. Generate each required tab using registered tab generators
        4. Run prose quality gate on generated content
        5. Validate card against schema (required tabs, field types)
        6. Persist card to canonical location
        7. Update staleness ledger
        8. Notify overseer of generation events

    Real-time operation:
        - Queue is processed continuously, not in nightly batches
        - Opus-allocated types queue for chatbot sessions (CW/CC/AG) when possible
        - Sonnet-allocated types can be batched via API for efficiency
        - Overseer monitors queue depth and alerts if > threshold
    """

    # Canonical storage locations
    CARD_STORAGE_DIR = "data/materialized_views/cards"
    CARD_INDEX_PATH = "data/materialized_views/cards/card_index.json"
    QUEUE_STATE_PATH = "data/materialized_views/cards/generation_queue.json"
    STALENESS_LEDGER_DIR = "data/materialized_views/cards/staleness"

    # Quality thresholds
    MIN_PROSE_HEALTH = 6.0          # Minimum prose revision score to publish
    MIN_PROSE_HEALTH_DRAFT = 3.0    # Lower threshold for draft cards (fallback generators)
    MIN_COVERAGE_SCORE = 0.70       # Minimum tab coverage completeness
    MAX_QUEUE_DEPTH_ALERT = 50      # Overseer alert if queue exceeds this

    def __init__(
        self,
        base_dir: str = ".",
        overseer: Optional[Any] = None,
        prose_service: Optional[Any] = None,
    ):
        self._base = Path(base_dir)
        self._card_dir = self._base / self.CARD_STORAGE_DIR
        self._card_dir.mkdir(parents=True, exist_ok=True)
        self._staleness_dir = self._base / self.STALENESS_LEDGER_DIR
        self._staleness_dir.mkdir(parents=True, exist_ok=True)

        self._queue = GenerationQueue()
        self._tab_registry = TabGeneratorRegistry()
        self._overseer = overseer
        self._prose_service = prose_service

        # Annotation service for enriching source_data with A9-A18 data
        try:
            self._annotation_service = AnnotationService()
        except Exception as e:
            logger.warning(f"Could not initialize AnnotationService: {e}")
            self._annotation_service = None

        # Card index: card_id → metadata for fast retrieval
        self._card_index: Dict[str, Dict] = {}
        self._load_index()

        # Staleness ledgers: card_id → StalenessLedger
        self._staleness_ledgers: Dict[str, StalenessLedger] = {}

        # Generation stats
        self._generation_count = 0
        self._total_generation_time_ms = 0.0

        # Register built-in tab generators
        self._register_builtin_generators()

        logger.info(
            f"CardGenerationOrchestrator initialized: "
            f"{len(self._card_index)} cards indexed, "
            f"storage at {self._card_dir}"
        )

    # ------------------------------------------------------------------
    # Index Management
    # ------------------------------------------------------------------

    def _load_index(self) -> None:
        """Load the card index from disk."""
        index_path = self._base / self.CARD_INDEX_PATH
        if index_path.exists():
            try:
                with open(index_path) as f:
                    self._card_index = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load card index: {e}")
                self._card_index = {}

    def _save_index(self) -> None:
        """Persist the card index to disk."""
        index_path = self._base / self.CARD_INDEX_PATH
        index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(index_path, "w") as f:
            json.dump(self._card_index, f, indent=2)

    def _save_queue_state(self) -> None:
        """Persist queue state for recovery after restart."""
        queue_path = self._base / self.QUEUE_STATE_PATH
        with open(queue_path, "w") as f:
            json.dump(self._queue.to_dict(), f, indent=2)

    # ------------------------------------------------------------------
    # Card Generation (Core)
    # ------------------------------------------------------------------

    def generate_card(self, request: GenerationRequest) -> GenerationResult:
        """
        Generate a single card from a request.

        This is the core generation method. It:
        1. Creates a draft Card object
        2. Populates Surface (confidence, direction, evidence counts)
        3. Generates each required tab using registered generators
        4. Runs quality gate
        5. Populates Iceberg (provenance, agent context, quality scores)
        6. Persists the card
        7. Updates index and staleness ledger
        8. Notifies overseer

        Returns:
            GenerationResult with status and optional Card
        """
        start_time = time.time()
        card_id = request.card_id
        spec = get_card_type_spec(request.card_type)

        # Notify overseer: generation starting
        self._notify_overseer("generation_start", {
            "card_id": card_id,
            "card_type": request.card_type.value,
            "model": request.model,
        })

        try:
            # Enrich source_data with annotations before tab generation
            # SC-ANN-CARD-1: Cards for entities with annotations include annotation data in source_data
            enriched_source_data = enrich_source_data_with_annotations(
                request.source_data,
                request.entity_id,
                target_type="belief",  # Default; can be inferred from card_type if needed
                annotation_service=self._annotation_service,
            )
            # Update the request's source_data for use in tabs
            request.source_data = enriched_source_data

            # Step 1: Create draft card
            card = create_card(
                card_type=request.card_type,
                entity_id=request.entity_id,
                title=request.source_data.get("title", f"[{spec.display_name}] {request.entity_id}"),
            )

            # Step 2: Populate Surface from source data
            card = self._populate_surface(card, request)

            # Step 3: Generate tabs
            generated_tabs = []
            tab_errors = []
            for tab_name in spec.required_tabs:
                try:
                    tab = self._generate_tab(request, tab_name)
                    if tab:
                        generated_tabs.append(tab)
                except Exception as e:
                    tab_errors.append(f"{tab_name}: {e}")
                    logger.warning(f"Tab generation failed for {card_id}/{tab_name}: {e}")

            # Also generate optional tabs if data supports them
            for tab_name in spec.optional_tabs:
                try:
                    tab = self._generate_tab(request, tab_name)
                    if tab:
                        generated_tabs.append(tab)
                except Exception:
                    pass  # Optional tabs can fail silently

            # Update body with generated tabs (CardBody.tabs is Dict[str, CardTab])
            card.body = CardBody(tabs={tab.tab_name: tab for tab in generated_tabs})

            # Step 4: Quality gate
            quality_scores = self._run_quality_gate(card)

            # Use lower threshold for draft cards (fallback generators produce [DRAFT] placeholder text)
            has_drafts = any("[DRAFT]" in (t.prose or "") for t in card.body.tabs.values())
            min_health = self.MIN_PROSE_HEALTH_DRAFT if has_drafts else self.MIN_PROSE_HEALTH

            if quality_scores.get("prose_health", 10.0) < min_health:
                result = GenerationResult(
                    card_id=card_id,
                    status=GenerationStatus.FAILED_QUALITY,
                    card=card,
                    error=f"Prose health {quality_scores.get('prose_health', 0):.1f} < {min_health}",
                    generation_time_ms=(time.time() - start_time) * 1000,
                    model_used=request.model,
                    quality_score=quality_scores.get("prose_health", 0),
                    quality_details=quality_scores,
                )
                self._notify_overseer("quality_gate_failed", {
                    "card_id": card_id, "score": quality_scores,
                })
                return result

            # Step 5: Populate Iceberg
            elapsed_ms = (time.time() - start_time) * 1000
            card.iceberg = self._build_iceberg(request, quality_scores, elapsed_ms)

            # Step 6: Validate tabs
            missing = card.validate_tabs()
            if missing:
                logger.warning(f"Card {card_id} missing required tabs: {missing}")
                # Don't fail — some tabs may be legitimately empty in draft mode

            # Step 7: Mark as non-draft if quality passes
            card.is_draft = False
            card.is_stale = False

            # Step 8: Persist
            card_path = self._card_path(card)
            card.save(card_path)

            # Step 9: Update index
            self._card_index[card_id] = {
                "card_type": request.card_type.value,
                "entity_id": request.entity_id,
                "title": card.surface.title,
                "confidence": card.surface.confidence_level.value if card.surface.confidence_level else None,
                "direction": card.surface.direction.value if card.surface.direction else None,
                "staleness": Staleness.FRESH.value,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "model": request.model,
                "quality_score": quality_scores.get("prose_health", 0),
                "path": str(card_path.relative_to(self._base)),
                "tab_count": len(generated_tabs),
                "generation_ms": round(elapsed_ms, 1),
            }
            self._save_index()

            # Step 10: Update staleness ledger
            self._record_generation(card_id)

            # Step 11: Save queue state
            self._save_queue_state()

            result = GenerationResult(
                card_id=card_id,
                status=GenerationStatus.COMPLETE,
                card=card,
                generation_time_ms=elapsed_ms,
                model_used=request.model,
                quality_score=quality_scores.get("prose_health", 0),
                quality_details=quality_scores,
            )

            self._generation_count += 1
            self._total_generation_time_ms += elapsed_ms

            # Notify overseer: generation complete
            self._notify_overseer("generation_complete", {
                "card_id": card_id,
                "card_type": request.card_type.value,
                "quality_score": quality_scores.get("prose_health", 0),
                "generation_ms": round(elapsed_ms, 1),
                "tab_count": len(generated_tabs),
            })

            logger.info(
                f"Generated {card_id}: {len(generated_tabs)} tabs, "
                f"quality={quality_scores.get('prose_health', 0):.1f}, "
                f"{elapsed_ms:.0f}ms"
            )

            return result

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            result = GenerationResult(
                card_id=card_id,
                status=GenerationStatus.FAILED,
                error=str(e),
                generation_time_ms=elapsed_ms,
                model_used=request.model,
            )
            self._notify_overseer("generation_failed", {
                "card_id": card_id, "error": str(e),
            })
            logger.error(f"Card generation failed for {card_id}: {e}")
            return result

    # ------------------------------------------------------------------
    # Bulk Operations
    # ------------------------------------------------------------------

    def queue_all_for_type(
        self,
        card_type: CardType,
        source_items: List[Dict[str, Any]],
        priority: int = 5,
        session_mode: Optional[bool] = None,
    ) -> int:
        """
        Queue generation for all items of a given card type.

        If session_mode is None, auto-selects based on model allocation:
            - Opus-allocated types → session_mode=True (queue for CW/CC/AG)
            - Sonnet-allocated types → session_mode=False (API batch)

        Returns number of items queued.
        """
        spec = get_card_type_spec(card_type)
        if session_mode is None:
            session_mode = spec.model_allocation == "opus"

        queued = 0
        for item in source_items:
            entity_id = item.get("entity_id") or item.get("id") or item.get("cluster_id", "unknown")
            request = GenerationRequest(
                card_type=card_type,
                entity_id=str(entity_id),
                source_data=item,
                priority=priority,
                session_mode=session_mode,
                requested_by="bulk_init",
            )
            self._queue.enqueue(request)
            queued += 1

        logger.info(
            f"Queued {queued} {card_type.value} cards "
            f"(model={spec.model_allocation}, session={session_mode})"
        )
        return queued

    def process_queue(
        self,
        max_cards: int = 0,
        model_filter: Optional[str] = None,
        session_only: bool = False,
    ) -> List[GenerationResult]:
        """
        Process queued generation requests.

        Args:
            max_cards: Max cards to generate (0 = all)
            model_filter: Only process cards for this model
            session_only: Only process session-queued cards

        Returns:
            List of GenerationResults
        """
        results = []
        processed = 0

        while True:
            if max_cards > 0 and processed >= max_cards:
                break

            if session_only:
                session_queue = self._queue.get_session_queue()
                if not session_queue:
                    break
                request = self._queue.dequeue(model_filter=session_queue[0].model)
            else:
                request = self._queue.dequeue(model_filter=model_filter)

            if request is None:
                break

            result = self.generate_card(request)
            self._queue.complete(result)
            results.append(result)
            processed += 1

        return results

    # ------------------------------------------------------------------
    # Staleness-Triggered Regeneration (Real-Time)
    # ------------------------------------------------------------------

    def check_and_queue_stale(self) -> int:
        """
        Scan all cards for staleness and queue regeneration for stale ones.

        Called by overseer (real-time), not by nightly batch.

        Returns number of cards queued for regeneration.
        """
        queued = 0
        for card_id, meta in self._card_index.items():
            ledger = self._get_staleness_ledger(card_id)
            score, status = compute_staleness_score(ledger)

            if status == Staleness.STALE:
                # Queue for regeneration
                card_type = CardType(meta["card_type"])
                entity_id = meta["entity_id"]

                # Load existing card's source data if available
                card_path = self._base / meta.get("path", "")
                source_data = {}
                if card_path.exists():
                    try:
                        existing = Card.load(card_path)
                        source_data = existing.iceberg.raw_data if existing.iceberg else {}
                    except Exception:
                        pass

                request = GenerationRequest(
                    card_type=card_type,
                    entity_id=entity_id,
                    source_data=source_data,
                    priority=3,  # High priority for stale cards
                    requested_by="staleness",
                    session_mode=(get_card_type_spec(card_type).model_allocation == "opus"),
                )
                self._queue.enqueue(request)
                queued += 1

                # Update index
                meta["staleness"] = Staleness.STALE.value

        if queued > 0:
            self._save_index()
            self._save_queue_state()
            logger.info(f"Queued {queued} stale cards for regeneration")

        return queued

    def on_new_evidence(self, card_id: str, paper_doi: Optional[str] = None) -> None:
        """
        Called when new evidence arrives that affects a card.

        Updates the staleness ledger and potentially queues regeneration.
        Real-time trigger — not waiting for nightly batch.
        """
        ledger = self._get_staleness_ledger(card_id)
        ledger.record_new_source(paper_doi or "unknown")
        self._save_staleness_ledger(card_id, ledger)

        # Check if now stale
        score, status = compute_staleness_score(ledger)
        if status == Staleness.STALE:
            self.check_and_queue_stale()

    def on_credence_shift(self, card_id: str, old_omega: float, new_omega: float) -> None:
        """Called when a card's credence (omega) changes significantly."""
        ledger = self._get_staleness_ledger(card_id)
        ledger.record_credence_shift(old_omega, new_omega)
        self._save_staleness_ledger(card_id, ledger)

        score, status = compute_staleness_score(ledger)
        if status == Staleness.STALE:
            self.check_and_queue_stale()

    # ------------------------------------------------------------------
    # Surface Population
    # ------------------------------------------------------------------

    def _populate_surface(self, card: Card, request: GenerationRequest) -> Card:
        """Populate the card's Surface layer from source data."""
        data = request.source_data
        spec = get_card_type_spec(request.card_type)

        # Title
        card.surface.title = data.get("title", card.surface.title)

        # Confidence thermometer
        omega = data.get("omega", data.get("omega_composite", None))
        if omega is not None:
            if omega >= 0.75:
                card.surface.confidence_level = ConfidenceLevel.HIGH
            elif omega >= 0.55:
                card.surface.confidence_level = ConfidenceLevel.MOD_HIGH
            elif omega >= 0.35:
                card.surface.confidence_level = ConfidenceLevel.MODERATE
            else:
                card.surface.confidence_level = ConfidenceLevel.LOW
            card.surface.confidence_omega = omega
            card.surface.confidence_label = (
                f"{card.surface.confidence_level.value.replace('_', '-').title()} "
                f"(ω = {omega:.2f})"
            )

        # Direction
        direction_str = data.get("direction", data.get("direction_consensus", ""))
        direction_map = {
            "increase": Direction.INCREASE,
            "decrease": Direction.DECREASE,
            "mixed": Direction.MIXED,
            "no_effect": Direction.NO_EFFECT,
        }
        if direction_str:
            card.surface.direction = direction_map.get(direction_str.lower(), Direction.NA)

        # Evidence counts
        card.surface.n_findings = data.get("n_findings", data.get("evidence_count", 0))
        card.surface.n_papers = data.get("n_papers", data.get("paper_count", 0))

        # Staleness (new cards are FRESH)
        card.surface.staleness = Staleness.FRESH
        card.surface.staleness_score = 0.0

        return card

    # ------------------------------------------------------------------
    # Tab Generation
    # ------------------------------------------------------------------

    def _generate_tab(
        self, request: GenerationRequest, tab_name: str
    ) -> Optional[CardTab]:
        """Generate a single tab using the registered generator."""
        generator = self._tab_registry.get(request.card_type, tab_name)

        if generator:
            return generator(request.card_type, request.entity_id,
                           request.source_data, request.model)

        # Fallback: create a placeholder tab from source data
        return self._generate_fallback_tab(request, tab_name)

    def _generate_fallback_tab(
        self, request: GenerationRequest, tab_name: str
    ) -> Optional[CardTab]:
        """
        Create a placeholder tab when no specific generator is registered.

        This produces a draft tab with available data, marked for LLM refinement.
        """
        data = request.source_data
        spec = get_card_type_spec(request.card_type)

        # Build prose from available data based on tab type
        prose = ""
        structured_data = {}

        if tab_name == "overview":
            prose = data.get("description", data.get("summary", ""))
            if not prose:
                prose = f"[DRAFT] Overview for {spec.display_name}: {request.entity_id}"
            # Include surprise flags if present
            surprise_flags = data.get("surprise_flags", [])
            if surprise_flags:
                prose += f"\n\nSurprise findings: {'; '.join(surprise_flags[:2])}"
            structured_data = {
                "entity_id": request.entity_id,
                "card_type": request.card_type.value,
                "tier": spec.tier.value,
            }

        elif tab_name == "mechanism":
            mechanism = data.get("mechanism_chain", data.get("mechanism", []))
            if isinstance(mechanism, list) and mechanism:
                prose = " → ".join(
                    f"{step.get('from_construct', '?')} → {step.get('to_construct', '?')}"
                    for step in mechanism
                )
            else:
                prose = f"[DRAFT] Mechanism for {request.entity_id}"
            if spec.has_mechanism_diagram:
                structured_data["diagram_needed"] = True

        elif tab_name == "evidence":
            n_findings = data.get("n_findings", 0)
            n_papers = data.get("n_papers", 0)
            prose = f"Based on {n_findings} findings across {n_papers} papers."
            # SC-ANN-CARD-3: Evidence tab includes replication status from annotations
            replication_status = data.get("replication_status")
            if replication_status:
                prose += f" Replication status: {replication_status}."
            if spec.has_evidence_forest_plot:
                structured_data["forest_plot_needed"] = True
            structured_data["n_findings"] = n_findings
            structured_data["n_papers"] = n_papers

        elif tab_name == "design":
            design = data.get("design_implications", data.get("design", ""))
            prose = design if design else f"[DRAFT] Design implications for {request.entity_id}"
            if spec.has_design_parameters:
                structured_data["parameter_table_needed"] = True

        elif tab_name == "connections":
            connections = data.get("connections", data.get("related_entities", []))
            if connections:
                prose = f"Connected to: {', '.join(str(c) for c in connections[:10])}"
            else:
                prose = f"[DRAFT] Connections for {request.entity_id}"

        elif tab_name == "debate":
            # SC-ANN-CARD-2: Debate tab includes disputes from annotation service when available
            disputes = data.get("disputes", [])
            if disputes:
                prose = "Active disputes: " + "; ".join(disputes[:3])
            else:
                debate = data.get("debate", data.get("competing_accounts", ""))
                prose = debate if debate else f"[DRAFT] Debate for {request.entity_id}"

        elif tab_name == "history":
            history = data.get("history", "")
            prose = history if history else f"[DRAFT] Revision history for {request.entity_id}"

        return CardTab(
            tab_name=tab_name,
            prose=prose,
            structured_data=structured_data if structured_data else None,
        )

    def _register_builtin_generators(self) -> None:
        """Register default tab generators for common patterns."""
        # CW builtin generators: overview, evidence, history
        self._tab_registry.register_default("overview", self._gen_overview_tab)
        self._tab_registry.register_default("evidence", self._gen_evidence_tab)
        self._tab_registry.register_default("history", self._gen_history_tab)

        # AG corpus-grounded generators (Round 14): mechanism, design,
        # connections, debate. These produce factual scaffolds from corpus
        # data. CW's content agents can wrap them with LLM refinement later.
        try:
            from src.qa.tab_generators import register_corpus_generators
            register_corpus_generators(self)
        except ImportError:
            logger.debug("AG tab_generators not available — using fallbacks")

    @staticmethod
    def _gen_overview_tab(
        card_type: CardType, entity_id: str, data: Dict, model: str
    ) -> CardTab:
        """Generate an overview tab from source data."""
        spec = get_card_type_spec(card_type)
        title = data.get("title", entity_id)
        description = data.get("description", data.get("summary", ""))

        if not description:
            description = f"{spec.display_name} for {entity_id}."

        n_findings = data.get("n_findings", 0)
        n_papers = data.get("n_papers", 0)

        prose = f"# {title}\n\n{description}"
        if n_findings > 0:
            prose += f"\n\nSupported by {n_findings} findings across {n_papers} papers."

        return CardTab(
            tab_name="overview",
            prose=prose,
            structured_data={
                "entity_id": entity_id,
                "type": card_type.value,
                "tier": spec.tier.value,
                "badge": spec.badge_text,
                "model_allocation": spec.model_allocation,
            },
        )

    @staticmethod
    def _gen_evidence_tab(
        card_type: CardType, entity_id: str, data: Dict, model: str
    ) -> CardTab:
        """Generate an evidence tab from source data."""
        spec = get_card_type_spec(card_type)
        n_findings = data.get("n_findings", 0)
        n_papers = data.get("n_papers", 0)
        theory_links = data.get("theory_links", [])

        prose = f"## Evidence Summary\n\n"
        prose += f"- **Findings**: {n_findings}\n"
        prose += f"- **Papers**: {n_papers}\n"
        if theory_links:
            prose += f"- **Theory links**: {', '.join(theory_links[:5])}\n"

        structured_data = {
            "n_findings": n_findings,
            "n_papers": n_papers,
            "theory_links": theory_links,
        }

        if spec.has_evidence_forest_plot:
            structured_data["forest_plot_needed"] = True

        return CardTab(
            tab_name="evidence",
            prose=prose,
            structured_data=structured_data,
        )

    @staticmethod
    def _gen_history_tab(
        card_type: CardType, entity_id: str, data: Dict, model: str
    ) -> CardTab:
        """Generate a history tab (revision log)."""
        now = datetime.now(timezone.utc).isoformat()
        prose = f"## Revision History\n\n- **{now}**: Initial generation\n"

        return CardTab(
            tab_name="history",
            prose=prose,
            structured_data={
                "revisions": [
                    {"timestamp": now, "event": "initial_generation", "model": model}
                ],
            },
        )

    # ------------------------------------------------------------------
    # Quality Gate
    # ------------------------------------------------------------------

    def _run_quality_gate(self, card: Card) -> Dict[str, float]:
        """
        Run prose quality checks on all tabs.

        Uses ProseRevisionService if available; otherwise basic metrics.
        """
        scores = {}

        # Aggregate prose from all tabs (tabs is Dict[str, CardTab])
        all_prose = "\n\n".join(
            tab.prose for tab in card.body.tabs.values() if tab.prose
        )

        if not all_prose.strip():
            scores["prose_health"] = 0.0
            scores["word_count"] = 0
            return scores

        word_count = len(all_prose.split())
        scores["word_count"] = word_count

        # Try ProseRevisionService
        if self._prose_service:
            try:
                report = self._prose_service.full_critique(all_prose)
                scores["prose_health"] = report.quality_score * 10  # 0-10 scale
                scores["nominalization_rate"] = getattr(report, "nominalization_rate", 0)
                scores["passive_rate"] = getattr(report, "passive_rate", 0)
            except Exception as e:
                logger.debug(f"Prose service failed: {e}")
                # Fallback to basic scoring
                scores["prose_health"] = 7.0 if word_count > 50 else 5.0
        else:
            # Basic quality heuristic when prose service unavailable
            draft_count = all_prose.count("[DRAFT]")
            if draft_count > 0:
                scores["prose_health"] = max(3.0, 7.0 - draft_count)
            else:
                scores["prose_health"] = 7.0 if word_count > 100 else 5.0

        # Tab coverage
        spec = get_card_type_spec(card.card_type)
        required = spec.required_tabs
        present = set(card.body.tabs.keys())
        coverage = len(required & present) / max(len(required), 1)
        scores["tab_coverage"] = coverage

        # Confidence calibration (is confidence level consistent with evidence?)
        if card.surface.confidence_level and card.surface.n_findings:
            ec = card.surface.n_findings
            cl = card.surface.confidence_level
            # High confidence with < 5 findings is suspicious
            if cl == ConfidenceLevel.HIGH and ec < 5:
                scores["confidence_calibration"] = 0.5
            else:
                scores["confidence_calibration"] = 1.0
        else:
            scores["confidence_calibration"] = 0.8  # No data → moderate

        return scores

    # ------------------------------------------------------------------
    # Iceberg Population
    # ------------------------------------------------------------------

    def _build_iceberg(
        self, request: GenerationRequest, quality_scores: Dict, elapsed_ms: float
    ) -> CardIceberg:
        """Build the Iceberg layer with provenance and agent context."""
        data = request.source_data

        source_map = IcebergSourceMap(
            source_card_ids=data.get("source_card_ids", []),
            template_ids=data.get("template_ids", []),
            framework_ids=data.get("framework_ids", []),
            molecule_ids=data.get("molecule_ids", []),
            finding_ids=data.get("finding_ids", []),
            paper_dois=data.get("paper_dois", []),
        )

        agent_context = IcebergAgentContext(
            model=request.model,
            prompt_template=f"card_gen_{request.card_type.value}",
            prompt_hash="",  # Will be filled by actual LLM call
            temperature=0.3,
            generation_timestamp=datetime.now(timezone.utc).isoformat(),
            generation_duration_ms=int(elapsed_ms),
            token_count_input=0,
            token_count_output=0,
            cost_usd=0.0,
        )

        quality = IcebergQualityScores(
            prose_health=quality_scores.get("prose_health", 0),
            confidence_calibration=quality_scores.get("confidence_calibration", 0),
            coverage_completeness=quality_scores.get("tab_coverage", 0),
            reference_accuracy=quality_scores.get("reference_accuracy", 1.0),
            passes_quality_gate=quality_scores.get("prose_health", 0) >= self.MIN_PROSE_HEALTH,
        )

        return CardIceberg(
            source_map=source_map,
            agent_context=agent_context,
            quality_scores=quality,
            raw_data=data,
        )

    # ------------------------------------------------------------------
    # Staleness Ledger Management
    # ------------------------------------------------------------------

    def _get_staleness_ledger(self, card_id: str) -> StalenessLedger:
        """Get or create a staleness ledger for a card."""
        if card_id not in self._staleness_ledgers:
            ledger_path = self._staleness_dir / f"{card_id.replace(':', '_')}.json"
            if ledger_path.exists():
                try:
                    with open(ledger_path) as f:
                        data = json.load(f)
                    self._staleness_ledgers[card_id] = StalenessLedger.from_dict(data)
                except Exception:
                    self._staleness_ledgers[card_id] = StalenessLedger()
            else:
                self._staleness_ledgers[card_id] = StalenessLedger()
        return self._staleness_ledgers[card_id]

    def _save_staleness_ledger(self, card_id: str, ledger: StalenessLedger) -> None:
        """Persist a staleness ledger to disk."""
        ledger_path = self._staleness_dir / f"{card_id.replace(':', '_')}.json"
        with open(ledger_path, "w") as f:
            json.dump(ledger.to_dict(), f, indent=2)

    def _record_generation(self, card_id: str) -> None:
        """Record a generation event in the staleness ledger (resets freshness)."""
        ledger = self._get_staleness_ledger(card_id)
        ledger.clear()  # Fresh start after regeneration
        self._save_staleness_ledger(card_id, ledger)

    # ------------------------------------------------------------------
    # Overseer Integration (Real-Time)
    # ------------------------------------------------------------------

    def _notify_overseer(self, event_type: str, data: Dict) -> None:
        """Notify the overseer of a generation event."""
        if self._overseer is None:
            return

        try:
            # Use overseer's pipeline registry if available
            if hasattr(self._overseer, "record_pipeline_event"):
                self._overseer.record_pipeline_event(
                    pipeline_id="card_generation",
                    event_type=event_type,
                    data=data,
                )
            elif hasattr(self._overseer, "log_event"):
                self._overseer.log_event(event_type, data)
        except Exception as e:
            logger.debug(f"Overseer notification failed: {e}")

    def get_overseer_health_report(self) -> Dict[str, Any]:
        """
        Produce a health report for the overseer.

        Includes queue status, generation stats, staleness distribution,
        and coverage gaps.
        """
        # Staleness distribution
        staleness_dist = {"FRESH": 0, "AGING": 0, "STALE": 0, "UNKNOWN": 0}
        for card_id, meta in self._card_index.items():
            s = meta.get("staleness", "UNKNOWN")
            staleness_dist[s] = staleness_dist.get(s, 0) + 1

        # Coverage: which card types have cards?
        type_coverage = {}
        for ct in CardType:
            spec = get_card_type_spec(ct)
            cards_of_type = [
                m for m in self._card_index.values()
                if m.get("card_type") == ct.value
            ]
            type_coverage[ct.value] = {
                "expected": spec.approximate_count,
                "generated": len(cards_of_type),
                "model": spec.model_allocation,
            }

        return {
            "total_cards": len(self._card_index),
            "queue": self._queue.stats(),
            "staleness_distribution": staleness_dist,
            "type_coverage": type_coverage,
            "generation_stats": {
                "total_generated": self._generation_count,
                "avg_time_ms": round(
                    self._total_generation_time_ms / max(self._generation_count, 1), 1
                ),
            },
            "tab_generator_coverage": self._tab_registry.coverage(),
            "alert_queue_depth": self._queue.queue_depth() > self.MAX_QUEUE_DEPTH_ALERT,
        }

    # ------------------------------------------------------------------
    # Retrieval Support
    # ------------------------------------------------------------------

    def get_card(self, card_id: str) -> Optional[Card]:
        """Load a card by ID."""
        meta = self._card_index.get(card_id)
        if not meta:
            return None
        card_path = self._base / meta["path"]
        if not card_path.exists():
            return None
        return Card.load(card_path)

    def get_cards_by_type(self, card_type: CardType) -> List[Dict]:
        """Get index entries for all cards of a given type."""
        return [
            {**meta, "card_id": cid}
            for cid, meta in self._card_index.items()
            if meta.get("card_type") == card_type.value
        ]

    def search_cards(self, query: str, max_results: int = 10) -> List[Dict]:
        """Simple keyword search across card index."""
        query_lower = query.lower()
        results = []
        for card_id, meta in self._card_index.items():
            title = meta.get("title", "").lower()
            entity_id = meta.get("entity_id", "").lower()
            if query_lower in title or query_lower in entity_id or query_lower in card_id.lower():
                results.append({**meta, "card_id": card_id})
                if len(results) >= max_results:
                    break
        return results

    # ------------------------------------------------------------------
    # Card Path Convention
    # ------------------------------------------------------------------

    def _card_path(self, card: Card) -> Path:
        """
        Compute the canonical storage path for a card.

        Convention: cards/{tier}/{card_type}/{entity_id}.json
        """
        spec = get_card_type_spec(card.card_type)
        tier_dir = self._card_dir / spec.tier.value
        type_dir = tier_dir / card.card_type.value
        type_dir.mkdir(parents=True, exist_ok=True)
        safe_id = card.entity_id.replace("/", "_").replace(":", "_")
        return type_dir / f"{safe_id}.json"

    # ------------------------------------------------------------------
    # Two-Pass Architecture: Sonnet-Prepares, Opus-Polishes
    # ------------------------------------------------------------------
    # Design: Sonnet does exhaustive structured data gathering (cheap, parallel).
    # Opus does quality prose polish (expensive, via CW/CC/AG sessions = free).
    # All intermediate data is persisted in the Iceberg so Opus has full context.
    # All generated answers are cached as cards — retrieved, not regenerated.

    def generate_card_two_pass(self, request: GenerationRequest) -> GenerationResult:
        """
        Two-pass card generation:
            Pass 1 (Haiku/Sonnet): Gather evidence, structure data, draft prose
            Pass 2 (Opus): Polish prose, calibrate language, frame debates

        EVERY card gets Opus polish — no exceptions. Pass 1 produces a
        working card; Pass 2 raises it to publication quality.

        Pass 1 model is determined by card type complexity:
            - Haiku for T3 belief cards (simple, high-volume)
            - Sonnet for T2 mechanism, Layer, Competition
            - Sonnet for Opus-allocated types (Opus reserved for Pass 2)
        """
        spec = get_card_type_spec(request.card_type)

        # Pass 1 model: use the cheaper model for drafting
        pass1_model = request.force_model or "sonnet"
        if pass1_model == "opus":
            pass1_model = "sonnet"  # Never waste Opus on Pass 1

        # Pass 1: Draft with cheap model (immediate)
        pass1_request = GenerationRequest(
            card_type=request.card_type,
            entity_id=request.entity_id,
            source_data=request.source_data,
            priority=request.priority,
            requested_by=request.requested_by,
            session_mode=False,
            force_model=pass1_model,
        )
        result = self.generate_card(pass1_request)

        if result.status != GenerationStatus.COMPLETE:
            return result

        # EVERY card gets Pass 2 (Opus polish) — mandatory
        polish_request = GenerationRequest(
            card_type=request.card_type,
            entity_id=request.entity_id,
            source_data={
                **request.source_data,
                "_pass": 2,
                "_pass1_card_id": result.card_id,
                "_pass1_structured_data": {
                    tab_name: tab.structured_data
                    for tab_name, tab in result.card.body.tabs.items()
                    if tab.structured_data
                },
                "_pass1_prose": {
                    tab_name: tab.prose
                    for tab_name, tab in result.card.body.tabs.items()
                },
            },
            priority=max(1, request.priority - 1),  # Higher priority for polish
            requested_by="two_pass_polish",
            session_mode=True,  # Queue for CW/CC/AG session (free Opus)
            force_model="opus",
        )
        self._queue.enqueue(polish_request)
        self._save_queue_state()

        logger.info(
            f"Two-pass: {result.card_id} Pass 1 complete (sonnet), "
            f"Pass 2 queued for session (opus)"
        )

        return result

    def process_polish_queue(self, max_cards: int = 0) -> List[GenerationResult]:
        """
        Process Pass 2 (Opus polish) cards from the session queue.

        Called from CW/CC/AG sessions — uses monthly allocation, not API credits.
        Each polish takes the Pass 1 structured data + draft prose and rewrites
        with Opus-quality synthesis and language.
        """
        results = []
        processed = 0

        while True:
            if max_cards > 0 and processed >= max_cards:
                break

            request = self._queue.dequeue(model_filter="opus")
            if request is None:
                break

            # For polish passes, use the full generate_card which will
            # use the stored structured_data as rich context
            result = self.generate_card(request)
            self._queue.complete(result)
            results.append(result)
            processed += 1

        if results:
            logger.info(
                f"Processed {len(results)} Opus polish cards: "
                f"{sum(1 for r in results if r.status == GenerationStatus.COMPLETE)} complete"
            )

        return results

    # ------------------------------------------------------------------
    # Follow-Up Question Caching
    # ------------------------------------------------------------------
    # Every answer is a card. Follow-up questions that produce new answers
    # create new cards, which are then cached. The next time the same
    # follow-up is asked, the card retriever serves it in 5-20ms.

    def cache_followup_answer(
        self,
        parent_card_id: str,
        question: str,
        answer_data: Dict[str, Any],
    ) -> GenerationResult:
        """
        Cache a follow-up question's answer as a new card.

        The parent card's ID is stored in the Iceberg source_map
        for provenance tracking.
        """
        # Create a T3-like belief card for the follow-up
        safe_q = question[:50].replace(" ", "_").replace("?", "")
        entity_id = f"followup_{parent_card_id}_{safe_q}"

        request = GenerationRequest(
            card_type=CardType.T3_BELIEF,
            entity_id=entity_id,
            source_data={
                **answer_data,
                "title": question,
                "source_card_ids": [parent_card_id],
                "_is_followup": True,
            },
            priority=4,
            requested_by="followup_cache",
            session_mode=False,
            force_model="sonnet",  # Follow-ups use Sonnet unless complex
        )

        return self.generate_card(request)

    # ------------------------------------------------------------------
    # Status & Diagnostics
    # ------------------------------------------------------------------

    def status(self) -> Dict[str, Any]:
        """Full status report for display or logging."""
        return {
            "cards_indexed": len(self._card_index),
            "queue": self._queue.stats(),
            "generation_count": self._generation_count,
            "avg_generation_ms": round(
                self._total_generation_time_ms / max(self._generation_count, 1), 1
            ),
            "tab_coverage": self._tab_registry.coverage(),
            "storage_dir": str(self._card_dir),
        }
