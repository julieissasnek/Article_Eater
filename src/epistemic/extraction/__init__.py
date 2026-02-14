"""
Epistemic Extraction Extensions (Sprint 4).

Extends the extraction pipeline with:
- Task 4.1: Argumentative structure extraction
- Task 4.2: Source quality metadata extraction
- Task 4.3: Epistemic mediation pathway classification
- Task 4.4: Prediction error subtype classification
"""

from src.epistemic.extraction.argumentative import (
    ArgumentativeMetadata,
    extract_argumentative_structure,
    THEORY_SUPPORT_PATTERNS,
    THEORY_CHALLENGE_PATTERNS,
)

from src.epistemic.extraction.source_quality_metadata import (
    SourceQualityMetadata,
    extract_source_quality_metadata,
    StudyDesign,
    PaperType,
)

from src.epistemic.extraction.pathway_classifier import (
    classify_pathway,
    PathwayClassification,
    EPISTEMIC_KEYWORDS,
    SUBPERSONAL_KEYWORDS,
)

from src.epistemic.extraction.pe_classifier import (
    classify_pe_subtype,
    PEClassification,
    FUNCTIONAL_PE_KEYWORDS,
    NAVIGATIONAL_PE_KEYWORDS,
    SOCIAL_PE_KEYWORDS,
)

__all__ = [
    # Argumentative extraction
    "ArgumentativeMetadata",
    "extract_argumentative_structure",
    "THEORY_SUPPORT_PATTERNS",
    "THEORY_CHALLENGE_PATTERNS",
    # Source quality extraction
    "SourceQualityMetadata",
    "extract_source_quality_metadata",
    "StudyDesign",
    "PaperType",
    # Pathway classification
    "classify_pathway",
    "PathwayClassification",
    "EPISTEMIC_KEYWORDS",
    "SUBPERSONAL_KEYWORDS",
    # PE classification
    "classify_pe_subtype",
    "PEClassification",
    "FUNCTIONAL_PE_KEYWORDS",
    "NAVIGATIONAL_PE_KEYWORDS",
    "SOCIAL_PE_KEYWORDS",
]
