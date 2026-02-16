# Cross-Repo Contract v2: Theory Tier Integration

Date: 2026-02-16
Owner: Codex (CX-3)
Supersedes: prior cross-repo contracts that covered epistemic core only.

## Purpose

Define the data and lifecycle contract between:
- Extraction pipeline (PDF/abstract parsing)
- Theory tier registries (templates, reductions, cross-reference)
- Epistemic core claim graph
- Validation and integration tests

## Contracted Artifacts

### 1. Template registry
- Location: `data/templates/*.json`
- Type contract: `src/types/template.ts`
- Required keys: `template_id`, `display_id`, `version`, `name`, `description`, `causal_links`, `overall_maturity`, `bridging_quality`
- ID rule: all IDs must satisfy `REGISTRY_ID_PATTERN` and be globally unique across theory-tier registries.

### 2. Reduction registry
- Location: `data/reductions/*.json`
- Type contract: `src/types/reduction.ts`
- Must reference existing `template_id` values from template registry.

### 3. Cross-reference index
- Location: `data/attributes/*.json` or generated matrix artifact
- Type contract: `src/types/attribute.ts` and `src/types/crossReference.ts`
- Matrix cells are integer coverage ratings `0..4`.
- Domain IDs must be exactly `A1..A10`.

### 4. Theory API layer
- Location: `src/theory/api.ts`
- API contract: `docs/api_specification.md`
- Query methods are synchronous and operate on in-memory registries.

## Initialization Contract

1. Loader validates every artifact against the TypeScript interfaces and JSON-schema equivalents where available.
2. Loader enforces ID uniqueness across:
- template IDs
- reduction claim IDs
- cross-reference row template IDs
3. Loader verifies referential integrity:
- every referenced template exists
- every domain ID is in `A1..A10`
4. Loader publishes a version snapshot:
- template registry version set
- reduction registry version set
- cross-reference version

## Extraction Pipeline Integration Contract

Extraction outputs must be transformable into theory match inputs without lossy domain mapping:
- attribute domain mapping to `A1..A10`
- optional sub-attribute mapping
- outcome domain mapping
- direction and confidence values

Uncertainty propagation rule:
- mapping confidence from extraction must be retained and exposed to downstream evaluation/confidence scoring.

Multi-domain rule:
- one finding may map to multiple attribute domains.
- API consumers must pass all mapped domains to `evaluateFinding`.

## Epistemic Core Bridge Contract

Mechanistic claims exported to the epistemic core must include:
- source template ID
- triggering finding ID and paper ID
- prior confidence fields (`prior_maturity`, `prior_bridging_quality`, numeric prior)
- empirical evidence payload for posterior updates

Bridge edge semantics must use reduction edge types:
- `implements`
- `enables`
- `modulates`
- `partially_implements`

## Versioning Contract

- Every template file has explicit `version`.
- Registry loaders publish loaded versions as a snapshot in runtime metadata.
- Version bumps are required when:
  - required fields change
  - enum sets change
  - mapping semantics change
- Backward compatibility policy:
  - additive optional fields: minor bump
  - required field or enum break: major bump

## Ongoing Template Additions (Opus panel feed)

When new panel templates arrive:
1. Add new template artifacts with unique IDs and versions.
2. Update cross-reference mappings and matrix cells.
3. Re-run validation and drift checks.
4. Recompute gap reports.
5. Update version snapshot.

## Responsibilities

- Claude Code: implements and updates JSON registry artifacts.
- Codex: maintains type contracts, API contracts, and integration spec.
- Antigravity: validates structural/referential integrity and end-to-end behavior.

## Exit Criteria for Contract v2 Adoption

1. `src/types/*.ts` contracts present and used by API/test layers.
2. Theory API spec available in `docs/api_specification.md`.
3. Integration tests can execute expert workflow scenarios.
4. Drift checks enforce referential integrity after template additions.
