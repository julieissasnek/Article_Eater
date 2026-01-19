# Expert Panel Review: Article Eater Sprint 2 Validation & Sprint 3 Specification

**Date**: Sunday, January 18, 2026
 **Convened by**: Professor David Kirsh, UCSD Cognitive Science
 **Panel Chair**: Claude (facilitating synthesis of expert perspectives)

------

## Preamble: On the Construction of Expert Voices

Before proceeding, a methodological note is warranted. The following panel discussion synthesizes positions that these scholars would likely take based on their published corpus. I have attempted to remain faithful to their documented intellectual commitments while applying them to a problem domain—software epistemology for environmental psychology—that they did not directly address. Where I am confident of alignment with their published views, I indicate this; where I am extrapolating, I mark the inference as such.

------

## PART 1: SPRINT 2 DECISION VALIDATION

### Decision 2.1: Fresh Web Per Paper vs. Cumulative Integration

**The Implementation**: Each paper receives a fresh `WebOfBelief` instance; beliefs do not accumulate across papers within a single pipeline run.

------

**Dr. Nancy Cartwright** (Philosophy of Science, LSE):

The decision to isolate webs per paper is epistemologically sound for this sprint, though it requires careful justification. In *How the Laws of Physics Lie* (Cartwright, 1983), I argued that scientific claims have limited domains of applicability—what I termed their "capacities." A claim extracted from Paper A about amygdala response to angular objects operates within a specific experimental capacity; mechanically accumulating it with claims from Paper B about architectural preference risks what I would call *premature unification*.

However—and this is crucial—isolation should not be permanent. The entire point of coherentist epistemology is that beliefs gain justification through their relations with other beliefs (BonJour, 1985). A web containing only beliefs from a single paper cannot achieve genuine coherence; it can only achieve *internal consistency*, which is a weaker property.

**Recommendation**: Approve the Sprint 2 decision, but ensure Sprint 5 (Persistence & Accumulation) is designed to perform *principled* accumulation—not mere concatenation. The accumulation algorithm must include:

1. Domain compatibility checking
2. Bridge warrant verification (Sprint 3)
3. Tension detection before integration

**Dr. Judea Pearl** (Computer Science, UCLA):

From a causal inference perspective, the fresh-web-per-paper approach has an important advantage: it preserves the *provenance* of causal claims. When I developed the do-calculus (Pearl, 2009), a central concern was maintaining clarity about which variables were observed versus intervened upon. Similarly, maintaining per-paper webs preserves clarity about which paper contributed which beliefs.

The cumulative approach creates what I would call *causal contamination*—if Paper A and Paper B both mention "arousal" but operationalize it differently (one as GSR, one as self-report), naive accumulation would treat these as the same variable. This is a category error that corrupts subsequent inference.

**Recommendation**: Approve. Additionally, when Sprint 5 implements accumulation, require explicit *variable alignment* procedures before merging webs.

**Dr. Herbert Simon** (Carnegie Mellon, *constructed posthumously from his methodology*):

The principle of bounded rationality suggests that we should not attempt to solve problems we are not yet equipped to solve (Simon, 1956). Sprint 2's mandate was pipeline integration, not accumulation architecture. The decision to defer accumulation honors the sprint boundary—this is good engineering practice.

However, I would note that the decision has *satisficing* character: it is good enough for now, but should not be mistaken for optimal. The system's ultimate value lies in its ability to synthesize across papers; isolated webs are means, not ends.

**Recommendation**: Approve, with explicit acknowledgment that this is a scaffolding decision to be superseded.

------

**Panel Consensus on 2.1**: **APPROVED**

The fresh-web-per-paper approach is correct for Sprint 2. Accumulation requires the bridge warrant machinery (Sprint 3) and persistence infrastructure (Sprint 5) that do not yet exist. Implementing premature accumulation would conflate the extraction problem with the integration problem.

------

### Decision 2.2: Graceful Degradation on Web Integration Failure

**The Implementation**: If `web_of_belief` imports fail or integration throws an exception, the pipeline continues, returning `"web_integration": "skipped"` or `"failed"`. Extraction outputs (claims.jsonl, rules.jsonl) are still produced.

------

**Dr. Herbert Simon**:

This is precisely correct. In *The Sciences of the Artificial* (Simon, 1969/1996), I emphasized that complex systems should be *nearly decomposable*—failures in one subsystem should not cascade to others. The extraction pipeline and the web-of-belief integration are logically separable functions. If Track B (Web of Belief) fails, Track A (Extraction) outputs remain valuable.

The alternative—halting the entire pipeline on web integration failure—would violate what I term *progressive commitment*. Users who simply want extracted claims should not be blocked by failures in a downstream analysis module they may not need.

**Dr. Marcia Bates** (Information Studies, UCLA):

From an information science perspective, the key question is: *who are the downstream consumers, and what are their information needs?* (Bates, 2005). If the consumer is a researcher wanting raw claims for manual analysis, graceful degradation is appropriate. If the consumer is an automated system expecting web-integrated output, silent degradation could cause subtle failures downstream.

**Recommendation**: The degradation should not be *silent*. At minimum:

1. Log a WARNING-level message (not just INFO)
2. Include failure reason in the output metadata
3. Consider a `--strict` mode that fails loudly for automated pipelines

**Dr. Rachel Kaplan** (Environmental Psychology, University of Michigan):

As someone who would be a consumer of this system, I strongly support graceful degradation. Environmental psychology research often involves extracting claims from dozens of papers. If web integration fails for one paper, I would still want the extracted claims from the others. Blocking the entire batch on a single failure would be operationally frustrating.

However, I echo the concern about visibility. The failure should be clearly marked so I know which papers need reprocessing.

------

**Panel Consensus on 2.2**: **APPROVED WITH MODIFICATIONS**

Graceful degradation is correct, but should be *visible* degradation:

- Emit WARNING-level log
- Write a `web_integration_error.json` file on failure (containing traceback, timestamp)
- Add `--strict` CLI flag for pipelines that require web integration

------

### Decision 2.3: Schema Formalization (Ad Hoc vs. Formal Contracts)

**The Implementation**: Schemas were invented on-the-fly (`ae.web_state.v1`, `ae.coherence_summary.v1`) without formal JSON schema definitions in `contracts/ae_af/schemas/`.

------

**Dr. Marcia Bates**:

This concerns me significantly. In information architecture, *schema drift* is a primary cause of system entropy (Bates, 2002). When schemas are defined implicitly by code rather than explicitly by contract, several problems emerge:

1. **Documentation decay**: Code changes but implicit schemas are not updated
2. **Consumer confusion**: Downstream systems must reverse-engineer the schema
3. **Validation absence**: No mechanism to catch malformed outputs

The versioning convention (`ae.web_state.v1`) is a good practice—it acknowledges that schemas evolve. But the version number is meaningless without a formal definition of what v1 contains.

**Recommendation**: Formal JSON schemas are **required** before Sprint 3 proceeds. These should:

- Live in `contracts/ae_af/schemas/`
- Use JSON Schema (draft-07 or later)
- Include field descriptions, types, and required/optional annotations
- Be versioned with semantic versioning (breaking changes increment major version)

**Dr. Herbert Simon**:

I would add a pragmatic consideration. The cost of formalizing schemas is low; the cost of *not* formalizing them accumulates over time. Every hour spent deciphering implicit schemas later is an hour that could have been saved by ten minutes of documentation now.

Furthermore, formal schemas enable *automated validation*, which reduces debugging time when integration fails.

------

**Panel Consensus on 2.3**: **REVISION REQUIRED**

Sprint 2 cannot be considered complete until formal JSON schemas exist for:

- `ae.web_state.v1`
- `ae.coherence_summary.v1`
- `ae.stub.v1` (for stubs.jsonl)
- `ae.tension.v1` (for tensions.jsonl)

These schemas should be created before Sprint 3 begins, as Sprint 3 will extend them with bridge warrant fields.

------

### Decision 2.4: Web State Serialization Detail Level

**The Implementation**: web_state.json includes truncated belief content (first 200 chars), level, status, credence, theory_id, and entrenchment for each belief.

------

**Dr. Judea Pearl**:

The serialization is missing a critical component: **constraint serialization**. In a Bayesian network, the edges (representing conditional dependencies) carry as much information as the nodes (variables). Similarly, in a coherentist web, the constraints (coherence/tension relations between beliefs) carry as much information as the beliefs themselves.

Without constraints, the web_state.json is a *bag of beliefs*, not a *web*. You cannot reconstruct the coherence structure from beliefs alone.

**Recommendation**: Add a `constraints` field containing:

```json
"constraints": [
  {
    "type": "COHERENCE|TENSION",
    "belief_a": "belief_id_1",
    "belief_b": "belief_id_2",
    "strength": 0.7,
    "basis": "shared_mechanism"
  }
]
```

**Dr. Nancy Cartwright**:

On the question of truncation: I would argue against it, at least for the primary serialization. The full content of a belief is necessary for understanding its *capacity*—the domain within which it operates. A truncated belief like "Curvilinear forms reduce amygdala activa..." loses the crucial specificity about *which* curvilinear forms and *under what conditions*.

**Recommendation**: Provide two serialization modes:

1. `web_state.json` — full content, for archival and rehydration
2. `web_state_summary.json` — truncated, for human inspection and dashboards

**Dr. Herbert Simon**:

The truncation concern is valid for *persistence* (Sprint 5), where you need full fidelity to reconstruct the web. For *inspection* (Sprint 2's primary use case), truncation is acceptable.

I recommend implementing full serialization now, with a separate summary generator for human consumption.

------

**Panel Consensus on 2.4**: **REVISION REQUIRED**

1. **Add constraint serialization** — without edges, you have nodes but no graph
2. **Store full content** — truncation is acceptable only in separate summary files
3. **Design for Sprint 5** — the serialization format should support round-trip rehydration

------

### Decision 2.5: Equilibrium Parameters (Hardcoded vs. Configurable)

**The Implementation**: `seek_equilibrium=True` and `equilibrium_iterations=5` are hardcoded.

------

**Dr. Judea Pearl**:

Five iterations is likely insufficient for non-trivial webs. In belief propagation algorithms, convergence typically requires O(diameter) iterations, where diameter is the longest path in the graph. For a web with 50 beliefs and moderate connectivity, diameter could easily be 8-10.

However, I recognize the tradeoff: more iterations mean slower processing. The correct solution is not to pick a fixed number, but to **iterate until convergence** with a maximum iteration cap as a safety bound.

**Recommendation**:

```python
equilibrium_iterations = config.get("max_equilibrium_iterations", 20)
convergence_threshold = config.get("equilibrium_convergence_threshold", 0.001)
# Iterate until coherence score change < threshold OR max iterations reached
```

**Dr. Herbert Simon**:

Hardcoding is acceptable for early development—it reduces configuration complexity. But by Sprint 3, these should be configurable. The design principle is *progressive parameterization*: start with sensible defaults, expose parameters as the system matures.

**Dr. Rachel Kaplan**:

As an end user, I would appreciate a `--fast` flag that reduces iterations for exploratory runs, and a `--thorough` flag for final analyses. The defaults should be thorough; speed is a user-invoked tradeoff.

------

**Panel Consensus on 2.5**: **APPROVED WITH FUTURE WORK**

Hardcoding is acceptable for Sprint 2. Sprint 4 or Sprint 5 should:

1. Make parameters configurable via environment variables or profile settings
2. Implement convergence-based termination (not just iteration count)
3. Expose `--fast` / `--thorough` CLI presets

------

### Decision 2.6: Output File Conditionality

**The Implementation**: New files (web_state.json, stubs.jsonl, tensions.jsonl, coherence_summary.json) are only written if integration succeeds. On failure, they are not created.

------

**Dr. Marcia Bates**:

This is the correct approach, provided the failure is otherwise visible (per Decision 2.2). Writing empty or error-state files creates ambiguity: does an empty `tensions.jsonl` mean "no tensions detected" or "integration failed"? The absence of the file is an unambiguous signal.

**However**: there should be a *manifest* file that lists which outputs were produced. This allows downstream consumers to programmatically determine what succeeded without checking for file existence.

**Recommendation**: Add `pipeline_manifest.json`:

```json
{
  "run_id": "...",
  "outputs_produced": ["claims.jsonl", "rules.jsonl", "web_state.json"],
  "outputs_skipped": ["stubs.jsonl"],
  "outputs_failed": []
}
```

**Dr. Herbert Simon**:

The manifest approach is elegant—it separates the *inventory* of outputs from the *content* of outputs. This is a clean interface for downstream automation.

------

**Panel Consensus on 2.6**: **APPROVED WITH ENHANCEMENT**

File conditionality is correct. Add a `pipeline_manifest.json` documenting which outputs were produced, skipped, or failed.

------

## PART 2: SPRINT 3 SPECIFICATION — BRIDGE WARRANTS

### Preliminary: What Are Bridge Warrants?

**Dr. Nancy Cartwright** (Primary Expert):

Bridge warrants are the explicit assumptions that license the transfer of knowledge from one domain to another. The term originates in my work on *nomological machines* (Cartwright, 1999) and has been developed in the context of evidence-based policy (Cartwright & Hardie, 2012).

Consider the case at hand: Bar & Neta (2006) found that angular objects activate the amygdala, suggesting threat detection. Vartanian et al. (2013) investigated whether angular *rooms* have similar effects. The transfer from "objects" to "rooms" requires a bridge warrant—an explicit assumption such as:

> *Angular geometry activates a domain-general threat detection mechanism (amygdala pathway) regardless of the scale or category of the angular stimulus.*

This bridge warrant has **testable implications**. If rooms activate ACC rather than amygdala (as Vartanian found), the mechanism bridge fails, though a functional bridge (both evoke negative affect) might succeed.

Bridge warrants are not merely rhetorical devices; they are **load-bearing epistemic structures** that determine whether evidence transfers across domains.

------

### Question 3.1: Where Does the Bridge Field Live?

**Panel Deliberation**:

**Dr. Nancy Cartwright**: Bridge warrants are *relations between claims*, not properties of individual claims. A claim like "angular objects activate amygdala" does not intrinsically have a bridge type; it acquires bridge relevance only when someone attempts to apply it to a different domain.

Therefore, bridges should **not** live in `ae.claim.v1` or `ae.rule.v1`. They should be first-class entities.

**Dr. Judea Pearl**: I agree. In causal graphs, we distinguish between nodes (variables) and edges (relations). The bridge warrant is analogous to a *transport formula* (Pearl & Bareinboim, 2014)—a formal condition under which causal effects can be transported from one population to another.

Transport formulas are not properties of individual studies; they are properties of the *relationship* between the source and target populations.

**Dr. Marcia Bates**: From a data modeling perspective, bridges should be a separate entity with foreign keys to the beliefs they connect. This allows:

- Many-to-many relationships (one bridge might connect multiple source beliefs to multiple target beliefs)
- Independent versioning
- Separate provenance tracking

**Panel Consensus on 3.1**:

**Create `ae.bridge.v1` as a new schema**. Bridges are first-class entities, not annotations on existing schemas. They reference beliefs by ID but are stored separately.

Implementation location: new file `src/services/bridge_warrants.py`, with schema in `contracts/ae_af/schemas/bridge.v1.json`.

------

### Question 3.2: How Is Bridge Type Determined?

**The Four Bridge Types** (from Cartwright's typology, extended):

| Type             | Definition                                           | Example                                                      |
| ---------------- | ---------------------------------------------------- | ------------------------------------------------------------ |
| **Mechanism**    | Same causal pathway operates in both domains         | Amygdala activation for angular objects → angular rooms      |
| **Functional**   | Same functional outcome despite different mechanisms | Objects and rooms both evoke negative affect, but via different pathways |
| **Analogical**   | Structural similarity suggests similar effects       | Fractal patterns in nature → fractal patterns in architecture |
| **Constitutive** | Target domain is literally composed of source domain | Room corners are composed of angular objects                 |

**Panel Deliberation**:

**Dr. Nancy Cartwright**: Bridge type determination is fundamentally a *judgment* requiring domain expertise. However, LLM inference can propose a bridge type based on how the source paper frames its claims. If Bar & Neta explicitly discuss "threat detection circuitry," an LLM can reasonably infer they are proposing a mechanism-level generalization.

**Dr. Rachel Kaplan**: In environmental psychology, researchers often signal their bridging assumptions in the discussion section. Phrases like "this suggests a general principle" indicate analogical bridging; "the same neural pathway" indicates mechanism bridging. These are extractable cues.

**Dr. Herbert Simon**: Given bounded resources, I recommend a **two-stage approach**:

1. **LLM inference** during extraction (add to the seven-panel prompt) proposes bridge type with confidence
2. **HITL review** (Sprint 7 or later) allows domain experts to correct or confirm

This balances automation with accuracy. The LLM's proposal is a *draft*, not a determination.

**Panel Consensus on 3.2**:

**Hybrid approach**:

1. Extend the extraction prompt to identify bridge-relevant claims and propose bridge types
2. Store proposals with `confidence` field
3. Default status is `"hypothesized"` (machine-proposed)
4. HITL review can change status to `"confirmed"` or `"rejected"`

------

### Question 3.3: Bridge-Weighted Credence Formula

**The Proposed Formula**:

```
P(CNFA effect) = P(parent theory) × P(bridge) × P(CNFA-specific)
```

**Panel Deliberation**:

**Dr. Judea Pearl**: This formula is *Naïve Bayes-esque*—it assumes independence between the three probability terms, which is almost certainly false. The probability that a bridge holds is not independent of the parent theory's credence; stronger theories tend to have more tested bridges.

However, for a first approximation, this multiplicative decomposition has the right *qualitative* properties:

- If the parent theory is weak, CNFA predictions inherit that weakness
- If the bridge is uncertain, CNFA predictions inherit that uncertainty
- CNFA-specific factors (e.g., confounds in architectural studies) further attenuate

I would recommend keeping this formula but documenting its independence assumption explicitly.

**Dr. Nancy Cartwright**: The formula needs clarification. What does "P(bridge)" mean operationally? I propose:

> **P(bridge)** = the probability that the bridging assumption holds—i.e., that the mechanism/function/analogy claimed in the source domain actually transfers to the target domain.

This should be *initialized* based on bridge type (mechanisms are typically more reliable than analogies) but *updated* based on evidence.

**Default P(bridge) by type**:

| Bridge Type  | Default P(bridge) | Rationale                                                   |
| ------------ | ----------------- | ----------------------------------------------------------- |
| Constitutive | 0.85              | Target literally contains source; transfer is near-certain  |
| Mechanism    | 0.60              | Mechanisms often conserved, but scale/context can disrupt   |
| Functional   | 0.50              | Functions often achieved by different mechanisms            |
| Analogical   | 0.35              | Analogies are suggestive but frequently fail under scrutiny |

These defaults should be **configurable** and **domain-specific** (environmental psychology may have different base rates than, say, pharmacology).

**Dr. Herbert Simon**: The formula should be computed *lazily*—only when a downstream consumer requests the credence of a CNFA-specific prediction. Pre-computing all bridge-weighted credences would be wasteful if most are never queried.

**Panel Consensus on 3.3**:

**Adopt the multiplicative formula with documented assumptions**:

```python
def compute_bridged_credence(
    parent_theory_credence: float,
    bridge_confidence: float,
    cnfa_specific_confidence: float
) -> float:
    """
    Compute credence for a CNFA-specific claim derived via bridge warrant.
    
    Assumes independence (known limitation - see documentation).
    
    Args:
        parent_theory_credence: P(parent theory is correct), 0-1
        bridge_confidence: P(bridge transfers), 0-1, defaults by bridge type
        cnfa_specific_confidence: P(no CNFA-specific confounds), 0-1
    
    Returns:
        Bridged credence, 0-1
    """
    return parent_theory_credence * bridge_confidence * cnfa_specific_confidence
```

**Default P(bridge) values**: Constitutive 0.85, Mechanism 0.60, Functional 0.50, Analogical 0.35.

**Bridge confidence is continuous (0-1)**, not categorical. The type determines the default; evidence updates the value.

------

### Question 3.4: Bridge Failure Handling

**The Bar & Neta → Vartanian Case**:

- Bar & Neta (2006): Angular objects → amygdala activation
- Vartanian et al. (2013): Angular rooms → ACC activation (not amygdala)
- **Mechanism bridge failed**; functional bridge may still hold (both evoke negative responses)

**Panel Deliberation**:

**Dr. Nancy Cartwright**: Bridge failure is an extremely important epistemic event—it is how we learn the *boundaries* of our theories. Failed bridges should not be deleted; they should be marked as failed and retained for their informational value.

Furthermore, a failed mechanism bridge should trigger a *bridge revision*: perhaps a functional bridge is warranted instead. The system should support bridge *downgrading* (mechanism → functional) as a response to disconfirming evidence.

**Dr. Judea Pearl**: From a causal perspective, failed bridges are *transportability violations* (Pearl & Bareinboim, 2014). They indicate that some variable differs between source and target domains in a way that breaks the causal mechanism.

In the Bar & Neta → Vartanian case, the failure suggests that *scale* (object vs. room) mediates the effect. This is valuable causal information—it tells us to look for scale-dependent variables.

**Recommendation**: Bridge failure should create:

1. A **tension** in the web (STRONG_TENSION between the mechanism claim and the Vartanian finding)
2. An **anomaly** record documenting the failure
3. A **VOI flag** indicating high value of information for follow-up studies that investigate the boundary condition

**Dr. Rachel Kaplan**: As a domain user, I would want to see failed bridges prominently displayed. They tell me where to focus future research. A system that hides failures would be epistemically misleading.

**Panel Consensus on 3.4**:

**Bridge failure creates a multi-part response**:

1. **Update bridge status** to `"failed"` with timestamp and evidence
2. **Create tension** in web_of_belief between source claim and disconfirming target finding
3. **Generate anomaly record** in a new `anomalies.jsonl` output
4. **Trigger VOI computation**: failed bridges are high-value targets for investigation
5. **Propose bridge revision**: can the mechanism bridge be downgraded to a functional bridge that still holds?

Schema addition for `ae.bridge.v1`:

```json
{
  "failure_record": {
    "failed_at": "2026-01-18T14:30:00Z",
    "disconfirming_evidence": ["belief_id_vartanian_001"],
    "failure_type": "mechanism_not_conserved",
    "suggested_revision": "functional"
  }
}
```

------

### Question 3.5: Bridge Warrant Schema

**Panel Consensus Schema for `ae.bridge.v1`**:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "ae.bridge.v1",
  "title": "Bridge Warrant",
  "description": "Explicit assumption licensing transfer of knowledge between domains",
  "type": "object",
  "required": ["schema", "bridge_id", "source_domain", "target_domain", "bridge_type", "warrant_statement", "confidence", "status"],
  "properties": {
    "schema": {
      "const": "ae.bridge.v1"
    },
    "bridge_id": {
      "type": "string",
      "pattern": "^bridge:[a-zA-Z0-9_-]+$",
      "description": "Unique identifier for this bridge warrant"
    },
    "source_domain": {
      "type": "string",
      "description": "Domain from which evidence originates (e.g., 'object_perception')"
    },
    "target_domain": {
      "type": "string",
      "description": "Domain to which evidence is transferred (e.g., 'architectural_perception')"
    },
    "bridge_type": {
      "type": "string",
      "enum": ["mechanism", "functional", "analogical", "constitutive"],
      "description": "Type of bridging assumption"
    },
    "warrant_statement": {
      "type": "string",
      "description": "Natural language statement of the bridging assumption"
    },
    "assumed_mechanism": {
      "type": ["string", "null"],
      "description": "For mechanism bridges: the conserved causal pathway"
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Probability that the bridge holds (0-1)"
    },
    "confidence_source": {
      "type": "string",
      "enum": ["default", "llm_inferred", "human_assigned", "evidence_updated"],
      "description": "How confidence was determined"
    },
    "status": {
      "type": "string",
      "enum": ["hypothesized", "supported", "contested", "failed", "revised"],
      "description": "Current epistemic status of the bridge"
    },
    "source_beliefs": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Belief IDs from source domain that ground this bridge"
    },
    "target_beliefs": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Belief IDs in target domain that this bridge supports"
    },
    "evidence_for": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Belief IDs or paper IDs supporting the bridge"
    },
    "evidence_against": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Belief IDs or paper IDs disconfirming the bridge"
    },
    "failure_record": {
      "type": ["object", "null"],
      "properties": {
        "failed_at": { "type": "string", "format": "date-time" },
        "disconfirming_evidence": { "type": "array", "items": { "type": "string" } },
        "failure_type": { "type": "string" },
        "suggested_revision": { "type": ["string", "null"] }
      },
      "description": "Record of bridge failure, if applicable"
    },
    "provenance": {
      "type": "object",
      "properties": {
        "created_at": { "type": "string", "format": "date-time" },
        "created_by": { "type": "string" },
        "last_updated": { "type": "string", "format": "date-time" },
        "version": { "type": "integer" }
      }
    }
  }
}
```

------

### Question 3.6: Integration Points

**Panel Recommendation**:

**Dr. Herbert Simon**: Follow the *separation of concerns* principle. Bridge warrant logic should be modular and loosely coupled to existing components.

**Recommended architecture**:

```
NEW FILE: src/services/bridge_warrants.py
├── BridgeWarrant (dataclass matching ae.bridge.v1)
├── BridgeRegistry (manages bridge instances, like TheoryRegistry)
├── create_bridge(source_beliefs, target_beliefs, bridge_type, ...) -> BridgeWarrant
├── evaluate_bridge(bridge_id, evidence) -> updated confidence
├── record_failure(bridge_id, disconfirming_evidence) -> failure_record
├── compute_bridged_credence(belief_id) -> float
└── suggest_bridges(source_domain, target_domain) -> List[BridgeWarrant candidates]

MODIFICATIONS TO: src/services/extraction_to_web.py
├── Add bridge_type extraction to LLM prompt
├── When mapping claim→belief, check for bridge-relevant claims
├── Propose bridges when cross-domain claims detected

MODIFICATIONS TO: src/services/web_of_belief.py
├── Add method: integrate_bridge(bridge: BridgeWarrant)
├── When bridge integrated, create constraints between connected beliefs
├── Bridge failure creates STRONG_TENSION constraint

MODIFICATIONS TO: app/tasks/pipeline.py
├── After web integration, run bridge detection
├── Output: bridges.jsonl containing all proposed bridges
```

**Test Cases for Sprint 3**:

1. **Basic bridge creation**: Extract claim from Bar & Neta paper, propose mechanism bridge to architectural domain, verify bridge structure matches schema
2. **Bridge-weighted credence**: Given parent theory credence 0.8, mechanism bridge (default 0.6), CNFA-specific 0.9, verify output ≈ 0.432
3. **Bridge failure**: Integrate Vartanian finding that contradicts mechanism bridge, verify:
   - Bridge status changes to "failed"
   - Tension created in web
   - Anomaly record generated
   - VOI flag set
4. **Bridge revision**: After mechanism bridge fails, verify functional bridge can be proposed as alternative
5. **Serialization round-trip**: Create bridge, serialize to JSON, deserialize, verify equality

------

## PART 3: CONSOLIDATED DELIVERABLES

### Sprint 2 Validation Summary

| Decision                    | Verdict                       | Required Changes                                     |
| --------------------------- | ----------------------------- | ---------------------------------------------------- |
| 2.1 Fresh Web Per Paper     | **APPROVED**                  | None                                                 |
| 2.2 Graceful Degradation    | **APPROVED WITH MODS**        | Add WARNING log, error file, --strict flag           |
| 2.3 Schema Formalization    | **REVISION REQUIRED**         | Create formal JSON schemas before Sprint 3           |
| 2.4 Web State Serialization | **REVISION REQUIRED**         | Add constraints, store full content                  |
| 2.5 Equilibrium Parameters  | **APPROVED**                  | Future: make configurable, add convergence detection |
| 2.6 Output Conditionality   | **APPROVED WITH ENHANCEMENT** | Add pipeline_manifest.json                           |

### Sprint 3 Specification Summary

**Objective**: Implement bridge warrant foundation enabling principled knowledge transfer across domains.

**New Files**:

- `src/services/bridge_warrants.py` — Bridge warrant logic
- `contracts/ae_af/schemas/bridge.v1.json` — Schema definition

**Schema**: `ae.bridge.v1` as specified above (all fields documented)

**Formula**:

```
bridged_credence = parent_theory_credence × bridge_confidence × cnfa_specific_confidence
```

**Default P(bridge)**: Constitutive 0.85, Mechanism 0.60, Functional 0.50, Analogical 0.35

**Bridge Lifecycle**:

```
hypothesized → supported (if evidence_for grows)
            → contested (if evidence_for AND evidence_against)
            → failed (if disconfirming evidence strong)
            → revised (if downgraded to different type)
```

**Integration Points**:

- extraction_to_web.py: detect bridge-relevant claims, propose bridges
- web_of_belief.py: integrate bridges, create constraints
- pipeline.py: output bridges.jsonl

**Test Cases**: 5 specified above

**Exit Criteria for Sprint 3**:

1. ✓ `ae.bridge.v1` schema exists and validates
2. ✓ BridgeWarrant class and BridgeRegistry implemented
3. ✓ `compute_bridged_credence()` function works with documented formula
4. ✓ Bridge failure creates tension in web
5. ✓ Pipeline outputs bridges.jsonl
6. ✓ All 5 test cases pass

------

## References

Bar, M., & Neta, M. (2006). Humans prefer curved visual objects. *Psychological Science, 17*(8), 645-648. https://doi.org/10.1111/j.1467-9280.2006.01759.x

Bates, M. J. (2002). Speculations on browsing, directed searching, and linking in relation to the Bradford distribution. In H. Bruce, R. Fidel, P. Ingwersen, & P. Vakkari (Eds.), *Emerging frameworks and methods: Proceedings of the Fourth International Conference on Conceptions of Library and Information Science* (pp. 137-150). Libraries Unlimited.

Bates, M. J. (2005). Information and knowledge: An evolutionary framework for information science. *Information Research, 10*(4), paper 239.

BonJour, L. (1985). *The structure of empirical knowledge*. Harvard University Press.

Cartwright, N. (1983). *How the laws of physics lie*. Oxford University Press.

Cartwright, N. (1999). *The dappled world: A study of the boundaries of science*. Cambridge University Press.

Cartwright, N., & Hardie, J. (2012). *Evidence-based policy: A practical guide to doing it better*. Oxford University Press.

Pearl, J. (2009). *Causality: Models, reasoning, and inference* (2nd ed.). Cambridge University Press.

Pearl, J., & Bareinboim, E. (2014). External validity: From do-calculus to transportability across populations. *Statistical Science, 29*(4), 579-595. https://doi.org/10.1214/14-STS486

Simon, H. A. (1956). Rational choice and the structure of the environment. *Psychological Review, 63*(2), 129-138. https://doi.org/10.1037/h0042769

Simon, H. A. (1996). *The sciences of the artificial* (3rd ed.). MIT Press. (Original work published 1969)

Vartanian, O., Navarrete, G., Chatterjee, A., Fich, L. B., Leder, H., Modroño, C., Nadal, M., Rostrup, N., & Skov, M. (2013). Impact of contour on aesthetic judgments and approach-avoidance decisions in architecture. *Proceedings of the National Academy of Sciences, 110*(Suppl. 2), 10446-10453. https://doi.org/10.1073/pnas.1301227110

------

*Panel review concluded: Sunday, January 18, 2026*
 *Document prepared for handoff to Claude Code implementation*