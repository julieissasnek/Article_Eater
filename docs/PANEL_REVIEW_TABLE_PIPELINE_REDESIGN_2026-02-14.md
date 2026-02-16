# Panel Review: Table Pipeline Redesign (2026-02-14)

## Context Sent to Experts
System state:
- PDF extraction queue: 514 rows
- Completed extracted: 344
- Completed no-claims: 167
- Errors: 3
- Article-type review backlog: 323
- Main failure classes:
  - article family misclassification (previously brittle keyword chain)
  - long-running PDF extraction on difficult layouts
  - table detections that do not convert to high-quality claims
  - insufficient stage-wise measurement of preprocess/repair gain

Current architecture:
- Abstract intake creates provisional table/rule rows immediately.
- PDF stage upgrades provisional evidence with table/discourse extraction.
- Web/BN ingest consumes confirmed rows.

## Expert Queries
Q1. Should abstract-stage rule generation be family-conditional (e.g., suppress causal edge rules for non-empirical or low-confidence type rows)?
Q2. How should uncertainty in article typing propagate into downstream PDF claims (hard block vs soft verification flag)?
Q3. What minimal measurement regime is required so preprocess/repair and timeout recovery are objectively tracked?

## Panel
1. Information Extraction Engineer (scientific NLP pipelines)
2. Causal/Bayesian Systems Engineer (evidence-to-graph reliability)
3. Workflow Reliability Engineer (batch processing and failure recovery)

## Converged Recommendation
1. Apply family-gated abstract rule creation:
   - Only emit abstract causal edge rules when family is empirically credible and classification confidence is acceptable.
   - For non-empirical or low-confidence rows: keep table/provenance record, defer edge rule to PDF/manual confirmation.

2. Propagate type uncertainty into PDF-confirmed claims:
   - Do not discard extracted content.
   - Mark claims with `needs_verification=true` + downgraded quality flags when article family is uncertain.
   - Prevent uncertain claims from being treated as fully trusted in downstream integrations.

3. Make recovery measurable and repeatable:
   - Track timeout recovery pipeline in one run:
     `requeue -> preprocess -> repair -> preprocess -> safe extract`.
   - Report stage gains and residual failures explicitly each run.

## Implemented Revisions
1. Family-gated abstract rule creation (defer weakly typed/non-empirical rows).
2. Article-type uncertainty propagated into PDF claim verification flags.
3. Timeout recovery pipeline with stage-level tracking scripts and artifacts.

## Why This Convergence Is Correct
- It reduces false-positive causal edges at the earliest stage.
- It preserves recall (content still extracted) while protecting graph trust.
- It converts operational troubleshooting into quantifiable engineering control.

