"""
Tests for ART (Attention Restoration Theory) Reduction.

Sprint 12 Task 12.1: Verify ART constructs reduce correctly to template mechanisms.
"""

import pytest
import json
from pathlib import Path

from src.cmr.reductions.art_reduction import (
    ART_REDUCTIONS,
    reduce_art_construct,
    get_art_template_coverage,
    get_art_constructs,
    get_art_summary,
    export_art_reductions_json,
    ConstructReduction,
)


class TestARTReductionBasics:
    """Basic functionality tests."""

    def test_all_constructs_defined(self):
        """All five ART constructs should be defined."""
        expected = ["Being_Away", "Fascination_Soft", "Fascination_Hard", "Extent", "Compatibility"]
        for construct in expected:
            assert construct in ART_REDUCTIONS, f"Missing construct: {construct}"

    def test_reduce_art_construct_returns_reduction(self):
        """reduce_art_construct should return ConstructReduction for valid input."""
        result = reduce_art_construct("Being_Away")
        assert result is not None
        assert isinstance(result, ConstructReduction)
        assert result.theory == "ART"
        assert result.construct == "Being_Away"

    def test_reduce_art_construct_normalizes_input(self):
        """reduce_art_construct should normalize spaces and dashes."""
        result1 = reduce_art_construct("Being_Away")
        result2 = reduce_art_construct("Being Away")
        result3 = reduce_art_construct("Being-Away")
        assert result1 is not None
        assert result1 == result2 == result3

    def test_reduce_art_construct_returns_none_for_invalid(self):
        """reduce_art_construct should return None for unknown constructs."""
        result = reduce_art_construct("NotARealConstruct")
        assert result is None


class TestBeingAwayReduction:
    """Tests for Being Away construct reduction."""

    def test_being_away_has_view1(self):
        """Being Away should map to VIEW1."""
        result = reduce_art_construct("Being_Away")
        template_ids = [m.template_id for m in result.template_mappings]
        assert "VIEW1" in template_ids

    def test_being_away_has_sc2(self):
        """Being Away should map to SC2 (vista/prospect)."""
        result = reduce_art_construct("Being_Away")
        template_ids = [m.template_id for m in result.template_mappings]
        assert "SC2" in template_ids

    def test_being_away_has_vf3(self):
        """Being Away should map to VF3 (R_h ratio)."""
        result = reduce_art_construct("Being_Away")
        template_ids = [m.template_id for m in result.template_mappings]
        assert "VF3" in template_ids

    def test_being_away_coverage_approximately_85(self):
        """Being Away total coverage should be approximately 0.85."""
        result = reduce_art_construct("Being_Away")
        assert abs(result.total_coverage - 0.85) < 0.01

    def test_being_away_has_irreducible_residual(self):
        """Being Away should document intentional component as residual."""
        result = reduce_art_construct("Being_Away")
        assert "intentional" in result.irreducible_residual.lower()


class TestFascinationSoftReduction:
    """Tests for Soft Fascination construct reduction."""

    def test_soft_fascination_has_view1(self):
        """Soft Fascination should map to VIEW1."""
        result = reduce_art_construct("Fascination_Soft")
        template_ids = [m.template_id for m in result.template_mappings]
        assert "VIEW1" in template_ids

    def test_soft_fascination_has_vf1(self):
        """Soft Fascination should map to VF1 (contour curvature)."""
        result = reduce_art_construct("Fascination_Soft")
        template_ids = [m.template_id for m in result.template_mappings]
        assert "VF1" in template_ids

    def test_soft_fascination_coverage_approximately_90(self):
        """Soft Fascination total coverage should be approximately 0.90."""
        result = reduce_art_construct("Fascination_Soft")
        assert abs(result.total_coverage - 0.90) < 0.01

    def test_soft_fascination_high_confidence(self):
        """Soft Fascination should have high confidence."""
        result = reduce_art_construct("Fascination_Soft")
        assert result.confidence == "high"


class TestFascinationHardReduction:
    """Tests for Hard Fascination construct reduction."""

    def test_hard_fascination_has_crea2(self):
        """Hard Fascination should map to CREA2 (disfluency pathway)."""
        result = reduce_art_construct("Fascination_Hard")
        template_ids = [m.template_id for m in result.template_mappings]
        assert "CREA2" in template_ids

    def test_hard_fascination_lower_coverage(self):
        """Hard Fascination should have lower coverage (~0.70)."""
        result = reduce_art_construct("Fascination_Hard")
        assert result.total_coverage < 0.80  # Lower than soft fascination


class TestExtentReduction:
    """Tests for Extent construct reduction."""

    def test_extent_has_spatial_templates(self):
        """Extent should map to spatial cognition templates."""
        result = reduce_art_construct("Extent")
        template_ids = [m.template_id for m in result.template_mappings]
        assert "SC1" in template_ids  # Legibility
        assert "SC3" in template_ids or "SC4" in template_ids  # Path/wayfinding

    def test_extent_has_view1(self):
        """Extent should map to VIEW1 (depth/openness)."""
        result = reduce_art_construct("Extent")
        template_ids = [m.template_id for m in result.template_mappings]
        assert "VIEW1" in template_ids


class TestCompatibilityReduction:
    """Tests for Compatibility construct reduction."""

    def test_compatibility_has_soc2(self):
        """Compatibility should map to SOC2 (privacy-encounter match)."""
        result = reduce_art_construct("Compatibility")
        template_ids = [m.template_id for m in result.template_mappings]
        assert "SOC2" in template_ids

    def test_compatibility_has_task_match_templates(self):
        """Compatibility should include task-environment match templates."""
        result = reduce_art_construct("Compatibility")
        template_ids = [m.template_id for m in result.template_mappings]
        # Should have at least one of CREA4 or MAT1
        assert "CREA4" in template_ids or "MAT1" in template_ids


class TestCoverageValidation:
    """Validate coverage values are sensible."""

    def test_all_coverages_between_0_and_1(self):
        """All coverage values should be between 0 and 1."""
        for construct_name, reduction in ART_REDUCTIONS.items():
            for mapping in reduction.template_mappings:
                assert 0.0 <= mapping.coverage <= 1.0, (
                    f"{construct_name}/{mapping.template_id}: coverage {mapping.coverage} out of range"
                )

    def test_total_coverage_not_over_1(self):
        """Total coverage should not exceed 1.0."""
        for construct_name, reduction in ART_REDUCTIONS.items():
            assert reduction.total_coverage <= 1.0, (
                f"{construct_name}: total coverage {reduction.total_coverage} exceeds 1.0"
            )

    def test_total_coverage_matches_sum(self):
        """Total coverage should approximately match sum of individual coverages."""
        for construct_name, reduction in ART_REDUCTIONS.items():
            sum_coverage = sum(m.coverage for m in reduction.template_mappings)
            assert abs(reduction.total_coverage - sum_coverage) < 0.01, (
                f"{construct_name}: total {reduction.total_coverage} != sum {sum_coverage}"
            )


class TestReverseLookup:
    """Test reverse lookup functionality."""

    def test_view1_used_by_multiple_constructs(self):
        """VIEW1 should be used by multiple ART constructs."""
        usages = get_art_template_coverage("VIEW1")
        assert len(usages) >= 3  # Being Away, Soft Fascination, Extent

    def test_reverse_lookup_includes_mechanism(self):
        """Reverse lookup should include mechanism description."""
        usages = get_art_template_coverage("VIEW1")
        assert all("mechanism" in u for u in usages)

    def test_reverse_lookup_returns_empty_for_unused(self):
        """Reverse lookup should return empty list for unused templates."""
        usages = get_art_template_coverage("NONEXISTENT")
        assert usages == []


class TestSummary:
    """Test summary statistics."""

    def test_summary_has_correct_construct_count(self):
        """Summary should report 5 constructs."""
        summary = get_art_summary()
        assert summary["n_constructs"] == 5

    def test_summary_has_templates_used(self):
        """Summary should list all templates used."""
        summary = get_art_summary()
        assert "VIEW1" in summary["templates_used"]
        assert "SC2" in summary["templates_used"]

    def test_summary_average_coverage(self):
        """Summary should report average coverage."""
        summary = get_art_summary()
        assert 0.70 <= summary["average_coverage"] <= 0.90


class TestJSONExport:
    """Test JSON export functionality."""

    def test_export_returns_dict(self):
        """Export should return a dictionary."""
        data = export_art_reductions_json()
        assert isinstance(data, dict)
        assert data["theory"] == "ART"

    def test_export_has_all_constructs(self):
        """Export should include all constructs."""
        data = export_art_reductions_json()
        for construct in ["Being_Away", "Fascination_Soft", "Fascination_Hard", "Extent", "Compatibility"]:
            assert construct in data["constructs"]

    def test_json_file_exists(self):
        """Pre-exported JSON file should exist."""
        json_path = Path("data/reductions/art_reduction.json")
        assert json_path.exists()

    def test_json_file_valid(self):
        """Pre-exported JSON file should be valid JSON."""
        json_path = Path("data/reductions/art_reduction.json")
        with open(json_path) as f:
            data = json.load(f)
        assert data["theory"] == "ART"
        assert "Being_Away" in data["constructs"]


class TestIrreducibleResiduals:
    """Test that irreducible residuals are documented."""

    def test_all_constructs_have_residual(self):
        """Every construct should document irreducible residual."""
        for construct_name, reduction in ART_REDUCTIONS.items():
            assert reduction.irreducible_residual, f"{construct_name} missing irreducible residual"
            assert len(reduction.irreducible_residual) > 20, f"{construct_name} residual too short"

    def test_residuals_are_substantive(self):
        """Residuals should explain what cannot be reduced."""
        keywords = ["cannot", "not captured", "individual", "subjective", "goal",
                    "transcends", "not fully", "varies", "beyond", "residual"]
        for construct_name, reduction in ART_REDUCTIONS.items():
            residual = reduction.irreducible_residual.lower()
            # Should mention limitations, not just restate the construct
            assert any(word in residual for word in keywords), (
                f"{construct_name} residual doesn't explain limitation"
            )
