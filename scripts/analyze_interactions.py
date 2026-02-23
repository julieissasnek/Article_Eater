import os
import json
import glob

TEMPLATE_DIR = "data/templates"

def audit_interactions():
    valid_ids = set()
    display_to_id = {}
    templates = {}
    
    # Pass 1: Gather all valid IDs
    for filepath in glob.glob(os.path.join(TEMPLATE_DIR, "*.json")):
        with open(filepath, 'r') as f:
            data = json.load(f)
            tid = data.get("template_id")
            did = data.get("display_id")
            if tid:
                valid_ids.add(tid)
            if did and tid:
                display_to_id[did] = tid
            templates[filepath] = data

    print(f"Found {len(valid_ids)} valid template IDs.")
    print(f"Found {len(display_to_id)} valid display IDs.")

    # Let's see what is broken and how we can map it
    broken_interactions = set()
    broken_cross_keys = set()
    
    for filepath, data in templates.items():
        # Check interaction_templates
        int_templates = data.get("interaction_templates", [])
        if int_templates:
            for item in int_templates:
                if isinstance(item, dict):
                    print(f"[DICT ENTRY] {data.get('template_id')}: {item}")
                elif isinstance(item, str):
                    if item not in valid_ids:
                        broken_interactions.add(item)
                
        # Check cross_template_interactions
        cross_int = data.get("cross_template_interactions", {})
        if cross_int and isinstance(cross_int, dict):
            for key in cross_int.keys():
                if key not in valid_ids:
                    broken_cross_keys.add(key)
                    
    print("\nBroken interaction_template string IDs:")
    for b in sorted(broken_interactions):
        print(f"  - {b}")
        
    print("\nBroken cross_template_interactions keys:")
    for k in sorted(broken_cross_keys):
        # Can we map it?
        if k in display_to_id:
            print(f"  - {k} -> maps to {display_to_id[k]}")
        else:
            print(f"  - {k} -> NO MAP FOUND")

if __name__ == "__main__":
    audit_interactions()
