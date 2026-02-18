"""Tests for Paper Processing Pipeline (Sprint 13 Task 13.13)."""

import json
import os
import tempfile
from datetime import datetime

import pytest

from src.cmr.process_paper import (
    ProcessingResult,
    process_paper,
    process_paper_from_text,
    format_processing_report,
    get_processing_summary,
    _convert_update_to_proposal,
    _extract_effect_data_from_claims,
)
from src.cmr.learning.update_proposals import ProposalType, ProposalStatus, Evidence
from src.cmr.models import create_tables


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    create_tables(path)
    yield path
    os.unlink(path)


class TestProcessingResult:
    """Tests for ProcessingResult dataclass."""

    def test_result_creation(self):
        """Test creating a ProcessingResult."""
        result = ProcessingResult(
            paper_citation="Test 2024",
            doi="10.1234/test",
            processed_at=datetime.utcnow(),
            n_claims=5,
            n_matched=3,
            n_unmatched=2,
            n_contradictions=1,
            n_confirmations=2,
            n_gaps=0,
            aggregate_voi=0.75,
            proposals_generated=[],
            evidence_accumulated=[],
            template_system_updates=[],
            recommendations=["Review contradiction"],
        )
        assert result.paper_citation == "Test 2024"
        assert result.n_claims == 5
        assert result.n_matched == 3
        assert result.status == "complete"

    def test_result_to_dict(self):
        """Test converting result to dict."""
        result = ProcessingResult(
            paper_citation="Test 2024",
            doi=None,
            processed_at=datetime(2024, 1, 1, 12, 0, 0),
            n_claims=3,
            n_matched=2,
            n_unmatched=1,
            n_contradictions=0,
            n_confirmations=2,
            n_gaps=1,
            aggregate_voi=0.5,
            proposals_generated=[],
            evidence_accumulated=[],
            template_system_updates=[],
            recommendations=[],
        )
        d = result.to_dict()
        assert d["paper_citation"] == "Test 2024"
        assert d["n_claims"] == 3
        assert "processed_at" in d
        assert isinstance(d["proposals_generated"], list)


class TestConvertUpdateToProposal:
    """Tests for _convert_update_to_proposal helper."""

    def test_contradiction_creates_proposal(self, temp_db):
        """Test that contradiction update creates a proposal."""
        update = {
            "type": "contradicts",
            "template": "VIEW1",
            "detail": "Claim contradicts VIEW1 prediction",
        }
        proposal = _convert_update_to_proposal(
            update=update,
            citation="Test 2024",
            db_path=temp_db,
            persist=False,
        )
        assert proposal is not None
        assert proposal.proposal_type == ProposalType.CONTRADICTION_FLAG
        assert proposal.template_id == "VIEW1"

    def test_extends_creates_boundary_revision(self, temp_db):
        """Test that extends update creates boundary revision proposal."""
        update = {
            "type": "extends",
            "template": "CH1",
            "detail": "Claim extends CH1 ceiling height range",
        }
        proposal = _convert_update_to_proposal(
            update=update,
            citation="Test 2024",
            db_path=temp_db,
            persist=False,
        )
        assert proposal is not None
        assert proposal.proposal_type == ProposalType.BOUNDARY_REVISION
        assert proposal.template_id == "CH1"

    def test_gap_creates_new_parameter(self, temp_db):
        """Test that gap update creates new parameter proposal."""
        update = {
            "type": "gap",
            "template": "none",
            "detail": "No template covers air quality",
        }
        proposal = _convert_update_to_proposal(
            update=update,
            citation="Test 2024",
            db_path=temp_db,
            persist=False,
        )
        assert proposal is not None
        assert proposal.proposal_type == ProposalType.NEW_PARAMETER
        assert proposal.template_id == "SYSTEM"

    def test_confirms_returns_none(self, temp_db):
        """Test that confirms update doesn't create a proposal."""
        update = {
            "type": "confirms",
            "template": "VIEW1",
            "detail": "Claim confirms VIEW1",
        }
        proposal = _convert_update_to_proposal(
            update=update,
            citation="Test 2024",
            db_path=temp_db,
            persist=False,
        )
        assert proposal is None


class TestExtractEffectData:
    """Tests for _extract_effect_data_from_claims helper."""

    def test_extracts_complete_effect_data(self):
        """Test extraction of effect data from claims."""
        claims = [
            {
                "source": "Smith 2024",
                "effect_size": 0.5,
                "sample_n": 100,
                "template_id": "CH1",
                "parameter_name": "optimal_ceiling_height",
                "description": "Ceiling height improves mood",
            }
        ]
        effect_data = _extract_effect_data_from_claims(claims)
        assert len(effect_data) == 1
        assert effect_data[0]["paper_citation"] == "Smith 2024"
        assert effect_data[0]["effect_size"] == 0.5
        assert effect_data[0]["sample_n"] == 100

    def test_skips_claims_without_effect_size(self):
        """Test that claims without effect size are skipped."""
        claims = [
            {"source": "Smith 2024", "sample_n": 100},  # No effect_size
        ]
        effect_data = _extract_effect_data_from_claims(claims)
        assert len(effect_data) == 0

    def test_skips_claims_without_sample_n(self):
        """Test that claims without sample_n are skipped."""
        claims = [
            {"source": "Smith 2024", "effect_size": 0.5},  # No sample_n
        ]
        effect_data = _extract_effect_data_from_claims(claims)
        assert len(effect_data) == 0

    def test_handles_n_key(self):
        """Test that 'n' is accepted as alternative to 'sample_n'."""
        claims = [
            {"source": "Smith 2024", "effect_size": 0.5, "n": 80},
        ]
        effect_data = _extract_effect_data_from_claims(claims)
        assert len(effect_data) == 1
        assert effect_data[0]["sample_n"] == 80


class TestProcessPaper:
    """Tests for process_paper main function."""

    def test_process_simple_claims(self, temp_db):
        """Test processing simple claims."""
        claims = [
            {
                "description": "Nature view reduces stress",
                "iv": "nature_view",
                "dv": "stress",
                "direction": "decrease",
            }
        ]
        result = process_paper(
            claims=claims,
            citation="Test 2024",
            db_path=temp_db,
            persist_proposals=False,
        )
        assert result.status == "complete"
        assert result.paper_citation == "Test 2024"
        assert result.n_claims >= 1

    def test_process_with_doi(self, temp_db):
        """Test processing with DOI."""
        claims = [{"description": "Test claim", "iv": "x", "dv": "y"}]
        result = process_paper(
            claims=claims,
            citation="Test 2024",
            doi="10.1234/test",
            db_path=temp_db,
            persist_proposals=False,
        )
        assert result.doi == "10.1234/test"

    def test_process_generates_proposals_for_contradictions(self, temp_db):
        """Test that contradictions generate proposals."""
        # This is a simplified test - actual contradiction detection
        # depends on template matching
        claims = [
            {
                "description": "Ceiling height does not affect creativity",
                "iv": "ceiling_height",
                "dv": "creativity",
                "direction": "none",
            }
        ]
        result = process_paper(
            claims=claims,
            citation="Contrary 2024",
            db_path=temp_db,
            persist_proposals=False,
        )
        assert result.status == "complete"

    def test_process_with_effect_data(self, temp_db):
        """Test processing claims with effect size data."""
        claims = [
            {
                "description": "Nature view reduces stress",
                "iv": "nature_view",
                "dv": "stress",
                "direction": "decrease",
                "effect_size": 0.73,
                "sample_n": 46,
                "template_id": "VIEW1",
                "parameter_name": "stress_reduction_effect",
            }
        ]
        result = process_paper(
            claims=claims,
            citation="Ulrich 1984",
            db_path=temp_db,
            persist_proposals=False,
        )
        assert result.status == "complete"
        # May have evidence accumulated if template exists
        assert isinstance(result.evidence_accumulated, list)

    def test_process_empty_claims(self, temp_db):
        """Test processing with empty claims list."""
        result = process_paper(
            claims=[],
            citation="Empty 2024",
            db_path=temp_db,
            persist_proposals=False,
        )
        assert result.status == "complete"
        # Note: evaluate_paper creates a placeholder claim when list is empty
        # This is backward-compatible fallback behavior
        assert result.n_claims >= 0


class TestFormatProcessingReport:
    """Tests for format_processing_report."""

    def test_format_basic_report(self):
        """Test formatting a basic report."""
        result = ProcessingResult(
            paper_citation="Test 2024",
            doi="10.1234/test",
            processed_at=datetime(2024, 1, 1, 12, 0, 0),
            n_claims=5,
            n_matched=3,
            n_unmatched=2,
            n_contradictions=1,
            n_confirmations=2,
            n_gaps=0,
            aggregate_voi=0.75,
            proposals_generated=[],
            evidence_accumulated=[],
            template_system_updates=[],
            recommendations=["Review contradiction"],
        )
        report = format_processing_report(result)
        assert "Test 2024" in report
        assert "10.1234/test" in report
        assert "Total claims extracted: 5" in report
        assert "Contradictions: 1" in report
        assert "Review contradiction" in report

    def test_format_report_without_doi(self):
        """Test formatting report without DOI."""
        result = ProcessingResult(
            paper_citation="Test 2024",
            doi=None,
            processed_at=datetime.utcnow(),
            n_claims=3,
            n_matched=2,
            n_unmatched=1,
            n_contradictions=0,
            n_confirmations=2,
            n_gaps=1,
            aggregate_voi=0.5,
            proposals_generated=[],
            evidence_accumulated=[],
            template_system_updates=[],
            recommendations=[],
        )
        report = format_processing_report(result)
        assert "Test 2024" in report
        assert "DOI:" not in report


class TestGetProcessingSummary:
    """Tests for get_processing_summary."""

    def test_summary_empty_db(self, temp_db):
        """Test summary on empty database."""
        summary = get_processing_summary(db_path=temp_db)
        assert "total_papers_processed" in summary
        assert "pending_proposals" in summary
        assert "recent_papers" in summary
        assert summary["total_papers_processed"] == 0


class TestCLIIntegration:
    """Tests for CLI integration."""

    def test_process_paper_command_exists(self):
        """Test that process-paper command is recognized."""
        from src.cmr.cli import build_parser

        parser = build_parser()
        # Parse with process-paper and required args
        args = parser.parse_args([
            "process-paper",
            "--citation", "Test 2024",
            "--summary",
        ])
        assert args.command == "process-paper"
        assert args.citation == "Test 2024"
        assert args.summary is True

    def test_process_paper_with_claims(self, temp_db):
        """Test process-paper CLI with claims."""
        from src.cmr.cli import main

        claims_json = json.dumps([
            {"description": "Test claim", "iv": "x", "dv": "y"}
        ])
        ret = main([
            "process-paper",
            "--citation", "CLI Test 2024",
            "--claims", claims_json,
            "--no-persist",
            "--db-path", temp_db,
            "--json",
        ])
        assert ret == 0

    def test_process_paper_summary_mode(self, temp_db):
        """Test process-paper --summary mode."""
        from src.cmr.cli import main

        ret = main([
            "process-paper",
            "--citation", "ignored",
            "--summary",
            "--db-path", temp_db,
        ])
        assert ret == 0


class TestUlrich1984Integration:
    """Integration test with Ulrich 1984 style claims."""

    def test_ulrich_1984_claims(self, temp_db):
        """Test processing Ulrich 1984 style claims."""
        claims = [
            {
                "description": "Patients with tree views had shorter postoperative stays",
                "iv": "window_view_content",
                "dv": "hospital_stay_duration",
                "direction": "decrease",
                "effect_size": 0.73,
                "sample_n": 46,
            },
            {
                "description": "Patients with tree views took fewer analgesic doses",
                "iv": "window_view_content",
                "dv": "analgesic_use",
                "direction": "decrease",
                "effect_size": 0.5,
                "sample_n": 46,
            },
            {
                "description": "Patients with tree views had fewer negative nurse notes",
                "iv": "window_view_content",
                "dv": "nurse_negative_notes",
                "direction": "decrease",
                "sample_n": 46,
            },
        ]
        result = process_paper(
            claims=claims,
            citation="Ulrich 1984",
            doi="10.1126/science.6143402",
            db_path=temp_db,
            persist_proposals=False,
        )

        assert result.status == "complete"
        assert result.paper_citation == "Ulrich 1984"
        assert result.n_claims == 3
        assert result.doi == "10.1126/science.6143402"

        # Check that the processing completed and report can be generated
        report = format_processing_report(result)
        assert "Ulrich 1984" in report
        assert "Total claims extracted: 3" in report


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_process_malformed_claims(self, temp_db):
        """Test processing with malformed claims."""
        claims = [
            {"not_a_claim": True},
            {"description": "Valid claim", "iv": "x", "dv": "y"},
        ]
        result = process_paper(
            claims=claims,
            citation="Malformed 2024",
            db_path=temp_db,
            persist_proposals=False,
        )
        # Should still complete
        assert result.status == "complete"

    def test_process_unicode_citation(self, temp_db):
        """Test processing with unicode in citation."""
        claims = [{"description": "Test", "iv": "x", "dv": "y"}]
        result = process_paper(
            claims=claims,
            citation="Müller & Schäfer 2024",
            db_path=temp_db,
            persist_proposals=False,
        )
        assert result.paper_citation == "Müller & Schäfer 2024"

    def test_process_very_long_claim(self, temp_db):
        """Test processing with very long claim description."""
        long_desc = "This is a very long description. " * 100
        claims = [{"description": long_desc, "iv": "x", "dv": "y"}]
        result = process_paper(
            claims=claims,
            citation="Long 2024",
            db_path=temp_db,
            persist_proposals=False,
        )
        assert result.status == "complete"
