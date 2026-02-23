import json
import os
import glob
import collections

TEMPLATE_DIR = "data/templates"
SCHEMA_PATH = "schemas/canonical_variables.json"

def fix_variables():
    # 1. Build Reverse Mapping (Alias -> Canonical)
    with open(SCHEMA_PATH, 'r') as f:
        schema = json.load(f)
        
    alias_map = {}
    canonical_vars = set()
    
    for domain, domain_data in schema.get("domains", {}).items():
        for var_name, var_data in domain_data.get("variables", {}).items():
            canonical_vars.add(var_name)
            for alias in var_data.get("aliases", []):
                alias_map[alias] = var_name

    fixed_files = 0
    total_replacements = 0

    # 2. Iterate through all templates and find/replace
    for filepath in glob.glob(os.path.join(TEMPLATE_DIR, "*.json")):
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        modified = False
        
        # A. Fix mechanism chains
        for step in data.get("mechanism_chain", []) + data.get("mechanism_steps", []):
            if "from" in step and step["from"] in alias_map:
                step["from"] = alias_map[step["from"]]
                modified = True
                total_replacements += 1
                
            if "to" in step and step["to"] in alias_map:
                step["to"] = alias_map[step["to"]]
                modified = True
                total_replacements += 1
                
        # B. Fix calibrated parameters keys
        cal_params = data.get("calibrated_parameters", {})
        if cal_params:
            new_params = {}
            for k, v in cal_params.items():
                new_key = alias_map.get(k, k)
                if new_key != k:
                    modified = True
                    total_replacements += 1
                # Check nested modifiers if they exist
                if isinstance(v, dict):
                    new_nested = {}
                    for sub_k, sub_v in v.items():
                        new_sub = alias_map.get(sub_k, sub_k)
                        if new_sub != sub_k:
                            modified = True
                            total_replacements += 1
                        new_nested[new_sub] = sub_v
                    new_params[new_key] = new_nested
                else:
                    new_params[new_key] = v
            data["calibrated_parameters"] = new_params
            
        # C. Fix population and architectural modifiers top level
        for mod_field in ["population_modifiers", "architectural_modifiers"]:
            mods = data.get(mod_field, {})
            if mods and isinstance(mods, dict):
                new_mods = {}
                for k, v in mods.items():
                    new_key = alias_map.get(k, k)
                    if new_key != k:
                        modified = True
                        total_replacements += 1
                    new_mods[new_key] = v
                data[mod_field] = new_mods

        if modified:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
            fixed_files += 1
            print(f"Fixed aliases in: {filepath}")

    print(f"\nMigration complete.")
    print(f"Total files bumped: {fixed_files}")
    print(f"Total variables canonicalized: {total_replacements}")

if __name__ == "__main__":
    fix_variables()
