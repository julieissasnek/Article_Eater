"""Tests for paper triage classifier (Sprint D Task D.2)."""

import json
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from src.extraction.paper_triage import (
    PaperTriage,
    TriageResult,
    ARTICLE_TYPE_MAPPING,
    DOMAIN_KEYWORDS,
    _detect_domains,
    _has_empirical_signals,
    _classify_paper,
    triage_papers,
    get_extractable_papers,
    print_triage_report,
)


class TestDomainKeywords:
    """Tests for domain keyword configuration."""

    def test_has_expected_domains(self):
        expected_domains = [
            "A1_Materials", "A2_Spatial_Scale", "A3_Spatial_Config",
            "A4_Light", "A5_Acoustic", "A6_Visual_Form",
            "A7_Haptic_Thermal", "A8_Social", "A9_Task_Cognition",
            "A10_Temporal"
        ]
        for domain in expected_domains:
            assert domain in DOMAIN_KEYWORDS

    def test_each_domain_has_keywords(self):
        for domain, keywords in DOMAIN_KEYWORDS.items():
            assert len(keywords) >= 3, f"{domain} should have at least 3 keywords"


class TestArticleTypeMapping:
    """Tests for article type mapping."""

    def test_empirical_types(self):
        empirical_sources = ["empirical", "experiment", "field_study", "survey_study"]
        for source in empirical_sources:
            assert ARTICLE_TYPE_MAPPING.get(source) == "empirical"

    def test_review_types(self):
        review_sources = ["narrative_review", "literature_review", "systematic_review"]
        for source in review_sources:
            assert ARTICLE_TYPE_MAPPING.get(source) == "review"

    def test_meta_analysis_types(self):
        assert ARTICLE_TYPE_MAPPING.get("meta_analysis") == "meta_analysis"
        assert ARTICLE_TYPE_MAPPING.get("meta-analysis") == "meta_analysis"

    def test_theoretical_types(self):
        theoretical_sources = ["theoretical", "conceptual", "commentary", "editorial"]
        for source in theoretical_sources:
            assert ARTICLE_TYPE_MAPPING.get(source) == "theoretical"


class TestDetectDomains:
    """Tests for domain detection from text."""

    def test_detects_light_domain(self):
        text = "The effect of daylight on occupant wellbeing was measured using lux meters."
        domains = _detect_domains(text)
        assert "A4_Light" in domains

    def test_detects_acoustic_domain(self):
        text = "Noise levels were measured in decibels and related to speech intelligibility."
        domains = _detect_domains(text)
        assert "A5_Acoustic" in domains

    def test_detects_multiple_domains(self):
        text = "We studied how ceiling height and natural light affect creativity."
        domains = _detect_domains(text)
        assert "A2_Spatial_Scale" in domains
        assert "A4_Light" in domains

    def test_empty_text_returns_empty(self):
        assert _detect_domains("") == []
        assert _detect_domains(None) == []

    def test_case_insensitive(self):
        text = "DAYLIGHT and CEILING HEIGHT effects"
        domains = _detect_domains(text)
        assert len(domains) >= 2


class TestHasEmpiricalSignals:
    """Tests for empirical signal detection."""

    def test_sample_size_detected(self):
        text = "We recruited n = 120 participants."
        score = _has_empirical_signals(text)
        assert score > 0

    def test_pvalue_detected(self):
        text = "The effect was significant (p < 0.05)."
        score = _has_empirical_signals(text)
        assert score > 0

    def test_statistical_terms_detected(self):
        text = "ANOVA revealed significant main effects. Correlation analysis showed..."
        score = _has_empirical_signals(text)
        assert score > 0.3

    def test_multiple_signals_high_confidence(self):
        text = "N=50 participants. Results show significant effects (p < 0.001). Effect size was large."
        score = _has_empirical_signals(text)
        assert score >= 0.9

    def test_empty_returns_zero(self):
        assert _has_empirical_signals("") == 0.0
        assert _has_empirical_signals(None) == 0.0

    def test_no_signals_low_score(self):
        text = "This paper discusses theoretical frameworks for understanding architecture."
        score = _has_empirical_signals(text)
        assert score < 0.3


class TestPaperTriage:
    """Tests for PaperTriage dataclass."""

    def test_to_dict(self):
        triage = PaperTriage(
            paper_id="doi:10.1234/test",
            triage_type="empirical",
            confidence=0.85,
            n_rows=10,
            has_tables=True,
            relevant_domains=["A4_Light"],
            article_type_family="experiment",
            title="Test Paper",
            extractable=True,
            priority=90,
        )
        d = triage.to_dict()
        assert d["paper_id"] == "doi:10.1234/test"
        assert d["triage_type"] == "empirical"
        assert d["confidence"] == 0.85
        assert d["has_tables"] is True
        assert d["extractable"] is True

    def test_defaults(self):
        triage = PaperTriage(
            paper_id="test",
            triage_type="unknown",
            confidence=0.5,
            n_rows=0,
            has_tables=False,
            relevant_domains=[],
            article_type_family="unknown",
        )
        assert triage.title is None
        assert triage.abstract is None
        assert triage.extractable is False
        assert triage.priority == 0


class TestTriageResult:
    """Tests for TriageResult dataclass."""

    def test_to_dict(self):
        papers = [
            PaperTriage(
                paper_id="p1", triage_type="empirical", confidence=0.8,
                n_rows=5, has_tables=True, relevant_domains=["A4_Light"],
                article_type_family="experiment", extractable=True, priority=80
            ),
            PaperTriage(
                paper_id="p2", triage_type="theoretical", confidence=0.7,
                n_rows=2, has_tables=False, relevant_domains=[],
                article_type_family="conceptual", extractable=False, priority=20
            ),
        ]
        result = TriageResult(
            papers=papers,
            total_papers=2,
            by_type={"empirical": 1, "theoretical": 1},
            extractable_count=1,
        )
        d = result.to_dict()
        assert d["total_papers"] == 2
        assert len(d["papers"]) == 2
        assert d["extractable_count"] == 1


class TestClassifyPaper:
    """Tests for paper classification logic."""

    def test_classify_empirical_paper(self):
        rows = pd.DataFrame({
            "paper_id": ["p1", "p1", "p1"],
            "statement": ["n=50 participants showed significant effects", "p<0.05", "correlation r=0.6"],
            "article_type_family": ["experiment", "experiment", "experiment"],
            "environment_variable": ["light", "light", None],
            "outcome_variable": ["stress", None, "mood"],
            "claim_type": ["finding", "finding", "finding"],
        })
        triage = _classify_paper("p1", rows, title="Light and stress", abstract=None)
        assert triage.triage_type == "empirical"
        assert triage.has_tables is True
        assert triage.extractable is True

    def test_classify_theoretical_paper(self):
        rows = pd.DataFrame({
            "paper_id": ["p2", "p2"],
            "statement": ["theoretical framework", "conceptual model"],
            "article_type_family": ["theoretical", "theoretical"],
            "environment_variable": [None, None],
            "outcome_variable": [None, None],
            "claim_type": ["theory", "theory"],
        })
        triage = _classify_paper("p2", rows, title="Framework for architecture")
        assert triage.triage_type == "theoretical"
        assert triage.extractable is False

    def test_classify_review_paper(self):
        rows = pd.DataFrame({
            "paper_id": ["p3"],
            "statement": ["Literature review of 50 studies"],
            "article_type_family": ["systematic_review"],
            "environment_variable": ["light"],
            "outcome_variable": ["wellbeing"],
            "claim_type": ["summary"],
        })
        triage = _classify_paper("p3", rows)
        assert triage.triage_type == "review"
        assert triage.has_tables is True

    def test_meta_analysis_high_priority(self):
        rows = pd.DataFrame({
            "paper_id": ["p4"],
            "statement": ["Meta-analysis of 20 studies"],
            "article_type_family": ["meta_analysis"],
            "environment_variable": ["noise"],
            "outcome_variable": ["performance"],
            "claim_type": ["meta"],
        })
        triage = _classify_paper("p4", rows)
        assert triage.triage_type == "meta_analysis"
        assert triage.priority >= 100

    def test_domain_detection_in_classification(self):
        rows = pd.DataFrame({
            "paper_id": ["p5"],
            "statement": ["Ceiling height affects creativity"],
            "article_type_family": ["empirical"],
            "environment_variable": ["ceiling_height"],
            "outcome_variable": ["creativity"],
            "claim_type": ["finding"],
        })
        triage = _classify_paper("p5", rows, title="Ceiling height and creative cognition")
        assert "A2_Spatial_Scale" in triage.relevant_domains or "A9_Task_Cognition" in triage.relevant_domains


class TestTriagePapers:
    """Tests for full triage pipeline."""

    def test_triage_with_temp_files(self):
        # Create temporary CSV
        df = pd.DataFrame({
            "paper_id": ["doi:paper1", "doi:paper1", "doi:paper2"],
            "statement": ["n=30 participants", "p<0.05", "theoretical framework"],
            "article_type_family": ["experiment", "experiment", "conceptual"],
            "environment_variable": ["light", "light", None],
            "outcome_variable": ["mood", "mood", None],
            "claim_type": ["finding", "finding", "theory"],
        })

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test_data.csv"
            df.to_csv(csv_path, index=False)

            output_path = Path(tmpdir) / "triage_output.json"
            result = triage_papers(
                csv_path=str(csv_path),
                articles_db_path="nonexistent.db",  # Will be skipped
                output_path=str(output_path),
            )

            assert result.total_papers == 2
            assert "empirical" in result.by_type
            assert output_path.exists()

            # Verify JSON is valid
            with open(output_path) as f:
                loaded = json.load(f)
            assert loaded["total_papers"] == 2

    def test_triage_no_output(self):
        df = pd.DataFrame({
            "paper_id": ["p1"],
            "statement": ["test"],
            "article_type_family": ["empirical"],
            "environment_variable": [None],
            "outcome_variable": [None],
            "claim_type": ["finding"],
        })

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test.csv"
            df.to_csv(csv_path, index=False)

            result = triage_papers(csv_path=str(csv_path), output_path=None)
            assert result.total_papers == 1


class TestGetExtractablePapers:
    """Tests for extractable paper retrieval."""

    def test_get_extractable(self):
        data = {
            "papers": [
                {"paper_id": "p1", "extractable": True},
                {"paper_id": "p2", "extractable": False},
                {"paper_id": "p3", "extractable": True},
            ]
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            f.flush()

            extractable = get_extractable_papers(f.name)
            assert extractable == ["p1", "p3"]


class TestPrintTriageReport:
    """Tests for report generation."""

    def test_report_contains_sections(self):
        papers = [
            PaperTriage(
                paper_id="doi:10.1234/test", triage_type="empirical",
                confidence=0.9, n_rows=10, has_tables=True,
                relevant_domains=["A4_Light"], article_type_family="experiment",
                n_table_rows=8, extractable=True, priority=90
            ),
        ]
        result = TriageResult(
            papers=papers, total_papers=1,
            by_type={"empirical": 1}, extractable_count=1
        )

        report = print_triage_report(result)
        assert "PAPER TRIAGE REPORT" in report
        assert "BY TYPE:" in report
        assert "empirical: 1" in report
        assert "Extractable papers: 1" in report
        assert "TOP 20 BY PRIORITY:" in report


class TestJSONSerialization:
    """Tests to verify JSON serialization works with numpy types."""

    def test_triage_result_serializes(self):
        # Create with numpy-like types (simulating pandas output)
        import numpy as np

        triage = PaperTriage(
            paper_id="test",
            triage_type="empirical",
            confidence=0.8,
            n_rows=int(np.int64(10)),
            has_tables=bool(np.bool_(True)),
            relevant_domains=["A4_Light"],
            article_type_family="experiment",
            n_table_rows=int(np.int64(5)),
            n_discourse_rows=int(np.int64(5)),
            extractable=bool(np.bool_(True)),
            priority=80,
        )

        result = TriageResult(
            papers=[triage],
            total_papers=1,
            by_type={"empirical": 1},
            extractable_count=1,
        )

        # This should not raise TypeError
        json_str = json.dumps(result.to_dict())
        assert "empirical" in json_str

    def test_full_pipeline_json_output(self):
        """Verify the full pipeline produces valid JSON."""
        df = pd.DataFrame({
            "paper_id": ["p1", "p1"],
            "statement": ["test statement", "another statement"],
            "article_type_family": ["empirical", "empirical"],
            "environment_variable": ["light", None],
            "outcome_variable": ["mood", "stress"],
            "claim_type": ["finding", "finding"],
        })

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test.csv"
            output_path = Path(tmpdir) / "output.json"
            df.to_csv(csv_path, index=False)

            result = triage_papers(
                csv_path=str(csv_path),
                output_path=str(output_path)
            )

            # Read back and verify
            with open(output_path) as f:
                loaded = json.load(f)

            assert isinstance(loaded["papers"][0]["has_tables"], bool)
            assert isinstance(loaded["papers"][0]["extractable"], bool)
            assert isinstance(loaded["papers"][0]["n_rows"], int)
