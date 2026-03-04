#!/usr/bin/env python3
"""
End-to-End Reachability Audit (Health Test)
===========================================
Tests that all services/modules referenced in the codebase actually resolve.
Catches the "90% built, 10% never wired" pattern before it reaches production.

Can be run as:
  pytest tests/test_reachability_audit.py -v
  python3 tests/test_reachability_audit.py  (standalone)

Part of the nightly health check suite.
"""

import sys
import json
import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# =====================================================================
# PROBE 1: ServiceRegistry — all claimed services must import
# =====================================================================

class TestServiceRegistry:
    """Every service the enrichment ServiceRegistry claims to provide must import."""

    def test_credence_intervals(self):
        from src.services import credence_intervals
        assert credence_intervals is not None

    def test_warrant_strength(self):
        from src.services import warrant_strength
        assert warrant_strength is not None

    def test_confounder_risk_checker(self):
        from src.qa.confounder_risk_checker import ConfounderRiskChecker
        assert ConfounderRiskChecker is not None

    def test_gap_predictor(self):
        from src.services.gap_predictor import GapPredictor
        assert GapPredictor is not None

    def test_integrated_query_service(self):
        from src.services.integrated_query_service import IntegratedQueryService
        assert IntegratedQueryService is not None

    def test_recommendation_loop(self):
        from src.services.recommendation_loop import RecommendationLoopService
        assert RecommendationLoopService is not None

    def test_follow_up_suggestion_service(self):
        from src.services.follow_up_suggestion_service import FollowUpSuggestionService
        assert FollowUpSuggestionService is not None

    def test_theory_guide_service(self):
        from src.services.theory_guide_service import TheoryGuideService
        assert TheoryGuideService is not None

    def test_knowledge_catalog(self):
        from src.services.knowledge_catalog import KnowledgeCatalog
        assert KnowledgeCatalog is not None

    def test_interpretive_intelligence(self):
        from src.services.interpretive_intelligence import QuestionClassifier
        assert QuestionClassifier is not None

    def test_t3_interp_bridge(self):
        from src.services.t3_interp_bridge import T3InterpBridge
        assert T3InterpBridge is not None


# =====================================================================
# PROBE 2: Paper Integration module-level imports
# =====================================================================

class TestPaperIntegrationImports:
    """All 11 module-level imports in paper_integration/orchestrator.py must resolve."""

    def test_outcome_resolver(self):
        from lib.outcome_resolver import resolve_outcome
        assert resolve_outcome is not None

    def test_web_of_belief(self):
        from src.services.web_of_belief import WebOfBelief, Belief
        assert WebOfBelief is not None

    def test_extraction_to_web(self):
        from src.services.extraction_to_web import integrate_extraction
        assert integrate_extraction is not None

    def test_incremental_bn(self):
        from src.services.incremental_bn import BetaBernoulliEdge
        assert BetaBernoulliEdge is not None

    def test_epistemic_orchestrator(self):
        from src.services.epistemic_orchestrator import EpistemicOrchestrator
        assert EpistemicOrchestrator is not None

    def test_epistemic_causal_bridge(self):
        from src.services.epistemic_causal_bridge import EpistemicCausalBridge
        assert EpistemicCausalBridge is not None

    def test_epistemic_projection(self):
        from src.services.epistemic_projection import project_with_diagnostic
        assert project_with_diagnostic is not None

    def test_social_epistemology(self):
        from src.services.social_epistemology import CommunityRegistry
        assert CommunityRegistry is not None

    def test_discovery_funnel(self):
        from src.services.discovery_funnel import DiscoveryFunnelService
        assert DiscoveryFunnelService is not None

    def test_provenance(self):
        from src.models.provenance import Provenance, Source
        assert Provenance is not None

    def test_scalable_coherence(self):
        from src.services.scalable_coherence import CoherenceManager
        assert CoherenceManager is not None

    def test_pipeline_qa_integration(self):
        from src.services.pipeline_qa_integration import assess_paper_beliefs
        assert assess_paper_beliefs is not None

    def test_notification_service(self):
        from src.services.notification_service import notify, NotificationType
        assert notify is not None


# =====================================================================
# PROBE 3: Enrichment step critical imports
# =====================================================================

class TestEnrichmentStepWiring:
    """Enrichment steps should either import or have documented fallback."""

    @pytest.mark.xfail(reason="Module never created — replaced by figure_suggestion_service")
    def test_fig_suggester(self):
        from src.services.academic_presentation_service import fig_suggester

    def test_follow_up_suggestion_service(self):
        from src.services.follow_up_suggestion_service import FollowUpSuggestionService
        assert FollowUpSuggestionService is not None

    def test_figure_suggestion_service(self):
        from src.services.figure_suggestion_service import FigureSuggestionService
        assert FigureSuggestionService is not None

    def test_warrant_strength_with_enums(self):
        from src.services.warrant_strength import compute_omega_sev, DesignType, PublicationType
        assert DesignType.STANDARD_RCT is not None  # Not DesignType.RCT (P1 bug)
        assert PublicationType.PEER_REVIEWED is not None

    def test_credence_intervals(self):
        from src.services import credence_intervals
        assert credence_intervals is not None


# =====================================================================
# PROBE 4: Nightly pipeline stage dependencies
# =====================================================================

class TestNightlyPipelineDeps:
    """Every nightly pipeline stage dependency should be importable."""

    def test_extraction_field_validator(self):
        from src.qa.extraction_field_validator import ExtractionFieldValidator
        assert ExtractionFieldValidator is not None

    def test_system_setup(self):
        from src.services.system_setup import SystemSetup
        assert SystemSetup is not None

    def test_overseer_service(self):
        from src.services.overseer import OverseerService
        assert OverseerService is not None

    def test_t3_adapter(self):
        from src.services.t3_integration import T3Adapter
        assert T3Adapter is not None

    def test_t3_interp_bridge(self):
        from src.services.t3_interp_bridge import T3InterpBridge
        assert T3InterpBridge is not None

    def test_interpretation_space(self):
        from src.services.interpretation_space_suggestions import InterpretationSpaceSuggestionsManager
        assert InterpretationSpaceSuggestionsManager is not None

    def test_gap_predictor(self):
        from src.services.gap_predictor import GapPredictor
        assert GapPredictor is not None

    def test_mv_builder(self):
        from src.qa.mv_builder import MaterializedViewBuilder
        assert MaterializedViewBuilder is not None

    def test_incremental_updater(self):
        from src.qa.incremental_updater import IncrementalUpdater
        assert IncrementalUpdater is not None

    @pytest.mark.skipif(
        not __import__("importlib").util.find_spec("google"),
        reason="google-generativeai not installed"
    )
    def test_molecular_qa_precomputer(self):
        from src.qa.precompute_pipeline import MolecularQAPrecomputer
        assert MolecularQAPrecomputer is not None

    def test_voi_scoring(self):
        from src.cmr.voi_scoring import aggregate_paper_voi
        assert aggregate_paper_voi is not None


# =====================================================================
# PROBE 5: QA Router handler chain
# =====================================================================

class TestQARouterChain:
    """The full QA router handler chain must resolve."""

    def test_arbitrary_qa_handler(self):
        from src.services.arbitrary_qa_handler import ArbitraryQAHandler
        assert ArbitraryQAHandler is not None

    def test_read_next_engine(self):
        from src.services.read_next_engine import ReadNextEngine
        assert ReadNextEngine is not None

    def test_argument_query_handler(self):
        from src.argument.qa_handlers import ArgumentQueryHandler
        assert ArgumentQueryHandler is not None

    def test_molecule_aware_router(self):
        from src.qa.router import MoleculeAwareRouter
        assert MoleculeAwareRouter is not None

    def test_molecule_registry(self):
        from src.qa.molecules.registry import MoleculeRegistry
        assert MoleculeRegistry is not None


# =====================================================================
# PROBE 6: Module existence (file on disk)
# =====================================================================

class TestModuleExistence:
    """Referenced modules should exist as files on disk."""

    @pytest.fixture
    def services_dir(self):
        return PROJECT_ROOT / "src" / "services"

    @pytest.fixture
    def all_dirs(self):
        return [
            PROJECT_ROOT / "src" / "services",
            PROJECT_ROOT / "src" / "qa",
            PROJECT_ROOT / "src" / "models",
            PROJECT_ROOT / "src" / "argument",
            PROJECT_ROOT / "src" / "cmr",
            PROJECT_ROOT / "lib",
        ]

    def _module_exists(self, mod_name, all_dirs):
        for d in all_dirs:
            if (d / f"{mod_name}.py").exists() or (d / mod_name).is_dir():
                return True
        return False

    @pytest.mark.xfail(reason="Never created — replaced by figure_suggestion_service")
    def test_academic_presentation_service_exists(self, all_dirs):
        assert self._module_exists("academic_presentation_service", all_dirs)

    def test_follow_up_suggestion_service_exists(self, all_dirs):
        assert self._module_exists("follow_up_suggestion_service", all_dirs)

    def test_figure_suggestion_service_exists(self, all_dirs):
        assert self._module_exists("figure_suggestion_service", all_dirs)

    def test_critical_modules_exist(self, all_dirs):
        """All critical service modules must exist on disk."""
        critical = [
            "credence_intervals", "warrant_strength", "gap_predictor",
            "integrated_query_service", "recommendation_loop",
            "theory_guide_service", "knowledge_catalog",
            "interpretive_intelligence", "overseer", "system_setup",
            "web_of_belief", "extraction_to_web",
        ]
        missing = [m for m in critical if not self._module_exists(m, all_dirs)]
        assert not missing, f"Missing critical modules: {missing}"


# =====================================================================
# Standalone runner
# =====================================================================

if __name__ == "__main__":
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"],
        cwd=str(PROJECT_ROOT),
    )
    sys.exit(result.returncode)
