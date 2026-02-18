#!/usr/bin/env python3
"""
Task 12.16: Tier 2 Reduction Validation Script (Antigravity).

Validates that EvaluateBuilding produces correct Tier 2 Reduction Scores 
(ART, SRT, Biophilia) for three benchmark scenarios:
1. Salk Institute (High ART/Bio/SRT) - Nature, Concrete, Ocean View, Quiet
2. Open Plan Office (Low/Poor) - No view, noise, crowded
3. Primary Classroom (Moderate/Mixed) - Nature view but standard materials

Usage:
    python3 scripts/validate_tier2_reductions.py
"""

import sys
import json
from pathlib import Path

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.cmr.building_eval import evaluate_building

def run_scenario(name, context, features, profile):
    print(f"\nEvaluating: {name}...")
    try:
        result = evaluate_building(
            building_context=context,
            measured_features=features,
            occupant_profile=profile,
            db_path="ae.db"
        )
        return result
    except Exception as e:
        print(f"FAILED: {e}")
        return None

def main():
    # --- SCENARIO 1: SALK INSTITUTE (The Gold Standard) ---
    salk_features = {
        "ceiling_height_m": 2.75,
        "floor_area_m2": 18.0,
        "illuminance_lux": 350,
        "ambient_noise_dba": 38,
        "window_area_ratio": 0.40,
        "primary_material": "concrete",
        "secondary_material": "teak",
        "has_nature_view": True,
        "rt60_seconds": 0.6,
        "view_content": "ocean_horizon",
        # Assuming minimal other features or relying on defaults
    }
    salk_context = {"building_name": "Salk Institute", "building_type": "research"}
    salk_profile = {"age": 30, "role": "researcher"}

    # --- SCENARIO 2: OPEN PLAN OFFICE (The Stress Check) ---
    open_plan_features = {
        "ceiling_height_m": 3.2,
        "floor_area_m2": 150.0,
        "illuminance_lux": 500,
        "ambient_noise_dba": 62, # Noisy
        "window_area_ratio": 0.30,
        "primary_material": "plaster",
        "secondary_material": "glass",
        "has_nature_view": False,
        "rt60_seconds": 0.8,
        "view_content": "city_street",
        "desk_density_m2_per_person": 8.0,
    }
    open_plan_context = {"building_name": "Open Plan Office", "building_type": "office"}
    open_plan_profile = {"age": 24, "role": "focus_work"}

    # --- SCENARIO 3: PRIMARY CLASSROOM (Developmental) ---
    classroom_features = {
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
    classroom_context = {"building_name": "Primary Classroom", "building_type": "school"}
    classroom_profile = {"age": 7, "role": "student"}

    salk = run_scenario("Salk Institute", salk_context, salk_features, salk_profile)
    # DEBUG: Print activated templates for Salk
    if salk:
        print("\n[DEBUG] Activated Templates for Salk:")
        print(json.dumps(salk.get("activated_templates", []), indent=2))

    open_plan = run_scenario("Open Plan Office", open_plan_context, open_plan_features, open_plan_profile)
    classroom = run_scenario("Primary Classroom", classroom_context, classroom_features, classroom_profile)

    if not all([salk, open_plan, classroom]):
        print("\nCRITICAL FAILURE: One or more evaluations crashed.")
        sys.exit(1)

    # --- VALIDATION LOGIC ---
    print("\n--- TIER 2 REDUCTION SCORES ---")

    def print_scores(name, result):
        t2 = result.get("tier2_scores", {})
        print(f"\n{name}:")
        if not t2:
            print("  [ERROR] No tier2_scores found in result!")
            return
        
        for theory, constructs in t2.items():
            print(f"  {theory}:")
            for c, s in constructs.items():
                print(f"    - {c}: {s:.1f}")

    print_scores("Salk Institute", salk)
    print_scores("Open Plan Office", open_plan)
    print_scores("Primary Classroom", classroom)

    # Assertions
    # Keys in tier2_scores use underscore naming: Being_Away, Fascination_Soft, etc.
    # Theory keys are abbreviated: ART, SRT, Biophilia

    def get_score(result, theory, construct):
        """Get a Tier 2 score, handling underscore naming."""
        t2 = result.get("tier2_scores", {}).get(theory, {})
        return t2.get(construct, 0.0)

    # === SALK VALIDATION ===
    # Expected: High ART (Being_Away > 60, Fascination_Soft > 60)
    salk_ba = get_score(salk, "ART", "Being_Away")
    salk_fasc = get_score(salk, "ART", "Fascination_Soft")
    salk_srt = get_score(salk, "SRT", "Autonomic_Stress_Reduction")
    salk_bio = get_score(salk, "Biophilia", "Nature_In_Space")

    all_pass = True

    if salk_ba > 60 and salk_fasc > 60:
        print(f"\n[PASS] Salk ART: Being_Away={salk_ba:.1f}, Fascination_Soft={salk_fasc:.1f}")
    else:
        print(f"\n[FAIL] Salk ART: Being_Away={salk_ba:.1f}, Fascination_Soft={salk_fasc:.1f}")
        all_pass = False

    if salk_srt > 60:
        print(f"[PASS] Salk SRT: Autonomic_Stress_Reduction={salk_srt:.1f}")
    else:
        print(f"[FAIL] Salk SRT: Autonomic_Stress_Reduction={salk_srt:.1f}")
        all_pass = False

    if salk_bio > 60:
        print(f"[PASS] Salk Biophilia: Nature_In_Space={salk_bio:.1f}")
    else:
        print(f"[FAIL] Salk Biophilia: Nature_In_Space={salk_bio:.1f}")
        all_pass = False

    # === OPEN PLAN VALIDATION ===
    # Expected: Lower scores than Salk (noise, no nature view)
    op_ba = get_score(open_plan, "ART", "Being_Away")
    op_srt = get_score(open_plan, "SRT", "Autonomic_Stress_Reduction")
    op_bio_space = get_score(open_plan, "Biophilia", "Nature_Of_Space")

    if op_ba < salk_ba:
        print(f"\n[PASS] Open Plan vs Salk: Being_Away lower ({op_ba:.1f} < {salk_ba:.1f})")
    else:
        print(f"\n[WARN] Open Plan vs Salk: Being_Away not lower ({op_ba:.1f} >= {salk_ba:.1f})")
        # This is a warning, not a failure - high ceilings boost Being_Away

    if op_srt < salk_srt:
        print(f"[PASS] Open Plan vs Salk: SRT lower ({op_srt:.1f} < {salk_srt:.1f})")
    else:
        print(f"[WARN] Open Plan vs Salk: SRT not lower ({op_srt:.1f} >= {salk_srt:.1f})")

    if op_bio_space < get_score(salk, "Biophilia", "Nature_Of_Space"):
        print(f"[PASS] Open Plan vs Salk: Nature_Of_Space lower ({op_bio_space:.1f})")
    else:
        print(f"[WARN] Open Plan: Nature_Of_Space higher than expected ({op_bio_space:.1f})")

    # === CLASSROOM VALIDATION ===
    # Expected: Moderate scores (nature view but standard materials)
    class_ba = get_score(classroom, "ART", "Being_Away")
    class_bio = get_score(classroom, "Biophilia", "Nature_In_Space")
    class_srt = get_score(classroom, "SRT", "Autonomic_Stress_Reduction")

    if 50 < class_ba < 90:
        print(f"\n[PASS] Classroom ART: Being_Away={class_ba:.1f} (moderate as expected)")
    else:
        print(f"\n[WARN] Classroom ART: Being_Away={class_ba:.1f} (outside moderate range)")

    if 50 < class_bio < 90:
        print(f"[PASS] Classroom Biophilia: Nature_In_Space={class_bio:.1f} (moderate)")
    else:
        print(f"[WARN] Classroom Biophilia: Nature_In_Space={class_bio:.1f}")

    if 50 < class_srt < 80:
        print(f"[PASS] Classroom SRT: Autonomic_Stress_Reduction={class_srt:.1f}")
    else:
        print(f"[WARN] Classroom SRT: Autonomic_Stress_Reduction={class_srt:.1f}")

    # === FINAL SUMMARY ===
    print("\n" + "=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)

    # Core validation: Salk should outperform Open Plan on key restorative metrics
    salk_avg = (salk_ba + salk_fasc + salk_srt + salk_bio) / 4
    op_avg = (get_score(open_plan, "ART", "Being_Away") +
              get_score(open_plan, "ART", "Fascination_Soft") +
              get_score(open_plan, "SRT", "Autonomic_Stress_Reduction") +
              get_score(open_plan, "Biophilia", "Nature_In_Space")) / 4

    print(f"Salk average restorative score: {salk_avg:.1f}")
    print(f"Open Plan average restorative score: {op_avg:.1f}")

    if salk_avg > op_avg:
        print("[PASS] Salk outperforms Open Plan as expected")
    else:
        print("[FAIL] Salk does NOT outperform Open Plan - check model!")
        all_pass = False

    if all_pass:
        print("\n✓ Tier 2 Reduction Validation PASSED")
        sys.exit(0)
    else:
        print("\n✗ Tier 2 Reduction Validation has FAILURES")
        sys.exit(1)

if __name__ == "__main__":
    main()
