"""
generalization_tree.py — T3 Generalization Tree & Subsumption Engine
====================================================================

The core data structure for T3 belief formation. Groups individual
EN findings into generalized beliefs at the appropriate granularity.

Design principles:
  1. Beliefs form at the FIRST level where ≥3 independent sources converge
  2. Subsumption requires MECHANISM IDENTITY (Cartwright's capacities)
  3. Different ACCESS LEVELS are never merged (Barrett)
  4. Parametric stimuli merge into ranges when direction is consistent
  5. Missing subtypes → coverage gap, not overgeneralization
  6. Delivery mode (VR vs real) is a BOUNDARY CONDITION facet
  7. NASCENT beliefs (single-article findings) are PRESERVED as search seeds —
     they are exactly the claims we want to find more articles about

Informed by:
  - Tenenbaum & Griffiths (2001): Bayesian generalization
  - Lakatos (1978): Research programmes — progressive vs degenerating
  - Cartwright (1989): Nature's capacities and their measurement
  - Quine (1969): Natural kinds — projectibility

ADR: Extension layer — new file, no existing code modified.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, FrozenSet, List, Optional, Set, Tuple

from src.services.stimulus_taxonomy import (
    StimulusTaxonomy, get_stimulus_taxonomy,
    DeliveryMode, SensoryModality, ManipulationType,
)
from src.services.dv_generalization import (
    can_generalize_dvs, dv_common_ancestor, dv_equivalence_class,
    DVAccessLevel, get_dv_node,
)

LOGGER = logging.getLogger(__name__)

# Minimum independent sources to form a generalized belief
MIN_SOURCES_FOR_BELIEF = 3

# Minimum coverage of subtypes to permit category-level generalization
MIN_SUBTYPE_COVERAGE = 0.5


# ══════════════════════════════════════════════════════════════════
# Belief Granularity Levels
# ══════════════════════════════════════════════════════════════════

class GranularityLevel(Enum):
    """How general a T3 belief is."""
    SPECIFIC = 0        # Exact stimulus + measure (9' ceiling → fluency)
    PARAMETRIC = 1      # Range of numerical values (high ceiling → fluency)
    CONSTRUCT = 2       # Same construct measured differently (high ceiling → creativity)
    CATEGORY = 3        # Category-level IV + DV (ceiling height → cognition)
    DOMAIN = 4          # Domain-level (spatial → cognition) — usually too broad


class BeliefStatus(Enum):
    """Status of a T3 belief."""
    NASCENT = "nascent"            # 1 source — single-article finding, search seed
    TENTATIVE = "tentative"        # 2 sources, not yet established
    ESTABLISHED = "established"    # ≥3 sources, consistent direction
    CONTESTED = "contested"        # ≥3 sources but conflicting directions
    BOUNDARY = "boundary"          # Discovered moderator splits the belief


# ══════════════════════════════════════════════════════════════════
# Finding (input to generalization)
# ══════════════════════════════════════════════════════════════════

@dataclass
class Finding:
    """
    A single empirical finding from the EN, ready for T3 aggregation.

    Extracted from Belief objects in the web_of_belief.
    """
    finding_id: str                    # EN belief_id
    iv_node: str                       # stimulus taxonomy node
    dv_node: str                       # DV taxonomy node
    effect_direction: str              # positive/negative/null
    effect_size: Optional[float] = None  # Cohen's d or equivalent
    sample_n: Optional[int] = None
    paper_id: Optional[str] = None
    delivery_mode: DeliveryMode = DeliveryMode.UNSPECIFIED
    modality: SensoryModality = SensoryModality.UNSPECIFIED
    population: str = ""               # Population description
    temporal_scope: str = ""           # Duration/timing
    study_design: str = ""             # RCT, quasi-experimental, etc.
    access_level: DVAccessLevel = DVAccessLevel.UNSPECIFIED
    publication_year: Optional[int] = None  # For warrant decay (Wave 6)


# ══════════════════════════════════════════════════════════════════
# T3 Belief Node
# ══════════════════════════════════════════════════════════════════

@dataclass
class T3Belief:
    """A consolidated T3 empirical belief at a specific granularity level."""
    t3_id: str                                # e.g., "t3:spatial.height→cog.creativity"
    iv_node: str                              # Stimulus taxonomy node (may be parent)
    dv_node: str                              # DV taxonomy node (may be parent)
    granularity: GranularityLevel
    status: BeliefStatus = BeliefStatus.TENTATIVE

    # Evidence
    effect_direction: str = "positive"        # consensus direction
    n_positive: int = 0
    n_negative: int = 0
    n_null: int = 0
    source_findings: List[str] = field(default_factory=list)  # Finding IDs
    aggregated_effect_size: Optional[float] = None  # Meta-analytic mean
    confidence: float = 0.5                   # Bayesian posterior

    # Boundary conditions
    boundary_conditions: Dict[str, str] = field(default_factory=dict)
    delivery_modes_tested: Set[str] = field(default_factory=set)
    populations_tested: Set[str] = field(default_factory=set)

    # Linkage
    linked_templates: List[str] = field(default_factory=list)  # T2 template IDs
    mechanism_ids: List[str] = field(default_factory=list)
    coverage_gaps: List[str] = field(default_factory=list)

    # Sample size (S2: weighted aggregation)
    total_sample_n: int = 0  # Sum of sample sizes across all findings

    # Defeasibility tracking (S3-5, Expert Decision #11)
    defeaters: List[Dict[str, str]] = field(default_factory=list)
    status_history: List[Dict[str, str]] = field(default_factory=list)
    effect_size_metric: str = "d"  # Canonical metric (always Cohen's d)
    effect_size_standardized: bool = False  # Whether ES was converted

    # I² heterogeneity (Wave 6, V10 panel #18 Methodologist)
    i_squared: Optional[float] = None       # 0-100%, between-study variability
    cochran_q: Optional[float] = None       # Cochran's Q statistic
    i_squared_label: str = ""               # "low"/"moderate"/"high"/"very_high"

    # Warrant decay (Wave 6, V10 panel #2 Epistemologist)
    warrant_decay_factor: float = 1.0       # 0.0-1.0, temporal discount on confidence
    evidence_years: List[int] = field(default_factory=list)  # Publication years
    median_evidence_year: Optional[int] = None
    decayed_confidence: Optional[float] = None  # confidence × warrant_decay_factor

    @property
    def n_total(self) -> int:
        return self.n_positive + self.n_negative + self.n_null

    @property
    def consistency(self) -> float:
        """Fraction of findings in the majority direction."""
        if self.n_total == 0:
            return 0.0
        majority = max(self.n_positive, self.n_negative, self.n_null)
        return majority / self.n_total

    @property
    def is_nascent(self) -> bool:
        """Is this a nascent belief (single-article search seed)?"""
        return self.status == BeliefStatus.NASCENT

    @property
    def search_seed_query(self) -> str:
        """Generate a search query to find more articles like this nascent belief."""
        tax = get_stimulus_taxonomy()
        iv = tax.get(self.iv_node)
        dv = get_dv_node(self.dv_node)
        iv_label = iv.label if iv else self.iv_node
        dv_label = dv.label if dv else self.dv_node
        return f"{iv_label} effect on {dv_label}"

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "t3_id": self.t3_id,
            "iv_node": self.iv_node,
            "dv_node": self.dv_node,
            "granularity": self.granularity.value,
            "status": self.status.value,
            "effect_direction": self.effect_direction,
            "n_positive": self.n_positive,
            "n_negative": self.n_negative,
            "n_null": self.n_null,
            "n_total": self.n_total,
            "consistency": round(self.consistency, 3),
            "confidence": round(self.confidence, 3),
            "aggregated_effect_size": self.aggregated_effect_size,
            "n_source_findings": len(self.source_findings),
            "delivery_modes_tested": sorted(self.delivery_modes_tested),
            "populations_tested": sorted(self.populations_tested),
            "linked_templates": self.linked_templates,
            "coverage_gaps": self.coverage_gaps,
            "boundary_conditions": self.boundary_conditions,
            "i_squared": round(self.i_squared, 1) if self.i_squared is not None else None,
            "i_squared_label": self.i_squared_label,
            "warrant_decay_factor": round(self.warrant_decay_factor, 3),
            "decayed_confidence": round(self.decayed_confidence, 3) if self.decayed_confidence is not None else None,
            "median_evidence_year": self.median_evidence_year,
        }
        if self.is_nascent:
            d["search_seed_query"] = self.search_seed_query
        return d

    @property
    def natural_language(self) -> str:
        """Generate a human-readable summary."""
        tax = get_stimulus_taxonomy()
        iv = tax.get(self.iv_node)
        dv = get_dv_node(self.dv_node)
        iv_label = iv.label if iv else self.iv_node
        dv_label = dv.label if dv else self.dv_node

        direction_word = {
            "positive": "increases",
            "negative": "decreases",
            "null": "does not significantly affect",
            "mixed": "has mixed effects on",
        }.get(self.effect_direction, "affects")

        conf_word = "strongly" if self.confidence > 0.7 else "moderately" if self.confidence > 0.5 else "tentatively"

        return (
            f"{iv_label} {conf_word} {direction_word} {dv_label} "
            f"(n={self.n_total} studies, consistency={self.consistency:.0%})"
        )


# ══════════════════════════════════════════════════════════════════
# Coverage Gap
# ══════════════════════════════════════════════════════════════════

@dataclass
class CoverageGap:
    """An identified gap in empirical coverage."""
    gap_id: str
    iv_node: str
    dv_node: str
    gap_type: str                # "untested_subtype", "missing_modality", "missing_delivery", "missing_population"
    description: str
    priority: float = 0.5        # 0-1, higher = more important to fill
    search_query: str = ""       # Suggested search query

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gap_id": self.gap_id,
            "iv_node": self.iv_node,
            "dv_node": self.dv_node,
            "gap_type": self.gap_type,
            "description": self.description,
            "priority": round(self.priority, 3),
            "search_query": self.search_query,
        }


# ══════════════════════════════════════════════════════════════════
# Generalization Engine
# ══════════════════════════════════════════════════════════════════

class GeneralizationEngine:
    """
    Builds the T3 belief tree from EN findings.

    Algorithm (Tenenbaum-inspired):
    1. Group findings by (iv_node, dv_node) at leaf level
    2. At each group:
       a. If ≥3 sources → form SPECIFIC belief
       b. Check if parametric merge is possible (same IV parent, same direction)
       c. Check if construct merge is possible (DV equivalence class)
       d. Check if category merge is possible (IV parent + DV parent)
    3. Apply boundary condition detection (when direction conflicts exist)
    4. Compute coverage gaps for formed beliefs
    """

    def __init__(self, taxonomy: Optional[StimulusTaxonomy] = None):
        self.taxonomy = taxonomy or get_stimulus_taxonomy()
        self.findings: List[Finding] = []
        self.beliefs: Dict[str, T3Belief] = {}
        self.gaps: List[CoverageGap] = []

    def add_finding(self, finding: Finding) -> None:
        """Add a finding to the aggregation pool."""
        self.findings.append(finding)

    def add_findings(self, findings: List[Finding]) -> None:
        self.findings.extend(findings)

    def aggregate(self) -> Dict[str, T3Belief]:
        """
        Run the full aggregation pipeline.

        Returns dict of t3_id → T3Belief.
        """
        LOGGER.info("Aggregating %d findings into T3 beliefs", len(self.findings))
        self.beliefs = {}
        self.gaps = []

        # Step 1: Group by (iv_node, dv_node) — leaf level
        groups = self._group_findings()

        # Step 2: Form specific beliefs
        for key, group_findings in groups.items():
            belief = self._form_specific_belief(key, group_findings)
            self.beliefs[belief.t3_id] = belief

        # Step 3: Try parametric merges
        parametric_beliefs = self._try_parametric_merges()
        self.beliefs.update(parametric_beliefs)

        # Step 4: Try construct merges
        construct_beliefs = self._try_construct_merges()
        self.beliefs.update(construct_beliefs)

        # Step 5: Detect boundary conditions
        self._detect_boundaries()

        # Step 6: Compute coverage gaps
        self._compute_coverage_gaps()

        # Step 7: Generate search seeds for nascent beliefs
        self._generate_nascent_search_seeds()

        n_nascent = sum(1 for b in self.beliefs.values() if b.status == BeliefStatus.NASCENT)
        LOGGER.info(
            "Aggregation complete: %d beliefs (%d established, %d tentative, %d nascent, %d contested), %d gaps",
            len(self.beliefs),
            sum(1 for b in self.beliefs.values() if b.status == BeliefStatus.ESTABLISHED),
            sum(1 for b in self.beliefs.values() if b.status == BeliefStatus.TENTATIVE),
            n_nascent,
            sum(1 for b in self.beliefs.values() if b.status == BeliefStatus.CONTESTED),
            len(self.gaps),
        )
        return self.beliefs

    def _group_findings(self) -> Dict[Tuple[str, str], List[Finding]]:
        """Group findings by (iv_node, dv_node)."""
        groups: Dict[Tuple[str, str], List[Finding]] = {}
        for f in self.findings:
            key = (f.iv_node, f.dv_node)
            groups.setdefault(key, []).append(f)
        return groups

    def _form_specific_belief(
        self,
        key: Tuple[str, str],
        findings: List[Finding],
    ) -> T3Belief:
        """Form a belief from a specific (iv, dv) group."""
        iv_node, dv_node = key
        t3_id = f"t3:{iv_node}→{dv_node}"

        n_pos = sum(1 for f in findings if f.effect_direction == "positive")
        n_neg = sum(1 for f in findings if f.effect_direction == "negative")
        n_null = sum(1 for f in findings if f.effect_direction == "null")

        # Consensus direction
        if n_pos > n_neg and n_pos > n_null:
            direction = "positive"
        elif n_neg > n_pos and n_neg > n_null:
            direction = "negative"
        elif n_null > n_pos and n_null > n_neg:
            direction = "null"
        else:
            direction = "mixed"

        # Status — nascent (1 source) vs tentative (2) vs established (≥3)
        total = len(findings)
        if total >= MIN_SOURCES_FOR_BELIEF:
            if direction == "mixed":
                status = BeliefStatus.CONTESTED
            else:
                status = BeliefStatus.ESTABLISHED
        elif total == 1:
            status = BeliefStatus.NASCENT  # Single-article search seed
        else:
            status = BeliefStatus.TENTATIVE  # 2 sources, not yet established

        # Meta-analytic effect size — sample-size weighted (S2: Expert Decision #5)
        effect_sizes = []
        weights = []
        total_n = 0
        for f in findings:
            es = f.effect_size
            n = f.sample_n
            if n is not None:
                try:
                    total_n += int(n)
                except (TypeError, ValueError):
                    pass
            if es is not None:
                try:
                    es_val = float(es)
                    # Weight by sqrt(N) if available, else equal weight
                    w = math.sqrt(int(n)) if n and int(n) > 0 else 1.0
                    effect_sizes.append(es_val)
                    weights.append(w)
                except (TypeError, ValueError):
                    pass
        if effect_sizes:
            total_w = sum(weights)
            agg_es = sum(e * w for e, w in zip(effect_sizes, weights)) / total_w if total_w > 0 else None
        else:
            agg_es = None

        # Confidence (Bayesian: prior=0.5, each confirming study increases)
        # S2: Add sample-size bonus — larger studies increase confidence
        confidence = self._compute_confidence(n_pos, n_neg, n_null, total_n)

        # I² heterogeneity (Wave 6, V10 #18 Methodologist)
        # Cochran's Q = Σ w_i (ES_i − ES_bar)² ; I² = max(0, (Q-df)/Q × 100)
        i_sq = None
        q_stat = None
        i_sq_label = ""
        if len(effect_sizes) >= 2 and agg_es is not None:
            q_stat = sum(w * (es - agg_es) ** 2 for es, w in zip(effect_sizes, weights))
            df = len(effect_sizes) - 1
            i_sq = max(0.0, (q_stat - df) / q_stat * 100.0) if q_stat > 0 else 0.0
            if i_sq < 25:
                i_sq_label = "low"
            elif i_sq < 50:
                i_sq_label = "moderate"
            elif i_sq < 75:
                i_sq_label = "high"
            else:
                i_sq_label = "very_high"

        # Warrant decay (Wave 6, V10 #2 Epistemologist)
        # Evidence older than 10 years gets discounted; half-life = 20 years
        import datetime as _dt
        current_year = _dt.datetime.now().year
        evidence_years = []
        for f in findings:
            # Try to extract year from finding_id or source
            yr = getattr(f, 'publication_year', None)
            if yr and isinstance(yr, int) and 1900 < yr <= current_year:
                evidence_years.append(yr)
        median_year = None
        decay_factor = 1.0
        if evidence_years:
            sorted_years = sorted(evidence_years)
            mid = len(sorted_years) // 2
            median_year = sorted_years[mid]
            age = current_year - median_year
            # Exponential decay: half-life of 20 years
            # Beliefs based on 2006 evidence → 50% warrant
            # Beliefs based on 2016 evidence → ~70% warrant
            # Beliefs based on 2024 evidence → ~98% warrant
            HALF_LIFE = 20.0
            decay_factor = 0.5 ** (age / HALF_LIFE) if age > 0 else 1.0

        # Collect facets
        delivery_modes = {f.delivery_mode.value for f in findings if f.delivery_mode != DeliveryMode.UNSPECIFIED}
        populations = {f.population for f in findings if f.population}

        # Mechanism linkage
        iv_tax_node = self.taxonomy.get(iv_node)
        mechanism_ids = list(iv_tax_node.mechanism_ids) if iv_tax_node else []

        return T3Belief(
            t3_id=t3_id,
            iv_node=iv_node,
            dv_node=dv_node,
            granularity=GranularityLevel.SPECIFIC,
            status=status,
            effect_direction=direction,
            n_positive=n_pos,
            n_negative=n_neg,
            n_null=n_null,
            source_findings=[f.finding_id for f in findings],
            aggregated_effect_size=agg_es,
            confidence=confidence,
            delivery_modes_tested=delivery_modes,
            populations_tested=populations,
            mechanism_ids=mechanism_ids,
            total_sample_n=total_n,
            i_squared=i_sq,
            cochran_q=q_stat,
            i_squared_label=i_sq_label,
            warrant_decay_factor=decay_factor,
            evidence_years=evidence_years,
            median_evidence_year=median_year,
            decayed_confidence=round(confidence * decay_factor, 4) if decay_factor < 1.0 else None,
        )

    def _compute_confidence(self, n_pos: int, n_neg: int, n_null: int,
                            total_sample_n: int = 0) -> float:
        """
        Bayesian posterior confidence with sample-size bonus.

        Using a simple beta model: prior Beta(1,1), each confirming study
        adds 1 to alpha, each contradicting adds 1 to beta.
        S2: Add sqrt(total_N)/100 bonus (capped at 0.05) for larger samples.
        """
        total = n_pos + n_neg + n_null
        if total == 0:
            return 0.5
        majority = max(n_pos, n_neg, n_null)
        minority = total - majority
        # Beta posterior: alpha = 1 + majority, beta = 1 + minority
        alpha = 1.0 + majority
        beta_param = 1.0 + minority
        posterior_mean = alpha / (alpha + beta_param)
        # S2: Sample-size bonus — larger cumulative N increases confidence
        if total_sample_n > 0:
            size_bonus = min(0.05, math.sqrt(total_sample_n) / 100.0)
            posterior_mean = min(0.99, posterior_mean + size_bonus)
        return posterior_mean

    def _try_parametric_merges(self) -> Dict[str, T3Belief]:
        """
        Merge beliefs at sibling parametric levels.

        Example: spatial.height.low + spatial.height.high → spatial.height
        if both have ≥1 finding and direction is consistent.
        """
        merged = {}
        # Group existing specific beliefs by IV parent
        parent_groups: Dict[Tuple[str, str], List[T3Belief]] = {}
        for belief in self.beliefs.values():
            if belief.granularity != GranularityLevel.SPECIFIC:
                continue
            iv_node = self.taxonomy.get(belief.iv_node)
            if iv_node and iv_node.parent_id:
                key = (iv_node.parent_id, belief.dv_node)
                parent_groups.setdefault(key, []).append(belief)

        for (iv_parent, dv_node), children in parent_groups.items():
            if len(children) < 2:
                continue

            # Check direction consistency
            directions = {b.effect_direction for b in children}
            if len(directions) == 1 or (directions <= {"positive", "null"} or directions <= {"negative", "null"}):
                # Consistent enough to merge
                total_findings = []
                n_pos = sum(b.n_positive for b in children)
                n_neg = sum(b.n_negative for b in children)
                n_null = sum(b.n_null for b in children)
                total = n_pos + n_neg + n_null

                if total >= MIN_SOURCES_FOR_BELIEF:
                    t3_id = f"t3:{iv_parent}→{dv_node}"
                    for b in children:
                        total_findings.extend(b.source_findings)

                    es_vals = [b.aggregated_effect_size for b in children if b.aggregated_effect_size is not None]
                    agg_es = sum(es_vals) / len(es_vals) if es_vals else None

                    merged[t3_id] = T3Belief(
                        t3_id=t3_id,
                        iv_node=iv_parent,
                        dv_node=dv_node,
                        granularity=GranularityLevel.PARAMETRIC,
                        status=BeliefStatus.ESTABLISHED,
                        effect_direction=max({"positive": n_pos, "negative": n_neg, "null": n_null},
                                             key=lambda d: {"positive": n_pos, "negative": n_neg, "null": n_null}[d]),
                        n_positive=n_pos,
                        n_negative=n_neg,
                        n_null=n_null,
                        source_findings=total_findings,
                        aggregated_effect_size=agg_es,
                        confidence=self._compute_confidence(n_pos, n_neg, n_null),
                        delivery_modes_tested=set().union(*(b.delivery_modes_tested for b in children)),
                        populations_tested=set().union(*(b.populations_tested for b in children)),
                        mechanism_ids=list(set().union(*(set(b.mechanism_ids) for b in children))),
                    )

        return merged

    def _try_construct_merges(self) -> Dict[str, T3Belief]:
        """
        Merge beliefs where DVs are in the same equivalence class.

        Example: cog.creativity.divergent.fluency + cog.creativity.divergent.originality
        → cog.creativity.divergent (if same IV and direction)
        """
        merged = {}
        # Group by (iv_node, dv_equivalence_class)
        equiv_groups: Dict[Tuple[str, str], List[T3Belief]] = {}
        for belief in self.beliefs.values():
            if belief.granularity != GranularityLevel.SPECIFIC:
                continue
            dv_node = get_dv_node(belief.dv_node)
            if dv_node and dv_node.equivalence_class:
                key = (belief.iv_node, dv_node.equivalence_class)
                equiv_groups.setdefault(key, []).append(belief)

        for (iv_node, equiv_class), children in equiv_groups.items():
            if len(children) < 2:
                continue

            # Find common DV ancestor
            dv_ids = [b.dv_node for b in children]
            dv_parent = dv_ids[0]
            for other_dv in dv_ids[1:]:
                ancestor = dv_common_ancestor(dv_parent, other_dv)
                if ancestor:
                    dv_parent = ancestor
                else:
                    break

            n_pos = sum(b.n_positive for b in children)
            n_neg = sum(b.n_negative for b in children)
            n_null = sum(b.n_null for b in children)
            total = n_pos + n_neg + n_null

            if total >= MIN_SOURCES_FOR_BELIEF:
                t3_id = f"t3:{iv_node}→{dv_parent}[{equiv_class}]"
                total_findings = []
                for b in children:
                    total_findings.extend(b.source_findings)

                merged[t3_id] = T3Belief(
                    t3_id=t3_id,
                    iv_node=iv_node,
                    dv_node=dv_parent,
                    granularity=GranularityLevel.CONSTRUCT,
                    status=BeliefStatus.ESTABLISHED,
                    effect_direction=max({"positive": n_pos, "negative": n_neg, "null": n_null},
                                         key=lambda d: {"positive": n_pos, "negative": n_neg, "null": n_null}[d]),
                    n_positive=n_pos,
                    n_negative=n_neg,
                    n_null=n_null,
                    source_findings=total_findings,
                    confidence=self._compute_confidence(n_pos, n_neg, n_null),
                )

        return merged

    def _detect_boundaries(self) -> None:
        """
        Detect boundary conditions: when a belief has mixed findings,
        check if delivery mode, population, or modality explains the split.
        """
        for belief in self.beliefs.values():
            if belief.status != BeliefStatus.CONTESTED:
                continue

            # Check if delivery mode splits the data
            if len(belief.delivery_modes_tested) > 1:
                belief.boundary_conditions["delivery_mode"] = (
                    f"Mixed results may reflect delivery mode differences: "
                    f"{', '.join(sorted(belief.delivery_modes_tested))}"
                )

            # Check if population splits the data
            if len(belief.populations_tested) > 1:
                belief.boundary_conditions["population"] = (
                    f"Mixed results may reflect population differences: "
                    f"{', '.join(sorted(belief.populations_tested))}"
                )

    def _compute_coverage_gaps(self) -> None:
        """
        Identify what hasn't been tested yet.

        For each established belief at a parent level, check which
        children haven't been tested.
        """
        for belief in self.beliefs.values():
            if belief.status not in (BeliefStatus.ESTABLISHED, BeliefStatus.CONTESTED):
                continue

            # Check untested IV subtypes
            iv_children = self.taxonomy.children(belief.iv_node)
            tested_iv_children = set()
            for specific in self.beliefs.values():
                if specific.granularity == GranularityLevel.SPECIFIC:
                    if self.taxonomy.is_ancestor_of(belief.iv_node, specific.iv_node):
                        tested_iv_children.add(specific.iv_node)

            for child in iv_children:
                if child.node_id not in tested_iv_children:
                    gap = CoverageGap(
                        gap_id=f"gap:{child.node_id}→{belief.dv_node}",
                        iv_node=child.node_id,
                        dv_node=belief.dv_node,
                        gap_type="untested_subtype",
                        description=f"{child.label} has not been tested for {belief.dv_node}",
                        priority=0.7 if belief.status == BeliefStatus.ESTABLISHED else 0.5,
                        search_query=f"{child.label} effect on {belief.dv_node}",
                    )
                    self.gaps.append(gap)
                    belief.coverage_gaps.append(gap.gap_id)

            # Check delivery mode gaps
            if len(belief.delivery_modes_tested) < 2 and belief.status == BeliefStatus.ESTABLISHED:
                for mode in [DeliveryMode.REAL, DeliveryMode.VR, DeliveryMode.PHOTOGRAPH]:
                    if mode.value not in belief.delivery_modes_tested:
                        gap = CoverageGap(
                            gap_id=f"gap:delivery:{mode.value}:{belief.t3_id}",
                            iv_node=belief.iv_node,
                            dv_node=belief.dv_node,
                            gap_type="missing_delivery",
                            description=f"Not tested with {mode.value} delivery",
                            priority=0.4,
                            search_query=f"{belief.iv_node} {belief.dv_node} {mode.value}",
                        )
                        self.gaps.append(gap)

    def _generate_nascent_search_seeds(self) -> None:
        """
        Generate search-seed gaps for every nascent belief.

        Nascent beliefs (single-article findings) are precisely the claims
        we want to search for more articles about. Each nascent belief
        produces a high-priority coverage gap with a targeted search query.
        """
        for belief in self.beliefs.values():
            if belief.status != BeliefStatus.NASCENT:
                continue
            gap = CoverageGap(
                gap_id=f"seed:{belief.t3_id}",
                iv_node=belief.iv_node,
                dv_node=belief.dv_node,
                gap_type="nascent_search_seed",
                description=(
                    f"Only 1 study found for '{belief.natural_language}'. "
                    f"Search for corroborating or contradicting evidence."
                ),
                priority=0.85,  # High — we specifically want to find more
                search_query=belief.search_seed_query,
            )
            self.gaps.append(gap)
            belief.coverage_gaps.append(gap.gap_id)

    # ── Query API ──

    def get_belief(self, iv_pattern: str, dv_pattern: str) -> Optional[T3Belief]:
        """Find a belief matching IV and DV patterns."""
        for belief in self.beliefs.values():
            if iv_pattern in belief.iv_node and dv_pattern in belief.dv_node:
                return belief
        return None

    def get_established_beliefs(self) -> List[T3Belief]:
        """Get all established T3 beliefs."""
        return [b for b in self.beliefs.values() if b.status == BeliefStatus.ESTABLISHED]

    def get_nascent_beliefs(self) -> List[T3Belief]:
        """Get all nascent beliefs (single-article search seeds).

        These are precisely the beliefs we want to find more articles about.
        Each nascent belief represents one article's claim that hasn't yet
        been corroborated — making it a prime target for literature search.
        """
        return sorted(
            [b for b in self.beliefs.values() if b.status == BeliefStatus.NASCENT],
            key=lambda b: b.t3_id,
        )

    def get_nascent_search_queries(self) -> List[Dict[str, str]]:
        """Get search queries derived from nascent beliefs.

        Returns list of {t3_id, query, iv_label, dv_label, direction}
        suitable for feeding into article acquisition pipeline.
        """
        results = []
        for belief in self.get_nascent_beliefs():
            results.append({
                "t3_id": belief.t3_id,
                "query": belief.search_seed_query,
                "iv_node": belief.iv_node,
                "dv_node": belief.dv_node,
                "direction": belief.effect_direction,
                "source_paper": belief.source_findings[0] if belief.source_findings else None,
            })
        return results

    def get_contested_beliefs(self) -> List[T3Belief]:
        """Get all contested T3 beliefs (good argumentation targets)."""
        return [b for b in self.beliefs.values() if b.status == BeliefStatus.CONTESTED]

    def get_coverage_gaps(self, min_priority: float = 0.0) -> List[CoverageGap]:
        """Get coverage gaps above a priority threshold."""
        return [g for g in self.gaps if g.priority >= min_priority]

    def summary(self) -> Dict[str, Any]:
        """Summary statistics for the T3 layer."""
        return {
            "total_findings": len(self.findings),
            "total_beliefs": len(self.beliefs),
            "nascent": sum(1 for b in self.beliefs.values() if b.status == BeliefStatus.NASCENT),
            "established": sum(1 for b in self.beliefs.values() if b.status == BeliefStatus.ESTABLISHED),
            "tentative": sum(1 for b in self.beliefs.values() if b.status == BeliefStatus.TENTATIVE),
            "contested": sum(1 for b in self.beliefs.values() if b.status == BeliefStatus.CONTESTED),
            "coverage_gaps": len(self.gaps),
            "granularity_distribution": {
                level.name: sum(1 for b in self.beliefs.values() if b.granularity == level)
                for level in GranularityLevel
            },
        }

    def record_defeat(self, belief_id: str, defeating_finding_id: str,
                       new_status: BeliefStatus, reason: str = "") -> bool:
        """
        Record that new evidence has defeated (or contested) a belief.

        Expert Panel (#2 Epistemologist):
          "When a belief gets contested, track WHICH evidence defeated it."

        Args:
            belief_id: The T3 belief identifier
            defeating_finding_id: ID of the finding that caused the defeat
            new_status: New status for the belief
            reason: Optional human-readable explanation

        Returns:
            True if belief was found and updated
        """
        from datetime import datetime, timezone

        belief = self.beliefs.get(belief_id)
        if not belief:
            return False

        old_status = belief.status

        # Record the defeat
        belief.defeaters.append({
            "finding_id": defeating_finding_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "old_status": old_status.name,
            "new_status": new_status.name,
            "reason": reason,
        })

        # Record status history
        belief.status_history.append({
            "from": old_status.name,
            "to": new_status.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "triggered_by": defeating_finding_id,
        })

        # Update status
        belief.status = new_status

        LOGGER.info(
            "Belief %s: %s → %s (defeated by %s)",
            belief_id, old_status.name, new_status.name, defeating_finding_id,
        )
        return True

    # ══════════════════════════════════════════════════════════════
    # S3: Moderator Analysis for Contested Beliefs
    # ══════════════════════════════════════════════════════════════

    def analyze_moderators(self, belief: T3Belief) -> Dict[str, Any]:
        """
        S3-1: Analyze potential moderators for a contested belief.

        For a contested belief (mixed directions), examines whether
        study-level factors (population, delivery mode, study design)
        correlate with effect direction. This identifies WHY a belief
        is contested.

        Returns dict with moderator analysis results.
        """
        # Get source findings
        source_findings = [f for f in self.findings if f.finding_id in belief.source_findings]
        if len(source_findings) < 4:
            return {"status": "insufficient_data", "n_findings": len(source_findings)}

        analysis = {
            "belief_id": belief.t3_id,
            "n_findings": len(source_findings),
            "n_positive": belief.n_positive,
            "n_negative": belief.n_negative,
            "n_null": belief.n_null,
            "moderators": {},
        }

        # Moderator 1: Delivery Mode
        mode_groups: Dict[str, Dict[str, int]] = {}
        for f in source_findings:
            mode = f.delivery_mode.value if f.delivery_mode.value != "unspecified" else "unspecified"
            if mode not in mode_groups:
                mode_groups[mode] = {"positive": 0, "negative": 0, "null": 0}
            dir_key = f.effect_direction if f.effect_direction in ("positive", "negative", "null") else "null"
            mode_groups[mode][dir_key] += 1
        if len(mode_groups) > 1:
            analysis["moderators"]["delivery_mode"] = mode_groups

        # Moderator 2: Population
        pop_groups: Dict[str, Dict[str, int]] = {}
        for f in source_findings:
            pop = f.population.strip().lower() if f.population else "unspecified"
            # Normalize to broad categories
            if "student" in pop:
                pop_cat = "students"
            elif "worker" in pop or "employee" in pop or "office" in pop:
                pop_cat = "workers"
            elif "patient" in pop or "clinical" in pop:
                pop_cat = "clinical"
            elif "child" in pop or "children" in pop:
                pop_cat = "children"
            elif "elder" in pop or "older" in pop:
                pop_cat = "elderly"
            elif pop == "unspecified":
                pop_cat = "unspecified"
            else:
                pop_cat = "general"
            if pop_cat not in pop_groups:
                pop_groups[pop_cat] = {"positive": 0, "negative": 0, "null": 0}
            dir_key = f.effect_direction if f.effect_direction in ("positive", "negative", "null") else "null"
            pop_groups[pop_cat][dir_key] += 1
        if len(pop_groups) > 1:
            analysis["moderators"]["population"] = pop_groups

        # Moderator 3: Study Design
        design_groups: Dict[str, Dict[str, int]] = {}
        for f in source_findings:
            design = f.study_design.strip().lower() if f.study_design else "unspecified"
            if "rct" in design or "randomized" in design or "experimental" in design:
                design_cat = "experimental"
            elif "quasi" in design:
                design_cat = "quasi_experimental"
            elif "survey" in design or "cross-section" in design:
                design_cat = "observational"
            elif "longitudinal" in design:
                design_cat = "longitudinal"
            else:
                design_cat = "unspecified"
            if design_cat not in design_groups:
                design_groups[design_cat] = {"positive": 0, "negative": 0, "null": 0}
            dir_key = f.effect_direction if f.effect_direction in ("positive", "negative", "null") else "null"
            design_groups[design_cat][dir_key] += 1
        if len(design_groups) > 1:
            analysis["moderators"]["study_design"] = design_groups

        # Compute I² heterogeneity estimate (S3-3)
        effect_sizes = [float(f.effect_size) for f in source_findings
                        if f.effect_size is not None]
        if len(effect_sizes) >= 3:
            mean_es = sum(effect_sizes) / len(effect_sizes)
            q_stat = sum((es - mean_es) ** 2 for es in effect_sizes)
            df = len(effect_sizes) - 1
            i_squared = max(0, (q_stat - df) / q_stat * 100) if q_stat > 0 else 0
            analysis["heterogeneity"] = {
                "I_squared": round(i_squared, 1),
                "Q_statistic": round(q_stat, 3),
                "df": df,
                "interpretation": (
                    "low" if i_squared < 25 else
                    "moderate" if i_squared < 75 else
                    "high"
                ),
            }

        # Determine if a moderator explains the contestation
        best_moderator = None
        best_separation = 0
        for mod_name, groups in analysis["moderators"].items():
            # Check if any group is predominantly one direction
            for group_name, counts in groups.items():
                total = sum(counts.values())
                if total < 2:
                    continue
                majority = max(counts.values())
                separation = majority / total
                if separation > best_separation and separation > 0.7:
                    best_moderator = f"{mod_name}:{group_name}"
                    best_separation = separation

        if best_moderator:
            analysis["likely_moderator"] = best_moderator
            analysis["recommendation"] = f"Split belief by {best_moderator.split(':')[0]}"
        else:
            analysis["likely_moderator"] = None
            analysis["recommendation"] = "No clear moderator found; may be genuine inconsistency"

        return analysis

    def cross_modal_analysis(self) -> Dict[str, Any]:
        """
        S3-2: Analyze cross-modal generalization potential.

        Identifies belief pairs that share IV/DV taxonomy nodes but differ
        in delivery mode (VR vs real vs image). Assesses whether effect
        directions are consistent across modalities.
        """
        # Group findings by (iv_node, dv_node, delivery_mode)
        modal_groups: Dict[Tuple[str, str], Dict[str, List[Finding]]] = {}
        for f in self.findings:
            key = (f.iv_node, f.dv_node)
            mode = f.delivery_mode.value if f.delivery_mode.value != "unspecified" else "unspecified"
            if key not in modal_groups:
                modal_groups[key] = {}
            modal_groups[key].setdefault(mode, []).append(f)

        # Find pairs with multiple modalities
        cross_modal = []
        for (iv, dv), modes in modal_groups.items():
            non_unspecified = {k: v for k, v in modes.items() if k != "unspecified"}
            if len(non_unspecified) >= 2:
                # Compare effect directions across modalities
                mode_directions = {}
                for mode, findings in non_unspecified.items():
                    dirs = [f.effect_direction for f in findings]
                    mode_directions[mode] = {
                        "n": len(dirs),
                        "predominant": max(set(dirs), key=dirs.count) if dirs else "none",
                        "consistency": dirs.count(max(set(dirs), key=dirs.count)) / len(dirs) if dirs else 0,
                    }

                # Check if directions are consistent
                predominant_dirs = [v["predominant"] for v in mode_directions.values()]
                consistent = len(set(predominant_dirs)) == 1

                cross_modal.append({
                    "iv": iv,
                    "dv": dv,
                    "modalities": mode_directions,
                    "consistent": consistent,
                    "can_generalize": consistent and all(v["n"] >= 2 for v in mode_directions.values()),
                })

        return {
            "total_cross_modal_pairs": len(cross_modal),
            "consistent": sum(1 for c in cross_modal if c["consistent"]),
            "generalizable": sum(1 for c in cross_modal if c["can_generalize"]),
            "pairs": cross_modal[:20],  # Top 20
        }

    def assess_publication_bias(self) -> Dict[str, Any]:
        """
        Wave 8f: Detect publication bias using simplified Egger's test.

        Expert Panel (#18 Methodologist):
          "Detect publication bias using Egger's test or trim-and-fill."

        For each established belief with ≥5 findings that have both
        effect_size and sample_size, tests whether precision (1/SE)
        predicts standardized effect (ES/SE). Asymmetry in the
        funnel plot indicates small-study bias (likely positive results
        from small studies disproportionately published).

        Returns dict with per-belief bias assessments.
        """
        results = []
        skipped = 0

        for belief in self.beliefs.values():
            if belief.status not in (BeliefStatus.ESTABLISHED, BeliefStatus.CONTESTED):
                continue

            # Collect findings with both effect_size and sample_size
            valid_findings = []
            for fid in belief.source_findings:
                f = next((f for f in self.findings if f.finding_id == fid), None)
                if f and f.effect_size is not None and f.sample_size and f.sample_size > 0:
                    valid_findings.append(f)

            if len(valid_findings) < 5:
                skipped += 1
                continue

            # Simplified Egger's regression: test whether precision
            # predicts standardized effect
            # SE ≈ 1/√N (simple approximation)
            # precision = √N
            # standardized_effect = ES * √N
            n_vals = [f.sample_size for f in valid_findings]
            es_vals = [f.effect_size for f in valid_findings]

            precisions = [math.sqrt(n) for n in n_vals]  # 1/SE
            std_effects = [es * math.sqrt(n) for es, n in zip(es_vals, n_vals)]  # ES/SE

            # Simple linear regression: std_effect = a + b * precision
            n_k = len(precisions)
            mean_prec = sum(precisions) / n_k
            mean_std = sum(std_effects) / n_k

            ss_prec = sum((p - mean_prec) ** 2 for p in precisions)
            if ss_prec < 1e-10:
                skipped += 1
                continue

            ss_cross = sum(
                (p - mean_prec) * (s - mean_std)
                for p, s in zip(precisions, std_effects)
            )
            slope = ss_cross / ss_prec
            intercept = mean_std - slope * mean_prec

            # SE of intercept
            residuals = [s - (intercept + slope * p) for s, p in zip(std_effects, precisions)]
            sse = sum(r ** 2 for r in residuals)
            mse = sse / max(n_k - 2, 1)
            se_intercept = math.sqrt(mse * (1.0 / n_k + mean_prec ** 2 / ss_prec))

            # Z-test for intercept ≠ 0  (Egger's test)
            z = intercept / se_intercept if se_intercept > 0 else 0.0
            # Approximate two-sided p-value from z using simple formula
            p_value = 2.0 * math.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi)
            p_value = min(p_value, 1.0)

            bias_detected = abs(z) > 1.96  # p < 0.05

            results.append({
                "t3_id": belief.t3_id,
                "n_findings_tested": n_k,
                "egger_intercept": round(intercept, 3),
                "egger_z": round(z, 3),
                "egger_p": round(p_value, 4),
                "bias_detected": bias_detected,
                "direction": "small-study favoring positive" if intercept > 0 else "small-study favoring negative",
                "slope": round(slope, 3),
            })

        n_tested = len(results)
        n_biased = sum(1 for r in results if r["bias_detected"])

        return {
            "beliefs_tested": n_tested,
            "beliefs_skipped": skipped,
            "bias_detected": n_biased,
            "bias_rate": round(n_biased / max(n_tested, 1), 3),
            "assessments": sorted(results, key=lambda r: abs(r["egger_z"]), reverse=True)[:20],
        }

