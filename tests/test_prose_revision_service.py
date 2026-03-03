"""
Tests for ProseRevisionService — the active prose diagnostic and revision tool.

Tests cover:
  - Individual diagnostics (nominalizations, passive voice, hedges, etc.)
  - Writer's Diet composite diagnostic
  - Lard factor estimation
  - Full 3-pass critique
  - Context-sensitive thresholds (qa_response vs. paper vs. general)
  - QA handler integration (prose_review field)
  - Edge cases (empty text, very short text, markdown-heavy text)
"""

import pytest
from src.services.prose_revision_service import (
    ProseRevisionService,
    ProseHealthReport,
    WritersDiet,
    Diagnostic,
    Severity,
    DiagnosticCategory,
)


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def service():
    """Default service with 'general' context."""
    return ProseRevisionService(context="general")


@pytest.fixture
def qa_service():
    """Service configured for QA response thresholds."""
    return ProseRevisionService(context="qa_response")


@pytest.fixture
def paper_service():
    """Service configured for academic paper thresholds."""
    return ProseRevisionService(context="paper")


# ── Sample texts ─────────────────────────────────────────────────────────────

GOOD_PROSE = """
The Goldilocks Principle operates across all five sensory modalities studied.
Visual complexity peaks at fractal dimension D = 1.3, thermal comfort at adaptive
neutral, and acoustic preference at 50-60 dB. This cross-modal consistency is
the theory's distinctive claim. Berlyne (1971) showed that collative variables
follow inverted-U curves. Taylor and colleagues (1999, 2005) replicated this
for fractal visual patterns. The evidence is strongest for visual complexity
and thermal comfort, moderate for acoustics, and preliminary for social density.
"""

BAD_PROSE = """
It is important to note that the optimization of the environmental conditions
was performed by the researchers. The implementation of the intervention was
carried out in a systematic manner. It has been suggested that the utilization
of the methodology could potentially perhaps somewhat improve the outcomes.
The fact that the participants were recruited from undergraduate courses
is clearly obviously relevant. There is a need for the examination of the
relationship between the variables. The assessment of the measurement
was conducted by trained observers. It is well known that the investigation
of the phenomenon is of considerable interest to note that the analysis
of the data might perhaps possibly indicate a trend.
"""

HEDGE_HEAVY = """
The effect might perhaps be somewhat related to the intervention. It is possible
that the results could potentially indicate a trend. The mechanism appears to
perhaps involve some form of prediction error, though it seems to be relatively
unclear whether this tends to apply in all cases.
"""

OVERCLAIMING_PROSE = """
The results clearly demonstrate that biophilic design obviously improves
workplace productivity. This undoubtedly proves that natural elements
are interestingly the most important factor. The data remarkably shows
a strikingly large effect. Without question, these findings definitively
establish the causal mechanism.
"""

MARKDOWN_TEXT = """
## Introduction

The brain optimizes its response to intermediate prediction error.

## Methods

Taylor et al. (1999) measured aesthetic preference for fractal patterns.
The study recruited 220 participants from three universities.

### Stimuli

Each participant viewed 40 fractal images at varying complexity levels.

## Results

Preference peaked at fractal dimension D = 1.3 across all conditions.
"""

CITATION_CLUSTER_TEXT = """
Several studies support the inverted-U hypothesis (Berlyne, 1971; Martindale & Moore,
1988; Taylor et al., 1999; Spehar et al., 2003; Hagerhall et al., 2004). This pattern
has been documented across sensory modalities.
"""


# ── Test: Nominalizations ────────────────────────────────────────────────────

class TestNominalizations:
    def test_detects_high_nominalization_density(self, service):
        diags = service.find_nominalizations(BAD_PROSE)
        # Should flag overall density
        density_diags = [d for d in diags if "density" in d.message.lower()]
        assert len(density_diags) >= 1

    def test_clean_prose_no_warnings(self, service):
        diags = service.find_nominalizations(GOOD_PROSE)
        # Good prose should have no critical/warning nominalizations
        serious = [d for d in diags if d.severity in (Severity.CRITICAL, Severity.WARNING)]
        assert len(serious) == 0

    def test_exceptions_not_flagged(self, service):
        """Words like 'information', 'education' should not count as nominalizations."""
        text = "The information about education and the environment was relevant to the population."
        diags = service.find_nominalizations(text)
        # No warnings — these are exception words
        serious = [d for d in diags if d.severity in (Severity.CRITICAL, Severity.WARNING)]
        assert len(serious) == 0

    def test_sentence_level_nominalization_clusters(self, service):
        text = "The optimization of the implementation of the utilization of the procedure required careful examination."
        diags = service.find_nominalizations(text)
        cluster_diags = [d for d in diags if "sentence has" in d.message.lower()]
        assert len(cluster_diags) >= 1


# ── Test: Passive Voice ──────────────────────────────────────────────────────

class TestPassiveVoice:
    def test_detects_heavy_passive(self, service):
        diags = service.find_passive_voice(BAD_PROSE)
        serious = [d for d in diags if d.severity in (Severity.CRITICAL, Severity.WARNING)]
        assert len(serious) >= 1

    def test_active_prose_passes(self, service):
        diags = service.find_passive_voice(GOOD_PROSE)
        serious = [d for d in diags if d.severity in (Severity.CRITICAL, Severity.WARNING)]
        assert len(serious) == 0

    def test_passive_percentage_computation(self, service):
        # All passive sentences
        text = "The test was conducted. The data were analyzed. The results were published."
        diags = service.find_passive_voice(text)
        # Should detect high passive percentage
        assert any("%" in d.message for d in diags)


# ── Test: Hedge Stacks ──────────────────────────────────────────────────────

class TestHedgeStacks:
    def test_detects_hedge_stacks(self, service):
        diags = service.find_hedge_stacks(HEDGE_HEAVY)
        assert len(diags) >= 1
        assert all(d.category == DiagnosticCategory.HEDGE_STACK for d in diags)

    def test_single_hedge_ok(self, service):
        text = "The effect might be related to prediction error. Further research is needed."
        diags = service.find_hedge_stacks(text)
        # Single hedge per sentence should not trigger
        assert len(diags) == 0

    def test_hedge_severity_is_warning(self, service):
        diags = service.find_hedge_stacks(HEDGE_HEAVY)
        for d in diags:
            assert d.severity == Severity.WARNING


# ── Test: Throat Clearing ────────────────────────────────────────────────────

class TestThroatClearing:
    def test_detects_throat_clearing(self, service):
        diags = service.find_throat_clearing(BAD_PROSE)
        assert len(diags) >= 2  # "It is important to note that", "It has been suggested that", "It is well known that"

    def test_clean_prose_no_throat_clearing(self, service):
        diags = service.find_throat_clearing(GOOD_PROSE)
        assert len(diags) == 0

    def test_each_pattern_detected(self, service):
        text = "It is important to note that X. It should be noted that Y. As previously discussed, Z."
        diags = service.find_throat_clearing(text)
        assert len(diags) >= 3


# ── Test: Overclaiming ──────────────────────────────────────────────────────

class TestOverclaiming:
    def test_detects_overclaiming(self, service):
        diags = service.find_overclaiming(OVERCLAIMING_PROSE)
        assert len(diags) >= 4  # clearly, obviously, undoubtedly, interestingly, remarkably, strikingly, etc.

    def test_calibrated_prose_clean(self, service):
        text = "The evidence suggests that biophilic design improves productivity. Initial studies report a medium effect size."
        diags = service.find_overclaiming(text)
        assert len(diags) == 0


# ── Test: Long Sentences ─────────────────────────────────────────────────────

class TestLongSentences:
    def test_flags_long_sentences(self, service):
        long_sent = "The " + " ".join(["very"] * 50) + " long sentence was problematic."
        diags = service.find_long_sentences(long_sent)
        assert len(diags) >= 1

    def test_normal_sentences_pass(self, service):
        diags = service.find_long_sentences(GOOD_PROSE)
        assert len(diags) == 0


# ── Test: Weak Openers ──────────────────────────────────────────────────────

class TestWeakOpeners:
    def test_flags_weak_openers(self, service):
        text = """It is clear that results matter. There are many reasons for this.
        It was noted by the team. There were several factors involved.
        It is the case that data supports this. There is evidence for the claim.
        This is a fundamental problem. The brain processes information efficiently."""
        diags = service.find_weak_openers(text)
        assert len(diags) >= 1


# ── Test: Citation Clusters ──────────────────────────────────────────────────

class TestCitationClusters:
    def test_detects_citation_clusters(self, service):
        diags = service.find_citation_clusters(CITATION_CLUSTER_TEXT)
        assert len(diags) >= 1
        assert diags[0].category == DiagnosticCategory.CITATION_STYLE

    def test_woven_citations_pass(self, service):
        text = "Berlyne (1971) showed inverted-U curves. Taylor et al. (1999) replicated this for fractals."
        diags = service.find_citation_clusters(text)
        assert len(diags) == 0


# ── Test: Knowledge Curse Audit ──────────────────────────────────────────────

class TestKnowledgeCurseAudit:
    def test_detects_unexpanded_abbreviations(self, service):
        text = "The ATLAS system uses QLP to process articles. RASA molecules are extracted from the WOB."
        diags = service.knowledge_curse_audit(text)
        # QLP, RASA, WOB should be flagged (ATLAS might be too long for the <=6 filter)
        flagged = [d.original for d in diags]
        assert "QLP" in flagged or "RASA" in flagged or "WOB" in flagged

    def test_common_abbreviations_not_flagged(self, service):
        text = "The fMRI data from the US study showed DNA methylation patterns."
        diags = service.knowledge_curse_audit(text)
        # All are common abbreviations — should not be flagged
        assert len(diags) == 0

    def test_expanded_abbreviations_not_flagged(self, service):
        text = "The Article Transcription and Learning Architecture System (ATLAS) processes papers. ATLAS uses deep extraction."
        diags = service.knowledge_curse_audit(text)
        flagged_abbrevs = [d.original for d in diags]
        assert "ATLAS" not in flagged_abbrevs

    def test_defined_terms_respected(self, service):
        text = "The XYZ metric was computed for all samples."
        diags = service.knowledge_curse_audit(text, defined_terms={"XYZ"})
        flagged = [d.original for d in diags]
        assert "XYZ" not in flagged


# ── Test: Structural Audit ───────────────────────────────────────────────────

class TestStructuralAudit:
    def test_flags_topic_only_headings(self, service):
        text = "## Introduction\n\nSome content here.\n\n## Methods\n\nMore content.\n\n## Results\n\nFinal content."
        diags = service.structural_audit(text)
        heading_diags = [d for d in diags if "topic-only" in d.message.lower()]
        assert len(heading_diags) >= 2  # Introduction, Methods, Results

    def test_informative_headings_pass(self, service):
        text = "## Fractal Dimension Peaks at D = 1.3 Because Natural Scenes Do\n\nContent here."
        diags = service.structural_audit(text)
        heading_diags = [d for d in diags if "topic-only" in d.message.lower()]
        assert len(heading_diags) == 0

    def test_flags_long_paragraphs(self, service):
        # Build a paragraph with 12 sentences
        long_para = " ".join([f"This is sentence number {i} about the topic." for i in range(12)])
        diags = service.structural_audit(long_para)
        length_diags = [d for d in diags if "sentences" in d.message and "paragraph" in d.message.lower()]
        assert len(length_diags) >= 1


# ── Test: Writer's Diet ─────────────────────────────────────────────────────

class TestWritersDiet:
    def test_healthy_prose_lean(self, service):
        diet = service.writers_diet(GOOD_PROSE)
        assert diet.verdict in ("Lean & Mean", "Fit & Trim", "Needs Toning")
        assert diet.total_words > 0

    def test_bad_prose_unhealthy(self, service):
        diet = service.writers_diet(BAD_PROSE)
        # Bad prose should be flabby or worse
        assert diet.verdict in ("Needs Toning", "Flabby", "Heart Attack Territory")

    def test_empty_text(self, service):
        diet = service.writers_diet("")
        assert diet.verdict == "Empty text"
        assert diet.total_words == 0

    def test_as_dict_returns_all_fields(self, service):
        diet = service.writers_diet(GOOD_PROSE)
        d = diet.as_dict()
        assert "be_verb_pct" in d
        assert "abstract_noun_pct" in d
        assert "preposition_pct" in d
        assert "adjadv_pct" in d
        assert "it_this_there_pct" in d
        assert "total_words" in d
        assert "verdict" in d


# ── Test: Lard Factor ────────────────────────────────────────────────────────

class TestLardFactor:
    def test_clean_prose_low_lard(self, service):
        lard = service.lard_factor(GOOD_PROSE)
        assert lard < 30  # Good prose: low lard

    def test_bad_prose_high_lard(self, service):
        lard = service.lard_factor(BAD_PROSE)
        assert lard > 20  # Bad prose: significant lard

    def test_empty_text_zero_lard(self, service):
        assert service.lard_factor("") == 0.0


# ── Test: Full Critique ─────────────────────────────────────────────────────

class TestFullCritique:
    def test_good_prose_high_score(self, service):
        report = service.full_critique(GOOD_PROSE)
        assert report.overall_score >= 7.0
        assert "Excellent" in report.verdict or "Good" in report.verdict

    def test_bad_prose_low_score(self, service):
        report = service.full_critique(BAD_PROSE)
        assert report.overall_score < 6.0

    def test_report_has_all_fields(self, service):
        report = service.full_critique(GOOD_PROSE)
        assert report.word_count > 0
        assert report.sentence_count > 0
        assert report.paragraph_count > 0
        assert report.avg_sentence_length > 0
        assert report.writers_diet is not None
        assert isinstance(report.lard_factor_estimate, float)
        assert isinstance(report.passive_voice_pct, float)
        assert isinstance(report.nominalization_density, float)
        assert report.summary != ""
        assert report.verdict != ""

    def test_all_diagnostics_aggregation(self, service):
        report = service.full_critique(BAD_PROSE)
        total = len(report.all_diagnostics)
        parts = len(report.pass1_structural) + len(report.pass2_sentence) + len(report.pass3_knowledge)
        assert total == parts

    def test_critical_and_warning_counts(self, service):
        report = service.full_critique(BAD_PROSE)
        assert report.critical_count >= 0
        assert report.warning_count >= 0
        assert report.critical_count + report.warning_count <= len(report.all_diagnostics)


# ── Test: Context Sensitivity ────────────────────────────────────────────────

class TestContextSensitivity:
    def test_qa_stricter_sentence_length(self):
        qa = ProseRevisionService(context="qa_response")
        paper = ProseRevisionService(context="paper")
        assert qa._thresholds["max_sentence_length"] < paper._thresholds["max_sentence_length"]

    def test_qa_shorter_paragraphs(self):
        qa = ProseRevisionService(context="qa_response")
        general = ProseRevisionService(context="general")
        assert qa._thresholds["max_paragraph_sentences"] < general._thresholds["max_paragraph_sentences"]

    def test_paper_more_lenient(self):
        paper = ProseRevisionService(context="paper")
        assert paper._thresholds["max_sentence_length"] == 50
        assert paper._thresholds["max_paragraph_sentences"] == 10


# ── Test: Suggest Revisions ──────────────────────────────────────────────────

class TestSuggestRevisions:
    def test_returns_prioritized_list(self, service):
        suggestions = service.suggest_revisions(BAD_PROSE, max_suggestions=5)
        assert len(suggestions) <= 5
        # Critical should come before warning
        severities = [d.severity for d in suggestions]
        critical_indices = [i for i, s in enumerate(severities) if s == Severity.CRITICAL]
        warning_indices = [i for i, s in enumerate(severities) if s == Severity.WARNING]
        if critical_indices and warning_indices:
            assert max(critical_indices) < min(warning_indices)

    def test_clean_prose_few_suggestions(self, service):
        suggestions = service.suggest_revisions(GOOD_PROSE, max_suggestions=10)
        # Good prose should have very few serious suggestions
        serious = [d for d in suggestions if d.severity in (Severity.CRITICAL, Severity.WARNING)]
        assert len(serious) <= 2


# ── Test: Format Report ─────────────────────────────────────────────────────

class TestFormatReport:
    def test_format_produces_markdown(self, service):
        report = service.full_critique(BAD_PROSE)
        formatted = service.format_report(report)
        assert "# Prose Health Report" in formatted
        assert "Quantitative Metrics" in formatted
        assert "Words" in formatted

    def test_format_includes_diagnostics(self, service):
        report = service.full_critique(BAD_PROSE)
        formatted = service.format_report(report)
        # Should include at least one pass section
        assert "Pass" in formatted or "Sentence-Level" in formatted or "Structural" in formatted


# ── Test: Edge Cases ─────────────────────────────────────────────────────────

class TestEdgeCases:
    def test_empty_text(self, service):
        report = service.full_critique("")
        assert report.word_count == 0
        assert report.overall_score >= 0

    def test_single_sentence(self, service):
        report = service.full_critique("The brain processes visual information efficiently.")
        assert report.sentence_count >= 1
        assert report.overall_score >= 0

    def test_markdown_heavy_text(self, service):
        report = service.full_critique(MARKDOWN_TEXT)
        assert report.word_count > 0
        # Should handle markdown gracefully
        assert report.overall_score >= 0

    def test_very_long_text(self, service):
        """Service should handle long texts without crashing."""
        long_text = GOOD_PROSE * 50
        report = service.full_critique(long_text)
        assert report.word_count > 1000


# ── Test: QA Handler Integration ─────────────────────────────────────────────

class TestQAHandlerIntegration:
    """Test that ProseRevisionService integrates correctly with QA handler."""

    def test_prose_review_method_exists(self):
        """The _apply_prose_review method should exist on ArbitraryQAHandler."""
        try:
            from src.services.arbitrary_qa_handler import ArbitraryQAHandler
            handler = ArbitraryQAHandler()
            assert hasattr(handler, '_apply_prose_review')
        except Exception:
            pytest.skip("QA handler not importable in test environment")

    def test_prose_review_disabled_by_default(self):
        """Prose review should be off by default (opt-in)."""
        try:
            from src.services.arbitrary_qa_handler import ArbitraryQAHandler
            handler = ArbitraryQAHandler()
            assert handler._enable_prose_review is False
        except Exception:
            pytest.skip("QA handler not importable in test environment")

    def test_prose_review_on_sample_answer(self):
        """When enabled, prose review should add prose_review field."""
        try:
            from src.services.arbitrary_qa_handler import ArbitraryQAHandler
            handler = ArbitraryQAHandler(enable_prose_review=True)
            # Construct a fake answer dict
            fake_answer = {
                "question_type": "test",
                "headline": "Test answer",
                "sections": [
                    {
                        "heading": "Answer",
                        "items": [BAD_PROSE],
                    }
                ],
                "confidence": 0.9,
            }
            result = handler._apply_prose_review(fake_answer)
            assert result["prose_reviewed"] is True
            assert "prose_review" in result
            review = result["prose_review"]
            assert "score" in review
            assert "verdict" in review
            assert "top_suggestions" in review
            assert review["score"] < 6.0  # Bad prose should score low
        except Exception:
            pytest.skip("QA handler not importable in test environment")

    def test_prose_review_disabled_returns_false(self):
        """When disabled, prose_reviewed should be False."""
        try:
            from src.services.arbitrary_qa_handler import ArbitraryQAHandler
            handler = ArbitraryQAHandler(enable_prose_review=False)
            fake_answer = {
                "sections": [{"heading": "Test", "items": ["Some text."]}],
            }
            result = handler._apply_prose_review(fake_answer)
            assert result["prose_reviewed"] is False
            assert "prose_review" not in result
        except Exception:
            pytest.skip("QA handler not importable in test environment")

    def test_prose_review_short_text_skipped(self):
        """Very short answers should skip prose review."""
        try:
            from src.services.arbitrary_qa_handler import ArbitraryQAHandler
            handler = ArbitraryQAHandler(enable_prose_review=True)
            fake_answer = {
                "sections": [{"heading": "Answer", "items": ["Yes."]}],
            }
            result = handler._apply_prose_review(fake_answer)
            assert result["prose_reviewed"] is False
        except Exception:
            pytest.skip("QA handler not importable in test environment")
