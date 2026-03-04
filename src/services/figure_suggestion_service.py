"""
Figure Suggestion Service
=========================

Suggests relevant figures, tables, and visual assets for enriched answers.

Architecture:
1. On init, builds a lightweight figure index from the extraction corpus
2. Index maps topic keywords → figure references + paper metadata
3. Queries match topic words against the index (O(1) vs O(N) corpus scan)

This replaces the inline fallback in the enrichment orchestrator that
scanned up to 200 random JSON files per query — an O(N) operation that
was also unreliable because it relied on brittle word overlap heuristics.

SUCCESS CONDITIONS:
SC-FIG-1: __init__ builds figure index from data/extractions/ if available
SC-FIG-2: suggest_figures_for_topic returns list of dicts
SC-FIG-3: Each dict has keys: figure_id, title, relevance_score, path
SC-FIG-4: Results are sorted by relevance_score descending
SC-FIG-5: Index build is cached (not rebuilt per query)
SC-FIG-6: Graceful degradation if no extractions exist (returns [])
SC-FIG-7: Respects limit parameter
"""

from __future__ import annotations

import json
import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class FigureSuggestionService:
    """Indexed figure registry for fast topic-matched figure suggestions."""

    def __init__(self, extractions_dir: str = "data/extractions"):
        self._extractions_dir = Path(extractions_dir)
        self._index: Dict[str, List[Dict]] = defaultdict(list)  # keyword → figures
        self._all_figures: List[Dict] = []
        self._built = False

    def _ensure_index(self):
        """Build the figure index exactly once, on first query."""
        if self._built:
            return
        self._built = True

        if not self._extractions_dir.exists():
            logger.debug("No extractions dir found; figure index empty")
            return

        stopwords = {"the", "of", "and", "in", "on", "for", "a", "is", "to",
                      "by", "an", "at", "or", "be", "it", "as", "do", "no",
                      "if", "we", "so", "up", "are", "was", "has", "had",
                      "not", "but", "can", "all", "its", "more", "with",
                      "from", "this", "that", "than", "were", "been", "have"}

        count = 0
        for json_file in self._extractions_dir.glob("*.json"):
            try:
                with open(json_file) as f:
                    data = json.load(f)

                paper_title = data.get("title", json_file.stem)
                paper_id = json_file.stem

                # Collect paper-level keywords for relevance matching
                title_words = set(re.findall(r'\w{3,}', paper_title.lower())) - stopwords
                abstract_words = set(re.findall(
                    r'\w{3,}', (data.get("abstract") or "").lower()
                )) - stopwords
                paper_keywords = title_words | abstract_words

                # Extract figure references from findings
                for i, finding in enumerate(data.get("findings", [])):
                    fig_ref = finding.get("figure_reference") or finding.get("figure")
                    if not fig_ref:
                        continue

                    fig_text = finding.get("finding", "") or finding.get("description", "")
                    fig_entry = {
                        "figure_id": f"{paper_id}_fig_{fig_ref}" if fig_ref else f"{paper_id}_f{i}",
                        "title": f"{fig_text[:100]} (Fig. {fig_ref})" if fig_text else f"Figure {fig_ref}",
                        "path": str(json_file),
                        "paper_title": paper_title,
                        "paper_id": paper_id,
                        "fig_ref": str(fig_ref),
                        "keywords": paper_keywords | set(re.findall(
                            r'\w{3,}', fig_text.lower()
                        )) - stopwords,
                    }

                    self._all_figures.append(fig_entry)
                    count += 1

                    # Index by each keyword
                    for kw in fig_entry["keywords"]:
                        self._index[kw].append(fig_entry)

                # Also check for explicit tables
                for i, table in enumerate(data.get("tables", [])):
                    table_caption = table.get("caption", "") or table.get("title", "")
                    if not table_caption:
                        continue
                    table_entry = {
                        "figure_id": f"{paper_id}_table_{i}",
                        "title": f"{table_caption[:120]}",
                        "path": str(json_file),
                        "paper_title": paper_title,
                        "paper_id": paper_id,
                        "fig_ref": f"Table {i+1}",
                        "keywords": paper_keywords | set(re.findall(
                            r'\w{3,}', table_caption.lower()
                        )) - stopwords,
                    }
                    self._all_figures.append(table_entry)
                    for kw in table_entry["keywords"]:
                        self._index[kw].append(table_entry)
                    count += 1

            except Exception as e:
                logger.debug(f"Failed to index {json_file}: {e}")
                continue

        logger.info(f"Figure index built: {count} entries from {len(list(self._extractions_dir.glob('*.json')))} files")

    def suggest_figures_for_topic(
        self, topic: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find figures relevant to a topic using the pre-built index.

        Args:
            topic: The topic to find figures for
            limit: Maximum number of figures to return

        Returns:
            List of {figure_id, title, relevance_score, path} dicts
        """
        self._ensure_index()

        if not self._all_figures:
            return []

        stopwords = {"the", "of", "and", "in", "on", "for", "a", "is", "to",
                      "how", "does", "what", "do", "why", "are", "which", "when"}
        topic_words = set(re.findall(r'\w{3,}', topic.lower())) - stopwords
        if not topic_words:
            return []

        # Score each figure by keyword overlap (using the index for speed)
        scores: Dict[str, float] = defaultdict(float)
        candidates: Dict[str, Dict] = {}

        for tw in topic_words:
            for fig_entry in self._index.get(tw, []):
                fid = fig_entry["figure_id"]
                scores[fid] += 1.0
                candidates[fid] = fig_entry

        if not candidates:
            return []

        # Normalize scores by number of topic words
        max_possible = len(topic_words)
        results = []
        for fid, fig_entry in candidates.items():
            raw_score = scores[fid]
            relevance = min(raw_score / max(max_possible, 1), 1.0)
            if relevance >= 0.3:  # Minimum threshold
                results.append({
                    "figure_id": fig_entry["figure_id"],
                    "title": fig_entry["title"],
                    "relevance_score": round(relevance, 3),
                    "path": fig_entry["path"],
                    "paper_title": fig_entry.get("paper_title", ""),
                })

        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:limit]
