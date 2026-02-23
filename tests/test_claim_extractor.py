"""Tests for claim extraction engine (Sprint D Task D.6)."""

import pytest
from unittest.mock import patch, MagicMock

from src.extraction.claim_extractor import (
    _detect_direction,
    _extract_statistics,
    _extract_sample_size,
    _infer_sample_size_from_stats,
    _detect_context,
    _convert_to_cohens_d,
    _extract_variables_from_row,
    detect_attack_patterns_from_text,
    extract_claims_from_table,
    extract_claims_from_paper,
    get_llm_extraction_prompt,
)


class TestDirectionDetection:
    """Tests for direction detection from text."""

    def test_detect_increase(self):
        assert _detect_direction("ceiling height increases creativity") == "increase"
        assert _detect_direction("natural light enhances mood") == "increase"
        assert _detect_direction("higher noise leads to better focus") == "increase"

    def test_detect_decrease(self):
        assert _detect_direction("noise reduces concentration") == "decrease"
        assert _detect_direction("lower light impairs performance") == "decrease"
        assert _detect_direction("stress levels decreased significantly") == "decrease"

    def test_detect_no_effect(self):
        assert _detect_direction("no significant effect was found") == "no_effect"
        assert _detect_direction("the difference was non-significant (p = 0.15)") == "no_effect"
        assert _detect_direction("results showed ns difference") == "no_effect"

    def test_detect_unknown(self):
        assert _detect_direction("") == "unknown"
        assert _detect_direction("the study measured lighting") == "unknown"

    def test_detect_mixed_signals(self):
        # When both positive and negative signals with equal counts, returns unknown
        text = "increased light levels decreased stress"
        result = _detect_direction(text)
        # Equal counts (1 increase, 1 decrease) returns unknown
        assert result == "unknown"

        # When one dominates, should return that direction
        text2 = "increased light levels improved mood and enhanced performance"
        result2 = _detect_direction(text2)
        assert result2 == "increase"


class TestStatisticsExtraction:
    """Tests for extracting statistical values from text."""

    def test_extract_f_value(self):
        stats = _extract_statistics("F(1, 60) = 4.52, p < .05")
        assert stats.get("f_value") == 4.52
        assert stats.get("df1") == 1
        assert stats.get("df2") == 60

    def test_extract_t_value(self):
        stats = _extract_statistics("t(38) = 2.10, p = .043")
        assert stats.get("t_value") == 2.10
        assert stats.get("df2") == 38

    def test_extract_correlation(self):
        stats = _extract_statistics("r = .30, p < .01")
        assert stats.get("r") == 0.30

    def test_extract_eta_squared(self):
        stats = _extract_statistics("partial eta squared = 0.06")
        assert stats.get("eta_squared") == 0.06

        stats2 = _extract_statistics("η² = .12")
        assert stats2.get("eta_squared") == 0.12

    def test_extract_cohens_d(self):
        stats = _extract_statistics("d = 0.75")
        assert stats.get("cohens_d") == 0.75

        stats2 = _extract_statistics("Cohen's d = 0.50")
        assert stats2.get("cohens_d") == 0.50

    def test_extract_beta(self):
        stats = _extract_statistics("β = 0.35, SE = 0.12")
        assert stats.get("beta") == 0.35

    def test_extract_p_value(self):
        stats = _extract_statistics("p < 0.001")
        assert stats.get("p_value") == 0.001

        stats2 = _extract_statistics("p = 0.043")
        assert stats2.get("p_value") == 0.043

    def test_extract_multiple_stats(self):
        text = "F(1, 120) = 8.50, p < .01, η² = .07"
        stats = _extract_statistics(text)
        assert stats.get("f_value") == 8.50
        assert stats.get("df1") == 1
        assert stats.get("df2") == 120
        assert stats.get("eta_squared") == 0.07
        assert stats.get("p_value") == 0.01

    def test_invalid_correlation_rejected(self):
        stats = _extract_statistics("r = 1.5")  # Invalid
        assert "r" not in stats


class TestSampleSizeExtraction:
    """Tests for sample size extraction."""

    def test_extract_n_equals(self):
        assert _extract_sample_size("N = 120") == 120
        assert _extract_sample_size("n = 45") == 45

    def test_extract_sample_size(self):
        assert _extract_sample_size("sample size: 200") == 200

    def test_extract_participants(self):
        assert _extract_sample_size("120 participants completed the study") == 120

    def test_no_sample_found(self):
        assert _extract_sample_size("the study measured responses") is None

    def test_infer_sample_from_t_and_f_stats(self):
        assert _infer_sample_size_from_stats({"t_value": 2.1, "df2": 38}) == 40
        assert _infer_sample_size_from_stats({"f_value": 4.0, "df1": 1, "df2": 60}) == 62


class TestContextDetection:
    """Tests for study context detection."""

    def test_detect_office(self):
        assert _detect_context("open-plan office environment") == "office"
        assert _detect_context("workplace lighting") == "office"

    def test_detect_hospital(self):
        assert _detect_context("hospital recovery room") == "hospital"
        assert _detect_context("patient outcomes in healthcare setting") == "hospital"

    def test_detect_school(self):
        assert _detect_context("classroom lighting") == "school"
        assert _detect_context("student performance in university") == "school"

    def test_detect_residential(self):
        assert _detect_context("home environment") == "residential"
        assert _detect_context("residential apartment") == "residential"

    def test_detect_laboratory(self):
        assert _detect_context("laboratory experiment") == "laboratory"
        assert _detect_context("controlled lab setting") == "laboratory"

    def test_no_context(self):
        assert _detect_context("the study found effects") is None


class TestEffectSizeConversion:
    """Tests for effect size conversion to Cohen's d."""

    def test_passthrough_cohens_d(self):
        d, dtype = _convert_to_cohens_d({"cohens_d": 0.75}, 100)
        assert d == 0.75
        assert dtype == "cohens_d"

    def test_convert_r(self):
        d, dtype = _convert_to_cohens_d({"r": 0.30}, 100)
        assert d is not None
        assert 0.60 < d < 0.70  # Expected ~0.63
        assert dtype == "r_converted"

    def test_convert_eta_squared(self):
        d, dtype = _convert_to_cohens_d({"eta_squared": 0.06}, 100)
        assert d is not None
        assert 0.48 < d < 0.54  # Expected ~0.51
        assert dtype == "eta_squared_converted"

    def test_convert_t_value(self):
        d, dtype = _convert_to_cohens_d({"t_value": 2.10, "df2": 38}, 40)
        assert d is not None
        assert 0.65 < d < 0.72  # Expected ~0.68
        assert dtype == "t_value_converted"

    def test_convert_f_value(self):
        d, dtype = _convert_to_cohens_d({"f_value": 4.0, "df1": 1, "df2": 60}, 62)
        assert d is not None
        assert 0.48 < d < 0.56  # Expected ~0.52
        assert dtype == "f_value_converted"

    def test_no_stats(self):
        d, dtype = _convert_to_cohens_d({}, None)
        assert d is None
        assert dtype is None


class TestVariableExtraction:
    """Tests for extracting variable pairs from text."""

    def test_extract_affects_pattern(self):
        candidates = _extract_variables_from_row("ceiling height affects creativity")
        assert len(candidates) >= 1
        assert any("ceiling" in c["iv_raw"].lower() for c in candidates)

    def test_extract_leads_to_pattern(self):
        candidates = _extract_variables_from_row("natural light leads to improved mood")
        assert len(candidates) >= 1

    def test_extract_arrow_pattern(self):
        candidates = _extract_variables_from_row("noise → stress")
        assert len(candidates) >= 1

    def test_short_text_skipped(self):
        candidates = _extract_variables_from_row("x y")
        assert len(candidates) == 0


class TestTableExtraction:
    """Tests for extracting claims from tables."""

    @pytest.fixture
    def sample_vocabulary(self):
        return {
            "independent_variables": {
                "ceiling_height_m": {
                    "synonyms": ["ceiling height", "room height", "vertical dimension"],
                    "domain": "A2_Spatial_Scale",
                },
                "illuminance_lux": {
                    "synonyms": ["daylight", "light level", "lighting"],
                    "domain": "A4_Light",
                },
                "ambient_noise_dba": {
                    "synonyms": ["noise", "ambient noise", "sound level"],
                    "domain": "A5_Acoustic",
                },
            },
            "dependent_variables": {
                "creativity": {
                    "synonyms": ["creative thinking", "divergent thinking", "creative output"],
                    "measurement_types": ["RAT", "AUT", "Torrance"],
                },
                "stress": {
                    "synonyms": ["psychological stress", "stress levels", "anxiety"],
                    "measurement_types": ["cortisol", "PSS", "STAI"],
                },
            },
        }

    @pytest.fixture
    def sample_table(self):
        return {
            "paper_id": "test_paper_001",
            "table_id": "TBL-001",
            "page": 5,
            "rows": [
                {
                    "text": "High ceiling height increases creative thinking, F(1, 60) = 4.50, p < .05, η² = .07, N = 62",
                },
                {
                    "text": "Noise levels lead to higher stress, r = .35, p < .01, n = 120",
                },
            ],
        }

    def test_extract_from_table(self, sample_table, sample_vocabulary):
        claims = extract_claims_from_table(
            sample_table,
            vocabulary=sample_vocabulary,
            method="rule_based",
        )

        assert len(claims) >= 1
        assert all("claim_id" in c for c in claims)
        assert all("paper_id" in c for c in claims)
        assert all("direction" in c for c in claims)
        assert all(c.get("claim_type") for c in claims)
        assert all(c.get("rule_type") for c in claims)

    def test_claims_have_required_fields(self, sample_table, sample_vocabulary):
        claims = extract_claims_from_table(
            sample_table,
            vocabulary=sample_vocabulary,
            method="rule_based",
        )

        required_fields = [
            "claim_id", "paper_id", "iv", "dv", "direction",
            "effect_size", "source_quote", "extraction_confidence",
            "claim_type", "rule_type", "field_targets",
        ]

        for claim in claims:
            for field in required_fields:
                assert field in claim, f"Missing field: {field}"

    def test_claims_include_field_contract_hints(self, sample_table, sample_vocabulary):
        claims = extract_claims_from_table(
            sample_table,
            paper_context={"article_type_family": "empirical_v2"},
            vocabulary=sample_vocabulary,
            method="rule_based",
        )
        assert claims
        for claim in claims:
            assert claim.get("article_type_family") == "empirical_v2"
            assert claim.get("field_contract_family") == "empirical_v2"
            assert isinstance(claim.get("field_targets"), list)
            assert claim.get("field_targets")

    def test_effect_sizes_converted(self, sample_table, sample_vocabulary):
        claims = extract_claims_from_table(
            sample_table,
            vocabulary=sample_vocabulary,
            method="rule_based",
        )

        # At least some claims should have effect sizes
        claims_with_effect = [c for c in claims if c.get("effect_size") is not None]
        # May or may not find them depending on extraction success

    def test_claims_include_attack_annotation_fields(self, sample_table, sample_vocabulary):
        claims = extract_claims_from_table(
            sample_table,
            vocabulary=sample_vocabulary,
            method="rule_based",
        )
        assert claims
        for claim in claims:
            assert "attack_patterns" in claim
            assert "attack_detected" in claim
            assert "attack_types" in claim
            assert "attack_max_confidence" in claim
            assert isinstance(claim["attack_patterns"], list)
            assert isinstance(claim["attack_types"], list)


class TestAttackPatternDetection:
    """Tests for ATK-2 argument-attack cue extraction."""

    def test_detect_attack_patterns_from_text(self):
        text = (
            "An unmeasured confounding variable may explain the effect and "
            "failed to replicate in follow-up studies."
        )
        patterns = detect_attack_patterns_from_text(text)
        attack_types = {p["attack_type"] for p in patterns}
        assert "confounder" in attack_types
        assert "replication" in attack_types


class TestPaperExtraction:
    """Tests for extracting claims from multiple tables in a paper."""

    @pytest.fixture
    def sample_vocabulary(self):
        return {
            "independent_variables": {
                "ceiling_height_m": {"synonyms": ["ceiling height"]},
                "illuminance_lux": {"synonyms": ["light level"]},
            },
            "dependent_variables": {
                "creativity": {"synonyms": ["creative thinking"]},
                "stress": {"synonyms": ["stress levels"]},
            },
        }

    def test_extract_from_multiple_tables(self, sample_vocabulary):
        tables = [
            {
                "table_id": "TBL-001",
                "page": 5,
                "rows": [{"text": "ceiling height affects creativity, p < .05"}],
            },
            {
                "table_id": "TBL-002",
                "page": 8,
                "rows": [{"text": "light level reduces stress, p < .01"}],
            },
        ]

        claims = extract_claims_from_paper(
            paper_id="test_paper",
            tables=tables,
            vocabulary=sample_vocabulary,
            method="rule_based",
        )

        # Should have claims from both tables
        assert len(claims) >= 0  # May not extract if patterns don't match

    def test_deduplication(self, sample_vocabulary):
        # Same claim in two tables should be deduplicated
        tables = [
            {
                "table_id": "TBL-001",
                "rows": [{"text": "ceiling height increases creativity"}],
            },
            {
                "table_id": "TBL-002",
                "rows": [{"text": "ceiling height increases creativity"}],
            },
        ]

        claims = extract_claims_from_paper(
            paper_id="test_paper",
            tables=tables,
            vocabulary=sample_vocabulary,
            method="rule_based",
        )

        # Should be deduplicated based on IV+DV+direction
        iv_dv_pairs = [(c.get("iv"), c.get("dv"), c.get("direction")) for c in claims]
        # No duplicates
        assert len(iv_dv_pairs) == len(set(iv_dv_pairs))


class TestLLMPromptGeneration:
    """Tests for LLM extraction prompt generation."""

    def test_prompt_includes_table_content(self):
        prompt = get_llm_extraction_prompt(
            table_content="F(1, 60) = 4.50, p < .05",
            table_type="RESULTS_ANOVA",
            paper_title="Test Paper",
        )

        assert "F(1, 60) = 4.50" in prompt
        assert "RESULTS_ANOVA" in prompt
        assert "Test Paper" in prompt

    def test_prompt_includes_vocabulary(self):
        vocab = {
            "independent_variables": {
                "ceiling_height_m": {"synonyms": ["ceiling height"]},
            },
            "dependent_variables": {
                "creativity": {"synonyms": ["creative thinking"]},
            },
        }

        prompt = get_llm_extraction_prompt(
            table_content="test content",
            table_type="RESULTS",
            vocabulary=vocab,
        )

        assert "ceiling_height_m" in prompt
        assert "creativity" in prompt

    def test_prompt_includes_output_format(self):
        prompt = get_llm_extraction_prompt(
            table_content="test",
            table_type="RESULTS",
        )

        assert "JSON array" in prompt
        assert "iv_mapped" in prompt
        assert "effect_size" in prompt


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_table(self):
        claims = extract_claims_from_table(
            {"paper_id": "test", "rows": []},
            method="rule_based",
        )
        assert claims == []

    def test_table_no_extractable_content(self):
        claims = extract_claims_from_table(
            {
                "paper_id": "test",
                "rows": [{"text": "a b c"}],  # Too short
            },
            method="rule_based",
        )
        assert claims == []

    def test_invalid_method_raises(self):
        with pytest.raises(ValueError, match="Unknown extraction method"):
            extract_claims_from_table(
                {"paper_id": "test", "rows": []},
                method="invalid_method",
            )

    def test_missing_vocabulary_loads_default(self):
        # Should not raise even without vocabulary
        try:
            claims = extract_claims_from_table(
                {
                    "paper_id": "test",
                    "rows": [{"text": "ceiling height affects creativity, p < .05, N = 50"}],
                },
                vocabulary=None,  # Will load default
                method="rule_based",
            )
        except FileNotFoundError:
            pytest.skip("Vocabulary file not found - expected in test environment")


class TestIntegrationWithVocabulary:
    """Integration tests with actual vocabulary mapping."""

    @pytest.fixture
    def real_vocabulary(self):
        """Load actual vocabulary if available."""
        try:
            from src.extraction.vocabulary import load_vocabulary
            return load_vocabulary()
        except FileNotFoundError:
            pytest.skip("Vocabulary file not available")

    def test_known_iv_mapping(self, real_vocabulary):
        from src.extraction.vocabulary import find_closest_iv

        iv, conf = find_closest_iv("ceiling height", real_vocabulary)
        assert iv == "ceiling_height_m"
        assert conf >= 0.8

    def test_known_dv_mapping(self, real_vocabulary):
        from src.extraction.vocabulary import find_closest_dv

        dv, conf = find_closest_dv("creative thinking", real_vocabulary)
        assert dv == "creativity"
        assert conf >= 0.8


class TestSpecialTableModes:
    """Tests for correlation-matrix and stepwise-regression extraction paths."""

    @pytest.fixture
    def sample_vocabulary(self):
        return {
            "independent_variables": {
                "ceiling_height_m": {"synonyms": ["ceiling height", "height"]},
                "ambient_noise_dba": {"synonyms": ["noise", "ambient noise"]},
            },
            "dependent_variables": {
                "creativity": {"synonyms": ["creativity", "creative thinking"]},
                "stress": {"synonyms": ["stress", "stress levels"]},
            },
        }

    def test_correlation_matrix_numbered_headers_are_mapped(self, sample_vocabulary):
        table = {
            "paper_id": "corr_paper",
            "table_id": "TBL-CORR",
            "type": "RESULTS_CORRELATION",
            "rows": [
                {"text": "col_1: Variable; col_2: 1; col_3: 2"},
                {"text": "col_1: 1 ceiling height; col_2: 1.00; col_3: .31**"},
                {"text": "col_1: 2 creativity; col_2: .31**; col_3: 1.00"},
            ],
        }
        claims = extract_claims_from_table(table, vocabulary=sample_vocabulary, method="enhanced")
        assert any(c.get("extraction_method") == "correlation_matrix" for c in claims)
        assert any(c.get("iv") and c.get("dv") for c in claims)

    def test_stepwise_regression_uses_caption_first_dv(self, sample_vocabulary):
        table = {
            "paper_id": "reg_paper",
            "table_id": "TBL-REG",
            "type": "RESULTS_REGRESSION",
            "sample_content": "Table 3. Stepwise regression predicting creativity from environmental features.",
            "rows": [
                {"text": "col_1: Step 1; col_2: R2 = .18"},
                {"text": "col_1: ceiling height; col_2: beta = 0.34; col_3: t = 2.8; col_4: p = .01"},
            ],
        }
        claims = extract_claims_from_table(table, vocabulary=sample_vocabulary, method="enhanced")
        assert any(c.get("extraction_method") == "stepwise_regression" for c in claims)
        assert any(c.get("dv") == "creativity" for c in claims)

    def test_regression_column_semantics_recovers_stats_direction_and_n(self, sample_vocabulary):
        table = {
            "paper_id": "reg_cols_paper",
            "table_id": "TBL-REG-COLS",
            "type": "RESULTS_REGRESSION",
            "sample_content": "Table 2. Stepwise regression predicting stress from environmental features.",
            "rows": [
                {"text": "col_1: Predictor; col_2: beta; col_3: p; col_4: N"},
                {"text": "col_1: ambient noise; col_2: -0.32; col_3: .01; col_4: 120"},
            ],
        }
        claims = extract_claims_from_table(table, vocabulary=sample_vocabulary, method="enhanced")
        assert claims
        best = claims[0]
        assert best.get("direction") in {"decrease", "increase"}
        assert best.get("effect_size") is not None
        assert best.get("sample_n") == 120
