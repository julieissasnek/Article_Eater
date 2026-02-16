# Extraction-to-Theory Interface Specification (CX-4b)

**Status**: Revised V1.1 (CC-5-aligned)
**Author**: Codex
**Date**: February 16, 2026
**Based on**: Doc 35 (CX-4) + CC-5 audit signal

## Why this revision exists

CC-5 found the extraction pipeline does not reliably output:
- `architectural_variable`
- `direction`
- `magnitude`
- `effect_pathway`

A strict type contract that requires these fields is unsafe. CX-4b changes the interface to match observed extractor behavior and moves repair logic to CC-6 mapper implementation.

## Contract changes in CX-4b

1. `ExtractedFinding.architectural_variable` is now optional.
2. `ExtractedFinding.effect.direction` is now optional.
3. `TheoryMatchInput` now includes optional `magnitude` and `effect_pathway`.
4. Mapper failure path changed from bare `null` to structured output:
   - `{ result: TheoryMatchInput | null, confidence: number, warnings: string[] }`

## Mapping behavior requirements (for CC-6)

When `extractionToTheoryMatch` runs:
1. Use explicit mapped domain if provided with high confidence.
2. If missing, use `architectural_variable.raw_text` when available.
3. If still missing, use `intervention_text` fallback and emit warning.
4. Return best viable guess with confidence and warnings whenever possible.
5. Return `result: null` only when no plausible domain can be inferred.

## Epistemic policy

- No silent failures.
- Low-confidence mappings are allowed but must be explicitly flagged.
- Downstream theory-tier consumers decide whether to proceed, request review, or quarantine the finding.

## Type references

- `src/types/extraction.ts`
- `src/types/attribute.ts`
- `src/types/template.ts`
