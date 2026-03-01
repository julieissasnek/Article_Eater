# CONSOLIDATED AUDIT SOLUTION PLAN
## Cross-Auditor Findings and Remediation
## February 23, 2026

---

## AUDITOR FINDINGS SUMMARY

### Claude Code (CC) Audit — v4 Spec
| Finding | Severity | Count |
|---------|----------|-------|
| Fabricated T1.5 theory names | **HIGH** | 9 templates |
| Test failures | MEDIUM | 11 tests (99.7% pass) |
| Ceiling exceedances (unreviewed) | LOW (panel) | 68 |
| Missing `beartype` dependency | LOW | 1 |

### Antigravity (AG) Audit — v2 Superset
| Finding | Severity | Count |
|---------|----------|-------|
| Unregistered mechanism variables | **HIGH** | 272 in 48 templates |
| Hardcoded DB paths | MEDIUM | Multiple scripts |
| Ceiling violations | LOW (panel) | ~60 |

---

## CONSOLIDATED ACTION PLAN

### Priority 1: T1.5 Fabricated Names (BLOCKING)

**Problem**: 9 templates contain non-canonical T1.5 theory names that violate the formal roster.

**Affected Templates**:
| Template | Fabricated Names |
|----------|------------------|
| NM_SOCIAL_ISOLATION_ALLOSTATIC_001 | Allostasis, CTRA_Conserved_Transcriptional_Response |
| PRIVACY_GRADIENT_REGULATION_001 | Altman_Privacy_Regulation |
| PROXEMIC_PE_ARCH_001 | Amygdala_Proximity_Detection, Hall_Proxemics |
| NM_OXYTOCIN_SOCIAL_003 | Oxytocin_Social_Bonding |
| CROSS_SOCIAL_MIRROR_PRESENCE_001 | Second_Person_Neuroscience, Shared_Manifold_Hypothesis |
| CROSS_TPJ_SPATIAL_SOCIAL_BRIDGE_001 | Theory_of_Mind_Neural_Basis |

**Solution**:
```bash
# For each template, either:
# 1. Remove from t1_5_parent_theories (if not a formal theory)
# 2. Move to t1_5_candidates (if pending formal reduction)
# 3. Rename to canonical form (e.g., Altman_Privacy_Regulation → Privacy_Regulation)

# Script approach:
python3 -c "
import json
from pathlib import Path

CANONICAL_T1_5 = {
    'ART', 'SRT', 'Biophilia', 'Prospect_Refuge', 'Privacy_Regulation',
    'Kaplan_Preference_Matrix', 'Adaptive_Thermal_Comfort', 'Space_Syntax',
    'Soundscape', 'Soundscape_Theory', 'Place_Attachment', 'Fractal_Fluency',
    'Awe_Kama_Muta', 'BRECVEMA', 'Flow_Theory'
}

RENAMES = {
    'Altman_Privacy_Regulation': 'Privacy_Regulation',
}

templates_dir = Path('data/templates')
for path in templates_dir.glob('*.json'):
    t = json.loads(path.read_text())
    theories = t.get('t1_5_parent_theories', [])

    # Filter and rename
    canonical = []
    candidates = []
    for th in theories:
        if th in RENAMES:
            canonical.append(RENAMES[th])
        elif th in CANONICAL_T1_5:
            canonical.append(th)
        else:
            candidates.append(th)  # Move to candidates

    if canonical != theories:
        t['t1_5_parent_theories'] = canonical
        if candidates:
            t['t1_5_candidates'] = t.get('t1_5_candidates', []) + candidates
        path.write_text(json.dumps(t, indent=2))
        print(f'Fixed: {path.name}')
"
```

---

### Priority 2: Test Failures (11 tests)

**Problem**: 11 tests fail but 4060 pass (99.7% pass rate).

**Failing Tests by Category**:

| Category | Tests | Likely Fix |
|----------|-------|------------|
| Star tracker (3) | v22 scorecard mismatch | Update scorecard version or test expectations |
| Template record (3) | Stale queries | Update query expectations for current template state |
| Sprint verification (2) | Orphan files, direction | Clean orphan JSON files, fix direction test |
| Path contracts (1) | Hardcoded paths | Fix absolute path references |
| Sensitivity (1) | CREA2 noise | Review sensitivity threshold |

**Solution for test_star_tracker**:
```bash
# These tests reference v22 scorecard - check if scorecard exists
ls data/star_tracker_v22*.json 2>/dev/null || echo "Missing scorecard"

# If missing, may need to generate or update version reference
```

**Solution for orphan files**:
```bash
# Find and review orphan JSON files
python3 scripts/validate_templates.py 2>&1 | grep -i orphan
```

---

### Priority 3: Missing Dependencies

**Problem**: `beartype` not in requirements.txt

**Solution**:
```bash
echo "beartype>=0.22.0" >> requirements.txt
```

---

### Priority 4: Hardcoded DB Paths (AG finding)

**Problem**: Some scripts reference `data/web_persistence.db` instead of `web_persistence_v2.db`

**Note**: My CC audit found web_accumulator works (4888 beliefs loaded). This may have been fixed since the AG audit.

**Verify**:
```bash
grep -r "web_persistence\.db" src/ scripts/ --include="*.py" | grep -v "_v2"
```

---

### Priority 5: Unregistered Variables (AG finding, 272 in 48 templates)

**Note**: My CC audit found variable lint PASSES (all 1902 variables registered). This may have been fixed since the AG audit.

**Verify**:
```bash
python3 scripts/lint_variables.py
```

---

## CEILING EXCEEDANCES (NOT ACTIONABLE BY CC)

68 unreviewed ceiling exceedances require **panel review**, not automated fixes.

Per v4 epistemics:
- Ceilings are Bayesian soft priors
- Panel must decide: warrant upgrade, documented override, or confidence reduction
- Reference: `docs/CEILING_RECALIBRATION_PANEL_Feb23.md`

**Status**: Flagged for next panel session. NOT blocking.

---

## EXECUTION ORDER

1. **T1.5 Cleanup** — Fix 9 fabricated names (Priority 1)
2. **Add beartype** — Update requirements.txt (Priority 3)
3. **Test Fixes** — Address 11 failing tests (Priority 2)
4. **Verify AG Findings** — Confirm DB paths and variables are now fixed

---

## VERIFICATION COMMANDS

After fixes, run:
```bash
# Full audit verification
pytest tests/test_bridge_ceilings.py -v
pytest tests/test_canonical_variables.py -v
python3 scripts/validate_templates.py
python3 scripts/lint_variables.py

# Check T1.5 cleanup
python3 -c "
import json
from pathlib import Path

CANONICAL = {'ART','SRT','Biophilia','Prospect_Refuge','Privacy_Regulation',
'Kaplan_Preference_Matrix','Adaptive_Thermal_Comfort','Space_Syntax',
'Soundscape','Soundscape_Theory','Place_Attachment','Fractal_Fluency',
'Awe_Kama_Muta','BRECVEMA','Flow_Theory'}

bad = []
for p in Path('data/templates').glob('*.json'):
    t = json.loads(p.read_text())
    for th in t.get('t1_5_parent_theories', []):
        if th not in CANONICAL:
            bad.append((p.stem, th))

if bad:
    print('REMAINING FABRICATED T1.5 NAMES:')
    for t, th in bad: print(f'  {t}: {th}')
else:
    print('ALL T1.5 NAMES CANONICAL')
"
```

---

*Consolidated by: Claude Opus 4.5*
*Date: 2026-02-23*
*Sources: CC v4 audit, AG v2 superset audit*
