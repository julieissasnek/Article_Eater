"""
Tests for SessionCardWriter — Session-mode Card Generation

Tests the zero-API-cost card generation workflow where the session
agent IS the LLM.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any, Dict

import pytest

from src.qa.session_card_writer import (
    SessionCardWriter,
    ClaimsRegistry,
    CardClaim,
    PromptForAgent,
)
from src.qa.card_generation_orchestrator import (
    GenerationRequest,
    GenerationQueue,
)
from src.qa.cards import CardType, ConfidenceLevel, Direction


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def queue() -> GenerationQueue:
    """Create a queue with sample cards."""
    queue = GenerationQueue()

    # Add some sample requests marked for session generation
    queue.enqueue(
        GenerationRequest(
            card_type=CardType.T1_FRAMEWORK,
            entity_id="ecological_psychology",
            source_data={
                "title": "Ecological Psychology (Gibson)",
                "description": "Direct perception of affordances in the environment.",
                "n_findings": 340,
                "n_papers": 120,
                "omega": 0.78,
                "direction_consensus": "increase",
            },
            priority=1,
            session_mode=True,  # For session generation
        )
    )

    queue.enqueue(
        GenerationRequest(
            card_type=CardType.T1_FRAMEWORK,
            entity_id="attention_restoration",
            source_data={
                "title": "Attention Restoration Theory (Kaplan)",
                "description": "Natural environments restore directed attention capacity.",
                "n_findings": 280,
                "n_papers": 95,
                "omega": 0.72,
                "direction_consensus": "increase",
            },
            priority=2,
            session_mode=True,
        )
    )

    queue.enqueue(
        GenerationRequest(
            card_type=CardType.MOLECULE,
            entity_id="daylighting_perception",
            source_data={
                "title": "Daylighting Perception",
                "description": "How natural light is perceived and influences mood.",
                "n_findings": 150,
                "n_papers": 45,
                "omega": 0.65,
                "direction_consensus": "increase",
            },
            priority=3,
            session_mode=True,
        )
    )

    queue.enqueue(
        GenerationRequest(
            card_type=CardType.T2_MECHANISM,
            entity_id="thermal_comfort_productivity",
            source_data={
                "title": "Thermal Comfort → Productivity",
                "description": "Temperature affects cognitive performance via thermal comfort.",
                "n_findings": 200,
                "n_papers": 60,
                "omega": 0.70,
                "direction_consensus": "decrease",
            },
            priority=4,
            session_mode=True,
        )
    )

    queue.enqueue(
        GenerationRequest(
            card_type=CardType.T2_MECHANISM,
            entity_id="noise_concentration",
            source_data={
                "title": "Background Noise → Concentration",
                "description": "Ambient noise levels affect task concentration and focus.",
                "n_findings": 180,
                "n_papers": 55,
                "omega": 0.68,
                "direction_consensus": "decrease",
            },
            priority=5,
            session_mode=True,
        )
    )

    return queue


@pytest.fixture
def writer(queue, temp_dir) -> SessionCardWriter:
    """Create a SessionCardWriter for testing."""
    claims_file = temp_dir / "claims.json"
    card_dir = temp_dir / "cards"
    return SessionCardWriter(
        queue=queue,
        claims_file=claims_file,
        card_storage_dir=card_dir,
    )


# ---------------------------------------------------------------------------
# Tests: ClaimsRegistry
# ---------------------------------------------------------------------------

class TestClaimsRegistry:
    """Tests for the parallel terminal claims system."""

    def test_claim_new_card(self, temp_dir):
        """Agent can claim a new card."""
        registry = ClaimsRegistry()
        registry.load_from_file(temp_dir / "claims.json")

        success = registry.claim(
            card_id="t1-framework:ecological_psychology",
            card_type=CardType.T1_FRAMEWORK,
            entity_id="ecological_psychology",
            terminal_id="claude-1",
        )

        assert success is True
        assert "t1-framework:ecological_psychology" in registry.get_claimed_card_ids()

    def test_cannot_claim_already_claimed_card(self, temp_dir):
        """Cannot claim a card that's already claimed by another terminal."""
        registry = ClaimsRegistry()
        registry.load_from_file(temp_dir / "claims.json")

        # Claude-1 claims the card
        registry.claim(
            card_id="t1-framework:ecological_psychology",
            card_type=CardType.T1_FRAMEWORK,
            entity_id="ecological_psychology",
            terminal_id="claude-1",
        )

        # Claude-2 tries to claim the same card
        success = registry.claim(
            card_id="t1-framework:ecological_psychology",
            card_type=CardType.T1_FRAMEWORK,
            entity_id="ecological_psychology",
            terminal_id="claude-2",
        )

        assert success is False

    def test_claim_persistence(self, temp_dir):
        """Claims persist to disk and reload correctly."""
        claims_file = temp_dir / "claims.json"

        # Create and save claims
        registry1 = ClaimsRegistry()
        registry1.load_from_file(claims_file)
        registry1.claim(
            card_id="card-1",
            card_type=CardType.T1_FRAMEWORK,
            entity_id="test_entity",
            terminal_id="claude-1",
        )

        # Load in a new registry instance
        registry2 = ClaimsRegistry()
        registry2.load_from_file(claims_file)

        assert "card-1" in registry2.get_claimed_card_ids()
        claim = registry2._claims["card-1"]
        assert claim.terminal_id == "claude-1"
        assert claim.status == "claimed"

    def test_update_claim_status(self, temp_dir):
        """Can update claim status (claimed → completed)."""
        registry = ClaimsRegistry()
        registry.load_from_file(temp_dir / "claims.json")

        registry.claim(
            card_id="card-1",
            card_type=CardType.T1_FRAMEWORK,
            entity_id="test_entity",
            terminal_id="claude-1",
        )

        registry.update_status("card-1", "completed")
        claim = registry._claims["card-1"]
        assert claim.status == "completed"

    def test_get_claims_by_terminal(self, temp_dir):
        """Can retrieve all claims for a specific terminal."""
        registry = ClaimsRegistry()
        registry.load_from_file(temp_dir / "claims.json")

        # Claude-1 claims two cards
        registry.claim(
            card_id="card-1",
            card_type=CardType.T1_FRAMEWORK,
            entity_id="entity1",
            terminal_id="claude-1",
        )
        registry.claim(
            card_id="card-2",
            card_type=CardType.T1_FRAMEWORK,
            entity_id="entity2",
            terminal_id="claude-1",
        )

        # Claude-2 claims one card
        registry.claim(
            card_id="card-3",
            card_type=CardType.MOLECULE,
            entity_id="entity3",
            terminal_id="claude-2",
        )

        claude1_claims = registry.get_claims_by_terminal("claude-1")
        assert len(claude1_claims) == 2
        assert all(c.terminal_id == "claude-1" for c in claude1_claims)


# ---------------------------------------------------------------------------
# Tests: SessionCardWriter
# ---------------------------------------------------------------------------

class TestSessionCardWriter:
    """Tests for the main SessionCardWriter class."""

    def test_claim_cards_multiple_terminals(self, writer):
        """Multiple terminals can claim different cards without duplicates."""
        # Claude-1 claims 2 cards
        claimed_1 = writer.claim_cards("claude-1", 2)
        assert len(claimed_1) == 2

        # Claude-2 claims 2 cards (should get different ones)
        claimed_2 = writer.claim_cards("claude-2", 2)
        assert len(claimed_2) == 2

        # No overlap
        assert set(claimed_1) & set(claimed_2) == set()

    def test_get_next_card_prompt(self, writer):
        """Agent can get next card prompt."""
        prompt = writer.get_next_card_prompt(terminal_id="claude-1")

        assert prompt is not None
        assert prompt.card_id == "t1-framework:ecological_psychology"
        assert prompt.card_type == CardType.T1_FRAMEWORK
        assert prompt.entity_id == "ecological_psychology"
        assert len(prompt.tabs_to_generate) > 0
        assert prompt.system_prompt != ""
        assert len(prompt.user_prompts) > 0

    def test_prompt_to_markdown(self, writer):
        """Prompt formats to readable Markdown."""
        prompt = writer.get_next_card_prompt(terminal_id="claude-1")

        markdown = prompt.to_markdown()

        assert "# Card Generation Prompt" in markdown
        assert prompt.card_id in markdown
        assert prompt.card_type.value in markdown
        assert "## System Prompt" in markdown
        assert "## User Prompts" in markdown
        assert "## Instructions" in markdown

    def test_get_next_prompt_with_type_filter(self, writer):
        """Can filter prompts by card type."""
        prompt = writer.get_next_card_prompt(
            terminal_id="claude-1",
            card_type_filter=CardType.T1_FRAMEWORK,
        )

        assert prompt is not None
        assert prompt.card_type == CardType.T1_FRAMEWORK

    def test_accept_card_response_success(self, writer):
        """Successfully accept and save a card response."""
        # Get a prompt first
        prompt = writer.get_next_card_prompt(terminal_id="claude-1")

        # Simulate agent response
        tab_responses = {
            "overview": "Ecological Psychology is a theory by Gibson.\n```json\n{\"n_findings\": 340}\n```",
            "mechanism": "The mechanism is direct perception.\n```json\n{\"steps\": 3}\n```",
        }

        success, message, card = writer.accept_card_response(
            card_id=prompt.card_id,
            tab_responses=tab_responses,
            terminal_id="claude-1",
        )

        assert success is True
        assert card is not None
        assert card.card_id == prompt.card_id
        assert len(card.body.tabs) == 2

    def test_accept_card_response_parses_prose_and_json(self, writer):
        """Correctly parses prose and JSON from agent response."""
        prompt = writer.get_next_card_prompt(terminal_id="claude-1")

        # Response with both prose and JSON
        tab_responses = {
            "overview": (
                "This is a theory about something important.\n"
                "It has multiple sentences describing the concept.\n"
                "\n"
                "```json\n"
                '{"n_findings": 100, "omega": 0.75}\n'
                "```"
            ),
        }

        success, message, card = writer.accept_card_response(
            card_id=prompt.card_id,
            tab_responses=tab_responses,
            terminal_id="claude-1",
        )

        assert success is True
        tab = card.body.tabs["overview"]
        assert "theory" in tab.prose.lower()
        assert "multiple sentences" in tab.prose.lower()
        assert tab.structured_data is not None
        assert tab.structured_data.get("n_findings") == 100

    def test_card_saved_to_disk(self, writer):
        """Card is saved to disk in correct location."""
        prompt = writer.get_next_card_prompt(terminal_id="claude-1")

        tab_responses = {
            "overview": "Overview content.",
            "mechanism": "Mechanism content.",
        }

        success, message, card = writer.accept_card_response(
            card_id=prompt.card_id,
            tab_responses=tab_responses,
            terminal_id="claude-1",
        )

        # Check file exists
        expected_path = (
            writer.card_storage_dir
            / "t1-framework"
            / "ecological_psychology.json"
        )
        assert expected_path.exists()

        # Verify content
        with open(expected_path) as f:
            saved_data = json.load(f)

        assert saved_data["card_id"] == prompt.card_id
        assert saved_data["entity_id"] == "ecological_psychology"

    def test_queue_status(self, writer):
        """Can retrieve queue status."""
        # Claim one card
        writer.claim_cards("claude-1", 1)

        status = writer.get_queue_status()

        assert status["total_queued"] == 5
        assert status["unclaimed_count"] == 4
        assert status["claimed_count"] == 1
        assert "t1-framework" in status["by_type"]
        assert "molecule" in status["by_type"]
        assert "t2-mechanism" in status["by_type"]

    def test_claim_cards_respects_count(self, writer):
        """Claim cards stops at requested count."""
        claimed = writer.claim_cards("claude-1", 2)
        assert len(claimed) == 2

        # Try to claim more
        more = writer.claim_cards("claude-1", 5)
        # Should get 3 (only 5 total - 2 already claimed)
        assert len(more) == 3

    def test_accept_response_updates_claims(self, writer):
        """Accepting response updates claim status."""
        prompt = writer.get_next_card_prompt(terminal_id="claude-1")
        card_id = prompt.card_id

        tab_responses = {
            "overview": "Content.",
            "mechanism": "Content.",
        }

        writer.accept_card_response(
            card_id=card_id,
            tab_responses=tab_responses,
            terminal_id="claude-1",
        )

        # Check claim status
        claim = writer.claims._claims.get(card_id)
        assert claim is not None
        assert claim.status == "completed"


# ---------------------------------------------------------------------------
# Tests: Integration
# ---------------------------------------------------------------------------

class TestSessionCardWriterIntegration:
    """End-to-end integration tests."""

    def test_full_workflow_three_agents(self, writer):
        """Three agents generate cards in parallel without duplicates."""
        # Each agent gets 2 cards
        agent1_cards = writer.claim_cards("agent-1", 2)
        agent2_cards = writer.claim_cards("agent-2", 2)
        agent3_cards = writer.claim_cards("agent-3", 2)

        # No overlap
        all_claimed = set(agent1_cards) | set(agent2_cards) | set(agent3_cards)
        assert len(all_claimed) == 5  # 5 cards total in queue
        assert set(agent1_cards) & set(agent2_cards) == set()
        assert set(agent1_cards) & set(agent3_cards) == set()
        assert set(agent2_cards) & set(agent3_cards) == set()

        # Each agent completes their cards
        for card_id in agent1_cards:
            writer.accept_card_response(
                card_id=card_id,
                tab_responses={"overview": "Content."},
                terminal_id="agent-1",
            )

        for card_id in agent2_cards:
            writer.accept_card_response(
                card_id=card_id,
                tab_responses={"overview": "Content."},
                terminal_id="agent-2",
            )

        for card_id in agent3_cards:
            writer.accept_card_response(
                card_id=card_id,
                tab_responses={"overview": "Content."},
                terminal_id="agent-3",
            )

        # Check status — all cards should be completed (0 unclaimed, 0 still-claimed)
        status = writer.get_queue_status()
        assert status["unclaimed_count"] == 0
        assert status["completed_count"] == 5  # All 5 cards completed

        # All cards should be on disk
        assert len(list(writer.card_storage_dir.rglob("*.json"))) == 5
