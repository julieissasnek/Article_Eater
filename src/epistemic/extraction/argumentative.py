"""
Argumentative Structure Extraction (Sprint 4 / Task 4.1).

Extracts argumentative metadata from scientific papers:
- Which theories the finding supports
- Which theories the finding challenges
- Whether adversarial scrutiny has been survived
- Replication type classification

References:
- Pollock (1995): Defeasible reasoning and defeat relations
- Walton (2008): Argumentation schemes for presumptive reasoning
"""

from dataclasses import dataclass, field
from typing import Optional, List, Tuple
import re


# =============================================================================
# DETECTION PATTERNS
# =============================================================================

THEORY_SUPPORT_PATTERNS: List[Tuple[str, float]] = [
    # Strong support indicators (weight 1.0) - capture multi-word theory names
    (r"consistent with (?:the )?([a-z]+(?:'s)? (?:\w+ )*(?:theory|hypothesis|model|framework|account))", 1.0),
    (r"supports? (?:the )?([a-z]+(?:'s)? (?:\w+ )*(?:theory|hypothesis|model|framework|account))", 1.0),
    (r"confirms? (?:the )?([a-z]+(?:'s)? (?:\w+ )*(?:theory|hypothesis|model|prediction))", 1.0),
    (r"provides? evidence for (?:the )?([a-z]+(?:'s)? (?:\w+ )*(?:theory|hypothesis|model))", 1.0),
    (r"in line with (?:the )?([a-z]+(?:'s)? (?:\w+ )*(?:theory|hypothesis|model|framework))", 1.0),
    (r"corroborates? (?:the )?([a-z]+(?:'s)? (?:\w+ )*(?:theory|hypothesis|predictions?))", 1.0),

    # Moderate support indicators (weight 0.7)
    (r"aligns? with (?:the )?([a-z]+(?:'s)? (?:\w+ )*(?:theory|framework|model))", 0.7),
    (r"as predicted by (?:the )?([a-z]+(?:'s)? (?:\w+ )*(?:theory|model))", 0.7),
    (r"consistent with (\w+(?: \w+)*) theory", 0.7),
    (r"supports? (\w+(?: \w+)*) theory", 0.7),

    # Theory name mentions with positive context (weight 0.5)
    (r"(\w+(?: \w+)* (?:theory|hypothesis)) predicts? (?:that )?.*(?:which|and) (?:we|this study) (?:found|observed|confirmed)", 0.5),
]

THEORY_CHALLENGE_PATTERNS: List[Tuple[str, float]] = [
    # Strong challenge indicators (weight 1.0) - capture multi-word theory names
    (r"challenges? (?:the )?([a-z]+(?:'s)? (?:\w+ )*(?:theory|hypothesis|model|framework|account))", 1.0),
    (r"contradicts? (?:the )?([a-z]+(?:'s)? (?:\w+ )*(?:theory|hypothesis|model|predictions?))", 1.0),
    (r"inconsistent with (?:the )?([a-z]+(?:'s)? (?:\w+ )*(?:theory|hypothesis|model|framework))", 1.0),
    (r"contrary to (?:the )?([a-z]+(?:'s)? (?:\w+ )*(?:theory|hypothesis|model|predictions?))", 1.0),
    (r"fails? to support (?:the )?([a-z]+(?:'s)? (?:\w+ )*(?:theory|hypothesis|model))", 1.0),
    (r"(?:does not|doesn't) support (?:the )?([a-z]+(?:'s)? (?:\w+ )*(?:theory|hypothesis|model))", 1.0),

    # Moderate challenge indicators (weight 0.7)
    (r"in contrast to (?:the )?([a-z]+(?:'s)? (?:\w+ )*(?:theory|framework|model))", 0.7),
    (r"diverges? from (?:the )?([a-z]+(?:'s)? (?:\w+ )*(?:theory|model|predictions?))", 0.7),
    (r"at odds with (\w+(?: \w+)*) theory", 0.7),

    # Weak challenge indicators (weight 0.5)
    (r"questions? (?:the )?([a-z]+(?:'s)? (?:\w+ )*(?:theory|model|framework))", 0.5),
    (r"casts? doubt on (?:the )?([a-z]+(?:'s)? (?:\w+ )*(?:theory|model|hypothesis))", 0.5),
]

REPLICATION_PATTERNS = {
    "direct_replication": [
        r"direct replication",
        r"exact replication",
        r"replicat(?:e|ed|ing) (?:the )?(?:original|prior) (?:study|experiment|finding)",
        r"replication (?:of|study)",
    ],
    "conceptual_replication": [
        r"conceptual replication",
        r"systematic replication",
        r"extended replication",
        r"replicat(?:e|ed|ing) (?:with|using) (?:different|novel|new) (?:method|sample|population)",
    ],
    "meta_analysis": [
        r"meta-analysis",
        r"meta analysis",
        r"systematic review",
        r"quantitative synthesis",
        r"pooled (?:effect|estimate)",
    ],
}

ADVERSARIAL_INDICATORS = [
    r"independent lab",
    r"independent research group",
    r"different theoretical tradition",
    r"competing hypothesis",
    r"rival theory",
    r"skeptic",
    r"critic(?:s|al)",
    r"registered report",
    r"adversarial collaboration",
    r"multi-lab",
    r"many labs",
]


# =============================================================================
# DATACLASS
# =============================================================================

@dataclass
class ArgumentativeMetadata:
    """
    Argumentative structure extracted from a paper.

    Per Pollock's defeasible reasoning framework, claims can serve as
    reasons FOR or AGAINST theoretical positions.
    """
    argument_for: Optional[str] = None
    argument_against: Optional[str] = None
    adversarial_scrutiny_survived: bool = False
    replication_type: str = "original"

    # Extended fields for richer analysis
    support_confidence: float = 0.0
    challenge_confidence: float = 0.0
    supporting_theories: List[str] = field(default_factory=list)
    challenged_theories: List[str] = field(default_factory=list)
    adversarial_indicators_found: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "argument_for": self.argument_for,
            "argument_against": self.argument_against,
            "adversarial_scrutiny_survived": self.adversarial_scrutiny_survived,
            "replication_type": self.replication_type,
            "support_confidence": self.support_confidence,
            "challenge_confidence": self.challenge_confidence,
            "supporting_theories": self.supporting_theories,
            "challenged_theories": self.challenged_theories,
            "adversarial_indicators_found": self.adversarial_indicators_found,
        }


# =============================================================================
# EXTRACTION FUNCTIONS
# =============================================================================

def _extract_theories(
    text: str,
    patterns: List[Tuple[str, float]]
) -> Tuple[List[str], float]:
    """
    Extract theory references from text using weighted patterns.

    Returns:
        Tuple of (list of theory names, max confidence score)
    """
    theories = []
    max_confidence = 0.0
    text_lower = text.lower()

    for pattern, weight in patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            # Clean up the theory name
            theory = match.strip() if isinstance(match, str) else match
            if theory and theory not in theories:
                theories.append(theory)
                max_confidence = max(max_confidence, weight)

    return theories, max_confidence


def _detect_replication_type(text: str) -> str:
    """
    Detect replication type from paper text.

    Priority: meta_analysis > direct_replication > conceptual_replication > original
    """
    text_lower = text.lower()

    # Check for meta-analysis first (highest priority)
    for pattern in REPLICATION_PATTERNS["meta_analysis"]:
        if re.search(pattern, text_lower):
            return "meta_analysis"

    # Check for direct replication
    for pattern in REPLICATION_PATTERNS["direct_replication"]:
        if re.search(pattern, text_lower):
            return "direct_replication"

    # Check for conceptual replication
    for pattern in REPLICATION_PATTERNS["conceptual_replication"]:
        if re.search(pattern, text_lower):
            return "conceptual_replication"

    return "original"


def _detect_adversarial_scrutiny(
    text: str,
    author_affiliations: Optional[List[str]] = None,
    theory_originators: Optional[List[str]] = None
) -> Tuple[bool, List[str]]:
    """
    Detect whether the study has undergone adversarial scrutiny.

    Adversarial scrutiny occurs when:
    1. Researchers from competing theoretical traditions test the claim
    2. The study is part of a multi-lab replication
    3. Authors explicitly identify as testing rival hypotheses
    4. Registered reports with adversarial review

    Args:
        text: Paper text to analyze
        author_affiliations: List of author institution names (optional)
        theory_originators: Names of theory originators (optional)

    Returns:
        Tuple of (is_adversarial, list of indicators found)
    """
    text_lower = text.lower()
    indicators_found = []

    for indicator in ADVERSARIAL_INDICATORS:
        if re.search(indicator, text_lower):
            indicators_found.append(indicator)

    # Check if authors are different from theory originators
    if author_affiliations and theory_originators:
        author_set = set(a.lower() for a in author_affiliations)
        originator_set = set(o.lower() for o in theory_originators)
        if not author_set.intersection(originator_set):
            indicators_found.append("authors_differ_from_originators")

    # Require at least one indicator for adversarial scrutiny
    is_adversarial = len(indicators_found) > 0

    return is_adversarial, indicators_found


def extract_argumentative_structure(
    paper_text: str,
    introduction_text: Optional[str] = None,
    discussion_text: Optional[str] = None,
    author_affiliations: Optional[List[str]] = None,
    theory_originators: Optional[List[str]] = None
) -> ArgumentativeMetadata:
    """
    Extract argumentative structure from a paper.

    Scans Introduction and Discussion sections for theory support/challenge
    language, detects replication type, and identifies adversarial scrutiny.

    Args:
        paper_text: Full paper text
        introduction_text: Introduction section (optional, extracted from paper_text if not provided)
        discussion_text: Discussion section (optional, extracted from paper_text if not provided)
        author_affiliations: List of author institutions
        theory_originators: Names of theory originators (for adversarial check)

    Returns:
        ArgumentativeMetadata with extracted information

    Example:
        >>> text = "Our results support Kaplan's attention restoration theory..."
        >>> meta = extract_argumentative_structure(text)
        >>> assert "attention restoration theory" in meta.argument_for.lower()
    """
    # Use full text if section-specific text not provided
    analysis_text = ""
    if introduction_text:
        analysis_text += introduction_text + " "
    if discussion_text:
        analysis_text += discussion_text + " "
    if not analysis_text:
        analysis_text = paper_text

    # Extract supporting and challenging theories
    supporting_theories, support_confidence = _extract_theories(
        analysis_text, THEORY_SUPPORT_PATTERNS
    )
    challenged_theories, challenge_confidence = _extract_theories(
        analysis_text, THEORY_CHALLENGE_PATTERNS
    )

    # Detect replication type
    replication_type = _detect_replication_type(paper_text)

    # Detect adversarial scrutiny
    is_adversarial, adversarial_indicators = _detect_adversarial_scrutiny(
        paper_text, author_affiliations, theory_originators
    )

    # Build result
    return ArgumentativeMetadata(
        argument_for=supporting_theories[0] if supporting_theories else None,
        argument_against=challenged_theories[0] if challenged_theories else None,
        adversarial_scrutiny_survived=is_adversarial,
        replication_type=replication_type,
        support_confidence=support_confidence,
        challenge_confidence=challenge_confidence,
        supporting_theories=supporting_theories,
        challenged_theories=challenged_theories,
        adversarial_indicators_found=adversarial_indicators,
    )
