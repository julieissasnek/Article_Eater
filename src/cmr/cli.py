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
from src.cmr.compare import compare_buildings
from src.cmr.paper_eval import evaluate_paper
from src.cmr.paper_report import format_paper_report_text, generate_paper_report
from src.cmr.report import generate_report, format_report_text
from src.cmr.quick_assess import quick_assess, format_quick_report
from src.cmr.sensitivity import analyze_sensitivity, format_sensitivity_report, get_quick_sensitivity


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

    # quick-assess subcommand (Tier A + optional Tier B)
    quick_parser = subparsers.add_parser(
        "quick-assess",
        help="Quick assessment using Tier A inputs, with optional Tier B measurements",
    )
    quick_parser.add_argument("--ceiling", type=float, help="Ceiling height in meters")
    quick_parser.add_argument("--area", type=float, help="Floor area in square meters")
    quick_parser.add_argument("--nature-view", type=str, help="View content (nature/urban/none)")
    quick_parser.add_argument("--wayfinding", action="store_true", help="Wayfinding is clear")
    quick_parser.add_argument("--walking-paths", action="store_true", help="Walking paths available")
    quick_parser.add_argument("--colors", type=str, help="Comma-separated wall colors")
    quick_parser.add_argument("--color-varied", action="store_true", help="Color varies through space")
    quick_parser.add_argument("--floor-surface", type=str, default="level", help="Floor surface type")
    quick_parser.add_argument("--stairs-standard", action="store_true", help="Stairs meet standards")
    quick_parser.add_argument("--thermal", type=str, help="Thermal system (operable_windows/hvac)")
    quick_parser.add_argument("--material", type=str, help="Primary material (wood/concrete/etc)")
    quick_parser.add_argument("--max-group", type=int, help="Maximum group size")
    quick_parser.add_argument("--illuminance", type=float, help="Tier B: measured illuminance (lux)")
    quick_parser.add_argument("--noise", type=float, help="Tier B: measured ambient noise (dBA)")
    quick_parser.add_argument("--rt60", type=float, help="Tier B: measured reverberation time (seconds)")
    quick_parser.add_argument("--age", type=int, default=35, help="Occupant age")
    quick_parser.add_argument("--json", action="store_true", dest="json_output", help="JSON output")

    # sensitivity subcommand
    sens_parser = subparsers.add_parser(
        "sensitivity",
        help="Analyze sensitivity of WIS to input features",
    )
    sens_parser.add_argument("--ceiling-height", type=float, help="Current ceiling height (m)")
    sens_parser.add_argument("--floor-area", type=float, help="Current floor area (m²)")
    sens_parser.add_argument("--illuminance", type=float, help="Current illuminance (lux)")
    sens_parser.add_argument("--noise", type=float, help="Current noise level (dBA)")
    sens_parser.add_argument("--window-area-ratio", type=float, help="Current window ratio")
    sens_parser.add_argument("--rt60", type=float, help="Current RT60 (seconds)")
    sens_parser.add_argument("--operative-temp", type=float, help="Current temperature (°C)")
    sens_parser.add_argument("--density", type=float, help="Current density (m²/person)")
    sens_parser.add_argument("--has-nature-view", action="store_true", help="Has nature view")
    sens_parser.add_argument("--primary-material", type=str, help="Primary material")
    sens_parser.add_argument("--age", type=int, default=35, help="Occupant age")
    sens_parser.add_argument("--quick", action="store_true", help="Quick heuristic analysis (faster)")
    sens_parser.add_argument("--no-diminishing", action="store_true", help="Skip diminishing returns check")
    sens_parser.add_argument("--db-path", type=str, default="ae.db", help="Path to database")
    sens_parser.add_argument("--json", action="store_true", dest="json_output", help="JSON output")

    compare_parser = subparsers.add_parser(
        "compare",
        help="Compare two building scenarios side by side",
    )
    compare_parser.add_argument("--a", type=str, required=True, help="JSON object for Building A features")
    compare_parser.add_argument("--b", type=str, required=True, help="JSON object for Building B features")
    compare_parser.add_argument(
        "--labels",
        nargs=2,
        metavar=("LABEL_A", "LABEL_B"),
        default=["Current", "Proposed"],
        help="Labels used for Building A and Building B",
    )
    compare_parser.add_argument("--age", type=int, default=35, help="Occupant age")
    compare_parser.add_argument("--db-path", type=str, default="ae.db", help="Path to database")
    compare_parser.add_argument("--json", action="store_true", dest="json_output", help="JSON output")

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


def run_quick_assess(args: argparse.Namespace) -> int:
    """Execute the quick-assess subcommand."""
    wall_colors = args.colors.split(",") if args.colors else None
    has_nature_view = args.nature_view is not None
    view_content = args.nature_view if args.nature_view else None

    result = quick_assess(
        ceiling_height_m=args.ceiling,
        floor_area_m2=args.area,
        has_nature_view=has_nature_view,
        view_content=view_content,
        walking_paths_available=args.walking_paths if hasattr(args, "walking_paths") else None,
        wayfinding_clear=args.wayfinding if hasattr(args, "wayfinding") else None,
        wall_colors=wall_colors,
        color_sequence_varied=args.color_varied if hasattr(args, "color_varied") else None,
        floor_surface=args.floor_surface,
        stair_dimensions_standard=args.stairs_standard if hasattr(args, "stairs_standard") else None,
        thermal_system=args.thermal,
        primary_material=args.material,
        max_group_size=args.max_group,
        illuminance_lux=args.illuminance,
        ambient_noise_dba=args.noise,
        rt60_seconds=args.rt60,
        occupant_age=args.age,
    )

    if args.json_output:
        output = {
            "overall_rating": result.overall_rating,
            "overall_wis": result.overall_wis,
            "template_scores": result.template_scores,
            "strengths": result.strengths,
            "deficits": result.deficits,
            "recommendations": result.recommendations,
            "tier_b_suggestions": result.tier_b_suggestions,
            "tier_mode": result.tier_mode,
            "tier_b_reveals": result.tier_b_reveals,
            "templates_assessed": result.templates_assessed,
            "templates_skipped": result.templates_skipped,
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_quick_report(result))

    return 0


def run_sensitivity(args: argparse.Namespace) -> int:
    """Execute the sensitivity subcommand."""
    measured_features: dict[str, Any] = {}

    if args.ceiling_height is not None:
        measured_features["ceiling_height_m"] = args.ceiling_height
    if args.floor_area is not None:
        measured_features["floor_area_m2"] = args.floor_area
    if args.illuminance is not None:
        measured_features["illuminance_lux"] = args.illuminance
    if args.noise is not None:
        measured_features["ambient_noise_dba"] = args.noise
    if args.window_area_ratio is not None:
        measured_features["window_area_ratio"] = args.window_area_ratio
    if args.rt60 is not None:
        measured_features["rt60_seconds"] = args.rt60
    if args.operative_temp is not None:
        measured_features["operative_temp_c"] = args.operative_temp
    if args.density is not None:
        measured_features["density_m2_per_person"] = args.density
    if args.has_nature_view:
        measured_features["has_nature_view"] = True
    if args.primary_material is not None:
        measured_features["primary_material"] = args.primary_material

    occupant_profile = {"age": args.age}

    if args.quick:
        # Quick heuristic analysis
        result = get_quick_sensitivity(measured_features, occupant_profile)
        if args.json_output:
            print(json.dumps(result, indent=2))
        else:
            print("=" * 50)
            print("QUICK SENSITIVITY ANALYSIS")
            print("=" * 50)
            print()
            print(f"Top recommendation: {result['top_recommendation']}")
            print()
            for i, rec in enumerate(result.get("recommendations", []), 1):
                print(f"{i}. {rec['recommendation']}")
                print(f"   Feature: {rec['feature']}")
                print(f"   Estimated impact: +{rec['estimated_impact']:.1f} WIS points")
                print()
        return 0

    try:
        result = analyze_sensitivity(
            measured_features=measured_features,
            occupant_profile=occupant_profile,
            db_path=args.db_path,
            check_diminishing=not args.no_diminishing,
        )
    except Exception as e:
        print(f"Error during sensitivity analysis: {e}", file=sys.stderr)
        return 1

    if args.json_output:
        output = {
            "baseline_wis": result.baseline_wis,
            "top_feature": result.top_feature,
            "top_delta": result.top_delta,
            "top_recommendation": result.top_recommendation,
            "category_impacts": result.category_impacts,
            "feature_sensitivities": [
                {
                    "rank": s.rank,
                    "feature": s.feature,
                    "description": s.description,
                    "category": s.category,
                    "wis_delta": s.wis_delta,
                    "worst_value": s.worst_value,
                    "best_value": s.best_value,
                    "unit": s.unit,
                    "diminishing_returns": s.diminishing_returns,
                    "diminishing_threshold": s.diminishing_threshold,
                }
                for s in result.feature_sensitivities
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_sensitivity_report(result))

    return 0


def run_compare(args: argparse.Namespace) -> int:
    """Execute the compare subcommand."""
    try:
        features_a = json.loads(args.a)
        features_b = json.loads(args.b)
        if not isinstance(features_a, dict) or not isinstance(features_b, dict):
            raise ValueError("--a and --b must be JSON objects.")

        result = compare_buildings(
            features_a=features_a,
            features_b=features_b,
            label_a=args.labels[0],
            label_b=args.labels[1],
            occupant_age=args.age,
            db_path=args.db_path,
        )
    except Exception as e:
        print(f"Error during comparison: {e}", file=sys.stderr)
        return 1

    if args.json_output:
        print(json.dumps(result, indent=2, default=str))
        return 0

    overall = result.get("overall", {})
    print("=" * 60)
    print("BUILDING COMPARISON")
    print("=" * 60)
    print(f"{args.labels[0]} overall WIS: {overall.get('a_wis', 0.0):.1f}")
    print(f"{args.labels[1]} overall WIS: {overall.get('b_wis', 0.0):.1f}")
    print(f"Delta ({args.labels[1]} - {args.labels[0]}): {overall.get('delta', 0.0):+.1f}")
    print("")
    print("Top Improvements:")
    for row in result.get("biggest_improvements", [])[:3]:
        print(f"- {row['domain']}: {row['delta']:+.1f}")
    print("")
    print("Top Regressions:")
    for row in result.get("biggest_regressions", [])[:3]:
        print(f"- {row['domain']}: {row['delta']:+.1f}")
    print("")
    print(result.get("summary", ""))
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
    if args.command == "quick-assess":
        return run_quick_assess(args)
    if args.command == "sensitivity":
        return run_sensitivity(args)
    if args.command == "compare":
        return run_compare(args)

    print(f"Unknown command: {args.command}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
