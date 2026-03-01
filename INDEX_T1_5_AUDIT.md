# T1.5 Audit Project Index

**Completion Date**: 2026-02-23  
**Status**: Complete and Verified  
**Scope**: All 208 templates, 103 calibrated, 97 modified

---

## Quick Navigation

### Run the Audit
```bash
cd /sessions/practical-zen-darwin/mnt/REPOS/Article_Eater_PostQuinean_v1
python3 scripts/audit_t1_5.py
```

### Read the Reports (Choose One)
- **Quick overview**: `T1_5_AUDIT_SUMMARY.txt` (5.2 KB)
- **Detailed findings**: `docs/AUDIT_T1_5_COMPLETION_2026-02-23.md` (12 KB)
- **How to use script**: `scripts/AUDIT_README.md` (7.9 KB)

---

## File Locations

| File | Purpose | Size | Type |
|------|---------|------|------|
| `scripts/audit_t1_5.py` | Main audit script | 16 KB | Python 3 |
| `docs/AUDIT_T1_5_COMPLETION_2026-02-23.md` | Complete audit report | 12 KB | Markdown |
| `T1_5_AUDIT_SUMMARY.txt` | Quick reference | 5.2 KB | Text |
| `scripts/AUDIT_README.md` | Usage guide | 7.9 KB | Markdown |
| `data/templates/*.json` | Modified templates | 97 files | JSON |

---

## What Was Done

### 1. Canonical T1.5 Registry Created
12 formally reduced theories with case-insensitive alias matching:
- Attention_Restoration_Theory (ART)
- Stress_Reduction_Theory (SRT)
- Biophilia
- Prospect_Refuge
- Privacy_Regulation
- Kaplan_Preference_Matrix
- Adaptive_Thermal_Comfort
- Space_Syntax
- Soundscape_Theory
- Place_Attachment
- Fractal_Fluency
- Awe_Kama_Muta

### 2. Plausible Candidates Registry Identified
56 real but unreduced theories:
- Free_Energy_Minimization (9 templates)
- BRECVEMA (8 templates)
- Predictive_Coding_Vision (7 templates)
- Episodic_Memory_Theory (7 templates)
- Chronobiology (6 templates)
- [... 51 more ...]

### 3. Fabricated Labels Removed
39 distinct fabricated labels with no theoretical standing:
- Neuromodulatory_Architecture (10 instances)
- Allostasis_Theory (3 instances)
- Self_Transcendence (2 instances)
- [... 36 more ...]

### 4. Templates Normalized
97 templates modified with:
- `t1_5_parent_theories`: Strings only, canonical names
- `t1_5_candidates`: New field for plausible theories
- All dict metadata removed
- All casing normalized

---

## Key Results

```
Templates Audited:        208 total
  - Calibrated:          103
  
Changes Applied:         97 templates

Formal T1.5:
  - Retained: 19 templates
  - Theories in use: 8 distinct
  - Total references: 26

Candidates:
  - Moved to new field: 75 templates
  - Distinct theories: 52

Fabrications:
  - Removed: 40 instances
  - Distinct labels: 39

Empty T1.5:
  - Templates: 84
  - Status: No formal T1.5 assigned
```

---

## Data Quality Improvements

**Before Audit**:
- Mixed string/dict entries in t1_5_parent_theories
- Inconsistent casing (ART vs art vs Attention_Restoration)
- Citation formats misplaced in data (e.g., "Space Syntax [Hillier & Hanson, 1984]")
- 40 fabricated labels mixed with valid theories
- No tracking of plausible but unreduced theories

**After Audit**:
- All entries are strings
- All names normalized to canonical form
- All citations removed from theory names
- 0 fabricated labels in formal tier
- 52 distinct candidate theories tracked in new field
- Contract maintained (empty lists explicit, not absent)

---

## How to Use This Audit

### For Development
When creating templates, consult:
1. `FORMAL_T1_5` in `scripts/audit_t1_5.py` for formal theory names
2. `PLAUSIBLE_CANDIDATES` for candidate theories
3. Run the script before committing

### For Reductions
When you formally reduce a new theory:
1. Add to `FORMAL_T1_5` dict in `scripts/audit_t1_5.py`
2. Re-run script with `python3 scripts/audit_t1_5.py` + press `y`
3. Templates using that theory are automatically promoted
4. Update the audit report in your commit message

### For Analysis
Use the candidate list to prioritize future reductions:
- Top by frequency: Free_Energy_Minimization, BRECVEMA
- Top by relevance: Predictive_Coding frameworks, Chronobiology
- See detailed report for all 52 candidates

---

## Sample Template (Post-Audit)

```json
{
  "template_id": "HC_CREATIVE_DIVERGENCE_001",
  "name": "High-Complexity Creative Divergence",
  "t1_5_parent_theories": ["ART", "Biophilia"],
  "t1_5_candidates": ["Flow_Theory", "Embodied_Cognition"],
  "... other fields ..."
}
```

### Field Meanings
- `t1_5_parent_theories`: Formally reduced theories (with reduction pathways documented)
- `t1_5_candidates`: Real theories this template might eventually reduce to
- Both fields are lists of strings (no dicts)

---

## Verification Command

Confirm post-audit state anytime:

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
print(f'Formal theories in use:')
for k,v in formal.most_common(): print(f'  {k}: {v}')
"
```

Expected output:
```
Calibrated with formal T1.5: 19/103
Formal theories in use:
  Adaptive_Thermal_Comfort: 5
  SRT: 4
  ART: 3
  ...
```

---

## Report Reading Guide

### For the Impatient (5 min read)
→ Read `T1_5_AUDIT_SUMMARY.txt`

### For Implementation Details (15 min read)
→ Read `scripts/AUDIT_README.md`

### For Complete Analysis (45 min read)
→ Read `docs/AUDIT_T1_5_COMPLETION_2026-02-23.md`

### For Usage Questions
→ Run the script in dry-run mode (press 'n' to skip apply)

---

## Next Steps

1. **Review findings** (this week)
   - Confirm formal/candidate distinctions
   - Note any theories that should move between categories

2. **Prioritize reductions** (next 2 weeks)
   - Target high-frequency candidates (Free_Energy, BRECVEMA)
   - Document reduction pathways
   - Add to FORMAL_T1_5

3. **Re-run audit** (after each reduction)
   - Templates automatically categorized
   - Report updated

4. **Panel review** (optional)
   - Use candidate list for expert discussion
   - Validate choices against epistemic frameworks

---

## Contact & Support

For questions about:
- **How to run the script**: See `scripts/AUDIT_README.md`
- **What the audit found**: See `docs/AUDIT_T1_5_COMPLETION_2026-02-23.md`
- **Quick stats**: See `T1_5_AUDIT_SUMMARY.txt`
- **Specific theory**: Search the completion report

---

## Version History

| Date | Version | Change |
|------|---------|--------|
| 2026-02-23 | 1.0 | Initial audit creation and execution |

---

**Last Updated**: 2026-02-23  
**Audited By**: T1.5 Audit Script v1.0  
**Status**: Complete & Verified
