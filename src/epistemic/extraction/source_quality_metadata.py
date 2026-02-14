"""
Source Quality Metadata Extraction (Sprint 4 / Task 4.2).

Extracts methodological quality indicators from scientific papers:
- Study design classification
- Sample size extraction
- Pre-registration detection
- Author affiliation extraction
- Funding source identification
- Paper type classification

References:
- Cochrane GRADE framework
- Cartwright (2007): Evidence-based policy
"""

from dataclasses import dataclass, field
from typing import Optional, List, Tuple
from enum import Enum
import re


# =============================================================================
# ENUMS
# =============================================================================

class StudyDesign(str, Enum):
    """Study design hierarchy (roughly ordered by internal validity)."""
    RCT = "rct"
    QUASI_EXPERIMENTAL = "quasi_experimental"
    WITHIN_SUBJECTS = "within_subjects"
    CORRELATIONAL = "correlational"
    CASE_STUDY = "case_study"
    QUALITATIVE = "qualitative"
    DESCRIPTIVE = "descriptive"
    UNKNOWN = "unknown"


class PaperType(str, Enum):
    """Type of paper."""
    PRIMARY = "primary"
    REVIEW = "review"
    META_ANALYSIS = "meta_analysis"
    COMMENTARY = "commentary"
    THEORETICAL = "theoretical"
    PROTOCOL = "protocol"
    UNKNOWN = "unknown"


# =============================================================================
# DETECTION PATTERNS
# =============================================================================

STUDY_DESIGN_PATTERNS = {
    StudyDesign.RCT: [
        r"random(?:ly)? assign(?:ed|ment)?",
        r"randomized controlled trial",
        r"randomised controlled trial",
        r"RCT",
        r"double-blind",
        r"single-blind",
        r"placebo.{0,20}control",
    ],
    StudyDesign.QUASI_EXPERIMENTAL: [
        r"quasi-experiment",
        r"non-random(?:ized|ised)? assign",
        r"natural experiment",
        r"pre-post (?:design|study)",
        r"before.{0,10}after (?:design|study)",
        r"interrupted time series",
    ],
    StudyDesign.WITHIN_SUBJECTS: [
        r"within-subjects? (?:design|study)?",
        r"repeated measures",
        r"crossover (?:design|study)",
        r"counterbalanced",
        r"each participant.{0,30}all conditions",
    ],
    StudyDesign.CORRELATIONAL: [
        r"correlational (?:design|study)?",
        r"cross-sectional (?:design|study)?",
        r"survey (?:design|study)?",
        r"observational (?:design|study)?",
        r"regression analysis",
        r"path analysis",
    ],
    StudyDesign.CASE_STUDY: [
        r"case study",
        r"single case",
        r"n\s*=\s*1\b",
    ],
    StudyDesign.QUALITATIVE: [
        r"qualitative (?:study|research|method)",
        r"interview(?:s|ed)?",
        r"focus group",
        r"thematic analysis",
        r"grounded theory",
        r"ethnograph",
        r"phenomenolog",
    ],
}

PAPER_TYPE_PATTERNS = {
    PaperType.META_ANALYSIS: [
        r"meta-analysis",
        r"meta analysis",
        r"quantitative synthesis",
        r"pooled effect",
    ],
    PaperType.REVIEW: [
        r"systematic review",
        r"literature review",
        r"scoping review",
        r"narrative review",
    ],
    PaperType.COMMENTARY: [
        r"commentary",
        r"letter to (?:the )?editor",
        r"response to",
        r"reply to",
        r"editorial",
    ],
    PaperType.THEORETICAL: [
        r"theoretical (?:paper|framework|model)",
        r"conceptual (?:paper|framework|model)",
        r"theory development",
    ],
    PaperType.PROTOCOL: [
        r"study protocol",
        r"trial protocol",
        r"registered report",
    ],
}

SAMPLE_SIZE_PATTERNS = [
    r"N\s*=\s*(\d+)",
    r"n\s*=\s*(\d+)",
    r"(\d+)\s*participants",
    r"(\d+)\s*subjects",
    r"(\d+)\s*respondents",
    r"sample\s+(?:size\s+)?(?:of\s+)?(\d+)",
    r"total\s+(?:sample\s+)?(?:of\s+)?(\d+)",
    r"(\d+)\s+(?:patients|adults|children|students|employees|individuals)",
]

PREREGISTRATION_PATTERNS = [
    r"pre-register",
    r"preregister",
    r"registered (?:in advance|prior to)",
    r"OSF",
    r"Open Science Framework",
    r"AsPredicted",
    r"ClinicalTrials\.gov",
    r"PROSPERO",
    r"registered report",
]


# =============================================================================
# DATACLASS
# =============================================================================

@dataclass
class SourceQualityMetadata:
    """
    Methodological quality metadata extracted from a paper.

    Per Cochrane GRADE framework, these factors contribute to
    evidence quality assessment.
    """
    study_design: StudyDesign = StudyDesign.UNKNOWN
    sample_size: Optional[int] = None
    pre_registered: Optional[bool] = None
    author_affiliations: List[str] = field(default_factory=list)
    funding_source: Optional[str] = None
    paper_type: PaperType = PaperType.PRIMARY

    # Extended fields
    design_confidence: float = 0.0
    sample_sizes_found: List[int] = field(default_factory=list)
    preregistration_indicators: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "study_design": self.study_design.value,
            "sample_size": self.sample_size,
            "pre_registered": self.pre_registered,
            "author_affiliations": self.author_affiliations,
            "funding_source": self.funding_source,
            "paper_type": self.paper_type.value,
            "design_confidence": self.design_confidence,
            "sample_sizes_found": self.sample_sizes_found,
            "preregistration_indicators": self.preregistration_indicators,
        }


# =============================================================================
# EXTRACTION FUNCTIONS
# =============================================================================

def _detect_study_design(text: str) -> Tuple[StudyDesign, float]:
    """
    Detect study design from paper text.

    Returns:
        Tuple of (StudyDesign, confidence score)
    """
    text_lower = text.lower()

    # Priority order: RCT > quasi > within-subjects > correlational > case > qualitative
    design_priority = [
        StudyDesign.RCT,
        StudyDesign.QUASI_EXPERIMENTAL,
        StudyDesign.WITHIN_SUBJECTS,
        StudyDesign.CORRELATIONAL,
        StudyDesign.CASE_STUDY,
        StudyDesign.QUALITATIVE,
    ]

    for design in design_priority:
        patterns = STUDY_DESIGN_PATTERNS.get(design, [])
        match_count = 0
        for pattern in patterns:
            if re.search(pattern, text_lower):
                match_count += 1

        if match_count > 0:
            # Confidence based on number of matching patterns
            confidence = min(1.0, 0.5 + (match_count * 0.2))
            return design, confidence

    return StudyDesign.UNKNOWN, 0.0


def _detect_paper_type(text: str, title: Optional[str] = None) -> PaperType:
    """
    Detect paper type from text and title.
    """
    # Check title first (more reliable)
    search_text = (title or "") + " " + text[:2000]  # Title + abstract area
    search_lower = search_text.lower()

    for paper_type, patterns in PAPER_TYPE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, search_lower):
                return paper_type

    return PaperType.PRIMARY


def _extract_sample_sizes(text: str) -> List[int]:
    """
    Extract all sample sizes mentioned in text.
    """
    sizes = []
    text_lower = text.lower()

    for pattern in SAMPLE_SIZE_PATTERNS:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            try:
                size = int(match)
                if 1 <= size <= 1000000:  # Reasonable range
                    sizes.append(size)
            except (ValueError, TypeError):
                continue

    # Remove duplicates, preserve order
    seen = set()
    unique_sizes = []
    for s in sizes:
        if s not in seen:
            seen.add(s)
            unique_sizes.append(s)

    return unique_sizes


def _detect_preregistration(text: str) -> Tuple[Optional[bool], List[str]]:
    """
    Detect whether study was pre-registered.

    Returns:
        Tuple of (is_preregistered, list of indicators found)
    """
    text_lower = text.lower()
    indicators = []

    for pattern in PREREGISTRATION_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            indicators.append(pattern)

    if indicators:
        return True, indicators

    # Check for explicit "not pre-registered"
    if re.search(r"not pre-?register", text_lower):
        return False, ["explicitly_not_preregistered"]

    return None, []


def _extract_affiliations(text: str) -> List[str]:
    """
    Extract author affiliations from paper metadata area.

    Looks for common affiliation patterns in the first portion of text.
    """
    # Focus on first 5000 chars (metadata area)
    metadata_area = text[:5000]

    affiliations = []

    # Pattern for university/institution names
    affiliation_patterns = [
        r"(?:University|Institute|College|School|Department|Lab(?:oratory)?|Center|Centre) of [A-Z][a-z]+(?:\s+[A-Z][a-z]+)*",
        r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:University|Institute|College)",
    ]

    for pattern in affiliation_patterns:
        matches = re.findall(pattern, metadata_area)
        for match in matches:
            if match not in affiliations:
                affiliations.append(match)

    return affiliations[:10]  # Limit to 10 affiliations


def _extract_funding(text: str) -> Optional[str]:
    """
    Extract funding source from paper.
    """
    funding_patterns = [
        r"(?:funded|supported|grant) by ([^.]+)",
        r"funding.*?from ([^.]+)",
        r"(?:grant|award) (?:from|number) ([^.]+)",
        r"acknowledg.*?(?:support|funding).*?from ([^.]+)",
    ]

    # Look in last 20% of paper (acknowledgments area)
    search_area = text[int(len(text) * 0.8):]

    for pattern in funding_patterns:
        match = re.search(pattern, search_area, re.IGNORECASE)
        if match:
            funding = match.group(1).strip()
            # Clean up
            funding = re.sub(r'\s+', ' ', funding)
            if len(funding) < 200:  # Reasonable length
                return funding

    return None


# =============================================================================
# QUALITY SCORING
# =============================================================================

# Study design scores (higher = better internal validity)
DESIGN_SCORES = {
    StudyDesign.RCT: 1.0,
    StudyDesign.QUASI_EXPERIMENTAL: 0.7,
    StudyDesign.WITHIN_SUBJECTS: 0.6,
    StudyDesign.CORRELATIONAL: 0.4,
    StudyDesign.CASE_STUDY: 0.2,
    StudyDesign.QUALITATIVE: 0.3,
    StudyDesign.DESCRIPTIVE: 0.2,
    StudyDesign.UNKNOWN: 0.3,
}


def compute_design_score(study_design: str) -> float:
    """
    Compute internal validity score based on study design.

    Args:
        study_design: Study design string or StudyDesign enum value

    Returns:
        Score in [0, 1] where 1 = highest internal validity (RCT)
    """
    # Handle string input
    if isinstance(study_design, str):
        try:
            design = StudyDesign(study_design)
        except ValueError:
            # Try case-insensitive match
            for sd in StudyDesign:
                if sd.value.lower() == study_design.lower():
                    design = sd
                    break
            else:
                design = StudyDesign.UNKNOWN
    else:
        design = study_design

    return DESIGN_SCORES.get(design, 0.3)


def extract_source_quality_metadata(
    paper_text: str,
    title: Optional[str] = None,
    methods_section: Optional[str] = None,
    abstract: Optional[str] = None
) -> SourceQualityMetadata:
    """
    Extract source quality metadata from a paper.

    Scans the paper for study design indicators, sample size,
    pre-registration status, and other quality signals.

    Args:
        paper_text: Full paper text
        title: Paper title (optional)
        methods_section: Methods section text (optional, more reliable)
        abstract: Abstract text (optional)

    Returns:
        SourceQualityMetadata with extracted information

    Example:
        >>> text = "We conducted a randomized controlled trial with N=200 participants..."
        >>> meta = extract_source_quality_metadata(text)
        >>> assert meta.study_design == StudyDesign.RCT
        >>> assert meta.sample_size == 200
    """
    # Prioritize methods section if available
    design_text = methods_section or abstract or paper_text

    # Extract study design
    study_design, design_confidence = _detect_study_design(design_text)

    # Extract paper type
    paper_type = _detect_paper_type(paper_text, title)

    # Extract sample sizes
    sample_sizes = _extract_sample_sizes(design_text)

    # Take largest sample size as primary (often total N)
    primary_sample_size = max(sample_sizes) if sample_sizes else None

    # Detect pre-registration
    pre_registered, prereg_indicators = _detect_preregistration(paper_text)

    # Extract affiliations
    affiliations = _extract_affiliations(paper_text)

    # Extract funding
    funding = _extract_funding(paper_text)

    return SourceQualityMetadata(
        study_design=study_design,
        sample_size=primary_sample_size,
        pre_registered=pre_registered,
        author_affiliations=affiliations,
        funding_source=funding,
        paper_type=paper_type,
        design_confidence=design_confidence,
        sample_sizes_found=sample_sizes,
        preregistration_indicators=prereg_indicators,
    )
