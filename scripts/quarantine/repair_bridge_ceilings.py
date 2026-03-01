import json
import re
import os

report_file = "docs/CEILING_VIOLATION_REPORT.md"
templates_dir = "data/templates"

def repair_ceilings():
    if not os.path.exists(report_file):
        print(f"Report file {report_file} not found.")
        return

    with open(report_file, 'r') as f:
        lines = f.readlines()

    # Regex to parse lines like:
    # - ED_RECONSOLIDATION_001 | mechanism_chain[3].confidence | conf=0.45 | ceiling=0.35 | Δ=0.100 | suggestion: REVIEW
    pattern = re.compile(r'- ([A-Za-z0-9_]+) \| (.*?) \| conf=[0-9.]+ \| ceiling=([0-9.]+) \|')

    updates_by_template = {}

    for line in lines:
        match = pattern.search(line)
        if match:
            template_id = match.group(1).strip()
            path = match.group(2).strip()
            ceiling = float(match.group(3).strip())
            
            if template_id not in updates_by_template:
                updates_by_template[template_id] = []
                
            updates_by_template[template_id].append((path, ceiling))

    total_fixed = 0
    for template_id, updates in updates_by_template.items():
        # Find the actual json file
        # The template_id is usually the filename, but not always (e.g., T14 is T14.json, but some might differ)
        json_path = os.path.join(templates_dir, f"{template_id}.json")
        
        # If it doesn't exist, try to find it
        if not os.path.exists(json_path):
            found = False
            for fname in os.listdir(templates_dir):
                if fname.endswith(".json"):
                    with open(os.path.join(templates_dir, fname), 'r') as tf:
                        try:
                            tdata = json.load(tf)
                            if tdata.get("template_id") == template_id:
                                json_path = os.path.join(templates_dir, fname)
                                found = True
                                break
                        except:
                            pass
            if not found:
                print(f"Template {template_id} not found.")
                continue

        with open(json_path, 'r') as f:
            data = json.load(f)

        dirty = False
        for path, ceiling in updates:
            # Handle path like mechanism_chain[3].confidence or bridge_warrant or calibrated_parameters...
            if path == 'bridge_warrant':
                # The report says path is bridge_warrant but it implies the top-level confidence
                if data.get('confidence', 0) > ceiling:
                    print(f"Fixing {template_id} top-level confidence to {ceiling}")
                    data['confidence'] = ceiling
                    dirty = True
            elif path.startswith("mechanism_chain["):
                # e.g., mechanism_chain[3].confidence
                idx_match = re.search(r'\[(\d+)\]', path)
                if idx_match:
                    idx = int(idx_match.group(1))
                    if 'mechanism_chain' in data and len(data['mechanism_chain']) > idx:
                        if data['mechanism_chain'][idx].get('confidence', 0) > ceiling:
                            print(f"Fixing {template_id} mechanism_chain[{idx}] confidence to {ceiling}")
                            data['mechanism_chain'][idx]['confidence'] = ceiling
                            dirty = True
            else:
                print(f"Unhandled path: {path} in {template_id}")

        if dirty:
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=4)
            total_fixed += len(updates)

    print(f"Repaired {total_fixed} ceiling violations.")

if __name__ == "__main__":
    repair_ceilings()
