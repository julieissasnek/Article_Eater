"""
CMR Learning Module (Sprint 13).

Components for template update proposal generation, evidence accumulation,
and Bayesian parameter updating.
"""

from src.cmr.learning.update_proposals import (
    UpdateProposal,
    Evidence,
    ProposalType,
    ProposalStatus,
    generate_proposal,
    generate_contradiction_proposal,
    generate_boundary_revision_proposal,
    generate_moderator_proposal,
    get_pending_proposals,
    format_proposal_summary,
)

from src.cmr.learning.evidence_accumulation import (
    EffectEstimate,
    EvidencePool,
    AccumulatedEvidence,
    accumulate_evidence,
    accumulate_and_propose,
    generate_proposals_from_accumulated,
    format_accumulation_report,
)

__all__ = [
    # Update proposals
    "UpdateProposal",
    "Evidence",
    "ProposalType",
    "ProposalStatus",
    "generate_proposal",
    "generate_contradiction_proposal",
    "generate_boundary_revision_proposal",
    "generate_moderator_proposal",
    "get_pending_proposals",
    "format_proposal_summary",
    # Evidence accumulation
    "EffectEstimate",
    "EvidencePool",
    "AccumulatedEvidence",
    "accumulate_evidence",
    "accumulate_and_propose",
    "generate_proposals_from_accumulated",
    "format_accumulation_report",
]
