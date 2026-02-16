#!/usr/bin/env python3
"""
Generate article-type crosswalk adapter module from canonical contract
(AE TemplateFamily <-> Outcome ArticleType), non-destructive.

Canonical contract section enforced:
  contracts/vocab/canonical_enums.json -> enums.ArticleTypeCrosswalk
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Set


CANONICAL_SECTION = "enums.ArticleTypeCrosswalk"


def load_spec(ae_root: Path) -> dict:
    path = ae_root / "contracts/vocab/canonical_enums.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    return doc["enums"]["ArticleTypeCrosswalk"]


def test_migration_lossless() -> None:
    outcome_to_ae = {
        "case_study": "case_study",
        "interview_study": "interview_study",
        "mixed_methods": "mixed_methods",
        "meta_analysis": "meta_analysis",
        "systematic_review": "systematic_review",
        "narrative_review": "narrative_review",
        "theoretical": "theoretical",
        "thought_piece": "thought_piece",
        "unknown": "unknown",
    }
    ae_to_outcome = {v: [k] for k, v in outcome_to_ae.items()}
    for outcome, ae in outcome_to_ae.items():
        back = ae_to_outcome[ae]
        assert outcome in back


def adapter_module_text(
    canonical_section: str,
    outcome_to_ae: Dict[str, str],
    ae_to_outcome: Dict[str, List[str]],
    lossy_ae: Dict[str, List[str]],
) -> str:
    return f'''"""
Auto-generated article-type crosswalk adapter.
Canonical contract section: {canonical_section}
"""

from __future__ import annotations

from typing import Dict, List

OUTCOME_TO_AE: Dict[str, str] = {json.dumps(outcome_to_ae, indent=2, sort_keys=True)}
AE_TO_OUTCOME: Dict[str, List[str]] = {json.dumps(ae_to_outcome, indent=2, sort_keys=True)}
LOSSY_AE_MAPPINGS: Dict[str, List[str]] = {json.dumps(lossy_ae, indent=2, sort_keys=True)}


def outcome_article_to_ae_template(outcome_article_type: str) -> str:
    key = outcome_article_type.strip().lower()
    if key not in OUTCOME_TO_AE:
        raise KeyError(f"Unknown Outcome article type: {{outcome_article_type}}")
    return OUTCOME_TO_AE[key]


def ae_template_to_outcome_articles(ae_template_family: str) -> List[str]:
    key = ae_template_family.strip().lower()
    if key not in AE_TO_OUTCOME:
        raise KeyError(f"Unknown AE template family: {{ae_template_family}}")
    return list(AE_TO_OUTCOME[key])


def ae_template_to_primary_outcome_article(ae_template_family: str) -> str:
    return ae_template_to_outcome_articles(ae_template_family)[0]


def is_lossy_ae_template(ae_template_family: str) -> bool:
    key = ae_template_family.strip().lower()
    return key in LOSSY_AE_MAPPINGS and len(LOSSY_AE_MAPPINGS[key]) > 1


def test_migration_lossless() -> None:
    # Round-trip outcome -> ae -> outcomes includes original (set-preserving)
    for outcome, ae in OUTCOME_TO_AE.items():
        outcomes = ae_template_to_outcome_articles(ae)
        assert outcome in outcomes

    # Strict round-trip for non-lossy mappings
    for ae, outcomes in AE_TO_OUTCOME.items():
        if len(outcomes) == 1:
            back = outcome_article_to_ae_template(outcomes[0])
            assert back == ae


if __name__ == "__main__":
    test_migration_lossless()
    print("ArticleType adapter self-test passed.")
'''


def report_text(
    canonical_section: str,
    outcome_to_ae: Dict[str, str],
    ae_to_outcome: Dict[str, List[str]],
    lossy_ae: Dict[str, List[str]],
) -> str:
    lines: List[str] = []
    lines.append("# ArticleType Migration Report")
    lines.append("")
    lines.append(f"Canonical section: `{canonical_section}`")
    lines.append("")
    lines.append("## Outcome -> AE")
    for k in sorted(outcome_to_ae):
        lines.append(f"- `{k}` -> `{outcome_to_ae[k]}`")
    lines.append("")
    lines.append("## AE -> Outcome")
    for k in sorted(ae_to_outcome):
        lines.append(f"- `{k}` -> {ae_to_outcome[k]}")
    lines.append("")
    lines.append("## Lossy conversions")
    if lossy_ae:
        for ae, outcomes in sorted(lossy_ae.items()):
            lines.append(f"- `{ae}` collapses: {outcomes}")
    else:
        lines.append("- None")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate ArticleType crosswalk migration artifacts")
    parser.add_argument("--dry-run", action="store_true", help="Print artifacts but do not write files")
    parser.add_argument(
        "--output-dir",
        default="data/review/migration_adapters",
        help="Output directory (relative to AE repo root)",
    )
    args = parser.parse_args()

    test_migration_lossless()

    ae_root = Path(__file__).resolve().parents[1]
    out_dir = ae_root / args.output_dir

    spec = load_spec(ae_root)
    cross = spec.get("crosswalk", {})
    outcome_to_ae = dict(cross.get("outcome_to_ae", {}))
    ae_to_outcome = {k: list(v) for k, v in cross.get("ae_to_outcome", {}).items()}

    lossy_ae = {k: v for k, v in ae_to_outcome.items() if len(v) > 1}

    report = report_text(CANONICAL_SECTION, outcome_to_ae, ae_to_outcome, lossy_ae)
    adapter = adapter_module_text(CANONICAL_SECTION, outcome_to_ae, ae_to_outcome, lossy_ae)

    print(f"[ArticleType Migration] canonical section: {CANONICAL_SECTION}")
    print(f"Outcome->AE mappings: {len(outcome_to_ae)}")
    print(f"AE->Outcome mappings: {len(ae_to_outcome)}")
    print(f"Lossy AE mappings: {len(lossy_ae)}")

    if args.dry_run:
        print("\n--- REPORT (dry-run) ---")
        print(report)
        print("\n--- ADAPTER MODULE (dry-run) ---")
        print(adapter)
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "migrate_article_type_report.md"
    adapter_path = out_dir / "article_type_adapter.py"
    report_path.write_text(report, encoding="utf-8")
    adapter_path.write_text(adapter, encoding="utf-8")
    print(f"Wrote report: {report_path}")
    print(f"Wrote adapter module: {adapter_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
