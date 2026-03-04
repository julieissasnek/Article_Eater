"""
Tests for corpus-grounded framework voices.

Validates that:
1. MV builder produces real corpus data (not empty stubs)
2. get_theoretical_voices() returns different content for different topics
3. Quarantine labels are present when voices are templated
4. Each voice includes n_papers and source metadata
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# MV Builder tests
# ---------------------------------------------------------------------------

class TestMVBuilderFrameworkVoices:
    """Test the MaterializedViewBuilder.build_framework_voices() method."""

    def test_build_returns_all_10_frameworks(self):
        """All 10 T1 frameworks should be present in output."""
        from src.qa.mv_builder import MaterializedViewBuilder
        builder = MaterializedViewBuilder()
        voices = builder.build_framework_voices()

        assert isinstance(voices, dict)
        assert "error" not in voices

        expected = {"PP", "SN", "DP", "DT", "NM", "IC", "MS", "EC", "CB", "MSI"}
        assert set(voices.keys()) == expected, (
            f"Missing frameworks: {expected - set(voices.keys())}"
        )

    def test_each_framework_has_required_fields(self):
        """Each framework voice entry must have corpus-grounded fields."""
        from src.qa.mv_builder import MaterializedViewBuilder
        builder = MaterializedViewBuilder()
        voices = builder.build_framework_voices()

        required_fields = {
            "framework", "name", "n_papers", "n_findings",
            "top_findings", "mechanism_chains", "study_designs",
            "scope_conditions", "source",
        }

        for abbr, data in voices.items():
            for field in required_fields:
                assert field in data, f"{abbr} missing field: {field}"

    def test_source_is_corpus_grounded(self):
        """All voices should report source as 'corpus_grounded'."""
        from src.qa.mv_builder import MaterializedViewBuilder
        builder = MaterializedViewBuilder()
        voices = builder.build_framework_voices()

        for abbr, data in voices.items():
            assert data["source"] == "corpus_grounded", (
                f"{abbr} has source={data['source']}, expected 'corpus_grounded'"
            )

    def test_paper_counts_are_nonzero(self):
        """With the real corpus, each framework should have at least some papers."""
        from src.qa.mv_builder import MaterializedViewBuilder
        builder = MaterializedViewBuilder()
        voices = builder.build_framework_voices()

        # At minimum, PP and NM should have papers (they're the most common)
        assert voices["PP"]["n_papers"] > 0, "PP should have papers"
        assert voices["NM"]["n_papers"] > 0, "NM should have papers"

    def test_top_findings_have_content(self):
        """Top findings should include antecedent/consequent data."""
        from src.qa.mv_builder import MaterializedViewBuilder
        builder = MaterializedViewBuilder()
        voices = builder.build_framework_voices()

        for abbr, data in voices.items():
            if data["n_findings"] > 0:
                assert len(data["top_findings"]) > 0, (
                    f"{abbr} has {data['n_findings']} findings but empty top_findings"
                )
                first = data["top_findings"][0]
                assert "antecedent" in first
                assert "consequent" in first

    def test_empty_extractions_dir_returns_zero_counts(self):
        """With no extraction files, all counts should be zero."""
        from src.qa.mv_builder import MaterializedViewBuilder

        with tempfile.TemporaryDirectory() as tmpdir:
            builder = MaterializedViewBuilder(
                extractions_dir=tmpdir,
                output_dir=os.path.join(tmpdir, "output"),
            )
            voices = builder.build_framework_voices()
            # Should still have frameworks (from schema) but with 0 papers
            if "error" not in voices:
                for abbr, data in voices.items():
                    assert data["n_papers"] == 0
                    assert data["n_findings"] == 0


# ---------------------------------------------------------------------------
# IntegratedQueryService tests
# ---------------------------------------------------------------------------

class TestGetTheoreticalVoices:
    """Test the IntegratedQueryService.get_theoretical_voices() method."""

    def test_returns_dict(self):
        """Should always return a dict."""
        from src.services.integrated_query_service import IntegratedQueryService
        svc = IntegratedQueryService(use_embeddings=False)
        result = svc.get_theoretical_voices("daylight")
        assert isinstance(result, dict)

    def test_voices_have_source_field(self):
        """Every voice must declare its source."""
        from src.services.integrated_query_service import IntegratedQueryService
        svc = IntegratedQueryService(use_embeddings=False)
        result = svc.get_theoretical_voices("stress reduction")

        for name, data in result.items():
            assert "source" in data, f"Voice '{name}' missing 'source' field"
            assert data["source"] in ("corpus_grounded", "framework_template")

    def test_quarantine_label_on_fallback(self):
        """When corpus is unavailable, voices must have quarantine_notice."""
        from src.services.integrated_query_service import IntegratedQueryService

        svc = IntegratedQueryService(use_embeddings=False)

        # Force fallback by making MV builder fail
        with patch("src.qa.mv_builder.MaterializedViewBuilder") as MockBuilder:
            MockBuilder.side_effect = ImportError("test")
            result = svc.get_theoretical_voices("test topic")

            for name, data in result.items():
                assert data["source"] == "framework_template"
                assert "quarantine_notice" in data

    def test_limit_respected(self):
        """Should not return more frameworks than limit."""
        from src.services.integrated_query_service import IntegratedQueryService
        svc = IntegratedQueryService(use_embeddings=False)

        for limit in [1, 2, 3, 4]:
            result = svc.get_theoretical_voices("nature", limit=limit)
            assert len(result) <= limit, (
                f"Got {len(result)} voices with limit={limit}"
            )

    def test_different_topics_get_different_rankings(self):
        """Different topics should surface different framework rankings."""
        from src.services.integrated_query_service import IntegratedQueryService
        svc = IntegratedQueryService(use_embeddings=False)

        v_light = svc.get_theoretical_voices("circadian light exposure daylight")
        v_wayfinding = svc.get_theoretical_voices("wayfinding spatial navigation")

        # The top framework should differ (CB for light, SN for wayfinding)
        light_names = list(v_light.keys())
        wayfind_names = list(v_wayfinding.keys())

        # At minimum, the ordering shouldn't be identical
        if light_names and wayfind_names:
            # This is a soft check — if both have the same evidence base,
            # different topics should at least change relevance scores
            light_scores = [v.get("relevance_score", 0) for v in v_light.values()]
            wayfind_scores = [v.get("relevance_score", 0) for v in v_wayfinding.values()]
            # They should not be identical lists
            assert light_names != wayfind_names or light_scores != wayfind_scores, (
                "Different topics produced identical framework rankings"
            )

    def test_n_papers_present(self):
        """Each voice must report paper count."""
        from src.services.integrated_query_service import IntegratedQueryService
        svc = IntegratedQueryService(use_embeddings=False)
        result = svc.get_theoretical_voices("stress")

        for name, data in result.items():
            assert "n_papers" in data, f"Voice '{name}' missing 'n_papers'"
            assert isinstance(data["n_papers"], int)

    def test_corpus_grounded_voices_have_perspective(self):
        """Corpus-grounded voices should have non-empty perspective text."""
        from src.services.integrated_query_service import IntegratedQueryService
        svc = IntegratedQueryService(use_embeddings=False)
        result = svc.get_theoretical_voices("thermal comfort")

        for name, data in result.items():
            assert "perspective" in data
            assert len(data["perspective"]) > 0
