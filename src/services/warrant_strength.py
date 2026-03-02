"""
Warrant Strength (ω) Computation Module

Implements the panel-approved warrant strength formula per §48.3B of the ATLAS master documentation.
This module provides the foundation for evidence-based credence assignment in the Quinean web-of-belief
system for environmental psychology.

The warrant strength formula combines:
  ω = ω_base × ω_conf × ω_rep × ω_meta

Where each component captures a distinct epistemic dimension:
  - ω_base: Experimental severity + theory support (primary evidence quality)
  - ω_conf: Confound risk adjustment (threats to validity)
  - ω_rep: Replication adjustment (robustness across studies)
  - ω_meta: Meta-calibration (publication type and registration status)

Author: Claude Code (agent for Prof. David Kirsh, UCSD Cognitive Science)
Date: 2026-03-02
Reference: ATLAS §48.3B (Panel Revision R1, R2)
"""

import json
import logging
import math
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# Legacy key → new hyphenated theory_id mapping for backward compatibility
_LEGACY_KEY_MAP = {
    # Old lowercase keys → new hyphenated
    "chronobiology": "chronobiological-regulation",
    "art": "attention-restoration-theory",
    "srt": "stress-recovery-theory",
    "biophilia": "biophilia-hypothesis",
    "prospect_refuge": "prospect-refuge-theory",
    "kaplan_preference": "kaplan-preference-matrix",
    "flow_theory": "flow-theory",
    "processing_fluency": "processing-fluency",
    "proxemics": "proxemics",
    "cognitive_map": "cognitive-mapping",
    "place_attachment": "place-attachment",
    "privacy_regulation": "privacy-regulation",
    "adaptive_thermal": "adaptive-thermal-comfort",
    "predictive_coding_music": "predictive-processing-music",
    # 2-letter abbreviation → new hyphenated
    "PP": "predictive-processing",
    "SN": "spatial-navigation",
    "DP": "dual-process-evaluation",
    "DT": "default-mode-dynamics",
    "NM": "neuromodulatory-systems",
    "IC": "interoceptive-constructionist-affect",
    "MS": "memory-systems",
    "EC": "embodied-cognition",
    "CB": "chronobiological-regulation",
    "MSI": "multisensory-integration",
    "ART": "attention-restoration-theory",
    "SRT": "stress-recovery-theory",
    "BIOPHILIA": "biophilia-hypothesis",
    "PROSPECT_REFUGE": "prospect-refuge-theory",
}


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp value to [lo, hi] range."""
    return max(lo, min(hi, float(value)))


class DesignType(Enum):
    """Enumeration of experimental design types for severity scoring."""
    LARGE_RCT = "large_rct"  # N > 200, pre-registered
    STANDARD_RCT = "standard_rct"  # Randomized, controlled
    QUASI_EXPERIMENTAL = "quasi_experimental"  # Natural experiment, ITS
    WITHIN_SUBJECTS = "within_subjects"  # Crossover designs
    OBSERVATIONAL = "observational"  # Correlational, survey
    CASE_STUDY = "case_study"  # Qualitative, case study
    META_ANALYSIS = "meta_analysis"  # Systematic review aggregation
    SYSTEMATIC_REVIEW = "systematic_review"  # Qualitative synthesis


class PublicationType(Enum):
    """Publication/registration status types."""
    REGISTERED_REPORT = "registered_report"
    PEER_REVIEWED = "peer_reviewed"
    PREPRINT = "preprint"
    GREY_LITERATURE = "grey_literature"


@dataclass
class OmegaResult:
    """
    Complete warrant strength result with all component values for auditability.

    This dataclass captures the full decomposition of ω for inspection and panel review.
    All values are clamped to [0, 1] per panel specifications.

    Attributes:
        omega: Final composite warrant strength ω ∈ [0, 1]
        omega_base: Base warrant from experimental severity + theory support
        omega_sev: Severity score from experimental design quality
        omega_theory: Theory support contribution (T_ent × mechanism_specificity)
        omega_conf: Confound risk adjustment (inverted: 1.0 = low risk)
        omega_rep: Replication adjustment
        omega_meta: Meta-calibration (publication type + registration)
        omega_source: Source quality multiplier ∈ [0.7, 1.1] (Sprint B)
        floor_constraint_applied: Whether R1 floor constraint was applied to ω_base
        design_type: Type of experimental design (if computed from design)
        notes: Auditable explanation of computation steps
    """
    omega: float
    omega_base: float
    omega_sev: float
    omega_theory: float
    omega_conf: float
    omega_rep: float
    omega_meta: float
    omega_source: float = 1.0  # Sprint B: SQ → ω multiplier
    floor_constraint_applied: bool = False
    design_type: Optional[str] = None
    notes: str = ""

    def __post_init__(self):
        """Clamp all values to [0, 1] range."""
        self.omega = _clamp(self.omega, 0.0, 1.0)
        self.omega_base = _clamp(self.omega_base, 0.0, 1.0)
        self.omega_sev = _clamp(self.omega_sev, 0.0, 1.0)
        self.omega_theory = _clamp(self.omega_theory, 0.0, 1.0)
        self.omega_conf = _clamp(self.omega_conf, 0.0, 1.0)
        self.omega_rep = _clamp(self.omega_rep, 0.0, 1.0)
        self.omega_meta = _clamp(self.omega_meta, 0.0, 1.0)
        # omega_source has special range [0.7, 1.1], not [0, 1]
        self.omega_source = _clamp(self.omega_source, 0.7, 1.1)

    def to_dict(self) -> Dict:
        """Serialize OmegaResult to dictionary for logging/storage."""
        return {
            "omega": float(self.omega),
            "omega_base": float(self.omega_base),
            "omega_sev": float(self.omega_sev),
            "omega_theory": float(self.omega_theory),
            "omega_conf": float(self.omega_conf),
            "omega_rep": float(self.omega_rep),
            "omega_meta": float(self.omega_meta),
            "omega_source": float(self.omega_source),
            "floor_constraint_applied": self.floor_constraint_applied,
            "design_type": self.design_type,
            "notes": self.notes,
        }


def load_tea_scores(path: Optional[str] = None) -> Dict[str, float]:
    """
    Load Theory Entrenchment Assessment (TEA) scores from JSON.

    TEA scores (T_ent) represent the degree to which a causal theory is entrenched
    in the broader scientific consensus, ranging from 0.0 (novel, unvetted) to 1.0
    (canonical, widely accepted).

    Supports backward compatibility: the returned dictionary includes:
    - New hyphenated theory IDs (e.g., "attention-restoration-theory")
    - Abbreviation codes from the theories list (e.g., "ART")
    - Legacy old-style keys mapped via _LEGACY_KEY_MAP (e.g., "art")

    All variants map to the same T_ent value.

    Args:
        path: Path to tea_scores.json. If None, uses default path relative to this module.

    Returns:
        Dictionary mapping theory identifiers (str) → T_ent score (float ∈ [0, 1])
        Keys include: new theory_ids, abbreviations, and legacy keys (all backed by same T_ent).

    Raises:
        FileNotFoundError: If tea_scores.json cannot be located.
        json.JSONDecodeError: If file is malformed JSON.

    Example:
        >>> tea_scores = load_tea_scores()
        >>> tea_scores["attention-restoration-theory"]  # 0.78
        >>> tea_scores["ART"]  # 0.78 (abbreviation)
        >>> tea_scores["art"]  # 0.78 (legacy key)
    """
    if path is None:
        # Default path relative to this module: ../../../data/theories/tea_scores.json
        module_dir = Path(__file__).parent
        path = module_dir / ".." / ".." / "data" / "theories" / "tea_scores.json"
    else:
        path = Path(path)

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        tea_scores = {}

        # Handle structured format: {metadata: {...}, theories: [{theory_id, abbreviation, T_ent, ...}, ...]}
        if isinstance(raw, dict) and "theories" in raw:
            for entry in raw["theories"]:
                tid = entry.get("theory_id", "")
                t_ent = float(entry.get("T_ent", 0.5))

                # Add primary key: new hyphenated theory_id
                if tid:
                    tea_scores[tid] = t_ent

                # Add abbreviation key if present
                abbreviation = entry.get("abbreviation", "")
                if abbreviation:
                    tea_scores[abbreviation] = t_ent

        elif isinstance(raw, dict):
            # Flat format: {theory_id: T_ent, ...}
            tea_scores = {k: float(v) for k, v in raw.items()}
        else:
            raise ValueError(f"Unexpected TEA scores format: {type(raw)}")

        # Add legacy key mappings for backward compatibility
        # For each old_key → new_key mapping, add old_key to dict if new_key exists
        for old_key, new_key in _LEGACY_KEY_MAP.items():
            if new_key in tea_scores:
                tea_scores[old_key] = tea_scores[new_key]

        logger.info(
            f"Loaded {len(tea_scores)} TEA score entries (including legacy aliases) from {path}"
        )
        return tea_scores
    except FileNotFoundError:
        logger.error(f"TEA scores file not found at {path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse TEA scores JSON: {e}")
        raise


def compute_omega_sev(
    design_type: DesignType,
    sample_size: Optional[int] = None,
    pre_registered: bool = False,
    blinded: bool = False,
    self_report_only: bool = False,
) -> float:
    """
    Compute experimental severity score (ω_sev) from design characteristics.

    Severity reflects the strength of evidence from experimental design quality,
    modulated by design type, sample size, pre-registration, blinding, and measurement method.

    Design type baseline severity ranges:
        - LARGE_RCT (N>200, pre-registered): 0.85-0.95
        - STANDARD_RCT (randomized, controlled): 0.70-0.85
        - QUASI_EXPERIMENTAL (natural experiment, ITS): 0.50-0.70
        - WITHIN_SUBJECTS (crossover): 0.55-0.75
        - OBSERVATIONAL (correlational, survey): 0.20-0.40
        - CASE_STUDY (qualitative): 0.10-0.25
        - META_ANALYSIS: 0.80-0.95
        - SYSTEMATIC_REVIEW: 0.75-0.90

    Modifiers (applied after baseline):
        +0.05 for pre-registration (reduces researcher degrees of freedom)
        +0.05 for blinding (reduces bias)
        -0.10 for self-report-only measurement (increases measurement error)

    Args:
        design_type: DesignType enum value specifying experimental design.
        sample_size: Sample size N. For LARGE_RCT, N > 200 sets baseline to 0.95.
        pre_registered: Whether study was pre-registered (OSF, AsPredicted, etc.).
        blinded: Whether study employed blinding (double-blind preferred).
        self_report_only: Whether all outcomes are self-reported (no objective measures).

    Returns:
        Severity score ω_sev ∈ [0, 1]

    Reference:
        Mayo & Spohn (2011) on severity in evidence evaluation; ATLAS §48.3B

    Example:
        >>> omega_sev = compute_omega_sev(
        ...     DesignType.LARGE_RCT,
        ...     sample_size=250,
        ...     pre_registered=True,
        ...     blinded=True
        ... )  # Returns ~0.98
    """
    # Baseline severity by design type
    baseline_severity = {
        DesignType.LARGE_RCT: 0.90,  # N > 200 → 0.95; otherwise 0.85
        DesignType.STANDARD_RCT: 0.77,
        DesignType.QUASI_EXPERIMENTAL: 0.60,
        DesignType.WITHIN_SUBJECTS: 0.65,
        DesignType.OBSERVATIONAL: 0.30,
        DesignType.CASE_STUDY: 0.17,
        DesignType.META_ANALYSIS: 0.87,
        DesignType.SYSTEMATIC_REVIEW: 0.82,
    }

    omega_sev = baseline_severity.get(design_type, 0.5)

    # Sample size adjustment for LARGE_RCT
    if design_type == DesignType.LARGE_RCT and sample_size is not None:
        if sample_size > 200:
            omega_sev = 0.95
        else:
            omega_sev = 0.85

    # Apply modifiers
    if pre_registered:
        omega_sev += 0.05
    if blinded:
        omega_sev += 0.05
    if self_report_only:
        omega_sev -= 0.10

    # Clamp to [0, 1]
    omega_sev = _clamp(omega_sev, 0.0, 1.0)

    logger.debug(
        f"compute_omega_sev: design={design_type.value}, "
        f"N={sample_size}, pre_reg={pre_registered}, "
        f"blinded={blinded}, self_report={self_report_only} → ω_sev={omega_sev:.3f}"
    )

    return omega_sev


def compute_omega_theory(
    theory_id: str,
    mechanism_specificity: float,
    tea_scores: Optional[Dict[str, float]] = None,
) -> float:
    """
    Compute theory support contribution (ω_theory).

    ω_theory = T_ent × mechanism_specificity

    where:
        - T_ent: Theory Entrenchment score from TEA lookup (0-1 scale)
        - mechanism_specificity: How precisely the theory predicts the observed mechanism (0-1)

    Theory support is only applied to mechanism/theory edges (see compute_omega_base).
    For non-mechanism edges, ω_theory = 0.

    Args:
        theory_id: Identifier for the theory (e.g., "attention_restoration_theory").
        mechanism_specificity: Mechanistic fit of theory to observed causal path (0-1).
        tea_scores: Pre-loaded TEA scores dict. If None, loads from default path.

    Returns:
        ω_theory ∈ [0, 1]

    Raises:
        KeyError: If theory_id not found in TEA scores (logs warning, returns 0).

    Reference:
        ATLAS §48.3B: "T_ent values come from tea_scores.json"

    Example:
        >>> tea_scores = load_tea_scores()
        >>> omega_theory = compute_omega_theory(
        ...     "stress_reduction_theory",
        ...     mechanism_specificity=0.85,
        ...     tea_scores=tea_scores
        ... )  # Returns T_ent × 0.85
    """
    if tea_scores is None:
        tea_scores = load_tea_scores()

    # Clamp mechanism_specificity to [0, 1]
    mechanism_specificity = _clamp(mechanism_specificity, 0.0, 1.0)

    if theory_id not in tea_scores:
        logger.warning(
            f"Theory '{theory_id}' not found in TEA scores. "
            f"Returning ω_theory = 0.0. Available theories: {list(tea_scores.keys())}"
        )
        return 0.0

    t_ent = tea_scores[theory_id]
    omega_theory = t_ent * mechanism_specificity

    logger.debug(
        f"compute_omega_theory: theory={theory_id}, "
        f"T_ent={t_ent:.3f}, mech_spec={mechanism_specificity:.3f} → ω_theory={omega_theory:.3f}"
    )

    return _clamp(omega_theory, 0.0, 1.0)


def compute_omega_base(
    omega_sev: float,
    omega_theory: float = 0.0,
    is_mechanism_edge: bool = False,
) -> Tuple[float, bool]:
    """
    Compute base warrant strength (ω_base) from severity and theory support.

    For mechanism/theory edges:
        ω_base = ω_sev + ω_theory × (1 − ω_sev)

    For non-mechanism edges:
        ω_base = ω_sev

    Floor Constraint R1 (Panel Revision):
        When ω_sev < 0.20, enforce: ω_base ≤ 2 × ω_sev

        Rationale: This prevents theory from substituting for absent direct evidence.
        A theory that's well-supported cannot rescue a fundamentally weak design.

    Args:
        omega_sev: Experimental severity score (0-1).
        omega_theory: Theory support contribution (0-1). Only used if is_mechanism_edge=True.
        is_mechanism_edge: Whether this edge is theory-driven (causal mechanism).

    Returns:
        Tuple of (ω_base ∈ [0, 1], floor_constraint_applied: bool)

    Reference:
        ATLAS §48.3B (Panel Revision R1)

    Example:
        >>> omega_base, constraint = compute_omega_base(
        ...     omega_sev=0.75,
        ...     omega_theory=0.60,
        ...     is_mechanism_edge=True
        ... )  # Returns (~0.90, False)

        >>> omega_base, constraint = compute_omega_base(
        ...     omega_sev=0.15,
        ...     omega_theory=0.80,
        ...     is_mechanism_edge=True
        ... )  # Returns (~0.30, True) — floor enforced
    """
    omega_sev = _clamp(omega_sev, 0.0, 1.0)
    omega_theory = _clamp(omega_theory, 0.0, 1.0)

    # Compute ω_base per formula
    if is_mechanism_edge:
        omega_base = omega_sev + omega_theory * (1.0 - omega_sev)
    else:
        omega_base = omega_sev

    # Apply floor constraint R1
    floor_constraint_applied = False
    if omega_sev < 0.20:
        floor_max = 2.0 * omega_sev
        if omega_base > floor_max:
            logger.debug(
                f"Floor constraint R1 applied: ω_sev={omega_sev:.3f} < 0.20, "
                f"clamping ω_base from {omega_base:.3f} to {floor_max:.3f}"
            )
            omega_base = floor_max
            floor_constraint_applied = True

    omega_base = _clamp(omega_base, 0.0, 1.0)

    logger.debug(
        f"compute_omega_base: ω_sev={omega_sev:.3f}, ω_theory={omega_theory:.3f}, "
        f"is_mechanism={is_mechanism_edge}, constraint_applied={floor_constraint_applied} → ω_base={omega_base:.3f}"
    )

    return omega_base, floor_constraint_applied


def compute_omega_conf(
    n_uncontrolled_confounds: int = 0,
    has_randomization: bool = False,
    has_active_control: bool = False,
) -> float:
    """
    Compute confound risk adjustment (ω_conf).

    Based on Woodward's interventionist framing: how many plausible confounds remain
    uncontrolled after accounting for randomization and active controls?

    Mapping (Woodward-based):
        - 0 uncontrolled confounds + randomization: 0.95-1.00
        - 0-1 uncontrolled + randomization: 0.85-0.95
        - 1-2 uncontrolled + some control: 0.70-0.89
        - 2-3 uncontrolled + poor control: 0.50-0.69
        - 3+ uncontrolled: 0.30-0.49

    This function uses a simplified heuristic based on argument count:
        n_uncontrolled_confounds=0: 0.90 (tight controls)
        n_uncontrolled_confounds=1-2: 0.70 (multiple possible confounds)
        n_uncontrolled_confounds=3+: 0.40 (many confounds likely)

    Adjustments:
        +0.08 if has_randomization
        +0.05 if has_active_control

    Args:
        n_uncontrolled_confounds: Number of plausible confounds not controlled.
        has_randomization: Whether design employs randomization (RCT).
        has_active_control: Whether design includes active control condition.

    Returns:
        ω_conf ∈ [0, 1] (1.0 = low risk, 0.0 = high risk)

    Reference:
        Woodward (2003) Making Things Happen; ATLAS §48.3B

    Example:
        >>> omega_conf = compute_omega_conf(
        ...     n_uncontrolled_confounds=1,
        ...     has_randomization=True,
        ...     has_active_control=False
        ... )  # Returns ~0.90
    """
    # Base confound risk by count
    if n_uncontrolled_confounds == 0:
        omega_conf = 0.95
    elif n_uncontrolled_confounds <= 2:
        omega_conf = 0.70
    else:
        omega_conf = 0.40

    # Adjustments for control mechanisms
    if has_randomization:
        omega_conf += 0.08
    if has_active_control:
        omega_conf += 0.05

    omega_conf = _clamp(omega_conf, 0.0, 1.0)

    logger.debug(
        f"compute_omega_conf: n_confounds={n_uncontrolled_confounds}, "
        f"randomized={has_randomization}, active_control={has_active_control} → ω_conf={omega_conf:.3f}"
    )

    return omega_conf


def compute_omega_rep(
    n_independent_replications: int = 0,
    n_conceptual_replications: int = 0,
) -> float:
    """
    Compute replication adjustment (ω_rep).

    Replication strengthens warrant by demonstrating robustness across samples,
    contexts, and operationalizations. Independent replications (same method,
    different labs) are stronger than conceptual replications (different methods,
    same construct).

    Mapping:
        1+ independent replications: 1.00 (robust across labs)
        At least one independent replication: 0.85 (some external validation)
        Conceptual replications only: 0.70 (method variation)
        Single study: 0.55 (no external validation)

    Args:
        n_independent_replications: Number of independent replications
            (same method, different lab/sample).
        n_conceptual_replications: Number of conceptual replications
            (different method/operationalization, same construct).

    Returns:
        ω_rep ∈ [0, 1]

    Reference:
        Nosek & Errington (2020) on replication robustness; ATLAS §48.3B

    Example:
        >>> omega_rep = compute_omega_rep(
        ...     n_independent_replications=2,
        ...     n_conceptual_replications=0
        ... )  # Returns 1.00
    """
    if n_independent_replications >= 1:
        omega_rep = 1.00
    elif n_independent_replications > 0:
        omega_rep = 0.85
    elif n_conceptual_replications > 0:
        omega_rep = 0.70
    else:
        omega_rep = 0.55

    logger.debug(
        f"compute_omega_rep: n_independent={n_independent_replications}, "
        f"n_conceptual={n_conceptual_replications} → ω_rep={omega_rep:.3f}"
    )

    return omega_rep


def compute_omega_meta(
    publication_type: PublicationType = PublicationType.PEER_REVIEWED,
    is_pre_registered: bool = False,
) -> float:
    """
    Compute meta-calibration adjustment (ω_meta).

    Panel Revision R2: Citation count and author prestige are EXCLUDED from
    formal computation. Only publication type and pre-registration status matter.

    Mapping:
        Registered report: 1.00
        Peer-reviewed (journal or conference): 0.90
        Preprint or non-peer-reviewed: 0.80
        Grey literature (report, dissertation, blog): 0.70

    Pre-registration bonus: +0.10 if pre-registered (applies to all types)

    Args:
        publication_type: PublicationType enum (journal, preprint, grey, etc.).
        is_pre_registered: Whether study was pre-registered before data collection.

    Returns:
        ω_meta ∈ [0, 1]

    Reference:
        ATLAS §48.3B (Panel Revision R2): Excludes citation count and author prestige

    Example:
        >>> omega_meta = compute_omega_meta(
        ...     publication_type=PublicationType.PEER_REVIEWED,
        ...     is_pre_registered=True
        ... )  # Returns 1.00
    """
    base_meta = {
        PublicationType.REGISTERED_REPORT: 1.00,
        PublicationType.PEER_REVIEWED: 0.90,
        PublicationType.PREPRINT: 0.80,
        PublicationType.GREY_LITERATURE: 0.70,
    }

    omega_meta = base_meta.get(publication_type, 0.70)

    if is_pre_registered:
        omega_meta += 0.10

    omega_meta = _clamp(omega_meta, 0.0, 1.0)

    logger.debug(
        f"compute_omega_meta: pub_type={publication_type.value}, "
        f"pre_reg={is_pre_registered} → ω_meta={omega_meta:.3f}"
    )

    return omega_meta


def compute_omega_source(
    pre_registered: bool = False,
    blinded: bool = False,
    independence_of_evidence: float = 0.5,
    sample_adequacy: float = 0.5,
) -> float:
    """
    Compute source quality modifier (ω_source) for warrant strength.

    Sprint B (CW directive): Source Quality feeds into ω as a 5th factor,
    NOT into legacy credence. This is a multiplicative modifier in [0.7, 1.1]
    based on pre-registration, blinding, independence, and sample adequacy.

    The range [0.7, 1.1] means:
    - Poor source quality reduces ω by up to 30%
    - Excellent source quality can boost ω by up to 10%
    - Neutral source quality (ω_source = 1.0) has no effect

    Mapping:
        Base: 0.85 (neutral point)
        +0.08 for pre-registration (reduces researcher degrees of freedom)
        +0.07 for blinding (reduces experimenter bias)
        +0.05 × independence (elevated per Cartwright D-PANEL.3)
        +0.05 × sample_adequacy (floor = 0.0 for N < 10)

    Args:
        pre_registered: Whether study was pre-registered (OSF, AsPredicted).
        blinded: Whether study employed blinding.
        independence_of_evidence: Independence from same-lab cluster [0, 1].
        sample_adequacy: N-adequacy for design type [0, 1].

    Returns:
        ω_source ∈ [0.7, 1.1]

    Reference:
        CW Sprint B directive: SQ indicators → [0.7, 1.1] multiplier → 5th factor in ω.
        source_quality.py SourceQualityIndicators for component definitions.
    """
    omega_source = 0.85  # Neutral base

    if pre_registered:
        omega_source += 0.08
    if blinded:
        omega_source += 0.07

    # Independence: 0→0, 0.5→0.025, 1.0→0.05
    omega_source += 0.05 * _clamp(independence_of_evidence, 0.0, 1.0)
    # Sample adequacy: 0→0, 0.5→0.025, 1.0→0.05
    omega_source += 0.05 * _clamp(sample_adequacy, 0.0, 1.0)

    omega_source = _clamp(omega_source, 0.7, 1.1)

    logger.debug(
        f"compute_omega_source: pre_reg={pre_registered}, blinded={blinded}, "
        f"independence={independence_of_evidence:.2f}, sample_adequacy={sample_adequacy:.2f} "
        f"→ ω_source={omega_source:.3f}"
    )

    return omega_source


def compute_omega(
    omega_base: float,
    omega_conf: float = 1.0,
    omega_rep: float = 0.55,
    omega_meta: float = 0.90,
    omega_source: float = 1.0,
) -> float:
    """
    Compute composite warrant strength (ω).

    ω = ω_base × ω_conf × ω_rep × ω_meta × ω_source

    This is a multiplicative model: all components must be sufficiently strong
    for warrant to be high. A single weak component can significantly reduce
    overall warrant (e.g., poor replication → ω_rep=0.55 → composite reduced).

    Sprint B addition: ω_source ∈ [0.7, 1.1] modulates based on source quality
    (pre-registration, blinding, independence, sample adequacy).

    Args:
        omega_base: Base warrant from experimental severity + theory support.
        omega_conf: Confound risk adjustment (1.0 = low risk).
        omega_rep: Replication adjustment (1.0 = multiple independent replications).
        omega_meta: Meta-calibration (publication type + registration).
        omega_source: Source quality modifier (1.0 = neutral, [0.7, 1.1]).

    Returns:
        ω ∈ [0, 1]

    Reference:
        ATLAS §48.3B: "ω = ω_base × ω_conf × ω_rep × ω_meta × ω_source"
    """
    # Clamp all inputs to [0, 1] except omega_source which is [0.7, 1.1]
    omega_base = _clamp(omega_base, 0.0, 1.0)
    omega_conf = _clamp(omega_conf, 0.0, 1.0)
    omega_rep = _clamp(omega_rep, 0.0, 1.0)
    omega_meta = _clamp(omega_meta, 0.0, 1.0)
    omega_source = _clamp(omega_source, 0.7, 1.1)

    omega = omega_base * omega_conf * omega_rep * omega_meta * omega_source

    logger.debug(
        f"compute_omega: ω_base={omega_base:.3f}, ω_conf={omega_conf:.3f}, "
        f"ω_rep={omega_rep:.3f}, ω_meta={omega_meta:.3f}, "
        f"ω_source={omega_source:.3f} → ω={omega:.3f}"
    )

    return _clamp(omega, 0.0, 1.0)


def compute_omega_from_extraction(
    finding: Dict,
    theory_id: Optional[str] = None,
    tea_scores: Optional[Dict[str, float]] = None,
) -> OmegaResult:
    """
    Convenience function: compute full OmegaResult from an extraction finding dict.

    This function is the primary entry point for integrating warrant computation
    into the extraction pipeline. It handles a finding dict with extraction metadata
    and returns a complete auditable OmegaResult.

    Expected finding dict keys (all optional, sensible defaults provided):
        - design_type: DesignType enum or string name
        - sample_size: int or None
        - pre_registered: bool
        - blinded: bool
        - self_report_only: bool
        - n_uncontrolled_confounds: int (default 0)
        - has_randomization: bool
        - has_active_control: bool
        - n_independent_replications: int
        - n_conceptual_replications: int
        - publication_type: PublicationType enum or string name
        - mechanism_specificity: float (for theory edges)
        - is_mechanism_edge: bool

    Args:
        finding: Dictionary from extraction result containing study metadata.
        theory_id: Optional theory identifier for theory support computation.
        tea_scores: Pre-loaded TEA scores. If None, loads from default path.

    Returns:
        OmegaResult with all components computed and clamped to [0, 1].

    Raises:
        ValueError: If design_type or publication_type is invalid string.

    Example:
        >>> finding = {
        ...     "design_type": "standard_rct",
        ...     "sample_size": 150,
        ...     "pre_registered": True,
        ...     "blinded": True,
        ...     "n_independent_replications": 1,
        ...     "publication_type": "peer_reviewed",
        ...     "is_mechanism_edge": True,
        ...     "mechanism_specificity": 0.80
        ... }
        >>> result = compute_omega_from_extraction(finding, theory_id="attention_restoration_theory")
        >>> print(result.omega)  # ~0.75
        >>> print(result.to_dict())  # Full auditability dict
    """
    # Parse design_type
    design_type_val = finding.get("design_type", "standard_rct")
    if isinstance(design_type_val, str):
        try:
            design_type = DesignType[design_type_val.upper().replace("-", "_")]
        except KeyError:
            raise ValueError(
                f"Invalid design_type: '{design_type_val}'. "
                f"Must be one of: {[dt.value for dt in DesignType]}"
            )
    else:
        design_type = design_type_val

    # Parse publication_type
    pub_type_val = finding.get("publication_type", "peer_reviewed")
    if isinstance(pub_type_val, str):
        try:
            pub_type = PublicationType[pub_type_val.upper().replace("-", "_")]
        except KeyError:
            raise ValueError(
                f"Invalid publication_type: '{pub_type_val}'. "
                f"Must be one of: {[pt.value for pt in PublicationType]}"
            )
    else:
        pub_type = pub_type_val

    # Extract study characteristics with defaults
    sample_size = finding.get("sample_size")
    pre_registered = finding.get("pre_registered", False)
    blinded = finding.get("blinded", False)
    self_report_only = finding.get("self_report_only", False)
    n_uncontrolled_confounds = finding.get("n_uncontrolled_confounds", 0)
    has_randomization = finding.get("has_randomization", design_type == DesignType.STANDARD_RCT)
    has_active_control = finding.get("has_active_control", False)
    n_independent_replications = finding.get("n_independent_replications", 0)
    n_conceptual_replications = finding.get("n_conceptual_replications", 0)
    is_mechanism_edge = finding.get("is_mechanism_edge", False)
    mechanism_specificity = finding.get("mechanism_specificity", 0.0)

    # Load TEA scores if needed
    if tea_scores is None and theory_id is not None:
        tea_scores = load_tea_scores()

    # Compute all components
    omega_sev = compute_omega_sev(
        design_type=design_type,
        sample_size=sample_size,
        pre_registered=pre_registered,
        blinded=blinded,
        self_report_only=self_report_only,
    )

    omega_theory = 0.0
    if is_mechanism_edge and theory_id:
        omega_theory = compute_omega_theory(
            theory_id=theory_id,
            mechanism_specificity=mechanism_specificity,
            tea_scores=tea_scores,
        )

    omega_base, floor_constraint_applied = compute_omega_base(
        omega_sev=omega_sev,
        omega_theory=omega_theory,
        is_mechanism_edge=is_mechanism_edge,
    )

    omega_conf = compute_omega_conf(
        n_uncontrolled_confounds=n_uncontrolled_confounds,
        has_randomization=has_randomization,
        has_active_control=has_active_control,
    )

    omega_rep = compute_omega_rep(
        n_independent_replications=n_independent_replications,
        n_conceptual_replications=n_conceptual_replications,
    )

    omega_meta = compute_omega_meta(
        publication_type=pub_type,
        is_pre_registered=pre_registered,
    )

    # Sprint B: Compute source quality modifier
    # SQ indicators from extraction metadata
    independence = finding.get("independence_of_evidence", 0.5)
    sample_adequacy = finding.get("sample_adequacy", 0.5)
    # Estimate sample adequacy from sample_size if not explicit
    if "sample_adequacy" not in finding and sample_size is not None:
        if sample_size >= 200:
            sample_adequacy = 1.0
        elif sample_size >= 50:
            sample_adequacy = 0.7
        elif sample_size >= 20:
            sample_adequacy = 0.4
        else:
            sample_adequacy = 0.1

    omega_source = compute_omega_source(
        pre_registered=pre_registered,
        blinded=blinded,
        independence_of_evidence=independence,
        sample_adequacy=sample_adequacy,
    )

    omega = compute_omega(
        omega_base=omega_base,
        omega_conf=omega_conf,
        omega_rep=omega_rep,
        omega_meta=omega_meta,
        omega_source=omega_source,
    )

    notes = (
        f"Computed from {design_type.value} design; "
        f"theory_id={theory_id}; "
        f"is_mechanism_edge={is_mechanism_edge}; "
        f"ω_source={omega_source:.3f}"
    )

    result = OmegaResult(
        omega=omega,
        omega_base=omega_base,
        omega_sev=omega_sev,
        omega_theory=omega_theory,
        omega_conf=omega_conf,
        omega_rep=omega_rep,
        omega_meta=omega_meta,
        omega_source=omega_source,
        floor_constraint_applied=floor_constraint_applied,
        design_type=design_type.value,
        notes=notes,
    )

    logger.info(f"compute_omega_from_extraction: result.omega={result.omega:.3f}, notes={notes}")

    return result


def _logit(p: float) -> float:
    """Log-odds transformation: logit(p) = ln(p / (1 - p))."""
    p = _clamp(p, 1e-10, 1.0 - 1e-10)
    return math.log(p / (1.0 - p))


def _sigmoid(x: float) -> float:
    """Sigmoid (logistic) function: σ(x) = 1 / (1 + exp(-x))."""
    if x > 100:
        return 1.0
    if x < -100:
        return 0.0
    return 1.0 / (1.0 + math.exp(-x))


# Canonical discount factors (d) per warrant type — imported from epistemic_projection.py
# These represent transfer reliability: how well does this TYPE of evidence generalize?
CANONICAL_DISCOUNT_FACTORS: Dict[str, float] = {
    "constitutive": 0.95,
    "mechanism": 0.80,
    "empirical_association": 0.80,
    "functional": 0.65,
    "capacity": 0.55,
    "analogical": 0.40,
    "theory_derived": 0.25,
}


def compute_credence_from_warrants(edges: List[Dict]) -> float:
    """
    Parallel projection formula: compute credence from warrant-based edges.

    Formula (ATLAS §48.3B, integrated with §48.1 projection calculus):

        credence(belief) = σ(Σ d_i · ω_i · δ_i · logit(p_lab_i))

    Where:
        σ:       sigmoid function
        d_i:     canonical discount factor for warrant type τ_i (from CANONICAL_DISCOUNT_FACTORS)
        ω_i:     warrant strength (this module's primary output)
        δ_i:     population transfer factor ∈ [0, 1] (1.0 if populations identical)
        p_lab_i: laboratory effect probability ∈ (0, 1) — the observed probability of the
                 effect in the original study context

    Each edge represents an independent line of evidence. In log-odds space,
    independent evidence sums (equivalent to Bayesian updating with independent
    likelihood ratios). The sigmoid maps the cumulative log-odds back to [0, 1].

    Args:
        edges: List of edge dicts, each containing:
            - "p_lab": Laboratory effect probability ∈ (0, 1)
            - "tau": Warrant type string (key into CANONICAL_DISCOUNT_FACTORS)
            - "omega": Warrant strength ω ∈ [0, 1] (from compute_omega_from_extraction)
            - "delta": Population transfer factor ∈ [0, 1] (default 1.0)

    Returns:
        credence ∈ (0, 1), with 0.5 = neutral (no evidence either way)

    Reference:
        ATLAS §48.3B: "credence(belief) = σ(Σ d_i · ω_i · δ_i · logit(p_lab_i))"
        Epistemic_projection.py project_parallel() for the same formula on BN edges

    Example:
        >>> edges = [
        ...     {"p_lab": 0.75, "tau": "empirical_association", "omega": 0.85, "delta": 1.0},
        ...     {"p_lab": 0.65, "tau": "mechanism", "omega": 0.70, "delta": 0.90}
        ... ]
        >>> credence = compute_credence_from_warrants(edges)
        >>> print(f"{credence:.3f}")  # ~0.72
    """
    if not edges:
        logger.warning("compute_credence_from_warrants called with empty edges list")
        return 0.5  # Neutral credence — no evidence

    logit_sum = 0.0

    for edge in edges:
        p_lab = edge.get("p_lab", 0.5)
        tau = edge.get("tau", "empirical_association")
        omega = edge.get("omega", 0.5)
        delta = edge.get("delta", 1.0)

        d = CANONICAL_DISCOUNT_FACTORS.get(tau, 0.50)

        logit_p = _logit(p_lab)
        contribution = d * omega * delta * logit_p
        logit_sum += contribution

        logger.debug(
            f"Edge contribution: τ={tau}, d={d:.3f}, ω={omega:.3f}, "
            f"δ={delta:.3f}, logit(p_lab)={logit_p:.3f} → {contribution:.3f}"
        )

    credence = _sigmoid(logit_sum)

    logger.info(
        f"compute_credence_from_warrants: {len(edges)} edges, "
        f"logit_sum={logit_sum:.3f} → credence={credence:.3f}"
    )

    return credence
