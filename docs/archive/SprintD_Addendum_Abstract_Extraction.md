# SPRINT D ADDENDUM: Abstract Extraction (Tasks D.14 + D.15)
## Send to CC and Codex immediately

---

## Prompt for CC

```
SPRINT D ADDENDUM — Two new tasks added.

Read docs/Doc71_SprintD_Diagnostics_and_Precision_Fix.md, Part 3 (Abstract Extraction).

NEW TASK D.14 — Abstract + Caption Claim Extraction (assigned to YOU)
Dependency: D.1 (vocabulary) DONE

We overlooked abstracts AND figure/table captions. They're the cleanest text we have — 
no OCR, no table parsing, authors state findings in plain English. The current abstract 
extraction (abstract_rule beliefs in the web) captures ONE crude claim per paper with no 
effect size, no sample N, no null findings. A typical abstract contains 2-4 extractable 
claims. Captions on results figures add 1-2 more per paper.

Build src/extraction/abstract_extractor.py:
- extract_claims_from_abstract(paper_id, title, abstract, vocabulary) → list[dict]
- extract_claims_from_captions(paper_id, captions, vocabulary) → list[dict]
- batch_extract_abstracts_and_captions() → processes all 386 papers
- Sources for abstracts: articles table in ae.db, CSV abstract sections, Semantic Scholar API for gaps
- Sources for captions: scan full PDF text (or CSV source_quote fields) for "Figure N." 
  and "Table N." patterns. Extract the full caption sentence. Only process captions that 
  describe RESULTS (e.g., "Figure 3. Mean creativity scores by noise condition") — skip 
  captions that describe methods, stimuli photos, or study design diagrams.

Caption detection patterns:
  - "Figure/Fig. N. Mean/median X by/across condition/group" → results figure, extract DV from X
  - "Figure/Fig. N. Effect of X on Y" → results figure, extract IV=X, DV=Y
  - "Figure/Fig. N. Relationship between X and Y" → results figure, both variables
  - "Figure/Fig. N. Photograph of..." → stimulus photo, SKIP (no extractable claim)
  - "Figure/Fig. N. Floor plan / layout / diagram" → spatial diagram, SKIP
  - "Table N. Regression/ANOVA/correlation results for Y" → results table caption, extract DV=Y
    (This DV-from-caption is critical — it's the missing piece for table extraction too. 
    Save caption DVs in a lookup: {source_table_id: dv_from_caption} so D.6 and D.10 can use them.)

LLM prompt: extract EVERY finding including null results and curvilinear effects
Rule-based fallback using finding-pattern regex
Output: data/production/abstract_claims.json (same claim format as table extraction)
Also output: data/production/caption_dv_lookup.json mapping table IDs to their caption-derived DVs

Expected yield: ~950 claims from abstracts + ~300 from results captions, ~70% cleanly 
vocabulary-mapped, ~40% with effect sizes. The caption DV lookup also fixes table 
extraction precision by solving the "DV is in the caption not the table" problem.

Also incorporate these fixes from Doc 71 into your existing D.1 and D.6 work:
- D.1: target 200+ synonyms, include measurement instruments (RAT, PANAS, PSS, STAI), 
  abbreviations (CCT, SPL, RT60), physiological markers (cortisol→stress, HRV→arousal), 
  ART terms (fascination, being-away), Appleton terms (prospect, refuge). 
  MUST have rejection threshold — return None if best match < 0.65.
- D.6: table-type-aware extraction (different logic per table type), caption-first DV 
  extraction (DV is usually in the caption, not the table body).

When done: "D.14 DONE [CC] <timestamp>" → docs/DONE.md
```

---

## Prompt for Codex

```
SPRINT D ADDENDUM — One new task added, plus fixes for D.3.

Read docs/Doc71_SprintD_Diagnostics_and_Precision_Fix.md, Parts 2 and 3.

NEW TASK D.15 — Abstract/Caption Claim Integration (assigned to YOU)
Dependency: D.14 (CC) + D.10 (yours) DONE

Modify src/extraction/batch_extract.py to merge THREE claim sources:
1. Abstract claims (from CC's D.14: data/production/abstract_claims.json)
2. Caption claims (from CC's D.14: included in abstract_claims.json)
3. Table claims (from your D.10 pipeline)

ALSO: CC's D.14 produces data/production/caption_dv_lookup.json — a mapping from 
source_table_id to the DV extracted from that table's caption. WIRE THIS INTO YOUR 
D.10 TABLE EXTRACTION. When extracting claims from a table, check the lookup first: 
if a caption DV exists for that table, use it instead of guessing the DV from cell 
content. This is the single highest-impact fix for table extraction precision — most 
results tables state the DV only in the caption, not in the body.

Merge rules:
- Same IV+DV+direction in both → flag "corroborated", keep both, prefer table's 
  effect_size and abstract's context description
- Unique to either source → keep, mark provenance
- Same IV+DV with DIFFERENT directions → flag "conflict" for review

Update structured_claims.json to include provenance tracking and summary stats 
(total, from_abstracts, from_tables, corroborated, conflicts).

Also incorporate these fixes from Doc 71 into your D.3 work:
- Add OCR quality gate as PRE-FILTER before table classification. Detect: character 
  doubling (regex (.)\1{2,}), concatenated words (>30 chars, no spaces), consonant 
  clusters >3. Corrupted tables → GARBAGE, skip.
- Self-match detection: if env_var == outcome_var for most rows, classify as 
  EXTRACTION_ERROR not results table.

When done: "D.15 DONE [Codex] <timestamp>" → docs/DONE.md
```
