# SPRINT D: AGENT PROMPTS

## Prompt for CC (Claude Code)

```
Sprint D — Data Remediation — has been committed. Read docs/SprintD_Data_Remediation.md and docs/Doc70_PDF_Data_Diagnosis_and_Remediation.md.

This sprint runs IN PARALLEL with Sprints 12-13. It fixes the PDF extraction DATA while those sprints fix the pipeline engineering. Do not pause or modify your Sprint 12-13 work — Sprint D is additional.

Your tasks are: D.1 (vocabulary sheet), D.2 (paper triage), D.3 (table classification), D.5 (gold standard 15 papers), D.6 (claim extraction engine), D.8 (effect size converter), D.10 (batch pipeline), D.12 (CMR integration).

Start with D.1 (vocabulary), D.2 (triage), and D.8 (effect size converter) — they have no dependencies and can run in any order. D.1 is highest priority because everything else uses the vocabulary.

When done with each task, append to docs/DONE.md: "D.X DONE [CC] <timestamp>". Check DONE.md for dependencies before starting tasks that need other agents' work. D.10 is the convergence point — it needs D.2 + D.3 + D.6 + D.8 all done first.

The core problem: pdfplumber extracted 171k table cells but treated author bios, OCR artifacts, and figure captions as scientific variables. The web of belief (12,628 beliefs) was built from this garbage. Your job is to build the reprocessing pipeline that produces clean structured claims from the raw source_quote text, using the CMR vocabulary as the target schema.

Don't check in unless broken. Don't ask David for confirmation. Document decisions in DECISIONS.md.
```

---

## Prompt for Antigravity

```
Sprint D — Data Remediation — has been committed. Read docs/SprintD_Data_Remediation.md and docs/Doc70_PDF_Data_Diagnosis_and_Remediation.md.

This sprint runs IN PARALLEL with Sprints 12-13. It fixes the PDF extraction DATA while those sprints fix the pipeline engineering.

Your tasks are: D.4 (garbage audit of full CSV), D.7 (gold standard validation framework), D.9 (web of belief health report), D.11 (web rebuild from clean claims), D.13 (sprint validation).

Start immediately with D.4 — it has no dependencies. Audit the FULL 154 MB CSV (not just 10k rows). Quantify: rows by source type, OCR artifacts, unresolved variables, table counts, paper coverage. Save to docs/full_csv_audit_report.md.

D.7 depends on CC finishing D.5 (gold standard papers). D.9 depends on D.4. D.11 depends on D.9 + CC's D.10 (batch pipeline output). D.13 validates everything and goes last.

Check docs/DONE.md before starting tasks with dependencies. When done with each task, append: "D.X DONE [AG] <timestamp>".

Key context: the current web_persistence.db (83 MB, 12,628 beliefs, 28,314 constraints) is populated from garbage extractions. Your D.11 task rebuilds it from CC's clean structured_claims.json. Create web_persistence_v2.db — do NOT overwrite the current web. Your D.13 validates the entire sprint by comparing old web vs new web and running gold standard papers through the CMR pipeline.

Don't check in unless broken. Don't ask David for confirmation. Document decisions in DECISIONS.md.
```
