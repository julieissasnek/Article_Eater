"""
Extraction Approval Service — HITL Gate for ATLAS Integration
=============================================================

Created: 2026-02-27
Sprint: COMPLETENESS-1

Provides the human-in-the-loop gate between extraction (Gemini) and
integration (14-step cascade). Papers must be explicitly APPROVED before
they enter the web of belief and Bayesian network.

Design decision D4: Extraction approval is an explicit HITL gate.
Prevents bad extractions from corrupting the epistemic web.

Workflow:
    PDF → Gemini Extraction → ACCEPTED in queue
        → Human reviews via CLI or dashboard
        → APPROVED → triggers orchestrator.integrate_paper()
        → REJECTED → logged with reason, optionally re-queued

Usage:
    from src.services.extraction_approval import ExtractionApprovalService
    svc = ExtractionApprovalService()

    pending = svc.get_pending_approvals()
    summary = svc.get_review_summary(paper_id)
    svc.approve(paper_id, notes="Looks good")
    svc.reject(paper_id, reason="Too few claims")
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_DATA_DIR = _REPO_ROOT / "data"
_QUEUE_PATH = _DATA_DIR / "extraction_pipeline" / "extraction_queue.json"
_EXTRACTIONS_DIR = _DATA_DIR / "extractions"
_APPROVAL_LOG = _DATA_DIR / "notifications" / "approval_log.json"


class ExtractionApprovalService:
    """
    HITL gate between extraction and integration.

    Reads the extraction queue to find papers with status 'accepted'
    (meaning Gemini extraction succeeded and validation passed),
    then provides approve/reject operations.
    """

    def __init__(
        self,
        queue_path: Path = None,
        extractions_dir: Path = None,
    ):
        self.queue_path = Path(queue_path) if queue_path else _QUEUE_PATH
        self.extractions_dir = Path(extractions_dir) if extractions_dir else _EXTRACTIONS_DIR
        self.approval_log_path = _APPROVAL_LOG
        self.approval_log_path.parent.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------------------
    # Queue Access
    # -------------------------------------------------------------------------

    def _load_queue(self) -> Dict[str, Any]:
        """Load the extraction queue."""
        if not self.queue_path.exists():
            return {"stats": {}, "items": {}}
        raw = json.loads(self.queue_path.read_text(encoding="utf-8"))
        if isinstance(raw, dict) and "items" in raw:
            return raw
        # Legacy format: flat dict of DOI → item
        return {"stats": {}, "items": raw if isinstance(raw, dict) else {}}

    def _save_queue(self, queue: Dict[str, Any]) -> None:
        """Save the extraction queue."""
        queue["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.queue_path.write_text(
            json.dumps(queue, indent=2, default=str),
            encoding="utf-8",
        )

    def _log_approval_action(
        self, paper_id: str, action: str, notes: str = ""
    ) -> None:
        """Append to the approval log."""
        log_items = []
        if self.approval_log_path.exists():
            try:
                log_items = json.loads(
                    self.approval_log_path.read_text(encoding="utf-8")
                )
            except (json.JSONDecodeError, IOError):
                pass

        log_items.append({
            "paper_id": paper_id,
            "action": action,
            "notes": notes,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        self.approval_log_path.write_text(
            json.dumps(log_items, indent=2, default=str),
            encoding="utf-8",
        )

    # -------------------------------------------------------------------------
    # Approval Operations
    # -------------------------------------------------------------------------

    def get_pending_approvals(self) -> List[Dict[str, Any]]:
        """
        Return papers that have been extracted and accepted but not yet
        approved for integration.

        These are papers with status='accepted' in the extraction queue.
        """
        queue = self._load_queue()
        items = queue.get("items", {})
        pending = []

        for paper_id, item in items.items():
            if not isinstance(item, dict):
                continue
            status = item.get("status", "")
            if status == "accepted":
                pending.append({
                    "paper_id": paper_id,
                    "doi": item.get("doi", paper_id),
                    "article_type": item.get("article_type", "unknown"),
                    "priority": item.get("priority", 0),
                    "classification_confidence": item.get(
                        "classification_confidence", 0
                    ),
                    "extraction_result": item.get("extraction_result"),
                })

        # Sort by priority (higher first)
        pending.sort(key=lambda x: x.get("priority", 0), reverse=True)
        return pending

    def get_review_summary(self, paper_id: str) -> Dict[str, Any]:
        """
        Generate a human-readable review summary for a paper.

        Returns claim count, rule count, theory links, and key metadata.
        """
        queue = self._load_queue()
        items = queue.get("items", {})
        item = items.get(paper_id, {})

        if not isinstance(item, dict):
            return {"error": f"Paper {paper_id} not found in queue"}

        extraction = item.get("extraction_result", {})
        findings = extraction.get("findings", []) if extraction else []

        # Count claims and rules
        n_claims = len(findings)
        n_rules = sum(
            1 for f in findings
            if f.get("antecedent") and f.get("consequent")
        )

        # Collect theory links
        theories = set()
        for f in findings:
            for t in f.get("theory_links", []):
                if isinstance(t, str):
                    theories.add(t)
                elif isinstance(t, dict):
                    theories.add(t.get("theory", "unknown"))

        # Effect sizes
        with_effect = sum(1 for f in findings if f.get("effect_size"))
        with_pvalue = sum(1 for f in findings if f.get("p_value"))

        return {
            "paper_id": paper_id,
            "doi": item.get("doi", paper_id),
            "article_type": item.get("article_type", "unknown"),
            "status": item.get("status"),
            "n_claims": n_claims,
            "n_rules": n_rules,
            "theories": sorted(theories),
            "with_effect_size": with_effect,
            "with_p_value": with_pvalue,
            "findings_preview": findings[:3],  # First 3 for preview
        }

    def approve(
        self,
        paper_id: str,
        reviewer_notes: str = "",
    ) -> Dict[str, Any]:
        """
        Approve a paper for integration into the web of belief + BN.

        This transitions the paper from 'accepted' to 'approved' and
        triggers the 14-step integration cascade.
        """
        queue = self._load_queue()
        items = queue.get("items", {})

        if paper_id not in items:
            return {"success": False, "error": f"Paper {paper_id} not found"}

        item = items[paper_id]
        if not isinstance(item, dict):
            return {"success": False, "error": "Invalid queue item format"}

        current_status = item.get("status", "")
        if current_status != "accepted":
            return {
                "success": False,
                "error": (
                    f"Can only approve 'accepted' papers, "
                    f"got '{current_status}'"
                ),
            }

        # Transition to approved
        item["status"] = "approved"
        item["approved_at"] = datetime.now(timezone.utc).isoformat()
        item["reviewer_notes"] = reviewer_notes

        # Update stats
        stats = queue.get("stats", {})
        stats["accepted"] = max(0, stats.get("accepted", 0) - 1)
        stats["approved"] = stats.get("approved", 0) + 1
        queue["stats"] = stats

        self._save_queue(queue)
        self._log_approval_action(paper_id, "approved", reviewer_notes)

        logger.info(f"Paper APPROVED for integration: {paper_id}")

        # Attempt to trigger integration
        integration_result = self._trigger_integration(paper_id)

        # Notify completion
        try:
            from src.services.notification_service import (
                notify, NotificationType, Severity,
            )
            if integration_result.get("success"):
                notify(
                    NotificationType.INTEGRATION_COMPLETE,
                    Severity.INFO,
                    f"Integration complete: {paper_id[:40]}",
                    f"Paper integrated into web + BN. {reviewer_notes}",
                    context={"paper_id": paper_id},
                    send_email=False,
                )
        except Exception as e:
            logger.debug(f"Notification failed: {e}")

        return {
            "success": True,
            "paper_id": paper_id,
            "integration": integration_result,
        }

    def reject(
        self,
        paper_id: str,
        reason: str = "",
        requeue: bool = False,
    ) -> Dict[str, Any]:
        """
        Reject a paper's extraction. Optionally re-queue for re-extraction.
        """
        queue = self._load_queue()
        items = queue.get("items", {})

        if paper_id not in items:
            return {"success": False, "error": f"Paper {paper_id} not found"}

        item = items[paper_id]
        if not isinstance(item, dict):
            return {"success": False, "error": "Invalid queue item format"}

        if requeue:
            item["status"] = "requeued"
            stats = queue.get("stats", {})
            stats["accepted"] = max(0, stats.get("accepted", 0) - 1)
            stats["requeued"] = stats.get("requeued", 0) + 1
            queue["stats"] = stats
            logger.info(f"Paper REJECTED and re-queued: {paper_id}")
        else:
            item["status"] = "rejected"
            stats = queue.get("stats", {})
            stats["accepted"] = max(0, stats.get("accepted", 0) - 1)
            stats["rejected"] = stats.get("rejected", 0) + 1
            queue["stats"] = stats
            logger.info(f"Paper REJECTED: {paper_id}")

        item["rejected_at"] = datetime.now(timezone.utc).isoformat()
        item["rejection_reason"] = reason

        self._save_queue(queue)
        self._log_approval_action(paper_id, "rejected", reason)

        return {"success": True, "paper_id": paper_id, "requeued": requeue}

    def _trigger_integration(self, paper_id: str) -> Dict[str, Any]:
        """
        Trigger the 14-step integration cascade for an approved paper.

        Returns integration result or error.
        """
        try:
            from src.services.paper_integration.orchestrator import (
                PaperIntegrationOrchestrator,
            )
            orchestrator = PaperIntegrationOrchestrator()
            event = orchestrator.integrate_paper(paper_id)
            logger.info(f"Integration triggered for {paper_id}: {event}")
            return {"success": True, "event": str(event)}
        except ImportError:
            logger.warning(
                "IntegrationOrchestrator not available — "
                "paper approved but integration must be run manually"
            )
            return {
                "success": False,
                "error": "Orchestrator not available in this environment",
            }
        except Exception as e:
            logger.error(f"Integration failed for {paper_id}: {e}")
            return {"success": False, "error": str(e)}
