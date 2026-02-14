"""
Epistemic contracts for web ingestion (Sprint 6a).

Provides ae.claim.v2 and ae.edge.v2 dataclasses for universal
node and edge ingestion into the web of belief.
"""

from .claim_v2 import ClaimV2
from .edge_v2 import EdgeV2

__all__ = ["ClaimV2", "EdgeV2"]
