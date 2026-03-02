#!/usr/bin/env python3
"""
Standalone Recommendation Loop Runner

Invokes the RecommendationLoopService for article discovery pipeline integration.

Usage:
    python scripts/run_recommendation_loop.py --once         # Single pass
    python scripts/run_recommendation_loop.py --continuous   # Daemon mode
    python scripts/run_recommendation_loop.py --status       # Health check
    python scripts/run_recommendation_loop.py --continuous --interval 300  # Custom interval

Options:
    --once              Run a single cycle and exit
    --continuous        Run continuously as a daemon
    --interval SECS     Interval between cycles (default 300 = 5 min)
    --max-cycles N      Max cycles to run in continuous mode
    --status            Check current loop health
    --db DB_PATH        Path to web_persistence database
    --web-db WEB_DB     Path to article_eater.db
    --help              Show this help
"""

import argparse
import json
import sys
import logging
from pathlib import Path
from datetime import datetime, timezone

# Ensure repo root is in path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Recommendation Loop Service Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single pass cycle"
    )
    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Run continuously as daemon"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Interval between cycles in seconds (default 300)"
    )
    parser.add_argument(
        "--max-cycles",
        type=int,
        default=None,
        help="Max cycles in continuous mode (None = infinite)"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Check loop health status"
    )
    parser.add_argument(
        "--db",
        type=str,
        default=None,
        help="Path to web_persistence database"
    )
    parser.add_argument(
        "--web-db",
        type=str,
        default=None,
        help="Path to article_eater.db"
    )

    args = parser.parse_args()

    # Resolve database paths
    if args.db is None:
        args.db = str(REPO_ROOT / "web_persistence_v2.db")
    if args.web_db is None:
        args.web_db = str(REPO_ROOT / "data" / "article_eater.db")

    logger.info("=" * 80)
    logger.info("RECOMMENDATION LOOP RUNNER")
    logger.info(f"Started at {datetime.now(timezone.utc).isoformat()}")
    logger.info(f"DB: {args.db}")
    logger.info(f"Web DB: {args.web_db}")
    logger.info("=" * 80)

    try:
        from src.services.recommendation_loop import RecommendationLoopService

        service = RecommendationLoopService(
            db_path=args.db,
            web_db_path=args.web_db,
        )

        if args.status:
            # Health check: run single pass with minimal output
            logger.info("Running health check...")
            result = service.run_single_pass(top_n=3)
            print(json.dumps(result, indent=2, default=str))
            return 0

        elif args.continuous:
            logger.info(
                f"Starting continuous loop (interval={args.interval}s, "
                f"max_cycles={args.max_cycles})"
            )
            service.run_continuous(
                interval_seconds=args.interval,
                max_cycles=args.max_cycles
            )
            return 0

        else:
            # Default: single pass
            logger.info("Running single pass cycle...")
            result = service.run_single_pass(top_n=5)
            print(json.dumps(result, indent=2, default=str))
            return 0

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
