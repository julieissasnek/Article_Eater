"""
Tests for Query Alerts and Monitoring System.

Sprint 3.0.2-G — 2026-02-09

Comprehensive tests covering:
- AlertCondition threshold logic
- Watch matching and cooldown
- Alert creation and delivery
- AlertStorage SQLite operations
- AlertManager orchestration
- Convenience functions
"""

import json
import os
import tempfile
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.services.query_alerts import (
    Alert,
    AlertCondition,
    AlertManager,
    AlertSensitivity,
    AlertSeverity,
    AlertStatus,
    AlertStorage,
    AlertType,
    EmailNotificationHandler,
    InAppNotificationHandler,
    SENSITIVITY_THRESHOLDS,
    Watch,
    WatchTarget,
    WebhookNotificationHandler,
    create_credence_watch,
    create_credence_watch_with_sensitivity,
    create_system_coherence_watch,
    create_theory_watch,
    create_theory_watch_with_sensitivity,
    create_topic_watch,
    create_topic_watch_with_sensitivity,
    get_alert_manager,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def temp_db_path():
    """Create a temporary database file."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        yield f.name
    # Cleanup
    try:
        os.unlink(f.name)
    except FileNotFoundError:
        pass


@pytest.fixture
def storage(temp_db_path):
    """Create AlertStorage with temp database."""
    return AlertStorage(db_path=temp_db_path)


@pytest.fixture
def in_app_handler():
    """Create InAppNotificationHandler."""
    return InAppNotificationHandler()


@pytest.fixture
def manager(temp_db_path, in_app_handler):
    """Create AlertManager with temp database."""
    storage = AlertStorage(db_path=temp_db_path)
    return AlertManager(
        storage=storage,
        in_app_handler=in_app_handler
    )


# =============================================================================
# ALERT CONDITION TESTS
# =============================================================================


class TestAlertCondition:
    """Tests for AlertCondition threshold logic."""

    def test_credence_change_absolute_threshold(self):
        """Test absolute threshold triggering."""
        condition = AlertCondition(
            alert_type=AlertType.CREDENCE_CHANGE,
            threshold_absolute=0.1
        )

        # Should not trigger - change too small
        triggered, reason = condition.is_triggered(0.5, 0.55)
        assert not triggered

        # Should trigger - change meets threshold
        triggered, reason = condition.is_triggered(0.5, 0.65)
        assert triggered
        assert "absolute change" in reason
        assert "0.150" in reason

    def test_credence_change_percentage_threshold(self):
        """Test percentage threshold triggering."""
        condition = AlertCondition(
            alert_type=AlertType.CREDENCE_CHANGE,
            threshold_percentage=20.0
        )

        # Should not trigger - percentage too small
        triggered, reason = condition.is_triggered(0.5, 0.55)
        assert not triggered

        # Should trigger - 30% change
        triggered, reason = condition.is_triggered(0.5, 0.65)
        assert triggered
        assert "percentage change" in reason

    def test_direction_increase_only(self):
        """Test direction filtering for increases only."""
        condition = AlertCondition(
            alert_type=AlertType.CREDENCE_CHANGE,
            threshold_absolute=0.1,
            direction="increase"
        )

        # Should trigger - increase exceeds threshold
        triggered, reason = condition.is_triggered(0.5, 0.7)
        assert triggered

        # Should not trigger - decrease
        triggered, reason = condition.is_triggered(0.5, 0.3)
        assert not triggered
        assert "not in specified direction" in reason

    def test_direction_decrease_only(self):
        """Test direction filtering for decreases only."""
        condition = AlertCondition(
            alert_type=AlertType.CREDENCE_CHANGE,
            threshold_absolute=0.1,
            direction="decrease"
        )

        # Should trigger - decrease exceeds threshold
        triggered, reason = condition.is_triggered(0.5, 0.3)
        assert triggered

        # Should not trigger - increase
        triggered, reason = condition.is_triggered(0.5, 0.7)
        assert not triggered

    def test_min_credence_bound(self):
        """Test min_credence filtering."""
        condition = AlertCondition(
            alert_type=AlertType.CREDENCE_CHANGE,
            threshold_absolute=0.1,
            min_credence=0.3
        )

        # Should trigger - new value above min
        triggered, reason = condition.is_triggered(0.3, 0.5)
        assert triggered

        # Should not trigger - new value below min
        triggered, reason = condition.is_triggered(0.3, 0.2)
        assert not triggered
        assert "below min_credence" in reason

    def test_max_credence_bound(self):
        """Test max_credence filtering."""
        condition = AlertCondition(
            alert_type=AlertType.CREDENCE_CHANGE,
            threshold_absolute=0.1,
            max_credence=0.7
        )

        # Should trigger - new value below max
        triggered, reason = condition.is_triggered(0.3, 0.5)
        assert triggered

        # Should not trigger - new value above max
        triggered, reason = condition.is_triggered(0.5, 0.8)
        assert not triggered
        assert "above max_credence" in reason

    def test_status_change_always_triggers(self):
        """Test that status changes always trigger (no threshold)."""
        condition = AlertCondition(
            alert_type=AlertType.STATUS_CHANGE
        )

        triggered, reason = condition.is_triggered(None, 1.0)
        assert triggered
        assert "status_change detected" in reason

    def test_new_evidence_always_triggers(self):
        """Test that new evidence always triggers."""
        condition = AlertCondition(
            alert_type=AlertType.NEW_EVIDENCE
        )

        triggered, reason = condition.is_triggered(None, 1.0)
        assert triggered
        assert "new_evidence detected" in reason

    def test_constraint_added_always_triggers(self):
        """Test that constraint_added always triggers."""
        condition = AlertCondition(
            alert_type=AlertType.CONSTRAINT_ADDED
        )

        triggered, reason = condition.is_triggered(None, 1.0)
        assert triggered

    def test_no_previous_value(self):
        """Test behavior when no previous value exists."""
        condition = AlertCondition(
            alert_type=AlertType.CREDENCE_CHANGE,
            threshold_absolute=0.1
        )

        # Without old value, cannot detect change
        triggered, reason = condition.is_triggered(None, 0.5)
        assert not triggered
        assert "No previous value" in reason

    def test_to_dict_and_from_dict(self):
        """Test serialization round-trip."""
        condition = AlertCondition(
            alert_type=AlertType.CREDENCE_CHANGE,
            threshold_absolute=0.15,
            threshold_percentage=10.0,
            direction="increase",
            min_credence=0.2,
            max_credence=0.9
        )

        data = condition.to_dict()
        restored = AlertCondition.from_dict(data)

        assert restored.alert_type == condition.alert_type
        assert restored.threshold_absolute == condition.threshold_absolute
        assert restored.threshold_percentage == condition.threshold_percentage
        assert restored.direction == condition.direction
        assert restored.min_credence == condition.min_credence
        assert restored.max_credence == condition.max_credence

    def test_both_thresholds_or_logic(self):
        """Test that meeting either threshold triggers (OR logic)."""
        condition = AlertCondition(
            alert_type=AlertType.CREDENCE_CHANGE,
            threshold_absolute=0.2,
            threshold_percentage=10.0
        )

        # Meets percentage but not absolute (15% change, 0.075 absolute)
        triggered, reason = condition.is_triggered(0.5, 0.575)
        assert triggered
        assert "percentage change" in reason


# =============================================================================
# WATCH TESTS
# =============================================================================


class TestWatch:
    """Tests for Watch matching and cooldown."""

    def test_matches_belief_by_id(self):
        """Test belief matching by ID."""
        watch = Watch(
            watch_id="test_watch",
            name="Test Watch",
            target_type=WatchTarget.BELIEF,
            target_id="belief_123"
        )

        assert watch.matches_belief("belief_123", "Some content", "theory_1", "EMPIRICAL")
        assert not watch.matches_belief("belief_456", "Some content", "theory_1", "EMPIRICAL")

    def test_matches_belief_by_theory(self):
        """Test belief matching by theory ID."""
        watch = Watch(
            watch_id="test_watch",
            name="Test Watch",
            target_type=WatchTarget.THEORY,
            target_id="theory_ART"
        )

        assert watch.matches_belief("belief_123", "Some content", "theory_ART", "EMPIRICAL")
        assert not watch.matches_belief("belief_123", "Some content", "theory_SRT", "EMPIRICAL")

    def test_matches_belief_by_topic_pattern(self):
        """Test belief matching by topic regex pattern."""
        watch = Watch(
            watch_id="test_watch",
            name="Test Watch",
            target_type=WatchTarget.TOPIC,
            target_id=r"stress|anxiety"
        )

        assert watch.matches_belief("b1", "Reduces stress in office workers", None, None)
        assert watch.matches_belief("b2", "Decreases anxiety levels", None, None)
        assert not watch.matches_belief("b3", "Improves productivity", None, None)

    def test_matches_belief_by_level(self):
        """Test belief matching by epistemic level."""
        watch = Watch(
            watch_id="test_watch",
            name="Test Watch",
            target_type=WatchTarget.LEVEL,
            target_id="THEORETICAL"
        )

        assert watch.matches_belief("b1", "Theory content", None, "THEORETICAL")
        assert not watch.matches_belief("b2", "Empirical content", None, "EMPIRICAL")

    def test_matches_system_watch(self):
        """Test system watches match everything."""
        watch = Watch(
            watch_id="test_watch",
            name="System Watch",
            target_type=WatchTarget.SYSTEM,
            target_id="coherence"
        )

        assert watch.matches_belief("any_belief", "any content", "any_theory", "any_level")

    def test_cooldown_can_trigger(self):
        """Test cooldown respects timing."""
        watch = Watch(
            watch_id="test_watch",
            name="Test Watch",
            target_type=WatchTarget.BELIEF,
            target_id="b1",
            cooldown_minutes=5
        )

        # No previous trigger
        assert watch.can_trigger()

        # Just triggered
        watch.last_triggered = datetime.now(timezone.utc)
        assert not watch.can_trigger()

        # Triggered 6 minutes ago
        watch.last_triggered = datetime.now(timezone.utc) - timedelta(minutes=6)
        assert watch.can_trigger()

    def test_disabled_watch_cannot_trigger(self):
        """Test disabled watches cannot trigger."""
        watch = Watch(
            watch_id="test_watch",
            name="Test Watch",
            target_type=WatchTarget.BELIEF,
            target_id="b1",
            enabled=False
        )

        assert not watch.can_trigger()

    def test_invalid_regex_pattern(self):
        """Test invalid regex pattern handled gracefully."""
        watch = Watch(
            watch_id="test_watch",
            name="Test Watch",
            target_type=WatchTarget.TOPIC,
            target_id=r"[invalid(regex"  # Invalid regex
        )

        # Should not match and not raise exception
        assert not watch.matches_belief("b1", "test content", None, None)

    def test_to_dict_and_from_dict(self):
        """Test Watch serialization round-trip."""
        condition = AlertCondition(
            alert_type=AlertType.CREDENCE_CHANGE,
            threshold_absolute=0.1
        )

        watch = Watch(
            watch_id="test_watch",
            name="Test Watch",
            target_type=WatchTarget.BELIEF,
            target_id="belief_123",
            conditions=[condition],
            notify_webhook="http://example.com/webhook",
            notify_email="test@example.com",
            notify_in_app=True,
            cooldown_minutes=10,
            retention_days=60,
            description="A test watch"
        )

        data = watch.to_dict()
        restored = Watch.from_dict(data)

        assert restored.watch_id == watch.watch_id
        assert restored.name == watch.name
        assert restored.target_type == watch.target_type
        assert restored.target_id == watch.target_id
        assert len(restored.conditions) == 1
        assert restored.notify_webhook == watch.notify_webhook
        assert restored.cooldown_minutes == watch.cooldown_minutes


# =============================================================================
# ALERT TESTS
# =============================================================================


class TestAlert:
    """Tests for Alert dataclass."""

    def test_alert_creation(self):
        """Test creating an alert."""
        alert = Alert(
            alert_id="alert_123",
            watch_id="watch_456",
            alert_type=AlertType.CREDENCE_CHANGE,
            severity=AlertSeverity.WARNING,
            status=AlertStatus.PENDING,
            entity_type="belief",
            entity_id="belief_789",
            entity_content="Some belief content",
            old_value=0.5,
            new_value=0.8,
            change_description="Credence increased by 0.3"
        )

        assert alert.alert_id == "alert_123"
        assert alert.severity == AlertSeverity.WARNING
        assert alert.status == AlertStatus.PENDING

    def test_to_dict_and_from_dict(self):
        """Test Alert serialization round-trip."""
        alert = Alert(
            alert_id="alert_123",
            watch_id="watch_456",
            alert_type=AlertType.STATUS_CHANGE,
            severity=AlertSeverity.CRITICAL,
            status=AlertStatus.DELIVERED,
            entity_type="theory",
            entity_id="theory_ART",
            entity_content=None,
            old_value=None,
            new_value=None,
            change_description="Status changed",
            context={"extra": "info"}
        )
        alert.delivered_at = datetime.now(timezone.utc)

        data = alert.to_dict()
        restored = Alert.from_dict(data)

        assert restored.alert_id == alert.alert_id
        assert restored.alert_type == alert.alert_type
        assert restored.severity == alert.severity
        assert restored.context == {"extra": "info"}


# =============================================================================
# NOTIFICATION HANDLER TESTS
# =============================================================================


class TestInAppNotificationHandler:
    """Tests for in-app notification handler."""

    def test_send_adds_to_queue(self, in_app_handler):
        """Test that send adds alert to queue."""
        alert = Alert(
            alert_id="alert_1",
            watch_id="watch_1",
            alert_type=AlertType.CREDENCE_CHANGE,
            severity=AlertSeverity.INFO,
            status=AlertStatus.PENDING,
            entity_type="belief",
            entity_id="b1",
            entity_content="Content",
            old_value=0.5,
            new_value=0.6,
            change_description="Changed"
        )
        watch = Watch(
            watch_id="watch_1",
            name="Test",
            target_type=WatchTarget.BELIEF
        )

        result = in_app_handler.send(alert, watch)

        assert result is True
        assert len(in_app_handler.notifications) == 1

    def test_get_pending(self, in_app_handler):
        """Test getting pending notifications."""
        for i in range(3):
            alert = Alert(
                alert_id=f"alert_{i}",
                watch_id="watch_1",
                alert_type=AlertType.CREDENCE_CHANGE,
                severity=AlertSeverity.INFO,
                status=AlertStatus.PENDING if i < 2 else AlertStatus.ACKNOWLEDGED,
                entity_type="belief",
                entity_id="b1",
                entity_content="Content",
                old_value=0.5,
                new_value=0.6,
                change_description="Changed"
            )
            in_app_handler.notifications.append(alert)

        pending = in_app_handler.get_pending()

        assert len(pending) == 2

    def test_acknowledge(self, in_app_handler):
        """Test acknowledging notifications."""
        alert = Alert(
            alert_id="alert_1",
            watch_id="watch_1",
            alert_type=AlertType.CREDENCE_CHANGE,
            severity=AlertSeverity.INFO,
            status=AlertStatus.PENDING,
            entity_type="belief",
            entity_id="b1",
            entity_content="Content",
            old_value=0.5,
            new_value=0.6,
            change_description="Changed"
        )
        in_app_handler.notifications.append(alert)

        result = in_app_handler.acknowledge("alert_1", user="david")

        assert result is True
        assert alert.status == AlertStatus.ACKNOWLEDGED
        assert alert.acknowledged_by == "david"

    def test_thread_safety(self, in_app_handler):
        """Test thread safety of in-app handler."""
        def add_notifications():
            for i in range(100):
                alert = Alert(
                    alert_id=f"alert_{threading.current_thread().name}_{i}",
                    watch_id="watch_1",
                    alert_type=AlertType.CREDENCE_CHANGE,
                    severity=AlertSeverity.INFO,
                    status=AlertStatus.PENDING,
                    entity_type="belief",
                    entity_id="b1",
                    entity_content="Content",
                    old_value=0.5,
                    new_value=0.6,
                    change_description="Changed"
                )
                watch = Watch(
                    watch_id="watch_1",
                    name="Test",
                    target_type=WatchTarget.BELIEF
                )
                in_app_handler.send(alert, watch)

        threads = [threading.Thread(target=add_notifications) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(in_app_handler.notifications) == 500


class TestWebhookNotificationHandler:
    """Tests for webhook notification handler."""

    def test_send_without_webhook(self):
        """Test that send returns False if no webhook configured."""
        handler = WebhookNotificationHandler()
        alert = Alert(
            alert_id="alert_1",
            watch_id="watch_1",
            alert_type=AlertType.CREDENCE_CHANGE,
            severity=AlertSeverity.INFO,
            status=AlertStatus.PENDING,
            entity_type="belief",
            entity_id="b1",
            entity_content="Content",
            old_value=0.5,
            new_value=0.6,
            change_description="Changed"
        )
        watch = Watch(
            watch_id="watch_1",
            name="Test",
            target_type=WatchTarget.BELIEF,
            notify_webhook=None
        )

        result = handler.send(alert, watch)

        assert result is False

    @patch("urllib.request.urlopen")
    def test_send_with_webhook_success(self, mock_urlopen):
        """Test successful webhook delivery."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        handler = WebhookNotificationHandler()
        alert = Alert(
            alert_id="alert_1",
            watch_id="watch_1",
            alert_type=AlertType.CREDENCE_CHANGE,
            severity=AlertSeverity.INFO,
            status=AlertStatus.PENDING,
            entity_type="belief",
            entity_id="b1",
            entity_content="Content",
            old_value=0.5,
            new_value=0.6,
            change_description="Changed"
        )
        watch = Watch(
            watch_id="watch_1",
            name="Test",
            target_type=WatchTarget.BELIEF,
            notify_webhook="http://example.com/hook"
        )

        result = handler.send(alert, watch)

        assert result is True
        mock_urlopen.assert_called_once()

    @patch("urllib.request.urlopen")
    def test_send_with_webhook_failure(self, mock_urlopen):
        """Test webhook delivery failure handling."""
        mock_urlopen.side_effect = Exception("Connection refused")

        handler = WebhookNotificationHandler()
        alert = Alert(
            alert_id="alert_1",
            watch_id="watch_1",
            alert_type=AlertType.CREDENCE_CHANGE,
            severity=AlertSeverity.INFO,
            status=AlertStatus.PENDING,
            entity_type="belief",
            entity_id="b1",
            entity_content="Content",
            old_value=0.5,
            new_value=0.6,
            change_description="Changed"
        )
        watch = Watch(
            watch_id="watch_1",
            name="Test",
            target_type=WatchTarget.BELIEF,
            notify_webhook="http://example.com/hook"
        )

        result = handler.send(alert, watch)

        assert result is False


class TestEmailNotificationHandler:
    """Tests for email notification handler (placeholder)."""

    def test_send_without_email(self):
        """Test that send returns False if no email configured."""
        handler = EmailNotificationHandler()
        alert = Alert(
            alert_id="alert_1",
            watch_id="watch_1",
            alert_type=AlertType.CREDENCE_CHANGE,
            severity=AlertSeverity.INFO,
            status=AlertStatus.PENDING,
            entity_type="belief",
            entity_id="b1",
            entity_content="Content",
            old_value=0.5,
            new_value=0.6,
            change_description="Changed"
        )
        watch = Watch(
            watch_id="watch_1",
            name="Test",
            target_type=WatchTarget.BELIEF,
            notify_email=None
        )

        result = handler.send(alert, watch)

        assert result is False

    def test_send_with_email(self):
        """Test email placeholder (always succeeds if email set)."""
        handler = EmailNotificationHandler()
        alert = Alert(
            alert_id="alert_1",
            watch_id="watch_1",
            alert_type=AlertType.CREDENCE_CHANGE,
            severity=AlertSeverity.INFO,
            status=AlertStatus.PENDING,
            entity_type="belief",
            entity_id="b1",
            entity_content="Content",
            old_value=0.5,
            new_value=0.6,
            change_description="Changed"
        )
        watch = Watch(
            watch_id="watch_1",
            name="Test",
            target_type=WatchTarget.BELIEF,
            notify_email="test@example.com"
        )

        result = handler.send(alert, watch)

        assert result is True


# =============================================================================
# ALERT STORAGE TESTS
# =============================================================================


class TestAlertStorage:
    """Tests for SQLite-based alert storage."""

    def test_init_creates_tables(self, storage):
        """Test that initialization creates required tables."""
        import sqlite3
        conn = sqlite3.connect(storage.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}

        assert "watches" in tables
        assert "alerts" in tables
        conn.close()

    def test_save_and_get_watch(self, storage):
        """Test saving and retrieving a watch."""
        watch = Watch(
            watch_id="test_watch_1",
            name="Test Watch",
            target_type=WatchTarget.BELIEF,
            target_id="belief_123",
            conditions=[
                AlertCondition(
                    alert_type=AlertType.CREDENCE_CHANGE,
                    threshold_absolute=0.1
                )
            ],
            cooldown_minutes=10
        )

        storage.save_watch(watch)
        retrieved = storage.get_watch("test_watch_1")

        assert retrieved is not None
        assert retrieved.name == "Test Watch"
        assert retrieved.target_id == "belief_123"
        assert len(retrieved.conditions) == 1

    def test_get_all_watches(self, storage):
        """Test getting all watches."""
        for i in range(3):
            watch = Watch(
                watch_id=f"watch_{i}",
                name=f"Watch {i}",
                target_type=WatchTarget.BELIEF,
                target_id=f"belief_{i}",
                enabled=i < 2  # Third watch is disabled
            )
            storage.save_watch(watch)

        all_watches = storage.get_all_watches(enabled_only=False)
        enabled_watches = storage.get_all_watches(enabled_only=True)

        assert len(all_watches) == 3
        assert len(enabled_watches) == 2

    def test_delete_watch(self, storage):
        """Test deleting a watch."""
        watch = Watch(
            watch_id="to_delete",
            name="To Delete",
            target_type=WatchTarget.BELIEF
        )
        storage.save_watch(watch)

        assert storage.get_watch("to_delete") is not None

        result = storage.delete_watch("to_delete")

        assert result is True
        assert storage.get_watch("to_delete") is None

    def test_save_and_get_alerts(self, storage):
        """Test saving and retrieving alerts."""
        alert = Alert(
            alert_id="alert_1",
            watch_id="watch_1",
            alert_type=AlertType.CREDENCE_CHANGE,
            severity=AlertSeverity.WARNING,
            status=AlertStatus.PENDING,
            entity_type="belief",
            entity_id="b1",
            entity_content="Some content",
            old_value=0.5,
            new_value=0.8,
            change_description="Credence increased"
        )

        storage.save_alert(alert)
        alerts = storage.get_alerts(limit=10)

        assert len(alerts) == 1
        assert alerts[0].alert_id == "alert_1"
        assert alerts[0].severity == AlertSeverity.WARNING

    def test_get_alerts_with_filters(self, storage):
        """Test alert filtering."""
        # Create alerts with different statuses
        for i, status in enumerate([AlertStatus.PENDING, AlertStatus.DELIVERED, AlertStatus.PENDING]):
            alert = Alert(
                alert_id=f"alert_{i}",
                watch_id="watch_1",
                alert_type=AlertType.CREDENCE_CHANGE,
                severity=AlertSeverity.INFO,
                status=status,
                entity_type="belief",
                entity_id="b1",
                entity_content="Content",
                old_value=0.5,
                new_value=0.6,
                change_description="Changed"
            )
            storage.save_alert(alert)

        pending_alerts = storage.get_alerts(status=AlertStatus.PENDING)

        assert len(pending_alerts) == 2

    def test_get_alerts_since_datetime(self, storage):
        """Test alerts filtered by datetime."""
        now = datetime.now(timezone.utc)

        # Old alert
        old_alert = Alert(
            alert_id="old_alert",
            watch_id="watch_1",
            alert_type=AlertType.CREDENCE_CHANGE,
            severity=AlertSeverity.INFO,
            status=AlertStatus.PENDING,
            entity_type="belief",
            entity_id="b1",
            entity_content="Content",
            old_value=0.5,
            new_value=0.6,
            change_description="Changed",
            triggered_at=now - timedelta(days=2)
        )
        storage.save_alert(old_alert)

        # Recent alert
        recent_alert = Alert(
            alert_id="recent_alert",
            watch_id="watch_1",
            alert_type=AlertType.CREDENCE_CHANGE,
            severity=AlertSeverity.INFO,
            status=AlertStatus.PENDING,
            entity_type="belief",
            entity_id="b1",
            entity_content="Content",
            old_value=0.5,
            new_value=0.6,
            change_description="Changed",
            triggered_at=now
        )
        storage.save_alert(recent_alert)

        since = now - timedelta(days=1)
        recent_alerts = storage.get_alerts(since=since)

        assert len(recent_alerts) == 1
        assert recent_alerts[0].alert_id == "recent_alert"

    def test_cleanup_old_alerts(self, storage):
        """Test cleaning up old alerts."""
        now = datetime.now(timezone.utc)

        # Create old and new alerts
        for i, age_days in enumerate([40, 35, 10, 5]):
            alert = Alert(
                alert_id=f"alert_{i}",
                watch_id="watch_1",
                alert_type=AlertType.CREDENCE_CHANGE,
                severity=AlertSeverity.INFO,
                status=AlertStatus.PENDING,
                entity_type="belief",
                entity_id="b1",
                entity_content="Content",
                old_value=0.5,
                new_value=0.6,
                change_description="Changed",
                triggered_at=now - timedelta(days=age_days)
            )
            storage.save_alert(alert)

        deleted = storage.cleanup_old_alerts(default_retention_days=30)

        assert deleted == 2

        remaining = storage.get_alerts()
        assert len(remaining) == 2

    def test_cache_behavior(self, storage):
        """Test that cache is populated and used."""
        watch = Watch(
            watch_id="cached_watch",
            name="Cached Watch",
            target_type=WatchTarget.BELIEF
        )
        storage.save_watch(watch)

        # First get - from DB
        retrieved1 = storage.get_watch("cached_watch")

        # Second get - should be from cache
        retrieved2 = storage.get_watch("cached_watch")

        assert retrieved1 is retrieved2  # Same object from cache


# =============================================================================
# ALERT MANAGER TESTS
# =============================================================================


class TestAlertManager:
    """Tests for AlertManager orchestration."""

    def test_create_watch(self, manager):
        """Test creating a watch through manager."""
        watch = manager.create_watch(
            name="Test Watch",
            target_type=WatchTarget.BELIEF,
            target_id="belief_123",
            conditions=[
                AlertCondition(
                    alert_type=AlertType.CREDENCE_CHANGE,
                    threshold_absolute=0.1
                )
            ],
            description="Monitors belief_123"
        )

        assert watch.watch_id.startswith("watch_")
        assert watch.name == "Test Watch"

        # Verify persisted
        retrieved = manager.storage.get_watch(watch.watch_id)
        assert retrieved is not None

    def test_add_condition_to_watch(self, manager):
        """Test adding conditions to existing watch."""
        watch = manager.create_watch(
            name="Test Watch",
            target_type=WatchTarget.BELIEF,
            target_id="belief_123"
        )

        condition = AlertCondition(
            alert_type=AlertType.STATUS_CHANGE
        )

        result = manager.add_condition_to_watch(watch.watch_id, condition)

        assert result is True

        updated = manager.storage.get_watch(watch.watch_id)
        assert len(updated.conditions) == 1

    def test_enable_disable_watch(self, manager):
        """Test enabling and disabling watches."""
        watch = manager.create_watch(
            name="Test Watch",
            target_type=WatchTarget.BELIEF
        )

        manager.disable_watch(watch.watch_id)
        disabled = manager.storage.get_watch(watch.watch_id)
        assert disabled.enabled is False

        manager.enable_watch(watch.watch_id)
        enabled = manager.storage.get_watch(watch.watch_id)
        assert enabled.enabled is True

    def test_check_belief_change_triggers_alert(self, manager):
        """Test that belief changes trigger appropriate alerts."""
        # Create a watch
        watch = manager.create_watch(
            name="Credence Watch",
            target_type=WatchTarget.BELIEF,
            target_id="belief_123",
            conditions=[
                AlertCondition(
                    alert_type=AlertType.CREDENCE_CHANGE,
                    threshold_absolute=0.1
                )
            ]
        )

        # Initial state (no old value)
        manager._belief_states["belief_123"] = {"credence": 0.5, "status": "ACCEPTED"}

        # Significant change
        alerts = manager.check_belief_change(
            belief_id="belief_123",
            content="Some belief content",
            new_credence=0.8,
            new_status="ACCEPTED",
            theory_id=None,
            level=None
        )

        assert len(alerts) == 1
        assert alerts[0].alert_type == AlertType.CREDENCE_CHANGE
        assert alerts[0].old_value == 0.5
        assert alerts[0].new_value == 0.8

    def test_check_belief_change_respects_cooldown(self, manager):
        """Test that cooldown prevents rapid re-alerting."""
        watch = manager.create_watch(
            name="Credence Watch",
            target_type=WatchTarget.BELIEF,
            target_id="belief_123",
            conditions=[
                AlertCondition(
                    alert_type=AlertType.CREDENCE_CHANGE,
                    threshold_absolute=0.1
                )
            ],
            cooldown_minutes=5
        )

        manager._belief_states["belief_123"] = {"credence": 0.5, "status": "ACCEPTED"}

        # First change
        alerts1 = manager.check_belief_change(
            belief_id="belief_123",
            content="Content",
            new_credence=0.7,
            new_status="ACCEPTED"
        )

        # Second change immediately after
        manager._belief_states["belief_123"]["credence"] = 0.7
        alerts2 = manager.check_belief_change(
            belief_id="belief_123",
            content="Content",
            new_credence=0.9,
            new_status="ACCEPTED"
        )

        assert len(alerts1) == 1
        assert len(alerts2) == 0  # Blocked by cooldown

    def test_check_status_change(self, manager):
        """Test status change detection."""
        watch = manager.create_watch(
            name="Status Watch",
            target_type=WatchTarget.BELIEF,
            target_id="belief_456",
            conditions=[
                AlertCondition(alert_type=AlertType.STATUS_CHANGE)
            ]
        )

        manager._belief_states["belief_456"] = {"credence": 0.5, "status": "ACCEPTED"}

        alerts = manager.check_belief_change(
            belief_id="belief_456",
            content="Content",
            new_credence=0.5,
            new_status="CONTESTED"
        )

        assert len(alerts) == 1
        assert alerts[0].alert_type == AlertType.STATUS_CHANGE
        assert "ACCEPTED → CONTESTED" in alerts[0].change_description

    def test_check_new_evidence(self, manager):
        """Test new evidence detection."""
        watch = manager.create_watch(
            name="Evidence Watch",
            target_type=WatchTarget.BELIEF,
            target_id="belief_789",
            conditions=[
                AlertCondition(alert_type=AlertType.NEW_EVIDENCE)
            ]
        )

        manager._belief_states["belief_789"] = {
            "credence": 0.5,
            "status": "ACCEPTED",
            "paper_ids": ["paper_1", "paper_2"]
        }

        alerts = manager.check_belief_change(
            belief_id="belief_789",
            content="Content",
            new_credence=0.5,
            new_status="ACCEPTED",
            paper_ids=["paper_1", "paper_2", "paper_3"]
        )

        assert len(alerts) == 1
        assert alerts[0].alert_type == AlertType.NEW_EVIDENCE
        assert "1 paper(s)" in alerts[0].change_description

    def test_check_theory_change(self, manager):
        """Test theory-level alerts."""
        watch = manager.create_watch(
            name="Theory Watch",
            target_type=WatchTarget.THEORY,
            target_id="theory_ART",
            conditions=[
                AlertCondition(
                    alert_type=AlertType.THEORY_SHIFT,
                    threshold_absolute=0.1
                )
            ]
        )

        manager._theory_states["theory_ART"] = {"average_credence": 0.6}

        alerts = manager.check_theory_change(
            theory_id="theory_ART",
            average_credence=0.8,
            belief_count=10,
            contested_count=2
        )

        assert len(alerts) == 1
        assert alerts[0].alert_type == AlertType.THEORY_SHIFT

    def test_check_theory_contested(self, manager):
        """Test theory contested alert."""
        watch = manager.create_watch(
            name="Theory Watch",
            target_type=WatchTarget.THEORY,
            target_id="theory_SRT",
            conditions=[
                AlertCondition(alert_type=AlertType.THEORY_CONTESTED)
            ]
        )

        manager._theory_states["theory_SRT"] = {"contested_count": 1}

        alerts = manager.check_theory_change(
            theory_id="theory_SRT",
            average_credence=0.7,
            belief_count=15,
            contested_count=3
        )

        assert len(alerts) == 1
        assert alerts[0].alert_type == AlertType.THEORY_CONTESTED

    def test_check_system_coherence(self, manager):
        """Test system coherence alerts."""
        watch = manager.create_watch(
            name="Coherence Watch",
            target_type=WatchTarget.SYSTEM,
            target_id="coherence",
            conditions=[
                AlertCondition(
                    alert_type=AlertType.COHERENCE_DROP,
                    threshold_absolute=0.1,
                    direction="decrease"
                )
            ]
        )

        manager._system_state["coherence"] = 0.85

        alerts = manager.check_system_coherence(0.7)

        assert len(alerts) == 1
        assert alerts[0].alert_type == AlertType.COHERENCE_DROP

    def test_acknowledge_alert(self, manager):
        """Test acknowledging an alert."""
        watch = manager.create_watch(
            name="Test Watch",
            target_type=WatchTarget.BELIEF,
            target_id="belief_test",
            conditions=[
                AlertCondition(
                    alert_type=AlertType.CREDENCE_CHANGE,
                    threshold_absolute=0.1
                )
            ]
        )

        manager._belief_states["belief_test"] = {"credence": 0.5, "status": "ACCEPTED"}

        alerts = manager.check_belief_change(
            belief_id="belief_test",
            content="Content",
            new_credence=0.8,
            new_status="ACCEPTED"
        )

        result = manager.acknowledge_alert(alerts[0].alert_id, user="david")

        assert result is True

    def test_severity_determination(self, manager):
        """Test alert severity is determined correctly."""
        watch = manager.create_watch(
            name="Severity Watch",
            target_type=WatchTarget.BELIEF,
            target_id="belief_sev",
            conditions=[
                AlertCondition(
                    alert_type=AlertType.CREDENCE_CHANGE,
                    threshold_absolute=0.05
                )
            ]
        )

        # Small change - INFO
        manager._belief_states["belief_sev"] = {"credence": 0.5}
        alerts = manager.check_belief_change(
            belief_id="belief_sev",
            content="Content",
            new_credence=0.58,
            new_status="ACCEPTED"
        )
        assert alerts[0].severity == AlertSeverity.INFO

        # Allow cooldown
        watch.last_triggered = datetime.now(timezone.utc) - timedelta(minutes=10)
        manager.storage.save_watch(watch)

        # Medium change - WARNING
        manager._belief_states["belief_sev"]["credence"] = 0.58
        alerts = manager.check_belief_change(
            belief_id="belief_sev",
            content="Content",
            new_credence=0.78,
            new_status="ACCEPTED"
        )
        assert alerts[0].severity == AlertSeverity.WARNING

        # Allow cooldown again
        watch.last_triggered = datetime.now(timezone.utc) - timedelta(minutes=10)
        manager.storage.save_watch(watch)

        # Large change - CRITICAL
        manager._belief_states["belief_sev"]["credence"] = 0.78
        alerts = manager.check_belief_change(
            belief_id="belief_sev",
            content="Content",
            new_credence=0.38,
            new_status="ACCEPTED"
        )
        assert alerts[0].severity == AlertSeverity.CRITICAL

    def test_generate_digest(self, manager):
        """Test digest generation."""
        # Create some alerts
        watch = manager.create_watch(
            name="Digest Watch",
            target_type=WatchTarget.BELIEF,
            target_id="belief_dig",
            conditions=[
                AlertCondition(
                    alert_type=AlertType.CREDENCE_CHANGE,
                    threshold_absolute=0.05
                )
            ],
            cooldown_minutes=0  # No cooldown for test
        )

        for i, cred in enumerate([0.5, 0.6, 0.72, 0.85]):
            manager._belief_states["belief_dig"] = {"credence": cred}
            manager.check_belief_change(
                belief_id="belief_dig",
                content="Content",
                new_credence=cred + 0.08,
                new_status="ACCEPTED"
            )
            # Force reset cooldown
            watch.last_triggered = None
            manager.storage.save_watch(watch)

        digest = manager.generate_digest(since=datetime.now(timezone.utc) - timedelta(hours=1))

        assert "summary" in digest
        assert "by_severity" in digest
        assert "by_type" in digest
        assert digest["summary"]["total_alerts"] >= 3


# =============================================================================
# CONVENIENCE FUNCTION TESTS
# =============================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_create_credence_watch(self, temp_db_path):
        """Test create_credence_watch convenience function."""
        # Reset singleton
        import src.services.query_alerts as qa_module
        qa_module._manager = AlertManager(storage=AlertStorage(db_path=temp_db_path))

        watch = create_credence_watch(
            name="My Credence Watch",
            belief_id="belief_xyz",
            threshold=0.15,
            direction="increase"
        )

        assert watch.target_type == WatchTarget.BELIEF
        assert watch.target_id == "belief_xyz"
        assert len(watch.conditions) == 1
        assert watch.conditions[0].alert_type == AlertType.CREDENCE_CHANGE
        assert watch.conditions[0].threshold_absolute == 0.15
        assert watch.conditions[0].direction == "increase"

    def test_create_theory_watch(self, temp_db_path):
        """Test create_theory_watch convenience function."""
        import src.services.query_alerts as qa_module
        qa_module._manager = AlertManager(storage=AlertStorage(db_path=temp_db_path))

        watch = create_theory_watch(
            name="ART Theory Watch",
            theory_id="theory_ART",
            threshold=0.1
        )

        assert watch.target_type == WatchTarget.THEORY
        assert watch.target_id == "theory_ART"
        assert len(watch.conditions) == 2  # THEORY_SHIFT and THEORY_CONTESTED

    def test_create_topic_watch(self, temp_db_path):
        """Test create_topic_watch convenience function."""
        import src.services.query_alerts as qa_module
        qa_module._manager = AlertManager(storage=AlertStorage(db_path=temp_db_path))

        watch = create_topic_watch(
            name="Stress Research Watch",
            pattern=r"stress|cortisol",
            threshold=0.15
        )

        assert watch.target_type == WatchTarget.TOPIC
        assert watch.target_id == r"stress|cortisol"
        assert len(watch.conditions) == 2  # CREDENCE_CHANGE and NEW_EVIDENCE

    def test_create_system_coherence_watch(self, temp_db_path):
        """Test create_system_coherence_watch convenience function."""
        import src.services.query_alerts as qa_module
        qa_module._manager = AlertManager(storage=AlertStorage(db_path=temp_db_path))

        watch = create_system_coherence_watch(
            name="System Monitor",
            threshold=0.1,
            direction="decrease"
        )

        assert watch.target_type == WatchTarget.SYSTEM
        assert watch.target_id == "coherence"
        assert len(watch.conditions) == 1
        assert watch.conditions[0].alert_type == AlertType.COHERENCE_DROP

    def test_get_alert_manager_singleton(self, temp_db_path):
        """Test that get_alert_manager returns singleton."""
        import src.services.query_alerts as qa_module
        import os

        # Reset singleton
        qa_module._manager = None
        os.environ["AE_ALERTS_DB"] = temp_db_path
        
        try:
            manager1 = get_alert_manager()
            manager2 = get_alert_manager()
    
            assert manager1 is manager2
        finally:
            if "AE_ALERTS_DB" in os.environ:
                del os.environ["AE_ALERTS_DB"]


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestIntegration:
    """Integration tests for full alert workflow."""

    def test_full_workflow_belief_monitoring(self, temp_db_path):
        """Test complete workflow: watch creation, change detection, alert delivery."""
        storage = AlertStorage(db_path=temp_db_path)
        in_app = InAppNotificationHandler()
        manager = AlertManager(storage=storage, in_app_handler=in_app)

        # 1. Create a watch
        watch = manager.create_watch(
            name="Important Belief Watch",
            target_type=WatchTarget.BELIEF,
            target_id="belief_important",
            conditions=[
                AlertCondition(
                    alert_type=AlertType.CREDENCE_CHANGE,
                    threshold_absolute=0.1
                ),
                AlertCondition(
                    alert_type=AlertType.STATUS_CHANGE
                )
            ],
            notify_in_app=True,
            cooldown_minutes=0
        )

        # 2. Set initial state
        manager._belief_states["belief_important"] = {
            "credence": 0.6,
            "status": "ACCEPTED",
            "paper_ids": []
        }

        # 3. Trigger credence change
        alerts = manager.check_belief_change(
            belief_id="belief_important",
            content="Important research finding about nature exposure",
            new_credence=0.8,
            new_status="ACCEPTED",
            theory_id="theory_ART"
        )

        assert len(alerts) == 1
        assert alerts[0].alert_type == AlertType.CREDENCE_CHANGE

        # 4. Verify in-app notification was queued
        # Note: Alert status is DELIVERED after successful send, so we check
        # the notifications list directly instead of get_pending()
        assert len(in_app.notifications) == 1
        assert in_app.notifications[0].status == AlertStatus.DELIVERED

        # 5. Acknowledge (acknowledging a delivered alert)
        in_app.acknowledge(alerts[0].alert_id, user="david")
        assert in_app.notifications[0].status == AlertStatus.ACKNOWLEDGED
        assert in_app.notifications[0].acknowledged_by == "david"

        # 6. Trigger status change
        manager._belief_states["belief_important"]["credence"] = 0.8
        watch.last_triggered = None  # Reset cooldown
        manager.storage.save_watch(watch)

        alerts2 = manager.check_belief_change(
            belief_id="belief_important",
            content="Important research finding",
            new_credence=0.8,
            new_status="CONTESTED"
        )

        assert len(alerts2) == 1
        assert alerts2[0].alert_type == AlertType.STATUS_CHANGE

        # 7. Generate digest
        digest = manager.generate_digest()
        assert digest["summary"]["total_alerts"] == 2

    def test_multiple_watches_same_belief(self, temp_db_path):
        """Test multiple watches monitoring same entity."""
        storage = AlertStorage(db_path=temp_db_path)
        manager = AlertManager(storage=storage)

        # Create two watches with different thresholds
        watch1 = manager.create_watch(
            name="Sensitive Watch",
            target_type=WatchTarget.BELIEF,
            target_id="belief_multi",
            conditions=[
                AlertCondition(
                    alert_type=AlertType.CREDENCE_CHANGE,
                    threshold_absolute=0.05
                )
            ],
            cooldown_minutes=0
        )

        watch2 = manager.create_watch(
            name="Less Sensitive Watch",
            target_type=WatchTarget.BELIEF,
            target_id="belief_multi",
            conditions=[
                AlertCondition(
                    alert_type=AlertType.CREDENCE_CHANGE,
                    threshold_absolute=0.2
                )
            ],
            cooldown_minutes=0
        )

        manager._belief_states["belief_multi"] = {"credence": 0.5}

        # Small change - triggers only sensitive watch
        alerts = manager.check_belief_change(
            belief_id="belief_multi",
            content="Content",
            new_credence=0.58,
            new_status="ACCEPTED"
        )

        assert len(alerts) == 1
        assert alerts[0].watch_id == watch1.watch_id

        # Reset cooldowns
        watch1.last_triggered = None
        watch2.last_triggered = None
        manager.storage.save_watch(watch1)
        manager.storage.save_watch(watch2)

        manager._belief_states["belief_multi"]["credence"] = 0.58

        # Large change - triggers both
        alerts2 = manager.check_belief_change(
            belief_id="belief_multi",
            content="Content",
            new_credence=0.88,
            new_status="ACCEPTED"
        )

        assert len(alerts2) == 2

    def test_topic_pattern_watch(self, temp_db_path):
        """Test topic pattern matching across multiple beliefs."""
        storage = AlertStorage(db_path=temp_db_path)
        manager = AlertManager(storage=storage)

        # Create topic watch
        watch = manager.create_watch(
            name="Stress Research Monitor",
            target_type=WatchTarget.TOPIC,
            target_id=r"stress|anxiety|cortisol",
            conditions=[
                AlertCondition(
                    alert_type=AlertType.CREDENCE_CHANGE,
                    threshold_absolute=0.1
                )
            ],
            cooldown_minutes=0
        )

        # Matching belief
        manager._belief_states["belief_stress1"] = {"credence": 0.5}
        alerts1 = manager.check_belief_change(
            belief_id="belief_stress1",
            content="Nature exposure reduces stress in office workers",
            new_credence=0.7,
            new_status="ACCEPTED"
        )
        assert len(alerts1) == 1

        # Reset cooldown
        watch.last_triggered = None
        manager.storage.save_watch(watch)

        # Another matching belief
        manager._belief_states["belief_cortisol1"] = {"credence": 0.4}
        alerts2 = manager.check_belief_change(
            belief_id="belief_cortisol1",
            content="Morning light exposure affects cortisol levels",
            new_credence=0.6,
            new_status="ACCEPTED"
        )
        assert len(alerts2) == 1

        # Non-matching belief
        manager._belief_states["belief_other"] = {"credence": 0.5}
        alerts3 = manager.check_belief_change(
            belief_id="belief_other",
            content="Color temperature affects visual comfort",
            new_credence=0.7,
            new_status="ACCEPTED"
        )
        assert len(alerts3) == 0


# =============================================================================
# EDGE CASE TESTS
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_conditions_list(self, manager):
        """Test watch with no conditions doesn't trigger."""
        watch = manager.create_watch(
            name="No Conditions Watch",
            target_type=WatchTarget.BELIEF,
            target_id="belief_empty",
            conditions=[]
        )

        manager._belief_states["belief_empty"] = {"credence": 0.5}

        alerts = manager.check_belief_change(
            belief_id="belief_empty",
            content="Content",
            new_credence=0.9,
            new_status="ACCEPTED"
        )

        assert len(alerts) == 0

    def test_zero_old_value(self):
        """Test percentage calculation with zero old value."""
        condition = AlertCondition(
            alert_type=AlertType.CREDENCE_CHANGE,
            threshold_percentage=50.0
        )

        # 0 to 0.5 - would be infinite percentage, handled gracefully
        triggered, reason = condition.is_triggered(0.0, 0.5)

        # Should not crash, and should not trigger (percentage is 0 when old=0)
        assert not triggered

    def test_nonexistent_watch_operations(self, manager):
        """Test operations on nonexistent watches."""
        result = manager.add_condition_to_watch("nonexistent_watch", AlertCondition(alert_type=AlertType.CREDENCE_CHANGE))
        assert result is False

        result = manager.enable_watch("nonexistent_watch")
        assert result is False

        result = manager.disable_watch("nonexistent_watch")
        assert result is False

    def test_acknowledge_nonexistent_alert(self, manager):
        """Test acknowledging nonexistent alert."""
        result = manager.acknowledge_alert("nonexistent_alert")
        assert result is False

    def test_belief_content_truncation(self, manager):
        """Test that long belief content is truncated in alerts."""
        watch = manager.create_watch(
            name="Long Content Watch",
            target_type=WatchTarget.BELIEF,
            target_id="belief_long",
            conditions=[
                AlertCondition(
                    alert_type=AlertType.CREDENCE_CHANGE,
                    threshold_absolute=0.1
                )
            ]
        )

        long_content = "A" * 1000
        manager._belief_states["belief_long"] = {"credence": 0.5}

        alerts = manager.check_belief_change(
            belief_id="belief_long",
            content=long_content,
            new_credence=0.8,
            new_status="ACCEPTED"
        )

        assert len(alerts[0].entity_content) <= 200

    def test_first_belief_observation(self, manager):
        """Test first observation of a belief (no prior state)."""
        watch = manager.create_watch(
            name="New Belief Watch",
            target_type=WatchTarget.BELIEF,
            target_id="belief_new",
            conditions=[
                AlertCondition(
                    alert_type=AlertType.CREDENCE_CHANGE,
                    threshold_absolute=0.1
                )
            ]
        )

        # No prior state for this belief
        alerts = manager.check_belief_change(
            belief_id="belief_new",
            content="Brand new belief",
            new_credence=0.6,
            new_status="ACCEPTED"
        )

        # No alert - need prior state for change detection
        assert len(alerts) == 0

    def test_unicode_in_topic_pattern(self, temp_db_path):
        """Test unicode characters in topic patterns."""
        storage = AlertStorage(db_path=temp_db_path)
        manager = AlertManager(storage=storage)

        watch = manager.create_watch(
            name="Unicode Watch",
            target_type=WatchTarget.TOPIC,
            target_id=r"café|naïve|résumé",
            conditions=[
                AlertCondition(
                    alert_type=AlertType.CREDENCE_CHANGE,
                    threshold_absolute=0.1
                )
            ]
        )

        manager._belief_states["b1"] = {"credence": 0.5}

        alerts = manager.check_belief_change(
            belief_id="b1",
            content="Research conducted at a café showed...",
            new_credence=0.7,
            new_status="ACCEPTED"
        )

        assert len(alerts) == 1


# =============================================================================
# SENSITIVITY PRESET TESTS (Panel Recommendation)
# =============================================================================


class TestSensitivityPresets:
    """Tests for sensitivity preset convenience functions."""

    def test_sensitivity_thresholds_defined(self):
        """Test that sensitivity thresholds are defined for all levels."""
        for sensitivity in AlertSensitivity:
            assert sensitivity in SENSITIVITY_THRESHOLDS
            thresholds = SENSITIVITY_THRESHOLDS[sensitivity]
            assert "absolute" in thresholds
            assert "percentage" in thresholds

    def test_sensitivity_ordering(self):
        """Test that LOW < MEDIUM < HIGH in sensitivity."""
        low = SENSITIVITY_THRESHOLDS[AlertSensitivity.LOW]
        medium = SENSITIVITY_THRESHOLDS[AlertSensitivity.MEDIUM]
        high = SENSITIVITY_THRESHOLDS[AlertSensitivity.HIGH]

        # Higher sensitivity = lower thresholds
        assert high["absolute"] < medium["absolute"] < low["absolute"]
        assert high["percentage"] < medium["percentage"] < low["percentage"]

    def test_create_credence_watch_with_sensitivity(self, temp_db_path):
        """Test credence watch with sensitivity presets."""
        import src.services.query_alerts as qa_module
        qa_module._manager = AlertManager(
            storage=AlertStorage(db_path=temp_db_path),
            auto_cleanup=False
        )

        watch = create_credence_watch_with_sensitivity(
            name="High Sensitivity Watch",
            belief_id="belief_test",
            sensitivity=AlertSensitivity.HIGH
        )

        assert watch.target_type == WatchTarget.BELIEF
        assert watch.target_id == "belief_test"
        assert len(watch.conditions) == 1
        assert watch.conditions[0].threshold_absolute == 0.05
        assert watch.conditions[0].threshold_percentage == 10.0

    def test_create_topic_watch_with_sensitivity(self, temp_db_path):
        """Test topic watch with sensitivity presets."""
        import src.services.query_alerts as qa_module
        qa_module._manager = AlertManager(
            storage=AlertStorage(db_path=temp_db_path),
            auto_cleanup=False
        )

        watch = create_topic_watch_with_sensitivity(
            name="Medium Sensitivity Topic Watch",
            pattern=r"stress|anxiety",
            sensitivity=AlertSensitivity.MEDIUM
        )

        assert watch.target_type == WatchTarget.TOPIC
        assert watch.target_id == r"stress|anxiety"
        assert len(watch.conditions) == 2  # CREDENCE_CHANGE + NEW_EVIDENCE

        credence_condition = watch.conditions[0]
        assert credence_condition.threshold_absolute == 0.1
        assert credence_condition.threshold_percentage == 20.0

    def test_create_theory_watch_with_sensitivity(self, temp_db_path):
        """Test theory watch with sensitivity presets."""
        import src.services.query_alerts as qa_module
        qa_module._manager = AlertManager(
            storage=AlertStorage(db_path=temp_db_path),
            auto_cleanup=False
        )

        watch = create_theory_watch_with_sensitivity(
            name="Low Sensitivity Theory Watch",
            theory_id="theory_ART",
            sensitivity=AlertSensitivity.LOW
        )

        assert watch.target_type == WatchTarget.THEORY
        assert watch.target_id == "theory_ART"
        assert len(watch.conditions) == 2  # THEORY_SHIFT + THEORY_CONTESTED

        shift_condition = watch.conditions[0]
        assert shift_condition.threshold_absolute == 0.2
        assert shift_condition.threshold_percentage == 40.0


class TestPanelChanges:
    """Tests verifying panel recommendation implementation."""

    def test_entrenchment_change_removed(self):
        """Verify ENTRENCHMENT_CHANGE was removed from AlertType."""
        alert_types = [t.value for t in AlertType]
        assert "entrenchment_change" not in alert_types

    def test_stale_evidence_added(self):
        """Verify STALE_EVIDENCE was added."""
        alert_types = [t.value for t in AlertType]
        assert "stale_evidence" in alert_types

    def test_stale_evidence_triggers_without_threshold(self):
        """Test STALE_EVIDENCE always triggers (like STATUS_CHANGE)."""
        condition = AlertCondition(
            alert_type=AlertType.STALE_EVIDENCE
        )

        triggered, reason = condition.is_triggered(None, 0.5)
        assert triggered
        assert "stale_evidence detected" in reason

    def test_webhook_timeout_reduced(self):
        """Verify webhook timeout changed from 10s to 5s."""
        handler = WebhookNotificationHandler()
        assert handler.timeout == 5

    def test_wal_mode_enabled(self, temp_db_path):
        """Verify WAL mode is enabled on storage initialization."""
        import sqlite3

        storage = AlertStorage(db_path=temp_db_path)

        conn = sqlite3.connect(storage.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode")
        mode = cursor.fetchone()[0]
        conn.close()

        assert mode.lower() == "wal"

    def test_auto_cleanup_on_init(self, temp_db_path):
        """Verify auto_cleanup runs on AlertManager initialization."""
        import sqlite3

        storage = AlertStorage(db_path=temp_db_path)

        # Add an old alert directly
        conn = sqlite3.connect(storage.db_path)
        cursor = conn.cursor()
        old_date = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
        cursor.execute("""
            INSERT INTO alerts (alert_id, watch_id, alert_type, severity, status,
                               entity_type, change_description, triggered_at, context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("old_alert", "watch_1", "credence_change", "info", "pending",
              "belief", "Old change", old_date, "{}"))
        conn.commit()
        conn.close()

        # Initialize manager with auto_cleanup
        manager = AlertManager(storage=storage, auto_cleanup=True)

        # Old alert should be cleaned up
        alerts = storage.get_alerts()
        assert len(alerts) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
