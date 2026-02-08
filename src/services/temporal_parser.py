"""
Temporal Expression Parser for Scientific Text
===============================================

Sprint: TD-D (Technical Debt - Temporal Parsing)
Created: February 8, 2026

This module extracts and normalizes temporal expressions from scientific
articles, particularly for CNFA (Cognitive Neuroarchitecture of Flow and Attention)
research where exposure duration is a key moderating variable.

Key capabilities:
1. Duration extraction ("20 minutes", "2 hours", "6-week intervention")
2. Normalization to standard units (minutes for short, days for long)
3. Temporal relation extraction (before, after, during, following)
4. Range handling ("15-30 minutes", "2-4 weeks")
5. Frequency parsing ("twice daily", "3 times per week")

Per P-TD Panel:
- Pustejovsky: TimeML-inspired annotation approach
- Manning: Robust pattern matching with graceful degradation
- Kleinberg: Temporal reasoning for longitudinal studies

Architecture:
-------------
```
Raw Text
    │
    ▼
┌─────────────────┐
│ TemporalParser  │
│ (this module)   │
└─────────────────┘
    │
    ├── DurationExtractor (patterns for time spans)
    ├── FrequencyExtractor (patterns for repetition)
    ├── TemporalRelationExtractor (before/after/during)
    └── TemporalNormalizer (convert to standard units)
    │
    ▼
NormalizedTemporal (minutes, days, or sessions)
```
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any, Union
from enum import Enum
import re
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS AND CONSTANTS
# =============================================================================

class TemporalUnit(Enum):
    """Units for temporal expressions."""
    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"
    SESSIONS = "sessions"  # For repeated exposures
    UNKNOWN = "unknown"


class TemporalRelation(Enum):
    """Temporal relations between events."""
    BEFORE = "before"
    AFTER = "after"
    DURING = "during"
    IMMEDIATELY_BEFORE = "immediately_before"
    IMMEDIATELY_AFTER = "immediately_after"
    CONCURRENT = "concurrent"
    FOLLOWING = "following"
    PRECEDING = "preceding"
    UNKNOWN = "unknown"


class ExposureType(Enum):
    """Type of temporal exposure in CNFA research."""
    ACUTE = "acute"          # Single, short exposure (<1 day)
    SUBACUTE = "subacute"    # Multiple sessions over days
    CHRONIC = "chronic"       # Long-term, weeks to months
    RESIDENTIAL = "residential"  # Based on where you live
    UNKNOWN = "unknown"


# Conversion factors to minutes
UNIT_TO_MINUTES = {
    TemporalUnit.SECONDS: 1/60,
    TemporalUnit.MINUTES: 1,
    TemporalUnit.HOURS: 60,
    TemporalUnit.DAYS: 60 * 24,
    TemporalUnit.WEEKS: 60 * 24 * 7,
    TemporalUnit.MONTHS: 60 * 24 * 30,  # Approximate
    TemporalUnit.YEARS: 60 * 24 * 365,  # Approximate
}

# Word to number mapping
WORD_NUMBERS = {
    'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
    'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
    'ten': 10, 'eleven': 11, 'twelve': 12, 'fifteen': 15,
    'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
    'sixty': 60, 'ninety': 90, 'hundred': 100,
    'a': 1, 'an': 1, 'half': 0.5, 'quarter': 0.25,
    'single': 1, 'brief': 1, 'short': 1,
}

# Unit aliases
UNIT_ALIASES = {
    # Seconds
    'sec': TemporalUnit.SECONDS, 'secs': TemporalUnit.SECONDS,
    'second': TemporalUnit.SECONDS, 'seconds': TemporalUnit.SECONDS,
    's': TemporalUnit.SECONDS,

    # Minutes
    'min': TemporalUnit.MINUTES, 'mins': TemporalUnit.MINUTES,
    'minute': TemporalUnit.MINUTES, 'minutes': TemporalUnit.MINUTES,
    'm': TemporalUnit.MINUTES,

    # Hours
    'hr': TemporalUnit.HOURS, 'hrs': TemporalUnit.HOURS,
    'hour': TemporalUnit.HOURS, 'hours': TemporalUnit.HOURS,
    'h': TemporalUnit.HOURS,

    # Days
    'day': TemporalUnit.DAYS, 'days': TemporalUnit.DAYS,
    'd': TemporalUnit.DAYS,

    # Weeks
    'wk': TemporalUnit.WEEKS, 'wks': TemporalUnit.WEEKS,
    'week': TemporalUnit.WEEKS, 'weeks': TemporalUnit.WEEKS,
    'w': TemporalUnit.WEEKS,

    # Months
    'mo': TemporalUnit.MONTHS, 'mos': TemporalUnit.MONTHS,
    'month': TemporalUnit.MONTHS, 'months': TemporalUnit.MONTHS,

    # Years
    'yr': TemporalUnit.YEARS, 'yrs': TemporalUnit.YEARS,
    'year': TemporalUnit.YEARS, 'years': TemporalUnit.YEARS,
    'y': TemporalUnit.YEARS,

    # Sessions
    'session': TemporalUnit.SESSIONS, 'sessions': TemporalUnit.SESSIONS,
    'visit': TemporalUnit.SESSIONS, 'visits': TemporalUnit.SESSIONS,
    'trial': TemporalUnit.SESSIONS, 'trials': TemporalUnit.SESSIONS,
    'exposure': TemporalUnit.SESSIONS, 'exposures': TemporalUnit.SESSIONS,
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Duration:
    """
    A parsed duration with value, unit, and optional range.
    """
    value: float
    unit: TemporalUnit

    # For ranges like "15-30 minutes"
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    is_range: bool = False

    # Original text
    raw_text: str = ""

    # Confidence in extraction
    confidence: float = 1.0

    def to_minutes(self) -> float:
        """Convert to minutes."""
        if self.unit not in UNIT_TO_MINUTES:
            return 0.0
        return self.value * UNIT_TO_MINUTES[self.unit]

    def to_minutes_range(self) -> Tuple[float, float]:
        """Convert range to minutes."""
        if not self.is_range or self.min_value is None or self.max_value is None:
            mins = self.to_minutes()
            return (mins, mins)

        factor = UNIT_TO_MINUTES.get(self.unit, 1)
        return (self.min_value * factor, self.max_value * factor)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'value': self.value,
            'unit': self.unit.value,
            'minutes': self.to_minutes(),
            'is_range': self.is_range,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'raw_text': self.raw_text,
            'confidence': self.confidence
        }


@dataclass
class Frequency:
    """
    A parsed frequency (e.g., "twice daily", "3 times per week").
    """
    count: float  # Number of occurrences
    per_unit: TemporalUnit  # Per what time period

    raw_text: str = ""
    confidence: float = 1.0

    def sessions_per_week(self) -> float:
        """Normalize to sessions per week."""
        if self.per_unit == TemporalUnit.DAYS:
            return self.count * 7
        elif self.per_unit == TemporalUnit.WEEKS:
            return self.count
        elif self.per_unit == TemporalUnit.MONTHS:
            return self.count / 4.33  # Approximate
        elif self.per_unit == TemporalUnit.HOURS:
            return self.count * 24 * 7
        else:
            return self.count

    def to_dict(self) -> Dict[str, Any]:
        return {
            'count': self.count,
            'per_unit': self.per_unit.value,
            'sessions_per_week': self.sessions_per_week(),
            'raw_text': self.raw_text,
            'confidence': self.confidence
        }


@dataclass
class TemporalExpression:
    """
    A complete temporal expression with duration, frequency, and relations.
    """
    # Core duration
    duration: Optional[Duration] = None

    # Frequency (for repeated exposures)
    frequency: Optional[Frequency] = None

    # Total study duration (e.g., "over 6 weeks")
    study_duration: Optional[Duration] = None

    # Relations to other events
    relations: List[Tuple[TemporalRelation, str]] = field(default_factory=list)

    # Classification
    exposure_type: ExposureType = ExposureType.UNKNOWN

    # Source
    raw_text: str = ""
    source_section: str = ""  # methods, results, etc.

    # Confidence
    confidence: float = 1.0

    def total_exposure_minutes(self) -> Optional[float]:
        """
        Calculate total exposure time if possible.

        For repeated exposures: session_duration × sessions_per_week × weeks
        For single exposures: just the duration
        """
        if self.duration is None:
            return None

        session_mins = self.duration.to_minutes()

        if self.frequency and self.study_duration:
            sessions_per_week = self.frequency.sessions_per_week()
            weeks = self.study_duration.to_minutes() / UNIT_TO_MINUTES[TemporalUnit.WEEKS]
            return session_mins * sessions_per_week * weeks

        return session_mins

    def to_dict(self) -> Dict[str, Any]:
        return {
            'duration': self.duration.to_dict() if self.duration else None,
            'frequency': self.frequency.to_dict() if self.frequency else None,
            'study_duration': self.study_duration.to_dict() if self.study_duration else None,
            'relations': [(r.value, target) for r, target in self.relations],
            'exposure_type': self.exposure_type.value,
            'total_exposure_minutes': self.total_exposure_minutes(),
            'raw_text': self.raw_text,
            'confidence': self.confidence
        }


# =============================================================================
# DURATION PATTERNS
# =============================================================================

# Pattern components
NUMBER_PATTERN = r'(?:\d+(?:\.\d+)?|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|thirty|forty|fifty|sixty|ninety|hundred|half|quarter|a|an)'
UNIT_PATTERN = r'(?:sec(?:ond)?s?|min(?:ute)?s?|hours?|hrs?|days?|weeks?|wks?|months?|mos?|years?|yrs?|sessions?|visits?|trials?|exposures?)'

# Duration patterns (ordered by specificity)
DURATION_PATTERNS = [
    # Range patterns: "15-30 minutes", "2 to 4 hours"
    (
        re.compile(
            rf'({NUMBER_PATTERN})\s*[-–—to]+\s*({NUMBER_PATTERN})\s*({UNIT_PATTERN})',
            re.IGNORECASE
        ),
        'range'
    ),

    # Compound: "1 hour and 30 minutes", "2 hours 15 minutes"
    (
        re.compile(
            rf'({NUMBER_PATTERN})\s*({UNIT_PATTERN})\s*(?:and\s+)?({NUMBER_PATTERN})\s*({UNIT_PATTERN})',
            re.IGNORECASE
        ),
        'compound'
    ),

    # Hyphenated: "20-minute walk", "6-week intervention" (before simple to catch these)
    (
        re.compile(
            rf'({NUMBER_PATTERN})-({UNIT_PATTERN})',
            re.IGNORECASE
        ),
        'hyphenated'
    ),

    # Simple: "20 minutes", "2 hours", "6 weeks"
    (
        re.compile(
            rf'({NUMBER_PATTERN})\s*({UNIT_PATTERN})',
            re.IGNORECASE
        ),
        'simple'
    ),

    # Approximate: "approximately 30 minutes", "about 2 hours"
    (
        re.compile(
            rf'(?:approximately|about|around|roughly|~)\s*({NUMBER_PATTERN})\s*({UNIT_PATTERN})',
            re.IGNORECASE
        ),
        'approximate'
    ),

    # Minimum: "at least 20 minutes", "minimum of 30 minutes"
    (
        re.compile(
            rf'(?:at\s+least|minimum\s+(?:of\s+)?|>\s*)({NUMBER_PATTERN})\s*({UNIT_PATTERN})',
            re.IGNORECASE
        ),
        'minimum'
    ),

    # Maximum: "up to 30 minutes", "maximum of 1 hour"
    (
        re.compile(
            rf'(?:up\s+to|maximum\s+(?:of\s+)?|<\s*)({NUMBER_PATTERN})\s*({UNIT_PATTERN})',
            re.IGNORECASE
        ),
        'maximum'
    ),
]


# =============================================================================
# FREQUENCY PATTERNS
# =============================================================================

FREQUENCY_PATTERNS = [
    # "twice daily", "once per week" - must come before adverb patterns
    (
        re.compile(
            r'(once|twice|thrice)\s+(daily|weekly|monthly|yearly)',
            re.IGNORECASE
        ),
        'multiplier_adverb'
    ),

    # "twice daily", "once per week"
    (
        re.compile(
            r'(once|twice|thrice|(\d+)\s*times?)\s*(?:per|a|each|every)?\s*({UNIT_PATTERN})'.format(UNIT_PATTERN=UNIT_PATTERN),
            re.IGNORECASE
        ),
        'per_unit'
    ),

    # "3 sessions per week", "2 visits weekly"
    (
        re.compile(
            rf'({NUMBER_PATTERN})\s*(?:sessions?|visits?|times?)\s*(?:per|a|each)?\s*({UNIT_PATTERN})',
            re.IGNORECASE
        ),
        'sessions_per'
    ),

    # "daily", "weekly", "monthly" - standalone adverbs
    (
        re.compile(
            r'\b(daily|weekly|monthly|yearly|annually)\b',
            re.IGNORECASE
        ),
        'adverb'
    ),

    # "every day", "every other week"
    (
        re.compile(
            rf'every\s*(other\s+)?({UNIT_PATTERN})',
            re.IGNORECASE
        ),
        'every'
    ),
]


# =============================================================================
# TEMPORAL RELATION PATTERNS
# =============================================================================

RELATION_PATTERNS = [
    (re.compile(r'\b(before)\s+(?:the\s+)?(\w+(?:\s+\w+)?)', re.IGNORECASE), TemporalRelation.BEFORE),
    (re.compile(r'\b(after)\s+(?:the\s+)?(\w+(?:\s+\w+)?)', re.IGNORECASE), TemporalRelation.AFTER),
    (re.compile(r'\b(during)\s+(?:the\s+)?(\w+(?:\s+\w+)?)', re.IGNORECASE), TemporalRelation.DURING),
    (re.compile(r'\b(following)\s+(?:the\s+)?(\w+(?:\s+\w+)?)', re.IGNORECASE), TemporalRelation.FOLLOWING),
    (re.compile(r'\b(preceding)\s+(?:the\s+)?(\w+(?:\s+\w+)?)', re.IGNORECASE), TemporalRelation.PRECEDING),
    (re.compile(r'\bimmediately\s+(before)\s+(?:the\s+)?(\w+(?:\s+\w+)?)', re.IGNORECASE), TemporalRelation.IMMEDIATELY_BEFORE),
    (re.compile(r'\bimmediately\s+(after)\s+(?:the\s+)?(\w+(?:\s+\w+)?)', re.IGNORECASE), TemporalRelation.IMMEDIATELY_AFTER),
    (re.compile(r'\b(while|concurrent\s+with)\s+(?:the\s+)?(\w+(?:\s+\w+)?)', re.IGNORECASE), TemporalRelation.CONCURRENT),
]

# CNFA-specific context patterns
EXPOSURE_CONTEXT_PATTERNS = [
    (re.compile(r'\b(forest\s+)?walk(?:ing|ed)?\b', re.IGNORECASE), 'forest_walk'),
    (re.compile(r'\bview(?:ing|ed)?\s+(?:of\s+)?(?:nature|natural|green)', re.IGNORECASE), 'nature_viewing'),
    (re.compile(r'\bexposure\s+to\s+(?:nature|natural|green)', re.IGNORECASE), 'nature_exposure'),
    (re.compile(r'\btime\s+(?:spent\s+)?(?:in|outdoors?|outside)', re.IGNORECASE), 'outdoor_time'),
    (re.compile(r'\b(?:nature|green\s+space)\s+(?:contact|interaction)', re.IGNORECASE), 'nature_contact'),
    (re.compile(r'\bshinrin-?yoku\b', re.IGNORECASE), 'shinrin_yoku'),
    (re.compile(r'\bforest\s+bath(?:ing)?\b', re.IGNORECASE), 'forest_bathing'),
]


# =============================================================================
# TEMPORAL PARSER
# =============================================================================

class TemporalParser:
    """
    Main parser for temporal expressions in scientific text.

    Usage:
    ```python
    parser = TemporalParser()
    result = parser.parse("Participants walked for 20 minutes in the forest.")
    print(result.duration.to_minutes())  # 20.0
    ```
    """

    def __init__(self, strict_mode: bool = False):
        """
        Initialize parser.

        Args:
            strict_mode: If True, only return high-confidence extractions
        """
        self.strict_mode = strict_mode
        self._confidence_threshold = 0.7 if strict_mode else 0.3

    def parse(self, text: str, source_section: str = "") -> TemporalExpression:
        """
        Parse temporal expressions from text.

        Args:
            text: The text to parse
            source_section: Section of paper (methods, results, etc.)

        Returns:
            TemporalExpression with extracted information
        """
        if not text or not text.strip():
            return TemporalExpression(confidence=0.0)

        text = text.strip()

        # Extract components
        duration = self._extract_duration(text)
        frequency = self._extract_frequency(text)
        study_duration = self._extract_study_duration(text)
        relations = self._extract_relations(text)
        exposure_type = self._classify_exposure_type(duration, frequency, study_duration)

        # Calculate overall confidence
        confidence = self._calculate_confidence(duration, frequency, study_duration)

        # Apply strict mode filter
        if self.strict_mode and confidence < self._confidence_threshold:
            return TemporalExpression(confidence=confidence, raw_text=text)

        return TemporalExpression(
            duration=duration,
            frequency=frequency,
            study_duration=study_duration,
            relations=relations,
            exposure_type=exposure_type,
            raw_text=text,
            source_section=source_section,
            confidence=confidence
        )

    def extract_all_durations(self, text: str) -> List[Duration]:
        """Extract all duration mentions from text."""
        durations = []

        for pattern, pattern_type in DURATION_PATTERNS:
            for match in pattern.finditer(text):
                duration = self._parse_duration_match(match, pattern_type)
                if duration:
                    durations.append(duration)

        # Remove duplicates (overlapping matches)
        return self._deduplicate_durations(durations)

    def extract_exposure_duration(self, text: str) -> Optional[Duration]:
        """
        Extract the primary exposure duration (most relevant for CNFA).

        Prioritizes:
        1. Durations near CNFA-specific context words
        2. Durations in reasonable ranges for exposure (5-180 minutes)
        3. First mentioned duration if no context found
        """
        durations = self.extract_all_durations(text)

        if not durations:
            return None

        # Score each duration by CNFA relevance
        scored = []
        for d in durations:
            score = self._score_exposure_relevance(d, text)
            scored.append((score, d))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1] if scored else None

    def normalize_to_minutes(self, text: str) -> Optional[float]:
        """
        Convenience method: extract and normalize primary duration to minutes.

        Returns None if no duration found.
        """
        duration = self.extract_exposure_duration(text)
        return duration.to_minutes() if duration else None

    def _extract_duration(self, text: str) -> Optional[Duration]:
        """Extract the primary duration from text."""
        for pattern, pattern_type in DURATION_PATTERNS:
            match = pattern.search(text)
            if match:
                return self._parse_duration_match(match, pattern_type)
        return None

    def _parse_duration_match(self, match: re.Match, pattern_type: str) -> Optional[Duration]:
        """Parse a regex match into a Duration object."""
        try:
            groups = match.groups()
            raw_text = match.group(0)

            if pattern_type == 'range':
                min_val = self._parse_number(groups[0])
                max_val = self._parse_number(groups[1])
                unit = self._parse_unit(groups[2])

                return Duration(
                    value=(min_val + max_val) / 2,
                    unit=unit,
                    min_value=min_val,
                    max_value=max_val,
                    is_range=True,
                    raw_text=raw_text,
                    confidence=0.9
                )

            elif pattern_type == 'compound':
                val1 = self._parse_number(groups[0])
                unit1 = self._parse_unit(groups[1])
                val2 = self._parse_number(groups[2])
                unit2 = self._parse_unit(groups[3])

                # Convert to smaller unit
                if unit1 in UNIT_TO_MINUTES and unit2 in UNIT_TO_MINUTES:
                    total_minutes = (val1 * UNIT_TO_MINUTES[unit1] +
                                   val2 * UNIT_TO_MINUTES[unit2])
                    return Duration(
                        value=total_minutes,
                        unit=TemporalUnit.MINUTES,
                        raw_text=raw_text,
                        confidence=0.95
                    )

            elif pattern_type in ('simple', 'hyphenated'):
                value = self._parse_number(groups[0])
                unit = self._parse_unit(groups[1])

                return Duration(
                    value=value,
                    unit=unit,
                    raw_text=raw_text,
                    confidence=0.95 if pattern_type == 'simple' else 0.9
                )

            elif pattern_type == 'approximate':
                value = self._parse_number(groups[0])
                unit = self._parse_unit(groups[1])

                return Duration(
                    value=value,
                    unit=unit,
                    raw_text=raw_text,
                    confidence=0.7  # Lower confidence for approximations
                )

            elif pattern_type == 'minimum':
                value = self._parse_number(groups[0])
                unit = self._parse_unit(groups[1])

                return Duration(
                    value=value,
                    unit=unit,
                    min_value=value,
                    max_value=None,
                    is_range=True,
                    raw_text=raw_text,
                    confidence=0.8
                )

            elif pattern_type == 'maximum':
                value = self._parse_number(groups[0])
                unit = self._parse_unit(groups[1])

                return Duration(
                    value=value,
                    unit=unit,
                    min_value=None,
                    max_value=value,
                    is_range=True,
                    raw_text=raw_text,
                    confidence=0.8
                )

        except (ValueError, IndexError) as e:
            logger.debug(f"Failed to parse duration: {e}")
            return None

        return None

    def _parse_number(self, text: str) -> float:
        """Parse a number from text (numeric or word)."""
        text = text.strip().lower()

        # Try as float first
        try:
            return float(text)
        except ValueError:
            pass

        # Try word lookup
        if text in WORD_NUMBERS:
            return float(WORD_NUMBERS[text])

        # Handle compound words like "twenty-five"
        if '-' in text:
            parts = text.split('-')
            if len(parts) == 2:
                return sum(WORD_NUMBERS.get(p, 0) for p in parts)

        raise ValueError(f"Cannot parse number: {text}")

    def _parse_unit(self, text: str) -> TemporalUnit:
        """Parse a temporal unit from text."""
        text = text.strip().lower()

        # Remove trailing 's' for singular lookup
        singular = text.rstrip('s') if text.endswith('s') and len(text) > 1 else text

        if text in UNIT_ALIASES:
            return UNIT_ALIASES[text]
        if singular in UNIT_ALIASES:
            return UNIT_ALIASES[singular]

        return TemporalUnit.UNKNOWN

    def _extract_frequency(self, text: str) -> Optional[Frequency]:
        """Extract frequency information from text."""
        text_lower = text.lower()

        for pattern, pattern_type in FREQUENCY_PATTERNS:
            match = pattern.search(text)
            if match:
                return self._parse_frequency_match(match, pattern_type)

        return None

    def _parse_frequency_match(self, match: re.Match, pattern_type: str) -> Optional[Frequency]:
        """Parse a regex match into a Frequency object."""
        try:
            groups = match.groups()
            raw_text = match.group(0)

            if pattern_type == 'multiplier_adverb':
                # "twice daily", "once weekly"
                multiplier = groups[0].lower()
                adverb = groups[1].lower()

                if multiplier == 'once':
                    count = 1
                elif multiplier == 'twice':
                    count = 2
                elif multiplier == 'thrice':
                    count = 3
                else:
                    count = 1

                if adverb == 'daily':
                    unit = TemporalUnit.DAYS
                elif adverb == 'weekly':
                    unit = TemporalUnit.WEEKS
                elif adverb == 'monthly':
                    unit = TemporalUnit.MONTHS
                elif adverb in ('yearly', 'annually'):
                    unit = TemporalUnit.YEARS
                else:
                    unit = TemporalUnit.UNKNOWN

                return Frequency(
                    count=count,
                    per_unit=unit,
                    raw_text=raw_text,
                    confidence=0.95
                )

            elif pattern_type == 'per_unit':
                count_text = groups[0].lower()
                if count_text == 'once':
                    count = 1
                elif count_text == 'twice':
                    count = 2
                elif count_text == 'thrice':
                    count = 3
                elif groups[1]:
                    count = float(groups[1])
                else:
                    count = 1

                unit = self._parse_unit(groups[2])

                return Frequency(
                    count=count,
                    per_unit=unit,
                    raw_text=raw_text,
                    confidence=0.9
                )

            elif pattern_type == 'sessions_per':
                count = self._parse_number(groups[0])
                unit = self._parse_unit(groups[1])

                return Frequency(
                    count=count,
                    per_unit=unit,
                    raw_text=raw_text,
                    confidence=0.9
                )

            elif pattern_type == 'adverb':
                adverb = groups[0].lower()
                if adverb == 'daily':
                    return Frequency(1, TemporalUnit.DAYS, raw_text, 0.95)
                elif adverb == 'weekly':
                    return Frequency(1, TemporalUnit.WEEKS, raw_text, 0.95)
                elif adverb == 'monthly':
                    return Frequency(1, TemporalUnit.MONTHS, raw_text, 0.95)
                elif adverb in ('yearly', 'annually'):
                    return Frequency(1, TemporalUnit.YEARS, raw_text, 0.95)

            elif pattern_type == 'every':
                is_other = groups[0] is not None
                unit = self._parse_unit(groups[1])

                count = 0.5 if is_other else 1

                return Frequency(
                    count=count,
                    per_unit=unit,
                    raw_text=raw_text,
                    confidence=0.85
                )

        except (ValueError, IndexError) as e:
            logger.debug(f"Failed to parse frequency: {e}")
            return None

        return None

    def _extract_study_duration(self, text: str) -> Optional[Duration]:
        """
        Extract overall study duration (distinct from session duration).

        Looks for patterns like "over 6 weeks", "for the 8-week study period"
        """
        study_patterns = [
            re.compile(rf'(?:over|across|for|during)\s+(?:a\s+)?({NUMBER_PATTERN})\s*[-–]?\s*({UNIT_PATTERN})\s*(?:period|study|intervention|program)?', re.IGNORECASE),
            re.compile(rf'({NUMBER_PATTERN})\s*[-–]?\s*({UNIT_PATTERN})\s+(?:study|intervention|program|period|trial)', re.IGNORECASE),
            re.compile(rf'(?:study|intervention|program)\s+(?:lasted|duration|period)?\s*(?:of\s+)?({NUMBER_PATTERN})\s*({UNIT_PATTERN})', re.IGNORECASE),
        ]

        for pattern in study_patterns:
            match = pattern.search(text)
            if match:
                groups = match.groups()
                try:
                    value = self._parse_number(groups[0])
                    unit = self._parse_unit(groups[1])

                    # Study durations are typically weeks or months
                    if unit in (TemporalUnit.WEEKS, TemporalUnit.MONTHS, TemporalUnit.DAYS):
                        return Duration(
                            value=value,
                            unit=unit,
                            raw_text=match.group(0),
                            confidence=0.85
                        )
                except (ValueError, IndexError):
                    continue

        return None

    def _extract_relations(self, text: str) -> List[Tuple[TemporalRelation, str]]:
        """Extract temporal relations to other events."""
        relations = []

        for pattern, relation in RELATION_PATTERNS:
            for match in pattern.finditer(text):
                target = match.group(2) if len(match.groups()) >= 2 else ""
                target = target.strip()
                if target and len(target) < 50:  # Sanity check
                    relations.append((relation, target))

        return relations

    def _classify_exposure_type(self, duration: Optional[Duration],
                                 frequency: Optional[Frequency],
                                 study_duration: Optional[Duration]) -> ExposureType:
        """Classify the type of temporal exposure."""
        if duration is None:
            return ExposureType.UNKNOWN

        duration_mins = duration.to_minutes()

        # Check for residential (based on where you live)
        if duration.unit in (TemporalUnit.YEARS, TemporalUnit.MONTHS):
            return ExposureType.RESIDENTIAL

        # Check for chronic (weeks to months with repeated exposure)
        if study_duration:
            study_mins = study_duration.to_minutes()
            if study_mins >= UNIT_TO_MINUTES[TemporalUnit.WEEKS] * 2:  # 2+ weeks
                return ExposureType.CHRONIC

        # Check for subacute (multiple sessions over days)
        if frequency:
            sessions = frequency.sessions_per_week()
            if sessions >= 2:
                return ExposureType.SUBACUTE

        # Default to acute for single short exposures
        if duration_mins < UNIT_TO_MINUTES[TemporalUnit.DAYS]:
            return ExposureType.ACUTE

        return ExposureType.UNKNOWN

    def _calculate_confidence(self, duration: Optional[Duration],
                              frequency: Optional[Frequency],
                              study_duration: Optional[Duration]) -> float:
        """Calculate overall confidence in the temporal extraction."""
        scores = []

        if duration:
            scores.append(duration.confidence)
        if frequency:
            scores.append(frequency.confidence)
        if study_duration:
            scores.append(study_duration.confidence)

        if not scores:
            return 0.0

        return sum(scores) / len(scores)

    def _score_exposure_relevance(self, duration: Duration, text: str) -> float:
        """Score how relevant a duration is for CNFA exposure analysis."""
        score = 0.0

        # Check proximity to CNFA context words
        duration_pos = text.lower().find(duration.raw_text.lower())
        if duration_pos >= 0:
            for pattern, context_type in EXPOSURE_CONTEXT_PATTERNS:
                match = pattern.search(text)
                if match:
                    context_pos = match.start()
                    distance = abs(duration_pos - context_pos)
                    if distance < 100:  # Within ~100 characters
                        score += 2.0 * (1 - distance / 100)

        # Prefer reasonable exposure durations (5-180 minutes)
        mins = duration.to_minutes()
        if 5 <= mins <= 180:
            score += 1.0
        elif 1 <= mins <= 480:  # 1 min to 8 hours
            score += 0.5

        # Prefer higher confidence
        score += duration.confidence

        return score

    def _deduplicate_durations(self, durations: List[Duration]) -> List[Duration]:
        """Remove duplicate/overlapping duration extractions."""
        if not durations:
            return []

        # Sort by position in text (approximate by raw_text)
        unique = []
        seen_texts = set()

        for d in durations:
            normalized = d.raw_text.lower().strip()
            if normalized not in seen_texts:
                seen_texts.add(normalized)
                unique.append(d)

        return unique


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

_default_parser: Optional[TemporalParser] = None


def get_temporal_parser(strict_mode: bool = False) -> TemporalParser:
    """Get or create the default temporal parser."""
    global _default_parser
    if _default_parser is None or _default_parser.strict_mode != strict_mode:
        _default_parser = TemporalParser(strict_mode=strict_mode)
    return _default_parser


def parse_temporal(text: str, source_section: str = "") -> TemporalExpression:
    """
    Parse temporal expressions from text.

    Convenience function using the default parser.
    """
    return get_temporal_parser().parse(text, source_section)


def extract_duration_minutes(text: str) -> Optional[float]:
    """
    Extract and normalize the primary duration to minutes.

    Returns None if no duration found.
    """
    return get_temporal_parser().normalize_to_minutes(text)


def classify_exposure_duration(minutes: float) -> ExposureType:
    """
    Classify an exposure duration by type.

    Args:
        minutes: Duration in minutes

    Returns:
        ExposureType classification
    """
    if minutes < 60 * 24:  # Less than a day
        return ExposureType.ACUTE
    elif minutes < 60 * 24 * 7:  # Less than a week
        return ExposureType.SUBACUTE
    elif minutes < 60 * 24 * 30:  # Less than a month
        return ExposureType.CHRONIC
    else:
        return ExposureType.RESIDENTIAL
