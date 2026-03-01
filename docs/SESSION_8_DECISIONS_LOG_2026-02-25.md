# Session 8 Decisions Log

**Date**: 2026-02-25
**Sprint**: METADATA-1, SETUP-1, OVERSEER-2

---

## Decisions Made

### D8.1: PaperMetadata as separate dataclass (not inlined into ExtractedPaper)
- **Context**: Needed to add bibliographic metadata to multiple classes
- **Alternatives**: (A) Inline fields in each class, (B) Shared dataclass
- **Rationale**: Option B — single definition, consistent serialization, reusable across ExtractedPaper, ClaimV2, PaperIntegrationEvent, and setup()
- **Risk**: Low — purely structural, easily refactored
- **Dependencies**: All downstream consumers must import PaperMetadata
- **Panelist Concerns**: Liskov (substitution), Parnas (information hiding)

### D8.2: Citation graph stored as DOI lists per paper (not a separate graph DB)
- **Context**: How to represent citation relationships for argumentation structure
- **Alternatives**: (A) Separate graph DB (Neo4j), (B) DOI lists in JSON per paper, (C) Edge table in SQLite
- **Rationale**: Option B for now — simplest, fits existing JSON extraction files. Citation_graph.json provides the aggregated view. Can migrate to Option C or A later if graph queries become bottleneck.
- **Risk**: Medium — DOI lists grow large for highly-cited papers; graph queries require full scan
- **Dependencies**: Sprint 4 (argumentation graph) may need Option C
- **Panelist Concerns**: Pearl (graph structure), Simon (organizational simplicity)

### D8.3: Convergence threshold for Phase 5 reflective equilibrium = 0.001
- **Context**: How to determine when bulk reflective equilibrium has converged
- **Alternatives**: (A) Fixed iterations (5, 10, 50), (B) Absolute coherence delta < ε, (C) Relative delta < ε
- **Rationale**: Option B with ε = 0.001. Fixed iterations risk under- or over-computing. Relative delta is sensitive to scale. Absolute delta of 0.001 means "coherence changed by less than 0.1% — system has settled." Max iterations = 100 as safety valve.
- **Risk**: HIGH — This is the most consequential parameter. If convergence is slow, 100 iterations may not suffice. If convergence is fast, 0.001 may be too tight (wasting computation). Needs empirical calibration with actual data.
- **Dependencies**: None immediate; Phase 5 logs iteration count for calibration
- **Panelist Concerns**: **Spohn** (rank convergence guarantees), **Quine** (holism implies non-trivial dynamics)

### D8.4: Overseer uses separate SQLite database (overseer.db)
- **Context**: Where to store OVERSEER health metrics, violations, quarantine state
- **Alternatives**: (A) Same DB as web/beliefs, (B) Separate overseer.db, (C) In-memory only
- **Rationale**: Option B per panel decision O-7. Parnas information hiding: OVERSEER's monitoring state is independent of the system it monitors. Separate DB means OVERSEER can be reset/rebuilt without affecting web state.
- **Risk**: Low — requires passing two DB paths, but clean separation
- **Dependencies**: Migration 023 creates tables
- **Panelist Concerns**: Parnas (information hiding), Dijkstra (state separation)

### D8.5: Quarantine preserves original credence (not zero)
- **Context**: When a belief is quarantined (O-3), what happens to its credence?
- **Alternatives**: (A) Set credence to 0, (B) Preserve original credence but flag status, (C) Remove from web
- **Rationale**: Option B — quarantine is epistemic due diligence, not conviction. The belief may be correct but needs review. Preserving original credence means restoration is lossless.
- **Risk**: Low — quarantined beliefs still participate in coherence computation (this may or may not be desired)
- **Dependencies**: Review within 7 days (O-3)
- **Panelist Concerns**: **Haack** (epistemic caution), **Pollock** (defeaters don't destroy, they suspend)

### D8.6: Temporal ordering = publication year (not extraction date)
- **Context**: In what order should papers be loaded during setup()?
- **Alternatives**: (A) Extraction date, (B) Publication year, (C) Alphabetical by DOI, (D) Random
- **Rationale**: Option B — Quine's holism requires that earlier findings shape the epistemic landscape for later ones. A 1999 paper should contribute to the web before a 2024 meta-analysis that builds on it. Falls back to extraction date for papers with no year.
- **Risk**: Low — order effects dampen after global reflective equilibrium (Phase 5)
- **Dependencies**: Requires paper_metadata.year (from S2 enrichment)
- **Panelist Concerns**: **Quine** (temporal ordering for holistic revision), **DerSimonian** (recency weighting)

---

## Open Questions for Panel

| Q# | Question | Context | Options |
|----|----------|---------|---------|
| Q8.1 | Should quarantined beliefs participate in coherence computation? | D8.5: Currently they do (status flagged, credence preserved) | Yes (current), No (exclude from coherence), Partial (weight at 50%) |
| Q8.2 | Is 0.001 the right convergence threshold? | D8.3: No empirical data yet; needs calibration with 796 papers | Calibrate after Sprint 0 execution |
| Q8.3 | Should Phase 5 use damped vs. undamped reflective equilibrium? | Spohn suggests rank adjustments should be monotonically decreasing | Undamped (current), Damped (multiply adjustment by 0.9^iteration) |

---

## Files Created This Session

| File | Lines | Purpose |
|------|-------|---------|
| src/services/pdf_extraction.py | +60 | PaperMetadata dataclass |
| src/epistemic/contracts/claim_v2.py | +16 | 8 citation metadata fields |
| contracts/ae_af/schemas/ae.claim.v2.schema.json | +36 | Schema extension |
| src/services/paper_integration/models.py | +8 | Paper metadata on events |
| scripts/semantic_scholar_enrichment.py | ~450 | S2 enrichment + citation graph |
| src/services/system_setup.py | ~1,145 | 12-phase setup() function |
| src/services/overseer.py | ~1,226 | OVERSEER service (6 sub-components) |
| migrations/023_paper_metadata_and_overseer.sql | ~240 | 5 new DB tables |
| docs/SPRINT_PLAN_SETUP_AND_OVERSEER_2026-02-25.md | ~1,740 | 6-sprint plan |
| docs/SPRINT_PLAN_SUMMARY_2026-02-25.md | ~238 | Executive summary |
| docs/SESSION_8_DECISIONS_LOG_2026-02-25.md | this file | Decision record |
