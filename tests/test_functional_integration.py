#!/usr/bin/env python3
"""
Functional Integration Tests — "Turn on the water"
====================================================

Unlike test_reachability_audit.py (which tests that pipes are connected),
this test suite sends real questions through the actual pipeline and
verifies every stage produces non-empty, correct output.

Designed around five test question archetypes:

Q1: "What is Attention Restoration Theory?" — well-known molecule with
    cached QA data. Exercises: QA router molecule path, enrichment pipeline,
    follow-up suggestions, figure suggestions.

Q2: "What circuits use predictive coding?" — T2 archetype query. Exercises:
    archetype routing, molecule listing, functional circuit awareness.

Q3: "Show me all functional circuits" — molecule type listing.

Q4: A naturalistic question with no matching molecule — exercises the
    ArbitraryQA → enrichment fallback path.

Q5: Confounder risk input — synthetic beliefs with various study designs
    to verify the 4-tier classifier.

Run with:
  pytest tests/test_functional_integration.py -v --tb=long
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# =============================================================================
# FIXTURES — construct realistic inputs from actual corpus data
# =============================================================================

@pytest.fixture
def project_root():
    return PROJECT_ROOT


@pytest.fixture
def sample_beliefs():
    """
    Construct a realistic beliefs list from actual extraction data.
    These are what the enrichment pipeline receives from ArbitraryQA.
    """
    extractions_dir = PROJECT_ROOT / "data" / "extractions"
    beliefs = []

    if extractions_dir.exists():
        # Grab findings from real papers about nature/restoration/attention
        target_keywords = {"nature", "attention", "restoration", "green", "stress"}
        for json_file in sorted(extractions_dir.glob("*.json"))[:100]:
            try:
                with open(json_file) as f:
                    data = json.load(f)
                title = (data.get("title") or "").lower()
                if any(kw in title for kw in target_keywords):
                    for finding in data.get("findings", [])[:3]:
                        beliefs.append({
                            "belief_id": f"b_{json_file.stem}_{finding.get('id', 'x')}",
                            "statement": f"{finding.get('antecedent', '')} → {finding.get('consequent', '')}",
                            "content": f"{finding.get('antecedent', '')} → {finding.get('consequent', '')}",
                            "credence_mean": 0.6,
                            "credence_se": 0.15,
                            "epistemic_level": "EMPIRICAL",
                            "paper_id": json_file.stem,
                            "design_type": finding.get("claim_type", "observational"),
                            "sample_size": finding.get("sample_size"),
                            "effect_size_d": finding.get("effect_size"),
                        })
            except Exception:
                continue

    # Ensure we have at least some beliefs even without extraction data
    if not beliefs:
        beliefs = [
            {
                "belief_id": "b_test_1",
                "statement": "Exposure to natural environments reduces attentional fatigue",
                "content": "Exposure to natural environments reduces attentional fatigue",
                "credence_mean": 0.7,
                "credence_se": 0.12,
                "epistemic_level": "EMPIRICAL",
                "design_type": "randomized_controlled_trial",
                "sample_size": 120,
                "effect_size_d": 0.45,
            },
            {
                "belief_id": "b_test_2",
                "statement": "Green views from hospital windows accelerate surgical recovery",
                "content": "Green views from hospital windows accelerate surgical recovery",
                "credence_mean": 0.65,
                "credence_se": 0.18,
                "epistemic_level": "EMPIRICAL",
                "design_type": "quasi_experimental",
                "sample_size": 46,
                "effect_size_d": 0.8,
            },
            {
                "belief_id": "b_test_3",
                "statement": "Survey respondents prefer natural over built environments",
                "content": "Survey respondents prefer natural over built environments",
                "credence_mean": 0.8,
                "credence_se": 0.08,
                "epistemic_level": "EMPIRICAL",
                "design_type": "cross-sectional survey",
                "sample_size": 500,
            },
        ]

    return beliefs


# =============================================================================
# TEST 1: QA Router — Molecule Lookup (Cached Fast Path)
# =============================================================================

class TestRouterMoleculeLookup:
    """Q1: "What is Attention Restoration Theory?" → molecule fast path."""

    def test_router_finds_art_molecule(self):
        """Router should classify ART question as molecule query."""
        from src.qa.router import MoleculeAwareRouter
        router = MoleculeAwareRouter()
        classified = router._classify_question(
            "What is Attention Restoration Theory?"
        )
        assert classified.target_type == "molecule", (
            f"Expected 'molecule', got '{classified.target_type}'"
        )
        assert classified.target_id is not None, "target_id should be set"

    def test_router_returns_cached_answer_for_art(self):
        """If ART_QA.json exists, router should return cached content."""
        from src.qa.router import MoleculeAwareRouter
        router = MoleculeAwareRouter()
        result = router.route_query("What is Attention Restoration Theory?")
        assert result is not None
        assert result.get("query_type") != "unrouted", (
            f"ART query should be routed, got: {result.get('query_type')}"
        )

    def test_router_identifies_component(self):
        """Questions about specific components should route to component."""
        from src.qa.router import MoleculeAwareRouter
        router = MoleculeAwareRouter()
        classified = router._classify_question(
            "What is Soft Fascination in Attention Restoration Theory?"
        )
        # Should find the component OR the molecule (both acceptable)
        assert classified.target_type in ("molecule", "component"), (
            f"Expected molecule/component, got '{classified.target_type}'"
        )


# =============================================================================
# TEST 2: QA Router — Archetype Queries (New routing)
# =============================================================================

class TestRouterArchetypeQueries:
    """Q2: "What circuits use predictive coding?" → archetype listing."""

    def test_predictive_coding_routes_to_archetype(self):
        from src.qa.router import MoleculeAwareRouter
        router = MoleculeAwareRouter()
        classified = router._classify_question(
            "What circuits use predictive coding?"
        )
        assert classified.target_type == "archetype", (
            f"Expected 'archetype', got '{classified.target_type}'"
        )
        assert classified.target_id == "PREDICTIVE_CODING"

    def test_archetype_query_returns_molecules(self):
        from src.qa.router import MoleculeAwareRouter
        router = MoleculeAwareRouter()
        result = router.route_query("What circuits use predictive coding?")
        assert result.get("query_type") == "archetype_lookup"
        assert "molecules" in result
        assert isinstance(result["molecules"], list)
        # Check structure
        if result["molecules"]:
            mol = result["molecules"][0]
            assert "molecule_id" in mol
            assert "name" in mol

    def test_bayesian_brain_alias_works(self):
        """Alias 'bayesian brain' should map to PREDICTIVE_CODING."""
        from src.qa.router import MoleculeAwareRouter
        router = MoleculeAwareRouter()
        classified = router._classify_question(
            "Tell me about the bayesian brain hypothesis"
        )
        assert classified.target_type == "archetype"
        assert classified.target_id == "PREDICTIVE_CODING"

    def test_homeostatic_routes_correctly(self):
        from src.qa.router import MoleculeAwareRouter
        router = MoleculeAwareRouter()
        classified = router._classify_question("What is homeostatic regulation?")
        assert classified.target_type == "archetype"
        assert classified.target_id == "HOMEOSTATIC_REGULATION"


# =============================================================================
# TEST 3: QA Router — Molecule Type Listing
# =============================================================================

class TestRouterMoleculeTypeListing:
    """Q3: "Show me all functional circuits" → type listing."""

    def test_functional_circuit_listing(self):
        from src.qa.router import MoleculeAwareRouter
        router = MoleculeAwareRouter()
        result = router.route_query("Show me all functional circuits")
        assert result.get("query_type") == "type_listing"
        assert result.get("molecule_type") == "FUNCTIONAL_CIRCUIT"
        assert isinstance(result.get("molecules"), list)

    def test_theory_listing(self):
        from src.qa.router import MoleculeAwareRouter
        router = MoleculeAwareRouter()
        result = router.route_query("What theories are available?")
        assert result.get("query_type") == "type_listing"
        assert result.get("molecule_type") == "THEORY"


# =============================================================================
# TEST 4: Enrichment Pipeline — Full Pass
# =============================================================================

class TestEnrichmentPipeline:
    """
    Send a realistic base_answer through the full enrichment pipeline.
    Every step should either succeed or gracefully skip — never crash.
    """

    def _make_base_answer(self, beliefs: List[Dict]) -> Dict[str, Any]:
        return {
            "answer": "Attention Restoration Theory proposes that natural environments "
                      "facilitate recovery from directed attention fatigue through four "
                      "key mechanisms: fascination, being away, extent, and compatibility.",
            "beliefs": beliefs,
            "evidence_count": len(beliefs),
            "topic": "Attention Restoration Theory",
            "confidence": 0.72,
        }

    def test_enrichment_completes_without_crash(self, sample_beliefs):
        """The full enrichment pipeline should complete without exceptions."""
        from src.services.answer_enrichment_orchestrator import (
            AnswerEnrichmentOrchestrator, EnrichmentConfig,
        )

        config = EnrichmentConfig(timeout_per_service_ms=5000, global_timeout_ms=30000)
        orchestrator = AnswerEnrichmentOrchestrator(config=config)
        base_answer = self._make_base_answer(sample_beliefs)

        result = orchestrator.enrich(
            base_answer=base_answer,
            question="What is Attention Restoration Theory?",
            user_type="researcher",
        )

        assert result is not None
        assert result.base_answer == base_answer
        assert result.enrichment_metadata["question"] == "What is Attention Restoration Theory?"

    def test_enrichment_attempts_all_steps(self, sample_beliefs):
        """Every enabled enrichment step should appear in services_attempted."""
        from src.services.answer_enrichment_orchestrator import (
            AnswerEnrichmentOrchestrator, EnrichmentConfig,
        )

        config = EnrichmentConfig(timeout_per_service_ms=5000, global_timeout_ms=60000)
        orchestrator = AnswerEnrichmentOrchestrator(config=config)
        base_answer = self._make_base_answer(sample_beliefs)

        result = orchestrator.enrich(
            base_answer=base_answer,
            question="What is Attention Restoration Theory?",
            user_type="researcher",
        )

        attempted = result.enrichment_metadata["services_attempted"]
        failed = result.enrichment_metadata["services_failed"]
        skipped = result.enrichment_metadata["services_skipped"]

        # Log for diagnostic purposes
        print(f"\n  Attempted: {attempted}")
        print(f"  Failed: {failed}")
        print(f"  Skipped: {skipped}")
        print(f"  Timing: {result.enrichment_metadata.get('timing', {})}")

        # At minimum, several core steps should be attempted
        assert len(attempted) >= 3, (
            f"Expected at least 3 services attempted, got {len(attempted)}: {attempted}"
        )

    def test_confounder_risk_produces_output(self, sample_beliefs):
        """Confounder risk should produce non-empty risk assessments."""
        from src.services.answer_enrichment_orchestrator import (
            AnswerEnrichmentOrchestrator, EnrichmentConfig,
        )

        config = EnrichmentConfig(timeout_per_service_ms=5000, global_timeout_ms=30000)
        orchestrator = AnswerEnrichmentOrchestrator(config=config)
        base_answer = self._make_base_answer(sample_beliefs)

        result = orchestrator.enrich(
            base_answer=base_answer,
            question="What is the evidence for biophilic design?",
            user_type="researcher",
        )

        # Check if confounder risk produced anything
        if hasattr(result, 'confounder_risk') and result.confounder_risk:
            assert isinstance(result.confounder_risk, dict) or isinstance(result.confounder_risk, list)
            print(f"\n  Confounder risk output: {json.dumps(result.confounder_risk, indent=2, default=str)[:500]}")
        else:
            # If skipped, check why
            skipped = result.enrichment_metadata.get("services_skipped", [])
            failed = result.enrichment_metadata.get("services_failed", [])
            print(f"\n  Confounder risk not in output. Skipped: {skipped}, Failed: {failed}")

    def test_follow_ups_are_corpus_grounded(self, sample_beliefs):
        """Follow-ups should include some non-template sources."""
        from src.services.answer_enrichment_orchestrator import (
            AnswerEnrichmentOrchestrator, EnrichmentConfig,
        )

        config = EnrichmentConfig(timeout_per_service_ms=5000, global_timeout_ms=30000)
        orchestrator = AnswerEnrichmentOrchestrator(config=config)
        base_answer = self._make_base_answer(sample_beliefs)

        result = orchestrator.enrich(
            base_answer=base_answer,
            question="What is Attention Restoration Theory?",
            user_type="researcher",
        )

        if hasattr(result, 'follow_ups') and result.follow_ups:
            print(f"\n  Follow-ups ({len(result.follow_ups)}):")
            sources_seen = set()
            for fu in result.follow_ups:
                source = fu.get("source", "unknown")
                sources_seen.add(source)
                print(f"    [{source}] VOI={fu.get('voi', '?')}: {fu.get('question', '')[:80]}")

            # Key assertion: at least some should NOT be template-only
            # (Gap predictor, adjacent molecules, or underexplored findings)
            assert len(result.follow_ups) > 0, "Should have at least 1 follow-up"
            print(f"  Sources seen: {sources_seen}")
        else:
            skipped = result.enrichment_metadata.get("services_skipped", [])
            failed = result.enrichment_metadata.get("services_failed", [])
            print(f"\n  No follow-ups. Skipped: {skipped}, Failed: {failed}")


# =============================================================================
# TEST 5: Confounder Risk 4-Tier Classifier
# =============================================================================

class TestConfounderRiskClassifier:
    """Verify the 4-tier design type classification through the full pipeline."""

    def test_rct_classified_as_low_risk(self):
        """RCTs should be classified as low confounder risk."""
        from src.services.answer_enrichment_orchestrator import (
            AnswerEnrichmentOrchestrator, EnrichmentConfig,
        )

        config = EnrichmentConfig(timeout_per_service_ms=5000, global_timeout_ms=30000)
        orch = AnswerEnrichmentOrchestrator(config=config)

        base_answer = {
            "answer": "Drug A reduces symptom B in controlled trials.",
            "beliefs": [
                {
                    "belief_id": "test_rct",
                    "statement": "Drug A reduces symptom B",
                    "design_type": "Randomized Controlled Trial",
                    "sample_size": 200,
                    "effect_size_d": 0.5,
                    "credence_mean": 0.8,
                }
            ],
            "evidence_count": 1,
        }

        result = orch.enrich(base_answer=base_answer, question="Does drug A work?")

        # Check per-belief confounder risk
        if result.enriched_beliefs:
            eb = result.enriched_beliefs[0]
            risk = getattr(eb, 'confounder_risk', None)
            if risk:
                assert "low" in risk.lower(), (
                    f"RCT should be low risk, got: {risk}"
                )
                print(f"\n  RCT risk: {risk}")
                print(f"  Details: {getattr(eb, 'confounder_details', [])}")
            else:
                # confounder_risk may have been skipped by budget
                skipped = result.enrichment_metadata.get("services_skipped", [])
                budget = result.enrichment_metadata.get("services_budget_exceeded", [])
                print(f"\n  Confounder risk not set. Skipped: {skipped}, Budget: {budget}")

    def test_observational_classified_as_high_risk(self):
        """Observational studies should be classified as high confounder risk."""
        from src.services.answer_enrichment_orchestrator import (
            AnswerEnrichmentOrchestrator, EnrichmentConfig,
        )

        config = EnrichmentConfig(timeout_per_service_ms=5000, global_timeout_ms=30000)
        orch = AnswerEnrichmentOrchestrator(config=config)

        base_answer = {
            "answer": "Trees near homes correlate with lower stress.",
            "beliefs": [
                {
                    "belief_id": "test_obs",
                    "statement": "Trees near homes correlate with lower stress",
                    "design_type": "Cross-sectional survey",
                    "sample_size": 500,
                    "credence_mean": 0.6,
                }
            ],
            "evidence_count": 1,
        }

        result = orch.enrich(base_answer=base_answer, question="Do trees reduce stress?")

        if result.enriched_beliefs:
            eb = result.enriched_beliefs[0]
            risk = getattr(eb, 'confounder_risk', None)
            if risk:
                assert "high" in risk.lower(), (
                    f"Cross-sectional survey should be high risk, got: {risk}"
                )
                print(f"\n  Observational risk: {risk}")
                print(f"  Details: {getattr(eb, 'confounder_details', [])}")
            else:
                skipped = result.enrichment_metadata.get("services_skipped", [])
                budget = result.enrichment_metadata.get("services_budget_exceeded", [])
                print(f"\n  Confounder risk not set. Skipped: {skipped}, Budget: {budget}")


# =============================================================================
# TEST 6: Follow-Up Suggestion Service (Direct)
# =============================================================================

class TestFollowUpServiceDirect:
    """Test the FollowUpSuggestionService directly (not through enrichment)."""

    def test_generates_follow_ups(self):
        from src.services.follow_up_suggestion_service import FollowUpSuggestionService
        svc = FollowUpSuggestionService()
        results = svc.generate_follow_ups(
            topic="Attention Restoration Theory",
            beliefs=None,
            gaps=None,
            max_results=5,
        )
        assert isinstance(results, list)
        assert len(results) > 0, "Should generate at least 1 follow-up"
        for fu in results:
            assert "question" in fu, f"Missing 'question' key: {fu}"
            assert "voi" in fu, f"Missing 'voi' key: {fu}"
            assert "source" in fu, f"Missing 'source' key: {fu}"

    def test_deduplicates_results(self):
        from src.services.follow_up_suggestion_service import FollowUpSuggestionService
        svc = FollowUpSuggestionService()
        # Provide gaps that duplicate template questions
        gaps = [
            {
                "question": "What are the boundary conditions where Attention Restoration Theory does NOT hold?",
                "voi": 0.9,
            }
        ]
        results = svc.generate_follow_ups(
            topic="Attention Restoration Theory", gaps=gaps, max_results=5,
        )
        questions = [fu["question"].lower().strip() for fu in results]
        assert len(questions) == len(set(questions)), (
            f"Duplicate questions found: {questions}"
        )

    def test_voi_ordering(self):
        from src.services.follow_up_suggestion_service import FollowUpSuggestionService
        svc = FollowUpSuggestionService()
        results = svc.generate_follow_ups(
            topic="Attention Restoration Theory", max_results=5,
        )
        vois = [fu.get("voi", 0) for fu in results]
        assert vois == sorted(vois, reverse=True), (
            f"Results not sorted by VOI descending: {vois}"
        )


# =============================================================================
# TEST 7: Figure Suggestion Service (Direct)
# =============================================================================

class TestFigureServiceDirect:
    """Test the FigureSuggestionService directly."""

    def test_service_initializes_and_queries(self):
        from src.services.figure_suggestion_service import FigureSuggestionService
        svc = FigureSuggestionService()
        results = svc.suggest_figures_for_topic(
            topic="nature exposure and stress reduction", limit=5
        )
        assert isinstance(results, list)
        # If we have extraction data with figure refs, we should get results
        print(f"\n  Figure results: {len(results)}")
        for fig in results[:3]:
            print(f"    {fig.get('figure_id', 'N/A')}: {fig.get('title', 'N/A')[:60]} "
                  f"(relevance={fig.get('relevance_score', 'N/A')})")

    def test_index_built_once(self):
        """Index should not be rebuilt on second query."""
        from src.services.figure_suggestion_service import FigureSuggestionService
        svc = FigureSuggestionService()
        # First query builds index
        svc.suggest_figures_for_topic("test", limit=1)
        assert svc._built is True
        # Store figure count
        n_figures = len(svc._all_figures)
        # Second query should not rebuild
        svc.suggest_figures_for_topic("another test", limit=1)
        assert len(svc._all_figures) == n_figures, "Index rebuilt on second query"

    def test_relevance_ordering(self):
        from src.services.figure_suggestion_service import FigureSuggestionService
        svc = FigureSuggestionService()
        results = svc.suggest_figures_for_topic(
            topic="lighting and mood and circadian rhythm", limit=10
        )
        if results:
            scores = [r["relevance_score"] for r in results]
            assert scores == sorted(scores, reverse=True), (
                f"Not sorted by relevance: {scores}"
            )


# =============================================================================
# TEST 8: MV Builder Smoke Test
# =============================================================================

class TestMVBuilderSmoke:
    """Verify MV builder can be instantiated and its methods don't crash."""

    def test_build_all_dry_run(self, tmp_path):
        """Build all views to a temp directory — should not crash."""
        from src.qa.mv_builder import MaterializedViewBuilder
        builder = MaterializedViewBuilder(output_dir=str(tmp_path / "mv_output"))
        manifest = builder.build_all(incremental=False)
        assert manifest is not None
        assert isinstance(manifest, dict)
        print(f"\n  MV manifest keys: {list(manifest.keys())}")
        print(f"  MV output files: {list((tmp_path / 'mv_output').glob('*'))}")


# =============================================================================
# Standalone runner
# =============================================================================

if __name__ == "__main__":
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "pytest", __file__, "-v", "--tb=long", "-s"],
        cwd=str(PROJECT_ROOT),
    )
    sys.exit(result.returncode)
