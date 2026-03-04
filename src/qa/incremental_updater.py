"""
Incremental Updater — On-Change MV Refresh
=============================================

When new articles are ingested, this module:
1. Identifies which topic clusters are affected
2. Marks those clusters' materialized views as STALE
3. The next nightly run rebuilds only STALE views

Usage:
    updater = IncrementalUpdater()
    updater.on_new_extraction("data/extractions/new_article.json")
    # Next nightly: builder.build_all(incremental=True) only rebuilds affected views
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List, Set

logger = logging.getLogger(__name__)


class IncrementalUpdater:
    """
    Tracks which materialized views need rebuilding when new data arrives.

    Uses the topic cluster classification from query_classifier to determine
    which pre-computed views are affected by new extractions.
    """

    def __init__(
        self,
        extractions_dir: str = "data/extractions",
        mv_dir: str = "data/materialized_views",
    ):
        self._extractions_dir = Path(extractions_dir)
        self._mv_dir = Path(mv_dir)
        self._mv_dir.mkdir(parents=True, exist_ok=True)

    def on_new_extraction(self, extraction_path: str) -> List[str]:
        """
        Process a new extraction and mark affected MV clusters as STALE.

        Args:
            extraction_path: Path to the new extraction JSON file

        Returns:
            List of affected topic cluster IDs
        """
        path = Path(extraction_path)
        if not path.exists():
            logger.warning(f"Extraction file not found: {extraction_path}")
            return []

        try:
            with open(path) as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to read extraction: {e}")
            return []

        # Find affected clusters
        affected = self._find_affected_clusters(data)

        if affected:
            # Mark MVs as stale
            self._mark_stale(affected)
            logger.info(
                f"New extraction {path.name}: "
                f"affected clusters: {affected}"
            )

            # Append to change log
            self._log_change(path.name, affected)

        return affected

    def get_pending_updates(self) -> List[str]:
        """Get list of clusters that need rebuilding."""
        log_path = self._mv_dir / "_pending_updates.json"
        if not log_path.exists():
            return []
        try:
            with open(log_path) as f:
                data = json.load(f)
            return data.get("stale_clusters", [])
        except Exception:
            return []

    def clear_pending(self):
        """Clear pending updates after rebuild."""
        log_path = self._mv_dir / "_pending_updates.json"
        if log_path.exists():
            log_path.unlink()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _find_affected_clusters(self, extraction_data: dict) -> List[str]:
        """Determine which topic clusters are affected by this extraction."""
        from src.qa.query_classifier import TOPIC_CLUSTERS

        affected: Set[str] = set()

        # Check theory links
        theories_in_extraction = set()
        for finding in extraction_data.get("findings", []):
            theories_in_extraction.update(finding.get("theory_links", []))

        for cluster_name, cluster_info in TOPIC_CLUSTERS.items():
            cluster_theories = set(cluster_info.get("theories", []))
            if cluster_theories & theories_in_extraction:
                affected.add(cluster_name)

        # Check domain overlap via keywords
        text = " ".join([
            extraction_data.get("title", ""),
            " ".join(
                f.get("antecedent", "") + " " + f.get("consequent", "")
                for f in extraction_data.get("findings", [])
            ),
        ]).lower()

        for cluster_name, cluster_info in TOPIC_CLUSTERS.items():
            for kw in cluster_info["keywords"]:
                if kw in text:
                    affected.add(cluster_name)
                    break

        return sorted(affected)

    def _mark_stale(self, clusters: List[str]):
        """Mark materialized views as STALE for affected clusters."""
        from src.qa.mv_builder import MaterializedViewBuilder
        builder = MaterializedViewBuilder(
            extractions_dir=str(self._extractions_dir),
            output_dir=str(self._mv_dir),
        )
        for cluster_id in clusters:
            builder.mark_stale(cluster_id)

    def _log_change(self, filename: str, affected_clusters: List[str]):
        """Log the change for tracking."""
        log_path = self._mv_dir / "_pending_updates.json"
        existing = {"stale_clusters": [], "changes": []}
        if log_path.exists():
            try:
                with open(log_path) as f:
                    existing = json.load(f)
            except Exception:
                pass

        # Merge stale clusters
        existing_stale = set(existing.get("stale_clusters", []))
        existing_stale.update(affected_clusters)
        existing["stale_clusters"] = sorted(existing_stale)

        # Log the change
        existing.setdefault("changes", []).append({
            "file": filename,
            "affected_clusters": affected_clusters,
        })

        with open(log_path, "w") as f:
            json.dump(existing, f, indent=2)
