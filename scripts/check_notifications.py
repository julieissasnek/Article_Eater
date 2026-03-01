#!/usr/bin/env python3
"""
Check Notifications CLI — ATLAS HITL Interface
===============================================

Created: 2026-02-27

Usage:
    python scripts/check_notifications.py pending          # Show unread
    python scripts/check_notifications.py pending --type extraction_review
    python scripts/check_notifications.py digest           # Daily summary
    python scripts/check_notifications.py mark-read <id>   # Mark as read
    python scripts/check_notifications.py archive          # Archive read items
    python scripts/check_notifications.py count            # Just the count
"""

import sys
import os
import argparse

# Add repo root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.notification_service import (
    NotificationService,
    NotificationType,
    Severity,
)


def cmd_pending(args):
    ns = NotificationService()
    filter_type = None
    if args.type:
        try:
            filter_type = NotificationType(args.type)
        except ValueError:
            print(f"Unknown type: {args.type}")
            print(f"Valid types: {[t.value for t in NotificationType]}")
            return 1

    pending = ns.get_pending(filter_type=filter_type)
    if not pending:
        print("No pending notifications.")
        return 0

    print(f"\n{'='*70}")
    print(f"  ATLAS Notifications: {len(pending)} pending")
    print(f"{'='*70}\n")

    for n in pending:
        sev_icon = {"critical": "!!!", "warning": " ! ", "info": "   "}.get(
            n.severity, "   "
        )
        print(f"  [{sev_icon}] {n.title}")
        print(f"        Type: {n.type}  |  Severity: {n.severity}")
        print(f"        {n.description}")
        if n.action_url:
            print(f"        Action: {n.action_url}")
        print(f"        ID: {n.id}  |  {n.created_at}")
        print()

    return 0


def cmd_digest(args):
    ns = NotificationService()
    digest = ns.generate_digest()
    print(digest)
    return 0


def cmd_mark_read(args):
    ns = NotificationService()
    if ns.mark_read(args.id):
        print(f"Notification {args.id} marked as read.")
        return 0
    else:
        print(f"Notification {args.id} not found.")
        return 1


def cmd_archive(args):
    ns = NotificationService()
    count = ns.archive_read()
    print(f"Archived {count} read notification(s).")
    return 0


def cmd_count(args):
    ns = NotificationService()
    pending = ns.get_pending()
    critical = sum(1 for n in pending if n.severity == "critical")
    warning = sum(1 for n in pending if n.severity == "warning")
    info = sum(1 for n in pending if n.severity == "info")
    print(f"Pending: {len(pending)} (critical: {critical}, warning: {warning}, info: {info})")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="ATLAS Notification CLI"
    )
    sub = parser.add_subparsers(dest="command")

    p_pending = sub.add_parser("pending", help="Show pending notifications")
    p_pending.add_argument("--type", help="Filter by notification type")

    sub.add_parser("digest", help="Generate daily digest")

    p_read = sub.add_parser("mark-read", help="Mark notification as read")
    p_read.add_argument("id", help="Notification ID")

    sub.add_parser("archive", help="Archive read notifications")
    sub.add_parser("count", help="Show notification count")

    args = parser.parse_args()

    commands = {
        "pending": cmd_pending,
        "digest": cmd_digest,
        "mark-read": cmd_mark_read,
        "archive": cmd_archive,
        "count": cmd_count,
    }

    if args.command in commands:
        sys.exit(commands[args.command](args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
