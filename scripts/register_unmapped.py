import sys
import json
from pathlib import Path

repo_root = Path("/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1")
sys.path.append(str(repo_root))

from scripts.lint_variables import load_registered_variables, lint_template
import glob

def register_unmapped():
    schema_path = repo_root / "schemas/canonical_variables.json"
    registered = load_registered_variables(str(schema_path))
    template_files = sorted(glob.glob(str(repo_root / "data/templates/*.json")))
    
    unregistered_set = set()
    for filepath in template_files:
        issues = lint_template(filepath, registered)
        for _, var in issues:
            if var and isinstance(var, str):
                unregistered_set.add(var)
    
    unregistered_set = {v for v in unregistered_set if v.strip()}
    print(f"Found {len(unregistered_set)} unique unregistered variables.")
    
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
        
    unmapped_domain = schema["domains"]["UNMAPPED_LEGACY"]["variables"]
    
    added_count = 0
    for var in sorted(unregistered_set):
        if var not in unmapped_domain:
            unmapped_domain[var] = {
                "description": "[AUTO-REGISTERED] Legacy variable extracted during Sprint 11 template validation.",
                "unit": "unknown",
                "aliases": [],
                "used_by_templates": [],
                "role": "Pending manual ontological alignment."
            }
            added_count += 1
            
    with open(schema_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=4)
        
    print(f"Added {added_count} new variables to UNMAPPED_LEGACY.")

if __name__ == "__main__":
    register_unmapped()
