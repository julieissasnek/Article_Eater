# SPRINT D: AGENT PROMPTS

---

## Prompt for CC (Claude Code)

```
Sprint D — Data Remediation — has been committed. Read docs/SprintD_Data_Remediation.md and docs/Doc70_PDF_Data_Diagnosis_and_Remediation.md.

This sprint runs IN PARALLEL with Sprints 12-13. It fixes the PDF extraction DATA while those sprints fix the pipeline engineering. Do not pause or modify your Sprint 12-13 work — Sprint D is additional.

Your tasks are: D.1 (vocabulary sheet), D.2 (paper triage), D.5 (gold standard 15 papers), D.6 (claim extraction engine), D.12 (CMR integration). NOTE: D.3, D.8, and D.10 have been reassigned to Codex.

Start with D.1 (vocabulary) and D.2 (triage) — they have no dependencies. D.1 is highest priority because everything else uses the vocabulary. Then D.5 (gold standard) once D.1 is done, and D.6 (extraction engine) once D.1 is done.

When done with each task, append to docs/DONE.md: "D.X DONE [CC] <timestamp>". Check DONE.md for dependencies before starting tasks that need other agents' work. D.12 (CMR integration) is your last task — it needs Codex's D.10 and AG's D.11 done first.

The core problem: pdfplumber extracted 171k table cells but treated author bios, OCR artifacts, and figure captions as scientific variables. The web of belief (12,628 beliefs) was built from this garbage. Your job is to build the vocabulary sheet and extraction engine that produces clean structured claims from the raw source_quote text, using the CMR vocabulary as the target schema.

Don't check in unless broken. Don't ask David for confirmation. Document decisions in DECISIONS.md.
```

---

## Prompt for Codex

```
Sprint D — Data Remediation — has been committed. Read docs/SprintD_Data_Remediation.md and docs/Doc70_PDF_Data_Diagnosis_and_Remediation.md.

This sprint runs IN PARALLEL with Sprints 12-13. It fixes the PDF extraction DATA. You are taking three tasks from CC's original assignment to parallelize the work.

Your tasks are: D.8 (effect size converter), D.3 (table reconstruction and classification), D.10 (batch extraction pipeline).

Start immediately with D.8 — it has no dependencies. Build src/extraction/effect_size_converter.py with to_cohens_d() supporting t, F, r, η², β, odds ratio, and p-value-only conversions. Include Hedges' g small-sample correction. Write tests against known textbook values (t(38)=2.10 → d≈0.68, F(1,60)=4.0 → d≈0.52, r=0.30 → d≈0.63, η²=0.06 → d≈0.51).

D.3 depends on CC's D.2 (paper triage). Check DONE.md — when D.2 is done, reconstruct tables by grouping CSV rows on source_table_id, then classify each table as RESULTS_ANOVA, RESULTS_REGRESSION, LITERATURE_REVIEW, DEMOGRAPHICS, MODEL_FIT, GARBAGE, etc. Flag OCR artifacts (doubled characters, concatenated words). Output: data/production/table_classifications.json.

D.10 is the convergence point — it wires together D.2 (triage) + D.3 (table classification) + CC's D.6 (extraction engine) + D.8 (your effect size converter) into src/extraction/batch_extract.py. Check DONE.md — all four must be done before you start D.10. Output: data/production/structured_claims.json.

When done with each task, append to docs/DONE.md: "D.X DONE [Codex] <timestamp>". CC is no longer assigned D.3, D.8, or D.10 — those are yours.

Don't check in unless broken. Don't ask David for confirmation. Document decisions in DECISIONS.md.
```

---

## Prompt for Antigravity

```
Sprint D — Data Remediation — has been committed. Read docs/SprintD_Data_Remediation.md and docs/Doc70_PDF_Data_Diagnosis_and_Remediation.md.

This sprint runs IN PARALLEL with Sprints 12-13. It fixes the PDF extraction DATA while those sprints fix the pipeline engineering.

Your tasks are: D.4 (garbage audit of full CSV), D.7 (gold standard validation framework), D.9 (web of belief health report), D.11 (web rebuild from clean claims), D.13 (sprint validation).

Start immediately with D.4 — it has no dependencies. Audit the FULL 154 MB CSV (not just 10k rows). Quantify: rows by source type, OCR artifacts, unresolved variables, table counts, paper coverage. Save to docs/full_csv_audit_report.md.

D.7 depends on CC finishing D.5 (gold standard papers). D.9 depends on D.4. D.11 depends on D.9 + Codex's D.10 (batch pipeline output). D.13 validates everything and goes last.

Check docs/DONE.md before starting tasks with dependencies. When done with each task, append: "D.X DONE [AG] <timestamp>".

Key context: the current web_persistence.db (83 MB, 12,628 beliefs, 28,314 constraints) is populated from garbage extractions. Your D.11 task rebuilds it from the clean structured_claims.json that Codex produces in D.10. Create web_persistence_v2.db — do NOT overwrite the current web. Your D.13 validates the entire sprint by comparing old web vs new web and running gold standard papers through the CMR pipeline.

Don't check in unless broken. Don't ask David for confirmation. Document decisions in DECISIONS.md.
```

---

## Rebalanced Task Assignments

| Agent | Tasks | Count |
|-------|-------|-------|
| **CC** | D.1, D.2, D.5, D.6, D.12 | 5 |
| **Codex** | D.8, D.3, D.10 | 3 |
| **Antigravity** | D.4, D.7, D.9, D.11, D.13 | 5 |

---

## Shared LLM Ladder Benchmark Prompt (Codex/CC/AG)

Use this when you want all agents to run the same high->balanced->low extraction benchmark protocol.

```
Run the detached ladder benchmark using:

python3 scripts/run_llm_table_ladder_agent.py start \
  --profiles <agent_specific_profiles.json> \
  --n-pdfs 5 \
  --variants strict_gate \
  --mode parallel \
  --detach \
  --tag <agent_label>

Then run:
python3 scripts/run_llm_table_ladder_agent.py status --manifest <manifest_path>
python3 scripts/run_llm_table_ladder_agent.py summarize --manifest <manifest_path>

Report:
1. manifest path
2. ladder_summary.json path
3. best_by_precision_proxy row
4. full runs table (profile, variant, claims, mapped_both_pct, suspect_claims_pct, unknown_direction_pct, precision_proxy)
```
