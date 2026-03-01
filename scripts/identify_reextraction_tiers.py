#!/usr/bin/env python3
"""
Score all extractions and identify Tier 1/2/3 re-extraction candidates.

Reads each extraction file, validates it using a practical scoring system,
and outputs three files:
- tier1_reextract.json: articles scoring < 0.65 (full re-extraction)
- tier2_surgical.json: articles scoring 0.65-0.85 (surgical LLM fixes)
- tier3_ok.json: articles scoring > 0.85 (just add new fields)

Scoring penalties:
- antecedent is vague or null: -0.20
- direction is non-canonical: -0.15
- sample_size is null for empirical findings: -0.10
- n_findings == 0: automatic Tier 1
- very short antecedents (<10 chars): -0.10
- no theory_links at all: -0.05

Base score is 1.0, subtract penalties.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, field
import statistics

# Add src to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


@dataclass
class ExtractionScore:
    """Score and metadata for a single extraction."""
    file_path: str
    doi: str
    n_findings: int
    score: float
    penalties: Dict[str, float] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    tier: str = ""  # "tier1", "tier2", "tier3"

    def add_penalty(self, label: str, amount: float, issue: str):
        """Record a penalty and associated issue."""
        self.penalties[label] = amount
        self.score -= amount
        self.issues.append(issue)

    def determine_tier(self):
        """Determine tier based on score."""
        if self.n_findings == 0:
            self.tier = "tier1"
        elif self.score < 0.65:
            self.tier = "tier1"
        elif self.score < 0.85:
            self.tier = "tier2"
        else:
            self.tier = "tier3"


@dataclass
class TierSummary:
    """Summary statistics for a tier."""
    tier_name: str
    count: int = 0
    scores: List[float] = field(default_factory=list)

    def mean_score(self) -> float:
        if not self.scores:
            return 0.0
        return statistics.mean(self.scores)

    def add_score(self, score: float):
        self.count += 1
        self.scores.append(score)


def score_extraction(file_path: Path) -> ExtractionScore:
    """
    Score a single extraction file.

    Returns an ExtractionScore object with score in [0.0, 1.0].
    """
    base_score = 1.0
    score_obj = ExtractionScore(
        file_path=str(file_path),
        doi="unknown",
        n_findings=0,
        score=base_score
    )

    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except Exception as e:
        score_obj.issues.append(f"Failed to parse JSON: {str(e)[:50]}")
        score_obj.score = 0.0
        return score_obj

    # Skip non-extraction files (batch logs, query logs, etc.)
    if not isinstance(data, dict):
        return score_obj

    # Extract metadata
    score_obj.doi = data.get("doi", "unknown")
    findings = data.get("findings", [])
    score_obj.n_findings = len(findings)

    # Rule 1: n_findings == 0 → automatic Tier 1
    if score_obj.n_findings == 0:
        score_obj.add_penalty(
            "empty_findings",
            base_score,  # Entire score penalty
            "No findings extracted"
        )
        score_obj.determine_tier()
        return score_obj

    # Check each finding
    has_theory_links = False

    for idx, finding in enumerate(findings):
        if not isinstance(finding, dict):
            continue

        antecedent = finding.get("antecedent", "")
        direction = finding.get("direction", "")
        sample_size = finding.get("sample_size")
        finding_type = finding.get("type", "").lower()
        theory_links = finding.get("theory_links", [])

        if theory_links:
            has_theory_links = True

        # Antecedent: null or very vague
        if not antecedent or antecedent is None:
            if idx == 0:  # Only penalize once per extraction
                score_obj.add_penalty(
                    "null_antecedent",
                    0.20,
                    "Antecedent is null or empty"
                )
        elif len(antecedent.strip()) < 10:
            if idx == 0:  # Penalize once for the whole extraction
                score_obj.add_penalty(
                    "short_antecedent",
                    0.10,
                    f"Very short antecedent: '{antecedent}'"
                )

        # Detect vague patterns (simple heuristic)
        vague_patterns = ["the environment", "the condition", "the setting", "this situation"]
        if any(p in antecedent.lower() for p in vague_patterns):
            if idx == 0:  # Penalize once
                score_obj.add_penalty(
                    "vague_antecedent",
                    0.20,
                    f"Antecedent contains vague language: '{antecedent[:50]}...'"
                )
            break  # Don't penalize again

        # Direction: non-canonical
        canonical_directions = {"increase", "decrease", "no_effect", "mixed"}
        if direction and direction.lower().strip() not in canonical_directions:
            if idx == 0:
                score_obj.add_penalty(
                    "bad_direction",
                    0.15,
                    f"Non-canonical direction: '{direction}'"
                )
            break

        # Sample size: missing for empirical findings
        if "empirical" in finding_type or "experiment" in finding_type:
            if sample_size is None or (isinstance(sample_size, (int, float)) and sample_size <= 0):
                if idx == 0:
                    score_obj.add_penalty(
                        "missing_sample_size",
                        0.10,
                        "Empirical finding missing sample_size"
                    )
                break

    # Rule: no theory_links at all
    if not has_theory_links:
        score_obj.add_penalty(
            "no_theory_links",
            0.05,
            "No theory_links in any finding"
        )

    # Clamp score to [0.0, 1.0]
    score_obj.score = max(0.0, min(1.0, score_obj.score))
    score_obj.determine_tier()

    return score_obj


def score_all_extractions(extractions_dir: Path) -> List[ExtractionScore]:
    """Score all extraction files."""
    json_files = sorted(extractions_dir.glob("*.json"))
    scores = []

    # Filter out batch/log files
    skip_files = {"batch_20260223_1501.json", "batch_20260223_1506.json", "batch_20260223_1657.json", "scholar_query_log.json"}

    print(f"Scoring extraction files (skipping {len(skip_files)} non-extraction files)...")

    for i, json_file in enumerate(json_files):
        if json_file.name.startswith(".") or json_file.name == "quarantine" or json_file.name in skip_files:
            continue

        score = score_extraction(json_file)
        scores.append(score)

        if (i + 1) % 100 == 0:
            print(f"  Scored {i + 1} files...")

    return scores


def main():
    """Main: score, sort, and output tier files."""
    extractions_dir = PROJECT_ROOT / "data" / "extractions"
    field_discovery_dir = PROJECT_ROOT / "data" / "field_discovery"
    field_discovery_dir.mkdir(parents=True, exist_ok=True)

    if not extractions_dir.exists():
        print(f"Error: {extractions_dir} does not exist")
        sys.exit(1)

    # Score all
    scores = score_all_extractions(extractions_dir)

    # Sort by score
    scores.sort(key=lambda s: s.score)

    # Partition into tiers
    tier1 = [s for s in scores if s.tier == "tier1"]
    tier2 = [s for s in scores if s.tier == "tier2"]
    tier3 = [s for s in scores if s.tier == "tier3"]

    # Write output files
    tier1_out = field_discovery_dir / "tier1_reextract.json"
    tier2_out = field_discovery_dir / "tier2_surgical.json"
    tier3_out = field_discovery_dir / "tier3_ok.json"

    with open(tier1_out, "w") as f:
        json.dump([
            {
                "doi": s.doi,
                "file": Path(s.file_path).name,
                "score": round(s.score, 4),
                "n_findings": s.n_findings,
                "issues": s.issues
            }
            for s in tier1
        ], f, indent=2)

    with open(tier2_out, "w") as f:
        json.dump([
            {
                "doi": s.doi,
                "file": Path(s.file_path).name,
                "score": round(s.score, 4),
                "n_findings": s.n_findings,
                "issues": s.issues
            }
            for s in tier2
        ], f, indent=2)

    with open(tier3_out, "w") as f:
        json.dump([
            {
                "doi": s.doi,
                "file": Path(s.file_path).name,
                "score": round(s.score, 4),
                "n_findings": s.n_findings,
                "issues": s.issues
            }
            for s in tier3
        ], f, indent=2)

    # Print summary
    print("\n" + "=" * 70)
    print("EXTRACTION SCORING REPORT")
    print("=" * 70)
    print(f"Total articles scored:         {len(scores)}")
    print(f"\nTier Distribution:")
    print(f"  Tier 1 (< 0.65, need re-extraction):    {len(tier1):4d} articles ({100*len(tier1)/len(scores):5.1f}%)")
    print(f"  Tier 2 (0.65-0.85, surgical fixes):     {len(tier2):4d} articles ({100*len(tier2)/len(scores):5.1f}%)")
    print(f"  Tier 3 (> 0.85, add new fields):        {len(tier3):4d} articles ({100*len(tier3)/len(scores):5.1f}%)")

    print(f"\nScore Statistics:")
    all_scores = [s.score for s in scores]
    print(f"  Mean score:                  {statistics.mean(all_scores):6.4f}")
    print(f"  Median score:                {statistics.median(all_scores):6.4f}")
    print(f"  Std dev:                     {statistics.stdev(all_scores) if len(all_scores) > 1 else 0:6.4f}")

    print(f"\nMean Score by Tier:")
    for tier, items in [("Tier 1", tier1), ("Tier 2", tier2), ("Tier 3", tier3)]:
        if items:
            tier_scores = [s.score for s in items]
            print(f"  {tier}: {statistics.mean(tier_scores):6.4f}")

    # Top issues
    issue_counts = {}
    for score in scores:
        for issue in score.issues:
            # Extract issue type from issue string
            issue_type = issue.split(":")[0]
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1

    if issue_counts:
        print(f"\nTop Issues Across All Articles:")
        for issue_type, count in sorted(issue_counts.items(), key=lambda x: -x[1])[:10]:
            print(f"  {issue_type}: {count:4d} articles")

    print(f"\nOutput Files:")
    print(f"  - {tier1_out} ({len(tier1)} articles)")
    print(f"  - {tier2_out} ({len(tier2)} articles)")
    print(f"  - {tier3_out} ({len(tier3)} articles)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
