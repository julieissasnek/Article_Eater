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

# Sentinel value to distinguish "not set" from "explicitly None"
_UNSET = object()


class GapPredictor:
    """
    Predicts knowledge gaps from the epistemic web structure.

    Uses argument patterns and coverage analysis to identify:
    - Mediation gaps (missing direct relationships)
    - Mechanism gaps (missing explanations)
    - Boundary gaps (limited scope)
    - Direction gaps (causal ambiguity)
    """

    def __init__(self, web=None, edge_justification_service=None, voi_scorer=_UNSET):
        """
        Initialize the gap predictor.

        Args:
            web: WebOfBelief instance
            edge_justification_service: EdgeJustificationService for BN integration
            voi_scorer: Optional VOICalculator for computing real VOI scores.
                        If not provided, will lazy-load.
                        If None, explicitly disables VOI scoring.
        """
        self._web = web
        self._edge_service = edge_justification_service
        self._voi_scorer = voi_scorer if voi_scorer is not _UNSET else _UNSET
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

    @property
    def voi_scorer(self):
        """Lazy-load VOI calculator for real VOI computation.

        If voi_scorer was explicitly passed to __init__ (including None),
        use that value. Otherwise, try to lazy-load VOICalculator.
        """
        if self._voi_scorer is _UNSET:
            try:
                from src.services.voi_search import VOICalculator
                self._voi_scorer = VOICalculator()
            except ImportError:
                logger.debug("VOICalculator not available; gaps will use default VOI scores")
                self._voi_scorer = None
            except Exception as e:
                logger.warning(f"Could not load VOI scorer: {e}")
                self._voi_scorer = None
        return self._voi_scorer if self._voi_scorer is not _UNSET else None

    def _next_gap_id(self) -> str:
        """Generate next gap ID."""
        self._gap_counter += 1
        return f"gap_{self._gap_counter:04d}"

    def _compute_gap_voi(self, gap_type: GapType, affected_belief_id: Optional[str] = None) -> float:
        """
        Compute VOI score for a gap using real VOI scorer if available.

        Falls back to 0.5 if VOI scorer is unavailable or fails.

        Args:
            gap_type: Type of gap (MEDIATION, MECHANISM, etc.)
            affected_belief_id: Optional belief ID for context

        Returns:
            VOI score between 0.0 and 1.0
        """
        scorer = self.voi_scorer
        if scorer is None:
            return 0.5

        try:
            # Try to find the affected belief in the web
            belief = None
            if affected_belief_id and self.web and self.web.beliefs:
                belief = self.web.beliefs.get(affected_belief_id)

            if belief is None and self.web and self.web.beliefs:
                # Fallback: use first available belief
                beliefs_list = list(self.web.beliefs.values())
                if beliefs_list:
                    belief = beliefs_list[0]

            if belief is not None:
                combined_voi, _, _ = scorer.calculate_voi(gap_type, belief, self.web)
                return float(combined_voi)
            else:
                return 0.5
        except Exception as e:
            logger.warning(f"VOI computation failed for gap type {gap_type}: {e}; using fallback 0.5")
            return 0.5

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
        # NOTE: Corpus uses *.json not *.jsonl (fixed 2026-03-03, P1 #9)
        findings_dir = Path("data/extractions")
        if findings_dir.exists():
            # Search .json first (actual corpus format), then .jsonl for compat
            extraction_files = list(findings_dir.glob("*.json")) or list(findings_dir.glob("*.jsonl"))
            for ext_file in extraction_files:
                try:
                    with open(ext_file, 'r') as f:
                        data = json.load(f)
                        # Extraction JSONs have a 'findings' array
                        findings_list = data.get('findings', [])
                        if not findings_list and isinstance(data, dict):
                            findings_list = [data]  # Single finding
                        for finding in findings_list:
                            content = finding.get('finding_text', '') + ' ' + finding.get('content', '')
                            if not content.strip():
                                # Try alternate field names
                                content = finding.get('antecedent', '') + ' ' + finding.get('consequent', '')
                            if self._content_matches_keywords(content, keywords):
                                result['extracted_findings'].append({
                                    'source_file': str(ext_file.name),
                                    'finding': finding
                                })
                except Exception as e:
                    logger.warning(f"Error reading {ext_file}: {e}")

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
        # NOTE: Corpus uses *.json not *.jsonl (fixed 2026-03-03, P1 #9)
        findings_dir = Path("data/extractions")
        if findings_dir.exists():
            extraction_files = list(findings_dir.glob("*.json")) or list(findings_dir.glob("*.jsonl"))
            for ext_file in extraction_files:
                try:
                    with open(ext_file, 'r') as f:
                        data = json.load(f)
                        findings_list = data.get('findings', [])
                        if not findings_list and isinstance(data, dict):
                            findings_list = [data]
                        for finding in findings_list:
                            content = finding.get('content', '') + ' ' + finding.get('finding', '')
                            if not content.strip():
                                content = finding.get('antecedent', '') + ' ' + finding.get('consequent', '')
                            if self._is_potential_defeater(content, search_concepts):
                                defeater_info = {
                                    'source': 'extracted_finding',
                                    'source_file': str(ext_file.name),
                                    'content': content[:300] + '...' if len(content) > 300 else content,
                                    'defeater_type': self._identify_defeater_type(content)
                                }
                                category = self._categorize_defeater(content)
                                result['defeater_categories'][category].append(defeater_info)
                                result['potential_defeaters'].append(defeater_info)
                except Exception as e:
                    logger.warning(f"Error reading {ext_file}: {e}")

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
    # Annotation Harvest (AG 2026-03-01, QA Spec Fix 3)
    # Wires OPEN_QUESTION + SEARCH_PROMPT annotations → PredictedGap
    # =========================================================================

    def harvest_annotation_gaps(self) -> List[PredictedGap]:
        """Harvest OPEN_QUESTION and SEARCH_PROMPT annotations as gaps.

        User-created annotations often encode the most valuable gap signals —
        questions a human researcher noticed but the system hasn't addressed.
        This method converts those annotations into PredictedGap objects that
        integrate with the rest of the gap prediction pipeline.

        Returns:
            List of PredictedGaps generated from active annotations
        """
        gaps: List[PredictedGap] = []

        try:
            from src.services.annotation_service import AnnotationService, AnnotationType
        except ImportError:
            logger.debug("AnnotationService not available for annotation harvest")
            return gaps

        try:
            ann_svc = AnnotationService()

            # Harvest OPEN_QUESTION annotations
            open_questions = ann_svc.get_annotations_by_type(
                AnnotationType.OPEN_QUESTION, status="active"
            )
            for ann in open_questions:
                gap = PredictedGap(
                    gap_id=self._next_gap_id(),
                    gap_type=GapType.VALIDATION,  # Most open questions need validation
                    description=f"User-identified question: {ann.content[:200]}",
                    priority=GapPriority.HIGH,  # User questions are high priority
                    voi_score=0.85,  # High VOI — human-identified gaps are valuable
                    affected_beliefs=[ann.target_id] if ann.target_type == "belief" else [],
                    affected_edge=ann.target_id if ann.target_type == "causal_link" else None,
                    suggested_search=ann.content[:100],
                    resolution_approach="Address user-identified knowledge gap",
                    explanation=(
                        f"Annotation {ann.id[:8]} by {ann.author}: "
                        f"Open question on {ann.target_type} '{ann.target_id}'"
                    ),
                    confidence=ann.confidence,
                )
                gaps.append(gap)

            # Harvest SEARCH_PROMPT annotations
            search_prompts = ann_svc.get_annotations_by_type(
                AnnotationType.SEARCH_PROMPT, status="active"
            )
            for ann in search_prompts:
                gap = PredictedGap(
                    gap_id=self._next_gap_id(),
                    gap_type=GapType.MECHANISM,  # Search prompts often target mechanism
                    description=f"User search suggestion: {ann.content[:200]}",
                    priority=GapPriority.MEDIUM,
                    voi_score=0.75,
                    affected_beliefs=[ann.target_id] if ann.target_type == "belief" else [],
                    affected_edge=ann.target_id if ann.target_type == "causal_link" else None,
                    suggested_search=ann.content,
                    resolution_approach="Execute user-suggested search",
                    explanation=(
                        f"Annotation {ann.id[:8]} by {ann.author}: "
                        f"Search prompt on {ann.target_type} '{ann.target_id}'"
                    ),
                    confidence=ann.confidence,
                )
                gaps.append(gap)

            if gaps:
                logger.info(
                    "Harvested %d gaps from annotations (%d open questions, %d search prompts)",
                    len(gaps), len(open_questions), len(search_prompts),
                )

        except Exception as e:
            logger.warning(f"Annotation harvest failed (non-fatal): {e}")

        return gaps

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
        # QA Spec Fix 3: Harvest user annotations as gaps (AG 2026-03-01)
        all_gaps.extend(self.harvest_annotation_gaps())

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

    def predict_gaps(self, topic: str = "", max_gaps: int = 5) -> List[Dict]:
        """
        Bridge method for AnswerEnrichmentOrchestrator Step 5.

        Wraps find_all_gaps() and returns a simplified list of dicts
        with 'type', 'description', and 'severity' keys.

        Args:
            topic: The topic context (used for logging; gap detection
                   operates on the full belief web structure)
            max_gaps: Maximum number of gaps to return

        Returns:
            List of dicts with keys: type, description, severity
        """
        logger.info(f"predict_gaps called for topic='{topic[:50]}', max_gaps={max_gaps}")
        try:
            report = self.find_all_gaps(max_gaps=max_gaps)
            return [
                {
                    "type": g.gap_type.value if hasattr(g.gap_type, 'value') else str(g.gap_type),
                    "description": g.description,
                    "severity": g.priority.value if hasattr(g.priority, 'value') else str(g.priority),
                    "voi": g.voi_score,
                    "explanation": g.explanation,
                }
                for g in report.gaps
            ]
        except Exception as e:
            logger.warning(f"predict_gaps failed: {e}")
            return []

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

        If VOI scorer is available, uses real VOI computation.
        Falls back to heuristic computation if unavailable.
        """
        scorer = self.voi_scorer
        if scorer is not None:
            try:
                # Use real VOI scorer with the outcome belief
                if self.web and self.web.beliefs:
                    # Try to find outcome belief
                    for belief in self.web.beliefs.values():
                        if hasattr(belief, 'outcome_id') and belief.outcome_id == y:
                            combined_voi, _, _ = scorer.calculate_voi(GapType.MEDIATION, belief, self.web)
                            return float(combined_voi)
                    # If not found, use first belief
                    beliefs_list = list(self.web.beliefs.values())
                    if beliefs_list:
                        combined_voi, _, _ = scorer.calculate_voi(GapType.MEDIATION, beliefs_list[0], self.web)
                        return float(combined_voi)
            except Exception as e:
                logger.debug(f"Real VOI computation failed for mediation gap: {e}; falling back to heuristic")

        # Heuristic fallback (original logic)
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

        If VOI scorer is available, uses real VOI computation.
        Falls back to heuristic computation if unavailable.
        """
        scorer = self.voi_scorer
        if scorer is not None and empirical_beliefs:
            try:
                # Use real VOI scorer with average of affected beliefs
                voi_scores = []
                for belief_obj in empirical_beliefs:
                    # Get actual belief from web
                    belief = belief_obj if hasattr(belief_obj, 'belief_id') else belief_obj
                    belief_id = getattr(belief, 'belief_id', None) or str(belief)
                    if self.web and self.web.beliefs and belief_id in self.web.beliefs:
                        web_belief = self.web.beliefs[belief_id]
                        combined_voi, _, _ = scorer.calculate_voi(GapType.MECHANISM, web_belief, self.web)
                        voi_scores.append(float(combined_voi))
                if voi_scores:
                    return float(sum(voi_scores) / len(voi_scores))
            except Exception as e:
                logger.debug(f"Real VOI computation failed for mechanism gap: {e}; falling back to heuristic")

        # Heuristic fallback (original logic)
        # Base VOI: Higher if more empirical beliefs (well-established relationship)
        n_beliefs = len(empirical_beliefs)
        base_voi = min(0.4 + 0.1 * n_beliefs, 0.7)

        # Panel D0d: Add centrality bonus
        # Average centrality of affected beliefs
        if empirical_beliefs and self.web:
            centralities = [
                self._get_centrality(b.belief_id if hasattr(b, 'belief_id') else str(b))
                for b in empirical_beliefs
            ]
            avg_centrality = sum(centralities) / len(centralities) if centralities else 0
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
        """
        Compute VOI for boundary gap.

        If VOI scorer is available, uses real VOI computation.
        Falls back to heuristic computation if unavailable.
        """
        scorer = self.voi_scorer
        if scorer is not None:
            try:
                # Use real VOI scorer with a sample belief
                if self.web and self.web.beliefs:
                    beliefs_list = list(self.web.beliefs.values())
                    if beliefs_list:
                        combined_voi, _, _ = scorer.calculate_voi(GapType.BOUNDARY, beliefs_list[0], self.web)
                        return float(combined_voi)
            except Exception as e:
                logger.debug(f"Real VOI computation failed for boundary gap: {e}; falling back to heuristic")

        # Heuristic fallback (original logic)
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
        gaps = []

        if self.web is None:
            return gaps

        # Walton's critical questions by argument scheme
        WALTON_CRITICAL_QUESTIONS = {
            "argument_from_expert_opinion": [
                "is_credible_expert",
                "within_field_of_expertise",
                "expert_consensus",
                "consistent_with_evidence"
            ],
            "argument_from_analogy": [
                "relevant_similarities",
                "relevant_differences",
                "other_analogies"
            ],
            "argument_from_sign": [
                "other_explanations",
                "sign_reliability",
                "contradictory_signs"
            ],
            "argument_from_cause": [
                "correlation_vs_causation",
                "other_causes",
                "reversed_causation"
            ],
            "argument_from_popular_opinion": [
                "evidence_independent",
                "sample_representative",
                "alternative_explanation"
            ]
        }

        try:
            for belief in self.web.beliefs.values():
                # Check if belief has argument_scheme attribute
                argument_scheme = getattr(belief, 'argument_scheme', None)
                if not argument_scheme:
                    continue

                # Get the critical questions addressed (should be list/set)
                critical_questions_addressed = getattr(belief, 'critical_questions_addressed', set())
                if isinstance(critical_questions_addressed, str):
                    critical_questions_addressed = {critical_questions_addressed}
                elif not isinstance(critical_questions_addressed, (set, list)):
                    critical_questions_addressed = set()
                else:
                    critical_questions_addressed = set(critical_questions_addressed)

                # Look up required critical questions for this scheme
                scheme_key = argument_scheme.lower().replace(' ', '_')
                required_questions = WALTON_CRITICAL_QUESTIONS.get(scheme_key, [])

                if not required_questions:
                    continue

                # Find unaddressed questions
                unaddressed = [q for q in required_questions if q not in critical_questions_addressed]

                if unaddressed:
                    # Determine priority based on scheme type
                    if "expert" in scheme_key:
                        priority = GapPriority.HIGH
                    else:
                        priority = GapPriority.MEDIUM

                    description = (
                        f"Belief uses '{argument_scheme}' scheme but {len(unaddressed)} "
                        f"critical question(s) unaddressed: {', '.join(unaddressed)}"
                    )

                    explanation = (
                        f"This belief makes a claim using an '{argument_scheme}' argument, but hasn't "
                        f"addressed all of Walton's critical questions for this scheme. "
                        f"Unaddressed questions: {', '.join(unaddressed)}. "
                        f"Each critical question represents a potential vulnerability to counterargument. "
                        f"Addressing these questions strengthens the argument by demonstrating awareness "
                        f"of common objections and providing supporting evidence."
                    )

                    gaps.append(PredictedGap(
                        gap_id=self._next_gap_id(),
                        gap_type=GapType.VALIDATION,
                        description=description,
                        explanation=explanation,
                        priority=priority,
                        voi_score=0.6,
                        affected_beliefs=[belief.belief_id] if hasattr(belief, 'belief_id') else [],
                        suggested_search=f"{argument_scheme} {' '.join(unaddressed[:2])}",
                        resolution_approach=f"Address critical questions: {', '.join(unaddressed)}"
                    ))

        except Exception as e:
            logger.warning(f"Error in find_critical_question_gaps: {e}")

        logger.info(f"find_critical_question_gaps: Found {len(gaps)} gaps")
        return gaps

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
        gaps = []

        if self.web is None:
            return gaps

        try:
            from src.services.argument_attack import AttackType, ShiftClassifier, ContrastShiftType

            for belief in self.web.beliefs.values():
                # Get belief content/description for text analysis
                belief_text = getattr(belief, 'claim', '') or getattr(belief, 'description', '') or ""
                if not belief_text:
                    continue

                # Detect patterns suggesting vulnerability to specific attacks
                belief_text_lower = belief_text.lower()

                # 1. Check for BOUNDARY_CONDITION vulnerability
                # Beliefs with empirical level but no explicit boundary conditions
                level = self._normalized_level(belief)
                has_boundary_conditions = getattr(belief, 'scope_conditions', None) or getattr(belief, 'boundary_conditions', None)

                if level in ['EMPIRICAL', 'OBSERVATIONAL'] and not has_boundary_conditions:
                    # Text-based classification to confirm attack type
                    shift_type, attack_type, dimensions = ShiftClassifier.classify_from_text(
                        "Effect may only hold under specific conditions",
                        belief_text,
                        ""
                    )

                    if attack_type == AttackType.BOUNDARY_CONDITION or "condition" in belief_text_lower:
                        gaps.append(PredictedGap(
                            gap_id=self._next_gap_id(),
                            gap_type=GapType.BOUNDARY,
                            description=f"Empirical belief lacks explicit boundary conditions; may not generalize",
                            explanation=(
                                f"This empirical belief claims a relationship but doesn't specify the conditions "
                                f"under which it holds. Boundary condition attacks argue: 'This effect only occurs "
                                f"under specific conditions (e.g., certain populations, settings, or baseline states).' "
                                f"Without explicit boundary conditions, the belief is vulnerable to counterexamples "
                                f"from different contexts."
                            ),
                            priority=GapPriority.MEDIUM,
                            voi_score=0.55,
                            affected_beliefs=[belief.belief_id] if hasattr(belief, 'belief_id') else [],
                            suggested_search="boundary conditions scope limitations when only holds",
                            resolution_approach="Identify and document the specific conditions under which this effect holds"
                        ))

                # 2. Check for REPLICATION vulnerability
                # High credence beliefs without replication mention
                credence = getattr(belief, 'credence', None)
                credence_value = 0.5
                if credence:
                    if hasattr(credence, 'point_estimate'):
                        credence_value = credence.point_estimate
                    elif isinstance(credence, (int, float)):
                        credence_value = credence

                has_replication_mention = any(word in belief_text_lower for word in ['replicate', 'replication', 'reproduce', 'confirmation'])

                if credence_value > 0.7 and not has_replication_mention:
                    gaps.append(PredictedGap(
                        gap_id=self._next_gap_id(),
                        gap_type=GapType.VALIDATION,
                        description=f"High-credence belief lacks replication evidence",
                        explanation=(
                            f"This belief has high credence (>{credence_value:.1%}) but no mention of replication. "
                            f"Many findings fail to replicate, especially in social/behavioral sciences. "
                            f"A replication attack argues: 'Others cannot reproduce this finding under similar conditions.' "
                            f"Without independent replication, credence should be tempered."
                        ),
                        priority=GapPriority.MEDIUM,
                        voi_score=0.65,
                        affected_beliefs=[belief.belief_id] if hasattr(belief, 'belief_id') else [],
                        suggested_search="replication study reproduce confirm findings",
                        resolution_approach="Search for independent replication studies confirming this finding"
                    ))

                # 3. Check for MECHANISM vulnerability
                # Causal claims without mechanism explanation
                if "cause" in belief_text_lower or "effect" in belief_text_lower:
                    has_mechanism = any(word in belief_text_lower for word in ['mechanism', 'pathway', 'process', 'mediate', 'mediating'])

                    if not has_mechanism:
                        gaps.append(PredictedGap(
                            gap_id=self._next_gap_id(),
                            gap_type=GapType.MECHANISM,
                            description=f"Causal claim lacks proposed mechanism",
                            explanation=(
                                f"This belief makes a causal claim but doesn't explain the mechanism (HOW or WHY). "
                                f"A mechanism attack argues: 'The proposed causal pathway is implausible or unknown.' "
                                f"Without a credible mechanism, the causal claim is vulnerable to challenge."
                            ),
                            priority=GapPriority.HIGH,
                            voi_score=0.7,
                            affected_beliefs=[belief.belief_id] if hasattr(belief, 'belief_id') else [],
                            suggested_search="mechanism pathway how why explains",
                            resolution_approach="Propose or identify the causal mechanism explaining this relationship"
                        ))

                # 4. Check for CONFOUNDER vulnerability
                # Claims about relationships without discussion of confounders
                if "relationship" in belief_text_lower or "association" in belief_text_lower:
                    has_confounder_discussion = any(word in belief_text_lower for word in ['confounder', 'confound', 'control', 'alternative', 'unmeasured', 'third'])

                    if not has_confounder_discussion:
                        gaps.append(PredictedGap(
                            gap_id=self._next_gap_id(),
                            gap_type=GapType.DIRECTION,
                            description=f"Relationship claim lacks confounder analysis",
                            explanation=(
                                f"This belief claims a relationship but doesn't discuss potential confounders. "
                                f"A confounder attack argues: 'The observed relationship is actually due to an "
                                f"unmeasured third variable, not the claimed cause.' Without confounder analysis, "
                                f"the relationship claim is vulnerable."
                            ),
                            priority=GapPriority.MEDIUM,
                            voi_score=0.6,
                            affected_beliefs=[belief.belief_id] if hasattr(belief, 'belief_id') else [],
                            suggested_search="confounder confounding variable control for",
                            resolution_approach="Identify and rule out potential confounding variables"
                        ))

        except ImportError:
            logger.warning("argument_attack module not available, skipping attack gap detection")
        except Exception as e:
            logger.warning(f"Error in find_argument_attack_gaps: {e}")

        logger.info(f"find_argument_attack_gaps: Found {len(gaps)} gaps")
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
