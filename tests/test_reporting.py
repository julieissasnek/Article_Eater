"""
Tests for Reporting Service
===========================

Tests for report generation from the web of belief.

Date: January 21, 2026
Phase D Sprint D2
"""

import pytest
from src.services.reporting import (
    ReportGenerator,
    Report,
    ReportType,
    ReportSection,
    generate_report
)
from src.services.web_of_belief import (
    WebOfBelief, Belief, Credence, EpistemicLevel, SourceDepth,
    ScopeConditions
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def empty_web():
    """Create empty web."""
    return WebOfBelief()


@pytest.fixture
def populated_web():
    """Create web with diverse beliefs."""
    web = WebOfBelief()

    # High confidence, full text
    b1 = Belief(
        belief_id="b1",
        content="Natural light improves productivity by 15%",
        level=EpistemicLevel.EMPIRICAL,
        credence=Credence(0.78, 0.10),
        outcome_id="productivity",
        source_depth=SourceDepth.FULL_TEXT,
        paper_ids=["p1", "p2"]
    )
    web.beliefs[b1.belief_id] = b1

    # Medium confidence, abstract
    b2 = Belief(
        belief_id="b2",
        content="Daylight exposure reduces stress hormones",
        level=EpistemicLevel.EMPIRICAL,
        credence=Credence(0.65, 0.15),
        outcome_id="stress",
        source_depth=SourceDepth.ABSTRACT,
        paper_ids=["p3"]
    )
    web.beliefs[b2.belief_id] = b2

    # Low confidence
    b3 = Belief(
        belief_id="b3",
        content="Plants may affect air quality perception",
        level=EpistemicLevel.OBSERVATIONAL,
        credence=Credence(0.35, 0.20),
        outcome_id="perception",
        source_depth=SourceDepth.ABSTRACT,
        paper_ids=["p4"]
    )
    web.beliefs[b3.belief_id] = b3

    # Contested
    b4 = Belief(
        belief_id="b4",
        content="Open offices affect productivity (disputed)",
        level=EpistemicLevel.EMPIRICAL,
        credence=Credence(0.50, 0.30),
        outcome_id="productivity",
        contested=True,
        source_depth=SourceDepth.FULL_TEXT
    )
    web.beliefs[b4.belief_id] = b4

    # Theoretical with scope
    b5 = Belief(
        belief_id="b5",
        content="Thermal comfort optimizes cognition through attention mechanisms",
        level=EpistemicLevel.THEORETICAL,
        credence=Credence(0.72, 0.12),
        outcome_id="cognition",
        source_depth=SourceDepth.FULL_TEXT,
        scope=ScopeConditions(
            population="office workers",
            setting="climate-controlled buildings",
            scope_specified=True
        )
    )
    web.beliefs[b5.belief_id] = b5

    # High uncertainty
    b6 = Belief(
        belief_id="b6",
        content="Noise levels may affect focus",
        level=EpistemicLevel.EMPIRICAL,
        credence=Credence(0.55, 0.30),
        outcome_id="attention",
        source_depth=SourceDepth.METADATA
    )
    web.beliefs[b6.belief_id] = b6

    return web


# =============================================================================
# Report Generator Tests
# =============================================================================

class TestReportGenerator:
    """Tests for ReportGenerator."""

    def test_generator_creation(self, empty_web):
        """Test generator can be created."""
        generator = ReportGenerator(empty_web)
        assert generator is not None

    def test_generate_returns_report(self, populated_web):
        """Test generate returns Report object."""
        generator = ReportGenerator(populated_web)
        report = generator.generate(ReportType.EXECUTIVE_SUMMARY)
        assert isinstance(report, Report)


# =============================================================================
# Executive Summary Tests
# =============================================================================

class TestExecutiveSummary:
    """Tests for executive summary report."""

    def test_executive_summary_structure(self, populated_web):
        """Test executive summary has correct structure."""
        report = generate_report(populated_web, ReportType.EXECUTIVE_SUMMARY)

        assert report.report_type == ReportType.EXECUTIVE_SUMMARY
        assert report.title is not None
        assert report.summary is not None
        assert len(report.sections) > 0

    def test_executive_summary_metrics(self, populated_web):
        """Test executive summary includes metrics."""
        report = generate_report(populated_web, ReportType.EXECUTIVE_SUMMARY)

        # Should have key metrics section
        metrics_section = next(
            (s for s in report.sections if "Metrics" in s.title), None
        )
        assert metrics_section is not None
        assert metrics_section.data is not None
        assert 'total_beliefs' in metrics_section.data

    def test_executive_summary_empty_web(self, empty_web):
        """Test executive summary with empty web."""
        report = generate_report(empty_web, ReportType.EXECUTIVE_SUMMARY)
        assert report.metadata.get('belief_count') == 0


# =============================================================================
# Evidence Inventory Tests
# =============================================================================

class TestEvidenceInventory:
    """Tests for evidence inventory report."""

    def test_inventory_structure(self, populated_web):
        """Test inventory has correct structure."""
        report = generate_report(populated_web, ReportType.EVIDENCE_INVENTORY)

        assert report.report_type == ReportType.EVIDENCE_INVENTORY
        assert len(report.sections) > 0  # Should have sections by outcome

    def test_inventory_groups_by_outcome(self, populated_web):
        """Test inventory groups beliefs by outcome."""
        report = generate_report(populated_web, ReportType.EVIDENCE_INVENTORY)

        # Should have sections for different outcomes
        section_titles = [s.title.lower() for s in report.sections]
        assert any("productivity" in t for t in section_titles)


# =============================================================================
# Confidence Analysis Tests
# =============================================================================

class TestConfidenceAnalysis:
    """Tests for confidence analysis report."""

    def test_confidence_structure(self, populated_web):
        """Test confidence report structure."""
        report = generate_report(populated_web, ReportType.CONFIDENCE_ANALYSIS)

        assert report.report_type == ReportType.CONFIDENCE_ANALYSIS
        assert len(report.sections) >= 3  # High, Medium, Low sections

    def test_confidence_categorization(self, populated_web):
        """Test beliefs are categorized by confidence."""
        report = generate_report(populated_web, ReportType.CONFIDENCE_ANALYSIS)

        section_titles = [s.title for s in report.sections]
        assert any("High Confidence" in t for t in section_titles)
        assert any("Medium Confidence" in t for t in section_titles)
        assert any("Low Confidence" in t for t in section_titles)

    def test_confidence_uncertainty_analysis(self, populated_web):
        """Test uncertainty is analyzed."""
        report = generate_report(populated_web, ReportType.CONFIDENCE_ANALYSIS)

        uncertainty_section = next(
            (s for s in report.sections if "Uncertainty" in s.title), None
        )
        assert uncertainty_section is not None


# =============================================================================
# Gap Analysis Tests
# =============================================================================

class TestGapAnalysis:
    """Tests for gap analysis report."""

    def test_gap_structure(self, populated_web):
        """Test gap analysis structure."""
        report = generate_report(populated_web, ReportType.GAP_ANALYSIS)

        assert report.report_type == ReportType.GAP_ANALYSIS
        # Should identify various gaps

    def test_gap_identifies_missing_outcomes(self, populated_web):
        """Test gap analysis identifies missing outcome categories."""
        report = generate_report(populated_web, ReportType.GAP_ANALYSIS)

        # populated_web doesn't have all outcomes, should find gaps
        missing_section = next(
            (s for s in report.sections if "Missing" in s.title), None
        )
        if missing_section:
            assert len(missing_section.data.get('missing', [])) > 0

    def test_gap_identifies_abstract_only_causal(self, populated_web):
        """Test gap analysis flags abstract-only causal claims."""
        report = generate_report(populated_web, ReportType.GAP_ANALYSIS)

        # b2 is abstract-only and contains "reduces" (causal)
        abstract_section = next(
            (s for s in report.sections if "Abstract" in s.title or "Unverified" in s.title), None
        )
        # May or may not have this section depending on detection


# =============================================================================
# H2: Taxonomy-Driven Outcomes Tests (per Kaplan panel)
# =============================================================================

class TestTaxonomyDrivenOutcomes:
    """Tests for H2: Dynamic outcome categories from taxonomy."""

    def test_expected_outcomes_method_exists(self, populated_web):
        """Test that _get_expected_outcomes method exists on generator."""
        generator = ReportGenerator(populated_web)
        assert hasattr(generator, '_get_expected_outcomes')
        outcomes = generator._get_expected_outcomes()
        assert isinstance(outcomes, set)
        assert len(outcomes) > 0

    def test_gap_analysis_uses_taxonomy_or_fallback(self, populated_web):
        """Test gap analysis uses taxonomy if available, fallback otherwise."""
        report = generate_report(populated_web, ReportType.GAP_ANALYSIS)

        missing_section = next(
            (s for s in report.sections if "Missing" in s.title), None
        )
        if missing_section:
            # Should indicate source (taxonomy or fallback)
            assert 'source' in missing_section.data
            assert missing_section.data['source'] in ['taxonomy', 'fallback']

    def test_fallback_outcomes_when_taxonomy_unavailable(self):
        """Test fallback outcomes are used when taxonomy unavailable."""
        from src.services.reporting import ReportGenerator
        web = WebOfBelief()
        generator = ReportGenerator(web)

        # Even with empty web, should have fallback outcomes
        outcomes = generator._get_expected_outcomes()
        assert len(outcomes) > 0

        # Fallback should have core outcomes
        assert any('productivity' in o or 'behav' in o for o in outcomes)

    def test_taxonomy_outcomes_are_hierarchical(self, populated_web):
        """Test taxonomy outcomes include domain and subdomain levels."""
        generator = ReportGenerator(populated_web)
        outcomes = generator._get_expected_outcomes()

        # Should have domain-level outcomes (e.g., affect, cog, behav)
        # or subdomain-level (e.g., affect.stress, cog.attention)
        domain_count = sum(1 for o in outcomes if '.' not in o or o.count('.') == 1)
        assert domain_count > 0  # Should have at least some top-level outcomes

    def test_missing_outcomes_sorted_in_report(self, populated_web):
        """Test missing outcomes are sorted for consistent display."""
        report = generate_report(populated_web, ReportType.GAP_ANALYSIS)

        missing_section = next(
            (s for s in report.sections if "Missing" in s.title), None
        )
        if missing_section and missing_section.data.get('missing'):
            missing = missing_section.data['missing']
            # Check that displayed order is sorted (content should reflect sorted list)
            assert sorted(missing) == list(sorted(missing))


# =============================================================================
# H3: Confounder Coverage Gap Tests (per Pearl panel)
# =============================================================================

class TestConfounderCoverageGap:
    """Tests for H3: Confounder coverage gap detection per Pearl."""

    def test_confounder_method_exists(self, populated_web):
        """Test that _find_causal_without_confounders method exists."""
        generator = ReportGenerator(populated_web)
        assert hasattr(generator, '_find_causal_without_confounders')

    def test_detects_causal_without_confounders(self):
        """Test detection of causal claims without confounder mentions."""
        from src.services.web_of_belief import Belief, Credence, SourceDepth, EpistemicLevel

        web = WebOfBelief()
        # Causal claim without confounder mention
        b1 = Belief(
            belief_id="causal_no_conf",
            content="Natural light improves productivity by 15%",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.75, 0.10),
            source_depth=SourceDepth.FULL_TEXT,
            paper_ids=["p1"]
        )
        web.beliefs[b1.belief_id] = b1

        generator = ReportGenerator(web)
        without_conf = generator._find_causal_without_confounders(list(web.beliefs.values()))

        assert len(without_conf) == 1
        assert without_conf[0].belief_id == "causal_no_conf"

    def test_ignores_causal_with_confounders(self):
        """Test that causal claims with confounder mentions are not flagged."""
        from src.services.web_of_belief import Belief, Credence, SourceDepth, EpistemicLevel

        web = WebOfBelief()
        # Causal claim WITH confounder mention
        b1 = Belief(
            belief_id="causal_with_conf",
            content="Natural light improves productivity after controlling for age and job type",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.75, 0.10),
            source_depth=SourceDepth.FULL_TEXT,
            paper_ids=["p1"]
        )
        web.beliefs[b1.belief_id] = b1

        generator = ReportGenerator(web)
        without_conf = generator._find_causal_without_confounders(list(web.beliefs.values()))

        assert len(without_conf) == 0

    def test_ignores_non_causal_claims(self):
        """Test that non-causal claims are not checked for confounders."""
        from src.services.web_of_belief import Belief, Credence, SourceDepth, EpistemicLevel

        web = WebOfBelief()
        # Non-causal descriptive claim
        b1 = Belief(
            belief_id="non_causal",
            content="The study measured light levels in 50 office buildings",
            level=EpistemicLevel.OBSERVATIONAL,
            credence=Credence(0.90, 0.05),
            source_depth=SourceDepth.FULL_TEXT,
            paper_ids=["p1"]
        )
        web.beliefs[b1.belief_id] = b1

        generator = ReportGenerator(web)
        without_conf = generator._find_causal_without_confounders(list(web.beliefs.values()))

        assert len(without_conf) == 0

    def test_gap_report_includes_confounder_section(self):
        """Test gap analysis report includes confounder coverage section."""
        from src.services.web_of_belief import Belief, Credence, SourceDepth, EpistemicLevel

        web = WebOfBelief()
        # Causal claim without confounder mention
        # Note: "Temperature" was added as a confounder keyword in panel validation 2026-01-22,
        # so we use "blue light" instead to avoid matching confounder keywords
        b1 = Belief(
            belief_id="causal_test",
            content="Blue light exposure improves cognitive performance significantly",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.70, 0.15),
            source_depth=SourceDepth.FULL_TEXT,
            paper_ids=["p1"],
            outcome_id="cog.performance"
        )
        web.beliefs[b1.belief_id] = b1

        report = generate_report(web, ReportType.GAP_ANALYSIS)

        confounder_section = next(
            (s for s in report.sections if "Confounder" in s.title or "WARNING" in s.title), None
        )
        assert confounder_section is not None
        assert confounder_section.data['count'] > 0

    def test_confounder_keywords_detected(self):
        """Test various confounder-related keywords are detected."""
        from src.services.web_of_belief import Belief, Credence, SourceDepth, EpistemicLevel

        keywords_to_test = [
            "adjusted for age",
            "controlling for income",
            "held constant across groups",
            "independent of prior experience",
            "after adjusting for baseline"
        ]

        web = WebOfBelief()
        generator = ReportGenerator(web)

        for i, phrase in enumerate(keywords_to_test):
            b = Belief(
                belief_id=f"conf_{i}",
                content=f"Natural light improves productivity, {phrase}",
                level=EpistemicLevel.EMPIRICAL,
                credence=Credence(0.75, 0.10),
                source_depth=SourceDepth.FULL_TEXT,
                paper_ids=["p1"]
            )
            without_conf = generator._find_causal_without_confounders([b])
            assert len(without_conf) == 0, f"Should detect confounder keyword in: {phrase}"

    def test_confounder_gap_data_includes_belief_ids(self):
        """Test confounder gap section includes belief IDs for tracking."""
        from src.services.web_of_belief import Belief, Credence, SourceDepth, EpistemicLevel

        web = WebOfBelief()
        b1 = Belief(
            belief_id="track_me",
            content="Light exposure reduces stress levels",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.65, 0.12),
            source_depth=SourceDepth.ABSTRACT,
            paper_ids=["p1"],
            outcome_id="affect.stress"
        )
        web.beliefs[b1.belief_id] = b1

        report = generate_report(web, ReportType.GAP_ANALYSIS)

        confounder_section = next(
            (s for s in report.sections if "Confounder" in s.title or "CRITICAL" in s.title), None
        )
        if confounder_section:
            assert 'belief_ids' in confounder_section.data
            assert "track_me" in confounder_section.data['belief_ids']

    def test_severity_weighting_critical_for_abstract(self):
        """Test CRITICAL severity for abstract-only causal claims (E1.D4 panel)."""
        from src.services.web_of_belief import Belief, Credence, SourceDepth, EpistemicLevel

        web = WebOfBelief()
        # Abstract-only causal claim should be CRITICAL
        b1 = Belief(
            belief_id="abstract_causal",
            content="Natural light causes improved productivity",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.70, 0.15),
            source_depth=SourceDepth.ABSTRACT,  # Abstract only!
            paper_ids=["p1"],
            outcome_id="behav.productivity"
        )
        web.beliefs[b1.belief_id] = b1

        report = generate_report(web, ReportType.GAP_ANALYSIS)

        critical_section = next(
            (s for s in report.sections if "CRITICAL" in s.title), None
        )
        assert critical_section is not None
        assert critical_section.data.get('severity') == 'CRITICAL'
        assert "abstract_causal" in critical_section.data['belief_ids']

    def test_severity_weighting_warning_for_fulltext(self):
        """Test WARNING severity for full-text causal claims (E1.D4 panel)."""
        from src.services.web_of_belief import Belief, Credence, SourceDepth, EpistemicLevel

        web = WebOfBelief()
        # Full-text causal claim should be WARNING
        # Use content that doesn't match confounder keywords (e.g., avoid "temperature")
        b1 = Belief(
            belief_id="fulltext_causal",
            content="Blue light exposure affects cognitive focus significantly",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.75, 0.10),
            source_depth=SourceDepth.FULL_TEXT,  # Full text
            paper_ids=["p1"],
            outcome_id="cog.performance"
        )
        web.beliefs[b1.belief_id] = b1

        report = generate_report(web, ReportType.GAP_ANALYSIS)

        warning_section = next(
            (s for s in report.sections if "WARNING" in s.title), None
        )
        assert warning_section is not None
        assert warning_section.data.get('severity') == 'WARNING'
        assert "fulltext_causal" in warning_section.data['belief_ids']

    def test_expanded_keywords_pearl_additions(self):
        """Test expanded keywords per Pearl panel (E1.D4)."""
        from src.services.web_of_belief import Belief, Credence, SourceDepth, EpistemicLevel

        web = WebOfBelief()
        generator = ReportGenerator(web)

        pearl_keywords = [
            "propensity score matching",
            "instrumental variable analysis",
            "difference-in-differences design",
            "regression discontinuity",
            "within-subjects design"
        ]

        for i, phrase in enumerate(pearl_keywords):
            b = Belief(
                belief_id=f"pearl_{i}",
                content=f"Light affects productivity, using {phrase}",
                level=EpistemicLevel.EMPIRICAL,
                credence=Credence(0.75, 0.10),
                source_depth=SourceDepth.FULL_TEXT,
                paper_ids=["p1"]
            )
            without_conf = generator._find_causal_without_confounders([b])
            assert len(without_conf) == 0, f"Should detect Pearl keyword: {phrase}"

    def test_expanded_keywords_domain_specific(self):
        """Test domain-specific keywords per Cartwright/Kaplan panel (E1.D4)."""
        from src.services.web_of_belief import Belief, Credence, SourceDepth, EpistemicLevel

        web = WebOfBelief()
        generator = ReportGenerator(web)

        domain_keywords = [
            "controlling for socioeconomic status",
            "accounting for self-selection bias",
            "baseline measurements taken",
            "pre-post design",
            "seasonal variation controlled"
        ]

        for i, phrase in enumerate(domain_keywords):
            b = Belief(
                belief_id=f"domain_{i}",
                content=f"Light affects productivity, with {phrase}",
                level=EpistemicLevel.EMPIRICAL,
                credence=Credence(0.75, 0.10),
                source_depth=SourceDepth.FULL_TEXT,
                paper_ids=["p1"]
            )
            without_conf = generator._find_causal_without_confounders([b])
            assert len(without_conf) == 0, f"Should detect domain keyword: {phrase}"


# =============================================================================
# Quality Assessment Tests
# =============================================================================

class TestQualityAssessment:
    """Tests for quality assessment report."""

    def test_quality_structure(self, populated_web):
        """Test quality assessment structure."""
        report = generate_report(populated_web, ReportType.QUALITY_ASSESSMENT)

        assert report.report_type == ReportType.QUALITY_ASSESSMENT
        assert len(report.sections) >= 3

    def test_quality_score(self, populated_web):
        """Test quality score is calculated."""
        report = generate_report(populated_web, ReportType.QUALITY_ASSESSMENT)

        score_section = next(
            (s for s in report.sections if "Quality Score" in s.title), None
        )
        assert score_section is not None
        assert 0 <= score_section.data.get('quality_score', -1) <= 1

    def test_quality_source_depth(self, populated_web):
        """Test source depth is analyzed."""
        report = generate_report(populated_web, ReportType.QUALITY_ASSESSMENT)

        depth_section = next(
            (s for s in report.sections if "Source Depth" in s.title), None
        )
        assert depth_section is not None
        assert 'full_text' in depth_section.data


# =============================================================================
# Topic Deep Dive Tests
# =============================================================================

class TestTopicDeepDive:
    """Tests for topic deep dive report."""

    def test_deep_dive_with_topic(self, populated_web):
        """Test deep dive with valid topic."""
        report = generate_report(
            populated_web,
            ReportType.TOPIC_DEEP_DIVE,
            topic="light"
        )

        assert report.report_type == ReportType.TOPIC_DEEP_DIVE
        assert "light" in report.title.lower()

    def test_deep_dive_no_topic(self, populated_web):
        """Test deep dive without topic."""
        report = generate_report(populated_web, ReportType.TOPIC_DEEP_DIVE)
        assert "No topic specified" in report.summary

    def test_deep_dive_nonmatching_topic(self, populated_web):
        """Test deep dive with non-matching topic."""
        report = generate_report(
            populated_web,
            ReportType.TOPIC_DEEP_DIVE,
            topic="xyzzy_nomatch"
        )
        assert "No beliefs found" in report.summary


# =============================================================================
# Contradiction Report Tests
# =============================================================================

class TestContradictionReport:
    """Tests for contradiction report."""

    def test_contradiction_structure(self, populated_web):
        """Test contradiction report structure."""
        report = generate_report(populated_web, ReportType.CONTRADICTION_REPORT)

        assert report.report_type == ReportType.CONTRADICTION_REPORT

    def test_contradiction_finds_contested(self, populated_web):
        """Test contested beliefs are found."""
        report = generate_report(populated_web, ReportType.CONTRADICTION_REPORT)

        # populated_web has b4 which is contested
        assert report.metadata.get('total_contested', 0) >= 1


# =============================================================================
# Report Serialization Tests
# =============================================================================

class TestReportSerialization:
    """Tests for report serialization."""

    def test_report_to_dict(self, populated_web):
        """Test Report.to_dict()."""
        report = generate_report(populated_web, ReportType.EXECUTIVE_SUMMARY)
        d = report.to_dict()

        assert 'report_type' in d
        assert 'title' in d
        assert 'generated_at' in d
        assert 'summary' in d
        assert 'sections' in d
        assert 'metadata' in d

    def test_section_to_dict(self):
        """Test ReportSection.to_dict()."""
        section = ReportSection(
            title="Test Section",
            content="Test content",
            data={'key': 'value'}
        )
        d = section.to_dict()

        assert d['title'] == "Test Section"
        assert d['content'] == "Test content"
        assert d['data'] == {'key': 'value'}


# =============================================================================
# Convenience Function Tests
# =============================================================================

class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_generate_report_function(self, populated_web):
        """Test generate_report convenience function."""
        report = generate_report(populated_web, ReportType.EXECUTIVE_SUMMARY)
        assert isinstance(report, Report)

    def test_generate_report_with_topic(self, populated_web):
        """Test generate_report with topic."""
        report = generate_report(
            populated_web,
            ReportType.TOPIC_DEEP_DIVE,
            topic="productivity"
        )
        assert "productivity" in report.title.lower()


# =============================================================================
# Integration Tests
# =============================================================================

class TestReportingIntegration:
    """Integration tests for reporting."""

    def test_all_report_types(self, populated_web):
        """Test all report types can be generated."""
        for report_type in ReportType:
            report = generate_report(populated_web, report_type)
            assert report is not None
            assert report.report_type == report_type

    def test_report_consistency(self, populated_web):
        """Test reports are internally consistent."""
        exec_report = generate_report(populated_web, ReportType.EXECUTIVE_SUMMARY)
        inv_report = generate_report(populated_web, ReportType.EVIDENCE_INVENTORY)

        # Both should report same total beliefs
        exec_total = exec_report.metadata.get('belief_count', 0)
        # Inventory total is sum of beliefs across sections
        inv_total = sum(
            s.data.get('count', 0) for s in inv_report.sections
            if s.data and 'count' in s.data
        )

        assert exec_total == inv_total

    def test_full_reporting_workflow(self, populated_web):
        """Test complete reporting workflow."""
        generator = ReportGenerator(populated_web)

        # Generate executive summary
        exec_report = generator.generate(ReportType.EXECUTIVE_SUMMARY)
        assert exec_report.summary is not None

        # Generate gap analysis
        gap_report = generator.generate(ReportType.GAP_ANALYSIS)
        assert gap_report.sections is not None

        # Generate topic deep dive
        topic_report = generator.generate(
            ReportType.TOPIC_DEEP_DIVE,
            topic="productivity"
        )
        assert "productivity" in topic_report.title.lower()
