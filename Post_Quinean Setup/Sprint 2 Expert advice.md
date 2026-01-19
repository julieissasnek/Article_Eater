

**Decision 2.1: Fresh Web Per Paper vs. Cumulative**

- Pearl: Would think about this in terms of causal inference - each paper is a distinct data source, but the causal structure we're learning about is unified. Would likely favor cumulative with careful provenance tracking.
- Cartwright: Would emphasize that bridge warrants and domain transfer require seeing patterns across papers - isolated webs can't discover cross-paper tensions or confirmations.
- Simon: Bounded rationality perspective - there's computational and cognitive overhead to cumulative integration. Fresh-per-paper is simpler, debugging is easier. But the scientific goal requires eventual integration.
- Bates: Information science perspective - knowledge organization requires understanding relationships between sources. Fresh-per-paper loses relational structure.
- Kaplan: Environmental psychology domain expert - would want to see how findings from different studies relate to each other. The field is characterized by conflicting findings that need reconciliation.

Verdict: The decision to use fresh-web-per-paper for Sprint 2 is APPROPRIATE given the sprint roadmap (Sprint 5 handles persistence/accumulation), but the panel should note what must be preserved to enable future accumulation.

**Decision 2.2: Graceful Degradation**

- Pearl: Would want to know what failed and why - silent degradation obscures causal understanding of system behavior.
- Cartwright: Would emphasize that the extraction outputs have value independent of web integration.
- Simon: Satisficing principle - getting extraction done is better than getting nothing. But bounded rationality also requires good feedback for learning.
- Bates sees metadata about processing success and failure as essential for information management. Kaplan, as a domain user, needs explicit signals when integration breaks so she doesn't misinterpret incomplete results as complete findings.

Verdict: Graceful degradation works but requires visibility - logs should flag failures prominently, and downstream systems must clearly indicate what was and wasn't integrated.

**Decision 2.3: Schema Formalization**

All panelists converge on the risk of ad-hoc schemas drifting over time. Simon particularly values how formal governance reduces cognitive load and prevents inconsistency creep across the extraction pipeline.

Verdict: Implement formal schemas to anchor the system.

**Decision 2.4: Web State Serialization**

Pearl needs enough detail to reconstruct the Bayesian network or trace how credences were derived. Cartwright wants warrant information preserved. Simon seeks balance between capturing what matters and avoiding unnecessary complexity. Bates emphasizes that metadata standards should guide what gets serialized.

Verdict: Current approach is sound but should capture additional warrant and derivation details.

**Decision 2.5: Equilibrium Parameters**

Pearl flags that five iterations is arbitrary - convergence properties should drive the choice. Simon prefers satisficing over optimization, though configurability lets researchers experiment. Cartwright notes that different papers may need different iteration counts depending on how much tension exists in the network.

Verdict: Make iterations configurable with reasonable defaults rather than fixed.

**Decision 2.6: Output File Conditionality**

Bates emphasizes that consistent output structure enables reliable downstream processing.

Simon points out that error files serve a diagnostic purpose. Rather than omitting outputs when conditions aren't met, structured error or empty files maintain consistency across runs.

Verdict: Generate structured error and empty files to preserve consistent output patterns.

I'll convene the panel now for Sprint 2 deliberations.

------

# Expert Panel Deliberation: Sprint 2 Implementation Review

**Date**: Sunday, January 18, 2026 **Panel Convened For**: Validation of Sprint 2 implementation decisions **Deliverable**: Approve/Revise verdicts with rationale for each decision

------

## Preamble: Panel Methodology

The following deliberation synthesizes perspectives from five scholars whose published work bears directly on the design questions at hand. Each panelist's voice is constructed from their documented intellectual commitments: Pearl's emphasis on causal transparency and graphical model semantics; Cartwright's analysis of warrant structures and domain portability; Simon's satisficing principles and attention to bounded rationality; Bates's information science frameworks for knowledge organization; and Kaplan's grounding in environmental psychology as both methodologist and domain practitioner.

Where panelists would likely agree, I present unified recommendations. Where their frameworks generate productive tension, I make that tension explicit—such disagreements often illuminate genuine design tradeoffs rather than errors.

------

## Decision 2.1: Fresh Web Per Paper vs. Cumulative

### What Was Implemented

Each paper receives a fresh `WebOfBelief` instance. Beliefs do not accumulate across papers within a single pipeline run.

### Panel Deliberation

**Pearl** opens with a structural observation: the Web of Belief is intended to represent a unified epistemic state about how built environments affect cognition. Each paper provides *evidence* bearing on that unified state, not a self-contained epistemic world. From a causal inference standpoint, treating papers as isolated prevents exactly what coherentism promises—the discovery of cross-source tensions and confirmations. When Bar & Neta's amygdala findings meet Vartanian's ACC findings, the *tension itself* is epistemically informative. Isolated webs cannot detect such tensions.

**Cartwright** reinforces this concern from the philosophy of science: bridge warrants, by their very nature, connect findings across studies. A bridge warrant asserting that object-level threat detection mechanisms transfer to architectural scale *requires* beliefs from multiple papers to be co-present for evaluation. Sprint 3's bridge warrant machinery will be crippled if Sprint 2 produces only isolated webs.

**Simon**, however, introduces a crucial pragmatic counterpoint. The sprint roadmap explicitly assigns persistence and accumulation to Sprint 5. There are sound engineering reasons for this sequencing: cumulative integration is substantially more complex (requiring merge semantics, conflict resolution, provenance tracking), and debugging is vastly easier when each paper's integration can be examined in isolation. Building cumulative integration prematurely invites compounding errors that obscure whether problems originate in extraction, mapping, or accumulation logic. Simon would endorse fresh-per-paper *for Sprint 2* as appropriate satisficing—getting the pipeline working end-to-end before adding accumulation complexity.

**Bates** mediates between these positions with an information science lens: the decision is acceptable *if and only if* Sprint 2's outputs preserve everything needed for later accumulation. The web_state.json files must be designed as *mergeable artifacts*—each containing sufficient provenance and structure that Sprint 5 can reconstruct a cumulative web from the collection of per-paper webs.

**Kaplan**, speaking as domain expert, notes that environmental psychology is characterized by apparently conflicting findings that often reflect moderator variables rather than true contradictions. Cross-paper integration isn't optional for the field—it's the primary scientific question. She accepts Sprint 2's isolation as temporary scaffolding but emphasizes urgency for Sprint 5.

### Verdict: **APPROVED WITH CONDITIONS**

The fresh-web-per-paper decision is appropriate for Sprint 2's scope, but the implementation must satisfy a forward-compatibility requirement:

**Condition**: web_state.json must include all information necessary for Sprint 5 merge operations, specifically:

- Full belief content (not truncated)
- Complete provenance chains (paper_id, claim_ids, extraction metadata)
- Constraint serialization (not just beliefs)
- Timestamp and version information for merge conflict resolution

This condition affects Decision 2.4 below.

------

## Decision 2.2: Graceful Degradation

### What Was Implemented

If web_of_belief imports fail or integration throws an exception, the pipeline continues and produces extraction outputs (claims.jsonl, rules.jsonl) with `"web_integration": "skipped"` or `"failed"`. Integration failures do not block extraction.

### Panel Deliberation

**Simon** provides the framework here: this is a classic satisficing decision, and it's correct. The extraction pipeline and the web integration are *separable value streams*. A user who wants claims.jsonl should not be blocked by an unrelated failure in coherence computation. The system delivers partial value rather than total failure—this is sound bounded rationality.

**Cartwright** agrees but adds a caveat from her work on evidence and policy: silent degradation creates epistemic risk. A downstream consumer who sees claims.jsonl might reasonably assume those claims were coherence-checked, especially once the system matures and web integration becomes routine. The silence creates a false confidence problem.

**Pearl** sharpens this to a transparency requirement: his work on causal models emphasizes that understanding *why* something happened is as important as knowing *that* it happened. A logged "web_integration: failed" is insufficient—the failure reason must be captured and surfaced. Was it an import error (environment problem)? A schema mismatch (versioning problem)? A coherence explosion (algorithmic problem)? Different failures have different implications for trust in the extraction outputs themselves.

**Bates** frames this as a metadata quality issue: the output manifest should distinguish between "integration was not attempted," "integration failed with error X," and "integration succeeded." These are categorically different states with different downstream implications.

**Kaplan** adds a user perspective: as a researcher, she would want to know if her paper's findings couldn't be integrated. Silent degradation means she might not realize her work was excluded from the web, which could lead to incorrect conclusions about the state of evidence in the field.

### Verdict: **APPROVED WITH REVISIONS**

Graceful degradation is the correct architectural choice. However, the implementation requires enhancement:

**Revision 1**: Failure logging must capture structured error information:

json

```json
{
  "web_integration": "failed",
  "failure_stage": "import|mapping|equilibrium|serialization",
  "error_type": "ImportError|ValidationError|CoherenceError|...",
  "error_message": "...",
  "recoverable": true|false
}
```

**Revision 2**: Pipeline logs should emit a WARNING-level message (not just DEBUG) when integration fails, ensuring operators notice degraded runs.

**Revision 3**: The coherence_summary.json file should be written even on failure (see Decision 2.6), containing the error structure above rather than being absent.

------

## Decision 2.3: Schema Formalization

### What Was Implemented

Schemas were invented ad hoc during implementation (`ae.web_state.v1`, `ae.coherence_summary.v1`) without formal JSON schema definitions in `contracts/ae_af/schemas/`.

### Panel Deliberation

The panel reaches rapid consensus on this decision, which is unusual and therefore noteworthy.

**Bates** is most emphatic: the absence of formal schemas violates fundamental principles of knowledge organization. Schemas are not bureaucratic overhead—they are *contracts* that enable interoperability, validation, and evolution. Without formal schemas, the "v1" version string is meaningless; there is no machine-readable specification against which to validate outputs or detect breaking changes. This is technical debt that compounds over time.

**Simon** agrees, framing it in terms of cognitive load: ad hoc schemas require every downstream consumer (including future Claude Code instances) to reverse-engineer the structure from examples. Formal schemas externalize this knowledge, reducing the bounded rationality burden on future developers.

**Pearl** adds that formal schemas enable automated validation in the pipeline itself—a web_state.json file can be checked against the schema before being written, catching structural errors at production time rather than consumption time.

**Cartwright** notes that bridge warrants will require careful schema work (Sprint 3), and establishing schema governance now creates the infrastructure that Sprint 3 will need.

**Kaplan** observes that as the system scales to dozens or hundreds of papers, schema drift will become invisible without formal validation. A paper processed in month 6 might produce subtly different web_state.json than a paper processed in month 1, and no one will notice until analysis fails mysteriously.

### Verdict: **REVISE**

Formal JSON schemas must be created for all new output types. Specifically:

1. Create `contracts/ae_af/schemas/ae.web_state.v1.json`
2. Create `contracts/ae_af/schemas/ae.coherence_summary.v1.json`
3. Add schema validation to the pipeline before file write
4. Document schema evolution policy (how will v2 be introduced?)

The panel recommends JSON Schema Draft 2020-12 for the schema language, consistent with modern tooling.

------

## Decision 2.4: Web State Serialization

### What Was Implemented

The web_state.json includes: schema version, run/paper identifiers, timestamps, belief/constraint counts, coherence score, and a beliefs dictionary with truncated content (200 chars), level, status, credence, theory_id, and entrenchment. Constraints are not serialized.

### Panel Deliberation

**Pearl** immediately flags the constraint omission: the Bayesian Network is generated *from* the constraint structure. If constraints are not serialized, the BN cannot be reconstructed, and the web_state.json is a lossy representation that discards the relational structure that makes it a *web* rather than a *bag of beliefs*. This is a significant deficiency.

**Cartwright** amplifies the concern: constraints encode the *warrant relationships* between beliefs. A belief that "angular rooms increase arousal" might be constrained by (warrant-linked to) an underlying mechanism belief about amygdala activation. Without constraints, we lose exactly the inferential structure that coherentism cares about.

**Simon** introduces a tradeoff consideration: full constraint serialization increases file size and complexity. If web_state.json is intended only for human inspection and summary statistics, full constraints may be unnecessary. But if it's intended for Sprint 5 persistence and web reconstruction, constraints are mandatory.

**Bates** resolves this by distinguishing use cases: the system should produce *two* outputs:

- A **summary file** (coherence_summary.json) for human inspection, dashboards, and quick assessment
- A **full state file** (web_state.json) for persistence, reconstruction, and programmatic consumption

The current web_state.json conflates these purposes.

**Kaplan** adds that belief content truncation (200 chars) is problematic for environmental psychology findings, which often require contextual detail. "Curved architectural elements reduce stress in healthcare settings among elderly patients with chronic conditions" cannot be meaningfully truncated to 200 characters without losing critical moderator information.

### Verdict: **REVISE**

The serialization strategy requires restructuring:

**Revision 1**: Include full constraint serialization in web_state.json:

json

```json
{
  "constraints": {
    "constraint_id": {
      "type": "SUPPORTS|TENSIONS|ENTAILS|...",
      "source_belief_id": "...",
      "target_belief_id": "...",
      "strength": 0.8,
      "warrant_type": "empirical|theoretical|methodological",
      "provenance": "..."
    }
  }
}
```

**Revision 2**: Store full belief content, not truncated. If file size is a concern, implement optional compression (gzip) rather than lossy truncation.

**Revision 3**: Confirm that the serialization format aligns with `WebOfBelief` reconstruction requirements—Claude Code should verify that `WebOfBelief.from_state(web_state)` is implementable from this schema.

------

## Decision 2.5: Equilibrium Parameters

### What Was Implemented

Hardcoded `seek_equilibrium=True` and `equilibrium_iterations=5`.

### Panel Deliberation

**Pearl** notes that equilibrium convergence is an empirical question, not a constant. A web with many tensions may require more iterations; a web with few beliefs may converge in two. Hardcoding 5 iterations means some papers will undergo unnecessary computation while others will terminate before convergence. At minimum, convergence should be *detected* (has the coherence score stabilized?) rather than iteration-counted.

**Simon** frames this as premature optimization: for Sprint 2, hardcoded defaults are acceptable. The goal is to get the pipeline working, not to tune equilibrium parameters. However, he would insist on *logging* the convergence trajectory (coherence score at each iteration) so that future optimization has data to work from. Satisficing now; data collection for later refinement.

**Cartwright** raises a deeper question: should equilibrium-seeking be optional? Some users might want the "raw" integration result before coherence pressures redistribute credences. This is philosophically significant—it's the difference between reporting what the paper claims and reporting what's *coherent given everything else we know*. Both have legitimate uses.

**Bates** suggests a profile-based approach: different use cases warrant different equilibrium strategies. Extraction-for-archiving might want no equilibrium; extraction-for-synthesis might want aggressive equilibrium. This should be configurable at the profile level, not hardcoded.

**Kaplan** adds that in environmental psychology, premature equilibrium can mask genuine disagreements in the field. If one paper finds that nature views reduce stress and another finds they increase arousal, forced equilibrium might artificially moderate both findings rather than preserving the tension for human examination.

### Verdict: **REVISE**

Equilibrium parameters should be configurable with sensible defaults:

**Revision 1**: Add to profile configuration:

yaml

```yaml
web_integration:
  seek_equilibrium: true  # default
  equilibrium_strategy: "iteration_count|convergence_threshold|none"
  max_iterations: 10  # default, safety bound
  convergence_threshold: 0.001  # coherence score delta
```

**Revision 2**: Log convergence trajectory regardless of strategy:

json

```json
{
  "equilibrium_log": [
    {"iteration": 0, "coherence": 0.312},
    {"iteration": 1, "coherence": 0.387},
    {"iteration": 2, "coherence": 0.401},
    {"iteration": 3, "coherence": 0.403},
    {"iteration": 4, "coherence": 0.403}
  ],
  "converged": true,
  "converged_at_iteration": 3
}
```

**Revision 3**: For Sprint 2, hardcoded defaults are acceptable as interim implementation, but the configuration infrastructure should be specified now for Sprint 4+ implementation.

------

## Decision 2.6: Output File Conditionality

### What Was Implemented

New files (web_state.json, stubs.jsonl, tensions.jsonl, coherence_summary.json) are only written if integration succeeds. On failure, these files are not created.

### Panel Deliberation

**Bates** identifies this as an information architecture anti-pattern: file presence/absence as a signaling mechanism creates fragile downstream logic. Consumers must check for file existence before processing, and absence is ambiguous—does it mean failure, or does it mean the pipeline version predates web integration? Explicit is better than implicit.

**Simon** agrees from a debugging perspective: when investigating a failed run, the operator must infer the failure point from which files exist. An explicit error file is vastly more informative than a missing file.

**Pearl** extends this to causal diagnosis: an error file with structured information (see Decision 2.2) allows automated analysis of failure patterns across many runs. Missing files cannot be analyzed.

**Cartwright** and **Kaplan** concur without significant additions.

### Verdict: **REVISE**

All expected output files should be written, with failure states explicitly represented:

**Revision 1**: On integration failure, write coherence_summary.json containing:

json

```json
{
  "schema": "ae.coherence_summary.v1",
  "status": "failed",
  "failure_stage": "...",
  "error_type": "...",
  "error_message": "...",
  "extraction_succeeded": true,
  "web_integration_succeeded": false
}
```

**Revision 2**: On integration failure, write web_state.json containing:

json

```json
{
  "schema": "ae.web_state.v1",
  "status": "failed",
  "paper_id": "...",
  "run_id": "...",
  "error": { ... },
  "beliefs": {},
  "constraints": {}
}
```

**Revision 3**: stubs.jsonl and tensions.jsonl may remain absent on failure (they are derivative outputs that require successful integration to exist), but this should be documented in schema documentation.

------

## Summary: Sprint 2 Verdicts

| Decision                       | Verdict                      | Key Revision                                    |
| ------------------------------ | ---------------------------- | ----------------------------------------------- |
| 2.1 Fresh Web Per Paper        | **APPROVED WITH CONDITIONS** | Ensure web_state.json supports Sprint 5 merge   |
| 2.2 Graceful Degradation       | **APPROVED WITH REVISIONS**  | Structured error capture, WARNING-level logging |
| 2.3 Schema Formalization       | **REVISE**                   | Create formal JSON schemas in contracts/        |
| 2.4 Web State Serialization    | **REVISE**                   | Include constraints, full belief content        |
| 2.5 Equilibrium Parameters     | **REVISE**                   | Make configurable, log convergence trajectory   |
| 2.6 Output File Conditionality | **REVISE**                   | Write error-state files, not absent files       |

------

## References

Bates, M. J. (1999). The invisible substrate of information science. *Journal of the American Society for Information Science*, 50(12), 1043–1050. https://doi.org/10.1002/(SICI)1097-4571(1999)50:12<1043::AID-ASI1>3.0.CO;2-X

Cartwright, N. (1999). *The dappled world: A study of the boundaries of science*. Cambridge University Press.

Kaplan, R., & Kaplan, S. (1989). *The experience of nature: A psychological perspective*. Cambridge University Press.

Pearl, J. (2009). *Causality: Models, reasoning, and inference* (2nd ed.). Cambridge University Press.

Simon, H. A. (1956). Rational choice and the structure of the environment. *Psychological Review*, 63(2), 129–138. https://doi.org/10.1037/h0042769

Simon, H. A. (1996). *The sciences of the artificial* (3rd ed.). MIT Press.