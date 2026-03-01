#!/usr/bin/env python3
"""
Apply ceiling override decisions from ceiling_decisions.json to template files.

This script:
1. Reads data/ceiling_decisions.json to get all 69 decisions
2. Reads data/ceiling_decisions_template_mapping.json for resolution guidance
3. For each decision, finds the matching template file
4. Locates the correct mechanism_chain step
5. Adds ceiling_override_rationale to that step
6. If decision says "warrant_upgrade", updates the warrant type
7. Saves the modified template

Returns:
- How many decisions were applied
- How many templates were modified
- How many decisions couldn't be applied (and why)
"""

import json
import os
import sys
from pathlib import Path
from difflib import SequenceMatcher
from typing import Dict, List, Tuple, Optional

# Paths
REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / "data"
DECISIONS_FILE = DATA_DIR / "ceiling_decisions.json"
MAPPING_FILE = DATA_DIR / "ceiling_decisions_template_mapping.json"
TEMPLATES_DIR = DATA_DIR / "templates"

def load_json(filepath: Path) -> Dict:
    """Load JSON file safely."""
    with open(filepath, 'r') as f:
        return json.load(f)

def save_json(filepath: Path, data: Dict) -> None:
    """Save JSON file with indent=2 for readability."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def find_template_file(template_id: str, mapping: Dict, templates_dir: Path) -> Optional[Path]:
    """
    Find the template file for a given template_id.
    
    Strategy:
    1. Direct filename match (template_id.json)
    2. Check mapping file for resolved_files (use first match)
    3. Search for template_id as a field value in templates
    4. Fuzzy match on filename
    """
    
    # Strategy 1: Direct filename
    direct_file = templates_dir / f"{template_id}.json"
    if direct_file.exists():
        return direct_file
    
    # Strategy 2: Check mapping and use resolved_files
    for mapping_entry in mapping.get("template_mappings", []):
        if mapping_entry.get("template_id") == template_id:
            resolved_files = mapping_entry.get("resolved_files", [])
            if resolved_files:
                # Try first resolved file
                candidate = templates_dir / resolved_files[0]
                if candidate.exists():
                    return candidate
    
    # Strategy 3: Search for template_id as display_id or in content
    for template_file in sorted(templates_dir.glob("*.json")):
        try:
            template_data = load_json(template_file)
            if template_data.get("display_id") == template_id:
                return template_file
            if template_data.get("template_id") == template_id:
                return template_file
        except:
            pass
    
    # Strategy 4: Fuzzy match on filename
    best_match = None
    best_ratio = 0.0
    for template_file in templates_dir.glob("*.json"):
        filename = template_file.stem.upper()
        ratio = SequenceMatcher(None, filename, template_id.upper()).ratio()
        if ratio > best_ratio and ratio > 0.6:
            best_ratio = ratio
            best_match = template_file
    
    return best_match

def find_step_in_mechanism_chain(
    template_data: Dict,
    step_number: int,
    field_path: Optional[str] = None
) -> Optional[Dict]:
    """
    Find the correct step in mechanism_chain.
    
    Match by:
    1. Exact step number
    2. Field path if provided
    """
    mechanism_chain = template_data.get("mechanism_chain", [])
    
    for step in mechanism_chain:
        if step.get("step") == step_number:
            return step
    
    # If not found and field_path provided, try to match by description
    if field_path:
        for step in mechanism_chain:
            desc = step.get("description", "").upper()
            if field_path.upper() in desc:
                return step
    
    return None

def apply_decision(
    template_data: Dict,
    decision: Dict,
    template_file: Path
) -> Tuple[bool, str]:
    """
    Apply a single decision to a template.
    
    Returns:
    - (success: bool, message: str)
    """
    step_num = decision.get("step")
    rationale = decision.get("rationale")
    decision_type = decision.get("decision")
    new_warrant = decision.get("new_warrant")
    
    # Find the step
    step = find_step_in_mechanism_chain(template_data, step_num)
    if not step:
        return False, f"Could not find step {step_num} in mechanism_chain"
    
    # Add ceiling_override_rationale (only if rationale exists and not already set)
    if rationale and not step.get("ceiling_override_rationale"):
        step["ceiling_override_rationale"] = rationale
    
    # If warrant upgrade is needed, update warrant
    if decision_type == "A" and new_warrant:
        old_warrant = step.get("warrant")
        step["warrant"] = new_warrant
        if rationale:
            return True, f"Step {step_num}: Added override rationale + upgraded warrant from {old_warrant} to {new_warrant}"
        else:
            return True, f"Step {step_num}: Upgraded warrant from {old_warrant} to {new_warrant}"
    else:
        if rationale:
            return True, f"Step {step_num}: Added override rationale"
        else:
            return True, f"Step {step_num}: Processed (no rationale or action needed)"

def main():
    print("=" * 80)
    print("CEILING DECISIONS APPLICATION SCRIPT")
    print(f"Date: {Path(DECISIONS_FILE).exists() and 'Running...' or 'ERROR'}")
    print("=" * 80)
    
    # Verify files exist
    if not DECISIONS_FILE.exists():
        print(f"ERROR: {DECISIONS_FILE} not found")
        sys.exit(1)
    if not MAPPING_FILE.exists():
        print(f"ERROR: {MAPPING_FILE} not found")
        sys.exit(1)
    if not TEMPLATES_DIR.exists():
        print(f"ERROR: {TEMPLATES_DIR} not found")
        sys.exit(1)
    
    # Load data
    print("\nLoading data...")
    decisions_data = load_json(DECISIONS_FILE)
    mapping_data = load_json(MAPPING_FILE)
    
    decisions = decisions_data.get("decisions", [])
    print(f"  - Loaded {len(decisions)} decisions")
    print(f"  - Template mapping has {len(mapping_data.get('template_mappings', []))} entries")
    
    # Track results
    applied_count = 0
    failed_count = 0
    failed_decisions = []
    modified_templates = set()
    modified_template_details = {}  # Track which decisions modified each template
    
    print("\n" + "=" * 80)
    print("APPLYING DECISIONS")
    print("=" * 80)
    
    for idx, decision in enumerate(decisions, 1):
        template_id = decision.get("template_id")
        step = decision.get("step")
        
        # Find template file
        template_file = find_template_file(template_id, mapping_data, TEMPLATES_DIR)
        
        if not template_file:
            failed_count += 1
            failed_decisions.append({
                "template_id": template_id,
                "step": step,
                "reason": "Template file not found"
            })
            print(f"[{idx:3d}] FAIL: {template_id} step {step} - Template file not found")
            continue
        
        try:
            # Load template
            template_data = load_json(template_file)
            
            # Apply decision
            success, message = apply_decision(template_data, decision, template_file)
            
            if success:
                # Save template
                save_json(template_file, template_data)
                modified_templates.add(template_file.name)
                
                # Track which template was modified for which decision
                if template_file.name not in modified_template_details:
                    modified_template_details[template_file.name] = []
                modified_template_details[template_file.name].append({
                    "template_id": template_id,
                    "step": step,
                    "decision_type": decision.get("decision"),
                    "message": message
                })
                
                applied_count += 1
                print(f"[{idx:3d}] OK:   {template_id} step {step} - {message}")
            else:
                failed_count += 1
                failed_decisions.append({
                    "template_id": template_id,
                    "step": step,
                    "reason": message
                })
                print(f"[{idx:3d}] FAIL: {template_id} step {step} - {message}")
        
        except Exception as e:
            failed_count += 1
            failed_decisions.append({
                "template_id": template_id,
                "step": step,
                "reason": str(e)
            })
            print(f"[{idx:3d}] ERROR: {template_id} step {step} - {str(e)}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total decisions:        {len(decisions)}")
    print(f"Applied:                {applied_count}")
    print(f"Failed:                 {failed_count}")
    print(f"Templates modified:     {len(modified_templates)}")
    
    if failed_decisions:
        print("\nFailed Decisions:")
        print("-" * 80)
        for fail in failed_decisions:
            print(f"  {fail['template_id']:40s} step {fail['step']:2d} - {fail['reason']}")
    
    print("\nModified Templates (with decision counts):")
    print("-" * 80)
    for template_name in sorted(modified_templates):
        decision_count = len(modified_template_details.get(template_name, []))
        print(f"  {template_name:50s} ({decision_count} decisions applied)")
    
    print("\n" + "=" * 80)
    
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
