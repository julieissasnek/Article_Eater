import os
import json
import glob

TEMPLATE_DIR = "data/templates"

def repair_interactions():
    # 1. Build mappings
    templates = {}
    valid_ids = set()
    display_to_id = {}
    
    for filepath in glob.glob(os.path.join(TEMPLATE_DIR, "*.json")):
        with open(filepath, 'r') as f:
            data = json.load(f)
            tid = data.get("template_id")
            did = data.get("display_id")
            templates[filepath] = data
            if tid:
                valid_ids.add(tid)
            if did and tid:
                display_to_id[did] = tid
                
    # Add manual fallbacks for the ones we saw
    display_to_id["AX4_perceived_control"] = "AX_CONTROL_STRESS_004"
    display_to_id["IC2_body_budget"] = "IC_BODY_BUDGET_002"

    fixed_count = 0

    # 2. Iterate and repair
    for filepath, data in templates.items():
        modified = False
        
        # Repair interaction_templates
        int_templates = data.get("interaction_templates", [])
        new_int_templates = []
        
        cross_int = data.get("cross_template_interactions", {})
        
        if int_templates:
            for item in int_templates:
                if isinstance(item, dict):
                    # We have a dict! Move the id to the list, and description to cross_int
                    tid = item.get("id")
                    nature = item.get("nature")
                    if tid:
                        new_int_templates.append(tid)
                        if nature:
                            cross_int[tid] = nature
                        modified = True
                elif isinstance(item, str):
                    # Usually valid, but might be a display ID
                    if item not in valid_ids and item in display_to_id:
                        new_int_templates.append(display_to_id[item])
                        modified = True
                    else:
                        new_int_templates.append(item)
            
            if modified:
                data["interaction_templates"] = new_int_templates
                
        # Repair cross_template_interactions keys
        if cross_int and isinstance(cross_int, dict):
            new_cross_int = {}
            for k, v in cross_int.items():
                if k not in valid_ids:
                    # Try to map it
                    if k in display_to_id:
                        new_cross_int[display_to_id[k]] = v
                        modified = True
                    else:
                        new_cross_int[k] = v # leave unmapped
                else:
                    new_cross_int[k] = v
                    
            if modified:
                data["cross_template_interactions"] = new_cross_int
                
        if modified:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
            fixed_count += 1
            print(f"Repaired interactions in {os.path.basename(filepath)}")
            
    print(f"\nMigration complete. Total files repaired: {fixed_count}")

if __name__ == "__main__":
    repair_interactions()
