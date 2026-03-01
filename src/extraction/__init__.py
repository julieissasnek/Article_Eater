"""
Extraction module for Article Eater.

Main Components:
    - ExtractionPipeline: PDF extraction with queue management (pdf_extraction_module.py)
    - Vocabulary tools for variable mapping
    - Paper triage for classification
    - Gold standard validation

Usage (PDF Extraction Pipeline):
    from src.extraction import ExtractionPipeline

    pipeline = ExtractionPipeline(pdf_dir="/path/to/pdfs", output_dir="/path/to/output")
    pipeline.scan_pdfs(source_file=Path("data/extractions/full_extraction.json"))
    pipeline.process_batch(batch_size=50)
    pipeline.resume()  # Continue later
    ready = pipeline.get_ready_for_integration()  # Get results for BN/Web
"""

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

try:
    from src.extraction.paper_triage import (
        PaperTriage,
        TriageResult,
        triage_papers,
        get_extractable_papers,
        print_triage_report,
        ARTICLE_TYPE_MAPPING,
        DOMAIN_KEYWORDS,
    )
except Exception:  # pragma: no cover - optional dependency guard
    PaperTriage = None
    TriageResult = None
    triage_papers = None
    get_extractable_papers = None
    print_triage_report = None
    ARTICLE_TYPE_MAPPING = {}
    DOMAIN_KEYWORDS = {}

try:
    from src.extraction.gold_standard import (
        VerifiedClaim,
        GoldStandardPaper,
        load_gold_standard,
        save_gold_standard,
        get_selected_papers,
        get_paper_by_id,
        add_verified_claim,
        validate_extraction_against_gold,
        print_gold_standard_summary,
    )
except Exception:  # pragma: no cover - optional dependency guard
    VerifiedClaim = None
    GoldStandardPaper = None
    load_gold_standard = None
    save_gold_standard = None
    get_selected_papers = None
    get_paper_by_id = None
    add_verified_claim = None
    validate_extraction_against_gold = None
    print_gold_standard_summary = None

# PDF Extraction Pipeline (primary module)
try:
    from src.extraction.pdf_extraction_module import (
        ExtractionPipeline,
        ExtractionRequest,
        ExtractionResult,
        QueueItem,
        QualityReport,
        Finding,
        Stimulus,
        TableInfo,
        QueueStatus,
        ArticleType,
        QUALITY_THRESHOLDS,
        FIELD_WEIGHTS,
    )
except Exception:  # pragma: no cover - optional dependency guard
    ExtractionPipeline = None
    ExtractionRequest = None
    ExtractionResult = None
    QueueItem = None
    QualityReport = None
    Finding = None
    Stimulus = None
    TableInfo = None
    QueueStatus = None
    ArticleType = None
    QUALITY_THRESHOLDS = {}
    FIELD_WEIGHTS = {}


__all__ = [
    # PDF Extraction Pipeline
    "ExtractionPipeline",
    "ExtractionRequest",
    "ExtractionResult",
    "QueueItem",
    "QualityReport",
    "Finding",
    "Stimulus",
    "TableInfo",
    "QueueStatus",
    "ArticleType",
    "QUALITY_THRESHOLDS",
    "FIELD_WEIGHTS",
    # Vocabulary
    "load_vocabulary",
    "find_closest_iv",
    "find_closest_dv",
    "find_closest_variable",
    "get_extraction_prompt_vocabulary",
    "get_iv_list",
    "get_dv_list",
    "validate_vocabulary",
    # Paper Triage
    "PaperTriage",
    "TriageResult",
    "triage_papers",
    "get_extractable_papers",
    "print_triage_report",
    "ARTICLE_TYPE_MAPPING",
    "DOMAIN_KEYWORDS",
    # Gold Standard
    "VerifiedClaim",
    "GoldStandardPaper",
    "load_gold_standard",
    "save_gold_standard",
    "get_selected_papers",
    "get_paper_by_id",
    "add_verified_claim",
    "validate_extraction_against_gold",
    "print_gold_standard_summary",
]
