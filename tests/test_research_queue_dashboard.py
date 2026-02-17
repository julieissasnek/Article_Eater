from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

from src.epistemic.gap_types import GapType
from src.queue import CollectorProfile, CollectorType, ResearchQueueService, TargetStatus


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


def _service(tmp_path):
    svc = ResearchQueueService(
        web=SimpleNamespace(beliefs={}),
        gap_predictor=_FakeGapPredictor(
            [
                _FakeGap("g1", GapType.DIRECTION, "direction conflict", 0.9, ["b1"], []),
                _FakeGap("g2", GapType.MECHANISM, "missing mechanism", 0.5, ["b2"], []),
            ]
        ),
        queue_path=tmp_path / "dashboard_queue.json",
        frameworks=[],
    )
    svc.refresh_queue(include_theory=False)
    return svc


def test_dashboard_snapshot_counts(tmp_path):
    svc = _service(tmp_path)
    snapshot = svc.get_dashboard_snapshot()

    assert snapshot["n_targets"] == 2
    assert snapshot["by_status"]["open"] == 2
    assert snapshot["by_priority"]["high"] == 1
    assert snapshot["by_priority"]["medium"] == 1


def test_set_target_status_and_collector_count(tmp_path):
    svc = _service(tmp_path)
    svc.register_collector(
        CollectorProfile(
            collector_id="collector:1",
            collector_type=CollectorType.HUMAN_ASSISTANT,
            name="Collector 1",
            can_access_databases=["semantic_scholar"],
            max_concurrent_targets=1,
            typical_turnaround_hours=12,
        )
    )

    updated = svc.set_target_status("gap:g1", TargetStatus.CLOSED)
    assert updated is not None
    assert updated.status == TargetStatus.CLOSED

    snapshot = svc.get_dashboard_snapshot()
    assert snapshot["n_collectors"] == 1
    assert snapshot["by_status"]["closed"] == 1
