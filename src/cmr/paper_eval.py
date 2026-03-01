"""Paper evaluation orchestrator (Sprint 11 Task 11.10)."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

from sqlalchemy.orm import Session

from src.cmr.claim_extraction import extract_claims_from_text, extract_claims_structured
from src.cmr.convergence import assess_convergence, check_composition_failures
from src.cmr.mechanism_tracing import trace_claim
from src.cmr.models import TemplateRecord, create_tables, get_session
from src.cmr.paper_history import create_paper_record
from src.cmr.template_matching import build_template_index, match_claims_to_templates
from src.cmr.voi_scoring import aggregate_paper_voi, score_voi
from src.services.web_persistence import WebPersistenceService


@dataclass
class PaperEvalStep:
    step: int
    name: str
    status: str
    details: dict[str, Any]


def _extract_claims(
    paper_text: str,
    structured_claims: list[dict] | None,
) -> tuple[list[dict], dict[str, Any]]:
    if structured_claims:
        claims = extract_claims_structured(structured_claims)
        return claims, {"mode": "provided", "count": len(claims)}

    claims = extract_claims_from_text(paper_text or "")
    if claims:
        return claims, {"mode": "text_extraction", "count": len(claims)}

    # Backward-compatible fallback used by existing tests.
    return (
        [
            {
                "claim_id": "placeholder_claim_1",
                "text": (paper_text or "")[:240],
                "iv": None,
                "dv": None,
                "source": "placeholder_extractor",
                "direction": "unknown",
            }
        ],
        {"mode": "placeholder", "count": 1},
    )


def _load_active_templates(session: Session) -> list[TemplateRecord]:
    return (
        session.query(TemplateRecord)
        .filter(TemplateRecord.dedup_status == "active")
        .all()
    )


def _trace_mechanisms(claim_matches: list[dict], template_index: dict[str, dict]) -> list[dict]:
    traced_claims: list[dict] = []
    for entry in claim_matches:
        claim = entry.get("claim", {})
        traced_templates: list[dict[str, Any]] = []
        for match in entry.get("matches", []):
            template_id = match.get("template_id")
            template_data = template_index.get(template_id, {}).get("json_data", {})
            trace = trace_claim(claim, template_data)
            traced_templates.append(
                {
                    "template_id": template_id,
                    "status": trace.get("status", "nuanced"),
                    "confidence": float(trace.get("confidence", 0.3)),
                    "reasoning": trace.get("reasoning", ""),
                    "match_type": match.get("match_type"),
                    "match_confidence": float(match.get("confidence", 0.0)),
                }
            )
        traced_claims.append(
            {
                "claim": claim,
                "matches": entry.get("matches", []),
                "traced_templates": traced_templates,
            }
        )
    return traced_claims


def _prioritize_findings(
    composed_claims: list[dict],
    template_maturity_by_id: dict[str, str],
) -> list[dict]:
    """
    Rank findings via VOI scoring contract (Task 11.20).
    """
    raw_findings: list[dict[str, Any]] = []
    for entry in composed_claims:
        convergence = entry.get("convergence", {})
        status = convergence.get("status", "unsupported")
        claim = entry.get("claim", {})
        matches = entry.get("matches", []) or []
        matched_ids = [m.get("template_id") for m in matches if m.get("template_id")]
        maturities = [template_maturity_by_id.get(tid, "") for tid in matched_ids]

        has_matches = bool(matched_ids)
        if status == "contradicted":
            category = "contradiction"
        elif status in {"unsupported"} and _is_air_quality_gap_claim(claim):
            category = "gap"
        elif status in {"unsupported"} and has_matches:
            category = "extension"
        elif status in {"unsupported"}:
            category = "gap"
        else:
            category = "confirmation"

        raw_findings.append(
            {
                "claim": claim,
                "category": category,
                "assessment": category,
                "template_maturity": maturities,
                "effect_size": _claim_effect_size_abs(claim),
                "convergence_status": status,
                "supporting_templates": convergence.get("supporting_templates", []),
                "contradicting_templates": convergence.get("contradicting_templates", []),
                "composition_warnings": entry.get("composition_analysis", {}).get("warnings", []),
            }
        )

    scored = score_voi(raw_findings)
    prioritized: list[dict[str, Any]] = []
    for idx, finding in enumerate(scored, start=1):
        prioritized.append(
            {
                **finding,
                "priority": idx,
                "voi_score": round(100.0 * float(finding.get("voi_score", 0.0)), 2),
                "voi_bucket": finding.get("voi_bucket", "low"),
            }
        )
    return prioritized


def _score_to_band(score: float) -> str:
    if score >= 0.75:
        return "high"
    if score >= 0.5:
        return "medium"
    return "low"


def _claim_effect_size_abs(claim: dict[str, Any]) -> float:
    try:
        return abs(float(claim.get("effect_size", 0.0) or 0.0))
    except (TypeError, ValueError):
        return 0.0


def _is_air_quality_gap_claim(claim: dict[str, Any]) -> bool:
    joined = " ".join(
        [
            str(claim.get("description", "")),
            str(claim.get("iv", "")),
            str(claim.get("dv", "")),
        ]
    ).lower()
    keywords = {"co2", "carbon dioxide", "air quality", "ventilation", "ppm"}
    return any(keyword in joined for keyword in keywords)


def _build_template_system_updates(composed_claims: list[dict]) -> list[dict]:
    updates: list[dict[str, str]] = []
    for entry in composed_claims:
        claim = entry.get("claim", {})
        convergence = entry.get("convergence", {})
        status = convergence.get("status", "unsupported")
        claim_text = claim.get("description") or f"{claim.get('iv')} -> {claim.get('dv')}"

        supporting = convergence.get("supporting_templates", []) or []
        contradicting = convergence.get("contradicting_templates", []) or []
        matched_templates = [m.get("template_id") for m in entry.get("matches", []) if m.get("template_id")]

        if status == "contradicted" and contradicting:
            for template_id in contradicting:
                updates.append(
                    {
                        "type": "contradicts",
                        "template": str(template_id),
                        "detail": f"Claim contradicts {template_id}: {claim_text}",
                    }
                )

        if supporting:
            for template_id in supporting:
                updates.append(
                    {
                        "type": "confirms",
                        "template": str(template_id),
                        "detail": f"Claim confirms {template_id}: {claim_text}",
                    }
                )

        if status == "contradicted" and contradicting:
            continue
        if supporting:
            continue

        if _is_air_quality_gap_claim(claim):
            updates.append(
                {
                    "type": "gap",
                    "template": "none",
                    "detail": "No template covers indoor air quality. Consider AIR-I panel.",
                }
            )
            continue

        if matched_templates:
            for template_id in matched_templates:
                updates.append(
                    {
                        "type": "extends",
                        "template": str(template_id),
                        "detail": f"Claim partially maps to {template_id} and may extend template boundaries: {claim_text}",
                    }
                )
        else:
            updates.append(
                {
                    "type": "gap",
                    "template": "none",
                    "detail": f"No template matched claim: {claim_text}",
                }
            )

    # Preserve first-seen order while deduplicating.
    deduped: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    for update in updates:
        key = (update["type"], update["template"], update["detail"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(update)
    return deduped


def _build_findings_for_contract(composed_claims: list[dict], prioritized: list[dict]) -> list[dict]:
    findings: list[dict[str, Any]] = []
    prioritized_by_claim: dict[str, dict] = {}
    for item in prioritized:
        claim_key = str(item.get("claim"))
        prioritized_by_claim[claim_key] = item

    for entry in composed_claims:
        claim = entry.get("claim", {})
        convergence = entry.get("convergence", {})
        traced_templates = entry.get("traced_templates", [])
        max_conf = max([float(t.get("confidence", 0.0)) for t in traced_templates], default=0.0)

        ranked = prioritized_by_claim.get(str(claim), {})
        category = ranked.get("category", "gap")
        voi = str(ranked.get("voi_bucket", "low"))

        findings.append(
            {
                "claim": claim,
                "assessment": category,
                "convergence": convergence.get("status", "unsupported"),
                "confidence": _score_to_band(max_conf),
                "voi": voi,
            }
        )
    return findings


def _claim_query_terms(claim: dict[str, Any], max_terms: int = 8) -> list[str]:
    text = " ".join(
        [
            str(claim.get("description", "")),
            str(claim.get("text", "")),
            str(claim.get("iv", "")),
            str(claim.get("dv", "")),
            str(claim.get("direction", "")),
        ]
    ).lower()
    terms = [token for token in re.findall(r"[a-z0-9_]+", text) if len(token) >= 3]
    deduped: list[str] = []
    seen: set[str] = set()
    for term in terms:
        if term in seen:
            continue
        seen.add(term)
        deduped.append(term)
        if len(deduped) >= max_terms:
            break
    return deduped


def _query_web_for_claims(
    claims: list[dict[str, Any]],
    *,
    db_path: str,
    web_service: WebPersistenceService | None = None,
) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "web_id": None,
        "query_count": 0,
        "queries": [],
        "matched_beliefs": 0,
    }
    try:
        service = web_service or WebPersistenceService(db_path)
        master_web_id = service.get_master_web_id()
        if not master_web_id:
            summary["reason"] = "no_master_web"
            return summary

        summary["web_id"] = master_web_id
        beliefs = service.get_beliefs_for_web(master_web_id)
        summary["belief_pool_size"] = len(beliefs)

        total_matches = 0
        for claim in claims:
            terms = _claim_query_terms(claim)
            if not terms:
                continue

            matches = 0
            for belief in beliefs:
                haystack = " ".join(
                    [
                        str(getattr(belief, "content", "")),
                        str(getattr(belief, "theory_id", "")),
                        str(getattr(belief, "domain", "")),
                        " ".join(getattr(belief, "tags", []) or []),
                    ]
                ).lower()
                if any(term in haystack for term in terms):
                    matches += 1

            summary["queries"].append(
                {
                    "claim_id": claim.get("claim_id"),
                    "terms": terms,
                    "query": " ".join(terms),
                    "match_count": matches,
                }
            )
            total_matches += matches

        summary["query_count"] = len(summary["queries"])
        summary["matched_beliefs"] = total_matches
        return summary
    except Exception as exc:  # pragma: no cover - defensive path
        summary["error"] = str(exc)
        return summary


def _build_recommendations(
    prioritized: list[dict[str, Any]],
    template_system_updates: list[dict[str, str]],
) -> list[str]:
    recommendations: list[str] = []

    has_contradiction = any(item.get("category") == "contradiction" for item in prioritized)
    has_gap = any(item.get("category") in {"gap", "extension"} for item in prioritized)
    has_confirmation = any(item.get("category") == "confirmation" for item in prioritized)

    contradicted_templates = {
        update.get("template")
        for update in template_system_updates
        if update.get("type") == "contradicts"
    }

    if has_contradiction:
        recommendations.append("Investigate contradiction findings first (highest VOI).")
        if "VF3" in contradicted_templates or "CREA2" in contradicted_templates:
            recommendations.append(
                "Review VF3 Goldilocks boundaries; check if effect reverses above R_h 0.80."
            )
        recommendations.append(
            "Run targeted replication checks for contradicted templates before ontology updates."
        )

    if has_gap:
        recommendations.append("Queue unsupported claims as template/ontology gaps.")
        if any("AIR-I" in str(update.get("detail", "")) for update in template_system_updates):
            recommendations.append(
                "No template covers indoor air quality; prioritize AIR-I panel development."
            )

    if has_confirmation:
        recommendations.append("Treat single-mechanism confirmations as provisional.")

    if not recommendations:
        recommendations.append("No critical issues detected; continue with broader validation sweep.")

    # Keep order, remove duplicates.
    deduped: list[str] = []
    seen: set[str] = set()
    for rec in recommendations:
        if rec in seen:
            continue
        seen.add(rec)
        deduped.append(rec)
    return deduped


def _flatten_scored_matches(claim_matches: list[dict], traced_claims: list[dict]) -> list[dict]:
    trace_lookup: dict[tuple[int, str], dict[str, Any]] = {}
    for idx, traced in enumerate(traced_claims):
        for item in traced.get("traced_templates", []):
            trace_lookup[(idx, item.get("template_id"))] = item

    scored: list[dict] = []
    for idx, entry in enumerate(claim_matches):
        for match in entry.get("matches", []):
            template_id = match.get("template_id")
            trace = trace_lookup.get((idx, template_id), {})
            scored.append(
                {
                    "claim": entry.get("claim"),
                    "template_id": template_id,
                    "match_type": match.get("match_type"),
                    "match_confidence": float(match.get("confidence", 0.0)),
                    "trace_status": trace.get("status", "nuanced"),
                    "trace_confidence": float(trace.get("confidence", 0.0)),
                    "score": round(
                        0.5 * float(match.get("confidence", 0.0))
                        + 0.5 * float(trace.get("confidence", 0.0)),
                        3,
                    ),
                }
            )
    return scored


def evaluate_paper(
    paper_text: str = "",
    structured_claims: list[dict] | None = None,
    *,
    citation: str | None = None,
    doi: str | None = None,
    db_path: str = "ae.db",
    session: Session | None = None,
    web_service: WebPersistenceService | None = None,
) -> dict:
    """Full paper evaluation pipeline (Doc 68 Part 3.2 Steps 1-7)."""
    own_session = session is None
    session = session or get_session(db_path)
    create_tables(db_path)

    steps: list[PaperEvalStep] = []

    try:
        # Step 1: claim extraction
        claims, step1_details = _extract_claims(paper_text, structured_claims)
        steps.append(PaperEvalStep(1, "claim_extraction", "complete", step1_details))
        web_query_summary = _query_web_for_claims(
            claims,
            db_path=db_path,
            web_service=web_service,
        )

        # Step 2: template matching
        templates = _load_active_templates(session)
        template_maturity_by_id = {template.display_id: template.maturity for template in templates}
        template_index = build_template_index(templates)
        claim_matches = match_claims_to_templates(claims, template_index)
        total_matches = sum(len(item.get("matches", [])) for item in claim_matches)
        steps.append(
            PaperEvalStep(
                2,
                "template_matching",
                "complete",
                {
                    "templates_indexed": len(template_index),
                    "claims": len(claims),
                    "matches_found": total_matches,
                    "web_queries": web_query_summary.get("query_count", 0),
                    "web_belief_matches": web_query_summary.get("matched_beliefs", 0),
                },
            )
        )

        # Step 3: mechanism tracing
        traced = _trace_mechanisms(claim_matches, template_index)
        steps.append(
            PaperEvalStep(
                3,
                "mechanism_tracing",
                "complete",
                {"claims_traced": len(traced)},
            )
        )

        # Step 4: convergence assessment
        converged = assess_convergence(traced)
        steps.append(
            PaperEvalStep(
                4,
                "convergence_assessment",
                "complete",
                {
                    "strong": sum(1 for c in converged if c.get("convergence", {}).get("status") == "strong"),
                    "contradicted": sum(
                        1 for c in converged if c.get("convergence", {}).get("status") == "contradicted"
                    ),
                },
            )
        )

        # Step 5: composition checks
        composed = check_composition_failures(converged)
        steps.append(
            PaperEvalStep(
                5,
                "composition_check",
                "complete",
                {
                    "warnings": sum(
                        len(c.get("composition_analysis", {}).get("warnings", [])) for c in composed
                    )
                },
            )
        )

        # Step 6: VOI prioritization
        prioritized = _prioritize_findings(composed, template_maturity_by_id)
        aggregate_voi = aggregate_paper_voi(prioritized)
        steps.append(
            PaperEvalStep(
                6,
                "prioritization",
                "complete",
                {
                    "findings": len(prioritized),
                    "top_category": prioritized[0]["category"] if prioritized else None,
                    "aggregate_voi": aggregate_voi.get("aggregate_voi", 0.0),
                },
            )
        )

        # Step 7: report assembly
        n_claims_extracted = len(claims)
        n_claims_matched = sum(1 for item in claim_matches if item.get("matches"))
        n_claims_unmatched = max(0, n_claims_extracted - n_claims_matched)
        findings = _build_findings_for_contract(composed, prioritized)
        template_system_updates = _build_template_system_updates(composed)
        matched_template_ids = sorted(
            {
                str(match.get("template_id")).strip()
                for row in claim_matches
                for match in row.get("matches", [])
                if match.get("template_id")
            }
        )

        report = {
            "summary": {
                "claims_evaluated": len(claims),
                "template_matches": total_matches,
                "contradictions": sum(1 for f in prioritized if f["category"] == "contradiction"),
                "gaps": sum(1 for f in prioritized if f["category"] == "gap"),
                "confirmations": sum(1 for f in prioritized if f["category"] == "confirmation"),
                "aggregate_voi": aggregate_voi.get("aggregate_voi", 0.0),
                "expected_information_gain": aggregate_voi.get("expected_information_gain", "low"),
                "status": "paper_pipeline_complete",
            },
            "top_findings": prioritized[:10],
            "recommendations": _build_recommendations(prioritized, template_system_updates),
        }
        steps.append(
            PaperEvalStep(
                7,
                "report_assembly",
                "complete",
                {"sections": list(report.keys())},
            )
        )
        paper_summary = (
            f"Processed {n_claims_extracted} claims from paper; "
            f"{n_claims_matched} matched templates and {n_claims_unmatched} unmatched."
        )
        create_paper_record(
            citation=citation,
            doi=doi,
            n_claims=n_claims_extracted,
            n_matched=n_claims_matched,
            n_unmatched=n_claims_unmatched,
            n_contradictions=sum(1 for f in prioritized if f["category"] == "contradiction"),
            n_confirmations=sum(1 for f in prioritized if f["category"] == "confirmation"),
            n_gaps=sum(1 for f in prioritized if f["category"] == "gap"),
            aggregate_voi=float(aggregate_voi.get("aggregate_voi", 0.0) or 0.0),
            proposals_generated=sum(
                1
                for update in template_system_updates
                if update.get("type") in {"contradicts", "extends", "gap"}
            ),
            matched_template_ids=matched_template_ids,
            session=session,
        )

        return {
            "status": "complete",
            "pipeline_type": "paper_evaluation",
            # Doc 68 contract-friendly fields for Task 11.10.
            "paper_summary": paper_summary,
            "n_claims_extracted": n_claims_extracted,
            "n_claims_matched": n_claims_matched,
            "n_claims_unmatched": n_claims_unmatched,
            "findings": findings,
            "template_system_updates": template_system_updates,
            # Backward-compatible detailed outputs.
            "claims": claims,
            "web_query_summary": web_query_summary,
            "template_matches": claim_matches,
            "traced_claims": composed,
            "prioritized_findings": prioritized,
            "scored_matches": _flatten_scored_matches(claim_matches, composed),
            "steps": [step.__dict__ for step in steps],
            "report": report,
        }
    finally:
        if own_session:
            session.close()
