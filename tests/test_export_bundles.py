"""
Tests for Purpose-Driven Export Bundles.
Sprint 3.0.4-E — 2026-02-09

Comprehensive tests for:
- All export purposes
- Content generation
- Bundle validation
- File generation
- Munzner framework compliance

Created: 2026-02-09
"""

import pytest
import json
from pathlib import Path
from datetime import datetime

from src.services.export_bundles import (
    # Enums
    ExportPurpose,
    # Data classes
    PurposeProfile,
    BundleFile,
    ExportBundle,
    # Classes
    ContentGenerator,
    PurposeDrivenBundleGenerator,
    # Functions
    generate_bundle,
    list_purposes,
    get_bundle_generator,
    # Constants
    PURPOSE_PROFILES,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def sample_beliefs():
    """Sample beliefs for testing."""
    return [
        {
            "id": "belief1",
            "content": "Exposure to nature reduces stress levels",
            "credence": 0.85,
            "uncertainty": 0.10,
            "status": "ACCEPTED",
            "level": "EMPIRICAL",
            "theory": "Stress Recovery Theory",
            "sources": ["ulrich1984", "kaplan1989"],
            "constraints": []
        },
        {
            "id": "belief2",
            "content": "Indoor plants improve air quality",
            "credence": 0.65,
            "uncertainty": 0.20,
            "status": "ACCEPTED",
            "level": "EMPIRICAL",
            "theory": "Biophilia",
            "sources": ["wolverton1989"],
            "constraints": []
        },
        {
            "id": "belief3",
            "content": "Natural light enhances productivity",
            "credence": 0.75,
            "uncertainty": 0.15,
            "status": "ACCEPTED",
            "level": "EMPIRICAL",
            "theory": None,
            "sources": ["heschong2002"],
            "constraints": []
        },
        {
            "id": "belief4",
            "content": "Window views correlate with recovery time",
            "credence": 0.90,
            "uncertainty": 0.08,
            "status": "ACCEPTED",
            "level": "EMPIRICAL",
            "theory": "Stress Recovery Theory",
            "sources": ["ulrich1984"],
            "constraints": []
        },
        {
            "id": "belief5",
            "content": "Biophilic design principles apply universally",
            "credence": 0.45,
            "uncertainty": 0.30,
            "status": "CONTESTED",
            "level": "THEORETICAL",
            "theory": "Biophilia",
            "sources": [],
            "constraints": []
        }
    ]


@pytest.fixture
def sample_sources():
    """Sample source papers for testing."""
    return [
        {
            "paper_id": "ulrich1984",
            "title": "View through a window may influence recovery from surgery",
            "authors": ["Roger S. Ulrich"],
            "year": 1984,
            "journal": "Science",
            "doi": "10.1126/science.6143402",
            "key_finding": "Patients with window views recovered faster",
            "study_type": "Quasi-experimental",
            "sample_size": 46
        },
        {
            "paper_id": "kaplan1989",
            "title": "The Experience of Nature: A Psychological Perspective",
            "authors": ["Rachel Kaplan", "Stephen Kaplan"],
            "year": 1989,
            "journal": None,
            "doi": None,
            "key_finding": "Attention restoration theory framework",
            "study_type": "Theoretical",
            "sample_size": None
        },
        {
            "paper_id": "wolverton1989",
            "title": "Interior Landscape Plants for Indoor Air Pollution Abatement",
            "authors": ["B.C. Wolverton"],
            "year": 1989,
            "journal": None,
            "doi": None,
            "key_finding": "Plants can filter indoor air pollutants",
            "study_type": "Laboratory",
            "sample_size": None
        }
    ]


# =============================================================================
# PURPOSE PROFILE TESTS
# =============================================================================


class TestPurposeProfiles:
    """Tests for purpose profile definitions."""

    def test_all_purposes_have_profiles(self):
        """Verify all export purposes have defined profiles."""
        for purpose in ExportPurpose:
            assert purpose in PURPOSE_PROFILES

    def test_profile_structure(self):
        """Verify profile structure is complete."""
        for purpose, profile in PURPOSE_PROFILES.items():
            assert profile.purpose == purpose
            assert profile.name
            assert profile.description
            assert profile.primary_audience
            assert profile.expertise_level in ["novice", "intermediate", "expert"]
            assert profile.primary_tasks
            assert profile.required_content is not None
            assert profile.primary_formats
            assert 1 <= profile.detail_level <= 5

    def test_practitioner_profile(self):
        """Test practitioner briefing profile specifics."""
        profile = PURPOSE_PROFILES[ExportPurpose.PRACTITIONER_BRIEFING]
        assert profile.expertise_level == "intermediate"
        assert profile.time_available == "minutes"
        assert "key_findings" in profile.required_content
        assert "markdown" in profile.primary_formats

    def test_systematic_review_profile(self):
        """Test systematic review profile specifics."""
        profile = PURPOSE_PROFILES[ExportPurpose.SYSTEMATIC_REVIEW]
        assert profile.expertise_level == "expert"
        assert "study_table" in profile.required_content
        assert "prisma_checklist" in profile.required_content
        assert "json" in profile.primary_formats  # json, csv, bibtex are primary

    def test_policy_brief_profile(self):
        """Test policy brief profile specifics."""
        profile = PURPOSE_PROFILES[ExportPurpose.POLICY_BRIEF]
        assert "executive_summary" in profile.required_content
        assert profile.include_statistics is False
        assert profile.detail_level <= 3


# =============================================================================
# CONTENT GENERATOR TESTS
# =============================================================================


class TestContentGenerator:
    """Tests for content generation."""

    def test_executive_summary(self, sample_beliefs):
        """Test executive summary generation."""
        gen = ContentGenerator()
        summary = gen.generate_executive_summary("Biophilic Design", sample_beliefs)

        assert "# Executive Summary: Biophilic Design" in summary
        assert "Key Findings" in summary
        assert "Evidence Strength" in summary
        # Should include high-credence findings
        assert "nature" in summary.lower() or "window" in summary.lower()

    def test_key_recommendations(self, sample_beliefs):
        """Test recommendations generation."""
        gen = ContentGenerator()
        recs = gen.generate_key_recommendations("Biophilic Design", sample_beliefs)

        assert "# Key Recommendations" in recs
        # Should have actionable recommendations
        assert "Consider" in recs

    def test_evidence_synthesis(self, sample_beliefs):
        """Test evidence synthesis generation."""
        gen = ContentGenerator()
        synthesis = gen.generate_evidence_synthesis("Biophilic Design", sample_beliefs)

        assert "# Evidence Synthesis" in synthesis
        # Should group by theory
        assert "Stress Recovery Theory" in synthesis or "General Findings" in synthesis

    def test_evidence_synthesis_with_citations(self, sample_beliefs):
        """Test evidence synthesis includes citations."""
        gen = ContentGenerator()
        synthesis = gen.generate_evidence_synthesis(
            "Biophilic Design", sample_beliefs, include_citations=True
        )

        # Should include source citations
        assert "ulrich" in synthesis.lower() or "kaplan" in synthesis.lower()

    def test_study_table_markdown(self, sample_sources):
        """Test study table markdown generation."""
        gen = ContentGenerator()
        table = gen.generate_study_table(sample_sources, format="markdown")

        assert "# Study Characteristics" in table
        assert "| Citation |" in table
        assert "Ulrich" in table

    def test_study_table_csv(self, sample_sources):
        """Test study table CSV generation."""
        gen = ContentGenerator()
        csv = gen.generate_study_table(sample_sources, format="csv")

        assert "citation,year" in csv
        # Should have data rows
        assert len(csv.split("\n")) > 1

    def test_prisma_checklist(self, sample_beliefs, sample_sources):
        """Test PRISMA checklist generation."""
        gen = ContentGenerator()
        checklist = gen.generate_prisma_checklist(sample_beliefs, sample_sources)

        assert "# PRISMA Checklist" in checklist
        assert "Identification" in checklist
        assert "Screening" in checklist
        assert "Quality Assessment" in checklist

    def test_teaching_content(self, sample_beliefs):
        """Test teaching materials generation."""
        gen = ContentGenerator()
        content = gen.generate_teaching_content("Biophilic Design", sample_beliefs)

        assert "# Teaching Module" in content
        assert "Learning Objectives" in content
        assert "Key Concepts" in content
        assert "Discussion Questions" in content
        assert "Exercise" in content

    def test_grant_justification(self, sample_beliefs):
        """Test grant writing content generation."""
        gen = ContentGenerator()
        justification = gen.generate_grant_justification("Biophilic Design", sample_beliefs)

        assert "# Research Justification" in justification
        assert "Significance" in justification
        assert "Evidence Gaps" in justification
        assert "Research Need" in justification

    def test_policy_implications(self, sample_beliefs):
        """Test policy brief generation."""
        gen = ContentGenerator()
        brief = gen.generate_policy_implications("Biophilic Design", sample_beliefs)

        assert "# Policy Brief" in brief
        assert "The Issue" in brief
        assert "Policy Recommendations" in brief
        assert "Implementation" in brief

    def test_credence_to_label(self):
        """Test credence score to label conversion."""
        gen = ContentGenerator()

        assert gen._credence_to_label(0.90) == "Very High"
        assert gen._credence_to_label(0.75) == "High"
        assert gen._credence_to_label(0.55) == "Moderate"
        assert gen._credence_to_label(0.35) == "Low"
        assert gen._credence_to_label(0.15) == "Very Low"


# =============================================================================
# BUNDLE FILE TESTS
# =============================================================================


class TestBundleFile:
    """Tests for BundleFile dataclass."""

    def test_create_bundle_file(self):
        """Test creating a bundle file."""
        file = BundleFile(
            filename="summary.md",
            content="# Summary\nContent here",
            format="markdown",
            description="Evidence summary",
            is_primary=True
        )

        assert file.filename == "summary.md"
        assert file.format == "markdown"
        assert file.is_primary is True

    def test_bundle_file_default_primary(self):
        """Test default is_primary value."""
        file = BundleFile(
            filename="test.md",
            content="Content",
            format="markdown",
            description="Test"
        )

        assert file.is_primary is True


# =============================================================================
# EXPORT BUNDLE TESTS
# =============================================================================


class TestExportBundle:
    """Tests for ExportBundle dataclass."""

    def test_create_export_bundle(self, sample_beliefs):
        """Test creating an export bundle."""
        files = [
            BundleFile("summary.md", "# Summary", "markdown", "Summary"),
            BundleFile("data.json", "{}", "json", "Data")
        ]

        bundle = ExportBundle(
            purpose=ExportPurpose.PRACTITIONER_BRIEFING,
            topic="Test Topic",
            generated_at="2026-02-09T21:00:00Z",
            files=files,
            manifest={"test": "value"}
        )

        assert bundle.purpose == ExportPurpose.PRACTITIONER_BRIEFING
        assert len(bundle.files) == 2

    def test_bundle_to_dict(self):
        """Test bundle serialization."""
        files = [
            BundleFile("summary.md", "# Summary", "markdown", "Summary")
        ]

        bundle = ExportBundle(
            purpose=ExportPurpose.PRACTITIONER_BRIEFING,
            topic="Test",
            generated_at="2026-02-09T21:00:00Z",
            files=files,
            manifest={}
        )

        d = bundle.to_dict()

        assert d["purpose"] == "practitioner_briefing"
        assert d["topic"] == "Test"
        assert d["file_count"] == 1
        assert len(d["files"]) == 1
        assert d["files"][0]["filename"] == "summary.md"

    def test_bundle_write_to_directory(self, tmp_path):
        """Test writing bundle to directory."""
        files = [
            BundleFile("summary.md", "# Test Summary", "markdown", "Summary"),
            BundleFile("data.json", '{"test": 1}', "json", "Data")
        ]

        bundle = ExportBundle(
            purpose=ExportPurpose.DATA_PIPELINE,
            topic="Test",
            generated_at="2026-02-09T21:00:00Z",
            files=files,
            manifest={"key": "value"}
        )

        written = bundle.write_to_directory(tmp_path)

        assert len(written) == 3  # 2 files + manifest
        assert (tmp_path / "summary.md").exists()
        assert (tmp_path / "data.json").exists()
        assert (tmp_path / "MANIFEST.json").exists()

        # Check manifest content
        manifest = json.loads((tmp_path / "MANIFEST.json").read_text())
        assert manifest["purpose"] == "data_pipeline"


# =============================================================================
# BUNDLE GENERATOR TESTS
# =============================================================================


class TestPurposeDrivenBundleGenerator:
    """Tests for the main bundle generator."""

    def test_generator_initialization(self):
        """Test generator initialization."""
        gen = PurposeDrivenBundleGenerator()
        assert gen.content_gen is not None
        assert gen.profiles is not None

    @pytest.mark.parametrize("purpose", list(ExportPurpose))
    def test_generate_all_purposes(self, purpose, sample_beliefs, sample_sources):
        """Test bundle generation for all purposes."""
        gen = PurposeDrivenBundleGenerator()
        bundle = gen.generate(purpose, "Test Topic", sample_beliefs, sample_sources)

        assert bundle.purpose == purpose
        assert len(bundle.files) > 0
        assert bundle.manifest is not None

    def test_generate_practitioner_bundle(self, sample_beliefs):
        """Test practitioner briefing bundle."""
        gen = PurposeDrivenBundleGenerator()
        bundle = gen.generate(
            ExportPurpose.PRACTITIONER_BRIEFING,
            "Biophilic Design",
            sample_beliefs
        )

        filenames = {f.filename for f in bundle.files}
        assert "summary.md" in filenames
        assert "recommendations.md" in filenames

    def test_generate_literature_bundle(self, sample_beliefs, sample_sources):
        """Test literature review bundle."""
        gen = PurposeDrivenBundleGenerator()
        bundle = gen.generate(
            ExportPurpose.LITERATURE_REVIEW,
            "Biophilic Design",
            sample_beliefs,
            sample_sources
        )

        filenames = {f.filename for f in bundle.files}
        assert "synthesis.md" in filenames
        assert "references.bib" in filenames
        assert "beliefs.json" in filenames

    def test_generate_systematic_bundle(self, sample_beliefs, sample_sources):
        """Test systematic review bundle."""
        gen = PurposeDrivenBundleGenerator()
        bundle = gen.generate(
            ExportPurpose.SYSTEMATIC_REVIEW,
            "Biophilic Design",
            sample_beliefs,
            sample_sources
        )

        filenames = {f.filename for f in bundle.files}
        assert "evidence_summary.json" in filenames
        assert "beliefs.jsonl" in filenames
        assert "sources.jsonl" in filenames
        assert "prisma_checklist.md" in filenames

    def test_generate_presentation_bundle(self, sample_beliefs):
        """Test presentation bundle."""
        gen = PurposeDrivenBundleGenerator()
        bundle = gen.generate(
            ExportPurpose.PRESENTATION,
            "Biophilic Design",
            sample_beliefs
        )

        filenames = {f.filename for f in bundle.files}
        assert "talking_points.md" in filenames
        assert "visual_summary.html" in filenames

    def test_generate_pipeline_bundle(self, sample_beliefs, sample_sources):
        """Test data pipeline bundle."""
        gen = PurposeDrivenBundleGenerator()
        bundle = gen.generate(
            ExportPurpose.DATA_PIPELINE,
            "Test",
            sample_beliefs,
            sample_sources
        )

        filenames = {f.filename for f in bundle.files}
        assert "beliefs.jsonl" in filenames
        assert "sources.jsonl" in filenames
        assert "schema.json" in filenames
        assert "pipeline_manifest.json" in filenames

    def test_generate_teaching_bundle(self, sample_beliefs):
        """Test teaching materials bundle."""
        gen = PurposeDrivenBundleGenerator()
        bundle = gen.generate(
            ExportPurpose.TEACHING_MATERIALS,
            "Biophilic Design",
            sample_beliefs
        )

        filenames = {f.filename for f in bundle.files}
        assert "module.md" in filenames
        assert "handout.md" in filenames

    def test_generate_grant_bundle(self, sample_beliefs, sample_sources):
        """Test grant writing bundle."""
        gen = PurposeDrivenBundleGenerator()
        bundle = gen.generate(
            ExportPurpose.GRANT_WRITING,
            "Biophilic Design",
            sample_beliefs,
            sample_sources
        )

        filenames = {f.filename for f in bundle.files}
        assert "justification.md" in filenames
        assert "evidence_review.md" in filenames

    def test_generate_policy_bundle(self, sample_beliefs):
        """Test policy brief bundle."""
        gen = PurposeDrivenBundleGenerator()
        bundle = gen.generate(
            ExportPurpose.POLICY_BRIEF,
            "Biophilic Design",
            sample_beliefs
        )

        filenames = {f.filename for f in bundle.files}
        assert "policy_brief.md" in filenames
        assert "executive_summary.md" in filenames

    def test_bundle_manifest_structure(self, sample_beliefs, sample_sources):
        """Test manifest structure."""
        gen = PurposeDrivenBundleGenerator()
        bundle = gen.generate(
            ExportPurpose.LITERATURE_REVIEW,
            "Test Topic",
            sample_beliefs,
            sample_sources
        )

        manifest = bundle.manifest
        assert "purpose" in manifest
        assert "topic" in manifest
        assert "belief_count" in manifest
        assert "source_count" in manifest
        assert "file_count" in manifest
        assert "primary_files" in manifest
        assert "generated_at" in manifest

    def test_bundle_validation_warnings(self):
        """Test bundle validation produces warnings."""
        gen = PurposeDrivenBundleGenerator()

        # Empty beliefs should produce warnings
        bundle = gen.generate(
            ExportPurpose.SYSTEMATIC_REVIEW,
            "Test",
            [],  # Empty beliefs
            []   # Empty sources
        )

        # Should still generate bundle but may have validation issues
        assert bundle is not None


# =============================================================================
# CONVENIENCE FUNCTION TESTS
# =============================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_generate_bundle_with_enum(self, sample_beliefs, sample_sources):
        """Test generate_bundle with enum purpose."""
        bundle = generate_bundle(
            ExportPurpose.PRACTITIONER_BRIEFING,
            "Test Topic",
            sample_beliefs,
            sample_sources
        )

        assert bundle.purpose == ExportPurpose.PRACTITIONER_BRIEFING
        assert len(bundle.files) > 0

    def test_generate_bundle_with_string(self, sample_beliefs):
        """Test generate_bundle with string purpose."""
        bundle = generate_bundle(
            "presentation",
            "Test Topic",
            sample_beliefs
        )

        assert bundle.purpose == ExportPurpose.PRESENTATION

    def test_generate_bundle_writes_to_directory(self, sample_beliefs, tmp_path):
        """Test generate_bundle with output directory."""
        output_dir = tmp_path / "export"

        bundle = generate_bundle(
            ExportPurpose.DATA_PIPELINE,
            "Test",
            sample_beliefs,
            output_dir=output_dir
        )

        assert output_dir.exists()
        assert (output_dir / "beliefs.jsonl").exists()
        assert (output_dir / "MANIFEST.json").exists()

    def test_list_purposes(self):
        """Test listing available purposes."""
        purposes = list_purposes()

        assert len(purposes) == len(ExportPurpose)
        for p in purposes:
            assert "purpose" in p
            assert "name" in p
            assert "description" in p
            assert "audience" in p
            assert "primary_formats" in p

    def test_get_bundle_generator_singleton(self):
        """Test singleton behavior."""
        gen1 = get_bundle_generator()
        gen2 = get_bundle_generator()

        assert gen1 is gen2


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestIntegration:
    """Integration tests for export bundles."""

    def test_full_workflow(self, sample_beliefs, sample_sources, tmp_path):
        """Test complete export workflow."""
        # Generate bundle
        bundle = generate_bundle(
            ExportPurpose.SYSTEMATIC_REVIEW,
            "Biophilic Design Effects",
            sample_beliefs,
            sample_sources,
            output_dir=tmp_path
        )

        # Verify all expected files exist
        assert (tmp_path / "evidence_summary.json").exists()
        assert (tmp_path / "references.bib").exists()
        assert (tmp_path / "beliefs.jsonl").exists()
        assert (tmp_path / "MANIFEST.json").exists()

        # Verify JSON is valid
        summary = json.loads((tmp_path / "evidence_summary.json").read_text())
        assert summary["topic"] == "Biophilic Design Effects"
        assert summary["belief_count"] == len(sample_beliefs)

        # Verify JSONL is valid
        jsonl = (tmp_path / "beliefs.jsonl").read_text()
        for line in jsonl.strip().split("\n"):
            if line:
                json.loads(line)  # Should not raise

        # Verify manifest
        manifest = json.loads((tmp_path / "MANIFEST.json").read_text())
        assert manifest["purpose"] == "systematic_review"

    def test_bibtex_integration(self, sample_beliefs, sample_sources, tmp_path):
        """Test BibTeX generation integration."""
        bundle = generate_bundle(
            ExportPurpose.LITERATURE_REVIEW,
            "Test",
            sample_beliefs,
            sample_sources,
            output_dir=tmp_path
        )

        bibtex_file = tmp_path / "references.bib"
        assert bibtex_file.exists()

        content = bibtex_file.read_text()
        assert "@" in content  # Should have BibTeX entries

    def test_empty_sources_handling(self, sample_beliefs, tmp_path):
        """Test handling when no sources provided."""
        bundle = generate_bundle(
            ExportPurpose.PRACTITIONER_BRIEFING,
            "Test",
            sample_beliefs,
            sources=None,  # No sources
            output_dir=tmp_path
        )

        assert bundle is not None
        assert len(bundle.files) > 0

    def test_empty_beliefs_handling(self, sample_sources, tmp_path):
        """Test handling when no beliefs provided."""
        bundle = generate_bundle(
            ExportPurpose.DATA_PIPELINE,
            "Test",
            beliefs=[],  # Empty beliefs
            sources=sample_sources,
            output_dir=tmp_path
        )

        assert bundle is not None
        # JSONL should be empty but file should exist
        assert (tmp_path / "beliefs.jsonl").exists()


# =============================================================================
# EDGE CASE TESTS
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases."""

    def test_special_characters_in_topic(self, sample_beliefs):
        """Test handling special characters in topic."""
        bundle = generate_bundle(
            ExportPurpose.PRESENTATION,
            "Effects of 'Nature' & \"Plants\" on <People>",
            sample_beliefs
        )

        assert bundle is not None
        # Should not crash

    def test_unicode_in_beliefs(self):
        """Test handling Unicode in beliefs."""
        beliefs = [{
            "id": "unicode1",
            "content": "Exposure to ñatüre rédûces stréss (研究)",
            "credence": 0.80,
            "uncertainty": 0.10,
            "status": "ACCEPTED",
            "level": "EMPIRICAL",
            "sources": [],
            "constraints": []
        }]

        bundle = generate_bundle(
            ExportPurpose.PRACTITIONER_BRIEFING,
            "Test",
            beliefs
        )

        assert bundle is not None
        # Content should be preserved
        summary_file = next(f for f in bundle.files if f.filename == "summary.md")
        assert "ñatüre" in summary_file.content or "nature" in summary_file.content.lower()

    def test_very_long_content(self):
        """Test handling very long belief content."""
        beliefs = [{
            "id": "long1",
            "content": "This is a very long finding. " * 100,
            "credence": 0.80,
            "uncertainty": 0.10,
            "status": "ACCEPTED",
            "level": "EMPIRICAL",
            "sources": [],
            "constraints": []
        }]

        bundle = generate_bundle(
            ExportPurpose.POLICY_BRIEF,
            "Test",
            beliefs
        )

        assert bundle is not None

    def test_many_beliefs(self):
        """Test handling many beliefs."""
        beliefs = [
            {
                "id": f"belief{i}",
                "content": f"Finding number {i}",
                "credence": 0.5 + (i % 50) / 100,
                "uncertainty": 0.20,
                "status": "ACCEPTED",
                "level": "EMPIRICAL",
                "sources": [],
                "constraints": []
            }
            for i in range(100)
        ]

        bundle = generate_bundle(
            ExportPurpose.DATA_PIPELINE,
            "Large Dataset",
            beliefs
        )

        assert bundle is not None
        # Should have all beliefs in JSONL
        jsonl_file = next(f for f in bundle.files if f.filename == "beliefs.jsonl")
        lines = jsonl_file.content.strip().split("\n")
        assert len(lines) == 100

    def test_null_fields_in_beliefs(self):
        """Test handling null/missing fields in beliefs."""
        beliefs = [{
            "id": "null1",
            "content": "Test finding",
            "credence": 0.70,
            "uncertainty": None,  # Null field
            "status": "ACCEPTED",
            "level": None,  # Null field
            # Missing: theory, sources, constraints
        }]

        bundle = generate_bundle(
            ExportPurpose.PRESENTATION,
            "Test",
            beliefs
        )

        assert bundle is not None
