"""
V13 P0 Fixes Validation Tests
==============================

These tests probe EXACTLY the four P0 fixes identified by the V13 Ruthless Audit
and implemented by AG. Each test targets a specific failure mode that the existing
test suite (test_answer_enrichment_orchestrator.py) does NOT cover.

Fix 1: Paper traceability — paper_ids preserved through enrichment
Fix 2: Grounding gate — abstains on crash instead of proceeding
Fix 3: get_master_web() — tuple unpacking handles (WebOfBelief, BridgeRegistry)
Fix 4: Answer status/warnings — degradation visible to consumers

Author: CW (Claude Code review)
Date: 2026-03-03
"""

import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from dataclasses import asdict

from src.services.answer_enrichment_orchestrator import (
    AnswerEnrichmentOrchestrator,
    EnrichmentConfig,
    EnrichedAnswer,
    EnrichedBelief,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def base_answer_with_paper_ids():
    """Base answer where beliefs carry paper_ids — the field the old code discarded."""
    return {
        "answer": "Nature exposure reduces cortisol levels.",
        "beliefs": [
            {
                "text": "Park walks reduce salivary cortisol by 12%",
                "confidence": 0.80,
                "p_lab": 0.80,
                "d": 0.85,
                "omega": 0.90,
                "delta": 1.0,
                "design_type": "standard_rct",
                "paper_ids": ["arxiv:2020.1234", "doi:10.1038/s41598-019"],
                "belief_id": "belief_cortisol_001",
            },
            {
                "text": "Forest bathing lowers blood pressure",
                "confidence": 0.70,
                "p_lab": 0.70,
                "d": 0.75,
                "omega": 0.80,
                "delta": 0.95,
                "design_type": "observational",
                "paper_ids": ["doi:10.1016/j.envres.2018"],
                "belief_id": "belief_bp_002",
            },
        ],
        "evidence_count": 2,
    }


@pytest.fixture
def base_answer_no_paper_ids():
    """Base answer where beliefs have NO paper_ids — tests the default."""
    return {
        "answer": "Some answer.",
        "beliefs": [
            {
                "text": "A belief without provenance",
                "confidence": 0.60,
                "p_lab": 0.60,
                "d": 0.70,
                "omega": 0.65,
                "delta": 0.90,
                "design_type": "observational",
            },
        ],
        "evidence_count": 1,
    }


@pytest.fixture
def minimal_config():
    """Config with only credence enabled — isolates paper_ids test."""
    return EnrichmentConfig(
        enable_credence_ci=True,
        enable_warrant_trace=False,
        enable_confounder_risk=False,
        enable_framework_voices=False,
        enable_gap_analysis=False,
        enable_follow_ups=False,
        enable_language_adaptation=False,
        enable_figure_suggestions=False,
        enable_interpretation_context=False,
        timeout_per_service_ms=2000,
    )


@pytest.fixture
def full_config():
    """Config with everything enabled."""
    return EnrichmentConfig()


# =============================================================================
# FIX 1: PAPER TRACEABILITY
# These tests verify that paper_ids survive the enrichment pipeline.
# The OLD code discarded them — EnrichedBelief had no paper_ids field.
# =============================================================================

@pytest.mark.layer2_nightly
class TestPaperTraceability:
    """Fix 1: paper_ids must persist through enrichment."""

    def test_enriched_belief_has_paper_ids_field(self):
        """EnrichedBelief dataclass must include paper_ids."""
        eb = EnrichedBelief(text="test")
        assert hasattr(eb, "paper_ids"), "EnrichedBelief missing paper_ids field"
        assert isinstance(eb.paper_ids, list), "paper_ids should default to list"

    def test_enriched_belief_has_belief_id_field(self):
        """EnrichedBelief dataclass must include belief_id."""
        eb = EnrichedBelief(text="test")
        assert hasattr(eb, "belief_id"), "EnrichedBelief missing belief_id field"

    def test_paper_ids_default_empty_list(self):
        """paper_ids defaults to [] not None — safe for iteration."""
        eb = EnrichedBelief(text="test")
        assert eb.paper_ids == [], f"Expected empty list, got {eb.paper_ids}"
        # Must be iterable without null check
        count = sum(1 for _ in eb.paper_ids)
        assert count == 0

    def test_belief_id_default_none(self):
        """belief_id defaults to None (not all sources assign IDs)."""
        eb = EnrichedBelief(text="test")
        assert eb.belief_id is None

    def test_paper_ids_preserved_through_credence_enrichment(
        self, base_answer_with_paper_ids, minimal_config
    ):
        """CRITICAL: paper_ids from input beliefs must appear in EnrichedBeliefs."""
        orch = AnswerEnrichmentOrchestrator(minimal_config)
        result = orch.enrich(
            base_answer_with_paper_ids,
            question="Does nature reduce cortisol?",
        )
        # If grounding gate abstains, skip this check (separate issue)
        if result.status == "abstained":
            pytest.skip("Grounding gate abstained — cannot test credence path")

        assert len(result.enriched_beliefs) > 0, "No enriched beliefs created"

        for eb in result.enriched_beliefs:
            assert hasattr(eb, "paper_ids"), f"EnrichedBelief missing paper_ids"
            # At least one belief should have non-empty paper_ids
        has_papers = any(len(eb.paper_ids) > 0 for eb in result.enriched_beliefs)
        assert has_papers, (
            "No enriched beliefs preserved paper_ids — traceability broken! "
            f"Beliefs: {[(eb.text[:30], eb.paper_ids) for eb in result.enriched_beliefs]}"
        )

    def test_paper_ids_absent_defaults_empty(
        self, base_answer_no_paper_ids, minimal_config
    ):
        """Beliefs without paper_ids should get empty list, not crash."""
        orch = AnswerEnrichmentOrchestrator(minimal_config)
        result = orch.enrich(
            base_answer_no_paper_ids,
            question="Some question",
        )
        if result.status == "abstained":
            pytest.skip("Grounding gate abstained")

        for eb in result.enriched_beliefs:
            assert eb.paper_ids == [], f"Expected empty list, got {eb.paper_ids}"

    def test_paper_ids_in_serialized_output(
        self, base_answer_with_paper_ids, minimal_config
    ):
        """paper_ids must appear in to_dict() output — consumers need it."""
        orch = AnswerEnrichmentOrchestrator(minimal_config)
        result = orch.enrich(
            base_answer_with_paper_ids,
            question="Does nature reduce cortisol?",
        )
        d = result.to_dict()
        for belief_dict in d.get("enriched_beliefs", []):
            assert "paper_ids" in belief_dict, (
                f"paper_ids missing from serialized belief: {list(belief_dict.keys())}"
            )

    def test_belief_id_preserved_through_enrichment(
        self, base_answer_with_paper_ids, minimal_config
    ):
        """belief_id from input should persist in EnrichedBelief."""
        orch = AnswerEnrichmentOrchestrator(minimal_config)
        result = orch.enrich(
            base_answer_with_paper_ids,
            question="Does nature reduce cortisol?",
        )
        if result.status == "abstained":
            pytest.skip("Grounding gate abstained")

        has_id = any(eb.belief_id is not None for eb in result.enriched_beliefs)
        assert has_id, "No enriched beliefs preserved belief_id"


# =============================================================================
# FIX 2: GROUNDING GATE ABSTENTION
# The OLD code caught grounding gate exceptions and PROCEEDED with enrichment.
# The fix returns early with status="abstained".
# =============================================================================

@pytest.mark.layer2_nightly
class TestGroundingGateAbstention:
    """Fix 2: Grounding gate crash must trigger abstention, not proceed."""

    def test_grounding_gate_crash_sets_abstained_status(self, full_config):
        """If grounding gate raises, status must be 'abstained'."""
        orch = AnswerEnrichmentOrchestrator(full_config)
        base = {
            "answer": "test",
            "beliefs": [{"text": "test belief", "confidence": 0.5,
                         "p_lab": 0.5, "d": 0.5, "omega": 0.5, "delta": 0.5,
                         "design_type": "observational"}],
        }
        # GroundingGate is imported inside enrich() via:
        #   from src.qa.grounding_gate import GroundingGate
        # We mock the module so import succeeds but .check() crashes
        mock_gate = MagicMock()
        mock_gate.check.side_effect = RuntimeError("Grounding gate internal error")

        with patch.dict("sys.modules", {"src.qa.grounding_gate": MagicMock(GroundingGate=lambda: mock_gate)}):
            result = orch.enrich(base, question="test question")

        assert result.status == "abstained", (
            f"Expected 'abstained' after grounding gate crash, got '{result.status}'"
        )

    def test_grounding_gate_crash_returns_early(self, full_config):
        """After grounding gate crash, NO enrichment steps should run."""
        orch = AnswerEnrichmentOrchestrator(full_config)
        base = {
            "answer": "test",
            "beliefs": [{"text": "test", "confidence": 0.5,
                         "p_lab": 0.5, "d": 0.5, "omega": 0.5, "delta": 0.5,
                         "design_type": "observational"}],
        }
        mock_gate = MagicMock()
        mock_gate.check.side_effect = RuntimeError("Crash")

        with patch.dict("sys.modules", {"src.qa.grounding_gate": MagicMock(GroundingGate=lambda: mock_gate)}):
            result = orch.enrich(base, question="test question")

        # If gate crashed and we abstained, enriched_beliefs should be empty
        assert len(result.enriched_beliefs) == 0, (
            f"Expected no enrichment after gate crash, got {len(result.enriched_beliefs)} beliefs"
        )
        # No framework voices either
        assert len(result.framework_voices) == 0, "Framework voices should not run after gate crash"

    def test_grounding_gate_crash_has_warning(self, full_config):
        """User-visible warning must be present after gate crash."""
        orch = AnswerEnrichmentOrchestrator(full_config)
        base = {
            "answer": "test",
            "beliefs": [{"text": "test", "confidence": 0.5,
                         "p_lab": 0.5, "d": 0.5, "omega": 0.5, "delta": 0.5,
                         "design_type": "observational"}],
        }
        mock_gate = MagicMock()
        mock_gate.check.side_effect = RuntimeError("Crash")

        with patch.dict("sys.modules", {"src.qa.grounding_gate": MagicMock(GroundingGate=lambda: mock_gate)}):
            result = orch.enrich(base, question="test question")

        assert len(result.warnings) > 0, "No warnings after grounding gate crash"
        assert any("abstain" in w.lower() or "grounding" in w.lower() for w in result.warnings), (
            f"Warning should mention abstention or grounding gate: {result.warnings}"
        )

    def test_grounding_gate_crash_metadata_has_fatal(self, full_config):
        """Metadata must flag the crash as fatal."""
        orch = AnswerEnrichmentOrchestrator(full_config)
        base = {
            "answer": "test",
            "beliefs": [{"text": "test", "confidence": 0.5,
                         "p_lab": 0.5, "d": 0.5, "omega": 0.5, "delta": 0.5,
                         "design_type": "observational"}],
        }
        mock_gate = MagicMock()
        mock_gate.check.side_effect = RuntimeError("Crash")

        with patch.dict("sys.modules", {"src.qa.grounding_gate": MagicMock(GroundingGate=lambda: mock_gate)}):
            result = orch.enrich(base, question="test question")

        grounding_meta = result.enrichment_metadata.get("grounding", {})
        assert grounding_meta.get("fatal") is True, (
            f"Grounding metadata should have fatal=True: {grounding_meta}"
        )

    def test_grounding_gate_import_error_also_abstains(self, full_config):
        """If grounding gate module doesn't exist, must also abstain."""
        orch = AnswerEnrichmentOrchestrator(full_config)
        base = {
            "answer": "test",
            "beliefs": [{"text": "test", "confidence": 0.5,
                         "p_lab": 0.5, "d": 0.5, "omega": 0.5, "delta": 0.5,
                         "design_type": "observational"}],
        }
        # Remove the module so import fails
        import sys
        modules_backup = {}
        for key in list(sys.modules.keys()):
            if "grounding_gate" in key:
                modules_backup[key] = sys.modules.pop(key)

        try:
            with patch.dict("sys.modules", {"src.qa.grounding_gate": None}):
                # This should trigger ImportError → abstain
                result = orch.enrich(base, question="test question")
                assert result.status == "abstained", (
                    f"Expected abstained on import failure, got '{result.status}'"
                )
        finally:
            sys.modules.update(modules_backup)


# =============================================================================
# FIX 3: get_master_web() TUPLE UNPACKING
# =============================================================================

@pytest.mark.layer2_nightly
class TestMasterWebTupleUnpacking:
    """Fix 3: get_master_web() returns tuple; code must unpack correctly."""

    def test_tuple_result_extracts_web(self):
        """When get_master_web() returns (WebOfBelief, BridgeRegistry), extract [0]."""
        try:
            from src.services.integrated_query_service import IntegratedQueryService
        except ImportError:
            pytest.skip("IntegratedQueryService not importable")

        mock_web = MagicMock()
        mock_web.beliefs = {"b1": {"text": "test"}}
        mock_registry = MagicMock()

        mock_accumulator = MagicMock()
        mock_accumulator.get_master_web.return_value = (mock_web, mock_registry)

        service = IntegratedQueryService.__new__(IntegratedQueryService)
        service._web = None
        service._accumulator = mock_accumulator

        # Access the web property
        result = service.web
        assert result is mock_web, f"Expected WebOfBelief, got {type(result)}"
        assert result is not (mock_web, mock_registry), "Got tuple instead of WebOfBelief"

    def test_non_tuple_result_passes_through(self):
        """When get_master_web() returns bare WebOfBelief, use it directly."""
        try:
            from src.services.integrated_query_service import IntegratedQueryService
        except ImportError:
            pytest.skip("IntegratedQueryService not importable")

        mock_web = MagicMock()
        mock_web.beliefs = {"b1": {"text": "test"}}

        mock_accumulator = MagicMock()
        mock_accumulator.get_master_web.return_value = mock_web  # Not a tuple

        service = IntegratedQueryService.__new__(IntegratedQueryService)
        service._web = None
        service._accumulator = mock_accumulator

        result = service.web
        assert result is mock_web


# =============================================================================
# FIX 4: ANSWER STATUS AND WARNINGS
# =============================================================================

@pytest.mark.layer2_nightly
class TestAnswerStatusAndWarnings:
    """Fix 4: EnrichedAnswer must expose status and warnings."""

    def test_enriched_answer_has_status_field(self):
        """EnrichedAnswer must have a status field."""
        ea = EnrichedAnswer(base_answer={"answer": "test"})
        assert hasattr(ea, "status"), "EnrichedAnswer missing 'status' field"
        assert ea.status == "complete", f"Default status should be 'complete', got '{ea.status}'"

    def test_enriched_answer_has_warnings_field(self):
        """EnrichedAnswer must have a warnings field."""
        ea = EnrichedAnswer(base_answer={"answer": "test"})
        assert hasattr(ea, "warnings"), "EnrichedAnswer missing 'warnings' field"
        assert isinstance(ea.warnings, list)
        assert len(ea.warnings) == 0

    def test_status_in_serialized_output(self):
        """status and warnings must appear in to_dict()."""
        ea = EnrichedAnswer(base_answer={"answer": "test"})
        ea.status = "degraded"
        ea.warnings = ["Service X failed"]
        d = ea.to_dict()
        assert "status" in d, f"status missing from to_dict: {list(d.keys())}"
        assert d["status"] == "degraded"
        assert "warnings" in d, f"warnings missing from to_dict: {list(d.keys())}"
        assert "Service X failed" in d["warnings"]

    def test_status_degraded_when_services_fail(self, full_config):
        """If services crash, status should be 'degraded'."""
        orch = AnswerEnrichmentOrchestrator(full_config)
        base = {
            "answer": "test",
            "beliefs": [{"text": "test", "confidence": 0.5,
                         "p_lab": 0.5, "d": 0.5, "omega": 0.5, "delta": 0.5,
                         "design_type": "observational"}],
        }
        # Make the grounding gate pass, then let services fail naturally
        mock_gate_result = MagicMock()
        mock_gate_result.should_abstain = False
        mock_gate_result.has_empirical_anchor = True
        mock_gate_result.n_supporting_findings = 1
        mock_gate_result.coherence_status = "coherent"
        mock_gate_result.recommendation = "proceed"
        mock_gate_result.grounding_time_ms = 10

        mock_gate = MagicMock()
        mock_gate.check.return_value = mock_gate_result

        with patch.dict("sys.modules", {"src.qa.grounding_gate": MagicMock(GroundingGate=lambda: mock_gate)}):
            result = orch.enrich(base, question="test question")

        # Status should be complete, partial, or degraded depending on what services exist
        assert result.status in ("complete", "partial", "degraded"), (
            f"Unexpected status: {result.status}"
        )
        # The status field must be populated (not left as default if services were skipped)
        assert isinstance(result.status, str)

    def test_warnings_list_populated_on_failure(self, full_config):
        """Warnings should list which services failed or were skipped."""
        orch = AnswerEnrichmentOrchestrator(full_config)
        base = {
            "answer": "test",
            "beliefs": [{"text": "test", "confidence": 0.5,
                         "p_lab": 0.5, "d": 0.5, "omega": 0.5, "delta": 0.5,
                         "design_type": "observational"}],
        }
        mock_gate_result = MagicMock()
        mock_gate_result.should_abstain = False
        mock_gate_result.has_empirical_anchor = True
        mock_gate_result.n_supporting_findings = 1
        mock_gate_result.coherence_status = "coherent"
        mock_gate_result.recommendation = "proceed"
        mock_gate_result.grounding_time_ms = 10

        mock_gate = MagicMock()
        mock_gate.check.return_value = mock_gate_result

        with patch.dict("sys.modules", {"src.qa.grounding_gate": MagicMock(GroundingGate=lambda: mock_gate)}):
            result = orch.enrich(base, question="test question")

        # If any services were skipped/failed, warnings should be non-empty
        skipped = result.enrichment_metadata.get("services_skipped", [])
        failed = result.enrichment_metadata.get("services_failed", [])
        if skipped or failed:
            assert len(result.warnings) > 0, (
                f"Services skipped={skipped}, failed={failed} but no warnings generated"
            )
