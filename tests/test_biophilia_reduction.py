"""Tests for Biophilia Reduction. Sprint 12 Task 12.3."""

import pytest
from pathlib import Path
from src.cmr.reductions.biophilia_reduction import (
    BIOPHILIA_REDUCTIONS, reduce_biophilia_construct, get_biophilia_template_coverage,
    get_biophilia_constructs, get_biophilia_summary, export_biophilia_reductions_json,
)


class TestBiophiliaReductionBasics:
    def test_all_constructs_defined(self):
        expected = ["Nature_In_Space", "Natural_Analogues", "Nature_Of_Space", "Remaining_Patterns"]
        for c in expected:
            assert c in BIOPHILIA_REDUCTIONS

    def test_reduce_returns_reduction(self):
        result = reduce_biophilia_construct("Nature_In_Space")
        assert result is not None
        assert result.theory == "Biophilia"


class TestNatureInSpace:
    def test_has_view1(self):
        result = reduce_biophilia_construct("Nature_In_Space")
        assert "VIEW1" in [m.template_id for m in result.template_mappings]

    def test_coverage_90(self):
        result = reduce_biophilia_construct("Nature_In_Space")
        assert abs(result.total_coverage - 0.90) < 0.01

    def test_high_confidence(self):
        result = reduce_biophilia_construct("Nature_In_Space")
        assert result.confidence == "high"


class TestNaturalAnalogues:
    def test_has_vf1_vf2(self):
        result = reduce_biophilia_construct("Natural_Analogues")
        template_ids = [m.template_id for m in result.template_mappings]
        assert "VF1" in template_ids
        assert "VF2" in template_ids


class TestNatureOfSpace:
    def test_has_sc2(self):
        result = reduce_biophilia_construct("Nature_Of_Space")
        assert "SC2" in [m.template_id for m in result.template_mappings]


class TestCoverageValidation:
    def test_all_valid(self):
        for name, reduction in BIOPHILIA_REDUCTIONS.items():
            for m in reduction.template_mappings:
                assert 0 <= m.coverage <= 1
            assert reduction.total_coverage <= 1
            sum_cov = sum(m.coverage for m in reduction.template_mappings)
            assert abs(reduction.total_coverage - sum_cov) < 0.01


class TestSummaryAndExport:
    def test_summary_4_constructs(self):
        assert get_biophilia_summary()["n_constructs"] == 4

    def test_export_dict(self):
        data = export_biophilia_reductions_json()
        assert data["theory"] == "Biophilia"

    def test_json_exists(self):
        assert Path("data/reductions/biophilia_reduction.json").exists()


class TestReverseLookup:
    def test_view1_in_nature_in_space(self):
        usages = get_biophilia_template_coverage("VIEW1")
        assert "Nature_In_Space" in [u["construct"] for u in usages]

    def test_mat4_multiple_uses(self):
        usages = get_biophilia_template_coverage("MAT4")
        assert len(usages) >= 2
