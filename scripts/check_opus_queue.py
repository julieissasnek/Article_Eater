#!/usr/bin/env python3
"""
AG Opus Queue Detector

Monitors the card generation queue depth for Pass 2 (Opus polish) cards.
Can be run standalone or imported as a module.

Usage:
    python scripts/check_opus_queue.py              # Print status, exit with 0 or 1
    from scripts.check_opus_queue import check_opus_queue
    status = check_opus_queue(".")
    if status["opus_queued"] > 0:
        print(f"Queued for polish: {status['opus_queued']}")

The script returns a dict with:
    {
        "opus_queued": int,       # Cards waiting for Opus polish (Pass 2)
        "total_queued": int,      # Total cards in queue (any model)
        "alert": bool,            # True if queue is non-empty
        "message": str,           # Human-readable status message
        "queue_stats": dict       # Full stats from orchestrator
    }

Exit codes (when run as __main__):
    0: Queue is empty (success)
    1: Queue has pending cards (needs processing)
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def check_opus_queue(base_dir: str = ".") -> Dict[str, Any]:
    """
    Check Opus polish queue depth from CardGenerationOrchestrator.

    Reads the generation_queue.json state file and extracts:
    - opus_queued: Number of Opus-model cards in queue (these are Pass 2 polish jobs)
    - total_queued: Total cards waiting for generation (any model)
    - alert: Whether any Opus cards are waiting
    - message: Human-readable status message

    Args:
        base_dir: Base directory for the project (where QUEUE_STATE_PATH is found)

    Returns:
        Dictionary with queue status:
        {
            "opus_queued": int,
            "total_queued": int,
            "alert": bool,
            "message": str,
            "queue_stats": dict (full stats from orchestrator)
        }
    """
    base_path = Path(base_dir)
    queue_path = base_path / "data/materialized_views/cards/generation_queue.json"

    # Initialize result
    result = {
        "opus_queued": 0,
        "total_queued": 0,
        "alert": False,
        "message": "Queue status unknown",
        "queue_stats": {}
    }

    # Check if queue file exists
    if not queue_path.exists():
        result["message"] = (
            f"Queue file not found: {queue_path}\n"
            "Card generation pipeline may not have been initialized."
        )
        return result

    try:
        # Read queue state
        queue_data = json.loads(queue_path.read_text())

        # Extract stats
        stats = queue_data.get("stats", {})
        result["queue_stats"] = stats

        # Total cards in queue
        total_queued = stats.get("queued", 0)
        result["total_queued"] = total_queued

        # Cards queued for Opus (Pass 2 polish)
        opus_queued = stats.get("by_model", {}).get("opus", 0)
        result["opus_queued"] = opus_queued

        # Set alert flag
        result["alert"] = opus_queued > 0

        # Generate message
        if opus_queued == 0:
            result["message"] = (
                "No cards waiting for Opus polish (Pass 2). Queue is healthy."
            )
        elif opus_queued == 1:
            result["message"] = (
                "1 card waiting for Opus polish (Pass 2).\n"
                "Run: python scripts/batch_generate_cards.py --process-opus-queue"
            )
        else:
            result["message"] = (
                f"{opus_queued} cards waiting for Opus polish (Pass 2).\n"
                f"Total in queue: {total_queued} (other models: {total_queued - opus_queued}).\n"
                "Run: python scripts/batch_generate_cards.py --process-opus-queue --max-cards 50"
            )

        return result

    except json.JSONDecodeError as e:
        result["message"] = f"Queue file corrupted (JSON error): {e}"
        return result
    except Exception as e:
        result["message"] = f"Failed to read queue: {e}"
        return result


def main():
    """
    Standalone entry point: check queue and print status.

    Prints a clear status message. If queue is non-empty, includes
    instructions for processing. Exits with code 1 if queue has pending
    cards, 0 if queue is empty.
    """
    status = check_opus_queue(".")

    # Print status
    print(status["message"])
    print()

    # Print detailed stats if queue is non-empty
    if status["alert"]:
        stats = status["queue_stats"]
        print("Queue Status Details:")
        print(f"  Opus cards (Pass 2):     {status['opus_queued']}")
        print(f"  Total in queue:          {status['total_queued']}")

        by_model = stats.get("by_model", {})
        if by_model:
            print(f"  By model breakdown:")
            for model, count in by_model.items():
                if count > 0:
                    print(f"    {model}: {count}")

        session_q = stats.get("session_queue", 0)
        api_q = stats.get("api_queue", 0)
        print(f"  Session-based queue:     {session_q}")
        print(f"  API batch queue:         {api_q}")
        print()

    # Exit code
    sys.exit(1 if status["alert"] else 0)


if __name__ == "__main__":
    main()
