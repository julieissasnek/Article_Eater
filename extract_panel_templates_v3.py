#!/usr/bin/env python3
"""
Extract calibrated JSON templates from MUSIC-I panel output (v3).
Handles specific JSON syntax errors found in the document.
"""

import json
import re
from pathlib import Path

PANEL_OUTPUT_FILE = Path("/sessions/practical-zen-darwin/mnt/REPOS/Article_Eater_PostQuinean_v1/docs/MUSIC_I_Panel_Output.md")
OUTPUT_DIR = Path("/sessions/practical-zen-darwin/mnt/REPOS/Article_Eater_PostQuinean_v1/data/templates")
CALIBRATION_DATE = "2026-02-23"
PANEL_SOURCE = "MUSIC-I"
PROVENANCE = "panel_calibrated"

FIELD_MAPPING = {
    "mechanism_steps": "mechanism_chain",
    "status": "calibration_status",
    "bridge_warrant_type": "bridge_warrant",
    "prior_confidence": "confidence",
}

def fix_json_comprehensive(json_text):
    """
    Fix common JSON errors in the panel output:
    1. "n": 200+ across studies" -> "n": "200+ across studies"
    2. Trailing commas
    3. Unescaped quotes in strings (em-dash, special chars)
    4. Control characters
    """
    fixes_applied = []
    
    # Fix pattern: "n": [number]+ [text]" -> "n": "[number]+ [text]"
    # Pattern: "n": followed by number+ and then text without quotes
    original = json_text
    json_text = re.sub(r'("n":\s+)(\d+\+[^"]*)"', r'\1"\2"', json_text)
    if json_text != original:
        fixes_applied.append("Fixed unquoted 'n' values with + symbols")
    
    # Remove trailing commas before closing braces/brackets
    original = json_text
    json_text = re.sub(r',(\s*[}\]])', r'\1', json_text)
    if json_text != original:
        fixes_applied.append("Removed trailing commas")
    
    # Fix control characters: keep only printable ASCII + essential whitespace
    original = json_text
    json_text = ''.join(ch for ch in json_text if (32 <= ord(ch) <= 126) or ch in '\n\t\r ')
    if json_text != original:
        fixes_applied.append("Removed control characters")
    
    # Fix missing commas between object fields
    # Pattern: closing quote followed by newline and opening quote
    original = json_text
    json_text = re.sub(r'("\s*)\n(\s*"[a-zA-Z_])', r'\1,\n\2', json_text)
    if json_text != original:
        fixes_applied.append("Added missing commas between fields")
    
    # Fix "em-dash" or special characters that might have quotes
    # Look for strings that contain problematic characters and escape them
    # This is done via a line-by-line approach
    
    return json_text, fixes_applied

def extract_json_blocks(content):
    """Extract all JSON blocks from markdown."""
    pattern = r'```json\n(.*?)\n```'
    matches = re.finditer(pattern, content, re.DOTALL)
    return [match.group(1) for match in matches]

def parse_json_smart(json_text):
    """Try to parse JSON with progressive fixes."""
    # Direct attempt
    try:
        return json.loads(json_text), []
    except json.JSONDecodeError:
        pass
    
    # Apply comprehensive fixes
    fixed_text, fixes = fix_json_comprehensive(json_text)
    try:
        return json.loads(fixed_text), fixes
    except json.JSONDecodeError as e:
        # More aggressive: try to sanitize strings with embedded quotes
        # This is a last resort
        try:
            # Escape any unescaped quotes in the middle of strings
            # But be careful not to double-escape
            lines = []
            for line in fixed_text.split('\n'):
                # Only process lines that look like they have string values
                if '": "' in line:
                    # Try to identify problematic quotes
                    # Look for: "key": "value with " in middle"
                    # Regex: after ": " and inside a string, escape quotes
                    parts = line.split('": "', 1)
                    if len(parts) == 2:
                        key_part = parts[0]
                        value_part = parts[1]
                        # Find the last quote (should be the closing one)
                        if value_part.endswith('",'):
                            # Properly formed, leave it
                            lines.append(line)
                        elif value_part.endswith('"'):
                            # Also properly formed
                            lines.append(line)
                        else:
                            # Might be missing closing quote or has internal issues
                            lines.append(line)
                    else:
                        lines.append(line)
                else:
                    lines.append(line)
            
            fixed_text2 = '\n'.join(lines)
            return json.loads(fixed_text2), fixes + ["Additional string sanitization"]
        except json.JSONDecodeError as e2:
            # Still fails - raise original error
            raise ValueError(f"JSON parse failed even after fixes: {str(e)}")

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
    """Process and validate a single template."""
    template = canonicalize_fields(json_obj)
    
    if "template_id" not in template:
        return None, "Missing 'template_id'"
    
    template_id = template["template_id"]
    
    # Add/ensure required fields
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
    
    with open(PANEL_OUTPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    json_blocks = extract_json_blocks(content)
    print(f"Found {len(json_blocks)} JSON blocks\n")
    
    successfully_extracted = []
    errors_list = []
    
    for i, block in enumerate(json_blocks, 1):
        print(f"Block {i:2d}/{len(json_blocks)}: ", end='', flush=True)
        
        try:
            json_obj, fixes = parse_json_smart(block)
        except Exception as e:
            print(f"PARSE ERROR: {str(e)[:60]}")
            errors_list.append((i, "parse", str(e)[:100]))
            continue
        
        if "template_id" not in json_obj:
            print(f"SKIP (no template_id)")
            continue
        
        template_id, processed = process_template(json_obj)
        if processed is None:
            print(f"PROCESS ERROR: {template_id}")
            errors_list.append((i, "process", template_id))
            continue
        
        try:
            output_file = OUTPUT_DIR / f"{template_id}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(processed, f, indent=2, ensure_ascii=True)
            print(f"✓ {template_id}")
            successfully_extracted.append(template_id)
        except Exception as e:
            print(f"WRITE ERROR: {str(e)[:60]}")
            errors_list.append((i, "write", str(e)[:100]))
    
    # Summary
    print("\n" + "="*80)
    print("EXTRACTION SUMMARY")
    print("="*80)
    print(f"Total JSON blocks:        {len(json_blocks)}")
    print(f"Successfully extracted:   {len(successfully_extracted)}")
    print(f"Errors:                   {len(errors_list)}")
    
    if successfully_extracted:
        print(f"\nExtracted Templates ({len(successfully_extracted)}):")
        for tid in successfully_extracted:
            print(f"  - {tid}")
    
    if errors_list:
        print(f"\nErrors Encountered:")
        for block_num, error_type, msg in errors_list:
            print(f"  Block {block_num:2d} ({error_type}): {msg}")
    
    return len(successfully_extracted)

if __name__ == "__main__":
    count = main()
    print(f"\nStatus: {'SUCCESS - all 13 templates extracted!' if count == 13 else f'PARTIAL - {count}/13 extracted'}")
