"""
Scholarly-time entrenchment replay (stub).

Rebuilds the web in publication order to estimate historical entrenchment
trajectories. Use a separate replay DB to avoid mutating the live master web.
"""

from __future__ import annotations

import copy
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from src.services.web_of_belief import WebOfBelief
from src.services.web_persistence import WebPersistenceService

logger = logging.getLogger(__name__)

PaperWebLoader = Callable[[str], Optional[WebOfBelief]]


class ScholarlyReplayService:
    """
    Replay entrenchment in publication order.

    NOTE: integrate_paper_web writes to the master web. Use a separate DB path
    for replay unless you explicitly want to mutate the live master.
    """

    def __init__(
        self,
        source_db_path: str = "ae.db",
        replay_db_path: Optional[str] = None
    ) -> None:
        self.source_db_path = source_db_path
        self.replay_db_path = replay_db_path or source_db_path
        self.source = WebPersistenceService(source_db_path)
        self.replay_db = WebPersistenceService(self.replay_db_path)
        self._same_db = (source_db_path == self.replay_db_path)

    @classmethod
    def with_safe_replay_copy(
        cls,
        source_db_path: str = "ae.db",
        replay_db_path: Optional[str] = None,
        copy_dir: str = "data/replay",
        overwrite: bool = False
    ) -> "ScholarlyReplayService":
        """
        Create a replay service using a copied DB to avoid live mutation.

        If replay_db_path is omitted, a timestamped copy is created under copy_dir.
        """
        source = Path(source_db_path).expanduser().resolve()
        if not source.exists():
            raise FileNotFoundError(f"Source DB not found: {source}")

        if replay_db_path:
            target = Path(replay_db_path).expanduser().resolve()
        else:
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            target = Path(copy_dir).expanduser().resolve() / f"entrenchment_replay_{stamp}.db"

        if source == target:
            raise ValueError("Replay DB path must differ from source DB path.")

        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and not overwrite:
            raise FileExistsError(
                f"Replay DB already exists: {target}. "
                "Use overwrite=True or choose a different path."
            )

        shutil.copy2(source, target)
        logger.info("Created replay DB copy: %s -> %s", source, target)
        return cls(source_db_path=str(source), replay_db_path=str(target))

    def get_publication_order(
        self,
        paper_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Return paper publications ordered by scholarly time."""
        return self.source.list_paper_publications(paper_ids)

    def make_master_filtered_loader(self) -> PaperWebLoader:
        """
        Build a loader from source master web filtered by paper_id.

        This provides a self-contained fallback when paper-level web artifacts
        are not available as separate files.
        """
        master_id = self.source.get_master_web_id()
        if not master_id:
            return lambda _: None

        master_web, _ = self.source.load_web(master_id)
        if not master_web:
            return lambda _: None

        def _loader(paper_id: str) -> Optional[WebOfBelief]:
            belief_ids = {
                belief.belief_id
                for belief in master_web.beliefs.values()
                if paper_id in getattr(belief, "paper_ids", [])
            }
            if not belief_ids:
                return None

            paper_web = WebOfBelief()
            for belief_id in belief_ids:
                belief = master_web.beliefs.get(belief_id)
                if belief:
                    paper_web.add_belief(copy.deepcopy(belief))

            for constraint in master_web.constraints.values():
                if (
                    constraint.source_id in belief_ids
                    and constraint.target_id in belief_ids
                ):
                    paper_web.add_constraint(copy.deepcopy(constraint))

            return paper_web

        return _loader

    def replay(
        self,
        paper_web_loader: PaperWebLoader,
        paper_ids: Optional[List[str]] = None,
        limit: Optional[int] = None,
        allow_mutating_master: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Replay entrenchment history in publication order.

        Args:
            paper_web_loader: Callback that returns a per-paper WebOfBelief
            paper_ids: Optional list of paper IDs to replay
            limit: Optional max papers to replay
            allow_mutating_master: Set True to run against live DB

        Returns:
            List of integration reports (dicts)
        """
        if self._same_db and not allow_mutating_master:
            raise ValueError(
                "Replay would mutate the live master web. "
                "Provide replay_db_path or set allow_mutating_master=True."
            )

        publications = self.get_publication_order(paper_ids)
        if limit is not None:
            publications = publications[:limit]

        reports: List[Dict[str, Any]] = []
        for pub in publications:
            paper_id = pub["paper_id"]
            paper_web = paper_web_loader(paper_id)
            if not paper_web:
                logger.warning("Replay skip: no paper web for %s", paper_id)
                continue

            report = self.replay_db.integrate_paper_web(
                paper_web,
                paper_id,
                publication_year=pub.get("publication_year"),
                publication_date=pub.get("publication_date"),
                first_seen_at=pub.get("first_seen_at"),
                metadata_source=pub.get("source")
            )

            master_id = self.replay_db.get_master_web_id()
            master_web, _ = self.replay_db.load_web(master_id) if master_id else (None, None)

            as_of_date = pub.get("publication_date")
            if not as_of_date and pub.get("publication_year"):
                as_of_date = f"{pub['publication_year']}-01-01"
            if not as_of_date:
                as_of_date = datetime.now(timezone.utc).date().isoformat()

            if master_web:
                belief_ids = [
                    b.belief_id for b in master_web.beliefs.values()
                    if paper_id in getattr(b, "paper_ids", [])
                ]
                if belief_ids:
                    self.replay_db.record_entrenchment_snapshots(
                        web_id=master_id,
                        web=master_web,
                        belief_ids=belief_ids,
                        paper_id=paper_id,
                        timeline_type="scholarly",
                        as_of_date=as_of_date,
                        event_type="historical_replay",
                        reason="scholarly_replay"
                    )

            reports.append({
                "paper_id": paper_id,
                "n_beliefs_added": report.n_beliefs_added,
                "n_beliefs_updated": report.n_beliefs_updated,
                "n_constraints_added": report.n_constraints_added,
                "coherence_before": report.coherence_before,
                "coherence_after": report.coherence_after,
            })

        return reports
