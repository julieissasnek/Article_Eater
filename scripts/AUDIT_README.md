# T1.5 Audit Script

**Location**: `scripts/audit_t1_5.py`  
**Date Created**: 2026-02-23  
**Status**: Production-ready  
**Language**: Python 3

---

## Overview

The T1.5 audit script performs comprehensive validation and normalization of all template theory registries. It separates:

1. **FORMAL theories** — Canonically reduced T1.5 theories with documented reduction pathways
2. **PLAUSIBLE_CANDIDATES** — Real, peer-reviewed theories not yet formally reduced
3. **FABRICATED labels** — Ad-hoc or invalid theory names to be discarded

---

## Quick Start

```bash
cd /sessions/practical-zen-darwin/mnt/REPOS/Article_Eater_PostQuinean_v1

# Run the audit (with dry-run prompt)
python3 scripts/audit_t1_5.py
```

You will see:
1. Dry-run report of what changes would be made
2. Prompt: "Do you want to APPLY these changes? (y/n)"
3. If yes: Templates are modified in-place
4. Verification report of post-audit state

---

## How It Works

### Phase 1: Dry-Run

The script scans all templates in `data/templates/` and:

- Identifies which are calibrated
- Extracts `t1_5_parent_theories` for each
- Classifies each theory as FORMAL, CANDIDATE, or FABRICATED
- Reports what would be changed (no modifications yet)

### Phase 2: Apply (Optional)

If you enter `y` at the prompt:

- Modifies each calibrated template to have:
  - `t1_5_parent_theories`: Only canonical formal theories (strings)
  - `t1_5_candidates`: Only plausible candidate theories (new field)
  - Removes all fabricated labels
  - Normalizes all names to canonical form

### Phase 3: Verification

Reports post-audit statistics to confirm changes succeeded.

---

## Data Structures

### FORMAL_T1_5 Dictionary

```python
FORMAL_T1_5 = {
    "ART": ["Attention_Restoration_Theory", "ART", "Attention_Restoration"],
    "SRT": ["Stress_Reduction_Theory", "SRT", "Stress_Recovery_Theory", ...],
    # ... 12 formal theories with aliases
}
```

- **Key**: Canonical name (normalized form)
- **Value**: List of accepted aliases (case-insensitive)

When a template theory is classified as FORMAL, it's normalized to the canonical key.

### PLAUSIBLE_CANDIDATES Set

```python
PLAUSIBLE_CANDIDATES = {
    "Free_Energy_Minimization",
    "BRECVEMA",
    "Predictive_Coding_Vision",
    # ... 56 total candidates
}
```

Real theories not formally reduced. If a template uses one, it's moved to `t1_5_candidates`.

---

## Output Format

### Dry-Run Report

```
DRY RUN SUMMARY:
  Calibrated templates: 103
  With formal T1.5: 19
  With candidates to move: 75
  With fabricated labels to discard: 40

FORMAL T1.5 THEORIES (retained):
  Adaptive_Thermal_Comfort: 5 templates
  SRT: 4 templates
  ...

PLAUSIBLE CANDIDATES (to be moved to t1_5_candidates):
  Free_Energy_Minimization: 9 templates
  BRECVEMA: 8 templates
  ...

FABRICATED LABELS (to be discarded):
  Neuromodulatory_Architecture: 10 occurrences
  Allostasis_Theory: 3 occurrences
  ...
```

### Templates After Audit

```json
{
  "template_id": "EXAMPLE_001",
  "t1_5_parent_theories": ["ART", "Biophilia"],
  "t1_5_candidates": ["Flow_Theory", "Embodied_Cognition"]
}
```

---

## Common Scenarios

### Adding a New Formal Theory

If you formally reduce a new theory (e.g., "Dynamic_Attending_Theory"):

1. Add to `FORMAL_T1_5` in the script:

```python
FORMAL_T1_5 = {
    # ... existing theories
    "Dynamic_Attending": ["Dynamic_Attending_Theory", "Dynamic_Attending"],
}
```

2. Re-run the audit:

```bash
python3 scripts/audit_t1_5.py
# Then press 'y' to apply
```

3. Any templates that used "Dynamic_Attending_Theory" will be promoted from candidates to formal.

### Fixing a Fabrication

If you identify a fabricated label that should be moved to candidates:

1. Remove from templates (the audit already did this)
2. Add to `PLAUSIBLE_CANDIDATES` if it's a real theory
3. Re-run audit to categorize correctly

### Auditing Only Changes

To see what changed without modifying anything:

```bash
python3 scripts/audit_t1_5.py
# Type 'n' when prompted to apply
```

---

## Theory Classification Logic

The script uses this classification order:

```
Input: Theory name (string)
  ↓
Is it an alias in FORMAL_T1_5? (case-insensitive)
  YES → Classify as FORMAL, return canonical name
  NO  ↓
Is it in PLAUSIBLE_CANDIDATES? (exact or case-insensitive)
  YES → Classify as CANDIDATE, return the theory name
  NO  ↓
Classify as FABRICATED, return the theory name
```

---

## Handling Mixed Data Structures

The audit handles templates with different formats:

```python
# Format 1: Simple string (preferred post-audit)
"t1_5_parent_theories": ["ART", "Biophilia"]

# Format 2: Dict with metadata (normalized away)
"t1_5_parent_theories": [
  {
    "name": "Space Syntax",
    "reduction_pathway": "..."
  }
]
```

Both formats are converted to Format 1 (strings only).

---

## Verification Command

To manually verify post-audit state:

```bash
python3 -c "
import json, glob, collections
ts = glob.glob('data/templates/*.json')
formal = collections.Counter()
candidates = collections.Counter()
empty = 0
for t in ts:
    d = json.load(open(t))
    cal = d.get('calibration_status','') == 'calibrated' or d.get('calibrated', False)
    if not cal: continue
    f = d.get('t1_5_parent_theories', [])
    c = d.get('t1_5_candidates', [])
    if not f: empty += 1
    formal.update(f)
    candidates.update(c)
print(f'Calibrated with formal T1.5: {103 - empty}/{103}')
print(f'Formal theories used:')
for k,v in formal.most_common(): print(f'  {k}: {v}')
"
```

---

## Files

| File | Purpose |
|------|---------|
| `scripts/audit_t1_5.py` | Main audit script |
| `docs/AUDIT_T1_5_COMPLETION_2026-02-23.md` | Detailed completion report |
| `T1_5_AUDIT_SUMMARY.txt` | Quick reference summary |
| `scripts/AUDIT_README.md` | This file |

---

## API Reference

### Main Function

```python
main()
```

Orchestrates the entire audit:
1. Loads canonical registries
2. Finds all templates
3. Runs dry-run phase
4. Prompts for apply confirmation
5. Optionally applies changes
6. Reports verification results

### Key Functions

#### `build_alias_map() -> Dict[str, str]`

Builds case-insensitive mapping from aliases to canonical names.

```python
alias_map = build_alias_map()
# {"art": "ART", "attention_restoration": "ART", ...}
```

#### `classify_theory(theory_name: str, alias_map: Dict) -> Tuple[str, str]`

Classifies a single theory name.

```python
category, canonical = classify_theory("attention restoration", alias_map)
# Returns: ("FORMAL", "ART")
```

Returns:
- `("FORMAL", canonical_name)` if matched to formal theory
- `("CANDIDATE", theory_name)` if matched to plausible candidate
- `("FABRICATED", theory_name)` if no match

#### `audit_template_dry_run(path: str, alias_map: Dict) -> Dict`

Dry-run audit on a single template. Returns dict with:
- `is_calibrated`: bool
- `formal_theories`: List[str]
- `candidates_moved`: List[str]
- `fabricated_discarded`: List[str]
- `actions`: List[str]

#### `apply_audit_to_template(path: str, alias_map: Dict) -> bool`

Applies audit to a single template. Returns True if modified.

---

## Performance

- **Scan time**: ~1 second (208 templates)
- **Dry-run time**: ~2 seconds (103 calibrated templates)
- **Apply time**: ~3 seconds (97 modified templates)
- **Total run time**: ~5 seconds

---

## Future Enhancements

1. **Selective apply** — Apply changes only to specific theory/status
2. **Diff mode** — Show before/after JSON diffs
3. **Integration with TASKS.md** — Auto-track reduction tasks
4. **Panel review mode** — Export for expert review before apply
5. **Migration tracking** — Log how theories moved between categories

---

## Support

For questions or issues:

1. Review `docs/AUDIT_T1_5_COMPLETION_2026-02-23.md` for audit findings
2. Check `T1_5_AUDIT_SUMMARY.txt` for quick reference
3. Re-run script in dry-run mode to see current state
4. Update `FORMAL_T1_5` or `PLAUSIBLE_CANDIDATES` as needed

---

**Last Updated**: 2026-02-23  
**Version**: 1.0  
**Maintainer**: T1.5 Audit System
