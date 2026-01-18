# RUTHLESS v5.1 — Article Eater GO/NO‑GO (Governance‑First)
**Panel:** Enterprise Stability Engineer · Cognitive Psychology Methods Lead · UX/UI Expert
**Hard rules:** No deletions. Quarantine old files. Respect `release.keep.yml` and `deprecations.yml`. Contract‑first.

## Checks
A) Governance present & enforced; no kept-file deletions.
B) Contracts/micro‑contracts; `public_surface_ledger.json` current.
C) Repo health: pinned deps; local run; logging; secrets hygiene.
D) DB & migrations: present, reversible, versioned.
E) Tests & coverage.
F) Frontend: rules tree, provenance, empty/loading, a11y.
G) Paper→rules validity: provenance, evidence counts, negative results.
H) Release assets: ZIP + concatenated TXT + `deconcat.py` + SHA256 manifest.

## Output
- GO/NO‑GO with rationale
- Blocking / High / Medium issues
- Minimal patch plan (≤10 steps) with filenames/path

## Subject typing & BN coverage

- Report global and per‑paper subject typing coverage from the RuleGraph v2 tab:
  - % of rules with age bands, culture regions, clinical populations, traits, moderators.
- Flag papers with <50% coverage in any dimension as **High** priority for curation.
- Verify that `config/subject_vocab.json` contains the canonical subject vocab used by:
  - RuleGraph v2 subject‑editing UI (suggestions and validation),
  - BN export pipeline (subject attribute nodes),
  - BN CSV writers (nodes/edges/rules).
- Confirm that subject typing distributions are reflected (at least qualitatively) in the
  BN Playground export summary, so panelists can see which populations the BN is actually
  about (e.g., mostly WEIRD vs diverse samples).
