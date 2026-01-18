# Article Eater v20.8.0 — Claude Primer (necessary & sufficient)

## 0) Verdict on the ZIP you uploaded
The repo is **functionally “complete”** (code + contracts + docs), but it is **not a good artifact to hand Claude as-is**.

Why Claude can freeze on it:
- **1496 files** (mostly `__pycache__` + archived material). That is a lot for an LLM file-ingest step.
- **Binary payloads** that are irrelevant to understanding the system (notably `ae.db`, plus multiple nested ZIPs and a DOCX).
- **Pathnames with shell-sensitive characters**: there is a directory named `<relative/` containing a file named `path>`.
  Some ingestion pipelines choke on `<` / `>` in filenames.

**Recommendation:** Give Claude the *minimal pack* listed in §7, or the cleaned ZIP I can generate (see below in chat).

---

## 1) What Article Eater is (in one paragraph)
**Article Eater (AE)** is a literature-processing module that takes a single academic paper (PDF + metadata), extracts **structured empirical claims** and **candidate “rules”** (design factor → outcome relations), produces **machine-validated output bundles** for downstream modules, and optionally exports a **RuleGraph/BN-ready representation**. AE also includes a research track implementing a **Quinean coherentist “web of belief”** so extracted findings can be integrated as revisable beliefs rather than treated as fixed BN edges.

---

## 2) AE’s primary integration surface (the only thing AF must rely on)
### File-bundle contract with Article Finder (AF)
**Canonical contract pack:** `contracts/ae_af/`

AF → AE input bundle (directory):
- `paper.pdf`
- `paper.json` (validates `contracts/ae_af/schemas/ae.paper.v1.schema.json`)
- `abstract.txt` (optional but supported by example)

AE → AF output bundle (directory):
- `result.json` (validates `contracts/ae_af/schemas/ae.result.v1.schema.json`)
- `claims.jsonl` (each line validates `contracts/ae_af/schemas/ae.claim.v1.schema.json`)
- `rules.jsonl`  (each line validates `contracts/ae_af/schemas/ae.rule.v1.schema.json`)
- `provenance.json` (validates `contracts/ae_af/schemas/ae.provenance.v1.schema.json`)
- `audit.log.jsonl` (each line validates `contracts/ae_af/schemas/ae.audit_event.v1.schema.json`)
- `review_items.jsonl` may appear when HITL is required (schema: `ae.review_item.v1.schema.json`)

**Non-negotiable behavior for AF:**
- AF must treat `result.json.status` as the truth for success/failure.
- AF must *not* parse logs to determine success.

### Canonical CLI (contract-level)
Entry point:
- `bin/article_eater`

Contract command:
- `article_eater eat --in <JOB_IN_DIR> --out <JOB_OUT_DIR> --profile <fast|standard|deep> --hitl <off|auto|required>`

Implementation:
- `app/cli/article_eater_contract_cli.py` → `app/tasks/pipeline.py::run_from_contract_bundle()`

---

## 3) What AE produces conceptually
### A) Claims (atomic empirical statements)
`claims.jsonl` is intended to represent **single-study findings** in a schema-stable way:
- a natural-language statement
- typed variables (IV/DV), measures, population/subjects (when extractable)
- effect sizes / directionality where available
- evidence pointers + provenance

### B) Rules (cross-paper/generalized candidates)
`rules.jsonl` represents **generalizations** AE believes are justified (or at least worth proposing), backed by one or more claims.

### C) Provenance & audit
- `provenance.json` ties outputs back to the input paper + extraction settings.
- `audit.log.jsonl` is append-only logging suitable for governance and HITL review.

---

## 4) How AE talks to the rest of your CNfA ecosystem
### 4.1 Tagging_Contractor / environment vocabulary
AE aligns “independent variable” environmental terms to canonical tag IDs using:
- `lib/environment_resolver.py`
- `contracts/vocab/environment_lookup.json` (declares source: Tagging_Contractor)

Behavior:
- Exact+fuzzy lookup of environment terms → `env.*` tag ids.
- Unresolved terms can be queued via `resolve_or_queue_environment()`.

### 4.2 Outcome_Contractor / outcome vocabulary
AE aligns “dependent variable” outcome terms to canonical IDs using:
- `lib/outcome_resolver.py`
- `contracts/outcome_vocab/outcome_lookup.json`

Behavior:
- Exact+fuzzy lookup.
- Unknown outcome terms are appended to `data/unresolved_outcomes.jsonl` for later import.
- Import helper: `scripts/import_outcomes_to_oc.py` (push queued terms into Outcome_Contractor).

### 4.3 BN‑Maker
AE supports producing BN‑Maker-friendly exports:
- `src/tools/bn_export_to_csv.py` (RuleGraph → CSVs)
- Documentation: `docs/BN_EXPORT_SCHEMA_v0_1.md`, `docs/BN_Outcome_Templates_v0_1.md`

Interpretation:
- AE’s rules/claims are **not** a complete BN (no full CPDs);
  they are structured inputs BN‑Maker can use to scaffold CPDs, priors, and subject‑type conditioning.

### 4.4 Image Tagger (indirect)
AE does not call Image Tagger directly. Interop happens via:
- **shared tag IDs** (environment factor vocabulary) so Image Tagger outputs can match AE‑derived rules.

---

## 5) Quine vs BN: what is actually implemented in v20.8.0?
### 5.1 The Quinean “web of belief” exists (explicitly)
Core implementation:
- `src/services/web_of_belief.py`

What it implements (high-level):
- Beliefs at multiple epistemic levels (theoretical ↔ observational).
- Constraint links (supports/contradicts/explains/instantiates/etc.).
- **Credence with meta-uncertainty** (uncertainty about the credence itself).
- Coherence scoring and belief status (stub/tentative/established/entrenched/anomalous).
- The idea that findings can exist as **stubs** without immediate theory attachment.

This is explicitly framed as Quinean coherentism (and reflective equilibrium) in the module docstring.

### 5.2 Is the Quine web wired into the AF contract CLI?
**Not yet.** In this repo, the contract-facing CLI path is:
`article_eater eat` → `app/tasks/pipeline.py`.

The Quinean system lives in `src/services/*` and is exercised primarily via:
- `src/services/evidence_integration.py`
- `tests/test_phase1_refined_epistemic.py`
- reports in `reports/` + `docs/ARCHITECTURE.md`

So, **AE currently contains both**:
1) A pragmatic extraction/contract pipeline for AF.
2) A research-grade coherentist epistemic engine.

If your “big changes” involve moving from a BN‑only worldview to a Quine‑style belief web, the engineering work is primarily **wiring these two streams together**:
- map extracted claims/rules → Belief nodes
- map rule support/contradiction → constraint edges
- propagate credence/coherence → usable decision outputs
- export views back out to BN‑Maker when needed

---

## 6) Where to look first (for engineering work)
If someone must understand the system quickly:

1) **AF↔AE contract and schemas**
   - `contracts/ae_af/CLAUDE_HANDOFF_PROMPT.md`
   - `contracts/ae_af/README.md`
   - `contracts/ae_af/schemas/*.schema.json`

2) **Contract CLI and bundle execution**
   - `bin/article_eater`
   - `app/cli/article_eater_contract_cli.py`
   - `app/tasks/pipeline.py`

3) **Vocab alignment (shared ontology across modules)**
   - `lib/environment_resolver.py` + `contracts/vocab/environment_lookup.json`
   - `lib/outcome_resolver.py` + `contracts/outcome_vocab/outcome_lookup.json`

4) **Quinean engine**
   - `docs/ARCHITECTURE.md`
   - `src/services/web_of_belief.py`
   - `src/services/evidence_integration.py`

---

## 7) Minimal pack to give Claude (recommended)
If you want Claude to *understand everything relevant* without freezing, give it only:

**A) Contract pack**
- `contracts/ae_af/` (entire folder)

**B) Contract execution path**
- `bin/article_eater`
- `app/cli/article_eater_contract_cli.py`
- `app/tasks/pipeline.py`

**C) Shared vocab alignment**
- `lib/environment_resolver.py`
- `contracts/vocab/environment_lookup.json`
- `lib/outcome_resolver.py`
- `contracts/outcome_vocab/outcome_lookup.json`
- `scripts/import_outcomes_to_oc.py`

**D) Quinean web-of-belief (only if the planned changes involve it)**
- `docs/ARCHITECTURE.md`
- `src/services/web_of_belief.py`
- `src/services/evidence_integration.py`

That’s enough for Claude to:
- implement AF↔AE integration correctly,
- preserve vocab compatibility with Tagging_Contractor and Outcome_Contractor,
- understand the Quine/coherence direction and where it lives.

---

## 8) Concrete explanation for Claude “freezing”
Most likely causes in this exact ZIP:
- `__pycache__` proliferation inflates file count and distracts the model.
- `ae.db` is binary and non-essential for reasoning about architecture.
- Nested ZIPs (`Envkit.zip`, old handoff packages) invite recursive ingestion.
- Unusual filenames (`<relative/path>`, `path>`) can trip sanitizers.

If you want to keep using ZIP uploads, produce a “clean” ZIP that excludes:
- `ae.db`, `Envkit.zip`, `__pycache__/`, `__MACOSX/`, `docs/archive/`, `backup_*/`, and `<relative/`.

