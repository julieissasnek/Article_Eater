import json
import os
import re

doc_path = "docs/THERMAL_I_Panel_Output.md"
out_dir = "data/templates"

with open(doc_path, 'r') as f:
    content = f.read()

# Find all json blocks
pattern = re.compile(r'```json\s+(.*?)\s+```', re.DOTALL)
matches = pattern.findall(content)

extracted = []
for m in matches:
    try:
        data = json.loads(m)
        tid = data.get("template_id")
        if tid:
            out_file = os.path.join(out_dir, f"{tid}.json")
            with open(out_file, 'w') as f_out:
                json.dump(data, f_out, indent=4)
            extracted.append(tid)
            print(f"Extracted {tid} to {out_file}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON block: {e}")

print(f"Successfully extracted {len(extracted)} templates.")
