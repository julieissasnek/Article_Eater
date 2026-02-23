"""Modular helpers extracted from the WebOfBelief monolith (ARCH-5d)."""

from .independence import compute_independence_score
from .severity import compute_severity_score
from .entrenchment import (
    DEFAULT_LEVEL_WEIGHTS,
    EntrenchmentComponents,
    EntrenchmentInput,
    compute_entrenchment_components,
    empty_entrenchment_components,
)
from .coherence import CoherenceResult, compute_coherence_state
from .equilibrium import (
    CredenceAdjustment,
    CredenceAdjustmentResult,
    EquilibriumChoice,
    choose_adjustment_target,
    compute_credence_adjustment,
)
from .engines import (
    CoherenceEngine,
    ReportingEngine,
    SnapshotEngine,
    TheoryWorldEngine,
    WebOfBeliefEngines,
)
from .evidence_updates import (
    EvidenceUpdateInput,
    build_evidence_input,
    ensure_theory_relevance,
    init_updates_payload,
    make_belief_update_record,
    make_temporal_update_record,
    make_theory_world_update_records,
    normalize_strength_map,
    normalize_temporal_observations,
)
from .experiments import (
    ExperimentBeliefInput,
    estimate_resolution,
    identify_scope_differences,
    infer_experiment_type,
    infer_test_focus_and_hypothesis,
    suggest_contested_scope,
    suggest_scope,
)
from .reporting import build_web_dict, build_web_summary
from .snapshots import (
    build_snapshot_fields,
    snapshot_anomalies,
    snapshot_beliefs_by_level,
    snapshot_stubs,
    snapshot_to_dict,
)
from .theory_worlds import (
    build_theory_worlds,
    canonical_world_id,
    conditional_probability,
    compute_world_likelihood,
    compute_world_prior,
    generate_world_assignments,
    joint_probability,
    marginal_probability,
    update_world_posteriors,
)
from .web_state import WebOfBeliefState
from .mutations import EquilibriumRequest, MutationContracts, WebMutationOperations
from .analysis_ops import AnalysisContracts, WebAnalysisOperations
from .value_metrics import (
    BeliefValueRecord,
    CentralityInput,
    EpistemicValueInput,
    compute_centrality,
    compute_epistemic_value,
    sort_value_records,
)

__all__ = [
    "compute_independence_score",
    "compute_severity_score",
    "DEFAULT_LEVEL_WEIGHTS",
    "EntrenchmentComponents",
    "EntrenchmentInput",
    "compute_entrenchment_components",
    "empty_entrenchment_components",
    "CoherenceResult",
    "compute_coherence_state",
    "EquilibriumChoice",
    "CredenceAdjustment",
    "CredenceAdjustmentResult",
    "choose_adjustment_target",
    "compute_credence_adjustment",
    "CoherenceEngine",
    "TheoryWorldEngine",
    "ReportingEngine",
    "SnapshotEngine",
    "WebOfBeliefEngines",
    "EvidenceUpdateInput",
    "normalize_strength_map",
    "normalize_temporal_observations",
    "build_evidence_input",
    "init_updates_payload",
    "make_belief_update_record",
    "make_temporal_update_record",
    "ensure_theory_relevance",
    "make_theory_world_update_records",
    "ExperimentBeliefInput",
    "infer_experiment_type",
    "infer_test_focus_and_hypothesis",
    "identify_scope_differences",
    "suggest_scope",
    "suggest_contested_scope",
    "estimate_resolution",
    "build_web_summary",
    "build_web_dict",
    "build_snapshot_fields",
    "snapshot_beliefs_by_level",
    "snapshot_stubs",
    "snapshot_anomalies",
    "snapshot_to_dict",
    "canonical_world_id",
    "generate_world_assignments",
    "compute_world_prior",
    "build_theory_worlds",
    "compute_world_likelihood",
    "update_world_posteriors",
    "marginal_probability",
    "joint_probability",
    "conditional_probability",
    "WebOfBeliefState",
    "MutationContracts",
    "EquilibriumRequest",
    "WebMutationOperations",
    "AnalysisContracts",
    "WebAnalysisOperations",
    "BeliefValueRecord",
    "CentralityInput",
    "EpistemicValueInput",
    "compute_centrality",
    "compute_epistemic_value",
    "sort_value_records",
]
