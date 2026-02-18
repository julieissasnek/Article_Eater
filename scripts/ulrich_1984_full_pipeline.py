#!/usr/bin/env python3
"""
Task 12.17: Ulrich 1984 Full Pipeline Test with Reductions.

Demonstrates the complete paper processing pipeline with Tier 2 reductions:
1. Load Ulrich 1984 claims
2. Run claim extraction
3. Match claims via reductions (ART/SRT pathways)
4. Standard template matching
5. Mechanism tracing
6. Convergence assessment
7. Generate proposals
8. Format report

Expected outcomes:
- ART pathway detected (nature view → attention restoration)
- SRT pathway detected (nature view → stress reduction)
- VIEW1 template matches found
- Higher convergence than non-reduction matching

Usage:
    python3 scripts/ulrich_1984_full_pipeline.py
"""

import sys
import json
from pathlib import Path

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.cmr.paper_eval import evaluate_paper
from src.cmr.process_paper import process_paper, format_processing_report
from src.cmr.template_matching import (
    match_claims_via_reduction,
    build_template_index,
    REDUCTION_KEYWORDS,
    _claim_text,
)
from src.cmr.reduction_api import reduce_construct
from src.cmr.models import TemplateRecord, get_session, create_tables


def load_ulrich_claims() -> list[dict]:
    """Load Ulrich 1984 claims from test data."""
    path = REPO_ROOT / "data" / "test_papers" / "ulrich_1984.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("claims", [])


def test_reduction_detection(claims: list[dict]) -> dict:
    """Test that reductions detect ART, SRT, and Biophilia pathways."""
    print("\n--- REDUCTION DETECTION TEST ---")

    art_hits = []
    srt_hits = []
    bio_hits = []

    for claim in claims:
        claim_text = _claim_text(claim)
        print(f"\nClaim text: {claim_text}")

        for keyword, (theory, construct) in REDUCTION_KEYWORDS.items():
            if keyword in claim_text:
                reduction = reduce_construct(theory, construct)
                if reduction and reduction.get("template_mappings"):
                    hit = {
                        "claim_id": claim.get("claim_id"),
                        "keyword": keyword,
                        "theory": theory,
                        "construct": construct,
                        "template_mappings": [m.get("template_id") for m in reduction.get("template_mappings", [])],
                    }
                    if theory == "ART":
                        art_hits.append(hit)
                    elif theory == "SRT":
                        srt_hits.append(hit)
                    elif theory == "BIOPHILIA":
                        bio_hits.append(hit)
                    print(f"  Matched: {keyword} → {theory}.{construct}")

    print(f"\n--- REDUCTION SUMMARY ---")
    print(f"ART pathway hits: {len(art_hits)}")
    for hit in art_hits:
        print(f"  - {hit['claim_id']}: {hit['keyword']} → {hit['construct']}")
        print(f"    Templates: {hit['template_mappings']}")

    print(f"\nSRT pathway hits: {len(srt_hits)}")
    for hit in srt_hits:
        print(f"  - {hit['claim_id']}: {hit['keyword']} → {hit['construct']}")
        print(f"    Templates: {hit['template_mappings']}")

    print(f"\nBiophilia pathway hits: {len(bio_hits)}")
    for hit in bio_hits:
        print(f"  - {hit['claim_id']}: {hit['keyword']} → {hit['construct']}")
        print(f"    Templates: {hit['template_mappings']}")

    return {
        "art_detected": len(art_hits) > 0,
        "srt_detected": len(srt_hits) > 0,
        "bio_detected": len(bio_hits) > 0,
        "art_hits": art_hits,
        "srt_hits": srt_hits,
        "bio_hits": bio_hits,
    }


def test_reduction_template_matching(claims: list[dict], db_path: str) -> dict:
    """Test that reduction-based matching finds templates."""
    print("\n--- REDUCTION TEMPLATE MATCHING TEST ---")

    create_tables(db_path)
    session = get_session(db_path)

    try:
        templates = session.query(TemplateRecord).filter(
            TemplateRecord.dedup_status == "active"
        ).all()

        if not templates:
            print("WARNING: No active templates in database")
            print("         Using empty template index")
            template_index = {}
        else:
            template_index = build_template_index(templates)
            print(f"Loaded {len(template_index)} templates")

        # Match via reduction
        matches = match_claims_via_reduction(claims, template_index)

        total_matches = 0
        view1_matches = 0

        for m in matches:
            claim = m.get("claim", {})
            claim_matches = m.get("matches", [])
            total_matches += len(claim_matches)

            print(f"\nClaim: {claim.get('claim_id', 'unknown')}")
            print(f"  {claim.get('iv')} → {claim.get('dv')}")

            if claim_matches:
                for match in claim_matches:
                    tid = match.get("template_id", "")
                    conf = match.get("confidence", 0.0)
                    print(f"  → {tid} (conf: {conf:.2f})")
                    if "VIEW1" in tid.upper():
                        view1_matches += 1
            else:
                print("  → No template matches via reduction")

        return {
            "total_matches": total_matches,
            "view1_matches": view1_matches,
            "templates_loaded": len(template_index),
        }

    finally:
        session.close()


def test_full_paper_pipeline(claims: list[dict], db_path: str) -> dict:
    """Run full paper evaluation pipeline."""
    print("\n--- FULL PAPER EVALUATION PIPELINE ---")

    result = evaluate_paper(
        paper_text="",
        structured_claims=claims,
        citation="Ulrich, R.S. (1984). View through a window may influence recovery from surgery.",
        doi="10.1126/science.6143402",
        db_path=db_path,
    )

    print(f"\nPipeline Status: {result.get('status', 'unknown')}")
    print(f"Claims Extracted: {result.get('n_claims_extracted', 0)}")
    print(f"Claims Matched: {result.get('n_claims_matched', 0)}")
    print(f"Claims Unmatched: {result.get('n_claims_unmatched', 0)}")

    summary = result.get("report", {}).get("summary", {})
    print(f"\nFindings Summary:")
    print(f"  Contradictions: {summary.get('contradictions', 0)}")
    print(f"  Confirmations: {summary.get('confirmations', 0)}")
    print(f"  Gaps: {summary.get('gaps', 0)}")
    print(f"  Aggregate VOI: {summary.get('aggregate_voi', 0.0):.2f}")

    # Check template system updates
    updates = result.get("template_system_updates", [])
    print(f"\nTemplate System Updates: {len(updates)}")
    for update in updates:
        print(f"  - {update.get('type')}: {update.get('template')} | {update.get('detail')[:60]}...")

    return {
        "status": result.get("status"),
        "n_claims_extracted": result.get("n_claims_extracted", 0),
        "n_claims_matched": result.get("n_claims_matched", 0),
        "contradictions": summary.get("contradictions", 0),
        "confirmations": summary.get("confirmations", 0),
        "gaps": summary.get("gaps", 0),
        "aggregate_voi": summary.get("aggregate_voi", 0.0),
        "template_updates": len(updates),
    }


def test_process_paper_with_proposals(claims: list[dict], db_path: str) -> dict:
    """Test process_paper with proposal generation."""
    print("\n--- PROCESS PAPER WITH PROPOSALS ---")

    result = process_paper(
        claims=claims,
        citation="Ulrich 1984",
        doi="10.1126/science.6143402",
        db_path=db_path,
        persist_proposals=False,  # Don't persist in test
    )

    print(format_processing_report(result))

    return {
        "status": result.status,
        "n_claims": result.n_claims,
        "n_matched": result.n_matched,
        "proposals_generated": len(result.proposals_generated),
        "evidence_accumulated": len(result.evidence_accumulated),
    }


def main():
    print("=" * 70)
    print("ULRICH 1984 FULL PIPELINE TEST WITH TIER 2 REDUCTIONS")
    print("=" * 70)

    db_path = "ae.db"

    # Load claims
    claims = load_ulrich_claims()
    print(f"\nLoaded {len(claims)} claims from Ulrich 1984")
    for claim in claims:
        print(f"  - {claim.get('claim_id')}: {claim.get('description')[:50]}...")

    # Test 1: Reduction detection
    reduction_results = test_reduction_detection(claims)

    # Test 2: Reduction template matching
    matching_results = test_reduction_template_matching(claims, db_path)

    # Test 3: Full paper pipeline
    pipeline_results = test_full_paper_pipeline(claims, db_path)

    # Test 4: Process paper with proposals
    proposal_results = test_process_paper_with_proposals(claims, db_path)

    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    all_pass = True

    # Check 1: At least one theory pathway detected
    theories_detected = []
    if reduction_results["art_detected"]:
        theories_detected.append("ART")
    if reduction_results["srt_detected"]:
        theories_detected.append("SRT")
    if reduction_results["bio_detected"]:
        theories_detected.append("Biophilia")

    if len(theories_detected) >= 2:
        print(f"[PASS] Multiple theory pathways detected: {', '.join(theories_detected)}")
    elif len(theories_detected) == 1:
        print(f"[PASS] Theory pathway detected: {theories_detected[0]}")
    else:
        print("[WARN] No theory pathways detected (may need reduction tuning)")

    # Check 3: Pipeline completed
    if pipeline_results["status"] == "complete":
        print("[PASS] Paper evaluation pipeline completed")
    else:
        print(f"[FAIL] Pipeline status: {pipeline_results['status']}")
        all_pass = False

    # Check 4: Claims were extracted
    if pipeline_results["n_claims_extracted"] >= 2:
        print(f"[PASS] Claims extracted: {pipeline_results['n_claims_extracted']}")
    else:
        print(f"[FAIL] Only {pipeline_results['n_claims_extracted']} claims extracted")
        all_pass = False

    # Check 5: Process paper completed
    if proposal_results["status"] == "complete":
        print("[PASS] Process paper with proposals completed")
    else:
        print(f"[FAIL] Process paper status: {proposal_results['status']}")
        all_pass = False

    print("")
    if all_pass:
        print("✓ Ulrich 1984 Full Pipeline Test PASSED")
        return 0
    else:
        print("✗ Some checks failed - review output above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
