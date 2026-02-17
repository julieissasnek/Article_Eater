"""Sprint 10 worked examples for CMR evaluation."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict, Tuple

from src.cmr.building_eval import evaluate_building
from src.cmr.models import TemplateRecord
from src.cmr.template_computations import (
    ComputeResult,
    OutputType,
    compute_l1_luminance_contrast,
    compute_l2_circadian_medi,
    compute_l3_daylight_composite,
    compute_mat2_thermal_adaptive,
    compute_sc1_spatial_integration,
    compute_soc2_privacy_encounter,
    compute_tp1_motor_pe,
    compute_vf3_ceiling_height,
    compute_view1_vqi,
)


PRIMARY_SCHOOL_CLASSROOM: Dict[str, Any] = {
    "ceiling_height_m": 3.0,
    "floor_area_m2": 60.0,
    "illuminance_lux": 400,
    "ambient_noise_dba": 40,
    "window_area_ratio": 0.30,
    "primary_material": "timber_frame",
    "secondary_material": "linoleum",
    "has_nature_view": True,
    "rt60_seconds": 0.4,
    "view_content": "playground_trees",
}


def _clamp_wis(value: float) -> float:
    return max(0.0, min(100.0, value))


def _to_base_wis(result: ComputeResult) -> float:
    """Normalize heterogeneous compute outputs to a common 0-100 WIS scale."""
    if result.output_type == OutputType.SCORE:
        if result.unit == "score_0_1":
            return result.value * 100.0
        if result.unit in {"vqi_0_100", "wis_0_100"}:
            return result.value
        return result.value * 100.0 if result.value <= 1.0 else result.value

    if result.output_type == OutputType.RATIO:
        return result.value * 100.0

    if result.output_type == OutputType.THRESHOLD:
        # 55 at threshold, then linear up/down slope around it.
        return 55.0 + 25.0 * (result.value - 1.0)

    if result.output_type == OutputType.GOLDILOCKS:
        zone_to_wis = {
            "confinement": 25.0,
            "standard": 55.0,
            "liberating": 82.0,
            "expansive": 75.0,
            "awe": 35.0,
            "comfort": 65.0,
            "aesthetic": 85.0,
            "dramatic": 55.0,
            "glare": 25.0,
            "neutral": 78.0,
            "alliesthesia": 65.0,
            "discomfort": 25.0,
        }
        return zone_to_wis.get(result.zone or "", 50.0)

    return 50.0


def _apply_lifespan_moderation(base_wis: float, result: ComputeResult) -> float:
    """
    Apply developmental/lifespan moderation around the neutral point (50).

    This uses multipliers emitted by template computations so children in
    supportive environments get stronger positive uplift, and in adverse
    environments receive stronger penalties.
    """
    details = result.details or {}
    multiplier = 1.0
    for key in ("restoration_multiplier", "lifespan_multiplier"):
        value = details.get(key)
        if isinstance(value, (int, float)):
            multiplier = max(multiplier, float(value))
    moderated = 50.0 + (base_wis - 50.0) * multiplier
    return _clamp_wis(moderated)


def _template_record_stub(display_id: str, series: str, root: Path) -> TemplateRecord:
    payload_path = root / f"{display_id}.json"
    payload_path.write_text(json.dumps({"inputs_required": []}), encoding="utf-8")
    return TemplateRecord(
        template_id=f"{display_id}_WORKED_EXAMPLE_001",
        display_id=display_id,
        name=display_id,
        series=series,
        generation=2,
        dedup_status="active",
        superseded_by=None,
        pe_contribution="organizational",
        maturity="supported",
        calibration_status="partial",
        practical_accessibility="B",
        ecological_validation=False,
        json_path=str(payload_path),
        source_docs="68,61",
    )


def _compute_classroom_overrides(age: int) -> Dict[str, float]:
    """Compute age-specific template overrides for the classroom scenario."""
    vf3 = compute_vf3_ceiling_height(3.0, 60.0, age)
    l1 = compute_l1_luminance_contrast(0.8, age)
    l2 = compute_l2_circadian_medi(350.0, 3.0, "morning", age)
    view1 = compute_view1_vqi("nature", 3, 0.30, 0.75, True, age)
    mat2 = compute_mat2_thermal_adaptive(23.5, 20.0, age)
    sc1 = compute_sc1_spatial_integration(0.72, 0.78, 2, False, False, age)
    soc2 = compute_soc2_privacy_encounter(0.48, 0.13, 0.05, 0.72, 50.0, age)
    tp1 = compute_tp1_motor_pe("stairs_optimal", 165, 0.65, age)

    l3 = compute_l3_daylight_composite(
        max(0.0, min(1.0, l2.value)),
        max(0.0, min(1.0, view1.value / 100.0)),
        0.8,
        0.7,
        0.8,
        age,
    )

    raw_results: Dict[str, ComputeResult] = {
        "VF3": vf3,
        "L1": l1,
        "L2": l2,
        "L3": l3,
        "MAT2": mat2,
        "SC1": sc1,
        "SOC2": soc2,
        "VIEW1": view1,
        "TP1": tp1,
    }

    overrides: Dict[str, float] = {}
    for template_id, result in raw_results.items():
        base = _to_base_wis(result)
        moderated = _apply_lifespan_moderation(base, result)
        overrides[template_id] = round(moderated, 2)
    return overrides


def _domain_map(report: Dict[str, Any]) -> Dict[str, float]:
    return {row["domain"]: float(row["wis"]) for row in report.get("domain_scores", [])}


def run_primary_school_classroom_example(db_path: str = "ae.db") -> Dict[str, Any]:
    """
    Task 3.11 worked example: compare age 7 vs age 35 in the same classroom.
    """
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        templates = [
            _template_record_stub("VF3", "VF", root),
            _template_record_stub("L1", "L", root),
            _template_record_stub("L2", "L", root),
            _template_record_stub("L3", "L", root),
            _template_record_stub("MAT2", "MAT", root),
            _template_record_stub("SC1", "SC", root),
            _template_record_stub("SOC2", "SOC", root),
            _template_record_stub("VIEW1", "VIEW", root),
            _template_record_stub("TP1", "TP", root),
        ]

        child_age = 7
        teacher_age = 35

        child_report = evaluate_building(
            building_context={
                "building_name": "Primary School Classroom (Task 3.11)",
                "template_wis_overrides": _compute_classroom_overrides(child_age),
            },
            measured_features=dict(PRIMARY_SCHOOL_CLASSROOM),
            occupant_profile={"age": child_age, "cultural_context": "Western"},
            db_path=db_path,
            template_records=templates,
        )

        teacher_report = evaluate_building(
            building_context={
                "building_name": "Primary School Classroom (Task 3.11)",
                "template_wis_overrides": _compute_classroom_overrides(teacher_age),
            },
            measured_features=dict(PRIMARY_SCHOOL_CLASSROOM),
            occupant_profile={"age": teacher_age, "cultural_context": "Western"},
            db_path=db_path,
            template_records=templates,
        )

    child_domains = _domain_map(child_report)
    teacher_domains = _domain_map(teacher_report)
    deltas: Dict[str, float] = {}
    for key in sorted(set(child_domains) | set(teacher_domains)):
        deltas[key] = round(child_domains.get(key, 0.0) - teacher_domains.get(key, 0.0), 2)

    return {
        "scenario": dict(PRIMARY_SCHOOL_CLASSROOM),
        "profiles": {
            "child_age_7": {
                "overall_wis": float(child_report["overall_wis"]),
                "domain_scores": child_domains,
            },
            "teacher_age_35": {
                "overall_wis": float(teacher_report["overall_wis"]),
                "domain_scores": teacher_domains,
            },
        },
        "delta_child_minus_teacher": {
            "overall_wis": round(
                float(child_report["overall_wis"]) - float(teacher_report["overall_wis"]), 2
            ),
            "domain_scores": deltas,
        },
    }

