# PARALLEL TASK INSTRUCTIONS FOR ENGINEERING AIs
## Article Eater — Sprint Acceleration While Theory Panels Continue
## February 16, 2026 — Document 35

---

## CONTEXT FOR ALL THREE AIs

Opus (theory architect) is now building gap-filling panels: Light (Doc 34), Materials+Haptic (Doc 35), Space Syntax (Doc 36). These will produce ~10–12 new templates over the next several sessions. **You do not need to wait for these.** There are already **63 formalized templates** (T1–T40, M1–M17, AX1–AX6) and **10 ReductionClaim objects** (ART×4, SRT×3, Biophilia×3) that are fully specified in the panel documents and ready for encoding. Additionally, Document 33 (Dual-Index Cross-Reference Layer) provides a complete attribute-to-mechanism mapping that needs to be encoded as navigable infrastructure.

The work below is parallelizable with Opus's theory work. It draws from Sprint 7 (Theory Tier), Sprints 1–3 (Epistemic Core), and Sprint 0 completion. Each AI has a distinct scope with defined interfaces.

---

# CLAUDE CODE — PRIMARY IMPLEMENTATION

## CC-1: Template Data Structure Encoding (Sprint 7, Part 1)

**What**: Encode all 63 existing mechanistic templates into the software's data model.

**Source documents** (read these first):
- Panels I–V (Docs 13–20): Templates T1–T40, T48–T52
- Panel M-I (Doc 28): Templates M1–M6
- Panel M-II (Doc 29): Templates M7–M11
- Panel M-III (Doc 30): Templates M12–M17
- Panel AX-I (Doc 31): Templates AX1–AX6

**Each template has this structure** (encode every field):

```
template_id: string          # e.g., "PP_SPECTRAL_MATCH_001"
display_id: string           # e.g., "T1"
name: string                 # e.g., "Spectral Match / Fractal Fluency"
structural_pattern: string   # prose description of the causal pattern
higher_order_principle: string  # the general principle this instantiates
framework_ids: string[]      # which theoretical frameworks it belongs to

causal_links: [              # THE CORE — each template has 2–8 of these
  {
    from_variable: string,   # e.g., "fractal_dimension_D"
    to_variable: string,     # e.g., "processing_fluency"
    activity: string,        # e.g., "enhances" | "inhibits" | "modulates"
    from_level: string,      # e.g., "environmental" | "neural" | "cognitive" | "behavioral"
    to_level: string,
    bridging_quality: string, # "strong" | "moderate" | "weak" | "speculative"
    maturity: string         # "established" | "supported" | "preliminary" | "theoretical"
  }
]

scope_conditions: string[]   # when does this template apply?
moderators: string[]         # what factors change the effect size/direction?
interactions: string[]       # which other templates does this interact with?
overall_maturity: string     # "established" | "supported" | "preliminary"
key_references: [            # APA format entries
  { citation: string, google_scholar_count: number }
]
```

**Implementation requirements**:
1. Use TypeScript interfaces that match this schema exactly
2. Store as structured JSON files in `data/templates/` with one file per template
3. Create a template registry module (`src/theory/templateRegistry.ts`) that:
   - Loads all template files at initialization
   - Provides lookup by template_id, display_id, or framework_id
   - Provides search by causal_link properties (from_level, to_level, activity)
   - Returns typed Template objects
4. Write validation that checks: all required fields present, causal_link levels are from the allowed enum, maturity values are from allowed enum, referenced interactions point to existing templates

**Encoding priority** (do these first — they're most frequently referenced):
- T1, T2, T5, T8, T9, T12, T29 (high fan-out templates per Doc 33 matrix)
- AX1, AX3, AX5, AX6 (bridging templates)
- M12 (BRECVEMA — complex multi-mechanism template)

**Acceptance criteria**: All 63 templates encoded, validated, and loadable. Registry can answer: "Give me all templates where from_level = 'environmental' and to_level = 'neural'" and return the correct set.

---

## CC-2: ReductionClaim Encoding (Sprint 7, Part 2)

**What**: Encode the 10 ReductionClaim objects that map Tier 2 theories to Tier 1 mechanisms.

**Source documents**:
- Panel T2-A (Doc 17/21): ART reduction — 4 ReductionClaim objects
- Panel T2-B (Doc 18/22): SRT reduction — 3 ReductionClaim objects
- Panel T2-C (Doc 19/23): Biophilia reduction — 3 ReductionClaim objects
- D1/D1b (Docs 24–25): ReductionClaim architecture specification (DAG structure)

**Each ReductionClaim has this structure**:

```
reduction_id: string           # e.g., "RC_ART_FASCINATION_001"
tier2_theory: string           # e.g., "ART"
tier2_construct: string        # e.g., "Fascination"
tier2_construct_definition: string

reducing_templates: [          # Tier 1 templates that jointly explain this construct
  {
    template_id: string,       # reference to template registry
    role: string,              # how this template contributes to the reduction
    necessity: string,         # "required" | "typical" | "occasional"
    edge_type: string          # "implements" | "enables" | "modulates" | "partially_implements"
  }
]

dag_structure: {               # Directed acyclic graph of template interactions
  nodes: string[],             # template_ids
  edges: [
    { from: string, to: string, type: string }
  ]
}

residual: string               # what the Tier 2 construct captures that the reduction does NOT
confidence: string             # "high" | "moderate" | "low"
key_evidence: string[]         # citations supporting the reduction
```

**Implementation requirements**:
1. Store in `data/reductions/` with one file per ReductionClaim
2. Create `src/theory/reductionRegistry.ts` that:
   - Loads all reduction files
   - Provides lookup by tier2_theory, tier2_construct, or reducing template_id
   - Can traverse the DAG: given a Tier 2 claim, return the full tree of Tier 1 templates
   - Can answer reverse queries: "Which Tier 2 constructs use template T27?"
3. Validate that all template_ids in reducing_templates exist in the template registry

**Acceptance criteria**: All 10 ReductionClaims encoded and validated. System can answer: "How does ART's 'Fascination' reduce to Tier 1?" and return the DAG with T27, T31, T2, etc.

---

## CC-3: Cross-Reference Index Encoding (Sprint 7, Part 3)

**What**: Encode the dual-index cross-reference layer from Document 33 into a navigable data structure.

**Source document**: Doc 33 — Dual-Index Cross-Reference Layer V1.0

**Two indices to encode**:

**Index 1 — Attribute-First** (from Part A of Doc 33):

```
attribute_domains: [
  {
    domain_id: string,           # "A1" through "A10"
    domain_name: string,         # "Materials & Surfaces"
    description: string,
    coverage_rating: number,     # 0–4 (stars)
    sub_attributes: [
      {
        sub_id: string,          # "A1.1"
        name: string,            # "Visual properties of materials"
        template_mappings: [
          {
            template_id: string,
            mechanism_summary: string,   # brief description of relevance
            confidence: number           # 0–4 (stars)
          }
        ]
      }
    ],
    unintegrated_literature: [
      { citation: string, google_scholar_count: number, gap_description: string }
    ],
    open_questions: string[],
    panel_recommendation: { priority: string, description: string }
  }
]
```

**Index 2 — Mechanism-First** (from Part B of Doc 33):

```
mechanism_index: [
  {
    template_id: string,
    architectural_attributes: [
      { domain_id: string, sub_attributes: string[], coverage: number }
    ]
  }
]
```

**Cross-Reference Matrix** (from Part C of Doc 33):
Encode as a 2D lookup: `matrix[template_id][domain_id] → coverage_rating`

**Implementation requirements**:
1. Store attribute domain definitions in `data/attributes/`
2. Create `src/theory/crossReference.ts` that:
   - Loads both indices
   - Provides attribute-first lookup: domain_id → all relevant templates with confidence
   - Provides mechanism-first lookup: template_id → all relevant attribute domains
   - Provides matrix lookup: (template_id, domain_id) → coverage rating
   - Provides gap query: "Which attribute domains have coverage < 2?" → returns list with panel recommendations
3. The cross-reference must stay in sync with the template registry — if a new template is added, the cross-reference can flag it as unmapped

**Acceptance criteria**: Expert workflow from Doc 33 lines 769–781 is executable programmatically. Given "wood surfaces + stress reduction," system returns: A1.1 → T1, T2 (visual grain); A1.2 → AX1, AX2, AX5 (acoustic); A1.3 → T12, T8, AX5 (haptic/thermal); A1.4 → M12 (olfactory).

---

## CC-4: Sprint 1–3 Epistemic Core (parallel with CC-1 through CC-3)

**What**: Build the claim/edge/node infrastructure that the template encoding will plug into.

This is existing sprint plan work. Key tasks:
- **Claim extensions**: Extend the Claim type to support mechanistic claims (not just empirical)
- **Edge/node consolidation**: Standardize the graph representation
- **Bayesian network upgrades**: Support for conditional independence, Markov blankets
- **Coherence engine**: Basic coherence scoring between claims

**Interface with theory tier**: The template registry (CC-1) and reduction registry (CC-2) will feed INTO the epistemic core as structured claim sources. Design the Claim interface to accept template-derived claims. A template's causal_link becomes a MechanisticClaim; a ReductionClaim becomes a ReductionEdge in the graph.

**Key design decision**: Templates are NOT claims themselves — they are *generators* of claims. When a template is applied to a specific finding, it produces a claim. The template says "fractal dimension near D ≈ 1.3 → processing fluency"; the claim says "THIS building's facade has D = 1.35, therefore processing fluency is predicted." The epistemic core manages claims; the theory tier provides the templates that generate them.

---

## CC-5: PDF Table & Abstract Table Audit (Sprint 4–5 prerequisite)

**What**: Evaluate the current state of the PDF extraction tables and abstract tables. Determine whether they are in a condition to interface with the theory tier, and identify what work they need.

**Background**: The theory tier (templates, reductions, cross-reference index) is being built to evaluate findings extracted from papers. But the extraction side — the code that parses PDFs, pulls out abstracts, identifies claims, extracts statistical results, and structures them into queryable tables — was built earlier and may not have the fields, structure, or granularity that the theory tier now requires. We have been building Tier 1 and Tier 2 theory without testing whether the extraction tables can actually connect to it. This audit closes that gap.

**Audit scope — answer these questions**:

### PDF Tables
1. **What is the current schema?** Document every field in the PDF extraction output: what does each column/field represent, what are the data types, what is nullable?
2. **What extraction quality are we getting?** Run the extractor against 5–10 sample papers from the architecture-wellbeing domain (if test papers exist in the repo) and evaluate: Are claims being identified? Are statistical results captured? Are architectural variables named in a way that maps to our attribute domains (A1–A10)?
3. **What is missing for theory-tier connection?** The theory tier needs to match extracted findings to attribute domains and then to templates. For this to work, the extraction must produce at minimum:
   - The **architectural variable** studied (e.g., "ceiling height," "wood surface," "daylight exposure") — mappable to A1–A10 sub-attributes
   - The **outcome variable** (e.g., "stress," "creativity," "satisfaction") — mappable to the `to_variable` field in template causal_links
   - The **direction and magnitude** of the finding (e.g., "15% reduction in self-reported stress")
   - The **study design** (between/within, N, controls) — needed for confidence weighting
   Does the current schema capture these? If not, what fields need to be added?
4. **What is the parse quality for tables embedded in PDFs?** Many architecture-wellbeing papers have results in tables. Can the extractor handle these? What percentage get correctly parsed vs. garbled?

### Abstract Tables
1. **What is the current schema?** Same audit: every field, data type, nullable.
2. **Are abstracts being parsed into structured claims?** An abstract like "We found that wood surfaces reduced cortisol by 12% (p < .01) compared to laminate" should produce a structured claim with variables, direction, effect size, and significance. Is the current parser doing this, or is it storing the abstract as a flat text blob?
3. **Are the parsed claims in a form the theory tier can consume?** The template matching system needs to take a structured finding and ask: "Which attribute domain does this finding belong to? Which templates predict this outcome? Is the finding consistent with, or in tension with, the mechanistic predictions?" Can the current abstract table output feed that query?

### Specific deliverables from this audit:
1. **Schema documentation** — current PDF table and abstract table schemas, fully documented
2. **Gap report** — a list of fields that need to be added or modified for theory-tier compatibility, with priority ranking
3. **Quality report** — results of running the extractor against sample papers, with error analysis
4. **Recommended changes** — specific schema modifications, with estimated effort

**Acceptance criteria**: Written audit report delivered. If the tables are in good shape, the report says so with evidence. If they need work, the report specifies exactly what work, prioritized by what's needed for the expert workflow (Doc 33 §D5) to function end-to-end.

---

# CODEX — SCHEMA DESIGN, CONTRACTS, AND API LAYER

## CX-1: TypeScript Interface Definitions (Sprint 7 prerequisite)

**What**: Define the canonical TypeScript interfaces that Claude Code will implement against. Codex designs the contracts; Claude Code implements them.

**Deliver these interface files**:

```
src/types/template.ts          — Template, CausalLink, Reference interfaces
src/types/reduction.ts         — ReductionClaim, DAGNode, DAGEdge interfaces
src/types/attribute.ts         — AttributeDomain, SubAttribute, TemplateMapping interfaces
src/types/crossReference.ts    — CrossRefMatrix, GapReport interfaces
src/types/claim.ts             — MechanisticClaim, ReductionEdge (bridge to epistemic core)
```

**Design constraints**:
1. All enums must be string unions (not numeric) for readability in JSON
2. Maturity levels: `"established" | "supported" | "preliminary" | "theoretical"`
3. Bridging quality: `"strong" | "moderate" | "weak" | "speculative"`
4. Coverage ratings: 0 (absent) through 4 (strong) — integer, maps to ○ through ★★★★
5. Level taxonomy for causal_links: `"environmental" | "sensory" | "neural" | "cognitive" | "affective" | "behavioral" | "physiological"`
6. Edge types for ReductionClaims: `"implements" | "enables" | "modulates" | "partially_implements"`
7. All IDs must be unique across registries; define an ID validation pattern

**Critical interface**: The `MechanisticClaim` type bridges the theory tier (templates) to the epistemic core (claims). Design it so that:
- It references the source template_id
- It specifies the concrete instantiation (which specific finding triggered this claim)
- It carries the template's maturity and bridging_quality as prior confidence
- It has a slot for empirical evidence that confirms or disconfirms the prediction

**Acceptance criteria**: Interface files compile cleanly. Claude Code can import them and implement against them without ambiguity. No `any` types. Full JSDoc comments on every field explaining what it means and where the data comes from.

---

## CX-2: API Layer for Theory Tier Queries (Sprint 7, Part 4)

**What**: Design the API surface that the rest of the system uses to query the theory tier.

**Core queries the API must support**:

```typescript
// Attribute-first lookup (expert encounters a finding)
getTemplatesForAttribute(domainId: string, subAttributeId?: string): TemplateMapping[]

// Mechanism-first lookup (exploring where a mechanism applies)
getAttributesForTemplate(templateId: string): AttributeMapping[]

// Matrix lookup
getCoverage(templateId: string, domainId: string): number

// Gap analysis
getGaps(maxCoverage?: number): GapReport[]

// Reduction traversal
getReductionForConstruct(theory: string, construct: string): ReductionClaim
getConstructsUsingTemplate(templateId: string): ReductionClaim[]

// Template search
searchTemplates(query: {
  fromLevel?: string,
  toLevel?: string,
  activity?: string,
  minMaturity?: string,
  frameworkId?: string
}): Template[]

// Expert workflow (compound query — the full pipeline from Doc 33 lines 769–781)
evaluateFinding(attributeDomainIds: string[]): {
  relevantTemplates: TemplateMapping[],
  predictions: string[],
  critiques: string[],
  extensions: string[]
}
```

**Implementation notes**:
- This should be a module API (not REST) — it's called internally by the CMR pipeline and the extraction pipeline
- Keep it synchronous where possible; these are in-memory lookups against loaded registries
- The `evaluateFinding` compound query is the ultimate integration test — if it works for the wood-surfaces-stress example from Doc 33, the API is correct

**Acceptance criteria**: Full API specification with types, parameter descriptions, return types, and error conditions. Test specification for each endpoint using examples drawn from Doc 33.

---

## CX-3: Cross-Repo Contract Updates (Sprint 0 completion)

**What**: Update the cross-repo contract (started in Sprint 0) to include the theory tier interfaces.

The existing contract covers the epistemic core. It needs to be extended to specify:
1. How the template registry is loaded and initialized
2. How the reduction registry connects to the claim graph
3. How the cross-reference index is queried by the extraction pipeline (Sprint 4–5)
4. How new templates (from Opus's ongoing panels) are added without breaking existing encodings
5. Versioning: each template file has a `version` field; the registry tracks which version is loaded

**Acceptance criteria**: Contract document updated. All three AIs can read it and know exactly what data shapes cross the boundaries between their code.

---

## CX-4: Extraction-to-Theory Interface Specification (Sprint 4–7 bridge)

**What**: Define the formal interface between the extraction pipeline output (what comes out of PDF/abstract parsing) and the theory tier input (what the template matching system needs to receive).

**Why this matters**: The extraction pipeline (Sprints 4–5) and the theory tier (Sprint 7) were designed in separate sprint blocks. There is currently no specification for how a parsed finding from a paper becomes an input to the template matching system. Without this interface, we have two halves of a system that cannot talk to each other.

**The interface must specify**:

```typescript
// What the extraction pipeline produces for each finding
interface ExtractedFinding {
  paper_id: string;
  finding_id: string;
  source_location: "abstract" | "results_table" | "results_text" | "discussion";
  
  // Architectural variable — must map to attribute domains
  architectural_variable: {
    raw_text: string;              // as stated in paper: "ceiling height"
    normalized_name?: string;      // standardized: "ceiling_height"
    attribute_domain?: string;     // mapped: "A2" (Spatial Scale)
    sub_attribute?: string;        // mapped: "A2.1" (Ceiling height)
    mapping_confidence: number;    // 0–1: how confident is the mapping?
  };
  
  // Outcome variable — must map to template to_variables
  outcome_variable: {
    raw_text: string;              // "self-reported stress"
    normalized_name?: string;      // "stress_self_report"  
    domain: string;                // "affective" | "cognitive" | "behavioral" | "physiological"
  };
  
  // Effect
  direction: "positive" | "negative" | "null" | "curvilinear" | "unclear";
  effect_size?: { type: string; value: number; ci_lower?: number; ci_upper?: number };
  significance?: { p_value?: number; significant: boolean };
  
  // Study quality markers
  study_design: string;            // "RCT" | "quasi-experimental" | "correlational" | "qualitative"
  sample_size?: number;
  control_condition?: string;
}

// What the theory tier needs to perform template matching
interface TheoryMatchInput {
  attribute_domain_id: string;     // "A1" through "A10"
  sub_attribute_id?: string;       // "A1.1", "A2.3", etc.
  outcome_domain: string;          // maps to template causal_link to_level
  direction: string;
}

// The mapping function between them
function extractionToTheoryMatch(finding: ExtractedFinding): TheoryMatchInput;
```

**Key design questions to resolve**:
1. **Who does the attribute domain mapping?** Does the extraction pipeline output a raw architectural variable and the theory tier maps it, or does the extraction pipeline map to A1–A10 itself? Recommendation: extraction maps to A1–A10 using a controlled vocabulary; theory tier accepts the mapping and retrieves templates.
2. **What about findings that span multiple attribute domains?** A study on "open-plan office layout and stress" touches A3 (spatial configuration), A5 (acoustics), A8 (social). The interface must support multi-domain findings.
3. **How does mapping confidence propagate?** If the extraction is uncertain about the attribute domain mapping (confidence = 0.4), that uncertainty should reduce the confidence of the template match downstream.

**Acceptance criteria**: Interface specification delivered. Claude Code can implement the mapping function. The interface handles the wood-surfaces-stress example from Doc 33 and a multi-domain example like the open-plan office case.

---

# ANTIGRAVITY — TEST SUITE AND VALIDATION

## AG-1: Template Encoding Validation Suite

**What**: Build a comprehensive test suite that validates the encoded templates against the source panel documents.

**Test categories**:

### Structural Validation
- Every template JSON file parses without error
- All required fields are present and non-empty
- All enum values are from allowed sets (maturity, bridging_quality, level, activity)
- template_id is unique across all templates
- display_id matches expected pattern (T\d+, M\d+, AX\d+)
- All interaction references point to existing template_ids
- causal_links array has at least 1 entry per template

### Referential Integrity
- Every template_id referenced in a ReductionClaim exists in the template registry
- Every template_id referenced in the cross-reference index exists in the template registry
- Every domain_id in the cross-reference matrix is from the set A1–A10
- Bidirectional consistency: if the attribute index says T2 maps to A4 (Light) at ★★, then the mechanism index must list A4 under T2, and the matrix cell [T2, A4] must = 2

### Content Spot-Checks (against source documents)
For a selected subset of templates (at minimum: T1, T2, T5, T9, T29, M12, AX1, AX3, AX5, AX6), verify:
- The name field matches the panel document
- The number of causal_links matches what the panel specifies
- The key_references include the citations listed in the panel
- The overall_maturity matches the panel's assessment

### Coverage Consistency
- Column sums in the cross-reference matrix match the coverage summary from Doc 33 (lines 654–667)
- A5 (Acoustic) should have 10 templates at ★★+ coverage
- A4 (Light) should have 4 templates at ★★+ coverage
- A7 (Haptic) should have 3 templates at ★★+ coverage

**Implementation**: Write as a test suite (Jest or Vitest) that can be run with `npm test`. Each category is a describe block. Tests should produce clear error messages pointing to the specific template and field that failed.

**Acceptance criteria**: Full test suite passing against Claude Code's encoded data. Zero structural or referential integrity failures. Content spot-checks match source documents.

---

## AG-2: Expert Workflow Integration Test

**What**: Build an end-to-end integration test that executes the expert workflow from Doc 33 (lines 769–781).

**Test scenario**: "Wood surfaces in hospital patient rooms reduce self-reported stress by 15% relative to plastic laminate surfaces."

**Expected behavior**:
1. System identifies relevant attribute domains: A1 (Materials), specifically A1.1 (visual), A1.2 (acoustic), A1.3 (haptic/thermal), A1.4 (olfactory)
2. For each sub-attribute, system returns the correct template mappings:
   - A1.1 → T1 (fractal grain), T2 (complexity), T9 (implicit evaluation), M12→E-cond
   - A1.2 → AX1 (BRECVEMA-A), AX2 (acoustic expectancy), AX5 (cross-modal congruence)
   - A1.3 → T12 (interoceptive), T8 (affordance), AX5 (cross-modal)
   - A1.4 → M12→Episodic, M12→E-cond
3. System generates plausibility assessment: multi-modal convergence (AX6) predicts amplification
4. System generates predictions: effect reduced when modality blocked; stronger when multiple modalities active
5. System generates critiques: visual complexity confound, evaluative conditioning confound, demand characteristics

**Implementation**: This is the canonical acceptance test for the entire theory tier. If this works, the system delivers on its core promise.

**Acceptance criteria**: Test passes. Output matches the worked example in Doc 33.

---

## AG-3: Drift Check Infrastructure (Sprint 9 preview)

**What**: Build the scaffolding for ongoing validation as new templates are added.

When Opus produces new templates (from the Light, Materials, and Space Syntax panels), they need to be encoded and added to the registries. The drift check ensures:
1. New templates don't break existing referential integrity
2. The cross-reference index is updated when new templates are added (flag unmapped templates)
3. Coverage ratings in the matrix are recalculated when new templates fill gaps
4. ReductionClaims remain valid (no dangling references)

**Implementation**: A CI-style check that runs after any template file is added or modified. Reports: what changed, what's new, what's now unmapped, whether coverage ratings need updating.

**Acceptance criteria**: When a new template JSON file is dropped into `data/templates/`, the drift check runs and reports its status cleanly.

---

## AG-4: Extraction-to-Theory Round-Trip Test (Sprint 4–7 bridge validation)

**What**: Build an end-to-end test that takes a real (or realistic) PDF, runs it through the extraction pipeline, and tests whether the output successfully feeds into the theory tier for template matching and evaluation.

**Why this matters**: CC-5 (the audit) tells us what condition the tables are in. CX-4 (the interface spec) tells us what they should look like. AG-4 tests whether the full pipeline actually works — paper in, evaluation out.

**Test scenarios** (at minimum three):

### Scenario 1: Single-domain finding (baseline)
**Input**: A paper (or mock paper) reporting "Wood surfaces in hospital rooms reduced self-reported stress by 15% vs. plastic laminate (N=120, p < .01)."
**Expected pipeline**:
1. Extraction produces an ExtractedFinding with architectural_variable mapped to A1 (Materials), outcome_variable in domain "affective"
2. Theory tier receives TheoryMatchInput, queries attribute index A1
3. Template matching returns: T1, T2, T9, M12 (visual); AX1, AX2, AX5 (acoustic); T12, T8 (haptic); M12 (olfactory); AX6 (convergence)
4. Evaluation output: plausibility assessment, predictions, critiques
**Pass criteria**: All four steps complete without error. Template set matches Doc 33 worked example.

### Scenario 2: Multi-domain finding
**Input**: "Open-plan office workers reported 30% more distraction and 20% lower satisfaction than workers in private offices."
**Expected pipeline**:
1. Extraction maps to: A3 (spatial config), A5 (acoustics), A8 (social)
2. Theory tier queries all three domains
3. Template matching returns: T3, T14 (spatial); T31, T25, AX1 (acoustic); T48–T52, T5, T29 (social)
4. Evaluation identifies: multiple converging pathways predict negative outcome (navigational complexity, ASA overload, social monitoring demand, privacy loss)
**Pass criteria**: Multi-domain routing works. Template set is correct for all three domains.

### Scenario 3: Finding with weak theory-tier coverage (gap detection)
**Input**: "Exposure to blue-enriched LED lighting at 6500K increased alertness ratings by 25% compared to warm 3000K lighting (N=45, p < .05)."
**Expected pipeline**:
1. Extraction maps to: A4 (Light), sub-attribute A4.4 (circadian/non-visual)
2. Theory tier queries A4 and finds: only 4 templates at weak-to-moderate coverage
3. System flags: "Low template coverage for this attribute domain. Gap identified. Relevant unintegrated literature: Berson et al. (2002), Cajochen (2007)."
4. System provides what evaluation it can using T29 (allostatic regulation) but flags confidence as low
**Pass criteria**: System correctly identifies the gap. Does not hallucinate templates that don't exist. Provides honest coverage assessment.

**Implementation notes**:
- If the extraction pipeline is not yet functional enough to parse real PDFs, use mock ExtractedFinding objects that simulate what the pipeline would produce. The point is to test the extraction→theory interface, not the PDF parser itself.
- This test depends on: CC-5 (audit complete), CX-4 (interface defined), CC-1/CC-3 (templates and cross-ref encoded)
- This test becomes the canonical smoke test for the full system. If these three scenarios pass, the core promise of Article Eater — mechanistic evaluation of architectural findings — is functioning.

**Acceptance criteria**: All three scenarios pass. System correctly identifies templates, routes multi-domain findings, and honestly reports coverage gaps.

---

## AG-5: Validate New Templates (ongoing)

**What**: Run the full validation suite against L1–L5, MAT1–MAT5, SC1–SC4 as they arrive from Opus.

Re-run AG-1 structural validation, AG-2 integration test (with expanded scenarios), and AG-3 drift check after each batch of new templates is encoded. Also re-run AG-4 Scenario 3 after the Light panel — at that point, A4 should have improved coverage and the system should return a richer template set for the blue-light finding.

**Acceptance criteria**: New templates pass all existing validations. Coverage ratings improve as predicted by Doc 33 gap analysis.

---

# DEPENDENCY GRAPH

```
Codex CX-1 (interfaces) ──────► Claude Code CC-1 (template encoding)
                          ├────► Claude Code CC-2 (reduction encoding)
                          ├────► Claude Code CC-3 (cross-ref encoding)
                          └────► Antigravity AG-1 (validation suite design)

Claude Code CC-1 ──────────────► Antigravity AG-1b (run validation)
Claude Code CC-2 ──────────────► Antigravity AG-1b (run validation)
Claude Code CC-3 ──────────────► Antigravity AG-2 (integration test)

Codex CX-2 (API design) ──────► Claude Code CC-4 (epistemic core bridge)
                          └────► Antigravity AG-2 (integration test design)

Codex CX-3 (contract update) ──► All (shared reference)

Claude Code CC-5 (extraction audit) ──► Codex CX-4 (extraction-theory interface)
Codex CX-4 (extraction-theory spec) ──► Claude Code (implement mapping function)
                                   └──► Antigravity AG-4 (round-trip test design)

CC-1 + CC-3 + CC-5 + CX-4 ────► Antigravity AG-4 (round-trip test execution)

Antigravity AG-3 (drift check) ── runs continuously as new templates arrive from Opus
Antigravity AG-5 (new template validation) ── runs after each Opus panel delivery
```

**Critical path**: CX-1 → CC-1 → AG-1b (theory tier functional).
**Second critical path**: CC-5 → CX-4 → AG-4 (extraction-theory bridge functional).
These two paths converge at AG-4, which is the first test that the full system works end-to-end.

**Note on CC-5**: The extraction audit (CC-5) can start immediately — it has no dependencies. It examines existing code and tables. Its output feeds CX-4 (interface spec), which then feeds both Claude Code's implementation of the mapping function and Antigravity's round-trip test. CC-5 should be one of the first tasks started because it may reveal problems that change other priorities.

---

# WHAT OPUS IS DOING IN PARALLEL

While the engineering AIs work the above:

| Session | Opus Builds | Templates Produced | Feeds Into |
|---------|-------------|-------------------|------------|
| Current/Next | Panel L-I: Light & Luminance (Doc 34) | L1–L5 (est. 4–5 new) | CC adds to registry; AG validates; CX-2 API serves them |
| Following | Panel MAT-I: Materials + Haptic (Doc 35) | MAT1–MAT5 (est. 4–5 new) | Same pipeline |
| After that | Panel SC-I: Space Syntax (Doc 36) | SC1–SC4 (est. 3–4 new) | Same pipeline |

Each new panel also updates the cross-reference index (Doc 33). Claude Code re-encodes the updated index; Antigravity re-runs coverage validation. **After AG-4 round-trip test passes with the Light panel templates (post-L-I), re-run Scenario 3 — A4 coverage should jump from ★ to ★★★, and the blue-light finding should now return a rich template set instead of a gap warning.**

---

*Document 35 — AI Task Instructions & Parallel Plan V1.1*
*February 16, 2026*
*V1.1 adds: CC-5 (extraction audit), CX-4 (extraction-theory interface), AG-4 (round-trip test), AG-5 (ongoing validation)*
*Next action: CC-5 (extraction audit) and CX-1 (interface definitions) can both start immediately and in parallel. CC-5 has no dependencies; CX-1 unblocks the rest of the theory tier encoding.*
