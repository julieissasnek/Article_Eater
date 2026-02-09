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
from dataclasses import dataclass, field, asdict
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
        """
        evidence = []

        # This would integrate with the actual WebOfBelief
        # For now, return placeholder
        # In production: use parsed.entities to search beliefs

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
        """
        start_time = time.time()

        # If no evidence, return simple response
        if not evidence:
            return self._no_evidence_response(parsed)

        # Build evidence context
        evidence_context = self._format_evidence_context(evidence)

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
        """Deep mode: full trace with detailed explanation."""
        # Would use BEST tier model for deep reasoning
        # For now, delegate to standard with extra context
        return self._standard_synthesis(parsed, evidence, evidence_context)

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
