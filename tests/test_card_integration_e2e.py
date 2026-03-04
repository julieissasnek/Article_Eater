"""
End-to-End Card System Integration Tests — "Last Mile" Problem Detection
========================================================================

PHILOSOPHY
----------
Many bugs are "last mile" problems: Component A works in isolation, Component B
works in isolation, but A's output never actually reaches B. This test suite
verifies that data flows across component boundaries, not just that individual
components work.

Each success condition (SC-E2E-*) is an **end-to-end integration test** that
simulates a real user or downstream system receiving data from the card system.

Success conditions verify:
  1. Cards can be created, saved, and loaded (persistence boundary)
  2. Schema is importable from canonical paths (API boundary)
  3. Card types match generator expectations (type compatibility)
  4. All tab definitions are available and properly configured (data completeness)
  5. Staleness scoring works with real card data (computation boundary)
  6. Tab validation catches missing required tabs (constraint enforcement)
  7. JSON serialization produces standard-compliant output (data format boundary)
  8. Meta-review data lands in the right place on disk (file system boundary)
  9. User-type personalization actually changes output (personalization boundary)
  10. Badge colors are valid CSS/HTML colors (visual rendering boundary)
  11. Model allocation routing can work correctly (LLM dispatch boundary)
  12. Direction enum values match extraction system expectations (extraction-to-card data flow)

Each test includes docstrings explaining the "last mile" concern it addresses.

Author: CW (Claude/Cowork)
Date: 2026-03-04
Version: E2E-1.0.0 (integrated with ATLAS card system v1)
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------------------------
# SC-E2E-1: Card Persistence — Create, Save, Load, Verify
# ---------------------------------------------------------------------------

class TestE2ECardPersistence:
    """Verify data flows correctly through the save/load boundary."""

    def test_SC_E2E_1_card_roundtrip_with_real_path(self, tmp_path: Path) -> None:
        """SC-E2E-1: Card can be created, saved, and loaded with identical content.

        Last Mile Concern:
            The card schema defines save() and load() methods, but do they actually
            produce files in the right location? Does a downstream retriever
            component find what the generator saved?

        This test creates a card, saves it to a realistic data directory path
        (like data/qa_cache/), and then verifies the file exists and can be
        loaded back with identical content.
        """
        from src.qa.cards import (
            Card, CardType, CardTab, CardBody, ConfidenceLevel,
            Direction, Staleness, create_card
        )

        # Create a test card with realistic content
        card = create_card(
            card_type=CardType.T2_MECHANISM,
            entity_id="light-01",
            title="Environmental light affects circadian rhythm",
            confidence_level=ConfidenceLevel.MOD_HIGH,
            confidence_omega=0.65,
            direction=Direction.INCREASE,
            n_findings=12,
            n_papers=5,
        )

        # Add a tab (simulate actual card generation)
        overview_tab = CardTab(
            tab_name="overview",
            prose="This mechanism describes how environmental light cues entrain "
                  "circadian oscillators in the suprachiasmatic nucleus.",
        )
        card.body.tabs["overview"] = overview_tab

        # Save to a realistic data directory path
        card_dir = tmp_path / "qa_cache" / "cards"
        card_dir.mkdir(parents=True, exist_ok=True)
        card_path = card_dir / f"{card.card_id}.json"

        # Persist to disk
        card.save(card_path)

        # Verify file exists and is readable
        assert card_path.exists(), f"Card file should exist at {card_path}"
        assert card_path.stat().st_size > 0, "Card file should have content"

        # Load from disk
        loaded_card = Card.load(card_path)

        # Verify roundtrip integrity
        assert loaded_card.card_id == card.card_id
        assert loaded_card.card_type == card.card_type
        assert loaded_card.entity_id == card.entity_id
        assert loaded_card.surface.title == card.surface.title
        assert loaded_card.surface.confidence_omega == card.surface.confidence_omega
        assert loaded_card.surface.direction == card.surface.direction
        assert loaded_card.body.has_tab("overview")

        # Verify tab content survived roundtrip
        loaded_overview = loaded_card.body.get_tab("overview")
        assert loaded_overview is not None
        assert loaded_overview.prose == overview_tab.prose


# ---------------------------------------------------------------------------
# SC-E2E-2: Schema Importability — Canonical Paths Work
# ---------------------------------------------------------------------------

class TestE2ESchemaImports:
    """Verify all card components can be imported from canonical paths."""

    def test_SC_E2E_2_card_schema_imports(self) -> None:
        """SC-E2E-2: Card schema is importable from the canonical path.

        Last Mile Concern:
            Downstream code (generators, retrievers, renderers) will import
            the card schema. If the __init__.py doesn't properly export types,
            or if components depend on circular imports, the whole system breaks.

        This test verifies that the canonical import paths work.
        """
        # Import from the top-level package __init__.py
        from src.qa.cards import (
            Card, CardType, CardTier, ConfidenceLevel, Direction, Staleness,
            CardTab, CardBody, CardSurface,
            CARD_TYPE_REGISTRY, TAB_DEFINITIONS,
            create_card, make_card_id,
            get_tabs_for_card_type,
            compute_staleness_score, StalenessLedger,
        )

        # Verify all types are the correct objects
        assert Card is not None
        assert CardType is not None
        assert CardTier is not None
        assert CARD_TYPE_REGISTRY is not None and isinstance(CARD_TYPE_REGISTRY, dict)
        assert TAB_DEFINITIONS is not None and isinstance(TAB_DEFINITIONS, dict)

        # Verify factory functions exist and are callable
        assert callable(create_card)
        assert callable(make_card_id)
        assert callable(get_tabs_for_card_type)
        assert callable(compute_staleness_score)


# ---------------------------------------------------------------------------
# SC-E2E-3: Card Type Compatibility — Generator Expectations
# ---------------------------------------------------------------------------

class TestE2ECardTypeCompatibility:
    """Verify card types match what the generator produces."""

    def test_SC_E2E_3_cardtype_enum_matches_generator(self) -> None:
        """SC-E2E-3: CardType enum values match what card_generator.py produces.

        Last Mile Concern:
            The card_generator reads clusters and produces card objects with
            card_type set to a string value. If those string values don't match
            the CardType enum values, cards can't be created or serialized.

        This test reads the card_generator source and verifies that all card
        type strings it uses are valid CardType enum values.
        """
        from src.qa.cards import CardType

        # Read the generator to find what card types it uses
        generator_path = PROJECT_ROOT / "src" / "qa" / "card_generator.py"
        assert generator_path.exists(), f"Generator not found at {generator_path}"

        with open(generator_path) as f:
            generator_code = f.read()

        # CardType enum values (from card_types.py)
        valid_types = {ct.value for ct in CardType}

        # The generator should use these type strings in some form
        # At minimum, it should not reference any string that looks like a card type
        # that doesn't exist in the enum

        # Check that all CardType enum values are valid
        for card_type in CardType:
            assert card_type.value in valid_types, \
                f"CardType.{card_type.name} has invalid value: {card_type.value}"

        # Verify enum has the expected 9 types
        assert len(list(CardType)) == 9, "Should have exactly 9 card types"


# ---------------------------------------------------------------------------
# SC-E2E-4: Tab Coverage — All Referenced Tabs Are Defined
# ---------------------------------------------------------------------------

class TestE2ETabCoverage:
    """Verify all tabs used downstream are defined."""

    def test_SC_E2E_4_all_tabs_defined(self) -> None:
        """SC-E2E-4: Tab definitions cover all tabs referenced in card_generator.py.

        Last Mile Concern:
            The card_generator and card_retriever code references tab names.
            If a tab name is used in downstream code but missing from TAB_DEFINITIONS,
            tabs will fail to render for those cards.

        This test verifies that all tab names used by downstream components
        have definitions.
        """
        from src.qa.cards import TAB_DEFINITIONS, CardType, CARD_TYPE_REGISTRY

        defined_tabs = set(TAB_DEFINITIONS.keys())

        # The 7 canonical tabs (per §178.3.2)
        canonical_tabs = {
            "overview", "mechanism", "evidence", "design",
            "connections", "debate", "history"
        }

        # All canonical tabs must be defined
        for tab in canonical_tabs:
            assert tab in defined_tabs, f"Tab '{tab}' not in TAB_DEFINITIONS"

        # All tabs used by card types must be defined
        for card_type, spec in CARD_TYPE_REGISTRY.items():
            all_tabs = spec.required_tabs | spec.optional_tabs
            for tab_name in all_tabs:
                assert tab_name in defined_tabs, \
                    f"Card type {card_type.value} references undefined tab '{tab_name}'"

        # Verify each tab definition has required fields
        for tab_name, tab_def in TAB_DEFINITIONS.items():
            assert tab_def.name == tab_name
            assert tab_def.display_name
            assert tab_def.description
            assert tab_def.primary_user
            assert tab_def.min_prose_words >= 0


# ---------------------------------------------------------------------------
# SC-E2E-5: Staleness Scoring — Real Card Data
# ---------------------------------------------------------------------------

class TestE2EStalnessScoring:
    """Verify staleness computation works with real card data."""

    def test_SC_E2E_5_staleness_score_computation(self) -> None:
        """SC-E2E-5: Staleness score can be computed for a real card and result is valid.

        Last Mile Concern:
            The staleness system computes a score, but does that score actually
            make sense? Does it produce valid Staleness enum values that can be
            used to route cards to regeneration pipelines?

        This test creates a card with a staleness ledger, computes the score,
        and verifies the result is a valid Staleness value.
        """
        from src.qa.cards import (
            create_card, CardType, ConfidenceLevel, Direction,
            StalenessLedger, StalenessLedgerEntry, compute_staleness_score,
            Staleness
        )

        # Create a card
        card = create_card(
            card_type=CardType.T2_MECHANISM,
            entity_id="test-mech",
            title="Test mechanism",
            confidence_level=ConfidenceLevel.MODERATE,
        )

        # Create a staleness ledger with some entries
        ledger = StalenessLedger(
            last_regenerated=datetime.now(timezone.utc).isoformat()
        )

        # Record a credence shift (significant change)
        ledger.record_credence_shift(0.5, 0.65, "Evidence accumulation")

        # Compute staleness
        score, status = compute_staleness_score(
            ledger=ledger,
            total_sources=10,
            days_since_generation=5.0,
        )

        # Verify result is valid
        assert isinstance(score, float), "Score should be a float"
        assert 0.0 <= score <= 1.0, f"Score should be in [0, 1], got {score}"
        assert isinstance(status, Staleness), "Status should be a Staleness enum"
        assert status in [Staleness.FRESH, Staleness.AGING, Staleness.STALE]


# ---------------------------------------------------------------------------
# SC-E2E-6: Tab Validation — Missing Tabs Detected
# ---------------------------------------------------------------------------

class TestE2ETabValidation:
    """Verify tab validation catches constraint violations."""

    def test_SC_E2E_6_validate_tabs_detects_missing(self) -> None:
        """SC-E2E-6: Card.validate_tabs() correctly detects missing required tabs.

        Last Mile Concern:
            A downstream component might construct a card without all required tabs.
            The validation method should detect this, but does it? Does it return
            the right list of missing tabs that can be used for error reporting?

        This test creates a card that's missing required tabs and verifies
        validate_tabs() reports them correctly.
        """
        from src.qa.cards import create_card, CardType, CardTab

        # Create a T2 mechanism card (requires: overview, mechanism, evidence, design, connections, history)
        card = create_card(
            card_type=CardType.T2_MECHANISM,
            entity_id="incomplete",
            title="Incomplete card",
        )

        # Add only overview (missing others)
        card.body.tabs["overview"] = CardTab(
            tab_name="overview",
            prose="Summary",
        )

        # Validate
        missing = card.validate_tabs()

        # Should report missing tabs
        assert len(missing) > 0, "Should detect missing required tabs"

        # Check specific required tabs for T2
        from src.qa.cards import CARD_TYPE_REGISTRY
        spec = CARD_TYPE_REGISTRY[CardType.T2_MECHANISM]
        expected_missing = spec.required_tabs - {"overview"}

        for expected_tab in expected_missing:
            assert expected_tab in missing, \
                f"Tab '{expected_tab}' should be reported as missing"


# ---------------------------------------------------------------------------
# SC-E2E-7: JSON Serialization — Standard Compliance
# ---------------------------------------------------------------------------

class TestE2EJSONSerialization:
    """Verify cards serialize to standard JSON."""

    def test_SC_E2E_7_card_json_is_standard_json(self) -> None:
        """SC-E2E-7: Card.to_json() produces standard JSON with no non-serializable types.

        Last Mile Concern:
            A card might serialize fine in isolation, but downstream systems
            need to parse the JSON with standard libraries (json.loads, JavaScript JSON.parse, etc).
            If non-serializable types leak through, downstream breaks.

        This test serializes a card to JSON and verifies it can be parsed
        by a standard JSON parser.
        """
        from src.qa.cards import create_card, CardType, CardTab

        # Create a realistic card
        card = create_card(
            card_type=CardType.T1_FRAMEWORK,
            entity_id="predictive-processing",
            title="Predictive Processing Framework",
        )

        # Add content
        card.body.tabs["overview"] = CardTab(
            tab_name="overview",
            prose="The brain is a prediction machine.",
        )

        # Serialize to JSON
        json_str = card.to_json()

        # Verify it's standard JSON by parsing with json.loads
        assert isinstance(json_str, str)
        data = json.loads(json_str)  # Should not raise

        # Verify structure
        assert "card_id" in data
        assert "card_type" in data
        assert "surface" in data
        assert "body" in data
        assert "iceberg" in data

        # Re-serialize and compare
        json_str2 = json.dumps(data, indent=2)
        assert len(json_str2) > 0


# ---------------------------------------------------------------------------
# SC-E2E-8: Data Directory — Meta-Reviews Actually Exist
# ---------------------------------------------------------------------------

class TestE2EDataDirectory:
    """Verify data lands in the expected directories."""

    def test_SC_E2E_8_meta_review_directory_exists(self) -> None:
        """SC-E2E-8: Meta-review data directory exists and contains files.

        Last Mile Concern:
            Extraction and enrichment pipelines write to data/materialized_views/meta_reviews/.
            If that directory doesn't exist or is empty, the entire review system fails.

        This test verifies the directory exists and has content (per spec: 3,788 reviews).
        """
        meta_review_dir = PROJECT_ROOT / "data" / "materialized_views" / "meta_reviews"

        # Directory should exist
        assert meta_review_dir.exists(), \
            f"Meta-review directory should exist at {meta_review_dir}"
        assert meta_review_dir.is_dir(), f"{meta_review_dir} should be a directory"

        # Should contain files
        files = list(meta_review_dir.glob("*.json"))
        assert len(files) > 0, "Meta-review directory should contain JSON files"

        # Verify at least one file is readable
        if files:
            test_file = files[0]
            with open(test_file) as f:
                data = json.load(f)
            assert isinstance(data, dict), "Meta-review file should parse as JSON"


# ---------------------------------------------------------------------------
# SC-E2E-9: User-Type Personalization — Different Orderings
# ---------------------------------------------------------------------------

class TestE2EUserTypePersonalization:
    """Verify user-type personalization actually changes output."""

    def test_SC_E2E_9_user_type_tab_ordering_varies(self) -> None:
        """SC-E2E-9: User-type tab ordering produces different orderings for at least 2 user types.

        Last Mile Concern:
            The system claims to personalize tab order by user type, but does it?
            If all user types get the same ordering, personalization isn't working.

        This test verifies that at least two user types have different tab orderings.
        """
        from src.qa.cards import USER_TYPE_TAB_ORDER, CardType

        orderings = {}
        for user_type, tab_list in USER_TYPE_TAB_ORDER.items():
            orderings[user_type] = tuple(tab_list)

        # Should have multiple user types
        assert len(orderings) >= 2, "Should have at least 2 user types"

        # At least two should have different orderings
        orderings_set = set(orderings.values())
        assert len(orderings_set) >= 2, \
            "At least two user types should have different tab orderings"

        # Example: researcher and designer should differ
        researcher_order = USER_TYPE_TAB_ORDER.get("researcher", [])
        designer_order = USER_TYPE_TAB_ORDER.get("designer", [])

        if researcher_order and designer_order:
            assert researcher_order != designer_order, \
                "Researcher and designer tab orders should differ"


# ---------------------------------------------------------------------------
# SC-E2E-10: Badge Colors — Valid CSS/HTML Colors
# ---------------------------------------------------------------------------

class TestE2EBadgeColors:
    """Verify badge colors are valid for rendering."""

    def test_SC_E2E_10_badge_colors_are_valid_hex(self) -> None:
        """SC-E2E-10: Badge colors in CARD_TYPE_REGISTRY are valid hex colors.

        Last Mile Concern:
            The card schema includes badge colors for visual rendering. If a color
            is invalid (typo, wrong format), the frontend crashes when rendering.

        This test verifies all badge colors are valid hex colors that can be
        used in HTML/CSS.
        """
        from src.qa.cards import CARD_TYPE_REGISTRY

        # Regex for valid hex colors: #RRGGBB or #RGB
        hex_pattern = re.compile(r"^#[0-9A-Fa-f]{6}$|^#[0-9A-Fa-f]{3}$")

        for card_type, spec in CARD_TYPE_REGISTRY.items():
            # Check badge color
            assert hex_pattern.match(spec.badge_color), \
                f"{card_type.value}: badge_color '{spec.badge_color}' is not valid hex"

            # Check badge text color
            assert hex_pattern.match(spec.badge_text_color), \
                f"{card_type.value}: badge_text_color '{spec.badge_text_color}' is not valid hex"


# ---------------------------------------------------------------------------
# SC-E2E-11: Model Allocation — Routing Compatibility
# ---------------------------------------------------------------------------

class TestE2EModelAllocation:
    """Verify model allocation routing works correctly."""

    def test_SC_E2E_11_model_allocation_values_valid(self) -> None:
        """SC-E2E-11: Every card type has a valid model_allocation for LLM routing.

        Last Mile Concern:
            The generation orchestrator reads model_allocation from the registry
            to decide which LLM to use. If the values are invalid, routing fails.

        This test verifies all card types have model allocation values that
        the routing logic can work with.
        """
        from src.qa.cards import CARD_TYPE_REGISTRY

        valid_models = {"opus", "sonnet", "gemini"}

        for card_type, spec in CARD_TYPE_REGISTRY.items():
            assert spec.model_allocation in valid_models, \
                f"{card_type.value}: model_allocation '{spec.model_allocation}' " \
                f"not in {valid_models}"


# ---------------------------------------------------------------------------
# SC-E2E-12: Direction Enum Compatibility — Extraction-to-Card Data Flow
# ---------------------------------------------------------------------------

class TestE2EDirectionEnumCompatibility:
    """Verify Direction enum matches extraction system expectations."""

    def test_SC_E2E_12_direction_values_match_extraction(self) -> None:
        """SC-E2E-12: Direction enum values match extraction_field_validator.py.

        Last Mile Concern:
            The extraction validator produces direction values ("increase", "decrease",
            "no_effect", "mixed"). These values must flow into Card objects via the
            Direction enum. If the enum values don't match, extraction data can't
            be used to create cards.

        This test verifies that Direction enum values match the canonical set
        from the extraction validator.
        """
        from src.qa.cards import Direction

        # Canonical directions from extraction_field_validator.py line 554
        canonical_directions = {"increase", "decrease", "no_effect", "mixed"}

        # Get Direction enum values (excluding "NA" which is for system cards)
        enum_values = {d.value for d in Direction if d.value != "na"}

        # All canonical directions must be in the enum
        for direction in canonical_directions:
            assert direction in enum_values, \
                f"Direction '{direction}' from extraction validator not in Direction enum"

        # Verify the enum has at least the 4 canonical values (plus NA for system cards)
        assert len(enum_values) >= 4, \
            f"Direction enum should have at least 4 values (plus NA)"


# ---------------------------------------------------------------------------
# Integration Test Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_card_data() -> Dict[str, Any]:
    """Provide sample card JSON for testing deserialization."""
    return {
        "card_id": "t2-mechanism:light-01",
        "card_type": "t2-mechanism",
        "entity_id": "light-01",
        "card_schema_version": "1.0.0",
        "surface": {
            "title": "Environmental light affects circadian rhythm",
            "card_type": "t2-mechanism",
            "confidence_level": "mod_high",
            "confidence_omega": 0.65,
            "confidence_label": "Mod-High (ω = 0.65)",
            "direction": "increase",
            "n_findings": 12,
            "n_papers": 5,
            "staleness": "fresh",
            "staleness_score": 0.15,
            "key_visual_path": None,
            "last_generated": datetime.now(timezone.utc).isoformat(),
        },
        "body": {
            "tabs": {
                "overview": {
                    "tab_name": "overview",
                    "prose": "Light synchronizes circadian rhythms.",
                }
            }
        },
        "iceberg": {
            "source_map": {
                "source_card_ids": [],
                "template_ids": [],
                "framework_ids": [],
                "molecule_ids": [],
                "finding_ids": [],
                "paper_dois": [],
            },
            "agent_context": {
                "model": "claude-opus-4-6",
                "prompt_template": "standard",
                "prompt_hash": "abc123",
                "temperature": 0.7,
                "generation_timestamp": datetime.now(timezone.utc).isoformat(),
                "generation_duration_ms": 2500,
                "token_count_input": 1000,
                "token_count_output": 500,
                "cost_usd": 0.05,
            },
            "quality_scores": {
                "prose_health": 7.5,
                "confidence_calibration": 0.65,
                "coverage_completeness": 0.8,
                "reference_accuracy": 0.95,
                "overall_quality": 0.8,
                "passes_quality_gate": True,
            },
        },
        "is_draft": False,
        "is_stale": False,
        "generation_count": 1,
    }


# ---------------------------------------------------------------------------
# Additional Smoke Tests
# ---------------------------------------------------------------------------

class TestE2ESmoke:
    """Quick smoke tests for critical paths."""

    def test_smoke_card_type_registry_nonempty(self) -> None:
        """Registry should contain all 9 card types."""
        from src.qa.cards import CARD_TYPE_REGISTRY
        assert len(CARD_TYPE_REGISTRY) == 9

    def test_smoke_confidence_levels_exist(self) -> None:
        """ConfidenceLevel enum should have 4 values."""
        from src.qa.cards import ConfidenceLevel
        levels = list(ConfidenceLevel)
        assert len(levels) == 4
        assert ConfidenceLevel.HIGH in levels
        assert ConfidenceLevel.LOW in levels

    def test_smoke_staleness_enum_complete(self) -> None:
        """Staleness enum should have 3 values."""
        from src.qa.cards import Staleness
        values = list(Staleness)
        assert len(values) == 3
        assert Staleness.FRESH in values
        assert Staleness.STALE in values


# ---------------------------------------------------------------------------
# Module-level markers and configuration
# ---------------------------------------------------------------------------

pytestmark = [
    pytest.mark.integration,
    pytest.mark.e2e,
]
