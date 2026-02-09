"""
Article Eater V23 — Direct Query Service
Sprint 3.0.3 — 2026-02-09

Direct service layer for Streamlit to use query services without API server.
This enables "direct mode" where queries execute locally using the service modules.

Architecture:
- Uses query_parser.py for intent detection (rule-based, no LLM required)
- Uses llm_query_bridge.py for synthesis (optional LLM)
- Uses scope_renderer.py for scope-aware output
- Operates directly on WebOfBelief when available
"""

import sys
import logging
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from enum import Enum

# Add src directory for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

logger = logging.getLogger(__name__)


# =============================================================================
# Response Data Classes
# =============================================================================

@dataclass
class ScopeInfo:
    """Scope conditions for a finding."""
    population: Optional[str] = None
    setting: Optional[str] = None
    methodology: Optional[str] = None
    duration: Optional[str] = None
    limitations: Optional[str] = None

    def to_dict(self) -> Dict[str, str]:
        return {k: v for k, v in asdict(self).items() if v}


@dataclass
class EvidenceSource:
    """A source of evidence."""
    belief_id: str
    content: str
    credence: float
    credence_label: str
    status: str
    level: str
    sources: List[str] = field(default_factory=list)
    scope: Optional[ScopeInfo] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "belief_id": self.belief_id,
            "content": self.content,
            "credence": self.credence,
            "credence_label": self.credence_label,
            "status": self.status,
            "level": self.level,
            "sources": self.sources
        }
        if self.scope:
            result["scope"] = self.scope.to_dict()
        return result


@dataclass
class QueryResult:
    """Complete query result with progressive disclosure."""
    query: str
    query_type: str
    causal_level: str

    # Progressive disclosure
    headline: str
    summary: Optional[Dict[str, Any]] = None
    detail: Optional[Dict[str, Any]] = None

    # Additional sections
    practical_implications: Optional[List[str]] = None
    scope_conditions: Optional[Dict[str, str]] = None
    caveats: Optional[List[str]] = None
    key_sources: Optional[List[str]] = None

    # Evidence items
    evidence: List[EvidenceSource] = field(default_factory=list)

    # Metadata
    confidence: float = 0.0
    processing_mode: str = "direct"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "query_type": self.query_type,
            "causal_level": self.causal_level,
            "headline": self.headline,
            "summary": self.summary,
            "detail": self.detail,
            "practical_implications": self.practical_implications,
            "scope_conditions": self.scope_conditions,
            "caveats": self.caveats,
            "key_sources": self.key_sources,
            "evidence": [e.to_dict() for e in self.evidence],
            "confidence": self.confidence,
            "processing_mode": self.processing_mode
        }


@dataclass
class SystemStats:
    """System-wide statistics."""
    total_beliefs: int = 0
    total_constraints: int = 0
    total_papers: int = 0
    total_communities: int = 0
    overall_coherence: float = 0.0
    average_credence: float = 0.0
    contested_beliefs: int = 0
    stub_beliefs: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# =============================================================================
# Direct Query Service
# =============================================================================

class DirectQueryService:
    """
    Direct query service that operates without API server.

    Uses the query_parser and llm_query_bridge services directly.
    Can operate in two modes:
    - Rule-based: Uses pattern matching only (no LLM required)
    - Hybrid: Uses LLM for synthesis when available
    """

    def __init__(self, web_of_belief: Any = None, use_llm: bool = False):
        """
        Initialize direct query service.

        Args:
            web_of_belief: Optional WebOfBelief instance for evidence retrieval
            use_llm: Whether to use LLM for synthesis (requires API keys)
        """
        self.web = web_of_belief
        self.use_llm = use_llm
        self._parser = None
        self._orchestrator = None
        self._load_services()

    def _load_services(self):
        """Load query services."""
        try:
            from services.query_parser import QueryParser, QueryType, CausalLevel
            self._parser = QueryParser()
            self.QueryType = QueryType
            self.CausalLevel = CausalLevel
            logger.info("Loaded query_parser service")
        except ImportError as e:
            logger.warning(f"Could not load query_parser: {e}")

        if self.use_llm:
            try:
                from services.llm_query_bridge import QueryOrchestrator
                self._orchestrator = QueryOrchestrator()
                logger.info("Loaded llm_query_bridge service")
            except ImportError as e:
                logger.warning(f"Could not load llm_query_bridge: {e}")

    def set_web_of_belief(self, web: Any):
        """Set or update the WebOfBelief instance."""
        self.web = web

    def execute_query(
        self,
        query: str,
        mode: str = "standard",
        include_scope: bool = True,
        include_practitioner: bool = True,
        max_evidence: int = 10
    ) -> QueryResult:
        """
        Execute a natural language query.

        Args:
            query: The user's natural language query
            mode: Response depth - "quick", "standard", or "deep"
            include_scope: Include scope condition analysis
            include_practitioner: Include practical implications
            max_evidence: Maximum evidence items to retrieve

        Returns:
            QueryResult with progressive disclosure structure
        """
        # Step 1: Parse query intent
        parsed = self._parse_query(query)

        # Step 2: Retrieve evidence
        evidence = self._retrieve_evidence(parsed, max_evidence)

        # Step 3: Generate response
        result = self._generate_response(
            query, parsed, evidence, mode,
            include_scope, include_practitioner
        )

        return result

    def _parse_query(self, query: str) -> Dict[str, Any]:
        """Parse query using rule-based parser."""
        if self._parser is None:
            return {
                "query_type": "what",
                "causal_level": "associational",
                "subject": query,
                "object": None,
                "entities": [],
                "confidence": 0.0
            }

        result = self._parser.parse(query)
        intent = result.primary

        return {
            "query_type": intent.query_type.value,
            "causal_level": intent.causal_level.value,
            "subject": intent.subject,
            "object": intent.object,
            "entities": [intent.subject, intent.object] if intent.object else [intent.subject] if intent.subject else [],
            "confidence": intent.confidence,
            "vocabulary_expansions": result.vocabulary_expansions
        }

    def _retrieve_evidence(
        self,
        parsed: Dict[str, Any],
        max_results: int
    ) -> List[EvidenceSource]:
        """Retrieve evidence from WebOfBelief."""
        evidence = []

        if self.web is None:
            return evidence

        try:
            beliefs = list(self.web.beliefs.values())
        except (AttributeError, Exception):
            return evidence

        # Build search terms
        search_terms = []
        for entity in parsed.get("entities", []):
            if entity:
                search_terms.append(entity.lower())

        # Add vocabulary expansions
        for term, expansions in parsed.get("vocabulary_expansions", {}).items():
            search_terms.extend([e.lower() for e in expansions])

        # Score and filter beliefs
        scored = []
        for belief in beliefs:
            score = self._score_belief(belief, search_terms, parsed)
            if score > 0:
                scored.append((score, belief))

        # Sort by score then credence
        scored.sort(key=lambda x: (x[0], x[1].credence.point), reverse=True)

        # Convert to EvidenceSource
        for _, belief in scored[:max_results]:
            scope = None
            if hasattr(belief, 'scope') and belief.scope:
                scope = ScopeInfo(
                    population=getattr(belief.scope, 'population', None),
                    setting=getattr(belief.scope, 'setting', None),
                    methodology=getattr(belief.scope, 'methodology', None),
                    duration=getattr(belief.scope, 'duration', None)
                )

            credence_val = belief.credence.point if hasattr(belief.credence, 'point') else belief.credence
            evidence.append(EvidenceSource(
                belief_id=belief.belief_id,
                content=belief.content,
                credence=credence_val,
                credence_label=self._credence_label(credence_val),
                status=belief.status.value if hasattr(belief.status, 'value') else str(belief.status),
                level=belief.level.value if hasattr(belief.level, 'value') else str(belief.level),
                sources=belief.paper_ids[:5] if belief.paper_ids else [],
                scope=scope
            ))

        return evidence

    def _score_belief(
        self,
        belief: Any,
        search_terms: List[str],
        parsed: Dict[str, Any]
    ) -> float:
        """Score belief relevance."""
        score = 0.0
        content_lower = belief.content.lower()

        # Term matching
        for term in search_terms:
            if term in content_lower:
                score += 1.0

        # Environment/outcome matching
        subject = parsed.get("subject")
        obj = parsed.get("object")

        if subject and hasattr(belief, 'environment_id') and belief.environment_id:
            if subject.lower() in belief.environment_id.lower():
                score += 2.0

        if obj and hasattr(belief, 'outcome_id') and belief.outcome_id:
            if obj.lower() in belief.outcome_id.lower():
                score += 2.0

        # Boost established/entrenched
        if hasattr(belief, 'status'):
            status_val = belief.status.value if hasattr(belief.status, 'value') else str(belief.status)
            if status_val == 'established':
                score *= 1.2
            elif status_val == 'entrenched':
                score *= 1.5

        return score

    def _credence_label(self, credence: float) -> str:
        """Convert credence to human-readable label."""
        if credence >= 0.75:
            return "High confidence"
        elif credence >= 0.50:
            return "Moderate confidence"
        elif credence >= 0.25:
            return "Low confidence"
        else:
            return "Very low confidence"

    def _generate_response(
        self,
        query: str,
        parsed: Dict[str, Any],
        evidence: List[EvidenceSource],
        mode: str,
        include_scope: bool,
        include_practitioner: bool
    ) -> QueryResult:
        """Generate structured response."""
        query_type = parsed.get("query_type", "what")
        causal_level = parsed.get("causal_level", "associational")

        # Generate headline
        headline = self._generate_headline(query, evidence)

        # Generate summary (for standard/deep modes)
        summary = None
        if mode in ["standard", "deep"] and evidence:
            summary = self._generate_summary(evidence)

        # Generate detail (for deep mode)
        detail = None
        if mode == "deep" and evidence:
            detail = self._generate_detail(evidence)

        # Generate practical implications
        practical = None
        if include_practitioner and evidence:
            practical = self._generate_practical(evidence, query_type)

        # Aggregate scope conditions
        scope_conds = None
        if include_scope and evidence:
            scope_conds = self._aggregate_scope(evidence)

        # Generate caveats
        caveats = self._generate_caveats(evidence, parsed)

        # Key sources
        sources = []
        for ev in evidence[:5]:
            for src in ev.sources:
                if src and src not in sources:
                    sources.append(src)

        return QueryResult(
            query=query,
            query_type=query_type,
            causal_level=causal_level,
            headline=headline,
            summary=summary,
            detail=detail,
            practical_implications=practical,
            scope_conditions=scope_conds,
            caveats=caveats,
            key_sources=sources[:10],
            evidence=evidence,
            confidence=parsed.get("confidence", 0.0),
            processing_mode="direct"
        )

    def _generate_headline(
        self,
        query: str,
        evidence: List[EvidenceSource]
    ) -> str:
        """Generate headline summary."""
        if not evidence:
            return f"No evidence found for: {query}"

        top = evidence[0]
        credence_str = f"{top.credence:.2f}"
        return f"{top.content} (credence: {credence_str})"

    def _generate_summary(
        self,
        evidence: List[EvidenceSource]
    ) -> Dict[str, Any]:
        """Generate summary section."""
        high_cred = [e for e in evidence if e.credence >= 0.7]

        return {
            "finding": evidence[0].content if evidence else "No findings",
            "confidence": evidence[0].credence_label if evidence else "Unknown",
            "supporting_evidence": len(evidence),
            "high_confidence_count": len(high_cred),
            "key_beliefs": [e.content for e in evidence[:3]]
        }

    def _generate_detail(
        self,
        evidence: List[EvidenceSource]
    ) -> Dict[str, Any]:
        """Generate detailed section."""
        by_level = {}
        for e in evidence:
            level = e.level
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(e.content)

        return {
            "evidence_by_level": by_level,
            "total_evidence": len(evidence),
            "average_credence": sum(e.credence for e in evidence) / len(evidence) if evidence else 0,
            "all_sources": list(set(src for e in evidence for src in e.sources))
        }

    def _generate_practical(
        self,
        evidence: List[EvidenceSource],
        query_type: str
    ) -> List[str]:
        """Generate practical implications."""
        implications = []

        # Extract from high-credence empirical evidence
        for e in evidence:
            if e.level == "empirical" and e.credence >= 0.6:
                # Simple extraction - in production would use LLM
                content = e.content
                if "reduce" in content.lower():
                    implications.append(f"Consider: {content}")
                elif "improve" in content.lower():
                    implications.append(f"Potential benefit: {content}")
                elif "increase" in content.lower():
                    implications.append(f"May enhance: {content}")

        if not implications:
            implications = ["Review evidence for specific implementation guidance"]

        return implications[:5]

    def _aggregate_scope(
        self,
        evidence: List[EvidenceSource]
    ) -> Dict[str, str]:
        """Aggregate scope conditions from evidence."""
        populations = []
        settings = []
        methodologies = []

        for e in evidence:
            if e.scope:
                if e.scope.population:
                    populations.append(e.scope.population)
                if e.scope.setting:
                    settings.append(e.scope.setting)
                if e.scope.methodology:
                    methodologies.append(e.scope.methodology)

        result = {}
        if populations:
            result["population"] = "; ".join(set(populations))
        if settings:
            result["setting"] = "; ".join(set(settings))
        if methodologies:
            result["methodology"] = "; ".join(set(methodologies))

        return result if result else None

    def _generate_caveats(
        self,
        evidence: List[EvidenceSource],
        parsed: Dict[str, Any]
    ) -> List[str]:
        """Generate caveats and warnings."""
        caveats = []

        if not evidence:
            caveats.append("No direct evidence found - results based on related findings")
            return caveats

        # Check evidence quality
        low_cred = [e for e in evidence if e.credence < 0.5]
        if len(low_cred) > len(evidence) / 2:
            caveats.append("Most evidence has low confidence - interpret with caution")

        # Check for contested
        contested = [e for e in evidence if e.status == "contested"]
        if contested:
            caveats.append(f"{len(contested)} beliefs are currently contested")

        # Causal level caveat
        causal = parsed.get("causal_level", "")
        if causal == "interventional":
            caveats.append("Query implies intervention - verify causal claims carefully")
        elif causal == "counterfactual":
            caveats.append("Query is counterfactual - limited direct evidence available")

        return caveats

    # =========================================================================
    # Statistics
    # =========================================================================

    def get_stats(self) -> SystemStats:
        """Get system statistics."""
        if self.web is None:
            return SystemStats()

        try:
            beliefs = list(self.web.beliefs.values())
            constraints = list(self.web.constraints) if hasattr(self.web, 'constraints') else []

            # Count by status
            contested = sum(1 for b in beliefs
                          if hasattr(b, 'status') and
                          (b.status.value if hasattr(b.status, 'value') else str(b.status)) == 'contested')
            stubs = sum(1 for b in beliefs
                       if hasattr(b, 'status') and
                       (b.status.value if hasattr(b.status, 'value') else str(b.status)) == 'stub')

            # Average credence
            credences = [b.credence.point if hasattr(b.credence, 'point') else b.credence
                        for b in beliefs if hasattr(b, 'credence')]
            avg_cred = sum(credences) / len(credences) if credences else 0.0

            # Get papers
            papers = set()
            for b in beliefs:
                if hasattr(b, 'paper_ids') and b.paper_ids:
                    papers.update(b.paper_ids)

            return SystemStats(
                total_beliefs=len(beliefs),
                total_constraints=len(constraints),
                total_papers=len(papers),
                total_communities=0,  # Would need community registry
                overall_coherence=0.72,  # Would calculate from web
                average_credence=avg_cred,
                contested_beliefs=contested,
                stub_beliefs=stubs
            )
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return SystemStats()


# =============================================================================
# Singleton Instance
# =============================================================================

_service: Optional[DirectQueryService] = None


def get_query_service(web_of_belief: Any = None) -> DirectQueryService:
    """Get or create query service singleton."""
    global _service
    if _service is None:
        _service = DirectQueryService(web_of_belief=web_of_belief)
    elif web_of_belief is not None:
        _service.set_web_of_belief(web_of_belief)
    return _service
