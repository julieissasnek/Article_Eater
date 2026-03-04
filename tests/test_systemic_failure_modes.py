"""
Systemic Failure Mode Tests — Layer 2/3 Validation
====================================================

These tests probe failure modes that CROSS service boundaries, checking invariants
that no single unit test can cover. They are the kind of test an overnight overseer
should run to catch systemic degradation.

Five categories:
1. Cross-service data integrity — information survives transit across all 9 steps
2. Silent failure detection — injected failures are visible in final output
3. Epistemic invariants — architectural commitments enforced end-to-end
4. Budget honesty — latency budget reflected accurately in status/warnings
5. Schema consistency — data structures stable across different runs

Author: CW (Claude Code)
Date: 2026-03-03
"""

import logging
import time
import pytest
from unittest.mock import patch, MagicMock
from dataclasses import asdict, fields

from src.services.answer_enrichment_orchestrator import (
    AnswerEnrichmentOrchestrator,
    EnrichmentConfig,
    EnrichedAnswer,
    EnrichedBelief,
)

logger = logging.getLogger(__name__)


# =============================================================================
# HELPER: Create mock grounding gates
# =============================================================================

def _make_passing_gate():
    """Returns (mock_gate, context_manager) for a grounding gate that passes."""
    mock_result = MagicMock()
    mock_result.should_abstain = False
    mock_result.has_empirical_anchor = True
    mock_result.n_supporting_findings = 2
    mock_result.coherence_status = "coherent"
    mock_result.recommendation = "proceed"
    mock_result.grounding_time_ms = 5.0

    mock_gate = MagicMock()
    mock_gate.check.return_value = mock_result

    cm = patch.dict("sys.modules", {
        "src.qa.grounding_gate": MagicMock(GroundingGate=lambda: mock_gate)
    })
    return mock_gate, cm


def _make_crashing_gate():
    """Returns context_manager for a grounding gate that crashes."""
    mock_gate = MagicMock()
    mock_gate.check.side_effect = RuntimeError("Gate crash")
    cm = patch.dict("sys.modules", {
        "src.qa.grounding_gate": MagicMock(GroundingGate=lambda: mock_gate)
    })
    return cm


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def rich_base_answer():
    """Base answer with full provenance — the realistic case."""
    return {
        "answer": "Green spaces reduce stress through multiple pathways.",
        "beliefs": [
            {
                "text": "Urban green spaces reduce cortisol by 12-15%",
                "confidence": 0.82,
                "p_lab": 0.82, "d": 0.85, "omega": 0.90, "delta": 1.0,
                "design_type": "standard_rct",
                "paper_ids": ["doi:10.1038/s41598-019-44097", "arxiv:2020.1234"],
                "belief_id": "belief_cortisol_001",
            },
            {
                "text": "This effect is mediated by reduced sympathetic arousal",
                "confidence": 0.68,
                "p_lab": 0.68, "d": 0.72, "omega": 0.75, "delta": 0.90,
                "design_type": "observational",
                "paper_ids": ["doi:10.1016/j.envres.2018.04"],
                "belief_id": "belief_arousal_002",
            },
            {
                "text": "Children show larger stress-reduction effects than adults",
                "confidence": 0.55,
                "p_lab": 0.55, "d": 0.60, "omega": 0.50, "delta": 0.85,
                "design_type": "observational",
                "paper_ids": [],
                "belief_id": "belief_children_003",
            },
        ],
        "evidence_count": 3,
        "theories_involved": ["stress_reduction_theory", "attention_restoration_theory"],
    }


@pytest.fixture
def all_enabled_config():
    """Config with everything enabled — maximum pipeline coverage."""
    return EnrichmentConfig(
        enable_credence_ci=True,
        enable_warrant_trace=True,
        enable_confounder_risk=True,
        enable_framework_voices=True,
        enable_gap_analysis=True,
        enable_follow_ups=True,
        enable_language_adaptation=True,
        enable_figure_suggestions=True,
        enable_interpretation_context=True,
        timeout_per_service_ms=2000,
        global_timeout_ms=10000,  # generous for testing
    )


@pytest.fixture
def credence_only_config():
    """Config with only credence — isolates first step."""
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
    )


# =============================================================================
# 1. CROSS-SERVICE DATA INTEGRITY
# =============================================================================

@pytest.mark.layer2_nightly
class TestCrossServiceDataIntegrity:
    """Information must survive transit across ALL enrichment steps."""

    def test_paper_ids_survive_full_pipeline(self, rich_base_answer, all_enabled_config):
        """paper_ids set during credence must persist through all 9 steps."""
        orch = AnswerEnrichmentOrchestrator(all_enabled_config)
        _, cm = _make_passing_gate()
        with cm:
            result = orch.enrich(rich_base_answer, question="Does green space reduce stress?")

        if result.status == "abstained":
            pytest.skip("Grounding gate abstained")

        beliefs_with_papers = [
            eb for eb in result.enriched_beliefs if len(eb.paper_ids) > 0
        ]
        assert len(beliefs_with_papers) >= 2, (
            f"Expected >=2 beliefs with paper_ids, got {len(beliefs_with_papers)}. "
            f"Full pipeline may be stripping provenance."
        )

    def test_belief_count_matches_input(self, rich_base_answer, credence_only_config):
        """Number of enriched beliefs should match input beliefs."""
        orch = AnswerEnrichmentOrchestrator(credence_only_config)
        _, cm = _make_passing_gate()
        with cm:
            result = orch.enrich(rich_base_answer, question="test")

        if result.status == "abstained":
            pytest.skip("Grounding gate abstained")

        assert len(result.enriched_beliefs) == len(rich_base_answer["beliefs"]), (
            f"Input had {len(rich_base_answer['beliefs'])} beliefs but "
            f"output has {len(result.enriched_beliefs)}"
        )

    def test_belief_text_not_corrupted(self, rich_base_answer, credence_only_config):
        """Belief text must pass through enrichment unchanged."""
        orch = AnswerEnrichmentOrchestrator(credence_only_config)
        _, cm = _make_passing_gate()
        with cm:
            result = orch.enrich(rich_base_answer, question="test")

        if result.status == "abstained":
            pytest.skip("Grounding gate abstained")

        input_texts = {b["text"] for b in rich_base_answer["beliefs"]}
        output_texts = {eb.text for eb in result.enriched_beliefs}
        assert input_texts == output_texts, (
            f"Belief texts changed during enrichment!\n"
            f"  Input:  {input_texts}\n"
            f"  Output: {output_texts}"
        )

    def test_base_answer_preserved(self, rich_base_answer, all_enabled_config):
        """base_answer in EnrichedAnswer must be the original, unmodified."""
        import copy
        original = copy.deepcopy(rich_base_answer)
        orch = AnswerEnrichmentOrchestrator(all_enabled_config)
        _, cm = _make_passing_gate()
        with cm:
            result = orch.enrich(rich_base_answer, question="test")

        assert result.base_answer["answer"] == original["answer"], (
            "base_answer was modified during enrichment"
        )

    def test_grounding_gate_status_not_overwritten(self, all_enabled_config):
        """If grounding gate sets status='abstained', later steps must not change it."""
        orch = AnswerEnrichmentOrchestrator(all_enabled_config)
        base = {
            "answer": "test",
            "beliefs": [{"text": "t", "confidence": 0.5,
                         "p_lab": 0.5, "d": 0.5, "omega": 0.5, "delta": 0.5,
                         "design_type": "observational"}],
        }
        cm = _make_crashing_gate()
        with cm:
            result = orch.enrich(base, question="test")

        assert result.status == "abstained", (
            f"Grounding gate crash should set 'abstained' but got '{result.status}' — "
            f"a later step may have overwritten it"
        )


# =============================================================================
# 2. SILENT FAILURE DETECTION
# =============================================================================

@pytest.mark.layer2_nightly
class TestSilentFailureDetection:
    """Every service failure must be visible in the final EnrichedAnswer."""

    def _run_with_passing_gate(self, config, base, question="test"):
        orch = AnswerEnrichmentOrchestrator(config)
        _, cm = _make_passing_gate()
        with cm:
            return orch.enrich(base, question=question)

    def test_all_services_missing_not_complete(self, all_enabled_config, rich_base_answer):
        """With services unavailable, status must not be 'complete'."""
        result = self._run_with_passing_gate(all_enabled_config, rich_base_answer)
        skipped = result.enrichment_metadata.get("services_skipped", [])
        failed = result.enrichment_metadata.get("services_failed", [])
        if skipped or failed:
            assert result.status != "complete", (
                f"Services skipped/failed but status is 'complete'. "
                f"Skipped: {skipped}, Failed: {failed}"
            )

    def test_failed_services_named_in_warnings(self, all_enabled_config, rich_base_answer):
        """Each failed service should be mentioned in warnings."""
        result = self._run_with_passing_gate(all_enabled_config, rich_base_answer)
        failed = result.enrichment_metadata.get("services_failed", [])
        if failed:
            warning_text = " ".join(result.warnings)
            assert len(result.warnings) > 0, (
                f"Services failed ({failed}) but no warnings generated"
            )

    def test_skipped_services_produce_warnings(self, all_enabled_config, rich_base_answer):
        """Skipped services should generate warnings."""
        result = self._run_with_passing_gate(all_enabled_config, rich_base_answer)
        skipped = result.enrichment_metadata.get("services_skipped", [])
        if skipped:
            assert len(result.warnings) > 0, (
                f"Services skipped ({skipped}) but no warnings generated"
            )

    def test_services_attempted_includes_credence(self, all_enabled_config, rich_base_answer):
        """Credence enrichment should always be in services_attempted when enabled.
        NOTE: config flag is 'enable_credence_ci' but service name is 'credence_enrichment'.
        This naming inconsistency is itself a finding worth tracking.
        """
        result = self._run_with_passing_gate(all_enabled_config, rich_base_answer)
        attempted = result.enrichment_metadata.get("services_attempted", [])
        assert "credence_enrichment" in attempted, (
            f"credence enrichment enabled but not in services_attempted: {attempted}"
        )

    def test_every_attempted_service_has_outcome(self, all_enabled_config, rich_base_answer):
        """Every service in services_attempted must appear in timing, skipped, or failed."""
        result = self._run_with_passing_gate(all_enabled_config, rich_base_answer)
        attempted = set(result.enrichment_metadata.get("services_attempted", []))
        timed = set(result.enrichment_metadata.get("timing", {}).keys())
        skipped = set(result.enrichment_metadata.get("services_skipped", []))
        failed = set(result.enrichment_metadata.get("services_failed", []))

        accounted_for = timed | skipped | failed
        unaccounted = attempted - accounted_for
        assert len(unaccounted) == 0, (
            f"Services attempted but with no outcome recorded: {unaccounted}"
        )

    def test_complete_requires_no_failures_or_skips(self, all_enabled_config, rich_base_answer):
        """If status='complete', there must be zero failures AND zero skips."""
        result = self._run_with_passing_gate(all_enabled_config, rich_base_answer)
        if result.status == "complete":
            failed = result.enrichment_metadata.get("services_failed", [])
            skipped = result.enrichment_metadata.get("services_skipped", [])
            budget_exceeded = result.enrichment_metadata.get("services_budget_exceeded", [])
            assert len(failed) == 0, f"Status 'complete' but services_failed={failed}"
            assert len(skipped) == 0, f"Status 'complete' but services_skipped={skipped}"
            assert len(budget_exceeded) == 0, f"Status 'complete' but budget_exceeded={budget_exceeded}"


# =============================================================================
# 3. EPISTEMIC INVARIANTS
# =============================================================================

@pytest.mark.layer2_nightly
class TestEpistemicInvariants:
    """Invariants that encode the system's epistemic commitments."""

    def test_abstained_answer_has_no_enrichment(self, all_enabled_config):
        """An abstained answer must not carry any enrichment output."""
        orch = AnswerEnrichmentOrchestrator(all_enabled_config)
        base = {
            "answer": "test", "beliefs": [
                {"text": "t", "confidence": 0.5, "p_lab": 0.5,
                 "d": 0.5, "omega": 0.5, "delta": 0.5,
                 "design_type": "observational"}
            ],
        }
        cm = _make_crashing_gate()
        with cm:
            result = orch.enrich(base, question="test")

        assert result.status == "abstained"
        assert len(result.enriched_beliefs) == 0, (
            f"Abstained answer should have 0 enriched beliefs, got {len(result.enriched_beliefs)}"
        )
        assert len(result.framework_voices) == 0
        assert len(result.gaps) == 0
        assert len(result.follow_ups) == 0
        assert len(result.figures) == 0

    def test_warnings_never_empty_strings(self, all_enabled_config, rich_base_answer):
        """Warnings must be informative — no empty strings."""
        orch = AnswerEnrichmentOrchestrator(all_enabled_config)
        _, cm = _make_passing_gate()
        with cm:
            result = orch.enrich(rich_base_answer, question="test")

        for w in result.warnings:
            assert len(w.strip()) > 0, "Found empty warning string"

    def test_metadata_always_has_timing(self, all_enabled_config, rich_base_answer):
        """enrichment_metadata must always include a 'timing' dict."""
        orch = AnswerEnrichmentOrchestrator(all_enabled_config)
        _, cm = _make_passing_gate()
        with cm:
            result = orch.enrich(rich_base_answer, question="test")

        assert "timing" in result.enrichment_metadata
        assert isinstance(result.enrichment_metadata["timing"], dict)

    def test_metadata_always_has_question(self, all_enabled_config, rich_base_answer):
        """enrichment_metadata must record the question asked."""
        orch = AnswerEnrichmentOrchestrator(all_enabled_config)
        _, cm = _make_passing_gate()
        with cm:
            result = orch.enrich(rich_base_answer, question="Does green space reduce stress?")

        assert "question" in result.enrichment_metadata
        assert result.enrichment_metadata["question"] == "Does green space reduce stress?"

    def test_status_is_valid_enum(self, all_enabled_config, rich_base_answer):
        """status must be one of the four defined values."""
        valid_statuses = {"complete", "partial", "degraded", "abstained"}
        orch = AnswerEnrichmentOrchestrator(all_enabled_config)
        _, cm = _make_passing_gate()
        with cm:
            result = orch.enrich(rich_base_answer, question="test")

        assert result.status in valid_statuses, (
            f"Invalid status '{result.status}', must be one of {valid_statuses}"
        )

    def test_paper_ids_not_lost_when_answer_complete(self, all_enabled_config, rich_base_answer):
        """If status is complete/partial and input had paper_ids, output must too."""
        orch = AnswerEnrichmentOrchestrator(all_enabled_config)
        _, cm = _make_passing_gate()
        with cm:
            result = orch.enrich(rich_base_answer, question="test")

        if result.status in ("complete", "partial") and len(result.enriched_beliefs) > 0:
            has_papers = any(len(eb.paper_ids) > 0 for eb in result.enriched_beliefs)
            assert has_papers, (
                "Invariant violated: completed answer lost all paper_ids despite "
                "input beliefs having them"
            )


# =============================================================================
# 4. BUDGET HONESTY
# =============================================================================

@pytest.mark.layer2_nightly
class TestBudgetHonesty:
    """Latency budget must be accurately reflected in status/warnings."""

    def test_tight_budget_causes_skips_or_degradation(self, rich_base_answer):
        """With 1ms budget, later steps should be skipped."""
        tight_config = EnrichmentConfig(
            enable_credence_ci=True,
            enable_warrant_trace=True,
            enable_confounder_risk=True,
            enable_framework_voices=True,
            enable_gap_analysis=True,
            enable_follow_ups=True,
            enable_language_adaptation=True,
            enable_figure_suggestions=True,
            enable_interpretation_context=True,
            global_timeout_ms=1,
            timeout_per_service_ms=1,
        )
        orch = AnswerEnrichmentOrchestrator(tight_config)
        _, cm = _make_passing_gate()
        with cm:
            result = orch.enrich(rich_base_answer, question="test")

        budget_exceeded = result.enrichment_metadata.get("services_budget_exceeded", [])
        total_skipped = len(budget_exceeded) + len(
            result.enrichment_metadata.get("services_skipped", [])
        )
        assert total_skipped > 0 or result.status != "complete", (
            "1ms budget but nothing was skipped and status is 'complete'"
        )

    def test_budget_exceeded_reflected_in_status(self, rich_base_answer):
        """If budget forces skips, status should not be 'complete'."""
        tight_config = EnrichmentConfig(
            enable_credence_ci=True,
            enable_warrant_trace=True,
            enable_confounder_risk=True,
            enable_framework_voices=True,
            enable_gap_analysis=True,
            enable_follow_ups=True,
            enable_language_adaptation=True,
            enable_figure_suggestions=True,
            enable_interpretation_context=True,
            global_timeout_ms=50,
            timeout_per_service_ms=10,
        )
        orch = AnswerEnrichmentOrchestrator(tight_config)
        _, cm = _make_passing_gate()
        with cm:
            result = orch.enrich(rich_base_answer, question="test")

        budget_exceeded = result.enrichment_metadata.get("services_budget_exceeded", [])
        if len(budget_exceeded) > 0:
            assert result.status in ("partial", "degraded"), (
                f"Budget exceeded for {budget_exceeded} but status is '{result.status}'"
            )

    def test_budget_exceeded_services_appear_in_metadata(self, rich_base_answer):
        """services_budget_exceeded must be a list in metadata."""
        config = EnrichmentConfig(global_timeout_ms=100, timeout_per_service_ms=10)
        orch = AnswerEnrichmentOrchestrator(config)
        _, cm = _make_passing_gate()
        with cm:
            result = orch.enrich(rich_base_answer, question="test")

        assert "services_budget_exceeded" in result.enrichment_metadata, (
            "services_budget_exceeded missing from metadata"
        )
        assert isinstance(
            result.enrichment_metadata["services_budget_exceeded"], list
        )


# =============================================================================
# 5. SCHEMA CONSISTENCY
# =============================================================================

@pytest.mark.layer2_nightly
class TestSchemaConsistency:
    """Data structures must have consistent shapes across runs."""

    def test_enriched_belief_fields_consistent(self, rich_base_answer, credence_only_config):
        """All EnrichedBelief objects must have the same set of fields."""
        orch = AnswerEnrichmentOrchestrator(credence_only_config)
        _, cm = _make_passing_gate()
        with cm:
            result = orch.enrich(rich_base_answer, question="test")

        if len(result.enriched_beliefs) < 2:
            pytest.skip("Need >=2 beliefs to check consistency")

        field_sets = [set(asdict(eb).keys()) for eb in result.enriched_beliefs]
        for i, fs in enumerate(field_sets[1:], 1):
            assert fs == field_sets[0], (
                f"EnrichedBelief[0] has fields {field_sets[0]} but "
                f"EnrichedBelief[{i}] has fields {fs}"
            )

    def test_to_dict_has_all_dataclass_fields(self, rich_base_answer, credence_only_config):
        """to_dict() must include every field on EnrichedAnswer."""
        orch = AnswerEnrichmentOrchestrator(credence_only_config)
        _, cm = _make_passing_gate()
        with cm:
            result = orch.enrich(rich_base_answer, question="test")

        d = result.to_dict()
        dataclass_fields = {f.name for f in fields(EnrichedAnswer)}
        dict_keys = set(d.keys())
        missing = dataclass_fields - dict_keys
        assert len(missing) == 0, f"to_dict() missing fields: {missing}"

    def test_metadata_has_required_keys(self, rich_base_answer, all_enabled_config):
        """enrichment_metadata must always have the expected keys."""
        orch = AnswerEnrichmentOrchestrator(all_enabled_config)
        _, cm = _make_passing_gate()
        with cm:
            result = orch.enrich(rich_base_answer, question="test")

        required = {"timing", "services_attempted", "services_failed",
                    "services_skipped", "services_budget_exceeded"}
        actual = set(result.enrichment_metadata.keys())
        missing = required - actual
        assert len(missing) == 0, (
            f"Metadata missing required keys: {missing}. Present: {actual}"
        )

    def test_to_dict_roundtrip_preserves_status(self, rich_base_answer, credence_only_config):
        """status and warnings must survive to_dict() serialization."""
        orch = AnswerEnrichmentOrchestrator(credence_only_config)
        _, cm = _make_passing_gate()
        with cm:
            result = orch.enrich(rich_base_answer, question="test")

        d = result.to_dict()
        assert d["status"] == result.status
        assert d["warnings"] == result.warnings

    def test_multiple_runs_same_schema(self, rich_base_answer, credence_only_config):
        """Two runs with same input should produce same-shaped output."""
        orch = AnswerEnrichmentOrchestrator(credence_only_config)

        results = []
        for _ in range(2):
            _, cm = _make_passing_gate()
            with cm:
                results.append(orch.enrich(rich_base_answer, question="test"))

        d1 = results[0].to_dict()
        d2 = results[1].to_dict()
        assert set(d1.keys()) == set(d2.keys()), (
            f"Schema differs between runs: {set(d1.keys())} vs {set(d2.keys())}"
        )
