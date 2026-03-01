#!/usr/bin/env python3
"""
Expert Calibration Report Generator — Sprint 6
================================================
Generates a structured report for expert panel review of system baselines.

Usage:
  python scripts/generate_calibration_report.py
  python scripts/generate_calibration_report.py --output docs/EXPERT_CALIBRATION_REPORT.md
  python scripts/generate_calibration_report.py --json              # Output JSON instead of markdown

This script:
  1. Reads from overseer.db (latest health metrics, snapshots)
  2. Reads from web.db or beliefs DB (per-theory belief counts, coherence)
  3. Reads from extraction files (coverage statistics)
  4. Reads citation_graph.json if it exists (citation statistics)
  5. Generates markdown/JSON report with:
     - System Overview
     - Per-Theory Coherence Baselines
     - Proposed Alert Thresholds
     - Template Coverage Analysis
     - Community Structure (if available)
     - Citation Topology (if available)
     - VOI Gap Rankings
     - Proposed Thresholds for Panel Approval
     - Open Questions

Author: Claude Code (Article Eater CMR System)
Date: February 2026
"""

import argparse
import json
import logging
import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict

# Setup repo root
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ============================================================================
# Database Query Functions
# ============================================================================

class DatabaseReader:
    """Reads calibration data from overseer.db and web.db."""

    def __init__(self, overseer_db_path: Path, web_db_path: Path):
        self.overseer_db_path = overseer_db_path
        self.web_db_path = web_db_path

    def get_system_overview(self) -> Dict[str, Any]:
        """
        Get system overview: papers loaded, beliefs, constraints, theories.

        Returns:
            Dict with overview statistics
        """
        overview = {
            "total_papers": 0,
            "total_beliefs": 0,
            "total_constraints": 0,
            "total_theories": 0,
            "total_templates": 0,
        }

        try:
            with sqlite3.connect(str(self.web_db_path)) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Count papers
                cursor.execute("SELECT COUNT(DISTINCT paper_id) as count FROM beliefs")
                result = cursor.fetchone()
                if result:
                    overview["total_papers"] = result["count"]

                # Count beliefs
                cursor.execute("SELECT COUNT(*) as count FROM beliefs")
                result = cursor.fetchone()
                if result:
                    overview["total_beliefs"] = result["count"]

                # Count constraints
                cursor.execute("SELECT COUNT(*) as count FROM constraints")
                result = cursor.fetchone()
                if result:
                    overview["total_constraints"] = result["count"]

                # Count theories
                cursor.execute("SELECT COUNT(DISTINCT theory_id) as count FROM beliefs")
                result = cursor.fetchone()
                if result:
                    overview["total_theories"] = result["count"]

                # Count templates
                cursor.execute("SELECT COUNT(*) as count FROM templates")
                result = cursor.fetchone()
                if result:
                    overview["total_templates"] = result["count"]

        except Exception as e:
            logger.warning(f"Could not read system overview: {e}")

        return overview

    def get_per_theory_coherence_baselines(self) -> Dict[str, Dict[str, float]]:
        """
        Get per-theory coherence baselines: mean, std, min, max.

        Returns:
            Dict mapping theory_id -> {mean, std, min, max, count}
        """
        baselines = {}

        try:
            with sqlite3.connect(str(self.overseer_db_path)) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Get latest health metrics snapshot (schema: global_coherence, per_theory_coherence_json)
                cursor.execute("""
                    SELECT global_coherence, per_theory_coherence_json, coherence_delta
                    FROM overseer_health_metrics
                    ORDER BY timestamp DESC
                    LIMIT 1
                """)

                result = cursor.fetchone()
                if result:
                    baselines["global"] = {
                        "mean": result["global_coherence"] or 0.0,
                        "delta": result["coherence_delta"] or 0.0,
                    }

                    # Parse per-theory JSON if available
                    per_theory_json = result["per_theory_coherence_json"]
                    if per_theory_json:
                        import json as _json
                        per_theory = _json.loads(per_theory_json)
                        for theory_id, score in per_theory.items():
                            baselines[theory_id] = {"mean": score}

                # Get historical stats across all snapshots for std/min/max
                cursor.execute("""
                    SELECT
                        AVG(global_coherence) as coherence_mean,
                        MIN(global_coherence) as coherence_min,
                        MAX(global_coherence) as coherence_max,
                        COUNT(*) as count
                    FROM overseer_health_metrics
                    WHERE global_coherence IS NOT NULL
                """)
                hist = cursor.fetchone()
                if hist and hist["count"] and hist["count"] > 0:
                    baselines["global"]["min"] = hist["coherence_min"]
                    baselines["global"]["max"] = hist["coherence_max"]
                    baselines["global"]["count"] = hist["count"]

        except Exception as e:
            logger.warning(f"Could not read per-theory coherence baselines: {e}")

        return baselines

    def get_template_coverage(self) -> Dict[str, Any]:
        """
        Get template coverage analysis: which have evidence, which are orphans.

        Returns:
            Dict with coverage statistics
        """
        coverage = {
            "total_templates": 0,
            "templates_with_evidence": 0,
            "orphan_templates": 0,
            "coverage_percent": 0.0,
        }

        try:
            with sqlite3.connect(str(self.web_db_path)) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Count total templates (try discovery_templates, fall back to templates)
                for table in ["discovery_templates", "templates"]:
                    try:
                        cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                        result = cursor.fetchone()
                        if result:
                            coverage["total_templates"] = result["count"]
                        break
                    except sqlite3.OperationalError:
                        continue

                # Count templates with beliefs (join on paper_id as proxy)
                try:
                    cursor.execute("""
                        SELECT COUNT(DISTINCT paper_id) as count
                        FROM beliefs
                        WHERE paper_id IS NOT NULL
                    """)
                    result = cursor.fetchone()
                    if result:
                        coverage["templates_with_evidence"] = result["count"]
                except sqlite3.OperationalError:
                    pass

                # Orphan templates (no beliefs)
                coverage["orphan_templates"] = (
                    coverage["total_templates"] - coverage["templates_with_evidence"]
                )

                # Coverage percent
                if coverage["total_templates"] > 0:
                    coverage["coverage_percent"] = (
                        100.0 * coverage["templates_with_evidence"] / coverage["total_templates"]
                    )

        except Exception as e:
            logger.warning(f"Could not read template coverage: {e}")

        return coverage

    def get_citation_graph_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get citation graph statistics if citation_graph.json exists.

        Returns:
            Dict with citation statistics or None
        """
        citation_graph_path = REPO_ROOT / "citation_graph.json"

        if not citation_graph_path.exists():
            return None

        try:
            with open(citation_graph_path, "r") as f:
                citation_graph = json.load(f)

            stats = {
                "nodes": len(citation_graph.get("nodes", [])),
                "edges": len(citation_graph.get("edges", [])),
                "densest_communities": [],
            }

            # Find densest communities (if community data available)
            nodes = citation_graph.get("nodes", [])
            communities = defaultdict(int)
            for node in nodes:
                if "community" in node:
                    communities[node["community"]] += 1

            # Top communities
            top_communities = sorted(communities.items(), key=lambda x: x[1], reverse=True)[:5]
            stats["densest_communities"] = [
                {"community_id": c[0], "member_count": c[1]} for c in top_communities
            ]

            return stats

        except Exception as e:
            logger.warning(f"Could not read citation graph: {e}")
            return None

    def get_voi_gap_rankings(self) -> List[Dict[str, Any]]:
        """
        Get top VOI gaps for research prioritization.

        Returns:
            List of top gaps with VOI scores
        """
        gaps = []

        try:
            # Try discovery_funnel gaps from web DB
            with sqlite3.connect(str(self.web_db_path)) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Try multiple possible table names for gap data
                for table_query in [
                    "SELECT gap_id, theory_id, description, voi_score FROM discovery_gaps ORDER BY voi_score DESC LIMIT 10",
                    "SELECT gap_id, theory_id, description, voi_score FROM gaps ORDER BY voi_score DESC LIMIT 10",
                ]:
                    try:
                        cursor.execute(table_query)
                        for row in cursor.fetchall():
                            gaps.append({
                                "gap_id": row["gap_id"],
                                "theory_id": row["theory_id"],
                                "description": row["description"],
                                "voi_score": row["voi_score"],
                            })
                        break  # Found the table
                    except sqlite3.OperationalError:
                        continue

            # If no DB table exists, try loading from discovery funnel service
            if not gaps:
                try:
                    from src.services.discovery_funnel import DiscoveryFunnelService
                    funnel = DiscoveryFunnelService(db_path=str(self.web_db_path))
                    if hasattr(funnel, 'get_top_gaps'):
                        raw_gaps = funnel.get_top_gaps(limit=10)
                        for g in raw_gaps:
                            gaps.append({
                                "gap_id": getattr(g, 'gap_id', str(g)),
                                "theory_id": getattr(g, 'theory_id', ''),
                                "description": getattr(g, 'description', str(g)),
                                "voi_score": getattr(g, 'voi_score', 0.0),
                            })
                except (ImportError, Exception):
                    pass

        except Exception as e:
            logger.info(f"Could not read VOI gaps: {e}")

        return gaps

    def get_quarantine_queue(self) -> List[Dict[str, Any]]:
        """
        Get current quarantine queue.

        Returns:
            List of quarantined beliefs
        """
        queue = []

        try:
            # Quarantine state is in overseer.db (per O-7 Parnas information hiding)
            with sqlite3.connect(str(self.overseer_db_path)) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT belief_id, reason, status, quarantined_at,
                           review_deadline, original_credence
                    FROM overseer_quarantine
                    WHERE status = 'QUARANTINED'
                    ORDER BY quarantined_at DESC
                    LIMIT 20
                """)

                for row in cursor.fetchall():
                    queue.append({
                        "belief_id": row["belief_id"],
                        "reason": row["reason"],
                        "status": row["status"],
                        "quarantined_at": row["quarantined_at"],
                        "review_deadline": row["review_deadline"],
                        "original_credence": row["original_credence"],
                    })

        except Exception as e:
            logger.warning(f"Could not read quarantine queue: {e}")

        return queue


# ============================================================================
# Report Generation
# ============================================================================

def generate_markdown_report(data: Dict[str, Any]) -> str:
    """Generate markdown format calibration report."""

    lines = []

    # Header
    lines.append("# Expert Calibration Report")
    lines.append("")
    lines.append(f"**Generated**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append("")

    # Section 1: System Overview
    lines.append("## 1. System Overview")
    lines.append("")
    overview = data["system_overview"]
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| Papers Loaded | {overview['total_papers']} |")
    lines.append(f"| Total Beliefs | {overview['total_beliefs']} |")
    lines.append(f"| Constraints | {overview['total_constraints']} |")
    lines.append(f"| Theories | {overview['total_theories']} |")
    lines.append(f"| Templates | {overview['total_templates']} |")
    lines.append("")

    # Section 2: Per-Theory Coherence Baselines
    lines.append("## 2. Per-Theory Coherence Baselines")
    lines.append("")
    lines.append(
        "These baselines establish the normal range of coherence for each theory. "
        "Used for statistical alerting (O-2: mean ± 1σ detection)."
    )
    lines.append("")

    baselines = data["per_theory_coherence"]
    if baselines:
        lines.append("| Theory | Mean | Std Dev | Min | Max |")
        lines.append("|--------|------|---------|-----|-----|")
        for theory_id, stats in baselines.items():
            lines.append(
                f"| {theory_id} | {stats.get('mean', 'N/A'):.3f} | "
                f"{stats.get('std', 'N/A'):.3f} | {stats.get('min', 'N/A'):.3f} | "
                f"{stats.get('max', 'N/A'):.3f} |"
            )
    else:
        lines.append("*No per-theory baseline data available yet.*")

    lines.append("")

    # Section 3: Template Coverage
    lines.append("## 3. Template Coverage Analysis")
    lines.append("")
    coverage = data["template_coverage"]
    lines.append(f"- **Total Templates**: {coverage['total_templates']}")
    lines.append(f"- **With Evidence**: {coverage['templates_with_evidence']}")
    lines.append(f"- **Orphan Templates**: {coverage['orphan_templates']}")
    lines.append(f"- **Coverage**: {coverage['coverage_percent']:.1f}%")
    lines.append("")

    # Section 4: Citation Topology
    lines.append("## 4. Citation Topology")
    lines.append("")
    citation_stats = data.get("citation_graph_stats")
    if citation_stats:
        lines.append(f"- **Papers (Nodes)**: {citation_stats['nodes']}")
        lines.append(f"- **Citation Links (Edges)**: {citation_stats['edges']}")

        if citation_stats.get("densest_communities"):
            lines.append("- **Densest Communities**:")
            for comm in citation_stats["densest_communities"]:
                lines.append(f"  - Community {comm['community_id']}: {comm['member_count']} members")
    else:
        lines.append("*Citation graph data not available.*")

    lines.append("")

    # Section 5: VOI Gap Rankings
    lines.append("## 5. Research Prioritization: Top VOI Gaps")
    lines.append("")
    voi_gaps = data.get("voi_gap_rankings", [])
    if voi_gaps:
        lines.append("| Gap ID | Theory | VOI Score | Description |")
        lines.append("|--------|--------|-----------|-------------|")
        for gap in voi_gaps[:10]:
            desc = (gap["description"][:40] + "...") if len(gap["description"]) > 40 else gap["description"]
            lines.append(
                f"| {gap['gap_id'][:10]} | {gap['theory_id']} | "
                f"{gap['voi_score']:.3f} | {desc} |"
            )
    else:
        lines.append("*No VOI gap data available.*")

    lines.append("")

    # Section 6: Quarantine Status
    lines.append("## 6. Quarantine Queue Status")
    lines.append("")
    quarantine_queue = data.get("quarantine_queue", [])
    lines.append(f"- **Beliefs in Quarantine**: {len(quarantine_queue)}")
    if quarantine_queue:
        lines.append("- **Sample (first 5)**:")
        for belief in quarantine_queue[:5]:
            lines.append(
                f"  - {belief['belief_id'][:20]}: {belief['theory_id']} "
                f"({belief['quarantine_timestamp'][:10]})"
            )
    lines.append("")

    # Section 7: Proposed Thresholds for Panel Approval
    lines.append("## 7. Proposed Thresholds for Panel Approval")
    lines.append("")
    lines.append("These thresholds guide OVERSEER alerting (decision O-2). Recommend panel review.")
    lines.append("")
    lines.append("| Invariant | Threshold | Rationale |")
    lines.append("|-----------|-----------|-----------|")
    lines.append("| INV-4 Coherence Decline | ≤ 5% | Dijkstra degradation control |")
    lines.append("| INV-0 Operational State | Required | No bootstrap failures |")
    lines.append("| INV-1 Provenance | 100% | Haack foundherentism |")
    lines.append("| INV-2 BN-Web Sync | ≥ 99% | Pearl edge integrity |")
    lines.append("| Alert Window | mean ± 1σ | O-2 statistical detection |")
    lines.append("| Quarantine Review | 7 days | O-3 human review deadline |")
    lines.append("")

    # Section 8: Open Questions
    lines.append("## 8. Open Questions for Panel Discussion")
    lines.append("")
    lines.append("### Q1: Coherence Temporal Dynamics")
    lines.append(
        "Should coherence warrants decay over time? Currently using Quinean static model."
    )
    lines.append("- **Options**: Yes (Bayesian temporal), No (Quinean static)")
    lines.append("")

    lines.append("### Q2: Multi-Theory Constraint Propagation")
    lines.append(
        "When a belief spans multiple theories, how should constraint violations propagate?"
    )
    lines.append("- **Options**: Full propagation, Isolated per-theory, Consensus-based")
    lines.append("")

    lines.append("### Q3: Community Detection Weighting")
    lines.append(
        "Should citation community membership affect belief baselines and alerts?"
    )
    lines.append("- **Options**: Yes (dynamic per-community), No (global baseline only)")
    lines.append("")

    lines.append("### Q4: Orphan Template Remediation")
    lines.append(
        f"Current orphan count: {coverage['orphan_templates']}. How should we address?"
    )
    lines.append("- **Options**: Prioritize evidence collection, Retire templates, Mark as TBD")
    lines.append("")

    return "\n".join(lines)


def generate_json_report(data: Dict[str, Any]) -> str:
    """Generate JSON format calibration report."""
    return json.dumps(data, indent=2)


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point."""

    parser = argparse.ArgumentParser(
        description="Generate expert calibration report for panel review",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--output",
        type=Path,
        help="Output file path (default: docs/EXPERT_CALIBRATION_REPORT_YYYY-MM-DD.md)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of markdown",
    )
    parser.add_argument(
        "--overseer-db",
        type=Path,
        help="Path to overseer.db (auto-detected if not specified)",
    )
    parser.add_argument(
        "--web-db",
        type=Path,
        help="Path to web.db (auto-detected if not specified)",
    )

    args = parser.parse_args()

    logger.info("Generating expert calibration report...")

    # Auto-detect databases
    overseer_db_path = args.overseer_db
    web_db_path = args.web_db

    if not overseer_db_path:
        candidates = [
            REPO_ROOT / "overseer.db",
            REPO_ROOT / "data" / "overseer.db",
        ]
        for candidate in candidates:
            if candidate.exists():
                overseer_db_path = candidate
                break

    if not web_db_path:
        candidates = [
            REPO_ROOT / "web.db",
            REPO_ROOT / "data" / "web.db",
        ]
        for candidate in candidates:
            if candidate.exists():
                web_db_path = candidate
                break

    if not overseer_db_path or not overseer_db_path.exists():
        logger.error(f"overseer.db not found")
        return 1

    if not web_db_path or not web_db_path.exists():
        logger.error(f"web.db not found")
        return 1

    logger.info(f"Using overseer.db: {overseer_db_path}")
    logger.info(f"Using web.db: {web_db_path}")

    # Read data
    reader = DatabaseReader(overseer_db_path, web_db_path)

    report_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system_overview": reader.get_system_overview(),
        "per_theory_coherence": reader.get_per_theory_coherence_baselines(),
        "template_coverage": reader.get_template_coverage(),
        "citation_graph_stats": reader.get_citation_graph_stats(),
        "voi_gap_rankings": reader.get_voi_gap_rankings(),
        "quarantine_queue": reader.get_quarantine_queue(),
    }

    logger.info(f"Data collected: {report_data['system_overview']['total_beliefs']} beliefs")

    # Generate report
    if args.json:
        report_content = generate_json_report(report_data)
        output_ext = ".json"
    else:
        report_content = generate_markdown_report(report_data)
        output_ext = ".md"

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        output_path = REPO_ROOT / "docs" / f"EXPERT_CALIBRATION_REPORT_{timestamp}{output_ext}"

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write report
    with open(output_path, "w") as f:
        f.write(report_content)

    logger.info(f"Report written to {output_path}")
    print(f"\nCalibration report saved to: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
