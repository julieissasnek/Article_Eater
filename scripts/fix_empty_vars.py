import json
import os
from pathlib import Path

files = [
    "AX3_AWE_MECHANISM_001.json",
    "AX3_SMALL_SELF_001.json",
    "ER_ECOLOGICAL_RATIONALITY_001.json",
    "TEMPORAL_HIERARCHY_ARCH_PE_001.json"
]

base_dir = Path("/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/data/templates")
schema_path = Path("/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/schemas/canonical_variables.json")

extracted_vars = set()

for filename in files:
    path = base_dir / filename
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    chain = data.get("mechanism_chain", [])
    for step in chain:
        if step.get("from") == "" and step.get("to") == "":
            desc = step.get("description", "")
            if "->" in desc:
                parts = desc.split("->")
                step["from"] = parts[0].strip()
                step["to"] = parts[1].strip()
                extracted_vars.add(step["from"])
                extracted_vars.add(step["to"])
            elif "→" in desc:
                parts = desc.split("→")
                step["from"] = parts[0].strip()
                step["to"] = parts[1].strip()
                extracted_vars.add(step["from"])
                extracted_vars.add(step["to"])
                
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

print(f"Fixed files. Discovered new variables: {extracted_vars}")

if extracted_vars:
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    unmapped_domain = schema["domains"]["UNMAPPED_LEGACY"]["variables"]
    for var in extracted_vars:
        if var and var not in unmapped_domain:
            unmapped_domain[var] = {
                "description": "[AUTO-REGISTERED] Recovered from empty mechanism string.",
                "unit": "unknown",
                "aliases": [],
                "used_by_templates": [],
                "role": "Pending manual ontological alignment."
            }
    with open(schema_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=4)
