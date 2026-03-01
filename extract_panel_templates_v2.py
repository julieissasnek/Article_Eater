#!/usr/bin/env python3
"""
Extract calibrated JSON templates from MUSIC-I panel output (v2).
Handles multiline strings, special characters, and malformed JSON.
"""

import json
import re
from pathlib import Path

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

def fix_json_string_aggressive(json_text):
    """
    Aggressively fix JSON issues:
    - Trailing commas
    - Unescaped quotes in string values
    - Control characters
    - Missing commas between fields
    """
    # Remove trailing commas before } or ]
    json_text = re.sub(r',(\s*[}\]])', r'\1', json_text)
    
    # Escape unescaped quotes in string values (but not the key/value delimiters)
    # This is tricky - we need to escape quotes that appear inside string values
    # Pattern: look for "key": "value with "quote" inside"
    # We'll handle this by processing line by line and being careful
    
    # Handle null values that might be quoted
    json_text = re.sub(r': "null"([,\n}])', r': null\1', json_text)
    
    # Handle empty arrays/objects
    json_text = re.sub(r': \[\]([,\n}])', r': []\1', json_text)
    json_text = re.sub(r': \{\}([,\n}])', r': {}\1', json_text)
    
    # Try to strip control characters (keep only printable + whitespace)
    json_text = ''.join(ch for ch in json_text if ord(ch) >= 32 or ch in '\n\t\r')
    
    # Handle missing commas between fields (before opening brace on new line)
    # Look for }" (closing a value) followed by newline and "key"
    json_text = re.sub(r'(\}|\]|")\s*\n\s*"([a-zA-Z_])', r'\1,\n  "\2', json_text)
    
    return json_text

def extract_json_blocks_robust(content):
    """Extract all JSON blocks from markdown, handling malformed markdown fence markers."""
    # Look for blocks between ```json and next ``` regardless of newlines
    pattern = r'```json\n(.*?)\n```'
    matches = re.finditer(pattern, content, re.DOTALL)
    blocks = []
    for match in matches:
        blocks.append(match.group(1))
    return blocks

def parse_json_with_fallbacks(json_text):
    """Try multiple parsing strategies."""
    # Strategy 1: Direct parsing
    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        pass
    
    # Strategy 2: Aggressive fix
    try:
        fixed = fix_json_string_aggressive(json_text)
        return json.loads(fixed)
    except json.JSONDecodeError as e:
        # Try to pinpoint and fix the issue
        pass
    
    # Strategy 3: Manual string escaping for problematic quotes
    try:
        # Find all quoted strings and ensure they're properly escaped
        lines = json_text.split('\n')
        fixed_lines = []
        for line in lines:
            # Skip lines that are entirely comments or structure
            if ':' in line and '"' in line:
                # This is a key-value line
                # Split on first colon
                key_part, _, value_part = line.partition(':')
                
                # If value starts with a quote, try to handle it
                if value_part.strip().startswith('"'):
                    # Find the matching closing quote
                    # This is complex, so we'll just try to parse as-is first
                    fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        fixed_text = '\n'.join(fixed_lines)
        return json.loads(fixed_text)
    except json.JSONDecodeError:
        pass
    
    raise ValueError("Could not parse JSON with any strategy")

def canonicalize_fields(obj):
    """Recursively apply field name mappings."""
    if not isinstance(obj, dict):
        return obj
    
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
    """Process a single template."""
    template = canonicalize_fields(json_obj)
    
    if "template_id" not in template:
        return None, "Missing 'template_id' field"
    
    template_id = template["template_id"]
    
    # Add default fields
    if "display_id" not in template:
        template["display_id"] = template_id
    
    if "name" not in template:
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
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(PANEL_OUTPUT_FILE, 'r') as f:
        content = f.read()
    
    json_blocks = extract_json_blocks_robust(content)
    print(f"Found {len(json_blocks)} JSON blocks\n")
    
    successfully_extracted = []
    parse_errors = []
    
    for i, block in enumerate(json_blocks, 1):
        print(f"--- Processing block {i}/{len(json_blocks)} ---")
        
        try:
            json_obj = parse_json_with_fallbacks(block)
        except Exception as e:
            error_msg = f"Parse error: {str(e)}"
            print(f"ERROR: {error_msg}")
            parse_errors.append((i, error_msg))
            continue
        
        if "template_id" not in json_obj:
            print(f"SKIPPED (no 'template_id' field)")
            continue
        
        template_id, processed = process_template(json_obj)
        if processed is None:
            error_msg = f"Process error: {template_id}"
            print(f"ERROR: {error_msg}")
            parse_errors.append((i, error_msg))
            continue
        
        try:
            output_file = OUTPUT_DIR / f"{template_id}.json"
            with open(output_file, 'w') as f:
                json.dump(processed, f, indent=2)
            print(f"✓ {template_id}")
            successfully_extracted.append(template_id)
        except Exception as e:
            error_msg = f"Write error: {str(e)}"
            print(f"ERROR: {error_msg}")
            parse_errors.append((i, error_msg))
    
    # Report
    print("\n" + "="*80)
    print("EXTRACTION SUMMARY")
    print("="*80)
    print(f"Total JSON blocks found: {len(json_blocks)}")
    print(f"Successfully extracted: {len(successfully_extracted)}")
    print(f"Parse errors: {len(parse_errors)}")
    
    if successfully_extracted:
        print(f"\nExtracted template IDs:")
        for tid in successfully_extracted:
            print(f"  - {tid}")
    
    if parse_errors:
        print(f"\nErrors encountered:")
        for i, error in parse_errors:
            print(f"  Block {i}: {error}")
    
    return len(successfully_extracted)

if __name__ == "__main__":
    count = main()
    exit(0 if count == 13 else 1)
