#!/usr/bin/env python3
"""
Scan CI shape usage across all repos and generate a non-destructive
adapter module + usage report.

Canonical contract section enforced:
  contracts/vocab/canonical_enums.json -> enums.ConfidenceIntervalShape
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


CANONICAL_SECTION = "enums.ConfidenceIntervalShape"
FILE_EXTENSIONS = {".py", ".json", ".sql", ".md", ".yaml", ".yml", ".csv"}
SKIP_PARTS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "archive",
    "Archive",
    "Archive 2",
    "backups",
    "broken_venvs",
}


@dataclass
class FileShapeUsage:
    repo: str
    path: Path
    scalar_lines: List[int]
    object_lines: List[int]


def load_ci_spec(ae_root: Path) -> dict:
    path = ae_root / "contracts/vocab/canonical_enums.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    return doc["enums"]["ConfidenceIntervalShape"]


def ci_object_to_scalars(ci_obj: Optional[object]) -> Tuple[Optional[float], Optional[float]]:
    """
    Convert object/array CI representation to scalar pair.
    Lossless when inputs are valid.
    """
    if ci_obj is None:
        return None, None

    if isinstance(ci_obj, dict):
        lower = ci_obj.get("ci_lower")
        upper = ci_obj.get("ci_upper")
        if lower is None and upper is None:
            return None, None
        if lower is None or upper is None:
            raise ValueError("CI object must contain both ci_lower and ci_upper.")
        return float(lower), float(upper)

    if isinstance(ci_obj, (list, tuple)):
        if len(ci_obj) != 2:
            raise ValueError("CI array must have exactly two elements.")
        return float(ci_obj[0]), float(ci_obj[1])

    raise TypeError(f"Unsupported CI object type: {type(ci_obj)!r}")


def scalars_to_ci_object(ci_lower: Optional[float], ci_upper: Optional[float]) -> Optional[Dict[str, float]]:
    """
    Convert scalar CI representation to canonical object form.
    """
    if ci_lower is None and ci_upper is None:
        return None
    if ci_lower is None or ci_upper is None:
        raise ValueError("Both ci_lower and ci_upper are required, or both must be None.")
    return {"ci_lower": float(ci_lower), "ci_upper": float(ci_upper)}


def test_migration_lossless() -> None:
    obj = {"ci_lower": 0.11, "ci_upper": 0.93}
    lower, upper = ci_object_to_scalars(obj)
    assert lower == 0.11
    assert upper == 0.93
    obj2 = scalars_to_ci_object(lower, upper)
    assert obj2 == obj

    arr = [0.25, 0.75]
    lower2, upper2 = ci_object_to_scalars(arr)
    assert scalars_to_ci_object(lower2, upper2) == {"ci_lower": 0.25, "ci_upper": 0.75}

    assert ci_object_to_scalars(None) == (None, None)
    assert scalars_to_ci_object(None, None) is None


def should_scan(path: Path) -> bool:
    if path.suffix.lower() not in FILE_EXTENSIONS:
        return False
    for part in path.parts:
        lower = part.lower()
        if part in SKIP_PARTS:
            return False
        if "venv" in lower:
            return False
        if lower.startswith("archive"):
            return False
    return True


def scan_file_for_shapes(repo_name: str, path: Path) -> Optional[FileShapeUsage]:
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return None

    scalar_lines: List[int] = []
    object_lines: List[int] = []
    scalar_pattern = re.compile(r"\b(ci_lower|ci_upper|effect_ci_lower|effect_ci_upper|ci95)\b")
    object_pattern = re.compile(r"\bconfidence_interval\b")

    for i, line in enumerate(lines, start=1):
        if scalar_pattern.search(line):
            scalar_lines.append(i)
        if object_pattern.search(line):
            object_lines.append(i)

    if not scalar_lines and not object_lines:
        return None
    return FileShapeUsage(
        repo=repo_name,
        path=path,
        scalar_lines=scalar_lines,
        object_lines=object_lines,
    )


def adapter_module_text(canonical_section: str) -> str:
    return f'''"""
Auto-generated CI shape adapter.
Canonical contract section: {canonical_section}
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple


def ci_object_to_scalars(ci_obj: Optional[object]) -> Tuple[Optional[float], Optional[float]]:
    if ci_obj is None:
        return None, None
    if isinstance(ci_obj, dict):
        lower = ci_obj.get("ci_lower")
        upper = ci_obj.get("ci_upper")
        if lower is None and upper is None:
            return None, None
        if lower is None or upper is None:
            raise ValueError("CI object must contain both ci_lower and ci_upper.")
        return float(lower), float(upper)
    if isinstance(ci_obj, (list, tuple)):
        if len(ci_obj) != 2:
            raise ValueError("CI array must have exactly two elements.")
        return float(ci_obj[0]), float(ci_obj[1])
    raise TypeError(f"Unsupported CI object type: {{type(ci_obj)!r}}")


def scalars_to_ci_object(ci_lower: Optional[float], ci_upper: Optional[float]) -> Optional[Dict[str, float]]:
    if ci_lower is None and ci_upper is None:
        return None
    if ci_lower is None or ci_upper is None:
        raise ValueError("Both ci_lower and ci_upper are required, or both must be None.")
    return {{"ci_lower": float(ci_lower), "ci_upper": float(ci_upper)}}


def test_migration_lossless() -> None:
    obj = {{"ci_lower": 0.11, "ci_upper": 0.93}}
    lo, hi = ci_object_to_scalars(obj)
    assert (lo, hi) == (0.11, 0.93)
    assert scalars_to_ci_object(lo, hi) == obj

    lo2, hi2 = ci_object_to_scalars([0.25, 0.75])
    assert scalars_to_ci_object(lo2, hi2) == {{"ci_lower": 0.25, "ci_upper": 0.75}}


if __name__ == "__main__":
    test_migration_lossless()
    print("CI adapter self-test passed.")
'''


def build_report(usages: List[FileShapeUsage], canonical_section: str) -> str:
    lines: List[str] = []
    lines.append("# CI Shape Migration Report")
    lines.append("")
    lines.append(f"Canonical section: `{canonical_section}`")
    lines.append("")
    lines.append("| Repo | File | Scalar lines (`ci_lower`/`ci_upper`) | Object lines (`confidence_interval`) |")
    lines.append("|---|---|---|---|")
    for u in sorted(usages, key=lambda x: (x.repo, str(x.path))):
        scalar = ", ".join(str(n) for n in u.scalar_lines) if u.scalar_lines else "-"
        obj = ", ".join(str(n) for n in u.object_lines) if u.object_lines else "-"
        lines.append(f"| {u.repo} | `{u.path}` | {scalar} | {obj} |")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate CI shape migration artifacts")
    parser.add_argument("--dry-run", action="store_true", help="Print artifacts but do not write files")
    parser.add_argument(
        "--output-dir",
        default="data/review/migration_adapters",
        help="Output directory (relative to AE repo root)",
    )
    args = parser.parse_args()

    test_migration_lossless()

    ae_root = Path(__file__).resolve().parents[1]
    repos_root = ae_root.parent
    out_dir = ae_root / args.output_dir

    spec = load_ci_spec(ae_root)
    canonical_section = CANONICAL_SECTION
    _ = spec  # Explicitly loaded to bind check to contract file.

    repos = {
        "Article_Eater_PostQuinean_v1": ae_root,
        "Article_Finder_v3_2_3": repos_root / "Article_Finder_v3_2_3",
        "BN_graphical": repos_root / "BN_graphical",
        "Tagging_Contractor": repos_root / "Tagging_Contractor",
        "Outcome_Contractor": repos_root / "Outcome_Contractor",
    }

    usages: List[FileShapeUsage] = []
    for repo_name, repo_root in repos.items():
        if not repo_root.exists():
            continue
        for path in repo_root.rglob("*"):
            if not path.is_file() or not should_scan(path):
                continue
            usage = scan_file_for_shapes(repo_name, path)
            if usage:
                usages.append(usage)

    report = build_report(usages, canonical_section)
    adapter = adapter_module_text(canonical_section)

    print(f"[CI Shape Migration] canonical section: {canonical_section}")
    print(f"Files with CI shape usage: {len(usages)}")

    if args.dry_run:
        print("\n--- REPORT (dry-run) ---")
        print(report)
        print("\n--- ADAPTER MODULE (dry-run) ---")
        print(adapter)
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "migrate_ci_shape_report.md"
    adapter_path = out_dir / "ci_shape_adapter.py"
    report_path.write_text(report, encoding="utf-8")
    adapter_path.write_text(adapter, encoding="utf-8")
    print(f"Wrote report: {report_path}")
    print(f"Wrote adapter module: {adapter_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
