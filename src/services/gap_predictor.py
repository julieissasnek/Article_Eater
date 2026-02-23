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
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Set, Tuple
from datetime import datetime, timezone

# Import canonical gap types from single source of truth
# Per Canonical Decisions Record (02-15_09), Decision 1
from src.epistemic.gap_types import GapType, GapPriority

logger = logging.getLogger(__name__)


# =============================================================================
# Data Structures
# =============================================================================


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

    def _normalized_level(self, belief: Any) -> str:
        """Return a normalized epistemic level label for robust comparisons."""
        level = getattr(belief, 'level', None)
        if level is None:
            return ""

        # Enum-backed beliefs should compare by `.value` (e.g., "empirical"),
        # not `str(enum)` (e.g., "EpistemicLevel.EMPIRICAL").
        if hasattr(level, 'value'):
            return str(level.value).upper()
        return str(level).upper()

    # =========================================================================
    # GR-2: Local Corpus Check (Gap Resolution Improvement 2026-02-12)
    # =========================================================================

    def find_local_evidence_for_gap(self, gap: PredictedGap) -> Dict[str, List[Dict]]:
        """
        Before suggesting external search, check local corpus for evidence.

        Checks:
        1. Extracted findings in data/extracted_findings/
        2. Existing beliefs that match via keywords but not canonical IDs
        3. Unprocessed abstracts in data/abstracts/

        Args:
            gap: The PredictedGap to find evidence for

        Returns:
            Dict with keys: 'extracted_findings', 'keyword_matched_beliefs', 'unprocessed'
        """
        from pathlib import Path
        import json

        result = {
            'extracted_findings': [],
            'keyword_matched_beliefs': [],
            'unprocessed_abstracts': []
        }

        # Get keywords from gap description and affected edge
        keywords = self._extract_gap_keywords(gap)
        logger.info(f"Searching local corpus for gap {gap.gap_id} with keywords: {keywords}")

        # 1. Check extracted findings
        findings_dir = Path("data/extracted_findings")
        if findings_dir.exists():
            for jsonl_file in findings_dir.glob("*.jsonl"):
                try:
                    with open(jsonl_file, 'r') as f:
                        for line in f:
                            finding = json.loads(line.strip())
                            content = finding.get('content', '') + ' ' + finding.get('finding', '')
                            if self._content_matches_keywords(content, keywords):
                                result['extracted_findings'].append({
                                    'source_file': str(jsonl_file.name),
                                    'finding': finding
                                })
                except Exception as e:
                    logger.warning(f"Error reading {jsonl_file}: {e}")

        # 2. Check existing beliefs via keyword matching
        if self.web and self.web.beliefs:
            for belief in self.web.beliefs.values():
                if self._content_matches_keywords(belief.content, keywords):
                    # Check if this belief is NOT already linked to the gap's edge
                    edge_id = gap.affected_edge
                    is_already_supporting = False

                    if edge_id and hasattr(belief, 'environment_id') and hasattr(belief, 'outcome_id'):
                        # Simple check - if belief already supports this edge, skip
                        edge_parts = edge_id.split('_')
                        if len(edge_parts) >= 2:
                            env_part = edge_parts[0]
                            out_part = edge_parts[-1]
                            if (belief.environment_id and env_part in belief.environment_id.lower()) or \
                               (belief.outcome_id and out_part in belief.outcome_id.lower()):
                                is_already_supporting = True

                    if not is_already_supporting:
                        result['keyword_matched_beliefs'].append({
                            'belief_id': belief.belief_id,
                            'content': belief.content[:200] + '...' if len(belief.content) > 200 else belief.content,
                            'environment_id': getattr(belief, 'environment_id', None),
                            'outcome_id': getattr(belief, 'outcome_id', None),
                            'note': 'May need canonical ID update to match edge'
                        })

        # 3. Check unprocessed abstracts
        abstracts_dir = Path("data/abstracts")
        if abstracts_dir.exists():
            for json_file in abstracts_dir.glob("*.json"):
                try:
                    with open(json_file, 'r') as f:
                        abstract_data = json.load(f)
                        abstract_text = abstract_data.get('abstract', '')
                        if self._content_matches_keywords(abstract_text, keywords):
                            result['unprocessed_abstracts'].append({
                                'source_file': str(json_file.name),
                                'doi': abstract_data.get('doi'),
                                'title': abstract_data.get('title'),
                                'preview': abstract_text[:300] + '...' if len(abstract_text) > 300 else abstract_text
                            })
                except Exception as e:
                    logger.warning(f"Error reading {json_file}: {e}")

        total_found = (len(result['extracted_findings']) +
                      len(result['keyword_matched_beliefs']) +
                      len(result['unprocessed_abstracts']))
        logger.info(f"Found {total_found} potential local evidence items for gap {gap.gap_id}")

        return result

    def _extract_gap_keywords(self, gap: PredictedGap) -> List[str]:
        """Extract search keywords from a gap."""
        keywords = []

        # From affected edge
        if gap.affected_edge:
            parts = gap.affected_edge.replace('_', ' ').split()
            keywords.extend(parts)

        # From description
        desc_words = gap.description.lower().split()
        for word in desc_words:
            if len(word) > 4 and word not in ['that', 'this', 'with', 'from', 'have', 'been']:
                keywords.append(word)

        # From suggested search
        if gap.suggested_search:
            keywords.extend(gap.suggested_search.split()[:5])

        return list(set(keywords))[:10]  # Dedupe and limit

    def _content_matches_keywords(self, content: str, keywords: List[str], min_matches: int = 2) -> bool:
        """Check if content contains enough keywords."""
        if not content:
            return False
        content_lower = content.lower()
        matches = sum(1 for kw in keywords if kw.lower() in content_lower)
        return matches >= min_matches

    # =========================================================================
    # Mayo Panel Fix: Defeater Search (2026-02-12)
    # Panel: "Confirmation bias is structural. You search for 'supporting beliefs'
    # for edges. This is confirmation seeking. A proper system would search for
    # potential DEFEATERS."
    # =========================================================================

    # Keywords that suggest contradictory evidence or failed replication
    DEFEATER_INDICATORS = {
        'no_effect': ['no effect', 'no significant', 'not significant', 'failed to find',
                      'did not find', 'null result', 'no relationship', 'no correlation',
                      'no association', 'null hypothesis', 'failed to replicate'],
        'contrary': ['contrary to', 'in contrast to', 'however', 'conversely',
                     'opposing', 'contradicts', 'inconsistent with', 'challenges'],
        'limitation': ['limitation', 'confound', 'bias', 'artifact', 'methodological',
                       'small sample', 'underpowered', 'publication bias'],
        'replication': ['failed replication', 'replication failure', 'did not replicate',
                        'could not replicate', 'replication crisis'],
        'boundary': ['only under', 'only when', 'limited to', 'does not generalize',
                     'boundary condition', 'moderator', 'interaction effect']
    }

    def find_defeaters_for_belief(self, belief_id: str) -> Dict[str, Any]:
        """
        Search for potential defeaters (disconfirming evidence) for a belief.

        Panel Review 2026-02-12 (Mayo): Addresses confirmation bias by actively
        searching for evidence AGAINST beliefs rather than only seeking support.

        Types of defeaters sought:
        1. Null results: Studies that found no effect
        2. Contrary findings: Studies with opposite conclusions
        3. Methodological critiques: Questions about the evidence base
        4. Replication failures: Studies that failed to replicate the finding
        5. Boundary conditions: Limitations on generalizability

        Args:
            belief_id: ID of the belief to find defeaters for

        Returns:
            Dict containing:
            - belief_summary: The belief being examined
            - potential_defeaters: List of potential contradicting evidence
            - defeater_categories: Breakdown by type
            - confidence_adjustment: Suggested credence adjustment if defeaters found
            - recommendation: What to do with findings
        """
        from pathlib import Path
        import json

        result = {
            'belief_id': belief_id,
            'belief_summary': None,
            'potential_defeaters': [],
            'defeater_categories': {
                'null_results': [],
                'contrary_findings': [],
                'methodological_critiques': [],
                'replication_failures': [],
                'boundary_conditions': []
            },
            'confidence_adjustment': 0.0,
            'recommendation': ''
        }

        # Get the belief
        if not self.web or belief_id not in self.web.beliefs:
            logger.warning(f"Belief {belief_id} not found in web")
            result['recommendation'] = 'Belief not found - cannot search for defeaters'
            return result

        belief = self.web.beliefs[belief_id]
        result['belief_summary'] = {
            'content': belief.content[:300] + '...' if len(belief.content) > 300 else belief.content,
            'credence': belief.credence.value if hasattr(belief.credence, 'value') else belief.credence,
            'environment_id': getattr(belief, 'environment_id', None),
            'outcome_id': getattr(belief, 'outcome_id', None)
        }

        # Extract core concepts from the belief for targeted defeater search
        search_concepts = self._extract_defeater_search_concepts(belief)
        logger.info(f"Searching for defeaters for belief {belief_id}: concepts={search_concepts}")

        # 1. Check existing beliefs for contradictions
        contradicting_beliefs = self._find_contradicting_beliefs(belief, search_concepts)
        for cb in contradicting_beliefs:
            category = self._categorize_defeater(cb['content'])
            result['defeater_categories'][category].append(cb)
            result['potential_defeaters'].append(cb)

        # 2. Check extracted findings for contradictions
        findings_dir = Path("data/extracted_findings")
        if findings_dir.exists():
            for jsonl_file in findings_dir.glob("*.jsonl"):
                try:
                    with open(jsonl_file, 'r') as f:
                        for line in f:
                            finding = json.loads(line.strip())
                            content = finding.get('content', '') + ' ' + finding.get('finding', '')
                            if self._is_potential_defeater(content, search_concepts):
                                defeater_info = {
                                    'source': 'extracted_finding',
                                    'source_file': str(jsonl_file.name),
                                    'content': content[:300] + '...' if len(content) > 300 else content,
                                    'defeater_type': self._identify_defeater_type(content)
                                }
                                category = self._categorize_defeater(content)
                                result['defeater_categories'][category].append(defeater_info)
                                result['potential_defeaters'].append(defeater_info)
                except Exception as e:
                    logger.warning(f"Error reading {jsonl_file}: {e}")

        # 3. Check unprocessed abstracts
        abstracts_dir = Path("data/abstracts")
        if abstracts_dir.exists():
            for json_file in abstracts_dir.glob("*.json"):
                try:
                    with open(json_file, 'r') as f:
                        abstract_data = json.load(f)
                        abstract_text = abstract_data.get('abstract', '')
                        if self._is_potential_defeater(abstract_text, search_concepts):
                            defeater_info = {
                                'source': 'unprocessed_abstract',
                                'source_file': str(json_file.name),
                                'doi': abstract_data.get('doi'),
                                'title': abstract_data.get('title'),
                                'content': abstract_text[:300] + '...' if len(abstract_text) > 300 else abstract_text,
                                'defeater_type': self._identify_defeater_type(abstract_text)
                            }
                            category = self._categorize_defeater(abstract_text)
                            result['defeater_categories'][category].append(defeater_info)
                            result['potential_defeaters'].append(defeater_info)
                except Exception as e:
                    logger.warning(f"Error reading {json_file}: {e}")

        # Calculate confidence adjustment based on defeaters found
        n_defeaters = len(result['potential_defeaters'])
        if n_defeaters == 0:
            result['confidence_adjustment'] = 0.0
            result['recommendation'] = 'No defeaters found. Consider external search for contrary evidence.'
        elif n_defeaters <= 2:
            result['confidence_adjustment'] = -0.1
            result['recommendation'] = f'Found {n_defeaters} potential defeater(s). Review and consider widening uncertainty.'
        elif n_defeaters <= 5:
            result['confidence_adjustment'] = -0.2
            result['recommendation'] = f'Found {n_defeaters} potential defeaters. Significant uncertainty warranted.'
        else:
            result['confidence_adjustment'] = -0.3
            result['recommendation'] = f'Found {n_defeaters} potential defeaters. This belief is contested - major revision needed.'

        logger.info(f"Defeater search complete for {belief_id}: found {n_defeaters} potential defeaters")
        return result

    def _extract_defeater_search_concepts(self, belief) -> List[str]:
        """Extract key concepts from a belief for defeater search."""
        concepts = []

        # Environment and outcome IDs
        if hasattr(belief, 'environment_id') and belief.environment_id:
            concepts.append(belief.environment_id.split('.')[-1])  # Get leaf concept
        if hasattr(belief, 'outcome_id') and belief.outcome_id:
            concepts.append(belief.outcome_id.split('.')[-1])

        # Key nouns from content (simple extraction)
        content_words = belief.content.lower().split()
        important_words = [w for w in content_words
                          if len(w) > 5 and w not in ['which', 'where', 'these', 'those', 'about']]
        concepts.extend(important_words[:5])

        return list(set(concepts))

    def _find_contradicting_beliefs(self, target_belief, search_concepts: List[str]) -> List[Dict]:
        """Find existing beliefs that might contradict the target."""
        contradictions = []

        if not self.web or not self.web.beliefs:
            return contradictions

        target_env = getattr(target_belief, 'environment_id', None)
        target_out = getattr(target_belief, 'outcome_id', None)

        for belief_id, belief in self.web.beliefs.items():
            if belief_id == target_belief.belief_id:
                continue

            # Check for same env/outcome with different direction or effect
            belief_env = getattr(belief, 'environment_id', None)
            belief_out = getattr(belief, 'outcome_id', None)

            same_domain = False
            if target_env and belief_env and target_out and belief_out:
                if target_env == belief_env and target_out == belief_out:
                    same_domain = True

            # Check for defeater language in content
            if same_domain or self._content_matches_keywords(belief.content, search_concepts, min_matches=2):
                if self._has_defeater_language(belief.content):
                    contradictions.append({
                        'source': 'existing_belief',
                        'belief_id': belief_id,
                        'content': belief.content[:300] + '...' if len(belief.content) > 300 else belief.content,
                        'same_domain': same_domain,
                        'defeater_type': self._identify_defeater_type(belief.content)
                    })

        return contradictions

    def _is_potential_defeater(self, content: str, search_concepts: List[str]) -> bool:
        """Check if content might be a defeater for given concepts."""
        if not content:
            return False

        # Must mention the concepts AND have defeater language
        matches_concepts = self._content_matches_keywords(content, search_concepts, min_matches=1)
        has_defeater = self._has_defeater_language(content)

        return matches_concepts and has_defeater

    def _has_defeater_language(self, content: str) -> bool:
        """Check if content contains language suggesting contradiction/limitation."""
        if not content:
            return False

        content_lower = content.lower()
        for category_indicators in self.DEFEATER_INDICATORS.values():
            for indicator in category_indicators:
                if indicator in content_lower:
                    return True
        return False

    def _identify_defeater_type(self, content: str) -> str:
        """Identify the type of defeater based on content."""
        content_lower = content.lower()

        for category, indicators in self.DEFEATER_INDICATORS.items():
            for indicator in indicators:
                if indicator in content_lower:
                    return category

        return 'general'

    def _categorize_defeater(self, content: str) -> str:
        """Map defeater type to result category."""
        defeater_type = self._identify_defeater_type(content)
        mapping = {
            'no_effect': 'null_results',
            'contrary': 'contrary_findings',
            'limitation': 'methodological_critiques',
            'replication': 'replication_failures',
            'boundary': 'boundary_conditions',
            'general': 'contrary_findings'
        }
        return mapping.get(defeater_type, 'contrary_findings')

    def find_all_defeaters(self, limit: int = 10) -> Dict[str, Any]:
        """
        Find potential defeaters for the most confident beliefs.

        Panel Review 2026-02-12 (Mayo): "For each belief, actively seek
        disconfirming evidence."

        Prioritizes highly-confident beliefs since those are where
        overconfidence is most dangerous.

        Args:
            limit: Maximum number of beliefs to check

        Returns:
            Dict with defeater analysis for top beliefs
        """
        if not self.web or not self.web.beliefs:
            return {'beliefs_checked': 0, 'results': []}

        # Sort beliefs by credence (most confident first)
        sorted_beliefs = sorted(
            self.web.beliefs.values(),
            key=lambda b: b.credence.value if hasattr(b.credence, 'value') else b.credence,
            reverse=True
        )[:limit]

        results = []
        for belief in sorted_beliefs:
            defeater_result = self.find_defeaters_for_belief(belief.belief_id)
            if defeater_result['potential_defeaters']:  # Only include if defeaters found
                results.append(defeater_result)

        return {
            'beliefs_checked': len(sorted_beliefs),
            'beliefs_with_defeaters': len(results),
            'results': results
        }

    # Panel D0d (Pearl): Compute graph centrality for VOI weighting
    # Panel Review 2026-02-12 (Haack): Equal weights - entrenchment emerges from
    # connections, not from type labels. The 1.5/0.8 ratio was crypto-foundationalism.
    # Per foundherentism: ANY belief can be revised; entrenchment is structural.
    LEVEL_WEIGHTS: Dict[str, float] = {
        'THEORETICAL': 1.0,      # Equal weight - no privilege for theory
        'INTERMEDIATE': 1.0,     # Equal weight
        'EMPIRICAL': 1.0,        # Equal weight
        'OBSERVATIONAL': 1.0,    # Equal weight - observations anchor to reality
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
        # Sprint 10: Argument-level gap detection
        all_gaps.extend(self.find_critical_question_gaps())
        all_gaps.extend(self.find_argument_attack_gaps())

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
            empirical = [b for b in beliefs if self._normalized_level(b) in ['EMPIRICAL', 'OBSERVATIONAL']]
            theoretical = [b for b in beliefs if self._normalized_level(b) == 'THEORETICAL']

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
            theoretical = [b for b in beliefs if self._normalized_level(b) == 'THEORETICAL']
            empirical = [b for b in beliefs if self._normalized_level(b) in ['EMPIRICAL', 'OBSERVATIONAL']]

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

    # =========================================================================
    # Sprint 10: Argument-Level Gap Detection (STUB)
    # =========================================================================

    def find_critical_question_gaps(self) -> List[PredictedGap]:
        """
        Find gaps where Walton critical questions are unaddressed.

        Sprint 10: STUB — Not yet implemented.

        This will check ClaimV2.argument_scheme and ClaimV2.critical_questions_addressed
        to identify claims that use an argumentation scheme but haven't addressed
        the scheme's critical questions.

        Example: An "argument from expert opinion" that hasn't addressed:
        - Is the source a credible expert?
        - Is this within their field of expertise?
        - Is there consensus among experts?

        Requires: ClaimV2 fields to be populated by extraction pipeline.
        Currently blocked by: Extraction pipeline not populating these fields.
        """
        # TODO: Implement when ClaimV2 argument fields are populated
        logger.debug("find_critical_question_gaps: STUB - not yet implemented (Sprint 10)")
        return []

    def find_argument_attack_gaps(self) -> List[PredictedGap]:
        """
        Find gaps where known argument attack types apply.

        Sprint 10: STUB — Not yet implemented.

        This will check beliefs against known attack types from argument_attack.py:
        - CONFOUNDER: Unmeasured variable explains relationship
        - BOUNDARY_CONDITION: Effect only holds under specific conditions
        - MEASUREMENT: Measurement validity concerns
        - REVERSE_CAUSATION: Direction might be reversed
        - SELECTION_BIAS: Sample not representative
        - PUBLICATION_BIAS: Only positive results published

        Requires: AttackType patterns to be matched against belief content.
        Currently blocked by: Need contrast class analysis from argument_attack.py
        """
        # TODO: Implement when AttackType matching is available
        logger.debug("find_argument_attack_gaps: STUB - not yet implemented (Sprint 10)")
        return []


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
