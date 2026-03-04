#!/usr/bin/env python3
"""
Layer 3 Adversarial Audit Runner
=================================

This script structures and templates the Layer 3 (weekly, LLM-based) adversarial audit.

The adversarial audit uses an external LLM to:
1. Review system architecture for hidden assumptions
2. Identify edge cases Layer 1/2 tests may miss
3. Propose failure scenarios
4. Evaluate resilience under adversarial input

This is a scaffolding script that:
- Runs existing tests first (to establish baseline)
- Generates the audit template (saved to docs/)
- Formats prompts for LLM submission
- Records results for future panel review

The actual LLM invocation is stubbed and left for explicit user permission.

Usage:
    python scripts/run_adversarial_audit.py [--run-tests] [--output-dir OUTDIR]

Output:
    - docs/adversarial_audit_template.md (prompt for LLM)
    - docs/nightly_reports/{timestamp}_baseline_tests.json (Layer 1/2 baseline)

Author: CW (Claude Code)
Date: 2026-03-03
"""

import json
import os
import sys
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


# ============================================================================
# LAYER 3 AUDIT PROMPT TEMPLATE
# ============================================================================

ADVERSARIAL_AUDIT_PROMPT = """
# Layer 3 Adversarial Audit Prompt

You are conducting a weekly LLM-based adversarial audit of the ATLAS system
(Article-to-Theoretical-Landscape-Analysis System).

Your role:
- Attack the system architecture
- Expose hidden assumptions
- Find edge cases
- Propose failure modes Layer 1/2 tests miss

## Context

### System Overview
The ATLAS system extracts evidence-backed scientific rules from articles using
a Quinean coherentist epistemology. Key components:

1. **Extraction Pipeline** (Layer 0)
   - Ingests peer-reviewed articles (PDF)
   - Extracts findings, study designs, evidence levels
   - Tags: population, intervention, outcome, causal tier

2. **Paper Integration Orchestrator** (13-step pipeline)
   - Credence computation (warrant-derived ω formula)
   - Belief supersession (newer evidence replaces older)
   - Entrenchment scoring (contribution to coherence)
   - Web-of-Belief integration (Haack foundherentism)

3. **Answer Enrichment Orchestrator** (9 services)
   - Credence confidence intervals
   - Warrant trace (belief justification)
   - Confounder risk assessment
   - Framework voices (5 T1 frameworks comment)
   - Gap analysis (what's unknown)
   - Follow-up questions
   - Language adaptation
   - Figure suggestions
   - Interpretation context

4. **QA Infrastructure**
   - Layer 1: Success condition tests (deterministic, every commit)
   - Layer 2: Systemic failure tests (nightly overseer)
   - Layer 3: Adversarial audit (weekly LLM, this script)

### Baseline Test Results
See accompanying JSON report for Layer 1/2 baseline.
(Tests marked @pytest.mark.layer1_success and @pytest.mark.layer2_nightly)

## Audit Instructions

### Part A: Architecture Threats (45 min)

Review each component below. For each, identify:
1. Hidden assumption (what does this code assume about inputs/world?)
2. Edge case (what breaks the assumption?)
3. Severity (LOW/MEDIUM/HIGH)
4. Example (concrete failing scenario)

#### A1. Credence Computation (warrant-based ω)

Current formula:
```
ω = ω_base × ω_conf × ω_rep × ω_meta

where:
  ω_base = warrant strength from evidence (0.55–0.99)
  ω_conf = confidence in methodology (0.5–1.0)
  ω_rep = replication credibility (0.4–1.0)
  ω_meta = meta-analytic harmonization (0.7–1.0)
```

Hidden assumptions:
- Independence: Four factors assumed independent (are they?)
- Multiplicative composition: Why multiply not add?
- Bounds: Why these specific ranges?
- Canonicity: Are 0.55, 0.99 empirically grounded or stipulated?

#### A2. Belief Supersession (Temporal Dynamics)

Current rule:
- Newer study replaces older for same (population, intervention, outcome)
- Entrenchment only boosts if replacement has higher credence
- Entrenchment score = coherence delta × time_factor

Hidden assumptions:
- Recency = better (contradicts historical precedent literature)
- No citation lag (new study is immediately known)
- Coherence is monotonic (adding a belief never decreases coherence)
- Population equivalence is transitive

#### A3. Web-of-Belief Coherence (Foundherentism)

Current implementation:
- Quantifies coherence via agreement/conflict ratios
- Tension detected when |agreement - conflict| < threshold
- Minimizes tension through selective entrenchment

Hidden assumptions:
- Coherence is a linear scalar (not multi-dimensional)
- Agreement/conflict is binary (not graded)
- Entrenchment is reversible (beliefs can lose support)
- No incommensurable frameworks (all beliefs on same scale)

#### A4. Extraction Quality Gate

Current validator:
- Blocks findings below 0.75 overall quality score
- Validates 8 principle-compliance fields
- 6 hard gates must pass (causal tier, scope, justification, etc.)

Hidden assumptions:
- 0.75 threshold is universal (same for all article types?)
- All 8 principles equally weighted
- Gate failures are recoverable
- Failed findings can be re-extracted

#### A5. Grounding Gate (Gating Function)

Current behavior:
- Checks empirical anchor (≥2 supporting findings)
- Checks coherence status (tension < 0.3)
- Checks confidence (mean ω > 0.55)
- Abstains if ANY check fails

Hidden assumptions:
- 2 findings is "sufficient" empirical grounding
- Tension threshold (0.3) is universal
- Confidence threshold (0.55) applies to all answer types
- Abstention is always safe (no cost to user)

### Part B: Edge Cases (30 min)

Test these scenarios. Each should either PASS gracefully or FAIL with
a clear, actionable error message.

#### B1. Pathological Inputs

1. **Empty article**: 0 findings, 0 claims
2. **Single-evidence circle**: A cites B, B cites A
3. **Contradictory frameworks**: T1 framework says X, another says ¬X
4. **Extreme credence**: ω = 0.01 or 0.99
5. **Massive article**: 10,000 findings, 100,000 claims
6. **Null/missing fields**: Optional fields genuinely absent in DB

#### B2. Temporal Anomalies

1. **Future-dated article**: Published date > now
2. **Supersession chain**: A supersedes B supersedes C (15 chains)
3. **Retroactive entrenchment**: Re-entrench old belief after new finding
4. **Time-reversal**: Two studies same date, unclear ordering

#### B3. Semantic Ambiguity

1. **Homonym outcome**: "stress" (psychological vs. mechanical)
2. **Scope creep**: Finding says "humans 18-65" but is applied to "adults"
3. **Mechanism inversion**: Study claims effect is mediated by X, but data shows ¬X
4. **Definition shift**: Article redefines key term mid-text

#### B4. Configuration Faults

1. **Disabled grounding gate**: System runs with gate.check() = no-op
2. **Missing frameworks**: Only 3 of 5 T1 frameworks available
3. **Corrupted theory JSON**: Theory file is valid JSON but missing required field
4. **Budget exhaustion**: All 9 enrichment services timeout

#### B5. Consistency Failures

1. **Stale cache**: Cached belief exists but DB version is newer
2. **Schema version mismatch**: Old belief saved in v1 format, code expects v2
3. **Orphaned claim**: Claim references a finding that was deleted
4. **Cyclic dependency**: Belief A entrench depends on belief B, B on A

### Part C: Resilience Assessment (15 min)

Rate the system on these dimensions:

| Dimension | Scale | Questions |
|-----------|-------|-----------|
| Graceful Degradation | 0-10 | When something fails, do users get partial results + warnings or total blackout? |
| Observability | 0-10 | Can operators see what's failing and why? Warnings vs. silent failures? |
| Recoverability | 0-10 | Can the system recover from failures without human intervention? |
| Testability | 0-10 | Can Layer 1/2 tests access the internal state needed to validate invariants? |
| Assumption Clarity | 0-10 | Are all implicit assumptions documented and justified? |

## Report Structure

Your response should follow this template:

```markdown
# Adversarial Audit Report — [TIMESTAMP]

## Part A Findings: Architecture Threats

### A1. Credence Computation
**Hidden Assumptions**: [list]
**Edge Cases**: [scenarios that break assumptions]
**Severity**: [LOW/MEDIUM/HIGH]
**Recommendation**: [what to fix]

[repeat for A2-A5]

## Part B Findings: Edge Case Testing

### B1 Pathological Inputs
- [Scenario]: [Expected vs. Actual]
- [Scenario]: [Expected vs. Actual]

[repeat for B2-B5]

## Part C: Resilience Scores

| Dimension | Score | Justification |
|-----------|-------|---|

## Summary

**Overall Grade**: [A/B/C/D/F]
**Critical Findings**: [count]
**Recommended Actions (Prioritized)**:
1. [Action]
2. [Action]

**Panel Review Questions** (for expert deliberation):
- [Question for architects]
- [Question for epistemologists]
- [Question for methodologists]
```

---

**Your Task**:
Conduct this audit based on:
1. System documentation: docs/master_doc_parts/
2. Code review: src/services/
3. Test results: {baseline_json}
4. Architecture diagram: docs/ARCHITECTURE.md

You may reference external literature (Pollock, Haack, Cartwright, Pearl, Mayo, etc.)
as appropriate. Be specific and actionable.

Estimated time: 90 minutes
Output format: Markdown (suitable for GitHub issue + expert panel)
"""


def run_layer1_layer2_baseline(verbose: bool = False) -> Dict[str, Any]:
    """
    Run all Layer 1 and Layer 2 tests to establish baseline.

    Returns:
        Dictionary with test results
    """
    print("Running Layer 1/2 baseline tests...")

    results = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'layer1': {'passed': 0, 'failed': 0, 'skipped': 0, 'errors': 0},
        'layer2': {'passed': 0, 'failed': 0, 'skipped': 0, 'errors': 0},
    }

    # Run Layer 1 tests
    cmd_l1 = [
        'pytest',
        'tests',
        '-m', 'layer1_success',
        '-v' if verbose else '-q',
        '--tb=short',
    ]

    try:
        result_l1 = subprocess.run(
            cmd_l1,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True,
            text=True,
            timeout=300
        )
        # Parse output (simple approach: count "passed" in output)
        output_l1 = result_l1.stdout + result_l1.stderr
        if 'passed' in output_l1:
            # Extract counts from pytest summary line
            import re
            match = re.search(r'(\d+) passed', output_l1)
            if match:
                results['layer1']['passed'] = int(match.group(1))
            match = re.search(r'(\d+) failed', output_l1)
            if match:
                results['layer1']['failed'] = int(match.group(1))
            match = re.search(r'(\d+) skipped', output_l1)
            if match:
                results['layer1']['skipped'] = int(match.group(1))
    except Exception as e:
        print(f"Warning: Layer 1 test run failed: {e}", file=sys.stderr)

    # Run Layer 2 tests
    cmd_l2 = [
        'pytest',
        'tests',
        '-m', 'layer2_nightly',
        '-v' if verbose else '-q',
        '--tb=short',
    ]

    try:
        result_l2 = subprocess.run(
            cmd_l2,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True,
            text=True,
            timeout=300
        )
        output_l2 = result_l2.stdout + result_l2.stderr
        if 'passed' in output_l2:
            import re
            match = re.search(r'(\d+) passed', output_l2)
            if match:
                results['layer2']['passed'] = int(match.group(1))
            match = re.search(r'(\d+) failed', output_l2)
            if match:
                results['layer2']['failed'] = int(match.group(1))
            match = re.search(r'(\d+) skipped', output_l2)
            if match:
                results['layer2']['skipped'] = int(match.group(1))
    except Exception as e:
        print(f"Warning: Layer 2 test run failed: {e}", file=sys.stderr)

    return results


def generate_audit_template(baseline: Dict[str, Any]) -> str:
    """
    Generate the adversarial audit template with baseline context.

    Args:
        baseline: Layer 1/2 baseline test results

    Returns:
        Markdown string with audit prompt
    """
    baseline_json = json.dumps(baseline, indent=2)

    # Insert baseline into prompt
    template = ADVERSARIAL_AUDIT_PROMPT.format(baseline_json=baseline_json)

    return template


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Run Layer 3 adversarial audit')
    parser.add_argument('--run-tests', action='store_true',
                        help='Run Layer 1/2 baseline tests before generating template')
    parser.add_argument('--output-dir', default='docs',
                        help='Directory for template output')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose pytest output')
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Layer 3 Adversarial Audit Runner")
    print("=" * 60)

    # Run baseline if requested
    if args.run_tests:
        baseline = run_layer1_layer2_baseline(verbose=args.verbose)
    else:
        # Create minimal baseline
        baseline = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'layer1': {'passed': 0, 'failed': 0, 'skipped': 0, 'errors': 0},
            'layer2': {'passed': 0, 'failed': 0, 'skipped': 0, 'errors': 0},
            'note': 'Baseline not run. Use --run-tests to collect Layer 1/2 baseline.',
        }

    # Save baseline JSON
    timestamp_short = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    baseline_file = output_dir / 'nightly_reports' / f'{timestamp_short}_baseline_tests.json'
    baseline_file.parent.mkdir(parents=True, exist_ok=True)

    with open(baseline_file, 'w') as f:
        json.dump(baseline, f, indent=2)
    print(f"Wrote baseline: {baseline_file}")

    # Generate audit template
    print("Generating adversarial audit template...")
    template = generate_audit_template(baseline)

    # Save template
    template_file = output_dir / 'adversarial_audit_template.md'
    with open(template_file, 'w') as f:
        f.write(template)
    print(f"Wrote template: {template_file}")

    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print(f"""
1. Review the audit template: {template_file}

2. Submit to LLM (e.g., Claude Opus):
   - Copy full prompt from {template_file}
   - Send to your LLM of choice
   - Request response in markdown format

3. Save LLM response as: docs/layer3_audit_reports/{timestamp_short}_audit_response.md

4. Convene expert panel to review:
   - Architecture threats (Part A)
   - Edge case findings (Part B)
   - Resilience scores (Part C)
   - Panel review questions

5. Create GitHub issues for recommended actions

Example command to submit to Claude:
    cat {template_file} | xclip  # Copy to clipboard
    # Then paste into Claude or use API

Note: This script only TEMPLATES the audit. The actual LLM invocation
requires explicit user permission (to avoid automated API calls that
consume tokens/cost money).
""")

    return 0


if __name__ == '__main__':
    sys.exit(main())
