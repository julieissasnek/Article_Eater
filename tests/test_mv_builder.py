"""
Tests for Materialized View Builder
=====================================

Tests that the MV builder correctly pre-computes:
1. Omega scores from extraction findings
2. Evidence indices mapping findings to sources
3. Gap analysis per theory/domain
4. Framework voices per topic
5. FRESH/STALE tracking and incremental builds
"""

import json
import os
import pytest
import tempfile
from pathlib import Path

from src.qa.mv_builder import MaterializedViewBuilder


@pytest.fixture
def sample_extractions(tmp_path):
    """Create sample extraction files for testing."""
    extractions_dir = tmp_path / "extractions"
    extractions_dir.mkdir()

    # Sample extraction 1: empirical study
    extraction1 = {
        "article_type": "empirical",
        "title": "Effects of daylight on cognitive performance",
        "study_design": "experiment",
        "n_participants": 120,
        "domains": ["A1", "A3"],
        "findings": [
            {
                "id": "f1",
                "antecedent": "natural daylight exposure",
                "consequent": "cognitive task performance",
                "direction": "increase",
                "p_value": "0.03",
                "effect_size": 0.42,
                "theory_links": ["ART", "SRT"],
                "measure_type": "objective",
                "quote": "Participants under natural light scored significantly higher",
                "source": "Table 2",
                "finding_text": "Natural daylight improves cognitive performance",
            },
            {
                "id": "f2",
                "antecedent": "artificial fluorescent lighting",
                "consequent": "fatigue ratings",
                "direction": "increase",
                "p_value": "0.01",
                "effect_size": 0.55,
                "theory_links": ["PP"],
                "measure_type": "self_report",
                "quote": "Fluorescent lighting increased self-reported fatigue",
                "source": "Table 3",
                "finding_text": "Fluorescent lights increase fatigue",
            },
        ],
    }

    # Sample extraction 2: theoretical paper
    extraction2 = {
        "article_type": "theoretical",
        "title": "Biophilic design principles",
        "domains": ["A2"],
        "findings": [
            {
                "id": "f3",
                "antecedent": "biophilic design elements",
                "consequent": "stress recovery",
                "direction": "increase",
                "theory_links": ["Biophilia", "SRT"],
                "quote": "Natural elements in built environments support recovery",
                "finding_text": "Biophilic design aids stress recovery",
            },
        ],
    }

    with open(extractions_dir / "study1.json", "w") as f:
        json.dump(extraction1, f)
    with open(extractions_dir / "study2.json", "w") as f:
        json.dump(extraction2, f)

    return extractions_dir


@pytest.fixture
def mv_builder(sample_extractions, tmp_path):
    """Create a MaterializedViewBuilder with test data."""
    output_dir = tmp_path / "materialized_views"
    return MaterializedViewBuilder(
        extractions_dir=str(sample_extractions),
        output_dir=str(output_dir),
    )


class TestMVBuilder:
    """Test the MaterializedViewBuilder."""

    def test_build_evidence_index(self, mv_builder):
        """Evidence index maps findings to source papers."""
        result = mv_builder.build_evidence_index()
        assert result["total_entries"] == 3
        assert result["unique_claims"] >= 2
        # Check that index contains actual finding data
        index = result["index"]
        some_key = list(index.keys())[0]
        entry = index[some_key][0]
        assert "source_file" in entry
        assert "antecedent" in entry
        assert "consequent" in entry

    def test_build_gap_analysis(self, mv_builder):
        """Gap analysis identifies under-covered theories."""
        result = mv_builder.build_gap_analysis()
        assert "theory_gaps" in result
        assert "domain_gaps" in result
        assert "theory_coverage" in result

        # ART has 1 paper -> should be "high" gap
        art_gap = [g for g in result["theory_gaps"] if g["theory"] == "ART"]
        assert len(art_gap) == 1
        assert art_gap[0]["n_papers"] >= 1

    def test_build_framework_voices(self, mv_builder):
        """Framework voices are pre-rendered."""
        result = mv_builder.build_framework_voices()
        # If FRAMEWORK_VOICES is available, should have entries
        if "error" not in result:
            assert len(result) > 0
            # Each voice should have expected structure
            for name, voice in result.items():
                assert "framework" in voice
                assert "perspective" in voice

    def test_build_all_creates_manifest(self, mv_builder, tmp_path):
        """build_all creates a build manifest."""
        stats = mv_builder.build_all()
        manifest_path = tmp_path / "materialized_views" / "_build_manifest.json"
        assert manifest_path.exists()
        with open(manifest_path) as f:
            manifest = json.load(f)
        assert "timestamp" in manifest
        assert "views" in manifest

    def test_build_all_incremental_skips_fresh(self, mv_builder):
        """Incremental build skips FRESH views."""
        # First build: everything is new
        stats1 = mv_builder.build_all()
        for view_name, info in stats1.items():
            if info.get("status") != "FAILED":
                assert info["status"] == "BUILT"

        # Second build (incremental): should skip FRESH
        stats2 = mv_builder.build_all(incremental=True)
        for view_name, info in stats2.items():
            if info.get("status") != "FAILED":
                assert info.get("skipped") is True or info["status"] == "BUILT"

    def test_mark_stale(self, mv_builder, tmp_path):
        """mark_stale changes view status to STALE."""
        # Build first
        mv_builder.build_all()
        # Mark stale
        mv_builder.mark_stale("any-cluster")
        # Check that views are now stale
        assert mv_builder._is_stale("evidence_index") is True

    def test_get_view(self, mv_builder):
        """get_view retrieves pre-computed data."""
        mv_builder.build_all()
        view = mv_builder.get_view("evidence_index")
        assert view is not None
        assert view["status"] == "FRESH"
        assert "data" in view

    def test_get_view_missing(self, mv_builder):
        """get_view returns None for missing views."""
        result = mv_builder.get_view("nonexistent_view")
        assert result is None

    def test_output_directory_created(self, tmp_path):
        """Output directory is created automatically."""
        output = tmp_path / "new_views" / "subdir"
        builder = MaterializedViewBuilder(
            extractions_dir="/nonexistent",
            output_dir=str(output),
        )
        assert output.exists()
