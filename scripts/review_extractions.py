#!/usr/bin/env python3
"""
Review Extractions CLI — ATLAS HITL Approval Interface
======================================================

Created: 2026-02-27
Sprint: COMPLETENESS-1

Human-in-the-loop tool for reviewing and approving/rejecting
paper extractions before they enter the web of belief + BN.

Usage:
    python scripts/review_extractions.py list
    python scripts/review_extractions.py preview <paper_id>
    python scripts/review_extractions.py approve <paper_id> [--notes "..."]
    python scripts/review_extractions.py reject <paper_id> --reason "..."
    python scripts/review_extractions.py reject <paper_id> --reason "..." --requeue
"""

import sys
import os
import argparse
import json

# Add repo root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.extraction_approval import ExtractionApprovalService


def cmd_list(args):
    """List papers pending approval."""
    svc = ExtractionApprovalService()
    pending = svc.get_pending_approvals()

    if not pending:
        print("\nNo papers pending approval.")
        print("All extracted papers have been reviewed.")
        return 0

    print(f"\n{'='*75}")
    print(f"  Papers Pending Approval: {len(pending)}")
    print(f"{'='*75}\n")
    print(f"  {'#':>3}  {'Priority':>8}  {'Type':<14}  {'Conf':>5}  {'Paper ID'}")
    print(f"  {'':->3}  {'':->8}  {'':->14}  {'':->5}  {'':->40}")

    for i, p in enumerate(pending, 1):
        extraction = p.get("extraction_result") or {}
        n_claims = len(extraction.get("findings", []))
        print(
            f"  {i:>3}  {p['priority']:>8}  {p['article_type']:<14}  "
            f"{p['classification_confidence']:>5.2f}  {p['paper_id'][:50]}"
        )
        if n_claims:
            print(f"       ({n_claims} claims extracted)")

    print(f"\nUse 'preview <paper_id>' to see extracted claims.")
    print(f"Use 'approve <paper_id>' to trigger integration.")
    return 0


def cmd_preview(args):
    """Show detailed extraction review for a paper."""
    svc = ExtractionApprovalService()
    summary = svc.get_review_summary(args.paper_id)

    if "error" in summary:
        print(f"\nError: {summary['error']}")
        return 1

    print(f"\n{'='*70}")
    print(f"  Extraction Review: {summary['paper_id'][:60]}")
    print(f"{'='*70}\n")
    print(f"  DOI:           {summary['doi']}")
    print(f"  Article type:  {summary['article_type']}")
    print(f"  Status:        {summary['status']}")
    print(f"  Claims:        {summary['n_claims']}")
    print(f"  Rules:         {summary['n_rules']}")
    print(f"  With effect:   {summary['with_effect_size']}")
    print(f"  With p-value:  {summary['with_p_value']}")
    print(f"  Theories:      {', '.join(summary['theories']) or 'none'}")

    preview = summary.get("findings_preview", [])
    if preview:
        print(f"\n  --- First {len(preview)} findings ---\n")
        for i, f in enumerate(preview, 1):
            claim = f.get("claim", f.get("statement", ""))[:80]
            ant = f.get("antecedent", "?")[:30]
            con = f.get("consequent", "?")[:30]
            direction = f.get("direction", "?")
            print(f"  {i}. {claim}")
            print(f"     {ant} → {con} ({direction})")
            if f.get("p_value"):
                print(f"     p={f['p_value']}, effect={f.get('effect_size', '?')}")
            print()

    print(f"  To approve: python scripts/review_extractions.py approve {args.paper_id}")
    print(f"  To reject:  python scripts/review_extractions.py reject {args.paper_id} --reason '...'")
    return 0


def cmd_approve(args):
    """Approve a paper for integration."""
    svc = ExtractionApprovalService()
    result = svc.approve(args.paper_id, reviewer_notes=args.notes or "")

    if result.get("success"):
        print(f"\nPaper APPROVED: {args.paper_id}")
        integration = result.get("integration", {})
        if integration.get("success"):
            print("Integration cascade triggered successfully.")
        else:
            print(f"Integration note: {integration.get('error', 'unknown')}")
            print("Paper is marked approved — run integration manually when ready.")
    else:
        print(f"\nApproval failed: {result.get('error')}")
        return 1

    return 0


def cmd_reject(args):
    """Reject a paper's extraction."""
    svc = ExtractionApprovalService()
    result = svc.reject(
        args.paper_id,
        reason=args.reason or "No reason given",
        requeue=args.requeue,
    )

    if result.get("success"):
        action = "REJECTED and RE-QUEUED" if args.requeue else "REJECTED"
        print(f"\nPaper {action}: {args.paper_id}")
        print(f"Reason: {args.reason or 'No reason given'}")
    else:
        print(f"\nRejection failed: {result.get('error')}")
        return 1

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="ATLAS Extraction Review CLI"
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="List papers pending approval")

    p_preview = sub.add_parser("preview", help="Preview extraction")
    p_preview.add_argument("paper_id", help="Paper ID or DOI")

    p_approve = sub.add_parser("approve", help="Approve for integration")
    p_approve.add_argument("paper_id", help="Paper ID or DOI")
    p_approve.add_argument("--notes", help="Reviewer notes")

    p_reject = sub.add_parser("reject", help="Reject extraction")
    p_reject.add_argument("paper_id", help="Paper ID or DOI")
    p_reject.add_argument("--reason", help="Rejection reason", required=True)
    p_reject.add_argument(
        "--requeue", action="store_true",
        help="Re-queue for re-extraction instead of permanent rejection",
    )

    args = parser.parse_args()

    commands = {
        "list": cmd_list,
        "preview": cmd_preview,
        "approve": cmd_approve,
        "reject": cmd_reject,
    }

    if args.command in commands:
        sys.exit(commands[args.command](args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
