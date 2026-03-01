#!/usr/bin/env python3
"""
Extract calibrated JSON templates from MUSIC-I panel output (final version).
Handles all identified JSON syntax errors.
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

def fix_json_final(json_text):
    """Fix all identified JSON errors."""
    fixes = []
    original = json_text
    
    # 1. Fix "n": [digits]", -> "n": "[digits]",
    # Pattern: "n": (number or number+something) without quotes before the closing quote
    json_text = re.sub(r'("n":\s+)(\d+(?:\+[^"]*)?)"', r'\1"\2"', json_text)
    if json_text != original:
        fixes.append("Fixed unquoted numeric/range 'n' values")
        original = json_text
    
    # 2. Fix escaped single quotes in JSON strings (Juslin\'s -> Juslin's)
    # This is actually OK in JSON strings, but let's be consistent
    # Actually, keep them as-is since they're valid
    
    # 3. Remove trailing commas
    original = json_text
    json_text = re.sub(r',(\s*[}\]])', r'\1', json_text)
    if json_text != original:
        fixes.append("Removed trailing commas")
        original = json_text
    
    # 4. Remove control characters
    original = json_text
    cleaned = []
    for ch in json_text:
        code = ord(ch)
        if (32 <= code <= 126) or ch in '\n\t\r ':
            cleaned.append(ch)
        elif code < 32 and ch not in '\n\t\r':
            # Skip control chars except whitespace
            pass
        else:
            cleaned.append(ch)
    json_text = ''.join(cleaned)
    if json_text != original:
        fixes.append("Removed control characters")
        original = json_text
    
    # 5. Fix missing commas between object fields
    # After }: or ]: or ": "value", add comma if next line has "key"
    original = json_text
    json_text = re.sub(r'("\s*)\n(\s*"[a-zA-Z_])', r'\1,\n\2', json_text)
    if json_text != original:
        fixes.append("Added missing commas between fields")
    
    return json_text, fixes

def extract_json_blocks(content):
    """Extract all JSON blocks from markdown."""
    pattern = r'```json\n(.*?)\n```'
    matches = re.finditer(pattern, content, re.DOTALL)
    return [match.group(1) for match in matches]

def parse_json_smart(json_text):
    """Try to parse JSON, applying fixes as needed."""
    try:
        return json.loads(json_text), []
    except json.JSONDecodeError:
        pass
    
    # Apply comprehensive fixes
    fixed_text, fixes = fix_json_final(json_text)
    try:
        return json.loads(fixed_text), fixes
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON parse error at line {e.lineno} col {e.colno}: {e.msg}")

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
    
    # Ensure required fields
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
        print(f"Block {i:2d}/13: ", end='', flush=True)
        
        try:
            json_obj, fixes = parse_json_smart(block)
        except Exception as e:
            print(f"ERROR - {str(e)[:50]}")
            errors_list.append((i, str(e)[:100]))
            continue
        
        if "template_id" not in json_obj:
            print(f"SKIP (no template_id)")
            continue
        
        template_id, processed = process_template(json_obj)
        if processed is None:
            print(f"ERROR - {template_id}")
            errors_list.append((i, template_id))
            continue
        
        try:
            output_file = OUTPUT_DIR / f"{template_id}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(processed, f, indent=2, ensure_ascii=True)
            print(f"✓ {template_id}")
            successfully_extracted.append(template_id)
        except Exception as e:
            print(f"WRITE ERROR - {str(e)[:50]}")
            errors_list.append((i, f"Write: {str(e)}"))
    
    # Summary report
    print("\n" + "="*80)
    print("EXTRACTION SUMMARY")
    print("="*80)
    print(f"Total JSON blocks found:       {len(json_blocks)}")
    print(f"Successfully extracted:        {len(successfully_extracted)}")
    if errors_list:
        print(f"Parse/write errors:            {len(errors_list)}")
    
    if successfully_extracted:
        print(f"\nExtracted Templates ({len(successfully_extracted)}):")
        for tid in successfully_extracted:
            print(f"  - {tid}")
    
    if errors_list:
        print(f"\nErrors:")
        for block_num, msg in errors_list:
            print(f"  Block {block_num}: {msg}")
    
    return len(successfully_extracted)

if __name__ == "__main__":
    count = main()
    if count == 13:
        print(f"\n✓ SUCCESS: All 13 templates extracted!")
        exit(0)
    else:
        print(f"\n✗ PARTIAL: Only {count}/13 templates extracted")
        exit(1)
