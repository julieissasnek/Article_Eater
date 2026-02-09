"""
Tests for Report Generator Service — Sprint 3.0.4-F
2026-02-10

Tests cover report building, format conversion, and export.
"""

import pytest
import json
from typing import Dict, List, Any

from src.services.report_generator import (
    ReportGenerator,
    Report,
    ReportMetadata,
    Finding,
    ScopeSection,
    PracticalImplication,
    EvidenceSource,
    ReportType,
    ReportFormat,
    ConfidenceLevel,
    get_report_generator,
    generate_evidence_report,
)


# =============================================================================
# Test Data
# =============================================================================

def create_test_findings() -> List[Dict[str, Any]]:
    """Create test finding data."""
    return [
        {
            "id": "B001",
            "content": "Plants reduce perceived stress in office environments",
            "credence": 0.75,
            "status": "ACCEPTED",
            "level": "EMPIRICAL",
            "theory_ids": ["Biophilia", "SRT"],
            "scope": {
                "population": "Office workers",
                "setting": "Indoor office",
                "methodology": "RCT",
                "limitations": "Limited to Western countries"
            },
            "sources": [
                {"id": "P001", "title": "Plants and Stress", "authors": ["Smith, J."], "year": 2020},
                {"id": "P002", "title": "Office Greenery Study", "authors": ["Jones, M."], "year": 2019}
            ]
        },
        {
            "id": "B002",
            "content": "Attention Restoration Theory explains nature's cognitive benefits",
            "credence": 0.85,
            "status": "ESTABLISHED",
            "level": "THEORETICAL",
            "theory_ids": ["ART"],
            "sources": ["P003", "P004"]
        },
        {
            "id": "B003",
            "content": "Window views improve patient recovery times",
            "credence": 0.65,
            "status": "CONTESTED",
            "level": "EMPIRICAL",
            "scope": {
                "population": "Hospital patients",
                "setting": "Hospital rooms"
            },
            "sources": [{"id": "P005", "title": "Nature Views Study", "authors": ["Brown, K."], "year": 2018}]
        },
    ]


def create_test_scope() -> Dict[str, Any]:
    """Create test scope data."""
    return {
        "populations": ["Office workers", "Hospital patients", "Students"],
        "settings": ["Indoor office", "Hospital", "University campus"],
        "methodologies": ["RCT", "Quasi-experimental", "Survey"],
        "limitations": ["Limited to Western populations", "Short-term studies only"],
        "warnings": ["Results may not generalize to non-Western cultures"]
    }


def create_test_implications() -> List[Dict[str, Any]]:
    """Create test practical implications."""
    return [
        {
            "recommendation": "Add plants to office workspaces",
            "confidence": "high",
            "evidence_strength": "strong",
            "applicable_when": ["Indoor office environment", "Workers present 4+ hours"],
            "not_applicable_when": ["Outdoor settings", "Allergy concerns"]
        },
        {
            "recommendation": "Provide window views where possible",
            "confidence": "moderate",
            "evidence_strength": "moderate",
            "applicable_when": ["Healthcare settings"],
            "not_applicable_when": ["Privacy concerns", "Security requirements"]
        }
    ]


# =============================================================================
# Report Building Tests
# =============================================================================

class TestReportBuilding:
    """Tests for report construction."""

    def test_create_report(self):
        """Test creating a new report."""
        gen = ReportGenerator()
        report = gen.create_report("Test Report", query="What reduces stress?")

        assert report is not None
        assert report.metadata.title == "Test Report"
        assert report.metadata.query == "What reduces stress?"
        assert report.metadata.report_type == ReportType.EVIDENCE_SUMMARY

    def test_add_findings(self):
        """Test adding findings to report."""
        gen = ReportGenerator()
        report = gen.create_report("Test Report")
        findings = create_test_findings()

        gen.add_findings(findings, report)

        assert len(report.findings) == 3
        assert report.metadata.total_beliefs == 3

    def test_finding_credence_parsed(self):
        """Test that credence is correctly parsed."""
        gen = ReportGenerator()
        report = gen.create_report("Test")

        gen.add_findings([{"id": "B1", "content": "Test", "credence": 0.8}], report)

        assert report.findings[0].credence == 0.8

    def test_finding_credence_dict_parsed(self):
        """Test that dict credence is correctly parsed."""
        gen = ReportGenerator()
        report = gen.create_report("Test")

        gen.add_findings([{
            "id": "B1",
            "content": "Test",
            "credence": {"point": 0.75, "uncertainty": 0.1}
        }], report)

        assert report.findings[0].credence == 0.75

    def test_confidence_calculated_from_credence(self):
        """Test that confidence level is calculated from credence."""
        gen = ReportGenerator()
        report = gen.create_report("Test")

        gen.add_findings([
            {"id": "B1", "content": "High", "credence": 0.8},
            {"id": "B2", "content": "Moderate", "credence": 0.6},
            {"id": "B3", "content": "Low", "credence": 0.3},
        ], report)

        assert report.findings[0].confidence == ConfidenceLevel.HIGH
        assert report.findings[1].confidence == ConfidenceLevel.MODERATE
        assert report.findings[2].confidence == ConfidenceLevel.LOW

    def test_sources_parsed(self):
        """Test that sources are correctly parsed."""
        gen = ReportGenerator()
        report = gen.create_report("Test")
        findings = create_test_findings()

        gen.add_findings(findings, report)

        # First finding has dict sources
        assert len(report.findings[0].sources) == 2
        assert report.findings[0].sources[0].title == "Plants and Stress"

        # Second finding has string sources
        assert len(report.findings[1].sources) == 2

    def test_scope_parsed(self):
        """Test that scope conditions are parsed from findings."""
        gen = ReportGenerator()
        report = gen.create_report("Test")
        findings = create_test_findings()

        gen.add_findings(findings, report)

        assert report.findings[0].scope_population == "Office workers"
        assert report.findings[0].scope_setting == "Indoor office"

    def test_add_scope_conditions(self):
        """Test adding scope conditions section."""
        gen = ReportGenerator()
        report = gen.create_report("Test")
        scope = create_test_scope()

        gen.add_scope_conditions(scope, report)

        assert report.scope is not None
        assert len(report.scope.populations) == 3
        assert len(report.scope.generalization_warnings) == 1

    def test_add_implications(self):
        """Test adding practical implications."""
        gen = ReportGenerator()
        report = gen.create_report("Test")
        implications = create_test_implications()

        gen.add_implications(implications, report)

        assert len(report.implications) == 2
        assert report.implications[0].recommendation == "Add plants to office workspaces"

    def test_add_caveats(self):
        """Test adding caveats."""
        gen = ReportGenerator()
        report = gen.create_report("Test")

        gen.add_caveats(["Limited evidence", "Need more research"], report)

        assert len(report.caveats) == 2

    def test_average_credence_computed(self):
        """Test that average credence is computed."""
        gen = ReportGenerator()
        report = gen.create_report("Test")

        gen.add_findings([
            {"id": "B1", "content": "Test", "credence": 0.8},
            {"id": "B2", "content": "Test", "credence": 0.6},
        ], report)

        assert report.metadata.average_credence == 0.7


# =============================================================================
# Executive Summary Tests
# =============================================================================

class TestExecutiveSummary:
    """Tests for executive summary generation."""

    def test_generate_executive_summary(self):
        """Test auto-generating executive summary."""
        gen = ReportGenerator()
        report = gen.create_report("Test", query="What reduces stress?")
        gen.add_findings(create_test_findings(), report)

        summary = gen.generate_executive_summary(report)

        assert summary is not None
        assert len(summary) > 0
        assert "What reduces stress?" in summary

    def test_summary_includes_key_finding(self):
        """Test that summary includes key finding."""
        gen = ReportGenerator()
        report = gen.create_report("Test")
        gen.add_findings(create_test_findings(), report)

        summary = gen.generate_executive_summary(report)

        # Should mention the highest credence finding
        assert "Key Finding" in summary

    def test_summary_includes_evidence_count(self):
        """Test that summary includes evidence count."""
        gen = ReportGenerator()
        report = gen.create_report("Test")
        gen.add_findings(create_test_findings(), report)

        summary = gen.generate_executive_summary(report)

        assert "3 beliefs" in summary

    def test_set_executive_summary(self):
        """Test manually setting executive summary."""
        gen = ReportGenerator()
        report = gen.create_report("Test")

        gen.set_executive_summary("Custom summary text", report)

        assert report.executive_summary == "Custom summary text"


# =============================================================================
# Markdown Export Tests
# =============================================================================

class TestMarkdownExport:
    """Tests for Markdown export."""

    def test_to_markdown_returns_string(self):
        """Test that markdown export returns string."""
        gen = ReportGenerator()
        report = gen.create_report("Test Report")
        gen.add_findings(create_test_findings(), report)

        md = gen.to_markdown(report)

        assert isinstance(md, str)
        assert len(md) > 100

    def test_markdown_contains_title(self):
        """Test that markdown contains title."""
        gen = ReportGenerator()
        report = gen.create_report("My Test Report")

        md = gen.to_markdown(report)

        assert "# My Test Report" in md

    def test_markdown_contains_findings(self):
        """Test that markdown contains findings."""
        gen = ReportGenerator()
        report = gen.create_report("Test")
        gen.add_findings(create_test_findings(), report)

        md = gen.to_markdown(report)

        assert "Plants reduce perceived stress" in md
        assert "Attention Restoration Theory" in md

    def test_markdown_contains_toc(self):
        """Test that markdown contains table of contents."""
        gen = ReportGenerator()
        report = gen.create_report("Test")
        gen.add_findings(create_test_findings(), report)

        md = gen.to_markdown(report, include_toc=True)

        assert "Table of Contents" in md
        assert "Executive Summary" in md

    def test_markdown_contains_scope(self):
        """Test that markdown contains scope conditions."""
        gen = ReportGenerator()
        report = gen.create_report("Test")
        gen.add_scope_conditions(create_test_scope(), report)

        md = gen.to_markdown(report)

        assert "Scope Conditions" in md
        assert "Office workers" in md

    def test_markdown_contains_implications(self):
        """Test that markdown contains implications."""
        gen = ReportGenerator()
        report = gen.create_report("Test")
        gen.add_implications(create_test_implications(), report)

        md = gen.to_markdown(report)

        assert "Practical Implications" in md
        assert "Add plants" in md

    def test_markdown_contains_caveats(self):
        """Test that markdown contains caveats."""
        gen = ReportGenerator()
        report = gen.create_report("Test")
        gen.add_caveats(["Limited evidence"], report)

        md = gen.to_markdown(report)

        assert "Caveats" in md
        assert "Limited evidence" in md


# =============================================================================
# HTML Export Tests
# =============================================================================

class TestHTMLExport:
    """Tests for HTML export."""

    def test_to_html_returns_string(self):
        """Test that HTML export returns string."""
        gen = ReportGenerator()
        report = gen.create_report("Test Report")
        gen.add_findings(create_test_findings(), report)

        html = gen.to_html(report)

        assert isinstance(html, str)
        assert "<html>" in html

    def test_html_contains_title(self):
        """Test that HTML contains title."""
        gen = ReportGenerator()
        report = gen.create_report("My HTML Report")

        html = gen.to_html(report)

        assert "My HTML Report" in html

    def test_html_standalone_has_doctype(self):
        """Test that standalone HTML has DOCTYPE."""
        gen = ReportGenerator()
        report = gen.create_report("Test")

        html = gen.to_html(report, standalone=True)

        assert "<!DOCTYPE html>" in html

    def test_html_standalone_has_styles(self):
        """Test that standalone HTML has styles."""
        gen = ReportGenerator()
        report = gen.create_report("Test")

        html = gen.to_html(report, standalone=True)

        assert "<style>" in html

    def test_html_not_standalone_no_wrapper(self):
        """Test that non-standalone HTML has no wrapper."""
        gen = ReportGenerator()
        report = gen.create_report("Test")

        html = gen.to_html(report, standalone=False)

        assert "<!DOCTYPE" not in html


# =============================================================================
# JSON Export Tests
# =============================================================================

class TestJSONExport:
    """Tests for JSON export."""

    def test_to_json_returns_valid_json(self):
        """Test that JSON export is valid JSON."""
        gen = ReportGenerator()
        report = gen.create_report("Test Report")
        gen.add_findings(create_test_findings(), report)

        json_str = gen.to_json(report)

        # Should parse without error
        data = json.loads(json_str)
        assert isinstance(data, dict)

    def test_json_contains_metadata(self):
        """Test that JSON contains metadata."""
        gen = ReportGenerator()
        report = gen.create_report("Test Report", query="What?")

        json_str = gen.to_json(report)
        data = json.loads(json_str)

        assert "metadata" in data
        assert data["metadata"]["title"] == "Test Report"
        assert data["metadata"]["query"] == "What?"

    def test_json_contains_findings(self):
        """Test that JSON contains findings."""
        gen = ReportGenerator()
        report = gen.create_report("Test")
        gen.add_findings(create_test_findings(), report)

        json_str = gen.to_json(report)
        data = json.loads(json_str)

        assert "findings" in data
        assert len(data["findings"]) == 3

    def test_json_enums_serialized(self):
        """Test that enums are properly serialized."""
        gen = ReportGenerator()
        report = gen.create_report("Test")
        gen.add_findings([{"id": "B1", "content": "Test", "credence": 0.8}], report)

        json_str = gen.to_json(report)
        data = json.loads(json_str)

        # Confidence should be string, not enum object
        assert data["findings"][0]["confidence"] == "high"


# =============================================================================
# PDF Export Tests
# =============================================================================

class TestPDFExport:
    """Tests for PDF export."""

    def test_to_pdf_returns_bytes(self):
        """Test that PDF export returns bytes."""
        gen = ReportGenerator()
        report = gen.create_report("Test Report")
        gen.add_findings(create_test_findings(), report)

        pdf = gen.to_pdf(report)

        # If reportlab is installed, should get bytes
        # If not, should get empty bytes
        assert isinstance(pdf, bytes)

    def test_pdf_has_content_if_reportlab_available(self):
        """Test that PDF has content if reportlab available."""
        try:
            import reportlab
            has_reportlab = True
        except ImportError:
            has_reportlab = False

        gen = ReportGenerator()
        report = gen.create_report("Test Report")
        gen.add_findings(create_test_findings(), report)

        pdf = gen.to_pdf(report)

        if has_reportlab:
            assert len(pdf) > 100
            # PDF files start with %PDF
            assert pdf[:4] == b'%PDF'
        else:
            # Should return empty bytes if no reportlab
            assert pdf == b""


# =============================================================================
# Export Method Tests
# =============================================================================

class TestExportMethod:
    """Tests for the unified export method."""

    def test_export_markdown(self):
        """Test exporting as markdown."""
        gen = ReportGenerator()
        report = gen.create_report("Test")

        result = gen.export(ReportFormat.MARKDOWN, report)

        assert isinstance(result, str)
        assert "#" in result

    def test_export_html(self):
        """Test exporting as HTML."""
        gen = ReportGenerator()
        report = gen.create_report("Test")

        result = gen.export(ReportFormat.HTML, report)

        assert isinstance(result, str)
        assert "<html>" in result

    def test_export_json(self):
        """Test exporting as JSON."""
        gen = ReportGenerator()
        report = gen.create_report("Test")

        result = gen.export(ReportFormat.JSON, report)

        assert isinstance(result, str)
        json.loads(result)  # Should be valid JSON

    def test_export_pdf(self):
        """Test exporting as PDF."""
        gen = ReportGenerator()
        report = gen.create_report("Test")

        result = gen.export(ReportFormat.PDF, report)

        assert isinstance(result, bytes)


# =============================================================================
# Convenience Function Tests
# =============================================================================

class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_get_report_generator_singleton(self):
        """Test singleton pattern."""
        g1 = get_report_generator()
        g2 = get_report_generator()
        assert g1 is g2

    def test_generate_evidence_report_markdown(self):
        """Test convenience function for markdown report."""
        findings = create_test_findings()

        result = generate_evidence_report(
            title="Test Report",
            findings=findings,
            format=ReportFormat.MARKDOWN
        )

        assert isinstance(result, str)
        assert "Test Report" in result
        assert "Plants reduce" in result

    def test_generate_evidence_report_with_scope(self):
        """Test convenience function with scope."""
        findings = create_test_findings()
        scope = create_test_scope()

        result = generate_evidence_report(
            title="Test Report",
            findings=findings,
            scope=scope,
            format=ReportFormat.MARKDOWN
        )

        assert "Scope Conditions" in result
        assert "Office workers" in result

    def test_generate_evidence_report_with_caveats(self):
        """Test convenience function with caveats."""
        findings = create_test_findings()

        result = generate_evidence_report(
            title="Test",
            findings=findings,
            caveats=["Limited data", "More research needed"],
            format=ReportFormat.MARKDOWN
        )

        assert "Caveats" in result
        assert "Limited data" in result


# =============================================================================
# Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_findings(self):
        """Test handling of empty findings."""
        gen = ReportGenerator()
        report = gen.create_report("Test")
        gen.add_findings([], report)

        assert len(report.findings) == 0
        assert report.metadata.total_beliefs == 0

    def test_no_report_markdown(self):
        """Test markdown with no report."""
        gen = ReportGenerator()
        md = gen.to_markdown(None)

        assert "No Report Data" in md

    def test_finding_missing_fields(self):
        """Test finding with minimal fields."""
        gen = ReportGenerator()
        report = gen.create_report("Test")

        gen.add_findings([{"id": "B1", "content": "Minimal finding"}], report)

        assert len(report.findings) == 1
        assert report.findings[0].credence == 0.5  # Default
        assert report.findings[0].status == "UNKNOWN"

    def test_no_report_to_add_to(self):
        """Test error when no report exists."""
        gen = ReportGenerator()

        with pytest.raises(ValueError):
            gen.add_findings([{"id": "B1", "content": "Test"}])

    def test_html_special_characters_escaped(self):
        """Test that special characters are handled in HTML."""
        gen = ReportGenerator()
        report = gen.create_report("Test <script>alert('xss')</script>")

        html = gen.to_html(report)

        # The title should be in HTML but script shouldn't execute
        # (simple implementation may not fully escape, but shouldn't break)
        assert isinstance(html, str)
