#!/usr/bin/env python3
"""
Completeness Inventory Generator (Sprint 11 Task 11.30).

Generates a machine-readable inventory of what's connected and what isn't
in the CMR building/paper evaluation pipeline.

Usage:
    python scripts/generate_completeness_report.py
    python scripts/generate_completeness_report.py --json > completeness.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Set

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cmr.template_computations import (
    TEMPLATE_COMPUTE_FUNCTIONS,
    list_implemented_templates,
)
from src.cmr.feature_mapping import FEATURE_TO_TEMPLATE_INPUT
from src.cmr.lifespan_moderation import FEATURE_MAPPINGS, ZONE_TO_WIS
from src.cmr.models import get_session, TemplateRecord


def get_json_templates() -> Set[str]:
    """Get template IDs from JSON files in data/templates."""
    templates_dir = Path(__file__).parent.parent / "data" / "templates"
    template_ids = set()
    
    if templates_dir.exists():
        for json_file in templates_dir.glob("*.json"):
            # Extract template ID from filename (e.g., "VF3.json" -> "VF3")
            template_id = json_file.stem
            template_ids.add(template_id)
    
    return template_ids


def get_db_templates(session) -> Set[str]:
    """Get template IDs from TemplateRecord table."""
    records = session.query(TemplateRecord).all()
    return {r.display_id for r in records}


def get_compute_templates() -> Set[str]:
    """Get template IDs that have compute functions."""
    return set(TEMPLATE_COMPUTE_FUNCTIONS.keys())


def get_feature_mapped_templates() -> Set[str]:
    """Get template IDs that have feature mappings."""
    mapped = set(FEATURE_TO_TEMPLATE_INPUT.keys())
    mapped.update(FEATURE_MAPPINGS.keys())
    return mapped


def get_interaction_templates() -> Dict[str, List[str]]:
    """Get templates involved in interaction rules."""
    # Import interactions module
    try:
        from src.cmr.interactions import INTERACTION_RULES
        
        interaction_map = {}
        for rule in INTERACTION_RULES:
            triggers = rule.get("triggers", [])
            for template_id in triggers:
                if template_id not in interaction_map:
                    interaction_map[template_id] = []
                interaction_map[template_id].append(rule.get("name", "unnamed"))
        return interaction_map
    except ImportError:
        return {}
    except Exception:
        return {}


def generate_inventory(session) -> Dict[str, Any]:
    """Generate the completeness inventory."""
    json_templates = get_json_templates()
    db_templates = get_db_templates(session)
    compute_templates = get_compute_templates()
    mapped_templates = get_feature_mapped_templates()
    interaction_templates = get_interaction_templates()
    
    # All known template IDs
    all_templates = json_templates | db_templates | compute_templates
    
    # Build inventory for each template
    inventory = {}
    for template_id in sorted(all_templates):
        has_json = template_id in json_templates
        has_db = template_id in db_templates
        has_compute = template_id in compute_templates
        has_mapping = template_id in mapped_templates
        has_interaction = template_id in interaction_templates
        
        # Determine status
        if has_compute and has_mapping:
            status = "COMPLETE" if has_json and has_db else "PARTIAL_COMPLETE"
        elif has_compute:
            status = "NEEDS_MAPPING"
        elif has_json or has_db:
            status = "STUB"
        else:
            status = "UNKNOWN"
        
        inventory[template_id] = {
            "json_file": has_json,
            "db_record": has_db,
            "compute_fn": has_compute,
            "feature_map": has_mapping,
            "interactions": interaction_templates.get(template_id, []),
            "status": status,
        }
    
    # Compute summary stats
    complete_count = sum(1 for t in inventory.values() if t["status"] == "COMPLETE")
    partial_count = sum(1 for t in inventory.values() if "PARTIAL" in t["status"])
    needs_mapping = sum(1 for t in inventory.values() if t["status"] == "NEEDS_MAPPING")
    stub_count = sum(1 for t in inventory.values() if t["status"] == "STUB")
    
    summary = {
        "total_templates": len(all_templates),
        "complete": complete_count,
        "partial_complete": partial_count,
        "needs_mapping": needs_mapping,
        "stub_only": stub_count,
        "json_files": len(json_templates),
        "db_records": len(db_templates),
        "compute_functions": len(compute_templates),
        "feature_mappings": len(mapped_templates),
        "templates_with_interactions": len(interaction_templates),
        "zone_to_wis_mappings": len(ZONE_TO_WIS),
    }
    
    return {
        "inventory": inventory,
        "summary": summary,
    }


def print_table(data: Dict[str, Any]) -> None:
    """Print inventory as ASCII table."""
    inventory = data["inventory"]
    summary = data["summary"]
    
    print("=" * 80)
    print("TEMPLATE COMPLETENESS INVENTORY")
    print("=" * 80)
    print()
    
    # Header
    print(f"{'Template':<12} | {'JSON':<4} | {'DB':<4} | {'Compute':<7} | {'FeatMap':<7} | {'Interactions':<20} | {'Status':<15}")
    print("-" * 12 + "-+-" + "-" * 4 + "-+-" + "-" * 4 + "-+-" + "-" * 7 + "-+-" + "-" * 7 + "-+-" + "-" * 20 + "-+-" + "-" * 15)
    
    for template_id, info in sorted(inventory.items()):
        json_mark = "Y" if info["json_file"] else "-"
        db_mark = "Y" if info["db_record"] else "-"
        compute_mark = "Y" if info["compute_fn"] else "-"
        map_mark = "Y" if info["feature_map"] else "-"
        interactions = ", ".join(info["interactions"][:2]) if info["interactions"] else "-"
        if len(info["interactions"]) > 2:
            interactions += "..."
        
        print(f"{template_id:<12} | {json_mark:<4} | {db_mark:<4} | {compute_mark:<7} | {map_mark:<7} | {interactions:<20} | {info['status']:<15}")
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"Total templates discovered: {summary['total_templates']}")
    print(f"Complete (compute + mapping): {summary['complete']}/{summary['total_templates']}")
    print(f"Partial complete: {summary['partial_complete']}/{summary['total_templates']}")
    print(f"Needs feature mapping: {summary['needs_mapping']}/{summary['total_templates']}")
    print(f"Stub only (no compute): {summary['stub_only']}/{summary['total_templates']}")
    print()
    print(f"JSON template files: {summary['json_files']}")
    print(f"Database records: {summary['db_records']}")
    print(f"Compute functions: {summary['compute_functions']}")
    print(f"Feature mappings: {summary['feature_mappings']}")
    print(f"Templates with interactions: {summary['templates_with_interactions']}")
    print(f"Zone-to-WIS mappings: {summary['zone_to_wis_mappings']}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Generate completeness inventory")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--db", default="ae.db", help="Database path")
    args = parser.parse_args()
    
    # Initialize database session
    session = get_session(args.db)
    
    # Generate inventory
    data = generate_inventory(session)
    
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print_table(data)


if __name__ == "__main__":
    main()
