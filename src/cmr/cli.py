"""
CMR Command-Line Interface (Sprint 10 Task 3.9).

Usage:
    python -m src.cmr.cli evaluate \\
        --building-type research_institute \\
        --climate-zone 3C \\
        --ceiling-height 2.75 \\
        --floor-area 18.0 \\
        --illuminance 350 \\
        --noise 38 \\
        --occupant-age 35
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from src.cmr.building_eval import evaluate_building
from src.cmr.paper_eval import evaluate_paper
from src.cmr.paper_report import format_paper_report_text, generate_paper_report
from src.cmr.report import generate_report, format_report_text


def build_parser() -> argparse.ArgumentParser:
    """Construct the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="cmr",
        description="Cognitive-Mechanism-Referenced Building Assessment Tool",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # evaluate subcommand
    eval_parser = subparsers.add_parser(
        "evaluate",
        help="Evaluate a building against CMR templates",
    )

    # Building context arguments
    eval_parser.add_argument(
        "--building-type",
        type=str,
        default="generic",
        help="Building type (e.g., research_institute, office, school)",
    )
    eval_parser.add_argument(
        "--building-name",
        type=str,
        default=None,
        help="Name of the building being evaluated",
    )
    eval_parser.add_argument(
        "--climate-zone",
        type=str,
        default="4A",
        help="ASHRAE climate zone (e.g., 3C, 4A, 5B)",
    )

    # Measured features
    eval_parser.add_argument(
        "--ceiling-height",
        type=float,
        required=True,
        help="Ceiling height in meters",
    )
    eval_parser.add_argument(
        "--floor-area",
        type=float,
        required=True,
        help="Floor area in square meters",
    )
    eval_parser.add_argument(
        "--illuminance",
        type=float,
        default=None,
        help="Illuminance in lux",
    )
    eval_parser.add_argument(
        "--noise",
        type=float,
        default=None,
        help="Ambient noise level in dBA",
    )
    eval_parser.add_argument(
        "--window-area-ratio",
        type=float,
        default=None,
        help="Window-to-wall area ratio (0.0-1.0)",
    )
    eval_parser.add_argument(
        "--primary-material",
        type=str,
        default=None,
        help="Primary surface material (e.g., concrete, timber, glass)",
    )
    eval_parser.add_argument(
        "--secondary-material",
        type=str,
        default=None,
        help="Secondary surface material",
    )
    eval_parser.add_argument(
        "--has-nature-view",
        action="store_true",
        help="Building has a nature view",
    )
    eval_parser.add_argument(
        "--rt60",
        type=float,
        default=None,
        help="Reverberation time RT60 in seconds",
    )
    eval_parser.add_argument(
        "--view-content",
        type=str,
        default=None,
        help="View content type (e.g., ocean_horizon, interior_only)",
    )
    eval_parser.add_argument(
        "--privacy-visual",
        type=str,
        default=None,
        help="Visual privacy level (none, low, moderate, high)",
    )
    eval_parser.add_argument(
        "--privacy-acoustic",
        type=str,
        default=None,
        help="Acoustic privacy level (none, low, moderate, high)",
    )
    eval_parser.add_argument(
        "--density",
        type=float,
        default=None,
        help="Density in square meters per person",
    )
    eval_parser.add_argument(
        "--operative-temp",
        type=float,
        default=None,
        help="Operative temperature in Celsius",
    )

    # Occupant profile
    eval_parser.add_argument(
        "--occupant-age",
        type=int,
        default=35,
        help="Occupant age in years (default: 35)",
    )
    eval_parser.add_argument(
        "--cultural-context",
        type=str,
        default="Western",
        help="Cultural context (e.g., Western, East-Asian)",
    )

    # Output options
    eval_parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results in JSON format",
    )
    eval_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show per-template scores (not just domain summaries)",
    )
    eval_parser.add_argument(
        "--db-path",
        type=str,
        default="ae.db",
        help="Path to the SQLite database",
    )

    # evaluate-paper subcommand
    paper_parser = subparsers.add_parser(
        "evaluate-paper",
        help="Evaluate a paper's claims against CMR templates",
    )
    paper_parser.add_argument(
        "--claims",
        type=str,
        default=None,
        help="JSON array of structured claims",
    )
    paper_parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Path to JSON file containing claims array (or {'claims': [...]}).",
    )
    paper_parser.add_argument(
        "--text",
        type=str,
        default=None,
        help="Paper text for regex-based claim extraction.",
    )
    paper_parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results in JSON format",
    )
    paper_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Include raw evaluation details in output",
    )
    paper_parser.add_argument(
        "--db-path",
        type=str,
        default="ae.db",
        help="Path to the SQLite database",
    )

    return parser


def run_evaluate(args: argparse.Namespace) -> int:
    """Execute the evaluate subcommand."""
    building_context: dict[str, Any] = {
        "building_type": args.building_type,
        "climate_zone": args.climate_zone,
    }
    if args.building_name:
        building_context["building_name"] = args.building_name

    measured_features: dict[str, Any] = {
        "ceiling_height_m": args.ceiling_height,
        "floor_area_m2": args.floor_area,
    }

    # Add optional measured features if provided
    if args.illuminance is not None:
        measured_features["illuminance_lux"] = args.illuminance
    if args.noise is not None:
        measured_features["ambient_noise_dba"] = args.noise
    if args.window_area_ratio is not None:
        measured_features["window_area_ratio"] = args.window_area_ratio
    if args.primary_material is not None:
        measured_features["primary_material"] = args.primary_material
    if args.secondary_material is not None:
        measured_features["secondary_material"] = args.secondary_material
    if args.has_nature_view:
        measured_features["has_nature_view"] = True
    if args.rt60 is not None:
        measured_features["rt60_seconds"] = args.rt60
    if args.view_content is not None:
        measured_features["view_content"] = args.view_content
    if args.privacy_visual is not None:
        measured_features["privacy_visual"] = args.privacy_visual
    if args.privacy_acoustic is not None:
        measured_features["privacy_acoustic"] = args.privacy_acoustic
    if args.density is not None:
        measured_features["density_m2_per_person"] = args.density
    if args.operative_temp is not None:
        measured_features["operative_temp_c"] = args.operative_temp

    occupant_profile: dict[str, Any] = {
        "age": args.occupant_age,
        "cultural_context": args.cultural_context,
    }

    try:
        evaluation_result = evaluate_building(
            building_context=building_context,
            measured_features=measured_features,
            occupant_profile=occupant_profile,
            db_path=args.db_path,
        )
    except Exception as e:
        print(f"Error during evaluation: {e}", file=sys.stderr)
        return 1

    report = generate_report(evaluation_result)

    if args.verbose:
        report["activated_templates"] = evaluation_result.get("activated_templates", [])
        report["domain_details"] = evaluation_result.get("domain_scores", [])

    if args.json_output:
        print(json.dumps(report, indent=2, default=str))
    else:
        print(format_report_text(report))
        if args.verbose:
            print("\nActivated Templates:")
            for template_id in evaluation_result.get("activated_templates", []):
                print(f"  - {template_id}")
            print("\nDomain Details:")
            for domain in evaluation_result.get("domain_scores", []):
                templates_str = ", ".join(domain.get("template_ids", []))
                print(
                    f"  {domain['domain']}: WIS={domain['wis']:.1f}, "
                    f"n={domain.get('n_templates', 0)}, templates=[{templates_str}]"
                )

    return 0


def _load_structured_claims(args: argparse.Namespace) -> list[dict] | None:
    if args.claims:
        payload = json.loads(args.claims)
        if isinstance(payload, list):
            return payload
        raise ValueError("--claims must be a JSON array")

    if args.file:
        with open(args.file, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict) and isinstance(payload.get("claims"), list):
            return payload["claims"]
        raise ValueError("--file JSON must be an array or object with a 'claims' array")

    return None


def run_evaluate_paper(args: argparse.Namespace) -> int:
    """Execute the evaluate-paper subcommand."""
    if not args.claims and not args.file and not args.text:
        print(
            "Error: provide at least one input source (--claims, --file, or --text).",
            file=sys.stderr,
        )
        return 2

    try:
        structured_claims = _load_structured_claims(args)
        evaluation = evaluate_paper(
            paper_text=args.text or "",
            structured_claims=structured_claims,
            db_path=args.db_path,
        )
        report = generate_paper_report(evaluation)
    except Exception as exc:
        print(f"Error during paper evaluation: {exc}", file=sys.stderr)
        return 1

    if args.verbose:
        report["raw_evaluation"] = {
            "status": evaluation.get("status"),
            "steps": evaluation.get("steps", []),
            "findings": evaluation.get("findings", []),
            "template_system_updates": evaluation.get("template_system_updates", []),
            "report": evaluation.get("report", {}),
        }

    if args.json_output:
        print(json.dumps(report, indent=2, default=str))
    else:
        print(format_paper_report_text(report))

    return 0


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "evaluate":
        return run_evaluate(args)
    if args.command == "evaluate-paper":
        return run_evaluate_paper(args)

    print(f"Unknown command: {args.command}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
