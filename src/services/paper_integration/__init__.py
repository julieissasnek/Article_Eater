"""
Paper Integration Pipeline — End-to-End Approved Paper Propagation
==================================================================

Created: 2026-02-25
Sprint: INTEGRATION-1

When a paper's extraction is ACCEPTED, this package orchestrates propagation
through the entire CMR system: web of belief, Bayesian network, tag
precomputation, molecule QA cache, T1/T1.5/T2 linkages, provenance database,
and the QA system.

Core components:
- PaperIntegrationOrchestrator: 14-step cascade coordinator
- SupersessionResolver: Detects when newer papers replace older findings
- IntegrationRollback: Paper-level undo via pre-integration snapshots
- TagAssignmentEngine: 3D taxonomy (entity/topic, theoretical, effect_size)
- MoleculeLinker: Belief → template → molecule → T1.5 hookup

Design principles:
- Atomic per-paper (single transaction, partial integration never visible)
- Idempotent (re-running with same paper_id is safe)
- Triggered on-demand (when paper status → ACCEPTED)
- Readily rescinded (any integration can be rolled back)
- Non-critical steps don't block (tags, molecules, BN, QA can fail gracefully)
- Provenance-tracked (every belief knows which paper(s) contributed to it)
"""

from src.services.paper_integration.models import (
    PaperIntegrationEvent,
    CascadeStep,
    SupersessionRecord,
    IntegrationAction,
    IntegrationStatus,
    SupersessionReason,
    CascadeStepStatus,
)
