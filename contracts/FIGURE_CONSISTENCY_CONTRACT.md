# Figure-Document Consistency Contract

*Created: 2026-03-02*
*Status: ACTIVE — applies to all figures in docs/FIGURE_INDEX.md*

## The Problem

Figures encode specific claims, numbers, and structural relationships from the text at a particular moment. When the master doc evolves — new panels, revised credences, updated parameters, restructured sections — figures silently become stale. A figure showing "3,420 beliefs" remains unchanged when the count reaches 4,000. A diagram showing three layers persists after a fourth is introduced. This staleness is invisible until a reader notices a contradiction.

## The Solution: Dependency Declarations

Every figure generation script must declare its **data dependencies** — the specific textual claims, numbers, and structural assumptions it encodes. When any dependency changes, the figure is flagged for regeneration.

### Dependency Types

| Type | Description | Example | How to detect change |
|------|-------------|---------|---------------------|
| **COUNT** | A specific number from the text | "3,420 beliefs" | grep for the number in source section |
| **STRUCTURE** | Architectural arrangement | "Three layers: EN → π → BN" | Section heading or structural description change |
| **PARAMETER** | A calibrated value or range | "D ≈ 1.3 optimal" | Parameter table or calibrated value change |
| **TAXONOMY** | A classification or typology | "12 domain panels" | Addition/removal/renaming of categories |
| **RELATIONSHIP** | A causal or logical connection | "EN feeds π feeds BN" | Change in described data flow or dependency |
| **FORMULA** | A mathematical expression | "logit(p_target) = d·ω·δ·logit(p_lab)" | Any term added/removed/redefined |

### Dependency Declaration Format

Each figure script must include a `FIGURE_DEPENDENCIES` dictionary:

```python
FIGURE_DEPENDENCIES = {
    "m1_three_layer_architecture": {
        "title": "Three Computational Layers Inside a Superordinate Interpretive Envelope",
        "source_sections": ["§1", "§48A", "§79-83"],
        "source_parts": ["PART_I_EXPLANATION_GAP.md", "PART_IV_CREDENCE.md", "PART_VIII_IE_DPT.md"],
        "dependencies": [
            {"type": "STRUCTURE", "claim": "Three computational layers: EN, π, BN", "grep_pattern": "three.layer|EN.*π.*BN|epistemic.network.*projection.*bayesian"},
            {"type": "STRUCTURE", "claim": "IE-DPT as superordinate envelope", "grep_pattern": "superordinate|interpretive.envelope|IE-DPT"},
            {"type": "TAXONOMY", "claim": "Kirsh × Kahneman 2×2 matrix (4 cells)", "grep_pattern": "Kirsh.*Kahneman|four.*cell|4.*architectural.*cell"},
            {"type": "FORMULA", "claim": "logit(p_target) = d·ω·δ·logit(p_lab)", "grep_pattern": "logit.*p_target.*d.*omega|logit.*p_target.*d.*ω"},
            {"type": "COUNT", "claim": "3,420+ beliefs in EN", "grep_pattern": "3,4[0-9]{2}.*belief|3420.*belief"},
            {"type": "RELATIONSHIP", "claim": "Feedback loop from BN back to EN", "grep_pattern": "feedback.*BN.*EN|coherence.*signal.*feed.*back"},
        ],
        "last_verified": "2026-03-02",
        "generated_from_script": "scripts/generate_master_doc_figures.py",
    },
    # ... one entry per figure
}
```

## Consistency Checking Protocol

### When to Check

1. **After any master doc edit** — run the consistency checker
2. **Before any figure regeneration** — verify dependencies still hold
3. **At session start** — quick scan for stale figures
4. **Before any paper submission** — full audit

### The Checker Script

`scripts/check_figure_consistency.py` performs the following:

1. **Load all FIGURE_DEPENDENCIES** from all generator scripts
2. **For each dependency**, grep the source Part files for the claim
3. **Flag mismatches**:
   - COUNT changed (number differs)
   - STRUCTURE missing (grep pattern not found)
   - PARAMETER changed (value differs)
   - TAXONOMY changed (category added/removed)
4. **Output a staleness report** with severity levels:
   - **STALE-CRITICAL**: A number or formula in the figure contradicts the text
   - **STALE-MINOR**: A label or description has drifted but the figure is still approximately correct
   - **CURRENT**: Dependency verified, no change detected
5. **Update `last_verified` timestamps** for passing dependencies

### Staleness Severity Levels

| Level | Meaning | Action Required |
|-------|---------|-----------------|
| CURRENT | All dependencies verified | None |
| STALE-MINOR | Label, caption, or non-quantitative detail has drifted | Regenerate when convenient |
| STALE-CRITICAL | A number, formula, or structural claim contradicts the text | Regenerate immediately |
| STALE-STRUCTURAL | The figure's fundamental architecture no longer matches the text | Redesign the figure |

## Integration with TASKS.md

When the consistency checker finds stale figures, it should:
1. Add a task to TASKS.md: "Regenerate M-X: [reason for staleness]"
2. Note the dependency that triggered the flag
3. Estimate effort (regenerate = low, redesign = high)

## Integration with Session Start

Add to CLAUDE.md session-start protocol:
```
After reading TASKS.md, run: python scripts/check_figure_consistency.py --quick
If any STALE-CRITICAL figures are found, prioritize regeneration.
```

## The FIGURE_DEPENDENCIES Master File

Rather than scattering dependencies across individual scripts, maintain a single source of truth:

**`contracts/FIGURE_DEPENDENCIES.json`**

This JSON file contains all dependency declarations for all figures. The consistency checker reads this file. Generator scripts reference it. The advantage: when a section moves or is renumbered, you update one file rather than hunting through six scripts.

## Success Conditions

This contract succeeds when the following conditions are met:

### SC-1: Zero STALE-CRITICAL at Any Commit
No figure may be committed to the repository while flagged STALE-CRITICAL. The quick check (`--quick`) must pass with exit code 0 before any commit touching Part files. **Verification**: `python scripts/check_figure_consistency.py --quick` returns exit code 0.

### SC-2: Full Audit Pass Weekly
A full audit (`--full`) should return at most 2 STALE-MINOR figures at any given time. If more than 2 accumulate, regeneration becomes the next session's first priority. **Verification**: `python scripts/check_figure_consistency.py --full` returns exit code 0 or exit code 1 with ≤2 STALE-MINOR.

### SC-3: Every Figure Has ≥3 Declared Dependencies
No figure may exist in FIGURE_DEPENDENCIES.json with fewer than 3 dependencies. Figures with fewer than 3 are under-specified and likely to drift undetected. **Verification**: `jq '.figures | to_entries[] | select((.value.dependencies | length) < 3) | .key' contracts/FIGURE_DEPENDENCIES.json` returns empty.

### SC-4: Every Dependency Has a Grep Pattern That Matches
At the time of declaration, every dependency's grep pattern must match at least one line in its source Part files. A pattern that never matches is useless — it will always flag STALE. **Verification**: full audit with `--full -v` shows matched text for every dependency.

### SC-5: Regeneration Latency < 1 Session
When a figure is flagged stale, it must be regenerated within the same session or the immediately following one. No figure may remain STALE-CRITICAL across two sessions. **Verification**: TASKS.md shows no STALE-CRITICAL regeneration tasks older than 1 session.

### SC-6: Common-Sense Labeling
Every figure title, axis label, legend entry, and annotation uses plain English that a smart non-specialist would understand on first reading. Technical terms may appear in parentheses. **Verification**: visual review at each regeneration.

### SC-7: Caption–Figure Agreement
Every embedded caption accurately describes the figure it accompanies. When a figure is regenerated with changed content, its caption must be updated in the same edit. **Verification**: grep for `Figure M-X` in Part files after regeneration; verify caption matches new figure content.

---

## What This Contract Does NOT Cover

- **Aesthetic quality** — whether the figure is well-designed (that's the visualization norms contract)
- **Caption accuracy** — captions are embedded in Part files and tracked separately
- **Cross-figure consistency** — whether M-1 and M-3 tell the same architectural story (future extension)

## Revision History

| Date | Change | Reason |
|------|--------|--------|
| 2026-03-02 | Created | David identified figure-document drift as a structural risk |
