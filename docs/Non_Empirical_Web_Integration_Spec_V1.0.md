# ⚠️ SUPERSEDED — See (newer version exists) for current version

# Non-Empirical Paper Types: Extraction-to-Web Bridge Specification
## Version 1.0 — February 14, 2026
## Article Eater Epistemic Infrastructure

---

# PART I: THE PROBLEM AND ITS CONSEQUENCES

## 1.1 The Current Gap

Article Eater has 15 extraction template families with detailed schemas specifying what to extract from each paper type. It also has a web-of-belief architecture with typed nodes, typed edges, coherence scoring, and BN assembly. What it lacks is a formal bridge specification: for each non-empirical paper type, what web objects does the extraction produce, and how do those objects participate in the web's epistemic machinery?

The consequence: approximately half of processed PDFs produce no usable claims. The extraction pipeline was designed around an implicit model — paper = empirical study = {Methods, Results, causal claims with effect sizes} — that captures only one of the 15 template families. The other 14 families contain precisely the connective tissue that makes the web of belief more than a glorified effect-size database.

## 1.2 Why Non-Empirical Papers Are More Valuable Per Paper Than Empirical Papers

Consider what different paper types contribute to a Quinean web:

An **empirical paper** contributes 3–8 claim nodes with metadata. Each node connects to a small local neighborhood — the theory it tests, the method it uses, the other studies it replicates or contradicts. Important, but structurally local.

A **review paper** contributes something categorically different: it proposes inferential structure. "Finding A from Lab X, Finding B from Lab Y, and Finding C from Lab Z — which looked unrelated — are actually connected because they all instantiate Mechanism M." That's a set of bridge warrants, coherence links, and theoretical derivation edges connecting dozens of existing nodes. One review paper can be worth more to the web's inferential structure than twenty empirical studies.

A **theoretical paper** contributes proposed causal architectures — the templates against which empirical findings are evaluated. Without these, the BN has nodes but no principled way to determine edge direction.

A **methodological critique** contributes validity assessments that propagate across the web, downgrading the confidence of every study using the criticized method.

A **conceptual framework** contributes the taxonomy — the shared vocabulary that determines whether two claims are about the same construct or different ones.

None of these currently enter the web. The web is flying blind.

## 1.3 What This Specification Does

For each of the 15 template families, this document specifies:

1. **Web node types** produced (extending the current EMPIRICAL_FINDING type)
2. **Edge types** connecting those nodes to the rest of the web
3. **Entrenchment dynamics** — how each node type gains and loses confidence
4. **BN participation** — whether and how each node type enters the Bayesian network
5. **Tier 2 interaction** — how each node type interacts with the epistemic monitoring framework
6. **Extraction-to-web field mapping** — the concrete contract between template output and web ingestion

---

# PART II: EXPANDED NODE TYPE TAXONOMY

## 2.1 Current State

The web currently has one effective node type: `EMPIRICAL_FINDING` — a causal or associational claim extracted from an empirical study, carrying study design metadata, effect sizes, and statistical results.

## 2.2 Proposed Node Types (12 types organized in 5 families)

### Family A: Evidence Nodes (carry data)

| Node Type | Source Templates | Description |
|-----------|-----------------|-------------|
| `EMPIRICAL_FINDING` | empirical_v2, observational_field, case_study | Single-study finding with design metadata. EXISTING TYPE. |
| `SYNTHESIS_CONCLUSION` | meta_analysis, systematic_review | Aggregated finding across multiple studies. Higher-order evidence. |
| `QUALITATIVE_FINDING` | interview_study, ethnographic, grounded_theory, phenomenological | Theme, pattern, or experiential structure from qualitative research. |

### Family B: Structural Nodes (organize the web)

| Node Type | Source Templates | Description |
|-----------|-----------------|-------------|
| `THEORETICAL_PROPOSITION` | theoretical | Proposed causal relationship or mechanism, derived from a theoretical framework. |
| `DERIVED_HYPOTHESIS` | theoretical, conceptual_framework | Testable prediction derived from a proposition. Links to confirming/disconfirming evidence. |
| `CONCEPTUAL_DEFINITION` | conceptual_framework, theoretical | Definition of a construct, term, or distinction. Feeds taxonomy/harmonization. |
| `CONCEPTUAL_CONSTRAINT` | conceptual_framework | A "must-not-conflate" rule: two things that look similar but must be distinguished. |

### Family C: Interpretive Nodes (carry expert judgment)

| Node Type | Source Templates | Description |
|-----------|-----------------|-------------|
| `EXPERT_SYNTHESIS` | narrative_review, thought_piece | Expert interpretation of a body of evidence. Lower confidence than SYNTHESIS_CONCLUSION because selection is non-systematic. |
| `METHODOLOGICAL_CRITIQUE` | thought_piece, narrative_review, systematic_review | Argument that a method, paradigm, or finding is flawed. Propagates validity penalties. |

### Family D: Gap Nodes (mark what's missing)

| Node Type | Source Templates | Description |
|-----------|-----------------|-------------|
| `KNOWLEDGE_GAP` | narrative_review, systematic_review, meta_analysis | Identified gap in the evidence. High VOI signal for future search/research. |

### Family E: Meta-Nodes (organize other nodes)

| Node Type | Source Templates | Description |
|-----------|-----------------|-------------|
| `FRAMEWORK_STRUCTURE` | conceptual_framework | Organizational schema (taxonomy, typology, classification system). Not a claim — a way of organizing claims. |
| `BRIDGE_WARRANT` | theoretical, narrative_review | Explicit link licensing transfer from one domain/level to another (e.g., "neural finding X supports architectural recommendation Y because Z"). EXISTING TYPE, now produced by more sources. |

## 2.3 Node Type Properties

Each node type carries different metadata and participates differently in web computations:

| Node Type | Has Effect Size | Has Study Design | Has Argument Structure | Entrenchment Source | BN Eligible |
|-----------|----------------|------------------|----------------------|--------------------|----|
| EMPIRICAL_FINDING | Yes | Yes | Optional | Direct evidence + coherence | Yes |
| SYNTHESIS_CONCLUSION | Pooled | Aggregate | Yes | Included studies + coherence | Yes (higher weight) |
| QUALITATIVE_FINDING | No | Qualitative design | Yes | Triangulation + coherence | Limited (structural only) |
| THEORETICAL_PROPOSITION | No | N/A | Yes (derivation chain) | Prediction accuracy + coherence | Yes (proposed edges) |
| DERIVED_HYPOTHESIS | Predicted | N/A | Yes | Confirmation/disconfirmation | Yes (prior → posterior) |
| CONCEPTUAL_DEFINITION | No | N/A | No | Adoption + usefulness | No (taxonomy) |
| CONCEPTUAL_CONSTRAINT | No | N/A | Yes | Violations detected | No (validation) |
| EXPERT_SYNTHESIS | No | N/A | Yes | Author expertise + coherence | Limited |
| METHODOLOGICAL_CRITIQUE | No | N/A | Yes (argumentative) | Argument quality + uptake | No (modifies others) |
| KNOWLEDGE_GAP | No | N/A | No | Persistence | No (VOI signal) |
| FRAMEWORK_STRUCTURE | No | N/A | No | Adoption | No (organizational) |
| BRIDGE_WARRANT | No | N/A | Yes | Grounding quality | Yes (licensing) |

---

# PART III: EXPANDED EDGE TYPE TAXONOMY

## 3.1 Current Edge Types

The web currently supports: COHERENCE_SUPPORT, COHERENCE_TENSION, EPISTEMIC_DERIVATION, EPISTEMIC_CROSS_TEMPLATE, EPISTEMIC_MEDIATION, ARGUMENTATIVE_SUPPORT, ARGUMENTATIVE_CHALLENGE, GENERALIZABILITY_WARRANT, plus bridge warrants and causal links.

## 3.2 New Edge Types for Non-Empirical Integration

### 3.2.1 Review/Synthesis Edges

| Edge Type | From → To | Meaning | Weight Source |
|-----------|-----------|---------|---------------|
| `INCLUDES_IN_SYNTHESIS` | SYNTHESIS_CONCLUSION → EMPIRICAL_FINDING | "This meta-analytic conclusion incorporates this study." | Quality of included study |
| `SYNTHESIZES_AS` | SYNTHESIS_CONCLUSION → direction | "Across N studies, evidence direction is [positive/negative/mixed]." | Heterogeneity (I²) |
| `IDENTIFIES_MODERATOR` | SYNTHESIS_CONCLUSION → variable | "Effect is moderated by X." | Moderator analysis quality |
| `CONTRADICTS_SYNTHESIS` | EMPIRICAL_FINDING → SYNTHESIS_CONCLUSION | "This new study contradicts the meta-analytic conclusion." | Study quality vs. synthesis quality |

### 3.2.2 Theoretical Edges

| Edge Type | From → To | Meaning | Weight Source |
|-----------|-----------|---------|---------------|
| `THEORETICALLY_PREDICTS` | THEORETICAL_PROPOSITION → DERIVED_HYPOTHESIS | "Theory T predicts finding H." | Logical validity of derivation |
| `CONFIRMS_PREDICTION` | EMPIRICAL_FINDING → DERIVED_HYPOTHESIS | "This study confirms hypothesis H." | Study quality + effect direction |
| `DISCONFIRMS_PREDICTION` | EMPIRICAL_FINDING → DERIVED_HYPOTHESIS | "This study disconfirms hypothesis H." | Study quality + effect direction |
| `PROPOSES_MECHANISM` | THEORETICAL_PROPOSITION → causal pathway | "Theory T proposes mechanism M connecting X to Y." | Argument quality |
| `SUBSUMES_THEORY` | THEORETICAL_PROPOSITION → THEORETICAL_PROPOSITION | "Theory A subsumes/explains Theory B." | Scope + parsimony |
| `THEORY_TENSION` | THEORETICAL_PROPOSITION → THEORETICAL_PROPOSITION | "Theory A and Theory B make incompatible predictions about X." | Specificity of conflict |

### 3.2.3 Conceptual Edges

| Edge Type | From → To | Meaning | Weight Source |
|-----------|-----------|---------|---------------|
| `DEFINES_CONSTRUCT` | CONCEPTUAL_DEFINITION → construct | "This is what 'restoration' means in this framework." | Adoption rate |
| `MUST_DISTINGUISH` | CONCEPTUAL_CONSTRAINT → (construct_A, construct_B) | "These must not be conflated." | Consequence of conflation |
| `REDEFINES` | CONCEPTUAL_DEFINITION → CONCEPTUAL_DEFINITION | "This newer definition supersedes or refines the older one." | Argument quality |
| `ORGANIZES` | FRAMEWORK_STRUCTURE → [nodes] | "This taxonomy organizes these constructs." | Framework adoption |

### 3.2.4 Critique Edges

| Edge Type | From → To | Meaning | Weight Source |
|-----------|-----------|---------|---------------|
| `CHALLENGES_METHOD` | METHODOLOGICAL_CRITIQUE → method_registry_entry | "This method has validity problem X." | Argument quality |
| `CHALLENGES_PARADIGM` | METHODOLOGICAL_CRITIQUE → [EMPIRICAL_FINDINGs] | "All studies using paradigm P are vulnerable to problem X." | Scope + severity |
| `PROPOSES_BETTER_METHOD` | METHODOLOGICAL_CRITIQUE → method_registry_entry | "Method B addresses the problems of Method A." | Feasibility + adoption |

### 3.2.5 Attribution Edges (from reviews citing primary studies)

| Edge Type | From → To | Meaning | Weight Source |
|-----------|-----------|---------|---------------|
| `ATTRIBUTES_FINDING` | EXPERT_SYNTHESIS → EMPIRICAL_FINDING | "Review R cites Study S as showing X." | Needs verification from primary |
| `INTERPRETS_AS` | EXPERT_SYNTHESIS → interpretation | "Review author interprets evidence as meaning X." | Author expertise |

## 3.3 Edge Type × Node Type Compatibility Matrix

Not all edge types connect to all node types. Here is the valid connection matrix:

| Edge Type | Valid Source Types | Valid Target Types |
|-----------|------------------|-------------------|
| INCLUDES_IN_SYNTHESIS | SYNTHESIS_CONCLUSION | EMPIRICAL_FINDING |
| SYNTHESIZES_AS | SYNTHESIS_CONCLUSION | (direction value) |
| THEORETICALLY_PREDICTS | THEORETICAL_PROPOSITION | DERIVED_HYPOTHESIS |
| CONFIRMS_PREDICTION | EMPIRICAL_FINDING, SYNTHESIS_CONCLUSION | DERIVED_HYPOTHESIS |
| DISCONFIRMS_PREDICTION | EMPIRICAL_FINDING, SYNTHESIS_CONCLUSION | DERIVED_HYPOTHESIS |
| CHALLENGES_METHOD | METHODOLOGICAL_CRITIQUE | (method_registry entry) |
| CHALLENGES_PARADIGM | METHODOLOGICAL_CRITIQUE | EMPIRICAL_FINDING (multiple) |
| DEFINES_CONSTRUCT | CONCEPTUAL_DEFINITION | (construct in taxonomy) |
| MUST_DISTINGUISH | CONCEPTUAL_CONSTRAINT | (construct pair) |
| ATTRIBUTES_FINDING | EXPERT_SYNTHESIS | EMPIRICAL_FINDING |
| SUBSUMES_THEORY | THEORETICAL_PROPOSITION | THEORETICAL_PROPOSITION |
| THEORY_TENSION | THEORETICAL_PROPOSITION | THEORETICAL_PROPOSITION |

---

# PART IV: ENTRENCHMENT DYNAMICS BY NODE TYPE

## 4.1 Principle

In a Quinean web, entrenchment is earned through coherence — mutual support from connected nodes. But different node types earn entrenchment differently. An empirical finding gains confidence from replication and methodological quality. A theoretical proposition gains confidence from successful predictions. A methodological critique gains confidence from the rigor of its argument and the field's uptake. Treating all node types identically in constraint satisfaction would be epistemically wrong.

## 4.2 Entrenchment Rules by Node Type

### EMPIRICAL_FINDING (existing, unchanged)
- **Base**: from source_quality score (method rigor, presentation validity, measurement validity, task-ecological validity, independence)
- **Gains**: replication (+), coherence with other findings (+), confirmation by synthesis (+)
- **Loses**: failed replication (-), methodological critique targeting its method (-), contradicted by higher-quality study (-)

### SYNTHESIS_CONCLUSION
- **Base**: 0.65–0.80 depending on review quality (GRADE-equivalent)
- **Gains**: low heterogeneity (+), consistent moderator pattern (+), no publication bias (+), confirmed by new primary studies (+)
- **Loses**: high heterogeneity (-), significant publication bias (-), contradicted by large new RCT (-), methodological critique of included study pool (-)
- **Special rule**: A SYNTHESIS_CONCLUSION's entrenchment should ALWAYS be ≥ the median entrenchment of its included studies (it represents their aggregate, not a new claim)

### QUALITATIVE_FINDING
- **Base**: 0.40–0.60 depending on qualitative rigor (sampling, saturation, triangulation, member checking)
- **Gains**: triangulation across data sources (+), participant convergence (+), coherence with quantitative findings on same construct (+)
- **Loses**: low transferability (-), single informant (-), researcher positionality concerns (-)
- **Special rule**: QUALITATIVE_FINDINGs cannot directly raise entrenchment of causal claims above the base rate for observational evidence. They can SUPPORT causal claims (corroborate direction, illuminate mechanism) but cannot ESTABLISH them.

### THEORETICAL_PROPOSITION
- **Base**: 0.30–0.55 depending on argument quality (logical validity, premise plausibility, evidential grounding, scope)
- **Gains**: confirmed predictions (+0.05 per confirmation), subsumes rival theory (+), parsimony advantage (+), adopted by other researchers (+)
- **Loses**: disconfirmed predictions (-0.10 per disconfirmation, asymmetric to reflect Popperian logic), rival theory with better predictive record (-), scope limitations discovered (-)
- **Special rule**: Confirmation/disconfirmation is ASYMMETRIC. A single clear disconfirmation should reduce entrenchment more than a single confirmation raises it. This implements a Popperian correction within the Quinean framework.

### DERIVED_HYPOTHESIS
- **Base**: inherits from parent THEORETICAL_PROPOSITION × derivation quality
- **Gains**: confirmed by empirical test (+), confirmed by multiple independent tests (++)
- **Loses**: disconfirmed by empirical test (-), disconfirmed by multiple tests (--)
- **Special rule**: When a DERIVED_HYPOTHESIS is confirmed, entrenchment increase propagates UPWARD to the parent THEORETICAL_PROPOSITION (the theory made a successful prediction). When disconfirmed, entrenchment decrease propagates upward too but with a damping factor (theories can survive some disconfirmation, especially of peripheral predictions).

### CONCEPTUAL_DEFINITION
- **Base**: 0.70–0.90 (definitions themselves can be highly confident; what's uncertain is whether they're useful)
- **Gains**: widely adopted (+), enables productive distinctions (+), consistent with empirical operationalizations (+)
- **Loses**: superseded by better definition (-), conflated terms continue to be used interchangeably despite distinction (-)
- **Special rule**: CONCEPTUAL_DEFINITIONs don't participate in coherence computation directly. They participate INDIRECTLY by determining whether two claims are about the same construct. If Definition D says "restoration" and "stress recovery" are distinct constructs, then claims about restoration and claims about stress recovery should NOT automatically cohere.

### CONCEPTUAL_CONSTRAINT
- **Base**: 0.60–0.85 depending on consequence of violation
- **Gains**: violations empirically demonstrated (+), theoretical argument for distinction strong (+)
- **Loses**: distinction shown to be without practical consequence (-)
- **Special rule**: CONCEPTUAL_CONSTRAINTs act as VALIDATION rules during extraction and web maintenance. When a new claim conflates two things a constraint says must be distinguished, the system should flag it for disambiguation.

### EXPERT_SYNTHESIS
- **Base**: 0.35–0.55 (non-systematic → selection bias risk)
- **Gains**: authored by established domain expert (+), consistent with systematic reviews (+), multiple experts converge (+)
- **Loses**: contradicted by systematic review (-), author has known theoretical commitment affecting interpretation (-), key studies missed (-)
- **Special rule**: EXPERT_SYNTHESIS nodes are DISCOUNTED relative to SYNTHESIS_CONCLUSION nodes. An expert's narrative interpretation gets less weight than a systematic meta-analysis reaching the same conclusion. The discount factor should be configurable (default: 0.7 × equivalent systematic finding).

### METHODOLOGICAL_CRITIQUE
- **Base**: 0.40–0.70 depending on argument quality and scope
- **Gains**: critique adopted by field (+), subsequent studies address the criticized flaw (+), empirical demonstration of the artifact (+)
- **Loses**: critique rebutted with evidence (-), field continues using method without problems (-)
- **Special rule**: METHODOLOGICAL_CRITIQUEs have a PROPAGATION effect. When a critique targets a method in the method registry, it should reduce the measurement_validity or presentation_validity score for EVERY claim extracted from studies using that method. This is the mechanism by which a single Heft-style ecological validity critique can cascade through the web.

### KNOWLEDGE_GAP
- **Base**: N/A (gaps don't have entrenchment in the traditional sense)
- **Lifecycle**: Created when identified in review/synthesis. CLOSED when a study addressing the gap is published and ingested. Gaps that persist across multiple reviews gain priority.
- **Special rule**: KNOWLEDGE_GAP nodes don't participate in coherence or BN computation. They feed the Value of Information (VOI) system — guiding which papers to seek next.

### FRAMEWORK_STRUCTURE
- **Base**: 0.65–0.85 depending on adoption and usefulness
- **Gains**: widely adopted (+), empirically validated taxonomy (+), enables productive research (+)
- **Loses**: superseded by better framework (-), shown to be culturally specific when claimed as universal (-)
- **Special rule**: FRAMEWORK_STRUCTUREs organize other nodes but don't make claims themselves. They should be versioned — when a taxonomy changes, all nodes organized under it may need reclassification.

### BRIDGE_WARRANT
- **Base**: 0.30–0.60 depending on theoretical grounding + empirical support for the bridge
- **Gains**: empirical evidence supporting the bridge (+), multiple independent bridges converge (+)
- **Loses**: bridge shown to fail empirically (-), conditions for bridge shown to be narrower than claimed (-)
- **Special rule**: BRIDGE_WARRANTs carry the burden of justification for cross-level and cross-domain inferences. The default weight for an unjustified bridge is LOW (0.3). Bridges require explicit conditions under which they hold.

---

# PART V: FAMILY-BY-FAMILY WEB INTEGRATION CONTRACTS

This section specifies, for each of the 15 template families, exactly what web objects the extraction produces and how they map from the template's output fields.

## 5.1 EMPIRICAL_V2

**Status**: Already integrated (primary development target)

**Produces**: EMPIRICAL_FINDING nodes
**Edges**: COHERENCE_SUPPORT/TENSION to related findings, BRIDGE_WARRANT to theoretical frameworks, CONFIRMS/DISCONFIRMS_PREDICTION to hypotheses

**Field mapping**: Existing `ae.claim.v1` contract. No changes needed.

---

## 5.2 META_ANALYSIS

**Produces**:
- 1 SYNTHESIS_CONCLUSION per pooled effect
- N INCLUDES_IN_SYNTHESIS edges (one per included study)
- 0–M IDENTIFIES_MODERATOR edges
- 0–K KNOWLEDGE_GAP nodes (from identified gaps)

**Template → Web mapping**:

| Template Field | Web Object | Web Field |
|----------------|------------|-----------|
| `overall_effect.effect_size` | SYNTHESIS_CONCLUSION | `pooled_effect_size` |
| `overall_effect.CI` | SYNTHESIS_CONCLUSION | `confidence_interval` |
| `overall_effect.N_studies` | SYNTHESIS_CONCLUSION | `n_included_studies` |
| `overall_effect.heterogeneity_I2` | SYNTHESIS_CONCLUSION | `heterogeneity` (→ entrenchment modifier) |
| `moderator_analyses[].moderator` | IDENTIFIES_MODERATOR edge | `moderator_variable` |
| `moderator_analyses[].effect_per_level` | IDENTIFIES_MODERATOR edge | `effect_by_level` |
| `publication_bias.result` | SYNTHESIS_CONCLUSION | `publication_bias_assessment` (→ entrenchment modifier) |
| `included_studies[]` | INCLUDES_IN_SYNTHESIS edges | `target_paper_id` |

**Entrenchment computation**:
```
base = 0.75
heterogeneity_penalty = -0.15 if I² > 75%, -0.05 if 50-75%, 0 if < 50%
pub_bias_penalty = -0.10 if significant, -0.05 if marginally significant
quality_bonus = +0.05 if GRADE high, 0 if moderate, -0.05 if low
entrenchment = base + heterogeneity_penalty + pub_bias_penalty + quality_bonus
```

**BN participation**: SYNTHESIS_CONCLUSIONs enter the BN as higher-weight evidence nodes. A meta-analytic finding that ceiling height affects creativity (d=0.4, I²=30%, no publication bias) enters the BN with higher weight than any individual study.

**Tier 2 interaction**: Heterogeneity statistic (I²) is a natural signal for the structural bias detection monitor — high I² means the included studies don't agree, which should trigger investigation of moderators or methodological differences.

---

## 5.3 SYSTEMATIC_REVIEW

**Produces**:
- 1+ SYNTHESIS_CONCLUSION per synthesized theme (qualitative, not pooled)
- N INCLUDES_IN_SYNTHESIS edges
- 0–K KNOWLEDGE_GAP nodes
- 0–M METHODOLOGICAL_CRITIQUE nodes (if review identifies quality problems)

**Template → Web mapping**:

| Template Field | Web Object | Web Field |
|----------------|------------|-----------|
| `themes[].evidence_direction` | SYNTHESIS_CONCLUSION | `evidence_direction` (positive/negative/mixed/insufficient) |
| `themes[].n_studies` | SYNTHESIS_CONCLUSION | `n_included_studies` |
| `themes[].quality_summary` | SYNTHESIS_CONCLUSION | `quality_profile` |
| `inclusion_exclusion.exclusion_criteria` | SYNTHESIS_CONCLUSION | `scope_conditions` (what's outside scope) |
| `gaps[].gap` | KNOWLEDGE_GAP | `gap_description` |
| `quality_issues[].problem` | METHODOLOGICAL_CRITIQUE | `critique_content` |

**Special handling**: Systematic reviews with "mixed" evidence direction should generate COHERENCE_TENSION edges between the conflicting studies, plus a SYNTHESIS_CONCLUSION node that explicitly represents the equipoise.

---

## 5.4 NARRATIVE_REVIEW

**Produces**:
- 1+ EXPERT_SYNTHESIS per author synthesis statement
- N ATTRIBUTES_FINDING edges (claims attributed to cited primary studies)
- 0–K KNOWLEDGE_GAP nodes (identified gaps)
- 0–M BRIDGE_WARRANT nodes (when review proposes connections across domains)

**Template → Web mapping**:

| Template Field | Web Object | Web Field |
|----------------|------------|-----------|
| `themes[].author_synthesis` | EXPERT_SYNTHESIS | `synthesis_statement` |
| `themes[].key_studies[].citation` | ATTRIBUTES_FINDING edge | `attributed_to_paper_id` |
| `themes[].key_studies[].interpretation` | ATTRIBUTES_FINDING edge | `reviewer_interpretation` |
| `conclusions.summary_statements[]` | EXPERT_SYNTHESIS | `conclusion_statement` |
| `conclusions.gaps[]` | KNOWLEDGE_GAP | `gap_description` |
| `author.expertise_domain` | EXPERT_SYNTHESIS | `author_expertise` (→ entrenchment modifier) |
| `author.stated_perspective` | EXPERT_SYNTHESIS | `declared_bias` (→ entrenchment modifier) |

**Critical rule**: ATTRIBUTED_FINDING edges REQUIRE VERIFICATION. When a narrative review says "Smith (2020) showed that biophilic design reduces stress," this is the reviewer's interpretation of Smith's finding. The actual Smith (2020) finding might be more nuanced. Attributed findings should be flagged `needs_verification: true` and matched against primary extractions when Smith (2020) is independently processed.

**Web enrichment value**: The primary value of narrative reviews is the CROSS-STUDY CONNECTIONS the reviewer draws. When a reviewer groups Studies A, B, and C under Theme T and argues they all support Mechanism M, this creates COHERENCE_SUPPORT edges between A, B, and C that the system would not have generated from the individual studies alone. This is the "mortar between bricks" function.

---

## 5.5 THEORETICAL

**Produces**:
- 1+ THEORETICAL_PROPOSITION per core proposition
- 0–N DERIVED_HYPOTHESIS per testable prediction
- 0–M BRIDGE_WARRANT nodes
- 0–K CONCEPTUAL_DEFINITION nodes (new terms introduced)
- Theory-relation edges (SUBSUMES_THEORY, THEORY_TENSION)

**Template → Web mapping**:

| Template Field | Web Object | Web Field |
|----------------|------------|-----------|
| `thesis.main_claim` | THEORETICAL_PROPOSITION (central) | `proposition_text` |
| `arguments.premise_conclusion[]` | THEORETICAL_PROPOSITION | `derivation_chain` |
| `framework.relationships[]` | PROPOSES_MECHANISM edge | `mechanism_specification` |
| `framework.derived_hypotheses[]` | DERIVED_HYPOTHESIS | `hypothesis_text`, `testable_via` |
| `framework.scope_conditions[]` | THEORETICAL_PROPOSITION | `scope_conditions` |
| `foundation.prior_theories[]` | SUBSUMES_THEORY or THEORY_TENSION edge | `relation_type`, `what_changed` |
| `foundation.key_concepts[]` (where source="new") | CONCEPTUAL_DEFINITION | `term`, `definition` |

**Entrenchment computation**:
```
base = 0.35
argument_quality_bonus = +0.15 if logically valid + premises supported,
                         +0.05 if valid but premises questionable,
                         -0.10 if logical gaps
evidential_grounding_bonus = +0.10 if builds on strong empirical base,
                             +0.05 if some support
testability_bonus = +0.05 if clearly testable, -0.05 if difficult to test
```

**BN participation**: THEORETICAL_PROPOSITIONs propose BN edges. A theoretical proposition that "legible layout reduces cognitive load via reduced prediction error" proposes the directed edge `layout_legibility → cognitive_load` with mediator `prediction_error`. This enters the BN as a PROPOSED edge (lower weight than an empirically confirmed edge) until empirical evidence confirms or disconfirms it.

**Prediction tracking**: The system should maintain a ledger for each DERIVED_HYPOTHESIS:
```yaml
hypothesis_id: "kaplan_1995_h3"
text: "Exposure to natural settings restores directed attention capacity"
derived_from: "kaplan_1995_prop2"  # ART's core proposition
confirmed_by: ["berman_2008", "berto_2005", "hartig_2003"]  # 3 confirmations
disconfirmed_by: []  # 0 disconfirmations
current_entrenchment: 0.62  # base 0.35 + 3 × 0.05 + quality adjustments
```

This ledger is how the system implements theory evaluation. A theory with many confirmed predictions and few disconfirmations is gaining entrenchment. A theory with accumulating disconfirmations is losing it.

---

## 5.6 CONCEPTUAL_FRAMEWORK

**Produces**:
- 1+ CONCEPTUAL_DEFINITION per new term
- 0–N CONCEPTUAL_CONSTRAINT per distinction
- 1 FRAMEWORK_STRUCTURE per organizational schema
- 0–M REDEFINES edges (when redefining existing terms)

**Template → Web mapping**:

| Template Field | Web Object | Web Field |
|----------------|------------|-----------|
| `terms[].term` | CONCEPTUAL_DEFINITION | `term_name`, `canonical_id` |
| `terms[].definition_author` | CONCEPTUAL_DEFINITION | `definition_text` |
| `terms[].distinguished_from` | MUST_DISTINGUISH edge | `contrast_term` |
| `distinctions[].name` | CONCEPTUAL_CONSTRAINT | `constraint_name` |
| `distinctions[].category_a/b` | CONCEPTUAL_CONSTRAINT | `concept_pair` |
| `distinctions[].conflation_consequences` | CONCEPTUAL_CONSTRAINT | `violation_consequences` |
| `taxonomy.parent/children` | FRAMEWORK_STRUCTURE | `hierarchy` |
| `taxonomy.organizing_principle` | FRAMEWORK_STRUCTURE | `organizing_principle` |
| `implications.for_measurement[]` | (feeds method_registry) | `recommended_operationalization` |

**System-level effects**:
1. New CONCEPTUAL_DEFINITIONs update the term harmonization lookup tables (`outcome_lookup.json`, `environment_lookup.json`)
2. CONCEPTUAL_CONSTRAINTs become validation rules — when future extractions conflate the distinguished terms, the system flags for disambiguation
3. FRAMEWORK_STRUCTUREs can trigger reclassification of existing nodes if the new taxonomy supersedes an old one

---

## 5.7 THOUGHT_PIECE

**Produces**:
- 0–N EXPERT_SYNTHESIS nodes (where evidence-based)
- 0–M METHODOLOGICAL_CRITIQUE nodes (where critiquing methods/paradigms)
- 0–K KNOWLEDGE_GAP nodes (where identifying needs)

**Critical handling**: Thought pieces have the LOWEST base confidence (0.25) because they are opinion-heavy. The extraction must rigorously distinguish:
- Claims supported by cited evidence → EXPERT_SYNTHESIS (can be somewhat trusted)
- Claims that are pure opinion → flagged `evidence_basis: "opinion"` (very low weight)
- Assertions that sound causal → flagged `asserted_causal: true, requires_external_verification: true` (cannot enter BN without corroboration)

**Template → Web mapping**:

| Template Field | Web Object | Web Field |
|----------------|------------|-----------|
| `claims[].claim` (where evidence-backed) | EXPERT_SYNTHESIS | `synthesis_statement` |
| `claims[].claim` (where opinion) | EXPERT_SYNTHESIS | `synthesis_statement` + `evidence_basis: "opinion"` |
| `methodology_critique[]` | METHODOLOGICAL_CRITIQUE | `critique_content` |
| `recommendations[]` | EXPERT_SYNTHESIS or KNOWLEDGE_GAP | depends on whether actionable gap or interpretation |
| `coi_declaration` | EXPERT_SYNTHESIS | `conflict_of_interest` (→ entrenchment modifier) |

---

## 5.8 MIXED_METHODS

**Produces**: Combination of EMPIRICAL_FINDING (from quantitative strand) + QUALITATIVE_FINDING (from qualitative strand), plus a CONVERGENCE_ASSESSMENT meta-node.

**Special handling**: The integration strategy matters epistemically:
- **Convergent findings** (quant and qual agree): Both strands' findings get an entrenchment BONUS for convergence
- **Divergent findings** (quant and qual disagree): Both get flagged for investigation; COHERENCE_TENSION edge between them
- **Complementary findings** (qual illuminates mechanism for quant finding): BRIDGE_WARRANT from qualitative mechanism to quantitative effect

**Template → Web mapping**: Route quantitative strand fields through EMPIRICAL_FINDING mapping, qualitative strand through QUALITATIVE_FINDING mapping, then generate cross-strand edges based on integration strategy.

---

## 5.9 OBSERVATIONAL_FIELD

**Produces**: EMPIRICAL_FINDING nodes, but with `causal_level: "association"` ceiling.

**Special handling**: These findings have HIGH ecological validity (real behavior in real settings) but LOW causal certainty (no experimental control). The task-ecological validity score should be high (0.8–1.0 for REAL_TASK_CONTROLLED or NATURAL_BEHAVIOR), while methodological_rigor is moderate.

This creates an interesting tension: the most ecologically valid evidence is the least causally certain. The system should represent this explicitly — these findings tell us WHAT HAPPENS in real buildings but not WHY.

---

## 5.10 CASE_STUDY

**Produces**: EMPIRICAL_FINDING nodes (descriptive) + potential BRIDGE_WARRANT or DERIVED_HYPOTHESIS (from process tracing).

**Template → Web mapping**:

| Template Field | Web Object | Web Field |
|----------------|------------|-----------|
| `case_description` | Context metadata | (not a node) |
| `findings[].finding` | EMPIRICAL_FINDING | `statement` (with `causal_level: "association"`) |
| `process_tracing` | BRIDGE_WARRANT or DERIVED_HYPOTHESIS | `proposed_mechanism` |
| `generalization_limits` | EMPIRICAL_FINDING | `scope_conditions` |
| `hypothesis_generation[]` | DERIVED_HYPOTHESIS | `hypothesis_text` (with `source: "case_derived"`) |

**Special rule**: Case study findings should carry explicit generalization limits. A finding from "one hospital ward redesign" should not be treated as equivalent to a finding from "N=93 RCT."

---

## 5.11 INTERVIEW_STUDY

**Produces**: QUALITATIVE_FINDING nodes

**Template → Web mapping**:

| Template Field | Web Object | Web Field |
|----------------|------------|-----------|
| `themes[].theme` | QUALITATIVE_FINDING | `finding_statement` |
| `themes[].participant_convergence` | QUALITATIVE_FINDING | `convergence_level` (→ entrenchment modifier) |
| `analytic_method` | QUALITATIVE_FINDING | `method_quality` |
| `credibility_limits` | QUALITATIVE_FINDING | `scope_conditions` |

**Epistemic role**: Interview findings are PERSPECTIVAL — they tell us how people experience and interpret environments, not what environments objectively do. This maps to the EXPLICIT pathway in the effect pathway taxonomy. Interview data is strong evidence for "people consciously notice and appreciate X" claims but weak evidence for "X reduces cortisol" claims.

---

## 5.12 ETHNOGRAPHIC

**Produces**: QUALITATIVE_FINDING nodes + potential CONCEPTUAL_DEFINITION nodes (when identifying tacit cultural patterns)

**Special value**: Ethnographic studies are uniquely positioned to identify cultural variation in environmental experience — exactly the kind of evidence needed for the Goldilocks framework on cultural variation in sensory preferences. Ethnographic findings about how different cultures use, modify, and experience built spaces should be tagged with cultural context metadata.

---

## 5.13 GROUNDED_THEORY

**Produces**: QUALITATIVE_FINDING nodes + DERIVED_HYPOTHESIS nodes (grounded theory generates theory from data)

**Special handling**: Grounded theory's output is a substantive theory — a set of categories, relationships, and a core category that organizes them. This is structurally similar to a THEORETICAL_PROPOSITION, but derived from data rather than from logical argument. It should enter the web as a set of DERIVED_HYPOTHESEs with `source: "grounded_theory"` and moderate entrenchment (0.45–0.60, higher than purely theoretical propositions because data-derived, but needing replication).

---

## 5.14 PHENOMENOLOGICAL

**Produces**: QUALITATIVE_FINDING nodes (experiential structures)

**Epistemic role**: Phenomenological findings describe the STRUCTURE of experience — what it is LIKE to be in a particular kind of space. These are first-person evidence about conscious experience. They enter the web as QUALITATIVE_FINDINGs with `evidence_type: "experiential_structure"` and explicit `causal_level: null` (phenomenology makes no causal claims).

**Design relevance**: Despite making no causal claims, phenomenological findings are highly relevant to design because they articulate what architects should be designing FOR — the experiential qualities people value.

---

## 5.15 PANEL_ADDITIONS (Cross-Cutting)

**Not a source of nodes** — panel additions specify METADATA that attaches to nodes from all other families:
- `causal_level` → stored on every node
- `argument_scheme` + `critical_questions` → stored as argumentative metadata
- `contrast_class` + `difference_maker` → stored on explanatory claims
- `extraction_difficulty` + `source_zone` → stored for audit/calibration

---

# PART VI: EXTRACTION-TO-WEB INGESTION CONTRACT

## 6.1 The Problem Identified in Gap Audit C1/C2

The gap audit found that table-derived claims use `claim_text` / `confidence` while the web expects `statement` / `ae_confidence`. This field mismatch causes silent data loss during ingestion.

## 6.2 Universal Ingestion Contract (ae.claim.v2)

Every node entering the web — regardless of source template family — must carry these fields:

```yaml
# === REQUIRED FOR ALL NODE TYPES ===
node_id: ""                    # Unique identifier
node_type: ""                  # One of the 12 types from §2.2
paper_id: ""                   # Source paper
statement: ""                  # Human-readable claim/finding text
ae_confidence: 0.0             # [0, 1] confidence score
provenance_tier: ""            # abstract_provisional | pdf_confirmed
evidence_level: ""             # abstract_finding_rule | pdf_table_extracted
source_section: ""             # abstract | introduction | methods | results | discussion | conclusion
source_page_start: null        # Page number (if PDF)
source_page_end: null
source_quote: ""               # Verbatim supporting quote
source_quote_hash: ""          # For deduplication

# === REQUIRED FOR EVIDENCE NODES (Family A) ===
study_design: ""               # RCT | quasi_experimental | observational | cross_sectional | ...
sample_size: null
effect_size: null
effect_size_type: ""           # cohen_d | eta_squared | odds_ratio | correlation | ...
confidence_interval: []
p_value: null
causal_level: ""               # association | intervention | counterfactual

# === REQUIRED FOR STRUCTURAL NODES (Family B) ===
derivation_chain: []           # Premise → conclusion steps
scope_conditions: []           # When this applies / doesn't
testable: true|false
falsifiable: true|false

# === REQUIRED FOR INTERPRETIVE NODES (Family C) ===
author_expertise: ""
evidence_basis: ""             # cited_evidence | expert_opinion | consensus
n_studies_cited: null
declared_bias: ""

# === REQUIRED FOR ALL: ARGUMENTATIVE METADATA (Panel Additions) ===
argument_scheme: ""            # From Walton taxonomy
critical_questions: []
critical_questions_addressed: []
critical_questions_unaddressed: []
contrast_class: ""             # "Why X rather than Y?"
difference_maker: ""

# === REQUIRED FOR ALL: WEB INTEGRATION METADATA ===
extraction_difficulty: ""      # easy | moderate | hard
source_zone: ""                # abstract | introduction | methods | results | discussion | conclusion | table | figure
article_type_family: ""        # One of 15 canonical families
template_version: ""           # Template version used for extraction
```

## 6.3 Edge Ingestion Contract (ae.edge.v2)

Every edge entering the web must carry:

```yaml
edge_id: ""                    # Unique identifier
edge_type: ""                  # One of the types from §3.2
source_node_id: ""             # From
target_node_id: ""             # To
weight: 0.0                    # [0, 1] — strength of connection
paper_id: ""                   # Paper that justifies this edge (may differ from source/target paper)
evidence_basis: ""             # explicit_statement | implicit_connection | reviewer_interpretation
justification: ""              # Human-readable reason for this edge
provenance_tier: ""            # abstract_provisional | pdf_confirmed
needs_verification: false      # True for attributed findings from reviews
```

---

# PART VII: IMPLICATIONS FOR TIER 2 EPISTEMIC MONITORING

## 7.1 Reflexive Monitor Updates

The four reflexive monitors (coherence audit, entrenchment asymmetry, structural bias, adversarial review) need updates to handle the new node types:

### Coherence Audit
Now must detect coherence drift in THEORETICAL_PROPOSITION nodes — when a theory's entrenchment changes without new direct evidence, that's suspicious. But it's EXPECTED when a theory's predictions are being confirmed or disconfirmed; the entrenchment change flows through the DERIVED_HYPOTHESIS links. The audit should distinguish legitimate propagation from unexplained drift.

### Entrenchment Asymmetry Monitor
Now must flag THEORETICAL_PROPOSITIONs with high entrenchment but few confirmed predictions — a theory that's entrenched purely by coherence with other theories, without empirical grounding, is epistemically suspect.

### Structural Bias Detection
Now must check for REVIEW_DOMINANCE — when most of the web's structure comes from a small number of review papers rather than from independent primary studies. Over-reliance on one influential review means the web inherits that reviewer's selection bias and interpretive framework.

### Adversarial Review
Now must test whether removing a single highly-influential review paper would collapse web structure. If so, the web is fragile.

## 7.2 Method Registry Integration

METHODOLOGICAL_CRITIQUE nodes should update the method registry:
- When a critique targets a specific method, the method's `confounds` list should be updated
- When a critique proposes a better method, the registry should note the recommended alternative
- When a critique has been widely adopted by the field, the method's `construct_validity_map` should be adjusted downward for the affected constructs

## 7.3 Auto-Challenge Generation

The five automatic argumentative challenges should now also trigger from non-empirical sources:
- A THEORETICAL_PROPOSITION proposing that "effect X operates through implicit physiological pathways" should trigger Challenge 2 (presentation lacks critical channel) for any EMPIRICAL_FINDING claiming to test this effect using photographs
- A METHODOLOGICAL_CRITIQUE arguing that "all photo-based preference studies have low ecological validity" should trigger Challenge 5 (exposure duration inadequate) for all relevant studies

---

# PART VIII: IMPLEMENTATION PRIORITY

## 8.1 What Codex Needs Now

For the immediate table extraction work, Codex needs to know: which fields from each template should be extracted with web integration in mind? The answer: **all of them, but with explicit node_type and edge_type tagging**.

The minimal change to the extraction pipeline:
1. Add `node_type` field to every extracted claim/rule (one of the 12 types)
2. Add `edge_type` field to every extracted relation (one of the types from §3.2)
3. Ensure all extracted claims carry the `ae.claim.v2` required fields
4. Ensure all extracted relations carry the `ae.edge.v2` required fields

## 8.2 What Claude Code Needs Next

A new Sprint (6 or 4c) implementing:
1. Node type enum and schema extensions (the 12 types)
2. Edge type enum and schema extensions (the new edge types)
3. Entrenchment dynamics per node type (the rules from §4.2)
4. Prediction tracking ledger for THEORETICAL_PROPOSITIONs
5. Updated reflexive monitors (§7.1)
6. Method registry integration for METHODOLOGICAL_CRITIQUEs (§7.2)

## 8.3 Priority Order

1. **THEORETICAL + CONCEPTUAL_FRAMEWORK templates** — these provide the structural skeleton the web needs most urgently
2. **META_ANALYSIS + SYSTEMATIC_REVIEW templates** — these provide high-quality aggregated evidence
3. **NARRATIVE_REVIEW templates** — these provide cross-study connections and expert interpretation
4. **THOUGHT_PIECE + METHODOLOGICAL templates** — these provide validity challenges and field direction
5. **Qualitative families** (interview, ethnographic, grounded theory, phenomenological, case study) — these provide ecological validity and experiential evidence

---

# PART IX: GOLD STANDARD TABLE REQUIREMENTS FOR NON-EMPIRICAL PAPERS

## 9.1 What "Gold" Means for Each Non-Empirical Family

### Meta-Analysis Gold Standard
- [ ] Every included study identified with paper_id
- [ ] Pooled effect(s) with CI and heterogeneity
- [ ] Moderator analyses extracted as structured data
- [ ] Publication bias assessment captured
- [ ] Each pooled effect tagged as SYNTHESIS_CONCLUSION node type
- [ ] INCLUDES_IN_SYNTHESIS edges enumerated

### Systematic Review Gold Standard
- [ ] PRISMA counts present
- [ ] Theme-level evidence direction for each synthesized topic
- [ ] Quality ratings for included studies captured
- [ ] Each synthesis statement tagged as SYNTHESIS_CONCLUSION node type
- [ ] Gaps tagged as KNOWLEDGE_GAP node type

### Theoretical Paper Gold Standard
- [ ] Core propositions extracted as numbered, distinct statements
- [ ] Derivation chain (premises → conclusions) captured
- [ ] Proposed mechanisms extracted with trigger/process/outcome
- [ ] Testable predictions extracted as DERIVED_HYPOTHESIS nodes
- [ ] Scope conditions explicit
- [ ] Relations to prior theories captured (extends/critiques/subsumes)
- [ ] New terms captured as CONCEPTUAL_DEFINITION nodes
- [ ] Each proposition tagged as THEORETICAL_PROPOSITION node type

### Conceptual Framework Gold Standard
- [ ] New terms with definitions, distinguished_from, canonical_id
- [ ] Key distinctions with categories, diagnostic criteria, conflation consequences
- [ ] Taxonomy structure with organizing principle
- [ ] Implications for measurement extracted
- [ ] Each term tagged as CONCEPTUAL_DEFINITION node type
- [ ] Each distinction tagged as CONCEPTUAL_CONSTRAINT node type

### Narrative Review Gold Standard
- [ ] Author expertise assessed and recorded
- [ ] Each synthesis statement distinguished from attributed findings
- [ ] Attributed findings linked to cited primary sources
- [ ] Evidence-vs-opinion separation enforced
- [ ] Identified gaps extracted as KNOWLEDGE_GAP nodes
- [ ] Cross-study connections captured as edge proposals

### Thought Piece Gold Standard
- [ ] Every claim tagged as evidence-backed vs. opinion
- [ ] COI declaration captured
- [ ] Asserted-causal claims flagged for external verification
- [ ] Methodological critiques extracted as METHODOLOGICAL_CRITIQUE nodes
- [ ] Confidence floor enforced (≤ 0.25 base for opinion claims)

## 9.2 Quality Gate Updates

Add to `config/table_extraction_quality_thresholds.json`:

```json
{
  "non_empirical_gates": {
    "theoretical_proposition_coverage": 0.80,
    "derived_hypothesis_per_theoretical_paper": 1,
    "node_type_tag_rate": 0.95,
    "edge_type_tag_rate": 0.90,
    "theory_link_has_relation_type": 0.85,
    "opinion_evidence_separation_rate": 0.90
  }
}
```

---

# APPENDIX A: COMPLETE NODE TYPE → TEMPLATE FAMILY MAPPING

| Template Family | EMPIRICAL_FINDING | SYNTHESIS_CONCLUSION | QUALITATIVE_FINDING | THEORETICAL_PROPOSITION | DERIVED_HYPOTHESIS | CONCEPTUAL_DEFINITION | CONCEPTUAL_CONSTRAINT | EXPERT_SYNTHESIS | METHODOLOGICAL_CRITIQUE | KNOWLEDGE_GAP | FRAMEWORK_STRUCTURE | BRIDGE_WARRANT |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| empirical_v2 | ✓ | | | | | | | | | | | |
| meta_analysis | | ✓ | | | | | | | | ✓ | | |
| systematic_review | | ✓ | | | | | | | ✓ | ✓ | | |
| narrative_review | | | | | | | | ✓ | | ✓ | | ✓ |
| theoretical | | | | ✓ | ✓ | ✓ | | | | | | ✓ |
| conceptual_framework | | | | | | ✓ | ✓ | | | | ✓ | |
| mixed_methods | ✓ | | ✓ | | | | | | | | | ✓ |
| observational_field | ✓ | | | | | | | | | | | |
| case_study | ✓ | | | | ✓ | | | | | | | ✓ |
| interview_study | | | ✓ | | | | | | | | | |
| ethnographic | | | ✓ | | | ✓ | | | | | | |
| grounded_theory | | | ✓ | | ✓ | | | | | | | |
| phenomenological | | | ✓ | | | | | | | | | |
| thought_piece | | | | | | | | ✓ | ✓ | ✓ | | |

---

# APPENDIX B: EXAMPLE — HOW A SINGLE REVIEW PAPER POPULATES THE WEB

**Paper**: Joye & Dewitte (2018), "Nature, aesthetics, and processing fluency" (theoretical/narrative review hybrid)

**Extraction produces**:

1. **THEORETICAL_PROPOSITION**: "Preference for natural environments is driven by processing fluency — natural patterns (fractals, bilateral symmetry) are easier for visual system to process"
   - `ae_confidence: 0.45` (well-argued, some empirical support, but debated)
   - PROPOSES_MECHANISM edge: `natural_pattern → processing_fluency → aesthetic_preference`

2. **DERIVED_HYPOTHESIS**: "Environments with mid-range fractal dimension (D ≈ 1.3) should be maximally preferred because they optimize processing fluency"
   - `testable_via: "fractal dimension manipulation in VR or image sets"`
   - THEORETICALLY_PREDICTS edge from Proposition 1

3. **DERIVED_HYPOTHESIS**: "Individual differences in need for cognition should moderate nature preference (high NFC → less fluency preference)"
   - THEORETICALLY_PREDICTS edge from Proposition 1

4. **SUBSUMES_THEORY edge**: THEORETICAL_PROPOSITION → Kaplan ART (argues fluency account subsumes/explains restoration effects)

5. **THEORY_TENSION edge**: THEORETICAL_PROPOSITION → Ulrich SRT (tension — fluency is cognitive, SRT is affective/evolutionary)

6. **EXPERT_SYNTHESIS**: "Across 12 studies, fractal preference peaks at D ≈ 1.3" (citing Taylor, Spehar, Hagerhall etc.)
   - ATTRIBUTES_FINDING edges to each cited study
   - `evidence_basis: "cited_evidence"`

7. **KNOWLEDGE_GAP**: "No studies test fluency account directly in real buildings"
   - `voi_relevance: "high"`

8. **CONCEPTUAL_DEFINITION**: "Processing fluency = ease with which information is processed by the cognitive system"
   - DEFINES_CONSTRUCT edge to `fluency` construct

This single paper generates ~8 nodes and ~15 edges. Compare to an empirical paper that generates ~4 nodes and ~6 edges. The review paper provides 2.5× more web structure per paper. Multiplied across the ~50% of papers currently producing NO claims, this represents an enormous amount of lost epistemic infrastructure.

---

**END OF SPECIFICATION**
