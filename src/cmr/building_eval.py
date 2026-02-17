"""Building evaluation orchestrator (Doc 68 Part 3.1).
"""

from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
from typing import Iterable

from sqlalchemy.orm import Session

from src.cmr import models
from src.cmr.models import (
    CMREvaluation,
    CMRTemplateActivation,
    CMRDomainScore,
    CMROverallScore,
    TemplateRecord,
    get_session,
)
from src.cmr.interactions import apply_all_interactions
from src.cmr.feature_mapping import resolve_template_inputs
from src.cmr.template_computations import TEMPLATE_COMPUTE_FUNCTIONS
from src.cmr.wis import aggregate_domain_wis, aggregate_overall_wis
from src.cmr.lifespan_moderation import (
    compute_template_with_lifespan,
    extract_occupant_age,
)


def _select_templates(
    session: Session,
    limit: int = 12,
    template_records: Iterable[TemplateRecord] | None = None,
) -> list[TemplateRecord]:
    if template_records is not None:
        return list(template_records)
    return (
        session.query(TemplateRecord)
        .filter(TemplateRecord.dedup_status == "active")
        .order_by(TemplateRecord.series, TemplateRecord.display_id)
        .limit(limit)
        .all()
    )


def _load_required_inputs_from_json(json_path: str) -> list[str]:
    path = Path(json_path)
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    return list(payload.get("inputs_required", []) or [])


def evaluate_building(
    building_context: dict,
    measured_features: dict,
    occupant_profile: dict,
    *,
    db_path: str = "ae.db",
    session: Session | None = None,
    template_records: Iterable[TemplateRecord] | None = None,
) -> dict:
    """Run Steps 1-9 of the building evaluation pipeline."""

    session = session or get_session(db_path)
    models.Base.metadata.create_all(session.get_bind())
    template_wis_overrides = building_context.get("template_wis_overrides", {})
    declared_data_gaps = building_context.get("data_gaps", [])

    evaluation = CMREvaluation(
        evaluation_type="building",
        target_description=building_context.get(
            "target_description",
            building_context.get("building_name", "Unnamed Building"),
        ),
        status="in_progress",
        building_context={**building_context, "occupant_profile": occupant_profile},
    )
    session.add(evaluation)
    session.flush()

    templates = _select_templates(session, template_records=template_records)
    template_lookup = {template.display_id: template for template in templates}

    template_scores: list[dict] = []
    computed_data_gaps: list[str] = []
    for template in templates:
        mapped_inputs: dict = {}
        if template.display_id in TEMPLATE_COMPUTE_FUNCTIONS:
            mapped_inputs, missing_inputs = resolve_template_inputs(
                template.display_id,
                measured_features,
                occupant_profile,
            )
        else:
            required_inputs = _load_required_inputs_from_json(template.json_path)
            missing_inputs = [name for name in required_inputs if name not in measured_features]
            mapped_inputs = {name: measured_features[name] for name in required_inputs if name in measured_features}

        if missing_inputs:
            computed_data_gaps.append(template.display_id)
            continue

        # Step 4: Call real compute function with lifespan moderation
        # Check for explicit override first
        if template.display_id in template_wis_overrides:
            base_wis = float(template_wis_overrides[template.display_id])
            compute_outputs = {"base_wis": base_wis, "source": "override"}
            needs_computation = False
        else:
            # Try to compute using real template function with occupant age
            compute_result = compute_template_with_lifespan(
                template_id=template.display_id,
                measured_features=measured_features,
                occupant_profile=occupant_profile,
            )
            base_wis = float(compute_result.get("wis", 50.0))
            needs_computation = compute_result.get("needs_computation", True)
            compute_outputs = {
                "base_wis": base_wis,
                "source": "placeholder" if needs_computation else "computed",
                "lifespan_applied": compute_result.get("lifespan_applied", False),
                "age": compute_result.get("age"),
                "lifespan_multiplier": compute_result.get("lifespan_multiplier", 1.0),
            }
            if "raw_output" in compute_result:
                compute_outputs["raw_output"] = compute_result["raw_output"]

        activation = CMRTemplateActivation(
            evaluation_id=evaluation.id,
            template_display_id=template.display_id,
            activation_reason="auto: sufficient input features",
            inputs={
                "measured_features": measured_features,
                "occupant_profile": occupant_profile,
                "mapped_inputs": mapped_inputs,
            },
            outputs=compute_outputs,
            wis_score=base_wis,
            wis_confidence=5.0 if needs_computation else 7.0,
            interaction_adjustments=[],
        )
        session.add(activation)
        template_scores.append(
            {
                "template": template.display_id,
                "wis": base_wis,
                "calibration_confidence": template.calibration_status,
                "activation": activation,
                "interaction_adjustments": [],
                "lifespan_applied": compute_outputs.get("lifespan_applied", False),
            }
        )

    adjusted = apply_all_interactions(template_scores)

    domain_map: dict[str, list[dict]] = defaultdict(list)
    domain_templates: dict[str, list[str]] = defaultdict(list)

    for score in adjusted:
        activation: CMRTemplateActivation = score["activation"]
        activation.wis_score = float(score["wis"])
        activation.outputs = {"wis": float(score["wis"])}
        activation.interaction_adjustments = score.get("interaction_adjustments", [])

        template = template_lookup.get(score["template"])
        if not template:
            continue
        domain = template.series
        domain_map[domain].append(
            {
                "wis": float(score["wis"]),
                "calibration_confidence": score.get("calibration_confidence", 0.4),
            }
        )
        domain_templates[domain].append(template.display_id)

    domain_scores = []
    overall_input = []
    for domain, items in domain_map.items():
        agg = aggregate_domain_wis(items)
        domain_score = CMRDomainScore(
            evaluation_id=evaluation.id,
            domain=domain,
            wis_score=agg["domain_wis"],
            wis_confidence=min(100.0, agg.get("total_weight", 0.0) or 5.0),
            n_templates_activated=agg["template_count"],
            template_ids=",".join(domain_templates[domain]),
        )
        session.add(domain_score)
        domain_scores.append(
            {
                "domain": domain,
                "wis": agg["domain_wis"],
                "confidence": min(1.0, max(0.1, (agg.get("total_weight", 0.0) or 0.1) / 2.0)),
                "n_templates": agg["template_count"],
                "template_ids": domain_templates[domain],
            }
        )
        overall_input.append({"domain": domain, "domain_wis": agg["domain_wis"]})

    overall_result = aggregate_overall_wis(overall_input)
    overall = CMROverallScore(
        evaluation_id=evaluation.id,
        wis_geometric_mean=overall_result["overall_wis"],
        wis_confidence=min(100.0, overall_result.get("domain_count", 0) * 5.0 or 5.0),
        n_domains_assessed=overall_result.get("domain_count", 0),
        severe_deficit_domains=",".join(overall_result.get("severe_deficits", [])),
        data_gaps=",".join(declared_data_gaps),
    )
    session.add(overall)

    evaluation.status = "complete"
    session.commit()

    return {
        "evaluation_id": evaluation.id,
        "status": "complete",
        "domain_scores": domain_scores,
        "overall_wis": overall_result["overall_wis"],
        "overall_confidence": min(1.0, max(0.1, len(domain_scores) / 10.0)),
        "severe_deficits": overall_result.get("severe_deficits", []),
        "data_gaps": sorted(set(list(declared_data_gaps) + computed_data_gaps)),
        "activated_templates": [item["template"] for item in adjusted],
    }
