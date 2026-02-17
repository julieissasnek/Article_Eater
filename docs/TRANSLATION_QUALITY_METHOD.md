# Translation Quality Method (Qualification + Mapper Upgrade)

Date: 2026-02-16  
Scope: Table -> Rule translation quality for `pdf_table_extracted` rows.

## Problem Statement

The pipeline was enforcing a strict causal rule contract on table-derived rows that are often:

1. noncausal (`sample`, `methodology`),
2. low-information/noisy table text,
3. partially mappable to ontology (not exact canonical terms).

This created a type/contract mismatch: rows passed extraction but failed translation quality at runtime.

## Why "55% ontology + 44% mapper" is not 99%

These categories overlap heavily on the same rows.  
One row can simultaneously have:

- unresolved ontology mapping,
- weak statement-to-source overlap,
- low-information source text.

So improvements must reduce overlap and route rows into explicit qualified states, not just "force resolve everything."

## Method Implemented

### Lane A: Qualification Layer (epistemic honesty)

Added explicit translation qualifiers:

- `translation_status`: `exact | fuzzy | inferred | noncausal | untranslatable_noise`
- `translation_confidence` (0..1)
- `translation_warnings` (pipe-delimited)

Effect:

- Noncausal rows are treated as noncausal, not fake causal failures.
- Noisy rows are explicitly marked as low-confidence/noise.
- Downstream can filter by status instead of trusting binary pass/fail.

### Lane B: Mapper Upgrade (context + alias + ranked candidates)

Upgraded table mapper to use:

- row metadata context (`row_data`, intervention/outcome hints),
- alias expansion (`cct`, `lux`, `hrv`, `co2`, etc.),
- ranked lookup candidates with similarity scores,
- domain/generic fallback (`env.generic.*`, `out.generic.*`, `out.inferred.*`) with explicit low confidence.

This improves practical resolution coverage without pretending uncertain mappings are exact.

### Lane C: Production Backfill (fast retrofit)

Applied translation qualification and inferred canonical backfill directly to existing production rows (no full corpus re-extraction required):

- backfilled `translation_*` for all table rows,
- inferred env canonical IDs for unresolved inferred rows,
- inferred outcome canonical IDs for unresolved inferred rows,
- preserved `untranslatable_noise` for low-information rows.

### Lane D: Updated Audit Semantics

Gold audit and translation-cause analysis were updated to consume `translation_status`, so noncausal and qualified inferred rows are evaluated correctly.

## Concrete Before/After (same 13,253 table rows)

Baseline before this method (pre-qualification/inference pass):

- unresolved environment IDs: `7,943` (`59.9%`)
- unresolved outcome IDs: `11,642` (`87.8%`)
- verified strong rows (gold audit): `705`
- inadequate tables queued: `482`

After method application:

- unresolved environment IDs: `2,749` (`20.7%`)
- unresolved outcome IDs: `4,649` (`35.1%`)
- verified strong rows (gold audit): `7,630`
- inadequate tables queued: `376`

Contract quality remains:

- `error_rate = 0.0`
- `garbled_rate_table_rows = 0.0`

## Justification

This method is justified because it improves utility while preserving epistemic transparency:

1. It does not hide uncertainty.  
   Uncertain mappings are explicitly labeled (`inferred`, `untranslatable_noise`) with low confidence.

2. It avoids false precision.  
   Noncausal rows are not forced into causal env->outcome claims.

3. It is efficient.  
   It upgrades current production rows immediately, then improves future extraction behavior in the main queue processor.

4. It is reversible and auditable.  
   All changes are reflected in explicit fields and existing audit scripts.

## Files Changed

- `scripts/process_realtime_pdf_completion_queue.py`
  - context-aware alias/ranked mapping
  - translation qualification fields in emitted rows
- `scripts/repair_pdf_confirmed_rules.py`
  - translation field backfill/recompute
  - inferred canonical ID backfill for unresolved inferred rows
- `scripts/check_rule_contract_quality.py`
  - translation-status-aware contract checks
- `scripts/audit_table_rule_gold_standard.py`
  - translation-status-aware evaluation
- `scripts/analyze_translation_failure_causes.py`
  - cause attribution using translation qualifiers

## Remaining Gap

Not solved by this pass:

- true extraction-quality failures (low-information table text) still remain a major bucket.
- these require extraction-stage improvements (table parser quality/OCR/structure recovery), not only mapping logic.

## Operational Rule Going Forward

Use row filtering by confidence/status for downstream consumers:

- "high-trust": `translation_status in {exact, fuzzy}` and `translation_confidence >= 0.7`
- "usable-with-caution": `translation_status = inferred`
- "exclude from causal reasoning": `translation_status in {noncausal, untranslatable_noise}`

