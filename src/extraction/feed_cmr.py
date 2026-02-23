"""
Feed structured claims to CMR pipeline (Sprint D Task D.12).

Processes extracted claims through the CMR paper evaluation pipeline,
validates against gold standard, and produces integration report.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import sys
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.cmr.process_paper import (
    process_paper,
    ProcessingResult,
    format_processing_report,
)


def _load_structured_claims(claims_path: str) -> dict[str, Any]:
    """Load structured claims from JSON file."""
    with open(claims_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_gold_standard(gold_standard_dir: str) -> dict[str, dict[str, Any]]:
    """
    Load gold standard papers from directory.

    Returns dict mapping paper_id to gold standard data.
    """
    gold_dir = Path(gold_standard_dir)
    gold_papers: dict[str, dict[str, Any]] = {}

    # Check for main gold standard file
    main_file = gold_dir / "gold_standard_papers.json"
    if main_file.exists():
        with open(main_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            papers_list = data.get("papers", [])
            for paper in papers_list:
                paper_id = paper.get("paper_id")
                if paper_id:
                    gold_papers[paper_id] = paper

    # Also load individual paper JSON files
    for json_file in gold_dir.glob("*.json"):
        if json_file.name == "gold_standard_papers.json":
            continue
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                paper_data = json.load(f)
                paper_id = paper_data.get("paper_id")
                if paper_id:
                    # Merge with existing or add new
                    if paper_id in gold_papers:
                        gold_papers[paper_id].update(paper_data)
                    else:
                        gold_papers[paper_id] = paper_data
        except (json.JSONDecodeError, KeyError):
            continue

    return gold_papers


def _group_claims_by_paper(claims: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group claims by paper_id."""
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for claim in claims:
        paper_id = claim.get("paper_id", "unknown")
        groups[paper_id].append(claim)
    return groups


def _transform_claim_for_cmr(claim: dict[str, Any]) -> dict[str, Any]:
    """
    Transform a structured claim to CMR process_paper format.

    CMR process_paper expects claims with:
    - description: Text description
    - iv: Independent variable
    - dv: Dependent variable
    - direction: Effect direction
    - effect_size: Cohen's d (optional)
    - sample_n: Sample size (optional)
    """
    iv = claim.get("iv") or claim.get("iv_raw", "")
    dv = claim.get("dv") or claim.get("dv_raw", "")
    direction = claim.get("direction", "unknown")

    description = f"{iv} affects {dv}"
    if direction == "increase":
        description = f"{iv} increases {dv}"
    elif direction == "decrease":
        description = f"{iv} decreases {dv}"
    elif direction == "no_effect":
        description = f"{iv} has no significant effect on {dv}"

    return {
        "description": description,
        "iv": iv,
        "dv": dv,
        "direction": direction,
        "effect_size": claim.get("effect_size"),
        "sample_n": claim.get("sample_n"),
        "source": claim.get("source_quote", "")[:200],
        "context": claim.get("context"),
        "template_id": None,  # Will be matched by CMR
        "parameter_name": dv,
    }


def _validate_against_gold_standard(
    paper_id: str,
    result: ProcessingResult,
    gold_paper: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate CMR processing result against gold standard.

    Returns validation metrics.
    """
    validation = {
        "paper_id": paper_id,
        "gold_standard_available": True,
        "expected_templates": gold_paper.get("templates_expected", []),
        "matched_templates": [],
        "template_match_correct": False,
        "direction_correct": False,
        "notes": [],
    }

    # Extract templates from proposals
    for proposal in result.proposals_generated:
        if proposal.template_id and proposal.template_id != "SYSTEM":
            validation["matched_templates"].append(proposal.template_id)

    # Also check template_system_updates
    for update in result.template_system_updates:
        template = update.get("template")
        if template and template != "none":
            if template not in validation["matched_templates"]:
                validation["matched_templates"].append(template)

    # Check if expected templates were matched
    expected = set(gold_paper.get("templates_expected", []))
    matched = set(validation["matched_templates"])

    if expected and matched:
        overlap = expected & matched
        validation["template_match_correct"] = len(overlap) > 0
        validation["template_overlap"] = list(overlap)
        validation["template_precision"] = len(overlap) / len(matched) if matched else 0
        validation["template_recall"] = len(overlap) / len(expected) if expected else 0

    # Check direction from verified claims
    verified = gold_paper.get("verified_claims", [])
    if verified and result.template_system_updates:
        directions_match = 0
        for vc in verified:
            gold_dir = vc.get("direction")
            gold_iv = vc.get("iv")
            gold_dv = vc.get("dv")

            for update in result.template_system_updates:
                detail = update.get("detail", "")
                update_type = update.get("type", "")

                # Simple heuristic: check if IV/DV mentioned in detail
                if gold_iv and gold_iv in detail and gold_dv and gold_dv in detail:
                    directions_match += 1
                    break

        if verified:
            validation["direction_correct"] = directions_match > 0
            validation["direction_match_rate"] = directions_match / len(verified)

    return validation


def feed_claims_to_cmr(
    claims_path: str = "data/production/structured_claims.json",
    gold_standard_dir: str = "data/gold_standard/",
    db_path: str = "ae.db",
    limit: Optional[int] = None,
    persist_proposals: bool = False,
) -> dict[str, Any]:
    """
    Process all extracted claims through the CMR pipeline.

    Steps:
    1. Load structured claims from claims_path
    2. Group claims by paper_id
    3. For each paper: call process_paper() from CMR
    4. Collect: template matches, contradictions, confirmations, gaps, VOI
    5. Compare results against gold standard (where available)
    6. Return comprehensive report

    Args:
        claims_path: Path to structured_claims.json from D.10
        gold_standard_dir: Directory containing gold standard paper JSONs
        db_path: Path to ae.db database
        limit: Optional limit on number of papers to process
        persist_proposals: Whether to persist proposals to database

    Returns:
        Comprehensive integration report dict
    """
    # Load data
    claims_data = _load_structured_claims(claims_path)
    claims_list = claims_data.get("claims", [])

    if not claims_list:
        return {
            "status": "error",
            "message": "No claims found in structured_claims.json",
            "claims_path": claims_path,
        }

    gold_standards = _load_gold_standard(gold_standard_dir)

    # Group claims by paper
    paper_claims = _group_claims_by_paper(claims_list)
    paper_ids = list(paper_claims.keys())

    if limit:
        paper_ids = paper_ids[:limit]

    # Process each paper
    results: list[dict[str, Any]] = []
    validations: list[dict[str, Any]] = []

    totals = {
        "papers_processed": 0,
        "total_claims": 0,
        "claims_matched_to_templates": 0,
        "claims_unmatched": 0,
        "contradictions_found": 0,
        "confirmations_found": 0,
        "gaps_identified": 0,
        "proposals_generated": 0,
        "aggregate_voi": 0.0,
    }

    for paper_id in paper_ids:
        claims = paper_claims[paper_id]

        # Transform claims to CMR format
        cmr_claims = [_transform_claim_for_cmr(c) for c in claims]

        # Create citation from paper_id
        citation = paper_id
        doi = paper_id if paper_id.startswith("doi:") else None

        try:
            # Process through CMR pipeline
            result = process_paper(
                claims=cmr_claims,
                citation=citation,
                doi=doi,
                db_path=db_path,
                persist_proposals=persist_proposals,
                include_raw_evaluation=False,
            )

            # Collect metrics
            paper_result = {
                "paper_id": paper_id,
                "status": "success",
                "n_claims": result.n_claims,
                "n_matched": result.n_matched,
                "n_unmatched": result.n_unmatched,
                "n_contradictions": result.n_contradictions,
                "n_confirmations": result.n_confirmations,
                "n_gaps": result.n_gaps,
                "aggregate_voi": result.aggregate_voi,
                "proposals_count": len(result.proposals_generated),
                "recommendations": result.recommendations[:3] if result.recommendations else [],
            }

            # Update totals
            totals["papers_processed"] += 1
            totals["total_claims"] += result.n_claims
            totals["claims_matched_to_templates"] += result.n_matched
            totals["claims_unmatched"] += result.n_unmatched
            totals["contradictions_found"] += result.n_contradictions
            totals["confirmations_found"] += result.n_confirmations
            totals["gaps_identified"] += result.n_gaps
            totals["proposals_generated"] += len(result.proposals_generated)
            totals["aggregate_voi"] += result.aggregate_voi

            # Validate against gold standard if available
            if paper_id in gold_standards:
                validation = _validate_against_gold_standard(
                    paper_id, result, gold_standards[paper_id]
                )
                validations.append(validation)
                paper_result["gold_standard_validation"] = validation

            results.append(paper_result)

        except Exception as e:
            results.append({
                "paper_id": paper_id,
                "status": "error",
                "error": str(e),
            })

    # Compute gold standard summary
    gold_summary = {
        "papers_tested": len(validations),
        "template_match_accuracy": 0.0,
        "direction_accuracy": 0.0,
        "false_matches": 0,
        "missed_matches": 0,
    }

    if validations:
        template_correct = sum(1 for v in validations if v.get("template_match_correct", False))
        direction_correct = sum(1 for v in validations if v.get("direction_correct", False))

        gold_summary["template_match_accuracy"] = template_correct / len(validations)
        gold_summary["direction_accuracy"] = direction_correct / len(validations) if any(
            v.get("direction_correct") is not None for v in validations
        ) else 0.0

        # Count misses
        for v in validations:
            expected = set(v.get("expected_templates", []))
            matched = set(v.get("matched_templates", []))
            gold_summary["missed_matches"] += len(expected - matched)
            gold_summary["false_matches"] += len(matched - expected) if expected else 0

    # Build final report
    report = {
        "integration_date": datetime.now(timezone.utc).isoformat(),
        "claims_path": claims_path,
        "gold_standard_dir": gold_standard_dir,
        "db_path": db_path,
        **totals,
        "gold_standard_validation": gold_summary,
        "paper_results": results,
        "validations": validations,
    }

    return report


def format_integration_report(report: dict[str, Any]) -> str:
    """Format integration report as readable text."""
    lines = []
    lines.append("=" * 70)
    lines.append("CMR INTEGRATION REPORT (Sprint D Task D.12)")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"Integration Date: {report.get('integration_date', 'Unknown')}")
    lines.append(f"Claims Path: {report.get('claims_path', 'Unknown')}")
    lines.append("")

    lines.append("-" * 50)
    lines.append("PROCESSING SUMMARY")
    lines.append("-" * 50)
    lines.append(f"Papers processed: {report.get('papers_processed', 0)}")
    lines.append(f"Total claims: {report.get('total_claims', 0)}")
    lines.append(f"Claims matched to templates: {report.get('claims_matched_to_templates', 0)}")
    lines.append(f"Claims unmatched: {report.get('claims_unmatched', 0)}")
    lines.append("")
    lines.append(f"Contradictions found: {report.get('contradictions_found', 0)}")
    lines.append(f"Confirmations found: {report.get('confirmations_found', 0)}")
    lines.append(f"Gaps identified: {report.get('gaps_identified', 0)}")
    lines.append("")
    lines.append(f"Update proposals generated: {report.get('proposals_generated', 0)}")
    lines.append(f"Aggregate VOI: {report.get('aggregate_voi', 0):.2f}")
    lines.append("")

    gold = report.get("gold_standard_validation", {})
    if gold.get("papers_tested", 0) > 0:
        lines.append("-" * 50)
        lines.append("GOLD STANDARD VALIDATION")
        lines.append("-" * 50)
        lines.append(f"Papers tested: {gold.get('papers_tested', 0)}")
        lines.append(f"Template match accuracy: {gold.get('template_match_accuracy', 0):.1%}")
        lines.append(f"Direction accuracy: {gold.get('direction_accuracy', 0):.1%}")
        lines.append(f"False matches: {gold.get('false_matches', 0)}")
        lines.append(f"Missed matches: {gold.get('missed_matches', 0)}")
        lines.append("")

    # Show sample results
    paper_results = report.get("paper_results", [])
    if paper_results:
        lines.append("-" * 50)
        lines.append(f"PAPER RESULTS (showing first 5 of {len(paper_results)})")
        lines.append("-" * 50)
        for pr in paper_results[:5]:
            lines.append("")
            lines.append(f"Paper: {pr.get('paper_id', 'Unknown')}")
            lines.append(f"  Status: {pr.get('status', 'Unknown')}")
            if pr.get("status") == "success":
                lines.append(f"  Claims: {pr.get('n_claims', 0)} (matched: {pr.get('n_matched', 0)})")
                lines.append(f"  Contradictions: {pr.get('n_contradictions', 0)}, Confirmations: {pr.get('n_confirmations', 0)}")
                lines.append(f"  Proposals: {pr.get('proposals_count', 0)}, VOI: {pr.get('aggregate_voi', 0):.2f}")
            else:
                lines.append(f"  Error: {pr.get('error', 'Unknown error')}")

    lines.append("")
    lines.append("=" * 70)
    return "\n".join(lines)


def save_integration_report(
    report: dict[str, Any],
    output_path: str = "data/production/cmr_integration_report.json",
) -> None:
    """Save integration report to JSON file."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)


def main() -> None:
    """CLI for CMR integration."""
    parser = argparse.ArgumentParser(
        description="Feed structured claims to CMR pipeline (Sprint D Task D.12)"
    )
    parser.add_argument(
        "--claims-path",
        default="data/production/structured_claims.json",
        help="Path to structured claims JSON",
    )
    parser.add_argument(
        "--gold-standard-dir",
        default="data/gold_standard/",
        help="Directory with gold standard papers",
    )
    parser.add_argument(
        "--db-path",
        default="ae.db",
        help="Path to ae.db database",
    )
    parser.add_argument(
        "--output",
        default="data/production/cmr_integration_report.json",
        help="Output path for integration report",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of papers to process",
    )
    parser.add_argument(
        "--persist",
        action="store_true",
        help="Persist proposals to database",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed report",
    )

    args = parser.parse_args()

    # Check if claims file exists
    claims_path = Path(args.claims_path)
    if not claims_path.exists():
        # Try alternative paths
        alt_paths = [
            "data/production/structured_claims_codex.json",
            "data/production/structured_claims.json",
        ]
        for alt in alt_paths:
            if Path(alt).exists():
                args.claims_path = alt
                print(f"Using claims file: {alt}")
                break
        else:
            print(f"ERROR: Claims file not found: {args.claims_path}")
            print("D.12 requires D.10 (batch extraction) to be completed first.")
            print("Available files:", list(Path("data/production").glob("*.json")))
            return

    report = feed_claims_to_cmr(
        claims_path=args.claims_path,
        gold_standard_dir=args.gold_standard_dir,
        db_path=args.db_path,
        limit=args.limit,
        persist_proposals=args.persist,
    )

    save_integration_report(report, args.output)

    if args.verbose:
        print(format_integration_report(report))
    else:
        print(f"Papers processed: {report.get('papers_processed', 0)}")
        print(f"Total claims: {report.get('total_claims', 0)}")
        print(f"Claims matched: {report.get('claims_matched_to_templates', 0)}")
        print(f"Proposals generated: {report.get('proposals_generated', 0)}")
        gold = report.get("gold_standard_validation", {})
        if gold.get("papers_tested", 0) > 0:
            print(f"Gold standard accuracy: {gold.get('template_match_accuracy', 0):.1%}")
        print(f"\nReport saved to: {args.output}")


if __name__ == "__main__":
    main()
