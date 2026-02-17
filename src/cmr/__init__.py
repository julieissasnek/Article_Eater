"""
Compositional Mechanistic Reasoning (CMR) module.

This module implements the CMR pipeline for building and paper evaluation
per Doc 68 Implementation Contract.

Key components:
- models: SQLAlchemy models (TemplateRecord, CMREvaluation, etc.)
- template_scanner: Populates TemplateRecord from JSON files
- wis: Wellbeing Impact Score conversion functions
- interactions: Template interaction matrices
- building_eval: Building evaluation pipeline
- paper_eval: Paper evaluation pipeline (future)
"""

# Core models - always available
from src.cmr.models import (
    Base,
    CMRDomainScore,
    CMREvaluation,
    CMROverallScore,
    CMRTemplateActivation,
    ReductionClaim,
    TemplateRecord,
    get_engine,
    get_session,
    create_tables,
)

# Template scanner - always available
from src.cmr.template_scanner import (
    scan_templates,
    scan_template_file,
    query_active_gen2_series,
    query_by_dedup_status,
)

# Template computations - always available
from src.cmr.template_computations import (
    ComputeResult,
    OutputType,
    TEMPLATE_COMPUTE_FUNCTIONS,
    get_compute_function,
    list_implemented_templates,
    get_lifespan_multiplier,
    compute_vf3_ceiling_height,
    compute_l1_luminance_contrast,
    compute_l2_circadian_medi,
    compute_l3_daylight_composite,
    compute_crea2_processing_style,
    compute_mat1_ct_afferent,
    compute_mat2_thermal_adaptive,
    compute_mat4_material_convergence,
    compute_soc2_privacy_encounter,
    compute_sc1_spatial_integration,
    compute_sc4_wayfinding_social,
    compute_view1_vqi,
)

# Optional modules - may not exist yet
try:
    from src.cmr.wis import (
        aggregate_domain_wis,
        aggregate_overall_wis,
        cohens_d_to_wis,
        goldilocks_to_wis,
        threshold_to_wis,
    )
    _WIS_AVAILABLE = True
except ImportError:
    _WIS_AVAILABLE = False

try:
    from src.cmr.interactions import apply_all_interactions, get_interaction
    _INTERACTIONS_AVAILABLE = True
except ImportError:
    _INTERACTIONS_AVAILABLE = False

try:
    from src.cmr.building_eval import evaluate_building
    _BUILDING_EVAL_AVAILABLE = True
except ImportError:
    _BUILDING_EVAL_AVAILABLE = False

try:
    from src.cmr.report import format_report_text, generate_report
    _REPORT_AVAILABLE = True
except ImportError:
    _REPORT_AVAILABLE = False

__all__ = [
    # Core models
    "Base",
    "TemplateRecord",
    "CMREvaluation",
    "CMRTemplateActivation",
    "CMRDomainScore",
    "CMROverallScore",
    "ReductionClaim",
    # Database utilities
    "get_engine",
    "get_session",
    "create_tables",
    # Scanner
    "scan_templates",
    "scan_template_file",
    "query_active_gen2_series",
    "query_by_dedup_status",
    # Template computations
    "ComputeResult",
    "OutputType",
    "TEMPLATE_COMPUTE_FUNCTIONS",
    "get_compute_function",
    "list_implemented_templates",
    "get_lifespan_multiplier",
    "compute_vf3_ceiling_height",
    "compute_l1_luminance_contrast",
    "compute_l2_circadian_medi",
    "compute_l3_daylight_composite",
    "compute_crea2_processing_style",
    "compute_mat1_ct_afferent",
    "compute_mat2_thermal_adaptive",
    "compute_mat4_material_convergence",
    "compute_soc2_privacy_encounter",
    "compute_sc1_spatial_integration",
    "compute_sc4_wayfinding_social",
    "compute_view1_vqi",
]

# Add optional exports if available
if _WIS_AVAILABLE:
    __all__.extend([
        "cohens_d_to_wis",
        "goldilocks_to_wis",
        "threshold_to_wis",
        "aggregate_domain_wis",
        "aggregate_overall_wis",
    ])

if _INTERACTIONS_AVAILABLE:
    __all__.extend([
        "get_interaction",
        "apply_all_interactions",
    ])

if _BUILDING_EVAL_AVAILABLE:
    __all__.append("evaluate_building")

if _REPORT_AVAILABLE:
    __all__.extend([
        "generate_report",
        "format_report_text",
    ])
