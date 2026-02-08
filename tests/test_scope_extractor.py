"""
Tests for Scope Extractor (TD-B: Scope Extraction)

Sprint: TD-B
Created: February 8, 2026
"""

import pytest
from typing import Dict

from src.services.scope_extractor import (
    ScopeExtractor,
    ExtractedScope,
    ScopeSource,
    PopulationCategory,
    SettingCategory,
    DurationCategory,
    extract_scope,
    extract_scope_from_claim,
    get_scope_extractor,
    POPULATION_PATTERNS,
    SETTING_PATTERNS,
    DURATION_PATTERNS,
    NATURE_TYPE_PATTERNS,
)


# =============================================================================
# PATTERN TESTS
# =============================================================================

class TestPatternDefinitions:
    """Test that pattern dictionaries are properly defined."""

    def test_population_patterns_exist(self):
        """All population categories should have patterns."""
        expected = {PopulationCategory.CHILDREN, PopulationCategory.ELDERLY,
                   PopulationCategory.CLINICAL, PopulationCategory.HEALTHY}
        assert expected.issubset(set(POPULATION_PATTERNS.keys()))

    def test_setting_patterns_exist(self):
        """All setting categories should have patterns."""
        expected = {SettingCategory.LABORATORY, SettingCategory.FIELD,
                   SettingCategory.SIMULATED}
        assert expected.issubset(set(SETTING_PATTERNS.keys()))

    def test_duration_patterns_exist(self):
        """All duration categories should have patterns."""
        expected = {DurationCategory.ACUTE, DurationCategory.CHRONIC}
        assert expected.issubset(set(DURATION_PATTERNS.keys()))

    def test_nature_type_patterns_exist(self):
        """CNFA nature types should have patterns."""
        expected = {"forest", "park", "water", "indoor_plants"}
        assert expected.issubset(set(NATURE_TYPE_PATTERNS.keys()))


# =============================================================================
# EXTRACTED SCOPE TESTS
# =============================================================================

class TestExtractedScope:
    """Test ExtractedScope dataclass."""

    def test_scope_creation(self):
        """Can create scope with all fields."""
        scope = ExtractedScope(
            population="adults",
            population_category=PopulationCategory.ADULTS,
            setting="laboratory",
            setting_category=SettingCategory.LABORATORY,
            duration="acute",
            duration_category=DurationCategory.ACUTE,
            duration_minutes=20,
            source=ScopeSource.EXPLICIT
        )
        assert scope.population == "adults"
        assert scope.duration_minutes == 20

    def test_scope_to_dict(self):
        """Scope should serialize to dict."""
        scope = ExtractedScope(
            population="children",
            population_category=PopulationCategory.CHILDREN,
            source=ScopeSource.EXPLICIT,
            explicit_fields={"population"},
            generalization_risk=0.6
        )
        d = scope.to_dict()
        assert d['population'] == "children"
        assert d['population_category'] == "children"
        assert d['source'] == "explicit"
        assert 'population' in d['explicit_fields']

    def test_default_scope(self):
        """Default scope should have unknown source."""
        scope = ExtractedScope()
        assert scope.source == ScopeSource.UNKNOWN
        assert scope.population is None


# =============================================================================
# POPULATION EXTRACTION TESTS
# =============================================================================

class TestPopulationExtraction:
    """Test population extraction."""

    def setup_method(self):
        self.extractor = ScopeExtractor(use_spacy=False)

    def test_extract_children(self):
        """Should extract children population."""
        text = "The study included 50 children aged 8-12 years."
        scope = self.extractor.extract(text)
        assert scope.population_category == PopulationCategory.CHILDREN

    def test_extract_elderly(self):
        """Should extract elderly population."""
        text = "Older adults (mean age 72) participated in the study."
        scope = self.extractor.extract(text)
        assert scope.population_category == PopulationCategory.ELDERLY

    def test_extract_clinical(self):
        """Should extract clinical population."""
        text = "Patients with diagnosed depression were recruited."
        scope = self.extractor.extract(text)
        assert scope.population_category == PopulationCategory.CLINICAL

    def test_extract_healthy(self):
        """Should extract healthy population."""
        text = "Healthy volunteers from the community participated."
        scope = self.extractor.extract(text)
        assert scope.population_category == PopulationCategory.HEALTHY

    def test_extract_college_students(self):
        """Should extract young adults (college students)."""
        text = "Undergraduate students from the university were recruited."
        scope = self.extractor.extract(text)
        assert scope.population_category == PopulationCategory.YOUNG_ADULTS


# =============================================================================
# SETTING EXTRACTION TESTS
# =============================================================================

class TestSettingExtraction:
    """Test setting extraction."""

    def setup_method(self):
        self.extractor = ScopeExtractor(use_spacy=False)

    def test_extract_laboratory(self):
        """Should extract laboratory setting."""
        text = "Participants were tested in a controlled laboratory environment."
        scope = self.extractor.extract(text)
        assert scope.setting_category == SettingCategory.LABORATORY

    def test_extract_field(self):
        """Should extract field setting."""
        text = "A naturalistic field study was conducted in local parks."
        scope = self.extractor.extract(text)
        assert scope.setting_category == SettingCategory.FIELD

    def test_extract_simulated(self):
        """Should extract simulated (VR/photos) setting."""
        text = "Participants viewed photographs of natural and urban scenes."
        scope = self.extractor.extract(text)
        assert scope.setting_category == SettingCategory.SIMULATED

    def test_extract_urban(self):
        """Should extract urban setting."""
        text = "The study was conducted in urban areas of the city."
        scope = self.extractor.extract(text)
        assert scope.setting_category == SettingCategory.URBAN

    def test_extract_hospital(self):
        """Should extract hospital setting."""
        text = "Patients in the hospital ward were observed during recovery."
        scope = self.extractor.extract(text)
        assert scope.setting_category == SettingCategory.HOSPITAL


# =============================================================================
# DURATION EXTRACTION TESTS
# =============================================================================

class TestDurationExtraction:
    """Test duration extraction."""

    def setup_method(self):
        self.extractor = ScopeExtractor(use_spacy=False)

    def test_extract_acute(self):
        """Should extract acute duration."""
        text = "A single brief exposure of 20 minutes was used."
        scope = self.extractor.extract(text)
        assert scope.duration_category == DurationCategory.ACUTE

    def test_extract_minutes(self):
        """Should extract and normalize minutes."""
        text = "Participants were exposed for 30 minutes."
        scope = self.extractor.extract(text)
        assert scope.duration_minutes == 30

    def test_extract_hours_to_minutes(self):
        """Should convert hours to minutes."""
        text = "The intervention lasted 2 hours."
        scope = self.extractor.extract(text)
        assert scope.duration_minutes == 120

    def test_extract_chronic(self):
        """Should extract chronic duration."""
        text = "Long-term residential proximity to green space was measured."
        scope = self.extractor.extract(text)
        assert scope.duration_category == DurationCategory.CHRONIC

    def test_extract_repeated(self):
        """Should extract repeated exposure."""
        text = "Participants attended multiple sessions twice per week."
        scope = self.extractor.extract(text)
        assert scope.duration_category == DurationCategory.REPEATED


# =============================================================================
# NATURE TYPE EXTRACTION TESTS
# =============================================================================

class TestNatureTypeExtraction:
    """Test CNFA-specific nature type extraction."""

    def setup_method(self):
        self.extractor = ScopeExtractor(use_spacy=False)

    def test_extract_forest(self):
        """Should extract forest nature type."""
        text = "Participants walked through a forest trail."
        scope = self.extractor.extract(text)
        assert scope.nature_type == "forest"

    def test_extract_park(self):
        """Should extract park nature type."""
        text = "The study was conducted in an urban green space."
        scope = self.extractor.extract(text)
        assert scope.nature_type == "park"

    def test_extract_water(self):
        """Should extract water nature type."""
        text = "Views of the lake were compared to urban views."
        scope = self.extractor.extract(text)
        assert scope.nature_type == "water"

    def test_extract_indoor_plants(self):
        """Should extract indoor plants nature type."""
        text = "Indoor plants were placed in office environments."
        scope = self.extractor.extract(text)
        assert scope.nature_type == "indoor_plants"


# =============================================================================
# METHODOLOGY EXTRACTION TESTS
# =============================================================================

class TestMethodologyExtraction:
    """Test methodology extraction."""

    def setup_method(self):
        self.extractor = ScopeExtractor(use_spacy=False)

    def test_extract_rct(self):
        """Should extract RCT methodology."""
        text = "A randomized controlled trial was conducted."
        scope = self.extractor.extract(text)
        assert scope.methodology == "RCT"

    def test_extract_observational(self):
        """Should extract observational methodology."""
        text = "This cross-sectional survey examined associations."
        scope = self.extractor.extract(text)
        assert scope.methodology == "observational"

    def test_extract_longitudinal(self):
        """Should extract longitudinal methodology."""
        text = "A prospective cohort study followed participants."
        scope = self.extractor.extract(text)
        assert scope.methodology == "longitudinal"

    def test_extract_within_subjects(self):
        """Should extract within-subjects design."""
        text = "A repeated measures design was used."
        scope = self.extractor.extract(text)
        assert scope.methodology == "within_subjects"


# =============================================================================
# GENERALIZATION RISK TESTS
# =============================================================================

class TestGeneralizationRisk:
    """Test generalization risk calculation."""

    def setup_method(self):
        self.extractor = ScopeExtractor(use_spacy=False)

    def test_simulated_higher_risk(self):
        """Simulated settings should have higher risk."""
        simulated = self.extractor.extract("Participants viewed photographs of nature.")
        field = self.extractor.extract("A naturalistic field study in parks.")

        assert simulated.generalization_risk > field.generalization_risk

    def test_young_adults_higher_risk(self):
        """College student samples (WEIRD) should have higher risk."""
        students = self.extractor.extract("Undergraduate students participated.")
        general = self.extractor.extract("Adults from the general population.")

        # Both should extract, students should have higher risk
        if students.population_category and general.population_category:
            assert students.generalization_risk >= general.generalization_risk

    def test_more_dimensions_lower_risk(self):
        """More specified dimensions should reduce risk."""
        sparse = self.extractor.extract("A study was conducted.")
        rich = self.extractor.extract(
            "Healthy adults aged 25-40 were tested in a field setting "
            "with 30 minutes of forest exposure."
        )

        assert rich.generalization_risk < sparse.generalization_risk

    def test_risk_bounds(self):
        """Risk should be bounded between 0.1 and 0.9."""
        scope = self.extractor.extract("Some text about a study.")
        assert 0.1 <= scope.generalization_risk <= 0.9


# =============================================================================
# SOURCE TRACKING TESTS
# =============================================================================

class TestSourceTracking:
    """Test explicit vs. inferred tracking."""

    def setup_method(self):
        self.extractor = ScopeExtractor(use_spacy=False)

    def test_explicit_source(self):
        """Matched fields should be marked explicit."""
        scope = self.extractor.extract("Children participated in the laboratory study.")
        assert scope.source == ScopeSource.EXPLICIT
        assert 'population' in scope.explicit_fields
        assert 'setting' in scope.explicit_fields

    def test_unknown_source_for_empty(self):
        """No matches should result in unknown source."""
        scope = self.extractor.extract("The results were interesting.")
        assert scope.source == ScopeSource.UNKNOWN
        assert len(scope.explicit_fields) == 0


# =============================================================================
# SECTION-AWARE EXTRACTION TESTS
# =============================================================================

class TestSectionAwareExtraction:
    """Test section-aware extraction."""

    def setup_method(self):
        self.extractor = ScopeExtractor(use_spacy=False)

    def test_methods_section_priority(self):
        """Methods section should be primary source."""
        scope = self.extractor.extract_from_sections(
            methods="Fifty children aged 8-12 participated in the laboratory study.",
            abstract="This study examined nature effects."
        )
        assert scope.population_category == PopulationCategory.CHILDREN
        assert scope.setting_category == SettingCategory.LABORATORY

    def test_abstract_fills_gaps(self):
        """Abstract should fill gaps from methods."""
        scope = self.extractor.extract_from_sections(
            methods="Participants were tested in the laboratory.",
            abstract="Elderly adults from the community were recruited."
        )
        # Setting from methods, population from abstract
        assert scope.setting_category == SettingCategory.LABORATORY
        assert scope.population_category == PopulationCategory.ELDERLY
        assert 'population' in scope.inferred_fields  # Came from abstract

    def test_discussion_limitations(self):
        """Discussion limitations should increase risk."""
        scope_no_limit = self.extractor.extract_from_sections(
            methods="Healthy adults participated."
        )
        scope_with_limit = self.extractor.extract_from_sections(
            methods="Healthy adults participated.",
            discussion="Limitations include that results may not generalize to other populations."
        )
        assert scope_with_limit.generalization_risk > scope_no_limit.generalization_risk

    def test_methods_boost_confidence(self):
        """Methods section should boost confidence."""
        methods_scope = self.extractor.extract(
            "Adults participated in a 30 minute forest walk.",
            is_methods_section=True
        )
        normal_scope = self.extractor.extract(
            "Adults participated in a 30 minute forest walk.",
            is_methods_section=False
        )
        assert methods_scope.extraction_confidence >= normal_scope.extraction_confidence


# =============================================================================
# CONVENIENCE FUNCTION TESTS
# =============================================================================

class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_get_scope_extractor_singleton(self):
        """get_scope_extractor returns singleton."""
        e1 = get_scope_extractor()
        e2 = get_scope_extractor()
        assert e1 is e2

    def test_extract_scope_function(self):
        """extract_scope convenience function works."""
        scope = extract_scope("Children in the park were observed.")
        assert isinstance(scope, ExtractedScope)
        assert scope.population_category == PopulationCategory.CHILDREN

    def test_extract_scope_from_claim(self):
        """extract_scope_from_claim works with claim dict."""
        claim = {
            'statement': "Forest bathing reduced cortisol in healthy adults.",
            'study': {
                'methodology': 'RCT',
                'setting': 'field'
            }
        }
        scope = extract_scope_from_claim(claim)
        assert isinstance(scope, ExtractedScope)
        assert scope.nature_type == "forest"


# =============================================================================
# EDGE CASES
# =============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def setup_method(self):
        self.extractor = ScopeExtractor(use_spacy=False)

    def test_empty_text(self):
        """Empty text should return default scope."""
        scope = self.extractor.extract("")
        assert scope.source == ScopeSource.UNKNOWN

    def test_whitespace_only(self):
        """Whitespace-only text should return default scope."""
        scope = self.extractor.extract("   \n\t  ")
        assert scope.source == ScopeSource.UNKNOWN

    def test_unicode_text(self):
        """Unicode text should be handled."""
        scope = self.extractor.extract("Étude avec des enfants à Paris.")
        # "enfants" won't match English patterns, but shouldn't crash
        assert isinstance(scope, ExtractedScope)

    def test_very_long_text(self):
        """Very long text should still work."""
        long_text = "The study included healthy adults. " * 100
        scope = self.extractor.extract(long_text)
        assert scope.population_category == PopulationCategory.HEALTHY

    def test_multiple_populations(self):
        """Multiple populations should match first."""
        text = "Children and elderly adults participated."
        scope = self.extractor.extract(text)
        # Should match one (first in iteration order)
        assert scope.population_category is not None

    def test_case_insensitive(self):
        """Matching should be case insensitive."""
        scope = self.extractor.extract("HEALTHY VOLUNTEERS from LABORATORY settings")
        assert scope.population_category == PopulationCategory.HEALTHY
        assert scope.setting_category == SettingCategory.LABORATORY


# =============================================================================
# INTEGRATION READINESS TESTS
# =============================================================================

class TestIntegrationReadiness:
    """Test that extractor is ready for integration."""

    def test_scope_has_required_fields(self):
        """Scope should have all fields needed by ScopeConditions."""
        scope = extract_scope("Adults in field study with 30 min exposure.")

        # Required for ScopeConditions integration
        assert hasattr(scope, 'population')
        assert hasattr(scope, 'setting')
        assert hasattr(scope, 'duration')
        assert hasattr(scope, 'generalization_risk')
        assert hasattr(scope, 'explicit_fields')

    def test_scope_serializable(self):
        """Scope should be JSON serializable."""
        import json
        scope = extract_scope("Laboratory study with children.")
        d = scope.to_dict()
        json_str = json.dumps(d)
        assert 'population' in json_str
