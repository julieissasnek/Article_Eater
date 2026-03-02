#!/usr/bin/env python3
"""
field_reviewer.py — Extraction Field Reviewer & Normalizer
===========================================================

Reads every extraction JSON, checks each field against the canonical spec
in schemas/extraction_field_spec.json, and:
  - Fixes: normalizes fixable non-conforming values
  - Flags: marks ambiguous values for manual review
  - Skips: marks terminally confused values as unfixable

Usage:
  python3 scripts/field_reviewer.py                    # Dry-run report
  python3 scripts/field_reviewer.py --fix              # Fix in-place
  python3 scripts/field_reviewer.py --report out.md    # Write markdown report
"""

import argparse
import json
import glob
import os
import re
import sys
from pathlib import Path
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
SPEC_PATH = PROJECT_ROOT / "schemas" / "extraction_field_spec.json"
DATA_DIR = PROJECT_ROOT / "data" / "extractions"


# ══════════════════════════════════════════════════════════════════
# Field Spec Loader
# ══════════════════════════════════════════════════════════════════

def load_spec() -> Dict:
    """Load the canonical field spec."""
    with open(SPEC_PATH) as f:
        return json.load(f)


# ══════════════════════════════════════════════════════════════════
# Validators
# ══════════════════════════════════════════════════════════════════

class FieldIssue:
    """A single field validation issue."""
    def __init__(self, file: str, field: str, severity: str, message: str,
                 original: Any = None, fixed: Any = None):
        self.file = file
        self.field = field
        self.severity = severity  # "fixed", "ambiguous", "terminal"
        self.message = message
        self.original = original
        self.fixed = fixed

    def to_dict(self):
        d = {"file": self.file, "field": self.field, "severity": self.severity,
             "message": self.message}
        if self.original is not None:
            d["original"] = str(self.original)[:100]
        if self.fixed is not None:
            d["fixed"] = str(self.fixed)[:100]
        return d


def validate_field(value: Any, spec: Dict, field_name: str, file_name: str) -> Tuple[Any, Optional[FieldIssue]]:
    """
    Validate a single field value against its spec.
    Returns (possibly_fixed_value, issue_or_None).
    """
    ftype = spec.get("type", "string")

    # --- Null handling ---
    if value is None:
        if spec.get("required"):
            return value, FieldIssue(file_name, field_name, "terminal",
                                     "Required field is null")
        return value, None

    # --- Type checking ---
    if ftype == "string":
        if not isinstance(value, str):
            try:
                fixed = str(value)
                return fixed, FieldIssue(file_name, field_name, "fixed",
                                         f"Converted {type(value).__name__} to string",
                                         original=value, fixed=fixed)
            except:
                return value, FieldIssue(file_name, field_name, "terminal",
                                         f"Cannot convert {type(value).__name__} to string")
        # Length checks
        if "min_length" in spec and len(value) < spec["min_length"]:
            return value, FieldIssue(file_name, field_name, "ambiguous",
                                     f"Too short: {len(value)} < {spec['min_length']}")
        if "max_length" in spec and len(value) > spec["max_length"]:
            return value, FieldIssue(file_name, field_name, "ambiguous",
                                     f"Too long: {len(value)} > {spec['max_length']}")
        # Pattern
        if "pattern" in spec and not re.match(spec["pattern"], value):
            return value, FieldIssue(file_name, field_name, "ambiguous",
                                     f"Does not match pattern: {spec['pattern']}",
                                     original=value)

    elif ftype == "integer" or ftype == "integer_or_null":
        if value is None and "null" in ftype:
            return value, None
        if isinstance(value, str):
            # Try to parse string as integer
            try:
                cleaned = re.sub(r'[,\s]', '', value)
                fixed = int(float(cleaned))
                issue = FieldIssue(file_name, field_name, "fixed",
                                   f"Parsed string '{value}' as int {fixed}",
                                   original=value, fixed=fixed)
                return fixed, issue
            except:
                return value, FieldIssue(file_name, field_name, "terminal",
                                         f"Cannot parse '{value}' as integer")
        if isinstance(value, float):
            fixed = int(value)
            return fixed, FieldIssue(file_name, field_name, "fixed",
                                     f"Converted float {value} to int {fixed}",
                                     original=value, fixed=fixed)
        if not isinstance(value, int):
            return value, FieldIssue(file_name, field_name, "terminal",
                                     f"Expected integer, got {type(value).__name__}")
        # Range
        if "min" in spec and value < spec["min"]:
            return value, FieldIssue(file_name, field_name, "ambiguous",
                                     f"Below minimum: {value} < {spec['min']}")
        if "max" in spec and value > spec["max"]:
            return value, FieldIssue(file_name, field_name, "ambiguous",
                                     f"Above maximum: {value} > {spec['max']}")

    elif ftype in ("float", "number_or_null"):
        if value is None:
            return value, None
        if isinstance(value, str):
            try:
                cleaned = value.strip()
                # Handle scientific p-value conventions
                if cleaned.lower() in ("ns", "n.s.", "n.s", "not significant"):
                    return 1.0, FieldIssue(file_name, field_name, "fixed",
                                           f"Interpreted '{value}' as p=1.0 (not significant)",
                                           original=value, fixed=1.0)
                if cleaned.startswith("<"):
                    num = float(re.sub(r'[<\s]', '', cleaned))
                    return num, FieldIssue(file_name, field_name, "fixed",
                                           f"Interpreted '{value}' as {num}",
                                           original=value, fixed=num)
                if cleaned.startswith(">"):
                    num = float(re.sub(r'[>\s]', '', cleaned)) + 0.01
                    return num, FieldIssue(file_name, field_name, "fixed",
                                           f"Interpreted '{value}' as {num}",
                                           original=value, fixed=num)
                cleaned = re.sub(r'[,\s]', '', cleaned)
                # Handle ranges like "0.3-0.5" → take mean
                if '-' in cleaned and not cleaned.startswith('-'):
                    parts = cleaned.split('-')
                    fixed = sum(float(p) for p in parts) / len(parts)
                else:
                    fixed = float(cleaned)
                return fixed, FieldIssue(file_name, field_name, "fixed",
                                         f"Parsed string '{value}' as float {fixed}",
                                         original=value, fixed=fixed)
            except:
                return value, FieldIssue(file_name, field_name, "terminal",
                                         f"Cannot parse '{value}' as number")
        if not isinstance(value, (int, float)):
            return value, FieldIssue(file_name, field_name, "terminal",
                                     f"Expected number, got {type(value).__name__}")
        # Range
        if "min" in spec and value < spec["min"]:
            return value, FieldIssue(file_name, field_name, "ambiguous",
                                     f"Below minimum: {value} < {spec['min']}")
        if "max" in spec and value > spec["max"]:
            return value, FieldIssue(file_name, field_name, "ambiguous",
                                     f"Above maximum: {value} > {spec['max']}")

    elif ftype in ("enum", "enum_or_null"):
        if value is None:
            return value, None
        valid = spec.get("values", [])
        normalize = spec.get("normalize_map", {})
        val_str = str(value).strip().lower()
        if val_str in normalize:
            fixed = normalize[val_str]
            return fixed, FieldIssue(file_name, field_name, "fixed",
                                     f"Normalized '{value}' → '{fixed}'",
                                     original=value, fixed=fixed)
        # Case-insensitive match
        for v in valid:
            if v is not None and val_str == str(v).lower():
                if value != v:
                    return v, FieldIssue(file_name, field_name, "fixed",
                                         f"Fixed case: '{value}' → '{v}'",
                                         original=value, fixed=v)
                return value, None
        # Check if null is valid
        if value is None and None in valid:
            return value, None
        return value, FieldIssue(file_name, field_name, "ambiguous",
                                 f"'{value}' not in {valid[:5]}...",
                                 original=value)

    elif ftype == "list_of_strings":
        if not isinstance(value, list):
            return value, FieldIssue(file_name, field_name, "terminal",
                                     f"Expected list, got {type(value).__name__}")

    return value, None


# ══════════════════════════════════════════════════════════════════
# Main Reviewer
# ══════════════════════════════════════════════════════════════════

def review_all(fix: bool = False) -> Dict[str, Any]:
    """
    Review all extraction JSONs against the canonical spec.
    
    Returns a report dict with statistics and issues.
    """
    spec = load_spec()
    field_specs = spec.get("fields", {})
    finding_specs = spec.get("finding_fields", {})

    files = sorted(glob.glob(str(DATA_DIR / "*.json")))
    issues: List[FieldIssue] = []
    stats = {
        "total_files": len(files),
        "total_findings": 0,
        "fixed": 0,
        "ambiguous": 0,
        "terminal": 0,
        "clean": 0,
    }
    severity_by_field = defaultdict(Counter)
    fixed_files = 0

    for fpath in files:
        try:
            with open(fpath) as f:
                data = json.load(f)
        except json.JSONDecodeError:
            issues.append(FieldIssue(os.path.basename(fpath), "_file_", "terminal",
                                     "Invalid JSON"))
            stats["terminal"] += 1
            continue

        if not isinstance(data, dict):
            issues.append(FieldIssue(os.path.basename(fpath), "_file_", "terminal",
                                     f"Root is {type(data).__name__}, expected dict"))
            stats["terminal"] += 1
            continue

        fname = os.path.basename(fpath)
        file_modified = False

        # Validate top-level fields
        for field_name, fspec in field_specs.items():
            if field_name in data:
                fixed_val, issue = validate_field(data[field_name], fspec, field_name, fname)
                if issue:
                    issues.append(issue)
                    stats[issue.severity] += 1
                    severity_by_field[field_name][issue.severity] += 1
                    if issue.severity == "fixed" and fix:
                        data[field_name] = fixed_val
                        file_modified = True
                else:
                    stats["clean"] += 1
            elif fspec.get("required"):
                issues.append(FieldIssue(fname, field_name, "terminal",
                                         "Required field missing"))
                stats["terminal"] += 1

        # Validate findings
        for finding in data.get("findings", []):
            if not isinstance(finding, dict):
                continue
            stats["total_findings"] += 1
            for field_name, fspec in finding_specs.items():
                if field_name in finding:
                    fixed_val, issue = validate_field(
                        finding[field_name], fspec, f"finding.{field_name}", fname
                    )
                    if issue:
                        issues.append(issue)
                        stats[issue.severity] += 1
                        severity_by_field[f"finding.{field_name}"][issue.severity] += 1
                        if issue.severity == "fixed" and fix:
                            # Preserve original p-value strings (Expert Decision #7)
                            if field_name == "p_value" and isinstance(finding.get(field_name), str):
                                finding["p_value_original"] = finding[field_name]
                            finding[field_name] = fixed_val
                            file_modified = True
                    else:
                        stats["clean"] += 1

        # Write fixed file
        if fix and file_modified:
            with open(fpath, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            fixed_files += 1

    stats["fixed_files"] = fixed_files
    stats["total_issues"] = len(issues)

    return {
        "stats": stats,
        "issues": issues,
        "severity_by_field": dict(severity_by_field),
    }


def generate_report(result: Dict) -> str:
    """Generate a markdown report from review results."""
    stats = result["stats"]
    issues = result["issues"]
    severity_by_field = result["severity_by_field"]

    lines = [
        "# Extraction Field Review Report\n",
        f"**Files reviewed**: {stats['total_files']}",
        f"**Findings reviewed**: {stats['total_findings']}",
        f"**Total issues**: {stats['total_issues']}",
        "",
        "## Summary\n",
        f"| Severity | Count | % |",
        f"|----------|-------|---|",
        f"| ✅ Clean | {stats['clean']} | {stats['clean']/(stats['clean']+stats['total_issues'])*100:.1f}% |",
        f"| 🔧 Fixed | {stats['fixed']} | {stats['fixed']/(stats['total_issues'] or 1)*100:.1f}% |",
        f"| ⚠️  Ambiguous | {stats['ambiguous']} | {stats['ambiguous']/(stats['total_issues'] or 1)*100:.1f}% |",
        f"| ❌ Terminal | {stats['terminal']} | {stats['terminal']/(stats['total_issues'] or 1)*100:.1f}% |",
        "",
    ]

    if severity_by_field:
        lines.append("## Issues by Field\n")
        lines.append("| Field | Fixed | Ambiguous | Terminal |")
        lines.append("|-------|-------|-----------|----------|")
        for field, counts in sorted(severity_by_field.items(), key=lambda x: -sum(x[1].values())):
            lines.append(
                f"| {field} | {counts.get('fixed', 0)} | "
                f"{counts.get('ambiguous', 0)} | {counts.get('terminal', 0)} |"
            )

    # Sample issues
    if issues:
        lines.append("\n## Sample Issues (first 20)\n")
        for issue in issues[:20]:
            d = issue.to_dict()
            lines.append(f"- **{d['severity']}** `{d['field']}` in `{d['file']}`: {d['message']}")

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Review extraction field quality")
    parser.add_argument("--fix", action="store_true", help="Fix issues in-place")
    parser.add_argument("--report", type=str, help="Write markdown report to file")
    args = parser.parse_args()

    print("🔍 Reviewing extraction fields...")
    result = review_all(fix=args.fix)

    report = generate_report(result)
    print(report)

    if args.report:
        with open(args.report, 'w') as f:
            f.write(report)
        print(f"\n📄 Report written to {args.report}")

    stats = result["stats"]
    print(f"\n{'='*50}")
    print(f"Total: {stats['total_issues']} issues across {stats['total_files']} files")
    if args.fix:
        print(f"Fixed {stats['fixed_files']} files")
    terminal_rate = stats['terminal'] / max(stats['total_issues'], 1) * 100
    print(f"Terminal rate: {terminal_rate:.1f}%")


if __name__ == "__main__":
    main()
