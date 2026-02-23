import os
import json
import glob
import re
from collections import defaultdict

TEMPLATE_DIR = 'data/templates'

def load_all_templates():
    templates = {}
    for filepath in glob.glob(os.path.join(TEMPLATE_DIR, '*.json')):
        if filepath.endswith('.bak'): continue
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                if 'template_id' in data:
                    templates[data['template_id']] = data
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
    return templates

def extract_explicit_overlaps(overlap_texts):
    """Uses regex to find uppercase template IDs referenced in overlap text."""
    found_ids = set()
    for text in overlap_texts:
        # Match standard template IDs like PP_COMPLEXITY_GOLDILOCKS_002, T_IE_006
        matches = re.findall(r'\b[A-Z_]+_\d{3}\b', text)
        found_ids.update(matches)
        
        # Match short IDs like SC1, SC3, T14
        short_matches = re.findall(r'\b(?:SC|T|L|M|TP|AX|CB)\d{1,2}\b', text)
        found_ids.update(short_matches)
    return found_ids

def main():
    templates = load_all_templates()
    print(f"Loaded {len(templates)} total templates.")
    
    ie_templates = {tid: data for tid, data in templates.items() if tid.startswith('T_IE_')}
    print(f"Found {len(ie_templates)} IE_DPT templates to analyze.\n")
    
    print("="*60)
    print(" 1. EXPLICIT OVERLAP ANALYSIS (From overlap_analysis field)")
    print("="*60)
    
    missing_references = []
    for tid, data in ie_templates.items():
        overlaps = data.get('overlap_analysis', [])
        if not overlaps:
            continue
            
        explicit_ids = extract_explicit_overlaps(overlaps)
        if explicit_ids:
            print(f"\n[{tid}] {data.get('template_name')}")
            print(f"  Explicit overlaps cited:")
            for ref_id in explicit_ids:
                if ref_id in templates:
                    ref_name = templates[ref_id].get('template_name', 'Unknown Name')
                    print(f"    [VALID] {ref_id}: {ref_name}")
                else:
                    print(f"    [WARN ] {ref_id} - NOT FOUND IN DATABASE")
                    missing_references.append((tid, ref_id))

    print("\n" + "="*60)
    print(" 2. IMPLICIT OVERLAP ANALYSIS (Shared Constructs > 1)")
    print("="*60)
    
    # Check for implicit overlaps by high construct sharing
    # Compare T_IE templates against all non-IE templates
    for ie_tid, ie_data in ie_templates.items():
        ie_constructs = set(ie_data.get('constructs', []))
        if not ie_constructs:
            continue
            
        strong_overlaps = []
        for other_tid, other_data in templates.items():
            if other_tid.startswith('T_IE_'):
                continue
            
            other_text = json.dumps(other_data).lower()
            shared = set()
            for c in ie_constructs:
                if c.lower() in other_text:
                    shared.add(c)
            
            if len(shared) >= 2:
                other_name = other_data.get('template_name', other_data.get('name', 'Unknown Name'))
                strong_overlaps.append((other_tid, other_name, shared))
                
        if strong_overlaps:
            print(f"\n[{ie_tid}] {ie_data.get('template_name', 'Unknown Name')} (Constructs: {', '.join(ie_constructs)})")
            for ov_tid, ov_name, shared in sorted(strong_overlaps, key=lambda x: len(x[2]), reverse=True):
                print(f"  -> High Construct Overlap with {ov_tid}: {ov_name}")
                print(f"     Shared: {list(shared)}")

    print("\n" + "="*60)
    print(" SUMMARY")
    print("="*60)
    if missing_references:
        print(f"WARNING: {len(missing_references)} explicitly cited templates are missing from the database.")
        for src, missing in missing_references:
            print(f"  {src} cites missing {missing}")
    else:
        print("All explicitly cited template overlaps are functionally linked to existing templates in the database.")

if __name__ == '__main__':
    main()
