# ATLAS System: Synthesis of Six Documents and Revised Sprint Plan

**Date**: February 27, 2026
**Status**: Expert Panel Deliberation + Revised Sprint Schedule
**Prepared for**: Professor David Kirsh, UCSD Cognitive Science
**Scope**: Three-part comprehensive synthesis of crashed AG sessions

---

## PART 1: SYNTHESIS OF SIX NEW DOCUMENTS

### Executive Summary

Six documents from crashed AG (agent) sessions revealed major architectural breakthroughs in the ATLAS system. These documents establish:

1. **Canonical discount factors** for all seven warrant types (updated from 2025 values)
2. **Three-layer annotation model** for computational architecture (web molecules, stimulus tags, methodological tags)
3. **Formal defense** of typed edges beyond Pearl's untyped framework
4. **Terminology cheat sheet** resolving the "four credence formulas" problem into three categorically distinct numbers
5. **Log-odds projection formula** for π projection (π: EN → BN bridge)
6. **Six T2 mechanism templates** as computational archetypes

The synthesis addresses critical ambiguities that have persisted since the 2025 workshop. These documents form the basis for Sprint revisions below.

---

### Document 1: EN to BN Rethink (Transcript)

**Source**: `EN to BN rethink.docx` (AG-generated synthesis)

#### Key Technical Findings

**1. Warrant Strength (ω) is Epistemic Confidence, Not Probability**

The document establishes a critical distinction:

- **ω** = "degree of belief in the evidential bridge" (meta-level judgment about evidence quality)
- **NOT** a credence about outcomes
- **NOT** a probability of a phenomenon
- Expressed in (0, 1); updated by evidence about evidence quality

Example: A study on daylight exposure → serotonin may have ω = 0.85 (high quality study, good controls, replicated) but this does NOT mean "85% chance that daylight increases serotonin in this building." The ω judges the study quality; the actual outcome probability is computed by the π projection.

**2. Discount Factor (d) is Type-Based, Not Study-Based**

All evidence of a given warrant type receives the same discount factor:

- Discount factors are structural properties of the evidence type
- They reflect expected invariance range under contextual perturbation (Woodward, 2003)
- They are SET by warrant type, not calibrated per study
- This is foundational to the transportability framework

**3. Canonical Discount Factors (Updated)**

The old 2025 values have been revised upward (except THEORY_DERIVED, which drops significantly):

| Warrant Type | Old (2025) | New (2026) | Δ | Justification |
|---|---|---|---|---|
| CONSTITUTIVE | 0.75 | 0.95 | +0.20 | Identities transfer perfectly; only edge cases discount |
| MECHANISM | 0.60 | 0.80 | +0.20 | Mechanistic pathways robust to context; Woodward invariance |
| EMPIRICAL_ASSOCIATION | 0.60 | 0.80 | +0.20 | Replicated associations robust (by definition); unknown mechanism is the risk, not the association itself |
| FUNCTIONAL | 0.50 | 0.65 | +0.15 | Functions reliable across observed contexts; moderate transfer |
| CAPACITY | 0.45 | 0.55 | +0.10 | Capacities may not be triggered; conservative estimate |
| ANALOGICAL | 0.35 | 0.40 | +0.05 | Cross-domain transfer notoriously fragile; slight upward revision after panel review |
| THEORY_DERIVED | 0.40 | 0.25 | -0.15 | **Major downward revision**: unconfirmed theoretical predictions are weak evidence; 0.25 reflects "speculative" status |

**Rationale for revisions**:
- CONSTITUTIVE through FUNCTIONAL: Woodward's invariance framework (Woodward, 2003) shows mechanistic knowledge is more robust than previously estimated
- EMPIRICAL_ASSOCIATION: Replication itself provides robustness; unknown mechanism is confound risk, not transfer risk
- THEORY_DERIVED: Down from 0.40 because theoretical predictions are notoriously context-sensitive; set to represent "promising but unconfirmed"

**4. π Projection Formula (Log-Odds Basis)**

The projection function π translates EN credences to BN conditional probabilities:

```
logit(p_target) = d(τ) · ω · δ(pop, pop_target) · logit(p_lab)
```

Where:
- **d(τ)**: Discount factor for warrant type τ
- **ω**: Warrant strength (epistemic confidence in this specific evidence)
- **δ(pop, pop_target)**: Population transfer factor (between source and target samples)
- **logit(p_lab)**: Source (laboratory) outcome in log-odds form
- **Result**: Converted back to probability via sigmoid

**Multi-edge aggregation**:
When multiple edges support the same claim:
```
logit(p_target) = Σ_i d_i · ω_i · δ_i · logit(p_lab,i)
```

Sum log-odds contributions; convert result back to probability.

**Path composition** (serial chains):
For a chain of edges e₁, e₂, ..., eₙ:
```
d_eff = min(d(τ(e₁)), d(τ(e₂)), ..., d(τ(eₙ)))
```

The weakest link dominates. This prevents claiming stronger transfer reliability than any single link supports.

**5. Warrant Type Tagging**

- **MECHANISM edges** carry the tag `"MECHANISM"`
- **THEORY_DERIVED edges** carry an explicit theory tag (e.g., `"THEORY_DERIVED[Predictive_Processing]"`)
- This enables query-based updates: if Predictive Processing theory is challenged, all dependent edges can be updated as a class
- Auditability: Every edge traces to a named source (mechanism name or theory name)

---

### Document 2: Aesthetics Molecules (CNfA Aesthetics Appraisal)

**Source**: `CNfA_Aesthetics_Appraisal_Master.md` (AG-generated complete synthesis)

#### Key Architectural Findings

**1. Three-Layer Annotation Model**

The document identifies a clean separation between what belongs in the computational web and what belongs in external annotation layers:

**Layer 1: Web Molecules/T1.5 Theories** (In web)
- T1.5 computational structures modeling domain-specific mechanisms
- Example: ProcessingFluency, ComplexityRegulation, ThreatSafety (aesthetics domain)
- These are actual nodes/edges in the Epistemic Network
- They represent substantive mechanistic claims

**Layer 2: Stimulus Feature Tags** (On studies, not in web)
- Tags describing experimental stimuli: symmetry, clutter, entropy, fractal dimension, spatial frequency, curvature, depth variance, enclosure, horizon visibility, natural ratio, material warmth, reconstruction error
- These are properties of the study context, not of the computational web
- They annotate papers/claims, enabling downstream filtering by feature type

**Layer 3: Methodological/DV Tags** (On studies)
- Tags describing how dependent variables were measured and context
- Example: "behavioral_approach_probability", "dwell_time", "physiological_cortisol", "self_report_pleasure"
- These enable aggregation by measurement type when computing meta-analytic priors

**Implication for architecture**: Most aesthetic factors previously considered for the web (e.g., "beauty", "elegance", "visual pleasure") belong in Layer 3 or Layer 2, not Layer 1. They are emergent outcomes, not computational primitives.

**2. Six T2 Mechanism Templates (Computational Archetypes)**

The document identifies six computational patterns that recur across domains:

| Template | Definition | Example (Aesthetics) | Example (Other) |
|---|---|---|---|
| **Predictive Coding** | Prediction error minimization via forward/backward models | Moderate complexity minimizes cortical prediction error → aesthetic preference | Visual perception (Friston, 2010) |
| **Homeostatic Regulation** | Arousal/activation maintained within optimal range via feedback | Symmetry increases processing fluency (optimal encoding demand) | Thermal comfort, circadian rhythm |
| **Accumulation to Bound** | Evidence accumulation until threshold triggers decision | Preference emerges as perceptual evidence accumulates over exposure time | Reach-to-grasp timing, lexical decision |
| **Competitive Selection** | Winner-take-all or softmax choice between alternative representations | Aesthetic preference emerges from competition between salient features | Attentional selection, saccade planning |
| **Gated Propagation** | Modulatory signal controls information flow through pathway | Arousal state gates whether aesthetic preference → approach behavior | Autonomic regulation, working memory |
| **Convergent State Monitoring** | Multiple sensors converge on shared representational target (new) | Multiple stimulus dimensions (symmetry, naturalness, safety) converge on "perceived restorativeness" | Pain perception, emotion categorization |

**Significance**: These templates are NOT new theories; they are computational primitives that can be composed and parameterized. They provide a grammar for building mechanistic explanations.

**3. T1.5 Instance Catalog**

The document catalogs 22 T1.5 instances across the aesthetics and broader neuroscience domains:
- Each has a formal definition, measurable parameters, and identified mechanism
- Examples: ProcessingFluency, ComplexityRegulation, ThreatSafety, Restorativeness, AffordanceFit, SocialSignaling (aesthetics); AttentionRestoration, BiophilicPreference, CircadianAlignment (multimodal)

**4. Processing Fluency as Genuine Monitoring Node**

The document establishes that processing fluency is NOT epiphenomenal:
- It integrates three independent signals: prediction error (predictive coding), perceptual organization complexity (Gestalt principles), metabolic cost (metabolic efficiency trade-off)
- It has causal consequences: fluency influences approach behavior, aesthetic judgment, and memory encoding
- It should be represented as a T1.5 node in the web, with inputs from multiple stimulus features and outputs to affective states and behavioral dispositions

---

### Document 3: Pearl Typed Edges V2.0 (Transcript)

**Source**: `02-26_02_Addressing_Pearl_Typed_Edges_V2.0.docx` (AG-generated comprehensive defense)

#### Key Philosophical & Formal Findings

**1. Pearl's Framework Handles Computation; EWG Handles Epistemology**

The document articulates a clear division of labor:

- **Pearl's Structural Causal Model (SCM)** with do-calculus excels at answering interventional questions in a specific domain with known structure
- **EWG (Epistemic Web Graph)** excels at representing cross-domain, cross-context evidence transfer where structure is uncertain
- They are not competitors; they answer different questions
- A single ATLAS application may use both: EWG to assess transferability of evidence, SCM to predict outcomes in a specific building

**2. Woodward's Invariance as Justification for Discount Ordering**

The document grounds the seven warrant types in Woodward's (2003) concept of invariance:

- **Constitutive (d = 0.95)**: Identities are maximally invariant (true in all contexts by definition)
- **Mechanism (d = 0.80)**: Mechanistic knowledge is highly invariant (holds wherever the mechanism is intact)
- **Empirical_Association (d = 0.80)**: Replicated associations have demonstrated robustness
- **Functional (d = 0.65)**: Functional claims are moderately invariant (function may not be exercised in new context)
- **Capacity (d = 0.55)**: Capacities are context-dependent (may not be triggered in target context)
- **Analogical (d = 0.40)**: Analogical transfer is fragile (depends on structural similarity which is itself uncertain)
- **Theory_Derived (d = 0.25)**: Untested theoretical predictions are minimally invariant

This ordering reflects a defensible philosophical principle, not arbitrary calibration.

**3. Five Key Capabilities Enabled by Typed Edges**

- **Targeted acquisition**: Know which warrant types are missing and seek evidence accordingly
- **Differential sensitivity**: Different models and applications may weight warrant types differently (e.g., a regulatory compliance model weights empirical association heavily; a novel application weights mechanism heavily)
- **Confound assessment**: EMPIRICAL_ASSOCIATION edges are flagged as potentially confounded; helps guide subsequent mechanistic research
- **Audit trail**: Every claim in BN traces to a typed edge in EN; transparency for stakeholders
- **Graceful degradation**: If theoretical knowledge fails, system can revert to empirical associations; if mechanisms are disrupted, system degrades gracefully

**4. S-Node Placement Guided by Warrant Types**

Pearl's "selection node" (S-node) concept maps naturally to warrant types:

- If a claim rests on a MECHANISM edge, the S-node should be placed at the point where the mechanism could be disrupted
- If a claim rests on an EMPIRICAL_ASSOCIATION edge without known mechanism, S-node placement is uncertain (because we don't know what confound to worry about)
- If a claim rests on a THEORY_DERIVED edge, S-nodes should represent the assumptions of the theory

This provides concrete guidance for transportability analysis.

**5. Context-Sensitive BN Generation via π**

The π projection function enables different Bayesian Networks for different contexts:

- Same EN (evidence base) can project to different BNs depending on target population, building characteristics, intervention scope
- Enables "adaptive BNs" that scale evidence to specific applications
- Avoids false universalism (pretending laboratory BN applies everywhere) while maintaining epistemically grounded reasoning

**6. The Causal Hierarchy Theorem (CHT) Demands Something Like EWG**

The document argues that Pearl's own causal hierarchy (associational, interventional, counterfactual) actually REQUIRES something like the EWG:

- Moving from associational to interventional claims requires asserting causal structure
- Moving from interventional to counterfactual claims requires mechanistic understanding
- EWG explicitly represents which warrants support which claims in the hierarchy
- Without EWG, applied scientists have no systematic way to assess whether they are making claims they can actually support

---

### Document 4: ATLAS Terminology Cheat Sheet V1.0

**Source**: `02-27_03_ATLAS_Terminology_Cheat_Sheet_V1.0.docx` (AG-generated canonical reference)

#### Key Clarity Findings

**1. The "Four Credence Formulas" Problem is Resolved**

Previous confusion: The codebase appeared to have four competing formulas for computing credences:
1. Bridge warrant formula (π projection)
2. Coherentist formula (Quine-style mutual support)
3. Bayesian network formula (conditional probability)
4. Classical credence formula (some hybrid)

**Resolution**: There are NOT four formulas. There are THREE categorically different numbers:

| Number | Location | Meaning | Updates | Domain |
|---|---|---|---|---|
| **ω** (warrant strength) | Epistemic Network, on edges | Degree of belief in THIS evidence's quality | By evidence about evidence quality; coherentist updating | Epistemic layer |
| **d** (discount factor) | Projection bridge | How much of THIS WARRANT TYPE survives transfer | SET by warrant type; not calibrated | Epistemic layer |
| **CPT** (conditional probability) | Bayesian Network, on edges | What actually happens in the world | By Bayesian learning from outcomes | Aleatory layer |

These are not in competition. They play different roles:

- **ω** answers: "Is this evidence solid?" (Epistemology)
- **d** answers: "Will this type of evidence transfer to the target context?" (Transportability)
- **CPT** answers: "What is the probability of outcome Y given inputs X in this context?" (Prediction)

The π projection combines ω and d to generate CPT:
```
logit(CPT_target) = d · ω · δ · logit(p_lab) → sigmoid(result)
```

**2. Confounds, Interactions, and Theory vs. Mechanism Appear Differently in Each Layer**

- **In the EN**: Confounds are represented as missing edges or questionable edges; mechanistic knowledge is represented as chains through intermediate nodes
- **In the BN**: Confounds are represented as common causes (v-structures); mechanistic knowledge is represented as linear causal chains
- **In the bridge (π)**: Theory-derived claims have lower d; empirical associations acknowledge confound risk without knowing which confound

The same phenomenon looks different depending on which layer you examine.

**3. BN is a Strict Subset of EN After Projection**

- EN can have cycles, parallel edges, and typed edges
- π projects to a directed acyclic graph (the BN)
- Some edges drop out (e.g., mutual support edges that don't contribute to causal structure)
- The BN is sparser and more computationally tractable than the EN
- But the EN remains as the epistemic justification for what remains in the BN

**4. Three Layers Clarified**

The cheat sheet provides clean definitions:

- **Layer 1 (EN)**: Epistemic structure. Propositions, typed edges, warrant strengths. What we know and why.
- **Layer 2 (π bridge)**: Projection/transfer layer. Discount factors, population adjustment, transformations.
- **Layer 3 (BN)**: Operational structure. Variables, conditional probabilities, inference.

Each layer answers different stakeholder questions:
- Scientists care about Layer 1 (evidence quality)
- Engineers care about Layer 3 (predictions)
- Applied epistemologists care about Layer 2 (why we trust the projection)

---

### Document 5: create_master.js

**Source**: `create_master.js` (AG-generated docx-js implementation)

#### Key Implementation Findings

**1. The Script Generates the Terminology Cheat Sheet as Formatted DOCX**

The script uses docx-js library to produce a professionally formatted Word document with:
- Consistent heading hierarchy (H1, H2, H3)
- Tables with proper borders and shading
- Proper spacing and indentation
- Georgia font, academic formatting
- ~500 lines of JavaScript, highly parameterized

**2. Confirms Canonical Status of Key Concepts**

By encoding the terminology cheat sheet as generative code (rather than manual document), the script establishes:
- These definitions are maintainable and versionable
- They can be regenerated with updated values (e.g., if discount factors change)
- They form the authoritative reference for the system

**3. Generative Documentation Pattern**

The script demonstrates that documentation can be code-generated from data structures, enabling:
- Single source of truth (update the data, regenerate the document)
- Automated consistency checking
- Easy updates when system architecture changes

---

### Document 6: Pearl Typed Edges V2.0 variant (1)

**Source**: `02-26_02_Addressing_Pearl_Typed_Edges_V2.0 (1).docx` and (2).docx

**Finding**: These are earlier versions of Document 3 with no significant new content beyond the comprehensive defense. They establish the robustness of the framework but do not introduce new technical innovations.

---

## PART 2: EXPERT PANEL DELIBERATIONS

### Panel A: Formal Architecture (π Projection + Discount Factors)

**Panelists**: Pearl, Woodward, Cartwright, Spohn, Cooke

**Chair**: Claude Opus 4.6 (Anthropic)

#### Background

The six documents present a dramatically revised set of discount factors and establish the π projection formula with mathematical rigor. Panel A must decide whether to adopt these revisions and how to implement them in code.

---

#### DECISION A1: Adopt New Canonical Discount Factors

**Question**: Should the codebase adopt the new discount factors from the EN-to-BN rethink?

**Current (2025)**: CONSTITUTIVE=0.75, MECHANISM=0.60, EC=0.60, FUNCTIONAL=0.50, CAPACITY=0.45, TD=0.40, ANALOGICAL=0.35

**Proposed (2026)**: CONSTITUTIVE=0.95, MECHANISM=0.80, EA=0.80, FUNCTIONAL=0.65, CAPACITY=0.55, ANALOGICAL=0.40, TD=0.25

**Panel Deliberation**

*Pearl*: The proposed values are grounded in invariance analysis, which is exactly what transportability theory recommends. The upward revision of MECHANISM and EMPIRICAL_ASSOCIATION reflects my own work (Pearl & Bareinboim, 2014) showing that replicated associations are indeed robust to many contextual changes. The dramatic downward revision of THEORY_DERIVED (0.40 → 0.25) is philosophically defensible—untested theoretical predictions are notoriously fragile. **Vote: YES**.

*Woodward*: The ordering of discount factors by invariance range is sound. Mechanistic knowledge has genuine invariance properties; identities are maximally invariant by definition. The small discount on CONSTITUTIVE (0.95 instead of 1.0) is wise—edge cases do occur. One concern: Are these values calibrated to specific domains (environmental psychology, architecture) or are they meant to be universal? **Query: Scope of universality?**

*Cartwright*: I have always insisted that mechanisms are not as transferable as statisticians assume. The new framework acknowledges this by setting MECHANISM = 0.80, not 1.0. Empirical associations should not be discounted merely because mechanisms are unknown—that conflates confounding risk with transfer risk. The new framework distinguishes these clearly. The downward revision of THEORY_DERIVED is essential; I have spent forty years showing that theoretical predictions fail in new domains. **Vote: YES with caveat**.

*Spohn*: From a ranking theory perspective, these discount factors can be interpreted as updates to comparative belief orderings. The multiplicative structure (d · ω · δ) is well-founded in information-theoretic accounts. The specific numerical values are empirical calibrations; the philosophical structure is sound. **Vote: YES, with recommendation for sensitivity analysis**.

*Cooke*: I want to see the calibration sources. Where does d_MECHANISM = 0.80 come from? Is this a consensus expert judgment, or does it rest on specific empirical analyses? For structured expert judgment, we need to document the basis. That said, the framework is coherent and the values are defensible. **Vote: YES, conditional on proper documentation**.

**Consensus Decision**: ADOPT new discount factors, effective in Sprint 1.

**Dissenting views**: Cartwright noted that domain variation may require local adjustments (e.g., architectural psychology may have different transfer properties than medical interventions). Woodward emphasized the need for explicit documentation of universality assumptions.

**Risk level**: MEDIUM. Impact is widespread (affects all π projections); mitigation is backward-compatibility layer (preserve old values for comparison during transition period).

**Implementation implications**:
- Create `src/models/warrant_types.py` enum with updated discount factors
- Maintain old values in deprecated field for comparison
- Update all π projection computations to use new d values
- Add "discount factor source" field to warrant type documentation
- Implement sensitivity analysis: show BN outputs with old vs. new discount factors

---

#### DECISION A2: Refactor "Four Credence Formulas" as "Three Numbers" Implementation

**Question**: Should Sprint 1 be renamed and reimplemented to separate ω, d, and CPT throughout the codebase?

**Current problem**: Bridge warrants conflate warrant strength with discount factor. The code has variables like `DEFAULT_BRIDGE_CONFIDENCE` that mix epistemic and operational concerns.

**Proposed change**: Explicitly separate:
- ω (warrant strength): computed during evidence assessment, stored on EN edges
- d (discount factor): set by warrant type, not calibrated per edge
- CPT (conditional probability): computed by π projection, stored on BN edges

**Panel Deliberation**

*Pearl*: This separation is essential for transportability. In my framework, confounders must be disentangled from causal structure. Here, ω and d must be disentangled from outcome probabilities. The three-number framework does exactly that. **Vote: YES, rename to "Three-Number Separation"**.

*Woodward*: More fundamentally, this reflects the distinction between epistemic reliability (ω) and structural invariance (d). They answer different questions. Confusing them is a common error in applied causal inference. **Vote: YES, strong support**.

*Cartwright*: I approve strongly. This prevents claims like "Well, the warrant strength is 0.75, so..." when warrant strength says nothing about transfer, only about evidence quality. **Vote: YES**.

*Spohn*: The terminology matters. If we call the bridge warrant "confidence" without distinguishing epistemic from aleatoric, we invite confusion. The new separation is terminologically cleaner. **Vote: YES**.

*Cooke*: What happens to existing code that uses `DEFAULT_BRIDGE_CONFIDENCE`? Do we deprecate it or refactor in place? **Query: Backward compatibility strategy?**

**Consensus Decision**: IMPLEMENT full three-number separation in Sprint 1.

**Implementation implications**:
- Refactor `bridge_warrants.py`: separate warrant strength computation from discount factor application
- Create new module `projection_bridge.py` with explicit π projection formula
- Update all BN CPT generation to use π formula: `logit(CPT) = d · ω · δ · logit(p_lab)`
- Audit codebase for variables conflating the three numbers
- Add type hints: `WarrantStrength`, `DiscountFactor`, `ConditionalProbability` as distinct types
- Write documentation: "Three Numbers" reference guide

**Risk level**: MEDIUM-HIGH. Affects many code paths; refactoring is pervasive.

**Mitigation**: Extensive test coverage for π projection; cross-validate against old formulas during transition.

---

#### DECISION A3: Implement Log-Odds π Projection Formula

**Question**: How and where should the π projection be implemented?

**Formula to implement**:
```
logit(p_target) = d(τ) · ω · δ(pop, pop_target) · logit(p_lab)
p_target = sigmoid(logit(p_target))
```

**Multi-edge case** (convergent evidence):
```
logit(p_target) = Σ_i d_i · ω_i · δ_i · logit(p_lab,i)
```

**Serial case** (chain of evidence):
```
d_eff = min(d_i)  [then proceed as single-edge]
```

**Location options**:
- A) Extend `bridge_warrants.py`
- B) New module `projection_bridge.py`
- C) New module `epistemic_projection.py` (more general namespace)

**Panel Deliberation**

*Pearl*: The log-odds formulation is the right choice. It correctly implements the composition of independent evidence. I recommend a dedicated module, not buried in existing code. **Preference: Option B or C**.

*Woodward*: The minimum-discount composition rule for serial paths is conservative and defensible. Make it explicit in code and documentation. **Support: dedicated module**.

*Cartwright*: The summation of log-odds is correct for parallel evidence. This is standard in information theory. I want to see explicit tests for all three cases (single edge, convergent, serial). **Vote: dedicated module**.

*Spohn*: Consider efficiency. Log-odds computation is fast, but if we have thousands of beliefs with multiple edges, repeated sigmoid calculations could be expensive. Implement with lazy evaluation. **Concern: computational efficiency**.

*Cooke*: This formula is right, but the input data (p_lab, δ values, ω values) must be carefully validated. Garbage in, garbage out. Recommend strict type checking and input validation. **Concern: data quality**.

**Consensus Decision**: IMPLEMENT in new dedicated module `src/services/epistemic_projection.py` with explicit handling of three cases (single, convergent, serial).

**Implementation implications**:
- Create `epistemic_projection.py` with:
  - `class ProjectionBridge`: main coordinator
  - `def single_edge_projection()`: single warrant
  - `def convergent_projection()`: multiple independent edges (Σ log-odds)
  - `def serial_projection()`: chain of evidence (min discount)
  - `def compute_population_transfer_factor()`: δ calculation
- Add input validation and error handling
- Implement lazy evaluation for sigmoid to avoid recomputation
- Add comprehensive tests (at least 20 test cases covering boundary conditions)
- Document formula explicitly with APA references (Jaynes 2003, Der Kiureghian & Ditlevsen 2009)

**Risk level**: MEDIUM. Formula is mathematically sound, but implementation must be correct; test coverage is essential.

---

#### DECISION A4: Handle EMPIRICAL_COVARIANCE → EMPIRICAL_ASSOCIATION Rename

**Question**: How should the rename be managed?

**Issue**: Existing database records, enums, and code reference `EMPIRICAL_COVARIANCE`. Changing to `EMPIRICAL_ASSOCIATION` affects:
- Enum `WarrantType` (need to update)
- Database schema (need migration)
- Backward compatibility with existing template JSONs
- Documentation and external stakeholders

**Options**:
- A) Clean break: Rename everywhere, update migrations, require manual data update
- B) Enum alias: Keep both names in enum, deprecate old name
- C) Gradual migration: Add new field, deprecate old field, migrate over time

**Panel Deliberation**

*Pearl*: Clean break is better than carrying dead code. But do it correctly with clear communication. **Preference: Option A**.

*Woodward*: The term "association" is more accurate (epidemiological term of art). I support the rename. **Vote: Option A or B**.

*Cartwright*: "Association" is clearer; it signals "relationship, not necessarily causal." I support the rename. **Vote: Option A**.

*Spohn*: From a maintenance perspective, clean break avoids technical debt. We can provide a simple migration script. **Vote: Option A**.

*Cooke*: Will other teams or external users be affected? What's the communication plan? **Query: stakeholder impact?**

**Consensus Decision**: CLEAN BREAK (Option A) with comprehensive migration plan.

**Implementation implications**:
- Sprint 0: Create migration `024_rename_empirical_covariance_to_association.sql`
  - Add new enum value `EMPIRICAL_ASSOCIATION`
  - Migrate all records: `UPDATE warrant_edges SET warrant_type = 'EMPIRICAL_ASSOCIATION' WHERE warrant_type = 'EMPIRICAL_COVARIANCE'`
  - Drop old enum value (or keep as deprecated in database for audit trail)
- Sprint 1: Update Python code
  - Update `WarrantType` enum
  - Update all imports and references
  - Update template JSONs in data/theories/
- Documentation: Create migration guide `docs/EMPIRICAL_COVARIANCE_RENAME_MIGRATION_GUIDE.md`
- Communication: Email to stakeholders with migration timeline

**Risk level**: LOW. Straightforward rename with clear migration path.

---

### Panel B: Computational Architecture (Molecules + Templates + Tags)

**Panelists**: Thagard, Haack, Clark (predictive processing), Chemero (ecological), Friston (free energy)

**Chair**: Claude Opus 4.6 (Anthropic)

#### Background

The aesthetics documents and CNfA analysis establish a three-layer annotation model and six T2 mechanism templates. Panel B must decide how to formalize these in the codebase.

---

#### DECISION B1: Formalize T2 Mechanism Templates in Code

**Question**: How should the six T2 templates be represented in the codebase?

**Templates identified**:
1. Predictive Coding
2. Homeostatic Regulation
3. Accumulation to Bound
4. Competitive Selection
5. Gated Propagation
6. Convergent State Monitoring (new)

**Options**:
- A) Enum: `T2Template { PREDICTIVE_CODING, HOMEOSTATIC_REGULATION, ... }`
- B) Schema/configuration: YAML/JSON schema describing template parameters
- C) Data class hierarchy: Base class `T2Template` with subclasses for each archetype
- D) No formal representation yet; document as reference

**Panel Deliberation**

*Thagard*: These are real computational primitives. They should be formalized. I recommend a data class hierarchy (Option C) so that concrete instantiations can inherit from template and override parameters. **Vote: Option C**.

*Haack*: From a coherentist perspective, the templates are nodes in a web of mechanistic explanations. They help explain why specific mechanisms work. An enum (Option A) is too coarse; a schema (Option B) is better than nothing. But Option C enables the most epistemically useful representation. **Vote: Option C**.

*Clark*: These templates map to predictive processing architectures. Predictive Coding and Gated Propagation are central in active inference theory. Formalizing them as data classes allows us to reason about their properties formally. **Vote: Option C, with type parameters for inputs/outputs**.

*Chemero*: Ecological psychology also recognizes these templates (especially Affordance Fit and Convergent State Monitoring). A data class hierarchy allows domain-specific subclasses. **Vote: Option C**.

*Friston*: The Free Energy Principle unifies these templates under the umbrella of surprise minimization. A formal representation enables showing how each template reduces free energy. **Vote: Option C, with free energy annotations**.

**Consensus Decision**: FORMALIZE as data class hierarchy with enum registry.

**Implementation implications**:
- Create `src/models/mechanism_templates.py`:
  ```python
  @dataclass
  class T2Template:
      name: str
      template_type: T2TemplateType  # enum
      description: str
      mechanism_stage: str  # Which cognitive process?
      input_variables: list[str]  # What it takes as input
      output_variables: list[str]  # What it produces
      parameters: dict  # Tunable parameters
      theoretical_basis: str  # Which theories justify this?
      calibration_sources: list[str]  # Where did we get these values?

  @dataclass
  class PredictiveCodingTemplate(T2Template):
      prediction_error_weight: float = 0.7
      precision_weighting: bool = True
      hierarchy_depth: int = 3

  # ... subclasses for other templates
  ```
- Create template registry in `src/data/mechanism_templates.json`
- Update template validation to check that concrete instances reference valid T2 templates
- Add tests for template instantiation and parameter validation

**Risk level**: LOW. Non-breaking change; templates are additive.

---

#### DECISION B2: Implement Three-Layer Annotation Model

**Question**: How should the three-layer model be implemented in the database and extraction pipeline?

**Layers**:
1. **Web layer** (EN nodes/edges): Propositions, mechanisms, T1.5 theories
2. **Stimulus tag layer**: Features of stimuli (symmetry, clutter, entropy, ...)
3. **Methodological tag layer**: How DVs measured (behavioral, physiological, self-report), context

**Implementation options**:
- A) Database-level: Separate tables `stimulus_features`, `methodological_tags`; join on claim records
- B) Schema-level: Add `stimulus_tags` and `method_tags` arrays to existing claim schema
- C) Service-level: TaggingService that manages both layers without schema changes

**Panel Deliberation**

*Thagard*: Conceptually, these layers are distinct epistemically. Stimulus tags are about what was measured (design description); methodological tags are about how it was measured (measurement description). They should be separate in the schema. **Vote: Option A**.

*Haack*: The web layer is evaluative/coherentist; the tag layers are descriptive. Separating them maintains that conceptual distinction in the database. **Vote: Option A**.

*Clark*: Tags enable flexible filtering and aggregation. If a researcher wants to "find all studies measuring approach behavior with aesthetic stimuli varying in symmetry," the tags must be queryable. Separate tables enable efficient SQL queries. **Vote: Option A**.

*Chemero*: From an affordances perspective, the stimulus layer describes what the environment offers; the web layer describes how the organism responds. They are genuinely different kinds of information. **Vote: Option A**.

*Friston*: The tags are observational data about the experimental setup; the web layer is theoretical interpretation. This is the familiar data/model distinction in Bayesian inference. Separate representation makes that distinction explicit. **Vote: Option A**.

**Consensus Decision**: IMPLEMENT as database-level separation with dedicated tables.

**Implementation implications**:
- Create migration `025_add_stimulus_and_methodological_tags.sql`:
  - `stimulus_features` table: `(id, claim_id, feature_name, feature_value, measurement_type, source_paper)`
    - Features: symmetry, clutter, entropy, fractal_dimension, spatial_frequency, curvature, depth_variance, enclosure, horizon_visibility, natural_ratio, material_warmth, reconstruction_error
  - `methodological_tags` table: `(id, claim_id, tag_name, tag_value, coding_reliability, notes)`
    - Tags: behavioral_approach, behavioral_avoidance, dwell_time, reaction_time, pupil_dilation, heart_rate, cortisol, skin_conductance, self_report_pleasure, self_report_interest, fmri_activation, etc.
- Update extraction pipeline:
  - PDF extraction → identifies stimulus features from paper description
  - Extraction → extracts methodological tags (how DV measured)
  - Both stored separately from web propositions
- Update `claim_v2.schema` to remove stimulus/method fields (now in separate tables)
- Add query service for finding claims by feature combinations

**Risk level**: MEDIUM-HIGH. Schema changes are non-trivial; requires data migration on existing claims.

**Mitigation**: Write comprehensive migration tests; validate that all extracted claims have proper tags.

---

#### DECISION B3: Add Processing Fluency as Monitoring Node

**Question**: Should processing fluency be formalized as a T1.5 computational node?

**Argument for**: Processing fluency integrates three independent signals (prediction error, perceptual organization, metabolic cost) and has causal consequences (affects approach, aesthetics, memory). It is not epiphenomenal.

**Argument against**: Fluency is a summary statistic over other processes, not a primitive. Adding it creates redundancy.

**Panel Deliberation**

*Thagard*: In cognitive coherentism, monitoring nodes represent the system's "sense of" its own processing state. Fluency does exactly that. It is not a primitive but a integrator; integrators are legitimate nodes. **Vote: YES**.

*Haack*: Coherence is best understood as a holistic property. Fluency represents the local coherence signal—how smoothly inputs are integrating. This is genuinely computational. **Vote: YES**.

*Clark*: In predictive processing, fluency signals prediction error magnitude. High fluency = low prediction error = high confidence in current model. This is foundational. **Vote: YES, strongly**.

*Chemero*: From ecological psychology, fluency signals affordance recognition—"this environment is readable and navigable." It is more than a summary; it is information about the environment-organism fit. **Vote: YES**.

*Friston*: Processing fluency is a proxy for free energy in the moment. Organisms minimize free energy partly by seeking fluent processing states. This is causal, not epiphenomenal. **Vote: YES, strongly**.

**Consensus Decision**: ADD processing fluency as formal T1.5 node.

**Implementation implications**:
- Create T1.5 theory: `data/theories/processing_fluency.json`
- Define inputs: prediction_error, perceptual_organization_cost, metabolic_cost_rate
- Define outputs: fluency_signal (0–1), approach_probability, attention_allocation
- Link to three T2 templates: Predictive Coding (input), Homeostatic Regulation (mediation), Gated Propagation (output)
- Update aesthetics template library to include processing_fluency as core node
- Add 5–10 calibration studies showing fluency's causal role

**Risk level**: LOW. Additive change; does not affect existing structure.

---

#### DECISION B4: Integrate Three-Layer Model with Existing Sprint Plan

**Question**: How do the three-layer model and T2 templates affect the current sprint schedule?

**Current plan** (from SPRINT_PLAN_SETUP_AND_OVERSEER_2026-02-25.md):
- Sprint 0: Metadata enrichment
- Sprint 1: Setup function
- Sprint 2: OVERSEER core
- Sprint 3: Coherence dashboard
- Sprint 4: Argumentation graph
- Sprint 5: Nightly batch
- Sprint 6: Expert calibration prep

**Panel Deliberation**

*Thagard*: The three-layer model is foundational to the extraction and integration pipelines. It should be in the critical path. Recommend adding as Sprint 0.5 (schema setup) before Sprint 1 (setup function). **Vote: Reorder**.

*Haack*: T2 templates are less critical—they are governance/quality tools, not infrastructure. They can be in a parallel sprint or post-Sprint-6. **Vote: Defer to parallel or Sprint 7**.

*Clark*: The annotation layers must be in place before extraction and integration. Otherwise, the integration pipeline has no way to tag stimuli and methods. **Vote: Critical path**.

*Chemero*: Agree. The tags enable the adaptive BN generation that Clark mentioned. Critical path. **Vote: Critical path**.

*Friston*: T2 templates are governance; important but not blocking. The annotation model is infrastructure; critical. **Vote: annotation model critical, templates parallel**.

**Consensus Decision**:
- Add ANNOTATION_MODEL (schema + extraction hooks) to critical path as **Sprint 0.5**
- Add T2_TEMPLATES (formalization + quality governance) as **parallel Sprint** or **Sprint 7** (post-deployment)

**Revised Sprint Schedule**:

| Sprint | Name | Criticality | Duration | Dependencies |
|---|---|---|---|---|
| 0 | Metadata Enrichment | CRITICAL | 30 min | None |
| 0.5 | Three-Layer Annotation Model | CRITICAL | 2 hrs | Sprint 0 |
| 1 | Setup Function | CRITICAL | 4 hrs | Sprint 0.5 |
| 2 | OVERSEER Core | CRITICAL | 3 hrs | Sprint 1 |
| 3 | Coherence Dashboard | HIGH | 2 hrs | Sprint 2 |
| 4 | Argumentation Graph | HIGH | 2 hrs | Sprint 1 |
| 5 | Nightly Batch | HIGH | 2 hrs | Sprint 2 |
| 6 | Expert Calibration Prep | HIGH | 2 hrs | Sprint 5 |
| 7 | T2 Templates & Governance | MEDIUM | 3 hrs | Sprint 1 |

---

## PART 3: REVISED SPRINT PLAN

### Overview

Based on panel deliberations, the existing 6-sprint plan is revised into 8 sprints with updated scope and content. The revisions address:

1. **Rename Sprint 1**: From "credence unification" to "three-number separation"
2. **Add Sprint 0.5**: Schema and extraction hooks for three-layer annotation model
3. **Upgrade Sprint 2**: π projection formula implementation and discount factor updates
4. **Add Sprint 7**: T2 template formalization (can run in parallel with earlier sprints)
5. **Consolidate discount factor updates**: Distributed across Sprints 1–2

**Total duration**: ~20–22 hours engineering + ~4 hours expert calibration = ~24–26 hours (revised from 18–20 hours, due to annotation model and refactoring scope)

**Target completion**: March 2–5, 2026 (revised from Feb 25–Mar 3)

---

### Sprint 0: Metadata Enrichment (30 minutes)

**Target Date**: 2026-02-25 (already complete in Session 8)

**Status**: VERIFIED

No changes from original plan. See `SPRINT_PLAN_SETUP_AND_OVERSEER_2026-02-25.md` §Sprint 0.

---

### Sprint 0.5: Three-Layer Annotation Model (NEW CRITICAL SPRINT, 2 hours)

**Target Date**: 2026-02-27 (today, or Feb 28)

**Dependencies**: Sprint 0 (citation graph)

**Objective**: Establish database schema and extraction hooks for three-layer model (web, stimulus tags, methodological tags).

#### Files Affected

**New files**:
- `migrations/025_add_stimulus_and_methodological_tags.sql` (100 lines)
- `src/services/tag_engine.py` (250 lines) — manages stimulus and methodological tag lifecycle

**Modified files**:
- `src/services/paper_integration/orchestrator.py` — add Step 3.5 (tag assignment)
- `src/services/pdf_extraction_module.py` — extract stimulus features from full text

**Schema Changes**:
```sql
-- Stimulus features layer
CREATE TABLE stimulus_features (
    id UUID PRIMARY KEY,
    claim_id UUID NOT NULL REFERENCES claims(id),
    feature_name VARCHAR(100) NOT NULL,  -- symmetry, clutter, entropy, ...
    feature_value FLOAT,  -- measured value
    feature_discrete VARCHAR(50),  -- discrete category if applicable
    measurement_type VARCHAR(50),  -- computed, reported, inferred
    confidence FLOAT,  -- 0–1, how confident in tag
    source_paper VARCHAR(200),  -- which paper described it
    created_at TIMESTAMP,
    FOREIGN KEY (claim_id) REFERENCES claims(id) ON DELETE CASCADE
);

-- Methodological tags layer
CREATE TABLE methodological_tags (
    id UUID PRIMARY KEY,
    claim_id UUID NOT NULL REFERENCES claims(id),
    tag_name VARCHAR(100) NOT NULL,  -- behavioral_approach, dwell_time, fmri_activation, ...
    tag_category VARCHAR(50),  -- behavioral, physiological, neuroimaging, self_report
    tag_value VARCHAR(200),  -- How measured? Units?
    coding_reliability FLOAT,  -- 0–1, coder agreement
    notes TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (claim_id) REFERENCES claims(id) ON DELETE CASCADE
);

CREATE INDEX idx_stimulus_feature_name ON stimulus_features(feature_name);
CREATE INDEX idx_tag_name ON methodological_tags(tag_name);
```

#### Specific Tasks

| Task | What Changes | Acceptance Criterion |
|---|---|---|
| Create migration script | New migration 025 | Runs cleanly; creates both tables with proper indexes |
| Create TagEngine service | New `tag_engine.py` | Can assign stimulus tags and methodological tags; tests pass |
| Extract stimulus features from PDFs | Modify `pdf_extraction_module.py` | Extracts 8+ stimulus feature types from paper; stores with confidence |
| Wire tag assignment into integration pipeline | Modify `orchestrator.py` | Step 3.5 executes after Step 3 (provenance); tags accessible in BN |
| Update `claim_v2.schema` | Remove old stimulus/method fields from schema; replace with foreign key refs | Schema validation passes; old fields deprecated |
| Write TagEngine tests | 8–10 test cases | 100% pass rate on tag CRUD, validation, query |

#### Key Design Decisions

**D0.5.1**: Should stimulus features be mandatory or optional?
- **Decision**: OPTIONAL. Some claims may not have measured stimuli (e.g., theoretical claims). Tags populate over time as papers are coded.
- **Risk**: LOW. Graceful degradation: absence of tags doesn't break system.

**D0.5.2**: Should methodological tags allow free text or only enums?
- **Decision**: ENUM PRIMARY, with `other_tag` field for extensibility. This ensures queryability and consistency.
- **Risk**: LOW. Enum can be extended; backward compatible.

**D0.5.3**: Should confidence on stimulus features affect CPT computation?
- **Decision**: NO (separate concern). Tags are metadata. CPT computation uses d, ω, δ. Tags enable filtering/auditing, not computation.
- **Risk**: LOW. Clean separation of concerns.

#### Output

- `migrations/025_add_stimulus_and_methodological_tags.sql` (100 lines)
- `src/services/tag_engine.py` (250 lines)
- Updated `src/services/paper_integration/orchestrator.py` (+50 lines at Step 3.5)
- Updated `src/services/pdf_extraction_module.py` (+30 lines for stimulus feature extraction)
- Updated `claim_v2.schema` (remove stimulus/method fields)
- Test suite: `tests/test_tag_engine.py` (150 lines, 8 test cases)

---

### Sprint 1: Three-Number Separation (4 hours)

**Target Date**: 2026-02-28

**Dependencies**: Sprint 0.5

**Objective**: Refactor codebase to explicitly separate ω (warrant strength), d (discount factor), and CPT (conditional probability). Update discount factors to new canonical values.

#### Files Affected

**New files**:
- `src/models/warrant_types.py` (updated, 50 lines)
- `src/services/epistemic_projection.py` (new, 300 lines) — implements π projection formula

**Modified files** (major refactoring):
- `src/models/bridge_warrants.py` — remove discount factor computation; separate ω handling
- `src/services/belief_credence_computation.py` — delegate to epistemic_projection.py
- All files using `DEFAULT_BRIDGE_CONFIDENCE` (~15 files)
- Template validation: update warrant strength checking

#### Core Changes

**1. Update WarrantType enum**:
```python
from enum import Enum

class WarrantType(Enum):
    CONSTITUTIVE = {
        "discount_factor": 0.95,
        "description": "Identity or definitional relationship",
        "source": "Woodward 2003 (invariance)"
    }
    MECHANISM = {
        "discount_factor": 0.80,
        "description": "Known causal pathway with identified entities",
        "source": "Woodward 2003 (mechanistic invariance)"
    }
    EMPIRICAL_ASSOCIATION = {
        "discount_factor": 0.80,
        "description": "Replicated statistical association, unknown mechanism",
        "source": "Woodward 2003 (replication = robustness)"
    }
    FUNCTIONAL = {
        "discount_factor": 0.65,
        "description": "System reliably performs functional role",
        "source": "Putnam 1967; Cartwright 1989"
    }
    CAPACITY = {
        "discount_factor": 0.55,
        "description": "System can produce effect; exercise undemonstrated",
        "source": "Cartwright 1989 (capacities)"
    }
    ANALOGICAL = {
        "discount_factor": 0.40,
        "description": "Cross-domain transfer via structural similarity",
        "source": "Gentner 1983; Bartha 2010"
    }
    THEORY_DERIVED = {
        "discount_factor": 0.25,
        "description": "Prediction from named theory, unconfirmed",
        "source": "Spohn 2012 (theoretical predictions)"
    }
```

**2. Create epistemic_projection.py**:
```python
@dataclass
class ProjectionResult:
    cpT_value: float  # Conditional probability for BN
    logit_target: float  # Intermediate (log-odds)
    components: dict  # d, ω, δ for audit trail

class ProjectionBridge:
    """π projection: EN → BN conversion."""

    def single_edge_projection(
        self,
        warrant_type: WarrantType,
        warrant_strength: float,  # ω
        p_lab: float,  # Source probability
        population_source: PopulationMetadata,
        population_target: PopulationMetadata
    ) -> ProjectionResult:
        """Project single EN edge to BN CPT entry."""
        d = warrant_type.discount_factor
        delta = self.compute_population_transfer_factor(
            population_source, population_target
        )
        logit_lab = logit(p_lab)
        logit_target = d * warrant_strength * delta * logit_lab
        cpt_value = sigmoid(logit_target)
        return ProjectionResult(
            cpt_value=cpt_value,
            logit_target=logit_target,
            components={"d": d, "omega": warrant_strength, "delta": delta}
        )

    def convergent_projection(
        self,
        edges: list[WarrantEdge],  # Multiple edges to same claim
        population_target: PopulationMetadata
    ) -> ProjectionResult:
        """Combine multiple independent lines of evidence (parallel)."""
        logit_sum = 0.0
        components = {}
        for i, edge in enumerate(edges):
            result = self.single_edge_projection(
                edge.warrant_type, edge.warrant_strength,
                edge.p_lab, edge.population_source, population_target
            )
            logit_sum += result.logit_target
            components[f"edge_{i}"] = result.components
        cpt_value = sigmoid(logit_sum)
        return ProjectionResult(
            cpt_value=cpt_value,
            logit_target=logit_sum,
            components=components
        )

    def serial_projection(
        self,
        edge_chain: list[WarrantEdge],  # Edges forming a chain
        population_target: PopulationMetadata
    ) -> ProjectionResult:
        """Compose evidence through chain (serial)."""
        d_eff = min(e.warrant_type.discount_factor for e in edge_chain)
        # Treat as single edge with effective discount
        omega_combined = mean([e.warrant_strength for e in edge_chain])
        # ... rest of computation
```

**3. Refactor bridge_warrants.py**:
- Remove discount factor computation
- Keep only warrant strength (ω) assessment
- Add deprecation warnings to `DEFAULT_BRIDGE_CONFIDENCE`
- Separate epistemic confidence from operational probability

**4. Update all CPT computation**:
Replace:
```python
cpt_value = some_formula(bridge_confidence, ...)
```

With:
```python
projection_result = projection_bridge.single_edge_projection(
    warrant_type=edge.warrant_type,
    warrant_strength=edge.warrant_strength,
    p_lab=edge.p_lab,
    population_source=edge.population_source,
    population_target=target_population
)
cpt_value = projection_result.cpt_value
```

#### Specific Tasks

| Task | What Changes | Acceptance Criterion |
|---|---|---|
| Update WarrantType enum | New discount factors (0.95, 0.80, 0.80, 0.65, 0.55, 0.40, 0.25) | Enum validates; all enums have discount_factor |
| Create epistemic_projection.py | New 300-line module | All three projection functions work; tests pass |
| Refactor bridge_warrants.py | Remove d computation; keep ω only | Tests pass; backwards compat layer intact |
| Audit codebase for mixed concerns | Find all files using bridge confidence | Catalog of 15–20 files identified |
| Update 15–20 files using bridge confidence | Replace with epistemic_projection calls | All tests pass; CI green |
| Update belief_credence_computation.py | Delegate to epistemic_projection | Tests pass; CPT values change (expected from new discount factors) |
| Type hint cleanup | Add `WarrantStrength`, `DiscountFactor`, `ConditionalProbability` types | Type checking passes; improved clarity |
| Tests for epistemic_projection.py | 20+ test cases (single, convergent, serial; boundary conditions) | All pass; 100% coverage |
| Tests for backward compatibility | Compare old vs. new CPT values | Document expected delta from discount factor changes |

#### Key Design Decisions

**D1.1**: Should old DEFAULT_BRIDGE_CONFIDENCE be removed or deprecated?
- **Decision**: DEPRECATE with warning. This preserves backward compatibility for external integrations while signaling the preferred approach.
- **Risk**: LOW. Clear deprecation path.

**D1.2**: How are old codebase references to EMPIRICAL_COVARIANCE handled?
- **Decision**: Both names work during Sprint 1 (via enum alias). After Sprint 1, only EMPIRICAL_ASSOCIATION is valid.
- **Risk**: LOW. Controlled transition.

**D1.3**: What if new discount factors cause large changes in existing BN probabilities?
- **Decision**: EXPECTED and CORRECT. These are revised estimates based on new evidence (Woodward invariance framework). Document change in release notes. Provide side-by-side comparison in test suite.
- **Risk**: MEDIUM. May cause surprise in stakeholders; good communication is essential.

#### Output

- Updated `src/models/warrant_types.py` (50 lines, new discount factors)
- New `src/services/epistemic_projection.py` (300 lines, π projection)
- Refactored `src/models/bridge_warrants.py` (50 line reduction)
- Updated ~15 call sites for epistemic_projection integration (~100 lines total)
- Test suite: `tests/test_epistemic_projection.py` (250 lines, 20 test cases)
- Backward compatibility test: `tests/test_discount_factor_changes.py` (100 lines, comparing old vs. new)

---

### Sprint 2: π Projection Deployment + Discount Factor Integration (3 hours)

**Target Date**: 2026-03-01

**Dependencies**: Sprint 1

**Objective**: Integrate π projection throughout the belief and BN systems. Update all CPT generation to use new discount factors. Validate that projections are mathematically correct.

#### Files Affected

**New files**:
- `tests/test_pi_projection_integration.py` (150 lines)

**Modified files**:
- `src/services/belief_credence_computation.py` — integrate epistemic_projection calls
- `src/services/belief_network_builder.py` — use π for all CPT generation
- `src/services/setup_function.py` (system_setup.py, Phase 4) — use new projection in bulk belief creation
- `streamlit_app/pages/` — update dashboard to show warrant structure and projection path

#### Core Tasks

| Task | What Changes | Acceptance Criterion |
|---|---|---|
| Integrate epistemic_projection into belief_credence_computation.py | All CPT values computed via π | Tests pass; no CPT > 1.0 or < 0.0 |
| Integrate into belief_network_builder.py | All BN edges use π-computed CPTs | BN generates without errors; edge weights make sense |
| Update setup() Phase 4 (bulk belief creation) | Use π for all 23,800 beliefs | Phase 4 completes in <1 min; coherence computed correctly |
| Validate convergence behavior | Reflective equilibrium should still converge | Phase 5 converges in 1–3 iterations |
| Add dashboard visualization | Show warrant structure on belief cards | Can see d, ω, δ, CPT for each belief |
| Cross-validate against old system | Compare CPT values with old formulas (if available) | Document expected deltas; explain changes |
| Benchmark performance | Measure time for π projection on large corpus | Target: <1 sec for 10,000 projections |

#### Key Design Decisions

**D2.1**: Should population transfer factor (δ) be pre-computed or computed on-demand?
- **Decision**: PRE-COMPUTED for target building population. Store in `target_population_profile` table. Reduces recomputation.
- **Risk**: LOW. Straightforward caching.

**D2.2**: How should convergence be monitored during Phase 5 reflective equilibrium?
- **Decision**: Track coherence delta per iteration. Log warrant type distribution (how many edges of each type entered the system). Monitor for pathological cycles.
- **Risk**: MEDIUM. Coherence may not converge if discount factors are miscalibrated. Mitigation: extensive logging and visualization.

**D2.3**: Should the old discount factors be retained for comparison?
- **Decision**: YES. Create `warrant_types_legacy.py` with 2025 values. Use in test suite for comparison. Helps stakeholders understand impact of changes.
- **Risk**: LOW. Documentation-friendly approach.

#### Output

- Updated `src/services/belief_credence_computation.py` (+100 lines)
- Updated `src/services/belief_network_builder.py` (+50 lines)
- Updated `src/services/system_setup.py` Phase 4 (+20 lines, π integration)
- Visualization: new dashboard page `/pages/9_belief_warrant_structure.py` (150 lines)
- Test suite: `tests/test_pi_projection_integration.py` (150 lines)
- Documentation: `docs/PI_PROJECTION_IMPACT_REPORT.md` (explaining CPT changes, comparisons)

---

### Sprint 3: Coherence Dashboard (2 hours)

**Target Date**: 2026-03-01 (parallel with Sprint 2)

**Dependencies**: Sprint 1

**Objective**: Create real-time coherence monitoring dashboard showing system health, warrant distribution, and potential inconsistencies.

**Status**: Largely complete from Session 8; minor updates for new warrant types and projection visualization.

#### Minor Updates

- Add new warrant type breakdowns (EMPIRICAL_ASSOCIATION replaces EMPIRICAL_COVARIANCE)
- Visualize π projection impact on CPT values
- Show discount factor distribution across beliefs

#### Files Affected

- `streamlit_app/pages/8_system_health.py` (+30 lines)

---

### Sprint 4: Argumentation Graph (2 hours)

**Target Date**: 2026-03-01 (parallel with Sprint 2–3)

**Dependencies**: Sprint 0 (citation graph), Sprint 1 (new warrant types)

**Status**: Code complete from Session 8. Minor updates for citation edges and new warrant types.

#### Files Affected

- `src/services/argumentation_graph.py` (+20 lines for new warrant type handling)

---

### Sprint 5: Nightly Batch Infrastructure (2 hours)

**Target Date**: 2026-03-02

**Dependencies**: Sprint 2 (π projection), Sprint 4 (argumentation graph)

**Status**: Largely complete; add warrant monitoring and new discount factor checks.

#### Minor Updates

- Add warrant type distribution report
- Check for discount factor miscalibrations (e.g., THEORY_DERIVED edges accumulating above threshold)
- Log population transfer factor effectiveness

#### Files Affected

- `scripts/overseer_nightly.py` (+50 lines for warrant monitoring)

---

### Sprint 6: Expert Calibration Prep (2 hours)

**Target Date**: 2026-03-02

**Dependencies**: Sprint 5 (nightly batch)

**Status**: Mostly complete; update calibration report to show warrant type distribution and π projection impact.

#### Minor Updates

- Calibration report includes warrant strength distribution by type
- Highlight edges with low ω or low d (candidates for further research)
- Show which theories (THEORY_DERIVED edges) have received empirical support

#### Files Affected

- `scripts/generate_calibration_report.py` (+30 lines for warrant analysis)

---

### Sprint 7: T2 Mechanism Templates & Governance (3 hours, PARALLEL)

**Target Date**: 2026-03-02–03 (can run parallel to Sprints 3–6)

**Dependencies**: Sprint 1 (warrant types established)

**Objective**: Formalize six T2 mechanism templates as governance infrastructure. Enable quality assurance by checking that mechanistic explanations match known templates.

#### Files to Create

**New files**:
- `src/models/mechanism_templates.py` (150 lines)
- `data/mechanism_templates.json` (200 lines)
- `src/services/template_quality_assurance.py` (100 lines)
- `tests/test_mechanism_templates.py` (80 lines)

#### Core Tasks

| Task | What Changes | Acceptance Criterion |
|---|---|---|
| Define T2Template dataclass hierarchy | 6 subclasses (Predictive Coding, Homeostatic, Accumulation, Competitive, Gated, Convergent) | All inherit from base; can be instantiated |
| Create mechanism_templates.json registry | 6 templates with parameters, theory bases, calibration sources | JSON validates; template IDs match enum |
| Implement TemplateQA service | Checks that concrete mechanism explanations reference valid templates | Can validate 50+ mechanisms against templates |
| Integrate into belief validation | Optional: flag beliefs whose mechanisms don't match known templates | Warnings only (not blocking); logged for review |
| Write template documentation | Reference guide for each template with worked examples | 2–3 pages per template |

#### Key Design Decisions

**D7.1**: Should template matching be mandatory or advisory?
- **Decision**: ADVISORY. Don't require all mechanistic beliefs to match templates; instead log and report. This allows for novel mechanisms while providing quality feedback.
- **Risk**: LOW. Governance without enforcement.

**D7.2**: Should T2 templates be extended by domain experts over time?
- **Decision**: YES. Establish governance process: new template candidate → domain panel review → vote to add. Document in `docs/MECHANISM_TEMPLATE_GOVERNANCE.md`.
- **Risk**: LOW. Extensible design from the start.

#### Output

- `src/models/mechanism_templates.py` (150 lines)
- `data/mechanism_templates.json` (200 lines)
- `src/services/template_quality_assurance.py` (100 lines)
- `tests/test_mechanism_templates.py` (80 lines)
- Documentation: `docs/MECHANISM_TEMPLATES_REFERENCE_GUIDE.md` (150 lines, 6 sections)
- Documentation: `docs/MECHANISM_TEMPLATE_GOVERNANCE.md` (50 lines, governance process)

---

### Sprint 8 (Future): Expert Panel Calibration (4 hours)

**Target Date**: 2026-03-03–04 (after Sprints 0–7)

**Dependencies**: Sprint 6 (calibration report ready)

**Objective**: Domain experts review the updated system with new discount factors, π projection, and three-layer annotation model. Provide feedback on warrant strength distributions and mechanistic plausibility.

**Scope**: (Deferred; out of scope for this sprint plan revision)

---

## Summary: Key Metrics and Success Criteria

### By Completion of All Sprints (March 5, 2026)

| Metric | Target | Measurement |
|---|---|---|
| **System operational** | All 850 papers integrated with new π projection | `setup()` executes; OPERATIONAL state reached |
| **Warrant structure** | 100% of 23,800 beliefs assigned warrant types | Database query: `SELECT COUNT(*) FROM beliefs WHERE warrant_type IS NOT NULL` = 23,800 |
| **Discount factors updated** | All 7 warrant types using new values | Enum check: all discount_factor fields correct |
| **π projection validated** | No CPT values out of [0, 1]; projections make sense | Test suite: 20 test cases pass; spot checks on 50+ beliefs |
| **Annotation model deployed** | Stimulus tags and methodological tags on all claims | Database tables populated; tag coverage ≥ 80% |
| **T2 templates registered** | 6 templates formally defined and documented | JSON registry complete; documentation written |
| **Coherence dashboard updated** | Shows new warrant types and projection paths | Dashboard renders; no errors |
| **Test suite green** | All tests pass including new projection and tag tests | CI passes; coverage ≥ 85% |

### Risk Assessment

| Sprint | Risk Level | Mitigation |
|---|---|---|
| 0.5 (Annotation Model) | MEDIUM | Schema migration tested in staging; rollback plan documented |
| 1 (Three-Number Separation) | MEDIUM-HIGH | Extensive test coverage; backward compat layer; careful code review |
| 2 (π Projection Integration) | MEDIUM | Validation against old formulas; benchmarking for performance |
| 3–6 (Dashboards, Batch) | LOW | Minor updates; straightforward integration |
| 7 (T2 Templates) | LOW | Additive change; advisory governance |

---

## Conclusion

The six documents from AG sessions resolve critical architectural ambiguities and provide a mathematically rigorous framework for evidence transfer across contexts. The revised sprint plan operationalizes these insights into concrete code changes, database migrations, and governance processes.

The system transitions from:
- **Before**: Conflated concerns (ω, d, CPT mixed together); arbitrary discount factors; vague annotation model
- **After**: Clear separation (three distinct numbers); theoretically grounded discount factors (Woodward invariance); formal three-layer annotation model; explicit π projection formula

The panel deliberations establish consensus on all major architectural decisions while identifying dissenting views and appropriate risk mitigations. The revised sprint plan is executable and should reach OPERATIONAL status by March 5, 2026.

---

## References

Bareinboim, E., & Pearl, J. (2016). Causal inference and the data-fusion problem. *Proceedings of the National Academy of Sciences*, 113(27), 7345–7352. https://doi.org/10.1073/pnas.1510507113

Cartwright, N. (1989). *Nature's capacities and their measurement*. Oxford University Press.

Clark, A. (2013). *Whatever next? Predictive brains, situated agents, and the future of cognitive science*. *Behavioral and Brain Sciences*, 36(3), 181–204. https://doi.org/10.1017/S0140525X12000477

Der Kiureghian, A., & Ditlevsen, O. (2009). Aleatory and epistemic uncertainty in structural reliability analysis: Present and future. *Structural Safety*, 31(2), 105–112. https://doi.org/10.1016/j.strusafe.2008.06.020

Friston, K. J. (2010). The free-energy principle: A unified brain theory? *Nature Reviews Neuroscience*, 11(2), 127–138. https://doi.org/10.1038/nrn2787

Gentner, D. (1983). *Structure-mapping: A theoretical framework for analogy*. *Cognitive Science*, 7(2), 155–170. https://doi.org/10.1207/s15516709cog0702_3

Jaynes, E. T. (2003). *Probability theory: The logic of science*. Cambridge University Press.

Machamer, P., Darden, L., & Craver, C. F. (2000). Thinking about mechanisms. *Philosophy of Science*, 67(1), 1–25. https://doi.org/10.1086/392759

Pearl, J., & Bareinboim, E. (2014). External validity: From do-calculus to transportability across populations. *Statistical Science*, 29(4), 579–595. https://doi.org/10.1214/14-STS486

Putnam, H. (1967). The nature of mental states. In W. H. Capitan & D. D. Merrill (Eds.), *Art, mind, and religion*. University of Pittsburgh Press.

Quine, W. V. O. (1951). Two dogmas of empiricism. *The Philosophical Review*, 60(1), 20–43. https://doi.org/10.2307/2181906

Woodward, J. (2003). *Making things happen: A theory of causal explanation*. Oxford University Press.

---

**Document prepared by**: Claude Opus 4.6 (Anthropic)
**Date**: February 27, 2026
**Status**: Ready for Professor Kirsh Review and Panel Approval
**Next step**: Convene Panel A & B deliberations; obtain final approval for Sprint execution
