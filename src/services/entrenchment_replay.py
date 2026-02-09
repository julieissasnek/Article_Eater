"""
Scholarly-time entrenchment replay (stub).

Rebuilds the web in publication order to estimate historical entrenchment
trajectories. Use a separate replay DB to avoid mutating the live master web.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Callable, Dict, Any, List, Optional

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
        self.source = WebPersistenceService(source_db_path)
        self.replay_db = WebPersistenceService(replay_db_path or source_db_path)
        self._same_db = (source_db_path == (replay_db_path or source_db_path))

    def get_publication_order(
        self,
        paper_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Return paper publications ordered by scholarly time."""
        return self.source.list_paper_publications(paper_ids)

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
