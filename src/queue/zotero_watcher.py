"""Zotero watcher for Research Queue synchronization.

This implementation watches a BibTeX export file (typically from Zotero),
tracks newly seen entries, and auto-matches additions to open queue targets.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.queue.models import ArticleReference, SearchResult, SearchResultType, TargetStatus
from src.services.bibtex_utils import BibTeXEntry, BibTeXParser

logger = logging.getLogger(__name__)


def _iso_z(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class ZoteroWatcher:
    """Detect new BibTeX entries and match them against queue targets."""

    def __init__(
        self,
        bibtex_path: str | Path,
        state_path: str | Path = "data/production/zotero_watcher_state.json",
    ):
        self.bibtex_path = Path(bibtex_path)
        self.state_path = Path(state_path)
        self._parser = BibTeXParser()

    def scan_new_entries(self) -> list[BibTeXEntry]:
        """Return entries not seen in previous watcher scans."""
        if not self.bibtex_path.exists():
            logger.warning("ZoteroWatcher: BibTeX file not found: %s", self.bibtex_path)
            return []

        content = self.bibtex_path.read_text(encoding="utf-8", errors="ignore")
        entries = self._parser.parse(content)
        state = self._load_state()
        seen = set(state.get("seen_keys", []))

        new_entries: list[BibTeXEntry] = []
        all_keys: set[str] = set()
        for entry in entries:
            key = self._entry_key(entry)
            if not key:
                continue
            all_keys.add(key)
            if key not in seen:
                new_entries.append(entry)

        self._save_state(
            {
                "seen_keys": sorted(all_keys),
                "last_scanned_at": _iso_z(datetime.now(timezone.utc)),
                "bibtex_path": str(self.bibtex_path),
                "total_entries": len(entries),
            }
        )
        return new_entries

    def match_entries_to_targets(
        self,
        entries: list[BibTeXEntry],
        targets: list[Any],
        min_score: float = 0.18,
    ) -> dict[str, list[ArticleReference]]:
        """Match new entries to target descriptions and query terms."""
        by_target: dict[str, list[ArticleReference]] = {}

        for target in targets:
            if getattr(target, "status", None) not in {TargetStatus.OPEN, TargetStatus.SEARCHING}:
                continue

            target_tokens = self._target_tokens(target)
            if not target_tokens:
                continue

            matches: list[ArticleReference] = []
            for entry in entries:
                score = self._entry_match_score(entry, target_tokens)
                if score < min_score:
                    continue
                matches.append(self._entry_to_reference(entry, score, target))

            if matches:
                matches.sort(key=lambda r: r.relevance_score, reverse=True)
                by_target[getattr(target, "target_id")] = matches

        return by_target

    def sync_to_queue(
        self,
        queue_service: Any,
        collector_id: str = "zotero_watcher",
        min_score: float = 0.18,
    ) -> list[ArticleReference]:
        """Apply new Zotero matches to queue state and return matched references."""
        new_entries = self.scan_new_entries()
        if not new_entries:
            return []

        targets = queue_service.list_targets()
        matches = self.match_entries_to_targets(new_entries, targets, min_score=min_score)

        all_refs: list[ArticleReference] = []
        for target_id, refs in matches.items():
            all_refs.extend(refs)
            queue_service.report_search_result(
                target_id=target_id,
                result=SearchResult(
                    collector_id=collector_id,
                    result_type=SearchResultType.FOUND_RELEVANT,
                    queries_used=["zotero_passive_sync"],
                    databases_searched=["zotero"],
                    time_spent_minutes=0,
                    articles_found=refs,
                    confidence=max(r.relevance_score for r in refs),
                    notes="Auto-matched from Zotero watcher BibTeX delta",
                ),
            )

        return all_refs

    def _entry_key(self, entry: BibTeXEntry) -> str:
        if entry.doi:
            return f"doi:{entry.doi.strip().lower()}"
        if entry.cite_key:
            return f"cite:{entry.cite_key.strip().lower()}"
        title = (entry.title or "").strip().lower()
        if title:
            year = str(entry.year or "")
            return f"title:{title}:{year}"
        return ""

    def _target_tokens(self, target: Any) -> set[str]:
        parts: list[str] = []
        parts.append(getattr(target, "gap_description", "") or "")
        parts.extend(list(getattr(target, "suggested_queries", []) or []))
        parts.extend(list(getattr(target, "mechanism_predictions", []) or []))
        parts.extend(list(getattr(target, "cross_field_terms", []) or []))
        return self._tokenize(" ".join(parts))

    def _entry_match_score(self, entry: BibTeXEntry, target_tokens: set[str]) -> float:
        entry_text = " ".join(
            [
                entry.title or "",
                entry.abstract or "",
                " ".join(entry.keywords or []),
                entry.journal or "",
                entry.booktitle or "",
            ]
        )
        entry_tokens = self._tokenize(entry_text)
        if not entry_tokens or not target_tokens:
            return 0.0

        overlap = len(entry_tokens.intersection(target_tokens))
        return overlap / float(len(target_tokens))

    def _entry_to_reference(self, entry: BibTeXEntry, score: float, target: Any) -> ArticleReference:
        authors = entry.authors or ([entry.author] if entry.author else [])
        return ArticleReference(
            doi=entry.doi,
            title=entry.title or entry.cite_key,
            authors=[a for a in authors if a],
            year=entry.year,
            venue=entry.journal or entry.booktitle or entry.publisher or "",
            relevance_score=round(min(max(score, 0.0), 1.0), 4),
            relevance_rationale=(
                f"token overlap with target '{getattr(target, 'target_id', 'unknown')}'"
            ),
            pdf_available=bool(entry.file),
            pdf_path=entry.file,
            retrieval_method="zotero",
            addresses_gap=True,
            gap_closure_estimate=min(1.0, max(0.2, score * 1.3)),
        )

    def _tokenize(self, text: str) -> set[str]:
        raw = re.findall(r"[a-zA-Z][a-zA-Z0-9_\-]+", (text or "").lower())
        stop = {
            "the",
            "and",
            "for",
            "with",
            "from",
            "this",
            "that",
            "into",
            "architecture",
            "study",
            "effect",
            "effects",
        }
        return {t for t in raw if len(t) > 3 and t not in stop}

    def _load_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return {}
        try:
            with self.state_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_state(self, payload: dict[str, Any]) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        with self.state_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=True)
            f.write("\n")


__all__ = ["ZoteroWatcher"]
