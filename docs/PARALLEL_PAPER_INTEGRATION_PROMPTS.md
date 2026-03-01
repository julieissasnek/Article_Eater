# Parallel Paper Integration — AG Batch Prompts

**Created:** 2026-02-27
**Purpose:** Ready-to-paste prompts for opening multiple AG (Opus) conversations to process papers in parallel.

---

## How to Use

1. Open a **new AG conversation** in your IDE
2. Copy-paste the prompt for one batch below
3. Repeat for as many batches as you want to run in parallel
4. Each AG instance will independently process its batch with full Opus reasoning

> **Important:** Each batch writes to the same database (`data/web_persistence_v2.db`). SQLite handles concurrent reads well but concurrent writes need WAL mode (already set). For safety, we recommend running **2–3 batches in parallel**, not all 11 at once.

---

## Batch 1: Papers 1–100

```
TASK: Process Paper Batch 1 (papers 1-100) for Web of Belief Integration

You are processing research paper extractions into the ATLAS Web of Belief system.

CONTEXT: The project is at /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1
- 1,037 paper extractions exist in data/extractions/ (JSON files with findings, claims, effect sizes)
- 208 templates exist in data/templates/ (the mechanistic vocabulary)
- 13 molecules and 23 T1.5 theories exist in data/molecules/ and data/theories/
- The 14-step integration pipeline is at src/services/paper_integration/orchestrator.py
- The batch manifest is at data/extractions/batch_manifest.json

YOUR BATCH: Process files from batch 1 (papers 1-100) per the manifest.

FOR EACH PAPER:
1. Read the extraction JSON from data/extractions/
2. Evaluate the quality of findings (are they real findings with effect sizes, or noise?)
3. For high-quality findings, run them through PaperIntegrationOrchestrator.integrate_paper()
4. For each finding, assess:
   - Which template(s) does it connect to? (match by construct, DV/IV, keywords)
   - What warrant type is appropriate? (CONSTITUTIVE, MECHANISM, EMPIRICAL_ASSOCIATION, ANALOGICAL)
   - What is the appropriate confidence level?
   - Does it supersede or contradict existing beliefs?
5. Record skip reasons for low-quality papers (too few findings, no effect sizes, wrong domain)
6. Create annotations for notable findings (SENSITIVITY_FLAG for variable parameters, OPEN_QUESTION for gaps)

QUALITY STANDARDS (excellence over speed):
- Examine each paper's findings carefully — do NOT bulk-import without understanding
- Correct warrant type assignment matters more than speed
- Flag any paper that seems to contradict existing template claims
- Provenance must be complete: DOI, finding ID, template match reason

WRITE results to: data/integration_results/batch_1_results.json
Format: {paper_doi: {status, n_findings, n_integrated, n_skipped, skip_reason, template_matches, notes}}

When done, report: total papers processed, findings integrated, quality distribution.
```

---

## Batch 2: Papers 101–200

```
TASK: Process Paper Batch 2 (papers 101-200) for Web of Belief Integration

[Same instructions as Batch 1, but change:]
YOUR BATCH: Process files from batch 2 (papers 101-200) per the manifest at data/extractions/batch_manifest.json.
WRITE results to: data/integration_results/batch_2_results.json
```

---

## Batch 3: Papers 201–300

```
TASK: Process Paper Batch 3 (papers 201-300) for Web of Belief Integration

YOUR BATCH: Process files from batch 3 (papers 201-300) per the manifest.
WRITE results to: data/integration_results/batch_3_results.json
[Use the full instructions from Batch 1.]
```

---

## Batches 4–11: Quick Reference

| Batch | Papers | Result File |
|---|---|---|
| 4 | 301–400 | `data/integration_results/batch_4_results.json` |
| 5 | 401–500 | `data/integration_results/batch_5_results.json` |
| 6 | 501–600 | `data/integration_results/batch_6_results.json` |
| 7 | 601–700 | `data/integration_results/batch_7_results.json` |
| 8 | 701–800 | `data/integration_results/batch_8_results.json` |
| 9 | 801–900 | `data/integration_results/batch_9_results.json` |
| 10 | 901–1000 | `data/integration_results/batch_10_results.json` |
| 11 | 1001–1037 | `data/integration_results/batch_11_results.json` |

For batches 4-11, use the same full prompt as Batch 1 but change the batch number and result file.

---

## After All Batches Complete

Run the merge script to combine results:
```bash
python3 -c "
import json, glob
results = {}
for f in sorted(glob.glob('data/integration_results/batch_*_results.json')):
    batch = json.load(open(f))
    results.update(batch)
print(f'Total papers processed: {len(results)}')
integrated = sum(1 for v in results.values() if v.get('status') == 'integrated')
skipped = sum(1 for v in results.values() if v.get('status') == 'skipped')
print(f'Integrated: {integrated}, Skipped: {skipped}')
json.dump(results, open('data/integration_results/all_results.json', 'w'), indent=2)
"
```
