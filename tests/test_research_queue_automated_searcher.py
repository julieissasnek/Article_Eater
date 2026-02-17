from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

from src.epistemic.gap_types import GapType
from src.queue import AutomatedQueueSearcher, AutomatedSearcherConfig, ResearchQueueService, TargetStatus


@dataclass
class _FakeGap:
    gap_id: str
    gap_type: GapType
    description: str
    voi_score: float
    affected_beliefs: list[str]
    implied_by: list[str]


class _FakeGapPredictor:
    def __init__(self, gaps: list[_FakeGap]):
        self._gaps = gaps

    def find_all_gaps(self, max_gaps: int = 50):
        return SimpleNamespace(gaps=self._gaps[:max_gaps])


def _service(tmp_path, gaps):
    svc = ResearchQueueService(
        web=SimpleNamespace(beliefs={}),
        gap_predictor=_FakeGapPredictor(gaps),
        queue_path=tmp_path / "auto_searcher_queue.json",
        frameworks=[],
    )
    svc.refresh_queue(include_theory=False)
    return svc


def test_automated_searcher_finds_candidates(tmp_path):
    service = _service(
        tmp_path,
        [
            _FakeGap(
                "g1",
                GapType.VALIDATION,
                "unfamiliar hospital layouts increase anxiety",
                0.82,
                ["b1"],
                [],
            )
        ],
    )

    def fake_search(query: str, limit: int = 10, **kwargs):
        return [
            {
                "title": "Hospital wayfinding unfamiliar layouts and anxiety",
                "authors": [{"name": "A. Author"}],
                "year": 2025,
                "abstract": "Examines anxiety and unfamiliar layouts in hospitals.",
                "externalIds": {"DOI": "10.1000/fake1"},
                "citationCount": 33,
                "url": "https://example.org/paper1",
            }
        ]

    bot = AutomatedQueueSearcher(
        queue_service=service,
        search_fn=fake_search,
        config=AutomatedSearcherConfig(
            max_targets_per_run=1,
            max_queries_per_target=2,
            max_results_per_query=5,
            min_relevance=0.2,
        ),
    )

    runs = bot.run_once()
    assert len(runs) == 1
    assert runs[0].n_candidates >= 1
    assert runs[0].status == TargetStatus.FOUND.value


def test_automated_searcher_not_found_creates_opportunity(tmp_path):
    service = _service(
        tmp_path,
        [_FakeGap("g1", GapType.MECHANISM, "missing mechanism for daylight and stress", 0.75, ["b1"], [])],
    )

    def fake_search(query: str, limit: int = 10, **kwargs):
        return []

    bot = AutomatedQueueSearcher(
        queue_service=service,
        search_fn=fake_search,
        config=AutomatedSearcherConfig(max_targets_per_run=1),
    )

    runs = bot.run_once()
    assert len(runs) == 1
    assert runs[0].status == TargetStatus.STALE.value

    opportunities = service.list_research_opportunities()
    assert len(opportunities) == 1
    assert opportunities[0].source_target_id == "gap:g1"
