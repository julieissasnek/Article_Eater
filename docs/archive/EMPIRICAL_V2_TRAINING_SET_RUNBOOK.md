# Empirical_v2 Sentence-Field Training Set Runbook

## Goal
Create `sentence -> extracted fields` examples for ML training and a review queue for gold-label curation.

## Script
`scripts/build_empirical_v2_sentence_training_set.py`

## Default Command
```bash
python3 scripts/build_empirical_v2_sentence_training_set.py
```

## Default Outputs
- Training JSONL (silver labels):
  - `data/training/empirical_v2_sentence_field_pairs.jsonl`
- Review JSONL (lower-confidence / conflict rows):
  - `data/training/empirical_v2_sentence_field_pairs.review.jsonl`
- Summary JSON:
  - `data/training/empirical_v2_sentence_field_pairs.summary.json`

## What each row contains
- Whole sentence (`sentence_text`)
- Local context window (`context_window_text`, previous/current/next sentence when available)
- Raw quote (`raw_quote`)
- Extracted fields:
  - `iv_raw`, `dv_raw`, `iv`, `dv`, `direction`, `effect_size`, `effect_size_type`, `p_value`, `sample_n`, `is_significant`, `context`, `claim_type`, `provenance_depth`
- Sentence-level field evidence spans:
  - `field_evidence.iv_span`
  - `field_evidence.dv_span`
  - `field_evidence.direction_span`
  - `field_evidence.p_value_span`
  - `field_evidence.effect_size_span`
  - `field_evidence.significance_cue_span`
- Label quality diagnostics:
  - `extraction_confidence`, `reliability_score`, `ocr_noisy_sentence`

## Current defaults (precision-first)
- Source filter: `abstract,caption`
- Minimum reliability: `0.78`
- Minimum sentence length: `40`
- Sentences per claim: `2` (keeps multiple high-value sentence patterns when present)
- Direction-label conflicts with sentence cues are sent to review queue.
- Placeholder variable labels (e.g., `col_2`, `row_3`) are routed to review queue.

## Useful variants
Include table claims too:
```bash
python3 scripts/build_empirical_v2_sentence_training_set.py --allowed-sources abstract,caption,table
```

Include all claim sources:
```bash
python3 scripts/build_empirical_v2_sentence_training_set.py --allowed-sources all
```

Tighter precision:
```bash
python3 scripts/build_empirical_v2_sentence_training_set.py --min-reliability 0.85
```

Higher recall:
```bash
python3 scripts/build_empirical_v2_sentence_training_set.py --min-reliability 0.70
```

More sentence variants per claim:
```bash
python3 scripts/build_empirical_v2_sentence_training_set.py --sentences-per-claim 3
```

## Recommended ML workflow
1. Start with training JSONL as silver labels.
2. Curate review JSONL into gold labels.
3. Retrain with silver + gold weighting.
4. Re-run extraction and regenerate this dataset each iteration.
