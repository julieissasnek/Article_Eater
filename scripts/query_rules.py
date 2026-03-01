#!/usr/bin/env python3
"""
scripts/query_rules.py

A tool to query JSON extraction templates or rule records across multi-dimensional criteria.
Useful for performing aggregations resembling meta-analyses on extracted rules.

Usage Examples:
    # Find all visual, curved shape rules
    python3 scripts/query_rules.py --tag spatial.shape.curved --tag sensory.visual
    
    # Find rules explained by Perceptual Fluency
    python3 scripts/query_rules.py --theory Perceptual_Fluency
    
    # Find rules with a large effect size (d > 0.8)
    python3 scripts/query_rules.py --min-effect 0.8
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

def get_effect_size(record: Dict[str, Any]) -> float:
    """Extract effect size or strength from a record, accommodating various schemas."""
    # Check ae.rule.v2 schema format
    strength = record.get("strength")
    if isinstance(strength, dict) and "value" in strength:
        return float(strength["value"])
    
    # Check Web of Belief evidence format
    if "evidence_effect_size" in record and record["evidence_effect_size"]:
        return float(record["evidence_effect_size"])
        
    return 0.0

def matches_query(record: Dict[str, Any], args: argparse.Namespace) -> bool:
    """Determine if a single JSON record matches the query parameters."""
    
    # 1. Check tags
    if args.tags:
        record_tags = set(record.get("tags", []) or [])
        # If trying to find ANY tag provided
        if not any(tag in record_tags for tag in args.tags):
            return False

    # 2. Check mechanism (which we embed as a "mechanism:*" tag)
    if args.mechanism:
        mech_tag = f"mechanism:{args.mechanism}"
        record_tags = set(record.get("tags", []) or [])
        if mech_tag not in record_tags:
            return False

    # 3. Check theory ID
    if args.theory:
        theory_id = record.get("theory_id", "")
        # Also check within T1 framework fields if it's an older template
        frameworks = set(record.get("framework_ids", []) or [])
        if args.theory != theory_id and args.theory not in frameworks:
            return False

    # 4. Check minimum effect size
    if args.min_effect is not None:
        val = get_effect_size(record)
        if val < args.min_effect:
            return False

    return True

def main():
    parser = argparse.ArgumentParser(description="Query rules and extraction templates.")
    parser.add_argument("--dir", default="data/templates", help="Directory containing JSON files to query.")
    parser.add_argument("--theory", type=str, help="Filter by T1/T1.5 Theory ID (e.g. 'Perceptual_Fluency')")
    parser.add_argument("--mechanism", type=str, help="Filter by physiological/cognitive mechanism")
    parser.add_argument("--tag", action="append", dest="tags", help="Filter by taxonomy tag (can specify multiple)")
    parser.add_argument("--min-effect", type=float, help="Minimum effect size (strength)")
    parser.add_argument("--max-results", type=int, default=50, help="Maximum results to display")
    
    args = parser.parse_args()
    
    search_dir = Path(args.dir)
    if not search_dir.exists():
        print(f"Directory {search_dir} does not exist.")
        sys.exit(1)

    matched_records = []
    
    for filepath in search_dir.glob("*.json"):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                
                # If the JSON is a list of rules/beliefs:
                if isinstance(data, list):
                    records = data
                # If the JSON wraps findings in a specific key:
                elif "findings" in data and isinstance(data["findings"], list):
                    records = data["findings"]
                elif "beliefs" in data and isinstance(data["beliefs"], dict):
                    records = list(data["beliefs"].values())
                else:
                    # Treat the file itself as a single record
                    records = [data]
                
                for record in records:
                    if isinstance(record, dict) and matches_query(record, args):
                        # Attempt to attach a readable ID for output
                        rec_id = record.get("rule_id") or record.get("belief_id") or record.get("template_id") or filepath.name
                        record_copy = record.copy()
                        record_copy["_source_id"] = rec_id
                        matched_records.append(record_copy)
                        
        except Exception as e:
            # Skip unparseable JSON files silently or log
            pass

    print(f"\nFound {len(matched_records)} records matching query criteria.\n")
    
    for i, r in enumerate(matched_records[:args.max_results]):
        source_id = r.pop("_source_id", "Unknown")
        effect = get_effect_size(r)
        tags = r.get("tags", [])
        theory = r.get("theory_id") or r.get("framework_ids", ["None"])[0] if r.get("framework_ids") else "None"
        
        # Determine human text 
        text = r.get("rule_text") or r.get("content") or r.get("finding_text") or r.get("description") or "No text description."
        
        print(f"[{i+1}] {source_id} | Theory: {theory} | Effect: {effect:.2f}")
        print(f"    Tags: {', '.join(tags) if tags else 'None'}")
        print(f"    Text: \"{text}\"\n")

if __name__ == "__main__":
    main()
