#!/usr/bin/env python3
"""M-03a: Variable Migration Script.

Reads schemas/canonical_variables.json and renames all variable references
in data/templates/*.json to their canonical names using the alias_map.

IMPORTANT: Do NOT run this until CC completes M-01 (schema field migration).
Run order: E-01 → M-01 (field names) → M-03b (variable names via this script).

Usage:
    python3 scripts/migrate_variables.py --dry-run    # Preview changes
    python3 scripts/migrate_variables.py              # Apply changes
"""

import argparse
import json
import glob
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def load_alias_map(schema_path: str) -> Dict[str, str]:
    """Load the alias_map from the canonical variables schema."""
    with open(schema_path) as f:
        schema = json.load(f)
    return schema.get("alias_map", {})


def walk_and_rename(
    obj: Any,
    alias_map: Dict[str, str],
    path: str = "",
    renames: List[Tuple[str, str, str]] = None,
) -> Any:
    """Recursively walk a JSON object, renaming variable references.
    
    Targets:
    - mechanism_chain[].from / .to fields (variable names in causal links)
    - calibrated_parameters keys
    - population_modifiers keys  
    - architectural_modifiers keys
    - architectural_modifier_coefficients keys
    - cross_template_interactions[].shared_variables
    """
    if renames is None:
        renames = []

    if isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.items():
            current_path = f"{path}.{key}" if path else key

            # Check if this key is a variable name that should be renamed
            # (only for specific parent contexts)
            parent = path.rsplit(".", 1)[-1] if "." in path else path
            rename_contexts = {
                "calibrated_parameters",
                "population_modifiers",
                "architectural_modifiers",
                "architectural_modifier_coefficients",
                "population_modifier_coefficients",
            }

            new_key = key
            if parent in rename_contexts and key in alias_map:
                canonical = alias_map[key]
                if canonical != key:
                    new_key = canonical
                    renames.append((current_path, key, canonical))

            # Recurse into value
            new_value = walk_and_rename(value, alias_map, current_path, renames)

            # Special handling for mechanism_chain step from/to fields
            if key in ("from", "to") and isinstance(value, str) and value in alias_map:
                canonical = alias_map[value]
                if canonical != value:
                    new_value = canonical
                    renames.append((current_path, value, canonical))

            # Handle shared_variables in cross_template_interactions
            if key == "shared_variables" and isinstance(value, list):
                new_value = []
                for v in value:
                    if isinstance(v, str) and v in alias_map:
                        canonical = alias_map[v]
                        if canonical != v:
                            renames.append((current_path, v, canonical))
                            new_value.append(canonical)
                        else:
                            new_value.append(v)
                    else:
                        new_value.append(v)

            new_dict[new_key] = new_value
        return new_dict

    elif isinstance(obj, list):
        return [
            walk_and_rename(item, alias_map, f"{path}[{i}]", renames)
            for i, item in enumerate(obj)
        ]

    return obj


def migrate_template(
    filepath: str,
    alias_map: Dict[str, str],
    dry_run: bool = True,
) -> List[Tuple[str, str, str]]:
    """Migrate a single template file. Returns list of (path, old, new) renames."""
    with open(filepath) as f:
        data = json.load(f)

    renames: List[Tuple[str, str, str]] = []
    migrated = walk_and_rename(data, alias_map, "", renames)

    if renames and not dry_run:
        with open(filepath, "w") as f:
            json.dump(migrated, f, indent=2, ensure_ascii=False)
            f.write("\n")

    return renames


def main():
    parser = argparse.ArgumentParser(description="Migrate template variables to canonical names")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    parser.add_argument("--schema", default="schemas/canonical_variables.json", help="Path to canonical variables schema")
    parser.add_argument("--templates", default="data/templates", help="Directory containing template JSONs")
    args = parser.parse_args()

    # Resolve paths
    repo_root = Path(__file__).parent.parent
    schema_path = repo_root / args.schema
    templates_dir = repo_root / args.templates

    if not schema_path.exists():
        print(f"ERROR: Schema not found: {schema_path}")
        sys.exit(1)

    alias_map = load_alias_map(str(schema_path))
    print(f"Loaded alias_map with {len(alias_map)} entries")

    template_files = sorted(glob.glob(str(templates_dir / "*.json")))
    print(f"Found {len(template_files)} templates")

    if args.dry_run:
        print("\n=== DRY RUN — No files will be modified ===\n")

    total_renames = 0
    files_changed = 0

    for filepath in template_files:
        basename = os.path.basename(filepath)
        renames = migrate_template(filepath, alias_map, dry_run=args.dry_run)

        if renames:
            files_changed += 1
            print(f"\n  {basename}: {len(renames)} renames")
            for path, old, new in renames:
                print(f"    {path}: {old} → {new}")
            total_renames += len(renames)

    print(f"\n{'DRY RUN ' if args.dry_run else ''}SUMMARY:")
    print(f"  Templates scanned: {len(template_files)}")
    print(f"  Templates {'would be ' if args.dry_run else ''}modified: {files_changed}")
    print(f"  Total renames: {total_renames}")

    if args.dry_run and total_renames > 0:
        print(f"\n  Run without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
