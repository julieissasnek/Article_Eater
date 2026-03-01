# Outcome Vocabulary to Instrument Registry Linking Summary

**Date**: 2026-02-28
**Task**: Link outcome vocabulary terms to instrument registry IDs
**Status**: Completed

---

## Overview

Successfully updated `contracts/outcome_vocab/outcome_vocab.json` to add `instrument_ids` fields that reference instruments from `contracts/instruments/instruments_registry.json`. This creates a formal linkage between outcome terms and the measurement instruments that operationalize them.

---

## Matching Strategy

The linking script (`scripts/link_outcomes_to_instruments.py`) employs a multi-level matching strategy:

1. **Abbreviation Extraction** — Identifies instrument abbreviations in parentheses (e.g., "STAI" in "State-Trait Anxiety Inventory (STAI)")
2. **Exact Name Matching** — Matches full operationalization text against instrument full names and abbreviations
3. **Case-Insensitive Fallback** — Handles inconsistent capitalization
4. **Deduplication** — Ensures each term's `instrument_ids` array contains unique entries

### Lookup Table

- **Total lookup entries**: 378 (mapping from instrument abbreviations and full names to instrument IDs)
- **Total instruments in registry**: 95
- **Leverage**: Multiple lookup paths per instrument (e.g., "STAI", "State-Trait Anxiety Inventory", etc.)

---

## Coverage Statistics

### Outcome Terms (n=112)

| Metric | Count | Percentage |
|--------|-------|-----------|
| Terms with ≥1 instrument match | 52 | 46.4% |
| Terms with 0 matches | 60 | 53.6% |
| Total operationalization→instrument links | 72 | — |

### Instruments (n=95)

| Metric | Count | Percentage |
|--------|-------|-----------|
| Instruments referenced in outcomes | 57 | 60.0% |
| Instruments not referenced | 38 | 40.0% |

---

## Top 15 Most-Referenced Instruments

| Rank | ID | Full Name | Outcome Terms |
|------|----|-----------|----|
| 1 | PRS | Perceived Restorativeness Scale | 6 |
| 2 | EEG | Electroencephalography | 5 |
| 3 | CPT | Continuous Performance Test | 2 |
| 4 | BRS | Brief Resilience Scale | 2 |
| 5 | CD-RISC | Connor-Davidson Resilience Scale | 2 |
| 6 | SAM | Self-Assessment Manikin | 2 |
| 7 | ACTIGRAPHY | Actigraphy | 2 |
| 8 | ERP | Event-Related Potential | 2 |
| 9 | ANT | Attention Network Test | 1 |
| 10 | MOT | Multiple Object Tracking | 1 |
| 11 | PVT | Psychomotor Vigilance Task | 1 |
| 12 | SART | Sustained Attention to Response Task | 1 |
| 13 | NASA-TLX | NASA Task Load Index | 1 |
| 14 | AUT | Alternate Uses Task | 1 |
| 15 | RAT | Remote Associates Test | 1 |

**Note**: PRS and EEG are exceptionally well-connected, reflecting their broad applicability across multiple outcome constructs (restorative qualities measured via subjective scales and neural correlates measured via brain activity).

---

## Examples of Successful Linkages

### Cognitive Domain

```json
{
  "term_id": "cog.attention",
  "name": "Attention",
  "operationalizations": [
    "Attention Network Test (ANT)",
    "Continuous Performance Test (CPT)",
    "d-prime signal detection"
  ],
  "instrument_ids": ["ANT", "CPT"]
}
```

### Affective Domain

```json
{
  "term_id": "affect.arousal",
  "name": "Arousal",
  "operationalizations": [
    "Self-Assessment Manikin (SAM)",
    "Semantic Differential scales"
  ],
  "instrument_ids": ["SAM"]
}
```

### Physiological Domain

```json
{
  "term_id": "physio.heart_rate_variability",
  "name": "Heart Rate Variability",
  "operationalizations": [
    "Heart rate variability (HRV)",
    "ECG spectral analysis"
  ],
  "instrument_ids": []
}
```

---

## Terms with No Matches (60 terms)

### Common Reasons for Non-Matching

1. **Domain-Specific Methods** — Terms like "dwell time", "gaze duration", "walking speed" operationalize via behavioral observation or sensor data, not standardized instruments in the registry
2. **Generic Scales** — Some operationalizations reference custom or generic measurement approaches (e.g., "Safety perception scale", "Behavioral observation coding")
3. **Registry Gap** — Some instruments used in operationalizations (e.g., "Serenity Scale") may exist but are not currently in the registry
4. **Behavioral Metrics** — Environmental psychology studies often use direct behavioral metrics rather than standardized instruments

### Sample Terms Without Matches

| Term ID | Name | Example Operationalization |
|---------|------|---------------------------|
| affect.safety_perception | Perceived Safety | Safety perception scale, Fear of crime survey |
| behav.comfort_seeking | Comfort Seeking | Behavioral observation coding, Window/thermostat adjustment frequency |
| behav.dwell_time | Dwell Time | Time in zone (seconds), Stay/leave ratio |
| env.color_perception | Color Perception | Color preference survey, Saturation rating |
| neural.eeg_alpha | Alpha Band Activity | EEG alpha power (8-12 Hz) |
| physio.heart_rate_variability | Heart Rate Variability | Heart rate variability (HRV), ECG spectral analysis |

---

## Unreferenced Instruments (38)

These instruments exist in the registry but do not appear in any outcome term's operationalizations. Possible next steps:

1. **Review** — Assess whether these instruments should be added to outcome terms
2. **Expand** — Enhance outcome term operationalizations to include these instruments
3. **Archive** — Consider whether infrequently-used instruments belong in the active registry

### Sample Unreferenced Instruments

- ACTIGRAPH (ActiGraph Accelerometer)
- AFFECT-GRID (Affect Grid)
- ASHRAE-TSV (ASHRAE Thermal Sensation Vote)
- AWE-S (Awe Experience Scale)
- BALES-IPA (Bales Interaction Process Analysis)
- ECG (Electrocardiography)
- EDA (Electrodermal Activity)
- EYE-TRACKER (Eye-Tracker / Gaze-Tracking System)
- FLANKER (Eriksen Flanker Task)
- FMRI-BOLD (Functional Magnetic Resonance Imaging)
- FNIRS (Functional Near-Infrared Spectroscopy)
- GAD-7 (Generalized Anxiety Disorder-7)
- GONOGO (Go-No-Go Task)
- MOCA (Montreal Cognitive Assessment)

---

## Files Modified

| File | Change | Impact |
|------|--------|--------|
| `contracts/outcome_vocab/outcome_vocab.json` | Added `instrument_ids` array field to all 112 terms | Vocabulary now formally linked to instrument registry |
| `scripts/link_outcomes_to_instruments.py` | Created | Reusable script for maintaining outcome-instrument linkages |

---

## Data Integrity

- ✓ No existing fields modified or deleted
- ✓ JSON syntax validated post-update
- ✓ All 112 terms processed
- ✓ New `instrument_ids` field is an ordered array of unique strings (instrument IDs)
- ✓ Empty arrays used for terms with no matches (consistent representation)

---

## Next Steps

### High Priority

1. **Registry Expansion** — Review terms with no matches (e.g., "Serenity Scale", "Behavioral Engagement Scale") and consider adding missing instruments to the registry
2. **Validation** — Manually review high-usage instruments (PRS, EEG, CPT) to ensure matches are semantically correct
3. **Documentation** — Update data dictionary to explain the new `instrument_ids` field in outcome terms

### Medium Priority

1. **Unreferenced Instruments** — Triage the 38 unreferenced instruments; determine if they should be removed or if outcome terms should be updated
2. **Coverage Analysis** — 46.4% coverage suggests room for improvement; identify high-value gaps
3. **Reverse Linkage** — Consider adding an `outcome_terms` array to instrument registry entries for two-way navigation

### Low Priority

1. **Matching Algorithm** — Explore NLP-based fuzzy matching for improved recall (current strategy is high-precision but may miss valid matches)
2. **Temporal Tracking** — Add metadata to record when each outcome→instrument link was established
3. **Validation Rules** — Formalize rules for acceptable outcome-instrument pairs (e.g., domain compatibility checks)

---

## Technical Notes

### Matching Algorithm Details

```python
# Pattern matching for extracting abbreviations
# Handles: "Anything (ABBREV)", "ABBREV score", etc.
# Case handling: Exact matches preferred, lowercase fallback available
# Deduplication: Set used to prevent duplicate instrument_ids in output
```

### Performance

- **Processing time**: <1 second for 112 terms
- **Lookup efficiency**: O(1) average case for exact matching via dictionary
- **Memory footprint**: ~50KB for lookup table + expanded JSON

### Extensibility

The script can be reused to:
- Re-link after updating the instruments registry
- Add new outcome terms
- Modify matching strategy (adjust regex patterns, implement fuzzy matching)

---

## References

- **Outcome Vocabulary**: `contracts/outcome_vocab/outcome_vocab.json` (v2.0.0)
- **Instruments Registry**: `contracts/instruments/instruments_registry.json` (v1.1.0)
- **Linking Script**: `scripts/link_outcomes_to_instruments.py`

---

*Generated 2026-02-28 by Article_Eater Post-Quinean v1*
