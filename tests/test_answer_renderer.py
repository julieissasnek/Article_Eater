"""
Tests for Answer Renderer
===========================

Tests confidence thermometer, per-user rendering, and quality gate.
"""

import pytest
from src.qa.answer_renderer import (
    AnswerRenderer,
    ConfidenceLevel,
    ConfidenceThermometer,
    RenderingConfig,
    USER_TYPE_CONFIGS,
    build_thermometer,
    compute_confidence_level,
)


class TestConfidenceThermometer:
    """Test confidence level computation and thermometer building."""

    def test_high_confidence(self):
        level = compute_confidence_level(0.85)
        assert level == ConfidenceLevel.HIGH

    def test_mod_high_confidence(self):
        level = compute_confidence_level(0.62)
        assert level == ConfidenceLevel.MOD_HIGH

    def test_moderate_confidence(self):
        level = compute_confidence_level(0.42)
        assert level == ConfidenceLevel.MODERATE

    def test_low_confidence(self):
        level = compute_confidence_level(0.15)
        assert level == ConfidenceLevel.LOW

    def test_build_thermometer(self):
        therm = build_thermometer(0.65, n_findings=12, n_replications=3)
        assert therm.level == ConfidenceLevel.MOD_HIGH
        assert therm.color == "#2171B5"  # ATLAS blue
        assert "Mod-High" in therm.label
        assert "0.65" in therm.label
        assert therm.n_supporting_findings == 12

    def test_thermometer_to_dict(self):
        therm = build_thermometer(0.35)
        d = therm.to_dict()
        assert d["level"] == "moderate"
        assert d["color"] == "#F39C12"  # ATLAS amber
        assert isinstance(d["omega_composite"], float)

    def test_boundary_values(self):
        """Boundary values map correctly (strict > comparison)."""
        assert compute_confidence_level(0.71) == ConfidenceLevel.HIGH
        assert compute_confidence_level(0.70) == ConfidenceLevel.MOD_HIGH  # NOT > 0.7
        assert compute_confidence_level(0.51) == ConfidenceLevel.MOD_HIGH
        assert compute_confidence_level(0.50) == ConfidenceLevel.MODERATE  # NOT > 0.5
        assert compute_confidence_level(0.31) == ConfidenceLevel.MODERATE
        assert compute_confidence_level(0.30) == ConfidenceLevel.LOW      # NOT > 0.3


class TestUserTypeConfigs:
    """Test that all user types have valid configs."""

    def test_all_user_types_have_configs(self):
        expected = [
            "general_public", "student", "clinician",
            "architect_designer", "researcher", "deep_researcher",
        ]
        for ut in expected:
            assert ut in USER_TYPE_CONFIGS, f"Missing config for {ut}"

    def test_general_public_is_shortest(self):
        gp = USER_TYPE_CONFIGS["general_public"]
        assert gp.max_length_words <= 100
        assert gp.disclosure_levels == ["L1"]
        assert gp.include_citations is False

    def test_deep_researcher_is_unlimited(self):
        dr = USER_TYPE_CONFIGS["deep_researcher"]
        assert dr.max_length_words == 0  # unlimited
        assert dr.include_provenance_chains is True
        assert dr.include_research_tools is True
        assert dr.include_omega_scores is True

    def test_architect_designer_has_design_implications(self):
        ad = USER_TYPE_CONFIGS["architect_designer"]
        assert ad.include_design_implications is True

    def test_voice_bias_sums_to_one(self):
        for name, config in USER_TYPE_CONFIGS.items():
            total = config.voice_bias_popular + config.voice_bias_expert
            assert abs(total - 1.0) < 0.01, f"{name}: voice bias sums to {total}"


class TestAnswerRenderer:
    """Test the AnswerRenderer class."""

    @pytest.fixture
    def renderer(self):
        return AnswerRenderer()

    @pytest.fixture
    def sample_evidence(self):
        return {
            "findings": [
                {
                    "antecedent": "natural daylight exposure",
                    "consequent": "cognitive task performance",
                    "direction": "increase",
                    "p_value": "0.03",
                    "source_file": "study1.json",
                },
                {
                    "antecedent": "artificial lighting",
                    "consequent": "fatigue",
                    "direction": "increase",
                    "p_value": "0.01",
                    "source_file": "study2.json",
                },
            ]
        }

    @pytest.fixture
    def sample_omega(self):
        return {
            "scores": [
                {"omega_total": 0.55, "omega_sev": 0.7, "omega_conf": 0.8},
                {"omega_total": 0.60, "omega_sev": 0.65, "omega_conf": 0.75},
            ]
        }

    def test_render_produces_answer(self, renderer, sample_evidence, sample_omega):
        result = renderer.render(
            "lighting_performance", sample_evidence, sample_omega, "researcher"
        )
        assert result.prose
        assert result.word_count > 0
        assert result.thermometer is not None

    def test_render_general_public_is_short(self, renderer, sample_evidence, sample_omega):
        result = renderer.render(
            "lighting_performance", sample_evidence, sample_omega, "general_public"
        )
        assert result.word_count <= 120  # ~100 word limit + tolerance

    def test_render_deep_researcher_is_longer(self, renderer, sample_evidence, sample_omega):
        gp = renderer.render(
            "lighting_performance", sample_evidence, sample_omega, "general_public"
        )
        dr = renderer.render(
            "lighting_performance", sample_evidence, sample_omega, "deep_researcher"
        )
        assert dr.word_count > gp.word_count

    def test_thermometer_color_matches_level(self, renderer, sample_evidence, sample_omega):
        result = renderer.render(
            "lighting_performance", sample_evidence, sample_omega, "researcher"
        )
        level = result.thermometer.level
        expected_color = {
            ConfidenceLevel.HIGH: "#27AE60",
            ConfidenceLevel.MOD_HIGH: "#2171B5",
            ConfidenceLevel.MODERATE: "#F39C12",
            ConfidenceLevel.LOW: "#CB4335",
        }
        assert result.thermometer.color == expected_color[level]

    def test_quality_check_runs(self, renderer, sample_evidence, sample_omega):
        result = renderer.render(
            "lighting_performance", sample_evidence, sample_omega, "student"
        )
        assert result.quality_score > 0
        assert isinstance(result.quality_passed, bool)

    def test_architect_designer_includes_design(self, renderer, sample_evidence, sample_omega):
        result = renderer.render(
            "lighting_performance", sample_evidence, sample_omega, "architect_designer"
        )
        assert "design" in result.prose.lower()

    def test_to_dict(self, renderer, sample_evidence, sample_omega):
        result = renderer.render(
            "nature_restoration", sample_evidence, sample_omega, "student"
        )
        d = result.to_dict()
        assert "thermometer" in d
        assert "prose" in d
        assert d["user_type"] == "student"
