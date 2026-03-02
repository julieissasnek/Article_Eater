#!/usr/bin/env python3
"""E-03b: Variable Lint Script.

Checks that all variable names used in template JSONs are registered in
the canonical variable ontology (schemas/canonical_variables.json).

Reports any unregistered variables. Intended as a CI/pre-commit check —
after M-03b migration, all templates should pass with 0 unregistered.

Usage:
    python3 scripts/lint_variables.py                     # Lint all templates
    python3 scripts/lint_variables.py data/templates/T1.json  # Lint one file
    python3 scripts/lint_variables.py --strict            # Exit code 1 on any unregistered
"""

import argparse
import json
import glob
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


def load_registered_variables(schema_path: str) -> Set[str]:
    """Load all known variable names (canonical + aliases + mechanism levels + calibration metadata) from the schema."""
    with open(schema_path) as f:
        schema = json.load(f)

    registered = set()

    # All canonical names
    for domain_data in schema.get("domains", {}).values():
        for var_name in domain_data.get("variables", {}):
            registered.add(var_name)

    # All aliases
    for alias in schema.get("alias_map", {}):
        registered.add(alias)

    # Mechanism chain levels (valid in mechanism_chain from/to)
    for level_name in schema.get("mechanism_levels", {}).get("levels", {}):
        registered.add(level_name)

    # Calibration metadata keys (valid in calibrated_parameters)
    for meta_key in schema.get("calibration_metadata", {}).get("keys", {}):
        registered.add(meta_key)

    return registered


def extract_variable_names(obj: Any, path: str = "") -> List[Tuple[str, str]]:
    """Extract all variable name references from a template JSON.
    
    Returns list of (field_path, variable_name) tuples.
    """
    results = []

    if isinstance(obj, dict):
        parent = path.rsplit(".", 1)[-1] if "." in path else path

        # Keys in these contexts ARE variable names
        variable_key_contexts = {
            "calibrated_parameters",
            "population_modifiers",
            "architectural_modifiers",
            "architectural_modifier_coefficients",
            "population_modifier_coefficients",
        }

        for key, value in obj.items():
            current_path = f"{path}.{key}" if path else key

            # If parent is a variable context, the key is a variable name
            if parent in variable_key_contexts:
                results.append((current_path, key))

            # mechanism_chain from/to values are variable names
            if key in ("from", "to") and isinstance(value, str):
                results.append((current_path, value))

            # shared_variables list entries are variable names
            if key == "shared_variables" and isinstance(value, list):
                for i, v in enumerate(value):
                    if isinstance(v, str):
                        results.append((f"{current_path}[{i}]", v))

            # Recurse
            results.extend(extract_variable_names(value, current_path))

    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            results.extend(extract_variable_names(item, f"{path}[{i}]"))

    return results


def lint_template(
    filepath: str,
    registered: Set[str],
) -> List[Tuple[str, str]]:
    """Lint a single template. Returns list of (field_path, unregistered_var)."""
    with open(filepath) as f:
        data = json.load(f)

    all_vars = extract_variable_names(data)
    unregistered = [
        (path, var) for path, var in all_vars
        if var not in registered
        # Skip sub-field notation (e.g. var.source, var.CI_95)
        and "." not in var
        # Skip obvious non-variable keys
        and var not in {"description", "unit", "source", "notes", "name", "type", "formula"}
    ]

    return unregistered


def main():
    parser = argparse.ArgumentParser(description="Lint template variables against canonical registry")
    parser.add_argument("files", nargs="*", help="Specific template files to lint (default: all)")
    parser.add_argument("--schema", default="schemas/canonical_variables.json", help="Path to schema")
    parser.add_argument("--templates", default="data/templates", help="Templates directory")
    parser.add_argument("--strict", action="store_true", help="Exit with code 1 if any unregistered found")
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    schema_path = repo_root / args.schema

    if not schema_path.exists():
        print(f"ERROR: Schema not found: {schema_path}")
        sys.exit(1)

    registered = load_registered_variables(str(schema_path))
    print(f"Registry: {len(registered)} known variable names (canonical + aliases)")

    # Determine files to lint
    if args.files:
        template_files = args.files
    else:
        templates_dir = repo_root / args.templates
        template_files = sorted(glob.glob(str(templates_dir / "*.json")))

    print(f"Scanning {len(template_files)} templates...\n")

    total_unregistered = 0
    files_with_issues = 0

    for filepath in template_files:
        basename = os.path.basename(filepath)
        issues = lint_template(filepath, registered)

        if issues:
            files_with_issues += 1
            print(f"  FAIL  {basename}: {len(issues)} unregistered variable(s)")
            for path, var in issues:
                print(f"         {path}: {var}")
            total_unregistered += len(issues)
        # Don't print PASS for every file — too noisy

    print(f"\n{'='*50}")
    if total_unregistered == 0:
        print(f"PASS — All variables in {len(template_files)} templates are registered.")
        sys.exit(0)
    else:
        print(f"{'FAIL' if args.strict else 'WARN'} — {total_unregistered} unregistered variable(s) in {files_with_issues} template(s)")
        print(f"  Templates scanned: {len(template_files)}")
        print(f"  Templates clean: {len(template_files) - files_with_issues}")
        print(f"  Templates with issues: {files_with_issues}")
        sys.exit(1 if args.strict else 0)


if __name__ == "__main__":
    main()
