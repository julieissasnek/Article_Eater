"""
Tests for PaperEvidenceAuditor service.

Tests cover:
- Markdown paper parsing and claim extraction
- Cross-reference against mock ATLAS data
- Search target generation
- Pipeline submission
- End-to-end functionality
"""

import pytest
import tempfile
import sqlite3
from pathlib import Path

from src.services.paper_evidence_auditor import (
    Claim,
    ClaimAssessment,
    SearchTarget,
    EvidenceAuditReport,
    MarkdownPaperParser,
    AtlasBeliefQuerier,
    PaperEvidenceAuditor
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def temp_paper_file():
    """Create temporary Markdown paper file."""
    paper_content = """# The Goldilocks Principle

## Introduction

This paper demonstrates that optimal stimulation exists across sensory modalities.

## Section 2: Historical Context

### Part 2.1: Wundt and Arousal Theory

Wundt (1874) found that stimulus intensity produces an inverted-U arousal curve.
The effect size was moderate, with d = 0.35 across multiple studies.

### Part 2.2: Berlyne and Aesthetics

Berlyne (1971) showed that complexity and novelty both follow inverted-U preference curves.
This study compared Japanese and German participants on visual complexity preference.
Japanese preferred D ≈ 1.10, German preferred D ≈ 1.45, showing large effect d = 0.83.

## Section 4: Cross-Modal Evidence

Peak acoustic preference occurs at 50-60 dB LAeq according to soundscape research.
Thermal comfort follows an inverted-U as well, with optimal temperature at T_neutral.

We measured social group density and found 3-5 groups produce maximum engagement.
The effect size for social density was d = 0.32, showing moderate effect.
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(paper_content)
        return f.name


@pytest.fixture
def temp_db_with_beliefs():
    """Create temporary database with mock ATLAS beliefs."""
    db_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    db_path = db_file.name
    db_file.close()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create beliefs table
    cursor.execute("""
    CREATE TABLE beliefs (
        belief_id TEXT PRIMARY KEY,
        content TEXT,
        tags TEXT,
        credence_value REAL
    )
    """)

    # Insert mock beliefs related to paper claims
    beliefs = [
        ("B001", "Wundt inverted-U arousal curve foundation", "Wundt, arousal, inverted-U", 0.8),
        ("B002", "Berlyne optimal arousal theory aesthetic preference", "Berlyne, optimal, complexity", 0.75),
        ("B003", "Japanese aesthetic preference visual complexity", "Japanese, aesthetic, complexity", 0.7),
        ("B004", "Acoustic preference loudness ISO 12913 soundscape", "acoustic, loudness, preference", 0.72),
        ("B005", "Thermal comfort de Dear adaptive model", "thermal, comfort, temperature", 0.78),
        ("B006", "Social group density cognitive monitoring", "social, density, group", 0.45),
        ("B007", "Fractal dimension visual preference Taylor", "fractal, dimension, visual", 0.8),
    ]

    for belief_id, content, tags, credence in beliefs:
        cursor.execute("""
        INSERT INTO beliefs (belief_id, content, tags, credence_value)
        VALUES (?, ?, ?, ?)
        """, (belief_id, content, tags, credence))

    # Create gap_searches table for submission testing
    cursor.execute("""
    CREATE TABLE gap_searches (
        id INTEGER PRIMARY KEY,
        source TEXT,
        status TEXT,
        description TEXT,
        suggested_search TEXT,
        priority_score REAL
    )
    """)

    conn.commit()
    conn.close()

    return db_path


# ============================================================================
# Tests: Markdown Parser
# ============================================================================

class TestMarkdownPaperParser:

    def test_parse_claims_extraction(self, temp_paper_file):
        """Test that parser extracts claims from markdown."""
        parser = MarkdownPaperParser()
        claims = parser.parse_claims(temp_paper_file)

        assert len(claims) > 0
        assert all(isinstance(c, Claim) for c in claims)

    def test_parse_claims_sections(self, temp_paper_file):
        """Test that claims are tagged with sections."""
        parser = MarkdownPaperParser()
        claims = parser.parse_claims(temp_paper_file)

        sections = set(c.section for c in claims)
        assert len(sections) > 0
        assert any("2" in section or "4" in section for section in sections)

    def test_claim_type_inference(self, temp_paper_file):
        """Test that claim types are inferred correctly."""
        parser = MarkdownPaperParser()
        claims = parser.parse_claims(temp_paper_file)

        # Should find multiple claim types
        claim_types = set(c.claim_type for c in claims)
        assert len(claim_types) >= 1  # At least one type detected

        # All claims should have valid types
        valid_types = {"FACTUAL", "QUANTITATIVE", "CAUSAL", "COMPARATIVE"}
        assert all(c.claim_type in valid_types for c in claims)

    def test_keyword_extraction(self, temp_paper_file):
        """Test that keywords are extracted from claims."""
        parser = MarkdownPaperParser()
        claims = parser.parse_claims(temp_paper_file)

        for claim in claims:
            assert len(claim.evidence_keywords) > 0
            assert all(isinstance(k, str) for k in claim.evidence_keywords)

    def test_title_extraction(self, temp_paper_file):
        """Test that paper title is extracted."""
        parser = MarkdownPaperParser()
        title = parser.extract_title(temp_paper_file)

        assert title == "The Goldilocks Principle"


# ============================================================================
# Tests: ATLAS Belief Querier
# ============================================================================

class TestAtlasBeliefQuerier:

    def test_find_supporting_beliefs_with_match(self, temp_db_with_beliefs):
        """Test finding beliefs that match claim keywords."""
        querier = AtlasBeliefQuerier(temp_db_with_beliefs)

        claim = Claim(
            claim_id="C001",
            section="2.1",
            subsection="Wundt",
            claim_text="Wundt proposed inverted-U",
            claim_type="FACTUAL",
            evidence_keywords=["Wundt", "arousal", "inverted-U"]
        )

        beliefs, avg_credence = querier.find_supporting_beliefs(claim)

        assert len(beliefs) > 0
        assert avg_credence > 0.0

    def test_find_supporting_beliefs_no_match(self, temp_db_with_beliefs):
        """Test handling of claims with no matching beliefs."""
        querier = AtlasBeliefQuerier(temp_db_with_beliefs)

        claim = Claim(
            claim_id="C999",
            section="X",
            subsection="None",
            claim_text="Unknown claim about quantum foam",
            claim_type="FACTUAL",
            evidence_keywords=["quantum", "foam", "spacetime"]
        )

        beliefs, avg_credence = querier.find_supporting_beliefs(claim)

        assert len(beliefs) == 0
        assert avg_credence == 0.0

    def test_assess_support_level_well_supported(self):
        """Test support level assessment: well-supported."""
        querier = AtlasBeliefQuerier(":memory:")

        level, confidence = querier.assess_support_level(avg_credence=0.75, num_beliefs=3)

        assert level == "WELL_SUPPORTED"
        assert confidence > 0.75

    def test_assess_support_level_partial(self):
        """Test support level assessment: partially-supported."""
        querier = AtlasBeliefQuerier(":memory:")

        level, confidence = querier.assess_support_level(avg_credence=0.55, num_beliefs=1)

        assert level == "PARTIALLY_SUPPORTED"
        assert 0.5 < confidence < 0.8

    def test_assess_support_level_unsupported(self):
        """Test support level assessment: unsupported."""
        querier = AtlasBeliefQuerier(":memory:")

        level, confidence = querier.assess_support_level(avg_credence=0.3, num_beliefs=0)

        assert level == "UNSUPPORTED"
        assert confidence > 0.5


# ============================================================================
# Tests: Search Target Generation
# ============================================================================

class TestSearchTargetGeneration:

    def test_generate_search_targets_for_gaps(self, temp_paper_file, temp_db_with_beliefs):
        """Test that search targets are generated for unsupported claims."""
        auditor = PaperEvidenceAuditor(temp_db_with_beliefs)
        report = auditor.audit_paper(temp_paper_file)

        targets = auditor.generate_search_targets(report)

        assert len(targets) > 0
        assert all(isinstance(t, SearchTarget) for t in targets)

    def test_search_targets_prioritized(self, temp_paper_file, temp_db_with_beliefs):
        """Test that search targets are ranked by priority."""
        auditor = PaperEvidenceAuditor(temp_db_with_beliefs)
        report = auditor.audit_paper(temp_paper_file)
        targets = auditor.generate_search_targets(report)

        if len(targets) > 1:
            # Later targets should have lower priority scores
            for i in range(len(targets) - 1):
                assert targets[i].priority_score >= targets[i + 1].priority_score

    def test_search_targets_have_queries(self, temp_paper_file, temp_db_with_beliefs):
        """Test that search targets have search queries."""
        auditor = PaperEvidenceAuditor(temp_db_with_beliefs)
        report = auditor.audit_paper(temp_paper_file)
        targets = auditor.generate_search_targets(report)

        for target in targets:
            assert len(target.search_query) > 0
            assert isinstance(target.search_query, str)
            assert "study" in target.search_query or "research" in target.search_query.lower()

    def test_search_targets_have_type(self, temp_paper_file, temp_db_with_beliefs):
        """Test that search targets specify expected article type."""
        auditor = PaperEvidenceAuditor(temp_db_with_beliefs)
        report = auditor.audit_paper(temp_paper_file)
        targets = auditor.generate_search_targets(report)

        for target in targets:
            assert target.expected_article_type in ["empirical", "meta-analysis", "review", "theoretical"]


# ============================================================================
# Tests: Full Pipeline
# ============================================================================

class TestFullPipeline:

    def test_full_pipeline_execution(self, temp_paper_file, temp_db_with_beliefs):
        """Test complete audit → targets → submission pipeline."""
        auditor = PaperEvidenceAuditor(temp_db_with_beliefs)

        result = auditor.full_pipeline(temp_paper_file)

        assert "paper" in result
        assert "claims_total" in result
        assert "well_supported" in result
        assert "unsupported" in result
        assert "search_targets" in result
        assert result["claims_total"] > 0

    def test_pipeline_submission(self, temp_paper_file, temp_db_with_beliefs):
        """Test that search targets are submitted to pipeline."""
        auditor = PaperEvidenceAuditor(temp_db_with_beliefs)
        report = auditor.audit_paper(temp_paper_file)
        targets = auditor.generate_search_targets(report)

        submissions = auditor.submit_to_pipeline(targets, temp_db_with_beliefs)

        assert submissions > 0

        # Verify submissions were recorded in interpretation_space_suggestions
        conn = sqlite3.connect(temp_db_with_beliefs)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM interpretation_space_suggestions WHERE source = ?", ("paper_evidence_gap",))
        count = cursor.fetchone()[0]
        conn.close()

        assert count == submissions

    def test_audit_report_statistics(self, temp_paper_file, temp_db_with_beliefs):
        """Test that audit report contains correct statistics."""
        auditor = PaperEvidenceAuditor(temp_db_with_beliefs)
        report = auditor.audit_paper(temp_paper_file)

        # Check totals add up
        total = report.well_supported + report.partially_supported + report.unsupported + report.contradicted
        assert total == report.total_claims

        # Check overall warrant is in valid range
        assert 0.0 <= report.overall_warrant <= 1.0


# ============================================================================
# Tests: Data Structures
# ============================================================================

class TestDataStructures:

    def test_claim_creation(self):
        """Test Claim dataclass."""
        claim = Claim(
            claim_id="C001",
            section="2.1",
            subsection="Intro",
            claim_text="Test claim",
            claim_type="FACTUAL",
            evidence_keywords=["keyword1", "keyword2"]
        )

        assert claim.claim_id == "C001"
        assert claim.claim_type == "FACTUAL"
        assert len(claim.evidence_keywords) == 2

    def test_assessment_to_dict(self):
        """Test ClaimAssessment serialization."""
        claim = Claim(
            claim_id="C001",
            section="2",
            subsection="Sub",
            claim_text="Test",
            claim_type="FACTUAL",
            evidence_keywords=[]
        )

        assessment = ClaimAssessment(
            claim=claim,
            support_level="WELL_SUPPORTED",
            atlas_beliefs=["B001"],
            avg_warrant=0.8,
            confidence=0.9,
            notes="Good match"
        )

        d = assessment.to_dict()
        assert d["claim_id"] == "C001"
        assert d["support_level"] == "WELL_SUPPORTED"
        assert d["avg_warrant"] == 0.8

    def test_search_target_to_dict(self):
        """Test SearchTarget serialization."""
        target = SearchTarget(
            target_id="ST001",
            section="2",
            claim_id="C001",
            claim_summary="Test claim",
            search_query="test query",
            priority="HIGH",
            priority_score=0.9
        )

        d = target.to_dict()
        assert d["target_id"] == "ST001"
        assert d["priority"] == "HIGH"
        assert d["search_query"] == "test query"

    def test_evidence_audit_report_properties(self):
        """Test EvidenceAuditReport statistical properties."""
        claim = Claim(
            claim_id="C001",
            section="2",
            subsection="Sub",
            claim_text="Test",
            claim_type="FACTUAL",
            evidence_keywords=[]
        )

        assessments = [
            ClaimAssessment(claim=claim, support_level="WELL_SUPPORTED", avg_warrant=0.8),
            ClaimAssessment(claim=claim, support_level="PARTIALLY_SUPPORTED", avg_warrant=0.6),
            ClaimAssessment(claim=claim, support_level="UNSUPPORTED", avg_warrant=0.2),
        ]

        report = EvidenceAuditReport(
            paper_path="/tmp/test.md",
            paper_title="Test Paper",
            audit_date="2026-03-02",
            total_claims=3,
            assessments=assessments
        )

        assert report.well_supported == 1
        assert report.partially_supported == 1
        assert report.unsupported == 1
        assert report.overall_warrant == pytest.approx(0.533, abs=0.01)


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:

    def test_end_to_end_with_real_paper(self, temp_paper_file, temp_db_with_beliefs):
        """Test complete workflow with realistic paper."""
        auditor = PaperEvidenceAuditor(temp_db_with_beliefs)

        # Step 1: Audit
        result = auditor.full_pipeline(temp_paper_file)

        assert result["claims_total"] > 0
        assert result["search_targets"] > 0

        # Step 2: Verify report
        report = result["report"]
        assert report.overall_warrant >= 0.0
        assert len(report.assessments) == report.total_claims

        # Step 3: Verify submissions
        conn = sqlite3.connect(temp_db_with_beliefs)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM interpretation_space_suggestions WHERE source = ?", ("paper_evidence_gap",))
        final_count = cursor.fetchone()[0]
        conn.close()

        assert final_count > 0

    def test_multiple_papers_in_sequence(self, temp_paper_file, temp_db_with_beliefs):
        """Test auditing multiple papers maintains independence."""
        auditor = PaperEvidenceAuditor(temp_db_with_beliefs)

        result1 = auditor.full_pipeline(temp_paper_file)
        result2 = auditor.full_pipeline(temp_paper_file)

        # Results should be identical (same paper)
        assert result1["claims_total"] == result2["claims_total"]
        assert result1["well_supported"] == result2["well_supported"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
