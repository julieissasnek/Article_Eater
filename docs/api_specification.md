# Theory Tier Module API Specification

Date: 2026-02-16
Owner: Codex (CX-2)
Companion: `docs/35_AI_Task_Instructions_Parallel_Plan.md`

## Scope

This document specifies the internal module API for theory-tier queries. The API is synchronous and in-memory. It is designed to support Doc 33's expert workflow (attribute lookup, plausibility evaluation, predictions, critiques, and gap signaling).

## Data Contracts

Primary types are defined in:
- `src/types/template.ts`
- `src/types/reduction.ts`
- `src/types/attribute.ts`
- `src/types/crossReference.ts`
- `src/types/claim.ts`

## Public Interface

### `getTemplatesForAttribute(domainId: AttributeDomainId, subAttributeId?: SubAttributeId): TemplateMapping[]`
- Purpose: Attribute-first lookup when an expert starts from a finding.
- Parameters:
  - `domainId`: `"A1" | ... | "A10"`
  - `subAttributeId` (optional): sub-attribute ID, e.g. `"A1.1"`
- Returns: all matching template mappings.
- Errors: none; returns empty array when no matches.

### `getAttributesForTemplate(templateId: string): AttributeMapping[]`
- Purpose: Mechanism-first lookup to inspect where a template applies.
- Parameters:
  - `templateId`: global registry ID (validated by `REGISTRY_ID_PATTERN`)
- Returns: all mapped domains/sub-attributes for this template.
- Errors: none; returns empty array when no matches.

### `getCoverage(templateId: string, domainId: AttributeDomainId): number`
- Purpose: Matrix cell lookup.
- Parameters:
  - `templateId`: template ID
  - `domainId`: domain ID
- Returns: integer coverage rating `0..4`.
- Errors: none; unknown pair returns `0`.

### `getGaps(maxCoverage?: number): GapReport[]`
- Purpose: Gap analysis query.
- Parameters:
  - `maxCoverage` (optional): integer threshold `0..4` (default `1`)
- Returns: domains with current coverage count at or below threshold.
- Errors:
  - `TheoryApiError("INVALID_ARGUMENT")` when threshold is not integer `0..4`.

### `getReductionForConstruct(theory: string, construct: string): ReductionClaim`
- Purpose: Get one reduction claim for a theory construct.
- Parameters:
  - `theory`: theory family name (e.g., `"ART"`)
  - `construct`: construct label
- Returns: a single `ReductionClaim`.
- Errors:
  - `TheoryApiError("NOT_FOUND")` if no exact match exists.

### `getConstructsUsingTemplate(templateId: string): ReductionClaim[]`
- Purpose: Reverse traversal from template to reduction claims.
- Parameters:
  - `templateId`: template ID
- Returns: all claims referencing this template.
- Errors: none; empty array for no matches.

### `searchTemplates(query: TemplateSearchQuery): Template[]`
- Purpose: Flexible retrieval by level/activity/maturity/framework.
- Parameters:
  - `query.fromLevel?: LevelTaxonomy`
  - `query.toLevel?: LevelTaxonomy`
  - `query.activity?: string`
  - `query.minMaturity?: MaturityLevel`
  - `query.frameworkId?: string`
- Returns: templates satisfying all provided filters.
- Errors: none; empty array for no matches.

### `evaluateFinding(attributeDomainIds: AttributeDomainId[]): EvaluateFindingResult`
- Purpose: Compound query for the end-to-end expert workflow in Doc 33.
- Parameters:
  - `attributeDomainIds`: one or more domain IDs from extraction/theory mapping.
- Returns:
  - `relevantTemplates: TemplateMapping[]`
  - `predictions: string[]`
  - `critiques: string[]`
  - `extensions: string[]`
- Errors:
  - `TheoryApiError("INVALID_ARGUMENT")` when array is empty.

## Error Model

`TheoryApiError` codes:
- `INVALID_ARGUMENT`: parameter shape/range violations.
- `NOT_FOUND`: requested singleton record does not exist.
- `INVARIANT_VIOLATION`: reserved for registry integrity issues.

## Test Examples (from Doc 33 scenarios)

### Example A: Wood surfaces and stress (single-domain anchor)
- Input finding maps to `A1` plus sub-attributes.
- Test calls:
  - `getTemplatesForAttribute("A1")`
  - `evaluateFinding(["A1"])`
- Expected: includes T1, T2, T9, M12, AX1, AX2, AX5, AX6 family mappings; returns predictions/critiques/extensions.

### Example B: Open-plan office finding (multi-domain)
- Input finding maps to `A3`, `A5`, `A8`.
- Test calls:
  - `evaluateFinding(["A3", "A5", "A8"])`
- Expected: merged template set across all 3 domains and multi-pathway critiques.

### Example C: Blue-enriched light alertness finding (gap detection)
- Input finding maps to `A4`.
- Test calls:
  - `getGaps(1)`
  - `evaluateFinding(["A4"])`
- Expected: low-coverage warning path via gap reports; bounded-confidence predictions only.

## Non-Goals

- No REST/HTTP interface in this phase.
- No async IO dependency in query methods.
- No direct PDF parsing in this layer.
