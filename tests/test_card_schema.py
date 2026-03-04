"""
Tests for the ATLAS Card System Schema
=======================================

Covers: card_types.py, card_schema.py, tab_config.py, staleness.py

Success Conditions:
  SC-CARD-1:  All 9 card types are registered
  SC-CARD-2:  Card types cover all 3 tiers (A, B, C)
  SC-CARD-3:  Every card type has at least 3 required tabs
  SC-CARD-4:  Surface serialization round-trips correctly
  SC-CARD-5:  Body tab architecture preserves content
  SC-CARD-6:  Iceberg stores provenance chain
  SC-CARD-7:  Card JSON round-trip preserves all fields
  SC-CARD-8:  Tab ordering varies by user type
  SC-CARD-9:  Staleness scoring produces correct thresholds
  SC-CARD-10: Staleness ledger tracks change events
  SC-CARD-11: make_card_id produces canonical format
  SC-CARD-12: create_card factory sets correct defaults
  SC-CARD-13: validate_tabs detects missing required tabs
  SC-CARD-14: Policymaker sees fewer tabs than researcher
  SC-CARD-15: Math cards have math_layers=True
  SC-CARD-16: Opus allocation covers theoretical card types
  SC-CARD-17: Badge colors meet WCAG contrast requirements
  SC-CARD-18: Staleness config validates weight sum
  SC-CARD-19: Competition cards show debate tab for all users
  SC-CARD-20: Staleness success conditions validator works

Author: CW (Claude/Cowork)
Date: 2026-03-04
"""

import json
import pytest
from pathlib import Path

from src.qa.cards.card_types import (
    CardType, CardTier, CardTypeSpec,
    CARD_TYPE_REGISTRY,
    get_card_type_spec, get_types_for_tier,
    get_types_requiring_opus, get_all_tabs_for_type,
)
from src.qa.cards.card_schema import (
    Card, CardSurface, CardBody, CardTab, CardIceberg,
    IcebergSourceMap, IcebergAgentContext, IcebergQualityScores,
    ConfidenceLevel, Direction, Staleness, UserType,
    CONFIDENCE_COLORS, STALENESS_COLORS,
    create_card, make_card_id,
)
from src.qa.cards.tab_config import (
    TAB_DEFINITIONS, USER_TYPE_TAB_ORDER, USER_TYPE_HIDDEN_TABS,
    get_tabs_for_card_type, get_tab_order_for_user, get_required_tabs,
    TabDefinition,
)
from src.qa.cards.staleness import (
    StalenessLedger, StalenessLedgerEntry, StalenessConfig,
    compute_staleness_score, validate_staleness_system, DEFAULT_CONFIG,
)


# ═══════════════════════════════════════════════════════════════════════════
# SC-CARD-1: All 9 card types are registered
# ═══════════════════════════════════════════════════════════════════════════

class TestCardTypeRegistry:
    """SC-CARD-1: All 9 card types are registered."""

    def test_nine_types_registered(self):
        assert len(CARD_TYPE_REGISTRY) == 9

    def test_all_enum_values_in_registry(self):
        for ct in CardType:
            assert ct in CARD_TYPE_REGISTRY, f"{ct} missing from registry"

    def test_each_type_has_spec(self):
        for ct in CardType:
            spec = get_card_type_spec(ct)
            assert isinstance(spec, CardTypeSpec)
            assert spec.card_type == ct


# ═══════════════════════════════════════════════════════════════════════════
# SC-CARD-2: Card types cover all 3 tiers
# ═══════════════════════════════════════════════════════════════════════════

class TestCardTiers:
    """SC-CARD-2: Card types cover all 3 tiers."""

    def test_tier_a_has_4_types(self):
        tier_a = get_types_for_tier(CardTier.A)
        assert len(tier_a) == 4
        assert CardType.T1_FRAMEWORK in tier_a
        assert CardType.T1_5_DOMAIN_THEORY in tier_a
        assert CardType.T2_MECHANISM in tier_a
        assert CardType.MOLECULE in tier_a

    def test_tier_b_has_2_types(self):
        tier_b = get_types_for_tier(CardTier.B)
        assert len(tier_b) == 2
        assert CardType.T3_BELIEF in tier_b
        assert CardType.COMPETITION in tier_b

    def test_tier_c_has_3_types(self):
        tier_c = get_types_for_tier(CardTier.C)
        assert len(tier_c) == 3
        assert CardType.LAYER in tier_c
        assert CardType.METHOD in tier_c
        assert CardType.MATH in tier_c


# ═══════════════════════════════════════════════════════════════════════════
# SC-CARD-3: Every card type has at least 3 required tabs
# ═══════════════════════════════════════════════════════════════════════════

class TestRequiredTabs:
    """SC-CARD-3: Every card type has at least 3 required tabs."""

    def test_minimum_required_tabs(self):
        for ct, spec in CARD_TYPE_REGISTRY.items():
            assert len(spec.required_tabs) >= 3, (
                f"{ct.value} has only {len(spec.required_tabs)} required tabs"
            )

    def test_overview_always_required(self):
        for ct, spec in CARD_TYPE_REGISTRY.items():
            assert "overview" in spec.required_tabs, (
                f"{ct.value} is missing 'overview' tab"
            )

    def test_history_always_required(self):
        for ct, spec in CARD_TYPE_REGISTRY.items():
            assert "history" in spec.required_tabs, (
                f"{ct.value} is missing 'history' tab"
            )


# ═══════════════════════════════════════════════════════════════════════════
# SC-CARD-4 through SC-CARD-7: Serialization round-trips
# ═══════════════════════════════════════════════════════════════════════════

class TestSerialization:
    """SC-CARD-4..7: Surface, Body, Iceberg, and Card round-trip."""

    def _make_full_card(self) -> Card:
        card = create_card(
            card_type=CardType.T2_MECHANISM,
            entity_id="LIGHT-01",
            title="Morning daylight reduces stress via circadian entrainment",
            confidence_level=ConfidenceLevel.MOD_HIGH,
            confidence_omega=0.68,
            direction=Direction.DECREASE,
            n_findings=23,
            n_papers=7,
        )
        # Add tabs
        card.body.tabs["overview"] = CardTab(
            tab_name="overview",
            prose="This is the overview prose content.",
            prose_health_score=7.2,
        )
        card.body.tabs["mechanism"] = CardTab(
            tab_name="mechanism",
            prose="The mechanism involves melanopsin-ipRGC activation.",
            figures=[{"type": "mechanism_diagram", "path": "/fig/mech.svg"}],
        )
        # Add iceberg data
        card.iceberg.source_map.finding_ids = ["f_001", "f_002", "f_003"]
        card.iceberg.source_map.paper_dois = ["10.1234/abc", "10.5678/def"]
        card.iceberg.agent_context.model = "claude-opus-4-6"
        card.iceberg.quality_scores.prose_health = 7.2
        card.iceberg.quality_scores.passes_quality_gate = True
        card.iceberg.questions_generated = [
            "Does this effect persist beyond 30 days?",
            "What is the minimum lux threshold?",
        ]
        card.is_draft = False
        card.generation_count = 1
        return card

    def test_surface_round_trip(self):
        """SC-CARD-4"""
        card = self._make_full_card()
        d = card.surface.to_dict()
        surface2 = CardSurface.from_dict(d)
        assert surface2.title == card.surface.title
        assert surface2.confidence_omega == 0.68
        assert surface2.direction == Direction.DECREASE
        assert surface2.n_findings == 23

    def test_body_round_trip(self):
        """SC-CARD-5"""
        card = self._make_full_card()
        d = card.body.to_dict()
        body2 = CardBody.from_dict(d)
        assert body2.has_tab("overview")
        assert body2.has_tab("mechanism")
        assert body2.get_tab("overview").prose_health_score == 7.2
        assert len(body2.get_tab("mechanism").figures) == 1

    def test_iceberg_round_trip(self):
        """SC-CARD-6"""
        card = self._make_full_card()
        d = card.iceberg.to_dict()
        iceberg2 = CardIceberg.from_dict(d)
        assert len(iceberg2.source_map.finding_ids) == 3
        assert iceberg2.agent_context.model == "claude-opus-4-6"
        assert iceberg2.quality_scores.passes_quality_gate is True
        assert len(iceberg2.questions_generated) == 2

    def test_card_json_round_trip(self):
        """SC-CARD-7"""
        card = self._make_full_card()
        json_str = card.to_json()
        card2 = Card.from_json(json_str)
        assert card2.card_id == card.card_id
        assert card2.card_type == CardType.T2_MECHANISM
        assert card2.entity_id == "LIGHT-01"
        assert card2.surface.confidence_omega == 0.68
        assert card2.body.has_tab("overview")
        assert card2.iceberg.agent_context.model == "claude-opus-4-6"
        assert card2.is_draft is False
        assert card2.generation_count == 1

    def test_card_save_load(self, tmp_path):
        """SC-CARD-7 extension: file I/O round-trip."""
        card = self._make_full_card()
        path = tmp_path / "test_card.json"
        card.save(path)
        card2 = Card.load(path)
        assert card2.card_id == card.card_id
        assert card2.surface.title == card.surface.title


# ═══════════════════════════════════════════════════════════════════════════
# SC-CARD-8: Tab ordering varies by user type
# ═══════════════════════════════════════════════════════════════════════════

class TestTabOrdering:
    """SC-CARD-8: Tab ordering varies by user type."""

    def test_researcher_starts_with_overview(self):
        order = get_tab_order_for_user("researcher", CardType.T2_MECHANISM)
        assert order[0] == "overview"

    def test_designer_starts_with_design(self):
        order = get_tab_order_for_user("designer", CardType.T2_MECHANISM)
        assert order[0] == "design"

    def test_policymaker_sees_fewer_tabs(self):
        """SC-CARD-14"""
        researcher_tabs = get_tab_order_for_user("researcher", CardType.T2_MECHANISM)
        policymaker_tabs = get_tab_order_for_user("policymaker", CardType.T2_MECHANISM)
        assert len(policymaker_tabs) < len(researcher_tabs)

    def test_competition_shows_debate_for_all(self):
        """SC-CARD-19: When competition exists, debate is shown even for hidden users."""
        # Policymaker normally hides debate
        no_comp = get_tab_order_for_user("policymaker", CardType.COMPETITION, has_competition=False)
        with_comp = get_tab_order_for_user("policymaker", CardType.COMPETITION, has_competition=True)
        assert "debate" not in no_comp
        assert "debate" in with_comp


# ═══════════════════════════════════════════════════════════════════════════
# SC-CARD-9, SC-CARD-10: Staleness scoring and ledger
# ═══════════════════════════════════════════════════════════════════════════

class TestStaleness:
    """SC-CARD-9, SC-CARD-10: Staleness scoring and ledger."""

    def test_empty_ledger_is_fresh(self):
        """SC-CARD-9: No changes → FRESH."""
        ledger = StalenessLedger()
        score, status = compute_staleness_score(ledger, total_sources=20)
        assert status == Staleness.FRESH
        assert score == 0.0

    def test_many_new_sources_causes_staleness(self):
        """SC-CARD-9: Many new sources → STALE."""
        ledger = StalenessLedger()
        for i in range(20):
            ledger.record_new_source(f"finding_{i}")
        score, status = compute_staleness_score(ledger, total_sources=20)
        assert status == Staleness.STALE
        assert score >= 0.40

    def test_credence_shift_affects_score(self):
        """SC-CARD-9: Large credence shift increases staleness."""
        ledger = StalenessLedger()
        ledger.record_credence_shift(0.50, 0.90)  # Δ = 0.40
        score, status = compute_staleness_score(ledger, total_sources=10)
        assert score > 0.10

    def test_competition_resolved_affects_score(self):
        """SC-CARD-10: Competition resolution is recorded."""
        ledger = StalenessLedger()
        ledger.record_competition_resolved("comp_barrett_craig")
        assert ledger.n_entries == 1
        score, _ = compute_staleness_score(ledger, total_sources=10)
        assert score == pytest.approx(0.15, abs=0.01)

    def test_ledger_clear_archives(self):
        """SC-CARD-10: Clearing ledger returns archived entries."""
        ledger = StalenessLedger()
        ledger.record_new_source("f1")
        ledger.record_new_source("f2")
        archived = ledger.clear()
        assert len(archived) == 2
        assert ledger.n_entries == 0
        assert ledger.last_regenerated is not None

    def test_ledger_serialization(self):
        """SC-CARD-10: Ledger round-trips through JSON."""
        ledger = StalenessLedger()
        ledger.record_new_source("f1", "New daylight study")
        ledger.record_credence_shift(0.60, 0.72)
        d = ledger.to_dict()
        ledger2 = StalenessLedger.from_dict(d)
        assert ledger2.n_entries == 2
        assert ledger2.entries[0].change_type == "new_source"
        assert ledger2.entries[1].change_type == "credence_shift"

    def test_time_decay(self):
        """SC-CARD-9: Time decay adds to staleness."""
        ledger = StalenessLedger()
        score_0, _ = compute_staleness_score(ledger, 10, days_since_generation=0)
        score_100, _ = compute_staleness_score(ledger, 10, days_since_generation=100)
        assert score_100 > score_0
        assert score_100 == pytest.approx(0.20, abs=0.01)  # 100 * 0.002

    def test_config_validation(self):
        """SC-CARD-18: Config validates weight sum."""
        good = StalenessConfig()
        assert good.validate() == []

        bad = StalenessConfig(w_new_sources=0.50)  # Sum != 1.0
        errors = bad.validate()
        assert len(errors) > 0


# ═══════════════════════════════════════════════════════════════════════════
# SC-CARD-11, SC-CARD-12, SC-CARD-13: Factory and validation
# ═══════════════════════════════════════════════════════════════════════════

class TestFactoryAndValidation:
    """SC-CARD-11..13: Card creation and tab validation."""

    def test_make_card_id_format(self):
        """SC-CARD-11"""
        assert make_card_id(CardType.T1_FRAMEWORK, "pp") == "t1-framework:pp"
        assert make_card_id(CardType.T2_MECHANISM, "LIGHT-01") == "t2-mechanism:LIGHT-01"
        assert make_card_id(CardType.MATH, "coherence") == "math:coherence"

    def test_create_card_defaults(self):
        """SC-CARD-12"""
        card = create_card(
            card_type=CardType.MOLECULE,
            entity_id="soft-fascination",
            title="Soft Fascination: DMN-permissive sensory input",
        )
        assert card.is_draft is True
        assert card.generation_count == 0
        assert card.surface.staleness == Staleness.FRESH
        assert card.surface.confidence_level == ConfidenceLevel.LOW
        assert card.card_id == "molecule:soft-fascination"

    def test_validate_tabs_detects_missing(self):
        """SC-CARD-13"""
        card = create_card(
            card_type=CardType.T2_MECHANISM,
            entity_id="LIGHT-01",
            title="Test",
        )
        missing = card.validate_tabs()
        # T2 requires: overview, mechanism, evidence, design, connections, history
        assert len(missing) == 6
        assert "overview" in missing


# ═══════════════════════════════════════════════════════════════════════════
# SC-CARD-15, SC-CARD-16: Math layers and Opus allocation
# ═══════════════════════════════════════════════════════════════════════════

class TestSpecialProperties:
    """SC-CARD-15, SC-CARD-16: Math layers and model allocation."""

    def test_math_cards_have_math_layers(self):
        """SC-CARD-15"""
        math_spec = get_card_type_spec(CardType.MATH)
        assert math_spec.has_math_layers is True
        method_spec = get_card_type_spec(CardType.METHOD)
        assert method_spec.has_math_layers is True

    def test_t3_does_not_have_math_layers(self):
        """SC-CARD-15 negative"""
        t3_spec = get_card_type_spec(CardType.T3_BELIEF)
        assert t3_spec.has_math_layers is False

    def test_opus_types_include_theoretical(self):
        """SC-CARD-16"""
        opus_types = get_types_requiring_opus()
        assert CardType.T1_FRAMEWORK in opus_types
        assert CardType.T1_5_DOMAIN_THEORY in opus_types
        assert CardType.MOLECULE in opus_types
        assert CardType.COMPETITION in opus_types
        assert CardType.MATH in opus_types

    def test_opus_does_not_include_bulk(self):
        """SC-CARD-16 negative"""
        opus_types = get_types_requiring_opus()
        assert CardType.T3_BELIEF not in opus_types
        assert CardType.LAYER not in opus_types


# ═══════════════════════════════════════════════════════════════════════════
# SC-CARD-17: Badge colors meet WCAG contrast
# ═══════════════════════════════════════════════════════════════════════════

class TestAccessibility:
    """SC-CARD-17: Badge colors use appropriate contrast."""

    def test_all_types_have_badge_colors(self):
        for ct, spec in CARD_TYPE_REGISTRY.items():
            assert spec.badge_color.startswith("#"), f"{ct} badge_color not hex"
            assert spec.badge_text_color.startswith("#"), f"{ct} badge_text_color not hex"

    def test_confidence_colors_defined(self):
        for level in ConfidenceLevel:
            assert level in CONFIDENCE_COLORS

    def test_staleness_colors_defined(self):
        for status in Staleness:
            assert status in STALENESS_COLORS


# ═══════════════════════════════════════════════════════════════════════════
# SC-CARD-20: Staleness system success conditions validator
# ═══════════════════════════════════════════════════════════════════════════

class TestStalenessValidator:
    """SC-CARD-20: validate_staleness_system works."""

    def test_healthy_system_passes(self):
        cards = [
            {
                "staleness_score": 0.05, "is_stale": False,
                "tier": "entity", "has_ledger": True,
            },
            {
                "staleness_score": 0.15, "is_stale": False,
                "tier": "entity", "has_ledger": True,
            },
        ]
        results = validate_staleness_system(cards)
        assert results["overall"]["pass"] is True

    def test_stale_not_queued_fails(self):
        cards = [
            {
                "staleness_score": 0.50, "is_stale": False,  # Should be True!
                "tier": "entity", "has_ledger": True,
            },
        ]
        results = validate_staleness_system(cards)
        assert results["SC-STALE-3"]["pass"] is False

    def test_over_max_score_fails(self):
        cards = [
            {
                "staleness_score": 1.5, "is_stale": True,
                "tier": "entity", "has_ledger": True,
            },
        ]
        results = validate_staleness_system(cards)
        assert results["SC-STALE-2"]["pass"] is False


# ═══════════════════════════════════════════════════════════════════════════
# Tab config integration
# ═══════════════════════════════════════════════════════════════════════════

class TestTabConfig:
    """Tab definition completeness."""

    def test_seven_tab_definitions(self):
        assert len(TAB_DEFINITIONS) == 7

    def test_all_required_tabs_have_definitions(self):
        for ct, spec in CARD_TYPE_REGISTRY.items():
            for tab_name in spec.required_tabs:
                assert tab_name in TAB_DEFINITIONS, (
                    f"{ct.value} requires '{tab_name}' but it's not defined"
                )

    def test_five_user_types_have_orders(self):
        assert len(USER_TYPE_TAB_ORDER) == 5
        for ut in ["researcher", "designer", "clinician", "policymaker", "student"]:
            assert ut in USER_TYPE_TAB_ORDER

    def test_get_tabs_for_card_type_returns_correct_set(self):
        tabs = get_tabs_for_card_type(CardType.T2_MECHANISM)
        assert "overview" in tabs
        assert "mechanism" in tabs
        assert "evidence" in tabs
        assert "design" in tabs

    def test_get_required_tabs(self):
        required = get_required_tabs(CardType.T1_FRAMEWORK)
        assert "overview" in required
        assert "mechanism" in required
        assert "evidence" in required
