"""
Session Card Writer — Zero-Cost Card Generation for CW/CC/AG Sessions
=======================================================================

This module enables the session agent (CW/CC/AG) to generate ATLAS cards
WITHOUT making paid API calls. The session agent IS the LLM — it generates
content directly in the conversation.

Architecture:
    SessionCardWriter.get_next_card_prompt()
        → Session agent reads prompt and generates content
    SessionCardWriter.accept_card_response()
        → Session agent provides content in conversation
        → SessionCardWriter parses, validates, and saves

Design:
    - No API calls — the session agent does all LLM work
    - Prompts are built using same prompt_builders from card_tab_generators.py
    - Validation uses same _parse_llm_response() and _check_prose_health()
    - Card persistence uses CardRetriever and card storage backends
    - Parallel terminal support via claim_cards() with claims tracking

Success Conditions:
    SC-SCW-1: Session agent can read get_next_card_prompt() output
    SC-SCW-2: Session agent provides tab content via accept_card_response()
    SC-SCW-3: Cards saved to disk and retrievable via CardRetriever
    SC-SCW-4: Multiple terminals can claim cards without duplicates
    SC-SCW-5: Queue status reflects claimed and completed cards
    SC-SCW-6: Validation uses same prose health checks as batch generation

References:
    - scripts/batch_generate_cards.py: Batch API generation (Pass 1)
    - src/qa/card_tab_generators.py: System prompts, context builders,
      _parse_llm_response(), _check_prose_health()
    - src/qa/card_generation_orchestrator.py: Queue management

Author: CW (Claude/Cowork)
Date: 2026-03-04
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from src.qa.cards import (
    Card,
    CardBody,
    CardIceberg,
    CardSurface,
    CardTab,
    CardType,
    CARD_TYPE_REGISTRY,
    ConfidenceLevel,
    Direction,
    Staleness,
    make_card_id,
)
from src.qa.cards.card_types import CardTypeSpec, get_card_type_spec, get_all_tabs_for_type
from src.qa.card_tab_generators import (
    TAB_GENERATOR_CONFIG,
    _parse_llm_response,
    _check_prose_health,
    _omega_to_confidence,
)
from src.qa.card_generation_orchestrator import (
    GenerationQueue,
    GenerationRequest,
    GenerationStatus,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Session Card Claims — Prevent Duplicate Work Across Parallel Terminals
# ---------------------------------------------------------------------------

@dataclass
class CardClaim:
    """A card claimed by a terminal for generation."""
    card_id: str
    card_type: CardType
    entity_id: str
    terminal_id: str
    claimed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "claimed"  # claimed, in_progress, completed, failed
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "card_id": self.card_id,
            "card_type": self.card_type.value,
            "entity_id": self.entity_id,
            "terminal_id": self.terminal_id,
            "claimed_at": self.claimed_at,
            "status": self.status,
            "error": self.error,
        }


@dataclass
class ClaimsRegistry:
    """Track which cards are claimed by which terminals."""
    _claims: Dict[str, CardClaim] = field(default_factory=dict)  # card_id → CardClaim
    _persistence_path: Optional[Path] = None

    def load_from_file(self, path: Path) -> None:
        """Load existing claims from a JSON file."""
        self._persistence_path = path
        if path.exists():
            try:
                with open(path) as f:
                    data = json.load(f)
                for claim_dict in data.get("claims", []):
                    claim = CardClaim(
                        card_id=claim_dict["card_id"],
                        card_type=CardType(claim_dict["card_type"]),
                        entity_id=claim_dict["entity_id"],
                        terminal_id=claim_dict["terminal_id"],
                        claimed_at=claim_dict.get("claimed_at"),
                        status=claim_dict.get("status", "claimed"),
                        error=claim_dict.get("error"),
                    )
                    self._claims[claim.card_id] = claim
                logger.info(f"Loaded {len(self._claims)} claims from {path}")
            except Exception as e:
                logger.warning(f"Failed to load claims from {path}: {e}")

    def save_to_file(self) -> None:
        """Persist claims to JSON file."""
        if self._persistence_path:
            data = {
                "claims": [claim.to_dict() for claim in self._claims.values()],
                "saved_at": datetime.now(timezone.utc).isoformat(),
            }
            self._persistence_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._persistence_path, "w") as f:
                json.dump(data, f, indent=2)

    def claim(self, card_id: str, card_type: CardType, entity_id: str, terminal_id: str) -> bool:
        """
        Claim a card for a terminal. Returns True if successful, False if already claimed.
        """
        if card_id in self._claims:
            claim = self._claims[card_id]
            if claim.status in ("completed", "failed"):
                # Stale claim — can reclaim
                pass
            else:
                logger.debug(f"Card {card_id} already claimed by {claim.terminal_id}")
                return False

        self._claims[card_id] = CardClaim(
            card_id=card_id,
            card_type=card_type,
            entity_id=entity_id,
            terminal_id=terminal_id,
            status="claimed",
        )
        self.save_to_file()
        return True

    def update_status(self, card_id: str, status: str, error: Optional[str] = None) -> None:
        """Update the status of a claimed card."""
        if card_id in self._claims:
            self._claims[card_id].status = status
            self._claims[card_id].error = error
            self.save_to_file()

    def get_claims_by_terminal(self, terminal_id: str) -> List[CardClaim]:
        """Get all claims for a specific terminal."""
        return [c for c in self._claims.values() if c.terminal_id == terminal_id]

    def get_claimed_card_ids(self) -> Set[str]:
        """Get all card IDs that have been claimed (not yet completed/failed)."""
        return {c.card_id for c in self._claims.values() if c.status == "claimed"}

    def get_all_card_ids(self) -> Set[str]:
        """Get all card IDs that have been touched (claimed, completed, or failed)."""
        return set(self._claims.keys())


# ---------------------------------------------------------------------------
# Session Card Writer
# ---------------------------------------------------------------------------

@dataclass
class PromptForAgent:
    """A prompt ready for the session agent to process."""
    card_id: str
    card_type: CardType
    entity_id: str
    tabs_to_generate: List[str]
    system_prompt: str
    user_prompts: Dict[str, str]  # tab_name → user_prompt

    def to_markdown(self) -> str:
        """Format as readable Markdown for agent display."""
        parts = [
            f"# Card Generation Prompt",
            f"",
            f"**Card Type**: {self.card_type.value}",
            f"**Entity ID**: {self.entity_id}",
            f"**Card ID**: {self.card_id}",
            f"",
            f"**Tabs to Generate**: {', '.join(self.tabs_to_generate)}",
            f"",
            f"## System Prompt",
            f"```",
            f"{self.system_prompt}",
            f"```",
            f"",
            f"## User Prompts",
            f"",
        ]

        for tab_name in self.tabs_to_generate:
            if tab_name in self.user_prompts:
                parts.append(f"### {tab_name.upper()}")
                parts.append(f"```")
                parts.append(self.user_prompts[tab_name])
                parts.append(f"```")
                parts.append(f"")

        parts.append(f"## Instructions")
        parts.append(f"For each tab above:")
        parts.append(f"1. Read the system prompt and user prompt")
        parts.append(f"2. Generate the tab content (prose + optional JSON)")
        parts.append(f"3. Respond in this format:")
        parts.append(f"")
        parts.append(f"---")
        parts.append(f"## YOUR RESPONSE")
        parts.append(f"")
        parts.append(f"### overview")
        parts.append(f"[Your prose here...]")
        parts.append(f"```json")
        parts.append(f"{{}}")
        parts.append(f"```")
        parts.append(f"")
        parts.append(f"### mechanism")
        parts.append(f"[Your prose here...]")
        parts.append(f"```json")
        parts.append(f"{{}}")
        parts.append(f"```")
        parts.append(f"")
        parts.append(f"(etc. for each tab)")

        return "\n".join(parts)


class SessionCardWriter:
    """
    Generates ATLAS cards using the session agent (free Opus allocation).

    The session agent reads prompts from get_next_card_prompt() and provides
    responses via accept_card_response(). No API calls — the session is the LLM.
    """

    def __init__(
        self,
        queue: Optional[GenerationQueue] = None,
        claims_file: Optional[Path] = None,
        card_storage_dir: Optional[Path] = None,
    ):
        """
        Args:
            queue: The GenerationQueue to read from (or None to create a new one)
            claims_file: Path to persist card claims (for parallel terminals)
            card_storage_dir: Where to save generated cards (default: data/cards/)
        """
        self.queue = queue or GenerationQueue()
        self.claims = ClaimsRegistry()
        if claims_file:
            self.claims.load_from_file(claims_file)

        if card_storage_dir:
            self.card_storage_dir = Path(card_storage_dir)
        else:
            self.card_storage_dir = Path(__file__).parent.parent.parent / "data" / "cards"

        self.card_storage_dir.mkdir(parents=True, exist_ok=True)

    def claim_cards(
        self,
        terminal_id: str,
        count: int,
        card_type_filter: Optional[CardType] = None,
    ) -> List[str]:
        """
        Claim N cards for this terminal from the session queue.

        Filters by card_type if specified. Skips cards already claimed.
        Returns list of claimed card_ids.
        """
        claimed = []
        session_queue = self.queue.get_session_queue()
        already_claimed = self.claims.get_claimed_card_ids()

        for request in session_queue:
            if len(claimed) >= count:
                break

            # Skip if already claimed
            if request.card_id in already_claimed:
                continue

            # Skip if card_type filter doesn't match
            if card_type_filter and request.card_type != card_type_filter:
                continue

            # Try to claim this card
            if self.claims.claim(request.card_id, request.card_type, request.entity_id, terminal_id):
                claimed.append(request.card_id)

        logger.info(f"Terminal {terminal_id} claimed {len(claimed)} cards")
        return claimed

    def get_next_card_prompt(
        self,
        terminal_id: str = "default",
        card_type_filter: Optional[CardType] = None,
    ) -> Optional[PromptForAgent]:
        """
        Get the next card prompt for the session agent to process.

        The agent reads this prompt and generates tab content in the conversation.

        Args:
            terminal_id: Which terminal is requesting (for claims tracking)
            card_type_filter: Only return cards of this type (optional)

        Returns:
            PromptForAgent ready for agent display, or None if queue is empty
        """
        # Get next unclaimed card from session queue
        session_queue = self.queue.get_session_queue()
        already_claimed = self.claims.get_claimed_card_ids()

        next_request = None
        for request in session_queue:
            if request.card_id not in already_claimed:
                if card_type_filter is None or request.card_type == card_type_filter:
                    next_request = request
                    break

        if not next_request:
            logger.info("No unclaimed cards in session queue")
            return None

        # Claim this card
        if not self.claims.claim(
            next_request.card_id,
            next_request.card_type,
            next_request.entity_id,
            terminal_id,
        ):
            logger.warning(f"Failed to claim {next_request.card_id}, another terminal may have grabbed it")
            return self.get_next_card_prompt(terminal_id, card_type_filter)

        # Build prompts for all tabs
        spec = get_card_type_spec(next_request.card_type)
        tabs_to_generate = spec.required_tabs | spec.optional_tabs
        system_prompt = ""
        user_prompts = {}

        # Combine system prompt from first tab (they're all similar)
        first_tab = sorted(tabs_to_generate)[0]
        if first_tab in TAB_GENERATOR_CONFIG:
            system_prompt, context_builder = TAB_GENERATOR_CONFIG[first_tab]

        # Build user prompt for each tab
        for tab_name in sorted(tabs_to_generate):
            if tab_name == "history":
                # History tab is not generated by LLM
                continue

            if tab_name in TAB_GENERATOR_CONFIG:
                _, context_builder = TAB_GENERATOR_CONFIG[tab_name]
                user_prompt = context_builder(next_request.source_data, next_request.card_type)
                user_prompt += (
                    f"\n\nWrite the {tab_name.upper()} tab for this entity. "
                    f"Follow all norms in the system prompt. "
                    f"If you include a structured data block, wrap it in ```json ... ``` markers."
                )
                user_prompts[tab_name] = user_prompt

        return PromptForAgent(
            card_id=next_request.card_id,
            card_type=next_request.card_type,
            entity_id=next_request.entity_id,
            tabs_to_generate=sorted([t for t in tabs_to_generate if t != "history"]),
            system_prompt=system_prompt,
            user_prompts=user_prompts,
        )

    def accept_card_response(
        self,
        card_id: str,
        tab_responses: Dict[str, str],
        terminal_id: str = "default",
    ) -> Tuple[bool, str, Optional[Card]]:
        """
        Accept the session agent's generated content for a card.

        Args:
            card_id: The card being completed
            tab_responses: Dict mapping tab_name → prose+json response from agent
            terminal_id: Which terminal provided this response

        Returns:
            (success: bool, message: str, card: Optional[Card])
        """
        start_ms = int(time.time() * 1000)

        # Find the original request in the queue to get source_data
        original_request = None
        for r in self.queue._queue + list(self.queue._in_progress.values()):
            if r.card_id == card_id:
                original_request = r
                break

        if not original_request:
            msg = f"Card {card_id} not found in queue"
            logger.error(msg)
            self.claims.update_status(card_id, "failed", msg)
            return False, msg, None

        card_type = original_request.card_type
        entity_id = original_request.entity_id
        source_data = original_request.source_data

        # Parse each tab response
        tabs = {}
        all_prose_health = []
        errors = []

        for tab_name, response_text in tab_responses.items():
            try:
                prose, structured_data = _parse_llm_response(response_text)

                if not prose:
                    prose = response_text  # Fallback: treat entire response as prose

                prose_health = _check_prose_health(prose)
                all_prose_health.append(prose_health)

                tab = CardTab(
                    tab_name=tab_name,
                    prose=prose,
                    structured_data=structured_data,
                )
                tabs[tab_name] = tab

                logger.info(
                    f"Parsed {tab_name} for {card_id}: "
                    f"prose_health={prose_health:.1f}, "
                    f"prose_words={len(prose.split())}, "
                    f"has_json={structured_data is not None}"
                )

            except Exception as e:
                msg = f"Failed to parse {tab_name}: {e}"
                logger.error(msg)
                errors.append(msg)

        if errors:
            error_text = "; ".join(errors)
            self.claims.update_status(card_id, "failed", error_text)
            return False, error_text, None

        # Check minimum prose health
        if all_prose_health:
            min_health = min(all_prose_health)
            avg_health = sum(all_prose_health) / len(all_prose_health)
            logger.info(f"Card {card_id} prose health: min={min_health:.1f}, avg={avg_health:.1f}")
        else:
            return False, "No tabs generated", None

        # Build Card object
        try:
            spec = get_card_type_spec(card_type)

            # Determine confidence level from omega
            omega = source_data.get("omega", 0.5)
            confidence_str = _omega_to_confidence(omega)
            try:
                confidence_level = ConfidenceLevel(confidence_str.lower())
            except ValueError:
                confidence_level = ConfidenceLevel.MODERATE

            # Determine direction from source
            direction_str = source_data.get("direction_consensus", "na")
            try:
                direction = Direction(direction_str)
            except ValueError:
                direction = Direction.NA

            # Create Surface (always required)
            surface = CardSurface(
                title=source_data.get("title", entity_id),
                card_type=card_type,
                confidence_level=confidence_level,
                confidence_omega=omega,
                confidence_label=f"{confidence_str} (ω = {omega:.2f})",
                direction=direction,
                n_findings=source_data.get("n_findings", 0),
                n_papers=source_data.get("n_papers", 0),
                staleness=Staleness.FRESH,
                staleness_score=0.0,
                key_visual_path=None,
                last_generated=datetime.now(timezone.utc).isoformat(),
            )

            # Create Body with tabs (tabs is a Dict[str, CardTab])
            body = CardBody(
                tabs=tabs,
            )

            # Create Iceberg (optional quality/agent context)
            iceberg = CardIceberg(
                quality_scores={
                    "prose_health": avg_health if all_prose_health else 0.0,
                    "completeness": float(len(tabs) / len(spec.required_tabs)),
                },
                agent_context={
                    "generated_by": terminal_id,
                    "generation_time_ms": int(time.time() * 1000) - start_ms,
                    "model": "session",
                },
            )

            # Assemble Card
            card = Card(
                card_id=card_id,
                card_type=card_type,
                entity_id=entity_id,
                surface=surface,
                body=body,
                iceberg=iceberg,
            )

            # Validate
            try:
                card.validate_tabs()
            except Exception as e:
                msg = f"Card validation failed: {e}"
                logger.error(msg)
                self.claims.update_status(card_id, "failed", msg)
                return False, msg, None

            # Persist to disk
            card_path = self._get_card_file_path(card_id)
            card_path.parent.mkdir(parents=True, exist_ok=True)
            with open(card_path, "w") as f:
                # Build minimal card representation for persistence
                # Note: tabs is a Dict[str, CardTab]
                body_dict = {
                    "tabs": {
                        tab_name: {
                            "tab_name": tab.tab_name,
                            "prose": tab.prose,
                            "structured_data": tab.structured_data,
                        }
                        for tab_name, tab in body.tabs.items()
                    }
                }
                card_data = {
                    "card_id": card.card_id,
                    "card_type": card_type.value,
                    "entity_id": entity_id,
                    "surface": surface.to_dict(),
                    "body": body_dict,
                    "iceberg": {
                        "quality_scores": iceberg.quality_scores,
                        "agent_context": iceberg.agent_context,
                    },
                }
                json.dump(card_data, f, indent=2)

            logger.info(f"Saved card {card_id} to {card_path}")
            self.claims.update_status(card_id, "completed")
            return True, f"Card {card_id} generated successfully", card

        except Exception as e:
            msg = f"Failed to build/save card: {e}"
            logger.error(msg)
            self.claims.update_status(card_id, "failed", msg)
            return False, msg, None

    def get_queue_status(self) -> Dict[str, Any]:
        """Get current status of cards waiting for session generation."""
        session_queue = self.queue.get_session_queue()
        all_touched = self.claims.get_all_card_ids()
        active_claimed = self.claims.get_claimed_card_ids()
        completed_ids = {
            c.card_id for c in self.claims._claims.values()
            if c.status == "completed"
        }

        unclaimed = []
        claimed = []
        completed = []

        for request in session_queue:
            item = {
                "card_id": request.card_id,
                "entity_id": request.entity_id,
                "card_type": request.card_type.value,
                "priority": request.priority,
                "created_at": request.created_at,
            }
            if request.card_id in completed_ids:
                completed.append(item)
            elif request.card_id in active_claimed:
                claimed.append(item)
            else:
                unclaimed.append(item)

        return {
            "unclaimed": unclaimed,
            "claimed": claimed,
            "completed": completed,
            "total_queued": len(session_queue),
            "unclaimed_count": len(unclaimed),
            "claimed_count": len(claimed),
            "completed_count": len(completed),
            "by_type": self._count_by_type(session_queue),
        }

    def _count_by_type(self, requests: List[GenerationRequest]) -> Dict[str, int]:
        """Count requests by card type."""
        counts = {}
        for req in requests:
            counts[req.card_type.value] = counts.get(req.card_type.value, 0) + 1
        return counts

    def _get_card_file_path(self, card_id: str) -> Path:
        """Get the file path for storing a card."""
        # card_id format: {card_type}:{entity_id}
        parts = card_id.split(":")
        if len(parts) == 2:
            card_type, entity_id = parts
            return self.card_storage_dir / card_type / f"{entity_id}.json"
        else:
            # Fallback
            return self.card_storage_dir / f"{card_id}.json"
