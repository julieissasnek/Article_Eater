"""Tests for extraction gold standard paper management (Sprint D Task D.5)."""

import json
import tempfile
from pathlib import Path

import pytest

from src.extraction.gold_standard import (
    VerifiedClaim,
    GoldStandardPaper,
    load_gold_standard,
    save_gold_standard,
    get_selected_papers,
    get_paper_by_id,
    add_verified_claim,
    validate_extraction_against_gold,
    print_gold_standard_summary,
)


class TestVerifiedClaim:
    """Tests for VerifiedClaim dataclass."""

    def test_to_dict(self):
        claim = VerifiedClaim(
            claim_id="c1",
            environment_variable="illuminance_lux",
            outcome_variable="productivity",
            effect_direction="positive",
            statement="Higher light levels improve productivity",
            source_page=5,
        )
        d = claim.to_dict()
        assert d["environment_variable"] == "illuminance_lux"
        assert d["outcome_variable"] == "productivity"
        assert d["effect_direction"] == "positive"

    def test_from_dict(self):
        d = {
            "claim_id": "c2",
            "environment_variable": "ceiling_height_m",
            "outcome_variable": "creativity",
            "effect_direction": "positive",
            "statement": "Higher ceilings enhance creative thinking",
        }
        claim = VerifiedClaim.from_dict(d)
        assert claim.environment_variable == "ceiling_height_m"
        assert claim.outcome_variable == "creativity"

    def test_roundtrip(self):
        original = VerifiedClaim(
            claim_id="c3",
            environment_variable="ambient_noise_dba",
            outcome_variable="concentration",
            effect_direction="negative",
            statement="Noise reduces concentration",
            source_page=10,
            source_table="Table 2",
            verified_by="DK",
            verified_at="2026-02-18T12:00:00Z",
        )
        d = original.to_dict()
        restored = VerifiedClaim.from_dict(d)
        assert restored.claim_id == original.claim_id
        assert restored.verified_by == original.verified_by


class TestGoldStandardPaper:
    """Tests for GoldStandardPaper dataclass."""

    def test_to_dict(self):
        paper = GoldStandardPaper(
            paper_id="doi:10.1234/test",
            article_type_family="empirical",
            n_structured_rows=100,
            gold_standard_status="selected",
            domains=["light", "cognition"],
        )
        d = paper.to_dict()
        assert d["paper_id"] == "doi:10.1234/test"
        assert d["gold_standard_status"] == "selected"
        assert "light" in d["domains"]

    def test_from_dict(self):
        d = {
            "paper_id": "doi:10.5678/test",
            "article_type_family": "review",
            "n_structured_rows": 50,
            "gold_standard_status": "candidate",
            "verified_claims": [
                {
                    "claim_id": "c1",
                    "environment_variable": "daylight",
                    "outcome_variable": "mood",
                    "effect_direction": "positive",
                    "statement": "Daylight improves mood",
                }
            ],
        }
        paper = GoldStandardPaper.from_dict(d)
        assert paper.paper_id == "doi:10.5678/test"
        assert len(paper.verified_claims) == 1
        assert paper.verified_claims[0].environment_variable == "daylight"


class TestLoadSave:
    """Tests for loading and saving gold standard files."""

    def test_save_and_load(self):
        papers = [
            GoldStandardPaper(
                paper_id="doi:test1",
                article_type_family="empirical",
                n_structured_rows=100,
                gold_standard_status="selected",
                domains=["light"],
            ),
            GoldStandardPaper(
                paper_id="doi:test2",
                article_type_family="review",
                n_structured_rows=50,
                gold_standard_status="candidate",
            ),
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name

        save_gold_standard(papers, path)
        loaded = load_gold_standard(path)

        assert len(loaded) == 2
        assert loaded[0].paper_id == "doi:test1"
        assert loaded[1].paper_id == "doi:test2"

    def test_load_nonexistent_returns_empty(self):
        result = load_gold_standard("/nonexistent/path/file.json")
        assert result == []


class TestGetPapers:
    """Tests for paper retrieval functions."""

    def test_get_selected_papers(self):
        papers = [
            GoldStandardPaper("p1", "empirical", 100, "selected"),
            GoldStandardPaper("p2", "review", 50, "candidate"),
            GoldStandardPaper("p3", "empirical", 75, "selected"),
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name

        save_gold_standard(papers, path)
        selected = get_selected_papers(path)

        assert len(selected) == 2
        assert all(p.gold_standard_status == "selected" for p in selected)

    def test_get_paper_by_id(self):
        papers = [
            GoldStandardPaper("doi:10.1234/abc", "empirical", 100, "selected"),
            GoldStandardPaper("doi:10.5678/xyz", "review", 50, "candidate"),
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name

        save_gold_standard(papers, path)

        found = get_paper_by_id("doi:10.1234/abc", path)
        assert found is not None
        assert found.paper_id == "doi:10.1234/abc"

        not_found = get_paper_by_id("doi:nonexistent", path)
        assert not_found is None


class TestAddVerifiedClaim:
    """Tests for adding verified claims."""

    def test_add_claim_to_paper(self):
        papers = [
            GoldStandardPaper("doi:test", "empirical", 100, "selected"),
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name

        save_gold_standard(papers, path)

        claim = VerifiedClaim(
            claim_id="c1",
            environment_variable="light",
            outcome_variable="mood",
            effect_direction="positive",
            statement="Light improves mood",
        )

        result = add_verified_claim("doi:test", claim, path)
        assert result is True

        loaded = load_gold_standard(path)
        assert len(loaded[0].verified_claims) == 1

    def test_add_claim_to_nonexistent_paper(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name

        save_gold_standard([], path)

        claim = VerifiedClaim(
            claim_id="c1",
            environment_variable="light",
            outcome_variable="mood",
            effect_direction="positive",
            statement="Light improves mood",
        )

        result = add_verified_claim("nonexistent", claim, path)
        assert result is False


class TestValidateExtraction:
    """Tests for extraction validation."""

    def test_validate_perfect_extraction(self):
        papers = [
            GoldStandardPaper(
                paper_id="doi:test",
                article_type_family="empirical",
                n_structured_rows=100,
                gold_standard_status="selected",
                verified_claims=[
                    VerifiedClaim("c1", "light", "mood", "positive", "stmt1"),
                    VerifiedClaim("c2", "noise", "stress", "positive", "stmt2"),
                ],
            ),
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name

        save_gold_standard(papers, path)

        extracted = [
            {"environment_variable": "light", "outcome_variable": "mood"},
            {"environment_variable": "noise", "outcome_variable": "stress"},
        ]

        result = validate_extraction_against_gold("doi:test", extracted, path)
        assert result["status"] == "validated"
        assert result["precision"] == 1.0
        assert result["recall"] == 1.0
        assert result["f1"] == 1.0

    def test_validate_partial_extraction(self):
        papers = [
            GoldStandardPaper(
                paper_id="doi:test",
                article_type_family="empirical",
                n_structured_rows=100,
                gold_standard_status="selected",
                verified_claims=[
                    VerifiedClaim("c1", "light", "mood", "positive", "stmt1"),
                    VerifiedClaim("c2", "noise", "stress", "positive", "stmt2"),
                ],
            ),
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name

        save_gold_standard(papers, path)

        # Only extract one of two claims
        extracted = [
            {"environment_variable": "light", "outcome_variable": "mood"},
        ]

        result = validate_extraction_against_gold("doi:test", extracted, path)
        assert result["recall"] == 0.5
        assert result["precision"] == 1.0

    def test_validate_no_gold_standard(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name

        save_gold_standard([], path)

        result = validate_extraction_against_gold("nonexistent", [], path)
        assert result["status"] == "no_gold_standard"


class TestSummaryReport:
    """Tests for summary report generation."""

    def test_summary_with_papers(self):
        papers = [
            GoldStandardPaper(
                paper_id="doi:test1",
                article_type_family="empirical",
                n_structured_rows=100,
                gold_standard_status="selected",
                domains=["light", "cognition"],
                verified_claims=[
                    VerifiedClaim("c1", "light", "mood", "positive", "stmt"),
                ],
            ),
            GoldStandardPaper(
                paper_id="doi:test2",
                article_type_family="review",
                n_structured_rows=50,
                gold_standard_status="selected",
                domains=["light"],
            ),
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name

        save_gold_standard(papers, path)
        summary = print_gold_standard_summary(path)

        assert "GOLD STANDARD PAPERS SUMMARY" in summary
        assert "Selected: 2" in summary
        assert "light" in summary

    def test_summary_empty(self):
        summary = print_gold_standard_summary("/nonexistent/path.json")
        assert "No gold standard papers loaded" in summary
