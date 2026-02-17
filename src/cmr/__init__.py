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
    PaperRecord,
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
    # Batch 1 templates
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
    # Batch 2 templates
    compute_l4_cct_temporal,
    compute_l5_dynamic_light,
    compute_mat3_material_identity,
    compute_mat5_material_cultural,
    compute_tp1_motor_pe,
    compute_tp2_threshold_boundary,
    compute_tp3_temporal_rhythm,
    compute_tp4_temporal_hierarchy,
    compute_soc1_proxemic_pe,
    compute_soc3_territorial,
    compute_crea1_creative_network,
    compute_crea3_incubation,
    compute_crea4_collaborative,
    compute_sc2_isovist,
    compute_sc3_promenade,
    compute_col1_chromatic_pe,
    compute_col2_color_harmony,
    compute_vf1_contour_curvature,
    compute_vf2_visual_rhythm,
    compute_olf1_olfactory_pe,
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

try:
    from src.cmr.paper_eval import evaluate_paper
    _PAPER_EVAL_AVAILABLE = True
except ImportError:
    _PAPER_EVAL_AVAILABLE = False

try:
    from src.cmr.paper_report import generate_paper_report, format_paper_report_text
    _PAPER_REPORT_AVAILABLE = True
except ImportError:
    _PAPER_REPORT_AVAILABLE = False

try:
    from src.cmr.voi_scoring import score_voi, aggregate_paper_voi
    _VOI_SCORING_AVAILABLE = True
except ImportError:
    _VOI_SCORING_AVAILABLE = False

try:
    from src.cmr.paper_history import (
        create_paper_record,
        get_high_voi_papers,
        get_papers_for_template,
        get_processed_papers,
    )
    _PAPER_HISTORY_AVAILABLE = True
except ImportError:
    _PAPER_HISTORY_AVAILABLE = False

__all__ = [
    # Core models
    "Base",
    "TemplateRecord",
    "CMREvaluation",
    "CMRTemplateActivation",
    "CMRDomainScore",
    "CMROverallScore",
    "PaperRecord",
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
    # Batch 1
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
    # Batch 2
    "compute_l4_cct_temporal",
    "compute_l5_dynamic_light",
    "compute_mat3_material_identity",
    "compute_mat5_material_cultural",
    "compute_tp1_motor_pe",
    "compute_tp2_threshold_boundary",
    "compute_tp3_temporal_rhythm",
    "compute_tp4_temporal_hierarchy",
    "compute_soc1_proxemic_pe",
    "compute_soc3_territorial",
    "compute_crea1_creative_network",
    "compute_crea3_incubation",
    "compute_crea4_collaborative",
    "compute_sc2_isovist",
    "compute_sc3_promenade",
    "compute_col1_chromatic_pe",
    "compute_col2_color_harmony",
    "compute_vf1_contour_curvature",
    "compute_vf2_visual_rhythm",
    "compute_olf1_olfactory_pe",
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

if _PAPER_EVAL_AVAILABLE:
    __all__.append("evaluate_paper")

if _PAPER_REPORT_AVAILABLE:
    __all__.extend([
        "generate_paper_report",
        "format_paper_report_text",
    ])

if _VOI_SCORING_AVAILABLE:
    __all__.extend([
        "score_voi",
        "aggregate_paper_voi",
    ])

if _PAPER_HISTORY_AVAILABLE:
    __all__.extend([
        "create_paper_record",
        "get_processed_papers",
        "get_papers_for_template",
        "get_high_voi_papers",
    ])
