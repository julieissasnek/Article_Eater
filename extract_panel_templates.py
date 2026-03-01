#!/usr/bin/env python3
"""
Extract calibrated JSON templates from MUSIC-I panel output.
Applies canonical field name resolution and writes to data/templates/.
"""

import json
import re
from pathlib import Path
from datetime import datetime

# Configuration
PANEL_OUTPUT_FILE = Path("/sessions/practical-zen-darwin/mnt/REPOS/Article_Eater_PostQuinean_v1/docs/MUSIC_I_Panel_Output.md")
OUTPUT_DIR = Path("/sessions/practical-zen-darwin/mnt/REPOS/Article_Eater_PostQuinean_v1/data/templates")
CALIBRATION_DATE = "2026-02-23"
PANEL_SOURCE = "MUSIC-I"
PROVENANCE = "panel_calibrated"

# Field name mapping (old → new canonical names)
FIELD_MAPPING = {
    "mechanism_steps": "mechanism_chain",
    "status": "calibration_status",
    "bridge_warrant_type": "bridge_warrant",
    "prior_confidence": "confidence",
}

def fix_json_string(json_text):
    """Fix common JSON issues: trailing commas, quotes in strings, etc."""
    # Remove trailing commas before } or ]
    json_text = re.sub(r',(\s*[}\]])', r'\1', json_text)
    # Fix patterns like "n": 32" → "n": 32
    json_text = re.sub(r'": (\d+)"([,}\]])', r': \1\2', json_text)
    # Fix quotes around numeric values in certain patterns
    json_text = re.sub(r'": "(\d+\.?\d*)"([,}\]])', r': \1\2', json_text)
    return json_text

def extract_json_blocks(content):
    """Extract all JSON blocks from markdown content."""
    pattern = r'```json\n(.*?)\n```'
    matches = re.finditer(pattern, content, re.DOTALL)
    blocks = []
    for match in matches:
        blocks.append(match.group(1))
    return blocks

def canonicalize_fields(obj):
    """Recursively apply field name mappings and add required fields."""
    if not isinstance(obj, dict):
        return obj
    
    # Create new dict with mapped keys
    result = {}
    for key, value in obj.items():
        new_key = FIELD_MAPPING.get(key, key)
        if isinstance(value, dict):
            result[new_key] = canonicalize_fields(value)
        elif isinstance(value, list):
            result[new_key] = [canonicalize_fields(item) if isinstance(item, dict) else item for item in value]
        else:
            result[new_key] = value
    
    return result

def process_template(json_obj):
    """Process a single template: validate, canonicalize, add defaults."""
    # Canonicalize field names
    template = canonicalize_fields(json_obj)
    
    # Extract template_id for filename and display_id
    if "template_id" not in template:
        return None, "Missing 'template_id' field"
    
    template_id = template["template_id"]
    
    # Add default fields if missing
    if "display_id" not in template:
        template["display_id"] = template_id
    
    if "name" not in template:
        # Derive name from template_id
        template["name"] = template_id.replace("_", " ").title()
    
    if "panel_source" not in template:
        template["panel_source"] = PANEL_SOURCE
    
    if "calibration_status" not in template:
        template["calibration_status"] = "calibrated"
    
    if "provenance" not in template:
        template["provenance"] = PROVENANCE
    
    if "calibration_date" not in template:
        template["calibration_date"] = CALIBRATION_DATE
    
    if "cross_template_interactions" not in template:
        template["cross_template_interactions"] = []
    
    if "residual_gaps" not in template:
        template["residual_gaps"] = []
    
    return template_id, template

def main():
    """Main extraction pipeline."""
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Read panel output
    with open(PANEL_OUTPUT_FILE, 'r') as f:
        content = f.read()
    
    # Extract all JSON blocks
    json_blocks = extract_json_blocks(content)
    print(f"Found {len(json_blocks)} JSON blocks")
    
    successfully_extracted = []
    parse_errors = []
    
    for i, block in enumerate(json_blocks, 1):
        print(f"\n--- Processing block {i}/{len(json_blocks)} ---")
        
        # Try to parse JSON with fixes
        try:
            fixed_block = fix_json_string(block)
            json_obj = json.loads(fixed_block)
        except json.JSONDecodeError as e:
            error_msg = f"Block {i}: {str(e)}"
            print(f"ERROR: {error_msg}")
            parse_errors.append((i, error_msg, block[:100]))
            continue
        
        # Check if this is a template (has template_id field)
        if "template_id" not in json_obj:
            print(f"Block {i}: SKIPPED (no 'template_id' field)")
            continue
        
        # Process template
        template_id, processed = process_template(json_obj)
        if processed is None:
            error_msg = f"Block {i}: {template_id}"
            print(f"ERROR: {error_msg}")
            parse_errors.append((i, error_msg, ""))
            continue
        
        # Write to file
        output_file = OUTPUT_DIR / f"{template_id}.json"
        try:
            with open(output_file, 'w') as f:
                json.dump(processed, f, indent=2)
            print(f"✓ Extracted: {template_id}")
            print(f"  Written to: {output_file}")
            successfully_extracted.append(template_id)
        except Exception as e:
            error_msg = f"Block {i}: Write error: {str(e)}"
            print(f"ERROR: {error_msg}")
            parse_errors.append((i, error_msg, ""))
    
    # Report summary
    print("\n" + "="*80)
    print("EXTRACTION SUMMARY")
    print("="*80)
    print(f"Total JSON blocks found: {len(json_blocks)}")
    print(f"Successfully extracted templates: {len(successfully_extracted)}")
    print(f"Parse errors: {len(parse_errors)}")
    
    if successfully_extracted:
        print(f"\nExtracted template IDs:")
        for tid in successfully_extracted:
            print(f"  - {tid}")
    
    if parse_errors:
        print(f"\nParse errors and fixes:")
        for block_num, error, preview in parse_errors:
            print(f"  Block {block_num}: {error}")
            if preview:
                print(f"    Preview: {preview}")
    
    return len(successfully_extracted), parse_errors

if __name__ == "__main__":
    count, errors = main()
    exit(0 if not errors else 1)
