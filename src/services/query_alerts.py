"""
Query Alerts and Monitoring System.
Sprint 3.0.2-G — 2026-02-09

Provides alerting and monitoring capabilities for the Web of Belief:
- Watch lists for beliefs, theories, and topics
- Threshold-based alerts for credence changes
- Status change notifications
- New evidence alerts
- Periodic digest generation
- Webhook integration for external systems

Design Decisions (to be reviewed by panel):
D1. Alert condition types: credence_change, status_change, new_evidence,
    entrenchment_change, constraint_added, theory_shift
D2. Notification delivery: in-app queue + webhook + email placeholder
D3. Alert persistence: SQLite for durability, in-memory cache for speed
D4. Watch granularity: belief_id, theory_id, topic_pattern, credence_range
D5. Threshold semantics: absolute delta AND percentage change supported
D6. Deduplication: 5-minute window with configurable cooldown per watch
D7. Historical retention: 30 days default, configurable per watch

Created: 2026-02-09
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import sqlite3
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict
import os

logger = logging.getLogger(__name__)


# =============================================================================
# ALERT TYPES AND CONDITIONS
# =============================================================================


class AlertType(Enum):
    """
    Types of alerts that can be triggered.

    Panel Review (2026-02-09): Removed ENTRENCHMENT_CHANGE as redundant
    since entrenchment is now emergent (V23.0.0) and changes are always
    downstream of other alertable events (constraint changes, coherence shifts).
    """
    # Belief-level alerts
    CREDENCE_CHANGE = "credence_change"       # Belief credence changed significantly
    STATUS_CHANGE = "status_change"            # Belief status changed (ACCEPTED→CONTESTED)
    NEW_EVIDENCE = "new_evidence"              # New evidence added to belief
    STALE_EVIDENCE = "stale_evidence"          # Belief hasn't received evidence in X days

    # Constraint-level alerts
    CONSTRAINT_ADDED = "constraint_added"      # New constraint involving watched belief
    CONSTRAINT_REMOVED = "constraint_removed"  # Constraint removed

    # Theory-level alerts
    THEORY_SHIFT = "theory_shift"              # Theory average credence changed
    THEORY_CONTESTED = "theory_contested"      # Theory has contested beliefs

    # System-level alerts
    COHERENCE_DROP = "coherence_drop"          # Overall coherence dropped
    NEW_STUB = "new_stub"                      # New stub belief added (potential gap)

    # Custom pattern alerts
    PATTERN_MATCH = "pattern_match"            # Custom pattern matched


class AlertSeverity(Enum):
    """Severity levels for alerts."""
    INFO = "info"           # Informational
    WARNING = "warning"     # Attention needed
    CRITICAL = "critical"   # Immediate attention


class AlertStatus(Enum):
    """Status of an alert."""
    PENDING = "pending"       # Not yet delivered
    DELIVERED = "delivered"   # Sent to notification channel
    ACKNOWLEDGED = "acknowledged"  # User acknowledged
    RESOLVED = "resolved"     # Issue resolved
    EXPIRED = "expired"       # Past retention period


@dataclass
class AlertCondition:
    """
    Condition that triggers an alert.

    Design Decision D5: Support both absolute and percentage thresholds.
    """
    alert_type: AlertType
    threshold_absolute: Optional[float] = None  # Absolute change (e.g., 0.1)
    threshold_percentage: Optional[float] = None  # Percentage change (e.g., 10.0)
    direction: Optional[str] = None  # "increase", "decrease", or "any"
    min_credence: Optional[float] = None  # Only alert if credence above this
    max_credence: Optional[float] = None  # Only alert if credence below this

    def is_triggered(
        self,
        old_value: Optional[float],
        new_value: float,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str]:
        """
        Check if condition is triggered.

        Returns:
            Tuple of (is_triggered, reason_string)
        """
        # Status/evidence changes don't need threshold checks
        if self.alert_type in [
            AlertType.STATUS_CHANGE,
            AlertType.NEW_EVIDENCE,
            AlertType.STALE_EVIDENCE,
            AlertType.CONSTRAINT_ADDED,
            AlertType.CONSTRAINT_REMOVED,
            AlertType.NEW_STUB,
            AlertType.PATTERN_MATCH
        ]:
            return True, f"{self.alert_type.value} detected"

        # Need old value for change detection
        if old_value is None:
            return False, "No previous value"

        # Calculate changes
        absolute_change = new_value - old_value
        percentage_change = (absolute_change / old_value * 100) if old_value != 0 else 0

        # Check direction
        if self.direction == "increase" and absolute_change <= 0:
            return False, "Change not in specified direction"
        if self.direction == "decrease" and absolute_change >= 0:
            return False, "Change not in specified direction"

        # Check thresholds
        triggered = False
        reason_parts = []

        if self.threshold_absolute is not None:
            if abs(absolute_change) >= self.threshold_absolute:
                triggered = True
                reason_parts.append(f"absolute change {absolute_change:.3f} >= {self.threshold_absolute}")

        if self.threshold_percentage is not None:
            if abs(percentage_change) >= self.threshold_percentage:
                triggered = True
                reason_parts.append(f"percentage change {percentage_change:.1f}% >= {self.threshold_percentage}%")

        # Check credence bounds
        if self.min_credence is not None and new_value < self.min_credence:
            return False, f"New value {new_value} below min_credence {self.min_credence}"
        if self.max_credence is not None and new_value > self.max_credence:
            return False, f"New value {new_value} above max_credence {self.max_credence}"

        reason = "; ".join(reason_parts) if reason_parts else "Threshold check failed"
        return triggered, reason

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "alert_type": self.alert_type.value,
            "threshold_absolute": self.threshold_absolute,
            "threshold_percentage": self.threshold_percentage,
            "direction": self.direction,
            "min_credence": self.min_credence,
            "max_credence": self.max_credence
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AlertCondition":
        """Create from dictionary."""
        return cls(
            alert_type=AlertType(data["alert_type"]),
            threshold_absolute=data.get("threshold_absolute"),
            threshold_percentage=data.get("threshold_percentage"),
            direction=data.get("direction"),
            min_credence=data.get("min_credence"),
            max_credence=data.get("max_credence")
        )


# =============================================================================
# WATCH DEFINITIONS
# =============================================================================


class WatchTarget(Enum):
    """What entity is being watched."""
    BELIEF = "belief"           # Specific belief ID
    THEORY = "theory"           # Theory ID
    TOPIC = "topic"             # Topic pattern (regex)
    CREDENCE_RANGE = "credence_range"  # All beliefs in credence range
    LEVEL = "level"             # All beliefs at epistemic level
    SYSTEM = "system"           # System-wide metrics


@dataclass
class Watch:
    """
    A watch definition that monitors for specific conditions.

    Design Decision D4: Support multiple granularities of watching.
    Design Decision D6: Include cooldown for deduplication.
    """
    watch_id: str
    name: str
    target_type: WatchTarget
    target_id: Optional[str] = None  # belief_id, theory_id, or pattern
    conditions: List[AlertCondition] = field(default_factory=list)

    # Notification settings
    notify_webhook: Optional[str] = None
    notify_email: Optional[str] = None
    notify_in_app: bool = True

    # Deduplication (Design Decision D6)
    cooldown_minutes: int = 5  # Don't re-alert within this window
    last_triggered: Optional[datetime] = None

    # Retention (Design Decision D7)
    retention_days: int = 30

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None
    enabled: bool = True
    description: Optional[str] = None

    def can_trigger(self) -> bool:
        """Check if watch can trigger (respecting cooldown)."""
        if not self.enabled:
            return False
        if self.last_triggered is None:
            return True
        cooldown_end = self.last_triggered + timedelta(minutes=self.cooldown_minutes)
        return datetime.now(timezone.utc) >= cooldown_end

    def matches_belief(self, belief_id: str, belief_content: str, theory_id: Optional[str], level: Optional[str]) -> bool:
        """Check if a belief matches this watch's target."""
        if self.target_type == WatchTarget.BELIEF:
            return belief_id == self.target_id

        if self.target_type == WatchTarget.THEORY:
            return theory_id == self.target_id

        if self.target_type == WatchTarget.TOPIC:
            # Regex pattern matching on content
            if self.target_id:
                try:
                    return bool(re.search(self.target_id, belief_content, re.IGNORECASE))
                except re.error:
                    return False
            return False

        if self.target_type == WatchTarget.LEVEL:
            return level == self.target_id

        if self.target_type == WatchTarget.SYSTEM:
            return True  # System watches match everything

        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for persistence."""
        return {
            "watch_id": self.watch_id,
            "name": self.name,
            "target_type": self.target_type.value,
            "target_id": self.target_id,
            "conditions": [c.to_dict() for c in self.conditions],
            "notify_webhook": self.notify_webhook,
            "notify_email": self.notify_email,
            "notify_in_app": self.notify_in_app,
            "cooldown_minutes": self.cooldown_minutes,
            "last_triggered": self.last_triggered.isoformat() if self.last_triggered else None,
            "retention_days": self.retention_days,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "enabled": self.enabled,
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Watch":
        """Create from dictionary."""
        return cls(
            watch_id=data["watch_id"],
            name=data["name"],
            target_type=WatchTarget(data["target_type"]),
            target_id=data.get("target_id"),
            conditions=[AlertCondition.from_dict(c) for c in data.get("conditions", [])],
            notify_webhook=data.get("notify_webhook"),
            notify_email=data.get("notify_email"),
            notify_in_app=data.get("notify_in_app", True),
            cooldown_minutes=data.get("cooldown_minutes", 5),
            last_triggered=datetime.fromisoformat(data["last_triggered"]) if data.get("last_triggered") else None,
            retention_days=data.get("retention_days", 30),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(timezone.utc),
            created_by=data.get("created_by"),
            enabled=data.get("enabled", True),
            description=data.get("description")
        )


# =============================================================================
# ALERT DEFINITION
# =============================================================================


@dataclass
class Alert:
    """
    An alert that was triggered.
    """
    alert_id: str
    watch_id: str
    alert_type: AlertType
    severity: AlertSeverity
    status: AlertStatus

    # What triggered it
    entity_type: str  # belief, theory, system
    entity_id: Optional[str]
    entity_content: Optional[str]

    # Change details
    old_value: Optional[float]
    new_value: Optional[float]
    change_description: str

    # Metadata
    triggered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    delivered_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None

    # Context
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "watch_id": self.watch_id,
            "alert_type": self.alert_type.value,
            "severity": self.severity.value,
            "status": self.status.value,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "entity_content": self.entity_content,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "change_description": self.change_description,
            "triggered_at": self.triggered_at.isoformat(),
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "acknowledged_by": self.acknowledged_by,
            "context": self.context
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Alert":
        """Create from dictionary."""
        return cls(
            alert_id=data["alert_id"],
            watch_id=data["watch_id"],
            alert_type=AlertType(data["alert_type"]),
            severity=AlertSeverity(data["severity"]),
            status=AlertStatus(data["status"]),
            entity_type=data["entity_type"],
            entity_id=data.get("entity_id"),
            entity_content=data.get("entity_content"),
            old_value=data.get("old_value"),
            new_value=data.get("new_value"),
            change_description=data["change_description"],
            triggered_at=datetime.fromisoformat(data["triggered_at"]),
            delivered_at=datetime.fromisoformat(data["delivered_at"]) if data.get("delivered_at") else None,
            acknowledged_at=datetime.fromisoformat(data["acknowledged_at"]) if data.get("acknowledged_at") else None,
            acknowledged_by=data.get("acknowledged_by"),
            context=data.get("context", {})
        )


# =============================================================================
# NOTIFICATION HANDLERS
# =============================================================================


class NotificationHandler(ABC):
    """Abstract base for notification delivery."""

    @abstractmethod
    def send(self, alert: Alert, watch: Watch) -> bool:
        """Send notification. Returns True if successful."""
        pass


class InAppNotificationHandler(NotificationHandler):
    """In-app notification queue."""

    def __init__(self):
        self.notifications: List[Alert] = []
        self._lock = threading.Lock()

    def send(self, alert: Alert, watch: Watch) -> bool:
        """Add to in-app queue."""
        with self._lock:
            self.notifications.append(alert)
            logger.info(f"In-app notification queued: {alert.alert_id}")
        return True

    def get_pending(self, limit: int = 50) -> List[Alert]:
        """Get pending notifications."""
        with self._lock:
            pending = [a for a in self.notifications if a.status == AlertStatus.PENDING]
            return pending[:limit]

    def acknowledge(self, alert_id: str, user: Optional[str] = None) -> bool:
        """Acknowledge a notification."""
        with self._lock:
            for alert in self.notifications:
                if alert.alert_id == alert_id:
                    alert.status = AlertStatus.ACKNOWLEDGED
                    alert.acknowledged_at = datetime.now(timezone.utc)
                    alert.acknowledged_by = user
                    return True
        return False


class WebhookNotificationHandler(NotificationHandler):
    """
    Webhook notification delivery.

    Panel Review (2026-02-09): Reduced timeout from 10s to 5s per Kahneman.
    Most webhooks respond in <1s; long timeouts block the alert loop.
    """

    def __init__(self, timeout: int = 5):
        self.timeout = timeout

    def send(self, alert: Alert, watch: Watch) -> bool:
        """Send webhook notification."""
        if not watch.notify_webhook:
            return False

        try:
            import urllib.request
            import urllib.error

            payload = json.dumps({
                "alert": alert.to_dict(),
                "watch": {
                    "watch_id": watch.watch_id,
                    "name": watch.name
                }
            }).encode("utf-8")

            req = urllib.request.Request(
                watch.notify_webhook,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                if response.status == 200:
                    logger.info(f"Webhook sent successfully: {alert.alert_id}")
                    return True
                else:
                    logger.warning(f"Webhook returned status {response.status}")
                    return False

        except Exception as e:
            logger.error(f"Webhook delivery failed: {e}")
            return False


class EmailNotificationHandler(NotificationHandler):
    """Email notification (placeholder - would integrate with SMTP)."""

    def send(self, alert: Alert, watch: Watch) -> bool:
        """Send email notification (placeholder)."""
        if not watch.notify_email:
            return False

        # Placeholder - would integrate with SMTP or email service
        logger.info(f"Email notification would be sent to {watch.notify_email}: {alert.alert_id}")
        return True


# =============================================================================
# ALERT STORAGE
# =============================================================================


class AlertStorage:
    """
    Persistent storage for watches and alerts.

    Design Decision D3: SQLite for durability with in-memory cache.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.environ.get("AE_ALERTS_DB", "alerts.db")
        self._init_db()
        self._cache: Dict[str, Watch] = {}
        self._cache_loaded = False

    def _init_db(self):
        """
        Initialize database schema.

        Panel Review (2026-02-09): Enable WAL mode per Simon for better
        concurrent access (multiple Streamlit sessions).
        """
        import os
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Enable WAL mode for better concurrent access
        cursor.execute("PRAGMA journal_mode=WAL")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS watches (
                watch_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                target_type TEXT NOT NULL,
                target_id TEXT,
                conditions TEXT,
                notify_webhook TEXT,
                notify_email TEXT,
                notify_in_app INTEGER DEFAULT 1,
                cooldown_minutes INTEGER DEFAULT 5,
                last_triggered TEXT,
                retention_days INTEGER DEFAULT 30,
                created_at TEXT,
                created_by TEXT,
                enabled INTEGER DEFAULT 1,
                description TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                alert_id TEXT PRIMARY KEY,
                watch_id TEXT,
                alert_type TEXT,
                severity TEXT,
                status TEXT,
                entity_type TEXT,
                entity_id TEXT,
                entity_content TEXT,
                old_value REAL,
                new_value REAL,
                change_description TEXT,
                triggered_at TEXT,
                delivered_at TEXT,
                acknowledged_at TEXT,
                acknowledged_by TEXT,
                context TEXT,
                FOREIGN KEY (watch_id) REFERENCES watches(watch_id)
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alerts_watch ON alerts(watch_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alerts_triggered ON alerts(triggered_at)
        """)

        conn.commit()
        conn.close()

    def save_watch(self, watch: Watch):
        """Save or update a watch."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO watches
            (watch_id, name, target_type, target_id, conditions, notify_webhook,
             notify_email, notify_in_app, cooldown_minutes, last_triggered,
             retention_days, created_at, created_by, enabled, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            watch.watch_id,
            watch.name,
            watch.target_type.value,
            watch.target_id,
            json.dumps([c.to_dict() for c in watch.conditions]),
            watch.notify_webhook,
            watch.notify_email,
            1 if watch.notify_in_app else 0,
            watch.cooldown_minutes,
            watch.last_triggered.isoformat() if watch.last_triggered else None,
            watch.retention_days,
            watch.created_at.isoformat(),
            watch.created_by,
            1 if watch.enabled else 0,
            watch.description
        ))

        conn.commit()
        conn.close()

        self._cache[watch.watch_id] = watch

    def get_watch(self, watch_id: str) -> Optional[Watch]:
        """Get a watch by ID."""
        if watch_id in self._cache:
            return self._cache[watch_id]

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM watches WHERE watch_id = ?", (watch_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            watch = self._row_to_watch(row)
            self._cache[watch_id] = watch
            return watch

        return None

    def get_all_watches(self, enabled_only: bool = True) -> List[Watch]:
        """Get all watches."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if enabled_only:
            cursor.execute("SELECT * FROM watches WHERE enabled = 1")
        else:
            cursor.execute("SELECT * FROM watches")

        rows = cursor.fetchall()
        conn.close()

        watches = [self._row_to_watch(row) for row in rows]
        for watch in watches:
            self._cache[watch.watch_id] = watch

        return watches

    def delete_watch(self, watch_id: str) -> bool:
        """Delete a watch."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM watches WHERE watch_id = ?", (watch_id,))
        deleted = cursor.rowcount > 0

        conn.commit()
        conn.close()

        if watch_id in self._cache:
            del self._cache[watch_id]

        return deleted

    def save_alert(self, alert: Alert):
        """Save an alert."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO alerts
            (alert_id, watch_id, alert_type, severity, status, entity_type,
             entity_id, entity_content, old_value, new_value, change_description,
             triggered_at, delivered_at, acknowledged_at, acknowledged_by, context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            alert.alert_id,
            alert.watch_id,
            alert.alert_type.value,
            alert.severity.value,
            alert.status.value,
            alert.entity_type,
            alert.entity_id,
            alert.entity_content,
            alert.old_value,
            alert.new_value,
            alert.change_description,
            alert.triggered_at.isoformat(),
            alert.delivered_at.isoformat() if alert.delivered_at else None,
            alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
            alert.acknowledged_by,
            json.dumps(alert.context)
        ))

        conn.commit()
        conn.close()

    def get_alerts(
        self,
        watch_id: Optional[str] = None,
        status: Optional[AlertStatus] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Alert]:
        """Get alerts with optional filtering."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM alerts WHERE 1=1"
        params = []

        if watch_id:
            query += " AND watch_id = ?"
            params.append(watch_id)

        if status:
            query += " AND status = ?"
            params.append(status.value)

        if since:
            query += " AND triggered_at >= ?"
            params.append(since.isoformat())

        query += " ORDER BY triggered_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_alert(row) for row in rows]

    def cleanup_old_alerts(self, default_retention_days: int = 30):
        """Remove alerts past retention period."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff = datetime.now(timezone.utc) - timedelta(days=default_retention_days)

        cursor.execute("""
            DELETE FROM alerts WHERE triggered_at < ?
        """, (cutoff.isoformat(),))

        deleted = cursor.rowcount
        conn.commit()
        conn.close()

        logger.info(f"Cleaned up {deleted} old alerts")
        return deleted

    def _row_to_watch(self, row) -> Watch:
        """Convert database row to Watch."""
        conditions = json.loads(row["conditions"]) if row["conditions"] else []
        return Watch(
            watch_id=row["watch_id"],
            name=row["name"],
            target_type=WatchTarget(row["target_type"]),
            target_id=row["target_id"],
            conditions=[AlertCondition.from_dict(c) for c in conditions],
            notify_webhook=row["notify_webhook"],
            notify_email=row["notify_email"],
            notify_in_app=bool(row["notify_in_app"]),
            cooldown_minutes=row["cooldown_minutes"],
            last_triggered=datetime.fromisoformat(row["last_triggered"]) if row["last_triggered"] else None,
            retention_days=row["retention_days"],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.now(timezone.utc),
            created_by=row["created_by"],
            enabled=bool(row["enabled"]),
            description=row["description"]
        )

    def _row_to_alert(self, row) -> Alert:
        """Convert database row to Alert."""
        return Alert(
            alert_id=row["alert_id"],
            watch_id=row["watch_id"],
            alert_type=AlertType(row["alert_type"]),
            severity=AlertSeverity(row["severity"]),
            status=AlertStatus(row["status"]),
            entity_type=row["entity_type"],
            entity_id=row["entity_id"],
            entity_content=row["entity_content"],
            old_value=row["old_value"],
            new_value=row["new_value"],
            change_description=row["change_description"],
            triggered_at=datetime.fromisoformat(row["triggered_at"]),
            delivered_at=datetime.fromisoformat(row["delivered_at"]) if row["delivered_at"] else None,
            acknowledged_at=datetime.fromisoformat(row["acknowledged_at"]) if row["acknowledged_at"] else None,
            acknowledged_by=row["acknowledged_by"],
            context=json.loads(row["context"]) if row["context"] else {}
        )


# =============================================================================
# ALERT MANAGER
# =============================================================================


class AlertManager:
    """
    Central manager for alert monitoring and delivery.

    Integrates with WebOfBelief to detect changes and trigger alerts.
    """

    def __init__(
        self,
        storage: Optional[AlertStorage] = None,
        in_app_handler: Optional[InAppNotificationHandler] = None,
        webhook_handler: Optional[WebhookNotificationHandler] = None,
        email_handler: Optional[EmailNotificationHandler] = None,
        auto_cleanup: bool = True
    ):
        """
        Initialize AlertManager.

        Panel Review (2026-02-09): Added auto_cleanup per Simon to prevent
        unbounded growth of alerts table.
        """
        self.storage = storage or AlertStorage()
        self.in_app_handler = in_app_handler or InAppNotificationHandler()
        self.webhook_handler = webhook_handler or WebhookNotificationHandler()
        self.email_handler = email_handler or EmailNotificationHandler()

        # State tracking for change detection
        self._belief_states: Dict[str, Dict[str, Any]] = {}
        self._theory_states: Dict[str, Dict[str, Any]] = {}
        self._system_state: Dict[str, Any] = {}

        # Automatic cleanup on initialization
        if auto_cleanup:
            try:
                deleted = self.storage.cleanup_old_alerts()
                if deleted > 0:
                    logger.info(f"Auto-cleanup removed {deleted} old alerts on startup")
            except Exception as e:
                logger.warning(f"Auto-cleanup failed: {e}")

    def create_watch(
        self,
        name: str,
        target_type: WatchTarget,
        target_id: Optional[str] = None,
        conditions: Optional[List[AlertCondition]] = None,
        notify_webhook: Optional[str] = None,
        notify_email: Optional[str] = None,
        notify_in_app: bool = True,
        cooldown_minutes: int = 5,
        retention_days: int = 30,
        description: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> Watch:
        """Create a new watch."""
        watch_id = f"watch_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hashlib.md5(name.encode()).hexdigest()[:6]}"

        watch = Watch(
            watch_id=watch_id,
            name=name,
            target_type=target_type,
            target_id=target_id,
            conditions=conditions or [],
            notify_webhook=notify_webhook,
            notify_email=notify_email,
            notify_in_app=notify_in_app,
            cooldown_minutes=cooldown_minutes,
            retention_days=retention_days,
            description=description,
            created_by=created_by
        )

        self.storage.save_watch(watch)
        logger.info(f"Created watch: {watch_id} ({name})")

        return watch

    def add_condition_to_watch(
        self,
        watch_id: str,
        condition: AlertCondition
    ) -> bool:
        """Add a condition to an existing watch."""
        watch = self.storage.get_watch(watch_id)
        if not watch:
            return False

        watch.conditions.append(condition)
        self.storage.save_watch(watch)
        return True

    def delete_watch(self, watch_id: str) -> bool:
        """Delete a watch."""
        return self.storage.delete_watch(watch_id)

    def enable_watch(self, watch_id: str) -> bool:
        """Enable a watch."""
        watch = self.storage.get_watch(watch_id)
        if not watch:
            return False
        watch.enabled = True
        self.storage.save_watch(watch)
        return True

    def disable_watch(self, watch_id: str) -> bool:
        """Disable a watch."""
        watch = self.storage.get_watch(watch_id)
        if not watch:
            return False
        watch.enabled = False
        self.storage.save_watch(watch)
        return True

    def get_watches(self, enabled_only: bool = True) -> List[Watch]:
        """Get all watches."""
        return self.storage.get_all_watches(enabled_only)

    def get_alerts(
        self,
        watch_id: Optional[str] = None,
        status: Optional[AlertStatus] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Alert]:
        """Get alerts with optional filtering."""
        return self.storage.get_alerts(watch_id, status, since, limit)

    def acknowledge_alert(self, alert_id: str, user: Optional[str] = None) -> bool:
        """Acknowledge an alert."""
        alerts = self.storage.get_alerts(limit=1000)  # Search through recent
        for alert in alerts:
            if alert.alert_id == alert_id:
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_at = datetime.now(timezone.utc)
                alert.acknowledged_by = user
                self.storage.save_alert(alert)
                return True
        return False

    def check_belief_change(
        self,
        belief_id: str,
        content: str,
        new_credence: float,
        new_status: str,
        theory_id: Optional[str] = None,
        level: Optional[str] = None,
        paper_ids: Optional[List[str]] = None
    ) -> List[Alert]:
        """
        Check if a belief change triggers any alerts.

        Call this after any belief modification.
        """
        alerts: List[Alert] = []
        old_state = self._belief_states.get(belief_id, {})

        # Get matching watches
        watches = self.storage.get_all_watches(enabled_only=True)
        matching_watches = [
            w for w in watches
            if w.matches_belief(belief_id, content, theory_id, level) and w.can_trigger()
        ]

        for watch in matching_watches:
            for condition in watch.conditions:
                triggered = False
                change_description = ""

                if condition.alert_type == AlertType.CREDENCE_CHANGE:
                    old_credence = old_state.get("credence")
                    triggered, change_description = condition.is_triggered(old_credence, new_credence)

                elif condition.alert_type == AlertType.STATUS_CHANGE:
                    old_status = old_state.get("status")
                    if old_status and old_status != new_status:
                        triggered = True
                        change_description = f"Status changed: {old_status} → {new_status}"

                elif condition.alert_type == AlertType.NEW_EVIDENCE:
                    old_papers = set(old_state.get("paper_ids", []))
                    new_papers = set(paper_ids or [])
                    new_evidence = new_papers - old_papers
                    if new_evidence:
                        triggered = True
                        change_description = f"New evidence added: {len(new_evidence)} paper(s)"

                if triggered:
                    alert = self._create_and_deliver_alert(
                        watch=watch,
                        condition=condition,
                        entity_type="belief",
                        entity_id=belief_id,
                        entity_content=content[:200],
                        old_value=old_state.get("credence"),
                        new_value=new_credence,
                        change_description=change_description
                    )
                    alerts.append(alert)

        # Update state
        self._belief_states[belief_id] = {
            "credence": new_credence,
            "status": new_status,
            "theory_id": theory_id,
            "level": level,
            "paper_ids": paper_ids or [],
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        return alerts

    def check_theory_change(
        self,
        theory_id: str,
        average_credence: float,
        belief_count: int,
        contested_count: int
    ) -> List[Alert]:
        """
        Check if a theory-level change triggers alerts.
        """
        alerts: List[Alert] = []
        old_state = self._theory_states.get(theory_id, {})

        watches = self.storage.get_all_watches(enabled_only=True)
        matching_watches = [
            w for w in watches
            if w.target_type == WatchTarget.THEORY and w.target_id == theory_id and w.can_trigger()
        ]

        for watch in matching_watches:
            for condition in watch.conditions:
                triggered = False
                change_description = ""

                if condition.alert_type == AlertType.THEORY_SHIFT:
                    old_credence = old_state.get("average_credence")
                    triggered, change_description = condition.is_triggered(old_credence, average_credence)

                elif condition.alert_type == AlertType.THEORY_CONTESTED:
                    old_contested = old_state.get("contested_count", 0)
                    if contested_count > old_contested:
                        triggered = True
                        change_description = f"Contested beliefs increased: {old_contested} → {contested_count}"

                if triggered:
                    alert = self._create_and_deliver_alert(
                        watch=watch,
                        condition=condition,
                        entity_type="theory",
                        entity_id=theory_id,
                        entity_content=f"Theory: {theory_id}",
                        old_value=old_state.get("average_credence"),
                        new_value=average_credence,
                        change_description=change_description
                    )
                    alerts.append(alert)

        # Update state
        self._theory_states[theory_id] = {
            "average_credence": average_credence,
            "belief_count": belief_count,
            "contested_count": contested_count,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        return alerts

    def check_system_coherence(self, coherence: float) -> List[Alert]:
        """
        Check if system coherence triggers alerts.
        """
        alerts: List[Alert] = []
        old_coherence = self._system_state.get("coherence")

        watches = self.storage.get_all_watches(enabled_only=True)
        system_watches = [
            w for w in watches
            if w.target_type == WatchTarget.SYSTEM and w.can_trigger()
        ]

        for watch in system_watches:
            for condition in watch.conditions:
                if condition.alert_type == AlertType.COHERENCE_DROP:
                    triggered, change_description = condition.is_triggered(old_coherence, coherence)
                    if triggered:
                        alert = self._create_and_deliver_alert(
                            watch=watch,
                            condition=condition,
                            entity_type="system",
                            entity_id="coherence",
                            entity_content="System coherence",
                            old_value=old_coherence,
                            new_value=coherence,
                            change_description=change_description
                        )
                        alerts.append(alert)

        self._system_state["coherence"] = coherence
        return alerts

    def _create_and_deliver_alert(
        self,
        watch: Watch,
        condition: AlertCondition,
        entity_type: str,
        entity_id: Optional[str],
        entity_content: Optional[str],
        old_value: Optional[float],
        new_value: Optional[float],
        change_description: str
    ) -> Alert:
        """Create an alert and deliver through configured channels."""
        alert_id = f"alert_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

        # Determine severity
        severity = AlertSeverity.INFO
        if condition.alert_type in [AlertType.COHERENCE_DROP, AlertType.THEORY_CONTESTED]:
            severity = AlertSeverity.WARNING
        if old_value is not None and new_value is not None:
            change = abs(new_value - old_value)
            if change >= 0.3:
                severity = AlertSeverity.CRITICAL
            elif change >= 0.15:
                severity = AlertSeverity.WARNING

        alert = Alert(
            alert_id=alert_id,
            watch_id=watch.watch_id,
            alert_type=condition.alert_type,
            severity=severity,
            status=AlertStatus.PENDING,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_content=entity_content,
            old_value=old_value,
            new_value=new_value,
            change_description=change_description,
            context={
                "watch_name": watch.name,
                "condition": condition.to_dict()
            }
        )

        # Save alert
        self.storage.save_alert(alert)

        # Update watch last_triggered
        watch.last_triggered = datetime.now(timezone.utc)
        self.storage.save_watch(watch)

        # Deliver notifications
        delivered = False

        if watch.notify_in_app:
            if self.in_app_handler.send(alert, watch):
                delivered = True

        if watch.notify_webhook:
            if self.webhook_handler.send(alert, watch):
                delivered = True

        if watch.notify_email:
            if self.email_handler.send(alert, watch):
                delivered = True

        if delivered:
            alert.status = AlertStatus.DELIVERED
            alert.delivered_at = datetime.now(timezone.utc)
            self.storage.save_alert(alert)

        logger.info(f"Alert triggered: {alert_id} ({condition.alert_type.value})")
        return alert

    def generate_digest(
        self,
        since: Optional[datetime] = None,
        watch_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a digest of alerts.

        Useful for periodic email summaries.
        """
        if since is None:
            since = datetime.now(timezone.utc) - timedelta(days=1)

        alerts = self.storage.get_alerts(since=since, limit=500)

        if watch_ids:
            alerts = [a for a in alerts if a.watch_id in watch_ids]

        # Group by severity
        by_severity = defaultdict(list)
        for alert in alerts:
            by_severity[alert.severity.value].append(alert.to_dict())

        # Group by type
        by_type = defaultdict(list)
        for alert in alerts:
            by_type[alert.alert_type.value].append(alert.to_dict())

        # Summary stats
        summary = {
            "total_alerts": len(alerts),
            "by_severity": {
                "critical": len(by_severity["critical"]),
                "warning": len(by_severity["warning"]),
                "info": len(by_severity["info"])
            },
            "by_status": {
                "pending": sum(1 for a in alerts if a.status == AlertStatus.PENDING),
                "delivered": sum(1 for a in alerts if a.status == AlertStatus.DELIVERED),
                "acknowledged": sum(1 for a in alerts if a.status == AlertStatus.ACKNOWLEDGED)
            },
            "period": {
                "start": since.isoformat(),
                "end": datetime.now(timezone.utc).isoformat()
            }
        }

        return {
            "summary": summary,
            "by_severity": dict(by_severity),
            "by_type": dict(by_type),
            "all_alerts": [a.to_dict() for a in alerts]
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


_manager: Optional[AlertManager] = None


def get_alert_manager() -> AlertManager:
    """Get or create the alert manager singleton."""
    global _manager
    if _manager is None:
        _manager = AlertManager()
    return _manager


def create_credence_watch(
    name: str,
    belief_id: str,
    threshold: float = 0.1,
    direction: str = "any",
    notify_in_app: bool = True
) -> Watch:
    """Convenience function to create a credence change watch."""
    manager = get_alert_manager()
    return manager.create_watch(
        name=name,
        target_type=WatchTarget.BELIEF,
        target_id=belief_id,
        conditions=[
            AlertCondition(
                alert_type=AlertType.CREDENCE_CHANGE,
                threshold_absolute=threshold,
                direction=direction
            )
        ],
        notify_in_app=notify_in_app
    )


def create_theory_watch(
    name: str,
    theory_id: str,
    threshold: float = 0.1,
    notify_in_app: bool = True
) -> Watch:
    """Convenience function to create a theory-level watch."""
    manager = get_alert_manager()
    return manager.create_watch(
        name=name,
        target_type=WatchTarget.THEORY,
        target_id=theory_id,
        conditions=[
            AlertCondition(
                alert_type=AlertType.THEORY_SHIFT,
                threshold_absolute=threshold
            ),
            AlertCondition(
                alert_type=AlertType.THEORY_CONTESTED
            )
        ],
        notify_in_app=notify_in_app
    )


def create_topic_watch(
    name: str,
    pattern: str,
    threshold: float = 0.15,
    notify_in_app: bool = True
) -> Watch:
    """Convenience function to create a topic pattern watch."""
    manager = get_alert_manager()
    return manager.create_watch(
        name=name,
        target_type=WatchTarget.TOPIC,
        target_id=pattern,
        conditions=[
            AlertCondition(
                alert_type=AlertType.CREDENCE_CHANGE,
                threshold_absolute=threshold
            ),
            AlertCondition(
                alert_type=AlertType.NEW_EVIDENCE
            )
        ],
        notify_in_app=notify_in_app
    )


def create_system_coherence_watch(
    name: str = "System Coherence Monitor",
    threshold: float = 0.1,
    direction: str = "decrease",
    notify_in_app: bool = True
) -> Watch:
    """Convenience function to create a system coherence watch."""
    manager = get_alert_manager()
    return manager.create_watch(
        name=name,
        target_type=WatchTarget.SYSTEM,
        target_id="coherence",
        conditions=[
            AlertCondition(
                alert_type=AlertType.COHERENCE_DROP,
                threshold_absolute=threshold,
                direction=direction
            )
        ],
        notify_in_app=notify_in_app
    )


# =============================================================================
# SENSITIVITY PRESETS (Panel Recommendation D5)
# =============================================================================


class AlertSensitivity(Enum):
    """
    Preset sensitivity levels for alert thresholds.

    Panel Review (2026-02-09): Added per Kahneman to reduce threshold
    tuning paralysis. Users can select LOW/MEDIUM/HIGH instead of
    choosing between 0.1 and 0.15.
    """
    LOW = "low"        # Conservative: fewer alerts, only major changes
    MEDIUM = "medium"  # Balanced: reasonable coverage
    HIGH = "high"      # Aggressive: catch smaller changes


# Threshold mappings for sensitivity levels
SENSITIVITY_THRESHOLDS = {
    AlertSensitivity.LOW: {
        "absolute": 0.2,
        "percentage": 40.0
    },
    AlertSensitivity.MEDIUM: {
        "absolute": 0.1,
        "percentage": 20.0
    },
    AlertSensitivity.HIGH: {
        "absolute": 0.05,
        "percentage": 10.0
    }
}


def create_credence_watch_with_sensitivity(
    name: str,
    belief_id: str,
    sensitivity: AlertSensitivity = AlertSensitivity.MEDIUM,
    direction: str = "any",
    notify_in_app: bool = True
) -> Watch:
    """
    Create a credence change watch using preset sensitivity levels.

    Panel Review (2026-02-09): Convenience function using sensitivity
    presets instead of raw thresholds.

    Args:
        name: Watch name
        belief_id: The belief to monitor
        sensitivity: LOW, MEDIUM, or HIGH
        direction: "increase", "decrease", or "any"
        notify_in_app: Whether to add to in-app queue
    """
    thresholds = SENSITIVITY_THRESHOLDS[sensitivity]
    manager = get_alert_manager()
    return manager.create_watch(
        name=name,
        target_type=WatchTarget.BELIEF,
        target_id=belief_id,
        conditions=[
            AlertCondition(
                alert_type=AlertType.CREDENCE_CHANGE,
                threshold_absolute=thresholds["absolute"],
                threshold_percentage=thresholds["percentage"],
                direction=direction
            )
        ],
        notify_in_app=notify_in_app,
        description=f"Sensitivity: {sensitivity.value}"
    )


def create_topic_watch_with_sensitivity(
    name: str,
    pattern: str,
    sensitivity: AlertSensitivity = AlertSensitivity.MEDIUM,
    notify_in_app: bool = True
) -> Watch:
    """
    Create a topic pattern watch using preset sensitivity levels.

    Args:
        name: Watch name
        pattern: Regex pattern to match belief content
        sensitivity: LOW, MEDIUM, or HIGH
        notify_in_app: Whether to add to in-app queue
    """
    thresholds = SENSITIVITY_THRESHOLDS[sensitivity]
    manager = get_alert_manager()
    return manager.create_watch(
        name=name,
        target_type=WatchTarget.TOPIC,
        target_id=pattern,
        conditions=[
            AlertCondition(
                alert_type=AlertType.CREDENCE_CHANGE,
                threshold_absolute=thresholds["absolute"],
                threshold_percentage=thresholds["percentage"]
            ),
            AlertCondition(
                alert_type=AlertType.NEW_EVIDENCE
            )
        ],
        notify_in_app=notify_in_app,
        description=f"Topic: {pattern}, Sensitivity: {sensitivity.value}"
    )


def create_theory_watch_with_sensitivity(
    name: str,
    theory_id: str,
    sensitivity: AlertSensitivity = AlertSensitivity.MEDIUM,
    notify_in_app: bool = True
) -> Watch:
    """
    Create a theory-level watch using preset sensitivity levels.

    Args:
        name: Watch name
        theory_id: The theory to monitor
        sensitivity: LOW, MEDIUM, or HIGH
        notify_in_app: Whether to add to in-app queue
    """
    thresholds = SENSITIVITY_THRESHOLDS[sensitivity]
    manager = get_alert_manager()
    return manager.create_watch(
        name=name,
        target_type=WatchTarget.THEORY,
        target_id=theory_id,
        conditions=[
            AlertCondition(
                alert_type=AlertType.THEORY_SHIFT,
                threshold_absolute=thresholds["absolute"],
                threshold_percentage=thresholds["percentage"]
            ),
            AlertCondition(
                alert_type=AlertType.THEORY_CONTESTED
            )
        ],
        notify_in_app=notify_in_app,
        description=f"Theory: {theory_id}, Sensitivity: {sensitivity.value}"
    )
