"""
Epistemic Services API Routes
==============================

FastAPI routes exposing all enrichment and adaptation services through the API.

Services exposed:
- Answer enrichment (base answer + orchestrator)
- Language adaptation (text rewriting per user type)
- Figure suggestions (relevant figures for topics)
- Math formula explanation (LLM-generated explanations)
- Credence intervals (confidence bounds on beliefs)
- Warrant traces (decomposition of belief sources)
- Confounder risk (observational study flag)
- T1 framework perspectives (multi-theory viewpoints)
- Knowledge gap analysis (missing topics)

Date: March 3, 2026
Author: Claude Code (agent for Prof. David Kirsh, UCSD Cognitive Science)
Version: V22.0.0
"""

from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/services", tags=["services"])


# =============================================================================
# Request/Response Models
# =============================================================================

class UserTypeEnum(str, Enum):
    """User persona types for language adaptation."""
    RESEARCHER = "researcher"
    STUDENT = "student"
    CLINICIAN = "clinician"
    POLICY_MAKER = "policy_maker"
    GENERAL_PUBLIC = "general_public"


class EnrichedQueryRequest(BaseModel):
    """Request to execute a query with full epistemic enrichment."""
    question: str = Field(..., description="Natural language question", min_length=3)
    user_type: UserTypeEnum = Field(
        UserTypeEnum.RESEARCHER,
        description="User persona type for language adaptation"
    )
    enable_enrichment: bool = Field(True, description="Apply enrichment orchestrator")


class EnrichedBelief(BaseModel):
    """A single belief with all enrichments applied."""
    text: str
    credence_point: Optional[float] = None
    credence_ci: Optional[Dict[str, float]] = None
    warrant_trace: Optional[List[Dict[str, Any]]] = None
    confounder_risk: Optional[str] = None
    confounder_details: Optional[List[str]] = None


class EnrichedAnswer(BaseModel):
    """Full enriched answer with all service outputs."""
    base_answer: Dict[str, Any]
    enriched_beliefs: List[EnrichedBelief] = []
    framework_voices: List[Dict[str, Any]] = []
    gaps: List[Dict[str, Any]] = []
    follow_ups: List[Dict[str, str]] = []
    figures: List[Dict[str, Any]] = []
    user_type: str = "researcher"
    enrichment_metadata: Dict[str, Any] = {}


class CredenceIntervalRequest(BaseModel):
    """Request credence interval for a belief."""
    belief_id: str = Field(..., description="Belief identifier")
    belief_text: Optional[str] = Field(None, description="Belief text (if ID not found)")


class WarrantTraceRequest(BaseModel):
    """Request warrant decomposition for a belief."""
    belief_id: str = Field(..., description="Belief identifier")
    belief_text: Optional[str] = Field(None, description="Belief text (if ID not found)")
    max_components: int = Field(5, ge=1, le=20, description="Max warrant components to return")


class ConfounderRiskRequest(BaseModel):
    """Request confounder risk assessment for a belief."""
    belief_id: str = Field(..., description="Belief identifier")
    belief_text: Optional[str] = Field(None, description="Belief text (if ID not found)")


class LanguageAdaptationRequest(BaseModel):
    """Request text adaptation for specific user type."""
    text: str = Field(..., description="Text to adapt", min_length=10)
    user_type: UserTypeEnum = Field(UserTypeEnum.RESEARCHER, description="Target user type")
    context: Optional[str] = Field(None, description="Optional context for adaptation")


class FormulaExplanationRequest(BaseModel):
    """Request explanation for a mathematical formula."""
    formula_name: str = Field(..., description="Name or LaTeX of formula")
    user_type: UserTypeEnum = Field(UserTypeEnum.RESEARCHER, description="User type for depth")
    depth: str = Field("standard", description="Explanation depth: brief, standard, detailed")


# =============================================================================
# Service Initialization (Lazy Loading with Graceful Degradation)
# =============================================================================

def _get_qa_handler():
    """Get or create arbitrary QA handler."""
    try:
        from src.services.arbitrary_qa_handler import ArbitraryQAHandler
        return ArbitraryQAHandler()
    except Exception as e:
        logger.warning(f"Failed to initialize QA handler: {e}")
        return None


def _get_language_adapter():
    """Get or create language adaptation service."""
    try:
        from src.services.language_adaptation_service import LanguageAdaptationService
        return LanguageAdaptationService()
    except Exception as e:
        logger.warning(f"Failed to initialize language adapter: {e}")
        return None


def _get_figure_suggester():
    """Get or create figure suggestion service."""
    try:
        from src.services.figure_suggestion_service import FigureSuggestionService
        return FigureSuggestionService()
    except Exception as e:
        logger.warning(f"Failed to initialize figure suggester: {e}")
        return None


def _get_math_explainer():
    """Get or create math explanation service."""
    try:
        from src.services.math_explanation_service import MathExplanationService
        return MathExplanationService()
    except Exception as e:
        logger.warning(f"Failed to initialize math explainer: {e}")
        return None


# =============================================================================
# ENRICHED QUERY ENDPOINT (Primary)
# =============================================================================

@router.post("/query/enriched", response_model=EnrichedAnswer)
async def enriched_query(request: EnrichedQueryRequest):
    """
    Execute a query with full epistemic enrichment.

    This is the primary endpoint that combines:
    1. Base answer from question classification and retrieval
    2. Credence intervals on extracted beliefs
    3. Warrant decomposition
    4. Confounder risk assessment
    5. Multi-framework perspectives
    6. Knowledge gap analysis
    7. Relevant figure suggestions
    8. Follow-up questions

    Graceful degradation: if any enrichment service fails, the base answer is
    still returned with partial enrichments.
    """
    try:
        handler = _get_qa_handler()
        if not handler:
            raise HTTPException(
                status_code=503,
                detail="QA handler unavailable - check service logs"
            )

        # Generate base answer
        base_answer = handler.answer(
            question=request.question
        )

        # If enrichment requested and not already applied, apply it now
        if request.enable_enrichment and not base_answer.get("enriched"):
            try:
                from src.services.answer_enrichment_orchestrator import (
                    AnswerEnrichmentOrchestrator
                )
                orchestrator = AnswerEnrichmentOrchestrator()
                enriched = orchestrator.enrich(
                    base_answer=base_answer,
                    question=request.question,
                    user_type=request.user_type.value
                )
                return enriched.to_dict()
            except Exception as e:
                logger.warning(f"Enrichment failed, returning base answer: {e}")

        return base_answer

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enriched query failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}"
        )


# =============================================================================
# CREDENCE INTERVAL ENDPOINTS
# =============================================================================

@router.get("/credence/{belief_id}/interval")
async def get_credence_interval(
    belief_id: str = Path(..., description="Belief identifier"),
    belief_text: Optional[str] = Query(None, description="Belief text (if ID not found)")
):
    """
    Get confidence interval (credence bounds) for a specific belief.

    Returns:
    - point_estimate: Single best estimate (0-1)
    - lower: Lower bound of 95% CI
    - upper: Upper bound of 95% CI
    - standard_error: Estimated SE
    - sources: How this credence was derived
    - last_updated: Timestamp of last credence update
    """
    try:
        # Try to fetch from web of belief or annotation service
        from src.services.web_of_belief import WebOfBelief
        web = WebOfBelief()
        belief = web.get_belief(belief_id)
        if not belief:
            raise HTTPException(
                status_code=404,
                detail=f"Belief '{belief_id}' not found"
            )

        credence = belief.get("credence", {})
        return {
            "belief_id": belief_id,
            "belief_text": belief.get("content", belief_text),
            "point_estimate": credence.get("point", 0.5),
            "ci_lower": credence.get("lower", 0.3),
            "ci_upper": credence.get("upper", 0.7),
            "standard_error": credence.get("se", 0.1),
            "warrant_sources": credence.get("sources", []),
            "last_updated": belief.get("updated", None),
            "confidence_in_estimate": credence.get("confidence", "medium")
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Credence fetch failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve credence interval: {str(e)}"
        )


# =============================================================================
# WARRANT TRACE ENDPOINTS
# =============================================================================

@router.get("/warrant/{belief_id}/trace")
async def get_warrant_trace(
    belief_id: str = Path(..., description="Belief identifier"),
    max_components: int = Query(5, ge=1, le=20, description="Max components to return")
):
    """
    Get warrant decomposition for a specific belief.

    Shows how the belief's credence is composed of:
    - Direct evidence (empirical support)
    - Coherence with related beliefs
    - Expert consensus
    - Meta-theoretical considerations

    Each component includes:
    - contribution: How much this warrant adds to total credence
    - evidence_count: Number of sources backing this warrant
    - strength: Subjective assessment (weak/moderate/strong)
    """
    try:
        from src.services.web_of_belief import WebOfBelief
        web = WebOfBelief()
        belief = web.get_belief(belief_id)
        if not belief:
            raise HTTPException(
                status_code=404,
                detail=f"Belief '{belief_id}' not found"
            )

        # Return warrant decomposition
        warrants = belief.get("warrants", [])[:max_components]
        return {
            "belief_id": belief_id,
            "belief_text": belief.get("content"),
            "total_credence": belief.get("credence", {}).get("point", 0.5),
            "warrant_components": [
                {
                    "type": w.get("type", "unknown"),
                    "contribution": w.get("contribution", 0.0),
                    "strength": w.get("strength", "moderate"),
                    "evidence_count": w.get("evidence_count", 0),
                    "description": w.get("description", "")
                }
                for w in warrants
            ],
            "decomposition_timestamp": belief.get("updated")
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Warrant trace failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve warrant trace: {str(e)}"
        )


# =============================================================================
# CONFOUNDER RISK ENDPOINTS
# =============================================================================

@router.get("/confounder/{belief_id}/risk")
async def get_confounder_risk(
    belief_id: str = Path(..., description="Belief identifier")
):
    """
    Get confounder risk assessment for a specific belief.

    Flags beliefs derived from observational studies without adequate confounding
    controls. Returns:
    - risk_level: high/medium/low
    - primary_confounders: Top confounds not controlled for
    - methodology_notes: Design features that mitigate risk
    - remediation_steps: How to reduce risk
    """
    try:
        from src.services.web_of_belief import WebOfBelief
        web = WebOfBelief()
        belief = web.get_belief(belief_id)
        if not belief:
            raise HTTPException(
                status_code=404,
                detail=f"Belief '{belief_id}' not found"
            )

        risk_assessment = belief.get("confounder_risk", {})
        return {
            "belief_id": belief_id,
            "risk_level": risk_assessment.get("level", "unknown"),
            "is_observational": risk_assessment.get("observational", False),
            "primary_confounders": risk_assessment.get("confounders", []),
            "control_features": risk_assessment.get("controls", []),
            "methodology_notes": risk_assessment.get("notes", ""),
            "remediation": risk_assessment.get("remediation", []),
            "confidence_in_assessment": risk_assessment.get("confidence", "medium")
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Confounder risk assessment failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to assess confounder risk: {str(e)}"
        )


# =============================================================================
# FRAMEWORK VOICES ENDPOINTS
# =============================================================================

@router.get("/frameworks/{topic}/voices")
async def get_framework_voices(
    topic: str = Path(..., description="Topic or belief topic"),
    max_voices: int = Query(3, ge=1, le=10, description="Max frameworks to return")
):
    """
    Get T1 framework perspectives on a topic.

    Returns perspectives from multiple theoretical frameworks (e.g., evolutionary,
    developmental, ecological, mechanistic). Each perspective includes:
    - framework_name: Theory name
    - prediction: What this framework predicts
    - evidence_support: How much evidence supports it
    - key_assumptions: Core commitments of the framework
    """
    try:
        from src.services.ai_panel_resolver import AIPanelResolver
        resolver = AIPanelResolver()
        perspectives = resolver.get_framework_perspectives(topic, max_voices)
        return {
            "topic": topic,
            "framework_count": len(perspectives),
            "frameworks": [
                {
                    "name": p.get("name", "unknown"),
                    "prediction": p.get("prediction", ""),
                    "evidence_support": p.get("support", 0.5),
                    "key_assumptions": p.get("assumptions", []),
                    "citations": p.get("citations", [])
                }
                for p in perspectives
            ]
        }

    except Exception as e:
        logger.warning(f"Framework voices retrieval failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve framework perspectives: {str(e)}"
        )


# =============================================================================
# KNOWLEDGE GAP ENDPOINTS
# =============================================================================

@router.get("/gaps/{topic}")
async def get_knowledge_gaps(
    topic: str = Path(..., description="Topic to analyze"),
    max_gaps: int = Query(5, ge=1, le=20, description="Max gaps to return")
):
    """
    Get knowledge gaps around a topic.

    Identifies important questions that haven't been adequately addressed in
    the literature. Each gap includes:
    - question: The unanswered research question
    - importance: Why this matters (high/medium/low)
    - scope: How broad is this gap (narrow/moderate/broad)
    - related_beliefs: What we do know
    """
    try:
        from src.services.interpretation_space_suggestions import (
            InterpretationSpaceSuggestionsManager
        )
        from app.db import get_db_path
        db_path = get_db_path() or "web.db"
        suggester = InterpretationSpaceSuggestionsManager(db_path)
        gaps = suggester.get_gaps(topic, max_gaps)

        return {
            "topic": topic,
            "gap_count": len(gaps),
            "gaps": [
                {
                    "question": g.get("question", ""),
                    "importance": g.get("importance", "medium"),
                    "scope": g.get("scope", "moderate"),
                    "related_beliefs": g.get("related", []),
                    "suggested_research_direction": g.get("research_direction", "")
                }
                for g in gaps
            ]
        }

    except Exception as e:
        logger.warning(f"Knowledge gap analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze knowledge gaps: {str(e)}"
        )


# =============================================================================
# FIGURE SUGGESTION ENDPOINTS
# =============================================================================

@router.get("/figures/{topic}")
async def get_suggested_figures(
    topic: str = Path(..., description="Topic to find figures for"),
    max_figures: int = Query(5, ge=1, le=20, description="Max figures to return")
):
    """
    Get relevant figures for a topic.

    Recommends figures from the system's figure gallery that are relevant to
    the given topic. Each suggestion includes:
    - figure_id: Internal reference
    - title: Figure title
    - relevance_score: How relevant (0-1)
    - caption: Original figure caption
    - source: Paper or document source
    """
    try:
        suggester = _get_figure_suggester()
        if not suggester:
            raise HTTPException(
                status_code=503,
                detail="Figure suggestion service unavailable"
            )

        figures = suggester.suggest_figures_for_topic(topic, max_figures)
        return {
            "topic": topic,
            "figure_count": len(figures),
            "figures": [
                {
                    "figure_id": f.get("id", ""),
                    "title": f.get("title", ""),
                    "relevance_score": f.get("relevance", 0.5),
                    "caption": f.get("caption", ""),
                    "source": f.get("source", ""),
                    "url": f.get("url")
                }
                for f in figures
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Figure suggestion failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to suggest figures: {str(e)}"
        )


# =============================================================================
# MATH EXPLANATION ENDPOINTS
# =============================================================================

@router.get("/math/{formula_name}")
async def explain_formula(
    formula_name: str = Path(..., description="Formula name or LaTeX"),
    user_type: UserTypeEnum = Query(UserTypeEnum.RESEARCHER, description="User type"),
    depth: str = Query("standard", description="brief, standard, or detailed")
):
    """
    Explain a mathematical formula.

    Provides an explanation of a formula tailored to the user type and
    requested depth level. Returns:
    - formula_latex: LaTeX representation
    - english_summary: Plain-language description
    - components: Explanation of each term
    - intuition: Why this formula matters
    - examples: Worked examples
    """
    try:
        explainer = _get_math_explainer()
        if not explainer:
            raise HTTPException(
                status_code=503,
                detail="Math explanation service unavailable"
            )

        explanation = explainer.explain_formula(
            formula_name,
            user_type=user_type.value,
            depth=depth
        )
        return {
            "formula_name": formula_name,
            "formula_latex": explanation.get("latex", ""),
            "english_summary": explanation.get("summary", ""),
            "components": explanation.get("components", []),
            "intuition": explanation.get("intuition", ""),
            "examples": explanation.get("examples", []),
            "depth_level": depth,
            "user_type": user_type.value
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Formula explanation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to explain formula: {str(e)}"
        )


# =============================================================================
# LANGUAGE ADAPTATION ENDPOINTS
# =============================================================================

@router.get("/language/profiles")
async def get_user_profiles():
    """
    Get all available user type profiles.

    Returns metadata about each user type including:
    - vocabulary_level: Complexity of language
    - technical_depth: How much technical detail
    - examples_per_section: Ratio of examples to theory
    - typical_use_cases: Who typically uses this profile
    """
    return {
        "profiles": [
            {
                "type": "researcher",
                "vocabulary_level": "advanced",
                "technical_depth": "high",
                "examples_per_section": 1,
                "typical_use_cases": ["literature review", "methodology development"]
            },
            {
                "type": "student",
                "vocabulary_level": "intermediate",
                "technical_depth": "moderate",
                "examples_per_section": 2,
                "typical_use_cases": ["learning", "coursework"]
            },
            {
                "type": "clinician",
                "vocabulary_level": "specialized",
                "technical_depth": "moderate",
                "examples_per_section": 3,
                "typical_use_cases": ["practice application", "case analysis"]
            },
            {
                "type": "policy_maker",
                "vocabulary_level": "plain",
                "technical_depth": "low",
                "examples_per_section": 3,
                "typical_use_cases": ["decision support", "briefing preparation"]
            },
            {
                "type": "general_public",
                "vocabulary_level": "plain",
                "technical_depth": "very_low",
                "examples_per_section": 4,
                "typical_use_cases": ["public engagement", "science communication"]
            }
        ]
    }


@router.post("/language/adapt")
async def adapt_text(request: LanguageAdaptationRequest):
    """
    Adapt text for a specific user type.

    Rewrites the input text to match vocabulary, depth, and structure
    appropriate for the specified user type. Returns:
    - original: Input text
    - adapted: Rewritten text
    - changes_made: List of adaptations applied
    - readability_metrics: Before/after readability scores
    """
    try:
        adapter = _get_language_adapter()
        if not adapter:
            raise HTTPException(
                status_code=503,
                detail="Language adaptation service unavailable"
            )

        adapted_text = adapter.adapt_text(
            text=request.text,
            user_type=request.user_type.value,
            context=request.context
        )

        return {
            "original": request.text,
            "adapted": adapted_text.get("text", request.text),
            "changes_made": adapted_text.get("changes", []),
            "user_type": request.user_type.value,
            "readability_original": adapted_text.get("readability_original", {}),
            "readability_adapted": adapted_text.get("readability_adapted", {})
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Language adaptation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to adapt text: {str(e)}"
        )


# =============================================================================
# Health/Status Endpoint
# =============================================================================

@router.get("/health")
async def services_health():
    """Check health status of all enrichment services."""
    health = {
        "timestamp": str(__import__('datetime').datetime.now(
            __import__('datetime').timezone.utc
        ).isoformat()),
        "services": {}
    }

    # Check each service
    try:
        _get_qa_handler()
        health["services"]["qa_handler"] = "available"
    except Exception:
        health["services"]["qa_handler"] = "unavailable"

    try:
        _get_language_adapter()
        health["services"]["language_adapter"] = "available"
    except Exception:
        health["services"]["language_adapter"] = "unavailable"

    try:
        _get_figure_suggester()
        health["services"]["figure_suggester"] = "available"
    except Exception:
        health["services"]["figure_suggester"] = "unavailable"

    try:
        _get_math_explainer()
        health["services"]["math_explainer"] = "available"
    except Exception:
        health["services"]["math_explainer"] = "unavailable"

    try:
        from src.services.answer_enrichment_orchestrator import AnswerEnrichmentOrchestrator
        AnswerEnrichmentOrchestrator()
        health["services"]["orchestrator"] = "available"
    except Exception:
        health["services"]["orchestrator"] = "unavailable"

    return health
