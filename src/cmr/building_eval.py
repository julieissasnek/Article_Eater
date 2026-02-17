"""
Building evaluation orchestrator for CMR (Doc 68 Part 3.1).

Implements pipeline steps 1-9 with graceful fallbacks when template-specific
computation functions are not yet available.
"""

from __future__ import annotations

import importlib
import inspect
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

from src.cmr.models import (
    CMRDomainScore,
    CMREvaluation,
    CMROverallScore,
    CMRTemplateActivation,
    TemplateRecord,
    create_tables,
    get_session,
)
from src.cmr.wis import (
    aggregate_domain_wis,
    aggregate_overall_wis,
    cohens_d_to_wis,
    goldilocks_to_wis,
    threshold_to_wis,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

CALIBRATION_CONFIDENCE = {
    "substantial": 0.9,
    "partial": 0.7,
    "protocol": 0.4,
    "uncalibrated": 0.2,
}

GOLDILOCKS_ZONE_WIS = {
    "optimal": 85.0,
    "balanced": 80.0,
    "liberating": 82.0,
    "good": 75.0,
    "neutral": 55.0,
    "marginal": 40.0,
    "confining": 30.0,
    "poor": 25.0,
    "bad": 20.0,
    "overwhelming": 35.0,
}


def _resolve_json_path(json_path: str) -> Path:
    path = Path(json_path)
    if path.is_absolute():
        return path
    return REPO_ROOT / json_path


def _load_template_json(record: TemplateRecord) -> dict[str, Any]:
    path = _resolve_json_path(record.json_path)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _extract_required_inputs(template_json: dict[str, Any]) -> list[str]:
    required = template_json.get("inputs_required")
    if isinstance(required, dict):
        return [str(key) for key in required.keys()]

    if isinstance(required, list):
        keys: list[str] = []
        for item in required:
            if isinstance(item, str):
                keys.append(item)
                continue
            if not isinstance(item, dict):
                continue
            for candidate in (
                "name",
                "parameter_name",
                "input_name",
                "variable",
                "field",
                "id",
            ):
                value = item.get(candidate)
                if isinstance(value, str) and value.strip():
                    keys.append(value.strip())
                    break
        return keys

    return []


def _infer_domain(record: TemplateRecord, template_json: dict[str, Any]) -> str:
    domain = template_json.get("domain") or template_json.get("attribute_domain")
    if isinstance(domain, list) and domain:
        return str(domain[0])
    if isinstance(domain, str) and domain.strip():
        return domain.strip()
    return record.series


def _extract_wis_raw(output: dict[str, Any]) -> float:
    if "wis_raw" in output:
        return float(output["wis_raw"])

    output_type = str(output.get("output_type", "")).lower()

    if output_type == "cohens_d" and "value" in output:
        return cohens_d_to_wis(float(output["value"]))

    if output_type == "threshold" and "value" in output:
        threshold = float(output.get("threshold", 0.0))
        return threshold_to_wis(float(output["value"]), threshold)

    if output_type == "goldilocks_zone":
        if "value" in output and "zone_boundaries" in output:
            return goldilocks_to_wis(float(output["value"]), output["zone_boundaries"])
        zone = str(output.get("zone", "")).lower()
        if zone in GOLDILOCKS_ZONE_WIS:
            return GOLDILOCKS_ZONE_WIS[zone]

    if "value" in output and isinstance(output["value"], (int, float)):
        return float(output["value"])

    return 50.0


def _template_compute(display_id: str, inputs: dict[str, Any], occupant_age: int | None) -> dict[str, Any]:
    try:
        module = importlib.import_module("src.cmr.template_computations")
    except ImportError:
        module = None

    if module is None:
        return {
            "template": display_id,
            "output_type": "placeholder",
            "wis_raw": 50.0,
            "needs_calibration": True,
        }

    fn_name = f"compute_{display_id.lower()}"
    compute_fn = getattr(module, fn_name, None)
    if compute_fn is None:
        return {
            "template": display_id,
            "output_type": "placeholder",
            "wis_raw": 50.0,
            "needs_calibration": True,
        }

    try:
        signature = inspect.signature(compute_fn)
        kwargs = {name: value for name, value in inputs.items() if name in signature.parameters}
        if occupant_age is not None and "occupant_age" in signature.parameters:
            kwargs["occupant_age"] = occupant_age
        result = compute_fn(**kwargs)
        if isinstance(result, dict):
            return result
    except Exception as exc:  # pragma: no cover - defensive path
        return {
            "template": display_id,
            "output_type": "placeholder",
            "wis_raw": 50.0,
            "needs_calibration": True,
            "error": str(exc),
        }

    return {
        "template": display_id,
        "output_type": "placeholder",
        "wis_raw": 50.0,
        "needs_calibration": True,
    }


def evaluate_building(
    building_context: dict,
    measured_features: dict,
    occupant_profile: dict,
    db_path: str = "ae.db",
) -> dict:
    """Full building evaluation pipeline (Doc 68 Part 3.1, steps 1-9)."""
    create_tables(db_path)
    session = get_session(db_path)
    template_wis_overrides = building_context.get("template_wis_overrides", {})
    occupant_age = occupant_profile.get("age")

    evaluation = CMREvaluation(
        evaluation_type="building",
        target_description=building_context.get("target_description", "Building evaluation"),
        status="in_progress",
        building_context={
            **building_context,
            "occupant_profile": occupant_profile,
        },
    )

    session.add(evaluation)
    session.commit()

    try:
        # Step 2 + 3: map features and activate templates
        structured_inputs = dict(measured_features)
        active_templates = (
            session.query(TemplateRecord)
            .filter(TemplateRecord.dedup_status == "active")
            .order_by(TemplateRecord.display_id)
            .all()
        )

        activation_rows: list[dict[str, Any]] = []
        data_gaps: list[str] = []

        for record in active_templates:
            template_json = _load_template_json(record)
            required_inputs = _extract_required_inputs(template_json)

            if required_inputs:
                provided = {
                    key: structured_inputs[key]
                    for key in required_inputs
                    if key in structured_inputs
                }
                if not provided:
                    data_gaps.append(record.display_id)
                    continue
                partial = len(provided) < len(required_inputs)
                activation_reason = (
                    "partial inputs available" if partial else "all required inputs available"
                )
            else:
                provided = dict(structured_inputs)
                partial = False
                activation_reason = "no explicit inputs_required; activated with available features"

            activation = CMRTemplateActivation(
                evaluation_id=evaluation.id,
                template_display_id=record.display_id,
                activation_reason=activation_reason,
                inputs=provided,
                outputs=None,
                wis_score=None,
                wis_confidence=None,
                interaction_adjustments=[],
            )
            session.add(activation)
            session.flush()

            activation_rows.append(
                {
                    "record": record,
                    "json": template_json,
                    "activation": activation,
                    "inputs": provided,
                    "partial": partial,
                }
            )

        # Step 4 + 5: template computation and WIS conversion
        score_rows: list[dict[str, Any]] = []
        for row in activation_rows:
            record: TemplateRecord = row["record"]
            activation: CMRTemplateActivation = row["activation"]

            override = template_wis_overrides.get(record.display_id)
            if isinstance(override, (int, float)):
                output = {
                    "template": record.display_id,
                    "output_type": "override",
                    "wis_raw": float(override),
                }
            else:
                output = _template_compute(record.display_id, row["inputs"], occupant_age)

            wis_value = _extract_wis_raw(output)
            wis_confidence = CALIBRATION_CONFIDENCE.get(record.calibration_status, 0.5)
            if row["partial"]:
                wis_confidence *= 0.8

            activation.outputs = output
            activation.wis_score = max(0.0, min(100.0, wis_value))
            activation.wis_confidence = wis_confidence

            score_rows.append(
                {
                    "template": record.display_id,
                    "wis": activation.wis_score,
                    "domain": _infer_domain(record, row["json"]),
                    "calibration_confidence": record.calibration_status,
                    "activation": activation,
                }
            )

        # Step 6: interaction adjustments
        try:
            from src.cmr.interactions import apply_all_interactions
        except ImportError:  # pragma: no cover - defensive fallback
            apply_all_interactions = None

        if apply_all_interactions is not None and score_rows:
            interaction_input = [
                {"template": row["template"], "wis": row["wis"]}
                for row in score_rows
            ]
            interaction_rows = {
                row["template"]: row for row in apply_all_interactions(interaction_input)
            }
            for row in score_rows:
                updated = interaction_rows.get(row["template"])
                if not updated:
                    continue
                row["wis"] = float(updated.get("wis", row["wis"]))
                row["activation"].wis_score = row["wis"]
                row["activation"].interaction_adjustments = updated.get(
                    "interaction_adjustments", []
                )

        # Step 7: aggregate by domain
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in score_rows:
            grouped[row["domain"]].append(row)

        domain_outputs: list[dict[str, Any]] = []
        for domain, rows in sorted(grouped.items()):
            template_scores = [
                {"wis": item["wis"], "calibration_confidence": item["calibration_confidence"]}
                for item in rows
            ]
            domain_result = aggregate_domain_wis(template_scores)
            domain_wis = float(domain_result["domain_wis"])
            domain_confidence = min(1.0, max(0.1, 1.0 / math.sqrt(len(rows))))
            template_ids = ",".join(item["template"] for item in rows)

            session.add(
                CMRDomainScore(
                    evaluation_id=evaluation.id,
                    domain=domain,
                    wis_score=domain_wis,
                    wis_confidence=domain_confidence,
                    n_templates_activated=len(rows),
                    template_ids=template_ids,
                    aggregation_method="weighted_average",
                    weight_basis="calibration_confidence",
                )
            )
            domain_outputs.append(
                {
                    "domain": domain,
                    "wis": domain_wis,
                    "confidence": domain_confidence,
                    "n_templates": len(rows),
                    "template_ids": [item["template"] for item in rows],
                }
            )

        # Step 8: overall score
        overall_result = aggregate_overall_wis(
            [{"domain": d["domain"], "domain_wis": d["wis"]} for d in domain_outputs]
        )
        overall_wis = float(overall_result["overall_wis"])
        severe_deficits = list(overall_result["severe_deficits"])
        overall_confidence = (
            sum(item["confidence"] for item in domain_outputs) / len(domain_outputs)
            if domain_outputs
            else 0.0
        )

        session.add(
            CMROverallScore(
                evaluation_id=evaluation.id,
                wis_geometric_mean=overall_wis,
                wis_confidence=overall_confidence,
                n_domains_assessed=len(domain_outputs),
                severe_deficit_domains=",".join(severe_deficits) if severe_deficits else None,
                data_gaps=",".join(sorted(set(data_gaps))) if data_gaps else None,
            )
        )

        # Step 9: build report
        evaluation.status = "complete"
        session.commit()

        return {
            "evaluation_id": evaluation.id,
            "status": "complete",
            "overall_wis": overall_wis,
            "overall_confidence": overall_confidence,
            "domain_scores": domain_outputs,
            "severe_deficits": severe_deficits,
            "data_gaps": sorted(set(data_gaps)),
            "activated_templates": [row["template"] for row in score_rows],
        }
    except Exception:
        evaluation.status = "failed"
        session.commit()
        raise
    finally:
        session.close()

