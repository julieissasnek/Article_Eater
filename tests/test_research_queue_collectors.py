from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from src.epistemic.gap_types import GapType
from src.queue import CollectorProfile, CollectorType, ResearchQueueService, TargetStatus
from tests.conftest import FakeGap, FakeGapPredictor






def _make_service(tmp_path, gaps: list[FakeGap]):
    return ResearchQueueService(
        web=SimpleNamespace(beliefs={}),
        gap_predictor=FakeGapPredictor(gaps),
        queue_path=tmp_path / "collector_queue_state.json",
        frameworks=[],
    )


def test_claim_target_requires_registered_collector(tmp_path):
    service = _make_service(
        tmp_path,
        [FakeGap("g1", GapType.MECHANISM, "missing mechanism", 0.7, ["b1"], [])],
    )
    service.refresh_queue(include_theory=False)

    result = service.claim_target("unknown_collector")
    assert result.success is False
    assert "not registered" in result.message


def test_register_and_claim_target_returns_guidance(tmp_path):
    service = _make_service(
        tmp_path,
        [FakeGap("g1", GapType.VALIDATION, "unfamiliar layouts increase anxiety", 0.82, ["b1"], [])],
    )
    service.refresh_queue(include_theory=False)

    collector = CollectorProfile(
        collector_id="ra_1",
        collector_type=CollectorType.HUMAN_ASSISTANT,
        name="RA One",
        can_access_databases=["semantic_scholar", "zotero"],
        max_concurrent_targets=2,
        typical_turnaround_hours=12,
    )
    service.register_collector(collector)

    claim = service.claim_target("ra_1")
    assert claim.success is True
    assert claim.target is not None
    assert claim.search_guidance is not None
    assert claim.target.status == TargetStatus.SEARCHING
    assert claim.target.assigned_to == "ra_1"
    assert "semantic_scholar" in claim.search_guidance.databases
    assert claim.deadline is not None
    assert claim.deadline > datetime.now(timezone.utc)


def test_claim_respects_collector_capacity(tmp_path):
    service = _make_service(
        tmp_path,
        [
            FakeGap("g1", GapType.VALIDATION, "missing validation one", 0.9, ["b1"], []),
            FakeGap("g2", GapType.MECHANISM, "missing mechanism two", 0.8, ["b2"], []),
        ],
    )
    service.refresh_queue(include_theory=False)

    collector = CollectorProfile(
        collector_id="bot_1",
        collector_type=CollectorType.AUTOMATED_SEARCHER,
        name="Bot One",
        can_access_databases=["semantic_scholar"],
        max_concurrent_targets=1,
        typical_turnaround_hours=2,
    )
    service.register_collector(collector)

    first = service.claim_target("bot_1")
    assert first.success is True

    second = service.claim_target("bot_1")
    assert second.success is False
    assert "capacity" in second.message


def test_claim_specific_target_id(tmp_path):
    service = _make_service(
        tmp_path,
        [
            FakeGap("g1", GapType.BOUNDARY, "boundary issue one", 0.5, ["b1"], []),
            FakeGap("g2", GapType.MECHANISM, "mechanism issue two", 0.6, ["b2"], []),
        ],
    )
    service.refresh_queue(include_theory=False)

    collector = CollectorProfile(
        collector_id="human_1",
        collector_type=CollectorType.HUMAN_RESEARCHER,
        name="Human One",
        can_access_databases=["pubmed", "semantic_scholar"],
        max_concurrent_targets=2,
    )
    service.register_collector(collector)

    claim = service.claim_target("human_1", target_id="gap:g1")
    assert claim.success is True
    assert claim.target is not None
    assert claim.target.target_id == "gap:g1"
