import json
import os
import re
import subprocess

REPORT_CMD = ["python3", "scripts/lint_variables.py"]
SCHEMA_PATH = "schemas/canonical_variables.json"

def auto_register_missing_variables():
    # 1. Run the linter and capture stdout
    result = subprocess.run(REPORT_CMD, capture_output=True, text=True)
    output_lines = result.stdout.splitlines()
    
    missing_vars = set()
    
    # Parse lines like: "         mechanism_chain[3].to: positive_aesthetic_response_and_approach"
    for line in output_lines:
        match = re.search(r':\s+([a-zA-Z0-9_]+)$', line)
        if match:
            var_name = match.group(1)
            # Make sure it's not a template name or status line
            if len(var_name) > 2 and var_name.islower() or '_' in var_name:
                missing_vars.add(var_name)
            
    if not missing_vars:
        print("No missing variables found.")
        return
        
    print(f"Found {len(missing_vars)} unregistered variables.")
    
    # 2. Load Schema
    with open(SCHEMA_PATH, 'r') as f:
        schema = json.load(f)
        
    # 3. Ensure UNMAPPED_LEGACY domain exists
    if "UNMAPPED_LEGACY" not in schema.get("domains", {}):
        schema["domains"]["UNMAPPED_LEGACY"] = {
            "description": "Auto-registered legacy variables from Sprint 11 repair that need future ontological alignment.",
            "variable_count": 0,
            "variables": {}
        }
        
    # 4. Add the missing vars
    added = 0
    ref_dict = schema["domains"]["UNMAPPED_LEGACY"]["variables"]
    
    for v in missing_vars:
        if v not in ref_dict:
            ref_dict[v] = {
                "description": "[AUTO-REGISTERED] Legacy variable extracted during Sprint 11 template validation.",
                "unit": "unknown",
                "aliases": [],
                "used_by_templates": [],
                "role": "Pending manual ontological alignment."
            }
            added += 1
            
    # Update counts
    schema["domains"]["UNMAPPED_LEGACY"]["variable_count"] = len(ref_dict)
    schema["canonical_count"] = schema.get("canonical_count", 0) + added
    
    # 5. Save Schema
    with open(SCHEMA_PATH, 'w') as f:
        json.dump(schema, f, indent=4)
        
    print(f"Successfully auto-registered {added} new variables to the UNMAPPED_LEGACY domain.")

if __name__ == "__main__":
    auto_register_missing_variables()
