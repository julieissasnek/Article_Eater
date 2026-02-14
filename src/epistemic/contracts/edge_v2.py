"""
ae.edge.v2 Contract (Sprint 6a / Task 6a.4).

Universal edge ingestion contract for all edge types.
Every edge entering the web must conform to this contract.

Reference: Non_Empirical_Web_Integration_Spec_V1.0.md §6.3
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class EvidenceBasisEdge(str, Enum):
    """How the edge was established."""
    EXPLICIT_STATEMENT = "explicit_statement"
    IMPLICIT_CONNECTION = "implicit_connection"
    REVIEWER_INTERPRETATION = "reviewer_interpretation"


@dataclass
class EdgeV2:
    """
    Universal edge ingestion contract (ae.edge.v2).

    Required fields:
        edge_id, edge_type, source_node_id, target_node_id, weight, paper_id

    Optional fields:
        evidence_basis, justification, provenance_tier, needs_verification
    """
    # === REQUIRED ===
    edge_id: str
    edge_type: str  # One of the EdgeType values
    source_node_id: str
    target_node_id: str
    weight: float  # [0, 1]
    paper_id: str  # Paper that justifies this edge

    # === OPTIONAL ===
    evidence_basis: Optional[str] = None  # explicit_statement | implicit_connection | reviewer_interpretation
    justification: Optional[str] = None  # Human-readable reason
    provenance_tier: Optional[str] = None  # abstract_provisional | pdf_confirmed
    needs_verification: bool = False  # True for attributed findings from reviews

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "edge_id": self.edge_id,
            "edge_type": self.edge_type,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "weight": self.weight,
            "paper_id": self.paper_id,
            "evidence_basis": self.evidence_basis,
            "justification": self.justification,
            "provenance_tier": self.provenance_tier,
            "needs_verification": self.needs_verification,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EdgeV2":
        """Create from dictionary."""
        return cls(
            edge_id=data.get("edge_id", ""),
            edge_type=data.get("edge_type", ""),
            source_node_id=data.get("source_node_id", ""),
            target_node_id=data.get("target_node_id", ""),
            weight=data.get("weight", 0.5),
            paper_id=data.get("paper_id", ""),
            evidence_basis=data.get("evidence_basis"),
            justification=data.get("justification"),
            provenance_tier=data.get("provenance_tier"),
            needs_verification=data.get("needs_verification", False),
        )
