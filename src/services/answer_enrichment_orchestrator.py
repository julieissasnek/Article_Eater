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
    timeout_per_service_ms: int = 2000
    global_timeout_ms: int = DEFAULT_GLOBAL_TIMEOUT_MS  # V11: total budget
    max_beliefs_to_enrich: int = 20
    max_framework_voices: int = 3
    max_gaps: int = 5
    max_follow_ups: int = 5


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
    """A single belief with all enrichments applied."""
    text: str
    credence_point: Optional[float] = None
    credence_ci: Optional[Dict[str, float]] = None  # {lower, upper, se}
    warrant_trace: Optional[List[Dict[str, Any]]] = None  # [{component, value}, ...]
    confounder_risk: Optional[str] = None  # "high", "medium", "low"
    confounder_details: Optional[List[str]] = None


@dataclass
class EnrichedAnswer:
    """Full enriched answer with all service outputs."""
    base_answer: Dict[str, Any]  # Original answer from arbitrary_qa_handler
    enriched_beliefs: List[EnrichedBelief] = field(default_factory=list)
    framework_voices: List[Dict[str, Any]] = field(default_factory=list)
    gaps: List[Dict[str, Any]] = field(default_factory=list)
    follow_ups: List[Dict[str, str]] = field(default_factory=list)
    figures: List[Dict[str, Any]] = field(default_factory=list)
    interpretation_context: Optional[Dict[str, Any]] = None  # Step 9 output
    user_type: str = "researcher"
    enrichment_metadata: Dict[str, Any] = field(default_factory=dict)

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
        }

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


# =============================================================================
# SERVICE IMPORTS (LAZY-LOADED)
# =============================================================================

class _ServiceRegistry:
    """Lazy-load all services; graceful degradation if modules missing."""

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

    def enrich(
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
                # Return early — do not enrich ungrounded answers
                return enriched
        except Exception as e:
            logger.warning(f"Grounding gate failed (proceeding with enrichment): {e}")
            enriched.enrichment_metadata["grounding"] = {"error": str(e)}


        # V11 Panel Fix: Steps run in dependency order with budget checks.
        # Dependencies declared in STEP_DEPENDENCIES dict.

        # Step 1: Credence enrichment (no deps)
        if self._config.enable_credence_ci and _check_budget("credence_ci"):
            self._enrich_credence(
                enriched, beliefs, timeout_ms
            )

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
        """Add confidence intervals to each belief."""
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
        """Decompose each belief's credence into warrant contributions."""
        service_name = "warrant_trace"
        enriched.enrichment_metadata["services_attempted"].append(service_name)

        start = time.time()
        try:
            warrant_module = self._services.get_warrant_strength()
            if not warrant_module:
                enriched.enrichment_metadata["services_skipped"].append(service_name)
                return

            for i, belief_dict in enumerate(
                enriched.enriched_beliefs[:self._config.max_beliefs_to_enrich]
            ):
                if (time.time() - start) * 1000 > timeout_ms:
                    logger.warning(
                        f"{service_name}: timeout after {timeout_ms}ms, stopping"
                    )
                    break

                try:
                    # Import the actual warrant computation functions
                    from src.services.warrant_strength import (
                        compute_omega_sev, compute_omega_conf,
                        compute_omega_rep, compute_omega_meta,
                        DesignType, PublicationType,
                    )

                    # Map string design types to DesignType enum
                    _design_map = {
                        "experimental": DesignType.STANDARD_RCT,
                        "rct": DesignType.STANDARD_RCT,
                        "large_rct": DesignType.LARGE_RCT,
                        "quasi_experimental": DesignType.QUASI_EXPERIMENTAL,
                        "within_subjects": DesignType.WITHIN_SUBJECTS,
                        "observational": DesignType.OBSERVATIONAL,
                        "case_study": DesignType.CASE_STUDY,
                        "meta_analysis": DesignType.META_ANALYSIS,
                        "systematic_review": DesignType.SYSTEMATIC_REVIEW,
                    }

                    # Extract design metadata from the belief
                    raw_design = getattr(belief_dict, 'design_type', None) or "observational"
                    design_enum = _design_map.get(
                        raw_design.lower().replace("-", "_").replace(" ", "_"),
                        DesignType.OBSERVATIONAL
                    )
                    sample_n = getattr(belief_dict, 'sample_size', None) or getattr(belief_dict, 'n', None)
                    pre_reg = getattr(belief_dict, 'pre_registered', False)

                    # Compute actual omega components using panel-approved formulas
                    omega_sev = compute_omega_sev(
                        design_type=design_enum,
                        sample_size=int(sample_n) if sample_n else None,
                        pre_registered=pre_reg,
                    )
                    omega_conf = compute_omega_conf(
                        n_uncontrolled_confounds=getattr(belief_dict, 'n_confounds', 1),
                        has_randomization=design_enum in (DesignType.STANDARD_RCT, DesignType.LARGE_RCT),
                    )
                    omega_rep = compute_omega_rep(
                        n_independent_replications=getattr(belief_dict, 'n_replications', 0),
                    )
                    omega_meta = compute_omega_meta(
                        publication_type=PublicationType.PEER_REVIEWED,
                        is_pre_registered=pre_reg,
                    )

                    # Create warrant trace with real computed values
                    trace = [
                        {"component": "experimental_severity", "omega_sev": round(omega_sev, 3),
                         "design_type": design_enum.value},
                        {"component": "confound_control", "omega_conf": round(omega_conf, 3)},
                        {"component": "replication", "omega_rep": round(omega_rep, 3)},
                        {"component": "publication_meta", "omega_meta": round(omega_meta, 3)},
                    ]

                    belief_dict.warrant_trace = trace
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
        """Flag confounder risks per belief."""
        service_name = "confounder_risk"
        enriched.enrichment_metadata["services_attempted"].append(service_name)

        start = time.time()
        try:
            checker = self._services.get_confounder_risk_checker()
            if not checker:
                enriched.enrichment_metadata["services_skipped"].append(service_name)
                return

            for i, belief_dict in enumerate(
                enriched.enriched_beliefs[:self._config.max_beliefs_to_enrich]
            ):
                if (time.time() - start) * 1000 > timeout_ms:
                    logger.warning(
                        f"{service_name}: timeout after {timeout_ms}ms, stopping"
                    )
                    break

                try:
                    # Check if this is an observational study
                    design_type = beliefs[i].get("design_type", "observational")
                    if "observational" in design_type.lower():
                        belief_dict.confounder_risk = "medium"
                        belief_dict.confounder_details = [
                            "Observational study: cannot rule out confounding",
                            "Consider: selection bias, unmeasured confounds",
                        ]
                    else:
                        belief_dict.confounder_risk = "low"
                        belief_dict.confounder_details = [
                            "Experimental design with randomization",
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
        """Get T1 framework perspectives on the topic."""
        service_name = "framework_voices"
        enriched.enrichment_metadata["services_attempted"].append(service_name)

        start = time.time()
        try:
            # Use integrated_query_service for framework voices
            service = self._services.get_integrated_query_service()
            if service:
                # The service returns a dict mapping framework -> perspective
                voices = service.get_theoretical_voices(topic, limit=self._config.max_framework_voices)
                
                # Format them into the expected structure
                formatted_voices = []
                for framework_name, details in voices.items():
                    formatted_voices.append({
                        "framework": framework_name,
                        "voice": details.get("perspective", ""),
                        "implications": details.get("implications", [])
                    })
                
                enriched.framework_voices = formatted_voices[:self._config.max_framework_voices]
            else:
                enriched.enrichment_metadata["services_skipped"].append(service_name)
                return

            elapsed = (time.time() - start) * 1000
            enriched.enrichment_metadata["timing"][service_name] = elapsed
            logger.info(
                f"{service_name}: added {len(enriched.framework_voices)} framework voices in {elapsed:.1f}ms"
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
        """Find knowledge gaps around this topic."""
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
        """Generate VOI-ranked follow-up questions."""
        service_name = "follow_up_suggestions"
        enriched.enrichment_metadata["services_attempted"].append(service_name)

        start = time.time()
        try:
            # Use the follow-up suggestion service
            follow_up_service = self._services.get_follow_up_suggestion_service()
            if follow_up_service:
                suggestions = follow_up_service.generate_follow_ups(
                    topic=topic,
                    existing_beliefs=beliefs,
                    max_suggestions=self._config.max_follow_ups
                )
                enriched.follow_ups = [
                    {
                        "question": s.get("question", ""),
                        "voi": s.get("voi", 0.0),
                        "difficulty": s.get("difficulty", "unknown"),
                    }
                    for s in suggestions
                ]
            else:
                enriched.enrichment_metadata["services_skipped"].append(service_name)
                return

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
        """Adapt vocabulary, structure, uncertainty language per user type."""
        service_name = "language_adaptation"
        enriched.enrichment_metadata["services_attempted"].append(service_name)

        start = time.time()
        try:
            try:
                from src.services.language_adaptation_service import adapt_content
                adaptation = adapt_content(
                    content=enriched.base_answer.get("answer", ""),
                    user_type=user_type,
                    topic=enriched.enrichment_metadata.get("question", "general")
                )
                enriched.enrichment_metadata["language_adaptation"] = adaptation
            except ImportError:
                enriched.enrichment_metadata["services_skipped"].append(service_name)
                return

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
        """Identify relevant existing figures."""
        service_name = "figure_suggestions"
        enriched.enrichment_metadata["services_attempted"].append(service_name)

        start = time.time()
        try:
            # Use academic presentation service to find relevant figures
            try:
                from src.services.academic_presentation_service.fig_suggester import suggest_figures_for_topic
                suggestions = suggest_figures_for_topic(topic, limit=self._config.max_figures)
                enriched.figures = [
                    {
                        "figure_id": fig.get("id", ""),
                        "title": fig.get("caption", ""),
                        "relevance_score": fig.get("relevance", 0.5),
                        "path": fig.get("path", "")
                    }
                    for fig in suggestions
                ]
            except ImportError:
                # Fallback to theory guide service if the precise presentation service isn't there
                guide = self._services.get_theory_guide_service()
                if guide and hasattr(guide, "get_figures_for_topic"):
                    figures = guide.get_figures_for_topic(topic)
                    enriched.figures = [
                        {
                            "figure_id": getattr(f, "id", ""),
                            "title": getattr(f, "caption", ""),
                            "relevance_score": getattr(f, "relevance", 0.8),
                            "path": getattr(f, "path", "")
                        }
                        for f in figures[:self._config.max_figures]
                    ]
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

        This turns the interpretation layer into a callable service that enriches
        every QA answer with structured explanation context.
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
