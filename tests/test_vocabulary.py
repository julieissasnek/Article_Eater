"""Tests for vocabulary module (Sprint D Task D.1)."""

import pytest

from src.extraction.vocabulary import (
    load_vocabulary,
    find_closest_iv,
    find_closest_dv,
    find_closest_variable,
    get_extraction_prompt_vocabulary,
    get_iv_list,
    get_dv_list,
    validate_vocabulary,
)


class TestLoadVocabulary:
    """Tests for vocabulary loading."""

    def test_load_vocabulary_returns_dict(self):
        vocab = load_vocabulary()
        assert isinstance(vocab, dict)

    def test_vocabulary_has_required_keys(self):
        vocab = load_vocabulary()
        assert "independent_variables" in vocab
        assert "dependent_variables" in vocab
        assert "unmapped_flag" in vocab

    def test_vocabulary_has_ivs(self):
        vocab = load_vocabulary()
        ivs = vocab["independent_variables"]
        assert len(ivs) > 20  # Should have many IVs
        assert "ceiling_height_m" in ivs
        assert "illuminance_lux" in ivs
        assert "ambient_noise_dba" in ivs

    def test_vocabulary_has_dvs(self):
        vocab = load_vocabulary()
        dvs = vocab["dependent_variables"]
        assert len(dvs) > 15  # Should have many DVs
        assert "creativity" in dvs
        assert "stress" in dvs
        assert "productivity" in dvs


class TestFindClosestIV:
    """Tests for IV matching."""

    def test_exact_match(self):
        canonical, conf = find_closest_iv("ceiling_height_m")
        assert canonical == "ceiling_height_m"
        assert conf == 1.0

    def test_synonym_match(self):
        canonical, conf = find_closest_iv("ceiling height")
        assert canonical == "ceiling_height_m"
        assert conf >= 0.85

    def test_fuzzy_match(self):
        canonical, conf = find_closest_iv("room tallness")
        assert canonical == "ceiling_height_m"
        assert conf >= 0.4

    def test_noise_synonym(self):
        canonical, conf = find_closest_iv("ambient noise")
        assert canonical == "ambient_noise_dba"
        assert conf >= 0.85

    def test_light_synonym(self):
        canonical, conf = find_closest_iv("daylight")
        assert canonical == "illuminance_lux"
        assert conf >= 0.7

    def test_nature_view_synonym(self):
        canonical, conf = find_closest_iv("nature views")
        assert canonical == "has_nature_view"
        assert conf >= 0.8

    def test_no_match_returns_none(self):
        canonical, conf = find_closest_iv("completely unrelated gibberish xyz123")
        assert canonical is None
        assert conf == 0.0

    def test_empty_string(self):
        canonical, conf = find_closest_iv("")
        assert canonical is None
        assert conf == 0.0


class TestFindClosestDV:
    """Tests for DV matching."""

    def test_exact_match(self):
        canonical, conf = find_closest_dv("creativity")
        assert canonical == "creativity"
        assert conf == 1.0

    def test_synonym_match(self):
        canonical, conf = find_closest_dv("creative thinking")
        assert canonical == "creativity"
        assert conf >= 0.8

    def test_cortisol_maps_to_stress(self):
        # Cortisol is listed as both a synonym and measurement type for stress
        canonical, conf = find_closest_dv("cortisol levels")
        # Could map to either cortisol (its own DV) or stress
        assert canonical in ("cortisol", "stress")
        assert conf >= 0.7

    def test_stress_synonym(self):
        canonical, conf = find_closest_dv("stress reduction")
        assert canonical == "stress"
        assert conf >= 0.8

    def test_measurement_type_match(self):
        canonical, conf = find_closest_dv("Remote Associates Test")
        assert canonical == "creativity"
        assert conf >= 0.4

    def test_recovery_time(self):
        canonical, conf = find_closest_dv("recovery time")
        assert canonical == "recovery_time"
        assert conf >= 0.9

    def test_no_match_returns_none(self):
        canonical, conf = find_closest_dv("xyzzy plugh zorkmid")
        assert canonical is None
        assert conf == 0.0


class TestFindClosestVariable:
    """Tests for combined variable matching."""

    def test_finds_iv(self):
        canonical, var_type, conf = find_closest_variable("ceiling height")
        assert canonical == "ceiling_height_m"
        assert var_type == "iv"
        assert conf >= 0.85

    def test_finds_dv(self):
        canonical, var_type, conf = find_closest_variable("creative output")
        assert canonical == "creativity"
        assert var_type == "dv"
        assert conf >= 0.7

    def test_no_match(self):
        canonical, var_type, conf = find_closest_variable("qwxzjkfm vbnprt")
        assert canonical is None
        assert var_type is None
        assert conf == 0.0


class TestGetExtractionPromptVocabulary:
    """Tests for prompt formatting."""

    def test_returns_string(self):
        prompt = get_extraction_prompt_vocabulary()
        assert isinstance(prompt, str)

    def test_contains_iv_section(self):
        prompt = get_extraction_prompt_vocabulary()
        assert "INDEPENDENT VARIABLES" in prompt

    def test_contains_dv_section(self):
        prompt = get_extraction_prompt_vocabulary()
        assert "DEPENDENT VARIABLES" in prompt

    def test_contains_key_variables(self):
        prompt = get_extraction_prompt_vocabulary()
        assert "ceiling_height_m" in prompt
        assert "creativity" in prompt
        assert "stress" in prompt

    def test_contains_synonyms(self):
        prompt = get_extraction_prompt_vocabulary()
        assert "Synonyms:" in prompt


class TestListFunctions:
    """Tests for list retrieval functions."""

    def test_get_iv_list(self):
        ivs = get_iv_list()
        assert isinstance(ivs, list)
        assert len(ivs) > 20
        assert "ceiling_height_m" in ivs

    def test_get_dv_list(self):
        dvs = get_dv_list()
        assert isinstance(dvs, list)
        assert len(dvs) > 15
        assert "creativity" in dvs


class TestValidateVocabulary:
    """Tests for vocabulary validation."""

    def test_validation_returns_dict(self):
        result = validate_vocabulary()
        assert isinstance(result, dict)

    def test_validation_has_counts(self):
        result = validate_vocabulary()
        assert "iv_count" in result
        assert "dv_count" in result
        assert "total_variables" in result
        assert "total_synonyms" in result

    def test_vocabulary_is_valid(self):
        result = validate_vocabulary()
        # Should have reasonable counts
        assert result["iv_count"] >= 30
        assert result["dv_count"] >= 25
        assert result["total_synonyms"] > 200


class TestEdgeCases:
    """Tests for edge cases and robustness."""

    def test_case_insensitive(self):
        canonical, conf = find_closest_iv("CEILING HEIGHT")
        assert canonical == "ceiling_height_m"

    def test_extra_whitespace(self):
        canonical, conf = find_closest_iv("  ceiling   height  ")
        assert canonical == "ceiling_height_m"

    def test_punctuation_handling(self):
        canonical, conf = find_closest_iv("ceiling-height")
        assert canonical == "ceiling_height_m"

    def test_partial_match(self):
        canonical, conf = find_closest_iv("height")
        # Should still find ceiling_height_m as best match
        assert canonical is not None
        assert conf >= 0.4
