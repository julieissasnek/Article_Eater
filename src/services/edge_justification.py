"""
Edge Justification Service — Sprint INT-1
2026-02-11

Links Bayesian Network edges to their epistemic justification from the Web of Belief.

This service bridges the gap between:
- BN_graphical's causal structure (edges between variables)
- Article_Eater's epistemic web (beliefs with credences)

Expert Panel Guidance (P-VIS, P-LAYER):
- Pearl: BN edges should be justified by beliefs, not vice versa
- Haack: Track epistemic level of supporting beliefs
- Simon: Aggregate credence using established methods
"""

import logging
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any, Set, Tuple
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)


# =============================================================================
# Data Structures
# =============================================================================

class JustificationStatus(Enum):
    """Overall justification strength for an edge."""
    STRONG = "strong"          # High credence, multiple sources, no conflicts
    MODERATE = "moderate"      # Moderate credence or limited sources
    WEAK = "weak"              # Low credence or significant conflicts
    UNJUSTIFIED = "unjustified"  # No supporting beliefs found
    CONTESTED = "contested"    # Significant conflicts exist


class ConflictType(Enum):
    """Type of conflict between a belief and a BN edge."""
    CONTRADICTS = "contradicts"      # Belief directly contradicts the edge
    WEAKENS = "weakens"              # Belief suggests weaker relationship
    BOUNDARY_VIOLATION = "boundary_violation"  # Edge exceeds belief's scope
    DIRECTION_CONFLICT = "direction_conflict"  # Belief suggests opposite direction


@dataclass
class BeliefSummary:
    """Summary of a belief that supports or conflicts with a BN edge."""
    belief_id: str
    credence: float
    uncertainty: float
    content_summary: str
    paper_id: Optional[str] = None
    paper_citation: Optional[str] = None
    epistemic_level: Optional[str] = None
    theory_tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ConflictSummary:
    """Summary of a belief that conflicts with a BN edge."""
    belief_id: str
    credence: float
    conflict_type: ConflictType
    content_summary: str
    conflict_detail: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d['conflict_type'] = self.conflict_type.value
        return d


@dataclass
class ProvenanceSummary:
    """Summary of source provenance for edge justification."""
    n_papers: int = 0
    primary_papers: List[str] = field(default_factory=list)
    date_range: Optional[Dict[str, int]] = None
    study_types: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EdgeJustification:
    """
    Complete justification for a BN edge from the epistemic web.

    This is the primary output of the EdgeJustificationService.
    """
    edge_id: str
    source_node: str
    target_node: str
    aggregate_credence: float
    aggregate_uncertainty: float = 0.0
    justification_status: JustificationStatus = JustificationStatus.UNJUSTIFIED
    supporting_beliefs: List[BeliefSummary] = field(default_factory=list)
    conflicting_beliefs: List[ConflictSummary] = field(default_factory=list)
    net_support: float = 0.0
    key_theories: List[str] = field(default_factory=list)
    causal_direction_confidence: float = 0.5
    provenance: Optional[ProvenanceSummary] = None
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            'schema': 'integration.edge_justification.v1',
            'edge_id': self.edge_id,
            'source_node': self.source_node,
            'target_node': self.target_node,
            'aggregate_credence': self.aggregate_credence,
            'aggregate_uncertainty': self.aggregate_uncertainty,
            'justification_status': self.justification_status.value,
            'supporting_beliefs': [b.to_dict() for b in self.supporting_beliefs],
            'conflicting_beliefs': [c.to_dict() for c in self.conflicting_beliefs],
            'net_support': self.net_support,
            'key_theories': self.key_theories,
            'causal_direction_confidence': self.causal_direction_confidence,
            'provenance': self.provenance.to_dict() if self.provenance else None,
            'generated_at': self.generated_at.isoformat()
        }


# =============================================================================
# Variable Matching
# =============================================================================

# Decision D1-1: Use taxonomy-based matching
# BN variable names map to environment/outcome taxonomy IDs

# Common BN variables and their taxonomy mappings
# This can be extended via configuration
BN_VARIABLE_MAPPINGS: Dict[str, Dict[str, List[str]]] = {
    # Attributes (Layer 1 in BN)
    'daylight': {'environment_ids': ['sensory.light.natural', 'natural.daylight'], 'keywords': ['daylight', 'natural light', 'sunlight']},
    'plants': {'environment_ids': ['natural.vegetation', 'natural.plants'], 'keywords': ['plants', 'vegetation', 'greenery', 'biophilia']},
    'wood_coverage': {'environment_ids': ['natural.wood', 'spatial.materials.wood'], 'keywords': ['wood', 'timber', 'natural materials']},
    'noise': {'environment_ids': ['sensory.noise', 'sensory.sound'], 'keywords': ['noise', 'sound', 'acoustic']},
    'temperature': {'environment_ids': ['sensory.thermal', 'config.temperature'], 'keywords': ['temperature', 'thermal', 'heat', 'cold']},
    'crowding': {'environment_ids': ['spatial.density', 'spatial.crowding'], 'keywords': ['crowding', 'density', 'personal space']},
    'ceiling_height': {'environment_ids': ['spatial.ceiling', 'spatial.height'], 'keywords': ['ceiling height', 'volume', 'spaciousness']},
    'nature_view': {'environment_ids': ['natural.view', 'natural.window_view'], 'keywords': ['nature view', 'window view', 'outdoor view']},

    # Mediators (Layer 2 in BN)
    'warmth': {'outcome_ids': ['psych.warmth', 'affect.warmth'], 'keywords': ['warmth', 'cozy', 'comfortable']},
    'cognitive_load': {'outcome_ids': ['cog.load', 'cog.cognitive_load'], 'keywords': ['cognitive load', 'mental effort', 'complexity']},
    'restorativeness': {'outcome_ids': ['psych.restoration', 'affect.restoration'], 'keywords': ['restorative', 'restoration', 'recovery']},

    # Outcomes (Layer 3 in BN)
    'stress': {'outcome_ids': ['psych.stress', 'affect.stress'], 'keywords': ['stress', 'anxiety', 'tension', 'cortisol']},
    'focus': {'outcome_ids': ['cog.attention', 'cog.focus', 'cog.concentration'], 'keywords': ['focus', 'attention', 'concentration']},
    'satisfaction': {'outcome_ids': ['psych.satisfaction', 'affect.satisfaction'], 'keywords': ['satisfaction', 'contentment', 'happiness']},
    'productivity': {'outcome_ids': ['perf.productivity', 'cog.performance'], 'keywords': ['productivity', 'performance', 'output']},
    'mood': {'outcome_ids': ['affect.mood', 'psych.mood'], 'keywords': ['mood', 'affect', 'emotional state']},
    'creativity': {'outcome_ids': ['cog.creativity', 'perf.creativity'], 'keywords': ['creativity', 'creative', 'innovation']},
}


def get_variable_matching_criteria(bn_variable: str) -> Tuple[List[str], List[str], List[str]]:
    """
    Get matching criteria for a BN variable.

    Returns:
        Tuple of (environment_ids, outcome_ids, keywords) to search for.
    """
    mapping = BN_VARIABLE_MAPPINGS.get(bn_variable.lower(), {})
    env_ids = mapping.get('environment_ids', [])
    outcome_ids = mapping.get('outcome_ids', [])
    keywords = mapping.get('keywords', [bn_variable.lower()])
    return env_ids, outcome_ids, keywords


# =============================================================================
# Edge Justification Service
# =============================================================================

class EdgeJustificationService:
    """
    Service to compute epistemic justification for BN edges.

    Given a BN edge (source → target), this service:
    1. Finds beliefs in the web that relate source to target
    2. Aggregates their credences
    3. Identifies conflicts
    4. Returns an EdgeJustification object
    """

    def __init__(self, web=None, accumulator=None):
        """
        Initialize the service.

        Args:
            web: WebOfBelief instance (if None, will try to get from accumulator)
            accumulator: WebAccumulator instance (if None, will try to create)
        """
        self._web = web
        self._accumulator = accumulator
        self._belief_cache: Dict[str, Any] = {}

    @property
    def web(self):
        """Lazy-load the web of belief."""
        if self._web is None:
            if self._accumulator is not None:
                self._web = self._accumulator.web
            else:
                # Try to import and get the global web
                try:
                    from src.services.web_accumulator import get_accumulator
                    self._accumulator = get_accumulator()
                    self._web = self._accumulator.web
                except Exception as e:
                    logger.warning(f"Could not load web: {e}")
                    return None
        return self._web

    def get_justification(
        self,
        source_var: str,
        target_var: str,
        edge_id: Optional[str] = None
    ) -> EdgeJustification:
        """
        Get epistemic justification for a BN edge.

        Args:
            source_var: BN source variable name (e.g., 'daylight')
            target_var: BN target variable name (e.g., 'stress')
            edge_id: Optional explicit edge ID (default: source_target)

        Returns:
            EdgeJustification object with aggregated evidence
        """
        if edge_id is None:
            edge_id = f"{source_var}_{target_var}"

        logger.info(f"Getting justification for edge: {edge_id}")

        # Find supporting beliefs
        supporting = self._find_supporting_beliefs(source_var, target_var)
        logger.debug(f"Found {len(supporting)} supporting beliefs")

        # Find conflicting beliefs
        conflicting = self._find_conflicting_beliefs(source_var, target_var, supporting)
        logger.debug(f"Found {len(conflicting)} conflicting beliefs")

        # Aggregate credence
        # Decision D1-2: Using inverse-variance weighted average
        agg_credence, agg_uncertainty = self._aggregate_credence(supporting)

        # Compute net support
        net_support = self._compute_net_support(supporting, conflicting)

        # Determine justification status
        status = self._determine_status(supporting, conflicting, agg_credence)

        # Extract theories
        theories = self._extract_theories(supporting)

        # Compute causal direction confidence
        direction_conf = self._compute_direction_confidence(supporting)

        # Build provenance summary
        provenance = self._build_provenance(supporting)

        return EdgeJustification(
            edge_id=edge_id,
            source_node=source_var,
            target_node=target_var,
            aggregate_credence=agg_credence,
            aggregate_uncertainty=agg_uncertainty,
            justification_status=status,
            supporting_beliefs=[self._to_belief_summary(b) for b in supporting],
            conflicting_beliefs=conflicting,
            net_support=net_support,
            key_theories=theories,
            causal_direction_confidence=direction_conf,
            provenance=provenance
        )

    def get_all_justifications(
        self,
        bn_edges: Optional[List[Tuple[str, str]]] = None
    ) -> List[EdgeJustification]:
        """
        Get justifications for all BN edges.

        Args:
            bn_edges: List of (source, target) tuples. If None, uses default BN structure.

        Returns:
            List of EdgeJustification objects
        """
        if bn_edges is None:
            # Default BN edges (from BN_graphical structure)
            bn_edges = [
                # Attributes → Mediators
                ('daylight', 'warmth'),
                ('daylight', 'restorativeness'),
                ('plants', 'restorativeness'),
                ('wood_coverage', 'warmth'),
                ('noise', 'cognitive_load'),
                # Mediators → Outcomes
                ('warmth', 'satisfaction'),
                ('cognitive_load', 'stress'),
                ('cognitive_load', 'focus'),
                ('restorativeness', 'stress'),
                ('restorativeness', 'mood'),
                # Direct Attribute → Outcome edges
                ('daylight', 'stress'),
                ('daylight', 'mood'),
                ('daylight', 'productivity'),
                ('plants', 'stress'),
                ('plants', 'mood'),
                ('noise', 'stress'),
                ('noise', 'focus'),
                ('temperature', 'productivity'),
                ('crowding', 'stress'),
            ]

        justifications = []
        for source, target in bn_edges:
            try:
                j = self.get_justification(source, target)
                justifications.append(j)
            except Exception as e:
                logger.error(f"Error getting justification for {source}→{target}: {e}")

        return justifications

    def get_unjustified_edges(
        self,
        bn_edges: List[Tuple[str, str]]
    ) -> List[str]:
        """
        Find BN edges that lack epistemic justification.

        Returns:
            List of edge IDs with no supporting beliefs
        """
        unjustified = []
        for source, target in bn_edges:
            j = self.get_justification(source, target)
            if j.justification_status == JustificationStatus.UNJUSTIFIED:
                unjustified.append(j.edge_id)
        return unjustified

    # =========================================================================
    # Private Methods
    # =========================================================================

    def _find_supporting_beliefs(self, source_var: str, target_var: str) -> List[Any]:
        """Find beliefs that support the relationship source → target."""
        if self.web is None:
            return []

        supporting = []

        # Get matching criteria for both variables
        src_env_ids, src_out_ids, src_keywords = get_variable_matching_criteria(source_var)
        tgt_env_ids, tgt_out_ids, tgt_keywords = get_variable_matching_criteria(target_var)

        # Search all beliefs
        for belief in self.web.beliefs.values():
            # Check if belief relates source to target
            if self._belief_matches_edge(belief, src_env_ids, src_keywords, tgt_out_ids, tgt_keywords):
                supporting.append(belief)

        return supporting

    def _belief_matches_edge(
        self,
        belief: Any,
        src_env_ids: List[str],
        src_keywords: List[str],
        tgt_out_ids: List[str],
        tgt_keywords: List[str]
    ) -> bool:
        """
        Check if a belief matches a source → target edge.

        A belief matches if:
        1. Its environment_id matches a source ID AND outcome_id matches a target ID
        2. OR its content mentions both source and target keywords
        """
        # Method 1: Canonical ID matching
        env_match = belief.environment_id in src_env_ids if belief.environment_id else False
        out_match = belief.outcome_id in tgt_out_ids if belief.outcome_id else False

        if env_match and out_match:
            return True

        # Method 2: Keyword matching in content
        content_lower = belief.content.lower()
        src_found = any(kw in content_lower for kw in src_keywords)
        tgt_found = any(kw in content_lower for kw in tgt_keywords)

        if src_found and tgt_found:
            return True

        return False

    def _find_conflicting_beliefs(
        self,
        source_var: str,
        target_var: str,
        supporting: List[Any]
    ) -> List[ConflictSummary]:
        """Find beliefs that conflict with the edge."""
        if self.web is None:
            return []

        conflicts = []
        supporting_ids = {b.belief_id for b in supporting}

        # Check constraints for negative relationships
        for belief in supporting:
            # Look for constraints with negative weight
            constraints = self.web._constraint_index.get(belief.belief_id, [])
            for constraint in constraints:
                other_id = constraint.target_id if constraint.source_id == belief.belief_id else constraint.source_id
                if other_id in supporting_ids:
                    continue  # Already in supporting

                # Decision D1-3: Conflict threshold is -0.3
                if constraint.weight < -0.3:
                    other = self.web.beliefs.get(other_id)
                    if other:
                        conflicts.append(ConflictSummary(
                            belief_id=other_id,
                            credence=other.credence.value,
                            conflict_type=ConflictType.WEAKENS,
                            content_summary=other.content[:200],
                            conflict_detail=f"Negative constraint weight: {constraint.weight:.2f}"
                        ))

        return conflicts

    def _aggregate_credence(self, beliefs: List[Any]) -> Tuple[float, float]:
        """
        Aggregate credences from multiple beliefs.

        Decision D1-2: Using inverse-variance weighted average (DerSimonian-Laird style)
        """
        if not beliefs:
            return 0.0, 1.0

        # Simple inverse-variance weighting
        weights = []
        credences = []

        for b in beliefs:
            cred = b.credence.value if hasattr(b.credence, 'value') else b.credence
            unc = b.credence.uncertainty if hasattr(b.credence, 'uncertainty') else 0.3

            # Weight is inverse of variance (uncertainty squared)
            variance = max(unc ** 2, 0.01)  # Minimum variance to avoid division by zero
            weight = 1.0 / variance

            weights.append(weight)
            credences.append(cred)

        total_weight = sum(weights)
        if total_weight == 0:
            return sum(credences) / len(credences), 0.5

        # Weighted average
        agg_credence = sum(w * c for w, c in zip(weights, credences)) / total_weight

        # Pooled uncertainty (inverse of sum of weights)
        agg_uncertainty = (1.0 / total_weight) ** 0.5

        return agg_credence, min(agg_uncertainty, 1.0)

    def _compute_net_support(
        self,
        supporting: List[Any],
        conflicting: List[ConflictSummary]
    ) -> float:
        """Compute net support score."""
        support_sum = sum(
            b.credence.value if hasattr(b.credence, 'value') else b.credence
            for b in supporting
        )
        conflict_sum = sum(c.credence for c in conflicting)

        return support_sum - conflict_sum

    def _determine_status(
        self,
        supporting: List[Any],
        conflicting: List[ConflictSummary],
        agg_credence: float
    ) -> JustificationStatus:
        """Determine the justification status."""
        if not supporting:
            return JustificationStatus.UNJUSTIFIED

        if len(conflicting) > len(supporting) * 0.5:
            return JustificationStatus.CONTESTED

        if agg_credence >= 0.7 and len(supporting) >= 2:
            return JustificationStatus.STRONG

        if agg_credence >= 0.5:
            return JustificationStatus.MODERATE

        return JustificationStatus.WEAK

    def _extract_theories(self, beliefs: List[Any]) -> List[str]:
        """Extract unique theories from supporting beliefs."""
        theories: Set[str] = set()
        for b in beliefs:
            if b.theory_id:
                theories.add(b.theory_id)
            for tag in b.tags:
                if tag.startswith('theory:'):
                    theories.add(tag.replace('theory:', ''))
        return sorted(theories)

    def _compute_direction_confidence(self, beliefs: List[Any]) -> float:
        """
        Compute confidence in causal direction.

        Checks for beliefs that explicitly mention direction or use causal language.
        """
        if not beliefs:
            return 0.5

        # Look for causal indicators in belief content
        forward_indicators = ['causes', 'leads to', 'results in', 'increases', 'decreases', 'reduces']
        reverse_indicators = ['caused by', 'due to', 'because of', 'resulting from']

        forward_count = 0
        reverse_count = 0

        for b in beliefs:
            content_lower = b.content.lower()
            if any(ind in content_lower for ind in forward_indicators):
                forward_count += 1
            if any(ind in content_lower for ind in reverse_indicators):
                reverse_count += 1

        total = forward_count + reverse_count
        if total == 0:
            return 0.5

        return forward_count / total

    def _build_provenance(self, beliefs: List[Any]) -> ProvenanceSummary:
        """Build provenance summary from supporting beliefs."""
        papers: Set[str] = set()
        for b in beliefs:
            papers.update(b.paper_ids)

        return ProvenanceSummary(
            n_papers=len(papers),
            primary_papers=sorted(papers)[:5],
            date_range=None,  # Would need paper metadata
            study_types=[]
        )

    def _to_belief_summary(self, belief: Any) -> BeliefSummary:
        """Convert a Belief to a BeliefSummary."""
        cred = belief.credence.value if hasattr(belief.credence, 'value') else belief.credence
        unc = belief.credence.uncertainty if hasattr(belief.credence, 'uncertainty') else 0.3

        return BeliefSummary(
            belief_id=belief.belief_id,
            credence=cred,
            uncertainty=unc,
            content_summary=belief.content[:200],
            paper_id=belief.paper_ids[0] if belief.paper_ids else None,
            paper_citation=None,  # Would need paper metadata
            epistemic_level=belief.level.value if hasattr(belief.level, 'value') else str(belief.level),
            theory_tags=[belief.theory_id] if belief.theory_id else []
        )


# =============================================================================
# Convenience Functions
# =============================================================================

_service_instance: Optional[EdgeJustificationService] = None


def get_edge_justification_service() -> EdgeJustificationService:
    """Get or create the edge justification service singleton."""
    global _service_instance
    if _service_instance is None:
        _service_instance = EdgeJustificationService()
    return _service_instance


def get_justification(source_var: str, target_var: str) -> EdgeJustification:
    """Convenience function to get justification for an edge."""
    service = get_edge_justification_service()
    return service.get_justification(source_var, target_var)
