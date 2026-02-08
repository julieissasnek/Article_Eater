"""
Scope Extractor: Extract scope conditions from scientific text.

Sprint: TD-B (Scope Extraction)
Panel: P-TD (Technical Debt)
Created: February 8, 2026

This module extracts scope conditions (population, setting, duration, etc.)
from scientific paper text. It uses pattern matching and NER to identify
the conditions under which findings apply.

Key insight from Dr. Nancy Cartwright (P-TD Panel):
"Scope conditions are everything for scientific claims. A finding without
scope is an abstraction—potentially useful, but not directly applicable."

Target: 80% recall on critical scope dimensions
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set
from enum import Enum
import logging
import re

logger = logging.getLogger(__name__)

# =============================================================================
# OPTIONAL: TEMPORAL PARSER (TD-D Integration)
# =============================================================================
# The temporal parser provides enhanced duration extraction with normalization,
# range handling, and frequency parsing. Import is optional for fallback.

try:
    from src.services.temporal_parser import (
        TemporalParser,
        extract_duration_minutes,
        ExposureType,
    )
    TEMPORAL_PARSER_AVAILABLE = True
except ImportError:
    TEMPORAL_PARSER_AVAILABLE = False
    TemporalParser = None


# =============================================================================
# SCOPE DIMENSION DEFINITIONS
# =============================================================================

class ScopeSource(Enum):
    """How scope information was obtained."""
    EXPLICIT = "explicit"      # Stated directly in text
    INFERRED = "inferred"      # Inferred from context
    DEFAULT = "default"        # Default assumption
    UNKNOWN = "unknown"        # Could not determine


class PopulationCategory(Enum):
    """Population age/demographic categories."""
    CHILDREN = "children"          # < 12 years
    ADOLESCENTS = "adolescents"    # 12-17 years
    YOUNG_ADULTS = "young_adults"  # 18-30 years
    ADULTS = "adults"              # 18-65 years (general)
    MIDDLE_AGED = "middle_aged"    # 40-65 years
    ELDERLY = "elderly"            # > 65 years
    CLINICAL = "clinical"          # Clinical population
    HEALTHY = "healthy"            # Healthy population
    MIXED = "mixed"                # Mixed population
    UNKNOWN = "unknown"


class SettingCategory(Enum):
    """Study setting categories."""
    LABORATORY = "laboratory"
    FIELD = "field"
    SIMULATED = "simulated"       # VR, photos, videos
    URBAN = "urban"
    RURAL = "rural"
    HOSPITAL = "hospital"
    SCHOOL = "school"
    WORKPLACE = "workplace"
    RESIDENTIAL = "residential"
    UNKNOWN = "unknown"


class DurationCategory(Enum):
    """Exposure duration categories."""
    ACUTE = "acute"              # Single brief exposure (< 1 hour)
    SHORT_TERM = "short_term"    # Single session (1-4 hours)
    REPEATED = "repeated"        # Multiple sessions
    CHRONIC = "chronic"          # Long-term regular exposure
    UNKNOWN = "unknown"


# =============================================================================
# PATTERN DEFINITIONS
# =============================================================================

# Population patterns
POPULATION_PATTERNS: Dict[PopulationCategory, List[str]] = {
    PopulationCategory.CHILDREN: [
        r'\bchildren\b', r'\bchild\b', r'\bpediatric\b', r'\bminor[s]?\b',
        r'\bkids?\b', r'\baged?\s*[3-9]\s*(?:to|-)\s*1[0-2]\b',
        r'\b(?:elementary|primary)\s*school\b'
    ],
    PopulationCategory.ADOLESCENTS: [
        r'\badolescent[s]?\b', r'\bteen(?:ager)?s?\b', r'\byouth\b',
        r'\baged?\s*1[2-7]\s*(?:to|-)\s*1[7-9]\b', r'\bhigh\s*school\b'
    ],
    PopulationCategory.YOUNG_ADULTS: [
        r'\byoung\s*adult[s]?\b', r'\bcollege\s*student[s]?\b',
        r'\bundergraduate[s]?\b', r'\buniversity\s*student[s]?\b',
        r'\baged?\s*1[8-9]\s*(?:to|-)\s*[23][0-5]\b'
    ],
    PopulationCategory.ELDERLY: [
        r'\belderly\b', r'\bolder\s*adult[s]?\b', r'\bsenior[s]?\b',
        r'\baged?\s*(?:over|above|>)\s*6[05]\b', r'\b(?:6[5-9]|[789]\d)\s*years?\b',
        r'\bgeriatric\b', r'\baging\b'
    ],
    PopulationCategory.CLINICAL: [
        r'\bpatient[s]?\b', r'\bclinical\b', r'\bdiagnos(?:ed|is)\b',
        r'\bdepression\b', r'\banxiety\b', r'\bADHD\b', r'\bdementia\b',
        r'\bAlzheimer\b', r'\bschizophreni[ac]\b', r'\bpsychiatric\b'
    ],
    PopulationCategory.HEALTHY: [
        r'\bhealthy\b', r'\bnon-?clinical\b', r'\bgeneral\s*population\b',
        r'\bcommunity\s*sample\b', r'\bvolunteer[s]?\b'
    ],
}

# Setting patterns
SETTING_PATTERNS: Dict[SettingCategory, List[str]] = {
    SettingCategory.LABORATORY: [
        r'\blaboratory\b', r'\blab\b', r'\bcontrolled\s*(?:setting|environment)\b',
        r'\bexperimental\s*room\b'
    ],
    SettingCategory.FIELD: [
        r'\bfield\s*(?:study|experiment|setting)\b', r'\breal-?world\b',
        r'\bnaturalistic\b', r'\bin\s*situ\b', r'\bnatural\s*setting\b'
    ],
    SettingCategory.SIMULATED: [
        r'\bvirtual\s*reality\b', r'\bVR\b', r'\bvideo[s]?\b',
        r'\bphoto(?:graph)?s?\b', r'\bimage[s]?\b', r'\bsimulated\b',
        r'\bdigital\b', r'\bscreen\b'
    ],
    SettingCategory.URBAN: [
        r'\burban\b', r'\bcity\b', r'\bmetropolitan\b', r'\bdowntown\b'
    ],
    SettingCategory.RURAL: [
        r'\brural\b', r'\bcountryside\b', r'\bvillage\b', r'\bfarmland\b'
    ],
    SettingCategory.HOSPITAL: [
        r'\bhospital\b', r'\bclinic\b', r'\bmedical\s*center\b',
        r'\bhealthcare\s*(?:facility|setting)\b', r'\bward\b'
    ],
    SettingCategory.SCHOOL: [
        r'\bschool\b', r'\bclassroom\b', r'\beducational\b',
        r'\buniversity\b', r'\bcampus\b'
    ],
    SettingCategory.WORKPLACE: [
        r'\bworkplace\b', r'\boffice\b', r'\bwork\s*environment\b',
        r'\boccupational\b'
    ],
}

# Duration patterns (with time extraction)
DURATION_PATTERNS: Dict[DurationCategory, List[str]] = {
    DurationCategory.ACUTE: [
        r'\b(?:single|one|brief)\s*(?:exposure|session|visit)\b',
        r'\b(?:5|10|15|20|30)\s*minutes?\b',
        r'\bacute\b'
    ],
    DurationCategory.SHORT_TERM: [
        r'\b(?:1|2|3|4)\s*hours?\b', r'\bhalf\s*(?:an?\s*)?hour\b',
        r'\b(?:60|90|120)\s*minutes?\b'
    ],
    DurationCategory.REPEATED: [
        r'\b(?:multiple|repeated|several)\s*(?:sessions?|exposures?|visits?)\b',
        r'\b(?:twice|three\s*times?)\s*(?:a|per)\s*week\b',
        r'\bweekly\b', r'\bdaily\b'
    ],
    DurationCategory.CHRONIC: [
        r'\blong-?term\b', r'\bchronic\b', r'\bextended\b',
        r'\b(?:weeks?|months?|years?)\s*of\s*exposure\b',
        r'\bresidential\s*(?:exposure|proximity)\b'
    ],
}

# Nature type patterns (CNFA-specific)
NATURE_TYPE_PATTERNS: Dict[str, List[str]] = {
    "forest": [r'\bforest\b', r'\bwoods?\b', r'\bwoodland\b', r'\btree[s]?\b'],
    "park": [r'\bpark\b', r'\bgreen\s*space\b', r'\bgreenspace\b', r'\bgarden\b'],
    "water": [r'\bwater\b', r'\blake\b', r'\bocean\b', r'\briver\b', r'\bstream\b', r'\bcoast\b'],
    "indoor_plants": [r'\bindoor\s*plant[s]?\b', r'\bpotted\s*plant[s]?\b', r'\bplant[s]?\s*(?:in|inside)\b'],
    "view": [r'\bview\b', r'\bwindow\b', r'\bvisual\s*access\b'],
    "urban_green": [r'\burban\s*(?:green|nature|park)\b', r'\bstreet\s*tree[s]?\b'],
}

# Temporal measurement patterns
MEASUREMENT_TIMING_PATTERNS: Dict[str, List[str]] = {
    "immediate": [
        r'\bimmediately\b', r'\bright\s*after\b', r'\bpost-?exposure\b',
        r'\bimmediately\s*(?:after|following)\b'
    ],
    "short_delay": [
        r'\b(?:5|10|15|30)\s*minutes?\s*(?:after|later|post)\b',
        r'\bhalf\s*(?:an?\s*)?hour\s*(?:after|later)\b'
    ],
    "long_delay": [
        r'\b(?:1|2|3|24)\s*hours?\s*(?:after|later|post)\b',
        r'\bthe\s*(?:next|following)\s*day\b',
        r'\bfollow-?up\b'
    ],
}


# =============================================================================
# SCOPE EXTRACTION RESULT
# =============================================================================

@dataclass
class ExtractedScope:
    """Result of scope extraction from text."""
    # Core dimensions
    population: Optional[str] = None
    population_category: Optional[PopulationCategory] = None
    setting: Optional[str] = None
    setting_category: Optional[SettingCategory] = None
    duration: Optional[str] = None
    duration_category: Optional[DurationCategory] = None
    duration_minutes: Optional[int] = None  # Normalized duration

    # CNFA-specific
    nature_type: Optional[str] = None
    measurement_timing: Optional[str] = None

    # Geography
    geography: Optional[str] = None
    country: Optional[str] = None

    # Methodology
    methodology: Optional[str] = None  # RCT, observational, etc.

    # Source tracking
    source: ScopeSource = ScopeSource.UNKNOWN
    explicit_fields: Set[str] = field(default_factory=set)
    inferred_fields: Set[str] = field(default_factory=set)

    # Confidence and coverage
    extraction_confidence: float = 0.0
    generalization_risk: float = 0.5  # Higher = more risk in generalizing

    # Raw matches for debugging
    matches: Dict[str, List[str]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'population': self.population,
            'population_category': self.population_category.value if self.population_category else None,
            'setting': self.setting,
            'setting_category': self.setting_category.value if self.setting_category else None,
            'duration': self.duration,
            'duration_category': self.duration_category.value if self.duration_category else None,
            'duration_minutes': self.duration_minutes,
            'nature_type': self.nature_type,
            'measurement_timing': self.measurement_timing,
            'geography': self.geography,
            'country': self.country,
            'methodology': self.methodology,
            'source': self.source.value,
            'explicit_fields': list(self.explicit_fields),
            'inferred_fields': list(self.inferred_fields),
            'extraction_confidence': self.extraction_confidence,
            'generalization_risk': self.generalization_risk,
        }


# =============================================================================
# SCOPE EXTRACTOR
# =============================================================================

class ScopeExtractor:
    """
    Extracts scope conditions from scientific text.

    Uses pattern matching (with optional spaCy NER) to identify:
    - Population characteristics (age, health status)
    - Study setting (lab, field, simulated)
    - Exposure duration
    - Nature type (forest, park, indoor plants)
    - Measurement timing
    - Geography
    """

    def __init__(self, use_spacy: bool = True, use_temporal_parser: bool = True):
        """
        Initialize the extractor.

        Args:
            use_spacy: Whether to use spaCy for NER (geography, etc.)
            use_temporal_parser: Whether to use enhanced temporal parsing (TD-D)
        """
        self.use_spacy = use_spacy
        self._nlp = None
        self._spacy_available = False

        # TD-D: Initialize temporal parser for enhanced duration extraction
        self._temporal_parser = None
        if use_temporal_parser and TEMPORAL_PARSER_AVAILABLE:
            try:
                self._temporal_parser = TemporalParser()
            except Exception as e:
                logger.debug(f"Could not initialize temporal parser: {e}")

        if use_spacy:
            self._init_spacy()

    def _init_spacy(self):
        """Initialize spaCy model."""
        try:
            import spacy
            try:
                self._nlp = spacy.load("en_core_web_sm")
                self._spacy_available = True
                logger.info("spaCy loaded successfully")
            except OSError:
                logger.warning("spaCy model 'en_core_web_sm' not found. "
                             "Run: python -m spacy download en_core_web_sm")
                self._spacy_available = False
        except ImportError:
            logger.warning("spaCy not installed, using pattern matching only")
            self._spacy_available = False

    def _extract_with_patterns(
        self,
        text: str,
        patterns: Dict[Any, List[str]]
    ) -> Tuple[Optional[Any], List[str]]:
        """
        Extract category using regex patterns.

        Returns:
            Tuple of (matched_category, list_of_matched_strings)
        """
        text_lower = text.lower()
        matches = []

        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                found = re.findall(pattern, text_lower, re.IGNORECASE)
                if found:
                    matches.extend(found)
                    return category, matches

        return None, matches

    def _extract_population(self, text: str) -> Tuple[Optional[PopulationCategory], List[str]]:
        """Extract population category."""
        return self._extract_with_patterns(text, POPULATION_PATTERNS)

    def _extract_setting(self, text: str) -> Tuple[Optional[SettingCategory], List[str]]:
        """Extract setting category."""
        return self._extract_with_patterns(text, SETTING_PATTERNS)

    def _extract_duration(self, text: str) -> Tuple[Optional[DurationCategory], Optional[int], List[str]]:
        """
        Extract duration category and normalize to minutes.

        TD-D Integration: Uses TemporalParser when available for enhanced extraction.

        Returns:
            Tuple of (category, duration_minutes, matched_strings)
        """
        category, matches = self._extract_with_patterns(text, DURATION_PATTERNS)

        # Try to extract numeric duration
        duration_minutes = None

        # TD-D: Use temporal parser if available for enhanced extraction
        if TEMPORAL_PARSER_AVAILABLE and self._temporal_parser is not None:
            try:
                result = self._temporal_parser.parse(text)
                if result.duration is not None:
                    duration_minutes = int(result.duration.to_minutes())
                    if result.duration.raw_text:
                        matches.append(result.duration.raw_text)

                    # Map exposure type to duration category
                    if result.exposure_type == ExposureType.ACUTE:
                        category = DurationCategory.ACUTE
                    elif result.exposure_type == ExposureType.SUBACUTE:
                        category = DurationCategory.REPEATED
                    elif result.exposure_type == ExposureType.CHRONIC:
                        category = DurationCategory.CHRONIC
                    elif result.exposure_type == ExposureType.RESIDENTIAL:
                        category = DurationCategory.CHRONIC

                    return category, duration_minutes, matches
            except Exception as e:
                logger.debug(f"Temporal parser failed, falling back: {e}")

        # Fallback: Simple pattern matching
        # Pattern: "X minutes"
        min_match = re.search(r'(\d+)\s*(?:min(?:ute)?s?)\b', text, re.IGNORECASE)
        if min_match:
            duration_minutes = int(min_match.group(1))

        # Pattern: "X hours" -> convert to minutes
        hour_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:hour?s?|hr?s?)\b', text, re.IGNORECASE)
        if hour_match and not duration_minutes:
            duration_minutes = int(float(hour_match.group(1)) * 60)

        return category, duration_minutes, matches

    def _extract_nature_type(self, text: str) -> Tuple[Optional[str], List[str]]:
        """Extract nature type for CNFA contexts."""
        text_lower = text.lower()
        matches = []

        for nature_type, patterns in NATURE_TYPE_PATTERNS.items():
            for pattern in patterns:
                found = re.findall(pattern, text_lower, re.IGNORECASE)
                if found:
                    matches.extend(found)
                    return nature_type, matches

        return None, matches

    def _extract_measurement_timing(self, text: str) -> Tuple[Optional[str], List[str]]:
        """Extract when outcomes were measured."""
        text_lower = text.lower()

        for timing, patterns in MEASUREMENT_TIMING_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return timing, [timing]

        return None, []

    def _extract_geography_with_spacy(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Use spaCy NER to extract geography/country."""
        if not self._spacy_available or not self._nlp:
            return None, None

        doc = self._nlp(text)
        countries = []
        locations = []

        for ent in doc.ents:
            if ent.label_ == "GPE":  # Geo-Political Entity
                countries.append(ent.text)
            elif ent.label_ == "LOC":  # Location
                locations.append(ent.text)

        country = countries[0] if countries else None
        geography = locations[0] if locations else None

        return geography, country

    def _extract_methodology(self, text: str) -> Optional[str]:
        """Extract study methodology."""
        text_lower = text.lower()

        methodology_patterns = {
            "RCT": [r'\brandomized\s*controlled\s*trial\b', r'\bRCT\b', r'\brandomized\b.*\bcontrol\b'],
            "quasi_experimental": [r'\bquasi-?experiment\b', r'\bnon-?random\b'],
            "observational": [r'\bobservational\b', r'\bcross-?sectional\b', r'\bsurvey\b'],
            "longitudinal": [r'\blongitudinal\b', r'\bprospective\b', r'\bcohort\b'],
            "case_control": [r'\bcase-?control\b'],
            "meta_analysis": [r'\bmeta-?analy\w+\b', r'\bsystematic\s*review\b'],
            "within_subjects": [r'\bwithin-?subject\b', r'\brepeated\s*measures\b', r'\bcrossover\b'],
            "between_subjects": [r'\bbetween-?subject\b', r'\bindependent\s*groups\b'],
        }

        for methodology, patterns in methodology_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return methodology

        return None

    def _calculate_generalization_risk(self, scope: ExtractedScope) -> float:
        """
        Calculate risk of overgeneralizing the finding.

        Per Dr. Mayo (P-TD Panel): Track scope coverage to identify
        untested dimensions.

        Higher risk when:
        - Few scope dimensions specified
        - Only one population tested
        - Only one setting tested
        - Simulated rather than real environment
        """
        risk = 0.5  # Base risk

        # Reduce risk for each specified dimension
        specified_count = len(scope.explicit_fields) + len(scope.inferred_fields)
        risk -= specified_count * 0.05  # Each specified dimension reduces risk

        # Increase risk for limited populations
        if scope.population_category == PopulationCategory.YOUNG_ADULTS:
            risk += 0.1  # WEIRD sample concern
        if scope.population_category == PopulationCategory.CLINICAL:
            risk += 0.05  # May not generalize to healthy

        # Increase risk for simulated settings
        if scope.setting_category == SettingCategory.SIMULATED:
            risk += 0.15  # Photos/videos may not replicate real nature
        if scope.setting_category == SettingCategory.LABORATORY:
            risk += 0.1  # Lab may not generalize to field

        # Decrease risk for field studies
        if scope.setting_category == SettingCategory.FIELD:
            risk -= 0.1

        # Clamp to valid range
        return max(0.1, min(0.9, risk))

    def _calculate_confidence(self, scope: ExtractedScope) -> float:
        """Calculate confidence in extraction."""
        # Base confidence from explicit matches
        explicit_count = len(scope.explicit_fields)
        inferred_count = len(scope.inferred_fields)

        if explicit_count == 0 and inferred_count == 0:
            return 0.0

        # Weight explicit more than inferred
        confidence = (explicit_count * 0.9 + inferred_count * 0.6) / 6  # Max 6 dimensions

        return min(1.0, confidence)

    def extract(self, text: str, is_methods_section: bool = False) -> ExtractedScope:
        """
        Extract scope conditions from text.

        Args:
            text: Text to extract from (methods section ideal)
            is_methods_section: If True, treat as higher reliability

        Returns:
            ExtractedScope with extracted conditions
        """
        if not text or not text.strip():
            return ExtractedScope()

        scope = ExtractedScope()

        # Extract population
        pop_cat, pop_matches = self._extract_population(text)
        if pop_cat:
            scope.population_category = pop_cat
            scope.population = pop_cat.value
            scope.explicit_fields.add('population')
            scope.matches['population'] = pop_matches

        # Extract setting
        set_cat, set_matches = self._extract_setting(text)
        if set_cat:
            scope.setting_category = set_cat
            scope.setting = set_cat.value
            scope.explicit_fields.add('setting')
            scope.matches['setting'] = set_matches

        # Extract duration
        dur_cat, dur_minutes, dur_matches = self._extract_duration(text)
        if dur_cat:
            scope.duration_category = dur_cat
            scope.duration = dur_cat.value
            scope.explicit_fields.add('duration')
            scope.matches['duration'] = dur_matches
        if dur_minutes:
            scope.duration_minutes = dur_minutes

        # Extract nature type
        nature_type, nature_matches = self._extract_nature_type(text)
        if nature_type:
            scope.nature_type = nature_type
            scope.explicit_fields.add('nature_type')
            scope.matches['nature_type'] = nature_matches

        # Extract measurement timing
        timing, timing_matches = self._extract_measurement_timing(text)
        if timing:
            scope.measurement_timing = timing
            scope.explicit_fields.add('measurement_timing')

        # Extract geography with spaCy
        geography, country = self._extract_geography_with_spacy(text)
        if geography:
            scope.geography = geography
            scope.explicit_fields.add('geography')
        if country:
            scope.country = country
            scope.explicit_fields.add('country')

        # Extract methodology
        methodology = self._extract_methodology(text)
        if methodology:
            scope.methodology = methodology
            scope.explicit_fields.add('methodology')

        # Set source
        if scope.explicit_fields:
            scope.source = ScopeSource.EXPLICIT
        else:
            scope.source = ScopeSource.UNKNOWN

        # Calculate confidence and risk
        scope.extraction_confidence = self._calculate_confidence(scope)
        scope.generalization_risk = self._calculate_generalization_risk(scope)

        # Boost confidence for methods sections
        if is_methods_section and scope.extraction_confidence > 0:
            scope.extraction_confidence = min(1.0, scope.extraction_confidence * 1.2)

        return scope

    def extract_from_sections(
        self,
        abstract: Optional[str] = None,
        methods: Optional[str] = None,
        results: Optional[str] = None,
        discussion: Optional[str] = None
    ) -> ExtractedScope:
        """
        Section-aware extraction (per Dr. Hearst's recommendation).

        Priority:
        1. Methods section (primary source for sample, setting)
        2. Abstract (summary of key scope)
        3. Results (confirms what was measured)
        4. Discussion (explicit limitations)
        """
        # Start with methods section (highest reliability)
        if methods:
            scope = self.extract(methods, is_methods_section=True)
        else:
            scope = ExtractedScope()

        # Supplement with abstract
        if abstract:
            abstract_scope = self.extract(abstract)
            self._merge_scope(scope, abstract_scope)

        # Look for explicit limitations in discussion
        if discussion:
            # Check for explicit scope limitations
            limitation_patterns = [
                r'limit(?:ed|ation)[s]?\s*(?:include|are|is)',
                r'only\s*(?:tested|examined|studied)',
                r'may\s*not\s*generalize',
                r'future\s*(?:research|studies)\s*should'
            ]
            for pattern in limitation_patterns:
                if re.search(pattern, discussion, re.IGNORECASE):
                    scope.inferred_fields.add('has_limitations')
                    # Increase generalization risk
                    scope.generalization_risk = min(0.9, scope.generalization_risk + 0.1)
                    break

        return scope

    def _merge_scope(self, primary: ExtractedScope, secondary: ExtractedScope):
        """Merge secondary scope into primary (filling gaps only)."""
        if not primary.population and secondary.population:
            primary.population = secondary.population
            primary.population_category = secondary.population_category
            primary.inferred_fields.add('population')

        if not primary.setting and secondary.setting:
            primary.setting = secondary.setting
            primary.setting_category = secondary.setting_category
            primary.inferred_fields.add('setting')

        if not primary.duration and secondary.duration:
            primary.duration = secondary.duration
            primary.duration_category = secondary.duration_category
            primary.inferred_fields.add('duration')

        if not primary.nature_type and secondary.nature_type:
            primary.nature_type = secondary.nature_type
            primary.inferred_fields.add('nature_type')


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

# Singleton instance
_extractor_instance: Optional[ScopeExtractor] = None


def get_scope_extractor() -> ScopeExtractor:
    """Get singleton scope extractor instance."""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = ScopeExtractor()
    return _extractor_instance


def extract_scope(text: str) -> ExtractedScope:
    """
    Extract scope conditions from text.

    Convenience function using singleton extractor.
    """
    return get_scope_extractor().extract(text)


def extract_scope_from_claim(claim: Dict[str, Any]) -> ExtractedScope:
    """
    Extract scope from a claim dictionary.

    Uses statement and any available study metadata.
    """
    extractor = get_scope_extractor()

    statement = claim.get('statement', '')
    study = claim.get('study', {})

    # Build text from available sources
    text_parts = [statement]

    if study.get('methodology'):
        text_parts.append(f"Methodology: {study['methodology']}")
    if study.get('sample'):
        text_parts.append(f"Sample: {study['sample']}")
    if study.get('setting'):
        text_parts.append(f"Setting: {study['setting']}")

    combined_text = " ".join(text_parts)

    return extractor.extract(combined_text)
