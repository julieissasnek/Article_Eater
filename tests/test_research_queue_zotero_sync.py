from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

from src.epistemic.gap_types import GapType
from src.queue import ResearchQueueService, TargetStatus


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


def test_sync_zotero_to_queue_matches_new_bibtex_entries(tmp_path):
    bib_path = tmp_path / "zotero_export.bib"
    state_path = tmp_path / "zotero_state.json"

    bib_path.write_text(
        """
@article{smith2025,
  title={Unfamiliar hospital layouts increase anxiety and navigation burden},
  author={Smith, Jane and Doe, Alex},
  year={2025},
  journal={Journal of Healthcare Design},
  doi={10.1234/example.2025.1},
  abstract={We show that unfamiliar layouts increase anxiety in hospital visitors.}
}
""".strip(),
        encoding="utf-8",
    )

    gaps = [
        _FakeGap(
            gap_id="g1",
            gap_type=GapType.VALIDATION,
            description="unfamiliar layouts increase anxiety in hospitals",
            voi_score=0.78,
            affected_beliefs=["b1"],
            implied_by=[],
        )
    ]

    service = ResearchQueueService(
        web=SimpleNamespace(beliefs={}),
        gap_predictor=_FakeGapPredictor(gaps),
        queue_path=tmp_path / "queue_state.json",
        frameworks=[],
    )
    service.refresh_queue(include_theory=False)

    matches = service.sync_zotero_to_queue(
        bibtex_path=bib_path,
        state_path=state_path,
        collector_id="zotero_watcher",
        min_score=0.12,
    )

    assert len(matches) == 1
    assert matches[0].doi == "10.1234/example.2025.1"

    target = service.get_target("gap:g1")
    assert target is not None
    assert target.status == TargetStatus.FOUND

    # Second sync with unchanged BibTeX should return no new matches.
    second_matches = service.sync_zotero_to_queue(
        bibtex_path=bib_path,
        state_path=state_path,
        collector_id="zotero_watcher",
        min_score=0.12,
    )
    assert second_matches == []
