#!/usr/bin/env python3
"""
Terminal Card Generation — Quick-Start for CC/CW/AG Sessions
=============================================================

Paste this into a CC terminal to start generating cards.
The session agent does the writing — zero API cost.

Usage:
    python scripts/terminal_card_gen.py status
    python scripts/terminal_card_gen.py claim --terminal CC-1 --count 10
    python scripts/terminal_card_gen.py next --terminal CC-1
    python scripts/terminal_card_gen.py show-claims

Supports up to 15 simultaneous terminals. Each terminal claims
a slice of cards, generates them, and marks them done. File-based
coordination via data/session_card_claims.json prevents duplication.

Author: CW (Claude/Cowork)
Date: 2026-03-04
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.qa.session_card_writer import SessionCardWriter


def cmd_status(writer: SessionCardWriter, args):
    """Show queue status and claims."""
    status = writer.get_queue_status()
    print(f"\n{'='*60}")
    print(f"CARD GENERATION STATUS")
    print(f"{'='*60}")
    print(json.dumps(status, indent=2, default=str))
    print(f"{'='*60}\n")


def cmd_claim(writer: SessionCardWriter, args):
    """Claim cards for a terminal."""
    terminal = args.terminal
    count = args.count
    card_type = args.type

    claimed = writer.claim_cards(
        terminal_id=terminal,
        count=count,
        card_type_filter=card_type,
    )

    print(f"\nClaimed {len(claimed)} cards for terminal {terminal}:")
    for card_id in claimed:
        print(f"  - {card_id}")
    print(f"\nRun: python scripts/terminal_card_gen.py next --terminal {terminal}")


def cmd_next(writer: SessionCardWriter, args):
    """Get the next card prompt for a terminal."""
    terminal = args.terminal
    prompt = writer.get_next_card_prompt(terminal_id=terminal)

    if prompt is None:
        print(f"\nNo cards available for terminal {terminal}.")
        print("Either queue is empty or all cards are claimed.")
        print("Run: python scripts/terminal_card_gen.py status")
        return

    print(f"\n{'='*60}")
    print(f"CARD: {prompt.card_id}")
    print(f"TYPE: {prompt.card_type}")
    print(f"TABS: {', '.join(prompt.tab_names)}")
    print(f"{'='*60}")

    for tab_name in prompt.tab_names:
        if tab_name in prompt.tab_prompts:
            sys_prompt, user_prompt = prompt.tab_prompts[tab_name]
            print(f"\n{'─'*40}")
            print(f"TAB: {tab_name.upper()}")
            print(f"{'─'*40}")
            print(f"\n[SYSTEM PROMPT — {len(sys_prompt)} chars]")
            # Print first 200 chars of system prompt
            print(sys_prompt[:200] + "..." if len(sys_prompt) > 200 else sys_prompt)
            print(f"\n[USER PROMPT — {len(user_prompt)} chars]")
            print(user_prompt[:500] + "..." if len(user_prompt) > 500 else user_prompt)

    print(f"\n{'='*60}")
    print(f"Write content for each tab above, then submit with:")
    print(f"  writer.accept_card_response('{prompt.card_id}', tab_responses, '{terminal}')")
    print(f"{'='*60}\n")


def cmd_show_claims(writer: SessionCardWriter, args):
    """Show all current claims across terminals."""
    claims = writer._claims_registry._claims
    if not claims:
        print("\nNo active claims.")
        return

    by_terminal = {}
    for card_id, claim in claims.items():
        tid = claim.terminal_id
        if tid not in by_terminal:
            by_terminal[tid] = {"claimed": 0, "completed": 0, "failed": 0}
        by_terminal[tid][claim.status] = by_terminal[tid].get(claim.status, 0) + 1

    print(f"\n{'='*60}")
    print(f"TERMINAL CLAIMS")
    print(f"{'='*60}")
    for tid, counts in sorted(by_terminal.items()):
        total = sum(counts.values())
        print(f"  {tid}: {total} cards — "
              f"{counts.get('claimed', 0)} active, "
              f"{counts.get('completed', 0)} done, "
              f"{counts.get('failed', 0)} failed")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Terminal card generation with parallel coordination"
    )
    subparsers = parser.add_subparsers(dest="command")

    # status
    subparsers.add_parser("status", help="Show queue status")

    # claim
    p_claim = subparsers.add_parser("claim", help="Claim cards for terminal")
    p_claim.add_argument("--terminal", required=True, help="Terminal ID (e.g. CC-1, AG-OPUS-1)")
    p_claim.add_argument("--count", type=int, default=10, help="Number of cards to claim")
    p_claim.add_argument("--type", help="Card type filter (e.g. t1-framework)")

    # next
    p_next = subparsers.add_parser("next", help="Get next card prompt")
    p_next.add_argument("--terminal", required=True, help="Terminal ID")

    # show-claims
    subparsers.add_parser("show-claims", help="Show all claims across terminals")

    args = parser.parse_args()

    writer = SessionCardWriter(base_dir=str(PROJECT_ROOT))

    if args.command == "status":
        cmd_status(writer, args)
    elif args.command == "claim":
        cmd_claim(writer, args)
    elif args.command == "next":
        cmd_next(writer, args)
    elif args.command == "show-claims":
        cmd_show_claims(writer, args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
