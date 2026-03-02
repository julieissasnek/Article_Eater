#!/usr/bin/env python3
"""
OVERSEER v2 Management Layer CLI

Run management checks and print readable reports.

Usage:
    python scripts/overseer_management_check.py \
        --overseer-db data/overseer.db \
        --web-db data/web.db \
        [--format text|json] \
        [--output report.txt]
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from src.services.overseer_management import ManagementDashboard

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Setup logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def report_to_json(report) -> dict:
    """Convert ManagementReport to JSON-serializable dict."""
    def dt_to_str(dt):
        return dt.isoformat() if dt else None

    def pipeline_to_dict(p):
        return {
            "pipeline_id": p.pipeline_id,
            "display_name": p.display_name,
            "status": p.status.value,
            "queue_depth": p.queue_depth,
            "throughput_24h": p.throughput_24h,
            "error_rate_24h": p.error_rate_24h,
            "bottleneck": p.bottleneck,
        }

    def stage_to_dict(s):
        return {
            "stage_name": s.stage_name,
            "items_waiting": s.items_waiting,
            "items_in_progress": s.items_in_progress,
            "items_completed_24h": s.items_completed_24h,
            "items_completed_7d": s.items_completed_7d,
            "items_completed_30d": s.items_completed_30d,
            "failure_rate_24h": s.failure_rate_24h,
            "avg_processing_time_hours": s.avg_processing_time_hours,
            "bottleneck_score": s.bottleneck_score,
            "bottleneck_component": s.bottleneck_component,
        }

    return {
        "timestamp": dt_to_str(report.timestamp),
        "overall_health": report.overall_health,
        "critical_alerts": report.critical_alerts,
        "immediate_actions_recommended": report.immediate_actions_recommended,
        "pipeline_statuses": {
            pid: pipeline_to_dict(p)
            for pid, p in report.pipeline_statuses.items()
        },
        "queue_health": {
            "total_targets": report.queue_health.total_targets,
            "open_targets": report.queue_health.open_targets,
            "searching_targets": report.queue_health.searching_targets,
            "found_targets": report.queue_health.found_targets,
            "closed_targets": report.queue_health.closed_targets,
            "stale_targets": report.queue_health.stale_targets,
            "search_to_found_rate": report.queue_health.search_to_found_rate,
            "oldest_open_target_hours": report.queue_health.oldest_open_target_hours,
            "health_status": report.queue_health.health_status,
        },
        "article_flow": {
            "overall_throughput_24h": report.article_flow.overall_throughput_24h,
            "overall_throughput_7d": report.article_flow.overall_throughput_7d,
            "total_items_in_system": report.article_flow.total_items_in_system,
            "critical_bottleneck": report.article_flow.critical_bottleneck,
            "flow_efficiency": report.article_flow.flow_efficiency,
            "health_status": report.article_flow.health_status,
            "stages": [stage_to_dict(s) for s in report.article_flow.stages],
        },
        "suggestion_backlog": {
            "total_unacted_suggestions": report.suggestion_backlog.total_unacted_suggestions,
            "oldest_suggestion_days": report.suggestion_backlog.age_distribution.oldest_suggestion_days,
            "by_argumentation_gaps": report.suggestion_backlog.by_argumentation_gaps,
            "by_voi_gaps": report.suggestion_backlog.by_voi_gaps,
            "by_qa_gaps": report.suggestion_backlog.by_qa_gaps,
            "by_interpretation_space_gaps": report.suggestion_backlog.by_interpretation_space_gaps,
            "staleness_alert": report.suggestion_backlog.staleness_alert,
            "health_status": report.suggestion_backlog.health_status,
        },
        "extraction_queue": {
            "pdfs_downloaded_not_extracted": report.extraction_queue.pdfs_downloaded_not_extracted,
            "pdfs_extracted_not_validated": report.extraction_queue.pdfs_extracted_not_validated,
            "pdfs_validated_not_integrated": report.extraction_queue.pdfs_validated_not_integrated,
            "extraction_quality_mean": report.extraction_queue.extraction_quality_mean,
            "throughput_24h": report.extraction_queue.throughput_24h,
            "throughput_7d": report.extraction_queue.throughput_7d,
            "estimated_hours_to_clear": report.extraction_queue.estimated_hours_to_clear,
            "critical_backlog": report.extraction_queue.critical_backlog,
            "health_status": report.extraction_queue.health_status,
        },
        "panel_needs": [
            {
                "panel_type": rec.panel_type,
                "urgency": rec.urgency,
                "reason": rec.reason,
            }
            for rec in report.panel_needs
        ],
        "error_summary": {
            "error_count_24h": report.error_count_24h,
            "error_rate_trend": report.error_rate_trend,
            "most_common_error": report.most_common_error,
        },
    }


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="OVERSEER v2 Management Check",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Print management report
  python scripts/overseer_management_check.py \
    --overseer-db data/overseer.db \
    --web-db data/web.db

  # Export as JSON
  python scripts/overseer_management_check.py \
    --overseer-db data/overseer.db \
    --web-db data/web.db \
    --format json \
    --output report.json

  # With verbose logging
  python scripts/overseer_management_check.py \
    --overseer-db data/overseer.db \
    --web-db data/web.db \
    --verbose
        """
    )

    parser.add_argument("--overseer-db", required=True,
                       help="Path to overseer.db")
    parser.add_argument("--web-db", required=True,
                       help="Path to web.db")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                       help="Output format")
    parser.add_argument("--output", default=None,
                       help="Output file (default: stdout)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")

    args = parser.parse_args()

    setup_logging(args.verbose)
    logger.info("Starting OVERSEER v2 management check")

    # Verify databases exist
    overseer_db = Path(args.overseer_db)
    web_db = Path(args.web_db)

    if not overseer_db.exists():
        logger.error(f"Overseer DB not found: {overseer_db}")
        return 1

    if not web_db.exists():
        logger.error(f"Web DB not found: {web_db}")
        return 1

    try:
        # Run management check
        logger.info("Initializing management dashboard...")
        dashboard = ManagementDashboard(str(overseer_db), str(web_db))

        logger.info("Generating management report...")
        if args.format == "text":
            report_text = dashboard.management_check()
        else:
            report = dashboard.generate_management_report()
            report_text = json.dumps(report_to_json(report), indent=2)

        # Output
        if args.output:
            output_path = Path(args.output)
            logger.info(f"Writing report to {output_path}")
            output_path.write_text(report_text)
            print(f"Report written to {output_path}")
        else:
            print(report_text)

        logger.info("Management check complete")
        return 0

    except Exception as e:
        logger.error(f"Failed to run management check: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
