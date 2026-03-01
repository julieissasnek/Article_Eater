"""
Notification Service — HITL Enabler for ATLAS
==============================================

Created: 2026-02-27
Sprint: COMPLETENESS-1

File-based notification queue with optional email dispatch.
Enables human-in-the-loop workflows by queuing review requests,
health alerts, and pipeline failure notices.

Design decisions:
- D1: JSON file queue (not DB) — simpler, inspectable, portable
- D2: Email optional — graceful skip if SMTP unconfigured
- Queue at: data/notifications/queue.json
- Archive at: data/notifications/archive/

Notification types:
- EXTRACTION_REVIEW: Paper extracted, awaiting human approval
- QUARANTINE_EXPIRING: Belief nearing 7-day review deadline
- CEILING_VIOLATION: Bridge warrant exceeds type ceiling
- HEALTH_ALERT: AESHI score dropped or critical invariant violated
- PIPELINE_FAILURE: A pipeline stage failed
- INTEGRATION_COMPLETE: Paper successfully integrated into web + BN
"""

from __future__ import annotations

import json
import logging
import os
import smtplib
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Resolve paths relative to repo root
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_DATA_DIR = _REPO_ROOT / "data" / "notifications"
_QUEUE_PATH = _DATA_DIR / "queue.json"
_ARCHIVE_DIR = _DATA_DIR / "archive"


# =============================================================================
# Enums and Data Structures
# =============================================================================

class NotificationType(str, Enum):
    """Types of notifications the system can generate."""
    EXTRACTION_REVIEW = "extraction_review"
    QUARANTINE_EXPIRING = "quarantine_expiring"
    CEILING_VIOLATION = "ceiling_violation"
    HEALTH_ALERT = "health_alert"
    PIPELINE_FAILURE = "pipeline_failure"
    INTEGRATION_COMPLETE = "integration_complete"


class Severity(str, Enum):
    """Notification severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Notification:
    """A single notification in the queue."""
    id: str
    type: str
    severity: str
    title: str
    description: str
    context: Dict[str, Any] = field(default_factory=dict)
    action_url: Optional[str] = None
    created_at: str = ""
    read_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Notification":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

    @property
    def is_read(self) -> bool:
        return self.read_at is not None


# =============================================================================
# Email Templates
# =============================================================================

_EMAIL_TEMPLATES = {
    NotificationType.EXTRACTION_REVIEW: {
        "subject": "[ATLAS] Paper ready for review: {title}",
        "body": (
            "A new paper has been extracted and is ready for your review.\n\n"
            "Paper: {paper_title}\n"
            "DOI: {doi}\n"
            "Claims extracted: {n_claims}\n"
            "Rules inferred: {n_rules}\n\n"
            "To review:\n"
            "  python scripts/review_extractions.py preview {paper_id}\n\n"
            "To approve:\n"
            "  python scripts/review_extractions.py approve {paper_id}\n\n"
            "— ATLAS Overseer"
        ),
    },
    NotificationType.QUARANTINE_EXPIRING: {
        "subject": "[ATLAS] Quarantine deadline approaching: {title}",
        "body": (
            "A belief is approaching its 7-day review deadline.\n\n"
            "Belief ID: {belief_id}\n"
            "Reason: {reason}\n"
            "Days remaining: {days_left}\n\n"
            "Action required: Review and resolve before expiry.\n\n"
            "— ATLAS Overseer"
        ),
    },
    NotificationType.HEALTH_ALERT: {
        "subject": "[ATLAS] Health Alert: {title}",
        "body": (
            "ATLAS system health requires attention.\n\n"
            "{description}\n\n"
            "AESHI Score: {aeshi_score}\n"
            "Band: {band}\n\n"
            "Run health check:\n"
            "  python scripts/overseer_nightly_v2.py\n\n"
            "— ATLAS Overseer"
        ),
    },
    NotificationType.PIPELINE_FAILURE: {
        "subject": "[ATLAS] Pipeline failure: {title}",
        "body": (
            "A pipeline stage has failed.\n\n"
            "Stage: {stage}\n"
            "Error: {error}\n\n"
            "Check logs:\n"
            "  tail -50 logs/pipeline_scheduler.log\n\n"
            "— ATLAS Overseer"
        ),
    },
    NotificationType.INTEGRATION_COMPLETE: {
        "subject": "[ATLAS] Integration complete: {title}",
        "body": (
            "Paper successfully integrated into web of belief + BN.\n\n"
            "Paper: {paper_title}\n"
            "Beliefs added: {n_beliefs}\n"
            "Constraints added: {n_constraints}\n"
            "Coherence impact: {coherence_delta}\n\n"
            "— ATLAS Overseer"
        ),
    },
}


# =============================================================================
# Notification Service
# =============================================================================

class NotificationService:
    """
    File-based notification queue with optional email dispatch.

    Usage:
        ns = NotificationService()
        ns.queue(
            NotificationType.EXTRACTION_REVIEW,
            Severity.WARNING,
            "Paper ready: Smith et al. 2024",
            "3 claims, 5 rules extracted from cortisol study",
            context={"paper_id": "10.1234/foo", "n_claims": 3, "n_rules": 5}
        )

        pending = ns.get_pending()
        ns.mark_read(pending[0].id)
    """

    def __init__(
        self,
        queue_path: Path = None,
        archive_dir: Path = None,
    ):
        self.queue_path = Path(queue_path) if queue_path else _QUEUE_PATH
        self.archive_dir = Path(archive_dir) if archive_dir else _ARCHIVE_DIR
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        # SMTP config from environment (optional)
        self.smtp_host = os.environ.get("AE_SMTP_HOST")
        self.smtp_port = int(os.environ.get("AE_SMTP_PORT", "587"))
        self.smtp_user = os.environ.get("AE_SMTP_USER")
        self.smtp_pass = os.environ.get("AE_SMTP_PASS")
        self.notify_email = os.environ.get(
            "AE_NOTIFY_EMAIL", "dkirsh@gmail.com"
        )
        self.from_email = os.environ.get(
            "AE_FROM_EMAIL", "atlas-overseer@ucsd.edu"
        )

    # -------------------------------------------------------------------------
    # Queue Operations
    # -------------------------------------------------------------------------

    def _load_queue(self) -> List[Dict[str, Any]]:
        """Load the notification queue from disk."""
        if self.queue_path.exists():
            try:
                return json.loads(
                    self.queue_path.read_text(encoding="utf-8")
                )
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load queue: {e}")
                return []
        return []

    def _save_queue(self, items: List[Dict[str, Any]]) -> None:
        """Persist the notification queue to disk."""
        try:
            self.queue_path.write_text(
                json.dumps(items, indent=2, default=str),
                encoding="utf-8",
            )
        except IOError as e:
            logger.error(f"Failed to save queue: {e}")

    def queue(
        self,
        type_: NotificationType,
        severity: Severity,
        title: str,
        description: str,
        context: Dict[str, Any] = None,
        action_url: str = None,
        send_email: bool = True,
    ) -> str:
        """
        Add a notification to the queue.

        Returns the notification ID.
        """
        notif = Notification(
            id=str(uuid.uuid4())[:8],
            type=type_.value if isinstance(type_, NotificationType) else type_,
            severity=severity.value if isinstance(severity, Severity) else severity,
            title=title,
            description=description,
            context=context or {},
            action_url=action_url,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        items = self._load_queue()
        items.append(notif.to_dict())
        self._save_queue(items)

        logger.info(
            f"Notification queued: [{notif.severity.upper()}] {notif.title} "
            f"(id={notif.id})"
        )

        # Optionally send email
        if send_email and self.smtp_host:
            try:
                self.dispatch_email(notif)
            except Exception as e:
                logger.warning(f"Email dispatch failed (non-fatal): {e}")

        return notif.id

    def get_pending(
        self,
        filter_type: NotificationType = None,
        filter_severity: Severity = None,
    ) -> List[Notification]:
        """Return all unread notifications, optionally filtered."""
        items = self._load_queue()
        result = []
        for item in items:
            if item.get("read_at"):
                continue
            if filter_type and item.get("type") != filter_type.value:
                continue
            if filter_severity and item.get("severity") != filter_severity.value:
                continue
            result.append(Notification.from_dict(item))
        return result

    def get_all(self) -> List[Notification]:
        """Return all notifications (read and unread)."""
        items = self._load_queue()
        return [Notification.from_dict(i) for i in items]

    def mark_read(self, notif_id: str) -> bool:
        """Mark a notification as read. Returns True if found."""
        items = self._load_queue()
        found = False
        for item in items:
            if item.get("id") == notif_id:
                item["read_at"] = datetime.now(timezone.utc).isoformat()
                found = True
                break
        if found:
            self._save_queue(items)
            logger.info(f"Notification marked read: {notif_id}")
        return found

    def archive_read(self) -> int:
        """Move all read notifications to the archive. Returns count archived."""
        items = self._load_queue()
        pending = [i for i in items if not i.get("read_at")]
        archived = [i for i in items if i.get("read_at")]

        if archived:
            # Append to daily archive file
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            archive_path = self.archive_dir / f"archived_{today}.json"
            existing = []
            if archive_path.exists():
                try:
                    existing = json.loads(
                        archive_path.read_text(encoding="utf-8")
                    )
                except (json.JSONDecodeError, IOError):
                    pass
            existing.extend(archived)
            archive_path.write_text(
                json.dumps(existing, indent=2, default=str),
                encoding="utf-8",
            )
            self._save_queue(pending)
            logger.info(f"Archived {len(archived)} read notifications")

        return len(archived)

    # -------------------------------------------------------------------------
    # Email Dispatch
    # -------------------------------------------------------------------------

    def dispatch_email(
        self,
        notif: Notification,
        recipients: List[str] = None,
    ) -> bool:
        """
        Send a notification via email. Returns True on success.

        Gracefully skips if SMTP is not configured.
        """
        if not self.smtp_host:
            logger.debug("SMTP not configured; skipping email dispatch")
            return False

        recipients = recipients or [self.notify_email]
        notif_type = NotificationType(notif.type)
        template = _EMAIL_TEMPLATES.get(notif_type)

        if template:
            # Merge context into template
            merge_vars = {"title": notif.title, "description": notif.description}
            merge_vars.update(notif.context)
            subject = template["subject"].format_map(
                _SafeFormatDict(merge_vars)
            )
            body = template["body"].format_map(_SafeFormatDict(merge_vars))
        else:
            subject = f"[ATLAS] {notif.title}"
            body = f"{notif.description}\n\nContext: {json.dumps(notif.context, indent=2)}"

        msg = MIMEMultipart()
        msg["From"] = self.from_email
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.ehlo()
                if self.smtp_port == 587:
                    server.starttls()
                if self.smtp_user and self.smtp_pass:
                    server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            logger.info(f"Email sent: {subject} → {recipients}")
            return True
        except Exception as e:
            logger.warning(f"Email dispatch failed: {e}")
            return False

    # -------------------------------------------------------------------------
    # Digest Generation
    # -------------------------------------------------------------------------

    def generate_digest(self) -> str:
        """Generate a markdown digest of all pending notifications."""
        pending = self.get_pending()
        if not pending:
            return "# ATLAS Notification Digest\n\nNo pending notifications."

        lines = [
            "# ATLAS Notification Digest",
            f"*Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*",
            f"**{len(pending)} pending notification(s)**",
            "",
        ]

        # Group by severity
        by_severity = {"critical": [], "warning": [], "info": []}
        for n in pending:
            by_severity.get(n.severity, by_severity["info"]).append(n)

        for sev in ["critical", "warning", "info"]:
            items = by_severity[sev]
            if items:
                lines.append(f"## {sev.upper()} ({len(items)})")
                lines.append("")
                for n in items:
                    lines.append(f"- **[{n.type}]** {n.title}")
                    lines.append(f"  {n.description}")
                    if n.action_url:
                        lines.append(f"  Action: {n.action_url}")
                    lines.append(f"  _{n.created_at}_ (id: {n.id})")
                    lines.append("")

        return "\n".join(lines)


# =============================================================================
# Helpers
# =============================================================================

class _SafeFormatDict(dict):
    """Dict that returns '{key}' for missing keys instead of raising KeyError."""
    def __missing__(self, key):
        return f"{{{key}}}"


# =============================================================================
# Convenience Functions (for use in other modules)
# =============================================================================

_default_service: Optional[NotificationService] = None


def get_notification_service() -> NotificationService:
    """Get or create the default notification service singleton."""
    global _default_service
    if _default_service is None:
        _default_service = NotificationService()
    return _default_service


def notify(
    type_: NotificationType,
    severity: Severity,
    title: str,
    description: str,
    context: Dict[str, Any] = None,
    **kwargs,
) -> str:
    """Convenience function to queue a notification."""
    return get_notification_service().queue(
        type_, severity, title, description, context, **kwargs
    )


def notify_extraction_ready(
    paper_id: str,
    title: str = "",
    n_claims: int = 0,
    n_rules: int = 0,
    doi: str = "",
) -> str:
    """Notify that a paper extraction is ready for human review."""
    return notify(
        NotificationType.EXTRACTION_REVIEW,
        Severity.WARNING,
        f"Paper ready for review: {title or paper_id}",
        f"{n_claims} claims and {n_rules} rules extracted, awaiting approval",
        context={
            "paper_id": paper_id,
            "paper_title": title,
            "doi": doi,
            "n_claims": n_claims,
            "n_rules": n_rules,
        },
    )


def notify_health_alert(
    aeshi_score: float,
    band: str,
    details: str = "",
) -> str:
    """Notify about a health alert."""
    severity = Severity.CRITICAL if aeshi_score < 40 else Severity.WARNING
    return notify(
        NotificationType.HEALTH_ALERT,
        severity,
        f"AESHI {aeshi_score:.0f} ({band})",
        details or f"System health score is {aeshi_score:.1f}/100 ({band})",
        context={"aeshi_score": aeshi_score, "band": band},
    )


def notify_pipeline_failure(
    stage: str,
    error: str,
) -> str:
    """Notify about a pipeline stage failure."""
    return notify(
        NotificationType.PIPELINE_FAILURE,
        Severity.WARNING,
        f"Pipeline stage failed: {stage}",
        f"Stage '{stage}' encountered an error: {error}",
        context={"stage": stage, "error": error},
    )


def notify_quarantine_expiring(
    belief_id: str,
    reason: str,
    days_left: int,
) -> str:
    """Notify about a quarantine deadline approaching."""
    severity = Severity.CRITICAL if days_left <= 1 else Severity.WARNING
    return notify(
        NotificationType.QUARANTINE_EXPIRING,
        severity,
        f"Quarantine expiring: belief {belief_id[:12]}...",
        f"Review deadline in {days_left} day(s). Reason: {reason}",
        context={
            "belief_id": belief_id,
            "reason": reason,
            "days_left": days_left,
        },
    )
