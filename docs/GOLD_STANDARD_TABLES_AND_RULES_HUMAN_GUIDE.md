# Gold Standard Tables and Rules: Human Guide

Date: February 14, 2026
Audience: Human reviewers, project leads, graduate assistants
Companion to: `docs/GOLD_STANDARD_TABLES_AND_RULES_SPEC.md`

## What this is
This is the practical, plain-language version of the gold standard.
Use it to decide quickly:
- Is this paper extraction usable now?
- Does it need manual correction?
- Is it truly gold-verified?

## One-minute definition of "gold"
A paper is gold-standard only if:
1. Claims are traceable to exact text (section/page/quote/hash).
2. Core fields are complete for that article type.
3. Stimulus details are deep enough when stimulus is central.
4. Relations/theory links are not decorative; they are evidenced.
5. Quality gate passes and unresolved edge cases are reviewed.

### Why each gold attribute exists
1. Traceability:
Without quote/page anchors, errors are hard to detect and impossible to audit.
Traceability prevents hallucinated claims from entering the web/BN.
2. Article-type completeness:
Different paper families answer different questions.
Missing family-critical fields creates misleading summaries and weak downstream rules.
3. Stimulus depth:
In CNfA, intervention/stimulus details often determine whether effects are interpretable or replicable.
Shallow stimulus documentation breaks theory testing and practical design use.
4. Evidenced relations/theory links:
If relation labels are decorative, the argument layer becomes noise.
Evidenced links are required for meaningful contradiction handling and theory comparison.
5. Quality gates + manual review:
Automation scales throughput, but unresolved ambiguity must be surfaced.
Gates and manual queues prevent silent quality drift.

## Quick triage (first pass)
For each paper, check these first:
1. Does it have anchored evidence (`source_section`, `source_page_*`, `source_quote`)?
2. Are environment/outcome mappings mostly resolved?
3. Are relation types reasonable (`supports/explains/contradicts`)?
4. If intro/conclusion mention theory or prior studies, do we have `theory_link` and `inter_article_relation` claims?

If any answer is "no", move the paper to manual review.

## Deep review checklist

### A) Evidence traceability
- Every high-impact claim should be directly traceable to a quote and page.
- No unanchored high-confidence claims.
Rationale: This is the minimum requirement for scientific auditability and error correction.

### B) Article-type completeness
- Empirical papers: sample, design, outcomes, effect/statistics, scope limits.
- Reviews/meta-analyses: synthesis method, inclusion logic, quality comments.
- Theoretical/conceptual papers: propositions, mechanisms, scope/boundaries, testability.
Rationale: Completeness must be judged relative to paper type, not a single generic template.

### C) Stimulus quality
If stimulus is central, verify:
- What stimulus was used (type/modality/source).
- How it was delivered (timing, duration, order).
- What control/comparison was used.
- Ecological realism comments.
Rationale: Stimulus mis-specification is a major source of false equivalence across studies.

## Stimulus Provenance Standard (Human Priority)
This section is mandatory for high-value CNfA papers where the stimulus/setting drives interpretation.

### Why this is non-negotiable
1. Reproducibility:
If the stimulus is not concretely specified, another lab cannot duplicate the experiment.
For visual-spatial studies, textual summaries are often insufficient; human reviewers need access to what participants actually saw.
2. Human interpretability and critique:
To evaluate confounds, boundary conditions, and generalizability, humans need enough detail about the 2D/3D setting and stimulus constraints.
Without this, “effect summaries” can be technically correct but scientifically misleading.

### Minimum human-facing stimulus packet
For each central stimulus condition, provide:
- Stimulus identity:
  stimulus name, modality, source, and exact condition labels.
- Presentation details:
  duration, sequence/order, inter-stimulus interval, exposure context, instructions.
- Geometry/context:
  2D/3D setting description (layout, viewpoint, distance/scale cues, camera path if applicable).
- Control and comparison:
  what differs between conditions and what is held constant.
- Material/lighting/acoustic specifics (as applicable):
  enough to evaluate whether condition differences are plausible confounds.
- Provenance anchors:
  section/page/quote references for each key stimulus claim.
- Visual evidence pointers:
  figure/table identifiers and captions; figures should be stored as extracted assets.
  External figure links should not be used for gold review, except links that resolve to our own DB assets.

### Confound and generality checklist
Human reviewer should explicitly ask:
- Is the effect plausibly driven by unintended stimulus differences?
- Is the stimulus representative of real environments or an artificial edge case?
- Do findings likely transfer across populations/settings/tasks, or only this setup?
- Are there hidden constraints (VR fidelity, rendering, display hardware, viewing angle, noise floor)?

### Gold implication
A paper cannot be considered `gold_verified` for stimulus-driven claims unless the stimulus packet above is present (or missing elements are explicitly marked with reason and risk note).
For figure-dependent claims, `gold_verified` also requires stored figure assets in project-controlled storage.

### D) Relations and theory links
- If the paper says it supports/challenges/refines prior work, relation labels should reflect that.
- Theory mentions should become explicit `theory_link` claims when justified.
- Citation-based relations should map to known paper IDs where possible.
Rationale: The argument layer is only useful if relation semantics are faithful to the text and linked to concrete evidence.

## How to use Codex output safely

Trust Codex most for:
- Consistency checks
- Field completeness checks
- Provenance enforcement
- High-throughput relation extraction candidates
Rationale: These are structured, repeatable tasks where deterministic validation is strong.

Require human confirmation for:
- Ambiguous causal claims
- Thinly evidenced theory interpretations
- Borderline stimulus interpretation
- Conflicts between strong papers
Rationale: These cases require domain judgment, interpretation under uncertainty, and accountability.

## Should we use Claude too?
Yes, as independent cross-check.
Best use:
1. Run Codex and Claude on overlapping PDF sample.
2. Compare key fields and relation decisions.
3. Send disagreements to human adjudication.

This improves quality because disagreement highlights hidden ambiguity.

## Practical labels to use
- `production_usable`: passes core fields and provenance; may still need minor edits.
- `needs_manual_review`: any serious ambiguity/low-confidence gap.
- `gold_verified`: quality gate pass + manual/adjudicated conflict resolution complete.

## Where to look
- Canonical standard: `docs/GOLD_STANDARD_TABLES_AND_RULES_SPEC.md`
- Quality thresholds: `config/table_extraction_quality_thresholds.json`
- Quality gate: `scripts/check_table_extraction_quality.py`
- Manual queue: `data/review/table_quality_manual_queue.csv`

## Reviewer note
The goal is not “no errors ever.” The goal is:
- fast reliable throughput,
- explicit uncertainty,
- targeted human attention on the hardest cases.
