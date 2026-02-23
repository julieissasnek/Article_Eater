import os
import re
import json
import glob

docs_dir = 'docs'
templates_dir = 'data/templates'

md_files = [
    'VISUAL_I_Panel_Output_Feb21.md'
]

# Get a mapping of template_id AND display_id to existing file path
existing_files = glob.glob(os.path.join(templates_dir, '*.json'))
template_mapping = {}
display_mapping = {}
for filepath in existing_files:
    # Skip backup files from previous fixes
    if filepath.endswith('.bak'):
        continue
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            if 'template_id' in data:
                template_mapping[data['template_id']] = filepath
            if 'display_id' in data:
                display_mapping[data['display_id']] = filepath
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

processed_count = 0
for md_file in md_files:
    md_path = os.path.join(docs_dir, md_file)
    print(f"Processing {md_path}...")
    with open(md_path, 'r') as f:
        content = f.read()
    
    # Extract JSON blocks
    matches = re.finditer(r'```json\s*(.*?)\s*```', content, re.DOTALL)
    for match in matches:
        json_str = match.group(1)
        try:
            data = json.loads(json_str)
            templates_to_process = []
            
            # Handle {"templates": [...]} format
            if isinstance(data, dict) and 'templates' in data and isinstance(data['templates'], list):
                templates_to_process = data['templates']
            else:
                templates_to_process = [data]
                
            for template_data in templates_to_process:
                template_id = template_data.get('template_id')
                display_id = template_data.get('display_id')
                if template_id:
                    out_path = None
                    if template_id in template_mapping:
                        out_path = template_mapping[template_id]
                        print(f"  Updating existing file (by template_id): {out_path}")
                    elif display_id and display_id in display_mapping:
                        out_path = display_mapping[display_id]
                        print(f"  Updating existing file (by display_id collision): {out_path}")
                    else:
                        # Clean filename
                        safe_id = re.sub(r'[^a-zA-Z0-9_\-]', '_', template_id)
                        out_path = os.path.join(templates_dir, f"{safe_id}.json")
                        print(f"  Creating new file: {out_path}")
                    
                    with open(out_path, 'w') as out_f:
                        json.dump(template_data, out_f, indent=2)
                    processed_count += 1
        except json.JSONDecodeError as e:
            print(f"  Failed to parse JSON block in {md_path}: {e}")

print(f"Done. Processed {processed_count} templates.")
