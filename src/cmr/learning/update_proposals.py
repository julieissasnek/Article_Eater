"""
Template Update Proposal Generator (Sprint 13 Task 13.1).

When paper evaluation finds a contradiction or extension, generates a formal
proposal for updating the affected template. Proposals NEVER auto-apply;
they queue for human review.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
import hashlib
import json

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text

from src.cmr.models import Base, get_session


class ProposalType(str, Enum):
    """Types of template update proposals."""

    BOUNDARY_REVISION = "boundary_revision"  # Goldilocks boundary needs adjustment
    NEW_PARAMETER = "new_parameter"  # Missing parameter discovered
    INTERACTION_DISCOVERY = "interaction_discovery"  # New template interaction found
    MODERATOR_ADDITION = "moderator_addition"  # New moderator variable identified
    CONTRADICTION_FLAG = "contradiction_flag"  # Evidence contradicts current model


class ProposalStatus(str, Enum):
    """Status of a proposal in the review pipeline."""

    PROPOSED = "proposed"  # Awaiting review
    UNDER_REVIEW = "under_review"  # Being evaluated
    ACCEPTED = "accepted"  # Approved, will be applied
    REJECTED = "rejected"  # Declined with reason
    DEFERRED = "deferred"  # Postponed for more evidence


class UpdateProposalRecord(Base):
    """SQLAlchemy model for persisting update proposals."""

    __tablename__ = "cmr_update_proposals"

    id = Column(Integer, primary_key=True)
    proposal_id = Column(String(50), unique=True, nullable=False)
    proposal_type = Column(String(30), nullable=False)
    template_id = Column(String(20), nullable=False)
    parameter_name = Column(String(100), nullable=True)
    current_value = Column(Text, nullable=True)  # JSON-encoded
    proposed_value = Column(Text, nullable=True)  # JSON-encoded
    evidence_summary = Column(Text, nullable=True)  # JSON-encoded
    paper_citation = Column(String(500), nullable=True)
    effect_size = Column(Float, nullable=True)
    sample_n = Column(Integer, nullable=True)
    confidence = Column(Float, default=0.5)
    impact_assessment = Column(Text, nullable=True)
    requires_human_review = Column(Boolean, default=True)
    status = Column(String(20), default="proposed")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    reviewed_by = Column(String(100), nullable=True)
    review_notes = Column(Text, nullable=True)


@dataclass
class Evidence:
    """Evidence supporting a proposal."""

    paper_citation: str
    effect_size: Optional[float] = None
    sample_n: Optional[int] = None
    context: Optional[str] = None
    direction: Optional[str] = None  # "increase" / "decrease" / "none"
    p_value: Optional[float] = None
    study_design: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "paper_citation": self.paper_citation,
            "effect_size": self.effect_size,
            "sample_n": self.sample_n,
            "context": self.context,
            "direction": self.direction,
            "p_value": self.p_value,
            "study_design": self.study_design,
        }


@dataclass
class UpdateProposal:
    """Formal proposal for updating a template."""

    proposal_id: str
    proposal_type: ProposalType
    template_id: str
    parameter_name: Optional[str] = None
    current_value: Any = None
    proposed_value: Any = None
    evidence: list[Evidence] = field(default_factory=list)
    confidence: float = 0.5
    impact_assessment: str = ""
    requires_human_review: bool = True
    status: ProposalStatus = ProposalStatus.PROPOSED
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    review_notes: str = ""

    def to_dict(self) -> dict:
        return {
            "proposal_id": self.proposal_id,
            "proposal_type": self.proposal_type.value,
            "template_id": self.template_id,
            "parameter_name": self.parameter_name,
            "current_value": self.current_value,
            "proposed_value": self.proposed_value,
            "evidence": [e.to_dict() for e in self.evidence],
            "confidence": self.confidence,
            "impact_assessment": self.impact_assessment,
            "requires_human_review": self.requires_human_review,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "review_notes": self.review_notes,
        }


def _generate_proposal_id(
    template_id: str,
    proposal_type: ProposalType,
    parameter_name: Optional[str] = None,
) -> str:
    """Generate a unique proposal ID."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    content = f"{template_id}:{proposal_type.value}:{parameter_name or 'none'}:{timestamp}"
    hash_suffix = hashlib.md5(content.encode()).hexdigest()[:6]
    return f"UPD-{timestamp[:8]}-{hash_suffix.upper()}"


def _assess_impact(
    template_id: str,
    proposal_type: ProposalType,
    current_value: Any,
    proposed_value: Any,
) -> str:
    """Generate impact assessment for a proposal."""
    impacts = []

    if proposal_type == ProposalType.BOUNDARY_REVISION:
        if current_value is not None and proposed_value is not None:
            try:
                delta = abs(float(proposed_value) - float(current_value))
                pct = delta / abs(float(current_value)) * 100 if float(current_value) != 0 else 0
                impacts.append(f"Boundary shift: {pct:.1f}% change")
                if pct > 20:
                    impacts.append("SIGNIFICANT: May affect many existing evaluations")
                elif pct > 10:
                    impacts.append("MODERATE: Some evaluations may change scores")
                else:
                    impacts.append("MINOR: Limited impact on existing evaluations")
            except (TypeError, ValueError):
                impacts.append("Unable to quantify boundary change")

    elif proposal_type == ProposalType.CONTRADICTION_FLAG:
        impacts.append("CRITICAL: Evidence contradicts current template model")
        impacts.append("Requires expert review before any action")
        impacts.append("May indicate context-dependent effects")

    elif proposal_type == ProposalType.NEW_PARAMETER:
        impacts.append("EXTENSION: Adds new parameter to template")
        impacts.append("Existing evaluations will not retroactively change")
        impacts.append("Future evaluations may produce different scores")

    elif proposal_type == ProposalType.MODERATOR_ADDITION:
        impacts.append("MODERATOR: Adds context-dependent effect modifier")
        impacts.append("Will create subgroup-specific scoring")

    elif proposal_type == ProposalType.INTERACTION_DISCOVERY:
        impacts.append("INTERACTION: New template interaction discovered")
        impacts.append("May affect scoring when multiple templates active")

    return " | ".join(impacts)


def generate_proposal(
    template_id: str,
    proposal_type: ProposalType,
    evidence: list[Evidence],
    parameter_name: Optional[str] = None,
    current_value: Any = None,
    proposed_value: Any = None,
    confidence: float = 0.5,
    db_path: str = "ae.db",
    persist: bool = True,
) -> UpdateProposal:
    """
    Generate a formal update proposal.

    Args:
        template_id: ID of the template to update
        proposal_type: Type of proposed change
        evidence: List of Evidence objects supporting the proposal
        parameter_name: Specific parameter affected (if applicable)
        current_value: Current value in the template
        proposed_value: Proposed new value
        confidence: Confidence in the proposal (0-1)
        db_path: Path to database
        persist: Whether to save to database

    Returns:
        UpdateProposal object
    """
    proposal_id = _generate_proposal_id(template_id, proposal_type, parameter_name)
    impact_assessment = _assess_impact(template_id, proposal_type, current_value, proposed_value)

    proposal = UpdateProposal(
        proposal_id=proposal_id,
        proposal_type=proposal_type,
        template_id=template_id,
        parameter_name=parameter_name,
        current_value=current_value,
        proposed_value=proposed_value,
        evidence=evidence,
        confidence=confidence,
        impact_assessment=impact_assessment,
        requires_human_review=True,
        status=ProposalStatus.PROPOSED,
    )

    if persist:
        _persist_proposal(proposal, db_path)

    return proposal


def generate_contradiction_proposal(
    template_id: str,
    parameter_name: str,
    current_value: Any,
    observed_value: Any,
    evidence: Evidence,
    db_path: str = "ae.db",
) -> UpdateProposal:
    """
    Generate a proposal when evidence contradicts current template.

    Args:
        template_id: Template with contradicted prediction
        parameter_name: Parameter that's contradicted
        current_value: What the template says
        observed_value: What the evidence shows
        evidence: Evidence object with study details
        db_path: Database path

    Returns:
        UpdateProposal with contradiction_flag type
    """
    # Calculate confidence based on evidence strength
    confidence = 0.5
    if evidence.sample_n:
        if evidence.sample_n >= 100:
            confidence += 0.2
        elif evidence.sample_n >= 50:
            confidence += 0.1
    if evidence.effect_size:
        if abs(evidence.effect_size) >= 0.5:
            confidence += 0.15
        elif abs(evidence.effect_size) >= 0.3:
            confidence += 0.1
    confidence = min(0.9, confidence)  # Cap at 0.9

    return generate_proposal(
        template_id=template_id,
        proposal_type=ProposalType.CONTRADICTION_FLAG,
        evidence=[evidence],
        parameter_name=parameter_name,
        current_value=current_value,
        proposed_value=observed_value,
        confidence=confidence,
        db_path=db_path,
    )


def generate_boundary_revision_proposal(
    template_id: str,
    parameter_name: str,
    current_boundary: float,
    proposed_boundary: float,
    evidence: list[Evidence],
    db_path: str = "ae.db",
) -> UpdateProposal:
    """
    Generate a proposal for revising a Goldilocks boundary.

    Args:
        template_id: Template with boundary to revise
        parameter_name: Name of the boundary parameter
        current_boundary: Current boundary value
        proposed_boundary: Proposed new boundary value
        evidence: List of Evidence objects supporting the revision
        db_path: Database path

    Returns:
        UpdateProposal with boundary_revision type
    """
    # Calculate confidence based on evidence quantity and quality
    confidence = 0.4  # Base confidence
    n_studies = len(evidence)
    if n_studies >= 3:
        confidence += 0.2
    elif n_studies >= 2:
        confidence += 0.1

    total_n = sum(e.sample_n or 0 for e in evidence)
    if total_n >= 200:
        confidence += 0.15
    elif total_n >= 100:
        confidence += 0.1

    avg_effect = sum(abs(e.effect_size or 0) for e in evidence) / max(1, n_studies)
    if avg_effect >= 0.4:
        confidence += 0.1

    confidence = min(0.85, confidence)

    return generate_proposal(
        template_id=template_id,
        proposal_type=ProposalType.BOUNDARY_REVISION,
        evidence=evidence,
        parameter_name=parameter_name,
        current_value=current_boundary,
        proposed_value=proposed_boundary,
        confidence=confidence,
        db_path=db_path,
    )


def generate_moderator_proposal(
    template_id: str,
    moderator_name: str,
    moderator_values: dict[str, float],
    evidence: list[Evidence],
    db_path: str = "ae.db",
) -> UpdateProposal:
    """
    Generate a proposal for adding a moderator variable.

    Args:
        template_id: Template to add moderator to
        moderator_name: Name of the moderator (e.g., "age_group", "cultural_context")
        moderator_values: Dict mapping moderator levels to effect multipliers
        evidence: List of Evidence objects demonstrating moderation
        db_path: Database path

    Returns:
        UpdateProposal with moderator_addition type
    """
    confidence = 0.5
    if len(evidence) >= 2:
        confidence += 0.15
    if any(e.sample_n and e.sample_n >= 50 for e in evidence):
        confidence += 0.1

    return generate_proposal(
        template_id=template_id,
        proposal_type=ProposalType.MODERATOR_ADDITION,
        evidence=evidence,
        parameter_name=moderator_name,
        current_value=None,
        proposed_value=moderator_values,
        confidence=confidence,
        db_path=db_path,
    )


def _persist_proposal(proposal: UpdateProposal, db_path: str) -> None:
    """Save proposal to database."""
    session = get_session(db_path)
    Base.metadata.create_all(session.get_bind())

    record = UpdateProposalRecord(
        proposal_id=proposal.proposal_id,
        proposal_type=proposal.proposal_type.value,
        template_id=proposal.template_id,
        parameter_name=proposal.parameter_name,
        current_value=json.dumps(proposal.current_value) if proposal.current_value is not None else None,
        proposed_value=json.dumps(proposal.proposed_value) if proposal.proposed_value is not None else None,
        evidence_summary=json.dumps([e.to_dict() for e in proposal.evidence]),
        paper_citation=proposal.evidence[0].paper_citation if proposal.evidence else None,
        effect_size=proposal.evidence[0].effect_size if proposal.evidence else None,
        sample_n=proposal.evidence[0].sample_n if proposal.evidence else None,
        confidence=proposal.confidence,
        impact_assessment=proposal.impact_assessment,
        requires_human_review=proposal.requires_human_review,
        status=proposal.status.value,
        created_at=proposal.created_at,
    )

    session.add(record)
    session.commit()


def get_pending_proposals(
    db_path: str = "ae.db",
    template_id: Optional[str] = None,
    proposal_type: Optional[ProposalType] = None,
) -> list[UpdateProposal]:
    """
    Retrieve pending proposals from database.

    Args:
        db_path: Database path
        template_id: Filter by template (optional)
        proposal_type: Filter by type (optional)

    Returns:
        List of UpdateProposal objects with status=proposed
    """
    session = get_session(db_path)
    Base.metadata.create_all(session.get_bind())

    query = session.query(UpdateProposalRecord).filter(
        UpdateProposalRecord.status == ProposalStatus.PROPOSED.value
    )

    if template_id:
        query = query.filter(UpdateProposalRecord.template_id == template_id)
    if proposal_type:
        query = query.filter(UpdateProposalRecord.proposal_type == proposal_type.value)

    proposals = []
    for record in query.all():
        evidence_data = json.loads(record.evidence_summary) if record.evidence_summary else []
        evidence = [
            Evidence(
                paper_citation=e.get("paper_citation", ""),
                effect_size=e.get("effect_size"),
                sample_n=e.get("sample_n"),
                context=e.get("context"),
                direction=e.get("direction"),
            )
            for e in evidence_data
        ]

        proposals.append(
            UpdateProposal(
                proposal_id=record.proposal_id,
                proposal_type=ProposalType(record.proposal_type),
                template_id=record.template_id,
                parameter_name=record.parameter_name,
                current_value=json.loads(record.current_value) if record.current_value else None,
                proposed_value=json.loads(record.proposed_value) if record.proposed_value else None,
                evidence=evidence,
                confidence=record.confidence,
                impact_assessment=record.impact_assessment or "",
                requires_human_review=record.requires_human_review,
                status=ProposalStatus(record.status),
                created_at=record.created_at,
            )
        )

    return proposals


def update_proposal_status(
    proposal_id: str,
    new_status: ProposalStatus,
    reviewed_by: str,
    review_notes: str = "",
    db_path: str = "ae.db",
) -> bool:
    """
    Update the status of a proposal.

    Args:
        proposal_id: ID of proposal to update
        new_status: New status to set
        reviewed_by: Reviewer identifier
        review_notes: Optional notes explaining the decision
        db_path: Database path

    Returns:
        True if updated, False if not found
    """
    session = get_session(db_path)
    Base.metadata.create_all(session.get_bind())

    record = session.query(UpdateProposalRecord).filter(
        UpdateProposalRecord.proposal_id == proposal_id
    ).first()

    if not record:
        return False

    record.status = new_status.value
    record.reviewed_by = reviewed_by
    record.review_notes = review_notes
    record.updated_at = datetime.now(timezone.utc)
    session.commit()
    return True


def format_proposal_summary(proposal: UpdateProposal) -> str:
    """Format a proposal for display."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"PROPOSAL: {proposal.proposal_id}")
    lines.append("=" * 60)
    lines.append(f"Type: {proposal.proposal_type.value}")
    lines.append(f"Template: {proposal.template_id}")
    lines.append(f"Status: {proposal.status.value}")
    lines.append(f"Confidence: {proposal.confidence:.2f}")
    lines.append("")

    if proposal.parameter_name:
        lines.append(f"Parameter: {proposal.parameter_name}")
        lines.append(f"Current Value: {proposal.current_value}")
        lines.append(f"Proposed Value: {proposal.proposed_value}")
        lines.append("")

    lines.append("IMPACT ASSESSMENT:")
    lines.append(f"  {proposal.impact_assessment}")
    lines.append("")

    lines.append("EVIDENCE:")
    for i, e in enumerate(proposal.evidence, 1):
        lines.append(f"  [{i}] {e.paper_citation}")
        if e.effect_size:
            lines.append(f"      Effect size: d={e.effect_size:.2f}")
        if e.sample_n:
            lines.append(f"      Sample size: N={e.sample_n}")
        if e.context:
            lines.append(f"      Context: {e.context}")

    lines.append("")
    lines.append(f"Created: {proposal.created_at.strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"Requires Human Review: {proposal.requires_human_review}")

    return "\n".join(lines)


# ==============================================================================
# Proposal Review Queue (Sprint 13 Task 13.2)
# ==============================================================================

def get_proposal_by_id(
    proposal_id: str,
    db_path: str = "ae.db",
) -> Optional[UpdateProposal]:
    """
    Retrieve a specific proposal by ID.

    Args:
        proposal_id: The proposal ID to look up
        db_path: Database path

    Returns:
        UpdateProposal or None if not found
    """
    session = get_session(db_path)
    Base.metadata.create_all(session.get_bind())

    record = session.query(UpdateProposalRecord).filter(
        UpdateProposalRecord.proposal_id == proposal_id
    ).first()

    if not record:
        return None

    evidence_data = json.loads(record.evidence_summary) if record.evidence_summary else []
    evidence = [
        Evidence(
            paper_citation=e.get("paper_citation", ""),
            effect_size=e.get("effect_size"),
            sample_n=e.get("sample_n"),
            context=e.get("context"),
            direction=e.get("direction"),
        )
        for e in evidence_data
    ]

    return UpdateProposal(
        proposal_id=record.proposal_id,
        proposal_type=ProposalType(record.proposal_type),
        template_id=record.template_id,
        parameter_name=record.parameter_name,
        current_value=json.loads(record.current_value) if record.current_value else None,
        proposed_value=json.loads(record.proposed_value) if record.proposed_value else None,
        evidence=evidence,
        confidence=record.confidence,
        impact_assessment=record.impact_assessment or "",
        requires_human_review=record.requires_human_review,
        status=ProposalStatus(record.status),
        created_at=record.created_at,
        review_notes=record.review_notes or "",
    )


def list_all_proposals(
    db_path: str = "ae.db",
    status_filter: Optional[ProposalStatus] = None,
    template_filter: Optional[str] = None,
) -> list[UpdateProposal]:
    """
    List all proposals, optionally filtered by status or template.

    Args:
        db_path: Database path
        status_filter: Filter by status (optional)
        template_filter: Filter by template ID (optional)

    Returns:
        List of UpdateProposal objects
    """
    session = get_session(db_path)
    Base.metadata.create_all(session.get_bind())

    query = session.query(UpdateProposalRecord).order_by(
        UpdateProposalRecord.created_at.desc()
    )

    if status_filter:
        query = query.filter(UpdateProposalRecord.status == status_filter.value)
    if template_filter:
        query = query.filter(UpdateProposalRecord.template_id == template_filter)

    proposals = []
    for record in query.all():
        evidence_data = json.loads(record.evidence_summary) if record.evidence_summary else []
        evidence = [
            Evidence(
                paper_citation=e.get("paper_citation", ""),
                effect_size=e.get("effect_size"),
                sample_n=e.get("sample_n"),
                context=e.get("context"),
                direction=e.get("direction"),
            )
            for e in evidence_data
        ]

        proposals.append(
            UpdateProposal(
                proposal_id=record.proposal_id,
                proposal_type=ProposalType(record.proposal_type),
                template_id=record.template_id,
                parameter_name=record.parameter_name,
                current_value=json.loads(record.current_value) if record.current_value else None,
                proposed_value=json.loads(record.proposed_value) if record.proposed_value else None,
                evidence=evidence,
                confidence=record.confidence,
                impact_assessment=record.impact_assessment or "",
                requires_human_review=record.requires_human_review,
                status=ProposalStatus(record.status),
                created_at=record.created_at,
                review_notes=record.review_notes or "",
            )
        )

    return proposals


def _apply_proposal_to_template(
    proposal: UpdateProposal,
    templates_dir: str = "data/templates",
) -> tuple[bool, str]:
    """
    Apply an accepted proposal to its template JSON file.

    Args:
        proposal: The accepted proposal to apply
        templates_dir: Directory containing template JSON files

    Returns:
        (success, message) tuple
    """
    from pathlib import Path

    # Find the template JSON file
    template_dir = Path(templates_dir)
    if not template_dir.exists():
        return False, f"Templates directory not found: {templates_dir}"

    # Search for template file
    template_file = None
    for json_file in template_dir.glob("**/*.json"):
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            if data.get("template_id") == proposal.template_id or \
               data.get("display_id") == proposal.template_id:
                template_file = json_file
                break
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Skipped: {e}")
            continue

    if not template_file:
        return False, f"Template file not found for {proposal.template_id}"

    # Load current template
    try:
        template_data = json.loads(template_file.read_text(encoding="utf-8"))
    except Exception as e:
        return False, f"Failed to read template: {e}"

    # Apply the change based on proposal type
    changed = False

    if proposal.proposal_type == ProposalType.BOUNDARY_REVISION:
        if proposal.parameter_name and proposal.proposed_value is not None:
            # Look for the parameter in goldilocks_zone or parameters
            if "goldilocks_zone" in template_data:
                if proposal.parameter_name in template_data["goldilocks_zone"]:
                    template_data["goldilocks_zone"][proposal.parameter_name] = proposal.proposed_value
                    changed = True
            if "parameters" in template_data:
                if proposal.parameter_name in template_data["parameters"]:
                    template_data["parameters"][proposal.parameter_name] = proposal.proposed_value
                    changed = True
            # Also check top-level
            if proposal.parameter_name in template_data:
                template_data[proposal.parameter_name] = proposal.proposed_value
                changed = True

    elif proposal.proposal_type == ProposalType.NEW_PARAMETER:
        if proposal.parameter_name and proposal.proposed_value is not None:
            if "parameters" not in template_data:
                template_data["parameters"] = {}
            template_data["parameters"][proposal.parameter_name] = proposal.proposed_value
            changed = True

    elif proposal.proposal_type == ProposalType.MODERATOR_ADDITION:
        if proposal.parameter_name and proposal.proposed_value is not None:
            if "moderators" not in template_data:
                template_data["moderators"] = {}
            template_data["moderators"][proposal.parameter_name] = proposal.proposed_value
            changed = True

    elif proposal.proposal_type == ProposalType.CONTRADICTION_FLAG:
        # For contradictions, add a note but don't auto-change values
        if "review_notes" not in template_data:
            template_data["review_notes"] = []
        template_data["review_notes"].append({
            "date": datetime.now(timezone.utc).isoformat(),
            "proposal_id": proposal.proposal_id,
            "note": f"Contradiction flagged for {proposal.parameter_name}: "
                    f"current={proposal.current_value}, observed={proposal.proposed_value}",
        })
        changed = True

    if not changed:
        return False, "No changes could be applied"

    # Add update history
    if "update_history" not in template_data:
        template_data["update_history"] = []
    template_data["update_history"].append({
        "date": datetime.now(timezone.utc).isoformat(),
        "proposal_id": proposal.proposal_id,
        "type": proposal.proposal_type.value,
        "parameter": proposal.parameter_name,
        "old_value": proposal.current_value,
        "new_value": proposal.proposed_value,
    })

    # Write back
    try:
        template_file.write_text(json.dumps(template_data, indent=2), encoding="utf-8")
    except Exception as e:
        return False, f"Failed to write template: {e}"

    return True, f"Applied to {template_file}"


def accept_proposal(
    proposal_id: str,
    reviewed_by: str,
    notes: str = "",
    db_path: str = "ae.db",
    templates_dir: str = "data/templates",
    apply_changes: bool = True,
) -> tuple[bool, str]:
    """
    Accept a proposal and optionally apply changes to template.

    Args:
        proposal_id: ID of proposal to accept
        reviewed_by: Identifier of reviewer
        notes: Optional review notes
        db_path: Database path
        templates_dir: Directory containing template JSONs
        apply_changes: Whether to apply changes to template file

    Returns:
        (success, message) tuple
    """
    proposal = get_proposal_by_id(proposal_id, db_path)
    if not proposal:
        return False, f"Proposal not found: {proposal_id}"

    if proposal.status != ProposalStatus.PROPOSED:
        return False, f"Proposal is not pending (status: {proposal.status.value})"

    # Apply changes if requested
    apply_msg = ""
    if apply_changes:
        success, apply_msg = _apply_proposal_to_template(proposal, templates_dir)
        if not success:
            # Still accept but note the failure
            apply_msg = f" (WARNING: {apply_msg})"

    # Update status
    updated = update_proposal_status(
        proposal_id=proposal_id,
        new_status=ProposalStatus.ACCEPTED,
        reviewed_by=reviewed_by,
        review_notes=notes,
        db_path=db_path,
    )

    if updated:
        return True, f"Proposal {proposal_id} accepted{apply_msg}"
    else:
        return False, "Failed to update proposal status"


def reject_proposal(
    proposal_id: str,
    reviewed_by: str,
    notes: str = "",
    db_path: str = "ae.db",
) -> tuple[bool, str]:
    """
    Reject a proposal.

    Args:
        proposal_id: ID of proposal to reject
        reviewed_by: Identifier of reviewer
        notes: Required rejection reason

    Returns:
        (success, message) tuple
    """
    proposal = get_proposal_by_id(proposal_id, db_path)
    if not proposal:
        return False, f"Proposal not found: {proposal_id}"

    if proposal.status != ProposalStatus.PROPOSED:
        return False, f"Proposal is not pending (status: {proposal.status.value})"

    if not notes:
        return False, "Rejection requires notes explaining the reason"

    updated = update_proposal_status(
        proposal_id=proposal_id,
        new_status=ProposalStatus.REJECTED,
        reviewed_by=reviewed_by,
        review_notes=notes,
        db_path=db_path,
    )

    if updated:
        return True, f"Proposal {proposal_id} rejected"
    else:
        return False, "Failed to update proposal status"


def format_proposal_list(proposals: list[UpdateProposal]) -> str:
    """Format a list of proposals for display."""
    if not proposals:
        return "No proposals found."

    lines = []
    lines.append(f"{'ID':<25} {'Type':<20} {'Template':<10} {'Status':<12} {'Confidence'}")
    lines.append("-" * 80)

    for p in proposals:
        lines.append(
            f"{p.proposal_id:<25} {p.proposal_type.value:<20} {p.template_id:<10} "
            f"{p.status.value:<12} {p.confidence:.2f}"
        )

    lines.append("-" * 80)
    lines.append(f"Total: {len(proposals)} proposals")
    return "\n".join(lines)
