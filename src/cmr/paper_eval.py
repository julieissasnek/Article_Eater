"""Paper evaluation skeleton (Doc 68 Part 3.2, Sprint 10 Task 3.6)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from src.cmr.models import TemplateRecord, create_tables, get_session


@dataclass
class PaperEvalStep:
    step: int
    name: str
    status: str
    details: dict[str, Any]


def _extract_claims(paper_text: str, structured_claims: list[dict] | None) -> tuple[list[dict], dict[str, Any]]:
    if structured_claims:
        return structured_claims, {"mode": "provided", "count": len(structured_claims)}
    return (
        [
            {
                "claim_id": "placeholder_claim_1",
                "text": paper_text[:240],
                "iv": None,
                "dv": None,
                "source": "placeholder_extractor",
            }
        ],
        {"mode": "placeholder", "count": 1},
    )


def _match_templates(session: Session, claims: list[dict]) -> list[dict]:
    templates = (
        session.query(TemplateRecord)
        .filter(TemplateRecord.dedup_status == "active")
        .all()
    )
    matches: list[dict] = []

    for claim in claims:
        iv = str(claim.get("iv") or "").strip().lower()
        dv = str(claim.get("dv") or "").strip().lower()
        claim_text = str(claim.get("text") or "").lower()

        for template in templates:
            haystacks = [
                str(template.name).lower(),
                str(template.template_id).lower(),
                str(template.display_id).lower(),
                str(template.series).lower(),
            ]
            if iv and not any(iv in h for h in haystacks):
                continue
            if dv and not any(dv in h for h in haystacks):
                continue
            if not iv and not dv and not any(token in claim_text for token in (template.display_id.lower(), template.series.lower())):
                continue

            matches.append(
                {
                    "claim_id": claim.get("claim_id"),
                    "template_display_id": template.display_id,
                    "template_id": template.template_id,
                    "series": template.series,
                    "match_method": "placeholder_text_filter",
                }
            )

    return matches


def evaluate_paper(
    paper_text: str,
    structured_claims: list[dict] | None = None,
    *,
    db_path: str = "ae.db",
    session: Session | None = None,
) -> dict:
    """Paper evaluation pipeline skeleton, Steps 1-7."""
    own_session = session is None
    session = session or get_session(db_path)
    create_tables(db_path)

    steps: list[PaperEvalStep] = []

    try:
        # Step 1: Claim extraction
        claims, step1_details = _extract_claims(paper_text, structured_claims)
        steps.append(
            PaperEvalStep(
                step=1,
                name="claim_extraction",
                status="complete",
                details=step1_details,
            )
        )

        # Step 2: Template matching
        matches = _match_templates(session, claims)
        steps.append(
            PaperEvalStep(
                step=2,
                name="template_matching",
                status="complete",
                details={"matches_found": len(matches), "method": "placeholder"},
            )
        )

        # Step 3: Mechanism tracing (stub)
        steps.append(
            PaperEvalStep(
                step=3,
                name="mechanism_tracing",
                status="stub",
                details={"status": "not_yet_implemented"},
            )
        )

        # Step 4: Claim-template scoring (stub)
        scored_matches = [
            {
                **match,
                "score": 0.5,
                "confidence": 0.4,
            }
            for match in matches
        ]
        steps.append(
            PaperEvalStep(
                step=4,
                name="claim_template_scoring",
                status="stub",
                details={"scored_matches": len(scored_matches)},
            )
        )

        # Step 5: Reduction assessment (stub)
        steps.append(
            PaperEvalStep(
                step=5,
                name="reduction_assessment",
                status="stub",
                details={"status": "placeholder"},
            )
        )

        # Step 6: Coherence update simulation (stub)
        steps.append(
            PaperEvalStep(
                step=6,
                name="coherence_projection",
                status="stub",
                details={"predicted_delta": 0.0},
            )
        )

        # Step 7: Report assembly
        report = {
            "summary": {
                "claims_evaluated": len(claims),
                "template_matches": len(matches),
                "status": "skeleton_complete",
            },
            "recommendations": [
                "Implement real claim extraction when parser contracts are finalized.",
                "Replace placeholder matching with IV/DV ontology matching.",
                "Implement mechanism tracing and reduction scoring.",
            ],
        }
        steps.append(
            PaperEvalStep(
                step=7,
                name="report_assembly",
                status="complete",
                details={"sections": list(report.keys())},
            )
        )

        return {
            "status": "complete",
            "pipeline_type": "paper_evaluation_skeleton",
            "claims": claims,
            "template_matches": matches,
            "scored_matches": scored_matches,
            "steps": [step.__dict__ for step in steps],
            "report": report,
        }
    finally:
        if own_session:
            session.close()

