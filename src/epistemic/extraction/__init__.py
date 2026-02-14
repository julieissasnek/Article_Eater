"""
Epistemic Extraction Extensions (Sprint 4, Sprint 6c).

Extends the extraction pipeline with:
- Task 4.1: Argumentative structure extraction
- Task 4.2: Source quality metadata extraction
- Task 4.3: Epistemic mediation pathway classification
- Task 4.4: Prediction error subtype classification
- Task 6c.1: Paper type classification
- Task 6c.2: Theoretical paper extraction
- Task 6c.3: Synthesis paper ingestion
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

# Sprint 6c: Non-Empirical Paper Processing
from src.epistemic.extraction.paper_classifier import (
    TemplateFamily,
    ClassificationSignals,
    ClassificationResult,
    PaperClassifier,
    classify_paper,
    get_node_types_for_template,
    TEMPLATE_NODE_TYPES,
)

from src.epistemic.extraction.theoretical_extractor import (
    TheoreticalExtractor,
    TheoreticalExtractionResult,
    ExtractedProposition,
    ExtractedHypothesis,
    ExtractedDefinition,
    ExtractedConstraint,
    ExtractedBridgeWarrant,
    TheoryRelation,
    extract_theoretical_paper,
    compute_proposition_entrenchment,
)

from src.epistemic.extraction.synthesis_ingester import (
    SynthesisIngester,
    SynthesisExtractionResult,
    SynthesisType,
    EvidenceDirection,
    SynthesisConclusion,
    ExpertSynthesis,
    KnowledgeGap,
    MethodologicalCritique,
    PooledEffect,
    ModeratorAnalysis,
    ingest_synthesis_paper,
    compute_synthesis_vs_primary_weight,
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
    # Paper classification (Sprint 6c)
    "TemplateFamily",
    "ClassificationSignals",
    "ClassificationResult",
    "PaperClassifier",
    "classify_paper",
    "get_node_types_for_template",
    "TEMPLATE_NODE_TYPES",
    # Theoretical extraction (Sprint 6c)
    "TheoreticalExtractor",
    "TheoreticalExtractionResult",
    "ExtractedProposition",
    "ExtractedHypothesis",
    "ExtractedDefinition",
    "ExtractedConstraint",
    "ExtractedBridgeWarrant",
    "TheoryRelation",
    "extract_theoretical_paper",
    "compute_proposition_entrenchment",
    # Synthesis ingestion (Sprint 6c)
    "SynthesisIngester",
    "SynthesisExtractionResult",
    "SynthesisType",
    "EvidenceDirection",
    "SynthesisConclusion",
    "ExpertSynthesis",
    "KnowledgeGap",
    "MethodologicalCritique",
    "PooledEffect",
    "ModeratorAnalysis",
    "ingest_synthesis_paper",
    "compute_synthesis_vs_primary_weight",
]
