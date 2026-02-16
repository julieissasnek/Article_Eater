# Theory Layer API Contract V1.0

**Date**: February 16, 2026
**Version**: 1.0.0
**Status**: ACTIVE

---

## 1. Overview

This contract defines the public API surface for the Article Eater Theory Layer (Tier 2). It provides unified access to mechanistic templates, reduction claims, and the cross-reference index.

## 2. Access Point

The entry point for all theory operations is the `TheoryAPI` class exported from `src/api/index.ts`.

```typescript
import { TheoryAPI } from './src/api';

const theory = new TheoryAPI();
await theory.initialize();
```

## 3. Data Types

### 3.1 Mechanistic Template
Represents a causal pathway specification.
- **Type Definition**: `src/types/template.ts`
- **Key Fields**: `id`, `framework_id`, `causal_chain`, `maturity`

### 3.2 Reduction Claim
Represents a theoretical claim reducing a complex construct to simpler mechanisms.
- **Type Definition**: `src/types/reduction.ts`
- **Key Fields**: `reduction_id`, `tier2_construct`, `reducing_templates`, `dag_structure`

### 3.3 Attribute Domain
Represents a domain of environmental attributes.
- **Type Definition**: `src/types/attribute.ts`
- **Key Fields**: `domain_id`, `attributes`, `mapped_templates`
- **Mapped Template Schema**:
  ```typescript
  interface TemplateMapping {
      template_id: string; // Must resolve to a valid template
      coverage: 0 | 1 | 2 | 3 | 4; // Rating (0=None, 4=Strong)
      notes?: string; 
  }
  ```
  *Note: Previous versions used simple string arrays. All new data must use the object format.*

## 4. Methods

### 4.1 Template Access
- `getTemplate(id: string): MechanisticTemplate | undefined`
- `getAllTemplates(): MechanisticTemplate[]`
- `getTemplatesByFramework(frameworkId: string): MechanisticTemplate[]`

### 4.2 Reduction Access
- `getReduction(id: string): ReductionClaim | undefined`
- `getAllReductions(): ReductionClaim[]`

### 4.3 Cross-Reference Access
- `getAttributeDomain(id: string): AttributeDomain | undefined`
- `getAllAttributeDomains(): AttributeDomain[]`
- `getTemplatesForAttributeDomain(domainId: string): MechanisticTemplate[]`

## 5. Invariants

1. **Referential Integrity**: All `template_id` references in Reductions and Attribute Domains MUST resolve to a valid loaded Template.
2. **Immutability**: Loaded data objects should be treated as immutable.
3. **Initialization**: `initialize()` MUST be called and awaited before any query methods are used.

## 6. Error Handling

- Methods return `undefined` for missing IDs.
- `initialize()` logs errors to console but attempts to continue loading partial data.
- Validation logic is available via `tests/validate_theory_completeness.ts`.
