# Instrument Linkage Reference

**Purpose**: Document the formal linkage between outcome vocabulary terms and the instruments registry.

**Last Updated**: 2026-02-28

---

## Data Structure

### Outcome Vocabulary Term (outcome_vocab.json)

Each term now includes an `instrument_ids` array:

```json
{
  "term_id": "affect.anxiety",
  "name": "Anxiety",
  "domain": "affect",
  "parent_id": "affect",
  "definition": "Apprehension and worry",
  "level": 2,
  "cognates": ["nervous", "worried", "apprehensive"],
  "operationalizations": [
    "State-Trait Anxiety Inventory (STAI)",
    "Visual Analogue Scale (VAS-Anxiety)",
    "Skin conductance level"
  ],
  "instrument_ids": ["STAI"]
}
```

### Instruments Registry (instruments_registry.json)

Each instrument has a unique `instrument_id`:

```json
{
  "instrument_id": "STAI",
  "full_name": "State-Trait Anxiety Inventory",
  "abbreviation": "STAI",
  "authors": "Spielberger, C. D., ...",
  "year": 1983,
  "domains": ["affect.anxiety"],
  "status": "active",
  ...
}
```

---

## Linking Semantics

### One-to-Many Relationship

A single outcome term can link to multiple instruments:

```
affect.anxiety → ["STAI", "GAD-7", "BAI"]
```

This represents multiple valid operational definitions of the construct.

### Zero Linkages

Some outcome terms have no matching instruments in the registry:

```
affect.safety_perception → []
```

This indicates either:
1. The outcome is measured via custom/non-standardized methods
2. Relevant instruments exist but are not in the registry yet
3. The operationalization descriptions don't match registry entries

### Many-to-One Relationship

Multiple outcome terms may reference the same instrument:

```
affect.arousal      → ["SAM", ...]
affect.valence      → ["SAM", ...]
affect.dominance    → ["SAM", ...]
```

The Self-Assessment Manikin (SAM) measures multiple emotional dimensions.

---

## Matching Rules

The linking script applies these rules in sequence:

### Rule 1: Exact Abbreviation Match

```
Operationalization: "Continuous Performance Test (CPT)"
                                                   ↓
Extract abbreviation from parentheses: CPT
Lookup in registry: instrument_id = "CPT" ✓
```

### Rule 2: Full Name Match

```
Operationalization: "State-Trait Anxiety Inventory"
                      ↓
Exact match in registry full_name: "State-Trait Anxiety Inventory"
Retrieve instrument_id: "STAI" ✓
```

### Rule 3: Case-Insensitive Fallback

```
Operationalization: "perceived restorativeness scale"
                      ↓
Lowercase lookup: "perceived restorativeness scale"
Registry entry (lowercase): "prs" → "Perceived Restorativeness Scale"
Retrieve instrument_id: "PRS" ✓
```

### Rule 4: No Match

```
Operationalization: "Safety perception scale"
                      ↓
No exact match, no abbreviation extracted
No instrument_id assigned
instrument_ids: [] (empty)
```

---

## Coverage & Gaps

### Current Coverage

| Category | Count | Coverage |
|----------|-------|----------|
| Outcome terms linked | 52 | 46.4% |
| Instruments referenced | 57 | 60.0% |
| Total links created | 72 | — |

### Gap Analysis

#### Terms Without Instruments (60)

- **Behavioral metrics**: dwell_time, walking_speed, comfort_seeking
- **Environmental perception**: color_perception, spatial_clarity
- **Custom scales**: serenity_scale, behavioral_engagement_scale
- **Physiological direct measurement**: heart_rate_variability (HRV), skin_conductance

**Action**: Review whether missing operationalizations should be added to outcome terms or missing instruments should be added to the registry.

#### Instruments Without Outcomes (38)

- **Task-based**: Go-No-Go, Flanker, etc. (cognitive tests not yet operationalized in outcomes)
- **Specialized biomarkers**: fMRI-BOLD, fNIRS, EDA (physiological measures present in registry but not linked)
- **Assessment tools**: MOCA, GAD-7 (clinical instruments in registry but not currently used to operationalize outcomes)

**Action**: Triage unreferenced instruments; determine if they should be included in outcome operationalizations or removed from active registry.

---

## Maintenance Operations

### Re-linking After Registry Changes

If the instruments registry is updated, re-run the linking script:

```bash
python scripts/link_outcomes_to_instruments.py
```

The script will:
1. Rebuild the lookup table from the updated instruments registry
2. Re-match all operationalizations
3. Update outcome_vocab.json with new instrument_ids
4. Print a summary of coverage changes

### Adding a New Outcome Term

When adding a new outcome term with operationalizations:

1. Use standard instrument abbreviations in parentheses: "Name (ID)"
2. Re-run the linking script to automatically populate instrument_ids
3. Verify matches manually (the script doesn't validate semantic correctness)

Example:
```json
{
  "term_id": "affect.joy",
  "name": "Joy",
  "operationalizations": [
    "Modified Differential Emotions Scale (MDES)",
    "Visual Analogue Scale (VAS-Joy)"
  ]
}
```

After re-linking: `"instrument_ids": ["MDES"]` (assuming MDES is in the registry)

### Adding a New Instrument

When adding a new instrument to the registry:

1. Ensure it has a unique `instrument_id` (e.g., abbreviation or short code)
2. Populate `full_name` and `abbreviation` fields (used for matching)
3. Re-run the linking script
4. Verify new matches in the outcome vocabulary

---

## Validation Queries

### Find all outcomes measuring a specific construct

```python
import json

with open('contracts/outcome_vocab/outcome_vocab.json') as f:
    outcomes = json.load(f)

# Find all outcomes linked to STAI
stai_outcomes = [t for t in outcomes['terms'] if 'STAI' in t.get('instrument_ids', [])]
for term in stai_outcomes:
    print(f"{term['term_id']}: {term['name']}")
```

### Find instruments referenced in a domain

```python
# Find all instruments used to measure cognitive outcomes
cog_instruments = set()
for term in outcomes['terms']:
    if term['domain'] == 'cog':
        cog_instruments.update(term.get('instrument_ids', []))
print(sorted(cog_instruments))
```

### Identify operationalizations without matches

```python
# Find operationalizations that didn't match any instrument
unmatched = []
for term in outcomes['terms']:
    if not term.get('instrument_ids'):
        for op in term.get('operationalizations', []):
            unmatched.append((term['term_id'], op))

for term_id, op in unmatched[:10]:
    print(f"{term_id}: {op}")
```

---

## Quality Assurance

### Pre-Commit Checks

Before committing changes to either file:

```bash
# Validate JSON syntax
python -m json.tool contracts/outcome_vocab/outcome_vocab.json > /dev/null
python -m json.tool contracts/instruments/instruments_registry.json > /dev/null

# Check for broken links (no instrument_ids field should be missing)
python -c "
import json
with open('contracts/outcome_vocab/outcome_vocab.json') as f:
    data = json.load(f)
missing = [t['term_id'] for t in data['terms'] if 'instrument_ids' not in t]
if missing:
    print(f'ERROR: Missing instrument_ids in {len(missing)} terms')
else:
    print('✓ All terms have instrument_ids field')
"
```

### Semantic Validation

Manual checks for correctness:

1. **Domain alignment**: Does the instrument fit the outcome domain?
   - Example: STAI should link to affective/anxiety outcomes, not cognitive ones
2. **Construct validity**: Does the operationalization description match the instrument?
3. **Citation accuracy**: Are full names and abbreviations correct?

---

## Future Enhancements

### Bidirectional Linkage

Add an `outcome_terms` array to each instrument in the registry:

```json
{
  "instrument_id": "STAI",
  "outcome_terms": ["affect.anxiety", "affect.worry"],
  ...
}
```

Benefits:
- Enables reverse navigation (instrument → outcomes it measures)
- Facilitates analysis of measurement instrument coverage
- Supports registry validation (checking if all linked outcomes exist)

### Confidence Scoring

Add optional confidence metrics:

```json
{
  "instrument_ids": [
    {
      "id": "STAI",
      "confidence": 0.95,
      "source": "exact_abbreviation_match"
    },
    {
      "id": "GAD-7",
      "confidence": 0.70,
      "source": "domain_inference"
    }
  ]
}
```

Allows distinguishing high-confidence matches from fuzzy matches.

### Temporal Versioning

Track when links were established:

```json
{
  "instrument_ids": ["STAI"],
  "linking_metadata": {
    "created_at": "2026-02-28T18:00:00Z",
    "last_validated": "2026-02-28T18:00:00Z",
    "validation_notes": "Validated by domain expert"
  }
}
```

---

## See Also

- `contracts/outcome_vocab/outcome_vocab.json` — Canonical outcome vocabulary with instrument linkages
- `contracts/instruments/instruments_registry.json` — Instrument registry with metadata
- `scripts/link_outcomes_to_instruments.py` — Linkage script
- `docs/LINKING_OUTCOMES_TO_INSTRUMENTS_SUMMARY.md` — Comprehensive summary report

---

*Reference document for Article_Eater Post-Quinean v1 outcome-instrument linkage system*
