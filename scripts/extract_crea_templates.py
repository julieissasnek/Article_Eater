import json
import re
import os

input_file = "docs/CREATIVE_I_Panel_Output.md"
output_dir = "data/templates"

os.makedirs(output_dir, exist_ok=True)

with open(input_file, "r") as f:
    content = f.read()

# Find all JSON blocks
json_blocks = re.findall(r'```json\s+(.*?)\s+```', content, re.DOTALL)

for i, block in enumerate(json_blocks):
    try:
        data = json.loads(block)
        template_id = data.get("template_id")
        if template_id:
            output_path = os.path.join(output_dir, f"{template_id}.json")
            with open(output_path, "w") as out_f:
                json.dump(data, out_f, indent=2)
            print(f"Extraction successful: {output_path}")
        else:
            print(f"Warning: Block {i} missing template_id")
    except json.JSONDecodeError as e:
        print(f"Error decoding block {i}: {e}")
