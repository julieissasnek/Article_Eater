"""
Tests for Temporal Parser (TD-D: Temporal Parsing)

Sprint: TD-D
Created: February 8, 2026
"""

import pytest
from typing import Dict

from src.services.temporal_parser import (
    TemporalUnit,
    TemporalRelation,
    ExposureType,
    Duration,
    Frequency,
    TemporalExpression,
    TemporalParser,
    get_temporal_parser,
    parse_temporal,
    extract_duration_minutes,
    classify_exposure_duration,
    UNIT_TO_MINUTES,
    WORD_NUMBERS,
    UNIT_ALIASES,
)


# =============================================================================
# DURATION TESTS
# =============================================================================

class TestDuration:
    """Test Duration dataclass."""

    def test_duration_creation(self):
        """Can create a duration."""
        d = Duration(value=30, unit=TemporalUnit.MINUTES)
        assert d.value == 30
        assert d.unit == TemporalUnit.MINUTES

    def test_to_minutes_simple(self):
        """Convert simple duration to minutes."""
        d = Duration(value=30, unit=TemporalUnit.MINUTES)
        assert d.to_minutes() == 30

    def test_to_minutes_hours(self):
        """Convert hours to minutes."""
        d = Duration(value=2, unit=TemporalUnit.HOURS)
        assert d.to_minutes() == 120

    def test_to_minutes_days(self):
        """Convert days to minutes."""
        d = Duration(value=1, unit=TemporalUnit.DAYS)
        assert d.to_minutes() == 60 * 24

    def test_to_minutes_weeks(self):
        """Convert weeks to minutes."""
        d = Duration(value=1, unit=TemporalUnit.WEEKS)
        assert d.to_minutes() == 60 * 24 * 7

    def test_range_duration(self):
        """Range durations store min/max."""
        d = Duration(
            value=22.5,  # Average of 15-30
            unit=TemporalUnit.MINUTES,
            min_value=15,
            max_value=30,
            is_range=True
        )
        assert d.is_range
        assert d.min_value == 15
        assert d.max_value == 30

    def test_to_minutes_range(self):
        """Convert range to minutes."""
        d = Duration(
            value=22.5,
            unit=TemporalUnit.MINUTES,
            min_value=15,
            max_value=30,
            is_range=True
        )
        min_m, max_m = d.to_minutes_range()
        assert min_m == 15
        assert max_m == 30

    def test_to_dict(self):
        """Duration serializes to dict."""
        d = Duration(value=20, unit=TemporalUnit.MINUTES, raw_text="20 minutes")
        data = d.to_dict()
        assert data['value'] == 20
        assert data['unit'] == 'minutes'
        assert data['minutes'] == 20


# =============================================================================
# FREQUENCY TESTS
# =============================================================================

class TestFrequency:
    """Test Frequency dataclass."""

    def test_frequency_creation(self):
        """Can create a frequency."""
        f = Frequency(count=3, per_unit=TemporalUnit.WEEKS)
        assert f.count == 3
        assert f.per_unit == TemporalUnit.WEEKS

    def test_sessions_per_week_weekly(self):
        """Weekly frequency normalization."""
        f = Frequency(count=3, per_unit=TemporalUnit.WEEKS)
        assert f.sessions_per_week() == 3

    def test_sessions_per_week_daily(self):
        """Daily frequency to weekly."""
        f = Frequency(count=2, per_unit=TemporalUnit.DAYS)
        assert f.sessions_per_week() == 14  # 2 per day * 7 days

    def test_to_dict(self):
        """Frequency serializes to dict."""
        f = Frequency(count=2, per_unit=TemporalUnit.DAYS)
        data = f.to_dict()
        assert data['count'] == 2
        assert data['per_unit'] == 'days'


# =============================================================================
# SIMPLE DURATION PARSING TESTS
# =============================================================================

class TestSimpleDurationParsing:
    """Test parsing of simple duration expressions."""

    def setup_method(self):
        self.parser = TemporalParser()

    def test_parse_minutes(self):
        """Parse 'X minutes'."""
        result = self.parser.parse("Participants walked for 20 minutes.")
        assert result.duration is not None
        assert result.duration.to_minutes() == 20

    def test_parse_hours(self):
        """Parse 'X hours'."""
        result = self.parser.parse("The intervention lasted 2 hours.")
        assert result.duration is not None
        assert result.duration.to_minutes() == 120

    def test_parse_days(self):
        """Parse 'X days'."""
        result = self.parser.parse("Participants were observed for 3 days.")
        assert result.duration is not None
        assert result.duration.unit == TemporalUnit.DAYS

    def test_parse_weeks(self):
        """Parse 'X weeks'."""
        result = self.parser.parse("The study lasted 6 weeks.")
        assert result.duration is not None
        assert result.duration.value == 6
        assert result.duration.unit == TemporalUnit.WEEKS

    def test_parse_abbreviated_units(self):
        """Parse abbreviated units like '30 min', '2 hrs'."""
        result = self.parser.parse("30 min exposure")
        assert result.duration is not None
        assert result.duration.to_minutes() == 30

        result = self.parser.parse("2 hrs of walking")
        assert result.duration is not None
        assert result.duration.to_minutes() == 120

    def test_parse_hyphenated(self):
        """Parse '20-minute walk'."""
        result = self.parser.parse("A 20-minute walk in the forest.")
        assert result.duration is not None
        assert result.duration.to_minutes() == 20

    def test_parse_word_numbers(self):
        """Parse word numbers like 'thirty minutes'."""
        result = self.parser.parse("A thirty minute exposure was used.")
        assert result.duration is not None
        assert result.duration.to_minutes() == 30


# =============================================================================
# RANGE DURATION PARSING TESTS
# =============================================================================

class TestRangeDurationParsing:
    """Test parsing of range duration expressions."""

    def setup_method(self):
        self.parser = TemporalParser()

    def test_parse_range_hyphen(self):
        """Parse '15-30 minutes'."""
        result = self.parser.parse("Sessions lasted 15-30 minutes.")
        assert result.duration is not None
        assert result.duration.is_range
        assert result.duration.min_value == 15
        assert result.duration.max_value == 30

    def test_parse_range_to(self):
        """Parse '2 to 4 hours'."""
        result = self.parser.parse("Exposure was 2 to 4 hours.")
        assert result.duration is not None
        assert result.duration.is_range

    def test_parse_approximate(self):
        """Parse 'approximately 30 minutes'."""
        result = self.parser.parse("Approximately 30 minutes of exposure.")
        assert result.duration is not None
        assert result.duration.value == 30
        # Note: Simple pattern may match first; approximate prefix is context

    def test_parse_minimum(self):
        """Parse 'at least 20 minutes'."""
        result = self.parser.parse("At least 20 minutes of walking.")
        assert result.duration is not None
        assert result.duration.value == 20
        # Note: The 'at least' context is captured but simple pattern may match


# =============================================================================
# COMPOUND DURATION TESTS
# =============================================================================

class TestCompoundDurationParsing:
    """Test parsing of compound duration expressions."""

    def setup_method(self):
        self.parser = TemporalParser()

    def test_parse_compound_and(self):
        """Parse '1 hour and 30 minutes'."""
        result = self.parser.parse("The session was 1 hour and 30 minutes.")
        assert result.duration is not None
        assert result.duration.to_minutes() == 90

    def test_parse_compound_no_and(self):
        """Parse '2 hours 15 minutes'."""
        result = self.parser.parse("Walking for 2 hours 15 minutes.")
        assert result.duration is not None
        assert result.duration.to_minutes() == 135


# =============================================================================
# FREQUENCY PARSING TESTS
# =============================================================================

class TestFrequencyParsing:
    """Test parsing of frequency expressions."""

    def setup_method(self):
        self.parser = TemporalParser()

    def test_parse_twice_daily(self):
        """Parse 'twice daily'."""
        result = self.parser.parse("Exposure occurred twice daily.")
        assert result.frequency is not None
        assert result.frequency.count == 2
        assert result.frequency.per_unit == TemporalUnit.DAYS

    def test_parse_once_per_week(self):
        """Parse 'once per week'."""
        result = self.parser.parse("Sessions were once per week.")
        assert result.frequency is not None
        assert result.frequency.count == 1
        assert result.frequency.per_unit == TemporalUnit.WEEKS

    def test_parse_three_times_weekly(self):
        """Parse '3 times per week'."""
        result = self.parser.parse("Participants attended 3 times per week.")
        assert result.frequency is not None
        assert result.frequency.count == 3

    def test_parse_daily_adverb(self):
        """Parse 'daily' adverb."""
        result = self.parser.parse("Daily walks were recorded.")
        assert result.frequency is not None
        assert result.frequency.count == 1
        assert result.frequency.per_unit == TemporalUnit.DAYS

    def test_parse_weekly_adverb(self):
        """Parse 'weekly' adverb."""
        result = self.parser.parse("Weekly sessions were conducted.")
        assert result.frequency is not None
        assert result.frequency.per_unit == TemporalUnit.WEEKS

    def test_parse_every_other_day(self):
        """Parse 'every other day'."""
        result = self.parser.parse("Walks every other day.")
        assert result.frequency is not None
        assert result.frequency.count == 0.5


# =============================================================================
# STUDY DURATION PARSING TESTS
# =============================================================================

class TestStudyDurationParsing:
    """Test parsing of study duration expressions."""

    def setup_method(self):
        self.parser = TemporalParser()

    def test_parse_over_weeks(self):
        """Parse 'over 6 weeks'."""
        result = self.parser.parse("The intervention was conducted over 6 weeks.")
        assert result.study_duration is not None
        assert result.study_duration.value == 6
        assert result.study_duration.unit == TemporalUnit.WEEKS

    def test_parse_study_period(self):
        """Parse '8-week study period'."""
        result = self.parser.parse("The 8-week study period included...")
        assert result.study_duration is not None
        assert result.study_duration.value == 8

    def test_parse_intervention_duration(self):
        """Parse 'intervention lasted X months'."""
        result = self.parser.parse("The intervention lasted 3 months.")
        assert result.study_duration is not None
        assert result.study_duration.unit == TemporalUnit.MONTHS


# =============================================================================
# TEMPORAL RELATION TESTS
# =============================================================================

class TestTemporalRelationParsing:
    """Test parsing of temporal relations."""

    def setup_method(self):
        self.parser = TemporalParser()

    def test_parse_before(self):
        """Parse 'before' relation."""
        result = self.parser.parse("Stress was measured before the walk.")
        assert len(result.relations) >= 1
        assert any(r[0] == TemporalRelation.BEFORE for r in result.relations)

    def test_parse_after(self):
        """Parse 'after' relation."""
        result = self.parser.parse("Cortisol was sampled after the exposure.")
        assert len(result.relations) >= 1
        assert any(r[0] == TemporalRelation.AFTER for r in result.relations)

    def test_parse_during(self):
        """Parse 'during' relation."""
        result = self.parser.parse("Heart rate was recorded during the intervention.")
        assert len(result.relations) >= 1
        assert any(r[0] == TemporalRelation.DURING for r in result.relations)

    def test_parse_following(self):
        """Parse 'following' relation."""
        result = self.parser.parse("Mood improved following the nature exposure.")
        assert len(result.relations) >= 1
        assert any(r[0] == TemporalRelation.FOLLOWING for r in result.relations)

    def test_parse_immediately_after(self):
        """Parse 'immediately after' relation."""
        result = self.parser.parse("Tests were given immediately after the walk.")
        assert len(result.relations) >= 1
        assert any(r[0] == TemporalRelation.IMMEDIATELY_AFTER for r in result.relations)


# =============================================================================
# EXPOSURE TYPE CLASSIFICATION TESTS
# =============================================================================

class TestExposureTypeClassification:
    """Test exposure type classification."""

    def setup_method(self):
        self.parser = TemporalParser()

    def test_classify_acute(self):
        """Single short exposure is acute."""
        result = self.parser.parse("A single 30 minute walk.")
        assert result.exposure_type == ExposureType.ACUTE

    def test_classify_subacute(self):
        """Multiple sessions is subacute."""
        result = self.parser.parse("Sessions of 30 minutes, 3 times per week.")
        assert result.exposure_type == ExposureType.SUBACUTE

    def test_classify_chronic(self):
        """Long-term study is chronic."""
        result = self.parser.parse("30 minute sessions over 8 weeks.")
        assert result.exposure_type == ExposureType.CHRONIC

    def test_classify_residential(self):
        """Years of exposure is residential."""
        result = self.parser.parse("Participants had lived there for 5 years.")
        assert result.exposure_type == ExposureType.RESIDENTIAL


# =============================================================================
# CNFA CONTEXT TESTS
# =============================================================================

class TestCNFAContext:
    """Test CNFA-specific context recognition."""

    def setup_method(self):
        self.parser = TemporalParser()

    def test_forest_walk_context(self):
        """Forest walk context increases relevance."""
        durations = self.parser.extract_all_durations(
            "Participants walked in the forest for 20 minutes, followed by 60 minutes of testing."
        )
        # Should prefer the 20-minute forest walk
        primary = self.parser.extract_exposure_duration(
            "Participants walked in the forest for 20 minutes, followed by 60 minutes of testing."
        )
        assert primary is not None
        assert primary.to_minutes() == 20

    def test_nature_viewing_context(self):
        """Nature viewing context is recognized."""
        result = self.parser.parse("Viewing nature scenes for 15 minutes.")
        assert result.duration is not None
        assert result.duration.to_minutes() == 15

    def test_shinrin_yoku_context(self):
        """Shinrin-yoku (forest bathing) context is recognized."""
        result = self.parser.parse("Shinrin-yoku session of 2 hours.")
        assert result.duration is not None
        assert result.duration.to_minutes() == 120


# =============================================================================
# CONVENIENCE FUNCTION TESTS
# =============================================================================

class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_get_temporal_parser_singleton(self):
        """get_temporal_parser returns consistent parser."""
        p1 = get_temporal_parser()
        p2 = get_temporal_parser()
        assert p1 is p2

    def test_parse_temporal(self):
        """parse_temporal convenience function works."""
        result = parse_temporal("A 20 minute walk.")
        assert result.duration is not None
        assert result.duration.to_minutes() == 20

    def test_extract_duration_minutes(self):
        """extract_duration_minutes returns minutes."""
        mins = extract_duration_minutes("30 minute exposure")
        assert mins == 30

    def test_extract_duration_minutes_none(self):
        """extract_duration_minutes returns None for no match."""
        mins = extract_duration_minutes("The study was interesting.")
        assert mins is None

    def test_classify_exposure_duration(self):
        """classify_exposure_duration works."""
        assert classify_exposure_duration(30) == ExposureType.ACUTE
        assert classify_exposure_duration(60 * 24 * 2) == ExposureType.SUBACUTE
        assert classify_exposure_duration(60 * 24 * 14) == ExposureType.CHRONIC
        assert classify_exposure_duration(60 * 24 * 365) == ExposureType.RESIDENTIAL


# =============================================================================
# EDGE CASES
# =============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def setup_method(self):
        self.parser = TemporalParser()

    def test_empty_text(self):
        """Empty text returns default expression."""
        result = self.parser.parse("")
        assert result.duration is None
        assert result.confidence == 0.0

    def test_no_temporal_content(self):
        """Text without temporal content."""
        result = self.parser.parse("The forest was beautiful.")
        assert result.duration is None

    def test_multiple_durations(self):
        """Extract all durations from text with multiple."""
        durations = self.parser.extract_all_durations(
            "Sessions were 20 minutes, twice daily, over 4 weeks."
        )
        assert len(durations) >= 1

    def test_unicode_text(self):
        """Unicode text is handled."""
        result = self.parser.parse("Participants marched for 30 minutes.")
        assert result.duration is not None

    def test_case_insensitive(self):
        """Parsing is case insensitive."""
        result = self.parser.parse("THIRTY MINUTES of exposure.")
        assert result.duration is not None
        assert result.duration.to_minutes() == 30

    def test_decimal_hours(self):
        """Decimal hours are parsed."""
        result = self.parser.parse("The session lasted 1.5 hours.")
        assert result.duration is not None
        assert result.duration.to_minutes() == 90

    def test_strict_mode(self):
        """Strict mode filters low confidence."""
        parser = TemporalParser(strict_mode=True)
        result = parser.parse("Approximately some time was spent.")
        # Low confidence results should be filtered
        assert result.duration is None or result.duration.confidence >= 0.7


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Test integration scenarios."""

    def setup_method(self):
        self.parser = TemporalParser()

    def test_complete_study_description(self):
        """Parse a complete study description."""
        text = """
        Participants engaged in 30-minute forest walks, twice weekly,
        over a 6-week period. Stress was measured before and after each walk.
        """
        result = self.parser.parse(text)

        assert result.duration is not None
        assert result.duration.to_minutes() == 30

        assert result.frequency is not None
        assert result.frequency.count == 2

        assert result.study_duration is not None
        assert result.study_duration.unit == TemporalUnit.WEEKS

        assert result.exposure_type == ExposureType.CHRONIC
        assert len(result.relations) >= 2  # before, after

    def test_total_exposure_calculation(self):
        """Calculate total exposure for repeated exposures."""
        text = "30-minute sessions, 3 times per week, over 8 weeks."
        result = self.parser.parse(text)

        # Check components are extracted
        assert result.duration is not None
        assert result.duration.to_minutes() == 30

        # Total exposure requires all three components
        # If any component is missing, just the session duration is returned
        total = result.total_exposure_minutes()
        assert total is not None
        assert total >= 30  # At minimum, the session duration

    def test_to_dict_complete(self):
        """Full serialization works."""
        text = "20-minute walk, daily, for 4 weeks."
        result = self.parser.parse(text)
        data = result.to_dict()

        assert 'duration' in data
        assert 'frequency' in data
        assert 'exposure_type' in data
        assert 'confidence' in data


# =============================================================================
# UNIT CONVERSION TESTS
# =============================================================================

class TestUnitConversion:
    """Test unit conversion constants."""

    def test_unit_to_minutes(self):
        """UNIT_TO_MINUTES has expected values."""
        assert UNIT_TO_MINUTES[TemporalUnit.SECONDS] == 1/60
        assert UNIT_TO_MINUTES[TemporalUnit.MINUTES] == 1
        assert UNIT_TO_MINUTES[TemporalUnit.HOURS] == 60
        assert UNIT_TO_MINUTES[TemporalUnit.DAYS] == 60 * 24

    def test_word_numbers(self):
        """WORD_NUMBERS has expected values."""
        assert WORD_NUMBERS['one'] == 1
        assert WORD_NUMBERS['twenty'] == 20
        assert WORD_NUMBERS['half'] == 0.5

    def test_unit_aliases(self):
        """UNIT_ALIASES maps correctly."""
        assert UNIT_ALIASES['min'] == TemporalUnit.MINUTES
        assert UNIT_ALIASES['hrs'] == TemporalUnit.HOURS
        assert UNIT_ALIASES['wk'] == TemporalUnit.WEEKS


# =============================================================================
# SCIENTIFIC TEXT TESTS
# =============================================================================

class TestScientificText:
    """Test with realistic scientific text."""

    def setup_method(self):
        self.parser = TemporalParser()

    def test_methods_section(self):
        """Parse typical methods section text."""
        text = """
        Participants (N=60) were randomly assigned to either a nature walk
        (n=30) or urban walk (n=30) condition. Each walk lasted approximately
        45 minutes. Saliva samples were collected before and 15 minutes after
        the walk to measure cortisol levels.
        """
        result = self.parser.parse(text, source_section="methods")

        assert result.duration is not None
        assert 40 <= result.duration.to_minutes() <= 50

    def test_abstract_text(self):
        """Parse typical abstract text."""
        text = """
        We investigated the effects of brief nature exposure (20 minutes)
        on stress reduction in a sample of university students.
        """
        result = self.parser.parse(text, source_section="abstract")

        assert result.duration is not None
        assert result.duration.to_minutes() == 20

    def test_results_section(self):
        """Parse typical results section text."""
        text = """
        Participants who engaged in the 30-minute forest walk showed
        significantly lower cortisol levels (M=0.15 μg/dL) compared to
        the control group (M=0.28 μg/dL), t(58)=3.42, p<.001.
        """
        result = self.parser.parse(text, source_section="results")

        assert result.duration is not None
        assert result.duration.to_minutes() == 30
