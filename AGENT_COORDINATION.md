# ⚠️ AGENT COORDINATION — ALL AGENTS MUST READ BEFORE ANY EDIT ⚠️

**Last updated**: 2026-03-04T18:31 by AG (Antigravity in IDE)

## RULE: Before editing ANY file, check this document. After editing, update this document.

---

## COMPLETED FIXES (DO NOT REDO)

| File | Fixed By | What | When |
|------|----------|------|------|
| `scripts/batch_generate_cards.py` | AG | CardSurface bug — now uses `create_card()` correctly | 18:25 |
| `src/qa/belief_clustering.py` | AG | Effect size cap [-5,+5], all members saved, I², richer fields | 18:19 |
| `scripts/enrich_card_sources.py` | AG | Data layer loaders, T1/T2/T3 enrichment | 17:00 |
| `src/qa/card_tab_generators.py` | AG | Evidence/Design/Debate context builders | 17:00 |
| `scripts/cc_restart_safe.py` | AG | Iceberg raw_data, was already correct for CardSurface | 17:00 |

## FILES SAFE TO EDIT (unclaimed)

- `scripts/run_stimulus_extraction.py` — stimulus backfill (needs to be run)
- `scripts/extract_pdf_images.py` — image extraction
- `scripts/v3_surgical_update.py` — can be used for field backfill
- Any NEW files

## CURRENT PRIORITIES (for whoever reads this)

1. **DO NOT re-edit already-fixed files** — check table above first
2. **Run stimulus backfill** (`run_stimulus_extraction.py`) at scale
3. **Backfill effect_size and sample_size** — currently 24% and 5.6% fill
4. **DO NOT start card generation until data quality improves**

## HOW create_card() WORKS
`create_card()` builds CardSurface INTERNALLY with all 12 fields.
Do NOT construct `CardSurface()` directly — use `create_card()`.
The function signature:
```python
create_card(card_type, entity_id, title, confidence_level, confidence_omega, 
            direction, n_findings, n_papers)
```
Then attach body/iceberg after: `card.body = ...`, `card.iceberg = ...`
