"""
Batch Paper Processing (Sprint 13 Task 13.14).

Process all test paper claim files from data/test_papers/.
Report: total claims, template matches, update proposals generated,
which templates have most evidence, evidence gap map after processing.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from src.cmr.process_paper import process_paper, ProcessingResult


@dataclass
class BatchResult:
    """Result of batch paper processing."""

    papers_processed: int
    papers_succeeded: int
    papers_failed: int
    total_claims: int
    total_matched: int
    total_unmatched: int
    total_proposals: int
    template_evidence_counts: dict[str, int]  # template_id -> evidence count
    proposal_types: dict[str, int]  # proposal_type -> count
    failed_papers: list[str]
    paper_results: list[dict]
    processing_time_seconds: float
    processed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "papers_processed": self.papers_processed,
            "papers_succeeded": self.papers_succeeded,
            "papers_failed": self.papers_failed,
            "total_claims": self.total_claims,
            "total_matched": self.total_matched,
            "total_unmatched": self.total_unmatched,
            "total_proposals": self.total_proposals,
            "match_rate": self.total_matched / max(1, self.total_claims),
            "template_evidence_counts": self.template_evidence_counts,
            "proposal_types": self.proposal_types,
            "failed_papers": self.failed_papers,
            "paper_results": self.paper_results,
            "processing_time_seconds": self.processing_time_seconds,
            "processed_at": self.processed_at.isoformat(),
        }


def load_test_papers(test_papers_dir: str = "data/test_papers") -> list[dict]:
    """
    Load all test paper claim files from directory.

    Args:
        test_papers_dir: Directory containing test paper JSON files

    Returns:
        List of dicts with 'path', 'citation', 'claims', 'doi'
    """
    papers_dir = Path(test_papers_dir)
    if not papers_dir.exists():
        return []

    papers = []
    for json_file in sorted(papers_dir.glob("*.json")):
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))

            # Extract citation from filename if not in file
            citation = data.get("citation")
            if not citation:
                citation = json_file.stem.replace("_", " ").title()

            # Get claims
            claims = data.get("claims", [])
            if not claims and isinstance(data, list):
                claims = data

            papers.append({
                "path": str(json_file),
                "citation": citation,
                "claims": claims,
                "doi": data.get("doi"),
            })
        except Exception as e:
            papers.append({
                "path": str(json_file),
                "citation": json_file.stem,
                "claims": [],
                "doi": None,
                "error": str(e),
            })

    return papers


def process_batch(
    test_papers_dir: str = "data/test_papers",
    db_path: str = "ae.db",
    persist_proposals: bool = True,
) -> BatchResult:
    """
    Process all test papers in batch.

    Args:
        test_papers_dir: Directory containing test paper JSON files
        db_path: Database path for proposals
        persist_proposals: Whether to persist proposals to database

    Returns:
        BatchResult with aggregated statistics
    """
    import time

    start_time = time.time()

    papers = load_test_papers(test_papers_dir)

    papers_succeeded = 0
    papers_failed = 0
    total_claims = 0
    total_matched = 0
    total_unmatched = 0
    total_proposals = 0
    template_evidence: Counter = Counter()
    proposal_types: Counter = Counter()
    failed_papers = []
    paper_results = []

    for paper in papers:
        if paper.get("error"):
            papers_failed += 1
            failed_papers.append(f"{paper['citation']}: {paper['error']}")
            continue

        if not paper["claims"]:
            papers_failed += 1
            failed_papers.append(f"{paper['citation']}: No claims found")
            continue

        try:
            result = process_paper(
                claims=paper["claims"],
                citation=paper["citation"],
                doi=paper.get("doi"),
                db_path=db_path,
                persist_proposals=persist_proposals,
            )

            papers_succeeded += 1
            total_claims += result.n_claims
            total_matched += result.n_matched
            total_unmatched += result.n_claims - result.n_matched
            total_proposals += len(result.proposals_generated)

            # Count template evidence from template_system_updates
            for update in result.template_system_updates:
                tid = update.get("template")
                if tid:
                    template_evidence[tid] += 1

            # Count proposal types
            for proposal in result.proposals_generated:
                if hasattr(proposal, "proposal_type"):
                    ptype = proposal.proposal_type.value if hasattr(proposal.proposal_type, "value") else str(proposal.proposal_type)
                elif isinstance(proposal, dict):
                    ptype = proposal.get("proposal_type", "unknown")
                else:
                    ptype = "unknown"
                proposal_types[ptype] += 1

            paper_results.append({
                "citation": paper["citation"],
                "n_claims": result.n_claims,
                "n_matched": result.n_matched,
                "n_proposals": len(result.proposals_generated),
                "aggregate_voi": result.aggregate_voi,
                "status": result.status,
            })

        except Exception as e:
            papers_failed += 1
            failed_papers.append(f"{paper['citation']}: {e}")

    processing_time = time.time() - start_time

    return BatchResult(
        papers_processed=len(papers),
        papers_succeeded=papers_succeeded,
        papers_failed=papers_failed,
        total_claims=total_claims,
        total_matched=total_matched,
        total_unmatched=total_unmatched,
        total_proposals=total_proposals,
        template_evidence_counts=dict(template_evidence),
        proposal_types=dict(proposal_types),
        failed_papers=failed_papers,
        paper_results=paper_results,
        processing_time_seconds=processing_time,
    )


def get_evidence_gap_map(batch_result: BatchResult) -> dict:
    """
    Generate evidence gap map from batch processing results.

    Returns dict with templates categorized by evidence strength.
    """
    from src.cmr.models import TemplateRecord, get_session, create_tables

    # Get all active templates
    create_tables("ae.db")
    session = get_session("ae.db")
    templates = session.query(TemplateRecord).filter(
        TemplateRecord.dedup_status == "active"
    ).all()
    session.close()

    all_template_ids = {t.display_id for t in templates}
    evidence_counts = batch_result.template_evidence_counts

    # Categorize by evidence strength
    strong_evidence = []    # 4+ studies
    moderate_evidence = []  # 2-3 studies
    weak_evidence = []      # 1 study
    no_evidence = []        # 0 studies

    for tid in all_template_ids:
        count = evidence_counts.get(tid, 0)
        if count >= 4:
            strong_evidence.append({"template_id": tid, "evidence_count": count})
        elif count >= 2:
            moderate_evidence.append({"template_id": tid, "evidence_count": count})
        elif count >= 1:
            weak_evidence.append({"template_id": tid, "evidence_count": count})
        else:
            no_evidence.append({"template_id": tid, "evidence_count": 0})

    # Sort by evidence count (descending)
    strong_evidence.sort(key=lambda x: x["evidence_count"], reverse=True)
    moderate_evidence.sort(key=lambda x: x["evidence_count"], reverse=True)
    weak_evidence.sort(key=lambda x: x["evidence_count"], reverse=True)
    no_evidence.sort(key=lambda x: x["template_id"])

    return {
        "strong_evidence": strong_evidence,
        "moderate_evidence": moderate_evidence,
        "weak_evidence": weak_evidence,
        "no_evidence": no_evidence,
        "summary": {
            "total_templates": len(all_template_ids),
            "with_strong": len(strong_evidence),
            "with_moderate": len(moderate_evidence),
            "with_weak": len(weak_evidence),
            "with_none": len(no_evidence),
        },
    }


def format_batch_report(result: BatchResult) -> str:
    """Format batch processing result for display."""
    lines = []
    lines.append("=" * 70)
    lines.append("BATCH PAPER PROCESSING REPORT")
    lines.append("=" * 70)
    lines.append(f"Processed: {result.processed_at.strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"Duration: {result.processing_time_seconds:.1f}s")
    lines.append("")

    lines.append("-" * 50)
    lines.append("PROCESSING SUMMARY")
    lines.append("-" * 50)
    lines.append(f"Papers processed: {result.papers_processed}")
    lines.append(f"  Succeeded: {result.papers_succeeded}")
    lines.append(f"  Failed: {result.papers_failed}")
    lines.append("")
    lines.append(f"Total claims: {result.total_claims}")
    lines.append(f"  Matched: {result.total_matched} ({100*result.total_matched/max(1,result.total_claims):.0f}%)")
    lines.append(f"  Unmatched: {result.total_unmatched}")
    lines.append("")
    lines.append(f"Update proposals generated: {result.total_proposals}")
    if result.proposal_types:
        for ptype, count in sorted(result.proposal_types.items()):
            lines.append(f"  {ptype}: {count}")
    lines.append("")

    lines.append("-" * 50)
    lines.append("TEMPLATES WITH MOST EVIDENCE")
    lines.append("-" * 50)
    sorted_templates = sorted(
        result.template_evidence_counts.items(),
        key=lambda x: x[1],
        reverse=True,
    )[:10]
    if sorted_templates:
        for tid, count in sorted_templates:
            lines.append(f"  {tid}: {count} claims")
    else:
        lines.append("  No template matches recorded")
    lines.append("")

    lines.append("-" * 50)
    lines.append("PAPER RESULTS")
    lines.append("-" * 50)
    for paper in result.paper_results:
        status_icon = "✓" if paper["status"] == "complete" else "✗"
        lines.append(
            f"  {status_icon} {paper['citation'][:40]:<40} "
            f"claims={paper['n_claims']}, matched={paper['n_matched']}, "
            f"VOI={paper['aggregate_voi']:.2f}"
        )
    lines.append("")

    if result.failed_papers:
        lines.append("-" * 50)
        lines.append("FAILED PAPERS")
        lines.append("-" * 50)
        for failure in result.failed_papers:
            lines.append(f"  ✗ {failure}")
        lines.append("")

    lines.append("=" * 70)
    return "\n".join(lines)


def format_evidence_gap_report(gap_map: dict) -> str:
    """Format evidence gap map for display."""
    lines = []
    lines.append("=" * 70)
    lines.append("EVIDENCE GAP MAP")
    lines.append("=" * 70)
    lines.append("")

    summary = gap_map["summary"]
    lines.append(f"Total templates: {summary['total_templates']}")
    lines.append(f"  Strong evidence (4+): {summary['with_strong']}")
    lines.append(f"  Moderate evidence (2-3): {summary['with_moderate']}")
    lines.append(f"  Weak evidence (1): {summary['with_weak']}")
    lines.append(f"  No evidence: {summary['with_none']}")
    lines.append("")

    if gap_map["strong_evidence"]:
        lines.append("-" * 50)
        lines.append("STRONG EVIDENCE (4+ studies)")
        lines.append("-" * 50)
        for item in gap_map["strong_evidence"]:
            lines.append(f"  {item['template_id']}: {item['evidence_count']} studies")
        lines.append("")

    if gap_map["moderate_evidence"]:
        lines.append("-" * 50)
        lines.append("MODERATE EVIDENCE (2-3 studies)")
        lines.append("-" * 50)
        for item in gap_map["moderate_evidence"]:
            lines.append(f"  {item['template_id']}: {item['evidence_count']} studies")
        lines.append("")

    if gap_map["no_evidence"]:
        lines.append("-" * 50)
        lines.append("NO EVIDENCE (Priority Research Targets)")
        lines.append("-" * 50)
        for item in gap_map["no_evidence"][:20]:  # Top 20
            lines.append(f"  {item['template_id']}")
        if len(gap_map["no_evidence"]) > 20:
            lines.append(f"  ... and {len(gap_map['no_evidence']) - 20} more")
        lines.append("")

    lines.append("=" * 70)
    return "\n".join(lines)


__all__ = [
    "BatchResult",
    "load_test_papers",
    "process_batch",
    "get_evidence_gap_map",
    "format_batch_report",
    "format_evidence_gap_report",
]
