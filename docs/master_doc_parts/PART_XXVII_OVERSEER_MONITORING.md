# §184. Overseer Health Monitoring: Invariants, Playbooks, and Remediation

**Date**: 2026-03-05
**Part**: PART XXVII (Operational Pipelines)
**Status**: Foundational specification for self-monitoring and maintenance

---

## §184.1: Philosophy and Design Principles

The ATLAS system maintains a vast and intricate web of beliefs, evidence relationships, and meta-epistemic structures. As the knowledge base grows and as new papers are integrated, the system must ensure that epistemic integrity is maintained—that beliefs have proper justification, that coherence is preserved, that pipelines remain healthy. Manual inspection by humans cannot scale to thousands of beliefs and relationships. Instead, the system must monitor itself.

The OVERSEER system is a Dijkstra-inspired watchdog that operates above the web of belief, conducting continuous automated audits and triggering remediations when violations are detected. The name evokes Dijkstra's concept of the superordinate program (Dijkstra, 1968): a program that monitors and enforces invariants on the system below it, ensuring that the system remains in valid states.

OVERSEER is guided by eight design principles:

1. **Separation of Concerns**: OVERSEER operates in a separate database (overseer.db) and does not modify the epistemic network unless remediation is explicitly triggered.

2. **Statistical Alerting**: Rather than flagging every anomaly, OVERSEER uses per-theory baselines. A belief's credence is judged against the mean and variance of credences in its theory cluster; deviations beyond 1–2 standard deviations trigger alerts.

3. **Quarantine, Not Auto-Retire**: When a problem is detected (inconsistency, warrant gap), the affected belief is flagged for manual human review rather than automatically deleted or downgraded.

4. **BN-Web Synchronization**: Edges in the Bayesian network must reflect credences in the web of belief. OVERSEER verifies this consistency nightly.

5. **Real-Time Conflict Detection**: Certain invariants (like "no belief has credence outside [0, 1]") are checked immediately on every write.

6. **Provenance Verification**: Every belief must have documented justification (Haack's foundherentism requirement). OVERSEER audits that justifications are sound and sufficient.

7. **Parnas Database Separation**: OVERSEER maintains its own database, enforcing information hiding and preventing OVERSEER anomalies from corrupting the epistemic network.

8. **Graceful Degradation**: Optional monitoring modules do not break the core system. If a module fails, it is disabled and logged.

---

## §184.2: Invariants and Success Conditions

The ATLAS system enforces a set of 20 invariants—conditions that must hold if the system is healthy. These invariants range from trivial (credences in [0, 1]) to sophisticated (coherence metrics, pipeline utilization). They are organized into four tiers.

**Tier 0: Bootstrap Invariants** (Checked at startup)

**INV-0: System is in OPERATIONAL state** — The core databases are accessible, the web of belief has loaded, pipelines are initialized. If this fails, no other invariants matter; the system is down.

**Tier 1: Immediate Invariants** (Checked on every write)

These are simple checks that must always be true. They are checked in microseconds and cannot be deferred.

**INV-1: Every belief has provenance** — Each belief in the epistemic network carries a justification structure (warrant chain, supporting papers, credence intervals). No belief exists without documented grounds. Violation: belief created without justification record.

**INV-2: BN edges reflect web credences** — Each edge in the Bayesian network has a probability that should match or closely approximate the credence of the corresponding relationship in the web of belief. Violation: edge probability and web credence diverge by more than 0.05.

**INV-3: All beliefs conform to ClaimV2 schema** — Every belief in the system is a valid JSON object matching the ClaimV2 schema (defining claim structure, fields, required properties). Violation: a belief violates the schema.

**INV-4: Credence values are valid** — Each credence is a float in [0, 1]. Violation: credence outside range.

**Tier 2: Post-Integration Invariants** (Checked within 5 seconds after paper integration)

When a new paper is integrated, the system updates the web of belief. These invariants are checked immediately after.

**INV-5: Coherence decline ≤ 5%** — When new beliefs are added or credences updated, the overall coherence of the web (measured by Quine-style coherence metrics) should not decline by more than 5%. Large declines suggest that the new evidence conflicts with existing beliefs in problematic ways. Violation: coherence drops by ≥ 5%.

**INV-6: Pipeline utilization ≥ 25%** — At least 25% of template slots have been filled with claims from extracted papers, indicating that the extraction process is reaching diverse domains. Violation: utilization < 25%.

**INV-7: Template coverage ≥ 80%** — At least 80% of defined templates (causal relationships like "daylight → alertness") have at least one claim instantiating them. Violation: coverage < 80%.

**INV-8: Theory orphan rate ≤ 10%** — At most 10% of theories have fewer than 3 supporting beliefs. Orphan theories indicate that theoretical frameworks are not being well-grounded in claims. Violation: orphan rate > 10%.

**INV-9: Paper-sourced evidence ≥ 20%** — At least 20% of beliefs are grounded in integrated papers (as opposed to seeded beliefs or theoretically-derived beliefs without empirical support). Violation: sourced evidence < 20%.

**INV-10: Extraction quality mean score ≥ 0.75** — The quality assurance pipeline assigns scores to extracted claims (0–1 scale, measuring fidelity to source and absence of errors). The mean across recent extractions should be ≥ 0.75. Violation: mean QA score < 0.75.

**Tier 3: Nightly Invariants** (Checked in full audit, 15 minutes daily)

These invariants involve more complex computations and are checked nightly rather than immediately.

**INV-11: T3 classification rate ≥ 70%** — Tier 3 theories (synthesized frameworks) should have at least 70% of their constituent claims classified as T3-relevant (belonging to the T3 frameworks). Violation: classification rate < 70%.

**INV-12: T3 established beliefs ≥ 200** — The T3 belief engine should have identified at least 200 distinct, well-supported beliefs at the T3 level (scientific consensus claims). Violation: count < 200.

**INV-13: Field reviewer terminal rate ≤ 10%** — When domain expert field reviewers evaluate extracted claims, at most 10% should result in "terminal" rejections (claims so flawed they cannot be salvaged). Higher rates indicate systematic extraction errors. Violation: rejection rate > 10%.

**INV-14: Card generation queue depth ≤ 50** — The card generation pipeline should not accumulate more than 50 pending cards; deeper queues indicate the system is falling behind. Violation: queue depth > 50.

**INV-15: Stale card ratio ≤ 20%** — Cards are marked stale if the underlying belief credence has changed significantly since the card was created. At most 20% of cards should be stale at any time. Violation: stale ratio > 20%.

**INV-16: Card two-pass pipeline health** — The card generation system operates in two passes (first pass: raw card generation; second pass: enrichment and refinement). Both passes should complete for at least 95% of cards within 24 hours of belief update. Violation: completion rate < 95%.

**INV-17: Sources tab coverage ≥ 80%** — Each card includes a sources/methods section explaining how the finding was derived. At least 80% of empirical cards should have this section filled. Violation: coverage < 80%.

**INV-18: Stimulus description coverage ≥ 50%** — For empirical findings, at least 50% should include detailed description of the stimulus (e.g., "angular shapes at 45-degree angles, presented for 100ms"). Violation: coverage < 50%.

**INV-19: Session card writer claim integrity** — The session card writer (used for real-time card generation during QA interactions) should not create duplicate claims or orphaned claims. Violation: duplicates detected or orphaned claims found.

---

## §184.3: Measurement and Quantification

Most invariants are quantitative and can be checked automatically. Here are measurement details for a few critical ones:

**Coherence Metric (INV-5)**: The system computes coherence using a variant of the Quine-Haack coherence measure. Briefly, coherence depends on:

$$\text{Coherence} = 1 - \frac{\sum_{i,j} \text{conflict}(B_i, B_j)}{n(n-1)} + \frac{\sum_{i,j} \text{support}(B_i, B_j)}{n(n-1)}$$

Where conflict measures the degree to which two beliefs contradict each other (via warrant chains, empirical evidence), and support measures the degree to which they reinforce each other (via argumentation, shared warrants, coherence relationships). A change in coherence ≥ 5% is flagged.

**Template Coverage (INV-7)**: The system counts the total number of defined templates (causal relationships, e.g., "angular-objects" → "negative-affect-amygdala"). For each template, it checks whether at least one belief instantiates it (claim exists for that relationship). Coverage is the fraction of instantiated templates.

**Quality Score (INV-10)**: Each extracted claim receives a quality score from the extraction validation pipeline:

- 0.0–0.3: Claim is inaccurate or contradicts source; should be rejected.
- 0.3–0.6: Claim is partially accurate but has significant gaps or ambiguities.
- 0.6–0.8: Claim is accurate; minor issues in formulation or scope specification.
- 0.8–1.0: Claim is accurate, well-specified, with proper boundary conditions.

The QA process samples recent claims and scores them. The mean score is compared to the threshold (0.75). If mean < 0.75, the system flags a quality issue.

---

## §184.4: Alert Triggering and Severity Classification

When an invariant violation is detected, the system generates an alert with a severity level:

**Severity 0 (Critical)**: The system's operation is compromised. Examples: INV-0 (not operational), INV-2 (BN-web sync broken). Action: Immediate alert to operators; system may enter degraded mode or lockdown.

**Severity 1 (High)**: Core epistemic integrity is at risk. Examples: INV-1 (belief without provenance), INV-5 (large coherence drop). Action: Alert to operators; proposed remediation displayed; human approval required before action.

**Severity 2 (Medium)**: System quality is degraded but operation is not compromised. Examples: INV-14 (queue depth rising), INV-15 (stale cards increasing). Action: Logged alert; proposed remediation scheduled; executed automatically if user approves.

**Severity 3 (Low)**: System is operating normally but could be improved. Examples: INV-8 (orphan rate slightly above threshold). Action: Logged for review; displayed in nightly dashboard; remediation optional.

---

## §184.5: Playbooks and Remediation Protocols

When an invariant is violated, OVERSEER consults a playbook—a set of remediation steps tailored to the violation. Each playbook includes:

1. **Diagnosis**: What was the violation, and why did it occur?
2. **Options**: Multiple remediation strategies with trade-offs.
3. **Recommended Action**: The action most likely to resolve the issue.
4. **Verification**: How to check that the remediation worked.

**Example Playbook: INV-5 Violation (Coherence Decline ≥ 5%)**

```
Violation: Integration of paper P reduced coherence from 0.72 to 0.68 (4.9% drop).

Diagnosis:
  Paper P claims X, but belief B contradicts X. The system attempted to integrate
  X into the web but the integration reduced overall coherence. Possible causes:
  - X is genuinely flawed and should be rejected.
  - X is correct but contradicts a false belief B, which should be downgraded.
  - X applies to a narrower population/context than B and should be scoped differently.

Options:
  1. QUARANTINE X: Mark claim X for manual review before integration.
     Restore coherence immediately. (Fast, but delays integration.)

  2. DOWNGRADE B: Reduce credence of belief B, assuming X is correct.
     Improves coherence if B was less reliable than X.
     (Risky if B is well-grounded.)

  3. SCOPE_SPLIT: Reframe B as applying to context C1; reframe X as applying
     to context C2. Different scopes = no contradiction.
     (Precise, but requires domain knowledge.)

  4. ACCEPT_DROP: Keep X integrated; accept the coherence drop.
     (Honest but indicates unresolved dispute.)

Recommended Action:
  1. Examine the warrant chains supporting B and X.
  2. If X's warrant is stronger (more papers, higher quality), DOWNGRADE B.
  3. If B's warrant is stronger, QUARANTINE X.
  4. If warrants are comparable, investigate whether X and B can be scoped
     to different populations (SCOPE_SPLIT).

Verification:
  Recompute coherence. If drop is ≤ 1%, remediation succeeded.
  If drop remains ≥ 5%, escalate to human expert review.
```

**Example Playbook: INV-14 Violation (Card Generation Queue Depth > 50)**

```
Violation: Card generation queue has 75 pending cards; normal is 5–20.

Diagnosis:
  The card generation pipeline is not keeping up with the rate of belief updates.
  Possible causes:
  - Recent paper integration created many new beliefs, exceeding generation capacity.
  - A generation service is slow or hung.
  - System load is high, competing for CPU.

Options:
  1. INCREASE_WORKERS: Spin up additional card generation worker processes.
     (Fast parallelization; requires CPU availability.)

  2. REDUCE_ENRICHMENT: Run cards through first pass (raw generation) only;
     defer enrichment (second pass) until queue clears.
     (Produces lower-quality cards temporarily.)

  3. PRIORITIZE_QUEUE: Reorder queue to prioritize high-impact beliefs
     (frequently referenced, high credence). Complete those first; leave
     low-impact cards for later.
     (Pragmatic; some cards remain pending longer.)

  4. EXTEND_DEADLINE: Relax INV-14 threshold temporarily (e.g., allow depth
     up to 100 for 24 hours).
     (Honest but decreases system responsiveness.)

Recommended Action:
  1. Check CPU and memory availability. If high (>80% CPU), REDUCE_ENRICHMENT.
  2. If resources available, INCREASE_WORKERS to 2x normal.
  3. Once queue clears, return to normal worker count.
  4. If queue does not clear within 2 hours, escalate.

Verification:
  Queue depth returns to normal (<30) within 30 minutes.
```

---

## §184.6: The Nightly Pipeline and Periodic Audits

Each night at 2 AM (configurable), the OVERSEER system runs a full audit:

1. **Checkpoint**: Create a snapshot of the web of belief, BN, and card system.

2. **Invariant Checks**: Run all 20 invariants against the snapshot.

3. **Alert Aggregation**: Collect all violations and organize by severity.

4. **Playbook Consultation**: For each violation, consult the playbook and compute recommended remediations.

5. **Health Report Generation**: Assemble a report summarizing:
   - Which invariants were violated
   - Severity and recommended actions
   - Automatic actions taken (if any)
   - Manual actions required

6. **Dashboard Update**: Push the health report to the system dashboard, visible to operators.

7. **Logging**: Log all decisions (which invariants checked, results, actions recommended).

8. **Remediation Execution**: Execute automatic low-risk remediations (e.g., queue rebalancing). Defer high-risk remediations (e.g., belief downgrading) for human approval.

The full nightly audit takes approximately 15 minutes and generates a JSON report stored in `overseer.db/nightly_audits/`.

---

## §184.7: AESHI Score: Aggregate Epistemic System Health Index

To summarize the system's overall health into a single number, OVERSEER computes the AESHI score (Aggregate Epistemic System Health Index), a weighted average of normalized invariant metrics:

$$\text{AESHI} = \sum_{i=1}^{20} w_i \cdot \text{normalize}(m_i)$$

Where:

- $m_i$ is the measured value for invariant $i$
- $\text{normalize}(m_i)$ converts the metric to a 0–1 scale, where 1 is optimal
- $w_i$ is the weight for invariant $i$ (critical invariants get higher weight)

For example:

- INV-5 (coherence decline) is weighted 0.15 (critical for epistemic integrity)
- INV-10 (extraction quality) is weighted 0.10 (important for data quality)
- INV-14 (queue depth) is weighted 0.02 (important for responsiveness but not core integrity)

The AESHI score ranges from 0 to 1. Interpretation:

- **AESHI ≥ 0.9**: System is healthy; minor issues only.
- **AESHI 0.8–0.9**: System is operating but with some degradation; monitor and fix low-risk issues.
- **AESHI 0.7–0.8**: System has moderate issues; some auto-remediation occurred; review alerts.
- **AESHI < 0.7**: System is unhealthy; expert intervention required.

The AESHI score is displayed on dashboards and used to trigger escalations (if AESHI drops below 0.75, alert the chief maintainer).

---

## §184.8: Failure Recovery and Graceful Degradation

When OVERSEER detects a critical failure, it does not crash the system. Instead, it activates graceful degradation:

- **QA Pipeline**: If the card system fails to keep up, the QA pipeline operates with slightly stale cards but continues functioning.
- **Belief Credence Updates**: If coherence computation becomes slow, updates proceed with cached coherence values, recomputed asynchronously.
- **Enrichment Services**: If an enrichment service fails, the QA pipeline returns less-enriched answers rather than failing entirely.
- **Database Isolation**: If overseer.db becomes corrupted, the overseer system disables itself but leaves the epistemic network and QA pipeline operational.

This design ensures that the system fails slowly and gracefully rather than abruptly.

---

## §184.9: Human-in-the-Loop Approval and Expert Override

For high-risk remediations (downgrading a well-supported belief, quarantining recent evidence), OVERSEER requires explicit human approval. The approval interface displays:

1. **Violation Summary**: What invariant was violated and why.
2. **Affected Beliefs**: Which beliefs are involved.
3. **Proposed Remediation**: What OVERSEER recommends.
4. **Risk Assessment**: What could go wrong if this remediation is applied.
5. **Alternative Actions**: Other remediation options with trade-offs.

A maintainer reviews this information and selects an action (approve remediation, choose alternative, defer decision, escalate to expert panel). OVERSEER logs this decision and acts on the human's choice.

---

## §184.10: Design Rationale and Philosophical Foundations

Why does ATLAS need an overseer? Because the system's integrity cannot be maintained by humans alone. As the knowledge base grows to thousands of beliefs and relationships, manual inspection becomes impossible. Automatic checking is necessary.

But why avoid auto-correction? Because the most important decisions (downgrading a belief, accepting incoherence) require human judgment and domain expertise. OVERSEER detects problems and recommends solutions, but humans make final decisions. This is the principle of "human-in-the-loop" from human-computer interaction and AI safety literature.

The design also reflects principles from Dijkstra (1968) and Parnas (1972) on program correctness and information hiding. By maintaining OVERSEER in a separate database and requiring human approval for consequential changes, the system ensures that OVERSEER errors do not cascade into the epistemic network.

---

## §184.11: Integration with Other Subsystems

OVERSEER depends on and monitors all other subsystems:

- **Web of Belief**: Checks invariants INV-1 through INV-5 (belief integrity)
- **Bayesian Network**: Checks INV-2 (BN-web sync)
- **Card System**: Checks INV-14 through INV-19 (card quality and pipeline health)
- **QA Pipeline**: Checks INV-10 (extraction quality, implicit in QA results)
- **Extraction Pipeline**: Provides quality scores for INV-10
- **Template Library**: Checks INV-6, INV-7 (coverage and utilization)
- **Bridge Warrant System**: Verifies consistency of discounts factors and applicability
- **ArgumentationGraph**: Detects unresolved disputes that might indicate coherence issues

OVERSEER also integrates with the interpretation space (§176): when a zone-3 gap is identified as part of epistemic planning, the OVERSEER system prioritizes its resolution in the playbooks.

---

## §184.12: Cross-References and Related Sections

- **§176** (Interpretation Space): Endogenous value for gap resolution; zone transitions trigger overseer attention.
- **§177** (Argumentation System): Disputes and debate clusters inform coherence assessment.
- **§181** (QA Pipeline): Pipeline health is monitored via INV-14 through INV-19.
- **§182** (Bridge Warrants): Bridge discount factors are validated against empirical outcomes.
- **§183** (Argumentation Graph): Coherence and debate-driven priorities inform maintenance actions.

---

**References**

Dijkstra, E. W. (1968). The structure of the "THE" multiprogramming system. *Communications of the ACM*, 11(5), 341–346.

Haack, S. (1993). *Evidence and Inquiry: Towards Reconstruction in Epistemology*. Blackwell.

Parnas, D. L. (1972). On the criteria to be used in decomposing systems into modules. *Communications of the ACM*, 15(12), 1053–1058.

Pearl, J. (2009). *Causality: Models, Reasoning, and Inference* (2nd ed.). Cambridge University Press.
