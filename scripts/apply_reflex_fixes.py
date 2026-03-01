#!/usr/bin/env python3
"""
Apply local reflex fixes to all extraction files.

Runs DirectionNormalizationReflex and other auto-fixable reflexes across
all extraction files in data/extractions/*.json.

Generates a summary report of fixes applied.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, field

# Add src to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from qa.reflex_system import DirectionNormalizationReflex


@dataclass
class RefixReport:
    """Summary of all fixes applied."""
    total_files_scanned: int = 0
    total_files_modified: int = 0
    total_files_quarantined: int = 0

    # Count by fix type
    directions_fixed: int = 0
    empty_findings_flagged: int = 0
    malformed_json_quarantined: int = 0
    null_antecedents_flagged: int = 0

    # Details
    modified_files: List[str] = field(default_factory=list)
    quarantined_files: List[Dict[str, Any]] = field(default_factory=list)
    flagged_issues: List[Dict[str, Any]] = field(default_factory=list)

    def print_summary(self):
        """Print human-readable summary."""
        print("\n" + "=" * 70)
        print("REFLEX FIX REPORT")
        print("=" * 70)
        print(f"Total files scanned:           {self.total_files_scanned}")
        print(f"Total files modified:          {self.total_files_modified}")
        print(f"Total files quarantined:       {self.total_files_quarantined}")
        print(f"\nFixes applied:")
        print(f"  - Direction values normalized: {self.directions_fixed}")
        print(f"  - Empty findings flagged:      {self.empty_findings_flagged}")
        print(f"  - Null antecedents flagged:    {self.null_antecedents_flagged}")
        print(f"  - Malformed JSON quarantined:  {self.malformed_json_quarantined}")

        if self.modified_files:
            print(f"\nModified files ({len(self.modified_files)}):")
            for fname in sorted(self.modified_files)[:10]:
                print(f"  - {fname}")
            if len(self.modified_files) > 10:
                print(f"  ... and {len(self.modified_files) - 10} more")

        if self.quarantined_files:
            print(f"\nQuarantined files ({len(self.quarantined_files)}):")
            for item in self.quarantined_files[:5]:
                print(f"  - {item['file']}: {item['reason']}")
            if len(self.quarantined_files) > 5:
                print(f"  ... and {len(self.quarantined_files) - 5} more")

        if self.flagged_issues:
            print(f"\nFlagged issues ({len(self.flagged_issues)}):")
            issue_types = {}
            for issue in self.flagged_issues:
                issue_type = issue.get('type', 'unknown')
                issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
            for issue_type, count in sorted(issue_types.items()):
                print(f"  - {issue_type}: {count}")
        print("=" * 70 + "\n")


def apply_reflex_fixes() -> RefixReport:
    """Apply all auto-fixable reflexes to extraction files."""
    extractions_dir = PROJECT_ROOT / "data" / "extractions"
    quarantine_dir = extractions_dir / "quarantine"
    quarantine_dir.mkdir(parents=True, exist_ok=True)

    report = RefixReport()

    # Collect all extraction files
    json_files = sorted(extractions_dir.glob("*.json"))
    report.total_files_scanned = len(json_files)

    print(f"Scanning {report.total_files_scanned} extraction files...")

    for json_file in json_files:
        if json_file.name == "quarantine":
            continue

        # 1. Check for malformed JSON
        try:
            with open(json_file, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            # Move to quarantine
            dst = quarantine_dir / json_file.name
            json_file.rename(dst)
            report.total_files_quarantined += 1
            report.malformed_json_quarantined += 1
            report.quarantined_files.append({
                "file": json_file.name,
                "reason": f"JSON parse error: {str(e)[:50]}"
            })
            continue
        except Exception as e:
            report.flagged_issues.append({
                "file": json_file.name,
                "type": "read_error",
                "message": str(e)[:100]
            })
            continue

        # Skip non-extraction files (batch logs, query logs, etc.)
        if not isinstance(data, dict):
            continue

        modified = False

        # 2. Check and fix direction values
        if "findings" in data and isinstance(data["findings"], list):
            canonical_directions = {"increase", "decrease", "no_effect", "mixed"}

            for finding in data["findings"]:
                direction = finding.get("direction", "").lower().strip()
                if direction and direction not in canonical_directions:
                    # Normalize
                    normalized = _normalize_direction(direction)
                    finding["direction"] = normalized
                    report.directions_fixed += 1
                    modified = True

                # Check for null antecedent
                antecedent = finding.get("antecedent")
                if antecedent is None or antecedent == "":
                    report.null_antecedents_flagged += 1
                    report.flagged_issues.append({
                        "file": json_file.name,
                        "type": "null_antecedent",
                        "finding_index": data["findings"].index(finding)
                    })

        # 3. Check for empty findings
        findings = data.get("findings", [])
        if len(findings) == 0:
            report.empty_findings_flagged += 1
            report.flagged_issues.append({
                "file": json_file.name,
                "type": "empty_findings",
                "doi": data.get("doi", "unknown")
            })

        # 4. Write back if modified
        if modified:
            with open(json_file, "w") as f:
                json.dump(data, f, indent=2)
            report.total_files_modified += 1
            report.modified_files.append(json_file.name)

    return report


def _normalize_direction(bad_value: str) -> str:
    """Map non-canonical direction to nearest canonical."""
    bad_val_lower = bad_value.lower().strip()

    if "incr" in bad_val_lower or "+" in bad_val_lower or "up" in bad_val_lower:
        return "increase"
    elif "decr" in bad_val_lower or "-" in bad_val_lower or "down" in bad_val_lower:
        return "decrease"
    elif "no" in bad_val_lower or "none" in bad_val_lower or "null" in bad_val_lower:
        return "no_effect"
    elif "mix" in bad_val_lower or "both" in bad_val_lower:
        return "mixed"

    return "no_effect"


if __name__ == "__main__":
    report = apply_reflex_fixes()
    report.print_summary()
