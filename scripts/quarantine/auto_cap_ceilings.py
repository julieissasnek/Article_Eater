import json
import re
from pathlib import Path

def auto_cap_ceilings():
    base_dir = Path("/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1")
    report_path = base_dir / "data" / "ceiling_violation_report.json"
    templates_dir = base_dir / "data" / "templates"
    
    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)
        
    violations = report.get("violations", [])
    
    updates_by_tid = {}
    for v in violations:
        tid = v["template_id"]
        field_path = v["field_path"]
        ceiling = v["ceiling"]
        if tid not in updates_by_tid:
            updates_by_tid[tid] = []
        updates_by_tid[tid].append((field_path, ceiling))
        
    files_changed = 0
    total_caps = 0
    
    json_paths = list(templates_dir.glob("*.json"))
    
    for json_path in json_paths:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        tid = data.get("template_id", json_path.stem)
        
        if tid in updates_by_tid:
            updates = updates_by_tid[tid]
            changed = False
            
            for field_path, ceiling in updates:
                if field_path == "bridge_warrant":
                    if "confidence" in data:
                        data["confidence"] = ceiling
                        changed = True
                        total_caps += 1
                elif field_path.startswith("mechanism_chain["):
                    match = re.match(r"mechanism_chain\[(\d+)\]\.confidence", field_path)
                    if match:
                        idx_1_based = int(match.group(1))
                        idx = idx_1_based - 1
                        chain = data.get("mechanism_chain", [])
                        if 0 <= idx < len(chain):
                            if "confidence" in chain[idx]:
                                chain[idx]["confidence"] = ceiling
                                changed = True
                                total_caps += 1
                                
            if changed:
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                files_changed += 1

    print(f"Applied {total_caps} hard ceilings across {files_changed} templates.")

if __name__ == "__main__":
    auto_cap_ceilings()
