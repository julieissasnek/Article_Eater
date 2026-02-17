"""Star rating advancement tracker (Sprint 13 Task 13.11).

Builds per-domain advancement guidance from:
- docs/52_Registry_Addendum_V2_2.md (revised coverage scorecard)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any


DEFAULT_REGISTRY_PATH = Path("docs/52_Registry_Addendum_V2_2.md")
GLOBAL_BLOCKER = "architectural-context validation is missing"


@dataclass(frozen=True)
class DomainStarProgress:
    """Current domain coverage and advancement requirements."""

    domain_id: str
    domain_name: str
    current_stars: float
    next_star_target: float | None
    stars_needed: float
    what_needed_for_next_star: str
    blockers: list[str]
    estimated_effort: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "domain_id": self.domain_id,
            "domain_name": self.domain_name,
            "current_stars": self.current_stars,
            "next_star_target": self.next_star_target,
            "stars_needed": self.stars_needed,
            "what_needed_for_next_star": self.what_needed_for_next_star,
            "blockers": list(self.blockers),
            "estimated_effort": self.estimated_effort,
        }


def _parse_star_symbol(raw: str) -> float:
    cleaned = str(raw or "").replace("*", "").strip()
    stars = float(cleaned.count("★"))
    if "½" in cleaned:
        stars += 0.5
    return stars


def _next_star_target(current: float) -> float | None:
    if current >= 5.0:
        return None
    integer = int(current)
    if current > integer:
        return float(integer + 1)
    return float(integer + 1)


def _estimate_effort(what_needed: str) -> str:
    text = (what_needed or "").lower()
    score = 0

    for token in ("field", "field-test", "field-validate", "architectural", "cross-cultural"):
        if token in text:
            score += 2

    for token in ("validate", "calibrate", "experiment", "measure", "psychophysical"):
        if token in text:
            score += 1

    if ";" in what_needed:
        score += 1

    if score >= 7:
        return "high (4+ quarters)"
    if score >= 4:
        return "medium (2-4 quarters)"
    return "low (1-2 quarters)"


def _extract_blockers(what_needed: str) -> list[str]:
    text = (what_needed or "").lower()
    blockers: list[str] = [GLOBAL_BLOCKER]

    if "field" in text or "architectural" in text:
        blockers.append("missing field validation in built environments")
    if "cross-cultural" in text:
        blockers.append("cross-cultural generalization not validated")
    if "calibrate" in text:
        blockers.append("calibration parameters remain incomplete")
    if "experiment" in text or "measure" in text:
        blockers.append("targeted empirical testing not yet executed")
    if "psychophysical" in text:
        blockers.append("psychophysical boundary testing pending")

    # Keep ordering stable but remove duplicates.
    deduped: list[str] = []
    for blocker in blockers:
        if blocker not in deduped:
            deduped.append(blocker)
    return deduped


def _parse_scorecard_rows(doc_text: str) -> list[DomainStarProgress]:
    rows: list[DomainStarProgress] = []
    for line in doc_text.splitlines():
        if not line.startswith("| A"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue

        domain_cell, _previous, revised, gap = cells[:4]
        match = re.match(r"^(A\d+)\s+(.+)$", domain_cell)
        if not match:
            continue
        domain_id = match.group(1)
        domain_name = match.group(2)

        current = _parse_star_symbol(revised)
        next_target = _next_star_target(current)
        stars_needed = 0.0 if next_target is None else max(0.0, next_target - current)
        progress = DomainStarProgress(
            domain_id=domain_id,
            domain_name=domain_name,
            current_stars=current,
            next_star_target=next_target,
            stars_needed=stars_needed,
            what_needed_for_next_star=gap,
            blockers=_extract_blockers(gap),
            estimated_effort=_estimate_effort(gap),
        )
        rows.append(progress)
    return rows


def get_star_advancement_tracker(registry_path: str | Path = DEFAULT_REGISTRY_PATH) -> dict[str, Any]:
    """Return star advancement status for all domains from Registry Addendum V2.2."""
    path = Path(registry_path)
    text = path.read_text(encoding="utf-8")
    domains = _parse_scorecard_rows(text)

    if domains:
        average_stars = round(sum(item.current_stars for item in domains) / len(domains), 2)
    else:
        average_stars = 0.0

    return {
        "source_doc": str(path),
        "global_blocker": GLOBAL_BLOCKER,
        "average_stars": average_stars,
        "domain_count": len(domains),
        "domains": [item.to_dict() for item in domains],
    }


def get_domain_star_progress(domain_id: str, registry_path: str | Path = DEFAULT_REGISTRY_PATH) -> dict[str, Any] | None:
    """Return advancement details for one domain (e.g. A4)."""
    key = str(domain_id or "").strip().upper()
    tracker = get_star_advancement_tracker(registry_path=registry_path)
    for item in tracker["domains"]:
        if str(item.get("domain_id", "")).upper() == key:
            return item
    return None


__all__ = [
    "DomainStarProgress",
    "get_domain_star_progress",
    "get_star_advancement_tracker",
]
