#!/usr/bin/env python3
"""
Session Card Generation — Free Opus Writing in CW/CC/AG Sessions
==================================================================

This script is run WITHIN a Claude Code session (CW/CC/AG). It provides
a zero-cost interface for the session agent to generate ATLAS cards without
making paid API calls. The session agent IS the LLM.

Architecture:
    SessionCardWriter.get_next_card_prompt()
        ↓ (agent reads and processes prompt)
    Agent generates tab content in conversation
        ↓ (agent provides structured response)
    SessionCardWriter.accept_card_response()
        → Parses, validates, saves card to disk

Usage:
    # Show next card prompt for agent to process
    python scripts/session_generate_cards.py --next-prompt

    # Show next 3 cards for agent to batch-process
    python scripts/session_generate_cards.py --next-prompt --count 3

    # Filter to specific card type
    python scripts/session_generate_cards.py --next-prompt --type t1-framework

    # Show queue status
    python scripts/session_generate_cards.py --status

    # Show claims from all terminals
    python scripts/session_generate_cards.py --show-claims

    # Accept generated card (normally called from agent via Python API)
    python scripts/session_generate_cards.py --accept-response \
        --card-id "t1-framework:ecological_psychology" \
        --response-file /path/to/response.txt

Success Conditions:
    SC-SGC-1: Agent can read --next-prompt output in conversation
    SC-SGC-2: Agent generates tab content following the prompts
    SC-SGC-3: Agent provides response in structured format
    SC-SGC-4: Script accepts response and saves card to disk
    SC-SGC-5: Multiple terminals can claim cards without duplicates
    SC-SGC-6: Status reports show queue depth and claim counts

References:
    - src/qa/session_card_writer.py: SessionCardWriter class
    - src/qa/card_tab_generators.py: Prompt builders
    - scripts/batch_generate_cards.py: Pass 1 for reference

Author: CW (Claude/Cowork)
Date: 2026-03-04
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.qa.session_card_writer import SessionCardWriter
from src.qa.card_generation_orchestrator import CardGenerationOrchestrator
from src.qa.cards import CardType

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

CLAIMS_FILE = PROJECT_ROOT / "data" / "session_card_claims.json"
CARD_STORAGE_DIR = PROJECT_ROOT / "data" / "cards"
QUEUE_FILE = PROJECT_ROOT / "data" / "generation_queue.json"


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_next_prompt(args: argparse.Namespace) -> None:
    """Show the next card prompt for the agent to process."""
    # Load or create orchestrator + session writer
    try:
        orchestrator = CardGenerationOrchestrator.from_file(QUEUE_FILE)
    except Exception as e:
        logger.warning(f"Could not load queue from {QUEUE_FILE}: {e}")
        orchestrator = CardGenerationOrchestrator()

    writer = SessionCardWriter(
        queue=orchestrator.queue,
        claims_file=CLAIMS_FILE,
        card_storage_dir=CARD_STORAGE_DIR,
    )

    # Determine card type filter
    card_type_filter = None
    if args.type:
        try:
            card_type_filter = CardType(args.type)
        except ValueError:
            print(f"Invalid card type: {args.type}")
            sys.exit(1)

    terminal_id = args.terminal or "default"

    # Get prompts
    prompts = []
    for i in range(args.count):
        prompt = writer.get_next_card_prompt(
            terminal_id=terminal_id,
            card_type_filter=card_type_filter,
        )
        if not prompt:
            if i == 0:
                print("No unclaimed cards in queue.")
                return
            else:
                break
        prompts.append(prompt)

    # Display prompts
    if len(prompts) == 1:
        print(prompts[0].to_markdown())
    else:
        for i, prompt in enumerate(prompts, 1):
            print(f"\n{'='*70}")
            print(f"CARD {i} of {len(prompts)}")
            print(f"{'='*70}\n")
            print(prompt.to_markdown())
            if i < len(prompts):
                print(f"\n{'='*70}\n")


def cmd_status(args: argparse.Namespace) -> None:
    """Show queue status."""
    try:
        orchestrator = CardGenerationOrchestrator.from_file(QUEUE_FILE)
    except Exception as e:
        logger.warning(f"Could not load queue: {e}")
        orchestrator = CardGenerationOrchestrator()

    writer = SessionCardWriter(
        queue=orchestrator.queue,
        claims_file=CLAIMS_FILE,
        card_storage_dir=CARD_STORAGE_DIR,
    )

    status = writer.get_queue_status()

    print("\n=== SESSION CARD GENERATION QUEUE STATUS ===\n")
    print(f"Total queued for session: {status['total_queued']}")
    print(f"  Unclaimed:              {status['unclaimed_count']}")
    print(f"  Claimed by terminals:   {status['claimed_count']}")
    print()

    if status["by_type"]:
        print("By card type:")
        for card_type, count in sorted(status["by_type"].items()):
            print(f"  {card_type:20s}: {count:3d}")
        print()

    if status["unclaimed"] and args.verbose:
        print("Unclaimed cards:")
        for item in status["unclaimed"][:10]:
            print(f"  {item['card_id']:40s} (priority {item['priority']})")
        if len(status["unclaimed"]) > 10:
            print(f"  ... and {len(status['unclaimed']) - 10} more")
        print()

    if status["claimed"] and args.verbose:
        print("Claimed cards:")
        for item in status["claimed"][:10]:
            print(f"  {item['card_id']:40s}")
        if len(status["claimed"]) > 10:
            print(f"  ... and {len(status['claimed']) - 10} more")
        print()


def cmd_show_claims(args: argparse.Namespace) -> None:
    """Show all terminal claims."""
    try:
        orchestrator = CardGenerationOrchestrator.from_file(QUEUE_FILE)
    except Exception as e:
        logger.warning(f"Could not load queue: {e}")
        orchestrator = CardGenerationOrchestrator()

    writer = SessionCardWriter(
        queue=orchestrator.queue,
        claims_file=CLAIMS_FILE,
        card_storage_dir=CARD_STORAGE_DIR,
    )

    print("\n=== TERMINAL CLAIMS ===\n")

    # Group by terminal
    all_claims = writer.claims._claims
    by_terminal = {}
    for claim in all_claims.values():
        if claim.terminal_id not in by_terminal:
            by_terminal[claim.terminal_id] = []
        by_terminal[claim.terminal_id].append(claim)

    for terminal_id in sorted(by_terminal.keys()):
        claims = by_terminal[terminal_id]
        print(f"Terminal: {terminal_id}")

        # Count by status
        by_status = {}
        for claim in claims:
            by_status[claim.status] = by_status.get(claim.status, 0) + 1

        for status in ["claimed", "in_progress", "completed", "failed"]:
            if status in by_status:
                print(f"  {status:12s}: {by_status[status]:3d}")

        if args.verbose:
            print("  Details:")
            for claim in sorted(claims, key=lambda c: c.claimed_at):
                print(
                    f"    {claim.card_id:40s} "
                    f"{claim.status:12s} {claim.claimed_at}"
                )
        print()


def cmd_accept_response(args: argparse.Namespace) -> None:
    """Accept generated card from agent."""
    if not args.card_id:
        print("--card-id required")
        sys.exit(1)

    if not args.response_file:
        print("--response-file required")
        sys.exit(1)

    # Load response from file
    response_file = Path(args.response_file)
    if not response_file.exists():
        print(f"Response file not found: {response_file}")
        sys.exit(1)

    with open(response_file) as f:
        response_text = f.read()

    # Parse response into tab structure
    # Expected format: ### tab_name ... content ... ### next_tab_name ...
    tab_responses = _parse_agent_response(response_text)

    # Load orchestrator and writer
    try:
        orchestrator = CardGenerationOrchestrator.from_file(QUEUE_FILE)
    except Exception as e:
        logger.warning(f"Could not load queue: {e}")
        orchestrator = CardGenerationOrchestrator()

    writer = SessionCardWriter(
        queue=orchestrator.queue,
        claims_file=CLAIMS_FILE,
        card_storage_dir=CARD_STORAGE_DIR,
    )

    # Accept response
    terminal_id = args.terminal or "default"
    success, message, card = writer.accept_card_response(
        card_id=args.card_id,
        tab_responses=tab_responses,
        terminal_id=terminal_id,
    )

    print(f"Result: {success}")
    print(f"Message: {message}")
    if card:
        print(f"Card ID: {card.card_id}")


def _parse_agent_response(response_text: str) -> Dict[str, str]:
    """
    Parse agent response text into tab responses.

    Expected format:
    ### tab_name
    prose and json content here...

    ### next_tab_name
    content here...
    """
    tab_responses = {}
    current_tab = None
    current_content = []

    for line in response_text.split("\n"):
        if line.startswith("### "):
            # New tab section
            if current_tab:
                tab_responses[current_tab] = "\n".join(current_content).strip()
            current_tab = line.replace("### ", "").strip().lower()
            current_content = []
        elif current_tab:
            current_content.append(line)

    # Save last tab
    if current_tab:
        tab_responses[current_tab] = "\n".join(current_content).strip()

    return tab_responses


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Session card generation — free Opus writing in CW/CC/AG sessions",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # --next-prompt
    next_parser = subparsers.add_parser(
        "next-prompt",
        help="Get the next card prompt for the agent to process",
    )
    next_parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of cards to show (default: 1)",
    )
    next_parser.add_argument(
        "--type",
        help="Filter to specific card type (e.g., t1-framework, t2-mechanism)",
    )
    next_parser.add_argument(
        "--terminal",
        default="default",
        help="Terminal ID for claims tracking (default: default)",
    )

    # --status
    status_parser = subparsers.add_parser(
        "status",
        help="Show queue status",
    )
    status_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed card lists",
    )

    # --show-claims
    claims_parser = subparsers.add_parser(
        "show-claims",
        help="Show all terminal claims",
    )
    claims_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed claim info",
    )

    # --accept-response
    accept_parser = subparsers.add_parser(
        "accept-response",
        help="Accept generated card response from agent",
    )
    accept_parser.add_argument(
        "--card-id",
        required=True,
        help="Card ID being completed",
    )
    accept_parser.add_argument(
        "--response-file",
        required=True,
        help="File containing agent's response",
    )
    accept_parser.add_argument(
        "--terminal",
        default="default",
        help="Terminal ID that provided the response",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Dispatch to command handler
    if args.command == "next-prompt":
        cmd_next_prompt(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "show-claims":
        cmd_show_claims(args)
    elif args.command == "accept-response":
        cmd_accept_response(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
