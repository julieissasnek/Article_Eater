"""
Article Eater V23 — LLM Query Bridge
Sprint 3.0.2 — 2026-02-08

Multi-AI orchestration for query processing.
Different models handle different phases:
- Intent Detection: Fast model (Haiku/GPT-4o-mini) for parsing
- Evidence Retrieval: No LLM (structured search)
- Response Synthesis: Capable model (Sonnet/GPT-4o) for nuanced answers
- Deep Explanation: Most capable (Opus/o1) for complex reasoning

Architecture based on AI panel recommendations:
- Liang: LLM for interpretation + synthesis, not facts
- LeCun: Structured retrieval without LLM
- Amodei: Model tiering for cost optimization
- Bender: Prompt engineering with scope/confidence
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import time

logger = logging.getLogger(__name__)


class QueryPhase(Enum):
    """Phases of query processing."""
    INTENT = "intent"           # Parse NL to structured query
    RETRIEVAL = "retrieval"     # Get evidence from web (no LLM)
    SYNTHESIS = "synthesis"     # Generate response
    EXPLANATION = "explanation" # Deep dive if requested


class QueryType(Enum):
    """Query types based on Pearl's causal ladder + Bates extensions."""
    WHAT = "what"               # Associational
    WHY = "why"                 # Mechanism explanation
    COMPARE = "compare"         # Comparison
    GAPS = "gaps"               # What don't we know
    CONTRADICT = "contradict"   # Conflicting evidence
    CONTINGENT = "contingent"   # Scope conditions
    HOW_CONFIDENT = "how_confident"  # Confidence assessment
    RELATED = "related"         # Serendipitous discovery
    TRENDING = "trending"       # Temporal patterns
    CANONICAL = "canonical"     # Entry points


class CausalLevel(Enum):
    """Pearl's causal ladder for query classification."""
    ASSOCIATIONAL = "associational"   # What is correlated?
    INTERVENTIONAL = "interventional" # What would happen if?
    COUNTERFACTUAL = "counterfactual" # What would have been?


class ModelTier(Enum):
    """Model capability tiers for cost optimization."""
    NONE = "none"       # Template/rule-based, no LLM
    FAST = "fast"       # Haiku, GPT-4o-mini, Gemini Flash
    CAPABLE = "capable" # Sonnet, GPT-4o, Gemini Pro
    BEST = "best"       # Opus, o1, Gemini Ultra


@dataclass
class ModelConfig:
    """Configuration for an LLM model."""
    provider: str  # anthropic, openai, google, local
    model_id: str
    tier: ModelTier
    cost_per_1k_input: float
    cost_per_1k_output: float
    max_tokens: int = 4096
    temperature: float = 0.0


@dataclass
class ParsedQuery:
    """Result of intent detection phase."""
    original: str
    query_type: QueryType
    causal_level: CausalLevel
    entities: List[str] = field(default_factory=list)
    subject: Optional[str] = None
    object: Optional[str] = None
    scope_hints: Dict[str, str] = field(default_factory=dict)
    confidence: float = 0.0


@dataclass
class EvidenceItem:
    """Single piece of evidence from retrieval."""
    belief_id: str
    content: str
    credence: float
    status: str
    level: str
    sources: List[str] = field(default_factory=list)
    scope_conditions: Optional[Dict[str, str]] = None


@dataclass
class QueryResponse:
    """Structured response with progressive disclosure."""
    query: str
    query_type: str
    causal_level: str

    # Progressive disclosure levels
    headline: str
    summary: Optional[Dict[str, Any]] = None
    detail: Optional[Dict[str, Any]] = None

    # Additional sections
    practical_implications: Optional[List[str]] = None
    scope_conditions: Optional[Dict[str, str]] = None
    caveats: Optional[List[str]] = None
    key_sources: Optional[List[str]] = None

    # Metadata
    models_used: Dict[str, str] = field(default_factory=dict)
    cost_estimate: float = 0.0
    processing_time_ms: int = 0


# Model registry with cost information
MODEL_REGISTRY: Dict[str, ModelConfig] = {
    # Anthropic
    "claude-haiku": ModelConfig(
        provider="anthropic",
        model_id="claude-3-haiku-20240307",
        tier=ModelTier.FAST,
        cost_per_1k_input=0.00025,
        cost_per_1k_output=0.00125
    ),
    "claude-sonnet": ModelConfig(
        provider="anthropic",
        model_id="claude-sonnet-4-20250514",
        tier=ModelTier.CAPABLE,
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015
    ),
    "claude-opus": ModelConfig(
        provider="anthropic",
        model_id="claude-opus-4-20250514",
        tier=ModelTier.BEST,
        cost_per_1k_input=0.015,
        cost_per_1k_output=0.075
    ),

    # OpenAI
    "gpt-4o-mini": ModelConfig(
        provider="openai",
        model_id="gpt-4o-mini",
        tier=ModelTier.FAST,
        cost_per_1k_input=0.00015,
        cost_per_1k_output=0.0006
    ),
    "gpt-4o": ModelConfig(
        provider="openai",
        model_id="gpt-4o",
        tier=ModelTier.CAPABLE,
        cost_per_1k_input=0.005,
        cost_per_1k_output=0.015
    ),
    "o1": ModelConfig(
        provider="openai",
        model_id="o1",
        tier=ModelTier.BEST,
        cost_per_1k_input=0.015,
        cost_per_1k_output=0.060
    ),

    # Google
    "gemini-flash": ModelConfig(
        provider="google",
        model_id="gemini-1.5-flash",
        tier=ModelTier.FAST,
        cost_per_1k_input=0.000075,
        cost_per_1k_output=0.0003
    ),
    "gemini-pro": ModelConfig(
        provider="google",
        model_id="gemini-1.5-pro",
        tier=ModelTier.CAPABLE,
        cost_per_1k_input=0.00125,
        cost_per_1k_output=0.005
    ),
}


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def complete(
        self,
        prompt: str,
        model_config: ModelConfig,
        system: Optional[str] = None
    ) -> Tuple[str, int, int]:
        """
        Generate completion.

        Returns:
            Tuple of (response_text, input_tokens, output_tokens)
        """
        pass


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""

    def __init__(self):
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                logger.warning("anthropic package not installed")
        return self._client

    def complete(
        self,
        prompt: str,
        model_config: ModelConfig,
        system: Optional[str] = None
    ) -> Tuple[str, int, int]:
        if not self.client:
            return self._mock_response(prompt), 100, 50

        try:
            response = self.client.messages.create(
                model=model_config.model_id,
                max_tokens=model_config.max_tokens,
                temperature=model_config.temperature,
                system=system or "You are a helpful research assistant.",
                messages=[{"role": "user", "content": prompt}]
            )
            return (
                response.content[0].text,
                response.usage.input_tokens,
                response.usage.output_tokens
            )
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return self._mock_response(prompt), 100, 50

    def _mock_response(self, prompt: str) -> str:
        """Return mock response for testing."""
        return json.dumps({
            "query_type": "WHAT",
            "causal_level": "associational",
            "entities": ["plants", "stress"],
            "subject": "plants",
            "object": "stress",
            "confidence": 0.85
        })


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider."""

    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                logger.warning("openai package not installed")
        return self._client

    def complete(
        self,
        prompt: str,
        model_config: ModelConfig,
        system: Optional[str] = None
    ) -> Tuple[str, int, int]:
        if not self.client:
            return self._mock_response(prompt), 100, 50

        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=model_config.model_id,
                messages=messages,
                max_tokens=model_config.max_tokens,
                temperature=model_config.temperature
            )
            return (
                response.choices[0].message.content,
                response.usage.prompt_tokens,
                response.usage.completion_tokens
            )
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._mock_response(prompt), 100, 50

    def _mock_response(self, prompt: str) -> str:
        return json.dumps({
            "query_type": "WHAT",
            "causal_level": "associational",
            "entities": ["plants", "stress"],
            "confidence": 0.85
        })


class GoogleProvider(LLMProvider):
    """Google Gemini provider."""

    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai
            except ImportError:
                logger.warning("google-generativeai package not installed")
        return self._client

    def complete(
        self,
        prompt: str,
        model_config: ModelConfig,
        system: Optional[str] = None
    ) -> Tuple[str, int, int]:
        if not self.client:
            return self._mock_response(prompt), 100, 50

        try:
            model = self.client.GenerativeModel(
                model_config.model_id,
                system_instruction=system
            )
            response = model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": model_config.max_tokens,
                    "temperature": model_config.temperature
                }
            )
            # Estimate tokens (Gemini doesn't always return exact counts)
            input_tokens = len(prompt.split()) * 1.3  # rough estimate
            output_tokens = len(response.text.split()) * 1.3
            return (
                response.text,
                int(input_tokens),
                int(output_tokens)
            )
        except Exception as e:
            logger.error(f"Google API error: {e}")
            return self._mock_response(prompt), 100, 50

    def _mock_response(self, prompt: str) -> str:
        return json.dumps({
            "query_type": "WHAT",
            "causal_level": "associational",
            "entities": ["plants", "stress"],
            "confidence": 0.85
        })


class MultiAIOrchestrator:
    """
    Orchestrates multiple AI models for different query phases.

    Phase → Model Tier mapping:
    - INTENT: FAST (Haiku/GPT-4o-mini) — cheap, quick parsing
    - RETRIEVAL: NONE — structured search, no LLM
    - SYNTHESIS: CAPABLE (Sonnet/GPT-4o) — nuanced response
    - EXPLANATION: BEST (Opus/o1) — deep reasoning
    """

    def __init__(
        self,
        intent_model: str = "claude-haiku",
        synthesis_model: str = "claude-sonnet",
        explanation_model: str = "claude-opus",
        fallback_provider: str = "anthropic"
    ):
        self.intent_model = MODEL_REGISTRY.get(intent_model)
        self.synthesis_model = MODEL_REGISTRY.get(synthesis_model)
        self.explanation_model = MODEL_REGISTRY.get(explanation_model)
        self.fallback_provider = fallback_provider

        # Initialize providers
        self.providers: Dict[str, LLMProvider] = {
            "anthropic": AnthropicProvider(),
            "openai": OpenAIProvider(),
            "google": GoogleProvider(),
        }

        # Track usage
        self.total_cost = 0.0
        self.call_count = 0

    def _get_provider(self, config: ModelConfig) -> LLMProvider:
        """Get the appropriate provider for a model config."""
        return self.providers.get(
            config.provider,
            self.providers[self.fallback_provider]
        )

    def _calculate_cost(
        self,
        config: ModelConfig,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Calculate cost for a completion."""
        input_cost = (input_tokens / 1000) * config.cost_per_1k_input
        output_cost = (output_tokens / 1000) * config.cost_per_1k_output
        return input_cost + output_cost

    # =========================================================================
    # Phase 1: Intent Detection
    # =========================================================================

    def detect_intent(self, query: str) -> ParsedQuery:
        """
        Parse natural language query into structured form.
        Uses FAST tier model for cost efficiency.
        """
        prompt = f"""Analyze this research query and extract structured information.

Query: "{query}"

Respond with JSON containing:
{{
    "query_type": one of [WHAT, WHY, COMPARE, GAPS, CONTRADICT, CONTINGENT, HOW_CONFIDENT, RELATED, TRENDING, CANONICAL],
    "causal_level": one of [associational, interventional, counterfactual],
    "entities": list of key entities mentioned,
    "subject": main subject of the query,
    "object": target/outcome if applicable,
    "scope_hints": any scope conditions mentioned (population, setting, etc.),
    "confidence": your confidence in this parse (0-1)
}}

Query type definitions:
- WHAT: "What is X?", "What does Y show?"
- WHY: "Why does X happen?", mechanism questions
- COMPARE: "How does X compare to Y?"
- GAPS: "What don't we know about X?"
- CONTRADICT: "What contradicts X?"
- CONTINGENT: "When does X apply?", scope questions
- HOW_CONFIDENT: "How confident are we about X?"
- RELATED: "What's related to X?"
- TRENDING: "What's gaining/losing support?"
- CANONICAL: "What's the seminal work on X?"

Causal level (Pearl's ladder):
- associational: Observational, correlational questions
- interventional: "What would happen if we do X?"
- counterfactual: "What would have happened if we had done X?"

Respond with valid JSON only."""

        system = """You are a research query parser for an evidence synthesis system.
Your job is to accurately classify queries and extract key entities.
Be precise about causal levels - most queries are associational unless they
explicitly ask about interventions or counterfactuals."""

        provider = self._get_provider(self.intent_model)
        response, in_tokens, out_tokens = provider.complete(
            prompt, self.intent_model, system
        )

        cost = self._calculate_cost(self.intent_model, in_tokens, out_tokens)
        self.total_cost += cost
        self.call_count += 1

        # Parse response
        try:
            data = json.loads(response)
            return ParsedQuery(
                original=query,
                query_type=QueryType[data.get("query_type", "WHAT")],
                causal_level=CausalLevel[data.get("causal_level", "associational").upper()],
                entities=data.get("entities", []),
                subject=data.get("subject"),
                object=data.get("object"),
                scope_hints=data.get("scope_hints", {}),
                confidence=data.get("confidence", 0.5)
            )
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse intent response: {e}")
            return ParsedQuery(
                original=query,
                query_type=QueryType.WHAT,
                causal_level=CausalLevel.ASSOCIATIONAL,
                confidence=0.0
            )

    # =========================================================================
    # Phase 2: Retrieval (No LLM)
    # =========================================================================

    def retrieve_evidence(
        self,
        parsed: ParsedQuery,
        web_of_belief: Any,
        max_results: int = 10
    ) -> List[EvidenceItem]:
        """
        Retrieve relevant evidence from the web of belief.
        NO LLM USED — structured search only.

        Dispatches to specialized retrieval for Bates patterns:
        - RELATED: Serendipitous discovery via constraint network
        - TRENDING: Temporal patterns (recent papers, credence changes)
        - CANONICAL: Foundational/entrenched beliefs

        Standard search strategy:
        1. Match entities against belief content (case-insensitive)
        2. Match subject/object against environment_id/outcome_id
        3. Filter by scope hints if provided
        4. Sort by credence (highest first)
        5. Limit to max_results
        """
        evidence = []

        if web_of_belief is None:
            return evidence

        # Dispatch to specialized Bates pattern retrieval
        if parsed.query_type == QueryType.RELATED:
            return self._retrieve_related(parsed, web_of_belief, max_results)
        elif parsed.query_type == QueryType.TRENDING:
            return self._retrieve_trending(parsed, web_of_belief, max_results)
        elif parsed.query_type == QueryType.CANONICAL:
            return self._retrieve_canonical(parsed, web_of_belief, max_results)

        # Standard retrieval for other query types
        # Get all beliefs from web
        try:
            beliefs = list(web_of_belief.beliefs.values())
        except AttributeError:
            # Handle snapshot or other WebOfBelief variants
            try:
                beliefs = list(web_of_belief.beliefs.values())
            except Exception:
                return evidence

        # Normalize search terms
        search_terms = [e.lower() for e in parsed.entities]
        if parsed.subject:
            search_terms.append(parsed.subject.lower())
        if parsed.object:
            search_terms.append(parsed.object.lower())

        # Score and filter beliefs
        scored_beliefs = []
        for belief in beliefs:
            score = self._score_belief_relevance(belief, search_terms, parsed)
            if score > 0:
                scored_beliefs.append((score, belief))

        # Sort by score (descending), then by credence
        scored_beliefs.sort(key=lambda x: (x[0], x[1].credence.point), reverse=True)

        # Convert to EvidenceItem
        for _, belief in scored_beliefs[:max_results]:
            evidence.append(EvidenceItem(
                belief_id=belief.belief_id,
                content=belief.content,
                credence=belief.credence.point,
                status=belief.status.value if hasattr(belief.status, 'value') else str(belief.status),
                level=belief.level.value if hasattr(belief.level, 'value') else str(belief.level),
                sources=belief.paper_ids[:5] if belief.paper_ids else [],
                scope_conditions=self._extract_scope_dict(belief.scope) if belief.scope else None
            ))

        return evidence

    def _score_belief_relevance(
        self,
        belief: Any,
        search_terms: List[str],
        parsed: ParsedQuery
    ) -> float:
        """
        Score belief relevance to query.
        Returns 0 if not relevant, positive score if relevant.
        """
        score = 0.0
        content_lower = belief.content.lower()

        # Term matching in content
        for term in search_terms:
            if term in content_lower:
                score += 1.0

        # Exact match bonuses for environment_id/outcome_id
        if parsed.subject and hasattr(belief, 'environment_id') and belief.environment_id:
            if parsed.subject.lower() in belief.environment_id.lower():
                score += 2.0

        if parsed.object and hasattr(belief, 'outcome_id') and belief.outcome_id:
            if parsed.object.lower() in belief.outcome_id.lower():
                score += 2.0

        # Scope hint matching
        if parsed.scope_hints and hasattr(belief, 'scope') and belief.scope:
            for hint_key, hint_val in parsed.scope_hints.items():
                hint_val_lower = hint_val.lower()
                if hasattr(belief.scope, 'population') and belief.scope.population:
                    if hint_val_lower in belief.scope.population.lower():
                        score += 0.5
                if hasattr(belief.scope, 'setting') and belief.scope.setting:
                    if hint_val_lower in belief.scope.setting.lower():
                        score += 0.5

        # Boost established/entrenched beliefs
        if hasattr(belief, 'status'):
            status_val = belief.status.value if hasattr(belief.status, 'value') else str(belief.status)
            if status_val == 'established':
                score *= 1.2
            elif status_val == 'entrenched':
                score *= 1.5

        return score

    def _extract_scope_dict(self, scope: Any) -> Dict[str, str]:
        """Extract scope conditions as a dictionary."""
        if scope is None:
            return {}
        result = {}
        for field in ['population', 'setting', 'methodology', 'duration', 'region']:
            if hasattr(scope, field):
                val = getattr(scope, field)
                if val:
                    result[field] = str(val)
        return result

    # =========================================================================
    # Bates Pattern Retrieval (RELATED, TRENDING, CANONICAL)
    # =========================================================================

    def _retrieve_related(
        self,
        parsed: ParsedQuery,
        web_of_belief: Any,
        max_results: int = 10
    ) -> List[EvidenceItem]:
        """
        Bates RELATED pattern: Serendipitous discovery.

        Finds beliefs connected via constraints to the queried topic
        but not directly matching the search terms. This enables
        "berrypicking" — finding unexpected but relevant connections.

        Strategy:
        1. Find directly matching beliefs
        2. Follow constraint edges to connected beliefs
        3. Filter out direct matches
        4. Prioritize beliefs with shared theories
        5. Return serendipitous discoveries
        """
        evidence = []

        try:
            beliefs = list(web_of_belief.beliefs.values())
        except (AttributeError, Exception):
            return evidence

        # Step 1: Find direct matches
        search_terms = [e.lower() for e in parsed.entities]
        if parsed.subject:
            search_terms.append(parsed.subject.lower())

        direct_match_ids = set()
        for belief in beliefs:
            content_lower = belief.content.lower()
            if any(term in content_lower for term in search_terms):
                direct_match_ids.add(belief.belief_id)

        # Step 2: Find connected beliefs via constraints
        connected_ids = set()
        try:
            constraints = web_of_belief.constraints
            for constraint in constraints:
                source_id = constraint.source_id if hasattr(constraint, 'source_id') else None
                target_id = constraint.target_id if hasattr(constraint, 'target_id') else None

                if source_id in direct_match_ids and target_id:
                    connected_ids.add(target_id)
                if target_id in direct_match_ids and source_id:
                    connected_ids.add(source_id)
        except (AttributeError, Exception):
            pass

        # Step 3: Find beliefs sharing theories with direct matches
        direct_theories = set()
        for belief in beliefs:
            if belief.belief_id in direct_match_ids:
                if hasattr(belief, 'theory_ids') and belief.theory_ids:
                    direct_theories.update(belief.theory_ids)

        for belief in beliefs:
            if belief.belief_id not in direct_match_ids:
                if hasattr(belief, 'theory_ids') and belief.theory_ids:
                    if direct_theories & set(belief.theory_ids):
                        connected_ids.add(belief.belief_id)

        # Step 4: Remove direct matches (we want serendipitous discoveries)
        serendipitous_ids = connected_ids - direct_match_ids

        # Step 5: Score and sort
        scored = []
        for belief in beliefs:
            if belief.belief_id in serendipitous_ids:
                # Score by credence and connectivity
                score = belief.credence.point
                # Bonus for established/entrenched
                status_val = belief.status.value if hasattr(belief.status, 'value') else ''
                if status_val == 'entrenched':
                    score *= 1.5
                elif status_val == 'established':
                    score *= 1.2
                scored.append((score, belief))

        scored.sort(key=lambda x: x[0], reverse=True)

        # Convert to EvidenceItem
        for _, belief in scored[:max_results]:
            evidence.append(EvidenceItem(
                belief_id=belief.belief_id,
                content=belief.content,
                credence=belief.credence.point,
                status=belief.status.value if hasattr(belief.status, 'value') else str(belief.status),
                level=belief.level.value if hasattr(belief.level, 'value') else str(belief.level),
                sources=belief.paper_ids[:5] if belief.paper_ids else [],
                scope_conditions=self._extract_scope_dict(belief.scope) if belief.scope else None
            ))

        return evidence

    def _retrieve_trending(
        self,
        parsed: ParsedQuery,
        web_of_belief: Any,
        max_results: int = 10
    ) -> List[EvidenceItem]:
        """
        Bates TRENDING pattern: Temporal patterns.

        Finds beliefs with recent evidence additions or changing credence.
        Useful for identifying emerging topics or shifting consensus.

        Strategy:
        1. Match relevant beliefs by entity/topic
        2. Score by recency (recent papers = higher score)
        3. Score by credence change if history available
        4. Prioritize beliefs with many recent additions
        """
        evidence = []

        try:
            beliefs = list(web_of_belief.beliefs.values())
        except (AttributeError, Exception):
            return evidence

        # Filter to relevant beliefs
        search_terms = [e.lower() for e in parsed.entities]
        if parsed.subject:
            search_terms.append(parsed.subject.lower())

        relevant_beliefs = []
        for belief in beliefs:
            content_lower = belief.content.lower()
            if any(term in content_lower for term in search_terms) or not search_terms:
                relevant_beliefs.append(belief)

        # Score by temporal factors
        scored = []
        current_year = 2026  # From environment

        for belief in relevant_beliefs:
            score = 0.0

            # Score by number of recent papers
            if hasattr(belief, 'paper_ids') and belief.paper_ids:
                n_papers = len(belief.paper_ids)
                score += min(n_papers * 0.5, 3.0)  # Cap at 3.0

            # Check for recent additions via metadata if available
            if hasattr(belief, 'metadata') and belief.metadata:
                if 'last_updated' in belief.metadata:
                    # Recent updates get bonus
                    score += 1.0
                if 'papers_by_year' in belief.metadata:
                    # Count recent papers
                    recent = sum(
                        count for year, count in belief.metadata['papers_by_year'].items()
                        if int(year) >= current_year - 2
                    )
                    score += recent * 0.5

            # Check credence history if available
            if hasattr(belief, 'credence') and hasattr(belief.credence, 'history'):
                history = belief.credence.history
                if len(history) >= 2:
                    # Credence change indicates activity
                    delta = abs(history[-1] - history[0])
                    score += delta * 2.0

            # Base score from credence
            score += belief.credence.point * 0.5

            if score > 0:
                scored.append((score, belief))

        # Sort by trending score
        scored.sort(key=lambda x: x[0], reverse=True)

        # Convert to EvidenceItem
        for _, belief in scored[:max_results]:
            evidence.append(EvidenceItem(
                belief_id=belief.belief_id,
                content=belief.content,
                credence=belief.credence.point,
                status=belief.status.value if hasattr(belief.status, 'value') else str(belief.status),
                level=belief.level.value if hasattr(belief.level, 'value') else str(belief.level),
                sources=belief.paper_ids[:5] if belief.paper_ids else [],
                scope_conditions=self._extract_scope_dict(belief.scope) if belief.scope else None
            ))

        return evidence

    def _retrieve_canonical(
        self,
        parsed: ParsedQuery,
        web_of_belief: Any,
        max_results: int = 10
    ) -> List[EvidenceItem]:
        """
        Bates CANONICAL pattern: Entry points / foundational works.

        Finds entrenched, highly-connected beliefs that serve as
        entry points to a topic. These are the "seminal" findings.

        Strategy:
        1. Match relevant beliefs by entity/topic
        2. Prioritize ENTRENCHED and ESTABLISHED status
        3. Score by connectivity (constraint count)
        4. Score by centrality/entrenchment score if available
        5. Prefer THEORETICAL level for foundational concepts
        """
        evidence = []

        try:
            beliefs = list(web_of_belief.beliefs.values())
        except (AttributeError, Exception):
            return evidence

        # Filter to relevant beliefs
        search_terms = [e.lower() for e in parsed.entities]
        if parsed.subject:
            search_terms.append(parsed.subject.lower())

        relevant_beliefs = []
        for belief in beliefs:
            content_lower = belief.content.lower()
            if any(term in content_lower for term in search_terms) or not search_terms:
                relevant_beliefs.append(belief)

        # Count constraints per belief for connectivity score
        constraint_counts = {}
        try:
            for constraint in web_of_belief.constraints:
                source_id = constraint.source_id if hasattr(constraint, 'source_id') else None
                target_id = constraint.target_id if hasattr(constraint, 'target_id') else None
                if source_id:
                    constraint_counts[source_id] = constraint_counts.get(source_id, 0) + 1
                if target_id:
                    constraint_counts[target_id] = constraint_counts.get(target_id, 0) + 1
        except (AttributeError, Exception):
            pass

        # Score by canonical factors
        scored = []
        for belief in relevant_beliefs:
            score = 0.0

            # Status strongly affects canonical score
            status_val = belief.status.value if hasattr(belief.status, 'value') else ''
            if status_val == 'entrenched':
                score += 5.0
            elif status_val == 'established':
                score += 3.0
            elif status_val == 'tentative':
                score += 1.0

            # Epistemic level affects canonical score
            level_val = belief.level.value if hasattr(belief.level, 'value') else ''
            if level_val == 'theoretical':
                score += 2.0  # Theories are foundational
            elif level_val == 'intermediate':
                score += 1.0

            # Connectivity score
            connectivity = constraint_counts.get(belief.belief_id, 0)
            score += min(connectivity * 0.5, 3.0)  # Cap at 3.0

            # Entrenchment score if available
            if hasattr(web_of_belief, 'get_entrenchment'):
                try:
                    entrenchment = web_of_belief.get_entrenchment(belief.belief_id)
                    score += entrenchment * 3.0
                except Exception as e:
                    logger.debug(f"Non-critical: {e}")

            # High credence contributes
            score += belief.credence.point * 2.0

            if score > 0:
                scored.append((score, belief))

        # Sort by canonical score
        scored.sort(key=lambda x: x[0], reverse=True)

        # Convert to EvidenceItem
        for _, belief in scored[:max_results]:
            evidence.append(EvidenceItem(
                belief_id=belief.belief_id,
                content=belief.content,
                credence=belief.credence.point,
                status=belief.status.value if hasattr(belief.status, 'value') else str(belief.status),
                level=belief.level.value if hasattr(belief.level, 'value') else str(belief.level),
                sources=belief.paper_ids[:5] if belief.paper_ids else [],
                scope_conditions=self._extract_scope_dict(belief.scope) if belief.scope else None
            ))

        return evidence

    # =========================================================================
    # Phase 3: Response Synthesis
    # =========================================================================

    def synthesize_response(
        self,
        parsed: ParsedQuery,
        evidence: List[EvidenceItem],
        mode: str = "standard",
        user_type: Optional[str] = None
    ) -> QueryResponse:
        """
        Synthesize a response from parsed query and retrieved evidence.
        Uses CAPABLE tier model for nuanced synthesis.

        Dispatches to specialized synthesis for Bates patterns:
        - RELATED: Serendipitous connections format
        - TRENDING: Temporal patterns format
        - CANONICAL: Foundational works format
        """
        start_time = time.time()

        # If no evidence, return simple response
        if not evidence:
            return self._no_evidence_response(parsed)

        # Build evidence context
        evidence_context = self._format_evidence_context(evidence)

        # Dispatch to Bates-specific synthesis
        if parsed.query_type == QueryType.RELATED:
            return self._synthesize_related(parsed, evidence, evidence_context)
        elif parsed.query_type == QueryType.TRENDING:
            return self._synthesize_trending(parsed, evidence, evidence_context)
        elif parsed.query_type == QueryType.CANONICAL:
            return self._synthesize_canonical(parsed, evidence, evidence_context)

        # Standard query type synthesis
        # Determine response depth
        if mode == "quick":
            return self._quick_synthesis(parsed, evidence)
        elif mode == "deep":
            return self._deep_synthesis(parsed, evidence, evidence_context)
        else:
            return self._standard_synthesis(parsed, evidence, evidence_context, user_type)

    def _format_evidence_context(self, evidence: List[EvidenceItem]) -> str:
        """Format evidence for LLM context."""
        lines = []
        for i, ev in enumerate(evidence, 1):
            lines.append(f"{i}. [{ev.status}] {ev.content}")
            lines.append(f"   Credence: {ev.credence:.2f}, Level: {ev.level}")
            if ev.sources:
                lines.append(f"   Sources: {', '.join(ev.sources[:3])}")
        return "\n".join(lines)

    def _quick_synthesis(
        self,
        parsed: ParsedQuery,
        evidence: List[EvidenceItem]
    ) -> QueryResponse:
        """Quick mode: headline only, minimal LLM use."""
        # Try to generate headline from evidence without LLM
        if evidence:
            top = evidence[0]
            headline = f"{top.content} (credence: {top.credence:.2f})"
        else:
            headline = "No strong evidence found for this query."

        return QueryResponse(
            query=parsed.original,
            query_type=parsed.query_type.value,
            causal_level=parsed.causal_level.value,
            headline=headline,
            models_used={"synthesis": "none"},
            cost_estimate=0.0,
            processing_time_ms=int((time.time() - time.time()) * 1000)
        )

    def _standard_synthesis(
        self,
        parsed: ParsedQuery,
        evidence: List[EvidenceItem],
        evidence_context: str,
        user_type: Optional[str] = None
    ) -> QueryResponse:
        """Standard mode: headline + summary + practical implications."""
        start_time = time.time()

        # Customize for user type
        user_context = ""
        if user_type == "practitioner":
            user_context = "Focus on practical design implications and actionable recommendations."
        elif user_type == "senior_researcher":
            user_context = "Emphasize methodological details and research gaps."
        elif user_type == "graduate_student":
            user_context = "Provide educational context and explain key concepts."

        prompt = f"""Generate a research synthesis for this query.

Query: "{parsed.original}"
Query Type: {parsed.query_type.value}
Causal Level: {parsed.causal_level.value}

Evidence retrieved:
{evidence_context}

{user_context}

Respond with JSON:
{{
    "headline": "One-sentence answer with credence if applicable",
    "summary": {{
        "finding": "2-3 sentence summary of the main finding",
        "confidence": "low/moderate/high",
        "key_evidence": ["list of 2-4 key sources"]
    }},
    "scope_conditions": {{
        "population": "who this applies to",
        "setting": "where this applies",
        "methodology": "how evidence was gathered",
        "limitations": "where this may not generalize"
    }},
    "practical_implications": ["actionable point 1", "actionable point 2", "actionable point 3"],
    "caveats": ["caveat 1", "caveat 2"]
}}

IMPORTANT:
- Ground all claims in the provided evidence
- Include credence values where known
- Be explicit about scope conditions
- Note any contradicting evidence

Respond with valid JSON only."""

        system = """You are a research synthesis assistant for Article Eater V23.
Your role is to synthesize evidence into clear, actionable summaries.
Always cite sources. Never hallucinate facts not in the evidence.
Be appropriately uncertain when evidence is limited."""

        provider = self._get_provider(self.synthesis_model)
        response, in_tokens, out_tokens = provider.complete(
            prompt, self.synthesis_model, system
        )

        cost = self._calculate_cost(self.synthesis_model, in_tokens, out_tokens)
        self.total_cost += cost
        self.call_count += 1

        # Parse response
        try:
            data = json.loads(response)
            return QueryResponse(
                query=parsed.original,
                query_type=parsed.query_type.value,
                causal_level=parsed.causal_level.value,
                headline=data.get("headline", ""),
                summary=data.get("summary"),
                scope_conditions=data.get("scope_conditions"),
                practical_implications=data.get("practical_implications"),
                caveats=data.get("caveats"),
                key_sources=data.get("summary", {}).get("key_evidence"),
                models_used={
                    "intent": self.intent_model.model_id,
                    "synthesis": self.synthesis_model.model_id
                },
                cost_estimate=cost,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse synthesis response: {e}")
            return self._no_evidence_response(parsed)

    def _deep_synthesis(
        self,
        parsed: ParsedQuery,
        evidence: List[EvidenceItem],
        evidence_context: str
    ) -> QueryResponse:
        """
        Deep mode: full trace with detailed explanation.
        Uses BEST tier model (Opus/o1) for complex reasoning.
        """
        start_time = time.time()

        prompt = f"""Provide a comprehensive research synthesis with deep analysis.

Query: "{parsed.original}"
Query Type: {parsed.query_type.value}
Causal Level: {parsed.causal_level.value}

Evidence retrieved:
{evidence_context}

Respond with JSON containing:
{{
    "headline": "One-sentence definitive answer",
    "summary": {{
        "finding": "Detailed summary (3-5 sentences)",
        "confidence": "low/moderate/high with reasoning",
        "key_evidence": ["detailed source 1", "detailed source 2", "..."],
        "evidence_quality": "assessment of the evidence base"
    }},
    "detail": {{
        "mechanism": "How/why this works (causal pathway if known)",
        "theoretical_basis": "Which theories support this finding",
        "methodological_notes": "How the evidence was gathered",
        "effect_sizes": "Quantitative estimates if available",
        "boundary_conditions": "When this does/doesn't apply"
    }},
    "scope_conditions": {{
        "population": "Who this applies to (with specificity)",
        "setting": "Environmental conditions required",
        "methodology": "Best methods to observe this effect",
        "limitations": "Where this definitely does NOT generalize",
        "temporal": "Duration and timing considerations"
    }},
    "practical_implications": [
        "Specific actionable recommendation 1",
        "Specific actionable recommendation 2",
        "Specific actionable recommendation 3",
        "Implementation consideration"
    ],
    "caveats": [
        "Important limitation 1",
        "Important limitation 2",
        "What we don't know yet"
    ],
    "further_reading": [
        "Recommended paper/source 1",
        "Recommended paper/source 2"
    ],
    "research_gaps": [
        "Gap 1 worth investigating",
        "Gap 2 worth investigating"
    ]
}}

CRITICAL REQUIREMENTS:
- Ground ALL claims in the provided evidence
- Be explicit about uncertainty and confidence levels
- Distinguish correlation from causation
- Note any contradicting evidence
- Provide specific, actionable insights where possible
- If evidence is limited, say so clearly

Respond with valid JSON only."""

        system = """You are an expert research synthesis assistant for Article Eater V23.
Your role is to provide deep, nuanced analysis of scientific evidence.
You have expertise in:
- Causal inference and identifying mechanism pathways
- Assessing evidence quality and methodological rigor
- Identifying scope conditions and generalizability limits
- Translating research findings into practical implications

Be rigorous but accessible. Never hallucinate - only cite evidence provided."""

        provider = self._get_provider(self.explanation_model)
        response, in_tokens, out_tokens = provider.complete(
            prompt, self.explanation_model, system
        )

        cost = self._calculate_cost(self.explanation_model, in_tokens, out_tokens)
        self.total_cost += cost
        self.call_count += 1

        # Parse response
        try:
            data = json.loads(response)
            return QueryResponse(
                query=parsed.original,
                query_type=parsed.query_type.value,
                causal_level=parsed.causal_level.value,
                headline=data.get("headline", ""),
                summary=data.get("summary"),
                detail=data.get("detail"),
                scope_conditions=data.get("scope_conditions"),
                practical_implications=data.get("practical_implications"),
                caveats=data.get("caveats"),
                key_sources=data.get("further_reading"),
                models_used={
                    "intent": self.intent_model.model_id,
                    "synthesis": self.explanation_model.model_id  # BEST tier
                },
                cost_estimate=cost,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse deep synthesis response: {e}")
            # Fallback to standard synthesis
            return self._standard_synthesis(parsed, evidence, evidence_context)

    # =========================================================================
    # Bates Pattern Synthesis (RELATED, TRENDING, CANONICAL)
    # =========================================================================

    def _synthesize_related(
        self,
        parsed: ParsedQuery,
        evidence: List[EvidenceItem],
        evidence_context: str
    ) -> QueryResponse:
        """
        Bates RELATED synthesis: Serendipitous discovery format.

        Emphasizes unexpected connections and exploration paths.
        """
        start_time = time.time()

        prompt = f"""You are helping with serendipitous discovery - finding unexpected but valuable connections.

The user asked about topics related to: "{parsed.original}"

These beliefs are connected to the query topic but weren't direct matches.
They represent potential exploration paths and unexpected connections:

{evidence_context}

Respond with JSON:
{{
    "headline": "Summary of the related topics discovered",
    "summary": {{
        "finding": "Overview of what related areas were found",
        "connection_type": "How these relate to the original topic",
        "key_evidence": ["list of most interesting connections"]
    }},
    "exploration_paths": [
        {{
            "topic": "Related topic name",
            "relevance": "Why this might be interesting",
            "suggested_queries": ["follow-up query 1", "follow-up query 2"]
        }}
    ],
    "serendipitous_insights": [
        "Unexpected connection 1",
        "Unexpected connection 2"
    ],
    "caveats": ["caveat about indirect connections"]
}}

Focus on helping the user discover valuable unexpected connections.
Respond with valid JSON only."""

        system = """You are a research discovery assistant specializing in finding
unexpected but valuable connections between topics. Help users explore beyond
their initial query to find serendipitous insights."""

        provider = self._get_provider(self.synthesis_model)
        response, in_tokens, out_tokens = provider.complete(
            prompt, self.synthesis_model, system
        )

        cost = self._calculate_cost(self.synthesis_model, in_tokens, out_tokens)
        self.total_cost += cost
        self.call_count += 1

        try:
            data = json.loads(response)
            return QueryResponse(
                query=parsed.original,
                query_type=parsed.query_type.value,
                causal_level=parsed.causal_level.value,
                headline=data.get("headline", ""),
                summary=data.get("summary"),
                detail={"exploration_paths": data.get("exploration_paths", [])},
                practical_implications=data.get("serendipitous_insights"),
                caveats=data.get("caveats"),
                models_used={
                    "intent": self.intent_model.model_id,
                    "synthesis": self.synthesis_model.model_id
                },
                cost_estimate=cost,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse related synthesis: {e}")
            return self._standard_synthesis(parsed, evidence, evidence_context, None)

    def _synthesize_trending(
        self,
        parsed: ParsedQuery,
        evidence: List[EvidenceItem],
        evidence_context: str
    ) -> QueryResponse:
        """
        Bates TRENDING synthesis: Temporal patterns format.

        Emphasizes what's gaining support, losing support, or actively debated.
        """
        start_time = time.time()

        prompt = f"""You are analyzing temporal trends in research evidence.

The user wants to know what's trending for: "{parsed.original}"

These beliefs show recent activity or changing credence:

{evidence_context}

Respond with JSON:
{{
    "headline": "Summary of what's trending in this area",
    "summary": {{
        "finding": "Overview of temporal patterns",
        "confidence": "low/moderate/high",
        "key_evidence": ["sources showing trends"]
    }},
    "trending_up": [
        {{
            "topic": "Topic gaining support",
            "evidence": "What's driving this",
            "significance": "Why this matters"
        }}
    ],
    "trending_down": [
        {{
            "topic": "Topic losing support (if any)",
            "evidence": "What's driving this",
            "significance": "Why this matters"
        }}
    ],
    "emerging_debates": [
        "Active debate 1",
        "Active debate 2"
    ],
    "caveats": ["caveat about temporal analysis"]
}}

Focus on helping the user understand what's changing in this research area.
Respond with valid JSON only."""

        system = """You are a research trends analyst. Help users understand
what's gaining or losing support in a research area, and what debates
are currently active. Be specific about evidence for trends."""

        provider = self._get_provider(self.synthesis_model)
        response, in_tokens, out_tokens = provider.complete(
            prompt, self.synthesis_model, system
        )

        cost = self._calculate_cost(self.synthesis_model, in_tokens, out_tokens)
        self.total_cost += cost
        self.call_count += 1

        try:
            data = json.loads(response)
            return QueryResponse(
                query=parsed.original,
                query_type=parsed.query_type.value,
                causal_level=parsed.causal_level.value,
                headline=data.get("headline", ""),
                summary=data.get("summary"),
                detail={
                    "trending_up": data.get("trending_up", []),
                    "trending_down": data.get("trending_down", []),
                    "emerging_debates": data.get("emerging_debates", [])
                },
                caveats=data.get("caveats"),
                models_used={
                    "intent": self.intent_model.model_id,
                    "synthesis": self.synthesis_model.model_id
                },
                cost_estimate=cost,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse trending synthesis: {e}")
            return self._standard_synthesis(parsed, evidence, evidence_context, None)

    def _synthesize_canonical(
        self,
        parsed: ParsedQuery,
        evidence: List[EvidenceItem],
        evidence_context: str
    ) -> QueryResponse:
        """
        Bates CANONICAL synthesis: Foundational works format.

        Emphasizes seminal papers, foundational theories, and entry points.
        """
        start_time = time.time()

        prompt = f"""You are helping identify foundational works and entry points for a topic.

The user wants canonical/seminal works for: "{parsed.original}"

These are the most entrenched, foundational beliefs in this area:

{evidence_context}

Respond with JSON:
{{
    "headline": "Summary of foundational works in this area",
    "summary": {{
        "finding": "Overview of the canonical knowledge",
        "confidence": "high (these are established)",
        "key_evidence": ["foundational sources"]
    }},
    "foundational_works": [
        {{
            "title": "Seminal work or theory",
            "significance": "Why this is foundational",
            "key_contribution": "What it established",
            "citation_info": "Source if available"
        }}
    ],
    "core_theories": [
        {{
            "theory": "Theory name",
            "description": "Brief description",
            "status": "How well established"
        }}
    ],
    "entry_points": [
        "Recommended starting point 1",
        "Recommended starting point 2"
    ],
    "reading_order": [
        "Read this first",
        "Then read this",
        "Then explore these"
    ],
    "caveats": ["caveats about canonical status"]
}}

Help the user understand where to start learning about this topic.
Respond with valid JSON only."""

        system = """You are a research guide specializing in identifying
foundational, seminal works. Help users find the canonical entry points
to a topic - the works everyone in the field knows and builds upon."""

        provider = self._get_provider(self.synthesis_model)
        response, in_tokens, out_tokens = provider.complete(
            prompt, self.synthesis_model, system
        )

        cost = self._calculate_cost(self.synthesis_model, in_tokens, out_tokens)
        self.total_cost += cost
        self.call_count += 1

        try:
            data = json.loads(response)
            return QueryResponse(
                query=parsed.original,
                query_type=parsed.query_type.value,
                causal_level=parsed.causal_level.value,
                headline=data.get("headline", ""),
                summary=data.get("summary"),
                detail={
                    "foundational_works": data.get("foundational_works", []),
                    "core_theories": data.get("core_theories", []),
                    "reading_order": data.get("reading_order", [])
                },
                practical_implications=data.get("entry_points"),
                caveats=data.get("caveats"),
                key_sources=[w.get("title") for w in data.get("foundational_works", [])
                            if isinstance(w, dict) and w.get("title")],
                models_used={
                    "intent": self.intent_model.model_id,
                    "synthesis": self.synthesis_model.model_id
                },
                cost_estimate=cost,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse canonical synthesis: {e}")
            return self._standard_synthesis(parsed, evidence, evidence_context, None)

    def _no_evidence_response(self, parsed: ParsedQuery) -> QueryResponse:
        """Return response when no evidence found."""
        return QueryResponse(
            query=parsed.original,
            query_type=parsed.query_type.value,
            causal_level=parsed.causal_level.value,
            headline="No evidence found for this query.",
            caveats=["The evidence base may not cover this topic yet."],
            models_used={},
            cost_estimate=0.0,
            processing_time_ms=0
        )

    # =========================================================================
    # Full Pipeline
    # =========================================================================

    def process_query(
        self,
        query: str,
        web_of_belief: Any = None,
        mode: str = "standard",
        user_type: Optional[str] = None,
        max_evidence: int = 10
    ) -> QueryResponse:
        """
        Process a complete query through all phases.

        Pipeline:
        1. Intent Detection (FAST model)
        2. Evidence Retrieval (no LLM)
        3. Response Synthesis (CAPABLE model)
        4. Deep Explanation if requested (BEST model)
        """
        start_time = time.time()

        # Phase 1: Intent
        parsed = self.detect_intent(query)
        logger.info(f"Query parsed: type={parsed.query_type}, causal={parsed.causal_level}")

        # Phase 2: Retrieval
        evidence = self.retrieve_evidence(parsed, web_of_belief, max_evidence)
        logger.info(f"Retrieved {len(evidence)} evidence items")

        # Phase 3: Synthesis
        response = self.synthesize_response(parsed, evidence, mode, user_type)

        # Add total processing time
        response.processing_time_ms = int((time.time() - start_time) * 1000)

        return response

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics for the orchestrator."""
        return {
            "total_cost": self.total_cost,
            "call_count": self.call_count,
            "average_cost_per_call": self.total_cost / self.call_count if self.call_count > 0 else 0
        }


# Convenience function for module-level access
_orchestrator: Optional[MultiAIOrchestrator] = None


def get_orchestrator(**kwargs) -> MultiAIOrchestrator:
    """Get or create the multi-AI orchestrator singleton."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MultiAIOrchestrator(**kwargs)
    return _orchestrator


def process_query(
    query: str,
    mode: str = "standard",
    user_type: Optional[str] = None
) -> QueryResponse:
    """Convenience function to process a query."""
    return get_orchestrator().process_query(query, mode=mode, user_type=user_type)
