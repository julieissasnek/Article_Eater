from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

from src.epistemic.gap_types import GapType
from src.queue import (
    OpportunityStatus,
    ResearchQueueService,
    SearchResult,
    SearchResultType,
)
from src.queue.models import NullResultEvidence


@dataclass
class _FakeGap:
    gap_id: str
    gap_type: GapType
    description: str
    voi_score: float
    affected_beliefs: list[str]
    implied_by: list[str]

    def to_dict(self):
        """Serialize to dict for compatibility with ResearchQueueService."""
        return {
            'gap_id': self.gap_id,
            'gap_type': self.gap_type.value,
            'description': self.description,
            'voi_score': self.voi_score,
            'affected_beliefs': self.affected_beliefs,
            'implied_by': self.implied_by,
        }


class _FakeGapPredictor:
    def __init__(self, gaps: list[_FakeGap]):
        self._gaps = gaps

    def find_all_gaps(self, max_gaps: int = 50):
        return SimpleNamespace(gaps=self._gaps[:max_gaps])


def _service(tmp_path):
    gaps = [
        _FakeGap(
            gap_id="g1",
            gap_type=GapType.VALIDATION,
            description="no empirical validation in healthcare settings",
            voi_score=0.77,
            affected_beliefs=["b1"],
            implied_by=[],
        )
    ]
    svc = ResearchQueueService(
        web=SimpleNamespace(beliefs={}),
        gap_predictor=_FakeGapPredictor(gaps),
        queue_path=tmp_path / "opportunity_queue.json",
        frameworks=[],
    )
    svc.refresh_queue(include_theory=False)
    return svc


def test_not_found_creates_opportunity_registry_entry(tmp_path):
    svc = _service(tmp_path)
    target = svc.get_next_target("collector:test")
    assert target is not None

    result = SearchResult(
        collector_id="collector:test",
        result_type=SearchResultType.NOT_FOUND,
        is_research_opportunity=True,
        research_opportunity_framing="Study needed for hospital wayfinding and anxiety",
        null_result_evidence=NullResultEvidence(
            n_databases_searched=3,
            n_queries_tried=10,
            n_results_screened=45,
            confidence_is_gap=0.91,
            suggested_study_design="cluster-randomized",
            suggested_population="hospital visitors",
            suggested_setting="hospital",
        ),
    )

    assessment = svc.report_search_result(target.target_id, result)
    assert assessment.became_research_opportunity is True

    opportunities = svc.list_research_opportunities()
    assert len(opportunities) == 1
    opp = opportunities[0]
    assert opp.source_target_id == target.target_id
    assert opp.status == OpportunityStatus.PROPOSED
    assert opp.suggested_design == "cluster-randomized"
    assert opp.suggested_population == "hospital visitors"
    assert "hospital" in opp.predicted_finding.lower()


def test_opportunity_status_updates_and_persists(tmp_path):
    svc = _service(tmp_path)
    target = svc.get_next_target("collector:test")
    assert target is not None

    svc.report_search_result(
        target.target_id,
        SearchResult(
            collector_id="collector:test",
            result_type=SearchResultType.NOT_FOUND,
            is_research_opportunity=True,
            research_opportunity_framing="Study required",
        ),
    )
    opportunity = svc.list_research_opportunities()[0]

    updated = svc.update_research_opportunity(
        opportunity.opportunity_id,
        status=OpportunityStatus.IN_PROGRESS,
        researcher_contact="lab@example.edu",
    )
    assert updated is not None
    assert updated.status == OpportunityStatus.IN_PROGRESS
    assert updated.researcher_contact == "lab@example.edu"

    updated2 = svc.update_research_opportunity(
        opportunity.opportunity_id,
        publication_doi="10.1111/new.study",
    )
    assert updated2 is not None
    assert updated2.status == OpportunityStatus.PUBLISHED
    assert updated2.publication_doi == "10.1111/new.study"

    # Reload service from persisted state to verify durability.
    reloaded = ResearchQueueService(
        queue_path=tmp_path / "opportunity_queue.json",
        frameworks=[],
    )
    restored = reloaded.get_research_opportunity(opportunity.opportunity_id)
    assert restored is not None
    assert restored.status == OpportunityStatus.PUBLISHED
    assert restored.publication_doi == "10.1111/new.study"
