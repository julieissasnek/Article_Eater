#!/usr/bin/env python3
"""Sprint 10 Task 3.11: Primary school classroom worked example."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.cmr.building_eval import evaluate_building
from src.cmr.template_computations import (
    compute_l2_circadian_medi,
    compute_vf3_ceiling_height,
    get_lifespan_multiplier,
)


CLASSROOM_FEATURES = {
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


def _domain_map(result: dict[str, Any]) -> dict[str, float]:
    return {row["domain"]: float(row["wis"]) for row in result.get("domain_scores", [])}


def run_primary_school_classroom_example(db_path: str = "ae.db") -> dict[str, Any]:
    context = {
        "building_name": "Primary School Classroom Example",
        "building_type": "primary_school_classroom",
        "climate_zone": "3C",
    }

    age7_result = evaluate_building(
        building_context=context,
        measured_features=CLASSROOM_FEATURES,
        occupant_profile={"age": 7, "role": "student", "cultural_context": "Western"},
        db_path=db_path,
    )
    age35_result = evaluate_building(
        building_context=context,
        measured_features=CLASSROOM_FEATURES,
        occupant_profile={"age": 35, "role": "teacher", "cultural_context": "Western"},
        db_path=db_path,
    )

    age7_l2 = compute_l2_circadian_medi(
        medi_lux=CLASSROOM_FEATURES["illuminance_lux"],
        exposure_duration_hours=6.0,
        time_of_day="morning",
        occupant_age=7,
    )
    age35_l2 = compute_l2_circadian_medi(
        medi_lux=CLASSROOM_FEATURES["illuminance_lux"],
        exposure_duration_hours=6.0,
        time_of_day="morning",
        occupant_age=35,
    )
    age7_vf3 = compute_vf3_ceiling_height(
        CLASSROOM_FEATURES["ceiling_height_m"],
        CLASSROOM_FEATURES["floor_area_m2"],
        occupant_age=7,
    )
    age35_vf3 = compute_vf3_ceiling_height(
        CLASSROOM_FEATURES["ceiling_height_m"],
        CLASSROOM_FEATURES["floor_area_m2"],
        occupant_age=35,
    )

    age7_domains = _domain_map(age7_result)
    age35_domains = _domain_map(age35_result)
    all_domains = sorted(set(age7_domains.keys()) | set(age35_domains.keys()))
    domain_deltas = {
        domain: round(age7_domains.get(domain, 0.0) - age35_domains.get(domain, 0.0), 3)
        for domain in all_domains
    }

    summary = {
        "age_7_overall_wis": round(float(age7_result["overall_wis"]), 3),
        "age_35_overall_wis": round(float(age35_result["overall_wis"]), 3),
        "overall_delta_age7_minus_age35": round(
            float(age7_result["overall_wis"]) - float(age35_result["overall_wis"]),
            3,
        ),
        "domain_deltas_age7_minus_age35": domain_deltas,
    }

    interpretation = {
        "building_eval_status": "pipeline_runs_for_both_profiles",
        "dev_moderation_visible_in_building_eval": any(abs(v) > 0.01 for v in domain_deltas.values()),
        "template_level_age_signal": {
            "lifespan_multiplier_age_7": get_lifespan_multiplier(7),
            "lifespan_multiplier_age_35": get_lifespan_multiplier(35),
            "l2_ratio_age_7": round(age7_l2.value, 3),
            "l2_ratio_age_35": round(age35_l2.value, 3),
            "vf3_lifespan_multiplier_age_7": age7_vf3.details.get("lifespan_multiplier"),
            "vf3_lifespan_multiplier_age_35": age35_vf3.details.get("lifespan_multiplier"),
        },
        "note": (
            "Current orchestrator output remains flat across ages for this scenario. "
            "Age sensitivity is observable in template-level computations "
            "(e.g., lifespan multipliers and age-corrected L2 threshold ratio)."
        ),
    }

    return {
        "scenario": "primary_school_classroom",
        "context": context,
        "features": CLASSROOM_FEATURES,
        "age_7_result": age7_result,
        "age_35_result": age35_result,
        "summary": summary,
        "interpretation": interpretation,
    }


def main() -> int:
    report = run_primary_school_classroom_example()
    out_path = Path("data/review/sprint10_classroom_worked_example.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    print(f"\nWrote detailed report to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
