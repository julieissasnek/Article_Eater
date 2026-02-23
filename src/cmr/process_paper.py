"""
Paper Processing Pipeline (Sprint 13 Task 13.13).

Main entry point for processing scientific papers through CMR.
Wires together: paper evaluation → update proposal generation →
evidence accumulation → paper record keeping.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from src.cmr.paper_eval import evaluate_paper
from src.cmr.paper_history import get_processed_papers
from src.cmr.learning.update_proposals import (
    Evidence,
    ProposalType,
    UpdateProposal,
    generate_proposal,
    generate_contradiction_proposal,
    get_pending_proposals,
    format_proposal_summary,
)
from src.cmr.learning.evidence_accumulation import (
    EvidencePool,
    AccumulatedEvidence,
    accumulate_evidence,
    generate_proposals_from_accumulated,
    format_accumulation_report,
)


@dataclass
class ProcessingResult:
    """Result of processing a paper through the full pipeline."""

    paper_citation: str
    doi: Optional[str]
    processed_at: datetime
    n_claims: int
    n_matched: int
    n_unmatched: int
    n_contradictions: int
    n_confirmations: int
    n_gaps: int
    aggregate_voi: float
    proposals_generated: list[UpdateProposal]
    evidence_accumulated: list[AccumulatedEvidence]
    template_system_updates: list[dict]
    recommendations: list[str]
    status: str = "complete"
    raw_evaluation: Optional[dict] = None

    def to_dict(self) -> dict:
        return {
            "paper_citation": self.paper_citation,
            "doi": self.doi,
            "processed_at": self.processed_at.isoformat(),
            "n_claims": self.n_claims,
            "n_matched": self.n_matched,
            "n_unmatched": self.n_unmatched,
            "n_contradictions": self.n_contradictions,
            "n_confirmations": self.n_confirmations,
            "n_gaps": self.n_gaps,
            "aggregate_voi": self.aggregate_voi,
            "proposals_generated": [p.to_dict() for p in self.proposals_generated],
            "evidence_accumulated": [e.to_dict() for e in self.evidence_accumulated],
            "template_system_updates": self.template_system_updates,
            "recommendations": self.recommendations,
            "status": self.status,
        }


def _convert_update_to_proposal(
    update: dict,
    citation: str,
    effect_size: Optional[float] = None,
    sample_n: Optional[int] = None,
    db_path: str = "ae.db",
    persist: bool = True,
) -> Optional[UpdateProposal]:
    """
    Convert a template_system_update dict to a formal UpdateProposal.

    Args:
        update: Dict with keys type, template, detail
        citation: Paper citation string
        effect_size: Effect size from the paper (if available)
        sample_n: Sample size from the paper (if available)
        db_path: Database path
        persist: Whether to persist to database

    Returns:
        UpdateProposal or None if update type doesn't warrant a proposal
    """
    update_type = update.get("type", "")
    template_id = update.get("template", "")
    detail = update.get("detail", "")

    if update_type == "confirms":
        # Confirmations don't generate proposals - they just strengthen existing templates
        return None

    evidence = Evidence(
        paper_citation=citation,
        effect_size=effect_size,
        sample_n=sample_n,
        context=detail,
    )

    if update_type == "contradicts":
        proposal_type = ProposalType.CONTRADICTION_FLAG
    elif update_type == "extends":
        proposal_type = ProposalType.BOUNDARY_REVISION
    elif update_type == "gap":
        proposal_type = ProposalType.NEW_PARAMETER
    else:
        return None

    return generate_proposal(
        template_id=template_id if template_id != "none" else "SYSTEM",
        proposal_type=proposal_type,
        evidence=[evidence],
        parameter_name=None,
        current_value=None,
        proposed_value=None,
        confidence=0.5,
        db_path=db_path,
        persist=persist,
    )


def _extract_effect_data_from_claims(claims: list[dict]) -> list[dict]:
    """
    Extract structured effect data from claims for evidence accumulation.

    Args:
        claims: List of claim dicts from paper evaluation

    Returns:
        List of dicts with paper_citation, effect_size, sample_n, template_id, parameter_name
    """
    effect_data = []
    for claim in claims:
        effect_size = claim.get("effect_size")
        sample_n = claim.get("sample_n") or claim.get("n")

        if effect_size is not None and sample_n is not None:
            try:
                effect_data.append({
                    "paper_citation": claim.get("source", "Unknown"),
                    "effect_size": float(effect_size),
                    "sample_n": int(sample_n),
                    "template_id": claim.get("template_id"),
                    "parameter_name": claim.get("parameter_name") or claim.get("dv"),
                    "context": claim.get("context") or claim.get("description"),
                    "direction": claim.get("direction"),
                })
            except (ValueError, TypeError):
                continue

    return effect_data


def _accumulate_evidence_by_template(
    effect_data: list[dict],
    template_values: dict[str, dict],
    db_path: str = "ae.db",
) -> tuple[list[AccumulatedEvidence], list[UpdateProposal]]:
    """
    Group effect data by template/parameter and run accumulation.

    Args:
        effect_data: List of effect dicts from claims
        template_values: Dict mapping template_id to current parameter values
        db_path: Database path

    Returns:
        (list of AccumulatedEvidence, list of generated proposals)
    """
    accumulated_results = []
    all_proposals = []

    # Group by (template_id, parameter_name)
    groups: dict[tuple[str, str], list[dict]] = {}
    for item in effect_data:
        template_id = item.get("template_id")
        parameter_name = item.get("parameter_name")
        if template_id and parameter_name:
            key = (template_id, parameter_name)
            if key not in groups:
                groups[key] = []
            groups[key].append(item)

    for (template_id, parameter_name), items in groups.items():
        pool = EvidencePool(template_id=template_id, parameter_name=parameter_name)
        for item in items:
            pool.add_estimate(
                paper_citation=item["paper_citation"],
                effect_size=item["effect_size"],
                sample_n=item["sample_n"],
                context=item.get("context"),
                direction=item.get("direction"),
            )

        # Get current value from template if available
        current_value = 0.0
        if template_id in template_values:
            params = template_values[template_id]
            if parameter_name in params:
                current_value = float(params.get(parameter_name, 0.0))

        accumulated = accumulate_evidence(pool, current_value)
        accumulated_results.append(accumulated)

        # Generate proposals if needed
        proposals = generate_proposals_from_accumulated(accumulated, db_path)
        all_proposals.extend(proposals)

    return accumulated_results, all_proposals


def process_paper(
    claims: list[dict],
    citation: str,
    doi: Optional[str] = None,
    db_path: str = "ae.db",
    persist_proposals: bool = True,
    include_raw_evaluation: bool = False,
    template_values: Optional[dict[str, dict]] = None,
) -> ProcessingResult:
    """
    Process a paper through the full CMR pipeline.

    This is the MAIN ENTRY POINT for paper processing. It:
    1. Evaluates the paper claims against templates
    2. Generates formal update proposals from findings
    3. Accumulates evidence for meta-analysis (if effect data present)
    4. Records the paper in history

    Args:
        claims: List of structured claim dicts with keys like:
            - description: Text description of the claim
            - iv: Independent variable
            - dv: Dependent variable
            - direction: Effect direction (increase/decrease)
            - effect_size: Cohen's d or similar (optional)
            - sample_n: Sample size (optional)
        citation: Paper citation string (e.g., "Ulrich 1984")
        doi: DOI if available
        db_path: Path to SQLite database
        persist_proposals: Whether to save proposals to database
        include_raw_evaluation: Whether to include raw evaluation in result
        template_values: Optional dict mapping template_id to current parameter values
            (used for evidence accumulation comparison)

    Returns:
        ProcessingResult with summary and generated proposals
    """
    template_values = template_values or {}

    # Step 1: Run paper evaluation
    evaluation = evaluate_paper(
        paper_text="",
        structured_claims=claims,
        citation=citation,
        doi=doi,
        db_path=db_path,
    )

    # Extract key metrics
    n_claims = evaluation.get("n_claims_extracted", 0)
    n_matched = evaluation.get("n_claims_matched", 0)
    n_unmatched = evaluation.get("n_claims_unmatched", 0)
    template_system_updates = evaluation.get("template_system_updates", [])
    report = evaluation.get("report", {})
    summary = report.get("summary", {})
    recommendations = report.get("recommendations", [])
    prioritized = evaluation.get("prioritized_findings", [])

    n_contradictions = summary.get("contradictions", 0)
    n_confirmations = summary.get("confirmations", 0)
    n_gaps = summary.get("gaps", 0)
    aggregate_voi = float(summary.get("aggregate_voi", 0.0))

    # Step 2: Convert template_system_updates to formal proposals
    proposals_generated = []
    for update in template_system_updates:
        proposal = _convert_update_to_proposal(
            update=update,
            citation=citation,
            db_path=db_path,
            persist=persist_proposals,
        )
        if proposal is not None:
            proposals_generated.append(proposal)

    # Step 3: Extract effect data and accumulate evidence
    extracted_claims = evaluation.get("claims", [])
    effect_data = _extract_effect_data_from_claims(extracted_claims)
    evidence_accumulated, accumulation_proposals = _accumulate_evidence_by_template(
        effect_data=effect_data,
        template_values=template_values,
        db_path=db_path,
    )
    proposals_generated.extend(accumulation_proposals)

    result = ProcessingResult(
        paper_citation=citation,
        doi=doi,
        processed_at=datetime.now(timezone.utc),
        n_claims=n_claims,
        n_matched=n_matched,
        n_unmatched=n_unmatched,
        n_contradictions=n_contradictions,
        n_confirmations=n_confirmations,
        n_gaps=n_gaps,
        aggregate_voi=aggregate_voi,
        proposals_generated=proposals_generated,
        evidence_accumulated=evidence_accumulated,
        template_system_updates=template_system_updates,
        recommendations=recommendations,
        status="complete",
        raw_evaluation=evaluation if include_raw_evaluation else None,
    )

    return result


def process_paper_from_text(
    paper_text: str,
    citation: str,
    doi: Optional[str] = None,
    db_path: str = "ae.db",
    persist_proposals: bool = True,
) -> ProcessingResult:
    """
    Process a paper from raw text (uses regex-based claim extraction).

    Args:
        paper_text: Full paper text or abstract
        citation: Paper citation string
        doi: DOI if available
        db_path: Path to database
        persist_proposals: Whether to save proposals to database

    Returns:
        ProcessingResult
    """
    # Let evaluate_paper handle claim extraction
    evaluation = evaluate_paper(
        paper_text=paper_text,
        structured_claims=None,
        citation=citation,
        doi=doi,
        db_path=db_path,
    )

    # Get extracted claims for re-processing
    claims = evaluation.get("claims", [])

    # Re-run through main pipeline with extracted claims
    return process_paper(
        claims=claims,
        citation=citation,
        doi=doi,
        db_path=db_path,
        persist_proposals=persist_proposals,
    )


def format_processing_report(result: ProcessingResult) -> str:
    """Format a ProcessingResult as a readable report."""
    lines = []
    lines.append("=" * 70)
    lines.append("PAPER PROCESSING REPORT")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"Citation: {result.paper_citation}")
    if result.doi:
        lines.append(f"DOI: {result.doi}")
    lines.append(f"Processed: {result.processed_at.strftime('%Y-%m-%d %H:%M')}")
    lines.append("")

    lines.append("-" * 50)
    lines.append("CLAIM SUMMARY")
    lines.append("-" * 50)
    lines.append(f"Total claims extracted: {result.n_claims}")
    lines.append(f"Claims matched to templates: {result.n_matched}")
    lines.append(f"Unmatched claims: {result.n_unmatched}")
    lines.append("")
    lines.append(f"Confirmations: {result.n_confirmations}")
    lines.append(f"Contradictions: {result.n_contradictions}")
    lines.append(f"Gaps identified: {result.n_gaps}")
    lines.append("")
    lines.append(f"Aggregate VOI: {result.aggregate_voi:.2f}")
    lines.append("")

    if result.proposals_generated:
        lines.append("-" * 50)
        lines.append(f"UPDATE PROPOSALS GENERATED ({len(result.proposals_generated)})")
        lines.append("-" * 50)
        for i, proposal in enumerate(result.proposals_generated, 1):
            lines.append(f"\n[{i}] {proposal.proposal_id}")
            lines.append(f"    Type: {proposal.proposal_type.value}")
            lines.append(f"    Template: {proposal.template_id}")
            lines.append(f"    Confidence: {proposal.confidence:.2f}")
            if proposal.parameter_name:
                lines.append(f"    Parameter: {proposal.parameter_name}")
            lines.append(f"    Status: {proposal.status.value}")
        lines.append("")
    else:
        lines.append("-" * 50)
        lines.append("No update proposals generated (paper confirms existing templates)")
        lines.append("-" * 50)
        lines.append("")

    if result.evidence_accumulated:
        lines.append("-" * 50)
        lines.append(f"EVIDENCE ACCUMULATION ({len(result.evidence_accumulated)} parameters)")
        lines.append("-" * 50)
        for acc in result.evidence_accumulated:
            lines.append(f"\n{acc.template_id}.{acc.parameter_name}:")
            lines.append(f"  Studies: {acc.n_studies}, Total N: {acc.total_n}")
            lines.append(f"  Weighted Mean: {acc.weighted_mean:.3f}")
            lines.append(f"  95% CI: [{acc.ci_lower:.3f}, {acc.ci_upper:.3f}]")
            if acc.needs_update:
                lines.append("  ** UPDATE RECOMMENDED **")
            if acc.contradiction_detected:
                lines.append("  ** CONTRADICTION DETECTED **")
        lines.append("")

    if result.recommendations:
        lines.append("-" * 50)
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 50)
        for i, rec in enumerate(result.recommendations, 1):
            lines.append(f"{i}. {rec}")
        lines.append("")

    lines.append("=" * 70)
    return "\n".join(lines)


def get_processing_summary(db_path: str = "ae.db", limit: int = 10) -> dict:
    """
    Get summary of recently processed papers.

    Args:
        db_path: Database path
        limit: Maximum number of papers to include

    Returns:
        Dict with processing statistics and recent papers
    """
    papers = get_processed_papers(db_path=db_path, limit=limit)
    pending = get_pending_proposals(db_path=db_path)

    return {
        "total_papers_processed": len(get_processed_papers(db_path=db_path)),
        "recent_papers": [
            {
                "citation": p.citation,
                "evaluated_at": p.evaluated_at.isoformat() if p.evaluated_at else None,
                "n_claims": p.n_claims,
                "aggregate_voi": p.aggregate_voi,
            }
            for p in papers
        ],
        "pending_proposals": len(pending),
        "proposals_by_type": _count_proposals_by_type(pending),
    }


def _count_proposals_by_type(proposals: list[UpdateProposal]) -> dict[str, int]:
    """Count proposals by type."""
    counts: dict[str, int] = {}
    for p in proposals:
        ptype = p.proposal_type.value
        counts[ptype] = counts.get(ptype, 0) + 1
    return counts


__all__ = [
    "ProcessingResult",
    "process_paper",
    "process_paper_from_text",
    "format_processing_report",
    "get_processing_summary",
]
