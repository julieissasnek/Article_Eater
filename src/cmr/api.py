"""CMR FastAPI wrapper endpoints (Sprint 12 Task 12.22)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Path as PathParam, Query
from pydantic import BaseModel, Field
from sqlalchemy import func

from src.cmr.building_eval import evaluate_building
from src.cmr.models import (
    CMRTemplateActivation,
    ReductionClaim,
    TemplateRecord,
    create_tables,
    get_session,
)
from src.cmr.paper_eval import evaluate_paper
from src.cmr.quick_assess import quick_assess
from src.cmr.reductions.art_reduction import ART_REDUCTIONS
from src.cmr.reductions.biophilia_reduction import BIOPHILIA_REDUCTIONS
from src.cmr.reductions.srt_reduction import SRT_REDUCTIONS


def _as_dict(model: BaseModel) -> dict[str, Any]:
    if hasattr(model, "model_dump"):  # Pydantic v2
        return model.model_dump(exclude_none=True)
    return model.dict(exclude_none=True)  # Pydantic v1


class BuildingEvaluationRequest(BaseModel):
    measured_features: dict[str, Any] = Field(default_factory=dict)
    building_context: dict[str, Any] = Field(default_factory=dict)
    occupant_profile: dict[str, Any] = Field(default_factory=lambda: {"age": 35, "cultural_context": "Western"})
    db_path: str | None = None


class BuildingEvaluationResponse(BaseModel):
    evaluation_id: int | None = None
    status: str
    domain_scores: list[dict[str, Any]] = Field(default_factory=list)
    overall_wis: float
    overall_confidence: float
    severe_deficits: list[str] = Field(default_factory=list)
    data_gaps: list[str] = Field(default_factory=list)
    activated_templates: list[str] = Field(default_factory=list)
    web_constraint_query_summary: dict[str, Any] = Field(default_factory=dict)


class QuickAssessmentRequest(BaseModel):
    ceiling_height_m: float | None = None
    floor_area_m2: float | None = None
    has_nature_view: bool | None = None
    view_content: str | None = None
    walking_paths_available: bool | None = None
    wayfinding_clear: bool | None = None
    wall_colors: list[str] | None = None
    color_sequence_varied: bool | None = None
    floor_surface: str | None = None
    stair_dimensions_standard: bool | None = None
    thermal_system: str | None = None
    primary_material: str | None = None
    max_group_size: int | None = None
    occupant_age: int = Field(default=35, ge=0, le=120)


class QuickAssessmentResponse(BaseModel):
    overall_rating: str
    overall_wis: float
    template_scores: dict[str, float]
    strengths: list[dict[str, Any]]
    deficits: list[dict[str, Any]]
    recommendations: list[str]
    tier_b_suggestions: list[str]
    templates_assessed: int
    templates_skipped: list[str]


class PaperEvaluationRequest(BaseModel):
    paper_text: str = ""
    structured_claims: list[dict[str, Any]] | None = None
    citation: str | None = None
    doi: str | None = None
    db_path: str | None = None


class PaperEvaluationResponse(BaseModel):
    status: str
    pipeline_type: str
    paper_summary: str
    n_claims_extracted: int
    n_claims_matched: int
    n_claims_unmatched: int
    findings: list[dict[str, Any]] = Field(default_factory=list)
    template_system_updates: list[dict[str, Any]] = Field(default_factory=list)
    report: dict[str, Any] = Field(default_factory=dict)


class CompareRequest(BaseModel):
    building_a: BuildingEvaluationRequest
    building_b: BuildingEvaluationRequest
    label_a: str = "Current"
    label_b: str = "Proposed"


class CompareResponse(BaseModel):
    label_a: str
    label_b: str
    overall_a: float
    overall_b: float
    overall_delta: float
    domain_deltas: list[dict[str, Any]] = Field(default_factory=list)
    top_improvements: list[dict[str, Any]] = Field(default_factory=list)
    top_regressions: list[dict[str, Any]] = Field(default_factory=list)


class SensitivityRequest(BaseModel):
    baseline: BuildingEvaluationRequest
    feature_variations: dict[str, list[Any]] = Field(default_factory=dict)
    top_k: int = Field(default=5, ge=1, le=20)


class SensitivityResponse(BaseModel):
    baseline_overall_wis: float
    ranked_impacts: list[dict[str, Any]] = Field(default_factory=list)
    best_single_change: dict[str, Any] | None = None


class TemplateSummary(BaseModel):
    template_id: str
    display_id: str
    name: str
    series: str
    generation: int
    dedup_status: str
    maturity: str
    calibration_status: str
    practical_accessibility: str


class TemplateListResponse(BaseModel):
    count: int
    templates: list[TemplateSummary]


class TemplateDetailsResponse(BaseModel):
    template_id: str
    display_id: str
    name: str
    series: str
    generation: int
    dedup_status: str
    superseded_by: str | None = None
    pe_contribution: str
    maturity: str
    calibration_status: str
    practical_accessibility: str
    ecological_validation: bool
    source_docs: str
    json_path: str
    json_data: dict[str, Any] | None = None


class ReductionResponse(BaseModel):
    theory: str
    source: str
    constructs: list[dict[str, Any]]


def _resolve_db_path(request_db_path: str | None, default_db_path: str) -> str:
    return request_db_path or default_db_path


def _validate_minimum_building_inputs(measured_features: dict[str, Any]) -> None:
    required = {"ceiling_height_m", "floor_area_m2"}
    missing = sorted(key for key in required if key not in measured_features)
    if missing:
        raise HTTPException(
            status_code=422,
            detail=(
                "Building evaluation requires measured_features with "
                f"{', '.join(sorted(required))}. Missing: {', '.join(missing)}"
            ),
        )


def _normalize_occupant_profile(payload: dict[str, Any]) -> dict[str, Any]:
    profile = dict(payload or {})
    profile.setdefault("age", 35)
    profile.setdefault("cultural_context", "Western")
    return profile


def _get_template_wis_by_evaluation(db_path: str, evaluation_id: int | None) -> dict[str, float]:
    if evaluation_id is None:
        return {}
    session = get_session(db_path)
    try:
        rows = (
            session.query(CMRTemplateActivation.template_display_id, CMRTemplateActivation.wis_score)
            .filter(CMRTemplateActivation.evaluation_id == evaluation_id)
            .all()
        )
        return {tid: float(score or 0.0) for tid, score in rows}
    finally:
        session.close()


def _domain_map(result: dict[str, Any]) -> dict[str, float]:
    return {
        str(item.get("domain")): float(item.get("wis", 0.0))
        for item in result.get("domain_scores", [])
        if item.get("domain") is not None
    }


def _template_to_summary(record: TemplateRecord) -> TemplateSummary:
    return TemplateSummary(
        template_id=record.template_id,
        display_id=record.display_id,
        name=record.name,
        series=record.series,
        generation=record.generation,
        dedup_status=record.dedup_status,
        maturity=record.maturity,
        calibration_status=record.calibration_status,
        practical_accessibility=record.practical_accessibility,
    )


def _load_template_json(json_path: str) -> dict[str, Any] | None:
    path = Path(json_path)
    if not path.is_absolute():
        repo_root = Path(__file__).resolve().parents[2]
        path = repo_root / path
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _fallback_reduction(theory: str) -> list[dict[str, Any]] | None:
    series_map = {
        "ART": ART_REDUCTIONS,
        "SRT": SRT_REDUCTIONS,
        "BIOPHILIA": BIOPHILIA_REDUCTIONS,
    }
    reductions = series_map.get(theory.upper())
    if reductions is None:
        return None
    rows: list[dict[str, Any]] = []
    for construct_name, reduction in reductions.items():
        rows.append(
            {
                "construct": construct_name,
                "reduction_type": "partial",
                "template_mappings": [
                    {
                        "template_id": m.template_id,
                        "mechanism": m.mechanism,
                        "coverage": m.coverage,
                        "channel": m.channel,
                    }
                    for m in reduction.template_mappings
                ],
                "irreducible_residual": reduction.irreducible_residual,
                "confidence": reduction.confidence,
                "source_panel": None,
                "staging_links_reconciled": None,
                "staging_links_total": None,
            }
        )
    return rows


def _auto_variations(measured_features: dict[str, Any]) -> dict[str, list[Any]]:
    variations: dict[str, list[Any]] = {}
    for key, value in measured_features.items():
        if isinstance(value, bool):
            variations[key] = [not value]
            continue
        if isinstance(value, (int, float)):
            val = float(value)
            span = max(abs(val) * 0.2, 1.0)
            low = round(val - span, 4)
            high = round(val + span, 4)
            if low == high:
                high = low + 1.0
            variations[key] = [low, high]
    return variations


def create_app(default_db_path: str = "ae.db") -> FastAPI:
    app = FastAPI(
        title="CMR API",
        description="FastAPI wrapper for CMR building, quick, paper, compare, and sensitivity workflows.",
        version="0.1.0",
    )

    @app.post("/evaluate/building", response_model=BuildingEvaluationResponse)
    def evaluate_building_endpoint(request: BuildingEvaluationRequest) -> BuildingEvaluationResponse:
        db_path = _resolve_db_path(request.db_path, default_db_path)
        create_tables(db_path)
        request_dict = _as_dict(request)
        measured_features = request_dict.get("measured_features", {})
        _validate_minimum_building_inputs(measured_features)
        result = evaluate_building(
            building_context=request_dict.get("building_context", {}),
            measured_features=measured_features,
            occupant_profile=_normalize_occupant_profile(request_dict.get("occupant_profile", {})),
            db_path=db_path,
        )
        return BuildingEvaluationResponse(**result)

    @app.post("/evaluate/building/quick", response_model=QuickAssessmentResponse)
    def evaluate_building_quick_endpoint(request: QuickAssessmentRequest) -> QuickAssessmentResponse:
        payload = _as_dict(request)
        result = quick_assess(**payload)
        return QuickAssessmentResponse(
            overall_rating=result.overall_rating,
            overall_wis=float(result.overall_wis),
            template_scores={k: float(v) for k, v in result.template_scores.items()},
            strengths=result.strengths,
            deficits=result.deficits,
            recommendations=result.recommendations,
            tier_b_suggestions=result.tier_b_suggestions,
            templates_assessed=result.templates_assessed,
            templates_skipped=result.templates_skipped,
        )

    @app.post("/evaluate/paper", response_model=PaperEvaluationResponse)
    def evaluate_paper_endpoint(request: PaperEvaluationRequest) -> PaperEvaluationResponse:
        db_path = _resolve_db_path(request.db_path, default_db_path)
        create_tables(db_path)
        payload = _as_dict(request)
        if not payload.get("paper_text") and not payload.get("structured_claims"):
            raise HTTPException(status_code=422, detail="Provide paper_text or structured_claims.")
        result = evaluate_paper(
            paper_text=payload.get("paper_text", ""),
            structured_claims=payload.get("structured_claims"),
            citation=payload.get("citation"),
            doi=payload.get("doi"),
            db_path=db_path,
        )
        return PaperEvaluationResponse(
            status=result.get("status", "complete"),
            pipeline_type=result.get("pipeline_type", "paper_evaluation"),
            paper_summary=result.get("paper_summary", ""),
            n_claims_extracted=int(result.get("n_claims_extracted", 0)),
            n_claims_matched=int(result.get("n_claims_matched", 0)),
            n_claims_unmatched=int(result.get("n_claims_unmatched", 0)),
            findings=result.get("findings", []),
            template_system_updates=result.get("template_system_updates", []),
            report=result.get("report", {}),
        )

    @app.post("/compare", response_model=CompareResponse)
    def compare_endpoint(request: CompareRequest) -> CompareResponse:
        first = _as_dict(request.building_a)
        second = _as_dict(request.building_b)
        db_a = _resolve_db_path(first.get("db_path"), default_db_path)
        db_b = _resolve_db_path(second.get("db_path"), default_db_path)
        create_tables(db_a)
        create_tables(db_b)
        _validate_minimum_building_inputs(first.get("measured_features", {}))
        _validate_minimum_building_inputs(second.get("measured_features", {}))

        result_a = evaluate_building(
            building_context=first.get("building_context", {}),
            measured_features=first.get("measured_features", {}),
            occupant_profile=_normalize_occupant_profile(first.get("occupant_profile", {})),
            db_path=db_a,
        )
        result_b = evaluate_building(
            building_context=second.get("building_context", {}),
            measured_features=second.get("measured_features", {}),
            occupant_profile=_normalize_occupant_profile(second.get("occupant_profile", {})),
            db_path=db_b,
        )

        domains_a = _domain_map(result_a)
        domains_b = _domain_map(result_b)
        all_domains = sorted(set(domains_a) | set(domains_b))
        domain_deltas = [
            {
                "domain": domain,
                "wis_a": domains_a.get(domain, 0.0),
                "wis_b": domains_b.get(domain, 0.0),
                "delta": round(domains_b.get(domain, 0.0) - domains_a.get(domain, 0.0), 3),
            }
            for domain in all_domains
        ]
        domain_deltas.sort(key=lambda row: row["delta"], reverse=True)

        template_scores_a = _get_template_wis_by_evaluation(db_a, result_a.get("evaluation_id"))
        template_scores_b = _get_template_wis_by_evaluation(db_b, result_b.get("evaluation_id"))
        all_templates = sorted(set(template_scores_a) | set(template_scores_b))
        template_deltas = [
            {
                "template_id": template_id,
                "wis_a": template_scores_a.get(template_id, 0.0),
                "wis_b": template_scores_b.get(template_id, 0.0),
                "delta": round(template_scores_b.get(template_id, 0.0) - template_scores_a.get(template_id, 0.0), 3),
            }
            for template_id in all_templates
        ]
        improvements = [row for row in template_deltas if row["delta"] > 0]
        regressions = [row for row in template_deltas if row["delta"] < 0]
        improvements.sort(key=lambda row: row["delta"], reverse=True)
        regressions.sort(key=lambda row: row["delta"])

        overall_a = float(result_a.get("overall_wis", 0.0))
        overall_b = float(result_b.get("overall_wis", 0.0))
        return CompareResponse(
            label_a=request.label_a,
            label_b=request.label_b,
            overall_a=overall_a,
            overall_b=overall_b,
            overall_delta=round(overall_b - overall_a, 3),
            domain_deltas=domain_deltas,
            top_improvements=improvements[:5],
            top_regressions=regressions[:5],
        )

    @app.post("/sensitivity", response_model=SensitivityResponse)
    def sensitivity_endpoint(request: SensitivityRequest) -> SensitivityResponse:
        baseline = _as_dict(request.baseline)
        db_path = _resolve_db_path(baseline.get("db_path"), default_db_path)
        create_tables(db_path)
        measured_features = baseline.get("measured_features", {})
        _validate_minimum_building_inputs(measured_features)

        base_result = evaluate_building(
            building_context=baseline.get("building_context", {}),
            measured_features=measured_features,
            occupant_profile=_normalize_occupant_profile(baseline.get("occupant_profile", {})),
            db_path=db_path,
        )
        baseline_wis = float(base_result.get("overall_wis", 0.0))

        variations = request.feature_variations or _auto_variations(measured_features)
        impacts: list[dict[str, Any]] = []
        for feature, values in variations.items():
            if not values:
                continue
            results: list[dict[str, Any]] = []
            for value in values:
                scenario_features = dict(measured_features)
                scenario_features[feature] = value
                scenario = evaluate_building(
                    building_context=baseline.get("building_context", {}),
                    measured_features=scenario_features,
                    occupant_profile=_normalize_occupant_profile(baseline.get("occupant_profile", {})),
                    db_path=db_path,
                )
                wis = float(scenario.get("overall_wis", 0.0))
                results.append(
                    {
                        "value": value,
                        "overall_wis": wis,
                        "delta_from_baseline": round(wis - baseline_wis, 3),
                    }
                )
            wis_values = [entry["overall_wis"] for entry in results]
            deltas = [entry["delta_from_baseline"] for entry in results]
            impacts.append(
                {
                    "feature": feature,
                    "tested_values": results,
                    "best_overall_wis": max(wis_values),
                    "worst_overall_wis": min(wis_values),
                    "impact_span": round(max(wis_values) - min(wis_values), 3),
                    "best_delta_from_baseline": round(max(deltas), 3),
                    "improvement_probability": round(
                        sum(1 for delta in deltas if delta > 0) / max(len(deltas), 1),
                        3,
                    ),
                }
            )

        impacts.sort(key=lambda row: row["impact_span"], reverse=True)
        top = impacts[: request.top_k]
        best_single = top[0] if top else None
        return SensitivityResponse(
            baseline_overall_wis=baseline_wis,
            ranked_impacts=top,
            best_single_change=best_single,
        )

    @app.get("/templates", response_model=TemplateListResponse)
    def list_templates(
        dedup_status: str | None = Query(default=None),
        limit: int = Query(default=200, ge=1, le=1000),
        db_path: str = Query(default=default_db_path),
    ) -> TemplateListResponse:
        create_tables(db_path)
        session = get_session(db_path)
        try:
            query = session.query(TemplateRecord)
            if dedup_status:
                query = query.filter(TemplateRecord.dedup_status == dedup_status)
            rows = query.order_by(TemplateRecord.series, TemplateRecord.display_id).limit(limit).all()
            payload = [_template_to_summary(row) for row in rows]
            return TemplateListResponse(count=len(payload), templates=payload)
        finally:
            session.close()

    @app.get("/templates/{template_id}", response_model=TemplateDetailsResponse)
    def get_template_details(
        template_id: str = PathParam(..., description="Display ID (e.g., VF3) or full template_id"),
        db_path: str = Query(default=default_db_path),
    ) -> TemplateDetailsResponse:
        create_tables(db_path)
        session = get_session(db_path)
        try:
            record = (
                session.query(TemplateRecord)
                .filter(
                    (TemplateRecord.display_id == template_id)
                    | (TemplateRecord.template_id == template_id)
                )
                .first()
            )
            if record is None:
                raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found.")
            return TemplateDetailsResponse(
                template_id=record.template_id,
                display_id=record.display_id,
                name=record.name,
                series=record.series,
                generation=record.generation,
                dedup_status=record.dedup_status,
                superseded_by=record.superseded_by,
                pe_contribution=record.pe_contribution,
                maturity=record.maturity,
                calibration_status=record.calibration_status,
                practical_accessibility=record.practical_accessibility,
                ecological_validation=bool(record.ecological_validation),
                source_docs=record.source_docs,
                json_path=record.json_path,
                json_data=_load_template_json(record.json_path),
            )
        finally:
            session.close()

    @app.get("/reductions/{theory}", response_model=ReductionResponse)
    def get_reduction(
        theory: str = PathParam(..., description="Tier-2 theory key (ART, SRT, Biophilia)"),
        db_path: str = Query(default=default_db_path),
    ) -> ReductionResponse:
        create_tables(db_path)
        session = get_session(db_path)
        try:
            rows = (
                session.query(ReductionClaim)
                .filter(func.upper(ReductionClaim.tier2_theory) == theory.upper())
                .all()
            )
            if rows:
                return ReductionResponse(
                    theory=theory.upper(),
                    source="database",
                    constructs=[
                        {
                            "construct": row.tier2_construct,
                            "reduction_type": row.reduction_type,
                            "template_mappings": row.template_mappings or [],
                            "irreducible_residual": row.irreducible_residual,
                            "confidence": row.confidence,
                            "source_panel": row.source_panel,
                            "staging_links_reconciled": row.staging_links_reconciled,
                            "staging_links_total": row.staging_links_total,
                        }
                        for row in rows
                    ],
                )
        finally:
            session.close()

        fallback = _fallback_reduction(theory)
        if fallback is None:
            raise HTTPException(status_code=404, detail=f"No reductions found for '{theory}'.")
        return ReductionResponse(theory=theory.upper(), source="module_fallback", constructs=fallback)

    return app


app = create_app()

