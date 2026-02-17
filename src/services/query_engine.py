"""
Query Engine Service (MVP-3)
============================

Created: 2026-02-11
Owner: Terminal 2

Main orchestration for the Article Eater query system.
Implements ae.query_request.v1 → ae.query_response.v1 contract.

Components used:
- WebAccumulator: Load persistent web state
- QueryParser: Parse natural language queries
- QueryResponseGenerator: Generate responses with progressive disclosure
- VOI Search: Identify knowledge gaps

Usage:
    from src.services.query_engine import QueryEngine

    engine = QueryEngine()

    # Simple query
    response = engine.query("What affects attention?")

    # Full contract query
    request = {
        "schema": "ae.query_request.v1",
        "query_id": "q_001",
        "query_text": "Does natural light improve productivity?",
        "response_mode": "summary",
        "include_gaps": True
    }
    response = engine.query_from_request(request)
"""

import json
import logging
import uuid
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Import components
from src.services.web_accumulator import WebAccumulator, AccumulatorStats
from src.services.query_parser import (
    QueryParser, QueryType, CausalLevel, QueryIntent, ParseResult
)
from src.services.query_response import (
    QueryResponseGenerator, ResponseMode, ProgressiveResponse,
    EvidenceItem, FollowUp
)
from src.services.web_of_belief import WebOfBelief, Belief, EpistemicLevel
from src.argument.qa_handlers import ArgumentQueryHandler

# Optional VOI integration
try:
    from src.services.voi_search import (
        VOIGapScorer, GapType, ResearchGap, SuggestedSearch
    )
    VOI_AVAILABLE = True
except ImportError:
    VOI_AVAILABLE = False
    logger.debug("VOI search not available")


@dataclass
class QueryResult:
    """Internal result before formatting to schema."""
    query_id: str
    query_text: str
    status: str  # success, partial, no_results, error
    parse_result: ParseResult
    matched_beliefs: List[Belief]
    headline: str
    confidence: float
    uncertainty: float
    processing_time_ms: int
    gaps: Optional[List[Dict]] = None
    error: Optional[str] = None


class QueryEngine:
    """
    Main query engine for Article Eater.

    Implements the ae.query_request.v1 → ae.query_response.v1 contract.
    """

    def __init__(
        self,
        accumulator: Optional[WebAccumulator] = None,
        web: Optional[WebOfBelief] = None,
        argument_query_handler: Optional[ArgumentQueryHandler] = None,
    ):
        """
        Initialize the query engine.

        Args:
            accumulator: WebAccumulator instance (loads from DB)
            web: Direct WebOfBelief instance (for testing)
            argument_query_handler: Optional argument-specific query router
        """
        self._accumulator = accumulator
        self._web = web
        self._parser = QueryParser()
        self._response_gen = None  # Lazy init
        self._voi_scorer = None  # Lazy init
        self._argument_query_handler = argument_query_handler

    @property
    def accumulator(self) -> WebAccumulator:
        """Lazy-load accumulator."""
        if self._accumulator is None:
            self._accumulator = WebAccumulator()
        return self._accumulator

    @property
    def web(self) -> WebOfBelief:
        """Get the web of belief (from accumulator or direct)."""
        if self._web is not None:
            return self._web

        # Load from accumulator
        try:
            self._web = self.accumulator.persistence.load_master_web()
            if self._web is None:
                # Create empty web if none exists
                self._web = WebOfBelief(domain="neuroarchitecture")
                logger.warning("No accumulated web found, using empty web")
        except Exception as e:
            logger.error(f"Failed to load web: {e}")
            self._web = WebOfBelief(domain="neuroarchitecture")

        return self._web

    @property
    def response_gen(self) -> QueryResponseGenerator:
        """Lazy-load response generator."""
        if self._response_gen is None:
            self._response_gen = QueryResponseGenerator(self.web)
        return self._response_gen

    def query(
        self,
        query_text: str,
        response_mode: str = "summary",
        include_gaps: bool = False,
        max_results: int = 10,
        min_credence: float = 0.3
    ) -> Dict[str, Any]:
        """
        Simple query interface.

        Args:
            query_text: Natural language query
            response_mode: headline, summary, detail, deep_dive
            include_gaps: Include gap analysis
            max_results: Max beliefs to return
            min_credence: Minimum credence threshold

        Returns:
            Query response dict (ae.query_response.v1 format)
        """
        request = {
            "schema": "ae.query_request.v1",
            "query_id": f"q_{uuid.uuid4().hex[:8]}",
            "query_text": query_text,
            "response_mode": response_mode,
            "include_gaps": include_gaps,
            "max_results": max_results,
            "min_credence": min_credence
        }
        return self.query_from_request(request)

    def query_from_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a query request per ae.query_request.v1 schema.

        Args:
            request: Query request dict

        Returns:
            Query response dict (ae.query_response.v1 format)
        """
        start_time = time.time()

        # Validate request
        if request.get("schema") not in [None, "ae.query_request.v1"]:
            return self._error_response(
                request.get("query_id", "unknown"),
                "invalid_schema",
                f"Expected ae.query_request.v1, got {request.get('schema')}"
            )

        query_id = request.get("query_id", f"q_{uuid.uuid4().hex[:8]}")
        query_text = request.get("query_text", "")

        if not query_text:
            return self._error_response(query_id, "empty_query", "Query text is required")

        # Route argument-structure queries before generic parser/search.
        if self._argument_query_handler is not None:
            argument_response = self._argument_query_handler.handle_query(
                query_id=query_id,
                query_text=query_text,
                processing_time_ms=int((time.time() - start_time) * 1000),
            )
            if argument_response is not None:
                return argument_response

        # Parse the query
        parse_result = self._parser.parse(query_text)

        # D7 Repair (Simon): Attempt search even for ambiguous queries
        # Return partial results with clarification, don't block
        needs_clarification = parse_result.needs_clarification

        # Search the web
        matched_beliefs = self._search_web(
            parse_result=parse_result,
            context=request.get("context"),
            min_credence=request.get("min_credence", 0.3),
            max_results=request.get("max_results", 10)
        )

        # Generate response
        processing_time_ms = int((time.time() - start_time) * 1000)

        response_mode = ResponseMode(request.get("response_mode", "summary"))

        if not matched_beliefs:
            # No results - check if clarification would help
            if needs_clarification:
                return self._clarification_response(query_id, query_text, parse_result)
            return self._no_results_response(
                query_id, query_text, parse_result, processing_time_ms,
                include_gaps=request.get("include_gaps", False)
            )

        # Build response
        response = self._build_response(
            query_id=query_id,
            query_text=query_text,
            parse_result=parse_result,
            matched_beliefs=matched_beliefs,
            response_mode=response_mode,
            include_gaps=request.get("include_gaps", False),
            processing_time_ms=processing_time_ms
        )

        # D7: If clarification was needed but we found results, mark as partial
        if needs_clarification:
            response["status"] = "partial"
            response["clarification"] = {
                "reason": "Query was ambiguous - showing best matches",
                "options": [
                    {
                        "label": opt,
                        "description": f"Search for {opt}",
                        "query_text": opt
                    }
                    for opt in parse_result.clarification_options[:4]
                ]
            }

        return response

    def _search_web(
        self,
        parse_result: ParseResult,
        context: Optional[Dict] = None,
        min_credence: float = 0.3,
        max_results: int = 10
    ) -> List[Belief]:
        """Search the web for matching beliefs."""
        intent = parse_result.primary
        matched = []

        # Get all search terms (subject + object + expansions)
        search_terms = set()
        if intent.subject:
            search_terms.add(intent.subject.lower())
            search_terms.update(t.lower() for t in intent.subject_expansions)
        if intent.object:
            search_terms.add(intent.object.lower())
            search_terms.update(t.lower() for t in intent.object_expansions)

        # Add vocabulary expansions
        for term_expansions in parse_result.vocabulary_expansions.values():
            search_terms.update(t.lower() for t in term_expansions)

        if not search_terms:
            # Fall back to tokenizing the query
            tokens = intent.normalized_query.lower().split()
            search_terms.update(t for t in tokens if len(t) > 3)

        # Search beliefs
        for belief in self.web.beliefs.values():
            # Check credence threshold
            if belief.credence.value < min_credence:
                continue

            # Check if belief matches search terms
            content_lower = belief.content.lower()
            tags_lower = [t.lower() for t in belief.tags]

            # Score based on term matches
            score = 0
            for term in search_terms:
                if term in content_lower:
                    score += 2
                if any(term in tag for tag in tags_lower):
                    score += 1

            if score > 0:
                matched.append((score, belief.credence.value, belief))

            # Apply context filters
            if context:
                if context.get("theory_filter"):
                    if belief.theory_id not in context["theory_filter"]:
                        continue

        # Sort by score (descending), then credence (descending)
        matched.sort(key=lambda x: (-x[0], -x[1]))

        return [b for _, _, b in matched[:max_results]]

    def _build_response(
        self,
        query_id: str,
        query_text: str,
        parse_result: ParseResult,
        matched_beliefs: List[Belief],
        response_mode: ResponseMode,
        include_gaps: bool,
        processing_time_ms: int
    ) -> Dict[str, Any]:
        """Build the full response dict."""
        intent = parse_result.primary

        # Generate headline
        if matched_beliefs:
            top_belief = matched_beliefs[0]
            headline = self._generate_headline(top_belief, len(matched_beliefs))
        else:
            headline = "No relevant evidence found."

        # Calculate overall confidence
        if matched_beliefs:
            credences = [b.credence.value for b in matched_beliefs]
            avg_credence = sum(credences) / len(credences)
            avg_uncertainty = sum(b.credence.uncertainty for b in matched_beliefs) / len(matched_beliefs)
        else:
            avg_credence = 0.0
            avg_uncertainty = 1.0

        response = {
            "schema": "ae.query_response.v1",
            "query_id": query_id,
            "status": "success",
            "response_mode": response_mode.value,
            "headline": headline,
            "metadata": {
                "processing_time_ms": processing_time_ms,
                "n_beliefs_searched": len(self.web.beliefs),
                "n_beliefs_matched": len(matched_beliefs),
                "parse_confidence": intent.confidence,
                "causal_level": intent.causal_level.value,
                "query_type": intent.query_type.value,
                "vocabulary_expansions": parse_result.vocabulary_expansions
            }
        }

        # Add summary if mode >= summary
        if response_mode in (ResponseMode.SUMMARY, ResponseMode.DETAIL, ResponseMode.DEEP_DIVE):
            response["summary"] = self._build_summary(
                matched_beliefs[:5], avg_credence, avg_uncertainty
            )
            response["follow_ups"] = self._generate_follow_ups(intent, matched_beliefs)

        # Add detail if mode >= detail
        if response_mode in (ResponseMode.DETAIL, ResponseMode.DEEP_DIVE):
            response["detail"] = self._build_detail(matched_beliefs)

        # Add deep dive if mode = deep_dive
        if response_mode == ResponseMode.DEEP_DIVE:
            response["deep_dive"] = self._build_deep_dive(matched_beliefs)

        # Add gaps if requested
        if include_gaps:
            response["gaps"] = self._identify_gaps(intent)

        return response

    def _generate_headline(self, top_belief: Belief, n_matches: int) -> str:
        """Generate a one-sentence headline."""
        content = top_belief.content
        if len(content) > 100:
            content = content[:97] + "..."

        credence = top_belief.credence.value
        uncertainty = top_belief.credence.uncertainty

        return f"{content} (credence: {credence:.2f} ± {uncertainty:.2f}, {n_matches} related beliefs)"

    def _build_summary(
        self,
        top_beliefs: List[Belief],
        avg_credence: float,
        avg_uncertainty: float
    ) -> Dict[str, Any]:
        """Build summary response."""
        evidence_items = []
        for belief in top_beliefs:
            evidence_items.append({
                "belief_id": belief.belief_id,
                "content": belief.content[:200],
                "credence": belief.credence.value,
                "uncertainty": belief.credence.uncertainty,
                "source_depth": belief.source_depth.value if hasattr(belief.source_depth, 'value') else str(belief.source_depth),
                "paper_ids": belief.paper_ids,
                "is_causal": self._is_causal_claim(belief),
                "needs_caution": belief.source_depth.value == "abstract" if hasattr(belief.source_depth, 'value') else False
            })

        # Extract scope conditions from beliefs
        scope_conditions = {}
        for belief in top_beliefs:
            if hasattr(belief, 'scope_conditions') and belief.scope_conditions:
                if belief.scope_conditions.population:
                    scope_conditions["population"] = belief.scope_conditions.population
                if belief.scope_conditions.setting:
                    scope_conditions["setting"] = belief.scope_conditions.setting

        return {
            "answer_confidence": avg_credence,
            "answer_uncertainty": avg_uncertainty,
            "key_evidence": evidence_items,
            "scope_conditions": scope_conditions if scope_conditions else None,
            "practical_implications": self._extract_implications(top_beliefs),
            "caveats": self._extract_caveats(top_beliefs)
        }

    def _build_detail(self, matched_beliefs: List[Belief]) -> Dict[str, Any]:
        """Build detailed response."""
        all_evidence = []
        theories = {}
        abstract_warnings = []

        for belief in matched_beliefs:
            all_evidence.append({
                "belief_id": belief.belief_id,
                "content": belief.content,
                "credence": belief.credence.value,
                "uncertainty": belief.credence.uncertainty,
                "source_depth": belief.source_depth.value if hasattr(belief.source_depth, 'value') else str(belief.source_depth),
                "paper_ids": belief.paper_ids,
                "is_causal": self._is_causal_claim(belief),
                "needs_caution": False
            })

            # Track theories
            if belief.theory_id:
                if belief.theory_id not in theories:
                    theories[belief.theory_id] = {"theory_id": belief.theory_id, "contribution": 0}
                theories[belief.theory_id]["contribution"] += 1

            # Track abstract-only causal claims
            if self._is_causal_claim(belief):
                if hasattr(belief.source_depth, 'value') and belief.source_depth.value == "abstract":
                    abstract_warnings.append(belief.belief_id)

        return {
            "all_evidence": all_evidence,
            "theories_involved": list(theories.values()),
            "methodological_notes": [],
            "abstract_only_warnings": abstract_warnings
        }

    def _build_deep_dive(self, matched_beliefs: List[Belief]) -> Dict[str, Any]:
        """Build deep dive response."""
        belief_ids = [b.belief_id for b in matched_beliefs]

        # Get entrenchment scores
        entrenchment = {}
        for belief in matched_beliefs:
            try:
                entrenchment[belief.belief_id] = self.web.get_entrenchment(belief.belief_id)
            except Exception:
                entrenchment[belief.belief_id] = 0.5

        return {
            "constraint_network": self._get_constraint_subgraph(belief_ids),
            "entrenchment_scores": entrenchment,
            "community_credences": {},  # Would come from social epistemology
            "counterfactual_analysis": None
        }

    def _get_constraint_subgraph(self, belief_ids: List[str]) -> Dict[str, Any]:
        """Get constraints involving the matched beliefs."""
        nodes = belief_ids
        edges = []

        for constraint in self.web.constraints.values():
            if constraint.source_id in belief_ids or constraint.target_id in belief_ids:
                edges.append({
                    "source": constraint.source_id,
                    "target": constraint.target_id,
                    "type": constraint.constraint_type.value,
                    "strength": constraint.strength
                })

        return {"nodes": nodes, "edges": edges}

    def _generate_follow_ups(
        self,
        intent: QueryIntent,
        matched_beliefs: List[Belief]
    ) -> List[Dict[str, Any]]:
        """Generate exactly 3 follow-ups: deeper, broader, uncertainty."""
        follow_ups = []

        subject = intent.subject or "this topic"
        obj = intent.object or ""

        # Deeper
        follow_ups.append({
            "question": f"What specific mechanisms explain the effect of {subject}?",
            "type": "deeper",
            "executable_query": f"mechanism {subject} {obj}".strip()
        })

        # Broader
        follow_ups.append({
            "question": f"What other factors are related to {obj or subject}?",
            "type": "broader",
            "executable_query": f"what affects {obj or subject}"
        })

        # Uncertainty
        follow_ups.append({
            "question": f"What don't we know about {subject}?",
            "type": "uncertainty",
            "executable_query": f"gaps {subject} {obj}".strip()
        })

        return follow_ups

    def _identify_gaps(self, intent: QueryIntent) -> Dict[str, Any]:
        """Identify knowledge gaps related to the query."""
        # Simple gap detection based on belief coverage
        gaps = []

        subject = intent.subject or ""
        obj = intent.object or ""

        # Check for unexplored combinations
        subject_beliefs = [b for b in self.web.beliefs.values()
                          if subject.lower() in b.content.lower()]
        object_beliefs = [b for b in self.web.beliefs.values()
                         if obj.lower() in b.content.lower()] if obj else []

        # If subject has beliefs but object doesn't
        if subject_beliefs and obj and not object_beliefs:
            gaps.append({
                "gap_id": f"gap_{uuid.uuid4().hex[:8]}",
                "gap_type": "unexplored",
                "description": f"No evidence found for '{obj}'",
                "priority": 0.7,
                "suggested_search": f"{obj} research studies"
            })

        # D3 Repair (Cartwright): Weight uncertainty by epistemic level
        # THEORETICAL uncertainty × 1.5, EMPIRICAL × 1.0
        def weighted_uncertainty(belief: Belief) -> float:
            base = belief.credence.uncertainty
            if belief.level == EpistemicLevel.THEORETICAL:
                return base * 1.5
            return base

        uncertain_beliefs = [b for b in self.web.beliefs.values()
                            if weighted_uncertainty(b) > 0.3 and
                            (subject.lower() in b.content.lower() or
                             (obj and obj.lower() in b.content.lower()))]

        if uncertain_beliefs:
            gaps.append({
                "gap_id": f"gap_{uuid.uuid4().hex[:8]}",
                "gap_type": "uncertain",
                "description": f"{len(uncertain_beliefs)} beliefs have high uncertainty",
                "priority": 0.6,
                "affected_beliefs": [b.belief_id for b in uncertain_beliefs[:5]],
                "suggested_search": f"{subject} replication studies"
            })

        return {
            "n_gaps": len(gaps),
            "top_gaps": gaps[:5]
        }

    def _is_causal_claim(self, belief: Belief) -> bool:
        """
        Check if belief is a causal claim.

        D8 Repair (Pearl): Use causal_direction field, not keywords.
        Keywords are fallback only for UNKNOWN direction.
        """
        from src.services.web_of_belief import CausalDirection

        # Primary check: use causal_direction field (per Pearl panel)
        if hasattr(belief, 'causal_direction'):
            causal_directions = {
                CausalDirection.FORWARD,
                CausalDirection.REVERSE,
                CausalDirection.BIDIRECTIONAL,
                CausalDirection.MEDIATED
            }
            if belief.causal_direction in causal_directions:
                return True
            if belief.causal_direction == CausalDirection.CORRELATIONAL:
                return False  # Explicitly correlational, not causal

        # Fallback: keyword matching only for UNKNOWN direction
        causal_keywords = ['cause', 'effect', 'increase', 'decrease', 'improve',
                          'reduce', 'lead to', 'result in', 'affect']
        content_lower = belief.content.lower()
        return any(kw in content_lower for kw in causal_keywords)

    def _extract_implications(self, beliefs: List[Belief]) -> List[str]:
        """Extract practical implications from beliefs."""
        implications = []
        for belief in beliefs[:3]:
            if self._is_causal_claim(belief):
                # Simple extraction
                content = belief.content
                if len(content) < 150:
                    implications.append(f"Consider: {content}")
        return implications if implications else ["See evidence for actionable insights"]

    def _extract_caveats(self, beliefs: List[Belief]) -> List[str]:
        """Extract caveats from beliefs."""
        caveats = []

        # Check for abstract-only sources
        abstract_count = sum(1 for b in beliefs
                            if hasattr(b.source_depth, 'value') and
                            b.source_depth.value == "abstract")
        if abstract_count > 0:
            caveats.append(f"{abstract_count} beliefs based on abstracts only")

        # Check uncertainty
        high_uncertainty = [b for b in beliefs if b.credence.uncertainty > 0.25]
        if high_uncertainty:
            caveats.append(f"{len(high_uncertainty)} beliefs have notable uncertainty")

        return caveats if caveats else ["Standard caveats apply to all evidence"]

    def _no_results_response(
        self,
        query_id: str,
        query_text: str,
        parse_result: ParseResult,
        processing_time_ms: int,
        include_gaps: bool = False
    ) -> Dict[str, Any]:
        """Build response when no results found."""
        intent = parse_result.primary

        response = {
            "schema": "ae.query_response.v1",
            "query_id": query_id,
            "status": "no_results",
            "response_mode": "summary",
            "headline": "No relevant evidence found for this query.",
            "metadata": {
                "processing_time_ms": processing_time_ms,
                "n_beliefs_searched": len(self.web.beliefs),
                "n_beliefs_matched": 0,
                "parse_confidence": intent.confidence,
                "causal_level": intent.causal_level.value,
                "query_type": intent.query_type.value,
                "vocabulary_expansions": parse_result.vocabulary_expansions
            },
            "follow_ups": [
                {
                    "question": "What topics does the knowledge base cover?",
                    "type": "broader",
                    "executable_query": "what do we know"
                }
            ]
        }

        if include_gaps:
            response["gaps"] = {
                "n_gaps": 1,
                "top_gaps": [{
                    "gap_id": f"gap_{uuid.uuid4().hex[:8]}",
                    "gap_type": "unexplored",
                    "description": f"No evidence for query: {query_text}",
                    "priority": 0.8,
                    "suggested_search": query_text
                }]
            }

        return response

    def _clarification_response(
        self,
        query_id: str,
        query_text: str,
        parse_result: ParseResult
    ) -> Dict[str, Any]:
        """Build response when clarification needed."""
        return {
            "schema": "ae.query_response.v1",
            "query_id": query_id,
            "status": "clarification_needed",
            "response_mode": "headline",
            "headline": "Please clarify your question.",
            "clarification": {
                "reason": "Ambiguous query - multiple interpretations possible",
                "options": [
                    {
                        "label": opt,
                        "description": f"Search for {opt}",
                        "query_text": opt
                    }
                    for opt in parse_result.clarification_options[:4]
                ]
            }
        }

    def _error_response(
        self,
        query_id: str,
        code: str,
        message: str
    ) -> Dict[str, Any]:
        """Build error response."""
        return {
            "schema": "ae.query_response.v1",
            "query_id": query_id,
            "status": "error",
            "response_mode": "headline",
            "headline": "An error occurred processing your query.",
            "error": {
                "code": code,
                "message": message
            }
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base."""
        return {
            "n_beliefs": len(self.web.beliefs),
            "n_constraints": len(self.web.constraints),
            "coherence": self.web.coherence_score(),
            "theories": list(self.web.theory_ids)
        }


# Convenience function for CLI
def run_query(query_text: str, mode: str = "summary") -> Dict[str, Any]:
    """Run a query and return results."""
    engine = QueryEngine()
    return engine.query(query_text, response_mode=mode)
