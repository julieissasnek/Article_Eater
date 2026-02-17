"""Paper processing history API (Sprint 13 Task 13.4)."""

from __future__ import annotations

from typing import Iterable

from sqlalchemy.orm import Session

from src.cmr.models import PaperRecord, get_session


def create_paper_record(
    *,
    n_claims: int,
    n_matched: int,
    n_unmatched: int,
    n_contradictions: int,
    n_confirmations: int,
    n_gaps: int,
    aggregate_voi: float,
    proposals_generated: int,
    matched_template_ids: Iterable[str] | None = None,
    citation: str | None = None,
    doi: str | None = None,
    db_path: str = "ae.db",
    session: Session | None = None,
) -> PaperRecord:
    """Persist a processed-paper history record."""
    own_session = session is None
    session = session or get_session(db_path)
    try:
        record = PaperRecord(
            citation=citation,
            doi=doi,
            n_claims=int(n_claims),
            n_matched=int(n_matched),
            n_unmatched=int(n_unmatched),
            n_contradictions=int(n_contradictions),
            n_confirmations=int(n_confirmations),
            n_gaps=int(n_gaps),
            aggregate_voi=float(aggregate_voi),
            proposals_generated=int(proposals_generated),
            matched_template_ids=sorted(set(matched_template_ids or [])),
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        return record
    finally:
        if own_session:
            session.close()


def get_processed_papers(
    *,
    db_path: str = "ae.db",
    session: Session | None = None,
    limit: int | None = None,
) -> list[PaperRecord]:
    """Return processed papers ordered by newest first."""
    own_session = session is None
    session = session or get_session(db_path)
    try:
        query = session.query(PaperRecord).order_by(PaperRecord.evaluated_at.desc(), PaperRecord.id.desc())
        if limit is not None:
            query = query.limit(limit)
        return list(query.all())
    finally:
        if own_session:
            session.close()


def get_papers_for_template(
    template_id: str,
    *,
    db_path: str = "ae.db",
    session: Session | None = None,
) -> list[PaperRecord]:
    """Return processed papers that matched a given template ID."""
    normalized = str(template_id or "").strip().upper()
    if not normalized:
        return []

    records = get_processed_papers(db_path=db_path, session=session)
    matched: list[PaperRecord] = []
    for record in records:
        ids = {str(item).strip().upper() for item in (record.matched_template_ids or [])}
        if normalized in ids:
            matched.append(record)
    return matched


def get_high_voi_papers(
    min_voi: float,
    *,
    db_path: str = "ae.db",
    session: Session | None = None,
) -> list[PaperRecord]:
    """Return papers whose aggregate VOI meets or exceeds threshold."""
    own_session = session is None
    session = session or get_session(db_path)
    try:
        threshold = float(min_voi)
        return list(
            session.query(PaperRecord)
            .filter(PaperRecord.aggregate_voi >= threshold)
            .order_by(PaperRecord.aggregate_voi.desc(), PaperRecord.evaluated_at.desc(), PaperRecord.id.desc())
            .all()
        )
    finally:
        if own_session:
            session.close()


__all__ = [
    "create_paper_record",
    "get_processed_papers",
    "get_papers_for_template",
    "get_high_voi_papers",
]
