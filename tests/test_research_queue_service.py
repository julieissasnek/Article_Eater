from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

from src.epistemic.gap_types import GapType
from src.queue import (
    ArticleReference,
    NullResultEvidence,
    ResearchQueueService,
    SearchResult,
    SearchResultType,
    TargetStatus,
)


@dataclass
class _FakeGap:
    gap_id: str
    gap_type: GapType
    description: str
    voi_score: float
    affected_beliefs: list[str]
    implied_by: list[str]

    def to_dict(self) -> dict:
        """Support serialization if needed."""
        return {
            "gap_id": self.gap_id,
            "gap_type": self.gap_type.value,
            "description": self.description,
            "voi_score": self.voi_score,
            "affected_beliefs": self.affected_beliefs,
            "implied_by": self.implied_by,
        }


class _FakeGapPredictor:
    def __init__(self, gaps: list[_FakeGap]):
        self._gaps = gaps

    def find_all_gaps(self, max_gaps: int = 50):
        return SimpleNamespace(gaps=self._gaps[:max_gaps])


def _make_service(tmp_path, gaps: list[_FakeGap], frameworks=None, web=None):
    return ResearchQueueService(
        web=web,
        gap_predictor=_FakeGapPredictor(gaps),
        queue_path=tmp_path / "research_queue.json",
        frameworks=frameworks,
    )


def test_refresh_queue_prioritizes_and_assigns(tmp_path):
    gaps = [
        _FakeGap("g1", GapType.DIRECTION, "Direction conflict on stress", 0.85, ["b1"], ["x->y"]),
        _FakeGap("g2", GapType.MECHANISM, "Mechanism missing", 0.52, ["b2"], []),
        _FakeGap("g3", GapType.BOUNDARY, "Boundary unknown", 0.20, ["b3"], []),
    ]

    service = _make_service(tmp_path, gaps)
    state = service.refresh_queue(include_theory=False)

    assert len(state.high_priority) == 1
    assert len(state.medium_priority) == 1
    assert len(state.low_priority) == 1
    assert state.n_open == 3

    assigned = service.get_next_target("collector:alpha")
    assert assigned is not None
    assert assigned.gap_id == "g1"
    assert assigned.status == TargetStatus.SEARCHING
    assert assigned.assigned_to == "collector:alpha"


def test_report_search_result_found(tmp_path):
    gaps = [
        _FakeGap("g1", GapType.MECHANISM, "Mechanism missing", 0.75, ["b1"], []),
    ]
    service = _make_service(tmp_path, gaps)
    service.refresh_queue(include_theory=False)
    target = service.get_next_target("collector:beta")
    assert target is not None

    result = SearchResult(
        collector_id="collector:beta",
        result_type=SearchResultType.FOUND_RELEVANT,
        articles_found=[
            ArticleReference(
                doi="10.1000/test",
                title="Mechanism evidence",
                relevance_score=0.9,
                addresses_gap=True,
            )
        ],
        confidence=0.9,
    )

    assessment = service.report_search_result(target.target_id, result)
    assert assessment.status == TargetStatus.FOUND
    assert assessment.n_articles_found == 1


def test_report_search_result_not_found_creates_research_opportunity(tmp_path):
    gaps = [
        _FakeGap("g1", GapType.VALIDATION, "Missing validation", 0.73, ["b1"], []),
    ]
    service = _make_service(tmp_path, gaps)
    service.refresh_queue(include_theory=False)
    target = service.get_next_target("collector:gamma")
    assert target is not None

    result = SearchResult(
        collector_id="collector:gamma",
        result_type=SearchResultType.NOT_FOUND,
        null_result_evidence=NullResultEvidence(
            n_databases_searched=3,
            n_queries_tried=12,
            n_results_screened=60,
            confidence_is_gap=0.92,
            suggested_study_design="quasi-experimental",
        ),
        confidence=0.8,
        is_research_opportunity=True,
        research_opportunity_framing="Study needed: validate prediction in hospital settings",
    )

    assessment = service.report_search_result(target.target_id, result)
    assert assessment.status == TargetStatus.STALE
    assert assessment.became_research_opportunity is True

    updated = service.get_target(target.target_id)
    assert updated is not None
    assert updated.is_research_opportunity is True
    assert "hospital settings" in (updated.opportunity_framing or "")


def test_theory_gap_detection_only_returns_unsupported_predictions(tmp_path):
    class _Prediction:
        def __init__(self, prediction_id: str, statement: str):
            self.prediction_id = prediction_id
            self.statement = statement

    class _Framework:
        theory_id = "framework:test"
        name = "Test Framework"
        overall_confidence = 0.9

        def __init__(self):
            self.all_predictions = [
                _Prediction("p1", "daylight exposure improves learning outcomes"),
                _Prediction("p2", "unfamiliar layouts increase anxiety in hospitals"),
            ]

    # First prediction has direct support; second should remain as a gap.
    belief = SimpleNamespace(
        content="Daylight exposure improves learning outcomes in schools",
        credence=SimpleNamespace(value=0.88),
        theory_id="framework:test",
    )
    web = SimpleNamespace(beliefs={"b1": belief})

    service = _make_service(tmp_path, gaps=[], frameworks=[_Framework()], web=web)
    targets = service.get_theory_predictions("framework:test")

    assert len(targets) == 1
    assert "increase anxiety" in targets[0].gap_description.lower()
    assert targets[0].gap_type == GapType.VALIDATION


def test_refresh_queue_reports_theory_coverage(tmp_path):
    class _Prediction:
        def __init__(self, prediction_id: str, statement: str):
            self.prediction_id = prediction_id
            self.statement = statement

    class _Framework:
        theory_id = "framework:test"
        name = "Test Framework"
        overall_confidence = 0.9

        def __init__(self):
            self.all_predictions = [
                _Prediction("p1", "daylight improves attention"),
                _Prediction("p2", "crowding increases stress hormones"),
            ]

    belief = SimpleNamespace(
        content="Daylight improves attention in classrooms",
        credence=SimpleNamespace(value=0.9),
        theory_id="framework:test",
    )
    web = SimpleNamespace(beliefs={"b1": belief})

    service = _make_service(tmp_path, gaps=[], frameworks=[_Framework()], web=web)
    state = service.refresh_queue(include_theory=True)

    assert state.theory_coverage["framework:test"] == 0.5
