"""Tests for SRT (Stress Recovery Theory) Reduction. Sprint 12 Task 12.2."""

import pytest
import json
from pathlib import Path
from src.cmr.reductions.srt_reduction import (
    SRT_REDUCTIONS, reduce_srt_construct, get_srt_template_coverage,
    get_srt_constructs, get_srt_summary, export_srt_reductions_json,
)


class TestSRTReductionBasics:
    def test_all_constructs_defined(self):
        expected = ["Autonomic_Stress_Reduction", "Affective_Response", "Approach_Avoidance"]
        for construct in expected:
            assert construct in SRT_REDUCTIONS

    def test_reduce_srt_construct_returns_reduction(self):
        result = reduce_srt_construct("Autonomic_Stress_Reduction")
        assert result is not None
        assert result.theory == "SRT"

    def test_reduce_srt_construct_returns_none_for_invalid(self):
        assert reduce_srt_construct("NotARealConstruct") is None


class TestAutonomicStressReduction:
    def test_has_view1(self):
        result = reduce_srt_construct("Autonomic_Stress_Reduction")
        template_ids = [m.template_id for m in result.template_mappings]
        assert "VIEW1" in template_ids

    def test_has_mat4(self):
        result = reduce_srt_construct("Autonomic_Stress_Reduction")
        template_ids = [m.template_id for m in result.template_mappings]
        assert "MAT4" in template_ids

    def test_coverage_approximately_70(self):
        result = reduce_srt_construct("Autonomic_Stress_Reduction")
        assert abs(result.total_coverage - 0.70) < 0.01


class TestAffectiveResponse:
    def test_has_vf1(self):
        result = reduce_srt_construct("Affective_Response")
        template_ids = [m.template_id for m in result.template_mappings]
        assert "VF1" in template_ids

    def test_has_col1(self):
        result = reduce_srt_construct("Affective_Response")
        template_ids = [m.template_id for m in result.template_mappings]
        assert "COL1" in template_ids


class TestApproachAvoidance:
    def test_has_sc2(self):
        result = reduce_srt_construct("Approach_Avoidance")
        template_ids = [m.template_id for m in result.template_mappings]
        assert "SC2" in template_ids

    def test_low_confidence(self):
        result = reduce_srt_construct("Approach_Avoidance")
        assert result.confidence == "low"


class TestCoverageValidation:
    def test_all_coverages_valid(self):
        for construct_name, reduction in SRT_REDUCTIONS.items():
            for mapping in reduction.template_mappings:
                assert 0.0 <= mapping.coverage <= 1.0
            assert reduction.total_coverage <= 1.0

    def test_total_matches_sum(self):
        for construct_name, reduction in SRT_REDUCTIONS.items():
            sum_coverage = sum(m.coverage for m in reduction.template_mappings)
            assert abs(reduction.total_coverage - sum_coverage) < 0.01


class TestSummaryAndExport:
    def test_summary_has_3_constructs(self):
        summary = get_srt_summary()
        assert summary["n_constructs"] == 3

    def test_export_returns_dict(self):
        data = export_srt_reductions_json()
        assert data["theory"] == "SRT"

    def test_json_file_exists(self):
        assert Path("data/reductions/srt_reduction.json").exists()


class TestReverseLookup:
    def test_view1_used_by_autonomic(self):
        usages = get_srt_template_coverage("VIEW1")
        constructs = [u["construct"] for u in usages]
        assert "Autonomic_Stress_Reduction" in constructs
