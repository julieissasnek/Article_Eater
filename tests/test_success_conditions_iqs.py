"""
Layer 1 Success Condition Tests — IntegratedQueryService
=========================================================

Tests derived from SC-* success conditions in integrated_query_service.py.
Each test validates one explicit promise from a function docstring.

Sprint SC-2 | 2026-03-03
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from dataclasses import asdict

from src.services.integrated_query_service import (
    ArticleEvidence,
    PanelComment,
    IntegratedResponse,
    IntegratedQueryService,
    T1Framework,
    FRAMEWORK_VOICES,
)
from src.services.template_query_service import (
    QueryResponse, TemplateAnswer, CausalPathway, UserPersona,
)


# =============================================================================
# HELPERS
# =============================================================================

def _make_causal_pathway(**overrides):
    defaults = dict(
        from_entity="noise",
        activity="increases",
        to_entity="stress",
        change_produced="elevated cortisol",
        level="environmental",
        bridging_to="cognitive load",
        bridging_quality="moderate",
        maturity="established",
        evidence_base="Smith 2020",
    )
    defaults.update(overrides)
    return CausalPathway(**defaults)


def _make_template_answer(**overrides):
    defaults = dict(
        template_id="t_001",
        display_id="NCA-001",
        name="Noise and Cognitive Load",
        relevance_score=0.8,
        how=[_make_causal_pathway()],
        why="Noise increases cognitive load via auditory masking",
        when=["open plan offices", "above 55 dB"],
        for_whom=["introverts more affected"],
        maturity="established",
        key_references=["Smith 2020"],
        confidence=0.75,
    )
    defaults.update(overrides)
    return TemplateAnswer(**defaults)


def _make_query_response(**overrides):
    defaults = dict(
        query="How does noise affect cognition?",
        headline="Noise impairs cognition via masking",
        how="Auditory masking reduces available working memory",
        why="Cognitive load theory",
        when=["open plan offices"],
        for_whom=["introverts"],
        relevant_templates=[_make_template_answer()],
        causal_chain="noise → masking → WM load → impaired cognition",
        overall_confidence=0.70,
        maturity_distribution={"established": 1},
        key_evidence=["Smith 2020"],
    )
    defaults.update(overrides)
    return QueryResponse(**defaults)


def _make_article_evidence(**overrides):
    defaults = dict(
        belief_id="b_001",
        content="Noise above 55 dB impairs working memory",
        paper_ids=["paper_123"],
        credence=0.7,
        credence_uncertainty=0.15,
        level="empirical",
        status="active",
        relevance_score=0.6,
    )
    defaults.update(overrides)
    return ArticleEvidence(**defaults)


def _make_panel_comment(**overrides):
    defaults = dict(
        framework=T1Framework.PP,
        framework_name="Predictive Processing",
        perspective="From a predictive processing view, noise is prediction error",
        complications=["PE magnitude depends on prior precision"],
        speculation="I suspect precision-weighting mediates this",
        limitations=["PP doesn't specify WHICH predictions are active"],
        key_question="What prediction is being violated here?",
    )
    defaults.update(overrides)
    return PanelComment(**defaults)


def _make_integrated_response(**overrides):
    defaults = dict(
        template_response=_make_query_response(),
        article_evidence=[_make_article_evidence()],
        total_supporting_papers=1,
        evidence_quality_summary="Limited evidence: 1 paper(s) found",
        bn_posterior=None,
        bn_prior=None,
        bn_likelihood_ratio=None,
        panel_comments=[_make_panel_comment()],
        panel_synthesis="The panel agrees this is real",
        panel_debates=["Is this perceptual or embodied?"],
        open_questions=["What is the threshold?"],
    )
    defaults.update(overrides)
    return IntegratedResponse(**defaults)


def _make_iqs_no_embeddings():
    """Create IQS with mocked template service and no embeddings."""
    with patch("src.services.integrated_query_service.IntegratedQueryService._init_embeddings"):
        with patch("src.services.integrated_query_service.TemplateQueryService") as mock_tqs:
            mock_service = MagicMock()
            mock_service.templates = {
                "NCA-001": {
                    "display_id": "NCA-001",
                    "name": "Noise and Cognitive Load",
                    "structural_pattern": "masking",
                    "higher_order_principle": "cognitive load",
                    "short_description": "Noise impairs cognition",
                    "framework_ids": ["predictive_processing"],
                }
            }
            mock_service.query.return_value = _make_query_response()
            mock_tqs.return_value = mock_service

            iqs = IntegratedQueryService(use_embeddings=False)
            iqs.template_service = mock_service
            iqs.templates = mock_service.templates
            return iqs


# =============================================================================
# SC-AE: ArticleEvidence dataclass
# =============================================================================

class TestSC_AE_ArticleEvidence:
    """Tests for ArticleEvidence success conditions."""

    def test_sc_ae_1_belief_id_nonempty(self):
        """SC-AE-1: belief_id is a non-empty string."""
        ae = _make_article_evidence()
        assert isinstance(ae.belief_id, str)
        assert len(ae.belief_id) > 0

    def test_sc_ae_3_paper_ids_is_list(self):
        """SC-AE-3: paper_ids is always a list."""
        ae = _make_article_evidence()
        assert isinstance(ae.paper_ids, list)

    def test_sc_ae_4_credence_in_range(self):
        """SC-AE-4: credence is a float in [0.0, 1.0]."""
        ae = _make_article_evidence(credence=0.7)
        assert 0.0 <= ae.credence <= 1.0

    def test_sc_ae_5_uncertainty_nonneg(self):
        """SC-AE-5: credence_uncertainty >= 0."""
        ae = _make_article_evidence(credence_uncertainty=0.15)
        assert ae.credence_uncertainty >= 0.0

    def test_sc_ae_8_relevance_in_range(self):
        """SC-AE-8: relevance_score is a float in [0.0, 1.0]."""
        ae = _make_article_evidence(relevance_score=0.6)
        assert 0.0 <= ae.relevance_score <= 1.0


# =============================================================================
# SC-PC: PanelComment dataclass
# =============================================================================

class TestSC_PC_PanelComment:
    """Tests for PanelComment success conditions."""

    def test_sc_pc_1_framework_is_enum(self):
        """SC-PC-1: framework is a valid T1Framework enum member."""
        pc = _make_panel_comment()
        assert isinstance(pc.framework, T1Framework)

    def test_sc_pc_2_framework_name_nonempty(self):
        """SC-PC-2: framework_name is a non-empty string."""
        pc = _make_panel_comment()
        assert isinstance(pc.framework_name, str) and len(pc.framework_name) > 0

    def test_sc_pc_3_perspective_nonempty(self):
        """SC-PC-3: perspective is non-empty."""
        pc = _make_panel_comment()
        assert len(pc.perspective) > 0

    def test_sc_pc_4_complications_is_list(self):
        """SC-PC-4: complications is a list of strings."""
        pc = _make_panel_comment()
        assert isinstance(pc.complications, list)
        for c in pc.complications:
            assert isinstance(c, str)

    def test_sc_pc_5_speculation_nonempty(self):
        """SC-PC-5: speculation is non-empty."""
        pc = _make_panel_comment()
        assert len(pc.speculation) > 0

    def test_sc_pc_7_key_question_nonempty(self):
        """SC-PC-7: key_question is non-empty."""
        pc = _make_panel_comment()
        assert len(pc.key_question) > 0


# =============================================================================
# SC-IR: IntegratedResponse dataclass
# =============================================================================

class TestSC_IR_IntegratedResponse:
    """Tests for IntegratedResponse success conditions."""

    def test_sc_ir_1_template_response_not_none(self):
        """SC-IR-1: template_response is always a valid QueryResponse."""
        ir = _make_integrated_response()
        assert ir.template_response is not None
        assert isinstance(ir.template_response, QueryResponse)

    def test_sc_ir_2_article_evidence_is_list(self):
        """SC-IR-2: article_evidence is always a list."""
        ir = _make_integrated_response()
        assert isinstance(ir.article_evidence, list)

    def test_sc_ir_3_total_papers_nonneg(self):
        """SC-IR-3: total_supporting_papers is int >= 0."""
        ir = _make_integrated_response()
        assert isinstance(ir.total_supporting_papers, int)
        assert ir.total_supporting_papers >= 0

    def test_sc_ir_4_evidence_summary_nonempty(self):
        """SC-IR-4: evidence_quality_summary is non-empty."""
        ir = _make_integrated_response()
        assert len(ir.evidence_quality_summary) > 0

    def test_sc_ir_5_panel_comments_is_list(self):
        """SC-IR-5: panel_comments is always a list."""
        ir = _make_integrated_response()
        assert isinstance(ir.panel_comments, list)

    def test_sc_ir_10_persona_none_by_default(self):
        """SC-IR-10: persona_enrichment is None when no persona specified."""
        ir = _make_integrated_response()
        assert ir.persona_enrichment is None


# =============================================================================
# SC-GTV: get_theoretical_voices()
# =============================================================================

class TestSC_GTV_GetTheoreticalVoices:
    """Tests for get_theoretical_voices success conditions."""

    def setup_method(self):
        self.iqs = _make_iqs_no_embeddings()

    def test_sc_gtv_1_returns_dict(self):
        """SC-GTV-1: Returns a dict."""
        result = self.iqs.get_theoretical_voices("noise and stress")
        assert isinstance(result, dict)

    def test_sc_gtv_2_respects_limit(self):
        """SC-GTV-2: len(result) <= limit."""
        result = self.iqs.get_theoretical_voices("noise", limit=2)
        assert len(result) <= 2

    def test_sc_gtv_3_keys_are_framework_names(self):
        """SC-GTV-3: Each key is a framework name string (static or corpus-grounded)."""
        result = self.iqs.get_theoretical_voices("noise", limit=4)
        # Accept names from FRAMEWORK_VOICES (static) or corpus-grounded mode
        # which may append suffixes like "Affect" to names
        static_names = {v["name"] for v in FRAMEWORK_VOICES.values()}
        for key in result:
            # Check exact match or prefix match (corpus-grounded may extend names)
            matches_static = key in static_names
            matches_prefix = any(key.startswith(n) for n in static_names)
            assert matches_static or matches_prefix, \
                f"Key '{key}' not in FRAMEWORK_VOICES names or extensions thereof"

    def test_sc_gtv_4_value_has_required_keys(self):
        """SC-GTV-4: Each value has required keys (static OR corpus-grounded schema)."""
        # Static mode keys:
        static_required = {"perspective", "key_figures", "core_claim", "complications", "key_question", "implications"}
        # Corpus-grounded mode keys (AG's materialized view path):
        corpus_required = {"perspective", "core_mechanism", "key_principle", "source"}
        result = self.iqs.get_theoretical_voices("noise", limit=2)
        for name, data in result.items():
            source = data.get("source", "templated")
            if source == "corpus_grounded":
                missing = corpus_required - set(data.keys())
            else:
                missing = static_required - set(data.keys())
            assert not missing, f"Framework '{name}' (source={source}) missing keys: {missing}"

    def test_sc_gtv_5_perspective_nonempty(self):
        """SC-GTV-5: Each perspective is non-empty."""
        result = self.iqs.get_theoretical_voices("noise", limit=4)
        for name, data in result.items():
            assert len(data["perspective"]) > 0, f"Empty perspective for {name}"

    def test_sc_gtv_6_implications_or_findings(self):
        """SC-GTV-6: Each voice has implications (static) or top_findings (corpus-grounded)."""
        result = self.iqs.get_theoretical_voices("noise", limit=4)
        for name, data in result.items():
            source = data.get("source", "templated")
            if source == "corpus_grounded":
                assert "top_findings" in data or "implications" in data, \
                    f"Corpus-grounded '{name}' has neither top_findings nor implications"
            else:
                assert isinstance(data.get("implications", []), list)

    def test_sc_gtv_7_empty_topic_graceful(self):
        """SC-GTV-7: Works with empty string topic."""
        result = self.iqs.get_theoretical_voices("", limit=2)
        assert isinstance(result, dict)
        assert len(result) > 0


# =============================================================================
# SC-GFP: _generate_framework_perspective()
# =============================================================================

class TestSC_GFP_GenerateFrameworkPerspective:
    """Tests for _generate_framework_perspective success conditions."""

    def setup_method(self):
        self.iqs = _make_iqs_no_embeddings()

    def test_sc_gfp_1_returns_nonempty(self):
        """SC-GFP-1: Returns non-empty string."""
        response = _make_query_response()
        voice = FRAMEWORK_VOICES[T1Framework.PP]
        result = self.iqs._generate_framework_perspective(T1Framework.PP, voice, response)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_sc_gfp_2_pp_has_specific_content(self):
        """SC-GFP-2: PP framework returns framework-specific content."""
        response = _make_query_response()
        voice = FRAMEWORK_VOICES[T1Framework.PP]
        result = self.iqs._generate_framework_perspective(T1Framework.PP, voice, response)
        assert "predictive processing" in result.lower()

    def test_sc_gfp_2_ec_has_specific_content(self):
        """SC-GFP-2: EC framework returns framework-specific content."""
        response = _make_query_response()
        voice = FRAMEWORK_VOICES[T1Framework.EC]
        result = self.iqs._generate_framework_perspective(T1Framework.EC, voice, response)
        assert "embodied" in result.lower()

    def test_sc_gfp_3_empty_templates_fallback(self):
        """SC-GFP-3: Returns fallback when no relevant_templates."""
        response = _make_query_response(relevant_templates=[])
        voice = FRAMEWORK_VOICES[T1Framework.PP]
        result = self.iqs._generate_framework_perspective(T1Framework.PP, voice, response)
        assert "Insufficient" in result

    def test_sc_gfp_4_unknown_framework_uses_core_claim(self):
        """SC-GFP-4: Unknown/fallback framework uses voice core_claim."""
        response = _make_query_response()
        voice = FRAMEWORK_VOICES[T1Framework.CB]  # Chronobiological — uses else branch
        result = self.iqs._generate_framework_perspective(T1Framework.CB, voice, response)
        assert len(result) > 0
        # Should contain the framework name
        assert "Chronobiological" in result


# =============================================================================
# SC-GS: _generate_speculation()
# =============================================================================

class TestSC_GS_GenerateSpeculation:
    """Tests for _generate_speculation success conditions."""

    def setup_method(self):
        self.iqs = _make_iqs_no_embeddings()

    def test_sc_gs_1_returns_nonempty(self):
        """SC-GS-1: Returns non-empty string."""
        response = _make_query_response()
        voice = FRAMEWORK_VOICES[T1Framework.PP]
        result = self.iqs._generate_speculation(T1Framework.PP, voice, response)
        assert isinstance(result, str) and len(result) > 0

    def test_sc_gs_2_contains_hedging(self):
        """SC-GS-2: Contains speculative language."""
        response = _make_query_response()
        voice = FRAMEWORK_VOICES[T1Framework.PP]
        result = self.iqs._generate_speculation(T1Framework.PP, voice, response)
        # Should contain hedging language like "suspect", "may", "would"
        hedge_words = ["suspect", "may", "would", "might", "could"]
        assert any(w in result.lower() for w in hedge_words), f"No hedging in: {result[:100]}"

    def test_sc_gs_3_fallback_uses_voice_name(self):
        """SC-GS-3: Fallback for unknown framework uses voice name."""
        response = _make_query_response()
        voice = FRAMEWORK_VOICES[T1Framework.CB]
        result = self.iqs._generate_speculation(T1Framework.CB, voice, response)
        assert "Chronobiological" in result


# =============================================================================
# SC-IFL: _identify_framework_limitations()
# =============================================================================

class TestSC_IFL_IdentifyLimitations:
    """Tests for _identify_framework_limitations success conditions."""

    def setup_method(self):
        self.iqs = _make_iqs_no_embeddings()

    def test_sc_ifl_1_returns_list(self):
        """SC-IFL-1: Returns a list."""
        response = _make_query_response()
        voice = FRAMEWORK_VOICES[T1Framework.PP]
        result = self.iqs._identify_framework_limitations(T1Framework.PP, voice, response)
        assert isinstance(result, list)

    def test_sc_ifl_2_max_three(self):
        """SC-IFL-2: len(result) <= 3."""
        response = _make_query_response()
        voice = FRAMEWORK_VOICES[T1Framework.PP]
        result = self.iqs._identify_framework_limitations(T1Framework.PP, voice, response)
        assert len(result) <= 3

    def test_sc_ifl_3_strings_nonempty(self):
        """SC-IFL-3: Each element is a non-empty string."""
        response = _make_query_response()
        voice = FRAMEWORK_VOICES[T1Framework.PP]
        result = self.iqs._identify_framework_limitations(T1Framework.PP, voice, response)
        for lim in result:
            assert isinstance(lim, str) and len(lim) > 0

    def test_sc_ifl_4_unknown_uses_voice_name(self):
        """SC-IFL-4: Fallback for unknown framework uses voice name."""
        response = _make_query_response()
        voice = FRAMEWORK_VOICES[T1Framework.MSI]  # Multisensory — hits else branch
        result = self.iqs._identify_framework_limitations(T1Framework.MSI, voice, response)
        assert any("Multisensory" in lim for lim in result)


# =============================================================================
# SC-SP: _synthesize_panel()
# =============================================================================

class TestSC_SP_SynthesizePanel:
    """Tests for _synthesize_panel success conditions."""

    def setup_method(self):
        self.iqs = _make_iqs_no_embeddings()

    def test_sc_sp_1_returns_3_tuple(self):
        """SC-SP-1: Returns a 3-tuple."""
        comments = [_make_panel_comment()]
        result = self.iqs._synthesize_panel(comments)
        assert isinstance(result, tuple) and len(result) == 3

    def test_sc_sp_2_synthesis_nonempty(self):
        """SC-SP-2: synthesis is non-empty."""
        comments = [_make_panel_comment()]
        synthesis, _, _ = self.iqs._synthesize_panel(comments)
        assert isinstance(synthesis, str) and len(synthesis) > 0

    def test_sc_sp_3_debates_is_list(self):
        """SC-SP-3: debates is a list of strings."""
        comments = [_make_panel_comment()]
        _, debates, _ = self.iqs._synthesize_panel(comments)
        assert isinstance(debates, list)
        for d in debates:
            assert isinstance(d, str)

    def test_sc_sp_4_questions_is_list(self):
        """SC-SP-4: open_questions is a list."""
        comments = [_make_panel_comment()]
        _, _, questions = self.iqs._synthesize_panel(comments)
        assert isinstance(questions, list)

    def test_sc_sp_5_empty_comments_fallback(self):
        """SC-SP-5: Empty comments returns graceful fallback."""
        synthesis, debates, questions = self.iqs._synthesize_panel([])
        assert "No panel discussion" in synthesis
        assert debates == []
        assert questions == []

    def test_sc_sp_6_synthesis_mentions_frameworks(self):
        """SC-SP-6: Synthesis mentions all framework names from input."""
        comments = [
            _make_panel_comment(framework_name="Predictive Processing"),
            _make_panel_comment(
                framework=T1Framework.EC,
                framework_name="Embodied Cognition",
            ),
        ]
        synthesis, _, _ = self.iqs._synthesize_panel(comments)
        assert "Predictive Processing" in synthesis
        assert "Embodied Cognition" in synthesis


# =============================================================================
# SC-GPC: _generate_panel_comments()
# =============================================================================

class TestSC_GPC_GeneratePanelComments:
    """Tests for _generate_panel_comments success conditions."""

    def setup_method(self):
        self.iqs = _make_iqs_no_embeddings()

    def test_sc_gpc_1_returns_list(self):
        """SC-GPC-1: Returns a list of PanelComment."""
        response = _make_query_response()
        result = self.iqs._generate_panel_comments(response)
        assert isinstance(result, list)
        for c in result:
            assert isinstance(c, PanelComment)

    def test_sc_gpc_2_max_four(self):
        """SC-GPC-2: At most 4 framework comments."""
        response = _make_query_response()
        result = self.iqs._generate_panel_comments(response)
        assert len(result) <= 4

    def test_sc_gpc_3_pp_always_included(self):
        """SC-GPC-3: Predictive Processing always included."""
        response = _make_query_response()
        result = self.iqs._generate_panel_comments(response)
        frameworks = [c.framework for c in result]
        assert T1Framework.PP in frameworks

    def test_sc_gpc_4_fields_nonempty(self):
        """SC-GPC-4: Each comment has non-empty perspective, speculation, key_question."""
        response = _make_query_response()
        result = self.iqs._generate_panel_comments(response)
        for c in result:
            assert len(c.perspective) > 0, f"Empty perspective for {c.framework_name}"
            assert len(c.speculation) > 0, f"Empty speculation for {c.framework_name}"
            assert len(c.key_question) > 0, f"Empty key_question for {c.framework_name}"

    def test_sc_gpc_5_framework_names_valid(self):
        """SC-GPC-5: Framework names match FRAMEWORK_VOICES."""
        response = _make_query_response()
        result = self.iqs._generate_panel_comments(response)
        valid_names = {v["name"] for v in FRAMEWORK_VOICES.values()}
        for c in result:
            assert c.framework_name in valid_names

    def test_sc_gpc_6_complications_max_two(self):
        """SC-GPC-6: Each comment has <= 2 complications."""
        response = _make_query_response()
        result = self.iqs._generate_panel_comments(response)
        for c in result:
            assert len(c.complications) <= 2


# =============================================================================
# SC-FFR: format_full_response()
# =============================================================================

class TestSC_FFR_FormatFullResponse:
    """Tests for format_full_response success conditions."""

    def setup_method(self):
        self.iqs = _make_iqs_no_embeddings()

    def test_sc_ffr_1_returns_nonempty_string(self):
        """SC-FFR-1: Returns non-empty string."""
        ir = _make_integrated_response()
        result = self.iqs.format_full_response(ir)
        assert isinstance(result, str) and len(result) > 0

    def test_sc_ffr_2_contains_query(self):
        """SC-FFR-2: Output contains query text."""
        ir = _make_integrated_response()
        result = self.iqs.format_full_response(ir)
        assert ir.template_response.query in result

    def test_sc_ffr_3_contains_headline(self):
        """SC-FFR-3: Output contains headline."""
        ir = _make_integrated_response()
        result = self.iqs.format_full_response(ir)
        assert ir.template_response.headline in result

    def test_sc_ffr_4_contains_evidence_summary(self):
        """SC-FFR-4: Output contains evidence_quality_summary."""
        ir = _make_integrated_response()
        result = self.iqs.format_full_response(ir)
        assert ir.evidence_quality_summary in result

    def test_sc_ffr_5_panel_header_when_comments(self):
        """SC-FFR-5: Contains T1 PANEL DISCUSSION header when comments present."""
        ir = _make_integrated_response()
        result = self.iqs.format_full_response(ir)
        assert "T1 PANEL DISCUSSION" in result

    def test_sc_ffr_6_evidence_header_when_articles(self):
        """SC-FFR-6: Contains ARTICLE EVIDENCE header when evidence present."""
        ir = _make_integrated_response()
        result = self.iqs.format_full_response(ir)
        assert "ARTICLE EVIDENCE" in result

    def test_sc_ffr_7_no_exception_on_empty(self):
        """SC-FFR-7: No exception on minimal response."""
        ir = _make_integrated_response(
            article_evidence=[],
            panel_comments=[],
            panel_synthesis="",
            panel_debates=[],
            open_questions=[],
        )
        result = self.iqs.format_full_response(ir)
        assert isinstance(result, str)


# =============================================================================
# SC-SS: _semantic_search_templates() — only testable in degraded mode
# =============================================================================

class TestSC_SS_SemanticSearch:
    """Tests for _semantic_search_templates success conditions (no-embedding mode)."""

    def setup_method(self):
        self.iqs = _make_iqs_no_embeddings()

    def test_sc_ss_5_no_embeddings_returns_empty(self):
        """SC-SS-5: Returns empty list when embeddings unavailable."""
        result = self.iqs._semantic_search_templates("noise and stress")
        assert result == []


# =============================================================================
# SC-FAE: _find_article_evidence() — no WoB mode
# =============================================================================

class TestSC_FAE_FindArticleEvidence:
    """Tests for _find_article_evidence success conditions (no-WoB mode)."""

    def setup_method(self):
        self.iqs = _make_iqs_no_embeddings()

    def test_sc_fae_1_returns_list(self):
        """SC-FAE-1: Returns a list."""
        template = _make_template_answer()
        result = self.iqs._find_article_evidence(template)
        assert isinstance(result, list)

    def test_sc_fae_5_no_web_returns_empty(self):
        """SC-FAE-5: Returns empty list when web unavailable."""
        self.iqs._web = None  # ensure no cached web
        with patch.object(type(self.iqs), 'web', new_callable=PropertyMock, return_value=None):
            template = _make_template_answer()
            result = self.iqs._find_article_evidence(template)
            assert result == []


# =============================================================================
# SC-Q: query() — integration test
# =============================================================================

class TestSC_Q_Query:
    """Tests for query() success conditions."""

    def setup_method(self):
        self.iqs = _make_iqs_no_embeddings()

    def test_sc_q_1_returns_integrated_response(self):
        """SC-Q-1: Returns IntegratedResponse."""
        result = self.iqs.query("How does noise affect cognition?")
        assert isinstance(result, IntegratedResponse)

    def test_sc_q_2_template_response_populated(self):
        """SC-Q-2: template_response is always populated."""
        result = self.iqs.query("test query")
        assert result.template_response is not None

    def test_sc_q_4_no_panel_when_disabled(self):
        """SC-Q-4: panel_comments empty when include_panel=False."""
        result = self.iqs.query("test", include_panel=False)
        assert result.panel_comments == []

    def test_sc_q_7_no_persona_enrichment_when_none(self):
        """SC-Q-7: persona_enrichment is None when persona=None."""
        result = self.iqs.query("test", persona=None)
        assert result.persona_enrichment is None

    def test_sc_q_8_article_evidence_max_10(self):
        """SC-Q-8: article_evidence limited to 10."""
        result = self.iqs.query("test")
        assert len(result.article_evidence) <= 10

    def test_sc_q_9_evidence_summary_nonempty(self):
        """SC-Q-9: evidence_quality_summary is always non-empty."""
        result = self.iqs.query("test")
        assert len(result.evidence_quality_summary) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
