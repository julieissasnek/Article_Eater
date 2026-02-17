
import sys
import os
import json
sys.path.append(os.getcwd())
from src.cmr.building_eval import evaluate_building

def run_open_plan_evaluation():
    # Common Building Context
    building_context = {
        "building_name": "TechHub Open Plan Zone A",
        "building_type": "office",
        "climate_zone": "4C",
        "template_wis_overrides": {} # Can inject overrides if needed
    }

    # Measured Features (Open Plan Office)
    measured_features = {
        "ceiling_height_m": 3.2,
        "floor_area_m2": 150.0, # Large zone
        "illuminance_lux": 500, # Standard office
        "ambient_noise_dba": 62, # Noisy!
        "window_area_ratio": 0.30,
        "primary_material": "plaster",
        "secondary_material": "glass",
        "has_nature_view": False,
        "rt60_seconds": 0.8, # Slightly echoy
        "view_content": "city_street",
        "desk_density_m2_per_person": 8.0 # Crowded
    }

    # Occupant Profiles
    profiles = [
        {
            "name": "Junior Dev (Introvert)",
            "age": 24,
            "cultural_context": "Western",
            "personality_type": "introvert", # System might not use this yet, but good for reporting
            "role": "focus_work"
        },
        {
            "name": "Sales Lead (Extrovert)",
            "age": 45,
            "cultural_context": "Western",
            "personality_type": "extrovert",
            "role": "collaboration"
        },
        {
            "name": "Neurodivergent Engineer",
            "age": 30,
            "cultural_context": "Western",
            "neurodiversity": "high_sensitivity", # Testing if system picks this up
            "role": "focus_work"
        }
    ]

    print(f"EVALUATING: {building_context['building_name']}\n")
    print(f"Features: {json.dumps(measured_features, indent=2)}\n")

    for profile in profiles:
        print(f"--- Profile: {profile['name']} ({profile['age']}) ---")
        try:
            result = evaluate_building(
                building_context=building_context,
                measured_features=measured_features,
                occupant_profile=profile,
                db_path="ae.db"
            )
            
            print(f"Overall WIS: {result['overall_wis']:.1f}")
            print(f"Confidence: {result['overall_confidence']:.2f}")
            print("Domain Scores:")
            for ds in result['domain_scores']:
                print(f"  - {ds['domain']}: {ds['wis']:.1f} ({ds['n_templates']} templates)")
            
            if result['severe_deficits']:
                print(f"SEVERE DEFICITS: {result['severe_deficits']}")
            
            if result['data_gaps']:
                print(f"Data Gaps: {len(result['data_gaps'])}")
            
            print("\n")

        except Exception as e:
            print(f"FAILED: {e}\n")

if __name__ == "__main__":
    run_open_plan_evaluation()
