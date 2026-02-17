
import os
import json
import glob

# Mock classes to handle the Python-syntax templates
def MechanisticTemplate(**kwargs):
    return kwargs

def CausalLink(**kwargs):
    return kwargs


def repair_templates():
    template_dir = "data/templates"
    files = glob.glob(os.path.join(template_dir, "*.json"))
    
    fixed_count = 0
    error_count = 0
    injected_count = 0
    
    print(f"Scanning {len(files)} templates...")

    for file_path in files:
        filename = os.path.basename(file_path)
        display_id = os.path.splitext(filename)[0] # e.g., "E1"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        needs_write = False
        template_dict = {}

        # 1. Check if python format (re-run logic just in case)
        if content.startswith("MechanisticTemplate"):
            print(f"Fixing malformed Python file: {filename}")
            try:
                local_scope = {
                    "MechanisticTemplate": MechanisticTemplate,
                    "CausalLink": CausalLink
                }
                template_dict = eval(content, {}, local_scope)
                needs_write = True
                fixed_count += 1
            except Exception as e:
                print(f"FAILED to fix {filename}: {e}")
                error_count += 1
                continue
        else:
            # It's JSON (or we assume/hope so)
            try:
                template_dict = json.loads(content)
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON: {filename}")
                continue

        # 2. Check/Inject display_id
        if "display_id" not in template_dict:
            print(f"Injecting display_id='{display_id}' into {filename}")
            template_dict["display_id"] = display_id
            needs_write = True
            injected_count += 1
        
        # 3. Normalize levels (Fix invalid enum values)
        if "causal_links" in template_dict:
            for link in template_dict["causal_links"]:
                if "from_level" in link and isinstance(link["from_level"], str):
                    if link["from_level"].isupper():
                        link["from_level"] = link["from_level"].lower()
                        needs_write = True
                if "to_level" in link and isinstance(link["to_level"], str):
                    if link["to_level"].isupper():
                        link["to_level"] = link["to_level"].lower()
                        needs_write = True

        if needs_write:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(template_dict, f, indent=4)

    print(f"Repair complete. Fixed Python: {fixed_count}, Injected display_id: {injected_count}, Failed: {error_count}")

if __name__ == "__main__":
    repair_templates()
