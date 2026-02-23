"""
Query CLI (MVP-3)
=================

Created: 2026-02-11
Owner: Terminal 2

Command-line interface for querying the Article Eater knowledge base.

Usage:
    python -m src.cli.query "What affects attention?"
    python -m src.cli.query "Does natural light improve productivity?" --mode detail
    python -m src.cli.query "What factors affect stress?" --gaps --output results.json

Options:
    --mode: Response mode (headline, summary, detail, deep_dive) [default: summary]
    --gaps: Include gap analysis in response
    --output: Write response to JSON file instead of stdout
    --format: Output format (pretty, json, minimal) [default: pretty]
    --max-results: Maximum beliefs to return [default: 10]
    --min-credence: Minimum credence threshold [default: 0.3]
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.services.query_engine import QueryEngine


def format_pretty(response: dict) -> str:
    """Format response for human-readable output."""
    lines = []

    # Status line
    status = response.get("status", "unknown")
    if status == "success":
        lines.append("\033[92m[SUCCESS]\033[0m")
    elif status == "partial":
        lines.append("\033[93m[PARTIAL]\033[0m")
    elif status == "no_results":
        lines.append("\033[93m[NO RESULTS]\033[0m")
    elif status == "error":
        lines.append("\033[91m[ERROR]\033[0m")
    else:
        lines.append(f"[{status.upper()}]")

    lines.append("")

    # Headline (always present)
    headline = response.get("headline", "No headline")
    lines.append(f"\033[97m{headline}\033[0m")
    lines.append("")

    # Summary (if present)
    summary = response.get("summary")
    if summary:
        lines.append("\033[96m--- Key Evidence ---\033[0m")
        for i, ev in enumerate(summary.get("key_evidence", [])[:5], 1):
            credence = ev.get("credence", 0)
            uncertainty = ev.get("uncertainty", 0)
            content = ev.get("content", "")[:100]
            causal = " [CAUSAL]" if ev.get("is_causal") else ""
            caution = " [!]" if ev.get("needs_caution") else ""
            lines.append(f"  {i}. {content}...")
            lines.append(f"     Credence: {credence:.2f} +/- {uncertainty:.2f}{causal}{caution}")

        lines.append("")

        # Scope conditions
        scope = summary.get("scope_conditions")
        if scope:
            lines.append("\033[96m--- Scope ---\033[0m")
            for k, v in scope.items():
                lines.append(f"  {k}: {v}")
            lines.append("")

        # Practical implications
        implications = summary.get("practical_implications", [])
        if implications and implications[0] != "See evidence for actionable insights":
            lines.append("\033[96m--- Implications ---\033[0m")
            for impl in implications:
                lines.append(f"  - {impl}")
            lines.append("")

        # Caveats
        caveats = summary.get("caveats", [])
        if caveats and caveats[0] != "Standard caveats apply to all evidence":
            lines.append("\033[93m--- Caveats ---\033[0m")
            for caveat in caveats:
                lines.append(f"  - {caveat}")
            lines.append("")

    # Gaps (if present)
    gaps = response.get("gaps")
    if gaps:
        n_gaps = gaps.get("n_gaps", 0)
        lines.append(f"\033[96m--- Knowledge Gaps ({n_gaps}) ---\033[0m")
        for gap in gaps.get("top_gaps", [])[:3]:
            gap_type = gap.get("gap_type", "unknown")
            desc = gap.get("description", "")
            priority = gap.get("priority", 0)
            lines.append(f"  [{gap_type.upper()}] {desc}")
            lines.append(f"    Priority: {priority:.2f}")
            if gap.get("suggested_search"):
                lines.append(f"    Suggested: {gap['suggested_search']}")
        lines.append("")

    # Follow-ups (if present)
    follow_ups = response.get("follow_ups", [])
    if follow_ups:
        lines.append("\033[96m--- Follow-up Questions ---\033[0m")
        for fu in follow_ups:
            fu_type = fu.get("type", "")
            question = fu.get("question", "")
            lines.append(f"  [{fu_type}] {question}")
        lines.append("")

    # Error (if present)
    error = response.get("error")
    if error:
        lines.append(f"\033[91mError: {error.get('code')}: {error.get('message')}\033[0m")

    # Metadata
    metadata = response.get("metadata", {})
    if metadata:
        lines.append("\033[90m---")
        lines.append(f"Query: {metadata.get('query_type', 'unknown')} | "
                    f"Causal level: {metadata.get('causal_level', 'unknown')} | "
                    f"Searched: {metadata.get('n_beliefs_searched', 0)} | "
                    f"Matched: {metadata.get('n_beliefs_matched', 0)} | "
                    f"Time: {metadata.get('processing_time_ms', 0)}ms\033[0m")

    return "\n".join(lines)


def format_minimal(response: dict) -> str:
    """Format response as minimal one-line output."""
    status = response.get("status", "unknown")
    headline = response.get("headline", "No result")
    n_matched = response.get("metadata", {}).get("n_beliefs_matched", 0)
    return f"[{status}] {headline} ({n_matched} beliefs)"


def main():
    parser = argparse.ArgumentParser(
        description="Query the Article Eater knowledge base",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.cli.query "What affects attention?"
  python -m src.cli.query "Does light affect mood?" --mode detail
  python -m src.cli.query "What do we know about stress?" --gaps
  python -m src.cli.query "nature and well-being" --format json --output results.json
        """
    )

    parser.add_argument(
        "query",
        help="Natural language query"
    )

    parser.add_argument(
        "--mode",
        choices=["headline", "summary", "detail", "deep_dive"],
        default="summary",
        help="Response detail level (default: summary)"
    )

    parser.add_argument(
        "--gaps",
        action="store_true",
        help="Include knowledge gap analysis"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file (JSON format)"
    )

    parser.add_argument(
        "--format", "-f",
        choices=["pretty", "json", "minimal"],
        default="pretty",
        help="Output format (default: pretty)"
    )

    parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="Maximum beliefs to return (default: 10)"
    )

    parser.add_argument(
        "--min-credence",
        type=float,
        default=0.3,
        help="Minimum credence threshold (default: 0.3)"
    )

    args = parser.parse_args()

    # Create query engine
    try:
        engine = QueryEngine()
    except Exception as e:
        print(f"\033[91mError initializing query engine: {e}\033[0m", file=sys.stderr)
        sys.exit(1)

    # Run query
    try:
        response = engine.query(
            query_text=args.query,
            response_mode=args.mode,
            include_gaps=args.gaps,
            max_results=args.max_results,
            min_credence=args.min_credence
        )
    except Exception as e:
        print(f"\033[91mError executing query: {e}\033[0m", file=sys.stderr)
        sys.exit(1)

    # Format output
    if args.format == "json":
        output = json.dumps(response, indent=2)
    elif args.format == "minimal":
        output = format_minimal(response)
    else:
        output = format_pretty(response)

    # Write output
    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            if args.format != "json":
                # Always write JSON to file
                json.dump(response, f, indent=2)
            else:
                f.write(output)
        print(f"Results written to {output_path}")
    else:
        print(output)


if __name__ == "__main__":
    main()
