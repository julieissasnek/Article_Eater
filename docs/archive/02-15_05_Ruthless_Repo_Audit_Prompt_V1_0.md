# RUTHLESS REPO AUDIT PROMPT
## Article Eater — Full System Reality Check
## February 15, 2026

---

# YOUR TASK

You have access to the entire Article Eater codebase and all associated repositories. Your job is to produce a structured, honest, unflinching audit that tells us exactly where things stand — what exists, what's broken, what's missing, what contradicts what, and what's going to bite us when we start the next implementation sprint.

**Do not be polite. Do not soften findings. Be precise and cite file paths.**

---

# SECTION 1: CODEBASE REALITY MAP

## 1.1 What Actually Exists

For EACH of the following, report: **EXISTS (path)** or **DOES NOT EXIST** or **PARTIAL (path, what's missing)**.

**Data Models / Schemas:**
- [ ] Node model (claims, beliefs) — what fields does it actually have?
- [ ] Edge/Link model — what fields?
- [ ] Enum: node_domain — list all current values
- [ ] Enum: node_subtype — list all current values
- [ ] Enum: link_type — list all current values
- [ ] Any existing bridge warrant model or schema
- [ ] Any existing theory/framework model
- [ ] Any existing template/mechanism model
- [ ] Any existing ResearchTarget or queue model

**Inference / Reasoning Engines:**
- [ ] Bayesian Network assembly — what library? What's the graph structure?
- [ ] Coherence / constraint satisfaction — algorithm used? Working?
- [ ] Entrenchment scoring — how computed? What inputs?
- [ ] Any existing CMR or prediction generation code
- [ ] Any existing gap detection / gap predictor

**Extraction Pipeline:**
- [ ] PDF extraction — what tool? (GROBID? PyMuPDF? LLM?)
- [ ] Claim extraction — rule-based? LLM? What's the prompt/template?
- [ ] Metadata extraction (authors, affiliations, sample size, study design)
- [ ] Method identification (instruments, biomarkers)
- [ ] Any existing source quality scoring

**Data / Artifacts:**
- [ ] How many papers processed? Where stored?
- [ ] What format are extracted claims in? (JSON? CSV? DB?)
- [ ] Any existing test fixtures or test corpora?
- [ ] Database(s) — what kind? Schema?

**Tests:**
- [ ] Test framework (pytest? jest? other?)
- [ ] Total test count and pass/fail state RIGHT NOW
- [ ] Test coverage percentage if measurable
- [ ] Any CI/CD pipeline?

**Configuration / Infrastructure:**
- [ ] How is the project structured? Monorepo? Multiple repos?
- [ ] Python version? Node version? Key dependencies?
- [ ] Any Docker / containerization?
- [ ] Any deployment config?

## 1.2 Architecture Diagram

Draw (in ASCII or mermaid) the ACTUAL data flow as it exists today:
```
Paper PDF → [what] → [what] → [what] → stored where?
```

Don't draw what the specs say should exist. Draw what the code actually does.

---

# SECTION 2: SPECIFICATION vs. REALITY GAPS

## 2.1 Documents to Check

The following specification documents exist in `docs/` (or should be placed there). For each, check whether the code matches what the spec says should exist.

| Document | What It Specifies |
|----------|-------------------|
| `CLAUDE.md` | Overall architecture, four channels, three tiers |
| `IMPLEMENTATION_TASKS.md` | Sprints 0–5 (Epistemic Tier 2) — 30+ atomic tasks |
| `Theory_Tier_Architecture_V1_0.md` | 8 Tier 1 frameworks, criteria, tier hierarchy |
| `CMR_Spec_V1_0.md` | 6-step CMR pipeline |
| `CMR_Revised_Spec_Panel_Templates_V2_0.md` | Templates 1–20, panel critique |
| `Neuroscience_Panel_Tier1_Frameworks_V1_0.md` | Template corrections, Templates 21–30 context |
| `Neuroscience_Panel_Templates_and_Taxonomy_V1_0.md` | Templates 21–30 fully specified |
| `Panel_III_Multimodal_Senses_HigherCognition_V1_0.md` | Templates 31+, quantitative params |
| `Queue_Prioritization_Panel.md` | Priority formula, satisficing rules |
| `Pipeline_Expectation_Tests.md` | Guardrail tests, data expectations |
| `Ecological_Validity_Background_V1_0.md` | Task-ecological validity, method registry |
| `Claude_Code_Master_Sprint_Plan_V1_0.md` | Sprints 6–9 (queue, theory tier, CMR, health) |

## 2.2 For Each Spec Document, Report

1. **Implementation status**: What percentage of what it specifies actually exists in code? (0%, 25%, 50%, 75%, 100%)
2. **Stale assumptions**: Does the spec assume code structures that don't exist or have changed? List each.
3. **Contradictions with other specs**: Does this document contradict anything in another spec document? Be specific — quote the conflicting passages and file paths.

## 2.3 Cross-Document Terminology Audit

This is critical. Multiple authors (David, different Claude sessions) have written these specs over weeks. Terminology WILL have drifted. Find every case where:

- The same concept has different names in different documents
- The same name means different things in different documents
- A concept is defined in one doc but referenced differently in another

Format as a table:

| Concept | Doc A Name | Doc A File | Doc B Name | Doc B File | Reconciliation Needed |
|---------|-----------|------------|-----------|------------|----------------------|

Pay particular attention to:
- Tier numbering (are Tier 1/2/3 consistent everywhere?)
- Template numbering (do template IDs collide?)
- Variable names (cortisol vs. HPA_axis_output vs. hpa_stress_reactivity)
- Claim types (Type A/B vs. evaluative/functional vs. other terminology)
- Gap types (do GapPredictor and Queue use the same taxonomy?)
- Maturity levels (how-possibly/plausibly/actually — same labels everywhere?)
- Effect pathways (subpersonal/personal_epistemic/mixed vs. explicit/implicit_cognitive/implicit_physiological)

---

# SECTION 3: VARIABLE VOCABULARY AUDIT

Search across ALL specification documents and ALL code for every variable name used in:
- Mechanistic template causal chains
- BN node definitions
- Extraction pipeline outputs
- Queue target descriptions

Produce a **canonical variable list** organized by domain:

```
ENVIRONMENTAL FEATURES:
- [list every variable name found, with source file]
- Flag synonyms and conflicts

NEURAL / PHYSIOLOGICAL:
- [list]

PSYCHOLOGICAL / COGNITIVE:
- [list]

BEHAVIORAL / OUTCOME:
- [list]
```

For each cluster of synonyms, recommend a canonical name.

---

# SECTION 4: TEMPLATE COMPLETENESS AUDIT

For Templates 1–30 (and any beyond 30 from Panel III):

| Template ID | Name | Fully Specified? | Causal Chain Complete? | Params Given? | Scope Conditions? | Missing What? |
|-------------|------|-----------------|----------------------|---------------|-------------------|---------------|

"Fully specified" means: every causal link has from_variable, to_variable, maturity, bridging quality, and at least one piece of evidence cited. If the template is narrative-only (no structured data), mark it as "narrative only — needs encoding."

---

# SECTION 5: DEPENDENCY RISK ASSESSMENT

For the sprint plan (Sprints 0–9), identify:

## 5.1 Blocked Tasks
Tasks that CANNOT be done because prerequisite code or data doesn't exist:
- Task X.Y is blocked because [specific thing] doesn't exist yet and isn't in any prior task

## 5.2 Underspecified Tasks
Tasks where the description says "CC implements" but the logic requires theoretical judgment that a code agent can't make:
- Task X.Y requires [specific judgment] that needs human/expert specification

## 5.3 Duration Risks
Tasks that are estimated at 1–2 weeks but probably take longer because:
- Hidden complexity in [what]
- Dependency on external system [what]
- Requires data that doesn't exist yet [what]

## 5.4 Ordering Risks
Tasks that claim to be parallelizable but actually have hidden sequential dependencies.

---

# SECTION 6: EXTRACTION PIPELINE HEALTH

If an extraction pipeline exists and has produced artifacts:

## 6.1 Extraction Quality Spot Check
- Pick 5 random extracted claim records
- For each: is the claim correctly parsed? Are metadata fields populated? Are there obvious errors?
- What's the overall error rate estimate?

## 6.2 Coverage Assessment
- How many unique papers have been processed?
- How many claims extracted total?
- What's the average claims-per-paper?
- Are there papers that were attempted but failed? How many?

## 6.3 Data Format Assessment
- Are the extracted data in a format that Sprints 1–5 can consume?
- What transformations would be needed?
- Any data migration required?

---

# SECTION 7: CRITICAL RECOMMENDATIONS

Based on everything above, provide:

## 7.1 Top 5 Things to Fix Before Starting Sprints
Ordered by "if you don't fix this, everything downstream breaks."

## 7.2 Spec Revisions Needed
Which specification documents need revision before implementation, and what specifically needs to change?

## 7.3 Recommended Sprint Reordering
Based on what actually exists, should the sprint order change? Should any tasks be added, removed, or merged?

## 7.4 Vocabulary Reconciliation Decisions
List every terminology conflict that requires a human decision (not just a rename). For each, state the options and what depends on the choice.

---

# OUTPUT FORMAT

Produce a single markdown document titled `REPO_AUDIT_REPORT_[DATE].md`.

Be exhaustive. Cite file paths. Quote code. This document will be used to:
1. Revise the sprint plan
2. Produce theory reference specs
3. Reconcile vocabulary across documents
4. Unblock Claude Code implementation

**Err on the side of reporting too much rather than too little.**
