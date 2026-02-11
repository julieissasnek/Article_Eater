"""
Gap Prediction Service — Sprint INT-2
2026-02-11

Predicts knowledge gaps from argument structure in the epistemic web.

Gap Types (per Panel P-LAYER):
1. Mediation Gap: A→X→Y exists but direct A→Y missing
2. Mechanism Gap: Empirical beliefs but no theoretical explanation
3. Boundary Gap: Narrow scope conditions
4. Direction Gap: Conflicting causal directions
5. Interaction Gap: Independent effects without interaction beliefs
6. Validation Gap: Theoretical beliefs without empirical support

Expert Panel Guidance:
- Haack: Arguments have structure (premises → conclusions)
- Thagard: Gaps appear where local coherence is low
- Cartwright: Track enabling conditions and scope
- Simon: Prioritize by VOI (value of information)
"""

import logging
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any, Set, Tuple
from datetime import datetime, timezone
from enum import Enum
import math

logger = logging.getLogger(__name__)


# =============================================================================
# Data Structures
# =============================================================================

class GapType(Enum):
    """Types of knowledge gaps that can be predicted."""
    MEDIATION = "mediation"        # A→X→Y exists but direct A→Y missing
    MECHANISM = "mechanism"        # Empirical but no theoretical explanation
    BOUNDARY = "boundary"          # Narrow scope conditions
    DIRECTION = "direction"        # Conflicting causal directions
    INTERACTION = "interaction"    # Independent effects, no interaction
    VALIDATION = "validation"      # Theoretical but no empirical support
    UNJUSTIFIED_EDGE = "unjustified_edge"  # BN edge without belief support


class GapPriority(Enum):
    """Priority levels for gaps."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class PredictedGap:
    """
    A predicted knowledge gap.

    Includes:
    - Gap type and description
    - Affected BN edges/beliefs
    - VOI score for prioritization
    - Suggested search queries
    - Human-readable explanation
    """
    gap_id: str
    gap_type: GapType
    description: str
    priority: GapPriority = GapPriority.MEDIUM
    voi_score: float = 0.5  # Value of Information (0-1)

    # What this gap affects
    affected_edge: Optional[str] = None
    affected_beliefs: List[str] = field(default_factory=list)
    implied_by: List[str] = field(default_factory=list)

    # Resolution guidance
    suggested_search: str = ""
    resolution_approach: str = ""

    # Human-readable explanation
    explanation: str = ""

    # Metadata
    confidence: float = 0.7
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            'gap_id': self.gap_id,
            'gap_type': self.gap_type.value,
            'description': self.description,
            'explanation': self.explanation,
            'priority': self.priority.value,
            'voi_score': self.voi_score,
            'affected_edge': self.affected_edge,
            'affected_beliefs': self.affected_beliefs,
            'implied_by': self.implied_by,
            'suggested_search': self.suggested_search,
            'resolution_approach': self.resolution_approach,
            'confidence': self.confidence,
            'generated_at': self.generated_at.isoformat()
        }


@dataclass
class GapReport:
    """
    Complete gap analysis report.
    """
    report_id: str
    generated_at: datetime
    n_gaps: int
    n_high_priority: int
    gaps: List[PredictedGap]
    summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'schema': 'integration.gap_report.v1',
            'report_id': self.report_id,
            'generated_at': self.generated_at.isoformat(),
            'n_gaps': self.n_gaps,
            'n_high_priority': self.n_high_priority,
            'summary': self.summary,
            'gaps': [g.to_dict() for g in self.gaps]
        }


# =============================================================================
# Known Settings and Populations for Boundary Gap Detection
# =============================================================================

KNOWN_SETTINGS = {
    'office', 'healthcare', 'educational', 'residential', 'retail',
    'industrial', 'hospitality', 'outdoor', 'transportation'
}

KNOWN_POPULATIONS = {
    'adults', 'children', 'elderly', 'workers', 'patients', 'students'
}


# =============================================================================
# Gap Predictor Service
# =============================================================================

class GapPredictor:
    """
    Predicts knowledge gaps from the epistemic web structure.

    Uses argument patterns and coverage analysis to identify:
    - Mediation gaps (missing direct relationships)
    - Mechanism gaps (missing explanations)
    - Boundary gaps (limited scope)
    - Direction gaps (causal ambiguity)
    """

    def __init__(self, web=None, edge_justification_service=None):
        """
        Initialize the gap predictor.

        Args:
            web: WebOfBelief instance
            edge_justification_service: EdgeJustificationService for BN integration
        """
        self._web = web
        self._edge_service = edge_justification_service
        self._gap_counter = 0

    @property
    def web(self):
        """Lazy-load web of belief."""
        if self._web is None:
            try:
                from src.services.web_accumulator import get_accumulator
                acc = get_accumulator()
                # get_master_web() returns (WebOfBelief, BridgeRegistry) tuple
                self._web, _ = acc.get_master_web()
            except Exception as e:
                logger.warning(f"Could not load web: {e}")
        return self._web

    @property
    def edge_service(self):
        """Lazy-load edge justification service."""
        if self._edge_service is None:
            try:
                from src.services.edge_justification import get_edge_justification_service
                self._edge_service = get_edge_justification_service()
            except Exception as e:
                logger.warning(f"Could not load edge service: {e}")
        return self._edge_service

    def _next_gap_id(self) -> str:
        """Generate next gap ID."""
        self._gap_counter += 1
        return f"gap_{self._gap_counter:04d}"

    # Panel D0d (Pearl): Compute graph centrality for VOI weighting
    # Panel Review 2026-02-11: Weight connections by epistemic level (Pearl)
    LEVEL_WEIGHTS: Dict[str, float] = {
        'THEORETICAL': 1.5,      # Connections to theory matter most
        'INTERMEDIATE': 1.2,    # Bridging beliefs
        'EMPIRICAL': 1.0,       # Standard weight
        'OBSERVATIONAL': 0.8,   # Direct observations
    }

    def _compute_centrality_cache(self) -> Dict[str, float]:
        """
        Compute centrality scores for all nodes in the belief graph.
        Panel D0d (Pearl): Central nodes have higher VOI for gap resolution.

        Panel Review 2026-02-11 (Pearl): Weight connections by epistemic level
        of connected nodes. Connections to theoretical beliefs contribute more
        than connections to observational ones.
        """
        if self.web is None:
            logger.debug("Empty web in centrality computation")  # Haack: log empty cases
            return {}

        centrality: Dict[str, float] = {}

        # Build adjacency from constraints with level-weighted edges
        adjacency: Dict[str, List[Tuple[str, float]]] = {}  # node -> [(neighbor, weight)]

        # Handle case where web.constraints might not exist or is a mock
        try:
            constraints = self.web.constraints
            if not hasattr(constraints, 'values'):
                constraints = {}
        except (AttributeError, TypeError):
            constraints = {}

        if not constraints:
            logger.debug("No constraints in web for centrality computation")  # Haack

        for constraint in constraints.values():
            source_id = constraint.source_id
            target_id = constraint.target_id

            # Get epistemic level weights for connected beliefs (Pearl)
            source_belief = self.web.beliefs.get(source_id)
            target_belief = self.web.beliefs.get(target_id)

            source_level = str(getattr(source_belief, 'level', 'EMPIRICAL')).upper()
            target_level = str(getattr(target_belief, 'level', 'EMPIRICAL')).upper()

            source_weight = self.LEVEL_WEIGHTS.get(source_level, 1.0)
            target_weight = self.LEVEL_WEIGHTS.get(target_level, 1.0)

            if source_id not in adjacency:
                adjacency[source_id] = []
            if target_id not in adjacency:
                adjacency[target_id] = []

            # Weight edge by the level of the connected node (Pearl)
            adjacency[source_id].append((target_id, target_weight))
            adjacency[target_id].append((source_id, source_weight))

        # Also count beliefs by environment/outcome
        env_counts: Dict[str, int] = {}
        out_counts: Dict[str, int] = {}
        for belief in self.web.beliefs.values():
            if belief.environment_id:
                env_counts[belief.environment_id] = env_counts.get(belief.environment_id, 0) + 1
            if belief.outcome_id:
                out_counts[belief.outcome_id] = out_counts.get(belief.outcome_id, 0) + 1

        # Compute weighted degree centrality for beliefs (Pearl)
        max_weighted_degree = 1.0
        weighted_degrees: Dict[str, float] = {}

        for belief_id, edges in adjacency.items():
            weighted_degree = sum(weight for _, weight in edges)
            weighted_degrees[belief_id] = weighted_degree
            max_weighted_degree = max(max_weighted_degree, weighted_degree)

        for belief_id in self.web.beliefs:
            weighted_degree = weighted_degrees.get(belief_id, 0)
            centrality[belief_id] = weighted_degree / max_weighted_degree if max_weighted_degree > 0 else 0

        # Also compute centrality for environment/outcome IDs
        total_env = sum(env_counts.values()) or 1
        total_out = sum(out_counts.values()) or 1
        for env_id, count in env_counts.items():
            centrality[f"env:{env_id}"] = count / total_env
        for out_id, count in out_counts.items():
            centrality[f"out:{out_id}"] = count / total_out

        return centrality

    def _get_centrality(self, node_id: str) -> float:
        """Get centrality score for a node (cached)."""
        if not hasattr(self, '_centrality_cache'):
            self._centrality_cache = self._compute_centrality_cache()
        return self._centrality_cache.get(node_id, 0.3)  # Default moderate centrality

    def _get_env_out_centrality(self, env_id: Optional[str], out_id: Optional[str]) -> float:
        """Get combined centrality for an env→out relationship."""
        if not hasattr(self, '_centrality_cache'):
            self._centrality_cache = self._compute_centrality_cache()

        env_cent = self._centrality_cache.get(f"env:{env_id}", 0.3) if env_id else 0.3
        out_cent = self._centrality_cache.get(f"out:{out_id}", 0.3) if out_id else 0.3

        # Combined centrality (average)
        return (env_cent + out_cent) / 2

    # =========================================================================
    # Main Entry Points
    # =========================================================================

    def find_all_gaps(self, max_gaps: int = 50) -> GapReport:
        """
        Find all types of gaps.

        Returns:
            GapReport with all identified gaps
        """
        all_gaps: List[PredictedGap] = []

        # Collect gaps from each detector
        all_gaps.extend(self.find_mediation_gaps())
        all_gaps.extend(self.find_mechanism_gaps())
        all_gaps.extend(self.find_boundary_gaps())
        all_gaps.extend(self.find_direction_gaps())
        all_gaps.extend(self.find_validation_gaps())
        all_gaps.extend(self.find_unjustified_edge_gaps())

        # Sort by VOI score and limit
        all_gaps.sort(key=lambda g: -g.voi_score)
        all_gaps = all_gaps[:max_gaps]

        # Compute summary
        n_high = sum(1 for g in all_gaps if g.priority == GapPriority.HIGH)
        gap_type_counts = {}
        for g in all_gaps:
            gap_type_counts[g.gap_type.value] = gap_type_counts.get(g.gap_type.value, 0) + 1

        return GapReport(
            report_id=f"gap_report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            generated_at=datetime.now(timezone.utc),
            n_gaps=len(all_gaps),
            n_high_priority=n_high,
            gaps=all_gaps,
            summary={
                'gap_type_counts': gap_type_counts,
                'avg_voi': sum(g.voi_score for g in all_gaps) / len(all_gaps) if all_gaps else 0
            }
        )

    # =========================================================================
    # Mediation Gap Detection
    # =========================================================================

    def find_mediation_gaps(self) -> List[PredictedGap]:
        """
        Find mediation gaps: A→X→Y exists but direct A→Y missing.

        If A affects X, and X affects Y, does A affect Y directly?

        Decision D2-2: Check 2-hop paths only (A→X→Y)
        """
        gaps = []

        if self.web is None:
            return gaps

        # Build a simple adjacency from beliefs
        # A belief with environment_id E and outcome_id O implies E→O
        edges: Dict[str, Set[str]] = {}  # source → set of targets

        for belief in self.web.beliefs.values():
            if belief.environment_id and belief.outcome_id:
                if belief.environment_id not in edges:
                    edges[belief.environment_id] = set()
                edges[belief.environment_id].add(belief.outcome_id)

        # Find 2-hop paths
        for a, a_targets in edges.items():
            for x in a_targets:
                # Check if X has outgoing edges (X→Y)
                if x in edges:
                    for y in edges[x]:
                        # Check if direct A→Y exists
                        if y not in a_targets:
                            # Mediation gap found
                            voi = self._compute_mediation_voi(a, x, y)
                            a_name = a.split('.')[-1]
                            x_name = x.split('.')[-1]
                            y_name = y.split('.')[-1]

                            # Human-readable explanation
                            explanation = (
                                f"We know that '{a_name}' affects '{x_name}', and '{x_name}' affects '{y_name}'. "
                                f"This suggests '{a_name}' might also directly influence '{y_name}', but we have no "
                                f"evidence for this direct relationship. This is important because: (1) the effect "
                                f"might be fully mediated through {x_name} with no direct path, or (2) there may be "
                                f"an independent direct effect we're missing. Understanding whether the effect is "
                                f"direct, mediated, or both helps design better interventions. "
                                f"To resolve: search for studies that test {a_name}'s effect on {y_name} while "
                                f"controlling for {x_name}."
                            )

                            gaps.append(PredictedGap(
                                gap_id=self._next_gap_id(),
                                gap_type=GapType.MEDIATION,
                                description=f"Path {a}→{x}→{y} exists, but direct {a}→{y} is missing",
                                explanation=explanation,
                                priority=GapPriority.HIGH if voi > 0.7 else GapPriority.MEDIUM,
                                voi_score=voi,
                                implied_by=[f"{a}→{x}", f"{x}→{y}"],
                                suggested_search=f"{a.split('.')[-1]} {y.split('.')[-1]} direct effect",
                                resolution_approach="Search for studies that directly test the A→Y relationship"
                            ))

        return gaps

    def _compute_mediation_voi(self, a: str, x: str, y: str) -> float:
        """
        Compute VOI for a mediation gap.
        Panel D0d (Pearl): Incorporate graph centrality into VOI.
        """
        # Base VOI
        base_voi = 0.5

        # Panel D0d: Weight by centrality of the outcome Y
        # Gaps affecting central nodes are more valuable to resolve
        y_centrality = self._get_env_out_centrality(None, y)
        a_centrality = self._get_env_out_centrality(a, None)

        # Combined VOI: base + centrality bonus
        voi = base_voi + 0.3 * y_centrality + 0.2 * a_centrality

        # Simon: Cap VOI at 0.95 - no gap has perfect certainty of resolution value
        return min(voi, 0.95)

    # =========================================================================
    # Mechanism Gap Detection
    # =========================================================================

    def find_mechanism_gaps(self) -> List[PredictedGap]:
        """
        Find mechanism gaps: Empirical beliefs but no theoretical explanation.

        Decision D2-1: VOI = coverage × uncertainty (simple heuristic)
        """
        gaps = []

        if self.web is None:
            return gaps

        # Group beliefs by (environment_id, outcome_id) pairs
        pairs: Dict[Tuple[str, str], List[Any]] = {}

        for belief in self.web.beliefs.values():
            if belief.environment_id and belief.outcome_id:
                key = (belief.environment_id, belief.outcome_id)
                if key not in pairs:
                    pairs[key] = []
                pairs[key].append(belief)

        # Check each pair for mechanism gaps
        for (env_id, out_id), beliefs in pairs.items():
            empirical = [b for b in beliefs if hasattr(b, 'level') and
                        str(b.level).upper() in ['EMPIRICAL', 'OBSERVATIONAL']]
            theoretical = [b for b in beliefs if hasattr(b, 'level') and
                          str(b.level).upper() == 'THEORETICAL']

            if empirical and not theoretical:
                voi = self._compute_mechanism_voi(empirical)
                env_name = env_id.split('.')[-1]
                out_name = out_id.split('.')[-1]

                # Human-readable explanation
                explanation = (
                    f"We have {len(empirical)} empirical finding(s) showing that '{env_name}' affects "
                    f"'{out_name}', but we lack a theoretical explanation of WHY or HOW this happens. "
                    f"Empirical findings tell us THAT something works; theory tells us WHY. Without "
                    f"understanding the mechanism, we cannot predict when the effect will hold, design "
                    f"effective interventions, or know if the finding will generalize. For example, if "
                    f"plants reduce stress, is it because of visual complexity, air quality, biophilic "
                    f"association, or color? Each mechanism suggests different design implications. "
                    f"To resolve: look for theoretical frameworks (e.g., ART, SRT, Biophilia) that explain "
                    f"this relationship."
                )

                gaps.append(PredictedGap(
                    gap_id=self._next_gap_id(),
                    gap_type=GapType.MECHANISM,
                    description=f"The {env_name}→{out_name} relationship has empirical support but no mechanistic explanation",
                    explanation=explanation,
                    priority=GapPriority.MEDIUM,
                    voi_score=voi,
                    affected_beliefs=[b.belief_id for b in empirical],
                    suggested_search=f"{env_name} {out_name} mechanism pathway",
                    resolution_approach="Search for theoretical papers explaining the mechanism"
                ))

        return gaps

    def _compute_mechanism_voi(self, empirical_beliefs: List[Any]) -> float:
        """
        Compute VOI for mechanism gap.
        Panel D0d (Pearl): Incorporate graph centrality into VOI.
        """
        # Base VOI: Higher if more empirical beliefs (well-established relationship)
        n_beliefs = len(empirical_beliefs)
        base_voi = min(0.4 + 0.1 * n_beliefs, 0.7)

        # Panel D0d: Add centrality bonus
        # Average centrality of affected beliefs
        if empirical_beliefs and self.web:
            centralities = [
                self._get_centrality(b.belief_id)
                for b in empirical_beliefs
            ]
            avg_centrality = sum(centralities) / len(centralities)
            voi = base_voi + 0.3 * avg_centrality
        else:
            voi = base_voi

        return min(voi, 0.95)

    # =========================================================================
    # Boundary Gap Detection
    # =========================================================================

    def find_boundary_gaps(self) -> List[PredictedGap]:
        """
        Find boundary gaps: Narrow scope conditions.

        Decision D2-3: Compare against known universe of settings/populations
        """
        gaps = []

        if self.web is None:
            return gaps

        # Group beliefs by relationship (env→out)
        pairs: Dict[Tuple[str, str], List[Any]] = {}

        for belief in self.web.beliefs.values():
            if belief.environment_id and belief.outcome_id:
                key = (belief.environment_id, belief.outcome_id)
                if key not in pairs:
                    pairs[key] = []
                pairs[key].append(belief)

        # Check scope coverage for each pair
        for (env_id, out_id), beliefs in pairs.items():
            covered_settings: Set[str] = set()
            covered_populations: Set[str] = set()

            for b in beliefs:
                if hasattr(b, 'scope') and b.scope:
                    # Extract settings from scope
                    if hasattr(b.scope, 'setting'):
                        covered_settings.add(str(b.scope.setting).lower())
                    if hasattr(b.scope, 'population'):
                        covered_populations.add(str(b.scope.population).lower())

                # Also check tags
                for tag in getattr(b, 'tags', []):
                    tag_lower = tag.lower()
                    if any(s in tag_lower for s in KNOWN_SETTINGS):
                        covered_settings.add(tag_lower)
                    if any(p in tag_lower for p in KNOWN_POPULATIONS):
                        covered_populations.add(tag_lower)

            # Find missing settings
            missing_settings = KNOWN_SETTINGS - covered_settings
            missing_populations = KNOWN_POPULATIONS - covered_populations

            if missing_settings and len(covered_settings) > 0:
                env_name = env_id.split('.')[-1]
                out_name = out_id.split('.')[-1]

                # Report first few missing settings
                missing_list = list(missing_settings)[:3]
                voi = self._compute_boundary_voi(len(covered_settings), len(missing_settings))

                # Human-readable explanation
                covered_list = list(covered_settings)[:3]
                explanation = (
                    f"We have evidence that '{env_name}' affects '{out_name}' in some settings "
                    f"(e.g., {', '.join(covered_list)}), but no studies have examined this relationship "
                    f"in {', '.join(missing_list)} settings. This matters because effects found in one "
                    f"context may not generalize to others. For example, the impact of {env_name} on "
                    f"{out_name} might differ between a hospital and an office due to different "
                    f"occupant expectations, activities, and environmental baselines. "
                    f"To close this gap, look for studies conducted specifically in {missing_list[0]} environments."
                )

                gaps.append(PredictedGap(
                    gap_id=self._next_gap_id(),
                    gap_type=GapType.BOUNDARY,
                    description=f"{env_name}→{out_name}: No evidence for settings: {', '.join(missing_list)}",
                    explanation=explanation,
                    priority=GapPriority.LOW if voi < 0.5 else GapPriority.MEDIUM,
                    voi_score=voi,
                    affected_beliefs=[b.belief_id for b in beliefs],
                    suggested_search=f"{env_name} {out_name} {missing_list[0]}",
                    resolution_approach=f"Search for studies in {missing_list[0]} settings"
                ))

        return gaps

    def _compute_boundary_voi(self, n_covered: int, n_missing: int) -> float:
        """Compute VOI for boundary gap."""
        if n_covered == 0:
            return 0.3
        # Higher VOI if many covered but key ones missing
        coverage_ratio = n_covered / (n_covered + n_missing)
        return 0.4 + 0.4 * (1 - coverage_ratio)

    # =========================================================================
    # Direction Gap Detection
    # =========================================================================

    def find_direction_gaps(self) -> List[PredictedGap]:
        """
        Find direction gaps: Conflicting causal directions.

        Some beliefs may suggest A→B while others suggest B→A.
        """
        gaps = []

        if self.web is None:
            return gaps

        # This would require analyzing causal language in belief content
        # For now, check for bidirectional edges (A→B and B→A both exist)

        edges: Set[Tuple[str, str]] = set()

        for belief in self.web.beliefs.values():
            if belief.environment_id and belief.outcome_id:
                edges.add((belief.environment_id, belief.outcome_id))

        # Find bidirectional pairs
        for (a, b) in edges:
            if (b, a) in edges and a < b:  # a < b to avoid duplicates
                a_name = a.split('.')[-1]
                b_name = b.split('.')[-1]

                # Human-readable explanation
                explanation = (
                    f"We have evidence suggesting both that '{a_name}' affects '{b_name}' AND that "
                    f"'{b_name}' affects '{a_name}'. This creates causal ambiguity. The true relationship "
                    f"could be: (1) A causes B (reverse findings are spurious), (2) B causes A (forward "
                    f"findings are spurious), (3) Bidirectional causation (feedback loop), or (4) Common "
                    f"cause (both are effects of an unmeasured third variable). Resolving direction is "
                    f"critical for intervention design—you can only manipulate causes, not effects. "
                    f"To resolve: look for longitudinal studies (temporal precedence), experimental "
                    f"manipulations, or natural experiments that can establish causal direction."
                )

                gaps.append(PredictedGap(
                    gap_id=self._next_gap_id(),
                    gap_type=GapType.DIRECTION,
                    description=f"Causal direction unclear: Both {a_name}→{b_name} and {b_name}→{a_name} have support",
                    explanation=explanation,
                    priority=GapPriority.HIGH,
                    voi_score=0.8,
                    suggested_search=f"{a_name} {b_name} causal direction temporal",
                    resolution_approach="Look for longitudinal or experimental studies that establish direction"
                ))

        return gaps

    # =========================================================================
    # Validation Gap Detection
    # =========================================================================

    def find_validation_gaps(self) -> List[PredictedGap]:
        """
        Find validation gaps: Theoretical beliefs without empirical support.
        """
        gaps = []

        if self.web is None:
            return gaps

        # Group beliefs by relationship
        pairs: Dict[Tuple[str, str], List[Any]] = {}

        for belief in self.web.beliefs.values():
            if belief.environment_id and belief.outcome_id:
                key = (belief.environment_id, belief.outcome_id)
                if key not in pairs:
                    pairs[key] = []
                pairs[key].append(belief)

        # Check for theoretical-only relationships
        for (env_id, out_id), beliefs in pairs.items():
            theoretical = [b for b in beliefs if hasattr(b, 'level') and
                          str(b.level).upper() == 'THEORETICAL']
            empirical = [b for b in beliefs if hasattr(b, 'level') and
                        str(b.level).upper() in ['EMPIRICAL', 'OBSERVATIONAL']]

            if theoretical and not empirical:
                env_name = env_id.split('.')[-1]
                out_name = out_id.split('.')[-1]

                # Get theory names if available
                theory_names = []
                for b in theoretical:
                    if hasattr(b, 'theory_id') and b.theory_id:
                        theory_names.append(b.theory_id.split('.')[-1])

                theory_str = ', '.join(set(theory_names)) if theory_names else "theoretical frameworks"

                # Human-readable explanation
                explanation = (
                    f"According to {theory_str}, '{env_name}' should affect '{out_name}'. However, "
                    f"we have no empirical studies that have actually tested this prediction. "
                    f"Theories without empirical validation remain speculative—they may be correct, but "
                    f"we cannot have confidence in applying them to design decisions. This gap represents "
                    f"a testable hypothesis: the theory makes a prediction that hasn't been verified. "
                    f"To resolve: search for controlled experiments, field studies, or systematic "
                    f"observations that measure whether {env_name} actually affects {out_name} as predicted."
                )

                gaps.append(PredictedGap(
                    gap_id=self._next_gap_id(),
                    gap_type=GapType.VALIDATION,
                    description=f"Theory predicts {env_name}→{out_name}, but no empirical validation found",
                    explanation=explanation,
                    priority=GapPriority.MEDIUM,
                    voi_score=0.65,
                    affected_beliefs=[b.belief_id for b in theoretical],
                    suggested_search=f"{env_name} {out_name} empirical study experiment",
                    resolution_approach="Search for experimental or observational studies testing this prediction"
                ))

        return gaps

    # =========================================================================
    # Unjustified Edge Gap Detection
    # =========================================================================

    def find_unjustified_edge_gaps(self) -> List[PredictedGap]:
        """
        Find BN edges that lack epistemic justification.

        Uses EdgeJustificationService to identify edges without belief support.
        """
        gaps = []

        if self.edge_service is None:
            return gaps

        try:
            justifications = self.edge_service.get_all_justifications()

            for j in justifications:
                if j.justification_status.value == 'unjustified':
                    # Human-readable explanation
                    explanation = (
                        f"The Bayesian Network assumes that '{j.source_node}' causally influences "
                        f"'{j.target_node}', but we have found no scientific evidence supporting this "
                        f"relationship. This is a HIGH priority gap because any predictions involving "
                        f"this edge are currently based on assumption rather than evidence. "
                        f"To resolve this gap, search for peer-reviewed studies that examine how "
                        f"{j.source_node} affects {j.target_node} in built environments."
                    )

                    gaps.append(PredictedGap(
                        gap_id=self._next_gap_id(),
                        gap_type=GapType.UNJUSTIFIED_EDGE,
                        description=f"BN edge {j.source_node}→{j.target_node} has no supporting beliefs",
                        explanation=explanation,
                        priority=GapPriority.HIGH,
                        voi_score=0.85,
                        affected_edge=j.edge_id,
                        suggested_search=f"{j.source_node} {j.target_node} effect relationship",
                        resolution_approach="Search for papers that investigate this relationship"
                    ))
        except Exception as e:
            logger.warning(f"Error checking unjustified edges: {e}")

        return gaps


# =============================================================================
# Convenience Functions
# =============================================================================

_predictor_instance: Optional[GapPredictor] = None


def get_gap_predictor() -> GapPredictor:
    """Get or create the gap predictor singleton."""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = GapPredictor()
    return _predictor_instance


def find_all_gaps(max_gaps: int = 50) -> GapReport:
    """Convenience function to find all gaps."""
    predictor = get_gap_predictor()
    return predictor.find_all_gaps(max_gaps)
