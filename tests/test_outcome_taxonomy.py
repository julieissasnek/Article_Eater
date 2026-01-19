"""
Tests for Sprint 4: Extended Outcome Taxonomy

This module tests the outcome taxonomy extensions per the Sprint 4 specification.

Test Cases:
1. Theory-outcome mapping - Verify theory relevance is correctly assigned
2. Epistemic level assignment - Verify outcomes get correct default levels
3. CNFA extensions - Verify architectural outcomes are available
4. Stub outcome management - Verify unresolved terms become stubs
5. Bridge suggestion - Verify cross-domain bridges are suggested
6. Taxonomy export/import - Verify round-trip serialization
"""

import pytest
import json
from pathlib import Path

from src.services.outcome_taxonomy import (
    ExtendedOutcomeTaxonomy,
    ExtendedOutcome,
    THEORY_OUTCOME_RELEVANCE,
    OUTCOME_EPISTEMIC_LEVELS,
    CNFA_OUTCOME_EXTENSIONS,
    CNFA_LOOKUP_EXTENSIONS,
    outcome_to_belief_metadata,
    infer_theory_from_outcomes,
)
from src.services.web_of_belief import EpistemicLevel


class TestTheoryOutcomeMapping:
    """Test Case 1: Theory-outcome mappings."""

    def test_art_maps_to_attention_outcomes(self):
        """Verify ART theory maps to attention-related outcomes."""
        taxonomy = ExtendedOutcomeTaxonomy()

        outcomes = taxonomy.get_outcomes_for_theory("ART", threshold=0.5)
        outcome_ids = [oid for oid, _ in outcomes]

        # ART should map to attention outcomes
        assert any("attention" in oid for oid in outcome_ids)
        assert "cog.attention.sustained" in outcome_ids or "cog.attention" in outcome_ids

    def test_srt_maps_to_stress_outcomes(self):
        """Verify SRT theory maps to stress-related outcomes."""
        taxonomy = ExtendedOutcomeTaxonomy()

        outcomes = taxonomy.get_outcomes_for_theory("SRT", threshold=0.5)
        outcome_ids = [oid for oid, _ in outcomes]

        # SRT should map to stress/affect outcomes
        assert any("stress" in oid or "affect" in oid for oid in outcome_ids)

    def test_reverse_mapping_works(self):
        """Verify outcome → theory mapping works."""
        taxonomy = ExtendedOutcomeTaxonomy()

        theories = taxonomy.get_theories_for_outcome("cog.attention.sustained", threshold=0.3)
        theory_ids = [tid for tid, _ in theories]

        # Sustained attention should be relevant to ART
        assert "ART" in theory_ids

    def test_relevance_scores_are_valid(self):
        """Verify all relevance scores are between 0 and 1."""
        for theory, outcomes in THEORY_OUTCOME_RELEVANCE.items():
            for outcome, score in outcomes.items():
                assert 0 <= score <= 1, f"{theory}/{outcome} has invalid score {score}"


class TestEpistemicLevelAssignment:
    """Test Case 2: Epistemic level assignment."""

    def test_observational_outcomes_have_observational_level(self):
        """Verify physiological outcomes default to OBSERVATIONAL."""
        taxonomy = ExtendedOutcomeTaxonomy()

        alertness = taxonomy.resolve("alertness")
        assert alertness is not None
        assert alertness.epistemic_level == EpistemicLevel.OBSERVATIONAL

    def test_intermediate_outcomes_have_intermediate_level(self):
        """Verify mood outcomes default to INTERMEDIATE."""
        # affect.mood is intermediate (more abstract)
        assert OUTCOME_EPISTEMIC_LEVELS.get("affect.mood") == EpistemicLevel.INTERMEDIATE

    def test_empirical_outcomes_have_empirical_level(self):
        """Verify specific outcomes default to EMPIRICAL."""
        taxonomy = ExtendedOutcomeTaxonomy()

        stress = taxonomy.resolve("stress")
        assert stress is not None
        assert stress.epistemic_level == EpistemicLevel.EMPIRICAL

    def test_hierarchy_fallback_works(self):
        """Verify child outcomes inherit parent levels when not specified."""
        taxonomy = ExtendedOutcomeTaxonomy()

        # If cog.attention.sustained doesn't have explicit level, should inherit from parent
        result = taxonomy.resolve("sustained attention")
        assert result is not None
        assert result.epistemic_level in [EpistemicLevel.EMPIRICAL, EpistemicLevel.INTERMEDIATE]


class TestCNFAExtensions:
    """Test Case 3: CNFA-specific extensions."""

    def test_arch_domain_exists(self):
        """Verify architectural domain is added."""
        taxonomy = ExtendedOutcomeTaxonomy()

        all_outcomes = taxonomy.get_all_outcomes()
        domains = set(o.domain for o in all_outcomes)

        assert "arch" in domains

    def test_arch_outcomes_are_available(self):
        """Verify architectural outcomes can be resolved."""
        taxonomy = ExtendedOutcomeTaxonomy()

        # Test some CNFA outcomes (Expert Panel 4.3: restructured to feature/percept/response)
        spaciousness = taxonomy.resolve("spaciousness")
        assert spaciousness is not None
        assert spaciousness.outcome_id == "arch.percept.openness"  # Restructured per Expert Panel

        biophilic = taxonomy.resolve("biophilic design")
        assert biophilic is not None
        assert biophilic.outcome_id == "arch.environ.biophilic"  # Environmental quality

    def test_cnfa_lookup_entries_work(self):
        """Verify CNFA lookup synonyms resolve correctly."""
        taxonomy = ExtendedOutcomeTaxonomy()

        # Test various synonyms (Expert Panel 4.3: restructured hierarchy)
        assert taxonomy.resolve("daylight").outcome_id == "arch.environ.daylight"  # Environmental
        assert taxonomy.resolve("wayfinding").outcome_id == "arch.wayfinding"  # Top-level wayfinding
        assert taxonomy.resolve("visual complexity").outcome_id == "arch.percept.complexity"  # Percept

    def test_cnfa_outcomes_have_descriptions(self):
        """Verify CNFA outcomes have descriptions."""
        for term_id, term_data in CNFA_OUTCOME_EXTENSIONS.items():
            assert "description" in term_data, f"{term_id} missing description"


class TestStubOutcomeManagement:
    """Test Case 4: Stub outcome management."""

    def test_unresolved_terms_become_stubs(self):
        """Verify unresolved terms create stub outcomes."""
        taxonomy = ExtendedOutcomeTaxonomy()

        result = taxonomy.resolve_or_stub(
            "completely_unknown_outcome_xyz",
            paper_id="test:paper:001"
        )

        assert result is not None
        assert result.is_stub is True
        assert result.outcome_id.startswith("STUB:")
        # Expert Panel 4.4: Stubs now show construct validity, not paper_id
        assert "validity=" in result.stub_reason
        assert "pending" in result.stub_reason

    def test_stubs_are_tracked(self):
        """Verify stubs are added to stub collection."""
        taxonomy = ExtendedOutcomeTaxonomy()

        initial_stubs = len(taxonomy.get_stubs())

        taxonomy.resolve_or_stub("new_unknown_term_abc", paper_id="test:002")

        assert len(taxonomy.get_stubs()) == initial_stubs + 1

    def test_same_unknown_term_reuses_stub(self):
        """Verify same unknown term returns same stub."""
        taxonomy = ExtendedOutcomeTaxonomy()

        stub1 = taxonomy.resolve_or_stub("repeated_unknown_term")
        stub2 = taxonomy.resolve_or_stub("repeated_unknown_term")

        assert stub1.outcome_id == stub2.outcome_id

    def test_stub_domain_inference(self):
        """Verify stub domains are inferred from keywords."""
        taxonomy = ExtendedOutcomeTaxonomy()

        # Should infer cognitive domain
        cog_stub = taxonomy.resolve_or_stub("unknown_attention_measure")
        assert cog_stub.domain == "cog"

        # Should infer affect domain
        affect_stub = taxonomy.resolve_or_stub("unknown_mood_state")
        assert affect_stub.domain == "affect"


class TestBridgeSuggestion:
    """Test Case 5: Bridge suggestion for cross-domain transfer."""

    def test_arch_outcomes_have_bridge_candidates(self):
        """Verify architectural outcomes have bridge candidates."""
        taxonomy = ExtendedOutcomeTaxonomy()

        biophilic = taxonomy._extended_outcomes.get("arch.environ.biophilic")
        if biophilic:
            assert len(biophilic.bridge_candidates) > 0

    def test_bridge_suggestions_return_valid_structure(self):
        """Verify bridge suggestions have required fields."""
        taxonomy = ExtendedOutcomeTaxonomy()

        suggestions = taxonomy.suggest_bridges_for_outcome("arch.environ.biophilic")

        for suggestion in suggestions:
            assert "source_outcome" in suggestion
            assert "target_outcome" in suggestion
            assert "bridge_type" in suggestion
            assert suggestion["bridge_type"] in ["mechanism", "functional", "analogical", "constitutive"]

    def test_bridge_suggestions_cross_domains(self):
        """Verify bridge suggestions connect different domains."""
        taxonomy = ExtendedOutcomeTaxonomy()

        suggestions = taxonomy.suggest_bridges_for_outcome("arch.environ.biophilic")

        # Should suggest bridges to non-arch outcomes
        for suggestion in suggestions:
            source_domain = suggestion["source_domain"]
            target_domain = suggestion["target_domain"]
            # Either source or target should be different from arch
            assert source_domain != target_domain or source_domain != "arch"


class TestTaxonomyExportImport:
    """Test Case 6: Serialization round-trip."""

    def test_export_creates_valid_json(self, tmp_path):
        """Verify export creates valid JSON file."""
        taxonomy = ExtendedOutcomeTaxonomy()

        export_path = tmp_path / "extended_lookup.json"
        taxonomy.export_extended_lookup(export_path)

        assert export_path.exists()

        with open(export_path) as f:
            data = json.load(f)

        assert data["schema"] == "ae.extended_outcome_lookup.v2"  # Expert Panel refinements
        assert "terms" in data
        assert "lookup" in data

    def test_export_includes_cnfa_terms(self, tmp_path):
        """Verify export includes CNFA extensions."""
        taxonomy = ExtendedOutcomeTaxonomy()

        export_path = tmp_path / "extended_lookup.json"
        taxonomy.export_extended_lookup(export_path)

        with open(export_path) as f:
            data = json.load(f)

        # Check for CNFA terms
        assert "arch" in data.get("domains", [])
        assert any("arch." in term_id for term_id in data.get("terms", {}))

    def test_export_includes_theory_relevance(self, tmp_path):
        """Verify export includes theory-outcome mappings."""
        taxonomy = ExtendedOutcomeTaxonomy()

        export_path = tmp_path / "extended_lookup.json"
        taxonomy.export_extended_lookup(export_path)

        with open(export_path) as f:
            data = json.load(f)

        assert "theory_outcome_relevance" in data
        assert "ART" in data["theory_outcome_relevance"]

    def test_import_round_trip(self, tmp_path):
        """Verify taxonomy can be exported and re-imported."""
        original = ExtendedOutcomeTaxonomy()

        # Add a stub
        original.resolve_or_stub("test_unknown_term", paper_id="test:001")

        export_path = tmp_path / "extended_lookup.json"
        original.export_extended_lookup(export_path)

        # Import
        imported = ExtendedOutcomeTaxonomy.from_extended_lookup(export_path)

        # Verify same number of terms
        assert len(imported.get_all_outcomes()) == len(original.get_all_outcomes())

        # Verify stub was preserved
        assert len(imported.get_stubs()) == len(original.get_stubs())


class TestTheoryInference:
    """Test theory inference from outcomes."""

    def test_infer_theory_from_outcomes(self):
        """Verify theory can be inferred from outcome list."""
        taxonomy = ExtendedOutcomeTaxonomy()

        # Get attention-related outcomes
        outcomes = [
            taxonomy.resolve("sustained attention"),
            taxonomy.resolve("selective attention"),
            taxonomy.resolve("working memory")
        ]
        outcomes = [o for o in outcomes if o is not None]

        primary, scores = infer_theory_from_outcomes(outcomes, threshold=0.3)

        # Should infer ART as primary theory
        assert primary == "ART"
        assert "ART" in scores
        assert scores["ART"] > 0.3

    def test_infer_theory_returns_all_relevant(self):
        """Verify all relevant theories are returned in scores."""
        taxonomy = ExtendedOutcomeTaxonomy()

        outcomes = [
            taxonomy.resolve("stress"),
            taxonomy.resolve("anxiety"),
        ]
        outcomes = [o for o in outcomes if o is not None]

        _, scores = infer_theory_from_outcomes(outcomes, threshold=0.2)

        # Should include SRT for stress/anxiety
        assert "SRT" in scores


class TestBeliefMetadataConversion:
    """Test conversion to belief metadata."""

    def test_outcome_to_belief_metadata(self):
        """Verify outcome converts to belief metadata correctly."""
        outcome = ExtendedOutcome(
            outcome_id="cog.attention.sustained",
            name="Sustained Attention",
            domain="cog",
            parent="cog.attention",
            epistemic_level=EpistemicLevel.EMPIRICAL,
            theory_relevance={"ART": 0.9, "SRT": 0.3}
        )

        metadata = outcome_to_belief_metadata(outcome)

        assert metadata["outcome_id"] == "cog.attention.sustained"
        assert metadata["epistemic_level"].upper() == "EMPIRICAL"
        assert metadata["theory_relevance"]["ART"] == 0.9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
