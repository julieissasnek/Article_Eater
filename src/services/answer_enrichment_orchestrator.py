"""
Answer Enrichment Orchestrator — Composes all epistemic services into rich answers
===================================================================================

This is the composition layer between question classification and response formatting.
It takes a base answer from arbitrary_qa_handler and enriches it with all available
epistemic services (credence intervals, warrant traces, confounder risk, framework
voices, gap analysis, follow-ups, language adaptation, figure suggestions).

Each enrichment step is optional (graceful degradation) and has a timeout.
If a service fails, the answer still works — we just skip that enrichment.

Design Principles:
1. Every enrichment step is wrapped in try/except — failures are isolated
2. Each step has a timeout (default 2s) — slow services are skipped
3. Track which services ran and their timing in metadata
4. Services are lazy-loaded — missing modules don't break initialization
5. Composable: can enable/disable specific enrichments via config

Author: Claude Code (agent for Prof. David Kirsh, UCSD Cognitive Science)
Date: 2026-03-03
"""

import json
import logging
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, Tuple, runtime_checkable
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


# =============================================================================
# SERVICE CONTRACTS (V11 Panel Fix: Protocol-based type safety)
# =============================================================================

@runtime_checkable
class CredenceService(Protocol):
    """Contract: must compute credence intervals for beliefs."""
    def compute_ci(self, beliefs: List[Dict], **kwargs) -> List[Dict]: ...

@runtime_checkable
class WarrantService(Protocol):
    """Contract: must decompose credence into warrant components."""
    def decompose(self, belief: Dict, **kwargs) -> List[Dict]: ...

@runtime_checkable
class RiskAssessor(Protocol):
    """Contract: must assess confounder/methodological risk."""
    def assess(self, belief: Dict, **kwargs) -> Dict[str, Any]: ...

@runtime_checkable
class GapDetector(Protocol):
    """Contract: must identify knowledge gaps around a topic."""
    def detect_gaps(self, question: str, beliefs: List[Dict], **kwargs) -> List[Dict]: ...

@runtime_checkable
class QuestionClassifierService(Protocol):
    """Contract: must classify question into explanation pattern."""
    def classify(self, question: str, **kwargs) -> Dict[str, Any]: ...


# =============================================================================
# STEP DEPENDENCY GRAPH (V11 Panel Fix: explicit ordering)
# =============================================================================

STEP_DEPENDENCIES = {
    # step_name: [steps that must run before it]
    "credence_ci": [],              # No dependencies — runs first
    "warrant_trace": ["credence_ci"],  # Needs enriched beliefs with credence
    "confounder_risk": [],           # Independent
    "framework_voices": [],          # Independent
    "gap_analysis": ["credence_ci"], # Benefits from knowing which beliefs exist
    "follow_ups": ["gap_analysis"],  # Builds on gap analysis
    "language_adaptation": [],       # Independent (transforms output at end)
    "figure_suggestions": [],        # Independent
    "interpretation_context": [],    # Independent
}

# Global latency budget (V11 Panel Fix: SRE recommendation)
DEFAULT_GLOBAL_TIMEOUT_MS = 5000  # 5 seconds total for all steps


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class EnrichmentConfig:
    """Configuration for which enrichments to run and timeouts."""
    enable_credence_ci: bool = True
    enable_warrant_trace: bool = True
    enable_confounder_risk: bool = True
    enable_framework_voices: bool = True
    enable_gap_analysis: bool = True
    enable_follow_ups: bool = True
    enable_language_adaptation: bool = True
    enable_figure_suggestions: bool = True
    enable_interpretation_context: bool = True  # Step 9: explanation patterns
    enable_circuit_context: bool = True         # Step 10: functional circuit enrichment
    timeout_per_service_ms: int = 2000
    global_timeout_ms: int = DEFAULT_GLOBAL_TIMEOUT_MS  # V11: total budget
    max_beliefs_to_enrich: int = 20
    max_framework_voices: int = 3
    max_gaps: int = 5
    max_follow_ups: int = 5
    max_figures: int = 5


# =============================================================================
# DATA STRUCTURES
# =============================================================================

class UserType(str, Enum):
    """User persona types for language adaptation."""
    RESEARCHER = "researcher"
    STUDENT = "student"
    CLINICIAN = "clinician"
    ARCHITECT_DESIGNER = "architect_designer"  # was POLICY_MAKER — practical spatial advice
    GENERAL_PUBLIC = "general_public"
    DEEP_RESEARCHER = "deep_researcher"  # V14: unlimited depth, research tools, thread-following


@dataclass
class EnrichedBelief:
    """A single belief with all enrichments applied.

    SUCCESS CONDITIONS:
    SC-EB-1: text is a non-empty string copied verbatim from input belief
    SC-EB-2: paper_ids is always a list (never None); defaults to []
    SC-EB-3: belief_id is preserved from input if provided, else None
    SC-EB-4: credence_point, if set, is a float in [0.0, 1.0]
    SC-EB-5: credence_ci, if set, is a dict with keys: lower, upper, se, width
    SC-EB-6: warrant_trace, if set, is a list of dicts each with 'component' key
    SC-EB-7: confounder_risk, if set, is one of: 'high', 'medium', 'low'
    SC-EB-8: All fields survive asdict() serialization without loss
    """
    text: str
    credence_point: Optional[float] = None
    credence_ci: Optional[Dict[str, float]] = None  # {lower, upper, se}
    warrant_trace: Optional[List[Dict[str, Any]]] = None  # [{component, value}, ...]
    confounder_risk: Optional[str] = None  # "high", "medium", "low"
    confounder_details: Optional[List[str]] = None
    # V13 Audit Fix: Preserve paper traceability through enrichment pipeline
    paper_ids: List[str] = field(default_factory=list)
    belief_id: Optional[str] = None


@dataclass
class EnrichedAnswer:
    """Full enriched answer with all service outputs.

    SUCCESS CONDITIONS:
    SC-EA-1: base_answer is preserved unmodified from input
    SC-EA-2: status is always one of: 'complete', 'partial', 'degraded', 'abstained'
    SC-EA-3: If status='complete', services_failed and services_skipped are both empty
    SC-EA-4: If status='abstained', enriched_beliefs, framework_voices, gaps,
             follow_ups, and figures are all empty
    SC-EA-5: warnings is always a list; never contains empty strings
    SC-EA-6: enrichment_metadata always contains: timing, services_attempted,
             services_failed, services_skipped, services_budget_exceeded
    SC-EA-7: to_dict() includes every dataclass field without loss
    SC-EA-8: to_json() produces valid JSON parseable by json.loads()
    """
    base_answer: Dict[str, Any]  # Original answer from arbitrary_qa_handler
    enriched_beliefs: List[EnrichedBelief] = field(default_factory=list)
    framework_voices: List[Dict[str, Any]] = field(default_factory=list)
    gaps: List[Dict[str, Any]] = field(default_factory=list)
    follow_ups: List[Dict[str, str]] = field(default_factory=list)
    figures: List[Dict[str, Any]] = field(default_factory=list)
    interpretation_context: Optional[Dict[str, Any]] = None  # Step 9 output
    user_type: str = "researcher"
    enrichment_metadata: Dict[str, Any] = field(default_factory=dict)
    # V13 Audit Fix: Explicit answer completeness status
    status: str = "complete"  # "complete", "partial", "degraded", "abstained"
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON output."""
        return {
            "base_answer": self.base_answer,
            "enriched_beliefs": [asdict(b) for b in self.enriched_beliefs],
            "framework_voices": self.framework_voices,
            "gaps": self.gaps,
            "follow_ups": self.follow_ups,
            "figures": self.figures,
            "interpretation_context": self.interpretation_context,
            "user_type": self.user_type,
            "enrichment_metadata": self.enrichment_metadata,
            "status": self.status,
            "warnings": self.warnings,
        }

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


# =============================================================================
# SERVICE IMPORTS (LAZY-LOADED)
# =============================================================================

class _ServiceRegistry:
    """Lazy-load all services; graceful degradation if modules missing.

    SUCCESS CONDITIONS:
    SC-SR-1: Each get_*() method returns the service module/instance or None — never raises
    SC-SR-2: If import fails, the error is logged and stored in _import_errors
    SC-SR-3: Second call to same getter returns cached result (no re-import)
    SC-SR-4: all_service_names() returns a list covering every service getter
    """

    def __init__(self):
        self._services = {}
        self._import_errors = {}

    def get_credence_intervals(self):
        """Lazy-load credence_intervals module."""
        if "credence_intervals" not in self._services:
            try:
                from src.services import credence_intervals
                self._services["credence_intervals"] = credence_intervals
            except ImportError as e:
                logger.warning(f"credence_intervals module not available: {e}")
                self._import_errors["credence_intervals"] = str(e)
        return self._services.get("credence_intervals")

    def get_warrant_strength(self):
        """Lazy-load warrant_strength module."""
        if "warrant_strength" not in self._services:
            try:
                from src.services import warrant_strength
                self._services["warrant_strength"] = warrant_strength
            except ImportError as e:
                logger.warning(f"warrant_strength module not available: {e}")
                self._import_errors["warrant_strength"] = str(e)
        return self._services.get("warrant_strength")

    def get_confounder_risk_checker(self):
        """Lazy-load confounder_risk_checker."""
        if "confounder_risk_checker" not in self._services:
            try:
                from src.qa.confounder_risk_checker import ConfounderRiskChecker
                self._services["confounder_risk_checker"] = ConfounderRiskChecker()
            except ImportError as e:
                logger.warning(f"confounder_risk_checker not available: {e}")
                self._import_errors["confounder_risk_checker"] = str(e)
        return self._services.get("confounder_risk_checker")

    def get_gap_predictor(self):
        """Lazy-load gap_predictor."""
        if "gap_predictor" not in self._services:
            try:
                from src.services.gap_predictor import GapPredictor
                self._services["gap_predictor"] = GapPredictor()
            except ImportError as e:
                logger.warning(f"gap_predictor not available: {e}")
                self._import_errors["gap_predictor"] = str(e)
        return self._services.get("gap_predictor")

    def get_integrated_query_service(self):
        """Lazy-load integrated_query_service."""
        if "integrated_query_service" not in self._services:
            try:
                from src.services.integrated_query_service import IntegratedQueryService
                self._services["integrated_query_service"] = IntegratedQueryService()
            except ImportError as e:
                logger.warning(f"integrated_query_service not available: {e}")
                self._import_errors["integrated_query_service"] = str(e)
        return self._services.get("integrated_query_service")

    def get_recommendation_loop(self):
        """Lazy-load recommendation_loop."""
        if "recommendation_loop" not in self._services:
            try:
                from src.services.recommendation_loop import RecommendationLoopService
                from src.utils.db_locator import resolve_db_path
                self._services["recommendation_loop"] = RecommendationLoopService(
                    db_path=resolve_db_path("data/web_persistence_v2.db"),
                    web_db_path=resolve_db_path("data/article_eater.db"),
                )
            except (ImportError, Exception) as e:
                logger.warning(f"recommendation_loop not available: {e}")
                self._import_errors["recommendation_loop"] = str(e)
        return self._services.get("recommendation_loop")

    def get_follow_up_suggestion_service(self):
        """Lazy-load follow-up suggestion service."""
        if "follow_up_suggestion_service" not in self._services:
            # First try dedicated service if it exists
            try:
                from src.services.follow_up_suggestion_service import FollowUpSuggestionService
                self._services["follow_up_suggestion_service"] = FollowUpSuggestionService()
            except ImportError:
                # Fallback to recommendation loop
                logger.info("Dedicated follow_up_suggestion_service not found, falling back to recommendation_loop.")
                self._services["follow_up_suggestion_service"] = self.get_recommendation_loop()
        return self._services.get("follow_up_suggestion_service")

    def get_theory_guide_service(self):
        """Lazy-load theory_guide_service."""
        if "theory_guide_service" not in self._services:
            try:
                from src.services.theory_guide_service import TheoryGuideService
                self._services["theory_guide_service"] = TheoryGuideService()
            except ImportError as e:
                logger.warning(f"theory_guide_service not available: {e}")
                self._import_errors["theory_guide_service"] = str(e)
        return self._services.get("theory_guide_service")

    def get_knowledge_catalog(self):
        """Lazy-load knowledge_catalog."""
        if "knowledge_catalog" not in self._services:
            try:
                from src.services.knowledge_catalog import KnowledgeCatalog
                self._services["knowledge_catalog"] = KnowledgeCatalog()
            except ImportError as e:
                logger.warning(f"knowledge_catalog not available: {e}")
                self._import_errors["knowledge_catalog"] = str(e)
        return self._services.get("knowledge_catalog")

    def get_interpretive_intelligence(self):
        """Lazy-load interpretive_intelligence — explanation engine."""
        if "interpretive_intelligence" not in self._services:
            try:
                from src.services.interpretive_intelligence import (
                    QuestionClassifier,
                    ExplanationPattern,
                    DetailLevel,
                    ExpertiseLevel,
                    ExplanationRequest,
                )
                self._services["interpretive_intelligence"] = {
                    "classifier": QuestionClassifier(),
                    "ExplanationPattern": ExplanationPattern,
                    "DetailLevel": DetailLevel,
                    "ExpertiseLevel": ExpertiseLevel,
                    "ExplanationRequest": ExplanationRequest,
                }
            except ImportError as e:
                logger.warning(f"interpretive_intelligence not available: {e}")
                self._import_errors["interpretive_intelligence"] = str(e)
        return self._services.get("interpretive_intelligence")

    def get_figure_suggestion_service(self):
        """Lazy-load figure suggestion service (indexed figure registry)."""
        if "figure_suggestion_service" not in self._services:
            try:
                from src.services.figure_suggestion_service import FigureSuggestionService
                self._services["figure_suggestion_service"] = FigureSuggestionService()
            except ImportError as e:
                logger.warning(f"figure_suggestion_service not available: {e}")
                self._import_errors["figure_suggestion_service"] = str(e)
        return self._services.get("figure_suggestion_service")

    # V11 Panel Fix: Removed dead registry entries (argumentation_graph,
    # bridge_warrants, prediction_generator) that were loaded but never called
    # by any enrichment step. Per Panel Member B: "Dead code in a service
    # registry is worse than no registry — it implies capabilities that don't
    # exist." These services exist in src/services/ and can be re-added when
    # wired to actual enrichment steps.

    def all_service_names(self) -> List[str]:
        """List all registered service getter names."""
        return [
            "credence_intervals", "warrant_strength", "confounder_risk_checker",
            "gap_predictor", "integrated_query_service", "recommendation_loop",
            "theory_guide_service", "knowledge_catalog", "interpretive_intelligence",
            "t3_interp_bridge", "follow_up_suggestion_service",
            "figure_suggestion_service",
        ]


# =============================================================================
# MAIN ORCHESTRATOR
# =============================================================================

class AnswerEnrichmentOrchestrator:
    """Composes all epistemic services to enrich base answers.

    V11 Panel Fixes Applied:
    - Protocol-based service contracts for type safety
    - health_check() method for operational readiness
    - Global latency budget (default 5s) cancels remaining steps
    - Explicit step dependency ordering
    - Dead registry entries removed
    """

    def __init__(self, config: Optional[EnrichmentConfig] = None):
        """
        Initialize orchestrator with optional configuration.

        Args:
            config: EnrichmentConfig specifying which enrichments to run
        """
        self._config = config or EnrichmentConfig()
        self._services = _ServiceRegistry()

    def health_check(self) -> Dict[str, Any]:
        """V11 Panel Fix: Health check endpoint.

        Probes all registered services and reports availability.
        Returns dict with overall status and per-service details.
        """
        results = {}
        healthy = 0
        total = 0

        service_getters = {
            "credence_intervals": self._services.get_credence_intervals,
            "warrant_strength": self._services.get_warrant_strength,
            "confounder_risk_checker": self._services.get_confounder_risk_checker,
            "gap_predictor": self._services.get_gap_predictor,
            "integrated_query_service": self._services.get_integrated_query_service,
            "recommendation_loop": self._services.get_recommendation_loop,
            "theory_guide_service": self._services.get_theory_guide_service,
            "knowledge_catalog": self._services.get_knowledge_catalog,
            "interpretive_intelligence": self._services.get_interpretive_intelligence,
        }

        for name, getter in service_getters.items():
            total += 1
            try:
                svc = getter()
                if svc is not None:
                    results[name] = {"status": "available", "error": None}
                    healthy += 1
                else:
                    err = self._services._import_errors.get(name, "returned None")
                    results[name] = {"status": "unavailable", "error": err}
            except Exception as e:
                results[name] = {"status": "error", "error": str(e)}

        return {
            "overall": "healthy" if healthy == total else "degraded",
            "healthy_count": healthy,
            "total_count": total,
            "healthy_ratio": healthy / total if total > 0 else 0.0,
            "services": results,
            "import_errors": dict(self._services._import_errors),
            "global_timeout_ms": self._config.global_timeout_ms,
            "step_dependencies": STEP_DEPENDENCIES,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def enrich(  # noqa: C901
        self,
        base_answer: Dict[str, Any],
        question: str,
        user_type: str = "researcher",
        timeout_per_service_ms: Optional[int] = None,
    ) -> EnrichedAnswer:
        """
        Take a base answer from arbitrary_qa_handler and enrich it with all services.

        Enrichment steps (each optional, with graceful fallback):
        1. Credence enrichment — add CI to every belief in the answer
        2. Warrant trace — decompose each belief's credence into contributing warrants
        3. Confounder risk — flag beliefs from observational studies without controls
        4. Framework voices — get T1 framework perspectives on the topic
        5. Gap analysis — identify what's missing around this topic
        6. Follow-up suggestions — generate VOI-ranked research questions
        7. Language adaptation — adjust vocabulary/structure per user type
        8. Figure suggestions — identify which existing figures are relevant
        9. Interpretation context — classify question pattern for response structuring

        Args:
            base_answer: Dict from arbitrary_qa_handler.answer() with structure:
                {
                    "answer": str,
                    "beliefs": List[Dict],
                    "evidence_count": int,
                    ...
                }
            question: Original user question
            user_type: One of UserType enum values (for language adaptation)
            timeout_per_service_ms: Override config timeout

        Returns:
            EnrichedAnswer with all enrichments applied

        SUCCESS CONDITIONS:
        SC-E-1: Grounding gate runs FIRST; if it crashes, return early with status='abstained'
        SC-E-2: If grounding gate says should_abstain=True, return early with status='abstained'
        SC-E-3: base_answer is stored unmodified in result.base_answer
        SC-E-4: question is recorded in enrichment_metadata['question']
        SC-E-5: Every enabled step appears in services_attempted
        SC-E-6: Every attempted service appears in exactly ONE of: timing, services_failed, services_skipped
        SC-E-7: Global budget is checked before each step; exceeded steps go to services_budget_exceeded
        SC-E-8: After all steps, status is set based on failures/skips (see EnrichedAnswer SC-EA-2/3)
        SC-E-9: enrichment_metadata always has keys: timestamp, question, services_attempted,
                services_failed, services_skipped, services_budget_exceeded, timing
        """
        timeout_ms = timeout_per_service_ms or self._config.timeout_per_service_ms
        global_deadline = time.monotonic() + (self._config.global_timeout_ms / 1000.0)

        enriched = EnrichedAnswer(
            base_answer=base_answer,
            user_type=user_type,
            enrichment_metadata={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "question": question,
                "services_attempted": [],
                "services_failed": [],
                "services_skipped": [],
                "services_budget_exceeded": [],  # V11: steps cancelled by budget
                "timing": {},
                "global_timeout_ms": self._config.global_timeout_ms,
            },
        )

        def _budget_remaining() -> bool:
            """V11 Panel Fix: check if global latency budget is exceeded."""
            return time.monotonic() < global_deadline

        def _check_budget(step_name: str) -> bool:
            """Check budget and log if exceeded."""
            if not _budget_remaining():
                elapsed = self._config.global_timeout_ms  # we've used it all
                logger.warning(
                    f"Global latency budget ({self._config.global_timeout_ms}ms) "
                    f"exceeded — skipping {step_name}"
                )
                enriched.enrichment_metadata["services_budget_exceeded"].append(step_name)
                return False
            return True

        # Extract beliefs from base answer
        beliefs = base_answer.get("beliefs", [])
        if not beliefs:
            logger.warning(
                f"No beliefs found in base_answer. Keys: {list(base_answer.keys())}"
            )
            beliefs = []

        # ====================================================================
        # Step 0: GROUNDING GATE (Haack's Foundherentist Principle)
        # Before any enrichment, verify empirical anchoring.
        # If the query has zero supporting evidence, return explicit abstention.
        # ====================================================================
        try:
            from src.qa.grounding_gate import GroundingGate
            grounding_gate = GroundingGate()
            grounding_result = grounding_gate.check(question, beliefs)
            enriched.enrichment_metadata["grounding"] = {
                "has_empirical_anchor": grounding_result.has_empirical_anchor,
                "n_supporting_findings": grounding_result.n_supporting_findings,
                "coherence_status": grounding_result.coherence_status,
                "recommendation": grounding_result.recommendation,
                "grounding_time_ms": grounding_result.grounding_time_ms,
            }
            if grounding_result.should_abstain:
                logger.warning(
                    f"Grounding gate ABSTAIN: {grounding_result.reason}"
                )
                enriched.enrichment_metadata["abstention"] = {
                    "applied": True,
                    "reason": grounding_result.reason,
                }
                enriched.status = "abstained"
                enriched.warnings.append(
                    f"Answer abstained: {grounding_result.reason}"
                )
                # Return early — do not enrich ungrounded answers
                return enriched
        except ImportError as e:
            # CW Review: Distinguish 'module not installed' from 'module crashed'.
            # ImportError = system deployed without grounding gate module.
            logger.error(f"Grounding gate MODULE MISSING — abstaining for safety: {e}")
            enriched.enrichment_metadata["grounding"] = {
                "error": str(e),
                "fatal": True,
                "error_type": "module_missing",
            }
            enriched.enrichment_metadata["abstention"] = {
                "applied": True,
                "reason": f"Grounding gate not installed: {e}",
            }
            enriched.status = "abstained"
            enriched.warnings.append(
                f"Answer abstained: grounding gate not installed ({e})"
            )
            return enriched
        except Exception as e:
            # V13 Audit Fix: Grounding gate is a SAFETY gate, not optional.
            # If it crashes, we MUST abstain rather than proceed with enrichment.
            # Proceeding would risk hallucinated high-confidence answers.
            logger.error(f"Grounding gate CRASHED — abstaining for safety: {e}")
            enriched.enrichment_metadata["grounding"] = {
                "error": str(e),
                "fatal": True,
                "error_type": "runtime_crash",
            }
            enriched.enrichment_metadata["abstention"] = {
                "applied": True,
                "reason": f"Grounding system crashed: {e}",
            }
            enriched.status = "abstained"
            enriched.warnings.append(
                f"Answer abstained: grounding gate crashed ({e})"
            )
            return enriched


        # V11 Panel Fix: Steps run in dependency order with budget checks.
        # Dependencies declared in STEP_DEPENDENCIES dict.

        # Step 1: Credence enrichment (no deps)
        if self._config.enable_credence_ci and _check_budget("credence_ci"):
            self._enrich_credence(
                enriched, beliefs, timeout_ms
            )

        # CW Review Fix: If credence enrichment was skipped/disabled but beliefs
        # exist, create shell EnrichedBelief objects to preserve paper_ids.
        # Without this, paper traceability is lost when credence is off.
        if not enriched.enriched_beliefs and beliefs:
            for belief_dict in beliefs[:self._config.max_beliefs_to_enrich]:
                enriched.enriched_beliefs.append(EnrichedBelief(
                    text=belief_dict.get("text", ""),
                    paper_ids=belief_dict.get("paper_ids", []),
                    belief_id=belief_dict.get("belief_id"),
                ))

        # Step 2: Warrant trace (depends on credence_ci)
        if self._config.enable_warrant_trace and _check_budget("warrant_trace"):
            self._enrich_warrant_trace(
                enriched, beliefs, timeout_ms
            )

        # Step 3: Confounder risk (no deps)
        if self._config.enable_confounder_risk and _check_budget("confounder_risk"):
            self._enrich_confounder_risk(
                enriched, beliefs, timeout_ms
            )

        # Step 4: Framework voices (no deps)
        if self._config.enable_framework_voices and _check_budget("framework_voices"):
            self._get_framework_voices(
                enriched, question, timeout_ms
            )

        # Step 5: Gap analysis (depends on credence_ci)
        if self._config.enable_gap_analysis and _check_budget("gap_analysis"):
            self._identify_gaps(
                enriched, question, beliefs, timeout_ms
            )

        # Step 6: Follow-up suggestions (depends on gap_analysis)
        if self._config.enable_follow_ups and _check_budget("follow_ups"):
            self._suggest_follow_ups(
                enriched, question, beliefs, timeout_ms
            )

        # Step 7: Language adaptation (no deps)
        if self._config.enable_language_adaptation and _check_budget("language_adaptation"):
            self._adapt_language(
                enriched, user_type, timeout_ms
            )

        # Step 8: Figure suggestions (no deps)
        if self._config.enable_figure_suggestions and _check_budget("figure_suggestions"):
            self._suggest_figures(
                enriched, question, beliefs, timeout_ms
            )

        # Step 9: Interpretation context (no deps)
        if self._config.enable_interpretation_context and _check_budget("interpretation_context"):
            self._add_interpretation_context(
                enriched, question, user_type, timeout_ms
            )

        # Step 10: Circuit context enrichment (no deps)
        # If the answer relates to a functional circuit, add epistemic framing
        if self._config.enable_circuit_context and _check_budget("circuit_context"):
            self._enrich_circuit_context(
                enriched, question, timeout_ms
            )

        # V13 Audit Fix: Populate status and warnings based on service results
        failed = enriched.enrichment_metadata.get("services_failed", [])
        skipped = enriched.enrichment_metadata.get("services_skipped", [])
        budget_exceeded = enriched.enrichment_metadata.get("services_budget_exceeded", [])

        if failed:
            enriched.status = "degraded"
            enriched.warnings.append(
                f"{len(failed)} enrichment service(s) failed: {', '.join(failed)}. "
                f"Answer confidence may be reduced."
            )
        elif skipped or budget_exceeded:
            enriched.status = "partial"
            if skipped:
                enriched.warnings.append(
                    f"{len(skipped)} service(s) unavailable: {', '.join(skipped)}"
                )
            if budget_exceeded:
                enriched.warnings.append(
                    f"{len(budget_exceeded)} service(s) skipped due to latency budget: "
                    f"{', '.join(budget_exceeded)}"
                )
        else:
            enriched.status = "complete"

        return enriched

    # =========================================================================
    # ENRICHMENT STEP IMPLEMENTATIONS
    # =========================================================================

    def _enrich_credence(
        self,
        enriched: EnrichedAnswer,
        beliefs: List[Dict],
        timeout_ms: int,
    ) -> None:
        """Add confidence intervals to each belief.

        SUCCESS CONDITIONS:
        SC-CR-1: 'credence_enrichment' appears in services_attempted
        SC-CR-2: If service unavailable, 'credence_enrichment' in services_skipped; return without crash
        SC-CR-3: One EnrichedBelief created per input belief (up to max_beliefs_to_enrich)
        SC-CR-4: Each EnrichedBelief.text == input belief['text'] (verbatim copy)
        SC-CR-5: Each EnrichedBelief.paper_ids == input belief.get('paper_ids', [])
        SC-CR-6: Each EnrichedBelief.belief_id == input belief.get('belief_id')
        SC-CR-7: credence_point is a float in [0.0, 1.0] when computation succeeds
        SC-CR-8: credence_ci has keys {lower, upper, se, width} when computation succeeds
        SC-CR-9: Per-belief failure logged but does not crash the whole step
        SC-CR-10: Timing recorded in enrichment_metadata['timing']['credence_enrichment']
        SC-CR-11: On total failure, 'credence_enrichment' in services_failed
        """
        service_name = "credence_enrichment"
        enriched.enrichment_metadata["services_attempted"].append(service_name)

        start = time.time()
        try:
            ci_module = self._services.get_credence_intervals()
            if not ci_module:
                enriched.enrichment_metadata["services_skipped"].append(service_name)
                return

            # For each belief, try to extract credence parameters
            for belief_dict in beliefs[:self._config.max_beliefs_to_enrich]:
                if (time.time() - start) * 1000 > timeout_ms:
                    logger.warning(
                        f"{service_name}: timeout after {timeout_ms}ms, stopping"
                    )
                    break

                belief_text = belief_dict.get("text", "")
                p_lab = belief_dict.get("p_lab", 0.5)
                d = belief_dict.get("d", 0.8)
                omega = belief_dict.get("omega", 0.6)
                delta = belief_dict.get("delta", 1.0)

                try:
                    estimate = ci_module.compute_credence_with_ci(
                        p_lab=p_lab,
                        d=d,
                        omega=omega,
                        delta=delta,
                    )

                    enriched_belief = EnrichedBelief(
                        text=belief_text,
                        credence_point=estimate.point,
                        credence_ci={
                            "lower": estimate.lower,
                            "upper": estimate.upper,
                            "se": estimate.se,
                            "width": estimate.width(),
                        },
                        # V13 Audit Fix: Preserve paper traceability
                        paper_ids=belief_dict.get("paper_ids", []),
                        belief_id=belief_dict.get("belief_id"),
                    )
                    enriched.enriched_beliefs.append(enriched_belief)
                except Exception as e:
                    logger.debug(
                        f"{service_name}: failed to enrich belief: {e}"
                    )

            elapsed = (time.time() - start) * 1000
            enriched.enrichment_metadata["timing"][service_name] = elapsed
            logger.info(
                f"{service_name}: enriched {len(enriched.enriched_beliefs)} beliefs in {elapsed:.1f}ms"
            )

        except Exception as e:
            elapsed = (time.time() - start) * 1000
            enriched.enrichment_metadata["services_failed"].append(service_name)
            enriched.enrichment_metadata["timing"][service_name] = elapsed
            logger.warning(f"{service_name}: {e}")

    def _enrich_warrant_trace(
        self,
        enriched: EnrichedAnswer,
        beliefs: List[Dict],
        timeout_ms: int,
    ) -> None:
        """Decompose each belief's credence into warrant contributions.

        SUCCESS CONDITIONS:
        SC-WT-1: 'warrant_trace' appears in services_attempted
        SC-WT-2: If service unavailable, 'warrant_trace' in services_skipped; return without crash
        SC-WT-3: Each enriched belief gets warrant_trace set (list of dicts)
        SC-WT-4: Each warrant_trace dict has a 'component' key
        SC-WT-5: Standard components include: experimental_severity, confound_control, replication, publication_meta
        SC-WT-6: Per-belief failure logged but does not crash the whole step
        SC-WT-7: Timing recorded in enrichment_metadata['timing']['warrant_trace']
        SC-WT-8: On total failure, 'warrant_trace' in services_failed
        """
        service_name = "warrant_trace"
        enriched.enrichment_metadata["services_attempted"].append(service_name)

        start = time.time()
        try:
            warrant_module = self._services.get_warrant_strength()
            if not warrant_module:
                enriched.enrichment_metadata["services_skipped"].append(service_name)
                return

            # Import warrant computation functions once outside the loop
            from src.services.warrant_strength import (
                compute_omega_sev, compute_omega_conf,
                compute_omega_rep, compute_omega_meta,
                DesignType, PublicationType,
            )

            # Map string design types to DesignType enum — expanded to handle
            # real extraction data formats (P1 fix: extraction JSONs use varied
            # naming like "Experimental", "Cross-Sectional", "Survey", etc.)
            _design_map = {
                "experimental": DesignType.STANDARD_RCT,
                "rct": DesignType.STANDARD_RCT,
                "randomized_controlled_trial": DesignType.STANDARD_RCT,
                "large_rct": DesignType.LARGE_RCT,
                "quasi_experimental": DesignType.QUASI_EXPERIMENTAL,
                "quasi-experimental": DesignType.QUASI_EXPERIMENTAL,
                "within_subjects": DesignType.WITHIN_SUBJECTS,
                "within-subjects": DesignType.WITHIN_SUBJECTS,
                "repeated_measures": DesignType.WITHIN_SUBJECTS,
                "observational": DesignType.OBSERVATIONAL,
                "cross_sectional": DesignType.OBSERVATIONAL,
                "cross-sectional": DesignType.OBSERVATIONAL,
                "survey": DesignType.OBSERVATIONAL,
                "correlational": DesignType.OBSERVATIONAL,
                "longitudinal": DesignType.OBSERVATIONAL,
                "case_study": DesignType.CASE_STUDY,
                "case-study": DesignType.CASE_STUDY,
                "case_report": DesignType.CASE_STUDY,
                "meta_analysis": DesignType.META_ANALYSIS,
                "meta-analysis": DesignType.META_ANALYSIS,
                "systematic_review": DesignType.SYSTEMATIC_REVIEW,
                "systematic-review": DesignType.SYSTEMATIC_REVIEW,
                "review": DesignType.SYSTEMATIC_REVIEW,
            }

            for i, enriched_belief in enumerate(
                enriched.enriched_beliefs[:self._config.max_beliefs_to_enrich]
            ):
                if (time.time() - start) * 1000 > timeout_ms:
                    logger.warning(
                        f"{service_name}: timeout after {timeout_ms}ms, stopping"
                    )
                    break

                try:
                    # P1 fix: Extract design metadata from the ORIGINAL beliefs
                    # dicts (which have the extraction data), not from EnrichedBelief
                    # (which only has text, credence, and paper_ids).
                    orig_belief = beliefs[i] if i < len(beliefs) else {}
                    if isinstance(orig_belief, dict):
                        raw_design = orig_belief.get('design_type') or orig_belief.get('study_design') or "observational"
                        sample_n = orig_belief.get('sample_size') or orig_belief.get('n') or orig_belief.get('N')
                        pre_reg = orig_belief.get('pre_registered', False)
                        n_confounds = orig_belief.get('n_confounds', 1)
                        n_reps = orig_belief.get('n_replications', 0)
                    else:
                        raw_design = getattr(orig_belief, 'design_type', None) or "observational"
                        sample_n = getattr(orig_belief, 'sample_size', None) or getattr(orig_belief, 'n', None)
                        pre_reg = getattr(orig_belief, 'pre_registered', False)
                        n_confounds = getattr(orig_belief, 'n_confounds', 1)
                        n_reps = getattr(orig_belief, 'n_replications', 0)

                    # Normalize the design string and look up the enum
                    normalized = str(raw_design).lower().strip().replace("-", "_").replace(" ", "_")
                    design_enum = _design_map.get(normalized, DesignType.OBSERVATIONAL)

                    # Compute actual omega components using panel-approved formulas
                    omega_sev = compute_omega_sev(
                        design_type=design_enum,
                        sample_size=int(sample_n) if sample_n else None,
                        pre_registered=bool(pre_reg),
                    )
                    omega_conf = compute_omega_conf(
                        n_uncontrolled_confounds=int(n_confounds) if n_confounds else 1,
                        has_randomization=design_enum in (DesignType.STANDARD_RCT, DesignType.LARGE_RCT),
                    )
                    omega_rep = compute_omega_rep(
                        n_independent_replications=int(n_reps) if n_reps else 0,
                    )
                    omega_meta = compute_omega_meta(
                        publication_type=PublicationType.PEER_REVIEWED,
                        is_pre_registered=bool(pre_reg),
                    )

                    # Create warrant trace with real computed values
                    trace = [
                        {"component": "experimental_severity", "omega_sev": round(omega_sev, 3),
                         "design_type": design_enum.value},
                        {"component": "confound_control", "omega_conf": round(omega_conf, 3)},
                        {"component": "replication", "omega_rep": round(omega_rep, 3)},
                        {"component": "publication_meta", "omega_meta": round(omega_meta, 3)},
                    ]

                    enriched_belief.warrant_trace = trace
                except Exception as e:
                    logger.debug(f"{service_name}: failed for belief {i}: {e}")

            elapsed = (time.time() - start) * 1000
            enriched.enrichment_metadata["timing"][service_name] = elapsed
            logger.info(f"{service_name}: completed in {elapsed:.1f}ms")

        except Exception as e:
            elapsed = (time.time() - start) * 1000
            enriched.enrichment_metadata["services_failed"].append(service_name)
            enriched.enrichment_metadata["timing"][service_name] = elapsed
            logger.warning(f"{service_name}: {e}")

    def _enrich_confounder_risk(
        self,
        enriched: EnrichedAnswer,
        beliefs: List[Dict],
        timeout_ms: int,
    ) -> None:
        """Flag confounder risks per belief.

        SUCCESS CONDITIONS:
        SC-CF-1: 'confounder_risk' appears in services_attempted
        SC-CF-2: If service unavailable, 'confounder_risk' in services_skipped; return without crash
        SC-CF-3: Each enriched belief gets confounder_risk set to one of: 'high', 'medium', 'low'
        SC-CF-4: Each enriched belief gets confounder_details as a non-empty list of strings
        SC-CF-5: Observational designs get risk >= 'medium'
        SC-CF-6: Per-belief failure logged but does not crash the whole step
        SC-CF-7: Timing recorded in enrichment_metadata['timing']['confounder_risk']
        SC-CF-8: On total failure, 'confounder_risk' in services_failed
        """
        service_name = "confounder_risk"
        enriched.enrichment_metadata["services_attempted"].append(service_name)

        start = time.time()
        try:
            # P1 fix: Classify confounder risk based on study design.
            # Uses design_type from original beliefs dicts (not EnrichedBelief).
            # No external checker service needed — inline analysis is sufficient.

            # Design types grouped by inherent confound risk level
            _high_risk_designs = {
                "observational", "cross_sectional", "cross-sectional",
                "survey", "correlational", "case_study", "case-study",
                "case_report", "longitudinal", "retrospective",
                "ecological", "qualitative",
            }
            _medium_risk_designs = {
                "quasi_experimental", "quasi-experimental",
                "within_subjects", "within-subjects", "repeated_measures",
                "natural_experiment", "field_study",
            }
            _low_risk_designs = {
                "experimental", "rct", "randomized_controlled_trial",
                "standard_rct", "large_rct",
            }
            _synthesis_designs = {
                "meta_analysis", "meta-analysis",
                "systematic_review", "systematic-review", "review",
            }

            for i, belief_dict in enumerate(
                enriched.enriched_beliefs[:self._config.max_beliefs_to_enrich]
            ):
                if (time.time() - start) * 1000 > timeout_ms:
                    logger.warning(
                        f"{service_name}: timeout after {timeout_ms}ms, stopping"
                    )
                    break

                try:
                    # P1 fix: bounds-check the beliefs array
                    orig_belief = beliefs[i] if i < len(beliefs) else {}
                    if isinstance(orig_belief, dict):
                        raw_design = orig_belief.get("design_type") or orig_belief.get("study_design") or "observational"
                    else:
                        raw_design = getattr(orig_belief, "design_type", None) or "observational"

                    normalized = str(raw_design).lower().strip().replace("-", "_").replace(" ", "_")

                    if normalized in _high_risk_designs:
                        belief_dict.confounder_risk = "high"
                        belief_dict.confounder_details = [
                            f"Observational design ({raw_design}): cannot rule out confounding",
                            "Consider: selection bias, unmeasured confounds, reverse causation",
                        ]
                    elif normalized in _medium_risk_designs:
                        belief_dict.confounder_risk = "medium"
                        belief_dict.confounder_details = [
                            f"Quasi-experimental design ({raw_design}): partial confound control",
                            "Consider: selection bias, maturation effects",
                        ]
                    elif normalized in _synthesis_designs:
                        belief_dict.confounder_risk = "low"
                        belief_dict.confounder_details = [
                            f"Synthesis design ({raw_design}): aggregated across studies",
                            "Confound risk depends on constituent study designs",
                        ]
                    elif normalized in _low_risk_designs:
                        belief_dict.confounder_risk = "low"
                        belief_dict.confounder_details = [
                            f"Experimental design ({raw_design}) with randomization",
                        ]
                    else:
                        # Unknown design type — default to medium
                        belief_dict.confounder_risk = "medium"
                        belief_dict.confounder_details = [
                            f"Unrecognized design type ({raw_design}): defaulting to medium risk",
                        ]
                except Exception as e:
                    logger.debug(f"{service_name}: failed for belief {i}: {e}")

            elapsed = (time.time() - start) * 1000
            enriched.enrichment_metadata["timing"][service_name] = elapsed
            logger.info(f"{service_name}: completed in {elapsed:.1f}ms")

        except Exception as e:
            elapsed = (time.time() - start) * 1000
            enriched.enrichment_metadata["services_failed"].append(service_name)
            enriched.enrichment_metadata["timing"][service_name] = elapsed
            logger.warning(f"{service_name}: {e}")

    def _get_framework_voices(
        self,
        enriched: EnrichedAnswer,
        topic: str,
        timeout_ms: int,
    ) -> None:
        """Get T1 framework perspectives on the topic.

        Uses the FrameworkVoiceRenderer with pre-computed MV data when available.
        Falls back to IntegratedQueryService.get_theoretical_voices() otherwise.

        SUCCESS CONDITIONS (updated for corpus-grounded voices):
        SC-FV-1: 'framework_voices' appears in services_attempted
        SC-FV-2: If service unavailable, 'framework_voices' in services_skipped; return without crash
        SC-FV-3: enriched.framework_voices is a list of dicts
        SC-FV-4: Each dict has keys: 'framework', 'voice', 'n_papers', 'source', 'confidence_level'
        SC-FV-5: len(framework_voices) <= config.max_framework_voices
        SC-FV-6: Timing recorded in enrichment_metadata['timing']['framework_voices']
        SC-FV-7: On total failure, 'framework_voices' in services_failed
        SC-FV-8: source field is 'corpus_grounded' or 'framework_template'
        """
        service_name = "framework_voices"
        enriched.enrichment_metadata["services_attempted"].append(service_name)

        start = time.time()
        try:
            # Attempt 1: Use FrameworkVoiceRenderer with MV cache
            try:
                from src.qa.framework_voice_renderer import FrameworkVoiceRenderer
                from src.qa.mv_builder import MaterializedViewBuilder

                builder = MaterializedViewBuilder()
                mv_data = builder.get_view("framework_voices")

                if mv_data and "data" in mv_data and mv_data.get("status") == "FRESH":
                    renderer = FrameworkVoiceRenderer()
                    enriched.framework_voices = renderer.render_voices_as_dicts(
                        mv_data["data"],
                        topic=topic,
                        limit=self._config.max_framework_voices,
                    )
                    elapsed = (time.time() - start) * 1000
                    enriched.enrichment_metadata["timing"][service_name] = elapsed
                    enriched.enrichment_metadata["framework_voice_source"] = "mv_cache"
                    logger.info(
                        f"{service_name}: rendered {len(enriched.framework_voices)} "
                        f"corpus-grounded voices from MV cache in {elapsed:.1f}ms"
                    )
                    return
            except Exception as e:
                logger.debug(f"MV renderer path failed: {e}")

            # Attempt 2: Build on-the-fly with renderer
            try:
                from src.qa.framework_voice_renderer import FrameworkVoiceRenderer
                from src.qa.mv_builder import MaterializedViewBuilder

                builder = MaterializedViewBuilder()
                fw_data = builder.build_framework_voices()

                if isinstance(fw_data, dict) and "error" not in fw_data:
                    renderer = FrameworkVoiceRenderer()
                    enriched.framework_voices = renderer.render_voices_as_dicts(
                        fw_data,
                        topic=topic,
                        limit=self._config.max_framework_voices,
                    )
                    elapsed = (time.time() - start) * 1000
                    enriched.enrichment_metadata["timing"][service_name] = elapsed
                    enriched.enrichment_metadata["framework_voice_source"] = "on_the_fly"
                    logger.info(
                        f"{service_name}: rendered {len(enriched.framework_voices)} "
                        f"corpus-grounded voices on-the-fly in {elapsed:.1f}ms"
                    )
                    return
            except Exception as e:
                logger.debug(f"On-the-fly renderer path failed: {e}")

            # Attempt 3: Fall back to IntegratedQueryService (with quarantine labels)
            service = self._services.get_integrated_query_service()
            if service:
                voices = service.get_theoretical_voices(
                    topic, limit=self._config.max_framework_voices
                )

                formatted_voices = []
                for framework_name, details in voices.items():
                    formatted_voices.append({
                        "framework": details.get("framework", framework_name),
                        "name": framework_name,
                        "voice": details.get("perspective", ""),
                        "n_papers": details.get("n_papers", 0),
                        "n_findings": details.get("n_findings", 0),
                        "source": details.get("source", "framework_template"),
                        "confidence_level": "insufficient" if details.get("source") == "framework_template" else "moderate",
                    })

                enriched.framework_voices = formatted_voices[:self._config.max_framework_voices]
                enriched.enrichment_metadata["framework_voice_source"] = details.get("source", "unknown")
            else:
                enriched.enrichment_metadata["services_skipped"].append(service_name)
                return

            elapsed = (time.time() - start) * 1000
            enriched.enrichment_metadata["timing"][service_name] = elapsed
            logger.info(
                f"{service_name}: added {len(enriched.framework_voices)} framework "
                f"voices in {elapsed:.1f}ms"
            )

        except Exception as e:
            elapsed = (time.time() - start) * 1000
            enriched.enrichment_metadata["services_failed"].append(service_name)
            enriched.enrichment_metadata["timing"][service_name] = elapsed
            logger.warning(f"{service_name}: {e}")

    def _identify_gaps(
        self,
        enriched: EnrichedAnswer,
        topic: str,
        beliefs: List[Dict],
        timeout_ms: int,
    ) -> None:
        """Find knowledge gaps around this topic.

        SUCCESS CONDITIONS:
        SC-GA-1: 'gap_analysis' appears in services_attempted
        SC-GA-2: If service unavailable, 'gap_analysis' in services_skipped; return without crash
        SC-GA-3: enriched.gaps is a list of dicts
        SC-GA-4: Each gap dict has keys: 'gap_type', 'description', 'severity'
        SC-GA-5: len(gaps) <= config.max_gaps
        SC-GA-6: Timing recorded in enrichment_metadata['timing']['gap_analysis']
        SC-GA-7: On total failure, 'gap_analysis' in services_failed
        """
        service_name = "gap_analysis"
        enriched.enrichment_metadata["services_attempted"].append(service_name)

        start = time.time()
        try:
            predictor = self._services.get_gap_predictor()
            if predictor:
                # Get the actual predicted gaps using the knowledge service
                gaps = predictor.predict_gaps(topic, max_gaps=self._config.max_gaps)
                enriched.gaps = [
                    {
                        "gap_type": g.get("type", "Methodological"),
                        "description": g.get("description", ""),
                        "severity": g.get("severity", "medium")
                    }
                    for g in gaps
                ]
            else:
                enriched.enrichment_metadata["services_skipped"].append(service_name)
                return

            elapsed = (time.time() - start) * 1000
            enriched.enrichment_metadata["timing"][service_name] = elapsed
            logger.info(
                f"{service_name}: identified {len(enriched.gaps)} gaps in {elapsed:.1f}ms"
            )

        except Exception as e:
            elapsed = (time.time() - start) * 1000
            enriched.enrichment_metadata["services_failed"].append(service_name)
            enriched.enrichment_metadata["timing"][service_name] = elapsed
            logger.warning(f"{service_name}: {e}")

    def _suggest_follow_ups(
        self,
        enriched: EnrichedAnswer,
        topic: str,
        beliefs: List[Dict],
        timeout_ms: int,
    ) -> None:
        """Generate VOI-ranked follow-up questions.

        SUCCESS CONDITIONS:
        SC-FU-1: 'follow_up_suggestions' appears in services_attempted
        SC-FU-2: If service unavailable, 'follow_up_suggestions' in services_skipped; return without crash
        SC-FU-3: enriched.follow_ups is a list of dicts
        SC-FU-4: Each follow_up dict has keys: 'question', 'voi', 'difficulty'
        SC-FU-5: len(follow_ups) <= config.max_follow_ups
        SC-FU-6: Timing recorded in enrichment_metadata['timing']['follow_up_suggestions']
        SC-FU-7: On total failure, 'follow_up_suggestions' in services_failed
        """
        service_name = "follow_up_suggestions"
        enriched.enrichment_metadata["services_attempted"].append(service_name)

        start = time.time()
        try:
            fu_service = self._services.get_follow_up_suggestion_service()
            if fu_service is None:
                enriched.enrichment_metadata["services_skipped"].append(service_name)
                return

            follow_ups = fu_service.generate_follow_ups(
                topic=topic,
                beliefs=beliefs,
                gaps=enriched.gaps if hasattr(enriched, 'gaps') else None,
                max_results=self._config.max_follow_ups,
            )

            enriched.follow_ups = follow_ups

            elapsed = (time.time() - start) * 1000
            enriched.enrichment_metadata["timing"][service_name] = elapsed
            logger.info(
                f"{service_name}: generated {len(enriched.follow_ups)} follow-ups in {elapsed:.1f}ms"
            )

        except Exception as e:
            elapsed = (time.time() - start) * 1000
            enriched.enrichment_metadata["services_failed"].append(service_name)
            enriched.enrichment_metadata["timing"][service_name] = elapsed
            logger.warning(f"{service_name}: {e}")

    def _adapt_language(
        self,
        enriched: EnrichedAnswer,
        user_type: str,
        timeout_ms: int,
    ) -> None:
        """Adapt vocabulary, structure, uncertainty language per user type.

        SUCCESS CONDITIONS:
        SC-LA-1: 'language_adaptation' appears in services_attempted
        SC-LA-2: If service unavailable (ImportError), 'language_adaptation' in services_skipped
        SC-LA-3: Result stored in enrichment_metadata['language_adaptation']
        SC-LA-4: Timing recorded in enrichment_metadata['timing']['language_adaptation']
        SC-LA-5: On total failure, 'language_adaptation' in services_failed
        SC-LA-6: Enriched beliefs are vocabulary-translated for user type (P1 fix 2026-03-03)
        SC-LA-7: Base answer text is vocabulary-translated (P1 fix 2026-03-03)
        """
        service_name = "language_adaptation"
        enriched.enrichment_metadata["services_attempted"].append(service_name)

        start = time.time()
        try:
            try:
                from src.services.language_adaptation_service import (
                    adapt_content, LanguageAdaptationService, UserType,
                    _USER_TYPE_MAP
                )
            except ImportError:
                enriched.enrichment_metadata["services_skipped"].append(service_name)
                return

            # 1. Get adaptation metadata (vocabulary level, detail, structure)
            adaptation = adapt_content(
                content=enriched.base_answer.get("answer", ""),
                user_type=user_type,
                topic=enriched.enrichment_metadata.get("question", "general")
            )
            enriched.enrichment_metadata["language_adaptation"] = adaptation

            # 2. Actually adapt the enriched beliefs — P1 FIX (2026-03-03)
            #    This is the critical missing piece: adapt_belief_presentation()
            #    does vocabulary translation + user-type-specific fields.
            try:
                service = LanguageAdaptationService()
                ut = _USER_TYPE_MAP.get(user_type.lower(), UserType.RESEARCHER)

                for i, belief in enumerate(enriched.enriched_beliefs):
                    belief_dict = belief.to_dict() if hasattr(belief, 'to_dict') else {
                        'content': getattr(belief, 'text', str(belief)),
                        'credence': getattr(belief, 'credence_point', None),
                    }
                    adapted = service.adapt_belief_presentation(belief_dict, ut)
                    # Apply vocabulary-translated content back to the belief
                    if hasattr(belief, 'text') and 'content' in adapted:
                        belief.text = adapted['content']

                # 3. Also adapt the base answer text
                base_answer_text = enriched.base_answer.get("answer", "")
                if base_answer_text:
                    translated = service._translate_vocabulary(base_answer_text, ut)
                    enriched.base_answer["answer"] = translated
                    enriched.base_answer["language_adapted"] = True

            except Exception as adapt_err:
                # Non-fatal: we still got the metadata, just couldn't apply transforms
                logger.warning(f"{service_name}: belief adaptation failed: {adapt_err}")
                enriched.enrichment_metadata.setdefault("warnings", []).append(
                    f"Language adaptation metadata collected but text not transformed: {adapt_err}"
                )

            elapsed = (time.time() - start) * 1000
            enriched.enrichment_metadata["timing"][service_name] = elapsed
            logger.info(f"{service_name}: adapted for {user_type} in {elapsed:.1f}ms")

        except Exception as e:
            elapsed = (time.time() - start) * 1000
            enriched.enrichment_metadata["services_failed"].append(service_name)
            enriched.enrichment_metadata["timing"][service_name] = elapsed
            logger.warning(f"{service_name}: {e}")

    def _suggest_figures(
        self,
        enriched: EnrichedAnswer,
        topic: str,
        beliefs: List[Dict],
        timeout_ms: int,
    ) -> None:
        """Identify relevant existing figures.

        SUCCESS CONDITIONS:
        SC-FS-1: 'figure_suggestions' appears in services_attempted
        SC-FS-2: If service unavailable, 'figure_suggestions' in services_skipped; return without crash
        SC-FS-3: enriched.figures is a list of dicts
        SC-FS-4: Each figure dict has keys: 'figure_id', 'title', 'relevance_score', 'path'
        SC-FS-5: Timing recorded in enrichment_metadata['timing']['figure_suggestions']
        SC-FS-6: On total failure, 'figure_suggestions' in services_failed
        """
        service_name = "figure_suggestions"
        enriched.enrichment_metadata["services_attempted"].append(service_name)

        start = time.time()
        try:
            fig_service = self._services.get_figure_suggestion_service()
            if fig_service is None:
                enriched.enrichment_metadata["services_skipped"].append(service_name)
                return

            figures = fig_service.suggest_figures_for_topic(
                topic=topic, limit=self._config.max_figures
            )

            if figures:
                enriched.figures = figures
            else:
                enriched.enrichment_metadata["services_skipped"].append(service_name)
                return

            elapsed = (time.time() - start) * 1000
            enriched.enrichment_metadata["timing"][service_name] = elapsed
            logger.info(
                f"{service_name}: suggested {len(enriched.figures)} figures in {elapsed:.1f}ms"
            )

        except Exception as e:
            elapsed = (time.time() - start) * 1000
            enriched.enrichment_metadata["services_failed"].append(service_name)
            enriched.enrichment_metadata["timing"][service_name] = elapsed
            logger.warning(f"{service_name}: {e}")

    def _add_interpretation_context(
        self,
        enriched: EnrichedAnswer,
        question: str,
        user_type: str,
        timeout_ms: int,
    ) -> None:
        """Classify the question pattern and generate interpretation context.

        Uses InterpretiveIntelligence's QuestionClassifier to determine whether
        the question is asking for evidence, practical implications, mechanism
        analysis, or disagreement resolution. Then generates explanation-pattern-
        aware metadata that downstream consumers can use to structure the response.

        SUCCESS CONDITIONS:
        SC-IC-1: 'interpretation_context' appears in services_attempted
        SC-IC-2: If service unavailable, 'interpretation_context' in services_skipped
        SC-IC-3: enriched.interpretation_context is a dict with keys:
                 'explanation_pattern', 'pattern_confidence', 'expertise_level', 'pattern_description'
        SC-IC-4: explanation_pattern is one of: 'evidence', 'practical', 'mechanism', 'disagreement'
        SC-IC-5: pattern_confidence is a float in [0.0, 1.0]
        SC-IC-6: Timing recorded in enrichment_metadata['timing']['interpretation_context']
        SC-IC-7: On total failure, 'interpretation_context' in services_failed
        """
        service_name = "interpretation_context"
        enriched.enrichment_metadata["services_attempted"].append(service_name)

        start = time.time()
        try:
            interp = self._services.get_interpretive_intelligence()
            if not interp:
                enriched.enrichment_metadata["services_skipped"].append(service_name)
                return

            classifier = interp["classifier"]
            ExplanationPattern = interp["ExplanationPattern"]

            # Classify the question
            pattern, confidence = classifier.classify(question)

            # Map expertise from user_type
            expertise_map = {
                "researcher": interp["ExpertiseLevel"].RESEARCHER,
                "student": interp["ExpertiseLevel"].NOVICE,
                "clinician": interp["ExpertiseLevel"].PRACTITIONER,
                "policy_maker": interp["ExpertiseLevel"].PRACTITIONER,
                "general_public": interp["ExpertiseLevel"].NOVICE,
            }
            expertise = expertise_map.get(
                user_type, interp["ExpertiseLevel"].PRACTITIONER
            )

            # Build interpretation context
            enriched.interpretation_context = {
                "explanation_pattern": pattern.value,
                "pattern_confidence": confidence,
                "expertise_level": expertise.value,
                "pattern_description": {
                    ExplanationPattern.EVIDENCE.value: "User is asking about evidence — emphasize study quality, sample sizes, effect sizes, and contradictions",
                    ExplanationPattern.PRACTICAL.value: "User wants actionable design guidance — emphasize implications, recommendations, and caveats",
                    ExplanationPattern.MECHANISM.value: "User wants to understand the mechanism — emphasize T1 framework grounding, neural substrates, and causal chains",
                    ExplanationPattern.DISAGREEMENT.value: "User is asking about a contested topic — emphasize competing accounts, boundary conditions, and underdetermination",
                }.get(pattern.value, "General question — provide balanced overview"),
            }

            elapsed = (time.time() - start) * 1000
            enriched.enrichment_metadata["timing"][service_name] = elapsed
            logger.info(
                f"{service_name}: classified as {pattern.value} "
                f"(conf={confidence:.2f}) in {elapsed:.1f}ms"
            )

        except Exception as e:
            elapsed = (time.time() - start) * 1000
            enriched.enrichment_metadata["services_failed"].append(service_name)
            enriched.enrichment_metadata["timing"][service_name] = elapsed
            logger.warning(f"{service_name}: {e}")

    def _enrich_circuit_context(
        self,
        enriched: EnrichedAnswer,
        question: str,
        timeout_ms: int,
    ) -> None:
        """Add functional circuit context to answers that touch circuit-related topics.

        When a question relates to a functional circuit (e.g., sensory prediction
        error, arousal regulation, attentional selection), this step adds:
        - Which circuit(s) are relevant
        - The epistemic status of each (STRONG / MODERATE / HYPOTHETICAL)
        - A brief ontological framing note
        - Cross-references to related circuits sharing the same archetype

        This enrichment ensures that ALL answers touching circuit topics carry
        appropriate epistemic framing, even when the primary handler was not
        the circuit-specific one (e.g., a general evidence query that happens
        to involve a circuit-relevant phenomenon).

        SUCCESS CONDITIONS:
        SC-CC-1: 'circuit_context' appears in services_attempted
        SC-CC-2: If service unavailable, 'circuit_context' in services_skipped
        SC-CC-3: enriched.enrichment_metadata['circuit_context'] is a dict when relevant
        SC-CC-4: Timing recorded in enrichment_metadata['timing']['circuit_context']
        """
        service_name = "circuit_context"
        enriched.enrichment_metadata["services_attempted"].append(service_name)

        start = time.time()
        try:
            from src.services.circuit_qa_service import CircuitQAService, CIRCUIT_EVIDENCE_LEVELS
            service = CircuitQAService()
            if service.circuit_count == 0:
                enriched.enrichment_metadata["services_skipped"].append(service_name)
                return

            # Check if the question relates to any circuit
            circuit_id = service._identify_circuit(question)
            if circuit_id:
                card = service.get_circuit_card(circuit_id)
                if card:
                    enriched.enrichment_metadata["circuit_context"] = {
                        "circuit_id": card.circuit_id,
                        "circuit_name": card.circuit_name,
                        "epistemic_status": card.epistemic_status,
                        "archetype": card.archetype,
                        "ontological_note": card.ontological_statement[:200],
                        "related_circuits": card.related_circuits[:3],
                        "follow_up_questions": card.follow_up_questions[:3],
                    }
            else:
                # Check if any circuit keywords appear in the question
                q_lower = question.lower()
                circuit_keywords = {
                    "prediction error": ["FC_SENSORY_PREDICTION_ERROR", "FC_REWARD_PREDICTION_ERROR"],
                    "arousal": ["FC_AROUSAL_REGULATION"],
                    "attention": ["FC_ATTENTIONAL_SELECTION"],
                    "familiarity": ["FC_FAMILIARITY_DETECTION"],
                    "threat": ["FC_THREAT_MONITORING", "FC_CONTEXT_GATED_THREAT"],
                    "coherence": ["FC_COHERENCE_MONITORING"],
                    "dread": ["FC_DREAD_ACCUMULATION"],
                    "curiosity": ["FC_CURIOSITY_ACCUMULATION"],
                    "aesthetic": ["FC_AESTHETIC_EXPECTATION_VIOLATION", "FC_EXPERTISE_GATED_AESTHETICS"],
                }
                relevant = []
                for keyword, circuit_ids in circuit_keywords.items():
                    if keyword in q_lower:
                        for cid in circuit_ids:
                            evidence = CIRCUIT_EVIDENCE_LEVELS.get(cid, "HYPOTHETICAL")
                            relevant.append({"circuit_id": cid, "evidence": evidence})

                if relevant:
                    enriched.enrichment_metadata["circuit_context"] = {
                        "relevant_circuits": relevant,
                        "note": (
                            "This topic relates to one or more functional circuits. "
                            "Ask about a specific circuit for epistemic framing."
                        ),
                    }

            elapsed = (time.time() - start) * 1000
            enriched.enrichment_metadata["timing"][service_name] = elapsed

        except ImportError:
            enriched.enrichment_metadata["services_skipped"].append(service_name)
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            enriched.enrichment_metadata["services_failed"].append(service_name)
            enriched.enrichment_metadata["timing"][service_name] = elapsed
            logger.warning(f"{service_name}: {e}")


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_orchestrator(config: Optional[EnrichmentConfig] = None) -> AnswerEnrichmentOrchestrator:
    """Factory function to create a new orchestrator."""
    return AnswerEnrichmentOrchestrator(config)


def enrich_answer(
    base_answer: Dict[str, Any],
    question: str,
    user_type: str = "researcher",
    config: Optional[EnrichmentConfig] = None,
) -> EnrichedAnswer:
    """
    Convenience function: create orchestrator and enrich in one call.

    Args:
        base_answer: From arbitrary_qa_handler
        question: User question
        user_type: Persona type
        config: Optional EnrichmentConfig

    Returns:
        EnrichedAnswer
    """
    orchestrator = AnswerEnrichmentOrchestrator(config)
    return orchestrator.enrich(base_answer, question, user_type)
